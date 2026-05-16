# Skills Registry — Hitachi

Internal Claude Code skills and best practices for project setup.

## Terminology

- **Skill** — A reusable, distributable Claude Code workflow. Each skill is a directory containing a `SKILL.md` file and optional supporting files (templates, distributable content). Self-contained: everything a skill needs to function lives within its directory.
- **Installed skill** — A skill copied into a project's `.claude/skills/<name>/` directory. A skill becomes an installed skill when its directory is placed in a project.
- **Registry** — This repository (`GlobalLogic-a-Hitachi-Company/hitachi`). The source of truth for published skills and project-level best practices.

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
| Task Management | [task/](task/) | 24 | Task-driven workflow with per-person folders, indexes, PreToolUse gate hook, and SessionStart/End hooks (session-env, session-cleanup) |
| SecOps | [secops/](secops/) | 8 | Security posture — SessionStart `security-assert` hook, `project-secops` remediation agent, canonical `permissions.allow` list merged into `settings.json` |
| Best Practices | [best-practices/](best-practices/) | 15 | Project audit against shared registry and local skill best practices, with parallel sub-agent fan-out for multi-DHF projects |
| MedTech Docs | [medtech-docs/](medtech-docs/) | 23 | Scaffold and manage `docs/` structure for regulated medical device projects with HTML compliance dashboard |
| Tracker | [tracker/](tracker/) | 11 | Submission package tracker — milestone-driven readiness dashboard built from milestone catalog + composition manifests + DHF evidence |
| Strategy | [strategy/](strategy/) | 19 | Scan task docs for tagged strategy content and assemble unified strategy documents across 8 domains (regulatory, commercial, architecture, development, testing, risk, post-market, operations) |
| Docflow | [docflow/](docflow/) | 31 | Document conversion and round-trip management between markdown and formal formats (DOCX, PDF, XLSX) with image fidelity and cross-reference resolution |
| Skill Creator | [skill-creator/](skill-creator/) | 6 | Create, edit, and optimize skills; run evals and benchmark skill performance |
| Lessons | [lessons/](lessons/) | 4 | Capture, stage, and promote lessons learned from task work — harvest tagged insights into a team ledger and promote mature lessons |
| Advisors | [advisors/](advisors/) | 1.3.0 | Persona subagents (regulatory, clinical, risk, etc.) serving both Claude Code and project-console with three-tier (universal / shape-stable / project-overlay) grounding |
| DHF Manifest | [dhf-manifest/](dhf-manifest/) | 12 | 4-tier deliverable catalog projecting regulatory and QMS obligations through a project scope vector into per-DHF manifests with gap reports |
| Change Control | [change-control/](change-control/) | 0.13.0 | Bidirectional bridge between Claude Code / GitHub authoring and regulated downstream systems (Confluence, Windchill, Jira) with freeze-point lifecycle |
| Trace Matrix | [trace-matrix/](trace-matrix/) | 8 | Bidirectional design-controls trace matrix builder — parses source docs and emits controlled markdown deliverable plus JSON sidecar for project-console |
| Jira Pull | [jira-pull/](jira-pull/) | 1 | Mirror Jira issues for design-controls traceability and detect drift between Jira (canonical item universe) and regulated artifacts (DTM/HTM). Pull-only — never pushes to Jira |
| Digest | [digest/](digest/) | 9 | Automatic morning briefing at SessionStart (12 h throttled per user) and on-demand append to the project `CHANGELOG.md` |
| Project Console | [project-console/](project-console/) | 1.17.0 | FastAPI-based local console (agents chat, documents explorer, dashboards discovery) for medtech-docs projects |
| Web Control | [web-control/](web-control/) | 0.3.0 | Cross-platform browser automation as shared infrastructure — owns Chrome lifecycle and DevTools-Protocol connection helpers |
| Sync Skills | [sync-skills/](sync-skills/) | 8.1 | Bidirectional sync between project's `.claude/skills` + `.claude/agents` and the hitachi registry with three-way merge analysis and project-impact reporting |
| MD Deck | [md-deck/](md-deck/) | 0.6.0 | Build single-file HTML slide decks from structured markdown source using preset styles and iconography (non-interactive markdown → HTML pipeline) |
| Frontend Slides | [frontend-slides/](frontend-slides/) | 0.4.0 | Create zero-dependency, animation-rich HTML presentations from scratch or by converting PowerPoint files |
| File Locator | [file-locator/](file-locator/) | 1 | Local semantic file-locator MCP — `fastembed` BGE-small + SQLite FTS5; returns ranked `(path, summary, heading_anchor?, score)` tuples for natural-language queries. Complementary to `/dhf-manifest`'s structural discovery index; CI-rebuilt committed index |
| DOCX | [docx/](docx/) | — | Create, read, edit, or manipulate Word documents (`.docx`) with formatting, tables, images, tracked changes, headers/footers (Anthropic official skill) |
| PDF | [pdf/](pdf/) | — | All PDF operations: read/extract text/tables, merge, split, rotate, watermark, OCR (Anthropic official skill) |
| PPTX | [pptx/](pptx/) | — | Create, read, edit, or analyze PowerPoint files with professional design, formulas, and tracked changes (Anthropic official skill) |
| XLSX | [xlsx/](xlsx/) | — | Spreadsheet creation, editing, and analysis for `.xlsx` / `.xlsm` / `.csv` / `.tsv` files with formulas, formatting, and professional standards (Anthropic official skill) |

