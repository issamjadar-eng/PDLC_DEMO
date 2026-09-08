"""Capability tests for the submission-package transmit gates.

Runs `check_package_consistency.py --transmit-gate` and `qsub_scope_lint.py
--transmit-gate` over a minimal synthetic filing package shipped in
tests/fixtures/package/ (positive), then mutates copies of it to prove the gates
BLOCK: an attachment-numbering inconsistency (S2), an unresolved [VERIFY] tag in a
filed body (S7), and a manifest/cover-letter misalignment (C4). Hermetic; exit-code
contract: 0 clean / 1 advisory findings / 2 blocking findings under --transmit-gate.

    uv run --no-project --with pytest --with pyyaml -- pytest .claude/skills/submissions/tests -q
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
FIXTURE = SKILL / "tests" / "fixtures" / "package"
CONSISTENCY = SKILL / "scripts" / "check_package_consistency.py"
SCOPE = SKILL / "scripts" / "qsub_scope_lint.py"


def _pkg(tmp_path: Path) -> Path:
    dst = tmp_path / "pkg"
    shutil.copytree(FIXTURE, dst)
    return dst


def _run(script: Path, pkg: Path, *extra: str):
    proc = subprocess.run([sys.executable, str(script), str(pkg), "--transmit-gate", "--json", *extra],
                          capture_output=True, text=True, timeout=60)
    body = proc.stdout[proc.stdout.index("{"):] if "{" in proc.stdout else "{}"
    return proc.returncode, json.loads(body), proc.stderr


def _checks(data: dict) -> set:
    return {f["check"] for f in data.get("findings", [])}


# ---- positive: the clean fixture passes both gates ---------------------------

def test_clean_package_passes_consistency_gate(tmp_path):
    rc, data, err = _run(CONSISTENCY, _pkg(tmp_path))
    assert rc == 0, (data, err)
    assert data["fails"] == 0 and data["warns"] == 0
    assert data["support_matrix"] == {"Q1.1": ["device-description"]}


def test_clean_package_passes_scope_lint(tmp_path):
    rc, data, err = _run(SCOPE, _pkg(tmp_path))
    assert rc == 0, (data, err)
    assert data["blocks"] == 0 and data["warns"] == 0


# ---- negatives: the gates block --------------------------------------------

def test_attachment_number_mismatch_blocks_transmission(tmp_path):
    pkg = _pkg(tmp_path)
    cover = pkg / "cover-letter.md"
    cover.write_text(cover.read_text().replace(
        "Attachment 1, [Device description]", "Attachment 2, [Device description]"))
    rc, data, _ = _run(CONSISTENCY, pkg)
    assert rc == 2 and data["fails"] >= 1
    assert "S2" in _checks(data)


def test_unresolved_verify_tag_in_filed_body_blocks_transmission(tmp_path):
    pkg = _pkg(tmp_path)
    dd = pkg / "device-description.md"
    dd.write_text(dd.read_text().replace(
        "adult inpatients.", "adult inpatients with a flow range of 0.1–99 mL/h [VERIFY: spec table]."))
    rc, data, _ = _run(CONSISTENCY, pkg)
    assert rc == 2
    s7 = [f for f in data["findings"] if f["check"] == "S7"]
    assert len(s7) == 1 and s7[0]["file"] == "device-description.md" and s7[0]["sev"] == "FAIL"


def test_verify_tag_inside_internal_apparatus_does_not_fire(tmp_path):
    # the fixture already carries a [VERIFY] inside a <details> internal container
    rc, data, _ = _run(CONSISTENCY, _pkg(tmp_path))
    assert rc == 0 and "S7" not in _checks(data)


def test_manifest_transmitted_piece_missing_from_cover_blocks(tmp_path):
    pkg = _pkg(tmp_path)
    man = pkg / "composition-manifest.md"
    man.write_text(man.read_text().replace(
        "## Excluded Pieces",
        "| Predicate table | [`predicate-table.md`](./predicate-table.md) | Comparison | Q1.1 |\n\n## Excluded Pieces"))
    (pkg / "predicate-table.md").write_text("# Predicate table\n\nSupports Q1.1.\n")
    rc, data, _ = _run(SCOPE, pkg)
    assert rc == 2 and data["blocks"] >= 1
    assert any(f["check"] == "C4" and "predicate-table" in f["msg"] for f in data["findings"])


def test_missing_cover_letter_is_a_precondition_error_not_a_pass(tmp_path):
    pkg = _pkg(tmp_path)
    (pkg / "cover-letter.md").unlink()
    proc = subprocess.run([sys.executable, str(CONSISTENCY), str(pkg), "--transmit-gate"],
                          capture_output=True, text=True, timeout=60)
    assert proc.returncode == 2 and "cover letter not found" in proc.stderr
