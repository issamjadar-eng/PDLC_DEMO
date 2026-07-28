# Code review — market analysis modules (BQ-07 to BQ-11), 2026-07-27

_Demo sample data — not for clinical use._

**What was reviewed**: the five Python programs that compute the market-facing business
answers — our US segment share (BQ-07), win/loss drivers (BQ-08), the post-recall
disruption window (BQ-09), the buyer's five-year total cost of ownership (BQ-10), and
sold-but-underused sites (BQ-11).

- **Artifacts**: `docs/project/commercial/bq_modules/bq_07.py` … `bq_11.py`, reviewed
  against their committed analysis plans (`docs/project/commercial/plans/BQ-07.md` …
  `BQ-11.md`), the shared helpers in `docs/project/commercial/computations.py`, and the
  entity alias map (`entity-aliases.yml`)
- **Reviewer**: AI code reviewer (read-only review; task ben/108)
- **Date**: 2026-07-27
- **Verdict in one line**: all five programs approved with findings — 19 issues raised
  (no serious ones, 6 moderate, 13 minor); **13 have since been fixed and 6 were
  explicitly accepted with rationale** — every outcome re-verified in the current code
  before this report was written.

## Plain-language summary

This is a code review of the five programs that produce the market-facing business
answers. Each was checked against its written analysis plan, and every one conforms — the
review found no wrong number in any current published answer. The 19 issues raised are
latent hazards: safety checks that did not cover everything they promised to, sentences
whose wording could contradict the numbers printed next to them on a future data shape,
and one threshold test that rounded a number before comparing it. None of these corrupts
today's answers; each could quietly corrupt a future refresh. Thirteen of the issues have
since been fixed in the code, and the remaining six were consciously accepted — each with
a written reason, typically that the failure mode is a loud crash rather than a wrong
number, or that the imprecision is too small to matter. Every fix and every acceptance
was re-verified against the current code before this report was written.

## What we checked

- Does each program's arithmetic match what its written analysis plan commits to?
- Do the safety checks (assertions that stop the program if a source record changed)
  actually cover every fact the program copies out of those records?
- Are the verdict sentences computed from the data, or could their wording contradict the
  numbers they print on a future data shape?
- Is rounding applied only for display, never before comparing a value to a threshold?
- When company names are matched across datasets, can a new or misspelled name silently
  fall through the matching and skew the result?
- Do the programs behave honestly at the edges — empty groups, missing data, unexpected
  status values?
- Were the fixes promised by the earlier output-level review actually implemented?

## Findings

All resolutions below were verified against the current code on 2026-07-27. Line
references live in the technical appendix.

### F-1 (medium) — One copied market figure was not covered by the change alarm (bq_07.py, segment share)

- **What's wrong:** the program copies four figures out of the market-size assumption
  record and promises that assertions will halt it loudly if the record ever changes —
  but only three of the four were covered. The annual-demand range ("130k–230k units")
  could drift silently if the record was edited.
- **Why it matters:** a stale copied figure in a share analysis defeats the whole purpose
  of the loud-alarm design.
- **Resolution:** FIXED — the assertion now also requires the "130k-230k" range to be
  present in the assumption record, so any edit trips the alarm.

### F-2 (low) — A zero-unit year would crash the growth calculation (bq_07.py)

- **What's wrong:** if the earliest fiscal year had zero installed units, the growth-rate
  formula would divide by zero and crash.
- **Why it matters:** a crash would block the answer on a refresh, though it cannot
  publish a wrong number.
- **Resolution:** ACCEPTED — the demo datasets guarantee non-empty fiscal-year rows,
  and the failure mode is a crash (loud), not a wrong number. Revisit only if the data
  source changes.

### F-3 (medium) — The win-rate target was typed into the code instead of read from the catalog (bq_08.py, win/loss)

- **What's wrong:** the program judged the win rate against a hardcoded 50% while the
  official expectation text lives in the question catalog. If the catalog floor were
  changed (say to 55%), the program would silently keep judging against 50 while the
  printed expectation row showed the new number — verdict and stated target diverging.
- **Why it matters:** a pass/fail verdict computed against a different number than the
  one the reader sees is a credibility-destroying inconsistency.
- **Resolution:** FIXED — the floor is now parsed out of the catalog's own expected
  text (">= NN%"), with loud assertions if the expectation is missing or its wording
  changes shape. A catalog change now changes the verdict, or halts loudly — it can no
  longer diverge silently.

