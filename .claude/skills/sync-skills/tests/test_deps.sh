#!/usr/bin/env bash
# test_deps.sh — self-contained smoke tests for the `deps` action / resolve_deps.py.
#
# Builds a fake registry of skills with `dependencies:` frontmatter blocks and a
# fake consumer project missing some of them, then asserts the resolver computes
# the right closure (transitive required edges, one-level optional, agent union)
# and flags the right missing-locally members.
#
# Run: bash tests/test_deps.sh   (exit 0 = all pass, 1 = any fail)

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RESOLVER="$SCRIPT_DIR/../scripts/resolve_deps.py"
PASS=0; FAIL=0

ok()  { PASS=$((PASS+1)); echo "  ok: $1"; }
bad() { FAIL=$((FAIL+1)); echo "FAIL: $1"; }
note(){ echo "--- $1 ---"; }

# contains <needle> -- <resolver args...>
contains() {
  local needle="$1"; shift
  [[ "$1" == "--" ]] && shift
  local out; out="$(python3 "$RESOLVER" "$@" 2>&1)"
  if grep -qF -- "$needle" <<<"$out"; then ok "found '$needle'"; else
    bad "missing '$needle' in: $* "; echo "$out" | sed 's/^/      /'; fi
}
# absent <needle> -- <resolver args...>
absent() {
  local needle="$1"; shift
  [[ "$1" == "--" ]] && shift
  local out; out="$(python3 "$RESOLVER" "$@" 2>&1)"
  if grep -qF -- "$needle" <<<"$out"; then
    bad "unexpected '$needle' in: $*"; echo "$out" | sed 's/^/      /'
  else ok "absent '$needle'"; fi
}
# exits <code> -- <resolver args...>
exits() {
  local want="$1"; shift
  [[ "$1" == "--" ]] && shift
  python3 "$RESOLVER" "$@" >/dev/null 2>&1
  local got=$?
  if [[ "$got" == "$want" ]]; then ok "exit $want for: $*"; else
    bad "exit $got != $want for: $*"; fi
}

ROOT="$(mktemp -d)"
trap 'rm -rf "$ROOT"' EXIT
REG="$ROOT/reg"; CONS="$ROOT/cons"

mkskill() {  # mkskill <name> <frontmatter-deps-block-or-empty>
  local name="$1"; shift
  mkdir -p "$REG/skills/$name"
  {
    echo "---"
    echo "name: $name"
    echo "description: test skill $name"
    echo "version: 1"
    echo "updated: 2026-05-30"
    [[ -n "$1" ]] && printf '%s\n' "$1"
    echo "---"
    echo "# $name"
  } > "$REG/skills/$name/SKILL.md"
}

note "build fake registry"
# app -> required core, required shared; optional extras; owns agent app-agent
mkskill app "$(cat <<'YML'
dependencies:
  skills:
    - name: core
      type: required
      reason: core engine
    - name: shared
      type: required
    - name: extras
      type: optional
      reason: nice to have
  agents:
    - app-agent
YML
)"
# core -> required deep; owns agent core-agent (short scalar agent form)
mkskill core "$(cat <<'YML'
dependencies:
  skills:
    - deep
  agents:
    - core-agent
YML
)"
mkskill deep ""        # leaf, no deps
mkskill shared ""      # leaf
mkskill extras ""      # optional target exists but must NOT be traversed/forced
mkskill solo ""        # no deps at all

note "build fake consumer (has core+shared+app-agent; MISSING deep, core-agent)"
mkdir -p "$CONS/.claude/skills/core" "$CONS/.claude/skills/shared" "$CONS/.claude/agents"
cp "$REG/skills/core/SKILL.md"   "$CONS/.claude/skills/core/SKILL.md"
cp "$REG/skills/shared/SKILL.md" "$CONS/.claude/skills/shared/SKILL.md"
echo "x" > "$CONS/.claude/agents/app-agent.md"

note "1. transitive required closure (app -> core -> deep, + shared)"
contains "core"   -- --root "$REG" app
contains "deep"   -- --root "$REG" app
contains "shared" -- --root "$REG" app

note "2. optional edge is listed, NOT in required closure"
contains "Optional skills" -- --root "$REG" app
contains "extras (from app)" -- --root "$REG" app

note "3. agent union across the required closure (app-agent + core-agent)"
contains "app-agent"  -- --root "$REG" app
contains "core-agent" -- --root "$REG" app

note "4. missing-against flags absent members, not present ones"
# deep + core-agent are absent in consumer; core + app-agent are present.
contains "deep   [MISSING locally]"       -- --root "$REG" --missing-against "$CONS" app
contains "core-agent   [MISSING locally]" -- --root "$REG" --missing-against "$CONS" app
absent   "core   [MISSING locally]"       -- --root "$REG" --missing-against "$CONS" app
absent   "app-agent   [MISSING locally]"  -- --root "$REG" --missing-against "$CONS" app

note "5. skill with no deps reports none"
contains "Required skills: none" -- --root "$REG" solo
contains "Agents: none"          -- --root "$REG" solo

note "6. JSON shape"
contains '"required_skills"' -- --root "$REG" --json app
contains '"agents"'          -- --root "$REG" --json app

note "7. exit codes"
exits 0 -- --root "$REG" app
exits 0 -- --root "$REG" --all
exits 2 -- --root "$REG" nonexistent-skill
exits 2 -- --root "$REG"            # no skill named

note "8. unresolved required dep is surfaced"
mkskill broken "$(cat <<'YML'
dependencies:
  skills:
    - name: ghost
      type: required
YML
)"
contains "UNRESOLVED" -- --root "$REG" broken
contains "ghost"      -- --root "$REG" broken

echo
echo "=================================="
echo "test_deps: $PASS passed, $FAIL failed"
[[ "$FAIL" -eq 0 ]] && exit 0 || exit 1
