#!/usr/bin/env python3
"""
build-reference.py — Regulatory distillation aggregator.

Walks data/{fda-guidance,standards,industry-frameworks}/*.md, collects all
YAML obligation blocks, deduplicates by id, and emits:

  per-source JSON sidecar:   data/<category>/<file>.json
  aggregate YAML:            data/reference-dhf.yml  (canonical catalog)
  aggregate MD:              data/reference-dhf.md   (human-readable master table)
  scope enumeration:         data/scope-schema.yml
  per-dimension views:       data/dimensions/scope-<name>.md

The per-source JSON sidecar is the programmatic primitive for one regulator
source; consumers can read it directly instead of filtering the aggregate.
The aggregate still exists for cross-source queries (build-manifest, validate).

Usage:
  python3 build-reference.py [--skill-dir <path>] [--dry-run]

Exit codes: 0=success, 1=parse error, 2=duplicate ID found.
"""

import sys
import re
import json
import yaml
import argparse
from pathlib import Path
from datetime import date
from collections import defaultdict

from _linking import render_obl_link, is_valid_title

# Categories (subfolders under data/) scanned for Tier 1 source markdown.
CATEGORIES = ["fda-guidance", "standards", "industry-frameworks"]

SCOPE_DIMENSIONS = [
    "ai", "hardware", "software", "pccp", "510k",
    "tool-validation", "multi-function", "cybersecurity",
    "usability-hf", "clinical", "common-baseline",
]

TOPICS = [
    "architecture", "requirements", "design-outputs", "traceability",
    "risk-management", "verification", "validation", "software-lifecycle",
    "configuration-change", "design-reviews", "labeling-ifu",
    "human-factors", "cybersecurity", "clinical", "post-market",
    "regulatory-submission",
]

YAML_BLOCK_RE = re.compile(r"```yaml\n(.*?)```", re.DOTALL)


def parse_tier1_file(path: Path) -> list[dict]:
    """Extract all YAML obligation records from one Tier 1 distillation MD."""
    text = path.read_text(encoding="utf-8")
    records = []
    for match in YAML_BLOCK_RE.finditer(text):
        try:
            record = yaml.safe_load(match.group(1))
        except yaml.YAMLError as e:
            print(f"ERROR: YAML parse error in {path.name}: {e}", file=sys.stderr)
            sys.exit(1)
        if not isinstance(record, dict):
            continue
        if "id" not in record:
            continue
        record["_source_file"] = path.name
        records.append(record)
    return records


def discover_source_files(data_dir: Path) -> list[tuple[str, Path]]:
    """Return list of (category, md_path) for every Tier 1 source MD under
    data/<category>/*.md where <category> ∈ CATEGORIES. README.md files are
    skipped (they describe the folder, not obligations)."""
    pairs: list[tuple[str, Path]] = []
    for category in CATEGORIES:
        cat_dir = data_dir / category
        if not cat_dir.exists():
            continue
        for md in sorted(cat_dir.glob("*.md")):
            if md.name.lower() == "readme.md":
                continue
            pairs.append((category, md))
    return pairs


def build_reference_dhf(data_dir: Path) -> tuple[list[dict], dict, dict]:
    """Collect + deduplicate every obligation record across all categories.

    Returns:
      all_records — flat deduped list (drives the aggregate)
      scope_schema — dimensions + topics + counts
      by_file — {md_path: [records]} for per-source JSON sidecars
    """
    all_records = []
    seen_ids: dict[str, str] = {}
    by_file: dict[Path, list[dict]] = {}

    for category, md_file in discover_source_files(data_dir):
        records = parse_tier1_file(md_file)
        for record in records:
            record["_category"] = category  # stamp category onto record
            oid = record["id"]
            if oid in seen_ids:
                print(
                    f"ERROR: Duplicate obligation ID '{oid}' in {md_file} "
                    f"(first seen in {seen_ids[oid]})",
                    file=sys.stderr,
                )
                sys.exit(2)
            seen_ids[oid] = str(md_file)
            all_records.append(record)
        by_file[md_file] = records

    scope_schema = {
        "dimensions": SCOPE_DIMENSIONS,
        "topics": TOPICS,
        "categories": CATEGORIES,
        "total_obligations": len(all_records),
    }
    return all_records, scope_schema, by_file


