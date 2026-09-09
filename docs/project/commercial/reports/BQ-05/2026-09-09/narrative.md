---
report_sha256: 910277839e6f91b1a2b5ab73fc34d739a3c6fe07db83d4a7031a9365233d8af5
data_sha256: e59c36e98a30b3ae4b0d1db35dbc0fb8a78201a456efcc53a12c899b2bf0c5ee
generated_at: '2026-09-09T00:32:19+00:00'
author: AI assistant (grounded on report.md + data.json)
---
## Executive summary

$366.0M of the $1,000.0M five-year plan sits behind FDA decisions not yet received, and the plan breaches its 40% exposure threshold in two consecutive years [derived: v-main] [src: commercial/internal-revenue-plan@2026-07-27] [config: commercial.yml]. Exposure reaches 42.9% in FY2029 and peaks at 60.0% in FY2030 — meaning more than half of the largest plan year depends on clearances not yet in hand [derived: exposure-by-year] [src: commercial/internal-revenue-plan@2026-07-27]. This finding informs whether the board should require formal contingency plans for FY2029 and FY2030 before locking the plan of record. The single biggest caveat: the 40% threshold is a stand-in; the plan of record sets no risk-appetite ceiling of its own [derived: exposure-by-year] [config: commercial.yml].

## Plan revenue by regulatory dependency per plan year

The plan is front-loaded with cleared revenue — $103.0M of $105.0M in FY2026 carries no FDA dependency — but that cushion erodes rapidly as PCCP-enabled and new-submission categories grow [src: commercial/internal-revenue-plan@2026-07-27] [derived: exposure-by-year]. By FY2030, PCCP-enabled revenue reaches $140.0M and new-submission revenue reaches $70.0M, together accounting for $210.0M of FY2030's $350.0M total [src: commercial/internal-revenue-plan@2026-07-27] [derived: exposure-by-year]. Letter-to-file revenue grows from $2.0M to $12.0M across the window but is deliberately excluded from the dependent category because it requires internal documentation, not an FDA decision [src: commercial/internal-revenue-plan@2026-07-27] [config: commercial.yml]. The practical consequence: cleared and letter-to-file revenue alone cannot carry the plan in FY2029 or FY2030; the PCCP and new-submission bets must land on schedule.

## Slip scenarios (derived — method stated)

A 6-month slip of all dependent revenue reduces FY2030 from $350.0M to $297.5M and pushes $105.0M past the five-year window entirely [derived: slip-scenarios] [src: commercial/internal-revenue-plan@2026-07-27] [config: commercial.yml]. A 12-month slip is more severe: FY2030 falls to $245.0M and $210.0M leaves the window [derived: slip-scenarios] [src: commercial/internal-revenue-plan@2026-07-27] [config: commercial.yml]. The method distributes dependent revenue uniformly within each plan year and cannot disaggregate slips by individual submission program, because the plan carries no submission-event linkage [derived: slip-scenarios]. These are arithmetic outcomes of the stated method — they become decision-relevant only when the regulatory team supplies submission-timeline confidence to weight them.

## Context: how long one FDA review cycle runs (real public data)

The public record shows a median FRN 510(k) review interval of 214.0 days received-to-decision across 30 clearances since 2021 [derived: fda-review-stat] [src: commercial/openfda-510k-infusion@2026-09-09]. The report notes that 214.0 days already exceeds the span of the smallest slip scenario — a single review running at the historical median pace is enough to push dependent revenue into slip territory [derived: fda-review-stat] [src: commercial/openfda-510k-infusion@2026-09-09]. Two limits apply to this benchmark: it covers traditional and special 510(k) clearances for product code FRN only, not PCCP or De Novo/PMA pathways, and it reflects industry history — not this company's own submission record [src: commercial/openfda-510k-infusion@2026-09-09].

## Assumptions & expectations — plan vs actual

The single expectation tracked — regulatory-dependent revenue staying below 40% in every plan year — is not met: FY2029 registers 42.9% and FY2030 registers 60.0% [derived: exposure-by-year] [config: commercial.yml]. The verdict is flagged "unvalidated" because the 40% threshold is itself a stand-in; the plan of record sets no formal risk-appetite ceiling [derived: exposure-by-year] [config: commercial.yml]. That gap matters for governance: a breach of a board-approved limit would compel a plan revision, while a breach of a stand-in threshold first requires confirming whether the limit is the right one before deciding what the breach demands.

## Narrative — Risks / Mitigations / Issues

Issues I1 and I2 are both rated high and require the same remedy: the plan must carry formal contingencies for FY2029 ($105.0M exposed) and FY2030 ($210.0M exposed), with each dependent revenue block tied to a named submission milestone so any slip becomes a trackable event rather than a surprise [derived: exposure-by-year] [src: commercial/internal-revenue-plan@2026-07-27] [config: commercial.yml]. Risks R1 and R2 translate the same exposure into scenario terms: a 6-month slip removes $105.0M from the five-year window, and a 12-month slip removes $210.0M [derived: slip-scenarios] [src: commercial/internal-revenue-plan@2026-07-27] [config: commercial.yml]. Both are arithmetic descriptions of the plan structure, not probability-weighted forecasts, and become actionable only when paired with regulatory-team confidence in submission timelines [derived: slip-scenarios] [config: commercial.yml]. Watch items W1 and W2 flag two data gaps that limit the analysis: the public 214.0-day median benchmark is not directly applicable to PCCP or novel pathways, and the uniform slip method cannot be disaggregated by program without a submission register dataset [derived: fda-review-stat] [src: commercial/openfda-510k-infusion@2026-09-09] [derived: slip-scenarios].
