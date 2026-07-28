# Code review — the five roadmap analysis programs (BQ-13 to BQ-17)

**What was reviewed**: the five small computer programs that calculate the answers to
business questions BQ-13 through BQ-17 (competitive runway, feature parity, state-of-the-art
currency, KOL evidence, and the roadmap kill/pull-forward ranking).
Files: `docs/project/commercial/bq_modules/bq_13.py` … `bq_17.py`.

- **Date**: 2026-07-27 (findings resolved same day)
- **Reviewer**: AI assistant (independent code-review pass, task ben/108)
- **Verdict in one line**: all five programs compute their published answers correctly
  today; the review found wording and safety-margin defects that would surface on future
  data refreshes — all have since been fixed or explicitly accepted.

## Plain-language summary

We reviewed the five programs that produce the roadmap-related business answers, checking
that each one follows its written analysis plan, produces the same result every time it
runs, and cannot quietly say something untrue when the underlying data changes. Every
number in the published answers was confirmed correct. The review raised 21 issues: 1
serious (a headline sentence that would state the opposite of the truth after a routine
data update), 9 moderate (mostly sentences whose wording was fixed text rather than
computed from the data, plus a few places where a future data change could silently skew a
result), and 11 minor. Since the review, 18 of the 21 have been fixed in the code and
verified by re-reading it; the remaining 3 were consciously accepted with a written reason
(for example, preferring a loud crash over a silently wrong answer when data is missing).
Nothing remains unresolved.

## What we checked

- Each program against its committed analysis plan — does the code do what the plan says?
- Repeatability — run twice with different randomization settings, results byte-identical,
  and identical to the published 2026-07-27 answers.
- "Fixed wording" hazards — sentences that are only true for today's data and would become
  false, without warning, after a data refresh.
- Arithmetic traps — sign handling, rounding, division by zero, empty-data behavior.
- Configuration discipline — values read from the shared configuration file rather than
  typed into the code.
- Earlier red-team findings — confirming the previously agreed fixes really exist in code.

## Findings

### F-13-1 (high) — the runway headline could state "before" when the truth is "after"

**What's wrong:** BQ-13's headline said a rival's projected clearance lands "about N months
**before** our launch" using fixed wording that discarded the direction of the calculation
(an `abs()` call hid the sign of the computed margin).
**Why it matters:** the launch-runway verdict is the single most-quoted sentence of this
answer. After the next routine refresh of the FDA clearance data, the sentence would have
inverted its own fact — claiming a rival beats us to market when the numbers say the
opposite.
**Resolution:** FIXED — the direction word ("before" / "after" / "same month") is now
computed from the sign of the margin, in the headline, the supporting bullet, and the data
series label.

### F-13-2 (medium) — "razor-thin" was hard-wired regardless of the actual margin

**What's wrong:** the sentence describing the hardware-competitor margin always said the
edge "clears … by only N days" and called it fragile, whatever N was, and could not express
a negative margin (competitor ahead of us).
**Why it matters:** a 300-day cushion would still have been called razor-thin, and a
competitor actually beating our date would have been reported as us being safely ahead.
**Resolution:** FIXED — the sentence now branches on the sign of the margin, and the
fragility wording applies only below a declared 90-day threshold (a named constant in the
module).

### F-13-3 (medium) — "every documented row reads no" printed even when untrue

**What's wrong:** a bullet asserting that no competitor documents shipping the capability
was printed unconditionally, including in the branch where competitors do ship it.
**Why it matters:** the report could contradict its own headline while stating a false
universal.
**Resolution:** FIXED — the bullet is now chosen from two computed variants depending on
whether any shipping rows exist.

### F-13-4 (low) — crash on a dataset with no dated records

**What's wrong:** finding the newest decision date crashes if a data snapshot ever arrived
with zero dated rows (same pattern in BQ-15 and BQ-17).
**Why it matters:** an abrupt failure instead of a graceful message.
**Resolution:** ACCEPTED — the data-acquisition contract guarantees dated records, and a
loud crash is preferable to silently computing a wrong anchor date.

### F-14-1 (medium) — an unconfigured attribute silently got a "higher is better" guess

