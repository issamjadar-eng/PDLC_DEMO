# BQ-09 — Winning displaced accounts: the recall disruption window

_Demo sample data — not for clinical use._

**Verdict**: Method demo (fabricated CRM joined to REAL FDA recall dates): we win 53.7% of decided opportunities where the incumbent had an FRN recall posted within 180 days of close (n=54) vs 22.2% outside the window (n=9); the 0-3 months bucket wins at the highest rate (56.2%) while the interior buckets are flat (~50.0%) — not a smooth decay; the >12 months / no prior recall tail is far lower (14.3%, n=7 — small n) [derived: v-main] [src: commercial/internal-winloss@2026-07-27.2] [src: commercial/openfda-recalls-infusion@2026-07-22] [config: commercial.yml]

## Honesty box — what is real here and what is not

- REAL: FDA recall postings for product code FRN, 2021→present, from openFDA [src: commercial/openfda-recalls-infusion@2026-07-22].
- FABRICATED: every opportunity row (accounts, outcomes, dates) — demo-seeded CRM [src: commercial/internal-winloss@2026-07-27.2].
- Firm names on both sides are canonicalized through the versioned alias map
  [config: entity-aliases.yml]; unmatched firms keep their raw name.

## Win rate in vs out of the 180-day post-recall window [config: commercial.yml]

| Population | Decided opps | Won | Win rate |
|---|---|---|---|
| Incumbent recall posted ≤180d before close [derived: window-split] [src: commercial/internal-winloss@2026-07-27.2] | 54 | 29 | 53.7% |
| No recall in window [derived: window-split] [src: commercial/internal-winloss@2026-07-27.2] | 9 | 2 | 22.2% |

- Window sensitivity: at a 90-day window the split is 56.2% in (n=32) vs 41.9% out (n=31) — the size of the binary contrast at 180 days is partly an artifact of the window definition [derived: window-sensitivity] [config: commercial.yml] [src: commercial/internal-winloss@2026-07-27.2].
- Population: decided (won/lost) opportunities where the incumbent is a competitor; 8 no-decision opportunities excluded [src: commercial/internal-winloss@2026-07-27.2].
- Recall postings without an event_date_posted are excluded from the join: 0 record(s) [src: commercial/openfda-recalls-infusion@2026-07-22].

## How long does the window stay open? (win rate by months since the incumbent's most recent recall)

| Months since recall at close | Decided opps | Won | Win rate |
|---|---|---|---|
| 0-3 months [derived: decay-buckets] [src: commercial/internal-winloss@2026-07-27.2] | 32 | 18 | 56.2% |
| 3-6 months [derived: decay-buckets] [src: commercial/internal-winloss@2026-07-27.2] | 22 | 11 | 50.0% |
| 6-12 months [derived: decay-buckets] [src: commercial/internal-winloss@2026-07-27.2] | 2 (small n — indicative only) | 1 | 50.0% |
| >12 months / no prior recall [derived: decay-buckets] [src: commercial/internal-winloss@2026-07-27.2] | 7 (small n — indicative only) | 1 | 14.3% |

## Recall pressure by incumbent (canonicalized)

| Firm (canonical) | FRN recalls posted since 2021 |
|---|---|
| B. Braun [src: commercial/openfda-recalls-infusion@2026-07-22] [config: entity-aliases.yml] | 8 |
| BD (CareFusion) [src: commercial/openfda-recalls-infusion@2026-07-22] [config: entity-aliases.yml] | 16 |
| Baxter [src: commercial/openfda-recalls-infusion@2026-07-22] [config: entity-aliases.yml] | 27 |
| Fresenius Kabi [src: commercial/openfda-recalls-infusion@2026-07-22] [config: entity-aliases.yml] | 21 |
| ICU Medical [src: commercial/openfda-recalls-infusion@2026-07-22] [config: entity-aliases.yml] | 21 |
| Smiths Medical [src: commercial/openfda-recalls-infusion@2026-07-22] [config: entity-aliases.yml] | 18 |

## Narrative — Risks / Mitigations / Issues

### Risks (potential — mitigation identified)

- **R1 (high)** — The effect size is NOT market evidence: opportunity records are demo-fabricated and their seeded disruption windows were set independently of the real recall calendar — only the join method generalizes [src: commercial/internal-winloss@2026-07-27.2] [src: commercial/openfda-recalls-infusion@2026-07-22]
  - _Mitigation_: Re-run against the real CRM export before any strategy decision; keep the recall join and decay buckets as the reusable method [src: commercial/internal-winloss@2026-07-27.2] [src: commercial/openfda-recalls-infusion@2026-07-22]
- **R2 (medium)** — Large incumbents recall so often that 54 of 63 decided incumbent-held opportunities fall in-window — the out-of-window control group (n=9) is too small to carry weight on its own [derived: decay-buckets] [src: commercial/openfda-recalls-infusion@2026-07-22]
  - _Mitigation_: Read the months-since-recall decay buckets, not the binary in/out split; grow the control by extending history or narrowing the window definition [derived: decay-buckets] [src: commercial/openfda-recalls-infusion@2026-07-22]

### Watch

- **W1 (medium)** — Recall severity/scope carries no weighting (any FRN posting counts) and non-recall integration disruptions have no dataset — both widen what 'disruption' means vs what is measured [derived: window-split]

## Method & provenance

- In-window = at least one recall by the (canonical) incumbent posted in the 180 days ending at close_date [derived: window-split] [config: commercial.yml].
- Quarterly won/lost history, split in/out of window, charted zero-filled [derived: quarterly-outcomes] [src: commercial/internal-winloss@2026-07-27.2].
- No catalog expectations are declared for this question — none are invented.
- The verdict's window-duration language is derived from the computed bucket shape —
  a decay is claimed only when the bucket win rates actually decrease
  [derived: decay-buckets].
- Causality is not asserted: a recall near a close date does not prove the recall drove
  the outcome [derived: window-split].
