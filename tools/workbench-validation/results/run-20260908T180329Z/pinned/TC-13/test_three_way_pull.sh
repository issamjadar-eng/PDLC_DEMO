#!/usr/bin/env bash
# test_three_way_pull.sh — Smoke tests for `sync.sh analyze` and `check --analyzed`.
#
# Validates the three-way merge analysis recommendations introduced in
# sync-skills v8 to prevent UPSTREAM_NEWER auto-clobber of locally-newer files
# (the task 138 incident). Each case sets up a fake project + registry world
# and asserts that analyze recommends the right bucket:
#
#   1. UPSTREAM_ADVANCE  — local matches an OLD hitachi blob; upstream advanced
#                          → safe to auto-pull
#   2. LOCAL_AHEAD       — local blob unknown to hitachi; project edited recently
#                          → keep local, push candidate (NEVER auto-pull)
#   3. BOTH_DIVERGED     — local blob unknown, project edit > 7 days ago, upstream
#                          has commits → manual review required
#   4. mixed batch       — all three above + an UPSTREAM_ONLY new file → bucketing
#                          via `check --analyzed` works end-to-end
#
# Self-contained — no network, no real hitachi. Mirrors test_status.sh pattern.
#
# Run: bash .claude/skills/sync-skills/tests/test_three_way_pull.sh
# Exit: 0 if every case passes, 1 on first failure.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SYNC_SCRIPT="$SCRIPT_DIR/../scripts/sync.sh"

PASS=0
FAIL=0
FAILED_CASES=()

# ─── Test harness ────────────────────────────────────────────────────────

# Build a fresh world with one example skill in BOTH project and registry.
# Sets globals: WORLD, PROJECT_ROOT, REGISTRY_ROOT, REGISTRY_REMOTE.
# After this returns, both sides hold the same v1 content; per-case setup
# functions then mutate them to create the three-way scenarios.
_setup_world() {
  WORLD="$(mktemp -d)"
  PROJECT_ROOT="$WORLD/project"
  REGISTRY_ROOT="$WORLD/hitachi"
  REGISTRY_REMOTE="$WORLD/hitachi.git"

  # Bare remote for the registry.
  git init --bare --quiet --initial-branch=main "$REGISTRY_REMOTE"

  # Registry working repo: v1 content.
  mkdir -p "$REGISTRY_ROOT/skills/example/scripts"
  mkdir -p "$REGISTRY_ROOT/agents"
  cat >"$REGISTRY_ROOT/skills/example/SKILL.md" <<'EOF'
---
name: example
version: 1
---
# Example skill v1
Initial content.
EOF
  git -C "$REGISTRY_ROOT" init --quiet --initial-branch=main
  git -C "$REGISTRY_ROOT" config user.email "test@example.com"
  git -C "$REGISTRY_ROOT" config user.name "Test"
  git -C "$REGISTRY_ROOT" add -A
  git -C "$REGISTRY_ROOT" commit --quiet -m "v1 initial"
  git -C "$REGISTRY_ROOT" remote add origin "$REGISTRY_REMOTE"
  git -C "$REGISTRY_ROOT" push --quiet -u origin main

  # Project working repo: copy v1.
  mkdir -p "$PROJECT_ROOT/.claude/skills/example/scripts"
  mkdir -p "$PROJECT_ROOT/.claude/agents"
  cp "$REGISTRY_ROOT/skills/example/SKILL.md" "$PROJECT_ROOT/.claude/skills/example/SKILL.md"

  # Install sync.sh under test in the 4-level structure the script expects.
  mkdir -p "$PROJECT_ROOT/.claude/skills/sync-skills/scripts"
  cp "$SYNC_SCRIPT" "$PROJECT_ROOT/.claude/skills/sync-skills/scripts/sync.sh"
  chmod +x "$PROJECT_ROOT/.claude/skills/sync-skills/scripts/sync.sh"

  # project.yml pointing at the registry.
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
  git -C "$PROJECT_ROOT" commit --quiet -m "project v1"
}

_teardown_world() {
  if [[ -n "${WORLD:-}" && -d "$WORLD" ]]; then
    rm -rf "$WORLD"
  fi
}

# Advance the registry: replace example/SKILL.md with v2 content, commit + push.
_advance_registry_v2() {
  cat >"$REGISTRY_ROOT/skills/example/SKILL.md" <<'EOF'
---
name: example
version: 2
---
# Example skill v2
Upstream advanced.
EOF
  git -C "$REGISTRY_ROOT" add -A
  git -C "$REGISTRY_ROOT" commit --quiet -m "v2 upstream advance"
  git -C "$REGISTRY_ROOT" push --quiet origin main
}

