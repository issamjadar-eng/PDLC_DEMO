#!/usr/bin/env python3
"""
build-manifest.py — Tier 4 Project DHF Manifest generator.

Projects Tier 3 Reference DHF through project.yml scope flags + per-item
classifications into a single manifest document with 4 DHF sections
(system suite + 3 item DHFs), each grouped by topic.

Usage:
    python3 build-manifest.py [--dry-run]

Exit codes:
    0  success
    1  required input not found (Tier 3 YAML or project.yml missing)
    2  project.yml parse error
"""

import sys
import json
import yaml
import argparse
from pathlib import Path
from datetime import date
from collections import defaultdict

from _linking import render_obl_link, render_qms_link, find_bare_ids

SCRIPT_DIR = Path(__file__).parent
SKILL_DIR = SCRIPT_DIR.parent
PROJECT_ROOT = SKILL_DIR.parent.parent.parent

TIER3_YAML = SKILL_DIR / "data/reference-dhf.yml"
PROJECT_YML = PROJECT_ROOT / "project.yml"
OUTPUT_DIR = PROJECT_ROOT / "docs/project/dhf-manifest"
QMS_MANIFEST_JSON = OUTPUT_DIR / "qms-manifest.json"
# Tier 1 source dirs (categories mirror medtech-docs/references)
SOURCE_CATEGORIES = ["fda-guidance", "standards", "industry-frameworks"]
SOURCE_ROOT = SKILL_DIR / "data"

# IEC 62304 software safety class order (higher index = more strict)
CLASS_ORDER = {"A": 0, "B": 1, "C": 2}

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


# ─── Scope filtering ──────────────────────────────────────────────────────────

def scope_flag_active(flag: str, scope: dict, all_dhfs: list) -> bool:
    """Return True if the obligation scope_flag is active for this project."""
    any_ai = any(
        d.get("classification", {}).get("ai_enabled", False)
        for d in all_dhfs if d.get("role") == "item"
    )
    has_pccp = any("pccp" in str(d.get("filing", "")) for d in all_dhfs)

    mapping = {
        "ai": any_ai,
        "pccp": has_pccp,
        "510k": True,
        "hardware": scope.get("hardware", False),
        "software": True,
        "multi-function": scope.get("multi_function_device", False),
        "cybersecurity": True,
        "usability-hf": scope.get("usability_hf", True),
        "tool-validation": scope.get("tool_validation", False),
        "clinical": bool(scope.get("clinical_evaluation")),
        "post-market": True,
        "common-baseline": True,
    }
    # Unknown flags are conservatively included (forward-compatible)
    return mapping.get(flag, True)


def obligation_in_scope(obl: dict, scope: dict, all_dhfs: list) -> bool:
    """True if ALL scope_flags on the obligation are active for this project.

    scope_flags entries may be:
      - str  → simple flag (e.g. 'pccp')
      - dict → conditional qualifier: {requires: [flag1, flag2]} means
               obligation applies only when ALL listed flags are active.
    """
    flags = obl.get("scope_flags", [])
    if not flags:
        return True
    for entry in flags:
        if isinstance(entry, str):
            if not scope_flag_active(entry, scope, all_dhfs):
                return False
        elif isinstance(entry, dict):
            # {requires: [flag1, flag2]} — all must be active
            required = entry.get("requires", [])
            if not all(scope_flag_active(f, scope, all_dhfs) for f in required if isinstance(f, str)):
                return False
        # Non-string, non-dict entries are skipped (conservative: include)
    return True


# ─── DHF routing ──────────────────────────────────────────────────────────────

