#!/usr/bin/env python3
"""
build-qms.py — Build qms-manifest.json + refresh the visible tables in qms-manifest.md.

Reads docs/project/dhf-manifest/qms-manifest.md, extracts all `<!-- QMS-DATA ... -->`
HTML comment blocks (the hand-authored source of truth), and emits:
  - qms-manifest.json                        — cross-map sidecar
  - qms-manifest.md (in place rewrite)       — refreshes the Regulatory Grounding cells
                                                of each compact table from the QMS-DATA
                                                records + Tier 1 per-source JSON labels.

The hand-author edits only the hidden QMS-DATA YAML. The visible tables above each
block are semi-built: this script regenerates the Regulatory Grounding column cells
with linked OBL-IDs and short text labels (first extracted_requirement, truncated).

Output JSON shape:
    {
      "generated": "YYYY-MM-DD",
      "source_count": N,
      "obligation_count": N,
      "qms_obligations": [ {...full records...} ],
      "by_source": { "SOP-000355609": ["QMS-RM-001", ...], ... },
      "by_topic":  { "risk-management": [...], ... },
      "obl_to_qms": { "OBL-14971-001": ["QMS-RM-004", ...], ... },
      "qms_to_obl": { "QMS-RM-004": ["OBL-14971-001", "OBL-14971-002"], ... }
    }

Usage:
    python3 build-qms.py [--dry-run]

Exit codes:
    0  success
    1  qms-manifest.md not found
    2  YAML parse error in QMS-DATA block
    3  duplicate QMS-ID detected
"""

import sys
import re
import json
import yaml
import argparse
from pathlib import Path
from datetime import date
from collections import defaultdict, OrderedDict

from _linking import render_obl_link, render_qms_link, find_bare_ids

SCRIPT_DIR = Path(__file__).parent
SKILL_DIR = SCRIPT_DIR.parent
PROJECT_ROOT = SKILL_DIR.parent.parent.parent

MANIFEST_MD = PROJECT_ROOT / "docs/project/dhf-manifest/qms-manifest.md"
MANIFEST_JSON = PROJECT_ROOT / "docs/project/dhf-manifest/qms-manifest.json"

# Tier 1 source data — for OBL label + anchor lookup when rebuilding the
# Regulatory Grounding column cells.
TIER1_DIR = SKILL_DIR / "data"
TIER1_CATEGORIES = ["fda-guidance", "standards", "industry-frameworks"]

# Arthrex QMS source corpus — used to deep-link QMS-ID + Section cells into
# the actual SOP/WI/FORM/POL markdown.
QMS_SOURCE_ROOT = PROJECT_ROOT / "docs/internal/source-md"

# Relative paths from qms-manifest.md's folder (docs/project/dhf-manifest/).
# → Tier 1 data: ../../../.claude/skills/dhf-manifest/data
# → QMS sources: ../../internal/source-md
TIER1_REL = "../../../.claude/skills/dhf-manifest/data"
QMS_SRC_REL = "../../internal/source-md"

QMS_DATA_RE = re.compile(r"<!--\s*QMS-DATA\s*\n(.*?)\n\s*-->", re.DOTALL)


def _label(extracted_requirements: list, max_len: int | None = None) -> str:
    """First extracted_requirement bullet, for use as a human-readable label.

    `max_len` is ignored — kept only for backwards-compat with existing callers.
    Full text is returned so the reader never has to click through for the rest.
    """
    if not extracted_requirements:
        return ""
    first = extracted_requirements[0]
    if isinstance(first, dict):
        first = "; ".join(f"{k}: {v}" for k, v in first.items())
    return str(first).strip().strip('"')


