#!/bin/bash
# test-task-gate.sh — Test suite for the task gate hook and activation script
#
# Tests the PreToolUse hook (check-active-task.sh) and the state management
# script (task-activate.sh) that together enforce task discipline.
#
# State files: .claude/state/active-tasks-{session_id}.txt (project-local)
# Hook: .claude/hooks/check-active-task.sh
# Script: .claude/hooks/task-activate.sh
#
# Usage: bash .claude/skills/task/tests/test-task-gate.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
PROJECT_DIR="$(cd "$SKILL_DIR/../../.." && pwd)"
HOOK="$PROJECT_DIR/.claude/hooks/check-active-task.sh"
ACTIVATE="$PROJECT_DIR/.claude/hooks/task-activate.sh"
STATE_DIR="$PROJECT_DIR/.claude/state"

# Pre-flight checks
for f in "$HOOK" "$ACTIVATE"; do
  if [ ! -x "$f" ]; then
    echo "ERROR: Script not found or not executable: $f"
    exit 1
  fi
done

if ! command -v jq &>/dev/null; then
  echo "ERROR: jq is required. Install with: brew install jq"
  exit 1
fi

mkdir -p "$STATE_DIR"

# Test session IDs
TEST_SESSION="test-session-$(date +%s)"
FAKE_SESSION="fake-session-00000000"

# Counters
PASSED=0
FAILED=0
TOTAL=0

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m'

# ─── Test Helpers ───

run_hook_test() {
  local name="$1" target="$2" session="$3" expected="$4"
  local result actual
  TOTAL=$((TOTAL + 1))

  result=$(echo "{\"tool_input\":{\"file_path\":\"$target\"},\"session_id\":\"$session\",\"transcript_path\":\"\"}" \
    | CLAUDE_PROJECT_DIR="$PROJECT_DIR" bash "$HOOK" 2>/dev/null)

  if [ -z "$result" ]; then
    actual="ALLOW"
  else
    actual="DENY"
  fi

  if [ "$actual" = "$expected" ]; then
    PASSED=$((PASSED + 1))
    echo -e "  ${GREEN}PASS${NC}  $name"
  else
    FAILED=$((FAILED + 1))
    echo -e "  ${RED}FAIL${NC}  $name  (expected=$expected, got=$actual)"
    if [ -n "$result" ]; then
      echo "        $(echo "$result" | jq -r '.hookSpecificOutput.permissionDecisionReason' 2>/dev/null | head -c 120)"
    fi
  fi
}

run_activate_test() {
  local name="$1" expected_output="$2"
  shift 2
  local actual
  TOTAL=$((TOTAL + 1))

  actual=$(bash "$ACTIVATE" "$@" 2>&1 || true)

  if echo "$actual" | grep -qF "$expected_output"; then
    PASSED=$((PASSED + 1))
    echo -e "  ${GREEN}PASS${NC}  $name"
  else
    FAILED=$((FAILED + 1))
    echo -e "  ${RED}FAIL${NC}  $name"
    echo "        expected to contain: $expected_output"
    echo "        got: $actual"
  fi
}

run_deny_message_test() {
  local name="$1" target="$2" session="$3" expected_in_message="$4"
  local result reason
  TOTAL=$((TOTAL + 1))

  result=$(echo "{\"tool_input\":{\"file_path\":\"$target\"},\"session_id\":\"$session\",\"transcript_path\":\"\"}" \
    | CLAUDE_PROJECT_DIR="$PROJECT_DIR" bash "$HOOK" 2>/dev/null)

  if [ -z "$result" ]; then
    FAILED=$((FAILED + 1))
    echo -e "  ${RED}FAIL${NC}  $name  (expected DENY, got ALLOW)"
    return
  fi

  reason=$(echo "$result" | jq -r '.hookSpecificOutput.permissionDecisionReason' 2>/dev/null)

  if echo "$reason" | grep -qF "$expected_in_message"; then
    PASSED=$((PASSED + 1))
    echo -e "  ${GREEN}PASS${NC}  $name"
  else
    FAILED=$((FAILED + 1))
    echo -e "  ${RED}FAIL${NC}  $name"
    echo "        expected message to contain: $expected_in_message"
    echo "        got: $(echo "$reason" | head -c 120)"
  fi
}

# ─── Setup ───
echo ""
echo -e "${BOLD}Task Gate Hook — Test Suite${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Hook:      $HOOK"
echo "Activate:  $ACTIVATE"
echo "State dir: $STATE_DIR"
echo "Session:   $TEST_SESSION"
echo ""

