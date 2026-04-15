"""
`change-control:status [--filter <state>]` — traceability spine view. STUB.

Planned: walks docs/.change-control/state.json (validated against
frontmatter), prints a table of every controlled doc with its phase
and cross-system IDs:

  Path                          State     Confluence  Jira          Windchill
  inputs/pump-occlusion.md      frozen    458291 v1   PP3500-1234   —
  inputs/audible-alarm.md       released  458292 v3   PP3500-1235   ECO-9981
"""
from __future__ import annotations

import sys


def main(argv: list[str]) -> int:
    print("change-control:status — NOT IMPLEMENTED (scaffold only)")
    print()
    print("  Path                  State    Confluence   Jira           Windchill")
    print("  --                    --       --           --             --")
    print("  (no controlled docs registered — skill is in scaffold mode)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
