# Reference Audit — Design & Architecture

This document describes the design decisions behind the `reference-audit` skill. It is not loaded by Claude during normal skill operation — it exists for human understanding.

For skill usage and instructions, see `SKILL.md`.

## Overview

Verifies that every citation in a project document actually resolves to a real source and that the source supports the cited claim. The skill ships a verification engine (`citations` advisor) and three specialized researcher subagents (external-formal / internal-formal / informal-link), plus an action set (`setup` / `init` / `fan-out` / `list`) that scaffolds and refreshes a structured audit report under `docs/_analysis/<doc-slug>/references-audit.md`.

Two invocation modes share one engine:

- **Point query** — a domain advisor (regulatory-affairs, quality-engineering, etc.) calls `citations` via the Agent tool to verify one citation it's about to vouch for in its own answer.
- **Batch audit** — a human runs `/reference-audit init <doc>` + `fan-out <doc-slug>` to verify every citation in a document.

## Lineage

Original skill — not adapted from a prior version. Modeled after the action shape of `/gap-analysis` (`init` / `fan-out` / `list`) and the lightweight-researcher pattern of the `advisors` skill (`advisor-researcher`). The two-tier grounding model is inherited from `medtech-docs` (the L1a registry-reference + L1b project-applicability convention).

Conceptual prior art: `/gap-analysis` audits content methodology against standards; `/dhf-manifest` audits structural coverage of regulatory obligations; this skill audits the references themselves — distinct lane, complementary purpose.

## Key Design Decisions

### Engine + skill as parallel artifacts, not skill-owned advisor

The `citations` advisor and the `/reference-audit` skill are **peer artifacts** that share a common contract: a `(claim, reference_target) → finding` engine. The skill owns the agent files (they live under `skills/reference-audit/agents/` and are symlinked into `.claude/agents/` by `setup`) but the advisor is independently invocable by any caller via the Agent tool, not just by this skill. Other domain advisors call it for point queries; the skill calls it for batch audits.

Rationale: a skill-owned, skill-only engine would force every caller (including other domain advisors) to invoke the skill rather than invoke the agent directly, which conflicts with the Agent tool's natural calling convention.

### Two-tier verification by default (L1a + L1b)

External-formal references are verified against both the medtech-docs registry distillation (`.claude/skills/medtech-docs/references/`) and the project applicability layer (`docs/external/`). This honors the medtech-docs "cite both" mandate documented in the registry-reference README's "For Claude" section.

