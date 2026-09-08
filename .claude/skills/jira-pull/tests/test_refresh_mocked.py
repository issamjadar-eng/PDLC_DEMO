"""Mocked-tier tests for the deterministic halves of `/jira-pull refresh`.

The Atlassian MCP search call runs inside the agent's tool loop and is not
callable from pytest. Everything on either side of it IS testable, and this
file exercises those seams against canned payloads under
`tests/fixtures/atlassian/` (synthetic DEMO-N issues — no real data):

  build_jql          — JQL composition incl. the `key >` cursor protocol
  _read_raw_response — every accepted response envelope shape
  merge_pages        — multi-page concatenation + dedupe on the cursor boundary
  normalize_issue    — raw → flat mirror shape, idempotent on flat input
  build_meta         — provenance block written to each layer file

Tier: `mocked` (hermetic; the conftest socket guard is active). A single
`live` placeholder documents what a real-endpoint smoke test would need.

Run:
    uv run --no-project --with pytest --with pyyaml -- \
        pytest .claude/skills/jira-pull/tests/test_refresh_mocked.py -q
"""
from __future__ import annotations

import json
import socket
from pathlib import Path

import pytest

from jirapull_testkit import NetworkAccessInNonLiveTest, load_lib_module, load_refresh_module

norm = load_lib_module("normalize")
refresh = load_refresh_module()

pytestmark = pytest.mark.mocked


# ─── Envelope shapes ─────────────────────────────────────────────────────


def test_read_raw_response_accepts_page_envelope(atlassian_fixtures: Path) -> None:
    issues = refresh._read_raw_response(atlassian_fixtures / "search_page1.json")
    assert [i["key"] for i in issues] == ["DEMO-101", "DEMO-102"]


def test_read_raw_response_accepts_wrapped_nodes_envelope(atlassian_fixtures: Path) -> None:
    issues = refresh._read_raw_response(atlassian_fixtures / "search_wrapped_nodes.json")
    assert [i["key"] for i in issues] == ["DEMO-301"]


def test_read_raw_response_accepts_empty_result(atlassian_fixtures: Path) -> None:
    assert refresh._read_raw_response(atlassian_fixtures / "search_empty.json") == []


def test_read_raw_response_accepts_bare_list_and_pages(tmp_path: Path) -> None:
    bare = tmp_path / "bare.json"
    bare.write_text(json.dumps([{"key": "DEMO-1"}]))
    assert refresh._read_raw_response(bare) == [{"key": "DEMO-1"}]

    paged = tmp_path / "paged.json"
    paged.write_text(json.dumps({"pages": [{"issues": [{"key": "DEMO-1"}]},
                                           {"issues": {"nodes": [{"key": "DEMO-2"}]}}]}))
    assert [i["key"] for i in refresh._read_raw_response(paged)] == ["DEMO-1", "DEMO-2"]


def test_read_raw_response_rejects_unknown_shape(tmp_path: Path) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps({"nope": 1}))
    with pytest.raises(ValueError):
        refresh._read_raw_response(bad)


# ─── Pagination merge ────────────────────────────────────────────────────


def test_merge_pages_dedupes_cursor_boundary_and_keeps_order(atlassian_fixtures: Path) -> None:
    p1 = refresh._read_raw_response(atlassian_fixtures / "search_page1.json")
    p2 = refresh._read_raw_response(atlassian_fixtures / "search_page2.json")
    merged = refresh.merge_pages([p1, p2])
    # DEMO-102 appears on both pages (cursor boundary) and must survive once,
    # in first-seen position.
    assert [i["key"] for i in merged] == ["DEMO-101", "DEMO-102", "DEMO-103"]


def test_merge_pages_is_idempotent_on_retried_page(atlassian_fixtures: Path) -> None:
    p1 = refresh._read_raw_response(atlassian_fixtures / "search_page1.json")
    assert refresh.merge_pages([p1, p1]) == refresh.merge_pages([p1])


def test_merge_pages_keeps_keyless_records() -> None:
    merged = refresh.merge_pages([[{"summary": "no key"}, {"summary": "no key"}]])
    assert len(merged) == 2


def test_page_fixtures_mark_last_page_consistently(atlassian_fixtures: Path) -> None:
    """The cursor protocol: a non-final page carries `nextPageToken` and
    `isLast: false`; the final page carries `isLast: true`. The fixtures
    must model that so the mocked tier reflects the real envelope."""
    p1 = json.loads((atlassian_fixtures / "search_page1.json").read_text())
    p2 = json.loads((atlassian_fixtures / "search_page2.json").read_text())
    assert p1["isLast"] is False and p1.get("nextPageToken")
    assert p2["isLast"] is True and "nextPageToken" not in p2


# ─── JQL + cursor ────────────────────────────────────────────────────────


