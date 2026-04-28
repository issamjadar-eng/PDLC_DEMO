#!/usr/bin/env python3
"""
validate_phase7.py — Script gate replacing the LLM Phase 7 self-audit in v29.

Ports the mechanical Required gates from `agents/adopter.md` Phase 7 and
`agents/converter.md` Phase 7 to Python. A single subprocess call replaces what
the LLM previously walked tool-call-by-tool-call.

Runs in < 1 second on a 16-page SAD. Exit codes:
  0 — all Required gates pass (may have Warnings)
  1 — invocation error (bad arguments, missing files)
  2 — one or more Required gates failed

Output:
  JSON on stdout:
    {
      "result": "pass" | "fail",
      "doc_type": "architecture",
      "checks": {
        "doc_classify_marker": {"status": "pass|fail|warn", "detail": "..."},
        "f11_classify_adjacency": {"status": "pass", "detail": "8/8 markers ..."},
        ...
      },
      "warnings": [...],
      "errors": [...]
    }

The orchestrator (`scripts/adopt_v30.py`) calls this after assembly and before
commit_atomic. If this script exits 2, the orchestrator leaves staging in
place and reports VALIDATION_FAILED.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Optional


# --- Frontmatter parsing (minimal — no external YAML dep) ---

_FRONTMATTER_BOUND = re.compile(r"^---\s*$", re.MULTILINE)


def _parse_frontmatter(md: str) -> tuple[dict, str]:
    """
    Split MD into (frontmatter_dict, body_text).
    Minimal YAML — handles `key: value` and `key: "value"` at top level.
    For `images:` / `version_lineage:` arrays we just record presence, not contents.
    Enough for Phase 7 checks; validate_phase7 doesn't need deep YAML semantics.
    """
    m_start = _FRONTMATTER_BOUND.search(md)
    if not m_start or m_start.start() != 0:
        return {}, md
    m_end = _FRONTMATTER_BOUND.search(md, m_start.end())
    if not m_end:
        return {}, md
    fm_text = md[m_start.end(): m_end.start()]
    body = md[m_end.end():]

    fm: dict = {}
    for line in fm_text.splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        if line.startswith((" ", "\t", "-")):
            # indented continuation or list item — skip for minimal parse
            continue
        m = re.match(r"^([A-Za-z_][\w]*)\s*:\s*(.*)$", line)
        if not m:
            continue
        key, value = m.group(1), m.group(2).strip()
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
        fm[key] = value
    return fm, body


# --- Marker scanning ---

_DOC_CLASSIFY = re.compile(
    r"<!--\s*DOC-CLASSIFY:\s*(?P<attrs>[^>]+?)\s*-->"
)
_F11_CLASSIFY = re.compile(
    r"<!--\s*F11-CLASSIFY:\s*(?P<attrs>[^>]+?)\s*-->"
)
_TABLE_CLASSIFY = re.compile(
    r"<!--\s*TABLE-CLASSIFY:\s*(?P<attrs>[^>]+?)\s*-->"
)
_IMG_REF = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
_MERMAID_FENCE = re.compile(r"^```mermaid\s*$", re.MULTILINE)
_HYPERLINK = re.compile(r"\[[^\]]+\]\([^)]+\)")  # all [text](url) including images


def _parse_marker_attrs(s: str) -> dict:
    """Parse `key="value"` attributes from a marker body string."""
    return {
        m.group(1): m.group(2)
        for m in re.finditer(r'(\w[\w-]*)="([^"]*)"', s)
    }


# --- Individual gates ---

def _check_doc_classify(body: str) -> dict:
    matches = list(_DOC_CLASSIFY.finditer(body))
    if not matches:
        return {"status": "fail", "detail": "DOC-CLASSIFY marker not found"}
    if len(matches) > 1:
        return {"status": "warn", "detail": f"{len(matches)} DOC-CLASSIFY markers; expected 1"}
    attrs = _parse_marker_attrs(matches[0].group("attrs"))
    if "doc_type" not in attrs:
        return {"status": "fail", "detail": "DOC-CLASSIFY marker missing doc_type= attribute"}
    if "pack" not in attrs:
        return {"status": "warn", "detail": "DOC-CLASSIFY marker missing pack= attribute"}
    return {"status": "pass", "detail": f"doc_type={attrs['doc_type']}", "attrs": attrs}


def _check_f11_adjacency(body: str) -> dict:
    """
    Every F11-CLASSIFY marker must be followed within 3 lines by an `![...](...)`
    image reference. Every marker with mermaid-emit="required" must be followed
    within 7 lines (of the image ref) by a ```mermaid fence.
    """
    lines = body.splitlines()
    failures: list[str] = []
    counts = {"total": 0, "required": 0, "skip": 0, "mermaid_ok": 0, "review": 0}

    for i, line in enumerate(lines):
        m = _F11_CLASSIFY.search(line)
        if not m:
            continue
        counts["total"] += 1
        attrs = _parse_marker_attrs(m.group("attrs"))
        descriptor = attrs.get("descriptor", "?")
        emit = attrs.get("mermaid-emit", "")
        t = attrs.get("type", "")

        # Find image ref within next 3 lines (inclusive)
        img_line = None
        for j in range(i, min(i + 4, len(lines))):
            if _IMG_REF.search(lines[j]):
                img_line = j
                break
        if img_line is None:
            failures.append(f"marker[{descriptor}] has no adjacent image ref within 3 lines")
            continue

        if emit == "required":
            counts["required"] += 1
            # Find ```mermaid fence within 7 lines after the image
            fence_ok = False
            for j in range(img_line + 1, min(img_line + 8, len(lines))):
                if lines[j].strip() == "```mermaid":
                    fence_ok = True
                    break
            if fence_ok:
                counts["mermaid_ok"] += 1
            else:
                failures.append(
                    f"marker[{descriptor}] type={t} mermaid-emit=required but no "
                    f"```mermaid fence within 7 lines of image ref"
                )
        elif emit == "skip":
            counts["skip"] += 1
            if t == "review":
                counts["review"] += 1
                if "skip-reason" not in attrs:
                    failures.append(f"marker[{descriptor}] type=review missing skip-reason")
        else:
            failures.append(
                f"marker[{descriptor}] has invalid mermaid-emit='{emit}' "
                f"(must be 'required' or 'skip')"
            )

    if failures:
        return {
            "status": "fail",
            "detail": f"{len(failures)} failures across {counts['total']} markers",
            "failures": failures,
            "counts": counts,
        }

    return {
        "status": "pass",
        "detail": f"{counts['mermaid_ok']}/{counts['required']} mermaid fences, "
                  f"{counts['skip']} skipped ({counts['review']} for review)",
        "counts": counts,
    }