def item_accepts(item: dict, obl: dict) -> bool:
    """True if this item DHF should receive this obligation."""
    cls = item.get("classification", {})
    # Normalise scope_flags to strings only (skip dict conditionals for per-item routing)
    str_flags = [f for f in obl.get("scope_flags", []) if isinstance(f, str)]

    # AI flag: only for AI-enabled items
    if "ai" in str_flags and not cls.get("ai_enabled", False):
        return False

    # PCCP flag: only for SaMD items (Management Services is NOT in PCCP)
    if "pccp" in str_flags and not cls.get("samd", False):
        return False

    # IEC 62304 class threshold: min_iec62304_class must be ≤ item class
    min_cls = obl.get("min_iec62304_class", "A")
    item_cls = cls.get("iec62304", "A")
    if CLASS_ORDER.get(min_cls, 0) > CLASS_ORDER.get(item_cls, 0):
        return False

    return True


def route_obligation(obl: dict, system_dhf: dict, item_dhfs: list) -> list[str]:
    """Return the list of DHF leaves this obligation routes to."""
    owner = obl.get("dhf_owner", "system")
    result = []
    if owner in ("system", "both"):
        result.append(system_dhf["leaf"])
    if owner in ("item", "both"):
        for item in item_dhfs:
            if item_accepts(item, obl):
                result.append(item["leaf"])
    return result


# ─── Grounding / link-target loaders ─────────────────────────────────────────

# Relative path from the manifest's folder (docs/project/dhf-manifest/) to the
# skill-owned regulatory-source data root. Per-source files live at
# <REGS_REL_FROM_OUTPUT>/<category>/<file>.md — resolved per-record via the
# anchor map's 'category' field.
# NOTE: relative paths do not currently resolve correctly through the project-
# console's hash-routed viewer (it treats the hash as opaque state, so
# `../..` resolves against `/documents`, not the rendered file's virtual path).
# Fix tracked in a separate task on the project-console side — do not switch
# this output to absolute /documents#path=... URLs without that fix landing.
REGS_REL_FROM_OUTPUT = "../../../.claude/skills/dhf-manifest/data"


def load_qms_grounding_map() -> dict:
    """Return {'obl_to_qms': {...}, 'qms_by_id': {...}, 'topic_to_qms': {...}} from qms-manifest.json.

    - obl_to_qms: OBL-xxx → list of QMS-xxx (direct regulatory_grounding matches)
    - qms_by_id:  QMS-xxx → {source, topic, applies_to, source_id, label}
                  (label is first extracted_requirement, truncated, for link text)
    - topic_to_qms: topic → [QMS-ids] (for fallback rendering)
    If qms-manifest.json is missing, returns empty maps (the QMS column will
    render as 'GAP'/'—').
    """
    if not QMS_MANIFEST_JSON.exists():
        print(
            f"WARNING: {QMS_MANIFEST_JSON} not found — QMS Grounding column will be empty. "
            f"Run `python3 build-qms.py` first.",
            file=sys.stderr,
        )
        return {"obl_to_qms": {}, "qms_by_id": {}, "topic_to_qms": {}}
    with open(QMS_MANIFEST_JSON) as f:
        data = json.load(f)
    qms_by_id: dict = {}
    for rec in data.get("qms_obligations", []):
        reqs = rec.get("extracted_requirements", []) or []
        first = reqs[0] if reqs else ""
        if isinstance(first, dict):
            first = "; ".join(f"{k}: {v}" for k, v in first.items())
        label = str(first).strip().strip('"')
        qms_by_id[rec["id"]] = {
            "source": rec.get("source", ""),
            "topic": rec.get("topic", ""),
            "applies_to": rec.get("applies_to", []),
            "source_id": _source_id_prefix(rec.get("source", "")),
            "label": label,
            "title": rec.get("title", ""),
        }
    topic_to_qms: dict = {}
    for topic, qids in (data.get("by_topic") or {}).items():
        topic_to_qms[topic] = list(qids)
    return {
        "obl_to_qms": dict(data.get("obl_to_qms") or {}),
        "qms_by_id": qms_by_id,
        "topic_to_qms": topic_to_qms,
    }


def _source_id_prefix(source_str: str) -> str:
    import re
    m = re.match(r"^(SOP|WI|FORM|POL|QSD|GUI|STD)[-\s]?(\d+)", source_str or "")
    return f"{m.group(1)}-{m.group(2)}" if m else ""


