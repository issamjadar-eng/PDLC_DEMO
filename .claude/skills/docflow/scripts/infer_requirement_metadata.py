#!/usr/bin/env python3
"""
infer_requirement_metadata.py — parse R1 v22 requirement blocks and emit
frontmatter `requirements:` aggregate.

For doc_type=requirement adopts, the body structurer agent emits N H4 blocks
each with:
  - `#### <Key> — <Summary>` heading
  - 6-column markdown attributes table (Key | Traces To | Epic | Classification
    | Target | Status)
  - 3-column inline HTML detail table (Field | Value | Criticality) with
    Description row + per-AC rows

This script:
  1. Parses those blocks from a structured MD body
  2. Computes the document-wide `requirements:` aggregate (counts, distributions)
  3. Exposes the classification-taxonomy regex patterns as a library call
     `classify_text(text) -> set[str]` so the structurer agent can consume them
     deterministically via `python3 -m infer_requirement_metadata classify <text>`
     if needed

Library entry points:
  parse_blocks(body_text) -> list[Block]
  aggregate(blocks) -> dict
  classify_text(text) -> list[str]        # 9-tag canonical classification
  infer_criticality(ac_text) -> str       # CtS/CtC/CtP/none (never CtF)

CLI:
  infer_requirement_metadata.py aggregate <body-md-path>
      → print the `requirements:` aggregate as YAML on stdout
  infer_requirement_metadata.py classify "<text>"
      → print matched tags one per line
  infer_requirement_metadata.py --self-test
      → run embedded tests against the canonical Pre-Op SRS MD

No third-party deps.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Canonical classification taxonomy (from references/classification-taxonomy.md)
# ---------------------------------------------------------------------------
# The regex strings here MUST stay in lockstep with references/classification-
# taxonomy.md. If you change one, change both. `functional` is always added.

_CLASSIFICATION_PATTERNS: list[tuple[str, str]] = [
    ("safety",
     r"\b(hazard\w*|harm\w*|injur\w*|adverse event|risk control|mitigat\w*|patient safety|use.?safety|hazardous situation)\b"),
    ("security",
     r"\b(encrypt\w*|authentic\w*|authoriz\w*|token\w*|credential\w*|session|permission\w*|access control|audit log|cybersec\w*|vulnerab\w*|tamper\w*|SPDF|threat model)\b"),
    ("privacy",
     r"\b(PHI|PII|patient privacy|data protection|consent\w*|data subject|HIPAA|GDPR|anonymiz\w*|pseudonymiz\w*|de.?identif\w*)\b"),
    ("usability",
     r"\b(use.?error|human factor\w*|usability|ergonom\w*|clinical workflow|UX|UI.*clinical|alert\w*|warning message|confirm dialog)\b"),
    ("performance",
     r"\b(latency|throughput|response time|performance|speed|capacity|resource util\w*|concurrent users|load\w*|scale\w*)\b"),
    ("reliability",
     r"\b(availab\w*|failover|recover\w*|fault toler\w*|resilien\w*|uptime|redundan\w*|graceful degrad\w*|MTBF|backup\w*|restore\w*)\b"),
    ("interoperability",
     r"\b(DICOM|HL7|FHIR|IHE|interop\w*|integration profile|standard.*(compliance|conform\w*)|data exchange|LDAP)\b"),
    ("regulatory",
     r"\b(21.?CFR|Part.?11|audit trail\w*|electronic record\w*|ALCOA|MDR|GSPR|ISO.?13485|regulator\w*|compliance (check|requirement)\w*|traceability)\b"),
]

_COMPILED = [(tag, re.compile(pat, re.IGNORECASE)) for tag, pat in _CLASSIFICATION_PATTERNS]

_CANONICAL_TAGS = ["functional", "safety", "security", "privacy", "usability",
                   "performance", "reliability", "interoperability", "regulatory"]

_CRITICALITY_KEYS = ["CtF", "CtS", "CtC", "CtP", "none"]

_STATUS_KEYS = ["proposed", "accepted", "implemented", "verified",
                "deferred", "rejected", "superseded"]

_TARGET_KEYS = ["v1", "v2", "future", "unassigned"]


def classify_text(text: str) -> list[str]:
    """Apply the 9-tag canonical classification to `text`. `functional` is
    always included. Returns tags in the canonical order defined above."""
    matches = {"functional"}
    for tag, pat in _COMPILED:
        if pat.search(text):
            matches.add(tag)
    return [t for t in _CANONICAL_TAGS if t in matches]


def infer_criticality(ac_text: str) -> str:
    """Per-AC criticality inference. Returns one of CtS, CtC, CtP, or `none`.
    Never returns CtF — CtF requires human IFU assessment per R1b.
    Priority order (if multiple matches, the FIRST wins — conservative):
        safety → CtS
        regulatory → CtC
        performance → CtP
        otherwise → none
    """
    tags = set(classify_text(ac_text))
    if "safety" in tags:
        return "CtS"
    if "regulatory" in tags:
        return "CtC"
    if "performance" in tags:
        return "CtP"
    return "none"


# ---------------------------------------------------------------------------
# R1 block parsing
# ---------------------------------------------------------------------------

_H4_RE = re.compile(r"^####\s+(.+?)\s+—\s+(.+)\s*$", re.MULTILINE)
_ATTR_HEADER_RE = re.compile(
    r"^\|\s*Key\s*\|\s*Traces To\s*\|\s*Epic\s*\|\s*Classification\s*\|\s*Target\s*\|\s*Status\s*\|",
    re.IGNORECASE | re.MULTILINE,
)
_DETAIL_TABLE_RE = re.compile(r"<table>.*?</table>", re.DOTALL)
_INFERRED_RE = re.compile(r"\(inferred\)", re.IGNORECASE)
_CTX_TAG_RE = re.compile(r"`(CtF|CtS|CtC|CtP|none)`")
_CLASS_TAG_RE = re.compile(r"`([a-z]+)`")
_BACKTICK_STRIP_RE = re.compile(r"^\s*`?(.*?)`?\s*$")
_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
# Tolerant-to-nested-brackets variant (greedy anchor up to last `](url)`):
_LINK_RE_GREEDY = re.compile(r"^\[(.+)\]\(([^)]+)\)$", re.DOTALL)


@dataclass
class Block:
    key_raw: str                    # as rendered in heading (may include backticks or link)
    key: str                        # plain id (e.g. "AFAI-4083")
    summary: str
    # Attributes table cells (stripped of inline-code formatting):
    traces_to: Optional[str] = None
    traces_to_resolved: bool = False
    epic: Optional[str] = None
    classification: list[str] = field(default_factory=list)
    classification_inferred: bool = False
    target: str = "unassigned"
    status: str = "proposed"
    # Detail table:
    description_text: str = ""
    ac_texts: list[str] = field(default_factory=list)  # per-AC value cell text
    description_criticality: list[str] = field(default_factory=list)
    description_criticality_inferred: bool = False
    ac_criticalities: list[tuple[list[str], bool]] = field(default_factory=list)  # (tags, inferred)
    # Raw spans for inspection / rewriting:
    attr_row_raw: str = ""
    detail_table_raw: str = ""
    has_attrs: bool = False
    has_detail: bool = False


def _strip_link(text: str) -> str:
    """If `text` is a single `[a](u)` link, return `a`. Tolerant of `]` inside
    the anchor text (e.g. `[DI-0013 MEASUREMENTS [UNITY]](url)`)."""
    s = text.strip()
    m = _LINK_RE_GREEDY.match(s)
    if m:
        return m.group(1)
    m = _LINK_RE.fullmatch(s)
    return m.group(1) if m else s


def _strip_inline_code(text: str) -> str:
    """Strip surrounding backticks, plus inferred suffix, plus link wrap."""
    t = text.strip()
    t = re.sub(r"\s*\(inferred\)\s*$", "", t, flags=re.IGNORECASE).strip()
    t = _strip_link(t)
    m = _BACKTICK_STRIP_RE.match(t)
    return m.group(1).strip() if m else t


def _primary_section(cell: str) -> str:
    """R1b cells follow the shape `tag1`, `tag2` [(inferred)][<br>_rationale_].
    Return only the tag section (everything before the rationale). Rationale
    may itself contain backticked candidate CtX / classification tags that
    must NOT be counted as primary values."""
    # Cut at first `<br>_` or bare `_` starting italic rationale
    cut_points = []
    for marker in ("<br>_", "<br>\n_", "<br/>_", "\n_", "<br>\n\n_"):
        idx = cell.find(marker)
        if idx != -1:
            cut_points.append(idx)
    # Also cut at "(inferred)" if it precedes rationale (rationale is optional)
    m = _INFERRED_RE.search(cell)
    if m:
        # Include "(inferred)" itself in the prefix (it doesn't contain tags)
        cut_points.append(m.end())
    if cut_points:
        return cell[:min(cut_points)]
    return cell


def _parse_classification_cell(cell: str) -> tuple[list[str], bool]:
    """Return (tags, inferred_flag) from a Classification cell."""
    inferred = bool(_INFERRED_RE.search(cell))
    primary = _primary_section(cell)
    tags = [m.group(1) for m in _CLASS_TAG_RE.finditer(primary)]
    seen = set(tags)
    ordered = [t for t in _CANONICAL_TAGS if t in seen]
    return ordered, inferred


def _parse_criticality_cell(cell: str) -> tuple[list[str], bool]:
    """Return (tags, inferred_flag) from a Criticality cell — primary tags
    only (rationale-section candidate mentions are excluded)."""
    inferred = bool(_INFERRED_RE.search(cell))
    primary = _primary_section(cell)
    tags = [m.group(1) for m in _CTX_TAG_RE.finditer(primary)]
    seen = set(tags)
    ordered = [t for t in _CRITICALITY_KEYS if t in seen]
    return ordered, inferred


def _split_detail_rows(detail_html: str) -> list[tuple[str, str, str]]:
    """Return list of (field, value, criticality) cells for each <tr> inside
    <tbody>. Skips thead rows. Cells are raw HTML between <td>...</td>."""
    # Isolate <tbody>...</tbody> (first occurrence)
    tb_match = re.search(r"<tbody>(.*?)</tbody>", detail_html, re.DOTALL)
    body = tb_match.group(1) if tb_match else detail_html
    rows: list[tuple[str, str, str]] = []
    # Only direct <tr> inside tbody — but nested <table> inside cells also has <tr>.
    # To avoid false matches, track nested <table> depth as we scan.
    i = 0
    depth = 0
    tr_start = None
    while i < len(body):
        if body.startswith("<table", i):
            depth += 1
            i += 6
            continue
        if body.startswith("</table>", i):
            depth -= 1
            i += 8
            continue
        if depth == 0 and body.startswith("<tr", i):
            # advance past tag
            end = body.find(">", i)
            tr_start = end + 1 if end != -1 else i
            i = tr_start
            continue
        if depth == 0 and body.startswith("</tr>", i) and tr_start is not None:
            tr_content = body[tr_start:i]
            cells = _split_top_level_td(tr_content)
            if len(cells) >= 3:
                rows.append((cells[0], cells[1], cells[2]))
            tr_start = None
            i += 5
            continue
        i += 1
    return rows


def _split_top_level_td(tr_html: str) -> list[str]:
    """Extract top-level <td> cell contents, ignoring nested <table>."""
    cells: list[str] = []
    depth = 0
    i = 0
    td_start = None
    while i < len(tr_html):
        if tr_html.startswith("<table", i):
            depth += 1
            i += 6
            continue
        if tr_html.startswith("</table>", i):
            depth -= 1
            i += 8
            continue
        if depth == 0 and tr_html.startswith("<td", i):
            end = tr_html.find(">", i)
            td_start = end + 1 if end != -1 else i
            i = td_start
            continue
        if depth == 0 and tr_html.startswith("</td>", i) and td_start is not None:
            cells.append(tr_html[td_start:i])
            td_start = None
            i += 5
            continue
        i += 1
    return cells


def _parse_attr_row(attr_line: str) -> list[str]:
    """Split a markdown table row into cell strings."""
    if not attr_line.strip().startswith("|"):
        return []
    cells = [c.strip() for c in attr_line.strip().strip("|").split("|")]
    return cells


def _split_body_into_blocks(body_text: str) -> list[str]:
    """Return the text span belonging to each H4 requirement block (from the
    heading line to just before the next H4 or end-of-body)."""
    heading_positions = [m.start() for m in re.finditer(r"(?m)^####\s+\S+\s+—\s+.+$", body_text)]
    spans: list[str] = []
    for i, start in enumerate(heading_positions):
        end = heading_positions[i + 1] if i + 1 < len(heading_positions) else len(body_text)
        spans.append(body_text[start:end])
    return spans


def parse_blocks(body_text: str) -> list[Block]:
    """Parse all R1 per-requirement blocks from a structured MD body."""
    blocks: list[Block] = []
    for span in _split_body_into_blocks(body_text):
        # Heading — first line of the span
        first_nl = span.find("\n")
        heading_line = span[:first_nl] if first_nl != -1 else span
        m = re.match(r"^####\s+(.+?)\s+—\s+(.+?)\s*$", heading_line)
        if not m:
            continue
        key_raw = m.group(1).strip()
        summary = m.group(2).strip()
        key = _strip_link(key_raw).strip("` ")

        blk = Block(key_raw=key_raw, key=key, summary=summary)

        # Attributes table: find the header line with "| Key | Traces To |"
        ah = _ATTR_HEADER_RE.search(span)
        if ah:
            # Data row is two lines after header (header line + separator line + data line)
            lines_after = span[ah.end():].splitlines()
            data_row = None
            for line in lines_after:
                s = line.strip()
                if not s:
                    continue
                if s.startswith("|---") or s.startswith("|--"):
                    continue
                if s.startswith("|"):
                    data_row = s
                    break
            if data_row:
                blk.attr_row_raw = data_row
                blk.has_attrs = True
                cells = _parse_attr_row(data_row)
                if len(cells) >= 6:
                    # Key, Traces To, Epic, Classification, Target, Status
                    _, traces_cell, epic_cell, class_cell, target_cell, status_cell = cells[:6]
                    # Traces To
                    traces_text = traces_cell.strip()
                    if traces_text in ("null", "`null`", "*(none)*", "*(none — manual trace)*"):
                        blk.traces_to = None
                        blk.traces_to_resolved = False
                    else:
                        stripped = _strip_inline_code(traces_cell)
                        if re.match(r"^(DI-\d+|UN-\d+)$", stripped):
                            blk.traces_to = stripped
                            blk.traces_to_resolved = True
                        else:
                            blk.traces_to = stripped if stripped else None
                            blk.traces_to_resolved = False
                    # Epic — verbatim, strip backticks + link wrap
                    blk.epic = _strip_inline_code(epic_cell) or None
                    # Classification
                    blk.classification, blk.classification_inferred = _parse_classification_cell(class_cell)
                    # Target
                    target_val = _strip_inline_code(target_cell).lower().strip()
                    blk.target = target_val if target_val else "unassigned"
                    # Status
                    status_val = _strip_inline_code(status_cell).lower().strip()
                    blk.status = status_val if status_val else "proposed"

        # Detail table
        dt = _DETAIL_TABLE_RE.search(span)
        if dt:
            blk.detail_table_raw = dt.group(0)
            blk.has_detail = True
            rows = _split_detail_rows(dt.group(0))
            if rows:
                # First row: Description
                first_field = re.sub(r"<[^>]+>", "", rows[0][0]).strip().lower()
                if first_field.startswith("description"):
                    blk.description_text = rows[0][1]
                    blk.description_criticality, blk.description_criticality_inferred = \
                        _parse_criticality_cell(rows[0][2])
                    ac_rows = rows[1:]
                else:
                    ac_rows = rows
                for field_cell, value_cell, crit_cell in ac_rows:
                    blk.ac_texts.append(value_cell)
                    ctags, cinf = _parse_criticality_cell(crit_cell)
                    blk.ac_criticalities.append((ctags, cinf))

        blocks.append(blk)
    return blocks


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------

def aggregate(blocks: list[Block]) -> dict:
    """Produce the frontmatter `requirements:` aggregate dict from parsed blocks."""
    agg: dict = {
        "count": len(blocks),
        "epics": {},
        "classification": {t: 0 for t in _CANONICAL_TAGS},
        "criticality": {k: 0 for k in _CRITICALITY_KEYS},
        "target_releases": {k: 0 for k in _TARGET_KEYS},
        "traces_to": {"resolved": 0, "unresolved": 0},
        "status": {k: 0 for k in _STATUS_KEYS},
    }

    for blk in blocks:
        # Epics
        epic_key = blk.epic or "(none)"
        agg["epics"][epic_key] = agg["epics"].get(epic_key, 0) + 1

        # Classification — multi-valued
        for tag in blk.classification:
            if tag in agg["classification"]:
                agg["classification"][tag] += 1

        # Criticality — count the Description row only (it's the per-req
        # union of AC tags, which is the right rollup level for the
        # document-wide aggregate). Multi-valued: a req whose description
        # row carries `CtF, CtS` contributes to both. `none` when the row
        # has no CtX tags.
        desc_tags = blk.description_criticality
        if not desc_tags:
            agg["criticality"]["none"] += 1
        else:
            for tag in desc_tags:
                if tag in agg["criticality"]:
                    agg["criticality"][tag] += 1

        # Target releases
        tgt = blk.target if blk.target in agg["target_releases"] else blk.target
        if tgt not in agg["target_releases"]:
            agg["target_releases"][tgt] = 0
        agg["target_releases"][tgt] += 1

        # Traces To
        if blk.traces_to_resolved:
            agg["traces_to"]["resolved"] += 1
        else:
            agg["traces_to"]["unresolved"] += 1

        # Status
        st = blk.status if blk.status in agg["status"] else blk.status
        if st not in agg["status"]:
            agg["status"][st] = 0
        agg["status"][st] += 1

    return agg


# ---------------------------------------------------------------------------
# YAML emission (minimal — matches enrich_frontmatter.py style)
# ---------------------------------------------------------------------------

def _dump_yaml(d: dict, indent: int = 0) -> str:
    out: list[str] = []
    pad = "  " * indent
    for k, v in d.items():
        if isinstance(v, dict):
            if not v:
                out.append(f"{pad}{k}: {{}}")
            else:
                out.append(f"{pad}{k}:")
                out.append(_dump_yaml(v, indent + 1))
        elif isinstance(v, list):
            if not v:
                out.append(f"{pad}{k}: []")
            else:
                out.append(f"{pad}{k}:")
                for item in v:
                    out.append(f'{pad}  - "{item}"' if isinstance(item, str) else f"{pad}  - {item}")
        elif isinstance(v, bool):
            out.append(f"{pad}{k}: {str(v).lower()}")
        elif v is None:
            out.append(f"{pad}{k}: null")
        elif isinstance(v, (int, float)):
            out.append(f"{pad}{k}: {v}")
        else:
            s = str(v)
            if any(c in s for c in ' :#[]{}"\''):
                out.append(f'{pad}{k}: "{s}"')
            else:
                out.append(f"{pad}{k}: {s}")
    return "\n".join(out)


def _read_body(md_path: Path) -> str:
    """Read a full MD file and return only the body (post-frontmatter)."""
    text = md_path.read_text(encoding="utf-8", errors="ignore")
    m = re.match(r"---\s*\n.*?\n---\s*\n(.*)", text, re.DOTALL)
    return m.group(1) if m else text


# ---------------------------------------------------------------------------
# CLI + self-test
# ---------------------------------------------------------------------------

_CANONICAL_SRS = (
    "docs/project/dhfs/hiplink-pre-op/design-controls/requirements/"
    "HipLink Planning - Software Requirements Specification (SRS) - 1.0.0.md"
)


def _self_test(repo_root: Path) -> int:
    srs_path = repo_root / _CANONICAL_SRS
    if not srs_path.exists():
        print(f"self-test FAIL: canonical SRS not found at {srs_path}", file=sys.stderr)
        return 2
    body = _read_body(srs_path)
    blocks = parse_blocks(body)
    agg = aggregate(blocks)

    # Expected (from embedded frontmatter of the v29-adopted canonical SRS):
    expected = {
        "count": 7,
        "classification_floor_functional": 7,
        "criticality_CtS_min": 3,
        "traces_to_resolved": 2,
        "traces_to_unresolved": 5,
        "status_proposed": 7,
        "target_v1": 7,
    }

    failures: list[str] = []

    if agg["count"] != expected["count"]:
        failures.append(f"count: got {agg['count']} expected {expected['count']}")
    if agg["classification"].get("functional", 0) != expected["classification_floor_functional"]:
        failures.append(
            f"functional: got {agg['classification'].get('functional')} "
            f"expected {expected['classification_floor_functional']}"
        )
    if agg["criticality"].get("CtS", 0) < expected["criticality_CtS_min"]:
        failures.append(
            f"CtS: got {agg['criticality'].get('CtS')} expected >= {expected['criticality_CtS_min']}"
        )
    if agg["traces_to"]["resolved"] != expected["traces_to_resolved"]:
        failures.append(
            f"traces_to.resolved: got {agg['traces_to']['resolved']} "
            f"expected {expected['traces_to_resolved']}"
        )
    if agg["traces_to"]["unresolved"] != expected["traces_to_unresolved"]:
        failures.append(
            f"traces_to.unresolved: got {agg['traces_to']['unresolved']} "
            f"expected {expected['traces_to_unresolved']}"
        )
    if agg["status"].get("proposed", 0) != expected["status_proposed"]:
        failures.append(
            f"status.proposed: got {agg['status'].get('proposed')} "
            f"expected {expected['status_proposed']}"
        )
    if agg["target_releases"].get("v1", 0) != expected["target_v1"]:
        failures.append(
            f"target_releases.v1: got {agg['target_releases'].get('v1')} "
            f"expected {expected['target_v1']}"
        )

    # Sanity: CtF is zero (never auto-inferred, and the canonical SRS's
    # current content has no human-confirmed CtF tags either)
    if agg["criticality"].get("CtF", 0) != 0:
        failures.append(f"CtF should be 0 (never auto-inferred); got {agg['criticality'].get('CtF')}")

    # classify_text unit tests — taxonomy regexes now support stem-matching
    # (task ben/090 Phase 1: `\bencrypt\w*\b` etc. so `encrypted` matches).
    assert "functional" in classify_text("any text")
    assert "safety" in classify_text("hazard analysis")
    assert "safety" in classify_text("hazards were mitigated per ISO 14971"), \
        "stem-matching: mitigated should match mitigat\\w*"
    assert "privacy" in classify_text("PHI stored at rest")
    assert "security" in classify_text("PHI encrypted at rest"), \
        "stem-matching: encrypted should match encrypt\\w*"
    assert "security" in classify_text("users authenticate via SSO token")
    assert "security" in classify_text("authentication is required"), \
        "stem-matching: authentication should match authentic\\w*"
    assert "regulatory" in classify_text("audit trail per 21 CFR Part 11")
    assert "regulatory" in classify_text("audit trails are maintained"), \
        "stem-matching: trails should match audit trail\\w*"

    # infer_criticality unit tests
    assert infer_criticality("no medical stakes here") == "none"
    assert infer_criticality("hazardous situation for patient") == "CtS"
    # "Part 11" hits regulatory but not safety → CtC
    assert infer_criticality("compliance with 21 CFR Part 11 audit trail") == "CtC"
    assert infer_criticality("latency under 200ms") == "CtP"

    print(f"self-test: parsed {len(blocks)} blocks from canonical SRS")
    print(f"  aggregate = {json.dumps(agg, indent=2)}")

    if failures:
        print("\nFAILURES:", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1

    print("\nself-test PASS")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Infer requirement-doc metadata and aggregate.")
    sub = parser.add_subparsers(dest="cmd")

    sp_agg = sub.add_parser("aggregate", help="Parse an MD body and emit the requirements: aggregate.")
    sp_agg.add_argument("md_path", type=Path)
    sp_agg.add_argument("--format", choices=["yaml", "json"], default="yaml")
    sp_agg.add_argument("--body-only", action="store_true",
                        help="Treat input as already-body text (no frontmatter).")

    sp_classify = sub.add_parser("classify", help="Emit canonical tags for input text.")
    sp_classify.add_argument("text")

    sp_crit = sub.add_parser("criticality", help="Emit inferred CtX for input AC text.")
    sp_crit.add_argument("text")

    sp_test = sub.add_parser("self-test", help="Run embedded self-test.")
    # Convenience
    parser.add_argument("--self-test", dest="_self_test", action="store_true")

    args = parser.parse_args()

    # Discover repo root (look for project.yml upward from script)
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir
    for _ in range(6):
        if (repo_root / "project.yml").exists():
            break
        repo_root = repo_root.parent

    if args._self_test or args.cmd == "self-test":
        return _self_test(repo_root)

    if args.cmd == "aggregate":
        body = args.md_path.read_text(encoding="utf-8", errors="ignore") if args.body_only \
            else _read_body(args.md_path)
        blocks = parse_blocks(body)
        agg = aggregate(blocks)
        if args.format == "json":
            print(json.dumps(agg, indent=2))
        else:
            print("requirements:")
            print(_dump_yaml(agg, indent=1))
        return 0

    if args.cmd == "classify":
        for t in classify_text(args.text):
            print(t)
        return 0

    if args.cmd == "criticality":
        print(infer_criticality(args.text))
        return 0

    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
