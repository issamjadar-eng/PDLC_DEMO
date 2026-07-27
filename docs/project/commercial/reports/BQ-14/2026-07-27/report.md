# BQ-14 — PCA feature parity: roadmap-covered vs silently unaddressed

**Verdict**: 10 attributes compared: 2 ahead, 4 parity, 4 behind — 3 behind-gaps have a roadmap lane (of which 2 adjacency-only: integrated_etco2, pca_pause_or_etco2 — the lane responds but does not mechanically close the gap), 1 SILENTLY UNADDRESSED (weight_kg) [derived: v-main] [src: commercial/external-competitor-features@2026-07-27] [config: commercial.yml]

## Parity matrix (line by line)

_Verdict rules, our-status vocabulary, and numeric directions per plans/BQ-14.md; lane routing per the attribute-lane map [config: commercial.yml]. A routed gap is labeled **closure** (the lane ships the missing capability itself) or **ADJACENCY** (the nearest lane responds via a different mechanism — the competitor's shipped capability may remain unanswered even after the lane lands), per the attribute-lane-relation config [config: commercial.yml]. `undocumented` = no row for us in the matrix, scored conservatively as not-shipping [src: commercial/external-competitor-features@2026-07-27]._

| Attribute | Us | Best competitor | Verdict | Routing |
|---|---|---|---|---|
| battery_hours [src: commercial/external-competitor-features@2026-07-27] [config: commercial.yml] | 150 | Smiths Medical (ICU Medical) CADD Legacy at 48-72 | ahead | — |
| ders_drug_library [src: commercial/external-competitor-features@2026-07-27] [config: commercial.yml] | yes (drug library 200+ medications) | 7 competitor product(s) shipping | parity (provisional) | — |
| flow_accuracy_pct [src: commercial/external-competitor-features@2026-07-27] [config: commercial.yml] | 0.35 | BD Alaris at 2.3 | ahead | — |
| integrated_etco2 [src: commercial/external-competitor-features@2026-07-27] [config: commercial.yml] | (no row — undocumented) | 1 competitor product(s) shipping | behind | gap on roadmap — F6, Y3 (2028) (ADJACENCY, not closure — nearest lane responds via a different mechanism) |
| pca_mode [src: commercial/external-competitor-features@2026-07-27] [config: commercial.yml] | yes (flagship patient-controlled analges | 3 competitor product(s) shipping | parity | — |
| pca_pause_or_etco2 [src: commercial/external-competitor-features@2026-07-27] [config: commercial.yml] | (no row — undocumented) | 1 competitor product(s) shipping | behind | gap on roadmap — F4, Y2 (2027) (ADJACENCY, not closure — nearest lane responds via a different mechanism) |
| predictive_monitoring [src: commercial/external-competitor-features@2026-07-27] [config: commercial.yml] | no (complete absence of predictive monit | 0 competitor product(s) shipping | parity | — |
| remote_update_capability [src: commercial/external-competitor-features@2026-07-27] [config: commercial.yml] | planned Y1 (Fleet Management + drug-libr | 0 competitor product(s) shipping | parity | — |
| weight_kg [src: commercial/external-competitor-features@2026-07-27] [config: commercial.yml] | 0.75 | Smiths Medical (ICU Medical) CADD Legacy at 0.45 | behind | SILENTLY UNADDRESSED — no roadmap lane owns this gap |
| wireless_connectivity [src: commercial/external-competitor-features@2026-07-27] [config: commercial.yml] | planned Y1 (Connectivity Adapter MDDS -  | 6 competitor product(s) shipping | behind (provisional) | roadmap-committed (planned) — F2, Y1 (2026) (lane closes the gap) |

- Provisional verdicts (a `verify`-flagged source cell is involved): ders_drug_library, wireless_connectivity [src: commercial/external-competitor-features@2026-07-27] — re-confirm before any external-facing use.
- Matrix no-data: dose_personalization — lane-mapped but zero rows for every vendor [src: commercial/external-competitor-features@2026-07-27] [config: commercial.yml]; no vendor is scored on it.
- Adjacency-routed gaps (integrated_etco2, pca_pause_or_etco2) are NOT closed by their lanes [config: commercial.yml] [derived: parity-matrix]: the lane is the nearest roadmap response, not a mechanical answer — treat 'gap on roadmap' for these as 'gap acknowledged', and keep them on the roadmap-council agenda alongside the silently unaddressed one(s).

## Narrative — Risks / Mitigations / Issues

### Issues (materialized — needs action)

- **I1 (high)** — weight_kg is behind (0.75 vs Smiths Medical (ICU Medical) CADD Legacy at 0.45) and NO roadmap lane owns the gap — silently unaddressed, nobody has decided about it [src: commercial/external-competitor-features@2026-07-27] [derived: parity-matrix] [config: commercial.yml]
  - _Action_: Put the gap on the roadmap-council agenda: accept it explicitly (documented trade-off) or assign it a lane — silence is the only wrong state [src: commercial/external-competitor-features@2026-07-27] [derived: parity-matrix] [config: commercial.yml]

### Risks (potential — mitigation identified)

- **R1 (high)** — BD ships PCA Pause and integrated EtCO2 today while our nearest roadmap answers sit in the F4 (Y2 (2027)) and F6 (Y3 (2028)) slots — and BOTH lane assignments are adjacency, not closure: F4 is smart alarm filtering and F6 is predictive monitoring, neither a hardware PCA-pause response nor a capnography module, so BD's shipped capability may remain unanswered even after F4/F6 land [src: commercial/external-competitor-features@2026-07-27] [derived: parity-matrix] [config: commercial.yml]
  - _Mitigation_: Feed this gap into the BQ-17 kill/pull-forward composite and the positioning guidance: sell the connected-safety story, do not contest PCA-pause head-to-head, and have the roadmap council decide explicitly whether the adjacency answer is the committed answer [src: commercial/external-competitor-features@2026-07-27] [derived: parity-matrix] [config: commercial.yml]

### Watch

- **W1 (medium)** — Deliberate matrix absences (dataset README): our PCA-pause/EtCO2 rows, several competitor accuracy specs, Plum Duo and Perfusor Space products — absences are under-coverage, not verdicts; curate before the next edition [src: commercial/external-competitor-features@2026-07-27]

## Method & provenance

- All cells measured from the curated matrix [src: commercial/external-competitor-features@2026-07-27]; every row carries its own source and verification flag.
- Verdicts derived per the committed rules (capability vs numeric typing, range scored at the competitor-favorable end, absence scored conservatively) [derived: parity-matrix] [config: commercial.yml].
- Historical view: parity-over-time needs successive curated snapshots — one snapshot exists, so the history series is marked unavailable rather than faked [derived: parity-history].
