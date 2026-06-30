# 094 — Registry Skill Sync

**ID**: 094
**Created**: 2026-06-29
**Status**: Complete
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: Medium

---

## PERMANENT RULES (do not remove)

This task document is the **session-recovery point** for this work. If the current session drops, is compacted, or ends, the next session must be able to load **this file alone** and continue where we left off. That is only possible if the doc is kept current in-flight.

1. **Update at every meaningful checkpoint (HARD RULE).** After each meaningful unit of work, update this doc: tick the relevant Todo, add a dated Changelog line naming the concrete artifact, update progress counts.
2. **Phase-end batching is OK; drift-batching is not.** Write at phase boundaries, before the next phase starts.
3. **A commit is not a substitute.** Git records code; this doc records the narrative.
4. **Resume-ready before any session boundary.**
5. **Capture strategy + lessons as they happen.**

## Goals

_Bring the project's installed skills/agents into alignment with the `hitachi` registry, per the user's "make sure we have skills synced" request (scope chosen: updates + new skills)._

- Pull the 4 safe updates to already-installed skills (`manifest.md`, `usage-metrics` README/SKILL/setup.py).
- Install 3 new skills from the registry: `red-team`, `regulatory-authoring`, `writing-well` — including their bundled agents and rules, wired per each skill's `setup` action.
- Keep the locally-newer `usage-metrics/scripts/collect.py` (LOCAL_AHEAD) — do **not** clobber; it remains a push-back candidate.
- Update `project.yml` security allowlists (`approved_skills` += 3, `approved_agents` += 10) and the CLAUDE.md auto-loaded-rules pointer for `regulatory-authoring`.
- Commit + push the synced skills/agents to the project repo.

## Todos

- [x] `git pull --ff-only` project repo to latest
- [x] `/sync-skills` status + analyzed check — bucketize 45-file drift
- [x] Pull 44 files (4 UPSTREAM_ADVANCE + 40 UPSTREAM_ONLY); skip LOCAL_AHEAD `collect.py`
- [x] Wire agent symlinks (10) + `regulatory-authoring` rule symlink per setup actions
- [x] Append pull entry to `.claude/sync-log.md`
- [x] `project.yml`: add 3 skills to `approved_skills`, 10 agents to `approved_agents`
- [x] CLAUDE.md: add `regulatory-authoring.md` to Auto-loaded rules list
- [x] Commit + push the sync (project repo → main) — PR #68 merged, branch deleted
- [ ] (optional, deferred) Reconcile usage-metrics divergence — push newer `collect.py` to registry

## Changelog

- 2026-06-29: Task created. Pull already applied (44 files), agents/rule symlinked, sync-log updated.
- 2026-06-29: project.yml allowlists updated (approved_skills +red-team/regulatory-authoring/writing-well; approved_agents +10 pathed entries). CLAUDE.md auto-loaded-rules pointer added for regulatory-authoring. YAML validated.
- 2026-06-29: Pushed to main — PR #68 merged (49 files; agents/rule confirmed as symlinks mode 120000), branch deleted, working tree clean. Status → Complete. Only deferred item: optional push-back of locally-newer collect.py to registry.