A one-tier verifier (registry only, or applicability only) would miss the asymmetric failure modes: a registry-supported claim with no project applicability analysis is genuinely `unverified` (project hasn't decided how the clause applies); an applicability-supported claim with no registry coverage is also `unverified` (need to extend the distilled corpus). The two-tier consolidation table encodes those failure modes deterministically.

### Three-band verdict (sound / unverified / broken)

Each finding carries an explicit verdict band rather than a numeric confidence score. Numeric scores from LLMs are ungrounded; thresholds become arbitrary. The three bands map to how a regulated-document reviewer actually reads a citation audit — "this is solid", "I can't tell from here", "this is wrong". The middle band, `unverified`, is treated as a **real audit output** — fetch failures, paywalled sources, ambiguous text. Forcing those into a binary `sound / broken` either erodes trust (false `sound`) or creates noise (false `broken`).

### Open `kind` enum

The `kind` field on findings is an open enum. v1 emits a small set keyed to link-checking outcomes. v2 reserves additional kinds (`registry-gap`, `applicability-gap`, `applicability-conflict`, `obligation-unmapped`, `unsourced-claim-candidate`, `weak-reference`, `stronger-source-exists`) that extend the engine into adjudication-adjacent territory without breaking the contract — new kinds emerge as new researcher types, not as engine redesigns.

### v1 scope = pure link-checker; v2 candidate = unsourced-claim detection

v1 verifies references that are **explicitly present** in the document. v1 does NOT flag "this paragraph asserts a fact with no citation" — that's a domain-advisor call (which sources should be cited belongs to regulatory-affairs / quality-engineering / clinical-affairs / risk-management). v2 may add `unsourced-claim-candidate` as a researcher, but adjudication will still route to SME advisors.

Rationale: clean scope, lowest implementation risk, minimal overlap with existing SME advisors. The seam to v2 is preserved via the open `kind` enum.

### Hybrid reference extraction (regex + LLM-over-prose)

Reference extraction uses a two-pass strategy:

1. **Regex pass** for structured citations (standards, CFR, K-numbers, markdown links) — cheap, deterministic, high-precision.
2. **LLM pass** for narrative prose pointers ("see X", "per the Y doc") — only over spans not already extracted by regex.

Pure regex misses prose pointers; pure LLM is expensive over long docs. Hybrid carries 80% of the load deterministically and uses the LLM only where it adds value.

## Dependencies

| File | Required by | Purpose |
|------|-------------|---------|
| `.claude/skills/medtech-docs/references/` | `citations-external-researcher` | L1a registry-reference distillation — authoritative clause content |
| `docs/external/` | `citations-external-researcher` | L1b project applicability — project's decisions about each clause |
| `docs/internal/`, `docs/project/`, `project.yml`, `glossary.md` | `citations-internal-researcher` | Internal-formal corpus |
| `mcp__file-locator__locate` | `citations-internal-researcher` | Semantic confirmation that an internal source supports a cited claim |
| `WebFetch` | `citations-external-researcher` | L4 fallback for openly accessible external sources (CFR, FDA guidance, accessdata K-records) |
| `docs/_analysis/` | `/reference-audit init` and `fan-out` | Output destination for audit reports |
| `Agent` tool | `/reference-audit fan-out` and any caller of `citations` | Engine dispatch |

## Coexistence with Sibling Skills

| Skill | Boundary |
|-------|----------|
| `/gap-analysis` | Audits **content methodology** of a project artifact against standards (e.g., does the hazard register comply with ISO 14971's methodology?). Distinct from `/reference-audit` which checks whether the citations themselves resolve and say what they're claimed to say. Both skills write under `docs/_analysis/<topic>/` — different filenames. |
| `/dhf-manifest` | Audits **structural document coverage** of regulatory obligations (does the project have all the deliverables a 510(k) requires?). Distinct from `/reference-audit`'s concern with what's *inside* the documents. |
| `/jira-pull` | Audits **Jira-vs-trace-matrix drift** for design-controls items. Different corpus, different lane. |
| `medtech-docs` | Owns L1a + L1b convention. `/reference-audit` consumes that convention; does not modify it. |

## Best Practices

<!-- Consumed by /best-practices audit -->

| Check | How to Verify | Severity | Scope |
|-------|--------------|----------|-------|
| Skill has SKILL.md | `.claude/skills/reference-audit/SKILL.md` exists | Required | shared |
| Frontmatter complete | `name`, `description`, `version`, `updated` all present in SKILL.md | Required | shared |
| README.md exists | `.claude/skills/reference-audit/README.md` exists | Required | shared |
| Changelog current | Latest README changelog entry matches SKILL.md `version` | Required | shared |
| All 4 agents present in skill | `agents/citations.md`, `agents/citations-external-researcher.md`, `agents/citations-internal-researcher.md`, `agents/citations-informal-researcher.md` all exist in skill folder | Required | shared |
| Agent symlinks present | `.claude/agents/citations.md` and three citations-*-researcher symlinks resolve into the skill | Required | shared |
| Output template present | `templates/references-audit.md` exists | Required | shared |
| No project-specific names in skill or agents | grep skill folder + symlinked agents for company / device / project-task names; must be zero | Required | shared |
| External-formal verdicts cite L1a + L1b | A `sound` external-formal finding lists at least two evidence entries (registry + applicability) when both tiers cover the cited clause | Recommended | local |
| L1c never read | No researcher reads under `.claude/skills/medtech-docs/references/*/source/` or `.../source-md/` — raw upstream is excluded | Required | local |

## Changelog

- 3 (2026-05-29): Engine-quality fixes from the first batch pilot. Three changes: (a) **Semantic-predicate match** — `citations-external-researcher` Step 3.5 makes the previously-implicit "L1a/L1b consistent with claim" check explicit, instructing the researcher to extract the claim's central predicate, extract the source clause's predicate, and compare them directly. Same clause number + different predicate → `broken, kind=stale-citation`, not `sound`. Closes the false-`sound` failure mode where a clause exists but its content addresses a different topic than the citation attributes to it. (b) **`registry-gap` promoted to v1.1 emitted kind** — when L1a + L1b both lack a distillation, the verdict is `unverified, kind=registry-gap` with suggested-fix "extend the registry distillation," not a fallback to `sound` via internal cross-references. Surfaces missing CFR / standards distillations as actionable signal. (c) **Stricter web-fetch posture for K-numbers** — when accessdata WebFetch fails, return `unverified, kind=unreachable-source`. Internal project-cross-references are noted in evidence but do not change the verdict. The verdict reflects what was verified against authoritative sources, not what was inferred from internal corroboration. SKILL.md "v2 Roadmap" section renamed to "v1.1 enum + v2 Roadmap" with the emitted-vs-reserved split. `citations.md` finding-kinds table updated.
- 2 (2026-05-29): `init` action restructured to honor the project `_analysis/` convention (`<component>/<analysis-id>/<analysis-id>.md`) instead of the prior degenerate `<doc-slug>/references-audit.md` shape. Component segment is derived from `project.yml dhfs[]` (`arch_slug` for item DHFs, `leaf` for the system DHF) — same convention `/gap-analysis` uses. Cross-cutting docs (strategies, submissions, input-analysis, external, internal) route to the system DHF folder. `fan-out` glob updated; `list` glob updated. New step in `init`: scaffold a folder `README.md` per the readme-before-write rule. Motivation: prior v1 path convention was authored without reading the project's `_analysis/README.md`, then hand-corrected during the first batch pilot — surfaced the value of the day-before-codified `ground-in-contracts-not-assumptions` rule.
- 1 (2026-05-28): Initial version — citations engine + three researchers (external-formal two-tier, internal-formal with file-locator MCP, informal-link path-resolver) + setup / init / fan-out / list actions + audit-report template. Two-tier L1a/L1b verification by default for external-formal references; three-band verdict (sound / unverified / broken); open `kind` enum reserving v2 candidate kinds for future extension into adjudication-adjacent territory.
