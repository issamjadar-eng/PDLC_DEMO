#!/usr/bin/env bash
# test_prune.sh — Smoke tests for `sync.sh prune`.
#
# Builds a self-contained world: a bare "registry remote", a working hitachi
# checkout with `main` plus three sync/* branches, and a minimal project that
# points at the hitachi checkout. Exercises:
#
#   1. dry-run        → classifies MERGED / UNMERGED, deletes nothing
#   2. --apply        → deletes the merged branches (local + remote), keeps unmerged
#   3. idempotent     → a second --apply finds only the unmerged branch
#   4. clean repo     → "nothing to do" when no sync/* branches exist
#
# Branch fixtures in the hitachi checkout:
#   sync/merged-a          — commit merged into main; pushed to origin   → MERGED local+remote
#   sync/merged-localonly  — commit merged into main; NOT pushed         → MERGED local
#   sync/unmerged-b        — commit never merged; pushed to origin       → UNMERGED local+remote
#
# Self-contained — no network, no real hitachi clone. Origin is a local bare repo.
# Run:  bash .claude/skills/sync-skills/tests/test_prune.sh
# Exit: 0 if every case passes, 1 on first failure.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SYNC_SCRIPT="$SCRIPT_DIR/../scripts/sync.sh"

PASS=0
FAIL=0
FAILED_CASES=()

_git() { git -C "$1" "${@:2}"; }

