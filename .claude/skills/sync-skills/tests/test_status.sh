#!/usr/bin/env bash
# test_status.sh — Smoke tests for `sync.sh status`.
#
# Builds a self-contained world: a fake "project" git repo with a fake
# `.claude/skills` tree, a fake "registry" git repo with a fake `skills`
# tree, and a fake `project.yml` pointing at the registry. Then exercises
# four scenarios:
#
#   1. all-synced       → exit 0, "Overall: SYNCED"
#   2. project-dirty    → exit 1, lists modifications
#   3. project-ahead    → exit 1, mentions "AHEAD"
#   4. drift            → exit 1, mentions "DRIFT"
#
# Self-contained — no network, no real hitachi clone needed. Uses
# STATUS_NO_FETCH=1 to skip git fetch (origin in tests is a local bare repo).
#
# Run: bash .claude/skills/sync-skills/tests/test_status.sh
# Exit: 0 if every case passes, 1 on first failure.

set -uo pipefail

# Path to the sync.sh under test (project root, relative to this file).
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SYNC_SCRIPT="$SCRIPT_DIR/../scripts/sync.sh"

# Counters
PASS=0
FAIL=0
FAILED_CASES=()

# ─── Test harness ────────────────────────────────────────────────────────

# Build a fresh world. Sets the following globals:
#   WORLD            tmpdir root
#   PROJECT_ROOT     tmpdir/project (git repo, has .claude/, project.yml)
#   REGISTRY_ROOT    tmpdir/hitachi (git repo, has skills/ + agents/)
#   PROJECT_REMOTE   bare repo serving as project's origin
#   REGISTRY_REMOTE  bare repo serving as hitachi's origin
_setup_world() {
  WORLD="$(mktemp -d)"
  PROJECT_ROOT="$WORLD/project"
  REGISTRY_ROOT="$WORLD/hitachi"
  PROJECT_REMOTE="$WORLD/project.git"
  REGISTRY_REMOTE="$WORLD/hitachi.git"

  # ── Bare remotes
  git init --bare --quiet --initial-branch=main "$PROJECT_REMOTE"
  git init --bare --quiet --initial-branch=main "$REGISTRY_REMOTE"

  # ── Registry working repo
  mkdir -p "$REGISTRY_ROOT/skills/example/scripts"
  mkdir -p "$REGISTRY_ROOT/agents"
  cat >"$REGISTRY_ROOT/skills/example/SKILL.md" <<'EOF'
---
name: example
version: 1
---
# Example skill
EOF
  cat >"$REGISTRY_ROOT/agents/example-agent.md" <<'EOF'
# Example agent
EOF
  git -C "$REGISTRY_ROOT" init --quiet --initial-branch=main
  git -C "$REGISTRY_ROOT" config user.email "test@example.com"
  git -C "$REGISTRY_ROOT" config user.name "Test"
  git -C "$REGISTRY_ROOT" add -A
  git -C "$REGISTRY_ROOT" commit --quiet -m "initial registry"
  git -C "$REGISTRY_ROOT" remote add origin "$REGISTRY_REMOTE"
  git -C "$REGISTRY_ROOT" push --quiet -u origin main

  # ── Project working repo: copy the same skill content so they're in sync
  mkdir -p "$PROJECT_ROOT/.claude/skills/example/scripts"
  mkdir -p "$PROJECT_ROOT/.claude/agents"
  cp "$REGISTRY_ROOT/skills/example/SKILL.md" "$PROJECT_ROOT/.claude/skills/example/SKILL.md"
  cp "$REGISTRY_ROOT/agents/example-agent.md" "$PROJECT_ROOT/.claude/agents/example-agent.md"

  # Symlink sync-skills into place — the script under test resolves itself
  # via $BASH_SOURCE/../../../.. so we must keep that 4-level structure.
  mkdir -p "$PROJECT_ROOT/.claude/skills/sync-skills/scripts"
  cp "$SYNC_SCRIPT" "$PROJECT_ROOT/.claude/skills/sync-skills/scripts/sync.sh"
  chmod +x "$PROJECT_ROOT/.claude/skills/sync-skills/scripts/sync.sh"

  # Project.yml pointing at the registry working tree.
  cat >"$PROJECT_ROOT/project.yml" <<EOF
registries:
  - name: hitachi
    type: github
    repo: example/registry
    local_path: $REGISTRY_ROOT
EOF

  git -C "$PROJECT_ROOT" init --quiet --initial-branch=main
  git -C "$PROJECT_ROOT" config user.email "test@example.com"
  git -C "$PROJECT_ROOT" config user.name "Test"
  git -C "$PROJECT_ROOT" add -A
  git -C "$PROJECT_ROOT" commit --quiet -m "initial project"
  git -C "$PROJECT_ROOT" remote add origin "$PROJECT_REMOTE"
  git -C "$PROJECT_ROOT" push --quiet -u origin main
}

