# BQ-10 — The buyer's 5-year TCO spreadsheet (indicative, assumption-bounded)

_Demo sample data — not for clinical use._

_Our per-pump cost constants are demo stand-ins, not finance-validated rates [config: commercial.yml]; the competitor side is a real-compiled, assumption-bounded range [assume: A-004]._

**Verdict**: Indicative, assumption-bounded: our 5-yr TCO is $8,900/pump all-in ($5,100 on the capital+service basis) vs a class-wide competitor range of ~$3,000–$15,000 on capital+service ONLY — competitor consumables and software subscription are undisclosed and excluded, so their true all-in TCO sits ABOVE that range; the ranges overlap and no hard we-win claim is supportable [derived: v-main] [config: commercial.yml] [assume: A-004]

## Our 5-yr TCO per pump (declared constants) [config: commercial.yml]

| Component | Basis | 5-yr amount |
|---|---|---|
| PP3500 capital [config: commercial.yml] | one-time | $4,200 |
| Cloud Suite subscription [config: commercial.yml] | $450/yr × 5 | $2,250 |
| Consumables [config: commercial.yml] | $310/yr × 5 | $1,550 |
| Service [config: commercial.yml] | $180/yr × 5 | $900 |
| **Total (all-in)** [derived: our-tco] | | **$8,900** |
| **Capital + service only** (the A-004-comparable basis) [derived: our-tco] | | **$5,100** |

## Competitor side — a RANGE, and why it is one

- Realized pump prices are negotiated under confidential GPO/IDN contracts and never published; the competitor figures below are the assumption record's compiled range [assume: A-004].
- Capital: $2,200–$6,900 standalone LVP, effectively $4,400–$13,700 once networked/EMR-integrated [assume: A-004].
- Service: $150–$250 per pump/yr → $750–$1,250 over 5 years [assume: A-004].
- Indicative 5-yr TCO, capital + service only: ~$3,000–$15,000 [assume: A-004].
- EXCLUDED on the competitor side, restated from the record: consumables pricing
  (not publicly disclosed) and software-subscription magnitude (required annually,
  unquantified). Their true all-in TCO is therefore strictly above the quoted range
  [assume: A-004].
- Alaris, Spectrum IQ, and Plum 360 share this one class-wide range [assume: A-004] —
  public pricing does not split by vendor.

## Feature context per competitor (curated matrix; verification status carried)

_Cells marked “(verify)” have a named but independently unfetched source; “—” means no
confirmable source exists and the value is deliberately absent, not guessed
[src: commercial/external-competitor-features@2026-09-21]._

| Attribute | PP3500 (ours) | Alaris | Spectrum IQ | Plum 360 |
|---|---|---|---|---|
| ders_drug_library [src: commercial/external-competitor-features@2026-09-21] | yes (drug library 200+ medications) | yes (Guardrails) | yes (Dose IQ safety software) (verify) | yes (ICU Medical MedNet - up to 2500 drugs / 40 care areas) |
| wireless_connectivity [src: commercial/external-competitor-features@2026-09-21] | planned Y1 (Connectivity Adapter MDDS - roadmap F2) | yes (Wi-Fi) | yes (EMR auto-programming integration) (verify) | yes (Ethernet + 802.11 a/b/g/n dual-band) |
| predictive_monitoring [src: commercial/external-competitor-features@2026-09-21] | no (complete absence of predictive monitoring across portfolio) | no (reactive alarms only) | no (reactive alarms only) | no (named reactive-alarm incumbent) |
| battery_hours [src: commercial/external-competitor-features@2026-09-21] | 150 | 6 | — | 7 |
| flow_accuracy_pct [src: commercial/external-competitor-features@2026-09-21] | 0.35 | 2.3 | 2.3 | — |

## Narrative — Risks / Mitigations / Issues

### Risks (potential — mitigation identified)

- **R1 (high)** — The comparison is not like-for-like by construction: the competitor range excludes consumables (undisclosed) and quantifies software subscription only as 'required, magnitude unknown', while our figure includes both — the spread understates competitor cost [assume: A-004] [derived: tco-comparison]
  - _Mitigation_: Present only the capital+service basis side-by-side in buyer-facing material; state the exclusions verbatim from the assumption record [assume: A-004] [derived: tco-comparison]
- **R2 (medium)** — Our own cost constants are demo stand-ins, not finance-validated rates — both sides of the buyer's spreadsheet are currently unvalidated [config: commercial.yml]
  - _Mitigation_: Have finance ratify the four per-pump constants before external use; then re-answer [config: commercial.yml]

### Watch

- **W1 (medium)** — A-004's refresh trigger is a new procurement award / GPO disclosure / analyst pricing commentary — any of these should prompt a re-answer [assume: A-004]

## Data gap (stated, not papered over)

- No TCO history exists — a trend needs dated refreshes of the pricing assumption as
  procurement disclosures surface; the history series is published as unavailable, not
  faked [derived: tco-history].

## Method & provenance

- Our constants and the 5-yr horizon are declared plan constants [config: commercial.yml]; totals are arithmetic over them [derived: our-tco].
- Competitor range transcribed from the assumption record (confidence: low) [assume: A-004]; feature cells measured from [src: commercial/external-competitor-features@2026-09-21].
- No catalog expectations are declared for this question — none are invented.
