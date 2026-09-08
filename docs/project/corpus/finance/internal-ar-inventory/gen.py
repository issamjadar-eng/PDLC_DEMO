#!/usr/bin/env python3
"""Demo generator — monthly working-capital cube, 2025-01 .. 2026-08. Seeded,
deterministic. Stand-in for the ERP AR-aging + inventory-valuation export at the
grain period x region x channel (three fictional GPOs + direct) x product line.

Coherence anchors:
- Monthly revenue per line follows the FINANCIAL MODEL of
  commercial/internal-financials/gen.py (same FY2025 anchors + growth rates; the
  block below is a copy — keep in sync), so AR balances are DSO-consistent with the
  ~$80.5M FY2025 revenue. cloud-suite (subscription billing, no inventory) is out of
  scope for this cube — a stated gap, not an omission.
- Per row: ar_balance_usd, ar_over_90_usd (AR aged > 90 days), dso_days (days sales
  outstanding of that channel x line x region), inventory_usd + inventory_days
  (finished goods held against that channel's demand, days of cost consumption),
  consumable_units_shipped.
- Consumers aggregate DSO and inventory days by summing the implied daily flows:
  DSO = sum(AR) / sum(AR / dso); days = sum(inv) / sum(inv / days).
- Narrative knobs (modeled, not observed):
  * Northgate Purchasing Group: over-90 AR share climbs from ~8% to ~32% and DSO
    from ~48 to ~78 days across 2026 (a collections dispute building); the other
    channels hold DSO in the mid-40s / low-50s.
  * Inventory days rise on legacy hardware: PP3000 ~72 -> ~135 days, IP5000 ~68 ->
    ~120 days over the window; PP3500 steady ~55; SP lines ~62 flat.
- No clocks: literal periods; as_of 2026-08-31.
"""
import argparse, csv, json, random

BANNER = "_Demo sample data - not for clinical use._"

# ---------------------------------------------------------------- FINANCIAL MODEL
# (copied from commercial/internal-financials/gen.py — keep in sync)
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

MONTHS = [f"{y}-{m:02d}" for y in (2025, 2026) for m in range(1, 13)][:20]  # 2025-01..2026-08
LINES = ["PP3500", "PP3000", "IP5000", "SP6000", "SP6500"]
GPOS = ["Meridian Health Alliance", "Northgate Purchasing Group", "Cascadia Supply Co-op", "direct"]
GPO_SHARE = {"NA": [0.30, 0.25, 0.15, 0.30], "EMEA": [0.10, 0.15, 0.05, 0.70],
             "APAC": [0.05, 0.10, 0.05, 0.80]}
DSO_BASE = {"Meridian Health Alliance": 46.0, "Northgate Purchasing Group": 48.0,
            "Cascadia Supply Co-op": 52.0, "direct": 44.0}
OVER90_BASE = {"Meridian Health Alliance": 0.06, "Northgate Purchasing Group": 0.08,
               "Cascadia Supply Co-op": 0.08, "direct": 0.05}
REGION_DSO_ADD = {"NA": 0.0, "EMEA": 6.0, "APAC": 10.0}
COGS_RATIO = {"PP3500": 0.45, "PP3000": 0.52, "IP5000": 0.52, "SP6000": 0.50, "SP6500": 0.50}
INV_DAYS = {"PP3500": (55.0, 56.0), "PP3000": (72.0, 135.0), "IP5000": (68.0, 120.0),
            "SP6000": (62.0, 63.0), "SP6500": (61.0, 62.0)}
CONSUMABLE_ASP = 27
NORTHGATE = "Northgate Purchasing Group"


def lerp(a, b, t):
    return a + (b - a) * t


def month_qi(month):
    y, m = int(month[:4]), int(month[5:])
    return (y - 2024) * 4 + (m - 1) // 3          # 2025-01 -> 4 ... 2026-08 -> 10


def make_rows(rng):
    rows = []
    for mi, month in enumerate(MONTHS):
        t = mi / (len(MONTHS) - 1)
        t26 = max(0.0, (mi - 12) / 7.0)            # 0 through 2025, ramps across 2026
        qi = min(month_qi(month), len(QUARTERS) - 1)
        for line in LINES:
            rev_month = quarterly_line_revenue(line, qi) / 3.0
            inv_days_line = lerp(*INV_DAYS[line], t)
            for region, rs in REGION_SHARE.items():
                for gpo, gs in zip(GPOS, GPO_SHARE[region]):
                    rev = rev_month * rs * gs * (1 + rng.uniform(-0.03, 0.03))
                    dso = DSO_BASE[gpo] + REGION_DSO_ADD[region] + rng.uniform(-2, 2)
                    o90 = OVER90_BASE[gpo] + (0.02 if line in ("PP3000", "IP5000") else 0.0)
                    if gpo == NORTHGATE:
                        dso += lerp(0.0, 30.0, t26)
                        o90 += lerp(0.0, 0.24, t26)
                    ar = rev * dso / 30.0
                    daily_cogs = rev * COGS_RATIO[line] / 30.0
                    days = inv_days_line + rng.uniform(-2, 2)
                    rows.append({
                        "period": month, "region": region, "gpo": gpo, "product_line": line,
                        "ar_balance_usd": int(round(ar)),
                        "ar_over_90_usd": int(round(ar * o90)),
                        "inventory_usd": int(round(daily_cogs * days)),
                        "inventory_days": round(days, 1),
                        "dso_days": round(dso, 1),
                        "consumable_units_shipped": int(round(rev * TYPE_SHARE[line]["consumables"] / CONSUMABLE_ASP)),
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
                   "as_of": "2026-08-31", "rows": rows},
                  open(f"{a.out}/export.json", "w"), indent=1)
    else:
        rows = json.load(open(f"{a.raw}/export.json"))["rows"]
        w = csv.DictWriter(open(f"{a.out}/records.csv", "w", newline=""), fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)


main()
