#!/usr/bin/env python3
"""binary_coverage.py — find controlled binaries with no INDEXED markdown view.

The file-locator indexes markdown/YAML only (`corpus_includes`), so a
.docx/.doc/.pdf/.xlsx is invisible to semantic search UNLESS a markdown view of
it is indexed. This detector answers exactly "which binaries can the locator
NOT surface?" — it owns the *detection* half of the coverage loop.

It deliberately does NOT decide where a missing view should live or generate it
— that intelligence belongs to docflow. For each uncovered binary it emits a
`/docflow adopt "<binary>"` handoff line; docflow's adopt auto-locate sub-mode
then convention-detects the target and prompts when unsure.

A binary is COVERED when, restricted to the locator's INDEXED md set
(corpus_includes minus corpus_excludes):
  - a sibling md with the same stem sits in the same folder, OR
  - some indexed md links it via a frontmatter key
    (source_path / source_file / source_formal / target_formal).

Scope: binaries under `docs/` that are NOT in an excluded tree (per
`project.yml file_locator.corpus_excludes` — e.g. `_scratch`, `.staging`,
`formal/`, plus any project additions). Excluded trees are out of scope by
construction: the locator isn't expected to surface them, so they need no view.
The count of skipped/excluded binaries is reported (no silent caps).

Reuses the locator's own config + glob semantics from `common.py` (same skill).
Project-agnostic: no project/device/team names.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from common import load_config, walk_corpus, _matches_any

BINARY_EXTS = {".docx", ".doc", ".pdf", ".xlsx", ".xls", ".pptx", ".ppt"}
LINK_KEYS = ("source_path", "source_file", "source_formal", "target_formal")


def _read(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def scan(project_root: Path) -> dict:
    cfg = load_config(project_root)
    root = cfg.project_root

    # ---- the INDEXED md set (what the locator can actually surface) --------
    walk = walk_corpus(cfg)  # non-audit: only include-glob matches, minus excludes
    indexed_md = [root / rel for rel in walk.included if rel.suffix == ".md"]

    claimed_basenames: set[str] = set()
    md_stems_by_dir: dict[Path, set[str]] = {}
    for md in indexed_md:
        md_stems_by_dir.setdefault(md.parent, set()).add(md.stem)
        txt = _read(md)
        for key in LINK_KEYS:
            for m in re.finditer(rf'^\s*{key}\s*:\s*["\']?([^"\'\n]+)', txt, re.MULTILINE):
                claimed_basenames.add(Path(m.group(1).strip()).name)

    # ---- enumerate candidate binaries under docs/ -------------------------
    docs = root / "docs"
    covered: list[str] = []
    uncovered: list[str] = []
    skipped_excluded = 0
    if docs.is_dir():
        for f in sorted(docs.rglob("*")):
            if not f.is_file() or f.suffix.lower() not in BINARY_EXTS:
                continue
            rel = f.relative_to(root)
            rel_str = rel.as_posix()
            if _matches_any(rel_str, cfg.excludes):
                skipped_excluded += 1
                continue
            if f.name in claimed_basenames or f.stem in md_stems_by_dir.get(f.parent, set()):
                covered.append(rel_str)
            else:
                uncovered.append(rel_str)

    return {
        "scanned": len(covered) + len(uncovered),
        "covered": covered,
        "uncovered": uncovered,
        "skipped_excluded": skipped_excluded,
    }


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=".", help="project root (default: cwd)")
    ap.add_argument("--json", action="store_true", help="emit JSON instead of a report")
    args = ap.parse_args()
    r = scan(Path(args.root))

    if args.json:
        print(json.dumps(r, indent=2))
        return 1 if r["uncovered"] else 0

    print("Binary coverage — controlled binaries vs the locator's indexed md")
    print(f"  scanned (in-scope):   {r['scanned']}")
    print(f"  covered:              {len(r['covered'])}")
    print(f"  UNCOVERED:            {len(r['uncovered'])}")
    print(f"  skipped (excluded trees, out of scope): {r['skipped_excluded']}")
    if r["uncovered"]:
        print("\nUncovered binaries (invisible to semantic search) — hand off to docflow:")
        for b in r["uncovered"]:
            print(f"  • {b}")
            print(f'      → /docflow adopt "{b}"')
        print("\n(docflow auto-locate convention-detects the md target and prompts when unsure;")
        print(" it may report the binary already has a view to LINK rather than generate.)")
    else:
        print("\n✓ Every in-scope binary has an indexed markdown view.")
    return 1 if r["uncovered"] else 0


if __name__ == "__main__":
    sys.exit(main())
