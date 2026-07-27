# Code review — Roadmap computation modules bq_13–bq_17, editions 2026-07-27

_Task ben/108 · reviewer: AI assistant (independent code-review pass) · date 2026-07-27_
_Scope: `docs/project/commercial/bq_modules/bq_{13,14,15,16,17}.py` (read-only). Context read: commercial SKILL.md "Code quality" + computation contract; plans/BQ-13..17.md; computations.py shared helpers; the prior output-verification dossier (`108-verify-redteam-roadmap-2026-07-27.md`, already actioned — its settled findings are not re-flagged; the code implementing the fixes IS verified below). Lens: plan conformance, string-literal claim branches, numeric traps, config vs hardcoding, composite arithmetic, determinism, robustness, marker discipline. No style nits._

## Method

- Read all five modules end-to-end against their plans and the `commercial.yml` params (attribute_lane_map, attribute_lane_relation, numeric_directions, feature_rank_year, lane_watch_keywords, differentiators, wave_check_years).
- **Empirical determinism test**: each module run twice against the pinned edition inputs under `PYTHONHASHSEED=1` and `=42` into scratch dirs; `report.md` + `data.json` byte-compared — **all five identical across seeds**, and all five **byte-identical to the committed 2026-07-27 editions**.
- Register data inspected to validate latent-input assumptions (sentiment vocabulary is exactly {support, neutral, concern}; max 1 row per (kol_id, feature_id); the sole F9 voice is KOL-0004 Kuitunen).
- Latent tie hazard demonstrated by simulation (an F4/F5 composite tie yields order-dependent picks under shuffled set order — see F17-1).

## Verification of the previously-actioned fixes (as tasked)

| Fix | Verdict | Evidence |
|---|---|---|
| **BQ-17 deterministic rival tiebreak** (weight-sensitivity scan) | **Correctly deterministic.** | `bq_17.py` L128: `max((score[g], g) for g in eligible if g != pull)` — tuple comparison breaks score ties on the feature-id string, independent of set/dict iteration order. Weights sum to 1 (`(1/3−d, 1/3+d, 1/3)`); 0.25-pp granularity honestly reported as "~{flip_pp} pp"; scan uses the same rounded components as the composite (consistent). **But** the *pull/kill tie-break sorts themselves* retain a latent order dependence — see F17-1. |
| **BQ-17 conditional Kuitunen caution** | **Partially correct.** | L138: `kill_direction_note = (kill == "F9" and len(sent["F9"]["voices"]) == 1)` — self-retires when the kill pick changes or F9 gains a second voice ✓. It does **not** pin the voice's identity: the emitted text hardcodes Kuitunen and the "too late and too thin" quote, so a register change replacing the single F9 voice with a *different* KOL would misattribute — see F17-2. |
| **BQ-14 adjacency-vs-closure routing** (RT-14.1) | **Correctly implemented.** | Reads `attribute_lane_relation` with conservative `adjacent` fallback for unmapped attributes (L94); adjacency labeled in the matrix routing column, in the headline (branch computed — emitted only when `adjacent` non-empty), a dedicated bullet, and R1. Config labels `pca_pause_or_etco2` and `integrated_etco2` `adjacent`, `predictive_monitoring→F6` `closes` — matches the finding's intent. |
| **BQ-13 anchor-fragility disclosure** (RT-13.1) | **Implemented for the current data shape; not branch-safe** — see F13-1/F13-2. | Both anchor readings computed (`hw_edge_days`, `hw_beats_late`, `hw_late_margin`); margin stated in headline, runway bullet, R3, and the `hardware-edge-margin` series; H2 config-only provenance caveated in headline, section intro, R3, and method ✓. |
| **BQ-15 dual-basis margins** (RT-15.1) | **Correctly implemented in the computation; one unconditional headline literal** — see F15-1. | `acc_margin_vol` + `acc_ahead_vol` computed; refresh trigger fires on **either** basis (`acc_ahead is False or … acc_ahead_vol is False`, L78); both margins in report body + `differentiator-margins` series with basis stated in the derivation method ✓. |
| **BQ-16 evidence-absence framing** (RT-16.1) | **Correctly implemented.** | Headline: "read as NO documented endorsement of those slots, not as opposition"; flag renamed "no documented slot endorsement"; wave-check section + R1 restate the vocabulary-flattening limitation with source-doc spot checks ✓ (the spot-check sentence is itself an unconditional curated literal — F16-3). |

---

## bq_13.py — verdict: approve-with-findings