### Shared support

- [`shared/`](shared/) is not a published skill — it holds cross-skill utilities (e.g., `task-content-scanner.md`, `agent-design-principles.md`) consumed by the `/strategy` and `/lessons` skills.

## Published Agents

These agents are installed into a consumer project's `.claude/agents/` directory (either as symlinks via `/advisors init` or as copies via `/secops setup`). Skill-internal helper agents (those bundled inside `skills/<name>/agents/` but not installed into a consumer project's `.claude/agents/`) are intentionally omitted — they are implementation details of their parent skill.

### Advisor personas — owned by [`advisors/`](advisors/)

Canonical files live in [`skills/advisors/agents/`](advisors/agents/); root [`agents/`](../agents/) entries are symlinks into that directory.

| Agent | File | Description |
|-------|------|-------------|
| advisor-researcher | [agents/advisor-researcher.md](../agents/advisor-researcher.md) | Read/Glob/Grep-only helper subagent — domain advisors delegate here when Tier 1 + Tier 2 grounding doesn't cover the question. Returns curated `(path, why-relevant, size)` tuples |
| clinical-affairs | [agents/clinical-affairs.md](../agents/clinical-affairs.md) | Clinical evidence strategy, KOL engagement, user-needs validation, clinical risk framing, benefit-risk analysis |
| core-team-panel | [agents/core-team-panel.md](../agents/core-team-panel.md) | Console-only — cross-functional program advisory panel combining Program Manager, Regulatory, Clinical, Quality, and R&D for multi-perspective program-level questions |
| cybersecurity | [agents/cybersecurity.md](../agents/cybersecurity.md) | Threat modeling, SBOM, IEC 81001-5-1, pre-market cybersecurity controls, post-market vulnerability management, FDA pre-market cybersecurity guidance |
| design-review-panel | [agents/design-review-panel.md](../agents/design-review-panel.md) | Console-only — round-robin technical design review panel (Systems, R&D, V&V, HF, Risk, Quality) for architecture decisions, use-safety reviews, DHF gate decisions |
| human-factors | [agents/human-factors.md](../agents/human-factors.md) | IEC 62366 compliance, use-related risk analysis, task analysis, formative/summative usability evaluation, use-error mitigation |
| post-market | [agents/post-market.md](../agents/post-market.md) | Post-market surveillance strategy, complaint handling, trend analysis, PSUR/PMSR, field corrective actions, field-to-risk feedback loop |
| program-manager | [agents/program-manager.md](../agents/program-manager.md) | Schedule, scope, stakeholder alignment, cross-functional coordination, submission timeline tracking, DHF milestone planning |
| quality-engineering | [agents/quality-engineering.md](../agents/quality-engineering.md) | ISO 13485 compliance, design-controls process adherence, traceability, document control, deviation/CAPA, audit readiness (FDA, Notified Body) |
| rd-lead | [agents/rd-lead.md](../agents/rd-lead.md) | R&D engineering execution across software/firmware/hardware; design output quality; technical debt; gap between architectural intent and implementation reality |
| regulatory-affairs | [agents/regulatory-affairs.md](../agents/regulatory-affairs.md) | 510(k)/De Novo/PMA/PCCP pathway selection, substantial-equivalence argumentation, predicate selection, FDA Q-Sub planning, standards mapping, IFU/labeling, CDS/SaMD classification |
| risk-management | [agents/risk-management.md](../agents/risk-management.md) | ISO 14971 hazard identification, risk analysis, risk controls, residual-risk and benefit-risk evaluation, post-market risk feedback |
| systems-engineering | [agents/systems-engineering.md](../agents/systems-engineering.md) | System architecture, requirements decomposition, interface management, module boundaries, traceability from user needs through design inputs to verification |
| vnv-lead | [agents/vnv-lead.md](../agents/vnv-lead.md) | V&V strategy, test protocol authoring/review, trace from tests back to design inputs and user needs, IEC 62304 software-testing requirements, design-transfer readiness |

