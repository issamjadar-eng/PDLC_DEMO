# Code review — the six safety and economics analysis programs (BQ-20/21/22, BQ-28/29/30)

**What was reviewed**: the six small computer programs that calculate the answers to the
field-safety business questions (BQ-20 franchise-killer watch, BQ-21 regulatory exposure,
BQ-22 signal closed-loop) and the economics questions (BQ-28 revenue vs plan, BQ-29
attach-rate stage-gate, BQ-30 cost per update).
Files: `docs/project/commercial/bq_modules/bq_20.py`, `bq_21.py`, `bq_22.py`, `bq_28.py`,
`bq_29.py`, `bq_30.py`.

- **Date**: 2026-07-27 (findings resolved same day)
- **Reviewer**: AI assistant (independent code-review pass, task ben/108)
- **Verdict in one line**: every published number was confirmed correct and all earlier
  agreed fixes were confirmed present; the review found wording-vs-data and rounding
  defects that could misstate a future verdict — all have since been fixed or explicitly
  accepted.

## Plain-language summary

We reviewed the six programs behind the safety-watch and money-side business answers,
checking each against its written analysis plan, against the actual vocabulary of the
pinned data, and for traps that would only bite after a future data refresh. All 13
previously agreed fixes from earlier verification rounds were confirmed genuinely present
in the code. The review raised 24 new issues: 1 serious (the safety-watch headline was
fixed text that would still shout "WATCH TRIGGERED" in a period with zero safety events —
the very state the watch is supposed to report calmly), 7 moderate (verdict words typed as
fixed text, verdicts decided on rounded numbers near a threshold, and a missing-data case
shown as a perfect 0.0% variance), and 16 minor. Since the review, 15 of the 24 have been
fixed in the code and verified by re-reading it; the other 9 were consciously accepted
with a written reason (mostly cases that cannot occur under the data contracts, where a
loud failure is preferable to added complexity). Nothing remains unresolved.

## What we checked

- Each program against its committed analysis plan.
- The actual value vocabularies of the pinned data (status, disposition, category
  columns re-enumerated from the latest snapshots) against the vocabularies the code
  assumes.
- "Fixed wording" hazards — verdict words and summary sentences typed as constant text.
- Numeric traps — rounding before threshold comparisons, division by zero, sign handling,
  missing-data cells.
- Repeatability hygiene — no clocks, no randomness, no network; anchors derived only from
  pinned data.
- The 13 fixes agreed in the two prior verification dossiers — confirmed in code, not
  just in prose.

## Findings

### F-20-1 (high) — the safety watch could not report a quiet month truthfully

**What's wrong:** BQ-20's headline was fixed text reading "WATCH TRIGGERED … E-20.1
zero-tolerance NOT met". With zero watch-category events — the expected steady state for a
franchise-killer watch — the report would still open with a triggered watch and a failed
expectation, contradicting its own computed verdict table.
**Why it matters:** this is the safety report the CMO reads. A watch that cries wolf in
the all-clear state destroys trust in the one report that must be trusted.
**Resolution:** FIXED — the verdict is computed once and reused: the headline now branches
on whether events exist ("No franchise-killer events on file … the watch remains armed"
vs "WATCH TRIGGERED …"), and the met/NOT-met word derives from the computed expectation.

### F-20-2 (medium) — "(both signals landed as upgrade-items)" was typed, not computed

**What's wrong:** the report body hard-coded that both over-delivery signals landed as
upgrade items, next to a computed count.
**Why it matters:** the moment a third signal opens, or one lands differently, the
sentence becomes silently false.
**Resolution:** FIXED — the parenthetical is now derived from the closed-loop rows: count
word, noun plurality, and the actual disposition list are all computed.

### F-20-3 (low) — "the loop is demonstrably closing" even with zero closed signals

**What's wrong:** a watch note asserted loop closure unconditionally; with zero closed
signals it would have read "0 signals reached the corrective pipeline — the loop is
demonstrably closing".
**Why it matters:** self-contradicting reassurance in a safety context.
**Resolution:** FIXED — the clause is gated: with no closed signals it now states the loop
has not yet closed.

### F-20-4 (low) — the lag trim disappears on a very short data series

