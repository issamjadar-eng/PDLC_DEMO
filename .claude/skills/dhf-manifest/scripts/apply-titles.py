#!/usr/bin/env python3
"""Apply titles from tasks/ben/_scratch/104-titles-draft.md into Tier 1 source MD YAML blocks.

Reads the draft table (col1 = OBL-ID, col3 = Proposed Title), walks every Tier 1
source MD under data/{fda-guidance,standards,industry-frameworks}/, and inserts
`title: "<Title>"` directly after each `id: <OBL-ID>` line inside the YAML block.

Idempotent: if a `title:` line is already present for a record, it is replaced
with the draft value (not duplicated).

Run from repo root:
    python3 .claude/skills/dhf-manifest/scripts/apply-titles.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
DRAFT = REPO_ROOT / "tasks/ben/_scratch/104-titles-draft.md"
DATA_DIRS = [
    REPO_ROOT / ".claude/skills/dhf-manifest/data/fda-guidance",
    REPO_ROOT / ".claude/skills/dhf-manifest/data/standards",
    REPO_ROOT / ".claude/skills/dhf-manifest/data/industry-frameworks",
]

ROW_RE = re.compile(r"^\|\s*(OBL-[A-Z0-9-]+)\s*\|\s*([^|]*?)\s*\|\s*([^|]+?)\s*\|\s*$")


def load_titles() -> dict[str, str]:
    titles: dict[str, str] = {}
    for line in DRAFT.read_text(encoding="utf-8").splitlines():
        m = ROW_RE.match(line)
        if not m:
            continue
        obl_id = m.group(1).strip()
        title = m.group(3).strip()
        if not title or title.lower().startswith("proposed"):
            continue
        titles[obl_id] = title
    return titles


def apply_to_file(path: Path, titles: dict[str, str]) -> int:
    """Return count of title lines written/updated in this file."""
    src = path.read_text(encoding="utf-8")
    lines = src.splitlines()
    written = 0
    i = 0
    # First pass: replace existing `title:` lines in-place on the lines array.
    while i < len(lines):
        m = re.match(r"^(\s*)id:\s*(OBL-[A-Z0-9-]+)\s*$", lines[i])
        if m:
            indent = m.group(1)
            obl_id = m.group(2)
            title = titles.get(obl_id)
            if title is not None and (i + 1) < len(lines) and re.match(
                r"^\s*title:\s*", lines[i + 1]
            ):
                lines[i + 1] = f'{indent}title: "{title}"'
                written += 1
        i += 1

    # Second pass: build output, inserting `title:` lines where absent.
    out: list[str] = []
    i = 0
    while i < len(lines):
        out.append(lines[i])
        m = re.match(r"^(\s*)id:\s*(OBL-[A-Z0-9-]+)\s*$", lines[i])
        if m:
            indent = m.group(1)
            obl_id = m.group(2)
            title = titles.get(obl_id)
            already = (i + 1) < len(lines) and re.match(r"^\s*title:\s*", lines[i + 1])
            if title is not None and not already:
                out.append(f'{indent}title: "{title}"')
                written += 1
        i += 1

    new_text = "\n".join(out)
    if src.endswith("\n"):
        new_text += "\n"
    if new_text != src:
        path.write_text(new_text, encoding="utf-8")
    return written


def main() -> int:
    if not DRAFT.exists():
        print(f"ERROR: draft not found: {DRAFT}", file=sys.stderr)
        return 1

    titles = load_titles()
    print(f"Loaded {len(titles)} titles from draft")

    total_written = 0
    files_changed = 0
    ids_applied: set[str] = set()

    for data_dir in DATA_DIRS:
        if not data_dir.exists():
            continue
        for md in sorted(data_dir.glob("*.md")):
            if md.name == "README.md":
                continue
            before = md.read_text(encoding="utf-8")
            written = apply_to_file(md, titles)
            after = md.read_text(encoding="utf-8")
            if before != after:
                files_changed += 1
                for obl_id in re.findall(r"id:\s*(OBL-[A-Z0-9-]+)", after):
                    if obl_id in titles:
                        ids_applied.add(obl_id)
                print(f"  {md.relative_to(REPO_ROOT)}: {written} title lines")
            total_written += written

    missing = sorted(set(titles) - ids_applied)
    print(f"\nFiles changed: {files_changed}")
    print(f"Title lines written/updated: {total_written}")
    print(f"Distinct OBL-IDs touched: {len(ids_applied)}/{len(titles)}")
    if missing:
        print(f"WARNING: {len(missing)} draft IDs not matched to any source MD:")
        for x in missing:
            print(f"  - {x}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
