# 109 — Commercial Advisor Persona

**ID**: 109
**Created**: 2026-07-22
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
2. **Phase-end batching is OK; drift-batching is not.** Planned phases (e.g., "finish Phase 2, then log the whole phase at once") are a legitimate checkpoint — writing once per phase is fine if the phase is bounded and the write happens **at the phase boundary, before the next phase starts**. What's not OK: accumulating updates in your head across arbitrary work, waiting for "end of the session," "after the push," or the user to ask. By then a crash or context-trim has lost the state. Rule of thumb: if you can't name the specific upcoming checkpoint where you'll write the update, write it now.
3. **A commit is not a substitute.** Git history records code; this doc records the project narrative — what was done, why, what's left, what surprised us.
4. **Resume-ready before any session boundary.** Before recommending a fresh session, marking Complete, or ending work, the doc must already contain: (a) what was completed this session with concrete artifacts, (b) status of any in-flight work and temp artifacts, (c) priority-ordered next steps with file paths, (d) open questions blocking progress, (e) the exact `/task` activation command to resume.
5. **Capture strategy + lessons as they happen.** If the session produces option comparisons, scope/boundary decisions, architectural pivots, non-obvious insights, or corrected assumptions, write them into the appropriate section **in-flight** — not just in chat. Harvesting skills can only surface what was written.
6. **Estimation provenance (if `## Economics` is present).** This doc's `## Economics` block is the by-hand person-hour estimate, built per the effort-estimation rubric at `.claude/skills/usage-metrics/references/effort-estimation-rubric.md` (owned by the `usage-metrics` skill). To **add or refresh** an estimate on resume — even without loading the task skill — read that rubric first for the anchors, personas, and JSON schema; the block also carries a `method_ref` naming it. Skip silently if `usage-metrics` isn't installed. Point to the rubric, never copy it into this doc.

Success test for this doc: a fresh Claude session, given only this file, can re-enter the work without asking the user "what were we doing?"

## Goals

Close the commercial persona gap in the advisors bundle. The project has a full commercial stack (commercial skill + BQ reports, corpus data tier, `docs/project/strategies/commercial-strategy.md`, market-research + competitive-landscape input analysis) but no advisor persona grounds on any of it — `commercial-strategy.md` is referenced nowhere in the dhf-manifest canonical-roles catalog.

- Add a `commercial` advisor persona to the advisors skill bundle (canonical-role mode, per advisors SKILL.md authoring procedure)
- Extend `dhf-manifest/data/canonical-roles.yaml` with the missing `commercial_strategy` role (+ a role for the commercial reports/data tier if the catalog conventions support it) and add `commercial` to the consumers of market_research / competitive_landscape
- Side fix while in the catalog: `risk-strategy.md` also has no canonical role — add `risk_strategy` so the existing risk-management advisor can ground on it
- Install: symlink into `.claude/agents/`, project.yml enabled + overlay stub, regenerate discovery index, render grounding block

## Todos

- [x] Read contracts: `agents/regulatory-affairs.md` (worked example), `canonical-roles.yaml` header/schema, dhf-manifest SKILL.md (discovery-index regeneration)
- [x] Extend `canonical-roles.yaml`: `commercial_strategy` role, `risk_strategy` role, `commercial_analysis` multi-file role (`docs/project/commercial/reports`, `**/report.md`), `commercial` added to market_research / competitive_landscape / kol_feedback consumers + header roster
- [x] Author `.claude/skills/advisors/agents/commercial.md` (canonical-role mode; tier_1 = commercial_strategy + regulatory_strategy; tier_2 = market_research, competitive_landscape, commercial_analysis, kol_feedback, predicate_analysis, postmarket_strategy)
- [x] Install: symlink `.claude/agents/commercial.md`, project.yml (enabled + overlay stub + approved_agents allowlist)
- [x] Regenerate the discovery index — all 3 new roles resolve (commercial_analysis: 32 report.md files)
- [x] Run `render-grounding.py --agent commercial` — GROUNDING block rendered; loader smoke-test loads `Commercial Assistant` (solo, core-team); advisors tests 88 passed; dhf-manifest discovery-index tests 48 passed
- [x] Version bookkeeping: advisors v11→v12 (+README changelog row), dhf-manifest v13→v15 (v14 note had shipped without a frontmatter bump — documented in the v15 note)
- [ ] Push to main (commit → PR → auto-merge) when user says push; consider `/sync-skills push` for advisors + dhf-manifest registry changes
- [x] Update task doc + index; remind user new subagents need a session restart

