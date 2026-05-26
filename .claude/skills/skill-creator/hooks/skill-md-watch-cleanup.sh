#!/usr/bin/env bash
# SessionEnd hook — purge per-session armed-state file for skill-creator's
# SKILL.md watch hook. Mirrors the pattern in task skill's session-cleanup.sh.
#
# Reads SessionEnd JSON from stdin to extract session_id, removes the matching
# .state/skill-creator-armed-{session_id}.json file. Always exits 0.
set -euo pipefail

# Read JSON payload from stdin (SessionEnd hook contract)
payload="$(cat)"

# Extract session_id; fall back to env var if jq absent or payload malformed
if command -v jq >/dev/null 2>&1; then
  session_id="$(printf '%s' "$payload" | jq -r '.session_id // empty' 2>/dev/null || true)"
else
  session_id=""
fi
session_id="${session_id:-${CLAUDE_SESSION_ID:-}}"

if [ -z "$session_id" ]; then
  exit 0
fi

project_dir="${CLAUDE_PROJECT_DIR:-$PWD}"
state_file="$project_dir/.state/skill-creator-armed-$session_id.json"

if [ -f "$state_file" ]; then
  rm -f "$state_file"
fi

exit 0
