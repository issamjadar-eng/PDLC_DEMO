"""Regression suite for the workbench-validation runner + renderer.

Hermetic (endpoint: none): exercises the pure functions that decide what the
validation record says — need-format lint, frontmatter parsing, user-story
composition, per-need verdicts incl. NOT-APPLICABLE, strongest-evidence text,
schema comparison — plus an end-to-end run of a tiny synthetic manifest in a
temp git repo. Run:

    uv run --no-project --with pytest --with pyyaml -- pytest .claude/skills/workbench-validation/tests -q
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

SKILL = Path(__file__).resolve().parents[1]


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, SKILL / "scripts" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


run = _load("run_validation")
render = _load("render_report")


# ---- runner: pure helpers -------------------------------------------------

def test_frontmatter_block_reads_whole_fence_not_head_window():
    long_desc = "description: " + ("x" * 5000)
    text = f"---\nname: s\n{long_desc}\nversion: 7\n---\n# body\nversion: 99\n"
    block = run.frontmatter_block(text)
    assert "version: 7" in block and "version: 99" not in block


def test_frontmatter_block_empty_when_no_fence():
    assert run.frontmatter_block("# no frontmatter\nversion: 1\n") == ""


@pytest.mark.parametrize("a,b,expected", [("1.2", "1.2", True), ("1.10", "1.2", True),
                                          ("1.1", "1.2", False), ("2.0", "1.2", True), ("x", "1.2", False)])
def test_schema_at_least(a, b, expected):
    assert run._schema_at_least(a, b) is expected


def test_lint_needs_requires_role_need_so_that():
    problems, warns = run.lint_needs([
        {"id": "WUN-01", "role": "QE", "need": "do x", "so_that": "y"},
        {"id": "WUN-02", "role": "QE", "need": "do x"},
        {"id": "WUN-03", "need": "do x", "so_that": "y"},
    ])
    assert problems == ["WUN-02: missing `so_that`", "WUN-03: missing `role`"]
    assert warns == []


def test_lint_needs_warns_on_duplicated_story_wording():
    _, warns = run.lint_needs([
        {"id": "WUN-01", "role": "QE", "need": "As a QE I need x", "so_that": "so that y"},
        {"id": "WUN-02", "role": "QE", "need": "the workbench does x", "so_that": "y"},
    ])
    assert any("WUN-01" in w and "story wording" in w for w in warns)
    assert any("WUN-01" in w and "so_that" in w for w in warns)
    assert any("WUN-02" in w and "subject" in w for w in warns)


def test_execute_case_not_applicable_for_undeclared_live_connection(tmp_path):
    case = {"id": "TC-X", "endpoint": "live", "connection": "jira", "cmd": ["false"]}
    res = run.execute_case(case, tmp_path, connections={"jira": "none"})
    assert res["status"] == "NOT-APPLICABLE" and "jira" in res["reason"]


def test_execute_case_runs_live_when_connection_declared(tmp_path):
    case = {"id": "TC-X", "endpoint": "live", "connection": "jira", "cmd": ["true"]}
    res = run.execute_case(case, tmp_path, connections={"jira": "configured"})
    assert res["status"] == "PASS"


def test_execute_case_rejects_unknown_tier(tmp_path):
    res = run.execute_case({"id": "TC-X", "endpoint": "fake", "cmd": ["true"]}, tmp_path)
    assert res["status"] == "ERROR" and "endpoint tier" in res["reason"]


def test_execute_case_pass_and_fail_patterns(tmp_path):
    ok = run.execute_case({"id": "A", "endpoint": "none", "cmd": ["echo", "ALL GOOD"],
                           "pass_pattern": "ALL GOOD"}, tmp_path)
    bad = run.execute_case({"id": "B", "endpoint": "none", "cmd": ["echo", "FAILED x"],
                            "fail_pattern": "FAILED"}, tmp_path)
    assert ok["status"] == "PASS" and bad["status"] == "FAIL"


# ---- renderer: pure helpers ------------------------------------------------

def test_need_statement_composes_user_story_and_lowercases_role():
    n = {"role": "Reviewer / approver", "need": "show me x", "so_that": "I can y."}
    assert render.need_statement(n) == \
        "As a reviewer / approver, I need the workbench to show me x, so that I can y."


def test_need_statement_keeps_acronym_role_and_picks_article():
    assert render.need_statement({"role": "DHF author", "need": "x", "so_that": "y"}).startswith("As a DHF author,")
    assert render.need_statement({"role": "Auditor", "need": "x", "so_that": "y"}).startswith("As an auditor,")


def _cases(**statuses):
    return {cid: {"id": cid, "status": st, "endpoint": ep, "connection": conn}
            for cid, (st, ep, conn) in statuses.items()}


def test_need_verdict_not_applicable_never_lowers_verdict():
    idx = _cases(A=("PASS", "mocked", None), B=("NOT-APPLICABLE", "live", "jira"))
    need = {"coverage": "tests", "_tests": ["A", "B"]}
    assert render.need_verdict(need, idx) == "PASS"
    assert render.strongest_evidence(need, idx) == "mock-verified; live jira not applicable in this deployment"


def test_need_verdict_all_not_applicable():
    idx = _cases(B=("NOT-APPLICABLE", "live", "jira"))
    assert render.need_verdict({"coverage": "tests", "_tests": ["B"]}, idx) == "NOT-APPLICABLE"


def test_need_verdict_fail_partial_no_evidence():
    idx = _cases(A=("PASS", "none", None), B=("FAIL", "none", None), C=("SKIPPED", "none", None))
    assert render.need_verdict({"coverage": "tests", "_tests": ["A", "B"]}, idx) == "FAIL"
    assert render.need_verdict({"coverage": "tests", "_tests": ["A", "C"]}, idx) == "PARTIAL"
    assert render.need_verdict({"coverage": "tests", "_tests": []}, idx) == "NO-EVIDENCE"
    assert render.need_verdict({"coverage": "process-control"}, idx) == "PROCESS-CONTROL"


def test_overall_verdict_ignores_not_applicable():
    needs = [{"_verdict": "PASS"}, {"_verdict": "NOT-APPLICABLE"}, {"_verdict": "PROCESS-CONTROL"}]
    assert render.overall_verdict(needs) == "PASS"
    assert render.overall_verdict(needs + [{"_verdict": "PARTIAL"}]) == "PARTIAL"
    assert render.overall_verdict(needs + [{"_verdict": "FAIL"}]) == "FAIL"


# ---- end to end on a synthetic manifest -----------------------------------

def test_end_to_end_run_and_render(tmp_path):
    root = tmp_path
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    (root / ".claude" / "skills" / "demo").mkdir(parents=True)
    (root / ".claude" / "skills" / "demo" / "SKILL.md").write_text("---\nname: demo\nversion: 3\n---\n")
    (root / "docs").mkdir()
    manifest = {
        "schema_version": "1.2", "banner": "_demo_",
        "plan": "docs/plan.md", "results_dir": "out/results", "sidecar": "out/index.json",
        "report": {"title": "T", "output": "out/report.md"},
        "connections": {"jira": "none"},
        "user_needs": [
            {"id": "WUN-01", "role": "QE", "class": "gates", "tier": "T1",
             "need": "do x", "so_that": "y", "coverage": "tests", "implemented_by": "demo"},
        ],
        "test_cases": [
            {"id": "TC-01", "title": "ok", "wun": ["WUN-01"], "uut": ["demo"], "endpoint": "none",
             "cmd": ["true"]},
            {"id": "TC-02", "title": "live", "wun": ["WUN-01"], "uut": ["demo"], "endpoint": "live",
             "connection": "jira", "cmd": ["false"]},
        ],
    }
    import yaml
    (root / "docs" / "validation.yml").write_text(yaml.safe_dump(manifest))
    proc = subprocess.run([sys.executable, str(SKILL / "scripts" / "run_validation.py"), "--root", str(root),
                           "--manifest", "docs/validation.yml", "--render", "--model-id", "m-1"],
                          capture_output=True, text=True)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    data = json.loads((root / "out" / "results" / "latest.json").read_text())
    assert data["schema_version"] == "1.1"
    assert data["summary"] == {"PASS": 1, "NOT-APPLICABLE": 1}
    assert data["environment"]["model_id"] == "m-1" and data["environment"]["skills"]["demo"]["version"] == "3"
    assert "tooling" in data["environment"] and "connections" in data["environment"]
    side = json.loads((root / "out" / "index.json").read_text())
    assert side["summary"]["verdict"] == "PASS"
    assert side["needs"][0]["statement"] == "As a QE, I need the workbench to do x, so that y."
    assert side["tests"][1]["status"] == "NOT-APPLICABLE" and side["tests"][1]["endpoint"] == "live"
    report = (root / "out" / "report.md").read_text()
    assert "Full environment record" in report and "NOT-APPLICABLE" in report


def test_runner_refuses_manifest_missing_so_that(tmp_path):
    root = tmp_path
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    (root / "docs").mkdir()
    import yaml
    (root / "docs" / "validation.yml").write_text(yaml.safe_dump({
        "schema_version": "1.2", "results_dir": "out", "sidecar": "out/i.json",
        "report": {"output": "out/r.md"},
        "user_needs": [{"id": "WUN-01", "role": "QE", "need": "x", "coverage": "tests"}],
        "test_cases": [],
    }))
    proc = subprocess.run([sys.executable, str(SKILL / "scripts" / "run_validation.py"), "--root", str(root),
                           "--manifest", "docs/validation.yml"], capture_output=True, text=True)
    assert proc.returncode != 0 and "missing `so_that`" in (proc.stdout + proc.stderr)
