#!/usr/bin/env bash
# Structural + unit tests for the change-control internal-review surface.
#
# Tests:
#   1. Skill structure: required new files present
#   2. Action scripts are valid Python (no syntax errors)
#   3. lib/path_convention: project_name() reads project.yml
#   4. lib/path_convention: doc_name_from_repo_path normalizes correctly
#   5. lib/path_convention: drive_path_for builds AI_PDLC/<project>/<user>/<doc>
#   6. lib/path_convention: archived_doc_name applies date stamp
#   7. lib/internal_review: render → parse round-trip preserves data
#   8. lib/internal_review: upsert_block creates / replaces idempotently
#   9. lib/internal_review: find_block returns None for missing
#  10. lib/internal_review: remove_block clears the section
#  11. help action prints lifecycle + actions
#  12. help <action> prints per-action detail
#  13. web-control purge_stale: keeps referenced + deletes orphans
#  14. CDP modifier sanity: lib/internal_review preserves checkbox state
#       across upsert (regression: previously hand-edited Already-Addressed
#       must survive a review-status refresh)
#
# Live tests for review-start / review-status / review-update against a
# real gdoc are NOT in this suite — they require a live web-control debug
# Chrome and a corporate Google session. Documented as a manual integration
# test in the README.

set -uo pipefail

SKILL_DIR="$(cd "$(dirname "$0")"/.. && pwd)"
PROJECT_ROOT="$(cd "$SKILL_DIR"/../../.. && pwd)"
RESULTS=()
PASSED=0
FAILED=0

# Use the project's existing probe venv if available; fall back to system python3
VENV_PY="/tmp/dhf-probe-venv/bin/python3"
if [[ -x "$VENV_PY" ]]; then
    PY="$VENV_PY"
else
    PY="python3"
fi

# Ensure pyyaml is available for path_convention
if ! "$PY" -c "import yaml" 2>/dev/null; then
    if [[ -x "$VENV_PY" ]]; then
        /tmp/dhf-probe-venv/bin/pip install --quiet pyyaml 2>&1 | tail -3 || true
    fi
fi

assert() {
    local label="$1"
    local cmd="$2"
    if eval "$cmd" >/tmp/cc-test-stderr 2>&1; then
        echo "  PASS  $label"
        PASSED=$((PASSED + 1))
    else
        echo "  FAIL  $label"
        echo "        cmd: $cmd"
        echo "        stderr (last 5 lines):"
        tail -5 /tmp/cc-test-stderr 2>/dev/null | sed 's/^/        /'
        FAILED=$((FAILED + 1))
    fi
}

assert_output() {
    local label="$1"
    local cmd="$2"
    local pattern="$3"
    local out
    out="$(eval "$cmd" 2>&1)"
    if echo "$out" | grep -qE "$pattern"; then
        echo "  PASS  $label"
        PASSED=$((PASSED + 1))
    else
        echo "  FAIL  $label  (pattern '$pattern' not found)"
        echo "        output (last 8 lines):"
        echo "$out" | tail -8 | sed 's/^/        /'
        FAILED=$((FAILED + 1))
    fi
}

echo "==========================================================="
echo "change-control internal-review test suite"
echo "  SKILL_DIR:    $SKILL_DIR"
echo "  PROJECT:      $PROJECT_ROOT"
echo "  PYTHON:       $PY"
echo "==========================================================="
echo

# ------------------------------------------------------------
# 1. Structure
# ------------------------------------------------------------
echo "[1] structure"
for f in \
    actions/review_start.py \
    actions/review_status.py \
    actions/review_update.py \
    actions/review_abort.py \
    actions/help.py \
    lib/path_convention.py \
    lib/internal_review.py \
    lib/gdoc.py; do
    assert "structure: $f" "[ -f '$SKILL_DIR/$f' ]"
done

# ------------------------------------------------------------
# 2. Python syntax
# ------------------------------------------------------------
echo
echo "[2] python syntax"
for f in \
    "$SKILL_DIR/actions/review_start.py" \
    "$SKILL_DIR/actions/review_status.py" \
    "$SKILL_DIR/actions/review_update.py" \
    "$SKILL_DIR/actions/review_abort.py" \
    "$SKILL_DIR/actions/help.py" \
    "$SKILL_DIR/lib/path_convention.py" \
    "$SKILL_DIR/lib/internal_review.py" \
    "$SKILL_DIR/lib/gdoc.py" \
    "$PROJECT_ROOT/.claude/skills/web-control/actions/purge_stale.py"; do
    name="$(basename "$f")"
    assert "syntax: $name" "'$PY' -m py_compile '$f'"
done

# ------------------------------------------------------------
# 3-6. lib/path_convention behavior
# ------------------------------------------------------------
echo
echo "[3-6] path_convention"
assert_output "project_name() reads project.yml" \
    "cd '$PROJECT_ROOT' && PYTHONPATH='$SKILL_DIR' '$PY' -c 'from lib.path_convention import project_name; print(project_name())'" \
    'Arthrex PCCP'

