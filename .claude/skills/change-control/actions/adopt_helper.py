"""Adopt helper — turns an MCP `getConfluencePage(adf)` response into a
local markdown file with frontmatter, plus a snapshot cache entry.

Designed for Option A (agent-orchestrated) action flow:

  1. Agent calls `mcp__atlassian__getAccessibleAtlassianResources`
     and `mcp__atlassian__getConfluencePage(contentFormat=adf)`.
  2. Agent invokes:
         python actions/adopt_helper.py write \
             --target docs/confluence-staging/<SPACE>/<path>/<slug>.md \
             --space-key <SPACE> \
             --parent-page-id <parent-page-id> \
             --page-path "<SPACE>/<parent-title>/<page-title>" \
             --base-url https://<your-site>.atlassian.net \
             --cache-root docs/.change-control \
             < adf_response.json
     stdin is the raw `getConfluencePage` MCP result JSON.

Subcommands:

  write     Run the full adopt pipeline (normalize ADF, write markdown
            with frontmatter, write snapshot, print summary).
  preview   Print the normalized markdown to stdout without writing
            anywhere — used for dry-runs in the agent procedure.

The agent procedure decides where the file lands; this script doesn't
infer paths from the page tree (that's `adopt-tree`'s job).

This script is project-agnostic — no project-specific names hard-coded.
It accepts any space, any base URL, any tree.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

SKILL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_ROOT))

from lib.adopt_sync import (  # noqa: E402
    AdoptSyncDecision,
    classify_adopt,
    default_read_local_anc_version,
    default_read_local_body,
    render_conflict_prompt,
    write_conflict_files,
)
from lib.frontmatter import read as read_frontmatter  # noqa: E402
from lib.frontmatter import update as update_frontmatter  # noqa: E402
from lib.frontmatter import write as write_frontmatter  # noqa: E402
from lib.markdown_transform import md_link_dest  # noqa: E402
from lib.normalizer import (  # noqa: E402
    NormalizationReport,
    adf_to_markdown,
)
from lib.snapshot import read_snapshot, write_snapshot  # noqa: E402

try:
    from lib.config import read_change_control_config  # noqa: E402
except ImportError:  # pragma: no cover
    read_change_control_config = None  # type: ignore


def _apply_config_defaults(args: argparse.Namespace) -> None:
    """Fill in `--base-url` / `--space-key` from project.yml when blank.

    Reads the `change_control` block via `lib/config.py`. If a single space
    is configured, that space's key is used when `--space-key` is omitted.
    CLI flags continue to override (this only fires when the flag is "").
    """
    if read_change_control_config is None:
        return
    try:
        cfg = read_change_control_config()
    except Exception:  # noqa: BLE001
        return
    if not getattr(args, "base_url", "") and cfg.base_url:
        args.base_url = cfg.base_url
    if not getattr(args, "space_key", "") and len(cfg.spaces) == 1:
        args.space_key = cfg.spaces[0].key


# ---- Argument parsing ----


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="adopt_helper",
        description="Turn an MCP getConfluencePage response into a local markdown file.",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "--base-url",
        default="",
        help="Confluence base URL, e.g. https://example.atlassian.net. "
             "If omitted, falls back to project.yml `change_control.base_url`.",
    )
    common.add_argument(
        "--space-key",
        default="",
        help="Confluence space key the page belongs to (for frontmatter). "
             "If omitted with exactly one configured space in "
             "project.yml `change_control.spaces[]`, that space is used.",
    )
    common.add_argument(
        "--parent-page-id",
        default="",
        help="Parent page id (for frontmatter; empty if this is a space root).",
    )
    common.add_argument(
        "--page-path",
        default="",
        help="Human-readable Confluence path (for frontmatter).",
    )
    common.add_argument(
        "--adopted-at",
        default="",
        help="Override the adoption date (default: today UTC).",
    )

    w = sub.add_parser("write", parents=[common], help="Run the full adopt pipeline.")
    w.add_argument("--target", required=True, help="Output markdown path (relative or absolute).")
    w.add_argument(
        "--cache-root",
        default="docs/.change-control",
        help="Snapshot cache root (default: docs/.change-control).",
    )
    w.add_argument(
        "--download-images",
        action="store_true",
        help="Download Confluence media binaries via the web-control "
             "cookie bridge to <target-dir>/images/ and rewrite ADF "
             "media refs to relative paths. If omitted, images stay as "
             "live Confluence attachment URLs (auth-required to view).",
    )
    w.add_argument(
        "--on-conflict",
        choices=("prompt", "overwrite", "abort", "merge"),
        default="prompt",
        help="What to do when the local file has been edited AND "
             "Confluence has changed since the common-ancestor version. "
             "`prompt` (default) and `merge` both emit "
             "<doc>.confluence-side.md + <doc>.local-diff.md and exit "
             "non-zero so the agent can present the choice to the user. "
             "`overwrite` accepts the Confluence body (lossy). "
             "`abort` leaves the local file untouched.",
    )
    w.add_argument(
        "--force",
        action="store_true",
        help="Skip drift detection entirely — overwrite the target "
             "and refresh the snapshot exactly as the legacy adopt did. "
             "Use only for explicit destructive re-pulls.",
    )
    w.add_argument(
        "--manifest-path",
        default="",
        help="Path to a `.manifest.json` produced by `adopt-tree`. When "
             "provided, the adopt pipeline expands children/pagetree "
             "macros into a markdown bullet list of child pages and, "
             "for stub-container pages with no body macro, synthesizes "
             "an AUTO:CHILD-INDEX block at end-of-body. Both regions "
             "live between AUTO sentinels and are stripped from the "
             "diff so they never trigger spurious conflicts.",
    )
    w.add_argument(
        "--repo-root",
        default="",
        help="Path the manifest's `target_path` strings are relative to. "
             "Defaults to the current working directory. Used only when "
             "--manifest-path is set, to compute child-index relpaths.",
    )
    w.add_argument(
        "--storage-xhtml-input",
        default="",
        help="Optional path to a file containing the Confluence "
             "`body.storage` XHTML for THIS page. When provided, the "
             "adopt pipeline uses this for cross-page UNKNOWN_MEDIA_ID "
             "resolution instead of fetching it via the cookie bridge. "
             "Supports offline / mocked workflows.",
    )
    w.add_argument(
        "--cross-page-source-map",
        default="",
        help="Optional path to a JSON object mapping source-page-title → "
             "source-page-id. Lets the agent supply pre-resolved CQL "
             "search results so the cross-page resolver can pick up the "
             "right source page without making MCP calls itself.",
    )

    pv = sub.add_parser("preview", parents=[common], help="Print normalized markdown to stdout, no writes.")
    pv.add_argument("--target", default="", help="Optional target path (only used for the printed banner).")

    rs = sub.add_parser(
        "resolve-smartcards",
        help="Resolve [<<smartcard:KEY>>](URL) placeholders in a target file using a key→title map read from stdin (JSON object).",
    )
    rs.add_argument("--target", required=True,
                    help="Markdown file to rewrite in place.")
    return p


# ---- Pipeline ----


def _today_utc() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _attachment_url_resolver(base_url: str, page_id: str):
    """Resolver passed to the normalizer when no local image directory
    is available (preview mode, divergence-diff). Returns the live
    Confluence attachment URL — viewer will need an authenticated
    session to render the image, which is fine for diffing markdown.
    """
    def resolve(filename: str, media_id: str | None) -> str:
        if not filename:
            return f"{base_url.rstrip('/')}/wiki/download/attachments/{page_id}/"
        from urllib.parse import quote
        return (
            f"{base_url.rstrip('/')}/wiki/download/attachments/"
            f"{page_id}/{quote(filename)}"
        )
    return resolve


def _local_images_resolver():
    """Resolver that emits a relative `images/<filename>` path. Used by
    `cmd_write` so the on-disk markdown points at locally-downloaded
    binaries the action layer downloads after normalization.

    For unnamed media nodes (no `attrs.fileName`), we synthesize a
    filename from the media id so the rewrite is still deterministic.
    """
    def resolve(filename: str, media_id: str | None) -> str:
        name = filename
        if not name:
            # Anonymous media — use the media id as a stable handle. The
            # download pass uses the same fallback to choose a target
            # filename, so the path lines up.
            name = (media_id or "media") + ".bin"
        return f"images/{name}"
    return resolve


def normalize(
    raw: dict,
    base_url: str,
    *,
    image_mode: str = "url",
) -> tuple[str, NormalizationReport]:
    """Pure: turn the MCP response dict into (markdown, report).

    `image_mode`:
      - `"url"` (default) — emit live Confluence attachment URLs in the
        markdown. Used for preview, divergence-diff, and any flow that
        doesn't download binaries.
      - `"local"` — emit relative `images/<filename>` paths. The caller
        is responsible for downloading the binaries to that location.
    """
    page_id = str(raw.get("id") or raw.get("pageId") or "")
    body = raw.get("body")
    if isinstance(body, dict):
        # Shape A — live MCP: body is the ADF doc dict directly
        if body.get("type") == "doc":
            adf = body
        else:
            # Shape B — wrapped: body.{atlas_doc_format,storage,view}.value
            adf = None
            for key in ("atlas_doc_format", "storage", "view"):
                slot = body.get(key)
                if isinstance(slot, dict) and "value" in slot:
                    val = slot["value"]
                    if isinstance(val, str) and val.strip().startswith("{"):
                        try:
                            adf = json.loads(val)
                        except (ValueError, TypeError):
                            adf = None
                    elif isinstance(val, dict):
                        adf = val
                    break
            if adf is None:
                adf = {"type": "doc", "content": []}
    elif isinstance(body, str) and body.strip().startswith("{"):
        try:
            adf = json.loads(body)
        except (ValueError, TypeError):
            adf = {"type": "doc", "content": []}
    else:
        adf = {"type": "doc", "content": []}

    report = NormalizationReport()
    if image_mode == "local":
        resolver = _local_images_resolver()
    else:
        resolver = _attachment_url_resolver(base_url, page_id)
    md = adf_to_markdown(adf, attachment_url=resolver, report=report)
    return md, report


def build_frontmatter(
    raw: dict,
    *,
    space_key: str,
    parent_page_id: str,
    page_path: str,
    adopted_at: str,
) -> dict:
    page_id = str(raw.get("id") or raw.get("pageId") or "")
    title = str(raw.get("title") or "")
    version_section = raw.get("version") or {}
    version_number = (
        version_section.get("number")
        if isinstance(version_section, dict)
        else 1
    )
    try:
        version_int = int(version_number)
    except (TypeError, ValueError):
        version_int = 1
    fm: dict[str, Any] = {
        "title": title,
        "state": "published",
        "confluence": {
            "page_id": page_id,
            "space_key": space_key,
            "parent_page_id": parent_page_id or None,
            "page_path": page_path or None,
            "adopted_at": adopted_at,
            "adopted_from_version": version_int,
            "last_published_version": version_int,
        },
    }
    return fm


def render_summary(
    target: Path,
    fm: dict,
    report: NormalizationReport,
    snapshot_path: Path | None,
    download_summary: dict | None = None,
) -> str:
    lines = [
        f"adopted: {fm['confluence']['page_id']} -> {target}",
        f"  title:        {fm['title']!r}",
        f"  version:      {fm['confluence']['adopted_from_version']}",
        f"  zones:        {len(report.zones)} ({', '.join(report.zones) or '-'})",
        f"  extensions:   {len(report.extensions)}",
        f"  media refs:   {len(report.media_refs)}",
        f"  smart links:  {len(report.smart_links)}",
        f"  attach macros: {len(report.attachment_macros)}",
    ]
    if download_summary is not None:
        lines.append(
            f"  images:       {download_summary['downloaded']}/"
            f"{download_summary['total_refs']} downloaded"
            + (f" ({download_summary['failed']} failed)"
               if download_summary['failed'] else "")
        )
    if snapshot_path is not None:
        lines.append(f"  snapshot:     {snapshot_path}")
    return "\n".join(lines)


# ---- Subcommand handlers ----


def cmd_preview(args: argparse.Namespace, raw: dict) -> int:
    md, _ = normalize(raw, args.base_url)
    if args.target:
        print(f"# preview of: {args.target}", file=sys.stderr)
    sys.stdout.write(md)
    return 0


def _download_images(
    base_url: str,
    page_id: str,
    target_dir: Path,
    images: list[dict],
    target_md_file: Path | None = None,
) -> tuple[int, int, list[str], dict[str, str]]:
    """Download every image / file-card binary in `report.images` to
    `<target_dir>/images/`, resolving filename-less media via
    `list_attachments_by_uuid`.

    Returns `(downloaded, failed, errors, resolutions)` where
    `resolutions` is `{media_uuid: resolved_filename}` — the caller
    rewrites placeholder refs in the markdown after this returns.

    Filename-resolution flow:
      1. If the normalizer captured a `filename`, use it directly.
      2. If `filename` is blank but `media_id` is set, group these
         by page_id and call `list_attachments_by_uuid(page_id)` once
         to map UUIDs → titles. Use the resolved title as the on-disk
         filename (with the correct extension Confluence stored).
      3. If a UUID still has no resolution (older attachment without a
         `fileId`, or a permission glitch), fall back to `<uuid>.bin`
         — same behavior as before this fix, last resort only.

    Errors are stderr-friendly one-line strings; failures degrade
    gracefully (we leave the markdown reference intact so the page is
    still readable, and the user can re-adopt later).
    """
    if not images:
        return 0, 0, [], {}

    # Lazy import — keeps the helper importable even when web-control
    # isn't on disk (e.g., unit tests that exercise normalize() only).
    try:
        from lib.attachments import (  # type: ignore
            download_attachment,
            extract_confluence_cookies,
            list_attachments_by_uuid,
        )
    except ImportError as exc:
        return 0, len(images), [f"attachments lib missing: {exc}"], {}

    images_dir = target_dir / "images"
    try:
        cookies = extract_confluence_cookies(base_url)
    except Exception as exc:  # noqa: BLE001 — surface any cookie failure
        return 0, len(images), [f"cookie bridge failed: {exc}"], {}

    # Step 1: resolve every filename-less media UUID via list_attachments.
    needs_resolution = {
        img.get("media_id") for img in images
        if not img.get("filename") and img.get("media_id")
    }
    resolutions: dict[str, str] = {}
    if needs_resolution:
        try:
            uuid_map = list_attachments_by_uuid(base_url, page_id, cookies)
        except Exception as exc:  # noqa: BLE001 — degrade gracefully
            uuid_map = {}
            errors_init = [f"list_attachments({page_id}): {exc}"]
        else:
            errors_init = []
        for uuid in needs_resolution:
            entry = uuid_map.get(uuid)
            if entry and entry.get("title"):
                resolutions[uuid] = entry["title"]
    else:
        errors_init: list[str] = []

    downloaded = 0
    failed = 0
    errors: list[str] = list(errors_init)
    seen: set[str] = set()
    for img in images:
        filename = img.get("filename") or ""
        media_id = img.get("media_id") or ""
        if not filename and media_id and media_id in resolutions:
            filename = resolutions[media_id]
        if not filename:
            # Final fallback — synthesize the same `<uuid>.bin` the
            # local-images resolver uses so the relpath lines up. This
            # is only hit when list_attachments returned nothing for
            # this UUID (very rare; legacy attachments).
            filename = (media_id or "media") + ".bin"
        if filename in seen:
            # Same filename appears multiple times — Confluence
            # de-duplicates by name, so one download is enough.
            continue
        seen.add(filename)
        target = images_dir / filename
        try:
            download_attachment(
                base_url, page_id, filename, target, cookies
            )
            downloaded += 1
        except Exception as exc:  # noqa: BLE001 — degrade gracefully
            failed += 1
            errors.append(f"{filename}: {exc}")

    # Step 2: rewrite markdown placeholders in the target file.
    # Every image/file-card without a known filename was emitted with
    # placeholder ref `images/<uuid>.bin` (and, for file-cards, label
    # `<<file:<uuid>>>`). Swap those for the resolved title.
    if target_md_file is not None and resolutions:
        try:
            text = target_md_file.read_text()
            new_text = text
            for uuid, title in resolutions.items():
                # File-card placeholder: [<<file:UUID>>](images/UUID.bin)
                # — encode the resolved title for the URL slot so spaces /
                # parens / etc. in `title` don't break CommonMark parsing.
                enc_title = md_link_dest(f"images/{title}")
                new_text = new_text.replace(
                    f"[<<file:{uuid}>>](images/{uuid}.bin)",
                    f"[{title}]({enc_title})",
                )
                # Image placeholder: ![alt](images/UUID.bin) — preserve alt.
                # We do a targeted regex swap of the path part only.
                import re as _re
                pat = _re.compile(
                    r"!\[([^\]]*)\]\(images/" + _re.escape(uuid) + r"\.bin\)"
                )
                new_text = pat.sub(
                    lambda m, t=title, e=enc_title: f"![{m.group(1)}]({e})",
                    new_text,
                )
            if new_text != text:
                target_md_file.write_text(new_text)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"placeholder rewrite: {exc}")

    return downloaded, failed, errors, resolutions


def _fetch_storage_xhtml(
    base_url: str, page_id: str, cookie_header: str
) -> str:
    """Fetch `body.storage` XHTML for a Confluence page via the cookie
    bridge. Returns the raw XHTML string, or '' on any error.
    """
    import urllib.error
    import urllib.parse
    import urllib.request

    url = (
        base_url.rstrip("/")
        + f"/wiki/rest/api/content/{urllib.parse.quote(page_id)}"
        "?expand=body.storage"
    )
    req = urllib.request.Request(
        url,
        headers={
            "Cookie": cookie_header,
            "Accept": "application/json",
            "X-Atlassian-Token": "no-check",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            payload = json.loads(resp.read().decode("utf-8", errors="replace"))
    except (urllib.error.URLError, urllib.error.HTTPError, ValueError):
        return ""
    body = payload.get("body") or {}
    storage = body.get("storage") or {}
    return str(storage.get("value") or "")


def _resolve_cross_page_attachments(
    md: str,
    *,
    base_url: str,
    space_key: str,
    page_id: str,
    target_dir: Path,
    target_md_file: Path,
    report,  # NormalizationReport
    storage_xhtml_input: str = "",
    source_map: dict[str, str] | None = None,
) -> tuple[str, list[str]]:
    """Resolve cross-page UNKNOWN_MEDIA_ID placeholders into real filenames
    + downloaded binaries + round-trip markers carrying source-page=<id>.

    Sequence per cross-page unknown:
      1. Fetch Storage XHTML (or use `storage_xhtml_input`)
      2. Parse `<ri:attachment ri:filename ri:content-title>` → ordered list
      3. Pair against `report.cross_page_unknowns` by structural position
      4. For each pair:
         a. Resolve source-page-id from `source_map` (agent-supplied) — if
            missing, emit graceful warning placeholder
         b. List source page attachments by filename → get fileId
         c. Download binary into `<target_dir>/images/<filename>`
         d. Replace markdown placeholder with resolved file-card +
            round-trip marker
      5. Track unresolved entries in `report.cross_page_unresolved` for
         the post-run summary

    Returns `(rewritten_markdown, warnings)`. Warnings are stderr-friendly
    one-liners. The markdown is mutated in-place (via the file path); the
    return value is the final string for downstream snapshot writing.
    """
    warnings: list[str] = []
    if not report.cross_page_unknowns:
        return md, warnings

    # Lazy import — keep helper importable when web-control is missing.
    try:
        from lib.attachments import (  # type: ignore
            download_attachment,
            extract_confluence_cookies,
            list_attachments_by_filename,
        )
    except ImportError as exc:
        warnings.append(f"cross-page attachments lib missing: {exc}")
        return _fallback_warn_all(
            md, base_url, space_key, report, warnings
        )

    # Step 1: Storage XHTML
    if storage_xhtml_input:
        try:
            xhtml = Path(storage_xhtml_input).read_text(encoding="utf-8")
        except OSError as exc:
            warnings.append(
                f"cross-page: --storage-xhtml-input read failed: {exc}"
            )
            xhtml = ""
    else:
        try:
            cookies = extract_confluence_cookies(base_url)
        except Exception as exc:  # noqa: BLE001
            warnings.append(f"cross-page: cookie bridge failed: {exc}")
            return _fallback_warn_all(
                md, base_url, space_key, report, warnings
            )
        xhtml = _fetch_storage_xhtml(base_url, page_id, cookies)
        if not xhtml:
            warnings.append(
                f"cross-page: storage XHTML fetch failed for page {page_id}"
            )
            return _fallback_warn_all(
                md, base_url, space_key, report, warnings
            )

    # Step 2 + 3: Parse + pair
    from lib.cross_page_resolve import (  # noqa: WPS433
        build_resolved_markdown,
        build_warning_markdown,
        pair_unknowns_to_storage,
        parse_storage_xhtml,
    )

    storage_entries = parse_storage_xhtml(xhtml)
    pairings = pair_unknowns_to_storage(
        report.cross_page_unknowns, storage_entries
    )

    images_dir = target_dir / "images"
    source_map = source_map or {}
    cookies_for_download: str | None = None
    if not storage_xhtml_input:
        # We already extracted cookies above
        try:
            cookies_for_download = extract_confluence_cookies(base_url)
        except Exception:  # noqa: BLE001
            cookies_for_download = None

    new_md = md
    for pair in pairings:
        placeholder_id = pair["placeholder_id"]
        position = pair["adf_position"]
        filename = pair["filename"]
        content_title = pair["content_title"]
        # Find the original markdown link for this position so we can swap
        # it. Source link shape:
        #   `[<<crosspage:{position}>>](images/CROSSPAGE-{position}.bin)<!-- crosspage position={position} -->`
        # We use position-anchored regex to be robust against URL encoding.
        import re as _re
        from lib.markdown_transform import md_link_dest  # noqa: WPS433

        old_url_enc = md_link_dest(f"images/CROSSPAGE-{position}.bin")
        # Build the literal placeholder pattern. Escape only the URL slot.
        old_pat_link = (
            r"\[<<crosspage:" + str(position) + r">>\]\("
            + _re.escape(old_url_enc)
            + r"\)<!-- crosspage position=" + str(position) + r" -->"
        )

        if not pair["matched"] or not filename:
            warning_md = build_warning_markdown(
                filename or "(unnamed attachment)",
                content_title or "(unknown source page)",
                base_url, space_key,
            )
            new_md, n = _re.subn(old_pat_link, _re.escape(warning_md).replace("\\ ", " ").replace("\\&", "&"), new_md)
            # Simpler: we just do a literal replace using re.sub with a
            # callable that returns the literal string — avoids re.escape
            # complications on the replacement side.
            if n == 0:
                new_md = _re.sub(
                    old_pat_link,
                    lambda _m, w=warning_md: w,
                    new_md,
                )
            warnings.append(
                f"cross-page unresolved (position {position}): "
                f"filename={filename!r} title={content_title!r}"
            )
            report.cross_page_unresolved.append({
                "filename": filename,
                "source_page_title": content_title,
                "source_page_id": "",
                "reason": "unmatched in storage xhtml" if not pair["matched"] else "no filename",
            })
            continue

        # Resolve source page id
        source_page_id = source_map.get(content_title, "")
        if not source_page_id:
            # Graceful: still rewrite to a friendlier markdown but flag
            # for follow-up. The reader sees the source page title and
            # filename — better than UNKNOWN_MEDIA_ID.
            warning_md = build_warning_markdown(
                filename, content_title, base_url, space_key,
            )
            new_md = _re.sub(
                old_pat_link,
                lambda _m, w=warning_md: w,
                new_md,
            )
            warnings.append(
                f"cross-page: source page not in --cross-page-source-map "
                f"(title={content_title!r}, file={filename!r})"
            )
            report.cross_page_unresolved.append({
                "filename": filename,
                "source_page_title": content_title,
                "source_page_id": "",
                "reason": "source-page-id not provided",
            })
            continue

        # Look up + download (live path; gracefully degrade)
        media_id = ""
        if cookies_for_download:
            try:
                fname_map = list_attachments_by_filename(
                    base_url, source_page_id, cookies_for_download
                )
                entry = fname_map.get(filename) or {}
                media_id = entry.get("fileId", "") or ""
                # Download binary into THIS page's images/
                target = images_dir / filename
                download_attachment(
                    base_url, source_page_id, filename, target,
                    cookies_for_download,
                )
            except Exception as exc:  # noqa: BLE001
                warnings.append(
                    f"cross-page download failed for {filename!r} from "
                    f"page {source_page_id}: {exc}"
                )
                # Still resolve markdown to a friendly form (no UNKNOWN);
                # add to unresolved log.
                report.cross_page_unresolved.append({
                    "filename": filename,
                    "source_page_title": content_title,
                    "source_page_id": source_page_id,
                    "reason": f"download failed: {exc}",
                })
        else:
            warnings.append(
                "cross-page: no cookies available for download "
                f"({filename!r} from page {source_page_id})"
            )
            report.cross_page_unresolved.append({
                "filename": filename,
                "source_page_title": content_title,
                "source_page_id": source_page_id,
                "reason": "no cookie bridge",
            })

        resolved_md = build_resolved_markdown(
            filename, media_id, source_page_id, content_title,
        )
        new_md = _re.sub(
            old_pat_link,
            lambda _m, r=resolved_md: r,
            new_md,
        )

    # Persist mutated markdown if file already exists; otherwise the caller
    # will write it.
    if target_md_file.exists() and new_md != md:
        try:
            target_md_file.write_text(new_md)
        except OSError as exc:
            warnings.append(f"cross-page write failed: {exc}")
    return new_md, warnings


def _fallback_warn_all(
    md: str,
    base_url: str,
    space_key: str,
    report,  # NormalizationReport
    warnings: list[str],
) -> tuple[str, list[str]]:
    """When cross-page resolution can't even start (no cookies, no XHTML),
    rewrite every CROSSPAGE placeholder to a generic graceful-warning
    blockquote so the literal `<<crosspage:N>>` token doesn't end up in
    the committed markdown."""
    import re as _re
    from lib.cross_page_resolve import build_warning_markdown  # noqa: WPS433
    from lib.markdown_transform import md_link_dest  # noqa: WPS433

    new_md = md
    for unk in report.cross_page_unknowns:
        position = unk.get("position", 0)
        warning_md = build_warning_markdown(
            "(cross-page attachment)",
            "(source page unavailable)",
            base_url, space_key,
        )
        old_url_enc = md_link_dest(f"images/CROSSPAGE-{position}.bin")
        pat = (
            r"\[<<crosspage:" + str(position) + r">>\]\("
            + _re.escape(old_url_enc)
            + r"\)<!-- crosspage position=" + str(position) + r" -->"
        )
        new_md = _re.sub(pat, lambda _m, w=warning_md: w, new_md)
        report.cross_page_unresolved.append({
            "filename": "",
            "source_page_title": "",
            "source_page_id": "",
            "reason": "resolver could not start (no cookies / no xhtml)",
        })
    return new_md, warnings


def _format_attachment_size(size: Any) -> str:
    """Render Confluence's `extensions.fileSize` (bytes, int) as a
    short human-readable string (KB / MB). Returns '-' when missing."""
    try:
        n = int(size)
    except (TypeError, ValueError):
        return "-"
    if n < 1024:
        return f"{n} B"
    if n < 1024 * 1024:
        return f"{n / 1024:.1f} KB"
    return f"{n / (1024 * 1024):.1f} MB"


def _attachment_labels(att: dict) -> list[str]:
    """Pull the user-applied label names from an attachment record's
    `metadata.labels.results[]`. Empty list when labels weren't expanded
    or none are set."""
    md = att.get("metadata") or {}
    labels_block = md.get("labels") or {}
    results = labels_block.get("results") or []
    out: list[str] = []
    for entry in results:
        if isinstance(entry, dict):
            name = entry.get("name")
            if name:
                out.append(str(name))
    return out


def _filter_attachments_by_macro(
    attachments: list[dict],
    *,
    labels: str | None,
    name_filter: str | None,
) -> list[dict]:
    """Filter a page's full attachment list by an Attachments-macro's
    parameters.

    `labels` follows Confluence macro semantics: comma-separated values
    are OR'd (an attachment matches if it carries ANY of the listed
    labels). `name_filter` matches a substring against the attachment
    title (case-insensitive) — this is the more conservative read of
    the macro's `name` parameter, which Confluence treats as a glob in
    some renderers.

    When `labels` is None and `name_filter` is None, every attachment
    is returned (the macro renders the whole list).
    """
    selected: list[dict] = []
    label_set: set[str] | None = None
    if labels:
        label_set = {x.strip() for x in labels.split(",") if x.strip()}
    name_lower = name_filter.lower() if name_filter else None
    for att in attachments:
        if label_set is not None:
            attach_labels = set(_attachment_labels(att))
            if not (label_set & attach_labels):
                continue
        if name_lower:
            title = (att.get("title") or "").lower()
            if name_lower not in title:
                continue
        selected.append(att)
    return selected


def _render_attachment_table(filtered: list[dict]) -> str:
    """Render an attachments-macro file list as a markdown table.

    Columns: Filename | Size | Modified | Labels. Filename links to the
    locally-downloaded copy under `images/<title>` (the path the
    `_download_images` infrastructure populates)."""
    if not filtered:
        return "_No attachments matched this macro's filter._"
    lines = ["| Filename | Size | Modified | Labels |", "| --- | --- | --- | --- |"]
    for att in filtered:
        title = att.get("title") or "(unnamed)"
        # Escape pipe in title for table-cell safety
        safe_title = title.replace("|", "\\|")
        ext = att.get("extensions") or {}
        size = _format_attachment_size(ext.get("fileSize"))
        version = att.get("version") or {}
        when = version.get("when") or ext.get("when") or "-"
        labels = ", ".join(_attachment_labels(att)) or "-"
        # Local download path lines up with the `_download_images`
        # output: `<target_dir>/images/<filename>`. URL-encode the
        # destination so spaces / parens / etc. in `title` don't break
        # the markdown link parser; bracketed link text stays raw.
        local_ref = md_link_dest(f"images/{title}")
        lines.append(
            f"| [{safe_title}]({local_ref}) | {size} | {when} | {labels} |"
        )
    return "\n".join(lines)


def _load_manifest_pages(manifest_path: str) -> tuple[list[dict], str]:
    """Read `.manifest.json` from disk and return its raw `pages[]` list
    plus the staging-root prefix used to resolve relative paths. The
    manifest's `target_path` strings are repo-relative — the action
    layer's relpath calculation needs the same anchor."""
    if not manifest_path:
        return [], ""
    try:
        from lib.manifest import read_manifest  # noqa: WPS433
        m = read_manifest(Path(manifest_path))
    except Exception:  # noqa: BLE001
        return [], ""
    pages = []
    for p in m.pages:
        pages.append({
            "id": p.id,
            "title": p.title,
            "parent_id": p.parent_id or "",
            "depth": p.depth,
            "target_path": p.target_path,
            "is_container": p.is_container,
            "child_count": p.child_count,
        })
    return pages, ""