**What's wrong:** the trim that removes the incomplete trailing months of the public MAUDE
series degrades to no trim at all when the series is 3 months or shorter.
**Why it matters:** only relevant on a short series; the current pin has 40 months.
**Resolution:** ACCEPTED — unreachable under the dataset's history contract; noted for
reuse.

### F-21-1 (low) — "most favorable basis" decided on rounded rates

**What's wrong:** the sentence saying whether the published on-time-rate basis is the most
favorable of the four defensible bases compared display-rounded percentages; a near-tie
could flip the sentence on rounding alone.
**Why it matters:** a published qualifier should not depend on display precision.
**Resolution:** FIXED — the comparison now runs on unrounded fractions; the table still
shows rounded rates.

### F-21-2 (low) — the recall-rollout text parser is fragile

**What's wrong:** the pattern that extracts pending regions from the recall (FSCA)
description under-parses variant phrasings, silently.
**Why it matters:** a "why hasn't region X started" clause could be dropped — but the full
verbatim description is always quoted, so nothing false renders.
**Resolution:** ACCEPTED — the verbatim quote is the load-bearing disclosure; tighten the
pattern if the docket format ever varies.

### F-21-3 (low) — an unknown docket status would silently break the table

**What's wrong:** the roll-up table assumed statuses are exactly open/filed/closed; a new
status value would drop out of every cell and the totals, unflagged.
**Why it matters:** a self-inconsistent compliance table with no warning.
**Resolution:** FIXED — the module now fails loudly (refuses to publish, with a clear
message) if the docket ever carries a status outside the vocabulary.

### F-21-4 (low) — the code assumes at most one field corrective action

**What's wrong:** a second FSCA record would appear in the tables but get no rollout
narrative, quote, or issue entry.
**Why it matters:** only one FSCA exists in today's data.
**Resolution:** ACCEPTED — demo-data contract; generalize to a loop if a second FSCA is
ever seeded.

### F-21-5 (low) — crash instead of graceful message on an empty docket

**What's wrong:** date-min/max calls crash on an empty docket or zero filed reports.
**Why it matters:** unreachable while the dataset's minimum-rows contract holds.
**Resolution:** ACCEPTED — guarded by the corpus contract; a loud crash is acceptable.

### F-22-1 (medium) — "E-22.1 is NOT met" was typed while the verdict was computed

**What's wrong:** BQ-22's headline hard-coded the failed-expectation wording; a
breach-free refresh would have rendered a self-contradicting report (same defect class as
F-20-1).
**Why it matters:** the served-level-agreement verdict is the answer's point.
**Resolution:** FIXED — the verdict is computed once and the headline branches on it,
with matched wording for the met and not-met cases.

### F-22-2 (medium) — the over-delivery closure claim survived as a duplicate fixed sentence

**What's wrong:** the body repeated "Both over-delivery signals closed the loop into
upgrade items" as fixed text — the exact duplication an earlier fix was meant to remove,
surviving in a second location.
**Why it matters:** wrong count word, wrong disposition word, or an empty bracket the
moment the data shifts.
**Resolution:** FIXED — the body sentence is now derived from the same computed exemplar
set as the watch note (count word, noun, dispositions, and ids all computed), with an
explicit no-exemplar branch.

### F-22-3 (low) — a new disposition value would escape every funnel bucket

**What's wrong:** no exhaustiveness check on the disposition vocabulary; a new register
value would fall into no bucket, so rows would stop summing to the printed total.
**Why it matters:** silent misclassification in the loop-closure funnel.
**Resolution:** FIXED — the module now fails loudly if the register carries a disposition
outside the known set.

### F-22-4 (low) — distribution buckets assume the 90-day SLA

**What's wrong:** the histogram bucket edges and the sentence placing the SLA "between the
third and fourth buckets" assume the configured SLA stays at 90 days.
**Why it matters:** a config change would silently falsify the sentence.
**Resolution:** ACCEPTED — the SLA is a plan constant unlikely to move without a plan
edit; derive the buckets from the SLA if it ever changes.

### F-22-5 (low) — "median None days" possible in a degenerate case

**What's wrong:** if every breach were stale-open (no closed rows at all), one issue line
would interpolate a missing median as "None days".
**Why it matters:** unreachable on any realistic register.
**Resolution:** ACCEPTED — guard if that line is ever reused.

### F-28-1 (medium) — missing plan data displayed as a perfect 0.0% variance

