#!/bin/bash
# session-briefing.sh — SessionStart hook for the /digest skill.
#
# Emits a daily briefing to stdout (rendered as SessionStart system context by
# Claude Code) at most once per 12 hours per user. User identity is resolved
# via `git config user.email`; throttle state lives at
# `.claude/state/briefing-last-shown-<email-slug>.txt`.
#
# Silent unless ≥12h since last briefing for this user. No errors on
# unconfigured user email (falls back to 'unknown-user' slug).
#
# Requires: git, python3. Falls back silently if either is missing.

set -eu

# Resolve project root. Prefer CLAUDE_PROJECT_DIR (set by CC hook env) else cd's dir.
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-}"
if [[ -z "$PROJECT_DIR" ]]; then
  PROJECT_DIR="$(git rev-parse --show-toplevel 2>/dev/null || true)"
fi
if [[ -z "$PROJECT_DIR" || ! -d "$PROJECT_DIR" ]]; then
  exit 0
fi
cd "$PROJECT_DIR"

# Require git and python3; bail silently otherwise
if ! command -v git >/dev/null 2>&1 || ! command -v python3 >/dev/null 2>&1; then
  exit 0
fi

# Resolve user identity via project.yml roster (secops-owned helper).
# Falls back to the raw git email slug if the helper is missing or no roster
# match is found. SLUG is the state-file key — stable per team member, not
# per git-config-of-the-day.
RESOLVER="$PROJECT_DIR/.claude/skills/secops/scripts/resolve_user.py"
if [[ -x "$RESOLVER" || -f "$RESOLVER" ]]; then
  SLUG="$(python3 "$RESOLVER" --task-folder 2>/dev/null || true)"
fi
if [[ -z "$SLUG" ]]; then
  EMAIL="$(git config user.email 2>/dev/null || true)"
  [[ -z "$EMAIL" ]] && EMAIL="unknown-user"
  SLUG="$(echo -n "$EMAIL" | tr '@.' '--' | tr -c 'A-Za-z0-9-' '-' | sed 's/^-*//; s/-*$//')"
fi

STATE_DIR="$PROJECT_DIR/.claude/state"
STATE_FILE="$STATE_DIR/briefing-last-shown-$SLUG.txt"
mkdir -p "$STATE_DIR"

# Throttle check: if state file exists and is less than 12h old, exit silently
if [[ -f "$STATE_FILE" ]]; then
  LAST_MTIME="$(stat -c %Y "$STATE_FILE" 2>/dev/null || stat -f %m "$STATE_FILE" 2>/dev/null || echo 0)"
  NOW="$(date +%s)"
  AGE=$(( NOW - LAST_MTIME ))
  TWELVE_HOURS=$(( 12 * 3600 ))
  if [[ "$AGE" -lt "$TWELVE_HOURS" ]]; then
    exit 0
  fi
  # Use the stored ISO timestamp from inside the file as --since
  SINCE="$(cat "$STATE_FILE" 2>/dev/null || true)"
else
  SINCE=""
fi

# Build the briefing. If there are no commits since --since, digest.py still
# emits a short "No new commits" message — we suppress that here to keep the
# session start clean.
SCRIPT="$PROJECT_DIR/.claude/skills/digest/scripts/digest.py"
if [[ ! -x "$SCRIPT" && -f "$SCRIPT" ]]; then
  chmod +x "$SCRIPT" 2>/dev/null || true
fi
if [[ ! -f "$SCRIPT" ]]; then
  exit 0
fi

if [[ -n "$SINCE" ]]; then
  OUTPUT="$(python3 "$SCRIPT" --since "$SINCE" 2>/dev/null || true)"
else
  OUTPUT="$(python3 "$SCRIPT" 2>/dev/null || true)"
fi

# If the output is just the "No new commits" pattern, skip emission
if echo "$OUTPUT" | grep -q "^No new commits" ; then
  : # still update the throttle so we don't re-compute until 12h pass
else
  # Emit a separator so the briefing stands out in the session log
  echo "---"
  echo ""
  echo "$OUTPUT"
  echo "---"
fi

# Update the throttle state — stash the current ISO timestamp as file contents
date -u +"%Y-%m-%dT%H:%M:%S" > "$STATE_FILE"

exit 0
