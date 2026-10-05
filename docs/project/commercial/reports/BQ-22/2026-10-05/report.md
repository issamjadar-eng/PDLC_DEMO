# BQ-22 — Closed loop: field signals → design inputs, or death by spreadsheet

_Demo sample data — not for clinical use._

**Verdict**: 16 of 40 lifetime signals (40.0%) died in a spreadsheet (no-action or open past the 90-day SLA); trailing 12 months: 6 of 21 (28.6%) died vs 9 landed in design/upgrade — and only 36.8% of adjudicated cohort signals met the SLA, so E-22.1 is NOT met [derived: v-main] [src: commercial/internal-signal-register@2026-10-05] [config: commercial.yml]

## Disposition funnel (trailing 12 months: opened after 2025-07-17; anchor 2026-07-17)

_Died in a spreadsheet = `no-action` plus signals still open past the 90-day SLA [config: commercial.yml] — an undispositioned signal is functionally dead even though the register calls it open (plan definition)._

| Funnel bucket | Trailing 12 months | Lifetime |
|---|---|---|
| Landed as design input / requirement change [derived: funnel] [src: commercial/internal-signal-register@2026-10-05] | 4 | 9 |
| Landed in the upgrade pipeline [derived: funnel] [src: commercial/internal-signal-register@2026-10-05] | 5 | 6 |
| Monitoring (explicit watch decision) [derived: funnel] [src: commercial/internal-signal-register@2026-10-05] | 4 | 7 |
| No action [derived: funnel] [src: commercial/internal-signal-register@2026-10-05] | 4 | 10 |
| Still open > 90 days (functionally dead) [derived: funnel] [src: commercial/internal-signal-register@2026-10-05] | 2 | 6 |
| Open ≤ 90 days (in process) [derived: funnel] [src: commercial/internal-signal-register@2026-10-05] | 2 | 2 |
| **Total** [src: commercial/internal-signal-register@2026-10-05] | 21 | 40 |

- Died in a spreadsheet: 6 of 21 trailing (28.6%); 16 of 40 lifetime (40.0%) [derived: funnel] [src: commercial/internal-signal-register@2026-10-05]
- Landed (design + upgrade): 9 trailing, 15 lifetime [derived: funnel] [src: commercial/internal-signal-register@2026-10-05]

## Time to disposition (lifetime, all dispositioned signals)

| Days opened → closed | Signals |
|---|---|
| 0–30 days [derived: disposition-distribution] [src: commercial/internal-signal-register@2026-10-05] | 0 |
| 31–60 days [derived: disposition-distribution] [src: commercial/internal-signal-register@2026-10-05] | 3 |
| 61–90 days [derived: disposition-distribution] [src: commercial/internal-signal-register@2026-10-05] | 11 |
| 91–120 days [derived: disposition-distribution] [src: commercial/internal-signal-register@2026-10-05] | 9 |
| 121–180 days [derived: disposition-distribution] [src: commercial/internal-signal-register@2026-10-05] | 9 |
| >180 days [derived: disposition-distribution] [src: commercial/internal-signal-register@2026-10-05] | 0 |

- Median time to disposition: 103.5 days — the 90-day SLA line sits between the third and fourth buckets [derived: disposition-distribution] [src: commercial/internal-signal-register@2026-10-05] [config: commercial.yml]
- Monthly signals opened vs dispositions closed are charted (zero-filled) [derived: signal-trend] [src: commercial/internal-signal-register@2026-10-05]

## Where the loop DID close (exemplars with refs)

| Signal | Opened | Category | Disposition | Ref | Days to disposition |
|---|---|---|---|---|---|
| SIG-2025-004 [src: commercial/internal-signal-register@2026-10-05] | 2025-02-06 | alarm-fatigue | design-input | DI-0045 | 110 |
| SIG-2025-005 [src: commercial/internal-signal-register@2026-10-05] | 2025-03-13 | keypad-wear | requirement-change | REQ-0046 | 84 |
| SIG-2025-006 [src: commercial/internal-signal-register@2026-10-05] | 2025-03-19 | dose-programming | design-input | DI-0042 | 73 |
| SIG-2025-016 [src: commercial/internal-signal-register@2026-10-05] | 2025-05-31 | dose-programming | requirement-change | REQ-0048 | 97 |
| SIG-2025-017 [src: commercial/internal-signal-register@2026-10-05] | 2025-06-10 | battery | upgrade-item | UPG-0052 | 70 |
| SIG-2025-019 [src: commercial/internal-signal-register@2026-10-05] | 2025-06-21 | alarm-fatigue | design-input | DI-0043 | 148 |
| SIG-2025-020 [src: commercial/internal-signal-register@2026-10-05] | 2025-08-10 | screen-display | requirement-change | REQ-0047 | 157 |
| SIG-2025-021 [src: commercial/internal-signal-register@2026-10-05] | 2025-08-17 | dose-programming | design-input | DI-0044 | 113 |
| SIG-2025-024 [src: commercial/internal-signal-register@2026-10-05] | 2025-10-01 | drug-library | requirement-change | REQ-0049 | 179 |
| SIG-2025-028 [src: commercial/internal-signal-register@2026-10-05] | 2025-11-10 | over-delivery | upgrade-item | UPG-0101 | 88 |
| SIG-2026-002 [src: commercial/internal-signal-register@2026-10-05] | 2026-01-10 | tubing-set | upgrade-item | UPG-0050 | 86 |
| SIG-2026-003 [src: commercial/internal-signal-register@2026-10-05] | 2026-01-19 | alarm-fatigue | design-input | DI-0041 | 120 |
| SIG-2026-004 [src: commercial/internal-signal-register@2026-10-05] | 2026-02-03 | screen-display | upgrade-item | UPG-0053 | 127 |
| SIG-2026-005 [src: commercial/internal-signal-register@2026-10-05] | 2026-02-17 | over-delivery | upgrade-item | UPG-0102 | 101 |
| SIG-2026-009 [src: commercial/internal-signal-register@2026-10-05] | 2026-05-25 | battery | upgrade-item | UPG-0051 | 53 |

