# `/advisors` Skill — Design Documentation

> This file is for human reference. Claude reads `SKILL.md` for action definitions.

## Purpose

Packages persona advisor agents as a single bundle that serves two runtimes from one source of truth:

1. **Claude Code** — delegate strategy questions to a grounded subagent via `Agent(subagent_type: "<name>", ...)`
2. **project-console** — chat with the same advisors in a browser UI

## Architecture

```
.claude/skills/advisors/          ← skill bundle (registry-distributable)
├── SKILL.md                      ← action definitions (7 actions) + grounding model
├── VERSION
├── README.md                     ← this file (design doc for humans)
├── overlay-defaults.yml          ← seed for project.yml advisors section (literal-glob mode)
├── agents/                       ← bundled agent files (CC-native + console: block)
│   ├── advisor-researcher.md     ← helper subagent (Read/Glob/Grep only)
│   ├── regulatory-affairs.md     ← 11 domain advisors
│   ├── clinical-affairs.md
│   ├── risk-management.md
│   ├── vnv-lead.md
│   ├── post-market.md
│   ├── cybersecurity.md
│   ├── human-factors.md
│   ├── systems-engineering.md
│   ├── quality-engineering.md
│   ├── rd-lead.md
│   ├── program-manager.md
│   ├── core-team-panel.md        ← 2 cross-functional panels
│   └── design-review-panel.md
├── lib/                          ← shared Python loader
│   ├── __init__.py
│   └── loader.py                 ← DomainAgent + overlay merge + group assembly
├── scripts/
│   └── render-grounding.py       ← PEP 723 CLI, generates grounding blocks
└── tests/
    ├── test_loader.py            ← 15 tests
    └── test_render_grounding.py  ← 25 tests

.claude/agents/                   ← installed agents (CC discovers these at session start)
├── project-secops.md             ← non-advisor operational agent
├── advisor-researcher.md         ← installed by /advisors init
├── regulatory-affairs.md
└── ... (one symlink per advisor → ../skills/advisors/agents/<name>.md)

project.yml                       ← advisors: section (enabled list + literal-glob overlays)
```

## Source of Truth

`.claude/agents/*.md` (installed as **symlinks** into the skill bundle) is the single source of truth for every advisor. The console reads these files via the shared loader (`lib/loader.py`) symlinked into `tools/project-console/console/advisors_lib`.

Console-only metadata (`title`, `kind`, `group`, `context`, `sources`, `members`, `canonical_roles`) rides in a `console:` extension block in the frontmatter. Claude Code ignores unknown keys.

## Grounding modes — overview

| Mode | Where grounding is declared | When path resolution happens | Status |
|------|-----------------------------|------------------------------|--------|
| **Canonical-role** (v1.2.0+) | `console.canonical_roles:` block (`tier_1` / `tier_2` / `tier_3.researcher`) referring to roles in the sibling `/dhf-manifest` skill's `data/canonical-roles.yaml` catalog | At agent runtime, via the per-project discovery index (`docs/project/dhf-manifest/<slug>-dhf-discovery.json`) | **Default** for all bundled advisors. |
| **Literal-glob** (legacy v1.0–v1.1) | `console.context:` + `console.sources:` literal glob patterns, plus `project.yml advisors.overlays.<name>.{add,exclude}` for per-project filters | At render time, by expanding globs against the project filesystem | Parser fallback for project forks and downstream registries that haven't migrated. |

See `SKILL.md` § Grounding model for the full description, the tier-design recipe, and the `Agent` tool requirement for Tier 3. The catalog side of canonical-role mode (L1+L2 patterns, resolution algorithm, `multi_file:` flag) is documented in the sibling `/dhf-manifest` skill's `README.md` § 4.

## The advisor-researcher helper

A non-user-facing helper subagent shipped with the bundle. Tools: `Read`, `Glob`, `Grep` only. Purpose: domain advisors invoke it via the `Agent` tool when their Tier 1 + Tier 2 grounding leaves a question's answer thin — the researcher walks READMEs, follows cross-references, and globs/greps for additional grounding paths, returning curated `(path, why-relevant, ~size)` tuples without flooding the parent agent's context.

The researcher has no `console:` block — it is not exposed in the project-console UI, and `render-grounding.py --all` skips it via the `_is_grounding_agent` heuristic. It's strictly a helper invoked by other advisors.

**Platform caveat.** When a domain advisor is itself invoked as a nested subagent (e.g., `Agent(subagent_type=...)` from a parent CC session), Claude Code disables the `Agent` tool on the child. The advisor cannot reach the researcher in that nesting. Each advisor's auto-rendered body documents the fallback: perform the researcher's Read/Glob/Grep workflow inline.

## Console Symlink

```
tools/project-console/console/advisors_lib → ../../advisors/lib
```

