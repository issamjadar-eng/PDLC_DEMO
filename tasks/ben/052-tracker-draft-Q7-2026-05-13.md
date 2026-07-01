# 052 — Console Tracker draft Q7 (2026-05-13)

**ID**: 052
**Created**: 2026-05-13
**Status**: Abandoned
**Created By**: project-console (workflows/tracker-draft)
**Owner**: Ben Xavier
**Priority**: Medium

---

## PERMANENT RULES (do not remove)

1. Every stage transition (outline-proposed, outline-approved, draft-synthesized, saved/cancelled) is logged in this doc's Changelog.
2. On Save & Commit the console marks this task `Complete` and fast-forwards the worktree branch into main.
3. On Cancel the console flips this task to `Abandoned` and removes the worktree (the in-progress draft is discarded).
4. Do not edit the worktree files directly — use the console UI so the audit trail stays intact.

## Goals

Auto-created session task backing a live B6 Create Draft workflow for tracker row Q7. Worktree: `.worktrees/workflow-tracker-draft-Q7-2026-05-13/` on branch `workflow/tracker-draft-Q7-2026-05-13`. The agent proposes an outline → user approves → agent synthesizes → user reviews → Save & Commit ff-merges into main.

## Outline

_Will be populated when the agent proposes an outline._

## Final Draft Path

_Will be populated when Save & Commit relocates the draft from `_drafting/` to its eventual home._

## Changelog

- 2026-05-13 — Auto-created by project-console on first Create Draft click for row Q7.
- 2026-06-08: Marked ABANDONED via task-doc audit — orphaned workflow stub; worktree + branch already removed; no draft ever produced. Filed under Abandoned in 000-index.md.

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
        "todo": "Tracker draft Q7 (abandoned)",
        "personas": [
          "rd-lead"
        ],
        "manual_hours": {
          "min": 1,
          "max": 2
        },
        "confidence": "low",
        "basis": "abandoned orphan workflow stub"
      }
    ]
  }
}
```
