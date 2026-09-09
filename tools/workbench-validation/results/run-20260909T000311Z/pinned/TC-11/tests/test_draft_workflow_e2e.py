"""End-to-end integration tests for the B6 Create Draft workflow (task 175).

Exercises the full lifecycle: bootstrap session → outline-stub →
mark-approved → synthesize → save (git mv + tracker md update + ff-merge)
and the cancel path.

Self-contained: builds a temp git repo with a minimal tracker md + tasks
folder; uses stdlib unittest. Skips when git is unavailable.

Run:
    uv run --project tools/project-console python -m unittest \\
        .claude/skills/project-console/tests/test_draft_workflow_e2e.py
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


def _run(args, cwd):
    return subprocess.run(args, cwd=str(cwd), capture_output=True, text=True, timeout=30)


_REPO_ROOT = Path(__file__).resolve().parents[4]
_CONSOLE_PKG = _REPO_ROOT / ".claude" / "skills" / "project-console"
sys.path.insert(0, str(_CONSOLE_PKG))


SAMPLE_OUTLINE = {
    "description": "Q-Sub cover letter introducing the device + classification posture.",
    "title": "Q-Sub Cover Letter",
    "source_materials": [
        {"path": "docs/external/fda-guidance/q-submission-program.md", "rationale": "Defines Q-Sub purpose.", "found": True},
    ],
    "main_topics": [
        {"topic": "Purpose of the Q-Sub", "source_ids": [1]},
    ],
    "regulatory_anchors": {
        "layer1": ["docs/external/fda-guidance/q-submission-program.md"],
        "layer2": [],
    },
    "target": {
        "path": "docs/project/_confluence/suite/qsub/q-sub-cover-letter.md",
        "rationale": "QSub package files live under _confluence/<system-dhf>/qsub/.",
        "exists": False,
        "derived_filename": "q-sub-cover-letter.md",
    },
    "qms_template": {
        "found": False,
        "path": None,
        "governing_sop": None,
        "search_paths_consulted": ["docs/internal/templates/"],
    },
    "open_questions": [],
    "grounding_consulted": {"found": [], "searched_but_missing": [], "on_demand_hints": []},
}

SAMPLE_BODY = """## Purpose

The Q-Sub program enables sponsors to obtain pre-submission feedback [1] on
significant device decisions, with a 70-day target turnaround [2].

The proposed indications target adults aged 18-65 [VERIFY: confirm age range
against latest predicate IFU; assumes consistency with K230045].

## References

- FDA Q-Submission Program guidance (Sept 2023).

