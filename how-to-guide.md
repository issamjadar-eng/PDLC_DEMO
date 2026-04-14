# How-To: Stand Up a New MedTech PDLC Project

A reproducible walkthrough for starting a new regulated-device project using the Hitachi skill registry, `medtech-docs`, and the task/strategy skills. Every step is copy-pasteable; decisions that require human judgment are called out explicitly.

> **Status**: Skeleton / outline. Each step will be filled in as part of task 002. See `tasks/ben/002-how-to-guide-project-setup.md` for the authoring plan and open questions.

---

## Audience

A team lead or engineer who has been given a new device program and needs to turn an empty directory into a working DHF repository with design controls, standards, tasks, and an architecture-aligned DHF layout — the same shape PDLC_DEMO is in today. DHFs live under `docs/project/dhfs/<name>/` and can be top-level or arranged as parent→child (e.g., a `cloud-suite/` parent with per-service children).

## Flow at a glance

```
Phase 0 — Prerequisites
Phase 1 — Clone hitachi + install skills into .claude/
Phase 2 — Initialize the repo (git, gitignore, remote)
Phase 3 — Run /medtech-docs init  (scaffolds docs/, project.yml, CLAUDE.md, hooks)
Phase 4 — Personalize CLAUDE.md   (device identity, goals, scope, conventions)
Phase 5 — Create the first task   (001 project-init — captures the setup itself)
Phase 6 — Architecture & component strategy task
          → derive deployable components
          → decide DHF topology (top-level vs parent→child)
Phase 6.5 — Import applicable references (standards + FDA guidances)
            gated on: architecture + regulatory strategy docs populated
Phase 7 — Scaffold DHFs           (/medtech-docs add-dhf per component)
Phase 8 — Populate standards, frameworks, and sample inputs
Phase 9 — Ongoing registry sync with /sync-skills
Phase 10 — Troubleshooting
```

---

## Phase 0 — Prerequisites

- Claude Code installed and running
- `git` with SSH access to `GlobalLogic-a-Hitachi-Company/hitachi`
- `gh` CLI authenticated (needed later for `/sync-skills push`)
- `jq` on PATH (used by several skill scripts)
- A parent directory that will hold both your new project and the hitachi checkout as siblings — the default `local_path` in `project.yml` is `../hitachi`

## Phase 1 — Clone hitachi and install skills

_TODO: exact commands — clone hitachi as sibling, copy `skills/` and `agents/` into the new project's `.claude/`._

## Phase 2 — Initialize the repo

_TODO: `git init`, add remote, seed `.gitignore`. No skill runs yet — the task hooks are not wired._

## Phase 3 — Run `/medtech-docs init`

Run this **before** any `/task` command. Init is what installs and wires the `task` skill's hooks; running `task` first will fail the active-task gate.

`/medtech-docs init` asks ~8 project-context questions. Each answer shapes the scaffold:

| Question | What it controls |
|---|---|
| Device type (SaMD / SiMD / hardware / combination) | Which design-controls subfolders get created |
| Regulatory pathway (510(k) / De Novo / PMA / etc.) | Submissions scaffold and standards shortlist |
| Device class | Risk-management and V&V rigor defaults |
| AI/ML component? | Adds GMLP / PCCP folders and checklists |
| EHR integration? | Adds interop + HL7/FHIR standards stubs |
| Imaging? | Adds DICOM-related standards |
| Navigation/robotic? | Adds motion-safety standards |
| Existing docs to import? | Controls whether `docs/internal/source/` is pre-seeded |

_TODO: transcript of the prompts; link to `medtech-docs` SKILL.md._

## Phase 4 — Personalize `CLAUDE.md`

The init-generated `CLAUDE.md` is a template. Before any task work, replace the placeholders with:

- **Project identity** — device name, model number, predicate (if any), pathway
- **Scope statement** — what this repo is (DHF? portfolio? demo?) and what it is not
- **Working conventions** — carry over or adapt the conventions section (docs live in `docs/`, one task = one file, strategy/lessons captured in real time, etc.)
- **Demo vs. real disclaimers** — if this is a demo, say so explicitly so readers don't mistake fabricated data for real DHF evidence

Use this repo's `CLAUDE.md` as the reference shape.

## Phase 5 — Create the first task (`001-project-init`)

Now that init has wired the task hooks, create:

- `tasks/<person>/000-index.md`
- `tasks/<person>/001-project-init.md`

Task 001 records the setup work you just performed — prerequisites installed, skills copied, init answers, scaffold verified. This gives the task-gate hook an active task to gate against and makes the setup auditable. Use `tasks/ben/001-project-init.md` in this repo as the template.