**What's wrong:** for numeric comparisons, an attribute missing from the direction
configuration defaulted to "higher is better" with no warning.
**Why it matters:** a new column added to the comparison data without a configuration row
could invert a published ahead/behind verdict, invisibly.
**Resolution:** FIXED — there is no default any more; an unconfigured attribute is surfaced
as "NOT SCORED — direction unconfigured" in both the table and the headline.

### F-14-2 (low) — our own ranged values scored at our favorable end

**What's wrong:** when a value is a range (e.g. "4–6"), the code scored our rows at the end
most favorable to us, while the plan commits to the conservative-against-us end.
**Why it matters:** latent optimism bias — immaterial today because all our cells are
single values, but wrong the day a range appears.
**Resolution:** FIXED — our rows are now scored at the direction-unfavorable end via an
explicit parameter on the parsing helper.

### F-14-3 (low) — headline count could stop adding up

**What's wrong:** the headline breakdown ("N compared: a ahead, p parity, b behind") omits
the rare "no comparison possible" category.
**Why it matters:** if such a row ever appears, the counts stop summing to N.
**Resolution:** ACCEPTED — no such row exists in the curated data; revisit if the headline
arithmetic ever stops summing.

### F-14-4 (low) — values cut off mid-word in the display

**What's wrong:** long cell values were truncated at 40 characters mid-word.
**Why it matters:** cosmetic; unprofessional-looking tables.
**Resolution:** FIXED — a display helper now allows 80 characters and ellipsizes cleanly on
a word boundary.

### F-15-1 (medium) — "ahead on either basis" was fixed text that could contradict the verdict

**What's wrong:** BQ-15's headline always asserted our accuracy lead holds on both
measurement bases, even in the branch where the computed verdict says the lead is eroded.
**Why it matters:** the same sentence would simultaneously call for a refresh because the
lead eroded and claim the lead holds — a direct self-contradiction in the verdict line.
**Resolution:** FIXED — the phrase is now computed from the two per-basis results ("either
basis" / "LAB basis only" / "volumetric basis only" / "NOT ahead on either basis").

### F-15-2 (medium) — a comparison with zero documented competitor values crashed

**What's wrong:** with no competitor cells for an attribute, the code crashed (or would
have rendered "~Nonex") instead of degrading cleanly.
**Why it matters:** thin data coverage is a real possibility the plan contemplates; the
report must say "no documented cells" rather than fail.
**Resolution:** FIXED — every margin/best-competitor rendering is guarded; the empty case
now renders an explicit "no documented competitor cells — no margin computable" sentence,
and the refresh-trigger check treats the no-data state as neither ahead nor eroded.

### F-15-3 (low) — company name typed into the code instead of read from configuration

**What's wrong:** our vendor name and product label were string literals in BQ-15 (and
BQ-17) while sibling BQ-14 read them from configuration.
**Why it matters:** a vendor rename in the configuration would silently split behavior
across modules.
**Resolution:** FIXED — both modules now read the vendor identity (and BQ-15 the product
display label) from configuration.

### F-16-1 (low) — the "2-voice floor" label ignored the configurable floor

**What's wrong:** the flag text hard-coded "below 2-voice floor" while the floor is a
configuration value.
**Why it matters:** raising the floor to 3 would make the label lie.
**Resolution:** FIXED — the label interpolates the configured floor.

### F-16-2 (medium) — an unexpected sentiment value would silently vanish

**What's wrong:** a register row with a sentiment outside the three-value vocabulary
(support / neutral / concern) would be silently dropped from every mix and from the
concern-majority rule.
**Why it matters:** silent data loss in the input to a roadmap-level flag.
**Resolution:** FIXED — sentiments are validated against the vocabulary; out-of-vocabulary
rows are counted and surfaced as a visible DATA QUALITY line in the report.

### F-16-3 (low) — a curated example sentence had no retirement condition

**What's wrong:** the sentence citing two specific advisors' source-document positions
(the Giuliano/F4 and Gorski/F7 spot checks) printed unconditionally even if those register
rows changed.
**Why it matters:** the report could keep asserting spot checks that no longer match the
data.
**Resolution:** FIXED — the sentence now self-retires: the code checks both cited rows are
still present with "concern" sentiment, and otherwise prints a retirement notice telling
the reader to re-verify.

### F-16-4 (low) — a chart's primary value was misleading

