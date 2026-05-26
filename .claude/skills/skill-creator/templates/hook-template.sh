#!/bin/bash
# {{HOOK_NAME}}.sh — {{HOOK_DESCRIPTION}}
#
# Configured as: {{EVENT}} hook (matcher: {{MATCHER}})
# Requires: jq
#
# This hook lives in the skill directory and is symlinked from .claude/hooks/
# Source: .claude/skills/{{SKILL_NAME}}/hooks/{{HOOK_NAME}}.sh
# Symlink: .claude/hooks/{{SKILL_NAME}}-{{HOOK_NAME}}.sh
#
# ── MULTI-HOOK COEXISTENCE RULES ─────────────────────────────────────────
# Multiple skills can register hooks on the same event (e.g., several skills
# all hook PreToolUse). Claude Code chains them in registration order. To
# coexist safely:
#   1. SYMLINK NAME — prefix with the skill name: .claude/hooks/<skill>-<purpose>.sh
#      (so two skills' hooks can never collide on the same filename).
#   2. STATE FILES — prefix with the skill name + scope:
#      .state/<skill>-<purpose>-{session_id}.{json,txt}
#      Never read or write another skill's state file.
#   3. ORDER INDEPENDENCE — your hook must NOT depend on running before
#      or after any other hook. Each hook decides on its own input.
#   4. EXIT CODE — use 0 unless explicitly blocking. Informational nudges
#      go to stderr (visible to user); hard denials use the JSON contract.
#   5. SESSION CLEANUP — if you create per-session state, register a
#      SessionEnd hook that purges ONLY YOUR OWN state files.
# ─────────────────────────────────────────────────────────────────────────

set -euo pipefail

INPUT=$(cat)

# --- Hook logic here ---

# For PreToolUse hooks (allow/block/deny):
# jq -n '{"decision": "allow"}'

# For Stop hooks (block with reason):
# jq -n --arg reason "Your message here" '{
#   "hookSpecificOutput": {
#     "hookEventName": "Stop",
#     "decision": "block",
#     "reason": $reason
#   }
# }'

# For SessionStart/SessionEnd hooks (side effects only):
# Do work, exit 0

exit 0
