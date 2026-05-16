# 063 — sync-skills: auto-clean merged branches + `prune` action

**ID**: 063
**Created**: 2026-05-16
**Status**: In Progress
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: Medium

---

## PERMANENT RULES (do not remove)

Session-recovery point. Keep current in-flight.

1. **Update at every meaningful checkpoint (HARD RULE).**
2. **Phase-end batching is OK; drift-batching is not.**
3. **A commit is not a substitute.**
4. **Resume-ready before any session boundary.**
5. **Capture strategy + lessons as they happen.**

## Goals

Stop `/sync-skills` push branches from accumulating as stale debris (111 had piled up in the hitachi checkout — cleared manually 2026-05-16).

**Root cause:** `push-prep` does `git checkout -b sync/<branch>` in the hitachi checkout; nothing ever deletes that local branch. The `--merge` path deletes the *remote* branch (`gh pr merge --delete-branch`) but not the local one. PR-only pushes leave both sides for a later out-of-band merge.

- **Part 1** — `push` Step 5b (`--merge` path): after `checkout main` + `pull --ff-only`, also `git -C <hitachi> branch -D <branch>`. Self-cleaning merge.
- **Part 2** — new `prune` action: enumerate local + remote `sync/*` branches, `git cherry`-check each against `main`, delete verified-merged ones (both sides), list unmerged/superseded for manual review. Dry-run → confirm → delete.
- **Part 3 (light)** — `status` reports a stale-`sync/*`-branch count so accumulation is visible.

## Todos

- [x] Read `sync-skills/SKILL.md` + `scripts/sync.sh` end-to-end
- [x] Part 1: SKILL.md `push` Step 5b — delete local branch after merge
- [x] Part 2: `sync.sh` `prune` subcommand + SKILL.md `prune` action
- [x] Part 3: `status` stale-branch count
- [x] Test the `prune` subcommand
- [x] Version bump + README + Best Practices
- [ ] Push to hitachi (via `/sync-skills push`) + merge

## Changelog

- 2026-05-16: Task created. Follows the manual cleanup of 111 stale `sync/*` branches.
- 2026-05-16: **sync-skills v8.1 → v8.2.** Part 1 — `push` Step 5b (`--merge` path) now `git branch -D`s the local sync branch after the ff-pull (the `--delete-branch` only removed the remote). Part 2 — new `prune` action + `sync.sh prune [--apply]` subcommand: classifies `sync/*` branches MERGED/UNMERGED via `git cherry`, dry-run by default, `--apply` deletes merged ones local+remote, never touches unmerged. Part 3 — `status` block 5 notes a stale-branch count (hygiene only). New `tests/test_prune.sh` — 15 assertions, all pass; `test_status.sh` (11) + `test_three_way_pull.sh` (10) still green. README Changelog + Best Practices row added. Pending: push to hitachi.
