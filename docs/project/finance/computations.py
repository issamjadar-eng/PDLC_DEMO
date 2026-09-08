#!/usr/bin/env python3
"""Deterministic computations for the PDLC_DEMO Finance business-question catalog.

Contract (per the commercial skill, `--domain finance`): invoked as
    python3 computations.py <FQ-ID> --corpus-root <abs> --out <abs-edition-dir>
with cwd = docs/project/finance/. Reads {out}/pins.json and computes ONLY from the
pinned snapshots. Writes report.md + data.json. Deterministic: no clocks, no network —
"as-of" dates derive from the data itself. Internal (fabricated) data reports carry the
demo banner.

This file is the domain-local SHARED HELPER LAYER only — every question lives in its
own module at bq_modules/fq_nn.py exposing run(corpus_root, out, pins); the dispatcher
below imports it by name. Keep question-specific code out of this file.
"""

import argparse
import csv
import json
from pathlib import Path

import yaml

BANNER = "_Demo sample data — not for clinical use._"
CATALOG = "finance.yml"
CONFIG_MARKER = f"config: {CATALOG}"


def assert_vocab(rows, field, known, dataset):
    """Fail loud when a column carries values outside the known vocabulary —
    complement-defined populations must not silently absorb new upstream values."""
    unknown = {r[field] for r in rows} - set(known)
    if unknown:
        raise SystemExit(f"{dataset}: unexpected {field} value(s) {sorted(unknown)} — "
                         f"update the vocabulary sets and derivation strings before answering")


def load_pin_csv(corpus_root, pins, dataset):
    snap = pins[dataset]
    path = corpus_root / dataset / "snapshots" / snap / "normalized" / "records.csv"
    with open(path, newline="") as f:
        return list(csv.DictReader(f)), snap


def _entry(fq):
    cfg = yaml.safe_load(open(CATALOG))
    for q in cfg["questions"]:
        if q["id"] == fq:
            return q
    return {}


def params_for(fq):
    return _entry(fq).get("params", {})


def expectations_for(fq):
    return _entry(fq).get("expectations", [])


def evaluate_expectations(fq, results):
    """Join catalog expectations with computed {id: (actual, verdict, evidence[])}.
    Verdicts: met | at-risk | not-met | not-evaluable. Every expectation in the
    catalog appears in the output — an unevaluated expectation is itself a finding.
    The inverse also fails loud: a computed result whose id is not in the catalog
    (a typo'd E-id) must not silently vanish."""
    exps = expectations_for(fq)
    unknown = set(results) - {e["id"] for e in exps}
    if unknown:
        raise SystemExit(f"{fq}: computed expectation result id(s) {sorted(unknown)} not in "
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
             "in a plan of record or the risk file — challenge the assumption, not just the actual._", "",
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
    """RENDER-side percentage (rounded 1dp). Convention (round-before-compare):
    verdict/threshold decisions must compare UNROUNDED values (pct_raw or the raw
    quotient); rounding happens only at render time."""
    return round(100.0 * n / d, 1) if d else 0.0


def pct_raw(n, d):
    """COMPARE-side percentage — unrounded fraction*100 for threshold/verdict tests."""
    return 100.0 * n / d if d else 0.0


def musd(v):
    """Render-side dollars in $M, 2dp — finance figures are smaller than revenue totals,
    so one decimal would collapse warranty / working-capital numbers to zero."""
    return round(v / 1e6, 2)


def kusd(v):
    """Render-side dollars in $K, integer."""
    return int(round(v / 1e3))


def month_iso(period):
    """'YYYY-MM' -> ISO date of the month's first day (timeseries x axis)."""
    return f"{period}-01"


def quarter_iso(period):
    """'YYYY-Qn' -> ISO date of the quarter's first day (timeseries x axis)."""
    y, q = period.split("-Q")
    return f"{y}-{(int(q) - 1) * 3 + 1:02d}-01"


def flow_weighted_days(rows, amount_field, days_field):
    """Aggregate a days-type ratio (DSO, inventory days) over a slice by implied daily
    flow: sum(amount) / sum(amount / days). Ratios never average; this is the
    convention the internal-ar-inventory README declares. Returns None when empty."""
    amount = sum(float(r[amount_field]) for r in rows)
    daily = sum(float(r[amount_field]) / float(r[days_field]) for r in rows if float(r[days_field]))
    return amount / daily if daily else None


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


DISPATCH = {}


def module_dispatch(fq):
    """Per-question module: bq_modules/fq_nn.py exposing run(corpus_root, out, pins)."""
    mod_name = "bq_modules." + fq.lower().replace("-", "_")
    try:
        import importlib
        return importlib.import_module(mod_name).run
    except ModuleNotFoundError as e:
        # Only "the dispatched module itself does not exist" means no computation;
        # a ModuleNotFoundError raised INSIDE an existing module must fail loud.
        if e.name != mod_name and not (e.name and mod_name.startswith(e.name + ".")):
            raise
        return None


def main():
    p = argparse.ArgumentParser()
    p.add_argument("fq")
    p.add_argument("--corpus-root", required=True)
    p.add_argument("--out", required=True)
    a = p.parse_args()
    out, corpus_root = Path(a.out), Path(a.corpus_root)
    pins = json.loads((out / "pins.json").read_text())
    fn = DISPATCH.get(a.fq) or module_dispatch(a.fq)
    if fn is None:
        raise SystemExit(f"no computation for {a.fq}")
    fn(corpus_root, out, pins)


if __name__ == "__main__":
    main()
