#!/usr/bin/env python3
"""
/tracker classify-folders — context bundle builder.

Walks every registered taxonomy in the project, finds folders the Tier 1
heuristic flagged as uncertain (low confidence in `pending:` or per-file
mappings emitted because aggregation couldn't be decided), and emits one
YAML context bundle per uncertain folder. The orchestrator (Claude) reads
these bundles and dispatches one folder-classifier agent per bundle in
parallel.

Usage:
    python3 build_classify_context.py --project-dir <dir> --all
    python3 build_classify_context.py --project-dir <dir> --taxonomy <id>
    python3 build_classify_context.py --project-dir <dir> --folder <rel> --in <taxonomy-id>
    python3 build_classify_context.py --project-dir <dir> --all --out /tmp/classify-bundles/

When --out is given: one bundle written per folder as
    <out>/<safe-folder-id>.yaml
plus a manifest.json listing each (folder, bundle_path, output_path)
the orchestrator should iterate.

When --out omitted: bundles emitted to stdout as a single YAML stream.

Deterministic and side-effect-light: reads only; never mutates taxonomies.
The merger script `merge_classify_results.py` applies agent verdicts back
to the taxonomy file after agents complete.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from taxonomy import (  # noqa: E402
    DEFAULT_VOCABULARY, list_registered_taxonomies, load_yaml,
    scan_root, classify_folder,
)


FRONTMATTER_LINES = 30  # how many lines to sample per file


def _safe_id(folder_rel: str) -> str:
    """Filesystem-safe folder identifier for bundle filenames."""
    return re.sub(r"[^a-zA-Z0-9._-]+", "_", folder_rel.strip("/")) or "root"


def _read_head(path: Path, n_lines: int = FRONTMATTER_LINES) -> str:
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as f:
            return "".join(next(f) for _ in range(n_lines))
    except StopIteration:
        try:
            return path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return ""
    except Exception:
        return ""


def _read_readme(folder: Path) -> str:
    for name in ("README.md", "readme.md"):
        candidate = folder / name
        if candidate.is_file():
            return _read_head(candidate, n_lines=80)
    return ""


def _load_dhf_manifest(project_dir: Path) -> dict | None:
    """Load the project's dhf-manifest catalog (Tier 4 obligations) if
    present. Used by the bundle builder to attach role-specific obligations
    so the Tier 2 agent has HCLS catalog grounding for its judgment."""
    manifest_dir = project_dir / "docs/project/dhf-manifest"
    if not manifest_dir.is_dir():
        return None
    for f in manifest_dir.glob("*-dhf-manifest.json"):
        try:
            return json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
    return None


def _obligations_for_role_and_dhf(
    manifest: dict | None, dhf_leaf: str, canonical_role: str
) -> list[dict]:
    """Return the catalog obligations for (DHF, canonical_role). Each
    obligation is the agent's grounding for whether the folder's files
    represent ONE regulated artifact (aggregate) or DISTINCT regulated
    artifacts (independent). Conservative: returns empty list when the
    catalog is missing/unreadable so the agent falls back to its rubric
    table."""
    if not manifest:
        return []
    dhf_obls = (manifest.get("dhf_manifest") or {}).get(dhf_leaf) or []
    out = []
    for o in dhf_obls:
        if not isinstance(o, dict):
            continue
        # Role match heuristic: catalog topic/artifact_type may use hyphens
        # vs underscores vs spaces (e.g. "post-market" vs "postmarket").
        # Normalize by stripping non-alphanumerics so role names match
        # across formatting conventions.
        def _norm(s: str) -> str:
            return "".join(c for c in s.lower() if c.isalnum())
        topic_n = _norm(o.get("topic") or "")
        atype_n = _norm(o.get("artifact_type") or "")
        role_n = _norm(canonical_role)
        if role_n and (role_n in topic_n or role_n in atype_n
                       or topic_n in role_n):
            out.append({
                "id": o.get("id"),
                "title": o.get("title"),
                "topic": o.get("topic"),
                "artifact_type": o.get("artifact_type"),
                "applies_to": o.get("applies_to") or [],
                "reg_source": (o.get("reg_source") or {}).get("citation"),
            })
    return out


def _file_meta(folder_abs: Path, file_rel: str) -> dict:
    abs_path = folder_abs / Path(file_rel).name
    try:
        size = abs_path.stat().st_size
    except OSError:
        size = None
    return {
        "name": Path(file_rel).name,
        "rel_path": file_rel,
        "size_bytes": size,
        "head": _read_head(abs_path),
    }


def _roots_for_taxonomy(project_dir: Path, entry: dict) -> list[Path]:
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
        roots.append(entry["file"].parent)
    return roots


def _uncertain_folders_for_taxonomy(
    project_dir: Path, entry: dict, manifest: dict | None = None
) -> list[dict]:
    """Re-scan the taxonomy's roots, run Tier 1 classifier, return folders
    whose verdict was `uncertain`. Returns [{folder, file_paths, roles, …}]"""
    tax_file: Path = entry["file"]
    if not tax_file.is_file():
        return []
    taxonomy = load_yaml(tax_file)
    discovery_root = taxonomy.get("discovery_root", ".") or "."

    # Read existing aggregate folder mappings to skip them
    existing_aggregates: set[str] = set()
    for key, mapping in (taxonomy.get("mappings") or {}).items():
        if mapping.get("aggregate") == "folder":
            existing_aggregates.add(key.rstrip("/"))

    out = []
    for root in _roots_for_taxonomy(project_dir, entry):
        scan = scan_root(root, discovery_root=discovery_root, project_dir=project_dir)
        # Group high_confidence files by folder; run Tier 1 verdict per folder
        by_folder: dict[str, list[str]] = {}
        for path in scan["high_confidence"].keys():
            folder = "/".join(path.split("/")[:-1]) or "."
            by_folder.setdefault(folder, []).append(path)
        for folder, files in by_folder.items():
            if folder in existing_aggregates:
                continue
            roles = {p: scan["high_confidence"][p] for p in files}
            verdict = classify_folder(folder, files, roles)
            # Tier 1 (v15+ conservative posture) always returns
            # kind=independent. Tier 2 runs on folders flagged with the
            # aggregation_candidate signal — those are the folders worth
            # the LLM call. Skip everything else.
            if not verdict.get("aggregation_candidate"):
                continue
            walk_root = (root / discovery_root).resolve()
            folder_abs = (walk_root / folder).resolve()
            # Catalog grounding: attach this folder's role(s) to the agent's
            # context so it can reason against ACTUAL regulated obligations,
            # not only the rubric table baked into agents/folder-classifier.md.
            applicable_dhfs = list(entry.get("applies_to_dhfs") or [])
            roles_in_folder = sorted({r for r in roles.values() if r})
            catalog_obligations: dict[str, list] = {}
            for dhf_leaf in applicable_dhfs:
                for role in roles_in_folder:
                    obls = _obligations_for_role_and_dhf(manifest, dhf_leaf, role)
                    if obls:
                        catalog_obligations.setdefault(f"{dhf_leaf}::{role}", []).extend(obls)
            out.append({
                "folder": folder,
                "folder_abs": str(folder_abs),
                "files_meta": [
                    _file_meta(folder_abs, f)
                    for f in sorted(files)
                ],
                "roles": roles,
                "tier1_verdict": verdict,
                "readme": _read_readme(folder_abs),
                "taxonomy_id": entry["id"],
                "taxonomy_file": str(tax_file.relative_to(project_dir)),
                # HCLS catalog grounding (Tier 4 obligations from
                # /dhf-manifest). When non-empty: agent should use these
                # to decide whether the files satisfy ONE obligation
                # (aggregate) or DISTINCT obligations (independent).
                "catalog_obligations": catalog_obligations,
                "catalog_obligation_count": sum(len(v) for v in catalog_obligations.values()),
            })
    return out


def _bundle_to_yaml(bundle: dict) -> str:
    """Render the bundle as YAML-ish text (deterministic, human-readable)."""
    import yaml as _yaml
    return _yaml.safe_dump(bundle, sort_keys=False, default_flow_style=False,
                           width=100, allow_unicode=True)


def main() -> int:
    ap = argparse.ArgumentParser(description="/tracker classify-folders bundle builder")
    ap.add_argument("--project-dir", required=True)
    ap.add_argument("--all", action="store_true",
                    help="Build bundles for every uncertain folder across all taxonomies")
    ap.add_argument("--taxonomy",
                    help="Limit to one taxonomy id from project.yml.taxonomies[]")
    ap.add_argument("--folder",
                    help="Build bundle for one folder (requires --in)")
    ap.add_argument("--in", dest="taxonomy_in",
                    help="Taxonomy id when using --folder")
    ap.add_argument("--out", help="Directory to write bundles + manifest.json")
    ap.add_argument("--dry-run", action="store_true",
                    help="Print uncertain folder count + paths; no bundles")
    args = ap.parse_args()

    project_dir = Path(args.project_dir).resolve()
    registry = list_registered_taxonomies(project_dir)
    if not registry:
        print("No taxonomies registered in project.yml.taxonomies[]", file=sys.stderr)
        return 1

    if args.taxonomy:
        registry = [t for t in registry if t["id"] == args.taxonomy]
        if not registry:
            print(f"No taxonomy id={args.taxonomy} in registry", file=sys.stderr)
            return 2

    manifest = _load_dhf_manifest(project_dir)

    bundles = []
    for entry in registry:
        bundles.extend(_uncertain_folders_for_taxonomy(project_dir, entry, manifest))

    if args.folder:
        bundles = [b for b in bundles if b["folder"] == args.folder]

    if args.dry_run:
        print(f"Uncertain folders: {len(bundles)}")
        for b in bundles:
            print(f"  - [{b['taxonomy_id']}] {b['folder']} ({len(b['files_meta'])} files)")
        return 0

    if args.out:
        out_dir = Path(args.out).resolve()
        out_dir.mkdir(parents=True, exist_ok=True)
        manifest = {
            "schema_version": "0.1",
            "generated_by": "/tracker classify-folders bundle builder",
            "bundles": [],
        }
        for b in bundles:
            sid = f"{_safe_id(b['taxonomy_id'])}__{_safe_id(b['folder'])}"
            bundle_path = out_dir / f"{sid}.yaml"
            output_path = out_dir / f"{sid}.verdict.json"
            b["bundle_id"] = sid
            b["output_path"] = str(output_path)
            b["allowed_kinds"] = ["aggregate", "independent", "primary-with-supplements"]
            b["canonical_role_vocabulary"] = list(DEFAULT_VOCABULARY)
            bundle_path.write_text(_bundle_to_yaml(b), encoding="utf-8")
            manifest["bundles"].append({
                "bundle_id": sid,
                "taxonomy_id": b["taxonomy_id"],
                "taxonomy_file": b["taxonomy_file"],
                "folder": b["folder"],
                "bundle_path": str(bundle_path),
                "output_path": str(output_path),
            })
        (out_dir / "manifest.json").write_text(
            json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        print(f"Wrote {len(bundles)} bundle(s) + manifest.json to {out_dir}")
    else:
        # Stream all bundles to stdout as one YAML doc per bundle
        for b in bundles:
            print("---")
            print(_bundle_to_yaml(b))
        if not bundles:
            print("# No uncertain folders.", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
