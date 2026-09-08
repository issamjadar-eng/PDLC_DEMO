"""Regression tests for the depth-safe descendants paginator and the
first-class manifest artifact (task 125).

Covers:

  Phase A — paginator
    1. Default depth=10 is passed to the MCP tool (was implicitly 2).
    2. Cursor pagination follows `_links.next` until exhausted.
    3. Returning `limit` with no cursor raises (silent-truncation guard).

  Phase B — manifest
    4. Manifest schema round-trips deterministically (write/read).
    5. plan_paths is deterministic — same input → same paths.
    6. Container detection: a parent with children at depth=3+ is
       classified as `is_container=True`.
    7. Version-sibling collapse with deeply-nested topics:
         - Parent IS the topic → version files land at parent's folder
         - Parent is NOT the topic → version files nest under topic-slug
    8. annotate_pages_with_planned_paths fills `child_count`,
       `is_container`, `target_path` on every page.

Offline only — no Confluence calls. Run with:

    python3 .claude/skills/change-control/tests/test_depth_and_manifest.py
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_ROOT))

from lib.confluence_mcp import (  # noqa: E402
    ConfluenceMCP,
    MCPError,
)
from lib.manifest import (  # noqa: E402
    MANIFEST_VERSION,
    Manifest,
    ManifestPage,
    annotate_pages_with_planned_paths,
    plan_paths,
    read_manifest,
    write_manifest,
)


# ---- Phase A: paginator ----


class _RecordingMCP:
    """Test double: records every call and returns scripted responses
    keyed by (tool, kwargs-tuple)."""

    def __init__(self, scripts: list[tuple[dict, object]]):
        # scripts is a list of (kwargs_subset, response) pairs. We
        # match the first script whose subset is contained in the
        # call kwargs.
        self.scripts = scripts
        self.calls: list[tuple[str, dict]] = []
        self.cloud_id = "cid"

    def __call__(self, tool: str, **kwargs):
        self.calls.append((tool, dict(kwargs)))
        for subset, response in self.scripts:
            if all(kwargs.get(k) == v for k, v in subset.items()):
                return response
        raise AssertionError(
            f"No scripted response for {tool}({kwargs}); "
            f"available: {[s for s, _ in self.scripts]}"
        )


def test_paginator_passes_default_depth_10():
    mcp_call = _RecordingMCP([
        # No cursor, single page
        ({"pageId": "ROOT"}, {"results": [{"id": "A"}, {"id": "B"}]}),
    ])
    mcp = ConfluenceMCP(mcp_call, cloud_id="cid")
    out = mcp.get_descendants_paginated("ROOT")
    assert len(out) == 2
    # The first call must have specified an explicit depth (we default to 10)
    first_call = mcp_call.calls[0]
    assert first_call[0] == "getConfluencePageDescendants"
    assert first_call[1]["depth"] == 10, (
        f"expected depth=10 in first call, got {first_call[1]}"
    )
    print("  ok: paginator passes default depth=10")


def test_paginator_follows_cursor():
    # Page 1: 3 results + _links.next pointing to cursor=PAGE2
    # Page 2: 2 results, no cursor
    mcp_call = _RecordingMCP([
        ({"pageId": "ROOT", "cursor": "PAGE2"},
         {"results": [{"id": "D"}, {"id": "E"}]}),
        ({"pageId": "ROOT"},
         {"results": [{"id": "A"}, {"id": "B"}, {"id": "C"}],
          "_links": {"next": "/some/path?cursor=PAGE2&limit=250"}}),
    ])
    mcp = ConfluenceMCP(mcp_call, cloud_id="cid")
    out = mcp.get_descendants_paginated("ROOT", depth=10, page_limit=250)
    assert [p["id"] for p in out] == ["A", "B", "C", "D", "E"]
    assert len(mcp_call.calls) == 2
    print("  ok: paginator follows _links.next cursor across 2 pages")


def test_paginator_raises_on_silent_truncation():
    # page_limit=3, response is exactly 3 results, NO cursor → raise
    mcp_call = _RecordingMCP([
        ({"pageId": "ROOT"},
         {"results": [{"id": "A"}, {"id": "B"}, {"id": "C"}]}),
    ])
    mcp = ConfluenceMCP(mcp_call, cloud_id="cid")
    try:
        mcp.get_descendants_paginated("ROOT", depth=10, page_limit=3)
    except MCPError as exc:
        assert "page limit" in str(exc).lower() or "limit" in str(exc).lower()
        print("  ok: paginator raises on silent truncation (limit-with-no-cursor)")
        return
    raise AssertionError("expected MCPError when limit hit with no cursor")


def test_paginator_handles_nextcursor_field():
    # Some MCP shapes return `nextCursor` directly instead of _links.next
    mcp_call = _RecordingMCP([
        ({"pageId": "ROOT", "cursor": "TOKEN2"},
         {"results": [{"id": "C"}]}),
        ({"pageId": "ROOT"},
         {"results": [{"id": "A"}, {"id": "B"}], "nextCursor": "TOKEN2"}),
    ])
    mcp = ConfluenceMCP(mcp_call, cloud_id="cid")
    out = mcp.get_descendants_paginated("ROOT")
    assert [p["id"] for p in out] == ["A", "B", "C"]
    print("  ok: paginator handles nextCursor field")


# ---- Phase B: manifest ----


def _sample_manifest() -> Manifest:
    return Manifest(
        tool_version="0.7.0",
        cloud_id="cid-uuid",
        space_key="EX",
        base_url="https://example.atlassian.net",
        root_page_id="100",
        pulled_at="2026-04-29",
        pages=[
            ManifestPage(id="100", title="Root", parent_id="", depth=0,
                         confluence_version=4),
            ManifestPage(id="200", title="Module - Vulnerabilities (SEC)",
                         parent_id="100", depth=1, confluence_version=4),
            ManifestPage(id="201", title="Module - Vulnerabilities (SEC) - 1.0.0",
                         parent_id="200", depth=2, confluence_version=2),
            ManifestPage(id="202", title="Module - Vulnerabilities (SEC) - 2.0.0",
                         parent_id="200", depth=2, confluence_version=2),
        ],
    )


def test_manifest_round_trip_deterministic():
    m = _sample_manifest()
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / ".manifest.json"
        write_manifest(path, m)
        bytes1 = path.read_bytes()
        # Read back and re-write — must be byte-identical
        m2 = read_manifest(path)
        write_manifest(path, m2)
        bytes2 = path.read_bytes()
        assert bytes1 == bytes2, "manifest round-trip is not byte-deterministic"
        # And the round-trip preserves manifest_version
        assert m2.manifest_version == MANIFEST_VERSION
        assert len(m2.pages) == 4
        assert m2.pages[2].confluence_version == 2
    print("  ok: manifest round-trips deterministically")


def test_planner_determinism():
    m = _sample_manifest()
    p1 = plan_paths(m, prefixes=["Module - "],
                    staging_root="docs/_x/intra")
    p2 = plan_paths(m, prefixes=["Module - "],
                    staging_root="docs/_x/intra")
    assert p1 == p2
    print("  ok: planner determinism")


def test_planner_version_sibling_parent_is_topic():
    """When parent IS the topic (parent stem == versioned-child stem),
    versions land directly in parent's folder — no redundant subfolder."""
    m = _sample_manifest()
    paths = plan_paths(m, prefixes=["Module - "],
                       staging_root="docs/_x/intra")
    # The parent (200) carries title "Module - Vulnerabilities (SEC)";
    # the children (201, 202) are "Module - Vulnerabilities (SEC) - X.Y.Z".
    # Parent stem and child stem both slug to "vulnerabilities-sec", so
    # the parent IS the topic — children land directly in parent's folder.
    assert paths["200"] == "docs/_x/intra/root/vulnerabilities-sec/index.md", paths["200"]
    assert paths["201"] == "docs/_x/intra/root/vulnerabilities-sec/v1.0.0.md", paths["201"]
    assert paths["202"] == "docs/_x/intra/root/vulnerabilities-sec/v2.0.0.md", paths["202"]
    print("  ok: planner version-sibling parent-is-topic collapse")


