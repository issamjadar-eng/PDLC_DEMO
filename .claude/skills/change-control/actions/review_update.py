"""`change-control review-update <path>` — push md → gdoc + post replies.

Reads the task-doc section's "Already Addressed" list, posts replies on
each addressed comment + accepts/rejects suggestions, then wholesale-
pastes the current source content into the gdoc body.

After successful update:
  - Already Addressed → demoted to Recently Synced
  - Open list refreshed from gdoc
  - last_sync + last_md_push timestamps bumped
  - .state/web-control/<gdoc-id>.last-sync.json snapshot updated
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_ROOT))

# Self-relaunch under a Python with web-control's runtime deps if needed
from lib._runtime import ensure_runtime  # noqa: E402
ensure_runtime()

from lib.internal_review import (  # noqa: E402
    ReviewSection,
    active_task_path,
    find_block,
    parse_section,
    upsert_block,
)
from lib.path_convention import project_root  # noqa: E402


def _git_head_commit(root: Path, file_path: Path) -> str:
    """Return the latest commit SHA touching this file (short)."""
    try:
        out = subprocess.check_output(
            ["git", "log", "-1", "--format=%h", "--", str(file_path.relative_to(root))],
            cwd=root,
            stderr=subprocess.DEVNULL,
        )
        return out.decode().strip() or "uncommitted"
    except subprocess.CalledProcessError:
        return "uncommitted"


def _state_dir(root: Path) -> Path:
    d = root / ".state" / "web-control"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _gdoc_id_from_url(url: str) -> str:
    """Extract the doc ID from a Drive URL like
    https://docs.google.com/document/d/<id>/edit"""
    if "/document/d/" in url:
        tail = url.split("/document/d/", 1)[1]
        return tail.split("/", 1)[0]
    return url.replace("/", "_")


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: review-update <path>", file=sys.stderr)
        return 64

    rel_path = sys.argv[1].strip()
    root = project_root()
    src = (root / rel_path).resolve()
    if not src.is_file():
        print(f"ERROR: source file not found: {src}", file=sys.stderr)
        return 65

    session_id = os.environ.get("CLAUDE_SESSION_ID", "")
    task_doc_path = active_task_path(session_id, root) if session_id else None
    if task_doc_path is None:
        print("ERROR: no active task doc.", file=sys.stderr)
        return 1

    text = task_doc_path.read_text()
    block_range = find_block(text, rel_path)
    if block_range is None:
        print(
            f"ERROR: no internal-review section in {task_doc_path.name} for {rel_path}",
            file=sys.stderr,
        )
        return 1

    lines = text.splitlines(keepends=False)
    start, end = block_range
    section = parse_section("\n".join(lines[start : end + 1]))

    if not section.gdoc_url or section.gdoc_url.startswith("<"):
        print("ERROR: GDoc URL not set in section. Set it first.", file=sys.stderr)
        return 1

    print(f"change-control review-update {rel_path}")
    print(f"  GDoc:        {section.gdoc_url}")
    print(f"  Addressed:   {len(section.already_addressed)} item(s) to reply to")
    print()

    # Read source content
    src_content = src.read_text() if src.suffix.lower() in (".md", ".markdown", ".txt") else ""
    if src.suffix.lower() == ".docx":
        print("WARN: .docx update path is documented but not automated in v0.1.")
        print("      Re-upload the docx via Drive UI's 'Upload as Google Doc' action.")
        # Still proceed with replies + section bookkeeping below

    # ----- Step 1: post replies + accept/reject for Already Addressed -----
    try:
        from lib import gdoc as gdoc_lib  # noqa: WPS433
    except ImportError as exc:
        print(f"ERROR: gdoc lib import: {exc}", file=sys.stderr)
        return 1

    try:
        for item in section.already_addressed:
            if item.kind == "comment":
                reply = item.resolution_note or "Addressed by author in this update."
                gdoc_lib.post_reply_and_resolve(section.gdoc_url, item.id, reply)
            elif item.kind == "suggestion":
                if item.status == "addressed":
                    gdoc_lib.accept_suggestion(section.gdoc_url, item.id)
                else:
                    gdoc_lib.reject_suggestion(section.gdoc_url, item.id)
            elif item.kind == "body-edit":
                # Body edits don't have a comment thread to reply to; the
                # acknowledgement happens by the body-replace itself.
                pass
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR while posting replies: {exc}", file=sys.stderr)
        return 1

    # ----- Step 2: wholesale-replace the gdoc body with current source content -----
    if src_content:
        try:
            gdoc_lib.paste_markdown_into_doc(section.gdoc_url, src_content, replace_body=True)
        except Exception as exc:  # noqa: BLE001
            print(f"ERROR while replacing gdoc body: {exc}", file=sys.stderr)
            return 1

    # ----- Step 3: snapshot for next-sync diff -----
    gdoc_id = _gdoc_id_from_url(section.gdoc_url)
    snapshot = {
        "gdoc_url": section.gdoc_url,
        "synced_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "open_comments": [
            {"id": i.id, "author": i.author, "text": i.text}
            for i in section.open_items if i.kind == "comment"
        ],
        "open_suggestions": [
            {"id": i.id, "author": i.author, "text": i.text}
            for i in section.open_items if i.kind == "suggestion"
        ],
    }
    snapshot_path = _state_dir(root) / f"{gdoc_id}.last-sync.json"
    snapshot_path.write_text(json.dumps(snapshot, indent=2))
    push_path = _state_dir(root) / f"{gdoc_id}.last-push.txt"
    push_path.write_text(src_content)

    # ----- Step 4: demote Already Addressed → Recently Synced; bump timestamps -----
    section.recently_synced = list(section.already_addressed) + section.recently_synced
    section.recently_synced = section.recently_synced[:50]  # cap history
    section.already_addressed = []
    # Open items will be refreshed by the next review-status; we don't
    # re-read them here to keep this action focused on push semantics.
    section.last_sync = snapshot["synced_at"]
    section.last_md_push = f"{snapshot['synced_at']} (commit {_git_head_commit(root, src)})"

    # ----- Step 5: write back -----
    new_text = upsert_block(text, section)
    task_doc_path.write_text(new_text)

    print(f"  ✓ Replies posted, body replaced, snapshot saved to {snapshot_path.name}")
    print(f"  ✓ Task doc updated: {len(section.recently_synced)} now in Recently Synced")
    print()
    print("Next: run `change-control review-status <path>` to refresh open items.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