# ═══════════════════════════════════════
# Section 1: Activation Script Tests
# ═══════════════════════════════════════
echo -e "${BOLD}1. Activation Script — Basic Operations${NC}"

# Clean slate
rm -f "$STATE_DIR/active-tasks-${TEST_SESSION}.txt"

run_activate_test "add task → success message" \
  "Task 024 activated" add "$TEST_SESSION" 024

run_activate_test "add second task → success message" \
  "Task 025 activated" add "$TEST_SESSION" 025

run_activate_test "list shows both tasks" \
  "024" list "$TEST_SESSION"

run_activate_test "add duplicate → no error (idempotent)" \
  "Task 024 activated" add "$TEST_SESSION" 024

# Verify no duplicate in file
TOTAL=$((TOTAL + 1))
COUNT=$(grep -c "^024$" "$STATE_DIR/active-tasks-${TEST_SESSION}.txt" 2>/dev/null || echo "0")
if [ "$COUNT" = "1" ]; then
  PASSED=$((PASSED + 1))
  echo -e "  ${GREEN}PASS${NC}  duplicate add does not create duplicate line"
else
  FAILED=$((FAILED + 1))
  echo -e "  ${RED}FAIL${NC}  duplicate add created $COUNT lines for 024"
fi

run_activate_test "remove task → success message" \
  "Task 025 deactivated" remove "$TEST_SESSION" 025

run_activate_test "list after remove shows only 024" \
  "024" list "$TEST_SESSION"

# Verify 025 is gone
TOTAL=$((TOTAL + 1))
if ! grep -q "^025$" "$STATE_DIR/active-tasks-${TEST_SESSION}.txt" 2>/dev/null; then
  PASSED=$((PASSED + 1))
  echo -e "  ${GREEN}PASS${NC}  025 no longer in state file after remove"
else
  FAILED=$((FAILED + 1))
  echo -e "  ${RED}FAIL${NC}  025 still in state file after remove"
fi

run_activate_test "clear → success message" \
  "All tasks deactivated" clear "$TEST_SESSION"

run_activate_test "list after clear → no active tasks" \
  "(no active tasks)" list "$TEST_SESSION"

echo ""
echo -e "${BOLD}2. Activation Script — Edge Cases${NC}"

run_activate_test "list nonexistent session → no active tasks" \
  "(no active tasks)" list "nonexistent-session-xyz"

run_activate_test "add with no task_id → usage error" \
  "Usage:" add "$TEST_SESSION"

run_activate_test "unknown action → error" \
  "Unknown action:" badaction "$TEST_SESSION"

run_activate_test "help → usage info" \
  "Usage:" help

echo ""
echo -e "${BOLD}3. Activation Script — State File Location${NC}"

rm -f "$STATE_DIR/active-tasks-${TEST_SESSION}.txt"
bash "$ACTIVATE" add "$TEST_SESSION" 099 >/dev/null

TOTAL=$((TOTAL + 1))
if [ -f "$STATE_DIR/active-tasks-${TEST_SESSION}.txt" ]; then
  PASSED=$((PASSED + 1))
  echo -e "  ${GREEN}PASS${NC}  state file created in .claude/state/"
else
  FAILED=$((FAILED + 1))
  echo -e "  ${RED}FAIL${NC}  state file NOT in .claude/state/"
fi

TOTAL=$((TOTAL + 1))
if [ ! -f "$PROJECT_DIR/.claude/hooks/active-tasks-${TEST_SESSION}.txt" ]; then
  PASSED=$((PASSED + 1))
  echo -e "  ${GREEN}PASS${NC}  no state file leaked into .claude/hooks/"
else
  FAILED=$((FAILED + 1))
  echo -e "  ${RED}FAIL${NC}  state file leaked into .claude/hooks/"
fi

rm -f "$STATE_DIR/active-tasks-${TEST_SESSION}.txt"

# ═══════════════════════════════════════
# Section 2: Hook — Core Gate Tests
# ═══════════════════════════════════════
echo ""
echo -e "${BOLD}4. Hook — Core Gate (allow/deny)${NC}"

# Create state file with active task
bash "$ACTIVATE" add "$TEST_SESSION" 024 >/dev/null

run_hook_test "Active task, non-exempt path → ALLOW" \
  "$PROJECT_DIR/project.yml" "$TEST_SESSION" "ALLOW"

run_hook_test "No task (fake session), non-exempt path → DENY" \
  "$PROJECT_DIR/project.yml" "$FAKE_SESSION" "DENY"

