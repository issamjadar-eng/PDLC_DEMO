#!/usr/bin/env python3
"""
gap-report.py — Per-DHF gap summary from Tier 4 manifest.

Reads the Tier 4 manifest JSON, groups GAP entries by DHF and topic,
and emits a gap-report.md showing what artifacts are missing.

Usage:
    python3 gap-report.py [--output PATH]

Exit codes:
    0  report generated (even if all GAP — that is informational, not an error)
    1  Tier 4 manifest not found or parse error
"""

import sys
import json
import yaml
import argparse
from pathlib import Path
from datetime import date
from collections import defaultdict

SCRIPT_DIR = Path(__file__).parent
SKILL_DIR = SCRIPT_DIR.parent
PROJECT_ROOT = SKILL_DIR.parent.parent.parent

TIER4_JSON = PROJECT_ROOT / "docs/project/dhf-manifest/hiplink-manifest.json"
TIER3_YAML = SKILL_DIR / "data/tier3-reference/reference-dhf.yml"
DEFAULT_OUTPUT = PROJECT_ROOT / "docs/project/dhf-manifest/gap-report.md"

TOPIC_DISPLAY = {
    "architecture": "Architecture",
    "requirements": "Requirements",
    "design-outputs": "Design Outputs",
    "traceability": "Traceability",
    "risk-management": "Risk Management",
    "verification": "Verification",
    "validation": "Validation",
    "software-lifecycle": "Software Lifecycle",
    "configuration-change": "Configuration & Change Control",
    "design-reviews": "Design Reviews",
    "labeling-ifu": "Labeling & IFU",
    "human-factors": "Human Factors",
    "cybersecurity": "Cybersecurity",
    "clinical": "Clinical",
    "post-market": "Post-Market",
    "regulatory-submission": "Regulatory Submission",
}

TOPIC_ORDER = list(TOPIC_DISPLAY.keys())


def load_tier3_source_map() -> dict[str, dict]:
    """Return a map of obligation id → {applies_to, source} for richer gap rows."""
    if not TIER3_YAML.exists():
        return {}
    with open(TIER3_YAML) as f:
        data = yaml.safe_load(f)
    return {
        o["id"]: {
            "applies_to": o.get("applies_to", []),
            "source": o.get("source", ""),
            "section": o.get("section", ""),
            "artifact_type": o.get("artifact_type", ""),
        }
        for o in data.get("obligations", [])
        if "id" in o
    }