Created by `/advisors setup`. The console's `domain_agents.py` imports from `advisors_lib` to get the shared loader.

## Running Tests

```bash
.claude/skills/advisors/tests/run.sh                  # whole suite
.claude/skills/advisors/tests/run.sh -k locator -v    # extra args pass through to pytest
```

`run.sh` pulls `pytest` + `PyYAML` ephemerally via `uv run --no-project`, so no dev dependencies are installed into the repo and no build artifacts are committed (`__pycache__/`, `.pytest_cache/` are covered by the skill-local `.gitignore`).

85 tests cover the loader (16), render-grounding (24, including canonical-role-mode cases and helper-skip behavior), and file-locator wiring (45 — one renderer-level group plus per-agent structural checks across the bundled advisors and panels).

## Key Decisions

- **CC agents are source of truth, console consumes** (inversion locked in early design).
- **Naming**: skill code name `advisors`; console UI label "Assistants".
- **Canonical-role grounding** is the default mode for new advisors. Literal-glob is legacy — retained for backward compatibility with project forks, not for new authoring.
- **IoC pattern**: L1 + L2 (canonical role names + ranked pattern alternatives) live in the `/dhf-manifest` skill, **not** in this skill. The advisors skill is the *consumer* of the catalog. This keeps the advisor bundle agnostic about project file layouts.
- **Tier 3 implemented as a helper subagent** (`advisor-researcher`) rather than inlining Glob/Grep semantics into the advisor body — keeps each advisor body small and gives the researcher a dedicated, restricted tool set.
- **Panel agents** stay in canonical-role mode like solos, with smaller tier lists since panels delegate substantive analysis to their members.
- **Per-project persona overrides** not supported in v1+ (fork the file under `.claude/agents/`, then document the fork in `.claude/sync-log.md` per the best-practices audit).

## Best Practices

<!-- Consumed by /best-practices audit -->

| Check | How to Verify | Severity | Scope |
|-------|--------------|----------|-------|
| Skill installed | `.claude/skills/advisors/SKILL.md` exists | Required | shared |
| Frontmatter complete | `name`, `description`, `version`, `updated` all present in SKILL.md | Required | shared |
| Agents dir exists | `.claude/agents/` directory exists | Required | shared |
| Advisor agents installed as symlinks | For each advisor `<name>` in `project.yml.advisors.enabled`, `.claude/agents/<name>.md` is either a symlink into `.claude/skills/advisors/agents/` or a regular file explicitly documented as a fork in `.claude/sync-log.md`. | Required | shared |
| At least one advisor enabled | `project.yml` has `advisors.enabled` with ≥1 entry | Recommended | shared |
| Overlay schema valid | Every entry in `project.yml.advisors.overlays` has `add` and `exclude` as lists | Required | shared |
| Grounding blocks in sync | `render-grounding.py --all --dry-run` exits 0 (no changes needed) | Recommended | shared |
| Console symlink (if console installed) | If `tools/project-console/console/` exists, `tools/project-console/console/advisors_lib` is a symlink to `.claude/skills/advisors/lib` | Recommended | shared |
| Agent bodies device-agnostic | No device-specific names in bundled `agents/*.md` persona prose (use overlays for device context) | Recommended | shared |

## Changelog

_Versioning is integer from v9 onward (skill convention); earlier entries retain their original semver labels for historical continuity._

- 13 (2026-09-08): **`grounding_scan.py` — canonical-source check.** Deterministic evidence for the grounding need (WUN-25): every `<!-- BEGIN GROUNDING -->` block must reference canonical sources only, and the file-locator index must contain no path matching the project's `corpus_excludes`. Ships fixtures + tests; `tests/conftest.py` adds the socket guard. The index half is a deployment check (`requires_deployment: content.file_locator_index`).