# Make the project's local file a different blob unknown to hitachi history,
# AND backdate the project's commit-touching-file timestamp.
# Args: <commit-age-days>
_make_local_unknown_blob_with_age() {
  local age_days="$1"
  cat >"$PROJECT_ROOT/.claude/skills/example/SKILL.md" <<'EOF'
---
name: example
version: 1
---
# Example skill v1 — locally edited
Project added a section the registry has never seen.
EOF
  local backdate_secs=$(( age_days * 86400 ))
  local backdate_ts
  backdate_ts="$(date -d "@$(( $(date +%s) - backdate_secs ))" +'%Y-%m-%dT%H:%M:%S' 2>/dev/null || \
                  date -r $(( $(date +%s) - backdate_secs )) +'%Y-%m-%dT%H:%M:%S')"
  GIT_AUTHOR_DATE="$backdate_ts" GIT_COMMITTER_DATE="$backdate_ts" \
    git -C "$PROJECT_ROOT" commit --quiet -am "local edit (backdated $age_days d)"
}

# Run sync.sh with whatever args; echo stdout+stderr; capture exit code via caller.
_run() {
  bash "$PROJECT_ROOT/.claude/skills/sync-skills/scripts/sync.sh" "$@" 2>&1
}

# Assertion: stdout substring + exit code.
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

case_upstream_advance() {
  echo "Case 1: UPSTREAM_ADVANCE — local matches old hitachi blob, upstream advanced"
  _setup_world
  # Local stays at v1 (blob exists in hitachi @ initial commit).
  # Registry advances to v2.
  _advance_registry_v2
  local out exit_code
  out="$(_run analyze "skills/example/SKILL.md")" && exit_code=0 || exit_code=$?
  _assert "advance: tab-separated row" "0" $'UPSTREAM_NEWER\tskills/example/SKILL.md\tUPSTREAM_ADVANCE' "$exit_code" "$out"
  _assert "advance: summary mentions advance" "0" "upstream advanced" "$exit_code" "$out"
  _teardown_world
}

case_local_ahead() {
  echo "Case 2: LOCAL_AHEAD — local blob unknown to hitachi, project edited recently"
  _setup_world
  # Local diverges with content unknown to hitachi history (recent edit, 0d ago).
  _make_local_unknown_blob_with_age 0
  # Registry stays at v1 — but check would not flag UPSTREAM_NEWER without a remote
  # diff. We're testing analyze directly, which doesn't require check; assertion is
  # on the recommendation given the local-blob state. Force an upstream change so
  # check would also flag this in real flows:
  _advance_registry_v2
  local out exit_code
  out="$(_run analyze "skills/example/SKILL.md")" && exit_code=0 || exit_code=$?
  _assert "local_ahead: recommendation"  "0" $'UPSTREAM_NEWER\tskills/example/SKILL.md\tLOCAL_AHEAD' "$exit_code" "$out"
  _assert "local_ahead: summary mentions keep local" "0" "keep local" "$exit_code" "$out"
  _teardown_world
}

case_both_diverged() {
  echo "Case 3: BOTH_DIVERGED — local unknown blob, project edit >7 days ago, upstream advanced"
  _setup_world
  # Local diverges with old (backdated 30d) commit
  _make_local_unknown_blob_with_age 30
  _advance_registry_v2
  local out exit_code
  out="$(_run analyze "skills/example/SKILL.md")" && exit_code=0 || exit_code=$?
  _assert "both_diverged: recommendation" "0" $'UPSTREAM_NEWER\tskills/example/SKILL.md\tBOTH_DIVERGED' "$exit_code" "$out"
  _assert "both_diverged: summary mentions manual review" "0" "manual review" "$exit_code" "$out"
  _teardown_world
}

