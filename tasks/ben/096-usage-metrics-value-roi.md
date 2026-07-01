# 096 — Usage-Metrics: Value / ROI (person-hours saved via agentic-first)

**ID**: 096
**Created**: 2026-06-30
**Status**: In Progress
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: High

---

## PERMANENT RULES (do not remove)

This task document is the **session-recovery point** for this work. If the session drops, is compacted, or ends, the next session must be able to load **this file alone** and continue.

1. **Update at every meaningful checkpoint (HARD RULE)** — tick todos, add a dated changelog line with the concrete artifact, update counts.
2. **Phase-end batching OK; drift-batching not.**
3. **A commit is not a substitute** for the task-doc narrative.
4. **Resume-ready before any session boundary.**
5. **Capture strategy + lessons in-flight**, not as cleanup.

Success test: a fresh session, given only this file, can re-enter without asking "what were we doing?"

## Goals

_Turn usage-metrics from "tokens spent" into "value delivered." Answer, with data: the agentic-first approach did this work for ~these tokens / this wall-clock; by hand it would have taken **X–Y person-hours** of specialist time._

- **Attribute real actuals to tasks** — per-task tokens + wall-clock, with **no double counting**, where we have transcript data.
- **Produce person-hour estimates** of the by-hand baseline — **ranged (min–max), persona-tagged**, generated **inline as work happens** (main thread, no subagent on the hot path), plus **retrospectively** for the ~95 existing task docs.
- **Generate the JSON dataset** the project-console Value view consumes (one generator; measured + retrospective inputs).
- **Keep the hot path lightweight**; defensibility comes from ranges + calibration + red-team-the-aggregate, not from a human approval gate.

## Design & Decisions

<!-- STRATEGY CONTENT: architecture, agentic-value-measurement, usage-metrics+task+project-console -->

### A. Attribution of actuals (tokens/time → task) — no double counting

- **Source of truth = the session transcript** (`~/.claude/projects/<slug>/<session_id>.jsonl`), written continuously by Claude Code. **NOT SessionEnd.**
- **Decouple collection from SessionEnd.** Make `collect` an **idempotent periodic sweep** (SessionStart + daily CI), re-scanning transcripts; per-session output files are keyed by `session_id` and overwritten, so a **never-ended / crashed** session is still captured on the next sweep and converges. SessionEnd stays only as an optional "publish promptly" nudge. (This also kills the SessionEnd race that bit ben/095.)
- **Time-sliced attribution.** The **task skill** writes a **per-session, committed activation log** (`{session_id, task_id, event, ts}` on activate/deactivate). `collect` attributes **each transcript message's tokens to the task active at that message's timestamp** (most-recently-activated = owner). Messages with no active task → an honest **`unattributed`/overhead** bucket (never smeared into tasks). Existing `dedup_key: message.id` runs first.
  - Multiple sessions on one task → **summed** (correct).
  - One session spanning multiple tasks → **time-sliced** (each message counted once — no double count).
- **Parallel sessions** are isolated by `session_id` (own transcript, own active-task state, own **per-session** activation log → no write contention). Aggregate sums per task. `publish` already handles concurrent-push races (fetch+retry); the gitignore fix (ben/093) removes working-tree collisions.
- **Subagent accounting = MUST-VERIFY spike (first task of Phase 1).** Subagent work (red-team, advisors, workflows, the retrospective estimator) can dominate cost. How the installed CC logs subagent tokens (inline vs separate sidechain files) decides whether `collect` already counts them. Conceptually they attribute to the parent's active task; verify the transcript format before trusting per-task numbers.
- **Lightweight by design.** No per-turn hooks (the capture-nag hooks were removed for exactly this reason — task skill, ben/100). Live path = **one appended ledger line on the rare activate/deactivate event**. Heavy work is out-of-band: **incremental** transcript parse (per-session byte/message offset; skip unchanged by mtime/size), on-demand estimation, daily CI aggregation. Best-effort + detached (`nohup … &`), never blocks a turn.

### B. Estimation of the by-hand baseline — inline, ranged, no approval

- **Inline in the main thread, NOT a hot-path subagent.** The thread that did the work already holds the context (diff, what was hard); a subagent would cold-load it all again, doubling cost — and "todos can be many." So estimates are produced **inline as part of the task-doc update/checkpoint flow**, the same pattern as strategy/lessons capture.
- **The task skill owns a versioned estimation rubric** (the guide); the main thread fills an `economics:` block. Skill = guide, main thread = estimator.
- **Per-todo, ranged person-hours, persona-tagged.** Estimate at **todo** granularity (bounded, accurate), roll up todo → task → program. Each estimate is a **min–max range** + **confidence** + one-line **basis** + **method_version**.
- **No human approval gate** (too much burden). The **range replaces review** (uncertainty is explicit); anyone may edit the block later, but nothing is gated.
- **Credibility without review** rests on: the **range**, the **confidence** flag, the **Phase-0 calibration anchor** (validate ranges against ≥1 genuinely hand-done task; tune the rubric — this is how the estimator "improves over time"), **method versioning**, **red-team-the-aggregate** (Phase 6, the primary external check), and **headlining the conservative (min) end** ("at least N person-hours saved").

