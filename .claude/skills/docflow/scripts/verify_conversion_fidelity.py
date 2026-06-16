#!/usr/bin/env python3
"""verify_conversion_fidelity.py — PDF/text→markdown prose-fidelity finder.

Detects the failure mode where an LLM-assisted conversion silently *regenerates*
prose — fluent, plausible, but absent from the source — instead of faithfully
transcribing it. This is the defect that contaminated a guidance `source-md/`
appendix with fabricated worked examples (and bled into downstream submission
docs before anyone noticed).

Method (deterministic, no LLM): extract the source text (`pdftotext -layout` for
PDFs, or a caller-supplied baseline for other formats), normalize both sides, and
find the longest contiguous runs of markdown words that do not appear in the
source as 8-word shingles. Faithful transcriptions have only short invented runs
(editorial headings, added structure); a regenerated passage shows as a long
invented run (dozens of consecutive words with no source match).

Two-tier verdict (the signal is the LOCALIZED longest run, never whole-file
coverage% — a small fabricated section barely moves coverage):
  - longest run >= `fail`  (catastrophic) → "fail"  — almost never reformatting.
  - longest run >= `span`  (moderate)     → "warn"  — emit spans for adjudication.
  - otherwise                             → "pass".

This is a high-recall CANDIDATE FINDER, not an adjudicator: heavily reformatted or
table-dense conversions can produce long runs that are reformatting, not
fabrication. The `warn` band is meant to be handed to the fidelity-adjudicator
agent (or a human), which rules each flagged span fabrication-vs-reformatting
against the source region. Only confirmed fabrications should block a commit.

Importable API (used by `validate_phase7.py`):
  - assess(md_text, source_text, span=25, fail=80, top=3) -> dict
  - extract_source_words(source_path) -> list[str] | None   (None if unsupported)
  - longest_invented_runs(md_words, src_words, n=8) -> list[(start, end)]

CLI:
  verify_conversion_fidelity.py <source.pdf> <file.md>     # one pair
  verify_conversion_fidelity.py --dir <dir>                # <dir>/source/*.pdf vs <dir>/source-md/<base>.md
  [--span N]   moderate-run length (words) → warn          (default 25)
  [--fail N]   catastrophic-run length (words) → fail       (default 80)
  [--top  K]   show up to K longest spans per file          (default 3)
  [--json]     emit a JSON report instead of the text table

Exit code: 0 if no pair reaches `fail`; 2 if any pair fails; 1 on invocation error.
Requires `pdftotext` (poppler-utils) on PATH for PDF sources.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import subprocess
import sys

SHINGLE = 8  # n-gram length for the "present in source" test


def norm_words(s: str) -> list[str]:
    s = s.lower()
    s = re.sub(r"contains nonbinding recommendations", " ", s)  # FDA boilerplate footer
    s = re.sub(r"[^a-z0-9 ]", " ", s)  # strip punctuation + markdown syntax
    return re.sub(r"\s+", " ", s).split()


def strip_md_metadata(md: str) -> str:
    """Drop HTML-comment metadata zones (frontmatter changelogs, AI-CHANGELOG,
    review markers) so curated metadata headers don't read as 'invented prose'."""
    return re.sub(r"<!--.*?-->", " ", md, flags=re.S)


def pdf_text(pdf: str) -> str:
    return subprocess.run(
        ["pdftotext", "-layout", pdf, "-"],
        capture_output=True, text=True, timeout=180,
    ).stdout


def extract_source_words(source_path: str) -> list[str] | None:
    """Return normalized source words, or None if the format isn't supported here.

    PDF → pdftotext. Other formats return None so the gate SKIPs rather than
    false-fails (the caller may pass an already-extracted baseline via
    `assess(..., source_text=...)` instead — e.g. a DOCX pandoc `raw.md`)."""
    ext = os.path.splitext(source_path)[1].lower()
    if ext == ".pdf":
        return norm_words(pdf_text(source_path))
    return None


def longest_invented_runs(md_words: list[str], src_words: list[str], n: int = SHINGLE):
    """Runs of md_words not covered by any matching n-gram in src_words, longest first."""
    if len(src_words) < n:
        return []
    sset = {" ".join(src_words[i:i + n]) for i in range(len(src_words) - n + 1)}
    present = [" ".join(md_words[i:i + n]) in sset for i in range(max(0, len(md_words) - n + 1))]
    covered = [False] * len(md_words)
    for i, ok in enumerate(present):
        if ok:
            for j in range(i, i + n):
                if j < len(covered):
                    covered[j] = True
    runs, start = [], None
    for j in range(len(md_words)):
        if not covered[j] and start is None:
            start = j
        elif covered[j] and start is not None:
            runs.append((start, j))
            start = None
    if start is not None:
        runs.append((start, len(md_words)))
    return sorted(runs, key=lambda r: r[1] - r[0], reverse=True)


