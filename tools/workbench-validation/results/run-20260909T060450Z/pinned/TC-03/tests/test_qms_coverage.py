"""Capability tests for scripts/qms_coverage.py over the form-conformance fixture project."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
SCRIPT = SKILL / "scripts" / "qms_coverage.py"
FIX = SKILL / "tests" / "fixtures" / "form-conformance"


def _run(tmp_path, *args):
    out = tmp_path / "cov.json"
    proc = subprocess.run([sys.executable, str(SCRIPT), "--root", str(FIX), "--json-out", str(out), *args],
                          capture_output=True, text=True)
    data = json.loads(out.read_text()) if out.is_file() else None
    return proc.returncode, data, proc.stdout, proc.stderr


def test_inventory_contract_and_counts(tmp_path):
    code, inv, out, err = _run(tmp_path, "docs/project")
    assert code == 0, err
    assert set(inv) == {"generated", "registry", "templates", "procedures", "documents_without_template", "summary"}
    t = {x["id"]: x for x in inv["templates"]}
    assert t["FORM-000000001"]["instances"] == 2 and t["FORM-000000001"]["tested"] and t["FORM-000000001"]["status"] == "covered"
    assert t["FORM-000000002"]["instances"] == 1 and t["FORM-000000002"]["fail"] == 1 and t["FORM-000000002"]["status"] == "covered-failing"
    p = {x["id"]: x for x in inv["procedures"]}
    assert p["SOP-000000001"]["doc_type"] == "SOP" and p["SOP-000000001"]["referenced_by"] == 1
    reasons = {d["doc"].split("/")[-1] if not d["doc"].endswith("v1.0.0.md") else d["doc"].split("/")[-2]: d["reason"]
               for d in inv["documents_without_template"]}
    assert reasons["notes"].startswith("intentionally none")
    assert reasons["orphan.md"] == "no template imported"
    s = inv["summary"]
    assert s["templates_total"] == 2 and s["templates_instantiated"] == 2 and s["templates_tested"] == 2
    assert s["templates_unused"] == 0 and s["templates_failing"] == 1 and s["procedures_total"] == 1
    assert s["documents_total"] == 6 and s["documents_governed"] == 3 and s["documents_without_template"] == 2
    assert "FORM-000000002" in out and "covered-failing" in out


def test_unused_template_is_reported_and_does_not_fail(tmp_path):
    # only the hazard-analysis instance → FMEA template imported but unused
    code, inv, _, _ = _run(tmp_path, "docs/project/_mirror/widget/hazard-analysis")
    assert code == 0
    t = {x["id"]: x for x in inv["templates"]}
    assert t["FORM-000000002"]["status"] == "unused" and inv["summary"]["templates_unused"] == 1


def test_reuses_conformance_report_when_given(tmp_path):
    rep = tmp_path / "fc.json"
    proc = subprocess.run([sys.executable, str(SKILL / "scripts" / "form_conformance_check.py"), "--root", str(FIX),
                           "--json", "docs/project"], capture_output=True, text=True)
    rep.write_text(proc.stdout)
    code, inv, _, _ = _run(tmp_path, "--conformance-json", str(rep))
    assert code == 0 and inv["summary"]["documents_total"] == 6


def test_missing_registry_is_precondition_error(tmp_path):
    proc = subprocess.run([sys.executable, str(SCRIPT), "--root", str(tmp_path), "--json-out", str(tmp_path / "x.json")],
                          capture_output=True, text=True)
    assert proc.returncode == 2 and "registry" in proc.stderr
