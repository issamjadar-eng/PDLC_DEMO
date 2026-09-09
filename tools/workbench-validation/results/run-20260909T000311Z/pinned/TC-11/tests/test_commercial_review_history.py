"""Quality-tab review history + inline dossier rendering (console 1.56.0).

Covers the sidecar schema-1.3 contract end to end against a self-contained
fixture repo:

- per-artifact `review_history` entries render as expandable "Previous review"
  folds with the findings table (id | severity | summary | disposition);
- a repo-relative markdown `detail_ref` renders an inline dossier fold
  (lazy-loaded via GET /commercial/review-detail) for reviews, history entries,
  and verification records;
- /commercial/review-detail resolves paths STRICTLY inside the repo root and
  only serves .md files — traversal / absolute / non-markdown are rejected;
- schema ≤1.2 rows (no `review_history`) degrade cleanly: no history chrome,
  no errors.

Run:
    uv run --project tools/project-console python -m unittest \
        .claude/skills/project-console/tests/test_commercial_review_history.py
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
DOSSIER_REL = "tasks/ben/_work/review-dossier.md"

QUALITY = {
    "bq": "BQ-99", "edition": EDITION, "generated_at": "2026-07-27T10:00:00",
    "lint": {"status": "pass", "errors": [], "warnings": [], "checks": []},
    "references": [], "freshness": [],
    "data_availability": {"have": [], "assumed": [], "missing": []},
    "plan": None,
    "verifications": [
        {"type": "adversarial-verify", "verdict": "CONFIRMED", "by": "verify agent",
         "at": "2026-07-27T10:00:00", "summary": "re-derived headline from pins",
         "detail_ref": DOSSIER_REL},
    ],
}

CODE_13 = {
    "status": "reviewed-current",
    "artifacts": [{
        "path": "bq_modules/bq_99.py", "sha256_12": "aaaaaaaaaaaa", "role": "computation",
        "static_lint": {"status": "pass", "tool": "py_compile", "findings": []},
        "poison_scan": {"status": "pass", "hits": []},
        "determinism": {"status": "pass", "method": "double-run byte-compare"},
        "review": {"verdict": "APPROVED", "by": "AI code reviewer", "date": "2026-07-27",
                   "current": True, "findings": [], "detail_ref": DOSSIER_REL},
        "review_history": [{
            "sha256_12": "e7f42f06e380", "date": "2026-07-27",
            "verdict": "CHANGES-REQUIRED", "by": "AI code reviewer",
            "summary": "headline hardcodes the guardrail verdict",
            "findings": [
                {"id": "F-1", "severity": "high",
                 "summary": "Headline asserts guardrail unconditionally",
                 "disposition": "fix: branch on raw share vs thr"},
                {"id": "F-2", "severity": "low",
                 "summary": "top3_share sums rounded shares",
                 "disposition": "fix: C.pct(sum(top3), total)"},
            ],
            "detail_ref": DOSSIER_REL, "superseded": True,
        }],
    }],
}

# schema ≤1.2 shape: no review_history key anywhere, detail_ref absent
CODE_12 = {
    "status": "reviewed-current",
    "artifacts": [{
        "path": "bq_modules/bq_98.py", "sha256_12": "bbbbbbbbbbbb", "role": "computation",
        "static_lint": {"status": "pass", "tool": "py_compile", "findings": []},
        "poison_scan": {"status": "pass", "hits": []},
        "determinism": {"status": "pass", "method": "double-run byte-compare"},
        "review": {"verdict": "APPROVED", "by": "AI code reviewer", "date": "2026-07-27",
                   "current": True, "findings": [], "detail_ref": None},
    }],
}


def _question(bq: str, code: dict) -> dict:
    return {
        "id": bq, "question": f"Fixture question {bq}", "category": "fixture",
        "personas": ["commercial"], "cadence": "quarterly", "status": "draft-only",
        "approved_edition": None, "draft_edition": EDITION, "latest_edition": EDITION,
        "editions": [{"edition": EDITION, "status": "draft"}],
        "assumptions": [], "freshness": None, "verdict_headline": None,
        "evidence_class": None,
        "report_path": f"docs/project/commercial/reports/{bq}/{EDITION}/report.md",
        "data_path": f"docs/project/commercial/reports/{bq}/{EDITION}/data.json",
        "explainers": {}, "terms": [], "code": code,
    }


class CommercialReviewHistoryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="cm-hist-"))
        repo = cls.tmp
        (repo / "project.yml").write_text(
            "project:\n  name: Fixture\n"
            "team:\n  active:\n  - name: Ben\n    github: benx\n",
            encoding="utf-8")
        croot = repo / "docs" / "project" / "commercial"
        (croot / ".console").mkdir(parents=True)
        index = {"schema_version": "1.3", "generated": "2026-07-27T10:00:00",
                 "categories": [{"key": "fixture", "name": "Fixture"}],
                 "questions": [_question("BQ-99", CODE_13), _question("BQ-98", CODE_12)]}
        (croot / ".console" / "commercial-index.json").write_text(json.dumps(index), encoding="utf-8")
        for bq in ("BQ-99", "BQ-98"):
            edir = croot / "reports" / bq / EDITION
            edir.mkdir(parents=True)
            (edir / "edition.yml").write_text(
                f"bq: {bq}\nedition: '{EDITION}'\nstatus: draft\n"
                f"created_at: '2026-07-27T09:00:00'\npins: {{}}\n", encoding="utf-8")
            (edir / "data.json").write_text(json.dumps({"series": [], "verdicts": []}), encoding="utf-8")
            (edir / "report.md").write_text("# Fixture report\n\nNo figures.\n", encoding="utf-8")
            (edir / "quality.json").write_text(json.dumps({**QUALITY, "bq": bq}), encoding="utf-8")
        dossier = repo / DOSSIER_REL
        dossier.parent.mkdir(parents=True)
        dossier.write_text("# Review dossier\n\n## Verdict\n\nDossier body sentinel text.\n",
                           encoding="utf-8")
        # a non-markdown file inside the repo — must never be served inline
        (repo / "secrets.py").write_text("TOKEN = 'nope'\n", encoding="utf-8")

        os.environ["CLAUDE_PROJECT_DIR"] = str(repo)
        import console.config as config_mod
        config_mod.get_config.cache_clear()
        # console.app may already be imported by another test module — its
        # module-level get_config() call only mounts /assets, safe either way.
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

    # ---- schema 1.3: history renders ------------------------------------

    def test_history_fold_renders_with_findings_table(self):
        r = self.client.get("/commercial/BQ-99")
        self.assertEqual(r.status_code, 200)
        html = r.text
        self.assertIn("Previous review", html)
        self.assertIn("e7f42f06e380", html)          # superseded sha pill
        self.assertIn("CHANGES-REQUIRED", html)      # history verdict chip
        self.assertIn("superseded", html)
        # findings table content: id | severity | summary | disposition
        self.assertIn("F-1", html)
        self.assertIn("Headline asserts guardrail unconditionally", html)
        self.assertIn("fix: branch on raw share vs thr", html)
        self.assertIn("F-2", html)
        # severity chips resolved through SEV_META
        self.assertIn("sv-high", html)
        self.assertIn("sv-low", html)

    def test_inline_dossier_folds_present(self):
        html = self.client.get("/commercial/BQ-99").text
        # current review + history entry + verification record each carry a fold
        self.assertGreaterEqual(html.count(f'data-md="{DOSSIER_REL}"'), 3)
        self.assertIn("Full review dossier", html)
        # secondary affordance: the Documents-viewer link is kept
        self.assertIn(f"/documents#path={DOSSIER_REL}", html)

    # ---- review-detail endpoint -----------------------------------------

    def test_review_detail_renders_markdown(self):
        r = self.client.get("/commercial/review-detail", params={"path": DOSSIER_REL})
        self.assertEqual(r.status_code, 200)
        self.assertIn("Dossier body sentinel text", r.text)
        self.assertIn("<h1", r.text)  # rendered HTML, not raw markdown

    def test_review_detail_rejects_traversal(self):
        for bad in ("../../etc/passwd.md", "docs/../../outside.md",
                    "tasks/ben/_work/../../../escape.md"):
            r = self.client.get("/commercial/review-detail", params={"path": bad})
            self.assertEqual(r.status_code, 403, bad)

    def test_review_detail_rejects_absolute(self):
        for bad in ("/etc/passwd.md", "/tmp/x.md", "\\\\server\\share\\x.md"):
            r = self.client.get("/commercial/review-detail", params={"path": bad})
            self.assertEqual(r.status_code, 403, bad)

    def test_review_detail_rejects_non_markdown(self):
        for bad in ("secrets.py", "project.yml", "docs/project/commercial/.console/commercial-index.json"):
            r = self.client.get("/commercial/review-detail", params={"path": bad})
            self.assertEqual(r.status_code, 403, bad)

    def test_review_detail_missing_md_404(self):
        r = self.client.get("/commercial/review-detail", params={"path": "tasks/ben/_work/nope.md"})
        self.assertEqual(r.status_code, 404)

    def test_review_detail_empty_path_403(self):
        r = self.client.get("/commercial/review-detail", params={"path": ""})
        self.assertEqual(r.status_code, 403)

    # ---- schema ≤1.2 degradation ----------------------------------------

    def test_schema_12_row_degrades_cleanly(self):
        r = self.client.get("/commercial/BQ-98")
        self.assertEqual(r.status_code, 200)
        html = r.text
        self.assertNotIn("Previous review", html)
        # code panel still renders the artifact + current review
        self.assertIn("bq_modules/bq_98.py", html)
        self.assertIn("APPROVED", html)
        # no inline dossier chrome inside the code panel for a null detail_ref
        self.assertNotIn('details class="cm-dossier" data-md="None"', html)


if __name__ == "__main__":
    unittest.main()
