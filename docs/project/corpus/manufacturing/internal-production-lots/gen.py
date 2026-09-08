#!/usr/bin/env python3
"""Demo generator — production lot records. Seeded, deterministic, no clocks.
Stand-in for the MES / lot-traveler export: one row per station lot (a batch of
units booked through one line station), 2025-01 .. 2026-08, data through 2026-08-31.

Coherence anchors (locked across the manufacturing/internal-* datasets):
- product_line vocabulary = the five-device portfolio (IP5000, PP3000, PP3500, SP6000,
  SP6500); hw_rev letters reuse commercial/internal-fleet (PP3500 A/B in the field,
  C = the 2026 revision; "-" where a line carries no tracked hw rev).
- Two fictional plants: Eastbrook (PP3500, PP3000, IP5000) and Westfield (PP3500,
  SP6000, SP6500).

Planted narrative knobs (modeled, not observed — see README):
- PP3500 hw rev C first-pass yield dips at the test station in 2026-Q2 (Apr-Jun), with
  partial recovery from July.
- Westfield's release lead time trends up through the window; Eastbrook is flat.
- A handful of lots started 2026-06..2026-07 have dhr_complete=false and are therefore
  unreleased (blocked) well past their normal lead time, distinct from late-August lots
  still in process.
"""
import argparse, csv, json, random

BANNER = "_Demo sample data - not for clinical use._"
DATA_THROUGH = "2026-08-31"

MONTHS = [f"{y}-{m:02d}" for y in (2025, 2026) for m in range(1, 13)
          if not (y == 2026 and m > 8)]                          # 2025-01 .. 2026-08
DAYS_IN = {1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}
LINES = ["PP3500", "PP3000", "IP5000", "SP6000", "SP6500"]
SITES_FOR = {"PP3500": ["Eastbrook", "Westfield"], "PP3000": ["Eastbrook"],
             "IP5000": ["Eastbrook"], "SP6000": ["Westfield"], "SP6500": ["Westfield"]}
STATIONS = ["SMT", "final-assembly", "test", "pack"]
BASE_FPY = {"SMT": 0.972, "final-assembly": 0.965, "test": 0.962, "pack": 0.992}
LINE_FPY_ADJ = {"PP3500": 0.0, "PP3000": -0.004, "IP5000": -0.006, "SP6000": 0.002, "SP6500": 0.001}
REWORK_SHARE = {"SMT": 0.55, "final-assembly": 0.70, "test": 0.78, "pack": 0.60}
LOT_SIZE = {"PP3500": (90, 140), "PP3000": (60, 100), "IP5000": (50, 90),
            "SP6000": (70, 110), "SP6500": (60, 100)}
# knob: PP3500 rev C test-station FPY by month (None = baseline)
REV_C_TEST_FPY = {"2026-04": 0.905, "2026-05": 0.882, "2026-06": 0.896,
                  "2026-07": 0.928, "2026-08": 0.936}
# knob: share of PP3500 lots built on rev C by month (rev B otherwise)
REV_C_SHARE = {"2026-03": 0.15, "2026-04": 0.45, "2026-05": 0.65, "2026-06": 0.80,
               "2026-07": 0.85, "2026-08": 0.90}
DHR_INCOMPLETE_P = 0.12        # applies to lots started 2026-06..2026-07 (release-overdue by the horizon)


def add_days(iso, n):
    y, m, d = (int(x) for x in iso.split("-"))
    d += n
    while d > DAYS_IN[m]:
        d -= DAYS_IN[m]
        m += 1
        if m > 12:
            m, y = 1, y + 1
    return f"{y}-{m:02d}-{d:02d}"


def hw_rev(rng, line, month):
    if line == "PP3500":
        if month < "2025-07":
            return "A" if rng.random() < 0.35 else "B"
        return "C" if rng.random() < REV_C_SHARE.get(month, 0.0) else "B"
    if line in ("PP3000", "IP5000"):
        return "-"
    return "A"


def n_lots(line, site, month):
    if line == "PP3500":
        return 3 if (site == "Eastbrook" and month >= "2026-01") else 2
    return 1


def lead_days(rng, site, mi):
    # mi = month index 0..19; Westfield drifts up ~0.45 d/month, Eastbrook flat
    base = 8.0 if site == "Eastbrook" else 7.0 + 0.45 * mi
    return max(3, int(round(base + rng.uniform(-1.5, 1.5))))


def make_rows(rng):
    rows, seq = [], {}
    for mi, month in enumerate(MONTHS):
        y, m = (int(x) for x in month.split("-"))
        for line in LINES:
            for site in SITES_FOR[line]:
                for station in STATIONS:
                    for _ in range(n_lots(line, site, month)):
                        seq[y] = seq.get(y, 0) + 1
                        lot_id = f"LOT-{y}-{seq[y]:04d}"
                        rev = hw_rev(rng, line, month)
                        start = f"{month}-{rng.randint(1, DAYS_IN[m]):02d}"
                        lo, hi = LOT_SIZE[line]
                        started = rng.randint(lo, hi)
                        fpy = BASE_FPY[station] + LINE_FPY_ADJ[line]
                        if line == "PP3500" and rev == "C" and station == "test" and month in REV_C_TEST_FPY:
                            fpy = REV_C_TEST_FPY[month]
                        fpy += rng.uniform(-0.012, 0.012)
                        passed = min(started, max(0, int(round(started * fpy))))
                        failed = started - passed
                        reworked = int(round(failed * REWORK_SHARE[station]))
                        scrapped = failed - reworked
                        dhr_ok = not ("2026-06" <= month <= "2026-07" and rng.random() < DHR_INCOMPLETE_P)
                        lead = lead_days(rng, site, mi)
                        release = add_days(start, lead)
                        if not dhr_ok or release > DATA_THROUGH:
                            release, lead_out = "", ""
                        else:
                            lead_out = lead
                        rows.append({
                            "lot_id": lot_id, "product_line": line, "hw_rev": rev,
                            "line_station": station, "site": site, "start_date": start,
                            "release_date": release, "units_started": started,
                            "units_passed_first_time": passed, "units_scrapped": scrapped,
                            "units_reworked": reworked,
                            "dhr_complete": "true" if dhr_ok else "false",
                            "release_lead_days": lead_out,
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
                   "as_of": DATA_THROUGH, "rows": rows},
                  open(f"{a.out}/export.json", "w"), indent=1)
    else:
        rows = json.load(open(f"{a.raw}/export.json"))["rows"]
        w = csv.DictWriter(open(f"{a.out}/records.csv", "w", newline=""), fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)


main()
