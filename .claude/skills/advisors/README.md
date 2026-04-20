# `/advisors` Skill — Design Documentation

> This file is for human reference. Claude reads `SKILL.md` for action definitions.

## Purpose

Packages persona advisor agents as a single bundle that serves two runtimes from one source of truth:

1. **Claude Code** — delegate strategy questions to a grounded subagent via `Agent(subagent_type: "<name>", ...)`
2. **project-console** — chat with the same advisors in a browser UI

## Architecture

```
.claude/skills/advisors/          ← skill bundle (registry-distributable)
├── SKILL.md                      ← action definitions (7 actions)
├── VERSION
├── README.md                     ← this file
├── overlay-defaults.yml          ← seed for project.yml advisors section
├── agents/                       ← bundled agent files (CC-native + console: block)
│   └── regulatory-affairs.md     ← first agent (spike)
├── lib/                          ← shared Python loader
│   ├── __init__.py
│   └── loader.py                 ← DomainAgent + overlay merge + group assembly
├── scripts/
│   └── render-grounding.py       ← PEP 723 CLI, generates grounding blocks
└── tests/
    ├── test_loader.py            ← 16 tests
    └── test_render_grounding.py  ← 11 tests

.claude/agents/                   ← installed agents (CC discovers these at session start)
├── project-secops.md             ← existing operational agent (not an advisor)
└── regulatory-affairs.md         ← installed by /advisors init

project.yml                       ← advisors: section with enabled list + overlays
```

## Source of Truth

`.claude/agents/*.md` is the single source of truth for every advisor. The console reads these files via a shared loader (`lib/loader.py`) symlinked into `tools/project-console/console/advisors_lib`.

Console-only metadata (`title`, `kind`, `group`, `context`, `sources`, `members`) rides in a `console:` extension block in the frontmatter. CC ignores unknown keys.

## Three-Tier Sourcing

| Tier | What | Where | Example |
|------|------|-------|---------|
| Universal | Same across all medtech projects | Agent file `console.sources` | `docs/external/fda-guidance/**/*.md` |
| Shape-stable | Same structure, different content | Agent file `console.context` / `console.sources` | `docs/project/dhfs/**/design-controls/architecture/**/*.md` |
| Project overlay | Specific to this project | `project.yml advisors.overlays.<name>` | Narrowing to one DHF, adding a project-unique dir |

## Context vs. Sources

- **`context`** — always-read foundational docs (architecture, strategy). Loaded before the question.
- **`sources`** — triaged per question via the discovery workflow. Not all read every time.

## Console Symlink

```
tools/project-console/console/advisors_lib → ../../advisors/lib
```

Created by `/advisors setup`. Console's `domain_agents.py` imports from `advisors_lib` to get the shared loader.

## Running Tests

```bash
uv run --with pyyaml --with pytest pytest .claude/skills/advisors/tests/ -v
```

## Key Decisions

See task 057 (`tasks/ben/057-unify-console-cc-agents.md`) for the full analysis-of-record:

- **Inversion**: CC agents are source of truth, console consumes (not the reverse)
- **Naming**: skill code name `advisors`, console UI label "Assistants"
- **Grounding workflow**: context-first → triage sources → external lookup → counterpoint pass
- **Panel agents**: console-only in v1 (`console.kind: panel`)
- **Per-project persona overrides**: not supported in v1 (fork the file)
