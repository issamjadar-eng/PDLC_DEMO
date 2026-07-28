# Independent verification + red-team dossier — BQ-01..BQ-05, editions 2026-07-27

_Demo sample data — not for clinical use._

**Scope**: Two-pass independent audit of the five board-category business-question answer
editions (`docs/project/commercial/reports/BQ-0N/2026-07-27/`). Pass 1 re-derived every
headline figure from the pinned corpus snapshots with throwaway scripts written outside
the repo (OS tmp), before opening any report.md or bq_module. Pass 2 red-teamed the
framing (reports, plans, quality.json, modules) and the underlying board-category
datasets (internal-financials, internal-revenue-plan, internal-sales-accounts,
internal-subscriptions, internal-fleet).

**By**: independent verify agent · **Task**: ben/108 · **Date**: 2026-07-27

## Plain-language summary

This is an independent double-check of the five board-level business answers (funding
map, customer concentration, recurring-revenue mix, plan credibility, and launch-slip
exposure). An independent checker recomputed every published number from scratch, using
only the raw pinned data files — without looking at the published reports or the programs
that produced them — and then compared results. Every published figure reproduced exactly;
no number was wrong. The checker then attacked the framing and found 14 concerns about how
the correct numbers are presented: 1 moderate (a guardrail about customer concentration is
tested against a revenue base covering only about half of total revenue, and the verdict
could flip on the fuller base) and 13 minor (sentences a skimming reader could take the
wrong way, "measured" labels on figures that are really calculations, and rounding
presented as exactly zero). Seven further notes were positive — places where the reports
were unusually honest about their own limits. All the concerns were subsequently corrected
in the published answers the same day, and each affected answer's quality record carries
the ACTIONED entries documenting what was changed (the fifth answer, BQ-05, had nothing to
correct).

## Terms used

- **Pins-only re-derivation** — recomputing every published number from the raw, dated
  data files alone, without reading the report or its code, so agreement is independent
  confirmation rather than circular checking.
- **Basis sensitivity** — testing whether a conclusion still holds when a defensible
  alternative definition (a different window, population, or measure) is used.
- **Denominator** — the "out of what" in any percentage; many concerns here are about
  which denominator a rate is computed against.
- **CONFIRMED-WITH-CAVEAT** — the numbers reproduce exactly, but the verdict depends on a
  definitional choice the reader should know about.

**Verdict summary**

| BQ | Pass 1 (adversarial re-derivation) | Pass 2 (red-team) | Most serious finding |
|---|---|---|---|
| BQ-01 | CONFIRMED | CONFIRMED-WITH-CAVEAT | Headline parenthetical invites misreading ($45.2M is portfolio GM, not the pair's $27.0M) |
| BQ-02 | CONFIRMED-WITH-CAVEAT | CONFIRMED-WITH-CAVEAT | E-02.1 "annual revenue" guardrail verdict is basis-sensitive: tested on a denominator covering ~51% of revenue |
| BQ-03 | CONFIRMED | CONFIRMED-WITH-CAVEAT | Blended 60% aspiration understates the recurring-specific bet (87.5% of the cloud-suite FY2030 line is behind FDA) |
| BQ-04 | CONFIRMED | CONFIRMED-WITH-CAVEAT | E-04.2 fails by 0.8pp, within sampling noise of the stand-in 5% line (n=39, σ≈2.5) |
| BQ-05 | CONFIRMED | CONFIRMED | None above low; slip and exposure arithmetic exact under all tested bases |

---

## BQ-01 — Funding map (internal-financials@2026-07-27)

### Pass 1 — re-derived numbers

All figures recomputed from `internal-financials/snapshots/2026-07-27/normalized/records.csv`
(480 rows, 2024-Q1..2026-Q2), window 2025-Q3..2026-Q2:

| Claim (published) | Re-derived | Match |
|---|---|---|
| PP3500+cloud-suite = 59.7% of trailing-4Q GM | 59.754% (pair GM $27.00M / total $45.18M) | ✔ |
| Totals $45.2M GM on $88.2M revenue (51.2%) | $45.18M / $88.21M = 51.2% | ✔ |
| Per-line table (rev, GM, GM%, share, drift) | PP3500 40.9/20.3/49.5/44.8; cloud 8.6/6.7/78.0/14.9; PP3000 13.2/6.0/45.3/13.2; SP6000 10.1/4.9/49.1/10.9; IP5000 8.3/3.8/45.9/8.5; SP6500 7.0/3.4/48.9/7.6 | ✔ all |
| Margins compressing on IP5000, PP3000 | IP5000 47.4%→45.9% (−1.5); PP3000 46.8%→45.3% (−1.5); other four flat | ✔ |
| E-01.1 all lines GM-positive, thinnest PP3000 45.3% | confirmed | ✔ |

**Alternative bases tested**: (a) pair share of *revenue* = 56.2% (vs 59.7% of GM) — the
plan commits to the GM-dollar basis explicitly, and the conclusion (these two lines fund
the company) holds on either basis; (b) latest-quarter-only GM% ranks identically. Basis
choice does not change the verdict. **Pass-1 verdict: CONFIRMED.**

### Pass 2 — findings

| Sev | Passage / element | Objection | Suggested fix |
|---|---|---|---|
| low | Verdict line: "59.7% of trailing-4Q gross margin ($45.2M on $88.2M revenue…)" | The parenthetical binds visually to the pair, but $45.2M is the *portfolio* GM; the pair's GM is $27.0M. A skimming board reader takes away "the pair earns $45.2M". | Reword: "…59.7% of trailing-4Q gross margin ($27.0M of the portfolio's $45.2M GM on $88.2M revenue)". |
| low | data.json `gm-by-line`, `totals-stat` → `evidence_class: measured` | These series carry GM$, GM%, share-of-GM, drift — arithmetic derivations, not ledger fields; siblings `gm-share`/`gm-trend` are correctly `derived`, and the report itself cites `[derived: gm-by-line]`. Honesty-label inconsistency (measured-that-is-really-derived). | Mark the series `derived` with a derivation block, or split measured columns (revenue, cogs) from derived ones. |
| low | "GM % vs prior 4Q: +0.0 pts" (4 lines) | Rounded-to-zero drift is presented as exactly flat. | Render "±0.0" as "<0.1" or one decimal more. |
| info | Opex gap (W1, Data gap section) | Correctly stated, not papered over — "consumes the company" is scoped to GM level. Positive control. | — |