def _check_doc_version(fm: dict) -> dict:
    v = fm.get("doc_version", "")
    if not v:
        return {"status": "fail", "detail": "doc_version missing from frontmatter"}
    if not re.match(r"^v\d+$", v):
        return {"status": "fail", "detail": f"doc_version='{v}' violates ^v\\d+$"}
    return {"status": "pass", "detail": f"doc_version={v}"}


def _check_filename_no_version_suffix(md_path: Path) -> dict:
    stem = md_path.stem
    if re.search(r"-v\d+$", stem, re.IGNORECASE):
        return {"status": "fail", "detail": f"filename '{stem}' has -v\\d+ suffix"}
    if re.search(r"-\s*Draft\s*$", stem):
        return {"status": "fail", "detail": f"filename '{stem}' has -Draft suffix"}
    return {"status": "pass", "detail": f"filename='{stem}' ok"}


def _check_image_refs(body: str) -> dict:
    refs = _IMG_REF.findall(body)
    if not refs:
        return {"status": "pass", "detail": "no image refs found (ok for text-only docs)"}
    bad: list[str] = []
    for ref in refs:
        ref = ref.strip()
        # Allow both `images/...` (DHF working MD) and `../images/...` (QMS source-md)
        if not (ref.startswith("images/") or ref.startswith("../images/")):
            bad.append(ref)
    if bad:
        return {
            "status": "fail",
            "detail": f"{len(bad)}/{len(refs)} image refs not using images/ prefix",
            "failures": bad[:10],
        }
    return {"status": "pass", "detail": f"{len(refs)}/{len(refs)} image refs use images/ prefix"}


def _check_hyperlink_consistency(fm: dict, body: str) -> dict:
    has_links_str = fm.get("has_hyperlinks", "").lower()
    count_str = fm.get("hyperlink_count", "")

    if not count_str:
        return {"status": "warn", "detail": "hyperlink_count not set in frontmatter"}

    try:
        count = int(count_str)
    except ValueError:
        return {"status": "fail", "detail": f"hyperlink_count='{count_str}' is not an integer"}

    has_links = has_links_str in ("true", "yes")
    if count > 0 and not has_links:
        return {
            "status": "fail",
            "detail": f"hyperlink_count={count} but has_hyperlinks={has_links_str}",
        }
    if count == 0 and has_links:
        return {
            "status": "fail",
            "detail": f"hyperlink_count=0 but has_hyperlinks={has_links_str}",
        }
    return {"status": "pass", "detail": f"has_hyperlinks={has_links}, hyperlink_count={count}"}


