# Code-review dossier — board BQ modules bq_01–bq_05 (2026-07-27)

_Demo sample data — not for clinical use._

**Scope**: independent AI code review of the five board computation modules
`docs/project/commercial/bq_modules/bq_0{1..5}.py` against their committed plans
(`docs/project/commercial/plans/BQ-0N.md`), the shared helpers
(`docs/project/commercial/computations.py`), and the commercial skill's review
failure-class list (SKILL.md § Code quality). Read-only review; deliverable is this
dossier. **By**: AI code-review agent · **Task**: ben/108 · **Date**: 2026-07-27.

**Relationship to the prior output-level dossier**
(`tasks/ben/_work/108-verify-redteam-board-2026-07-27.md`): its findings were already
dispositioned — ACTIONED entries exist in each edition's `quality.json` for the
BQ-01 verdict-parenthetical restructure, BQ-02 basis-sensitivity disclosure, BQ-03
recurring-specific decomposition, and BQ-04 knife-edge + raw-sums rounding. **All four
fixes are implemented correctly in code** (verified below). Prior low notes with no
ACTIONED record (BQ-01 "+0.0 pts" rendering, BQ-04 section title, BQ-05 median
tail/survivorship clauses) are treated as accepted dispositions and are not re-flagged.

**Cross-module pattern (one root cause, several findings)**: `C.pct()` rounds to one
decimal, and every module compares thresholds against its output (`expo[y] > thr`,
`C.pct(v, total) > thr`, strict-increase tests on rounded shares). BQ-04's plan
committed "compute on raw, round for display" and its module honors it; the other four
compare on rounded values. All current verdicts are far from their thresholds, so
nothing is wrong today — but the pattern is exactly the knife-edge class the project's
history flags. A shared raw-fraction helper (or `pct_raw`) would retire the class in
one change.

---

## bq_01.py — Funding map · **APPROVED-WITH-FINDINGS**

**Plan conformance (plans/BQ-01.md)**: Conforms. Trailing-4Q window anchored at the
latest period in the pinned snapshot (no clocks) ✔; GM = revenue − COGS across all
regions/revenue types ✔; funds-in-proportion-to-GM-share and consumes-if-negative
(E-01.1) ✔; top-`timeseries_top_lines` + aggregated "other" trend with the aggregation
stated on the chart label ✔; quarter→ISO first-day mapping ✔. Prior fixes verified in
code: headline parenthetical now binds pair GM vs portfolio GM distinctly (L63–66);
`gm-by-line`/`totals-stat` now `derived` with derivation chains (L176–197).

| Sev | Location | Issue | Proposed disposition |
|---|---|---|---|
| med | L67–68 | Headline literal "all six lines gross-margin positive" — the line count is asserted, not computed; `lines_all` is derived from data, so a snapshot with a new line silently emits a wrong count in the verdict | fix: `f"all {len(lines_all)} lines gross-margin positive"` |
| low | L58 | `funders_share` = sum of per-line **rounded** shares; on current pins gives 59.7 vs 59.8 for round-of-raw (`C.pct(pair_gm, total_gm)`) — display drift only, but violates the raw-then-round convention | fix: `funders_share = C.pct(pair_gm, total_gm)` |
| low | L46–47, L53, L60 | GM% drift computed as difference of rounded percentages, then compared to the −1.0 threshold — double rounding can flip the "compressing" flag at the boundary | fix: compute delta from raw fractions; round for display only |
| low | L60 | The −1.0 pt "compressing" threshold is a bare code constant — the plan commits to flagging "margin-thin-and-shrinking" but sets no number, so the number is un-audited sentence logic | fix: move to `params` (or state the value in the plan) |
| low | L33 | `prior = periods[-2*n_trail:-n_trail]` silently shortens or empties when fewer than 8 periods are on file; drift then compares against a partial (or zero) prior window without notice | fix: guard — emit drift "n/a" when the prior window is incomplete |

---

## bq_02.py — Concentration · **CHANGES-REQUIRED**

**Plan conformance (plans/BQ-02.md)**: Conforms, including the committed
basis-sensitivity disclosure — implemented in all three promised places (verdict line
L103–110, dedicated report section L200–214, expectation row L168–177) plus the R3
narrative risk, with the floor-of-total computed from the internal-financials ledger
exactly as the plan specifies (L91–95). Anchor selection excludes `independent` ✔;
constant-dent floor scenario with FY2026 = quarterly sum ✔.

