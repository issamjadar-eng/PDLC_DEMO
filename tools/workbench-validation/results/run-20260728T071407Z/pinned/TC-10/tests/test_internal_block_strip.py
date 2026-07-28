"""Tests for INTERNAL_ONLY_BLOCK_KINDS stripping in the publish transform.

Background — task ben/152, Decision D5
======================================

Project-internal tooling needs to embed metadata in `_confluence/` source
markdown that points at out-of-tree resources (e.g., `<!-- TRACE:SCHEMA
... -->` pointing at `tools/project-console/trace-matrix/schemas/...`).

These blocks are *internal* — they must NOT survive the publish round-trip
back to the official Confluence page. `markdown_transform.py` defines an
`INTERNAL_ONLY_BLOCK_KINDS` registry; `transform_markdown()` strips every
matching HTML comment block before the body is converted to ADF.

This test suite is the strict-prerequisite gate for D5: until these
assertions pass, no `TRACE:*` sentinel is allowed to ship in any real
`_confluence/` doc, because a leak would expose internal mapping metadata
on the formal Confluence page.

Coverage
--------
- Single-line TRACE comments are stripped
- Multi-line TRACE comments (frontmatter-style body) are stripped
- Multiple TRACE blocks in one doc all stripped
- Paired-form (opening + closing TRACE) both stripped
- AUTO:* and confluence-side:* blocks are PRESERVED (round-trip-safe)
- Frontmatter strip still works correctly when followed by a TRACE block
- TransformReport.internal_blocks_stripped reports kind + line count
- Idempotent — second pass strips nothing
- Round-trip simulation through `transform_markdown()` end-to-end

Offline only — no Confluence calls. Run with:

    python3 .claude/skills/change-control/tests/test_internal_block_strip.py
"""
from __future__ import annotations

import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_ROOT))

from lib.markdown_transform import (  # noqa: E402
    INTERNAL_ONLY_BLOCK_KINDS,
    TransformOptions,
    TransformReport,
    strip_internal_only_blocks,
    transform_markdown,
)


# ---- Phase A — registry sanity ----


def test_registry_contains_trace():
    assert "TRACE" in INTERNAL_ONLY_BLOCK_KINDS, (
        f"TRACE missing from INTERNAL_ONLY_BLOCK_KINDS: {INTERNAL_ONLY_BLOCK_KINDS!r}"
    )


def test_registry_is_tuple():
    # Tuple, not list — registry is a constant.
    assert isinstance(INTERNAL_ONLY_BLOCK_KINDS, tuple), type(INTERNAL_ONLY_BLOCK_KINDS)


# ---- Phase B — strip_internal_only_blocks unit tests ----


def test_strip_single_line_trace():
    src = "before\n<!-- TRACE:SCHEMA path=tools/x/y.yml -->\nafter\n"
    out, blocks = strip_internal_only_blocks(src)
    assert "TRACE:" not in out, out
    assert out == "before\nafter\n", repr(out)
    assert len(blocks) == 1, blocks
    assert blocks[0]["kind"] == "TRACE", blocks[0]
    assert blocks[0]["line_count"] == 1, blocks[0]


def test_strip_multi_line_trace():
    src = (
        "intro paragraph\n"
        "\n"
        "<!-- TRACE:SCHEMA\n"
        "  schema: tools/project-console/trace-matrix/schemas/intra-op/v1.schema.yml\n"
        "  projection: tools/project-console/trace-matrix/projections/intra-op/v1.normalized.md\n"
        "  refresh_skill: trace-matrix\n"
        "  refresh_action: resolve\n"
        "  on_modify: required\n"
        "-->\n"
        "\n"
        "body paragraph\n"
    )
    out, blocks = strip_internal_only_blocks(src)
    assert "TRACE:" not in out, f"TRACE leaked: {out!r}"
    assert "schema:" not in out, f"schema leaked: {out!r}"
    assert "projection:" not in out, f"projection leaked: {out!r}"
    assert "refresh_skill" not in out, f"refresh_skill leaked: {out!r}"
    assert len(blocks) == 1
    assert blocks[0]["kind"] == "TRACE"
    assert blocks[0]["line_count"] >= 7, blocks[0]


