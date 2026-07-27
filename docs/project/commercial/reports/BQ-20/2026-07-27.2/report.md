# BQ-20 — Franchise-killer watch: opioid over-delivery / PCA-by-proxy

_Demo sample data — not for clinical use._

**Verdict**: WATCH TRIGGERED on our internal log (demo-fabricated): 3 over-delivery and 2 PCA-by-proxy-suspected complaint records (2 MDR-filed, 1 under investigation) — E-20.1 zero-tolerance NOT met; the signal→upgrade loop closed for 2 watch-category signals; real class-wide MAUDE context is counts-only (no denominator) [derived: v-main] [src: commercial/internal-complaints@2026-07-27.2] [config: commercial.yml]

## Watch-category events on the internal complaint log (event-level)

_Single events, not trends, are the signal here — every record is listed. Watch
categories are declared in [config: commercial.yml]; 'confirmed' for E-20.1 is any
record not dismissed as unfounded (the log has no dismissed status) [config: commercial.yml]._

| Complaint | Opened | Region | Model / firmware | Category | Severity | Status | MDR filed |
|---|---|---|---|---|---|---|---|
| C-2025-0431 [src: commercial/internal-complaints@2026-07-27.2] | 2025-08-14 | EMEA | PP3500 / 3.1.2 | over-delivery | 3 | closed | yes |
| C-2025-0434 [src: commercial/internal-complaints@2026-07-27.2] | 2025-11-20 | NA | PP3500 / 3.2.0 | pca-by-proxy-suspected | 3 | closed | no |
| C-2026-0432 [src: commercial/internal-complaints@2026-07-27.2] | 2026-03-05 | EMEA | PP3500 / 3.2.0 | over-delivery | 3 | closed | no |
| C-2026-0435 [src: commercial/internal-complaints@2026-07-27.2] | 2026-05-16 | NA | PP3500 / 3.1.2 | pca-by-proxy-suspected | 3 | open | no |
| C-2026-0433 [src: commercial/internal-complaints@2026-07-27.2] | 2026-06-27 | APAC | PP3500 / 3.2.0 | over-delivery | 3 | under-investigation | yes |

- 5 watch-category records total: 3 over-delivery, 2 PCA-by-proxy-suspected; 2 MDR-filed, 1 under investigation [derived: watch-events] [src: commercial/internal-complaints@2026-07-27.2]
- Under-investigation over-delivery event(s) on the log: C-2026-0433 [src: commercial/internal-complaints@2026-07-27.2]. The docket's open over-delivery MDR item(s): MDR-2026-0005 [derived: docket-watch] [src: commercial/internal-regulatory-docket@2026-07-27] — a category-level join (no shared key between the complaint log and the docket, per the plan); deadline posture is BQ-21's answer

## Signal-register linkage — is the loop closing for this category?

| Signal | Opened | Source | Category | Disposition | Ref | Closed |
|---|---|---|---|---|---|---|
| SIG-2025-028 [src: commercial/internal-signal-register@2026-07-27.2] | 2025-11-10 | maude-screen | over-delivery | upgrade-item | UPG-0101 | 2026-02-06 |
| SIG-2026-005 [src: commercial/internal-signal-register@2026-07-27.2] | 2026-02-17 | complaint-trend | over-delivery | upgrade-item | UPG-0102 | 2026-05-29 |

- 2 of 2 watch-category signals reached the corrective pipeline (both over-delivery signals landed as upgrade-items) [derived: watch-signals] [src: commercial/internal-signal-register@2026-07-27.2]

## Class-wide context — real PCA MAUDE trend (counts only)

- Monthly MAUDE event counts for product code MEA (PCA pumps) since 2023 are charted [derived: class-monthly-events] [src: commercial/openfda-maude-pca-monthly@2026-07-27]; the trailing 3 months (2026-04, 2026-05, 2026-06) are EXCLUDED — MAUDE reporting lag makes them artificially low, and charting them would fake a decline [src: commercial/openfda-maude-pca-monthly@2026-07-27].
- Lag caveat: the dataset README warns the reporting-lag tail runs ~3–6 months, so the 3-month trim is the lower bound of that range and the lag may run longer than the trim — the charted tail can still be incomplete; read a recent-month dip as lag, not signal [src: commercial/openfda-maude-pca-monthly@2026-07-27].
- 12,614 class-wide events in the charted window [derived: total-class-events] [src: commercial/openfda-maude-pca-monthly@2026-07-27].
- NO DENOMINATOR: MAUDE carries no installed-base or therapy-volume denominator, so no
  rate is computed or published — a rate would require the installed-base assumption
  [assume: A-001], which is deliberately not yet quantified; counts support trend/shape
  reading only.
