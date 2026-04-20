#!/usr/bin/env bash
# project-console start — idempotent launcher. Kills any process already
# listening on the configured port, then execs run.sh. Use this whenever
# skill code has changed (uvicorn --reload does NOT watch the skill
# package) or when an earlier session left a stale console running.
set -euo pipefail
cd "$(dirname "$0")"

# Resolve port: prefer console.yaml's server.port, fall back to 8765.
PORT=8765
if [ -f console.yaml ]; then
  discovered=$(awk '
    /^server:/ { s=1; next }
    /^[^[:space:]]/ && s { s=0 }
    s && /port:/ { gsub(/[^0-9]/, "", $2); if ($2 != "") { print $2; exit } }
  ' console.yaml 2>/dev/null || true)
  if [ -n "$discovered" ]; then
    PORT="$discovered"
  fi
fi

# Kill any existing listener on the port
existing=$(lsof -ti "tcp:$PORT" 2>/dev/null || true)
if [ -n "$existing" ]; then
  pids=$(echo "$existing" | tr '\n' ' ')
  echo "project-console: stopping existing console on port $PORT (pid(s): $pids)"
  # Best effort: TERM first, wait, then KILL stragglers
  echo "$existing" | xargs kill 2>/dev/null || true
  sleep 1
  still=$(lsof -ti "tcp:$PORT" 2>/dev/null || true)
  if [ -n "$still" ]; then
    echo "project-console: force-killing stragglers on port $PORT"
    echo "$still" | xargs kill -9 2>/dev/null || true
    sleep 1
  fi
fi

echo "project-console: starting on port $PORT..."
exec bash ./run.sh