def load_tier1_anchor_map() -> dict:
    """Walk data/{fda-guidance,standards,industry-frameworks}/*.md and build
    {OBL-xxx: {'category', 'file', 'source', 'section'}}.

    Prefers the per-source JSON sidecar (faster + built output); falls back to
    MD regex-scan when the JSON doesn't exist yet.
    """
    import re, yaml  # noqa: F401
    result: dict = {}
    yaml_block_re = re.compile(r"```yaml\n(.*?)```", re.DOTALL)

    for category in SOURCE_CATEGORIES:
        cat_dir = SOURCE_ROOT / category
        if not cat_dir.exists():
            continue
        for md in cat_dir.glob("*.md"):
            if md.name.lower() == "readme.md":
                continue
            json_sidecar = md.with_suffix(".json")
            if json_sidecar.exists():
                try:
                    payload = json.loads(json_sidecar.read_text())
                    for obl in payload.get("obligations", []):
                        if "id" in obl:
                            result[obl["id"]] = {
                                "category": category,
                                "file": md.name,
                                "source": obl.get("source", ""),
                                "section": obl.get("section", ""),
                                "title": obl.get("title", ""),
                            }
                    continue
                except json.JSONDecodeError:
                    pass  # fall through to MD parse
            # MD fallback
            text = md.read_text(encoding="utf-8")
            for match in yaml_block_re.finditer(text):
                try:
                    rec = yaml.safe_load(match.group(1))
                except yaml.YAMLError:
                    continue
                if not isinstance(rec, dict) or "id" not in rec:
                    continue
                result[rec["id"]] = {
                    "category": category,
                    "file": md.name,
                    "source": rec.get("source", ""),
                    "section": rec.get("section", ""),
                    "title": rec.get("title", ""),
                }
    return result


# ─── Rendering ───────────────────────────────────────────────────────────────

def obligation_short(obl: dict) -> str:
    """Human-readable label for the obligation (first extracted requirement, full text).

    extracted_requirements entries may be strings or dicts (when the Tier 1 YAML
    uses 'key: value' notation for inline bullets). Flatten dicts to 'key: value'.
    No truncation — the reader should see the whole requirement without clicking.
    """
    reqs = obl.get("extracted_requirements", [])
    if reqs:
        first = reqs[0]
        if isinstance(first, dict):
            # Flatten: join all key: value pairs with '; '
            return "; ".join(f"{k}: {v}" for k, v in first.items())
        return str(first)
    return obl.get("section", obl.get("id", ""))


def safe_cell(text: str, max_len: int | None = None) -> str:
    """Pipe-escape for a markdown table cell. No truncation — `max_len` is
    kept for backwards-compat with older callers but ignored."""
    return str(text).replace("|", "\\|")


def render_reg_source_cell(obl: dict, tier1_anchors: dict) -> str:
    """Render the Reg Source column: deep link to Tier 1 distillation anchor.

    Format: `[<source_text>](<tier1_file>#OBL-xxx)` — falls back to plain text
    when the OBL id isn't found in the Tier 1 map.
    """
    oid = obl.get("id", "")
    display = safe_cell(obl.get("source", "—"), 80)
    anchor_info = tier1_anchors.get(oid)
    if not anchor_info:
        return display
    category = anchor_info.get("category", "")
    path_prefix = f"{REGS_REL_FROM_OUTPUT}/{category}" if category else REGS_REL_FROM_OUTPUT
    return f"[{display}]({path_prefix}/{anchor_info['file']}#{oid})"