def _check_link_count_floor(body: str, expected_k: Optional[int],
                            expected_k_anchors: Optional[int] = None) -> dict:
    """
    Link-count floor. Counts CONTENT links only — same-page anchor links
    (`](#...)` targeting the doc's own headings) are excluded on both sides,
    because they're TOC-scaffold that gets regenerated by GFM's auto-IDs once
    the doc has proper heading structure. Dropping them during restructuring
    is correct behavior, not a regression.

    `expected_k` is the total link count from splice_hyperlinks. If
    `expected_k_anchors` is provided, it's subtracted to get the content K;
    otherwise we count content links both sides of the ledger.

    Ratio B_content / K_content: >= 0.9 pass, >= 0.5 warn, else fail.
    """
    if expected_k is None:
        return {"status": "skip", "detail": "no expected link count provided"}
    if expected_k == 0:
        return {"status": "pass", "detail": "source had no hyperlinks"}

    # Count body links, split by kind
    body_matches = [
        m for m in _HYPERLINK.finditer(body)
        if m.start() == 0 or body[m.start() - 1] != "!"
    ]
    body_anchor = sum(1 for m in body_matches if "](#" in m.group(0))
    body_content = len(body_matches) - body_anchor

    if expected_k_anchors is not None:
        k_content = expected_k - expected_k_anchors
    else:
        # Caller didn't break it down; assume K_content = K (conservative)
        k_content = expected_k

    if k_content <= 0:
        return {
            "status": "pass",
            "detail": f"B_content={body_content} K_content={k_content} "
                      f"(source had only anchor links; content-link preservation vacuous)",
        }

    ratio = body_content / k_content
    detail_suffix = f" (body anchors={body_anchor}, K_anchors={expected_k_anchors or 'unspecified'})"
    if ratio >= 0.9:
        return {
            "status": "pass",
            "detail": f"B_content={body_content} K_content={k_content} ratio={ratio:.2f}{detail_suffix}",
        }
    if ratio >= 0.5:
        return {
            "status": "warn",
            "detail": f"B_content={body_content} K_content={k_content} ratio={ratio:.2f}{detail_suffix} "
                      f"— between 0.5 and 0.9; reviewer should investigate",
        }
    return {
        "status": "fail",
        "detail": f"B_content={body_content} K_content={k_content} ratio={ratio:.2f}{detail_suffix} "
                  f"— below 0.5 catastrophic threshold",
    }


# --- Doc-type-pack-driven gates ---

_ARCH_REQUIRED_KEYWORDS = [
    ["purpose", "overview", "introduction"],
    ["intended audience", "audience"],
    ["system overview", "system architecture"],
    ["software architecture", "application architecture"],
    ["user workflows", "user flows", "workflows", "user roles"],
]

# requirement doc-type: a single H2 wrapper hosting N H4 per-req blocks.
_REQ_REQUIRED_KEYWORDS = [
    ["requirements", "stories", "user stories",
     "functional requirements", "non-functional requirements"],
]

# R1 v22 shape probes
_REQ_H4_RE = re.compile(r"^####\s+\S+\s+—\s+.+$", re.MULTILINE)
_REQ_ATTR_HEADER_RE = re.compile(
    r"\|\s*Key\s*\|\s*Traces To\s*\|\s*Epic\s*\|\s*Classification\s*\|\s*Target\s*\|\s*Status\s*\|",
    re.IGNORECASE,
)
_REQ_DETAIL_HEADER_RE = re.compile(
    r"<th>\s*Field\s*</th>\s*<th>\s*Value\s*</th>\s*<th>\s*Criticality\s*</th>",
    re.IGNORECASE | re.DOTALL,
)
_CANONICAL_CLASS_TAGS = {
    "functional", "safety", "security", "privacy", "usability",
    "performance", "reliability", "interoperability", "regulatory",
}
_CTX_VALID = {"CtF", "CtS", "CtC", "CtP", "none"}
_TRACES_TO_ID_RE = re.compile(r"^(DI-\d+|UN-\d+)$")
_CTF_INFERRED_RE = re.compile(r"`CtF`\s*\(inferred\)", re.IGNORECASE)


