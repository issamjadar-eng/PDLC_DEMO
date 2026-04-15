"""
`change-control:freeze <path>` — Phase 1 → Phase 2 transition. STUB.

Planned flow (see SKILL.md "freeze" section):

  1. Verify <path> is markdown with state: draft.
  2. Verify doc class requires control per change-control.yml.
  3. Resolve or create Jira ECR (per Jira-required policy).
  4. Render markdown → Confluence via `mark`; create/update page.
  5. Capture page ID + version into frontmatter.
  6. Flip state: draft → frozen.
  7. Update docs/.change-control/state.json cache.
  8. Commit with `freeze(<jira_ecr>): <doc title>`.
"""
from __future__ import annotations

import sys


def main(argv: list[str]) -> int:
    path = argv[0] if argv else "<path>"
    print(f"change-control:freeze {path} — NOT IMPLEMENTED (scaffold only)")
    print("See SKILL.md 'freeze' section and tasks/ben/017-change-control-skill.md")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