Plan conformance: **conforms** on current data — premise check, data anchor, both launch-anchor readings, A-005 bands, acquisition scenario (assumption-class, `evidence_class: assumed`), watch keywords via config + entity aliases, quarterly zero-filled series. Markers resolve (`v-main`, `runway-margin`, `hardware-edge-margin`, `entry-scenarios`, `predictive-shipping-check`, `watch-flagged`, `clearances-by-quarter`). Deterministic (alias list and YAML dict orders are stable; recent-clearance sort key can tie on date but falls back to stable CSV order).

| ID | Sev | Finding | Disposition |
|---|---|---|---|
| F13-1 | high | Headline (L128) and slow-end bullet (L169-170) hardcode "about {abs(margin)} months **before** our … launch anchor". `abs()` discards the sign of `months_between(samd_hi, launch)`. The data anchor advances with every 510(k) refresh: once the newest decision date passes ~2026-07-01, `samd_hi` lands **after** the launch anchor and the verdict sentence inverts its own fact ("N months before" when it is N months after) while the scenario table says "straddles" — an internal contradiction in the most-quoted string. | fix: branch the phrase on the sign (before/after) and drop `abs()`; the "even the SLOW end lands before us" bullet needs its own branch. |
| F13-2 | medium | `hw_edge_days = (hw_lo - launch).days` sign unhandled: if the hardware fast edge ever precedes the favorable anchor, the headline reads "clears the favorable launch anchor by only −N days"; conversely "RAZOR-THIN"/"only" are emitted regardless of magnitude (a 300-day margin would still print "by only 300 days"). | fix: branch on sign (clears/beats) and apply the fragility qualifier only under a smallness threshold. |
| F13-3 | medium | Bullet L150 "Every documented row reads `no` — … {len(shipping)} shipping" is emitted unconditionally. In the RUNWAY-MOOT branch (`shipping > 0`) it directly contradicts the headline while stating a false universal. | fix: conditionalize the sentence on `shipping`. |
| F13-4 | low | `max(r["decision_date"] for r in rows510 if r["decision_date"])` raises ValueError on a snapshot with zero dated rows (same pattern in bq_15, bq_17). | accept: the corpus snapshot contract guarantees dated FRN records; a crash (loud) is preferable to a silent wrong anchor. |

## bq_14.py — verdict: approve-with-findings

Plan conformance: **conforms** — attribute typing, our-status vocabulary incl. `undocumented`-scored-conservative, verdict rules, closure-vs-adjacency routing (verified above), provisional flags, lane-mapped no-data attributes (dose_personalization) reported unscored. Ties/counts deterministic (attrs sorted; row order stable).

