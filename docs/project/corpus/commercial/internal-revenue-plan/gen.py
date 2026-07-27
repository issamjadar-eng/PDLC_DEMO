#!/usr/bin/env python3
"""Demo generator — revenue plan of record. Seeded, deterministic.
Stand-in for the FP&A long-range-plan export.

Plan values are literal round numbers (a plan is a negotiated table, not a
random draw) — the seed is accepted for interface consistency but no random
noise is applied. No clocks: literal periods only.

Coherence anchors (locked):
- FY2026 plan ~= $105M, mostly `cleared` (actuals run-rate ~ $95-100M; the plan
  is deliberately a stretch).
- Trajectory reaches ~= $350M in FY2030, of which predictive-monitoring cloud
  revenue (pccp-enabled + new-submission inside cloud-suite) = $210M — the
  predictive-monitoring bet sits behind FUTURE regulatory events.
"""
import argparse, csv, json, random

BANNER = "_Demo sample data - not for clinical use._"
REGION_SHARE = {"NA": 0.55, "EMEA": 0.30, "APAC": 0.15}
QW = {"2026-Q1": 0.22, "2026-Q2": 0.24, "2026-Q3": 0.26, "2026-Q4": 0.28}

M = 1_000_000
# FY2026 plan by line ($M): total 105. Dependency: everything cleared except a
# small cloud-suite letter-to-file slice (incremental non-predictive features).
PLAN_2026 = {"PP3500": 52, "PP3000": 12, "IP5000": 7, "SP6000": 12, "SP6500": 9}
PLAN_2026_CLOUD = {"cleared": 11, "letter-to-file": 2}   # cloud-suite, total 13

# FY2027..FY2030 by line x regulatory dependency ($M), region ALL.
# Row sums: 130 / 170 / 245 / 350. FY2030 cloud pccp-enabled + new-submission
# = 210 — the predictive-monitoring-dependent revenue (target band 180-240).
PLAN_ANNUAL = {
    "FY2027": {"PP3500": {"cleared": 58, "letter-to-file": 4}, "PP3000": {"cleared": 10},
               "IP5000": {"cleared": 5}, "SP6000": {"cleared": 15}, "SP6500": {"cleared": 13},
               "cloud-suite": {"cleared": 14, "pccp-enabled": 8, "new-submission": 3}},
    "FY2028": {"PP3500": {"cleared": 60, "letter-to-file": 8}, "PP3000": {"cleared": 8},
               "IP5000": {"cleared": 4}, "SP6000": {"cleared": 16}, "SP6500": {"cleared": 14},
               "cloud-suite": {"cleared": 20, "pccp-enabled": 30, "new-submission": 10}},
    "FY2029": {"PP3500": {"cleared": 64, "letter-to-file": 10}, "PP3000": {"cleared": 6},
               "IP5000": {"cleared": 3}, "SP6000": {"cleared": 17}, "SP6500": {"cleared": 15},
               "cloud-suite": {"cleared": 25, "pccp-enabled": 75, "new-submission": 30}},
    "FY2030": {"PP3500": {"cleared": 66, "letter-to-file": 12}, "PP3000": {"cleared": 4},
               "IP5000": {"cleared": 2}, "SP6000": {"cleared": 14}, "SP6500": {"cleared": 12},
               "cloud-suite": {"cleared": 30, "pccp-enabled": 140, "new-submission": 70}},
}

def make_rows():
    rows = []
    # FY2026: quarterly x region
    for period, qw in QW.items():
        for region, rs in REGION_SHARE.items():
            for line, total in PLAN_2026.items():
                rows.append({"period": period, "product_line": line, "region": region,
                             "revenue_usd": int(round(total * M * qw * rs)),
                             "regulatory_dependency": "cleared"})
            for dep, total in PLAN_2026_CLOUD.items():
                rows.append({"period": period, "product_line": "cloud-suite", "region": region,
                             "revenue_usd": int(round(total * M * qw * rs)),
                             "regulatory_dependency": dep})
    # FY2027..FY2030: annual x line x dependency, region ALL
    for fy, lines in PLAN_ANNUAL.items():
        for line, deps in lines.items():
            for dep, total in deps.items():
                rows.append({"period": fy, "product_line": line, "region": "ALL",
                             "revenue_usd": total * M, "regulatory_dependency": dep})
    return rows

def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("gen"); g.add_argument("--seed", type=int, default=42); g.add_argument("--out", required=True)
    n = sub.add_parser("normalize"); n.add_argument("raw"); n.add_argument("out")
    a = p.parse_args()
    if a.cmd == "gen":
        random.Random(a.seed)  # interface consistency; plan values are literal
        json.dump({"banner": BANNER, "generator": "gen.py", "seed": a.seed,
                   "as_of": "2026-07-25", "plan_version": "LRP-2026.1 (approved 2026-02-10)",
                   "rows": make_rows()},
                  open(f"{a.out}/export.json", "w"), indent=1)
    else:
        rows = json.load(open(f"{a.raw}/export.json"))["rows"]
        w = csv.DictWriter(open(f"{a.out}/records.csv", "w", newline=""), fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)

main()
