#!/usr/bin/env python3
"""Narrative-knob check (corpus asserts.command seam) for finance/internal-standard-costs.

The dataset's story is a JOIN claim — "legacy hardware actual COGS runs above
standard and the gap widens; PP3500 runs favorable" — so the check reads the
sibling commercial/internal-financials LATEST snapshot (actual cogs_usd / units)
and proves the knob against it. Non-zero exit fails acquire/validate.

Usage: python3 check_knobs.py <normalized_dir>/records.csv   (cwd = dataset dir)
"""
import csv, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIN = HERE.parent.parent / "commercial" / "internal-financials"
WIDEN_MIN_PTS = 5.0   # last-quarter minus first-quarter unfavorable variance, pts of standard


def load(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def main():
    std = load(sys.argv[1])
    latest = (FIN / "latest").read_text().strip()
    fin = load(FIN / "snapshots" / latest / "normalized" / "records.csv")
    act = {}
    for r in fin:
        k = (r["period"], r["product_line"], r["revenue_type"])
        c, u = act.get(k, (0, 0))
        act[k] = (c + int(r["cogs_usd"]), u + int(r["units"]))
    var = {}
    for r in std:
        k = (r["period"], r["product_line"], r["revenue_type"])
        if k not in act or not act[k][1]:
            continue
        actual_unit = act[k][0] / act[k][1]
        var[k] = 100.0 * (actual_unit - float(r["std_unit_cost_usd"])) / float(r["std_unit_cost_usd"])
    quarters = sorted({k[0] for k in var})
    fails = []
    for line in ("PP3000", "IP5000"):
        vs = [var[(q, line, "hardware")] for q in quarters]
        if not all(v > 0 for v in vs):
            fails.append(f"{line} hardware not unfavorable in every quarter: {[round(v, 1) for v in vs]}")
        if vs[-1] - vs[0] < WIDEN_MIN_PTS:
            fails.append(f"{line} hardware variance widened only {vs[-1] - vs[0]:.1f} pts (< {WIDEN_MIN_PTS})")
    vs = [var[(q, "PP3500", "hardware")] for q in quarters]
    if not all(v < 0 for v in vs):
        fails.append(f"PP3500 hardware not favorable in every quarter: {[round(v, 1) for v in vs]}")
    if fails:
        print("check_knobs FAILED:\n  " + "\n  ".join(fails))
        return 1
    print(f"check_knobs OK: legacy hardware unfavorable + widening, PP3500 favorable "
          f"(vs commercial/internal-financials@{latest}, {len(quarters)} quarters)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
