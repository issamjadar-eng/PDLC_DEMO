# Code review — shared helpers and nine inline analysis computations, 2026-07-27

_Demo sample data — not for clinical use._
_Personal work artifact (task-support, not a controlled deliverable)._

**What was reviewed**: the shared engine file that all thirty business-question answers
depend on — its common helper functions (data loading, percentage math, expectation
scoring, report rendering, date/window logic, module dispatch) and the nine analysis
computations written inline in the same file (clearance cycle time, clearance sweep,
complaints vs thresholds, adverse-event profile, campaign coverage, failure clusters,
customer struggle and cost, capacity outlook, fleet currency).

- **Artifact**: `docs/project/commercial/computations.py`, reviewed against the
  commercial skill's computation contract, the nine analysis plans
  (`docs/project/commercial/plans/BQ-{06,12,18,19,23,24,25,26,27}.md`), the pinned data
  snapshots, and two assumption records (A-001, A-002)
- **Reviewer**: AI code reviewer (read-only review; task ben/108; filed via
  `record-code-review`)
- **Date**: 2026-07-27
- **Verdict in one line**: approved with findings — the shared helpers every answer
  leans on are correct; 17 issues raised (no serious ones, 7 moderate, 10 minor);
  **11 have since been fixed and 6 were explicitly accepted with rationale** — every
  outcome re-verified in the current code before this report was written.

## Plain-language summary

This is a code review of the shared engine behind the business-question answers: the
common helper functions that all thirty answers use, plus nine analyses written directly
in the same file. The helpers got extra scrutiny because a bug there would taint every
answer at once — and they were found correct: the statistics, the date and window logic,
the pass/fail scoring, and the guarantee that the same input always produces the same
output all check out. The review raised 17 issues, none of which invalidates a number
published today: seven moderate ones (values rounded before being compared to decision
thresholds, a broken analysis module that could be mistaken for a missing one, sentences
typed as fixed text that would quietly become false on new data, and unexpected data
categories being absorbed silently in the optimistic direction) and ten minor ones.
Eleven of the issues have since been fixed in the code and six were consciously accepted,
each with a written reason. Every fix and every acceptance was re-verified against the
current code before this report was written.

## What we checked

- The shared helper functions, line by line — because a defect there would corrupt all
  thirty answers at once (statistics, percentage math, expectation scoring, date and
  window arithmetic, report rendering, error behavior on missing data).
- Repeatability: same input, same output — no clocks, no randomness, no
  order-dependent iteration reaching any published line.
- Whether each of the nine inline analyses implements exactly what its written plan
  commits to.
- Whether verdict sentences are computed from the data or typed as fixed text.
- Whether values are rounded before or after being compared to decision thresholds.
- What happens when the data grows a new category or status value the code has never
  seen — loud failure, visible bucket, or silent absorption.
- Whether items promised by earlier reviews were actually implemented.

## Findings

All resolutions below were verified against the current code on 2026-07-27. Line
references and the legacy finding IDs (H-*, B*-*) that the code comments cite live in
the technical appendix.

### F-1 (medium) — Percentages were rounded before being compared to thresholds (shared helper + three analyses)

- **What's wrong:** the shared percentage helper rounds to one decimal, and three
  analyses compared its output against decision thresholds: the update-campaign pause
  trigger, the complaint-rate breach test, and the capacity shortfall/thin/stability
  verdicts. A true rate of 15.04% rounds to 15.0 and would not trip a 15% threshold that
  the unrounded value trips. Today's data sits far from every boundary, so no current
  verdict is wrong — but the pause trigger is safety-adjacent.
- **Why it matters:** for values near a line, rounding — not the data — would decide a
  verdict that can pause a field campaign.
- **Resolution:** FIXED — a compare-side helper (`pct_raw`, unrounded) was added and
  documented; the pause trigger, the breach test, and all three capacity verdicts now
  compare unrounded values, with rounding applied only when displaying.

### F-2 (medium) — A broken analysis module was indistinguishable from a missing one (module dispatch)