def render_qms_grounding_cell(obl: dict, qms_map: dict) -> str:
    """Render the QMS Grounding column with linked QMS-IDs + short text labels.

    - Direct hits: `[QMS-RM-004](qms-manifest.md#qms-rm-004) — <label>; [QMS-RM-006](...) — <label>`
    - Fallback (topic match): `_topic: risk-management (N QMS)_`
    - None: `—`
    """
    oid = obl.get("id", "")
    direct: list[str] = qms_map.get("obl_to_qms", {}).get(oid, []) or []
    qms_by_id = qms_map.get("qms_by_id", {}) or {}
    if direct:
        seen, ordered = set(), []
        for q in direct:
            if q not in seen:
                seen.add(q)
                ordered.append(q)
        parts: list[str] = []
        for q in ordered:
            info = qms_by_id.get(q) or {}
            title = info.get("title", "") or ""
            label = info.get("label") or ""
            link = render_qms_link(q, title, f"qms-manifest.md#{q.lower()}")
            if label:
                parts.append(f"{link} — {safe_cell(label)}")
            else:
                parts.append(link)
        return "; ".join(parts)
    # Topic fallback
    topic = obl.get("topic", "")
    topic_qms = qms_map.get("topic_to_qms", {}).get(topic, []) or []
    if topic_qms:
        return f"_topic: `{topic}` ({len(topic_qms)} QMS)_"
    return "—"


def render_dhf_section(
    dhf: dict,
    obligations: list,
    tier1_anchors: dict,
    qms_map: dict,
) -> list[str]:
    leaf = dhf["leaf"]
    cls = dhf.get("classification", {})

    if dhf.get("role") == "system":
        subtitle = "System DHF — device-level, aggregates evidence from all item DHFs"
    else:
        parts = []
        parts.append("SaMD" if cls.get("samd") else "Non-SaMD")
        parts.append(f"IEC 62304 Class {cls.get('iec62304', '?')}")
        if cls.get("ai_enabled"):
            parts.append("AI-enabled")
        if leaf == "hiplink-intra-op":
            parts.append("tablet / offline-capable")
        subtitle = " · ".join(parts)

    lines = [
        f"## {leaf}",
        f"*{subtitle}*  ",
        f"**Obligations in this DHF**: {len(obligations)}",
        "",
    ]

    if not obligations:
        lines += [
            "_No obligations scoped to this DHF under the current project scope vector._",
            "",
        ]
        return lines

    # Group by topic in canonical order
    by_topic: dict[str, list] = defaultdict(list)
    for obl in obligations:
        by_topic[obl.get("topic", "other")].append(obl)

    sorted_topics = sorted(
        by_topic.keys(),
        key=lambda t: (TOPIC_ORDER.index(t) if t in TOPIC_ORDER else 99, t),
    )

    for topic in sorted_topics:
        topic_obls = by_topic[topic]
        topic_label = TOPIC_DISPLAY.get(topic, topic.replace("-", " ").title())
        lines += [
            f"### {topic_label} ({len(topic_obls)})",
            "",
            "| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |",
            "|----|-----------|---------------|------------------------|-----------|---------------|:------:|",
        ]
        for obl in topic_obls:
            oid = obl.get("id", "—")
            anchor = tier1_anchors.get(oid, {})
            title = anchor.get("title", "") or obl.get("title", "")
            href = None
            if anchor.get("category") and anchor.get("file"):
                href = f"{REGS_REL_FROM_OUTPUT}/{anchor['category']}/{anchor['file']}#{oid}"
            id_cell = render_obl_link(oid, title, href)
            short = safe_cell(obligation_short(obl))
            atype = obl.get("artifact_type", "—")
            applies = safe_cell("; ".join(obl.get("applies_to", ["—"])))
            reg_src = render_reg_source_cell(obl, tier1_anchors)
            qms_cell = render_qms_grounding_cell(obl, qms_map)
            lines.append(
                f"| {id_cell} | {short} | {atype} | {applies} "
                f"| {reg_src} | {qms_cell} | GAP |"
            )
        lines.append("")

    return lines


