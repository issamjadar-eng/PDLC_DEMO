"""Regression tests for task 131 — change-control v0.10.0 bundle.

Covers all five phases:

  Phase A — children/pagetree macro normalizer + action-layer renderer
    1. ADF children macro → AUTO:CHILD-INDEX sentinel pair, params captured
    2. ADF pagetree macro → same shape, kind=pagetree
    3. Renderer produces correct relative paths between two test files
       at different tree depths (using a fixture manifest)

  Phase B — stub-container synthesis (Q5b)
    4. is_container && body has no child macro → synthesized AUTO block
    5. is_container && body has macro → no synthesis (avoid double TOC)

  Phase C — jira macro
    6. ADF jira macro → AUTO:JIRA-LIST sentinel pair, params captured
    7. Renderer graceful-degrades on auth failure (mock cookie failure)

  Phase D — underline preservation
    8. ADF mark.underline → markdown <u>...</u>
    9. Markdown <u>...</u> → ADF mark.underline (round-trip)

  Phase E — sentinel-aware diff (the keystone)
   10. strip_auto_regions removes AUTO:CHILD-INDEX content
   11. strip_auto_regions handles legacy solo `confluence-side: toc`
   12. classify_adopt returns `in_sync` when only diff is inside AUTO

  Phase F — publish-side strip + macro reconstruction
   13. AUTO:CHILD-INDEX block → single ADF extension w/ extensionKey=children

Offline only — no Confluence calls. Run:

    python3 .claude/skills/change-control/tests/test_v010_bundle.py
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
from lib.adopt_sync import classify_adopt  # noqa: E402


# ---- Phase A — normalizer ----


def _children_ext(depth: str | None = None, kind: str = "children") -> dict:
    params = {"macroParams": {}}
    if depth is not None:
        params["macroParams"]["depth"] = {"value": depth}
    return {
        "type": "extension",
        "attrs": {
            "extensionType": "com.atlassian.confluence.macro.core",
            "extensionKey": kind,
            "parameters": params,
        },
    }


def test_a_children_macro_emits_sentinel_and_captures_params() -> None:
    adf = {"type": "doc", "content": [_children_ext(depth="3")]}
    report = NormalizationReport()
    md = adf_to_markdown(adf, report=report)
    assert "<!-- AUTO:CHILD-INDEX source=children depth=3 position=0 -->" in md, md
    assert "<!-- /AUTO:CHILD-INDEX position=0 -->" in md, md
    assert len(report.child_index_macros) == 1, report.child_index_macros
    rec = report.child_index_macros[0]
    assert rec["kind"] == "children"
    assert rec["depth"] == "3"
    assert rec["position"] == 0


def test_a_pagetree_macro_emits_sentinel() -> None:
    adf = {"type": "doc", "content": [_children_ext(kind="pagetree")]}
    report = NormalizationReport()
    md = adf_to_markdown(adf, report=report)
    assert "<!-- AUTO:CHILD-INDEX source=pagetree" in md, md
    assert report.child_index_macros[0]["kind"] == "pagetree"


def test_a_renderer_produces_correct_relative_paths() -> None:
    """Two child pages at different depths — relpath from a parent's
    index.md should point into each child's planned target_path."""
    from actions.adopt_helper import _render_child_index_list

    children = [
        {"id": "100", "title": "First Child",
         "target_path": "docs/_confluence/topic/first-child/index.md"},
        {"id": "200", "title": "Second Child",
         "target_path": "docs/_confluence/topic/second-child.md"},
    ]
    self_target = Path("/repo/docs/_confluence/topic/index.md")
    repo_root = Path("/repo")
    out = _render_child_index_list(
        children, self_target=self_target, repo_root=repo_root
    )
    assert "[First Child](first-child/index.md)" in out, out
    assert "[Second Child](second-child.md)" in out, out


def test_a_renderer_relpath_two_levels_deep() -> None:
    """Page at deeper tree level — relpath should walk up + back down."""
    from actions.adopt_helper import _render_child_index_list

    children = [
        {"id": "300", "title": "Sibling",
         "target_path": "docs/_confluence/topic/sub/sibling.md"},
    ]
    self_target = Path("/repo/docs/_confluence/topic/sub/index.md")
    repo_root = Path("/repo")
    out = _render_child_index_list(
        children, self_target=self_target, repo_root=repo_root
    )
    assert "[Sibling](sibling.md)" in out, out


# ---- Phase B — stub-container ----


