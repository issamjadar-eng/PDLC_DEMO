"""Thin wrapper over the Atlassian Remote MCP `mcp__atlassian__*` tools.

The wrapper takes an `mcp_call: MCPCallable` — any callable mapping
`(tool_name, **kwargs)` to the tool's result dict. This indirection lets
the action layer choose its MCP transport at invocation time (Claude
issues the tool calls; tests inject a fake callable; a future direct-HTTP
client could plug in here too) without coupling the lib to any one path.

Responsibilities of this layer:
  - Resolve cloudId from `getAccessibleAtlassianResources`
  - Normalize raw MCP responses into ergonomic dataclasses
    (`ConfluencePage`, `FooterComment`, `InlineComment`)
  - Surface typed errors with recovery hints
  - Pass `versionMessage` on every update — this is the audit-trail hook
    `freeze` / `publish` rely on (Probe D verified)

Non-responsibilities (callers own these):
  - Pre-push markdown transformations (frontmatter strip, link rewrite,
    fence-language swap) → `lib/markdown_transform.py`
  - Confluence Zone capture/splice → `lib/zones.py`
  - Divergence detection → `lib/divergence.py`
  - Snapshot caching → `lib/snapshot.py`
  - Attachment ops (MCP exposes none) → `lib/attachments.py`

Format choice (locked by Probe A): push markdown, read ADF when we need
structural fidelity (round-trip is lossless on ADF, lossy on markdown
for `<details>` / Expand wrapping). Read markdown only for human skim.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Optional, Protocol


# ---- Errors ----


class MCPError(Exception):
    """Base for MCP-related errors. Carries a recovery hint."""

    recovery: str = "Run /mcp and verify atlassian shows Connected."

    def __init__(self, message: str, recovery: str | None = None) -> None:
        super().__init__(message)
        if recovery:
            self.recovery = recovery


class MCPUnreachable(MCPError):
    recovery = (
        "MCP unreachable. Run /mcp, verify atlassian shows Connected, "
        "and retry. v0.6 fails loud — there is no httpx fallback."
    )


class MCPNotBound(MCPError):
    recovery = (
        "ConfluenceMCP was constructed without an mcp_call callable. "
        "This is a programming error — pass a callable that issues "
        "mcp__atlassian__<tool>(**kwargs) and returns its result."
    )


class CloudIdNotFound(MCPError):
    recovery = (
        "Could not resolve cloudId from getAccessibleAtlassianResources. "
        "Either no Atlassian site is accessible to this MCP session, or "
        "the configured base_url does not match any accessible site. "
        "Re-run /mcp authentication."
    )


class ContentFormatInvalid(MCPError):
    recovery = (
        "MCP contentFormat enum is ['markdown', 'adf'] only — HTML is "
        "not callable despite docstring claims (see Probe A)."
    )


# ---- Callable protocol ----


class MCPCallable(Protocol):
    """A callable that issues an MCP tool call and returns its raw result.

    Implementations must:
      - Block on the call until the MCP returns
      - Raise `MCPUnreachable` on transport failure (or any subclass of
        `MCPError` for typed failures)
      - Return the parsed JSON result body as a dict (or list, for the
        few endpoints that return arrays directly)
    """

    def __call__(self, tool: str, **kwargs: Any) -> Any: ...  # pragma: no cover


# ---- Dataclasses ----


VALID_FORMATS = ("markdown", "adf")


def _check_format(content_format: str) -> None:
    if content_format not in VALID_FORMATS:
        raise ContentFormatInvalid(
            f"contentFormat={content_format!r} not in {VALID_FORMATS}"
        )


@dataclass
class ConfluencePage:
    page_id: str
    title: str
    space_id: Optional[str]
    parent_id: Optional[str]
    version: int
    version_message: str
    body: str
    body_format: str
    web_ui_link: str
    raw: dict = field(repr=False, default_factory=dict)


@dataclass
class FooterComment:
    comment_id: str
    parent_comment_id: Optional[str]
    body: str
    author_account_id: str
    created_at: str
    web_ui_link: str
    raw: dict = field(repr=False, default_factory=dict)


@dataclass
class InlineComment:
    comment_id: str
    parent_comment_id: Optional[str]
    body: str
    author_account_id: str
    created_at: str
    inline_marker_ref: str
    inline_original_selection: str
    resolution_status: str
    web_ui_link: str
    raw: dict = field(repr=False, default_factory=dict)


# ---- Response normalizers (pure) ----


def _coerce_int(v: Any, default: int = 0) -> int:
    try:
        return int(v)
    except (TypeError, ValueError):
        return default


def _page_from_raw(raw: dict) -> ConfluencePage:
    """Translate an MCP getConfluencePage / createConfluencePage /
    updateConfluencePage response into a `ConfluencePage`.

    The MCP normalizes responses across Cloud v1/v2; we accept either shape:
      - `body` may be at `body.atlas_doc_format.value` (ADF), `body.storage.value` (HTML),
        `body.view.value` (markdown rendered), or top-level `body` (newer wrappers)
      - `version` may be `version.number` or `currentVersion.number`
    """
    body_format = raw.get("contentFormat") or raw.get("bodyFormat") or "adf"
    body_value = raw.get("body", "")
    if isinstance(body_value, dict):
        for key in ("atlas_doc_format", "storage", "view"):
            slot = body_value.get(key)
            if isinstance(slot, dict) and "value" in slot:
                body_value = slot["value"]
                if key == "atlas_doc_format":
                    body_format = "adf"
                elif key == "storage":
                    body_format = "storage"
                elif key == "view":
                    body_format = "view"
                break
        else:
            body_value = ""
    elif body_value is None:
        body_value = ""
    version_section = raw.get("version") or raw.get("currentVersion") or {}
    version_number = _coerce_int(
        version_section.get("number") if isinstance(version_section, dict) else 1, 1
    )
    version_message = ""
    if isinstance(version_section, dict):
        version_message = (
            version_section.get("message") or version_section.get("versionMessage") or ""
        )
    web_ui = ""
    links = raw.get("_links") or {}
    if isinstance(links, dict):
        web_ui = links.get("webui") or links.get("base") or ""
    return ConfluencePage(
        page_id=str(raw.get("id") or raw.get("pageId") or ""),
        title=str(raw.get("title", "")),
        space_id=str(raw["spaceId"]) if raw.get("spaceId") else None,
        parent_id=str(raw["parentId"]) if raw.get("parentId") else None,
        version=version_number,
        version_message=str(version_message),
        body=str(body_value),
        body_format=str(body_format),
        web_ui_link=str(web_ui),
        raw=raw,
    )


def _footer_comment_from_raw(raw: dict) -> FooterComment:
    body = raw.get("body", "")
    if isinstance(body, dict):
        for key in ("storage", "view", "atlas_doc_format", "raw"):
            slot = body.get(key)
            if isinstance(slot, dict) and "value" in slot:
                body = slot["value"]
                break
            if isinstance(slot, str):
                body = slot
                break
        else:
            body = ""
    author_id = ""
    author = raw.get("author") or raw.get("createdBy") or {}
    if isinstance(author, dict):
        author_id = author.get("accountId") or author.get("id") or ""
    elif isinstance(author, str):
        author_id = author
    parent_id = raw.get("parentCommentId") or raw.get("parentId")
    web_ui = ""
    links = raw.get("_links") or {}
    if isinstance(links, dict):
        web_ui = links.get("webui") or ""
    return FooterComment(
        comment_id=str(raw.get("id") or raw.get("commentId") or ""),
        parent_comment_id=str(parent_id) if parent_id else None,
        body=str(body),
        author_account_id=str(author_id),
        created_at=str(raw.get("createdAt") or raw.get("created") or ""),
        web_ui_link=str(web_ui),
        raw=raw,
    )


def _inline_comment_from_raw(raw: dict) -> InlineComment:
    """Inline comments carry `inlineCommentProperties` with the anchor
    info — `inlineMarkerRef`, `inlineOriginalSelection`, and a
    `resolutionStatus` we rely on for the open/resolved filter (Probe F)."""
    base = _footer_comment_from_raw(raw)
    props = raw.get("inlineCommentProperties") or raw.get("properties") or {}
    if not isinstance(props, dict):
        props = {}
    return InlineComment(
        comment_id=base.comment_id,
        parent_comment_id=base.parent_comment_id,
        body=base.body,
        author_account_id=base.author_account_id,
        created_at=base.created_at,
        inline_marker_ref=str(props.get("inlineMarkerRef") or props.get("markerRef") or ""),
        inline_original_selection=str(
            props.get("inlineOriginalSelection") or props.get("originalSelection") or ""
        ),
        resolution_status=str(
            props.get("resolutionStatus") or raw.get("resolutionStatus") or "open"
        ),
        web_ui_link=base.web_ui_link,
        raw=raw,
    )


def _extract_next_cursor(payload: Any) -> Optional[str]:
    """Extract the next-page cursor token from a paginated MCP response.

    Confluence's pagination shape varies by MCP flavor. We accept the
    common forms:
      - `_links.next` (full URL — cursor is in the query string)
      - `next` (relative path — cursor is in the query string)
      - `nextCursor` / `nextPageToken` (raw cursor string)

    Returns the cursor string suitable for the next call, or `None` if
    no further pages are available.
    """
    if not isinstance(payload, dict):
        return None
    # Direct cursor fields
    for key in ("nextCursor", "nextPageToken"):
        val = payload.get(key)
        if isinstance(val, str) and val:
            return val
    # _links.next or next — extract `cursor` from the query string
    candidates = []
    links = payload.get("_links")
    if isinstance(links, dict):
        candidates.append(links.get("next"))
    candidates.append(payload.get("next"))
    from urllib.parse import urlparse, parse_qs
    for cand in candidates:
        if not isinstance(cand, str) or not cand:
            continue
        parsed = urlparse(cand)
        qs = parse_qs(parsed.query)
        cur = qs.get("cursor")
        if cur:
            return cur[0]
    return None


def _unwrap_results(payload: Any) -> list[dict]:
    """Confluence list endpoints return `{results: [...]}`; some MCP
    flavors return the array directly. Accept either."""
    if isinstance(payload, list):
        return [r for r in payload if isinstance(r, dict)]
    if isinstance(payload, dict):
        results = payload.get("results")
        if isinstance(results, list):
            return [r for r in results if isinstance(r, dict)]
    return []


# ---- The wrapper ----


class ConfluenceMCP:
    """Wrapper around `mcp__atlassian__*` page + comment tools."""

    def __init__(
        self,
        mcp_call: MCPCallable | Callable[..., Any] | None,
        cloud_id: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> None:
        if mcp_call is None:
            raise MCPNotBound("ConfluenceMCP requires an mcp_call callable")
        self._call = mcp_call
        self._cloud_id = cloud_id
        self._base_url = base_url

    # --- Resource resolution ---

    @property
    def cloud_id(self) -> str:
        if self._cloud_id is None:
            self._cloud_id = self._resolve_cloud_id()
        return self._cloud_id

    def _resolve_cloud_id(self) -> str:
        """Pick the cloudId from `getAccessibleAtlassianResources`.

        If `base_url` was provided to the constructor, prefer the
        resource whose `url` matches; otherwise return the first one
        (the MCP only exposes resources the user has access to)."""
        payload = self._call("getAccessibleAtlassianResources")
        items: list[dict]
        if isinstance(payload, list):
            items = [x for x in payload if isinstance(x, dict)]
        elif isinstance(payload, dict):
            items = [
                x
                for x in (payload.get("resources") or payload.get("results") or [])
                if isinstance(x, dict)
            ]
        else:
            items = []
        if not items:
            raise CloudIdNotFound("getAccessibleAtlassianResources returned no resources")
        if self._base_url:
            base = self._base_url.rstrip("/")
            for it in items:
                url = (it.get("url") or "").rstrip("/")
                if url and url == base:
                    return str(it["id"])
        return str(items[0]["id"])

    # --- Page CRUD ---

    def get_page(
        self,
        page_id: str,
        content_format: str = "adf",
    ) -> ConfluencePage:
        _check_format(content_format)
        raw = self._call(
            "getConfluencePage",
            cloudId=self.cloud_id,
            pageId=str(page_id),
            contentFormat=content_format,
        )
        if not isinstance(raw, dict):
            raise MCPError(f"getConfluencePage returned non-dict: {type(raw).__name__}")
        return _page_from_raw(raw)

    def create_page(
        self,
        space_id: str,
        title: str,
        body: str,
        *,
        parent_id: Optional[str] = None,
        content_format: str = "markdown",
        version_message: str = "",
    ) -> ConfluencePage:
        _check_format(content_format)
        kwargs: dict[str, Any] = {
            "cloudId": self.cloud_id,
            "spaceId": str(space_id),
            "title": title,
            "body": body,
            "contentFormat": content_format,
        }
        if parent_id:
            kwargs["parentId"] = str(parent_id)
        if version_message:
            kwargs["versionMessage"] = version_message
        raw = self._call("createConfluencePage", **kwargs)
        if not isinstance(raw, dict):
            raise MCPError(
                f"createConfluencePage returned non-dict: {type(raw).__name__}"
            )
        return _page_from_raw(raw)

    def update_page(
        self,
        page_id: str,
        title: str,
        body: str,
        *,
        content_format: str = "markdown",
        version_message: str = "",
        parent_id: Optional[str] = None,
    ) -> ConfluencePage:
        _check_format(content_format)
        kwargs: dict[str, Any] = {
            "cloudId": self.cloud_id,
            "pageId": str(page_id),
            "title": title,
            "body": body,
            "contentFormat": content_format,
        }
        if parent_id:
            kwargs["parentId"] = str(parent_id)
        if version_message:
            kwargs["versionMessage"] = version_message
        raw = self._call("updateConfluencePage", **kwargs)
        if not isinstance(raw, dict):
            raise MCPError(
                f"updateConfluencePage returned non-dict: {type(raw).__name__}"
            )
        return _page_from_raw(raw)

    def get_descendants(
        self,
        page_id: str,
        depth: Optional[int] = None,
    ) -> list[dict]:
        """Single-call descendants (legacy). Prefer
        `get_descendants_paginated` for tree walks — the underlying MCP
        tool silently truncates at a small default depth (observed: 2)
        and paginates large result sets via a `cursor` field that this
        method does not follow."""
        kwargs: dict[str, Any] = {
            "cloudId": self.cloud_id,
            "pageId": str(page_id),
        }
        if depth is not None:
            kwargs["depth"] = int(depth)
        payload = self._call("getConfluencePageDescendants", **kwargs)
        return _unwrap_results(payload)

    def get_descendants_paginated(
        self,
        page_id: str,
        *,
        depth: int = 10,
        page_limit: int = 250,
    ) -> list[dict]:
        """Depth-safe + cursor-paginated descendants enumeration.

        The MCP tool's default depth truncates the tree at depth=2 with
        no warning — pages at depth=3+ are silently dropped. We always
        pass an explicit `depth` and follow the response's pagination
        cursor (if present) until exhausted.

        Cursor sources observed across MCP shapes:
          - `_links.next` (full URL with `cursor=...`)
          - `next` (relative path with `cursor=...`)
          - `nextCursor` / `nextPageToken` (raw cursor string)

        Guard: if a single response returns exactly `page_limit` results
        with no cursor, we raise. That state is indistinguishable from
        a silent truncation, and silent truncation is the bug this
        helper exists to prevent.
        """
        page_id = str(page_id)
        all_descendants: list[dict] = []
        cursor: Optional[str] = None
        seen_pages = 0
        while True:
            kwargs: dict[str, Any] = {
                "cloudId": self.cloud_id,
                "pageId": page_id,
                "depth": int(depth),
                "limit": int(page_limit),
            }
            if cursor:
                kwargs["cursor"] = cursor
            payload = self._call("getConfluencePageDescendants", **kwargs)
            chunk = _unwrap_results(payload)
            all_descendants.extend(chunk)
            seen_pages += 1

            next_cursor = _extract_next_cursor(payload)
            if next_cursor:
                cursor = next_cursor
                continue
            # No cursor — we're either done or silently truncated.
            if len(chunk) >= page_limit:
                raise MCPError(
                    f"getConfluencePageDescendants returned the page "
                    f"limit ({page_limit}) with no pagination cursor; "
                    f"refusing to silently truncate. pageId={page_id} "
                    f"depth={depth} pages_fetched={seen_pages}.",
                    recovery=(
                        "Increase page_limit, or check that the MCP "
                        "wrapper is exposing _links.next / nextCursor "
                        "correctly."
                    ),
                )
            return all_descendants

    # --- Footer comments ---

    def list_footer_comments(
        self,
        page_id: str,
        *,
        content_format: str = "markdown",
    ) -> list[FooterComment]:
        _check_format(content_format)
        payload = self._call(
            "getConfluencePageFooterComments",
            cloudId=self.cloud_id,
            pageId=str(page_id),
            contentFormat=content_format,
        )
        return [_footer_comment_from_raw(r) for r in _unwrap_results(payload)]

    def create_footer_comment(
        self,
        page_id: str,
        body: str,
        *,
        parent_comment_id: Optional[str] = None,
    ) -> FooterComment:
        kwargs: dict[str, Any] = {
            "cloudId": self.cloud_id,
            "pageId": str(page_id),
            "body": body,
        }
        if parent_comment_id:
            kwargs["parentCommentId"] = str(parent_comment_id)
        raw = self._call("createConfluenceFooterComment", **kwargs)
        if not isinstance(raw, dict):
            raise MCPError(
                f"createConfluenceFooterComment returned non-dict: {type(raw).__name__}"
            )
        return _footer_comment_from_raw(raw)

    # --- Inline comments ---

    def list_inline_comments(
        self,
        page_id: str,
        *,
        resolution_status: str = "open",
        content_format: str = "markdown",
    ) -> list[InlineComment]:
        _check_format(content_format)
        if resolution_status not in ("open", "resolved", "all"):
            raise MCPError(
                f"resolution_status={resolution_status!r} must be 'open' | 'resolved' | 'all'"
            )
        kwargs: dict[str, Any] = {
            "cloudId": self.cloud_id,
            "pageId": str(page_id),
            "contentFormat": content_format,
        }
        if resolution_status != "all":
            kwargs["resolutionStatus"] = resolution_status
        payload = self._call("getConfluencePageInlineComments", **kwargs)
        return [_inline_comment_from_raw(r) for r in _unwrap_results(payload)]

    def create_inline_comment(
        self,
        page_id: str,
        body: str,
        *,
        text_selection: str,
        text_selection_match_count: int = 1,
        text_selection_match_index: int = 0,
        parent_comment_id: Optional[str] = None,
    ) -> InlineComment:
        """Create an inline comment anchored to `text_selection`.

        `text_selection_match_count` + `text_selection_match_index`
        disambiguate when the anchor text appears multiple times on the
        page (Probe F)."""
        inline_props: dict[str, Any] = {
            "textSelection": text_selection,
            "textSelectionMatchCount": int(text_selection_match_count),
            "textSelectionMatchIndex": int(text_selection_match_index),
        }
        kwargs: dict[str, Any] = {
            "cloudId": self.cloud_id,
            "pageId": str(page_id),
            "body": body,
            "inlineCommentProperties": inline_props,
        }
        if parent_comment_id:
            kwargs["parentCommentId"] = str(parent_comment_id)
        raw = self._call("createConfluenceInlineComment", **kwargs)
        if not isinstance(raw, dict):
            raise MCPError(
                f"createConfluenceInlineComment returned non-dict: {type(raw).__name__}"
            )
        return _inline_comment_from_raw(raw)