case_mixed_batch() {
  echo "Case 4: mixed batch — UPSTREAM_ADVANCE + LOCAL_AHEAD + BOTH_DIVERGED + UPSTREAM_ONLY"
  _setup_world

  # Add three more skills so we have 4 total paths to manipulate independently.
  for i in 2 3 4; do
    mkdir -p "$REGISTRY_ROOT/skills/skill$i"
    cat >"$REGISTRY_ROOT/skills/skill$i/SKILL.md" <<EOF
---
name: skill$i
version: 1
---
# Skill $i v1
EOF
  done
  # Add an UPSTREAM_ONLY skill5 that does NOT exist locally.
  mkdir -p "$REGISTRY_ROOT/skills/skill5"
  cat >"$REGISTRY_ROOT/skills/skill5/SKILL.md" <<'EOF'
---
name: skill5
version: 1
---
# Skill 5 — upstream only
EOF
  git -C "$REGISTRY_ROOT" add -A
  git -C "$REGISTRY_ROOT" commit --quiet -m "add skill2,3,4,5"
  git -C "$REGISTRY_ROOT" push --quiet origin main

  # Locally copy v1 of skill2, skill3, skill4 (but NOT skill5).
  for i in 2 3 4; do
    mkdir -p "$PROJECT_ROOT/.claude/skills/skill$i"
    cp "$REGISTRY_ROOT/skills/skill$i/SKILL.md" "$PROJECT_ROOT/.claude/skills/skill$i/SKILL.md"
  done
  git -C "$PROJECT_ROOT" add -A
  git -C "$PROJECT_ROOT" commit --quiet -m "adopt skill2,3,4 v1"

  # Now create the three diverging scenarios:
  # - skill2 → UPSTREAM_ADVANCE: registry advances; local stays at v1.
  cat >"$REGISTRY_ROOT/skills/skill2/SKILL.md" <<'EOF'
---
name: skill2
version: 2
---
# Skill 2 v2 — upstream-only advance
EOF
  # - skill3 → LOCAL_AHEAD: local diverges recently to a blob unknown upstream.
  cat >"$PROJECT_ROOT/.claude/skills/skill3/SKILL.md" <<'EOF'
---
name: skill3
version: 1
---
# Skill 3 v1 — locally edited (recent)
EOF
  git -C "$PROJECT_ROOT" commit --quiet -am "skill3 local edit (recent)"
  # Registry advances skill3 too so check flags it as UPSTREAM_NEWER.
  cat >"$REGISTRY_ROOT/skills/skill3/SKILL.md" <<'EOF'
---
name: skill3
version: 2
---
# Skill 3 v2 — upstream advanced ALSO (but local is what we keep)
EOF
  # - skill4 → BOTH_DIVERGED: local diverges with backdated commit, upstream advances.
  cat >"$PROJECT_ROOT/.claude/skills/skill4/SKILL.md" <<'EOF'
---
name: skill4
version: 1
---
# Skill 4 v1 — locally edited (long ago)
EOF
  local backdate_secs=$(( 30 * 86400 ))
  local backdate_ts
  backdate_ts="$(date -d "@$(( $(date +%s) - backdate_secs ))" +'%Y-%m-%dT%H:%M:%S' 2>/dev/null || \
                  date -r $(( $(date +%s) - backdate_secs )) +'%Y-%m-%dT%H:%M:%S')"
  GIT_AUTHOR_DATE="$backdate_ts" GIT_COMMITTER_DATE="$backdate_ts" \
    git -C "$PROJECT_ROOT" commit --quiet -am "skill4 local edit (backdated 30d)"
  cat >"$REGISTRY_ROOT/skills/skill4/SKILL.md" <<'EOF'
---
name: skill4
version: 2
---
# Skill 4 v2 — upstream advance
EOF
  git -C "$REGISTRY_ROOT" add -A
  git -C "$REGISTRY_ROOT" commit --quiet -m "advance skill2, skill3, skill4"
  git -C "$REGISTRY_ROOT" push --quiet origin main

  local out exit_code
  out="$(_run check --analyzed)" && exit_code=0 || exit_code=$?
  _assert "mixed: skill2 UPSTREAM_ADVANCE" "0" $'UPSTREAM_NEWER\tskills/skill2/SKILL.md\tUPSTREAM_ADVANCE' "$exit_code" "$out"
  _assert "mixed: skill3 LOCAL_AHEAD"      "0" $'UPSTREAM_NEWER\tskills/skill3/SKILL.md\tLOCAL_AHEAD'      "$exit_code" "$out"
  _assert "mixed: skill4 BOTH_DIVERGED"    "0" $'UPSTREAM_NEWER\tskills/skill4/SKILL.md\tBOTH_DIVERGED'    "$exit_code" "$out"
  _assert "mixed: skill5 UPSTREAM_ONLY"    "0" $'UPSTREAM_ONLY\tskills/skill5/SKILL.md'                    "$exit_code" "$out"
  _teardown_world
}

# ─── Run ─────────────────────────────────────────────────────────────────

echo "test_three_way_pull.sh"
echo "======================"
echo

case_upstream_advance
case_local_ahead
case_both_diverged
case_mixed_batch

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
