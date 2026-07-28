#!/usr/bin/env python3
"""dossier_lint.py — deterministic structure lint for review dossiers.

Checks any file a --detail-ref points at (filed via record-code-review /
record-verification) against the dossier authoring standard
(templates/review-dossier.md). The prose of a dossier is AI-authored and varies
between runs; this lint bounds that variance mechanically — structure, resolution
vocabulary, table width, machine block, store consistency, jargon coverage.

Usage:
    python3 dossier_lint.py <dossier.md> [--store <code-quality/records.yml>]

Exit 0 when clean (warnings allowed), 1 on any error.
"""

import argparse
import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # --store is optional; only needed when it is used
    yaml = None

# Required level-2 sections, in order. Each entry: (key, heading regex).
REQUIRED_SECTIONS = [
    ("summary", re.compile(r"summary", re.I)),
    ("what-we-checked", re.compile(r"what\s+we\s+checked", re.I)),
    ("findings", re.compile(r"findings", re.I)),
    ("terms-used", re.compile(r"terms\s+used", re.I)),
    ("technical-appendix", re.compile(r"technical\s+appendix", re.I)),
]

RESOLUTION_OK = re.compile(r"^(FIXED|ACCEPTED|NOT YET FIXED)\b")
RESOLUTION_LINE = re.compile(r"^\s*(?:[-*]\s+)?\*\*(Proposed )?Resolution:\*\*\s*(.*)$", re.I)
FINDING_HEAD = re.compile(r"^###\s+F-\S+")
LABELS = ["What's wrong", "Why it matters", "Resolution"]

# Reviewer vocabulary that must be defined in ## Terms used when it appears in a
# Findings entry.
JARGON = ["narrated", "knife-edge", "pins-only", "basis", "denominator",
          "determinism", "monotone"]


def split_fences(lines):
    """Return (prose_lines, fence_blocks). prose_lines: [(lineno, text)] outside
    fenced code; fence_blocks: [(lineno, info_string, [body lines])]."""
    prose, blocks = [], []
    stack = None  # (fence_len, info, start_lineno, body)
    for i, ln in enumerate(lines, 1):
        m = re.match(r"^(`{3,})\s*(\S*)", ln)
        if m and stack is None:
            stack = (len(m.group(1)), m.group(2).lower(), i, [])
            continue
        if m and stack is not None and len(m.group(1)) >= stack[0]:
            blocks.append((stack[2], stack[1], stack[3]))
            stack = None
            continue
        if stack is not None:
            stack[3].append(ln)
        else:
            prose.append((i, ln))
    if stack is not None:
        blocks.append((stack[2], stack[1], stack[3]))  # unclosed — keep body
    return prose, blocks