## Phase 6 — Architecture & component strategy task

Before scaffolding DHFs, you need to know **what the deployable components are**. Open a new task (e.g., `002-architecture-strategy.md`) whose job is to:

1. Sketch the system as if you were deploying it today — users, external systems, data flows, trust boundaries.
2. Identify the deployable components. A component is anything that ships, updates, or gets regulated as a unit: a SaMD app, a pump firmware binary, a cloud service, a connectivity adapter, etc.
3. For each component, note: owner discipline (SaMD / SiMD / HW / cloud), regulatory status (in-scope / out-of-scope / supporting), and rough interface contract.
4. Decide the **DHF topology**: every project has at least one DHF (created by `init`). Most real programs have several. The rule of thumb is one DHF per independently-regulated or independently-deliverable component. DHFs can be top-level or nested parent→child (e.g., a `cloud-suite/` parent DHF with per-service child DHFs underneath).
5. Capture decisions as tagged strategy blocks (`<!-- STRATEGY CONTENT: architecture, ... -->`) so the `strategy` skill can harvest them into the shared strategy doc later.

The output of this task is a concrete list like:

```
dhfs/
  pca-device/           (primary — pump firmware + on-device UI)
  connectivity-adapter/ (BLE/WiFi gateway)
  cloud-suite/          (parent)
    ingest/
    clinician-portal/
    ...
```

PDLC_DEMO's current topology is the worked example.

> **Future capability**: this phase is prose-only today. A dedicated skill (e.g., `/medtech-docs plan-topology` or a standalone `architecture` skill) that walks the user through system sketch → component list → DHF topology as a reproducible flow is a likely follow-up once the prose version has been exercised on a second project.

## Phase 6.5 — Import applicable references

**Gate**: do not run this phase until the **architecture** and **regulatory** strategy docs are populated (at minimum). Those docs are what identify *which* standards, FDA guidances, and industry frameworks actually apply to this program — importing references before they exist leads to a pile of untargeted boilerplate in `docs/external/`.

Once the gate is met, use the `medtech-docs` skill to import each reference called out by the strategy docs:

- **Standards** named in the regulatory strategy (e.g., IEC 62304, ISO 14971, IEC 62366-1): `/medtech-docs add-standard <standard>`
- **FDA guidances** called out in the regulatory strategy (premarket, cybersecurity, SaMD, PCCP, etc.): `/medtech-docs import-guidance <title>`
- **Industry frameworks** named in the architecture strategy (e.g., NIST, OWASP ASVS, HL7/FHIR profiles): import via the same skill

Each import should land under `docs/external/` as a distilled markdown summary with `[VERIFY]` flags on anything that wasn't mechanically extractable. Do not fabricate clause text. Run `/medtech-docs dashboard` afterwards to confirm the imports registered.

> **Why this is a dedicated phase, not part of Phase 3**: `init` installs a *default* standards shortlist based on the 8 project-context answers. The strategy-driven import in this phase is narrower and higher-fidelity — it only pulls what the architecture and regulatory decisions actually require.

## Phase 7 — Scaffold DHFs

With the topology decided, run `/medtech-docs add-dhf <name>` for each additional component. The primary DHF already exists from Phase 3. For nested topologies, add child DHFs under their parent. Verify with `/medtech-docs dashboard` and `/best-practices` (the latter dispatches per-DHF subagents).

## Phase 8 — Populate standards, frameworks, and sample inputs

_TODO: pulling standards into `docs/external/`, mapping sample docs via `docflow`, seeding first design inputs._

## Phase 9 — Ongoing registry sync with `/sync-skills`

Covers `check`, `pull` (must analyze pulled changelogs for project impact — no silent pulls), `push` (PR-only default), `push --merge` (opt-in auto-merge), `sync`, and how to read `.claude/sync-log.md`. Safety properties: path guard, self-exclusion, branch-from-fresh-main, no direct pushes to main.

_TODO: flesh out with the full command reference currently in task 002 step 9._

## Phase 10 — Troubleshooting

_TODO: `jq` missing, SSH auth failure, hook registration conflicts, `gh` not authenticated, dirty hitachi working tree, task-gate hook firing before init completes._

---

## Open questions (to resolve while authoring)

- Final home for this doc: root `how-to-guide.md` (current), `docs/internal/`, or split into per-phase pages?
- How much of Phase 4 (CLAUDE.md personalization) can the init skill itself prompt for, reducing manual edits?
