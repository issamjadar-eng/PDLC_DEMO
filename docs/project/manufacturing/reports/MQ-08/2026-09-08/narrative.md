---
report_sha256: ce1ca0500a3cd38fadda798f0b680d67ae0cc959a41e870f3abb01fa2ef0f8d7
data_sha256: 0f9087c066cb5e6fda2f856860b846ac9a54755e5137538b3b71707450c2db33
generated_at: '2026-09-08T19:50:48+00:00'
author: AI assistant (grounded on report.md + data.json)
---
## Executive summary

The manufacturing posture at 2026-08-31 has two urgent problems that require executive action now: 10 overdue calibrations concentrated at Westfield and 3 open PP3500 rev C validation items that have not prevented lot releases [derived: posture-stat] [src: manufacturing/internal-process-validation@2026-09-08]. The calibration gap is a quality-system failure — instruments up to 121 days past their due dates put every lot record touched by those assets in question [derived: overdue-calibrations] [src: manufacturing/internal-process-validation@2026-09-08]. The harder exposure is that 65 rev C lots shipped since 2026-03-25 before the test-fixture PQ was complete; whether any of those lots ran on the unvalidated rev C fixture cannot be determined from the register alone and requires tracing individual DHRs [derived: revc-blockers] [derived: revc-lots] [src: manufacturing/internal-process-validation@2026-09-08] [src: manufacturing/internal-production-lots@2026-09-08]. This data demands two immediate decisions: authorize a CAPA investigation on fixture routing for the 65 released lots, and pull the 10 overdue instruments from service [derived: overdue-calibrations] [derived: revc-lots]. The key caveat: both performance expectations framing these gaps are stand-ins not grounded in a verified procedure or plan of record, so the formal severity of the breach depends on what those source documents actually require.

## Headline

The register covers 155 entries across two sites as of 2026-08-31, with 10 items overdue and 6 falling due within 30 days [derived: posture-stat] [src: manufacturing/internal-process-validation@2026-09-08] [config: manufacturing.yml]. Every overdue item is a calibration — IQ, OQ, and PQ records are fully current [src: manufacturing/internal-process-validation@2026-09-08]. The 6 due-soon items are all preventive-maintenance records; they have not yet crossed into overdue, but the proximity to the as-of date means several may already be past due by the time this report is acted on [derived: posture-stat] [src: manufacturing/internal-process-validation@2026-09-08] [config: manufacturing.yml].

## By site

Westfield carries 9 of the 10 overdue items against 78 register entries; Eastbrook has 1 overdue item against 77 entries [src: manufacturing/internal-process-validation@2026-09-08]. The due-soon split is even at 3 items per site [src: manufacturing/internal-process-validation@2026-09-08]. That imbalance tells you where to focus remediation — Westfield's metrology program is the primary failure point, not a company-wide systemic drift.

## By record type

All 10 overdue items are calibrations; IQ, OQ, and PQ records show zero overdue [src: manufacturing/internal-process-validation@2026-09-08]. The 6 due-soon items belong entirely to the preventive-maintenance category [src: manufacturing/internal-process-validation@2026-09-08]. The formal validation program is current; the risk sits in the equipment metrology and maintenance scheduling layers, which are exactly the records that underpin the validity of everything else in the register.

## By product line

PP3500 has 3 overdue calibrations across 47 entries; shared infrastructure adds 3 more overdue items that can affect PP3500 production [src: manufacturing/internal-process-validation@2026-09-08]. SP6500 carries 2 overdue items, and IP5000 and SP6000 each carry 1 [src: manufacturing/internal-process-validation@2026-09-08]. The 3 shared overdue calibrations are a portfolio-wide exposure rather than a single-program problem — any product line whose lots were measured with those instruments faces the same impact-assessment obligation.

## Overdue calibrations

Nine of the 10 overdue instruments are at Westfield, with thermocouple set #06 the oldest at 121 days past due [derived: overdue-calibrations] [src: manufacturing/internal-process-validation@2026-09-08]. Three instruments directly support PP3500: leak tester reference #05 at 99 days overdue, electrical safety analyzer #08 at 89 days overdue, and syringe pump reference #09 at 79 days overdue — all at Westfield [derived: overdue-calibrations] [src: manufacturing/internal-process-validation@2026-09-08]. The spread from 21 to 121 days past due shows that slippage at Westfield is broad across asset types, not isolated to a single instrument or program [derived: overdue-calibrations] [src: manufacturing/internal-process-validation@2026-09-08].

## PP3500 rev C release blockers

The fixture PQ for the final functional test fixture rev C is in-progress at both Eastbrook and Westfield with a due date of 2026-09-30, and the occlusion pressure test process rev C OQ at Westfield has not yet started with a due date of 2026-10-15 [src: manufacturing/internal-process-validation@2026-09-08]. Despite those open validations, 65 rev C lots have been released since 2026-03-25, and 4 additional lots are held only by DHR gaps [derived: revc-lots] [src: manufacturing/internal-production-lots@2026-09-08]. The critical unknown is which fixture tested each of the 65 released lots; the register does not record fixture routing, so that determination requires reviewing individual DHRs rather than the register data alone [derived: revc-blockers] [derived: revc-lots] [src: manufacturing/internal-process-validation@2026-09-08] [src: manufacturing/internal-production-lots@2026-09-08].

## Assumptions & expectations — plan vs actual

Both expectations are flagged as unvalidated stand-ins — they have not been grounded in a distilled calibration procedure or design-transfer plan — so the verdicts below characterize a gap against a stated target, not a confirmed policy breach [derived: overdue-calibrations] [config: manufacturing.yml]. E-08.1 (zero overdue calibrations) is not met: the register records 10 overdue calibrations at 2026-08-31, with Eastbrook contributing 1 and Westfield 9 [derived: overdue-calibrations] [config: manufacturing.yml]. E-08.2 (validation before the first rev C release) is not met: 2 fixture PQ records remain in-progress and 65 rev C lots have been released since 2026-03-25, with lot releases beginning before PQ completion [derived: revc-blockers] [derived: revc-lots] [config: manufacturing.yml].

## Narrative — Risks / Mitigations / Issues

Issue I1 is the most operationally immediate: 10 calibration instruments must be pulled from service and the lots they measured since their respective due dates assessed for impact — the oldest instrument is 121 days past due, which means a wide window of potentially affected records [derived: overdue-calibrations] [src: manufacturing/internal-process-validation@2026-09-08]. Issue I2 is bounded and resolvable: 4 DHR-incomplete lots (LOT-2026-0188, LOT-2026-0223, LOT-2026-0231, LOT-2026-0236) are blocked from release pending record closure or NCR disposition [derived: revc-lots] [src: manufacturing/internal-production-lots@2026-09-08]. Risk R1 carries the highest potential consequence: 65 released rev C lots may have been tested on an unvalidated fixture, and the register cannot answer that question without DHR-level fixture routing data — if the trace confirms pre-PQ fixture use, a CAPA and unit-level assessment follow [derived: revc-blockers] [derived: revc-lots] [src: manufacturing/internal-process-validation@2026-09-08] [src: manufacturing/internal-production-lots@2026-09-08]. The 6 due-soon preventive-maintenance items in W1 warrant scheduling action before they enter the overdue column and compound the Westfield backlog already under scrutiny [derived: posture-by-site] [src: manufacturing/internal-process-validation@2026-09-08] [config: manufacturing.yml].