- **What's wrong:** the dispatcher that loads per-question analysis modules caught
  "module not found" around the entire import. A module that exists but whose own code
  imports a missing dependency raises the same error type — it was swallowed, and the
  engine reported "no computation for this question" instead of surfacing the breakage.
- **Why it matters:** a real defect would be mislabeled as "not implemented" and could
  sit unnoticed indefinitely.
- **Resolution:** FIXED — the dispatcher now re-raises the error unless the missing
  module is literally the one being dispatched, so a broken module fails loudly with its
  real error.

### F-3 (low) — A mistyped expectation ID would silently vanish (expectation scoring)

- **What's wrong:** the pass/fail scorer joined computed results to the catalog's
  expectations by ID, iterating the catalog only — a result keyed by a mistyped ID
  simply disappeared with no signal.
- **Why it matters:** a typo would silently drop a pass/fail result from the published
  scorecard.
- **Resolution:** FIXED — the scorer now halts with a clear message naming any
  computed result whose ID is not in the catalog.

### F-4 (low) — A zero denominator renders as "0%" instead of "not applicable" (percentage helper)

- **What's wrong:** dividing by an empty group displays 0% — a truthless number — rather
  than an honest "n/a".
- **Why it matters:** a "0%" where "not applicable" belongs reads as a real measurement.
- **Resolution:** ACCEPTED — no group in the current data can be empty (the fleet has
  hundreds of rows on both sides of every split); revisit with a
  none-propagating variant if a genuinely emptiable group appears.

### F-5 (low) — A vertical-bar character in catalog text would break the report tables (rendering)

- **What's wrong:** catalog text is inserted into markdown tables without escaping; a
  pipe character in it would break the table layout.
- **Why it matters:** a broken table would garble the published report for every reader.
- **Resolution:** ACCEPTED — the catalog is project-owned, reviewed input and is
  currently clean.

### F-6 (medium) — The "fastest frequent filer" was picked from a pre-trimmed list (BQ-06, clearance cycle time)

- **What's wrong:** the plan defines a frequent filer as any applicant with two or more
  clearances; the code first trimmed to the top six applicants by volume and only then
  filtered — coincidentally exact today (exactly six of fifteen applicants qualify), but
  the moment a seventh qualifies, the true fastest frequent filer could fall outside the
  trimmed list and the headline would be silently wrong.
- **Why it matters:** a headline claim resting on a coincidence between two numbers.
- **Resolution:** FIXED — the two-or-more filter now runs over the whole applicant
  set first; the top-N cut limits only what the table displays, and the "fastest" pick
  is computed over all qualifying applicants.

### F-7 (low) — "Since 2021" rides on the dataset's acquisition scope (BQ-06)

- **What's wrong:** the headline says "since 2021" with no year filter in the code — true
  because the dataset's committed scope starts in 2021, but it would rot if the scope
  ever widened.
- **Why it matters:** the claim would silently falsify if the dataset's scope ever
  widened.
- **Resolution:** ACCEPTED — the scope is committed in the plan's data section and
  carried by the dataset itself; noted for the dataset's next reviewer.

### F-8 (low) — The "90-day" windows were actually 91 days, unevenly (BQ-18 complaints, BQ-12 sweep)

- **What's wrong:** the complaints analysis compared a current window of 91 days
  (inclusive on both ends) against a prior window of 90 — giving the "rising volume"
  test a built-in upward bias of about one day. The clearance sweep had the same
  one-extra-day label mismatch (harmless there — no cross-window comparison).
- **Why it matters:** the extra day nudges the rising-volume test toward firing when it
  should not.
- **Resolution:** FIXED — the complaints windows are now symmetric half-open spans of
  exactly the configured length; the sweep window was corrected to exactly the labeled
  number of days.

### F-9 (low) — A chart's method note had "90-day" typed in (BQ-18)

- **What's wrong:** the window-trend series' method description said "trailing 90-day
  window" as fixed text while the width is a configuration parameter.
