#!/usr/bin/env python3
"""
/tracker assess-phases — context bundle builder.

Walks every registered taxonomy, groups taxonomy entries by canonical_role,
emits one YAML context bundle per role-batch. The orchestrator (Claude)
dispatches one regulatory-affairs agent per bundle in parallel; each agent
returns a single combined JSON containing per-file phase_map + scope + help
text + per-batch gap list.

Why batch by role: one regulatory framework per agent call (ISO 14971 for
risk-management, IEC 62304 for vnv, IEC 81001-5-1 for cybersecurity, etc.)
minimizes context-switching cost in the agent's reasoning. Files within a
batch share applicable catalog obligations so the agent reasons about
sibling deliverables holistically.

Per-batch budget: ~8-10K shared context + ~500-1K per file + ~700 token
output per file. Comfortable up to ~10 files per batch; auto-splits when
a role has more.

Usage:
    python3 build_phase_map_context.py --project-dir <dir> --all
    python3 build_phase_map_context.py --project-dir <dir> --role risk-management
    python3 build_phase_map_context.py --project-dir <dir> --all --out /tmp/phase-map-bundles/
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from taxonomy import (  # noqa: E402
    list_registered_taxonomies, load_yaml,
)


MAX_BATCH_SIZE = 10  # files per agent call (auto-split larger roles)


def _safe_id(s: str) -> str:
    return re.sub(r"[^a-zA-Z0-9._-]+", "_", s.strip("/")) or "root"


def _read_head(path: Path, n_lines: int = 30) -> str:
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


def _load_dhf_manifest(project_dir: Path) -> dict | None:
    manifest_dir = project_dir / "docs/project/dhf-manifest"
    if not manifest_dir.is_dir():
        return None
    for f in manifest_dir.glob("*-dhf-manifest.json"):
        try:
            return json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
    return None


def _obligations_for_role(
    manifest: dict | None, dhf_leaf: str, canonical_role: str
) -> list[dict]:
    if not manifest:
        return []
    dhf_obls = (manifest.get("dhf_manifest") or {}).get(dhf_leaf) or []
    out = []
    role_n = "".join(c for c in canonical_role.lower() if c.isalnum())
    for o in dhf_obls:
        if not isinstance(o, dict):
            continue
        topic_n = "".join(c for c in (o.get("topic") or "").lower() if c.isalnum())
        atype_n = "".join(c for c in (o.get("artifact_type") or "").lower() if c.isalnum())
        if role_n and (role_n in topic_n or role_n in atype_n or topic_n in role_n):
            out.append({
                "id": o.get("id"),
                "title": o.get("title"),
                "topic": o.get("topic"),
                "artifact_type": o.get("artifact_type"),
                "applies_to": o.get("applies_to") or [],
                "criticality": o.get("criticality"),
                "extracted_requirements": o.get("extracted_requirements"),
                "reg_source": (o.get("reg_source") or {}).get("citation"),
            })
    return out


def _read_milestones(project_dir: Path) -> list[dict]:
    cat = load_yaml(project_dir / "docs/project/milestones/regulatory.yml")
    return cat.get("milestones", []) or []


def _read_strategy_excerpt(project_dir: Path, max_chars: int = 4000) -> str:
    """Read the first chunk of regulatory-strategy.md to give the agent
    project-specific filing context. Falls back to empty when missing."""
    f = project_dir / "docs/project/strategies/regulatory-strategy.md"
    if not f.is_file():
        return ""
    try:
        return f.read_text(encoding="utf-8", errors="ignore")[:max_chars]
    except Exception:
        return ""


def _bundle_to_yaml(bundle: dict) -> str:
    import yaml as _yaml
    return _yaml.safe_dump(bundle, sort_keys=False, default_flow_style=False,
                           width=100, allow_unicode=True)


def _entries_for_taxonomy(
    project_dir: Path, entry: dict, manifest: dict | None
) -> list[dict]:
    """Return one assessment entry per taxonomy mapping (file or aggregate).
    Each entry carries: file path, title, role, members (if aggregate),
    frontmatter/head excerpt, applicable catalog obligations."""
    tax_file: Path = entry["file"]
    if not tax_file.is_file():
        return []
    taxonomy = load_yaml(tax_file)
    discovery_root = taxonomy.get("discovery_root", ".") or "."
    mappings = taxonomy.get("mappings") or {}

    # Resolve walk_base (where the relative paths in mappings resolve from).
    # For DHF taxonomies: dhf path / discovery_root.
    pyl = load_yaml(project_dir / "project.yml")
    dhfs_by_leaf = {d.get("leaf"): d for d in (pyl.get("dhfs") or [])}
    applies_to_dhfs = list(entry.get("applies_to_dhfs") or [])

    walk_bases: list[tuple[str, Path]] = []
    for leaf in applies_to_dhfs:
        d = dhfs_by_leaf.get(leaf)
        if d:
            walk_bases.append((leaf, (project_dir / d["path"] / discovery_root).resolve()))
    for p in (entry.get("applies_to_paths") or []):
        walk_bases.append(("(non-dhf)", (project_dir / p / discovery_root).resolve()))
    if not walk_bases:
        walk_bases.append(("(unknown)", tax_file.parent))

    out = []
    for rel_path, mapping in mappings.items():
        if mapping.get("unmapped"):
            continue
        role = mapping.get("canonical_role")
        if not role:
            continue

        # Resolve absolute path for frontmatter read; use first walk_base
        leaf, walk_base = walk_bases[0]
        if mapping.get("aggregate") == "folder":
            primary = mapping.get("primary_member") or rel_path
            target = walk_base / primary
            members = mapping.get("members") or []
        else:
            target = walk_base / rel_path
            members = []

        head = _read_head(target) if target.is_file() else ""
        title = mapping.get("title") or rel_path

        out.append({
            "file": rel_path,
            "title": title,
            "canonical_role": role,
            "subkind": mapping.get("subkind"),
            "aggregate": mapping.get("aggregate"),
            "members": members,
            "primary_member": mapping.get("primary_member"),
            "dhf_leaf": leaf,
            "abs_path_exists": target.is_file() if target else False,
            "frontmatter_head": head,
            "catalog_obligations": _obligations_for_role(manifest, leaf, role),
        })
    return out


def _split_into_batches(entries: list[dict], max_size: int) -> list[list[dict]]:
    """Group entries by canonical_role; auto-split roles with > max_size files."""
    by_role: dict[str, list[dict]] = {}
    for e in entries:
        by_role.setdefault(e["canonical_role"], []).append(e)
    batches: list[list[dict]] = []
    for role, items in sorted(by_role.items()):
        for i in range(0, len(items), max_size):
            batches.append(items[i:i + max_size])
    return batches


def _bundle_for_batch(
    batch: list[dict],
    *,
    milestones: list[dict],
    strategy_excerpt: str,
    posture_vocabulary: list[dict],
    output_path: str,
) -> dict:
    role = batch[0]["canonical_role"] if batch else "unknown"
    return {
        "batch_role": role,
        "batch_size": len(batch),
        "output_path": output_path,
        "schema_contract": {
            "format": "Return EXACTLY ONE JSON object. NO commentary, NO "
                      "markdown fences, NO trailing text. The orchestrator "
                      "parses strictly.",
            "shape": {
                "batch_role": "<role>",
                "assessments": [
                    {
                        "file": "<rel-path-from-input>",
                        "title": "<friendly title>",
                        "scope": "submission | other",
                        "scope_rationale": "<1 sentence>",
                        "phase_map": {
                            "<milestone_id>": {
                                "posture": "draft-readiness | full-package | update | inherited | phase-only | n/a",
                                "version_label": "<e.g. v0.1-draft, v1.0, v1.1>",
                                "rationale": "<1 sentence — why THIS posture for THIS file at THIS milestone>"
                            }
                        }
                    }
                ],
                "batch_gaps": [
                    {
                        "milestone": "<milestone_id>",
                        "obligation_id": "<from catalog>",
                        "title": "<obligation title>",
                        "expected_role": "<canonical_role this gap implies>",
                        "rationale": "<1 sentence — why this is missing>"
                    }
                ]
            },
        },
        "posture_vocabulary": posture_vocabulary,
        "milestone_catalog": milestones,
        "regulatory_strategy_excerpt": strategy_excerpt,
        "files_to_assess": batch,
    }


POSTURE_VOCABULARY = [
    {"id": "draft-readiness",
     "meaning": "Early/incomplete version sufficient for the milestone "
                "purpose (e.g., SAD at QSub is a draft used to anchor "
                "FDA discussion, NOT a final submission artifact)."},
    {"id": "full-package",
     "meaning": "Final, signed, submission-ready version. Used when this "
                "is the milestone where the artifact reaches its fully "
                "authoritative state for the regulatory record (e.g., "
                "SAD at 510k+PCCP filing)."},
    {"id": "update",
     "meaning": "Revised from a prior milestone — same logical artifact, "
                "new version number reflecting design changes (e.g., SAD "
                "at LMR1 reflects post-clearance design refinements). "
                "Iteration releases (LMR1, LMR2) typically use this."},
    {"id": "inherited",
     "meaning": "Carried forward from a prior milestone with no change. "
                "The artifact is part of the package but its content is "
                "identical to the prior milestone's version."},
    {"id": "phase-only",
     "meaning": "The artifact ONLY exists for this one milestone "
                "(e.g., QSub Cover Letter is a one-time submission piece; "
                "510k Cover Letter is a different one-time piece for the "
                "filing event)."},
    {"id": "n/a",
     "meaning": "Not applicable to this milestone. The artifact has no "
                "role in this milestone's package."},
]


def main() -> int:
    ap = argparse.ArgumentParser(description="/tracker assess-phases bundle builder")
    ap.add_argument("--project-dir", required=True)
    ap.add_argument("--all", action="store_true",
                    help="Build batches for every taxonomy mapping in the project")
    ap.add_argument("--role", help="Limit to one canonical role")
    ap.add_argument("--max-batch-size", type=int, default=MAX_BATCH_SIZE)
    ap.add_argument("--out", help="Directory to write bundles + manifest.json")
    ap.add_argument("--dry-run", action="store_true",
                    help="Print batch counts; do not write")
    args = ap.parse_args()

    project_dir = Path(args.project_dir).resolve()
    registry = list_registered_taxonomies(project_dir)
    if not registry:
        print("No taxonomies registered in project.yml.taxonomies[]", file=sys.stderr)
        return 1

    manifest = _load_dhf_manifest(project_dir)
    milestones = _read_milestones(project_dir)
    strategy_excerpt = _read_strategy_excerpt(project_dir)

    all_entries: list[dict] = []
    for entry in registry:
        all_entries.extend(_entries_for_taxonomy(project_dir, entry, manifest))

    if args.role:
        all_entries = [e for e in all_entries if e["canonical_role"] == args.role]

    batches = _split_into_batches(all_entries, args.max_batch_size)

    if args.dry_run:
        print(f"Total entries: {len(all_entries)}")
        print(f"Batches: {len(batches)} (max {args.max_batch_size} per batch)")
        for i, b in enumerate(batches):
            role = b[0]["canonical_role"] if b else "?"
            print(f"  [{i+1:2d}] role={role:20s} files={len(b)}")
        return 0

    if not args.out:
        print("error: --out required when not --dry-run", file=sys.stderr)
        return 2
    out_dir = Path(args.out).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest_out = {
        "schema_version": "0.1",
        "generated_by": "/tracker assess-phases bundle builder",
        "project_dir": str(project_dir),
        "milestones": [m.get("id") for m in milestones],
        "batches": [],
    }

    for i, batch in enumerate(batches):
        role = batch[0]["canonical_role"]
        bundle_id = f"{i+1:02d}__{_safe_id(role)}"
        bundle_path = out_dir / f"{bundle_id}.yaml"
        output_path = out_dir / f"{bundle_id}.result.json"
        bundle = _bundle_for_batch(
            batch,
            milestones=milestones,
            strategy_excerpt=strategy_excerpt,
            posture_vocabulary=POSTURE_VOCABULARY,
            output_path=str(output_path),
        )
        bundle_path.write_text(_bundle_to_yaml(bundle), encoding="utf-8")
        manifest_out["batches"].append({
            "bundle_id": bundle_id,
            "role": role,
            "file_count": len(batch),
            "bundle_path": str(bundle_path),
            "output_path": str(output_path),
        })

    (out_dir / "manifest.json").write_text(
        json.dumps(manifest_out, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(batches)} batch(es) + manifest.json to {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
