# 099 — Retrospective Token-Cost Allocation (de-unattribute by day-overlap)

**ID**: 099
**Created**: 2026-07-01
**Status**: In Progress
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: Medium

---

## PERMANENT RULES (do not remove)

This task document is the **session-recovery point** for this work. If the current session drops, is compacted, or ends, the next session must be able to load **this file alone** and continue where we left off.

1. **Update at every meaningful checkpoint (HARD RULE).** After each meaningful unit of work — tick the relevant Todo, add a dated Changelog line, update Goals. **When you tick a Todo off, fill/refresh the matching `## Economics` entry in the same edit** (usage-metrics installed).
2. **Phase-end batching is OK; drift-batching is not.**
3. **A commit is not a substitute.**
4. **Resume-ready before any session boundary.**
5. **Capture strategy + lessons as they happen.**
6. **Estimation provenance (if `## Economics` present).** Built per `.claude/skills/usage-metrics/references/effort-estimation-rubric.md`; block carries `method_ref`. Point to the rubric, never copy it in.

Success test: a fresh session, given only this file, can re-enter the work.

## Goals

_Turn the currently-`_unattributed` measured token spend (~$208 — sessions that predate the activation ledger) into per-task cost estimates by allocating each day's unattributed cost across the tasks active that day. The COST is measured; only the SPLIT is estimated — stronger evidence than the by-hand hours._

- Add a retrospective **cost allocator** to `usage-metrics/aggregate.py`: apportion each session's `_unattributed` cost across its days (by day token-share), then split each day's unattributed cost across tasks with a changelog entry that day.
- **Guard against bulk-edit-day noise** (e.g. the 2026-06-30 economics backfill touched many tasks): if a day has more than `max_tasks_per_day` active tasks, the signal is unreliable → skip allocation for that day, leave it unattributed.
- **Flag `cost_basis`** per task (`measured` / `allocated` / `measured+allocated`) so allocated ≠ measured is never hidden.
- Surface `cost_measured` / `cost_allocated` / `cost_unattributed_residual` in `value_summary`.
- **Bounded by transcript coverage** — only days with session data (Jun 15 → Jul 1) can be allocated; tasks worked before that have no token data and stay uncosted.

## Todos

- [x] Implemented `allocate_unattributed()` + `_task_active_days()` in `aggregate.py` (per-session day-share apportion → day→active-task even split)
- [x] Parse task-active-days from changelog dates (`- YYYY-MM-DD`); **excluded `000-index`** (was absorbing $17 as a phantom task)
- [x] Wired into `tasks_out` (`cost_allocated` + `cost_basis`) + `value_summary` (`cost_measured_attributed` / `cost_unattributed_measured` / `cost_allocated` / `cost_unattributed_residual`)
- [x] `max_tasks_per_day` threshold (`project.yml usage_metrics.cost_allocation.max_tasks_per_day`, default 4) + bulk-edit-day skip
- [x] Tested on real data — **$146.91 of $208.39 allocated** onto tasks 087–095; **$61.47 residual** (0-active or >4-active days). project-console 1.30.7 renders it (≈ marker + tooltip).
- [ ] usage-metrics v11 + project-console 1.30.7 README/version done; **push pending**

## Open Questions

- Even-split vs weight by changelog-touches-per-day? Lean: even split for v1 (defensible default), note the option.
- Does the console need to show `cost_basis`? Lean: later — data first.

## Resume

**Status:** Task created. Investigated the data contract: `collect_records` gives per-task `by_model` cost (incl `_unattributed`) + per-person `by_day` tokens; no per-day-per-task. Plan = per-session apportion of `_unattributed` cost by day-share → day→active-tasks split with a max-per-day guard.
**First action on resume:** implement `allocate_unattributed` in `aggregate.py`.

## Economics

_By-hand person-hour estimate, **filled at checkpoint / on todo check-off** per the effort-estimation rubric (`usage-metrics` skill). Empty until the first completed todo is estimated._

```json
{
  "economics": {
    "method_version": 1,
    "method_ref": ".claude/skills/usage-metrics/references/effort-estimation-rubric.md",
    "agentic_hours": {"min": 1, "max": 2},
    "todos": [
      {
        "todo": "retrospective cost allocator (allocate_unattributed + _task_active_days in aggregate.py) + console display",
        "personas": ["rd-lead"],
        "manual_hours": {"min": 6, "max": 14},
        "confidence": "med",
        "basis": "software: ~90 LOC aggregate.py (per-session apportion + day-overlap allocation + guards + value_summary wiring) + value.js display + config + tests — LOC-norm mid; algorithm design (day-share apportioning, bulk-edit guard) adds judgment"
      }
    ]
  }
}
```
_First ranged `agentic_hours` on a real task (dogfooding usage-metrics v10) — renders as "1–2" in the console._

## Changelog

- 2026-07-01: **Allocator built + tested + wired to console (uncommitted).** `allocate_unattributed()` in `aggregate.py`: apportions each session's `_unattributed` cost across its days by token-share, then splits each (person, day) cost evenly across tasks with a changelog entry that day (`_task_active_days`, **excluding `000-index`** — it was eating $17 as a phantom task). Guards: 0-active-tasks day stays unattributed; >4-active-tasks day skipped as bulk-edit noise (config `max_tasks_per_day`). Per-task `cost_allocated` + `cost_basis`; `value_summary` gains the 4-way cost breakdown. **Result: $146.91 of $208.39 (70%) allocated onto tasks 087–095; $61.47 residual.** The cost is measured; only the split is estimated (stronger than the modeled hours). project-console 1.30.7: by-task Agentic-$ column adds allocated + shows a ≈ marker + tooltip; hero/card totals include it. usage-metrics v10→v11. Verified live on :8765. Dogfooded the ranged `agentic_hours` (099's own = "1–2"). Next: push.
- 2026-07-01: Task created — retrospective token-cost allocation. Spun out of the ben/098 cost discussion: the ~$208 `_unattributed` (pre-ledger sessions) can be de-unattributed by allocating each day's measured cost across the tasks active that day, bounded by transcript coverage. Cost is measured; only the split is estimated.
