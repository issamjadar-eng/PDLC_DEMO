# 098 — Economics Model Integrity + Red-Team the Aggregate

**ID**: 098
**Created**: 2026-06-30
**Status**: In Progress
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: High

---

## PERMANENT RULES (do not remove)

This task document is the **session-recovery point** for this work. If the current session drops, is compacted, or ends, the next session must be able to load **this file alone** and continue where we left off.

1. **Update at every meaningful checkpoint (HARD RULE).** After each meaningful unit of work — tick the relevant Todo checkbox, add a dated Changelog line naming the concrete artifact, update Goals counts. **When you tick a Todo off (or add/restructure Todos), fill/refresh the corresponding `## Economics` entry in the same edit** (if usage-metrics is installed) — checking the box is the estimate trigger.
2. **Phase-end batching is OK; drift-batching is not.**
3. **A commit is not a substitute.** Git records code; this doc records the project narrative.
4. **Resume-ready before any session boundary.**
5. **Capture strategy + lessons as they happen.**
6. **Estimation provenance (if `## Economics` is present).** Built per `.claude/skills/usage-metrics/references/effort-estimation-rubric.md` (usage-metrics); the block carries a `method_ref`. Point to the rubric, never copy it in. Skip if usage-metrics isn't installed.

Success test: a fresh Claude session, given only this file, can re-enter the work without asking "what were we doing?"

## Goals

_Make the agentic-value model defensible before the ROI claim (~800–2,753 person-hours saved) goes anywhere external._

- **Close the economics fill-gap (task v33).** The `## Economics` stub (v32) exists from creation but only gets *filled* at checkpoint — so a task can be created, worked, and Completed with an empty stub (sister-project 267). Trigger the fill on the events that actually happen: **todo check-off / todo edits**, **task completion**, and **session end**.
- **Tighten the `agentic_hours` definition (usage-metrics v9).** Redefine from "elapsed supervised wall-clock" → **human supervised-attention hours** (labor actually contributed), so the number is additive across tasks and honestly comparable to by-hand person-hours. Flag that pre-existing retrospective values (elapsed-ish) are conservative floors.
- **Red-team the aggregate.** Run the buyer-committee skeptics (CFO/PMO/CEO/CTO/VP-Eng/RA-VP/QA-VP) over the corrected ROI narrative; capture and triage findings.

## Todos

- [x] task v33: PERMANENT RULE 1 gains the todo-check → economics-fill trigger (template `create` rule 1)
- [x] task v33: `update … Complete` fills economics before flipping Status (completion gate — new step 1b)
- [x] task v33: lower SessionEnd marker threshold 30 → 15 min (`session-cleanup.sh` + 2 doc refs)
- [ ] task v33: version bump + changelog; push to registry _(bumped v32→v33 + README row; push pending)_
- [ ] usage-metrics v9: tighten `agentic_hours` definition (attention-hours) + unit note; bump + push
- [ ] Assemble the ROI narrative (claim + method + honest caveats) as the red-team target
- [ ] Run the red-team panel; capture findings + triage (fix / defer / accept)

## Economics

_By-hand person-hour estimate, **filled at checkpoint / on todo check-off** per the effort-estimation rubric (`usage-metrics` skill). Empty until the first completed todo is estimated; an empty `todos` list is ignored by the aggregator._

```json
{
  "economics": {
    "method_version": 1,
    "method_ref": ".claude/skills/usage-metrics/references/effort-estimation-rubric.md",
    "agentic_hours": null,
    "todos": [
      {
        "todo": "task v33 — economics fill-cadence (todo-check trigger + completion gate + 15-min SessionEnd)",
        "personas": ["rd-lead"],
        "manual_hours": {"min": 3, "max": 6},
        "confidence": "med",
        "basis": "skill authoring: PERMANENT RULE 1 + update step 1b + session-cleanup threshold + 2 doc refs + versioning across 4 sites — small module, LOC-norm low end + judgment on trigger semantics"
      }
    ]
  }
}
```
_`agentic_hours` left `null` until 098 completes (agentic_hours-fix + red-team still pending); set at the completion gate per the rubric._

## Changelog

- 2026-06-30: **task v32→v33 — economics fill-cadence (uncommitted).** Closed the fill-gap (v32 made the section exist; it only got *filled* at manual checkpoint). Three triggers, no per-turn hook (per user — didn't re-introduce the ben/100 pattern): (1) **PERMANENT RULE 1** (template `create` rule 1) now says ticking a Todo off fills the matching `## Economics` entry in the same edit; (2) **`update … Complete` step 1b** — completion gate refuses to close on an unfilled stub; (3) **SessionEnd threshold 30→15 min** (`session-cleanup.sh` + 2 SKILL.md doc refs). `checkpoint` 3b reworded "fill"→"reconcile". Bumped v32→v33 (frontmatter + README row). **Dogfooded:** checked off the three v33 todos above and filled this doc's `## Economics` entry in the same edit (rd-lead, 3–6 h). Next: push v33, then agentic_hours (v9) + red-team.
- 2026-06-30: Task created — economics model integrity (checkpoint-cadence fill fix + agentic_hours definition) + red-team the aggregate ROI claim. Spun out of the ben/096 close-out discussion (agentic_hours ambiguity + the checkpoint fill-gap surfaced while fixing the missing-economics-section issue).