---

## BQ-02 — Concentration (internal-sales-accounts@2026-07-27, internal-revenue-plan@2026-07-27)

### Pass 1 — re-derived numbers

| Claim (published) | Re-derived | Match |
|---|---|---|
| Meridian 38.4% of FY2025 direct book | $15.63M / $40.70M = 38.4% | ✔ |
| GPO table (independent 48.9 / Cascadia 6.9 / AtlasPoint 3.3 / NovaBridge 2.4) | 48.9 / 6.9 / 3.3 / 2.4 | ✔ |
| Top-3 accounts 25.5% (Northgate 11.0, Clearwater 8.0, Redwing 6.5) | 25.5% ($4.47M/$3.26M/$2.64M) | ✔ |
| PCA franchise 74.5%; pumps alone 58.8% | 74.5% / 58.8% | ✔ |
| Dent $15.6M constant; 14.9% of FY2026 plan, declining to 4.5% FY2030 | 15.63/105.0 = 14.9%; 12.0/9.2/6.4/4.5% | ✔ |

**Alternative bases tested**: the direct book ($40.7M) covers only **50.6%** of total
CY2025 revenue ($80.5M, from internal-financials). Meridian's share of *total* annual
revenue is bounded below at **19.4%** (if it takes none of the distributor-routed
consumables/service book) and is unknowable above that from the pinned data. Under the
total-revenue basis the E-02.1 guardrail ("no GPO > 30% of **annual revenue**") would be
**met** at the floor — the basis choice can flip the expectation verdict. The published
figures are arithmetically exact and the direct-book basis is stated on the shares, but
the verdict's basis sensitivity is not itself stated. **Pass-1 verdict:
CONFIRMED-WITH-CAVEAT.**

### Pass 2 — findings

| Sev | Passage / element | Objection | Suggested fix |
|---|---|---|---|
| med | E-02.1 row: "No single GPO carries more than 30% of annual revenue … not-met" | Expectation text says *annual revenue*; the test denominator is the direct book (~51% of revenue). "Not-met" against the stated wording overclaims: on total revenue the verdict ranges met→unknown. The report states the basis and the data gap but never says the *verdict* flips with basis. | Reword the expectation in commercial.yml to "annual direct-book revenue", or add an explicit caveat: "on total revenue Meridian is ≥19.4% (floor, distributor book unattributed) — guardrail verdict is basis-dependent". |
| low | Verdict line: "top-3 accounts 25.5%, PCA franchise 74.5%" | Only the Meridian figure carries the "direct-book" qualifier in the headline; the following figures inherit it implicitly. | Qualify once for all: "…of FY2025 direct-book revenue: Meridian 38.4% ⚠, top-3 accounts 25.5%, PCA franchise 74.5%". |
| low | GPO table row "independent … 48.9%" | Half the direct book is GPO-unaffiliated (all EMEA/APAC per the dataset README). Correctly excluded from anchor selection per the plan, but a 49% "independent" bucket deserves a Watch of its own (channel-mix explanation), else the table's largest row goes unexplained. | Add a one-line note: independent = all EMEA/APAC accounts (dataset construction). |
| info | Constant-dent scenario | Floor semantics honestly flagged (R2) and dent direction conservative both ways. Positive control. | — |

