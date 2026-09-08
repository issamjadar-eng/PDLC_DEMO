#!/usr/bin/env python3
"""Narrative-knob check (corpus asserts.command seam) for finance/internal-gl-budget.

Proves the seeded budget story on the normalized CSV: R&D and Regulatory/Quality
run OVER budget year-to-date (beyond +5%), Sales & Marketing runs UNDER (beyond
-5%) with a headcount shortfall, and the other three functions stay inside +/-5%.
Non-zero exit fails acquire/validate.

Usage: python3 check_knobs.py <normalized_dir>/records.csv   (cwd = dataset dir)
"""
import csv, sys

TOL = 0.05


def main():
    with open(sys.argv[1], newline="") as f:
        rows = list(csv.DictReader(f))
    agg = {}
    for r in rows:
        b, a, hb, ha = agg.get(r["function"], (0, 0, 0, 0))
        agg[r["function"]] = (b + int(r["budget_usd"]), a + int(r["actual_usd"]),
                              hb + int(r["headcount_budget"]), ha + int(r["headcount_actual"]))
    var = {f: (a - b) / b for f, (b, a, _, _) in agg.items()}
    fails = []
    for f in ("R&D", "Regulatory/Quality"):
        if var.get(f, 0) <= TOL:
            fails.append(f"{f} YTD variance {var.get(f, 0):+.3f} not over +{TOL}")
    if var.get("Sales & Marketing", 0) >= -TOL:
        fails.append(f"Sales & Marketing YTD variance {var.get('Sales & Marketing', 0):+.3f} not under -{TOL}")
    _, _, hb, ha = agg["Sales & Marketing"]
    if ha >= hb:
        fails.append(f"Sales & Marketing headcount actual {ha} not below budget {hb}")
    for f in ("Manufacturing", "G&A", "Service"):
        if abs(var.get(f, 1)) > TOL:
            fails.append(f"{f} YTD variance {var.get(f, 1):+.3f} outside +/-{TOL}")
    if fails:
        print("check_knobs FAILED:\n  " + "\n  ".join(fails))
        return 1
    print("check_knobs OK: " + ", ".join(f"{f} {v:+.1%}" for f, v in sorted(var.items())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
