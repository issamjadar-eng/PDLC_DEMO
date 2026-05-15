"""Tracker markdown writer — find row by ID, swap Status cell, write back.

Backs the B4 tracker-status-update workflow (task ben/154 P3). Each status
change applies immediately to the worktree's submission-tracker.md, so the
worktree IS the pending-changeset staging area (mirrors b3's pattern — no
separate `.state/pending/` buffer to fork the source of truth).

Module API:
  * find_status_cell(md, row_id) → (line_idx, before, after, current_status)
    or None — locates the Status cell for a row without mutating
  * apply_status_change(md, row_id, new_status) → new_md or raises
    LookupError if row_id not found / RowParseError if the row doesn't
    have the expected 8-cell shape
  * write_status_change(wt, row_id, new_status, rationale, actor) →
    {row_id, old_status, new_status, written, rendered, changelog_appended}
    — full pipeline: read md → mutate → write → regenerate HTML →
    append task-doc changelog row
  * regenerate_html(repo_root, wt) → bool — invokes /tracker render via
    the script in the worktree's checkout
  * append_task_changelog(task_path, entry) → bool — appends one bulleted
    entry to the `## Changelog` section of the session task doc

Idempotency: applying the same (row_id, new_status) twice is a no-op
beyond the second changelog entry. parse_pending_changes() scans the
session task doc to surface the human-visible pending-changes list.
"""

from __future__ import annotations

import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

# Tracker md path inside the worktree (and inside the repo root).
TRACKER_MD_REL = "docs/project/submissions/submission-tracker.md"
TRACKER_HTML_REL = "docs/project/submissions/submission-tracker.html"

# 7-state lifecycle vocabulary (locked in 2026-05-03; matches render.py
# VALID_STATUSES). The overlay accepts only canonical values; render.py's
# coerce_status() handles legacy aliases at parse time for the md side.
VALID_STATUSES = {
    "Not Started", "Drafting", "Drafted", "In Review",
    "Needs Revision", "Approved", "N/A",
}


def _now_iso() -> str:
    """ISO 8601 UTC timestamp for overlay entries."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class RowParseError(ValueError):
    """Row found by ID but did not have the expected 8-cell deliverable
    shape. Callers should treat as user-visible — the markdown is in an
    unexpected state and direct hand-edit is needed."""


# Deliverable row shape: `| ID | Deliverable | Scope | Phase | REF | Effort | Status | Path |`
# Status cell is index 6 (zero-based) when split on `|` after stripping
# leading/trailing pipes. Must allow `**Status**` bolded as well as plain.
_DELIVERABLE_ROW_RE = re.compile(
    r"^\|\s*(?P<id>[A-Z][A-Z0-9-]+)\s*\|"
)


def find_status_cell(md: str, row_id: str) -> tuple[int, str, str, str] | None:
    """Locate the Status cell for `row_id`. Returns
    (line_index, line_before_cell, line_after_cell, current_status)
    where the cell content (including any bold ** markers) lies between
    line_before_cell and line_after_cell. Returns None if no row matches.
    Raises RowParseError if the row exists but isn't 8-cell shaped."""
    lines = md.splitlines(keepends=False)
    for i, line in enumerate(lines):
        m = _DELIVERABLE_ROW_RE.match(line)
        if not m or m.group("id") != row_id:
            continue
        # 8-cell deliverable line: 9 pipes total when wrapped
        if line.count("|") < 9:
            raise RowParseError(
                f"row {row_id} has {line.count('|')} pipes; expected 9 (8 cells)"
            )
        # Find the 7th pipe (start of status cell) and the 8th pipe (end).
        positions = [j for j, c in enumerate(line) if c == "|"]
        # positions[0] = leading; positions[6] starts status cell;
        # positions[7] ends it.
        start = positions[6] + 1
        end = positions[7]
        cell_raw = line[start:end].strip()
        # Strip surrounding ** if present
        cell_clean = re.sub(r"^\*\*|\*\*$", "", cell_raw).strip()
        return i, line[:start], line[end:], cell_clean
    return None


