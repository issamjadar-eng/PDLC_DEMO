---
report_sha256: 735939709751931fb8fc8209c03047cc76a6b32e27d76b7a1e8b3035f186c0ab
data_sha256: 23fa920a2143c1065d058b014514cb7cea9daf09e5d0c5d29fed848d44d49055
generated_at: '2026-09-08T19:42:08+00:00'
author: AI assistant (grounded on report.md + data.json)
---
## Executive summary

Recurring revenue stands at 10.8% of revenue in FY2026H1 against a FY2030 plan of 68.6% — the distance between those two numbers is the central commercial risk. [derived: v-main] [src: commercial/internal-financials@2026-07-27] [src: commercial/internal-revenue-plan@2026-07-27] Of the $350.0M FY2030 target, $128.0M rests on already-cleared products, $12.0M on letter-to-file execution, and $210.0M — 60.0% — waits on FDA decisions not yet received. [src: commercial/internal-revenue-plan@2026-07-27] [derived: y5-decomposition] The exposure is sharper inside the recurring line: 87.5% of the $240.0M cloud-suite recurring proxy ($210.0M) sits behind those same pending decisions, versus 60.0% blended across all revenue. [derived: y5-recurring-decomposition] [src: commercial/internal-revenue-plan@2026-07-27] This report informs whether to carry the aspiration bucket at plan value or to require a regulatory-contingency scenario. The single biggest caveat is that the recurring proxy carries $0.0M in letter-to-file coverage — every dollar of recurring revenue above the $30.0M cleared floor requires an FDA decision. [derived: y5-recurring-decomposition] [src: commercial/internal-revenue-plan@2026-07-27]

## Recurring share — actuals by fiscal year

Recurring share has grown each year: 5.0% in FY2024, 7.9% in FY2025, and 10.8% in FY2026H1 — the direction is right, but the pace is far below the FY2030 target. [src: commercial/internal-financials@2026-07-27] Subscription revenue rose from $3.5M in FY2024 to $5.0M in the first half of FY2026 alone, but total revenue expanded alongside it, keeping the share gains modest. [src: commercial/internal-financials@2026-07-27] FY2026H1 is a half-year of actuals and is never annualized; reading it against the full-year FY2026 plan figure of 12.4% would overstate the run rate. [src: commercial/internal-financials@2026-07-27] [src: commercial/internal-revenue-plan@2026-07-27]

## Plan trajectory — recurring proxy per plan year

The cloud-suite recurring proxy must reach $240.0M — 68.6% of plan total — by FY2030, up from $13.0M (12.4%) in FY2026. [src: commercial/internal-revenue-plan@2026-07-27] [config: commercial.yml] The share accelerates in the out-years: 35.3% of a $170.0M base in FY2028, 53.1% of $245.0M in FY2029, and 68.6% of $350.0M in FY2030 — both the share and the base total grow simultaneously. [src: commercial/internal-revenue-plan@2026-07-27] The proxy is a stand-in, not a revenue type: device-line service contracts are excluded and any non-recurring cloud revenue is included, so true recurring share may read higher or lower depending on mix. [config: commercial.yml] [src: commercial/internal-revenue-plan@2026-07-27]

## The FY2030 target decomposed — contracted / modeled / aspiration

At the $350.0M FY2030 target, 36.6% ($128.0M) rests on already-cleared products, 3.4% ($12.0M) requires letter-to-file execution only, and 60.0% ($210.0M) depends on FDA decisions not yet received. [src: commercial/internal-revenue-plan@2026-07-27] [derived: y5-decomposition] Within the recurring story the concentration is sharper: of the $240.0M cloud-suite proxy, $210.0M (87.5%) is aspiration, $30.0M is cleared, and $0.0M has letter-to-file coverage. [derived: y5-recurring-decomposition] [src: commercial/internal-revenue-plan@2026-07-27] The cleared cushion is mostly outside the recurring story — $98.0M of the $128.0M cleared bucket (76.6%) is non-recurring device revenue. [derived: y5-recurring-decomposition] [derived: y5-decomposition] [src: commercial/internal-revenue-plan@2026-07-27] What shifts this picture is a successful FDA clearance of a PCCP-enabled or new-submission product; until then the aspiration bucket carries the plan's weight.

## Assumptions & expectations — plan vs actual

The one tested expectation — that recurring share grows strictly year over year — is met: 5.0% in FY2024, 7.9% in FY2025, and 10.8% in FY2026H1. [derived: recurring-share-trend] [src: commercial/internal-financials@2026-07-27] The expectation is flagged as unvalidated: no numeric milestone was set, so meeting it confirms direction, not pace. A single reversal in any future year would flip the verdict; the trend needs monitoring as the plan enters its steeper ramp years.

## Narrative — Risks / Mitigations / Issues

The dominant risk (R1, high) is that 60.0% of the FY2030 target ($210.0M) sits behind FDA decisions not yet received, and the recurring-specific exposure is sharper: 87.5% of the $240.0M cloud-suite proxy ($210.0M) is in the same bucket. [derived: y5-decomposition] [derived: y5-recurring-decomposition] [src: commercial/internal-revenue-plan@2026-07-27] The recommended mitigation is to hold the aspiration bucket against BQ-05's exposure thresholds and require a contingency revenue line in the plan narrative. [derived: y5-decomposition] [src: commercial/internal-revenue-plan@2026-07-27] The watch item (W1) flags a measurement boundary: the cloud-suite proxy carries no revenue-type split, so it may over- or undercount true recurring revenue, and neither direction can be resolved without a finer plan breakdown. [config: commercial.yml] [src: commercial/internal-revenue-plan@2026-07-27]