### F-4 (low) — The "at-risk" warning band is the program's own invention (bq_08.py)

- **What's wrong:** the program labels a win rate within 2 points of the target as
  "at-risk" — a band committed in neither the plan nor the catalog.
- **Why it matters:** an uncommitted band changes how the verdict reads without anyone
  having signed off on the number behind it.
- **Resolution:** ACCEPTED — "at-risk" is sanctioned verdict vocabulary in the shared
  helpers, the band errs conservative, and the near-miss fragility is separately
  disclosed. Note it if the expectation is ever formalized.

### F-5 (low) — The bigger-deals sentence compares slightly rounded rates (bq_08.py)

- **What's wrong:** the "we lose bigger deals than we win" phrasing compares two rates
  already rounded to a tenth of a point, so a truly tiny difference could print
  "mirrors the count mix".
- **Why it matters:** the sentence could understate a real (if tiny) difference between
  the two rates.
- **Resolution:** ACCEPTED — a difference under 0.05 points is immaterial at this
  sample size; the phrasing branches are otherwise computed and exhaustive.

### F-6 (low) — An empty data window would crash rather than degrade (bq_08.py)

- **What's wrong:** an empty snapshot or empty trailing window would crash on a maximum
  over no values.
- **Why it matters:** a crash would block the answer, though it cannot publish a wrong
  number.
- **Resolution:** ACCEPTED — crash-not-wrong-number on input the demo pipeline cannot
  produce.

### F-7 (medium) — A new competitor name could silently match zero recalls (bq_09.py, disruption window)

- **What's wrong:** company names from the sales system are matched to FDA recall records
  through an alias map. A future vendor name matching no alias would keep its raw
  spelling, join zero recalls, and silently land in the "no prior recall" group —
  quietly diluting the analysis with no signal beyond an odd-looking name in a table.
- **Why it matters:** the whole answer is a join between two datasets; an unmatched name
  corrupts both sides of the comparison invisibly.
- **Resolution:** FIXED — the matcher now reports whether each name actually hit an
  alias, and the program halts with a clear message naming any unmatched vendor
  ("add alias entries first") before computing anything.

### F-8 (medium) — One verdict branch could call a declining pattern "not a decay" (bq_09.py)

- **What's wrong:** the sentence describing how win rate falls off after a recall is
  chosen from computed branches — but a weakly-declining pattern (small steps down) fell
  through to the wording "not a monotone decay", literally false against the rates
  printed beside it.
- **Why it matters:** a sentence contradicting its own numbers is worse than no sentence.
- **Resolution:** FIXED — a dedicated weakly-declining branch was added ("declines
  weakly … not every step is a clear drop"), and the fallback was reworded to the
  defensible "no uniform decay across the interior buckets".

### F-9 (low) — "Far lower" could fire on a hair's-width difference (bq_09.py)

- **What's wrong:** the tail-group comparison said "far lower" whenever the tail rate was
  below the minimum of the other groups — even by 0.1 point.
- **Why it matters:** overstated language would exaggerate a negligible difference into
  a market claim.
- **Resolution:** FIXED — "far lower" now requires at least a 10-point gap; smaller
  gaps get neutral wording that just states the rate.

### F-10 (low) — An empty group fed the verdict logic as a fake 0% (bq_09.py)

- **What's wrong:** a group with no opportunities in it produced a 0% win rate that the
  sentence-choosing logic treated as real — a fake cliff — while the small-sample warning
  skipped groups of exactly zero.
- **Why it matters:** a fake 0% could steer the verdict sentence toward a pattern that
  is not in the data.
- **Resolution:** FIXED — empty groups are now excluded from the verdict-shape
  derivation and annotated "(empty)" in the table; a too-few-groups branch words the
  verdict honestly when little remains.

### F-11 (low) — "Recalls posted since 2021" was typed text (bq_09.py)

- **What's wrong:** the table header asserted the dataset's start year as fixed text — a
  re-cut dataset (say, starting 2019) would silently falsify it.
- **Why it matters:** a typed dataset-span fact becomes silently false the moment the
  dataset is re-acquired with a different span.
- **Resolution:** FIXED — the start year is now derived from the earliest joined
  recall date, in both the report header and the data-series label.

### F-12 (low) — The most quotable table lacked its "demo of method" caveat (bq_09.py)

- **What's wrong:** the earlier review asked for the "(demo of method, not market
  evidence)" note to appear in the win-rate split table's own caption — the one most
  likely to be screenshotted — and it had not been implemented.