# Build a fresh world. Sets globals: WORLD, PROJECT_ROOT, REGISTRY_ROOT, REGISTRY_REMOTE
_setup_world() {
  WORLD="$(mktemp -d)"
  PROJECT_ROOT="$WORLD/project"
  REGISTRY_ROOT="$WORLD/hitachi"
  REGISTRY_REMOTE="$WORLD/hitachi.git"

  git init --bare --quiet --initial-branch=main "$REGISTRY_REMOTE"

  # ── Registry working repo: main with one skill
  mkdir -p "$REGISTRY_ROOT/skills/example"
  printf -- '---\nname: example\nversion: 1\n---\n' >"$REGISTRY_ROOT/skills/example/SKILL.md"
  git -C "$REGISTRY_ROOT" init --quiet --initial-branch=main
  git -C "$REGISTRY_ROOT" config user.email "test@example.com"
  git -C "$REGISTRY_ROOT" config user.name "Test"
  git -C "$REGISTRY_ROOT" add -A
  git -C "$REGISTRY_ROOT" commit --quiet -m "initial registry"
  git -C "$REGISTRY_ROOT" remote add origin "$REGISTRY_REMOTE"
  git -C "$REGISTRY_ROOT" push --quiet -u origin main

  # ── sync/merged-a — commit merged into main, pushed to origin
  git -C "$REGISTRY_ROOT" checkout --quiet -b sync/merged-a
  echo "a" >>"$REGISTRY_ROOT/skills/example/SKILL.md"
  git -C "$REGISTRY_ROOT" commit --quiet -am "merged-a change"
  git -C "$REGISTRY_ROOT" push --quiet -u origin sync/merged-a
  git -C "$REGISTRY_ROOT" checkout --quiet main
  git -C "$REGISTRY_ROOT" merge --quiet sync/merged-a

  # ── sync/merged-localonly — commit merged into main, NOT pushed
  git -C "$REGISTRY_ROOT" checkout --quiet -b sync/merged-localonly
  echo "l" >>"$REGISTRY_ROOT/skills/example/SKILL.md"
  git -C "$REGISTRY_ROOT" commit --quiet -am "merged-localonly change"
  git -C "$REGISTRY_ROOT" checkout --quiet main
  git -C "$REGISTRY_ROOT" merge --quiet sync/merged-localonly

  # ── sync/unmerged-b — commit never merged, pushed to origin
  git -C "$REGISTRY_ROOT" checkout --quiet -b sync/unmerged-b
  echo "b" >>"$REGISTRY_ROOT/skills/example/SKILL.md"
  git -C "$REGISTRY_ROOT" commit --quiet -am "unmerged-b change"
  git -C "$REGISTRY_ROOT" push --quiet -u origin sync/unmerged-b

  git -C "$REGISTRY_ROOT" push --quiet origin main
  git -C "$REGISTRY_ROOT" checkout --quiet main

  # ── Project: minimal, just needs project.yml + the sync.sh under test
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

_teardown_world() {
  [[ -n "${WORLD:-}" && -d "$WORLD" ]] && rm -rf "$WORLD"
}

_run_prune() { bash "$PROJECT_ROOT/.claude/skills/sync-skills/scripts/sync.sh" prune "$@" 2>&1; }

# _assert <case> <want_substring> <got_output>   (substring must be present)
_assert() {
  local case_name="$1" want="$2" got="$3"
  if grep -qF -- "$want" <<<"$got"; then
    PASS=$((PASS + 1)); echo "  PASS: $case_name"
  else
    FAIL=$((FAIL + 1)); FAILED_CASES+=("$case_name")
    echo "  FAIL: $case_name"
    echo "    want substring: $want"
    echo "    got:"; sed 's/^/      /' <<<"$got"
  fi
}

# _assert_absent <case> <substring> <got_output>  (substring must NOT be present)
_assert_absent() {
  local case_name="$1" bad="$2" got="$3"
  if grep -qF -- "$bad" <<<"$got"; then
    FAIL=$((FAIL + 1)); FAILED_CASES+=("$case_name")
    echo "  FAIL: $case_name (unexpected substring present: $bad)"
  else
    PASS=$((PASS + 1)); echo "  PASS: $case_name"
  fi
}

echo "test_prune.sh"
_setup_world

# ── Case 1: dry-run classifies correctly and deletes nothing
out="$(_run_prune)"
_assert        "dry-run: merged-a is MERGED"          "$(printf 'MERGED\tsync/merged-a\tlocal+remote')" "$out"
_assert        "dry-run: merged-localonly is MERGED"  "$(printf 'MERGED\tsync/merged-localonly\tlocal')" "$out"
_assert        "dry-run: unmerged-b is UNMERGED"      "$(printf 'UNMERGED\tsync/unmerged-b')"            "$out"
_assert        "dry-run: summary line"                "prune: 2 merged, 1 unmerged/superseded"           "$out"
_assert        "dry-run: offers --apply"              "(dry-run"                                         "$out"
# nothing deleted — branch still present
_assert        "dry-run: deletes nothing"             "sync/merged-a"  "$(_git "$REGISTRY_ROOT" branch --list 'sync/*')"

# ── Case 2: --apply deletes merged, keeps unmerged
out="$(_run_prune --apply)"
_assert        "apply: reports done"                  "removed 2 merged branch(es)" "$out"
locals="$(_git "$REGISTRY_ROOT" for-each-ref --format='%(refname:short)' 'refs/heads/sync/*')"
remotes="$(_git "$REGISTRY_ROOT" for-each-ref --format='%(refname:short)' 'refs/remotes/origin/sync/*')"
_assert_absent "apply: merged-a local gone"           "sync/merged-a"          "$locals"
_assert_absent "apply: merged-localonly local gone"   "sync/merged-localonly"  "$locals"
_assert        "apply: unmerged-b local kept"         "sync/unmerged-b"        "$locals"
_assert_absent "apply: merged-a remote gone"          "origin/sync/merged-a"   "$remotes"
_assert        "apply: unmerged-b remote kept"        "origin/sync/unmerged-b" "$remotes"

# ── Case 3: second --apply is idempotent — only the unmerged branch remains
out="$(_run_prune --apply)"
_assert        "idempotent: 0 merged"                 "prune: 0 merged, 1 unmerged/superseded" "$out"
_assert        "idempotent: nothing to delete"        "nothing to delete"                      "$out"

# ── Case 4: a registry with no sync/* branches reports nothing to do
_git "$REGISTRY_ROOT" branch -D sync/unmerged-b >/dev/null 2>&1
_git "$REGISTRY_ROOT" push origin --delete sync/unmerged-b >/dev/null 2>&1
out="$(_run_prune)"
_assert        "clean: nothing to do"                 "no sync/* branches — nothing to do" "$out"

_teardown_world

echo
echo "test_prune.sh — $PASS passed, $FAIL failed"
if [[ $FAIL -gt 0 ]]; then
  printf '  failed: %s\n' "${FAILED_CASES[@]}"
  exit 1
fi
exit 0
