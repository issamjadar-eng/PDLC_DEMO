# 068 — Post-Pull Audit Cleanup (2026-05-30)

**ID**: 068
**Created**: 2026-05-30
**Status**: In Progress
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: Medium
**Spawned from**: ben/067's `/best-practices audit` (11 FAILs surfaced)

---

## PERMANENT RULES (do not remove)

Same as standard task doc — keep updated at every checkpoint; phase-end batching OK; resume-ready before any session boundary.

## Goals

Address the 6 substantive `/best-practices audit` FAILs that pre-date today's hitachi pull but were surfaced cleanly by the audit. All are non-blocking but bring the project to a clean baseline before the next sync cycle. User direction: "proceed with the fixes, do as much as you can without prompting."

- **G1** — Remove stale `src/` reference from CLAUDE.md folder tree (FAIL #6).
- **G2** — Fix CLAUDE.md heading depth (`## For Claude` → `### For Claude`) and add the `Update as you go (HARD RULE` task-discipline section (FAIL #2).
- **G3** — Add the canonical 8-entry `strategy_domains:` block to `project.yml` (FAIL #1). Source: `.claude/skills/strategy/SKILL.md` Domain Registry + init-briefs sentinel-rendered tables (the 8 strategy docs in `docs/project/strategies/` already match).
- **G4** — Resolve lessons-ledger bootstrap state + add `## Lesson Records` section to `tasks/README.md` (FAIL #5).
- **G5** — Scaffold `docs/_analysis/README.md` + decide whether to seed a first component (FAIL #4 from gap-analysis v2).
- **G6** — Scaffold 20 missing `README.md` files (FAIL #3): `docs/project/dhf-manifest/`, `docs/project/milestones/`, `docs/project/console/` + 10 per-DHF console subfolders, 7 `docs/internal/source-md/<cat>/templates/` folders.

After all six: re-run `/best-practices audit` to confirm FAIL count dropped to (at most) the deferred ones, then commit + push.

## What's NOT in scope this session

- The two new categories surfaced by today's medtech-docs v30 pull (DHF `marketed_name`/`architecture_name` gap; `.taxonomy.yml` adoption) — those are content decisions deserving their own task.
- WARNs (12) — strategy content authoring, task-ref format mass-rewrite, leaf "Expected Content" sections, etc. — out of scope.

## Todos

- [x] G1 — CLAUDE.md src/ line removed (and `tasks/`, `commands/`, `rules/` added to the tree to match reality)
- [x] G2 — CLAUDE.md `### For Claude` heading depth (now H3 under new `## Operating Notes` H2) + `#### Ongoing task discipline` task-discipline section copied from medtech-docs template
- [x] G3 — `project.yml strategy_domains:` 8-entry block added (regulatory, commercial, architecture, development, testing, risk, postmarket, operations) with `scope_description` matching canonical strings
- [x] G3a — Strategy sentinels re-rendered cleanly via `render-sentinels.py` (all 3 targets, zero diffs against existing canonical content)
- [x] G4a — `/lessons assemble` delegated to subagent (running) — will remove the `awaiting-content` bootstrap marker
- [x] G4b — `tasks/README.md` `## Lesson Records` section added per `lessons` SKILL.md format
- [x] G5 — `docs/_analysis/README.md` scaffolded with subfolder-table sentinel; component subfolders left empty (created on first `/gap-analysis init` / `/reference-audit init`)
- [x] G6 — 20 missing READMEs scaffolded: `docs/project/{dhf-manifest,milestones,console}/` + 10 per-DHF console subfolders + 7 `docs/internal/source-md/<cat>/templates/` folders. `docs/project/console/README.md` subfolder-table sentinel rendered + DHF-purpose strings filled in.
- [x] `/lessons assemble` complete — 44 lessons staged across 26 source tasks; `<!-- Status: awaiting-content -->` marker removed; 0 records rolled up (no `/lessons record`-ing yet); 27 of 44 will fire the "untested staged lesson" rule on next `/lessons validate` (expected — first assembly)
- [ ] Re-run `/best-practices audit` to confirm FAIL count dropped
- [ ] Commit + push

## Changelog
- 2026-05-30: Task created. Cleanup begins.
- 2026-05-30: **G1-G6 deployed.** CLAUDE.md cleaned (src/ removed, For Claude H3, task-discipline section); project.yml strategy_domains added (8 entries with scope_description); strategy sentinels re-rendered clean; tasks/README.md Lesson Records section added; docs/_analysis/README.md scaffolded; 20 READMEs scaffolded (3 unique parents + 10 console subfolders + 7 templates subfolders). Awaiting `/lessons assemble` subagent + re-audit confirmation.
- 2026-05-30: **G4a complete.** `/lessons assemble` finished: 44 lessons staged across 26 source tasks; bootstrap marker removed; 0 records (no `/lessons record`-ing yet — 27 untested-staged warnings expected on next validate). Subagent also flagged an upstream skill bug: SKILL.md `seq` definition is per-block but tasks with multiple `<!-- LESSONS LEARNED -->` tags (019, 034, 044, 047, 049) need across-task sequential numbering for ID uniqueness — subagent applied that interpretation. Worth a follow-up to clarify in the lessons skill SKILL.md when next revised.