def apply_status_change(md: str, row_id: str, new_status: str) -> str:
    """Return md with row `row_id`'s Status cell replaced by `new_status`.
    Preserves bold-formatting on the cell. Raises LookupError if not found,
    RowParseError if row shape is unexpected, ValueError if status invalid."""
    if new_status not in VALID_STATUSES:
        raise ValueError(
            f"status {new_status!r} not in valid set {sorted(VALID_STATUSES)}"
        )
    located = find_status_cell(md, row_id)
    if located is None:
        raise LookupError(f"row {row_id} not found in tracker md")
    line_idx, before, after, _current = located
    # Preserve the surrounding-bold convention used in the canonical file
    # (every Status cell in submission-tracker.md is bolded).
    new_cell = f" **{new_status}** "
    lines = md.splitlines(keepends=False)
    lines[line_idx] = before + new_cell + after
    # splitlines(keepends=False) drops the trailing newline; restore it if
    # the original had one.
    suffix = "\n" if md.endswith("\n") else ""
    return "\n".join(lines) + suffix


TRACKER_HUMAN_SIDECAR_REL = "docs/project/submissions/submission-tracker.human.json"


def _load_human_sidecar(wt: Path) -> dict:
    """Load the human overlay sidecar from the worktree. Returns the full
    document dict (with `schema_version` + `rows`) or a fresh skeleton."""
    sidecar_path = wt / TRACKER_HUMAN_SIDECAR_REL
    if not sidecar_path.is_file():
        return {"schema_version": "0.1", "rows": {}}
    try:
        data = json.loads(sidecar_path.read_text(encoding="utf-8"))
    except Exception:
        # Corrupt sidecar: re-init rather than swallow data; surface in caller.
        return {"schema_version": "0.1", "rows": {}}
    if not isinstance(data, dict):
        return {"schema_version": "0.1", "rows": {}}
    if "rows" not in data or not isinstance(data["rows"], dict):
        data["rows"] = {}
    if "schema_version" not in data:
        data["schema_version"] = "0.1"
    return data


def _resolve_md_status(wt: Path, row_id: str) -> str | None:
    """Read the row's current Status cell from submission-tracker.md (the
    generator-owned baseline before overlay is applied). Returns None if
    the row isn't found."""
    md_path = wt / TRACKER_MD_REL
    if not md_path.is_file():
        return None
    md = md_path.read_text(encoding="utf-8")
    located = find_status_cell(md, row_id)
    if located is None:
        return None
    _, _, _, status = located
    return status


def write_status_change(
    wt: Path,
    row_id: str,
    new_status: str,
    rationale: str | None,
    actor: str,
    task_path: Path | None = None,
    repo_root: Path | None = None,
) -> dict:
    """Full pipeline for one status change inside the worktree (overlay-first):
      1. read existing entry from submission-tracker.human.json (if any)
      2. write/update the row's overlay entry with new status + metadata
      3. regenerate submission-tracker.html via /tracker render (which
         applies the overlay at render time)
      4. append a changelog row to the session task doc (if task_path given)

    The submission-tracker.md is NOT modified — it stays generator-owned.
    The overlay is the durable record of human-curated divergence from the
    generator's structural view; /tracker generate re-applies the overlay
    on top of freshly-built rows so changes survive regeneration.

    Returns a structured result dict with old/new status + step outcomes.
    Idempotent across the read+write step (same input → same output)."""
    if new_status not in VALID_STATUSES:
        raise ValueError(f"invalid status {new_status!r}; must be one of {sorted(VALID_STATUSES)}")

    # Resolve old status: prefer existing overlay entry; fall back to md cell
    # (so the very first overlay write reports the meaningful old value).
    sidecar = _load_human_sidecar(wt)
    existing = sidecar["rows"].get(row_id) or {}
    old_status = existing.get("status") or _resolve_md_status(wt, row_id)
    if old_status is None:
        raise LookupError(f"row {row_id} not found in tracker md (cannot establish baseline)")

    # Write overlay entry. Preserve any prior fields (ref override, owner,
    # target_date, etc.) so a Status change doesn't clobber other curated
    # values; the human overlay is a per-row merge target.
    entry = dict(existing)
    entry["status"] = new_status
    entry["updated_at"] = _now_iso()
    entry["updated_by"] = actor
    if rationale:
        entry["notes"] = rationale
    sidecar["rows"][row_id] = entry

    sidecar_path = wt / TRACKER_HUMAN_SIDECAR_REL
    sidecar_path.parent.mkdir(parents=True, exist_ok=True)
    sidecar_path.write_text(json.dumps(sidecar, indent=2) + "\n", encoding="utf-8")
    wrote = True

    # Regenerate html so the dashboard / standalone view show the new
    # resolved state (md + overlay merged at render time).
    rendered = regenerate_html(repo_root or wt, wt)

    changelog_appended = False
    if task_path is not None:
        entry_line = (
            f"{_today()} — `{row_id}` Status: **{old_status}** → **{new_status}**"
            + (f" — {rationale}" if rationale else "")
            + f" (by {actor})"
        )
        changelog_appended = append_task_changelog(task_path, entry_line)
    return {
        "row_id": row_id,
        "old_status": old_status,
        "new_status": new_status,
        "written": wrote,
        "rendered": rendered,
        "changelog_appended": changelog_appended,
        "overlay_path": str(sidecar_path.relative_to(wt)),
    }


