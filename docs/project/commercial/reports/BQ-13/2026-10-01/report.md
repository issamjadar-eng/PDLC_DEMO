# BQ-13 — Predictive-monitoring runway vs our F6 slot

**Verdict**: Nobody in the competitive matrix documents predictive monitoring today, but the runway is assumption-thin: a SaMD-only entrant starting at the data anchor (2026-07-24) could clear 2028-01-24 to 2028-07-24 — about 1 months after our F6 2028-H2 launch anchor; an incumbent acquisition inherits the same clock; 0 ai/predictive-flagged clearance(s) in the trailing-12-month watch. The hardware-scenario reassurance holds: its fast edge clears the favorable launch anchor by 207 days — and the H2 anchor refinement is a catalog config choice, not a strategy-doc commitment [derived: v-main] [assume: A-005] [src: commercial/openfda-510k-infusion@2026-09-28] [src: commercial/external-competitor-features@2026-09-28] [config: commercial.yml]

## Premise check — does anyone document shipping predictive monitoring?

| Vendor / product | predictive_monitoring | Verified |
|---|---|---|
| GlobalLogic PainEase PCA Advanced (PP3500) [src: commercial/external-competitor-features@2026-09-28] | no (complete absence of predictive monitoring across portfolio) | yes |
| BD Alaris [src: commercial/external-competitor-features@2026-09-28] | no (reactive alarms only) | yes |
| Baxter Spectrum IQ [src: commercial/external-competitor-features@2026-09-28] | no (reactive alarms only) | yes |
| ICU Medical Plum 360 [src: commercial/external-competitor-features@2026-09-28] | no (named reactive-alarm incumbent) | yes |
| B.Braun Infusomat Space [src: commercial/external-competitor-features@2026-09-28] | no (named reactive-alarm incumbent) | yes |

- Every documented row reads `no` — 5 products checked, 0 shipping [derived: predictive-shipping-check] [src: commercial/external-competitor-features@2026-09-28]. Products absent from the matrix are absent, not cleared — the matrix cannot prove entrant absence.

## Runway model — A-005 lead-time bands from the data anchor

_Data anchor = newest decision date in the pinned snapshot (2026-07-24); our launch anchor = first day of 2028-H2 (2028-07-01, the favorable-to-us reading; the unfavorable end-of-period reading is 2028-12-31) [src: commercial/openfda-510k-infusion@2026-09-28] [config: commercial.yml]. Anchor provenance caveat: the H2 half-year refinement exists ONLY in the question catalog [config: commercial.yml] — the strategy doc (D-COMM-1.4) commits F6 to bare 'Y3 (2028)' with no half-year granularity, so both readings below are config-sensitive, not strategy-committed._

| Entry scenario | Projected clearance window | Vs our launch anchor |
|---|---|---|
| SaMD-only entrant [assume: A-005] [derived: entry-scenarios] | 2028-01-24 → 2028-07-24 | straddles our launch anchor |
| Hardware-integrated / clinical-evidence program [assume: A-005] [derived: entry-scenarios] | 2029-01-24 → 2030-07-24 | clears after our launch anchor |
| Incumbent acquires AI entrant (SaMD clock on incumbent channel) [assume: A-005] [derived: entry-scenarios] | 2028-01-24 → 2028-07-24 | straddles our launch anchor |

- The SLOW end of the SaMD band (2028-07-24) lands about 1 months after our launch anchor — the worst-case-for-us SaMD entrant no longer beats our date; only the FAST end (2028-01-24) does [derived: runway-margin] [assume: A-005].
- The hardware-integrated / clinical-evidence band (2029-01-24 → 2030-07-24) clears after our launch anchor — anchor-reading-dependent: the fast edge clears the favorable anchor (2028-07-01) by 207 days [derived: hardware-edge-margin] [assume: A-005] [config: commercial.yml]. 'A hardware incumbent building in-house is not the fast threat' holds only under the favorable anchor reading; an acquisition converting an incumbent to the SaMD clock remains the fast threat under every reading [derived: entry-scenarios].

## Recent-clearance watch (trailing 12 months ending at the data anchor)

