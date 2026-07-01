# 071 — Gemini CLI Partial-Support Setup Guidance

**ID**: 071
**Created**: 2026-05-31
**Status**: Complete
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: Low

---

## PERMANENT RULES (do not remove)

This task document is the **session-recovery point** for this work. If the current session drops, is compacted, or ends, the next session must be able to load **this file alone** and continue.

1. **Update at every meaningful checkpoint (HARD RULE).** After each meaningful unit of work, tick the relevant Todo, add a dated Changelog line.
2. **Phase-end batching is OK; drift-batching is not.**
3. **A commit is not a substitute** for the task-doc update.
4. **Resume-ready before any session boundary** — exact `/task` activation command, in-flight artifacts, next steps.
5. **Capture strategy + lessons inline.**

## Goals

Add Gemini CLI install/setup/launch guidance to `setup.md` as an **optional** section, with explicit framing: Gemini support is **partial** and intended for users without Claude access who want to **evaluate/learn** the project, not develop in it. Claude Code remains the fully-supported assistant.

User's pinned constraints (2026-05-31):
1. Install path: `npm install -g @google/gemini-cli` (user-confirmed).
2. Section is **optional**, not in the README "Choose Your Path" table — surfaced only for users who don't have Claude.
3. Section must cover: install → auth → launch-in-project → cross-link to existing `GEMINI.md` (which already has project mandates but no install instructions).
4. Acknowledge Gemini does NOT have the task-gate hook enforcement Claude Code does (already documented in `GEMINI.md` — cross-link, don't redeclare).

## Todos

- [x] Create + activate task
- [x] Drafted `setup.md` §18 — Gemini CLI Optional, Evaluation Only. Placed between §17 file-locator and the (now-renumbered) §19 Confirm. Capability table contrasts Claude vs. Gemini on slash-skills, task-gate hook enforcement, MCP servers, and develop/commit/push. Sections: capability table → install (`npm install -g @google/gemini-cli`) → auth (`gemini`) → launch-in-project (`cd ~/projects/PDLC_DEMO && gemini`) → project-specific guardrails (self-enforced task gate, macOS symlink fallback) → when to switch back to Claude.
- [x] Cross-linked from `GEMINI.md` top → `setup.md#18`. Single sentence at top of GEMINI.md states partial-support framing + points at the install section.
- [x] Renumbered "Confirm Everything Is Wired Up" §18 → §19; added Changelog row dated 2026-05-31.
- [x] Commit + push — landed as `84e6eb8`, merged to `main` via PR #28 (`6be580b`).
- [x] Mark Complete + add row in `tasks/ben/000-index.md`.

## Resume

Nothing to resume — task Complete. All deliverables are on `main`:
- `setup.md` §18 "Gemini CLI (`gemini`) — Optional, Evaluation Only" (install → auth → launch → guardrails → when-to-switch-back), plus the §18→§19 renumber and a dated setup.md Changelog row.
- `GEMINI.md` line 5 cross-link to `setup.md#18` with the partial-support framing.

## Changelog

- 2026-05-31: Task created. User requested Gemini CLI install/setup/launch guidance in setup.md, framed as evaluation-only for non-Claude users. Constraints: optional section (not in README path table), npm install path confirmed.
- 2026-05-31: Authored `setup.md` §18 + `GEMINI.md` cross-link + §18→§19 renumber; committed as `84e6eb8` and merged via PR #28 (`6be580b`). _(Doc not updated at the time — session ended uncheckpointed.)_
- 2026-06-08: Retroactive checkpoint. Confirmed all deliverables present on `main` (setup.md §18 at L798, GEMINI.md cross-link at L5). Flipped Status → Complete, ticked the two remaining Todos, and added the index Completed row that was never created. Cleared the uncheckpointed marker.

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
        "todo": "Gemini CLI partial-support guidance",
        "personas": [
          "program-manager",
          "rd-lead"
        ],
        "manual_hours": {
          "min": 4,
          "max": 10
        },
        "confidence": "low",
        "basis": "setup.md Gemini-CLI section"
      }
    ]
  }
}
```
