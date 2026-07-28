# Code review — board analysis modules (BQ-01 to BQ-05), 2026-07-27

_Demo sample data — not for clinical use._

**What was reviewed**: the five Python programs that compute the board-level business
answers — which product lines fund the company (BQ-01), customer concentration (BQ-02),
recurring-revenue mix (BQ-03), subscription unit economics (BQ-04), and how much of the
revenue plan depends on pending FDA decisions (BQ-05).

- **Artifacts**: `docs/project/commercial/bq_modules/bq_01.py` … `bq_05.py`, reviewed
  against their committed analysis plans (`docs/project/commercial/plans/BQ-01.md` …
  `BQ-05.md`) and the shared helpers in `docs/project/commercial/computations.py`
- **Reviewer**: AI code reviewer (read-only review; task ben/108)
- **Date**: 2026-07-27
- **Verdict in one line**: all five programs follow their committed plans and no published
  number was wrong; 29 issues were raised (1 serious, 8 moderate, 20 minor) and **all 29
  have since been fixed** — each fix re-verified in the current code before this report
  was written.

## Plain-language summary

This is a code review of the five programs that produce the board-level business answers.
The reviewer checked each program against its written analysis plan and against the
project's known failure patterns. The arithmetic was found correct and each program does
what its plan commits to — no number published today was wrong. The review raised 29
issues — one serious, eight moderate, twenty minor — almost all of the form "this will
quietly become wrong the next time the data changes," rather than "this is wrong now."
The serious one was a verdict sentence that declared a risk threshold breached as fixed
text, so a future data refresh could have printed a wrong verdict. All 29 issues have
since been fixed, and each fix was independently confirmed present in the current code.

## What we checked

- Does each program's arithmetic match what its written analysis plan commits to?
- Are the verdict sentences computed from the data, or typed in as fixed text that could
  silently become false on a data refresh?
- Is rounding applied only when displaying numbers, never before comparing them to
  decision thresholds?
- What happens on a future data refresh — new categories, missing periods, empty data:
  does the program fail loudly, report the gap, or silently produce a wrong answer?
- Are thresholds and rosters read from the configuration file, or buried in the code
  where nobody audits them?
- Do the programs produce identical output on identical input (no clocks, no randomness)?
- Were the fixes promised by the earlier output-level review actually implemented?

## Findings

All resolutions below were verified against the current code on 2026-07-27. Line
references live in the technical appendix.

### F-1 (medium) — The "all six lines profitable" sentence had the number typed in (bq_01.py, funding map)

- **What's wrong:** the verdict said "all six lines gross-margin positive" with "six"
  written as fixed text, while the list of product lines is read from the data. A data
  refresh that adds a seventh line would print a wrong count in the board verdict.
- **Why it matters:** the verdict is the single sentence the board reads; a silently
  wrong count there undermines trust in every number below it.
- **Resolution:** FIXED — the sentence now derives the count from the data
  (`len(lines_all)`), so it can never disagree with the table it summarizes.

### F-2 (low) — The funders' combined share was a sum of already-rounded shares (bq_01.py)

- **What's wrong:** the two funding lines' combined share of gross margin was computed by
  adding two individually rounded percentages (59.7 shown vs 59.8 true), instead of
  computing the share once from the raw totals.
- **Why it matters:** a 0.1-point display drift today; the pattern is what flips verdicts
  when a number sits near a threshold.
- **Resolution:** FIXED — the share is now computed from the raw summed gross margin
  and rounded once for display (`C.pct(pair_gm, total_gm)`).

### F-3 (low) — Margin drift was compared to its threshold after rounding (bq_01.py)

- **What's wrong:** the "margins compressing" flag compared a difference of two rounded
  percentages against the threshold — double rounding can flip the flag at the boundary.
- **Why it matters:** knife-edge risk: rounding, not the data, would decide the verdict.
- **Resolution:** FIXED — the drift is now computed from unrounded fractions and
  compared raw; rounding happens only in the displayed cell.

