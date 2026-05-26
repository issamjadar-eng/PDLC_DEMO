"""Confluence attachment operations via web-control cookie reuse.

The official Atlassian Remote MCP exposes no attachment tooling. The
working pattern (proved end-to-end in task probes K/K2/K3 against the
sandbox) is:

  1. User signs into Confluence in the dedicated debug Chrome
     profile owned by the `web-control` skill (with "Remember me"
     checked so the session persists).
  2. We extract a `Cookie:` request header from that profile via
     `web-control`'s `extract_cookies` lib.
  3. We make raw HTTP calls to Confluence's REST attachment endpoints
     using that cookie header — same identity as the MCP, but reaches
     the attachment surface the MCP doesn't expose.

This module is the auth bridge plus the attachment-op surface
(`list_attachments`, `download_attachment`, `upload_attachment`,
`update_attachment`, `attachment_url`).

We use Python's stdlib `urllib` rather than `httpx` to keep the
dependency surface minimal — attachment ops are bounded and not in a
hot path, so async + connection pooling don't earn their cost here.

Failure modes the caller should expect:
  - `ChromeNotRunning` — debug Chrome isn't up. Caller surfaces
    "run /web-control launch" hint.
  - `NoConfluenceCookies` — Chrome is up but the user hasn't signed
    into the configured Atlassian instance. Caller surfaces
    "sign in to <base_url> in the debug Chrome (check 'Remember me')".
  - `ConfluenceAuthExpired` — HTTP 401/403 from a REST call. Cookie
    expired since last sign-in. Same recovery as NoConfluenceCookies.
  - `ConfluenceHTTPError` — any other non-2xx; preserves the response
    code and body for debugging.
"""
from __future__ import annotations

import hashlib
import json
import mimetypes
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path
from typing import Any

# ---- web-control bridge ----

_SKILL_ROOT = Path(__file__).resolve().parent.parent
_WEB_CONTROL_ROOT = _SKILL_ROOT.parent / "web-control"
if str(_WEB_CONTROL_ROOT) not in sys.path:
    sys.path.insert(0, str(_WEB_CONTROL_ROOT))

# Import lazily inside the helper so this module imports cleanly even when
# web-control is missing — that's a deployment problem, not an import-time one.


# ---- Errors ----


class AttachmentError(Exception):
    """Base class for attachment-op errors. Carries a recovery hint."""

    recovery: str = "See change-control README for attachment troubleshooting."

    def __init__(self, message: str, recovery: str | None = None) -> None:
        super().__init__(message)
        if recovery:
            self.recovery = recovery


class NoConfluenceCookies(AttachmentError):
    recovery = (
        "Sign in to your Confluence instance in the web-control debug Chrome "
        "(/web-control launch). Check 'Remember me' / 'Stay signed in' so the "
        "session cookie persists across browser restarts. Then retry."
    )


class ConfluenceAuthExpired(AttachmentError):
    recovery = (
        "The debug Chrome's Confluence session expired (HTTP 401/403). "
        "Open the Confluence instance in the web-control Chrome window, "
        "re-sign in (check 'Remember me'), and retry."
    )


class ConfluenceHTTPError(AttachmentError):
    recovery = "See response body for details. Inspect base_url and page_id."

    def __init__(self, status: int, body: str, url: str) -> None:
        self.status = status
        self.body = body
        self.url = url
        super().__init__(f"HTTP {status} from {url}: {body[:300]}")


class WebControlMissing(AttachmentError):
    recovery = (
        "The web-control skill is not present at the expected location. "
        "Ensure .claude/skills/web-control/ exists and is intact."
    )


# ---- Cookie extraction (delegates to web-control) ----


