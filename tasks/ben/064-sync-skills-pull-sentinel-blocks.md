# 064 — Registry pull: sentinel-blocks rule refresh

**ID**: 064
**Created**: 2026-05-16
**Status**: Complete
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: Low

---

## PERMANENT RULES (do not remove)

Session-recovery point. Keep current in-flight.

1. **Update at every meaningful checkpoint (HARD RULE).**
2. **Phase-end batching is OK; drift-batching is not.**
3. **A commit is not a substitute.**
4. **Resume-ready before any session boundary.**
5. **Capture strategy + lessons as they happen.**

## Goals

`/sync-skills pull` — apply the one upstream change cleanly classified as auto-pull.

- Pull `skills/medtech-docs/rules/sentinel-blocks.md` — hitachi **PR #168** (`cda0eaa`) backfilled the v23 renderer capabilities (`depth=<N>`, `dhf-table` variants, updated `exclude=`/`preserve-column` defaults) into the rule. Our copy is the pre-v23 stale text; the pull makes the rule match `render-sentinels.py` (already v23 here).
- `UPSTREAM_ADVANCE` — local matched the `b0beab3` blob, upstream advanced 1 commit. Safe fast-forward.

**Not pulled** (surfaced as ben/058 push candidates, `LOCAL_AHEAD` / `LOCAL_ONLY`): `skills/advisors/{README.md,SKILL.md,VERSION,.gitignore,tests/run.sh}` — local advisors work is newer than hitachi.

## Todos

- [x] `pull-file skills/medtech-docs/rules/sentinel-blocks.md` — applied (hitachi `cda0eaa`)
- [x] Verify the `.claude/rules/sentinel-blocks.md` symlink still resolves — resolves
- [x] Record the pull in `.claude/sync-log.md`
- [x] Land (commit via git-workflow PR cycle) — PR #4, merged `a9a1646`

## Outcome

Complete. `skills/medtech-docs/rules/sentinel-blocks.md` pulled (hitachi PR #168 backfill — v23 renderer-capability docs); rule-text-only, no project impact. Landed via project PR #4.

## Changelog

- 2026-05-16: Task created. `check --analyzed`: 1 auto-pull (sentinel-blocks UPSTREAM_ADVANCE), 5 advisors files LOCAL_AHEAD/LOCAL_ONLY (ben/058 push candidates, not pulled).

## Economics

_Retrospective estimate (rough; from task summary). See effort-estimation-rubric.md._

```json
{
  "economics": {
    "method_version": 1,
    "retrospective": true,
    "agentic_hours": 1,
    "todos": [
      {
        "todo": "sync-skills pull (sentinel-blocks)",
        "personas": [
          "rd-lead"
        ],
        "manual_hours": {
          "min": 2,
          "max": 5
        },
        "confidence": "low",
        "basis": "small sentinel-blocks rule pull"
      }
    ]
  }
}
```
