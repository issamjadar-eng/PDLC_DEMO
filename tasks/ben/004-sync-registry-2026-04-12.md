---
**ID**: 004
**Created**: 2026-04-12
**Status**: In Progress
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: Medium
---

# 004 — Sync Skills Registry (2026-04-12)

## Goals

Pull latest skills/agents from the hitachi registry and apply the resulting setup updates so the project tracks upstream.

- Pull upstream skill changes (task v11, new secops skill, manifest)
- Re-run `/task setup` to wire new SessionStart/SessionEnd hooks
- Run `/secops setup` to install agent, hook, and canonical permissions
- Update `project.yml` allowlists to include `secops`
- Record the sync in `.claude/sync-log.md`

## Todos

- [x] `/sync-skills check` — diff against registry
- [x] Pull upstream files (task v11, secops skill, hooks, manifest)
- [x] `/task setup` — register session-env / session-cleanup hooks
- [x] `/secops setup` — install agent, security-assert hook, merge permissions
- [ ] Update `project.yml` `approved_skills` (add `secops`)
- [ ] Write `.claude/sync-log.md` entry
- [ ] Re-run `/sync-skills check` — verify clean

## Changelog

- 2026-04-12: Task created to track registry sync session.
