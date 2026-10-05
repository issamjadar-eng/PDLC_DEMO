# BQ-21 — Regulatory exposure: docket, MDR timeliness, open items

_Demo sample data — not for clinical use._

**Verdict**: If FDA walks in tomorrow: 2 open docket item(s) (MDR-2026-0005 due in -68 days at the pin date; FSCA-2026-001 rollout incomplete) and 1 late MDR filing(s) in the trailing 12 months — on-time rate 94.7% (18 of 19); E-21.1 NOT met [derived: v-main] [src: commercial/internal-regulatory-docket@2026-10-05] [config: commercial.yml]

## Docket roll-up (type × status; 33 records) [src: commercial/internal-regulatory-docket@2026-10-05]

| Type | Open | Filed | Closed | Total |
|---|---|---|---|---|
| correction [src: commercial/internal-regulatory-docket@2026-10-05] | 0 | 0 | 2 | 2 |
| fsca [src: commercial/internal-regulatory-docket@2026-10-05] | 1 | 0 | 0 | 1 |
| mdr [src: commercial/internal-regulatory-docket@2026-10-05] | 1 | 4 | 25 | 30 |

## MDR timeliness — trailing 12 months (filing-date basis)

- On-time rate: 94.7% — 18 of 19 MDRs filed in the window (2025-06-29 → 2026-06-29) met their deadline [derived: ontime-rate] [src: commercial/internal-regulatory-docket@2026-10-05]
- Late in window: MDR-2025-0018 (+9d) [derived: ontime-rate] [src: commercial/internal-regulatory-docket@2026-10-05]
- Lifetime late filings: MDR-2025-0007 (+4d), MDR-2025-0018 (+9d) — MDR-2025-0007 predate(s) the trailing window; the window narrows the rate, it does not hide the record [derived: ontime-rate] [src: commercial/internal-regulatory-docket@2026-10-05]
- Monthly filings vs late filings are charted (zero-filled) [derived: filing-trend] [src: commercial/internal-regulatory-docket@2026-10-05]

## Basis sensitivity (disclosed, not absorbed)

_The trailing on-time rate is published on the plan-committed basis (filed-date window,
latest-event anchor). The other defensible bases are shown so the reader sees how much
the basis choice moves the rate — and whether any verdict flips._

| Basis | On-time rate | On time / in basis | Late |
|---|---|---|---|
| filed-date window, latest-event anchor (published) [derived: basis-sensitivity] [src: commercial/internal-regulatory-docket@2026-10-05] | 94.7% | 18 of 19 | 1 |
| filed-date window, pin-date anchor [derived: basis-sensitivity] [src: commercial/internal-regulatory-docket@2026-10-05] | 100.0% | 11 of 11 | 0 |
| opened-date window, latest-event anchor [derived: basis-sensitivity] [src: commercial/internal-regulatory-docket@2026-10-05] | 93.3% | 14 of 15 | 1 |
| lifetime (all filed MDRs) [derived: basis-sensitivity] [src: commercial/internal-regulatory-docket@2026-10-05] | 93.1% | 27 of 29 | 2 |

- The published basis is not the most favorable of the 4 defensible bases [derived: basis-sensitivity]
- E-21.1 verdict is basis-SENSITIVE — it flips under: filed-date window, pin-date anchor [derived: basis-sensitivity]

## Open items vs deadline (urgency anchored at the pin date 2026-10-05)

| Record | Type | Category | Opened | Deadline | Posture |
|---|---|---|---|---|---|
| FSCA-2026-001 [src: commercial/internal-regulatory-docket@2026-10-05] | fsca | drug-library-correction | 2026-05-12 | 2026-05-26 | report filed on time; action open pending completion |
| MDR-2026-0005 [src: commercial/internal-regulatory-docket@2026-10-05] | mdr | over-delivery | 2026-06-29 | 2026-07-29 | unfiled — deadline BLOWN by 68 days |

- FSCA rollout as recorded in the docket: "Field correction: PCA drug library v3.4.1 hard-limit update. Rollout status: NA complete 2026-06, EMEA in progress (~60% sites), APAC pending" [src: commercial/internal-regulatory-docket@2026-10-05] — reported qualitatively; per-site completion telemetry is not a corpus dataset (stated gap).

