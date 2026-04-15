"""
`change-control:init` — wire the skill into the project. STUB.

Planned steps (see SKILL.md "init" section for the full spec):

  1. Preflight (jq, register-hook.sh, project.yml, mark, python deps).
  2. Symlink hooks/pre_tool_use_frozen.py → .claude/hooks/change-control-frozen.py.
  3. Register PreToolUse hook via .claude/hooks/register-hook.sh.
  4. Add `change-control` to project.yml security.approved_skills.
  5. Copy templates/change-control.example.yml → ./change-control.yml if absent.
  6. Create docs/.change-control/state.json (empty array).
  7. Probe OS keychain for credentials; print one-time setup instructions if missing.
  8. Report what was done and what the user still needs to do.
"""
from __future__ import annotations

import sys


def main() -> int:
    print("change-control:init — NOT IMPLEMENTED (scaffold only)")
    print()
    print("This skill is currently a scaffold. See:")
    print("  .claude/skills/change-control/SKILL.md     (manual)")
    print("  .claude/skills/change-control/README.md    (design)")
    print("  tasks/ben/017-change-control-skill.md      (open questions)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
