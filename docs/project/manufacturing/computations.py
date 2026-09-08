#!/usr/bin/env python3
"""Deterministic computations for the PDLC_DEMO Manufacturing business-question catalog.

Contract (per the commercial skill, run with --domain manufacturing): invoked as
    python3 computations.py <MQ-ID> --corpus-root <abs> --out <abs-edition-dir>
with cwd = docs/project/manufacturing/. Reads {out}/pins.json and computes ONLY from the
pinned snapshots. Writes report.md + data.json. Deterministic: no clocks, no network —
"as-of" dates come from the pinned snapshot's provenance (`as_of`), never the machine
clock. Internal (fabricated) data reports carry the demo banner.

This file holds the SHARED helper layer only (a domain-local copy of the commercial
tree's helpers). Every question lives in its own module: bq_modules/mq_nn.py exposing
run(corpus_root, out, pins).
"""

import argparse
import csv
import datetime as dt
import json
from pathlib import Path

import yaml

BANNER = "_Demo sample data — not for clinical use._"
CATALOG = "manufacturing.yml"
CONFIG_MARKER = f"config: {CATALOG}"


def assert_vocab(rows, field, known, dataset):
    """Fail loud when a column carries values outside the known vocabulary —
    complement-defined populations must not silently absorb new upstream values."""
    unknown = {r[field] for r in rows} - set(known)
    if unknown:
        raise SystemExit(f"{dataset}: unexpected {field} value(s) {sorted(unknown)} — "
                         f"update the status sets and derivation strings before answering")


def load_pin_csv(corpus_root, pins, dataset):
    snap = pins[dataset]
    path = corpus_root / dataset / "snapshots" / snap / "normalized" / "records.csv"
    with open(path, newline="") as f:
        return list(csv.DictReader(f)), snap


def snapshot_as_of(corpus_root, pins, dataset):
    """The data's as-of date for urgency / aging math: the pinned snapshot's provenance
    `as_of` (set from dataset.yml data_through), falling back to the snapshot id date.
    Never the machine clock — that would make the answer non-reproducible."""
    snap = pins[dataset]
    prov = corpus_root / dataset / "snapshots" / snap / "provenance.yml"
    if prov.exists():
        as_of = yaml.safe_load(open(prov)).get("as_of")
        if as_of:
            return str(as_of)
    return snap.split(".")[0]


def days_between(a, b):
    """b − a in days for ISO dates (positive when b is later)."""
    return (dt.date.fromisoformat(b) - dt.date.fromisoformat(a)).days


def month_range(a, b):
    """Every YYYY-MM from a to b inclusive — zero-filled trend lines make stalls
    VISIBLE instead of silently skipping empty months."""
    y, m = int(a[:4]), int(a[5:7])
    ey, em = int(b[:4]), int(b[5:7])
    out = []
    while (y, m) <= (ey, em):
        out.append(f"{y}-{m:02d}")
        m += 1
        if m > 12:
            y, m = y + 1, 1
    return out


def trailing_months(as_of, n):
    """The n calendar months ending with as_of's month (inclusive), as YYYY-MM."""
    y, m = int(as_of[:4]), int(as_of[5:7])
    out = []
    for _ in range(n):
        out.append(f"{y}-{m:02d}")
        m -= 1
        if m == 0:
            y, m = y - 1, 12
    return list(reversed(out))


def mean(vals):
    vals = list(vals)
    return sum(vals) / len(vals) if vals else None


