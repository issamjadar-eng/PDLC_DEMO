"""Tracker assess.py — Phase 3 (resolution layer only).

Reads the DHF manifest catalog + project.yml wiring, resolves each obligation's
`applies_to` patterns against the project tree (per DHF), and writes a sidecar
recording bound evidence paths + zero-match warnings. No coverage analysis,
no lifecycle verdicts — those land in Phase 4.

The resolver consumes existing project config and never invents folder mappings:
  - For internal DHFs (`dhf_organization` absent or 'internal'): canonical_role →
    folder via the medtech-default `SYSTEM_DHF_ROLE_MAP` from generate.py (or
    `tracker.system_dhf_layout` override in project.yml).
  - For external DHFs (`dhf_organization: external`): canonical_role → folder via
    reverse-lookup of `<dhf>.taxonomy_path` (.taxonomy.yml mappings).
  - For submission-authored obligations (`canonical_role: submission-authored`):
    base is `docs/project/submissions/<filing>/` from `dhfs[].filing`.

Catalog `applies_to` schema (Phase 2b structured form):
    [{role: <canonical_role>, file_pattern: <leaf glob>}, ...]
Legacy free-text entries (string list) are tolerated and reported as
`unresolvable` warnings until they're converted.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

# Reuse the medtech-default role-map and taxonomy resolver from generate.py
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
import generate  # type: ignore  # noqa: E402


def find_project_dir(start: Path | None = None) -> Path:
    p = (start or Path.cwd()).resolve()
    for ancestor in [p] + list(p.parents):
        if (ancestor / "project.yml").exists():
            return ancestor
    raise SystemExit("project.yml not found from cwd")


def load_yaml(path: Path) -> dict:
    with path.open() as f:
        return yaml.safe_load(f) or {}


def internal_role_to_folder(canonical_role: str, project_yml: dict) -> str | None:
    """Look up the subfolder (relative to DHF root) for a canonical_role under the
    internal medtech-docs convention. Honors `tracker.system_dhf_layout` override."""
    tracker_cfg = project_yml.get("tracker") or {}
    generate.load_project_system_dhf_layout(tracker_cfg)
    for sub_path, role, _subkind in generate.SYSTEM_DHF_ROLE_MAP:
        if role == canonical_role:
            return sub_path
    return None


def external_role_to_folder(canonical_role: str, taxonomy: dict) -> str | None:
    """Reverse-lookup a canonical_role to its discovery folder name in the
    external taxonomy (.taxonomy.yml). Returns the first match's discovery
    sub_path under `discovery_root`."""
    discovery_root = taxonomy.get("discovery_root", "")
    mappings = taxonomy.get("mappings") or {}
    for folder_name, mapping in mappings.items():
        if not isinstance(mapping, dict):
            continue
        if mapping.get("canonical_role") == canonical_role:
            return f"{discovery_root}/{folder_name}".strip("/")
    return None


def resolve_obligation(
    obligation: dict,
    dhf: dict,
    project_root: Path,
    project_yml: dict,
    taxonomy_cache: dict,
) -> dict:
    """Resolve a single obligation against a single DHF tree.

    Returns:
        {obligation_id, canonical_role, criticality, applies_to: [{role, file_pattern,
         resolved_paths, warnings}], obligation_warnings}
    """
    oid = obligation.get("id") or obligation.get("obligation_id") or "<unknown>"
    canonical_role = obligation.get("canonical_role")
    criticality = obligation.get("criticality")
    applies_to = obligation.get("applies_to") or []

    out: dict = {
        "obligation_id": oid,
        "canonical_role": canonical_role,
        "criticality": criticality,
        "applies_to": [],
        "obligation_warnings": [],
    }

    if not canonical_role:
        out["obligation_warnings"].append(
            "missing canonical_role — cannot resolve folder base; obligation skipped"
        )
        return out

    # Submission-authored obligations resolve against submissions/<filing>/, not a DHF tree
    if canonical_role == "submission-authored":
        filing = dhf.get("filing")
        if not filing:
            out["obligation_warnings"].append(
                "submission-authored obligation but DHF has no `filing` key in project.yml"
            )
            return out
        # Strip plus-segments e.g. "510k+pccp" → use first as primary submission folder
        primary_filing = filing.split("+")[0]
        base = project_root / "docs/project/submissions" / primary_filing
    else:
        dhf_path = dhf.get("path")
        if not dhf_path:
            out["obligation_warnings"].append("DHF has no `path` in project.yml")
            return out
        dhf_root = project_root / dhf_path
        org = dhf.get("dhf_organization", "internal")
        if org == "external":
            taxonomy_path = dhf.get("taxonomy_path")
            if not taxonomy_path:
                out["obligation_warnings"].append(
                    "external DHF but no taxonomy_path in project.yml"
                )
                return out
            tp = project_root / taxonomy_path
            if tp not in taxonomy_cache:
                taxonomy_cache[tp] = load_yaml(tp)
            taxonomy = taxonomy_cache[tp]
        else:
            taxonomy = None

        # Per-applies-to entry, the role MAY differ from the obligation's top-level
        # canonical_role (cross-role obligations). Resolve each entry's role.
        base = dhf_root  # placeholder, overridden below per-entry

    for entry in applies_to:
        if not isinstance(entry, dict):
            # Legacy free-text — flag as unresolved
            out["applies_to"].append({
                "role": None,
                "file_pattern": str(entry),
                "resolved_paths": [],
                "warnings": ["legacy free-text applies_to entry — convert to {role, file_pattern} per Phase 2b"],
            })
            continue

        entry_role = entry.get("role") or canonical_role
        pattern = entry.get("file_pattern") or entry.get("artifact_pattern")
        warnings: list[str] = []
        resolved_paths: list[str] = []

        if not pattern:
            warnings.append("applies_to entry has no file_pattern")
            out["applies_to"].append({
                "role": entry_role,
                "file_pattern": None,
                "resolved_paths": [],
                "warnings": warnings,
            })
            continue

        # Compute the resolution base for this entry
        if canonical_role == "submission-authored":
            entry_base = base
        else:
            if entry_role == "submission-authored":
                # Cross-role into submissions
                filing = dhf.get("filing", "").split("+")[0]
                entry_base = project_root / "docs/project/submissions" / filing if filing else None
            elif dhf.get("dhf_organization", "internal") == "external":
                folder = external_role_to_folder(entry_role, taxonomy or {})
                if folder is None:
                    warnings.append(
                        f"taxonomy has no folder for canonical_role '{entry_role}'"
                    )
                    entry_base = None
                else:
                    entry_base = dhf_root / folder
            else:
                folder = internal_role_to_folder(entry_role, project_yml)
                if folder is None:
                    warnings.append(
                        f"medtech-default SYSTEM_DHF_ROLE_MAP has no folder for canonical_role "
                        f"'{entry_role}' — gap in skill convention"
                    )
                    entry_base = None
                else:
                    entry_base = dhf_root / folder

        if entry_base is not None:
            if not entry_base.exists():
                warnings.append(f"resolution base does not exist on disk: {entry_base.relative_to(project_root)}")
            else:
                matches = list(entry_base.rglob(pattern))
                # Filter out files in formal/ subfolders (working drafts only)
                matches = [m for m in matches if m.is_file()]
                resolved_paths = [str(m.relative_to(project_root)) for m in sorted(matches)]
                if not resolved_paths:
                    warnings.append(
                        f"zero-match: catalog expects {entry_role}/{pattern} under "
                        f"{entry_base.relative_to(project_root)}"
                    )

        out["applies_to"].append({
            "role": entry_role,
            "file_pattern": pattern,
            "resolved_paths": resolved_paths,
            "warnings": warnings,
        })

    return out


def main():
    project_root = find_project_dir()
    project_yml = load_yaml(project_root / "project.yml")
    catalog_path = project_root / f"docs/project/dhf-manifest/{project_root.name}-dhf-manifest.json"
    if not catalog_path.exists():
        # try project name from project.yml
        project_slug = (project_yml.get("project") or {}).get("repo", "").split("/")[-1]
        if project_slug:
            catalog_path = project_root / f"docs/project/dhf-manifest/{project_slug}-dhf-manifest.json"
    if not catalog_path.exists():
        # fallback: glob
        candidates = list((project_root / "docs/project/dhf-manifest").glob("*-dhf-manifest.json"))
        if not candidates:
            raise SystemExit(f"catalog not found at {catalog_path}")
        catalog_path = candidates[0]

    with catalog_path.open() as f:
        catalog = json.load(f)

    dhfs_by_leaf = {dhf["leaf"]: dhf for dhf in (project_yml.get("dhfs") or []) if "leaf" in dhf}
    taxonomy_cache: dict = {}

    sidecar = {
        "schema_version": "0.1",
        "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "obligation_set_hash": catalog.get("obligation_set_hash"),
        "dhfs": {},
    }

    counts = {"resolved": 0, "zero_match": 0, "unresolvable": 0, "legacy": 0}
    manifest = catalog.get("dhf_manifest") or {}
    for dhf_leaf, obligations in manifest.items():
        dhf = dhfs_by_leaf.get(dhf_leaf)
        if not dhf:
            continue
        sidecar["dhfs"][dhf_leaf] = []
        for obl in obligations:
            res = resolve_obligation(obl, dhf, project_root, project_yml, taxonomy_cache)
            sidecar["dhfs"][dhf_leaf].append(res)
            for entry in res["applies_to"]:
                if entry["resolved_paths"]:
                    counts["resolved"] += 1
                elif "legacy free-text" in (entry["warnings"][0] if entry["warnings"] else ""):
                    counts["legacy"] += 1
                elif entry["warnings"]:
                    if any("zero-match" in w for w in entry["warnings"]):
                        counts["zero_match"] += 1
                    else:
                        counts["unresolvable"] += 1

    out_path = project_root / "docs/project/submissions/submission-tracker.agent.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w") as f:
        json.dump(sidecar, f, indent=2, sort_keys=False)
        f.write("\n")

    print(f"/tracker assess (Phase 3) — resolution layer")
    print(f"  Catalog: {catalog_path.relative_to(project_root)}")
    print(f"  Sidecar: {out_path.relative_to(project_root)}")
    print(f"  Counts:  {counts['resolved']} resolved, {counts['zero_match']} zero-match warnings, "
          f"{counts['unresolvable']} unresolvable, {counts['legacy']} legacy free-text")


if __name__ == "__main__":
    main()
