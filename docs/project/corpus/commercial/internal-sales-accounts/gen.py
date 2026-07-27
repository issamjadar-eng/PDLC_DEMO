#!/usr/bin/env python3
"""Demo generator — account-level sales (FY2024, FY2025, FY2026H1). Seeded,
deterministic. Stand-in for a CRM / sales-ops revenue-by-account export.

Coherence anchors (locked):
- Accounts map onto the 48-site fleet model (identical `make_fleet` embedded
  from internal-fleet/gen.py, seed 42) — single sites or small systems grouping
  2-3 sites — plus a handful of prospect accounts with zero installed units.
- Account revenue carries the DIRECT (hardware + subscription) book only;
  consumables/service flow through distributors and are not account-attributed.
  Per-FY account revenue therefore reconciles with internal-financials
  hardware+subscription revenue (identical FINANCIAL MODEL block embedded).
- Concentration knobs (BQ-02): top GPO ("Meridian Health Alliance") ~35-40% of
  FY2025 revenue; top-3 accounts noticeably large. All GPO / health-system
  names are FICTIONAL.
- No clocks: literal as-of dates only; FY2026H1 runs through 2026-06-30.
"""
import argparse, csv, json, random

BANNER = "_Demo sample data - not for clinical use._"
REGIONS = {"NA": 24, "EMEA": 16, "APAC": 8}   # sites per region

