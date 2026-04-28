"""`change-control freeze <path>` — Phase 1 → Phase 2 transition.

v0.4 wires the internal-review archive flow:
  - If the user's active task doc has an internal-review section for
    this path, archive the gdoc (banner + close-comments + rename) and
    demote the section to "Archived internal reviews".
  - Then proceed with the existing freeze flow (Confluence/Comala) —
    which is still scaffold/stub for the formal-review tier.

The Confluence-side of freeze remains a stub. This action ships the
internal-review archive end-of-life today; the formal-review entry is
documented in the design doc.
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

from lib.internal_review import (  # noqa: E402
    ReviewSection,
    active_task_path,
    find_block,
    parse_section,
    upsert_block,
)
from lib.path_convention import project_root  # noqa: E402


def _archive_internal_review(rel_path: str) -> dict:
    """If there's an active internal-review section for rel_path in the
    user's active task doc, archive its gdoc + demote the section.

    Returns a status dict, or None if no section is found."""
    root = project_root()
    session_id = os.environ.get("CLAUDE_SESSION_ID", "")
    task_doc_path = active_task_path(session_id, root) if session_id else None
    if task_doc_path is None:
        return {"skipped": True, "reason": "no active task doc"}

    text = task_doc_path.read_text()
    block_range = find_block(text, rel_path)
    if block_range is None:
        return {"skipped": True, "reason": "no internal-review section for this path"}

    lines = text.splitlines(keepends=False)
    start, end = block_range
    section = parse_section("\n".join(lines[start : end + 1]))
    if not section.gdoc_url or section.gdoc_url.startswith("<"):
        return {"skipped": True, "reason": "section exists but gdoc URL not set"}

    # Already archived?
    if section.status == "archived":
        return {"skipped": True, "reason": "section already archived"}

    print(f"  Archiving internal-review gdoc: {section.gdoc_url}")
    try:
        from lib import gdoc as gdoc_lib  # noqa: WPS433
        freeze_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        result = gdoc_lib.archive_gdoc(
            section.gdoc_url,
            freeze_date=freeze_date,
            confluence_link="",  # filled by Confluence-side flow when implemented
        )
        # Demote the task-doc section
        section.status = "archived"
        new_text = upsert_block(text, section)
        task_doc_path.write_text(new_text)
        print(f"  ✓ Section demoted to archived in {task_doc_path.name}")

        # Clean up state files
        gdoc_id = section.gdoc_url.split("/document/d/", 1)[-1].split("/", 1)[0]
        state_dir = root / ".state" / "web-control"
        for suffix in (".last-sync.json", ".last-push.txt"):
            f = state_dir / f"{gdoc_id}{suffix}"
            if f.is_file():
                f.unlink()
        return {"archived": True, "result": result}
    except Exception as exc:  # noqa: BLE001
        return {"archived": False, "error": str(exc)}


def main(argv: list[str]) -> int:
    if not argv:
        print("usage: change-control freeze <path>", file=sys.stderr)
        return 64
    rel_path = argv[0].strip()

    print(f"change-control freeze {rel_path}")
    print()

    # Step 1: archive any active internal-review gdoc
    print("Step 1: archive internal-review gdoc (if any)")
    archive_result = _archive_internal_review(rel_path)
    if archive_result.get("skipped"):
        print(f"  skipped: {archive_result['reason']}")
    elif archive_result.get("archived"):
        result = archive_result.get("result", {})
        print(f"  banner_prepended: {result.get('banner_prepended')}")
        print(f"  comments_closed:  {result.get('comments_closed')}")
        print(f"  renamed:          {result.get('renamed')} ({result.get('new_title','')!r})")
        if result.get("errors"):
            print(f"  errors:           {result['errors']}")
    else:
        print(f"  ERROR: {archive_result.get('error')}")
    print()

    # Step 2-8: Confluence/Comala flow — still scaffold
    print("Step 2-8: Confluence/Comala/Jira flow — scaffold (NOT IMPLEMENTED)")
    print("  See SKILL.md 'freeze' section for the planned flow.")
    print(f"  In production this will: render md → Confluence, set state: frozen,")
    print(f"  capture page-id + commit, etc.")
    print()
    print("freeze (internal-review archive) complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
