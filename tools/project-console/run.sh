#!/usr/bin/env bash
# project-console launcher. The FastAPI app code lives in the skill at
# $CLAUDE_PROJECT_DIR/.claude/skills/project-console/console/; this script
# injects that directory onto sys.path and runs uvicorn.
set -euo pipefail
cd "$(dirname "$0")"

PROJECT_ROOT="$(cd ../.. && pwd)"
export CLAUDE_PROJECT_DIR="$PROJECT_ROOT"

SKILL_CONSOLE="$PROJECT_ROOT/.claude/skills/project-console/console"
if [ ! -d "$SKILL_CONSOLE" ]; then
    echo "Error: project-console skill not installed at $SKILL_CONSOLE" >&2
    echo "Run /sync-skills pull, or copy .claude/skills/project-console/ from the registry." >&2
    exit 1
fi

uv sync
export PYTHONPATH="$(dirname "$SKILL_CONSOLE"):${PYTHONPATH:-}"
exec uv run uvicorn console.app:app --reload --host 127.0.0.1 --port 8765