**What's wrong:** a product line, region, or quarter with actuals but no plan rows
rendered "0.0%" variance — exactly on plan — instead of admitting no comparison was
possible; it also silently understated the plan total.
**Why it matters:** masking incomparability as perfection in the CFO's variance report.
**Resolution:** FIXED — the variance helper now returns "no value" for a missing plan
side; such cells render "n/a — no plan row", are excluded from all breach logic, and any
actual-vs-plan period/line/region mismatch is called out in the headline and a warning
bullet.

### F-28-2 (medium) — breach verdicts decided on display-rounded numbers

**What's wrong:** every tolerance test (per-line flags and the overall E-28.1 verdict)
compared a variance rounded to one decimal; a true -5.04% rounded to -5.0% and read as
within tolerance.
**Why it matters:** the verdict that triggers the reforecast conversation should not move
with display rounding.
**Resolution:** FIXED — all comparisons now run on unrounded ratios; rounding happens only
at render time.

### F-28-3 (low) — "deteriorating" tests endpoints, not the path

**What's wrong:** the quarter-over-quarter deterioration flag compares only last vs first
quarter (plus a last-quarter breach), so a V-shaped path could suppress or misstate it.
**Why it matters:** equivalent for the current two-quarter window.
**Resolution:** ACCEPTED — revisit the predicate (pairwise monotonicity) when Q3 lands.

### F-29-1 (medium) — the $24M gate verdict was decided on a rounded percentage

**What's wrong:** the attach percentage was rounded to 0.1 before comparing to the gate; a
true 39.96% would round to 40.0% and read "HOLDS".
**Why it matters:** a $24M release decision should not flip on display rounding — the
reading sits only 3 points from the gate.
**Resolution:** FIXED — the gate (and the alternative-denominator gate) is now compared on
the unrounded fraction; the rounded value is display-only.

### F-29-2 (low) — churned-site count could include sites outside the gap

**What's wrong:** the go-get watch note counted and listed all churned sites as part of
the gap, not the intersection; a churned site that re-subscribed or has no connected pumps
would be miscounted.
**Why it matters:** an inconsistency between the note and the table below it.
**Resolution:** FIXED — the note now intersects churned sites with the gap-site set before
counting and listing.

### F-29-3 (low) — a subscription site missing from the fleet drops out of regional numbers

**What's wrong:** a subscription row whose site is absent from the fleet registry silently
drops from every regional numerator, so regional rows would stop summing to the total.
**Why it matters:** guarded today by the datasets' reconcile-by-construction contract
(verified).
**Resolution:** ACCEPTED — a sum-check assert would make drift loud; add if touched.

### F-30-1 (low) — "pays back in None–None campaigns" possible under a config change

**What's wrong:** if a rate change ever made remote updates no cheaper than on-site, the
payback figures become undefined and the old text would interpolate "None–None".
**Why it matters:** nonsense text in the business-case headline.
**Resolution:** FIXED — payback rendering is guarded with three explicit branches
(payback at both bounds / only at the ceiling / no payback at all), in both the headline
clause and the report bullet.

### F-30-2 (low) — the breakeven position could render negative or above 100%

**What's wrong:** the "breakeven sits N% of the way up the cost bound" figure was
unclamped and assumed a non-degenerate bound.
**Why it matters:** out-of-range or nonsense percentages in the campaign-conversion note.
**Resolution:** FIXED — the position is clamped to 0–100 and the sentence branches for
breakeven below the floor ("conversion wins across the whole bound"), above the ceiling
("wins nowhere in the bound"), and a degenerate bound.

### F-30-3 (low) — another report's number was quoted as fixed text

**What's wrong:** the note quoted BQ-26's "zero of the backlog is remote-convertible"
finding as a literal, though the same fact is computable from this module's own pinned
data.
**Why it matters:** a cross-report number can go stale independently.
**Resolution:** FIXED — the remote-convertible count of the on-site backlog is now
computed locally (same device-to-connectivity join the module already does), with the
BQ-26 pointer kept as attribution.

### F-30-4 (low) — a division-by-zero guard tests the wrong list

**What's wrong:** the mean-duration guard tests the unfiltered completion list, so a
method whose completions all lack a duration would crash.
**Why it matters:** unreachable while the campaign generator populates durations.
**Resolution:** ACCEPTED — guarded by the dataset contract; swap the guard to the filtered
list if touched.

