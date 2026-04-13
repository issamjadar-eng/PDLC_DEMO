# Skills Registry — Hitachi

Internal Claude Code skills and best practices for project setup.

## Terminology

- **Skill** — A reusable, distributable Claude Code workflow. Each skill is a directory containing a `SKILL.md` file and optional supporting files (templates, distributable content). Self-contained: everything a skill needs to function lives within its directory.
- **Installed skill** — A skill copied into a project's `.claude/skills/<name>/` directory. A skill becomes an installed skill when its directory is placed in a project.
- **Registry** — This repository (`benxavier-gl/hitachi`). The source of truth for published skills and project-level best practices.

## Project Practices

Best practices that apply to any Claude Code project. Checked by the `/best-practices` skill.

| Check | How to Verify | Severity |
|-------|--------------|----------|
| CLAUDE.md exists | `CLAUDE.md` exists in project root | Required |
| CLAUDE.md has project overview | `CLAUDE.md` contains a `## Project Overview` section | Required |
| CLAUDE.md has working conventions | `CLAUDE.md` contains a `## Working Conventions` section | Required |
| CLAUDE.md has For Claude section | `CLAUDE.md` contains `### For Claude` section with behavioral instructions | Required |
| Gitignore exists | `.gitignore` exists in project root | Recommended |
| Glossary exists | `glossary.md` exists for shared terminology | Recommended |
| README per folder | Every non-hidden directory under project root has a `README.md` | Recommended |
| Skills are self-contained | Every `.claude/skills/*/SKILL.md` must not reference files outside its own skill directory for templates, structures, or definitions. All content a skill generates must be defined inline in `SKILL.md` or in supporting files within the skill's directory (referenced via `${CLAUDE_SKILL_DIR}`). Skills may reference project files they read/write as part of their operation. | Required |
| Skills are versioned | Every `.claude/skills/*/SKILL.md` has `version:` in YAML frontmatter and a `## Changelog` section. | Required |
| Skills use SKILL.md convention | Every skill directory under `.claude/skills/` contains a `SKILL.md` file (all caps) as the entrypoint. | Required |

## Published Skills

| Skill | Directory | Version | Description |
|-------|-----------|---------|-------------|
| Task Management | [task/](task/) | 11 | Task-driven workflow with per-person folders, indexes, PreToolUse gate hook, and SessionStart/End hooks (session-env, session-cleanup) |
| SecOps | [secops/](secops/) | 1 | Security posture — SessionStart security-assert hook, project-secops remediation agent, canonical `permissions.allow` list merged into `settings.json` |
| Best Practices | [best-practices/](best-practices/) | 7 | Project audit against shared registry and local skill best practices |
| MedTech Docs | [medtech-docs/](medtech-docs/) | 11 | Scaffold and manage docs/ structure for regulated medical device projects with HTML compliance dashboard |
| Tracker | [tracker/](tracker/) | 3 | Submission package tracker — build markdown from architecture and regulatory context, render HTML dashboard, assess readiness |
| Strategy | [strategy/](strategy/) | 7 | Scan task docs for tagged strategy content and assemble unified strategy documents across domains |
| Docflow | [docflow/](docflow/) | 1 | Document conversion and round-trip management between markdown and formal formats (DOCX, PDF, XLSX) with image fidelity and cross-reference resolution |
| Skill Creator | [skill-creator/](skill-creator/) | — | Create, edit, and optimize skills; run evals and benchmark skill performance |
| Lessons | [lessons/](lessons/) | 1 | Capture, stage, and promote lessons learned from task work — harvest tagged insights into a team ledger and promote mature lessons |

## Published Agents

| Agent | File | Description |
|-------|------|-------------|
| project-secops | [secops/agents/project-secops.md](secops/agents/project-secops.md) | Security posture remediation agent — triggered when automated security checks report critical/high failures. Packaged inside the `secops` skill; `/secops setup` copies it into `.claude/agents/` so Claude Code can discover it. |

## Registry Structure

```
hitachi/
├── skills/
│   ├── manifest.md                        # This file — master index
│   ├── task/                              # Task management skill + hooks
│   ├── best-practices/                    # Best practices audit skill
│   ├── medtech-docs/                      # MedTech documentation skill with templates/standards/frameworks
│   ├── tracker/                           # Submission package tracker skill
│   ├── strategy/                          # Strategy harvester skill
│   ├── docflow/                           # Document conversion skill
│   ├── skill-creator/                     # Skill authoring and evaluation
│   ├── lessons/                           # Lessons learned harvester
│   └── secops/                            # Security posture skill — hooks, agent, canonical permissions allow list
└── agents/                                # (Empty — project-secops now lives under skills/secops/agents/)
```

Each skill is a directory containing `SKILL.md` (the entrypoint) and optional supporting files. Simple skills have just `SKILL.md`. Skills with distributable content (like `medtech-docs`, `tracker`, `task`) include subdirectories for templates, scripts, hooks, or references.
