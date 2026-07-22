#!/usr/bin/env python3
"""Demo generator — field-update campaign telemetry (campaign C-2026-02: PP3500
firmware -> 3.4.0). Seeded, deterministic. Stand-in for the campaign-management export.
Narrative knobs: EMEA behind plan; failure cluster on hw_rev B upgrading from 3.1.2;
remote updates only where Cloud Suite connected."""
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

WAVES = {"NA": ("W1", dt.date(2026, 3, 2)), "EMEA": ("W2", dt.date(2026, 4, 13)),
         "APAC": ("W3", dt.date(2026, 6, 1))}

def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("gen"); g.add_argument("--seed", type=int, default=42); g.add_argument("--out", required=True)
    n = sub.add_parser("normalize"); n.add_argument("raw"); n.add_argument("out")
    a = p.parse_args()
    if a.cmd == "gen":
        rng = random.Random(a.seed)
        _, fleet = make_fleet(rng)
        rng3 = random.Random(a.seed + 2)
        rows = []
        targets = [d for d in fleet if d["model"] == "PP3500" and d["firmware_version"] != "3.4.0"]
        for d in targets:
            wave, wstart = WAVES[d["region"]]
            method = "remote" if d["connected"] == "yes" else "onsite"
            # completion probability: EMEA lags; onsite lags
            p_done = {"NA": 0.85, "EMEA": 0.55, "APAC": 0.70}[d["region"]]
            if method == "onsite":
                p_done -= 0.15
            done = rng3.random() < p_done
            # failure cluster: hw_rev B from 3.1.2 fails 28%; else 4%
            p_fail = 0.28 if (d["hw_rev"] == "B" and d["firmware_version"] == "3.1.2") else 0.04
            failed_once = rng3.random() < p_fail
            if done:
                status = "completed-after-retry" if failed_once else "completed"
                # completion dates never post-date the export as-of date
                as_of = dt.date(2026, 7, 20)
                span = min(70, max(1, (as_of - wstart).days))
                cdate = (wstart + dt.timedelta(days=rng3.randint(0, span))).isoformat()
            else:
                status = "failed-pending-retry" if failed_once else "scheduled"
                cdate = ""
            if done and failed_once and rng3.random() < 0.15:
                status, cdate = "rolled-back", cdate
            dur = (rng3.randint(18, 45) if method == "remote" else rng3.randint(45, 150)) if done else 0
            tickets = (1 if failed_once else 0) + (1 if (done and rng3.random() < 0.08) else 0) \
                      + (2 if status == "rolled-back" else 0)
            rows.append({
                "campaign_id": "C-2026-02", "device_serial": d["device_serial"],
                "site_id": d["site_id"], "region": d["region"], "hw_rev": d["hw_rev"],
                "from_version": d["firmware_version"], "to_version": "3.4.0",
                "wave": wave, "method": method, "status": status,
                "completed_date": cdate, "duration_min": str(dur), "tickets_opened": str(tickets),
            })
        json.dump({"banner": BANNER, "generator": "gen.py", "seed": a.seed, "rows": rows},
                  open(f"{a.out}/export.json", "w"), indent=1)
    else:
        rows = json.load(open(f"{a.raw}/export.json"))["rows"]
        w = csv.DictWriter(open(f"{a.out}/records.csv", "w", newline=""), fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)

main()