---

## BQ-03 — Recurring mix vs Y5 (internal-financials@2026-07-27, internal-revenue-plan@2026-07-27)

### Pass 1 — re-derived numbers

| Claim (published) | Re-derived | Match |
|---|---|---|
| Recurring share FY2024 5.0 / FY2025 7.9 / FY2026H1 10.8% | 5.0 / 7.9 / 10.8 (subscription ÷ total) | ✔ |
| FY totals $69.9M / $80.5M / $46.3M; subscription $3.5M / $6.4M / $5.0M | matched | ✔ |
| Plan proxy shares 12.4 / 19.2 / 35.3 / 53.1 / 68.6% | 13/105, 25/130, 60/170, 130/245, 240/350 | ✔ |
| FY2030 decomposition 128 / 12 / 210 ($M), 210 = 60.0% | cleared 128, LTF 12, pccp 140 + new-sub 70 | ✔ |
| Plan FY2030 total vs catalog constant delta $0.0M | 350.0 vs 350.0 | ✔ |
| E-03.1 strictly increasing | 5.0 < 7.9 < 10.8 | ✔ |

**Alternative bases tested**: (a) trailing-4Q recurring share = 9.8% vs the H1 10.8% —
still strictly above FY2025, verdict unchanged; the report never annualizes H1 (checked:
annualized subscription $10.0M vs FY2026 cloud-suite plan $13.0M — actuals run *below*
plan, consistent with the stated "plan is a stretch"); (b) recurring = subscription +
service would read 26.1% today — a definitional change, and the plan-side proxy is
subscription-only, so the published subscription-only basis is the consistent one.
**Pass-1 verdict: CONFIRMED.**

### Pass 2 — findings

| Sev | Passage / element | Objection | Suggested fix |
|---|---|---|---|
| med-low | "of the $350.0M target, $128.0M rides on already-cleared products…" | The decomposition blends all six lines, but the question is about the *recurring* target. The recurring proxy itself (cloud-suite FY2030 $240M) splits $30M cleared / $0M LTF / $210M dependent — **87.5%** of the recurring bet is behind FDA decisions. The blended 60% *understates* the risk on the very revenue the question is about. (Arithmetic verified from the pinned plan.) | Add one line: "within the $240M recurring proxy, $210M (87.5%) is aspiration — the cleared bucket is mostly device hardware." |
| low | Lint warning on L40 ("modeled" bucket label without [assume:]) | Already surfaced by the lint as a warning and not suppressed — the word is a bucket name, not an estimate. Acceptable, but it will re-fire every edition. | Rename the bucket label ("execution-dependent") or attach a waiver/assumption record. |
| info | "contracted (upper bound — cleared today, not contractually committed)" | Honest upper-bound labeling directly in the table row. Positive control. | — |

---

## BQ-04 — Subscription unit economics (internal-subscriptions@2026-07-27.2, internal-fleet@2026-07-22)

### Pass 1 — re-derived numbers

| Claim (published) | Re-derived | Match |
|---|---|---|
| 39 active sites, 295 pumps; 3 churned (7.1%) | 39 / 295 / 3 of 42 | ✔ |
| ARR $447 /pump/yr; cost $544 /pump/yr | $447.42 / $543.97 (raw sums $131,989 / $160,470) | ✔ |
| LTV $2,235 vs $2,720; ratio 0.82 vs 3.0 floor | $2,237 vs $2,720 raw (report multiplies rounded rates); ratio 0.8225 → 0.82 | ✔ (rounding chain, immaterial) |
| 28 of 39 sites ARR < cost, concentrated in small | 28/39; small band 24/24 below, mid 4/6, large 0/9 | ✔ |
| Band table (24/92/453/913; 6/47/452/516; 9/156/443/334) | matched | ✔ |
| Mean hw discount 5.8% (active) | 5.75% unweighted; 5.68% pump-weighted; 5.88% incl. churned | ✔ under all bases |
| Fleet context: 331 connected; attach gap = S-NA-21, S-EMEA-08, S-EMEA-13, S-APAC-08 | 331; same 4 sites | ✔ |