# ═══════════════════════════════════════
# Section 3: Hook — Exempt Path Tests
# ═══════════════════════════════════════
echo ""
echo -e "${BOLD}5. Hook — Exempt Paths (allow without task)${NC}"

run_hook_test "tasks/* (task doc) → ALLOW" \
  "$PROJECT_DIR/tasks/ben/024-foo.md" "$FAKE_SESSION" "ALLOW"

run_hook_test "tasks/* (index) → ALLOW" \
  "$PROJECT_DIR/tasks/ben/000-index.md" "$FAKE_SESSION" "ALLOW"

run_hook_test "tasks/* (SECOPS.md) → ALLOW" \
  "$PROJECT_DIR/tasks/ben/SECOPS.md" "$FAKE_SESSION" "ALLOW"

run_hook_test ".claude/hooks/* → ALLOW" \
  "$PROJECT_DIR/.claude/hooks/check-active-task.sh" "$FAKE_SESSION" "ALLOW"

run_hook_test ".claude/state/* → ALLOW" \
  "$PROJECT_DIR/.claude/state/active-tasks-foo.txt" "$FAKE_SESSION" "ALLOW"

run_hook_test ".claude/skills/* → ALLOW" \
  "$PROJECT_DIR/.claude/skills/task/SKILL.md" "$FAKE_SESSION" "ALLOW"

run_hook_test ".claude/settings.json → ALLOW" \
  "$PROJECT_DIR/.claude/settings.json" "$FAKE_SESSION" "ALLOW"

# ═══════════════════════════════════════
# Section 4: Hook — Non-Exempt Paths
# ═══════════════════════════════════════
echo ""
echo -e "${BOLD}6. Hook — Non-Exempt Paths (deny without task)${NC}"

run_hook_test "CLAUDE.md → DENY" \
  "$PROJECT_DIR/CLAUDE.md" "$FAKE_SESSION" "DENY"

run_hook_test ".gitignore → DENY" \
  "$PROJECT_DIR/.gitignore" "$FAKE_SESSION" "DENY"

run_hook_test "project.yml → DENY" \
  "$PROJECT_DIR/project.yml" "$FAKE_SESSION" "DENY"

run_hook_test "docs/ file → DENY" \
  "$PROJECT_DIR/docs/project/design-controls/architecture/sad.md" "$FAKE_SESSION" "DENY"

run_hook_test "setup.sh → DENY" \
  "$PROJECT_DIR/setup.sh" "$FAKE_SESSION" "DENY"

run_hook_test "glossary.md → DENY" \
  "$PROJECT_DIR/glossary.md" "$FAKE_SESSION" "DENY"

# ═══════════════════════════════════════
# Section 5: Hook — Multi-Task Tests
# ═══════════════════════════════════════
echo ""
echo -e "${BOLD}7. Hook — Multi-Task Lifecycle${NC}"

bash "$ACTIVATE" add "$TEST_SESSION" 025 >/dev/null

run_hook_test "Two tasks (024+025) → ALLOW" \
  "$PROJECT_DIR/project.yml" "$TEST_SESSION" "ALLOW"

bash "$ACTIVATE" remove "$TEST_SESSION" 025 >/dev/null

run_hook_test "After removing 025, 024 still active → ALLOW" \
  "$PROJECT_DIR/project.yml" "$TEST_SESSION" "ALLOW"

bash "$ACTIVATE" remove "$TEST_SESSION" 024 >/dev/null

run_hook_test "All tasks removed → DENY" \
  "$PROJECT_DIR/project.yml" "$TEST_SESSION" "DENY"

# ═══════════════════════════════════════
# Section 6: Hook — Denial Message Tests
# ═══════════════════════════════════════
echo ""
echo -e "${BOLD}8. Hook — Denial Message Contains Session ID${NC}"

run_deny_message_test "Denial includes session ID" \
  "$PROJECT_DIR/project.yml" "$FAKE_SESSION" "$FAKE_SESSION"

run_deny_message_test "Denial includes activation command" \
  "$PROJECT_DIR/project.yml" "$FAKE_SESSION" "bash .claude/hooks/task-activate.sh add"

run_deny_message_test "Denial includes /task create hint" \
  "$PROJECT_DIR/project.yml" "$FAKE_SESSION" "/task create"

# ═══════════════════════════════════════
# Section 7: Hook — Edge Cases
# ═══════════════════════════════════════
echo ""
echo -e "${BOLD}9. Hook — Edge Cases${NC}"

