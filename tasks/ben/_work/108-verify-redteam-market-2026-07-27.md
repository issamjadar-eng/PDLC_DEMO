# Independent Verification + Red-Team Dossier — Market BQs (BQ-07..BQ-11), editions 2026-07-27

_Task ben/108 · 2026-07-27 · Pass 1 (adversarial re-derivation, pins-only) run before Pass 2 (red-team of reports/plans/modules/data). All recomputation done with throwaway scripts outside the repo against the pinned snapshots; no repo artifact modified except `quality.json` verification appends via `commercial.py record-verification`._

**Verdict summary**

| BQ | Pass-1 verdict | Pass-2 worst finding |
|---|---|---|
| BQ-07 | CONFIRMED | low (growth-rate basis mismatch, disclosed weakly) |
| BQ-08 | CONFIRMED-WITH-CAVEAT | medium (dollar-weighted win rate 42.9% not surfaced) |
| BQ-09 | CONFIRMED-WITH-CAVEAT | medium (hardcoded "decays" verdict; interior buckets are flat) |
| BQ-10 | CONFIRMED | low (missing demo banner; PCA-capital alternative basis) |
| BQ-11 | CONFIRMED | low ("median" is upper-middle element, not median) |

---

## BQ-07 — US PCA/smart-pump share range

**Pass-1 verdict: CONFIRMED.** Every headline figure reproduces exactly from `internal-sales-accounts@2026-07-27` + A-003:

- NA in-segment (PP3500+PP3000+IP5000) FY2026H1 units: **522** = 339 + 99 + 84 ✓ (FY2024 418, FY2025 485 ✓).
- Unit share vs A-003 1.1M–1.8M base: **0.029%–0.047%** ✓ (recomputed 0.0290 / 0.0475). FY trend rows ✓.
- Revenue share: FY2026H1 NA in-segment revenue $8,232,109 ×2 annualized = $16.46M vs $1.5B–$3.0B ⇒ **0.55%–1.1%** ✓. The ×2 annualization is explicitly labeled in the report table and Method section ✓.
- Growth: (522/418)^(1/1.5)−1 = **15.97%/yr ≈ 16.0%** ✓ vs A-003's 7.3% CAGR (transcribed correctly).

**Alternative bases tested**

- *Excluding IP5000* (PCA-only reading of "PCA/smart-pump"): 438 units ⇒ 0.024%–0.040%. Same order of magnitude; verdict robust. Including IP5000 is the CORRECT basis because A-003's denominator is LVP+PCA — numerator and denominator scopes match. ✓
- *Units vs dollars*: both are reported side by side and the stock-vs-flow distinction is explained in the report body ✓.
- *All-region vs NA*: all-region in-segment units = 1,052 (2× the NA numerator). Using them against a US denominator would double share; the report correctly restricts to NA and labels the US=NA proxy ✓.

**Pass-2 findings**

1. **(low) Growth-rate comparison is units-of-segment vs dollars-of-total-market.** Our 16.0%/yr is unit growth of our NA installed base; A-003's 7.3% CAGR is the *dollar* CAGR of the *total US infusion-pump market* (~$8.26B→$11.8B), not the LVP+PCA segment and not units. "Directionally gaining" survives (16 ≫ 7.3 under any deflator), but the report labels the 7.3% only as "assumed market" without the unit/dollar, segment/total mismatch. Fix: one clause in the growth bullet ("dollar CAGR of the total US infusion-pump market — not a unit-growth figure").
2. **(info) Honesty posture is exemplary**: share stated only as a range, A-003 LOW confidence in the verdict line, competitor unit split published as `unavailable` rather than guessed, denominator-constant simplification carried as R2.

---

## BQ-08 — Win/loss drivers, trailing 365d

**Pass-1 verdict: CONFIRMED-WITH-CAVEAT.** Exact reproduction from `internal-winloss@2026-07-27.2`:

- Window 2025-07-25→2026-07-25 (anchored at max close_date, per plan) ✓. Decided 73: **37W/36L = 50.7%**, 10 no-decision excluded ✓.
- PM-gap losses (primary OR cited): **11 of 36 = 30.6%**, value **$9,961,000**, primary-only 6 ✓.
- Loss-reason and win-reason tables reproduce row-for-row ✓ (price 12, PM-gap 6, features 5 …; contract-timing 15, features 7 …).

