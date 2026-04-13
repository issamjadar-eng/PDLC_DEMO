# Skill Creator — Design & Architecture

This document describes the design decisions behind the skill-creator skill. It is not loaded by Claude during normal skill operation — it exists for human understanding.

For skill usage and instructions, see `SKILL.md`.

## Overview

The skill-creator is a meta-skill for creating, testing, and optimizing other skills. It provides a structured workflow from intent capture through evaluation and iteration.

## Role in the Ecosystem

skill-creator is the **skill factory** — it produces the SKILL.md files that all other skills are built from:

```
User intent → Interview → SKILL.md draft → Test cases → Evaluation → Iteration
```

## Dependencies

| File | Required by | Purpose | How to create |
|------|-------------|---------|---------------|
| `.claude/skills/` | Skill creation | Output directory for new skills | `/medtech-docs init` or `mkdir -p .claude/skills/` |

This skill has minimal dependencies — it primarily creates files rather than reading project infrastructure.

## Key Design Decisions

### Structured Creation Workflow

1. **Capture Intent** — understand what the skill should do
2. **Interview & Research** — gather requirements, examine existing patterns
3. **Write SKILL.md** — draft the skill with actions, best practices, changelog
4. **Test Cases** — define input/expected-output pairs
5. **Evaluate** — run tests with variance analysis
6. **Iterate** — improve based on results

### Evaluation Framework

Skills are tested by spawning parallel agent runs (with-skill vs baseline) and grading outputs against assertions. This provides quantitative measurement of skill effectiveness.

### Description Optimization

The skill description (frontmatter) determines when Claude Code triggers the skill. The optimization loop generates trigger queries, runs matching tests, and iterates on the description for accuracy.

### Skill File Format Convention

Every skill follows a standard structure:
- YAML frontmatter: `name`, `description`, `version`, `updated`
- Actions with step-by-step instructions
- `## Best Practices` table (optional — read by /best-practices audit)
- `## Changelog` (reverse-chronological, per version)
- `## Dependencies` table (required files, how to create them)
- Supporting files in the skill directory (hooks, templates, README.md)

## Changelog Context

This skill was sourced from Anthropic's skill-creator template and adapted for the project's conventions.
