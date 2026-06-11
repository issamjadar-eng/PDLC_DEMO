#!/usr/bin/env python3
"""dhf-manifest audit-coverage — taxonomy mapping-completeness audit.

The INVERSE of `discovery-index.py`. Discovery walks **role → folder** ("does each
*expected* canonical role resolve to a folder?") and only one level deep
(`<discovery_root>/<slug>/`). This audit walks **folder → mapping** ("does every
document-node folder in the external/Confluence-mirror tree have a `mappings[<slug>]`
entry in the DHF's `.taxonomy.yml`?") — including **nested** sub-doctypes, which
discovery never visits.

A "document node" is a folder that holds a version file (`v*.md`) or `index.md`
(or a flat `<slug>.md` directly under the discovery root). Version-container dirs
(`v1.0.0`, `v.2.0.0`, …) and asset dirs (`images/`, `assets/`) are not doctypes
and are skipped.

Runs per external DHF (`dhfs[]` entries that declare `taxonomy_path`); internal
(project-waterfall) DHFs are skipped — they have no taxonomy rosetta to be
incomplete against.

Exit code: 0 = full coverage; 1 = at least one unmapped doctype (CI-friendly).
Project-agnostic — reads `project.yml` + each DHF's `.taxonomy.yml`; no hard-coded
project names, slugs, or paths.

Usage:
    python3 audit-coverage.py [--repo <project-root>] [--json]
"""
import argparse
import json
import re
import sys
from pathlib import Path

import yaml

VERSION_DIR = re.compile(r"^v\.?\d")          # v1.0.0 / v.1.0.0 / v.2.0.0 — version container, not a doctype
SKIP_DIRS = {"images", "assets"}
SKIP_STEMS = {"index"}                         # the product-overview landing page, not a doctype


def _load_yaml(path: Path):
    try:
        return yaml.safe_load(path.read_text())
    except Exception:
        return None


def _is_document_node(d: Path) -> bool:
    """A doctype node holds a version file (v*.md) or index.md."""
    try:
        files = [f.name for f in d.iterdir() if f.is_file()]
    except OSError:
        return False
    return any(f.startswith("v") and f.endswith(".md") for f in files) or "index.md" in files


def audit_dhf(dhf: dict, project_root: Path) -> dict:
    leaf = dhf.get("leaf") or Path(dhf.get("path", "")).name
    rel_path = dhf.get("path")
    tax_path = dhf.get("taxonomy_path")
    if not rel_path:
        return {"leaf": leaf, "skipped": "no path"}
    if not tax_path:
        return {"leaf": leaf, "skipped": "internal DHF (no taxonomy_path)"}
    taxonomy = _load_yaml(project_root / tax_path)
    if not taxonomy:
        return {"leaf": leaf, "skipped": f"taxonomy unreadable: {tax_path}"}
    mapped = set((taxonomy.get("mappings") or {}).keys())
    discovery_root = taxonomy.get("discovery_root", "")
    base = (project_root / rel_path / discovery_root) if discovery_root else (project_root / rel_path)
    if not base.is_dir():
        return {"leaf": leaf, "skipped": f"discovery root not found: {base}"}

    nodes = 0
    unmapped = []
    # nested folder doctypes (any depth)
    for d in sorted(p for p in base.rglob("*") if p.is_dir()):
        if d.name in SKIP_DIRS or d.name.startswith(".") or VERSION_DIR.match(d.name):
            continue
        if not _is_document_node(d):
            continue
        nodes += 1
        if d.name not in mapped:
            unmapped.append(str(d.relative_to(project_root)))
    # flat-file doctypes directly under the discovery root (<slug>.md)
    for f in sorted(base.glob("*.md")):
        if f.stem in SKIP_STEMS:
            continue
        nodes += 1
        if f.stem not in mapped and f.name not in mapped:
            unmapped.append(str(f.relative_to(project_root)))
    return {"leaf": leaf, "nodes": nodes, "unmapped": sorted(unmapped)}


def main() -> int:
    ap = argparse.ArgumentParser(description="dhf-manifest taxonomy mapping-completeness audit (folder → mapping).")
    ap.add_argument("--repo", default=".", help="Project root (default: CWD)")
    ap.add_argument("--json", action="store_true", help="Emit JSON instead of text")
    args = ap.parse_args()

    root = Path(args.repo).resolve()
    proj = _load_yaml(root / "project.yml") or {}
    dhfs = proj.get("dhfs") or []
    results = [audit_dhf(d, root) for d in dhfs]
    total = sum(len(r.get("unmapped", [])) for r in results)

    if args.json:
        print(json.dumps({"total_unmapped": total, "results": results}, indent=2))
    else:
        print("dhf-manifest mapping-completeness audit — every external doctype node must have a .taxonomy.yml mapping\n")
        for r in results:
            if "skipped" in r:
                print(f"  – {r['leaf']}: skipped ({r['skipped']})")
                continue
            n = len(r["unmapped"])
            print(f"  {'✓' if n == 0 else '✗'} {r['leaf']}: {r['nodes']} doctype nodes, {n} UNMAPPED")
            for u in r["unmapped"]:
                print(f"        ✗ {u}")
        print(f"\n  TOTAL unmapped doctype nodes: {total}")
        if total:
            print("  → FAIL: add a `mappings[<slug>]` entry (canonical_role + governing_qms) to the")
            print("    DHF's .taxonomy.yml for each path above. See the taxonomy header for the schema.")
        else:
            print("  → PASS: full taxonomy mapping coverage across all external DHFs.")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
