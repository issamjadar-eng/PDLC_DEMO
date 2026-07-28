# BQ-29 — Cloud Suite attach-rate stage-gate

_Demo sample data — not for clinical use._

**Verdict**: The attach stage-gate HOLDS at the stand-in level: 43.0% of the PP3500 installed base (295 of 686 pumps) vs the 40% gate — but the $24M releases on a gate NUMBER nobody has ratified; the strategy of record says 'traction' and sets no threshold — and the verdict is denominator-definition-sensitive: under a whole-PCA denominator (884 pumps incl. 198 unconnectable PP3000) attach reads 33.4%, BELOW the stand-in gate; the metric definition is as unratified as the gate number [derived: v-main] [src: commercial/internal-subscriptions@2026-07-27.2] [src: commercial/internal-fleet@2026-07-27] [config: commercial.yml]

## The gate reading

- Attach = pumps under an ACTIVE subscription ÷ PP3500 installed base: 295 ÷ 686 = 43.0% [derived: attach-stat] [src: commercial/internal-subscriptions@2026-07-27.2] [src: commercial/internal-fleet@2026-07-27]
- Gate level: 40% releases the $24M predictive-monitoring spend [config: commercial.yml] — a numeric stand-in; commercial-strategy.md conditions the spend on 'Y1/Y2 Cloud Suite traction' and sets NO number [config: commercial.yml]
- Churned subscriptions count zero: 3 churned sites are in the gap pool, not the numerator [src: commercial/internal-subscriptions@2026-07-27.2]

## Denominator sensitivity (disclosed, not absorbed)

_The gate metric's denominator is a definition choice no one has ratified — with the gate number itself a stand-in, the metric definition is equally unratified, so the reading is shown under both bases [derived: denominator-sensitivity]._

| Basis | Attached | Denominator | Attach % | vs the 40% stand-in gate |
|---|---|---|---|---|
| PP3500 installed base (primary) [derived: denominator-sensitivity] [src: commercial/internal-fleet@2026-07-27] | 295 | 686 | 43.0% | holds |
| Whole PCA installed base (PP3500 + PP3000) [derived: denominator-sensitivity] [src: commercial/internal-fleet@2026-07-27] | 295 | 884 | 33.4% | BELOW |

- Basis defense: the primary excludes PP3000 because 0 of 198 PP3000 devices are connected and no PP3000 adapter path exists in the corpus — Cloud Suite sells on the PP3500 base [src: commercial/internal-fleet@2026-07-27]. The denominator choice alone moves the reading across the gate (43.0% vs 33.4%): ratify the metric definition together with the gate number [derived: denominator-sensitivity] [config: commercial.yml].

## Where the rest of the base sits

| Segment | PP3500 pumps | Share of installed base |
|---|---|---|
| Under active subscription [derived: attach-breakdown] [src: commercial/internal-subscriptions@2026-07-27.2] | 295 | 43.0% |
| Connected, no active subscription (go-get) [derived: attach-breakdown] [src: commercial/internal-fleet@2026-07-27] | 36 | 5.2% |
| Not connected [derived: attach-breakdown] [src: commercial/internal-fleet@2026-07-27] | 355 | 51.7% |

## Attach by region

| Region | Attached pumps | PP3500 installed | Attach % |
|---|---|---|---|
| APAC [derived: attach-by-region] [src: commercial/internal-subscriptions@2026-07-27.2] [src: commercial/internal-fleet@2026-07-27] | 28 | 146 | 19.2% |
| EMEA [derived: attach-by-region] [src: commercial/internal-subscriptions@2026-07-27.2] [src: commercial/internal-fleet@2026-07-27] | 79 | 201 | 39.3% |
| NA [derived: attach-by-region] [src: commercial/internal-subscriptions@2026-07-27.2] [src: commercial/internal-fleet@2026-07-27] | 188 | 339 | 55.5% |

## Go-get gap by site

