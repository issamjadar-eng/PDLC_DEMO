"""Capability tests for scripts/ai_changelog_check.py against skill-shipped
fixtures under tests/fixtures/ai-changelog/. The vendor-name fixture is
assembled at runtime so no product name sits in the skill tree."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
SCRIPT = SKILL / "scripts" / "ai_changelog_check.py"
FIX = SKILL / "tests" / "fixtures" / "ai-changelog"


def _run(root, *args):
    proc = subprocess.run([sys.executable, str(SCRIPT), "--root", str(root), "--json", *args],
                          capture_output=True, text=True)
    data = json.loads(proc.stdout) if proc.stdout.strip().startswith("{") else None
    return proc.returncode, data, proc.stderr


def _one(data):
    assert data["documents"] == 1
    return data["results"][0]


def test_good_document_passes():
    code, data, err = _run(FIX, "good.md")
    assert code == 0, err
    r = _one(data)
    assert r["status"] == "pass" and r["block"] and "1 row" in r["block_detail"]


def test_missing_block_fails():
    code, data, _ = _run(FIX, "missing-block.md")
    assert code == 1 and any(f.startswith("BLOCK") for f in _one(data)["failures"])


def test_header_without_rows_fails():
    code, data, _ = _run(FIX, "header-no-rows.md")
    assert code == 1 and "no rows" in _one(data)["failures"][0]


def test_block_inside_details_is_placement_failure():
    code, data, _ = _run(FIX, "block-in-details.md")
    assert code == 1 and any(f.startswith("PLACEMENT") for f in _one(data)["failures"])


def test_vendor_name_in_body_fails(tmp_path):
    vendor = "Cla" + "ude"  # assembled so the literal never sits in the skill tree
    (tmp_path / "v.md").write_text(
        "<!-- AI-CHANGELOG\n| Date | Task | Summary |\n|---|---|---|\n| 2026-01-01 | 001 | ok |\n-->\n\n"
        f"# Doc\n\nDrafted by {vendor}.\n")
    code, data, _ = _run(tmp_path, "v.md")
    assert code == 1 and any(f.startswith("VENDOR:") for f in _one(data)["failures"])


def test_vendor_name_in_changelog_row_fails(tmp_path):
    vendor = "Anthro" + "pic"
    (tmp_path / "v.md").write_text(
        f"<!-- AI-CHANGELOG\n| Date | Task | Summary |\n|---|---|---|\n| 2026-01-01 | 001 | edited via {vendor} tool |\n-->\n\n# Doc\n\nBody.\n")
    code, data, _ = _run(tmp_path, "v.md")
    assert code == 1 and any(f.startswith("VENDOR:") for f in _one(data)["failures"])


def test_vendor_name_in_frontmatter_is_warning_unless_strict(tmp_path):
    method = "cla" + "ude-authored"
    (tmp_path / "v.md").write_text(
        f"---\nconversion_method: \"{method}\"\n---\n\n"
        "<!-- AI-CHANGELOG\n| Date | Task | Summary |\n|---|---|---|\n| 2026-01-01 | 001 | ok |\n-->\n\n# Doc\n\nBody.\n")
    code, data, _ = _run(tmp_path, "v.md")
    assert code == 0 and _one(data)["status"] == "warn"
    code, data, _ = _run(tmp_path, "--strict", "v.md")
    assert code == 1 and _one(data)["status"] == "fail"


def test_ai_authored_only_skips_block_requirement_for_human_files(tmp_path):
    (tmp_path / "h.md").write_text("---\nconversion_method: \"pandoc\"\n---\n\n# Doc\n\nBody.\n")
    code, data, _ = _run(tmp_path, "--ai-authored-only", "h.md")
    assert code == 0 and _one(data)["block_required"] is False
    code, data, _ = _run(tmp_path, "h.md")
    assert code == 1


def test_sanctioned_label_is_not_a_vendor_hit():
    code, data, _ = _run(FIX, "good.md")
    assert not any("VENDOR" in f for f in _one(data)["failures"] + _one(data)["warnings"])


def test_folder_walk_excludes_readme_and_formal(tmp_path):
    (tmp_path / "formal").mkdir()
    (tmp_path / "formal" / "x.md").write_text("# no block\n")
    (tmp_path / "README.md").write_text("# readme\n")
    (tmp_path / "a.md").write_text("# no block\n")
    code, data, _ = _run(tmp_path, ".")
    assert data["documents"] == 1 and code == 1


def test_bad_path_is_usage_error(tmp_path):
    code, _, err = _run(tmp_path, "nope.md")
    assert code == 2 and "not found" in err
