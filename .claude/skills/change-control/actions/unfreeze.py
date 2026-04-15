"""
`change-control:unfreeze <path> [--reason <text>]` — frozen → draft. STUB.

Normally called automatically by the PreToolUse hook on user approval —
not directly by the user.

Planned flow (see SKILL.md "unfreeze" section):

  1. Verify <path> has state: frozen.
  2. Mark Confluence page as Superseded via Comala API.
  3. Comment on linked Jira ECR (`Unfrozen by <user>: <reason>`).
  4. Flip state: frozen → draft; clear confluence_version_at_publish; add unfrozen_at.
  5. Update state cache.
  6. Commit with `unfreeze(<jira_ecr>): <doc title> — <reason>`.
"""
from __future__ import annotations

import sys


def main(argv: list[str]) -> int:
    path = argv[0] if argv else "<path>"
    print(f"change-control:unfreeze {path} — NOT IMPLEMENTED (scaffold only)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
