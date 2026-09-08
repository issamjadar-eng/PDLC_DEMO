#!/usr/bin/env python3
"""Assert seam for internal-ncr-capa — proves the planted narrative knobs landed
(runs on every acquire AND validate)."""
import csv, sys

rows = list(csv.DictReader(open(sys.argv[1], newline="")))
fails = []
capas = [r for r in rows if r["type"] == "CAPA"]
ncrs = [r for r in rows if r["type"] == "NCR"]

# knob 1: past-due open CAPAs exist, at least one is critical, and the 2026 open cohort
# carries more past-due CAPAs than the 2025 cohort
overdue = [r for r in capas if r["status"] == "overdue-open"]
if len(overdue) < 5:
    fails.append(f"knob1: only {len(overdue)} past-due open CAPAs (expected >= 5)")
if not any(r["severity"] == "critical" for r in overdue):
    fails.append("knob1: no critical CAPA past due")
def overdue_at(month_end):
    """Past-due open CAPAs reconstructed at a month-end from the record dates alone."""
    return sum(1 for r in capas if r["due_date"] < month_end
               and (not r["closed_date"] or r["closed_date"] > month_end))

o25, o26 = overdue_at("2025-12-31"), overdue_at("2026-08-31")
if o26 < o25 + 5:
    fails.append(f"knob1: past-due open CAPAs at 2025-12-31={o25} at 2026-08-31={o26} (expected rising by >= 5)")

# knob 2: SUP-003 holds the plurality of supplier-sourced NCRs (>= 40%)
sup_ncrs = [r for r in ncrs if r["source"] == "supplier"]
s3 = sum(1 for r in sup_ncrs if r["supplier_id"] == "SUP-003")
if not sup_ncrs or s3 / len(sup_ncrs) < 0.40:
    fails.append(f"knob2: SUP-003 share of supplier NCRs = {s3}/{len(sup_ncrs)} (expected >= 40%)")

# knob 3: effectiveness verification lags — verified share of closed CAPAs is lower for
# 2026 closures than for 2025 closures
def ver_share(year):
    c = [r for r in capas if r["closed_date"].startswith(year)]
    return (sum(1 for r in c if r["effectiveness_verified"] == "true") / len(c)) if c else None

v25, v26 = ver_share("2025"), ver_share("2026")
if None in (v25, v26) or v26 >= v25:
    fails.append(f"knob3: effectiveness-verified share 2025={v25} 2026={v26} (expected falling)")

# integrity: every linked_record points at an existing CAPA id
ids = {r["record_id"] for r in capas}
bad = [r["record_id"] for r in ncrs if r["linked_record"] and r["linked_record"] not in ids]
if bad:
    fails.append(f"integrity: dangling linked_record on {bad[:5]}")

if fails:
    print("\n".join(fails)); sys.exit(1)
print(f"knobs OK ({len(rows)} rows: {len(ncrs)} NCR / {len(capas)} CAPA; past-due CAPAs "
      f"{len(overdue)} (at 2025-12-31 {o25} -> 2026-08-31 {o26}); SUP-003 {s3}/{len(sup_ncrs)} "
      f"supplier NCRs; eff-verified {v25:.2f}->{v26:.2f})")
