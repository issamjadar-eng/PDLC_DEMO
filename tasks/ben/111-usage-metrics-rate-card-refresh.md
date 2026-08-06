# 111 — Usage-Metrics Rate Card Refresh

**ID**: 111
**Created**: 2026-08-05
**Status**: In Progress
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: Medium

---

## PERMANENT RULES (do not remove)

This task document is the **session-recovery point** for this work. If the current session drops, is compacted, or ends, the next session must be able to load **this file alone** and continue where we left off. That is only possible if the doc is kept current in-flight.

1. **Update at every meaningful checkpoint (HARD RULE).** After each meaningful unit of work — a converted/adopted doc, a committed change, a launched batch, a completed phase, a decision, a discovered blocker, a design pivot — update this task doc:
   - tick the relevant Todo checkbox
   - add a dated Changelog line naming the concrete artifact (commit SHA, file path, decision, blocker)
   - update any progress counts/tables in Goals
   - **when you tick a Todo off (or add/restructure Todos), fill/refresh the matching `## Economics` entry in the same edit** — the by-hand person-hours that unit would have taken, ranged + persona-tagged, per the rubric (if `## Economics` is present / usage-metrics is installed). **Checking the box is the estimate trigger** — don't defer it to a later checkpoint.
2. **Phase-end batching is OK; drift-batching is not.** Planned phases are a legitimate checkpoint — writing once per phase is fine if the phase is bounded and the write happens **at the phase boundary, before the next phase starts**. What's not OK: accumulating updates in your head across arbitrary work, waiting for "end of the session," "after the push," or the user to ask.
3. **A commit is not a substitute.** Git history records code; this doc records the project narrative — what was done, why, what's left, what surprised us.
4. **Resume-ready before any session boundary.** Before recommending a fresh session, marking Complete, or ending work, the doc must already contain: (a) what was completed this session with concrete artifacts, (b) status of any in-flight work and temp artifacts, (c) priority-ordered next steps with file paths, (d) open questions blocking progress, (e) the exact `/task` activation command to resume.
5. **Capture strategy + lessons as they happen.** If the session produces option comparisons, scope/boundary decisions, architectural pivots, non-obvious insights, or corrected assumptions, write them into the appropriate section **in-flight** — not just in chat.
6. **Estimation provenance (if `## Economics` is present).** This doc's `## Economics` block is the by-hand person-hour estimate, built per the effort-estimation rubric at `.claude/skills/usage-metrics/references/effort-estimation-rubric.md` (owned by the `usage-metrics` skill). To **add or refresh** an estimate on resume — even without loading the task skill — read that rubric first for the anchors, personas, and JSON schema; the block also carries a `method_ref` naming it.

Success test for this doc: a fresh Claude session, given only this file, can re-enter the work without asking the user "what were we doing?"

## Goals

_Bring the usage-metrics rate card current with the Anthropic list prices as of 2026-08-05, so cost figures across the Metrics/Value console views price every model the team can actually invoke._