| Sev | Location | Issue | Proposed disposition |
|---|---|---|---|
| high | L103–104 | Headline asserts **"above the {thr}% guardrail on the direct-book basis" unconditionally** — it is a string literal, not a computed comparison. On a refresh where the anchor drops to ≤30%, the expectation flips to `met` while the verdict headline still declares a breach — a wrong verdict sentence. The floor-of-total clause two lines later IS conditioned (`floor_breaches`), which highlights the asymmetry | fix: condition the phrase on the raw share vs `thr` (mirror L210–214's BREACHES/within branching) |
| med | L227, L71–72 | Report line asserts "PCA franchise (PP3500 + PP3000 + cloud-suite per [config…])" as a literal while the actual roster comes from `pca_franchise_lines`; pumps-only cut hardcodes `("PP3500", "PP3000")` — a config change silently makes the sentence lie and the pumps figure stale | fix: interpolate `" + ".join(pca_lines)`; derive pump lines from config (new param or exclude the proxy line) |
| low | L59–60, L93–95, L193, L211 | All guardrail comparisons run on `C.pct()`-rounded values (anchor share, floor share, per-GPO ⚠ flags) — knife-edge flips at 30.0x | fix: compare raw `100*v/total` against `thr`; keep `C.pct` for display |
| low | L67 | `top3_share` = sum of three rounded shares instead of share of summed revenue | fix: `C.pct(sum(v for _, v in top3), total)` |
| low | L125 | Narrative gate `top3_share > 25` is a magic constant in neither plan nor params — the "compounds the GPO concentration" claim appears/disappears on an un-audited number | fix: move to `params` or tie to `concentration_threshold_pct` with the rationale stated in the plan |
| low | L15, L26–33 | `PLAN_YEARS` hardcoded and unknown periods silently dropped in `_plan_year_totals` — an FY2031 row in a refreshed plan vanishes without notice (window itself is plan-committed, the silence is the issue) | fix: count unmatched rows and surface them (report line or stderr warning) |

---

## bq_03.py — Recurring mix vs Y5 · **APPROVED-WITH-FINDINGS**

**Plan conformance (plans/BQ-03.md)**: Conforms. Recurring = subscription only ✔;
cloud-suite proxy from config with both error directions stated ✔; three-bucket
decomposition defined against `regulatory_dependency` with the committed bucket→tag
mapping ✔; y5 target checked against `y5_target_usd` and the delta reported, not
smoothed ✔; FY→ISO mapping handles the H1 label (`fy[2:6]`) ✔. Prior fix verified in
code: the committed recurring-specific decomposition (blended AND within-proxy, both
reported, headline carries both) is implemented at L77–97 and L190–201 — arithmetic
structure matches the plan and the ACTIONED record (210/240 = 87.5%).

| Sev | Location | Issue | Proposed disposition |
|---|---|---|---|
| med | L46, L152–154 | H1 handling only fires when **exactly 2** quarters are on file; with 1 or 3 quarters the current year renders as an unqualified "FY2026" while the static italic disclosure still asserts "The current fiscal year is a half-year of actuals" — label and prose both rot on the next quarterly refresh | fix: generic partial-year label (`f"FY{y} (Q1–Q{n})"` when n<4) and make the disclosure sentence conditional on the actual quarter count |
| med | L199–201 | "the cleared cushion **mostly** sits outside the recurring story" — 'mostly' is narrated, not computed (true today at 77%; the sentence persists even if `cleared_nonproxy/contracted` drops below half) | fix: compute the share and either interpolate it or branch the qualifier |
| med | L60–63 | A new `regulatory_dependency` value raises KeyError (dicts pre-seeded with `DEP_ORDER`) — the computation crashes on a category the plan's buckets don't cover instead of reporting an unclassified bucket (crash is loud, but blocks the refresh) | fix: collect unknown tags into a reported "unclassified" bucket (and fail the bucket table loudly in the report) |
| low | L89–90 | E-03.1 strict-increase evaluated on rounded shares — two years at 7.94/7.90 both round to 7.9 and flip the verdict | fix: compare raw `rec/tot` fractions |
| low | L110 | Narrative gate `asp_share > 40` is a magic constant — numerically coincides with BQ-05's `exposure_threshold_pct` but is not linked to it | fix: read the threshold from config (BQ-05 params) or add to BQ-03 params |
| low | L191 | "_The blended decomposition above spans all six lines_" — hardcoded line count (same class as bq_01) | fix: interpolate the computed line count or drop the number |
| low | L14, L53–55 | `PLAN_YEARS` hardcode + silent `continue` on unknown periods (same as bq_02) | fix: shared guard |

---

## bq_04.py — Subscription unit economics · **APPROVED-WITH-FINDINGS**

**Plan conformance (plans/BQ-04.md)**: Conforms. Active-only rates with churned
counted and surfaced against the no-churn horizon (W2) ✔; the committed **rounding
convention is implemented correctly** — ratio on raw sums (L43), band margin on raw
sums (L69), LTV from the raw rate (L41), verdicts compare unrounded values (L147,
L186, L193) ✔; the committed **threshold-sensitivity disclosure** (miss in pp, SE,
knife-edge flag at ≤1pp or ≤2 SE) is implemented in the report, W3, the E-04.2 row,
and a dedicated `discount-sensitivity` series ✔; size bands from config ✔; attach gap
= connected sites minus register sites, exactly the plan's definition (churned sites
have rows, so they are excluded — per plan) ✔; survivor-biased ARR build stated ✔.

