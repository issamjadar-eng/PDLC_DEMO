---
report_sha256: 88498c86e8d22b5816bf3fddabd5dfdfa2ecc9e8fa40c1a71f4e89762cc78d26
data_sha256: 821685194494a3980e3c3fb5fdc4170603adca6a5d57b7142724a71474d765b5
generated_at: '2026-09-08T19:46:42+00:00'
author: AI assistant (grounded on report.md + data.json)
---
## Executive summary

Across 29 infusion-pump 510(k) clearances since 2021, competitors face a median review interval of 213 days from receipt to decision [derived: cycle-by-applicant] [src: commercial/openfda-510k-infusion@2026-07-22]. Baxter Healthcare Corporation, the dominant frequent filer with 9 clearances in the period, achieves a median of 74 days — nearly three times faster than the field [src: commercial/openfda-510k-infusion@2026-07-22]. This gap matters for launch planning: a team targeting Baxter-level speed needs to understand what drives that difference, while a team planning conservatively should budget closer to the 213-day field median [derived: cycle-by-applicant] [src: commercial/openfda-510k-infusion@2026-07-22]. The single biggest caveat is that our own received→decision history is not yet available as a corpus dataset, so no internal benchmark exists to compare against the competitor baseline [derived: v-main] [src: commercial/openfda-510k-infusion@2026-07-22].

## Review interval by frequent filer (public FDA dates)

Baxter Healthcare Corporation's 74-day median across 9 clearances is the clear outlier — it sits well below both the 139-day second-fastest filer (Zevex, Inc., 2 clearances) and the 213-day field median [src: commercial/openfda-510k-infusion@2026-07-22] [derived: cycle-by-applicant]. The slower end of the table is striking: Carefusion 303, Inc. and Fresenius Kabi AG each show medians above 400 days on only 2 clearances apiece [src: commercial/openfda-510k-infusion@2026-07-22], which suggests either submission complexity or back-and-forth with FDA, though the public data alone cannot distinguish those causes. The wide spread — 74 days to 474.5 days [src: commercial/openfda-510k-infusion@2026-07-22] — tells leadership that applicant-level choices (submission quality, predicate strength, device complexity) matter as much as the FDA calendar in determining actual cycle time. Reading changes if the Baxter volume (9 clearances) turns out to reflect a specific product class rather than general submission excellence.

## Our own history (stated gap)

The left side of the benchmark comparison — our own received→decision history — has no data because the program's K-numbers are fabricated for this demonstration and the internal regulatory log is not yet a corpus dataset [derived: v-main] [src: commercial/openfda-510k-infusion@2026-07-22]. Until that log is loaded, the team cannot place itself relative to the 213-day field median or the 74-day Baxter benchmark [derived: cycle-by-applicant] [src: commercial/openfda-510k-infusion@2026-07-22]. A second scope limit also applies: received→decision measures FDA review time only, not the full develop-to-market interval, so concept-pipeline conversion speed requires the internal concept register — also a stated gap. This gap closes only by ingesting the actual regulatory submission log as a corpus dataset; no workaround from public FDA data is available for a program with non-public K-numbers.
