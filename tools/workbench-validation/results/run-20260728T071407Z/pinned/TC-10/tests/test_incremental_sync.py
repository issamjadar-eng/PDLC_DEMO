"""Tests for task 130 — incremental sync (adopt-direction drift
detection + adopt-tree refresh categorization).

Covers (10 cases):

  Pure classify_adopt:
    1. target absent           -> fresh
    2. target present, in_sync -> in_sync (no-op)
    3. target present, only-theirs (local matches snapshot, conf changed)
    4. target present, only-yours (local diverges, conf unchanged)
    5. target present, conflict (both sides changed)
    6. snapshot missing fallback -> only_theirs

  adopt_helper.cmd_write:
    7. --force overrides drift detection (writes regardless)

  adopt-tree refresh categorization:
    8. empty manifest delta -> all in_sync
    9. mix of new/removed/upstream-changed/predicted-conflict
   10. snapshot integrity — only_theirs path advances snapshot;
       conflict path does NOT advance snapshot

Offline only. Run with:

    python3 .claude/skills/change-control/tests/test_incremental_sync.py
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
ACTIONS_DIR = SKILL_ROOT / "actions"
sys.path.insert(0, str(SKILL_ROOT))
sys.path.insert(0, str(ACTIONS_DIR))

from lib.adopt_sync import (  # noqa: E402
    AdoptSyncDecision,
    classify_adopt,
    conflict_paths,
    write_conflict_files,
)
from lib.manifest import (  # noqa: E402
    Manifest,
    ManifestPage,
)
from lib.snapshot import write_snapshot, read_snapshot  # noqa: E402

import adopt_tree  # noqa: E402


# ---- Test harness ----


PASSED = 0
FAILED = 0


def check(label: str, cond: bool, detail: str = "") -> None:
    global PASSED, FAILED
    if cond:
        print(f"PASS  {label}")
        PASSED += 1
    else:
        print(f"FAIL  {label}  {detail}")
        FAILED += 1


# ---- 1-6: classify_adopt ----


def test_classify_fresh() -> None:
    decision = classify_adopt(
        Path("/nonexistent/foo.md"),
        "p1",
        "their body",
        read_snapshot=lambda pid, ver: None,
        read_local_body=lambda p: None,
        read_local_anc_version=lambda p: None,
    )
    check(
        "test_classify_fresh",
        decision.action == "fresh",
        detail=f"got action={decision.action}",
    )


def test_classify_in_sync() -> None:
    decision = classify_adopt(
        Path("/x.md"),
        "p1",
        "same body",
        read_snapshot=lambda pid, ver: "anc",
        read_local_body=lambda p: "same body",
        read_local_anc_version=lambda p: 3,
    )
    check(
        "test_classify_in_sync",
        decision.action == "in_sync",
        detail=f"got action={decision.action}",
    )


def test_classify_only_theirs() -> None:
    decision = classify_adopt(
        Path("/x.md"),
        "p1",
        "their new body",
        read_snapshot=lambda pid, ver: "anc body",
        read_local_body=lambda p: "anc body",  # local == snapshot
        read_local_anc_version=lambda p: 3,
    )
    check(
        "test_classify_only_theirs",
        decision.action == "only_theirs",
        detail=f"got action={decision.action}",
    )


def test_classify_only_yours() -> None:
    decision = classify_adopt(
        Path("/x.md"),
        "p1",
        "anc body",  # their == snapshot
        read_snapshot=lambda pid, ver: "anc body",
        read_local_body=lambda p: "locally-edited body",
        read_local_anc_version=lambda p: 3,
    )
    check(
        "test_classify_only_yours",
        decision.action == "only_yours",
        detail=f"got action={decision.action}",
    )


def test_classify_conflict() -> None:
    decision = classify_adopt(
        Path("/x.md"),
        "p1",
        "their new body",
        read_snapshot=lambda pid, ver: "anc body",
        read_local_body=lambda p: "locally-edited body",
        read_local_anc_version=lambda p: 3,
    )
    check(
        "test_classify_conflict",
        decision.action == "conflict",
        detail=f"got action={decision.action}",
    )


def test_classify_missing_snapshot_fallback() -> None:
    """No snapshot => only_theirs (best-effort, can't prove local edit)."""
    decision = classify_adopt(
        Path("/x.md"),
        "p1",
        "their body",
        read_snapshot=lambda pid, ver: None,  # missing!
        read_local_body=lambda p: "local body",
        read_local_anc_version=lambda p: 3,
    )
    check(
        "test_classify_missing_snapshot_fallback",
        decision.action == "only_theirs",
        detail=f"got action={decision.action}; reason={decision.reason}",
    )


# ---- 7: --force flag short-circuits drift detection ----


def _mk_args(**kwargs):
    from types import SimpleNamespace
    defaults = dict(
        base_url="https://x.atlassian.net",
        space_key="X",
        parent_page_id="",
        page_path="",
        adopted_at="2026-04-29",
        download_images=False,
        on_conflict="prompt",
        force=False,
    )
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def test_force_flag_overrides_drift() -> None:
    """When `args.force = True`, cmd_write skips classify_adopt entirely."""
    import adopt_helper

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        target = tmp / "doc.md"
        cache_root = tmp / ".cc"

        # Pre-existing local file with edits
        from lib.frontmatter import write as write_fm
        write_fm(
            target,
            {
                "title": "T",
                "state": "published",
                "confluence": {
                    "page_id": "p1",
                    "space_key": "X",
                    "adopted_from_version": 1,
                    "last_published_version": 1,
                },
            },
            "locally-edited body that should be clobbered\n",
        )
        # Snapshot of v1 differs from local, so without --force we'd
        # classify as only_yours/conflict.
        write_snapshot("p1", 1, "snapshot body\n", cache_root=cache_root)

        # Simulated MCP raw response with version=2
        raw = {
            "id": "p1",
            "title": "T",
            "version": {"number": 2},
            "body": {"type": "doc", "content": []},
        }

        args = _mk_args(target=str(target), cache_root=str(cache_root), force=True)
        rc = adopt_helper.cmd_write(args, raw)
        check(
            "test_force_flag_overrides_drift_returns_zero",
            rc == 0,
            detail=f"got rc={rc}",
        )
        # File should now reflect v2 (snapshot rewritten under cache_root)
        snap_after = read_snapshot("p1", 2, cache_root=cache_root)
        check(
            "test_force_flag_overrides_drift_writes_snapshot",
            snap_after is not None,
            detail="snapshot at v2 should exist after --force write",
        )


# ---- 8-10: adopt-tree refresh categorization ----


def _mk_old_manifest(pages_data: list[tuple[str, str, int, str]]) -> Manifest:
    """`pages_data` is list of (page_id, title, version, target_path)."""
    return Manifest(
        manifest_version=1,
        tool_version="0.9.0",
        cloud_id="cid",
        space_key="X",
        base_url="https://x.atlassian.net",
        root_page_id="root",
        pulled_at="2026-04-29",
        pages=[
            ManifestPage(
                id=pid,
                title=title,
                parent_id="root",
                depth=1,
                child_count=0,
                is_container=False,
                target_path=tp,
                confluence_version=ver,
                imported_at="2026-04-29",
            )
            for (pid, title, ver, tp) in pages_data
        ],
    )


def test_refresh_empty_delta_all_in_sync() -> None:
    """Manifest matches discovered pages; all snapshots == local => all in_sync."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        cache_root = tmp / ".cc"

        # Three local files, three snapshots, all matching.
        from lib.frontmatter import write as write_fm
        for pid in ("a", "b", "c"):
            target = tmp / f"{pid}.md"
            write_fm(
                target,
                {"confluence": {"page_id": pid, "adopted_from_version": 1}},
                f"body-{pid}\n",
            )
            write_snapshot(pid, 1, f"body-{pid}\n", cache_root=cache_root)

        old = _mk_old_manifest([
            ("a", "A", 1, str(tmp / "a.md")),
            ("b", "B", 1, str(tmp / "b.md")),
            ("c", "C", 1, str(tmp / "c.md")),
        ])
        new_pages = [
            {"id": pid, "title": pid.upper(), "version": {"number": 1}, "parentId": "root"}
            for pid in ("a", "b", "c")
        ]
        target_paths = {pid: tmp / f"{pid}.md" for pid in ("a", "b", "c")}

        plan = adopt_tree.categorize_refresh(
            old, new_pages, target_paths, cache_root=str(cache_root)
        )
        check(
            "test_refresh_empty_delta_all_in_sync",
            len(plan.in_sync) == 3
            and len(plan.upstream_changed) == 0
            and len(plan.added) == 0
            and len(plan.removed) == 0
            and len(plan.predicted_conflict) == 0
            and len(plan.only_yours_pending) == 0,
            detail=(
                f"in_sync={len(plan.in_sync)} upstream_changed={len(plan.upstream_changed)} "
                f"added={len(plan.added)} removed={len(plan.removed)} "
                f"conflict={len(plan.predicted_conflict)}"
            ),
        )


def test_refresh_mixed_categorization() -> None:
    """Add/remove/upstream-changed/predicted-conflict in one pass."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        cache_root = tmp / ".cc"
        from lib.frontmatter import write as write_fm

        # Page 'unchanged' - in both, version unchanged, local==snapshot
        write_fm(tmp / "unchanged.md", {}, "u\n")
        write_snapshot("unchanged", 1, "u\n", cache_root=cache_root)

        # Page 'only_yours_pending' - in both, version unchanged, local edited
        write_fm(tmp / "yours.md", {}, "edited locally\n")
        write_snapshot("yours", 1, "original\n", cache_root=cache_root)

        # Page 'upstream_changed' - in both, version 1->2, local==snapshot
        write_fm(tmp / "upstream.md", {}, "ups\n")
        write_snapshot("upstream", 1, "ups\n", cache_root=cache_root)

        # Page 'predicted_conflict' - in both, version 1->2, local diverges
        write_fm(tmp / "conflict.md", {}, "edited\n")
        write_snapshot("conflict", 1, "original\n", cache_root=cache_root)

        # Page 'removed' - in old, missing from new
        write_fm(tmp / "removed.md", {}, "r\n")
        write_snapshot("removed", 1, "r\n", cache_root=cache_root)

        old = _mk_old_manifest([
            ("unchanged", "U", 1, str(tmp / "unchanged.md")),
            ("yours", "Y", 1, str(tmp / "yours.md")),
            ("upstream", "Up", 1, str(tmp / "upstream.md")),
            ("conflict", "C", 1, str(tmp / "conflict.md")),
            ("removed", "R", 1, str(tmp / "removed.md")),
        ])

        # Discovered new pages - 'removed' missing, 'added' new, two version bumps
        new_pages = [
            {"id": "unchanged", "title": "U", "version": {"number": 1}, "parentId": "root"},
            {"id": "yours", "title": "Y", "version": {"number": 1}, "parentId": "root"},
            {"id": "upstream", "title": "Up", "version": {"number": 2}, "parentId": "root"},
            {"id": "conflict", "title": "C", "version": {"number": 2}, "parentId": "root"},
            {"id": "added", "title": "Added", "version": {"number": 1}, "parentId": "root"},
        ]
        target_paths = {
            "unchanged": tmp / "unchanged.md",
            "yours": tmp / "yours.md",
            "upstream": tmp / "upstream.md",
            "conflict": tmp / "conflict.md",
            "added": tmp / "added.md",
        }

        plan = adopt_tree.categorize_refresh(
            old, new_pages, target_paths, cache_root=str(cache_root)
        )
        ok = (
            len(plan.in_sync) == 1
            and len(plan.only_yours_pending) == 1
            and len(plan.upstream_changed) == 1
            and len(plan.predicted_conflict) == 1
            and len(plan.added) == 1
            and len(plan.removed) == 1
        )
        check(
            "test_refresh_mixed_categorization",
            ok,
            detail=(
                f"in_sync={[c.page_id for c in plan.in_sync]} "
                f"only_yours={[c.page_id for c in plan.only_yours_pending]} "
                f"upstream={[c.page_id for c in plan.upstream_changed]} "
                f"conflict={[c.page_id for c in plan.predicted_conflict]} "
                f"added={[c.page_id for c in plan.added]} "
                f"removed={[c.page_id for c in plan.removed]}"
            ),
        )


def test_refresh_dry_run_makes_no_io() -> None:
    """Pure categorization makes no filesystem writes — verified by
    re-reading inputs after a categorize call. (categorize_refresh is
    pure; the I/O writes happen in run() only when --dry-run is False.)
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        cache_root = tmp / ".cc"
        from lib.frontmatter import write as write_fm
        write_fm(tmp / "a.md", {}, "a\n")
        write_snapshot("a", 1, "a\n", cache_root=cache_root)
        old = _mk_old_manifest([("a", "A", 1, str(tmp / "a.md"))])
        new_pages = [{"id": "a", "title": "A", "version": {"number": 1}, "parentId": "root"}]
        before = (tmp / "a.md").read_text()
        snap_before = read_snapshot("a", 1, cache_root=cache_root)
        _ = adopt_tree.categorize_refresh(
            old, new_pages, {"a": tmp / "a.md"}, cache_root=str(cache_root)
        )
        after = (tmp / "a.md").read_text()
        snap_after = read_snapshot("a", 1, cache_root=cache_root)
        check(
            "test_refresh_dry_run_makes_no_io",
            before == after and snap_before == snap_after,
            detail="categorize_refresh must not modify any file",
        )


def test_snapshot_integrity_only_theirs_advances_conflict_does_not() -> None:
    """When cmd_write classifies as only_theirs, snapshot v_new exists.
    When it classifies as conflict (default prompt), v_new does NOT exist."""
    import adopt_helper

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        cache_root = tmp / ".cc"
        target = tmp / "doc.md"

        from lib.frontmatter import write as write_fm

        # Setup: local matches snapshot at v1; their (incoming) is v2 with
        # different body => should classify as only_theirs and write v2.
        write_fm(
            target,
            {
                "title": "T",
                "state": "published",
                "confluence": {
                    "page_id": "p1",
                    "space_key": "X",
                    "adopted_from_version": 1,
                    "last_published_version": 1,
                },
            },
            "shared body\n",
        )
        write_snapshot("p1", 1, "shared body\n", cache_root=cache_root)

        raw_only_theirs = {
            "id": "p1",
            "title": "T",
            "version": {"number": 2},
            "body": {
                "type": "doc",
                "content": [{
                    "type": "paragraph",
                    "content": [{"type": "text", "text": "their new body"}],
                }],
            },
        }

        args = _mk_args(target=str(target), cache_root=str(cache_root))
        rc = adopt_helper.cmd_write(args, raw_only_theirs)
        snap_v2 = read_snapshot("p1", 2, cache_root=cache_root)
        check(
            "test_snapshot_integrity_only_theirs_advances",
            rc == 0 and snap_v2 is not None,
            detail=f"rc={rc}; snap@v2={'exists' if snap_v2 else 'missing'}",
        )

        # Now create a CONFLICT scenario — both sides changed since v_anc.
        # Replace local file with a different body, snapshot still at v1
        # with original "shared body", their_md is something else again.
        target2 = tmp / "doc2.md"
        write_fm(
            target2,
            {
                "title": "T2",
                "state": "published",
                "confluence": {
                    "page_id": "p2",
                    "space_key": "X",
                    "adopted_from_version": 1,
                    "last_published_version": 1,
                },
            },
            "locally-edited body\n",
        )
        write_snapshot("p2", 1, "original anchor\n", cache_root=cache_root)

        raw_conflict = {
            "id": "p2",
            "title": "T2",
            "version": {"number": 2},
            "body": {
                "type": "doc",
                "content": [{
                    "type": "paragraph",
                    "content": [{"type": "text", "text": "their changed body"}],
                }],
            },
        }

        args2 = _mk_args(target=str(target2), cache_root=str(cache_root))
        rc2 = adopt_helper.cmd_write(args2, raw_conflict)
        snap_p2_v2 = read_snapshot("p2", 2, cache_root=cache_root)
        # On conflict, the helper writes side-by-side files and exits 3.
        # Snapshot at v_new must NOT have been advanced.
        their_path, diff_path = conflict_paths(target2)
        check(
            "test_snapshot_integrity_conflict_does_not_advance",
            rc2 == 3 and snap_p2_v2 is None
            and their_path.is_file() and diff_path.is_file(),
            detail=(
                f"rc={rc2}; snap@v2={'exists' if snap_p2_v2 else 'missing'}; "
                f"side-by-side files={'present' if their_path.is_file() else 'missing'}"
            ),
        )


# ---- Run ----


def main() -> int:
    test_classify_fresh()
    test_classify_in_sync()
    test_classify_only_theirs()
    test_classify_only_yours()
    test_classify_conflict()
    test_classify_missing_snapshot_fallback()
    test_force_flag_overrides_drift()
    test_refresh_empty_delta_all_in_sync()
    test_refresh_mixed_categorization()
    test_refresh_dry_run_makes_no_io()
    test_snapshot_integrity_only_theirs_advances_conflict_does_not()
    print()
    print(f"{PASSED}/{PASSED + FAILED} passed")
    return 0 if FAILED == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