def render_manifest(
    project: dict,
    scope: dict,
    all_dhfs: list,
    system_dhf: dict,
    item_dhfs: list,
    dhf_obligations: dict,
    tier1_anchors: dict,
    qms_map: dict,
) -> str:
    today = date.today().isoformat()
    project_name = project.get("project", {}).get("name", "Project")

    any_ai = any(d.get("classification", {}).get("ai_enabled", False) for d in item_dhfs)
    has_pccp = any("pccp" in str(d.get("filing", "")) for d in all_dhfs)

    lines = [
        f"# {project_name} — DHF Project Manifest",
        "",
        f"**Generated**: {today}  ",
        "**Tier**: 4 — Project DHF Manifests (Tier 3 Reference DHF → scope-projected)  ",
        "**Status**: Initial — all obligations at `GAP` (no location binding yet)  ",
        "**Sections**: 1 per DHF (system suite + 3 item DHFs), obligations grouped by topic  ",
        "",
        "> Run `/dhf-manifest reproject` to scan the DHF tree and bind obligations to actual file paths.",
        "",
        "---",
        "",
        "## Scope Configuration",
        "",
        "| Scope Flag | Value | Derivation |",
        "|-----------|-------|------------|",
        f'| `510k` | true | `project.regulatory_pathway` |',
        f'| `pccp` | {"true" if has_pccp else "false"} | `dhfs[].filing` contains `pccp` |',
        f'| `ai` | {"true" if any_ai else "false"} | any `dhfs[].classification.ai_enabled` |',
        f'| `multi-function` | {"true" if scope.get("multi_function_device") else "false"} | `scope.multi_function_device` |',
        f'| `cybersecurity` | true | always in scope |',
        f'| `common-baseline` | true | always in scope |',
        f'| `usability-hf` | {"true" if scope.get("usability_hf") else "false"} | `scope.usability_hf` |',
        f'| `tool-validation` | {"true" if scope.get("tool_validation") else "false"} | `scope.tool_validation` |',
        f'| `hardware` | {"true" if scope.get("hardware") else "false"} | `scope.hardware` |',
        f'| `clinical` | {"true" if scope.get("clinical_evaluation") else "false"} | `scope.clinical_evaluation` |',
        f'| `post-market` | true | always in scope |',
        "",
        "**Per-item DHF classifications:**",
        "",
        "| DHF | Role | SaMD | IEC 62304 | AI | In PCCP |",
        "|-----|------|------|-----------|-----|---------|",
        f'| `{system_dhf["leaf"]}` | system | — | — | — | — |',
    ]

    for item in item_dhfs:
        cls = item.get("classification", {})
        in_pccp = cls.get("samd", False) and has_pccp
        lines.append(
            f'| `{item["leaf"]}` | item'
            f' | {"✓" if cls.get("samd") else "✗"}'
            f' | Class {cls.get("iec62304", "?")}'
            f' | {"✓" if cls.get("ai_enabled") else "✗"}'
            f' | {"✓" if in_pccp else "✗"} |'
        )

    lines += ["", "---", ""]

    # One section per DHF in project.yml order
    for dhf in all_dhfs:
        leaf = dhf["leaf"]
        obls = dhf_obligations.get(leaf, [])
        lines += render_dhf_section(dhf, obls, tier1_anchors, qms_map)
        lines += ["---", ""]

    # Summary
    lines += [
        "## Summary — Gap Analysis",
        "",
        "| DHF | Role | Obligations | GAP | FOUND |",
        "|-----|------|------------|-----|-------|",
    ]
    grand_total = 0
    for dhf in all_dhfs:
        leaf = dhf["leaf"]
        role = dhf.get("role", "item")
        count = len(dhf_obligations.get(leaf, []))
        grand_total += count
        lines.append(f"| `{leaf}` | {role} | {count} | {count} | 0 |")
    lines += [
        f"| **Total** | | **{grand_total}** | **{grand_total}** | **0** |",
        "",
        "_All statuses are `GAP` at initial generation. Run `/dhf-manifest reproject` after "
        "authoring DHF artifacts to update `FOUND` counts._",
        "",
    ]

    return "\n".join(lines)


