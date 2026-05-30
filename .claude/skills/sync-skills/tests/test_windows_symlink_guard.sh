#!/usr/bin/env bash
# test_windows_symlink_guard.sh — Regression test for the Windows-clone
# symlink corruption vector.
#
# Bug class (from real incident, PDLC_DEMO commit 07574e9):
#   On a Windows git clone, `core.symlinks=false` is the default — tracked
#   symlinks (mode 120000) materialize in the working tree as plain text
#   files containing the target path string. Pre-v8.3 sync.sh detected
#   symlinks via `[[ -L $path ]]` (filesystem check), which returns FALSE
#   for these files. Consequences:
#     1. cmd_analyze hashed the path-string text as a regular blob,
#        mismatched every upstream symlink blob, and reported false
#        UPSTREAM_NEWER drift.
#     2. If pulled, cmd_pull_file's `cp` overwrote the path-string with
#        upstream agent markdown. git recorded the new content under the
#        preserved 120000 index mode.
#     3. cmd_push_stage then propagated that corrupted blob upstream —
#        a "symlink" whose target string is 5 KB of agent markdown, which
#        no filesystem can check out (PATH_MAX ~4096).
#
# Fix (v8.3): detect symlinks via `_is_tracked_symlink` (index mode 120000),
# not the filesystem. `_read_symlink_target` handles both real symlinks
# (readlink) and Windows-style file-as-target-string (cat + strip newline),
# refusing implausible content (multiline / > 4096 bytes). cmd_push_stage
# refuses to push corrupted symlinks with a clear remediation message.
#
# Strategy: this test simulates the Windows on-disk state directly — a
# path tracked as mode 120000 in the index, but materialized as a regular
# text file in the working tree. Achieved by:
#   1. Create a real symlink in the registry, commit it (mode 120000).
#   2. In the project: clone the registry layout, but `rm` the symlink and
#      write a regular file with the target-path string as content.
#   3. The index still has mode 120000; the WT is a plain file. Identical
#      to what a Windows clone would produce.
#
# Cases:
#   1. Windows-style local symlink, content matches upstream symlink target
#      → cmd_analyze must hash via symlink-blob format → NO false drift
#   2. Windows-style local symlink, content was OVERWRITTEN with arbitrary
#      content (the vlad scenario) → cmd_push_stage must REFUSE with exit 8
#   3. Windows-style local symlink, multi-line corrupt content
#      → cmd_push_stage must REFUSE
#   4. Windows-style local symlink, oversized content (> 4096 bytes)
#      → cmd_push_stage must REFUSE
#
# Run: bash .claude/skills/sync-skills/tests/test_windows_symlink_guard.sh
# Exit: 0 if every case passes, 1 on first failure.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SYNC_SCRIPT="$SCRIPT_DIR/../scripts/sync.sh"

PASS=0
FAIL=0
FAILED_CASES=()

# ─── Test harness ────────────────────────────────────────────────────────

_setup_world() {
  WORLD="$(mktemp -d)"
  PROJECT_ROOT="$WORLD/project"
  REGISTRY_ROOT="$WORLD/hitachi"
  REGISTRY_REMOTE="$WORLD/hitachi.git"
  PROJECT_REMOTE="$WORLD/project.git"

  git init --bare --quiet --initial-branch=main "$REGISTRY_REMOTE"
  git init --bare --quiet --initial-branch=main "$PROJECT_REMOTE"

  mkdir -p "$REGISTRY_ROOT/skills/example/agents"
  mkdir -p "$REGISTRY_ROOT/agents"
  cat >"$REGISTRY_ROOT/skills/example/SKILL.md" <<'EOF'
---
name: example
version: 1
---
EOF

  mkdir -p "$PROJECT_ROOT/.claude/skills/example/agents"
  mkdir -p "$PROJECT_ROOT/.claude/agents"
  cp "$REGISTRY_ROOT/skills/example/SKILL.md" "$PROJECT_ROOT/.claude/skills/example/SKILL.md"

  mkdir -p "$PROJECT_ROOT/.claude/skills/sync-skills/scripts"
  cp "$SYNC_SCRIPT" "$PROJECT_ROOT/.claude/skills/sync-skills/scripts/sync.sh"
  chmod +x "$PROJECT_ROOT/.claude/skills/sync-skills/scripts/sync.sh"

  cat >"$PROJECT_ROOT/project.yml" <<EOF
registries:
  - name: hitachi
    type: github
    repo: example/registry
    local_path: $REGISTRY_ROOT
EOF
}