[1]: docs/external/fda-guidance/q-submission-program.md#purpose
[2]: docs/external/fda-guidance/q-submission-program.md#timelines
"""


@unittest.skipUnless(_git_available(), "git not on PATH")
class TestDraftWorkflowE2E(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = Path(tempfile.mkdtemp(prefix="draft-e2e-"))
        self.repo = self.tmpdir / "repo"
        self.repo.mkdir()
        _run(["git", "init", "-b", "main"], cwd=self.repo)
        _run(["git", "config", "user.email", "test@example.com"], cwd=self.repo)
        _run(["git", "config", "user.name", "Test User"], cwd=self.repo)
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
        tracker_dir = self.repo / "docs/project/submissions"
        tracker_dir.mkdir(parents=True)
        (tracker_dir / "submission-tracker.md").write_text(
            "# Tracker\n\n"
            "## Phase: QSub\n\n"
            '| # | Deliverable | Scope | Phase | REF | Effort | Status | Path |\n'
            "|---|---|---|---|---|---|---|---|\n"
            '| Q4 | Q-Sub cover letter | Suite | QSub | FDA Q-Sub Guidance | Low | **Not Started** | <button class="tracker-action-btn" disabled>Create Draft</button> |\n',
            encoding="utf-8",
        )
        _run(["git", "add", "-A"], cwd=self.repo)
        _run(["git", "commit", "-m", "init"], cwd=self.repo)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_full_b6_flow(self) -> None:
        from console.workflows import draft_session as ds
        from console.workflows import draft_writer as dw

        actor_folder = "tester"
        actor_name = "Test User"
        row_id = "Q4"

        # 1. No session yet
        self.assertIsNone(ds.snapshot(self.repo, actor_folder, row_id))

        # 2. Bootstrap session + worktree
        task_id, task_path, wt = ds.resolve_or_create(
            self.repo, actor_folder, actor_name, row_id
        )
        self.assertTrue(task_path.is_file())
        self.assertTrue((wt / ".git").exists())
        self.assertTrue((wt / "_drafting").is_dir())

        sess = ds.snapshot(self.repo, actor_folder, row_id)
        self.assertIsNotNone(sess)
        self.assertEqual(sess.task_id, task_id)
        self.assertFalse(sess.has_outline)

        # 3. write_outline_stub creates _drafting/Q4-*.md with frontmatter
        result = dw.write_outline_stub(
            wt, row_id, SAMPLE_OUTLINE,
            agent_name="program-manager",
            actor=actor_name,
            branch=sess.branch,
            session_task_rel=str(task_path.relative_to(self.repo)),
        )
        self.assertTrue(result["created"])
        staging = wt / result["staging_file"]
        self.assertTrue(staging.is_file())
        text = staging.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\n"))
        self.assertIn("origin: local-draft", text)
        self.assertIn(f"tracker_row_id: {row_id}", text)
        self.assertIn("page_id: null", text)
        self.assertIn("strip_on_publish: true", text)
        self.assertIn("[VERIFY: No QMS template located]", text)  # banner
        # Re-run is idempotent (merged result)
        result2 = dw.write_outline_stub(
            wt, row_id, SAMPLE_OUTLINE,
            agent_name="program-manager",
            actor=actor_name,
            branch=sess.branch,
            session_task_rel=str(task_path.relative_to(self.repo)),
        )
        self.assertFalse(result2["created"])
        self.assertTrue(result2["merged"])

        # 4. mark_outline_approved
        ap = dw.mark_outline_approved(wt, row_id)
        self.assertTrue(ap["outline_approved_at"])
        sess = ds.snapshot(self.repo, actor_folder, row_id)
        self.assertTrue(sess.has_outline)

        # 5. write_synthesis stamps body + counters. The counter matches every
        # `[N]` (inline marks AND `[N]:` footnote-block lines) — both are
        # stripped at publish, so counting both is the right input for the
        # strip transform's report.
        syn = dw.write_synthesis(wt, row_id, SAMPLE_BODY)
        self.assertEqual(syn["counts"]["inline_citations"], 4)
        self.assertEqual(syn["counts"]["verify_markers"], 1)
        self.assertTrue(syn["counts"]["qms_references_section_present"])

        sess = ds.snapshot(self.repo, actor_folder, row_id)
        self.assertTrue(sess.has_synthesis)
        self.assertEqual(sess.target_path, SAMPLE_OUTLINE["target"]["path"])

        # 6. save_to_target — git mv + tracker md update
        save = dw.save_to_target(wt, row_id)
        self.assertTrue(save["moved"])
        self.assertEqual(save["target_path"], SAMPLE_OUTLINE["target"]["path"])
        self.assertTrue(save["tracker_md_updated"])
        # Staging file should no longer exist
        self.assertFalse(staging.is_file())
        # Target file should exist with frontmatter
        target_file = wt / save["target_path"]
        self.assertTrue(target_file.is_file())
        target_text = target_file.read_text(encoding="utf-8")
        self.assertIn("origin: local-draft", target_text)
        self.assertIn("exists: true", target_text)
        # Tracker md updated: status flipped to Drafted, button replaced by link
        wt_md = (wt / "docs/project/submissions/submission-tracker.md").read_text(encoding="utf-8")
        self.assertIn("**Drafted**", wt_md)
        self.assertNotIn('<button class="tracker-action-btn" disabled>', wt_md)
        self.assertIn("q-sub-cover-letter.md", wt_md)

        # 7. commit_and_merge — push fails silently (no remote), merge into main works
        merge = ds.commit_and_merge(
            self.repo, actor_folder, actor_name, row_id, f"draft({row_id}): cover letter",
        )
        self.assertTrue(merge.get("committed"))

        # 8. Post-conditions
        # Main has the new file
        main_target = (self.repo / SAMPLE_OUTLINE["target"]["path"]).read_text(encoding="utf-8")
        self.assertIn("origin: local-draft", main_target)
        # Worktree torn down
        self.assertFalse((wt / ".git").exists())
        # Branch deleted
        branches = _run(["git", "branch", "--list"], cwd=self.repo).stdout
        self.assertNotIn(f"workflow/tracker-draft-{row_id}", branches)
        # Task complete
        task_text = task_path.read_text(encoding="utf-8")
        self.assertIn("**Status**: Complete", task_text)

    def test_cancel_workflow(self) -> None:
        from console.workflows import draft_session as ds
        from console.workflows import draft_writer as dw

        actor_folder = "tester"
        row_id = "Q4"
        task_id, task_path, wt = ds.resolve_or_create(
            self.repo, actor_folder, "Test User", row_id
        )
        dw.write_outline_stub(
            wt, row_id, SAMPLE_OUTLINE,
            agent_name="program-manager",
            actor="Test User",
            branch=ds.worktree_branch(self.repo, row_id),
            session_task_rel=str(task_path.relative_to(self.repo)),
        )

        result = ds.cancel_workflow(self.repo, actor_folder, row_id)
        self.assertEqual(result["status"], "cancelled")
        self.assertFalse((wt / ".git").exists())
        # Main is unchanged
        self.assertFalse((self.repo / SAMPLE_OUTLINE["target"]["path"]).exists())
        # Task abandoned
        self.assertIn("**Status**: Abandoned", task_path.read_text(encoding="utf-8"))

    def test_resumability(self) -> None:
        """Re-clicking Create Draft on a row with an in-progress session
        re-attaches to the existing worktree and task."""
        from console.workflows import draft_session as ds

        actor_folder = "tester"
        row_id = "Q4"
        task_id_a, task_path_a, wt_a = ds.resolve_or_create(
            self.repo, actor_folder, "Test User", row_id
        )
        task_id_b, task_path_b, wt_b = ds.resolve_or_create(
            self.repo, actor_folder, "Test User", row_id
        )
        self.assertEqual(task_id_a, task_id_b)
        self.assertEqual(task_path_a, task_path_b)
        self.assertEqual(str(wt_a), str(wt_b))

    def test_two_rows_concurrent(self) -> None:
        """Two different rows get separate worktrees + tasks."""
        from console.workflows import draft_session as ds

        # Add a second row to the tracker md
        md = self.repo / "docs/project/submissions/submission-tracker.md"
        md.write_text(
            md.read_text(encoding="utf-8")
            + '| Q5 | Device description | Suite | QSub | FDA | Med | **Not Started** | <button class="tracker-action-btn" disabled>Create Draft</button> |\n',
            encoding="utf-8",
        )
        _run(["git", "add", "-A"], cwd=self.repo)
        _run(["git", "commit", "-m", "add Q5"], cwd=self.repo)

        actor_folder = "tester"
        ta, _, wta = ds.resolve_or_create(self.repo, actor_folder, "Test User", "Q4")
        tb, _, wtb = ds.resolve_or_create(self.repo, actor_folder, "Test User", "Q5")
        self.assertNotEqual(ta, tb)
        self.assertNotEqual(str(wta), str(wtb))


class TestOutlineSentinelScan(unittest.TestCase):
    def test_finds_latest_block_for_row(self) -> None:
        from console.workflows import draft_writer as dw

        transcript = """User: please propose an outline.

