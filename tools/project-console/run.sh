#!/usr/bin/env bash
# project-console launcher. The FastAPI app code lives in the skill at
# $CLAUDE_PROJECT_DIR/.claude/skills/project-console/console/; this script
# injects that directory onto sys.path and runs uvicorn.
#
# Port is read from console.yaml `server.port` (falls back to 8765). Use
# `start.sh` for an idempotent launch that stops any existing listener first.
set -euo pipefail
cd "$(dirname "$0")"

# Derive project root (where project.yml lives)
PROJECT_ROOT="$(cd ../.. && pwd)"
export CLAUDE_PROJECT_DIR="$PROJECT_ROOT"

SKILL_CONSOLE="$PROJECT_ROOT/.claude/skills/project-console/console"
if [ ! -d "$SKILL_CONSOLE" ]; then
    echo "Error: project-console skill not installed at $SKILL_CONSOLE" >&2
    echo "Run /sync-skills pull, or copy .claude/skills/project-console/ from the registry." >&2
    exit 1
fi

# Resolve port from console.yaml (falls back to 8765). Keep this block in sync
# with the matching one in start.sh.
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

HOST=127.0.0.1
if [ -f console.yaml ]; then
  discovered_host=$(awk '
    /^server:/ { s=1; next }
    /^[^[:space:]]/ && s { s=0 }
    s && /host:/ { sub(/^[[:space:]]*host:[[:space:]]*/, ""); sub(/[[:space:]]*#.*$/, ""); gsub(/["'\'']/, ""); print; exit }
  ' console.yaml 2>/dev/null || true)
  if [ -n "$discovered_host" ]; then
    HOST="$discovered_host"
  fi
fi

uv sync

# Strip macOS Finder junk (Icon\r, AppleDouble ._*) that can crash
# jsonschema.iterdir() when they show up inside site-packages. Cheap no-op
# on non-macOS machines or clean venvs.
if [ -d .venv ]; then
  find .venv \( -name $'Icon\r' -o -name '._*' \) -print -delete 2>/dev/null | head -20 >/dev/null || true
fi

export PYTHONPATH="$SKILL_CONSOLE/..:${PYTHONPATH:-}"
echo "project-console: launching on http://$HOST:$PORT ..."
# uvicorn --reload watches cwd (tools/project-console/) recursively. Exclude
# trace-matrix/ because the `Initialize with Claude` flow writes adapters
# there at runtime and we don't want the file write to kill the in-flight
# SSE stream. Also exclude common venv/cache dirs.
# The console package lives under the skill folder, OUTSIDE this cwd; uvicorn's
# default --reload watches the cwd only, so Python changes (loaders, routers)
# never hot-reloaded while Jinja templates did. Watch both.
exec uv run uvicorn console.app:app --reload \
  --reload-dir "$SKILL_CONSOLE" \
  --reload-dir . \
  --reload-exclude 'trace-matrix/*' \
  --reload-exclude 'trace-matrix/**/*' \
  --reload-exclude '.venv/*' \
  --reload-exclude '.venv/**/*' \
  --reload-exclude '__pycache__/*' \
  --reload-exclude '.data/*' \
  --host "$HOST" --port "$PORT"
