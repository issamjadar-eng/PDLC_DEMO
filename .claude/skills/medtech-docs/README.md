# MedTech Docs Skill — Design & Architecture

This document describes the design decisions behind the medtech-docs skill. It is not loaded by Claude during normal skill operation — it exists for human understanding.

For skill usage and instructions, see `SKILL.md`.

## Overview

The medtech-docs skill is the **project scaffolding entry point** for regulated medical device projects. It creates the docs/ folder hierarchy, determines applicable standards, generates a compliance dashboard, and initializes project infrastructure (`project.yml`, hooks, skill setup).

## Role in the Ecosystem

medtech-docs is the orchestrator — it sets up everything a new project needs:

```
/medtech-docs init
  ├─ docs/ folder hierarchy (3-tier: external, internal, project)
  ├─ README.md for every folder (meta-model compliant)
  ├─ Standards/frameworks evaluation
  ├─ project.yml (team roster, security config, registries)
  ├─ .claude/hooks/register-hook.sh (shared hook infrastructure)
  └─ Skill setup actions (calls /task setup, etc.)
```

## Dependencies

| File | Required by | Purpose | How to create |
|------|-------------|---------|---------------|
| None | — | This skill has no dependencies — it creates project infrastructure from scratch | — |

medtech-docs is the **root of the dependency chain**. Other skills depend on the files it creates (project.yml, tasks/, etc.), but medtech-docs itself has no prerequisites.

## Key Design Decisions

### Three-Tier Documentation Structure

```
docs/
  external/    → Reference material (FDA guidance, standards, frameworks)
  internal/    → SOPs, procedures, templates (source → markdown → distilled)
  project/     → What we're building (input analysis, design controls, submissions)
```

This separates concerns: what we read (external), how we work (internal), and what we produce (project). Each tier has its own conventions and information flow.

### README Meta-Model

Every README.md follows a strict section order:
1. Title + purpose
2. Structure/Subfolders (if applicable)
3. Information Flow (if applicable)
4. Expected Content (if leaf folder)
5. Domain-specific sections
6. Conventions (required)
7. For Claude (optional)
8. Changelog (required)

This ensures consistency across 30+ READMEs and allows automated validation by the best-practices skill.

### Project Infrastructure Creation

The `init` action creates project-level files that other skills depend on:
- **`project.yml`** — team roster, security policy, registries. Seeded from registry manifests and environment auto-detection.
- **`.claude/hooks/register-hook.sh`** — shared helper for skill hook registration. Installed from `templates/register-hook.sh`.

### Skill Setup Convention

After installing skills, `init` runs each skill's `setup` action (if it has one). This allows skills to self-wire their hooks and config without medtech-docs knowing the details. The convention:
1. Scan `.claude/skills/*/SKILL.md` for a `### setup` action
2. If found → invoke it
3. If not → skip silently

### Registry-Seeded Allowlists

`project.yml` allowlists are populated from approved registries:
- **Builtin** (Anthropic): hardcoded list of official skills
- **GitHub** registries: fetch manifest.md, parse Published Skills table
- Auto-detect MCPs and plugins from environment

### Auto-Loaded Rules — Skill-Owned and Symlinked

medtech-docs owns two **auto-loaded rules** — markdown files under `.claude/rules/` that Claude Code loads into every session:

| Rule | What it governs |
|------|-----------------|
| `readme-before-write.md` | Before any write under `docs/`, read the target folder's README **and** its parent's. Parent READMEs carry cross-cutting conventions; leaf READMEs carry folder-specific naming/content rules. Misplaced files are a compliance risk in a regulated project. |
| `sentinel-blocks.md` | The `<!-- AUTO:STRUCTURE -->` sentinel convention — the contract for `scripts/render-sentinels.py` and `/best-practices fix`: a fenced, tool-owned region inside an otherwise human-owned doc, so structural tables (folder trees, DHF rosters) can be regenerated without clobbering narrative. |

