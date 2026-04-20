# 019 — Digest Skill (daily briefing + project CHANGELOG)

**ID**: 019
**Created**: 2026-04-20
**Status**: Complete
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: Medium

---

## Goals

New `/digest` skill that produces two artifacts:

1. **Morning briefing** — ephemeral markdown digest printed at SessionStart, throttled to once per 12h per user (keyed by `git config user.email`). Covers commits since last-shown, grouped by author, plus a "Pay attention" section scoped to structural diffs (`CLAUDE.md`, `project.yml`, `.claude/rules/**`), skill updates (version bumps in `.claude/skills/*/SKILL.md`, new skills, new `.claude/sync-log.md` entries), and project-level changes (`docs/project/strategies/**`, `docs/project/submissions/**`, new DHF folders).
2. **Project CHANGELOG.md** — user-invoked append to a persistent `CHANGELOG.md` at repo root. First run does a full retrospective scan using a significance heuristic (commit subject matches `task NNN:` OR touches trigger paths) and groups by theme (Skills / Tasks Completed / Project Structure / Documentation). Each section is dated `## YYYY-MM-DD HH:MM — <title>`; subsequent runs pick up from the last dated header as the since-cursor.

Natural-language aliasing: `/digest` is invokable when the user says "update the project changelog", "build the changelog", "what changed today", "morning briefing", etc. — triggers listed verbatim in the skill's YAML description so they're always in Claude's triggering context.

## Todos

- [x] Scaffold `.claude/skills/digest/` with SKILL.md, README.md, VERSION
- [x] Write `scripts/digest.py` — daily-briefing aggregation
- [x] Write `scripts/build_changelog.py` — CHANGELOG.md appender with retrospective-capable first run
- [x] Write `hooks/session-briefing.sh` — SessionStart hook with 12h per-user throttle
- [x] Write `.claude/skills/medtech-docs/templates/changelog-project.md` — seed template (local delta)
- [x] Run `/digest setup` — hook symlinked, registered, CHANGELOG.md seeded, `digest` added to approved_skills
- [x] Run `/digest log --retrospective` — 32 significant commits captured, 4 themes, written to CHANGELOG.md
- [x] Verify daily briefing triggers + is correctly throttled

## Outcome

Digest skill v1 shipped. Two actions, one shared git-log core:

- `/digest daily` — fired by `.claude/hooks/session-briefing.sh` SessionStart hook, throttled to once per 12h per user (email-keyed state at `.claude/state/briefing-last-shown-<slug>.txt`). Emits a markdown digest grouping commits by author plus a "Pay attention" section scoped to Structural / Skill updates / Project-level paths. Verified working end-to-end: first invocation emits digest + stamps state, second invocation silently skips.
- `/digest log` — user-invoked `CHANGELOG.md` appender with retrospective-capable first run. Uses the topmost `## YYYY-MM-DD HH:MM UTC` header in `CHANGELOG.md` as the since-cursor on subsequent runs. Significance heuristic: `task NNN` subject ref OR trigger path hit OR SKILL.md version bump OR new skill/DHF directory. The first retrospective run captured 32 significant commits across Skills (15), Tasks Completed (1), Tasks (14), Project Structure (2).

Natural-language triggering works — the YAML `description` includes trigger phrases like "update the project changelog", "what changed today", "morning briefing" so Claude recognizes the alias without an explicit `/digest` invocation.

Bug fixed mid-build: the retrospective flag was silently overridden when a bootstrap-seeded `## YYYY-MM-DD` header existed in `CHANGELOG.md`. The fix respects `--retrospective` explicitly — full history scan regardless of headers. Caught on first live test run against PDLC_DEMO.

Local only. Upstream push to hitachi is a follow-up (both the `digest` skill itself and the `medtech-docs` `changelog-project.md` template addition).

<!-- STRATEGY CONTENT: architecture, skill-design, activity-summarization -->

**Strategy — Two-surface one-skill for overlapping aggregation logic.**

Principle: When two user-facing artifacts share the same data pipeline (here: `git log` since cutoff + path/subject filtering + grouping), combine them as two actions under one skill rather than splitting into two separate skills. Tradeoff analysis produced at design time: shared core code, single `approved_skills` entry, single audit surface — vs. perfectly-named skills with duplicated implementations.

Why: Splitting would produce two SKILL.md files, two Best Practices sections, two setup actions, and two places where the significance filter needs to stay in sync. The cost of a slightly overloaded skill name is outweighed by the cost of maintaining the same logic in two places.

How to apply: When two proposed skills share >60% of their core logic and one is merely a different output format or timing of the other, merge them. If they diverge later (e.g., one needs an LLM and the other stays mechanical), splitting at that point is cheap — the shared code becomes a `shared/` module.

<!-- LESSONS LEARNED: hook-testing, state-file-patterns, retrospective-bootstrap -->

**Lesson — Bootstrap headers can poison "since-cursor" logic on first run.**

Why: The `medtech-docs` CHANGELOG.md template seeded the file with `## YYYY-MM-DD 00:00 UTC — Project changelog initialized`. The `find_last_dated_header` function correctly found this header and used it as the since-cursor, which meant `/digest log --retrospective` only saw commits after midnight today — 2 commits instead of the expected 32.

How to apply: When a skill uses "the most recent dated header" as a since-cursor, the `--retrospective` / "first run" flag must force a full scan regardless of what the file contains. A bootstrap seed is not the same as a real entry, but the parser can't tell them apart structurally. The fix is explicit: `if retrospective: since = None` takes precedence over auto-discovery. Caught on live test run, not in a unit test — the class of bug where a pristine-but-nonempty file defeats an "is empty?" check.

## Changelog

- 2026-04-20: Task created to cover the digest skill build
- 2026-04-20: Skill v1 complete. Both actions verified on PDLC_DEMO. CHANGELOG.md seeded and populated with retrospective. Bootstrap-header since-cursor bug caught + fixed mid-build. Moved to Complete.
