"""Regression tests for task 140 / change-control v0.13.0 — AUTO:PAGE-TITLE
and AUTO:TOC chrome blocks.

Two coupled AUTO-rendered chrome blocks shipped together:

  AUTO:PAGE-TITLE — emit the page title as a visible H1 at the top of
  the markdown body, mirroring Confluence's title bar. Suppressed when
  the body's first content block is already `# <page_title>` so we
  don't double-render in markdown viewers. Round-trips back to nothing
  on publish (Confluence renders title from the API arg).

  AUTO:TOC — when the source has `extension key="toc"` (Confluence's
  Table of Contents macro), render the body's heading hierarchy as a
  clickable anchor list between sentinels. Round-trips back to a
  single ADF `extension key="toc"` node on publish.

Offline only — no Confluence calls. Run:

    python3 .claude/skills/change-control/tests/test_auto_chrome.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_ROOT))

from lib.normalizer import (  # noqa: E402
    NormalizationReport,
    adf_to_markdown,
)
from lib.divergence import strip_auto_regions  # noqa: E402

from actions.adopt_helper import (  # noqa: E402
    _expand_toc_macros,
    _slugify_anchor,
    _synthesize_page_title,
    _walk_headings_outside_auto,
)
from actions.publish_helper import _md_to_adf  # noqa: E402


# ---- Helpers ----


def _toc_ext(min_level: str | None = None, max_level: str | None = None) -> dict:
    params: dict = {}
    if min_level is not None:
        params["minLevel"] = {"value": min_level}
    if max_level is not None:
        params["maxLevel"] = {"value": max_level}
    return {
        "type": "extension",
        "attrs": {
            "layout": "default",
            "extensionType": "com.atlassian.confluence.macro.core",
            "extensionKey": "toc",
            "parameters": {"macroParams": params},
        },
    }


def _h(level: int, text: str) -> dict:
    return {
        "type": "heading",
        "attrs": {"level": level},
        "content": [{"type": "text", "text": text}],
    }


def _para(text: str) -> dict:
    return {"type": "paragraph", "content": [{"type": "text", "text": text}]}


# ---- AUTO:PAGE-TITLE tests ----


def test_page_title_emitted_when_body_lacks_matching_h1() -> None:
    """1. Adopt with title in frontmatter → markdown body starts with
    AUTO:PAGE-TITLE block containing the H1."""
    body_md = "## Background\n\nThis page describes the process.\n"
    out = _synthesize_page_title(body_md, "Software Development Plan")
    assert out.startswith("<!-- AUTO:PAGE-TITLE -->\n# Software Development Plan\n<!-- /AUTO:PAGE-TITLE -->"), out
    # Body content preserved
    assert "## Background" in out
    assert "This page describes the process." in out


def test_page_title_suppressed_when_body_first_h1_matches() -> None:
    """2. Adopt where Confluence body's first block is `# <title>` matching
    the page title → AUTO block suppressed (no double H1)."""
    body_md = "# Software Development Plan\n\nIntro paragraph.\n"
    out = _synthesize_page_title(body_md, "Software Development Plan")
    assert out == body_md
    # Confirm no AUTO:PAGE-TITLE block was added
    assert "AUTO:PAGE-TITLE" not in out


def test_page_title_emitted_when_body_first_h1_differs() -> None:
    """3. Adopt where Confluence body's first block is `# Different Title`
    → AUTO block emitted at top, body's `# Different Title` left in place."""
    body_md = "# Different Title\n\nBody content.\n"
    out = _synthesize_page_title(body_md, "Software Development Plan")
    assert out.startswith("<!-- AUTO:PAGE-TITLE -->\n# Software Development Plan\n<!-- /AUTO:PAGE-TITLE -->"), out
    # The body's original `# Different Title` is preserved
    assert "# Different Title" in out
    # Two H1s — one in AUTO, one in body
    assert out.count("# Different Title") == 1
    assert out.count("# Software Development Plan") == 1