### F-4 (low) — The compression threshold was a bare number in the code (bq_01.py)

- **What's wrong:** the −1.0-point "compressing" cutoff existed only as a constant in the
  code — committed in neither the plan nor the configuration, so nobody audits it.
- **Why it matters:** an un-audited number silently controls which lines get flagged to
  the board.
- **Resolution:** FIXED — the threshold now lives in the question's configuration
  (`gm_compression_threshold_pts` in `commercial.yml`) and is read at run time.

### F-5 (low) — A short data history silently produced a partial comparison window (bq_01.py)

- **What's wrong:** with fewer than eight quarters on file, the "prior four quarters"
  comparison window silently shrank or emptied, and drift was computed against it anyway.
- **Why it matters:** a drift figure against a partial baseline looks authoritative but
  is not comparable.
- **Resolution:** FIXED — a guard now detects the incomplete prior window; drift is
  reported "n/a" with an explicit warning line in the report instead of being computed
  against partial data.

### F-6 (high) — The verdict declared "above the guardrail" as fixed text (bq_02.py, concentration)

- **What's wrong:** the headline asserted the anchor buying group is "above the 30%
  guardrail" as a typed sentence, not a computed comparison. On a refresh where the share
  drops below the guardrail, the pass/fail row would flip to "met" while the verdict
  sentence still declared a breach — a self-contradicting report.
- **Why it matters:** this is the concentration verdict the board acts on; a wrong breach
  claim is the most damaging kind of error this report can make.
- **Resolution:** FIXED — the sentence now branches on the computed raw share
  ("above"/"under"), and the floor-of-total clause gained the matching conditional.

### F-7 (medium) — The product-family roster was typed into two sentences (bq_02.py)

- **What's wrong:** the report asserted "PCA franchise (PP3500 + PP3000 + cloud-suite)"
  as fixed text while the actual roster comes from configuration, and the pumps-only
  figure used a product list hardcoded in the code. A configuration change would make the
  sentence lie and the pumps figure go stale.
- **Why it matters:** the words and the numbers could describe two different rosters.
- **Resolution:** FIXED — both sentences now interpolate the configured lists, and
  the pump roster moved to a new configuration entry (`pca_pump_lines`).

### F-8 (low) — Guardrail comparisons ran on rounded percentages (bq_02.py)

- **What's wrong:** every share-versus-guardrail test (anchor share, floor share,
  per-group warning flags) compared rounded values — a knife-edge at exactly 30.0.
- **Why it matters:** rounding, not data, would decide a breach at the boundary.
- **Resolution:** FIXED — a raw-share helper now feeds every comparison; rounded
  values are display-only.

### F-9 (low) — The top-3 accounts' share summed three rounded shares (bq_02.py)

- **What's wrong:** same class as F-2: the combined share added three individually
  rounded percentages instead of computing one share from the summed revenue.
- **Why it matters:** small display drift; threshold-flip pattern.
- **Resolution:** FIXED — the share is computed once from the summed top-3 revenue.

### F-10 (low) — The "compounds the concentration" trigger was an unaudited number (bq_02.py)

- **What's wrong:** the narrative line about account concentration appeared only when the
  top-3 share exceeded 25% — a number committed in neither the plan nor the configuration.
- **Why it matters:** an invisible number decided whether a risk paragraph exists.
- **Resolution:** FIXED — the gate moved to configuration
  (`top3_narrative_gate_pct`) and is compared on the raw share.

### F-11 (low) — Plan rows outside the known window vanished silently (bq_02.py)

- **What's wrong:** revenue-plan rows for years outside the five known plan years were
  silently dropped, so a refreshed plan with an extra year would quietly understate the
  loss-scenario table.
- **Why it matters:** silent data loss in a board scenario table.
- **Resolution:** FIXED — out-of-window rows are now counted, a warning is printed at
  run time, and the report carries a visible caution line when any are excluded.

### F-12 (medium) — The half-year label only worked for exactly two quarters (bq_03.py, recurring mix)

