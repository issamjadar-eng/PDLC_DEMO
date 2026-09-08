"""Narrative layer + export on the domain answer view.

- an edition WITHOUT narrative.md renders the empty executive-summary panel with a
  Generate button and no "What this tells us" folds
- an edition WITH narrative.md (front matter pinning current hashes) renders the
  executive summary and a fold under each matching report section; markers become
  numbered references like the report's own
- a narrative whose pinned hashes no longer match is flagged stale
- the export route streams a markdown document assembled by the engine (exec
  summary + sections + narratives + references); bad format -> 400
"""
from __future__ import annotations

import hashlib
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

EDITION = "2026-09-08"
DS, SNAP = "fixture/ds", "2026-09-01"
REPORT = f"""# FQ-90 — Fixture margin

_Demo sample data — not for clinical use._

**Verdict**: margin 51.5% [derived: v-main] [src: {DS}@{SNAP}]

## Margin by line

| Line | GM % |
|---|---|
| PP3500 [src: {DS}@{SNAP}] | 60.1 |

## Method & provenance

- Summed from [src: {DS}@{SNAP}].
"""
NARR_BODY = f"""## Executive summary

Margin held at 51.5% this half, below the floor the plan set [derived: v-main]. The gap sits in two legacy lines; the flagship is healthy.

## Margin by line

PP3500 carries the portfolio at 60.1% [src: {DS}@{SNAP}]; the legacy lines dilute the total.
"""


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _seed(repo: Path, domain: str, qid: str, narrative: str | None, stale: bool = False):
    root = repo / "docs" / "project" / domain
    (root / ".console").mkdir(parents=True, exist_ok=True)
    (root / f"{domain}.yml").write_text(
        f"domain: {{name: Finance, icon: finance, id_prefix: FQ}}\n"
        f"categories: [{{key: fixture, name: Fixture}}]\n"
        f"questions:\n  - id: {qid}\n    question: Fixture margin\n    category: fixture\n"
        f"    personas: [cfo]\n    cadence: monthly\n    corpus_deps: [{DS}]\n"
        f"    computation: 'true'\n", encoding="utf-8")
    edir = root / "reports" / qid / EDITION
    edir.mkdir(parents=True, exist_ok=True)
    (edir / "report.md").write_text(REPORT, encoding="utf-8")
    (edir / "data.json").write_text(json.dumps({"series": [], "verdicts": [{"id": "v-main", "headline": "margin 51.5%", "evidence_class": "derived"}]}), encoding="utf-8")
    (edir / "edition.yml").write_text(
        f"bq: {qid}\nedition: '{EDITION}'\nstatus: draft\ncreated_at: '2026-09-08T09:00:00'\n"
        f"pins:\n  {DS}: '{SNAP}'\n", encoding="utf-8")
    if narrative is not None:
        r = "0" * 64 if stale else _sha(edir / "report.md")
        d = "0" * 64 if stale else _sha(edir / "data.json")
        (edir / "narrative.md").write_text(
            f"---\nreport_sha256: {r}\ndata_sha256: {d}\ngenerated_at: '2026-09-08T10:00:00+00:00'\n"
            f"author: AI assistant\n---\n{narrative}", encoding="utf-8")
    # corpus snapshot so [src:] resolves for the engine's export/lint
    snap = repo / "docs" / "project" / "corpus" / DS / "snapshots" / SNAP
    snap.mkdir(parents=True, exist_ok=True)
    (repo / "docs" / "project" / "corpus" / DS / "dataset.yml").write_text("max_age_days: 3650\n", encoding="utf-8")
    index = {"schema_version": "1.6", "generated": "2026-09-08T10:00:00",
             "domain": {"key": domain, "name": "Finance", "nav_title": "Finance", "icon": "finance", "id_prefix": "FQ"},
             "categories": [{"key": "fixture", "name": "Fixture"}],
             "questions": [{"id": qid, "question": "Fixture margin", "category": "fixture", "personas": ["cfo"],
                            "cadence": "monthly", "status": "draft-only", "approved_edition": None,
                            "draft_edition": EDITION, "latest_edition": EDITION,
                            "editions": [{"edition": EDITION, "status": "draft"}], "assumptions": [],
                            "freshness": None, "verdict_headline": "margin 51.5%", "evidence_class": "derived",
                            "report_path": f"docs/project/{domain}/reports/{qid}/{EDITION}/report.md",
                            "data_path": f"docs/project/{domain}/reports/{qid}/{EDITION}/data.json",
                            "explainers": {}, "terms": [], "code": None}]}
    (root / ".console" / f"{domain}-index.json").write_text(json.dumps(index), encoding="utf-8")


class CommercialNarrativeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="cm-narr-"))
        repo = cls.tmp
        (repo / "project.yml").write_text("project:\n  name: Fixture\nteam:\n  active:\n  - name: Ben\n    github: benx\n", encoding="utf-8")
        # the engine lives in the real repo — the export route shells it with cwd=fixture repo
        skill = repo / ".claude" / "skills" / "commercial" / "scripts"
        skill.mkdir(parents=True)
        shutil.copy(_REPO_ROOT / ".claude" / "skills" / "commercial" / "scripts" / "commercial.py", skill / "commercial.py")
        _seed(repo, "finance", "FQ-90", None)
        _seed(repo, "finance2", "FQ-91", NARR_BODY)
        _seed(repo, "finance3", "FQ-92", NARR_BODY, stale=True)
        os.environ["CLAUDE_PROJECT_DIR"] = str(repo)
        import console.config as config_mod
        config_mod.get_config.cache_clear()
        for m in [m for m in list(sys.modules) if m == "console.app"]:
            del sys.modules[m]
        from fastapi.testclient import TestClient
        from console.app import app
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)
        os.environ.pop("CLAUDE_PROJECT_DIR", None)
        import console.config as config_mod
        config_mod.get_config.cache_clear()

    def test_missing_narrative_renders_empty_panel_with_generate(self):
        html = self.client.get("/domains/finance/FQ-90").text
        self.assertIn("Executive summary", html)
        self.assertIn("Generate narrative", html)
        self.assertIn("No narrative yet", html)
        self.assertNotIn('class="cm-narr"', html)
        self.assertIn("/domains/finance/FQ-90/export?edition=2026-09-08&amp;format=docx", html)

    def test_present_narrative_renders_summary_and_section_folds(self):
        html = self.client.get("/domains/finance2/FQ-91").text
        self.assertIn("Regenerate narrative", html)
        self.assertIn("Margin held at 51.5% this half", html)
        self.assertEqual(html.count('class="cm-narr"'), 1)          # one report section matched
        self.assertIn("What this tells us", html)
        self.assertIn("carries the portfolio at 60.1%", html)
        self.assertNotIn("stale", html.split("cm-exec-head")[1].split("</section>")[0])
        # markers in the narrative became numbered references, not raw text
        self.assertNotIn("[derived: v-main]", html)

    def test_stale_narrative_is_flagged(self):
        html = self.client.get("/domains/finance3/FQ-92").text
        self.assertIn("stale — regenerate", html)
        self.assertIn('class="cm-narr-stale"', html)

    def test_export_markdown_assembles_document(self):
        r = self.client.get("/domains/finance2/FQ-91/export?edition=2026-09-08&format=md")
        self.assertEqual(r.status_code, 200, r.text[:300])
        self.assertIn("attachment", r.headers.get("content-disposition", ""))
        body = r.text
        self.assertIn("## Executive summary", body)
        self.assertIn("Margin held at 51.5%", body)
        self.assertIn("## Margin by line", body)
        self.assertIn("### What this tells us", body)
        self.assertIn("## References", body)
        self.assertIn(f"`{DS}`, immutable snapshot `{SNAP}`", body)
        self.assertNotIn("[src:", body)                             # markers rendered as references
        self.assertIn("DRAFT", body)

    def test_export_without_narrative_has_placeholder(self):
        r = self.client.get("/domains/finance/FQ-90/export?edition=2026-09-08&format=md")
        self.assertEqual(r.status_code, 200)
        self.assertIn("No executive summary has been written", r.text)

    def test_export_rejects_bad_format(self):
        self.assertEqual(self.client.get("/domains/finance2/FQ-91/export?format=txt").status_code, 400)


if __name__ == "__main__":
    unittest.main()
