#!/bin/bash
# capture-check.sh — Stop hook: hard backstop for Strategy/Lessons capture
#
# Fires when Claude finishes a response turn. For each active task in this
# session that is (a) armed (entry signal fired earlier) and (b) exit-pending
# (exit signal fired) and (c) still uncaptured (no Strategy/Lessons block in
# the task doc and no today-dated "No strategy/lessons content this session"
# changelog line), emits a block decision that prevents stopping and injects
# a capture instruction into Claude's context.
#
# The soft nudge (UserPromptSubmit → additionalContext) runs first. This
# hook is the hard backstop — if Claude ignored the nudge, this forces the
# issue before the session can truly end.
#
# Loop protection: one of three escape hatches must be satisfied for the
# block to clear — (1) Strategy tag added, (2) Lessons tag added, or
# (3) today-dated "No strategy/lessons content this session" changelog line
# added. All three are cheap for Claude to produce, so no max-block counter
# is needed for v1.
#
# State files read (written by capture-signals.sh):
#   .state/capture-armed-{session_id}-{task_id}.txt
#   .state/capture-exit-pending-{session_id}-{task_id}.txt
# (relocated from .claude/state/ in ben/083 to escape .claude/** sensitive-file guard)
#
# See: tasks/ben/050-task-capture-strategy-lessons.md for full design

INPUT=$(cat)

# Session ID
SESSION_ID="${CLAUDE_SESSION_ID}"
if [ -z "$SESSION_ID" ]; then
  SESSION_ID=$(echo "$INPUT" | jq -r '.session_id // empty')
fi
[ -z "$SESSION_ID" ] && exit 0

# Active tasks
STATE_DIR="${CLAUDE_PROJECT_DIR}/.state"
ACTIVE_FILE="${STATE_DIR}/active-tasks-${SESSION_ID}.txt"
[ -f "$ACTIVE_FILE" ] || exit 0
[ -s "$ACTIVE_FILE" ] || exit 0

task_has_capture() {
  local task_id="$1"
  local file
  file=$(find "${CLAUDE_PROJECT_DIR}/tasks" -type f -name "${task_id}-*.md" 2>/dev/null | head -1)
  [ -z "$file" ] && return 1
  if grep -qE '<!-- (STRATEGY CONTENT|LESSONS LEARNED):' "$file" 2>/dev/null; then
    return 0
  fi
  local today
  today=$(date +%Y-%m-%d)
  if grep -qE "^- ${today}: No strategy/lessons content this session" "$file" 2>/dev/null; then
    return 0
  fi
  return 1
}

PENDING=""
while IFS= read -r TASK_ID; do
  [ -z "$TASK_ID" ] && continue
  ARMED_FILE="${STATE_DIR}/capture-armed-${SESSION_ID}-${TASK_ID}.txt"
  EXIT_FILE="${STATE_DIR}/capture-exit-pending-${SESSION_ID}-${TASK_ID}.txt"
  [ -f "$ARMED_FILE" ] || continue
  [ -f "$EXIT_FILE" ] || continue
  if ! task_has_capture "$TASK_ID"; then
    PENDING="${PENDING}${TASK_ID} "
  fi
done < "$ACTIVE_FILE"

[ -z "$PENDING" ] && exit 0

REASON="Capture backstop: task(s) ${PENDING}were armed by strategic-intent signals this session, exit signals have fired, but the task doc(s) still lack a <!-- STRATEGY CONTENT: ... --> block, a <!-- LESSONS LEARNED: ... --> block, and a today-dated 'No strategy/lessons content this session' changelog line. Before stopping, do one of: (1) draft a Strategy block for user approval (domains: regulatory, commercial, architecture, development, testing, risk, postmarket), (2) draft a Lessons Learned block for user approval, or (3) add the 'No strategy/lessons content this session' changelog line if the session genuinely had no qualifying content. Do not silently commit strategic content — present drafts to the user for approval before writing."

jq -n --arg reason "$REASON" '{
  decision: "block",
  reason: $reason
}'

exit 0
