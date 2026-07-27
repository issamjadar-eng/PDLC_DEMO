# Code-Review Dossier — Market BQ Modules (bq_07..bq_11), 2026-07-27

_Task ben/108 · AI code review (read-only) of `docs/project/commercial/bq_modules/bq_{07,08,09,10,11}.py` against `plans/BQ-{07..11}.md`, the commercial skill's computation contract and code-quality rules, `computations.py` shared helpers, and `entity-aliases.yml`. Builds on the already-actioned output-verification dossier `108-verify-redteam-market-2026-07-27.md`: settled items are not re-flagged; the fixes it prompted are verified below. Style nits are not findings._

**Verdict summary**

| Module | Verdict | Findings (high/med/low) |
|---|---|---|
| `bq_modules/bq_07.py` | APPROVED-WITH-FINDINGS | 0 / 1 / 1 |
| `bq_modules/bq_08.py` | APPROVED-WITH-FINDINGS | 0 / 1 / 3 |
| `bq_modules/bq_09.py` | APPROVED-WITH-FINDINGS | 0 / 2 / 4 |
| `bq_modules/bq_10.py` | APPROVED-WITH-FINDINGS | 0 / 1 / 2 |
| `bq_modules/bq_11.py` | APPROVED-WITH-FINDINGS | 0 / 1 / 3 |

No module is CHANGES-REQUIRED: every medium finding is a **latent** hazard (guards that would not trip, phrasing branches that would mislabel a future snapshot, a rounded compare with no borderline data today) — none corrupts the current editions, whose numbers the verification pass already reproduced exactly.

---

## Verification of prior-dossier fixes (all checked against current code)

| Prior finding | Status in code |
|---|---|
| BQ-09 hardcoded "decays" verdict | **Implemented** — `bq_09.py:101-118` derives the shape phrase from computed bucket stats with three branches + a computed tail clause (branch-phrasing gaps flagged below as new findings) |
| BQ-11 median-by-index (`sorted[n//2]`) | **Implemented correctly** — `statistics.median` over **unrounded** ratios, rounded once for display (`bq_11.py:128`, `:178`) |
| BQ-08 dollar-weighted win rate absent | **Implemented** — computed (`:42-47`), in headline, report bullet, Watch item, and a dedicated `value-win-rate` series with derivation block |
| BQ-08 ND-as-losses denominator sensitivity | **Implemented** — `rate_nd` (`:41`) in the E-08.1 actual, the report bullet, and the near-target Watch branch |
| BQ-07 growth-rate basis mismatch undisclosed | **Implemented** — mismatched-bases clause in the headline, the growth bullet, and the `growth-rate` series provenance note |
| BQ-07 A-003 guard asserts (pattern copied from bq_10) | **Implemented** — `bq_09.py`-style asserts at `bq_07.py:31-36` (coverage gap flagged below) |
| BQ-09 90-day window sensitivity in report | **Implemented** — `sensitivity_window_days` from config, reported under the split table + `window-sensitivity` series |
| BQ-10 missing demo banner | **Implemented** — `C.BANNER` at `bq_10.py:87` plus the stand-ins caveat line |
| BQ-09 demo-of-method note **in the split-table caption itself** | **NOT implemented** — the verdict lead ("Method demo (fabricated CRM…)") and honesty box predate that finding; the split-table section (`bq_09.py:163-169`) still carries no caption note. Re-flagged as BQ-09 L4. |

---

## bq_modules/bq_07.py — VERDICT: APPROVED-WITH-FINDINGS

**Plan conformance (plans/BQ-07.md):** Conforms. NA-as-US proxy with labeling; in-segment = PP3500+PP3000+IP5000 matching A-003 scope; unit share and revenue share as ranges against the A-003 denominators; FY2026H1 ×2 annualization applied to the dollar comparison only and labeled; denominator held constant across FYs and stated; growth comparison labeled directional-only with the unit-vs-dollar / segment-vs-total mismatch stated at every claim site; competitor unit split published as `unavailable`, never estimated. No point share is asserted anywhere. Guard asserts check A-003 `status: active`, both range strings, and the 7.3% CAGR string — verified effective against the actual record (any edit to those substrings trips the assert; the fail direction is safe).

