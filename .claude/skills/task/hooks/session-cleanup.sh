#!/bin/bash
# session-cleanup.sh — SessionEnd hook that removes the session's state file
#
# Deletes .state/active-tasks-{session_id}.txt so completed sessions don't
# leave orphan state files. This is best-effort cleanup — the auto-purge in
# task-activate.sh already cleans up files older than 7 days as a fallback.
# State dir is .state/ at project root (relocated from .claude/state/ in
# ben/083 to escape the .claude/** sensitive-file guard).

INPUT=$(cat)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
STATE_DIR="${CLAUDE_PROJECT_DIR:-$(cd "$SCRIPT_DIR/../.." && pwd)}/.state"

# Get session ID from hook JSON or env var
SESSION_ID=""
if command -v jq &>/dev/null && [ -n "$INPUT" ]; then
    SESSION_ID=$(echo "$INPUT" | jq -r '.session_id // empty' 2>/dev/null)
fi
[ -z "$SESSION_ID" ] && SESSION_ID="${CLAUDE_SESSION_ID:-}"

if [ -n "$SESSION_ID" ]; then
    rm -f "$STATE_DIR/active-tasks-${SESSION_ID}.txt"
fi

# Clean up any leftover capture-armed / capture-exit-pending markers from the
# deprecated Strategy/Lessons capture hooks (removed in task v23). Targets all
# sessions, not just this one, so pre-upgrade markers get cleared. Auto-purge
# in check-active-task.sh also catches files older than 7 days as a fallback.
rm -f "$STATE_DIR"/capture-armed-*.txt 2>/dev/null
rm -f "$STATE_DIR"/capture-exit-pending-*.txt 2>/dev/null

# Always clear the docflow-active marker as a belt-and-suspenders fallback for
# /docflow agents that touched it but failed to remove it on their exit path.
# Safe to remove unconditionally — it's a global (non-per-session) marker, and
# a fresh session with no /docflow running shouldn't carry it forward.
rm -f "$STATE_DIR/docflow-active" 2>/dev/null

exit 0
