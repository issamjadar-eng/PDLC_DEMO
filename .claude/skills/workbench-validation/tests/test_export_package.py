"""Tests for export_package.py — the sectioned validation package exporter.

Hermetic: a tiny synthetic run (two cases: a scripted PASS with a log and a
pinned file; a protocol with an execution record and a run evidence file), a
pinned manifest with two needs, and a QMS coverage JSON — all under a temp
root. docx / pdf tests run only when the converters are installed.
"""
from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

SKILL = Path(__file__).resolve().parents[1]
SCRIPT = SKILL / "scripts" / "export_package.py"


def _load():
    spec = importlib.util.spec_from_file_location("export_package", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def make_root(tmp_path: Path) -> tuple[Path, str]:
    root = tmp_path
    run_id = "run-20260101T000000Z"
    results = root / "tools/workbench-validation/results"
    run_dir = results / run_id
    (run_dir / "pinned" / "TC-01" / "tests").mkdir(parents=True)
    (root / "tools/workbench-validation/protocols" / "TC-P" / "run-1").mkdir(parents=True)
    (root / "docs/project/workbench-validation/protocols").mkdir(parents=True)
    # the skill's renderer must be reachable at .claude/skills/workbench-validation/scripts
    # (export imports it by its own location, so nothing to copy) — but docflow is
    # looked up under root; docx/pdf tests copy it in.
    manifest = {
        "schema_version": "2.0", "banner": "_demo_",
        "plan": "docs/plan.md", "results_dir": "tools/workbench-validation/results",
        "sidecar": "tools/workbench-validation/index.json",
        "protocol_results_dir": "tools/workbench-validation/protocols",
        "qms_coverage": "tools/workbench-validation/qms-coverage.json",
        "report": {"title": "Test Workbench", "output": "tools/workbench-validation/report.md"},
        "deployment": {"connections": {"jira": "none"}, "content": {"qms_forms": True}},
        "user_needs": [
            {"id": "WUN-01", "role": "QE", "class": "gates", "tier": "T1", "need": "do x", "so_that": "y", "implemented_by": "demo"},
            {"id": "WUN-02", "role": "QE", "class": "audit", "tier": "T1", "need": "judge z", "so_that": "w", "implemented_by": "demo"},
        ],
        "test_cases": [
            {"id": "TC-01", "title": "scripted ok", "description": "d", "approach": "a", "wun": ["WUN-01"], "uut": ["demo"],
             "scope": "capability", "method": "scripted", "endpoint": "none", "cmd": ["true"]},
            {"id": "TC-P", "title": "protocol case", "description": "d", "approach": "a", "wun": ["WUN-02"], "uut": ["demo"],
             "scope": "deployment", "method": "protocol", "endpoint": "none",
             "protocol": "docs/project/workbench-validation/protocols/TC-P.md"},
        ],
    }
    (run_dir / "validation.yml").write_text(yaml.safe_dump(manifest))
    (run_dir / "pinned" / "TC-01" / "tests" / "test_x.py").write_text("def test(): pass\n")
    (run_dir / "TC-01.log").write_text("==== evidence log ====\nSECRET-LOG-MARKER pytest 1 passed\n")
    (root / "docs/project/workbench-validation/protocols/TC-P.md").write_text("# Protocol TC-P\n\nVersion: 2\n\nDo the thing.\n")
    (root / "tools/workbench-validation/protocols/TC-P.result.yml").write_text(
        "tc_id: TC-P\nverdict: PASS\nexecuted: 2026-01-01\noperator: qe\nmodel_id: m-1\ngit_sha: abc\nRECORD-MARKER: yes\n")
    (root / "tools/workbench-validation/protocols/TC-P/run-1/findings.md").write_text("# run 1\n\nEVIDENCE-MARKER observed\n")
    (root / "tools/workbench-validation/qms-coverage.json").write_text(json.dumps({
        "generated": "2026-01-01T00:00:00Z", "registry": "docs/internal/source-md/qms-index.md",
        "templates": [{"id": "TMP-1", "title": "Plan", "path": "p", "doc_type": "TMP", "instances": 2, "tested": True, "pass": 2, "fail": 0, "status": "covered"}],
        "procedures": [], "documents_without_template": [],
        "summary": {"templates_total": 1, "templates_instantiated": 1, "templates_tested": 1, "templates_unused": 0,
                    "procedures_total": 0, "documents_total": 2, "documents_governed": 2, "documents_without_template": 0}}))
    run = {
        "schema_version": "2.0", "run_id": run_id, "started": "2026-01-01T00:00:00Z", "finished": "2026-01-01T00:00:10Z",
        "duration_s": 10.0, "manifest": "docs/project/workbench-validation/validation.yml",
        "pinned_manifest": {"path": f"tools/workbench-validation/results/{run_id}/validation.yml", "sha256": "0" * 64},
        "invoked_via": "cli", "partial": False, "warnings": [], "connections": {"jira": "none"},
        "deployment": manifest["deployment"],
        "environment": {"git_sha": "abcdef0123", "git_sha_short": "abcdef0", "git_branch": "main", "git_dirty": False,
                        "git_dirty_files": [], "git_dirty_count": 0, "python": "3.14", "platform": "darwin",
                        "operator": {"git_user": "tester", "os_user": "t", "hostname": "h", "os": "macOS"},
                        "model_id": "m-1", "harness_version": "1.0", "hooks_installed": [], "skills": {"demo": {"version": "3"}},
                        "tooling": {"git": {"path": "/usr/bin/git", "version": "git 2"}}, "connections": {"declared": {"jira": "none"}}},
        "summary": {"PASS": 2},
        "cases": [
            {"id": "TC-01", "title": "scripted ok", "wun": ["WUN-01"], "uut": ["demo"], "uut_versions": {"demo": "3"},
             "endpoint": "none", "scope": "capability", "method": "scripted", "status": "PASS", "exit_code": 0,
             "duration_s": 0.1, "reason": None, "log": f"tools/workbench-validation/results/{run_id}/TC-01.log",
             "source": "tests", "pinned": f"tools/workbench-validation/results/{run_id}/pinned/TC-01",
             "pinned_files": [{"path": f"tools/workbench-validation/results/{run_id}/pinned/TC-01/tests/test_x.py", "sha256": "deadbeef" * 8}]},
            {"id": "TC-P", "title": "protocol case", "wun": ["WUN-02"], "uut": ["demo"], "uut_versions": {},
             "endpoint": "none", "scope": "deployment", "method": "protocol", "status": "PASS", "exit_code": None,
             "duration_s": 0.0, "reason": "protocol executed", "log": None,
             "protocol": "docs/project/workbench-validation/protocols/TC-P.md",
             "execution_record": {"path": "tools/workbench-validation/protocols/TC-P.result.yml", "executed": "2026-01-01",
                                  "operator": "qe", "model_id": "m-1", "git_sha": "abc",
                                  "evidence": ["tools/workbench-validation/protocols/TC-P/run-1/findings.md"]},
             "pinned": None, "pinned_files": []},
        ],
    }
    (results / f"{run_id}.json").write_text(json.dumps(run))
    (results / "latest.json").write_text(json.dumps(run))
    return root, run_id


def run_cli(root: Path, *args: str):
    return subprocess.run([sys.executable, str(SCRIPT), "--root", str(root), *args],
                          capture_output=True, text=True)


def test_md_export_contains_every_section_and_evidence(tmp_path):
    root, run_id = make_root(tmp_path)
    proc = run_cli(root, "--run", run_id, "--format", "md")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    out = Path(proc.stdout.strip().splitlines()[-1])
    assert out == (root / "tools/workbench-validation/exports" / run_id / "validation-package.md").resolve()
    text = out.read_text()
    for heading in ("## Appendix A — Pinned validation manifest",
                    "## Appendix B — Environment record and deployment declaration",
                    "## Appendix C — Protocols",
                    "## Appendix D — Evidence logs",
                    "## Appendix E — Pinned test sources",
                    "## Appendix F — QMS template coverage inventory",
                    "## Sign-off", "## 1. Validation report"):
        assert heading in text, heading
    assert "| Validation lead |" in text and "| Quality |" in text and "| Operator |" in text
    assert "**Verdict: PASS**" in text
    assert "SECRET-LOG-MARKER" in text                 # evidence log verbatim
    assert "RECORD-MARKER: yes" in text                # execution record YAML
    assert "EVIDENCE-MARKER observed" in text          # run evidence file
    assert "Do the thing." in text                     # written protocol
    assert "deadbeef" * 8 in text                      # pinned sha256
    assert "user_needs:" in text                       # pinned manifest YAML
    assert "QMS template coverage" in text and "TMP-1" in text
    assert "Deployment declaration" in text and "`content.qms_forms`" in text
    assert "Historical run re-rendered" not in text    # schema 2.0 run, not historical


def test_latest_resolves_and_unknown_run_is_precondition(tmp_path):
    root, run_id = make_root(tmp_path)
    ok = run_cli(root, "--run", "latest", "--format", "md")
    assert ok.returncode == 0 and run_id in ok.stdout
    bad = run_cli(root, "--run", "run-19990101T000000Z", "--format", "md")
    assert bad.returncode == 2 and "run not found" in bad.stderr


def test_historical_note_and_missing_artifacts_are_stated(tmp_path):
    root, run_id = make_root(tmp_path)
    results = root / "tools/workbench-validation/results"
    run = json.loads((results / f"{run_id}.json").read_text())
    run["schema_version"] = "1.0"
    run["cases"][1]["status"] = "NOT-EXECUTED"
    run["cases"][1]["reason"] = "no record"
    run["cases"][1]["execution_record"] = None
    (root / "tools/workbench-validation/protocols/TC-P.result.yml").unlink()
    (results / f"{run_id}.json").write_text(json.dumps(run))
    proc = run_cli(root, "--run", run_id, "--format", "md")
    assert proc.returncode == 0, proc.stderr
    text = Path(proc.stdout.strip().splitlines()[-1]).read_text()
    assert "Historical run re-rendered by the current renderer" in text
    assert "No execution record — NOT-EXECUTED" in text
    assert "no log — NOT-EXECUTED" in text


def test_fence_grows_past_embedded_backticks():
    mod = _load()
    fenced = mod.fence("x\n````\ninner\n````\n", "text")
    assert fenced.startswith("`````text") and fenced.endswith("`````")


def _with_docflow(root: Path) -> bool:
    src = Path(__file__).resolve().parents[3] / "skills" / "docflow" / "scripts" / "export_formal.py"
    if not src.is_file():
        return False
    dest = root / ".claude/skills/docflow/scripts"
    dest.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest / "export_formal.py")
    return True


