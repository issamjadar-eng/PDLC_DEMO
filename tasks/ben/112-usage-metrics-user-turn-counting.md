# 112 — Usage-Metrics: User-Turn Counting

**ID**: 112
**Created**: 2026-08-05
**Status**: In Progress
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: Medium

---

## PERMANENT RULES (do not remove)

This task document is the **session-recovery point** for this work. If the current session drops, is compacted, or ends, the next session must be able to load **this file alone** and continue where we left off. That is only possible if the doc is kept current in-flight.

1. **Update at every meaningful checkpoint (HARD RULE).** After each meaningful unit of work — a converted/adopted doc, a committed change, a launched batch, a completed phase, a decision, a discovered blocker, a design pivot — update this task doc: tick the relevant Todo checkbox, add a dated Changelog line naming the concrete artifact (commit SHA, file path, decision, blocker), update any progress counts/tables in Goals, and **when you tick a Todo off, fill/refresh the matching `## Economics` entry in the same edit**.
2. **Phase-end batching is OK; drift-batching is not.** Write at the phase boundary, before the next phase starts — never "at the end of the session."
3. **A commit is not a substitute.** Git history records code; this doc records the project narrative.
4. **Resume-ready before any session boundary.** The doc must contain: (a) what was completed with concrete artifacts, (b) in-flight work and temp artifacts, (c) priority-ordered next steps with file paths, (d) open questions, (e) the exact `/task` activation command.
5. **Capture strategy + lessons as they happen** — in-flight, not just in chat.
6. **Estimation provenance.** The `## Economics` block follows `.claude/skills/usage-metrics/references/effort-estimation-rubric.md`.

Success test for this doc: a fresh Claude session, given only this file, can re-enter the work without asking the user "what were we doing?"

## Goals

_Make **user turns** a first-class usage metric alongside token cost, so the program has a human-effort proxy that is measured rather than estimated._

- Count genuine user↔assistant turns per session, bucketed by day and by task, in `collect.py`.
- Roll them up per month/member and per task in `aggregate.py` and publish in `usage.json`.
- Backfill across all existing transcripts (the data is already on disk — this is not forward-only).
- Keep the schema backward-compatible: session files written before this change lack the field and must not break the aggregator.

## Todos

