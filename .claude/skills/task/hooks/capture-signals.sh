#!/bin/bash
# capture-signals.sh — UserPromptSubmit hook: detect strategy/lessons signals
#
# Scans each user prompt for entry signals (arms capture check) and exit
# signals (marks capture check as pending). When exit is triggered on an
# armed task whose doc still lacks capture, injects additionalContext to
# prompt Claude to handle it in-turn. The Stop hook (capture-check.sh)
# acts as the hard backstop if this soft nudge is ignored.
#
# State files (per session, per task):
#   .claude/state/capture-armed-{session_id}-{task_id}.txt       — exists after entry signal
#   .claude/state/capture-exit-pending-{session_id}-{task_id}.txt — exists after exit signal
#
# Pass-through conditions (no arming/triggering):
#   - No active task
#   - Prompt matches no signal
#
# See: tasks/ben/050-task-capture-strategy-lessons.md for full design

INPUT=$(cat)

# Session ID
SESSION_ID="${CLAUDE_SESSION_ID}"
if [ -z "$SESSION_ID" ]; then
  SESSION_ID=$(echo "$INPUT" | jq -r '.session_id // empty')
fi
[ -z "$SESSION_ID" ] && exit 0

# Active tasks for this session
STATE_DIR="${CLAUDE_PROJECT_DIR}/.claude/state"
ACTIVE_FILE="${STATE_DIR}/active-tasks-${SESSION_ID}.txt"
[ -f "$ACTIVE_FILE" ] || exit 0
[ -s "$ACTIVE_FILE" ] || exit 0

# User's prompt text
PROMPT=$(echo "$INPUT" | jq -r '.prompt // empty')
[ -z "$PROMPT" ] && exit 0

# Signal vocabulary — tune by editing these patterns
# Entry signals: arm the capture check for any active task in this session
ENTRY_RE="let'?s architect|architect this|let'?s design|think through|let'?s think about|help me think|strategize|let'?s strategize|strategy for|regulatory strategy|submission strategy|trade-?off|weigh.*option|pros and cons|best approach|how.*approach this|what'?s in scope|define.*scope|scope this|design decision|need to decide|help me decide|pathway|draw the line|architectur"

# Exit signals: mark exit-pending — triggers the capture check
EXIT_RE="wrap.*up|let'?s wrap|we'?re done|that'?s done|all done|end.*session|let'?s stop|stopping|ready to commit|let'?s commit|that'?s it|good for now|call it|wrap it up"

mkdir -p "$STATE_DIR"

ARMED_ANY=0
EXIT_ANY=0
PENDING_TASKS=""

# Helper: check if task doc has capture or an intentional-absence changelog line
task_has_capture() {
  local task_id="$1"
  # Find the task file
  local file
  file=$(find "${CLAUDE_PROJECT_DIR}/tasks" -type f -name "${task_id}-*.md" 2>/dev/null | head -1)
  [ -z "$file" ] && return 1
  # Any tagged block?
  if grep -qE '<!-- (STRATEGY CONTENT|LESSONS LEARNED):' "$file" 2>/dev/null; then
    return 0
  fi
  # Today-dated "no content" changelog line?
  local today
  today=$(date +%Y-%m-%d)
  if grep -qE "^- ${today}: No strategy/lessons content this session" "$file" 2>/dev/null; then
    return 0
  fi
  return 1
}

# Process each active task
while IFS= read -r TASK_ID; do
  [ -z "$TASK_ID" ] && continue
  ARMED_FILE="${STATE_DIR}/capture-armed-${SESSION_ID}-${TASK_ID}.txt"
  EXIT_FILE="${STATE_DIR}/capture-exit-pending-${SESSION_ID}-${TASK_ID}.txt"

  # Arm on entry signal
  if echo "$PROMPT" | grep -qiE "$ENTRY_RE"; then
    if [ ! -f "$ARMED_FILE" ]; then
      touch "$ARMED_FILE"
      ARMED_ANY=1
    fi
  fi

  # Mark exit-pending on exit signal (only if armed)
  if [ -f "$ARMED_FILE" ] && echo "$PROMPT" | grep -qiE "$EXIT_RE"; then
    if [ ! -f "$EXIT_FILE" ]; then
      touch "$EXIT_FILE"
      EXIT_ANY=1
    fi
    # If still uncaptured, add to pending list for context injection
    if ! task_has_capture "$TASK_ID"; then
      PENDING_TASKS="${PENDING_TASKS}${TASK_ID} "
    fi
  fi
done < "$ACTIVE_FILE"

# Inject context if exit signal fired with pending capture
if [ -n "$PENDING_TASKS" ]; then
  MSG="Capture check: task(s) ${PENDING_TASKS}had strategic intent signals earlier this session and now show exit signals, but the task doc(s) still have no Strategy or Lessons block and no 'No strategy/lessons content this session' changelog line. Before ending the session, review whether capture is warranted: either draft a <!-- STRATEGY CONTENT: domain, topics --> block or a <!-- LESSONS LEARNED: categories --> block for user approval, or add a today-dated 'No strategy/lessons content this session' line to the changelog to make the absence intentional. Do not silently commit strategic content — always show the draft to the user first."
  jq -n --arg msg "$MSG" '{
    hookSpecificOutput: {
      hookEventName: "UserPromptSubmit",
      additionalContext: $msg
    }
  }'
fi

exit 0
