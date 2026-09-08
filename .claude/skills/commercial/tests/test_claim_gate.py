"""Capability tests for the business-answer claim gate (`commercial.py lint`).

Builds a tiny synthetic domain tree + corpus in a temp dir: one question, one
edition whose report cites a pinned, fresh snapshot (lint passes, exit 0); then
proves the gate BLOCKS on (a) a numeric claim with no [src|assume|derived|config]
marker and (b) a pinned snapshot older than the dataset's freshness window with
no waiver. Hermetic; independent of this project's data state.

    uv run --no-project --with pytest --with pyyaml -- pytest .claude/skills/commercial/tests -q
"""
from __future__ import annotations

import datetime as dt
import json
import subprocess
import sys
from pathlib import Path

import yaml

SKILL = Path(__file__).resolve().parents[1]
ENGINE = SKILL / "scripts" / "commercial.py"
DS = "demo/sales"


def _build(tmp: Path, *, snapshot: str, max_age_days: int, report_line: str) -> tuple[Path, Path]:
    root, corpus = tmp / "domain", tmp / "corpus"
    (root / "reports" / "BQ-1" / "2026-09-01.1").mkdir(parents=True)
    (root / "commercial.yml").write_text(yaml.safe_dump({
        "questions": [{"id": "BQ-1", "category": "demo", "question": "How much revenue?",
                       "computation": "bq_modules/bq_1.py"}]}))
    ed = root / "reports" / "BQ-1" / "2026-09-01.1"
    (ed / "edition.yml").write_text(yaml.safe_dump({
        "bq": "BQ-1", "edition": "2026-09-01.1", "status": "draft",
        "created_at": "2026-09-01T00:00:00+00:00", "pins": {DS: snapshot}}))
    (ed / "data.json").write_text(json.dumps({
        "bq": "BQ-1",
        "series": [{"id": "rev", "label": "Revenue", "unit": "USD", "kind": "stat",
                    "evidence_class": "measured",
                    "provenance": {"dataset": DS, "snapshot": snapshot}}],
        "verdicts": []}))
    (ed / "report.md").write_text("# BQ-1 — Revenue\n\n" + report_line + "\n")
    d = corpus / DS
    (d / "snapshots" / snapshot).mkdir(parents=True)
    (d / "dataset.yml").write_text(yaml.safe_dump({"dataset": DS, "max_age_days": max_age_days}))
    (d / "latest").write_text(snapshot)
    return root, corpus


def _lint(root: Path, corpus: Path):
    proc = subprocess.run([sys.executable, str(ENGINE), "--root", str(root), "--corpus-root", str(corpus),
                           "lint", "BQ-1"], capture_output=True, text=True, timeout=60)
    return proc.returncode, proc.stdout + proc.stderr


FRESH = dt.date.today().isoformat()


def test_marked_fresh_claim_passes(tmp_path):
    root, corpus = _build(tmp_path, snapshot=FRESH, max_age_days=30,
                          report_line=f"Revenue was $5.0M [src: {DS}@{FRESH}] [derived: rev].")
    rc, out = _lint(root, corpus)
    assert rc == 0, out
    assert "0 error(s)" in out
    assert (root / "reports" / "BQ-1" / "2026-09-01.1" / "quality.json").exists()


def test_unmarked_numeric_claim_blocks(tmp_path):
    root, corpus = _build(tmp_path, snapshot=FRESH, max_age_days=30,
                          report_line="Revenue grew 12% year over year.")
    rc, out = _lint(root, corpus)
    assert rc == 1
    assert "numeric claim without a [src|assume|derived|config] marker" in out


def test_stale_pin_without_waiver_blocks(tmp_path):
    old = (dt.date.today() - dt.timedelta(days=400)).isoformat()
    root, corpus = _build(tmp_path, snapshot=old, max_age_days=30,
                          report_line=f"Revenue was $5.0M [src: {DS}@{old}].")
    rc, out = _lint(root, corpus)
    assert rc == 1
    assert "STALE" in out and "no [waived:" in out


def test_marker_citing_unpinned_dataset_blocks(tmp_path):
    root, corpus = _build(tmp_path, snapshot=FRESH, max_age_days=30,
                          report_line=f"Revenue was $5.0M [src: demo/other@{FRESH}].")
    rc, out = _lint(root, corpus)
    assert rc == 1 and "cites unpinned dataset" in out