**Alternative bases tested (the caveat)**

- *No-decision counted as losses*: 37/83 = **44.6%** — below the 50% target. E-08.1 "met" flips on this basis. The report does disclose the exclusion in the verdict line and the target is defined on won+lost, so the stated basis is internally consistent — but the verdict's "met" is one denominator choice away from "not-met" and W1 only says "a handful of deals swings the verdict" (count-based), not that the denominator choice itself swings it.
- *Dollar-weighted win rate*: in-window won value $23.68M vs lost $31.55M ⇒ **42.9%** by value. We lose bigger deals than we win. Nowhere surfaced.
- *All-time*: 54/101 = 53.5% — trailing window is conservative vs all-time; no gaming. ✓
- *Window anchor* at snapshot date instead of max close_date: identical result (50.7%). ✓

**Pass-2 findings**

1. **(medium) Value-weighted view absent.** The question is revenue-flavored ("how many recent losses cite predictive monitoring" is answered in $), and the report already sums value for PM-gap losses — but the headline 50.7% is count-based while the dollar win rate is 42.9%. A one-line "by CRM value we win 42.9% of decided dollars" would prevent a rosier-than-dollars read. Fix: add value-weighted rate as a secondary stat or a Watch item.
2. **(low) E-08.1 met-by-0.7pp on a chosen denominator.** W1 covers fragility by deal count; add the ND-inclusive sensitivity (44.6%) so the reader sees the verdict is definition-sensitive, not just sample-sensitive.
3. **(info) Honest touches**: "recorded value, not win-probability-weighted" ✓; R2 correctly disclaims single-primary-reason CRM attribution; plan discloses the seeded ~45%/~30% knobs and correctly notes the window figure may differ.

---

## BQ-09 — Recall disruption window (real recalls × fabricated CRM)

**Pass-1 verdict: CONFIRMED-WITH-CAVEAT.** I re-ran the join independently from the raw pinned CSVs (alias map re-implemented from `entity-aliases.yml`, prefix/top-down/case-insensitive):

- Population: decided opps with competitor incumbent (excl. `PainEase`, `none`): 63; 8 no-decision excluded ✓ (report line matches).
- **In-window (180d, event_date_posted): n=54, 29 won = 53.7% ✓. Out: n=9, 2 won = 22.2% ✓.**
- Decay buckets ✓ exactly: 0-3mo 32→56.2%; 3-6mo 22→50.0%; 6-12mo 2→50.0%; >12mo 7→14.3%. (No opp has zero prior recalls, so the ">12 / no prior recall" merged label is vacuously harmless.)
- Recalls-by-incumbent since 2021 ✓ exactly (B.Braun 8, BD 16, Baxter 27, Fresenius 21, ICU 21, Smiths 18).
- Alias coverage ✓: all six CRM `incumbent_vendor` values canonicalize (incl. bare "BD" and "B.Braun"); unmatched recall firms are small non-incumbent players (Zyno 9, Avanos 5, …) — visible, not silently dropped.

**Alternative bases tested (the caveat)**

- *90-day window*: in n=32 **56.2%** vs out n=31 **41.9%** — the contrast collapses from 31.5pt to 14.3pt. The dramatic binary split at 180d is substantially an artifact of the window definition pushing 54 of 63 opps in-window, leaving 9 unusual deals as the "control".
- *365-day window*: in n=56 53.6% vs out n=7 14.3% — the control nearly vanishes.
- *event_date_initiated instead of posted*: in n=51 54.9% vs out n=12 25.0% — similar.
- *Open-status-only recalls*: identical (all joins hit currently-open postings).
- *Decay shape*: 56.2 / 50.0 / 50.0 / 14.3. The interior (3-12 months) is FLAT; the whole "decay" is the 0-3 bucket vs a 7-deal >12mo tail. "The win rate decays as months-since-recall grow" is at best weakly supported by the report's own table.

**Pass-2 findings**

