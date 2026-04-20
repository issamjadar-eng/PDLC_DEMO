#!/bin/bash
# {{HOOK_NAME}}.sh — {{HOOK_DESCRIPTION}}
#
# Configured as: {{EVENT}} hook (matcher: {{MATCHER}})
# Requires: jq
#
# This hook lives in the skill directory and is symlinked from .claude/hooks/
# Source: .claude/skills/{{SKILL_NAME}}/hooks/{{HOOK_NAME}}.sh
# Symlink: .claude/hooks/{{HOOK_NAME}}.sh

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
