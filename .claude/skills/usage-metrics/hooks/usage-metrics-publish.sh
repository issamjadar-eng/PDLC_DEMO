#!/usr/bin/env bash
# usage-metrics-publish.sh — SessionEnd hook.
#
# Captures the just-finished session (collect) and PUBLISHES this user's own
# tasks/<task_folder>/_usage-metrics/ data to the shared branch via an isolated
# git worktree (publish.py) — so the daily-aggregate GitHub workflow always has
# current data with no manual step. Background + best-effort: never blocks or
# fails the session. Gated by usage_metrics.publish.enabled in project.yml.
set -uo pipefail

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"
cd "$PROJECT_DIR" 2>/dev/null || exit 0

grep -q '^usage_metrics:' project.yml 2>/dev/null || exit 0
[[ -f tools/usage-metrics/collect.py ]] || exit 0
command -v python3 >/dev/null 2>&1 || exit 0

# Only if publishing is enabled (usage_metrics.publish.enabled: true).
grep -A40 '^usage_metrics:' project.yml | grep -A8 '^[[:space:]]*publish:' \
    | grep -q 'enabled:[[:space:]]*true' || exit 0

LOG="$PROJECT_DIR/.state/usage-metrics-publish.log"
nohup bash -c '
    cd "'"$PROJECT_DIR"'/tools/usage-metrics" 2>/dev/null || exit 0
    python3 collect.py --quiet
    cd "'"$PROJECT_DIR"'" 2>/dev/null || exit 0
    python3 .claude/skills/usage-metrics/scripts/publish.py --quiet
' >"$LOG" 2>&1 &
disown 2>/dev/null || true

exit 0
