# 072 — Install Anthropic frontend-design Skill

**ID**: 072
**Created**: 2026-06-01
**Status**: Complete
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: Medium

---

## PERMANENT RULES (do not remove)

This task document is the **session-recovery point** for this work. If the current session drops, is compacted, or ends, the next session must be able to load **this file alone** and continue where we left off.

1. Update at every meaningful checkpoint (HARD RULE).
2. Phase-end batching OK; drift-batching not.
3. A commit is not a substitute.
4. Resume-ready before any session boundary.
5. Capture strategy + lessons as they happen.

## Goals

- Pull Anthropic's public `frontend-design` skill from [`anthropics/skills`](https://github.com/anthropics/skills/tree/main/skills/frontend-design).
- Install it under `.claude/skills/frontend-design/` adapted to this project's skill-creator format (frontmatter shape, README split with `## Best Practices` + `## Changelog`, `## Supporting Files` table).
- Preserve Anthropic's Apache-2.0 LICENSE.txt verbatim and credit lineage in README.
- Add to `project.yml security.approved_skills`.
- Skill content stays project-agnostic (it already is — domain-neutral web UI guidance).

## Todos

- [x] Clone upstream and inspect (`/tmp/anthropic-skills/skills/frontend-design/`).
- [x] Create task doc and activate.
- [x] Write `.claude/skills/frontend-design/SKILL.md` in our format (4-field frontmatter, Supporting Files table, body verbatim).
- [x] Write `.claude/skills/frontend-design/README.md` with Lineage, Best Practices, Changelog.
- [x] Copy `LICENSE.txt` verbatim and pin upstream SHA in `.pinned-sha` (`da20c92`).
- [x] Add `frontend-design` to `project.yml security.approved_skills`.
- [x] Disambiguate from sibling `frontend-slides` (deck-only) — explicit note in SKILL.md description.
- [x] Commit + push: PR #29 merged to main (`6988209`).

<!-- STRATEGY CONTENT: development, tooling -->
**Decision**: Keep upstream skill name `frontend-design` despite sibling `frontend-slides`. They serve disjoint surfaces (slides vs general web UI) and their descriptions clearly differentiate; renaming would drift from upstream and impair future `/sync-skills`-style updates.
<!-- /STRATEGY CONTENT -->

## Resume

### In-flight artifacts
- Upstream clone at `/tmp/anthropic-skills/` (transient — safe to discard).
- No commits yet.

### First action on resume
1. Verify task is active for current session.
2. Write the three files under `.claude/skills/frontend-design/`.
3. Edit `project.yml`.

## Changelog
- 2026-06-01: Task created. Upstream inspected (42-line SKILL.md, Apache-2.0).
- 2026-06-01: Skill installed at `.claude/skills/frontend-design/` (SKILL.md 6.4KB, README.md 4.9KB, LICENSE.txt 10KB verbatim, .pinned-sha=`da20c92`). Added to `project.yml security.approved_skills`. Awaiting commit/push confirmation.
- 2026-06-01: PR #29 merged to main (`6988209`). Task closed.