- **What's wrong:** the current fiscal year was labeled "H1" only when exactly two
  quarters were on file; with one or three quarters it rendered as a full year while a
  fixed sentence still claimed "a half-year of actuals" — both label and prose would rot
  on the next quarterly refresh.
- **Why it matters:** a mislabeled partial year invites annualization mistakes by readers.
- **Resolution:** FIXED — any 1–3-quarter year now gets a generic partial-year label
  ("(Q1–Qn)"), and the disclosure sentence branches on the actual quarter count,
  including in the chart legend.

### F-13 (medium) — "The cleared cushion **mostly** sits outside the recurring story" was narrated (bq_03.py)

- **What's wrong:** "mostly" was typed text — true today at 77%, but the sentence would
  persist unchanged even if the underlying share dropped below half.
- **Why it matters:** a qualitative word carrying a quantitative claim, with nothing
  keeping them aligned.
- **Resolution:** FIXED — the share is now computed and the qualifier branches on it
  ("mostly" / "partly" / "entirely inside"), with the percentage printed beside it.

### F-14 (medium) — An unrecognized plan category crashed the computation (bq_03.py)

- **What's wrong:** a new value in the plan's regulatory-dependency column raised an
  error and blocked the whole refresh, because the bucket dictionaries were pre-seeded
  with only the four known categories.
- **Why it matters:** a loud crash beats a wrong number, but it still blocks the answer
  on an otherwise-valid refresh.
- **Resolution:** FIXED — unknown categories now collect into a visible
  "unclassified" bucket with a run-time warning, a flagged table row, and an explicit
  caution not to trust the decomposition until the mapping is extended.

### F-15 (low) — The "strictly increasing" test ran on rounded shares (bq_03.py)

- **What's wrong:** the pass/fail check that recurring share rises every year compared
  rounded values — two years at 7.94% and 7.90% both display 7.9 and would flip the
  verdict.
- **Why it matters:** the check's whole point is small year-over-year differences.
- **Resolution:** FIXED — the test now compares unrounded fractions.

### F-16 (low) — A 40% narrative gate coincided with another module's threshold but was not linked (bq_03.py)

- **What's wrong:** the "aspiration revenue" risk paragraph fired above a bare 40 in the
  code — numerically equal to BQ-05's configured exposure threshold, but not connected to
  it, so changing one would silently desynchronize the two answers.
- **Why it matters:** two reports describing the same risk with different thresholds.
- **Resolution:** FIXED — the module now reads BQ-05's configured
  `exposure_threshold_pct` and compares on the raw share.

### F-17 (low) — "Spans all six lines" had the count typed in (bq_03.py)

- **What's wrong:** same class as F-1 — a line count written as text.
- **Why it matters:** rots silently when the portfolio changes.
- **Resolution:** FIXED — the count is computed from the distinct product lines in
  the plan data. Because the sentence now carries a computed figure, a data-source marker
  was added to the line in a post-lint follow-up (the claim lint requires every
  figure-bearing line to cite its source).

### F-18 (low) — Plan rows outside the window vanished silently (bq_03.py)

- **What's wrong:** same class as F-11, in the recurring-mix module.
- **Why it matters:** silent data loss in the plan trajectory and the target
  decomposition on a refreshed plan.
- **Resolution:** FIXED — counted, warned at run time, and disclosed in the report.

### F-19 (medium) — "Concentrated in small sites" was narrated (bq_04.py, unit economics)

- **What's wrong:** the failing-economics headline hardcoded "— concentrated in small
  sites —". True today (24 of 28 loss-making sites are small), but a refresh where
  mid-size sites dominate would keep emitting it.
- **Why it matters:** the phrase steers the remediation (small-site policy) — pointing it
  at the wrong band would misdirect real work.
- **Resolution:** FIXED — the program now finds which size band holds the majority of
  loss-making sites and names it; if no band holds a strict majority it says "spread
  across the size bands".

### F-20 (medium) — Unrecognized subscription statuses silently vanished from the rates (bq_04.py)

