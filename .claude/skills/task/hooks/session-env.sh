#!/bin/bash
# session-env.sh — SessionStart hook that exports session ID as an env var
#
# Reads session_id from the hook JSON input (provided by Claude Code) and
# exports it via CLAUDE_ENV_FILE so all Bash tool calls can access it.
#
# The hook JSON session_id is consistent across parent and subagent sessions,
# which is critical — the task gate must see the same ID everywhere.
#
# Falls back to uuidgen only if the hook JSON has no session_id (shouldn't
# happen, but keeps us self-sufficient).

INPUT=$(cat)

if [ -n "$CLAUDE_ENV_FILE" ]; then
  SESSION_ID=$(echo "$INPUT" | jq -r '.session_id // empty')
  if [ -z "$SESSION_ID" ]; then
    SESSION_ID=$(uuidgen | tr '[:upper:]' '[:lower:]')
  fi
  echo "export CLAUDE_SESSION_ID=$SESSION_ID" >> "$CLAUDE_ENV_FILE"
fi

exit 0