def test_b_stub_synthesis_when_container_has_no_macro() -> None:
    from actions.adopt_helper import _maybe_synthesize_stub_container

    md = "# Container Page\n\nSome intro text.\n"
    pages = [
        {"id": "P", "title": "Container", "parent_id": "",
         "is_container": True, "child_count": 2,
         "target_path": "docs/x/index.md"},
        {"id": "C1", "title": "Child One", "parent_id": "P",
         "is_container": False, "target_path": "docs/x/c1.md"},
        {"id": "C2", "title": "Child Two", "parent_id": "P",
         "is_container": False, "target_path": "docs/x/c2.md"},
    ]
    report = NormalizationReport()
    new_md, synth, warnings = _maybe_synthesize_stub_container(
        md,
        page_id="P",
        target_path=Path("/repo/docs/x/index.md"),
        manifest_pages=pages,
        repo_root=Path("/repo"),
        report=report,
    )
    assert synth is True
    assert "<!-- AUTO:CHILD-INDEX source=stub-container position=0 -->" in new_md
    assert "[Child One](c1.md)" in new_md
    assert "[Child Two](c2.md)" in new_md


def test_b_no_stub_synthesis_when_macro_already_in_body() -> None:
    from actions.adopt_helper import _maybe_synthesize_stub_container

    md = "# Container\n\n<!-- AUTO:CHILD-INDEX source=children position=0 -->\n<!-- /AUTO:CHILD-INDEX position=0 -->\n"
    pages = [
        {"id": "P", "title": "Container", "parent_id": "",
         "is_container": True, "child_count": 1,
         "target_path": "docs/x/index.md"},
        {"id": "C1", "title": "Child", "parent_id": "P",
         "is_container": False, "target_path": "docs/x/c.md"},
    ]
    report = NormalizationReport()
    # Simulate the macro having been captured already
    report.child_index_macros.append(
        {"position": 0, "kind": "children", "depth": None,
         "sort": None, "excerpt": None, "root": None, "style": None,
         "raw_params": {}}
    )
    new_md, synth, _ = _maybe_synthesize_stub_container(
        md,
        page_id="P",
        target_path=Path("/repo/docs/x/index.md"),
        manifest_pages=pages,
        repo_root=Path("/repo"),
        report=report,
    )
    assert synth is False
    assert new_md == md


# ---- Phase C — jira macro ----


def test_c_jira_macro_emits_sentinel_and_captures_jql() -> None:
    adf = {"type": "doc", "content": [{
        "type": "extension",
        "attrs": {
            "extensionKey": "jira",
            "parameters": {"macroParams": {
                "jqlQuery": {"value": "project = SEC AND status = Open"},
                "count": {"value": "25"},
            }},
        },
    }]}
    report = NormalizationReport()
    md = adf_to_markdown(adf, report=report)
    assert "<!-- AUTO:JIRA-LIST source=jira jql=" in md, md
    assert "<!-- /AUTO:JIRA-LIST position=0 -->" in md, md
    rec = report.jira_macros[0]
    assert rec["jql"] == "project = SEC AND status = Open"
    assert rec["count"] == "25"


def test_c_jira_renderer_graceful_degrades_on_auth_failure() -> None:
    from actions.adopt_helper import _expand_jira_macros

    md = (
        "Before\n\n"
        "<!-- AUTO:JIRA-LIST source=jira jql=project%3DX position=0 -->\n"
        "<!-- /AUTO:JIRA-LIST position=0 -->\n\n"
        "After\n"
    )
    report = NormalizationReport()
    report.jira_macros.append({
        "position": 0, "jql": "project=X",
        "columns": None, "count": None, "server_id": None,
        "max_issues": None, "raw_params": {},
    })
    # No cookies available → graceful-degrade comment expected. We don't
    # mock urllib here; we monkey-patch attachments.extract_confluence_cookies
    # to raise. If web-control isn't available the import fails the same
    # way and we still fall through.
    import lib.attachments as attachments_mod  # type: ignore
    orig = attachments_mod.extract_confluence_cookies
    try:
        attachments_mod.extract_confluence_cookies = (
            lambda *a, **kw: (_ for _ in ()).throw(
                RuntimeError("no cookies")
            )
        )
        new_md, warnings = _expand_jira_macros(
            md, "https://example.atlassian.net", report
        )
    finally:
        attachments_mod.extract_confluence_cookies = orig
    assert "jira-list render deferred" in new_md, new_md
    assert any("cookie bridge failed" in w for w in warnings), warnings


# ---- Phase D — underline ----


def test_d_underline_adf_to_markdown() -> None:
    adf = {"type": "doc", "content": [{
        "type": "paragraph",
        "content": [{
            "type": "text",
            "text": "important",
            "marks": [{"type": "underline"}],
        }],
    }]}
    md = adf_to_markdown(adf)
    assert "<u>important</u>" in md, md