_teardown_world() {
  if [[ -n "${WORLD:-}" && -d "$WORLD" ]]; then
    rm -rf "$WORLD"
  fi
}

# Run sync.sh status from inside the world. Echoes stdout, stderr, exit code.
_run_status() {
  STATUS_NO_FETCH=1 bash "$PROJECT_ROOT/.claude/skills/sync-skills/scripts/sync.sh" status 2>&1
}

# Expect: command's stdout contains string AND exit code matches.
_assert() {
  local case_name="$1"
  local want_exit="$2"
  local want_substring="$3"
  local got_exit="$4"
  local got_output="$5"

  local ok=1
  if [[ "$got_exit" != "$want_exit" ]]; then
    ok=0
  fi
  if ! grep -qF -- "$want_substring" <<<"$got_output"; then
    ok=0
  fi

  if [[ $ok -eq 1 ]]; then
    PASS=$((PASS + 1))
    echo "  PASS: $case_name"
  else
    FAIL=$((FAIL + 1))
    FAILED_CASES+=("$case_name")
    echo "  FAIL: $case_name"
    echo "    want_exit=$want_exit  got_exit=$got_exit"
    echo "    want_substring: $want_substring"
    echo "    got_output (first 30 lines):"
    head -30 <<<"$got_output" | sed 's/^/      /'
  fi
}

# ─── Cases ───────────────────────────────────────────────────────────────

case_all_synced() {
  echo "Case 1: all synced"
  _setup_world
  local out exit_code
  out="$(_run_status)" && exit_code=0 || exit_code=$?
  _assert "all_synced exits 0"          "0" "Overall: SYNCED"      "$exit_code" "$out"
  _assert "all_synced project SYNCED"   "0" "Status:        SYNCED" "$exit_code" "$out"
  _assert "all_synced drift count zero" "0" "Files differing: 0"    "$exit_code" "$out"
  _teardown_world
}

case_project_dirty() {
  echo "Case 2: project working tree dirty"
  _setup_world
  echo "uncommitted change" >>"$PROJECT_ROOT/.claude/skills/example/SKILL.md"
  echo "extra untracked" >"$PROJECT_ROOT/.claude/skills/example/new.md"
  local out exit_code
  out="$(_run_status)" && exit_code=0 || exit_code=$?
  _assert "dirty exits 1"        "1" "Overall: NOT SYNCED"            "$exit_code" "$out"
  _assert "dirty mentions DIRTY" "1" "Working tree:  DIRTY"           "$exit_code" "$out"
  _assert "dirty lists mod"      "1" "skills/example/SKILL.md"        "$exit_code" "$out"
  _teardown_world
}

case_project_ahead() {
  echo "Case 3: project local ahead of remote"
  _setup_world
  # Add a clean commit locally without pushing
  echo "ahead change" >>"$PROJECT_ROOT/.claude/skills/example/SKILL.md"
  git -C "$PROJECT_ROOT" add -A
  git -C "$PROJECT_ROOT" commit --quiet -m "ahead commit"
  local out exit_code
  out="$(_run_status)" && exit_code=0 || exit_code=$?
  _assert "ahead exits 1"        "1" "Overall: NOT SYNCED" "$exit_code" "$out"
  _assert "ahead mentions AHEAD" "1" "Status:        AHEAD" "$exit_code" "$out"
  _teardown_world
}

case_skill_drift() {
  echo "Case 4: skill drift between local and registry"
  _setup_world
  # Diverge the registry version of the example skill (simulating UPSTREAM_NEWER)
  echo "registry-only addition" >>"$REGISTRY_ROOT/skills/example/SKILL.md"
  git -C "$REGISTRY_ROOT" add -A
  git -C "$REGISTRY_ROOT" commit --quiet -m "registry advance"
  git -C "$REGISTRY_ROOT" push --quiet origin main
  local out exit_code
  out="$(_run_status)" && exit_code=0 || exit_code=$?
  _assert "drift exits 1"           "1" "Overall: NOT SYNCED"   "$exit_code" "$out"
  _assert "drift mentions DRIFT"    "1" "Status:          DRIFT" "$exit_code" "$out"
  _assert "drift names skill file"  "1" "skills/example/SKILL.md" "$exit_code" "$out"
  _teardown_world
}

# ─── Run ─────────────────────────────────────────────────────────────────

echo "test_status.sh"
echo "=============="
echo

case_all_synced
case_project_dirty
case_project_ahead
case_skill_drift

echo
echo "Results: $PASS passed, $FAIL failed"
if [[ $FAIL -gt 0 ]]; then
  echo "Failed cases:"
  for c in "${FAILED_CASES[@]}"; do
    echo "  - $c"
  done
  exit 1
fi
exit 0
