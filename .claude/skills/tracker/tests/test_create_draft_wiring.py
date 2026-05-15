"""Unit tests for the B6 Create Draft wiring in the tracker skill.

Covers:
  - render.wire_create_draft_button: rewrites disabled buttons to wired
    buttons with data-row-id + data-action; skips ineligible statuses.
  - render.find_draft_stage: detects in-progress drafts in `_drafting/`.
  - build-draft-context.py: emits the per-row YAML/JSON bundle.

Run:
    python3 -m unittest .claude/skills/tracker/tests/test_create_draft_wiring.py
"""

from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

_SKILL_DIR = Path(__file__).resolve().parents[1]


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


render = _load("tracker_render", _SKILL_DIR / "scripts" / "render.py")


class TestWireCreateDraftButton(unittest.TestCase):
    BTN = '<button class="tracker-action-btn" disabled>Create Draft</button>'

    def test_eligible_status_wires_button(self) -> None:
        out = render.wire_create_draft_button(self.BTN, "Q4", "Not Started")
        self.assertIn('data-row-id="Q4"', out)
        self.assertIn('data-action="create-draft"', out)
        self.assertNotIn("disabled", out)

    def test_ineligible_status_passes_through(self) -> None:
        out = render.wire_create_draft_button(self.BTN, "Q4", "Approved")
        self.assertEqual(out, self.BTN)

    def test_no_button_passes_through(self) -> None:
        out = render.wire_create_draft_button("[`cover.md`](cover.md)", "Q4", "Not Started")
        self.assertEqual(out, "[`cover.md`](cover.md)")

    def test_draft_stage_flips_label_and_adds_attr(self) -> None:
        out = render.wire_create_draft_button(self.BTN, "Q4", "Drafting", draft_stage="outline")
        self.assertIn("Edit Draft", out)
        self.assertIn('data-draft-state="outline"', out)
        self.assertIn("draft-stage-badge", out)

    def test_drafting_status_eligible(self) -> None:
        out = render.wire_create_draft_button(self.BTN, "Q4", "Drafting")
        self.assertIn('data-action="create-draft"', out)


class TestFindDraftStage(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="draft-stage-"))

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_no_drafting_dir_returns_none(self) -> None:
        self.assertIsNone(render.find_draft_stage(self.tmp, "Q4"))

    def test_no_match_returns_none(self) -> None:
        (self.tmp / "_drafting").mkdir()
        (self.tmp / "_drafting" / "PA1-foo.md").write_text("body", encoding="utf-8")
        self.assertIsNone(render.find_draft_stage(self.tmp, "Q4"))

    def test_outline_stage_when_no_timestamps(self) -> None:
        (self.tmp / "_drafting").mkdir()
        (self.tmp / "_drafting" / "Q4-cover.md").write_text(
            "---\nstate: draft\nagent:\n  outline_approved_at: null\n  synthesis_completed_at: null\n---\nbody",
            encoding="utf-8",
        )
        self.assertEqual(render.find_draft_stage(self.tmp, "Q4"), "outline")

    def test_drafting_stage(self) -> None:
        (self.tmp / "_drafting").mkdir()
        (self.tmp / "_drafting" / "Q4-cover.md").write_text(
            "---\nagent:\n  outline_approved_at: 2026-05-07T10:00:00Z\n  synthesis_completed_at: null\n---\nbody",
            encoding="utf-8",
        )
        self.assertEqual(render.find_draft_stage(self.tmp, "Q4"), "drafting")

    def test_drafted_stage(self) -> None:
        (self.tmp / "_drafting").mkdir()
        (self.tmp / "_drafting" / "Q4-cover.md").write_text(
            "---\nagent:\n  outline_approved_at: 2026-05-07T10:00:00Z\n  synthesis_completed_at: 2026-05-07T11:00:00Z\n---\nbody",
            encoding="utf-8",
        )
        self.assertEqual(render.find_draft_stage(self.tmp, "Q4"), "drafted")


class TestBuildDraftContextScript(unittest.TestCase):
    """Runs the build-draft-context.py script against the live project (the
    parent dir of this skill). The script is read-only — it is safe to run
    against the project this test ships in."""

    def test_script_emits_bundle_for_existing_row(self) -> None:
        # Find the project root by walking up for CLAUDE.md
        d = _SKILL_DIR
        for _ in range(8):
            if (d / "CLAUDE.md").exists():
                break
            if d.parent == d:
                self.skipTest("could not find project CLAUDE.md")
                return
            d = d.parent
        project_dir = d
        # Pick any row from submission-tracker.md (use Q4 if present)
        tracker_md = project_dir / "docs/project/submissions/submission-tracker.md"
        if not tracker_md.is_file():
            self.skipTest("no submission-tracker.md in this project")
            return
        # Find first row id
        import re
        m = re.search(r"^\|\s*([A-Z][A-Z0-9-]+)\s*\|", tracker_md.read_text(encoding="utf-8"), re.MULTILINE)
        if not m:
            self.skipTest("no rows found in tracker md")
            return
        row_id = m.group(1)
        script = _SKILL_DIR / "scripts" / "build-draft-context.py"
        r = subprocess.run(
            [sys.executable, str(script), "--row", row_id, "--json", "--project-dir", str(project_dir)],
            capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(r.returncode, 0, msg=f"stderr: {r.stderr}")
        bundle = json.loads(r.stdout)
        self.assertEqual(bundle["row"]["id"], row_id)
        self.assertIn("discovery_seed", bundle)
        seed = bundle["discovery_seed"]
        # The seed always carries QMS + external roots
        self.assertEqual(seed["qms_search_roots"], ["docs/internal/sops", "docs/internal/templates"])
        self.assertIn("readme_index_paths", seed)


if __name__ == "__main__":
    unittest.main()
