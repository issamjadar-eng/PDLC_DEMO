---
report_sha256: f3c012c2ccb91dc83560d83a5300d78d4f1244234fe0b6c806325925613ff250
data_sha256: 990d13195580304c9bba10b6c4799daa637997c32a0188a0f48a31589aee0887
generated_at: '2026-09-08T19:54:14+00:00'
author: AI assistant (grounded on report.md + data.json)
---
## Executive summary

Two complaint categories have crossed their post-market thresholds and require CAPA reviews now. Occlusion-alarm reached 3.17 per 100 devices against a threshold of 3.0, and connectivity reached 2.26 per 100 devices against a threshold of 2.0, both in the trailing 90-day window ending 2026-07-17 [derived: v-main] [src: commercial/internal-complaints@2026-07-27.2] [config: commercial.yml]. Total complaint volume also rose from 74 in the prior window to 101 in the current one, a broad signal that warrants monthly category-level tracking [derived: window-trend]. The data directly informs whether to open formal CAPA reviews for both categories. The key caveat: the thresholds are demo stand-ins, not the risk file's documented acceptability criteria, so breach verdicts are directionally useful but not yet regulatory-grade [config: commercial.yml].

## Trailing window, rate-normalized (stated denominator: 884 fleet devices [src: commercial/internal-fleet@2026-07-27])

Only two categories breached their thresholds: occlusion-alarm at 3.17 and connectivity at 2.26 per 100 devices [src: commercial/internal-complaints@2026-07-27.2] [config: commercial.yml]. The remaining categories sit below their shared 2.0 threshold, with battery the nearest at 1.81 per 100 devices [src: commercial/internal-complaints@2026-07-27.2] [config: commercial.yml]. Battery also shows the most favorable window-over-window movement, falling from 21 complaints in the prior window to 16 in the current one, while the two flagged categories moved in the opposite direction [src: commercial/internal-complaints@2026-07-27.2] [config: commercial.yml]. A change in threshold values — particularly if the risk file sets the occlusion-alarm threshold below 3.0 — would alter the severity picture materially [config: commercial.yml].

## Assumptions & expectations — plan vs actual

Both expectations failed this window, and neither is validated against a plan of record [config: commercial.yml]. E-18.1 requires complaint rates to stay within per-category thresholds; occlusion-alarm came in at 3.17 vs 3.0 and connectivity at 2.26 vs 2.0 [derived: rate-by-category] [config: commercial.yml]. E-18.2 requires the current window to stay within 130% of the prior window; at 101 complaints versus the prior window's 74, the expectation is not met [derived: window-trend] [config: commercial.yml]. Until thresholds are re-derived from the risk file and marked validated, every "not-met" verdict carries a qualification that the threshold itself has not been accepted [config: commercial.yml].

## Narrative — Risks / Mitigations / Issues

Two high-severity issues require immediate action: both occlusion-alarm (3.17 per 100 devices) and connectivity (2.26 per 100 devices) have crossed their thresholds and each warrants a CAPA review, with investigation stratified by site, firmware version, and device age [derived: rate-by-category] [src: commercial/internal-complaints@2026-07-27.2] [config: commercial.yml]. The same investigation arc for both categories makes it worth ruling out a common upstream factor — specifically, correlation with the upgrade campaign's rollback sites — before treating them as independent [derived: rate-by-category] [src: commercial/internal-complaints@2026-07-27.2] [config: commercial.yml]. The medium risks compound the picture: rising total volume from 74 to 101 window-over-window triggers a management-review escalation path if the pattern persists a second window [derived: window-trend] [config: commercial.yml]. The unvalidated threshold risk (R2) is the foundational qualifier for the entire analysis — replacing demo stand-ins with risk-file values is a prerequisite before any breach verdict carries audit weight [config: commercial.yml].
