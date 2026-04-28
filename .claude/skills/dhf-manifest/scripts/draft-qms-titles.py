#!/usr/bin/env python3
"""Generate _scratch/104-qms-titles-draft.md for Phase 3 review.

Parses qms-manifest.md QMS-DATA YAML blocks, proposes a compact title
(3-6 words, Title Case, <= 60 chars) per record, and writes a reviewable
table grouped by source document.

Heuristic: if source_title looks compact and distinctive, start from
extracted_requirements[0] clipped to a clause; otherwise fall back to
source_title + topic.

Run from repo root:
    python3 .claude/skills/dhf-manifest/scripts/draft-qms-titles.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[4]
MANIFEST = REPO_ROOT / "docs/project/dhf-manifest/qms-manifest.md"
OUT = REPO_ROOT / "tasks/ben/_scratch/104-qms-titles-draft.md"

BLOCK_RE = re.compile(r"<!--\s*QMS-DATA\s*\n(.*?)\n-->", re.DOTALL)
STOPWORDS = {
    "the", "a", "an", "of", "and", "or", "for", "in", "on", "at", "to",
    "with", "from", "be", "is", "as", "by", "that", "this", "these", "those",
}


def title_case(s: str) -> str:
    words = s.split()
    out = []
    for i, w in enumerate(words):
        if i > 0 and w.lower() in STOPWORDS and len(w) <= 4:
            out.append(w.lower())
        else:
            # preserve all-caps acronyms, hyphen compounds
            if w.isupper():
                out.append(w)
            elif "-" in w:
                out.append("-".join(p[:1].upper() + p[1:].lower() if p else p for p in w.split("-")))
            else:
                out.append(w[:1].upper() + w[1:].lower() if w else w)
    if out:
        out[0] = out[0][:1].upper() + out[0][1:]
    return " ".join(out)


TOPIC_LABELS = {
    "risk-management": "Risk",
    "architecture": "Architecture",
    "cybersecurity": "Cybersecurity",
    "design-outputs": "Design Outputs",
    "design-reviews": "Design Review",
    "human-factors": "Human Factors",
    "labeling-ifu": "Labeling",
    "regulatory-submission": "Regulatory Submission",
    "requirements": "Requirements",
    "software-lifecycle": "Software Lifecycle",
    "traceability": "Traceability",
    "validation": "Validation",
    "verification": "Verification",
    "configuration-change": "Configuration Change",
}


def propose_title(rec: dict, seen_src_titles: dict) -> str:
    src_title = (rec.get("source_title") or "").strip()
    topic = (rec.get("topic") or "").strip()
    src_field = (rec.get("source") or "").strip()

    # Base: source_title if present; else topic label
    base = src_title or TOPIC_LABELS.get(topic, "QMS Procedure")

    # Disambiguate when multiple records share source_title
    count = seen_src_titles.get(src_title, 0)
    seen_src_titles[src_title] = count + 1

    candidate = base
    if count > 0:
        # Pull a disambiguator: first extract the section hint from source field
        m = re.search(r"§\s*[\d\.]+", src_field)
        if m:
            disambiguator = m.group(0).replace(" ", "")
            candidate = f"{base} {disambiguator}"
        else:
            topic_label = TOPIC_LABELS.get(topic, topic)
            candidate = f"{base} — {topic_label}" if topic_label and topic_label not in base else f"{base} #{count + 1}"

    # enforce 60-char cap
    if len(candidate) > 60:
        candidate = candidate[:57].rstrip() + "..."

    return title_case(candidate)


def main() -> int:
    if not MANIFEST.exists():
        print(f"ERROR: {MANIFEST} not found", file=sys.stderr)
        return 1

    src = MANIFEST.read_text(encoding="utf-8")
    blocks = BLOCK_RE.findall(src)

    by_source: dict[str, list[tuple[str, str, str]]] = {}  # source -> [(id, section-hint, title)]
    seen_src_titles: dict = {}
    total = 0
    for block in blocks:
        try:
            data = yaml.safe_load(block)
        except yaml.YAMLError as e:
            print(f"WARN: yaml parse error: {e}", file=sys.stderr)
            continue
        if not data or "records" not in data:
            continue
        for rec in data["records"]:
            if not isinstance(rec, dict):
                continue
            qms_id = rec.get("id", "")
            src_field = rec.get("source", "").strip()
            # source doc key = first token (e.g. "FORM-000364981")
            m = re.match(r"^([A-Z]+-\d+)", src_field)
            src_key = m.group(1) if m else src_field[:20]
            src_title = rec.get("source_title", "").strip()
            section_hint = src_field.replace(src_key, "").strip(" ()")
            if not section_hint:
                section_hint = src_title or rec.get("topic", "")
            title = propose_title(rec, seen_src_titles)
            by_source.setdefault(f"{src_key} — {src_title}", []).append(
                (qms_id, section_hint, title)
            )
            total += 1

    lines = [
        "# Task 104 Phase 3 — Proposed Titles for QMS Records",
        "",
        f"**Total records**: {total}  ",
        f"**Source documents**: {len(by_source)}",
        "",
        "**Review workflow:**",
        "1. Scan the table(s) below, grouped by source document.",
        "2. Edit the \"Proposed Title\" column in place for any title that reads wrong.",
        "3. Style guide: 3–6 words, Title Case, describes *what the procedure covers* (not generic SOP language), ≤ 60 chars, no pipe chars, no markdown link syntax.",
        "4. When done, say \"apply QMS titles\" — the applicator script will write `title: \"...\"` into each QMS-DATA YAML block and rebuild.",
        "",
        "---",
        "",
    ]

    for src_hdr in sorted(by_source):
        recs = by_source[src_hdr]
        lines.append(f"## {src_hdr}")
        lines.append("")
        lines.append(f"_{len(recs)} record{'s' if len(recs) != 1 else ''}_")
        lines.append("")
        lines.append("| ID | Section / Scope | Proposed Title |")
        lines.append("|----|-----------------|----------------|")
        for qms_id, section_hint, title in recs:
            hint = section_hint.replace("|", "\\|")
            lines.append(f"| {qms_id} | {hint} | {title} |")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append(f"**Total: {total} proposed titles across {len(by_source)} source documents.**")
    lines.append("")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT.relative_to(REPO_ROOT)}")
    print(f"  {total} records across {len(by_source)} source documents")
    return 0


if __name__ == "__main__":
    sys.exit(main())
