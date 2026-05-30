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
    GATE_FILE="$STATE_DIR/active-tasks-${SESSION_ID}.txt"

    # Before purging the gate file, check if any active tasks were NOT recently
    # checkpointed. Write a marker for each stale one so the next session can
    # offer a retroactive `/checkpoint` recovery from git log.
    # "Stale" = no last-checkpoint marker OR last-checkpoint marker > 30 min old.
    if [ -f "$GATE_FILE" ]; then
        STALE_THRESHOLD=1800  # 30 minutes
        NOW=$(date +%s)
        TODAY=$(date +%Y-%m-%d)
        PROJECT_ROOT="$(cd "$STATE_DIR/.." && pwd)"

        while IFS= read -r TASK_ID; do
            [ -z "$TASK_ID" ] && continue

            # Discover which person owns this task (search tasks/*/NNN-*.md).
            TASK_FILE=$(find "$PROJECT_ROOT/tasks" -maxdepth 2 -name "${TASK_ID}-*.md" -type f 2>/dev/null | head -1)
            [ -z "$TASK_FILE" ] && continue
            PERSON=$(basename "$(dirname "$TASK_FILE")")

            # Check the last-checkpoint marker.
            CHECKPOINT_MARKER="$STATE_DIR/last-checkpoint-${PERSON}-${TASK_ID}.txt"
            STALE=1
            if [ -f "$CHECKPOINT_MARKER" ]; then
                # BSD stat (-f %m) on macOS; GNU stat (-c %Y) on Linux.
                LAST_CP=$(stat -f %m "$CHECKPOINT_MARKER" 2>/dev/null || stat -c %Y "$CHECKPOINT_MARKER" 2>/dev/null || echo 0)
                ELAPSED=$((NOW - LAST_CP))
                if [ "$ELAPSED" -lt "$STALE_THRESHOLD" ]; then
                    STALE=0
                fi
            fi

            if [ "$STALE" -eq 1 ]; then
                MARKER="$STATE_DIR/uncheckpointed-${PERSON}-${TASK_ID}-${TODAY}.txt"
                {
                    echo "session_id=${SESSION_ID}"
                    echo "task=${PERSON}/${TASK_ID}"
                    echo "task_file=${TASK_FILE}"
                    echo "ended_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
                } > "$MARKER"
            fi
        done < "$GATE_FILE"
    fi

    rm -f "$GATE_FILE"
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