**What's wrong:** the sentiment-mix data series carried the concern count as its primary
value, so a generic chart would plot concern under an unlabeled axis.
**Why it matters:** console-side misreading risk.
**Resolution:** FIXED — the primary value is now the row total; support/neutral/concern
ride as named fields.

### F-16-5 (low) — register rows outside the feature universe are invisible in the table

**What's wrong:** rows for features outside the committed roadmap are counted in the
census but appear in no per-feature table.
**Why it matters:** minor discoverability gap.
**Resolution:** ACCEPTED — the universe is the committed roadmap; add a stray-row count
line if the register ever grows beyond it.

### F-17-1 (medium) — ranking tie-breaks could depend on the computer's memory layout

**What's wrong:** the sorts that pick the pull-forward and kill candidates iterated over an
unordered set with keys that can tie (two features share a rank year; voice counts can
tie), with no final deterministic key.
**Why it matters:** on a genuine tie, the published pick could differ from run to run —
breaking the reproducibility guarantee the whole pipeline is built on. (Demonstrated by
simulation; today's data has no such tie.)
**Resolution:** FIXED — the feature id is appended as the final sort key at all five sort
sites (eligibility ranking, both tie lists, and both sentiment-axis-drop re-picks).

### F-17-2 (medium) — a named-person caution could fire with the wrong person's words

**What's wrong:** the caution quoting the single dissenting advisor (Kuitunen) checked only
that one voice existed, not whose voice it was; a register change swapping in a different
advisor would print the old name and quote.
**Why it matters:** misattributing a quoted expert position in a decision-support report.
**Resolution:** FIXED — the condition now pins the voice's identity (the exact advisor id,
KOL-0004); a different voice retires the curated text instead of misattributing it.

### F-17-3 (low) — the single-voice rule was implemented for one case only

**What's wrong:** the plan's rule "when a kill candidate rests on a single voice, state
that voice's actual position" existed only for the F9/Kuitunen case.
**Why it matters:** a different single-voice kill candidate would get no direction
statement.
**Resolution:** FIXED — the F9-only scope is now declared in the module's docstring (the
dossier's accepted alternative to generalizing), with instructions to extend the curated
note before relying on it for other cases.

### F-17-4 (medium) — a scoring component could drift outside its committed range

**What's wrong:** the sentiment component was not clamped to the plan-committed 0-to-1
range; an advisor filing two rows on one feature would push it outside.
**Why it matters:** an out-of-range component silently distorts the composite ranking.
**Resolution:** FIXED — the net sentiment is clamped to [-1, 1] before rescaling.

### F-17-5 (low) — features with no voices silently scored "neutral"

**What's wrong:** a feature with zero advisor voices received the neutral midpoint score
with no disclosure, and the list built to mark such features was dead code.
**Why it matters:** absence of evidence was silently treated as lukewarm evidence.
**Resolution:** FIXED — the zero-voice list is now used: when any zero-voice feature
exists, the report states it has no sentiment signal and that the midpoint is a modeling
choice, not evidence; the contradictory comment was removed.

## Terms used

- **Analysis plan** — the written, committed description of how a business question must
  be computed; the code is reviewed against it.
- **Pin / pinned snapshot** — the exact, dated copy of a dataset an answer was computed
  from, so the answer can be reproduced byte-for-byte later.
- **Headline / verdict** — the one-sentence answer at the top of each published report.
- **Composite** — BQ-17's combined score (competition + sentiment + demand) used to rank
  roadmap features.
- **Basis** — the definitional choice a comparison or rate is computed under (which
  specification standard, window, or population); "ahead on either basis" means the lead
  survives both defensible choices.
- **Deterministic** — same inputs always produce the same output, byte for byte.
- **KOL** — key opinion leader; a clinical expert advisor.
- **Fixed-wording (string-literal) defect** — a sentence typed as constant text whose truth
  actually depends on the data; the dominant defect class in this review.

## Technical appendix

Empirical checks performed at review time: each module run twice under
`PYTHONHASHSEED=1` and `=42`; `report.md` + `data.json` byte-compared — all five identical
across seeds and byte-identical to the committed 2026-07-27 editions. Register data
inspected to validate latent-input assumptions (sentiment vocabulary exactly
{support, neutral, concern}; max 1 row per (kol_id, feature_id); sole F9 voice is
KOL-0004). The F-17-1 tie hazard was demonstrated by simulation on a synthetic F4/F5 tie.