## Terms used

- **Analysis plan** — the written, committed description of how a business question must
  be computed; the code is reviewed against it.
- **Pin / pinned snapshot** — the exact, dated copy of a dataset an answer was computed
  from, enabling byte-for-byte reproduction.
- **E-NN.1 (expectation)** — a pre-declared pass/fail test each answer evaluates (e.g.
  "zero tolerance for confirmed over-delivery events").
- **MDR** — Medical Device Report, a mandatory adverse-event filing to FDA with a
  regulatory deadline.
- **FSCA** — Field Safety Corrective Action; a field recall/correction campaign.
- **MAUDE** — FDA's public database of medical-device adverse events; used here as
  class-wide context, counts only.
- **SLA** — service-level agreement; here, the 90-day limit for dispositioning a field
  signal.
- **Attach rate** — share of the installed pump base under an active Cloud Suite
  subscription; the stage-gate metric for a $24M spend decision.
- **Basis** — the definitional choice a rate is computed under (which window, anchor
  date, population, or measure); a "defensible basis" is any such choice a reasonable
  reviewer could argue for.
- **Denominator sensitivity** — showing how a rate changes under a different, equally
  defensible definition of its denominator.
- **Rounding-before-compare** — deciding a threshold verdict on a display-rounded number
  instead of the true value; a recurring defect class in this review.

## Technical appendix

Scope and grounding at review time: reviewed against the commercial skill's computation
contract ("Code quality" / "No string-literal facts" sections of
`.claude/skills/commercial/SKILL.md`), the analysis plans `plans/BQ-{20,21,22,28,29,30}.md`,
shared helpers in `computations.py`, and the pinned snapshots' actual value vocabularies.
Deterministic hygiene confirmed for all six modules: no clocks, no randomness, no network,
no absolute-path opens; all anchors derive from pins.

All 13 prior-dossier fixes verified present in code at review time: RT-20-1 (derived
docket join), RT-20-2 (3-month lag trim + caveat), RT-20-3 (derived loop pairs), RT-21-1
(FSCA rollout parsed, category gate, predates-window computed), BQ-21 basis-sensitivity
caveat (all branches computed), RT-21-2 (derived evidence class), RT-22-1 (true median via
shared `C._median`), RT-22-2 (derived W1 exemplars), F28-1-prior (breach count survives
rollup), F29-1-prior (denominator sensitivity table/series/clause), F29-2-prior (overreach
wording dropped), F30-1-prior (computed breakeven position).

Fix verification (2026-07-27, current code):

| Finding | Resolution | Where (current code) |
|---|---|---|
| F-20-1 | fixed | `bq_20.py` L100–117 (`e201_met` + branch), L120–128 |
| F-20-2 | fixed | L222–233 (`over_note` derived) |
| F-20-3 | fixed | L168–177 (W1 gated on `closed_loop`) |
| F-20-4 | accepted | L84 (`else []` when series ≤ trim) |
| F-21-1 | fixed | `bq_21.py` L87–91 (`basis_fracs` unrounded) |
| F-21-3 | fixed | L45–52 (unknown-status loud failure) |
| F-21-2 | accepted | L120 (`(\w+) pending` regex; verbatim quote load-bearing) |
| F-21-4 | accepted | L111 (single-FSCA `next()`) |
| F-21-5 | accepted | L38, L139 (min/max on contract-guarded inputs) |
| F-22-1 | fixed | `bq_22.py` L101–111 (`e221_met` + branch) |
| F-22-2 | fixed | L234–247 (`over_body` derived from `over_ex`) |
| F-22-3 | fixed | L40–47 (unknown-disposition loud failure) |
| F-22-4 | accepted | L17–18 (buckets), L221–223 (SLA sentence) |
| F-22-5 | accepted | L94 (median None), L152–154 (I2 interpolation) |
| F-28-1 | fixed | `bq_28.py` L21–31 (`_var`→None, `_vfmt`), L66–80, L89–91, L197–200 |
| F-28-2 | fixed | L21–27 (unrounded `_var`), L84 (`within` unrounded), rounding at render only |
| F-28-3 | accepted | L73–75 (endpoint predicate; fine for 2 quarters) |
| F-29-1 | fixed | `bq_29.py` L28–34 (`attach_frac` unrounded), L44 (`pca_gate_met`) |
| F-29-2 | fixed | L118–127 (`churned_gap` intersection) |
| F-29-3 | accepted | L58–60 (`site_region.get` silent drop; contract-guarded) |
| F-30-1 | fixed | `bq_30.py` L98–111 (payback clauses), L218–228 (report bullet) |
| F-30-2 | fixed | L79–96 (`be_pos` clamped + 4 branches) |
| F-30-3 | fixed | L146–151 (`rem_convertible` computed locally, BQ-26 pointer kept) |
| F-30-4 | accepted | L30–32 (guard tests unfiltered list) |

