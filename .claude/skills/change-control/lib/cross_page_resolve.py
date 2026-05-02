"""Cross-page attachment resolution for adopt.

The Atlassian REST `body.atlas_doc_format` endpoint emits the literal
string `"UNKNOWN_MEDIA_ID"` for media nodes whose attachment lives on
a different page than the one being fetched. The same body fetched
in `body.storage` XHTML preserves the original
`<ri:attachment ri:filename="X.docx" ri:content-title="Source Page">`
with the filename + source-page-title intact.

This module pairs ADF cross-page unknowns with Storage XHTML attachment
elements by structural traversal order so the action layer can:

  1. Look up the source page by title via CQL search
  2. List its attachments and pick the matching filename
  3. Download the binary into THIS page's `images/<filename>`
  4. Rewrite the markdown placeholder with the real filename + a
     round-trip marker carrying `source-page=<id>` for provenance

These functions are pure — no I/O. The action layer is responsible for
HTTP fetches.
"""
from __future__ import annotations

import re
from typing import Any

# `<ri:attachment ...>` self-closing or with separate close tag. We
# capture the attribute block; the namespace prefix stays literal.
_RI_ATTACHMENT_RE = re.compile(
    r"<ri:attachment\b([^>]*?)(?:/>|>)",
    re.IGNORECASE,
)
_ATTR_RE = re.compile(
    r'\b(ri:[\w-]+)\s*=\s*"([^"]*)"',
    re.IGNORECASE,
)


def parse_storage_xhtml(xhtml: str) -> list[dict[str, Any]]:
    """Walk Confluence Storage XHTML and return ordered list of
    `<ri:attachment>` references.

    Each entry shape:
      {
        "filename":  str,   # ri:filename attribute (the actual file)
        "content_title": str,  # ri:content-title attribute (source page)
        "version_at_save": str | None,  # ri:version-at-save if present
        "position": int,    # 0-based traversal index
      }

    Order matches the document's natural reading order, which is what
    the ADF traverser also produces — so position-by-position pairing
    works between this output and `report.cross_page_unknowns`.
    """
    if not xhtml:
        return []
    out: list[dict[str, Any]] = []
    for idx, m in enumerate(_RI_ATTACHMENT_RE.finditer(xhtml)):
        attr_blob = m.group(1) or ""
        attrs: dict[str, str] = {}
        for am in _ATTR_RE.finditer(attr_blob):
            attrs[am.group(1).lower()] = am.group(2)
        filename = attrs.get("ri:filename", "")
        content_title = attrs.get("ri:content-title", "")
        version = attrs.get("ri:version-at-save")
        out.append({
            "filename": filename,
            "content_title": content_title,
            "version_at_save": version,
            "position": idx,
        })
    return out


