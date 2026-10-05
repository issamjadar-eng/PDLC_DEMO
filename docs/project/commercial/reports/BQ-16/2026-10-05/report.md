# BQ-16 — KOL evidence per roadmap feature (and the meta-gap)

_Demo sample data — not for clinical use._

**Verdict**: META-GAP: all 38 evidence rows are a simulated advisory panel — zero real collected KOL evidence exists (no interviews, surveys, or publications). Within the simulated register: F9 rides on a single voice (E-16.1 floor not met), and the F4, F6, F7, F8 wave slots carry concern-majority sentiment — read as NO documented endorsement of those slots, not as opposition: the register's 3-value vocabulary collapses conditional support into `concern` (stated limitation) [derived: v-main] [src: commercial/internal-kol-register@2026-10-05] [config: commercial.yml]

## Epistemic status FIRST — what this register is and is not

- Every row is `evidence_type: advisory-board` from the simulated 8-persona KOL panel (38 of 38 rows) [src: commercial/internal-kol-register@2026-10-05] [derived: evidence-type-census]. These are project-authored persona opinions, NOT collected feedback.
- Real collected evidence on file — interviews: 0, surveys: 0, publications: 0 [derived: evidence-type-census] [src: commercial/internal-kol-register@2026-10-05]. All roster KOLs are 'not yet contacted' (dataset README, KOL-review finding F-1) — every per-feature figure below measures the simulated panel only.

## Voices and sentiment per feature (simulated panel)

| Feature | Wave | Voices | Support | Neutral | Concern | Flags |
|---|---|---|---|---|---|---|
| F1 Drug Library Manager GA [src: commercial/internal-kol-register@2026-10-05] [config: commercial.yml] | Y1 (2026) | 5 | 2 | 1 | 2 | — |
| F2 Connectivity Adapter GA [src: commercial/internal-kol-register@2026-10-05] [config: commercial.yml] | Y1 (2026) | 3 | 1 | 1 | 1 | — |
| F3 Fleet Management + Telemetry dashboards [src: commercial/internal-kol-register@2026-10-05] [config: commercial.yml] | Y1 (2026) | 3 | 1 | 1 | 1 | — |
| F4 Alerts Engine v1 (smart alarm filtering) [src: commercial/internal-kol-register@2026-10-05] [config: commercial.yml] | Y2 (2027) | 6 | 0 | 0 | 6 | concern-majority, no documented slot endorsement |
| F5 Clinical Surveillance [src: commercial/internal-kol-register@2026-10-05] [config: commercial.yml] | Y2 (2027) | 4 | 3 | 1 | 0 | — |
| F6 Predictive monitoring (occlusion/infiltration/deterioration) [src: commercial/internal-kol-register@2026-10-05] [config: commercial.yml] | Y3 (2028) | 5 | 0 | 0 | 5 | concern-majority, no documented slot endorsement |
| F7 Ambulatory PP3500-A (home PCA) [src: commercial/internal-kol-register@2026-10-05] [config: commercial.yml] | Y3-Y4 (2028-2029) | 5 | 0 | 0 | 5 | concern-majority, no documented slot endorsement |
| F8 Dose personalization decision-support [src: commercial/internal-kol-register@2026-10-05] [config: commercial.yml] | Y4 (2029) | 6 | 0 | 0 | 6 | concern-majority, no documented slot endorsement |
| F9 International expansion (EU MDR / Canada) [src: commercial/internal-kol-register@2026-10-05] [config: commercial.yml] | Y5 (2030) | 1 | 0 | 0 | 1 | below 2-voice floor, concern-majority |

- Single-voice features: F9; zero-voice features: none [derived: voices-per-feature] [src: commercial/internal-kol-register@2026-10-05].

## Wave check — do the committed wave slots have documented endorsement?