- **Why it matters:** a screenshot of that table alone could circulate as market
  evidence, which it explicitly is not.
- **Resolution:** FIXED — the split-table section heading now carries "(demo of
  method, not market evidence)" directly.

### F-13 (medium) — One copied price range was outside the change alarm (bq_10.py, cost of ownership)

- **What's wrong:** same class as F-1: of six figures copied from the pricing assumption
  record, the networked-capital range ($4.4k–$13.7k) was not covered by the assertions
  that promise to halt loudly on any record edit.
- **Why it matters:** a stale copied price range would silently mis-anchor the cost
  comparison the whole answer is built on.
- **Resolution:** FIXED — "$4.4k-$13.7k" is now part of the assertion.

### F-14 (low) — The five-year label was not pinned to the five-year data (bq_10.py)

- **What's wrong:** the competitor cost range is specifically a 5-year figure, but the
  horizon is a free configuration parameter — setting it to 7 would relabel the same
  range as "7-yr" and compare mismatched horizons.
- **Why it matters:** a horizon change would compare mismatched time spans under a
  correct-looking label.
- **Resolution:** FIXED — the program now asserts the configured horizon is 5,
  with a message explaining the range is horizon-specific.

### F-15 (low) — An unexpected verification status would render as settled fact (bq_10.py)

- **What's wrong:** feature-table cells special-cased only the "verify" status; any typo
  or new status value would print as a confirmed fact with no marker.
- **Why it matters:** an unverified claim would print as confirmed fact in a
  buyer-facing comparison.
- **Resolution:** FIXED — every row is now asserted to carry one of the two known
  statuses ("yes" / "verify"); anything else halts with a clear message.

### F-16 (medium) — Site flagging compared a rounded utilization to the threshold (bq_11.py, underused sites)

- **What's wrong:** whether a site is flagged as underused compared the
  display-rounded utilization against the 60% threshold — a site at a true 59.95–59.99%
  rounds to 60.0 and silently escapes flagging. Latent today (no site sits near the
  line), but it is exactly the round-before-compare trap this project's conventions
  exist to prevent.
- **Why it matters:** the flag drives customer-success intervention; a site escaping on a
  rounding artifact is a missed churn warning.
- **Resolution:** FIXED — flagging and sorting now run on the unrounded ratio;
  rounding happens only in the displayed cells.

### F-17 (low) — "Far below the fleet norm" was an unconditional claim (bq_11.py)

- **What's wrong:** the sentence asserting flagged sites sit "far below the fleet norm"
  was fixed text — it would survive a future snapshot where a flagged site sits at 59%
  against a 61% median.
- **Why it matters:** an overstated gap claim would survive a future snapshot that no
  longer supports it.
- **Resolution:** FIXED — the claim is now gated on a computed gap (at least 20
  points between the median and the least-bad flagged site); otherwise the sentence
  states the computed gap instead of the adjective.

### F-18 (low) — Missing months chart as zero utilization (bq_11.py)

- **What's wrong:** the monthly chart fills a missing site-month with 0 — for a ratio,
  zero reads as catastrophic utilization rather than missing data.
- **Why it matters:** a future data gap would chart as a utilization collapse and could
  trigger a false alarm.
- **Resolution:** ACCEPTED — the pinned snapshot is complete (every device, every
  month), so no gap exists to mis-chart. Revisit if telemetry ever gains gaps (skip or
  null instead of zero).

### F-19 (low) — An edge case renders empty parentheses in the headline (bq_11.py)

- **What's wrong:** if sites are flagged but none clears the materiality bar, the
  headline renders "0 clear the … bar ()" — empty parentheses.
- **Why it matters:** cosmetic only, but garbled punctuation in a verdict sentence
  erodes reader trust.
- **Resolution:** ACCEPTED — cosmetic; both branches are otherwise computed and the
  populated branch is the one exercised.

## Terms used

- **Latent hazard** — a defect that produces no wrong output today but will on a
  plausible future data shape.
- **Guard assert / change alarm** — an assertion that halts the program loudly if a fact
  it copied from a source record no longer matches that record.
- **Narrated, not computed** — a sentence typed as fixed text rather than derived from
  the data, so it can silently become false when the data changes.
- **Round-before-compare / knife-edge** — comparing a rounded value to a threshold, so
  rounding (not data) decides the verdict for values near the line.
- **Alias map** — the versioned table (`entity-aliases.yml`) that maps company-name
  variants to one canonical name so records join correctly across datasets.
