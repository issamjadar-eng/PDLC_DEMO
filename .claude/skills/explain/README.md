# Explain — Design & Architecture

This document describes the design decisions behind the `explain` skill. It is not loaded by Claude during normal skill operation — it exists for human understanding.

For skill usage and instructions, see `SKILL.md`.

## Overview

`/explain <question>` answers a question about the project and renders the answer as a **self-contained, visualization-rich HTML document** (tables, diagrams, badges, timelines), saves it to the user's personal scratch folder, and prints a clickable link. It is built for **onboarding** — helping technical and non-technical people get oriented in an AI-driven project — but is useful to anyone who prefers a structured, keepable answer over a long chat reply.

The skill is the **presentation layer**, not a search engine or a domain expert. It discovers and reuses whatever knowledge tooling the project already provides (specialized skills, expert agents, search tools) for the research, and falls back to built-in file tools when the project provides none. Its own contribution is structure and visuals.

## Lineage

Original skill, not adapted from a prior version. The HTML design system (color tokens, table/badge/timeline/figure styling, collapsible source widget) is derived from hand-made explainer documents produced in earlier sessions of this project (`responses/`), generalized to be project-agnostic.

## Key Design Decisions

### Explicit-invocation-only triggering

The description is deliberately **anti-pushy** — the opposite of most skills, which fight under-triggering. This skill must fight *over*-triggering: generating an HTML file mid-conversation when the user only asked a casual question would be a surprise and a nuisance. The skill fires only when the user explicitly types `/explain`. This also keeps it clear of the user-level `graphify` skill, which already claims broad "any question about the project" triggering.

### Output to personal scratch, gitignored

Generated documents land in `tasks/{person}/_scratch/explain/`. Three reasons:
1. **Task-gate exemption** — writes under `tasks/` are exempt from the project's PreToolUse task gate, so a brand-new user can run `/explain` as their first command without learning the task workflow.
2. **Privacy + no repo growth** — `_scratch/` is gitignored project-wide; explainers are personal consumption artifacts, not committed deliverables.
3. **Sanctioned location** — the scratch rule forbids inventing new gitignored directories; `_scratch/` already exists for exactly this kind of artifact.

### Aggregator, not searcher (runtime discovery, zero dependencies)

The skill declares **no** `dependencies:` and names **no** specific skills/agents/tools. Instead it describes a discovery procedure: survey what the project provides (their self-descriptions state when to use them), use whatever matches the question, fall back to built-in tools. This is what lets the skill work unmodified in a bare project, in this project, and in a future project with entirely different tooling.

### Self-contained HTML, inline SVG only

No JS frameworks, no CDN links, no external fonts. Inline CSS + inline SVG. The files must open offline, render identically years from now, and survive corporate proxies. The existing hand-made examples proved inline SVG is sufficient for the diagrams this skill needs.

### Two-layer documents + one-citation-per-block

Every document opens with a jargon-free "In plain terms" summary, then technical detail — serving both audiences without an `--audience` mode switch (a `--simple` flag exists for fully non-technical output). Source citations use collapsible `<details>` widgets placed **once per logical block** (table, wordy row, paragraph, connected section), not per claim — keeping documents readable rather than citation-cluttered.

### Not canonical

Every generated document carries a banner and a Sources section. In a regulated project, a stale personal HTML must never be mistakable for a controlled source. This mirrors the spirit of the `knowledge-pack-not-canonical` rule.

### Visual gallery (per-file, lean template)

The template ships only the canonical CSS + a lean set of core/common blocks; richer visuals live as **one self-contained file per visual** under `references/visuals/` (11 SVG diagrams + 8 CSS components), with a `README.md` index and a selection table in SKILL.md. The skill reads only the 1–3 files it picks.

