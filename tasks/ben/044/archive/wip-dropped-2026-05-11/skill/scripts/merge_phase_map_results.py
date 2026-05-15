#!/usr/bin/env python3
"""
/tracker assess-phases — verdict merger.

After regulatory-affairs agents have written their per-batch result JSONs
(one combined doc per batch with assessments[] + batch_gaps[]), this
script consolidates them into THREE sidecar files:

  - submission-tracker.phase-map.json  (per-file × per-milestone posture +
                                         scope + version_label + rationale)
  - submission-tracker.help.json       (per-file help block — extends/
                                         updates the existing enrich-help
                                         sidecar shape, keyed by row_id
                                         BUT also keyed by file path so
                                         downstream consumers can resolve
                                         either way)
  - submission-tracker.gaps.json       (per-milestone consolidated gap
                                         list across all batches)

Single deterministic pass. No second LLM call. Atomic-ish writes.

Usage:
    python3 merge_phase_map_results.py --project-dir <dir> \\
        --bundles-dir /tmp/phase-map-bundles/

    python3 merge_phase_map_results.py --project-dir <dir> \\
        --bundles-dir /tmp/phase-map-bundles/ --dry-run
"""

from __future__ import annotations

import argparse
import datetime
import json
import sys
from pathlib import Path


PHASE_MAP_REL = "docs/project/submissions/submission-tracker.phase-map.json"
GAPS_REL      = "docs/project/submissions/submission-tracker.gaps.json"
HELP_REL      = "docs/project/submissions/submission-tracker.help.json"


def _load_results(bundles_dir: Path) -> list[dict]:
    out = []
    for vf in sorted(bundles_dir.glob("*.result.json")):
        try:
            data = json.loads(vf.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"  [skip] {vf.name}: invalid JSON ({e})", file=sys.stderr)
            continue
        data["_source_file"] = str(vf)
        data["_bundle_id"] = vf.stem.replace(".result", "")
        out.append(data)
    return out


def _merge_phase_map(results: list[dict]) -> dict:
    """Per-file phase-map keyed by file path. Each entry carries scope,
    scope_rationale, phase_map (per milestone posture/version/rationale)."""
    rows: dict[str, dict] = {}
    for r in results:
        for a in (r.get("assessments") or []):
            f = a.get("file")
            if not f:
                continue
            rows[f] = {
                "title": a.get("title"),
                "canonical_role": r.get("batch_role"),
                "scope": a.get("scope"),
                "scope_rationale": a.get("scope_rationale"),
                "phase_map": a.get("phase_map") or {},
                "_source_bundle": r.get("_bundle_id"),
            }
    return {
        "schema_version": "0.1",
        "generated": datetime.datetime.now().isoformat(),
        "generated_by": "/tracker assess-phases (regulatory-affairs agent + merger)",
        "rows": rows,
    }


def _merge_help(results: list[dict]) -> dict:
    """Per-file help blocks. Keyed by file path (the generator joins to
    row_id at render time via the phase-map sidecar). Compatible with the
    existing enrich-help consumer in render.py — that consumer reads by
    row_id; the next /tracker render writes a row_id ↔ file lookup so
    help can be resolved either way."""
    rows: dict[str, dict] = {}
    for r in results:
        for a in (r.get("assessments") or []):
            f = a.get("file")
            help_block = a.get("help") or {}
            if not f or not help_block:
                continue
            rows[f] = {
                "title": a.get("title"),
                "description": help_block.get("description"),
                "why_important_in_project": help_block.get("why_important_in_project"),
                "main_topics": help_block.get("main_topics") or [],
                "regulatory_anchors": help_block.get("regulatory_anchors") or [],
                "_source_bundle": r.get("_bundle_id"),
            }
    return {
        "schema_version": "0.2",
        "generated": datetime.datetime.now().isoformat(),
        "generated_by": "/tracker assess-phases (regulatory-affairs agent + merger)",
        "key": "file_path",
        "rows": rows,
    }