- **Pinned snapshot (pin)** — the frozen copy of a dataset an answer is computed from,
  so the same answer is reproducible later.
- **Plan conformance** — whether the program implements exactly the definitions committed
  in its written analysis plan (`plans/BQ-NN.md`).
- **Bucket** — a group of records sharing a range (e.g. opportunities closed 0–3 months
  after a recall).
- **Materiality bar** — the minimum size (here, connected-device count) below which a
  flagged site is watched rather than escalated.
- **Monotone (decay)** — a pattern that only moves in one direction; a monotone decay
  means every step is down (or flat), never up.

## Technical appendix

### Prior-dossier fixes, verified in current code

Builds on the already-actioned output-verification dossier
`tasks/ben/_work/108-verify-redteam-market-2026-07-27.md`; settled items were not
re-flagged.

| Prior finding | Status |
|---|---|
| BQ-09 hardcoded "decays" verdict | Implemented — shape phrase derived from bucket stats (branch gaps became F-8/F-9, now also fixed) |
| BQ-11 median-by-index | Implemented — `statistics.median` on unrounded ratios, rounded once |
| BQ-08 dollar-weighted win rate absent | Implemented — headline, bullet, watch item, dedicated series |
| BQ-08 no-decision denominator sensitivity | Implemented — `rate_nd` in expectation actual, bullet, watch branch |
| BQ-07 growth-basis mismatch undisclosed | Implemented — mismatched-bases clause at every claim site |
| BQ-07 assumption guard asserts | Implemented (coverage gap became F-1, now fixed) |
| BQ-09 90-day window sensitivity | Implemented — config-driven, reported + series |
| BQ-10 missing demo banner | Implemented — banner + stand-ins caveat |
| BQ-09 demo-of-method note in split-table caption | Was NOT implemented at review time — re-flagged as F-12, **now fixed** |

### Per-module verification detail

Fix locations verified in the current working tree, 2026-07-27 (line numbers refer to
the post-fix modules).

**bq_07.py — segment share · review verdict APPROVED-WITH-FINDINGS.** Plan conformance:
conforms (NA-as-US proxy labeled; in-segment = PP3500+PP3000+IP5000 per A-003 scope;
unit and revenue share as ranges; half-year ×2 annualization labeled and dollar-only;
constant denominator stated; growth comparison directional-only with the mismatch stated
at every claim site; competitor unit split honestly `unavailable`; no point share
asserted anywhere).

| ID | Sev | Fix location | Outcome |
|---|---|---|---|
| F-1 | med | L33–34 | fixed: assert now requires "130k-230k" in `value_or_range` |
| F-2 | low | L54 (unchanged) | accepted: crash-not-wrong-number on impossible demo input |

**bq_08.py — win/loss · review verdict APPROVED-WITH-FINDINGS.** Plan conformance:
conforms (trailing-365d window anchored at pinned max close date; decided = won+lost with
no-decision reported; count and dollar-weighted rates side by side with computed
phrasing; committed denominator sensitivity next to the verdict; loss reasons on
`primary_reason`; monitoring-gap = primary OR cited with primary-only also reported;
monthly zero-filled history).

| ID | Sev | Fix location | Outcome |
|---|---|---|---|
| F-3 | med | L68–72 | fixed: floor parsed from catalog `expected` via `C.expectations_for("BQ-08")` + regex, double-asserted |
| F-4 | low | L85 (unchanged) | accepted: sanctioned vocabulary, conservative, disclosed |
| F-5 | low | L45–48 (unchanged) | accepted: 0.1pp granularity immaterial |
| F-6 | low | L35 (unchanged) | accepted: crash-not-wrong-number |

**bq_09.py — disruption window · review verdict APPROVED-WITH-FINDINGS.** Plan
conformance: conforms (population = decided opportunities with competitor incumbents;
canonicalization case-insensitive prefix, first-hit-wins, alias-file order; in-window per
config days; committed 90-day sensitivity under the split table; decay buckets with
sample sizes carried and small-sample annotation; verdict phrasing derived from computed
shape; density caveat as R2; zero-filled quarterly history).

| ID | Sev | Fix location | Outcome |
|---|---|---|---|
| F-7 | med | L50–56, L74–82 | fixed: `canon_match()` returns hit status; assert halts on unmatched incumbents |
| F-8 | med | L133–138 | fixed: weakly-monotone branch added; fallback reworded "no uniform decay" |
| F-9 | low | L139–144 | fixed: "far lower" requires `min(ir) − tail ≥ 10.0`; neutral wording otherwise |
| F-10 | low | L119–126, L213 | fixed: n=0 buckets excluded from shape logic; "(empty)" table annotation; too-few branch |
| F-11 | low | L217–224, L304–305 | fixed: `recall_start_year` derived from min joined recall date (header + series label) |
| F-12 | low | L189–190 | fixed: "(demo of method, not market evidence)" now in the split-table heading |