| Sev | Location | Issue | Proposed disposition |
|---|---|---|---|
| med | L111–114 | Failing-branch headline hardcodes "— **concentrated in small sites** —" — a narrated qualifier, not computed from the band distribution (true today: 24/28 in small; a refresh where mid-band sites dominate keeps emitting it) | fix: compute the band holding the max share of ARR-below-cost sites and emit the clause conditionally with the computed band name |
| med | L30–31 | Status set hardcoded to `{active, churned}` — a new register status (e.g. suspended/pending) silently drops sites from **both** the rates and the churn count while `len(subs)` denominators still include them; a silent-exclusion, not a crash | fix: compute `other = [r for r in subs if status not in (...)]` and report a nonzero count loudly (or assert) |
| low | L173–176, L190–192, L235–239 | Knife-edge prose asserts "≈2 standard errors" as static text; the flag also fires on the \|miss\|≤1pp branch where the SE multiple can be far from 2 — the narrated number can disagree with the computed condition | fix: compute `n_se = abs(disc_margin)/disc_se` and interpolate it; name which condition fired |
| low | L305–306 | data.json point label "knife-edge (\|miss\| <= 2 SE)" omits the 1pp branch of the actual rule (L85–86) — label misdocuments the computed flag | fix: label "knife-edge (\|miss\| <= 1pp or <= 2 SE)" |
| low | L95–98 | `starts[0]` raises IndexError when there are zero active sites (rates degrade to 0.0 gracefully, then the ARR-build crashes) | fix: guard the history build on empty `active`; emit the series as unavailable |

---

## bq_05.py — Plan revenue behind FDA decisions · **APPROVED-WITH-FINDINGS**

**Plan conformance (plans/BQ-05.md)**: Conforms fully. Dependent set read from
`dependent_categories` config (letter-to-file deliberately excluded, four-way split
still reported) ✔; exposure per plan year vs `exposure_threshold_pct`, evaluated every
year ✔; uniform-slip method with M/12 roll-forward and past-FY2030 truncation reported
as window shortfall — implemented exactly as committed (L53–62; the `prev_in` residue
after the loop is precisely the past-window loss) ✔; median FRN review interval via
the shared even/odd-correct `C._median` helper, scoped as public context with no
our-vs-market claim ✔; exposure history marked `unavailable`, not faked ✔. Prior
red-team was CONFIRMED with low notes only (median tail, survivorship clause) — accepted,
not re-flagged.

