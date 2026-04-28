"""Task-doc metadata-block read/write for the internal-review tier.

The metadata block is a sentinel-bounded section in the user's active
task doc. The skill writes and refreshes it; the user (and Claude) reads
and edits it. Block format:

    <!-- change-control:internal-review begin doc=<repo-path> -->
    ## Internal Review — `<repo-path>`

    | Field | Value |
    |---|---|
    | GDoc | https://docs.google.com/document/d/<id> |
    | Drive folder | AI_PDLC/<project>/<task_folder>/ |
    | Reviewers | _(populated manually)_ |
    | First pushed | 2026-04-27T11:30:00Z |
    | Last sync | 2026-04-28T09:15:00Z |
    | Last md push | 2026-04-27T11:30:00Z (commit a3f9c21) |
    | Open | 2 comments · 1 suggestion · 0 body edits |
    | Already addressed | 0 |

    ### Open

    - [ ] **#c-1** Maryna · § 4.2 · `"...sufficient..."`
          > This needs a citation.

    ### Already Addressed (will reply on next `review-update`)

    (none yet)

    ### Recently Synced

    (none yet)
    <!-- change-control:internal-review end -->

The `doc=<repo-path>` attribute on the opening sentinel lets us find the
right block when a single task doc tracks multiple internal reviews.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


SENTINEL_BEGIN_RE = re.compile(
    r"<!--\s*change-control:internal-review\s+begin\s+doc=(?P<doc>[^\s>]+)\s*-->"
)
SENTINEL_END = "<!-- change-control:internal-review end -->"


@dataclass
class ReviewItem:
    """One open or addressed item in the metadata block."""

    kind: str  # 'comment', 'suggestion', 'body-edit'
    id: str  # e.g., 'c-1', 's-2', 'e-3'
    author: str = ""
    anchor: str = ""  # location/section preview
    text: str = ""  # comment body OR suggestion before/after OR body-edit diff
    status: str = "open"  # 'open', 'addressed', 'deferred', 'wont-fix'
    resolution_note: str = ""  # what the author did; blank when status=open

    @property
    def kind_short(self) -> str:
        return {"comment": "c", "suggestion": "s", "body-edit": "e"}.get(self.kind, "?")


@dataclass
class ReviewSection:
    """In-memory model of one internal-review block in a task doc."""

    doc_path: str  # repo-relative path of the source md/docx
    gdoc_url: str = ""
    drive_folder: str = ""
    reviewers: str = ""  # free text, populated manually by user
    first_pushed: str = ""  # ISO 8601
    last_sync: str = ""  # ISO 8601
    last_md_push: str = ""  # ISO 8601 + commit
    open_items: list[ReviewItem] = field(default_factory=list)
    already_addressed: list[ReviewItem] = field(default_factory=list)
    recently_synced: list[ReviewItem] = field(default_factory=list)
    status: str = "active"  # 'active' | 'archived'

    @classmethod
    def new(cls, doc_path: str, gdoc_url: str, drive_folder: str) -> "ReviewSection":
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        return cls(
            doc_path=doc_path,
            gdoc_url=gdoc_url,
            drive_folder=drive_folder,
            first_pushed=now,
            last_sync=now,
            last_md_push=now,
        )


# ----------------------------------------------------------------------------
# Render
# ----------------------------------------------------------------------------


def _format_item_line(item: ReviewItem) -> str:
    """Render a single item as a markdown bullet line."""
    short = item.kind_short
    label = f"**#{short}-{item.id.split('-')[-1]}**" if "-" not in item.id else f"**#{item.id}**"
    parts = [item.author, item.anchor]
    parts = [p for p in parts if p]
    head = " · ".join(parts) if parts else ""
    if item.status in ("open",):
        line = f"- [ ] {label}"
        if head:
            line += f" {head}"
        if item.text:
            line += f"\n      > {item.text}"
        return line
    # addressed/deferred/won't-fix
    line = f"- [x] {label}"
    if head:
        line += f" {head}"
    if item.resolution_note:
        line += f" — {item.status}: {item.resolution_note}"
    elif item.status != "open":
        line += f" — {item.status}"
    return line


def render_section(section: ReviewSection) -> str:
    """Render the full sentinel-bounded metadata block as markdown."""
    n_open_comments = sum(1 for it in section.open_items if it.kind == "comment")
    n_open_suggestions = sum(1 for it in section.open_items if it.kind == "suggestion")
    n_open_bodyedits = sum(1 for it in section.open_items if it.kind == "body-edit")

    lines: list[str] = []
    lines.append(f"<!-- change-control:internal-review begin doc={section.doc_path} -->")
    if section.status == "archived":
        lines.append(f"### Archived internal reviews — `{section.doc_path}`")
    else:
        lines.append(f"## Internal Review — `{section.doc_path}`")
    lines.append("")
    lines.append("| Field | Value |")
    lines.append("|---|---|")
    lines.append(f"| GDoc | {section.gdoc_url or '_(pending)_'} |")
    lines.append(f"| Drive folder | {section.drive_folder or '_(pending)_'} |")
    lines.append(f"| Reviewers | {section.reviewers or '_(populated manually by user — v0.1 does not auto-share)_'} |")
    lines.append(f"| First pushed | {section.first_pushed or '_(pending)_'} |")
    lines.append(f"| Last sync | {section.last_sync or '_(never)_'} |")
    lines.append(f"| Last md push | {section.last_md_push or '_(pending)_'} |")
    lines.append(
        f"| Open | {n_open_comments} comments · {n_open_suggestions} suggestions · {n_open_bodyedits} body edits |"
    )
    lines.append(f"| Already addressed (will reply on next `review-update`) | {len(section.already_addressed)} |")
    if section.status == "archived":
        lines.append(f"| Status | **archived** (see `change-control freeze`) |")
    lines.append("")

    lines.append("### Open")
    lines.append("")
    if section.open_items:
        for it in section.open_items:
            lines.append(_format_item_line(it))
    else:
        lines.append("(none)")
    lines.append("")

    lines.append("### Already Addressed (will reply on next `review-update`)")
    lines.append("")
    if section.already_addressed:
        for it in section.already_addressed:
            lines.append(_format_item_line(it))
    else:
        lines.append("(none yet)")
    lines.append("")

    lines.append("### Recently Synced")
    lines.append("")
    if section.recently_synced:
        for it in section.recently_synced:
            lines.append(_format_item_line(it))
    else:
        lines.append("(none yet)")
    lines.append("")

    lines.append(SENTINEL_END)
    return "\n".join(lines)


# ----------------------------------------------------------------------------
# Parse
# ----------------------------------------------------------------------------

_TABLE_ROW_RE = re.compile(r"^\|\s*([^|]+?)\s*\|\s*(.+?)\s*\|$")
_OPEN_ITEM_RE = re.compile(
    r"^\s*-\s*\[\s\]\s+\*\*#(?P<id>[a-z\d-]+)\*\*\s*(?P<rest>.*)$"
)
_DONE_ITEM_RE = re.compile(
    r"^\s*-\s*\[x\]\s+\*\*#(?P<id>[a-z\d-]+)\*\*\s*(?P<rest>.*)$"
)


def _parse_item_line(line: str, next_line: str | None, status: str) -> ReviewItem | None:
    """Parse a single bullet line + optional follow-on quoted line into a ReviewItem."""
    m = _OPEN_ITEM_RE.match(line) if status == "open" else _DONE_ITEM_RE.match(line)
    if not m:
        return None
    id_token = m.group("id")
    rest = m.group("rest").strip()
    # id_token like 'c-1', 's-2', 'e-3' or just 'c1'
    short = id_token[0] if id_token else "?"
    kind = {"c": "comment", "s": "suggestion", "e": "body-edit"}.get(short, "comment")
    # Split rest by ' · ' for author / anchor
    author = ""
    anchor = ""
    if rest:
        bits = [b.strip() for b in rest.split("·")]
        bits = [b for b in bits if b]
        if bits:
            author = bits[0]
        if len(bits) > 1:
            anchor = " · ".join(bits[1:])
    text = ""
    resolution_note = ""
    if status == "open" and next_line and next_line.lstrip().startswith(">"):
        text = next_line.lstrip().lstrip(">").strip()
    if status != "open":
        # Addressed lines have format "rest — addressed: note"
        em_dash_split = rest.rsplit("—", 1)
        if len(em_dash_split) == 2:
            resolution_part = em_dash_split[1].strip()
            if ":" in resolution_part:
                stat, note = resolution_part.split(":", 1)
                # Override status from the line if it's a known one
                if stat.strip() in ("addressed", "deferred", "wont-fix"):
                    status = stat.strip()
                resolution_note = note.strip()
            else:
                if resolution_part in ("addressed", "deferred", "wont-fix"):
                    status = resolution_part
    return ReviewItem(
        kind=kind,
        id=id_token,
        author=author,
        anchor=anchor,
        text=text,
        status=status,
        resolution_note=resolution_note,
    )


def parse_section(block_text: str) -> ReviewSection:
    """Parse a sentinel-bounded block back into a ReviewSection."""
    lines = block_text.splitlines()
    # Find doc_path from opening sentinel
    doc_path = ""
    for line in lines:
        m = SENTINEL_BEGIN_RE.search(line)
        if m:
            doc_path = m.group("doc")
            break
    section = ReviewSection(doc_path=doc_path)
    # Parse the table rows
    field_map = {
        "GDoc": "gdoc_url",
        "Drive folder": "drive_folder",
        "Reviewers": "reviewers",
        "First pushed": "first_pushed",
        "Last sync": "last_sync",
        "Last md push": "last_md_push",
    }
    for line in lines:
        m = _TABLE_ROW_RE.match(line)
        if m:
            key = m.group(1).strip()
            val = m.group(2).strip()
            if key == "Status" and "archived" in val.lower():
                section.status = "archived"
                continue
            attr = field_map.get(key)
            if attr and not val.startswith("_"):
                setattr(section, attr, val)
    # Parse the three subsection lists
    current = None  # 'open' | 'addressed' | 'synced'
    for i, raw in enumerate(lines):
        s = raw.strip()
        if s.startswith("### Open"):
            current = "open"
        elif s.startswith("### Already Addressed"):
            current = "addressed"
        elif s.startswith("### Recently Synced"):
            current = "synced"
        elif s.startswith("### Archived") or s.startswith("##"):
            # Don't switch out of subsection on the H2; only ### sub-headings
            if s.startswith("### "):
                current = None
        elif current and s.startswith("- ["):
            next_line = lines[i + 1] if i + 1 < len(lines) else None
            status = "open" if current == "open" else "addressed"
            item = _parse_item_line(raw, next_line, status)
            if item:
                if current == "open":
                    section.open_items.append(item)
                elif current == "addressed":
                    section.already_addressed.append(item)
                elif current == "synced":
                    section.recently_synced.append(item)
    return section


# ----------------------------------------------------------------------------
# Find / replace blocks in a task doc
# ----------------------------------------------------------------------------


def find_block(task_doc_text: str, doc_path: str) -> tuple[int, int] | None:
    """Return (start_line, end_line) indices (0-based, inclusive) of the
    sentinel-bounded block matching doc_path, or None if not found."""
    lines = task_doc_text.splitlines(keepends=False)
    start = None
    for i, line in enumerate(lines):
        m = SENTINEL_BEGIN_RE.search(line)
        if m and m.group("doc") == doc_path:
            start = i
            break
    if start is None:
        return None
    for j in range(start + 1, len(lines)):
        if SENTINEL_END in lines[j]:
            return (start, j)
    return None


def upsert_block(task_doc_text: str, section: ReviewSection) -> str:
    """Insert or replace the section's block in the task doc text. Returns
    the updated text."""
    new_block = render_section(section)
    existing = find_block(task_doc_text, section.doc_path)
    lines = task_doc_text.splitlines(keepends=False)
    new_lines = new_block.splitlines(keepends=False)
    if existing is None:
        # Append at the end with a separator
        if lines and lines[-1] != "":
            lines.append("")
        lines.extend(new_lines)
        lines.append("")
        return "\n".join(lines) + ("\n" if not task_doc_text.endswith("\n") else "")
    start, end = existing
    new_doc = lines[:start] + new_lines + lines[end + 1 :]
    return "\n".join(new_doc) + ("\n" if not task_doc_text.endswith("\n") else "")


def remove_block(task_doc_text: str, doc_path: str) -> str:
    """Remove a block entirely (e.g., on review-abort). Returns updated text."""
    existing = find_block(task_doc_text, doc_path)
    if existing is None:
        return task_doc_text
    lines = task_doc_text.splitlines(keepends=False)
    start, end = existing
    new_doc = lines[:start] + lines[end + 1 :]
    return "\n".join(new_doc) + ("\n" if not task_doc_text.endswith("\n") else "")


# ----------------------------------------------------------------------------
# Active-task lookup
# ----------------------------------------------------------------------------


def active_task_path(session_id: str, project_root: Path) -> Path | None:
    """Read the per-session active-task state file and return the path to
    the user's active task doc. Returns None if no active task."""
    state_file = project_root / ".state" / f"active-tasks-{session_id}.txt"
    if not state_file.is_file():
        return None
    task_ids = [t.strip() for t in state_file.read_text().splitlines() if t.strip()]
    if not task_ids:
        return None
    # The state file holds task IDs (e.g., "116"). To find the task doc,
    # walk tasks/<person>/ folders for a file starting with the ID.
    tasks_root = project_root / "tasks"
    if not tasks_root.is_dir():
        return None
    target_id = task_ids[0]  # use the most recently activated (first listed)
    for person_dir in tasks_root.iterdir():
        if not person_dir.is_dir():
            continue
        for entry in person_dir.iterdir():
            if entry.is_file() and entry.name.startswith(f"{target_id}-") and entry.suffix == ".md":
                return entry
    return None