- These are REAL public data about the whole PCA class; our internal events above are
  demo-fabricated. The two are never compared numerically (different populations,
  reporting propensities, and provenance) — see the analysis plan.

## Assumptions & expectations — plan vs actual

_`unvalidated` means the expectation itself is a stand-in that has not been grounded
in a plan of record or the risk file — challenge the assumption, not just the actual._

| ID | Expectation | Expected | Actual | Verdict | Basis |
|---|---|---|---|---|---|
| E-20.1 | Zero confirmed over-delivery events in the field [derived: watch-events] [src: commercial/internal-complaints@2026-07-27.2] [config: commercial.yml] | 0 confirmed over-delivery complaints | 3 over-delivery complaint records on the log (2 MDR-filed, 1 under investigation) — zero-tolerance breached per the plan's 'confirmed' definition | not-met (unvalidated) | franchise-killer tolerance — any occurrence escalates to CMO; threshold not yet ratified in the risk file [VERIFY] |

## Narrative — Risks / Mitigations / Issues

### Issues (materialized — needs action)

- **I1 (high)** — 3 over-delivery complaint records on the internal log — the franchise-killer category; newest is C-2026-0433 (2026-06-27, under-investigation, MDR filed: yes); the docket carries open over-delivery MDR item(s) MDR-2026-0005 — a category-level join, no shared key (see BQ-21) [derived: watch-events] [derived: docket-watch] [src: commercial/internal-complaints@2026-07-27.2] [src: commercial/internal-regulatory-docket@2026-07-27]
  - _Action_: CMO review of each event this cycle; confirm the open investigation's MDR stays on deadline; assess whether the risk file's over-delivery controls need re-evaluation [derived: watch-events] [derived: docket-watch] [src: commercial/internal-complaints@2026-07-27.2] [src: commercial/internal-regulatory-docket@2026-07-27]
- **I2 (high)** — 2 PCA-by-proxy-suspected records (unauthorized bolus by family/visitor suspected); 1 still open — a use-environment hazard the pump's lockout design must answer [derived: watch-events] [src: commercial/internal-complaints@2026-07-27.2]
  - _Action_: Route to human-factors / risk-management review; check labeling and in-service training coverage of proxy dosing at the affected sites [derived: watch-events] [src: commercial/internal-complaints@2026-07-27.2]

### Risks (potential — mitigation identified)

- **R1 (medium)** — The question asks for alarm data, but raw alarm telemetry is not a corpus dataset — only signals sourced from alarm analytics are visible, so an alarm-signature precursor of over-delivery could be missed [derived: alarm-data-gap]
  - _Mitigation_: Acquire an alarm-analytics event-level dataset; until then this watch is complaints + register only (stated in the plan) [derived: alarm-data-gap]

### Watch

- **W1 (medium)** — Loop-closing counter-beat: 2 watch-category signals reached the corrective pipeline (SIG-2025-028 → UPG-0101, SIG-2026-005 → UPG-0102) — the signal→corrective loop is demonstrably closing for this category (see BQ-22) [derived: watch-signals] [src: commercial/internal-signal-register@2026-07-27.2]
- **W2 (medium)** — Real class-wide PCA MAUDE events run 12,614 since 2023 in the lag-trimmed window — context only: counts, never rates, and never compared numerically to our internal log [derived: total-class-events] [src: commercial/openfda-maude-pca-monthly@2026-07-27]

## Method & provenance

- Watch-category events and MDR flags measured from [src: commercial/internal-complaints@2026-07-27.2]; watch list [config: commercial.yml].
- Signal dispositions measured from [src: commercial/internal-signal-register@2026-07-27.2]; the complaint↔docket tie is derived from the pinned docket rows [src: commercial/internal-regulatory-docket@2026-07-27] as a category-level join (no shared key), per the plan [derived: docket-watch].
- Class-wide trend measured from openFDA's date-count API [src: commercial/openfda-maude-pca-monthly@2026-07-27] (public domain); lag-tail exclusion and the no-denominator constraint per the plan and [assume: A-001].
