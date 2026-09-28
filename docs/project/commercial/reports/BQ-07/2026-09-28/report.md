# BQ-07 — US PCA/smart-pump segment share (a range, honestly)

_Demo sample data — not for clinical use._

**Verdict**: US (NA-proxy) PCA/LVP smart-pump share is a RANGE, not a number: ~0.029%–0.047% of installed base and ~0.55%–1.1% of annual segment dollars (A-003 denominator, LOW confidence); our installed base grew ~16.0%/yr vs the assumed market ~7.3%/yr — directionally gaining, from a tiny base (mismatched bases: ours is UNIT growth of our NA in-segment book; A-003's rate is the DOLLAR CAGR of the total US infusion-pump market — directional comparison only) [derived: v-main] [src: commercial/internal-sales-accounts@2026-09-28] [assume: A-003]

## Share as a range, by fiscal year

_US proxied by the NA region; in-segment = PP3500 + PP3000 + IP5000 [src: commercial/internal-sales-accounts@2026-09-28] (PCA +
LVP smart pumps, matching the assumption's scope); syringe and cloud-suite lines excluded —
committed definitions in plans/BQ-07.md. Denominators held constant across FYs:
an installed base of 1.1M–1.8M units and a segment market of $1.5B–$3.0B/yr [assume: A-003]._

| FY | Our units (installed) | Unit share of installed base | Our revenue (direct book) | Revenue share of annual segment $ |
|---|---|---|---|---|
| FY2024 [src: commercial/internal-sales-accounts@2026-09-28] [assume: A-003] | 418 | 0.023%–0.038% | $10,520,092 | 0.35%–0.7% |
| FY2025 [src: commercial/internal-sales-accounts@2026-09-28] [assume: A-003] | 485 | 0.027%–0.044% | $13,492,738 | 0.45%–0.9% |
| FY2026H1 [src: commercial/internal-sales-accounts@2026-09-28] [assume: A-003] | 522 | 0.029%–0.047% | $8,232,109 (half-year actual; dollar share uses ×2) | 0.55%–1.1% |

## Taking share, or growing with the market?

- Our NA in-segment installed base grew 418 → 522 units (FY2024 → FY2026H1), ~16.0%/yr annualized [derived: growth-rate] [src: commercial/internal-sales-accounts@2026-09-28].
- The market grows ~7.3%/yr under the assumed model [assume: A-003] — that figure is the DOLLAR CAGR of the TOTAL US infusion-pump market, not a unit-growth rate and not scoped to the PCA/LVP segment, while ours is unit growth of our own NA in-segment base; the growth comparison is therefore directional only [derived: growth-rate]. At ~74 units added/yr against an assumed annual demand of 130k–230k units, share movement vs BD/Baxter is not observable in any data we hold; the defensible claim is a growth-rate differential from a tiny base [derived: growth-rate] [assume: A-003].

## Why this is a range, not a number

- No public per-segment unit census exists; vendors do not disclose US installed base by
  segment. The denominator is the assumption record — its confidence is LOW and its own
  method note calls the fleet-ratio term the widest-error input [assume: A-003].
- Unit share (stock: share of installed base) and revenue share (flow: share of annual
  segment dollars) answer different questions and legitimately differ — a growing entrant's
  flow share leads its stock share. Both are shown; neither is a point figure
  [derived: share-range] [assume: A-003].
- Competitor unit split (BD vs Baxter vs ICU installed units) is NOT public — published
  as an unavailable series, never guessed [derived: competitor-unit-split].

## Narrative — Risks / Mitigations / Issues

### Risks (potential — mitigation identified)

- **R1 (high)** — The entire share figure rests on A-003 (LOW confidence, triangulated from public analyst-report summaries) — the denominator could be off by a large factor, and the unit-share and dollar-share bases already tell different stories (stock share vs flow share) [assume: A-003] [derived: share-range]
  - _Mitigation_: Treat share as order-of-magnitude only; refresh A-003 annually or on any new market report; consider purchasing analyst unit data to retire the assumption [assume: A-003] [derived: share-range]
- **R2 (medium)** — US share is proxied by the NA region and the denominator is held constant across fiscal years (market growth not modeled per-year) — both stated simplifications of the committed plan [derived: share-range] [assume: A-003]
  - _Mitigation_: Acceptable at order-of-magnitude precision; revisit if the sales dataset gains a country field or A-003 gains dated vintages [derived: share-range] [assume: A-003]

### Watch

- **W1 (medium)** — Growth-rate differential (ours ~16.0%/yr vs market ~7.3%/yr) is the only taking-share evidence available at this share magnitude — watch it each quarter [derived: growth-rate] [assume: A-003]

## Method & provenance

- Numerators (units, revenue) measured from [src: commercial/internal-sales-accounts@2026-09-28] (demo-fabricated direct book:
  hardware + subscription; consumables/service flow through distributors and are absent).
- Denominators and market growth from the assumption record [assume: A-003]; FY2026H1
  revenue annualized ×2 for the dollar-share comparison only [derived: share-range].