Fix verification (2026-07-27, current code):

| Finding | Resolution | Where (current code) |
|---|---|---|
| F-13-1 | fixed | `bq_13.py` L81–87 (`samd_rel`), L197–204 (slow bullet) |
| F-13-2 | fixed | L19–20 (`FRAGILE_EDGE_DAYS`), L88–90, L140–148, L205–214, L267–277 |
| F-13-3 | fixed | L170–179 (`premise_bullet` branches) |
| F-13-4 | accepted | L56 (`max()` over decision dates; loud crash by contract) |
| F-14-1 | fixed | `bq_14.py` L61–71 (unscored row), L150–152 (headline) |
| F-14-2 | fixed | L24–33 (`favorable=False`), L73–76 |
| F-14-3 | accepted | headline count omits `no-comparison` (none exists) |
| F-14-4 | fixed | L17–21 (`display_value`, 80 chars, ellipsis) |
| F-15-1 | fixed | `bq_15.py` L92–104 (`basis_txt` computed) |
| F-15-2 | fixed | L95–106, L145–166, L179–192, L210–214 (guards + None states) |
| F-15-3 | fixed | L27–28 (config `our_vendor` / `our_product_label`); `bq_17.py` L37 |
| F-16-1 | fixed | `bq_16.py` L106 (floor interpolated) |
| F-16-2 | fixed | L14, L38, L44–47, L119–127 (vocabulary check + DATA QUALITY line) |
| F-16-3 | fixed | L51–56 (`spot_checks_hold`), L140–147 (retire branch) |
| F-16-4 | fixed | L219–224 (primary value = total) |
| F-16-5 | accepted | out-of-universe rows census-only |
| F-17-1 | fixed | `bq_17.py` L114–136 (id as final key at all five sorts) |
| F-17-2 | fixed | L156 (`voices == {"KOL-0004"}`) |
| F-17-3 | fixed | L8–13 (docstring scope note) |
| F-17-4 | fixed | L96–98 (clamp) |
| F-17-5 | fixed | L100–102, L196–199 (zero-voice disclosure) |

Prior red-team fixes re-verified in code at review time: RT-13.1 (both anchor readings +
margin disclosure), RT-14.1 (closure-vs-adjacency routing with conservative `adjacent`
fallback), RT-15.1 (dual-basis margins, either-basis trigger), RT-16.1 (evidence-absence
framing), RT-17.1 (deterministic rival tiebreak via `(score, id)` tuple max; weights sum
to 1; scan granularity honestly reported).

Machine-readable record (dispositions reflect actual outcomes):