| Site | Connected, unsubscribed pumps | History |
|---|---|---|
| S-NA-11 [derived: gap-sites] [src: commercial/internal-fleet@2026-07-27] | 17 | churned subscription |
| S-APAC-08 [derived: gap-sites] [src: commercial/internal-fleet@2026-07-27] | 5 | never subscribed |
| S-NA-21 [derived: gap-sites] [src: commercial/internal-fleet@2026-07-27] | 4 | never subscribed |
| S-EMEA-08 [derived: gap-sites] [src: commercial/internal-fleet@2026-07-27] | 3 | never subscribed |
| S-EMEA-13 [derived: gap-sites] [src: commercial/internal-fleet@2026-07-27] | 3 | never subscribed |
| S-NA-04 [derived: gap-sites] [src: commercial/internal-fleet@2026-07-27] | 3 | churned subscription |
| S-NA-01 [derived: gap-sites] [src: commercial/internal-fleet@2026-07-27] | 1 | churned subscription |

- Cumulative pumps under currently-active subscriptions are charted by start month [derived: cumulative-attach] [src: commercial/internal-subscriptions@2026-07-27.2]; a true attach-% history needs historical fleet snapshots and churn end-dates — published as unavailable, not faked [derived: attach-history].

## Assumptions & expectations — plan vs actual

_`unvalidated` means the expectation itself is a stand-in that has not been grounded
in a plan of record or the risk file — challenge the assumption, not just the actual._

| ID | Expectation | Expected | Actual | Verdict | Basis |
|---|---|---|---|---|---|
| E-29.1 | Installed-base Cloud Suite attach reaches the stage-gate level before the predictive-monitoring spend releases [derived: attach-stat] [derived: denominator-sensitivity] [config: commercial.yml] | >= 40% of PP3500 installed base attached | 43.0% attach vs the 40% stand-in (+3.0 points); no gate number is ratified in the strategy of record; denominator-sensitive — the whole-PCA basis reads 33.4%, below the gate | met (unvalidated) | numeric stand-in — commercial-strategy.md gates the $24M on 'Y1/Y2 Cloud Suite traction' but sets NO number [VERIFY] |

## Narrative — Risks / Mitigations / Issues

### Risks (potential — mitigation identified)

- **R1 (high)** — The $24M release decision references a gate with no number of record — the 40% is a stand-in, and at 43.0% attach the reading sits 3.0 points from it; any ratified threshold in that neighborhood flips the verdict — and the metric DEFINITION is equally unratified: the whole-PCA denominator reads 33.4%, below the gate, so the denominator choice alone spans the gate [derived: attach-stat] [derived: denominator-sensitivity] [config: commercial.yml]
  - _Mitigation_: Have the board/CFO ratify a numeric gate AND the metric definition (denominator basis) in the commercial strategy or plan of record and mark E-29.1 validated before the spend decision [derived: attach-stat] [derived: denominator-sensitivity] [config: commercial.yml]

### Watch

- **W1 (medium)** — Go-get gap: 36 connected-but-unsubscribed pumps across 7 sites (S-NA-11, S-APAC-08, S-NA-21, S-EMEA-08, S-EMEA-13, S-NA-04, S-NA-01) — 3 of those sites are churn-losses (S-NA-01, S-NA-04, S-NA-11), the rest never subscribed; this is the nearest-term attach growth and winback territory [derived: gap-sites] [src: commercial/internal-subscriptions@2026-07-27.2] [src: commercial/internal-fleet@2026-07-27]
- **W2 (medium)** — 355 of 686 PP3500 pumps are not connected at all — attach beyond the connected base runs through the connectivity/adapter path (the BQ-30 business case), not sales motion alone [derived: attach-breakdown] [src: commercial/internal-fleet@2026-07-27]

## Method & provenance

- Numerator summed from active rows of [src: commercial/internal-subscriptions@2026-07-27.2]; denominator is the PP3500 count in [src: commercial/internal-fleet@2026-07-27] — the project's installed-base registry. PP3000 is excluded from the primary basis (zero connected devices; Cloud Suite sells on the PP3500 base), and the whole-PCA alternative is printed in the denominator-sensitivity section rather than absorbed [src: commercial/internal-fleet@2026-07-27] [derived: denominator-sensitivity].
- Gate level and gated spend are declared constants [config: commercial.yml]; the gate's lack of a ratified number — and of a ratified metric definition — is the report's central caveat, stated in the verdict.
