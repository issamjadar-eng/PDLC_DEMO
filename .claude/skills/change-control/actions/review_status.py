"""`change-control review-status <path>` — refresh task-doc section.

Reads the gdoc state (open comments, suggestions, body edits) and
refreshes the `## Internal Review — <path>` section in the user's
active task doc. Preserves Already-Addressed and Recently-Synced.
"""
from __future__ import annotations

import os
import sys
from datetime import datetime, timezone
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_ROOT))

# Ensure we're running on a Python with web-control's runtime deps;
# self-relaunches under the right interpreter if not.
from lib._runtime import ensure_runtime  # noqa: E402
ensure_runtime()

from lib.internal_review import (  # noqa: E402
    ReviewItem,
    ReviewSection,
    active_task_path,
    find_block,
    parse_section,
    upsert_block,
)
from lib.path_convention import project_root  # noqa: E402


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: review-status <path>", file=sys.stderr)
        return 64

    rel_path = sys.argv[1].strip()
    root = project_root()

    session_id = os.environ.get("CLAUDE_SESSION_ID", "")
    task_doc_path = active_task_path(session_id, root) if session_id else None
    if task_doc_path is None:
        print("ERROR: no active task doc.", file=sys.stderr)
        return 1

    text = task_doc_path.read_text()
    block_range = find_block(text, rel_path)
    if block_range is None:
        print(
            f"ERROR: no internal-review section found in {task_doc_path.name} "
            f"for {rel_path}. Run `change-control review-start {rel_path}` first.",
            file=sys.stderr,
        )
        return 1

    # Extract the existing block + parse it
    lines = text.splitlines(keepends=False)
    start, end = block_range
    block_text = "\n".join(lines[start : end + 1])
    section = parse_section(block_text)

    if not section.gdoc_url or section.gdoc_url.startswith("<"):
        print(
            "WARN: GDoc URL not yet set in the task-doc section. "
            "Edit the section to paste the URL after creating the gdoc."
        )
        return 0

    print(f"change-control review-status {rel_path}")
    print(f"  Task doc:   {task_doc_path.name}")
    print(f"  GDoc:       {section.gdoc_url}")
    print()

    # ----- v0.1 implementation: pull state from web-control + diff -----
    #
    # Live behavior: connect to web-control's debug Chrome, find the gdoc
    # tab, read open comments + suggestions + body. Diff against last
    # snapshot in .state/web-control/<gdoc-id>.last-sync.json. Update the
    # section's Open list with the new state. Preserve Already-Addressed
    # and Recently-Synced.
    #
    # If web-control isn't running, print clear guidance and return.

    try:
        from lib import gdoc as gdoc_lib  # noqa: WPS433
    except ImportError as exc:
        print(f"ERROR: gdoc lib import failed: {exc}", file=sys.stderr)
        return 1

    try:
        comments = gdoc_lib.list_open_comments(section.gdoc_url)
        suggestions = gdoc_lib.list_open_suggestions(section.gdoc_url)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: could not read gdoc state: {exc}", file=sys.stderr)
        print(
            "  Recovery: ensure /web-control is running and you are signed in.",
            file=sys.stderr,
        )
        return 1

    # Body-edit detection: compare current gdoc body against the cached
    # last-pushed snapshot. Differences that are NOT covered by comments
    # or suggestions get surfaced as #e-N body-edit items.
    body_edits: list[tuple[str, str]] = []  # (id, preview)
    try:
        gdoc_id = section.gdoc_url.split("/document/d/", 1)[-1].split("/", 1)[0]
        push_snapshot = root / ".state" / "web-control" / f"{gdoc_id}.last-push.txt"
        if push_snapshot.is_file():
            last_push = push_snapshot.read_text()
            current_body = gdoc_lib.read_body_text(section.gdoc_url).text
            if current_body and last_push and current_body.strip() != last_push.strip():
                # Surface as a single body-edit summary item; line-level diff
                # is a v0.3 enhancement.
                preview = "doc body differs from last `review-update` push"
                # Find first differing chunk (~100 chars) for human context
                import difflib
                diff = list(difflib.unified_diff(
                    last_push.splitlines(), current_body.splitlines(),
                    n=1, lineterm="",
                ))
                added = [d[1:] for d in diff if d.startswith("+") and not d.startswith("+++")][:3]
                if added:
                    preview = f"changes include: " + " | ".join(a[:60] for a in added if a.strip())
                body_edits.append(("e-1", preview))
    except Exception:  # noqa: BLE001
        # Body-edit detection is best-effort; never block status read
        pass

    # Refresh Open list — replace existing
    section.open_items = []
    for i, c in enumerate(comments, start=1):
        section.open_items.append(ReviewItem(
            kind="comment",
            id=f"c-{i}",
            author=c.author,
            anchor=c.anchor_text,
            text=c.text,
            status="open",
        ))
    for i, s in enumerate(suggestions, start=1):
        section.open_items.append(ReviewItem(
            kind="suggestion",
            id=f"s-{i}",
            author=s.author,
            anchor=s.anchor_text,
            text=f"{s.before} → {s.after}" if s.before or s.after else "",
            status="open",
        ))
    # Surface body edits as #e-N items
    for be_id, be_preview in body_edits:
        section.open_items.append(ReviewItem(
            kind="body-edit",
            id=be_id,
            author="(direct edit)",
            anchor="doc body",
            text=be_preview,
            status="open",
        ))

    section.last_sync = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Upsert
    new_text = upsert_block(text, section)
    task_doc_path.write_text(new_text)

    print(f"  Open: {len([i for i in section.open_items if i.kind == 'comment'])} comments · "
          f"{len([i for i in section.open_items if i.kind == 'suggestion'])} suggestions · "
          f"{len([i for i in section.open_items if i.kind == 'body-edit'])} body edits")
    print(f"  Already addressed: {len(section.already_addressed)} (will reply on next `review-update`)")
    print(f"  ✓ Refreshed metadata block in {task_doc_path.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
