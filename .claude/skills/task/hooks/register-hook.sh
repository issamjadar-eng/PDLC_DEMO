#!/bin/bash
# register-hook.sh — Shared helper for skills to register hooks in settings.json
#
# Usage:
#   .claude/hooks/register-hook.sh <event> <matcher> <type> <command>
#
# Example:
#   .claude/hooks/register-hook.sh PreToolUse "Edit|Write|NotebookEdit" command \
#     '"$CLAUDE_PROJECT_DIR"/.claude/hooks/check-active-task.sh'
#
# Behavior:
#   - Creates settings.json if it doesn't exist
#   - Creates hooks.{event} array if it doesn't exist
#   - Checks if an entry with the same command already exists (idempotent)
#   - Appends the new entry if not present
#   - Preserves all existing settings and hooks
#
# Requires: jq

set -euo pipefail

EVENT="${1:?Usage: register-hook.sh <event> <matcher> <type> <command>}"
MATCHER="${2:-}"
HOOK_TYPE="${3:?}"
HOOK_COMMAND="${4:?}"

SETTINGS="${CLAUDE_PROJECT_DIR:-.}/.claude/settings.json"

# Create settings.json if missing
if [ ! -f "$SETTINGS" ]; then
  echo '{}' > "$SETTINGS"
fi

# Check if this exact hook command is already registered for this event
EXISTING=$(jq -r \
  --arg event "$EVENT" \
  --arg cmd "$HOOK_COMMAND" \
  '.hooks[$event] // [] | map(.hooks[]? | select(.command == $cmd)) | length' \
  "$SETTINGS" 2>/dev/null || echo "0")

if [ "$EXISTING" != "0" ]; then
  echo "Hook already registered for $EVENT: $HOOK_COMMAND"
  exit 0
fi

# Build the new hook entry
if [ -n "$MATCHER" ]; then
  NEW_ENTRY=$(jq -n \
    --arg matcher "$MATCHER" \
    --arg type "$HOOK_TYPE" \
    --arg cmd "$HOOK_COMMAND" \
    '{
      matcher: $matcher,
      hooks: [{
        type: $type,
        command: $cmd
      }]
    }')
else
  NEW_ENTRY=$(jq -n \
    --arg type "$HOOK_TYPE" \
    --arg cmd "$HOOK_COMMAND" \
    '{
      matcher: "",
      hooks: [{
        type: $type,
        command: $cmd
      }]
    }')
fi

# Append to the event's hook array (create if needed)
UPDATED=$(jq \
  --arg event "$EVENT" \
  --argjson entry "$NEW_ENTRY" \
  '.hooks[$event] = ((.hooks[$event] // []) + [$entry])' \
  "$SETTINGS")

echo "$UPDATED" > "$SETTINGS"
echo "Registered $HOOK_TYPE hook for $EVENT (matcher: $MATCHER)"
