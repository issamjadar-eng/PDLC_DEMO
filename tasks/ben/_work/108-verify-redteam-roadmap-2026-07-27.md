# Independent verification + red-team — Roadmap slice (BQ-13…BQ-17), editions 2026-07-27

_Task ben/108 · verifier: adversarial-verify + red-team agent (AI, independent) · date 2026-07-27_
_Method: strict two-pass. Pass 1 re-derived every verdict/series from `pins.json` + `data.json` + pinned snapshot CSVs only (throwaway scripts in the session scratchpad, outside the repo tree; params from `commercial.yml`; A-005 from the dataset's `assumptions/`). Pass 2 read report.md / plans / quality.json and audited the underlying data against source documents. No repo artifacts modified._

## Summary verdicts

| BQ | Pass 1 (adversarial re-derivation) | Pass 2 (red-team) most serious finding |
|---|---|---|
| BQ-13 | CONFIRMED-WITH-CAVEAT | Hardware-scenario reassurance is razor-thin (27 days) and anchor-reading-dependent (RT-13.1, medium) |
| BQ-14 | CONFIRMED | Lane map lets F4/F6 "own" gaps they arguably don't close (RT-14.1, medium) |
| BQ-15 | CONFIRMED | Accuracy margin mixes spec bases: 6.6x (lab) vs ~4.6x (volumetric); "ahead" survives both (RT-15.1, low-medium) |
| BQ-16 | CONFIRMED | "Concern-majority challenges the wave slots" overreads condition-concerns as slot-challenges (RT-16.1, medium) |
| BQ-17 | CONFIRMED-WITH-CAVEAT | F9 kill candidate's only voice actually argues to invest EARLIER, encoded as bare "concern" (RT-17.1, high) |

---

## Pass 1 — adversarial re-derivation (pins only)

### BQ-13 — CONFIRMED-WITH-CAVEAT

Recomputed from `openfda-510k-infusion@2026-07-22` (29 records) + `external-competitor-features@2026-07-27` + A-005 + config:

- Data anchor (newest decision_date): **2026-01-28** ✓. Review-time floor per A-005 estimation method: median **213 days (~7.0 mo)** ✓; IQR 84–293 reproduces with the *inclusive* quantile method (exclusive gives 79–353 — method unstated in A-005, immaterial).
- Runway stat: slow SaMD edge = 2026-01-28 + 24 mo = **2028-01-28**, vs launch anchor 2028-07-01 → **5.1 months** ✓ (reported: 5).
- Entry-scenario windows: SaMD 2027-07-28 → 2028-01-28 ✓; hardware 2028-07-28 → 2030-01-28 ✓; acquisition = SaMD window ✓.
- Watch flags (2025-01-28 → 2026-01-28, 8 clearances): exactly K251640, K251636, K243855, all `software`, **0 ai-predictive** ✓.
- Quarterly all/software/ai series: every point matches `data.json` exactly (ai line flat zero) ✓.

**Alternative-basis probes (as tasked):**

- **A-005 band edges**: SaMD fast edge beats the config anchor by +11.1 mo, slow edge by +5.1 mo — the "an entrant could clear first" verdict survives **both** ends of the band. The reported 5-month figure is the *minimum* beat; the verdict is conservative in that direction.
- **Launch-anchor readings**: start of 2028-H2 (2028-07-01, as configured) vs end (2028-12-31): under the end reading the SaMD entrant beats us by 11–17 mo — main verdict *strengthens*. **BUT** the hardware scenario flips: its fast edge (2028-07-28) misses the config anchor by only **27 days**, and under the end-of-H2 reading it *beats* our launch by ~5 months. The report's "clears after our launch anchor" reassurance (report.md L24/L28) holds only under the favorable anchor reading and by less than one month — the margin is never stated.
- **Anchor provenance**: `our_launch_period: 2028-H2` exists **only in commercial.yml** — `commercial-strategy.md` D-COMM-1.4 commits F6 to "Y3 (2028)" with no half-year granularity (grep of the strategy doc finds no "H2"). Under a plain "2028" reading with an early-2028 launch, the "even the SLOW end lands ~5 months before us" claim shrinks toward zero (slow edge 2028-01-28 vs launch 2028-01-01 ≈ beaten by <1 month, i.e. effectively a wash), though the fast SaMD edge (2027-07-28) beats any 2028 launch date. Verdict direction survives; magnitude is config-sensitive.

### BQ-14 — CONFIRMED

Recomputed the full parity matrix from the features snapshot per the plan's committed rules:

- 10 attributes scored: **2 ahead** (flow_accuracy 0.35 vs best 2.3; battery 150 vs best 72 — range "48-72" correctly scored at the competitor-favorable end), **4 parity** (ders provisional, pca_mode, predictive_monitoring, remote_update), **4 behind** (integrated_etco2→F6, pca_pause_or_etco2→F4, wireless provisional→F2, weight_kg 0.75 vs 0.45 → **silently unaddressed**, correctly the only unmapped behind-gap) ✓. Competitor "shipping" counts (7 ders / 6 wireless / 3 pca_mode / 1 etco2 / 1 pca_pause / 0 predictive) all reproduce ✓. dose_personalization correctly reported as no-data, unscored ✓.
- **Verify-cell exclusion probe (as tasked)**: the snapshot has exactly 3 `verify` cells (Spectrum IQ ders, Spectrum IQ wireless, B.Braun wireless). Dropping them entirely: ders still parity (6 verified shippers remain), wireless still behind (4 verified shippers remain). **No verdict flips; 2/4/4 counts unchanged.** The "provisional" labels are conservative — the verdicts do not actually depend on the unverified cells.

### BQ-15 — CONFIRMED

- Margins from **verified-only** cells (every accuracy/battery competitor cell used is `verified: yes` — the 3 verify cells are capability cells not touching the differentiators): accuracy 2.3/0.35 = **6.57 → 6.6x** ✓ (note: best is a BD/Baxter tie at 2.3, report names BD only — cosmetic); battery 150/72 = **2.08 → 2.1x** ✓ (competitor-favorable range ends: CADD Legacy 72, B.Braun 13). Documented-cell counts (4 accuracy / 5 battery) ✓; absence lists ✓.
- since-doc-count: 0 decisions after 2026-04-12 ✓ (snapshot coverage ends 2026-01-28 — the vacuity of this zero is plainly stated in the verdict and R1, which is the honest framing); trailing context 8 ✓; quarterly series exact ✓.
- **Refresh-trigger re-derivation**: (a) no margin eroded — both ahead; (b) 0 predictive_monitoring rows read `yes`; (c) doc age at snapshot acquisition = 2026-04-12 → 2026-07-22 = **101 days** < 365. No trigger → "ride"; next review = anchor + 12 mo = **2027-04-12** ✓. Rule applied exactly as committed in the plan.

### BQ-16 — CONFIRMED (exact reproduction)

Recounted directly from the register snapshot CSV (38 rows):

- Evidence census: **38/38 `advisory-board`, 0 interview/survey/publication** — meta-gap verified ✓. Single date 2026-06-04 across all rows (history correctly "unavailable") ✓.
- Voices per feature: F1:5, F2:3, F3:3, F4:6, F5:4, F6:5, F7:5, F8:6, **F9:1** — all ✓. E-16.1 verdict not-met (F9) ✓.
- Sentiment mixes match `data.json` cell-for-cell; concern-majority per the plan's rule (concern > support+neutral): F4, F6, F7, F8, F9 — wave-check flags exactly F4/F6/F7/F8 (F9 excluded as Y5) ✓.

### BQ-17 — CONFIRMED-WITH-CAVEAT

- **Attach rate**: 39 active-subscribed connected sites ÷ 46 connected fleet sites = **84.78 → 84.8%** ✓ (42 subs rows, 3 churned; all 39 active sites are connected). Cumulative gross-adds history matches point-for-point ✓.
- **Sentiment axis** independently re-derived from the register: (support−concern)/voices rescaled — F1/F2/F3 0.5, F4/F6/F7/F8/F9 0.0, F5 0.875 ✓.
- **Pressure axis** re-derived per the plan's committed rules: F4 1.0, F6 1.0 (verified behind-gaps), F2 0.5 (behind-but-planned), F1 0.5 (trailing-12-mo lane keyword hits K251640/K251636/K243855 — exactly the three reported), F3/F5/F7/F8/F9 0.0 (Curlin "Ambulatory" clearances fall before the window — checked) ✓.
- **Composite** = unweighted mean reproduces all nine values (0.616/0.616/0.449/0.616/0.574/0.616/0.0/0.283/0.0) ✓. Candidates: pull-forward F4 (tie with F6 → earliest wave 2027) ✓; kill F9 (tie with F7 → fewest voices 1 vs 5) ✓. Ties and tie-breaks reported, never silent — as the plan requires ✓.
- **Weight-perturbation probe (as tasked)**: F4 and F6 have *identical axis vectors* (1, 0, 0.848) → their tie survives **any** weighting; the pull-forward choice between them is 100% tie-break (earliest wave), as reported. Kill side: F7 and F9 are identical (0, 0, 0) → bottom tie survives any weighting (F8 > 0 whenever the demand weight > 0); kill pick is 100% tie-break (voices). **However**, F4 vs F5: F4 wins iff w_pressure > 0.875 × w_sentiment; at equal weights the margin is 0.616 vs 0.574, and a ~3–4 pp shift of weight from pressure to sentiment (e.g. 0.30/0.37/0.33) flips the pull-forward candidate to **F5**. The report's W1 ("a different weighting can reorder candidates") is accurate but understates how small the flip distance is.
- **Robustness positive**: dropping the simulated sentiment axis entirely (mean of pressure + demand only) leaves BOTH picks unchanged (F4/F6 still top-tie at 0.924 → F4; F7/F9 still bottom-tie at 0.0 → F9). The assumption-class axis is not load-bearing for either candidate — only for F5's ranking. Neither report states this; it would *strengthen* the answer.

---

## Pass 2 — red-team findings

### RT-17.1 (HIGH) — BQ-17/BQ-16 + register: the F9 kill candidate's only sentiment input argues the opposite direction

Kuitunen (KOL-0004), the *single* voice on F9, says: "F9 (Y5, EU MDR) is **too late and too thin** … Start the EU clinical-evaluation and library-governance evidence in **Y1–Y2, not Y5**" (`kol-KOL-0004-kuitunen-sini.md` L38). The register encodes this as bare `concern`, which zeroes F9's sentiment axis and (with the by-construction zero demand and zero pressure) makes F9 the kill candidate — i.e. **a voice arguing for earlier, stronger investment is arithmetically converted into evidence for killing the bet**. The three-value sentiment vocabulary (`support|neutral|concern`) cannot carry the *direction* of a concern. R1/R2 caveat the thinness of the evidence but neither report states that the one existing voice's actual position contradicts the kill reading.
**Fix**: add a direction/conditionality dimension to the register (or a `stance` note column), and in BQ-17 name the F9 voice's actual position next to the kill candidate line. Minimum fix: one sentence in the report ("the single F9 voice argues the slot is too *late*, not that the bet is wrong").

### RT-16.1 (MEDIUM) — BQ-16: "sentiment challenges the wave slots" overreads condition-concerns as slot-challenges

Spot-checks of the concern rows behind the wave check: Giuliano's F4 row is "**Conditional** [support] — I will not endorse F4 until it carries a pre-specified suppressed-true-alarm bound" (kol-KOL-0001 L28/L44); Gorski (4 concern rows incl. F7) verdicts "**Conditional yes** — sequencing is right" and explicitly endorses deferring F7 to Y3–5 as "the correct instinct" (kol-KOL-0007 L14/L18/L45). The plan's wave-check gloss ("the panel's documented sentiment **disagrees with committing that wave as scheduled**") and the report's "challenges the wave slot" flags therefore mischaracterize at least F4 and F7: the panel challenges the *feature's readiness conditions*, not the *slot*. The mapping convention (conditional → concern) is documented in the dataset README and applied consistently — the loss happens at interpretation, not curation.
**Fix**: reword the wave-check claim to "concern-majority ≠ documented endorsement of the slot" (evidence-absence framing), or split sentiment into stance (support/conditional/oppose) × timing (earlier/as-scheduled/later).

### RT-13.1 (MEDIUM) — BQ-13: hardware-scenario reassurance is a 27-day margin on a config-only anchor

Two stacked fragilities, neither stated: (a) the hardware band's fast edge (2028-07-28) clears "after our launch anchor" by **27 days**; (b) the anchor itself (2028-H2 → 2028-07-01) has no basis outside `commercial.yml` — the strategy doc commits only "Y3 (2028)". Under the end-of-H2 reading the hardware scenario *beats* our launch by ~5 months. The main SaMD verdict is robust to all of this (it strengthens under every alternative), but line 24/28's "a hardware incumbent building in-house is not the fast threat" is presented with no margin qualifier.
**Fix**: state the fast-edge margin ("by <1 month under the favorable anchor reading") and cite the H2 refinement as a config choice lacking strategy-doc grounding (candidate for a challengeable-assumption note, like the BQ-15 cadence stand-in).

### RT-14.1 (MEDIUM) — BQ-14: the lane map lets F4/F6 "own" gaps they arguably don't close

`attribute_lane_map` routes `pca_pause_or_etco2 → F4` and `integrated_etco2 → F6`, so both behind-gaps read "gap on roadmap". But F4 is *Alerts Engine v1 — smart alarm filtering* (software) and F6 is *predictive monitoring* (SaMD): neither is a PCA-Pause hardware pause response nor a capnography module. BD's shipped capability may remain unanswered even after F4/F6 land, yet the report's headline structure ("3 behind-gaps have a roadmap lane") counts them as owned. Config-committed and cited, so the computation is faithful — the challenge is to the config itself (which the plan invites: "challenge the assumption").
**Fix**: annotate the lane map (or the report's routing column) to distinguish "lane closes the gap" from "lane responds to the gap with a different mechanism".

### RT-15.1 (LOW-MEDIUM) — BQ-15: accuracy margin mixes spec bases

Our 0.35 is the **laboratory** standard (unit column discloses "(laboratory)"; SOTA doc L62: "±0.35% accuracy laboratory standard, ±2.5% market standard"; the competitive assessment L14 quotes the portfolio at **±0.5% volumetric**). Competitor cells are nominal/field specs. On the volumetric basis the margin is ~**4.6x**, not 6.6x. "Ahead of every documented value" survives every internal basis; the headline multiple is basis-sensitive and the report doesn't flag it.
**Fix**: footnote the basis ("lab-spec vs competitor nominal specs; ~4.6x on the volumetric basis").

### RT-x (LOW / cosmetic / positive)

- **Truncations**: BQ-13 report L37 "Dose IQ Safety Softwar"; BQ-14 40-char cell truncations ("patient-controlled analges", "Fleet Management + drug-libr"). Cosmetic render-width artifact in an otherwise lint-clean report.
- **BQ-16 `sentiment-mix` series**: the primary `value` field silently duplicates the concern count (support/neutral/concern ride as extra fields) — a console chart plotting `value` would show concern counts under an unlabeled generic axis. Low chart-form risk.
- **Provisional-verdict laundering — NOT found** (checked as tasked): BQ-14 marks provisional verdicts in the matrix cells, in a dedicated bullet, and the plan defines the rule; BQ-15 reports verified-cell coverage per table. The one soft spot: BQ-14's headline "4 behind" counts the provisional wireless verdict without the qualifier — the detail is one line below.
- **Meta-gap propagation — verified everywhere** (checked as tasked): BQ-16 leads with it (verdict, then "Epistemic status FIRST" section); BQ-17 carries it in the verdict headline, the composite-table caveats, R1, and the plan. The register README's integrity note is the upstream anchor. No consumer of the register was found that omits it (README: consumed by BQ-16/BQ-17 only).
- **Decision-language discipline — pass**: BQ-17 says "Decision support, not the decision" in the verdict, "candidates … council judgment pending" as the section title, and the plan's Assertions & limits disclaims the decision. The verdict language nominates; it does not decide.
- **Chart-form abuse — none found**: BQ-14 parity-history and BQ-16 sentiment-history are marked `unavailable` rather than drawn from one point; BQ-17's gross-adds line discloses churn non-recording; BQ-13's flat ai-predictive zero line is the finding, stated as such.
- **Expectation gaming — none**: the only declared expectation (E-16.1) is evaluated honestly to not-met and additionally flagged `unvalidated` (basis is a stand-in). No expectations invented for the other BQs (matches catalog).
- **Assumed-class discipline (BQ-13 acquisition scenario) — pass**: `entry-scenarios` carries `evidence_class: assumed` with an explicit "modeled, not observed" provenance note; the verdict's own evidence class is `assumed`; R2 restates it.

---

## Data audit

### external-competitor-features @2026-07-27 — source_ref spot-checks (project-doc cells)

| Cell | Claimed source | Result |
|---|---|---|
| PP3500 battery_hours 150 | competitive-product-assessment.md | ✓ L14/L26/L45 "150+ hour battery life" |
| PP3500 weight_kg 0.75 | competitive-product-assessment.md | ✓ L23 "0.75 kg" |
| PP3500 flow_accuracy 0.35 (lab) | state-of-the-art-analysis.md | ✓ L14/L24/L62 "±0.35% … laboratory" (see RT-15.1 basis note) |
| PP3500 predictive "complete absence" | competitive-product-assessment.md | ✓ L16 verbatim phrase |
| PP3500 ders "200+ medications" | competitive-product-assessment.md | ✓ L47 |
| BD Alaris / Baxter Spectrum IQ flow 2.3 | competitive-product-assessment.md | ✓ L14 "(Alaris, Baxter Spectrum IQ at ±2.3%)" |
| BD Alaris PCA Pause + EtCO2 | state-of-the-art-analysis.md | ✓ L39 + table L52 |
| Alaris 6h / Sigma 4h / Plum 7h battery | state-of-the-art-analysis.md | ✓ table L46-48 (incl. rate qualifiers) |
| CADD Legacy 0.45 kg, 48-72h | competitive-product-assessment.md | ✓ L63 "450g, 2–3 day battery" |
| Plum 360 / B.Braun predictive "no (named reactive-alarm incumbent)" | commercial-strategy.md | ✓ L131 names all four incumbents on the reactive-alarm axis |

**Unconfirmable in this audit** (public-web cells; web fetch out of scope per tasking): Plum 360 MedNet "2500 drugs/40 care areas", CADD-Solis spec cells, B.Braun mfimedical cells, Novum IQ cells, and the 3 `verify`-flagged cells (2× Spectrum IQ, 1× B.Braun wireless) — the last three are already flagged in-dataset, which is the correct posture. No project-doc-cited cell failed the check.

**A-005 internal anchors**: median 213d / IQR 84–293 reproduces from the pinned snapshot (inclusive quantiles); the "$24M / 42-month" hardware upper-bound benchmark ✓ competitive-product-assessment.md L31. Web-sourced development-time estimates not checked (out of scope).

**Aside (not consumed by these BQs)**: competitive-product-assessment.md L16 gives the AI-device market CAGR as 35%; commercial-strategy.md L36 quotes the same $15.1B→$98.3B span at "~45% CAGR". One of the two is wrong — worth a corpus-level errata note.

### internal-kol-register @2026-07-27 — fidelity vs `docs/_analysis/pca-device/commercial-roadmap-kol-review/`

- Row inventory consistent with the README coverage table; all 38 rows date 2026-06-04 and cite per-KOL source docs that exist.
- Spot-checks: Giuliano F5 `support` ✓ faithful ("Like it"); Giuliano F4/F6/F7 `concern` — defensible readings of a "Conditional" verdict, but see RT-16.1 (conditional-support flattened to concern); Gorski F1/F2/F3/F7 `concern` vs her "Conditional yes — sequencing is right" ✓ consistent with the documented convention, same flattening; Kuitunen F9 `concern` — see RT-17.1 (direction inverted downstream). **No fabricated rows found; the mapping convention is applied consistently; the vocabulary itself is the defect.**

---

## Friction log

- The tasking said to expect `.2`-suffixed *editions*; in fact each BQ has a single `2026-07-27` edition — the `.2` suffix lives on a *snapshot* pin (`internal-subscriptions@2026-07-27.2`). Edition-vs-snapshot naming overload cost a few minutes of orientation.
- `quality.json` files are large (~6KB each); a `--summary` flag on the quality audit (or a compact `lint.status` rollup per edition) would help reviewers.
- BQ-17's pressure-axis rules live only in plans/BQ-17.md; `data.json`'s derivation method string ("mean(pressure, …) per plans/BQ-17.md") is honest but forces a plan read to re-derive pins-only. A machine-readable rule echo (e.g. the 1.0/0.5/0.0 rule table) in the derivation block would make the composite fully re-derivable from the edition folder alone.
- A-005 states an IQR without naming the quantile method (inclusive vs exclusive changes 84–293 to 79–353). Trivial here, but assumption records quoting order statistics should name the method.
- The report tables truncate long values at ~40 chars mid-word ("Softwar") — a renderer width setting, worth one fix in the module shared by all editions.
- Positive: the pins/data/report separation made pass-1 blinding genuinely workable — every headline number was re-derivable from the snapshot CSVs without touching module code.