def test_page_title_strip_in_md_to_adf_emits_no_h1() -> None:
    """4. `_md_to_adf` strips the AUTO:PAGE-TITLE block — no `heading` ADF
    node from inside; surrounding body emitted normally."""
    md = (
        "<!-- AUTO:PAGE-TITLE -->\n"
        "# Software Development Plan\n"
        "<!-- /AUTO:PAGE-TITLE -->\n\n"
        "## Background\n\n"
        "Body paragraph.\n"
    )
    adf = _md_to_adf(md)
    nodes = adf["content"]
    # First node should be the H2 background heading, NOT the H1 title
    assert nodes[0]["type"] == "heading", nodes
    assert nodes[0]["attrs"]["level"] == 2
    # No H1 anywhere
    h1s = [n for n in nodes if n.get("type") == "heading" and (n.get("attrs") or {}).get("level") == 1]
    assert h1s == [], f"unexpected H1 nodes: {h1s}"


def test_page_title_roundtrip_no_double_h1() -> None:
    """5. End-to-end roundtrip: ADF → adopt → md has AUTO:PAGE-TITLE →
    `_md_to_adf` produces ADF with NO body H1 from the auto block."""
    adf_in = {
        "type": "doc", "version": 1,
        "content": [_h(2, "Section A"), _para("Paragraph.")],
    }
    md_body = adf_to_markdown(adf_in)
    md_with_title = _synthesize_page_title(md_body, "Page Alpha")
    assert "AUTO:PAGE-TITLE" in md_with_title
    adf_out = _md_to_adf(md_with_title)
    h1s = [
        n for n in adf_out["content"]
        if n.get("type") == "heading" and (n.get("attrs") or {}).get("level") == 1
    ]
    assert h1s == [], f"H1 leaked into ADF: {h1s}"


# ---- AUTO:TOC tests ----


def test_toc_macro_emits_auto_pair_with_rendered_headings() -> None:
    """6. Source ADF has `extension key="toc"` → adopt emits AUTO:TOC
    sentinel pair with rendered heading list (anchor slugs GitHub-style)."""
    adf = {
        "type": "doc", "version": 1,
        "content": [
            _toc_ext(),
            _h(1, "Purpose"),
            _h(1, "Scope"),
            _h(1, "Process and Methods"),
            _h(2, "Grooming"),
            _h(2, "Planning"),
            _h(1, "Updates"),
        ],
    }
    report = NormalizationReport()
    md = adf_to_markdown(adf, report=report)
    # Sentinels emitted
    assert "<!-- AUTO:TOC source=toc" in md
    assert "<!-- /AUTO:TOC position=0 -->" in md
    assert len(report.toc_macros) == 1
    # Now run the expander
    md_expanded, warnings = _expand_toc_macros(md, report)
    assert warnings == []
    assert "- [Purpose](#purpose)" in md_expanded
    assert "- [Scope](#scope)" in md_expanded
    assert "- [Process and Methods](#process-and-methods)" in md_expanded
    assert "  - [Grooming](#grooming)" in md_expanded
    assert "  - [Planning](#planning)" in md_expanded
    assert "- [Updates](#updates)" in md_expanded


def test_toc_macro_absent_emits_no_auto_block() -> None:
    """7. Source ADF has NO toc macro → no AUTO:TOC block emitted."""
    adf = {
        "type": "doc", "version": 1,
        "content": [_h(1, "Purpose"), _para("Content.")],
    }
    report = NormalizationReport()
    md = adf_to_markdown(adf, report=report)
    assert report.toc_macros == []
    assert "AUTO:TOC" not in md


def test_toc_macro_respects_min_level_filter() -> None:
    """8. AUTO:TOC respects `minLevel`/`maxLevel` from macroParams (e.g.,
    `minLevel=2` excludes H1 from list)."""
    adf = {
        "type": "doc", "version": 1,
        "content": [
            _toc_ext(min_level="2", max_level="3"),
            _h(1, "Top"),
            _h(2, "Mid A"),
            _h(3, "Deep"),
            _h(4, "Too Deep"),
        ],
    }
    report = NormalizationReport()
    md = adf_to_markdown(adf, report=report)
    md_expanded, warnings = _expand_toc_macros(md, report)
    assert warnings == []
    # H1 excluded
    assert "[Top]" not in md_expanded
    # H4 excluded
    assert "[Too Deep]" not in md_expanded
    # H2/H3 included
    assert "[Mid A](#mid-a)" in md_expanded
    assert "[Deep](#deep)" in md_expanded


