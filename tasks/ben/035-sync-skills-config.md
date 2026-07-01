# NNN — Sync-Skills Config & Console Restart

**ID**: NNN
**Created**: 2026-05-05
**Status**: Complete
**Owner**: Ben Xavier
**Priority**: High

---

## PERMANENT RULES (do not remove)

This task document is the **session-recovery point** for this work. Keep it updated at every meaningful checkpoint.

## Goals

- Update `project.yml` to approve new `jira-pull` skill
- Register two new agents from `dhf-manifest` in `approved_agents`
- Restart project-console to activate v1.17.0 code

## Todos

- [x] Add `jira-pull` to `approved_skills` in project.yml
- [x] Add `dhf-manifest/agents/tier1-enricher` to `approved_agents`
- [x] Add `dhf-manifest/agents/tier1-restructure` to `approved_agents`
- [x] Restart console with `/project-console start`

## Changelog

2026-05-05 — Synced 191 files from hitachi registry (project-console v1.17.0, dhf-manifest scope refresh, new jira-pull skill, tracker maturity bump)
2026-05-05 — Updated project.yml approved_skills + approved_agents; restarted console (v1.17.0 now active on port 8765)

## Economics

_Retrospective estimate (rough; from task summary). See effort-estimation-rubric.md._

```json
{
  "economics": {
    "method_version": 1,
    "retrospective": true,
    "agentic_hours": 2,
    "todos": [
      {
        "todo": "Sync-skills config",
        "personas": [
          "rd-lead"
        ],
        "manual_hours": {
          "min": 4,
          "max": 10
        },
        "confidence": "low",
        "basis": "sync-skills config"
      }
    ]
  }
}
```