| Sev | Location | Issue | Proposed disposition |
|---|---|---|---|
| med | L39–43 | A new `regulatory_dependency` value raises KeyError (dict pre-seeded with `DEP_ORDER`); dependency table columns are also hardcoded to the four known tags — crash on refresh with a fifth tag (same class as bq_03) | fix: collect unknown tags into a reported "unclassified" bucket; derive table columns from observed ∪ DEP_ORDER |
| low | L110–111, L177, L244 | "since 2021" asserted as a string literal in three places — an acquisition-window fact typed into source; a re-acquired snapshot with a different from-date rots all three silently | fix: derive the earliest year from the pinned records (`min(date_received)[:4]`) |
| low | L112 | "one review cycle is on the order of the smaller slip scenario" — comparative narrated, not computed; also assumes `slips[0]` is the smaller scenario (config order) | fix: compare `med` days against `min(slips)*365/12` and interpolate both figures; or drop the comparative |
| low | L46–47 | Breach test `expo[y] > thr` runs on `C.pct`-rounded exposure — knife-edge flips at 40.0x (current years are clear of the line) | fix: compare raw `100*dep/tot` |
| low | L70 | Empty or dateless FDA snapshot → `C._median` returns `None` → report renders "runs None days" silently | fix: guard — emit the context stat as unavailable when `ivs` is empty |
| low | L16, L41–43 | `PLAN_YEARS` hardcode + silent skip of unknown periods (same as bq_02/bq_03) | fix: shared guard |

---

## Summary

| Module | Verdict | High | Med | Low |
|---|---|---|---|---|
| bq_01.py | APPROVED-WITH-FINDINGS | 0 | 1 | 4 |
| bq_02.py | CHANGES-REQUIRED | 1 | 1 | 4 |
| bq_03.py | APPROVED-WITH-FINDINGS | 0 | 3 | 4 |
| bq_04.py | APPROVED-WITH-FINDINGS | 0 | 2 | 3 |
| bq_05.py | APPROVED-WITH-FINDINGS | 0 | 1 | 5 |

All prior-dossier ACTIONED fixes verified correctly implemented in code. No
string-literal *values* (numbers, ids) were found in any module — every figure is
computed from pins/params; the residual string-literal class is **sentence logic**
(hardcoded qualifiers/counts: bq_01 "six lines", bq_02 "above the guardrail",
bq_03 "mostly", bq_04 "concentrated in small sites", bq_05 "on the order of").
Determinism is clean across all five (no clocks/randomness; all set/dict iteration
feeding output is sorted or insertion-deterministic).