- Refresh `tools/usage-metrics/pricing.json` (and the skill's bundled seed) to the current standard rate card — **standard list prices, not introductory rates** (user decision, see Strategy).
- Add explicit entries for the current-generation flagships (`claude-opus-5`, `claude-sonnet-5`) rather than relying on the substring family fallback.
- Fix the `cost_note` provenance bug that publishes "(updated ?)" into `usage.json` and the dashboard.
- Re-aggregate and confirm the published artifacts carry the refreshed card.

## Todos

- [x] Update `tools/usage-metrics/pricing.json` — add `claude-opus-5` + `claude-sonnet-5`, bump `_retrieved` to 2026-08-05, add `_rates` note pinning the standard-not-intro policy
- [x] Mirror the same change into `.claude/skills/usage-metrics/templates/pricing.json` (the bundled seed) so a fresh install seeds current rates — verified byte-identical
- [x] Fix `aggregate.py` L920 `_updated` → `_retrieved` so `cost_note` stops rendering "(updated ?)"
- [x] Re-run `aggregate.py` and confirm `usage.json` `rate_card._retrieved` + `cost_note` refresh, and that no cost figure moves
- [x] Push (branch → PR → auto-merge); confirm CI `usage-metrics-aggregate.yml` re-runs on the `pricing.json` path trigger — PR #171 merged (`79c58cf`), CI run `31051473259` green in 15s
- [x] Push the `aggregate.py` fix + refreshed seed upstream to the hitachi registry — PR #296, awaiting review

## Strategy

<!-- STRATEGY CONTENT: operations, cost-model -->

**Decision — standard list prices, not introductory rates.** Claude Sonnet 5 currently carries an introductory rate of $2.00/$10.00 per MTok through 2026-08-31, versus its standard $3.00/$15.00. The user directed we use **standard** rates. Rationale: the rate card is an indicative API-equivalent valuation of subscription usage, not an invoice — pinning it to a promotional rate that expires in 26 days would bake in a scheduled inaccuracy and a maintenance trigger nobody owns. Standard rates are the stable, defensible basis and are conservative (they overstate rather than understate).

**Finding — this refresh moves no dollar figure, and that is worth stating plainly.** The rate card as retrieved 2026-06-22 already prices every model present in the collected data at correct standard rates (`claude-fable-5` $10/$50, `claude-opus-4-8` $5/$25, `claude-sonnet-4-6` $3/$15, `claude-haiku-4-5-20251001` $1/$5), with correct cache multipliers (write 1.25× at 5m, 2× at 1h; read 0.1× of input). The only gap was that Opus 5 and Sonnet 5 post-date the card. Because `_rates_for()` falls back to the first `families` key that is a **substring** of the model id, `claude-opus-5` already resolved to the `opus` family and `claude-sonnet-5` to `sonnet` — the same numbers the explicit entries carry. So the edit is correctness and legibility, not a repricing.

**Why add the explicit entries anyway.** Depending on substring fallback for the two current-generation flagships is fragile in a way that fails silently: the fallback resolves against whichever family key matches first, and a future model id whose name does not contain its family token (or contains another family's token) would price wrong with no error and no log line. Explicit entries make the flagships' rates auditable at a glance and remove the dependency on iteration order over the `families` dict.

**Architecture note — pricing is applied at aggregate time, never at collect time.** Per-session records under `tasks/*/_usage-metrics/**` carry token counts only (`input`, `output`, `cache_read`, `cache_write_5m`, `cache_write_1h`) and no cost field. Every dollar figure in `usage.json` — per member, per month, per task, `daily_cost`, `value_summary` — is derived by `aggregate.py` from those tokens × `pricing.json`. This makes the rate card fully retroactive: changing it and re-aggregating re-prices all history, and the GitHub Action triggers on pushes touching `tools/usage-metrics/pricing.json`. No historical figure is ever frozen at a stale rate.

**Known divergence (not in scope).** `statusline.sh` sources its cost from Claude Code's own `.cost.total_cost_usd` on stdin, not from `pricing.json`. The status line and the dashboard are independent cost paths and can legitimately disagree; this task does not attempt to reconcile them.

## Verification

**Claim under test:** refreshing the rate card moves no historical cost figure.

**Method — hold data constant, vary only the card.** Ran `aggregate.py` twice against the same session data: once with the pre-change `pricing.json` (`git show HEAD:tools/usage-metrics/pricing.json`), once with the refreshed card. Compared every cost-bearing field in `usage.json`: per-month per-member `cost`, per-month per-member per-model `cost`, per-task `cost`, every `daily_cost` entry, and every `cost*` key in `value_summary`.

**Result: 0 of 146 cost data points changed.** The refresh is provably rate-neutral.

**Resolver check.** Confirmed the new explicit entries resolve to exactly what the substring fallback previously produced, so no behavioural change is smuggled in with the additions:

| model id | explicit | via fallback | match |
|---|---|---|---|
| `claude-opus-5` | 5.0 / 25.0 | 5.0 / 25.0 | yes |
| `claude-opus-5[1m]` | 5.0 / 25.0 | 5.0 / 25.0 | yes |
| `claude-sonnet-5` | 3.0 / 15.0 | 3.0 / 15.0 | yes |
| `claude-fable-5` | 10.0 / 50.0 | 10.0 / 50.0 | yes |
| `claude-opus-4-8` | 5.0 / 25.0 | 5.0 / 25.0 | yes |
| `claude-sonnet-4-6` | 3.0 / 15.0 | 3.0 / 15.0 | yes |
| `claude-haiku-4-5-20251001` | 1.0 / 5.0 | 1.0 / 5.0 | yes |

Note `claude-opus-5[1m]` — the 1M-context variant id carries a bracketed suffix, so it never matches an exact `models[]` key and always resolves through the family fallback. It prices correctly, but this is the concrete case that motivates keeping the fallback robust rather than treating explicit entries as sufficient.

**Post-merge follow-up — the Opus 5 entry became load-bearing the same day.** After the refresh landed, a `collect` run picked up `claude-opus-5` in the transcripts for the first time (this session runs on it). The explicit `models["claude-opus-5"]` entry added by this task is now resolving as an **exact match** rather than through the substring family fallback — so the change moved from defensive to active within hours of merging. Measured per-model totals across all months at that point:

| model | cost | input | output | cache read | msgs |
|---|---:|---:|---:|---:|---:|
| `claude-fable-5` | $1,660.83 | 8,771 | 4,411,183 | 1,080,175,485 | 4,388 |
| `claude-opus-4-8` | $461.53 | 589,961 | 2,060,886 | 633,068,765 | 1,796 |
| **`claude-opus-5`** | **$26.64** | 141 | 51,907 | 28,247,628 | 75 |
| `claude-sonnet-4-6` | $1.60 | 6 | 795 | 0 | 2 |
| `claude-haiku-4-5-20251001` | $0.35 | 641 | 16,172 | 1,069,352 | 33 |
| **total** | **$2,150.95** | | | | |

Worth noting for anyone reading the cost figures: **cache reads dominate the spend profile.** 1.08B cache-read tokens on `claude-fable-5` at 0.1× input is where that $1,660 actually comes from — not output. Any future cost-reduction effort should target context size and cache behaviour, not output verbosity. This is exactly the kind of read the rate card exists to enable, and it depends on the 5m/1h cache-write split `collect.py` preserves.

**Unrelated movement observed and attributed.** A first re-aggregate (before the controlled comparison) did move two figures: `value_summary.cost_allocated` 215.73 → 224.56 and `cost_unattributed_residual` 91.14 → 82.31, summing constant at 306.87. Cause is **not** pricing — it is the retrospective allocator (`allocate_unattributed()`) re-splitting unattributed spend now that the session-start `git pull` brought in a new 2026-08 session record with additional day-overlap. Isolated and confirmed by the hold-data-constant run above.

## Open Questions

- Fast mode on Opus 5 bills at $10/$50 (double standard). If transcripts do not record the `speed` parameter, fast-mode sessions would be costed at standard Opus rates and understated ~2×. Not resolvable from the rate card alone — needs a check of whether `collect.py` can observe speed. Deferred; no fast-mode usage in the current dataset.

## Resume

**In-flight artifacts**:

- **PDLC_DEMO — merged.** PR [#171](https://github.com/GlobalLogic-a-Hitachi-Company/PDLC_DEMO/pull/171), merge commit `79c58cf`, branch deleted both sides. Local clone is on `main`. Aggregate workflow run `31051473259` fired on the merge and went green in 15s, so `usage.json` / `index.html` on `main` are CI-regenerated with the new card.
- **Registry — open, awaiting review.** hitachi PR [#296](https://github.com/GlobalLogic-a-Hitachi-Company/hitachi/pull/296) carries the `aggregate.py` provenance fix + the refreshed `templates/pricing.json` seed. Pushed PR-only (no `--merge`), so the hitachi checkout still has local branch `sync/pdlc-demo-usage-metrics-rate-card-2026-08-05`; it will need `/sync-skills prune` after the PR merges.
- **Uncommitted in the working tree, deliberately left alone** — not this task's: `tasks/ben/108-commercial-analytics-suite.md`, `tasks/ben/SECOPS.md` (pre-existing user edits), and locally regenerated `tools/usage-metrics/{usage.json,index.html}` (CI-owned; never hand-committed).

**First action on resume**: `bash .claude/hooks/task-activate.sh add <SESSION_ID> 111`, then:

1. Check hitachi PR #296 — if merged, run `/sync-skills prune` to clear the stale `sync/*` branch, and confirm `/sync-skills status` reports drift 0.
2. If #296 is still open, nothing to do; the local fix is already live in this project.
3. Then mark this task Complete via `/task update ben 111 Complete`.

**Do not redo**: the rate-neutrality verification (done, 0/146), the PDLC merge (done), or re-committing `usage.json` / `index.html` (CI owns them — every commit touching those files is `usage-metrics: CI aggregate team dashboard [skip ci]`).

## Economics

_By-hand person-hour estimate per the effort-estimation rubric (`usage-metrics` skill)._

```json
{
  "economics": {
    "method_version": 1,
    "method_ref": ".claude/skills/usage-metrics/references/effort-estimation-rubric.md",
    "agentic_hours": 0.5,
    "todos": [
      {
        "todo": "Trace the pricing wiring end-to-end (skill contract, both pricing.json copies, aggregate.py resolver + cost path, console consumer, session-record schema)",
        "persona": "engineer",
        "by_hand_hours": { "min": 1.0, "max": 2.5 },
        "note": "Reading an unfamiliar telemetry pipeline to establish where cost is applied and whether it is retroactive. The load-bearing question — is cost baked in at collect time or computed at aggregate time — is not answerable without reading the resolver and a raw session record."
      },
      {
        "todo": "Establish the current standard rate card and reconcile against the installed card",
        "persona": "engineer",
        "by_hand_hours": { "min": 0.5, "max": 1.0 },
        "note": "Includes catching that Sonnet 5 carries an introductory rate distinct from standard, which is the one judgement call in the task."
      },
      {
        "todo": "Edit both pricing.json copies + fix the cost_note provenance bug",
        "persona": "engineer",
        "by_hand_hours": { "min": 0.25, "max": 0.5 },
        "note": "Mechanical once the rates are known."
      },
      {
        "todo": "Verify rate-neutrality by controlled re-aggregate (hold data constant, vary card) and attribute the unrelated allocator movement",
        "persona": "engineer",
        "by_hand_hours": { "min": 0.75, "max": 2.0 },
        "note": "The wide range reflects that the obvious approach — re-run and diff — produces two changed figures that look like a pricing effect and are not. Attributing that correctly requires constructing the hold-data-constant comparison rather than trusting the naive diff."
      }
    ]
  }
}
```

## Changelog

- 2026-08-05: Task created. Scanned the pricing wiring (SKILL.md contract, `pricing.json` × 2 copies, `aggregate.py` resolver/cost path, console Metrics loader as pure consumer). Established that cost is computed at aggregate time from pricing-free session records, so the card is fully retroactive. Recorded the standard-vs-intro-rate decision and the finding that no dollar figure changes.
- 2026-08-05: Refreshed the rate card. `tools/usage-metrics/pricing.json` + the bundled seed `.claude/skills/usage-metrics/templates/pricing.json` now carry explicit `claude-opus-5` (5.0/25.0) and `claude-sonnet-5` (3.0/15.0) entries, `_retrieved` 2026-06-22 → 2026-08-05, and a new `_rates` field pinning the standard-not-introductory policy so the next person to refresh does not silently adopt a promo rate. Both copies verified byte-identical and JSON-valid (14 models each).
- 2026-08-05: Fixed `aggregate.py:920` — read `_updated` (a key the rate card has never carried) instead of `_retrieved`, publishing `cost_note: "… (updated ?)"` into `usage.json` and the dashboard. Now reads `_retrieved`, matching the HTML template at L737. Candidate for push-back to the hitachi registry.
- 2026-08-05: Verified rate-neutrality — 0 of 146 cost data points changed with data held constant across old vs new card (see Verification). Confirmed the two figures that did move on a naive re-aggregate are the retrospective allocator responding to newly pulled session data, not the rates.
- 2026-08-05: Landed in PDLC_DEMO via PR #171 (merge `79c58cf`), branch deleted. Committed 5 source files only; `usage.json` / `index.html` deliberately excluded as CI-authored. Aggregate workflow run `31051473259` fired on the merge path trigger and completed green in 15s, regenerating the dashboard on `main` with the refreshed card.
- 2026-08-05: Pushed the `aggregate.py` provenance fix + refreshed seed rate card upstream — hitachi PR #296, PR-only (awaiting review). Seed inclusion was a deliberate scope extension beyond the original bug fix, approved by user: a fresh `usage-metrics` install in any project was seeding a 2026-06-22 card with no Opus 5 / Sonnet 5 entries. Recorded in `.claude/sync-log.md`. Leaves a local `sync/*` branch in the hitachi checkout pending `/sync-skills prune` post-merge.
- 2026-08-05: Close-out records merged via PR #172 (`6af9074`). Post-merge, a `collect` run surfaced `claude-opus-5` in the transcripts for the first time — the explicit entry added by this task is now an exact `models[]` match rather than a fallback resolution, and prices $26.64 of Opus 5 usage. Per-model totals recorded in Verification; headline observation is that cache reads (1.08B tokens on Fable 5) dominate the cost profile, not output.
