# Gemini CLI Project Instructions

This project is primarily configured for **Claude Code**. To ensure consistency and avoid duplication, Gemini CLI must follow the established project mandates and workflows defined in the Claude configuration.

## Primary Mandates

1.  **Follow `CLAUDE.md`**: The `CLAUDE.md` file in the project root is the authoritative source for project-wide instructions, information flow, and working conventions. **Read and adhere to `CLAUDE.md` for all tasks.**
2.  **Single Source of Truth**: `project.yml` is the single source of truth for project identity, team roster, skill registries, and security policy. Reference it directly; do not redeclare its facts.
3.  **Task-First Workflow**: All non-trivial work must be associated with an active task in `tasks/<person>/NNN-<name>.md`.
    - Before making any changes (Execution phase), identify or create an active task.
    - If no task is active, use the logic described in the `CLAUDE.md` "Task-First Workflow" section.
4.  **Strategy & Lessons Capture**: Capture strategy decisions and lessons learned **inline** in the active task document using the HTML comment markers:
    - `<!-- STRATEGY CONTENT: domain, topics -->`
    - `<!-- LESSONS LEARNED: category -->`
5.  **Documentation Standards**: Documentation lives in `docs/`. Follow the three-tier structure (external / internal / project) and README conventions (Changelog, Conventions sections).

## Tooling & Skills

- Existing Claude skills (e.g., `medtech-docs`, `tracker`, `task`) are located in `.claude/skills/`.
- While Gemini CLI may not execute these skills as shell aliases, it should follow the procedures and patterns defined in their respective `SKILL.md` files when performing related tasks.
- Always `Read .claude/skills/<name>/SKILL.md` before performing work in a skill's domain.

## Workspace Safety

- Respect the task gate logic. Although Gemini CLI does not have the same `PreToolUse` hook enforcement as Claude Code, you are mandated to self-enforce the "No active task = No edits" rule for all files except those listed as exempt in `CLAUDE.md`.
