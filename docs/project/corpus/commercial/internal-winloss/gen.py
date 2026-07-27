#!/usr/bin/env python3
"""Demo generator — CRM opportunity win/loss log. Seeded, deterministic (NO clocks —
all dates literal). Stand-in for a CRM (opportunity-object) export.
Narrative knobs: overall win rate ~45%; predictive-monitoring-gap is the primary
reason or cited in ~30% of losses; win rate elevated (~65%) for opportunities closed
2025-07-01 onward where the incumbent is Baxter or ICU Medical, clustered in the
months following mid/late-2025 (stand-in for recall/integration disruption windows —
downstream joins against REAL openFDA recall dates)."""
import argparse, csv, hashlib, json, random

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

def site_segment(site_id):
    """Segment keyed on a stable hash of site_id — identical function embedded in the
    other internal generators so segments align across datasets without consuming rng."""
    h = int(hashlib.md5(site_id.encode()).hexdigest(), 16) % 10
    return "academic" if h < 3 else "community" if h < 7 else "idn" if h < 9 else "home-infusion"

VENDORS = ["BD", "Baxter", "ICU Medical", "Fresenius Kabi", "Smiths Medical", "B.Braun"]
# stand-in disruption windows (close-month pools) per disrupted incumbent — the
# downstream computation joins these clusters against real openFDA recall dates
DISRUPTION_MONTHS = {
    "Baxter":      ["2025-09", "2025-10", "2025-11", "2025-12", "2026-01", "2026-02"],
    "ICU Medical": ["2025-11", "2025-12", "2026-01", "2026-02", "2026-03", "2026-04"],
}
ALL_MONTHS = ([f"2025-{m:02d}" for m in range(1, 13)] + [f"2026-{m:02d}" for m in range(1, 8)])
NAME_A = ["Riverbend", "Cedar Grove", "Lakeshore", "Summit Ridge", "Blue Heron", "Oakdale",
          "Harborview", "Silver Birch", "Meadowbrook", "Stonebridge", "Northgate", "Falcon Crest",
          "Willow Creek", "Eastfield", "Pinehurst", "Copper Hill", "Marble Bay", "Ashford",
          "Granite Peak", "Foxglove", "Elm Hollow", "Kestrel Park", "Larkspur", "Amber Valley"]
NAME_B = {"academic": "University Medical Center", "community": "Community Hospital",
          "idn": "Health System", "home-infusion": "Home Infusion Services"}

def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("gen"); g.add_argument("--seed", type=int, default=42); g.add_argument("--out", required=True)
    n = sub.add_parser("normalize"); n.add_argument("raw"); n.add_argument("out")
    a = p.parse_args()
    if a.cmd == "gen":
        rng = random.Random(a.seed)
        sites, _ = make_fleet(rng)          # burn identical rng stream so fleet aligns
        rng2 = random.Random(a.seed + 10)   # dataset-local randomness
        names = {}
        def account_name(acct_id, segment):
            if acct_id not in names:
                names[acct_id] = f"{NAME_A[len(names) % len(NAME_A)]} {NAME_B[segment]}"
            return names[acct_id]
        rows = []
        for i in range(120):
            installed = rng2.random() < 0.55
            if installed:
                site = rng2.choice(sites)
                acct_id, region = site["site_id"], site["region"]
                segment = site_segment(acct_id)
            else:
                acct_id = f"PRO-{rng2.randint(1, 30):02d}"
                region = rng2.choices(["NA", "EMEA", "APAC"], weights=[50, 30, 20])[0]
                segment = rng2.choices(["academic", "community", "idn", "home-infusion"],
                                       weights=[25, 40, 25, 10])[0]
            incumbent = ("PainEase" if installed and rng2.random() < 0.45 else
                         rng2.choices(VENDORS + ["none"],
                                      weights=[15, 22, 16, 10, 8, 9, 20])[0])
            # disruption-window opportunities: incumbent Baxter / ICU Medical, closed
            # in the months following the mid/late-2025 disruption stand-ins
            if incumbent in DISRUPTION_MONTHS and rng2.random() < 0.75:
                month = rng2.choice(DISRUPTION_MONTHS[incumbent])
            else:
                month = rng2.choice(ALL_MONTHS)
            # elevated win rate applies to the WHOLE measurable group: Baxter/ICU
            # incumbent, closed 2025-07-01 onward (however the month was drawn)
            disrupted = incumbent in DISRUPTION_MONTHS and month >= "2025-07"
            if disrupted:
                outcome = rng2.choices(["won", "lost", "no-decision"], weights=[68, 22, 10])[0]
            else:
                outcome = rng2.choices(["won", "lost", "no-decision"], weights=[36, 45, 19])[0]
            day = rng2.randint(1, 25 if month == "2026-07" else 28)
            close_date = f"{month}-{day:02d}"
            if incumbent in VENDORS:
                competitor = incumbent if rng2.random() < 0.70 else rng2.choice(VENDORS)
            else:
                competitor = rng2.choice(VENDORS) if rng2.random() < 0.80 else "none"
            if outcome == "won":
                pool, wts = (["contract-timing", "service", "features", "clinical-evidence", "price", "other"],
                             [35, 25, 15, 10, 10, 5]) if disrupted else \
                            (["features", "clinical-evidence", "service", "price", "contract-timing", "other"],
                             [30, 20, 15, 15, 15, 5])
            elif outcome == "lost":
                pool, wts = (["price", "predictive-monitoring-gap", "incumbent-relationship",
                              "features", "clinical-evidence", "service", "contract-timing", "other"],
                             [25, 22, 20, 12, 8, 5, 5, 3])
            else:
                pool, wts = (["contract-timing", "price", "incumbent-relationship", "other"],
                             [40, 20, 20, 20])
            reason = rng2.choices(pool, weights=wts)[0]
            cites = "yes" if reason == "predictive-monitoring-gap" else \
                    ("yes" if rng2.random() < {"lost": 0.10, "won": 0.12, "no-decision": 0.10}[outcome] else "no")
            lo, hi = {"academic": (600, 1800), "idn": (500, 1500),
                      "community": (250, 800), "home-infusion": (150, 500)}[segment]
            value = rng2.randint(lo, hi) * 1000
            rows.append({
                "opp_id": f"OPP-{i+1:04d}", "close_date": close_date, "account_id": acct_id,
                "account_name": account_name(acct_id, segment), "region": region,
                "segment": segment, "outcome": outcome, "competitor": competitor,
                "incumbent_vendor": incumbent, "primary_reason": reason,
                "cites_predictive_monitoring": cites, "value_usd": str(value),
            })
        rows.sort(key=lambda r: (r["close_date"], r["opp_id"]))
        json.dump({"banner": BANNER, "generator": "gen.py", "seed": a.seed, "rows": rows},
                  open(f"{a.out}/export.json", "w"), indent=1)
    else:
        rows = json.load(open(f"{a.raw}/export.json"))["rows"]
        w = csv.DictWriter(open(f"{a.out}/records.csv", "w", newline=""), fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)

main()
