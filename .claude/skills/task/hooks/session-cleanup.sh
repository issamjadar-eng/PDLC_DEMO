#!/bin/bash
# session-cleanup.sh — SessionEnd hook that removes the session's state file
#
# Deletes .claude/state/active-tasks-{session_id}.txt so completed sessions
# don't leave orphan state files. This is best-effort cleanup — the auto-purge
# in task-activate.sh already cleans up files older than 7 days as a fallback.

INPUT=$(cat)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
STATE_DIR="$SCRIPT_DIR/../state"

# Get session ID from hook JSON or env var
SESSION_ID=""
if command -v jq &>/dev/null && [ -n "$INPUT" ]; then
    SESSION_ID=$(echo "$INPUT" | jq -r '.session_id // empty' 2>/dev/null)
fi
[ -z "$SESSION_ID" ] && SESSION_ID="${CLAUDE_SESSION_ID:-}"

if [ -n "$SESSION_ID" ]; then
    rm -f "$STATE_DIR/active-tasks-${SESSION_ID}.txt"
    # Clear capture-armed and capture-exit-pending markers for this session
    rm -f "$STATE_DIR"/capture-armed-"${SESSION_ID}"-*.txt 2>/dev/null
    rm -f "$STATE_DIR"/capture-exit-pending-"${SESSION_ID}"-*.txt 2>/dev/null
fi

exit 0