def extract_confluence_cookies(base_url: str) -> str:
    """Return a `Cookie:` header value for `base_url`, sourced from the
    debug Chrome's persistent jar.

    Raises `NoConfluenceCookies` if Chrome has no cookies for that URL
    (user hasn't signed in yet, or signed in to a different domain).
    Raises `WebControlError` (re-raised from the bridge) if the debug
    Chrome itself isn't reachable.
    """
    # Both change-control and web-control ship a top-level `lib`
    # package, so plain `from lib.cookies import ...` may resolve to
    # whichever was imported first. Load the web-control `lib` package
    # under an alias so its relative imports inside `cookies.py` (which
    # does `from .connect import ...`) still work.
    try:
        import importlib
        import importlib.util

        alias = "_webcontrol_lib"
        if alias in sys.modules:
            wc_pkg = sys.modules[alias]
        else:
            pkg_init = _WEB_CONTROL_ROOT / "lib" / "__init__.py"
            if not pkg_init.is_file():
                raise WebControlMissing(
                    f"web-control lib package not at {pkg_init}"
                )
            spec = importlib.util.spec_from_file_location(
                alias, str(pkg_init),
                submodule_search_locations=[str(_WEB_CONTROL_ROOT / "lib")],
            )
            wc_pkg = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
            sys.modules[alias] = wc_pkg
            spec.loader.exec_module(wc_pkg)  # type: ignore[union-attr]

        # Now import the cookies submodule under the alias so relative
        # imports (`from .connect import ...`) resolve correctly.
        cookies_mod = importlib.import_module(f"{alias}.cookies")
        cookies_to_header = cookies_mod.cookies_to_header
        extract_cookies = cookies_mod.extract_cookies
    except WebControlMissing:
        raise
    except Exception as exc:  # noqa: BLE001
        raise WebControlMissing(
            f"could not load web-control cookies module: {exc}"
        ) from exc

    cookies = extract_cookies(base_url)
    if not cookies:
        raise NoConfluenceCookies(f"no cookies in debug Chrome jar for {base_url}")
    header = cookies_to_header(cookies)
    if not header:
        raise NoConfluenceCookies(
            f"cookie list for {base_url} contained no usable name=value pairs"
        )
    return header


# ---- HTTP helpers ----


