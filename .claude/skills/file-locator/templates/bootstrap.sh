#!/usr/bin/env bash
# file-locator MCP bootstrap wrapper.
#
# This script is the `command` in .mcp.json for the file-locator server. Its
# job: guarantee the Python venv exists (building it on first launch after a
# fresh clone or repo move), then exec the real server. Because it sits on the
# MCP stdio launch path, `/mcp → Reconnect` self-heals a missing venv with no
# out-of-band shell commands — the recurring "venv gone after clone" failure
# becomes a one-time slow launch instead of a hard ENOENT.
#
# CRITICAL: stdout is the MCP JSON-RPC channel. This script must emit NOTHING
# to stdout — every diagnostic and every build subcommand's output is routed to
# stderr (>&2). The final `exec` hands an untouched stdout to server.py.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
VENV="${SCRIPT_DIR}/.venv"
VENV_PY="${VENV}/bin/python"
REQ="${SCRIPT_DIR}/requirements.txt"

# Scrub macOS Finder/iCloud `Icon\r` artifacts that crash server import on
# macOS. They repopulate whenever Finder/iCloud visits the tree, so scrub on
# every launch. (See SKILL.md § Troubleshooting, Cause 2.)
find "${VENV}" "${PROJECT_ROOT}/.claude/skills/file-locator" \
  -name $'Icon\r' -delete 2>/dev/null || true

# Fast path: venv present → fall straight through to exec with no output.
if [[ ! -x "${VENV_PY}" ]]; then
  echo "file-locator: venv missing — building at ${VENV} (first launch after clone/move)…" >&2
  if command -v uv >/dev/null 2>&1; then
    uv venv --python 3.12 "${VENV}" >&2
    uv pip install --python "${VENV_PY}" -r "${REQ}" >&2
  else
    # Fallback for machines without uv — stdlib venv + pip.
    python3 -m venv "${VENV}" >&2
    "${VENV_PY}" -m pip install --quiet --upgrade pip >&2
    "${VENV_PY}" -m pip install --quiet -r "${REQ}" >&2
  fi
  echo "file-locator: venv ready." >&2
fi

export CLAUDE_PROJECT_DIR="${PROJECT_ROOT}"
# cwd is the project root (the MCP launcher's working dir), so the
# project-root-relative server.py path passed in "$@" resolves correctly.
exec "${VENV_PY}" "$@"
