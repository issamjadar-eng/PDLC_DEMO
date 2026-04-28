#!/usr/bin/env python3
"""
validate.py — Tier 1–4 structural compliance checks for /dhf-manifest.

Checks are deterministic (no LLM). Reads Tier 1 source files, Tier 3
reference YAML, and Tier 4 manifest JSON.

Usage:
    python3 validate.py [--quiet]

Exit codes:
    0  all checks passed (or only warnings)
    1  one or more FAIL checks
    2  fatal input error (missing required file, parse error)
"""

import sys
import json
import yaml
import argparse
from pathlib import Path
from collections import Counter

SCRIPT_DIR = Path(__file__).parent
SKILL_DIR = SCRIPT_DIR.parent
PROJECT_ROOT = SKILL_DIR.parent.parent.parent

from _project_slug import project_slug, manifest_filename

SOURCE_CATEGORIES = ["fda-guidance", "standards", "industry-frameworks"]
SOURCE_ROOT = SKILL_DIR / "data"
TIER3_YAML = SKILL_DIR / "data/reference-dhf.yml"

PROJECT_SLUG = project_slug(PROJECT_ROOT)
MANIFEST_JSON_NAME = manifest_filename(PROJECT_SLUG, "manifest.json")
TIER4_JSON = PROJECT_ROOT / "docs/project/dhf-manifest" / MANIFEST_JSON_NAME

VALID_TOPICS = {
    "architecture", "requirements", "design-outputs", "traceability",
    "risk-management", "verification", "validation", "software-lifecycle",
    "configuration-change", "design-reviews", "labeling-ifu", "human-factors",
    "cybersecurity", "clinical", "post-market", "regulatory-submission",
}

VALID_DHF_OWNERS = {"system", "item", "both"}
VALID_IEC62304_CLASSES = {"A", "B", "C"}

KNOWN_SCOPE_FLAGS = {
    "ai", "pccp", "510k", "hardware", "software", "multi-function",
    "cybersecurity", "usability-hf", "tool-validation", "clinical",
    "post-market", "common-baseline",
}

REQUIRED_FIELDS = {
    "id", "title", "source", "topic", "artifact_type", "dhf_owner",
    "min_iec62304_class", "applies_to", "verbatim", "extracted_requirements",
}

# Task 104 Phase 4: strict title validation.
TITLE_MAX_LEN = 60


# ─── Check helpers ────────────────────────────────────────────────────────────

class Results:
    def __init__(self):
        self.checks = []

    def add(self, name: str, status: str, detail: str = ""):
        self.checks.append({"name": name, "status": status, "detail": detail})

    def passed(self) -> int:
        return sum(1 for c in self.checks if c["status"] == "PASS")

    def warnings(self) -> int:
        return sum(1 for c in self.checks if c["status"] == "WARN")

    def failures(self) -> int:
        return sum(1 for c in self.checks if c["status"] == "FAIL")

    def print_report(self, quiet: bool = False):
        for c in self.checks:
            status = c["status"]
            name = c["name"]
            detail = c["detail"]
            if quiet and status == "PASS":
                continue
            icon = {"PASS": "✓", "WARN": "⚠", "FAIL": "✗"}.get(status, "?")
            line = f"  {icon} [{status}] {name}"
            if detail:
                line += f"\n       {detail}"
            print(line)

        total = len(self.checks)
        print(f"\n  {self.passed()}/{total} passed | {self.warnings()} warnings | {self.failures()} failures")


