# 084 — Registry Sync 2026-06-08 (explain skill + advisor advances)

**ID**: 084
**Created**: 2026-06-08
**Status**: Complete
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: Medium

---

## PERMANENT RULES (do not remove)

This task document is the **session-recovery point** for this work. If the current session drops, is compacted, or ends, the next session must be able to load **this file alone** and continue where we left off.

1. **Update at every meaningful checkpoint (HARD RULE).** Tick the relevant Todo, add a dated Changelog line naming the concrete artifact (commit SHA, file path, decision, blocker), update progress counts.
2. **Phase-end batching is OK; drift-batching is not.** Write at the phase boundary, before the next phase starts.
3. **A commit is not a substitute.** Git records code; this doc records the narrative.
4. **Resume-ready before any session boundary.**
5. **Capture strategy + lessons as they happen.**

## Goals

_Bring the project's installed skills/agents back into lockstep with the hitachi registry, surfaced when the user asked "are we synced?"_

- Verify sync state across all four surfaces (`/sync-skills status`).
- Fast-forward the local hitachi mirror (was 9 commits behind `origin/main`).
- Pull the genuine drift into the project: new `explain` skill + 11 advisor-agent advances.
- Reconcile project config (`project.yml security.approved_skills`) + sync-log.
- Commit/push the pulled changes to the project repo `main`.
- Prune the 17 stale `sync/*` branches in the hitachi checkout.

## Todos

- [x] Run `/sync-skills status` — found registry BEHIND (9 commits) + 83-file drift
- [x] `git -C ../hitachi pull --ff-only` → registry SYNCED (`3535fe7`); drift fell to 46
- [x] `check --analyzed` → bucketed: 24 UPSTREAM_ONLY (new `explain` skill), 11 UPSTREAM_ADVANCE (advisor targets), 11 UNDETERMINED (advisor symlinks — reflections of the targets), 0 LOCAL_AHEAD, 0 push candidates
- [x] Pulled 35 files (24 explain + 11 advisor targets); re-check drift = 0 → SYNCED
- [x] Add `explain` to `project.yml` `security.approved_skills`
- [x] Write `.claude/sync-log.md` pull entry
- [x] Commit + push pulled changes to project `main`
- [x] `/sync-skills prune` — 17 merged branches removed (local+remote); 0 unmerged

## Notes

- `explain` is guidance-only: no `hooks/`, no `scripts/`, no `setup` action → no setup re-run needed.
- The 11 `agents/*.md` UNDETERMINED entries are symlinks into `skills/advisors/agents/`; pulling the 11 advisor target files resolved them automatically (same content, double-counted in the raw drift number).
- Advisor advance traces to `cd3f800` (ben/076 HIPAA-grounding follow-on).
- Task numbered 084 (not 082) because branch names `ben/082` / `ben/083` were already consumed by the 2026-06-08 task-doc audit + close-out work (PRs #49/#50), which produced no task docs.

## Changelog

- 2026-06-08: Task created mid-session to back the registry sync. Steps through "pull 35 files → drift 0" already complete; remaining: approved_skills + sync-log + project-repo push + prune.
- 2026-06-08: Sync complete — 35 files pulled (drift 0/SYNCED), `explain` added to approved_skills, sync-log written, 17 stale branches pruned. Status → Complete.