run_hook_test "Empty target path → DENY (no exempt match)" \
  "" "$FAKE_SESSION" "DENY"

# Empty state file (cleared)
bash "$ACTIVATE" add "$TEST_SESSION" 099 >/dev/null
bash "$ACTIVATE" clear "$TEST_SESSION" >/dev/null

run_hook_test "Empty state file (cleared) → DENY" \
  "$PROJECT_DIR/project.yml" "$TEST_SESSION" "DENY"

# State file deleted
rm -f "$STATE_DIR/active-tasks-${TEST_SESSION}.txt"

run_hook_test "State file deleted → DENY" \
  "$PROJECT_DIR/project.yml" "$TEST_SESSION" "DENY"

# Empty session ID (graceful handling)
run_hook_test "Empty session ID → DENY (no state file match)" \
  "$PROJECT_DIR/project.yml" "" "DENY"

# ═══════════════════════════════════════
# Section 8: End-to-End Integration
# ═══════════════════════════════════════
echo ""
echo -e "${BOLD}10. End-to-End — Activate Script + Hook${NC}"

E2E_SESSION="e2e-test-$(date +%s)"

# Start: no state → denied
run_hook_test "E2E: fresh session → DENY" \
  "$PROJECT_DIR/project.yml" "$E2E_SESSION" "DENY"

# Activate a task via script
bash "$ACTIVATE" add "$E2E_SESSION" 027 >/dev/null

# Now allowed
run_hook_test "E2E: after activate → ALLOW" \
  "$PROJECT_DIR/project.yml" "$E2E_SESSION" "ALLOW"

# Complete the task (remove)
bash "$ACTIVATE" remove "$E2E_SESSION" 027 >/dev/null

# Denied again
run_hook_test "E2E: after complete → DENY" \
  "$PROJECT_DIR/project.yml" "$E2E_SESSION" "DENY"

# Activate two tasks, complete one at a time
bash "$ACTIVATE" add "$E2E_SESSION" 018 >/dev/null
bash "$ACTIVATE" add "$E2E_SESSION" 023 >/dev/null

run_hook_test "E2E: two tasks active → ALLOW" \
  "$PROJECT_DIR/project.yml" "$E2E_SESSION" "ALLOW"

bash "$ACTIVATE" remove "$E2E_SESSION" 018 >/dev/null

run_hook_test "E2E: one task remaining → ALLOW" \
  "$PROJECT_DIR/project.yml" "$E2E_SESSION" "ALLOW"

bash "$ACTIVATE" remove "$E2E_SESSION" 023 >/dev/null

run_hook_test "E2E: all completed → DENY" \
  "$PROJECT_DIR/project.yml" "$E2E_SESSION" "DENY"

# ═══════════════════════════════════════
# Section 9: Session Isolation
# ═══════════════════════════════════════
echo ""
echo -e "${BOLD}11. Session Isolation${NC}"

SESSION_A="iso-a-$(date +%s)"
SESSION_B="iso-b-$(date +%s)"

bash "$ACTIVATE" add "$SESSION_A" 024 >/dev/null
bash "$ACTIVATE" add "$SESSION_B" 018 >/dev/null

run_hook_test "Session A has task → ALLOW" \
  "$PROJECT_DIR/project.yml" "$SESSION_A" "ALLOW"

run_hook_test "Session B has task → ALLOW" \
  "$PROJECT_DIR/project.yml" "$SESSION_B" "ALLOW"

# Complete session A's task — session B unaffected
bash "$ACTIVATE" remove "$SESSION_A" 024 >/dev/null

run_hook_test "Session A completed → DENY" \
  "$PROJECT_DIR/project.yml" "$SESSION_A" "DENY"

run_hook_test "Session B still active → ALLOW" \
  "$PROJECT_DIR/project.yml" "$SESSION_B" "ALLOW"

# Cleanup
rm -f "$STATE_DIR/active-tasks-${SESSION_A}.txt"
rm -f "$STATE_DIR/active-tasks-${SESSION_B}.txt"
rm -f "$STATE_DIR/active-tasks-${E2E_SESSION}.txt"
rm -f "$STATE_DIR/active-tasks-${TEST_SESSION}.txt"

# ─── Summary ───
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ "$FAILED" -eq 0 ]; then
  echo -e "${GREEN}${BOLD}ALL TESTS PASSED${NC}  ($PASSED/$TOTAL)"
else
  echo -e "${RED}${BOLD}$FAILED FAILED${NC}  ($PASSED passed, $FAILED failed, $TOTAL total)"
fi
echo ""

exit "$FAILED"