_commit_both() {
  for repo in "$REGISTRY_ROOT" "$PROJECT_ROOT"; do
    git -C "$repo" init --quiet --initial-branch=main 2>/dev/null || true
    git -C "$repo" config user.email "test@example.com"
    git -C "$repo" config user.name "Test"
    git -C "$repo" add -A
    git -C "$repo" commit --quiet -m "world setup" 2>/dev/null || true
  done
  git -C "$REGISTRY_ROOT" remote add origin "$REGISTRY_REMOTE" 2>/dev/null || true
  git -C "$REGISTRY_ROOT" push --quiet -u origin main 2>/dev/null || true
  git -C "$PROJECT_ROOT" remote add origin "$PROJECT_REMOTE" 2>/dev/null || true
  git -C "$PROJECT_ROOT" push --quiet -u origin main 2>/dev/null || true
}

# Convert a tracked symlink in the working tree to a Windows-style "plain
# file containing the target path" — simulates core.symlinks=false on a
# repo whose index has mode 120000 for that path.
#
# After this:
#   - Index still has mode 120000 (git's view: "this is a symlink")
#   - Working tree has a regular text file (filesystem's view)
#   - `[[ -L $path ]]` is FALSE
#   - `_is_tracked_symlink` is TRUE
_make_windows_style_symlink() {
  local path="$1" target="$2"
  rm -f "$path"
  # Write target as content, no trailing newline (matches Windows git default)
  printf '%s' "$target" > "$path"
}

# Overwrite a Windows-style symlink's content with arbitrary text, simulating
# what happens when an editor (or buggy sync tool) treats it as a regular
# file and writes new content. This is the vlad-commit corruption.
_corrupt_windows_style_symlink() {
  local path="$1" content="$2"
  printf '%s' "$content" > "$path"
}

_teardown_world() {
  if [[ -n "${WORLD:-}" && -d "$WORLD" ]]; then
    rm -rf "$WORLD"
  fi
}

_run_check() {
  STATUS_NO_FETCH=1 bash "$PROJECT_ROOT/.claude/skills/sync-skills/scripts/sync.sh" check 2>&1
}

_run_push_stage() {
  local rel="$1"
  STATUS_NO_FETCH=1 bash "$PROJECT_ROOT/.claude/skills/sync-skills/scripts/sync.sh" push-stage "$rel" 2>&1
}

_assert_no_drift_on() {
  local case_name="$1" path="$2" out="$3"
  if grep -q -E "^(UPSTREAM_NEWER|UPSTREAM_ONLY|LOCAL_ONLY)\s+${path}\b" <<<"$out"; then
    FAIL=$((FAIL + 1))
    FAILED_CASES+=("$case_name")
    echo "  FAIL: $case_name — expected no drift on $path"
    echo "    got:"
    grep -E "$path" <<<"$out" | sed 's/^/      /'
  else
    PASS=$((PASS + 1))
    echo "  PASS: $case_name"
  fi
}

_assert_push_stage_refused() {
  local case_name="$1" rel="$2"
  local out rc
  out="$(_run_push_stage "$rel")"
  rc=$?
  if [[ "$rc" -eq 8 ]] && grep -q "refusing to stage corrupted symlink" <<<"$out"; then
    PASS=$((PASS + 1))
    echo "  PASS: $case_name (exit=8, refusal message present)"
  else
    FAIL=$((FAIL + 1))
    FAILED_CASES+=("$case_name")
    echo "  FAIL: $case_name — expected exit 8 with refusal message"
    echo "    exit=$rc"
    echo "    out:"
    sed 's/^/      /' <<<"$out"
  fi
}

# ─── Cases ───────────────────────────────────────────────────────────────

case_1_windows_style_clean_no_drift() {
  echo "Case 1: Windows-style local symlink, content matches upstream target → no false drift"
  _setup_world

  echo "agent body" >"$REGISTRY_ROOT/skills/example/agents/example.md"
  ln -s "../skills/example/agents/example.md" "$REGISTRY_ROOT/agents/example.md"

  echo "agent body" >"$PROJECT_ROOT/.claude/skills/example/agents/example.md"
  ln -s "../skills/example/agents/example.md" "$PROJECT_ROOT/.claude/agents/example.md"

  _commit_both

  # Now flip the project's symlink to Windows-style (regular file with path string).
  _make_windows_style_symlink \
    "$PROJECT_ROOT/.claude/agents/example.md" \
    "../skills/example/agents/example.md"

  local out
  out="$(_run_check)"
  _assert_no_drift_on "case-1: agents/example.md (Windows-style, content matches)" \
    "agents/example.md" "$out"

  _teardown_world
}

