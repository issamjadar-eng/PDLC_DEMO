#!/usr/bin/env python3
"""
dashboard.py — View 3 status dashboard for the DHF Manifest.

Reads the project's `<project-slug>-dhf-manifest.json` (slug derived from
project.yml — see _project_slug.py), summarises per-DHF status (GAP /
FOUND) and QMS coverage (direct / topic-only / none) per topic. Replaces
gap-report.md with a status-first view that answers "what have we
authored, and what's the coverage story."

Output: `docs/project/dhf-manifest/<project-slug>-dhf-dashboard.md`.
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import date
from collections import defaultdict

from _project_slug import project_slug, manifest_filename, project_display_name

SCRIPT_DIR = Path(__file__).parent
SKILL_DIR = SCRIPT_DIR.parent
PROJECT_ROOT = SKILL_DIR.parent.parent.parent

PROJECT_SLUG = project_slug(PROJECT_ROOT)
PROJECT_NAME = project_display_name(PROJECT_ROOT)
MANIFEST_MD_NAME = manifest_filename(PROJECT_SLUG, "manifest.md")
MANIFEST_JSON_NAME = manifest_filename(PROJECT_SLUG, "manifest.json")
BY_SECTION_MD_NAME = manifest_filename(PROJECT_SLUG, "by-section.md")
DASHBOARD_MD_NAME = manifest_filename(PROJECT_SLUG, "dashboard.md")

TIER4_JSON = PROJECT_ROOT / "docs/project/dhf-manifest" / MANIFEST_JSON_NAME
DEFAULT_OUTPUT = PROJECT_ROOT / "docs/project/dhf-manifest" / DASHBOARD_MD_NAME

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


def bar(pct: float, width: int = 20) -> str:
    """Unicode progress bar (block glyphs)."""
    filled = max(0, min(width, int(round(pct / 100 * width))))
    return "█" * filled + "░" * (width - filled)


def entry_qms_class(entry: dict) -> str:
    """Classify a manifest entry's QMS grounding: direct / topic / none."""
    qms = entry.get("qms_grounding") or {}
    if qms.get("direct"):
        return "direct"
    fb = qms.get("topic_fallback") or {}
    if fb.get("qms_count"):
        return "topic"
    return "none"


def entry_bound(entry: dict) -> bool:
    """A DHF entry is bound when it has status != GAP and a location path."""
    return entry.get("status") != "GAP" and entry.get("location")


