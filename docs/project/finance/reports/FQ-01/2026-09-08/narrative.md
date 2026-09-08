---
report_sha256: de7d0969ffb91f797a80d2a41178e7687e89d32e9fdeee9afa744588d9383812
data_sha256: f67d11a56e481042b7c3f3104a199a93c60658d9ee46005e9c2d7dd244aa5dcf
generated_at: '2026-09-08T19:39:14+00:00'
author: AI assistant (grounded on report.md + data.json)
---
## Executive summary

H1 2026 company gross margin landed at 51.5% — up +1.0 pts versus 50.6% in H1 2025 [derived: gm-stat] — but remains below the 55% floor [config: finance.yml], and the headline improvement masks deterioration in two product lines. PP3000 and IP5000 each fell -1.5 pts year-over-year [derived: gm-by-line] [src: commercial/internal-financials@2026-07-27], driven by hardware unit costs running more than 10% above standard on both lines [derived: cost-variance-by-line] [src: finance/internal-standard-costs@2026-09-08]. The decision this report informs is whether to reset standard costs and take price action on those two lines at the next quarterly margin review, or to accelerate run-down. The central caveat: the 55% floor is an unratified board-deck carry-forward [config: finance.yml]; until finance puts it in a plan of record, the gap is directionally concerning but not a confirmed breach of a binding target [derived: gm-stat].

## Gross margin by product line

Four of six lines held margin flat year-over-year, and cloud-suite anchors at 78.0% [src: commercial/internal-financials@2026-07-27]. The problem is concentrated: PP3000 at 44.9% and IP5000 at 45.6% are both well below the 55% floor and falling [derived: gm-by-line] [src: commercial/internal-financials@2026-07-27] [config: finance.yml]. PP3500, the highest-revenue line at $22.40M in H1 2026, held exactly flat at 49.5% [src: commercial/internal-financials@2026-07-27] — meaningful because it means the company aggregate is being lifted by mix rather than by broad line improvement. If PP3000 or IP5000 revenue grows relative to PP3500, the mix tailwind reverses [derived: gm-by-line].

## Gross margin by region

All three regions landed at 51.5% gross margin in H1 2026, each up roughly +1 pt versus the prior year — APAC +1.1 pts, EMEA +0.9 pts, NA +0.9 pts [src: commercial/internal-financials@2026-07-27]. The uniformity across regions confirms that the margin signal is product-mix and cost-structure driven, not a regional pricing or channel problem. Because the standard-cost roll-up carries no region dimension [src: finance/internal-standard-costs@2026-09-08], this view cannot isolate whether one region bears a disproportionate share of the hardware cost overrun on PP3000 or IP5000.

## Standard-vs-actual cost variance by line

The line-total variance stays within the ±5% review tolerance for all six lines [derived: cost-variance-by-line] [config: finance.yml], but that headline passes only because consumables and service revenue dilute the hardware signal. Strip those out and hardware unit cost on PP3000 runs +11.0% above standard and on IP5000 +10.9% above standard [src: commercial/internal-financials@2026-07-27] [src: finance/internal-standard-costs@2026-09-08] — both well past the ±5% threshold [config: finance.yml]. PP3500 hardware variance is -2.8%, favorable, and SP6000 is effectively flat [derived: cost-variance-by-line]. The hardware column is the leading indicator the line total obscures, and both eroding lines are flashing it.

## Standard-cost variance by region: not computable (stated, not approximated)

Regional variance cannot be computed because the standard-cost roll-up holds no region dimension [src: finance/internal-standard-costs@2026-09-08] and actual COGS is regional [src: commercial/internal-financials@2026-07-27] — a regional variance requires either a regional standard or a regional actual-cost feed from the ERP [derived: cost-variance-by-region]. This is a data-architecture gap, not a data-quality gap. Until one of those feeds exists, regional cost accountability cannot be established from the current reporting stack.

## Assumptions & expectations — plan vs actual

E-01.1 is not met: company gross margin at 51.5% falls short of the ≥55% floor [derived: gm-stat] [derived: gm-by-line] [config: finance.yml]. E-01.2 is technically met at the line-total level — 0 of 6 lines breach ±5% when all revenue types are included [derived: cost-variance-by-line] [config: finance.yml] — but hardware-only variance puts PP3000 at +11.0% and IP5000 at +10.9%, both beyond the tolerance [src: finance/internal-standard-costs@2026-09-08]. Both expectations are marked unvalidated, meaning neither the 55% floor nor the ±5% tolerance has been ratified in a plan of record or controller policy [VERIFY]; a future ratification could reclassify E-01.2 from "met" to "breached" if the hardware-only column is adopted as the trigger.

## Narrative — Risks / Mitigations / Issues

The two materialized issues share the same root shape: margin erosion of -1.5 pts on PP3000 [derived: gm-by-line] and -1.5 pts on IP5000 [derived: gm-by-line] [src: commercial/internal-financials@2026-07-27] is being driven by hardware unit costs that have drifted well above the standards used to book COGS [derived: cost-variance-by-line] [src: finance/internal-standard-costs@2026-09-08]. The most immediate risk (R2) is that reported margin on those lines overstates actual economics — booked costs understate reality when standards are stale [derived: cost-variance-trend] [src: commercial/internal-financials@2026-07-27] [src: finance/internal-standard-costs@2026-09-08]. W1 is the diagnostic trap to watch: the company aggregate is up +1.0 pts [derived: gm-stat], so a dashboard that stops at the top line will miss that two lines are eroding while the mix holds the number up [derived: gm-by-line].