def lint(path: Path, store_path=None):
    errors, warnings = [], []
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    prose, blocks = split_fences(lines)

    # ---- STRUCTURE: sections present, in order, summary first after title ----
    h2 = [(n, ln) for n, ln in prose if re.match(r"^##\s+", ln)]
    found = {}
    for key, rx in REQUIRED_SECTIONS:
        for n, ln in h2:
            if rx.search(ln) and key not in found:
                found[key] = n
                break
        if key not in found:
            errors.append(f"missing required section: {key} "
                          f"(a `## …` heading matching '{rx.pattern}')")
    order = [(found[k], k) for k, _ in REQUIRED_SECTIONS if k in found]
    if order != sorted(order):
        errors.append("required sections out of order — expected "
                      + " → ".join(k for k, _ in REQUIRED_SECTIONS))
    if h2 and "summary" in found and h2[0][0] != found["summary"]:
        errors.append(f"L{h2[0][0]}: the plain-language Summary must be the FIRST "
                      f"`##` section after the title block (found '{h2[0][1].strip()}')")
    if not any(re.match(r"^#\s+", ln) for _, ln in prose[:5]):
        errors.append("missing title block — the dossier must open with a `# ` title")

    # ---- FINDINGS entries: at least one ### F-, each with the 3 labels ----
    findings_start = found.get("findings")
    findings_end = None
    if findings_start:
        after = [n for n, _ in h2 if n > findings_start]
        findings_end = min(after) if after else len(lines) + 1
    entries = []  # (lineno, heading, [body prose lines])
    if findings_start:
        section = [(n, ln) for n, ln in prose if findings_start < n < findings_end]
        cur = None
        for n, ln in section:
            if FINDING_HEAD.match(ln):
                cur = (n, ln.strip(), [])
                entries.append(cur)
            elif cur:
                cur[2].append(ln)
        if not entries:
            errors.append("Findings section has no `### F-` entry — one entry per "
                          "finding is the mandatory shape (never a table)")
        for n, head, body in entries:
            joined = "\n".join(body)
            for label in LABELS:
                if not re.search(r"\*\*(Proposed )?" + re.escape(label) + r"\b.*?:\*\*",
                                 joined, re.I):
                    errors.append(f"L{n}: finding '{head}' is missing the "
                                  f"**{label}:** line")

    # ---- RESOLUTION VOCABULARY ----
    for n, ln in prose:
        m = RESOLUTION_LINE.match(ln)
        if not m:
            continue
        label_proposed, rest = m.group(1), m.group(2).strip()
        if label_proposed or re.search(r"\bproposed\b", ln, re.I):
            errors.append(f"L{n}: 'proposed' in a Resolution line — audit surfaces "
                          f"carry outcomes (FIXED / ACCEPTED / NOT YET FIXED)")
        if not RESOLUTION_OK.match(rest):
            errors.append(f"L{n}: Resolution must begin FIXED / ACCEPTED / "
                          f"NOT YET FIXED (got: '{rest[:40] or '<empty>'}')")

    # ---- TABLE WIDTH: no markdown table anywhere > 4 columns ----
    for n, ln in prose:
        s = ln.strip()
        if s.startswith("|") and not re.match(r"^\|[\s:|-]+\|$", s):
            cells = [c for c in s.strip("|").split("|")]
            if len(cells) > 4:
                errors.append(f"L{n}: table row has {len(cells)} columns — dossiers "
                              f"render in a console fold, max 4; use stacked entries")

    # ---- MACHINE BLOCK: a fenced json block with a reviews/artifacts array ----
    json_blocks = [(n, "\n".join(body)) for n, info, body in blocks if info == "json"]
    machine, jerrs = None, []
    for n, body in json_blocks:
        try:
            obj = json.loads(body)
        except (ValueError, TypeError) as e:
            jerrs.append(f"L{n}: json block does not parse ({e})")
            continue
        arr = obj.get("reviews") if isinstance(obj, dict) else None
        if arr is None and isinstance(obj, dict):
            arr = obj.get("artifacts")
        if isinstance(arr, list):
            machine = (n, obj, arr)
            break
        jerrs.append(f"L{n}: json block parses but has no `reviews` or `artifacts` array")
    if machine is None:
        if not json_blocks:
            errors.append("missing machine-readable ```json block (with a `reviews` "
                          "or `artifacts` array) at the end of the technical appendix")
        else:
            errors.extend(jerrs)

    # ---- STORE CONSISTENCY (warnings, only with --store) ----
    if store_path and machine:
        if yaml is None:
            warnings.append("--store given but PyYAML is not importable — store "
                            "consistency not checked")
        else:
            store = yaml.safe_load(Path(store_path).read_text(encoding="utf-8")) or {}
            arts = store.get("artifacts", {})
            for entry in machine[2]:
                if not isinstance(entry, dict) or "path" not in entry:
                    continue
                p, v = entry["path"], str(entry.get("verdict", ""))
                recs = arts.get(p)
                if not recs:
                    warnings.append(f"store: no record for '{p}' in {store_path}")
                    continue
                filed = [str(r.get("verdict", ""))
                         for e in recs.get("entries", [])
                         for r in e.get("reviews", [])]
                if v and not any(v.lower() == f.lower() for f in filed):
                    warnings.append(f"store: dossier verdict '{v}' for '{p}' matches "
                                    f"no filed review verdict ({', '.join(sorted(set(filed))) or 'none filed'})")

    # ---- JARGON GUARD (warnings) ----
    if entries and "terms-used" in found:
        terms_end_c = [n for n, _ in h2 if n > found["terms-used"]]
        terms_end = min(terms_end_c) if terms_end_c else len(lines) + 1
        terms_text = "\n".join(ln for n, ln in prose
                               if found["terms-used"] < n < terms_end).lower()
        findings_text = "\n".join(head + "\n" + "\n".join(body)
                                  for _, head, body in entries)
        for term in JARGON:
            if re.search(r"\b" + re.escape(term) + r"\b", findings_text, re.I) \
                    and term not in terms_text:
                warnings.append(f"jargon: '{term}' used in a Findings entry but not "
                                f"defined under ## Terms used")

    return errors, warnings


def main(argv=None):
    p = argparse.ArgumentParser(prog="dossier_lint.py", description=__doc__)
    p.add_argument("dossier", help="path to the dossier markdown file")
    p.add_argument("--store", help="path to code-quality/records.yml for "
                                   "store-consistency warnings")
    args = p.parse_args(argv)
    dp = Path(args.dossier)
    if not dp.is_file():
        print(f"ERROR: no such file: {dp}", file=sys.stderr)
        return 1
    errors, warnings = lint(dp, args.store)
    print(f"[{dp}] dossier lint: {len(errors)} error(s), {len(warnings)} warning(s)")
    for e in errors:
        print(f"  ERROR {e}")
    for w in warnings:
        print(f"  warn  {w}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
