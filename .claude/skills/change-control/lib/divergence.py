"""Divergence detection — has Confluence moved ahead of our last push?

Used by `publish` and `review-formal-update` before any new write to
the page. The flow:

    1. Read frontmatter on the local doc → `page_id`,
       `last_published_version`.
    2. Ask the MCP for the current Confluence page (ADF format).
    3. If `current.version <= last_published_version` → no divergence.
    4. Otherwise, normalize current ADF to markdown (with stable
       diff-safe placeholders) and produce a unified diff against the
       cached snapshot at `last_published_version`. The action layer
       presents the user with Overwrite / Merge / Abort.

This module owns the comparison logic only. Frontmatter parsing,
snapshot I/O, and MCP calls are injected. Pure function inside; the
convenience `detect_divergence` orchestrator stitches them together.
"""
from __future__ import annotations

import difflib
import re as _re
from dataclasses import dataclass, field
from typing import Callable, Optional

from .confluence_mcp import ConfluenceMCP, ConfluencePage
from .normalizer import normalize_for_diff as _raw_normalize_for_diff


# ---- Sentinel-aware diff (task 131) ----
#
# Auto-rendered regions (children/pagetree TOCs, jira tables, attachments
# tables, stub-container TOCs) are bracketed by OPEN+CLOSE sentinel pairs.
# The content inside is regenerated deterministically from external state
# (manifest, attachment list, jira issues), so a byte-level diff would
# light up every time the TOC re-rendered even though no human-authored
# content has changed. Strip these regions before comparing.
#
# Recognized kinds:
#   - `AUTO:<KIND>` (uppercase, dashed) — task 131 onward.
#       open: `<!-- AUTO:CHILD-INDEX source=... position=N -->`
#       close: `<!-- /AUTO:CHILD-INDEX position=N -->`
#       Both `CHILD-INDEX` and `JIRA-LIST` follow this shape.
#   - `confluence-side: <kind>` (lowercase) — 0.7.0/0.8.0 zone-marker form.
#       open: `<!-- confluence-side: attachments labels=actual position=0 -->`
#       close: `<!-- /confluence-side: attachments position=0 -->`
#   - Solo (non-paired) `<!-- confluence-side: <kind> -->` — older zone
#       markers (toc, page-signatures) emitted as a single comment line
#       with no rendered content. Strip just the comment.
#
# Strip semantics: remove the entire region inclusive of the sentinels.
# Outside the regions, content is preserved byte-for-byte.

_AUTO_OPEN_PAT = _re.compile(
    r"<!--\s*AUTO:([A-Z][A-Z0-9-]*)\s+[^>]*?-->",
)
_AUTO_CLOSE_PAT_TPL = (
    r"<!--\s*/AUTO:{kind}\b[^>]*?-->"
)
_CONFLUENCE_SIDE_OPEN_PAT = _re.compile(
    r"<!--\s*confluence-side:\s*([\w-]+)\b[^>]*?-->",
)
_CONFLUENCE_SIDE_CLOSE_PAT_TPL = (
    r"<!--\s*/confluence-side:\s*{kind}\b[^>]*?-->"
)


def strip_auto_regions(md: str) -> str:
    """Remove every AUTO:<KIND>...{/AUTO:<KIND>} region, every paired
    `confluence-side: <kind>` region, and every solo `confluence-side`
    comment line. Returns a stripped string used as the canonical form
    for diffs.

    Pure function — never raises on malformed input; an open sentinel
    with no close survives as-is (the region falls through to be
    treated as content, which is the safe behavior — drift detection
    will then surface what looks like an unfinished auto block)."""
    if not md:
        return md

    out_chunks: list[str] = []
    cursor = 0
    text = md

    # Walk sentinels in order so we don't miss interleaved kinds.
    while cursor < len(text):
        m_auto = _AUTO_OPEN_PAT.search(text, cursor)
        m_cs = _CONFLUENCE_SIDE_OPEN_PAT.search(text, cursor)
        # Pick whichever comes first.
        candidates = [m for m in (m_auto, m_cs) if m]
        if not candidates:
            out_chunks.append(text[cursor:])
            break
        m = min(candidates, key=lambda x: x.start())
        # Append everything before the sentinel verbatim.
        out_chunks.append(text[cursor:m.start()])
        if m is m_auto:
            kind = m.group(1)
            close_pat = _re.compile(
                _AUTO_CLOSE_PAT_TPL.format(kind=_re.escape(kind))
            )
            m_close = close_pat.search(text, m.end())
            if m_close:
                # Strip from open through close inclusive. Also consume
                # one trailing newline if present so we don't leave a
                # blank line sentinel-ghost behind.
                end = m_close.end()
                if end < len(text) and text[end] == "\n":
                    end += 1
                cursor = end
                continue
            # No close — keep the open sentinel as content (defensive).
            out_chunks.append(text[m.start():m.end()])
            cursor = m.end()
            continue
        # confluence-side branch
        kind = m.group(1)
        close_pat = _re.compile(
            _CONFLUENCE_SIDE_CLOSE_PAT_TPL.format(kind=_re.escape(kind))
        )
        m_close = close_pat.search(text, m.end())
        if m_close:
            end = m_close.end()
            if end < len(text) and text[end] == "\n":
                end += 1
            cursor = end
            continue
        # No matching close → treat as solo zone marker; strip only the
        # comment line plus its trailing newline.
        end = m.end()
        if end < len(text) and text[end] == "\n":
            end += 1
        cursor = end

    return "".join(out_chunks)