def test_planner_version_sibling_parent_is_not_topic():
    """When the parent is NOT the topic (different stem), versions
    nest under a subfolder named after the topic slug."""
    m = Manifest(
        tool_version="t", cloud_id="c", space_key="EX",
        base_url="https://x.atlassian.net", root_page_id="100",
        pulled_at="2026-04-29",
        pages=[
            ManifestPage(id="100", title="Root", parent_id="", depth=0),
            # Parent is a generic group, not the topic itself
            ManifestPage(id="300", title="Module - Windchill Documentation",
                         parent_id="100", depth=1),
            # Versioned child whose stem differs from the parent's stem
            ManifestPage(id="301", title="Module - Hazard Analysis - 1.0.0",
                         parent_id="300", depth=2),
            ManifestPage(id="302", title="Module - Hazard Analysis - 2.0.0",
                         parent_id="300", depth=2),
        ],
    )
    paths = plan_paths(m, prefixes=["Module - "],
                       staging_root="docs/_x/intra")
    # Parent slug: "windchill-documentation". Topic slug: "hazard-analysis".
    # They don't match, so versions land under parent's folder + topic-slug subfolder.
    assert paths["301"] == \
        "docs/_x/intra/root/windchill-documentation/hazard-analysis/v1.0.0.md", paths["301"]
    assert paths["302"] == \
        "docs/_x/intra/root/windchill-documentation/hazard-analysis/v2.0.0.md", paths["302"]
    print("  ok: planner version-sibling parent-is-NOT-topic nesting")