- **Why it matters:** the note would misdescribe the chart after a configuration change.
- **Resolution:** FIXED — the description now interpolates the configured window
  length.

### F-10 (medium) — The "rate comparison is BLOCKED" sentence was fixed text (BQ-19, adverse events)

- **What's wrong:** the analysis correctly refuses to publish adverse-event *rates* until
  the installed-base assumption is quantified — but the "BLOCKED / not yet quantified"
  wording was typed text. The code computed whether the assumption had been quantified
  and used it only to flip a data-classification field; if the assumption were ever
  quantified, the edition would contradict itself (a "ready" classification under a
  headline still saying "blocked").
- **Why it matters:** this question is the project's honesty showcase; a
  self-contradicting edition there is maximally embarrassing.
- **Resolution:** FIXED — if the assumption is quantified while the rate calculation
  remains unimplemented, the program now halts loudly with instructions, before writing
  anything. The blocked wording is reachable only in the genuinely blocked state, making
  it a computed condition rather than a narration.

### F-11 (low) — Unmatched manufacturer names get cosmetically re-cased (BQ-19)

- **What's wrong:** the plan says unmatched names "stay raw and visible"; the code
  title-cases them — a cosmetic transform that could in principle merge two case-variant
  spellings.
- **Why it matters:** two spelling variants of one company could merge or split
  incorrectly in the counts.
- **Resolution:** ACCEPTED — harmless today; noted for the next plan/code sync.

### F-12 (low) — The 95% coverage target is judged by a 100%-completion projection (BQ-23, campaign coverage)

- **What's wrong:** the expectation asks whether each region reaches 95% coverage by the
  close date, but the projection computes when *all* remaining devices finish — a region
  could hit 95% in time yet be flagged as missing.
- **Why it matters:** a region could be flagged as missing its target when it actually
  meets it — a false alarm, never a false pass.
- **Resolution:** ACCEPTED — the direction is conservative (never optimistic), and
  the plan itself defines projected finish as remaining ÷ rate. Noted: if the 95%
  distinction ever matters, project the 95% date explicitly.

### F-13 (medium) — A new status value would be silently absorbed in the optimistic direction (BQ-24/25/26, campaign analyses)

- **What's wrong:** three campaign analyses define their populations by complement
  ("attempted = everything not scheduled"; "remaining = everything not completed"). The
  data's status vocabulary is exactly five known values today — but a new upstream status
  (say "cancelled") would silently join "attempted" as a non-failure, diluting the pause
  trigger, and join "remaining" in the capacity outlook. No guard existed.
- **Why it matters:** silent vocabulary drift would bias a safety-adjacent trigger
  toward not firing.
- **Resolution:** FIXED — a shared vocabulary guard (`assert_vocab`) was added and is
  called by all four campaign-data consumers immediately after loading; any unknown
  status halts the run with a message naming the values.

### F-14 (low) — A promised one-clause caveat from the earlier economics review was missing (BQ-26, capacity outlook)

- **What's wrong:** the remote-conversion mitigation lacked the caveat that the remote
  path carried the implicated failure mode (all the rollbacks were remote installs) —
  moot while zero devices are convertible, live the moment adapters convert the backlog.
- **Why it matters:** without the caveat, the recommended recovery lever hides a known
  exposure.
- **Resolution:** FIXED — the caveat is now computed from the pinned data (rollbacks
  by method) and appended to the mitigation text whenever remote rollbacks exist, with
  the counts interpolated — not typed as a fixed sentence.

### F-15 (medium) — "(All on the 2.9.x line)" was a typed fact (BQ-27, fleet currency)

- **What's wrong:** the legacy-fleet firmware posture was asserted as prose. True against
  both pinned snapshots today, but invisible to the claim lint and silently false the
  first time a legacy device reports anything else.
- **Why it matters:** a typed fact invisible to the claim lint silently falsifies on the
  next fleet refresh.
- **Resolution:** FIXED — the qualifier is now computed from the observed firmware
  versions: it prints "all on 2.9.x line" only when that is true, otherwise lists the
  actual versions.

