# BQ-17 — Roadmap capstone: kill / pull-forward composite

_Demo sample data — not for clinical use._

**Verdict**: Decision support, not the decision: pull-forward candidate F4 Alerts Engine v1 (smart alarm filtering) (composite 0.616, tie with F6 broken on earliest wave); kill candidate F9 International expansion (EU MDR / Canada) (composite 0.0, tie with F7 broken on weakest evidence base) — sentiment axis is simulated-panel only, demand axis is Cloud attach 84.8%. CAUTION on the kill read: the single F9 voice argues the slot is too LATE and too THIN — a voice FOR earlier EU investment, arithmetically converted into kill support by the 3-value sentiment vocabulary [derived: v-main] [derived: composite] [src: commercial/internal-kol-register@2026-09-28] [src: commercial/internal-subscriptions@2026-09-28] [config: commercial.yml]

## Composite per feature — method fully stated

_Three components in [0, 1], unweighted mean (config choice) [config: commercial.yml]: competitive pressure (parity gaps + lane clearance activity), simulated-panel KOL sentiment rescaled, Cloud attach applied to cloud-delivered features. Full rules in plans/BQ-17.md; every caveat below the table._

| Feature | Wave | Pressure | Sentiment | Demand | Composite | Eligible |
|---|---|---|---|---|---|---|
| F1 Drug Library Manager GA [derived: composite] [config: commercial.yml] | Y1 (2026) | 0.5 | 0.5 | 0.848 | 0.616 | context only |
| F2 Connectivity Adapter GA [derived: composite] [config: commercial.yml] | Y1 (2026) | 0.5 | 0.5 | 0.848 | 0.616 | context only |
| F3 Fleet Management + Telemetry dashboards [derived: composite] [config: commercial.yml] | Y1 (2026) | 0.0 | 0.5 | 0.848 | 0.449 | context only |
| F4 Alerts Engine v1 (smart alarm filtering) [derived: composite] [config: commercial.yml] | Y2 (2027) | 1.0 | 0.0 | 0.848 | 0.616 | yes |
| F5 Clinical Surveillance [derived: composite] [config: commercial.yml] | Y2 (2027) | 0.0 | 0.875 | 0.848 | 0.574 | yes |
| F6 Predictive monitoring (occlusion/infiltration/deterioration) [derived: composite] [config: commercial.yml] | Y3 (2028) | 1.0 | 0.0 | 0.848 | 0.616 | yes |
| F7 Ambulatory PP3500-A (home PCA) [derived: composite] [config: commercial.yml] | Y3-Y4 (2028-2029) | 0.0 | 0.0 | 0.0 | 0.0 | yes |
| F8 Dose personalization decision-support [derived: composite] [config: commercial.yml] | Y4 (2029) | 0.0 | 0.0 | 0.848 | 0.283 | yes |
| F9 International expansion (EU MDR / Canada) [derived: composite] [config: commercial.yml] | Y5 (2030) | 0.0 | 0.0 | 0.0 | 0.0 | yes |

- Pressure inputs: lane-mapped parity states from [src: commercial/external-competitor-features@2026-09-28]; trailing-12-month lane keyword hits 2025-07-24 → 2026-07-24 from [src: commercial/openfda-510k-infusion@2026-09-28] [config: commercial.yml]. Keyword hits: F1: K251636, K251640.
- Sentiment inputs: distinct-voice net sentiment from [src: commercial/internal-kol-register@2026-09-28] — SIMULATED panel, zero real collected KOL evidence (BQ-16 meta-gap); this third of every composite is assumption-class.
- Demand input: Cloud Suite attach 84.8% = 39 active subscribed connected sites of 46 connected sites [derived: attach-rate] [src: commercial/internal-subscriptions@2026-09-28] [src: commercial/internal-fleet@2026-09-28]. Non-cloud features (F7, F9) score zero on this axis BY CONSTRUCTION — no demand dataset exists for them; zero is a data gap, not measured absence of demand [config: commercial.yml].

## The two candidates (derived rankings, council judgment pending)

- **Pull forward: F4 Alerts Engine v1 (smart alarm filtering)** (Y2 (2027)) — composite 0.616 [derived: composite]; exact tie with F6 broken by earliest scheduled wave [config: commercial.yml].
- **Kill candidate: F9 International expansion (EU MDR / Canada)** (Y5 (2030)) — composite 0.0 [derived: composite]; exact tie with F7 broken by fewest distinct voices (1 vs 5) [src: commercial/internal-kol-register@2026-09-28].
- **Direction of the only voice behind the kill candidate**: the single F9 voice on file (Kuitunen) argues F9 is 'too late and too thin' — start the EU clinical-evaluation and library-governance evidence EARLIER (Y1-Y2), not never [src: commercial/internal-kol-register@2026-09-28] (per-KOL source doc via the dataset README). The register's 3-value vocabulary encodes that position as bare `concern`, which zeroes F9's sentiment axis — i.e. a voice FOR earlier, stronger investment arithmetically supports the kill ranking. A kill decision citing this composite must weigh that the only evidence on file contradicts the kill reading.

