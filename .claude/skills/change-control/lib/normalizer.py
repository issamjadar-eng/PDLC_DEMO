"""ADF → markdown normalizer.

Used by:
  - **adoption** — one-time pull of a Confluence page into the repo.
    `normalize_adf(adf, attachment_url_resolver)` walks the ADF tree and
    emits markdown; image refs are rewritten to attachment URLs the
    `adopt` action then downloads.
  - **change-detection** — divergence detection compares the cached
    snapshot's markdown against the current Confluence body. We
    normalize ADF to markdown first so reviewer-pasted bare URLs (which
    auto-smartlink) don't show up as drift against authored
    `[text](url)` source.

Project-agnostic policy:
  - `inlineCard` / `<custom data-type="smartlink">` → `[url](url)` —
    collapses smartlink rendering back to a stable markdown form
  - `media` / `mediaSingle` → `![alt](attachment_url)` (or relative
    path if `attachment_url_resolver` returns one)
  - `extension` / `bodiedExtension` → `<!-- confluence-side: <key> -->`
    placeholder. **Tool-specific recognition** (e.g., `page-signatures`
    as approval evidence) lives in the `lib.review_plugin.*` module
    that owns it — NOT here.
  - `expand` (incl. Confluence Zones marked
    `__CONFLUENCE_ZONE__: <name>`) — emitted as `<details><summary>`
    blocks; Zone titles are preserved verbatim so `lib.zones` can
    splice them back on republish.
  - Standard nodes — paragraph, heading, list, table, codeBlock,
    link, blockquote, hardBreak — emitted as standard markdown.

This is a structural normalizer, not a pixel-perfect rendering
pipeline; the goal is "round-trippable enough that a reviewer-side
edit doesn't masquerade as drift."
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

from lib.markdown_transform import md_link_dest


CONFLUENCE_ZONE_PREFIX = "__CONFLUENCE_ZONE__:"


# ---- Public API ----


@dataclass
class NormalizationReport:
    """Surfaces what the normalizer encountered — useful for
    `review-formal-status` ("Confluence-side macros enumerated") and
    for `adopt` post-run logging."""

    extensions: list[dict] = field(default_factory=list)
    media_refs: list[dict] = field(default_factory=list)
    # Each entry: {"url": str, "label": str} — label may be empty string
    # if neither the ADF nor the URL slug yielded a resolved title.
    smart_links: list[dict] = field(default_factory=list)
    zones: list[str] = field(default_factory=list)
    # Each entry: {"media_id", "collection", "filename", "alt",
    #              "target_relpath", "width", "height", "type"}.
    # The action layer reads this to download binaries and verify the
    # markdown→relpath rewrite landed correctly.
    images: list[dict] = field(default_factory=list)
    # Each entry: {"position", "labels", "name_filter", "page_size",
    #              "parent_page_id", "raw_params"}.
    # The action layer reads this to fetch the page's attachment list
    # once, filter per-macro, and splice the rendered table between the
    # OPEN/CLOSE sentinels emitted for each occurrence. `position` is the
    # unique counter the sentinels carry as `position=<n>` so the splice
    # finds the right region even when multiple macros appear on a page.
    attachment_macros: list[dict] = field(default_factory=list)
    # Each entry: {"position", "kind", "depth", "sort", "excerpt",
    #              "root", "style", "raw_params"}.
    # `kind` is "children" or "pagetree" — Confluence ships two macros
    # for the same purpose; we capture both. The action layer reads this
    # to query the manifest for child pages and splice a markdown bullet
    # list between the OPEN/CLOSE sentinels.
    child_index_macros: list[dict] = field(default_factory=list)
    # Each entry: {"position", "jql", "columns", "count", "server_id",
    #              "max_issues", "raw_params"}.
    # The action layer reads this to query Jira REST search via the
    # cookie bridge and splice a markdown table between the OPEN/CLOSE
    # sentinels. Graceful-degrades to a deferred-render comment when
    # the cookie bridge or the endpoint is unavailable.
    jira_macros: list[dict] = field(default_factory=list)
    # Each entry: {"position", "min_level", "max_level", "style",
    #              "outline", "printable", "include", "exclude",
    #              "raw_params"}.
    # The action layer reads this to walk the body's heading hierarchy
    # and splice a rendered anchor list between the OPEN/CLOSE
    # AUTO:TOC sentinels. Round-trips back to a single ADF
    # `extension key="toc"` node on publish.
    toc_macros: list[dict] = field(default_factory=list)
    # Each entry: {"position", "placeholder_id", "media_id", "collection",
    #              "node_type", "style"}.
    # The Atlassian REST `body.atlas_doc_format` endpoint emits the literal
    # string `"UNKNOWN_MEDIA_ID"` for media nodes whose attachment lives on
    # a different page than the one being fetched. Storage XHTML preserves
    # the original `<ri:attachment ri:filename ri:content-title>` so the
    # action layer can dual-fetch and resolve. `position` is the structural
    # ordinal among media nodes (matches Storage XHTML traversal order).
    cross_page_unknowns: list[dict] = field(default_factory=list)
    # Each entry: {"filename", "source_page_title", "source_page_id",
    #              "reason"}.
    # Populated by the action-layer cross-page resolver when an unknown
    # cannot be downloaded locally (search returned nothing, source page
    # not accessible, etc.). The graceful-warning placeholder still went
    # into the markdown — this is the audit trail for follow-up reporting.
    cross_page_unresolved: list[dict] = field(default_factory=list)


AttachmentURLResolver = Callable[[str, Optional[str]], str]
"""Signature: (filename, media_id_or_none) -> url.

