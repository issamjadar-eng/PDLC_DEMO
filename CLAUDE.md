# PDLC_DEMO

## Project Overview

Demonstration project for **agentic workflows across the Product Development Life Cycle (PDLC) in MedTech**. The lead product is the **PainEase PCA Advanced (PP3500)** — a patient-controlled analgesia (PCA) infusion pump cleared under K210345, predicate PP3000 (K190567). The DHF, design controls, V&V, and submission artifacts in this repo all anchor on PP3500.

A broader 5-device infusion portfolio (IP5000, PP3000, PP3500, SP6000, SP6500) is retained as **portfolio context and predicate reference** under `docs/project/input-analysis/predicate-analysis/`, but PP3500 is the DHF anchor. The product is a combination of SaMD components, SiMD pump firmware, and custom medical electrical hardware.

The demo exercises a full MedTech project footprint: Design History File (DHF) artifacts, regulatory and standards policies, corporate SOPs, submission materials, and illustrative embedded/SaMD code.

## Project Structure

```
.
├── project.yml             # Project manifest (see below)
├── docs/                   # MedTech documentation (three-tier: external / internal / project)
├── src/                    # Demo device code (SaMD + pump firmware placeholders)
├── .claude/
│   ├── skills/             # Installed skills (medtech-docs, task, docflow, ...)
│   ├── agents/             # Installed agents (project-secops, ...)
│   └── hooks/              # Shared hook infrastructure
└── CLAUDE.md               # This file
```

## Information Flow

```
external/  ──── defines rules ───▶ project/  ◀─── converts ──── internal/
(FDA, ISO,                         (DHF, design                  (corp SOPs,
 IEC, clinical lit)                 controls, submissions)        templates)
```

- **External** — authoritative outside sources (FDA guidances, standards, frameworks, clinical literature). Treated as read-only upstream truth; each distilled to a markdown summary with verification checks.
- **Internal** — corporate SOPs, procedures, templates. `source/` holds the original files (PDF/DOCX); `source-md/` holds markdown conversions used by agents.
- **Project** — everything specific to this device program: input analysis → design controls → submissions. The heart of the DHF.

### Project Manifest — `project.yml`

`project.yml` is the **single source of truth** for project identity, team roster, skill registries, and security policy. It lives in the project root and is read by skills, hooks, and automation scripts.

**What it contains:**

| Section | Purpose |
|---------|---------|
| `project:` | Project name, repo, type, regulatory pathway, device class, device family, composition, capabilities |
| `team:` | Active and inactive team members — name, GitHub username, task folder, role, email. Every repo collaborator must have a row here. |
| `registries:` | Approved sources for skills and templates. Skills are either `builtin` (shipped with Claude Code) or fetched from a `github` registry. Each `github` registry has a `local_path` (default `../hitachi`) for local clone-based sync used by `/sync-skills` and `/best-practices`. |
| `security:` | Approved email domains, gitignore patterns, and allowlists for skills, MCPs, plugins, and agents |

**Security allowlists** — when adding new skills, MCP servers, plugins, or agents to the project, add them to the corresponding `approved_*` list in `project.yml` first. The security posture check warns on anything installed but not listed. This ensures the team can audit what tools have access to project data.

**Team roster** — when onboarding a new team member, add their entry to `team.active`. When someone leaves, move them to `team.inactive` with a `removed` date and `reason`. The `setup.sh --check` audit cross-references this roster against actual GitHub repo collaborators.

## Working Conventions

- **Documentation lives in `docs/`**, never in scattered READMEs around the repo.
- **Working markdown at the root** of each design-controls / submissions leaf folder; **controlled deliverables** (DOCX/XLSX) in the matching `formal/` subfolder.
- **Every README has a `## Conventions` and `## Changelog` section.** When you edit a README, add a changelog row — AI-driven sessions collapse many edits into one commit, and the changelog captures the rationale git alone doesn't.
- **Do not fabricate standard content.** Starter files pulled from `.claude/skills/medtech-docs/references/` are distilled from real documents; anything unverified is flagged with `[VERIFY]`.
- **Capture strategy and lessons as they happen.** When a decision is made during task work that belongs to a strategy domain (architecture, regulatory, commercial, development, testing, risk, postmarket, operations), add it to the active task's strategy section in real time under a `<!-- STRATEGY CONTENT: domain, topics -->` block — not as a deferred cleanup pass. Same rule for lessons: when a correction or insight lands, add a `<!-- LESSONS LEARNED: category -->` block to the active task in the same turn. A decision that touches two domains goes in two blocks, not one. The user should never have to ask "did you capture that?"
- **One task, one file.** All design work, analysis, planning, phase deliverables, and drafted content produced under a task belong **inside that task's numbered markdown file** as new sections — never as sibling files like `NNN-task-p1-design.md` or `NNN-task-notes.md`. Subagents must be told to write into the task doc, not to create satellite files. If an artifact is genuinely meant to live elsewhere permanently (e.g., a new doc in `docs/`), the task still records what was produced and points to the real location. Default: capture-in-task unless explicitly told otherwise.