def median(vals):
    vals = sorted(vals)
    n = len(vals)
    if not n:
        return None
    return vals[n // 2] if n % 2 else (vals[n // 2 - 1] + vals[n // 2]) / 2


def _entry(bq):
    cfg = yaml.safe_load(open(CATALOG))
    for q in cfg["questions"]:
        if q["id"] == bq:
            return q
    return {}


def params_for(bq):
    return _entry(bq).get("params", {})


def expectations_for(bq):
    return _entry(bq).get("expectations", [])


def evaluate_expectations(bq, results):
    """Join catalog expectations with computed {id: (actual, verdict, evidence[])}.
    Verdicts: met | at-risk | not-met | not-evaluable. Every expectation in the
    catalog appears in the output — an unevaluated expectation is itself a finding.
    The inverse also fails loud: a computed result whose id is not in the catalog
    (a typo'd E-id) must not silently vanish."""
    exps = expectations_for(bq)
    unknown = set(results) - {e["id"] for e in exps}
    if unknown:
        raise SystemExit(f"{bq}: computed expectation result id(s) {sorted(unknown)} not in "
                         f"the {CATALOG} catalog — fix the id or declare the expectation")
    out = []
    for e in exps:
        actual, verdict, evidence = results.get(e["id"], ("not evaluated by this computation", "not-evaluable", []))
        out.append({**e, "actual": actual, "verdict": verdict, "evidence": evidence})
    return out


def expectations_section(exps):
    """Linted report rendering of the expectations table."""
    if not exps:
        return []
    lines = ["", "## Assumptions & expectations — plan vs actual", "",
             "_`unvalidated` means the expectation itself is a stand-in that has not been grounded",
             "in a plan of record, a procedure, or the risk file — challenge the assumption, not just the actual._", "",
             "| ID | Expectation | Expected | Actual | Verdict | Basis |",
             "|---|---|---|---|---|---|"]
    for e in exps:
        ev_items = list(e.get("evidence", []))
        # the expectation row always cites the catalog it comes from — but only once
        if CONFIG_MARKER not in ev_items:
            ev_items.append(CONFIG_MARKER)
        ev = " ".join(f"[{x}]" for x in ev_items)
        val = "" if e.get("validated") else " (unvalidated)"
        lines.append(f"| {e['id']} | {e['statement']} {ev} | {e['expected']} | "
                     f"{e['actual']} | {e['verdict']}{val} | {e['basis']} |")
    return lines


def write(out, report_lines, data):
    (out / "report.md").write_text("\n".join(report_lines) + "\n")
    (out / "data.json").write_text(json.dumps(data, indent=1))


def pct(n, d):
    """RENDER-side percentage (rounded 1dp). Convention: verdict/threshold decisions
    compare UNROUNDED values (pct_raw); rounding happens only at render time."""
    return round(100.0 * n / d, 1) if d else 0.0


def pct_raw(n, d):
    """COMPARE-side percentage — unrounded fraction*100 for threshold/verdict tests."""
    return 100.0 * n / d if d else 0.0


def narrative_section(narrative):
    """Render the narrative block into linted report lines (the report is the
    linted surface; data.json mirrors it for the console panel)."""
    lines = ["", "## Narrative — Risks / Mitigations / Issues", ""]
    for grp, title in (("issues", "Issues (materialized — needs action)"),
                       ("risks", "Risks (potential — mitigation identified)"),
                       ("watch", "Watch")):
        items = narrative.get(grp, [])
        if not items:
            continue
        lines.append(f"### {title}")
        lines.append("")
        for it in items:
            ev = " ".join(f"[{e}]" for e in it.get("evidence", []))
            lines.append(f"- **{it['id']} ({it.get('severity', 'medium')})** — {it['statement']} {ev}")
            if it.get("mitigation"):
                lines.append(f"  - _Mitigation_: {it['mitigation']} {ev}")
            if it.get("action"):
                lines.append(f"  - _Action_: {it['action']} {ev}")
        lines.append("")
    return lines


# ---------------------------------------------------------------- main

DISPATCH = {}


def module_dispatch(bq):
    """Per-question module: bq_modules/mq_NN.py exposing run(corpus_root, out, pins)."""
    mod_name = "bq_modules." + bq.lower().replace("-", "_")
    try:
        import importlib
        return importlib.import_module(mod_name).run
    except ModuleNotFoundError as e:
        # Only "the dispatched module itself does not exist" means no computation; a
        # ModuleNotFoundError raised INSIDE an existing module must fail loud.
        if e.name != mod_name and not (e.name and mod_name.startswith(e.name + ".")):
            raise
        return None


def main():
    p = argparse.ArgumentParser()
    p.add_argument("bq")
    p.add_argument("--corpus-root", required=True)
    p.add_argument("--out", required=True)
    a = p.parse_args()
    out, corpus_root = Path(a.out), Path(a.corpus_root)
    pins = json.loads((out / "pins.json").read_text())
    fn = DISPATCH.get(a.bq) or module_dispatch(a.bq)
    if fn is None:
        raise SystemExit(f"no computation for {a.bq}")
    fn(corpus_root, out, pins)


if __name__ == "__main__":
    main()