def _check_required_sections(body: str, doc_type: str) -> dict:
    """Doc-type-specific required H1/H2 sections."""
    keyword_sets = None
    if doc_type == "architecture":
        keyword_sets = _ARCH_REQUIRED_KEYWORDS
    elif doc_type == "requirement":
        keyword_sets = _REQ_REQUIRED_KEYWORDS
    else:
        return {"status": "skip", "detail": f"no required-sections rules for doc_type={doc_type}"}

    headings = [
        m.group(1).strip().lower()
        for m in re.finditer(r"^#{1,2}\s+(.+?)\s*$", body, re.MULTILINE)
    ]
    missing: list[str] = []
    for keyword_set in keyword_sets:
        if not any(kw in h for h in headings for kw in keyword_set):
            missing.append(" / ".join(keyword_set))
    if missing:
        return {
            "status": "fail",
            "detail": f"missing required sections: {missing}",
            "found_headings": headings[:12],
        }
    return {"status": "pass", "detail": f"{len(headings)} headings found; all required present"}


# --- requirement doc-type gates ---

def _check_requirement_blocks(body: str, doc_type: str) -> dict:
    """Every H4 req block has BOTH attributes table + detail table."""
    if doc_type != "requirement":
        return {"status": "skip", "detail": "not a requirement doc"}

    h4_matches = list(_REQ_H4_RE.finditer(body))
    if not h4_matches:
        return {"status": "fail", "detail": "no H4 requirement blocks found (`#### KEY — SUMMARY`)"}

    issues: list[str] = []
    for i, m in enumerate(h4_matches):
        start = m.start()
        end = h4_matches[i + 1].start() if i + 1 < len(h4_matches) else len(body)
        span = body[start:end]
        heading = m.group(0).strip()

        if not _REQ_ATTR_HEADER_RE.search(span):
            issues.append(f"{heading}: missing 6-col attributes table")
        if not _REQ_DETAIL_HEADER_RE.search(span):
            issues.append(f"{heading}: missing HTML detail table (Field/Value/Criticality)")

    if issues:
        return {
            "status": "fail",
            "detail": f"{len(issues)} shape issues across {len(h4_matches)} H4 blocks",
            "issues": issues[:10],
        }
    return {
        "status": "pass",
        "detail": f"{len(h4_matches)} H4 blocks all carry both attributes + detail tables",
    }


def _check_requirement_classification_cells(body: str, doc_type: str) -> dict:
    """Every attributes-table Classification cell has ≥1 canonical tag."""
    if doc_type != "requirement":
        return {"status": "skip", "detail": "not a requirement doc"}

    # Attributes table data row follows the separator: `|---|---|...|` then `| v1 | v2 | ...` (6 cells)
    bad: list[str] = []
    rows = re.finditer(
        r"\|\s*Key\s*\|\s*Traces To\s*\|\s*Epic\s*\|\s*Classification\s*\|\s*Target\s*\|\s*Status\s*\|\s*\n"
        r"\|[^\n]*\n"
        r"(\|[^\n]+\|)",
        body,
        re.IGNORECASE,
    )
    count = 0
    for m in rows:
        count += 1
        data_row = m.group(1)
        cells = [c.strip() for c in data_row.strip().strip("|").split("|")]
        if len(cells) < 6:
            bad.append(f"row {count}: expected 6 cells, got {len(cells)}")
            continue
        class_cell = cells[3]
        found_tags = set(re.findall(r"`([a-z]+)`", class_cell)) & _CANONICAL_CLASS_TAGS
        if not found_tags:
            bad.append(f"row {count}: classification cell has no canonical tag ({class_cell[:60]})")
    if count == 0:
        return {"status": "fail", "detail": "no attributes-table data rows parseable"}
    if bad:
        return {"status": "fail", "detail": f"{len(bad)}/{count} rows have bad Classification", "issues": bad[:10]}
    return {"status": "pass", "detail": f"{count}/{count} rows have ≥1 canonical classification tag"}


