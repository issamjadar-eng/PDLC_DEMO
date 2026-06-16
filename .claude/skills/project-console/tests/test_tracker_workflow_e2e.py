"""End-to-end integration test for the B4 tracker-status-update workflow
(task ben/154 P7). Exercises the full path: bootstrap session →
3 status changes → snapshot shows pending → commit_and_merge → verify
md committed + task Complete + worktree torn down.

Self-contained: builds a temp git repo with a minimal tracker md + tasks
folder; uses stdlib unittest (no pytest required). Skips when git is
unavailable on PATH.

Run:
    uv run --project tools/project-console python -m unittest \\
        .claude/skills/project-console/tests/test_tracker_workflow_e2e.py
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


def _git_available() -> bool:
    return shutil.which("git") is not None


def _run(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(args, cwd=str(cwd), capture_output=True, text=True, timeout=30)


# Ensure the project-console package is importable.
_REPO_ROOT = Path(__file__).resolve().parents[4]  # project root (…/<project-slug>/)
_CONSOLE_PKG = _REPO_ROOT / ".claude" / "skills" / "project-console"
sys.path.insert(0, str(_CONSOLE_PKG))


@unittest.skipUnless(_git_available(), "git not on PATH")
class TestTrackerStatusWorkflowE2E(unittest.TestCase):
    """End-to-end happy-path: 3 status changes → save → fully cleaned up."""

    def setUp(self) -> None:
        self.tmpdir = Path(tempfile.mkdtemp(prefix="tracker-e2e-"))
        self.repo = self.tmpdir / "repo"
        self.repo.mkdir()
        # Init repo with main as the default branch.
        _run(["git", "init", "-b", "main"], cwd=self.repo)
        _run(["git", "config", "user.email", "test@example.com"], cwd=self.repo)
        _run(["git", "config", "user.name", "Test User"], cwd=self.repo)
        # Minimal tasks folder + index for the actor.
        actor_folder = self.repo / "tasks" / "tester"
        actor_folder.mkdir(parents=True)
        (actor_folder / "000-index.md").write_text(
            "# Tasks\n\n## Active\n\n"
            "| ID | Title | File | Status | Summary | Priority | Created |\n"
            "|----|-------|------|--------|---------|----------|---------|\n\n"
            "## Completed\n\n"
            "| ID | Title | File | Status | Summary | Priority | Created |\n"
            "|----|-------|------|--------|---------|----------|---------|\n",
            encoding="utf-8",
        )
        # Minimal submission tracker md with 3 deliverable rows.
        tracker_dir = self.repo / "docs/project/submissions"
        tracker_dir.mkdir(parents=True)
        (tracker_dir / "submission-tracker.md").write_text(
            "# Tracker\n\n"
            "## Phase: 510k+PCCP\n\n"
            "| # | Deliverable | Scope | Phase | REF | Effort | Status | Path |\n"
            "|---|---|---|---|---|---|---|---|\n"
            "| PA1 | Cover Letter | (submission) | 510k+PCCP | 21 CFR 807.87 | Low | **Not Started** | `cover.md` |\n"
            "| PA2 | 510(k) Summary | (submission) | 510k+PCCP | 21 CFR 807.92 | Med | **Not Started** | `summary.md` |\n"
            "| PA3 | Truthful & Accuracy | (submission) | 510k+PCCP | 21 CFR 807.87(l) | Low | **Not Started** | `truth.md` |\n",
            encoding="utf-8",
        )
        _run(["git", "add", "-A"], cwd=self.repo)
        _run(["git", "commit", "-m", "init"], cwd=self.repo)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_full_b4_flow(self) -> None:
        from console.workflows import tracker_session as ts
        from console.workflows import tracker_writer as tw

        actor_folder = "tester"
        actor_name = "Test User"

        # 1. No session exists yet
        self.assertIsNone(ts.snapshot(self.repo, actor_folder, "status"))

        # 2. resolve_or_create — bootstraps task + worktree
        task_id, task_path, wt = ts.resolve_or_create(
            self.repo, actor_folder, actor_name, "status"
        )
        self.assertTrue(task_path.is_file())
        self.assertTrue((wt / ".git").exists())
        self.assertTrue((wt / ts.TRACKER_MD_REL).is_file())

        # 3. snapshot now returns the session; no diff yet
        sess = ts.snapshot(self.repo, actor_folder, "status")
        self.assertIsNotNone(sess)
        self.assertEqual(sess.task_id, task_id)
        self.assertFalse(sess.has_diff)

        # 4. Three status changes (skip HTML regen — no /tracker render
        #    script in the test repo)
        for row_id, new_status, rationale in [
            ("PA1", "Done", "draft signed off"),
            ("PA2", "In Progress", None),
            ("PA3", "Partial", "needs legal review"),
        ]:
            result = tw.write_status_change(
                wt=wt,
                row_id=row_id,
                new_status=new_status,
                rationale=rationale,
                actor=actor_name,
                task_path=task_path,
                repo_root=self.repo,
            )
            self.assertEqual(result["row_id"], row_id)
            self.assertEqual(result["new_status"], new_status)
            self.assertTrue(result["written"])
            self.assertTrue(result["changelog_appended"])

        # 5. Worktree md now reflects the changes
        wt_md = (wt / ts.TRACKER_MD_REL).read_text(encoding="utf-8")
        self.assertIn("| PA1 | Cover Letter |", wt_md)
        self.assertIn("**Done**", wt_md)
        self.assertIn("**In Progress**", wt_md)
        self.assertIn("**Partial**", wt_md)

        # 6. Pending-changes parser sees all 3
        pending = tw.parse_pending_changes(task_path)
        self.assertEqual(len(pending), 3)
        ids = sorted(p["row_id"] for p in pending)
        self.assertEqual(ids, ["PA1", "PA2", "PA3"])

        # 7. snapshot now shows has_diff (md mutated; task doc lives in
        #    main repo by design — the commit only captures regulated md
        #    changes, the task-doc changelog stays in main)
        sess = ts.snapshot(self.repo, actor_folder, "status")
        self.assertTrue(sess.has_diff)
        self.assertGreaterEqual(len(sess.diff_summary), 1)
        self.assertTrue(any(ts.TRACKER_MD_REL in line for line in sess.diff_summary))

        # 8. commit_and_merge — push step is best-effort and will fail
        #    silently (no remote); merge into main should succeed.
        result = ts.commit_and_merge(
            self.repo, actor_folder, actor_name, "status",
            "tracker status: 3 changes via test harness",
        )
        self.assertTrue(result.get("committed"))
        self.assertIn("commit_sha", result)

        # 9. Verify post-conditions:
        #    a) main has the tracker md changes
        main_md = (self.repo / ts.TRACKER_MD_REL).read_text(encoding="utf-8")
        self.assertIn("**Done**", main_md)
        self.assertIn("**Partial**", main_md)
        #    b) Worktree directory removed
        self.assertFalse((wt / ".git").exists())
        #    c) Branch deleted
        branches = _run(["git", "branch", "--list"], cwd=self.repo).stdout
        self.assertNotIn("workflow/tracker-status", branches)
        #    d) Task doc Status flipped to Complete
        task_text = task_path.read_text(encoding="utf-8")
        self.assertIn("**Status**: Complete", task_text)
        #    e) Index row moved Active → Completed
        idx_text = (self.repo / "tasks" / actor_folder / "000-index.md").read_text(encoding="utf-8")
        active_section = idx_text.split("## Completed")[0]
        completed_section = idx_text.split("## Completed")[1]
        self.assertNotIn(f"| {task_id} |", active_section)
        self.assertIn(f"| {task_id} |", completed_section)

    def test_cancel_workflow(self) -> None:
        """Cancel path: changes discarded, worktree removed, task Abandoned."""
        from console.workflows import tracker_session as ts
        from console.workflows import tracker_writer as tw

        actor_folder = "tester"
        actor_name = "Test User"
        task_id, task_path, wt = ts.resolve_or_create(
            self.repo, actor_folder, actor_name, "status"
        )
        tw.write_status_change(
            wt=wt, row_id="PA1", new_status="Done",
            rationale=None, actor=actor_name,
            task_path=task_path, repo_root=self.repo,
        )
        result = ts.cancel_workflow(self.repo, actor_folder, "status")
        self.assertEqual(result["status"], "cancelled")
        self.assertFalse((wt / ".git").exists())
        # Main md unchanged (cancel doesn't write to main)
        main_md = (self.repo / ts.TRACKER_MD_REL).read_text(encoding="utf-8")
        self.assertIn("PA1 | Cover Letter | (submission) | 510k+PCCP | 21 CFR 807.87 | Low | **Not Started**", main_md)
        # Task flipped to Abandoned
        task_text = task_path.read_text(encoding="utf-8")
        self.assertIn("**Status**: Abandoned", task_text)


if __name__ == "__main__":
    unittest.main()