def _children_of(pages: list[dict], parent_id: str) -> list[dict]:
    """Return children of `parent_id` in the order they appear in the
    manifest (Confluence's child_position order — stable across pulls)."""
    return [p for p in pages if p.get("parent_id") == parent_id]


def _render_child_index_list(
    children: list[dict],
    *,
    self_target: Path,
    repo_root: Path,
) -> str:
    """Render a markdown bullet list of children with paths relative to
    `self_target`. Each bullet is `- [<title>](<rel-path>)`."""
    if not children:
        return "_(no child pages)_"
    self_dir = self_target.parent
    lines: list[str] = []
    for child in children:
        title = child.get("title") or "(untitled)"
        target = child.get("target_path") or ""
        if not target:
            continue
        # `target_path` may be repo-relative (preferred). Resolve to an
        # absolute path then compute relpath from `self_dir`.
        abs_target = (repo_root / target).resolve()
        try:
            rel = os.path.relpath(abs_target, start=self_dir)
        except ValueError:
            rel = target
        rel_enc = md_link_dest(rel)
        lines.append(f"- [{title}]({rel_enc})")
    return "\n".join(lines) if lines else "_(no child pages)_"


def _expand_child_index_macros(
    md: str,
    *,
    page_id: str,
    target_path: Path,
    manifest_pages: list[dict],
    repo_root: Path,
    report: NormalizationReport,
) -> tuple[str, list[str]]:
    """Splice rendered child-index bullet lists between OPEN/CLOSE
    AUTO:CHILD-INDEX sentinels (one pair per macro). Returns
    `(rewritten_md, warnings)`.

    When the manifest is empty or the page isn't found, emits a
    deferred-render comment between the sentinels rather than failing
    the adopt — the page is still readable and a re-adopt with the
    manifest path will fill the TOC in."""
    warnings: list[str] = []
    if not report.child_index_macros:
        return md, warnings

    children = _children_of(manifest_pages, page_id) if manifest_pages else []
    new_text = md

    import re as _re
    for macro in report.child_index_macros:
        position = macro.get("position")
        if not manifest_pages:
            rendered = (
                "<!-- child-index render skipped: "
                "--manifest-path not provided -->"
            )
        elif not children:
            rendered = "_(no child pages)_"
        else:
            rendered = _render_child_index_list(
                children,
                self_target=target_path,
                repo_root=repo_root,
            )
        open_pat = _re.compile(
            r"<!--\s*AUTO:CHILD-INDEX\b[^>]*?position="
            + _re.escape(str(position))
            + r"\b[^>]*?-->",
        )
        close_pat = _re.compile(
            r"<!--\s*/AUTO:CHILD-INDEX\b[^>]*?position="
            + _re.escape(str(position))
            + r"\b[^>]*?-->",
        )
        m_open = open_pat.search(new_text)
        m_close = close_pat.search(new_text, m_open.end() if m_open else 0)
        if not m_open or not m_close:
            warnings.append(
                f"child-index macro position={position}: "
                f"sentinel pair not found; skipping splice"
            )
            continue
        replacement = (
            new_text[m_open.start():m_open.end()]
            + "\n\n"
            + rendered
            + "\n\n"
            + new_text[m_close.start():m_close.end()]
        )
        new_text = (
            new_text[:m_open.start()]
            + replacement
            + new_text[m_close.end():]
        )
    return new_text, warnings


