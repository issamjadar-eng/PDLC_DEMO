#!/usr/bin/env python3
"""
PreToolUse hook — blocks Edit/Write/NotebookEdit on frozen controlled docs.

STATUS: STUB. Currently exits 0 (allows all edits) so the skill can be
installed in a project without breaking anything. Real enforcement is
designed but not implemented.

Execution path (when implemented):
  1. Parse tool input JSON from stdin → target file path.
  2. Lookup in docs/.change-control/state.json — if not a controlled
     doc, exit 0 immediately. (Fast path; 99% of edits hit this.)
  3. If controlled, read frontmatter. If state != frozen, exit 0.
  4. If frozen, classify the proposed edit (lib/diff_classify.py) —
     cosmetic vs substantive.
  5. Emit a structured block message to stderr per Claude Code hook
     protocol containing the briefing text; exit non-zero to block
     the tool call.

The block message is a *briefing* — it explains what will be invalidated
(Confluence page state, in-progress reviewer signatures, Jira ticket
state) and requires an explicit typed phrase including the document name
to authorize the unfreeze. See README.md "The Freeze Enforcement
Mechanism" section for the full briefing format and rationale.
"""
import sys


def main() -> int:
    # STUB: pass-through. No enforcement until implementation lands.
    # When implemented, the logic above will replace this.
    return 0


if __name__ == "__main__":
    sys.exit(main())