1. **(medium) The "decays… real but finite" verdict text is hardcoded in `bq_modules/bq_09.py` (line ~99)** — it prints regardless of the computed bucket shape. On this snapshot the buckets don't actually decay across the interior (50.0% → 50.0%); a future snapshot with a rising profile would still get the "decays" verdict. Fix: derive the verdict phrase from the buckets (or soften to "0-3-month bucket wins at the highest rate; >12-month tail is far lower (small n)").
2. **(medium) Real×fabricated blending — the honesty box is adequate, but the effect is still manufactured and quotable.** The verdict leads with "Method demo (fabricated CRM…)", the honesty box is section one, and R1 states the seeded windows were set independently of the real recall calendar. That is genuinely good. Remaining hazard: the 53.7%-vs-22.2% pair with real firm names (Baxter 27 recalls, etc.) is the most screenshot-able artifact in the five reports, and every caveat lives outside the table. The winloss README shows the seeded truth: elevated wins were seeded for Baxter/ICU incumbents from 2025-07 — the "lift" the join finds is mostly the seed rediscovered through a recall calendar so dense it is near-always in-window. Fix: put "(demo of method, not market evidence)" in the split-table caption itself, not only the verdict/honesty box.
3. **(low) In/out split at 90d belongs in the report.** R2 says "narrow the window" as mitigation; the 90d numbers (56.2 vs 41.9) already exist in the data and would honestly deflate the binary contrast. Fix: add a one-row sensitivity note.
4. **(info) The "8 no-decision excluded" line, the zero-missing-posted-date line, and the alias-map citation all verified exactly.

---

## BQ-10 — 5-yr TCO vs Alaris / Spectrum IQ / Plum 360

**Pass-1 verdict: CONFIRMED.**

