#!/bin/bash
# checkpoint-recover.sh — SessionStart hook
#
# Scans .state/ for uncheckpointed-<person>-<NNN>-*.txt markers written by
# session-cleanup.sh when a previous session ended with an active task that
# wasn't recently checkpointed. If any markers exist, injects context for
# Claude via the SessionStart additionalContext hookSpecificOutput so the new
# session proactively offers to recover the lost state via /checkpoint.
#
# Recovery is best-effort: the conversation transcript is gone, but `git log`
# and `git diff` since the task doc's last mtime are still recoverable, and
# that's enough for most cases.
#
# This hook is paired with session-cleanup.sh (writes markers) and the
# task skill's checkpoint action (deletes its matching marker on completion).
# State dir is .state/ at project root (gitignored).

INPUT=$(cat)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
STATE_DIR="${CLAUDE_PROJECT_DIR:-$(cd "$SCRIPT_DIR/../.." && pwd)}/.state"

[ -d "$STATE_DIR" ] || exit 0

# Collect any uncheckpointed-*.txt markers.
MARKERS=()
while IFS= read -r M; do
    [ -n "$M" ] && MARKERS+=("$M")
done < <(find "$STATE_DIR" -maxdepth 1 -name "uncheckpointed-*.txt" -type f 2>/dev/null)

[ ${#MARKERS[@]} -eq 0 ] && exit 0

# Build the additional-context message.
CONTEXT=$(
    echo "## Uncheckpointed task(s) from previous session(s)"
    echo ""
    echo "One or more previous sessions ended with an active task that was NOT"
    echo "checkpointed — the task doc may not be in a resume-ready state."
    echo ""
    for M in "${MARKERS[@]}"; do
        TASK=$(grep -m1 '^task=' "$M" 2>/dev/null | cut -d= -f2-)
        TASK_FILE=$(grep -m1 '^task_file=' "$M" 2>/dev/null | cut -d= -f2-)
        ENDED=$(grep -m1 '^ended_at=' "$M" 2>/dev/null | cut -d= -f2-)
        echo "- **\`${TASK}\`** — session ended at \`${ENDED}\`"
        echo "  - Task doc: \`${TASK_FILE}\`"
        echo "  - Marker: \`${M}\`"
    done
    echo ""
    echo "**Recommended action:** After greeting the user and before starting"
    echo "new work, offer to run the task skill's \`checkpoint\` action for each"
    echo "task above. Recovery is best-effort — the conversation transcript is"
    echo "lost, but \`git log\` / \`git diff\` since the task doc's last mtime IS"
    echo "recoverable and usually enough."
    echo ""
    echo "Once a checkpoint completes (or the user explicitly declines), delete"
    echo "the matching marker file so it doesn't resurface."
)

# Emit as SessionStart additionalContext (Claude Code prepends this to context).
jq -Rs --arg ctx "$CONTEXT" '{"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": $ctx}}' <<< ""

exit 0