```json
{"reviews": [
  {"path": "bq_modules/bq_13.py", "verdict": "approve-with-findings",
   "summary": "Plan-conformant and deterministic on current pins; RT-13.1 disclosure implemented. All direction-word literals now branch-computed.",
   "findings": [
     {"id": "F-13-1", "severity": "high", "summary": "Headline+bullet hardcoded 'months before our launch'; abs() hid sign", "disposition": "fixed: direction word computed from sign of margin in headline, bullet, and series label"},
     {"id": "F-13-2", "severity": "medium", "summary": "hw_edge_days sign unhandled; 'by only N days'/'RAZOR-THIN' emitted regardless of sign or magnitude", "disposition": "fixed: sign branches + FRAGILE_EDGE_DAYS=90 smallness threshold"},
     {"id": "F-13-3", "severity": "medium", "summary": "'Every documented row reads no' bullet unconditional", "disposition": "fixed: bullet branches on shipping"},
     {"id": "F-13-4", "severity": "low", "summary": "max() over decision_date raises on zero dated rows (also bq_15/17)", "disposition": "accepted: snapshot contract guarantees dated rows; loud crash beats silent wrong anchor"}
   ]},
  {"path": "bq_modules/bq_14.py", "verdict": "approve-with-findings",
   "summary": "Plan-conformant; RT-14.1 routing correct. Unmapped numeric attributes now surface loudly instead of defaulting.",
   "findings": [
     {"id": "F-14-1", "severity": "medium", "summary": "numeric_directions.get(attr,'higher') silently assumed direction", "disposition": "fixed: no default - 'direction-unconfigured' verdict surfaced in table and headline"},
     {"id": "F-14-2", "severity": "low", "summary": "Our-row ranges scored at OUR favorable end; plan commits competitor-favorable end", "disposition": "fixed: favorable=False for our_vendor rows in parse_numeric"},
     {"id": "F-14-3", "severity": "low", "summary": "Headline breakdown omits no-comparison verdict class", "disposition": "accepted: none exists in matrix; revisit if counts stop summing"},
     {"id": "F-14-4", "severity": "low", "summary": "our_display 40-char mid-word truncation", "disposition": "fixed: display_value ellipsizes at 80 chars on word boundary"}
   ]},
  {"path": "bq_modules/bq_15.py", "verdict": "approve-with-findings",
   "summary": "Plan-conformant; RT-15.1 dual-basis margins correct. Basis phrase now computed; empty-coverage branch degrades cleanly; vendor identity from config.",
   "findings": [
     {"id": "F-15-1", "severity": "medium", "summary": "Headline literal 'ahead on either basis' unconditional", "disposition": "fixed: basis_txt computed from acc_ahead and acc_ahead_vol across all four states"},
     {"id": "F-15-2", "severity": "medium", "summary": "Zero documented competitor cells crashed (acc_best['label'] on None) or rendered '~Nonex'", "disposition": "fixed: guarded rendering + explicit 'no documented cells' sentences + None trigger states"},
     {"id": "F-15-3", "severity": "low", "summary": "Vendor 'GlobalLogic' + product label hardcoded (also bq_17)", "disposition": "fixed: our_vendor / our_product_label read from config in bq_15 and bq_17"}
   ]},
  {"path": "bq_modules/bq_16.py", "verdict": "approve-with-findings",
   "summary": "Plan-conformant; meta-gap leads; RT-16.1 framing implemented. Vocabulary drift now loud; curated spot-check sentence self-retires.",
   "findings": [
     {"id": "F-16-1", "severity": "low", "summary": "Flag label hardcoded 'below 2-voice floor' while floor is config", "disposition": "fixed: floor interpolated into label"},
     {"id": "F-16-2", "severity": "medium", "summary": "Unknown sentiment values silently vanished from mixes and concern-majority rule", "disposition": "fixed: validated against 3-value vocabulary; strays surfaced as DATA QUALITY line"},
     {"id": "F-16-3", "severity": "low", "summary": "Giuliano/Gorski spot-check sentence unconditional, no self-retire", "disposition": "fixed: spot_checks_hold gate on present-and-concern rows; retirement notice otherwise"},
     {"id": "F-16-4", "severity": "low", "summary": "sentiment-mix series primary value duplicated concern count", "disposition": "fixed: primary value is row total; components as named fields"},
     {"id": "F-16-5", "severity": "low", "summary": "Register rows outside F1-F9 universe counted in census but invisible in table", "disposition": "accepted: universe is the committed roadmap; add stray-row line if register grows"}
   ]},
  {"path": "bq_modules/bq_17.py", "verdict": "approve-with-findings",
   "summary": "Composite arithmetic and robustness checks verified; tie-break sorts now carry a final id key; Kuitunen caution pinned to voice identity; component clamped; zero-voice case disclosed.",
   "findings": [
     {"id": "F-17-1", "severity": "medium", "summary": "pull/kill tie-break sorts iterated sets with tie-able keys and no final key", "disposition": "fixed: feature id appended as final sort key at all five sort sites"},
     {"id": "F-17-2", "severity": "medium", "summary": "Kuitunen caution keyed on count not identity; changed voice would be misattributed", "disposition": "fixed: condition requires voices == {KOL-0004}; identity change retires the text"},
     {"id": "F-17-4", "severity": "medium", "summary": "Sentiment component unclamped; 2+ rows per (kol,feature) pushes it outside [0,1]", "disposition": "fixed: net clamped to [-1,1] before rescale"},
     {"id": "F-17-3", "severity": "low", "summary": "Single-voice-kill direction rule implemented only for F9", "disposition": "fixed: F9-only scope documented in module docstring with extension instructions"},
     {"id": "F-17-5", "severity": "low", "summary": "Zero-voice features silently scored 0.5; zero_voice list dead code", "disposition": "fixed: zero-voice disclosure rendered when present; dead comment removed"}
   ]}
]}
```
