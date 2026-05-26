#!/usr/bin/env python3
"""reconcile_taxonomy.py — diff disk vs taxonomy; refresh pending/broken_refs.

Usage:
  reconcile_taxonomy.py --project-dir <dir> --id <taxonomy-id>
  reconcile_taxonomy.py --project-dir <dir> --file <path-to-.taxonomy.yml>
  reconcile_taxonomy.py --project-dir <dir> --dhf <leaf>
  reconcile_taxonomy.py --project-dir <dir> --all
  reconcile_taxonomy.py --project-dir <dir> --report-only --all   # don't write

Behavior:
  Re-scans the root(s) the taxonomy serves, compares against existing
  mappings/pending/excluded, updates pending: (newly discovered files) and
  broken_refs: (mapped files no longer on disk). Mappings are NOT mutated;
  the user authors classification.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from taxonomy import (
    dump_yaml, list_registered_taxonomies, load_yaml, reconcile, scan_root,
)


def _resolve_target_files(project_dir: Path, args) -> list[dict]:
    """Return list of {file: Path, applies_to_dhfs, applies_to_paths} for
    each taxonomy this run should reconcile."""
    registry = list_registered_taxonomies(project_dir)
    reg_by_file = {str(t["file"]): t for t in registry}

    if args.all:
        return registry

    if args.id:
        match = next((t for t in registry if t["id"] == args.id), None)
        if not match:
            print(f"error: no taxonomy with id={args.id} in project.yml", file=sys.stderr)
            sys.exit(2)
        return [match]

    if args.dhf:
        match = next(
            (t for t in registry if args.dhf in t["applies_to_dhfs"]), None)
        if not match:
            print(f"error: no taxonomy registered for DHF leaf={args.dhf}", file=sys.stderr)
            sys.exit(2)
        return [match]

    if args.file:
        path = (project_dir / args.file).resolve()
        if str(path) in reg_by_file:
            return [reg_by_file[str(path)]]
        # File specified but not in registry — reconcile it standalone (no
        # registry context, so we walk its containing folder as the root).
        return [{
            "id": path.stem or "ad-hoc",
            "file": path,
            "applies_to_dhfs": [],
            "applies_to_paths": [str(path.parent.relative_to(project_dir))],
            "source": "ad-hoc",
        }]

    print("error: provide --id, --dhf, --file, or --all", file=sys.stderr)
    sys.exit(2)


def _roots_for_taxonomy(project_dir: Path, entry: dict) -> list[Path]:
    """Resolve the actual filesystem roots a taxonomy applies to."""
    pyl = load_yaml(project_dir / "project.yml")
    dhfs_by_leaf = {d.get("leaf"): d for d in (pyl.get("dhfs") or [])}

    roots: list[Path] = []
    for leaf in entry.get("applies_to_dhfs") or []:
        d = dhfs_by_leaf.get(leaf)
        if d:
            roots.append(project_dir / d["path"])
    for p in entry.get("applies_to_paths") or []:
        roots.append(project_dir / p)
    if not roots:
        # Fall back to the taxonomy file's parent
        roots.append(entry["file"].parent)
    return roots


def main() -> int:
    ap = argparse.ArgumentParser(description="/tracker reconcile-taxonomy")
    ap.add_argument("--project-dir", required=True)
    ap.add_argument("--id", help="Taxonomy id from project.yml.taxonomies[]")
    ap.add_argument("--dhf", help="Reconcile the taxonomy serving this DHF leaf")
    ap.add_argument("--file", help="Path to a .taxonomy.yml (project-relative)")
    ap.add_argument("--all", action="store_true",
                    help="Reconcile every registered taxonomy")
    ap.add_argument("--report-only", action="store_true",
                    help="Print report without writing changes")
    args = ap.parse_args()

    project_dir = Path(args.project_dir).resolve()
    targets = _resolve_target_files(project_dir, args)

    overall_added = 0
    overall_broken = 0
    overall_still = 0

    for entry in targets:
        tax_file: Path = entry["file"]
        if not tax_file.is_file():
            print(f"  [skip] {entry['id']}: {tax_file} not on disk")
            continue
        taxonomy = load_yaml(tax_file)
        roots = _roots_for_taxonomy(project_dir, entry)
        if not roots:
            print(f"  [skip] {entry['id']}: no roots resolved")
            continue

        # Merge scans across all roots this taxonomy serves
        merged = {"high_confidence": {}, "pending": [], "all_files": [],
                  "discovery_root": taxonomy.get("discovery_root", ".")}
        for root in roots:
            scan = scan_root(
                root,
                discovery_root=taxonomy.get("discovery_root", "."),
                project_dir=project_dir,
            )
            merged["all_files"].extend(scan["all_files"])
            merged["pending"].extend(scan["pending"])

        result = reconcile(taxonomy, merged)
        report = result["report"]

        added = report["added_to_pending"]
        broken = report["broken_refs"]
        still = report["still_pending"]

        overall_added += len(added)
        overall_broken += len(broken)
        overall_still += len(still)

        print(f"  [{entry['id']}]  mapped={report['mapped_count']} "
              f"on_disk={report['on_disk_count']} "
              f"+pending={len(added)} still_pending={len(still)} "
              f"broken={len(broken)}")
        if added:
            print("    new pending:")
            for p in added[:8]:
                print(f"      + {p}")
            if len(added) > 8:
                print(f"      … {len(added) - 8} more")
        if broken:
            print("    broken refs:")
            for p in broken[:8]:
                print(f"      ! {p}")
            if len(broken) > 8:
                print(f"      … {len(broken) - 8} more")

        if not args.report_only:
            dump_yaml(result["taxonomy"], tax_file)

    if args.report_only:
        print(f"\nReport-only: {overall_added} new pending, "
              f"{overall_broken} broken refs, {overall_still} still pending. "
              f"No files written.")
    else:
        print(f"\nReconciled {len(targets)} taxonomy file(s). "
              f"{overall_added} new pending entries, {overall_broken} broken refs.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
