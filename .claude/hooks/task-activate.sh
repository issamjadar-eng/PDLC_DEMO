#!/bin/bash
# task-activate.sh — Manage per-session active task state
#
# State files: .state/active-tasks-{session_id}.txt (project root, relocated from
# .claude/state/ in task ben/083 to escape Claude Code's built-in .claude/**
# sensitive-file guard)
# Called by: task skill (on create/find/complete), Claude (on hook denial recovery)
# Read by: .claude/hooks/check-active-task.sh (PreToolUse gate)

# State files live in .state/ at project root (gitignored); script lives in
# .claude/hooks/ (tracked).
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# Prefer CLAUDE_PROJECT_DIR when set (hook context); else resolve relative to
# the script location: from .claude/hooks/ go up two levels to project root.
if [ -n "${CLAUDE_PROJECT_DIR:-}" ]; then
  STATE_DIR="${CLAUDE_PROJECT_DIR}/.state"
elif [ "$(basename "$SCRIPT_DIR")" = "hooks" ]; then
  STATE_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")/.state"
else
  STATE_DIR="$SCRIPT_DIR"
fi
mkdir -p "$STATE_DIR"
ACTION="${1:-help}"
SESSION_ID="$2"
TASK_ID="$3"

if [ -z "$SESSION_ID" ] || [ "$ACTION" = "help" ]; then
  echo "Usage: task-activate.sh <add|remove|list|clear> <session_id> [task_id]"
  echo ""
  echo "Commands:"
  echo "  add <session_id> <task_id>     Activate a task for this session"
  echo "  remove <session_id> <task_id>  Deactivate a task for this session"
  echo "  list <session_id>              Show active tasks for this session"
  echo "  clear <session_id>             Deactivate all tasks for this session"
  exit 0
fi

STATE_FILE="$STATE_DIR/active-tasks-${SESSION_ID}.txt"

case "$ACTION" in
  add)
    if [ -z "$TASK_ID" ]; then
      echo "Usage: task-activate.sh add <session_id> <task_id>" >&2
      exit 1
    fi
    touch "$STATE_FILE"
    grep -qxF "$TASK_ID" "$STATE_FILE" 2>/dev/null || echo "$TASK_ID" >> "$STATE_FILE"
    echo "Task $TASK_ID activated for session $SESSION_ID"
    ;;
  remove)
    if [ -z "$TASK_ID" ]; then
      echo "Usage: task-activate.sh remove <session_id> <task_id>" >&2
      exit 1
    fi
    if [ -f "$STATE_FILE" ]; then
      # Portable line removal (BSD sed and GNU sed have incompatible -i syntax).
      # grep -vxF prints every line that isn't an exact-match of TASK_ID.
      # If grep returns no lines (task was the last entry), truncate the file.
      if grep -vxF "$TASK_ID" "$STATE_FILE" > "$STATE_FILE.tmp" 2>/dev/null; then
        mv "$STATE_FILE.tmp" "$STATE_FILE"
      else
        : > "$STATE_FILE"
        rm -f "$STATE_FILE.tmp"
      fi
    fi
    echo "Task $TASK_ID deactivated for session $SESSION_ID"
    ;;
  list)
    if [ -f "$STATE_FILE" ] && [ -s "$STATE_FILE" ]; then
      cat "$STATE_FILE"
    else
      echo "(no active tasks)"
    fi
    ;;
  clear)
    : > "$STATE_FILE"
    echo "All tasks deactivated for session $SESSION_ID"
    ;;
  *)
    echo "Unknown action: $ACTION" >&2
    echo "Usage: task-activate.sh <add|remove|list|clear> <session_id> [task_id]" >&2
    exit 1
    ;;
esac
