# 062 — Copy git-workflow rule into this project

**ID**: 062
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

Final rule of the disposition pass ([[059]], [[060]], [[061]]). `git-workflow` is **tier-3** — project policy, not registry-portable — so it is **hand-authored as a regular file** in this project's `.claude/rules/`, not skill-owned and not symlinked.

- Copy the `git-workflow` rule (from sister project `arthrex-pccp`) into `.claude/rules/git-workflow.md` as a regular committed file.
- Add a pointer line to CLAUDE.md's "Auto-loaded rules" section.

<!-- STRATEGY CONTENT: operations, repo-governance -->
**Tier-3 rule.** `git-workflow` is project-authored, never registry-distributed — each project chooses its own git workflow. Copied from arthrex as the starting point. **Open question flagged to user:** the copied rule defines "push" as PR-then-auto-merge, but PDLC-DEMO has been operating direct-to-`main` this session — the rule may need adapting to match actual practice.
<!-- END STRATEGY CONTENT -->

## Todos

- [x] Copy `git-workflow.md` into `.claude/rules/` as a regular file
- [x] Add pointer line to CLAUDE.md "Auto-loaded rules" section
- [x] Resolve with user: **keep verbatim** (PR-then-auto-merge) — user decision 2026-05-16

## Changelog

- 2026-05-16: Task created. git-workflow is the last rule in the disposition pass; tier-3, project-authored.
- 2026-05-16: Copied `git-workflow.md` from arthrex-pccp into `.claude/rules/` as a **regular file** (not a symlink — project-authored, never registry). Completed CLAUDE.md "Auto-loaded rules" section — now lists all 6 rules (was 1 of 6).
- 2026-05-16: **User decision — keep verbatim.** PDLC-DEMO adopts the PR-then-auto-merge workflow: "push" / "merge" now means commit → branch → PR → auto-merge → delete branch. No edit to the rule. From here on, project-repo landings follow the 6-step sequence (the direct-to-`main` commits earlier this session predate the rule).

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
        "todo": "git-workflow rule",
        "personas": [
          "rd-lead"
        ],
        "manual_hours": {
          "min": 2,
          "max": 5
        },
        "confidence": "low",
        "basis": "copy git-workflow rule into project"
      }
    ]
  }
}
```
