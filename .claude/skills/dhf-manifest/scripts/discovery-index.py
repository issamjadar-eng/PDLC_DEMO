#!/usr/bin/env python3
"""
discovery-index — resolve canonical roles to project file paths.

Usage:
    python3 .claude/skills/dhf-manifest/scripts/discovery-index.py [PROJECT_ROOT]

Reads:
    .claude/skills/dhf-manifest/data/canonical-roles.yaml   (L1 + L2)
    <PROJECT_ROOT>/project.yml                              (L3 overrides + dhf list)

Writes:
    <PROJECT_ROOT>/docs/project/dhf-manifest/<project>-dhf-discovery.json

Resolution algorithm (per role):
    1. Compute effective patterns list:
         L3 patterns_extra  (from project.yml evidence_layout.layers[role])
         ++ L2 patterns     (from canonical-roles.yaml)
         minus L3 patterns_exclude
    2. For each pattern in order, glob inside the role's folder.
    3. First pattern with exactly one match wins. Record alternatives in
       ambiguity_notes[]; record zero-match cases in gaps[].

Exits 0 on success, 1 on schema/io errors. Resolution gaps are recorded in
the output, not treated as failures (per /best-practices integration plan).
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: pyyaml not installed. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


def find_skill_dir(start: Path) -> Path | None:
    """Walk up from start until we find .claude/skills/dhf-manifest/."""
    cur = start.resolve()
    while cur != cur.parent:
        candidate = cur / ".claude/skills/dhf-manifest"
        if candidate.is_dir():
            return candidate
        cur = cur.parent
    return None


def load_canonical_roles(skill_dir: Path) -> dict:
    path = skill_dir / "data/canonical-roles.yaml"
    if not path.exists():
        raise FileNotFoundError(f"L1+L2 registry not found: {path}")
    return yaml.safe_load(path.read_text())


def load_project_yml(project_root: Path) -> dict:
    path = project_root / "project.yml"
    if not path.exists():
        raise FileNotFoundError(f"project.yml not found: {path}")
    return yaml.safe_load(path.read_text())


def project_slug(project_yml: dict) -> str:
    """Match the existing dhf-manifest filename slug convention."""
    name = (project_yml.get("project") or {}).get("name") or "project"
    return name.lower().replace(" ", "-").replace("_", "-")


def effective_patterns(patterns_base: list, override: dict) -> list[str]:
    """Merge a base patterns list with L3 overrides. Extras prepended; excludes removed."""
    extras = override.get("patterns_extra", [])
    excludes = set(override.get("patterns_exclude", []))
    merged = list(extras) + list(patterns_base or [])
    return [p for p in merged if p not in excludes]


def load_taxonomy(taxonomy_path: Path) -> dict | None:
    """Load a .taxonomy.yml file. Returns None if missing or unreadable."""
    if not taxonomy_path.exists():
        return None
    try:
        return yaml.safe_load(taxonomy_path.read_text())
    except Exception:
        return None


def external_folder_exists(taxonomy: dict, folder_name: str) -> bool:
    """Check whether the taxonomy declares (and thus considers valid) the given folder name."""
    return folder_name in (taxonomy.get("mappings") or {})


def glob_pattern(pattern: str, search_root: Path) -> list[Path]:
    """Glob a single pattern under search_root. Patterns containing '/' are
    treated as project-relative; others are matched against immediate children."""
    if "/" in pattern:
        # Project-relative pattern (e.g. docs/project/strategies/regulatory-strategy.md
        # or **/predicate-landscape.md).
        if "**" in pattern:
            return sorted(search_root.glob(pattern))
        else:
            candidate = search_root / pattern
            return [candidate] if candidate.exists() else []
    else:
        # Filename pattern — match against immediate children of search_root
        # (non-recursive).
        if not search_root.is_dir():
            return []
        return sorted(p for p in search_root.iterdir() if fnmatch.fnmatch(p.name, pattern))


def resolve_one(patterns: list[str], search_root: Path, project_root: Path) -> tuple[dict | None, list[dict], list[str]]:
    """Try patterns in order. Return (winner_entry, alternatives, patterns_tried).
    winner_entry is None if no pattern produced exactly one match."""
    winner = None
    alternatives = []
    tried = []
    for pattern in patterns:
        tried.append(pattern)
        hits = glob_pattern(pattern, search_root)
        # Filter to files (not directories)
        hits = [h for h in hits if h.is_file()]
        if not hits:
            continue
        if len(hits) == 1 and winner is None:
            winner = build_entry(hits[0], project_root, pattern)
        else:
            # >1 matches — record alternatives (if we already have a winner, these
            # are runner-ups; if not yet, the multi-match is an ambiguity too).
            for h in hits:
                # Skip if it's the winner itself
                if winner and winner["path"] == relpath(h, project_root):
                    continue
                alternatives.append({"pattern": pattern, "path": relpath(h, project_root)})
    return winner, alternatives, tried


def build_entry(path: Path, project_root: Path, matched_pattern: str) -> dict:
    rel = relpath(path, project_root)
    size = path.stat().st_size
    return {
        "path": rel,
        "exists": True,
        "size_bytes": size,
        "tokens_estimate": size // 4,
        "matched_pattern": matched_pattern,
    }


def relpath(path: Path, project_root: Path) -> str:
    try:
        return str(path.resolve().relative_to(project_root.resolve()))
    except ValueError:
        return str(path)


def get_overrides(project_yml: dict) -> dict:
    return ((project_yml.get("evidence_layout") or {}).get("layers") or {})


def build_multi_file_entry(folder_rel: str, search_root: Path, patterns: list[str]) -> dict:
    """Folder-pointer entry shape (multi_file: true roles + external_data scope).
    Enumerates every file matching any pattern under search_root and reports the
    folder + count. Consumers Glob the folder themselves when they need specifics.
    """
    all_hits: list[Path] = []
    for pattern in patterns:
        all_hits.extend(glob_pattern(pattern, search_root))
    files = sorted({h.resolve() for h in all_hits if h.is_file()})
    return {
        "folder": folder_rel,
        "exists": search_root.is_dir(),
        "file_count": len(files),
        "patterns_used": list(patterns),
    }


def resolve_project_role(role_name: str, role_def: dict, override: dict,
                        project_root: Path, output: dict) -> None:
    folder = override.get("folder_override", role_def.get("folder", ""))
    search_root = project_root / folder if folder else project_root
    patterns = effective_patterns(role_def.get("patterns"), override)

    if role_def.get("multi_file"):
        # Folder-pointer shape — researchers Glob the folder as needed.
        output["project_roles"][role_name] = build_multi_file_entry(folder, search_root, patterns)
        if not search_root.is_dir():
            output["gaps"].append({
                "scope": "project", "role": role_name,
                "reason": f"folder does not exist: {folder}",
                "patterns_tried": patterns,
            })
        return

    winner, alternatives, tried = resolve_one(patterns, search_root, project_root)
    if winner:
        output["project_roles"][role_name] = winner
        if alternatives:
            output["ambiguity_notes"].append({
                "scope": "project", "role": role_name,
                "winning_pattern": winner["matched_pattern"],
                "winning_path": winner["path"],
                "alternatives": alternatives,
            })
    else:
        output["gaps"].append({
            "scope": "project", "role": role_name,
            "reason": f"no file matched any pattern" + (f" in {folder}" if folder else ""),
            "patterns_tried": tried,
        })


def resolve_per_dhf_role(role_name: str, role_def: dict, override: dict,
                         project_yml: dict, project_root: Path, output: dict) -> None:
    """Per-DHF role resolution. Branches on each DHF's dhf_organization."""
    for dhf in project_yml.get("dhfs") or []:
        dhf_id = dhf.get("leaf") or dhf.get("id")
        dhf_path = project_root / dhf["path"]
        mode = dhf.get("dhf_organization", "internal")
        output["dhf_roles"].setdefault(dhf_id, {
            "role": dhf.get("role"),
            "dhf_organization": mode,
        })

        if mode == "internal":
            mode_block = role_def.get("internal") or {
                # Backwards-compat: top-level folder/patterns are internal-mode shorthand
                "folder": role_def.get("folder", ""),
                "patterns": role_def.get("patterns", []),
            }
            folder = override.get("folder_override", mode_block.get("folder", ""))
            patterns = effective_patterns(mode_block.get("patterns"), override)
            search_root = dhf_path / folder if folder else dhf_path

            if role_def.get("multi_file"):
                # Folder-pointer shape — same as external_data, just per-DHF scoped.
                folder_rel = relpath(search_root, project_root)
                output["dhf_roles"][dhf_id][role_name] = build_multi_file_entry(
                    folder_rel, search_root, patterns
                )
                if not search_root.is_dir():
                    output["gaps"].append({
                        "scope": "per-dhf", "dhf": dhf_id, "role": role_name,
                        "reason": f"folder does not exist: {folder_rel}",
                        "patterns_tried": patterns,
                    })
            else:
                _bind_per_dhf(role_name, dhf_id, search_root, patterns, project_root, output, folder)

        elif mode == "external":
            mode_block = role_def.get("external")
            if not mode_block:
                # Role not mapped in external mode — informational gap, not a failure.
                output["dhf_roles"][dhf_id][role_name] = None
                output["gaps"].append({
                    "scope": "per-dhf", "dhf": dhf_id, "role": role_name,
                    "reason": "role has no external-mode mapping in canonical-roles.yaml "
                              "(not applicable in this DHF's organizational mode)",
                    "patterns_tried": [],
                    "informational": True,
                })
                continue
            if role_def.get("multi_file"):
                # Multi-file in external mode is deferred — convention not yet defined
                # in the taxonomy. Emit informational gap, not a failure.
                output["dhf_roles"][dhf_id][role_name] = None
                output["gaps"].append({
                    "scope": "per-dhf", "dhf": dhf_id, "role": role_name,
                    "reason": "multi_file roles in external mode are not yet supported "
                              "(taxonomy has no convention for multi-file artifact families)",
                    "patterns_tried": [],
                    "informational": True,
                })
                continue

            taxonomy_rel = dhf.get("taxonomy_path")
            if not taxonomy_rel:
                output["dhf_roles"][dhf_id][role_name] = None
                output["gaps"].append({
                    "scope": "per-dhf", "dhf": dhf_id, "role": role_name,
                    "reason": "DHF declares dhf_organization=external but no taxonomy_path",
                    "patterns_tried": [],
                })
                continue

            taxonomy = load_taxonomy(project_root / taxonomy_rel)
            if not taxonomy:
                output["dhf_roles"][dhf_id][role_name] = None
                output["gaps"].append({
                    "scope": "per-dhf", "dhf": dhf_id, "role": role_name,
                    "reason": f"taxonomy file not found or unreadable: {taxonomy_rel}",
                    "patterns_tried": [],
                })
                continue

            taxonomy_folder = mode_block.get("taxonomy_folder")
            if not external_folder_exists(taxonomy, taxonomy_folder):
                # Role declares an external-mode mapping but the project's taxonomy
                # doesn't catalog that folder. This is "not applicable in this
                # project's external template", which is informational — same
                # semantic as the role having no external block at all.
                output["dhf_roles"][dhf_id][role_name] = None
                output["gaps"].append({
                    "scope": "per-dhf", "dhf": dhf_id, "role": role_name,
                    "reason": f"taxonomy folder '{taxonomy_folder}' not declared in {taxonomy_rel}",
                    "patterns_tried": [],
                    "informational": True,
                })
                continue

            discovery_root = taxonomy.get("discovery_root", "")
            patterns = effective_patterns(mode_block.get("patterns"), override)
            nested_root = dhf_path / discovery_root / taxonomy_folder
            flat_file = dhf_path / discovery_root / f"{taxonomy_folder}.md"

            # Sub-convention A: nested folder layout — <discovery_root>/<folder>/v*.md
            if nested_root.is_dir():
                _bind_per_dhf(role_name, dhf_id, nested_root, patterns, project_root, output,
                              f"{discovery_root}/{taxonomy_folder}" if discovery_root else taxonomy_folder)
            # Sub-convention B: flat file layout — <discovery_root>/<folder>.md
            elif flat_file.is_file():
                entry = build_entry(flat_file, project_root, f"{taxonomy_folder}.md (flat-file)")
                output["dhf_roles"][dhf_id][role_name] = entry
            else:
                output["dhf_roles"][dhf_id][role_name] = None
                output["gaps"].append({
                    "scope": "per-dhf", "dhf": dhf_id, "role": role_name,
                    "reason": f"neither {discovery_root}/{taxonomy_folder}/ folder "
                              f"nor {discovery_root}/{taxonomy_folder}.md flat-file found",
                    "patterns_tried": patterns,
                })

        else:
            output["dhf_roles"][dhf_id][role_name] = None
            output["gaps"].append({
                "scope": "per-dhf", "dhf": dhf_id, "role": role_name,
                "reason": f"unknown dhf_organization mode: {mode!r}",
                "patterns_tried": [],
            })