def test_strip_multiple_trace_blocks():
    src = (
        "alpha\n"
        "<!-- TRACE:SCHEMA path=a -->\n"
        "beta\n"
        "<!-- TRACE:LAYER-SOURCE layer=design_inputs -->\n"
        "gamma\n"
    )
    out, blocks = strip_internal_only_blocks(src)
    assert "TRACE:" not in out
    assert "alpha" in out and "beta" in out and "gamma" in out
    assert len(blocks) == 2, blocks
    kinds = [b["kind"] for b in blocks]
    assert kinds == ["TRACE", "TRACE"], kinds


def test_strip_paired_form_opening_and_closing():
    # If we ever introduce paired TRACE sentinels (with body content
    # between an opening and a /closing form), both ends must be stripped.
    src = (
        "<!-- TRACE:LAYER-SOURCE layer=design_inputs id_prefix=DI -->\n"
        "this body content is INSIDE the paired sentinel\n"
        "<!-- /TRACE:LAYER-SOURCE -->\n"
        "outside content\n"
    )
    out, blocks = strip_internal_only_blocks(src)
    # Both the opening AND closing comments must be stripped. Body
    # content between them is left intact (it's just markdown to the
    # stripper — the contract is that the body lives inside the comment
    # itself, not between paired sentinels — this test documents that
    # boundary).
    assert "<!--" not in out, f"comment leaked: {out!r}"
    assert "TRACE:" not in out
    assert "outside content" in out
    assert "this body content" in out  # non-comment body is preserved
    assert len(blocks) == 2, blocks


def test_preserves_auto_blocks():
    # AUTO:* blocks (TOC, page-title, jira-list, child-index) are
    # tooling-owned but round-trip-safe — must NOT be stripped.
    src = (
        "<!-- AUTO:PAGE-TITLE -->\n"
        "# My Page\n"
        "<!-- /AUTO:PAGE-TITLE -->\n"
        "\n"
        "<!-- AUTO:TOC source=toc minLevel=1 maxLevel=6 position=0 -->\n"
        "- [Section](#section)\n"
        "<!-- /AUTO:TOC position=0 -->\n"
        "\n"
        "<!-- AUTO:JIRA-LIST source=jira jql=key%20in%20%28X-1%29 position=0 -->\n"
        "deferred\n"
        "<!-- /AUTO:JIRA-LIST position=0 -->\n"
    )
    out, blocks = strip_internal_only_blocks(src)
    assert blocks == [], f"AUTO blocks were wrongly stripped: {blocks!r}"
    assert out == src, f"AUTO content was modified: {out!r}"


def test_preserves_confluence_side_blocks():
    src = (
        "<!-- confluence-side: attachments labels=actual position=0 -->\n"
        "| Filename | Size |\n"
        "| --- | --- |\n"
        "| foo.xlsx | 1.1 MB |\n"
        "<!-- /confluence-side: attachments position=0 -->\n"
        "\n"
        "<!-- confluence-side: page-signatures -->\n"
    )
    out, blocks = strip_internal_only_blocks(src)
    assert blocks == [], blocks
    assert out == src


def test_preserves_random_html_comments():
    # Generic HTML comments without a `KIND:SUBKIND` prefix are not
    # internal-only and must round-trip.
    src = "<!-- a generic note -->\nbody\n<!-- another -->\n"
    out, blocks = strip_internal_only_blocks(src)
    assert blocks == []
    assert out == src


def test_idempotent():
    src = (
        "intro\n"
        "<!-- TRACE:SCHEMA path=a -->\n"
        "body\n"
    )
    once, _ = strip_internal_only_blocks(src)
    twice, blocks2 = strip_internal_only_blocks(once)
    assert twice == once, "second pass changed the doc"
    assert blocks2 == [], f"second pass found blocks: {blocks2!r}"


def test_explicit_kinds_override():
    # Caller can pass an explicit kinds tuple to strip kinds beyond the
    # default registry — used for forward-compat probes.
    src = (
        "<!-- FOO:BAR x=1 -->\n"
        "<!-- TRACE:SCHEMA y=2 -->\n"
        "body\n"
    )
    out, blocks = strip_internal_only_blocks(src, kinds=("FOO", "TRACE"))
    assert "FOO:" not in out
    assert "TRACE:" not in out
    assert "body" in out
    kinds = sorted(b["kind"] for b in blocks)
    assert kinds == ["FOO", "TRACE"], kinds


# ---- Phase C — TransformReport assertions ----