### F-16 (medium) — Unrecognized firmware versions counted as up-to-date (BQ-27)

- **What's wrong:** a firmware version missing from the how-far-behind map defaulted to
  "zero versions behind" — the optimistic direction on a metric the report itself frames
  as patient-safety exposure. Today the map covers every observed version, so nothing is
  misclassified — but a new release or a data typo would understate "behind" with no
  signal.
- **Why it matters:** an optimistic silent default on a safety-framed metric is the worst
  combination this review looks for.
- **Resolution:** FIXED — unmapped versions are now their own surfaced bucket:
  excluded from the "current" counts, called out in the verdict sentence, given a warning
  line in the report telling the reader to extend the map, and included as a data point.

### F-17 (low) — Fragile report-assembly arithmetic and one unused variable (BQ-24/06/27, BQ-25)

- **What's wrong:** three analyses insert a bullet into the report by counting lines
  backwards from the end — valid output today, brittle to reordering; one analysis
  assigns a variable it never uses.
- **Why it matters:** brittle assembly code risks misplacing report lines on a future
  edit; cosmetic today.
- **Resolution:** ACCEPTED — cosmetic; fold into the next touch of the file.

## Terms used

- **Shared helpers** — the common functions in `computations.py` every business-question
  answer calls; a defect there affects all thirty answers at once.
- **Narrated, not computed** — a sentence typed as fixed text rather than derived from
  the data, so it can silently become false when the data changes.
- **Knife-edge / round-before-compare** — comparing a rounded value to a threshold, so
  rounding (not data) decides the verdict for values near the line.
- **Complement-defined population** — a group defined as "everything that is not X",
  which silently absorbs any new category the data grows.
- **Pause trigger** — the configured rule that flags an update-campaign cohort for
  pausing when its failure rate crosses a threshold.
- **Pinned snapshot (pin)** — the frozen copy of a dataset an answer is computed from,
  so the same answer is reproducible later.
- **Assumption record (A-NNN)** — a versioned file documenting an estimate (e.g.,
  installed base) with its confidence and refresh triggers; analyses cite it instead of
  burying the estimate in code.
- **Expectation (E-NN.N)** — a catalog-declared pass/fail commitment an answer is scored
  against.
- **Evidence class** — each published figure's label: measured, derived, assumed, or
  unavailable.
- **Denominator** — the base a rate is computed against (e.g., installed devices);
  without one, counts cannot honestly become rates.
- **Determinism** — the guarantee that the same pinned input always produces
  byte-identical output (no clocks, no randomness, no order-dependent iteration).

## Technical appendix

### Reviewed artifact and scope

Reviewed at sha256 `bf7fb8fa4263cc290a938eb0eb99fe39c1a5cc094393d2a041d8446319a28710`
(1368 lines; deterministic checks on that sha: static_lint pass, poison_scan pass,
determinism pass). The fix pass landed after the review, so the current file (1471
lines) differs from the reviewed sha; every resolution below was verified in the current
working tree on 2026-07-27. Scope: shared helpers (`load_pin_csv`, `params_for`/`_entry`,
`evaluate_expectations`, `expectations_section`, `narrative_section`, `write`, `pct`,
`_median`, `week_start`, `week_range`, `weekly_completion_lines`, `module_dispatch`,
`DISPATCH`/`main`) plus the nine inline computations bq06, bq12, bq18, bq19, bq23, bq24,
bq25, bq26, bq27. Grounding read before review: commercial SKILL.md v11 (computation
contract, code-quality rules), the nine plans, the prior dossiers
(`108-adversarial-verify-field-slice-2026-07-22.md`, `108-redteam-BQ-26-2026-07-22.3.md`,
`108-verify-redteam-{fieldsafety,economics}-2026-07-27.md`), the pinned snapshots
(`internal-fleet@{2026-07-22,2026-07-27}`,
`internal-upgrade-campaign@{2026-07-22.2,2026-07-27}`,
`openfda-510k-infusion@2026-07-22`), and assumption records A-001/A-002. Settled items
(BQ-24/25 basis switch, BQ-26 refit findings 1–4, F26-1 derivation strings) were
verified as implemented, not re-flagged.