## Skills & Agents

Installed skills live in `.claude/skills/` and are listed in `project.yml` under `security.approved_skills`. Key skills for this project:

| Skill | Purpose |
|-------|---------|
| `medtech-docs` | Scaffold and manage DHF/regulatory documentation |
| `docflow` | Convert source documents (PDF/DOCX) into reviewable markdown |
| `task` | Task management with active-task gating |
| `strategy` | Regulatory and product strategy authoring |
| `tracker` | Render compliance/progress dashboards |
| `lessons` | Capture lessons learned across the program |
| `best-practices` | Audit the project against the skill registry |
| `skill-creator` | Author new skills (meta) |

Agents live in `.claude/agents/`. `project-secops` audits the security posture of the project against `project.yml`.

## Task-First Workflow

All non-trivial work starts with an active task. The `/task` skill manages task documents under `tasks/<person>/NNN-<name>.md`; a `PreToolUse` hook (`.claude/hooks/check-active-task.sh`) denies Edit/Write/NotebookEdit when no task is active for the current session.

To start work:
1. Run `/task find <description>` — surfaces active tasks matching the topic, or creates a new one.
2. If the gate denies an edit, the denial message includes the exact `bash .claude/hooks/task-activate.sh add <SESSION_ID> <TASK_ID>` command to run.
3. Capture Strategy and Lessons Learned **inline** in the task doc using the required HTML-comment markers (`<!-- STRATEGY CONTENT: ... -->`, `<!-- LESSONS LEARNED: ... -->`) so the `/strategy` and `/lessons` harvest skills can find them.

Exempt paths (edits allowed without an active task): `tasks/*`, `.claude/state/*`, `.claude/settings*.json`, `.claude/sync-log.md`, `.claude/MEMORY.md`, `.claude/memory/*`. Everything else — including `.claude/skills/**`, `.claude/hooks/*`, `.claude/agents/*`, `CLAUDE.md`, `project.yml`, `docs/**` — is gated.

## Lessons Learned

Team-shared lessons staging lives at `tasks/lessons-ledger.md`. The `/lessons` skill harvests `<!-- LESSONS LEARNED -->` blocks from task docs into the ledger's `## Staged` section; mature lessons are promoted to their permanent home (skill, this CLAUDE.md, an agent prompt, a `.claude/rules/` file, `glossary.md`, a standard's applicability notes, or a folder README). Only `## Staged` is loaded at session start — `## Promoted` and `## Archived` are audit-only.

## Demo Scope

This is a **demonstration**, not a regulatory submission. Fabricated clinical data, placeholder predicates, and non-binding analyses are acceptable — but all such content must be marked clearly (e.g., `_Demo sample data — not for clinical use._`) so readers never mistake the demo for real DHF evidence.

## For Claude

- **Respect the task gate.** If a tool call is denied because no active task is set, follow the exact recovery command printed in the denial. Never try to bypass the gate.
- **Never fabricate standard, clinical, or regulatory content.** Anything not derivable from a distilled source in `docs/external/` or `docs/internal/source-md/` must be flagged `[VERIFY]` inline.
- **One task, one file.** Do not create `NNN-task-p1.md` sibling files or ad-hoc writeup docs — append sections to the active task doc. If an artifact genuinely belongs elsewhere (e.g., a new doc in `docs/`), the task still records what was produced and points to the real location.
- **Capture strategy and lessons in real time.** When a decision, trade-off, or non-obvious insight surfaces during task work, add a `<!-- STRATEGY CONTENT: domain, topic -->` or `<!-- LESSONS LEARNED: category -->` block to the active task in the same turn — not as a deferred cleanup pass.
- **READMEs have `## Conventions` and `## Changelog` sections.** When editing a README under `docs/`, append a changelog row describing the rationale (AI sessions collapse many edits into one commit; the changelog captures context git alone doesn't).
- **Do not mark demo content as real DHF evidence.** Every fabricated clinical datum, placeholder predicate, or illustrative analysis carries the `_Demo sample data — not for clinical use._` banner near the top.