_Window 2025-07-24 → 2026-07-24; keyword flags on public device names are a triage aid, never a capability judgment [config: commercial.yml] [src: commercial/openfda-510k-infusion@2026-09-28]._

| K-number | Applicant (canonical) | Device | Decision | Flags |
|---|---|---|---|---|
| K251636 [src: commercial/openfda-510k-infusion@2026-09-28] [config: entity-aliases.yml] | Baxter | Spectrum IQ Infusion System with Dose IQ Safety Softwar | 2025-07-28 | software |
| K251640 [src: commercial/openfda-510k-infusion@2026-09-28] [config: entity-aliases.yml] | Baxter | SIGMA Spectrum Infusion Pump with Master Drug Library | 2025-07-28 | software |

- 2 of 4 window clearances carry software/AI-adjacent flags; 0 carry the ai-predictive flag [derived: watch-flagged] [src: commercial/openfda-510k-infusion@2026-09-28].

## Narrative — Risks / Mitigations / Issues

### Risks (potential — mitigation identified)

- **R1 (high)** — The F6 runway verdict is assumption-bounded: the entire lead-time model is A-005 (medium confidence), and the entrant clock is modeled from the data anchor (2026-07-24) — a program already underway is ahead of every figure here [assume: A-005] [src: commercial/openfda-510k-infusion@2026-09-28]
  - _Mitigation_: Treat A-005's refresh triggers as standing: recompute on every 510(k) snapshot refresh and on any predictive-monitoring announcement; widen the corpus beyond product code FRN before relying on entrant absence [assume: A-005] [src: commercial/openfda-510k-infusion@2026-09-28]
- **R2 (medium)** — Acquisition scenario: an incumbent buying an AI entrant applies the 18-24-month SaMD clock to an established hospital channel — the fastest modeled path to closing our gap, and it is an assumption-class scenario, not an observed signal [assume: A-005] [derived: entry-scenarios] [config: commercial.yml]
  - _Mitigation_: Track M&A signals alongside the clearance watch; a deal announcement collapses the runway to the SaMD band immediately [assume: A-005] [derived: entry-scenarios] [config: commercial.yml]
- **R3 (medium)** — The hardware-scenario reassurance ('clears after our launch anchor') holds by 207 days at the fast edge under the favorable anchor reading, and holds under the end-of-period reading (2028-12-31) as well; the H2 anchor refinement itself is a catalog config choice — the strategy doc commits only 'Y3 (2028)' [derived: hardware-edge-margin] [assume: A-005] [config: commercial.yml]
  - _Mitigation_: Ground the launch anchor in the plan of record (commit a half-year or a date in commercial-strategy.md D-COMM-1.4), and never quote the hardware-scenario reassurance without its margin [derived: hardware-edge-margin] [assume: A-005] [config: commercial.yml]

### Watch

- **W1 (medium)** — Entry could be underway undetected: unannounced development programs are invisible in public data by construction, and FRN-only scope cannot see a De Novo or non-FRN predictive SaMD — absence of signal is not absence of entrant [src: commercial/openfda-510k-infusion@2026-09-28] [derived: watch-flagged]

## Method & provenance

- Premise check measured from [src: commercial/external-competitor-features@2026-09-28] (predictive_monitoring rows).
- Runway windows derived: A-005 band endpoints added to the data anchor [assume: A-005] [src: commercial/openfda-510k-infusion@2026-09-28]; launch anchor from [config: commercial.yml].
- Anchor sensitivity: both launch-anchor readings (first day / last day of the config period) are stated wherever a scenario's posture depends on them; the half-year refinement is config-only — the strategy doc commits the year, not the half [config: commercial.yml] [derived: hardware-edge-margin].
- Watch flags are keyword matches on public device names [config: commercial.yml]; applicant names normalized via [config: entity-aliases.yml].
- Historical view: quarterly clearance counts, software-flagged and ai/predictive-flagged, are charted zero-filled — the ai/predictive line is flat at zero, which IS the finding [derived: clearances-by-quarter] [src: commercial/openfda-510k-infusion@2026-09-28].
- Scope: product code FRN only; the dataset README's known limitation stands — widen the product-code scope before concluding no entrant activity.
