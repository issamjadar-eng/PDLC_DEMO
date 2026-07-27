# Code review — `computations.py` shared helpers + nine inline computations (ben/108, 2026-07-27)

_Personal work artifact (task-support, not a controlled deliverable). Independent AI-assistant
code review, READ-ONLY: no file besides this dossier was modified. Filed via
`record-code-review` by the main session._

**Artifact under review**: `docs/project/commercial/computations.py` (1368 lines)
**sha256**: `bf7fb8fa4263cc290a938eb0eb99fe39c1a5cc094393d2a041d8446319a28710`
(deterministic checks on this sha: static_lint pass · poison_scan pass · determinism pass; no prior review on file)

**Scope**: shared helpers (`load_pin_csv`, `params_for`/`_entry`, `evaluate_expectations`,
`expectations_section`, `narrative_section`, `write`, `pct`, `_median`, `week_start`,
`week_range`, `weekly_completion_lines`, `module_dispatch`, `DISPATCH`/`main`) and the nine
inline computations bq06, bq12, bq18, bq19, bq23, bq24, bq25, bq26, bq27.

**Grounding read before review**: `.claude/skills/commercial/SKILL.md` v11 (§ computation
contract, § Code quality, no-string-literal-facts rule, shared-helper rule); the nine plans
`plans/BQ-{06,12,18,19,23,24,25,26,27}.md`; prior dossiers
`108-adversarial-verify-field-slice-2026-07-22.md`, `108-redteam-BQ-26-2026-07-22.3.md`,
`108-verify-redteam-{fieldsafety,economics}-2026-07-27.md`. Settled items (BQ-24/25 basis
switch, BQ-26 refit findings 1–4, F26-1 derivation strings) were **verified as implemented,
not re-flagged**. Data-facing claims were checked against the pinned snapshots
(`internal-fleet@{2026-07-22,2026-07-27}`, `internal-upgrade-campaign@{2026-07-22.2,2026-07-27}`,
`openfda-510k-infusion@2026-07-22`) and the corpus assumption records A-001/A-002.

---

## Shared helpers (extra scrutiny — a bug here taints all 30 questions)

### Verified correct (checked, not assumed)

- **`_median`** (L1021–1026): correct for odd n (`vals[n//2]`, true middle) and even n
  (mean of the two middles, rounded 1dp); `None` on empty. The shared median the SKILL.md
  mandates is right. Two cosmetic asymmetries, no numeric error: odd-n returns the raw
  (unrounded) value while even-n rounds; and the helper sits mid-file at L1021 next to bq06
  rather than with the other helpers — module authors scanning the top of the file may miss
  it (`bq_11.py` independently uses `statistics.median` instead; correct, but the
  one-median-to-rule-them-all intent is already fraying).
- **`evaluate_expectations` + `expectations_section` `[config]` dedupe** (L74–80): the
  recently-added dedupe is exact-string membership (`"config: commercial.yml" not in
  ev_items`) with a single conditional append on a fresh `list(...)` copy — no off-by-one,
  no double marker, no mutation of the caller's list. Checked against every inline caller:
  none currently passes `config: commercial.yml` in expectation evidence, so the append
  fires exactly once per row; a module that does pass it is not double-stamped. Correct.
- **Catalog-side coverage**: every expectation declared in `commercial.yml` for the nine BQs
  (E-18.1/2, E-23.1/2, E-24.1, E-26.1) is evaluated by its computation; the
  `not-evaluable` fallback path is correct for future catalog additions.
- **Week/date logic**: `week_start` = ISO-Monday bucket; `week_range` inclusive Monday walk;
  `weekly_completion_lines` zero-fills across the full span so stalls flatline (the
  dataviz rule). 28-day trailing windows are `[anchor−27d, anchor]` inclusive = exactly
  28 days ÷ 4. ISO-string date comparisons are used only where both sides are ISO dates
  (safe). Correct.
- **`load_pin_csv` error behavior**: a missing pin key raises `KeyError`, a missing
  snapshot file raises `FileNotFoundError` — both are **loud** (non-zero exit; the engine
  discards the edition when report/data are not written). Not silent. The messages are
  cryptic (`KeyError: 'commercial/...'`) but the failure mode is safe. Accept.
