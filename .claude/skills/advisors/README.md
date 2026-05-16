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

- **CC agents are source of truth, console consumes** (inversion locked in task 057).
- **Naming**: skill code name `advisors`; console UI label "Assistants".
- **Canonical-role grounding** is the default mode for new advisors (locked task 191). Literal-glob is legacy — retained for backward compatibility with project forks, not for new authoring.
- **IoC pattern**: L1 + L2 (canonical role names + ranked pattern alternatives) live in the `/dhf-manifest` skill, **not** in this skill. The advisors skill is the *consumer* of the catalog. This keeps the advisor bundle agnostic about project file layouts.
- **Tier 3 implemented as a helper subagent** (`advisor-researcher`) rather than inlining Glob/Grep semantics into the advisor body — keeps each advisor body small and gives the researcher a dedicated, restricted tool set.
- **Panel agents** stay in canonical-role mode like solos (decision finalized in task 191 Phase 6 rollout), with smaller tier lists since panels delegate substantive analysis to their members.
- **Per-project persona overrides** not supported in v1+ (fork the file under `.claude/agents/`, then document the fork in `.claude/sync-log.md` per the best-practices audit).
