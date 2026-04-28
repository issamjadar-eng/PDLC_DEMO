"""`change-control help [<action>]` — runtime help.

Prints lifecycle diagram + per-action usage. Q13 lock (2026-04-27).
"""
from __future__ import annotations

import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent


HELP_TOP = """\
change-control — usage

Lifecycle:

    draft (md / docx in git)
        │
        │  (optional, free-flow) — internal review via Google Docs:
        │  ├─ review-start    create gdoc + task-doc section + manual-share reminder
        │  ├─ review-status   refresh task-doc section with current open items
        │  ├─ review-update   post replies for addressed items + push md → gdoc
        │  └─ review-abort    cancel review, archive section, delete state
        │
        ▼  freeze
    frozen (Confluence / Comala — Part 11 review)
        │
        ▼  release
    released (Windchill vault)


Actions:
  init                          Wire the change-control hook + create config
  freeze <path>                 Lock md from edits + push to Confluence
  unfreeze <path> [--reason]    Reopen for edits (called by hook on consent)
  status [--filter <state>]     Show traceability spine across controlled docs
  release <path>                Phase 2 → Phase 3 (Windchill)

Internal review tier (v0.1, task-doc-driven):
  review-start <path>           Kick off internal review for a doc
  review-status <path>          Refresh task-doc section with gdoc state
  review-update <path>          Post replies for Already-Addressed items + push md → gdoc
  review-abort <path>           Cancel review, archive section, clean up state

  help [<action>]               Show this help, or detailed help for one action
  diagnose [--live]             Run health checks + diagnostic dump (use when troubleshooting)

Run `change-control help <action>` for action-specific usage.
See: .claude/skills/change-control/README.md (design)
     .claude/skills/change-control/SKILL.md  (manual)
     getting-started.md (project workflow guide)
"""


HELP_DETAIL = {
    "init": """\
change-control init

Wire the change-control PreToolUse hook + create change-control.yml from
template if missing. Idempotent. Run during project setup.

Steps:
  1. Verify deps (jq, register-hook.sh, project.yml)
  2. Symlink hook into .claude/hooks/
  3. Register hook in .claude/settings.json
  4. Add change-control to project.yml security.approved_skills
  5. Copy templates/change-control.example.yml → change-control.yml
  6. Create docs/.change-control/state.json cache
  7. Probe credentials (keychain) — print setup instructions if missing
""",

    "freeze": """\
change-control freeze <path>

Lock the md file from further edits and publish to Confluence for
Part 11 customer review. Triggers the existing freeze flow plus, if
the doc has an active internal-review gdoc, archives it (banner +
[ARCHIVED YYYY-MM-DD] rename + close comments + demote task-doc section).

Args:
  <path>   Repo-relative path to the md file to freeze

Steps:
  1. Verify state == draft (or revised)
  2. Verify doc_class is set + meets policy
  3. Look up active internal-review gdoc in user's task doc; if found:
     a. Prepend archived banner to gdoc body
     b. Rename gdoc with [ARCHIVED YYYY-MM-DD] prefix
     c. Resolve open comments with "internal review closed" reply
     d. Demote task-doc section to "Archived internal reviews"
  4. Resolve or create Jira ECR
  5. Render md → Confluence via mark; create or update page
  6. Capture page ID + version into frontmatter
  7. Flip state: draft → frozen
  8. Update docs/.change-control/state.json cache
  9. Commit with message: freeze(<jira-ecr>): <doc-title>
""",

    "unfreeze": """\
change-control unfreeze <path> [--reason <text>]

Re-open a frozen doc for editing. Normally called by the PreToolUse
hook on user consent — not invoked directly.

Args:
  <path>           Repo-relative path
  --reason <text>  Free-text justification for the unfreeze
""",

    "status": """\
change-control status [--filter <state>]

Show every controlled doc and its phase + IDs:
  Path    State    Confluence    Jira    Windchill

Reads frontmatter (authoritative); validates against state.json cache.
""",

    "release": """\
change-control release <path>

Phase 2 → Phase 3 handoff: pulls signed PDF, attaches to new Windchill
ECO referencing the Jira ECR, updates frontmatter, flips state: frozen
→ released.

Normally triggered by the Comala "Released" webhook; can be invoked
manually for testing.
""",

    "review-start": """\
change-control review-start <path>

Kick off internal review for a markdown or docx file. Creates a Google
Doc in your AI_PDLC/<project>/<task_folder>/ folder, pastes source
content, writes a metadata block to your active task doc, and prints
a reminder to share with your reviewer group manually.

Args:
  <path>   Repo-relative path to source file (.md, .markdown, .docx)

v0.1 limitations:
  - Drive folder must exist; auto-create deferred to v0.2
  - Reviewer roster auto-share deferred to v0.2 (manual via Drive UI)
  - .docx upload via Drive UI is the documented path; not automated

Output:
  - Lists manual setup steps (open Drive, create gdoc, paste content,
    enable Markdown preference, share with reviewers)
  - Writes sentinel-bounded "## Internal Review — <path>" section to
    your active task doc with placeholder GDoc URL field
  - User pastes the URL after creating the gdoc
""",

    "review-status": """\
change-control review-status <path>

Refresh the task-doc section's "Open" list with current open comments,
suggestions, and body edits from the linked gdoc. Preserves Already-
Addressed and Recently-Synced subsections (those are user-driven).

Args:
  <path>   Repo-relative path matching the section's doc identifier

Requirements:
  - web-control debug Chrome must be running (web-control launch)
  - You must be signed in to your corporate Google account
  - The task-doc section must already exist (run review-start first)

Output:
  - Counts: <N> open comments · <M> suggestions · <K> body edits
  - Updated Last sync timestamp
  - Existing items in Already-Addressed / Recently-Synced preserved
""",

    "review-update": """\
change-control review-update <path>

Push your local md changes to the gdoc + post replies on Already-
Addressed items.

For each item in the section's "Already Addressed" subsection:
  - kind=comment    → posts reply (resolution_note or default text) and resolves
  - kind=suggestion → accepts (status=addressed) or rejects (status=wont-fix)
  - kind=body-edit  → no comment to reply to; body-replace is the ack

Then wholesale-replaces the gdoc body with current source file content.
Comment anchors orphan acceptably (Q3 lock); replies preserve the
conversation thread regardless.

Args:
  <path>   Repo-relative path matching the section's doc identifier

State files:
  .state/web-control/<gdoc-id>.last-sync.json   updated
  .state/web-control/<gdoc-id>.last-push.txt    updated

After successful update:
  - Already Addressed → Recently Synced (last 50 retained)
  - last_sync, last_md_push timestamps bumped
  - Run review-status next to refresh Open list
""",

    "review-abort": """\
change-control review-abort <path>

Cancel an active internal review without going through formal freeze.
Removes the metadata block from the task doc, deletes state files.
Does NOT delete the gdoc — you can manually clean up in Drive.

Args:
  <path>   Repo-relative path matching the section's doc identifier
""",

    "help": HELP_TOP,
}


def main() -> int:
    if len(sys.argv) < 2:
        print(HELP_TOP)
        return 0
    target = sys.argv[1].strip()
    detail = HELP_DETAIL.get(target)
    if detail is None:
        print(f"unknown action: {target}", file=sys.stderr)
        print(file=sys.stderr)
        print(HELP_TOP, file=sys.stderr)
        return 64
    print(detail)
    return 0


if __name__ == "__main__":
    sys.exit(main())
