# BQ-08 — What we win and lose on (trailing 365 days)

_Demo sample data — not for clinical use._

**Verdict**: Trailing-365d win rate is 58.7% of decided opportunities (37 won / 26 lost; 18 no-decision excluded) vs the 50% stand-in target; dollar-weighted we win 61.4% of decided CRM value ($30,389,000 won vs $19,071,000 lost — we win bigger deals than we lose); 8 of 26 losses (30.8%) have the predictive-monitoring gap primary or cited — $4,792,000 in CRM value [derived: v-main] [src: commercial/internal-winloss@2026-09-14] [config: commercial.yml]

## Decided outcomes in the window (2025-07-20 → 2026-07-20)

_Window: trailing 365 days anchored at the newest close_date in the pinned snapshot; decided = won + lost; no-decision reported separately, per plans/BQ-08.md [config: commercial.yml]._

- Win rate: 58.7% (37 won / 26 lost) [derived: win-rate] [src: commercial/internal-winloss@2026-09-14]
- Dollar-weighted: we win 61.4% of decided CRM value ($30,389,000 won vs $19,071,000 lost — we win bigger deals than we lose) [derived: value-win-rate] [src: commercial/internal-winloss@2026-09-14]
- No-decision outcomes excluded from the denominator: 18 [src: commercial/internal-winloss@2026-09-14]; counted as losses the win rate would be 45.7% [derived: win-rate] [src: commercial/internal-winloss@2026-09-14]

## Loss reasons (primary, in-window)

| Primary reason | Losses | % of losses |
|---|---|---|
| price [src: commercial/internal-winloss@2026-09-14] | 11 | 42.3% |
| predictive-monitoring-gap [src: commercial/internal-winloss@2026-09-14] | 5 | 19.2% |
| clinical-evidence [src: commercial/internal-winloss@2026-09-14] | 3 | 11.5% |
| contract-timing [src: commercial/internal-winloss@2026-09-14] | 3 | 11.5% |
| incumbent-relationship [src: commercial/internal-winloss@2026-09-14] | 3 | 11.5% |
| features [src: commercial/internal-winloss@2026-09-14] | 1 | 3.8% |

## The predictive-monitoring gap in losses

- Primary OR cited: 8 of 26 in-window losses (30.8%) [derived: pm-gap-losses] [src: commercial/internal-winloss@2026-09-14]
- Primary reason only: 5 losses [derived: pm-gap-losses] [src: commercial/internal-winloss@2026-09-14]
- CRM opportunity value of those losses: $4,792,000 (recorded value, not win-probability-weighted) [derived: pm-gap-losses] [src: commercial/internal-winloss@2026-09-14]

## What we win on (primary reason of in-window wins)

| Primary reason | Wins |
|---|---|
| contract-timing [src: commercial/internal-winloss@2026-09-14] | 12 |
| features [src: commercial/internal-winloss@2026-09-14] | 10 |
| price [src: commercial/internal-winloss@2026-09-14] | 8 |
| service [src: commercial/internal-winloss@2026-09-14] | 5 |
| clinical-evidence [src: commercial/internal-winloss@2026-09-14] | 2 |

## Assumptions & expectations — plan vs actual

_`unvalidated` means the expectation itself is a stand-in that has not been grounded
in a plan of record or the risk file — challenge the assumption, not just the actual._

| ID | Expectation | Expected | Actual | Verdict | Basis |
|---|---|---|---|---|---|
| E-08.1 | Competitive win rate holds at or above half of decided opportunities [derived: win-rate] [src: commercial/internal-winloss@2026-09-14] [config: commercial.yml] | >= 50% of won+lost | 58.7% of decided (37W/26L, window 2025-07-20 → 2026-07-20); sensitivity: 45.7% if the 18 no-decisions count as losses — the verdict is denominator-sensitive, not just sample-sensitive | met (unvalidated) | sales-plan stand-in; no documented target |

## Narrative — Risks / Mitigations / Issues

### Risks (potential — mitigation identified)

- **R1 (high)** — Predictive-monitoring gap touches 30.8% of in-window losses (8 deals, $4,792,000 CRM value; primary reason in 5 of them) — the largest addressable feature-driven loss pool [derived: pm-gap-losses] [src: commercial/internal-winloss@2026-09-14]
  - _Mitigation_: Feed this value into the predictive-monitoring investment case (Y3 roadmap bet); equip sales with the roadmap position for deals where the gap is cited but not primary [derived: pm-gap-losses] [src: commercial/internal-winloss@2026-09-14]
- **R2 (medium)** — Loss attribution is the CRM's single primary_reason per opportunity — a recorded citation is not proof the gap decided the deal [src: commercial/internal-winloss@2026-09-14]
  - _Mitigation_: Treat reason mix as directional; validate the big-ticket PM-gap losses with deal debriefs before funding decisions ride on them [src: commercial/internal-winloss@2026-09-14]

### Watch

- **W1 (medium)** — Dollar-weighted win rate is 61.4% of decided CRM value ($30,389,000 won vs $19,071,000 lost) vs 58.7% by count — we win bigger deals than we lose; read the count-based headline next to the value-based one [derived: value-win-rate] [src: commercial/internal-winloss@2026-09-14]
- **W2 (medium)** — Top loss reason in the window is price (11 of 26 losses) — competitive-selling coaching target [derived: loss-reasons] [src: commercial/internal-winloss@2026-09-14]

## Method & provenance

- All counts measured from [src: commercial/internal-winloss@2026-09-14] (demo-fabricated CRM log; real competitor names
  inside fabricated records).
- Monthly won/lost/PM-gap-loss history charted across the full snapshot span, zero-filled [derived: monthly-outcomes] [src: commercial/internal-winloss@2026-09-14].
- The win-rate target is a stand-in expectation, not a documented sales-plan number
  [config: commercial.yml].
