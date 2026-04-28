#!/usr/bin/env python3
"""Apply QMS titles from _scratch/104-qms-titles-draft.md into qms-manifest.md.

Reads the draft table (col1 = QMS-ID, col3 = Proposed Title), walks every
`<!-- QMS-DATA ... -->` block in `docs/project/dhf-manifest/qms-manifest.md`,
and inserts `title: "<Title>"` directly after each `id: "QMS-XXX"` line
inside the YAML records.

Idempotent: replaces existing `title:` lines; inserts if absent.

Run from repo root:
    python3 .claude/skills/dhf-manifest/scripts/apply-qms-titles.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
DRAFT = REPO_ROOT / "tasks/ben/_scratch/104-qms-titles-draft.md"
MANIFEST = REPO_ROOT / "docs/project/dhf-manifest/qms-manifest.md"

ROW_RE = re.compile(r"^\|\s*(QMS-[A-Z0-9-]+)\s*\|\s*([^|]*?)\s*\|\s*([^|]+?)\s*\|\s*$")


def load_titles() -> dict[str, str]:
    titles: dict[str, str] = {}
    for line in DRAFT.read_text(encoding="utf-8").splitlines():
        m = ROW_RE.match(line)
        if not m:
            continue
        qms_id = m.group(1).strip()
        title = m.group(3).strip()
        if not title or title.lower().startswith("proposed"):
            continue
        titles[qms_id] = title
    return titles


def apply(titles: dict[str, str]) -> tuple[int, set[str]]:
    src = MANIFEST.read_text(encoding="utf-8")
    lines = src.splitlines()
    touched: set[str] = set()

    # First pass: replace existing title: lines adjacent to id: lines
    i = 0
    while i < len(lines):
        m = re.match(r'^(\s*)-\s*id:\s*"(QMS-[A-Z0-9-]+)"\s*$', lines[i])
        if m:
            indent_dash = m.group(1)  # indent of `- id:`
            field_indent = indent_dash + "  "  # fields are 2 deeper
            qms_id = m.group(2)
            title = titles.get(qms_id)
            if title is not None and (i + 1) < len(lines) and re.match(
                r'^\s*title:\s*', lines[i + 1]
            ):
                lines[i + 1] = f'{field_indent}title: "{title}"'
                touched.add(qms_id)
        i += 1

    # Second pass: build output with inserts where absent
    out: list[str] = []
    i = 0
    while i < len(lines):
        out.append(lines[i])
        m = re.match(r'^(\s*)-\s*id:\s*"(QMS-[A-Z0-9-]+)"\s*$', lines[i])
        if m:
            indent_dash = m.group(1)
            field_indent = indent_dash + "  "
            qms_id = m.group(2)
            title = titles.get(qms_id)
            has_title_next = (i + 1) < len(lines) and re.match(
                r'^\s*title:\s*', lines[i + 1]
            )
            if title is not None and not has_title_next:
                out.append(f'{field_indent}title: "{title}"')
                touched.add(qms_id)
        i += 1

    new_text = "\n".join(out)
    if src.endswith("\n"):
        new_text += "\n"
    if new_text != src:
        MANIFEST.write_text(new_text, encoding="utf-8")
    return len(touched), touched


def main() -> int:
    if not DRAFT.exists():
        print(f"ERROR: draft not found: {DRAFT}", file=sys.stderr)
        return 1
    if not MANIFEST.exists():
        print(f"ERROR: manifest not found: {MANIFEST}", file=sys.stderr)
        return 1

    titles = load_titles()
    print(f"Loaded {len(titles)} titles from draft")

    written, touched = apply(titles)
    missing = sorted(set(titles) - touched)

    print(f"Titles applied: {written}/{len(titles)}")
    if missing:
        print(f"WARNING: {len(missing)} draft IDs not matched to any QMS-DATA record:")
        for x in missing[:20]:
            print(f"  - {x}")
        if len(missing) > 20:
            print(f"  ... and {len(missing) - 20} more")
    return 0


if __name__ == "__main__":
    sys.exit(main())
