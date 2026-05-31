# PDLC_DEMO

Demonstration project for **agentic workflows across the Product Development Life Cycle (PDLC) in MedTech**. The lead product is the **PainEase PCA Advanced (PP3500)** — a patient-controlled analgesia (PCA) infusion pump cleared under K210345, predicate PP3000 (K190567).

This is a working **demo**, not a regulatory submission. Fabricated clinical data, placeholder predicates, and illustrative analyses are acceptable; all such content carries the `_Demo sample data — not for clinical use._` banner.

## Where to start

### 🧑‍💻 New to PDLC_DEMO? Pick your onboarding path

| If you… | Read |
|---|---|
| Are joining the team and need to **set up your laptop** (admin → installs → repo clone → security posture) | [`setup.md`](setup.md) — accompanied by [`setup.sh`](setup.sh), the idempotent installer |
| Already have your laptop set up and want to learn **day-to-day usage** (open VS Code, `git pull`, launch Claude Code, navigate the project, use skills) | [`how-to-guide.md`](how-to-guide.md) |
| Want to **start a brand-new, *different* MedTech project** using the same skill stack — clone the hitachi registry, run `/medtech-docs init`, scaffold your own DHFs for a different device. You are NOT joining PDLC_DEMO; you are *replicating the pattern* for a different program. | [`new-project-bootstrap.md`](new-project-bootstrap.md) |

> Each doc opens with the same "📍 You are here" decision banner so you can confirm at a glance you're on the right one. The third row is the easy one to get wrong — `new-project-bootstrap.md` is for *replicators*, not for contributors joining PDLC_DEMO.

### 📖 Looking for specific content?

| If you want to… | Read |
|---|---|
| Understand the project at a high level | [`project-overview.md`](project-overview.md) |
| See the canonical project guide for Claude Code sessions | [`CLAUDE.md`](CLAUDE.md) |
| Read the agentic-delivery thought-leadership writing | [`articles/`](articles/) — [`articles/README.md`](articles/README.md) |
| Browse the DHF, design controls, and submissions | [`docs/project/`](docs/project/) |
| See corporate SOPs and templates | [`docs/internal/`](docs/internal/) |
| See FDA guidance, standards, and frameworks (read-only upstream) | [`docs/external/`](docs/external/) |
| See the active task ledger | [`tasks/`](tasks/) — start with [`tasks/ben/000-index.md`](tasks/ben/000-index.md) |
| Run the local project console (FastAPI agents/dashboards) | [`tools/project-console/`](tools/project-console/) |
| See the project manifest (team roster, registries, security policy) | [`project.yml`](project.yml) |

## Project structure

```
.
├── project.yml             # Single source of truth: identity, team, registries, security policy
├── CLAUDE.md               # Canonical project guide for Claude Code sessions
├── project-overview.md     # Project at a glance
├── articles/               # Thought-leadership writing (whitepapers, decks)
├── docs/                   # Three-tier MedTech documentation
│   ├── external/           # FDA guidances, ISO/IEC standards, clinical literature (read-only upstream)
│   ├── internal/           # Corporate SOPs, procedures, templates
│   └── project/            # DHF, design controls, submissions for PP3500
├── src/                    # Demo device code (SaMD + pump firmware placeholders)
├── scripts/                # Build/render automation (e.g., whitepaper PDF render)
├── assets/                 # Generated artifacts (decks, project-overview HTML, etc.)
├── tasks/                  # Task documents organized by team member
├── tools/project-console/  # Local FastAPI console (agents, documents, dashboards)
├── .claude/                # Skills, agents, hooks, settings
├── glossary.md             # Project-wide term definitions
├── setup.md                # New contributor onboarding — admin → installs → repo → security
├── setup.sh                # Idempotent installer (mac / WSL / linux; --check mode)
├── how-to-guide.md         # Day-to-day usage for contributors (after setup)
├── new-project-bootstrap.md # How to stand up a brand-new MedTech project from scratch
└── CHANGELOG.md            # Project-wide change log
```

## Information flow

```
external/  ──── defines rules ───▶ project/  ◀─── converts ──── internal/
(FDA, ISO,                         (DHF, design                  (corp SOPs,
 IEC, clinical lit)                 controls, submissions)        templates)
```

## Tooling

The project is driven by **Claude Code** with a curated set of installed skills (under `.claude/skills/`) — the relevant ones are listed in [`project.yml`](project.yml) under `security.approved_skills`. Key entry points:

- `/task` — manages task documents under `tasks/<person>/NNN-<name>.md`. A `PreToolUse` hook denies edits when no task is active for the current session; the denial message includes the exact recovery command.
- `/medtech-docs` — scaffolds and manages DHF / regulatory documentation.
- `/docflow` — converts source documents (PDF / DOCX / XLSX) into reviewable markdown and back.
- `/strategy`, `/lessons` — harvest tagged inline content from task docs into shared strategy and lessons-learned ledgers.
- `/best-practices` — audits the project against the skill registry.
- `/sync-skills` — bidirectional sync between `.claude/skills/` and the upstream registry.

## Conventions

- **Documentation lives in `docs/`**, never in scattered READMEs around the repo. The exception is `articles/` for long-form thought-leadership writing.
- **Working markdown at the root of each design-controls / submissions leaf folder; controlled deliverables (DOCX/XLSX) in the matching `formal/` subfolder.**
- **Every README has a `## Conventions` and `## Changelog` section.** AI-driven sessions collapse many edits into one commit; the changelog captures rationale that git alone doesn't.
- **Do not fabricate standard content.** Starter files pulled from `.claude/skills/medtech-docs/references/` are distilled from real documents; anything unverified is flagged with `[VERIFY]` inline.
- **One task, one file.** All design work, analysis, planning, phase deliverables, and drafted content produced under a task belong **inside that task's numbered markdown file** as new sections — never as sibling files.
- **Strategy and lessons captured in real time** via `<!-- STRATEGY CONTENT: domain, topic -->` and `<!-- LESSONS LEARNED: category -->` blocks inside the active task document.
- **Demo content carries the `_Demo sample data — not for clinical use._` banner** wherever fabricated clinical data, placeholder predicates, or illustrative analyses appear.

## Changelog

| Date | Change | Why |
|---|---|---|
| 2026-05-30 | Split "Where to start" into two sub-tables: "🧑‍💻 New to PDLC_DEMO? Pick your onboarding path" (the three onboarding docs — setup.md, how-to-guide.md, new-project-bootstrap.md — surfaced as the top-of-README entry point) + "📖 Looking for specific content?" (existing rows). Added an explicit warning that `new-project-bootstrap.md` is the easy doc to get wrong (replicators, not contributors). Under task ben/069. |
| 2026-05-01 | Root `README.md` authored | Provide a discoverable entry point alongside `CLAUDE.md` (project-internal) and `project-overview.md` (subject-matter); `articles/` relocated whitepapers needed a top-level pointer |
