"""Capability tests for usage-metrics `aggregate.py` (WUN-23: spend lands on
the task that was active; unmeasured slots are null, never zero; the
aggregation is idempotent).

Builds a synthetic project: two teammates, one month, two per-session
records — one written by the current collector (carries `user_turns` and a
`by_task` split), one pre-schema (no `user_turns`) — then runs the real
aggregator and reads `usage.json`. `collect.py` needs a live session
transcript and an activation ledger; that half is not faked here (the
transcript format is the harness's), so attribution is tested from the
per-session record onward, which is the seam `aggregate.py` owns.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "aggregate.py"

PROJECT_YML = """\
project:
  name: Fixture Project
team:
  active:
    - name: Alice Example
      github: alice
      task_folder: alice
      email: alice@example.com
    - name: Bob Example
      github: bob
      task_folder: bob
      email: bob@example.com
usage_metrics:
  output_dir: tools/usage-metrics
"""

MODEL = "claude-example-1"


def _stats(inp, out, msgs):
    return {"input": inp, "output": out, "cache_read": 0, "cache_creation": 0, "messages": msgs}


def _fixture(tmp: Path) -> Path:
    proj = tmp / "proj"
    (proj / "tasks" / "alice" / "_usage-metrics" / "2026-05").mkdir(parents=True)
    (proj / "tasks" / "bob" / "_usage-metrics" / "2026-05").mkdir(parents=True)
    (proj / "project.yml").write_text(PROJECT_YML)
    (proj / "tasks" / "alice" / "101-example.md").write_text("# 101 — Example\n\n## Changelog\n- 2026-05-02: x\n")
    (proj / "tasks" / "bob" / "202-other.md").write_text("# 202 — Other\n\n## Changelog\n- 2026-05-03: y\n")
    # Current-schema record: 1000 in / 200 out, split 700/140 to task 101 and 300/60 unattributed.
    alice = {
        "session_id": "s1", "totals": _stats(1000, 200, 10),
        "by_model": {MODEL: _stats(1000, 200, 10)},
        "by_day": {"2026-05-02": _stats(1000, 200, 10)},
        "by_task": {"101": {MODEL: _stats(700, 140, 7)}, "_unattributed": {MODEL: _stats(300, 60, 3)}},
        "user_turns": {"total": 5, "by_task": {"101": 4, "_unattributed": 1}},
    }
    # Pre-schema record: no user_turns at all → must roll up as null, not 0.
    bob = {
        "session_id": "s2", "totals": _stats(500, 50, 4),
        "by_model": {MODEL: _stats(500, 50, 4)},
        "by_day": {"2026-05-03": _stats(500, 50, 4)},
        "by_task": {"202": {MODEL: _stats(500, 50, 4)}},
    }
    (proj / "tasks" / "alice" / "_usage-metrics" / "2026-05" / "s1.json").write_text(json.dumps(alice))
    (proj / "tasks" / "bob" / "_usage-metrics" / "2026-05" / "s2.json").write_text(json.dumps(bob))
    return proj


def _aggregate(proj: Path) -> dict:
    r = subprocess.run([sys.executable, str(SCRIPT), "--project-root", str(proj), "--quiet"],
                       capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, r.stdout + r.stderr
    return json.loads((proj / "tools" / "usage-metrics" / "usage.json").read_text())


def test_spend_is_attributed_to_the_active_task(tmp_path):
    usage = _aggregate(_fixture(tmp_path))
    tasks = usage["tasks"]
    assert tasks["alice/101"]["totals"]["input"] == 700
    assert tasks["alice/101"]["totals"]["output"] == 140
    assert tasks["alice/_unattributed"]["totals"]["input"] == 300
    assert tasks["bob/202"]["totals"]["input"] == 500
    assert tasks["alice/101"]["user_turns"] == 4


def test_unmeasured_turns_are_null_not_zero(tmp_path):
    usage = _aggregate(_fixture(tmp_path))
    assert usage["tasks"]["bob/202"]["user_turns"] is None
    dumped = json.dumps(usage)
    assert '"user_turns": null' in dumped


def test_aggregation_is_idempotent(tmp_path):
    proj = _fixture(tmp_path)
    _aggregate(proj)
    first = (proj / "tools" / "usage-metrics" / "usage.json").read_bytes()
    _aggregate(proj)
    second = (proj / "tools" / "usage-metrics" / "usage.json").read_bytes()
    assert first == second