### Shared helpers verified correct (checked, not assumed)

- **`_median`** (now L1106–1111): correct for odd n (true middle) and even n (mean of the
  two middles, rounded 1dp); returns nothing on empty input. Cosmetic asymmetries only
  (odd-n unrounded vs even-n rounded; mid-file location; `bq_11.py` independently uses
  `statistics.median` — also correct).
- **Expectation scoring + `[config]` dedupe** (L69–106): exact-string membership on a
  fresh list copy — no off-by-one, no double marker, no caller-list mutation; verified
  against every inline caller. Every catalog expectation for the nine questions
  (E-18.1/2, E-23.1/2, E-24.1, E-26.1) is evaluated by its computation; the
  `not-evaluable` fallback is correct for future catalog additions.
- **Week/date logic** (L127–157): ISO-Monday buckets; inclusive Monday walk; zero-filled
  spans so stalls flatline visibly; 28-day trailing windows are exactly 28 days ÷ 4;
  ISO-string comparisons used only between ISO dates.
- **`load_pin_csv` error behavior** (L46–50): missing pin key → KeyError; missing
  snapshot file → FileNotFoundError — both loud (non-zero exit; edition discarded).
  Messages are terse but the failure mode is safe.
- **`write` / determinism** (L109–111): insertion-ordered JSON is deterministic on
  Python 3.7+; all groupings iterate sorted sets/dicts or CSV row order; alias/keyword
  list order is stable; no clocks, no randomness, no network.

### Finding-by-finding verification detail

Legacy IDs are the ones cited in the code comments and prior dossiers.

| ID (legacy) | Sev | Fix location | Outcome |
|---|---|---|---|
| F-1 (H-1) | med | L114–124; bq24 L363–367; bq18 L1319–1321, L1327, L1348; bq26 L614–619, L653–655 | fixed: `pct_raw` compare-side helper; pause/breach/capacity verdicts compare unrounded |
| F-2 (H-2) | med | L1447–1453 | fixed: re-raise unless `e.name` is the dispatched module |
| F-3 (H-3) | low | L76–79 | fixed: SystemExit naming unknown computed expectation IDs |
| F-4 (H-4) | low | L119 (unchanged) | accepted: no caller stratum currently empties |
| F-5 (H-5) | low | L96–106 (unchanged) | accepted: catalog-controlled input |
| F-6 (B06-1) | med | L1126–1135 | fixed: ≥2-clearance filter before top-N; fastest picked over all eligible |
| F-7 (B06-2) | low | L1138, L1182 (unchanged) | accepted: plan-committed dataset scope |
| F-8 (B18-1) | low | bq18 L1302–1313; bq12 L1211–1213 | fixed: symmetric half-open windows; sweep window exactly N days |
| F-9 (B18-2) | low | L1421 | fixed: derivation string interpolates `{window}` |
| F-10 (B19-1) | med | L1013–1021, L1036–1039 | fixed: quantified-model state fails loud pre-output; BLOCKED wording gated |
| F-11 (B19-2) | low | L1006 (unchanged) | accepted: cosmetic; note for plan/code sync |
| F-12 (B23-1) | low | bq23 (unchanged) | accepted: plan defines projection as remaining ÷ rate; conservative direction |
| F-13 (B24-1) | med | L29–43; called at L189, L348, L477, L586 | fixed: `assert_vocab` guard in all four campaign consumers |
| F-14 (B26-1) | low | L702–709, L718 | fixed: rollback-path caveat computed from pin, appended to mitigation |
| F-15 (B27-1) | med | L917–920, L953 | fixed: qualifier computed from observed firmware versions |
| F-16 (B27-2) | med | L900–908, L929–933, L942–945, L970–973 | fixed: unmapped-firmware bucket — excluded from current, in headline, ⚠ line, data point |
| F-17 (cleanup) | low | L443, L961, L1174; L479 (unchanged) | accepted: fold `lines.insert(-N)` + unused `assume_path` into next touch |

