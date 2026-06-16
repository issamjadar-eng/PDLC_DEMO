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

medtech-docs owns four **auto-loaded rules** — markdown files under `.claude/rules/` that Claude Code loads into every session:

| Rule | What it governs |
|------|-----------------|
| `readme-before-write.md` | Before any write under `docs/`, read the target folder's README **and** its parent's. Parent READMEs carry cross-cutting conventions; leaf READMEs carry folder-specific naming/content rules. Misplaced files are a compliance risk in a regulated project. |
| `sentinel-blocks.md` | The `<!-- AUTO:STRUCTURE -->` sentinel convention — the contract for `scripts/render-sentinels.py` and `/best-practices fix`: a fenced, tool-owned region inside an otherwise human-owned doc, so structural tables (folder trees, DHF rosters) can be regenerated without clobbering narrative. |
| `audit-wiring-before-adding-fields.md` | Before adding a metadata field, schema entry, or structural prose, grep `project.yml` and sibling configs first — reference the wiring layer, don't redeclare facts already encoded in it. Redeclared facts silently rot when structure moves. |
| `claude-md-references.md` | Persistent docs (CLAUDE.md, `project.yml`, READMEs, strategy/architecture docs) must reference durable project artifacts, never transient task documents. |

**Why medtech-docs owns them.** All four govern the `docs/` tree, the `project.yml` wiring layer, and the README scaffolding that *this skill* creates — and the sentinel renderer is this skill's own code (`scripts/render-sentinels.py`). The rule that documents a script's contract belongs with the script. (`/best-practices fix` merely *calls* the renderer — it's a consumer, not the owner.)

**Why symlink, not copy.** `init` Step 2c Checks 3–6 install each rule as a **symlink** — `.claude/rules/<rule>.md` → `../skills/medtech-docs/rules/<rule>.md` — not a copy. The canonical text lives once, inside the skill at `rules/`. A `/sync-skills pull` that updates medtech-docs then auto-updates the installed rule, with no drift and no stale duplicate to audit. This is the same self-contained install pattern the registry uses for hooks and agents (see skill-creator's "Self-Contained Skills & Symlink Pattern"). A project that needs to diverge **forks** the symlink into a regular file; `/sync-skills` leaves forks alone.

**One canonical form per rule.** Earlier medtech-docs versions seeded `audit-wiring` as a *CLAUDE.md block* (an `init` check that inserted text from a `claude-md-config-audit.md` template) **and** the rule also existed as a `.claude/rules/` file — the same rule in two places, which is exactly the duplication `audit-wiring` itself forbids. v25 removed the CLAUDE.md block and the template: the auto-loaded `.claude/rules/` file is the single source of truth.

**How they're used.** `.claude/rules/` files are auto-loaded every session — no CLAUDE.md insertion needed. `readme-before-write` gates every `docs/` write; `sentinel-blocks` is the spec the renderer and audit-fix consult; `audit-wiring` and `claude-md-references` govern how facts and references are written across the project. The rule sources version *with the skill*: e.g. any new sentinel `kind` is a simultaneous edit to `rules/sentinel-blocks.md` and `scripts/render-sentinels.py`.

## Templates

Scaffold content lives in `templates/`; auto-loaded rule sources live in `rules/`:
- 11 README templates for the docs/ hierarchy
- 1 standard file template
- 1 dashboard HTML template
- 1 register-hook.sh helper
- 4 rule sources in `rules/` — `readme-before-write.md`, `sentinel-blocks.md`, `audit-wiring-before-adding-fields.md`, `claude-md-references.md` (symlinked into `.claude/rules/` by `init`)

Templates use `{{PLACEHOLDER}}` substitution for leaf folder READMEs and `${CLAUDE_SKILL_DIR}` for file paths.

## Changelog Context

Major version milestones:
- v35 (2026-06-15): **`render-sentinels.py` registry-file guardrail.** The renderer now refuses to write any file whose path is under `.claude/skills/**` (skips with a notice, no-op). Sentinels that pull **project data** (`project.yml`, folder tree) must materialize only into **project-local** files (`CLAUDE.md`, `docs/**` READMEs) — baking a project's data into a registry-shared skill file caused permanent per-project `/sync-skills` drift (uncovered via the `strategy` skill's Domain Registry tables, de-rendered in strategy v20). The `rules/sentinel-blocks.md` rule gains a **"never render project data into a registry-tracked skill file"** guardrail section and drops the retired `strategy/SKILL.md` sentinel locations. Templates (e.g. `readme-strategies.md`) keep their sentinel but render only **after** instantiation into the project copy under `docs/`, never in place.
- v34 (2026-06-12): New **`new-article`** action + the top-level **`articles/`** tree — article-style documentation written for *external consumption* (explainers/narratives, typically the structured input to `frontend-design` / `frontend-slides`). Articles are deliberately **NOT** part of the DHF, **NOT** a design-control/regulatory record, **NOT** indexed by the file-locator, and **NEVER** canonical. Enforced via the full not-canonical pattern (mirroring `knowledge-pack-not-canonical`): new auto-loaded rule `rules/articles-not-canonical.md` (symlinked into `.claude/rules/` by `new-article` and by `init` Step 2c Check 7e), a `project.yml file_locator.corpus_excludes` `articles/**` glob, a per-article **"NOT A CANONICAL SOURCE"** banner stamped by the action, and the `templates/readme-articles.md` README warning. The `articles/` folder is created lazily by the first `new-article` (not part of the default `init` scaffold); `init` installs only the rule + exclude so the guardrail exists before the first article. Supporting Files gains two rows (`readme-articles.md`, `rules/articles-not-canonical.md`).
- v33 (2026-06-11): References content-correction pass two + the four-rung consumption ladder. (1) **`regulations/21-cfr-part-807.md`** — § 807.85 corrected against the live eCFR (the actual section exempts *custom devices* (FD&C § 520(b)) and *distributors/repackagers* — the prior quoted text was not the CFR text, and the "§ 807.85 is the recognition mechanism for class exemptions" note was wrong: class-based exemption flows from FD&C § 510(l)/(m) + the classification regulation); § 807.100 corrected to the five FDA actions (SE / NSE / additional-info / withhold-pending-Part-54 / advise-not-required); § 807.81(b)'s **cleared-PCCP carve-out** documented (live eCFR confirms paragraph (b) now includes changes under a cleared predetermined change control plan consistent with the submission). (2) **`regulations/21-cfr-part-892.md`** — §§ 892.2030/2040 classification quotes completed (Class II + special controls + exempt-subject-to-§ 892.9, verified live eCFR); LLZ/QIH product-code conflation fixed (both live under § 892.2050 — predicate searches must sweep both); § 892.9(c)(1)–(9) IVD list confirmed present and summarized; new adjacent-classification section for 21 CFR 882.4560 (stereotaxic instrument — the navigation-predicate landing zone). (3) **`industry-frameworks/astm-f2554.md`** — fabricated "ASTM F2101 (CAS performance)" related-standard row removed (F2101 is the face-mask BFE test); FRE-bounds-TRE error corrected (FRE and TRE are essentially uncorrelated — never use FRE as a TRE acceptance surrogate); edition flagged `[VERIFY]` (F2554-22 believed current); THA-literature thresholds table fenced as uncited arthroplasty examples not transplantable to other applications; distillation-notice header added. (4) **`references/README.md` "For Claude" restructured as the explicit four-rung consumption ladder** — (1) project applicability → (2) registry distillation (cite both) → (3) bundled source-md full text for exact wording → (4) open web last resort (live eCFR / Federal Register API / openFDA; ISO/IEC clause text on no rung). Companion: the advisors skill renders the same ladder into every advisor GROUNDING block.
- v32 (2026-06-11): Reference-library honesty + escalation-contract pass across the four `references/` category READMEs, following a distillation audit that found unverified clause skeletons and stale regulatory text presented as ground truth. (1) **Escalation contract codified** — every category README's "For Claude" section now ends with an explicit escalation step: fda-guidance → read the bundled `source-md/<basename>.md` full text when exact wording / omitted appendices / footnotes matter; regulations → fetch the live eCFR versioner API when currency or exact wording matters (each file is a dated snapshot); standards / most frameworks → state that the original (copyrighted, not in repo) must be consulted rather than inferring clause content. Top-level README documents the same triad and reframes `source-md/` from "NOT indexed or exposed to agents" to "excluded from search/grounding surfaces, readable on explicit escalation." (2) **standards/README honesty fixes** — "consume as ground truth" → "best-effort distillation" with an authority-disclaimer paragraph; the false "walks every normative clause" claim replaced with an explicit absence-is-not-evidence note; quarantine banners / `[VERIFY]` markers documented as the per-file confidence record. (3) **regulations/README** — removed the false claim that eCFR XML archives exist under `source/`+`source-md/` (no such folders; flagged as desirable since CFR is public domain); § 807.85 row description corrected (custom-device/investigational exemption, not the class-exemption mechanism) with a `[VERIFY]` flag on the quoted text; § 880.6310 row notes the 2021 hardware-only amendment. (4) Stale cross-refs fixed (dhf-manifest `tier1-regulatory/` → `data/`; retired waterfall DHF tree path → project.yml-derived). Companion content fixes shipped separately (880.6310 post-Cures rewrite, IEC 62304 Clause 4/§ 4.3, 62366-1/82304-1 quarantine banners, sw-changes Flowchart D2).
- v30 (2026-05-29): Q-Sub guidance distillations refreshed against the actual current FDA documents. (1) **`qsub-distilled.md` rewritten** — prior distillation had a wrong scope statement ("does not cover PMA Day 100 Meetings" — actually the 2025 final DOES cover it as Type II.E and supersedes the 1998 PMA Day 100 procedures) and listed Pre-Sub meeting/written-only as two separate Q-Sub types instead of the actual 5 types (Pre-Sub, SIR, Study Risk Determination, Informational Meeting, PMA Day 100). Corrected against the actual May 29, 2025 final guidance PDF (CDRH GUI00001677). (2) **`qsub-estar-draft-distilled.md` added** — May 29, 2025 draft eSTAR guidance for Q-Subs (GUI00007041); will become partially binding when final per FD&C § 745A(b)(3); defines technical screening replacing RTA, Table-1 template-section schema replacing the Appendix-1 acceptance checklist, exemption list (interactive review, certain amendment types), and a 1-year transition timeline. (3) The earlier `source/qsub.pdf` was actually a June 2019 FDA-webinar transcript, not the guidance itself — renamed to `source/qsub-webinar-2019.pdf` to prevent agents from grounding against webinar content as if it were the regulation. New canonical `source/qsub.pdf` is the 2025 final guidance. README table rows refreshed.
- v29 (2026-05-29): New reference category — `references/regulations/` for US federal regulations (21 CFR), with three initial distillations (Parts 807, 880, 892) covering 510(k) when required, MDDS classification, and the imaging-system regulatory chain. Plus one new FDA-guidance distillation: `mdds-distilled.md` (the 2022 update with Non-Device-MDDS vs Device-MDDS framework post-Cures-Act § 3060). Source content fetched via the eCFR public API (`https://www.ecfr.gov/api/versioner/v1/full/...`) — the AI-accessible federal-regulation endpoint that bypasses the unblock.federalregister.gov redirect wall on the eCFR human viewer. Per the reference architecture: distilled clause text at parent level; raw source XML/PDF under `source/`; markdown conversion under `source-md/`. `references/regulations/README.md` follows the same scope / conventions / "For Claude" pattern as `references/standards/README.md` and mandates cite-both grounding (regulation file for what the rule says, project applicability file for what the program decided). Closes the `registry-gap` finding class for CFR citations in the `/reference-audit` skill.
- v28 (2026-05-28): New auto-loaded rule — `ground-in-contracts-not-assumptions.md`. Codifies "read the contract before reasoning about behavior": when reasoning about how a sibling skill / agent / schema / script behaves, read its contract (SKILL.md / agent prompt / schema / source / README / frontmatter) and cite specific lines, rather than reasoning from pattern memory or component name. Design-time sibling of `audit-wiring-before-adding-fields` (which is the authoring-time counterpart). Failure mode it addresses: LLM analyses produce option tables and tradeoffs that look rigorous regardless of whether the premise is read or invented; an invented premise produces wallpaper over a wrong wall, undetectable from the analysis surface. Updates: new `rules/ground-in-contracts-not-assumptions.md` source file; new init Step 2c Check 7 (symlinks the rule); task-discipline check renumbered 7 → 8; Supporting Files table row added.
- v28 (2026-05-28): **Doctype governance auto-loaded rule + SessionStart freshness hook + 5 new best-practices audit checks**. (1) Sixth auto-loadable rule added — `doctype-governance.md`. Tells Claude (main session) and any reader: before editing a file under a `.taxonomy.yml`-governed folder, walk up to find the nearest taxonomy, look up the file's parent-folder slug in `mappings[]`, and read the listed `governing_qms.{forms[], sops[], work_instructions[]}` from the QMS registry before authoring changes. Six null/edge cases enumerated (absent taxonomy / unmapped slug / `governing_qms: null` / forms:[]+note / partial coverage / stale `last_updated`). Project-agnostic — no FORM/SOP IDs, no DHF names. Symlinked into `.claude/rules/` via the medtech-docs install pattern. (2) New hook `hooks/taxonomy-freshness.sh` — SessionStart hook that walks the project for `.taxonomy.yml` files, reads top-level `last_updated:` + `review_cadence_days:`, and emits a `hookSpecificOutput.additionalContext` system reminder when any taxonomy is past its review window. Throttled to one notification per 24h per project via `.state/taxonomy-freshness-reminded` marker. Silently skips if pyyaml is unavailable or taxonomy lacks metadata. (3) Five new `## Best Practices` audit rows in this README: "Taxonomy file declares freshness metadata" (WARN on missing `last_updated:` + `review_cadence_days:`), "Taxonomy file within review cadence" (WARN past threshold), "Taxonomy mappings cover the filesystem" (WARN on unmapped folders, cross-cutting scope), "Taxonomy mappings don't reference missing folders" (FAIL on stale mappings, cross-cutting), "Taxonomy governing_qms IDs resolve" (FAIL on unresolvable FORM-* / SOP-* / WI-* IDs against `docs/internal/source-md/`). Six rules now live under skill ownership.
- v27 (2026-05-28): New sentinel `kind=doc-governance source=taxonomy[:<slug>]` — renders a visible markdown banner above a doctype page body listing the QMS forms / parent SOPs / work instructions / upstream-input forms that govern producing the doc, sourced from the nearest ancestor `.taxonomy.yml` `mappings[<slug>].governing_qms` block. Slug defaults to the target file's parent folder name (the doctype-folder convention) and can be overridden via the `source=taxonomy:<slug>` syntax. Three null cases (no taxonomy / slug missing / `governing_qms` block absent) render discoverable italic-line warnings rather than aborting — keeps the gap visible in the published doc until authored. Bare-mapping case (`governing_qms` present but every list empty) distinguishes intentional null ("team-internal convention") from TBD via `note:`. Updates to: `scripts/render-sentinels.py` (new `render_doc_governance` + `_find_taxonomy_file` helper + dispatcher routing for `kind in ('folder-tree', 'folder-tree-subset', 'doc-governance')` + `source=taxonomy:<slug>` parsing into attrs); `rules/sentinel-blocks.md` (new kind row, new sources rows, new variant section, canonical locations row). Companion changes: `/dhf-manifest` v13 surfaces `governing_qms` in discovery index; `/advisors` updates GROUNDING template to instruct agents to read governing FORM-* / SOP-* before recommending changes to a governed doc; `.taxonomy.yml` schema bumped 0.2 → 0.3 (new `governing_qms` block).
- v26 (2026-05-28): Fifth auto-loadable rule added — `internal-vs-external-scope-labels.md`. Defines a four-icon label system (📤 / 📝 / ⏸️ / 📖) for internal-review documents that distill into formal external submissions (regulatory filings, IRB packages, notified-body dossiers, audit responses). Uses content-metaphor icons (outbox / memo / pause / book) instead of colored bubbles (🟢/🟡/🔴) to avoid status-traffic-light semantic conflict. Includes a drop-in scope-banner template, application/non-application criteria, Confluence-portability notes, and interaction with the existing four rules. Motivated by Q-Sub questions document review where Q-Sub-bound content was visually indistinguishable from internal rationale, deferred questions, and reference material. Five rules now live under skill ownership.
- v1: Initial scaffold with init, add-standard, evaluate, dashboard
- v3: Migrated to skills/ directory, extracted templates
- v5: README meta-model with strict section ordering
- v7: Formal/ subfolder pattern for controlled documents
- v8: Synced templates with actual docs/ state, added project infrastructure creation
- v25 (2026-05-15): Two more rules brought under skill ownership — `audit-wiring-before-adding-fields` and `claude-md-references` now ship as `rules/` sources, symlinked into `.claude/rules/` by `init` Step 2c Checks 5 & 6. **Deduplication:** `audit-wiring` was previously *also* seeded as a CLAUDE.md block (`init` Check 6, from `templates/claude-md-config-audit.md`) — that check and template were removed; the auto-loaded rule file is now the single canonical form. The `audit-wiring` rule text was tightened and gained a concrete ✅/❌ Examples section. Task-discipline CLAUDE.md-block check renumbered 5 → 7. medtech-docs now owns four auto-loaded rules.
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
| Taxonomy file declares freshness metadata | For every `.taxonomy.yml` under `docs/` (excluding `.git`, `.venv`, `node_modules`, `_scratch`, `tools`): the top of the file declares both `last_updated: <YYYY-MM-DD>` and `review_cadence_days: <int>`. A taxonomy file is the source of truth for doctype→QMS-template mapping; without freshness metadata, drift between the taxonomy and the QMS document registry is silent. WARN on missing metadata; FAIL on malformed values (non-date string, non-integer cadence). | Recommended | shared |
| Taxonomy file within review cadence | For every `.taxonomy.yml` with both `last_updated:` and `review_cadence_days:` fields populated: assert `today <= last_updated + review_cadence_days`. WARN past threshold — the per-doctype QMS-form mappings may have drifted from the current QMS document control system (form/SOP/WI renames or retirements, new doctypes added). Remediation: re-audit the mappings against `docs/internal/source-md/Forms/`, `docs/internal/source-md/SOPs/`, `docs/internal/source-md/Work Instructions/`, then bump `last_updated:` to today's date. | Recommended | shared |
| Taxonomy mappings cover the filesystem | For every `.taxonomy.yml` whose `discovery_root:` is set: every immediate subfolder of `<dhf-path>/<discovery_root>/` (across all DHFs whose `taxonomy_path:` in `project.yml` points to this file) appears as a key in `mappings[]` OR is in the taxonomy's `unmapped` entries. WARN on any folder that is neither mapped nor declared unmapped — silent drift between the actual filesystem and the taxonomy means consumer skills (discovery-index, render-sentinels, advisors) can't bind that doctype. Remediation: add a `mappings[<new-slug>]` entry (with `canonical_role` + optional `governing_qms`) or an `unmapped: informational` entry with a `note:`. | Recommended | cross-cutting |
| Taxonomy mappings don't reference missing folders | For every `.taxonomy.yml`, every key in `mappings[]` that is NOT marked `unmapped:` must correspond to an existing immediate-subfolder of `<dhf-path>/<discovery_root>/` for at least one DHF whose `taxonomy_path:` references this taxonomy. FAIL on stale mapping — the doctype was renamed or removed in the Confluence space but the taxonomy still claims it. | Required | cross-cutting |
| Taxonomy governing_qms IDs resolve | For every `mappings[].governing_qms.{forms,sops,work_instructions,upstream_inputs}[]` ID across every `.taxonomy.yml`: assert that a file matching `docs/internal/source-md/**/<ID>*.md` exists (or the project's equivalent QMS registry root, configured via `project.yml qms_registry_root` with default `docs/internal/source-md`). FAIL on unresolvable ID — a typo'd form/SOP/WI reference makes the governance banner mislead readers and the advisor agent's `Read` call fail. | Required | shared |
