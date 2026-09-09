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

Line margins are charted [derived: margin-by-line].

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
    series = [
        # cited by the "Margin by line" section via [derived: margin-by-line] -> placed there
        {"id": "margin-by-line", "label": "Gross margin by line", "unit": "%", "evidence_class": "derived",
         "derivation": {"method": "gm per line", "inputs": [f"src: {DS}@{SNAP}"]},
         "provenance": {"dataset": DS, "snapshot": SNAP},
         "points": [{"label": "PP3500", "value": 60.1}, {"label": "PP3000", "value": 45.3}]},
        # cited nowhere, no heading overlap -> Overview block
        {"id": "gm-stat", "label": "Company margin", "unit": "%", "kind": "stat", "evidence_class": "derived",
         "derivation": {"method": "total", "inputs": [f"src: {DS}@{SNAP}"]},
         "provenance": {"dataset": DS, "snapshot": SNAP},
         "points": [{"label": "H1 margin", "value": 51.5}]},
    ]
    (edir / "data.json").write_text(json.dumps({"series": series, "verdicts": [{"id": "v-main", "headline": "margin 51.5%", "evidence_class": "derived"}]}), encoding="utf-8")
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
                            "explainers": {"question": {"label": "This analysis",
                                                       "what": "What this analysis covers.",
                                                       "why": "Why it matters."}},
                            "terms": [], "code": None}]}
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

    def test_full_report_places_chart_in_cited_section_and_overview(self):
        html = self.client.get("/domains/finance2/FQ-91").text
        self.assertIn('data-tab="cm-tab-viz"', html)
        self.assertIn('data-tab="cm-tab-report"', html)
        full = html.split('id="cm-tab-report"')[1].split("<!-- /#cm-tab-report -->")[0]
        # section order inside the document: heading -> table -> chart -> narrative fold
        h = full.index("Margin by line</h2>")
        tbl = full.index("<table", h)
        fig = full.index("cm-chart-inline", h)
        fold = full.index('class="cm-narr"', h)
        self.assertTrue(h < tbl < fig < fold, (h, tbl, fig, fold))
        self.assertIn("Gross margin by line", full)
        # the uncited stat chart lands in the Overview block ahead of the sections
        ov = full.index("cm-fr-overview")
        self.assertIn("Company margin", full[ov:h])
        self.assertTrue(ov < h)

    def test_export_md_embeds_charts_by_section(self):
        r = self.client.get("/domains/finance2/FQ-91/export?edition=2026-09-08&format=md")
        self.assertEqual(r.status_code, 200)
        body = r.text
        sec = body.index("## Margin by line")
        img = body.index("![](charts/margin-by-line.svg)")
        self.assertIn("_Figure — Gross margin by line (%)", body)
        nxt = body.index("### What this tells us", sec)
        self.assertTrue(sec < img < nxt, (sec, img, nxt))
        ov = body.index("## Overview")
        self.assertIn("charts/gm-stat.svg", body[ov:sec])
        svg = self.tmp / "docs" / "project" / "finance2" / "reports" / "FQ-91" / EDITION / "exports" / "charts" / "margin-by-line.svg"
        self.assertTrue(svg.is_file())
        self.assertIn("PP3500", svg.read_text())

    # ---- header: status ≠ actions ≠ navigation ≠ help --------------------

    @property
    def html(self):
        return self.client.get("/domains/finance2/FQ-91").text

    def test_info_icon_rides_the_identifier_line_without_a_label(self):
        eyebrow = self.html.split('class="cm-eyebrow"')[1].split("</p>")[0]
        self.assertIn("cm-eyebrow-info", eyebrow)
        self.assertNotIn("About this analysis<", self.html)   # no labelled pill

    def test_export_is_one_menu_and_data_view_is_gone(self):
        self.assertIn('class="cm-menu"', self.html)
        self.assertIn("format=docx", self.html)
        self.assertIn("format=pdf", self.html)
        self.assertIn("format=md", self.html)
        self.assertNotIn("Data view", self.html)              # the Data tab goes there
        self.assertNotIn("cm-export-chip", self.html)

    def test_expected_state_renders_no_status_line(self):
        """Derived evidence with no freshness flag is unremarkable — the header stays
        silent so a marker always means "read this"."""
        self.assertNotIn('class="cm-meta"', self.html)
        self.assertNotIn("Draft — not approved", self.html)   # the editions rail names it

    def test_tab_row_carries_no_status_badges(self):
        tabrow = self.html.split('class="cm-toptabs"')[1].split("</div>")[0]
        for leaked in ("lint", "verification", "In sync", "cm-chip", "cm-badge"):
            self.assertNotIn(leaked, tabrow)
        self.assertIn("Quality &amp; audit", tabrow)

    # ---- "How it was built": a derived walkthrough, nothing authored ------

    def test_how_tab_is_present_and_labelled_for_readers(self):
        html = self.html
        self.assertIn('data-tab="cm-tab-how"', html)
        self.assertIn("How it was built", html)
        # not framed as model reasoning: a deterministic script computes every figure
        self.assertNotIn("Chain-of-Thought", html)

    def test_how_tab_shows_each_figure_s_recorded_derivation(self):
        how = self.html.split('id="cm-tab-how"')[1].split("<!-- /#cm-tab-how -->")[0]
        self.assertIn("How each figure was produced", how)
        self.assertIn("gm per line", how)                 # the computation's own method
        self.assertIn("Gross margin by line", how)

    def test_how_tab_lists_challengeable_points_with_an_action(self):
        how = self.html.split('id="cm-tab-how"')[1].split("<!-- /#cm-tab-how -->")[0]
        self.assertIn("Where to push back", how)
        self.assertIn("cm-how-item", how)
        self.assertIn("To change it", how)
        # the fixture has no analysis plan, so plan currency is the open point
        self.assertIn("analysis plan", how)

    def test_pin_freshness_is_computed_now_not_read_from_the_frozen_audit(self):
        """quality.json records a pin's age at LINT time. Reading it here made the
        challenge list say nothing while the header said "Stale" — the two surfaces
        must never contradict each other."""
        import datetime
        from console.commercial.router import _pin_freshness
        ds = "fixture/aged"
        d = self.tmp / "docs" / "project" / "corpus" / ds
        d.mkdir(parents=True, exist_ok=True)
        (d / "dataset.yml").write_text("max_age_days: 7\n", encoding="utf-8")
        old = _pin_freshness(self.tmp, ds, "2020-01-01")
        self.assertEqual(old["band"], "stale")
        self.assertGreater(old["age"], 7)
        today = datetime.date.today().isoformat()
        self.assertEqual(_pin_freshness(self.tmp, ds, today)["band"], "fresh")

    def test_how_tab_reads_the_plan_by_section(self):
        from console.commercial.router import _plan_sections
        secs = _plan_sections("## Question\nq\n\n## Goal — the decision this serves\n"
                              "the monthly review\n\n## Approach\nwindow = closed quarters\n\n"
                              "## Assertions & limits\nasserts nothing else\n")
        self.assertEqual(secs["goal"], "the monthly review")
        self.assertEqual(secs["approach"], "window = closed quarters")
        self.assertEqual(secs["assertions"], "asserts nothing else")

    def test_export_rejects_bad_format(self):
        self.assertEqual(self.client.get("/domains/finance2/FQ-91/export?format=txt").status_code, 400)


