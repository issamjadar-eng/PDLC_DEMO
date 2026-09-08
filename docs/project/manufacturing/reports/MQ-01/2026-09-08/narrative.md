---
report_sha256: cfeaf53f35913d221acd85bcf8978a2d56367c173ac5bb3094012a3d8d49ad56
data_sha256: da6b6ad4b846bb4a47c2d3b30ef258bb9f7e257d06408bc442901a424da24353
generated_at: '2026-09-08T19:45:47+00:00'
author: AI assistant (grounded on report.md + data.json)
---
## Executive summary

Portfolio first-pass yield held at 96.6% across 10,970 units started in 2026-06..2026-08, and 0 of 5 product lines fell below the 95% floor [derived: v-main] [src: manufacturing/internal-production-lots@2026-09-08] [config: manufacturing.yml]. The headline number masks a real problem: PP3500 rev C at the test station yields 92.5% against 96.1% for the other rev(s) at the same station, and has been below the floor every month since 2026-04 [derived: pp3500-rev-by-station] [src: manufacturing/internal-production-lots@2026-09-08]. IP5000 at test has also run below the floor, at 94.9% since 2026-04 [derived: erosion-cells] [src: manufacturing/internal-production-lots@2026-09-08] [config: manufacturing.yml]. The decision this informs is whether PP3500 rev C is ready to ramp: as rev C's share of PP3500 lots grows, portfolio yield tracks it down [derived: fpy-trend] [src: manufacturing/internal-production-lots@2026-09-08]. The critical caveat is that the 95% floor has not been ratified in any manufacturing plan or pFMEA, so every "below floor" verdict rests on an unvalidated threshold [config: manufacturing.yml].

## Headline

The portfolio yielded 96.6% first-pass in 2026-06..2026-08, down 0.1 pts from the prior window, on 10,970 units started [derived: fpy-stat] [src: manufacturing/internal-production-lots@2026-09-08]. Scrap at 1.0% and rework at 2.4% of units started confirm that most first-pass failures are being recovered rather than permanently lost [derived: fpy-stat] [src: manufacturing/internal-production-lots@2026-09-08]. That rework burden carries a real cost and cycle-time penalty — and the aggregate stays stable only because the affected volume is concentrated at one station in a subset of lines.

## By product line

All 5 product lines cleared the 95% floor, with SP6000 leading at 97.4% and IP5000 trailing at 96.1% [src: manufacturing/internal-production-lots@2026-09-08]. PP3500 accounts for 7,136 of the 10,970 units started and yields 96.5% at the line level [src: manufacturing/internal-production-lots@2026-09-08]; that aggregate obscures the rev C test problem covered below. Scrap and rework are highest on IP5000 at scrap 1.1%, rework 2.7% — worth watching alongside the IP5000 test-station issue [src: manufacturing/internal-production-lots@2026-09-08].

## By station

The test station yields 94.4% portfolio-wide with a 4.3% rework rate — both the lowest FPY and the highest rework of any station [src: manufacturing/internal-production-lots@2026-09-08]. Pack, at the end of line, runs at 99.1%, confirming that final escapes are not the issue [src: manufacturing/internal-production-lots@2026-09-08]. Test is where failures accumulate and where investigation effort should concentrate.

## By site

Eastbrook yields 96.4% on 6,141 units started versus Westfield at 96.9% on 4,829 [derived: fpy-by-site] [src: manufacturing/internal-production-lots@2026-09-08]. The gap is narrow enough that product-mix differences between the two plants could explain it without any underlying process difference. That mix hypothesis needs a site-by-line cut before the gap is treated as a process signal [derived: fpy-by-site] [src: manufacturing/internal-production-lots@2026-09-08].

## Where yield is eroding — line × station cells below the floor

Two cells have run below the 95% floor every month since 2026-04: PP3500 at test at 93.5%, and IP5000 at test at 94.9% [derived: erosion-cells] [src: manufacturing/internal-production-lots@2026-09-08] [config: manufacturing.yml]. Both share the same station and the same onset month, raising the question of a common cause — a fixture change, test-program update, or component shift — affecting both lines simultaneously. Neither cell has a documented NCR and containment in this report, and that is the immediate priority.

## PP3500 by hardware revision and station

Rev C at test yields 92.5% against rev B's 96.1% at the same station — the widest revision gap across any station for PP3500 [derived: pp3500-rev-by-station] [src: manufacturing/internal-production-lots@2026-09-08]. At every other station the two revisions are close; final-assembly is the only station where rev C leads, at 96.5% versus rev B's 95.8% [src: manufacturing/internal-production-lots@2026-09-08]. The gap is isolated to test and is revision-specific, pointing to a fixture or test-program gap that targets rev C's hardware changes rather than a broad build-quality regression. As rev C's production share grows, this cell will pull portfolio FPY lower unless the root cause is resolved [derived: fpy-trend] [src: manufacturing/internal-production-lots@2026-09-08].

## Assumptions & expectations — plan vs actual

The single tracked expectation — every product line holds FPY at or above 95% over the trailing window — was met: 0 of 5 lines fell below the floor in 2026-06..2026-08 [derived: fpy-by-line] [config: manufacturing.yml]. The expectation itself is unvalidated: the 95% floor is a stand-in not grounded in any manufacturing plan or pFMEA [config: manufacturing.yml]. Until manufacturing engineering ratifies per-line yield targets, a "met" verdict here carries no audit weight.

## Narrative — Risks / Mitigations / Issues

Two medium-severity issues are open and need NCRs with documented containment: PP3500 at test at 93.5%, and IP5000 at test at 94.9%, both below the 95% floor every month since 2026-04 [derived: erosion-cells] [src: manufacturing/internal-production-lots@2026-09-08] [config: manufacturing.yml]. The highest-severity risk is PP3500 rev C at test: at 92.5%, this is a revision-specific failure mode, and as rev C's share of PP3500 production grows, the problem amplifies in portfolio FPY [derived: pp3500-rev-by-station] [derived: fpy-trend] [src: manufacturing/internal-production-lots@2026-09-08]. A second risk is the unratified floor — without validated per-line yield targets, the compliance picture is conditional, not confirmed [config: manufacturing.yml]. The watch item is Eastbrook at 96.4% versus Westfield at 96.9%: the gap is small, but it needs a mix-versus-process diagnosis before it is cleared [derived: fpy-by-site] [src: manufacturing/internal-production-lots@2026-09-08].