def regenerate_html(repo_root: Path, wt: Path) -> bool:
    """Invoke `/tracker render` against the worktree's submission-tracker.md
    so the HTML reflects the latest md edits. Returns True on success.
    Best-effort — failure leaves the prior HTML in place."""
    script = repo_root / ".claude/skills/tracker/scripts/render.py"
    if not script.is_file():
        return False
    try:
        r = subprocess.run(
            ["python3", str(script), "--project-dir", str(wt)],
            cwd=str(wt),
            capture_output=True,
            text=True,
            timeout=60,
        )
        return r.returncode == 0
    except Exception:
        return False


def _today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def append_task_changelog(task_path: Path, entry: str) -> bool:
    """Append `- {entry}` under the `## Changelog` section of the task doc.
    Creates the section if missing. Returns True on success."""
    if not task_path.is_file():
        return False
    text = task_path.read_text(encoding="utf-8")
    if "## Changelog" not in text:
        text = text.rstrip() + "\n\n## Changelog\n\n- " + entry + "\n"
    else:
        # Insert at end of file (after the last existing changelog entry).
        # The Changelog section is conventionally the last section in tracker
        # task docs, so an append-to-end works.
        text = text.rstrip() + "\n- " + entry + "\n"
    task_path.write_text(text, encoding="utf-8")
    return True


# ── Pending-changes view (read from task doc) ────────────────────────────

# Match a changelog entry written by write_status_change: dated row with
# `<row_id>` Status: **<old>** → **<new>** [— rationale] (by <actor>)
_CHANGELOG_ENTRY_RE = re.compile(
    r"^-\s+(?P<date>\d{4}-\d{2}-\d{2})\s+—\s+`(?P<row_id>[A-Z][A-Z0-9-]+)`\s+"
    r"Status:\s+\*\*(?P<old>[^*]+)\*\*\s+→\s+\*\*(?P<new>[^*]+)\*\*"
    r"(?:\s+—\s+(?P<rationale>.+?))?\s+\(by\s+(?P<actor>[^)]+)\)\s*$",
    re.MULTILINE,
)


def parse_pending_changes(task_path: Path) -> list[dict]:
    """Return the list of status-change entries parsed from the session
    task doc's Changelog. Used by the UI to render the sidebar pending-
    changes panel."""
    if not task_path.is_file():
        return []
    text = task_path.read_text(encoding="utf-8")
    out = []
    for m in _CHANGELOG_ENTRY_RE.finditer(text):
        out.append({
            "date": m.group("date"),
            "row_id": m.group("row_id"),
            "old_status": m.group("old"),
            "new_status": m.group("new"),
            "rationale": m.group("rationale"),
            "actor": m.group("actor"),
        })
    return out