@pytest.mark.skipif(shutil.which("pandoc") is None, reason="pandoc not installed")
def test_docx_export_produces_file(tmp_path):
    root, run_id = make_root(tmp_path)
    if not _with_docflow(root):
        pytest.skip("docflow exporter not available")
    proc = run_cli(root, "--run", run_id, "--format", "docx")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    out = Path(proc.stdout.strip().splitlines()[-1])
    assert out.suffix == ".docx" and out.stat().st_size > 5000


@pytest.mark.skipif(shutil.which("pandoc") is None or shutil.which("soffice") is None,
                    reason="pandoc + soffice required for pdf")
def test_pdf_export_produces_file(tmp_path):
    root, run_id = make_root(tmp_path)
    if not _with_docflow(root):
        pytest.skip("docflow exporter not available")
    proc = run_cli(root, "--run", run_id, "--format", "pdf")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    out = Path(proc.stdout.strip().splitlines()[-1])
    assert out.suffix == ".pdf" and out.read_bytes()[:5] == b"%PDF-"


def test_missing_converter_is_precondition(tmp_path, monkeypatch):
    root, run_id = make_root(tmp_path)
    _with_docflow(root)
    mod = _load()
    monkeypatch.setattr(mod.shutil, "which", lambda name: None)
    code, err = mod.convert(root, root / "x.md", "docx", root / "x.docx", "t", "h")
    assert code == 2 and "pandoc" in err