### C. Categorization = personas (multi-label)

- Reuse the **advisor persona set** (~11: regulatory, clinical, quality, risk, cyber, human-factors, V&V, post-market, R&D, systems, PM). Bounded (not hundreds), meaningful, improvable.
- **Multi-label with an effort split** — a todo can be e.g. `regulatory-affairs + quality-engineering`. Persona is **also the costing dimension** (a by-hand DHF section = RA-hours + QA-hours + clinical-hours), which is both more credible and how a real MedTech team staffs the work.

### D. Person-hours in the data; dollars in the console (presentation)

- Repo stores **quantities**; the console converts to money.
  - Task doc `economics:` → **person-hours (min–max), persona-tagged** + confidence + basis + method_version. **No `$`.**
  - usage-metrics actuals → **tokens + wall-clock** per task (measured).
  - **project console** → person-hours × loaded rate → manual $; tokens × rate → agentic $; ROI. The **labor-rate table lives in console config, marked `[VERIFY]` assumption** — swappable per audience, never committed into the estimate data.
- **Primary metric = person-hours** (manual estimate vs agentic wall-clock + tokens); **$ is an optional console overlay.**

### E. Retrospective dataset (existing task docs)

- The skill can **build a retrospective dataset on demand**: estimate by-hand person-hours (ranged, persona-tagged) for the ~95 existing task docs that have **no token attribution**.
- **Use actuals when present; estimate when not.** Each task's value record carries a **`basis: measured | retrospective`** marker. `measured` = token attribution + inline `economics`. `retrospective` = **hours-only** estimate from the task doc + git history (no/partial tokens for old tasks — do **not** imply token precision we don't have).
- This is the **one place a subagent / `claude -p` batch is justified** — the context is NOT in-window for old tasks, so the cold-load is accepted as an **on-demand, off-hot-path** job (probably run on headline tasks first, not all 95).
- The headline must **separate measured vs retrospective** so the claim stays honest.

### F. JSON generation capability

- A skill action **generates the value dataset** (the schema the console Value view consumes) from (actuals + inline `economics`) and/or (retrospective estimates). One generator, two input modes. Schema bumps to `usage-metrics/team/v2` (adds per-task value block + measured/retrospective marker; keeps person-hours, no labor-$).

### Estimate shape (per todo, inline, no approval)

```yaml
economics:
  - todo: "Harden resolve_files against bad globs"
    personas: [rd-lead]
    manual_hours: { min: 2, max: 5 }     # specialist person-hours, ranged
    confidence: high                      # low | med | high
    basis: "one diagnostic + a guarded try/except + a test"
    method_version: 1
```
Rolls up to a task min–max and a program min–max. Console applies labor rates for the optional $ view.

## Phase 0 Findings — External Effort References (captured 2026-06-30)

_Gathered by a research subagent. The estimator rubric cites these; everything carries a confidence tag so a reviewer can see published-norm vs vendor-framed vs pure-judgment. **Headline finding: most MedTech specialist deliverables have NO published by-hand hour norm** → the estimator leans on (a) the per-page authoring rate and (b) explicitly-labeled model judgment, never an invented citation._

