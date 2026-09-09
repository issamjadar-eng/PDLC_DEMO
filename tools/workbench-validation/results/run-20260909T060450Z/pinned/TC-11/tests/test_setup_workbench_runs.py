"""Settings → Workbench Validation: run-revision selection and package export.

Hermetic: a temp repo carries two synthetic run JSONs, an index, one per-run
sidecar, a main sidecar, and a STUB export_package.py that writes a file and
prints its path — so the route contract is exercised without the real skill.
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve()
SKILL_ROOT = HERE.parents[1]
sys.path.insert(0, str(SKILL_ROOT))

RUN_OLD, RUN_NEW = "run-20260901T100000Z", "run-20260902T100000Z"


def _run_json(rid: str, started: str, summary: dict, sha: str) -> dict:
    return {"schema_version": "2.0", "run_id": rid, "started": started, "finished": started,
            "partial": False, "invoked_via": "cli", "summary": summary,
            "environment": {"git_sha_short": sha, "git_dirty": False, "model_id": "m-1"},
            "cases": []}


def _sidecar(rid: str, verdict: str, sha: str) -> dict:
    return {"schema_version": "2.0", "title": "T", "banner": None,
            "run": {"run_id": rid, "started": "2026-09-01T10:00:00Z", "finished": "2026-09-01T10:00:20Z",
                    "duration_s": 20, "partial": False, "invoked_via": "cli", "operator": {}},
            "baseline": {"git_sha_short": sha, "git_branch": "main", "git_dirty": False,
                         "skills_total": 1, "hooks_total": 0, "model_id": "m-1"},
            "summary": {"verdict": verdict, "needs": {"total": 1, "pass": 1}, "tests": {"total": 1, "PASS": 1}},
            "needs": [], "tests": [], "warnings": [], "environment": {}}


def _seed(repo: Path, with_index: bool = True) -> None:
    res = repo / "tools" / "workbench-validation" / "results"
    res.mkdir(parents=True)
    (res / f"{RUN_OLD}.json").write_text(json.dumps(_run_json(
        RUN_OLD, "2026-09-01T10:00:00Z", {"PASS": 3, "FAIL": 1}, "aaa1111")))
    (res / f"{RUN_NEW}.json").write_text(json.dumps(_run_json(
        RUN_NEW, "2026-09-02T10:00:00Z", {"PASS": 4}, "bbb2222")))
    # per-run sidecar for the OLD run only; the NEW (latest) run relies on the main sidecar
    (res / RUN_OLD).mkdir()
    (res / RUN_OLD / "sidecar.json").write_text(json.dumps(_sidecar(RUN_OLD, "FAIL", "aaa1111")))
    (repo / "tools" / "workbench-validation" / "workbench-validation-index.json").write_text(
        json.dumps(_sidecar(RUN_NEW, "PASS", "bbb2222")))
    if with_index:
        rows = []
        for rid, st, summ, sha, v in ((RUN_NEW, "2026-09-02T10:00:00Z", {"PASS": 4}, "bbb2222", "PASS"),
                                       (RUN_OLD, "2026-09-01T10:00:00Z", {"PASS": 3, "FAIL": 1}, "aaa1111", "FAIL")):
            rows.append({"run_id": rid, "started": st, "finished": st, "verdict": v, "summary": summ,
                         "partial": False, "invoked_via": "cli", "schema_version": "2.0",
                         "git_sha_short": sha, "git_dirty": False, "model_id": "m-1",
                         "sidecar": f"tools/workbench-validation/results/{rid}/sidecar.json",
                         "report": f"tools/workbench-validation/results/{rid}/validation-report.md"})
        (res / "index.json").write_text(json.dumps(rows))
    # skill scripts: runner (marks the skill installed) + STUB exporter
    scripts = repo / ".claude" / "skills" / "workbench-validation" / "scripts"
    scripts.mkdir(parents=True)
    (scripts / "run_validation.py").write_text("print('stub runner')\n")
    (scripts / "export_package.py").write_text(
        "import sys, argparse, pathlib\n"
        "ap = argparse.ArgumentParser(); ap.add_argument('--root'); ap.add_argument('--run'); ap.add_argument('--format')\n"
        "a = ap.parse_args()\n"
        "if a.run == 'run-explode': print('boom', file=sys.stderr); sys.exit(2)\n"
        "out = pathlib.Path(a.root) / 'tools' / 'workbench-validation' / 'exports' / a.run\n"
        "out.mkdir(parents=True, exist_ok=True)\n"
        "p = out / f'validation-package.{a.format}'\n"
        "p.write_text(f'# package {a.run} {a.format}\\n')\n"
        "print('building…'); print(str(p.resolve()))\n")


class _Base(unittest.TestCase):
    with_index = True

    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="wb-runs-"))
        (cls.tmp / "project.yml").write_text(
            "project:\n  name: Fixture\nteam:\n  active:\n  - name: Ben\n    github: benx\n")
        _seed(cls.tmp, with_index=cls.with_index)
        os.environ["CLAUDE_PROJECT_DIR"] = str(cls.tmp)
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


class WorkbenchRunsWithIndexTest(_Base):
    def test_roster_is_newest_first_and_latest_selected(self):
        from console.setup.loader import load_workbench_validation
        wb = load_workbench_validation(self.tmp)
        self.assertEqual([r["run_id"] for r in wb["runs"]], [RUN_NEW, RUN_OLD])
        self.assertEqual(wb["selected_run_id"], RUN_NEW)
        self.assertTrue(wb["is_latest"])
        # latest has no per-run sidecar → falls back to the main sidecar
        self.assertEqual(wb["data"]["summary"]["verdict"], "PASS")
        self.assertTrue(wb["data_source"].endswith("workbench-validation-index.json"))
        self.assertEqual(wb["runs"][1]["pass_cases"], 3)
        self.assertEqual(wb["runs"][1]["total_cases"], 4)

    def test_selecting_a_revision_reads_its_own_sidecar(self):
        from console.setup.loader import load_workbench_validation
        wb = load_workbench_validation(self.tmp, run_id=RUN_OLD)
        self.assertFalse(wb["is_latest"])
        self.assertEqual(wb["data"]["summary"]["verdict"], "FAIL")
        self.assertIn(f"{RUN_OLD}/sidecar.json", wb["data_source"])
        self.assertIsNone(wb["revision_notice"])

    def test_page_renders_toolbar_and_selection(self):
        r = self.client.get("/setup")
        self.assertEqual(r.status_code, 200)
        self.assertIn('id="su-wb-run-select"', r.text)
        self.assertIn(f'value="{RUN_NEW}" selected', r.text)
        self.assertIn("Export Word", r.text)
        self.assertIn(f"/setup/workbench/export?run={RUN_NEW}&format=pdf", r.text)
        self.assertIn('id="su-wb-run"', r.text)  # re-run available on latest
        r2 = self.client.get(f"/setup?run={RUN_OLD}")
        self.assertEqual(r2.status_code, 200)
        self.assertIn(f'value="{RUN_OLD}" selected', r2.text)
        self.assertIn("Viewing an earlier revision", r2.text)
        self.assertNotIn('id="su-wb-run"', r2.text)  # no re-run on an old revision

    def test_unknown_run_falls_back_to_latest_with_badge(self):
        r = self.client.get("/setup?run=run-nope")
        self.assertEqual(r.status_code, 200)
        self.assertIn("unknown run requested", r.text)
        self.assertIn(f'value="{RUN_NEW}" selected', r.text)

    def test_export_route_streams_the_package(self):
        r = self.client.get(f"/setup/workbench/export?run={RUN_OLD}&format=md")
        self.assertEqual(r.status_code, 200, r.text)
        self.assertEqual(r.headers["content-type"].split(";")[0], "text/markdown")
        self.assertIn(f"validation-package-{RUN_OLD}.md", r.headers.get("content-disposition", ""))
        self.assertIn(f"package {RUN_OLD} md", r.text)
        r = self.client.get(f"/setup/workbench/export?run={RUN_NEW}&format=docx")
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.headers["content-type"].startswith(
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"))

    def test_export_route_rejects_bad_run_and_format(self):
        self.assertEqual(self.client.get(f"/setup/workbench/export?run={RUN_NEW}&format=xls").status_code, 400)
        self.assertEqual(self.client.get("/setup/workbench/export?run=run-nope&format=md").status_code, 400)

    def test_export_route_surfaces_exporter_failure(self):
        # 'run-explode' must be in the roster for the stub to be reached
        res = self.tmp / "tools" / "workbench-validation" / "results"
        rows = json.loads((res / "index.json").read_text())
        rows.append({"run_id": "run-explode", "started": "2026-08-01T00:00:00Z", "verdict": "PASS", "summary": {"PASS": 1}})
        (res / "index.json").write_text(json.dumps(rows))
        try:
            r = self.client.get("/setup/workbench/export?run=run-explode&format=md")
            self.assertEqual(r.status_code, 400)
            self.assertIn("boom", r.json()["detail"])
        finally:
            (res / "index.json").write_text(json.dumps(rows[:-1]))


class WorkbenchRunsWithoutIndexTest(_Base):
    with_index = False

    def test_roster_derived_from_run_json_when_index_missing(self):
        from console.setup.loader import load_workbench_validation
        wb = load_workbench_validation(self.tmp)
        self.assertEqual([r["run_id"] for r in wb["runs"]], [RUN_NEW, RUN_OLD])
        self.assertTrue(all(r.get("derived") for r in wb["runs"]))
        self.assertEqual(wb["runs"][1]["verdict"], "FAIL")   # FAIL in summary → FAIL
        self.assertEqual(wb["runs"][0]["verdict"], "PASS")

    def test_missing_per_run_sidecar_is_reported_not_substituted(self):
        from console.setup.loader import load_workbench_validation
        res = self.tmp / "tools" / "workbench-validation" / "results"
        shutil.rmtree(res / RUN_OLD)
        try:
            wb = load_workbench_validation(self.tmp, run_id=RUN_OLD)
            self.assertIsNone(wb["data"])
            self.assertIn("no rendered sidecar", wb["revision_notice"])
            r = self.client.get(f"/setup?run={RUN_OLD}")
            self.assertEqual(r.status_code, 200)
            self.assertIn("render --all-runs", r.text)
        finally:
            (res / RUN_OLD).mkdir()
            (res / RUN_OLD / "sidecar.json").write_text(json.dumps(_sidecar(RUN_OLD, "FAIL", "aaa1111")))


if __name__ == "__main__":
    unittest.main()