def render_dashboard(tier4: dict) -> str:
    today = date.today().isoformat()
    generated = tier4.get("generated", "unknown")
    dhf_manifest = tier4.get("dhf_manifest", {})
    source_count = tier4.get("source_obligations", 0)
    skipped = tier4.get("skipped_out_of_scope", 0)

    # Per-DHF summary stats
    dhf_stats = {}
    for leaf, entries in dhf_manifest.items():
        total = len(entries)
        bound = sum(1 for e in entries if entry_bound(e))
        qms_direct = sum(1 for e in entries if entry_qms_class(e) == "direct")
        qms_topic = sum(1 for e in entries if entry_qms_class(e) == "topic")
        qms_none = sum(1 for e in entries if entry_qms_class(e) == "none")
        dhf_stats[leaf] = {
            "total": total,
            "bound": bound,
            "gap": total - bound,
            "qms_direct": qms_direct,
            "qms_topic": qms_topic,
            "qms_none": qms_none,
            "entries": entries,
        }

    grand_total = sum(s["total"] for s in dhf_stats.values())
    grand_bound = sum(s["bound"] for s in dhf_stats.values())
    grand_direct = sum(s["qms_direct"] for s in dhf_stats.values())
    grand_topic = sum(s["qms_topic"] for s in dhf_stats.values())
    grand_none = sum(s["qms_none"] for s in dhf_stats.values())
    pct_bound = round(100 * grand_bound / grand_total, 1) if grand_total else 0
    pct_direct = round(100 * grand_direct / grand_total, 1) if grand_total else 0

    lines = [
        f"# {PROJECT_NAME} DHF — Dashboard",
        "",
        f"**Generated**: {today}  ",
        f"**Manifest date**: {generated}  ",
        f"**Scope**: {source_count} source obligations ({skipped} out-of-scope), "
        f"{grand_total} routed entries across {len(dhf_manifest)} DHFs  ",
        "",
        "> Two questions answered here:  ",
        "> 1. **Authoring status** — how much of the DHF have we built? (GAP vs FOUND)  ",
        "> 2. **QMS coverage** — of the obligations scoped to each DHF, how many "
        "have a direct QMS procedure (green), only a topic-level fallback (yellow), "
        "or no grounding at all (red)?",
        "",
        f"Companion views: [`{MANIFEST_MD_NAME}`]({MANIFEST_MD_NAME}) (by DHF), "
        f"[`{BY_SECTION_MD_NAME}`]({BY_SECTION_MD_NAME}) (by topic).",
        "",
        "---",
        "",
        "## Overall",
        "",
        f"- **Authoring**: `{bar(pct_bound)}` {grand_bound}/{grand_total} bound ({pct_bound}%)",
        f"- **QMS coverage**: `{bar(pct_direct)}` {grand_direct}/{grand_total} direct ({pct_direct}%) · "
        f"{grand_topic} topic-only · {grand_none} no-grounding",
        "",
        "---",
        "",
        "## Per-DHF",
        "",
        "| DHF | Obligations | Bound (FOUND) | GAP | QMS direct | QMS topic-only | No grounding |",
        "|-----|------------|---------------|-----|-----------|---------------|--------------|",
    ]
    for leaf, s in dhf_stats.items():
        pct = round(100 * s["bound"] / s["total"], 1) if s["total"] else 0
        pct_d = round(100 * s["qms_direct"] / s["total"], 1) if s["total"] else 0
        lines.append(
            f"| `{leaf}` | {s['total']} "
            f"| {s['bound']} ({pct}%) "
            f"| {s['gap']} "
            f"| {s['qms_direct']} ({pct_d}%) "
            f"| {s['qms_topic']} "
            f"| {s['qms_none']} |"
        )
    lines += ["", "---", ""]

    # Per-DHF per-topic breakdown
    for leaf, s in dhf_stats.items():
        entries = s["entries"]
        by_topic: dict = defaultdict(list)
        for e in entries:
            by_topic[e.get("topic", "other")].append(e)

        sorted_topics = sorted(
            by_topic.keys(),
            key=lambda t: (TOPIC_ORDER.index(t) if t in TOPIC_ORDER else 99, t),
        )

        lines += [
            f"## `{leaf}` — topic coverage",
            "",
            "| Topic | Obligations | Bound | QMS direct | QMS topic-only | No grounding |",
            "|-------|------------|-------|-----------|---------------|--------------|",
        ]
        for topic in sorted_topics:
            t_entries = by_topic[topic]
            total_t = len(t_entries)
            bound_t = sum(1 for e in t_entries if entry_bound(e))
            direct_t = sum(1 for e in t_entries if entry_qms_class(e) == "direct")
            topic_t = sum(1 for e in t_entries if entry_qms_class(e) == "topic")
            none_t = sum(1 for e in t_entries if entry_qms_class(e) == "none")
            label = TOPIC_DISPLAY.get(topic, topic.replace("-", " ").title())
            lines.append(
                f"| {label} | {total_t} "
                f"| {bound_t} "
                f"| {direct_t} "
                f"| {topic_t} "
                f"| {none_t} |"
            )
        lines += ["", "---", ""]

    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Build DHF manifest dashboard")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args()

    if not TIER4_JSON.exists():
        print(f"ERROR: manifest JSON not found: {TIER4_JSON}", file=sys.stderr)
        print("Run: python3 build-manifest.py first", file=sys.stderr)
        return 1
    try:
        tier4 = json.loads(TIER4_JSON.read_text())
    except json.JSONDecodeError as e:
        print(f"ERROR: manifest JSON parse error: {e}", file=sys.stderr)
        return 1

    content = render_dashboard(tier4)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(content)

    grand = sum(len(v) for v in tier4.get("dhf_manifest", {}).values())
    print(f"Dashboard: {grand} routed obligations summarized → {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