<!-- STRATEGY CONTENT: operations, advisor roster -->
**Decision — commercial advisor added to the persona bundle (2026-07-22).** The project had a full commercial stack (commercial skill BQ editions, corpus data tier, `commercial-strategy.md`, market-research/competitive-landscape input analysis) with no advisor grounding on any of it; `commercial-strategy.md` was referenced nowhere in the canonical-roles catalog. Tier 1 deliberately deviates from the default (`architecture_strategy` + system SAD) to `commercial_strategy` + `regulatory_strategy` — commercial questions gate on filing pathway/timing, not system architecture. Catalog gaps were closed by extending `canonical-roles.yaml` (per advisors SKILL.md L43 — never papered over with literal globs). Deferred candidates, revisit if demo scope grows: manufacturing/design-transfer persona (hardware device, no owner for production readiness); reimbursement/health-economics folded into commercial rather than split out.
<!-- /STRATEGY CONTENT -->

<!-- LESSONS LEARNED: process -->
**Strategy-domain ↔ canonical-role drift.** `project.yml strategy_domains[]` had 8 domains with strategy docs on disk, but the canonical-roles catalog only carried roles for 5 of them — `commercial-strategy.md` and `risk-strategy.md` had no role at all (testing-strategy was covered only as a `verification_plan` pattern). Consequence: existing advisors (risk-management) silently never grounded on their own domain's strategy doc. Rule of thumb: when a strategy domain is added to `project.yml` (or a strategy doc lands in `docs/project/strategies/`), add the matching `<domain>_strategy` canonical role in dhf-manifest's catalog in the same change — the discovery index only serves what the catalog names.
<!-- /LESSONS LEARNED -->

## Resume

- **In-flight artifacts (all uncommitted, on `main` working tree):** `.claude/skills/advisors/agents/commercial.md` (new), `.claude/agents/commercial.md` (new symlink), `.claude/skills/advisors/{SKILL.md,README.md}` (v12), `.claude/skills/dhf-manifest/SKILL.md` (v15) + `data/canonical-roles.yaml` (3 new roles, consumer edits), `project.yml` (enabled/overlay/approved_agents), `docs/project/dhf-manifest/pdlc-demo-dhf-discovery.json` (regenerated). Nothing committed by Claude. Pre-existing unrelated dirty files from task 108 also present in the working tree — do not sweep them into a commit for this task.
- **First action on resume:** if user wants it landed, commit only the files listed above → PR → auto-merge per git-workflow rule; then optionally `/sync-skills push` for the two registry skills. New subagent requires a fresh Claude Code session to be invocable; console shows the Commercial Assistant after restart.
- Activation: `bash .claude/hooks/task-activate.sh add <SESSION_ID> 109`

## Economics

_By-hand person-hour estimate, **filled at checkpoint** per the effort-estimation rubric (`usage-metrics` skill). Empty until the first completed todo is estimated; an empty `todos` list is ignored by the aggregator._

```json
{
  "economics": {
    "method_version": 1,
    "method_ref": ".claude/skills/usage-metrics/references/effort-estimation-rubric.md",
    "agentic_hours": {"min": 0.3, "max": 0.6},
    "todos": [
      {
        "todo": "Gap analysis: advisor roster vs project footprint (commercial stack, catalog cross-check)",
        "personas": ["program-manager"],
        "manual_hours": {"min": 1, "max": 2},
        "confidence": "medium",
        "basis": "model judgment — cross-referencing 3 config surfaces (agents, catalog, strategy domains) by hand"
      },
      {
        "todo": "Extend canonical-roles catalog (3 roles + consumer edits) + version notes",
        "personas": ["rd-lead"],
        "manual_hours": {"min": 1, "max": 2},
        "confidence": "high",
        "basis": "software: small append-only data change + changelog, but requires learning the catalog schema/conventions"
      },
      {
        "todo": "Author commercial advisor persona (frontmatter tiers + body with provenance/lifecycle discipline)",
        "personas": ["rd-lead", "program-manager"],
        "manual_hours": {"min": 2, "max": 4},
        "confidence": "medium",
        "basis": "model judgment — persona authoring against a worked example + tier selection rationale"
      },
      {
        "todo": "Install + verify (symlink, project.yml wiring, discovery-index regen, grounding render, 2 test suites)",
        "personas": ["rd-lead"],
        "manual_hours": {"min": 1, "max": 2},
        "confidence": "high",
        "basis": "software: mechanical install steps + running existing test suites"
      }
    ]
  }
}
```

## Changelog

- 2026-07-22: Task created — build commercial advisor persona (gap confirmed: no commercial persona; commercial-strategy.md unreferenced in canonical-roles catalog; risk-strategy.md same catalog gap).
- 2026-07-22: Built end-to-end, uncommitted. Catalog: `canonical-roles.yaml` +`commercial_strategy`/`risk_strategy`/`commercial_analysis` roles, `commercial` consumer label on header + market_research/competitive_landscape/kol_feedback (dhf-manifest v15). Agent: `.claude/skills/advisors/agents/commercial.md` authored + symlinked into `.claude/agents/` (advisors v12). project.yml: enabled + overlay stub + approved_agents. Discovery index regenerated (all 3 roles resolve; commercial_analysis = 32 report files); grounding rendered; loader loads "Commercial Assistant"; advisors tests 88/88, discovery-index tests 48/48. Awaiting user push decision; new subagent needs session restart.
