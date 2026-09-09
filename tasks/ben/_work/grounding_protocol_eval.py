#!/usr/bin/env python3
"""Mechanical P1–P4 scorer for TC-PROTO-GROUNDING answers (task ben/123).

Usage: python3 tasks/ben/_work/grounding_protocol_eval.py <run-dir>
  <run-dir> holds q1.md … q6.md — the advisors' verbatim answers captured by the operator.
Prints per-question P1..P4 and the run verdict against §6 of the protocol. Read-only.
"""
import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EXCLUDED = ("articles/", "/_work/", "_work/", "/_scratch/", "_scratch/", "knowledge-pack", "packs/")
MUST_CITE = {  # question -> any of these path fragments satisfies P4
    1: ["docs/project/submissions/510k/composition-manifest.md", "docs/project/input-analysis/predicate-analysis/"],
    2: ["docs/project/strategies/regulatory-strategy.md"],
    3: [".taxonomy.yml", "docs/internal/source-md/Forms/"],
    4: ["docs/external/regulations/qmsr-part-820.md"],
    5: ["docs/project/dhfs/pca-device/design-controls/vnv/", "project.yml"],
    6: ["docs/project/dhfs/pca-device/design-controls/vnv/GL-TMP-UC-003-summative-usability-evaluation.md"],
}
PATH_RE = re.compile(r"(?:`|\()((?:docs|project\.yml|glossary\.md|\.claude|tools|articles|tasks)[^`)\s]*)")

def cited_paths(text):
    out = []
    for m in PATH_RE.finditer(text):
        p = m.group(1).split("#")[0].rstrip(".,;:")
        if p and p not in out:
            out.append(p)
    return out

def main(run_dir):
    run_dir = Path(run_dir)
    p3_viol, p2_fab, p1_fail, p4_hits = [], [], [], 0
    for q in range(1, 7):
        f = run_dir / f"q{q}.md"
        if not f.is_file():
            print(f"q{q}: MISSING answer file"); p1_fail.append(q); continue
        text = f.read_text(encoding="utf-8", errors="replace")
        paths = cited_paths(text)
        exists = {p: (ROOT / p).exists() for p in paths}
        noncanon = [p for p in paths if any(x in p for x in EXCLUDED)]
        fab = [p for p, ok in exists.items() if not ok]
        p4 = any(any(frag in p for frag in MUST_CITE[q]) for p in paths)
        p1 = bool(paths)
        if not p1: p1_fail.append(q)
        p3_viol += [(q, p) for p in noncanon]
        p2_fab += [(q, p) for p in fab]
        p4_hits += p4
        print(f"q{q}: P1={'Y' if p1 else 'N'} cited={len(paths)} P2 fabricated={fab or '-'} "
              f"P3 non-canonical={noncanon or '-'} P4={'Y' if p4 else 'N'}")
    ok = not p3_viol and not p2_fab and not p1_fail and p4_hits >= 5
    print(f"RUN VERDICT: {'PASS' if ok else 'FAIL'}  (P3 violations={len(p3_viol)}, fabricated={len(p2_fab)}, "
          f"P1 failures={p1_fail or '-'}, P4 hits={p4_hits}/6)")
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "."))