def pair_unknowns_to_storage(
    adf_unknowns: list[dict[str, Any]],
    storage_attachments: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Pair ADF cross-page unknowns with Storage `<ri:attachment>` elements
    by structural traversal order (position).

    Returns one entry per ADF unknown:
      {
        "adf_position": int,
        "placeholder_id": str,  # CROSSPAGE-<n>
        "filename": str,        # from Storage, "" if no match
        "content_title": str,   # from Storage, "" if no match
        "matched": bool,
      }

    Pairing strategy: positional. ADF position N pairs with Storage
    position N. If counts mismatch (extra ADF unknowns, or extra Storage
    attachments), unmatched ADF entries get `matched=False` and empty
    filename/title. Pairs the prefix where positions align — Confluence
    always preserves traversal order between the two body formats.

    NOTE: storage_attachments includes ALL `<ri:attachment>` elements,
    not only cross-page ones. The same-page attachments in Storage have
    matching real ids in ADF (so they're NOT in `adf_unknowns`). We
    pair by index INTO the unknowns list, but we have to scan storage
    for the cross-page ones. Heuristic: cross-page attachments in
    Storage carry `ri:content-title` (the source page); same-page ones
    do not. So we filter Storage to those with content_title before
    pairing.
    """
    cross_page_storage = [
        s for s in storage_attachments if s.get("content_title")
    ]
    out: list[dict[str, Any]] = []
    for i, unk in enumerate(adf_unknowns):
        if i < len(cross_page_storage):
            s = cross_page_storage[i]
            out.append({
                "adf_position": unk.get("position", i),
                "placeholder_id": unk.get("placeholder_id", f"CROSSPAGE-{i}"),
                "filename": s.get("filename", ""),
                "content_title": s.get("content_title", ""),
                "matched": True,
            })
        else:
            out.append({
                "adf_position": unk.get("position", i),
                "placeholder_id": unk.get("placeholder_id", f"CROSSPAGE-{i}"),
                "filename": "",
                "content_title": "",
                "matched": False,
            })
    return out


def build_resolved_markdown(
    filename: str,
    media_id: str,
    source_page_id: str,
    source_page_title: str,
) -> str:
    """Render the resolved file-card markdown with full round-trip marker.

    Output shape:
      `[<filename>](images/<filename-encoded>)<!-- media id=<uuid>
       collection=contentId-<source-page-id>
       source-page=<source-page-id>
       source-page-title="<title>" -->`
    """
    from lib.markdown_transform import md_link_dest  # noqa: WPS433

    enc = md_link_dest(f"images/{filename}")
    title_escaped = source_page_title.replace('"', "\\\"")
    parts = []
    if media_id:
        parts.append(f"id={media_id}")
        parts.append(f"collection=contentId-{source_page_id}")
    parts.append(f"source-page={source_page_id}")
    parts.append(f'source-page-title="{title_escaped}"')
    marker = f"<!-- media {' '.join(parts)} -->"
    return f"[{filename}]({enc}){marker}"


def build_warning_markdown(
    filename: str,
    source_page_title: str,
    base_url: str,
    space_key: str,
    source_page_id: str | None = None,
) -> str:
    """Render the graceful-degradation blockquote when cross-page resolution
    can't find the source page or the attachment.

    No `UNKNOWN_MEDIA_ID` ugliness — this gives the reader a clear pointer
    to where to find the file on Confluence.
    """
    base = base_url.rstrip("/")
    if source_page_id:
        link = f"{base}/wiki/spaces/{space_key}/pages/{source_page_id}"
    else:
        # Best-effort fallback: link to space search by title.
        from urllib.parse import quote
        link = (
            f"{base}/wiki/search?text={quote(source_page_title)}"
            f"&spaces={quote(space_key)}"
        )
    fname_disp = filename or "(unnamed attachment)"
    title_disp = source_page_title or "(unknown source page)"
    return (
        f"> ⚠️ Cross-page attachment: **{fname_disp}** lives on Confluence "
        f"page [{title_disp}]({link}). Local copy unavailable; view on "
        "Confluence."
    )


def project_config_source_map(
    page_id: str,
    config_map: dict[str, list[Any]] | None,
) -> dict[str, str]:
    """Translate the project.yml `cross_page_source_map[page_id]` block
    into a `{source_page_title: source_page_id}` shim. The config carries
    `(filename, source_page_title)` pairs but no resolved page ids — those
    have to come from CQL or cookie-bridge attachments lookup. This shim
    therefore returns `{title: ""}` so the live resolver path still tries
    to find a real id; if it can't, the graceful-warning blockquote at
    least carries the source-page title from config (better than UNKNOWN).

    Returns an empty dict when there is no config entry for this page_id.
    """
    if not config_map or not page_id:
        return {}
    raw = config_map.get(str(page_id))
    if not raw:
        return {}
    out: dict[str, str] = {}
    for entry in raw:
        if isinstance(entry, dict):
            title = str(entry.get("source_page_title") or "")
        elif hasattr(entry, "source_page_title"):
            title = str(entry.source_page_title or "")
        else:
            continue
        if title:
            out.setdefault(title, "")
    return out


__all__ = [
    "parse_storage_xhtml",
    "pair_unknowns_to_storage",
    "build_resolved_markdown",
    "build_warning_markdown",
    "project_config_source_map",
]