```json
{"reviews": [
  {"path": "bq_modules/bq_01.py", "verdict": "APPROVED-WITH-FINDINGS",
   "summary": "Plan-conformant; prior fixes verified; hardcoded 'six lines' count and rounded-compare hygiene remain.",
   "findings": [
     {"severity": "med", "summary": "Headline literal 'all six lines' - count asserted, not len(lines_all); rots on new line", "disposition": "fix: interpolate len(lines_all)"},
     {"severity": "low", "summary": "funders_share sums rounded shares (59.7 vs 59.8 raw-basis); violates raw-then-round", "disposition": "fix: C.pct(pair_gm, total_gm)"},
     {"severity": "low", "summary": "GM% drift computed/compared on rounded pcts vs -1.0 threshold; knife-edge flips", "disposition": "fix: raw fractions, round for display"},
     {"severity": "low", "summary": "Compressing threshold -1.0pt is a bare code constant absent from plan/params", "disposition": "fix: move to params or state in plan"},
     {"severity": "low", "summary": "prior window periods[-8:-4] silently partial/empty when <8 periods on file", "disposition": "fix: emit drift n/a when prior window incomplete"}
   ]},
  {"path": "bq_modules/bq_02.py", "verdict": "CHANGES-REQUIRED",
   "summary": "Basis-sensitivity disclosure correctly implemented, but headline hardcodes 'above the guardrail' unconditionally.",
   "findings": [
     {"severity": "high", "summary": "Headline asserts 'above the 30% guardrail' as string literal, not conditioned; wrong verdict if anchor drops", "disposition": "fix: branch on raw share vs thr like L210-214"},
     {"severity": "med", "summary": "'PP3500 + PP3000 + cloud-suite' literal + hardcoded pumps tuple; rots if franchise config changes", "disposition": "fix: interpolate pca_lines; config the pump subset"},
     {"severity": "low", "summary": "Guardrail comparisons on C.pct-rounded values (anchor, floor, per-GPO flags)", "disposition": "fix: compare raw 100*v/total"},
     {"severity": "low", "summary": "top3_share sums rounded shares instead of share of summed revenue", "disposition": "fix: C.pct(sum(top3 values), total)"},
     {"severity": "low", "summary": "Narrative gate top3_share > 25 is a magic constant in neither plan nor params", "disposition": "fix: move to params or tie to concentration threshold"},
     {"severity": "low", "summary": "PLAN_YEARS hardcoded; unknown plan periods silently dropped", "disposition": "fix: count and surface unmatched rows"}
   ]},
  {"path": "bq_modules/bq_03.py", "verdict": "APPROVED-WITH-FINDINGS",
   "summary": "Recurring-specific decomposition correctly implemented; H1 labeling and 'mostly' qualifier are refresh-fragile.",
   "findings": [
     {"severity": "med", "summary": "H1 label only when exactly 2 quarters; static 'half-year of actuals' prose rots at 1 or 3 quarters", "disposition": "fix: generic partial-year label + conditional sentence"},
     {"severity": "med", "summary": "'cleared cushion mostly sits outside recurring' - 'mostly' narrated, not computed (77% today)", "disposition": "fix: compute share, interpolate or branch qualifier"},
     {"severity": "med", "summary": "New regulatory_dependency value raises KeyError (DEP_ORDER pre-seeded dicts); crash on refresh", "disposition": "fix: reported 'unclassified' bucket"},
     {"severity": "low", "summary": "E-03.1 strict-increase tested on rounded shares; ties at 1dp flip verdict", "disposition": "fix: compare raw rec/tot fractions"},
     {"severity": "low", "summary": "Narrative gate asp_share > 40 magic constant, unlinked to BQ-05 exposure threshold", "disposition": "fix: read from config"},
     {"severity": "low", "summary": "'spans all six lines' hardcoded count in report prose", "disposition": "fix: interpolate computed count"},
     {"severity": "low", "summary": "PLAN_YEARS hardcode + silent continue on unknown periods", "disposition": "fix: shared guard"}
   ]},
  {"path": "bq_modules/bq_04.py", "verdict": "APPROVED-WITH-FINDINGS",
   "summary": "Committed raw-sums rounding and knife-edge disclosure implemented correctly; two narrated/status-set frailties remain.",
   "findings": [
     {"severity": "med", "summary": "Headline hardcodes 'concentrated in small sites' - qualifier narrated, not computed from band split", "disposition": "fix: compute max-neg band, emit conditionally"},
     {"severity": "med", "summary": "Status set {active,churned} hardcoded; new status silently drops sites from rates and churn count", "disposition": "fix: report unrecognized-status count loudly"},
     {"severity": "low", "summary": "Knife-edge prose asserts '~2 standard errors' statically; 1pp branch can fire at other SE multiples", "disposition": "fix: compute and interpolate miss/SE; name fired condition"},
     {"severity": "low", "summary": "data.json knife-edge label omits the 1pp branch of the actual rule", "disposition": "fix: label both conditions"},
     {"severity": "low", "summary": "starts[0] IndexError when zero active sites (ARR-build history)", "disposition": "fix: guard empty actives, emit series unavailable"}
   ]},
  {"path": "bq_modules/bq_05.py", "verdict": "APPROVED-WITH-FINDINGS",
   "summary": "Slip/exposure arithmetic exactly per plan; 'since 2021' literals and dependency-tag KeyError are the residual risks.",
   "findings": [
     {"severity": "med", "summary": "New regulatory_dependency value raises KeyError; table columns hardcoded to four known tags", "disposition": "fix: 'unclassified' bucket + derive columns"},
     {"severity": "low", "summary": "'since 2021' string literal in W1, report, data.json label; rots if acquisition window changes", "disposition": "fix: derive earliest year from pinned dates"},
     {"severity": "low", "summary": "'on the order of the smaller slip scenario' narrated comparative; assumes slips[0] smallest", "disposition": "fix: compute med-days vs min(slips) months, interpolate"},
     {"severity": "low", "summary": "Breach test expo[y] > thr on rounded pct; knife-edge at 40.0", "disposition": "fix: compare raw 100*dep/tot"},
     {"severity": "low", "summary": "Empty/dateless FDA snapshot renders 'runs None days' (C._median returns None)", "disposition": "fix: guard, emit context stat unavailable"},
     {"severity": "low", "summary": "PLAN_YEARS hardcode + silent skip of unknown plan periods", "disposition": "fix: shared guard"}
   ]}
]}
```