- Both over-delivery signals closed the loop into upgrade items (SIG-2025-028 → UPG-0101, SIG-2026-005 → UPG-0102) — see BQ-20's franchise-killer watch [derived: exemplars] [src: commercial/internal-signal-register@2026-10-05]
- Refs are trusted from the register; a cross-system trace (register ↔ DHF ↔ upgrade
  campaign) has not yet verified them (stated gap, per the plan).

## Assumptions & expectations — plan vs actual

_`unvalidated` means the expectation itself is a stand-in that has not been grounded
in a plan of record or the risk file — challenge the assumption, not just the actual._

| ID | Expectation | Expected | Actual | Verdict | Basis |
|---|---|---|---|---|---|
| E-22.1 | Every field signal reaches a disposition within the review SLA [derived: sla-compliance] [src: commercial/internal-signal-register@2026-10-05] [config: commercial.yml] | 100% dispositioned within 90 days of opening | 36.8% of adjudicated cohort signals dispositioned within 90 days (7 within, 12 breached incl. 2 stale-open; 2 recent-open pending, excluded) | not-met (unvalidated) | stand-in for the QMS signal-review SLA [VERIFY against the post-market SOP] |

## Narrative — Risks / Mitigations / Issues

### Issues (materialized — needs action)

- **I1 (high)** — 40.0% of lifetime signals (10 no-action + 6 open past 90 days) never reached the design or upgrade pipeline — the post-market → design-input loop is leaking [derived: funnel] [src: commercial/internal-signal-register@2026-10-05] [config: commercial.yml]
  - _Action_: Triage every stale-open signal to a disposition this quarter; require a recorded rationale for no-action dispositions; put SLA aging on the management-review dashboard [derived: funnel] [src: commercial/internal-signal-register@2026-10-05] [config: commercial.yml]
- **I2 (medium)** — Even signals that DO get dispositioned run slow: only 36.8% of the adjudicated cohort met the 90-day SLA (median lifetime time-to-disposition 103.5 days) [derived: sla-compliance] [derived: disposition-distribution] [src: commercial/internal-signal-register@2026-10-05]
  - _Action_: Set a triage checkpoint at day 30 for every open signal; report aging weekly to the signal-review board [derived: sla-compliance] [derived: disposition-distribution] [src: commercial/internal-signal-register@2026-10-05]

### Risks (potential — mitigation identified)

- **R1 (medium)** — The 90-day SLA is a stand-in, not yet traced to the post-market SOP — the verdict is only as good as its threshold [config: commercial.yml]
  - _Mitigation_: Verify the SLA against the QMS post-market surveillance SOP and mark E-22.1 validated [config: commercial.yml]
- **R2 (medium)** — Landed dispositions are trusted from the register's DI-/REQ-/UPG- refs — no cross-system trace yet verifies those refs exist in the requirements or upgrade systems [derived: exemplars]
  - _Mitigation_: Build the register ↔ DHF ↔ upgrade-campaign trace as a follow-on check [derived: exemplars]

### Watch

- **W1 (medium)** — The loop CAN close: 15 signals landed with refs, including both over-delivery signal(s) (SIG-2025-028 → UPG-0101, SIG-2026-005 → UPG-0102) — the counter-beat to BQ-20's franchise-killer watch [derived: exemplars] [src: commercial/internal-signal-register@2026-10-05]

## Method & provenance

- All funnel and SLA facts measured from [src: commercial/internal-signal-register@2026-10-05]; SLA and window constants [config: commercial.yml].
- As-of anchor = latest date present in the pinned register (2026-07-17) — no clocks; the trailing window is the 365 days ending there [derived: funnel] [src: commercial/internal-signal-register@2026-10-05].
- SLA verdict excludes recent-open signals from the denominator (in-process, counted
  and stated) [derived: sla-compliance] [src: commercial/internal-signal-register@2026-10-05].