- **What's wrong:** the code recognized only "active" and "churned"; a new register
  status (say, "suspended") would silently drop those sites from both the economics rates
  and the churn count while other totals still included them.
- **Why it matters:** silent exclusion skews the unit-economics verdict with no signal.
- **Resolution:** FIXED — rows with any other status are now counted, a run-time
  warning names the unrecognized values, and the report carries a visible caution line
  when any exist.

### F-21 (low) — "About 2 standard errors" was asserted as fixed text (bq_04.py)

- **What's wrong:** the knife-edge disclosure always said the discount miss is "≈2
  standard errors" from the threshold, but the flag can also fire on the
  within-1-point rule where the true multiple is different — the prose could disagree
  with the computed condition.
- **Why it matters:** the disclosure exists to be precise about fragility; imprecise
  fragility language defeats it.
- **Resolution:** FIXED — the program now computes the actual standard-error multiple
  and names which condition fired, and interpolates both into the watch item, the report,
  and the expectations row.

### F-22 (low) — A data label documented only half of the knife-edge rule (bq_04.py)

- **What's wrong:** the machine-readable data point was labeled "knife-edge (|miss| <= 2
  SE)", omitting the within-1-point branch of the actual rule.
- **Why it matters:** the label misdocuments the computed flag for downstream consumers.
- **Resolution:** FIXED — the label now reads "knife-edge (|miss| <= 1pp or <= 2 SE)".

### F-23 (low) — Zero active sites would crash the history build (bq_04.py)

- **What's wrong:** with no active subscription sites, the revenue-history builder
  crashed on an empty list instead of degrading gracefully.
- **Why it matters:** a refresh edge case would block the whole answer.
- **Resolution:** FIXED — the history build is guarded; with no active sites the
  series is published as "unavailable" with an explanatory note.

### F-24 (medium) — A new dependency category crashed the exposure table (bq_05.py, FDA-dependency)

- **What's wrong:** same class as F-14, plus the table's columns were hardcoded to the
  four known categories — a fifth tag in a refreshed plan raised an error.
- **Why it matters:** blocks the refresh; and hardcoded columns could never show new
  categories even if the crash were fixed.
- **Resolution:** FIXED — table columns are now derived from the observed categories
  plus the known ones; unknown tags get their own visible column, a run-time warning, and
  are deliberately NOT counted as FDA-dependent until classified in configuration.

### F-25 (low) — "Since 2021" was typed into three places (bq_05.py)

- **What's wrong:** the FDA-clearance context stat asserted "since 2021" as fixed text in
  the watch item, the report, and a data label — a re-acquired snapshot with a different
  start date would silently falsify all three.
- **Why it matters:** a dataset-scope fact should come from the dataset.
- **Resolution:** FIXED (with one deliberate deviation) — the year is now derived from
  the earliest **decision date** in the pinned records rather than the earliest
  **received date** the review suggested. The sentence reads "clearances since YYYY", and
  a clearance is dated by its decision, so the decision year is the semantically correct
  anchor; both derivations retire the typed literal.

### F-26 (low) — "On the order of the smaller slip scenario" was a narrated comparison (bq_05.py)

- **What's wrong:** the sentence compared the median FDA review cycle to the smaller slip
  scenario in words, without computing either side, and assumed the first configured slip
  was the smaller one.
- **Why it matters:** a comparison in prose with no arithmetic behind it.
- **Resolution:** FIXED — the watch item now interpolates both computed figures (the
  median review days and the smallest slip converted to days, via `min(slips)`); the
  vague comparative was dropped.

### F-27 (low) — The exposure breach test ran on rounded percentages (bq_05.py)

- **What's wrong:** same class as F-3/F-8: the over-threshold test compared the rounded
  exposure — a knife-edge at exactly 40.0.
- **Why it matters:** for a year sitting at the line, rounding — not the data — would
  decide whether the exposure verdict flags it.
- **Resolution:** FIXED — breach tests and the peak-year pick now use raw fractions;
  rounded values are display-only.

### F-28 (low) — An empty FDA snapshot would print "runs None days" (bq_05.py)