def render_source_json(category: str, md_path: Path, records: list[dict]) -> str:
    """Render the per-source JSON sidecar (one per Tier 1 MD file)."""
    # Drop transient _-prefixed fields but keep _category as a top-level property
    def clean(r: dict) -> dict:
        return {k: v for k, v in r.items() if not k.startswith("_")}

    by_topic: dict[str, list[str]] = defaultdict(list)
    for r in records:
        topic = r.get("topic", "")
        if topic:
            by_topic[topic].append(r["id"])

    payload = {
        "generated": date.today().isoformat(),
        "category": category,
        "source_file": md_path.name,
        "obligation_count": len(records),
        "obligations": [clean(r) for r in records],
        "by_topic": dict(sorted(by_topic.items())),
        "obligation_ids": [r["id"] for r in records],
    }
    return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"


def _obl_href_from_reference(record: dict) -> str | None:
    """Build the href for an OBL from reference-dhf.md (which lives at data/).

    href = '<category>/<source_file>#<OBL-id>'
    Returns None if the record doesn't carry enough info to build one.
    """
    category = record.get("_category") or ""
    source_file = record.get("_source_file") or ""
    oid = record.get("id") or ""
    if not (category and source_file and oid):
        return None
    return f"{category}/{source_file}#{oid}"


def _obl_href_from_dimension(record: dict) -> str | None:
    """Build the href for an OBL from a dimension doc under data/dimensions/.
    One directory deeper, so prepend `../`."""
    rel = _obl_href_from_reference(record)
    return f"../{rel}" if rel else None


def _applies_to_display(entries):
    """Polymorphic renderer: handles legacy free-text entries and structured
    `[{role, file_pattern}]` entries (task ben/158 Phase 2b)."""
    out = []
    for e in entries or []:
        if isinstance(e, dict):
            role = e.get("role") or ""
            pat = e.get("file_pattern") or e.get("artifact_pattern") or ""
            out.append(f"{role}:{pat}" if role and pat else (pat or role))
        else:
            out.append(str(e))
    return ", ".join(out)


def render_master_table(records: list[dict]) -> str:
    """Render reference-dhf.md — one row per obligation.

    Title column (added by task ben/104) renders `title` field when present.
    ID column is a hyperlink to the source distillation's anchored record.
    """
    lines = [
        "# Reference DHF — Canonical Obligation Catalog",
        "",
        f"**Total obligations**: {len(records)}  ",
        "_Generated by build-reference.py — do not edit directly._",
        "",
        "| ID | Title | Source | Topic | Artifact Type | DHF Owner | Min IEC 62304 | Applies To |",
        "|----|-------|--------|-------|--------------|-----------|--------------|------------|",
    ]
    for r in records:
        applies = _applies_to_display(r.get("applies_to", []))
        oid = r.get("id", "")
        title = r.get("title", "") or ""
        href = _obl_href_from_reference(r)
        # ID cell = linked ID only (title is its own column here, not inlined).
        id_cell = f"[`{oid}`]({href})" if href else f"`{oid}`"
        lines.append(
            f"| {id_cell} "
            f"| {title} "
            f"| {r.get('source','')} "
            f"| {r.get('topic','')} "
            f"| {r.get('artifact_type','')} "
            f"| {r.get('dhf_owner','')} "
            f"| {r.get('min_iec62304_class') or '—'} "
            f"| {applies} |"
        )
    return "\n".join(lines) + "\n"