Adopt uses this to map ADF media nodes to either a relative
`images/<filename>` path (after download) or, during divergence
detection, the live attachment URL."""


def adf_to_markdown(
    adf: Any,
    attachment_url: AttachmentURLResolver | None = None,
    report: NormalizationReport | None = None,
) -> str:
    """Convert an ADF document (parsed JSON) to markdown.

    `adf` may be the document dict itself or a JSON string. If
    `attachment_url` is None, media nodes are rewritten to a stable
    placeholder URL `confluence-attachment:<filename>` so the result
    is still diffable; production `adopt` should pass a resolver.
    """
    if isinstance(adf, str):
        adf = json.loads(adf)
    if not isinstance(adf, dict):
        return ""
    rep = report if report is not None else NormalizationReport()
    resolver = attachment_url or _default_attachment_resolver
    parts = _walk_block(adf, list_depth=0, resolver=resolver, report=rep)
    return _join_blocks(parts).rstrip() + "\n"


def normalize_for_diff(adf: Any) -> str:
    """Convenience wrapper for divergence detection: returns markdown
    with stable, diff-safe placeholders for media and extensions."""
    return adf_to_markdown(adf, attachment_url=None)


# ---- Default resolvers ----


def _default_attachment_resolver(filename: str, media_id: str | None) -> str:
    return f"confluence-attachment:{filename}"


# ---- Attachments-macro helpers ----


def _extract_macro_param(params: dict, key: str) -> str | None:
    """Pull `parameters.macroParams.<key>.value` out of an ADF extension
    attrs dict, accepting either the wrapped `{value: ...}` shape (the
    canonical Confluence form) or a bare-string fallback."""
    if not isinstance(params, dict):
        return None
    macro_params = params.get("macroParams") or {}
    entry = macro_params.get(key)
    if isinstance(entry, dict):
        v = entry.get("value")
        return str(v) if v is not None else None
    if isinstance(entry, (str, int)):
        return str(entry)
    return None


def _capture_attachment_macro(
    attrs: dict, report: NormalizationReport
) -> int:
    """Record an `extensionKey=attachments` occurrence in
    `report.attachment_macros`. Returns the unique position index the
    OPEN/CLOSE sentinels will carry (so the action-layer expander can
    splice rendered content between them)."""
    params = attrs.get("parameters") or {}
    labels = _extract_macro_param(params, "labels")
    name_filter = _extract_macro_param(params, "name")
    page_size_raw = _extract_macro_param(params, "pageSize")
    parent_page_id = _extract_macro_param(params, "_parentId")
    try:
        page_size = int(page_size_raw) if page_size_raw is not None else None
    except (TypeError, ValueError):
        page_size = None
    position = len(report.attachment_macros)
    report.attachment_macros.append({
        "position": position,
        "labels": labels,
        "name_filter": name_filter,
        "page_size": page_size,
        "parent_page_id": parent_page_id,
        "raw_params": (params.get("macroParams") or {}),
    })
    return position


def _capture_child_index_macro(
    attrs: dict, kind: str, report: NormalizationReport
) -> int:
    """Record an `extensionKey={children, pagetree}` occurrence in
    `report.child_index_macros`. Returns the position the OPEN/CLOSE
    sentinels carry."""
    params = attrs.get("parameters") or {}
    depth = _extract_macro_param(params, "depth")
    sort = _extract_macro_param(params, "sort")
    excerpt = _extract_macro_param(params, "excerpt")
    root = _extract_macro_param(params, "root")
    style = _extract_macro_param(params, "style")
    position = len(report.child_index_macros)
    report.child_index_macros.append({
        "position": position,
        "kind": kind,
        "depth": depth,
        "sort": sort,
        "excerpt": excerpt,
        "root": root,
        "style": style,
        "raw_params": (params.get("macroParams") or {}),
    })
    return position


def _child_index_open_close(
    position: int, kind: str, depth: str | None
) -> tuple[str, str]:
    """Build OPEN/CLOSE sentinel pair for a child-index macro. Note the
    uppercase `AUTO:` prefix and dashed `CHILD-INDEX` kind — distinct
    from the lowercase `confluence-side:` zone-marker form used by 0.7/0.8
    expanders. The publish-side strip + the sentinel-aware diff both
    recognize this AUTO-prefixed form."""
    parts = [f"AUTO:CHILD-INDEX source={kind}"]
    if depth:
        parts.append(f"depth={depth}")
    parts.append(f"position={position}")
    open_attrs = " ".join(parts)
    close_attrs = f"/AUTO:CHILD-INDEX position={position}"
    return f"<!-- {open_attrs} -->", f"<!-- {close_attrs} -->"


def _capture_jira_macro(
    attrs: dict, report: NormalizationReport
) -> int:
    """Record an `extensionKey=jira` occurrence in `report.jira_macros`.
    Returns the position the OPEN/CLOSE sentinels carry."""
    params = attrs.get("parameters") or {}
    jql = _extract_macro_param(params, "jqlQuery")
    columns = _extract_macro_param(params, "columns")
    count = _extract_macro_param(params, "count")
    server_id = _extract_macro_param(params, "serverId")
    max_issues = _extract_macro_param(params, "maximumIssues")
    position = len(report.jira_macros)
    report.jira_macros.append({
        "position": position,
        "jql": jql,
        "columns": columns,
        "count": count,
        "server_id": server_id,
        "max_issues": max_issues,
        "raw_params": (params.get("macroParams") or {}),
    })
    return position


def _jira_open_close(
    position: int, jql: str | None
) -> tuple[str, str]:
    """Build OPEN/CLOSE sentinel pair for a jira macro."""
    parts = ["AUTO:JIRA-LIST source=jira"]
    if jql:
        # Encode commas/spaces so the attribute parses as one token. We
        # use a minimal URL-style encoding (only the chars that would
        # break sentinel attribute splitting).
        from urllib.parse import quote
        parts.append(f"jql={quote(jql, safe='')}")
    parts.append(f"position={position}")
    open_attrs = " ".join(parts)
    close_attrs = f"/AUTO:JIRA-LIST position={position}"
    return f"<!-- {open_attrs} -->", f"<!-- {close_attrs} -->"


def _capture_toc_macro(
    attrs: dict, report: NormalizationReport
) -> int:
    """Record an `extensionKey=toc` occurrence in `report.toc_macros`.
    Returns the position the OPEN/CLOSE sentinels carry."""
    params = attrs.get("parameters") or {}
    min_level = _extract_macro_param(params, "minLevel")
    max_level = _extract_macro_param(params, "maxLevel")
    style = _extract_macro_param(params, "style")
    outline = _extract_macro_param(params, "outline")
    printable = _extract_macro_param(params, "printable")
    include = _extract_macro_param(params, "include")
    exclude = _extract_macro_param(params, "exclude")
    position = len(report.toc_macros)
    report.toc_macros.append({
        "position": position,
        "min_level": min_level,
        "max_level": max_level,
        "style": style,
        "outline": outline,
        "printable": printable,
        "include": include,
        "exclude": exclude,
        "raw_params": (params.get("macroParams") or {}),
    })
    return position


def _toc_open_close(
    position: int,
    min_level: str | None,
    max_level: str | None,
) -> tuple[str, str]:
    """Build OPEN/CLOSE sentinel pair for a toc macro.

    Carries the minimum attributes the publish path needs to rebuild
    the ADF extension on round-trip — `minLevel`, `maxLevel`, and
    `position` (the latter pairs the close sentinel with the open
    without ambiguity when multiple toc macros appear on a page).
    """
    parts = ["AUTO:TOC source=toc"]
    if min_level:
        parts.append(f"minLevel={min_level}")
    if max_level:
        parts.append(f"maxLevel={max_level}")
    parts.append(f"position={position}")
    open_attrs = " ".join(parts)
    close_attrs = f"/AUTO:TOC position={position}"
    return f"<!-- {open_attrs} -->", f"<!-- {close_attrs} -->"


def _attachments_open_close(position: int, labels: str | None) -> tuple[str, str]:
    """Build the OPEN/CLOSE sentinel pair for an attachments macro
    occurrence. Attributes carried on the OPEN sentinel are the
    minimum set the publish path needs to rebuild the macro params on
    round-trip — `labels` and `position` (the latter pairs the close
    sentinel with the open without ambiguity when multiple macros
    appear on the same page)."""
    parts = ["confluence-side: attachments"]
    if labels:
        parts.append(f"labels={labels}")
    parts.append(f"position={position}")
    open_attrs = " ".join(parts)
    close_attrs = f"/confluence-side: attachments position={position}"
    return f"<!-- {open_attrs} -->", f"<!-- {close_attrs} -->"


# ---- Walker ----


def _walk_block(
    node: dict,
    list_depth: int,
    resolver: AttachmentURLResolver,
    report: NormalizationReport,
) -> list[str]:
    """Walk a block node and return a list of markdown chunks.

    Each chunk is a self-contained block (heading, paragraph, list,
    table, code block, etc.) joined by a blank line. Inline content
    is rendered into a single-line string by `_walk_inline`.
    """
    if not isinstance(node, dict):
        return []
    t = node.get("type", "")
    content = node.get("content") or []

    if t == "doc":
        out: list[str] = []
        for child in content:
            out.extend(_walk_block(child, list_depth, resolver, report))
        return out

    if t in ("layoutSection", "layoutColumn"):
        # Confluence page layouts (one/two/three-column). For markdown, we
        # flatten to a single-column document — children render as siblings
        # with normal block separation. (Round-trip: the publish path
        # re-wraps in a single layoutColumn at width=100.)
        out = []
        for child in content:
            out.extend(_walk_block(child, list_depth, resolver, report))
        return out

    if t == "heading":
        level = int((node.get("attrs") or {}).get("level") or 1)
        level = max(1, min(level, 6))
        text = _walk_inline(content, resolver, report)
        return [f"{'#' * level} {text}".rstrip()]

    if t == "paragraph":
        text = _walk_inline(content, resolver, report)
        return [text] if text else [""]

    if t == "blockquote":
        sub_parts: list[str] = []
        for child in content:
            sub_parts.extend(_walk_block(child, list_depth, resolver, report))
        joined = _join_blocks(sub_parts)
        quoted = "\n".join(f"> {line}" if line else ">" for line in joined.split("\n"))
        return [quoted]

    if t == "bulletList":
        return [_walk_list(content, ordered=False, depth=list_depth, resolver=resolver, report=report)]

    if t == "orderedList":
        return [_walk_list(content, ordered=True, depth=list_depth, resolver=resolver, report=report)]

    if t == "codeBlock":
        lang = (node.get("attrs") or {}).get("language") or ""
        body_parts: list[str] = []
        for c in content:
            if isinstance(c, dict) and c.get("type") == "text":
                body_parts.append(c.get("text", ""))
        body = "".join(body_parts)
        return [f"```{lang}\n{body}\n```"]

    if t == "rule":
        return ["---"]

    if t == "table":
        return [_walk_table(content, resolver, report)]

    if t == "expand" or t == "nestedExpand":
        title = (node.get("attrs") or {}).get("title", "")
        is_zone = title.startswith(CONFLUENCE_ZONE_PREFIX)
        if is_zone:
            zone_name = title[len(CONFLUENCE_ZONE_PREFIX):].strip()
            report.zones.append(zone_name)
        sub_parts = []
        for child in content:
            sub_parts.extend(_walk_block(child, list_depth, resolver, report))
        inner = _join_blocks(sub_parts)
        # Author-side: emit as <details><summary>...</summary>...</details>
        # so the round-trip back to ADF preserves the Expand wrapping.
        return [
            f"<details>\n<summary>{title}</summary>\n\n{inner}\n\n</details>"
        ]

    if t in ("extension", "bodiedExtension", "inlineExtension"):
        attrs = node.get("attrs") or {}
        key = attrs.get("extensionKey") or attrs.get("extensionType") or "unknown"
        report.extensions.append({"key": key, "attrs": attrs})
        if key == "attachments":
            # Attachments macro — capture macroParams and emit OPEN +
            # CLOSE sentinel pair with a position marker. Action layer
            # splices a rendered file-list table between them.
            position = _capture_attachment_macro(attrs, report)
            labels = report.attachment_macros[position].get("labels")
            open_s, close_s = _attachments_open_close(position, labels)
            return [f"{open_s}\n{close_s}"]
        if key in ("children", "pagetree"):
            # Children/pagetree macro — capture and emit AUTO sentinel
            # pair. Action layer queries the manifest for child pages
            # and splices a markdown bullet list between them.
            position = _capture_child_index_macro(attrs, key, report)
            depth = report.child_index_macros[position].get("depth")
            open_s, close_s = _child_index_open_close(position, key, depth)
            return [f"{open_s}\n{close_s}"]
        if key == "jira":
            # Jira macro — capture and emit AUTO sentinel pair. Action
            # layer queries Jira REST search via the cookie bridge and
            # splices a markdown table between them.
            position = _capture_jira_macro(attrs, report)
            jql = report.jira_macros[position].get("jql")
            open_s, close_s = _jira_open_close(position, jql)
            return [f"{open_s}\n{close_s}"]
        if key == "toc":
            # TOC macro — capture macroParams and emit AUTO sentinel pair.
            # Action layer walks the body's heading hierarchy and splices
            # a rendered anchor list between them. Round-trips back to a
            # single ADF `extension key="toc"` node on publish.
            position = _capture_toc_macro(attrs, report)
            mac = report.toc_macros[position]
            open_s, close_s = _toc_open_close(
                position, mac.get("min_level"), mac.get("max_level")
            )
            return [f"{open_s}\n{close_s}"]
        return [f"<!-- confluence-side: {key} -->"]

    if t == "mediaSingle" or t == "mediaGroup":
        # Walk children — media nodes inside.
        out: list[str] = []
        for child in content:
            md = _render_media(child, resolver, report)
            if md:
                out.append(md)
        return out

    if t == "media":
        md = _render_media(node, resolver, report)
        return [md] if md else []

    if t == "panel":
        # info/warning/note panels — render as a blockquote with a tag
        panel_type = (node.get("attrs") or {}).get("panelType") or "info"
        sub_parts: list[str] = []
        for child in content:
            sub_parts.extend(_walk_block(child, list_depth, resolver, report))
        inner = _join_blocks(sub_parts)
        report.extensions.append({"key": f"panel:{panel_type}", "attrs": {}})
        quoted = "\n".join(f"> {line}" if line else ">" for line in inner.split("\n"))
        return [f"> **[{panel_type}]**\n{quoted}"]

    # Fallback: try inline render in case it's actually inline content
    text = _walk_inline([node], resolver, report)
    return [text] if text else []


def _walk_list(
    items: list,
    *,
    ordered: bool,
    depth: int,
    resolver: AttachmentURLResolver,
    report: NormalizationReport,
) -> str:
    """Render a list. Nested lists indent by 2 spaces per depth."""
    indent = "  " * depth
    lines: list[str] = []
    for idx, item in enumerate(items, start=1):
        if not isinstance(item, dict) or item.get("type") != "listItem":
            continue
        marker = f"{idx}." if ordered else "-"
        sub_blocks: list[str] = []
        for child in item.get("content") or []:
            if isinstance(child, dict) and child.get("type") == "bulletList":
                sub_blocks.append(
                    _walk_list(
                        child.get("content") or [],
                        ordered=False,
                        depth=depth + 1,
                        resolver=resolver,
                        report=report,
                    )
                )
            elif isinstance(child, dict) and child.get("type") == "orderedList":
                sub_blocks.append(
                    _walk_list(
                        child.get("content") or [],
                        ordered=True,
                        depth=depth + 1,
                        resolver=resolver,
                        report=report,
                    )
                )
            else:
                sub_blocks.extend(_walk_block(child, depth + 1, resolver, report))
        if not sub_blocks:
            lines.append(f"{indent}{marker} ")
            continue
        # First block becomes the bullet's leading line(s); subsequent
        # blocks are continuations indented under the bullet.
        first = sub_blocks[0]
        first_lines = first.split("\n")
        lines.append(f"{indent}{marker} {first_lines[0]}")
        for cont in first_lines[1:]:
            lines.append(f"{indent}  {cont}")
        for sub in sub_blocks[1:]:
            for cont in sub.split("\n"):
                lines.append(f"{indent}  {cont}" if cont else "")
    return "\n".join(lines)


def _walk_table(
    rows: list,
    resolver: AttachmentURLResolver,
    report: NormalizationReport,
) -> str:
    """Render an ADF table to GFM markdown.

    Header detection: first `tableRow` whose first cell type is
    `tableHeader` is treated as the header; otherwise we synthesize an
    empty header row (markdown requires one).
    """
    md_rows: list[list[str]] = []
    has_header = False
    header_idx = -1
    for i, row in enumerate(rows):
        if not isinstance(row, dict) or row.get("type") != "tableRow":
            continue
        cells = row.get("content") or []
        if i == 0 and cells and cells[0].get("type") == "tableHeader":
            has_header = True
            header_idx = i
        cell_texts: list[str] = []
        for cell in cells:
            if not isinstance(cell, dict):
                cell_texts.append("")
                continue
            sub_parts: list[str] = []
            for c in cell.get("content") or []:
                sub_parts.extend(_walk_block(c, 0, resolver, report))
            text = _join_blocks(sub_parts).replace("\n", " ").replace("|", "\\|")
            cell_texts.append(text.strip())
        md_rows.append(cell_texts)
    if not md_rows:
        return ""
    n = max(len(r) for r in md_rows)
    md_rows = [r + [""] * (n - len(r)) for r in md_rows]
    if not has_header:
        md_rows.insert(0, [""] * n)
        header_idx = 0
    out_lines: list[str] = []
    out_lines.append("| " + " | ".join(md_rows[0]) + " |")
    out_lines.append("|" + "|".join([" --- "] * n) + "|")
    for r in md_rows[1:]:
        out_lines.append("| " + " | ".join(r) + " |")
    return "\n".join(out_lines)


def _render_media(
    node: dict,
    resolver: AttachmentURLResolver,
    report: NormalizationReport,
    *,
    style: str = "block",
) -> str:
    """Render an ADF `media` or `mediaInline` node as markdown.

    Two render modes:
      - **image** — markdown `![alt](url)` syntax. Used when `attrs.type`
        looks image-like (e.g., the historical default for `mediaSingle`
        screenshots) OR when no type info is available and we're being
        conservative.
      - **file-card** — markdown `[label](url)` link syntax. Used when
        `attrs.type == "file"` and the mime/extension is non-image.
        Confluence's `mediaInline` and `mediaGroup` with `type=file`
        carry NO `fileName` in many cases — the action layer resolves
        the real title via `list_attachments` post-normalize. Until
        resolution, we emit a placeholder of the form
        `[<<file:<uuid>>>](images/<uuid>)` so the action layer can
        rewrite it deterministically (same convention as smartcards).

    `style="inline"` is set when this came from an inline context
    (`mediaInline`); `style="block"` for `media` / `mediaGroup` /
    `mediaSingle`. The bookkeeping in `report.images` records this so
    the post-normalize rewrite knows which markdown shape to swap.
    """
    if not isinstance(node, dict):
        return ""
    node_type = node.get("type") or ""
    if node_type not in ("media", "mediaInline"):
        return ""
    attrs = node.get("attrs") or {}
    # ADF uses `fileName` (camelCase) on file-collection media; older
    # variants and our publish path also see `filename`. Accept both.
    filename = (
        attrs.get("fileName")
        or attrs.get("filename")
        or attrs.get("title")
        or ""
    )
    if not filename and attrs.get("alt"):
        # `alt` is sometimes the human label, sometimes the filename —
        # only use it when no other name is available.
        filename = attrs["alt"]
    media_id = attrs.get("id") or ""
    collection = attrs.get("collection") or ""
    url = attrs.get("url") or ""
    media_type = attrs.get("type") or ""
    width = attrs.get("width")
    height = attrs.get("height")

    # Cross-page UNKNOWN detection — Atlassian's REST `body.atlas_doc_format`
    # emits `id == "UNKNOWN_MEDIA_ID"` for media nodes whose attachment lives
    # on a different page than the one being fetched. Storage XHTML preserves
    # the original `<ri:attachment ri:filename ri:content-title>` so the
    # action layer can dual-fetch and resolve. We track the structural
    # position (ordinal among ALL media nodes seen) so the resolver can pair
    # ADF unknowns with Storage attachments by traversal order.
    is_cross_page_unknown = (
        media_id == "UNKNOWN_MEDIA_ID"
        or (
            media_type == "file"
            and not media_id
            and not collection
            and (filename in ("", "UNKNOWN_ATTACHMENT") or
                 attrs.get("__fileName") == "UNKNOWN_ATTACHMENT")
        )
    )
    media_position = len(report.media_refs)  # captured before media_refs.append

    # Decide render shape: image vs file-card.
    #   - external images: image-syntax (current behavior)
    #   - file-collection media w/ filename whose extension looks image-y:
    #     image-syntax
    #   - file-collection media w/ no filename: file-card (filename will
    #     resolve via list_attachments post-normalize)
    #   - mediaInline: ALWAYS file-card — Confluence uses inline only for
    #     non-image attachments embedded in prose/tables (image-inline is
    #     extremely rare and the file-card render is still correct for it
    #     since `[…]` is valid in inline contexts where `![…]` may not be)
    image_exts = (
        ".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".bmp", ".tiff",
    )
    has_image_ext = bool(filename) and filename.lower().endswith(image_exts)
    if node_type == "mediaInline":
        render_as_image = False
    elif media_type == "external" and url:
        render_as_image = True
    elif media_type == "file" and not filename:
        # Filename will be resolved later — emit file-card placeholder.
        # Conservative default: render as file-card, NOT image, because
        # the inline contexts where mediaGroup appears (table cells with
        # mixed file types) frequently carry CSVs / PDFs, not images.
        render_as_image = False
    elif has_image_ext:
        render_as_image = True
    else:
        # No filename and not externally addressable, no image extension
        # — fall back to file-card.
        render_as_image = False

    # Build ref_url. For unresolved file-cards we use a placeholder UUID
    # that the action layer rewrites once `list_attachments` returns.
    placeholder_label: str | None = None
    cross_page_token: str | None = None  # set when this is an UNKNOWN_MEDIA_ID
    if is_cross_page_unknown:
        # Cross-page: filename + source_page live in Storage XHTML, not ADF.
        # Emit a position-tagged placeholder the action layer can pattern-match
        # on. We bake the structural ordinal (`media_position`) into the
        # placeholder so the resolver can pair against Storage XHTML
        # `<ri:attachment>` elements by traversal order even when ADF carries
        # multiple unknowns on the same page.
        cross_page_token = f"CROSSPAGE-{media_position}"
        ref_url = resolver(f"{cross_page_token}.bin", "")
        placeholder_label = f"<<crosspage:{media_position}>>"
        # Track in cross_page_unknowns so the action layer knows to look up
        # Storage XHTML for THIS page and resolve.
        report.cross_page_unknowns.append({
            "position": media_position,
            "placeholder_id": cross_page_token,
            "media_id": media_id,
            "collection": collection,
            "node_type": node_type,
            "style": style,
        })
    elif media_type == "external" and url:
        ref_url = url
        if filename == "":
            filename = url.rsplit("/", 1)[-1]
    elif not filename and media_id:
        # Filename will be resolved via list_attachments. Emit a
        # placeholder ref the action layer can pattern-match on.
        ref_url = resolver(media_id + ".bin", media_id or collection)
        placeholder_label = f"<<file:{media_id}>>"
    else:
        # `id` (file id) is the strongest hint for the resolver — fall
        # back to collection if the resolver disambiguates that way.
        ref_url = resolver(filename, media_id or collection)

    alt = attrs.get("alt") or filename
    report.media_refs.append({"filename": filename, "url": ref_url, "type": media_type})
    # Track every image (and now: every file-card) with the bookkeeping
    # the action layer needs to download the binary, verify the rewrite,
    # and (on roundtrip) emit an ADF media-node placeholder on publish.
    is_local_ref = ref_url.startswith("images/") or ref_url.startswith("./images/")
    report.images.append({
        "media_id": media_id,
        "collection": collection,
        "filename": filename,
        "alt": alt if isinstance(alt, str) else "",
        "target_relpath": ref_url if is_local_ref else "",
        "url": ref_url,
        "width": width,
        "height": height,
        "type": media_type,
        "node_type": node_type,
        "style": style,
        "render": "image" if render_as_image else "file",
        "needs_filename": placeholder_label is not None,
    })
    # Emit a round-trip marker comment so the publish-side ADF builder
    # can distinguish markdown originating from a Confluence media node
    # (which must round-trip to ADF media / mediaInline) from a regular
    # external image link in user prose. The marker is invisible in
    # rendered markdown.
    marker = ""
    if cross_page_token is not None:
        # Cross-page placeholder — emit a CROSSPAGE marker the action
        # layer can pattern-match on to swap in resolved metadata
        # (`<!-- media id=<real> source-page=<id> ... -->`).
        marker = f"<!-- crosspage position={media_position} -->"
    elif media_id or collection:
        # Only attach metadata for Confluence-sourced media — external
        # images keep their bare markdown form.
        parts = []
        if node_type == "mediaInline":
            parts.append("inline")
        if media_id:
            parts.append(f"id={media_id}")
        if collection:
            parts.append(f"collection={collection}")
        marker = f"<!-- media {' '.join(parts)} -->"
    # URL slot of every emitted markdown link must be percent-encoded so
    # spaces / parens / non-ASCII in filenames don't break the parser.
    # `ref_url` is kept raw above for `report.images` bookkeeping (which
    # stores filesystem-shaped relpaths); only the markdown emission gets
    # encoded.
    enc_ref = md_link_dest(ref_url)
    if render_as_image:
        return f"![{alt}]({enc_ref}){marker}"
    # File-card render: link syntax. Use placeholder label if filename is
    # unknown so the action layer can swap it post-`list_attachments`.
    label = placeholder_label or filename or alt or "attachment"
    return f"[{label}]({enc_ref}){marker}"


# ---- Inline ----


def _walk_inline(
    nodes: list,
    resolver: AttachmentURLResolver,
    report: NormalizationReport,
) -> str:
    parts: list[str] = []
    for n in nodes:
        if not isinstance(n, dict):
            continue
        t = n.get("type", "")
        if t == "text":
            parts.append(_render_text(n, report))
        elif t == "hardBreak":
            parts.append("  \n")
        elif t == "mention":
            attrs = n.get("attrs") or {}
            display = attrs.get("text") or attrs.get("displayName") or attrs.get("id") or "@mention"
            report.extensions.append({"key": "mention", "attrs": attrs})
            parts.append(f"`{display}`")
        elif t == "date":
            attrs = n.get("attrs") or {}
            ts = attrs.get("timestamp") or ""
            report.extensions.append({"key": "date", "attrs": attrs})
            parts.append(f"`{ts}`" if ts else "`date`")
        elif t == "emoji":
            attrs = n.get("attrs") or {}
            parts.append(attrs.get("text") or attrs.get("shortName") or ":emoji:")
        elif t == "inlineCard" or t == "blockCard" or t == "embedCard":
            attrs = n.get("attrs") or {}
            url = attrs.get("url") or ""
            # ADF inlineCards usually carry only `url` — the resolved
            # smartcard label is rendered by Confluence client-side. A few
            # variants do include a title; check the obvious places first.
            data = attrs.get("data") or {}
            label = (
                attrs.get("title")
                or data.get("title")
                or data.get("name")
                or attrs.get("text")
                or ""
            ).strip()
            # Capture page identifiers so the action layer can resolve
            # labels via MCP `getConfluencePage` after this pass.
            import re as _re
            page_id: str | None = None
            tinyui: str | None = None
            if url:
                m_full = _re.search(r"/wiki/spaces/[^/]+/pages/(\d+)(?:/([^?#]+))?", url)
                m_tiny = _re.search(r"/wiki/x/([^/?#]+)", url)
                if m_full:
                    page_id = m_full.group(1)
                    if not label and m_full.group(2):
                        # Slug suffix on full URL: human-readable title
                        # with `+` for spaces.
                        label = m_full.group(2).replace("+", " ").strip()
                elif m_tiny:
                    tinyui = m_tiny.group(1)
            report.smart_links.append({
                "url": url, "label": label,
                "page_id": page_id, "tinyui": tinyui,
            })
            if url:
                if label:
                    # Emit with round-trip marker so publish-side ADF
                    # builder can re-emit as inlineCard, not plain link.
                    parts.append(f"[{label}]({url})<!-- smartcard -->")
                elif page_id or tinyui:
                    # No local label — emit placeholder for action-layer
                    # resolution. The unique key is page_id-or-tinyui.
                    key = page_id or f"x{tinyui}"
                    parts.append(f"[<<smartcard:{key}>>]({url})<!-- smartcard -->")
                else:
                    # No identifier extractable (external URL etc.) —
                    # autolink with marker.
                    parts.append(f"<{url}><!-- smartcard -->")
        elif t == "media":
            md = _render_media(n, resolver, report, style="inline")
            if md:
                parts.append(md)
        elif t == "mediaInline":
            # Inline file-card (or, rarely, inline image) embedded in
            # prose / table cell content. Always renders to inline-safe
            # markdown — link syntax for files, image syntax for images.
            md = _render_media(n, resolver, report, style="inline")
            if md:
                parts.append(md)
        elif t in ("extension", "bodiedExtension", "inlineExtension"):
            attrs = n.get("attrs") or {}
            key = attrs.get("extensionKey") or "unknown"
            report.extensions.append({"key": key, "attrs": attrs})
            if key == "attachments":
                position = _capture_attachment_macro(attrs, report)
                labels = report.attachment_macros[position].get("labels")
                open_s, close_s = _attachments_open_close(position, labels)
                parts.append(f"{open_s}{close_s}")
            elif key in ("children", "pagetree"):
                position = _capture_child_index_macro(attrs, key, report)
                depth = report.child_index_macros[position].get("depth")
                open_s, close_s = _child_index_open_close(position, key, depth)
                parts.append(f"{open_s}{close_s}")
            elif key == "jira":
                position = _capture_jira_macro(attrs, report)
                jql = report.jira_macros[position].get("jql")
                open_s, close_s = _jira_open_close(position, jql)
                parts.append(f"{open_s}{close_s}")
            else:
                parts.append(f"<!-- confluence-side: {key} -->")
        else:
            # Unknown inline node — recurse into content if present
            sub = n.get("content")
            if isinstance(sub, list):
                parts.append(_walk_inline(sub, resolver, report))
    return "".join(parts)


def _render_text(node: dict, report: NormalizationReport) -> str:
    text = node.get("text", "")
    if not text:
        return ""
    marks = node.get("marks") or []
    code = False
    bold = False
    italic = False
    strike = False
    underline = False
    href: str | None = None
    for m in marks:
        if not isinstance(m, dict):
            continue
        mt = m.get("type")
        if mt == "strong":
            bold = True
        elif mt == "em":
            italic = True
        elif mt == "code":
            code = True
        elif mt == "strike":
            strike = True
        elif mt == "underline":
            # Markdown has no native underline. Confluence uses it for
            # sub-section labels and emphasis that doesn't fit bold/italic.
            # GFM permits inline HTML, so emit a raw <u>...</u> wrapper —
            # round-trip back to ADF on publish recovers the underline mark.
            underline = True
        elif mt == "link":
            href = (m.get("attrs") or {}).get("href")
    if code:
        # Code mark wins over other formatting per markdown semantics
        return f"`{text}`"
    out = text
    if bold and italic:
        out = f"***{out}***"
    elif bold:
        out = f"**{out}**"
    elif italic:
        out = f"*{out}*"
    if strike:
        out = f"~~{out}~~"
    if underline:
        out = f"<u>{out}</u>"
    if href:
        out = f"[{out}]({href})"
    return out


# ---- Helpers ----


def _join_blocks(blocks: list[str]) -> str:
    """Join block-level chunks with blank lines, suppressing duplicates."""
    cleaned = [b.rstrip("\n") for b in blocks if b is not None]
    cleaned = [b for b in cleaned if b != ""]
    return "\n\n".join(cleaned)
