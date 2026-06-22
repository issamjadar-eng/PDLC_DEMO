# 091 — Article: AI Cost Control & Token-Usage Governance (Fintech Lens)

**ID**: 091
**Created**: 2026-06-16
**Status**: Not Started
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
2. **Phase-end batching is OK; drift-batching is not.** Planned phases (e.g., "finish Phase 2, then log the whole phase at once") are a legitimate checkpoint — writing once per phase is fine if the phase is bounded and the write happens **at the phase boundary, before the next phase starts**. What's not OK: accumulating updates in your head across arbitrary work, waiting for "end of the session," "after the push," or the user to ask. By then a crash or context-trim has lost the state. Rule of thumb: if you can't name the specific upcoming checkpoint where you'll write the update, write it now.
3. **A commit is not a substitute.** Git history records code; this doc records the project narrative — what was done, why, what's left, what surprised us.
4. **Resume-ready before any session boundary.** Before recommending a fresh session, marking Complete, or ending work, the doc must already contain: (a) what was completed this session with concrete artifacts, (b) status of any in-flight work and temp artifacts, (c) priority-ordered next steps with file paths, (d) open questions blocking progress, (e) the exact `/task` activation command to resume.
5. **Capture strategy + lessons as they happen.** If the session produces option comparisons, scope/boundary decisions, architectural pivots, non-obvious insights, or corrected assumptions, write them into the appropriate section **in-flight** — not just in chat. Harvesting skills can only surface what was written.

Success test for this doc: a fresh Claude session, given only this file, can re-enter the work without asking the user "what were we doing?"

## Goals

_What this task aims to accomplish and why it matters to the project._

- Produce a new external-audience **article** (under the `articles/` tree, via `/medtech-docs new-article`) on **controlling and governing the cost of AI-model usage** — token consumption, spend visibility, and budget controls — framed through a **fintech / financial-operations (FinOps)** lens.
- Cover the core levers: token-usage accounting, prompt/context-budgeting, model-tier selection (right-sizing Opus vs Sonnet vs Haiku), caching, batching, rate/quota guardrails, per-team/per-workflow cost attribution, and chargeback/showback.
- Keep the article **non-canonical** per `articles-not-canonical.md` — it is an outward-facing explainer/retelling, carries the "NOT A CANONICAL SOURCE" banner, and links to canonical sources for any project-specific claims.
- Tie the cost-governance story back to this project's own AI-driven workflow where useful (e.g., the prompt-cache TTL economics, model-tier routing in workflows/agents) without treating the article as a source of truth.

## Todos

_Actionable work items. Check off as completed._

- [x] Confirm scope/angle with user → **General FinOps-for-AI** (vendor-neutral explainer; not tied to this repo's specifics)
- [x] Confirm target audience → **Leadership briefing** (concise, decision-oriented, cost-governance framing)
- [ ] Read `articles/README.md` and the `/medtech-docs new-article` action before authoring
- [ ] Scaffold the article via `/medtech-docs new-article` (gets the NOT-A-CANONICAL banner stamped)
- [ ] Draft sections: cost drivers → token accounting → control levers → attribution/chargeback → governance & guardrails
- [ ] Add concrete, clearly-marked illustrative figures/examples (mark any fabricated numbers as illustrative)
- [ ] Review for non-canonical posture + vendor-neutral AI attribution
- [ ] Push (PR → auto-merge) per git-workflow rule when user says "push"

## Scope (confirmed 2026-06-16)

- **Angle**: General **FinOps-for-AI** — a vendor-neutral explainer on controlling/governing AI-model spend (token economics, model tiering, caching, batching, attribution/chargeback). Not tied to this repo's internals; "fintech" interpreted as **FinOps (financial operations / cost governance) applied to AI spend**.
- **Audience**: **Leadership briefing** — concise, decision-oriented, cost-governance framing. Tone for execs, not engineers.

## Open Questions

- _(none blocking — scope confirmed above)_

## Resume

**Status at last checkpoint (2026-06-22):** Not Started. Scope + audience are locked (see Scope section); **no authoring has begun** — no article scaffolded, no `articles/` files created. Git confirms zero commits touch `091` or `articles/` since task creation, so nothing is in-flight or at risk.

**First action on resume:**
1. Activate: `bash .claude/hooks/task-activate.sh add <SESSION_ID> 091`
2. Read `articles/README.md` + the `/medtech-docs new-article` action contract before authoring (per the read-the-contract rule).
3. Scaffold via `/medtech-docs new-article` (stamps the NOT-A-CANONICAL banner), then draft in the section order in Todos.

**In-flight artifacts:** none. Nothing committed by Claude. No temp files.

## Changelog
- 2026-06-16: Task created.
- 2026-06-16: Scope confirmed with user — General FinOps-for-AI explainer, leadership-briefing audience. Resolved all three open questions.
- 2026-06-22: **Checkpoint (retroactive).** Cleared the stale `uncheckpointed-ben-091-2026-06-19` marker left by a prior session that ended without checkpointing. Confirmed via git log that no work was lost (task still Not Started; scope intact). Doc is resume-ready — see Resume section.
