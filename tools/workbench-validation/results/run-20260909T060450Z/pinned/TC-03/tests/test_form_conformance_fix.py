"""Capability tests for scripts/form_conformance_fix.py and
scripts/ai_changelog_backfill.py — run on temp copies of the skill-shipped fixtures."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

SKILL = Path(__file__).resolve().parents[1]
FIX_SCRIPT = SKILL / "scripts" / "form_conformance_fix.py"
CHECK_SCRIPT = SKILL / "scripts" / "form_conformance_check.py"
BACKFILL = SKILL / "scripts" / "ai_changelog_backfill.py"
AC_CHECK = SKILL / "scripts" / "ai_changelog_check.py"
FIX = SKILL / "tests" / "fixtures" / "form-conformance"
AC_FIX = SKILL / "tests" / "fixtures" / "ai-changelog"


def _run(script, root, *args):
    proc = subprocess.run([sys.executable, str(script), "--root", str(root), "--json", *args],
                          capture_output=True, text=True)
    data = json.loads(proc.stdout) if proc.stdout.strip().startswith("{") else None
    return proc.returncode, data, proc.stderr


@pytest.fixture
def tree(tmp_path):
    dst = tmp_path / "proj"
    shutil.copytree(FIX, dst)
    return dst


def test_dry_run_plans_but_does_not_write(tree):
    before = (tree / "docs/project/_mirror/widget/fmea/v1.0.0.md").read_text()
    code, data, _ = _run(FIX_SCRIPT, tree, "docs/project")
    assert code == 1 and data["summary"]["documents_to_fix"] == 1 and data["summary"]["applied"] == 0
    plan = data["plans"][0]
    assert plan["template_id"] == "FORM-000000002"
    assert plan["inserted"] == ["revision history"] and set(plan["reused"]) == {"identification", "scoring basis", "fmea table"}
    assert plan["content_preserved"] is True
    assert (tree / "docs/project/_mirror/widget/fmea/v1.0.0.md").read_text() == before


def test_apply_makes_document_conform_and_preserves_content(tree):
    doc = tree / "docs/project/_mirror/widget/fmea/v1.0.0.md"
    doc.write_text("# FMEA — Widget\n\nintro line\n\n## Identification\nid body\n## FMEA Table\n| a | b |\n## Scoring Basis\nscore body\n## Local Extra\nkeep me\n")
    code, data, _ = _run(FIX_SCRIPT, tree, "--apply", "docs/project/_mirror/widget/fmea")
    assert code == 0 and data["summary"]["applied"] == 1
    text = doc.read_text()
    # template order: identification, scoring basis, fmea table, revision history;
    # the extra section with content is retained under ONE demoted appendix
    heads = [ln for ln in text.splitlines() if ln.startswith("## ")]
    assert heads == ["## Identification", "## Scoring Basis", "## FMEA Table", "## Revision History",
                     "## Appendix — Sections retained from the previous structure"]
    assert "### Local Extra\nkeep me" in text and "\n## Local Extra" not in text
    for kept in ("intro line", "id body", "| a | b |", "score body", "keep me"):
        assert kept in text
    assert "_[TBD — section required by FORM-000000002; content to be authored.]_" in text
    assert data["plans"][0]["appended"] == ["local extra"] and data["plans"][0]["dropped_empty_skeleton"] == []
    # the checker treats the appendix as an EXTRA section: warning, never failure
    code, data, _ = _run(CHECK_SCRIPT, tree, "docs/project/_mirror/widget/fmea")
    assert code == 0 and data["results"][0]["status"] == "warn"
    assert data["results"][0]["extra"] == ["appendix — sections retained from the previous structure"]


def test_numbered_reused_sections_follow_template_numbering_and_skeletons_are_dropped(tree):
    """The first-pass defect: a reused section kept its old number (`## 4. Approvals`
    at template slot 12) and skeleton extras were appended verbatim, so numbering
    restarted. Reused sections are re-headed to the template text; empty template
    skeletons (placeholders, empty table rows) are dropped, not appended."""
    doc = tree / "docs/project/_mirror/widget/fmea/v1.0.0.md"
    doc.write_text(
        "# FMEA — Widget\n\n"
        "## 3. FMEA Table\n| a | b |\n"
        "## 4. Revision History\n| Rev | Date |\n|---|---|\n| 0.1 | 2026-01-01 |\n"
        "## 1. Identification\n| Field | Value |\n|---|---|\n| Owner | `{{NAME}}` |\n"
        "## 2. Contents\n\n`{{Fill per template}}`\n"
        "## 9. Notes\n\nreal note that must survive\n"
    )
    code, data, _ = _run(FIX_SCRIPT, tree, "--apply", "docs/project/_mirror/widget/fmea")
    assert code == 0, data
    plan = data["plans"][0]
    text = doc.read_text()
    heads = [ln for ln in text.splitlines() if ln.startswith("## ")]
    assert heads == ["## Identification", "## Scoring Basis", "## FMEA Table", "## Revision History",
                     "## Appendix — Sections retained from the previous structure"]
    # reused sections re-headed to the template's heading text (numbering follows the template)
    assert {r["from"] for r in plan["reheaded"]} == {"3. FMEA Table", "4. Revision History", "1. Identification"}
    # "2. Contents" is a pure placeholder skeleton → dropped; "9. Notes" has content → retained, number stripped
    assert plan["dropped_empty_skeleton"] == ["contents"] and plan["appended"] == ["notes"]
    assert "### Notes\n\nreal note that must survive" in text and "{{Fill per template}}" not in text
    assert "| 0.1 | 2026-01-01 |" in text and "| Owner | `{{NAME}}` |" in text  # reused bodies untouched
    nums = [int(h.split()[1].rstrip(".")) for h in heads if h.split()[1].rstrip(".").isdigit()]
    assert nums == sorted(nums)


def test_second_run_is_a_noop_and_appendix_is_not_nested(tree):
    doc = tree / "docs/project/_mirror/widget/fmea/v1.0.0.md"
    doc.write_text("# FMEA — Widget\n\n## Identification\nid\n## FMEA Table\n| a | b |\n## Scoring Basis\ns\n"
                   "## Local Extra\nkeep me\n### Sub of extra\nsub body\n")
    code, data, _ = _run(FIX_SCRIPT, tree, "--apply", "docs/project/_mirror/widget/fmea")
    assert code == 0 and data["summary"]["applied"] == 1
    once = doc.read_text()
    assert "### Local Extra\nkeep me\n#### Sub of extra\nsub body" in once
    code, data, _ = _run(FIX_SCRIPT, tree, "--apply", "docs/project/_mirror/widget/fmea")
    assert code == 0 and data["summary"]["documents_to_fix"] == 0 and data["summary"]["applied"] == 0
    assert doc.read_text() == once
    assert once.count("## Appendix — Sections retained from the previous structure") == 1


def test_reshape_of_first_pass_output_and_provenance_row(tree):
    """A document shaped by the first pass (template sections + verbatim extras with
    restarted numbering, an AI-CHANGELOG block) is re-shaped; the appendix replaces
    the loose extras and one provenance row is appended to the existing block."""
    doc = tree / "docs/project/_mirror/widget/fmea/v1.0.0.md"
    doc.write_text(
        "<!-- AI-CHANGELOG — internal provenance\n| Date | Task | Summary |\n|---|---|---|\n"
        "| 2026-09-08 | t/1 | Provenance block added retroactively |\n-->\n"
        "# FMEA — Widget\n\n"
        "## Identification\n\n_[TBD — section required by FORM-000000002; content to be authored.]_\n\n"
        "## Scoring Basis\n\nscore body\n\n## FMEA Table\n\n| a | b |\n\n## Revision History\n\n"
        "| Rev | Date |\n|---|---|\n| 0.1 | 2026-01-01 |\n\n"
        "## 1. Document Identification\n| Field | Value |\n|---|---|\n| Owner | `{{NAME}}` |\n\n"
        "## 2. Rationale\n\nwhy we did it\n"
    )
    # checker says warn (extras) — the fixer picks it up because of its own footprint
    code, data, _ = _run(FIX_SCRIPT, tree, "--apply", "--provenance-row", "t/2", "--date", "2026-09-09",
                         "docs/project/_mirror/widget/fmea")
    assert code == 0 and data["summary"]["applied"] == 1, data
    plan = data["plans"][0]
    assert plan["status_before"] == "warn"
    assert plan["dropped_empty_skeleton"] == ["document identification"] and plan["appended"] == ["rationale"]
    text = doc.read_text()
    assert text.count("<!-- AI-CHANGELOG") == 1 and "| 2026-09-09 | t/2 |" in text
    heads = [ln for ln in text.splitlines() if ln.startswith("## ")]
    assert heads[-1] == "## Appendix — Sections retained from the previous structure" and "### Rationale" in text
    assert "## 1. Document Identification" not in text and "why we did it" in text
    # an untouched warn document (no fixer footprint) is left alone
    doc.write_text("# FMEA — Widget\n\n## Identification\nid\n## Scoring Basis\ns\n## FMEA Table\n| a | b |\n"
                   "## Revision History\nr\n## Local Extra\nkeep\n")
    code, data, _ = _run(FIX_SCRIPT, tree, "--apply", "docs/project/_mirror/widget/fmea")
    assert code == 0 and data["summary"]["documents_to_fix"] == 0


def test_rename_aliases_reheads_matched_section(tree):
    doc = tree / "docs/project/_mirror/widget/fmea/v1.0.0.md"
    doc.write_text("# FMEA — Widget\n\n## Identification\n## FMEA Table\n## Scoring Basis\n## History\nold rows\n")
    code, data, _ = _run(FIX_SCRIPT, tree, "--apply", "--alias", "History=Revision History", "--rename-aliases",
                         "docs/project/_mirror/widget/fmea")
    assert code == 0 and data["plans"][0]["renamed"] == [{"from": "History", "to": "Revision History"}]
    text = doc.read_text()
    assert "## Revision History\nold rows" in text and "## History" not in text
    code, data, _ = _run(CHECK_SCRIPT, tree, "docs/project/_mirror/widget/fmea")
    assert code == 0 and data["results"][0]["status"] == "pass"


def test_frontmatter_and_preamble_are_byte_preserved(tree):
    doc = tree / "docs/project/_mirror/widget/fmea/v1.0.0.md"
    original = "---\ndoc_id: X\n---\n<!-- meta zone -->\n# FMEA — Widget\n\n> banner\n\n## Identification\n## FMEA Table\n## Scoring Basis\n"
    doc.write_text(original)
    _run(FIX_SCRIPT, tree, "--apply", "docs/project/_mirror/widget/fmea")
    text = doc.read_text()
    assert text.startswith("---\ndoc_id: X\n---\n<!-- meta zone -->\n# FMEA — Widget\n\n> banner\n\n")


def test_procedure_and_no_form_documents_are_untouched(tree):
    code, data, _ = _run(FIX_SCRIPT, tree, "docs/project/flat")
    assert code == 0 and data["summary"]["documents_to_fix"] == 0


# ---- backfill ---------------------------------------------------------------

@pytest.fixture
def ac_tree(tmp_path):
    dst = tmp_path / "ac"
    shutil.copytree(AC_FIX, dst)
    return dst


def test_backfill_adds_block_in_metadata_zone_and_checker_passes(ac_tree):
    code, data, _ = _run(BACKFILL, ac_tree, "--all", "--task", "t/1", "--date", "2026-09-08", "missing-block.md")
    assert code == 1 and data["summary"]["blocks_added"] == 1
    code, data, _ = _run(BACKFILL, ac_tree, "--all", "--apply", "--task", "t/1", "--date", "2026-09-08", "missing-block.md")
    assert code == 0 and data["summary"]["applied"] == 1
    text = (ac_tree / "missing-block.md").read_text()
    assert "<!-- AI-CHANGELOG" in text and "| 2026-09-08 | t/1" in text
    # block sits before the first rendered line
    first_render = next(i for i, ln in enumerate(text.splitlines()) if ln.startswith("# "))
    assert text.splitlines().index("<!-- AI-CHANGELOG — internal provenance of AI-assisted edits. Metadata only:") < first_render
    code, data, _ = _run(AC_CHECK, ac_tree, "missing-block.md")
    assert code == 0 and data["results"][0]["status"] in ("pass", "warn")


def test_backfill_is_idempotent_on_good_document(ac_tree):
    before = (ac_tree / "good.md").read_text()
    code, data, _ = _run(BACKFILL, ac_tree, "--all", "--apply", "good.md")
    assert code == 0 and data["summary"]["documents_to_fix"] == 0
    assert (ac_tree / "good.md").read_text() == before


def test_fix_vendor_neutralises_product_names_in_body_only(ac_tree):
    doc = ac_tree / "vendor.md"
    name = "Cla" + "ude"  # assembled so the fixture tree never carries the literal
    doc.write_text(f"---\nconversion_method: \"{name.lower()}-authored\"\n---\n<!-- AI-CHANGELOG\n| Date | Task | Summary |\n|---|---|---|\n| 2026-01-01 | t | x |\n-->\n# T\n\n| 2026-01-01 | {name} (first-stab) | scaffold |\n")
    code, data, _ = _run(BACKFILL, ac_tree, "--all", "--apply", "--fix-vendor", "vendor.md")
    assert code == 0 and data["summary"]["vendor_lines_fixed"] == 1
    text = doc.read_text()
    assert "AI assistant (first-stab)" in text and f"{name} (first-stab)" not in text
    assert f'conversion_method: "{name.lower()}-authored"' in text  # frontmatter untouched
