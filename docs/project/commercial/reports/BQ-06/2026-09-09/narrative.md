---
report_sha256: 0355da735acbfe9f5d52c958da48042a1c3038fe51dd9d4875fd96ddfe79e009
data_sha256: 74a3d539e1e2f1978b31564d1e7bcad6e10445f6bd52cbe8176745a0ebff41ca
generated_at: '2026-09-09T00:32:41+00:00'
author: AI assistant (grounded on report.md + data.json)
---
## Executive summary

Across 30 infusion-pump 510(k) clearances since 2021, competitors face a median FDA review interval of 214.0 days from receipt to decision [derived: cycle-by-applicant] [src: commercial/openfda-510k-infusion@2026-09-09]. Baxter Healthcare Corporation, the highest-volume filer with 9 clearances, achieves a median of just 74 days [src: commercial/openfda-510k-infusion@2026-09-09] — a pace that suggests meaningful pre-submission alignment with FDA. This benchmark informs submission timing: a team planning around the field median should budget roughly seven months of FDA review, while a team aspiring to Baxter-paced clearance must understand what drives that gap. The single biggest caveat is that our own received→decision history cannot be drawn from public data — the internal regulatory log has not yet been loaded as a corpus dataset — so no like-for-like comparison of our performance against the field exists today.

## Review interval by frequent filer (public FDA dates)

The spread across frequent filers is wide: Baxter Healthcare Corporation clears in a median 74 days [src: commercial/openfda-510k-infusion@2026-09-09] while Carefusion 303, Inc. and Fresenius Kabi AG sit at 474.5 and 413.0 days respectively [src: commercial/openfda-510k-infusion@2026-09-09]. That six-fold range is too large to be explained by device complexity alone; it more likely reflects differences in submission quality, pre-submission engagement with FDA, and deficiency response speed. Baxter's 9-clearance sample is the most statistically stable in this dataset [src: commercial/openfda-510k-infusion@2026-09-09], making their 74-day median the most reliable external benchmark for what is achievable. A team benchmarking submission readiness should ask not only "how long will FDA take?" but "what does our package quality look like relative to Baxter's?"

## Our own history (stated gap)

No internal review-interval data is available for comparison because our program's K-numbers are demo-fabricated and cannot be read from public FDA records [derived: cycle-by-year] [src: commercial/openfda-510k-infusion@2026-09-09]. The metric also measures only FDA review time — received to decision — not the full develop-to-market cycle, and the internal concept register needed to compute pipeline conversion is a second stated gap. The year-over-year trend in competitor review times does show a meaningful drop from 446.0 days in 2021 to 103 days in 2024 before recovering to 228.5 days in 2026 [derived: cycle-by-year] [src: commercial/openfda-510k-infusion@2026-09-09], suggesting the field is not static. The priority action to close this gap is ingesting the internal regulatory log as a corpus dataset so our own performance can be placed on the same axis.
