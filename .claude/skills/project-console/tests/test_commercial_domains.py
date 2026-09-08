"""Business-domain generalization of the commercial section.

One router, N domain roots: any `docs/project/<slug>/.console/<slug>-index.json`
is a domain tab at `/domains/<slug>`. Covers:

- discovery: two sidecars -> two domains, `commercial` first, titles from the
  sidecar's `domain` block (schema 1.5) with folder-derived fallback (schema 1.4)
- routing: `/domains/<slug>` + answer view render for a non-commercial domain,
  legacy `/commercial...` URLs 307 to `/domains/commercial...` (query kept),
  unknown slug -> 404
- the nav renders one entry per domain with its own icon
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

EDITION = "2026-09-08"


def _question(domain: str, qid: str) -> dict:
    return {
        "id": qid, "question": f"Fixture question {qid}", "category": "fixture",
        "personas": ["cfo"], "cadence": "monthly", "status": "draft-only",
        "approved_edition": None, "draft_edition": EDITION, "latest_edition": EDITION,
        "editions": [{"edition": EDITION, "status": "draft"}],
        "assumptions": [], "freshness": None, "verdict_headline": None,
        "evidence_class": None,
        "report_path": f"docs/project/{domain}/reports/{qid}/{EDITION}/report.md",
        "data_path": f"docs/project/{domain}/reports/{qid}/{EDITION}/data.json",
        "explainers": {}, "terms": [], "code": None,
    }


def _seed_domain(repo: Path, domain: str, qid: str, domain_block: dict | None):
    root = repo / "docs" / "project" / domain
    (root / ".console").mkdir(parents=True)
    index = {"schema_version": "1.5" if domain_block else "1.4",
             "generated": "2026-09-08T10:00:00",
             "categories": [{"key": "fixture", "name": "Fixture"}],
             "questions": [_question(domain, qid)]}
    if domain_block:
        index["domain"] = domain_block
    (root / ".console" / f"{domain}-index.json").write_text(json.dumps(index), encoding="utf-8")
    edir = root / "reports" / qid / EDITION
    edir.mkdir(parents=True)
    (edir / "edition.yml").write_text(
        f"bq: {qid}\nedition: '{EDITION}'\nstatus: draft\n"
        f"created_at: '2026-09-08T09:00:00'\npins: {{}}\n", encoding="utf-8")
    # one trend line with a NULL point — a gap (no observation that period), which the
    # geometry must skip rather than compare against floats
    series = [{"id": "trend", "label": "trend", "unit": "%", "kind": "timeseries",
               "evidence_class": "derived", "provenance": {"dataset": "x/y", "snapshot": EDITION},
               "lines": [{"label": "a", "points": [{"x": "2026-07-01", "y": 95.0},
                                                    {"x": "2026-08-01", "y": None},
                                                    {"x": "2026-09-01", "y": 96.5}]}],
               "points": []},
              # paired bars with a NULL measure (e.g. no plan row for one category)
              {"id": "pairs", "label": "pairs", "unit": "USD", "kind": "paired-bars",
               "pairs": {"a_label": "actual", "b_label": "plan"}, "evidence_class": "derived",
               "provenance": {"dataset": "x/y", "snapshot": EDITION},
               "points": [{"label": "L1", "a": 10.0, "b": 12.0}, {"label": "L2", "a": 3.0, "b": None}]}]
    (edir / "data.json").write_text(json.dumps({"series": series, "verdicts": []}), encoding="utf-8")
    (edir / "report.md").write_text("# Fixture report\n\nNo figures.\n", encoding="utf-8")


class CommercialDomainsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="cm-domains-"))
        repo = cls.tmp
        (repo / "project.yml").write_text(
            "project:\n  name: Fixture\nteam:\n  active:\n  - name: Ben\n    github: benx\n",
            encoding="utf-8")
        # schema-1.4 sidecar (no domain block) -> folder-derived identity
        _seed_domain(repo, "commercial", "BQ-01", None)
        # schema-1.5 sidecar with an explicit identity block
        _seed_domain(repo, "finance", "FQ-01",
                     {"key": "finance", "name": "Finance", "nav_title": "Finance",
                      "tagline": "margin, cost of quality, working capital",
                      "icon": "finance", "id_prefix": "FQ"})
        # a folder WITHOUT a sidecar must not become a domain
        (repo / "docs" / "project" / "strategies").mkdir(parents=True)

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

    # ---- discovery -------------------------------------------------------

    def test_list_domains_orders_commercial_first_and_reads_identity(self):
        from console.commercial.loader import list_domains
        doms = list_domains(self.tmp)
        self.assertEqual([d["key"] for d in doms], ["commercial", "finance"])
        self.assertEqual(doms[0]["name"], "Commercial")       # folder-derived (1.4)
        self.assertEqual(doms[0]["icon"], "commercial")
        self.assertEqual(doms[1]["name"], "Finance")          # from the block (1.5)
        self.assertEqual(doms[1]["icon"], "finance")
        self.assertEqual(doms[1]["href"], "/domains/finance")
        self.assertEqual(doms[1]["id_prefix"], "FQ")

    def test_unknown_icon_falls_back_to_commercial_sprite(self):
        from console.commercial.loader import domain_meta
        root = self.tmp / "docs" / "project" / "finance" / ".console" / "finance-index.json"
        idx = json.loads(root.read_text())
        idx["domain"]["icon"] = "no-such-sprite"
        root.write_text(json.dumps(idx))
        try:
            self.assertEqual(domain_meta(self.tmp, "finance")["icon"], "commercial")
        finally:
            idx["domain"]["icon"] = "finance"
            root.write_text(json.dumps(idx))

    # ---- routing ---------------------------------------------------------

    def test_domain_index_and_view_render_for_finance(self):
        r = self.client.get("/domains/finance")
        self.assertEqual(r.status_code, 200)
        self.assertIn("<h1>Finance</h1>", r.text)
        self.assertIn('href="/domains/finance/FQ-01"', r.text)
        r = self.client.get("/domains/finance/FQ-01")
        self.assertEqual(r.status_code, 200)
        self.assertIn("← Finance", r.text)
        self.assertIn("/domains/finance/FQ-01/data", r.text)
        self.assertIn("--domain finance", r.text)   # CLI hints name the domain
        self.assertIn("2026-09-01", r.text)          # null-y point skipped, others drawn
        self.assertNotIn('href="/commercial', r.text)

    def test_legacy_commercial_urls_redirect_with_query(self):
        r = self.client.get("/commercial", follow_redirects=False)
        self.assertEqual(r.status_code, 307)
        self.assertEqual(r.headers["location"], "/domains/commercial")
        r = self.client.get("/commercial/BQ-01?edition=" + EDITION, follow_redirects=False)
        self.assertEqual(r.status_code, 307)
        self.assertEqual(r.headers["location"], f"/domains/commercial/BQ-01?edition={EDITION}")
        # and the redirect target actually renders
        self.assertEqual(self.client.get("/commercial/BQ-01").status_code, 200)

    def test_unknown_domain_is_404_and_non_sidecar_folder_is_not_a_domain(self):
        self.assertEqual(self.client.get("/domains/nope").status_code, 404)
        self.assertEqual(self.client.get("/domains/strategies").status_code, 404)

    def test_grounding_names_the_domain(self):
        r = self.client.get("/domains/finance/catalog/grounding")
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.text.startswith("# Finance question board"))

    # ---- nav -------------------------------------------------------------

    def test_nav_renders_one_entry_per_domain(self):
        html = self.client.get("/domains/finance").text
        self.assertIn('href="/domains/commercial"', html)
        self.assertIn('href="/domains/finance"', html)
        self.assertIn('<use href="#ic-finance"/>', html)
        self.assertIn('<use href="#ic-commercial"/>', html)


if __name__ == "__main__":
    unittest.main()