def test_planner_container_detection_at_depth_3():
    """A page with children at depth=3+ must be classified as a
    container (`<slug>/index.md`), not a leaf. This is the exact
    bug-class that motivated this task."""
    m = Manifest(
        tool_version="t", cloud_id="c", space_key="EX",
        base_url="https://x.atlassian.net", root_page_id="100",
        pulled_at="2026-04-29",
        pages=[
            ManifestPage(id="100", title="Root", parent_id="", depth=0),
            ManifestPage(id="400", title="Module - Software Detailed Design (SDD)",
                         parent_id="100", depth=1),
            # depth=2 — versioned child, container with depth=3 grandchildren
            ManifestPage(id="401",
                         title="Module - Software Detailed Design (SDD) - 1.0.0",
                         parent_id="400", depth=2),
            # depth=3 — an actual leaf design spec under SDD-1.0.0
            ManifestPage(id="402",
                         title="Module - SDD Design Spec — Foo",
                         parent_id="401", depth=3),
            ManifestPage(id="403",
                         title="Module - SDD Design Spec — Bar",
                         parent_id="401", depth=3),
        ],
    )
    annotate_pages_with_planned_paths(
        m, prefixes=["Module - "], staging_root="docs/_x/intra"
    )
    by_id = {p.id: p for p in m.pages}
    # 400 is parent of a single versioned child → "sdd" topic container
    assert by_id["400"].is_container is True, "400 should be a container"
    # 401 is the v1.0.0 page; it has children at depth=3 → MUST be container
    assert by_id["401"].is_container is True, \
        "401 (SDD - 1.0.0) has depth=3 children, must be container"
    assert by_id["401"].child_count == 2
    # 402, 403 are leaves
    assert by_id["402"].is_container is False
    assert by_id["403"].is_container is False
    # And 402's planned path lands UNDER 401's folder (which now exists
    # as `<...>/v1.0.0/` because 401 is a versioned container).
    p402 = by_id["402"].target_path
    assert "/v1.0.0/" in p402, f"expected /v1.0.0/ segment in {p402}"
    assert p402.endswith("sdd-design-spec-foo.md"), p402
    # And 401's own path is `v1.0.0/index.md` (versioned container, not file)
    assert by_id["401"].target_path.endswith("/v1.0.0/index.md"), \
        by_id["401"].target_path
    print("  ok: planner container-detection at depth=3+")


def test_annotate_fills_target_path_and_counts():
    m = _sample_manifest()
    annotate_pages_with_planned_paths(
        m, prefixes=["Module - "], staging_root="docs/_x/intra"
    )
    root = m.pages[0]
    parent = m.pages[1]
    child = m.pages[2]
    # Root has 1 child (the parent at depth=1)
    assert root.child_count == 1
    assert root.is_container is True
    assert root.target_path.endswith("/index.md")
    # Parent has 2 children (the versioned siblings)
    assert parent.child_count == 2
    assert parent.is_container is True
    # Versioned children are leaves
    assert child.child_count == 0
    assert child.is_container is False
    print("  ok: annotate fills target_path + child_count + is_container")


# ---- Runner ----


TESTS = [
    test_paginator_passes_default_depth_10,
    test_paginator_follows_cursor,
    test_paginator_raises_on_silent_truncation,
    test_paginator_handles_nextcursor_field,
    test_manifest_round_trip_deterministic,
    test_planner_determinism,
    test_planner_version_sibling_parent_is_topic,
    test_planner_version_sibling_parent_is_not_topic,
    test_planner_container_detection_at_depth_3,
    test_annotate_fills_target_path_and_counts,
]


def main() -> int:
    failed = 0
    for t in TESTS:
        try:
            t()
        except AssertionError as e:
            print(f"  FAIL: {t.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"  ERROR: {t.__name__}: {type(e).__name__}: {e}")
            failed += 1
    print()
    print(f"{len(TESTS) - failed}/{len(TESTS)} tests passed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