- [x] `collect.py` — add user-turn detection + `user_turns` block to the session payload
- [x] `aggregate.py` — roll up `user_turns` per month/member and per task; tolerate absence on old files
- [x] Verify counts against a hand-audit of at least one transcript
- [x] Re-collect + re-aggregate to backfill history
- [x] Distinguish "not measured" (`null`) from "measured zero" — see Findings
- [x] Record the resulting data in this doc
- [x] Render unmeasured slots as `--` in the markdown month files and the HTML dashboard
- [x] Push to PDLC_DEMO (PR #173, merge `f286093`), then upstream to the hitachi registry (PR #297, awaiting review)
- [x] Surface turns in the project-console Metrics view (was Resume step 3 — the console is a pure consumer, so no collector change was needed)

## Strategy

<!-- STRATEGY CONTENT: operations, cost-model, architecture -->

**Why this metric.** The program already measures the agentic side automatically (tokens, cost, wall-clock) but the human side only through hand-written `agentic_hours` estimates in each task's `## Economics` block. Those are self-reported and uncalibrated — task ben/098 red-teamed them and landed on "modeled, uncalibrated." User turns are a **measured** human-effort signal sitting unused in transcripts already on disk, so they cost nothing to acquire and are not subject to estimation bias.

**Decision — the existing `messages` counter cannot be reused, and the gap is not a constant.** `collect.py` increments `messages` only on rows carrying `message.usage`, which user messages never have. So `messages` counts *assistant API responses* — every tool call, every subagent reply, every intermediate step. Measured inflation over three real transcripts:

| session | assistant msgs | real user turns | tool results | inflation |
|---|---:|---:|---:|---:|
| `c05c62a3` | 118 | 12 | 166 | 9.8× |
| `62ff8841` | 17 | 7 | 20 | 2.4× |
| `ccbcd1a9` | 72 | 13 | 67 | 5.5× |

The ratio swings with how tool-heavy the work is, so turns **cannot** be derived by scaling `messages` — a separate counter is required. This is the finding that motivates the task.

**Decision — turns bucket by day and task, never by model.** The existing per-session buckets (`by_model`, `by_day`, `by_task`) all share the `_zero()` shape. Adding `user_turns` to that shared shape would emit the field inside `by_model`, where it is meaningless: a user turn is not attributable to a model (the human types before any model is selected, and one turn can span several models via subagents). Rather than publish an always-zero or arbitrarily-attributed field, turns live in their own top-level `user_turns` block with `total` / `by_day` / `by_task`. Cost of the choice: one more branch in the aggregator. Benefit: no field that looks like data but is not.

**Decision — main transcript only, never subagent transcripts.** Subagent transcripts contain `role: user` rows, but those are the harness feeding the subagent its prompt — not a human typing. Counting them would inflate turns by exactly the amount of delegation a task used, which is the opposite of what the metric is for. Turn detection therefore reads only the session's main transcript, while token collection continues to walk subagents recursively.

**Detection rule.** A row counts as a user turn when it is `type: "user"` (or `message.role == "user"`) **and** its content is either a plain string, or a block list containing a `text` block and **no** `tool_result` block. The `tool_result` exclusion is load-bearing: the harness returns every tool result as a `user`-role message, and those outnumber real turns roughly 5–13× in the sampled sessions.

## Findings

### Verification

Hand-audited this session's transcript before trusting the collector: manual count of genuine user turns was 13 at the time of audit, and `collect.py` reported 14 after one further turn arrived. Task attribution also validated — every turn to that point predated task 112's activation, and the collector correctly attributed **0** turns to 112 and split the rest between `111` (7) and `_unattributed` (7), confirming the activation-timeline slicing works for turns exactly as it does for tokens.

### The measured data

Per month (`null` = not measured, see the coverage limit below):

| month | user turns | assistant msgs | cost |
|---|---:|---:|---:|
| 2026-06 | `--` (not measured) | 1,148 | $286.97 |
| 2026-07 | 251 | 5,054 | $1,828.51 |
| 2026-08 | 22 | 134 | $44.25 |

Top tasks by measured turns:

| task | turns | asst msgs | msgs/turn | cost | $/turn |
|---|---:|---:|---:|---:|---:|
| `ben/108` | 113 | 2,393 | 21.2 | $913.41 | $8.08 |
| `ben/_unattributed` | 69 | 1,340 | 19.4 | $319.30 | $4.63 |
| `ben/104` | 35 | 683 | 19.5 | $247.23 | $7.06 |
| `ben/106` | 15 | 453 | 30.2 | $162.19 | $10.81 |
| `ben/103` | 9 | 117 | 13.0 | $56.46 | $6.27 |
| `ben/110` | 7 | 207 | 29.6 | $79.92 | $11.42 |
| `ben/111` | 7 | 60 | 8.6 | $21.23 | $3.03 |
| `ben/102` | 5 | 69 | 13.8 | $26.49 | $5.30 |
| **measured total** | **273** | **5,604** | **20.5** | **$1,918.06** | **$7.03** |

**Program-level read: ~$7 of model spend and ~20 assistant messages per human turn.** That is the ratio the `messages` counter was obscuring — and the per-task spread (8.6 to 30.2 msgs/turn) is wide enough that a single blended multiplier would have been misleading for any individual task.

### Coverage limit — backfill is bounded by transcript retention

The goal said "backfill across all existing transcripts." That was met for every transcript still on disk, but **not for all historical sessions**: turn counts can only be derived from the raw transcripts under `~/.claude/projects/`, and Claude Code rotates those away over time. Current state:

| month | session files | with turn data |
|---|---:|---:|
| 2026-06 | 8 | 0 |
| 2026-07 | 19 | 16 |
| 2026-08 | 3 | 3 |

19 transcripts survive locally (July onward). June's are gone, so those 8 sessions can never be re-derived — **5 tasks carrying $239.92 of measured cost have no turn data and never will.**

**This is why `null` matters.** The first implementation emitted `0` for unmeasured slots, which is indistinguishable from a genuine zero and would have silently corrupted every downstream ratio — a June task would have shown `$286.97 / 0 turns`, either dividing by zero or, worse, being averaged in as "cost with no human involvement." The rollup now tracks whether *any* contributing session file carried the field and emits `null` when none did. Consumers must treat `null` as "not measured," never as zero.

**Practical consequence:** turn data is complete from 2026-07 onward and permanently partial before it. Any turn-based analysis should scope to measured months rather than the full program history — the `$7.03/turn` figure above is over the measured subset ($1,918.06 of $2,159.73 total), not the whole program.

### Display convention — `--`, not `0`, not `null`

Unmeasured turn slots render as **`--`** wherever a human reads them: the per-month markdown files, the HTML dashboard table, and the dashboard's summary card. The JSON keeps `null`.

**Why the split.** Writing the literal string `"--"` into `usage.json` would make `user_turns` sometimes-int / sometimes-string, so every consumer would have to type-sniff before arithmetic — and one that forgot would get a silent string-concat or a `TypeError` instead of a clean null check. `null` is the machine contract; `--` is the human rendering. The console (`project-console`) reads the JSON as a pure consumer and applies its own rendering, so it inherits the same distinction for free.

Two null-collapse traps were caught while wiring this up, both of which would have re-introduced the exact bug the `null` design exists to prevent:

1. **`render_markdown` reads the raw slots**, which carry `user_turns: 0` plus `_turns_seen: False` — not the nulled JSON view. Reading the int directly printed `0` for 2026-06. Fixed by mirroring the `_turns_seen` rule in the renderer.
2. **JS `null + 0` is `0`.** The dashboard's generic totals loop (`for(const k in tot) tot[k] += r[k]||0`) silently converted "not measured" into a measured zero the moment any row lacked turn data. `user_turns` is now excluded from that loop and accumulated null-aware.

The dashboard also names the uncovered months in its footnote, so a merged "all months" view cannot read as an all-time turn total when it is really the measured subset.

## Open Questions

- Should a user turn that arrives mid-assistant-turn (the "user sent a message while you were working" interjection path) count as one turn or be distinguished? Currently counted as one — it is a genuine human input. Revisit if the ratio looks off.

## Resume

**In-flight artifacts**:

- `.claude/skills/usage-metrics/scripts/collect.py` — new `_gather_user_turns()`; `parse_session()` emits a per-month `user_turns` block; payload + grand-total line carry it. **Uncommitted.**
- `.claude/skills/usage-metrics/scripts/aggregate.py` — `user_turns` rolled into month/member and per-task slots with `_turns_seen` null-vs-zero tracking. **Uncommitted.**
- `tasks/ben/_usage-metrics/**` — 19 session files re-derived with turn data (gitignored locally; the SessionEnd hook force-publishes them to the shared branch).
- `tools/usage-metrics/{usage.json,index.html}` — regenerated locally. **Do not commit** — CI owns these; every commit touching them is `usage-metrics: CI aggregate team dashboard [skip ci]`.

**First action on resume**: `bash .claude/hooks/task-activate.sh add <SESSION_ID> 112`, then:

1. Commit `collect.py` + `aggregate.py` + this doc; branch → PR → merge (never commit `usage.json` / `index.html`).
2. Push both scripts upstream via `/sync-skills push` — this is a registry-shared skill and the schema addition should not fork per-project.
3. Consider surfacing turns in the console Metrics view (`project-console` reads `usage.json` as a pure consumer, so the field is already available to it — no collector change needed).

**Do not redo**: the hand-audit verification (done), the backfill (done, and bounded by transcript retention — re-running `collect` will not recover June).

## Economics

_By-hand person-hour estimate per the effort-estimation rubric (`usage-metrics` skill)._

```json
{
  "economics": {
    "method_version": 1,
    "method_ref": ".claude/skills/usage-metrics/references/effort-estimation-rubric.md",
    "agentic_hours": null,
    "todos": []
  }
}
```

## Changelog

- 2026-08-05: Task created, split out of ben/111 (rate card refresh) when the turn-counting question surfaced. Design decisions captured up front: separate `user_turns` block rather than extending the shared `_zero()` bucket shape; main-transcript-only detection; `tool_result` exclusion as the load-bearing filter. Measured the assistant-msgs-to-turns inflation at 2.4×–9.8× across three transcripts, establishing that the existing `messages` counter cannot be rescaled into a turn count.
- 2026-08-05: Implemented. `collect.py` gained `_gather_user_turns()` (main-transcript-only, `tool_result` excluded) and emits a per-month `user_turns` block with `total`/`by_day`/`by_task`, attributed through the same activation timeline as tokens. `aggregate.py` rolls it up into month/member and per-task slots and publishes it in `usage.json`. Verified against a hand-audit of this session (13 manual vs 14 collected after one further turn) and confirmed correct task slicing (0 turns attributed to 112, which had not yet been activated).
- 2026-08-05: Caught and fixed a semantic defect before it shipped — the first implementation emitted `0` turns for sessions whose transcripts have been rotated away, indistinguishable from a genuine zero and corrupting any per-turn ratio. Added `_turns_seen` tracking so unmeasured slots emit `null`. 2026-06 (8 session files, $286.97) now correctly reports `null` rather than `0`.
- 2026-08-05: Measured result across the 273 turns with data — ~$7.03 model spend and ~20.5 assistant messages per human turn, with per-task msgs/turn ranging 8.6–30.2. Coverage is complete from 2026-07 onward and permanently partial before (5 tasks, $239.92, unrecoverable).
- 2026-08-05: Landed in PDLC_DEMO via PR #173 (merge `f286093`) — scripts + task docs only; `usage.json` / `index.html` excluded as CI-authored. Pushed upstream as hitachi PR #297. **Flagged an overlap**: #297 was branched from `origin/main` while ben/111's PR #296 was still open, so #297's `aggregate.py` diff also carries #296's `_retrieved` fix. Both are individually mergeable but must be sequenced — #296 uniquely carries the `templates/pricing.json` seed refresh and must not be dropped. Recorded in `.claude/sync-log.md` and in both PR bodies.
- 2026-08-05: Added the `--` display convention for unmeasured turn slots across the markdown month files, the HTML dashboard table, and the summary card, keeping `null` in `usage.json` as the machine contract. Caught two null-collapse traps in the process: `render_markdown` was reading raw slots (printing `0` for 2026-06) and the dashboard's generic totals loop relied on JS `null + 0 === 0`. Both fixed; verified `null`/`undefined` → `--` while a genuine `0` still renders `0`. Dashboard footnote now names uncovered months so a merged view can't read as an all-time total.
- 2026-08-06: **Fixed the console Metrics view going blank.** All four generated team artifacts under `tools/usage-metrics/` (`usage.json`, `index.html`, `2026-07.md`, `2026-08.md`) carried unresolved `git stash pop` conflict markers (`<<<<<<< Updated upstream` / `>>>>>>> Stashed changes`, 16 hunks total) from the `ben113-wip-others` stash — the `Updated upstream` side being the CI aggregate (which sees only committed session records, so `user_turns: null`) and the `Stashed changes` side the locally-generated one (`user_turns: 251` / `22`). The markers made `usage.json` unparseable, so `console/metrics/loader.py:load_usage()` swallowed the `JSONDecodeError`, returned `None`, and `/metrics` rendered its empty state. Fixed by **regenerating, not hand-merging** — `python3 tools/usage-metrics/aggregate.py`, per the skill's deterministic-aggregation contract (`usage-metrics/SKILL.md` § `setup`: "Aggregation is deterministic (same inputs → byte-identical output)"). The 17 per-session source records under `tasks/ben/_usage-metrics/` were verified intact (0 corrupt) beforehand, so the regenerate was safe. Verified end-to-end on a restarted console: `/metrics` and `/metrics/data` both 200, schema `usage-metrics/team/v2`, all three months present (2026-06 `null` / 2026-07 `251` / 2026-08 `34` turns), no empty-state markers, Metrics nav item rendering. Per the Resume note these four files stay **uncommitted** — CI owns them.

<!-- LESSONS LEARNED: tooling, debugging, git-hygiene -->

**Generated artifacts must be regenerated after a conflicted stash pop, never hand-merged.** A `git stash pop` that conflicts inside a generated file leaves markers in an artifact nobody reads as source — so the corruption is discovered downstream, as a symptom in a consumer, not at the merge. Here it surfaced as "the Metrics tab is blank" three commits later.

**Why:** Two things made it invisible. (1) The conflicting file was *generated*, so no one reviewed the pop's outcome — the mental model is "stash pop conflicts happen in code I'm editing." (2) The consumer failed **silently by design**: `load_usage()` catches `JSONDecodeError` and returns `None`, which is right for a missing file but turns a *corrupt* file into an indistinguishable empty state. Defensive `except` around a parse converts a loud failure into a quiet wrong answer.

**How to apply:**
- After any `git stash pop`/`merge` that reports conflicts, run `grep -rln '^<<<<<<<' .` before doing anything else — cheap, and it catches conflicts in files you weren't thinking about.
- Treat "a consumer shows an empty state" as a data-integrity question first, not a UI bug.
- When the conflicted file is a **generated artifact**, resolve by re-running its producer, not by picking a side. Deterministic producers (`aggregate.py` here) make this the strictly correct move; hand-picking a side can silently ship a stale half.
- Validate the *inputs* before regenerating (`json.load` over every source record) so you don't overwrite a good output from corrupt sources.
- When a loader catches a parse error and returns a "not available" sentinel, distinguish **absent** from **unparseable** — the first is a normal state, the second is a bug that deserves a log line at minimum. `console/metrics/loader.py:load_usage()` currently conflates them.

- 2026-08-06: **Surfaced user turns in the console Metrics view** (closes Resume step 3 — the console consumes `usage.json`, so no collector change was needed). `console/web/static/metrics.js` was still written against schema v1 and rendered none of v2's `user_turns`, so the data landed in the JSON in ben/112 and then sat invisible. Ported the null-aware logic **verbatim in behavior** from the skill's own dashboard (`usage-metrics/scripts/aggregate.py` L621 `turns()`, L639–643 merge, L681–684 total) rather than re-deriving it, so the two views of the same JSON cannot disagree — the skill owns that semantic, the console only renders it. Added: a `User turns` card, turn counts on each by-member bar row, and the month-selection-dependent coverage caveat appended to `#um-costnote`. Also surfaced the v2 rate-card `families` / `default_family` fallback in the rate-card note (previously `models || families` meant families never rendered once `models` existed, so an unlisted model id priced at a family rate was unexplainable from the page).
- 2026-08-06: **Added `Est. cost / turn` and `Msgs / turn` cards** — the actual payoff of measuring turns, and this task's documented headline finding. Both are computed over the **turn-covered subset only** (`cost_measured` / `messages_measured` accumulate solely on months where `user_turns` is non-null), because dividing all-time cost by partially-measured turns silently inflates the ratio — the same null-collapse trap this task already fixed twice in the markdown renderer and the dashboard totals loop. Verified against an independent Python computation of the same JSON: all-months 285 turns / $7.32 / 22.7 msgs — exact match. Month-selection verified for the null path: 2026-06 (uncovered) renders `--` for all three cards and the note names the excluded month; 2026-07 renders 251 / $7.28 / 20.1. **Divergence to note:** the skill's standalone dashboard does not carry these two ratio cards, so the console is now slightly richer than `tools/usage-metrics/index.html`. They are derived, not a competing value for a metric the skill already publishes — but if they earn their keep, push them upstream rather than letting the fork widen.
- 2026-08-06: Widened the Metrics page to 98% of viewport (`body.metrics-body main` in `console.css`) — it was capped at the console's 1040px default while being the widest content in the app (10 stat cards + two time-series). Used `98%` not `98vw`: `vw` includes the scrollbar and overflows horizontally on platforms that reserve gutter space. Widened `.um-barrow`'s value column 150px→230px to fit the newly-added turn count.