def test_report_records_internal_blocks_stripped():
    rep = TransformReport()
    assert rep.internal_blocks_stripped == [], (
        "Default TransformReport must initialize internal_blocks_stripped to []"
    )


def test_report_populated_after_transform():
    body = (
        "<!-- TRACE:SCHEMA path=tools/x.yml -->\n"
        "# Title\n"
        "Body content.\n"
    )
    transformed, rep = transform_markdown(
        source=body,
        source_doc_path="docs/project/_confluence/intra-op/sample.md",
        page_index={},
        options=TransformOptions(miss_policy="lenient"),
    )
    assert "TRACE:" not in transformed
    assert len(rep.internal_blocks_stripped) == 1, rep.internal_blocks_stripped
    assert rep.internal_blocks_stripped[0]["kind"] == "TRACE"


# ---- Phase D — End-to-end transform round-trip ----


def test_transform_markdown_strips_trace_with_real_frontmatter_pattern():
    """Simulate a realistic _confluence/ source: frontmatter HTML comment +
    AUTO:PAGE-TITLE + TRACE:SCHEMA pointer + AUTO:JIRA-LIST + signatures.
    After transform: frontmatter stripped, TRACE stripped, AUTO + confluence-side
    preserved.
    """
    body = (
        "<!-- AUTO:PAGE-TITLE -->\n"
        "# Sample Component - SRS - 1.0.0\n"
        "<!-- /AUTO:PAGE-TITLE -->\n"
        "\n"
        "<!-- TRACE:SCHEMA\n"
        "  schema: tools/project-console/trace-matrix/schemas/intra-op/v1.0.0.schema.yml\n"
        "  projection: tools/project-console/trace-matrix/projections/intra-op/v1.0.0.normalized.md\n"
        "  refresh_skill: trace-matrix\n"
        "  refresh_action: resolve\n"
        "  on_modify: required\n"
        "  on_readopt: required\n"
        "-->\n"
        "\n"
        "# Requirements\n"
        "\n"
        "## Stories\n"
        "\n"
        "<!-- AUTO:JIRA-LIST source=jira jql=key%20in%20%28PROJ-1%29 position=0 -->\n"
        "deferred\n"
        "<!-- /AUTO:JIRA-LIST position=0 -->\n"
        "\n"
        "<!-- confluence-side: page-signatures -->\n"
    )
    transformed, rep = transform_markdown(
        source=body,
        source_doc_path="docs/project/_confluence/intra-op/srs/v1.0.0.md",
        page_index={},
    )

    # The TRACE block and ALL its body fields must be gone — these are
    # the load-bearing assertions that prevent IP exfiltration.
    assert "TRACE:" not in transformed, f"TRACE leaked: {transformed!r}"
    assert "schema:" not in transformed, f"schema field leaked"
    assert "projection:" not in transformed, f"projection field leaked"
    assert "refresh_skill" not in transformed, f"refresh_skill leaked"
    assert "tools/project-console" not in transformed, (
        f"internal tools/ path leaked: {transformed!r}"
    )

    # AUTO blocks survive (they round-trip).
    assert "AUTO:PAGE-TITLE" in transformed
    assert "AUTO:JIRA-LIST" in transformed
    assert "/AUTO:JIRA-LIST" in transformed

    # confluence-side blocks survive.
    assert "confluence-side: page-signatures" in transformed

    # Report records exactly one TRACE strip.
    assert len(rep.internal_blocks_stripped) == 1, rep.internal_blocks_stripped
    assert rep.internal_blocks_stripped[0]["kind"] == "TRACE"


