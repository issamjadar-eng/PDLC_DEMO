# BQ-15 — SOTA currency: differentiators + refresh verdict

**Verdict**: ride to scheduled review (2027-04-12): both differentiators remain ahead of every documented competitor value and no refresh trigger fired. Accuracy margin ~6.6x vs best documented competitor on our LAB-basis spec (~4.6x on our volumetric-basis spec — ahead on either basis; competitor cells are nominal/field specs), battery ~2.1x; 1 FRN clearance(s) observed after the SOTA anchor date (2026-04-12) in a snapshot whose coverage ends 2026-07-24 [derived: v-refresh] [src: commercial/external-competitor-features@2026-09-21] [src: commercial/openfda-510k-infusion@2026-09-21] [config: commercial.yml]

## Headline differentiators vs every documented competitor value

_Our values are the config constants matching the SOTA doc's headline claims [config: commercial.yml]; the SOTA doc itself ([config: docs/project/input-analysis/competitive-landscape/state-of-the-art-analysis.md]) is referenced, not parsed._

### Flow accuracy (± pct, lower is better) — ours 0.35 [config: commercial.yml]

| Competitor product | Value | Verified |
|---|---|---|
| BD Alaris [src: commercial/external-competitor-features@2026-09-21] | 2.3 | yes |
| Baxter Spectrum IQ [src: commercial/external-competitor-features@2026-09-21] | 2.3 | yes |
| Smiths Medical (ICU Medical) CADD-Solis [src: commercial/external-competitor-features@2026-09-21] | 6 | yes |
| B.Braun Infusomat Space [src: commercial/external-competitor-features@2026-09-21] | 5 | yes |

- Ahead of all 4 documented values (4 verified); margin vs best (BD Alaris) ~6.6x [derived: differentiator-margins] [src: commercial/external-competitor-features@2026-09-21].
- Spec-basis disclosure: our 0.35 is the LABORATORY-standard spec, while competitor cells are nominal/field specs — a basis-mixed comparison. On our volumetric-basis spec (0.5) the margin is ~4.6x, and we are still ahead of every documented value — 'ahead' survives either basis; the headline multiple is basis-sensitive [derived: differentiator-margins] [config: commercial.yml] [src: commercial/external-competitor-features@2026-09-21].
- No documented accuracy value for: BD Alaris (PCA Module), Baxter Novum IQ (LVP), Baxter Sigma Spectrum, ICU Medical Plum 360, Smiths Medical (ICU Medical) CADD Legacy [src: commercial/external-competitor-features@2026-09-21] — the comparison covers only documented cells; superiority over undocumented specs is NOT claimed.

### Battery (hours, higher is better) — ours 150 [config: commercial.yml]

| Competitor product | Value | Verified |
|---|---|---|
| BD Alaris [src: commercial/external-competitor-features@2026-09-21] | 6 | yes |
| Baxter Sigma Spectrum [src: commercial/external-competitor-features@2026-09-21] | 4 | yes |
| ICU Medical Plum 360 [src: commercial/external-competitor-features@2026-09-21] | 7 | yes |
| Smiths Medical (ICU Medical) CADD Legacy [src: commercial/external-competitor-features@2026-09-21] | 48-72 | yes |
| B.Braun Infusomat Space [src: commercial/external-competitor-features@2026-09-21] | 3.5-13 | yes |

- Ahead of all 5 documented values (5 verified); margin vs best (Smiths Medical (ICU Medical) CADD Legacy) ~2.1x [derived: differentiator-margins] [src: commercial/external-competitor-features@2026-09-21].
- No documented battery value for: BD Alaris (PCA Module), Baxter Novum IQ (LVP), Baxter Spectrum IQ, Smiths Medical (ICU Medical) CADD-Solis [src: commercial/external-competitor-features@2026-09-21].

## Clearance activity since the SOTA anchor (the currency signal)

- 1 FRN clearance(s) with a decision date after the SOTA anchor (2026-04-12) [derived: since-doc-count] [src: commercial/openfda-510k-infusion@2026-09-21] [config: commercial.yml].
- Publication-lag caveat: the pinned snapshot's coverage ends at its newest decision date (2026-07-24) — a clearance decided after that date is invisible here, so a zero is lag-limited, not proof of quiet [src: commercial/openfda-510k-infusion@2026-09-21].
- Context: 4 clearances in the trailing window 2025-07-24 → 2026-07-24 [derived: trailing-context] [src: commercial/openfda-510k-infusion@2026-09-21] [config: commercial.yml] — the segment is active; currency erodes by cadence, not by event only.

## Refresh verdict (deterministic rule, plan-committed)

- Rule: refresh now if a margin erodes, a predictive_monitoring row turns `yes`, or the doc exceeds its 12-month review cadence [config: commercial.yml].
- Trigger check — margins: accuracy ahead (lab basis) / ahead (volumetric basis), battery ahead [derived: differentiator-margins]; predictive_monitoring rows reading `yes`: 0 [src: commercial/external-competitor-features@2026-09-21]; doc age at snapshot acquisition 162 days vs cadence [derived: v-refresh] [config: commercial.yml].
- Next scheduled review 2027-04-12 (anchor + 12 calendar months) [derived: v-refresh] [config: commercial.yml].
- The cadence is a config stand-in for the QMS SOTA/PMS review cadence, not a documented EU MDR obligation — challengeable [config: commercial.yml]. The anchor is the doc's ADOPTION date; if the underlying analysis was authored earlier, currency is overstated [config: commercial.yml].

## Narrative — Risks / Mitigations / Issues

### Risks (potential — mitigation identified)

- **R1 (medium)** — The currency signal is lag-limited: the 510(k) snapshot's coverage ends 2026-07-24, months before the snapshot's acquisition — a recent clearance may already exist unseen [src: commercial/openfda-510k-infusion@2026-09-21] [derived: since-doc-count]
  - _Mitigation_: Refresh the 510(k) dataset on its 90-day cadence and re-answer; treat a quiet window as unproven, not proven [src: commercial/openfda-510k-infusion@2026-09-21] [derived: since-doc-count]

### Watch

- **W1 (medium)** — Accuracy comparison rests on 4 documented cells and battery on 5 — several competitor products carry no value for these attributes, and undocumented is not beaten [src: commercial/external-competitor-features@2026-09-21] [derived: differentiator-margins]
- **W2 (medium)** — Scope: product code FRN only — a SOTA-relevant clearance outside FRN (e.g. a monitoring SaMD) is invisible to this currency signal; widen the corpus before treating the signal as complete [src: commercial/openfda-510k-infusion@2026-09-21]

## Method & provenance

- Competitor values measured from the curated matrix [src: commercial/external-competitor-features@2026-09-21] (ranges scored at the competitor-favorable end); our constants from [config: commercial.yml].
- Clearance counts measured from [src: commercial/openfda-510k-infusion@2026-09-21]; refresh rule and cadence from [config: commercial.yml].
- Historical view: quarterly FRN clearance counts are charted [derived: clearances-by-quarter] [src: commercial/openfda-510k-infusion@2026-09-21].