def _maybe_synthesize_stub_container(
    md: str,
    *,
    page_id: str,
    target_path: Path,
    manifest_pages: list[dict],
    repo_root: Path,
    report: NormalizationReport,
) -> tuple[str, bool, list[str]]:
    """Q5b: when the page is a container in the manifest AND the body
    has no child-index macro, append an AUTO:CHILD-INDEX block at the
    end of the body. Source attribute = `stub-container` so publish-side
    fully strips it (no source macro to reconstruct).

    Returns `(rewritten_md, synthesized: bool, warnings)`."""
    warnings: list[str] = []
    if report.child_index_macros:
        return md, False, warnings  # body already has a macro
    if not manifest_pages:
        return md, False, warnings
    self_page = next(
        (p for p in manifest_pages if p.get("id") == page_id), None
    )
    if self_page is None or not self_page.get("is_container"):
        return md, False, warnings
    children = _children_of(manifest_pages, page_id)
    if not children:
        return md, False, warnings

    # Synthesize at position=0 (no other AUTO:CHILD-INDEX macros exist).
    # `source=stub-container` distinguishes this from real macros so
    # publish-side can drop the entire block (and not emit an extension
    # node) — there was no source macro to round-trip.
    open_s = (
        "<!-- AUTO:CHILD-INDEX source=stub-container position=0 -->"
    )
    close_s = "<!-- /AUTO:CHILD-INDEX position=0 -->"
    rendered = _render_child_index_list(
        children, self_target=target_path, repo_root=repo_root,
    )
    block = "\n\n## Child pages\n\n" + open_s + "\n\n" + rendered + "\n\n" + close_s + "\n"
    new_md = md.rstrip("\n") + block
    return new_md, True, warnings


