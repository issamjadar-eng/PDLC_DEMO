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


# ---- v12: 🔒 INTERNAL blockquote container, bulleted attachments, eSTAR shape -----

INTERNAL_BQ = (
    "> **🔒 INTERNAL — working status.** Document control v0.1 · status: draft.\n"
    "> `[VERIFY]` submitter and tracking-number fields before transmission.\n"
    "> TBD (owner: RA lead) — confirm meeting format.\n\n"
)


def _insert_after_h1(text: str, block: str) -> str:
    lines = text.split("\n")
    for i, ln in enumerate(lines):
        if ln.startswith("# "):
            return "\n".join(lines[: i + 1] + ["", block.rstrip("\n")] + lines[i + 1 :])
    raise AssertionError("no H1 in fixture cover letter")


def test_verify_inside_internal_blockquote_does_not_fire_s7(tmp_path):
    pkg = _pkg(tmp_path)
    cover = pkg / "cover-letter.md"
    cover.write_text(_insert_after_h1(cover.read_text(), INTERNAL_BQ), encoding="utf-8")
    rc, data, err = _run(CONSISTENCY, pkg)
    assert "S7" not in _checks(data), data
    assert rc == 0, (data, err)


def test_verify_in_filed_body_right_after_internal_blockquote_still_fires_s7(tmp_path):
    pkg = _pkg(tmp_path)
    cover = pkg / "cover-letter.md"
    text = _insert_after_h1(cover.read_text(), INTERNAL_BQ + "\nThe device weighs 2 kg `[VERIFY] mass`.\n")
    cover.write_text(text, encoding="utf-8")
    rc, data, err = _run(CONSISTENCY, pkg)
    assert "S7" in _checks(data), data
    assert rc == 2


def _bulleted_cover(pkg: Path) -> None:
    cover = pkg / "cover-letter.md"
    text = cover.read_text()
    head, _, _ = text.partition("## Attachments")
    text = head + (
        "## Attachments\n\n"
        "- Device description ([`device-description.md`](./device-description.md))\n"
        "- Questions for the Agency ([`fda-questions.md`](./fda-questions.md))\n"
    )
    # the fixture body says "Attachment 1, …" — no numbered list remains, so drop the prose number
    text = text.replace("Attachment 1, [Device description]", "The [Device description]")
    cover.write_text(text, encoding="utf-8")


def test_bulleted_attachment_list_resolves_attachments(tmp_path):
    pkg = _pkg(tmp_path)
    _bulleted_cover(pkg)
    rc, data, err = _run(CONSISTENCY, pkg)
    assert rc == 0, (data, err)
    # the device description is now a transmitted attachment → it appears in the support matrix
    assert data["support_matrix"] == {"Q1.1": ["device-description"]}, data


def test_verify_inside_bulleted_attachment_is_caught(tmp_path):
    pkg = _pkg(tmp_path)
    _bulleted_cover(pkg)
    dd = pkg / "device-description.md"
    dd.write_text(dd.read_text() + "\n\nThe pump delivers 0.5 mL/h `[VERIFY] flow rate`.\n", encoding="utf-8")
    rc, data, err = _run(CONSISTENCY, pkg)
    s7 = [f for f in data["findings"] if f["check"] == "S7"]
    assert s7 and s7[0]["file"] == "device-description.md", data
    assert rc == 2


def test_estar_shaped_folder_is_a_clear_precondition_error(tmp_path):
    pkg = tmp_path / "510k"
    pkg.mkdir()
    (pkg / "510k.submission.json").write_text("{}", encoding="utf-8")
    proc = subprocess.run([sys.executable, str(CONSISTENCY), str(pkg), "--transmit-gate", "--json"],
                          capture_output=True, text=True, timeout=60)
    assert proc.returncode == 2
    assert "eSTAR-shaped" in proc.stderr and "estar_lint.py" in proc.stderr