- **`write` / determinism**: `json.dumps` without `sort_keys` is deterministic on 3.7+
  insertion order; all groupings iterate `sorted(...)` sets/dicts (regions, cohorts,
  months, rollback sites) or CSV row order; YAML list order (aliases, watch_keywords) is
  stable. No clocks, no RNG, no network. The replay-pass result is corroborated by reading.

### Findings

- **H-1 (medium) — `pct`/rounding: round-before-compare exported to callers.** `pct` and
  the inline `round(x,1)` rates are compared *after* rounding at every decision boundary:
  bq24's pause trigger (`s["rate"] > thr`, L331 — rate is `pct`-rounded), bq18's threshold
  breach (`rate(n) > t`, L1230 — 2dp-rounded), and bq26's shortfall/thin/stability
  classifications (`cur < req`, `cur < req*headroom`, `verdict_stable`, L596–611 — both
  sides rounded 1dp in `region_stats`). A true rate of 15.04% rounds to 15.0 and does NOT
  trip a 15% pause threshold that the unrounded value trips. Today's data sits far from
  every boundary (worst cohort 31.4% vs 15; complaint rates vs 2.0/3.0), so no current
  verdict is wrong — but the pattern puts a safety-adjacent trigger (bq24) on the wrong
  side of a knife-edge by up to 0.05pp. Disposition — **fix**: compare unrounded values;
  round only at render time.
- **H-2 (medium) — `module_dispatch` swallows real ModuleNotFoundErrors as "no
  computation".** L1346–1350 catches `ModuleNotFoundError` around the *entire* import. A
  `bq_modules/bq_nn.py` that EXISTS but whose body imports a missing dependency (e.g.
  `import pandas` on a machine without it) raises the same exception type — swallowed,
  `None` returned, and `main` reports `no computation for BQ-NN`. A broken module is
  indistinguishable from an absent one; the failure is mis-labeled, not surfaced.
  Disposition — **fix**: re-raise unless `e.name` is the module being dispatched
  (`except ModuleNotFoundError as e: if e.name != mod_name and not mod_name.startswith(e.name): raise; return None`),
  or probe `importlib.util.find_spec(mod_name)` first and never catch during the real import.
- **H-3 (low) — `evaluate_expectations` silently drops computed results with unknown
  ids.** The join iterates catalog expectations only; a result keyed by a typo'd id
  (`"E-23.3"`) vanishes with no signal — the inverse of the deliberate `not-evaluable`
  path. All nine inline callers currently match the catalog exactly (checked). Disposition
  — **fix** (cheap): after the loop, raise/print on `set(results) − {e["id"] for e in exps}`.
- **H-4 (low) — `pct(n, 0) == 0.0` renders a truthless "0%".** A zero denominator
  (e.g. bq27's connected/unconnected splits if a stratum empties, bq24's all-scheduled
  cohort) displays as 0% instead of n/a. No current population is empty (fleet has 389/884
  rows both sides of every split). Disposition — **accept** with note: revisit if any
  caller's stratum can genuinely empty; a `None`-propagating variant would be the fix.
- **H-5 (low) — markdown-table injection surface in `expectations_section` /
  `narrative_section`.** `statement`/`expected`/`basis` are interpolated into `|`-delimited
  rows unescaped; a pipe in catalog text breaks the table. Catalog text is project-owned
  and currently clean. Disposition — **accept** (catalog-controlled input).

## Inline computations — per-BQ verdicts

### bq06 — clearance cycle time · CONFORMS-WITH-FINDINGS

Interval = `decision_date − date_received` in days, per-applicant + overall medians
(median not mean, per plan), per-decision-year history: all as the plan commits. Stated-gap
series (`our-cycle-time`) correctly `unavailable`. Findings:

- **B06-1 (medium) — "fastest frequent filer" universe is truncated to `top_n` before the
  ≥2 filter.** `frequent` (L1043) filters `top` — the top-`top_n` applicants *by clearance
  count* — not all applicants. The plan defines frequent filer as "applicant with ≥ 2
  clearances in the window" over the whole set. Verified against the pin: 15 applicants,
  exactly 6 with ≥2, `top_n = 6` — today the two sets coincide and the headline is right.
  But the moment a 7th applicant reaches 2 clearances, the true fastest frequent filer can
  fall outside `top` and the headline claim becomes silently wrong; and in sparse data the
  "frequent filer" table can seat 1-clearance applicants under a "frequent filer" heading.
  Disposition — **fix**: filter `len(ds) >= 2` first, then apply `top_n` for display.
- **B06-2 (low) — "since 2021" is a dataset-scope literal.** No year filter exists in the
  code; the claim is true because the acquisition scope starts 2021 (pin min decision
  2021-11-09) and the plan states the scope. Rots only if the dataset scope widens.
  Disposition — **accept**: plan-committed scope carried by the dataset; note for the
  dataset README's next reviewer.

### bq12 — clearance sweep · CONFORMS

Window anchored at newest `decision_date` in the pin (deterministic, end stated in the
headline per plan); roadmap flags are computed keyword matches from `commercial.yml` (never
a capability judgment — the report says so); empty-window headline + table branches both
handled; quarter bucketing correct; no demo banner on real public data (correct). The flag
logic string in the headline interpolates computed counts only. One shared nit: the
"90-day" window is `[as_of−90d, as_of]` inclusive = **91 days** (see B18-1). No own findings.

### bq18 — complaints vs thresholds · CONFORMS-WITH-FINDINGS

Trailing-window rates per 100 fleet devices with the denominator stated in the section
header (`n_fleet` from the fleet pin — the sanctioned denominator, per plan); thresholds
from config with the unvalidated-stand-in risk emitted; 130% trend rule implemented
(`max(1, prev)` guards the zero-prior edge sanely); top-3 monthly trend zero-filled.
E-18.1/E-18.2 evaluated. Findings:

- **B18-1 (low) — window asymmetry biases the rising test.** Current window =
  `counts(start, "9999")` covers `[as_of−90d, as_of]` = **91 days** inclusive; prior =
  `counts(prev_start, start)` = 90 days half-open. The 130% comparison therefore gives the
  current window one extra day (~1.1% upward bias on the rising verdict). Same +1-day
  inclusive pattern exists in bq12's "90-day" sweep (internally consistent there — no
  comparison across windows). Disposition — **fix**: half-open windows
  (`start <= d < end`) with `start = as_of − 89d` or label as 91-day.
- **B18-2 (low) — `window-trend` derivation string hardcodes "90-day".** The method string
  (L1323) narrates "trailing 90-day window" while the width is a param (`window_days`) — a
  config change rots the string. Disposition — **fix** (trivial): interpolate `{window}`.
- Round-before-compare on the breach test: covered by **H-1**.
- Edge noted, not flagged: an empty current window (no complaints in 90d) would IndexError
  on `top3[0]` — unreachable while the no-breach headline needs a top category and the
  dataset is non-empty; acceptable for a demo pipeline that fails loud.

### bq19 — MAUDE honesty showcase · CONFORMS-WITH-FINDINGS

Counts-never-rates enforced structurally (rate series `unavailable`, empty points, no rate
figure anywhere); entity normalization via the versioned alias map with prefix matching
(deterministic in YAML order); monthly history lag-trims exactly the trailing 2 months and
`total_events` sums the charted window only; no demo banner on real data (correct); no
numeric juxtaposition of internal vs MAUDE counts. Findings:

- **B19-1 (medium) — the honesty-showcase phrasing is a string literal, not a computed
  sentence.** The headline "RATE comparison is BLOCKED — the installed-base denominator
  (A-001) is not yet quantified" (L953–954) and the body's "whose model is not yet
  quantified" are narrated. The code *computes* `rate_ready = isinstance(a001.get("model"),
  dict)` (L938 — currently False; verified A-001 carries no `model:` block) but uses it
  only to flip `rate-by-mfr.evidence_class` to `"assumed"`. If A-001 is ever quantified,
  the edition self-contradicts: an "assumed" series with empty points whose provenance note
  and headline still say "blocked / not yet quantified". This is exactly the SKILL.md
  sentence-logic failure class (qualifiers must be computed, not narrated). Disposition —
  **fix**: branch the headline/body on `rate_ready`, and until the rate path is actually
  implemented, `rate_ready == True` should be a loud failure ("A-001 quantified but the
  rate computation is not implemented"), not a silent evidence-class flip.
- **B19-2 (low) — unmatched manufacturers get `.title()`, not "raw and visible".** The plan
  commits "unmatched names stay raw and visible"; `canon()` title-cases them (L931), which
  is a cosmetic transform and could in principle merge case-variant raws. Harmless today.
  Disposition — **accept**: note for the next plan/code sync; or return `name` unchanged.
- Edge noted: with ≤2 months of monthly data the lag trim is skipped entirely (`len > 2`
  guard) and lag-suppressed months would chart — unreachable against a 2023-onward dataset.

### bq23 — campaign coverage · CONFORMS-WITH-FINDINGS

Anchor = latest `completed_date` — **plan-committed for BQ-23** (deliberately different
from BQ-26's as-of anchor; the plan owns the optimism note and the report states the
anchor). Completed set, 28d/4 run-rate, stall→Issue (projection labeled
"no-recent-completions", never a fake date), risks/watch split, cumulative-coverage trend
toward the target, misses computed (`no-recent-completions` OR projected past close — the
`or` short-circuits before the string/date compare, correct). Headline qualifiers all
computed. E-23.1/E-23.2 evaluated. Finding:

- **B23-1 (low) — E-23.1's 95% target is judged by the 100%-completion projection.**
  `target_pct` (95) appears in prose and the trend chart but never enters the projection
  math; `misses` tests whether *all remaining* devices land by close. Direction is
  conservative (a region can hit 95% before close yet be flagged not-met), and the plan's
  own definition of projected finish is remaining ÷ rate — so this is a expectation-vs-
  metric mismatch, not a code error. Disposition — **accept** with note: if the 95%
  distinction ever matters, project the 95%-coverage date explicitly.

### bq24 — failure clusters / pause trigger · CONFORMS-WITH-FINDINGS

Per-ATTEMPTED-device primary rate with whole-cohort context (the adversarial-verification
remedy — verified present and labeled in the report); pause rule = rate > threshold AND
attempted ≥ min_cohort, both from config; retry trend charts dated events only with the
exclusion stated; `worst` qualifier computed via `max`. E-24.1 evaluated. Findings:

- Round-before-compare on the pause trigger: covered by **H-1** (this is its
  highest-stakes call site).
- **B24-1 (medium, shared with bq25/bq26) — complement-based status sets silently absorb
  vocabulary drift.** `attempted = status != "scheduled"` (bq24 L324/332, bq25 L452/459),
  and bq26's `remaining = status not in COMPLETED`, define populations by complement. The
  pinned vocabulary is exactly {completed, completed-after-retry, scheduled,
  failed-pending-retry, rolled-back} (verified, both snapshots) and the derivation strings
  enumerate the sets (F26-1 actioned ✓) — but a new upstream status (e.g. `cancelled`)
  would silently join "attempted" in bq24/25 (counting as an attempt that did NOT fail —
  diluting the pause trigger, the optimistic direction) and "remaining" in bq26. No guard
  asserts observed ⊆ known. Disposition — **fix** (one place): assert the status vocabulary
  after `load_pin_csv` of the campaign dataset (or a tiny shared
  `assert_vocab(rows, "status", KNOWN)` helper) so drift fails loud.
- Cosmetic, not flagged as a finding: `lines.insert(-3, ...)` (L407) drops the
  historical-view bullet directly under the "## Method & provenance" heading with no blank
  line (verified in the rendered 2026-07-27 report) — valid markdown, fragile tail
  arithmetic; same pattern at bq06 L1083 / bq27 L888. Fold into cleanup.

### bq25 — customer struggle & cost · CONFORMS

Tickets AND denominator both over attempted devices (the adversarial-verification remedy —
verified, and the report states the basis); rollback sites = distinct sorted site ids;
customer cost = completed-onsite × A-002 model read from the corpus record (verified
`hours_per_device: [1.5, 2.5]` × `labor_rate_usd_hr: [48, 65]` — nothing hardcoded),
presented as assumed with confidence interpolated from the record; weekly tickets trend
dated-events-only with the limitation stated. "Highest in {region}" is computed via `max`;
the near-tie fragility was disclosed in the 07-22 verification and the plan does not
require tie disclosure — accept. No catalog expectations declared, none rendered
(consistent). Nit folded into cleanup: `assume_path` (L442) is assigned and never used.

### bq26 — capacity outlook (the 2026-07-27 refit) · CONFORMS (refit verified in code)

The five refit commitments were each verified in the code, not assumed:

1. **Uniform 28d stall rule**: `stalled = len(recent) == 0 and remaining > 0` inside
   `region_stats`, applied identically to every region; stalled regions become
   high-severity Issues, never Risks. ✓
2. **Snapshot-as-of anchor + sensitivity**: primary anchor `snap.split(".")[0]` (the
   snapshot id's date part — the SKILL.md-documented as-of convention; `.2`-suffix ids
   handled), alternative = latest `completed_date`; both fed through the same
   `region_stats`; the sensitivity table renders both and `verdict_stable` drives a
   computed CHANGED/UNCHANGED sentence (not narrated). ✓ (Rounded-compare inside
   `verdict_stable` → H-1.)
3. **Thin-margin watch rule**: `cur >= req and cur < req * headroom` with the guard from
   `thin_margin_headroom_pct` config; thin regions named in the verdict and Watch, with the
   "carries the largest on-site load" qualifier **computed** via `max(...)` comparison. ✓
4. **FSE-days + connectivity join**: global mean completed-onsite `duration_min` (plan
   commits the global mean) ÷ `fse_day_minutes`; join by `device_serial` with
   `conn.get(...) == "yes"` — a join miss counts as NOT convertible (conservative;
   dossier confirmed zero misses); labor-time-only lower bound stated everywhere it
   appears; `fse-capacity` stays `unavailable`. ✓
5. **Status-set-explicit derivation strings** (F26-1): all four derived series
   (`capacity-stat`, `required-rate`, `remote-convertible`, `fse-days-remaining`) name the
   completed/remaining/on-site-remaining status sets inside `derivation.method`, and the
   report's anchor preamble + Method restate them for pins-only re-derivation. ✓ Actioned.

Residual finding:

- **B26-1 (low) — F26-2 from the economics dossier remains unactioned.** R1's
  remote-conversion mitigation still lacks the one-clause caveat that the remote path
  carried the implicated failure mode (all 3 NA rollbacks were remote installs) — moot
  while remote-convertible = 0, live the moment adapters convert the backlog. Disposition
  — **fix** (one clause in R1's mitigation string) at the next re-answer.
- Edge noted, accepted: `weeks_left == 0` (anchor ≥ close) degenerates `req` to
  `float(remaining)` — a stand-in with odd units, loud enough in context.

### bq27 — fleet currency · CONFORMS-WITH-FINDINGS

Behind-by mapping from config; PP3500 scope with PP3000 counted separately and never mixed
(verified: model filter, separate count); connectivity comparison descriptive only (no
causal language — plan-conformant); history correctly `unavailable` with the
one-snapshot-is-not-a-trend note. Findings:

- **B27-1 (medium) — "(all on 2.9.x line)" is a narrated string-literal fact.** L880
  asserts the PP3000 firmware posture as prose. Verified TRUE against both fleet pins
  (198 = 107×2.9.1 + 91×2.9.3) — but it is typed into source, invisible to the lint (the
  line carries a `[src:]` marker), and rots silently the first time a PP3000 reports
  anything else. The SKILL.md names this exact pattern a verified failure class.
  Disposition — **fix**: compute it (`all(fw.startswith("2.9") for ...)`) and emit either
  the qualified sentence or the actual version set.
- **B27-2 (medium) — unmapped firmware versions silently count as CURRENT.**
  `behind_map.get(fw, 0)` defaults an unknown version to 0-behind — the optimistic
  direction on a patient-safety-framed metric (the report itself says currency lag is a
  safety exposure). Today the map covers exactly the three observed PP3500 versions
  (verified), so nothing is misclassified — but a new firmware release or a data typo
  understates "behind" with no signal. Disposition — **fix**: treat unmapped as its own
  bucket (surface the count) or fail loud on `fw not in behind_map`.

---

## Findings table (consolidated)

| ID | Sev | Where | Finding | Disposition |
|---|---|---|---|---|
| H-1 | med | pct + callers (bq18/24/26) | Thresholds/classifications compared on rounded rates — knife-edge misclassification exported to the pause trigger, breach test, capacity verdicts | fix: compare unrounded, round at render |
| H-2 | med | module_dispatch | ModuleNotFoundError raised *inside* an existing bq module is swallowed as "no computation" | fix: re-raise unless `e.name` == dispatched module (or find_spec probe) |
| H-3 | low | evaluate_expectations | Computed results with ids not in the catalog are silently dropped (typo'd E-id vanishes) | fix: loud check on unknown result ids |
| H-4 | low | pct | Zero denominator renders 0.0 ("0%") instead of n/a | accept: no current empty stratum; revisit if one can empty |
| H-5 | low | expectations/narrative sections | Unescaped `\|` in catalog text breaks markdown tables | accept: catalog-controlled input |
| B06-1 | med | bq06 | "Fastest frequent filer" universe truncated to top_n before the ≥2 filter — latent wrong-headline; coincidentally exact today (6 of 15 applicants ≥2, top_n=6) | fix: filter ≥2 first, then top_n for display |
| B06-2 | low | bq06 | "since 2021" scope is a literal riding on dataset acquisition scope (true: pin min 2021-11-09) | accept: plan-stated scope; note |
| B18-1 | low | bq18 (also bq12 label) | Current window 91 days inclusive vs prior 90 half-open — slight upward bias on the 130% rising test | fix: half-open windows |
| B18-2 | low | bq18 | window-trend derivation string hardcodes "90-day" instead of the window param | fix: interpolate |
| B19-1 | med | bq19 | BLOCKED/"not yet quantified" headline+body are literals; computed `rate_ready` only flips evidence_class → self-contradicting state if A-001 quantifies | fix: branch on rate_ready; fail loud when True |
| B19-2 | low | bq19 | Unmatched manufacturers `.title()`-cased, plan says "stay raw" | accept: cosmetic; note for plan/code sync |
| B23-1 | low | bq23 | E-23.1 (95% by close) judged via 100%-completion projection; target_pct unused in math — conservative direction | accept: plan defines projection as remaining÷rate; note |
| B24-1 | med | bq24/25/26 | Complement-based status sets (`!= "scheduled"`, `not in COMPLETED`) absorb vocabulary drift; new status dilutes the pause trigger optimistically | fix: assert observed status ⊆ known vocabulary |
| B26-1 | low | bq26 | F26-2 residual: R1 mitigation lacks the remote-path-rollback caveat from the prior dossier | fix: one clause at next re-answer |
| B27-1 | med | bq27 | "(all on 2.9.x line)" narrated string-literal fact (true today against both pins) | fix: compute the qualifier |
| B27-2 | med | bq27 | `behind_map.get(fw, 0)` — unmapped firmware silently counts as current (optimistic on a safety-framed metric) | fix: surface/fail on unmapped versions |
| — | low | bq24/06/27, bq25 | Cleanup: fragile `lines.insert(-N)` tail arithmetic (bullet renders under Method heading); unused `assume_path` in bq25 | accept: cosmetic; fold into next touch |

## Overall verdict

**approved-with-findings.** No finding invalidates a published number in the current
editions — every medium finding is either a knife-edge/latent hazard (H-1, H-2, B06-1,
B24-1, B27-2) or a narrated-fact rot risk that is true against today's pins (B19-1, B27-1).
The shared helpers the whole catalog leans on (`_median`, the expectations join + `[config]`
dedupe, week/window logic, determinism posture, loud pin errors) are correct. The BQ-26
refit implements all five commitments from the red-team/verification chain; F26-1 is
actioned, F26-2 remains open (low). The two fixes worth doing before the next approval
cycle: unrounded threshold comparisons (H-1 — the bq24 pause trigger is the stakes) and the
`module_dispatch` exception discrimination (H-2 — it can mislabel a broken module as
unimplemented).

```json
{"reviews": [{"path": "computations.py", "verdict": "approved-with-findings", "summary": "Shared helpers sound (median/dedupe/windows/determinism verified; loud pin errors); BQ-26 refit commitments all implemented; findings are latent hazards and literal-fact rot risks, none invalidates a current published number.", "findings": [
  {"severity": "medium", "summary": "helper/pct: thresholds compared on rounded rates (bq24 pause, bq18 breach, bq26 verdicts) — knife-edge risk", "disposition": "fix: compare unrounded, round only at render"},
  {"severity": "medium", "summary": "helper/module_dispatch: ModuleNotFoundError inside an existing bq module swallowed as 'no computation'", "disposition": "fix: re-raise unless e.name is the dispatched module"},
  {"severity": "low", "summary": "helper/evaluate_expectations: computed results with unknown E-ids silently dropped", "disposition": "fix: loud check on unknown result ids"},
  {"severity": "low", "summary": "helper/pct: zero denominator renders 0.0 not n/a", "disposition": "accept: no caller stratum currently empties; revisit if one can"},
  {"severity": "low", "summary": "helper/expectations_section: unescaped pipes in catalog text break markdown tables", "disposition": "accept: catalog-controlled input"},
  {"severity": "medium", "summary": "bq06: 'fastest frequent filer' computed from top_n-truncated set; exact today by coincidence (6 of 15 >=2)", "disposition": "fix: filter >=2 clearances before top_n"},
  {"severity": "low", "summary": "bq06: 'since 2021' scope literal rides on dataset acquisition scope (true vs pin)", "disposition": "accept: plan-stated dataset scope"},
  {"severity": "low", "summary": "bq18: current window 91d inclusive vs prior 90d — slight upward bias on 130% rising test; bq12 label same +1d", "disposition": "fix: half-open windows"},
  {"severity": "low", "summary": "bq18: window-trend derivation string hardcodes '90-day' instead of window param", "disposition": "fix: interpolate the param"},
  {"severity": "medium", "summary": "bq19: BLOCKED/'not yet quantified' headline is a literal; rate_ready computed but unused - rots if A-001 quantifies", "disposition": "fix: branch headline on rate_ready; fail loud when True"},
  {"severity": "low", "summary": "bq19: unmatched manufacturer names .title()-cased; plan says 'stay raw'", "disposition": "accept: cosmetic, note for plan/code sync"},
  {"severity": "low", "summary": "bq23: E-23.1 95% target judged by 100%-completion projection; target_pct unused in math (conservative)", "disposition": "accept: plan defines projection as remaining/rate"},
  {"severity": "medium", "summary": "bq24/25/26: complement status sets (!= scheduled / not in COMPLETED) absorb vocabulary drift, diluting the pause trigger", "disposition": "fix: assert observed statuses subset of known vocabulary"},
  {"severity": "low", "summary": "bq26: F26-2 residual — R1 mitigation lacks remote-path-rollback caveat (moot while convertible=0)", "disposition": "fix: one clause at next re-answer"},
  {"severity": "medium", "summary": "bq27: '(all on 2.9.x line)' narrated string-literal fact — true vs both pins, rots on refresh", "disposition": "fix: compute the qualifier from the data"},
  {"severity": "medium", "summary": "bq27: behind_map.get(fw,0) counts unmapped firmware as current — optimistic default on safety-framed metric", "disposition": "fix: surface or fail on unmapped versions"},
  {"severity": "low", "summary": "bq24/06/27/25: fragile lines.insert(-N) tail arithmetic + unused assume_path var — cosmetic", "disposition": "accept: fold into next touch"}
]}]}
```