def _render_jira_table(issues: list[dict], base_url: str) -> str:
    """Render Jira REST search results as a markdown table."""
    if not issues:
        return "_(no Jira issues match this query)_"
    base = base_url.rstrip("/")
    lines = ["| Key | Summary | Status | Updated |", "| --- | --- | --- | --- |"]
    for issue in issues:
        key = issue.get("key") or "?"
        fields = issue.get("fields") or {}
        summary = (fields.get("summary") or "").replace("|", "\\|")
        status = ((fields.get("status") or {}).get("name") or "-").replace("|", "\\|")
        updated = (fields.get("updated") or "-").replace("|", "\\|")
        url = f"{base}/browse/{key}"
        lines.append(f"| [{key}]({url}) | {summary} | {status} | {updated} |")
    return "\n".join(lines)


def _expand_jira_macros(
    md: str,
    base_url: str,
    report: NormalizationReport,
) -> tuple[str, list[str]]:
    """Splice rendered Jira issue tables between AUTO:JIRA-LIST sentinels.
    Graceful-degrades to a deferred-render comment on auth/endpoint
    failure — never fails the adopt."""
    warnings: list[str] = []
    if not report.jira_macros:
        return md, warnings

    # Lazy import — keep tests / offline use working when web-control
    # isn't on disk. extract_confluence_cookies returns a header string
    # (already `key=val; key=val; ...`).
    cookie_header: str | None = None
    try:
        from lib.attachments import extract_confluence_cookies  # type: ignore
        result = extract_confluence_cookies(base_url)
        if isinstance(result, dict):
            cookie_header = "; ".join(f"{k}={v}" for k, v in result.items())
        else:
            cookie_header = str(result) if result else None
    except Exception as exc:  # noqa: BLE001
        warnings.append(f"jira: cookie bridge failed: {exc}")
        cookie_header = None

    import re as _re
    from urllib.parse import quote

    new_text = md
    for macro in report.jira_macros:
        position = macro.get("position")
        jql = macro.get("jql") or ""
        if not jql:
            rendered = "<!-- jira-list render deferred: empty JQL -->"
        elif not cookie_header:
            rendered = "<!-- jira-list render deferred: no auth cookies -->"
        else:
            try:
                from urllib.request import Request, urlopen
                count = macro.get("count") or macro.get("max_issues") or 50
                try:
                    max_results = int(count)
                except (TypeError, ValueError):
                    max_results = 50
                url = (
                    base_url.rstrip("/")
                    + "/wiki/rest/api/3/search?jql="
                    + quote(jql, safe="")
                    + f"&fields=summary,status,updated&maxResults={max_results}"
                )
                req = Request(url, headers={
                    "Cookie": cookie_header,
                    "Accept": "application/json",
                })
                with urlopen(req, timeout=15) as resp:  # noqa: S310
                    raw = resp.read()
                payload = json.loads(raw.decode("utf-8"))
                issues = payload.get("issues") or []
                rendered = _render_jira_table(issues, base_url)
            except Exception as exc:  # noqa: BLE001
                warnings.append(f"jira position={position}: {exc}")
                rendered = (
                    "<!-- jira-list render deferred: "
                    f"{type(exc).__name__} -->"
                )

        open_pat = _re.compile(
            r"<!--\s*AUTO:JIRA-LIST\b[^>]*?position="
            + _re.escape(str(position))
            + r"\b[^>]*?-->",
        )
        close_pat = _re.compile(
            r"<!--\s*/AUTO:JIRA-LIST\b[^>]*?position="
            + _re.escape(str(position))
            + r"\b[^>]*?-->",
        )
        m_open = open_pat.search(new_text)
        m_close = close_pat.search(new_text, m_open.end() if m_open else 0)
        if not m_open or not m_close:
            warnings.append(
                f"jira position={position}: sentinel pair not found"
            )
            continue
        replacement = (
            new_text[m_open.start():m_open.end()]
            + "\n\n"
            + rendered
            + "\n\n"
            + new_text[m_close.start():m_close.end()]
        )
        new_text = (
            new_text[:m_open.start()]
            + replacement
            + new_text[m_close.end():]
        )
    return new_text, warnings