def test_d_underline_markdown_to_adf_roundtrip() -> None:
    sys.path.insert(0, str(SKILL_ROOT / "actions"))
    from publish_helper import _md_to_adf  # type: ignore

    md = "Some <u>important</u> phrase.\n"
    adf = _md_to_adf(md)
    found = False

    def _walk(n: dict) -> None:
        nonlocal found
        if isinstance(n, dict):
            if n.get("type") == "text":
                marks = n.get("marks") or []
                if any(m.get("type") == "underline" for m in marks):
                    found = True
            for c in n.get("content") or []:
                _walk(c)

    _walk(adf)
    assert found, json.dumps(adf, indent=2)


# ---- Phase E — sentinel-aware diff ----


def test_e_strip_auto_regions_removes_child_index() -> None:
    md = (
        "# Title\n\nIntro paragraph.\n\n"
        "<!-- AUTO:CHILD-INDEX source=children position=0 -->\n"
        "- [Child A](a.md)\n- [Child B](b.md)\n"
        "<!-- /AUTO:CHILD-INDEX position=0 -->\n\n"
        "Trailing content.\n"
    )
    out = strip_auto_regions(md)
    assert "Child A" not in out
    assert "AUTO:CHILD-INDEX" not in out
    assert "# Title" in out
    assert "Intro paragraph." in out
    assert "Trailing content." in out


def test_e_strip_handles_legacy_solo_confluence_side() -> None:
    md = "# H\n\n<!-- confluence-side: toc -->\n\nBody.\n"
    out = strip_auto_regions(md)
    assert "<!-- confluence-side: toc -->" not in out
    assert "# H" in out
    assert "Body." in out


def test_e_strip_handles_paired_attachments_zone() -> None:
    md = (
        "Before\n\n"
        "<!-- confluence-side: attachments labels=actual position=0 -->\n"
        "| File | Size |\n| --- | --- |\n| a.pdf | 1KB |\n"
        "<!-- /confluence-side: attachments position=0 -->\n\n"
        "After\n"
    )
    out = strip_auto_regions(md)
    assert "a.pdf" not in out
    assert "Before" in out
    assert "After" in out


def test_e_classify_adopt_in_sync_when_only_diff_is_auto_region() -> None:
    """Keystone test: re-adopting an unmodified file MUST NOT trigger a
    conflict just because the AUTO:CHILD-INDEX region was regenerated."""
    # Local file body (what the prior adopt wrote — has rendered TOC):
    local_md = (
        "# Title\n\n"
        "<!-- AUTO:CHILD-INDEX source=children position=0 -->\n"
        "- [Old child A](a.md)\n- [Old child B](b.md)\n"
        "<!-- /AUTO:CHILD-INDEX position=0 -->\n"
    )
    # New `their_md` (what normalize produced this run — empty AUTO):
    their_md = (
        "# Title\n\n"
        "<!-- AUTO:CHILD-INDEX source=children position=0 -->\n"
        "<!-- /AUTO:CHILD-INDEX position=0 -->\n"
    )
    decision = classify_adopt(
        Path("/tmp/fake.md"),
        page_id="P1",
        their_md=their_md,
        read_snapshot=lambda pid, ver: None,
        read_local_body=lambda p: local_md,
        read_local_anc_version=lambda p: 1,
    )
    assert decision.action == "in_sync", (
        f"expected in_sync, got {decision.action}: {decision.reason}"
    )


def test_e_classify_adopt_conflict_when_real_content_differs() -> None:
    """Verify drift detection still fires for non-AUTO content changes."""
    local_md = (
        "# Title\n\nLocal edit here.\n\n"
        "<!-- AUTO:CHILD-INDEX source=children position=0 -->\n"
        "<!-- /AUTO:CHILD-INDEX position=0 -->\n"
    )
    their_md = (
        "# Title\n\nThey edited here.\n\n"
        "<!-- AUTO:CHILD-INDEX source=children position=0 -->\n"
        "<!-- /AUTO:CHILD-INDEX position=0 -->\n"
    )
    snapshot = (
        "# Title\n\nOriginal content.\n\n"
        "<!-- AUTO:CHILD-INDEX source=children position=0 -->\n"
        "<!-- /AUTO:CHILD-INDEX position=0 -->\n"
    )
    decision = classify_adopt(
        Path("/tmp/fake.md"),
        page_id="P1",
        their_md=their_md,
        read_snapshot=lambda pid, ver: snapshot,
        read_local_body=lambda p: local_md,
        read_local_anc_version=lambda p: 1,
    )
    assert decision.action == "conflict", (
        f"expected conflict, got {decision.action}"
    )