- **What's wrong:** with no dated records, the median helper returns "nothing", and the
  report would render the literal word "None" inside a sentence.
- **Why it matters:** garbled output where an honest "unavailable" belongs.
- **Resolution:** FIXED — a guard now routes the empty case to explicit
  "unavailable" branches in the watch item, the report section, and the data series.

### F-29 (low) — Plan rows outside the window vanished silently (bq_05.py)

- **What's wrong:** same class as F-11/F-18, in the exposure module.
- **Why it matters:** silent data loss in the exposure table on a refreshed plan.
- **Resolution:** FIXED — counted, warned at run time, and disclosed in the report.

## Terms used

- **Narrated, not computed** — a sentence typed as fixed text rather than derived from
  the data, so it can silently become false when the data changes.
- **Knife-edge** — a value sitting so close to a threshold that rounding decides the
  verdict.
- **Raw-then-round** — the convention that comparisons run on unrounded values and
  rounding happens only when displaying; violating it creates knife-edges.
- **Pinned snapshot (pin)** — the frozen copy of a dataset an answer is computed from, so
  the same answer is reproducible later.
- **Magic constant** — a number that controls behavior but lives only in the code, where
  neither the plan nor the configuration commits to it.
- **Guardrail / threshold** — a configured limit that turns a measured number into a
  pass/fail verdict.
- **Plan conformance** — whether the program implements exactly the definitions committed
  in its written analysis plan (`plans/BQ-0N.md`).
- **Headline / verdict** — the one-sentence answer at the top of each generated report.

## Technical appendix

### Relationship to the prior output-level dossier

`tasks/ben/_work/108-verify-redteam-board-2026-07-27.md` findings were already
dispositioned; ACTIONED entries exist in each edition's `quality.json` for the BQ-01
verdict-parenthetical restructure, BQ-02 basis-sensitivity disclosure, BQ-03
recurring-specific decomposition, and BQ-04 knife-edge + raw-sums rounding. All four were
verified implemented in code by this review. Prior low notes with no ACTIONED record
(BQ-01 "+0.0 pts" rendering, BQ-04 section title, BQ-05 median tail/survivorship clauses)
were treated as accepted dispositions and not re-flagged.

### Cross-module pattern (one root cause, several findings)

`C.pct()` rounds to one decimal; four of the five modules originally compared thresholds
against its output. BQ-04's plan committed "compute on raw, round for display" and its
module already honored it. Resolution of the class: `computations.py` now exports
`pct_raw()` as the compare-side helper (raw fraction × 100), `pct()` is documented as
render-side only, and every board-module threshold compare was moved to raw values
(F-3, F-8, F-15, F-27).

### Per-module verification detail

Fix locations verified in the current working tree, 2026-07-27 (line numbers refer to
the post-fix modules).

**bq_01.py — funding map · review verdict APPROVED-WITH-FINDINGS.** Plan conformance:
conforms (trailing-4Q window anchored in-data, GM basis, funds/consumes rule E-01.1,
top-N + "other" trend, quarter→ISO mapping). Prior fixes verified: headline
parenthetical binds pair GM vs portfolio GM distinctly; `gm-by-line`/`totals-stat` are
`derived` with derivation chains.

| ID | Sev | Fix location | Mechanism |
|---|---|---|---|
| F-1 | med | L87–89 | `len(negatives)` / `len(lines_all)` interpolated |
| F-2 | low | L74–76 | `funders_share = C.pct(pair_gm, total_gm)` |
| F-3 | low | L52–56, L62–66, L79–81 | `gm_pct_raw` fields; compare `delta_raw <= comp_thr` |
| F-4 | low | L30 | `comp_thr = float(p["gm_compression_threshold_pts"])` |
| F-5 | low | L34–37, L62–69, L164–173 | `prior_ok` guard; "n/a" drift cell + ⚠ report line |

**bq_02.py — concentration · review verdict CHANGES-REQUIRED.** Plan conformance:
conforms, incl. the committed basis-sensitivity disclosure in all three promised places
plus the R3 narrative risk; anchor excludes `independent`; constant-dent floor scenario.