- Our TCO from `commercial.yml` constants: 4200 + 5×(450+310+180) = **$8,900** ✓; capital+service 4200+900 = **$5,100** ✓; component rows ✓.
- A-004 transcription faithful: capital $2.2k–$6.9k standalone / $4.4k–$13.7k networked, service $150–$250/yr, cap+svc 5-yr **~$3,000–$15,000** (arithmetic checks: 2200+750=2,950; 13,700+1,250=14,950 — the record's own rounding) ✓. No range narrowing anywhere; `bq_10.py` even asserts on the record's literal range strings so silent drift breaks the build (good control).
- Feature cells: all 18 populated cells match the pinned snapshot byte-for-byte, `verified: verify` carried as "(verify)" ✓; the two "—" cells (Spectrum IQ battery, Plum 360 flow accuracy) are genuinely absent from the snapshot — absence honest, not laundered ✓.

**Alternative bases tested**

- *Competitor software/consumables included*: impossible by construction (A-004 declares them undisclosed); crucially the direction of the omission is stated correctly and repeatedly — competitor true all-in sits ABOVE the quoted range, which biases *against* us claiming victory. No we-win claim is made. Conservative. ✓
- *Networked-capital-only basis* (arguably the right comparison for a connected PP3500): competitor cap+svc ≈ $5,150–$14,950 — our $5,100 sits at/below the floor. The report's use of the wider $3k floor (standalone/refurb anchors) makes US look worse, not better. Conservative direction again. ✓
- *(low) PCA-vs-PCA capital basis not examined*: A-004 carries PCA pumps $1.8k–$4.5k; PCA cap+svc ≈ $2.6k–$5.8k puts our $5,100 near the top of that band. The three named comparators are LVP platforms so the class-wide basis is defensible, but a PCA-basis sentence would pre-empt a hostile buyer running that math.

**Pass-2 findings**

1. **(low) Missing demo banner.** BQ-10 is the only one of the five reports without `_Demo sample data — not for clinical use._` (`bq_10.py` deliberately omits `C.BANNER`). The competitor side is real-compiled, but our four cost constants are, per the report's own R2, "demo stand-ins" — CLAUDE.md's demo-scope rule wants fabricated content marked. Fix: emit the banner or an equivalent "our constants are demo stand-ins" banner line at top.
2. **(info) Verdict language capped at "indicative, assumption-bounded" exactly as the plan commits; ranges-overlap/no-we-win is honored; TCO history published as `unavailable` rather than a faked trend.**

---

## BQ-11 — Sold-but-underused connected sites

**Pass-1 verdict: CONFIRMED.** From `internal-telemetry-utilization@2026-07-27` + `internal-fleet@2026-07-22`:

- Trailing-3-months window 2026-05..07, hours-weighted site utilization <60%: exactly **6 sites** with exactly the reported values — S-NA-13 34.0% (5 dev), S-NA-22 35.3% (19), S-NA-03 36.4% (8), S-NA-16 36.5% (5), S-EMEA-02 36.6% (16), S-APAC-06 37.0% (6) ✓. Material (≥10 connected devices): **S-NA-22, S-EMEA-02** ✓. E-11.1 not-met ✓.
- Regional revenue context (APAC $4,898,604 / EMEA $7,039,112 / NA $13,187,364) ✓ exactly; the extra `internal-sales-accounts` pin is properly declared.
- Telemetry↔fleet reconciliation: 331 telemetry devices = 331 connected fleet devices, zero orphans either way ✓.

**Alternative bases tested — verdict fully robust**

- *Device-level aggregation* (mean of per-device ratios): identical six sites, identical order, values within 0.1pp.
- *1-month window* (2026-07 only) and *6-month full span*: same six sites, same two material, no additions/removals.
- *Threshold sensitivity*: zero sites between 60% and 70% — the seeded data is bimodal (flagged ~34-37%, rest ≥85.7%), so the 60% knob has enormous slack. (This also means the analysis has never been stress-tested by a borderline site — a real deployment will not be this clean.)

**Pass-2 findings**

1. **(low) "Median" is not a median.** `bq_11.py:123` (and the monthly line at ~174) computes `sorted(vals)[len(vals)//2]` — the upper-middle element. With 46 sites (even count) the true median is 89.6%, reported 89.7%; monthly gaps reach 0.8pp (2026-05: 91.3% vs true 90.5%). No verdict impact whatsoever, but the label "median" is technically wrong on even-count populations. Fix: `statistics.median()`.
2. **(info) Honest handling of the blocked account join**: the question's core ask (account revenue at risk) is answered "NOT COMPUTABLE" with the missing key named, an `unavailable` series published, E-11.1 explicitly downgraded to a site-level proxy, and regional revenue labeled "context, explicitly not attribution". Exactly right.
3. **(info) expected_hours-is-a-norm caveat (R2) is present and correctly placed.**

---

## Data audit — the four datasets behind these BQs

### commercial/internal-winloss (@2026-07-27.2)

- README vs snapshot: 120 opps ✓, close 2025-01-06..2026-07-25 ✓, seed-42 generator declared ✓, real-competitor-names-in-fabricated-records disclosure ✓, schema columns match `dataset.yml` exactly ✓.
- Seeded knobs disclosed and re-measured: overall win rate 45.0% (54/120) ✓; PM-gap in 29.8% of 47 all-time losses (14/47) ✓; disruption knob — Baxter/ICU-incumbent opps closing ≥2025-07-01 elevated ✓.
- **(low) README knob rates use an undeclared denominator.** "win at 65.6% (21/32) vs 37.5% for everything else" counts *no-decision opps in the denominator* (21/32 and 33/88). On the decided-only basis used everywhere else in this program the same knob is 70.0% (21/30) vs 46.5% (33/71). Fix: state "of all outcomes incl. no-decision" or restate decided-only.
- The `.2` snapshot's changelog honestly records the same-day knob fix (supersedes 2026-07-27) ✓.

### commercial/internal-telemetry-utilization (@2026-07-27)

- README vs snapshot: 1,986 rows = 331 devices × 6 months ✓; expected-hours norms present as claimed (400/480/450/280) ✓; knob list matches measurement exactly — the six seeded sites and their full-span utilizations (34.9–37.1%) reproduce to the decimal ✓; "everything else 85.7–97.0% site-level" ✓ (measured identical).
- Knob disclosure quality: exemplary — the README names the exact sites, the draw range (25-48% of norm), and the ≥5-device pick rule.
- Note (info): seeded data is bimodal with a 48-point gap between flagged and healthy sites; BQ-11's threshold robustness is a property of the seed, not of the method.

### commercial/internal-sales-accounts (@2026-07-27)

- README vs snapshot: 554 rows ✓, 39 accounts ✓, schema matches ✓; FY2026H1 units by line (PP3500 686 / PP3000 198 / cloud-suite 331 all-region) ✓; concentration knobs re-measured — Meridian Health Alliance 38.4% of FY2025 revenue ✓, top-3 accounts 25.5% (largest 11.0%) ✓.
- (info) The `independent` bucket is the largest "gpo" value at 48.9% of FY2025 revenue; the README's "top GPO 38.4%" is correct only because `independent` is not a GPO — the README does say all EMEA/APAC buy independent, so this is disclosed, but a BQ-02 reader should keep it in mind.
- Reconciliation claims vs internal-financials are asserted with measured numbers in the README (±0.9% worst) — not re-verified here (outside the five target BQs' pin set).

### commercial/external-competitor-features (@2026-07-27)

- README vs snapshot: 42 rows ✓; curated.csv→snapshot model ✓; `verified: verify` rows are exactly the three the README names (Spectrum IQ DERS + wireless, Infusomat wireless) ✓; deliberate-absence list spot-checked (Spectrum IQ battery, Plum 360 flow accuracy absent as declared) ✓.
- **source_ref spot-checks (4 project-doc rows, all confirmed):**
  - PP3500 `flow_accuracy_pct` 0.35 → `state-of-the-art-analysis.md` carries "±0.35% accuracy … laboratory" ✓ (and the README explicitly discloses the tension with comp-assessment's ±0.5% volumetric — carried honestly).
  - PP3500 `battery_hours` 150 → `competitive-product-assessment.md` carries "150+ hour battery life" ✓ (matrix drops the "+"; immaterial).
  - Alaris `battery_hours` 6 → SOTA doc table carries "6 hr at 25 mL/hr" ✓ (matrix value loses the at-25mL/hr condition — worth carrying in the value string).
  - Spectrum IQ `flow_accuracy_pct` 2.3 → comp-assessment carries "Baxter Spectrum IQ at ±2.3%" ✓.
- **(info / not confirmable here) public-web rows** (e.g., Plum 360 MedNet "up to 2500 drugs / 40 care areas" → pattersonvet.com; Infusomat ±5% → mfimedical.com) are marked `verified: yes` but could not be independently confirmed in this audit (no web fetch). Not flagged as wrong — flagged as untested by this pass; the dataset's own "verify before external use" usage-rights note covers this.
- B.Braun ±0.1%-vs-±5% source conflict is disclosed in the README with the public value winning ✓ — the right call, documented.

---

## Cross-cutting observations

1. **Lint is green everywhere and yet the interesting findings are all denominator/framing issues** — exactly the documented lesson ("correct-but-misleading denominators pass lint"). The marker system verified 100%: every number I chased resolved to its pin, assumption, config, or series.
2. **No assumption-range laundering found.** A-003 and A-004 ranges appear verbatim wherever cited; `bq_10.py` mechanically asserts on A-004's literal strings — a pattern worth copying into bq_07 for A-003.
3. **Evidence-class honesty is real**: assumed-denominator results carry `assumed` (BQ-07, BQ-10 verdicts), joins carry `derived`, and the two `unavailable` series (competitor unit split, TCO history, account-revenue-at-risk) are published as gaps instead of estimates.
4. **Hardcoded narrative strings in modules are the main structural risk** (BQ-09 "decays"; BQ-10's overlap sentence is similarly static but currently true by arithmetic). Verdict prose that encodes a data-shape claim should be derived from the data.

## Friction log

- `record-verification --help` is discoverable and free-text verdicts are accepted; fine. But the verdict vocabulary (CONFIRMED / CONFIRMED-WITH-CAVEAT / REFUTED) is convention, not schema — a `choices=` on `--verdict` per type would keep filings comparable across agents.
- Pins-only Pass 1 works well, with one wrinkle: BQ-09's population rule ("exclude `none` incumbents") lives in the *plan*, not in `data.json` — a strict pins-only re-derivation first produced out-of-window n=21 vs the report's 9 and could not tell whether that was a bug or a definition gap without opening the plan (deferred to Pass 2 by the protocol). `data.json` derivation.method strings should carry population exclusions, not just the join sketch.
- The winloss `2026-07-27` vs `2026-07-27.2` double-snapshot day worked as designed (pins disambiguate), but `edition.yml` YAML-parses `2026-07-27.2` as a float-ish scalar (unquoted) while `pins.json` quotes it — cosmetic inconsistency that a strict YAML loader could mangle.
- The telemetry README's knob list measuring full-span (6-month) utilizations while BQ-11 reports 3-month-window values (e.g., S-NA-22: 35.6% vs 35.3%) is fine but initially confusing — the README could label the knob measurements with their window.
- `bq_11.py`'s median-by-index (`sorted[n//2]`) appears twice; a shared `C.median()` helper would have prevented it.