def _merge_gaps(results: list[dict]) -> dict:
    """Per-milestone gap list, deduplicated by (milestone, obligation_id)."""
    by_milestone: dict[str, dict[str, dict]] = {}
    for r in results:
        for g in (r.get("batch_gaps") or []):
            ms = g.get("milestone")
            oid = g.get("obligation_id") or g.get("title")
            if not ms or not oid:
                continue
            existing = by_milestone.setdefault(ms, {})
            if oid in existing:
                continue
            existing[oid] = {
                "obligation_id": g.get("obligation_id"),
                "title": g.get("title"),
                "expected_role": g.get("expected_role"),
                "rationale": g.get("rationale"),
                "_source_bundle": r.get("_bundle_id"),
            }
    return {
        "schema_version": "0.1",
        "generated": datetime.datetime.now().isoformat(),
        "generated_by": "/tracker assess-phases (regulatory-affairs agent + merger)",
        "milestones": {
            ms: list(obls.values())
            for ms, obls in sorted(by_milestone.items())
        },
    }


def _summary(phase_map: dict, gaps: dict, help_doc: dict) -> str:
    rows = phase_map.get("rows") or {}
    submission_count = sum(1 for v in rows.values() if v.get("scope") == "submission")
    other_count = sum(1 for v in rows.values() if v.get("scope") == "other")
    gap_total = sum(len(v) for v in (gaps.get("milestones") or {}).values())
    help_count = len(help_doc.get("rows") or {})
    posture_counter: dict[str, int] = {}
    for r in rows.values():
        for ms_id, pm in (r.get("phase_map") or {}).items():
            p = pm.get("posture") or "unknown"
            posture_counter[p] = posture_counter.get(p, 0) + 1
    posture_line = ", ".join(f"{k}={v}" for k, v in sorted(posture_counter.items()))
    return (
        f"  files assessed:    {len(rows)}\n"
        f"  scope=submission:  {submission_count}\n"
        f"  scope=other:       {other_count}\n"
        f"  posture totals:    {posture_line}\n"
        f"  gaps (per-milestone): {gap_total} entries across "
        f"{len(gaps.get('milestones') or {})} milestone(s)\n"
        f"  help blocks:       {help_count}"
    )


def main() -> int:
    ap = argparse.ArgumentParser(description="/tracker assess-phases merger")
    ap.add_argument("--project-dir", required=True)
    ap.add_argument("--bundles-dir", required=True,
                    help="Directory containing *.result.json from agent runs")
    ap.add_argument("--dry-run", action="store_true",
                    help="Compute and print summary without writing sidecars")
    args = ap.parse_args()

    project_dir = Path(args.project_dir).resolve()
    bundles_dir = Path(args.bundles_dir).resolve()
    if not bundles_dir.is_dir():
        print(f"error: bundles dir not found: {bundles_dir}", file=sys.stderr)
        return 2

    results = _load_results(bundles_dir)
    if not results:
        print("No *.result.json files found; nothing to merge.")
        return 0

    phase_map = _merge_phase_map(results)
    help_doc = _merge_help(results)
    gaps = _merge_gaps(results)

    print(_summary(phase_map, gaps, help_doc))

    if args.dry_run:
        print("\nDry-run: no files written.")
        return 0

    (project_dir / PHASE_MAP_REL).write_text(
        json.dumps(phase_map, indent=2) + "\n", encoding="utf-8")
    (project_dir / HELP_REL).write_text(
        json.dumps(help_doc, indent=2) + "\n", encoding="utf-8")
    (project_dir / GAPS_REL).write_text(
        json.dumps(gaps, indent=2) + "\n", encoding="utf-8")
    print(
        f"\nWrote:\n"
        f"  {PHASE_MAP_REL}\n"
        f"  {HELP_REL}\n"
        f"  {GAPS_REL}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