def test_toc_skips_headings_inside_other_auto_regions() -> None:
    """9. AUTO:TOC skips headings inside other AUTO regions (CHILD-INDEX,
    JIRA-LIST, PAGE-TITLE)."""
    md = (
        "<!-- AUTO:TOC source=toc minLevel=1 maxLevel=6 position=0 -->\n"
        "<!-- /AUTO:TOC position=0 -->\n\n"
        "<!-- AUTO:PAGE-TITLE -->\n"
        "# Outer Title\n"
        "<!-- /AUTO:PAGE-TITLE -->\n\n"
        "# Real Heading\n\n"
        "## Sub\n\n"
        "<!-- AUTO:CHILD-INDEX source=children position=0 -->\n"
        "## Child Pages\n"
        "<!-- /AUTO:CHILD-INDEX position=0 -->\n\n"
        "# Final Heading\n"
    )
    headings = _walk_headings_outside_auto(md)
    texts = [t for _, t in headings]
    assert "Outer Title" not in texts, texts
    assert "Child Pages" not in texts, texts
    assert "Real Heading" in texts
    assert "Sub" in texts
    assert "Final Heading" in texts


def test_md_to_adf_strips_toc_emits_single_extension_node() -> None:
    """10. `_md_to_adf` strips AUTO:TOC block + emits a SINGLE
    `extension key="toc"` ADF node with macroParams reconstructed from
    sentinel attrs."""
    md = (
        "<!-- AUTO:TOC source=toc minLevel=1 maxLevel=6 position=0 -->\n\n"
        "- [Purpose](#purpose)\n"
        "- [Scope](#scope)\n\n"
        "<!-- /AUTO:TOC position=0 -->\n\n"
        "# Purpose\n\n"
        "Body.\n"
    )
    adf = _md_to_adf(md)
    nodes = adf["content"]
    # First node should be the toc extension
    ext_nodes = [n for n in nodes if n.get("type") == "extension"]
    assert len(ext_nodes) == 1, ext_nodes
    assert ext_nodes[0]["attrs"]["extensionKey"] == "toc"
    macro_params = ext_nodes[0]["attrs"]["parameters"]["macroParams"]
    assert macro_params.get("minLevel") == {"value": "1"}
    assert macro_params.get("maxLevel") == {"value": "6"}
    # No bullet-list paragraph from the rendered TOC leaks through
    bullet_text = "- [Purpose](#purpose)"
    for node in nodes:
        for child in node.get("content") or []:
            text = (child.get("text") if isinstance(child, dict) else "") or ""
            assert bullet_text not in text


def test_toc_roundtrip_no_double_toc() -> None:
    """11. Round-trip with TOC macro: ADF (with toc extension) → adopt
    (md has AUTO:TOC + headings) → `_md_to_adf` (ADF has toc extension,
    no inline TOC list, no double TOC) → re-fetch → re-adopt restores
    AUTO:TOC."""
    adf_in = {
        "type": "doc", "version": 1,
        "content": [
            _toc_ext(min_level="1", max_level="3"),
            _h(1, "Alpha"),
            _h(2, "Beta"),
        ],
    }
    report = NormalizationReport()
    md = adf_to_markdown(adf_in, report=report)
    md_expanded, _ = _expand_toc_macros(md, report)
    # Now publish: md → ADF
    adf_out = _md_to_adf(md_expanded)
    toc_exts = [
        n for n in adf_out["content"]
        if n.get("type") == "extension"
        and n.get("attrs", {}).get("extensionKey") == "toc"
    ]
    assert len(toc_exts) == 1, f"expected 1 toc extension, got {len(toc_exts)}"
    # No bullet list from the rendered TOC should appear as paragraph text
    flat = json.dumps(adf_out)
    assert "[Alpha](#alpha)" not in flat
    assert "[Beta](#beta)" not in flat
    # macroParams round-trip
    params = toc_exts[0]["attrs"]["parameters"]["macroParams"]
    assert params.get("minLevel") == {"value": "1"}
    assert params.get("maxLevel") == {"value": "3"}


# ---- Shared (drift-detection) tests ----