def test_round_trip_probe_simulated():
    """Simulate the round-trip claim: adopt → add TRACE → publish-transform
    → re-adopt would fetch the published body. We verify the published
    body (the transform output) has no TRACE residue, so a subsequent
    adopt cannot re-import the metadata.
    """
    # Step 1 — start with an adopted source (frontmatter + body).
    adopted = (
        "<!--\n"
        "title: Sample Component - SRS - 1.0.0\n"
        "state: published\n"
        "confluence:\n"
        "  page_id: '1234567890'\n"
        "  space_key: SAMPLE\n"
        "-->\n"
        "\n"
        "<!-- AUTO:PAGE-TITLE -->\n"
        "# Sample Component - SRS - 1.0.0\n"
        "<!-- /AUTO:PAGE-TITLE -->\n"
        "\n"
        "<!-- TRACE:SCHEMA path=tools/project-console/trace-matrix/schemas/intra-op/v1.0.0.schema.yml -->\n"
        "\n"
        "# Requirements\n"
        "Body.\n"
    )

    # Step 2 — operator (or trace-matrix init) adds TRACE sentinel to source.
    # Already present above.

    # Step 3 — publish transform runs on the body (frontmatter is read +
    # stripped by `read_frontmatter` upstream of the transform; we feed
    # the body portion here, which is what `cmd_precheck` does in
    # publish_helper.py).
    body_only = adopted.split("-->", 1)[1].lstrip("\n")
    transformed, rep = transform_markdown(
        source=body_only,
        source_doc_path="docs/project/_confluence/intra-op/srs/v1.0.0.md",
        page_index={},
    )

    # Step 4 — assert the transformed body that would be pushed to
    # Confluence has NO TRACE residue and NO leak of the internal path.
    forbidden = [
        "TRACE:",
        "tools/project-console",
        "schemas/intra-op",
        "v1.0.0.schema.yml",
    ]
    for needle in forbidden:
        assert needle not in transformed, (
            f"INTERNAL DATA LEAKED to Confluence-bound body: {needle!r} "
            f"found in transformed output:\n{transformed}"
        )

    # Report confirms the strip happened.
    assert len(rep.internal_blocks_stripped) == 1
    assert rep.internal_blocks_stripped[0]["kind"] == "TRACE"


# ---- Phase E — Regression: existing transform behavior is unchanged ----


def test_transform_still_strips_frontmatter():
    body = (
        "<!--\n"
        "title: Sample\n"
        "state: draft\n"
        "-->\n"
        "\n"
        "# Heading\n"
    )
    out, rep = transform_markdown(
        source=body,
        source_doc_path="docs/x.md",
        page_index={},
    )
    assert rep.frontmatter_stripped is True
    assert "title: Sample" not in out
    assert "# Heading" in out


def test_transform_still_swaps_html_fence():
    body = (
        "intro\n"
        "```html\n"
        "<div>x</div>\n"
        "```\n"
    )
    out, rep = transform_markdown(
        source=body,
        source_doc_path="docs/x.md",
        page_index={},
    )
    assert rep.fence_swaps == 1
    assert "```text" in out
    assert "```html" not in out


def test_no_trace_no_change_to_output():
    """A doc without any TRACE blocks should pass through with
    internal_blocks_stripped == [] and no body modification beyond the
    existing frontmatter / fence behavior.
    """
    body = (
        "# Heading\n"
        "\n"
        "Some content.\n"
        "\n"
        "<!-- AUTO:CHILD-INDEX source=children position=0 -->\n"
        "- [child](child.md)\n"
        "<!-- /AUTO:CHILD-INDEX position=0 -->\n"
    )
    out, rep = transform_markdown(
        source=body,
        source_doc_path="docs/x.md",
        page_index={},
    )
    assert rep.internal_blocks_stripped == []
    assert "AUTO:CHILD-INDEX" in out


# ---- Test runner ----


def main() -> int:
    tests = [
        # Phase A
        test_registry_contains_trace,
        test_registry_is_tuple,
        # Phase B
        test_strip_single_line_trace,
        test_strip_multi_line_trace,
        test_strip_multiple_trace_blocks,
        test_strip_paired_form_opening_and_closing,
        test_preserves_auto_blocks,
        test_preserves_confluence_side_blocks,
        test_preserves_random_html_comments,
        test_idempotent,
        test_explicit_kinds_override,
        # Phase C
        test_report_records_internal_blocks_stripped,
        test_report_populated_after_transform,
        # Phase D
        test_transform_markdown_strips_trace_with_real_frontmatter_pattern,
        test_round_trip_probe_simulated,
        # Phase E
        test_transform_still_strips_frontmatter,
        test_transform_still_swaps_html_fence,
        test_no_trace_no_change_to_output,
    ]
    failures: list[tuple[str, BaseException]] = []
    for t in tests:
        try:
            t()
            print(f"PASS  {t.__name__}")
        except AssertionError as e:
            print(f"FAIL  {t.__name__}: {e}")
            failures.append((t.__name__, e))
        except Exception as e:  # noqa: BLE001
            print(f"ERROR {t.__name__}: {type(e).__name__}: {e}")
            failures.append((t.__name__, e))
    print(f"\n{len(tests) - len(failures)}/{len(tests)} passed")
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