def test_build_jql_always_orders_by_key_and_applies_cursor() -> None:
    base = norm.build_jql("DEMO", "Module v1.0.0", "epics")
    assert base.endswith(" ORDER BY key ASC")
    assert 'project = "DEMO"' in base and 'fixVersion = "Module v1.0.0"' in base
    assert 'issuetype = "Epic"' in base

    paged = norm.build_jql("DEMO", "Module v1.0.0", "epics", cursor_after_key="DEMO-102")
    assert 'key > "DEMO-102"' in paged
    assert paged.endswith(" ORDER BY key ASC")


def test_build_jql_story_filter_clauses() -> None:
    jql = norm.build_jql("DEMO", "v1", "stories",
                         story_filter={"labels": ["swreq"], "statuses": ["Done", "In Review"]})
    assert "labels in (" in jql and "status in (" in jql


# ─── Normalization ───────────────────────────────────────────────────────


def test_normalize_issue_flattens_raw_shape(atlassian_fixtures: Path) -> None:
    raw = refresh._read_raw_response(atlassian_fixtures / "search_page1.json")[1]
    flat = norm.normalize_issue(raw)
    assert flat["key"] == "DEMO-102"
    assert flat["status"] == "To Do"
    assert flat["issuetype"] == "Epic"
    assert flat["fix_versions"] == ["Module v1.0.0"]
    assert flat["issuelinks"] == [{
        "type": "1 Relates", "direction": "outward", "relation": "relates to",
        "key": "DEMO-201", "summary": "Story for DI-0002",
    }]


def test_normalize_issue_reads_parent_from_wrapped_envelope(atlassian_fixtures: Path) -> None:
    raw = refresh._read_raw_response(atlassian_fixtures / "search_wrapped_nodes.json")[0]
    flat = norm.normalize_issue(raw)
    assert flat["parent_key"] == "DEMO-101"
    assert flat["parent_summary"].startswith("DI-0001")


def test_normalize_issue_is_idempotent_on_flat_input(atlassian_fixtures: Path) -> None:
    raw = refresh._read_raw_response(atlassian_fixtures / "search_page1.json")[0]
    once = norm.normalize_issue(raw)
    assert norm.normalize_issue(once) == once


def test_merged_pages_normalize_to_deterministic_sorted_keys(atlassian_fixtures: Path) -> None:
    p1 = refresh._read_raw_response(atlassian_fixtures / "search_page1.json")
    p2 = refresh._read_raw_response(atlassian_fixtures / "search_page2.json")
    flat = [norm.normalize_issue(r) for r in refresh.merge_pages([p2, p1])]
    keys = sorted(i["key"] for i in flat)
    assert keys == ["DEMO-101", "DEMO-102", "DEMO-103"]


# ─── Provenance ──────────────────────────────────────────────────────────


def test_build_meta_records_provenance_fields() -> None:
    meta = norm.build_meta(
        cloud_id="00000000-0000-0000-0000-000000000000",
        fix_version="Module v1.0.0", fix_version_id="10001", issuetype="Epic",
        jql='project = "DEMO" ORDER BY key ASC', issue_count=3,
        field_set=["summary", "status"], enriched_with=["description"],
    )
    assert meta["issue_count"] == 3
    assert meta["fix_version_id"] == "10001"
    assert meta["field_set"] == ["summary", "status"]
    assert meta["enriched_with"] == ["description"]
    assert meta["schema_version"] == "1.1"
    assert meta["pulled_at"].endswith("Z")


# ─── Tier plumbing self-test ─────────────────────────────────────────────


def test_socket_guard_blocks_network_in_mocked_tier() -> None:
    with pytest.raises(NetworkAccessInNonLiveTest):
        socket.create_connection(("example.invalid", 443), timeout=0.1)


@pytest.mark.live
def test_live_jira_search_smoke() -> None:
    """Placeholder for the live tier. With `--live`, it requires a configured
    connection (`project.yml change_control.jira.base_url`) — otherwise it
    skips with a reason so the report never shows a silent PASS. The MCP
    search itself cannot be driven from pytest; a live run here can only
    check reachability of the configured base URL."""
    import urllib.request

    try:
        import yaml  # type: ignore
    except ImportError:  # pragma: no cover
        pytest.skip("pyyaml not available")
    root = Path(__file__).resolve()
    proj = None
    for parent in root.parents:
        cand = parent / "project.yml"
        if cand.is_file():
            proj = cand
            break
    if proj is None:
        pytest.skip("no live connection configured (project.yml not found)")
    data = yaml.safe_load(proj.read_text()) or {}
    base_url = (((data.get("change_control") or {}).get("jira") or {}).get("base_url")) or ""
    if not base_url:
        pytest.skip("no live connection configured (change_control.jira.base_url unset)")
    with urllib.request.urlopen(base_url, timeout=10) as resp:  # noqa: S310
        assert resp.status < 500