Agent: here is v1:
<!-- B6 OUTLINE START: Q4 v1 -->
First version.
<!-- /B6 OUTLINE END -->

User: refine it.

Agent: revised:
<!-- B6 OUTLINE START: Q4 v2 -->
Second version body here.
<!-- /B6 OUTLINE END -->

Agent (Q5): unrelated outline:
<!-- B6 OUTLINE START: Q5 v1 -->
Q5 body.
<!-- /B6 OUTLINE END -->
"""
        block = dw.find_latest_outline_block(transcript, "Q4")
        self.assertIsNotNone(block)
        self.assertEqual(block["version"], 2)
        self.assertIn("Second version body here.", block["body"])

    def test_returns_none_if_no_match(self) -> None:
        from console.workflows import draft_writer as dw
        self.assertIsNone(dw.find_latest_outline_block("plain transcript", "Q4"))


class TestFrontmatterCounters(unittest.TestCase):
    def test_count_markers(self) -> None:
        from console.workflows.draft_writer import _count_markers
        body = "Foo [1] bar [VERIFY: x] baz [2]\n\n## References\n[1]: a\n[2]: b\n"
        c = _count_markers(body)
        self.assertEqual(c["inline_citations"], 4)  # [1], [2], [1] in footnote, [2] in footnote
        self.assertEqual(c["verify_markers"], 1)
        self.assertTrue(c["qms_references_section_present"])


if __name__ == "__main__":
    unittest.main()
