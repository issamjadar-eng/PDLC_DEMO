# Code-review dossier — safety + economics slice (bq_20 / bq_21 / bq_22 / bq_28 / bq_29 / bq_30), 2026-07-27

_Task ben/108 — AI-assisted code review (read-only) of the six computation modules under
`docs/project/commercial/bq_modules/`. Personal work artifact, not a controlled deliverable.
Review record for filing via `/commercial record-code-review`; no module, report, plan, or
corpus file was modified._

**Scope & method.** Reviewed against: the commercial skill's computation contract and
"Code quality" / "No string-literal facts" sections (`.claude/skills/commercial/SKILL.md`);
the analysis plans `plans/BQ-{20,21,22,28,29,30}.md`; shared helpers in `computations.py`;
the actual vocabularies of the pinned corpus snapshots (disposition / status / type /
category columns re-enumerated from the latest `normalized/records.csv` of each dataset);
and the two prior output-verification dossiers (`108-verify-redteam-fieldsafety-2026-07-27.md`,
`108-verify-redteam-economics-2026-07-27.md`), whose findings were already actioned — this
review verifies the fixes landed in code and does not re-flag settled items. Lenses: plan
conformance, string-literal facts (incl. computed-qualifier sentences), regex brittleness,
numeric traps (rounding-before-compare, bound arithmetic), hardcoded vocabularies,
denominators/zero-division, determinism, degradation robustness, marker discipline.
No style findings.

## Prior-finding fix verification (all landed)

| Prior finding | Fix expected | Verified in code |
|---|---|---|
| RT-20-1 (high) | Docket linkage derived from pinned docket, not a literal id | ✓ `bq_20.py` L66–75: `dock_watch` filtered from pinned docket rows (type=mdr, status=open, category in watch list), ids joined at L74, cited `[src: {dsrc}]`; `internal-regulatory-docket` is in BQ-20 `corpus_deps` (commercial.yml) |
| RT-20-2 (med) | 3-month lag trim + in-report "lag may run longer" caveat | ✓ `LAG_TRIM_MONTHS = 3` (L20, with rationale comment) and the caveat sentence emitted at L213–216 |
| RT-20-3 (low) | W1 loop pairs derived; under-investigation record selected by status | ✓ `loop_pairs` computed L63–64; `over_ui` selected by status L75, rendered L188–189 |
| RT-21-1 (med) | FSCA rollout parsed from description; over-delivery clause gated on category; predates-window computed | ✓ regex parse L107–110 with clean no-match degradation ("no rollout status is recorded…"); category gate L161–162; `late_prewin` computed L61 and rendered L206–208 / L234–235 |
| Basis-sensitivity caveat (BQ-21 pass-1) | Alternate bases published; "most favorable" and "no verdict flips" computed | ✓ four bases computed L66–79; `most_favorable` L81; `basis_flips` L83–84; all three render branches (flips / no-flip-with-late / met-everywhere) are conditional on computed values L252–260 — no narrated qualifier |
| RT-21-2 (low) | v-main evidence_class derived | ✓ L344–346 |
| RT-22-1 (low) | True median via shared helper | ✓ `C._median` (computations.py L1021–1026, correct even-n mean-of-middle-pair) used at `bq_22.py` L85 |
| RT-22-2 (low) | W1 exemplar ids derived | ✓ `over_ex` computed L90, W1 renders from it L163–166 — **but the same claim is still a string literal in the report body, see F-22-2** |
| F28-1 (low) | Breach count survives rollup | ✓ headline carries "N of M lines breach the band individually" L68–69; E-28.1 `actual` carries it too L150–153 |
| F29-1 (med) | Denominator sensitivity table + series + verdict clause, computed | ✓ whole-PCA basis computed L35–39; table L157–163, basis-defense line L165–170, headline clause L83–85, R1 L96–98, E-29.1 actual L133–134, `denominator-sensitivity` series L230–239 — every above/below word is `'above' if pca_gate_met else …` (computed, all branches) |
| F29-2 (low) | Drop "only sanctioned denominator" overreach | ✓ Method now says "the project's installed-base registry" L209–210 |
| F30-1 (low) | Breakeven position computed, not a directional adverb | ✓ `breakeven` and `be_pos` computed L78–79; W1 states "$…/update, a point {be_pos}% of the way up the bound … upper {100−be_pos}%" L115–123, and the `finish-current-campaign` series carries `position_in_bound_pct` L271–272 |

