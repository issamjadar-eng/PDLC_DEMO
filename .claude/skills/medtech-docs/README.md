# MedTech Docs Skill — Design & Architecture

This document describes the design decisions behind the medtech-docs skill. It is not loaded by Claude during normal skill operation — it exists for human understanding.

For skill usage and instructions, see `SKILL.md`.

## Overview

The medtech-docs skill is the **project scaffolding entry point** for regulated medical device projects. It creates the docs/ folder hierarchy, determines applicable standards, generates a compliance dashboard, and initializes project infrastructure (`project.yml`, hooks, skill setup).

## Role in the Ecosystem

medtech-docs is the orchestrator — it sets up everything a new project needs:

```
/medtech-docs init
  ├─ docs/ folder hierarchy (3-tier: external, internal, project)
  ├─ README.md for every folder (meta-model compliant)
  ├─ Standards/frameworks evaluation
  ├─ project.yml (team roster, security config, registries)
  ├─ .claude/hooks/register-hook.sh (shared hook infrastructure)
  └─ Skill setup actions (calls /task setup, etc.)
```

## Dependencies

| File | Required by | Purpose | How to create |
|------|-------------|---------|---------------|
| None | — | This skill has no dependencies — it creates project infrastructure from scratch | — |

medtech-docs is the **root of the dependency chain**. Other skills depend on the files it creates (project.yml, tasks/, etc.), but medtech-docs itself has no prerequisites.

## Key Design Decisions

### Three-Tier Documentation Structure

```
docs/
  external/    → Reference material (FDA guidance, standards, frameworks)
  internal/    → SOPs, procedures, templates (source → markdown → distilled)
  project/     → What we're building (input analysis, design controls, submissions)
```

This separates concerns: what we read (external), how we work (internal), and what we produce (project). Each tier has its own conventions and information flow.

### README Meta-Model

Every README.md follows a strict section order:
1. Title + purpose
2. Structure/Subfolders (if applicable)
3. Information Flow (if applicable)
4. Expected Content (if leaf folder)
5. Domain-specific sections
6. Conventions (required)
7. For Claude (optional)
8. Changelog (required)

This ensures consistency across 30+ READMEs and allows automated validation by the best-practices skill.

### Project Infrastructure Creation

The `init` action creates project-level files that other skills depend on:
- **`project.yml`** — team roster, security policy, registries. Seeded from registry manifests and environment auto-detection.
- **`.claude/hooks/register-hook.sh`** — shared helper for skill hook registration. Installed from `templates/register-hook.sh`.

### Skill Setup Convention

After installing skills, `init` runs each skill's `setup` action (if it has one). This allows skills to self-wire their hooks and config without medtech-docs knowing the details. The convention:
1. Scan `.claude/skills/*/SKILL.md` for a `### setup` action
2. If found → invoke it
3. If not → skip silently

### Registry-Seeded Allowlists

`project.yml` allowlists are populated from approved registries:
- **Builtin** (Anthropic): hardcoded list of official skills
- **GitHub** registries: fetch manifest.md, parse Published Skills table
- Auto-detect MCPs and plugins from environment

## Templates

All scaffold content lives in `templates/`:
- 11 README templates for the docs/ hierarchy
- 1 standard file template
- 1 dashboard HTML template
- 1 register-hook.sh helper

Templates use `{{PLACEHOLDER}}` substitution for leaf folder READMEs and `${CLAUDE_SKILL_DIR}` for file paths.

## Changelog Context

Major version milestones:
- v1: Initial scaffold with init, add-standard, evaluate, dashboard
- v3: Migrated to skills/ directory, extracted templates
- v5: README meta-model with strict section ordering
- v7: Formal/ subfolder pattern for controlled documents
- v8: Synced templates with actual docs/ state, added project infrastructure creation
