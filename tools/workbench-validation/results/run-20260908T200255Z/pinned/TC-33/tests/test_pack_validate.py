"""Capability tests for the knowledge-pack validator (`build_pack.py validate`).

Builds a synthetic repo (two markdown sources + a pack manifest) in a temp dir:
validate passes (exit 0); a slot whose source pattern matches no file fails
(exit 1); more slots than the target's file cap fails (exit 1). Hermetic —
`--repo` points at the temp tree, so nothing in this project is read.

    uv run --no-project --with pytest --with pyyaml -- pytest .claude/skills/knowledge-pack-export/tests -q
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import yaml

SKILL = Path(__file__).resolve().parents[1]
BUILD = SKILL / "scripts" / "build_pack.py"


def _repo(tmp: Path, slots: list[dict]) -> tuple[Path, Path]:
    (tmp / "docs").mkdir()
    (tmp / "docs" / "a.md").write_text("# A\n\nAlpha content.\n")
    (tmp / "docs" / "b.md").write_text("# B\n\nBeta content.\n")
    manifest = tmp / "demo.pack.yml"
    manifest.write_text(yaml.safe_dump({
        "pack": {"slug": "demo", "title": "Demo pack", "targets": ["gemini-gem"],
                 "confidentiality": "test", "audience": "test", "persona": "test"},
        "slots": slots}))
    return tmp, manifest


def _validate(repo: Path, manifest: Path):
    proc = subprocess.run([sys.executable, str(BUILD), "validate", str(manifest), "--repo", str(repo)],
                          capture_output=True, text=True, timeout=60)
    return proc.returncode, proc.stdout + proc.stderr


def test_pack_with_present_sources_validates(tmp_path):
    repo, m = _repo(tmp_path, [{"file": "00-all.md", "title": "All", "sources": ["docs/a.md", "docs/b.md"],
                                "mode": "verbatim"}])
    rc, out = _validate(repo, m)
    assert rc == 0, out
    assert "RESULT: ok" in out


def test_missing_source_fails_validation(tmp_path):
    repo, m = _repo(tmp_path, [{"file": "00-all.md", "title": "All", "sources": ["docs/a.md", "docs/missing.md"],
                                "mode": "verbatim"}])
    rc, out = _validate(repo, m)
    assert rc == 1
    assert "pattern matched no files: docs/missing.md" in out and "1 missing-source problem" in out


def test_slot_overflow_fails_validation(tmp_path):
    slots = [{"file": f"{i:02d}.md", "title": f"S{i}", "sources": ["docs/a.md"], "mode": "verbatim"}
             for i in range(11)]  # gemini-gem cap is 10
    repo, m = _repo(tmp_path, slots)
    rc, out = _validate(repo, m)
    assert rc == 1 and "OVERFLOW" in out


def test_unknown_target_is_a_hard_error(tmp_path):
    repo, m = _repo(tmp_path, [{"file": "00.md", "title": "S", "sources": ["docs/a.md"], "mode": "verbatim"}])
    m.write_text(m.read_text().replace("gemini-gem", "no-such-target"))
    rc, out = _validate(repo, m)
    assert rc != 0 and "unknown target" in out