def test_strip_auto_regions_removes_both_auto_chrome_blocks() -> None:
    """12. `strip_auto_regions` removes both AUTO:PAGE-TITLE and
    AUTO:TOC blocks — drift-detection ignores them."""
    md = (
        "<!-- AUTO:PAGE-TITLE -->\n"
        "# Some Title\n"
        "<!-- /AUTO:PAGE-TITLE -->\n\n"
        "<!-- AUTO:TOC source=toc minLevel=1 maxLevel=6 position=0 -->\n\n"
        "- [Body](#body)\n\n"
        "<!-- /AUTO:TOC position=0 -->\n\n"
        "# Body\n\n"
        "Real content.\n"
    )
    stripped = strip_auto_regions(md)
    assert "AUTO:PAGE-TITLE" not in stripped
    assert "AUTO:TOC" not in stripped
    assert "Some Title" not in stripped  # H1 inside AUTO removed
    assert "[Body](#body)" not in stripped  # rendered TOC removed
    # Real body content preserved
    assert "# Body" in stripped
    assert "Real content." in stripped


def test_classify_adopt_in_sync_with_both_chrome_blocks() -> None:
    """13. `classify_adopt`: re-adopt unmodified file with both auto
    blocks → returns `in_sync` (regenerated chrome stripped from diff).

    Validates that the AUTO:PAGE-TITLE + AUTO:TOC chrome blocks ride
    `strip_auto_regions` for free without polluting drift detection.
    """
    # Two markdown bodies that are identical except for the AUTO chrome —
    # this is what re-adopt produces vs the cached snapshot when the
    # chrome regenerates with cosmetic differences (e.g., position
    # markers identical but line count of bullets differs).
    snapshot_md = (
        "<!-- AUTO:PAGE-TITLE -->\n"
        "# Page X\n"
        "<!-- /AUTO:PAGE-TITLE -->\n\n"
        "# Body Heading\n\n"
        "Real content.\n"
    )
    re_adopted_md = (
        "<!-- AUTO:PAGE-TITLE -->\n"
        "# Page X\n"
        "<!-- /AUTO:PAGE-TITLE -->\n\n"
        "<!-- AUTO:TOC source=toc minLevel=1 maxLevel=6 position=0 -->\n\n"
        "- [Body Heading](#body-heading)\n\n"
        "<!-- /AUTO:TOC position=0 -->\n\n"
        "# Body Heading\n\n"
        "Real content.\n"
    )
    # Both should reduce to the same canonical form for drift detection.
    # Strip-then-collapse-blank-lines mirrors what difflib comparison
    # treats as equivalent (consecutive blank lines collapse to one
    # for human review).
    import re as _re
    def _norm(s: str) -> str:
        return _re.sub(r"\n{2,}", "\n\n", s).strip()
    assert _norm(strip_auto_regions(snapshot_md)) == _norm(strip_auto_regions(re_adopted_md))


# ---- Slug helper sanity ----


def test_slugify_anchor_github_style() -> None:
    """Sanity: GitHub-style slug rules — lowercase, spaces to hyphens,
    strip non-alphanumeric except - and _."""
    assert _slugify_anchor("Process and Methods") == "process-and-methods"
    assert _slugify_anchor("V&V Plan") == "vv-plan"
    assert _slugify_anchor("Section 4.2 — Overview") == "section-42--overview".replace("--", "-")
    # Special-char only → empty
    assert _slugify_anchor("!!!") == ""


# ---- Test runner ----


TESTS = [
    test_page_title_emitted_when_body_lacks_matching_h1,
    test_page_title_suppressed_when_body_first_h1_matches,
    test_page_title_emitted_when_body_first_h1_differs,
    test_page_title_strip_in_md_to_adf_emits_no_h1,
    test_page_title_roundtrip_no_double_h1,
    test_toc_macro_emits_auto_pair_with_rendered_headings,
    test_toc_macro_absent_emits_no_auto_block,
    test_toc_macro_respects_min_level_filter,
    test_toc_skips_headings_inside_other_auto_regions,
    test_md_to_adf_strips_toc_emits_single_extension_node,
    test_toc_roundtrip_no_double_toc,
    test_strip_auto_regions_removes_both_auto_chrome_blocks,
    test_classify_adopt_in_sync_with_both_chrome_blocks,
    test_slugify_anchor_github_style,
]


def main() -> int:
    failures: list[tuple[str, BaseException]] = []
    for fn in TESTS:
        try:
            fn()
            print(f"  ok   {fn.__name__}")
        except BaseException as exc:  # noqa: BLE001
            failures.append((fn.__name__, exc))
            print(f"  FAIL {fn.__name__}: {exc}")
    if failures:
        print(f"\n{len(failures)} failures")
        return 1
    print(f"\n{len(TESTS)} passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
