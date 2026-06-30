#!/usr/bin/env bash
# usage-metrics-refresh.sh — SessionStart hook.
#
# If this user's usage-metrics dashboard is STALE (> TTL days), regenerate it
# in the background from LOCAL data only — NO git pull, NO commit, NO network.
# Mirrors the SECOPS 7-day TTL fast-path: silent + zero-overhead on the happy
# path, never fails the session (always exits 0).
#
# Scope decision: local-only. Your own usage stays
# current automatically; teammates' data refreshes when someone pulls/commits.
set -uo pipefail

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"
cd "$PROJECT_DIR" 2>/dev/null || exit 0

# Execution surface = tools/usage-metrics/ (symlinks → skill scripts). Running
# here keeps runtime artifacts (__pycache__, venv, deps) out of .claude/skills.
EXEC_DIR="tools/usage-metrics"

# Only act if usage_metrics is configured and the tooling exists.
grep -q '^usage_metrics:' project.yml 2>/dev/null || exit 0
[[ -f "$EXEC_DIR/collect.py" ]] || exit 0
command -v python3 >/dev/null 2>&1 || exit 0

# Resolve the current user's task folder via the canonical resolver.
TF=$(python3 .claude/skills/shared/scripts/resolve_user.py --task-folder 2>/dev/null)
[[ -z "$TF" ]] && exit 0

# TTL: project.yml usage_metrics.refresh_ttl_days (default 7).
TTL=$(grep -A40 '^usage_metrics:' project.yml | grep -m1 'refresh_ttl_days:' \
        | sed 's/.*refresh_ttl_days:[[:space:]]*//' | tr -dc '0-9')
[[ -z "$TTL" ]] && TTL=7

mkdir -p "$PROJECT_DIR/.state" 2>/dev/null
MARKER="$PROJECT_DIR/.state/usage-metrics-last-refresh-$TF.txt"

# Fast path — marker fresh enough?
if [[ -f "$MARKER" ]]; then
    last=$(tr -d '[:space:]' < "$MARKER" 2>/dev/null)
    if [[ -n "$last" ]]; then
        days=$(python3 - "$last" <<'PY'
import sys
from datetime import datetime
try:
    d = datetime.strptime(sys.argv[1], '%Y-%m-%d')
    print((datetime.now() - d).days)
except Exception:
    print(9999)
PY
)
        if [[ "$days" =~ ^[0-9]+$ ]] && [[ "$days" -lt "$TTL" ]]; then
            exit 0   # fresh — nothing to do
        fi
    fi
fi

# Stale (or first run): stamp the marker NOW (prevents concurrent-session
# stampede), then regenerate in the background, local-only.
date +%Y-%m-%d > "$MARKER" 2>/dev/null
LOG="$PROJECT_DIR/.state/usage-metrics-refresh.log"
nohup bash -c '
    cd "'"$PROJECT_DIR"'/tools/usage-metrics" || exit 0
    python3 collect.py --quiet
    python3 aggregate.py --quiet
' >"$LOG" 2>&1 &
disown 2>/dev/null || true

exit 0
