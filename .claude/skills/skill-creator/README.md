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

### Best Practices as Required Section

Every skill must declare health checks. This enables future `/best-practices audit` tooling to verify project health across all skills without reading every SKILL.md in full.

### README as Design Doc

The README.md serves as the skill's index layer (per README Navigation Rule) and as a design document. It explains **why** the skill works the way it does, which is information that doesn't belong in the operational SKILL.md.

## Dependencies

| File | Required by | Purpose |
|------|-------------|---------|
| `.claude/skills/` directory | Skill creation | Output directory for new skills |
| `.claude/hooks/register-hook.sh` | setup actions | Shared hook registration helper |
| `.claude/hooks/` directory | setup actions | Symlink target for skill hooks |
| `.claude/agents/` directory | setup actions | Symlink target for skill agents (Claude Code subagent discovery) |
| `.claude/state/` directory | hook scripts | Runtime state files |

## Changelog

- 2 (2026-04-16): Extended symlink pattern to `.claude/agents/`. Setup action template, Best Practices table, and skill template now require agent symlinks the same way hooks have been required. Added fork rule (explicit divergence via regular-file override) and registry-level agent-ownership rule.
- 1 (2026-04-16): Adapted from Anthropic's skill-creator. Added project conventions (versioning, symlinks, required sections, README design doc). Kept full evaluation pipeline and description optimization.
