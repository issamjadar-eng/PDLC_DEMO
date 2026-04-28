"""`change-control review-start <path>` — kick off internal review for a doc.

Creates a Google Doc in the user's `AI_PDLC/<project>/<task_folder>/`
folder, pastes the source content, writes a metadata block to the user's
active task doc, and prints a manual-share reminder.

Usage:
    python3 actions/review_start.py <path>

Args:
    <path> — repo-relative path to the source md or docx file to review
"""
from __future__ import annotations

import os
import sys
from datetime import datetime, timezone
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_ROOT))

# Self-relaunch under a Python with web-control's runtime deps if needed
from lib._runtime import ensure_runtime  # noqa: E402
ensure_runtime()

from lib.path_convention import (  # noqa: E402
    AI_PDLC_PREFIX,
    drive_path_for,
    project_name,
    project_root,
    resolve_current_user_task_folder,
)
from lib.internal_review import (  # noqa: E402
    ReviewSection,
    active_task_path,
    upsert_block,
)


def _read_source_content(src: Path) -> str:
    """Read source file content. .md → text. .docx → message asking user
    to use the Drive UI upload-and-convert flow (not automated in v0.1)."""
    suffix = src.suffix.lower()
    if suffix in (".md", ".markdown", ".txt"):
        return src.read_text()
    if suffix == ".docx":
        # v0.1: docx upload-and-convert is documented but not automated.
        return ""
    return src.read_text()


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: review-start <path>", file=sys.stderr)
        return 64

    rel_path = sys.argv[1].strip()
    root = project_root()
    src = (root / rel_path).resolve()

    if not src.is_file():
        print(f"ERROR: file not found: {src}", file=sys.stderr)
        return 65

    # Resolve identity + drive path
    try:
        task_folder = resolve_current_user_task_folder()
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    components = drive_path_for(rel_path, task_folder=task_folder)
    drive_folder = "/".join(components[:-1]) + "/"
    doc_name = components[-1]

    print(f"change-control review-start")
    print(f"  Source:        {rel_path}")
    print(f"  User:          {task_folder}")
    print(f"  Drive folder:  {drive_folder}")
    print(f"  Doc name:      {doc_name}")
    print()

    # Find active task doc
    session_id = os.environ.get("CLAUDE_SESSION_ID", "")
    task_doc_path = active_task_path(session_id, root) if session_id else None
    if task_doc_path is None:
        print(
            "ERROR: no active task doc found. Activate a task first via "
            "`/task setup activate <NNN>`.",
            file=sys.stderr,
        )
        return 1
    print(f"  Active task:   {task_doc_path.relative_to(root)}")
    print()

    src_content = _read_source_content(src)

    # ----- v0.2: auto-create the gdoc + paste content -----
    gdoc_url = ""
    auto_created = False
    if src_content:
        try:
            from lib import gdoc as gdoc_lib  # noqa: WPS433
            print(f"  Auto-creating gdoc + pasting content (web-control required)...")
            # Make sure Markdown preference is on so the paste auto-formats.
            # Best-effort — fails silently if the menu UI changed.
            try:
                wc = gdoc_lib._wc()
                chrome = wc["connect_to_chrome"]()
                # Ensure there is at least one doc tab so enable_markdown_preference
                # has a host to drive against. Skip if we'd need to create a
                # throwaway doc (just rely on the gdoc we're about to create).
                gdoc_url = gdoc_lib.create_new_gdoc(doc_name, folder_url="")
                print(f"  ✓ created gdoc: {gdoc_url}")
                # Now enable markdown preference on the freshly-opened doc
                gdoc_lib.enable_markdown_preference(chrome)
                # Paste content
                import time as _t
                _t.sleep(1)
                gdoc_lib.paste_markdown_into_doc(gdoc_url, src_content, replace_body=True)
                print(f"  ✓ pasted content")
                auto_created = True
            except Exception as exc:  # noqa: BLE001
                print(f"  WARN: auto-create failed ({exc}); falling back to manual steps")
                gdoc_url = ""
        except ImportError as exc:
            print(f"  WARN: gdoc lib import failed ({exc}); falling back to manual steps")

    if not auto_created:
        print()
        print("Manual steps (auto-create unavailable — Drive rate-limited or web-control offline):")
        print(f"  1. Open Drive: https://drive.google.com/drive/my-drive")
        print(f"  2. Navigate to (or create): {drive_folder}")
        print(f"  3. New → Google Docs (blank), rename to: {doc_name}")
        print(f"  4. Tools → Preferences → enable 'Markdown' (one-time per profile)")
        print(f"  5. Select all in the doc, delete, then paste the source content")
        print(f"     (source content is in your local file: {src})")
        print(f"  6. Copy the gdoc URL from the address bar and paste into the task-doc section")
    print()

    # Reminder: sharing is always manual (v0.1 decision per Q5)
    print("REMEMBER: open the gdoc and click Share to invite your reviewer group.")
    print("          (v0.1 does not auto-share — your call who sees it.)")
    print()

    # Write the metadata block
    section = ReviewSection.new(
        doc_path=rel_path,
        gdoc_url=gdoc_url or "<paste gdoc URL here after creating>",
        drive_folder=drive_folder,
    )
    task_doc_text = task_doc_path.read_text()
    new_text = upsert_block(task_doc_text, section)
    task_doc_path.write_text(new_text)
    print(f"  ✓ Wrote internal-review metadata block to {task_doc_path.name}")
    if not auto_created:
        print(f"     -> Edit the GDoc field with the URL once you create the doc")
    print()

    print("Once reviewers have started commenting, run:")
    print(f"  change-control review-status {rel_path}")
    print("to refresh the task-doc section with the latest open items.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