def _check_requirement_aggregate(raw_md: str, body: str, doc_type: str) -> dict:
    """Frontmatter has `requirements:` aggregate whose `count` matches H4 block count."""
    if doc_type != "requirement":
        return {"status": "skip", "detail": "not a requirement doc"}

    h4_count = len(_REQ_H4_RE.findall(body))

    fm_match = re.match(r"(?s)\A---\s*\n(.*?)\n---\s*\n", raw_md)
    fm_region = fm_match.group(1) if fm_match else ""
    agg_match = re.search(r"(?ms)^requirements:\s*\n((?:^[ \t].+\n)+)", fm_region)
    if not agg_match:
        return {
            "status": "fail",
            "detail": f"frontmatter missing `requirements:` aggregate (body has {h4_count} H4 blocks)",
        }
    count_match = re.search(r"^\s+count:\s*(\d+)", agg_match.group(1), re.MULTILINE)
    if not count_match:
        return {"status": "fail", "detail": "`requirements:` aggregate has no `count:` field"}
    agg_count = int(count_match.group(1))
    if agg_count != h4_count:
        return {
            "status": "fail",
            "detail": f"aggregate count={agg_count} but body has {h4_count} H4 blocks",
        }
    return {"status": "pass", "detail": f"aggregate count={agg_count} matches body H4 count"}


def _check_requirement_traces_to(body: str, doc_type: str) -> dict:
    """Warn on Traces To values that don't match DI-/UN- prefix — legal but
    flag for human review."""
    if doc_type != "requirement":
        return {"status": "skip", "detail": "not a requirement doc"}

    unresolved: list[str] = []
    # Attributes-table data rows
    for m in re.finditer(
        r"\|\s*Key\s*\|[^\n]*\n\|[^\n]*\n(\|[^\n]+\|)",
        body,
        re.IGNORECASE,
    ):
        data_row = m.group(1)
        cells = [c.strip() for c in data_row.strip().strip("|").split("|")]
        if len(cells) < 6:
            continue
        traces_cell = cells[1].strip()
        # Strip link wrap + inline-code for the ID check
        stripped = re.sub(r"^\[([^\]]+)\]\([^)]+\)$", r"\1", traces_cell).strip("`").strip()
        if stripped.lower() == "null":
            unresolved.append(cells[0])
            continue
        if not _TRACES_TO_ID_RE.match(stripped):
            unresolved.append(f"{cells[0]}: traces_to={traces_cell[:40]}")

    if unresolved:
        return {
            "status": "warn",
            "detail": f"{len(unresolved)} requirements have unresolved/non-ID Traces To",
            "unresolved": unresolved[:10],
        }
    return {"status": "pass", "detail": "all Traces To values resolve to DI-/UN- IDs"}


def _check_requirement_ctf_inference(body: str, doc_type: str) -> dict:
    """CtF must NEVER be auto-inferred per R1b. Warn on `CtF` (inferred) cells."""
    if doc_type != "requirement":
        return {"status": "skip", "detail": "not a requirement doc"}
    hits = _CTF_INFERRED_RE.findall(body)
    if hits:
        return {
            "status": "warn",
            "detail": f"{len(hits)} cell(s) mark CtF as inferred — CtF requires human IFU assessment per R1b",
        }
    return {"status": "pass", "detail": "no auto-inferred CtF cells"}


def _check_disallowed_element_types(body: str, doc_type: str) -> dict:
    """Architecture disallows type=d (matrix Mermaid) and colored/nested/positional tables."""
    if doc_type != "architecture":
        return {"status": "skip", "detail": "doc-type specific; only architecture enforced today"}

    disallowed_f11: list[str] = []
    for m in _F11_CLASSIFY.finditer(body):
        attrs = _parse_marker_attrs(m.group("attrs"))
        if attrs.get("type") == "d":
            disallowed_f11.append(attrs.get("descriptor", "?"))

    bg_color_tables = len(re.findall(r'style="background-color', body, re.IGNORECASE))

    if disallowed_f11 or bg_color_tables > 0:
        return {
            "status": "fail",
            "detail": (
                f"architecture doc has {len(disallowed_f11)} type=d markers "
                f"and {bg_color_tables} colored table cells (both disallowed)"
            ),
            "type_d_descriptors": disallowed_f11,
        }
    return {"status": "pass", "detail": "no disallowed element types"}


def _check_mermaid_warning(body: str, doc_type: str) -> dict:
    """Architecture expects Mermaid; zero fences is a warning."""
    if doc_type != "architecture":
        return {"status": "skip", "detail": "only architecture expected to have Mermaid"}
    count = len(_MERMAID_FENCE.findall(body))
    if count == 0:
        return {"status": "warn", "detail": "architecture doc has zero mermaid fences"}
    return {"status": "pass", "detail": f"{count} mermaid fences"}


