---
report_sha256: ffe1169077fb8b52279e0e15f291ebfbbd0ef5585e10aabaf10cf570988dfad4
data_sha256: aac41a56f497ea187dfa5fbc8daba514ba33fe23038883e1f7e8dd6c6ad86bf8
generated_at: '2026-09-09T00:34:31+00:00'
author: AI assistant (grounded on report.md + data.json)
---
## Executive summary

When an incumbent's PCA pump has an FDA recall posting within 180 days of deal close, we win 67.3% of decided opportunities (n=55); without that signal, the win rate drops to 14.3% (n=7). [derived: v-main] [src: commercial/internal-winloss@2026-09-08] [src: commercial/openfda-recalls-infusion@2026-09-09] [config: commercial.yml] The recall calendar among the six tracked incumbents is dense — Baxter alone carries 29 FRN postings since 2021. [src: commercial/openfda-recalls-infusion@2026-09-09] [config: entity-aliases.yml] This analysis validates a recall-join targeting method that field teams can apply to real CRM data to flag accounts currently in a disruption window. The critical caveat: every opportunity record is demo-fabricated, so the 67.3% win rate is not market evidence and should not drive strategy until the method is re-run against an actual CRM export. [src: commercial/internal-winloss@2026-09-08]

## Honesty box — what is real here and what is not

The FDA recall postings for product code FRN are drawn from openFDA and are real. [src: commercial/openfda-recalls-infusion@2026-09-09] Every opportunity row — accounts, outcomes, and close dates — is demo-fabricated. [src: commercial/internal-winloss@2026-09-08] Because the seeded disruption windows were set independently of the real recall calendar, the win rates in this report reflect the method's mechanics, not the market. The recall join structure and decay buckets are what carry forward to a real analysis.

## Win rate in vs out of the 180-day post-recall window (demo of method, not market evidence) [config: commercial.yml]

Accounts where the incumbent had a recall posting in the 180 days before close show a 67.3% win rate across 55 decided opportunities; accounts outside that window show 14.3% across just 7. [derived: window-split] [src: commercial/internal-winloss@2026-09-08] The contrast is striking, but with only 7 out-of-window observations the control group is too thin to stand on its own. [derived: window-split] [src: commercial/openfda-recalls-infusion@2026-09-09] At a 90-day window the gap narrows to 65.8% in (n=38) vs 54.2% out (n=24), showing that the magnitude of the binary contrast depends on where the cutoff is drawn. [derived: window-sensitivity] [config: commercial.yml] [src: commercial/internal-winloss@2026-09-08] The months-since-recall breakdown is the more stable read.

## How long does the window stay open? (win rate by months since the incumbent's most recent recall)

The 0–3 month bucket shows a 65.8% win rate (n=38) and the 3–6 month bucket shows 70.6% (n=17) — there is no decay across the first six months, and if anything a slight increase. [derived: decay-buckets] [src: commercial/internal-winloss@2026-09-08] Beyond that, the 6–12 month bucket lands at 0.0% on only 5 opportunities, and the >12 months / no prior recall tail is 50.0% on only 2 — both too small to interpret. [derived: decay-buckets] [src: commercial/internal-winloss@2026-09-08] The data do not support a clean decay narrative; what they show is that the strongest performance is concentrated in the first six months, and the sample outside that range is too thin to say more.

## Recall pressure by incumbent (canonicalized)

Baxter leads with 29 FRN recall postings since 2021, followed by Fresenius Kabi and ICU Medical at 21 each, Smiths Medical at 18, BD (CareFusion) at 16, and B. Braun at 8. [src: commercial/openfda-recalls-infusion@2026-09-09] [config: entity-aliases.yml] This volume of recall activity means nearly every incumbent-held account is within reach of a recent recall posting — which is why 55 of 62 decided incumbent-held opportunities fell in-window even in this demo dataset. [derived: decay-buckets] [src: commercial/openfda-recalls-infusion@2026-09-09] Baxter's frequency makes it the highest-priority target for recall-triggered outreach once real CRM data are in place.

## Narrative — Risks / Mitigations / Issues

The dominant risk is that the win rates here are not market evidence: opportunity records are demo-fabricated, so the 67.3% figure cannot inform strategy until the method is re-run on actual CRM data. [src: commercial/internal-winloss@2026-09-08] [src: commercial/openfda-recalls-infusion@2026-09-09] A structural weakness compounds this: the out-of-window control group at n=7 is too small to carry weight on its own, and the months-since-recall buckets beyond six months hold only 5 and 2 observations respectively. [derived: decay-buckets] [src: commercial/openfda-recalls-infusion@2026-09-09] One gap worth watching: recall severity and scope carry no weighting — any FRN posting counts equally — and non-recall integration disruptions are not captured, so the disruption measure is narrower than the concept it represents. [derived: window-split]
