# Best Practices Skill — Design & Architecture

This document describes the design decisions behind the best-practices skill. It is not loaded by Claude during normal skill operation — it exists for human understanding.

For skill usage and instructions, see `SKILL.md`.

## Overview

The best-practices skill audits project setup against a two-tier check system: shared practices from a remote registry and local practices defined by each installed skill. It also syncs skill versions against the registry.

## Role in the Ecosystem

best-practices is the **project auditor** — it validates that the project is set up correctly without modifying anything.

```
/best-practices audit
  ├─ Fetch registry manifest → project-level checks
  ├─ Scan local skills → skill-specific checks
  └─ Report: PASS / FAIL / WARN per check
```

## Dependencies

| File | Required by | Purpose | How to create |
|------|-------------|---------|---------------|
| `project.yml` | Privacy/security checks | Team roster, gitignore patterns | `/medtech-docs init` or create manually |
| `.gitignore` | Security checks | Verify secret/PHI patterns | Create manually |
| `setup.md` | Onboarding checks | Verify training opt-out, 2FA docs | `/medtech-docs init` or create manually |
| `CLAUDE.md` | Project checks | Verify task-first workflow, skill loading | Create manually |

When a dependency is missing, the audit reports it as a FAIL with guidance on how to create it.

## Key Design Decisions

### Two-Tier Check System

```
Registry (remote)              Local skills (project)
  ├─ Project-level checks        ├─ task skill checks
  ├─ CLAUDE.md exists            ├─ medtech-docs checks
  ├─ Glossary exists             ├─ best-practices own checks
  └─ ...                         └─ (any skill with ## Best Practices)
```

**Registry checks** are universal — they apply to any project using our skill ecosystem. **Local checks** are skill-specific — each skill defines its own in a `## Best Practices` table.

This means adding a new skill with checks automatically extends the audit without modifying best-practices itself.

### Registry Location

The registry repo is configured in `project.yml → registries[]`. Previously it was hardcoded in the skill — this was refactored in task 024 to make skills portable across organizations.

Fallback behavior: if the registry is unreachable, the audit runs using local checks only.

### Sync Action

`/best-practices sync` compares installed skill versions against the registry manifest. Reports: up to date, update available, not installed, local only. This is the skill update discovery mechanism — it doesn't auto-update, just informs.

## Key Design Decisions (continued)

### Best Practices in README.md, not SKILL.md

The `/best-practices` audit scans `README.md` files (not SKILL.md) for `## Best Practices` tables. This means health-check metadata never loads into Claude's context during skill execution — SKILL.md is loaded on every trigger while README.md is never auto-loaded. Each skill's own Best Practices table lives in its README.md.

## Best Practices

<!-- Consumed by /best-practices audit -->

