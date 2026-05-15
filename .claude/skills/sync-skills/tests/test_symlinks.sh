#!/usr/bin/env bash
# test_symlinks.sh — Regression tests for symlink-aware drift detection.
#
# Pre-fix bug: `cmd_check` hashed `git show <ref>:<path>` (which returns the
# symlink TARGET STRING for mode 120000) against `sha1sum <local-path>` (which
# follows symlinks and hashes resolved content). This produced false-positive
# drift on every git-tracked symlink AND false negatives whenever upstream
# tracked a regular file but local was a symlink-to-the-same-content (or vice
# versa).
#
# Post-fix: cmd_check uses filesystem-cat compare on both sides — `< file`
# redirection follows symlinks transparently, so what's compared is the
# resolved content, not the storage layout.
#
# Cases:
#   1. both-symlinks-same-target: both repos track <path> as symlink → same
#      target → resolved content matches → NO DRIFT
#   2. both-symlinks-different-target-same-content: both symlinks but to
#      different paths whose contents happen to match → NO DRIFT
#   3. type-mismatch-same-content: upstream has regular file, local has
#      symlink to a file with identical content → NO DRIFT
#   4. real-content-divergence-with-symlinks: both symlinks but resolved
#      content actually differs → REAL DRIFT (UPSTREAM_NEWER reported)
#
# Run: bash .claude/skills/sync-skills/tests/test_symlinks.sh
# Exit: 0 if every case passes, 1 on first failure.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SYNC_SCRIPT="$SCRIPT_DIR/../scripts/sync.sh"

PASS=0
FAIL=0
FAILED_CASES=()

# ─── Test harness ────────────────────────────────────────────────────────

# Build a minimal world: one project + one registry, both git repos. Sets:
#   WORLD          tmpdir root
#   PROJECT_ROOT   project working tree
#   REGISTRY_ROOT  registry working tree
_setup_world() {
  WORLD="$(mktemp -d)"
  PROJECT_ROOT="$WORLD/project"
  REGISTRY_ROOT="$WORLD/hitachi"
  REGISTRY_REMOTE="$WORLD/hitachi.git"
  PROJECT_REMOTE="$WORLD/project.git"

  git init --bare --quiet --initial-branch=main "$REGISTRY_REMOTE"
  git init --bare --quiet --initial-branch=main "$PROJECT_REMOTE"

  mkdir -p "$REGISTRY_ROOT/skills/example/scripts"
  mkdir -p "$REGISTRY_ROOT/agents"
  cat >"$REGISTRY_ROOT/skills/example/SKILL.md" <<'EOF'
---
name: example
version: 1
---
EOF

  mkdir -p "$PROJECT_ROOT/.claude/skills/example/scripts"
  mkdir -p "$PROJECT_ROOT/.claude/agents"
  cp "$REGISTRY_ROOT/skills/example/SKILL.md" "$PROJECT_ROOT/.claude/skills/example/SKILL.md"

  # Symlink sync-skills into place — script resolves itself via $BASH_SOURCE.
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
  # Push registry to bare remote so origin/main exists for STATUS_NO_FETCH paths.
  git -C "$REGISTRY_ROOT" remote add origin "$REGISTRY_REMOTE" 2>/dev/null || true
  git -C "$REGISTRY_ROOT" push --quiet -u origin main 2>/dev/null || true
  git -C "$PROJECT_ROOT" remote add origin "$PROJECT_REMOTE" 2>/dev/null || true
  git -C "$PROJECT_ROOT" push --quiet -u origin main 2>/dev/null || true
}

_teardown_world() {
  if [[ -n "${WORLD:-}" && -d "$WORLD" ]]; then
    rm -rf "$WORLD"
  fi
}

_run_check() {
  STATUS_NO_FETCH=1 bash "$PROJECT_ROOT/.claude/skills/sync-skills/scripts/sync.sh" check 2>&1
}