def load_tier1_obl_map() -> dict:
    """Return {OBL-xxx: {category, file, label, section}} from per-source Tier 1 JSONs.

    Falls back to an empty dict (callers will render plain OBL-IDs without links).
    """
    result: dict = {}
    for cat in TIER1_CATEGORIES:
        cat_dir = TIER1_DIR / cat
        if not cat_dir.exists():
            continue
        for jp in cat_dir.glob("*.json"):
            try:
                payload = json.loads(jp.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            md_name = payload.get("source_file") or (jp.with_suffix(".md").name)
            for obl in payload.get("obligations", []):
                oid = obl.get("id")
                if not oid:
                    continue
                result[oid] = {
                    "category": cat,
                    "file": md_name,
                    "label": _label(obl.get("extracted_requirements", [])),
                    "section": obl.get("section", ""),
                    "title": obl.get("title", ""),
                }
    return result


def escape_pipe(s: str) -> str:
    return s.replace("|", "\\|")


def url_encode_spaces(p: str) -> str:
    """URL-encode spaces in a path segment for markdown link targets.

    Keep `/` literal so relative paths still read cleanly in the source file.
    """
    return p.replace(" ", "%20")


# Directory layout of docs/internal/source-md/ (corpus is pre-curated).
QMS_SOURCE_SUBDIRS = ["SOPs", "Policies", "Work Instructions", "Forms", "Standards"]


def load_qms_source_doc_map() -> dict:
    """Walk docs/internal/source-md/*/<DOCID> - <Title>.md and return
    {DOCID: {'subdir', 'filename', 'title', 'rel_link'}}.

    DOCID is the first `<letters>-<digits>` token of the filename (e.g. SOP-000355609,
    POL-000100241, WI-000101591, FORM-000364987, QSD-000108614).
    Files that don't match the naming pattern are skipped.
    """
    doc_map: dict = {}
    if not QMS_SOURCE_ROOT.exists():
        return doc_map
    name_re = re.compile(r"^([A-Z]+-\d+)\s*-\s*(.+)\.md$")
    for sub in QMS_SOURCE_SUBDIRS:
        d = QMS_SOURCE_ROOT / sub
        if not d.exists():
            continue
        for md in sorted(d.glob("*.md")):
            m = name_re.match(md.name)
            if not m:
                continue
            doc_id, title = m.group(1), m.group(2).strip()
            # Encode spaces in BOTH the subdir ("Work Instructions") and the filename
            # ("WI-xxx - <Title>.md") — markdown viewers cut URLs at the first
            # un-encoded space, so any literal space anywhere in the path breaks the link.
            rel = f"{QMS_SRC_REL}/{url_encode_spaces(sub)}/{url_encode_spaces(md.name)}"
            doc_map[doc_id] = {
                "subdir": sub,
                "filename": md.name,
                "title": title,
                "rel_link": rel,
            }
    return doc_map


def _extract_doc_id_and_section(source_str: str) -> tuple[str, str]:
    """From 'SOP-000355609 §6.2' or 'FORM-000364987 (Purpose, Scope, ...)',
    return (doc_id, section_or_scope_text)."""
    m = re.match(r"^([A-Z]+-\d+)\s*(.*)$", source_str or "")
    if not m:
        return "", source_str or ""
    return m.group(1), m.group(2).strip()


def _render_qms_id_cell(rec: dict, source_doc_map: dict) -> str:
    """Col 1: `<a id="qms-xx-xxx"></a>[QMS-xx-xxx](source-doc.md) — <label>`.

    Link target = actual QMS source markdown file. If the source doc isn't
    in the corpus, fall back to the in-page anchor so the cell still works.
    """
    qid = rec.get("id", "")
    anchor = qid.lower()
    doc_id, _ = _extract_doc_id_and_section(rec.get("source", ""))
    info = source_doc_map.get(doc_id)
    title = rec.get("title", "") or ""
    href = info["rel_link"] if info else f"#{anchor}"
    link = render_qms_link(qid, title, href)
    label = _label(rec.get("extracted_requirements", []), max_len=100)
    if label:
        return f'<a id="{anchor}"></a>{link} — {escape_pipe(label)}'
    return f'<a id="{anchor}"></a>{link}'


def _render_qms_section_cell(rec: dict, source_doc_map: dict) -> str:
    """Col 2: `[DOCID §x.y](source-doc.md) — <source_title>`.

    Shows the QMS document the obligation comes from and (when parseable)
    the section within it, with the doc title spelled out so the reader
    sees what the source is without clicking through.
    """
    source_str = rec.get("source", "") or ""
    doc_id, section = _extract_doc_id_and_section(source_str)
    title = rec.get("source_title", "") or ""
    info = source_doc_map.get(doc_id)
    # Link text = "DOCID" + (" §x.y" if present)
    link_text_parts = [doc_id] if doc_id else []
    if section:
        link_text_parts.append(section)
    link_text = " ".join(link_text_parts) if link_text_parts else source_str
    if info:
        linked = f"[{escape_pipe(link_text)}]({info['rel_link']})"
    else:
        linked = escape_pipe(link_text)
    if title:
        return f"{linked} — {escape_pipe(title)}"
    return linked


def _render_reg_grounding_cell(obls: list, obl_map: dict) -> str:
    """Render the Regulatory Grounding column for one QMS record.

    Format per OBL reference: `[OBL-xxx](../../../... /file.md#OBL-xxx) — <label>`
    Multiple refs separated by `; ` so table parsers still see a single cell.
    """
    if not obls:
        return "—"
    parts: list[str] = []
    for oid in obls:
        info = obl_map.get(oid)
        if info:
            href = f"{TIER1_REL}/{info['category']}/{info['file']}#{oid}"
            title = info.get("title", "") or ""
            label = info.get("label") or ""
            link = render_obl_link(oid, title, href)
            if label:
                parts.append(f"{link} — {escape_pipe(label)}")
            else:
                parts.append(link)
        else:
            # OBL referenced by QMS record but no Tier 1 match — render plain.
            parts.append(render_obl_link(oid, "", None))
    return "; ".join(parts)


def _rewrite_data_rows(
    md_text: str,
    records: list[dict],
    obl_map: dict,
    source_doc_map: dict,
) -> str:
    """Regenerate every QMS data row in the visible compact tables from the
    structured records.

    A data row is identified by an `<a id="qms-...">` anchor at the start of
    cell 1. Header + separator rows don't carry this anchor and are left alone,
    as is every non-row line (intro prose, QMS-DATA blocks, context paragraphs).

    Output row shape:
      | <a id="..."></a>[`QMS-xx-xxx`](<qms-source-doc>.md) — <label> \
        | [DOCID §x.y](<qms-source-doc>.md) — <source_title> \
        | `topic` \
        | applies_to (semicolon-joined) \
        | linked + labeled regulatory grounding |
    """
    by_qid: dict[str, dict] = {r["id"]: r for r in records if r.get("id")}
    anchor_re = re.compile(r'^\|\s*<a id="(qms-[a-z0-9-]+)"></a>')

    out_lines: list[str] = []
    for line in md_text.splitlines():
        m = anchor_re.match(line)
        if not m:
            out_lines.append(line)
            continue
        qid = m.group(1).upper()
        rec = by_qid.get(qid)
        if not rec:
            out_lines.append(line)
            continue

        # Column 1: id cell with anchor + linked-id + label
        c1 = _render_qms_id_cell(rec, source_doc_map)

        # Column 2: source + section, linked to actual QMS doc
        c2 = _render_qms_section_cell(rec, source_doc_map)

        # Column 3: topic (backtick-quoted inline code)
        topic = rec.get("topic", "")
        c3 = f"`{topic}`" if topic else "—"

        # Column 4: applies_to (semicolon-joined, full text)
        applies = rec.get("applies_to", []) or []
        if isinstance(applies, list):
            applies_str = "; ".join(str(a) for a in applies)
        else:
            applies_str = str(applies)
        c4 = escape_pipe(applies_str) if applies_str else "—"

        # Column 5: regulatory grounding (linked OBL refs + labels)
        grounding = rec.get("regulatory_grounding") or []
        if not isinstance(grounding, list):
            grounding = []
        c5 = _render_reg_grounding_cell(grounding, obl_map)

        out_lines.append(f"| {c1} | {c2} | {c3} | {c4} | {c5} |")

    return "\n".join(out_lines) + ("\n" if md_text.endswith("\n") else "")


def extract_source_id(source_str: str) -> str:
    m = re.match(r"^(SOP|WI|FORM|POL|QSD|GUI|STD)[-\s]?(\d+)", source_str or "")
    if m:
        return f"{m.group(1)}-{m.group(2)}"
    return "UNKNOWN"


def main() -> int:
    parser = argparse.ArgumentParser(description="Build qms-manifest.json from qms-manifest.md")
    parser.add_argument("--dry-run", action="store_true", help="Print summary, do not write JSON")
    args = parser.parse_args()

    if not MANIFEST_MD.exists():
        print(f"ERROR: qms-manifest.md not found at {MANIFEST_MD}", file=sys.stderr)
        return 1

    text = MANIFEST_MD.read_text(encoding="utf-8")
    blocks = QMS_DATA_RE.findall(text)
    if not blocks:
        print("WARNING: no <!-- QMS-DATA --> blocks found; writing empty manifest.", file=sys.stderr)

    all_records: list[dict] = []
    seen_ids: dict[str, int] = {}
    for idx, block in enumerate(blocks):
        try:
            parsed = yaml.safe_load(block)
        except yaml.YAMLError as e:
            print(f"ERROR: YAML parse error in block #{idx + 1}: {e}", file=sys.stderr)
            return 2
        if not isinstance(parsed, dict) or "records" not in parsed:
            print(
                f"WARNING: block #{idx + 1} is not a mapping with 'records:' key, skipping",
                file=sys.stderr,
            )
            continue
        records = parsed.get("records", []) or []
        for rec in records:
            if not isinstance(rec, dict) or "id" not in rec:
                continue
            rid = rec["id"]
            if rid in seen_ids:
                print(
                    f"ERROR: duplicate QMS-ID '{rid}' (first at block #{seen_ids[rid]}, "
                    f"dup at block #{idx + 1})",
                    file=sys.stderr,
                )
                return 3
            seen_ids[rid] = idx + 1
            all_records.append(rec)

    # Build cross-maps
    by_source: dict[str, list[str]] = defaultdict(list)
    by_topic: dict[str, list[str]] = defaultdict(list)
    obl_to_qms: dict[str, list[str]] = defaultdict(list)
    qms_to_obl: dict[str, list[str]] = {}

    for rec in all_records:
        rid = rec["id"]
        src_id = extract_source_id(rec.get("source", ""))
        by_source[src_id].append(rid)
        topic = rec.get("topic", "")
        if topic:
            by_topic[topic].append(rid)
        grounding = rec.get("regulatory_grounding", []) or []
        qms_to_obl[rid] = list(grounding)
        for obl in grounding:
            obl_to_qms[obl].append(rid)

    # Sort maps for determinism
    by_source = OrderedDict(sorted(by_source.items()))
    by_topic = OrderedDict(sorted(by_topic.items()))
    obl_to_qms = OrderedDict(sorted(obl_to_qms.items()))

    payload = OrderedDict([
        ("generated", date.today().isoformat()),
        ("source_md", str(MANIFEST_MD.relative_to(PROJECT_ROOT))),
        ("source_count", len(by_source)),
        ("obligation_count", len(all_records)),
        ("qms_obligations", all_records),
        ("by_source", by_source),
        ("by_topic", by_topic),
        ("obl_to_qms", obl_to_qms),
        ("qms_to_obl", qms_to_obl),
    ])

    print(f"QMS manifest build:")
    print(f"  Source file       : {MANIFEST_MD.relative_to(PROJECT_ROOT)}")
    print(f"  QMS-DATA blocks   : {len(blocks)}")
    print(f"  QMS obligations   : {len(all_records)}")
    print(f"  Source documents  : {len(by_source)}")
    print(f"  Topics            : {len(by_topic)}")
    print(f"  Regulatory refs   : {sum(len(v) for v in qms_to_obl.values())} "
          f"(unique OBL targets: {len(obl_to_qms)})")

    # Refresh visible compact-table rows in qms-manifest.md
    obl_map = load_tier1_obl_map()
    source_doc_map = load_qms_source_doc_map()
    updated_md = _rewrite_data_rows(text, all_records, obl_map, source_doc_map)
    md_changed = updated_md != text

    linked_qms_docs = sum(
        1 for r in all_records
        if source_doc_map.get(_extract_doc_id_and_section(r.get("source", ""))[0])
    )

    print(f"  Tier 1 OBL map    : {len(obl_map)} obligations")
    print(f"  QMS source corpus : {len(source_doc_map)} docs indexed")
    print(f"  QMS recs linked   : {linked_qms_docs}/{len(all_records)} to source MDs")
    print(f"  qms-manifest.md   : {'updated' if md_changed else 'unchanged'}")

    if args.dry_run:
        print("[dry-run] would write:", MANIFEST_JSON.relative_to(PROJECT_ROOT))
        if md_changed:
            print("[dry-run] would rewrite:", MANIFEST_MD.relative_to(PROJECT_ROOT))
        return 0

    MANIFEST_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    print(f"  Wrote             : {MANIFEST_JSON.relative_to(PROJECT_ROOT)} "
          f"({MANIFEST_JSON.stat().st_size:,} bytes)")
    if md_changed:
        MANIFEST_MD.write_text(updated_md, encoding="utf-8")
        print(f"  Rewrote           : {MANIFEST_MD.relative_to(PROJECT_ROOT)} "
              f"({MANIFEST_MD.stat().st_size:,} bytes)")

    # Post-build bare-ID check (task 104 Phase 4) — every ID in the visible
    # tables of qms-manifest.md must be inside a markdown link. We only scan
    # content *outside* the `<!-- QMS-DATA ... -->` blocks (those are source of
    # truth and naturally contain bare IDs in YAML fields like
    # `regulatory_grounding: [OBL-14971-001]`).
    content_visible = re.sub(
        r"<!--\s*QMS-DATA\s*\n.*?\n-->", "", MANIFEST_MD.read_text(encoding="utf-8"),
        flags=re.DOTALL,
    )
    bare = find_bare_ids(content_visible)
    if bare:
        print(f"\n  ✗ POST-BUILD CHECK FAILED: {len(bare)} bare ID(s) in visible tables")
        for lineno, ident, snippet in bare[:20]:
            print(f"    qms-manifest.md:{lineno}  {ident}  — {snippet}")
        if len(bare) > 20:
            print(f"    ... and {len(bare) - 20} more")
        return 4
    return 0


if __name__ == "__main__":
    sys.exit(main())
