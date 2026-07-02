# 059 — Codify scratch-and-tmp convention in the task skill

**ID**: 059
**Created**: 2026-05-15
**Status**: Complete
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: Medium

---

## PERMANENT RULES (do not remove)

This task document is the **session-recovery point** for this work. If the current session drops, is compacted, or ends, the next session must be able to load **this file alone** and continue where we left off. That is only possible if the doc is kept current in-flight.

1. **Update at every meaningful checkpoint (HARD RULE).** After each meaningful unit of work — a converted/adopted doc, a committed change, a launched batch, a completed phase, a decision, a discovered blocker, a design pivot — update this task doc:
   - tick the relevant Todo checkbox
   - add a dated Changelog line naming the concrete artifact (commit SHA, file path, decision, blocker)
   - update any progress counts/tables in Goals
2. **Phase-end batching is OK; drift-batching is not.**
3. **A commit is not a substitute.**
4. **Resume-ready before any session boundary.**
5. **Capture strategy + lessons as they happen.**

Success test for this doc: a fresh Claude session, given only this file, can re-enter the work without asking the user "what were we doing?"

## Goals

_Codify the scratch / tmp convention so it is enforced and discoverable, closing an active drift bug in PDLC-DEMO._

- Make the **task skill** the single owner of the scratch-and-tmp convention. The `create` action already creates `tasks/<person>/_scratch/`; the `setup` action will additionally install the convention: gitignore entries, the `.claude/rules/scratch-and-tmp.md` rule file, and the CLAUDE.md auto-loaded-rules pointer.
- Fix the active drift in PDLC-DEMO: `tasks/ben/_scratch/` exists (task skill created it) but `.gitignore` has no `_scratch/` entry, CLAUDE.md has no scratch section, and the rule file does not exist — so scratch content would silently get committed.
- Push the task-skill change upstream to the hitachi registry so the convention propagates to all projects.

## Background

Reviewed sister project `arthrex-pccp`: it codifies this in `.claude/rules/scratch-and-tmp.md` (auto-loaded every session by Claude Code), references it from a "Auto-loaded rules (do not restate here)" section in CLAUDE.md, and gitignores `_scratch/` project-wide. PDLC-DEMO has none of this infrastructure yet.

**Decision (user, 2026-05-15):** the task skill owns the *whole* convention — gitignore entries + the `.claude/rules/scratch-and-tmp.md` rule file + the CLAUDE.md pointer are all installed by the task skill's `setup` action. Rationale: `_scratch/` only exists because tasks exist; keeping one owner is simpler and matches the "each rule gets owned by its most-related skill" plan. Tradeoff accepted: the rule's OS-`/tmp` half is generic hygiene, not strictly task-scoped.

<!-- STRATEGY CONTENT: operations, repo-governance -->
**Rule-ownership model.** Auto-loaded `.claude/rules/` files are owned by their most-related skill, which installs them during its `setup` action. scratch-and-tmp → task skill. This is the per-rule disposition pass the user is running ("find the right home for each type of rule"); other rules (sentinel-blocks, readme-before-write, git-workflow, etc.) will be dispositioned separately.
<!-- END STRATEGY CONTENT -->

<!-- LESSONS LEARNED: skill-architecture -->
**Skill-shipped rules go under `skills/<name>/rules/`, never a registry-root `rules/` namespace.** `/sync-skills` scans only `skills/` and `agents/`. Agents get a symlink-vs-content false positive (ben/029) because they have a registry-root `agents/` namespace *and* are symlink-installed into `.claude/agents/` — a symlink lands inside a scanned namespace. Keeping a rule's canonical source inside the owning skill means sync-skills only ever diffs the real file; the `.claude/rules/` symlink is invisible to it, like `.claude/hooks/` symlinks.
**Why:** avoids reproducing the ben/029 false positive for a whole new artifact class.
**How to apply:** any future skill-shipped, symlink-installed artifact should keep its canonical source inside the skill dir, not at a new registry-root namespace.
<!-- END LESSONS LEARNED -->

## Todos

- [x] Read `skill-creator` SKILL.md before modifying the task skill
- [x] Add the convention install to the task skill `setup` action (gitignore + rule file + CLAUDE.md pointer)
- [x] Update the task skill `create` action / SKILL.md to reference `.claude/rules/scratch-and-tmp.md` instead of the non-existent "CLAUDE.md § Personal Scratch & System tmp"
- [x] Bump task skill version + changelog
- [x] Apply the convention to PDLC-DEMO now (run/replay `setup`): create `.claude/rules/scratch-and-tmp.md`, add `_scratch/` gitignore entries, add CLAUDE.md pointer section
- [x] Push the task-skill change upstream via `/sync-skills push` — hitachi PR #164 (awaiting review)

## Changelog

- 2026-05-15: Task created. Reviewed arthrex-pccp codification; user decided task skill owns the full convention (all-in-task-skill).
- 2026-05-15: Task skill v24 → v25. Added `setup` step 13 (idempotent install of rule file + gitignore patterns + CLAUDE.md pointer); bundled rule as `templates/scratch-and-tmp.md`; `create` step 3 now points at `.claude/rules/scratch-and-tmp.md`; Supporting Files + README Version History updated. Applied to PDLC-DEMO: `.claude/rules/scratch-and-tmp.md` created, `_scratch/` + `**/_scratch/` added to `.gitignore` (verified `git check-ignore tasks/ben/_scratch` passes), "## Auto-loaded rules" section appended to CLAUDE.md. Active drift bug closed.
- 2026-05-15: **Symlink rework.** Moved the rule source from `templates/scratch-and-tmp.md` to a skill-owned `rules/` dir (`.claude/skills/task/rules/scratch-and-tmp.md`); `setup` step 13 now creates a symlink `.claude/rules/scratch-and-tmp.md` → `../skills/task/rules/scratch-and-tmp.md` instead of a copy (auto-updates on `/sync-skills pull`; fork-to-customize). PDLC-DEMO's copy replaced with the symlink (verified it resolves). skill-creator v6 → v7: documented the `rules/` subdir + `.claude/rules/` symlink-install pattern in the Required Skill Structure tree and Setup action pattern.
- 2026-05-15: Committed ben/059 work as project commit `3d552b8` (9 files). Note: a background process had switched the repo off `main` onto branch `ben/058-advisors-test-runner` and committed ben/058 (`a449d2e`), sweeping up the 059 index row — so `3d552b8` sits on `ben/058-advisors-test-runner`, not `main`. Pushed task v25 + skill-creator v7 to hitachi as **PR #164** (`sync/pdlc-demo-scratch-tmp-convention-2026-05-15`, hitachi commit `04c992a`), PR-only, awaiting review. Sync-log entry recorded.
- 2026-05-15: **sync-skills — no change needed.** Read `sync-skills/SKILL.md` + `scripts/sync.sh`: it scans only `skills/` and `agents/` (`sync.sh:387,405`; refuses other paths at `:67`). The rule's canonical source is a *real file* at `skills/task/rules/scratch-and-tmp.md` — diffed normally. The `.claude/rules/` symlink is a local install artifact sync-skills never scans (same as `.claude/hooks/` symlinks). No symlink-vs-content false positive arises; the ben/029 bug is specific to `agents/` (registry-root namespace + symlink install). Documented this rationale in skill-creator's Setup action pattern.

## Notes

Sister-project reference: `../arthrex-pccp/.claude/rules/scratch-and-tmp.md`, and the CLAUDE.md "Auto-loaded rules (do not restate here)" section (~line 232).

