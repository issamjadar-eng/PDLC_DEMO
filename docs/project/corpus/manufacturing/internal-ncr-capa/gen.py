#!/usr/bin/env python3
"""Demo generator — nonconformance (NCR) + CAPA register. Seeded, deterministic, no clocks.
Stand-in for the eQMS NCR/CAPA module export, 2025-01 .. 2026-08, status as of
2026-08-31 (DATA_THROUGH). Every status is DERIVED from the record's own dates against
DATA_THROUGH, so a consumer can rebuild the open/overdue population at any month-end.

Coherence anchors: product_line = the five-device portfolio + "shared" (site / QMS-level
records); supplier_id values reuse manufacturing/internal-suppliers ids (SUP-NNN).

Planted narrative knobs (modeled, not observed — see README):
- CAPA aging past due rises through 2026: closure probability falls by open cohort, so
  the past-due open CAPA count climbs month over month; includes critical CAPAs past due.
- Supplier-sourced NCRs concentrate on SUP-003 (single-source pump-motor supplier), more
  so in 2026.
- Effectiveness verification lags: the share of closed CAPAs with effectiveness verified
  falls by closure cohort.
"""
import argparse, csv, json, random

BANNER = "_Demo sample data - not for clinical use._"
DATA_THROUGH = "2026-08-31"

MONTHS = [f"{y}-{m:02d}" for y in (2025, 2026) for m in range(1, 13)
          if not (y == 2026 and m > 8)]
DAYS_IN = {1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}
LINES = ["PP3500", "PP3000", "IP5000", "SP6000", "SP6500", "shared"]
LINE_W = [40, 15, 10, 15, 12, 8]
SOURCES = ["production", "supplier", "complaint", "audit", "field"]
SOURCE_W = [48, 24, 12, 8, 8]
SEVERITY = ["minor", "major", "critical"]
SEV_W = [62, 31, 7]
ROOT_CAUSES = ["process", "material", "supplier-process", "design", "documentation",
               "equipment", "training", "under-investigation"]
RC_BY_SOURCE = {
    "production": ["process", "equipment", "training", "documentation", "material"],
    "supplier": ["supplier-process", "material", "documentation"],
    "complaint": ["design", "process", "material", "under-investigation"],
    "audit": ["documentation", "training", "process"],
    "field": ["design", "material", "under-investigation"],
}
SUPPLIERS = ["SUP-001", "SUP-002", "SUP-003", "SUP-004", "SUP-005", "SUP-006",
             "SUP-007", "SUP-008", "SUP-009", "SUP-010", "SUP-011", "SUP-012"]
NCR_DUE_DAYS, CAPA_DUE_DAYS = 30, 90


def add_days(iso, n):
    y, m, d = (int(x) for x in iso.split("-"))
    d += n
    while d > DAYS_IN[m]:
        d -= DAYS_IN[m]
        m += 1
        if m > 12:
            m, y = 1, y + 1
    return f"{y}-{m:02d}-{d:02d}"


def ncr_count(mi):
    # ~10/month in 2025 rising to ~13/month in 2026
    return 10 + (mi - 12) // 3 if mi >= 12 else 10


def capa_close_p(month):
    if month < "2025-10":
        return 0.95
    if month < "2026-03":
        return 0.60
    return 0.25


def sup003_share(month):
    return 0.62 if month >= "2026-01" else 0.48


def eff_verified_p(closed_month):
    if closed_month < "2025-07":
        return 0.90
    if closed_month < "2026-01":
        return 0.55
    return 0.20


def status_for(closed, due, opened):
    if closed:
        return "closed"
    if due < DATA_THROUGH:
        return "overdue-open"
    # opened in the last two weeks before the data horizon = not yet in investigation
    return "open" if opened >= "2026-08-18" else "in-progress"


def make_rows(rng):
    rows = []
    ncr_seq, capa_seq = {}, {}
    for mi, month in enumerate(MONTHS):
        y, m = (int(x) for x in month.split("-"))
        # --- CAPAs opened this month (3..5)
        capas_this_month = []
        for _ in range(rng.randint(3, 5)):
            capa_seq[y] = capa_seq.get(y, 0) + 1
            rid = f"CAPA-{y}-{capa_seq[y]:04d}"
            opened = f"{month}-{rng.randint(1, DAYS_IN[m]):02d}"
            due = add_days(opened, CAPA_DUE_DAYS)
            source = rng.choices(SOURCES, SOURCE_W)[0]
            sev = rng.choices(SEVERITY, [40, 45, 15])[0]
            closes = rng.random() < capa_close_p(month)
            closed = ""
            if closes:
                closed = add_days(opened, rng.randint(35, 130))
                if closed > DATA_THROUGH:
                    closed = ""
            eff = ""
            if closed:
                eff = "true" if rng.random() < eff_verified_p(closed[:7]) else "false"
            else:
                eff = "false"
            sup = rng.choice(SUPPLIERS) if source == "supplier" else ""
            if source == "supplier" and rng.random() < sup003_share(month):
                sup = "SUP-003"
            rows.append({
                "record_id": rid, "type": "CAPA", "opened_date": opened,
                "closed_date": closed, "due_date": due, "status": status_for(closed, due, opened),
                "source": source, "product_line": rng.choices(LINES, LINE_W)[0],
                "severity": sev, "root_cause_category": rng.choice(RC_BY_SOURCE[source]),
                "effectiveness_verified": eff, "linked_record": "", "supplier_id": sup,
            })
            capas_this_month.append(rid)
        # --- NCRs opened this month
        for _ in range(ncr_count(mi)):
            ncr_seq[y] = ncr_seq.get(y, 0) + 1
            rid = f"NCR-{y}-{ncr_seq[y]:04d}"
            opened = f"{month}-{rng.randint(1, DAYS_IN[m]):02d}"
            due = add_days(opened, NCR_DUE_DAYS)
            source = rng.choices(SOURCES, SOURCE_W)[0]
            sev = rng.choices(SEVERITY, SEV_W)[0]
            close_p = 0.97 if month < "2026-05" else 0.70
            closed = ""
            if rng.random() < close_p:
                closed = add_days(opened, rng.randint(5, 45))
                if closed > DATA_THROUGH:
                    closed = ""
            sup = ""
            if source == "supplier":
                sup = "SUP-003" if rng.random() < sup003_share(month) else rng.choice(
                    [s for s in SUPPLIERS if s != "SUP-003"])
            link = ""
            if sev in ("major", "critical") and capas_this_month and rng.random() < 0.6:
                link = rng.choice(capas_this_month)
            rows.append({
                "record_id": rid, "type": "NCR", "opened_date": opened,
                "closed_date": closed, "due_date": due, "status": status_for(closed, due, opened),
                "source": source, "product_line": rng.choices(LINES, LINE_W)[0],
                "severity": sev, "root_cause_category": rng.choice(RC_BY_SOURCE[source]),
                "effectiveness_verified": "", "linked_record": link, "supplier_id": sup,
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
