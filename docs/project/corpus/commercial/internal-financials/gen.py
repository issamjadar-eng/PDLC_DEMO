#!/usr/bin/env python3
"""Demo generator — quarterly financial actuals. Seeded, deterministic.
Stand-in for an ERP / financial-reporting export (revenue, COGS, units by
period x product line x region x revenue type).

Coherence anchors (locked across the internal-* datasets):
- FY2025 total revenue ~= $80M with subscription ~= 8%.
- PP3500 flagship ramping since 2024; PP3000/IP5000 declining legacy with
  thinning margins; SP6000/SP6500 steady; cloud-suite small but accelerating.
- No clocks: literal as-of dates only; actuals run 2024-Q1 .. 2026-Q2.

The FINANCIAL MODEL block below is embedded identically in the
internal-sales-accounts generator so account-level revenue reconciles with
these actuals (same anchors, growth rates, and revenue-type splits).
"""
import argparse, csv, json, random

BANNER = "_Demo sample data - not for clinical use._"

# ---------------------------------------------------------------- FINANCIAL MODEL
# (embedded identically in internal-sales-accounts/gen.py — keep in sync)
QUARTERS = ["2024-Q1", "2024-Q2", "2024-Q3", "2024-Q4",
            "2025-Q1", "2025-Q2", "2025-Q3", "2025-Q4",
            "2026-Q1", "2026-Q2"]                     # index 0..9; FY2025 = 4..7
FY2025_TARGETS = {"PP3500": 34_000_000, "PP3000": 14_000_000, "IP5000": 9_000_000,
                  "SP6000": 10_000_000, "SP6500": 7_000_000, "cloud-suite": 6_400_000}
GROWTH = {"PP3500": 1.10, "PP3000": 0.97, "IP5000": 0.96,
          "SP6000": 1.005, "SP6500": 1.000, "cloud-suite": 1.16}
REGION_SHARE = {"NA": 0.55, "EMEA": 0.30, "APAC": 0.15}
TYPE_SHARE = {  # revenue-type mix per line (legacy lines skew to consumables/service)
    "PP3500": {"hardware": 0.58, "consumables": 0.27, "service": 0.15},
    "PP3000": {"hardware": 0.30, "consumables": 0.48, "service": 0.22},
    "IP5000": {"hardware": 0.28, "consumables": 0.50, "service": 0.22},
    "SP6000": {"hardware": 0.45, "consumables": 0.38, "service": 0.17},
    "SP6500": {"hardware": 0.48, "consumables": 0.36, "service": 0.16},
    "cloud-suite": {"subscription": 1.00},
}

def quarterly_line_revenue(line, qi):
    """Deterministic trend value for a line at quarter index qi (0 = 2024-Q1)."""
    g = GROWTH[line]
    anchor = FY2025_TARGETS[line] / sum(g ** k for k in (4, 5, 6, 7))
    return anchor * g ** qi
# ---------------------------------------------------------------- /FINANCIAL MODEL

# COGS as a fraction of revenue. Legacy hardware margin thins over time
# (+1.2 pts per quarter on PP3000/IP5000 hardware, capped).
COGS_RATIO = {"hardware": 0.52, "consumables": 0.42, "service": 0.60, "subscription": 0.22}
LEGACY = {"PP3000", "IP5000"}
LEGACY_HW_BASE, LEGACY_HW_SLOPE, LEGACY_HW_CAP = 0.62, 0.012, 0.78
SP_HW_RATIO = 0.55

# Unit price used to derive units from revenue (per line x type).
ASP_HW = {"PP3500": 8000, "PP3000": 6000, "IP5000": 5500, "SP6000": 4200, "SP6500": 5200}
ASP = {"consumables": 27, "service": 2500, "subscription": 4800}  # subscription = covered device-quarter

def cogs_ratio(line, rtype, qi):
    if rtype == "hardware":
        if line in LEGACY:
            return min(LEGACY_HW_BASE + LEGACY_HW_SLOPE * qi, LEGACY_HW_CAP)
        if line.startswith("SP"):
            return SP_HW_RATIO
    return COGS_RATIO[rtype]

def make_rows(rng):
    rows = []
    for qi, period in enumerate(QUARTERS):
        for line in FY2025_TARGETS:
            base = quarterly_line_revenue(line, qi)
            for region, rs in REGION_SHARE.items():
                for rtype, ts in TYPE_SHARE[line].items():
                    rev = base * rs * ts * (1 + rng.uniform(-0.04, 0.04))
                    asp = ASP_HW[line] if rtype == "hardware" else ASP[rtype]
                    rows.append({
                        "period": period, "product_line": line, "region": region,
                        "revenue_type": rtype,
                        "revenue_usd": int(round(rev)),
                        "cogs_usd": int(round(rev * cogs_ratio(line, rtype, qi))),
                        "units": int(round(rev / asp)),
                    })
    return rows

def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("gen"); g.add_argument("--seed", type=int, default=42); g.add_argument("--out", required=True)
    n = sub.add_parser("normalize"); n.add_argument("raw"); n.add_argument("out")
    a = p.parse_args()
    if a.cmd == "gen":
        rng = random.Random(a.seed)
        rows = make_rows(rng)
        json.dump({"banner": BANNER, "generator": "gen.py", "seed": a.seed,
                   "as_of": "2026-07-25", "rows": rows},
                  open(f"{a.out}/export.json", "w"), indent=1)
    else:
        rows = json.load(open(f"{a.raw}/export.json"))["rows"]
        w = csv.DictWriter(open(f"{a.out}/records.csv", "w", newline=""), fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)

main()