### Per-computation plan-conformance summary (review verdicts at review time)

- **bq06 — clearance cycle time · CONFORMS-WITH-FINDINGS.** Interval = decision −
  received in days; per-applicant + overall medians (median not mean, per plan);
  per-decision-year history; our-side series honestly `unavailable`. Findings F-6, F-7.
- **bq12 — clearance sweep · CONFORMS.** Window anchored at newest pinned decision date;
  roadmap flags are computed keyword matches, stated as triage not capability judgment;
  empty-window branches handled; no findings of its own (window-length label fixed under
  F-8).
- **bq18 — complaints vs thresholds · CONFORMS-WITH-FINDINGS.** Rates per 100 fleet
  devices with the sanctioned denominator stated; thresholds from config with the
  stand-in risk emitted; 130% trend rule with sane zero-prior guard; zero-filled top-3
  trend. Findings F-8, F-9 (+ F-1 call site). Noted, not flagged: an empty current
  window would crash loudly — acceptable for a fail-loud demo pipeline.
- **bq19 — adverse-event profile · CONFORMS-WITH-FINDINGS.** Counts-never-rates enforced
  structurally; versioned alias normalization; lag-trimmed monthly history; no internal
  vs MAUDE numeric juxtaposition. Findings F-10, F-11. Noted: with ≤2 months of data the
  lag trim is skipped — unreachable against a 2023-onward dataset.
- **bq23 — campaign coverage · CONFORMS-WITH-FINDINGS.** Latest-completion anchor is
  plan-committed for this question (deliberately different from BQ-26); stall → Issue
  with labeled projection, never a fake date; misses computed with safe short-circuit
  ordering. Finding F-12.