def render_by_section_view(
    project: dict,
    all_dhfs: list,
    dhf_obligations: dict,
    tier1_anchors: dict,
    qms_map: dict,
) -> str:
    """View 2 — outer grouping by Topic → inner grouping by DHF.

    Makes SME review-by-domain trivial: a risk-management reviewer scrolls to
    the Risk Management section and sees every obligation across every DHF.
    """
    today = date.today().isoformat()
    project_name = project.get("project", {}).get("name", "Project")

    # Collect: topic → dhf_leaf → [obligations]
    topic_map: dict = defaultdict(lambda: defaultdict(list))
    for leaf, obls in dhf_obligations.items():
        for obl in obls:
            topic_map[obl.get("topic", "other")][leaf].append(obl)

    sorted_topics = sorted(
        topic_map.keys(),
        key=lambda t: (TOPIC_ORDER.index(t) if t in TOPIC_ORDER else 99, t),
    )
    ordered_leaves = [d["leaf"] for d in all_dhfs]

    lines = [
        f"# {project_name} — DHF Manifest (by Section)",
        "",
        f"**Generated**: {today}  ",
        "**View**: topic-first reading flow — for domain SME review  ",
        "**Companion views**: "
        "[`hiplink-manifest.md`](hiplink-manifest.md) (by DHF), "
        "[`hiplink-dashboard.md`](hiplink-dashboard.md) (status)  ",
        "",
        "> Same obligations as `hiplink-manifest.md`, reorganized so each DHF topic "
        "contains one subsection per DHF with that topic's obligations. Good for "
        "SME review by domain (Risk, Cyber, HF, V&V, etc.).",
        "",
        "---",
        "",
    ]
    for topic in sorted_topics:
        topic_label = TOPIC_DISPLAY.get(topic, topic.replace("-", " ").title())
        total_topic = sum(len(v) for v in topic_map[topic].values())
        lines += [
            f"## {topic_label} ({total_topic} across {len(topic_map[topic])} DHF{'s' if len(topic_map[topic])!=1 else ''})",
            "",
        ]
        for leaf in ordered_leaves:
            topic_obls = topic_map[topic].get(leaf, [])
            if not topic_obls:
                continue
            lines += [
                f"### `{leaf}` — {len(topic_obls)} obligation{'s' if len(topic_obls)!=1 else ''}",
                "",
                "| ID | Obligation | Artifact Type | Required Deliverable(s) | Reg Source | QMS Grounding | Status |",
                "|----|-----------|---------------|------------------------|-----------|---------------|:------:|",
            ]
            for obl in topic_obls:
                oid = obl.get("id", "—")
                anchor = tier1_anchors.get(oid, {})
                title = anchor.get("title", "") or obl.get("title", "")
                href = None
                if anchor.get("category") and anchor.get("file"):
                    href = f"{REGS_REL_FROM_OUTPUT}/{anchor['category']}/{anchor['file']}#{oid}"
                id_cell = render_obl_link(oid, title, href)
                short = safe_cell(obligation_short(obl))
                atype = obl.get("artifact_type", "—")
                applies = safe_cell("; ".join(obl.get("applies_to", ["—"])))
                reg_src = render_reg_source_cell(obl, tier1_anchors)
                qms_cell = render_qms_grounding_cell(obl, qms_map)
                lines.append(
                    f"| {id_cell} | {short} | {atype} | {applies} "
                    f"| {reg_src} | {qms_cell} | GAP |"
                )
            lines.append("")
        lines += ["---", ""]
    return "\n".join(lines)


# ─── Main ─────────────────────────────────────────────────────────────────────