def render_gap_report(tier4: dict, tier3_map: dict) -> str:
    today = date.today().isoformat()
    generated = tier4.get("generated", "unknown")
    source_count = tier4.get("source_obligations", 0)
    skipped = tier4.get("skipped_out_of_scope", 0)

    dhf_manifest = tier4.get("dhf_manifest", {})

    # Compute per-DHF stats
    dhf_stats = {}
    for dhf_leaf, entries in dhf_manifest.items():
        total = len(entries)
        gaps = [e for e in entries if e.get("status") == "GAP" and e.get("location") is None]
        found = total - len(gaps)
        dhf_stats[dhf_leaf] = {"total": total, "gap": len(gaps), "found": found, "gap_entries": gaps}

    grand_total = sum(s["total"] for s in dhf_stats.values())
    grand_gap = sum(s["gap"] for s in dhf_stats.values())
    grand_found = sum(s["found"] for s in dhf_stats.values())
    pct_complete = round(100 * grand_found / grand_total, 1) if grand_total else 0

    lines = [
        "# HipLink DHF — Gap Report",
        "",
        f"**Generated**: {today}  ",
        f"**Manifest date**: {generated}  ",
        f"**Scope**: {source_count} total obligations ({skipped} out-of-scope), {grand_total} routed entries  ",
        f"**Overall**: {grand_found}/{grand_total} bound ({pct_complete}%) — {grand_gap} GAP  ",
        "",
        "> `GAP` = obligation in scope but no DHF artifact bound to it yet.  ",
        "> Run `/dhf-manifest reproject` after authoring artifacts to update.",
        "",
        "---",
        "",
        "## Summary",
        "",
        "| DHF | Total | FOUND | GAP | % Complete |",
        "|-----|-------|-------|-----|-----------|",
    ]

    for dhf_leaf, stats in dhf_stats.items():
        pct = round(100 * stats["found"] / stats["total"], 1) if stats["total"] else 0
        lines.append(
            f"| `{dhf_leaf}` | {stats['total']} | {stats['found']} | {stats['gap']} | {pct}% |"
        )
    lines += [
        f"| **Total** | **{grand_total}** | **{grand_found}** | **{grand_gap}** | **{pct_complete}%** |",
        "",
        "---",
        "",
    ]

    # Per-DHF sections
    for dhf_leaf, stats in dhf_stats.items():
        gap_entries = stats["gap_entries"]
        lines += [
            f"## {dhf_leaf} — {stats['gap']} GAP / {stats['total']} total",
            "",
        ]

        if not gap_entries:
            lines += ["_No gaps — all obligations are bound._", "", "---", ""]
            continue

        # Group gaps by topic
        by_topic: dict[str, list] = defaultdict(list)
        for entry in gap_entries:
            topic = entry.get("topic", "other")
            by_topic[topic].append(entry)

        sorted_topics = sorted(
            by_topic.keys(),
            key=lambda t: (TOPIC_ORDER.index(t) if t in TOPIC_ORDER else 99, t),
        )

        for topic in sorted_topics:
            topic_entries = by_topic[topic]
            topic_label = TOPIC_DISPLAY.get(topic, topic.replace("-", " ").title())
            lines += [
                f"### {topic_label} ({len(topic_entries)} gap{'s' if len(topic_entries) != 1 else ''})",
                "",
                "| ID | Artifact Type | Required Deliverable(s) | Source |",
                "|----|--------------|------------------------|--------|",
            ]
            for entry in topic_entries:
                eid = entry.get("id", "—")
                # Enrich from Tier 3 if available
                t3 = tier3_map.get(eid, {})
                atype = entry.get("artifact_type") or t3.get("artifact_type", "—")
                applies = "; ".join(
                    entry.get("applies_to") or t3.get("applies_to", ["—"])
                ).replace("|", "\\|")[:120]
                source = (t3.get("source") or entry.get("source") or "—").replace("|", "\\|")[:80]
                lines.append(f"| `{eid}` | {atype} | {applies} | {source} |")
            lines.append("")

        lines += ["---", ""]

    # Topic cross-DHF summary
    lines += [
        "## Gaps by Topic (across all DHFs)",
        "",
        "| Topic | Total GAP | DHFs affected |",
        "|-------|----------|--------------|",
    ]
    all_gaps_by_topic: dict[str, set] = defaultdict(set)
    for dhf_leaf, stats in dhf_stats.items():
        for entry in stats["gap_entries"]:
            topic = entry.get("topic", "other")
            all_gaps_by_topic[topic].add(dhf_leaf)

    sorted_t = sorted(
        all_gaps_by_topic.items(),
        key=lambda kv: (-len(kv[1]), TOPIC_ORDER.index(kv[0]) if kv[0] in TOPIC_ORDER else 99),
    )
    for topic, dhfs in sorted_t:
        topic_label = TOPIC_DISPLAY.get(topic, topic.replace("-", " ").title())
        # Count total gap entries for this topic
        total = sum(
            len([e for e in dhf_stats[dhf]["gap_entries"] if e.get("topic") == topic])
            for dhf in dhfs
        )
        lines.append(f"| {topic_label} | {total} | {', '.join(f'`{d}`' for d in sorted(dhfs))} |")
    lines.append("")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate DHF manifest gap report")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT),
                        help=f"Output path (default: {DEFAULT_OUTPUT})")
    args = parser.parse_args()

    if not TIER4_JSON.exists():
        print(f"ERROR: Tier 4 manifest not found: {TIER4_JSON}", file=sys.stderr)
        print("Run: python3 build-manifest.py first", file=sys.stderr)
        return 1

    try:
        with open(TIER4_JSON) as f:
            tier4 = json.load(f)
    except json.JSONDecodeError as e:
        print(f"ERROR: Tier 4 manifest parse error: {e}", file=sys.stderr)
        return 1

    tier3_map = load_tier3_source_map()

    content = render_gap_report(tier4, tier3_map)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content)

    # Print summary to stdout
    dhf_manifest = tier4.get("dhf_manifest", {})
    total = sum(len(v) for v in dhf_manifest.values())
    gap = sum(len([e for e in v if e.get("status") == "GAP"]) for v in dhf_manifest.values())
    pct = round(100 * (total - gap) / total, 1) if total else 0

    print(f"Gap report: {total} routed obligations | {gap} GAP ({100 - pct:.1f}% unbound)")
    for dhf_leaf, entries in dhf_manifest.items():
        dhf_gap = len([e for e in entries if e.get("status") == "GAP"])
        print(f"  {dhf_leaf}: {dhf_gap}/{len(entries)} GAP")
    print(f"Output: {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
