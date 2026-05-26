#!/usr/bin/env python3
"""
PreToolUse hook — informational nudge when SKILL.md frontmatter or § Actions
is edited. Fires at most ONCE per skill per session (lifecycle-managed via
per-session armed state file). Body-only edits are skipped.

Lifecycle:
  - Per-session armed state at .state/skill-creator-armed-{session_id}.json
  - First trigger-surface edit to skill <name> in this session  -> arm + nudge
  - Subsequent edits to same skill in same session              -> silent
  - `audit-triggers <name>` action                              -> disarm <name>
  - SessionEnd                                                  -> purge file

Exit codes:
  0 always — informational only, never blocks the tool call.

The hook reads the PreToolUse JSON contract on stdin:
  {"session_id": "...", "tool_name": "Edit"|"Write"|"NotebookEdit",
   "tool_input": {"file_path": "...", "old_string": "...", "new_string": "...",
                  "content": "..."}}
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path


SKILL_MD_PATH_RE = re.compile(r"\.claude/skills/([^/]+)/SKILL\.md$")

# Markers that indicate a trigger-surface edit (frontmatter description or
# § Actions section). Body-only edits don't match any of these and are skipped.
FRONTMATTER_MARKERS = (
    "description:",       # frontmatter description field
    "version:",           # frontmatter version
    "name:",              # frontmatter name
    "## Actions",         # H2 actions section
    "### `",              # action heading (e.g. ### `setup`)
)


def find_project_root(start: Path) -> Path:
    """Walk up from `start` looking for `.claude/` to find the project root."""
    for parent in [start, *start.parents]:
        if (parent / ".claude").is_dir():
            return parent
    return start


def is_trigger_surface_edit(tool_input: dict) -> bool:
    """Return True if this edit plausibly touches the trigger surface.

    For Edit:    check old_string + new_string for any frontmatter marker.
    For Write:   any write to SKILL.md is treated as trigger-surface (could be
                 a new file or full rewrite).
    Heuristic — false positives are cheap (one extra nudge per session).
    """
    # Write tool: full file replacement, always trigger-surface
    if "content" in tool_input and "old_string" not in tool_input:
        return True

    chunk = (tool_input.get("old_string", "") + "\n" +
             tool_input.get("new_string", ""))
    return any(marker in chunk for marker in FRONTMATTER_MARKERS)


def load_armed(state_path: Path) -> set[str]:
    if not state_path.exists():
        return set()
    try:
        return set(json.loads(state_path.read_text()).get("skills", []))
    except (json.JSONDecodeError, OSError):
        return set()


def save_armed(state_path: Path, skills: set[str]) -> None:
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps({"skills": sorted(skills)}, indent=2))


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0  # malformed input — never block

    tool_name = payload.get("tool_name", "")
    if tool_name not in ("Edit", "Write", "NotebookEdit"):
        return 0

    tool_input = payload.get("tool_input", {})
    file_path = tool_input.get("file_path", "")
    if not file_path:
        return 0

    match = SKILL_MD_PATH_RE.search(file_path)
    if not match:
        return 0
    skill_name = match.group(1)

    if not is_trigger_surface_edit(tool_input):
        return 0  # body-only edit — silent

    session_id = payload.get("session_id") or os.environ.get("CLAUDE_SESSION_ID", "no-session")
    project_root = Path(os.environ.get("CLAUDE_PROJECT_DIR") or
                        find_project_root(Path(file_path).resolve()))
    state_path = project_root / ".state" / f"skill-creator-armed-{session_id}.json"

    armed = load_armed(state_path)
    if skill_name in armed:
        return 0  # already armed this session — silent

    armed.add(skill_name)
    save_armed(state_path, armed)

    # Informational nudge to stderr — visible to the user, doesn't block.
    msg = (
        f"\n[skill-creator] You edited the trigger surface of skill `{skill_name}` "
        f"(SKILL.md frontmatter or § Actions).\n"
        f"[skill-creator] Run `/skill-creator audit-triggers {skill_name}` before "
        f"committing — verifies trigger coverage + cross-skill conflicts.\n"
        f"[skill-creator] (Armed once per skill per session. Body-only edits silent.)\n"
    )
    print(msg, file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
