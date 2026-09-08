#!/usr/bin/env python3
"""Demo generator — approved-supplier register x monthly incoming-inspection results.
Seeded, deterministic, no clocks. Stand-in for the ASL (approved supplier list) joined
to the incoming-inspection log, 2025-01 .. 2026-08, data through 2026-08-31.
One row per supplier x period; register fields (name, family, single-source, approval
status, audit dates) repeat on every period row so each row is self-describing.

Coherence anchors: supplier ids (SUP-NNN) are the same ids cited by
manufacturing/internal-ncr-capa `supplier_id`.

Planted narrative knobs (modeled, not observed — see README):
- SUP-003 (Meridian Drive Systems, pump-motor, SINGLE SOURCE): audit overdue against
  DATA_THROUGH and incoming reject rate rising through 2026.
- SUP-006 (Halden Cell Works, battery): approval_status = probation, high rejects,
  weak on-time.
- Everyone else healthy (A/B scorecards), audits current.
"""
import argparse, csv, json, random

BANNER = "_Demo sample data - not for clinical use._"
DATA_THROUGH = "2026-08-31"

MONTHS = [f"{y}-{m:02d}" for y in (2025, 2026) for m in range(1, 13)
          if not (y == 2026 and m > 8)]

# id, name, component family, single_source, approval_status, last_audit, next_audit_due,
# base monthly lots received, base reject rate, base on-time %
REGISTER = [
    ("SUP-001", "Northwind Circuits", "PCB", "false", "approved", "2026-02-10", "2027-02-10", 110, 0.010, 96.0),
    ("SUP-002", "Coastal PCB Assembly", "PCB", "false", "approved", "2025-09-22", "2026-09-22", 70, 0.014, 94.0),
    ("SUP-003", "Meridian Drive Systems", "pump-motor", "true", "approved", "2024-11-15", "2025-11-15", 95, 0.020, 93.0),
    ("SUP-004", "Voltaic Power Cells", "battery", "false", "approved", "2026-01-20", "2027-01-20", 60, 0.012, 95.0),
    ("SUP-005", "Ardent Moldings", "enclosure", "false", "approved", "2025-11-04", "2026-11-04", 80, 0.011, 95.0),
    ("SUP-006", "Halden Cell Works", "battery", "false", "probation", "2026-04-14", "2026-10-14", 45, 0.058, 82.0),
    ("SUP-007", "Sable Polymer Housings", "enclosure", "false", "approved", "2026-03-03", "2027-03-03", 55, 0.013, 93.0),
    ("SUP-008", "Clearline Medical Tubing", "tubing-set", "false", "approved", "2025-12-09", "2026-12-09", 130, 0.009, 97.0),
    ("SUP-009", "Riverbend Fluidics", "tubing-set", "false", "approved", "2026-05-27", "2027-05-27", 90, 0.012, 95.0),
    ("SUP-010", "Lumen Display Group", "display", "true", "approved", "2026-06-18", "2027-06-18", 70, 0.011, 94.0),
    ("SUP-011", "Kestrel Electromech", "pump-motor", "false", "conditional", "2026-07-08", "2027-01-08", 20, 0.025, 90.0),
    ("SUP-012", "Brightfield Optics", "display", "false", "approved", "2025-10-30", "2026-10-30", 40, 0.015, 93.0),
]
# SUP-011 is the qualification-stage second source for pump motors (conditional, low
# volume) — it does NOT yet relieve SUP-003's single-source exposure on production parts.


def sup003_reject(month):
    if month < "2026-01":
        return 0.020
    if month < "2026-04":
        return 0.035
    if month < "2026-07":
        return 0.055
    return 0.080


def scorecard(reject_rate, on_time):
    if reject_rate < 0.015 and on_time >= 95:
        return "A"
    if reject_rate < 0.03 and on_time >= 90:
        return "B"
    if reject_rate < 0.06 and on_time >= 80:
        return "C"
    return "D"


def make_rows(rng):
    rows = []
    for month in MONTHS:
        for (sid, name, fam, single, status, last_audit, next_due, base_lots, base_rej, base_ot) in REGISTER:
            lots = max(1, base_lots + rng.randint(-8, 8))
            rej_rate = sup003_reject(month) if sid == "SUP-003" else base_rej
            rej_rate = max(0.0, rej_rate + rng.uniform(-0.004, 0.004))
            rejected = min(lots, max(0, int(round(lots * rej_rate + rng.uniform(-0.5, 0.5)))))
            ot = base_ot + rng.uniform(-2.5, 2.5)
            if sid == "SUP-003" and month >= "2026-04":
                ot -= 4.0
            ot = round(min(100.0, max(0.0, ot)), 1)
            rows.append({
                "supplier_id": sid, "supplier_name": name, "component_family": fam,
                "single_source": single, "approval_status": status,
                "last_audit_date": last_audit, "next_audit_due": next_due,
                "period": month, "lots_received": lots, "lots_rejected": rejected,
                "on_time_pct": ot, "scorecard": scorecard(rejected / lots, ot),
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
