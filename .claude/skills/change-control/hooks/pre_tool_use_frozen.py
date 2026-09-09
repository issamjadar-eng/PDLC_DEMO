#!/usr/bin/env python3
"""
PreToolUse hook — blocks Edit/Write/NotebookEdit on frozen controlled docs.

Protocol (same as .claude/hooks/check-active-task.sh): the tool payload arrives
as JSON on stdin (`tool_name`, `tool_input.file_path`, `session_id`, `cwd`).
A block is a JSON object on stdout with
`hookSpecificOutput.permissionDecision: "deny"` plus a reason (the briefing);
an allow is silent exit 0.

Decision:
  1. Only Edit / Write / NotebookEdit on a markdown file are examined; every
     other tool or file type is allowed immediately (fast path).
  2. The target's YAML frontmatter is read (stdlib only — no PyYAML needed for
     the one scalar we care about): `state: <value>`. Edits are DENIED when the
     state is one the lifecycle defines as edit-locked:
        frozen    — Confluence page locked, formal review signatures in flight
        released  — in the released vault (Windchill ECO + signed PDF)
     Any other state (draft, published, review-formal) or no `state:` at all is
     allowed — `review-formal` edits are the publish path's concern, not this
     hook's.
  3. Fail OPEN: a payload that cannot be parsed, a missing file, or an
     unreadable frontmatter never blocks the tool — a note goes to stderr and
     the hook exits 0. This gate must never break unrelated work.

The deny reason is a *briefing*: what state the document is in, what an edit
would invalidate, and the sanctioned way forward (`/change-control unfreeze`).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

EDIT_TOOLS = {"Edit", "Write", "NotebookEdit", "MultiEdit"}
LOCKED_STATES = {
    "frozen": "the Confluence page is locked and formal-review signatures may be in flight",
    "released": "the document is in the released vault (ECO + signed PDF)",
}
STATE_RE = re.compile(r"^state:\s*['\"]?([A-Za-z_-]+)['\"]?\s*(?:#.*)?$", re.MULTILINE)


def frontmatter_state(path: Path) -> str | None:
    """Value of the `state:` key in the leading YAML frontmatter, or None."""
    try:
        with path.open("r", encoding="utf-8", errors="replace") as fh:
            head = fh.read(16384)
    except OSError:
        return None
    if not head.startswith("---"):
        return None
    end = head.find("\n---", 3)
    block = head[3:end] if end != -1 else head[3:]
    m = STATE_RE.search(block)
    return m.group(1).strip().lower() if m else None


def deny(reason: str) -> int:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }))
    return 0


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception as exc:  # fail open — never block on a bad payload
        print(f"change-control frozen-gate: payload not parsed ({exc}); allowing", file=sys.stderr)
        return 0
    if not isinstance(payload, dict) or payload.get("tool_name") not in EDIT_TOOLS:
        return 0
    tool_input = payload.get("tool_input") or {}
    raw = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
    if not raw:
        return 0
    path = Path(raw)
    if not path.is_absolute():
        path = Path(payload.get("cwd") or ".") / path
    if path.suffix.lower() not in (".md", ".markdown"):
        return 0
    if not path.is_file():
        return 0  # a Write creating a new file cannot be frozen
    state = frontmatter_state(path)
    if state not in LOCKED_STATES:
        return 0
    why = LOCKED_STATES[state]
    return deny(
        f"FREEZE GATE: `{path.name}` is `state: {state}` — {why}. Editing it from the workbench "
        f"would invalidate that state and any review or release record tied to it. "
        f"To change the document, take it out of the locked state first through the sanctioned "
        f"transition (`/change-control unfreeze <doc>`), which records who unfroze it and why; "
        f"then edit and re-publish."
    )


if __name__ == "__main__":
    sys.exit(main())
