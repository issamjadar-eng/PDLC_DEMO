#!/usr/bin/env python3
"""
/tracker classify-folders — verdict merger.

After folder-classifier agents have written their per-folder verdict JSONs
to disk, this script applies them back to the .taxonomy.yml files.

For each verdict:
  - kind=aggregate or primary-with-supplements:
      • Drop per-file mappings under the folder
      • Add a folder mapping (key with trailing slash) carrying
        aggregate=folder, primary_member, members, confidence, rationale
      • Tag with `tier2_classifier: true` for provenance
  - kind=independent:
      • Leave per-file mappings unchanged
      • Add a per-folder note in the taxonomy's `classifier_notes:` block
        (no schema-bound field; informational only) so reviewers see
        the agent's verdict + rationale

Usage:
    python3 merge_classify_results.py --project-dir <dir> --bundles-dir /tmp/classify-bundles/
    python3 merge_classify_results.py --project-dir <dir> --manifest /tmp/classify-bundles/manifest.json
    python3 merge_classify_results.py --project-dir <dir> --bundles-dir <dir> --dry-run
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from taxonomy import dump_yaml, load_yaml  # noqa: E402


def _load_verdicts(bundles_dir: Path) -> list[dict]:
    """Walk bundles_dir for *.verdict.json files. Returns list of verdicts
    each augmented with the bundle id (filename stem)."""
    out = []
    for vf in sorted(bundles_dir.glob("*.verdict.json")):
        try:
            data = json.loads(vf.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"  [skip] {vf.name}: invalid JSON ({e})", file=sys.stderr)
            continue
        data["_bundle_id"] = vf.stem.replace(".verdict", "")
        data["_source_file"] = str(vf)
        out.append(data)
    return out


def _resolve_taxonomy_for_verdict(
    project_dir: Path, verdict: dict, manifest_lookup: dict
) -> Path | None:
    """Match a verdict to its taxonomy file. First tries manifest lookup;
    then walks project.yml.taxonomies[] to find one whose folder matches."""
    bundle_id = verdict.get("_bundle_id", "")
    if bundle_id in manifest_lookup:
        return Path(manifest_lookup[bundle_id]["taxonomy_file"])
    # Without manifest: caller must point us at one taxonomy at a time.
    return None


def _apply_verdict(taxonomy: dict, verdict_body: dict, folder_rel: str) -> dict:
    """Mutate taxonomy in place to reflect one folder's verdict.

    Returns a small report: {action, key_added, keys_removed}.
    """
    kind = verdict_body.get("kind")
    members = verdict_body.get("members") or []
    primary = verdict_body.get("primary_member")
    confidence = verdict_body.get("confidence", "medium")
    rationale = verdict_body.get("rationale", "Tier 2 classifier verdict")

    mappings = taxonomy.setdefault("mappings", {})
    folder_prefix = (folder_rel.rstrip("/") + "/") if folder_rel != "." else ""
    keys_removed = []

    if kind in ("aggregate", "primary-with-supplements"):
        # Drop per-file mappings within the folder
        keys_to_drop = [
            k for k in list(mappings.keys())
            if k.startswith(folder_prefix) and not k.endswith("/")
        ]
        for k in keys_to_drop:
            del mappings[k]
            keys_removed.append(k)
        # Add folder mapping
        folder_key = folder_prefix or "/"
        # Infer canonical_role from any member (or from existing per-file
        # mapping that we just removed)
        role = None
        if primary and primary in members:
            role = None  # filled below from existing mapping if present
        # Try to recover role from any dropped mapping by re-reading taxonomy
        # before the drop (not preserved here); fall back to scanning verdict
        # body or leaving as null if unknown.
        # Pragmatic fallback: tag with the role observed when the verdict
        # carries one. Verdicts produced by Tier 2 don't include role; rely
        # on the calling pipeline to also pass through role context. Since
        # we lack that here, leave role to be backfilled by the caller via
        # `--default-role` or by hand-editing post-merge.
        new_entry = {
            "canonical_role": role,
            "aggregate": "folder",
            "primary_member": primary,
            "members": members,
            "confidence": confidence,
            "rationale": rationale,
            "tier2_classifier": True,
        }
        # Strip None role so reviewers see the gap clearly
        if new_entry["canonical_role"] is None:
            del new_entry["canonical_role"]
        mappings[folder_key] = new_entry
        return {"action": "aggregated", "key_added": folder_key,
                "keys_removed": keys_removed}

    if kind == "independent":
        notes = taxonomy.setdefault("classifier_notes", [])
        notes.append({
            "folder": folder_rel,
            "verdict": "independent",
            "confidence": confidence,
            "rationale": rationale,
            "source": "tier2_classifier",
        })
        return {"action": "noted-independent", "key_added": None,
                "keys_removed": []}

    return {"action": "skipped-unknown-kind", "key_added": None,
            "keys_removed": []}


def main() -> int:
    ap = argparse.ArgumentParser(description="/tracker classify-folders merger")
    ap.add_argument("--project-dir", required=True)
    ap.add_argument("--bundles-dir",
                    help="Directory containing *.verdict.json from agent runs")
    ap.add_argument("--manifest",
                    help="Path to manifest.json from build_classify_context.py "
                         "(needed when verdicts span multiple taxonomies)")
    ap.add_argument("--taxonomy-file",
                    help="Apply all verdicts to this single taxonomy file "
                         "(use when --manifest is unavailable)")
    ap.add_argument("--dry-run", action="store_true",
                    help="Print actions without writing")
    ap.add_argument("--default-role",
                    help="Backfill canonical_role on aggregate folder mappings "
                         "(when the merger can't recover it from per-file "
                         "mappings being removed)")
    args = ap.parse_args()

    project_dir = Path(args.project_dir).resolve()
    if not args.bundles_dir:
        print("error: --bundles-dir is required", file=sys.stderr)
        return 2
    bundles_dir = Path(args.bundles_dir).resolve()
    if not bundles_dir.is_dir():
        print(f"error: bundles dir not found: {bundles_dir}", file=sys.stderr)
        return 2

    verdicts = _load_verdicts(bundles_dir)
    if not verdicts:
        print("No verdict JSON files found; nothing to merge.")
        return 0

    manifest_lookup: dict = {}
    if args.manifest:
        manifest_path = Path(args.manifest).resolve()
        if manifest_path.is_file():
            mdata = json.loads(manifest_path.read_text(encoding="utf-8"))
            for b in mdata.get("bundles") or []:
                manifest_lookup[b["bundle_id"]] = b

    # Group verdicts by taxonomy file
    by_taxonomy: dict[str, list[dict]] = {}
    for v in verdicts:
        if args.taxonomy_file:
            tax_rel = args.taxonomy_file
        else:
            tax_path = _resolve_taxonomy_for_verdict(project_dir, v, manifest_lookup)
            if tax_path is None:
                print(f"  [skip] {v.get('_bundle_id')}: no taxonomy resolved "
                      f"(provide --manifest or --taxonomy-file)", file=sys.stderr)
                continue
            tax_rel = str(tax_path)
        by_taxonomy.setdefault(tax_rel, []).append(v)

    overall_aggregated = 0
    overall_independent = 0
    for tax_rel, vs in by_taxonomy.items():
        tax_abs = project_dir / tax_rel
        if not tax_abs.is_file():
            print(f"  [skip] {tax_rel}: taxonomy file not on disk")
            continue
        taxonomy = load_yaml(tax_abs)
        for v in vs:
            folder_rel = v.get("folder")
            verdict_body = v.get("verdict") or {}
            if not folder_rel or not verdict_body:
                print(f"  [skip] {v.get('_bundle_id')}: missing folder/verdict")
                continue
            report = _apply_verdict(taxonomy, verdict_body, folder_rel)
            if report["action"] == "aggregated":
                overall_aggregated += 1
                if args.default_role:
                    entry = taxonomy["mappings"].get(report["key_added"])
                    if entry and "canonical_role" not in entry:
                        entry["canonical_role"] = args.default_role
                print(f"  [{tax_rel}] {folder_rel}: aggregated "
                      f"({len(report['keys_removed'])} per-file mapping(s) replaced)")
            elif report["action"] == "noted-independent":
                overall_independent += 1
                print(f"  [{tax_rel}] {folder_rel}: independent (noted)")
            else:
                print(f"  [{tax_rel}] {folder_rel}: {report['action']}")

        if not args.dry_run:
            dump_yaml(taxonomy, tax_abs)

    if args.dry_run:
        print(f"\nDry-run: {overall_aggregated} aggregated, "
              f"{overall_independent} independent. No files written.")
    else:
        print(f"\nApplied {overall_aggregated} aggregations + "
              f"{overall_independent} independent notes across "
              f"{len(by_taxonomy)} taxonomy file(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