**bq_10.py — cost of ownership · review verdict APPROVED-WITH-FINDINGS.** Plan
conformance: conforms (our full TCO from four config params; comparable basis vs A-004's
capital+service-only range with strictly-higher-true-TCO direction stated; one class-wide
range shared by all three competitors, stated; curated feature matrix with verification
status carried and absences rendered "—"; history `unavailable`; verdict capped at
"indicative, assumption-bounded"; demo banner present; confidence read from the record).

| ID | Sev | Fix location | Outcome |
|---|---|---|---|
| F-13 | med | L38–40 | fixed: "$4.4k-$13.7k" added to the A-004 range assert |
| F-14 | low | L41–44 | fixed: `assert horizon == 5` with horizon-specific message |
| F-15 | low | L56–59 | fixed: per-row `assert verified in ("yes", "verify")` |

**bq_11.py — underused sites · review verdict APPROVED-WITH-FINDINGS.** Plan
conformance: conforms (connected-devices-only scope stated; window = 3 newest pinned
months; hours-weighted site utilization; materiality tier + watch tier both visible;
expectation evaluated as a site-level proxy with the join gap stated; account
revenue-at-risk honestly `unavailable` naming the missing site→account key; regional
revenue as context-not-attribution; ≤4-line monthly history with the pick rule stated).

| ID | Sev | Fix location | Outcome |
|---|---|---|---|
| F-16 | med | L45–53 | fixed: `util_raw` drives flagging and sort; `util` (1dp) display-only |
| F-17 | low | L131–140 | fixed: "far below" gated on computed gap ≥ 20pp; else states the gap |
| F-18 | low | L186 (unchanged) | accepted: pinned snapshot complete (331 devices × 6 months); revisit on gaps |
| F-19 | low | L60–63 (unchanged) | accepted: cosmetic edge; branches otherwise computed |

### Review-wide observations

1. The guard-assert pattern's weak point was coverage — both BQ-07 and BQ-10 transcribed
   more assumption facts than their asserts protected. Both gaps are closed; the working
   convention stands: every transcribed constant gets a matching substring assert in the
   same commit.
2. Computed-phrasing branches were the second-generation risk (wording that can
   contradict the numbers on edge shapes). The three instances found (F-8, F-9, F-17)
   are fixed; BQ-11's flag test (F-16) closed the last rounded-compare in this group.
3. Determinism and marker discipline are clean across all five modules — no unordered
   iteration reaches any report line or series; every generated figure-bearing line
   carries a same-line provenance marker.
4. Style note (not a finding): `month_range` (bq_08) and `quarter_range` (bq_09) are
   date-axis helpers of the kind the skill routes into `computations.py`; harmless as
   module-locals until a third module needs one.

