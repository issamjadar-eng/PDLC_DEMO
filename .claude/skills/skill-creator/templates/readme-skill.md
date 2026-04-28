# {{SKILL_TITLE}} — Design & Architecture

This document describes the design decisions behind the {{SKILL_NAME}} skill. It is not loaded by Claude during normal skill operation — it exists for human understanding.

For skill usage and instructions, see `SKILL.md`.

## Overview

{{SKILL_OVERVIEW}}

## Lineage

<!-- If adapted from another skill, document the mapping -->
<!-- If original, state: "Original skill, not adapted from a prior version." -->

## Key Design Decisions

<!-- Document the why behind important choices -->

### {{DECISION_1_TITLE}}

{{DECISION_1_EXPLANATION}}

## Dependencies

| File | Required by | Purpose |
|------|-------------|---------|
<!-- List external files/directories this skill reads or writes -->

## Changelog

<!--
Skill-scoped only. Each entry describes what changed IN THE SKILL itself
(new action, schema change, behavior change, bug fix, version bump).

Do NOT log here:
  - Project-level work that happens to use the skill — that belongs in tasks/.
  - Project-specific names (e.g., a particular company, device, or codename).
  - Project task references (e.g., `ben/118`, `ros/045`).

The skill is project-agnostic; its changelog must be too. If a skill change
was driven by a project's needs, describe the skill change neutrally — the
project context lives in commit history and the task doc, not here.
-->

- 1 ({{DATE}}): Initial version — {{INITIAL_DESCRIPTION}}
