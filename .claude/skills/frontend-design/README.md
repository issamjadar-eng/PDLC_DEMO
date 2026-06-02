# Frontend Design

A skill that guides Claude to produce distinctive, production-grade frontend code with an intentional aesthetic point of view — the opposite of generic "AI slop" output.

## Lineage

This skill is adapted from Anthropic's public [`frontend-design`](https://github.com/anthropics/skills/tree/main/skills/frontend-design) skill in the [`anthropics/skills`](https://github.com/anthropics/skills) repository, licensed under the **Apache License 2.0**. The original license terms are preserved verbatim in [`LICENSE.txt`](LICENSE.txt); the pinned upstream commit at adoption time is recorded in [`.pinned-sha`](.pinned-sha).

Modifications from upstream are limited to:

- **Frontmatter shape** — upstream's `license:` field replaced with this project's required `name` / `description` / `version` / `updated` quartet (license info moved to a comment line + LICENSE.txt file).
- **Description expansion** — added explicit TRIGGER bullets and the `frontend-slides` disambiguation note to combat undertriggering and prevent overlap with the sibling slide-deck skill.
- **Required sections** — added `## Supporting Files` and `## Notes` sections to match this project's skill conventions; moved Best Practices + Changelog into this README per project convention (SKILL.md is loaded into context on every trigger; design-doc metadata belongs in the never-auto-loaded README).

The original body — Design Thinking and Frontend Aesthetics Guidelines — is preserved word-for-word. Substantive improvements to the guidance text should flow back upstream where compatible.

## What This Does

Anthropic's guidance text covers four design dimensions — **typography**, **color & theme**, **motion**, and **spatial composition** — plus a **backgrounds & visual details** layer and an explicit list of generic patterns to avoid. It's guidance-only: no scripts, no actions, no automation. The skill's value is loaded into Claude's context whenever the user asks for any kind of web UI work, biasing the output toward intentional aesthetic choices instead of the default-converged "purple gradient on white, Inter everywhere" template.

## Relationship to Sibling Skills

| Skill | Surface |
|-------|---------|
| `frontend-design` (this skill) | General web UI — components, pages, dashboards, landing pages, posters, artifacts, marketing sites |
| `frontend-slides` | HTML slide decks / presentations (zero-dependency, animation-rich) — uses `md-deck` as builder sibling |
| `md-deck` | Markdown → HTML deck pipeline; consumes `frontend-slides` style presets |

The three are designed to coexist without trigger overlap: `frontend-slides` constrains itself to slide-based artifacts, `md-deck` constrains itself to markdown-sourced decks, and `frontend-design` covers the rest of the web-UI space. The disambiguation note in `frontend-design`'s description makes the boundary explicit so neither skill claims the other's territory.

## Dependencies

| File | Required by | Purpose |
|------|-------------|---------|
| (none) | — | This is a guidance-only skill — no hooks, no agents, no scripts, no shared infrastructure. |

## Best Practices

<!-- Consumed by /best-practices audit -->

| Check | How to Verify | Severity | Scope |
|-------|--------------|----------|-------|
| Skill installed | `.claude/skills/frontend-design/SKILL.md` exists with valid frontmatter | Required | shared |
| README.md exists | Design doc at skill root | Required | shared |
| LICENSE.txt preserved | `LICENSE.txt` at skill root, byte-identical to upstream Apache-2.0 | Required | shared |
| Upstream SHA pinned | `.pinned-sha` at skill root records the commit adopted | Required | shared |
| Frontmatter complete | name, description, version, updated all present | Required | shared |
| Changelog current | Latest README changelog entry matches SKILL.md `version` | Required | shared |
| No trigger overlap with `frontend-slides` | SKILL.md description explicitly disambiguates from sibling decks skill | Required | shared |
| Project-agnostic | No project / company / device names in SKILL.md or README.md | Required | shared |

## Changelog

<!--
Skill-scoped only. Each entry describes what changed in frontend-design itself.
No project-specific names, no project task references — those go in the
project's tasks/ and commit history.
-->

- 1 (2026-06-01): Initial version — adapted from [`anthropics/skills`](https://github.com/anthropics/skills) pinned upstream SHA `da20c92`. Body text (Design Thinking + Frontend Aesthetics Guidelines) preserved verbatim under Apache-2.0; frontmatter rewritten to project's 4-field shape; description expanded with explicit TRIGGER bullets and `frontend-slides` disambiguation; `## Supporting Files` and `## Notes` sections added per project skill conventions; Best Practices + Changelog moved to this README.