Cross-cutting observations (all now resolved or accepted):

1. The narrated-verdict headline (F-20-1, F-22-1) was the last surviving instance of the
   string-literal-facts class — both now branch-computed, matching the pattern BQ-28/29/30
   already used.
2. Rounding-before-compare clustered in the finance/gate modules (F-28-2, F-29-1, F-21-1)
   — all three now compare raw and round only for display. A shared-helper convention
   ("compare raw, round for display") remains worth adopting in `computations.py`.
3. Vocabulary sets (F-21-3, F-22-3) now fail loudly on a new value instead of silently
   mis-summing.

Machine-readable record (dispositions reflect actual outcomes):

```json
{
  "reviews": [
    {
      "path": "bq_modules/bq_20.py",
      "verdict": "changes-requested",
      "summary": "All prior fixes landed; the hardcoded WATCH TRIGGERED / NOT-met headline is now branch-computed with a clean zero-event steady state, the over-delivery parenthetical is derived, and the loop-closure clause is gated.",
      "findings": [
        {"id": "F-20-1", "severity": "high", "summary": "Headline hardcoded 'WATCH TRIGGERED' + 'E-20.1 NOT met'; zero events still rendered a triggered watch", "disposition": "fixed: e201_met computed once; headline branches on events; met/NOT-met derived"},
        {"id": "F-20-2", "severity": "medium", "summary": "Body literal '(both over-delivery signals landed as upgrade-items)'", "disposition": "fixed: derived from closed-loop rows (count, noun, dispositions)"},
        {"id": "F-20-3", "severity": "low", "summary": "W1 'loop is demonstrably closing' unconditional even at closed_loop == 0", "disposition": "fixed: clause gated on closed_loop with a not-yet-closing branch"},
        {"id": "F-20-4", "severity": "low", "summary": "Lag trim degrades to no trim when MAUDE series <= LAG_TRIM_MONTHS", "disposition": "accepted: unreachable on the 40-month pin; noted for reuse"}
      ]
    },
    {
      "path": "bq_modules/bq_21.py",
      "verdict": "approve-with-findings",
      "summary": "Plan-conformant; basis-sensitivity qualifiers computed; most-favorable comparison now unrounded; unknown docket statuses fail loudly; remaining accepts are contract-guarded edge cases.",
      "findings": [
        {"id": "F-21-1", "severity": "low", "summary": "most_favorable compared rounded rates; near-tie could flip the qualifier", "disposition": "fixed: unrounded ok/n fractions compared; table shows rounded"},
        {"id": "F-21-3", "severity": "low", "summary": "Hardcoded status set; unknown status silently dropped from roll-up and Total", "disposition": "fixed: loud SystemExit on any status outside the vocabulary"},
        {"id": "F-21-2", "severity": "low", "summary": "fsca_pending regex under-parses variant phrasings; silent partial parse", "disposition": "accepted: verbatim description always quoted; tighten if docket format varies"},
        {"id": "F-21-4", "severity": "low", "summary": "Single-FSCA assumption; a second FSCA gets no narrative or quote", "disposition": "accepted: one FSCA in pin; generalize to a loop if seeded"},
        {"id": "F-21-5", "severity": "low", "summary": "Empty docket / no filed MDRs crashes on max()/min()", "disposition": "accepted: min_rows corpus contract guards it"}
      ]
    },
    {
      "path": "bq_modules/bq_22.py",
      "verdict": "approve-with-findings",
      "summary": "Median and exemplar fixes confirmed; the narrated NOT-met headline and the duplicate over-delivery literal are now both derived from computed verdicts/sets; unknown dispositions fail loudly.",
      "findings": [
        {"id": "F-22-1", "severity": "medium", "summary": "Headline hardcoded 'so E-22.1 is NOT met' while the verdict was computed", "disposition": "fixed: e221_met computed once; headline branches on it"},
        {"id": "F-22-2", "severity": "medium", "summary": "Body literal 'Both over-delivery signals closed the loop into upgrade items' duplicated W1's derived claim", "disposition": "fixed: over_body derived from over_ex with a no-exemplar branch"},
        {"id": "F-22-3", "severity": "low", "summary": "No exhaustiveness check on disposition vocabulary", "disposition": "fixed: loud SystemExit on any disposition outside the known set"},
        {"id": "F-22-4", "severity": "low", "summary": "Bucket edges and 'between third and fourth buckets' sentence assume sla_days == 90", "disposition": "accepted: plan constant; derive buckets from sla if it changes"},
        {"id": "F-22-5", "severity": "low", "summary": "I2 can render 'median None days' if all breaches are stale-open", "disposition": "accepted: unreachable on a realistic register"}
      ]
    },
    {
      "path": "bq_modules/bq_28.py",
      "verdict": "approve-with-findings",
      "summary": "Rollup-survival rule confirmed; missing-plan cells now render n/a and are excluded from breach logic with a headline warning; all tolerance/verdict comparisons run unrounded.",
      "findings": [
        {"id": "F-28-1", "severity": "medium", "summary": "_var(a, 0) returned 0.0: cells with actuals but no plan rows showed 0.0% unflagged", "disposition": "fixed: _var returns None; 'n/a - no plan row' rendering; excluded from breach logic; period-set mismatch surfaced"},
        {"id": "F-28-2", "severity": "medium", "summary": "Breach flags and E-28.1 verdict compared round(v,1) against tolerance", "disposition": "fixed: unrounded ratios compared; rounding only at render"},
        {"id": "F-28-3", "severity": "low", "summary": "'deteriorating' tests last-vs-first quarter, not quarter-over-quarter", "disposition": "accepted: equivalent for the 2-quarter H1 window; revisit when Q3 lands"}
      ]
    },
    {
      "path": "bq_modules/bq_29.py",
      "verdict": "approve-with-findings",
      "summary": "Denominator-sensitivity fix confirmed; the gate (both bases) is now decided on unrounded fractions and the churned-site note intersects with the gap set.",
      "findings": [
        {"id": "F-29-1", "severity": "medium", "summary": "gate_met compared rounded attach_pct to gate: true 39.96% would round to 40.0% and HOLD", "disposition": "fixed: attach_frac and attach_pca_frac compared unrounded against gate/100; rounded values display-only"},
        {"id": "F-29-2", "severity": "low", "summary": "W1 counted/listed ALL churned sites, not churned intersect gap", "disposition": "fixed: churned_gap intersection used for count and list"},
        {"id": "F-29-3", "severity": "low", "summary": "Subscription site missing from fleet silently drops from regional numerators", "disposition": "accepted: reconcile-by-construction contract verified; add sum-check assert if touched"}
      ]
    },
    {
      "path": "bq_modules/bq_30.py",
      "verdict": "approve-with-findings",
      "summary": "Breakeven-position fix confirmed; payback and bound-position rendering are now fully guarded and branched, and the BQ-26 cross-reference number is computed locally.",
      "findings": [
        {"id": "F-30-1", "severity": "low", "summary": "payback None (remote >= on-site floor) rendered 'None-None campaigns'", "disposition": "fixed: three-branch payback clause (both bounds / ceiling only / no payback) in headline and bullet"},
        {"id": "F-30-2", "severity": "low", "summary": "be_pos unclamped: out-of-bound breakeven or zero-width bound rendered nonsense percentages", "disposition": "fixed: clamped to [0,100] with branches for below-floor / above-ceiling / degenerate bound"},
        {"id": "F-30-3", "severity": "low", "summary": "W1 hardcoded BQ-26's 'zero remote-convertible' number", "disposition": "fixed: rem_convertible computed from this module's own pins; BQ-26 attribution kept"},
        {"id": "F-30-4", "severity": "low", "summary": "mean_dur guard tests the wrong list; all-empty duration_min raises ZeroDivisionError", "disposition": "accepted: campaign generator populates durations; swap guard if touched"}
      ]
    }
  ]
}
```