def _expand_attachment_macros(
    md: str,
    base_url: str,
    page_id: str,
    report: NormalizationReport,
) -> tuple[str, list[dict], list[str]]:
    """Splice rendered attachment-list tables between OPEN/CLOSE
    sentinels emitted by the normalizer for each `extensionKey="attachments"`
    macro occurrence on the page.

    Returns `(rewritten_md, synthetic_images, warnings)`:
      - `rewritten_md` — markdown with the rendered tables inline
      - `synthetic_images` — list of `report.images`-shaped entries
        (one per unique attachment filename) that the existing
        `_download_images` infrastructure will pull onto disk under
        `<target_dir>/images/`
      - `warnings` — non-fatal one-line strings the caller surfaces

    Failures degrade gracefully: if cookies / the attachment endpoint
    are unreachable, the OPEN/CLOSE sentinels stay in place (so a
    re-adopt can fill them in later) and a warning is added.
    """
    warnings: list[str] = []
    if not report.attachment_macros:
        return md, [], warnings

    # Lazy import — keeps the module importable in unit tests that
    # never reach this branch.
    try:
        from lib.attachments import (  # type: ignore
            extract_confluence_cookies,
            list_attachments,
        )
    except ImportError as exc:
        warnings.append(f"attachments lib missing: {exc}")
        return md, [], warnings

    try:
        cookies = extract_confluence_cookies(base_url)
    except Exception as exc:  # noqa: BLE001 — degrade gracefully
        warnings.append(f"cookie bridge failed: {exc}")
        return md, [], warnings

    try:
        all_atts = list_attachments(
            base_url, page_id, cookies, expand_labels=True
        )
    except Exception as exc:  # noqa: BLE001
        warnings.append(f"list_attachments({page_id}): {exc}")
        return md, [], warnings

    import re as _re
    new_text = md
    seen_filenames: set[str] = set()
    synthetic: list[dict] = []

    for macro in report.attachment_macros:
        position = macro.get("position")
        labels = macro.get("labels")
        name_filter = macro.get("name_filter")
        filtered = _filter_attachments_by_macro(
            all_atts, labels=labels, name_filter=name_filter
        )
        rendered = _render_attachment_table(filtered)
        # Splice between the OPEN and CLOSE sentinels, matched by
        # position marker. Tolerate any whitespace between them
        # (the normalizer emits them with a newline between, but
        # other passes may have collapsed it).
        open_pat = _re.compile(
            r"<!--\s*confluence-side:\s*attachments[^>]*?position="
            + _re.escape(str(position))
            + r"\b[^>]*?-->",
        )
        close_pat = _re.compile(
            r"<!--\s*/confluence-side:\s*attachments[^>]*?position="
            + _re.escape(str(position))
            + r"\b[^>]*?-->",
        )
        m_open = open_pat.search(new_text)
        m_close = close_pat.search(new_text, m_open.end() if m_open else 0)
        if not m_open or not m_close:
            warnings.append(
                f"attachments-macro position={position}: "
                f"sentinel pair not found; skipping splice"
            )
            continue
        replacement = (
            new_text[m_open.start():m_open.end()]
            + "\n\n"
            + rendered
            + "\n\n"
            + new_text[m_close.start():m_close.end()]
        )
        new_text = (
            new_text[:m_open.start()]
            + replacement
            + new_text[m_close.end():]
        )

        # Queue downloads for each unique attachment filename. Reuse the
        # `report.images`-shaped contract so `_download_images` handles
        # cookie reuse + dedupe + error reporting.
        for att in filtered:
            title = att.get("title") or ""
            if not title or title in seen_filenames:
                continue
            seen_filenames.add(title)
            synthetic.append({
                "media_id": "",
                "collection": "",
                "filename": title,
                "alt": title,
                "target_relpath": f"images/{title}",
                "url": f"images/{title}",
                "width": None,
                "height": None,
                "type": "file",
                "node_type": "attachments-macro",
                "style": "block",
                "render": "file",
                "needs_filename": False,
            })

    return new_text, synthetic, warnings