## Exposure list — what an investigator finds tomorrow

- FSCA-2026-001: report filed on time; action open pending completion [derived: exposure-list] [src: commercial/internal-regulatory-docket@2026-10-05]
- MDR-2026-0005: unfiled — deadline BLOWN by 68 days [derived: exposure-list] [src: commercial/internal-regulatory-docket@2026-10-05]
- MDR-2025-0018: filed 9 days late (2025-10-04) [derived: exposure-list] [src: commercial/internal-regulatory-docket@2026-10-05]

## Assumptions & expectations — plan vs actual

_`unvalidated` means the expectation itself is a stand-in that has not been grounded
in a plan of record or the risk file — challenge the assumption, not just the actual._

| ID | Expectation | Expected | Actual | Verdict | Basis |
|---|---|---|---|---|---|
| E-21.1 | Every MDR is filed within its regulatory deadline [derived: ontime-rate] [src: commercial/internal-regulatory-docket@2026-10-05] [config: commercial.yml] | 0 late filings, trailing 12 months | 1 late filing(s) in the trailing 12 months (MDR-2025-0018 +9d); lifetime record holds 2 late filing(s) | not-met (unvalidated) | 30-day MDR filing requirement (21 CFR 803) [VERIFY against docs/external distillation] |

## Narrative — Risks / Mitigations / Issues

### Issues (materialized — needs action)

- **I1 (high)** — MDR-2026-0005 (over-delivery) is open and unfiled with -68 days to its regulatory deadline (2026-07-29) at the pin date — the over-delivery event under investigation (see BQ-20) [derived: open-items] [src: commercial/internal-regulatory-docket@2026-10-05]
  - _Action_: Confirm the MDR narrative is in final review NOW; file before the deadline; escalate to RA leadership if investigation inputs are the blocker [derived: open-items] [src: commercial/internal-regulatory-docket@2026-10-05]
- **I2 (medium)** — FSCA-2026-001 (drug-library-correction) remains open: rollout as recorded — "NA complete 2026-06, EMEA in progress (~60% sites), APAC pending" — an FDA investigator will ask why APAC has not started [derived: open-items] [src: commercial/internal-regulatory-docket@2026-10-05]
  - _Action_: Get the pending region(s) (APAC) scheduled and in-progress completion dated; track per-site completion evidence for the FSCA file [derived: open-items] [src: commercial/internal-regulatory-docket@2026-10-05]

### Risks (potential — mitigation identified)

- **R1 (medium)** — 1 MDR(s) filed late inside the trailing window (MDR-2025-0018 +9d) — a repeat-observation pattern an investigator can cite even at a 94.7% on-time rate [derived: ontime-rate] [src: commercial/internal-regulatory-docket@2026-10-05]
  - _Mitigation_: Root-cause the late filing (intake-to-decision lag vs narrative drafting); add a deadline-minus-7-days internal gate to the RA tracker [derived: ontime-rate] [src: commercial/internal-regulatory-docket@2026-10-05]
- **R2 (medium)** — This docket audits filing timeliness of what was docketed — the complaint-to-MDR reportability decision trail is not a corpus dataset, so under-docketing would be invisible here [derived: docket-rollup]
  - _Mitigation_: Acquire the reportability-decision log as a dataset; until then pair this answer with BQ-20's complaint-level watch [derived: docket-rollup]

### Watch

- **W1 (medium)** — Lifetime late filings: 2 (MDR-2025-0007 +4d; MDR-2025-0018 +9d) — 1 (MDR-2025-0007) predate(s) the trailing window but stay(s) on the audit record [derived: ontime-rate] [src: commercial/internal-regulatory-docket@2026-10-05]

## Method & provenance

- All docket facts measured from [src: commercial/internal-regulatory-docket@2026-10-05]; trailing window [config: commercial.yml].
- Two anchors per the plan: event windows at the latest event date in the pin (2026-06-29); deadline urgency at the snapshot date (2026-10-05) — both deterministic, no clocks [src: commercial/internal-regulatory-docket@2026-10-05].
- On-time = filed on or before the regulatory deadline; the rate covers MDRs by
  filing date within the window [derived: ontime-rate] [src: commercial/internal-regulatory-docket@2026-10-05].