def render_dimension_doc(dimension: str, records: list[dict]) -> str:
    """Render one per-dimension filtered view."""
    dim_records = [
        r for r in records
        if any(
            (isinstance(sf, dict) and dimension in str(sf))
            or (isinstance(sf, str) and dimension in sf)
            for sf in r.get("scope_flags", [])
        )
        or (dimension == "common-baseline" and not r.get("scope_flags"))
    ]
    lines = [
        f"# Scope: {dimension} — DHF Obligations",
        "",
        f"**Obligations in this dimension**: {len(dim_records)}  ",
        "_Generated by build-reference.py — do not edit directly._",
        "",
    ]
    if not dim_records:
        lines.append("_No obligations tagged to this dimension yet._")
    else:
        lines += [
            "| ID | Title | Topic | Source | Applies To |",
            "|----|-------|-------|--------|------------|",
        ]
        for r in dim_records:
            applies = _applies_to_display(r.get("applies_to", []))
            oid = r.get("id", "")
            title = r.get("title", "") or ""
            href = _obl_href_from_dimension(r)
            id_cell = f"[`{oid}`]({href})" if href else f"`{oid}`"
            lines.append(
                f"| {id_cell} | {title} | {r.get('topic','')} "
                f"| {r.get('source','')} | {applies} |"
            )
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Aggregate regulatory distillations + emit per-source JSON sidecars.")
    parser.add_argument("--skill-dir", type=Path, default=None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    skill_dir = args.skill_dir or Path(__file__).parent.parent
    data_dir = skill_dir / "data"
    dim_dir = data_dir / "dimensions"

    if not data_dir.exists():
        print(f"ERROR: data directory not found: {data_dir}", file=sys.stderr)
        sys.exit(1)

    source_pairs = discover_source_files(data_dir)
    if not source_pairs:
        print(
            f"WARNING: No regulatory distillation files found under "
            f"{', '.join(CATEGORIES)}. Nothing to build.",
            file=sys.stderr,
        )
        sys.exit(0)

    counts_by_cat: dict[str, int] = defaultdict(int)
    for cat, _ in source_pairs:
        counts_by_cat[cat] += 1
    cat_summary = ", ".join(f"{c}={counts_by_cat[c]}" for c in CATEGORIES if counts_by_cat[c])
    print(f"Reading {len(source_pairs)} source files ({cat_summary})...")

    records, scope_schema, by_file = build_reference_dhf(data_dir)
    print(f"Collected {len(records)} obligation records.")

    # Phase 1 (task ben/104): title is optional; warn on missing so progress
    # toward Phase 3 (strict mode) is visible.
    missing_title = [r["id"] for r in records if not r.get("title")]
    if missing_title:
        print(
            f"  title field: {len(records) - len(missing_title)}/{len(records)} populated "
            f"({len(missing_title)} missing — run `validate.py` for full list).",
            file=sys.stderr,
        )

    outputs: dict[Path, str] = {
        data_dir / "reference-dhf.yml": yaml.dump(
            {"obligations": [{k: v for k, v in r.items() if not k.startswith("_")} | {"category": r.get("_category", "")} for r in records],
             "scope_schema": scope_schema},
            default_flow_style=False, allow_unicode=True, sort_keys=False,
        ),
        data_dir / "reference-dhf.md": render_master_table(records),
        data_dir / "scope-schema.yml": yaml.dump(scope_schema, default_flow_style=False),
    }
    for dim in SCOPE_DIMENSIONS:
        outputs[dim_dir / f"scope-{dim}.md"] = render_dimension_doc(dim, records)

    # Per-source JSON sidecars
    for md_path, recs in by_file.items():
        cat = md_path.parent.name
        json_path = md_path.with_suffix(".json")
        outputs[json_path] = render_source_json(cat, md_path, recs)

    if args.dry_run:
        for path in outputs:
            print(f"[dry-run] Would write: {path}")
        return

    dim_dir.mkdir(parents=True, exist_ok=True)
    for path, content in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        print(f"Wrote: {path.relative_to(skill_dir)}")

    print(
        f"\nDone. {len(records)} obligations across "
        f"{len(SCOPE_DIMENSIONS)} dimensions · {len(source_pairs)} sources "
        f"({cat_summary})."
    )


if __name__ == "__main__":
    main()
