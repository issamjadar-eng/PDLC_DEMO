# Bootstrap a New MedTech PDLC Project

A reproducible walkthrough for starting a new regulated-device project using the Hitachi skill registry, `medtech-docs`, and the task/strategy skills. Every step is copy-pasteable; decisions that require human judgment are called out explicitly.

> **Audience**: a team lead starting a brand-new device program from scratch. **Not** the doc you want if you're joining PDLC_DEMO — for that, see `setup.md` (machine setup) and `how-to-guide.md` (day-to-day use).
>
> This file was previously named `how-to-guide.md` at the repo root. It was renamed in task ben/069 (2026-05-30) when the contributor onboarding was overhauled to the arthrex three-file model (`setup.md` + `setup.sh` + `how-to-guide.md`). The Phase 0–10 bootstrap content here is unchanged from that rename.

---

## Audience

A team lead or engineer who has been given a new device program and needs to turn an empty directory into a working DHF repository with design controls, standards, tasks, and an architecture-aligned DHF layout — the same shape PDLC_DEMO is in today. DHFs live under `docs/project/dhfs/<name>/` and can be top-level or arranged as parent→child (e.g., a `cloud-suite/` parent with per-service children).

## Flow at a glance

```
Phase 0 — Prerequisites
Phase 1 — Clone hitachi + install skills into .claude/
Phase 2 — Initialize the repo (git, gitignore, remote)
Phase 3 — Run /medtech-docs init  (scaffolds docs/, project.yml, CLAUDE.md, hooks)
          → verify the scaffold (docs/ tree, project.yml, hook wiring, dashboard)
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

The `hitachi` registry is the source of truth for skills and agents. A skill is a **directory** (`skills/<name>/SKILL.md` + supporting files) — not a single file. Installing a skill means copying its directory into your project's `.claude/skills/`. (The hitachi `README.md` still shows an older `curl` single-file install under `.claude/commands/` — ignore it; the directory model in `skills/manifest.md` is current.)

Clone hitachi **as a sibling** of where your new project will live — `/sync-skills` later resolves the registry via `project.yml` → `registries[hitachi].local_path`, which defaults to `../hitachi`:

```bash
cd ~/projects                 # the parent that will hold both repos
git clone git@github.com:GlobalLogic-a-Hitachi-Company/hitachi.git
mkdir my-device && cd my-device
```

Install the skills and agents you want. The simplest first pass is to take everything — `/sync-skills` and `/best-practices` reconcile the set afterward:

```bash
mkdir -p .claude/skills .claude/agents
cp -R ../hitachi/skills/*/ .claude/skills/      # each <name>/ directory
cp    ../hitachi/agents/*.md .claude/agents/     # agent prompt files
```

> **Don't copy `skills/manifest.md` or `skills/shared/` blindly** — `manifest.md` is the registry index (not an installed skill), and `shared/` holds cross-skill helpers some skills import. Copy `shared/` only if a skill you installed references it; `/best-practices` will flag a missing dependency.

At minimum you need `medtech-docs`, `task`, and `best-practices` to follow this guide. The rest (`trace-matrix`, `dhf-manifest`, `tracker`, `strategy`, `docflow`, `sync-skills`, …) can be installed now or pulled later with `/sync-skills`.

## Phase 2 — Initialize the repo

No skill runs yet — the task-gate hooks aren't wired until Phase 3's `init`. Set up the bare git repo and a starter `.gitignore`:

```bash
git init
git branch -M main
# Seed .gitignore with the patterns init expects (it also adds its own):
cat > .gitignore <<'EOF'
_scratch/
**/_scratch/
.state/
**/PHI/**
.env
.venv/
__pycache__/
*.pyc
EOF
git add .gitignore && git commit -m "chore: init repo with starter gitignore"
```

Add the GitHub remote when you have one (needed later for `/sync-skills push` and any `gh` operations):

```bash
git remote add origin git@github.com:<your-org>/<your-repo>.git
```

You don't need to push yet. `/medtech-docs init` in Phase 3 generates `project.yml`, `CLAUDE.md`, and the `docs/` tree, which is your first real commit.

## Phase 3 — Run `/medtech-docs init`

Run this **before** any `/task` command. Init is what installs and wires the `task` skill's hooks; running `task` first will fail the active-task gate.

`/medtech-docs init` asks **9** project-context questions (it presents them all at once — answer in one block). Each answer shapes the scaffold. The canonical list lives in `.claude/skills/medtech-docs/SKILL.md` → `### init` → Step 1:

| # | Question | What it controls |
|---|---|---|
| 1 | Device type — SaMD / SiMD / combination / other | Which design-controls subfolders get created |
| 2 | Regulatory pathway — 510(k) / De Novo / PMA / not yet | Submissions scaffold and standards shortlist |
| 3 | **Modules/functions** the device has (e.g. planning, navigation, monitoring) | Seeds the module/component vocabulary used across design-controls |
| 4 | AI/ML in any module? | Adds GMLP / PCCP folders and checklists |
| 5 | Medical imaging (DICOM)? | Adds DICOM-related standards stubs |
| 6 | EHR integration (HL7 FHIR)? | Adds interop + HL7/FHIR standards stubs |
| 7 | Surgical navigation / real-time guidance? | Adds motion-safety standards |
| 8 | Existing docs to import? | Controls whether `docs/internal/source/` is pre-seeded |
| 9 | **Primary DHF name** (e.g. `pca-device`) — **required, no default** | Becomes the first `project.dhfs[]` entry and the `docs/project/dhfs/<name>/` folder |

> Q3 and Q9 are easy to miss but load-bearing: Q9 has no default and is what gives every project at least one DHF from day one (single-component projects are just N=1). Additional DHFs come later via `/medtech-docs add-dhf` (Phase 7).

After the questions, `init` creates `project.yml`, the `docs/` tree (external / internal / project tiers), per-folder READMEs (with `<!-- AUTO:STRUCTURE -->` sentinels rendered), a starter `CLAUDE.md`, and — critically — **wires the task-gate hooks**. That hook wiring is why `init` must precede any `/task` command (Phase 5).

### Verify the scaffold

Before building on the scaffold, confirm `init` landed everything. Five quick checks — all read-only:

```bash
# 1. The three-tier docs/ tree exists with READMEs at each level
find docs -maxdepth 2 -name README.md | sort
ls docs/external docs/internal docs/project

# 2. project.yml parses and has your primary DHF from Q9
jq -e '.dhfs[0].path' project.yml        # prints the DHF root, exits non-zero if absent
#   (project.yml is YAML, but the medtech-docs scripts also keep it jq-readable;
#    if jq errors, open it and confirm the project:, team:, and dhfs: blocks by eye)

# 3. The task-gate hook is wired into settings.json
jq '.hooks.PreToolUse' .claude/settings.json   # should reference check-active-task.sh

# 4. Sentinel blocks rendered (not left as empty AUTO:STRUCTURE stubs)
grep -rl 'AUTO:STRUCTURE' docs --include=README.md | head
```

Then run the dashboard for the first time — it's the fastest end-to-end confirmation that the scaffold is coherent:

```
/medtech-docs dashboard
```

It tallies per-folder document status and per-standard verification coverage. On a fresh scaffold everything reads as empty/`[VERIFY]` — that's expected; you're confirming the dashboard *runs* and sees the tree, not that content exists yet. If the dashboard errors on a missing folder or `project.yml` field, the scaffold is incomplete — re-run `/medtech-docs init` rather than hand-patching.

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

Once the gate is met, the `medtech-docs` skill imports references three ways — pick per source:

- **Bundled FDA guidance + standards + frameworks** — run `/medtech-docs update-external-references` (aliases: "import fda guidance", "pull reference guidances"). This reads your `project.yml`, `CLAUDE.md`, and strategy docs, applies an applicability rubric (pathway, device class, software/AI/imaging/EHR signals), and copies the matching **bundled distilled files** from the skill's `references/` into `docs/external/{fda-guidance,standards,industry-frameworks}/`. It is idempotent and never overwrites existing project files. This is the bulk first pass.
- **A specific standard not in the bundle** — `/medtech-docs add-standard <name>`. Prompts for title, the FDA guidance/regulation that references it, why it's required, and which modules it applies to; creates a distilled starter file and adds it to the folder README table.
- **A standard you considered but ruled out** — `/medtech-docs evaluate <name> not-required "<rationale>"`. Records the decision trail in the README's "Evaluated — Not Required" table without creating a file, so every standard you weighed has an auditable disposition.

> ⚠️ There is **no** `import-guidance` action — use `update-external-references` for FDA guidance. (Older drafts of this guide named a command that the skill doesn't recognize.)

Each import lands under `docs/external/` as a distilled markdown summary with `[VERIFY]` flags on anything not mechanically extractable. Do not fabricate clause text. Run `/medtech-docs dashboard` afterwards to confirm the imports registered (it tallies per-standard `## Verification Checks` coverage).

> **Why this is a dedicated phase, not part of Phase 3**: `init` seeds a *default* standards shortlist from the 9 project-context answers. The strategy-driven import here is narrower and higher-fidelity — it only pulls what the architecture and regulatory decisions actually require.

## Phase 7 — Scaffold DHFs

With the topology decided, run `/medtech-docs add-dhf <name>` for each additional component. The primary DHF already exists from Phase 3. For nested topologies, add child DHFs under their parent. Verify with `/medtech-docs dashboard` and `/best-practices` (the latter dispatches per-DHF subagents).

## Phase 8 — Populate standards, frameworks, and sample inputs

With references imported (Phase 6.5) and DHFs scaffolded (Phase 7), start filling content:

- **Convert any source documents you brought in** — if Phase 3 Q8 pre-seeded `docs/internal/source/` with corporate SOPs/templates (DOCX/PDF), run `/docflow adopt <path>` to produce reviewable markdown under `docs/internal/source-md/`. `docflow` owns the pandoc/soffice pipeline (direct calls are blocked by a hook), handles image extraction, frontmatter, and cross-refs.
- **Seed the first design inputs** — under each DHF's `design-controls/user-needs/` and `requirements/`, author the initial user needs and design inputs. Read the leaf folder's `README.md` first (naming + content rules are enforced there).
- **Stand up traceability early** — once a DHF has even a few inputs/requirements/tests, run `/trace-matrix init` for that DHF. `trace-matrix` generates project-adaptive parsers at init time (an IoC pattern — don't hand-edit the yml), then `/trace-matrix build` emits the controlled matrix + JSON sidecar.
- **Check completeness against obligations** — `/dhf-manifest` projects regulatory + QMS obligations into a per-DHF deliverable catalog with a gap report ("are the right documents present?"), complementing trace-matrix's intra-DHF edge checks.
- **Watch progress** — `/medtech-docs dashboard` for doc-status, `/tracker` for milestone/submission readiness, `/best-practices` for the shared-registry audit.

Everything above is incremental — there's no "all at once." A new project typically lands its first user needs and one DHF's trace matrix, then grows.

## Phase 9 — Ongoing registry sync with `/sync-skills`

`/sync-skills` keeps your installed `.claude/skills` + `.claude/agents` aligned with hitachi, **bidirectionally**. It resolves the registry from `project.yml` → `registries[hitachi].local_path` (default `../hitachi`), and only ever touches `skills/` and `agents/` — never `project.yml`, `.git/`, or anything else. (Current skill version: **v8.2**.)

**`/sync-skills status`** — start here. A read-only, four-surface health check ("are we synced?"): project working tree, project HEAD⇄origin, registry working tree, registry HEAD⇄origin, plus skill-drift counts. Ends in `Overall: SYNCED` or `NOT SYNCED — see <block>`. Run it before switching machines.

**`/sync-skills check`** — read-only diff in both directions. Classifies each file: `UPSTREAM_ONLY` (pull candidate), `LOCAL_ONLY` (push candidate), or `UPSTREAM_NEWER` — and for the last, a three-way recommendation: `UPSTREAM_ADVANCE` (safe to pull), `LOCAL_AHEAD` (your copy is newer — push it), or `BOTH_DIVERGED` (manual diff review).

**`/sync-skills pull`** — apply upstream changes, interactively. The key safety property (added in v8 after a bulk-approve clobbered 1131 lines of un-pushed work): `pull` runs mandatory three-way blob-history bucketing and **never auto-applies** `LOCAL_AHEAD` or `BOTH_DIVERGED` files. The default action is "approve the auto-pull bucket only." After applying, it runs a **mandatory Project Impact analysis** — reads every pulled file's changelog + `**Post-update:**` notes and tells you what your project must do (re-run a `setup` action, regenerate a template-derived file, run `/best-practices` for new checks, grep for a renamed term). No silent pulls — if nothing is needed, it says so explicitly.

**`/sync-skills push [--merge] <files…>`** — contribute local fixes upstream. **PR-only by default**: branches from fresh `origin/main`, commits, pushes, opens a PR via `gh`, and stops. Pass `--merge` (or say "push and merge") to opt into `gh pr merge --squash --delete-branch` + fast-forward of the local hitachi checkout. Use `--merge` only for changes you're confident in (your own skill authoring, trivial fixes) — it bypasses human review.

**`/sync-skills sync`** — convenience wrapper: `pull` first, then offer the remaining push candidates.

**`/sync-skills prune`** — branch hygiene. PR-only pushes leave merged `sync/*` branches behind on both sides (they accumulate — one cleanup cleared 111). `prune` dry-runs first, classifies each `sync/*` branch MERGED/UNMERGED against `main`, deletes only MERGED on `--apply`, and never touches `main` or unmerged work.

**Reading `.claude/sync-log.md`** — every `pull` and `push` appends a dated entry (hitachi HEAD, files moved, PR URL, merge status, follow-ups). It's the audit trail for "where did this skill version come from." `prune` deliberately writes **no** entry — it's hygiene, not a sync.

**Safety properties to trust**: path guard (only `skills/`/`agents/`), `sync-skills` self-excluded from its own diffs, `push-prep` always branches from fresh `origin/main`, the script refuses to push directly to `main`, and `push` refuses if the hitachi working tree is dirty.

## Phase 10 — Troubleshooting

| Symptom | Cause / Fix |
|---|---|
| Skill scripts error on missing `jq` | `jq` isn't on PATH. `brew install jq` (macOS) / `apt install jq`. |
| `git clone` of hitachi fails with auth error | SSH key not registered with GitHub, or no access to `GlobalLogic-a-Hitachi-Company/hitachi`. Test with `ssh -T git@github.com`; request repo access if you get a 403. |
| Task-gate hook denies an edit right after `init` | Expected — you have no active task yet. The denial prints the exact `bash .claude/hooks/task-activate.sh add <session> <task>` command. Do Phase 5 (create task 001) first; never bypass the gate. |
| `/task` fails before `init` was run | Ordering violation — `init` installs the task hooks. Run `/medtech-docs init` first (Phase 3). |
| `/medtech-docs import-guidance …` "unknown action" | That action doesn't exist. Use `/medtech-docs update-external-references` (Phase 6.5). |
| `/sync-skills push` fails at PR creation | `gh` not authenticated. `gh auth login`, then re-run `push` — the commit is already on the branch, so it reuses it. |
| `/sync-skills push` refuses to start | hitachi working tree is dirty. `git -C ../hitachi status`, then commit/stash/clean it. `pull` still works on a dirty tree (reads `origin/main`). |
| Pulled a skill but `/best-practices` flags a missing dependency | The skill imports something under `skills/shared/` you didn't copy. `cp -R ../hitachi/skills/shared/ .claude/skills/shared/`. |
| `<!-- AUTO:STRUCTURE -->` tables look stale after adding folders | Re-render: `python3 .claude/skills/medtech-docs/scripts/render-sentinels.py <README>`. `add-dhf` and `best-practices fix` do this for you. |

---

## Resolved decisions & open questions

**Resolved (2026-05-30):**

- **Doc home** — stays at repo root as `new-project-bootstrap.md` (renamed from `how-to-guide.md` under task ben/069). Sibling of `setup.md` (contributor machine setup), `setup.sh` (installer), and the new `how-to-guide.md` (day-to-day usage for contributors). Four peer entry points at root, three audiences (new contributor onboarding × 2 + day-to-day usage + new-program bootstrap). None belong under `docs/`, which is the *output* of the processes these guides describe.

**Resolved (2026-05-21):**

**Still open:**

- Should Phase 6 (architecture → component list → DHF topology) become its own skill rather than prose? Deferred until the prose flow has been exercised on a second project — flagged inline as a future capability.
- How much of Phase 4 (CLAUDE.md personalization) can `init` prompt for directly, reducing manual edits?

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| 2026-05-30 | Ben Xavier | Renamed from `how-to-guide.md` → `new-project-bootstrap.md` under task ben/069. Audience clarification banner added; Phase 0–10 content unchanged. The freed `how-to-guide.md` slot is being rewritten as a day-to-day-usage guide for new contributors (arthrex three-file model). |
| 2026-05-21 | Ben Xavier | Filled all skeleton TODOs (Phases 1, 2, 8, 9, 10) under task 002. Corrected three drift findings verified against the live SKILLs: init asks **9** questions not "~8" (added Modules/functions + Primary DHF name to the table); replaced the non-existent `/medtech-docs import-guidance` with `update-external-references`/`add-standard`/`evaluate`; expanded Phase 9 to sync-skills **v8.2** (`status`, `prune`, three-way pull bucketing). Resolved doc-home open question (stays at root, sibling of `setup.md`). Added companion-doc cross-reference. |
| 2026-04-13 | Ben Xavier | Initial skeleton — 10-phase outline created under task 002. |
