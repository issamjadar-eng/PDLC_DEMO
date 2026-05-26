#!/usr/bin/env python3
"""init_taxonomy.py — cold-start scan + write a new .taxonomy.yml.

Usage:
  init_taxonomy.py --project-dir <dir> --dhf <leaf>
  init_taxonomy.py --project-dir <dir> --path <relative-folder>
  init_taxonomy.py --project-dir <dir> --all-dhfs
  init_taxonomy.py --project-dir <dir> --shared <file> --for <leaf1,leaf2,...>

Behavior:
  - Walks the target root, classifies .md files via heuristics, writes a
    starter .taxonomy.yml at <root>/.taxonomy.yml (or at the path given by
    --shared).
  - Adds an entry to project.yml.taxonomies[] registering the new file.
  - Skips DHFs that already resolve to a taxonomy (legacy taxonomy_path or
    pre-existing registry entry) when run with --all-dhfs.
  - Prints a one-line summary per scaffolded taxonomy and a final tally.

This action does NOT auto-render or auto-generate; it produces the schema
artifact and the registry entry so subsequent /tracker generate runs use it.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from taxonomy import (
    SCHEMA_VERSION, build_mappings_from_scan, build_pending_block,
    dump_yaml, load_yaml, resolve_taxonomy, scan_root,
    add_taxonomy_to_project_yml,
)


def _scaffold_taxonomy(scan: dict, *, source_authority: str) -> dict:
    mappings, candidates = build_mappings_from_scan(scan)
    out = {
        "schema_version": SCHEMA_VERSION,
        "source_authority": source_authority,
        "description": (
            "Auto-scaffolded by /tracker init-taxonomy. Review the mappings "
            "below — files that the heuristic scanner couldn't classify with "
            "high confidence are listed under `pending:` for manual triage. "
            "Folders matching the numbered-series pattern that may warrant "
            "aggregation are flagged in `aggregation_candidates:` — Tier 1 "
            "never auto-aggregates; run /tracker classify-folders for an LLM "
            "verdict, or hand-edit the mapping to a folder-aggregate."
        ),
        "discovery_root": scan["discovery_root"],
        "mappings": mappings,
        "pending": build_pending_block(scan),
    }
    if candidates:
        out["aggregation_candidates"] = candidates
    return out


def init_for_dhf(project_dir: Path, leaf: str) -> tuple[Path, dict, dict]:
    project_yml = project_dir / "project.yml"
    pyl = load_yaml(project_yml)
    dhf = next((d for d in (pyl.get("dhfs") or []) if d.get("leaf") == leaf), None)
    if not dhf:
        raise ValueError(f"DHF leaf not found in project.yml: {leaf}")
    root = project_dir / dhf["path"]
    if not root.is_dir():
        raise ValueError(f"DHF root not found on disk: {root}")
    target = root / ".taxonomy.yml"
    scan = scan_root(root, discovery_root=".", project_dir=project_dir)
    taxonomy = _scaffold_taxonomy(scan, source_authority="project-layout")
    return target, taxonomy, scan


def init_for_path(project_dir: Path, rel_path: str) -> tuple[Path, dict, dict]:
    root = project_dir / rel_path
    if not root.is_dir():
        raise ValueError(f"Path not a directory: {root}")
    target = root / ".taxonomy.yml"
    scan = scan_root(root, discovery_root=".", project_dir=project_dir)
    taxonomy = _scaffold_taxonomy(scan, source_authority="project-layout")
    return target, taxonomy, scan


def main() -> int:
    ap = argparse.ArgumentParser(description="/tracker init-taxonomy")
    ap.add_argument("--project-dir", required=True, help="Project root")
    ap.add_argument("--dhf", help="DHF leaf to init (from project.yml dhfs[])")
    ap.add_argument("--path", help="Folder path to init (project-root-relative)")
    ap.add_argument("--all-dhfs", action="store_true",
                    help="Init for every DHF in project.yml that doesn't "
                         "already resolve to a taxonomy")
    ap.add_argument("--force", action="store_true",
                    help="Overwrite existing .taxonomy.yml at target path")
    ap.add_argument("--no-register", action="store_true",
                    help="Skip adding entry to project.yml.taxonomies[]")
    args = ap.parse_args()

    project_dir = Path(args.project_dir).resolve()
    targets: list[tuple[str, str, str]] = []  # (kind, identifier, label)

    if args.all_dhfs:
        pyl = load_yaml(project_dir / "project.yml")
        for d in (pyl.get("dhfs") or []):
            leaf = d.get("leaf")
            existing = resolve_taxonomy(project_dir, dhf_leaf=leaf)
            if existing is not None:
                print(f"  [skip] {leaf}: already resolves to {existing.relative_to(project_dir)}")
                continue
            targets.append(("dhf", leaf, leaf))
    elif args.dhf:
        targets.append(("dhf", args.dhf, args.dhf))
    elif args.path:
        targets.append(("path", args.path, args.path))
    else:
        ap.error("provide --dhf, --path, or --all-dhfs")

    written = 0
    skipped = 0
    for kind, ident, label in targets:
        try:
            if kind == "dhf":
                target, taxonomy, scan = init_for_dhf(project_dir, ident)
            else:
                target, taxonomy, scan = init_for_path(project_dir, ident)
        except ValueError as e:
            print(f"  [error] {label}: {e}", file=sys.stderr)
            continue

        if target.exists() and not args.force:
            print(f"  [skip] {label}: {target.relative_to(project_dir)} already exists "
                  f"(pass --force to overwrite)")
            skipped += 1
            continue

        dump_yaml(taxonomy, target)
        n_mapped = len(taxonomy.get("mappings") or {})
        n_pending = len(taxonomy.get("pending") or [])
        print(f"  [wrote] {label}: {target.relative_to(project_dir)} "
              f"({n_mapped} mapped, {n_pending} pending, "
              f"{len(scan['all_files'])} files scanned)")
        written += 1

        if not args.no_register:
            file_rel = str(target.relative_to(project_dir))
            tax_id = label if kind == "dhf" else label.rstrip("/").split("/")[-1]
            kw = {
                "applies_to_dhfs": [ident] if kind == "dhf" else None,
                "applies_to_paths": [ident] if kind == "path" else None,
            }
            modified = add_taxonomy_to_project_yml(
                project_dir,
                taxonomy_id=tax_id,
                file_rel=file_rel,
                **kw,
            )
            if modified:
                print(f"           → registered in project.yml.taxonomies[] as id={tax_id}")

    print(f"\nSummary: {written} written, {skipped} skipped, {len(targets)} target(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