| Check | How to Verify | Severity | Scope |
|-------|--------------|----------|-------|
| Team roster exists | `project.yml` exists in project root with `team:` section containing `active:` and `inactive:` lists | Required | shared |
| Team roster has active members | `project.yml` `team.active` list contains at least one entry with a `github:` field | Required | shared |
| .gitignore blocks secrets | `.gitignore` contains patterns for `.env`, `*.pem`, `*.key`, `credentials.json` | Required | shared |
| .gitignore blocks PHI | `.gitignore` contains patterns for patient/clinical data (e.g., `**/phi/`, `*.hl7`) | Required | shared |
| Setup guide covers training opt-out | `setup.md` contains instructions to disable Claude training on user data | Required | shared |
| Setup guide covers GitHub 2FA | `setup.md` contains instructions to enable GitHub two-factor authentication | Required | shared |
| Setup guide covers conversation hygiene | `setup.md` contains guidance on Claude conversation privacy and data awareness | Recommended | shared |
| Setup guide covers integration awareness | `setup.md` contains guidance on MCP/integration data flow and account usage | Recommended | shared |
| Agent design principles documented | `.claude/skills/shared/agent-design-principles.md` exists | Required | shared |
| Per-skill agents installed as symlinks | For every `.claude/agents/<name>.md` where the same basename exists under any `.claude/skills/*/agents/<name>.md`, the `.claude/agents/` entry must be a symlink pointing at the skill-owned source (verify via `test -L` and `readlink`). Regular files with no matching skill source are standalone agents and are exempt; regular files that DO have a matching skill source are drift candidates (project forks must be documented in `.claude/sync-log.md` to pass). | Required | shared |
| Evaluative skills document detection tiers | Every `.claude/skills/*/SKILL.md` that contains agent prompts (has an `agents/` subdirectory) or performs conflict detection / comparison / routing documents both programmatic (Tier 1) and semantic (Tier 2) evaluation approaches, or explicitly states why only one tier applies | Recommended | shared |
| Security hook installed | `.claude/settings.json` SessionStart hooks array contains a command referencing `security-assert.sh` | Required | shared |
| Secops agent exists | `.claude/agents/project-secops.md` exists | Required | shared |
| Project manifest has security policy | `project.yml` contains a `security:` section with `approved_email_domains` and `approved_skills` lists | Required | shared |
| Project has at least one DHF | `project.yml` contains a `dhfs:` list with at least one entry, and every entry's `path` field resolves to an existing folder under `docs/project/dhfs/` | Required | cross-cutting |
| DHF leaf names are unique | For every entry in `project.yml` `dhfs[]`, the last segment of `path` is unique across the list (case-sensitive). Enforced at add-dhf time; re-verified here to catch manual edits. | Required | cross-cutting |
| Platform DHFs have children | For every DHF with `regulatory: mixed`, at least one other `dhfs[]` entry has `parent` pointing to it. | Required | cross-cutting |
| Unreferenced DHFs flagged | For every `dhfs[]` entry with `regulatory` ∈ {`in-development`, `cleared`}, check whether it is listed in at least one composition manifest under `submissions/*/composition-manifest.md`. Skip entries with `regulatory: concept` or `regulatory: mixed`. Report unreferenced entries as WARN. | Recommended | cross-cutting |
| Composition manifests exist | If `project.dhfs[]` is non-empty AND `submissions/*/composition-manifest.md` glob returns zero matches, emit project-level WARN. | Recommended | cross-cutting |
| README Structure table matches folders | For every `docs/**/README.md`, if the README contains a `## Structure` or `## Subfolders` section with a markdown table, compare first column values to actual child subdirectories. Flag rows whose folder doesn't exist and on-disk subfolders not in the table. | Recommended | shared |
| CLAUDE.md Project Structure tree matches filesystem | Project root `CLAUDE.md` contains a `## Project Structure` section with a fenced code block. Compare top-level entries to actual top-level directories. | Recommended | shared |
| CLAUDE.md DHF table matches project.yml | Project root `CLAUDE.md` contains a DHF/module table. First-column leaf values should correspond to `project.yml` `dhfs[].leaf` fields. Classification columns must match `dhfs[].classification`. | Required | shared |
| CLAUDE.md team references match project.yml | If project root `CLAUDE.md` lists team members by name, every person named must have a matching entry in `project.yml` `team.active[]`. | Recommended | shared |
| `_scratch/` pattern in .gitignore | `.gitignore` contains a `_scratch/` line (or `**/_scratch/`) so personal scratch folders never enter version control. See CLAUDE.md § "Personal Scratch & System tmp" and `tasks/README.md` § "Personal `_scratch/` Folder". | Recommended | shared |
| No project-root `_scratch/` | `_scratch/` directory does not exist at the project root. The sanctioned location is `tasks/{person}/_scratch/` only — anything cross-cutting belongs in a real, committed doc, not scratch. Verify via `test ! -d _scratch`. | Recommended | shared |
| No tracked files under any `_scratch/` | `git ls-files` returns no paths matching `_scratch/` or `**/_scratch/`. Personal scratch must never be committed. If files appear here, the fix is to `git rm --cached` them and ensure the gitignore pattern is in place. | Recommended | shared |
| No project-tree `tmp/` | No `tmp/` directory exists at the project root or under `tasks/`. Claude uses the OS-provided system `/tmp` (outside the repo) for transient intermediates. Verify via `test ! -d tmp` and `find tasks -maxdepth 2 -type d -name tmp` returning empty. | Recommended | shared |
| Skill content is project-agnostic | No file under `.claude/skills/**` or `.claude/agents/**` contains project-specific names. A name is project-specific if it identifies one company, device, or codename rather than a generic placeholder. Build a project-specific patterns list from `project.yml` (`project.name`, `project.device_family`, any company-specific identifiers in `team.active[].email` domain) and `grep -ri` the patterns across `.claude/skills/` and `.claude/agents/`. Generic placeholders (`MedTech Project`, `MedTech Company`, `<device>`, `PROJECT-1234`) are fine. Per skill-creator § "Project-Agnostic Authoring (HARD RULE)". | Required | shared |
| Skill changelogs are skill-scoped | For every `.claude/skills/*/README.md` `## Changelog` section, no entry contains: (a) project-specific names per the patterns above, (b) project task references (`<task_folder>/NNN` form, e.g. `ben/118`, or bare `task NNN` followed by description). Skill changelogs describe skill changes only. Per skill-creator § "Changelog Format". | Recommended | shared |

