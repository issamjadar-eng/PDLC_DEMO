#!/bin/bash
# session-briefing.sh — SessionStart hook for the /digest skill.
#
# Emits a daily briefing to stdout (rendered as SessionStart system context by
# Claude Code) at most once per 12 hours per user. User identity is resolved
# via `git config user.email`; throttle state lives at
# `.state/briefing-last-shown-<email-slug>.txt` (relocated from .claude/state/
# in ben/083 to escape .claude/** sensitive-file guard).
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

# Resolve user identity via project.yml roster (shared helper).
# resolve_user.py --task-folder emits the roster task_folder on match, or
# a stable email-slug fallback otherwise; either value is fine as a
# state-file key. If the helper is missing, fall back to 'unknown-user'.
# Lives in shared/scripts/ since task ben/098 (cross-skill: digest + secops).
RESOLVER="$PROJECT_DIR/.claude/skills/shared/scripts/resolve_user.py"
SLUG=""
if [[ -f "$RESOLVER" ]]; then
  SLUG="$(python3 "$RESOLVER" --task-folder 2>/dev/null || true)"
fi
[[ -z "$SLUG" ]] && SLUG="unknown-user"

STATE_DIR="$PROJECT_DIR/.state"
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

# Sync check — runs ONLY when we're actually building a brief (throttle has
# elapsed), not on every session. Non-blocking: we READ git's ref state
# (populated by the previous session's background fetch) and SPAWN a new
# background fetch for the next session to consume. This avoids the up-to-5s
# block that the old foreground `timeout 5 git fetch` imposed at SessionStart.
#
# First-run behavior: no prior fetch → @{u} may be stale or missing →
# rev-list returns empty → no sync notice. One cycle later the background
# fetch has populated refs and the notice appears correctly.
SYNC_NOTICE=""
# Spawn a non-blocking background fetch. Subshell + disown detaches it from
# the hook's process group so the hook can exit cleanly. stdout/stderr are
# muted so the background job can't leak into the SessionStart system context.
( git fetch --quiet >/dev/null 2>&1 & ) 2>/dev/null || true
# Read ref state from the last fetch (may be empty on first run).
BEHIND="$(git rev-list --count HEAD..@{u} 2>/dev/null || true)"
UPSTREAM="$(git rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null || true)"
BRANCH="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || true)"
if [[ -n "$UPSTREAM" ]]; then
  if [[ -n "$BEHIND" && "$BEHIND" =~ ^[0-9]+$ && "$BEHIND" -gt 0 ]]; then
    if [[ "$BEHIND" == "1" ]]; then
      CHANGE_WORD="change"
      COMMIT_WORD="commit"
    else
      CHANGE_WORD="changes"
      COMMIT_WORD="commits"
    fi
    SYNC_NOTICE=$(cat <<EOF

## Heads up — your project folder is out of date

Your teammates have shared **$BEHIND new $CHANGE_WORD** on the \`$BRANCH\` branch that you don't have yet on your computer.
Pulling them in now means you'll be working from the same version everyone else is on.

<!-- CLAUDE INSTRUCTION — sync-check
The local branch is $BEHIND $COMMIT_WORD behind $UPSTREAM. On your very next turn, before doing any other work:
  1. Use AskUserQuestion to ask the user, in friendly business-user language, whether they'd like to pull the latest updates from the project repo now. Offer "Yes, pull now", "Not right now", and "Show me what changed first" as options.
  2. If they pick "Show me what changed first", run: git log --oneline --no-decorate HEAD..$UPSTREAM — then re-ask.
  3. If they say yes, run: git pull --ff-only  — and report the result in plain language (e.g., "Pulled N updates — you're all caught up.").
  4. If the pull isn't a fast-forward, do NOT force it. Explain plainly that their local changes and the team's changes have diverged, and ask how they'd like to proceed.
  5. If they decline, just acknowledge and continue with whatever they originally asked for.
-->
EOF
)
  fi
fi

# If the output is just the "No new commits" pattern, skip emission (but still
# surface the sync notice if one was generated — sync state is independent of
# whether there were commits to summarize).
if echo "$OUTPUT" | grep -q "^No new commits" ; then
  if [[ -n "$SYNC_NOTICE" ]]; then
    echo "---"
    echo ""
    echo "$SYNC_NOTICE"
    echo "---"
  fi
  # still update the throttle so we don't re-compute until 12h pass
else
  # Emit a separator so the briefing stands out in the session log
  echo "---"
  echo ""
  echo "$OUTPUT"
  if [[ -n "$SYNC_NOTICE" ]]; then
    echo "$SYNC_NOTICE"
  fi
  echo "---"
fi

# Update the throttle state — stash the current ISO timestamp as file contents
date -u +"%Y-%m-%dT%H:%M:%S" > "$STATE_FILE"

exit 0
