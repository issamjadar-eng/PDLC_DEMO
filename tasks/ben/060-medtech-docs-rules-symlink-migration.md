# 060 — Migrate readme-before-write + sentinel-blocks rules into medtech-docs (symlink pattern)

**ID**: 060
**Created**: 2026-05-15
**Status**: In Progress
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: Medium

---

## PERMANENT RULES (do not remove)

This task document is the **session-recovery point** for this work. Keep it current in-flight.

1. **Update at every meaningful checkpoint (HARD RULE)** — tick todos, add dated Changelog lines naming concrete artifacts.
2. **Phase-end batching is OK; drift-batching is not.**
3. **A commit is not a substitute.**
4. **Resume-ready before any session boundary.**
5. **Capture strategy + lessons as they happen.**

## Goals

Make `medtech-docs` the symlink-pattern owner of the `readme-before-write` and `sentinel-blocks` rules — the second rule-disposition batch after [[059]] (task skill → scratch-and-tmp).

- Convert medtech-docs `init` from the **copy** pattern (Checks 3 & 4) to the **symlink** pattern established in task v25 + skill-creator v7: canonical rule source under `skills/medtech-docs/rules/`, `.claude/rules/<rule>.md` symlinked to it.
- Create the bundled rule sources: `rules/readme-before-write.md` (currently inlined as "standard rule content" in Check 3 — no file) and `rules/sentinel-blocks.md` (currently `templates/rule-sentinel-blocks.md` — relocate).
- Update medtech-docs README design docs to cover the design/reasoning (why rules are skill-owned + symlinked) and how `init` installs them.
- Install in PDLC-DEMO: symlink both rules into `.claude/rules/`.
- Push upstream to hitachi.

## Background — current state (recon 2026-05-15)

medtech-docs v23 **already owns both rules** but with the pre-symlink copy pattern:
- `init` Step 2c **Check 3** — creates `.claude/rules/readme-before-write.md` from "standard rule content" (no bundled file).
- `init` Step 2c **Check 4** — copies `templates/rule-sentinel-blocks.md` → `.claude/rules/sentinel-blocks.md` verbatim.
- `render-sentinels.py` exists at `.claude/skills/medtech-docs/scripts/` (20 KB).
- PDLC-DEMO's `.claude/rules/` currently has only `scratch-and-tmp.md` (from [[059]]) — neither rule installed here yet; PDLC-DEMO docs/CLAUDE.md contain no live `AUTO:STRUCTURE` sentinels.

<!-- STRATEGY CONTENT: operations, repo-governance -->
**Rule-ownership model, batch 2.** `readme-before-write` + `sentinel-blocks` → `medtech-docs` (owns the `docs/` tree + README scaffolding + `render-sentinels.py`). Same symlink-install pattern as task v25. sentinel-blocks' real coupling is to `/best-practices fix` (calls the renderer), not Confluence — origin traced to sister-project task 072 (README drift detection + auto-remediation), not change-control. Remaining unowned rules: `claude-md-references`, `audit-wiring-before-adding-fields` (tier-2 candidates), `git-workflow` (tier-3, project-authored, never registry).
<!-- END STRATEGY CONTENT -->

## Todos

- [x] Read medtech-docs SKILL.md (init Step 2c, README Convention, Supporting Files, render passes) end-to-end
- [x] Create `skills/medtech-docs/rules/readme-before-write.md` (canonical source)
- [x] Relocate `templates/rule-sentinel-blocks.md` → `rules/sentinel-blocks.md`
- [x] Rewrite init Checks 3 & 4 to symlink (skip/repoint/leave-fork), not copy
- [x] Update SKILL.md Supporting Files + all references; bump version
- [x] Update medtech-docs README design docs — design/reasoning + how init installs the rules
- [x] Install in PDLC-DEMO: symlink both rules into `.claude/rules/`
- [x] Push upstream to hitachi — hitachi PR #165 (awaiting review)

## Changelog

- 2026-05-15: Task created. Recon: medtech-docs v23 already owns both rules via copy-pattern Checks 3 & 4; this task upgrades to the symlink pattern.
- 2026-05-15: **medtech-docs v23 → v24.** Created `rules/readme-before-write.md` (canonical source — was inlined in Check 3 with no file). `git mv templates/rule-sentinel-blocks.md → rules/sentinel-blocks.md`; fixed a project-leak in it (`task 072` reference removed — skill files stay project-agnostic). Rewrote `init` Step 2c Checks 3 & 4 to symlink `.claude/rules/<rule>.md` → `../skills/medtech-docs/rules/<rule>.md` (skip/repoint/leave-fork idempotency) instead of copy/inline. SKILL.md Supporting Files table + intro updated; version bumped. README gained design section "Auto-Loaded Rules — Skill-Owned and Symlinked" + v24 changelog entry. Installed in PDLC-DEMO: `.claude/rules/readme-before-write.md` + `.claude/rules/sentinel-blocks.md` symlinks created, both resolve. `.claude/rules/` now holds all three rules (scratch-and-tmp from [[059]] + these two).
- 2026-05-15: Committed project-side as `3985e0a`, pushed to `origin/main`. Pushed medtech-docs v24 to hitachi as **PR #165** (`sync/pdlc-demo-medtech-docs-rules-symlink-2026-05-15`, commit `b7c0874`), PR-only, awaiting review. Push included a rename (`templates/rule-sentinel-blocks.md` → `rules/sentinel-blocks.md`); old path removed via manual `git rm` on the hitachi branch since `push-stage` only copies. Sync-log recorded. **Task work complete pending PR review.**