**Well-sourced anchors (use these first):**
- **Technical/regulated doc authoring: 3–7 hr/page** (top of range for regulated/high-rigor) — [TechScribe](https://www.techscribe.co.uk/techw/documentation-project-metrics.htm). _The single most reusable anchor — scale by deliverable page count._
- **Software: 325–750 LOC/developer-month** (~20–25 LOC/day; bias to the **low** end for IEC 62304 Class B/C firmware where review/traceability/V&V dominate) — Capers Jones / McConnell / Brooks via [NDepend](https://blog.ndepend.com/mythical-man-month-10-lines-per-developer-day/). _Use **net delivered** LOC; treat scripts/CLI "skills" as small modules._
- **Requirements effort = 10–18% of total project** (Wiegers/Jones) — [Jama](https://www.jamasoftware.com/requirements-management-guide/requirements-gathering-and-management-processes/how-long-do-requirements-take/). _Ratio anchor — needs a total-effort base._
- **PM overhead = 7–15% of project** (larger programs → lower %) — [PMI](https://www.pmi.org/learning/library/project-management-much-enough-appropriate-5072). _Ratio anchor._

**Thin / vendor-framed (directional only):** 510(k) regulatory-strategy first draft ~40–80 hr + "dozens of hours" for predicate work — [Complizen](https://www.complizen.ai/post/how-much-does-510k-cost) (an automation vendor describing what it displaces; self-interested). 510(k) consultant flat fees **$15k–50k**, day-rates **$150–500/hr** — [Medical Device Academy](https://medicaldeviceacademy.com/510k-cost/) / [MedEnvoy](https://medenvoyglobal.com/blog/how-much-do-medical-device-consultants-charge/) (real market data, but fee→hours conversion is lossy — bundles non-labor). CER €150k–1M / 8–24 months — [Emergo](https://www.emergobyul.com/resources/what-clinical-evaluation-report) (EU-MDR cost/elapsed, **not** labor hours).

**Unfindable — NO reliable external by-hand hour figure** (sources describe *what's required*, not *how long*): quality-engineering (QMS/traceability), risk-management (14971/FMEA), cybersecurity (threat model/SBOM/81001-5-1), human-factors (UEF/protocols — distinct from summative *study* cost), V&V protocols, post-market (PMS/PSUR). → For these, estimate as document deliverables via **3–7 hr/pg + an explicit specialist analysis/workshop adder**, and **label `confidence: judgment` (not externally anchored)**.

**Method guidance for the rubric:**
1. Two anchor types: **per-page rate** (document-shaped deliverables → pages × 3–7 hr) and **ratio anchors** (requirements 10–18%, PM 7–15% — apply to a summed direct-work base, never in isolation).
2. **Software** → net delivered LOC ÷ (325–750/month), low end for IEC 62304.
3. **Fees → hours** only as a sanity cross-check (÷ ~$225–325/hr blended; state it's approximate).
4. **Regulated-device work sits at the HIGH end** of any generic authoring/coding range (review cycles, traceability, audit rigor) — anchor toward the upper bound when in doubt and say so.
5. Always carry **range + confidence tag** into the data — that transparency is what makes the comparison survive a skeptic (and feeds Phase 6 red-team).

_Implication for the design: this validates "ranges + confidence + red-team-the-aggregate" as the credibility model — since ~half the personas have no external anchor, honesty about which estimates are judgment-only is non-negotiable._

## Phase 1 Spike Findings — transcript & subagent anatomy (2026-06-30)

_Done empirically against this very session (it spawned a research subagent). Two surprises that reshape the Phase 1 build._

**Transcript layout (verified):**
- Main conversation tokens: `~/.claude/projects/<slug>/<session_id>.jsonl`; `assistant` rows carry `message.usage` = `{input_tokens, output_tokens, cache_creation_input_tokens, cache_read_input_tokens, cache_creation.{ephemeral_5m,ephemeral_1h}, server_tool_use.{web_search,web_fetch}}`. `collect.py` reads this — main-thread tokens ✓.
- ⚠️ Each usage row ALSO has an `iterations[]` array that **duplicates the row's own totals** — cost math must not sum `iterations[]` on top of the row. (Separate from the `message.id` cross-row dedup.)

**Surprise 1 — subagent tokens are NOT in the main transcript → `collect.py` undercounts.**
- The transcript had **0 `isSidechain` rows** and only the **1 `Agent` tool_use** (the spawn). The subagent's tokens live in a **separate file**: `<slug>/<session_id>/subagents/agent-<agentId>.jsonl` (28 usage rows here), beside `agent-<agentId>.meta.json` = `{agentType, description, toolUseId, spawnDepth}`.
- `meta.toolUseId` links the subagent back to the exact parent `Agent` tool_use → its timestamp → the active task. `spawnDepth` (=1 here) means **nested sub-subagents are possible** (scan recursively / cap depth).
- **Impact:** today `collect.py` (only reads `<slug>/<session_id>.jsonl`) **misses 100% of subagent cost.** Red-team panels, workflows, advisors, and the future retrospective estimator are subagent-heavy — omitting them would **inflate ROI**. **Fix: `collect` also scans `<session_id>/subagents/**.jsonl`, sums their usage, attributes to the parent session** (time-slice by the spawn tool_use timestamp / session's active task at spawn).

**Surprise 2 — one conversation can span MULTIPLE session ids (compaction).**
- This single conversation = `516d9c61` (2026-06-29T17:33 → 06-30T05:40) → **compaction** → `24c349b9` (05:41 → ongoing); ~1-min gap. `CLAUDE_SESSION_ID` (the gate key) **changed across the boundary**.
- **Impact:** the session↔task↔cost join must NOT assume one id per conversation. **Design adjustment:** per-session **timestamped** activation ledgers (written under whatever `CLAUDE_SESSION_ID` is current at activation), attribution = **timestamp-within-session** (message → task active at its ts), then **sum per task across all session-ids**. One rule handles compaction (sequential ids, summed) AND parallel sessions (isolated by id).

**Net Phase 1 adjustments:**
1. `collect` scans main + `<sid>/subagents/**.jsonl` (recursive for `spawnDepth>1`); attribute subagent tokens to the parent session via `meta.toolUseId` → parent tool_use timestamp.
2. Attribution is timestamp-within-session; sum per task across session-ids (compaction-safe); never assume one id per conversation.
3. Cost math ignores `iterations[]` (intra-row dup); keep `message.id` dedup.

## Open Questions

- **Subagent token accounting** — inline vs sidechain in the installed CC? (Phase 1 spike; blocks trustworthy per-task cost.)
- **Persona loaded-rate table** — values + source; lives in console config as `[VERIFY]`.
- **Agentic "time" denominator** — default = summed active **session** time; show calendar task-span separately as context.
- ~~Calibration anchor~~ — **RESOLVED (2026-06-30):** no internal hand-done task exists. Replaced with **external effort-reference research** (Phase 0, a research subagent) so estimates cite published/industry by-hand norms; model-judgment fallback (flagged lower-confidence) where references are thin.
- ~~Agentic "time" denominator~~ — **RESOLVED (2026-06-30):** summed active **session** time (primary); calendar task-span shown as context.
- **Retrospective presentation** — how to show hours-only retrospective tasks beside measured tasks without implying token precision.

## Phased Plan

- **Phase 0 — External effort references** (no internal hand-done anchor exists). A **research subagent** (own context — keeps the main thread lean) gathers published/industry references for by-hand specialist **person-hours per persona / artifact-type**, with citations + an honest inventory of gaps. These ground the estimator rubric so estimates cite external norms rather than pure model priors; where references are thin the rubric falls back to model judgment (flagged lower-confidence). Findings captured into this doc.
- **Phase 1 — Attribution backbone.** Task-skill **per-session activation log** (timestamped, committed) + **time-sliced, incremental `collect`** decoupled from SessionEnd → per-task tokens + `unattributed`. **First: the subagent-accounting spike.** Delivers real per-task cost with zero estimation — verifiable on its own.
- **Phase 2 — Persona taxonomy + (console-side) rate config.** Define the persona category set (reuse advisors) + a labor-rate table in console config (`[VERIFY]`).
- **Phase 3 — Inline ranged estimates.** Versioned estimation **rubric in the task skill** + inline `economics:` capture in the existing update/checkpoint flow. **No approval.**
- **Phase 3b — Retrospective estimator + dataset builder.** On-demand batch/subagent over existing task docs → **hours-only** retrospective dataset; `basis: retrospective`.
- **Phase 4 — Value aggregation + JSON generation.** Aggregate joins actuals + estimates → per-task & program ROI (person-hours saved, time-compression; tokens/wall-clock), **schema v2**, measured/retrospective marked, **no labor-$ in repo**.
- **Phase 5 — Console Value/ROI view.** Program rollup + per-task drill-down (people anonymized), min–max bands (conservative ↔ optimistic), the **$ overlay** (labor-rate config), measured/retrospective split, an "how we estimated" expander.
- **Phase 6 — Red-team the aggregate.** Run CFO/PMO/CEO skeptics over the rolled-up ROI narrative before it goes external; fix what they shred.

## Todos

- [x] **Phase 1 spike:** confirmed empirically — subagent tokens live in `<sid>/subagents/agent-<id>.jsonl` (NOT the main transcript; `collect` misses them today); one conversation can span multiple session-ids (compaction). See "Phase 1 Spike Findings" above.
- [x] Phase 1: task-skill per-session activation log — `task-activate.sh` appends `{ts,session_id,task_id,event}` to `tasks/<tf>/_usage-metrics/activations/<sid>.jsonl` on add/remove (best-effort, one-line, gitignored→rides publish). Verified.
- [x] Phase 1: time-sliced `collect` + subagent scan + `by_task` — `collect.py` reads the ledger → `task_at(ts)`, scans `<sid>/subagents/**.jsonl`, attributes each message to the active task, emits `by_task` + `_unattributed`. **Found+fixed a latent dedup bug** (see lessons). Validated: subagent 21→6,999 tokens, synthetic A→B→A slicing, real run (8 files). `collect` already runs at SessionStart (TTL-gated refresh hook) so it's not SessionEnd-only.
- [ ] Phase 1 (remaining, optimizations — not correctness): always-collect at SessionStart (close the never-ended-session gap) + incremental transcript parse (offset/mtime skip) so always-collect stays cheap.
- [x] Phase 0: research subagent → external by-hand effort references per persona (cited, with gaps); captured above as the estimator's reference basis
- [x] Phase 2: persona taxonomy = the **11 advisor personas** (canonical source `.claude/skills/advisors/agents/`; not redeclared). Console-side labor-rate config added to `console.yaml` `value.labor_rates` (12 entries incl `default`, all `[VERIFY]` fully-loaded USD/hr) + `config.py` accessors (`labor_rates`, `labor_rate_for`, `value_currency`). Verified all personas covered + default fallback.
- [x] Phase 3: estimation **rubric** authored at `.claude/skills/usage-metrics/references/effort-estimation-rubric.md` (method v1; embeds the Phase 0 anchor table + confidence-tag + `economics` schema + the ranged/persona/no-approval/headline-conservative rules). Task-skill `checkpoint` action gains step 3b: record/refresh `## Economics` inline per the rubric. **Dogfooded** on ben/096 (7 todos → 33–71 by-hand person-hours); YAML validated (parses, personas∈advisors, min≤max). _(Rubric lives in usage-metrics for domain ownership; the task-skill checkpoint references it — slight deviation from "rubric in the task skill", but capture is still task-flow-driven as the user wanted.)_
- [x] Phase 3b: retrospective dataset — wrote `## Economics` (one-todo, `retrospective: true`, ranged person-hours + `agentic_hours` + personas) into **all 95 existing task docs** (ben/001–095 + dmytro/001), in chunks of 10, re-aggregating per chunk so the dashboard filled in live. Program rollup: **~800–2,753 person-hours saved** (by-hand 1,280–3,233 vs agentic ~480). Estimates marked `retrospective` (rough; `confidence: low`); the view shows a `retro` badge.
- [x] Phase 4 (cost rollup + estimate join DONE): `aggregate.py` rolls `by_task` → per-task **cost actuals** AND parses `## Economics` JSON → per-task **by-hand person-hour estimates**, joined in `usage.json` v2 (`tasks` block + top-level `value_summary`). Person-hours in data; **no `$`** (console applies `labor_rates`). Stdlib-only (CI-safe). Verified: `ben/096` = $10.88 measured + 33–71 person-hours estimated (by_persona split). Remaining Phase 4: markdown/HTML task section (cosmetic).
- [x] Phase 5: project-console **Value/ROI view** — `/value` route (metrics router) + `value_view.html` + `value.js` + nav link/icon. Renders per-task agentic-$ (measured) vs by-hand person-hours (estimate, min–max bands) + by-hand-$ (via console `labor_rates`) + leverage; program hero cards headline the conservative `min`; people anonymized (Member N · NNN); measured/estimate badges + `[VERIFY]`-rate disclaimer. Verified: `/value` 200, embeds v2 data + rates, no `/metrics` regression. (Retrospective measured/estimate split is Phase 3b.)
- [ ] Phase 6: red-team the aggregate ROI narrative; fix findings

## Resume

**Activation command:** `bash .claude/hooks/task-activate.sh add <SESSION_ID> 096`

**Status:** Phase 0 done (external references). **Phase 1 attribution backbone built + validated** (activation ledger in `task-activate.sh`; `collect.py` does subagent scan + last-wins dedup + time-sliced `by_task`). **Uncommitted** — edits to `.claude/skills/task/hooks/task-activate.sh` (+ installed copy `.claude/hooks/task-activate.sh`) and `.claude/skills/usage-metrics/scripts/collect.py`; plus this doc. **Phases 0,1,2,3,4 (cost+estimate join) DONE.** `usage.json` v2 now carries, per task, measured token cost + by-hand person-hour estimate (+ `value_summary`); `ben/096` = $10.88 + 33–71h. Economics block is **JSON** (stdlib/CI-parseable). **First action on resume:** Phase 5 — the project-console **Value/ROI view** consuming `usage.json` v2 `tasks`+`value_summary`, applying `config.labor_rates` for the $ overlay (manual $ vs agentic $, person-hours-saved headline at the `min`, min–max bands, measured/estimate badges, people anonymized). Then Phase 3b (retrospective dataset for the ~95 existing task docs) + Phase 6 (red-team the aggregate ROI). Phase 1 optimizations + ben/093 untrack-usage-JSONs cleanup still open, non-blocking. Phase 1 optimizations (always-collect-at-start + incremental parse) + the ben/093 untrack-usage-JSONs cleanup can come anytime; not blocking. **Uncommitted now:** `aggregate.py` + regenerated `tools/usage-metrics/usage.json` + re-modified (tracked) `_usage-metrics/*.json`.

**Touches 3 skills:** `task` (activation log + estimation rubric + `economics:` block), `usage-metrics` (time-sliced incremental collect, value aggregation + JSON gen, retrospective builder; schema v2), `project-console` (Value/ROI view). Reuses `advisors` persona set + `red-team` for Phase 6.

## Economics

_By-hand person-hour estimates for the work completed under this task, per
`.claude/skills/usage-metrics/references/effort-estimation-rubric.md` (method v1).
Ranged + persona-tagged; the agentic side (tokens/wall-clock) is measured separately.
First dogfood of the rubric — recorded inline by the thread that did the work._

```json
{
  "economics": {
    "method_version": 1,
    "agentic_hours": 9,
    "todos": [
      {
        "todo": "Design: value model across 3 skills (attribution, estimation, schema)",
        "personas": ["systems-engineering", "rd-lead"],
        "manual_hours": {"min": 8, "max": 16},
        "confidence": "low",
        "basis": "judgment — senior SW/systems design across attribution + estimation methodology + schema; no external norm"
      },
      {
        "todo": "Phase 0: external effort-reference research + cited synthesis",
        "personas": ["program-manager"],
        "manual_hours": {"min": 6, "max": 14},
        "confidence": "low",
        "basis": "judgment — multi-domain web research + cited table (~0.5-1.5 person-days); no research-throughput norm"
      },
      {
        "todo": "Phase 1 spike: reverse-engineer transcript/subagent token format",
        "personas": ["rd-lead"],
        "manual_hours": {"min": 3, "max": 6},
        "confidence": "med",
        "basis": "software/judgment — reverse-engineering JSONL format + verifying token accounting"
      },
      {
        "todo": "Phase 1: activation ledger in task-activate.sh",
        "personas": ["rd-lead"],
        "manual_hours": {"min": 2, "max": 4},
        "confidence": "high",
        "basis": "software LOC-norm (low end) — small bash function + ledger schema + verification"
      },
      {
        "todo": "Phase 1: subagent-aware time-sliced collect.py + last-wins dedup bug fix",
        "personas": ["rd-lead"],
        "manual_hours": {"min": 8, "max": 18},
        "confidence": "med",
        "basis": "software — ~150 net LOC + a subtle progressive-usage dedup-bug diagnosis + multi-scenario validation; LOC-norm low end + debugging adder"
      },
      {
        "todo": "Phase 2: persona taxonomy + console labor-rate config + config accessors",
        "personas": ["rd-lead", "program-manager"],
        "manual_hours": {"min": 2, "max": 5},
        "confidence": "high",
        "basis": "software — small config block + 3 accessors + test; rates are judgment placeholders"
      },
      {
        "todo": "Phase 4a: aggregate.py per-task cost rollup + usage.json v2 schema",
        "personas": ["rd-lead"],
        "manual_hours": {"min": 4, "max": 8},
        "confidence": "med",
        "basis": "software — collect_records extension + tasks-block emit + schema design + validation"
      }
    ]
  }
}
```

_Roll-up so far: **~33–71 by-hand person-hours** (mostly rd-lead, with systems-engineering
+ program-manager). Headline conservatively at the **33h** floor. Agentic side: this landed
in ~1 day of session work — the comparison fills in once Phase 4b joins these to the measured
tokens/wall-clock._

## Lessons Learned

<!-- LESSONS LEARNED: tooling, token-accounting -->
**Claude Code logs token usage differently on main vs subagent transcripts — `collect` must dedup by message.id keeping the LAST (not first) record.** Each message is logged ~2–5×. On the MAIN transcript every copy carries the same complete usage (`first==last==max`), so the old first-wins dedup was fine there. But SUBAGENT transcripts (`<slug>/<sid>/subagents/agent-*.jsonl`) stream **progressive** usage — the first row is a near-empty start, the final row holds the totals. Measured on one research subagent: first-wins = **21** output tokens, last-wins = **6,999**. First-wins silently dropped ~99% of streamed subagent cost.
**Why it matters:** subagent-heavy work (red-team panels, workflows, advisors, the planned retrospective estimator) would have been undercounted → inflated ROI — the exact thing a skeptic attacks. **How to apply:** when summing CC transcript usage, dedup `message.id` with **last/max-wins**; and remember subagent tokens live in a separate `subagents/` tree, not the main transcript (scan both). Verified last-wins leaves main totals unchanged.

## Changelog

- 2026-06-30: **Task-doc resume-sufficiency for the estimate (task↔usage-metrics coupling optimization).** Context analysis first: the project-specific standing load is ~46k tok (skill descriptions ~19.6k, auto-loaded rules ~17k, agents ~6k, CLAUDE.md ~3.7k); a task doc adds only ~1–2k, and the rubric (~1.5k) is **already lazy-loaded on demand at checkpoint** (zero standing cost) — so the coupling was never a context problem. The real gap was **resume correctness**: the "read the rubric to build `## Economics`" instruction lived only in the task checkpoint action (step 3b), invisible to a session resuming from the task doc alone. Fix (pointer, never copy): (1) task skill v29→**v30** — embedded PERMANENT RULES block gains rule 6 naming the rubric path as the `## Economics` source; checkpoint 3b now also stamps `method_ref`. (2) usage-metrics v7→**v8** — economics schema gains optional `method_ref` (self-describing block); `parse_task_economics` tolerates it (unknown keys ignored — validated, no parser change). Template-forward (new docs get it; not mass-backfilling the 95 existing). Validated: rubric JSON still parses, aggregate.py compiles. **Uncommitted.**
- 2026-06-30: **Estimation-rubric anchor set expanded from research + methodology now in the console.** (per user) (1) Added a **live methodology section** to the Value tab: `metrics/router.py` reads `.claude/skills/usage-metrics/references/effort-estimation-rubric.md` per-request and renders markdown→HTML (`markdown` lib) into a collapsible section at the bottom of the tab — editing the rubric (or a `/sync-skills pull`) updates the console with no duplication. (2) Category cards: header % changed from savings-share to **% of tasks** (task-type distribution); savings % split into a distinct amber `.vv-catpct` span (was blurring with the green range); whole-number rounding (`hrs0`/`usd0`). (3) Added mtime-based **cache-busting** (`?v=<mtime>`) to metrics.js/value.js — the range filter already drove the table; the browser was serving a stale value.js. (4) **Four parallel research agents** gathered published by-hand effort norms for the "no-anchor" work types; folded results into the rubric Anchors table (test engineering ×1.3–3 Class C via DO-178C; defect ~4–6 h/defect, never cite contested "100×"; code review 150–400 LOC/hr Cisco/Wiegers/Fagan; doc review 8–12 pg/hr ord / 1–3 pg/hr regulated Gilb&Graham; audit IAF MD 5 auditor-days; pentest CREST tester-days) + **judgment-tier** rows (RCA/CAPA, document red-teaming — no external norm, proxy given). Full summaries + source links → new `## Effort-Estimation Research Basis` in the skill README. usage-metrics v6→v7. Verified: all 8 anchor rows + methodology render live at `/metrics`. **Uncommitted.**
- 2026-06-30: **UI fixes + Phase 3b retrospective (95 tasks).** (UI, per feedback) each Value row now shows a 3–5 word task summary (from the doc H1, emitted as `title` by aggregate) under the Member·NNN label, the Category cell wraps, and the table is wrapped in an overflow-x container so columns stay in the panel; merged via PR #82. (Phase 3b) wrote retrospective `## Economics` blocks into **all 95 existing task docs** in chunks of 10, re-aggregating per chunk (dashboard filled in live). Program rollup now **~800–2,753 person-hours saved** (by-hand 1,280–3,233 vs agentic ~480) across 95 tasks. Retrospective estimates marked `retrospective: true` / `confidence: low` (rough, from task summaries); view shows a `retro` badge. **Uncommitted:** 94 task docs + usage.json (the retrospective dataset).
- 2026-06-30: **Value tab reframed around HOURS SAVED + category; fixed the $0-token-cost bug** (per user feedback that leverage/$/confidence didn't read as savings, and "why no token cost?"). (1) Added `agentic_hours` to the economics schema (your estimate of how long the task actually took) → aggregate emits per-task `hours_saved` = by-hand `manual_hours` − `agentic_hours` + `personas` (category); `value_summary` headlines hours saved. (2) `value.js` + the Value tab rewritten: hero = **person-hours saved** (24–62 for ben/096) + by-hand (33–71) + agentic time (9h) + agentic $ (tokens); table columns = Task · **Category** · Agentic (hrs) · By-hand (hrs) · **Hours saved** · Agentic $ · Confidence (single readable tier). Dropped the confusing $/leverage framing. (3) **Root-caused the $0 token cost:** CI was aggregating STALE committed session JSONs that predate the Phase-1 `by_task` attribution (so per-task cost = $0); re-collected fresh `by_task` JSONs → real cost ($53.10 for ben/096) and committed them so CI stops producing $0. usage-metrics v5→v6, project-console v1.30.1→v1.30.2. Verified live: Value tab shows real cost + hours saved + category.
- 2026-06-30: **Phase 5 refinement — Value/ROI moved into a Metrics sub-tab** (per user). The `/metrics` page now has a two-tab switcher (**Token Metrics** / **Value & ROI**) — both rendered on one page (`metrics.js` + `value.js`); removed the standalone `/value` route + `value_view.html` + separate nav item; `/metrics` route now also passes `labor_rates` + `currency`; `value.js` reused unchanged. project-console v1.30.0→1.30.1. Verified live: `/metrics` 200 with both tabs + both scripts, `/value` 404, no stray nav link.
- 2026-06-30: **Phase 5 done + smoke-tested** (uncommitted; project-console skill). Added the **Value/ROI view**: `/value` route in `metrics/router.py` (passes `usage_json` + console `labor_rates` + `currency`), `web/templates/value_view.html` (scoped `vv-` styles, hero cards + per-task table + `[VERIFY]` disclaimer, empty-state when no data), `web/static/value.js` (anonymizes task_folder→Member N, computes by-hand-$ = by_persona hours × `labor_rates`, leverage = conservative by-hand-$ ÷ measured agentic-$, headlines the `min`), and a `#ic-value` nav link before Metrics (gated on `metrics_nav`). Smoke-test: `/value` HTTP 200, embeds `usage-metrics/team/v2` + `LABOR_RATES`, loads `value.js`, nav present, `/metrics` unaffected. Worked example (ben/096): ~$5.4k–$11.6k by-hand vs ~$35 agentic ≈ ~150× — eye-popping, which is exactly why Phase 6 red-team + ranges + `[VERIFY]` rates matter. Regenerated telemetry restored (not committed; CI/publish refreshes). **The value story is now visible end-to-end in the console.** Next: Phase 3b (retrospective for ~95 old tasks) + Phase 6 (red-team the aggregate).
- 2026-06-30: **Phase 4b done + validated** (uncommitted; `usage-metrics/aggregate.py`). `parse_task_economics()` extracts the `## Economics` **JSON** block from each task doc (switched the schema YAML→JSON so the stdlib-only CI aggregator can parse it — no PyYAML), rolls up per-task by-hand person-hours (min/max) + an even-split `by_persona` breakdown + confidence_mix; `main` joins it onto the per-task cost in `usage.json` `tasks` and adds a top-level `value_summary`. **Person-hours in data; no `$`** (console applies `labor_rates`). Validated with system python3 (CI-equivalent): `ben/096` = $10.88 measured token-cost joined to 33–71 estimated by-hand person-hours (rd-lead 22–46.5h, PM 7–16.5h, systems-eng 4–8h). Both halves of the value equation now sit together in the data. Next: Phase 5 (console Value/ROI view consuming v2) + Phase 3b (retrospective) + Phase 6 (red-team the aggregate).
- 2026-06-30: **Phase 3 done + validated** (uncommitted; `usage-metrics/references/effort-estimation-rubric.md` new + `task/SKILL.md` checkpoint step 3b + ben/096 `## Economics`). Authored the inline estimation rubric (method v1: economics schema, persona list, Phase-0 anchors, ranged/persona/confidence/no-approval/headline-conservative rules); wired capture into the task `checkpoint` action; **dogfooded** by recording ben/096's own completed todos → 7 entries, **33–71 by-hand person-hours** (mostly rd-lead). YAML validated: parses, personas∈advisor set, min≤max, confidence/basis present. No approval gate; credibility = ranges + confidence + Phase-6 red-team. Rubric filed under usage-metrics (domain owner); task checkpoint references it. Phase 2 merged via PR #77. Next: Phase 4b — `aggregate.py` parses `## Economics` from task docs + joins to per-task cost → person-hours-saved/ROI (person-hours in data; $ stays console-side).
- 2026-06-30: **Phase 2 done + validated** (uncommitted; `console.yaml` project-owned + `project-console/console/config.py` skill). Persona taxonomy = the 11 advisor personas (canonical source `.claude/skills/advisors/agents/`, referenced not redeclared). Added the console-side `value.labor_rates` block (presentation-layer $ assumption — kept OUT of the committed person-hours/token data) with `[VERIFY]` fully-loaded placeholders for all 11 personas + `default`, plus `config.py` accessors `labor_rates` / `labor_rate_for(persona)` / `value_currency`. Verified all advisor personas covered and `_unattributed`/unknown fall back to `default` ($170). Phase 4a (per-task cost) merged via PR #76. Next: Phase 3 (inline ranged person-hour estimates via a task-skill rubric that embeds the Phase 0 references).
- 2026-06-30: **Phase 4 first-half built + validated** (uncommitted; `usage-metrics/aggregate.py`). `collect_records` now also accumulates per-task (`<tf>/<task_id>`); `main` emits a `tasks` block in `usage.json` with per-task cost (schema `team/v1`→`v2`, additive — the anonymized `months` member view + the console v1 consumer are unaffected; the `tasks` block is task-identified, not person-anonymized, since value is task-scoped and must join to estimates). Verified end-to-end: `ben/096` $10.88 / `ben/_unattributed` $208.39. The dominant `_unattributed` is expected — the activation ledger is brand-new, so all pre-ledger historical work is honestly unattributed; per-task fills in as tasks are activated under the ledger going forward. This is the "real per-task cost, no estimates" milestone. Next: Phase 2 (persona taxonomy + console rate config) → Phase 3 (inline ranged estimates) → Phase 4 second-half (join estimates → ROI).
- 2026-06-30: **Phase 1 attribution backbone built + validated** (uncommitted; edits to `task` + `usage-metrics` skills). (1) `task-activate.sh` now writes a per-session timestamped activation ledger (`_usage-metrics/activations/<sid>.jsonl`) on add/remove — verified it appends + is gitignored. (2) `collect.py` rewritten: reads the ledger → `task_at(ts)`, scans `<sid>/subagents/**.jsonl`, time-slices every message to the active task, emits `by_task` + `_unattributed`; **switched dedup from first-wins to last-wins** after discovering subagent transcripts stream progressive usage (first-wins captured 21 of 6,999 subagent output tokens — see Lessons). Validated: subagent delta now 6,999; synthetic A→B→A slicing correct; real `collect` wrote 8 session files with `by_task`. (3) Confirmed `collect` already runs at SessionStart (TTL-gated refresh hook) — not SessionEnd-only. Remaining Phase 1 = optimizations (always-collect-at-start + incremental parse). Next major step: Phase 4 first-half — teach `aggregate.py` to roll up `by_task` into per-task cost (actuals, no estimates yet).
- 2026-06-30: **Phase 1 subagent-accounting spike done** (empirical, against this session). Found: (1) subagent tokens live in `<slug>/<sid>/subagents/agent-<id>.jsonl` + `.meta.json` (toolUseId→parent, spawnDepth), NOT the main transcript → `collect.py` currently misses 100% of subagent cost (would inflate ROI). (2) one conversation spans multiple session-ids across compaction (`516d9c61`→`24c349b9`); the gate's `CLAUDE_SESSION_ID` changes. (3) usage rows carry a duplicate `iterations[]` to avoid in cost math. Folded the net Phase-1 build adjustments into the doc. Design pushed earlier via PR #74; spike findings captured here (uncommitted).
- 2026-06-30: **Phase 0 references captured** (research agent `a9e5c4b29fae39cc5` returned, 83k subagent tokens, 16 tool uses). Folded a cited reference table + well-sourced/thin/unfindable inventory + method guidance into the new "Phase 0 Findings" section. Key result: only doc-authoring (3–7 hr/pg), software (325–750 LOC/dev-month), requirements-ratio (10–18%), and PM-ratio (7–15%) have solid published norms; QE/risk/cyber/HF/V&V/post-market have **no** external hour figure → estimator uses per-page + specialist adder, labeled `confidence: judgment`. Validates the ranges+confidence+red-team-aggregate credibility model.
- 2026-06-30: **Phase 0 reframed + research agent launched.** No internal calibration anchor exists → grounding by-hand estimates against **external references** instead, gathered by a **research subagent** (own context, keeps main thread lean). Agentic-time denominator settled = summed active session time (task-span as context). Research agent (general-purpose, background) is gathering published by-hand person-hour norms per persona/artifact-type with citations + honest gaps; findings to be captured here as the estimator's reference basis. _In-flight: background research agent `a9e5c4b29fae39cc5`; transcript at `.../tasks/a9e5c4b29fae39cc5.output` (do not tail — overflow). If this session drops before it returns, re-run the Phase-0 research prompt (in this doc's Phase 0) fresh._
- 2026-06-30: Task created. Captured the full design from the planning session: time-sliced no-double-count attribution decoupled from SessionEnd; inline (not subagent) ranged person-hour estimates with no approval gate; persona-based multi-label categorization; person-hours in data / $ in console; on-demand retrospective dataset for existing task docs; JSON generation capability; 7-phase plan (0–6) with the subagent-accounting spike first. Design grounded in reads of `collect.py`/`aggregate.py`/`publish.py`/`setup.py` + the console metrics loader/router.