def load_scope_overrides(override_strs: list[str]) -> dict:
    """Parse 'flag=value' strings into a scope-override dict."""
    overrides = {}
    for s in override_strs:
        if "=" not in s:
            print(f"WARNING: ignoring malformed scope override {s!r} (expected 'flag=value')", file=sys.stderr)
            continue
        key, _, val = s.partition("=")
        # Convert common boolean strings
        if val.lower() in ("true", "yes", "1"):
            overrides[key.replace("-", "_")] = True
        elif val.lower() in ("false", "no", "0"):
            overrides[key.replace("-", "_")] = False
        elif val.startswith("[") and val.endswith("]"):
            # List value: [us,eu]
            overrides[key.replace("-", "_")] = [v.strip() for v in val[1:-1].split(",") if v.strip()]
        else:
            overrides[key.replace("-", "_")] = val
    return overrides


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Tier 4 DHF Project Manifest")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print manifest to stdout, do not write files")
    parser.add_argument("--delta", action="store_true",
                        help="Diff new output against existing manifest JSON and report added/dropped/changed IDs")
    parser.add_argument("--scope", action="append", default=[], metavar="FLAG=VALUE",
                        help="Override a scope flag for this run (e.g. --scope hardware=true). "
                             "Implies --dry-run when used without --output.")
    args = parser.parse_args()

    if not TIER3_YAML.exists():
        print(f"ERROR: Tier 3 YAML not found: {TIER3_YAML}", file=sys.stderr)
        print("Run: python3 build-reference.py first", file=sys.stderr)
        return 1

    if not PROJECT_YML.exists():
        print(f"ERROR: project.yml not found: {PROJECT_YML}", file=sys.stderr)
        return 1

    with open(TIER3_YAML) as f:
        tier3 = yaml.safe_load(f)
    obligations: list = tier3.get("obligations", [])

    try:
        with open(PROJECT_YML) as f:
            project = yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(f"ERROR: project.yml parse error: {e}", file=sys.stderr)
        return 2

    scope = {**project.get("scope", {})}
    # Apply --scope overrides
    if args.scope:
        overrides = load_scope_overrides(args.scope)
        scope.update(overrides)
        if overrides:
            print(f"Scope overrides applied: {overrides}")

    all_dhfs: list = project.get("dhfs", [])
    system_dhf = next((d for d in all_dhfs if d.get("role") == "system"), None)
    item_dhfs = [d for d in all_dhfs if d.get("role") == "item"]

    if not system_dhf:
        print("ERROR: No system DHF (role: system) found in project.yml dhfs[]", file=sys.stderr)
        return 1

    # Project obligations through scope filter + DHF routing
    dhf_obligations: dict[str, list] = defaultdict(list)
    skipped = 0

    for obl in obligations:
        if not obligation_in_scope(obl, scope, all_dhfs):
            skipped += 1
            continue
        for leaf in route_obligation(obl, system_dhf, item_dhfs):
            dhf_obligations[leaf].append(obl)

    total_routed = sum(len(v) for v in dhf_obligations.values())

    # Load grounding + anchor maps for enriched columns
    qms_map = load_qms_grounding_map()
    tier1_anchors = load_tier1_anchor_map()

    md_content = render_manifest(
        project, scope, all_dhfs, system_dhf, item_dhfs, dhf_obligations,
        tier1_anchors, qms_map,
    )
    by_section_content = render_by_section_view(
        project, all_dhfs, dhf_obligations, tier1_anchors, qms_map,
    )

    def _entry_json(o: dict) -> dict:
        oid = o["id"]
        a_info = tier1_anchors.get(oid, {})
        direct_qms = qms_map.get("obl_to_qms", {}).get(oid, []) or []
        topic = o.get("topic", "")
        topic_qms = qms_map.get("topic_to_qms", {}).get(topic, []) or []
        return {
            "id": oid,
            "title": o.get("title", "") or a_info.get("title", ""),
            "topic": topic,
            "artifact_type": o.get("artifact_type"),
            "applies_to": o.get("applies_to", []),
            "dhf_owner": o.get("dhf_owner"),
            "source": o.get("source"),
            "reg_source": {
                "citation": o.get("source", ""),
                "category": a_info.get("category"),
                "source_file": a_info.get("file"),
                "anchor_url": (
                    f"{REGS_REL_FROM_OUTPUT}/{a_info['category']}/{a_info['file']}#{oid}"
                    if a_info else None
                ),
            },
            "qms_grounding": {
                "direct": list(direct_qms),
                "topic_fallback": {"topic": topic, "qms_count": len(topic_qms)} if not direct_qms else None,
            },
            "status": "GAP",
            "location": None,
        }

    json_content = json.dumps(
        {
            "generated": date.today().isoformat(),
            "source_obligations": len(obligations),
            "skipped_out_of_scope": skipped,
            "dhf_manifest": {
                leaf: [_entry_json(o) for o in obls]
                for leaf, obls in dhf_obligations.items()
            },
        },
        indent=2,
    )

    if args.dry_run or args.scope:
        print(md_content)
        return 0

    # --delta: diff new IDs against previously written manifest
    if args.delta and (OUTPUT_DIR / "hiplink-manifest.json").exists():
        try:
            old = json.loads((OUTPUT_DIR / "hiplink-manifest.json").read_text())
            old_ids: set[str] = set()
            for entries in old.get("dhf_manifest", {}).values():
                old_ids.update(e["id"] for e in entries)
            new_ids: set[str] = set()
            new_manifest_data = json.loads(json_content)
            for entries in new_manifest_data.get("dhf_manifest", {}).values():
                new_ids.update(e["id"] for e in entries)

            added = new_ids - old_ids
            dropped = old_ids - new_ids
            print(f"Reproject delta:")
            print(f"  Added  : {len(added)}" + (f" — {', '.join(sorted(added))}" if added else ""))
            print(f"  Dropped: {len(dropped)}" + (f" — {', '.join(sorted(dropped))}" if dropped else ""))
            if not added and not dropped:
                print("  No change.")
        except (json.JSONDecodeError, KeyError):
            pass  # Delta comparison failed — proceed with write

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "hiplink-manifest.md").write_text(md_content)
    (OUTPUT_DIR / "hiplink-manifest.json").write_text(json_content)
    (OUTPUT_DIR / "hiplink-by-section.md").write_text(by_section_content)

    direct_qms_count = sum(
        1 for leaf_obls in dhf_obligations.values()
        for o in leaf_obls
        if qms_map.get("obl_to_qms", {}).get(o["id"])
    )

    print(f"DHF Project Manifest — done.")
    print(f"  Source obligations : {len(obligations)}")
    print(f"  Skipped (scope)    : {skipped}")
    print(f"  Total routed       : {total_routed}")
    for dhf in all_dhfs:
        leaf = dhf["leaf"]
        count = len(dhf_obligations.get(leaf, []))
        print(f"    {leaf}: {count}")
    print(f"  Tier 1 anchors     : {len(tier1_anchors)}")
    print(f"  Direct QMS hits    : {direct_qms_count} / {total_routed}")
    print(f"  Output: {OUTPUT_DIR}/hiplink-manifest.{{md,json}}, hiplink-by-section.md")

    # Post-build bare-ID check (task 104 Phase 4) — every ID in rendered
    # dashboards must be inside a markdown link. Zero tolerance.
    bare_findings: list[tuple[str, int, str, str]] = []
    for md_path in [
        OUTPUT_DIR / "hiplink-manifest.md",
        OUTPUT_DIR / "hiplink-by-section.md",
    ]:
        if not md_path.exists():
            continue
        content = md_path.read_text(encoding="utf-8")
        for lineno, ident, snippet in find_bare_ids(content):
            bare_findings.append((str(md_path.name), lineno, ident, snippet))
    if bare_findings:
        print(f"\n  ✗ POST-BUILD CHECK FAILED: {len(bare_findings)} bare ID(s) found")
        for fname, lineno, ident, snippet in bare_findings[:20]:
            print(f"    {fname}:{lineno}  {ident}  — {snippet}")
        if len(bare_findings) > 20:
            print(f"    ... and {len(bare_findings) - 20} more")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