# ---- AUTO:PAGE-TITLE + AUTO:TOC chrome (task 140 / v0.13.0) ----
#
# Two coupled chrome blocks shipped together:
#   - AUTO:PAGE-TITLE — emit the page title as a visible H1 at the top
#     of the markdown body, mirroring Confluence's title bar. Suppressed
#     when the body's first content block is already `# <page_title>`
#     so we don't double-render in markdown viewers.
#   - AUTO:TOC — when the source has `extension key="toc"` (Confluence's
#     Table of Contents macro), render the body's heading hierarchy as
#     a clickable anchor list between sentinels.
#
# Both round-trip-safe via the AUTO-sentinel infrastructure shipped in
# v0.10.0/v0.12.0. Publish-side strip lives in
# `actions/publish_helper.py:_md_to_adf` (PAGE-TITLE → emit nothing,
# TOC → emit single ADF `extension key="toc"` node).


def _synthesize_page_title(body_md: str, page_title: str) -> str:
    """Emit AUTO:PAGE-TITLE block at the top of the body unless the
    body already starts with an H1 matching the page title.

    Detection: walk past leading blank lines, AUTO sentinels, and
    confluence-side comments to find the first content line. If that
    line is `# <page_title>` (after rstrip), suppress the auto block.

    Otherwise return:
        <!-- AUTO:PAGE-TITLE -->
        # <page_title>
        <!-- /AUTO:PAGE-TITLE -->

        <body_md>

    Title is emitted verbatim — no escaping. Page titles in Confluence
    that contain `#`, `[`, etc. would already round-trip via the title
    arg on the API call; the auto block is purely for local viewing.
    """
    if not page_title:
        return body_md

    # Find first content line.
    import re as _re
    lines = body_md.split("\n")
    i = 0
    while i < len(lines):
        s = lines[i].strip()
        if not s:
            i += 1
            continue
        # Skip auto sentinels and confluence-side comments
        if _re.match(r"<!--\s*(/?AUTO:|/?confluence-side:)", s):
            i += 1
            continue
        break
    first_line = lines[i].rstrip() if i < len(lines) else ""
    expected_h1 = f"# {page_title}".rstrip()
    if first_line == expected_h1:
        return body_md

    auto_block = (
        "<!-- AUTO:PAGE-TITLE -->\n"
        f"# {page_title}\n"
        "<!-- /AUTO:PAGE-TITLE -->"
    )
    if body_md.lstrip():
        return auto_block + "\n\n" + body_md.lstrip("\n")
    return auto_block + "\n"


def _slugify_anchor(text: str) -> str:
    """GitHub-style anchor slug for a heading.

    Lowercase; spaces become hyphens; non-alphanumeric (except `-`/`_`)
    stripped; runs of `-` collapsed.
    """
    import re as _re
    s = text.strip().lower()
    # Replace spaces (and runs of whitespace) with hyphens
    s = _re.sub(r"\s+", "-", s)
    # Strip everything except a-z0-9-_
    s = _re.sub(r"[^a-z0-9\-_]", "", s)
    # Collapse runs of -
    s = _re.sub(r"-+", "-", s)
    return s.strip("-")


def _walk_headings_outside_auto(body_md: str) -> list[tuple[int, str]]:
    """Return list of (level, text) for every ATX heading in `body_md`
    that lives OUTSIDE any AUTO:<KIND> region (CHILD-INDEX, JIRA-LIST,
    PAGE-TITLE, TOC itself, etc.) and outside fenced code blocks.

    Setext-style headings (--- under text) are not in scope — the
    normalizer emits ATX `# ... ######` exclusively.
    """
    import re as _re
    headings: list[tuple[int, str]] = []
    in_code = False
    in_auto = 0  # nesting depth of AUTO regions
    h_re = _re.compile(r"^(#{1,6})\s+(.+?)\s*$")
    auto_open = _re.compile(r"^\s*<!--\s*AUTO:[A-Z][A-Z0-9-]*\b[^>]*-->\s*$")
    auto_close = _re.compile(r"^\s*<!--\s*/AUTO:[A-Z][A-Z0-9-]*\b[^>]*-->\s*$")
    fence_re = _re.compile(r"^\s*```")
    for line in body_md.split("\n"):
        if fence_re.match(line):
            in_code = not in_code
            continue
        if in_code:
            continue
        if auto_open.match(line):
            in_auto += 1
            continue
        if auto_close.match(line):
            if in_auto > 0:
                in_auto -= 1
            continue
        if in_auto > 0:
            continue
        m = h_re.match(line)
        if m:
            level = len(m.group(1))
            text = m.group(2).strip()
            headings.append((level, text))
    return headings


def _render_toc_list(
    headings: list[tuple[int, str]],
    *,
    min_level: int,
    max_level: int,
) -> str:
    """Render an anchored bullet list. Indent nested levels by 2 spaces
    per heading-level above `min_level`."""
    seen_slugs: dict[str, int] = {}
    lines: list[str] = []
    for level, text in headings:
        if level < min_level or level > max_level:
            continue
        slug = _slugify_anchor(text) or "section"
        # GitHub disambiguates duplicate slugs with -1, -2, ...
        if slug in seen_slugs:
            seen_slugs[slug] += 1
            slug = f"{slug}-{seen_slugs[slug]}"
        else:
            seen_slugs[slug] = 0
        indent = "  " * (level - min_level)
        lines.append(f"{indent}- [{text}](#{slug})")
    if not lines:
        return "_(no headings to render)_"
    return "\n".join(lines)