**Alternative bases tested**: (a) **churn factored** — 3/42 register churn with mean
active tenure 1.7y means any churn decrement *lowers* LTV below $2,235; the published
no-churn choice flatters the metric and it still fails at 0.82, so the not-met verdict
is robust in the conservative direction (and the report says exactly this, R1/W2);
(b) discount incl. churned sites 5.88%, pump-weighted 5.68% — E-04.2 fails under every
mean tested. **Pass-1 verdict: CONFIRMED.**

### Pass 2 — findings

| Sev | Passage / element | Objection | Suggested fix |
|---|---|---|---|
| low | E-04.2 "5.8% vs the 5% tolerance — not-met" | The miss is 0.8pp on an n=39 mean whose generator knob is gauss(μ=6, σ=2.5) — SE ≈ 0.4pp, so the verdict sits ~2 SE from the stand-in line. Labeled unvalidated, but a near-threshold flag would prevent over-reading a knife-edge failure. | Add a sensitivity note ("within ~1pp of the tolerance; verdict fragile to the stand-in threshold choice"). |
| low | Ratio/LTV computed from rounded per-pump rates (bq_04.py L34-38) | 447/544 vs raw 131,989/160,470 gives 0.82 either way here, but computing on pre-rounded intermediates is the pattern that flips verdicts at thresholds. | Compute ratio on raw sums; round only for display. |
| low | "cannibalization" section title vs content | Section is titled "Hardware-discount signal (cannibalization)" while the text correctly disclaims causality. Title alone leaks the causal frame. | Retitle "Hardware-discount signal (no causal baseline)". |
| info | 5-year horizon framing | The horizon cancels in the ratio (plan states this); the $2,235-vs-$2,720 pair is presentational. Fine as stated. | — |

---

## BQ-05 — Plan revenue behind FDA decisions (internal-revenue-plan@2026-07-27, openfda-510k-infusion@2026-07-22)

### Pass 1 — re-derived numbers

| Claim (published) | Re-derived | Match |
|---|---|---|
| $366.0M of $1,000.0M dependent (pccp-enabled + new-submission) | 0+11+40+105+210 = $366M; plan total $1,000.0M | ✔ |
| Exposure 0.0 / 8.5 / 23.5 / 42.9 / 60.0%; over 40% in FY2029, FY2030 | matched exactly | ✔ |
| Dependency table (all 20 cells) | matched (incl. FY2026 = 103 cleared + 2 LTF) | ✔ |
| 6-mo slip 105/124.5/155.5/212.5/297.5, shortfall $105M | matched (M/12 roll-forward verified cell by cell) | ✔ |
| 12-mo slip 105/119/141/180/245, shortfall $210M | matched | ✔ |
| Median FRN 510(k) review 213 days, 29 clearances since 2021 | median 213 (n=29, decisions 2021–2026; mean 261, max 1079) | ✔ |

**Alternative bases tested**: including letter-to-file as "dependent" gives 1.9 / 11.5 /
28.2 / 46.9 / 63.4% — the same two years breach the 40% line and FY2028 stays under; the
five-year aggregate moves 36.6% → 40.2%, but the guardrail is per-year and the report
makes no aggregate-compliance claim. Basis choice does not change the verdict, and the
LTF exclusion is argued (needs no FDA decision) in both plan and report. **Pass-1
verdict: CONFIRMED.**

### Pass 2 — findings

| Sev | Passage / element | Objection | Suggested fix |
|---|---|---|---|
| low | "median FRN … 213 days" (W1, context stat) | Distribution is heavily right-skewed (mean 261, max 1,079 days). Median is the right robust choice and is named, but the slip scenarios (6/12 months) sit inside the tail the median hides — a 1,079-day outlier is ~3× the 12-month slip. | Add the p75 or max alongside the median ("213 median, tail to 1,079"). |
| low | FRN stat scope | Computed on *cleared* 510(k)s only — withdrawn/NSE submissions are absent from the openFDA clearance file, so the interval is survivorship-biased low. The report scopes it ("traditional/special … only") but doesn't name the survivorship. | One clause: "cleared submissions only — abandoned/NSE reviews not counted". |
| info | Real-vs-fabricated blending | Handled correctly: top-of-report banner splits fabricated plan from real openFDA data; no our-vs-market claim made. Positive control. | — |

