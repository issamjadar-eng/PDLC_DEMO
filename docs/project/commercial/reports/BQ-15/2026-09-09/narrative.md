---
report_sha256: 67861cbb75577874dae92fb1e6893ef2a3a101c58c784af1159ab314f7e10b5c
data_sha256: 286d327f765bf98bdf307a66924753d09f9dce545457a60f8220ddd16792796e
generated_at: '2026-09-09T00:31:29+00:00'
author: AI assistant (grounded on report.md + data.json)
---
## Executive summary

Both headline differentiators — flow accuracy and battery life — remain ahead of every documented competitor value, and no refresh trigger fired. [derived: differentiator-margins] The next scheduled SOTA review is 2027-04-12, and no action is required before then. [derived: v-refresh] [config: commercial.yml] This finding informs the decision to hold the current competitive-positioning claims without update. The single biggest caveat: the 510(k) clearance snapshot's coverage ends 2026-07-24 [src: commercial/openfda-510k-infusion@2026-09-09], so a clearance decided after that date is invisible — a quiet signal here is not proof of a quiet market.

## Headline differentiators vs every documented competitor value

On flow accuracy, the PP3500's 0.35 ± pct spec sits ahead of all 4 documented competitor values, with the closest competitor (BD Alaris) at 2.3 [src: commercial/external-competitor-features@2026-07-27] — a margin of ~6.6x on our laboratory-basis spec [derived: differentiator-margins]. That multiple is basis-sensitive: on our volumetric-basis spec of 0.5, the margin narrows to ~4.6x [derived: differentiator-margins] [config: commercial.yml], but superiority holds on either basis. Five competitor products carry no documented accuracy value, so the comparison is bounded to what is on record — undocumented is not beaten [src: commercial/external-competitor-features@2026-07-27].

On battery, the PP3500's 150-hour rating [config: commercial.yml] exceeds all 5 documented competitor values; the best-documented competitor (Smiths Medical CADD Legacy) tops out at 72 hours [src: commercial/external-competitor-features@2026-07-27], yielding a margin of ~2.1x [derived: differentiator-margins]. Four competitor products carry no documented battery value, and the same "undocumented is not beaten" limit applies [src: commercial/external-competitor-features@2026-07-27].

## Clearance activity since the SOTA anchor (the currency signal)

1 FRN clearance was recorded with a decision date after the SOTA anchor date of 2026-04-12, within a snapshot whose coverage ends 2026-07-24 [derived: since-doc-count] [src: commercial/openfda-510k-infusion@2026-09-09] [config: commercial.yml]. That single clearance does not constitute a threat signal, but context matters: 4 clearances were recorded in the trailing 12-month window 2025-07-24 → 2026-07-24 [derived: trailing-context] [src: commercial/openfda-510k-infusion@2026-09-09], confirming the segment is active. The coverage gap between the snapshot's newest decision date and today means the true post-anchor count may be higher — the 90-day dataset refresh cadence is the appropriate response, not a manual review now.

## Refresh verdict (deterministic rule, plan-committed)

No refresh trigger fired: both differentiator margins are positive on every measured basis, 0 predictive-monitoring rows read `yes` [src: commercial/external-competitor-features@2026-07-27], and the SOTA doc is 150 days old against a 12-month cadence [derived: v-refresh] [config: commercial.yml]. The next scheduled review date is 2027-04-12 [derived: v-refresh] [config: commercial.yml]. Two limits bound this verdict: the cadence is a config stand-in rather than a documented QMS or EU MDR obligation [config: commercial.yml], and the anchor reflects the doc's adoption date — if the underlying analysis was authored earlier, the effective currency window is shorter than the calendar math suggests [config: commercial.yml].

## Narrative — Risks / Mitigations / Issues

The dominant risk is lag: the 510(k) dataset's coverage ends 2026-07-24, well before the snapshot acquisition date of 2026-09-09 [src: commercial/openfda-510k-infusion@2026-09-09] [derived: since-doc-count], so a clearance that already exists may simply not appear here. The prescribed mitigation is to refresh the dataset on its 90-day cadence and treat any quiet window as unproven rather than confirmed. Two watch items reinforce the same boundary: the competitive accuracy and battery comparisons rest on 4 and 5 documented cells respectively [src: commercial/external-competitor-features@2026-07-27] [derived: differentiator-margins], and the clearance scope is limited to product code FRN — a monitoring SaMD clearance that could affect the SOTA picture would be invisible [src: commercial/openfda-510k-infusion@2026-09-09]. Neither watch item triggers a refresh now, but both define the conditions under which the verdict would change.