| ID | Sev | Finding | Disposition |
|---|---|---|---|
| F14-1 | medium | `numeric_directions.get(attr, "higher")` (L51): a numeric attribute absent from config silently gets higher-is-better. A new weight-like column added to the matrix without a config row would silently invert its verdict — no flag, no lint hit. | fix: no default — emit a "no direction configured" verdict (or raise) so the gap is visible. |
| F14-2 | low | Latent plan deviation: `parse_numeric` scores a range at the end favorable to the **row's owner**, so an OUR-row range would score at OUR favorable end; the plan commits ranges to the **competitor-favorable** (conservative-against-us) end. Immaterial today — all our cells are point values. | fix: for `our_vendor` rows take the direction-unfavorable end. |
| F14-3 | low | Headline "N attributes compared: a ahead, p parity, b behind" omits the `no-comparison` verdict class (our numeric value undocumented); if one appears the breakdown stops summing to N with no signal. | accept: no such row exists in the curated matrix; revisit if headline math ever stops summing — or add the class to the count string. |
| F14-4 | low | `our_display` truncates at 40 chars mid-word ("patient-controlled analges…" per the prior dossier's friction log; still present). | fix: widen or ellipsize — cosmetic, one-line. |

## bq_15.py — verdict: approve-with-findings

Plan conformance: **conforms** — differentiators from config, competitor-favorable range ends, verified-cell coverage stated, absence lists derived from the pin, dual-basis margins + either-basis trigger (verified above), calendar-month cadence rule exactly as committed (`acq_date > next_review`, strict), publication-lag caveat, FRN-scope caveat. Deterministic (sorted product sets; stable row order).

| ID | Sev | Finding | Disposition |
|---|---|---|---|
| F15-1 | medium | Headline literal "— ahead on either basis;" (L91-92) is **unconditional**. If a pinned competitor value ever beats our volumetric spec, `verdict_txt` correctly says "refresh WARRANTED … margin is eroded" while the *same headline* still asserts "ahead on either basis". The body bullet (L138) branches correctly; the verdict string does not. | fix: make the phrase conditional on `acc_ahead and acc_ahead_vol`, mirroring the body bullet. |
| F15-2 | medium | Zero-competitor-cell branch crashes: with `acc_vals` empty, `acc_best` is None → `acc_best['label']` (L134) raises TypeError; even before that the headline would render "~Nonex". Same for battery. The plan's "comparison covers only documented cells" contemplates thin coverage; the code does not survive empty coverage. | fix: guard the margin/best-label rendering behind a `vals`-present branch with an explicit "no documented cells" sentence. |
| F15-3 | low | Our vendor is hardcoded as `"GlobalLogic"` (L30) and the product label as a string literal in two series (L240, L246), while sibling bq_14 reads `our_vendor` from config (bq_17 hardcodes it too, L45/L50). A vendor rename in config would silently split behavior across modules. | fix: read `our_vendor` (and a display-name param) from config in bq_15/bq_17. |

## bq_16.py — verdict: approve-with-findings

Plan conformance: **conforms** — feature universe from config (zero-row features evaluated), distinct-kol_id voices, sentiment mix + concern-majority rule exactly as committed, E-16.1 evaluated honestly (not-met, unvalidated), wave check with evidence-absence framing (verified above), meta-gap leads the verdict and the report body, history marked unavailable rather than faked. `startswith(tuple(wave_check_years))` handles the F7 "Y3-Y4" slot correctly. Deterministic.

| ID | Sev | Finding | Disposition |
|---|---|---|---|
| F16-1 | low | Flag label hardcodes "below 2-voice floor" (L93) while the floor is config `min_voices_per_feature` — a config change to 3 makes the label lie. | fix: `f"below {floor}-voice floor"`. |
| F16-2 | medium | Latent vocabulary drift is silent: `feat[f][r["sentiment"]] = feat[f].get(...)` accepts any sentiment string, creating a stray key that is excluded from support/neutral/concern and from the concern-majority rule — a register row with e.g. `conditional` would silently vanish from every mix. Current snapshot vocabulary is exactly {support, neutral, concern} (verified). | fix: validate against the 3-value vocabulary and surface unknown values as a data-quality line. |
| F16-3 | low | The Giuliano/F4 + Gorski/F7 spot-check sentence (L117-119) is an unconditional curated literal with no self-retire condition — if those register rows change, the sentence still asserts the spot-checks. | fix: gate on the cited rows still being present-and-concern, or mark the sentence "at curation time (2026-07)". |
| F16-4 | low | `sentiment-mix` series primary `value` duplicates the concern count (support/neutral/concern ride as extra fields) — a console chart plotting `value` shows concern under a generic axis (carried over from the prior dossier's low-severity list; not in the actioned set). | fix: rename/omit the primary value or set it to total rows; console-side risk only. |
| F16-5 | low | Register rows whose `feature_id` is outside the universe are counted in the evidence census but appear nowhere in the per-feature table — silently ignored rather than surfaced. | accept: universe is the committed roadmap; suggest a one-line "rows outside F1-F9: N" if the register ever grows. |

## bq_17.py — verdict: approve-with-findings

Plan conformance: **conforms** — pressure rules (1.0/0.5/0.0) exactly as committed incl. zero-row lane attributes contributing nothing and `lane_watch_keywords` empty-list fallback (`F9: []` → no hits); demand = attach ∩ connected sites (denominator-safe, ≤1 by construction); unweighted mean; eligibility F4–F9; ties and tiebreaks reported; all three plan-committed robustness checks computed and reported (tie-vector invariance, sentiment-axis drop, weight-sensitivity scan); kill-direction caution at verdict level; decision-language discipline held. Markers resolve; composite arithmetic verified previously against pins and reproduced here byte-for-byte.

| ID | Sev | Finding | Disposition |
|---|---|---|---|
| F17-1 | medium | Latent nondeterminism in the pick tie-breaks: `pull_ties`/`kill_ties` (and `pull2`/`kill2`, `elig`) sort generators over a **set** with tie-able keys and no final key. `feature_rank_year` has ties (F4=F5=2027, F6=F7=2028) and voice counts can tie. Today's ties (F4/F6: 2027≠2028; F7/F9: 5≠1 voices) have distinct keys — outputs verified byte-identical across PYTHONHASHSEED 1/42 — but a plausible F4/F5 composite tie makes the pull pick hash-seed-dependent (demonstrated by simulation), which the determinism replay would then flag intermittently. | fix: append the feature id as the final sort key at all four sites, e.g. `key=lambda f: (rank_year[f], f)` / `(len(sent[f]["voices"]), f)`. |
| F17-2 | medium | The Kuitunen caution condition (L138) checks `kill == "F9" and voices == 1` but not **which** voice: the emitted text hardcodes Kuitunen and the quote, so replacing the single F9 row with a different KOL's concern would fire the caution with a false attribution. The sole F9 voice today is KOL-0004 Kuitunen (verified in the pinned register). | fix: tighten to `sent["F9"]["voices"] == {"KOL-0004"}` so an identity change retires the curated text instead of misattributing it. |
| F17-3 | low | The plan's general rule — "where the kill candidate's evidence base is a single voice, state that voice's actual position" — is implemented only for the F9/Kuitunen case. A different single-voice kill candidate would get no direction statement at all. | fix: generalize (fire on any single-voice kill with a "read the per-KOL source doc" pointer) or state the F9-only scope in the module docstring. |
| F17-4 | medium | Sentiment component is not clamped to [0, 1]: `net = (support − concern) / distinct voices` exceeds ±1 if any KOL ever files 2+ rows on one feature (plan commits every component to [0, 1]). Current register has max 1 row per (kol_id, feature_id) — verified — so latent. | fix: clamp `net` to [−1, 1] (or assert one row per pair) so a register append can't silently push a component out of range. |
| F17-5 | low | Zero-voice features silently receive sentiment 0.5 (the neutral midpoint) — a modeling choice the plan/report never disclose; the `zero_voice` list (L91) built to "mark them explicitly" is dead code, and the L89 comment contradicts itself about this exact behavior. No zero-voice feature exists today. | fix: use `zero_voice` to annotate affected rows (or score 0 with a stated data-gap note, symmetric with the demand axis); delete the confused comment. |

---

## Cross-module summary

**Positives (verified, not assumed):** all five modules reproduce their committed 2026-07-27 editions byte-for-byte and are hash-seed deterministic on current pins; no clocks, randomness, or network; every numeric claim in the reports carries resolvable markers and every cited `derived:` id exists in `data.json`; the previously-actioned red-team fixes (RT-13.1/14.1/15.1/16.1/17.1) are genuinely implemented in code, not just in prose — with the two qualifications above (F13-1/F13-2 branch-safety; F17-2 identity pinning).

**The dominant defect class** is *unconditional qualifier literals*: sentences whose truth depends on the data ("months **before**", "ahead on **either** basis", "**Every** documented row reads `no`", "by **only** N days", named spot-checks) are string constants rather than computed branches. All are true on today's pins; several invert under routine data refresh (F13-1 triggers on the next 510(k) anchor advance past 2026-07). The composite arithmetic, config plumbing, and disclosure machinery are otherwise sound.

```json
{"reviews": [
  {"path": "bq_modules/bq_13.py", "verdict": "approve-with-findings",
   "summary": "Plan-conformant and deterministic on current pins; RT-13.1 margin/provenance disclosure implemented. Main risk: direction words in the verdict are literals, not branches - the 'months before our launch' claim inverts when the data anchor advances past mid-2026.",
   "findings": [
     {"severity": "high", "summary": "Headline+bullet hardcode 'months before our launch'; abs() hides sign - inverts on next 510(k) anchor advance", "disposition": "fix: branch before/after on sign of margin; drop abs()"},
     {"severity": "medium", "summary": "hw_edge_days sign unhandled; 'by only N days'/'RAZOR-THIN' emitted regardless of sign or magnitude", "disposition": "fix: branch on sign; fragility qualifier only under smallness threshold"},
     {"severity": "medium", "summary": "'Every documented row reads no' bullet unconditional - false and self-contradicting in the RUNWAY-MOOT branch", "disposition": "fix: conditionalize on shipping"},
     {"severity": "low", "summary": "max() over decision_date raises on a snapshot with zero dated rows (also bq_15/17)", "disposition": "accept: snapshot contract guarantees dated rows; loud crash beats silent wrong anchor"}
   ]},
  {"path": "bq_modules/bq_14.py", "verdict": "approve-with-findings",
   "summary": "Plan-conformant; RT-14.1 closure-vs-adjacency routing correctly implemented with conservative 'adjacent' fallback. Main risk: silent 'higher' default for numeric attributes missing from numeric_directions can invert a future verdict.",
   "findings": [
     {"severity": "medium", "summary": "numeric_directions.get(attr,'higher') silently assumes direction for unmapped numeric attributes - can invert verdict", "disposition": "fix: no default - emit 'no direction configured' verdict or raise"},
     {"severity": "low", "summary": "Our-row ranges score at OUR favorable end; plan commits competitor-favorable end (latent - our cells are points)", "disposition": "fix: take direction-unfavorable end for our_vendor rows"},
     {"severity": "low", "summary": "Headline breakdown omits no-comparison verdict class; counts stop summing if one appears", "disposition": "accept: none exists in matrix; add class to count string if it ever does"},
     {"severity": "low", "summary": "our_display 40-char mid-word truncation persists (prior friction-log note)", "disposition": "fix: widen or ellipsize"}
   ]},
  {"path": "bq_modules/bq_15.py", "verdict": "approve-with-findings",
   "summary": "Plan-conformant; RT-15.1 dual-basis margins and either-basis refresh trigger correctly computed. Main risks: 'ahead on either basis' is an unconditional headline literal that contradicts its own eroded-margin branch, and empty competitor coverage crashes.",
   "findings": [
     {"severity": "medium", "summary": "Headline literal 'ahead on either basis' unconditional - contradicts verdict when volumetric-basis trigger fires", "disposition": "fix: condition phrase on acc_ahead and acc_ahead_vol, mirroring body bullet"},
     {"severity": "medium", "summary": "Zero documented competitor cells crashes (acc_best['label'] on None) or renders '~Nonex' in headline", "disposition": "fix: guard margin/best-label rendering; explicit 'no documented cells' sentence"},
     {"severity": "low", "summary": "Our vendor 'GlobalLogic' + product label hardcoded (also bq_17) while bq_14 reads our_vendor config", "disposition": "fix: read our_vendor/display name from config in bq_15 and bq_17"}
   ]},
  {"path": "bq_modules/bq_16.py", "verdict": "approve-with-findings",
   "summary": "Plan-conformant; meta-gap leads, E-16.1 honest, RT-16.1 evidence-absence framing implemented. Main risk: unknown sentiment vocabulary values silently vanish from mixes and the concern-majority rule.",
   "findings": [
     {"severity": "medium", "summary": "Unknown sentiment values create stray keys, silently excluded from mixes and concern-majority rule (latent vocab drift)", "disposition": "fix: validate against 3-value vocabulary; surface strays as data-quality line"},
     {"severity": "low", "summary": "Flag label hardcodes 'below 2-voice floor' while floor is config min_voices_per_feature", "disposition": "fix: interpolate floor into label"},
     {"severity": "low", "summary": "Giuliano/Gorski spot-check sentence is an unconditional curated literal with no self-retire condition", "disposition": "fix: gate on cited rows still present-and-concern, or mark 'at curation time'"},
     {"severity": "low", "summary": "sentiment-mix series primary value duplicates concern count (unlabeled-axis chart risk; carried from prior dossier)", "disposition": "fix: set primary value to total rows or omit"},
     {"severity": "low", "summary": "Register rows outside the F1-F9 universe counted in census but invisible in per-feature table", "disposition": "accept: universe is the committed roadmap; add stray-row count line if register grows"}
   ]},
  {"path": "bq_modules/bq_17.py", "verdict": "approve-with-findings",
   "summary": "Composite arithmetic, robustness checks, and disclosures verified correct; weight-scan rival tiebreak is genuinely deterministic ((score, id) tuple max). Main risks: pick tie-break sorts lack a final key over set iteration (rank_year and voice counts can tie), and the Kuitunen caution checks voice count but not voice identity.",
   "findings": [
     {"severity": "medium", "summary": "pull/kill tie-break sorts iterate sets with tie-able keys (rank_year F4=F5, F6=F7; voice counts) and no final key", "disposition": "fix: append feature id as final sort key at all four sort sites"},
     {"severity": "medium", "summary": "Kuitunen caution keyed on kill==F9 and voices==1, not voice identity - a changed single F9 voice is misattributed", "disposition": "fix: require sent['F9']['voices'] == {'KOL-0004'} so identity change retires the curated text"},
     {"severity": "medium", "summary": "Sentiment component unclamped: 2+ rows per (kol,feature) pushes it outside plan-committed [0,1] (latent; max 1 today)", "disposition": "fix: clamp net to [-1,1] or assert one row per (kol,feature)"},
     {"severity": "low", "summary": "Plan's single-voice-kill direction rule implemented only for F9; other single-voice kill candidates get no statement", "disposition": "fix: generalize to any single-voice kill, or document F9-only scope"},
     {"severity": "low", "summary": "Zero-voice features silently score 0.5 sentiment, undisclosed; zero_voice list is dead code; L89 comment confused", "disposition": "fix: disclose/mark zero-voice handling via the zero_voice list; delete confused comment"}
   ]}
]}
```
