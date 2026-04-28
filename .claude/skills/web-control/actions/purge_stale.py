"""`/web-control purge-stale` — clean up orphan state files.

Walks `.state/web-control/` and deletes any file whose <gdoc-id> doesn't
appear in any active task-doc internal-review section across the team's
task folders. Defensive sweep complementing the explicit deletes that
happen in change-control freeze / review-abort.

Per task ben/116 Q12 (locked 2026-04-27): state files mustn't leak.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_ROOT))


def _project_root() -> Path:
    """Walk up until we find a project.yml."""
    cur = Path.cwd().resolve()
    for parent in [cur] + list(cur.parents):
        if (parent / "project.yml").is_file():
            return parent
    raise RuntimeError("could not locate project.yml")


_GDOC_ID_RE = re.compile(r"docs\.google\.com/document/d/([a-zA-Z0-9_-]+)")


def _referenced_gdoc_ids(root: Path) -> set[str]:
    """Walk all task docs and extract gdoc IDs referenced in
    internal-review sections."""
    refs: set[str] = set()
    tasks_root = root / "tasks"
    if not tasks_root.is_dir():
        return refs
    for person_dir in tasks_root.iterdir():
        if not person_dir.is_dir() or person_dir.name.startswith("_"):
            continue
        for task_doc in person_dir.glob("*.md"):
            try:
                txt = task_doc.read_text()
            except OSError:
                continue
            # Only count gdoc references that appear inside a sentinel-bounded
            # internal-review section
            for m in re.finditer(
                r"<!--\s*change-control:internal-review\s+begin.*?<!--\s*change-control:internal-review\s+end\s*-->",
                txt,
                re.DOTALL,
            ):
                block = m.group(0)
                for gm in _GDOC_ID_RE.finditer(block):
                    refs.add(gm.group(1))
    return refs


def main() -> int:
    try:
        root = _project_root()
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    state_dir = root / ".state" / "web-control"
    if not state_dir.is_dir():
        print("nothing to purge — .state/web-control/ does not exist")
        return 0

    referenced = _referenced_gdoc_ids(root)
    print(f"web-control purge-stale")
    print(f"  state dir:      {state_dir}")
    print(f"  referenced ids: {len(referenced)}")

    deleted: list[Path] = []
    kept: list[Path] = []
    for f in state_dir.iterdir():
        if not f.is_file():
            continue
        # File names: <gdoc-id>.last-sync.json or <gdoc-id>.last-push.txt
        # gdoc-id is everything before the first dot
        name = f.name
        gdoc_id = name.split(".", 1)[0]
        if gdoc_id in referenced:
            kept.append(f)
        else:
            deleted.append(f)

    for f in deleted:
        try:
            f.unlink()
        except OSError as exc:
            print(f"  ERROR removing {f.name}: {exc}", file=sys.stderr)

    print(f"  deleted: {len(deleted)} file(s)")
    for f in deleted[:20]:
        print(f"    - {f.name}")
    if len(deleted) > 20:
        print(f"    ... ({len(deleted) - 20} more)")
    print(f"  kept:    {len(kept)} file(s) (still referenced)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