| ID | Sev | Fix location | Mechanism |
|---|---|---|---|
| F-6 | high | L73, L125–131 | `direct_breaches` on raw share; "above"/"under" branch; floor clause conditional |
| F-7 | med | L53–54, L88–92, L255–256 | `pca_lines` / `pump_lines` from config, `' + '.join(...)` interpolated |
| F-8 | low | L70–75, L113, L221 | `_raw_share()` feeds every guardrail compare + ⚠ flags |
| F-9 | low | L83–85 | `top3_share = C.pct(top3_rev, total)` on summed revenue |
| F-10 | low | L55, L149 | `top3_gate_pct` param; compared on `top3_share_raw` |
| F-11 | low | L28–40, L117–120, L270–276 | `unmatched` counter; stderr warning; ⚠ report line |

**bq_03.py — recurring mix · review verdict APPROVED-WITH-FINDINGS.** Plan conformance:
conforms (recurring = subscription only; cloud-suite proxy with both error directions;
three-bucket decomposition per committed mapping; Y5 delta reported not smoothed). Prior
fix verified: recurring-specific decomposition (blended AND within-proxy) implemented.

| ID | Sev | Fix location | Mechanism |
|---|---|---|---|
| F-12 | med | L42–55, L203–216, L324–327 | `n_last_q`-driven labels + conditional disclosure + legend |
| F-13 | med | L122–130, L285–288 | `cushion_clause` branch on `nonproxy_share_raw` (>50 / >0 / else) |
| F-14 | med | L58–96, L258–269 | `unknown_tags` set; unclassified bucket + warnings + ⚠ row |
| F-15 | low | L132–135 | `shares_raw` strict-increase on raw fractions |
| F-16 | low | L155–158 | `C.params_for("BQ-05")["exposure_threshold_pct"]`, raw compare |
| F-17 | low | L275–277 | computed distinct-line count, `[src:]` marker added post-lint |
| F-18 | low | L67–71, L89–91, L236–242 | `plan_unmatched` counter + warning + ⚠ report line |

**bq_04.py — subscription unit economics · review verdict APPROVED-WITH-FINDINGS.**
Plan conformance: conforms (active-only rates with churned surfaced W2; raw-sums rounding
convention; committed threshold-sensitivity disclosure; size bands from config; attach
gap per plan definition; survivor-biased ARR build stated).

| ID | Sev | Fix location | Mechanism |
|---|---|---|---|
| F-19 | med | L132–143 | `worst_neg_band` via strict-majority test; else "spread across the size bands" |
| F-20 | med | L33–41, L247–250 | `other_status` roster; stderr warning; ⚠ report line |
| F-21 | low | L96–104, L203–215, L274–280 | `disc_fired` condition names + `disc_n_se` interpolated |
| F-22 | low | L345 | label now names both branches: within 1pp or within 2 SE |
| F-23 | low | L113–130, L355–369 | `if starts:` guard; unavailable-series branch |

**bq_05.py — plan behind FDA decisions · review verdict APPROVED-WITH-FINDINGS.** Plan
conformance: conforms fully (dependent set from `dependent_categories`; per-year exposure
vs threshold; uniform-slip M/12 roll-forward with past-window truncation; median via
shared helper, public-context scope; exposure history honestly `unavailable`).

| ID | Sev | Fix location | Mechanism |
|---|---|---|---|
| F-24 | med | L39–60, L173–174, L183–191 | `dep_cols = DEP_ORDER + observed`; own column; warning; not counted dependent |
| F-25 | low | L87–94, L138, L228, L302 | `earliest_yr = min(dec_dates)[:4]` — decision-date basis (deliberate deviation from the proposed received-date basis; see F-25) |
| F-26 | low | L96–97, L137–141 | `min_slip_days = round(min(slips) * 365 / 12)`; both figures interpolated |
| F-27 | low | L64–67, L99, L178 | `expo_raw` dict feeds breaches, ⚠ flags, and peak pick |
| F-28 | low | L93–98, L135–147, L225–239, L296–309 | `med_ok` guard; unavailable branches in watch/report/series |
| F-29 | low | L47–56, L192–198 | `plan_unmatched` counter + warning + ⚠ report line |

