"""Capability tests for scan_tags.py — the harvest-tag lint shared by the
strategy and lessons harvesters. Fixtures under tests/fixtures/tags/."""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
FIX = HERE / "fixtures" / "tags"
SCRIPT = SKILL / "scripts" / "scan_tags.py"


def _load():
    spec = importlib.util.spec_from_file_location("scan_tags", SCRIPT)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_good_doc_has_two_blocks_and_no_findings():
    m = _load()
    ok, bad = m.scan_file(FIX / "good.md", ["regulatory", "testing"])
    assert ok == 2 and bad == []


def test_bad_doc_reports_every_malformed_variant():
    m = _load()
    ok, bad = m.scan_file(FIX / "bad.md", ["regulatory", "testing"])
    kinds = [b["kind"] for b in bad]
    assert ok == 0
    assert kinds.count("marker-text") == 4      # A hyphen, B case, C no space, I "LESSON LEARNED"
    assert "unknown-domain" in kinds             # D
    assert kinds.count("empty-tag") == 2         # E bare, F colon but no values
    assert "unclosed-comment" in kinds           # G
    assert "prose-on-line" in kinds              # H
    assert len(bad) == 9


def test_domain_keys_read_from_project_yml():
    m = _load()
    assert m.load_domain_keys(FIX) == ["regulatory", "testing"]


def test_cli_exit_codes_and_json(tmp_path):
    r = subprocess.run([sys.executable, str(SCRIPT), "--project-root", str(FIX), "--json", str(FIX / "good.md")],
                       capture_output=True, text=True)
    assert r.returncode == 0 and json.loads(r.stdout)["malformed"] == 0
    r = subprocess.run([sys.executable, str(SCRIPT), "--project-root", str(FIX), "--json", str(FIX / "bad.md")],
                       capture_output=True, text=True)
    assert r.returncode == 1 and json.loads(r.stdout)["malformed"] == 9
    r = subprocess.run([sys.executable, str(SCRIPT), "--project-root", str(tmp_path)], capture_output=True, text=True)
    assert r.returncode == 2
