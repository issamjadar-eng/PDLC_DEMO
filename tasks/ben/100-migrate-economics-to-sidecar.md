# 100 — Migrate Retrospective Economics to the v12 Sidecar

**ID**: 100
**Created**: 2026-07-02
**Status**: Complete
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: Medium

---

## PERMANENT RULES (do not remove)

This task document is the **session-recovery point** for this work. If the current session drops, is compacted, or ends, the next session must be able to load **this file alone** and continue.

1. **Update at every meaningful checkpoint (HARD RULE).** Tick the Todo, add a dated Changelog line, update Goals. When you tick a Todo off, fill/refresh the matching `## Economics` entry in the same edit (usage-metrics installed).
2. **Phase-end batching is OK; drift-batching is not.**
3. **A commit is not a substitute.**
4. **Resume-ready before any session boundary.**
5. **Capture strategy + lessons as they happen.**
6. **Estimation provenance (if `## Economics` present).** Built per `.claude/skills/usage-metrics/references/effort-estimation-rubric.md`; carries `method_ref`. Point, never copy.

Success test: a fresh session, given only this file, can re-enter the work.

## Goals

_Get the retrospective by-hand estimates OUT of the 95 finished task docs and into the v12 `economics.json` sidecar, so finished docs aren't carrying rough backfill data. The Value & ROI numbers must not change._

- Extract the **retrospective** (`retrospective: true`) `## Economics` blocks from the 95 historical task docs → `tools/usage-metrics/economics.json` (flat `{"<tf>/<NNN>": <econ-object>}` map, the v12 sidecar shape).
- **Remove** the `## Economics` section from those 95 docs (sidecar now holds the data; in-doc-wins precedence means the sidecar only takes effect once the in-doc block is gone).
- **Keep the 4 real-time blocks in-doc** (096–099) — genuine per-task records, not backfill.
- **Verify** `value_summary` is byte-identical to the baseline (97 w/ estimate, 94 retro, 801–2,768 hrs saved) — the migration is a pure relocation, not a data change.

## Todos

- [x] Extracted **94** retrospective econ objects → `tools/usage-metrics/economics.json` (flat `{"tf/NNN": econ}` map; 94 unique keys — `ben/035` has 2 docs sharing the number, which aggregate already collapsed)
- [x] Removed `## Economics` from **95** retrospective docs (kept 096–099 real-time + 100's own stub in-doc)
- [x] Re-aggregated; `value_summary` **byte-identical** to baseline (97 w/ estimate, 94 retro, 801–2,768 hrs saved) — pure relocation
- [ ] Commit + push (economics.json + 95 cleaned docs) — pending

## Baseline (must match after migration)

`tasks_with_estimate: 97 · tasks_retrospective: 94 · manual_hours: 1304–3292 · agentic_hours: 485 · hours_saved: 801–2768`

## Resume

**Status:** Task created. v12 sidecar contract read: `parse_task_economics` prefers the in-doc block only when it has non-empty `todos`; else falls to `sidecar.get("<tf>/<NNN>")`. So removing the in-doc block activates the sidecar.
**First action on resume:** run the migration script (extract → economics.json + strip sections), then re-aggregate and diff `value_summary`.

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
        "todo": "migrate 94 retrospective economics blocks out of task docs into the v12 economics.json sidecar + verify value_summary unchanged",
        "personas": ["rd-lead"],
        "manual_hours": {"min": 2, "max": 5},
        "confidence": "med",
        "basis": "data migration: extraction+strip script over ~95 docs + sidecar build + before/after aggregate diff — small scripting + careful verification (LOC-norm low; judgment on the strip regex + in-doc-wins precedence)"
      }
    ]
  }
}
```

## Changelog

- 2026-07-03: Status changed to Complete. Economics already filled (agentic 1–2 h).
- 2026-07-03 (checkpoint recovery — no transcript): Reconciled doc vs git. The migration below marked *"uncommitted / Next: commit + push"* **shipped and is merged to `main`**: PR #96 (`88bc141` — migrate 94 retrospective economics blocks to the v12 `economics.json` sidecar; `value_summary` verified byte-identical). This is the commit brought in by today's `git pull`. **Do not re-run the migration or re-push.** All described work delivered — Status left `In Progress` pending user confirmation to close.
- 2026-07-02: **Migration done + verified (uncommitted).** Extracted the 94 retrospective `## Economics` objects into `tools/usage-metrics/economics.json` (v12 sidecar, flat `{"tf/NNN": econ}` map) and removed the `## Economics` section from 95 finished task docs (kept 096–099 real-time + 100's stub in-doc). Re-aggregated: `value_summary` **byte-identical** to baseline (97 w/ estimate, 94 retro, 801–2,768 hrs saved) — pure relocation, no data change. Console value data intact. Note: `ben/035` has two docs sharing the number (pre-existing dup) → one sidecar key, both docs stripped; aggregate already collapsed them so no numeric change. Next: commit + push. The finished docs are now clean of rough backfill data; the sidecar is CI-read, in-doc-wins so any future real per-task estimate silently supersedes it.
- 2026-07-02: Task created — migrate the 95 retrospective `## Economics` blocks out of finished task docs into the v12 `economics.json` sidecar (pulled this session), keeping the 4 real-time blocks in-doc. Value numbers must not change.