### Review-wide observations

- No string-literal *values* (numbers, IDs) were found in any module — every figure is
  computed from pins/params. The residual class was **sentence logic** (hardcoded
  qualifiers/counts) — now retired across all five modules.
- Determinism is clean across all five: no clocks or randomness; all set/dict iteration
  feeding output is sorted or insertion-deterministic.

```json
{"reviews": [
  {"path": "bq_modules/bq_01.py", "verdict": "APPROVED-WITH-FINDINGS",
   "summary": "Plan-conformant; prior fixes verified; hardcoded 'six lines' count and rounded-compare hygiene remain.",
   "findings": [
     {"severity": "med", "summary": "Headline literal 'all six lines' - count asserted, not len(lines_all); rots on new line", "disposition": "fixed: headline interpolates len(negatives)/len(lines_all)"},
     {"severity": "low", "summary": "funders_share sums rounded shares (59.7 vs 59.8 raw-basis); violates raw-then-round", "disposition": "fixed: C.pct(pair_gm, total_gm) on raw sums"},
     {"severity": "low", "summary": "GM% drift computed/compared on rounded pcts vs -1.0 threshold; knife-edge flips", "disposition": "fixed: gm_pct_raw fields; delta compared raw, rounded for display"},
     {"severity": "low", "summary": "Compressing threshold -1.0pt is a bare code constant absent from plan/params", "disposition": "fixed: gm_compression_threshold_pts read from commercial.yml params"},
     {"severity": "low", "summary": "prior window periods[-8:-4] silently partial/empty when <8 periods on file", "disposition": "fixed: prior_ok guard; drift n/a + warning line when prior window incomplete"}
   ]},
  {"path": "bq_modules/bq_02.py", "verdict": "CHANGES-REQUIRED",
   "summary": "Basis-sensitivity disclosure correctly implemented, but headline hardcodes 'above the guardrail' unconditionally.",
   "findings": [
     {"severity": "high", "summary": "Headline asserts 'above the 30% guardrail' as string literal, not conditioned; wrong verdict if anchor drops", "disposition": "fixed: above/under branch on direct_breaches (raw share vs thr); floor clause conditional"},
     {"severity": "med", "summary": "'PP3500 + PP3000 + cloud-suite' literal + hardcoded pumps tuple; rots if franchise config changes", "disposition": "fixed: pca_franchise_lines/pca_pump_lines interpolated from config"},
     {"severity": "low", "summary": "Guardrail comparisons on C.pct-rounded values (anchor, floor, per-GPO flags)", "disposition": "fixed: _raw_share() feeds all guardrail compares"},
     {"severity": "low", "summary": "top3_share sums rounded shares instead of share of summed revenue", "disposition": "fixed: C.pct(sum(top3 values), total)"},
     {"severity": "low", "summary": "Narrative gate top3_share > 25 is a magic constant in neither plan nor params", "disposition": "fixed: top3_narrative_gate_pct param, compared raw"},
     {"severity": "low", "summary": "PLAN_YEARS hardcoded; unknown plan periods silently dropped", "disposition": "fixed: unmatched rows counted, stderr warning + report caution line"}
   ]},
  {"path": "bq_modules/bq_03.py", "verdict": "APPROVED-WITH-FINDINGS",
   "summary": "Recurring-specific decomposition correctly implemented; H1 labeling and 'mostly' qualifier are refresh-fragile.",
   "findings": [
     {"severity": "med", "summary": "H1 label only when exactly 2 quarters; static 'half-year of actuals' prose rots at 1 or 3 quarters", "disposition": "fixed: generic partial-year label (Q1-Qn) + disclosure branches on quarter count"},
     {"severity": "med", "summary": "'cleared cushion mostly sits outside recurring' - 'mostly' narrated, not computed (77% today)", "disposition": "fixed: cushion_clause computed from raw non-proxy share (mostly/partly/entirely)"},
     {"severity": "med", "summary": "New regulatory_dependency value raises KeyError (DEP_ORDER pre-seeded dicts); crash on refresh", "disposition": "fixed: unknown tags -> reported 'unclassified' bucket + warnings + flagged table row"},
     {"severity": "low", "summary": "E-03.1 strict-increase tested on rounded shares; ties at 1dp flip verdict", "disposition": "fixed: strict-increase on raw rec/tot fractions"},
     {"severity": "low", "summary": "Narrative gate asp_share > 40 magic constant, unlinked to BQ-05 exposure threshold", "disposition": "fixed: reads BQ-05 exposure_threshold_pct from config, raw compare"},
     {"severity": "low", "summary": "'spans all six lines' hardcoded count in report prose", "disposition": "fixed: distinct-line count computed from plan data; src marker added post-lint"},
     {"severity": "low", "summary": "PLAN_YEARS hardcode + silent continue on unknown periods", "disposition": "fixed: unmatched counter + warning + report caution line"}
   ]},
  {"path": "bq_modules/bq_04.py", "verdict": "APPROVED-WITH-FINDINGS",
   "summary": "Committed raw-sums rounding and knife-edge disclosure implemented correctly; two narrated/status-set frailties remain.",
   "findings": [
     {"severity": "med", "summary": "Headline hardcodes 'concentrated in small sites' - qualifier narrated, not computed from band split", "disposition": "fixed: strict-majority band computed; names band or 'spread across the size bands'"},
     {"severity": "med", "summary": "Status set {active,churned} hardcoded; new status silently drops sites from rates and churn count", "disposition": "fixed: other_status counted, stderr warning + report caution line"},
     {"severity": "low", "summary": "Knife-edge prose asserts '~2 standard errors' statically; 1pp branch can fire at other SE multiples", "disposition": "fixed: disc_fired names the condition(s); actual SE multiple (disc_n_se) interpolated"},
     {"severity": "low", "summary": "data.json knife-edge label omits the 1pp branch of the actual rule", "disposition": "fixed: label 'knife-edge (|miss| <= 1pp or <= 2 SE)'"},
     {"severity": "low", "summary": "starts[0] IndexError when zero active sites (ARR-build history)", "disposition": "fixed: empty-actives guard; series published unavailable with note"}
   ]},
  {"path": "bq_modules/bq_05.py", "verdict": "APPROVED-WITH-FINDINGS",
   "summary": "Slip/exposure arithmetic exactly per plan; 'since 2021' literals and dependency-tag KeyError are the residual risks.",
   "findings": [
     {"severity": "med", "summary": "New regulatory_dependency value raises KeyError; table columns hardcoded to four known tags", "disposition": "fixed: columns = DEP_ORDER + observed tags; unknown tags own column, warned, not counted dependent"},
     {"severity": "low", "summary": "'since 2021' string literal in W1, report, data.json label; rots if acquisition window changes", "disposition": "fixed (deviation): year derived from min(decision_date) rather than the proposed min(date_received) - decision year matches 'clearances since'"},
     {"severity": "low", "summary": "'on the order of the smaller slip scenario' narrated comparative; assumes slips[0] smallest", "disposition": "fixed: median days and min(slips)-in-days both computed and interpolated; comparative dropped"},
     {"severity": "low", "summary": "Breach test expo[y] > thr on rounded pct; knife-edge at 40.0", "disposition": "fixed: expo_raw feeds breach tests, flags, and peak pick"},
     {"severity": "low", "summary": "Empty/dateless FDA snapshot renders 'runs None days' (C._median returns None)", "disposition": "fixed: med_ok guard; unavailable branches in watch, report, and series"},
     {"severity": "low", "summary": "PLAN_YEARS hardcode + silent skip of unknown plan periods", "disposition": "fixed: unmatched counter + warning + report caution line"}
   ]}
]}
```
