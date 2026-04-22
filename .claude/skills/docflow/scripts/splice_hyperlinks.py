#!/usr/bin/env python3
"""splice_hyperlinks.py — rewrite the Phase 2 text cache to carry source hyperlinks inline.

Called by adopter Phase 2 immediately after the plain-text cache is written.
For each link annotation found in the source document, locate the visible
anchor text in the corresponding cache region and replace it with
`[anchor](url)` so every downstream phase sees links as standard markdown.

Preserves every link kind verbatim — external URIs and internal anchors alike —
per task ben/086 Phase A decision. Round-trip fidelity back to Confluence
depends on keeping same-page anchors intact.

Usage:
    splice_hyperlinks.py <source_file> <cache_file> <format>

Exits 0 on success (including the no-links case). Writes a short summary to
stdout: link counts by kind and how many were spliced. Exits non-zero on hard
errors (unreadable source, unknown format).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path


def splice_pdf(source: Path, cache: Path) -> tuple[int, int, dict[str, int]]:
    """Splice PDF link annotations into the pdftotext cache.

    Returns (found, spliced, kind_counts).
    """
    import pymupdf

    cache_text = cache.read_text()
    pages = cache_text.split("\f")

    doc = pymupdf.open(source)
    if len(pages) < len(doc):
        pages.extend([""] * (len(doc) - len(pages)))

    kind_counts = {"URI": 0, "GOTO": 0, "NAMED": 0, "other": 0}
    found = 0
    unique = 0
    spliced = 0

    for page_idx, page in enumerate(doc):
        links = page.get_links()
        if not links:
            continue

        page_text = pages[page_idx] if page_idx < len(pages) else ""
        rewrites: list[tuple[str, str]] = []

        for link in links:
            kind = link.get("kind")
            rect = link.get("from")
            if not rect:
                continue

            if kind == pymupdf.LINK_URI:
                target = link.get("uri", "")
                kind_counts["URI"] += 1
            elif kind == pymupdf.LINK_GOTO:
                dest_page = link.get("page", -1)
                target = f"#page={dest_page + 1}" if dest_page >= 0 else ""
                kind_counts["GOTO"] += 1
            elif kind == pymupdf.LINK_NAMED:
                target = f"#{link.get('nameddest', link.get('name', ''))}"
                kind_counts["NAMED"] += 1
            else:
                kind_counts["other"] += 1
                continue

            if not target:
                continue

            anchor_raw = page.get_textbox(rect)
            if not anchor_raw:
                continue
            anchor = anchor_raw.strip()
            if not anchor:
                continue

            found += 1
            rewrites.append((anchor, target))

        # De-duplicate identical (anchor, url) pairs on the same page. PDFs
        # commonly emit redundant annotations per visual fragment (e.g. a Jira
        # table with one status chip per row, each with its own rect — pymupdf
        # reports them all, but pdftotext only renders the visible text once
        # per cell). Passing duplicates through would leave most unmatched and
        # pollute the `found` count with noise. Dedup preserves order so the
        # longest-first sort in `_apply_rewrites` still works correctly.
        seen: set[tuple[str, str]] = set()
        deduped: list[tuple[str, str]] = []
        for pair in rewrites:
            if pair in seen:
                continue
            seen.add(pair)
            deduped.append(pair)

        unique += len(deduped)
        page_text, splice_count = _apply_rewrites(page_text, deduped)
        spliced += splice_count
        pages[page_idx] = page_text

    cache.write_text("\f".join(pages))
    # `found` = raw annotation count (for source-provenance accounting).
    # `spliced` = links actually written into cache. The gap is mostly PDF
    # visual redundancy (same chip repeated many times in a status table) and
    # is captured by `unique` for the Phase 7 validation bound.
    kind_counts["__unique"] = unique
    return found, spliced, kind_counts


def _apply_rewrites(text: str, rewrites: list[tuple[str, str]]) -> tuple[str, int]:
    """Replace each anchor with [anchor](url) in `text`.

    Strategy:
    1. Aggregate rewrites into `(anchor, url) -> requested_count` — duplicates
       in the input list (e.g. an XLSX column where 20 cells all display the
       same value linking to the same URL) reflect the true multiplicity the
       caller wants spliced, but re-runs must stay idempotent. For each pair,
       count existing `[anchor](url)` occurrences in `text` and subtract — only
       splice `max(0, requested - existing)` additional times per pair.
    2. Sort pair-iteration by anchor length descending — longest first. Prevents
       a short anchor ("Assessment") from matching inside a previously-inserted
       URL ("...Risk+Assessment+SRA...") when the longer anchor ("TEMPLATE -
       Software Risk Assessment") should have consumed that span first.
    3. Maintain a `protected` list of (start, end) character spans that hold
       already-inserted `[anchor](url)` structures. Reject any candidate match
       whose span overlaps a protected region. Seed from existing wrapped
       structures in `text` so re-runs don't double-wrap.
    4. For each pair, scan in left-to-right order for unprotected matches and
       splice up to the remaining budget for that pair.
    5. Tolerate whitespace differences: any run of whitespace in the anchor
       matches any run of whitespace (incl. newlines) in the cache, since
       `pdftotext -layout` may wrap long anchor text across lines.

    Returns the rewritten text and the count of successful splices.
    """
    # Aggregate duplicates while preserving first-seen order.
    pair_counts: dict[tuple[str, str], int] = {}
    for anchor, url in rewrites:
        if not anchor:
            continue
        key = (anchor, url)
        pair_counts[key] = pair_counts.get(key, 0) + 1
    sorted_pairs = sorted(pair_counts.items(), key=lambda kv: -len(kv[0][0]))

    # Seed protected regions from any `[anchor](url)` already present in text.
    # Makes the rewriter idempotent across re-runs.
    protected: list[tuple[int, int]] = [
        (m.start(), m.end())
        for m in re.finditer(r"\[[^\]]+\]\([^)]+\)", text)
    ]
    spliced = 0

    for (anchor, url), requested in sorted_pairs:
        safe_url = url.replace("(", "%28").replace(")", "%29")
        wrapped = f"[{anchor}]({safe_url})"
        # Count existing splices for this exact pair so idempotent re-runs
        # don't exceed `requested`. Escape for the count regex only.
        existing = len(re.findall(re.escape(wrapped), text))
        budget = requested - existing
        if budget <= 0:
            continue

        pattern = _ws_flexible_pattern(anchor)
        for match in pattern.finditer(text):
            if budget <= 0:
                break
            start, end = match.start(), match.end()
            if _overlaps(start, end, protected):
                continue
            # Belt-and-braces: skip if this match starts just after `[`, meaning
            # it's the anchor text inside an already-wrapped link the seed
            # regex failed to cover (e.g. URL contained `)` pre-encoding).
            if start >= 1 and text[start - 1] == "[":
                continue
            original = text[start:end]
            replacement = f"[{original}]({safe_url})"
            text = text[:start] + replacement + text[end:]
            shift = len(replacement) - (end - start)
            protected = [
                (s + shift, e + shift) if s >= end else (s, e)
                for s, e in protected
            ]
            protected.append((start, start + len(replacement)))
            # Re-scan from the top after a splice: positions shifted, and
            # finditer was over the pre-splice string — continuing invalidates
            # offsets. Break and rely on the outer budget loop via a re-iter.
            spliced += 1
            budget -= 1
            # Restart finditer on the mutated text for this pair.
            # (Inner for-loop exits; we loop back via `while budget > 0` below.)
            break
        else:
            # finditer exhausted with no splice or budget still positive but no
            # more matches — move on to next pair.
            continue
        # If we broke out with budget remaining, keep splicing same pair.
        while budget > 0:
            pattern = _ws_flexible_pattern(anchor)
            made_one = False
            for match in pattern.finditer(text):
                start, end = match.start(), match.end()
                if _overlaps(start, end, protected):
                    continue
                if start >= 1 and text[start - 1] == "[":
                    continue
                original = text[start:end]
                replacement = f"[{original}]({safe_url})"
                text = text[:start] + replacement + text[end:]
                shift = len(replacement) - (end - start)
                protected = [
                    (s + shift, e + shift) if s >= end else (s, e)
                    for s, e in protected
                ]
                protected.append((start, start + len(replacement)))
                spliced += 1
                budget -= 1
                made_one = True
                break
            if not made_one:
                break

    return text, spliced


def _overlaps(start: int, end: int, regions: list[tuple[int, int]]) -> bool:
    for r_start, r_end in regions:
        if start < r_end and end > r_start:
            return True
    return False


def _ws_flexible_pattern(anchor: str) -> re.Pattern[str]:
    """Build a regex that matches the anchor text with flexible internal whitespace.

    Any run of whitespace in the anchor matches any run of whitespace (incl.
    newlines) in the cache. Anchor punctuation is escaped.
    """
    tokens = re.split(r"\s+", anchor.strip())
    escaped = [re.escape(t) for t in tokens if t]
    return re.compile(r"\s+".join(escaped))


def splice_docx(source: Path, cache: Path) -> tuple[int, int, dict[str, int]]:
    """Splice DOCX w:hyperlink runs into the cache.

    DOCX hyperlinks live in `word/document.xml` as `<w:hyperlink r:id="rId7">`
    wrapping one or more `<w:r><w:t>...</w:t></w:r>` runs. The r:id resolves
    via `word/_rels/document.xml.rels` → Target attribute.
    """
    import docx

    doc = docx.Document(str(source))
    rels = doc.part.rels
    cache_text = cache.read_text()

    kind_counts = {"external": 0, "internal": 0, "broken": 0}
    rewrites: list[tuple[str, str]] = []

    W_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    R_NS = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"

    for para in _iter_paragraphs(doc):
        for hyperlink in para._element.findall(f".//{W_NS}hyperlink"):
            rid = hyperlink.get(f"{R_NS}id")
            anchor_attr = hyperlink.get(f"{W_NS}anchor")
            texts = hyperlink.findall(f".//{W_NS}t")
            display = "".join(t.text or "" for t in texts).strip()
            if not display:
                continue

            if rid and rid in rels:
                target = rels[rid].target_ref
                kind_counts["external"] += 1
            elif anchor_attr:
                target = f"#{anchor_attr}"
                kind_counts["internal"] += 1
            else:
                kind_counts["broken"] += 1
                continue

            rewrites.append((display, target))

    cache_text, spliced = _apply_rewrites(cache_text, rewrites)
    cache.write_text(cache_text)
    return len(rewrites), spliced, kind_counts


def _iter_paragraphs(doc):
    """Yield all paragraphs in body + tables (shallow; nested tables ok)."""
    for p in doc.paragraphs:
        yield p
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    yield p


def splice_xlsx(source: Path, cache: Path) -> tuple[int, int, dict[str, int]]:
    """Splice XLSX cell.hyperlink into the CSV cache.

    openpyxl exposes per-cell `.hyperlink.target` (external) and `.hyperlink.location`
    (intra-workbook). Display text is `cell.value` (or `.hyperlink.display` when set).
    """
    import openpyxl

    wb = openpyxl.load_workbook(str(source), data_only=False)
    cache_text = cache.read_text()

    kind_counts = {"external": 0, "internal": 0}
    rewrites: list[tuple[str, str]] = []

    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for cell in row:
                h = cell.hyperlink
                if not h:
                    continue
                display = str(h.display or cell.value or "").strip()
                if not display:
                    continue
                if h.target:
                    target = h.target
                    kind_counts["external"] += 1
                elif h.location:
                    target = f"#{h.location}"
                    kind_counts["internal"] += 1
                else:
                    continue
                rewrites.append((display, target))

    cache_text, spliced = _apply_rewrites(cache_text, rewrites)
    cache.write_text(cache_text)
    return len(rewrites), spliced, kind_counts


def splice_pptx(source: Path, cache: Path) -> tuple[int, int, dict[str, int]]:
    """Splice PPTX text-run hyperlinks into the cache.

    python-pptx `_Hyperlink` only exposes `.address` (external URI) and
    `.part`. Intra-deck jumps (slide-to-slide via `a:hlinkClick
    action="ppaction://hlinksldjump"`) are NOT exposed as an `.anchor`
    attribute — they'd need raw XML walking of the action attribute with
    slide-ID resolution. Out of scope for v23.0 PPTX support; flagged in
    task 086 Phase B edge-cases. External URIs cover the dominant case
    (Confluence/Figma/Jira cross-refs in decks).
    """
    from pptx import Presentation

    prs = Presentation(str(source))
    cache_text = cache.read_text()

    kind_counts = {"external": 0}
    rewrites: list[tuple[str, str]] = []

    for slide in prs.slides:
        for shape in slide.shapes:
            if not shape.has_text_frame:
                continue
            for para in shape.text_frame.paragraphs:
                for run in para.runs:
                    hl = run.hyperlink
                    if not hl or not hl.address:
                        continue
                    display = (run.text or "").strip()
                    if not display:
                        continue
                    rewrites.append((display, hl.address))
                    kind_counts["external"] += 1

    cache_text, spliced = _apply_rewrites(cache_text, rewrites)
    cache.write_text(cache_text)
    return len(rewrites), spliced, kind_counts


def main() -> int:
    if len(sys.argv) != 4:
        print(
            "Usage: splice_hyperlinks.py <source_file> <cache_file> <format>",
            file=sys.stderr,
        )
        return 2

    source = Path(sys.argv[1])
    cache = Path(sys.argv[2])
    fmt = sys.argv[3].lower()

    if not source.exists():
        print(f"ERROR: source not found: {source}", file=sys.stderr)
        return 1
    if not cache.exists():
        print(f"ERROR: cache not found: {cache}", file=sys.stderr)
        return 1

    if fmt == "pdf":
        found, spliced, kinds = splice_pdf(source, cache)
    elif fmt in ("docx", "doc"):
        found, spliced, kinds = splice_docx(source, cache)
    elif fmt == "xlsx":
        found, spliced, kinds = splice_xlsx(source, cache)
    elif fmt == "pptx":
        found, spliced, kinds = splice_pptx(source, cache)
    else:
        print(f"ERROR: unsupported format: {fmt}", file=sys.stderr)
        return 2

    unique = kinds.pop("__unique", None)
    kind_str = ", ".join(f"{k}={v}" for k, v in kinds.items() if v)
    unique_str = f" unique={unique}" if unique is not None else ""
    print(
        f"splice_hyperlinks: format={fmt} found={found}{unique_str} "
        f"spliced={spliced} kinds=[{kind_str}]"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