def _request(
    method: str,
    url: str,
    cookie_header: str,
    *,
    body: bytes | None = None,
    content_type: str | None = None,
    accept_json: bool = True,
    extra_headers: dict[str, str] | None = None,
    timeout: float = 30.0,
) -> tuple[int, bytes, dict[str, str]]:
    """Issue a single HTTP request with cookie auth. Returns (status, body, headers).

    Raises `ConfluenceAuthExpired` on 401/403, `ConfluenceHTTPError` on
    other non-2xx, and re-raises URLError for transport issues.
    """
    headers: dict[str, str] = {
        "Cookie": cookie_header,
        # Required for any state-changing call against Atlassian — defends
        # against XSRF protection on the form-encoded REST endpoints.
        "X-Atlassian-Token": "no-check",
    }
    if accept_json:
        headers["Accept"] = "application/json"
    if content_type:
        headers["Content-Type"] = content_type
    if extra_headers:
        headers.update(extra_headers)

    req = urllib.request.Request(url, data=body, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            payload = resp.read()
            resp_headers = {k.lower(): v for k, v in resp.headers.items()}
            return resp.status, payload, resp_headers
    except urllib.error.HTTPError as exc:
        body_text = ""
        try:
            body_text = exc.read().decode("utf-8", errors="replace")
        except Exception:
            pass
        if exc.code in (401, 403):
            raise ConfluenceAuthExpired(
                f"HTTP {exc.code} from {url}: {body_text[:200]}"
            )
        raise ConfluenceHTTPError(exc.code, body_text, url)


def _get_json(url: str, cookie_header: str) -> Any:
    status, body, _ = _request("GET", url, cookie_header)
    if status >= 400:
        raise ConfluenceHTTPError(status, body.decode("utf-8", errors="replace"), url)
    return json.loads(body.decode("utf-8"))


# ---- Multipart form encoder (stdlib only) ----


def _encode_multipart(
    file_path: Path,
    *,
    file_field_name: str = "file",
    extra_fields: dict[str, str] | None = None,
) -> tuple[bytes, str]:
    """Encode a single file + optional plain-text fields as multipart/form-data.

    Returns `(body_bytes, content_type_header)`.
    """
    boundary = "----WebKitFormBoundary" + uuid.uuid4().hex
    crlf = b"\r\n"
    parts: list[bytes] = []

    for name, value in (extra_fields or {}).items():
        parts.append(("--" + boundary).encode())
        parts.append(
            ('Content-Disposition: form-data; name="%s"' % name).encode()
        )
        parts.append(b"")
        parts.append(value.encode("utf-8"))

    filename = file_path.name
    content_type = (
        mimetypes.guess_type(filename)[0] or "application/octet-stream"
    )
    file_bytes = file_path.read_bytes()
    parts.append(("--" + boundary).encode())
    parts.append(
        (
            'Content-Disposition: form-data; name="%s"; filename="%s"'
            % (file_field_name, filename)
        ).encode()
    )
    parts.append(("Content-Type: " + content_type).encode())
    parts.append(b"")
    parts.append(file_bytes)

    parts.append(("--" + boundary + "--").encode())
    parts.append(b"")

    body = crlf.join(parts)
    return body, "multipart/form-data; boundary=" + boundary


# ---- Hashing ----


def compute_sha256(path: Path) -> str:
    """SHA-256 hex digest of a file. Used for content-hash comparison
    against existing Confluence attachments to skip no-op uploads."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


# ---- Attachment operations ----


def list_attachments(
    base_url: str,
    page_id: str,
    cookie_header: str,
    *,
    limit: int = 200,
    expand_labels: bool = False,
) -> list[dict[str, Any]]:
    """List attachments on a Confluence page.

    Returns the `results` array from `/wiki/rest/api/content/{pageId}/child/attachment?expand=metadata,version,extensions`.
    Each element includes `id` (Confluence attachment id like
    `att6642925726`), `title` (user-facing filename),
    `metadata.mediaType` (mime), `extensions.fileId` (the v2 media UUID
    that ADF `media.attrs.id` / `mediaInline.attrs.id` references),
    `extensions.fileSize`, and `_links.download`.

    `expand_labels=True` also requests `metadata.labels`, populating
    each result's `metadata.labels.results[]` with `{prefix, name, id}`
    entries — required by the Attachments-macro expander (which filters
    by `labels` macro parameter).
    """
    expand = "metadata,version,extensions"
    if expand_labels:
        expand += ",metadata.labels"
    url = (
        base_url.rstrip("/")
        + f"/wiki/rest/api/content/{page_id}/child/attachment"
        + f"?limit={int(limit)}&expand={expand}"
    )
    payload = _get_json(url, cookie_header)
    return list(payload.get("results", []))


def list_attachments_by_uuid(
    base_url: str,
    page_id: str,
    cookie_header: str,
    *,
    limit: int = 200,
    _attachments: list[dict[str, Any]] | None = None,
) -> dict[str, dict[str, Any]]:
    """Return `{file_uuid: {title, mediaType, attachment_id, fileSize}}`
    keyed by the v2 media UUID that ADF media nodes reference.

    The correlation field in Confluence's REST v1 attachment response is
    `extensions.fileId` — a UUID identical to the `attrs.id` on the
    corresponding ADF `media` / `mediaInline` node. The user-facing
    filename is `title`; the mime is `metadata.mediaType` (or
    `extensions.mediaType` as a fallback).

    Records missing a `fileId` (older attachments uploaded before
    Confluence's v2 media migration) are skipped — they cannot be
    matched to ADF UUIDs at all, and the caller's filename-fallback
    handles them via the original `<uuid>.bin` synthesis.

    `_attachments` lets callers pass a pre-fetched list (e.g., when
    they're already calling `list_attachments` for another reason).
    """
    if _attachments is None:
        _attachments = list_attachments(
            base_url, page_id, cookie_header, limit=limit
        )
    out: dict[str, dict[str, Any]] = {}
    for a in _attachments:
        ext = a.get("extensions") or {}
        file_uuid = ext.get("fileId")
        if not file_uuid:
            continue
        title = a.get("title") or ""
        mime = (
            (a.get("metadata") or {}).get("mediaType")
            or ext.get("mediaType")
            or ""
        )
        out[str(file_uuid)] = {
            "title": title,
            "mediaType": mime,
            "attachment_id": a.get("id") or "",
            "fileSize": ext.get("fileSize"),
        }
    return out


def find_attachment(
    attachments: list[dict[str, Any]], filename: str
) -> dict[str, Any] | None:
    """Locate an attachment by filename in a `list_attachments` result."""
    for a in attachments:
        if a.get("title") == filename:
            return a
    return None


def list_attachments_by_filename(
    base_url: str,
    page_id: str,
    cookie_header: str,
    *,
    limit: int = 200,
    _attachments: list[dict[str, Any]] | None = None,
) -> dict[str, dict[str, Any]]:
    """Return `{filename: {id, fileId, mediaType, fileSize, version}}`
    keyed by the user-facing filename (Confluence `title`).

    Sister of `list_attachments_by_uuid` — used by the cross-page resolver
    which knows the filename (from Storage XHTML `ri:filename`) but not
    the UUID. The output's `fileId` is the v2 media UUID that ADF
    `media.attrs.id` references on the source page, so the caller can
    splice the resolved value into round-trip markers.
    """
    if _attachments is None:
        _attachments = list_attachments(
            base_url, page_id, cookie_header, limit=limit
        )
    out: dict[str, dict[str, Any]] = {}
    for a in _attachments:
        title = a.get("title") or ""
        if not title:
            continue
        ext = a.get("extensions") or {}
        mime = (
            (a.get("metadata") or {}).get("mediaType")
            or ext.get("mediaType")
            or ""
        )
        out[title] = {
            "attachment_id": a.get("id") or "",
            "fileId": ext.get("fileId") or "",
            "mediaType": mime,
            "fileSize": ext.get("fileSize"),
        }
    return out


def attachment_url(base_url: str, page_id: str, filename: str) -> str:
    """The same-origin download URL for a page attachment.

    This is the URL we rewrite local image refs to before pushing
    markdown to Confluence — the renderer recognizes same-origin
    `/wiki/download/attachments/...` URLs and inlines them as images
    for authenticated viewers.
    """
    return (
        base_url.rstrip("/")
        + f"/wiki/download/attachments/{page_id}/{urllib.parse.quote(filename)}"
    )


def download_attachment(
    base_url: str,
    page_id: str,
    filename: str,
    target_path: Path,
    cookie_header: str,
) -> Path:
    """Download `filename` from page `page_id` to `target_path`.

    Creates parent directories. Returns the target path on success.
    """
    url = attachment_url(base_url, page_id, filename)
    status, body, _ = _request("GET", url, cookie_header, accept_json=False)
    if status >= 400:
        raise ConfluenceHTTPError(
            status, body.decode("utf-8", errors="replace"), url
        )
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_bytes(body)
    return target_path


def upload_attachment(
    base_url: str,
    page_id: str,
    source_path: Path,
    cookie_header: str,
    *,
    comment: str | None = None,
    minor_edit: bool = True,
) -> dict[str, Any]:
    """POST a new attachment to `page_id`. Returns the attachment record.

    Confluence's response wraps the new record in `{ "results": [ ... ] }`;
    we unwrap it for the caller.
    """
    if not source_path.is_file():
        raise AttachmentError(f"upload source not found: {source_path}")
    url = (
        base_url.rstrip("/")
        + f"/wiki/rest/api/content/{page_id}/child/attachment"
    )
    fields: dict[str, str] = {"minorEdit": "true" if minor_edit else "false"}
    if comment:
        fields["comment"] = comment
    body, ct = _encode_multipart(source_path, extra_fields=fields)
    status, resp_body, _ = _request(
        "POST", url, cookie_header, body=body, content_type=ct
    )
    if status >= 400:
        raise ConfluenceHTTPError(
            status, resp_body.decode("utf-8", errors="replace"), url
        )
    payload = json.loads(resp_body.decode("utf-8"))
    results = payload.get("results", [])
    if not results:
        raise ConfluenceHTTPError(
            status, resp_body.decode("utf-8", errors="replace"), url
        )
    return results[0]


def update_attachment(
    base_url: str,
    page_id: str,
    attachment_id: str,
    source_path: Path,
    cookie_header: str,
    *,
    comment: str | None = None,
    minor_edit: bool = True,
) -> dict[str, Any]:
    """POST a new version of an existing attachment.

    Endpoint: `/wiki/rest/api/content/{pageId}/child/attachment/{attachmentId}/data`.
    Returns the updated attachment record.
    """
    if not source_path.is_file():
        raise AttachmentError(f"update source not found: {source_path}")
    url = (
        base_url.rstrip("/")
        + f"/wiki/rest/api/content/{page_id}/child/attachment/{attachment_id}/data"
    )
    fields: dict[str, str] = {"minorEdit": "true" if minor_edit else "false"}
    if comment:
        fields["comment"] = comment
    body, ct = _encode_multipart(source_path, extra_fields=fields)
    status, resp_body, _ = _request(
        "POST", url, cookie_header, body=body, content_type=ct
    )
    if status >= 400:
        raise ConfluenceHTTPError(
            status, resp_body.decode("utf-8", errors="replace"), url
        )
    return json.loads(resp_body.decode("utf-8"))


def upload_or_update(
    base_url: str,
    page_id: str,
    source_path: Path,
    cookie_header: str,
    *,
    existing: list[dict[str, Any]] | None = None,
    comment: str | None = None,
) -> tuple[str, dict[str, Any]]:
    """Decide between upload (new file) and update (existing filename).

    Returns `(action, record)` where `action` is one of `"uploaded"`,
    `"updated"`, or `"skipped"`. `"skipped"` is reserved for callers that
    pre-compute a hash match — this helper itself does not skip; it
    always uploads or updates when called.

    If `existing` is None we list attachments first. Pass it when the
    caller has already paid that cost (e.g., bulk publish loop).
    """
    if existing is None:
        existing = list_attachments(base_url, page_id, cookie_header)
    match = find_attachment(existing, source_path.name)
    if match is None:
        rec = upload_attachment(
            base_url, page_id, source_path, cookie_header, comment=comment
        )
        return "uploaded", rec
    rec = update_attachment(
        base_url,
        page_id,
        match["id"],
        source_path,
        cookie_header,
        comment=comment,
    )
    return "updated", rec
