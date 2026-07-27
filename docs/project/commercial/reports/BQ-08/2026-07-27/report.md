# BQ-08 — What we win and lose on (trailing 365 days)

_Demo sample data — not for clinical use._

**Verdict**: Trailing-365d win rate is 50.7% of decided opportunities (37 won / 36 lost; 10 no-decision excluded) vs the 50% stand-in target; dollar-weighted we win 42.9% of decided CRM value ($23,682,000 won vs $31,550,000 lost — we lose bigger deals than we win); 11 of 36 losses (30.6%) have the predictive-monitoring gap primary or cited — $9,961,000 in CRM value [derived: v-main] [src: commercial/internal-winloss@2026-07-27.2] [config: commercial.yml]

## Decided outcomes in the window (2025-07-25 → 2026-07-25)

_Window: trailing 365 days anchored at the newest close_date in the pinned snapshot; decided = won + lost; no-decision reported separately, per plans/BQ-08.md [config: commercial.yml]._

- Win rate: 50.7% (37 won / 36 lost) [derived: win-rate] [src: commercial/internal-winloss@2026-07-27.2]
- Dollar-weighted: we win 42.9% of decided CRM value ($23,682,000 won vs $31,550,000 lost — we lose bigger deals than we win) [derived: value-win-rate] [src: commercial/internal-winloss@2026-07-27.2]
- No-decision outcomes excluded from the denominator: 10 [src: commercial/internal-winloss@2026-07-27.2]; counted as losses the win rate would be 44.6% [derived: win-rate] [src: commercial/internal-winloss@2026-07-27.2]

## Loss reasons (primary, in-window)

| Primary reason | Losses | % of losses |
|---|---|---|
| price [src: commercial/internal-winloss@2026-07-27.2] | 12 | 33.3% |
| predictive-monitoring-gap [src: commercial/internal-winloss@2026-07-27.2] | 6 | 16.7% |
| features [src: commercial/internal-winloss@2026-07-27.2] | 5 | 13.9% |
| clinical-evidence [src: commercial/internal-winloss@2026-07-27.2] | 3 | 8.3% |
| contract-timing [src: commercial/internal-winloss@2026-07-27.2] | 3 | 8.3% |
| incumbent-relationship [src: commercial/internal-winloss@2026-07-27.2] | 3 | 8.3% |
| other [src: commercial/internal-winloss@2026-07-27.2] | 3 | 8.3% |
| service [src: commercial/internal-winloss@2026-07-27.2] | 1 | 2.8% |

## The predictive-monitoring gap in losses

- Primary OR cited: 11 of 36 in-window losses (30.6%) [derived: pm-gap-losses] [src: commercial/internal-winloss@2026-07-27.2]
- Primary reason only: 6 losses [derived: pm-gap-losses] [src: commercial/internal-winloss@2026-07-27.2]
- CRM opportunity value of those losses: $9,961,000 (recorded value, not win-probability-weighted) [derived: pm-gap-losses] [src: commercial/internal-winloss@2026-07-27.2]

## What we win on (primary reason of in-window wins)

| Primary reason | Wins |
|---|---|
| contract-timing [src: commercial/internal-winloss@2026-07-27.2] | 15 |
| features [src: commercial/internal-winloss@2026-07-27.2] | 7 |
| service [src: commercial/internal-winloss@2026-07-27.2] | 6 |
| clinical-evidence [src: commercial/internal-winloss@2026-07-27.2] | 5 |
| other [src: commercial/internal-winloss@2026-07-27.2] | 2 |
| price [src: commercial/internal-winloss@2026-07-27.2] | 2 |

## Assumptions & expectations — plan vs actual

_`unvalidated` means the expectation itself is a stand-in that has not been grounded
in a plan of record or the risk file — challenge the assumption, not just the actual._

| ID | Expectation | Expected | Actual | Verdict | Basis |
|---|---|---|---|---|---|
| E-08.1 | Competitive win rate holds at or above half of decided opportunities [derived: win-rate] [src: commercial/internal-winloss@2026-07-27.2] [config: commercial.yml] | >= 50% of won+lost | 50.7% of decided (37W/36L, window 2025-07-25 → 2026-07-25); sensitivity: 44.6% if the 10 no-decisions count as losses — the verdict is denominator-sensitive, not just sample-sensitive | met (unvalidated) | sales-plan stand-in; no documented target |

## Narrative — Risks / Mitigations / Issues

### Risks (potential — mitigation identified)

- **R1 (high)** — Predictive-monitoring gap touches 30.6% of in-window losses (11 deals, $9,961,000 CRM value; primary reason in 6 of them) — the largest addressable feature-driven loss pool [derived: pm-gap-losses] [src: commercial/internal-winloss@2026-07-27.2]
  - _Mitigation_: Feed this value into the predictive-monitoring investment case (Y3 roadmap bet); equip sales with the roadmap position for deals where the gap is cited but not primary [derived: pm-gap-losses] [src: commercial/internal-winloss@2026-07-27.2]
- **R2 (medium)** — Loss attribution is the CRM's single primary_reason per opportunity — a recorded citation is not proof the gap decided the deal [src: commercial/internal-winloss@2026-07-27.2]
  - _Mitigation_: Treat reason mix as directional; validate the big-ticket PM-gap losses with deal debriefs before funding decisions ride on them [src: commercial/internal-winloss@2026-07-27.2]

### Watch

- **W1 (medium)** — Win rate 50.7% clears the 50% target by under two points — a handful of deals swings the verdict, and so does the denominator choice: with the 10 no-decisions counted as losses the rate is 44.6%, below the target [derived: win-rate] [config: commercial.yml]
- **W2 (medium)** — Dollar-weighted win rate is 42.9% of decided CRM value ($23,682,000 won vs $31,550,000 lost) vs 50.7% by count — we lose bigger deals than we win; read the count-based headline next to the value-based one [derived: value-win-rate] [src: commercial/internal-winloss@2026-07-27.2]
- **W3 (medium)** — Top loss reason in the window is price (12 of 36 losses) — competitive-selling coaching target [derived: loss-reasons] [src: commercial/internal-winloss@2026-07-27.2]

## Method & provenance

- All counts measured from [src: commercial/internal-winloss@2026-07-27.2] (demo-fabricated CRM log; real competitor names
  inside fabricated records).
- Monthly won/lost/PM-gap-loss history charted across the full snapshot span, zero-filled [derived: monthly-outcomes] [src: commercial/internal-winloss@2026-07-27.2].
- The win-rate target is a stand-in expectation, not a documented sales-plan number
  [config: commercial.yml].
