#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
VENV_PY="${SCRIPT_DIR}/.venv/bin/python"

# Preflight: purge macOS Finder/iCloud `Icon\r` artifacts that silently
# break MCP load (Claude Code's MCP loader chokes on these inside the venv
# tree). Repopulates whenever Finder visits the directory, so we scrub on
# every rebuild. See § Troubleshooting.
find "${SCRIPT_DIR}/.venv" "${PROJECT_ROOT}/.claude/skills/file-locator" \
  -name $'Icon\r' -delete 2>/dev/null || true

if [[ ! -x "${VENV_PY}" ]]; then
  echo "✗ venv not found at ${VENV_PY}"
  echo "  Run: uv venv --python 3.12 ${SCRIPT_DIR}/.venv"
  echo "       uv pip install --python ${VENV_PY} -r ${SCRIPT_DIR}/requirements.txt"
  exit 1
fi

export CLAUDE_PROJECT_DIR="${PROJECT_ROOT}"
exec "${VENV_PY}" "${PROJECT_ROOT}/.claude/skills/file-locator/scripts/rebuild.py" "$@"