case_2_corrupted_windows_symlink_refused() {
  echo "Case 2: Windows-style local symlink overwritten with 5 KB of agent markdown → push-stage refuses"
  _setup_world

  echo "agent body" >"$REGISTRY_ROOT/skills/example/agents/example.md"
  ln -s "../skills/example/agents/example.md" "$REGISTRY_ROOT/agents/example.md"

  echo "agent body" >"$PROJECT_ROOT/.claude/skills/example/agents/example.md"
  ln -s "../skills/example/agents/example.md" "$PROJECT_ROOT/.claude/agents/example.md"

  _commit_both

  # Simulate the vlad corruption: file is tracked as 120000, but content is
  # 5+ KB of arbitrary markdown (the resolved agent definition).
  _make_windows_style_symlink \
    "$PROJECT_ROOT/.claude/agents/example.md" \
    "../skills/example/agents/example.md"

  local corrupt_content="---
name: example
description: A fake long agent definition that should not become a symlink target.
"
  # Pad to > 4096 bytes
  while (( ${#corrupt_content} < 5000 )); do
    corrupt_content+=$'Some agent prose line that explains a thing.\n'
  done
  _corrupt_windows_style_symlink \
    "$PROJECT_ROOT/.claude/agents/example.md" \
    "$corrupt_content"

  # Prep hitachi for a push (cmd_push_stage requires it to exist)
  git -C "$REGISTRY_ROOT" checkout -b sync/test-corrupt 2>/dev/null

  _assert_push_stage_refused "case-2: oversized symlink content refused" "agents/example.md"

  _teardown_world
}

case_3_multiline_corrupt_refused() {
  echo "Case 3: Windows-style local symlink with multi-line content → push-stage refuses"
  _setup_world

  echo "agent body" >"$REGISTRY_ROOT/skills/example/agents/example.md"
  ln -s "../skills/example/agents/example.md" "$REGISTRY_ROOT/agents/example.md"

  echo "agent body" >"$PROJECT_ROOT/.claude/skills/example/agents/example.md"
  ln -s "../skills/example/agents/example.md" "$PROJECT_ROOT/.claude/agents/example.md"

  _commit_both

  _make_windows_style_symlink \
    "$PROJECT_ROOT/.claude/agents/example.md" \
    "../skills/example/agents/example.md"

  # Even small multiline content is suspicious — a symlink target is a single path string.
  _corrupt_windows_style_symlink \
    "$PROJECT_ROOT/.claude/agents/example.md" \
    "line one
line two
line three"

  git -C "$REGISTRY_ROOT" checkout -b sync/test-multiline 2>/dev/null

  _assert_push_stage_refused "case-3: multiline symlink content refused" "agents/example.md"

  _teardown_world
}

case_4_real_symlink_still_works() {
  echo "Case 4: real Linux symlink (mode 120000 + filesystem -L) → push-stage succeeds, no false refusal"
  _setup_world

  echo "agent body" >"$REGISTRY_ROOT/skills/example/agents/example.md"
  ln -s "../skills/example/agents/example.md" "$REGISTRY_ROOT/agents/example.md"

  echo "agent body" >"$PROJECT_ROOT/.claude/skills/example/agents/example.md"
  ln -s "../skills/example/agents/example.md" "$PROJECT_ROOT/.claude/agents/example.md"

  _commit_both

  git -C "$REGISTRY_ROOT" checkout -b sync/test-real-symlink 2>/dev/null

  local out rc
  out="$(_run_push_stage "agents/example.md")"
  rc=$?
  if [[ "$rc" -eq 0 ]] && grep -q "^staged: agents/example.md" <<<"$out"; then
    PASS=$((PASS + 1))
    echo "  PASS: case-4: real symlink staged without refusal"
  else
    FAIL=$((FAIL + 1))
    FAILED_CASES+=("case-4")
    echo "  FAIL: case-4 — expected exit 0 and 'staged:' line"
    echo "    exit=$rc"
    echo "    out:"
    sed 's/^/      /' <<<"$out"
  fi

  _teardown_world
}

# ─── Runner ──────────────────────────────────────────────────────────────

main() {
  case_1_windows_style_clean_no_drift
  case_2_corrupted_windows_symlink_refused
  case_3_multiline_corrupt_refused
  case_4_real_symlink_still_works

  echo
  echo "─── Summary ───────────────────────────────────────────────────────"
  echo "Passed: $PASS"
  echo "Failed: $FAIL"
  if (( FAIL > 0 )); then
    echo "Failed cases:"
    for c in "${FAILED_CASES[@]}"; do
      echo "  - $c"
    done
    exit 1
  fi
  echo "All cases passed."
}

main "$@"