### Security — owned by [`secops/`](secops/)

| Agent | File | Description |
|-------|------|-------------|
| project-secops | [secops/agents/project-secops.md](secops/agents/project-secops.md) | Security posture remediation agent — invoked when the `security-assert` SessionStart hook reports Critical/High failures. Parses results, walks the remediation playbook, and handles 30-day attestation cycles. Installed into `.claude/agents/` by `/secops setup` |

## Registry Structure

```
hitachi/
├── agents/                                # Published advisor bundle (symlinks into skills/advisors/agents/)
│                                          # plus project-secops symlink → skills/secops/agents/project-secops.md
└── skills/
    ├── manifest.md                        # This file — master index
    ├── advisors/                          # Persona subagents (regulatory, clinical, risk, …) — agents/
    ├── best-practices/                    # Project audit
    ├── change-control/                    # CC/GitHub ↔ Confluence/Windchill/Jira bridge
    ├── dhf-manifest/                      # 4-tier deliverable catalog — agents/
    ├── digest/                            # SessionStart morning briefing + CHANGELOG append
    ├── docflow/                           # Markdown ↔ DOCX/PDF/XLSX round-trip — agents/
    ├── docx/                              # Anthropic official Word skill
    ├── frontend-slides/                   # Zero-dep HTML presentations
    ├── jira-pull/                         # Jira mirror + drift detection
    ├── lessons/                           # Lessons-learned harvester
    ├── md-deck/                           # Markdown → single-file HTML deck
    ├── medtech-docs/                      # Regulated docs scaffold + compliance dashboard
    ├── pdf/                               # Anthropic official PDF skill
    ├── pptx/                              # Anthropic official PowerPoint skill
    ├── project-console/                   # FastAPI local console (agents / docs / dashboards)
    ├── secops/                            # Security posture — hooks, agents/, canonical permissions allow list
    ├── shared/                            # Cross-skill utilities (not a published skill)
    ├── skill-creator/                     # Skill authoring + evaluation — agents/
    ├── strategy/                          # Strategy harvester — agents/
    ├── sync-skills/                       # Registry ↔ project sync
    ├── task/                              # Task management + hooks
    ├── trace-matrix/                      # Design-controls trace matrix builder
    ├── tracker/                           # Submission package tracker — agents/
    ├── web-control/                       # Shared browser-automation infrastructure
    └── xlsx/                              # Anthropic official Excel skill
```

Each skill is a directory containing `SKILL.md` (the entrypoint) and optional supporting files. Simple skills have just `SKILL.md`. Skills with distributable content (like `medtech-docs`, `tracker`, `task`, `advisors`) include subdirectories for templates, scripts, hooks, or agents. Skills annotated `— agents/` above bundle one or more helper subagents under `skills/<name>/agents/`; of those, only the `advisors` and `secops` bundles are installed into a consumer project's `.claude/agents/`.