def assess(md_text: str, source_text: str, span: int = 25, fail: int = 80, top: int = 3) -> dict:
    """Core reusable check. Returns:
        {"status": "pass|warn|fail", "longest": N, "spans": [{"words": N, "snippet": "..."}]}
    `spans` lists up to `top` invented runs >= `span` words (longest first)."""
    mw = norm_words(strip_md_metadata(md_text))
    sw = norm_words(source_text)
    if not mw or not sw:
        return {"status": "pass", "longest": 0, "spans": [],
                "detail": "empty markdown or source text — nothing to compare"}
    runs = [r for r in longest_invented_runs(mw, sw) if (r[1] - r[0]) >= span]
    longest = (runs[0][1] - runs[0][0]) if runs else 0
    spans = []
    for s, e in runs[:top]:
        snippet = " ".join(mw[s:e])
        spans.append({"words": e - s, "snippet": snippet[:200] + ("…" if len(snippet) > 200 else "")})
    status = "fail" if longest >= fail else ("warn" if longest >= span else "pass")
    return {"status": status, "longest": longest, "spans": spans}


def check_pair(source: str, md: str, span: int, fail: int, top: int) -> dict:
    sw = extract_source_words(source)
    if sw is None:
        return {"status": "skip", "longest": 0, "spans": [],
                "detail": f"unsupported source format for {os.path.basename(source)} — pass a baseline via assess()"}
    md_text = open(md, encoding="utf-8", errors="replace").read()
    # Reuse assess() with the already-extracted words by joining back to text would
    # re-normalize; instead inline the comparison to avoid a double pdftotext.
    mw = norm_words(strip_md_metadata(md_text))
    if not mw:
        return {"status": "pass", "longest": 0, "spans": [], "detail": "empty markdown"}
    runs = [r for r in longest_invented_runs(mw, sw) if (r[1] - r[0]) >= span]
    longest = (runs[0][1] - runs[0][0]) if runs else 0
    spans = []
    for s, e in runs[:top]:
        snippet = " ".join(mw[s:e])
        spans.append({"words": e - s, "snippet": snippet[:200] + ("…" if len(snippet) > 200 else "")})
    status = "fail" if longest >= fail else ("warn" if longest >= span else "pass")
    return {"status": status, "longest": longest, "spans": spans}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("source", nargs="?", help="source file (PDF)")
    ap.add_argument("md", nargs="?", help="converted markdown")
    ap.add_argument("--dir", help="scan <dir>/source/*.pdf vs <dir>/source-md/<base>.md")
    ap.add_argument("--span", type=int, default=25, help="moderate-run length → warn (default 25)")
    ap.add_argument("--fail", type=int, default=80, help="catastrophic-run length → fail (default 80)")
    ap.add_argument("--top", type=int, default=3)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    pairs: list[tuple[str, str]] = []
    if a.dir:
        for src in sorted(glob.glob(os.path.join(a.dir, "source", "*.pdf"))):
            base = os.path.splitext(os.path.basename(src))[0]
            md = os.path.join(a.dir, "source-md", base + ".md")
            if os.path.isfile(md):
                pairs.append((src, md))
    elif a.source and a.md:
        pairs.append((a.source, a.md))
    else:
        ap.error("provide <source> <md> or --dir <dir>")

    results = []
    worst = "pass"
    rank = {"pass": 0, "skip": 0, "warn": 1, "fail": 2}
    for src, md in pairs:
        try:
            r = check_pair(src, md, a.span, a.fail, a.top)
        except Exception as e:  # noqa: BLE001 — report, don't crash a batch
            r = {"status": "error", "detail": str(e)[:120], "longest": 0, "spans": []}
        r["md"] = os.path.basename(md)
        results.append(r)
        if rank.get(r["status"], 0) > rank.get(worst, 0):
            worst = r["status"]

    if a.json:
        print(json.dumps({"worst": worst, "results": results}, indent=2))
    else:
        print(f"{'file':40} {'status':>7} {'longest run':>12}")
        print("-" * 64)
        for r in results:
            print(f"{r['md']:40} {r['status']:>7} {str(r.get('longest', 0)) + 'w':>12}")
        flagged = [r for r in results if r["status"] in ("warn", "fail") and r.get("spans")]
        if flagged:
            print("\nInvented spans (adjudicate each — fabrication vs reformatting):")
            for r in flagged:
                print(f"\n  {r['md']} [{r['status']}]")
                for sp in r["spans"]:
                    print(f"    [{sp['words']}w] {sp['snippet']}")
        print(f"\nworst: {worst}")
    return 2 if worst == "fail" else (1 if worst == "error" else 0)


if __name__ == "__main__":
    sys.exit(main())