```json
{"reviews": [
  {"path": "bq_modules/bq_07.py", "verdict": "APPROVED-WITH-FINDINGS",
   "summary": "Plan-conformant; honesty posture and A-003 guards verified. One guard gap: the 130k-230k annual-demand transcription is unprotected by the asserts.",
   "findings": [
     {"severity": "medium", "summary": "A-003 '130k-230k units/yr' typed as literal in growth bullet; not covered by the guard asserts — can drift silently", "disposition": "fixed: assert extended to require '130k-230k' in value_or_range"},
     {"severity": "low", "summary": "Zero FY2024 units would raise ZeroDivisionError in growth exponent; empty-snapshot paths unguarded", "disposition": "accepted: demo data non-empty; failure mode is a crash, not a wrong number"}
   ]},
  {"path": "bq_modules/bq_08.py", "verdict": "APPROVED-WITH-FINDINGS",
   "summary": "Plan-conformant; value-win-rate and ND-sensitivity fixes verified implemented. E-08.1 floor is hardcoded 50.0 instead of wired to the catalog.",
   "findings": [
     {"severity": "medium", "summary": "target=50.0 hardcoded; catalog E-08.1 change would silently diverge computed verdict from printed expectation", "disposition": "fixed: floor parsed from the catalog expected string (>= NN%) with loud asserts on absence or reshape"},
     {"severity": "low", "summary": "'at-risk' band (target-2) is a module-invented threshold committed nowhere", "disposition": "accepted: sanctioned verdict vocabulary, conservative, fragility disclosed in Watch"},
     {"severity": "low", "summary": "val_note phrasing compares 0.1pp-rounded rates; sub-0.05pp difference prints 'mirrors'", "disposition": "accepted: immaterial at this granularity"},
     {"severity": "low", "summary": "Empty snapshot/window crashes max(); unguarded", "disposition": "accepted: crash-not-wrong-number on impossible demo input"}
   ]},
  {"path": "bq_modules/bq_09.py", "verdict": "APPROVED-WITH-FINDINGS",
   "summary": "Plan-conformant; computed decay phrasing and 90d sensitivity fixes verified. Gaps: no alias-coverage guard for new incumbents; two shape-phrase branches can contradict their own printed rates; split-table demo caption from prior dossier not implemented.",
   "findings": [
     {"severity": "medium", "summary": "Unaliased incumbent_vendor silently joins zero recalls and lands in no-prior/out-of-window — no coverage guard", "disposition": "fixed: canon_match() tracks alias hits; assert halts naming any unmatched incumbent"},
     {"severity": "medium", "summary": "Shape branch C prints 'not a monotone decay' for weakly-monotone declining profiles — a false claim vs its own rates", "disposition": "fixed: weakly-monotone branch added; fallback reworded to 'no uniform decay'"},
     {"severity": "low", "summary": "Tail clause claims 'far lower' for any tail below min interior rate, even by 0.1pt", "disposition": "fixed: 'far lower' requires a >=10pt margin; neutral phrasing otherwise"},
     {"severity": "low", "summary": "Empty bucket feeds shape logic as 0.0% and escapes the small-n annotation (0<n<10)", "disposition": "fixed: n=0 buckets excluded from shape derivation; annotated '(empty)'; too-few-buckets branch added"},
     {"severity": "low", "summary": "'FRN recalls posted since 2021' table header is a typed dataset-span literal", "disposition": "fixed: start year derived from min joined recall date (header + series label)"},
     {"severity": "low", "summary": "Prior-dossier fix (demo-of-method note in split-table caption) not implemented; caveats stay outside the table", "disposition": "fixed: '(demo of method, not market evidence)' added to the split-table section heading"}
   ]},
  {"path": "bq_modules/bq_10.py", "verdict": "APPROVED-WITH-FINDINGS",
   "summary": "Plan-conformant; demo banner fix verified; verdict correctly capped. Guard gap: networked-capital range ($4.4k-$13.7k) transcribed outside the A-004 asserts; horizon not pinned to the 5-yr range.",
   "findings": [
     {"severity": "medium", "summary": "CAP_NET_LO/HI ($4.4k-$13.7k) transcribed from A-004 but not covered by the guard assert — can drift silently", "disposition": "fixed: '$4.4k-$13.7k' added to the assert"},
     {"severity": "low", "summary": "COMP_TCO range is A-004's 5-yr figure but horizon_years is free — horizon!=5 would mislabel the comparison", "disposition": "fixed: assert horizon == 5 beside the A-004 asserts"},
     {"severity": "low", "summary": "cell() treats any verified value other than 'verify' as settled fact — unexpected status renders unmarked", "disposition": "fixed: per-row assert verified in ('yes','verify')"}
   ]},
  {"path": "bq_modules/bq_11.py", "verdict": "APPROVED-WITH-FINDINGS",
   "summary": "Plan-conformant; statistics.median-on-raw-ratios fix verified implemented. One numeric trap: flagging compares rounded utilization against the threshold.",
   "findings": [
     {"severity": "medium", "summary": "Underuse flag compares 1dp-rounded utilization vs threshold — a 59.95-59.99% site escapes flagging (latent)", "disposition": "fixed: flagging and sort run on util_raw; rounding display-only"},
     {"severity": "low", "summary": "'flagged sites sit far below the fleet norm' is an unconditional literal data-shape claim", "disposition": "fixed: gated on computed gap >= 20pp; otherwise the computed gap is stated"},
     {"severity": "low", "summary": "Monthly ratio timeseries zero-fills missing site-months as 0%, conflating missing with catastrophic", "disposition": "accepted: pinned snapshot is complete; revisit if telemetry gains gaps"},
     {"severity": "low", "summary": "Headline renders '()' when flagged is non-empty but material is empty", "disposition": "accepted: cosmetic edge; branches otherwise computed"}
   ]}
]}
```
