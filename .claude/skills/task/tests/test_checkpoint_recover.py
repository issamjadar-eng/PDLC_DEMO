"""Capability tests for the SessionStart checkpoint-recovery hook
(`.claude/hooks/checkpoint-recover.sh`, paired with the task skill's
`checkpoint` action). The hook honours CLAUDE_PROJECT_DIR, so each test
points it at a temp project: with a planted `.state/uncheckpointed-*.txt`
marker it must surface the task and its doc path; without one it must stay
silent and exit 0."""
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[4]   # tests → task → skills → .claude → repo root
HOOK = ROOT / ".claude" / "hooks" / "checkpoint-recover.sh"


def _run(project: Path) -> subprocess.CompletedProcess:
    if not HOOK.is_file() or shutil.which("bash") is None:
        pytest.skip("checkpoint-recover.sh not present")
    env = dict(os.environ, CLAUDE_PROJECT_DIR=str(project))
    return subprocess.run(["bash", str(HOOK)], cwd=project, env=env, capture_output=True, text=True, timeout=30)


def test_planted_marker_is_surfaced(tmp_path):
    (tmp_path / ".state").mkdir()
    (tmp_path / "tasks" / "tp").mkdir(parents=True)
    (tmp_path / "tasks" / "tp" / "007-example.md").write_text("# 007 — Example\n")
    (tmp_path / ".state" / "uncheckpointed-tp-007-2026-01-01.txt").write_text(
        "task_id: tp/007\nsession_ended: 2026-01-01T00:00:00Z\n"
        f"task_doc: {tmp_path / 'tasks' / 'tp' / '007-example.md'}\n")
    r = _run(tmp_path)
    assert r.returncode == 0
    assert "007" in r.stdout and "uncheckpointed" in r.stdout.lower()


def test_no_marker_is_silent(tmp_path):
    (tmp_path / ".state").mkdir()
    r = _run(tmp_path)
    assert r.returncode == 0 and r.stdout.strip() == ""


def test_no_state_dir_is_silent(tmp_path):
    r = _run(tmp_path)
    assert r.returncode == 0 and r.stdout.strip() == ""