def run_checks(quiet: bool) -> int:
    results = Results()

    # ── Check 1: regulatory source files exist across categories ────────────
    tier1_files: list[Path] = []
    cat_counts: dict[str, int] = {}
    for cat in SOURCE_CATEGORIES:
        cat_dir = SOURCE_ROOT / cat
        if not cat_dir.exists():
            cat_counts[cat] = 0
            continue
        files = [p for p in sorted(cat_dir.glob("*.md")) if p.name.lower() != "readme.md"]
        tier1_files.extend(files)
        cat_counts[cat] = len(files)
    summary = ", ".join(f"{k}={v}" for k, v in cat_counts.items())
    if tier1_files:
        results.add("Regulatory source files present", "PASS", f"{len(tier1_files)} total ({summary})")
    else:
        results.add("Regulatory source files present", "FAIL", f"No .md files under data/{{{','.join(SOURCE_CATEGORIES)}}}/")
        results.print_report(quiet)
        return 2

    # ── Check 2: Tier 3 YAML exists and parses ───────────────────────────────
    if not TIER3_YAML.exists():
        results.add("Tier 3 reference-dhf.yml exists", "FAIL",
                    "Run: python3 build-reference.py")
        results.print_report(quiet)
        return 2

    try:
        with open(TIER3_YAML) as f:
            tier3 = yaml.safe_load(f)
        obligations: list = tier3.get("obligations", [])
        results.add("Tier 3 YAML parseable", "PASS", f"{len(obligations)} obligations")
    except yaml.YAMLError as e:
        results.add("Tier 3 YAML parseable", "FAIL", str(e))
        results.print_report(quiet)
        return 2

    # ── Check 3: No duplicate IDs ─────────────────────────────────────────────
    id_counts = Counter(o.get("id", "") for o in obligations)
    dupes = {k: v for k, v in id_counts.items() if v > 1 or k == ""}
    if dupes:
        dupe_str = ", ".join(f"{k!r} (×{v})" for k, v in dupes.items())
        results.add("No duplicate obligation IDs", "FAIL", f"Duplicates: {dupe_str}")
    else:
        results.add("No duplicate obligation IDs", "PASS")

    # ── Check 4: Required fields present ─────────────────────────────────────
    missing_fields = []
    for obl in obligations:
        oid = obl.get("id", "<no-id>")
        for field in REQUIRED_FIELDS:
            if field not in obl or obl[field] is None:
                missing_fields.append(f"{oid}.{field}")
    if missing_fields:
        sample = missing_fields[:5]
        more = len(missing_fields) - len(sample)
        detail = "; ".join(sample) + (f" (+{more} more)" if more else "")
        results.add("Required fields present", "FAIL", detail)
    else:
        results.add("Required fields present", "PASS")

    # ── Check 4b: Tier 1 title quality (task 104 Phase 4 strict) ─────────────
    title_issues = []
    for obl in obligations:
        oid = obl.get("id", "<no-id>")
        title = obl.get("title")
        if title is None or not str(title).strip():
            title_issues.append(f"{oid}: empty")
            continue
        t = str(title).strip()
        if len(t) > TITLE_MAX_LEN:
            title_issues.append(f"{oid}: too long ({len(t)} > {TITLE_MAX_LEN})")
        if "|" in t:
            title_issues.append(f"{oid}: pipe char")
        if "[" in t and "](" in t:
            title_issues.append(f"{oid}: markdown link")
    if title_issues:
        sample = title_issues[:5]
        more = len(title_issues) - len(sample)
        detail = "; ".join(sample) + (f" (+{more} more)" if more else "")
        results.add("Tier 1 title quality", "FAIL", detail)
    else:
        results.add("Tier 1 title quality", "PASS", f"{len(obligations)} titles, ≤ {TITLE_MAX_LEN} chars")

    # ── Check 5: Valid topic values ───────────────────────────────────────────
    bad_topics = [
        f"{obl.get('id')}: {obl.get('topic')!r}"
        for obl in obligations
        if obl.get("topic") not in VALID_TOPICS
    ]
    if bad_topics:
        results.add("Valid topic values", "FAIL",
                    f"{len(bad_topics)} unknown topics: {'; '.join(bad_topics[:3])}")
    else:
        results.add("Valid topic values", "PASS")

    # ── Check 6: Valid dhf_owner values ──────────────────────────────────────
    bad_owners = [
        f"{obl.get('id')}: {obl.get('dhf_owner')!r}"
        for obl in obligations
        if obl.get("dhf_owner") not in VALID_DHF_OWNERS
    ]
    if bad_owners:
        results.add("Valid dhf_owner values", "FAIL",
                    f"{len(bad_owners)} unknown owners: {'; '.join(bad_owners[:3])}")
    else:
        results.add("Valid dhf_owner values", "PASS")

    # ── Check 7: Valid min_iec62304_class values ──────────────────────────────
    bad_classes = [
        f"{obl.get('id')}: {obl.get('min_iec62304_class')!r}"
        for obl in obligations
        if obl.get("min_iec62304_class") not in VALID_IEC62304_CLASSES
    ]
    if bad_classes:
        results.add("Valid min_iec62304_class", "FAIL",
                    f"{len(bad_classes)} unknown: {'; '.join(bad_classes[:3])}")
    else:
        results.add("Valid min_iec62304_class", "PASS")

    # ── Check 8: Scope flags are known dimensions ─────────────────────────────
    unknown_flags = []
    for obl in obligations:
        for entry in obl.get("scope_flags", []):
            if isinstance(entry, str) and entry not in KNOWN_SCOPE_FLAGS:
                unknown_flags.append(f"{obl.get('id')}: {entry!r}")
            elif isinstance(entry, dict):
                # {requires: [flag1, ...]} — validate inner flags
                for f in entry.get("requires", []):
                    if isinstance(f, str) and f not in KNOWN_SCOPE_FLAGS:
                        unknown_flags.append(f"{obl.get('id')}: requires:{f!r}")
    if unknown_flags:
        sample = unknown_flags[:5]
        more = len(unknown_flags) - len(sample)
        detail = "; ".join(sample) + (f" (+{more} more)" if more else "")
        results.add("Known scope flags", "WARN", f"Unrecognized flags (may need KNOWN_SCOPE_FLAGS update): {detail}")
    else:
        results.add("Known scope flags", "PASS")

    # ── Check 9: Tier 4 manifest JSON exists ─────────────────────────────────
    if not TIER4_JSON.exists():
        results.add("Tier 4 manifest JSON exists", "WARN",
                    "Run: python3 build-manifest.py (Tier 4 not yet generated)")
        results.print_report(quiet)
        return 1 if results.failures() > 0 else 0

    try:
        with open(TIER4_JSON) as f:
            tier4 = json.load(f)
        results.add("Tier 4 manifest JSON parseable", "PASS")
    except json.JSONDecodeError as e:
        results.add("Tier 4 manifest JSON parseable", "FAIL", str(e))
        results.print_report(quiet)
        return 2

    # ── Check 10: Tier 4 IDs are all in Tier 3 ────────────────────────────────
    tier3_ids = {o.get("id") for o in obligations}
    orphan_tier4_ids = []
    dhf_manifest = tier4.get("dhf_manifest", {})
    for dhf_leaf, entries in dhf_manifest.items():
        for entry in entries:
            eid = entry.get("id")
            if eid and eid not in tier3_ids:
                orphan_tier4_ids.append(f"{dhf_leaf}: {eid}")
    if orphan_tier4_ids:
        results.add("Tier 4 IDs match Tier 3", "FAIL",
                    f"{len(orphan_tier4_ids)} stale IDs — re-run build-manifest: "
                    + "; ".join(orphan_tier4_ids[:3]))
    else:
        total_t4 = sum(len(v) for v in dhf_manifest.values())
        results.add("Tier 4 IDs match Tier 3", "PASS",
                    f"{total_t4} routed entries, all IDs exist in Tier 3")

    # ── Check 11: Tier 4 source matches Tier 3 obligation count ──────────────
    t4_source_count = tier4.get("source_obligations", 0)
    if t4_source_count != len(obligations):
        results.add(
            "Tier 4 obligation count matches Tier 3",
            "WARN",
            f"Tier 3 has {len(obligations)} obligations; Tier 4 was built from {t4_source_count}. "
            "Re-run: python3 build-manifest.py",
        )
    else:
        results.add("Tier 4 obligation count matches Tier 3", "PASS",
                    f"{len(obligations)} obligations")

    # ── Print and exit ─────────────────────────────────────────────────────────
    results.print_report(quiet)
    return 1 if results.failures() > 0 else 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate /dhf-manifest tier structure")
    parser.add_argument("--quiet", action="store_true", help="Show only WARN and FAIL checks")
    args = parser.parse_args()

    print("DHF Manifest — Structural Validation")
    print(f"  Sources: {SOURCE_ROOT.relative_to(PROJECT_ROOT)}/{{{','.join(SOURCE_CATEGORIES)}}}")
    print(f"  Tier 3: {TIER3_YAML.relative_to(PROJECT_ROOT)}")
    print(f"  Tier 4: {TIER4_JSON.relative_to(PROJECT_ROOT) if TIER4_JSON.exists() else '(not yet generated)'}")
    print()

    return run_checks(args.quiet)


if __name__ == "__main__":
    sys.exit(main())
