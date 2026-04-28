"""`change-control review-abort <path>` — cancel internal review.

Removes the metadata block from the active task doc and deletes the
.state/web-control/<gdoc-id>.{last-sync.json,last-push.txt} state files.
Does NOT delete the gdoc — user can manually clean up in Drive.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_ROOT))

# Self-relaunch under a Python with web-control's runtime deps if needed
from lib._runtime import ensure_runtime  # noqa: E402
ensure_runtime()

from lib.internal_review import (  # noqa: E402
    active_task_path,
    find_block,
    parse_section,
    remove_block,
)
from lib.path_convention import project_root  # noqa: E402


def _gdoc_id_from_url(url: str) -> str:
    if "/document/d/" in url:
        return url.split("/document/d/", 1)[1].split("/", 1)[0]
    return ""


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: review-abort <path>", file=sys.stderr)
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
        print(f"No internal-review section found for {rel_path}. Nothing to abort.")
        return 0

    lines = text.splitlines(keepends=False)
    start, end = block_range
    section = parse_section("\n".join(lines[start : end + 1]))

    print(f"change-control review-abort {rel_path}")
    print(f"  GDoc:        {section.gdoc_url}")

    # Delete state files
    gdoc_id = _gdoc_id_from_url(section.gdoc_url)
    state_dir = root / ".state" / "web-control"
    deleted: list[str] = []
    if gdoc_id:
        for suffix in (".last-sync.json", ".last-push.txt"):
            f = state_dir / f"{gdoc_id}{suffix}"
            if f.is_file():
                f.unlink()
                deleted.append(f.name)

    # Remove block from task doc
    new_text = remove_block(text, rel_path)
    task_doc_path.write_text(new_text)

    print(f"  ✓ Removed metadata block from {task_doc_path.name}")
    print(f"  ✓ Deleted {len(deleted)} state file(s): {', '.join(deleted) if deleted else '(none)'}")
    print()
    print("Note: the gdoc itself is still in Drive. Delete or rename manually if desired.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