# ---- Phase F — publish-side strip ----


def test_f_publish_side_emits_extension_node_for_child_index() -> None:
    sys.path.insert(0, str(SKILL_ROOT / "actions"))
    from publish_helper import _md_to_adf  # type: ignore

    md = (
        "# Title\n\n"
        "<!-- AUTO:CHILD-INDEX source=children depth=3 position=0 -->\n"
        "- [A](a.md)\n- [B](b.md)\n"
        "<!-- /AUTO:CHILD-INDEX position=0 -->\n"
    )
    adf = _md_to_adf(md)
    # Expect a single extension node with extensionKey=children
    found = None
    for node in adf.get("content") or []:
        if node.get("type") == "extension":
            attrs = node.get("attrs") or {}
            if attrs.get("extensionKey") == "children":
                found = node
                break
    assert found is not None, json.dumps(adf, indent=2)
    params = (found["attrs"].get("parameters") or {}).get("macroParams", {})
    # depth was on the sentinel, should be reconstructed
    assert "depth" in params, params
    assert params["depth"]["value"] == "3"


def test_f_publish_side_drops_stub_container_block() -> None:
    sys.path.insert(0, str(SKILL_ROOT / "actions"))
    from publish_helper import _md_to_adf  # type: ignore

    md = (
        "# Title\n\nSome content.\n\n"
        "## Child pages\n\n"
        "<!-- AUTO:CHILD-INDEX source=stub-container position=0 -->\n"
        "- [A](a.md)\n"
        "<!-- /AUTO:CHILD-INDEX position=0 -->\n"
    )
    adf = _md_to_adf(md)
    # No `extension` node should be emitted — stub-container has no source macro.
    for node in adf.get("content") or []:
        if node.get("type") == "extension":
            assert (node.get("attrs") or {}).get("extensionKey") not in (
                "children", "pagetree", "stub-container"
            ), json.dumps(adf, indent=2)


def test_f_publish_side_emits_jira_extension_with_jql() -> None:
    sys.path.insert(0, str(SKILL_ROOT / "actions"))
    from publish_helper import _md_to_adf  # type: ignore

    md = (
        "<!-- AUTO:JIRA-LIST source=jira jql=project%3DSEC%20AND%20status%3DOpen position=0 -->\n"
        "| Key | Summary | Status | Updated |\n"
        "| --- | --- | --- | --- |\n"
        "| [SEC-1](http://x/browse/SEC-1) | foo | Open | now |\n"
        "<!-- /AUTO:JIRA-LIST position=0 -->\n"
    )
    adf = _md_to_adf(md)
    found = None
    for node in adf.get("content") or []:
        if node.get("type") == "extension":
            attrs = node.get("attrs") or {}
            if attrs.get("extensionKey") == "jira":
                found = node
                break
    assert found is not None, json.dumps(adf, indent=2)
    params = (found["attrs"].get("parameters") or {}).get("macroParams", {})
    assert "jqlQuery" in params, params
    assert params["jqlQuery"]["value"] == "project=SEC AND status=Open"


# ---- Driver ----


TESTS = [
    test_a_children_macro_emits_sentinel_and_captures_params,
    test_a_pagetree_macro_emits_sentinel,
    test_a_renderer_produces_correct_relative_paths,
    test_a_renderer_relpath_two_levels_deep,
    test_b_stub_synthesis_when_container_has_no_macro,
    test_b_no_stub_synthesis_when_macro_already_in_body,
    test_c_jira_macro_emits_sentinel_and_captures_jql,
    test_c_jira_renderer_graceful_degrades_on_auth_failure,
    test_d_underline_adf_to_markdown,
    test_d_underline_markdown_to_adf_roundtrip,
    test_e_strip_auto_regions_removes_child_index,
    test_e_strip_handles_legacy_solo_confluence_side,
    test_e_strip_handles_paired_attachments_zone,
    test_e_classify_adopt_in_sync_when_only_diff_is_auto_region,
    test_e_classify_adopt_conflict_when_real_content_differs,
    test_f_publish_side_emits_extension_node_for_child_index,
    test_f_publish_side_drops_stub_container_block,
    test_f_publish_side_emits_jira_extension_with_jql,
]


def main() -> int:
    failed = 0
    for t in TESTS:
        try:
            t()
            print(f"PASS  {t.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL  {t.__name__}: {e}")
        except Exception as e:  # noqa: BLE001
            import traceback
            failed += 1
            print(f"ERROR {t.__name__}: {type(e).__name__}: {e}")
            traceback.print_exc()
    print()
    print(f"{len(TESTS) - failed}/{len(TESTS)} passed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
