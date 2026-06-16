#!/usr/bin/env python3
"""verify-conversion.py — PDF→markdown conversion fidelity gate (standalone corpus-audit CLI).

NOTE (ben/250): the conversion-fidelity check now also lives in the **docflow** skill at
`.claude/skills/docflow/scripts/verify_conversion_fidelity.py`, where it is the canonical
home — wired into the conversion pipeline (`validate_phase7.py` `prose_fidelity` check +
the `fidelity_adjudicator` agent) so every docflow conversion is gated, not just manually
audited. That version exposes an importable `assess()` core and a two-tier pass/warn
verdict (warn → adjudicate; never auto-fail on word-count alone).

This copy is retained for **ad-hoc auditing of the bundled reference-library corpus**
(`--dir .claude/skills/medtech-docs/references/fda-guidance`) — its original purpose. The
two share the same shingle-diff algorithm; keep them in sync, or consolidate (the
references README pointer is mykhailo/005's to repoint if this copy is retired).

Detects the failure mode where an LLM-assisted PDF→markdown conversion silently
*regenerates* prose (fluent, plausible, but absent from the source PDF) instead of
faithfully transcribing it — the defect that contaminated a guidance `source-md/`
appendix with fabricated worked examples.

Method (deterministic, no LLM): extract the PDF text with `pdftotext -layout`,
normalize both sides, and find the longest contiguous runs of markdown words that
do not appear in the PDF as 8-word shingles. Faithful transcriptions have only
short invented runs (editorial headings, added structure); a regenerated passage
shows as a long invented run (dozens of consecutive words with no PDF match).

This is a high-recall CANDIDATE FINDER, not an adjudicator: heavily reformatted or
table-dense conversions can produce long runs that are reformatting, not fabrication
— a human confirms each flagged span. Whole-file coverage% is intentionally NOT the
signal (a small fabricated section barely moves it); the localized longest-run is.

Usage:
  verify-conversion.py <file.pdf> <file.md>          # one pair
  verify-conversion.py --dir <dir>                    # all <dir>/source/*.pdf vs <dir>/source-md/<base>.md
  [--span N]    invented-run length (words) to report          (default 25)
  [--fail N]    exit non-zero if any run >= N words             (default 40; gate threshold)
  [--top K]     show up to K longest spans per file             (default 3)

Exit code: 0 if no run >= --fail in any pair; 1 otherwise (so it can gate CI / a hook).
Requires `pdftotext` (poppler-utils) on PATH.
"""
import argparse, os, re, subprocess, sys, glob

def norm_words(s: str):
    s = s.lower()
    s = re.sub(r"contains nonbinding recommendations", " ", s)
    s = re.sub(r"[^a-z0-9 ]", " ", s)          # strip punctuation + markdown syntax
    return re.sub(r"\s+", " ", s).split()

def strip_md_metadata(md: str) -> str:
    return re.sub(r"<!--.*?-->", " ", md, flags=re.S)   # leading frontmatter / changelog comment blocks

def pdf_text(pdf: str) -> str:
    return subprocess.run(["pdftotext", "-layout", pdf, "-"],
                          capture_output=True, text=True, timeout=120).stdout

def longest_invented_runs(md_words, pdf_words, n=8):
    pset = {" ".join(pdf_words[i:i+n]) for i in range(len(pdf_words) - n + 1)}
    present = [(" ".join(md_words[i:i+n]) in pset) for i in range(max(0, len(md_words) - n + 1))]
    covered = [False] * len(md_words)
    for i, ok in enumerate(present):
        if ok:
            for j in range(i, i + n):
                if j < len(covered):
                    covered[j] = True
    runs, start = [], None
    for j, c in enumerate(md_words):
        if not covered[j] and start is None:
            start = j
        elif covered[j] and start is not None:
            runs.append((start, j)); start = None
    if start is not None:
        runs.append((start, len(md_words)))
    return sorted(runs, key=lambda r: r[1] - r[0], reverse=True)

def check_pair(pdf, md, span, top):
    pw = norm_words(pdf_text(pdf))
    mw = norm_words(strip_md_metadata(open(md, encoding="utf-8", errors="replace").read()))
    if not mw:
        return 0, []
    runs = [r for r in longest_invented_runs(mw, pw) if (r[1] - r[0]) >= span]
    out = []
    for s, e in runs[:top]:
        snippet = " ".join(mw[s:e])
        out.append((e - s, snippet[:160] + ("…" if len(snippet) > 160 else "")))
    return (runs[0][1] - runs[0][0]) if runs else 0, out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf", nargs="?"); ap.add_argument("md", nargs="?")
    ap.add_argument("--dir"); ap.add_argument("--span", type=int, default=25)
    ap.add_argument("--fail", type=int, default=40); ap.add_argument("--top", type=int, default=3)
    a = ap.parse_args()

    pairs = []
    if a.dir:
        for pdf in sorted(glob.glob(os.path.join(a.dir, "source", "*.pdf"))):
            base = os.path.splitext(os.path.basename(pdf))[0]
            md = os.path.join(a.dir, "source-md", base + ".md")
            if os.path.isfile(md):
                pairs.append((pdf, md))
    elif a.pdf and a.md:
        pairs.append((a.pdf, a.md))
    else:
        ap.error("provide <pdf> <md> or --dir <dir>")

    worst = 0
    print(f"{'file':40} {'longest invented run':>20}")
    print("-" * 64)
    flagged = []
    for pdf, md in pairs:
        try:
            mx, spans = check_pair(pdf, md, a.span, a.top)
        except Exception as e:
            print(f"{os.path.basename(md):40} {'ERROR: ' + str(e)[:18]:>20}"); continue
        worst = max(worst, mx)
        mark = "  ⛔ FAIL" if mx >= a.fail else ("  ⚠" if mx >= a.span else "")
        print(f"{os.path.basename(md):40} {str(mx) + ' words':>20}{mark}")
        if spans and mx >= a.span:
            flagged.append((md, spans))
    if flagged:
        print("\nLongest invented spans (verify each — fabrication vs reformatting):")
        for md, spans in flagged:
            print(f"\n  {os.path.basename(md)}")
            for n, snip in spans:
                print(f"    [{n}w] {snip}")
    rc = 1 if worst >= a.fail else 0
    print(f"\n{'FAIL' if rc else 'PASS'} — worst invented run {worst} words (fail threshold {a.fail}).")
    return rc

if __name__ == "__main__":
    sys.exit(main())
