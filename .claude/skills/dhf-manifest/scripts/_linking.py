#!/usr/bin/env python3
"""
_linking.py — Shared link-rendering helpers for the dhf-manifest builders.

Every consumer that surfaces an obligation ID or QMS ID to a reader must
emit the canonical linked label shape:

    [`OBL-XXX` · Human-Readable Title](relative/path/to/source.md#OBL-XXX)
    [`QMS-XXX` · Human-Readable Title](relative/path/to/qms-source.md#qms-xxx)

ID stays the stable primary key (unchanged for cross-refs); the title is the
reading aid; the href is the one-click navigation to the source distillation
(Tier 1 MD) or the source QMS doc (docs/internal/source-md/).

Phase 1 (task ben/104) ships this helper with `title` optional — when the
record has no `title`, the label collapses to `[`OBL-XXX`](href)` so existing
output is byte-identical until titles are populated. Phase 3 flips title to
required in validate.py.

Usage:
    from _linking import render_obl_link, render_qms_link
    cell = render_obl_link("OBL-CYBER-003", "SBOM Requirements",
                           "fda-guidance/fda-cyber.md#OBL-CYBER-003")
    # → "[`OBL-CYBER-003` · SBOM Requirements](fda-guidance/fda-cyber.md#OBL-CYBER-003)"
"""

from __future__ import annotations


SEPARATOR = " · "  # middle dot — stable contract; change here applies everywhere


def render_obl_link(oid: str, title: str | None, href: str | None) -> str:
    """Canonical rendering for an obligation reference.

    Shape:
        with title + href   → [`OBL-XXX` · Title](href)
        with title, no href → `OBL-XXX` · Title
        no title, with href → [`OBL-XXX`](href)
        no title, no href   → `OBL-XXX`

    `href` None means "no link target known" (e.g. the Tier 1 anchor map didn't
    resolve the ID). The label still renders; the reader just can't click through.
    """
    return _render_id_link(oid, title, href)


def render_qms_link(qid: str, title: str | None, href: str | None) -> str:
    """Canonical rendering for a QMS record reference. Identical shape rules as
    `render_obl_link` — kept as a separate function so future QMS-specific
    formatting (e.g. section-anchor handling) can diverge without touching OBL
    call sites."""
    return _render_id_link(qid, title, href)


def _render_id_link(ident: str, title: str | None, href: str | None) -> str:
    """Internal — shared formatting for OBL- and QMS-style IDs.

    ID is wrapped in backticks so markdown tables render it as inline code
    (consistent with existing `build-manifest.py` / `build-qms.py` output).
    """
    title_clean = (title or "").strip()
    id_part = f"`{ident}`"
    label = f"{id_part}{SEPARATOR}{title_clean}" if title_clean else id_part
    if href:
        return f"[{label}]({href})"
    return label


def find_bare_ids(markdown_text: str, id_prefix: str = r"(OBL|QMS)") -> list[tuple[int, str, str]]:
    """Scan markdown for bare ID occurrences outside markdown link syntax.

    Returns a list of (line_number, id_text, snippet) tuples. An ID is "bare"
    if it is not wrapped in either inline code backticks within a markdown link
    (e.g. [\\`OBL-XXX\\`](href)) or a raw link target (e.g. ](...OBL-XXX)).

    This is the Phase 4 post-build check — zero tolerance for bare IDs in
    rendered dashboards; every ID must be part of a clickable link.

    Args:
        markdown_text: the content of the rendered .md file
        id_prefix: regex-class matching the ID family prefix — default covers
                   both OBL- and QMS-; pass `r"OBL"` or `r"QMS"` to scope.

    Returns:
        List of bare-ID findings. Empty list = pass.
    """
    import re as _re

    bare: list[tuple[int, str, str]] = []
    id_re = _re.compile(rf"\b({id_prefix})-[A-Z0-9-]+\b")
    for lineno, line in enumerate(markdown_text.splitlines(), start=1):
        for match in id_re.finditer(line):
            start, end = match.span()
            ident = match.group(0)
            # Acceptable contexts:
            #   1. inside a link label wrapped in backticks: [`OBL-XXX` ...](href)
            #   2. inside a link target (url): ](...#OBL-XXX)
            #   3. inside a raw HTML anchor: <a id="OBL-XXX">
            #   4. inside inline code: `OBL-XXX`
            before = line[:start]
            after = line[end:]
            backtick_before = before.rfind("`")
            backtick_after = after.find("`")
            in_code = (
                backtick_before != -1
                and backtick_after != -1
                and before[backtick_before:].count("`") % 2 == 1
            )
            if in_code:
                continue
            # Inside a link url (between `](` and `)`)?
            url_open = before.rfind("](")
            url_close_before = before.rfind(")")
            if url_open != -1 and url_open > url_close_before:
                continue
            # Inside an HTML id="..." attribute?
            if _re.search(r'id\s*=\s*"[^"]*$', before):
                continue
            # Otherwise: bare.
            snippet = line.strip()
            if len(snippet) > 120:
                snippet = snippet[:117] + "..."
            bare.append((lineno, ident, snippet))
    return bare


def is_valid_title(title: str | None, max_len: int = 60) -> tuple[bool, str]:
    """Validation helper for Phase-3 strict mode and validate.py.

    Returns (ok, reason). Rules:
      - non-empty after strip
      - length ≤ max_len chars
      - no pipe characters (would break table cells)
      - no markdown link syntax (titles should be plain text)
    """
    if not title or not title.strip():
        return False, "empty"
    t = title.strip()
    if len(t) > max_len:
        return False, f"too long ({len(t)} > {max_len})"
    if "|" in t:
        return False, "contains pipe character"
    if "[" in t or "](" in t:
        return False, "contains markdown link syntax"
    return True, ""
