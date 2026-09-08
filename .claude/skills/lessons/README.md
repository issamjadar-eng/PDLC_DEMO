# lessons — Design & Architecture

This document is not loaded by Claude during normal skill operation — it exists for human understanding.

For skill usage and instructions, see `SKILL.md`.

## Best Practices

<!-- Read by /best-practices skill to audit project setup -->

| Check | How to Verify | Severity |
|-------|--------------|----------|
| Lessons skill installed | `.claude/skills/lessons/SKILL.md` exists | Required |
| Ledger template installed | `.claude/skills/lessons/templates/lessons-ledger.md` exists | Required |
| Ledger initialized | `tasks/lessons-ledger.md` exists and does NOT contain `<!-- Status: awaiting-content -->` | Required |
| CLAUDE.md references ledger | `CLAUDE.md` contains a reference to `tasks/lessons-ledger.md` in a session-load or mandatory-load section | Required |
| Ledger structure correct | `tasks/lessons-ledger.md` has `## Staged`, `## Promoted`, and `## Archived / Superseded` section headings | Required |
| Tasks README documents the convention | `tasks/README.md` contains the `## Lesson Records` format example | Required |
| No orphan records | Every record in task docs references a lesson ID that exists in some source task | Recommended |
| Records live in task docs | `tasks/lessons-ledger.md` Record tables are not edited directly (no git blame on Record table rows) | Recommended |
| Ledger freshness | `<!-- Last assembled -->` date is within 7 days of the most recent task doc modification | Recommended |
| Lessons assembly is current (monthly cadence) | `<!-- Last assembled -->` date in `tasks/lessons-ledger.md` is within 30 days. The team-wide training wheel replacing the retired per-turn capture hooks (task ben/100). Fix: run `/lessons assemble`; review staged lessons with `/lessons promote` when any are ready for their permanent home. | Recommended |
| No noisy lessons | No staged lesson has >3 `false-positive` or >2 `challenged` in 30 days | Recommended |

## Changelog

- 5 (2026-09-08): **Pre-check pointer to `scan_tags.py`.** The `scan` action now points at the strategy skill's deterministic tag lint (shared grammar) so malformed `<!-- LESSONS LEARNED` tags surface before assembly instead of being silently skipped. No parser change.

- 2 (2026-04-20): **Update task-gate state file path references from `.claude/state/active-tasks-{session_id}.txt` to `.state/active-tasks-{session_id}.txt`** (task ben/083). Doc-only change — `/lessons record` uses the task-skill's state file by path; relocating the path source in step 4 of the `record` action keeps the instructions accurate. No code change to the `record` flow itself.
  **Post-update:** No action required. The path references are documentation; `/lessons record` reads `printenv CLAUDE_SESSION_ID` and joins against the path at runtime, which will follow task-skill v18's new location automatically.
- 1 (2026-04-12): Initial version — 9 actions (init, scan, assemble, record, diff, validate, list, show, promote). Ledger with Staged/Promoted/Archived sections. Two-pass assembly (lessons + records). Lesson IDs in `L-<task_folder>-<NNN>-<seq>` form. Record format in source task docs as source of truth. Four outcome types (applied, exception, challenged, false-positive) distinguishing "lesson held" from "lesson may be wrong." Interactive promote with evidence review. Seven promotion destinations (skill, claude-md, agent, rule, glossary, standard, readme). Best-effort Claude detection at decision time. Close-out reflection prompt via `/task update Complete`. See task 036.