## Robustness of the two picks (computed, plan-committed)

- Weighting invariance: the top tie (F4 / F6) shares an IDENTICAL axis vector and the bottom tie (F9 / F7) shares an IDENTICAL axis vector — an identical-vector tie survives ANY axis weighting, so each pick is 100% tie-break-decided (earliest wave / fewest voices), not weighting-decided [derived: robustness] [config: commercial.yml].
- Sentiment-axis drop: recomputing WITHOUT the simulated sentiment axis (mean of pressure + demand) leaves BOTH picks unchanged (F4 / F9) — the assumption-class axis is not load-bearing for the two candidates themselves [derived: robustness].
- Weight sensitivity: transferring ~2.25 pp of weight from the pressure axis to the sentiment axis flips the pull-forward candidate to F5 — the margin over the runner-up at equal weights is small, and the flipping axis is the simulated one; revisit weights with the council [derived: robustness] [config: commercial.yml].

## Narrative — Risks / Mitigations / Issues

### Issues (materialized — needs action)

- **I1 (high)** — Direction inversion on the kill candidate: the single F9 voice on file (Kuitunen) argues F9 is too LATE and too THIN — advocating earlier EU evidence investment — but the 3-value sentiment vocabulary encodes it as bare concern, arithmetically supporting the kill ranking; the only evidence on file contradicts the kill reading [src: commercial/internal-kol-register@2026-09-28] [derived: composite]
  - _Action_: Present the voice's actual position alongside any kill discussion; add a stance/timing-direction dimension to the register before the next edition (BQ-16 RT-16.1 shares this defect) [src: commercial/internal-kol-register@2026-09-28] [derived: composite]

### Risks (potential — mitigation identified)

- **R1 (high)** — The kill ranking rests on a composite whose sentiment third is simulated and whose demand third does not exist for non-cloud features — F9 scores zero pressure, zero measured demand, and its sentiment comes from 1 simulated voice(s) [derived: composite] [src: commercial/internal-kol-register@2026-09-28]
  - _Mitigation_: Before any kill decision: collect real KOL evidence for the candidate and acquire a demand-side dataset for non-cloud features (home-infusion channel, international pipeline) [derived: composite] [src: commercial/internal-kol-register@2026-09-28]
- **R2 (medium)** — F9 and F7 tie exactly at composite 0.0 — only evidence thinness separates the kill candidate from the runner(s)-up [derived: composite] [src: commercial/internal-kol-register@2026-09-28]
  - _Mitigation_: Treat both bottom-tier features as evidence-starved rather than ranking one safe; the tiebreak is stated, not meaningful [derived: composite] [src: commercial/internal-kol-register@2026-09-28]

### Watch

- **W1 (medium)** — Equal axis weighting is a committed modeling choice, not derived from the plan of record — and the flip distance is SMALL: a ~2.25 pp pressure-to-sentiment weight transfer flips the pull-forward candidate to F5; the two picks themselves are tie-break-decided and weighting-invariant (see robustness) — revisit the weights with the council before acting [config: commercial.yml] [derived: robustness] [derived: composite]
- **W2 (medium)** — No business-case axis: revenue/margin per feature is absent from this composite entirely — the ranking is evidence pressure, not economics [derived: composite]

## Method & provenance

- Components computed from the five pins: parity states [src: commercial/external-competitor-features@2026-09-28], clearance keyword activity [src: commercial/openfda-510k-infusion@2026-09-28], sentiment [src: commercial/internal-kol-register@2026-09-28], attach [src: commercial/internal-subscriptions@2026-09-28] + [src: commercial/internal-fleet@2026-09-28]; all maps, weights, and eligibility from [config: commercial.yml].
- Historical view: gross cumulative subscribed-site adds by start month are charted as the demand-signal history [derived: subscribed-sites-history] [src: commercial/internal-subscriptions@2026-09-28]; churn dates are not recorded in the register, so the line shows gross adds, not net — stated, not hidden.
- A composite-score history needs successive editions of this answer — none exist yet; re-answers will accumulate it [derived: composite].