class VerdictTypesettingTest(unittest.TestCase):
    """The headline is `"; ".join(parts)` from the computation. The console breaks it
    into a lead + points for readability; it must never alter a character."""

    def setUp(self):
        from console.commercial.router import _split_verdict
        self.split = _split_verdict

    def test_three_or_more_clauses_become_lead_plus_points(self):
        lead, pts = self.split("portfolio yield 96.6%; 0 of 5 lines below the floor; scrap 1.0%")
        self.assertEqual(lead, "portfolio yield 96.6%")
        self.assertEqual(pts, ["0 of 5 lines below the floor", "scrap 1.0%"])

    def test_semicolon_inside_parentheses_is_not_a_break(self):
        lead, pts = self.split("yield 96.6% (down 0.1 pts; prior window); 0 of 5 below; scrap 1.0%")
        self.assertEqual(lead, "yield 96.6% (down 0.1 pts; prior window)")
        self.assertEqual(len(pts), 2)

    def test_short_headline_stays_one_paragraph(self):
        lead, pts = self.split("margin 51.5%; below the 55% floor")
        self.assertEqual(lead, "margin 51.5%; below the 55% floor")
        self.assertEqual(pts, [])

    def test_no_characters_are_lost(self):
        raw = ("Trailing window 2026-06..2026-08: yield 96.6% on 10970 units (down 0.1 pts); "
               "0 of 5 lines below the 95% floor; erosion is rev-specific — rev C 92.5%; scrap 1.0%")
        lead, pts = self.split(raw)
        self.assertEqual("; ".join([lead] + pts), raw)


if __name__ == "__main__":
    unittest.main()
