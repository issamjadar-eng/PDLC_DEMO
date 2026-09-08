#!/usr/bin/env python3
"""Demo generator — process-validation + calibration status register. Seeded,
deterministic, no clocks. Stand-in for the validation master list joined to the
calibration / preventive-maintenance register, status as of 2026-08-31 (DATA_THROUGH).

Every status is DERIVED from the record's own dates against DATA_THROUGH:
  validated    — completed, next due date after the horizon (IQ/OQ/PQ: no re-due; a
                 completed validation stays validated)
  due          — completed but the next due date falls within 30 days of the horizon
  overdue      — the due date has passed without a completion after it
  in-progress  — started, not complete, due date ahead
  not-started  — planned, no activity, due date ahead

Coherence anchors: product_line = the five-device portfolio ("" = shared equipment);
site = Eastbrook | Westfield (as in internal-production-lots).

Planted narrative knobs (modeled, not observed — see README):
- PP3500 rev C test fixture: IQ + OQ validated, PQ in-progress (due 2026-09-30) —
  the validation-side blocker for rev C lot release.
- A cluster of overdue calibrations at Westfield (Eastbrook has one).
"""
import argparse, csv, json, random

BANNER = "_Demo sample data - not for clinical use._"
DATA_THROUGH = "2026-08-31"
DUE_SOON_DAYS = 30
DAYS_IN = {1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}

SITES = ["Eastbrook", "Westfield"]
LINES_AT = {"Eastbrook": ["PP3500", "PP3000", "IP5000"], "Westfield": ["PP3500", "SP6000", "SP6500"]}

# --- validation (IQ/OQ/PQ) subjects: (asset_or_process, product_line or "", site)
VALIDATION_SUBJECTS = [
    ("SMT reflow oven line A", "", "Eastbrook"),
    ("SMT reflow oven line B", "", "Westfield"),
    ("automated optical inspection", "", "Eastbrook"),
    ("automated optical inspection", "", "Westfield"),
    ("pump-motor press-fit process", "PP3500", "Eastbrook"),
    ("pump-motor press-fit process", "PP3500", "Westfield"),
    ("occlusion pressure test process", "PP3500", "Eastbrook"),
    ("occlusion pressure test process", "PP3500", "Westfield"),
    ("flow-accuracy test process", "PP3000", "Eastbrook"),
    ("flow-accuracy test process", "IP5000", "Eastbrook"),
    ("flow-accuracy test process", "SP6000", "Westfield"),
    ("flow-accuracy test process", "SP6500", "Westfield"),
    ("ultrasonic enclosure weld", "PP3500", "Eastbrook"),
    ("ultrasonic enclosure weld", "SP6000", "Westfield"),
    ("final functional test fixture rev B", "PP3500", "Eastbrook"),
    ("final functional test fixture rev B", "PP3500", "Westfield"),
    ("pouch sealer", "", "Eastbrook"),
    ("pouch sealer", "", "Westfield"),
    ("label printer / UDI verifier", "", "Eastbrook"),
    ("label printer / UDI verifier", "", "Westfield"),
]
# knob: the rev C fixture — IQ/OQ complete, PQ in-progress at both sites
REV_C_FIXTURE = ("final functional test fixture rev C", "PP3500")

CAL_ASSETS = ["torque driver", "digital pressure gauge", "flow meter reference",
              "precision balance", "leak tester reference", "thermocouple set",
              "caliper", "electrical safety analyzer", "syringe pump reference",
              "hipot tester", "oscilloscope", "environmental chamber probe",
              "force gauge", "vision system target", "DMM reference"]
PM_ASSETS = ["SMT pick-and-place", "reflow oven", "compressed-air dryer", "HVAC cleanroom unit",
             "conveyor", "ultrasonic welder", "pouch sealer", "label printer",
             "burn-in rack", "ESD flooring test"]
OWNER = {"IQ": "manufacturing-engineering", "OQ": "manufacturing-engineering",
         "PQ": "quality", "calibration": "metrology", "preventive-maintenance": "facilities"}


