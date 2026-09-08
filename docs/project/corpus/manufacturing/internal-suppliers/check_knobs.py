#!/usr/bin/env python3
"""Assert seam for internal-suppliers — proves the planted narrative knobs landed
(runs on every acquire AND validate)."""
import csv, sys

DATA_THROUGH = "2026-08-31"
rows = list(csv.DictReader(open(sys.argv[1], newline="")))
fails = []


def reject_rate(sid, lo, hi):
    sub = [r for r in rows if r["supplier_id"] == sid and lo <= r["period"] <= hi]
    rec = sum(int(r["lots_received"]) for r in sub)
    return sum(int(r["lots_rejected"]) for r in sub) / rec if rec else None


# knob 1: SUP-003 is single-source, its audit is overdue at the data horizon, and its
# 2026-Q3 reject rate is at least double its 2025 rate
s3 = [r for r in rows if r["supplier_id"] == "SUP-003"]
if not s3 or s3[0]["single_source"] != "true":
    fails.append("knob1: SUP-003 is not flagged single_source")
if not s3 or s3[0]["next_audit_due"] >= DATA_THROUGH:
    fails.append("knob1: SUP-003 audit is not overdue")
r25, r26 = reject_rate("SUP-003", "2025-01", "2025-12"), reject_rate("SUP-003", "2026-07", "2026-08")
if None in (r25, r26) or r26 < 2 * r25:
    fails.append(f"knob1: SUP-003 reject rate 2025={r25} 2026-Q3={r26} (expected >= 2x)")

# knob 2: SUP-006 is on probation and carries a D-or-C scorecard in most periods
s6 = [r for r in rows if r["supplier_id"] == "SUP-006"]
if not s6 or s6[0]["approval_status"] != "probation":
    fails.append("knob2: SUP-006 is not on probation")
weak = sum(1 for r in s6 if r["scorecard"] in ("C", "D"))
if not s6 or weak / len(s6) < 0.6:
    fails.append(f"knob2: SUP-006 C/D scorecards {weak}/{len(s6)} (expected >= 60%)")

# knob 3: no other approved supplier is audit-overdue
others = {r["supplier_id"] for r in rows
          if r["supplier_id"] != "SUP-003" and r["next_audit_due"] < DATA_THROUGH}
if others:
    fails.append(f"knob3: unexpected audit-overdue suppliers {sorted(others)}")

if fails:
    print("\n".join(fails)); sys.exit(1)
print(f"knobs OK ({len(rows)} rows; SUP-003 reject {r25:.3f}->{r26:.3f}; SUP-006 weak {weak}/{len(s6)})")