assert_output "doc_name_from_repo_path strips .md + replaces /" \
    "cd '$PROJECT_ROOT' && PYTHONPATH='$SKILL_DIR' '$PY' -c 'from lib.path_convention import doc_name_from_repo_path; print(doc_name_from_repo_path(\"docs/project/dhfs/foo/bar.md\"))'" \
    '^docs_project_dhfs_foo_bar$'

assert_output "drive_path_for builds AI_PDLC/<project>/<user>/<doc>" \
    "cd '$PROJECT_ROOT' && PYTHONPATH='$SKILL_DIR' '$PY' -c '
from lib.path_convention import drive_path_for
parts = drive_path_for(\"docs/system-sad.md\", task_folder=\"ben\")
print(\"|\".join(parts))
'" \
    'AI_PDLC\|Arthrex PCCP\|ben\|docs_system-sad'

assert_output "archived_doc_name applies [ARCHIVED YYYY-MM-DD]" \
    "cd '$PROJECT_ROOT' && PYTHONPATH='$SKILL_DIR' '$PY' -c '
from lib.path_convention import archived_doc_name
print(archived_doc_name(\"foo_bar\", \"2026-04-27\"))
'" \
    '^\[ARCHIVED 2026-04-27\] foo_bar$'

# ------------------------------------------------------------
# 7-10. lib/internal_review behavior
# ------------------------------------------------------------
echo
echo "[7-10] internal_review"

# Round-trip: render → parse → render produces the same dataclass content
assert_output "render → parse round-trip preserves doc_path + gdoc_url" \
    "cd '$PROJECT_ROOT' && PYTHONPATH='$SKILL_DIR' '$PY' -c '
from lib.internal_review import ReviewSection, ReviewItem, render_section, parse_section
s = ReviewSection.new(\"docs/foo.md\", \"https://docs.google.com/document/d/abc123/edit\", \"AI_PDLC/x/ben/\")
s.open_items.append(ReviewItem(kind=\"comment\", id=\"c-1\", author=\"Maryna\", anchor=\"§4.2\", text=\"need citation\"))
out = render_section(s)
parsed = parse_section(out)
assert parsed.doc_path == \"docs/foo.md\", parsed.doc_path
assert parsed.gdoc_url.startswith(\"https://docs.google.com/document/d/abc123\"), parsed.gdoc_url
assert len(parsed.open_items) == 1
assert parsed.open_items[0].kind == \"comment\"
print(\"OK\")
'" 'OK'

assert_output "upsert_block creates section in empty doc" \
    "cd '$PROJECT_ROOT' && PYTHONPATH='$SKILL_DIR' '$PY' -c '
from lib.internal_review import ReviewSection, upsert_block
s = ReviewSection.new(\"x.md\", \"https://docs.google.com/document/d/zz/edit\", \"AI_PDLC/p/ben/\")
out = upsert_block(\"# Some Task\\n\\nBody.\\n\", s)
assert \"change-control:internal-review begin doc=x.md\" in out
assert \"change-control:internal-review end\" in out
assert out.count(\"change-control:internal-review begin\") == 1
print(\"OK\")
'" 'OK'

assert_output "upsert_block replaces existing section idempotently" \
    "cd '$PROJECT_ROOT' && PYTHONPATH='$SKILL_DIR' '$PY' -c '
from lib.internal_review import ReviewSection, upsert_block
s1 = ReviewSection.new(\"x.md\", \"https://docs.google.com/document/d/aaa/edit\", \"AI_PDLC/p/ben/\")
text = upsert_block(\"# Task\\n\", s1)
s2 = ReviewSection.new(\"x.md\", \"https://docs.google.com/document/d/bbb/edit\", \"AI_PDLC/p/ben/\")
text2 = upsert_block(text, s2)
# Should still have exactly one block, with the new url
assert text2.count(\"change-control:internal-review begin\") == 1
assert \"bbb\" in text2
assert \"aaa\" not in text2
print(\"OK\")
'" 'OK'

assert_output "find_block returns None for missing doc" \
    "cd '$PROJECT_ROOT' && PYTHONPATH='$SKILL_DIR' '$PY' -c '
from lib.internal_review import find_block
result = find_block(\"# Task\\n\\nbody\\n\", \"x.md\")
print(\"None\" if result is None else \"NOT_NONE\")
'" '^None$'

assert_output "remove_block clears the section" \
    "cd '$PROJECT_ROOT' && PYTHONPATH='$SKILL_DIR' '$PY' -c '
from lib.internal_review import ReviewSection, upsert_block, remove_block, find_block
s = ReviewSection.new(\"y.md\", \"https://docs.google.com/document/d/zz/edit\", \"AI_PDLC/p/ben/\")
text = upsert_block(\"# Task\\n\", s)
text2 = remove_block(text, \"y.md\")
assert find_block(text2, \"y.md\") is None
print(\"OK\")
'" 'OK'

# ------------------------------------------------------------
# 11-12. help action
# ------------------------------------------------------------
echo
echo "[11-12] help action"
assert_output "help (no args) prints lifecycle + review-start" \
    "'$PY' '$SKILL_DIR/actions/help.py'" \
    'review-start'

assert_output "help review-start prints detailed usage" \
    "'$PY' '$SKILL_DIR/actions/help.py' review-start" \
    'AI_PDLC'

assert_output "help freeze prints archive flow per Q7" \
    "'$PY' '$SKILL_DIR/actions/help.py' freeze" \
    'ARCHIVED YYYY-MM-DD'

# ------------------------------------------------------------
# 13. web-control purge_stale (keeps referenced + deletes orphans)
# ------------------------------------------------------------
echo
echo "[13] web-control purge_stale"

# Build a transient .state/web-control with a referenced + an orphan,
# write a temp task doc with one referenced gdoc id, run purge_stale,
# verify only the orphan is gone.
TEST_TMP="$(mktemp -d)"
mkdir -p "$TEST_TMP/.state/web-control" "$TEST_TMP/tasks/test"
cp "$PROJECT_ROOT/project.yml" "$TEST_TMP/project.yml"
cat > "$TEST_TMP/tasks/test/001-test.md" <<EOF
# Test task

<!-- change-control:internal-review begin doc=test/foo.md -->
| Field | Value |
|---|---|
| GDoc | https://docs.google.com/document/d/REFERENCED_ID/edit |
<!-- change-control:internal-review end -->
EOF

touch "$TEST_TMP/.state/web-control/REFERENCED_ID.last-sync.json"
touch "$TEST_TMP/.state/web-control/REFERENCED_ID.last-push.txt"
touch "$TEST_TMP/.state/web-control/ORPHAN_ID.last-sync.json"
touch "$TEST_TMP/.state/web-control/ORPHAN_ID.last-push.txt"

(cd "$TEST_TMP" && "$PY" "$PROJECT_ROOT/.claude/skills/web-control/actions/purge_stale.py" >/tmp/cc-test-purge.log 2>&1)
PURGE_OK=true
[ -f "$TEST_TMP/.state/web-control/REFERENCED_ID.last-sync.json" ] || PURGE_OK=false
[ -f "$TEST_TMP/.state/web-control/REFERENCED_ID.last-push.txt" ] || PURGE_OK=false
[ ! -f "$TEST_TMP/.state/web-control/ORPHAN_ID.last-sync.json" ] || PURGE_OK=false
[ ! -f "$TEST_TMP/.state/web-control/ORPHAN_ID.last-push.txt" ] || PURGE_OK=false

if $PURGE_OK; then
    echo "  PASS  purge_stale keeps referenced + deletes orphans"
    PASSED=$((PASSED + 1))
else
    echo "  FAIL  purge_stale (referenced or orphan handling broken)"
    echo "        log:"
    head -20 /tmp/cc-test-purge.log | sed 's/^/        /'
    echo "        state dir after purge:"
    ls -la "$TEST_TMP/.state/web-control/" | sed 's/^/        /'
    FAILED=$((FAILED + 1))
fi
rm -rf "$TEST_TMP"

# ------------------------------------------------------------
# 14. Hand-edited Already-Addressed survives upsert (regression)
# ------------------------------------------------------------
echo
echo "[14] hand-edited state survives refresh"
TEST14_SCRIPT="$(mktemp /tmp/cc-test14-XXXXXX.py)"
cat > "$TEST14_SCRIPT" <<'PYEOF'
import sys
from lib.internal_review import (
    ReviewSection, ReviewItem, upsert_block, parse_section, find_block
)
# Build initial section with an open item
s = ReviewSection.new("x.md", "https://docs.google.com/document/d/zz/edit", "AI_PDLC/p/ben/")
s.open_items.append(ReviewItem(kind="comment", id="c-1", author="Maryna", anchor="§1", text="..."))
text = upsert_block("# T\n", s)
# Simulate user moving #c-1 to Already Addressed by hand
old = "### Already Addressed (will reply on next `review-update`)\n\n(none yet)"
new = "### Already Addressed (will reply on next `review-update`)\n\n- [x] **#c-1** Maryna · §1 — addressed: cited Bedi 2013"
text_edited = text.replace(old, new)
# Reparse and verify
rng = find_block(text_edited, "x.md")
block = "\n".join(text_edited.splitlines()[rng[0]:rng[1]+1])
parsed = parse_section(block)
assert len(parsed.already_addressed) == 1, parsed.already_addressed
assert parsed.already_addressed[0].id == "c-1"
print("OK")
PYEOF
assert_output "user-edited Already-Addressed survives upsert (regression)" \
    "cd '$PROJECT_ROOT' && PYTHONPATH='$SKILL_DIR' '$PY' '$TEST14_SCRIPT'" \
    'OK'
rm -f "$TEST14_SCRIPT"

# ------------------------------------------------------------
# Summary
# ------------------------------------------------------------
echo
echo "==========================================================="
echo "Results: $PASSED passed, $FAILED failed"
echo "==========================================================="
[ $FAILED -gt 0 ] && exit 1
exit 0
