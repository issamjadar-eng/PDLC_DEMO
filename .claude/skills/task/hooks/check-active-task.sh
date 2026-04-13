#!/bin/bash
# check-active-task.sh — Task discipline enforcement hook
#
# Denies Edit/Write/NotebookEdit tool calls when no active task is set.
# State file: per-session, inside the project at .claude/state/
#
# Exempt paths: tasks/*, .claude/*
# Requires: jq
#
# Configured as: PreToolUse hook (matcher: Edit|Write|NotebookEdit)
# See: tasks/ben/024-security-posture-automation.md for design
# See: tasks/ben/027-task-gate-overhaul.md for this implementation

INPUT=$(cat)

# Parse hook input
TARGET=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

# Use CLAUDE_SESSION_ID from environment (set by SessionStart hook)
# Falls back to hook JSON session_id if env var isn't set yet
SESSION_ID="${CLAUDE_SESSION_ID}"
if [ -z "$SESSION_ID" ]; then
  SESSION_ID=$(echo "$INPUT" | jq -r '.session_id // empty')
fi

# Exempt paths — these can be written without an active task
case "$TARGET" in
  */tasks/*|*/.claude/*)
    exit 0
    ;;
esac

# Auto-purge stale state files older than 7 days
find "${CLAUDE_PROJECT_DIR}/.claude/state" -name "active-tasks-*.txt" -mtime +7 -delete 2>/dev/null

# Check per-session state file in project-local .claude/state/
STATE_FILE="${CLAUDE_PROJECT_DIR}/.claude/state/active-tasks-${SESSION_ID}.txt"
if [ -f "$STATE_FILE" ] && [ -s "$STATE_FILE" ]; then
  exit 0
fi

# Deny — include session ID so Claude can recover in one command
SCRIPT=".claude/hooks/task-activate.sh"
jq -n --arg sid "$SESSION_ID" --arg script "$SCRIPT" '{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": ("TASK GATE: No active task for session " + $sid + ". Run: bash " + $script + " add " + $sid + " <TASK_ID> to activate a task, or create a new task with /task create.")
  }
}'
exit 0
