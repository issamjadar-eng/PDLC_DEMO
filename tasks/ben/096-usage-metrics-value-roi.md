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

- [ ] **Phase 1 spike:** run a subagent-heavy session; inspect the transcript; confirm where subagent tokens land (inline vs sidechain) and whether `collect` counts them
- [ ] Phase 1: task-skill per-session activation log (timestamped, committed, concurrency-safe)
- [ ] Phase 1: time-sliced + incremental `collect`, decoupled from SessionEnd (idempotent sweep); `unattributed` bucket
- [x] Phase 0: research subagent → external by-hand effort references per persona (cited, with gaps); captured above as the estimator's reference basis
- [ ] Phase 2: persona taxonomy (reuse advisors) + console-side labor-rate config (`[VERIFY]`)
- [ ] Phase 3: estimation rubric in the task skill + inline `economics:` capture in update/checkpoint flow (no approval) — **the rubric file embeds/cites the Phase 0 external references** (anchor table + confidence-tag convention) as its grounding, so estimates point at published norms (or are labeled `judgment`) by construction
- [ ] Phase 3b: retrospective estimator + dataset builder (on-demand; hours-only; `basis: retrospective`)
- [ ] Phase 4: value aggregation + JSON generator → schema `team/v2` (measured + retrospective; person-hours; no labor-$)
- [ ] Phase 5: project-console Value/ROI view ($ overlay, min–max bands, anonymized, measured/retrospective split)
- [ ] Phase 6: red-team the aggregate ROI narrative; fix findings

## Resume

**Activation command:** `bash .claude/hooks/task-activate.sh add <SESSION_ID> 096`

**Status:** design captured + Phase 0 external-effort references captured (research agent done, folded in above). Nothing built yet. **First action on resume:** the Phase 1 subagent-accounting spike (everything on the cost side depends on its answer), then the activation log + time-sliced collect.

**Touches 3 skills:** `task` (activation log + estimation rubric + `economics:` block), `usage-metrics` (time-sliced incremental collect, value aggregation + JSON gen, retrospective builder; schema v2), `project-console` (Value/ROI view). Reuses `advisors` persona set + `red-team` for Phase 6.

## Changelog

- 2026-06-30: **Phase 0 references captured** (research agent `a9e5c4b29fae39cc5` returned, 83k subagent tokens, 16 tool uses). Folded a cited reference table + well-sourced/thin/unfindable inventory + method guidance into the new "Phase 0 Findings" section. Key result: only doc-authoring (3–7 hr/pg), software (325–750 LOC/dev-month), requirements-ratio (10–18%), and PM-ratio (7–15%) have solid published norms; QE/risk/cyber/HF/V&V/post-market have **no** external hour figure → estimator uses per-page + specialist adder, labeled `confidence: judgment`. Validates the ranges+confidence+red-team-aggregate credibility model.
- 2026-06-30: **Phase 0 reframed + research agent launched.** No internal calibration anchor exists → grounding by-hand estimates against **external references** instead, gathered by a **research subagent** (own context, keeps main thread lean). Agentic-time denominator settled = summed active session time (task-span as context). Research agent (general-purpose, background) is gathering published by-hand person-hour norms per persona/artifact-type with citations + honest gaps; findings to be captured here as the estimator's reference basis. _In-flight: background research agent `a9e5c4b29fae39cc5`; transcript at `.../tasks/a9e5c4b29fae39cc5.output` (do not tail — overflow). If this session drops before it returns, re-run the Phase-0 research prompt (in this doc's Phase 0) fresh._
- 2026-06-30: Task created. Captured the full design from the planning session: time-sliced no-double-count attribution decoupled from SessionEnd; inline (not subagent) ranged person-hour estimates with no approval gate; persona-based multi-label categorization; person-hours in data / $ in console; on-demand retrospective dataset for existing task docs; JSON generation capability; 7-phase plan (0–6) with the subagent-accounting spike first. Design grounded in reads of `collect.py`/`aggregate.py`/`publish.py`/`setup.py` + the console metrics loader/router.
