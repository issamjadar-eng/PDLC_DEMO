#!/usr/bin/env python3
"""Demo generator — internal complaint log (18 months). Seeded, deterministic.
Stand-in for the complaint-handling system export."""
import argparse, csv, datetime as dt, json, random

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

CATEGORIES = [("occlusion-alarm", 30), ("battery", 18), ("screen-display", 12),
              ("dose-programming", 8), ("connectivity", 14), ("mechanical", 10), ("other", 8)]

def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("gen"); g.add_argument("--seed", type=int, default=42); g.add_argument("--out", required=True)
    n = sub.add_parser("normalize"); n.add_argument("raw"); n.add_argument("out")
    a = p.parse_args()
    if a.cmd == "gen":
        rng = random.Random(a.seed)
        _, fleet = make_fleet(rng)
        rng2 = random.Random(a.seed + 1)
        start = dt.date(2025, 2, 1)
        rows = []
        for i in range(430):
            d = rng2.choice(fleet)
            day = start + dt.timedelta(days=int(rng2.betavariate(1.4, 1.0) * 535))
            cat = rng2.choices([c for c, _ in CATEGORIES], weights=[w for _, w in CATEGORIES])[0]
            # narrative: battery complaints skew to PP3000 + older fw; connectivity to EMEA
            if cat == "battery" and d["model"] == "PP3500" and rng2.random() < 0.5:
                d = rng2.choice([x for x in fleet if x["model"] == "PP3000"])
            sev = rng2.choices([1, 2, 3], weights=[55, 35, 10])[0]
            rows.append({
                "complaint_id": f"C-{2025 if day.year==2025 else 2026}-{i+1:04d}",
                "date_opened": day.isoformat(), "device_serial": d["device_serial"],
                "site_id": d["site_id"], "region": d["region"], "model": d["model"],
                "firmware_version": d["firmware_version"], "category": cat,
                "severity": str(sev),
                "status": rng2.choices(["closed", "open", "under-investigation"], weights=[70, 18, 12])[0],
                "mdr_filed": "yes" if (sev == 3 and rng2.random() < 0.6) else "no",
            })
        rows.sort(key=lambda r: r["date_opened"])
        json.dump({"banner": BANNER, "generator": "gen.py", "seed": a.seed, "rows": rows},
                  open(f"{a.out}/export.json", "w"), indent=1)
    else:
        rows = json.load(open(f"{a.raw}/export.json"))["rows"]
        w = csv.DictWriter(open(f"{a.out}/records.csv", "w", newline=""), fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)

main()