**Guard-effectiveness check (lens 6):** the asserts at `:31-36` cover `1.1M-1.8M`, `$1.5B-$3.0B`, and `7.3% CAGR` — all three verified present verbatim in `A-003.yml value_or_range` / `estimation_method`, so a changed record trips them. But the module interpolates a **fourth** A-003 fact the guard does not cover (finding M1).

| Sev | Location | Issue | Disposition |
|---|---|---|---|
| medium | `bq_07.py:120` | The growth bullet types "assumed annual demand of 130k–230k units" as a string literal (from A-003's "~130k-230k units/yr") with **no guard assert** — the module's own comment promises the asserts break loudly on any A-003 range edit, but this range can drift silently. Line carries `[assume: A-003]`, so lint will never see it. | fix: extend the `:33` assert to also require `"130k-230k" in vr` |
| low | `bq_07.py:54` | `units["FY2024"] == 0` (or missing FY rows) raises ZeroDivisionError in the growth exponent; empty-snapshot robustness generally unhandled. | accept: demo datasets guarantee non-empty FY rows; a crash (not a wrong number) is the failure mode |

Numeric traps: rounding happens after computation, display-only. Determinism: clean (fixed tuples, dict-comprehension over a fixed FY list, no unordered iteration). Marker discipline: every generated figure-bearing line carries a same-line marker (multi-source-line f-strings all collapse to single physical report lines — verified per element).

---

## bq_modules/bq_08.py — VERDICT: APPROVED-WITH-FINDINGS

**Plan conformance (plans/BQ-08.md):** Conforms. Trailing-365d window anchored at the pinned snapshot's max `close_date` (no wall clock); decided = won+lost with no-decision excluded and reported; count and dollar-weighted win rates side by side with the lose-bigger/win-bigger sentence computed from the comparison; the committed denominator sensitivity (ND-as-losses) stated next to the verdict in both the E-08.1 actual and the report; loss-reason breakdown on `primary_reason`; PM-gap = primary OR cited with the primary-only count also reported; PM-gap value as recorded CRM value, disclaimed; monthly zero-filled history across the full snapshot span.

| Sev | Location | Issue | Disposition |
|---|---|---|---|
| medium | `bq_08.py:64` | `target = 50.0` is hardcoded in the module while E-08.1's floor lives in the catalog expectation text (`expected: ">= 50% of won+lost"`). If the catalog floor is re-set (e.g. to 55%), the module silently keeps judging against 50 while the expectations table prints the new catalog text — a met/not-met verdict computed against a different number than the row states. The comment's `[config: commercial.yml]` citation claims a wiring that doesn't exist. | fix: read the floor from a `params` entry (add `target_win_rate_pct`) or parse/assert the catalog `expected` string, so a catalog change trips loudly |
| low | `bq_08.py:77` | The "at-risk" band (`rate >= target - 2`) is a module-invented threshold committed nowhere in the plan or catalog. | accept: `at-risk` is sanctioned verdict vocabulary in `computations.evaluate_expectations`, the band is conservative, and the near-miss Watch branch discloses the fragility — but note it if E-08.1 is ever formalized |
| low | `bq_08.py:45-47` | `val_note` phrasing compares rates already rounded to 0.1pp (`C.pct`), so a sub-0.05pp true difference can print "mirrors the count mix". | accept: 0.1pp granularity is immaterial at this sample size; phrasing branches are otherwise computed and exhaustive |
| low | `bq_08.py:34` | Empty snapshot / empty window ⇒ `max()` ValueError; `rate` on zero decided is handled by `C.pct` (returns 0.0) but the crash paths are unguarded. | accept: crash-not-wrong-number on impossible demo input |

Hardcoded category sets: none — reasons are read from data and ranked with a deterministic `(-count, name)` sort. PM-gap matching uses the two committed field predicates only. Determinism and marker discipline: clean. Narrative Watch IDs are sequence-computed and deterministic.

---

## bq_modules/bq_09.py — VERDICT: APPROVED-WITH-FINDINGS

**Plan conformance (plans/BQ-09.md):** Conforms. Population = decided opps with competitor incumbents (PainEase/none excluded), no-decision counted and reported; canonicalization is case-insensitive prefix, first-hit-wins, in alias-file order — exactly the `entity-aliases.yml` header contract; in-window = most recent prior recall (`event_date_posted`, undated rows excluded and counted) within 180 config days of close; the committed 90-day sensitivity recomputed and reported directly under the split table; decay buckets 0–3/3–6/6–12/>12-or-no-prior with n carried and small-n annotated; verdict phrasing derived from the computed bucket shape; density caveat carried as R2 with computed n's; 4-line zero-filled quarterly history.

**Bucket-shape verdict logic — special scrutiny (`:101-118`):** Branch coverage is complete — A (strict decay, every interior step >1.0pt), B (highest-first + interior spread ≤2.0pt), else C, plus an independent two-way tail clause; every possible bucket shape lands somewhere, and all rates printed are computed. Current snapshot (56.2 / 50.0 / 50.0 / 14.3) correctly takes branch B + "far lower" tail. But two branches can emit **phrasing that contradicts the numbers it prints** (M2, L1), and empty buckets feed the logic as 0.0% (L2).

**Alias-map coverage (lens 5):** a recall firm matching NO alias is **not dropped** — it stays in `recall_dates` under its raw name (currently only small non-incumbent players: Zyno, Avanos, …). The real hazard is on the CRM side: an `incumbent_vendor` value matching no alias keeps its raw name, joins **zero** recalls (its postings live under a different raw variant), silently gets `_days = None`, and lands in ">12 months / no prior recall" + out-of-window — understating in-window n and polluting the control group. All six current incumbents canonicalize (verified in the prior dossier), but nothing guards the next snapshot's new vendor string (M1).

| Sev | Location | Issue | Disposition |
|---|---|---|---|
| medium | `bq_09.py:50-55, 70-76` | No coverage guard on the alias join: a future `incumbent_vendor` matching no alias silently joins zero recalls and inflates the no-prior/out-of-window buckets. The only signal is a raw-looking name in the incumbent table — weak and easy to miss. | fix: after building `decided`, warn/assert on any incumbent whose `canon()` returns the raw value unchanged (or emit an "unmatched incumbents" line in the report) |
| medium | `bq_09.py:112-114` | Branch C prints "the bucket profile is not a monotone decay" for a **weakly-monotone declining** profile — e.g. 56.0 → 55.6 → 45.0 (a step ≤1.0pt plus interior spread >2.0pt skips branches A and B). The sentence is literally false against the rates it prints beside it. | fix: add a weakly-monotone branch, or reword C to "no uniform decay across the buckets" |
| low | `bq_09.py:115-116` | Tail clause claims "far lower" whenever `tail < min(ir)` — fires even for a 0.1pt gap. | fix: require a margin (e.g. `min(ir) - tail >= 10`) before "far lower", else use the neutral `:118` phrasing |
| low | `bq_09.py:96-103, 186` | An empty bucket yields `wr = 0.0` (via `C.pct(0,0)`) and feeds the shape logic as a real rate — a fake cliff; the small-n table annotation `0 < len(sub) < 10` deliberately skips n=0 rows. | fix: exclude n=0 buckets from the shape derivation and annotate them "(empty)" in the table |
| low | `bq_09.py:192` | Table header "FRN recalls posted since 2021" types the dataset span as a string literal — a dataset re-cut (say 2019→) silently falsifies it. | fix: derive the start year from `min(recall_dates)` values (or accept: span is committed in the plan's Data section) |
| low | `bq_09.py:163-169` | Prior dossier's committed fix — "(demo of method, not market evidence)" in the split-table caption itself — was not implemented; the most screenshot-able table still relies on caveats outside it. | fix: add the note to the section caption, or record an explicit accept against the prior finding |

Determinism: alias iteration is file-ordered, incumbent table sorted, quarter axes derived — clean. `30.44` days/month and rounded-rate comparisons (±0.05pp vs 1.0/2.0pt thresholds) are immaterial. Marker discipline: clean, including both `[src:]` pins + `[config: entity-aliases.yml]` on join-derived rows and the full four-input `derivation.inputs` on every derived series (the prior friction-log note about population exclusions missing from `derivation.method` remains open at the engine level, not re-flagged here).

---

## bq_modules/bq_10.py — VERDICT: APPROVED-WITH-FINDINGS

**Plan conformance (plans/BQ-10.md):** Conforms. Our full-basis TCO = capital + 5×(cloud+consumables+service) from the four config params, all cited `[config: commercial.yml]`; comparable basis = capital + 5-yr service vs A-004's capital+service-only range, with the strictly-higher-true-TCO direction stated; one class-wide range shared by all three competitors, stated; per-competitor differentiation via the curated feature matrix with `verify` status carried and absent cells rendered "—", never guessed; history published as `unavailable`; verdict capped at "indicative, assumption-bounded" with an explicit no-hard-we-win clause; demo banner present; `a004['confidence']` read from the record, not typed.

**Guard-effectiveness check (lens 6):** asserts at `:36-39` cover `status: active`, `$3.0k-$15k`, `$2.2k-$6.9k`, `$150-$250` — all verified verbatim in `A-004.yml value_or_range`, so edits to those trip loudly. But of the six transcribed constants, two (`CAP_NET_LO/HI` = the "$4.4k-$13.7k" networked-capital range, `:25`) are **outside** the guard (M1).

| Sev | Location | Issue | Disposition |
|---|---|---|---|
| medium | `bq_10.py:25, 38-39` | The networked/EMR-integrated capital range ($4.4k–$13.7k) is transcribed from A-004 but not covered by the range assert — the header comment promises the asserts break loudly on any record edit, yet this pair can silently go stale in the report's capital bullet. | fix: add `"$4.4k-$13.7k" in vr` to the `:38` assert |
| low | `bq_10.py:23, 33, 113` | `COMP_TCO_LO/HI` is A-004's **5-year** figure, but `horizon` is a free config param — setting `horizon_years: 7` would relabel the same $3k–$15k as "7-yr TCO" and compare our 7-yr figure against a 5-yr range. | fix: `assert horizon == 5` next to the A-004 asserts (the transcription is horizon-specific) |
| low | `bq_10.py:130-135` | `cell()` special-cases only `verified == "verify"` — any unexpected status value (typo, new vocabulary) silently renders as settled fact. | fix: assert `verified in ("yes", "verify")` per row; cheap and consistent with the module's loud-guard posture |

String-literal facts: the EXCLUDED-items bullets restate A-004's own exclusions (consumables undisclosed, software unquantified) — these are the record's content, marker-carried, and their direction-of-bias sentence ("strictly above the quoted range") is arithmetically entailed by exclusion of positive costs, so it is not snapshot-fragile. Determinism (fixed product/attr lists), robustness (missing cells → "—"), and marker discipline: clean.

---

## bq_modules/bq_11.py — VERDICT: APPROVED-WITH-FINDINGS

**Plan conformance (plans/BQ-11.md):** Conforms. Connected-devices-only scope stated; window = 3 newest pinned telemetry months; site utilization hours-weighted (Σhours ÷ Σexpected), not a mean of ratios; flagged < 60% with the ≥10-device materiality tier and the below-bar watch tier kept visible; E-11.1 evaluated as a site-level proxy with the join gap stated in the actual; account revenue-at-risk published `unavailable` naming the missing site→account key; regional revenue given as context-not-attribution; monthly history = worst-3 flagged + fleet median (≤4 lines, pick rule stated). Median fix verified: `statistics.median` on raw ratios, single terminal rounding — both window-level and per-month.

| Sev | Location | Issue | Disposition |
|---|---|---|---|
| medium | `bq_11.py:46-48` | Flagging compares the **rounded** utilization (`util`, 1dp) against the threshold: a site at 59.95–59.99% raw rounds to 60.0 and silently escapes flagging (rounding-before-compare). Latent only — the seeded data is bimodal with no borderline site — but it is the exact trap the shared-helper rule exists to prevent, and the same rounded dict also keys the sort. | fix: flag and sort on `util_raw`, round only at display |
| low | `bq_11.py:131-133` | "the flagged sites sit far below the fleet norm" is an unconditional string literal — a data-shape claim that survives a snapshot with a 59%-vs-61% profile (the BQ-09-verdict failure class, in miniature). Currently true (~37% vs 89.6%). | fix: gate the clause on a computed gap (e.g. median − worst ≥ 20pp) or interpolate the computed gap instead of the adjective |
| low | `bq_11.py:173-175` | The monthly timeseries zero-fills a missing (site, month) as `y: 0` — for a **ratio** series, 0 reads as catastrophic utilization, not missing data (the zero-fill rule is for counts). No effect today: the pinned snapshot is complete (331 devices × 6 months). | accept: harmless on complete data; revisit if telemetry ever gains gaps (null/skip instead of 0) |
| low | `bq_11.py:57-62` | Headline edge: flagged non-empty but material empty renders "0 clear the …bar ()" — empty parens; and the all-clear branch loses the `[config]`-relevant threshold context markers only by luck of the shared line. | accept: cosmetic; both branches are otherwise computed and the flagged branch is exercised |

Determinism: `months_all` sorted, flagged sorted by utilization with stable CSV-order ties, region dicts rendered via `sorted()` — clean. Robustness: `expected == 0` would raise (accept — norm columns are positive by construction); empty-flagged path exercised and safe. Marker discipline: clean, including the multi-figure regional-context line (single physical line, marker at end).

---

## Cross-module observations (not per-module findings)

1. **The guard-assert pattern is good but coverage is the weak point** — both BQ-07 and BQ-10 transcribe more assumption facts than their asserts protect (M1 in each). A worthwhile convention: every module-level transcribed constant gets a matching substring assert, written in the same commit.
2. **Computed-phrasing branches are the second-generation risk.** The hardcoded-prose lesson was fixed by deriving phrases from data (BQ-08 `val_note`, BQ-09 shape) — the residue is branches whose *wording* can contradict the numbers on edge shapes (BQ-09 M2/L1) and one surviving unconditional adjective (BQ-11 L1).
3. **Determinism and marker discipline are clean across all five modules** — no unordered set/dict iteration reaches any report line or series, and every generated figure-bearing line carries a same-line marker.
4. Style note (not a finding): `month_range` (bq_08) and `quarter_range` (bq_09) are date-axis helpers of the kind SKILL.md routes into `computations.py`; harmless as module-locals until a third module needs one.

```json
{"reviews": [
  {"path": "bq_modules/bq_07.py", "verdict": "APPROVED-WITH-FINDINGS",
   "summary": "Plan-conformant; honesty posture and A-003 guards verified. One guard gap: the 130k-230k annual-demand transcription is unprotected by the asserts.",
   "findings": [
     {"severity": "medium", "summary": "A-003 '130k-230k units/yr' typed as literal in growth bullet; not covered by the guard asserts — can drift silently", "disposition": "fix: extend the assert to require '130k-230k' in value_or_range"},
     {"severity": "low", "summary": "Zero FY2024 units would raise ZeroDivisionError in growth exponent; empty-snapshot paths unguarded", "disposition": "accept: demo data non-empty; failure mode is a crash, not a wrong number"}
   ]},
  {"path": "bq_modules/bq_08.py", "verdict": "APPROVED-WITH-FINDINGS",
   "summary": "Plan-conformant; value-win-rate and ND-sensitivity fixes verified implemented. E-08.1 floor is hardcoded 50.0 instead of wired to the catalog.",
   "findings": [
     {"severity": "medium", "summary": "target=50.0 hardcoded; catalog E-08.1 change would silently diverge computed verdict from printed expectation", "disposition": "fix: read floor from params or assert the catalog expected string"},
     {"severity": "low", "summary": "'at-risk' band (target-2) is a module-invented threshold committed nowhere", "disposition": "accept: sanctioned verdict vocabulary, conservative, fragility disclosed in Watch"},
     {"severity": "low", "summary": "val_note phrasing compares 0.1pp-rounded rates; sub-0.05pp difference prints 'mirrors'", "disposition": "accept: immaterial at this granularity"},
     {"severity": "low", "summary": "Empty snapshot/window crashes max(); unguarded", "disposition": "accept: crash-not-wrong-number on impossible demo input"}
   ]},
  {"path": "bq_modules/bq_09.py", "verdict": "APPROVED-WITH-FINDINGS",
   "summary": "Plan-conformant; computed decay phrasing and 90d sensitivity fixes verified. Gaps: no alias-coverage guard for new incumbents; two shape-phrase branches can contradict their own printed rates; split-table demo caption from prior dossier not implemented.",
   "findings": [
     {"severity": "medium", "summary": "Unaliased incumbent_vendor silently joins zero recalls and lands in no-prior/out-of-window — no coverage guard", "disposition": "fix: warn/assert when canon() returns an incumbent unchanged, or report unmatched incumbents"},
     {"severity": "medium", "summary": "Shape branch C prints 'not a monotone decay' for weakly-monotone declining profiles — a false claim vs its own rates", "disposition": "fix: add weakly-monotone branch or reword to 'no uniform decay'"},
     {"severity": "low", "summary": "Tail clause claims 'far lower' for any tail below min interior rate, even by 0.1pt", "disposition": "fix: require a margin before 'far lower'"},
     {"severity": "low", "summary": "Empty bucket feeds shape logic as 0.0% and escapes the small-n annotation (0<n<10)", "disposition": "fix: exclude n=0 buckets from shape derivation; annotate '(empty)'"},
     {"severity": "low", "summary": "'FRN recalls posted since 2021' table header is a typed dataset-span literal", "disposition": "fix: derive start year from the joined recall dates"},
     {"severity": "low", "summary": "Prior-dossier fix (demo-of-method note in split-table caption) not implemented; caveats stay outside the table", "disposition": "fix: add the caption note or record an explicit accept"}
   ]},
  {"path": "bq_modules/bq_10.py", "verdict": "APPROVED-WITH-FINDINGS",
   "summary": "Plan-conformant; demo banner fix verified; verdict correctly capped. Guard gap: networked-capital range ($4.4k-$13.7k) transcribed outside the A-004 asserts; horizon not pinned to the 5-yr range.",
   "findings": [
     {"severity": "medium", "summary": "CAP_NET_LO/HI ($4.4k-$13.7k) transcribed from A-004 but not covered by the guard assert — can drift silently", "disposition": "fix: add '$4.4k-$13.7k' to the assert"},
     {"severity": "low", "summary": "COMP_TCO range is A-004's 5-yr figure but horizon_years is free — horizon!=5 would mislabel the comparison", "disposition": "fix: assert horizon == 5 beside the A-004 asserts"},
     {"severity": "low", "summary": "cell() treats any verified value other than 'verify' as settled fact — unexpected status renders unmarked", "disposition": "fix: assert verified in ('yes','verify') per row"}
   ]},
  {"path": "bq_modules/bq_11.py", "verdict": "APPROVED-WITH-FINDINGS",
   "summary": "Plan-conformant; statistics.median-on-raw-ratios fix verified implemented. One numeric trap: flagging compares rounded utilization against the threshold.",
   "findings": [
     {"severity": "medium", "summary": "Underuse flag compares 1dp-rounded utilization vs threshold — a 59.95-59.99% site escapes flagging (latent)", "disposition": "fix: flag and sort on util_raw, round only for display"},
     {"severity": "low", "summary": "'flagged sites sit far below the fleet norm' is an unconditional literal data-shape claim", "disposition": "fix: gate on a computed gap or interpolate the gap"},
     {"severity": "low", "summary": "Monthly ratio timeseries zero-fills missing site-months as 0%, conflating missing with catastrophic", "disposition": "accept: pinned snapshot is complete; revisit if telemetry gains gaps"},
     {"severity": "low", "summary": "Headline renders '()' when flagged is non-empty but material is empty", "disposition": "accept: cosmetic edge; branches otherwise computed"}
   ]}
]}
```