_assert_no_drift_on() {
  local case_name="$1" path="$2" out="$3"
  if grep -q -E "^(UPSTREAM_NEWER|UPSTREAM_ONLY|LOCAL_ONLY)\s+$path\b" <<<"$out"; then
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

_assert_drift_on() {
  local case_name="$1" path="$2" out="$3"
  if grep -q -E "^UPSTREAM_NEWER\s+$path\b" <<<"$out"; then
    PASS=$((PASS + 1))
    echo "  PASS: $case_name"
  else
    FAIL=$((FAIL + 1))
    FAILED_CASES+=("$case_name")
    echo "  FAIL: $case_name — expected UPSTREAM_NEWER on $path"
    echo "    got:"
    head -20 <<<"$out" | sed 's/^/      /'
  fi
}

# ─── Cases ───────────────────────────────────────────────────────────────

case_1_both_symlinks_same_target() {
  echo "Case 1: both repos track agents/example.md as symlink → same target → no drift"
  _setup_world

  # Registry: agent file lives inside skills/example/agents/, exposed via symlink at agents/
  mkdir -p "$REGISTRY_ROOT/skills/example/agents"
  echo "agent body content" >"$REGISTRY_ROOT/skills/example/agents/example.md"
  ln -s "../skills/example/agents/example.md" "$REGISTRY_ROOT/agents/example.md"

  # Project: identical layout
  mkdir -p "$PROJECT_ROOT/.claude/skills/example/agents"
  echo "agent body content" >"$PROJECT_ROOT/.claude/skills/example/agents/example.md"
  ln -s "../skills/example/agents/example.md" "$PROJECT_ROOT/.claude/agents/example.md"

  _commit_both

  local out
  out="$(_run_check)"
  _assert_no_drift_on "case 1: agents/example.md no drift" "agents/example\\.md" "$out"
  _teardown_world
}

case_2_both_symlinks_different_target_same_content() {
  echo "Case 2: both symlinks, different target paths, identical resolved content → no drift"
  _setup_world

  # Registry: symlink -> path A
  mkdir -p "$REGISTRY_ROOT/skills/example/agents"
  echo "shared content" >"$REGISTRY_ROOT/skills/example/agents/path-a.md"
  ln -s "../skills/example/agents/path-a.md" "$REGISTRY_ROOT/agents/example.md"

  # Project: symlink -> path B (different filename, same content)
  mkdir -p "$PROJECT_ROOT/.claude/skills/example/agents"
  echo "shared content" >"$PROJECT_ROOT/.claude/skills/example/agents/path-b.md"
  ln -s "../skills/example/agents/path-b.md" "$PROJECT_ROOT/.claude/agents/example.md"

  _commit_both

  local out
  out="$(_run_check)"
  _assert_no_drift_on "case 2: different targets but same content → no drift" "agents/example\\.md" "$out"
  _teardown_world
}

case_3_type_mismatch_same_content() {
  echo "Case 3: upstream regular file, local symlink to file with same content → no drift"
  _setup_world

  # Registry: regular file at agents/example.md
  echo "shared agent content" >"$REGISTRY_ROOT/agents/example.md"

  # Project: symlink at .claude/agents/example.md → identical content elsewhere in tree
  mkdir -p "$PROJECT_ROOT/.claude/skills/example/agents"
  echo "shared agent content" >"$PROJECT_ROOT/.claude/skills/example/agents/example.md"
  ln -s "../skills/example/agents/example.md" "$PROJECT_ROOT/.claude/agents/example.md"

  _commit_both

  local out
  out="$(_run_check)"
  _assert_no_drift_on "case 3: type mismatch, same content → no drift" "agents/example\\.md" "$out"
  _teardown_world
}

case_4_real_divergence_with_symlinks() {
  echo "Case 4: both symlinks but resolved content actually differs → real drift"
  _setup_world

  # Registry: symlink -> file with content A
  mkdir -p "$REGISTRY_ROOT/skills/example/agents"
  echo "upstream version" >"$REGISTRY_ROOT/skills/example/agents/example.md"
  ln -s "../skills/example/agents/example.md" "$REGISTRY_ROOT/agents/example.md"

  # Project: symlink -> file with content B (genuinely different)
  mkdir -p "$PROJECT_ROOT/.claude/skills/example/agents"
  echo "local version" >"$PROJECT_ROOT/.claude/skills/example/agents/example.md"
  ln -s "../skills/example/agents/example.md" "$PROJECT_ROOT/.claude/agents/example.md"

  _commit_both

  local out
  out="$(_run_check)"
  _assert_drift_on "case 4: divergent resolved content → UPSTREAM_NEWER" "agents/example\\.md" "$out"
  _teardown_world
}

# ─── Run ─────────────────────────────────────────────────────────────────

echo "test_symlinks.sh"
echo "================"
echo

case_1_both_symlinks_same_target
case_2_both_symlinks_different_target_same_content
case_3_type_mismatch_same_content
case_4_real_divergence_with_symlinks

echo
echo "Results: $PASS passed, $FAIL failed"
if (( FAIL > 0 )); then
  echo "Failed:"
  for c in "${FAILED_CASES[@]}"; do echo "  - $c"; done
  exit 1
fi
exit 0