---

## Data audit — board-category datasets

Every quantitative claim in the five dataset READMEs was checked against the pinned
snapshot; all verified: financials (FY2025 $80.5M, subscription 7.9%, PP3500 $34.0M,
cloud-suite $6.4M), revenue-plan (totals 105/130/170/245/350; FY2028 cloud-suite $40M of
$60M behind future events; FY2030 210 = 140+70), sales-accounts (39 accounts, 38.4%
Meridian, 25.5% top-3, reconciliation figures), subscriptions (26 small sites all
negative, 30/42 net-negative, median cost/pump $971 small vs $343 large, churned =
S-NA-01/04/11, mean discount 5.9% all-rows), fleet (884 devices, 48 sites, 331 connected,
PP3500-only connectivity).

| Sev | Element | Finding | Suggested fix |
|---|---|---|---|
| med-low | `internal-fleet/dataset.yml` schema | Declares 7 columns but `records.csv` carries 8 — **`hw_rev` is undeclared** (present between `region` and `firmware_version`). Any schema-driven validation is blind to it. | Add `{name: hw_rev, type: str, required: true}` to the columns list. |
| low | accounts↔financials reconciliation | FY2026H1 account book ($25.13M) **exceeds** the financials hardware+subscription ledger ($24.90M) by +0.9%. Within the stated ±5% contract, but in a real system attributed revenue ⊆ ledger total — the sign is impossible, not just noisy. FY2024 −0.4%, FY2025 +0.1%. | Constrain the generator noise so the account book never exceeds the ledger, or note the direction in the README contract. |
| low | subscriptions↔fleet churn semantics | The 3 churned subscription sites still show connected devices in the fleet registry. Plausible (connectivity ≠ entitlement) but unstated; BQ-29's attach-gap denominator excludes them because they have register rows — churned-but-connected sites are arguably attach-gap too. | State the churned-but-connected convention in the subscriptions README; revisit in BQ-29's plan. |
| info | subscriptions@2026-07-27.2 vs fleet@2026-07-22 | Cross-pin reconciliation is *exact* (42/42 site counts match, 0 mismatches) despite 5-day pin skew — by construction (shared seeded model). Fine for demo; declared in both READMEs. | — |
| info | fleet `max_age_days: 7`, pin age 5 at edition time | The BQ-04 edition's freshness margin was 2 days at generation; the approval gate will trip quickly. Expected behavior, worth knowing at approval time. | — |

---

## Friction log

Battle-testing notes on the corpus + commercial skills from this run:

1. **`evidence_class: measured` on derived aggregates goes un-linted.** BQ-01
   `gm-by-line`/`totals-stat` and BQ-02 `concentration-stat`/`top-accounts` carry
   `measured` while containing shares, margins, and drifts; the lint's series-hygiene
   check accepted them. A check flagging a "measured" series whose values are arithmetic
   combinations (or that the report itself cites as `[derived: …]`) would close the
   honesty-label gap.
2. **Basis-sensitivity is invisible to the claim lint** — as the project's documented
   lesson predicts. BQ-02's guardrail verdict flips with the denominator (direct book vs
   total revenue) and passes lint cleanly. A "denominator coverage" declaration per
   expectation (what fraction of the natural universe the test denominator covers) would
   make this auditable mechanically.
3. **`available: true` alongside `evidence_class: unavailable`** (opex-by-line,
   econ-history, exposure-history) is confusing at first read; the stated-gap pattern is
   excellent, but the two flags look contradictory in data.json.
4. **README "measured on snapshot" knob sections are a verification gift** — every
   dataset README stated its seeded knobs with measured values, which made the data audit
   fast and falsifiable. Keep this convention.
5. **Bucket-name "modeled" trips the estimation-language lint every edition** (BQ-03
   warning). The lint is doing its job, but a persistent warning that will never be fixed
   trains readers to ignore warnings; a waiver or rename is preferable.
6. **`record-verification` CLI** was clean (`--help` accurate, `--edition` required);
   no friction.
7. **Rounding-chain pattern in modules** (round-then-compute, bq_04 ratio) is benign
   here but is the class of bug that flips a verdict at a threshold; a convention
   "compute on raw sums, round for display" in the module template would prevent it.

## Changelog

- 2026-07-27: Created — two-pass independent verification + red-team of BQ-01..BQ-05
  2026-07-27 editions (task ben/108).