**Why medtech-docs owns them.** Both rules govern the `docs/` tree and the README scaffolding that *this skill* creates — and the sentinel renderer is this skill's own code (`scripts/render-sentinels.py`). The rule that documents a script's contract belongs with the script. (`/best-practices fix` merely *calls* the renderer — it's a consumer, not the owner.)

**Why symlink, not copy.** `init` Step 2c Checks 3 & 4 install each rule as a **symlink** — `.claude/rules/<rule>.md` → `../skills/medtech-docs/rules/<rule>.md` — not a copy. The canonical text lives once, inside the skill at `rules/`. A `/sync-skills pull` that updates medtech-docs then auto-updates the installed rule, with no drift and no stale duplicate to audit. This is the same self-contained install pattern the registry uses for hooks and agents (see skill-creator's "Self-Contained Skills & Symlink Pattern"). A project that needs to diverge **forks** the symlink into a regular file; `/sync-skills` leaves forks alone.

**How they're used.** `.claude/rules/` files are auto-loaded every session — no CLAUDE.md insertion needed. `readme-before-write` gates every `docs/` write; `sentinel-blocks` is the spec the renderer and audit-fix consult. The rule sources version *with the skill*: any new sentinel `kind` is a simultaneous edit to `rules/sentinel-blocks.md` and `scripts/render-sentinels.py`.

## Templates

Scaffold content lives in `templates/`; auto-loaded rule sources live in `rules/`:
- 11 README templates for the docs/ hierarchy
- 1 standard file template
- 1 dashboard HTML template
- 1 register-hook.sh helper
- 2 rule sources in `rules/` — `readme-before-write.md`, `sentinel-blocks.md` (symlinked into `.claude/rules/` by `init`)

Templates use `{{PLACEHOLDER}}` substitution for leaf folder READMEs and `${CLAUDE_SKILL_DIR}` for file paths.

## Changelog Context

Major version milestones:
- v1: Initial scaffold with init, add-standard, evaluate, dashboard
- v3: Migrated to skills/ directory, extracted templates
- v5: README meta-model with strict section ordering
- v7: Formal/ subfolder pattern for controlled documents
- v8: Synced templates with actual docs/ state, added project infrastructure creation
- v24 (2026-05-15): Rule ownership moved to the symlink-install pattern. The `readme-before-write` and `sentinel-blocks` rules now ship as canonical sources under `rules/` (sentinel rule relocated from `templates/rule-sentinel-blocks.md`; readme-before-write previously inlined in `init` Check 3 with no bundled file). `init` Step 2c Checks 3 & 4 now **symlink** them into `.claude/rules/` instead of copying — so `/sync-skills pull` auto-updates installed rules, matching the hooks/agents pattern. New README design section "Auto-Loaded Rules — Skill-Owned and Symlinked". Project-task reference removed from the sentinel rule (skill files stay project-agnostic).
- v23 (2026-05-04): `render-sentinels.py` enhancements — `dhf-table` now reads `architecture_name`/`marketed_name`/`dhf_purpose` from `project.yml dhfs[]` (fallback to preserve-column then `TODO`); new `variant=` dispatcher for `dhf-table` with `default`/`naming`/`flat-multi` schemas; `folder-tree` and `folder-tree-subset` now support `depth=N` recursion (defaults 1 and 2 respectively, hard-capped at 4) with proper `├── │   └──` connectors. Graceful handling of `class: non-device` (drops "Class X" prefix). New `tests/test_render_sentinels.py` — 11 assertions cover variants, depth, idempotence, fallback chains, and error paths.

## Best Practices

<!-- Read by /best-practices skill to audit project setup -->

**Scope column** — added in v12 to support the unified DHF shape. Values:
- `shared` — check runs once at project root.
- `per-dhf` — check runs once per entry in `project.dhfs[]`, with the DHF root as the implicit working directory. Path references in "How to Verify" below that start with `dhfs/<path>/` are interpreted relative to that DHF's root; paths without a `dhfs/` prefix are project-relative.
- `per-submission` — check runs once per `submissions/<filing>/` folder.
- `cross-cutting` — check runs once at project root but reads across multiple DHFs (enumerates `project.dhfs[]` and correlates).

Omitted Scope defaults to `shared` (per task 007 ambiguity #1 sign-off).

| Check | How to Verify | Severity | Scope |
|-------|--------------|----------|-------|
| Project manifest exists | `project.yml` exists in project root with `project:`, `dhfs:`, `team:`, `registries:`, and `security:` sections | Required | shared |
| Project has at least one DHF | `project.yml` `dhfs[]` list is non-empty, and every entry's `path` resolves to an existing folder under `docs/project/dhfs/` | Required | cross-cutting |
| DHF leaf names are unique | For every entry in `project.yml` `dhfs[]`, the last segment of `path` is unique across the list (case-sensitive). | Required | cross-cutting |
| DHF identity names present | Every entry in `project.yml` `dhfs[]` carries both `architecture_name` (technical/internal name) and `marketed_name` (commercial/customer-facing name). Both are strings; either may differ from the `leaf` slug. WARN if either is missing on any entry — downstream tools (submissions, dashboards, trace tooling) need both to render context-appropriate names. | Recommended | cross-cutting |
| Per-DHF Jira binding references valid project | If `change_control.jira.project_keys` is set in `project.yml`, every `dhfs[]` entry that includes a `jira:` block must have its `jira.project_key` appear in that list. FAIL on any reference to an unknown project key. INFO if a DHF has no `jira:` block at all (DHFs without a Jira binding are valid; system DHFs in particular often have none). | Required | cross-cutting |
| Per-DHF Confluence binding references valid space | If `change_control.spaces[]` is set in `project.yml`, every `dhfs[]` entry that includes a `confluence:` block must have its `confluence.space_key` appear in some entry's `key` field. FAIL on any reference to an unknown space key. INFO if a DHF has no `confluence:` block at all. | Required | cross-cutting |
| Per-DHF evidence file paths exist | For every `dhfs[]` entry that has an `evidence:` block, every leaf path inside it (`xlsx`, `page`, paths inside `xlsx_variants[]`) must resolve to an existing file or folder on disk. FAIL on broken references — these are stale pointers to artifacts that have been moved or removed. | Required | cross-cutting |
| Item DHFs declare classification | Every `dhfs[]` entry with `role: item` carries a `classification:` block with at least `samd` (bool) and `class`. WARN if missing or contains `tbd`. | Recommended | cross-cutting |
| Docs folder exists | `docs/` directory exists with `README.md` | Required | shared |
| Three-tier structure | `docs/external/`, `docs/internal/`, `docs/project/` all exist | Required | shared |
| Strategies folder exists | `docs/project/strategies/` directory exists with `README.md` | Required | shared |
| DHF README exists | `dhfs/<path>/README.md` exists and contains a purpose paragraph | Required | per-dhf |
| Design controls folder complete | All 7 design control subfolders exist under this DHF: `design-controls/{trace-matrix, plans, user-needs, requirements, architecture, vnv, tool-validation}` | Required | per-dhf |
| Risk management folder exists | `risk-management/` folder exists at the DHF root (sibling of `design-controls/`, not a child) with a `formal/` subfolder | Required | per-dhf |
| Clinical folder complete | `clinical/{evaluation-plans, benefit-risk, literature-search}` all exist under this DHF. Empty leaves are acceptable for early-stage DHFs and reported as INFO. | Recommended | per-dhf |
| Postmarket folder complete | `postmarket/{pmcf-plans, pmcf-studies, capa, complaints}` all exist under this DHF. Empty leaves acceptable and reported as INFO. | Recommended | per-dhf |
| Cybersecurity folder exists | `cybersecurity/` folder exists at DHF root with a `formal/` subfolder. Empty folder acceptable and reported as INFO. | Recommended | per-dhf |
| Platform DHFs have children | For every DHF with `regulatory: mixed`, at least one other `dhfs[]` entry has `parent` pointing to it. Prevents `mixed` from being used to silence the unreferenced-DHF check on leaf components. | Required | cross-cutting |
| Composition manifests referenced | If `dhfs[]` is non-empty AND `submissions/*/composition-manifest.md` glob returns zero matches, emit project-level WARN: "No composition manifests authored — per-submission checks will not run until at least one exists." | Recommended | cross-cutting |
| Standards have verification checks | Every `.md` file in `docs/external/standards/` (excluding README) contains a `## Verification Checks` section | Required | shared |
| Frameworks have evaluation decisions | `docs/external/industry-frameworks/README.md` contains both an active frameworks table and an "Evaluated — Not Required" table | Required | shared |
| Dashboard exists | `docs/dashboard.html` exists | Recommended | shared |
| Dashboard is current | `docs/dashboard.html` was modified within the last 7 days | Recommended | shared |
| No empty design control folders | Every subfolder under `design-controls/` contains at least one `.md` file besides README | Recommended | per-dhf |
| Submissions match pathway | If CLAUDE.md mentions "510(k)", `docs/project/submissions/510k/` exists; if "De Novo", `docs/project/submissions/de-novo/` exists; etc. | Recommended | shared |
| Standards README has exclusion rationale | Every standard/framework in the "Evaluated — Not Required" table has a non-empty rationale | Required | shared |
| Every docs folder has README | Every directory under `docs/` (recursively) contains a `README.md` file. Excluded: `.staging/`, `images/`, `formal/`, and hidden directories (starting with `.`). A missing README means Claude and team members have no guidance for that folder — naming conventions, expected content, and placement rules are undefined. | Required | shared |
| READMEs have changelogs | Every `README.md` under `docs/` contains a `## Changelog` section with a table (Date, Author, Summary). In AI-driven workflows, a session may make many edits collapsed into one commit — the changelog captures the rationale that git alone doesn't. | Required | shared |
| READMEs have conventions | Every `README.md` under `docs/` contains a `## Conventions` section documenting naming rules, formatting, and linking guidance for that folder. | Required | shared |
| READMEs follow section order | In every `README.md` under `docs/`, sections appear in meta-model order: Title → Subfolders/Structure → Information Flow/Relationships → Expected Content → Domain-specific → Conventions → For Claude → Changelog. Specifically: `## Conventions` must appear before `## Changelog`, and `## Expected Content` (if present) must appear before `## Conventions`. | Required | shared |
| Leaf READMEs have expected content | Every `README.md` in a leaf folder (no subdirectories) under `docs/` contains a `## Expected Content` or `## Expected Documents` section listing what document types belong in that folder. Exceptions: folders that use domain-specific sections instead (e.g., standards/ uses `## Distilled Standards`, frameworks/ uses `## Active Frameworks`). | Recommended | shared |
| README changelogs are current | When a `README.md` under `docs/` is modified, its `## Changelog` table has an entry matching the current date or the date of the most recent modification. Stale changelogs (last entry significantly older than git last-modified date) should be flagged. | Recommended | shared |
| No task refs in persistent docs | `CLAUDE.md`, `project.yml` descriptions, and DHF `README.md` files do not contain references to task documents (`tasks/*/NNN-*.md`). Persistent project documents must reference durable artifacts (strategy docs, architecture docs, input analysis, submission docs). Convention defined in CLAUDE.md Document Conventions. | Required | shared |
| CLAUDE.md has task discipline section | `CLAUDE.md` contains the string `Update as you go (HARD RULE` (the marker for the task-discipline block seeded by `/medtech-docs init` Step 2c Check 5). If missing, the active task doc has no recovery contract — sessions that drop or compact mid-batch lose their work narrative. Re-run `/medtech-docs init` to seed, or copy from `templates/claude-md-task-discipline.md`. | Required | shared |
| medtech-docs templates match init folder tree | Self-consistency check on this skill. Parse the `init` action's Step 3 "Folder tree" diagram (fenced code block) to extract the set of folders that receive a `README.md`. Parse the "README content sources" tables (Tier READMEs, Special READMEs, and the leaf-folder table) to extract the set of target paths and their mapped template files. Assert: (1) every folder in the tree that gets a README appears as a target in at least one content-sources table; (2) every target path in the content-sources tables corresponds to a folder in the tree; (3) every template file referenced (e.g., `readme-dhf.md`, `readme-leaf.md`) exists at `.claude/skills/medtech-docs/templates/<filename>`; (4) no orphan templates in `templates/` that aren't referenced by SKILL.md. Drift here means new-project scaffolds will either skip folders or reference missing templates — a bug at the source. | Required | shared |