- **bq24 — failure clusters / pause trigger · CONFORMS-WITH-FINDINGS.** Per-attempted
  rate with whole-cohort context (adversarial-verification remedy verified); pause rule
  fully config-driven; dated-events-only retry trend with the exclusion stated; "worst"
  computed via max. Findings F-13 (+ F-1's highest-stakes call site), F-17.
- **bq25 — customer struggle & cost · CONFORMS.** Tickets and denominator both over
  attempted devices (remedy verified); customer cost read from assumption record A-002
  (nothing hardcoded), presented as assumed with confidence interpolated; "highest in
  region" computed via max. Nit folded into F-17.
- **bq26 — capacity outlook (2026-07-27 refit) · CONFORMS.** All five refit commitments
  verified in code: uniform 28-day stall rule; snapshot-as-of anchor + latest-completion
  sensitivity with a computed CHANGED/UNCHANGED sentence; thin-margin watch rule with
  computed largest-load qualifier; FSE-days + connectivity join (join miss counts as NOT
  convertible — conservative); status-set-explicit derivation strings (F26-1 actioned).
  Residual F-14 (F26-2) now fixed. Edge accepted: zero weeks left degenerates the
  required rate to the remaining count — odd units, loud in context.
- **bq27 — fleet currency · CONFORMS-WITH-FINDINGS.** Behind-by mapping from config;
  PP3500 scope with PP3000 counted separately, never mixed; connectivity comparison
  descriptive only; history honestly `unavailable`. Findings F-15, F-16, F-17.

### Review-wide observations

- No finding invalidated a published number in the current editions — every moderate
  finding was a latent hazard or a narrated fact still true against today's pins.
- The two fixes the review ranked most important — unrounded threshold comparisons
  (F-1, the pause trigger being the stakes) and the module-dispatch exception
  discrimination (F-2) — are both in place.
- The engine-level note from a prior friction log (population exclusions missing from
  one series' derivation method) remains open at the engine level and was not re-flagged
  here.

```json
{"reviews": [{"path": "computations.py", "verdict": "approved-with-findings", "summary": "Shared helpers sound (median/dedupe/windows/determinism verified; loud pin errors); BQ-26 refit commitments all implemented; findings were latent hazards and literal-fact rot risks, none invalidated a current published number. All 17 findings dispositioned: 11 fixed, 6 accepted (verified in current code 2026-07-27).", "findings": [
  {"severity": "medium", "summary": "helper/pct: thresholds compared on rounded rates (bq24 pause, bq18 breach, bq26 verdicts) — knife-edge risk", "disposition": "fixed: pct_raw compare-side helper added; bq24/bq18/bq26 decision sites compare unrounded, round at render"},
  {"severity": "medium", "summary": "helper/module_dispatch: ModuleNotFoundError inside an existing bq module swallowed as 'no computation'", "disposition": "fixed: re-raises unless e.name is the dispatched module"},
  {"severity": "low", "summary": "helper/evaluate_expectations: computed results with unknown E-ids silently dropped", "disposition": "fixed: SystemExit names any computed result id not in the catalog"},
  {"severity": "low", "summary": "helper/pct: zero denominator renders 0.0 not n/a", "disposition": "accepted: no caller stratum currently empties; revisit if one can"},
  {"severity": "low", "summary": "helper/expectations_section: unescaped pipes in catalog text break markdown tables", "disposition": "accepted: catalog-controlled input"},
  {"severity": "medium", "summary": "bq06: 'fastest frequent filer' computed from top_n-truncated set; exact today by coincidence (6 of 15 >=2)", "disposition": "fixed: >=2-clearance filter applied before top_n; fastest picked over all eligible applicants"},
  {"severity": "low", "summary": "bq06: 'since 2021' scope literal rides on dataset acquisition scope (true vs pin)", "disposition": "accepted: plan-stated dataset scope"},
  {"severity": "low", "summary": "bq18: current window 91d inclusive vs prior 90d — slight upward bias on 130% rising test; bq12 label same +1d", "disposition": "fixed: symmetric half-open windows in bq18; bq12 window exactly the labeled length"},
  {"severity": "low", "summary": "bq18: window-trend derivation string hardcodes '90-day' instead of window param", "disposition": "fixed: derivation string interpolates the window param"},
  {"severity": "medium", "summary": "bq19: BLOCKED/'not yet quantified' headline is a literal; rate_ready computed but unused - rots if A-001 quantifies", "disposition": "fixed: rate_ready==True now fails loud before output; BLOCKED wording reachable only in the truly blocked state"},
  {"severity": "low", "summary": "bq19: unmatched manufacturer names .title()-cased; plan says 'stay raw'", "disposition": "accepted: cosmetic, note for plan/code sync"},
  {"severity": "low", "summary": "bq23: E-23.1 95% target judged by 100%-completion projection; target_pct unused in math (conservative)", "disposition": "accepted: plan defines projection as remaining/rate"},
  {"severity": "medium", "summary": "bq24/25/26: complement status sets (!= scheduled / not in COMPLETED) absorb vocabulary drift, diluting the pause trigger", "disposition": "fixed: assert_vocab guard asserts observed statuses subset of known vocabulary in all four campaign consumers"},
  {"severity": "low", "summary": "bq26: F26-2 residual — R1 mitigation lacks remote-path-rollback caveat (moot while convertible=0)", "disposition": "fixed: caveat computed from rollbacks-by-method in the pin and appended to the mitigation"},
  {"severity": "medium", "summary": "bq27: '(all on 2.9.x line)' narrated string-literal fact — true vs both pins, rots on refresh", "disposition": "fixed: qualifier computed from observed PP3000 firmware versions; lists actual versions otherwise"},
  {"severity": "medium", "summary": "bq27: behind_map.get(fw,0) counts unmapped firmware as current — optimistic default on safety-framed metric", "disposition": "fixed: unmapped firmware surfaced as its own bucket — excluded from current counts, named in headline, warning line, data point"},
  {"severity": "low", "summary": "bq24/06/27/25: fragile lines.insert(-N) tail arithmetic + unused assume_path var — cosmetic", "disposition": "accepted: fold into next touch"}
]}]}
```