def make_fleet(rng):
    """Deterministic demo fleet. Identical function is embedded in every internal
    generator so device serials/sites align across datasets (seed 42)."""
    sites, fleet, serial = [], [], 1
    for region, n in REGIONS.items():
        for i in range(n):
            sites.append({"site_id": f"S-{region}-{i+1:02d}", "region": region,
                          "beds": rng.choice([80, 120, 200, 350, 500])})
    for s in sites:
        n_dev = max(4, s["beds"] // 12)
        attach_p = {"NA": 0.60, "EMEA": 0.40, "APAC": 0.30}[s["region"]]
        for _ in range(n_dev):
            model = "PP3500" if rng.random() < 0.78 else "PP3000"
            hw = rng.choice(["A", "A", "B"]) if model == "PP3500" else "-"
            if model == "PP3500":
                fw = rng.choices(["3.4.0", "3.2.0", "3.1.2"], weights=[45, 35, 20])[0]
            else:
                fw = rng.choice(["2.9.1", "2.9.3"])
            fleet.append({
                "device_serial": f"PE-{serial:05d}", "model": model,
                "site_id": s["site_id"], "region": s["region"], "hw_rev": hw,
                "firmware_version": fw,
                "connected": "yes" if (model == "PP3500" and rng.random() < attach_p) else "no",
            })
            serial += 1
    return sites, fleet

# ---------------------------------------------------------------- FINANCIAL MODEL
# (embedded identically in internal-financials/gen.py — keep in sync)
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

FY_QI = {"FY2024": (0, 1, 2, 3), "FY2025": (4, 5, 6, 7), "FY2026H1": (8, 9)}
HS_SHARE = {ln: TYPE_SHARE[ln].get("hardware", TYPE_SHARE[ln].get("subscription"))
            for ln in FY2025_TARGETS}   # direct (hardware|subscription) share of line revenue

def fy_direct_target(line, fy):
    return sum(quarterly_line_revenue(line, qi) for qi in FY_QI[fy]) * HS_SHARE[line]

# Installed-base ramp per FY (fraction of current-state units).
RAMP = {
    "PP3500": {"FY2024": 0.55, "FY2025": 0.85, "FY2026H1": 1.00},
    "PP3000": {"FY2024": 1.25, "FY2025": 1.05, "FY2026H1": 1.00},
    "IP5000": {"FY2024": 1.30, "FY2025": 1.10, "FY2026H1": 1.00},
    "SP6000": {"FY2024": 0.95, "FY2025": 1.00, "FY2026H1": 1.00},
    "SP6500": {"FY2024": 0.95, "FY2025": 1.00, "FY2026H1": 1.00},
    "cloud-suite": {"FY2024": 0.35, "FY2025": 0.80, "FY2026H1": 1.00},
}

GPO_TOP = "Meridian Health Alliance"                       # fictional
GPO_OTHER = ["Cascadia Health Partners", "AtlasPoint Purchasing", "NovaBridge Alliance"]  # fictional
NAME_STEMS = [
    "Blue Harbor", "Sierra Vista", "Granite Peak", "Lakeshore", "Riverbend",
    "Aurora Plains", "Cedar Grove", "Maplewood", "Ironbridge", "Bright Meadow",
    "Silver Lake", "Northgate", "Eastwood", "Kestrel Bay", "Stonebridge",
    "Clearwater", "Highland Fen", "Copper Hills", "Willow Creek", "Foxglove",
    "Harborlight", "Summit Ridge", "Pinecrest", "Marigold", "Oakhaven",
    "Falcon Ridge", "Amberfield", "Larkspur", "Windmere", "Thornbury",
    "Redwing", "Saltgrass", "Moorland", "Glenrose", "Bayside", "Corminster",
    "Aldervale", "Uplands", "Quarry Bend", "Seagate", "Torval", "Midlyn",
    "Ashport", "Greenholm", "Vantora", "Elmstead", "Brackenfield", "Lowmoor",
    "Duskvale", "Ferncliff", "Halewick", "Ostbridge", "Peverell", "Rundale",
    "Skylark", "Tarnwood",
]

def build_accounts(sites, fleet, rng2):
    by_region = {}
    for s in sites:
        by_region.setdefault(s["region"], []).append(s)
    dev = {}
    for d in fleet:
        e = dev.setdefault(d["site_id"], {"PP3500": 0, "PP3000": 0, "connected": 0})
        e[d["model"]] += 1
        if d["connected"] == "yes":
            e["connected"] += 1
    accounts, stem_i = [], 0
    for region in ("NA", "EMEA", "APAC"):
        pool = by_region[region]
        i = 0
        while i < len(pool):
            take = rng2.choice([2, 3]) if rng2.random() < 0.35 else 1
            group = pool[i:i + take]
            i += take
            beds = sum(s["beds"] for s in group)
            if len(group) > 1:
                segment = "idn"
            elif beds >= 350:
                segment = "academic"
            elif beds >= 200:
                segment = "community"
            else:
                segment = "home-infusion" if rng2.random() < 0.30 else "community"
            suffix = {"idn": rng2.choice(["Health System", "Health Network", "Health Alliance"]),
                      "academic": "University Medical Center",
                      "community": rng2.choice(["Community Hospital", "Regional Medical Center"]),
                      "home-infusion": "Home Infusion Services"}[segment]
            name = f"{NAME_STEMS[stem_i]} {suffix}"; stem_i += 1
            units = {
                "PP3500": sum(dev.get(s["site_id"], {}).get("PP3500", 0) for s in group),
                "PP3000": sum(dev.get(s["site_id"], {}).get("PP3000", 0) for s in group),
                "cloud-suite": sum(dev.get(s["site_id"], {}).get("connected", 0) for s in group),
                "IP5000": beds // 40 if rng2.random() < 0.50 else 0,
                "SP6000": beds // 30,
                "SP6500": beds // 45,
            }
            accounts.append({"name": name, "region": region, "segment": segment,
                             "beds": beds, "units": units, "prospect": False})
    # GPO assignment: biggest NA accounts roll to the top GPO until it holds
    # ~34% of total account weight (greedy overshoots -> ~35-40% of FY2025 revenue).
    total_w = sum(a["beds"] for a in accounts)
    cum = 0.0
    for a in sorted([a for a in accounts if a["region"] == "NA"],
                    key=lambda a: -a["beds"]):
        if cum / total_w < 0.34:
            a["gpo"] = GPO_TOP
            cum += a["beds"]
    for a in accounts:
        if "gpo" not in a:
            a["gpo"] = rng2.choice(GPO_OTHER + ["independent"]) if a["region"] == "NA" else "independent"
    # Prospect accounts — in the funnel, zero installed units.
    for region, segment, gpo in [("NA", "idn", "Cascadia Health Partners"),
                                 ("NA", "academic", "independent"),
                                 ("NA", "community", "independent"),
                                 ("EMEA", "academic", "independent"),
                                 ("EMEA", "community", "independent"),
                                 ("APAC", "academic", "independent")]:
        suffix = {"idn": "Health System", "academic": "University Medical Center",
                  "community": "Community Hospital"}[segment]
        name = f"{NAME_STEMS[stem_i]} {suffix}"; stem_i += 1
        accounts.append({"name": name, "region": region, "segment": segment, "beds": 0,
                         "units": {ln: 0 for ln in FY2025_TARGETS}, "gpo": gpo,
                         "prospect": True})
    for i, a in enumerate(accounts):
        a["id"] = f"ACC-P{i+1:02d}" if a["prospect"] else f"ACC-{i+1:03d}"
    return accounts

def make_rows(accounts, rng2):
    rows = []
    for line in FY2025_TARGETS:
        for fy in FY_QI:
            alloc = []
            for a in accounts:
                n = int(round(a["units"][line] * RAMP[line][fy]))
                if a["prospect"] or n == 0:
                    continue
                alloc.append((a, n, n * rng2.uniform(0.7, 1.3)))
            total_w = sum(w for _, _, w in alloc)
            target = fy_direct_target(line, fy)
            for a, n, w in alloc:
                rows.append({"account_id": a["id"], "account_name": a["name"],
                             "gpo": a["gpo"], "region": a["region"], "segment": a["segment"],
                             "product_line": line, "fy": fy,
                             "revenue_usd": int(round(target * w / total_w)),
                             "units_installed": n})
    for a in accounts:      # prospects: evaluation-stage, zero installed units
        if a["prospect"]:
            rows.append({"account_id": a["id"], "account_name": a["name"],
                         "gpo": a["gpo"], "region": a["region"], "segment": a["segment"],
                         "product_line": "PP3500", "fy": "FY2026H1",
                         "revenue_usd": rng2.choice([0, 0, 12000, 25000, 40000]),
                         "units_installed": 0})
    rows.sort(key=lambda r: (r["account_id"], r["product_line"], r["fy"]))
    return rows

def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("gen"); g.add_argument("--seed", type=int, default=42); g.add_argument("--out", required=True)
    n = sub.add_parser("normalize"); n.add_argument("raw"); n.add_argument("out")
    a = p.parse_args()
    if a.cmd == "gen":
        rng = random.Random(a.seed)          # consumed exactly as in internal-fleet
        sites, fleet = make_fleet(rng)
        rng2 = random.Random(a.seed + 1)     # account-level stream, independent of fleet
        accounts = build_accounts(sites, fleet, rng2)
        rows = make_rows(accounts, rng2)
        json.dump({"banner": BANNER, "generator": "gen.py", "seed": a.seed,
                   "as_of": "2026-07-25", "rows": rows},
                  open(f"{a.out}/export.json", "w"), indent=1)
    else:
        rows = json.load(open(f"{a.raw}/export.json"))["rows"]
        w = csv.DictWriter(open(f"{a.out}/records.csv", "w", newline=""), fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)

main()
