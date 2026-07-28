"""Plan-tab verification-plan checklist + Quality-tab chip (console 1.57.0).

Covers the sidecar schema-1.4 `verification_plan` contract against a
self-contained fixture repo:

- a question row carrying `verification_plan` renders the Plan-tab checklist
  with all three computed mark states (✓ done / ○ not done / • informational)
  and an evidence line per gate;
- the Quality & audit toptab gains a compact "verification N/M" chip counting
  only computable gates (custom/null excluded from the denominator);
- schema ≤1.3 rows (no `verification_plan` field) degrade cleanly: no chip,
  no checklist section, zero errors.

Run:
    uv run --project tools/project-console python \
        .claude/skills/project-console/tests/test_commercial_vplan.py
"""

from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[4]
_CONSOLE_PKG = _REPO_ROOT / ".claude" / "skills" / "project-console"
sys.path.insert(0, str(_CONSOLE_PKG))

EDITION = "2026-07-27"

# All mark states: done True (machine + agent), done False (machine + agent),
# done None (custom token carried as informational).
VPLAN = [
    {"gate": "claim-lint", "kind": "machine", "note": "zero lint errors every edition",
     "done": True, "evidence": "0 error(s) / 2 warning(s)"},
    {"gate": "pin-freshness", "kind": "machine", "note": "fresh or waived",
     "done": True, "evidence": "2 pin(s) fresh"},
    {"gate": "code-audit", "kind": "machine", "note": "reviewed at pinned bytes",
     "done": False, "evidence": "code unreviewed"},
    {"gate": "adversarial-verify", "kind": "agent", "note": "pins-only re-derivation",
     "done": True, "evidence": "CONFIRMED by verify agent, 2026-07-27"},
    {"gate": "red-team", "kind": "agent", "note": "framing attack",
     "done": False, "evidence": "no red-team record filed on this edition"},
    {"gate": "finance-signoff", "kind": "custom", "note": "quarterly CFO look",
     "done": None,
     "evidence": "custom gate — completion not machine-computed (informational)"},
]


def _question(bq: str, vplan) -> dict:
    row = {
        "id": bq, "question": f"Fixture question {bq}", "category": "fixture",
        "personas": ["commercial"], "cadence": "quarterly", "status": "draft-only",
        "approved_edition": None, "draft_edition": EDITION, "latest_edition": EDITION,
        "editions": [{"edition": EDITION, "status": "draft"}],
        "assumptions": [], "freshness": None, "verdict_headline": None,
        "evidence_class": None,
        "report_path": f"docs/project/commercial/reports/{bq}/{EDITION}/report.md",
        "data_path": f"docs/project/commercial/reports/{bq}/{EDITION}/data.json",
        "explainers": {}, "terms": [], "code": None,
    }
    if vplan is not None:
        row["verification_plan"] = vplan
    return row


class CommercialVplanTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="cm-vplan-"))
        repo = cls.tmp
        (repo / "project.yml").write_text(
            "project:\n  name: Fixture\n"
            "team:\n  active:\n  - name: Ben\n    github: benx\n",
            encoding="utf-8")
        croot = repo / "docs" / "project" / "commercial"
        (croot / ".console").mkdir(parents=True)
        index = {"schema_version": "1.4", "generated": "2026-07-27T10:00:00",
                 "categories": [{"key": "fixture", "name": "Fixture"}],
                 "questions": [_question("BQ-97", VPLAN), _question("BQ-96", None)]}
        (croot / ".console" / "commercial-index.json").write_text(
            json.dumps(index), encoding="utf-8")
        for bq in ("BQ-97", "BQ-96"):
            edir = croot / "reports" / bq / EDITION
            edir.mkdir(parents=True)
            (edir / "edition.yml").write_text(
                f"bq: {bq}\nedition: '{EDITION}'\nstatus: draft\n"
                f"created_at: '2026-07-27T09:00:00'\npins: {{}}\n", encoding="utf-8")
            (edir / "data.json").write_text(
                json.dumps({"series": [], "verdicts": []}), encoding="utf-8")
            (edir / "report.md").write_text("# Fixture report\n\nNo figures.\n",
                                            encoding="utf-8")

        os.environ["CLAUDE_PROJECT_DIR"] = str(repo)
        import console.config as config_mod
        config_mod.get_config.cache_clear()
        for m in [m for m in list(sys.modules) if m == "console.app"]:
            del sys.modules[m]
        from fastapi.testclient import TestClient
        from console.app import app
        cls.client = TestClient(app)  # no context manager: skip lifespan/preflight

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)
        os.environ.pop("CLAUDE_PROJECT_DIR", None)
        import console.config as config_mod
        config_mod.get_config.cache_clear()

    # ---- schema 1.4: checklist + chip render -----------------------------

    def test_checklist_renders_all_mark_states(self):
        r = self.client.get("/commercial/BQ-97")
        self.assertEqual(r.status_code, 200)
        html = r.text
        self.assertIn("Verification plan", html)
        # gates + notes
        for gate in ("claim-lint", "pin-freshness", "code-audit",
                     "adversarial-verify", "red-team", "finance-signoff"):
            self.assertIn(gate, html)
        self.assertIn("zero lint errors every edition", html)
        # evidence lines
        self.assertIn("0 error(s) / 2 warning(s)", html)
        self.assertIn("CONFIRMED by verify agent, 2026-07-27", html)
        self.assertIn("no red-team record filed on this edition", html)
        # three mark states via the mark disc classes
        self.assertIn('cm-vp-mark vx-met', html)    # ✓ done
        self.assertIn('cm-vp-mark vx-risk', html)   # ○ not done
        self.assertIn('cm-vp-mark vx-none', html)   # • informational
        # custom gate flagged
        self.assertIn(">custom</span>", html)
        # never-hand-ticked framing present
        self.assertIn("never hand-ticked", html)

    def test_quality_tab_chip_counts_computable_gates_only(self):
        html = self.client.get("/commercial/BQ-97").text
        # 3 of 5 computable gates done; the custom gate is excluded from N/M
        self.assertIn("verification 3/5", html)
        self.assertIn("3/5 satisfied", html)

    # ---- schema ≤1.3 degradation ----------------------------------------

    def test_schema_13_row_degrades_cleanly(self):
        r = self.client.get("/commercial/BQ-96")
        self.assertEqual(r.status_code, 200)
        html = r.text
        self.assertNotIn("cm-vplan", html)
        self.assertNotIn("verification ", html.split("cm-toptabs")[1].split("</div>")[0]
                         if "cm-toptabs" in html else "")
        self.assertNotIn("/5 satisfied", html)


if __name__ == "__main__":
    unittest.main()