## Changelog

<!--
Skill-scoped only. Each entry describes what changed in best-practices itself.
No project-specific names, no project task references.
-->

- 15 (2026-04-27): Added two Required/Recommended audit checks that enforce the project-agnostic-skill rule end-to-end: (1) `Skill content is project-agnostic` — Required, scans `.claude/skills/**` and `.claude/agents/**` for project-specific patterns derived from `project.yml`; (2) `Skill changelogs are skill-scoped` — Recommended, scans `.claude/skills/*/README.md` `## Changelog` sections for project names and task references. Pairs with skill-creator v5's explicit § "Project-Agnostic Authoring (HARD RULE)" and § "Changelog Format" rules. Together: skill-creator defines the rule for new skills, best-practices catches drift in existing skills.
- 14 (2026-04-24): Added 4 warn-only personal-scratch checks (`_scratch/` pattern in `.gitignore`, no project-root `_scratch/`, no tracked files under `_scratch/`, no project-tree `tmp/`). Backs the convention codified in task ben/112 — `tasks/{person}/_scratch/` is the only sanctioned scratch location, gitignored and user-managed; Claude uses the OS `/tmp` for transient intermediates.
- 13 (2026-04-23): **Move Best Practices and Changelog from SKILL.md to README.md** (task ben/095). `/best-practices` audit Step 2 now scans `README.md` (not `SKILL.md`) for `## Best Practices` tables. Updated "Skills are versioned" check to look for `## Changelog` in README.md. Updated Registry Format skill file format description. Updated two inline references from `SKILL.md ## Best Practices` to `README.md ## Best Practices` in the partition and scope-parsing steps. Saves ~47 lines from SKILL.md context on every skill trigger.
- 12 (2026-04-20): New `fix` action with strict three-tier safety model. Auto-remediates mechanical drift inside `<!-- AUTO:STRUCTURE -->` sentinels (Tier A). Tier B (CLAUDE.md) and Tier C (narrative drift) are flagged only — generates task document with proposed-fix checklist. Hard rules: never writes to CLAUDE.md, never writes outside sentinel blocks, never commits, never deletes files, never removes content.
- 11 (2026-04-20): Added 4 drift-detection checks for persistent structural docs (README Structure table, CLAUDE.md Project Structure tree, CLAUDE.md DHF table, CLAUDE.md team references).
- 10 (2026-04-16): Added Required check `Per-skill agents installed as symlinks`. Pairs with skill-creator v2 which mandates agent symlinks in every setup action.
- 9 (2026-04-13): Subagent dispatch implementation. Per-dhf and per-submission checks fan out to LLM subagent workers via the Agent tool. N=1 short-circuit optimization.
- 8 (2026-04-13): Unified DHF shape support. Added Scope column parsing, per-dhf/per-submission/cross-cutting iteration, multi-dhf grouped report format.
- 7 (2026-04-10): Added 3 security infrastructure checks.
- 6 (2026-04-09): Registry repo/path read from project.yml instead of hardcoded.
- 5 (2026-04-08): Exempt externally-sourced skills from versioning check.
- 4 (2026-04-02): Added privacy and security best-practice checks.
- 3 (2026-03-30): Migrated from .claude/commands/ to .claude/skills/. Updated scan logic to read .claude/skills/*/SKILL.md.
- 2 (2026-03-30): Added self-containment and versioning checks.
- 1 (2026-03-23): Initial version — audit, check, and sync actions against shared registry.