def _expand_toc_macros(
    md: str, report: NormalizationReport
) -> tuple[str, list[str]]:
    """Splice rendered TOC bullet lists between OPEN/CLOSE AUTO:TOC
    sentinels (one pair per macro). Returns `(rewritten_md, warnings)`.

    Run AFTER all other expanders (attachment-macro, child-index,
    jira-list, page-title) so the heading hierarchy reflects the
    fully-resolved body. Headings inside any AUTO region are skipped
    so the rendered tables / bullet lists don't pollute the TOC.
    """
    import re as _re
    warnings: list[str] = []
    if not report.toc_macros:
        return md, warnings

    # Compute the heading list once — same view for every TOC macro.
    headings = _walk_headings_outside_auto(md)
    new_text = md
    for macro in report.toc_macros:
        position = macro.get("position")
        try:
            min_level = int(macro.get("min_level") or 1)
        except (TypeError, ValueError):
            min_level = 1
        try:
            max_level = int(macro.get("max_level") or 6)
        except (TypeError, ValueError):
            max_level = 6
        min_level = max(1, min(6, min_level))
        max_level = max(min_level, min(6, max_level))
        rendered = _render_toc_list(
            headings, min_level=min_level, max_level=max_level
        )
        open_pat = _re.compile(
            r"<!--\s*AUTO:TOC\b[^>]*?position="
            + _re.escape(str(position))
            + r"\b[^>]*?-->",
        )
        close_pat = _re.compile(
            r"<!--\s*/AUTO:TOC\b[^>]*?position="
            + _re.escape(str(position))
            + r"\b[^>]*?-->",
        )
        m_open = open_pat.search(new_text)
        m_close = close_pat.search(new_text, m_open.end() if m_open else 0)
        if not m_open or not m_close:
            warnings.append(
                f"toc-macro position={position}: "
                f"sentinel pair not found; skipping splice"
            )
            continue
        replacement = (
            new_text[m_open.start():m_open.end()]
            + "\n\n"
            + rendered
            + "\n\n"
            + new_text[m_close.start():m_close.end()]
        )
        new_text = (
            new_text[:m_open.start()]
            + replacement
            + new_text[m_close.end():]
        )
    return new_text, warnings


def cmd_write(args: argparse.Namespace, raw: dict) -> int:
    image_mode = "local" if getattr(args, "download_images", False) else "url"
    md, report = normalize(raw, args.base_url, image_mode=image_mode)
    fm = build_frontmatter(
        raw,
        space_key=args.space_key,
        parent_page_id=args.parent_page_id,
        page_path=args.page_path,
        adopted_at=args.adopted_at or _today_utc(),
    )
    # AUTO:PAGE-TITLE chrome (task 140 / v0.13.0). Emitted at the top of
    # the body BEFORE every other expander, so subsequent passes that
    # skip AUTO regions (e.g., AUTO:TOC walking the heading hierarchy)
    # see this as a stable AUTO block. Suppressed when the body's first
    # content is already `# <page_title>` (avoid double-render in
    # markdown viewers). Publish-side strip in `_md_to_adf` ensures the
    # block contributes nothing to the round-trip ADF (the title goes
    # through the API's `title` argument, not the body).
    md = _synthesize_page_title(md, str(fm.get("title") or ""))

    # Attachments-macro expander — runs before the snapshot so the
    # cached body already includes the rendered file list and divergence
    # detection compares apples-to-apples on next pull. Synthetic image
    # refs are appended to `report.images` so the existing image-download
    # path picks them up and lands binaries under `<target_dir>/images/`.
    page_id_str = str(fm["confluence"]["page_id"])
    macro_synthetic_count = 0
    if report.attachment_macros and image_mode == "local":
        md, synthetic_imgs, macro_warnings = _expand_attachment_macros(
            md, args.base_url, page_id_str, report
        )
        report.images.extend(synthetic_imgs)
        macro_synthetic_count = len(synthetic_imgs)
        if macro_warnings:
            print("attachments-macro warnings:", file=sys.stderr)
            for w in macro_warnings[:10]:
                print(f"  - {w}", file=sys.stderr)
    target = Path(args.target)

    # Child-index + stub-container expanders (task 131). Both the
    # children/pagetree macro path and the synthesized stub-container
    # path render into AUTO:CHILD-INDEX sentinel pairs. The sentinel-
    # aware diff strips both before comparing, so the auto regions
    # never trigger spurious conflicts on re-adopt.
    manifest_path = getattr(args, "manifest_path", "") or ""
    repo_root_str = getattr(args, "repo_root", "") or ""
    repo_root = Path(repo_root_str) if repo_root_str else Path.cwd()
    manifest_pages: list[dict] = []
    if manifest_path:
        manifest_pages, _ = _load_manifest_pages(manifest_path)
    if report.child_index_macros:
        md, ci_warnings = _expand_child_index_macros(
            md,
            page_id=page_id_str,
            target_path=target,
            manifest_pages=manifest_pages,
            repo_root=repo_root,
            report=report,
        )
        if ci_warnings:
            print("child-index warnings:", file=sys.stderr)
            for w in ci_warnings[:10]:
                print(f"  - {w}", file=sys.stderr)
    md, stub_synthesized, stub_warnings = _maybe_synthesize_stub_container(
        md,
        page_id=page_id_str,
        target_path=target,
        manifest_pages=manifest_pages,
        repo_root=repo_root,
        report=report,
    )
    if stub_warnings:
        print("stub-container warnings:", file=sys.stderr)
        for w in stub_warnings[:10]:
            print(f"  - {w}", file=sys.stderr)

    # Jira-macro expander — runs against the live cookie bridge but
    # gracefully degrades to a deferred-render comment on auth failure.
    if report.jira_macros:
        md, j_warnings = _expand_jira_macros(md, args.base_url, report)
        if j_warnings:
            print("jira-list warnings:", file=sys.stderr)
            for w in j_warnings[:10]:
                print(f"  - {w}", file=sys.stderr)

    # AUTO:TOC chrome — runs LAST so the heading hierarchy reflects the
    # fully-resolved body (incl. any headings the other expanders
    # produced). Headings inside any AUTO region (CHILD-INDEX, JIRA-LIST,
    # PAGE-TITLE) are skipped so the rendered tables / bullet lists
    # don't pollute the TOC. Round-trips back to a single ADF
    # `extension key="toc"` node on publish.
    if report.toc_macros:
        md, toc_warnings = _expand_toc_macros(md, report)
        if toc_warnings:
            print("auto-toc warnings:", file=sys.stderr)
            for w in toc_warnings[:10]:
                print(f"  - {w}", file=sys.stderr)

    # ---- Adopt-direction drift detection (task 130) ----
    on_conflict = getattr(args, "on_conflict", "prompt")
    force = getattr(args, "force", False)
    decision: AdoptSyncDecision | None = None
    if not force:
        decision = classify_adopt(
            target,
            page_id_str,
            md,
            read_snapshot=lambda pid, ver: read_snapshot(
                pid, ver, cache_root=args.cache_root
            ),
            read_local_body=default_read_local_body,
            read_local_anc_version=default_read_local_anc_version,
        )
        action = decision.action
        if action == "in_sync":
            print(
                f"adopt: {page_id_str} -> {target} (in_sync, no-op): "
                f"{decision.reason}",
                file=sys.stderr,
            )
            return 0
        if action == "only_yours":
            # Confluence unchanged since v_anc; preserve local edits.
            # Bump frontmatter pointer to the current version so next
            # diff is anchored to the freshest known anchor — body of
            # snapshot at that pointer remains the (still-correct) anc.
            new_version = int(fm["confluence"]["last_published_version"])
            update_frontmatter(
                target,
                confluence={
                    "adopted_from_version": new_version,
                    "last_published_version": new_version,
                },
            )
            print(
                f"adopt: {page_id_str} -> {target} (only_yours, preserved "
                f"local edits, frontmatter pointer refreshed to v{new_version}): "
                f"{decision.reason}",
                file=sys.stderr,
            )
            return 0
        if action == "conflict":
            if on_conflict == "overwrite":
                # Fall through to the normal write path.
                print(
                    f"adopt: {page_id_str} -> {target} (conflict, "
                    f"--on-conflict=overwrite, accepting Confluence body)",
                    file=sys.stderr,
                )
            elif on_conflict == "abort":
                print(
                    f"adopt: {page_id_str} -> {target} (conflict, "
                    f"--on-conflict=abort, leaving local file untouched): "
                    f"{decision.reason}",
                    file=sys.stderr,
                )
                return 2
            else:
                # `prompt` (default) and `merge`: emit side-by-side files
                # and exit non-zero with a structured prompt on stderr.
                their_path, diff_path = write_conflict_files(
                    target, decision, page_id=page_id_str
                )
                prompt = render_conflict_prompt(
                    target,
                    decision,
                    page_id=page_id_str,
                    their_path=their_path,
                    diff_path=diff_path,
                )
                print(prompt, file=sys.stderr)
                return 3
        # `fresh` and `only_theirs` (and conflict-overwrite) all proceed
        # to the normal write path below.

    write_frontmatter(target, fm, md)
    snap_path = write_snapshot(
        page_id=str(fm["confluence"]["page_id"]),
        version=int(fm["confluence"]["last_published_version"]),
        markdown=md,
        cache_root=args.cache_root,
    )
    # Image download pass — only when --download-images is set. Failures
    # degrade gracefully: we keep the markdown reference (now pointing at
    # `images/<file>`) and surface the error count so the agent can warn
    # the user. The page is still readable; images simply won't render
    # until a successful re-adopt fills in the binaries.
    download_summary = None
    if image_mode == "local":
        target_dir = target.parent
        downloaded, failed, errors, resolutions = _download_images(
            args.base_url,
            str(fm["confluence"]["page_id"]),
            target_dir,
            report.images,
            target_md_file=target,
        )
        download_summary = {
            "downloaded": downloaded,
            "failed": failed,
            "total_refs": len(report.images),
            "resolved": len(resolutions),
        }
        if errors:
            print(
                "image-download warnings:",
                file=sys.stderr,
            )
            for err in errors[:10]:
                print(f"  - {err}", file=sys.stderr)

    # Cross-page UNKNOWN_MEDIA_ID resolution. The Atlassian REST
    # `body.atlas_doc_format` endpoint emits literal "UNKNOWN_MEDIA_ID" for
    # media nodes whose attachment lives on another page. Storage XHTML
    # preserves the original `<ri:attachment ri:filename ri:content-title>`,
    # so we dual-fetch and pair by structural traversal order.
    if report.cross_page_unknowns and image_mode == "local":
        # Optional source-map JSON file (title -> source_page_id). Lets the
        # agent supply pre-resolved CQL search results.
        cp_source_map: dict[str, str] = {}
        cp_source_map_path = getattr(args, "cross_page_source_map", "") or ""
        if cp_source_map_path:
            try:
                cp_source_map = json.loads(
                    Path(cp_source_map_path).read_text(encoding="utf-8")
                )
                if not isinstance(cp_source_map, dict):
                    cp_source_map = {}
            except (OSError, ValueError) as exc:
                print(
                    f"cross-page: failed to load --cross-page-source-map: {exc}",
                    file=sys.stderr,
                )
                cp_source_map = {}
        # Deterministic fallback from project.yml: when no JSON file was
        # passed, look up THIS page in `change_control.cross_page_source_map`.
        # The config carries (filename, source_page_title) hints; we shim
        # them into a {title: ""} map so the resolver still graceful-warns
        # with the configured source-page title instead of UNKNOWN.
        if not cp_source_map and read_change_control_config is not None:
            try:
                cfg = read_change_control_config()
            except Exception:  # noqa: BLE001
                cfg = None
            if cfg is not None and cfg.cross_page_source_map:
                from lib.cross_page_resolve import (  # noqa: WPS433
                    project_config_source_map,
                )
                cp_source_map = project_config_source_map(
                    page_id_str, cfg.cross_page_source_map,
                )
        new_md, cp_warnings = _resolve_cross_page_attachments(
            md,
            base_url=args.base_url,
            space_key=args.space_key,
            page_id=page_id_str,
            target_dir=target.parent,
            target_md_file=target,
            report=report,
            storage_xhtml_input=getattr(args, "storage_xhtml_input", "") or "",
            source_map=cp_source_map,
        )
        if new_md != md:
            md = new_md
            # Re-write the target file with resolved markdown (preserving
            # frontmatter from the earlier write_frontmatter call) and
            # refresh the snapshot so divergence detection on next pull
            # compares against the resolved form.
            try:
                # Re-write with the resolved markdown body, preserving
                # the frontmatter dict written above. `read_frontmatter`
                # gives us the parsed FM block; `write_frontmatter` re-
                # serializes with the new body.
                fm_now = read_frontmatter(target)
                write_frontmatter(target, fm_now.data, md)
            except Exception as exc:  # noqa: BLE001
                print(
                    f"cross-page: failed to write resolved markdown: {exc}",
                    file=sys.stderr,
                )
            snap_path = write_snapshot(
                page_id=str(fm["confluence"]["page_id"]),
                version=int(fm["confluence"]["last_published_version"]),
                markdown=md,
                cache_root=args.cache_root,
            )
        if cp_warnings:
            print("cross-page warnings:", file=sys.stderr)
            for w in cp_warnings[:20]:
                print(f"  - {w}", file=sys.stderr)
    print(render_summary(target, fm, report, snap_path, download_summary))
    # Emit resolution-needs report for the action layer. Lists every
    # smartcard that has no local label — the agent batches MCP
    # `getConfluencePage` calls for these and feeds the results back via
    # `resolve-smartcards`. Always emitted (possibly empty) so the agent
    # can deterministically parse stderr.
    needs = [
        {
            "placeholder_key": l.get("page_id") or (f"x{l['tinyui']}" if l.get("tinyui") else None),
            "page_id": l.get("page_id"),
            "tinyui": l.get("tinyui"),
            "url": l.get("url"),
        }
        for l in report.smart_links
        if not l.get("label") and (l.get("page_id") or l.get("tinyui"))
    ]
    print(
        "NEEDS_RESOLUTION " + json.dumps({"target": str(target), "smartcards": needs}),
        file=sys.stderr,
    )
    return 0


