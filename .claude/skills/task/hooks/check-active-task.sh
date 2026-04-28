#!/bin/bash
# check-active-task.sh — Task discipline enforcement hook
#
# Denies Edit/Write/NotebookEdit tool calls when no active task is set.
# State file: per-session, inside the project at .state/ (project root, outside
# .claude/ to escape Claude Code's built-in .claude/** sensitive-file guard;
# relocated from .claude/state/ in task ben/083).
#
# Exempt paths (runtime housekeeping, not design surfaces):
#   - tasks/*                   — task docs themselves
#   - .state/*                  — per-session state (relocated in ben/083)
#   - .claude/settings*.json    — settings (often auto-managed by register-hook.sh)
#   - .claude/sync-log.md       — written by /sync-skills
#   - .claude/MEMORY.md         — memory index (auto-managed)
#   - .claude/memory/*          — memory files (auto-managed)
#
# Everything else (CLAUDE.md, project.yml, .claude/skills/**, .claude/rules/**,
# .claude/hooks/*, .claude/agents/*, docs/, etc.) requires an active task.
#
# Symlink safety: both the input path AND its canonical (symlink-resolved) path
# are checked. A symlink in an exempt location whose target is a design surface
# (e.g., .claude/agents/<name>.md → skills/<x>/agents/<name>.md) resolves to a
# gated path and is correctly denied. Requires `realpath`, `readlink -f`, or
# python3 on PATH for symlink resolution; falls back to raw path if none.
#
# Requires: jq
#
# Configured as: PreToolUse hook (matcher: Edit|Write|NotebookEdit)
# See: tasks/ben/024-security-posture-automation.md for original design
# See: tasks/ben/027-task-gate-overhaul.md for session-state implementation
# See: tasks/ben/066-task-gate-skill-source-scoping.md for this scoping rewrite

INPUT=$(cat)

# Parse hook input
TARGET=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

# Use CLAUDE_SESSION_ID from environment (set by SessionStart hook)
# Falls back to hook JSON session_id if env var isn't set yet
SESSION_ID="${CLAUDE_SESSION_ID}"
if [ -z "$SESSION_ID" ]; then
  SESSION_ID=$(echo "$INPUT" | jq -r '.session_id // empty')
fi

# Exempt-pattern matcher — used for both raw TARGET and its canonical form.
# Only exempt if BOTH match (so a symlink whose target is gated gets gated).
is_exempt() {
  local p="$1"
  case "$p" in
    */tasks/*)                        return 0 ;;
    */.state/*)                       return 0 ;;
    */.claude/settings*.json)         return 0 ;;
    */.claude/sync-log.md)            return 0 ;;
    */.claude/MEMORY.md)              return 0 ;;
    */.claude/memory/*)               return 0 ;;
  esac
  return 1
}

# Fast path: if TARGET is exempt AND not a symlink, the canonical form can't
# possibly land on a gated path — skip symlink resolution entirely. This is the
# overwhelming common case (editing a real file under tasks/ or .state/).
if [ -n "$TARGET" ] && is_exempt "$TARGET" && [ ! -L "$TARGET" ]; then
  exit 0
fi

# Slow path: canonicalize TARGET so symlinks can't bypass the gate. python3 is
# tried first because `os.path.realpath` has uniform semantics across macOS and
# Linux and tolerates missing leaf paths (e.g., Write creating a new file). If
# python3 is unavailable, fall back to platform-specific tools:
#   - GNU coreutils: `realpath -m` (macOS BSD realpath doesn't have -m)
#   - GNU readlink:  `readlink -f` (BSD readlink doesn't have -f)
#   - BSD realpath:  works when the file exists; for a missing leaf, resolve
#                    the parent directory and re-append the basename.
# If none succeed, fall through with the raw path — gate behavior then matches
# v14 for that one call (permissive on symlinks, correct on regular paths).
RESOLVED="$TARGET"
if [ -n "$TARGET" ]; then
  if command -v python3 >/dev/null 2>&1; then
    RESOLVED=$(python3 -c 'import os,sys; print(os.path.realpath(sys.argv[1]))' "$TARGET" 2>/dev/null || echo "$TARGET")
  elif command -v realpath >/dev/null 2>&1; then
    RESOLVED=$(realpath -m "$TARGET" 2>/dev/null \
               || realpath "$TARGET" 2>/dev/null \
               || printf '%s/%s' "$(realpath "$(dirname "$TARGET")" 2>/dev/null)" "$(basename "$TARGET")" \
               || echo "$TARGET")
  elif command -v readlink >/dev/null 2>&1 && readlink -f / >/dev/null 2>&1; then
    RESOLVED=$(readlink -f "$TARGET" 2>/dev/null || echo "$TARGET")
  fi
fi

if is_exempt "$TARGET" && is_exempt "$RESOLVED"; then
  exit 0
fi

# Auto-purge stale state files older than 7 days — rate-limited to once per 24h
# via a sentinel file so we don't issue a find(1) on every Edit/Write call.
PURGE_SENTINEL="${CLAUDE_PROJECT_DIR}/.state/purge-last.txt"
if [ ! -f "$PURGE_SENTINEL" ] || [ -n "$(find "$PURGE_SENTINEL" -mtime +1 2>/dev/null)" ]; then
  find "${CLAUDE_PROJECT_DIR}/.state" -name "active-tasks-*.txt" -mtime +7 -delete 2>/dev/null
  touch "$PURGE_SENTINEL" 2>/dev/null
fi

# Check per-session state file in project-local .state/
STATE_FILE="${CLAUDE_PROJECT_DIR}/.state/active-tasks-${SESSION_ID}.txt"
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