Deterministic hygiene (all six): no clocks, no randomness, no network, no absolute-path
`open()`; all anchors derive from pins; iteration is sorted or insertion-ordered — replay
determinism is expected to hold.

---

## BQ-20 — `bq_modules/bq_20.py` — verdict: **changes-requested**

Plan conformance: the computation honors every committed definition in `plans/BQ-20.md` —
watch categories enumerated from `params` (never discovered), event-level listing with no
trend gating, E-20.1 evaluated on the plan's "confirmed" definition (`not-met if over else
met`), docket linkage derived from the registered+pinned docket as a labeled category-level
join, MAUDE counts-only with the 3-month trim and the promised in-report lag caveat,
fabricated/real never blended. **One conformance hazard**: the plan's goal state ("the CMO
sees every watch-category event the month it appears") implies the zero-event month is the
expected steady state, and the module cannot render it truthfully (F-20-1).

| ID | Sev | Finding | Disposition |
|---|---|---|---|
| F-20-1 | high | Headline (L100–104) hardcodes `"WATCH TRIGGERED"` and `"E-20.1 zero-tolerance NOT met"` unconditionally. With zero watch-category records — the *expected* steady state for a franchise-killer watch — the report still opens "WATCH TRIGGERED … 0 over-delivery … E-20.1 zero-tolerance NOT met" while the expectations table computes `met`. The required clean "no events" degradation does not exist; the verdict sentence is narrated, not computed (the exact sentence-logic class SKILL.md bans). | fix: branch the headline on `events` — a "no watch-category events on the log this period; E-20.1 met" form when empty, "WATCH TRIGGERED …" only when non-empty; derive the met/NOT-met word from the computed verdict |
| F-20-2 | med | Report body L204–206 hardcodes "(both over-delivery signals landed as upgrade-items)" — a string-literal fact beside a computed count. True against today's pin; silently wrong the moment a third over-delivery signal opens or one lands as design-input. | fix: derive the parenthetical from the watch-signal rows (count + disposition), or drop it — the table above it already shows the facts |
| F-20-3 | low | W1 (L153–158) asserts "the signal→corrective loop is demonstrably closing for this category" unconditionally; with `closed_loop == 0` it would read "0 … signals reached the corrective pipeline (none with refs) — the loop is demonstrably closing". | fix: gate the clause on `closed_loop` |
| F-20-4 | low | Lag trim degrades to NO trim when the MAUDE series has ≤ `LAG_TRIM_MONTHS` months (L84: `else []`) — the one case where every charted month is inside the lag zone. Unreachable on the current 40-month pin. | accept: unreachable under the dataset's history contract; note for reuse |

## BQ-21 — `bq_modules/bq_21.py` — verdict: **approve-with-findings**

Plan conformance: fully conforms to `plans/BQ-21.md` — dual deterministic anchors (latest
event / pin date) both stated in Method; on-time and window definitions exactly as
committed; basis sensitivity published with both qualifier sentences ("most favorable",
"verdict flips") computed across all branches; FSCA rollout parsed from the pinned
description with honest no-match degradation; exposure list enumerated by id, never a bare
count. The E-21.1 verdict (`not-met if late_win`) matches the committed window basis.

| ID | Sev | Finding | Disposition |
|---|---|---|---|
| F-21-1 | low | `most_favorable` (L81) compares **rounded** rates (`C.pct` rounds to 0.1) — a near-tie basis pair (e.g. 94.649% vs 94.651%) can flip the "most favorable" sentence on rounding, the review's rounding-before-compare trap applied to a qualifier the report publishes. Verdict-flip logic (`basis_flips`) is count-based and immune. | fix: compare unrounded fractions (`ok/n`), display rounded |
| F-21-2 | low | `fsca_pending = re.findall(r"(\w+) pending", …)` (L110) silently under-parses variant phrasings — "APAC and LATAM pending" yields only `LATAM`; "pending in APAC" yields `[]`, dropping the "why has X not started" clause while the verbatim quote remains. Degradation is silence, not error, and the full description is always quoted (L272), so nothing false renders. | accept: the verbatim quote is the load-bearing disclosure; tighten the pattern if the docket generator's format ever varies |
| F-21-3 | low | Status vocabulary hardcoded `["open", "filed", "closed"]` (L45); a record with a new status (e.g. `superseded`) silently drops out of the roll-up cells AND the Total column while the heading's `len(rows)` still counts it — a self-inconsistent table with no warning. Matches today's docket vocabulary exactly (re-enumerated from the pin). | fix: derive statuses from the data (or assert observed ⊆ expected and fail loudly) |
| F-21-4 | low | Single-FSCA assumption: `next((r for r in rows if r["type"] == "fsca"), None)` (L101) — a second FSCA would appear in the roll-up and open-items table but get no rollout narrative/quote and no issue entry. One FSCA in today's pin. | accept: demo-data contract; generalize to a loop if the docket generator ever seeds a second FSCA |
| F-21-5 | low | Empty-docket / no-filed-MDR robustness: `max()` at L38 and `min()` at L128 raise `ValueError` on empty inputs — a crash, not a clean degradation. Unreachable while the dataset's `min_rows: 30` acquisition contract holds. | accept: guarded by the corpus contract; a two-line guard would make the failure mode explicit |

## BQ-22 — `bq_modules/bq_22.py` — verdict: **approve-with-findings**

Plan conformance: conforms to `plans/BQ-22.md` — cohort/lifetime windows, the committed
"died" definition (no-action + open>SLA), SLA denominator handling (pending excluded,
counted, stated), the bucketed distribution, the standard median via the shared helper, and
derived exemplars. Two hazards would break conformance on a refresh (F-22-1/-2). The funnel
bucket set exactly covers the register's current disposition vocabulary (re-enumerated from
the pin: design-input / requirement-change / upgrade-item / monitoring / no-action / open).

| ID | Sev | Finding | Disposition |
|---|---|---|---|
| F-22-1 | med | Headline (L92–96) hardcodes "so E-22.1 is NOT met" while the verdict is computed (`not-met if breach else met`, L117) — same narrated-verdict class as F-20-1. A breach-free refresh would render a self-contradicting report. Lower immediacy than BQ-20 only because a breach-free register is implausible near-term (16 lifetime dead signals). | fix: derive the met/NOT-met word from the computed verdict |
| F-22-2 | med | Report body L221–223 hardcodes "Both over-delivery signals closed the loop into upgrade items" — W1 computes the equivalent claim (L162–166) but the body line is a literal: wrong count word if a third over-delivery signal lands, wrong "upgrade items" if one lands as design-input, and an empty "( )" if none. The exact duplication RT-22-2's fix was meant to eliminate, surviving in a second location. | fix: render the body line from `over_ex` (reuse W1's logic), or delete it and keep W1 |
| F-22-3 | low | No exhaustiveness check on the disposition vocabulary: a new register value (e.g. `deferred`) falls into no funnel bucket — the bucket rows would no longer sum to the printed Total, with no flag; it would also silently escape both "died" and "landed". | fix: assert observed dispositions ⊆ the known set (fail loudly), or add a rendered "other" bucket |
| F-22-4 | low | Bucket edges (L17–18) and the sentence "the {sla}-day SLA line sits between the third and fourth buckets" (L206) assume `sla_days == 90`; changing the config param silently falsifies the sentence and misaligns the stale-open split from the distribution view. | accept: `sla_days` is a plan constant unlikely to move without a plan edit; note for the next plan revision (derive buckets from `sla` if it ever changes) |
| F-22-5 | low | If every breach were stale-open (no closed rows at all), I2 renders "median lifetime time-to-disposition None days" (`median_days` guarded to `None` at L85 but interpolated unguarded at L139). Unreachable on any realistic register. | accept: edge unreachable; guard if I2 is ever reused |

## BQ-28 — `bq_modules/bq_28.py` — verdict: **approve-with-findings**

Plan conformance: conforms to `plans/BQ-28.md` — actuals = closed quarters of the
configured FY from the pin, plan = matching quarterly rows, variance per line/region/
quarter/total, mix decomposition, the volume-vs-price split published as `unavailable` and
never approximated, and the F28-1 rollup-survival rule in both headline and E-28.1 actual.
**One conformance seam**: "compared only over matching periods" is enforced at quarter
granularity only — cell-level mismatches degrade silently (F-28-1).

| ID | Sev | Finding | Disposition |
|---|---|---|---|
| F-28-1 | med | `_var(a, p)` returns **0.0 when the plan cell is 0** (L21–22): a product line or region with actuals but no plan rows (or a quarter present in actuals but missing from the plan pin) renders "0.0%" variance, unflagged — masking exactly the incomparability the plan's "matching periods" commitment exists to prevent, and understating total plan in `tv`. | fix: render such cells as `n/a — no plan row` (and exclude from breach logic) instead of 0.0%; optionally warn when actual and plan period sets differ |
| F-28-2 | med | Rounding-before-compare on every tolerance test: `_var` rounds to 0.1 before `abs(v) > tol` (flags, L57–59, L171) and `within = abs(tv) <= tol` (the E-28.1 verdict, L65). A true −5.04% YTD rounds to −5.0% → `met`, where the unrounded comparison says breach. The verdict that triggers the CFO's reforecast conversation is decided on a display-rounded number. | fix: compute breach/verdict on unrounded ratios; round only for display |
| F-28-3 | low | `deteriorating` (L61) tests last-vs-**first** quarter plus a last-quarter breach, but R1's text claims "Quarter-over-quarter timing is deteriorating" — a V-shaped path (Q1 −6%, Q2 −2%, Q3 −5.5%) would suppress the flag, and a non-monotonic path could assert it. Correct on the current two-quarter window. | accept: equivalent for H1 (2 quarters); revisit the predicate (pairwise monotonicity) when Q3 lands |

## BQ-29 — `bq_modules/bq_29.py` — verdict: **approve-with-findings**

Plan conformance: conforms to `plans/BQ-29.md` — the attach definition exactly as
committed (active-subscription `pumps_connected` ÷ PP3500 fleet count, churned = zero),
the F29-1 denominator sensitivity as table + series + verdict clause with the basis
defense stated alongside (never in place of) it, the go-get gap sited, the unratified-gate
caveat in both verdict branches, and the attach-% history published as `unavailable`. The
"commercial-strategy.md … sets NO number" sentence is a literal but is verbatim-traceable
to the E-29.1 `basis` text in `commercial.yml` and cited `[config: commercial.yml]` —
acceptable grounding.

| ID | Sev | Finding | Disposition |
|---|---|---|---|
| F-29-1 | med | Gate verdict decided on a rounded value: `attach_pct = C.pct(...)` rounds to 0.1 before `gate_met = attach_pct >= gate` (L28–29); a true 39.96% rounds to 40.0% → "HOLDS". For a $24M release gate the reading sits 3.0 points from, the verdict boundary should not move with display rounding (same trap in `pca_gate_met`, L39, and `margin`). | fix: compare `attached / len(pp)` unrounded against `gate/100`; keep `C.pct` for display |
| F-29-2 | low | W1 (L115–119) counts **all** churned sites (`churned_sites` from the subscription register) as "of those sites", not `churned ∩ gap`: a churned site that re-subscribed (has an active row) or has zero connected pumps would be counted and *listed* in W1 while absent from the gap table below it. Subset holds on today's pin (verified: 3 churned ⊆ gap sites). | fix: intersect with `gap_by_site` keys before counting/listing |
| F-29-3 | low | A subscription site absent from the fleet registry silently drops out of every regional numerator (`site_region.get(...) == reg`, L54–55) — regional attach rows would no longer sum to the total with no warning. Guarded today by the datasets' reconcile-by-construction contract. | accept: cross-dataset reconciliation is an acquisition-time contract (verified in the prior dossier); a sum-check assert would make drift loud |

## BQ-30 — `bq_modules/bq_30.py` — verdict: **approve-with-findings**

Plan conformance: conforms to `plans/BQ-30.md` — completed-status set from the shared
`C.COMPLETED`, remote cost as config flat rate labeled a floor with retry counts
quantified, on-site cost strictly as the floor–ceiling bound (never a point), the E-30.1
deterministic bound rule implemented exactly as committed (met at floor / not-met at
ceiling / else at-risk, compared unrounded), payback per campaign (never annualized), the
method↔connectivity join reported, and the F30-1 breakeven stated as its computed position
in the bound. The fully-loaded figure is an `unavailable` series as promised.

| ID | Sev | Finding | Disposition |
|---|---|---|---|
| F-30-1 | low | `payback_floor` / `payback_ceiling` are `None` when the saving is ≤ 0 (L48–49), but the headline (L84–85) and payback line (L181–183) interpolate them unguarded → "pays back in None–None update campaigns" if a config change puts the remote rate at/above the labor floor. | fix: guard the rendering ("no payback — remote does not undercut on-site at this bound") |
| F-30-2 | low | `be_pos` (L79) is unclamped and assumes a non-degenerate bound: breakeven outside [floor, ceiling] renders a negative or >100 "position in the bound" and W1's "upper {100−be_pos}%" goes negative; a zero-width bound (mean duration = `fse_day_minutes`) hits `C.pct(x, 0) → 0.0` and renders nonsense. All well-formed on current config/pin (40.5% / upper 59.5%, matching the verification dossier). | fix: clamp to [0, 100] and branch the sentence when breakeven falls outside the bound ("conversion wins across the whole bound" / "nowhere in the bound") |
| F-30-3 | low | W1's closing clause "(BQ-26 shows zero of the on-site backlog is remote-convertible today)" (L122–123) hardcodes another BQ's numeric finding as a literal. Attributed cross-reference, but the fact is cheaply computable from THIS module's own pins (on-site-remaining joined to fleet `connected` — the same join the module already does for completions). | fix: compute the remote-convertible count of `rem` locally and interpolate it (keeping the "see BQ-26" attribution), or drop the number and keep the pointer |
| F-30-4 | low | `mean_dur` divides by the count of duration-bearing rows (L30–32): a method whose completions all lack `duration_min` raises `ZeroDivisionError` (the `if v else 0.0` guard tests the wrong list). Unreachable while the campaign generator populates durations on completions. | accept: guarded by the dataset contract; swap the guard to the filtered list if touched |

---

## Cross-cutting observations

1. **The narrated-verdict headline is the one surviving instance of the string-literal-facts
   failure class** (F-20-1, F-22-1): every *number* in every headline is computed, but two
   headlines hardcode the E-NN.1 met/NOT-met **word** and one hardcodes the "WATCH
   TRIGGERED" state. The fix pattern is one conditional per headline, and BQ-28/29/30
   already demonstrate it (`'within' if within else 'OUTSIDE'`, `'HOLDS' if gate_met …`).
2. **Rounding-before-compare clusters in the finance/gate modules** (F-28-2, F-29-1,
   F-21-1): `C.pct`/`round` values feed threshold comparisons that decide published
   verdicts. Worth one shared-helper convention: compare raw, round for display.
3. **Vocabulary sets are correct today and silently non-exhaustive tomorrow** (F-21-3,
   F-22-3): both modules' hardcoded status/disposition sets exactly match the pinned
   vocabularies (re-verified), but neither fails loudly on a new value. An
   `assert observed <= expected` idiom (or an "other" bucket) belongs in the shared file.
4. All 13 prior-dossier fixes assigned to this slice landed correctly; none was papered
   over, and the two "computed qualifier sentence" fixes (BQ-21 basis sensitivity, BQ-30
   breakeven position) are genuinely computed in every branch.

```json
{
  "reviews": [
    {
      "path": "bq_modules/bq_20.py",
      "verdict": "changes-requested",
      "summary": "All prior fixes landed (derived docket join, 3-month lag trim + caveat); but the headline hardcodes WATCH TRIGGERED / E-20.1 NOT met, so the zero-event steady state renders a false triggered watch contradicting the computed verdict.",
      "findings": [
        {"severity": "high", "summary": "Headline hardcodes 'WATCH TRIGGERED' + 'E-20.1 NOT met'; zero watch events still renders a triggered watch", "disposition": "fix: branch headline on events; derive met/NOT-met from computed verdict"},
        {"severity": "medium", "summary": "Report body literal '(both over-delivery signals landed as upgrade-items)' beside a computed count", "disposition": "fix: derive from watch-signal rows or drop; table already shows the facts"},
        {"severity": "low", "summary": "W1 'loop is demonstrably closing' unconditional even when closed_loop == 0", "disposition": "fix: gate the clause on closed_loop"},
        {"severity": "low", "summary": "Lag trim degrades to no trim when MAUDE series has <= LAG_TRIM_MONTHS months", "disposition": "accept: unreachable on the 40-month pin; note for reuse"}
      ]
    },
    {
      "path": "bq_modules/bq_21.py",
      "verdict": "approve-with-findings",
      "summary": "Plan-conformant; FSCA regex parse degrades honestly and both basis-sensitivity qualifier sentences are computed in every branch; residual findings are low (rounded-rate comparison, hardcoded status set, single-FSCA assumption, empty-input crash guarded only by the corpus contract).",
      "findings": [
        {"severity": "low", "summary": "most_favorable compares rounded rates; near-tie bases can flip the published qualifier", "disposition": "fix: compare unrounded ok/n fractions, round for display"},
        {"severity": "low", "summary": "fsca_pending regex '(\\w+) pending' under-parses variant phrasings; silent partial parse", "disposition": "accept: verbatim description always quoted; tighten if docket format varies"},
        {"severity": "low", "summary": "Hardcoded status set [open,filed,closed]; unknown status silently drops from roll-up and Total", "disposition": "fix: derive statuses from data or assert observed subset"},
        {"severity": "low", "summary": "Single-FSCA assumption via next(); a second FSCA gets no narrative or quote", "disposition": "accept: one FSCA in pin; generalize to a loop if seeded"},
        {"severity": "low", "summary": "Empty docket / no filed MDRs crashes on max()/min() instead of degrading", "disposition": "accept: min_rows corpus contract guards it; add guard if touched"}
      ]
    },
    {
      "path": "bq_modules/bq_22.py",
      "verdict": "approve-with-findings",
      "summary": "Median fix landed via shared C._median and W1 exemplars are derived, but the headline hardcodes 'E-22.1 is NOT met' and a body line duplicates the derived over-delivery claim as a literal — the same class RT-22-2 was meant to close.",
      "findings": [
        {"severity": "medium", "summary": "Headline hardcodes 'so E-22.1 is NOT met' while the verdict is computed; breach-free refresh self-contradicts", "disposition": "fix: derive met/NOT-met word from the computed verdict"},
        {"severity": "medium", "summary": "Body literal 'Both over-delivery signals closed the loop into upgrade items' duplicates W1's derived claim", "disposition": "fix: render from over_ex (reuse W1 logic) or delete; W1 covers it"},
        {"severity": "low", "summary": "No exhaustiveness check on disposition vocabulary; a new value silently escapes every funnel bucket", "disposition": "fix: assert observed dispositions subset of known set, or render an 'other' bucket"},
        {"severity": "low", "summary": "Bucket edges and 'between third and fourth buckets' sentence assume sla_days == 90", "disposition": "accept: plan constant; derive buckets from sla if it ever changes"},
        {"severity": "low", "summary": "I2 can render 'median ... None days' if all breaches are stale-open (no closed rows)", "disposition": "accept: unreachable on a realistic register; guard if reused"}
      ]
    },
    {
      "path": "bq_modules/bq_28.py",
      "verdict": "approve-with-findings",
      "summary": "Plan-conformant with the F28-1 rollup-survival rule in headline and E-28.1; two medium numeric traps — zero-plan cells render 0.0% variance unflagged, and tolerance/verdict comparisons run on display-rounded values.",
      "findings": [
        {"severity": "medium", "summary": "_var(a, 0) returns 0.0: line/region/quarter with actuals but no plan rows shows 0.0% unflagged", "disposition": "fix: render 'n/a — no plan row', exclude from breach logic, warn on period-set mismatch"},
        {"severity": "medium", "summary": "Breach flags and E-28.1 verdict compare round(v,1) against tolerance; -5.04% YTD reads met", "disposition": "fix: compare unrounded ratios; round only for display"},
        {"severity": "low", "summary": "'deteriorating' tests last-vs-first quarter but R1 claims quarter-over-quarter deterioration", "disposition": "accept: equivalent for the 2-quarter H1 window; revisit predicate when Q3 lands"}
      ]
    },
    {
      "path": "bq_modules/bq_29.py",
      "verdict": "approve-with-findings",
      "summary": "F29-1 denominator-sensitivity fix fully landed (table, series, verdict clause — every above/below branch computed) and F29-2 wording corrected; main residual is the $24M gate verdict being decided on a 0.1-rounded attach percentage.",
      "findings": [
        {"severity": "medium", "summary": "gate_met compares rounded attach_pct to gate: true 39.96% rounds to 40.0% and HOLDS", "disposition": "fix: compare attached/len(pp) unrounded against gate/100; round for display"},
        {"severity": "low", "summary": "W1 counts/lists ALL churned sites, not churned intersect gap; breaks if a churned site re-subscribes", "disposition": "fix: intersect churned_sites with gap_by_site keys"},
        {"severity": "low", "summary": "Subscription site missing from fleet silently drops from regional attach numerators", "disposition": "accept: reconcile-by-construction contract verified; a sum-check assert would make drift loud"}
      ]
    },
    {
      "path": "bq_modules/bq_30.py",
      "verdict": "approve-with-findings",
      "summary": "F30-1 breakeven-position fix landed (computed, matches independent re-derivation at 40.5% / upper 59.5%); E-30.1 bound rule implemented exactly per plan on unrounded comparisons; residual findings are low rendering/edge guards plus one computable cross-BQ literal.",
      "findings": [
        {"severity": "low", "summary": "payback None (remote >= on-site floor) renders 'None-None campaigns' in headline and report", "disposition": "fix: guard rendering with a 'no payback at this bound' branch"},
        {"severity": "low", "summary": "be_pos unclamped: breakeven outside the bound or a zero-width bound renders negative/nonsense percentages in W1", "disposition": "fix: clamp to [0,100] and branch the sentence for out-of-bound breakeven"},
        {"severity": "low", "summary": "W1 hardcodes BQ-26's 'zero remote-convertible' number though it is computable from this module's own pins", "disposition": "fix: compute the join over on-site-remaining locally; keep the BQ-26 attribution"},
        {"severity": "low", "summary": "mean_dur guard tests the wrong list; all-empty duration_min for a method raises ZeroDivisionError", "disposition": "accept: campaign generator populates durations; swap guard to the filtered list if touched"}
      ]
    }
  ]
}
```