def cmd_resolve_smartcards(args: argparse.Namespace) -> int:
    """Read a JSON object {key: title} from stdin and rewrite the target
    markdown file in place, replacing each `[<<smartcard:KEY>>](URL)`
    with `[<title>](URL)`. Round-trip marker `<!-- smartcard -->` is
    preserved so publish re-emits as inlineCard.
    """
    target = Path(args.target)
    if not target.is_file():
        print(f"resolve-smartcards: target not found: {target}", file=sys.stderr)
        return 64
    raw_in = sys.stdin.read()
    try:
        title_map = json.loads(raw_in) if raw_in.strip() else {}
    except ValueError as exc:
        print(f"resolve-smartcards: stdin is not valid JSON: {exc}", file=sys.stderr)
        return 65
    if not isinstance(title_map, dict):
        print("resolve-smartcards: stdin must be a JSON object {key: title}.",
              file=sys.stderr)
        return 65

    text = target.read_text()
    import re as _re
    n_resolved = 0
    n_unresolved = 0

    def _sub(m: "_re.Match[str]") -> str:
        nonlocal n_resolved, n_unresolved
        key, url = m.group(1), m.group(2)
        title = title_map.get(key)
        if title:
            n_resolved += 1
            return f"[{title}]({url})"
        n_unresolved += 1
        return m.group(0)  # unchanged — leave placeholder for future runs

    new_text = _re.sub(
        r"\[<<smartcard:([^\]>]+)>>\]\(([^)]+)\)",
        _sub,
        text,
    )
    if new_text != text:
        target.write_text(new_text)
    print(f"resolved: {n_resolved} smartcard(s) in {target}; "
          f"{n_unresolved} placeholder(s) remain.")
    return 0


# ---- Entry point ----


def _read_stdin_json() -> dict:
    raw = sys.stdin.read()
    if not raw.strip():
        print(
            "adopt_helper: no input on stdin. Pipe the MCP "
            "getConfluencePage response JSON in.",
            file=sys.stderr,
        )
        sys.exit(64)
    try:
        parsed = json.loads(raw)
    except ValueError as exc:
        print(f"adopt_helper: stdin is not valid JSON: {exc}", file=sys.stderr)
        sys.exit(65)
    if not isinstance(parsed, dict):
        print(
            f"adopt_helper: expected a JSON object on stdin, got "
            f"{type(parsed).__name__}.",
            file=sys.stderr,
        )
        sys.exit(65)
    return parsed


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.cmd == "resolve-smartcards":
        # Reads its own JSON map from stdin — not ADF.
        return cmd_resolve_smartcards(args)
    _apply_config_defaults(args)
    # Validate post-config: these are needed for the live pipelines but
    # we deferred required=True so config can fill them.
    missing = [name for name in ("base_url", "space_key") if not getattr(args, name, "")]
    if missing:
        parser.error(
            "the following required arguments are missing and not in "
            f"project.yml change_control config: {', '.join('--' + m.replace('_', '-') for m in missing)}"
        )
    raw = _read_stdin_json()
    if args.cmd == "preview":
        return cmd_preview(args, raw)
    if args.cmd == "write":
        return cmd_write(args, raw)
    parser.error(f"unknown command: {args.cmd}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
