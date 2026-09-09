"""Evidence for WUN-29 — "keep a frozen controlled document frozen".

THIS TEST IS EXPECTED TO FAIL TODAY. `hooks/pre_tool_use_frozen.py` is a
documented stub that exits 0 for every edit; the design (block Edit/Write on
a document whose frontmatter carries `state: frozen`, emit a briefing,
require typed consent) is not implemented. The failing test is the honest
validation evidence for the need — do not mark it xfail; implement the hook.

Marked `freeze_gate` so the workbench validation can run it as its own case
(`-m freeze_gate`) and keep it out of the change-control suite case
(`-m 'not freeze_gate'`). Payload shape follows the PreToolUse hook protocol
used by `.claude/hooks/check-active-task.sh`: JSON on stdin with
`tool_name`, `tool_input.file_path`, `session_id`; a block is exit code 2
or a `hookSpecificOutput.permissionDecision: deny` JSON on stdout.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

HOOK = Path(__file__).resolve().parents[1] / "hooks" / "pre_tool_use_frozen.py"

pytestmark = pytest.mark.freeze_gate


def _run_hook(project: Path, target: Path) -> tuple[int, dict | None]:
    payload = {"session_id": "test-session", "tool_name": "Edit", "cwd": str(project),
               "tool_input": {"file_path": str(target), "old_string": "a", "new_string": "b"}}
    r = subprocess.run([sys.executable, str(HOOK)], input=json.dumps(payload), cwd=project,
                       capture_output=True, text=True, timeout=30)
    out = None
    try:
        out = json.loads(r.stdout) if r.stdout.strip() else None
    except json.JSONDecodeError:
        out = None
    return r.returncode, out


def _is_deny(code: int, out: dict | None) -> bool:
    if code == 2:
        return True
    dec = ((out or {}).get("hookSpecificOutput") or {}).get("permissionDecision")
    return dec == "deny"


def _doc(project: Path, state: str) -> Path:
    d = project / "docs" / "controlled"
    d.mkdir(parents=True, exist_ok=True)
    f = d / "sop.md"
    f.write_text(f"---\ntitle: SOP\nstate: {state}\n---\n\n# SOP\n\nbody\n", encoding="utf-8")
    return f


def test_frozen_document_edit_is_denied(tmp_path):
    target = _doc(tmp_path, "frozen")
    code, out = _run_hook(tmp_path, target)
    assert _is_deny(code, out), (
        f"edit of a `state: frozen` document was ALLOWED (exit {code}, stdout {out!r}) — "
        "hooks/pre_tool_use_frozen.py is still the stub; WUN-29 has no enforcement")


def test_unfrozen_document_edit_is_allowed(tmp_path):
    target = _doc(tmp_path, "draft")
    code, out = _run_hook(tmp_path, target)
    assert not _is_deny(code, out) and code == 0
