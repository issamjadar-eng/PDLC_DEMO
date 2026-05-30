#!/bin/bash
# taxonomy-freshness.sh — SessionStart hook that warns when a project
# .taxonomy.yml is past its review-cadence threshold.
#
# Owned by the /medtech-docs skill. Symlinked into .claude/hooks/ by
# /medtech-docs init (same install pattern as the task gate hooks).
#
# Behavior:
#   - Walks the project root for *.taxonomy.yml files (excluding .git,
#     .venv, node_modules, _scratch, tools, __pycache__, .staging).
#   - For each, reads `last_updated:` + `review_cadence_days:` top-level fields.
#   - If current date > last_updated + review_cadence_days, emits a
#     SessionStart system reminder via the hookSpecificOutput JSON
#     protocol asking the user to re-audit the taxonomy.
#   - Silent if no taxonomy files exist or all are within cadence —
#     SessionStart hooks should be quiet by default.
#
# Project-agnostic: makes no reference to specific doctype slugs, FORM/
# SOP IDs, or specific projects. The taxonomy file's own header
# documents what it is.
#
# Throttle: emits a marker file at $CLAUDE_PROJECT_DIR/.state/taxonomy-
# freshness-reminded so the warning only fires once per 24h (per
# project, not per session). Delete the marker to force a re-emission.

set -e

PROJECT_ROOT="${CLAUDE_PROJECT_DIR:-$(pwd)}"
STATE_DIR="$PROJECT_ROOT/.state"
MARKER="$STATE_DIR/taxonomy-freshness-reminded"
THROTTLE_HOURS=24

# Consume hook stdin (we don't currently use any fields).
cat >/dev/null

# Throttle — skip if reminded within the last $THROTTLE_HOURS.
if [ -f "$MARKER" ]; then
  if [ "$(find "$MARKER" -mmin -$((THROTTLE_HOURS * 60)) 2>/dev/null | wc -l)" -gt 0 ]; then
    exit 0
  fi
fi

# Delegate to Python for YAML parsing + JSON output. Python handles all
# escaping correctly; the shell only orchestrates.
python3 - "$PROJECT_ROOT" <<'PY'
import json
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit(0)  # pyyaml missing — silently skip rather than nag

project_root = Path(sys.argv[1])
EXCLUDE_DIRS = {".git", ".venv", "node_modules", "_scratch", "__pycache__",
                "tools", ".staging"}

today = date.today()
stale = []  # list of (relpath, last_updated_str, cadence_days, days_overdue)

for tax_path in project_root.rglob(".taxonomy.yml"):
    if any(part in EXCLUDE_DIRS for part in tax_path.parts):
        continue
    try:
        data = yaml.safe_load(tax_path.read_text()) or {}
    except Exception:
        continue

    last_updated = data.get("last_updated")
    cadence = data.get("review_cadence_days")

    # No freshness metadata — silently skip. The audit check is the
    # right place to flag "missing metadata," not a SessionStart hook.
    if not last_updated or not cadence:
        continue

    # Normalize last_updated to a date.
    if isinstance(last_updated, str):
        try:
            lu = datetime.fromisoformat(last_updated).date()
        except ValueError:
            continue
    elif hasattr(last_updated, "year"):  # already a date object
        lu = last_updated
    else:
        continue

    try:
        cadence_days = int(cadence)
    except (TypeError, ValueError):
        continue

    threshold = lu + timedelta(days=cadence_days)
    if today > threshold:
        days_overdue = (today - threshold).days
        rel = tax_path.relative_to(project_root)
        stale.append((str(rel), str(lu), cadence_days, days_overdue))

if not stale:
    sys.exit(0)

# Build the system reminder message and emit hookSpecificOutput JSON.
lines = [
    "Doctype taxonomy review overdue — the following file(s) are past their review_cadence_days threshold:",
    "",
]
for rel, lu, cad, overdue in stale:
    lines.append(f"  - {rel} — last_updated={lu}, cadence={cad}d, overdue by {overdue}d")
lines += [
    "",
    "These taxonomy files declare which QMS forms / SOPs / WIs govern each "
    "doctype. Mappings may have drifted since last audit (new QMS forms, "
    "retired SOPs, renamed templates). Consider running an audit pass to "
    "re-verify mappings against the QMS document registry, then update "
    "each file's `last_updated:` field to today's date.",
]

payload = {
    "hookSpecificOutput": {
        "hookEventName": "SessionStart",
        "additionalContext": "\n".join(lines),
    }
}
print(json.dumps(payload))
PY

# If Python emitted anything (stale taxonomies found), update throttle marker.
# We can't easily detect Python's output from here without capturing it; the
# simpler discipline is to update the marker unconditionally after a non-trivial
# run. The throttle protects against re-firing within $THROTTLE_HOURS.
mkdir -p "$STATE_DIR"
touch "$MARKER"

exit 0
