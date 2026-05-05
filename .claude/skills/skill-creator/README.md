# Skill Creator — Design & Architecture

This document describes the design decisions behind the skill-creator skill. It is not loaded by Claude during normal skill operation — it exists for human understanding.

For skill usage and instructions, see `SKILL.md`.

## Overview

The skill-creator is a meta-skill for creating, testing, and optimizing other skills. It provides a structured workflow from intent capture through evaluation and iteration, while enforcing project-specific conventions for self-contained, versioned skills.

## Lineage

Adapted from Anthropic's skill-creator (sourced from the Hitachi shared skills repo).

| Anthropic Original | Our Adaptation |
|---|---|
| YAML frontmatter: name, description | Added: version (integer), updated (date) |
| Skill structure: SKILL.md + optional resources | Required: README.md, Supporting Files table, Best Practices table, Changelog |
| No hook/agent management convention | Symlink pattern: hooks and agents live in skill; `.claude/hooks/` and `.claude/agents/` are symlink layers |
| No design doc requirement | README.md as design document per README Navigation Rule |
| Evaluation pipeline (grader, comparator, analyzer) | Kept intact — agents, scripts, eval-viewer, schemas |
| Description optimization loop | Kept intact — run_eval, run_loop, improve_description |
| Skill anatomy section | Extended with project structure conventions |

## Key Design Decisions

### Self-Contained Skills

Every skill is a self-contained directory. Hooks, agents, templates, scripts — everything lives inside the skill. The `.claude/hooks/` and `.claude/agents/` directories are just symlink layers that Claude Code discovers at runtime. This means:
- Updating a skill automatically updates its hooks and agents
- Skills can be moved, copied, or shared as directories
- No hidden dependencies on files outside the skill directory

### Symlink Pattern over Copies

We use symlinks instead of copies for hooks **and agents** because:
- Single source of truth (skill directory)
- No drift between source and the installed hook/agent
- Skill updates via `/sync-skills pull` propagate automatically
- Project forks (customizations) are explicit: convert symlink → regular file, and the divergence is visible to `/sync-skills check` and `/best-practices`
- WSL2 limitation (VS Code can't see symlinks) is acceptable since the source files are accessible through the skill directory

Registry-level `agents/` (at the hitachi repo root) is reserved for cross-skill agents that don't belong to any single skill. Per-skill agents ship under `skills/<name>/agents/`.

### Versioning

Integer versions (not semver) because skills iterate rapidly and the distinction between major/minor/patch isn't useful at this granularity. The changelog provides the detail.

### Best Practices as README Section

Every skill must declare health checks in its README.md. The `/best-practices` auditor scans `README.md` files (not SKILL.md) for `## Best Practices` tables. This means health-check metadata never loads into Claude's context during skill execution — README.md is never auto-loaded.

### README as Design Doc

The README.md serves as the skill's index layer (per README Navigation Rule) and as a design document. It explains **why** the skill works the way it does, which is information that doesn't belong in the operational SKILL.md.

## Dependencies

| File | Required by | Purpose |
|------|-------------|---------|
| `.claude/skills/` directory | Skill creation | Output directory for new skills |
| `.claude/hooks/register-hook.sh` | setup actions | Shared hook registration helper |
| `.claude/hooks/` directory | setup actions | Symlink target for skill hooks |
| `.claude/agents/` directory | setup actions | Symlink target for skill agents (Claude Code subagent discovery) |
| `.state/` directory (project root) | hook scripts | Runtime state files (relocated from `.claude/state/` in ben/083 to escape `.claude/**` sensitive-file guard) |

## Best Practices

<!-- Consumed by /best-practices audit -->

| Check | How to Verify | Severity | Scope |
|-------|--------------|----------|-------|
| New skill has SKILL.md | File exists with valid frontmatter | Required | shared |
| New skill has README.md | Design doc exists at skill root | Required | shared |
| Frontmatter complete | name, description, version, updated present | Required | shared |
| Best Practices table in README.md | README.md contains `## Best Practices` with table | Required | shared |
| Changelog in README.md | README.md contains `## Changelog` with entries | Required | shared |
| Supporting Files table | SKILL.md lists all bundled files | Required | shared |
| Hooks use symlinks | `.claude/hooks/` contains symlinks into `skills/*/hooks/`, not copies | Required | shared |
| Agents use symlinks | `.claude/agents/` contains symlinks into `skills/*/agents/`, not copies (forks excepted — documented in sync-log) | Required | shared |
| Setup action idempotent | Re-running setup doesn't duplicate hooks, agent symlinks, or hook registrations | Required | shared |
| SKILL.md under 500 lines | Progressive disclosure respected | Recommended | shared |
| Evals exist | `evals/evals.json` with test cases | Recommended | local |
| New schema fields justified | Before adding fields to a skill's catalog/manifest/sidecar schema, the SKILL.md or design doc states what was checked in `project.yml`, sibling skill outputs (taxonomy yamls, milestone yamls, evidence_layout, etc.), and adjacent SKILL.md docs. If the answer was already encoded there, the new field is replaced by a lookup against existing config. Justification is recorded inline. | Required | shared |

## Changelog

<!--
Skill-scoped only. Each entry describes what changed in skill-creator itself.
No project-specific names, no project task references — those go in the
project's tasks/ and commit history.
-->

- 5 (2026-04-27): Made the project-agnostic-authoring rule and the skill-scoped-changelog rule explicit in skill-creator. New § "Project-Agnostic Authoring (HARD RULE)" in SKILL.md prohibits project-specific names in `.claude/skills/**` and `.claude/agents/**`; says project values belong in `project.yml`/`docs/`/`tasks/`/`CLAUDE.md`. The `### Changelog Format` section in SKILL.md gained explicit ❌/✅ examples for what belongs in a skill changelog (skill capability/schema/bugfix changes — yes; project work, project names, project task IDs — no). The `templates/readme-skill.md` `## Changelog` section gained an HTML-comment instruction so new skills are born clean.
- 4 (2026-04-23): **Move Best Practices and Changelog from SKILL.md to README.md** (task ben/095). SKILL.md is loaded into context on every skill trigger; these sections are metadata for auditors/maintainers, not execution instructions. `/best-practices` audit Step 2 now scans `README.md` (not `SKILL.md`) for `## Best Practices` tables. Updated skill-creator conventions: Best Practices and Changelog are now required in README.md, not SKILL.md. Updated the "Skills are versioned" check in best-practices to look for `## Changelog` in README.md.
- 3 (2026-04-20): Updated `setup` action template to create `.state/` at project root instead of `.claude/state/`. New skills scaffolded from templates now default to the correct state-dir location.
- 2 (2026-04-16): Extended symlink pattern to `.claude/agents/`. Setup action template, Best Practices table, and skill template now require agent symlinks the same way hooks have been required. Added fork rule (explicit divergence via regular-file override) and registry-level agent-ownership rule.
- 1 (2026-04-16): Adapted from Anthropic's skill-creator. Added project conventions (versioning, symlinks, required sections, README design doc). Kept full evaluation pipeline and description optimization.