def add_days(iso, n):
    y, m, d = (int(x) for x in iso.split("-"))
    d += n
    while d > DAYS_IN[m]:
        d -= DAYS_IN[m]
        m += 1
        if m > 12:
            m, y = 1, y + 1
    return f"{y}-{m:02d}-{d:02d}"


def status_from(typ, completed, due, started):
    if typ in ("IQ", "OQ", "PQ"):
        # one-shot validations: due = planned completion date
        if completed:
            return "validated"
        if due < DATA_THROUGH:
            return "overdue"
        return "in-progress" if started else "not-started"
    # recurring (calibration / PM): due = NEXT due date after the last completion
    if due < DATA_THROUGH:
        return "overdue"
    if add_days(DATA_THROUGH, DUE_SOON_DAYS) >= due:
        return "due"
    return "validated"


def make_rows(rng):
    rows, seq = [], 0

    def rec(typ, asset, line, site, completed, due, started):
        nonlocal seq
        seq += 1
        rows.append({
            "record_id": f"VAL-{seq:04d}", "type": typ, "asset_or_process": asset,
            "product_line": line, "site": site,
            "status": status_from(typ, completed, due, started),
            "completed_date": completed, "due_date": due, "owner_function": OWNER[typ],
        })

    # IQ/OQ/PQ for the established subjects: all validated, completed 2024-2025;
    # IQ/OQ/PQ "due" = the planned completion date (revalidation not modeled here)
    for asset, line, site in VALIDATION_SUBJECTS:
        base = f"2025-{rng.randint(1, 9):02d}-{rng.randint(1, 28):02d}"
        for i, typ in enumerate(("IQ", "OQ", "PQ")):
            done = add_days(base, 20 * i + rng.randint(0, 10))
            rec(typ, asset, line, site, done, add_days(done, rng.randint(5, 20)), True)
    # knob: rev C fixture — IQ, OQ validated (2026-Q1/Q2); PQ in-progress due 2026-09-30
    for site in SITES:
        rec("IQ", REV_C_FIXTURE[0], REV_C_FIXTURE[1], site, "2026-03-2%d" % rng.randint(0, 8), "2026-03-31", True)
        rec("OQ", REV_C_FIXTURE[0], REV_C_FIXTURE[1], site, "2026-05-1%d" % rng.randint(0, 9), "2026-05-31", True)
        rec("PQ", REV_C_FIXTURE[0], REV_C_FIXTURE[1], site, "", "2026-09-30", True)
    # rev C occlusion-test process OQ at Westfield not started (second, smaller blocker)
    rec("OQ", "occlusion pressure test process rev C", "PP3500", "Westfield", "", "2026-10-15", False)

    # calibration: ~34 per site, 12-month interval; Westfield knob = cluster overdue
    for site in SITES:
        for k in range(34):
            asset = f"{CAL_ASSETS[k % len(CAL_ASSETS)]} #{k + 1:02d}"
            line = rng.choice(LINES_AT[site] + [""])
            if site == "Westfield" and k < 9:
                # overdue cluster: last calibrated mid-2025, due already passed
                last = f"2025-{rng.randint(5, 8):02d}-{rng.randint(1, 28):02d}"
                rec("calibration", asset, line, site, last, add_days(last, 365), True)
            elif site == "Eastbrook" and k == 3:
                last = "2025-07-12"
                rec("calibration", asset, line, site, last, add_days(last, 365), True)
            else:
                last = f"{rng.choice(['2025-10', '2025-11', '2025-12', '2026-01', '2026-02', '2026-03', '2026-04', '2026-05', '2026-06', '2026-07', '2026-08'])}-{rng.randint(1, 28):02d}"
                rec("calibration", asset, line, site, last, add_days(last, 365), True)

    # preventive maintenance: 10 per site, 6-month interval; a few due soon
    for site in SITES:
        for k, asset in enumerate(PM_ASSETS):
            last = f"{rng.choice(['2026-03', '2026-04', '2026-05', '2026-06', '2026-07'])}-{rng.randint(1, 28):02d}"
            rec("preventive-maintenance", asset, "", site, last, add_days(last, 182), True)
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