def _bind_per_dhf(role_name: str, dhf_id: str, search_root: Path, patterns: list,
                  project_root: Path, output: dict, folder_label: str) -> None:
    winner, alternatives, tried = resolve_one(patterns, search_root, project_root)
    if winner:
        output["dhf_roles"][dhf_id][role_name] = winner
        if alternatives:
            output["ambiguity_notes"].append({
                "scope": "per-dhf", "dhf": dhf_id, "role": role_name,
                "winning_pattern": winner["matched_pattern"],
                "winning_path": winner["path"],
                "alternatives": alternatives,
            })
    else:
        output["dhf_roles"][dhf_id][role_name] = None
        output["gaps"].append({
            "scope": "per-dhf", "dhf": dhf_id, "role": role_name,
            "reason": f"no file matched any pattern in {folder_label or '<dhf-root>'}",
            "patterns_tried": tried,
        })


def resolve_per_submission_role(role_name: str, role_def: dict, override: dict,
                                project_yml: dict, project_root: Path, output: dict) -> None:
    submissions = project_yml.get("submissions") or _infer_submissions(project_root)
    folder_template = role_def.get("folder", "")
    patterns = effective_patterns(role_def.get("patterns"), override)
    for sub in submissions:
        sub_id = sub if isinstance(sub, str) else sub.get("id")
        folder = folder_template.replace("{submission_id}", sub_id)
        search_root = project_root / folder
        output["submission_roles"].setdefault(sub_id, {})
        winner, alternatives, tried = resolve_one(patterns, search_root, project_root)
        if winner:
            output["submission_roles"][sub_id][role_name] = winner
            if alternatives:
                output["ambiguity_notes"].append({
                    "scope": "per-submission", "submission": sub_id, "role": role_name,
                    "winning_pattern": winner["matched_pattern"],
                    "winning_path": winner["path"],
                    "alternatives": alternatives,
                })
        else:
            output["submission_roles"][sub_id][role_name] = None
            output["gaps"].append({
                "scope": "per-submission", "submission": sub_id, "role": role_name,
                "reason": f"no file matched any pattern in {folder}",
                "patterns_tried": tried,
            })