- 12 (2026-07-22): New `commercial` domain advisor (Commercial Assistant, core-team, canonical-role mode) — go-to-market, launch sequencing, pricing/reimbursement, competitive positioning, and interpretation of data-backed business-question report editions (provenance-marker + edition-lifecycle discipline in the persona body). Tier 1: `commercial_strategy` + `regulatory_strategy`; Tier 2: `market_research`, `competitive_landscape`, `commercial_analysis`, `kol_feedback`, `predicate_analysis`, `postmarket_strategy`. Companion dhf-manifest catalog extension adds the `commercial_strategy` / `risk_strategy` / `commercial_analysis` roles and the `commercial` consumer label. Bundle is now 12 domain advisors + 2 panels + researcher.
- 11 (2026-06-11): Four-rung reference-consumption ladder rendered into every advisor GROUNDING block (`render-grounding.py` template). New hard rule states the ladder explicitly — (1) L1b project applicability → (2) L1a registry distillation (cite both) → (3) bundled `source-md/` full text for exact wording / omitted appendices (fda-guidance only) → (4) open web last resort — with "never skip a rung downward; never stop a rung short when the claim needs exact wording" semantics and the ISO/IEC paywall honesty note. Mode-B inline citation verification gains the same escalation step plus quarantine-banner/`[VERIFY]`-marker honoring (bannered content cannot support a `sound` clause-number verdict). All advisor agents regenerated via `--all`.
- 10 (2026-06-11): `advisor-researcher` registry carve-out. The Tier-3 fallback researcher's "stay within the project root" hard rule previously barred everything under `.claude/` — which meant precisely when an advisor's Tier-1/2 grounding failed and it escalated to the researcher, the researcher could not surface the L1a registry reference library (`medtech-docs/references/`) that the advisors' own cite-both rule requires. The rule now carves out the four registry reference categories (top-level distilled `.md` files only; `source/` + `source-md/` and everything else under `.claude/` remain off-limits).
- 9 (2026-06-02): Conformance pass — added required YAML frontmatter (`name` / `description` / `version` / `updated`) so the skill carries a real trigger description instead of a stray in-file "Base directory" line (which had left the skill effectively undiscoverable by description); moved the Best Practices table and this Changelog out of SKILL.md and into README.md; converted from a semver `VERSION` file to an integer frontmatter `version`. No change to grounding behavior, actions, or agents.
- 1.5.1 (2026-05-29): Citation verification pass split into Mode A (citations-advisor dispatch when the `Agent` tool is available) and Mode B (inline verification fallback, required when the runtime strips `Agent` from subagent invocations as a recursion guard). Both feed the same `sound` / `unverified` / `broken` verdicts and must cite the L1a registry distillation and the L1b project applicability transparently.
- 1.5.0 (2026-05-29): Cite-both Hard Rule + citations-advisor invocation step + AI-friendly federal-endpoints guidance in the canonical-role GROUNDING block. The Hard Rule requires footnoting BOTH the L1a registry distillation and the L1b project applicability for any external citation. A new workflow step instructs advisors to invoke the citations advisor for each standards-clause / CFR / K-number / FDA-guidance reference; the external-lookup pass names the eCFR API, Federal Register API, openFDA, and govinfo PDFs as preferred over bot-blocked HTML sites. Pairs with the dhf-manifest `registry_*` canonical roles that surface L1a paths into Tier 2.
- 1.4.0 (2026-05-28): QMS-governance grounding section emitted in canonical-role mode. When a document's discovery-index entry carries `governing_qms`, advisors must read the governing FORM / SOP / WI templates before recommending changes to that document. Covers the internal-mode fallback (`qms-manifest.json`) and the unverified-mapping case. Purely additive.
- 1.3.1 (2026-05-15): Added a project-agnostic test runner (`tests/run.sh`) that resolves `pytest` + `PyYAML` ephemerally via `uv` so no dev dependencies are installed into the repo; added a skill-local `.gitignore` excluding build artifacts.
- 1.3.0 (2026-05-14): Semantic file-locator wiring for canonical-role advisors. The renderer emits a self-gated "Semantic file locator" subsection framing `mcp__file-locator__locate` as a Tier-2 accelerator / Tier-3 fast path, gated on the tool's presence. All solo canonical-role advisors gained the locator tool grant. New file-locator wiring tests (suite 40 → 85).
- 1.2.0 (2026-05-12): Canonical-role grounding mode + `advisor-researcher` subagent. The renderer and loader gained a third grounding mode alongside legacy literal-glob: a `console.canonical_roles` block declaring `tier_1` / `tier_2` / `tier_3.researcher`; the renderer fetches role descriptions from the sibling dhf-manifest `canonical-roles.yaml` and emits a 3-tier grounding body. Helper subagents (no `console` block) are skipped by `--all`. New `advisor-researcher` Read/Glob/Grep-only helper. Selectors (`dhfs: {role: ...}`, `submissions: all`) render inline (suite 24 → 40).
- 1.1.0 (2026-04-16): Install agents as symlinks instead of copies. `init` / `add` create `.claude/agents/<name>.md` → `../skills/advisors/agents/<name>.md` symlinks; `remove` distinguishes symlinks from regular-file forks. Symlinks propagate skill updates automatically instead of drifting.
- 1.0.0 (2026-04-15): Initial skill scaffold. Ships the first advisor (`regulatory-affairs`) end-to-end: CC-native frontmatter with a `console` extension block, a shared `lib/loader.py` consumed by the skill and (via symlink) by project-console, a PEP 723 `render-grounding.py` CLI, an `overlay-defaults.yml` seed, and 7 actions (init, list, add, remove, overlay, sync, setup). Three-tier sourcing model documented.
