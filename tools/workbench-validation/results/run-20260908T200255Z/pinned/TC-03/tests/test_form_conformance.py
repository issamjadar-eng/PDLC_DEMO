"""Capability tests for scripts/form_conformance_check.py — run against the
skill-shipped fixture project under tests/fixtures/form-conformance/."""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
SCRIPT = SKILL / "scripts" / "form_conformance_check.py"
FIX = SKILL / "tests" / "fixtures" / "form-conformance"


def _load():
    spec = importlib.util.spec_from_file_location("fcc", SCRIPT)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _run(*args):
    proc = subprocess.run([sys.executable, str(SCRIPT), "--root", str(FIX), "--json", *args],
                          capture_output=True, text=True)
    data = json.loads(proc.stdout) if proc.stdout.strip().startswith("{") else None
    return proc.returncode, data, proc.stderr


def _by_doc(data):
    return {r["doc"].split("/")[-2] if r["doc"].endswith("v1.0.0.md") else Path(r["doc"]).stem: r
            for r in data["results"]}


def test_normalize_heading_strips_numbering_and_case():
    m = _load()
    assert m.normalize_heading("2. Hazard Analysis Table:") == "hazard analysis table"
    assert m.normalize_heading("  Revision   History ") == "revision history"


def test_level2_sections_ignore_comments_and_fences():
    m = _load()
    text = "<!-- ## hidden -->\n# T\n## A\n```\n## not a heading\n```\n### deeper\n## B\n"
    assert m.level2_sections(text) == ["a", "b"]


def test_taxonomy_resolved_doc_passes_with_extra_section_as_warning():
    code, data, err = _run("docs/project/_mirror/widget/hazard-analysis")
    assert code == 0, err
    r = data["results"][0]
    assert r["resolved_via"] == "taxonomy" and r["form"].endswith("Hazard Analysis Worksheet.md")
    assert r["status"] == "warn" and r["extra"] == ["approvals"] and not r["missing"] and r["order_ok"]


def test_strict_turns_extra_into_failure():
    code, data, _ = _run("--strict", "docs/project/_mirror/widget/hazard-analysis")
    assert code == 1 and data["results"][0]["status"] == "fail"


def test_missing_and_out_of_order_sections_fail():
    code, data, _ = _run("docs/project/_mirror/widget/fmea")
    assert code == 1
    r = data["results"][0]
    assert r["status"] == "fail" and r["missing"] == ["revision history"] and r["order_ok"] is False


def test_intentional_null_form_is_informational():
    code, data, _ = _run("docs/project/_mirror/widget/notes")
    assert code == 0 and data["results"][0]["status"] == "no-form"
    assert "intentionally" in data["results"][0]["detail"]


def test_frontmatter_parent_template_resolves_via_qms_index():
    code, data, _ = _run("docs/project/flat/instance-via-frontmatter.md")
    assert code == 0
    r = data["results"][0]
    assert r["resolved_via"] == "frontmatter" and r["status"] == "pass"


def test_orphan_doc_is_no_form_not_failure():
    code, data, _ = _run("docs/project/flat/orphan.md")
    assert code == 0 and data["results"][0]["status"] == "no-form"


def test_alias_accepts_renamed_heading():
    # --alias DOC=FORM: the document's "Scoring Basis" is accepted as the form's
    # "Revision History", so only "scoring basis" remains missing and the shared
    # order (identification, fmea table, revision history) now matches the form.
    code, data, _ = _run("--alias", "Scoring Basis=Revision History", "docs/project/_mirror/widget/fmea")
    r = data["results"][0]
    assert r["missing"] == ["scoring basis"] and r["order_ok"] is True and code == 1


def test_folder_walk_covers_whole_fixture_tree():
    code, data, _ = _run("docs/project")
    assert code == 1
    assert data["documents"] == 5
    assert data["summary"]["fail"] == 1 and data["summary"]["no-form"] == 2


def test_explicit_form_overrides_resolution():
    code, data, _ = _run("--form", "docs/internal/source-md/quality/templates/fmea-worksheet.md",
                         "docs/project/flat/instance-via-frontmatter.md")
    assert code == 1 and data["results"][0]["resolved_via"] == "explicit"


def test_bad_path_is_usage_error():
    code, _, err = _run("docs/does-not-exist")
    assert code == 2 and "not found" in err