def _infer_submissions(project_root: Path) -> list[str]:
    """If project.yml has no submissions[] block, infer from
    docs/project/submissions/<id>/ directories."""
    submissions_dir = project_root / "docs/project/submissions"
    if not submissions_dir.is_dir():
        return []
    return sorted(p.name for p in submissions_dir.iterdir()
                  if p.is_dir() and not p.name.startswith("."))


def resolve_external_role(role_name: str, role_def: dict, override: dict,
                          project_root: Path, output: dict) -> None:
    """External_data roles enumerate files in a project-relative folder rather than
    picking one canonical. We record presence + count; no winner concept."""
    folder = override.get("folder_override", role_def.get("folder", ""))
    search_root = project_root / folder
    patterns = effective_patterns(role_def.get("patterns"), override)
    all_hits = []
    for pattern in patterns:
        all_hits.extend(glob_pattern(pattern, search_root))
    all_hits = [h for h in all_hits if h.is_file()]
    output["external_roles"][role_name] = {
        "folder": str(folder),
        "exists": search_root.is_dir(),
        "file_count": len(all_hits),
        "patterns_used": patterns,
    }
    if not search_root.is_dir():
        output["gaps"].append({
            "scope": "external", "role": role_name,
            "reason": f"folder does not exist: {folder}",
            "patterns_tried": patterns,
        })


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the canonical-role discovery index.")
    parser.add_argument("project_root", nargs="?", default=".",
                        help="Project root (default: current directory).")
    parser.add_argument("--skill-dir",
                        help="Skill directory override (default: auto-discover .claude/skills/dhf-manifest from project root).")
    parser.add_argument("--out",
                        help="Output path override (default: docs/project/dhf-manifest/<slug>-dhf-discovery.json).")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    skill_dir = Path(args.skill_dir).resolve() if args.skill_dir else find_skill_dir(project_root)
    if skill_dir is None or not skill_dir.is_dir():
        print(f"ERROR: cannot locate .claude/skills/dhf-manifest from {project_root}", file=sys.stderr)
        return 1

    registry = load_canonical_roles(skill_dir)
    project_yml = load_project_yml(project_root)
    overrides = get_overrides(project_yml)
    slug = project_slug(project_yml)

    output = {
        "schema_version": "1.0",
        "generated": datetime.now(timezone.utc).isoformat(),
        "project": slug,
        "project_roles": {},
        "dhf_roles": {},
        "submission_roles": {},
        "external_roles": {},
        "gaps": [],
        "ambiguity_notes": [],
    }

    for role_name, role_def in (registry.get("roles") or {}).items():
        override = overrides.get(role_name) or {}
        scope = role_def.get("scope", "per-dhf")
        if scope == "project":
            resolve_project_role(role_name, role_def, override, project_root, output)
        elif scope == "per-dhf":
            resolve_per_dhf_role(role_name, role_def, override, project_yml, project_root, output)
        elif scope == "per-submission":
            resolve_per_submission_role(role_name, role_def, override, project_yml, project_root, output)
        elif scope in ("external", "external_data"):
            resolve_external_role(role_name, role_def, override, project_root, output)
        else:
            print(f"WARN: unknown scope '{scope}' for role '{role_name}', skipping", file=sys.stderr)

    out_path = Path(args.out) if args.out else (
        project_root / "docs/project/dhf-manifest" / f"{slug}-dhf-discovery.json"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(output, indent=2) + "\n")

    n_project = len(output["project_roles"])
    n_dhf = sum(len([k for k in v if k != "role" and v[k] is not None])
                for v in output["dhf_roles"].values())
    n_gaps = len(output["gaps"])
    n_amb = len(output["ambiguity_notes"])
    print(f"discovery-index: {n_project} project + {n_dhf} per-dhf resolutions; "
          f"{n_gaps} gaps; {n_amb} ambiguity notes → {out_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