def normalize_for_diff(adf) -> str:  # type: ignore[no-untyped-def]
    """ADF → markdown for diffing, with auto-regions stripped.

    Wraps the raw normalizer so consumers always get the diff-canonical
    form. Adopt-side `classify_adopt` and publish-side `detect_divergence`
    both rely on this — auto regions cannot trigger spurious conflicts."""
    raw = _raw_normalize_for_diff(adf)
    return strip_auto_regions(raw)


@dataclass
class DivergenceResult:
    """Outcome of a divergence check."""

    diverged: bool
    current_version: int
    last_published_version: int
    page_id: str
    their_md: str = ""
    their_diff: str = ""
    their_page: Optional[ConfluencePage] = field(default=None, repr=False)
    snapshot: Optional[str] = field(default=None, repr=False)

    def summary(self) -> str:
        if not self.diverged:
            return (
                f"page {self.page_id}: no divergence "
                f"(version {self.current_version} == "
                f"last_published_version {self.last_published_version})"
            )
        return (
            f"page {self.page_id}: DIVERGED "
            f"(their version {self.current_version}, "
            f"your last {self.last_published_version})"
        )


SnapshotReader = Callable[[str, int], Optional[str]]
"""(page_id, version) -> markdown body or None if missing."""


# ---- Public API ----


def detect_divergence(
    mcp: ConfluenceMCP,
    *,
    page_id: str,
    last_published_version: int,
    read_snapshot: SnapshotReader,
) -> DivergenceResult:
    """Issue a `getConfluencePage(adf)` and compare to the cached snapshot.

    Returns a `DivergenceResult`. When `diverged is True`:
      - `their_md` is the current page's markdown rendering (with stable
        diff-safe placeholders for media + extensions)
      - `their_diff` is a unified diff `(snapshot, their_md)`
      - `snapshot` is the cached snapshot body if present (None if the
        cache is missing — diff is computed against the empty string in
        that case so the user still sees the new content)
      - `their_page` is the live page record
    """
    page = mcp.get_page(page_id, content_format="adf")
    current_version = page.version
    if current_version <= last_published_version:
        return DivergenceResult(
            diverged=False,
            current_version=current_version,
            last_published_version=last_published_version,
            page_id=page_id,
            their_page=page,
        )
    their_md = normalize_for_diff(page.body)
    snapshot = read_snapshot(page_id, last_published_version)
    diff = compute_diff(
        snapshot or "",
        their_md,
        from_label=f"snapshot@v{last_published_version}",
        to_label=f"confluence@v{current_version}",
    )
    return DivergenceResult(
        diverged=True,
        current_version=current_version,
        last_published_version=last_published_version,
        page_id=page_id,
        their_md=their_md,
        their_diff=diff,
        their_page=page,
        snapshot=snapshot,
    )


# ---- Pure diff helper ----


def compute_diff(
    a: str,
    b: str,
    *,
    from_label: str = "a",
    to_label: str = "b",
    context: int = 3,
) -> str:
    """Unified diff between two strings. Empty result when identical."""
    a_lines = a.splitlines(keepends=True)
    b_lines = b.splitlines(keepends=True)
    diff = difflib.unified_diff(
        a_lines, b_lines, fromfile=from_label, tofile=to_label, n=context
    )
    return "".join(diff)
