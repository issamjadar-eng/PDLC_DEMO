# 057 — Review and Correct Skills Manifest (registry PR #163)

**ID**: 057
**Created**: 2026-05-13
**Status**: Complete
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: Medium

---

## PERMANENT RULES (do not remove)

This task document is the **session-recovery point** for this work. If the current session drops, is compacted, or ends, the next session must be able to load **this file alone** and continue where we left off. That is only possible if the doc is kept current in-flight.

1. **Update at every meaningful checkpoint (HARD RULE).**
2. **Phase-end batching is OK; drift-batching is not.**
3. **A commit is not a substitute.**
4. **Resume-ready before any session boundary.**
5. **Capture strategy + lessons as they happen.**

## Goals

Review commit `2456f5a` ("skills: refresh manifest.md") on the `hitachi` registry repo, determine merge safety, merge it, then layer our corrections as a separate commit so the original contribution stays intact and attributable.

## Review Findings

Commit `2456f5a` (Mykhailo Chaus, May 12) refreshes `skills/manifest.md` from 9 → 24 skills and redraws the registry structure.

- **Merge safety**: PR branch based on `afcabb1`; `main` had advanced 5 commits (#158–#162). `main` never touched `manifest.md` → clean merge, no conflict. Change is purely additive doc content.
- **Stale versions**: `main` advanced past 3 skills the PR documented —
  - secops: PR said 7, actual `SKILL.md` frontmatter 8 (#162)
  - dhf-manifest: PR said 9, actual 12 (#161)
  - trace-matrix: PR said 7, actual 8 (#159)
- **Structural inaccuracy**: Registry Structure tree annotated root `agents/` as "symlinks back to skills/advisors/agents/". Reality: the 14 advisor `.md` files in root `agents/` are real file copies; only `project-secops.md` is a symlink. The prose at line 67 ("working copies kept in sync") is accurate; the tree comment was not.
- **Inherited (not PR's fault, not corrected here)**: `project-console` and `digest` have `VERSION` files (1.21.1, 1.3.0) that disagree with their `SKILL.md` frontmatter (1.17.0, 9). Per the registry's own Project Practices table, `SKILL.md` frontmatter is the canonical version source — so the PR's values are correct by convention. The `VERSION`-file drift is a separate skill-level bug.

<!-- STRATEGY CONTENT: operations, registry-governance -->
**Decision — accept-then-correct over edit-then-merge.** When a registry PR is mechanically safe but content-stale, merge the contributor's work untouched (preserves attribution + a clean `#163` merge commit), then layer corrections as a separate commit. Avoids rewriting someone else's branch and keeps the "what was contributed" vs "what we fixed" history legible.

**Decision — canonical version source is `SKILL.md` frontmatter, not `VERSION` files.** The registry's Project Practices table checks `version:` in `SKILL.md` YAML frontmatter. When the two disagree, the manifest follows frontmatter; `VERSION`-file drift is logged as a separate skill bug rather than papered over in the manifest.
<!-- /STRATEGY CONTENT -->

## Todos

- [x] Locate registry clone and inspect commit `2456f5a`
- [x] Confirm merge safety (branch base, conflict check)
- [x] Cross-check all 24 manifest version rows against actual skill state
- [x] Merge PR branch into `main` as `#163` (no-ff)
- [x] Apply corrections on `main` (3 stale versions + symlink annotation)
- [x] Commit corrections (`366bf1f`)
- [x] Resolve agents/ symlink question — convert 14 registry advisor copies to symlinks
- [x] Push `main` to origin

## Changelog

- 2026-05-13 — Created. Reviewed `2456f5a`; confirmed clean merge; merged PR branch into `main` as `132b41f` (no-ff). Identified 3 stale versions + 1 structural inaccuracy to correct in a follow-up commit.
- 2026-05-13 — Applied version corrections on `main` as `366bf1f` (secops 7→8, dhf-manifest 9→12, trace-matrix 7→8).
- 2026-05-13 — User flagged agents/ should be symlinks. Confirmed: consumer-project `.claude/agents/` already symlinks (advisors v1.1.0); but registry repo `hitachi/agents/` had 14 advisor files committed as real copies (only project-secops.md was a symlink). Verified all 14 byte-identical to `skills/advisors/agents/` canonical, converted to symlinks (git mode 100644→120000), manifest updated to "symlinks". Committed `db3df17`.
- 2026-05-13 — Pushed `main` to origin (`255eed8..db3df17`). No open GitHub PR existed for `skills/manifest-refresh-2026-05-12`; the branch is now fully merged into `main`. Task complete.

## Notes

- Registry repo: `/Users/ben.xavier/Documents/demos/hitachi`
- Resume command: `bash .claude/hooks/task-activate.sh add <UUID-from-denial> 057`