Rationale: a single combined gallery would load all snippets when only a few are needed; per-file is the finest-grained progressive disclosure, minimizing per-render token cost for an often-run skill, and each file previews standalone in a browser. Trade-off: the preview CSS in each gallery file duplicates the palette — accepted as **preview-only** (output always uses the template's canonical CSS, so duplication never affects real output). The diagram/component vocabulary is generalized from the hand-made explainers in earlier project sessions. Guardrail in SKILL.md: pick the 1–3 visuals that genuinely clarify; never decorate for its own sake.

## Dependencies

| File / dir | Required by | Purpose |
|------------|-------------|---------|
| `project.yml` (`team.active[]`) | explain, list actions | Resolve `git user.email` → `task_folder` for the output path. Optional — falls back to asking the user once if absent. |
| `tasks/{person}/_scratch/` | explain, list actions | Output location (created on first use). Gitignored. |
| `templates/explainer.html` | render step | Canonical CSS + skeleton; the only CSS the output uses. |
| `references/visuals/*.html` + `README.md` | render step | Optional richer visuals; only the chosen file(s) are read. Preview CSS in each is non-authoritative. |
| Project knowledge tooling (skills / agents / search MCP) | explain action (grounding) | Optional — used when present and matching; built-in Glob/Grep/Read otherwise. |

No frontmatter `dependencies:` block — the skill needs no other registry component to function (all use is runtime-discovered and optional).

## Best Practices

<!-- Consumed by /best-practices audit -->

| Check | How to Verify | Severity | Scope |
|-------|--------------|----------|-------|
| Skill has SKILL.md | `.claude/skills/explain/SKILL.md` exists | Required | shared |
| Frontmatter complete | name, description, version, updated all present | Required | shared |
| README.md exists | Design doc at skill root | Required | shared |
| Changelog current | Latest changelog entry matches the SKILL.md `version` | Required | shared |
| HTML template present | `.claude/skills/explain/templates/explainer.html` exists | Required | local |
| Template is self-contained | `explainer.html` contains no external `<script src>`, `<link href>`, or CDN/font URLs | Recommended | local |
| Visual gallery present | `.claude/skills/explain/references/visuals/` has the diagram/component `.html` files + `README.md` index | Recommended | local |
| Gallery snippets are fenced | Every `references/visuals/*.html` contains a `BEGIN SNIPPET` / `END SNIPPET` marker pair | Recommended | local |
| Gallery index in sync | Each `references/visuals/*.html` (excluding README) has an entry in the `references/visuals/README.md` catalog and a row in the SKILL.md selection table (the canonical "when to use" guide) | Recommended | local |
| No duplicated selection criteria | Per-file gallery notes carry mechanics only (preview-CSS caveat + copy-between-markers); "when to use" criteria live solely in the SKILL.md selection table | Recommended | local |
| Project-agnostic | No project names, device codenames, or domain terms in SKILL.md, README.md, the template, or the gallery | Required | shared |

## Changelog

<!--
Skill-scoped only. Each entry describes what changed IN THE SKILL itself.
No project-specific names, no task references, no project-level outcomes.
-->

- 3 (2026-06-03): Folded each visual's "when to use" description into the SKILL.md gallery selection table (merged into a `When to use` column, replacing the terse `If the content is…` column). Selection criteria now live in exactly one place — the SKILL.md table; the gallery files stay prose-free (mechanics handled generally in the render step). Recovered the descriptions from the v2 per-file notes.
- 2 (2026-06-03): Visual gallery. Added `references/visuals/` — 11 SVG diagram patterns (layered architecture, linear flow, feedback loop, decision flow, lifecycle, sequence/handshake, convergence, tree, comparison mapping, 2×2 matrix, swimlane) + 8 CSS components (legend cards, stat tiles, comparison ✓/✗ table, progress bars, spec-sheet, do/don't, horizontal timeline, pull-quote), one self-contained previewable file each with `BEGIN/END SNIPPET` markers, plus a `README.md` index. Expanded the template's canonical CSS to cover all components; added a selection table + an over-decoration guardrail to the render step. Skill reads only the chosen visual file(s). Triggering unchanged.
- 1 (2026-06-03): Initial version — `/explain <question>` renders a self-contained, visualization-rich HTML explainer to the user's scratch folder and returns a clickable link. Actions: explain (default, with `--simple`), `list`, `help`. Explicit-invocation-only triggering; aggregator design (runtime-discovers project knowledge tooling, zero declared dependencies); generic HTML template with 14 components; functional + trigger evals.