- Rule: a concern-majority feature scheduled in a Y2/Y3/Y4 slot is flagged [config: commercial.yml].
- Flagged: F4 (Y2 (2027)), F6 (Y3 (2028)), F7 (Y3-Y4 (2028-2029)), F8 (Y4 (2029)) [derived: sentiment-mix] [src: commercial/internal-kol-register@2026-10-05] [config: commercial.yml] — read the flag as EVIDENCE ABSENCE (concern-majority means the slot has no documented endorsement), NOT as the panel opposing the slot; advisory only, because the sentiment is simulated (meta-gap).
- Vocabulary-flattening limitation (stated): the register's 3-value sentiment scale (support | neutral | concern) cannot represent conditional support — per the dataset README's mapping convention, a 'conditional yes' encodes as `concern` [src: commercial/internal-kol-register@2026-10-05]. Source-doc spot checks show flagged-slot concern voices that explicitly endorse the sequencing while demanding conditions (Giuliano on F4: conditional support pending a pre-specified suppressed-true-alarm bound; Gorski on F7: 'sequencing is right', deferral endorsed) [src: commercial/internal-kol-register@2026-10-05] — check the per-KOL source doc before reading any concern row as slot opposition.

## Assumptions & expectations — plan vs actual

_`unvalidated` means the expectation itself is a stand-in that has not been grounded
in a plan of record or the risk file — challenge the assumption, not just the actual._

| ID | Expectation | Expected | Actual | Verdict | Basis |
|---|---|---|---|---|---|
| E-16.1 | Every committed roadmap feature has at least two independent KOL voices on file [derived: voices-per-feature] [src: commercial/internal-kol-register@2026-10-05] [config: commercial.yml] | >= 2 distinct KOLs per F1-F9 feature | distinct simulated-panel voices per feature — F1: 5; F2: 3; F3: 3; F4: 6; F5: 4; F6: 5; F7: 5; F8: 6; F9: 1; features below the floor: F9 (and zero REAL voices everywhere — see meta-gap) | not-met (unvalidated) | evidence-sufficiency stand-in; the KOL program sets no formal floor |

## Narrative — Risks / Mitigations / Issues

### Issues (materialized — needs action)

- **I1 (high)** — Zero real collected KOL evidence exists behind any of the 9 committed roadmap features — the entire register (38 rows) is simulated panel material [derived: evidence-type-census] [src: commercial/internal-kol-register@2026-10-05]
  - _Action_: Commission actual KOL engagement (interviews/advisory board) before the next roadmap commit; re-populate the register from collected evidence and re-answer [derived: evidence-type-census] [src: commercial/internal-kol-register@2026-10-05]
- **I2 (medium)** — F9 fails even the simulated-panel two-voice floor (E-16.1) — the weakest-evidenced committed bet(s) [derived: voices-per-feature] [config: commercial.yml] [src: commercial/internal-kol-register@2026-10-05]
  - _Action_: Add voices for the below-floor feature(s) in the next engagement round, or surface the thin base at the roadmap council [derived: voices-per-feature] [config: commercial.yml] [src: commercial/internal-kol-register@2026-10-05]

### Risks (potential — mitigation identified)

- **R1 (medium)** — The committed middle-wave slots (F4, F6, F7, F8) carry concern-majority sentiment — no documented endorsement of those slots exists. Caveat: the 3-value vocabulary flattens conditional support into concern (source docs show conditional-yes voices on F4 and F7), so this is an evidence-absence signal, not measured opposition [derived: sentiment-mix] [src: commercial/internal-kol-register@2026-10-05] [config: commercial.yml]
  - _Mitigation_: Feed the flagged features into BQ-17's composite, prioritize them in the real-KOL engagement plan, and capture stance + timing direction (not just 3-value sentiment) when real evidence is collected [derived: sentiment-mix] [src: commercial/internal-kol-register@2026-10-05] [config: commercial.yml]

### Watch

- **W1 (medium)** — Voice independence is overstated by construction: all voices come from one simulated panel session on one date — distinct kol_id is a weaker notion of independence than E-16.1 intends [src: commercial/internal-kol-register@2026-10-05]

## Method & provenance

- Voice counts (distinct kol_id), sentiment mixes, and the evidence-type census are measured from [src: commercial/internal-kol-register@2026-10-05]; feature universe and wave slots from [config: commercial.yml].
- Historical view: sentiment-over-time needs dated engagements across time — every current row carries the single panel date, so the history series is marked unavailable rather than faked [derived: sentiment-history].