# --- Orchestration ---

def validate(
    md_path: Path,
    expected_k: Optional[int] = None,
    expected_k_anchors: Optional[int] = None,
) -> dict:
    md = md_path.read_text(encoding="utf-8")
    fm, body = _parse_frontmatter(md)

    checks: dict[str, dict] = {}

    doc_classify = _check_doc_classify(body)
    checks["doc_classify_marker"] = doc_classify
    # Resolve doc_type — prefer DOC-CLASSIFY marker, fall back to frontmatter
    doc_type = (
        doc_classify.get("attrs", {}).get("doc_type")
        if doc_classify["status"] != "fail"
        else None
    ) or fm.get("doc_type", "")

    checks["f11_classify_adjacency"] = _check_f11_adjacency(body)
    checks["doc_version_shape"] = _check_doc_version(fm)
    checks["filename_no_version_suffix"] = _check_filename_no_version_suffix(md_path)
    checks["image_path_prefix"] = _check_image_refs(body)
    checks["hyperlink_consistency"] = _check_hyperlink_consistency(fm, body)
    checks["link_count_floor"] = _check_link_count_floor(body, expected_k, expected_k_anchors)
    checks["required_sections"] = _check_required_sections(body, doc_type)
    checks["disallowed_elements"] = _check_disallowed_element_types(body, doc_type)
    checks["mermaid_presence_warning"] = _check_mermaid_warning(body, doc_type)

    # --- requirement doc-type gates ---
    if doc_type == "requirement":
        checks["requirement_blocks"] = _check_requirement_blocks(body, doc_type)
        checks["requirement_classification"] = _check_requirement_classification_cells(body, doc_type)
        checks["requirement_aggregate"] = _check_requirement_aggregate(md, body, doc_type)
        checks["requirement_traces_to"] = _check_requirement_traces_to(body, doc_type)
        checks["requirement_ctf_never_inferred"] = _check_requirement_ctf_inference(body, doc_type)

    errors = [name for name, r in checks.items() if r["status"] == "fail"]
    warnings = [name for name, r in checks.items() if r["status"] == "warn"]
    result = "fail" if errors else "pass"

    return {
        "result": result,
        "doc_type": doc_type,
        "md_path": str(md_path),
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
    }


def _self_test() -> int:
    """Smoke-test against existing adopted MDs in the repo."""
    repo = Path(__file__).resolve().parents[4]
    targets = [
        repo / "docs/project/dhfs/hiplink-intra-op/design-controls/architecture"
              / "HipLink IntraOp - Software Architecture Document (SAD) - 1.0.0.md",
    ]
    fails = 0
    for t in targets:
        if not t.exists():
            print(f"[self-test] SKIP: {t} (not found)")
            continue
        r = validate(t)
        print(f"\n=== {t.name} ===")
        print(json.dumps(r, indent=2))
        if r["result"] == "fail":
            # v29 MDs are EXPECTED to fail some v30 gates (no DOC-CLASSIFY marker,
            # no F11-CLASSIFY markers). That's the point — v30 validate is stricter.
            # Report the deltas, don't fail the self-test.
            print(f"[self-test] v29 MD has {len(r['errors'])} expected v30 gaps: {r['errors']}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("md", nargs="?", help="Path to the MD to validate (omit for --self-test)")
    ap.add_argument(
        "--expected-hyperlink-count",
        type=int,
        default=None,
        help="Phase-2-splice K total (for link-count floor check); omit to skip this gate",
    )
    ap.add_argument(
        "--expected-anchor-count",
        type=int,
        default=None,
        help=("Phase-2-splice K-anchor (same-page `](#...)` count in the cache). "
              "Subtracted from K to compute the content-link ratio. Optional."),
    )
    ap.add_argument("--self-test", action="store_true", help="Run smoke tests against repo MDs")
    args = ap.parse_args()

    if args.self_test:
        return _self_test()

    if not args.md:
        ap.error("md path required (or pass --self-test)")

    md_path = Path(args.md).expanduser().resolve()
    if not md_path.exists():
        print(json.dumps({"error": f"file not found: {md_path}"}), file=sys.stderr)
        return 1

    result = validate(
        md_path,
        expected_k=args.expected_hyperlink_count,
        expected_k_anchors=args.expected_anchor_count,
    )
    print(json.dumps(result, indent=2))
    return 0 if result["result"] == "pass" else 2


if __name__ == "__main__":
    sys.exit(main())
