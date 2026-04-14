---
name: medtech-docs
description: "Scaffold and manage documentation for regulated medical device projects — init docs structure, manage sub-DHFs, manage standards, generate compliance dashboard"
version: 13
updated: 2026-04-13
---

# MedTech Docs

Scaffold and manage documentation for regulated medical device projects. Usage: `/medtech-docs <action> [arguments]`

## Supporting Files

This skill includes template files in `${CLAUDE_SKILL_DIR}/templates/`:

| File | Used By | Purpose |
|------|---------|---------|
| `readme-docs.md` | `init` | Top-level `docs/README.md` |
| `readme-external.md` | `init` | `docs/external/README.md` |
| `readme-internal.md` | `init` | `docs/internal/README.md` |
| `readme-project.md` | `init` | `docs/project/README.md` |
| `readme-fda-guidance.md` | `init` | `docs/external/fda-guidance/README.md` |
| `readme-standards.md` | `init` | `docs/external/standards/README.md` |
| `readme-industry-frameworks.md` | `init` | `docs/external/industry-frameworks/README.md` |
| `readme-clinical-literature.md` | `init` | `docs/external/clinical-literature/README.md` |
| `readme-input-analysis.md` | `init` | `docs/project/input-analysis/README.md` |
| `readme-strategies.md` | `init` | `docs/project/strategies/README.md` (shared cross-cutting strategies — commercial, operations) |
| `readme-submissions.md` | `init` | `docs/project/submissions/README.md` |
| `readme-sub-dhf.md` | `init`, `add-sub-dhf` | `docs/project/dhfs/<name>/README.md` — per sub-DHF root README (substitute `{{SUB_DHF_NAME}}`, `{{REGULATORY_STATUS}}`, `{{FILING}}`) |
| `readme-design-controls.md` | `init`, `add-sub-dhf` | `docs/project/dhfs/<name>/design-controls/README.md` |
| `readme-trace-matrix.md` | `init`, `add-sub-dhf` | `docs/project/dhfs/<name>/design-controls/trace-matrix/README.md` |
| `readme-clinical.md` | `init`, `add-sub-dhf` | `docs/project/dhfs/<name>/clinical/README.md` |
| `readme-postmarket.md` | `init`, `add-sub-dhf` | `docs/project/dhfs/<name>/postmarket/README.md` |
| `readme-risk-management.md` | `init`, `add-sub-dhf` | `docs/project/dhfs/<name>/risk-management/README.md` |
| `readme-cybersecurity.md` | `init`, `add-sub-dhf` | `docs/project/dhfs/<name>/cybersecurity/README.md` |
| `readme-leaf.md` | `init`, `add-sub-dhf` | Template for leaf folder READMEs (substitute `{{TITLE}}`, `{{PURPOSE}}`, `{{NAMING}}`) |
| `readme-source.md` | `init` | `docs/internal/source/README.md` |
| `readme-source-md.md` | `init` | `docs/internal/source-md/README.md` |
| `readme-formal.md` | `init`, `add-sub-dhf` | Template for `formal/` subfolder READMEs (substitute `{{PARENT}}`) |
| `standard-file.md` | `add-standard`, `init` | Template for new standard/framework files |
| `dashboard.html` | `dashboard` | HTML template for compliance dashboard |
| `register-hook.sh` | `init` | Shared hook registration helper — installed to `.claude/hooks/` for skills to use |

## Actions

Parse the user's argument string `$ARGUMENTS` to determine which action to perform.

### `init`

Interactive guided setup of the `docs/` folder hierarchy for a MedTech project. Asks the user questions to determine what's needed, then creates the full structure.

**Step 1 — Gather project context**

Ask the user the following questions (present all at once, let them answer):

1. **Device type**: SaMD, SiMD, combination product, or other?
2. **Regulatory pathway**: 510(k), De Novo, PMA, or not yet determined?
3. **Modules/functions**: What functional modules does the device have? (e.g., planning, navigation, monitoring)
4. **AI/ML involved?**: Does any module use machine learning or AI algorithms?
5. **Medical imaging?**: Does any module import, process, or display medical images (DICOM)?
6. **EHR integration?**: Does any module exchange data with EHR systems (HL7 FHIR)?
7. **Surgical navigation/guidance?**: Does any module provide real-time spatial guidance during procedures?
8. **Existing docs?**: Does the project already have a docs/ folder or any documentation structure?
9. **Primary sub-DHF name**: Short name for the primary component whose design controls anchor this project (e.g., `pca-device`, `ecg-monitor`, `insulin-pump`). **No default — required.** This becomes the first entry in `project.sub_dhfs[]` and the first `docs/project/dhfs/<name>/` folder. Additional sub-DHFs can be added later via `/medtech-docs add-sub-dhf`. Every project has at least one sub-DHF from day one; single-component and multi-component projects use the same shape (single-component is just N=1).

**Step 2 — Create `project.yml`**

Create `project.yml` in the project root if it doesn't already exist. This is the single source of truth for project identity, team roster, skill registries, and security policy. Pre-populate using answers from Step 1:

```yaml
# project.yml — Project manifest
#
# Single source of truth for project identity, team roster, and security policy.
# Skills and agents read this for project-specific context.
# This file is committed to the repo.
#
# Maintained by: medtech-docs init (creation), manual edits (ongoing)
# Consumed by: security-assert.sh, setup.sh, best-practices, task skill, secops agent

# ─── Project Identity ───

project:
  name: {{PROJECT_NAME}}
  repo: {{REPO_OWNER/REPO_NAME}}
  type: medtech
  regulatory_pathway: {{510k|denovo|pma|tbd}}
  device_class: {{I|II|III|tbd}}
  device_family: {{DEVICE_FAMILY}}

# ─── Sub-DHFs ───
#
# Every project has at least one sub-DHF from day one. A sub-DHF is a
# component with its own design controls, risk-management, clinical, and
# postmarket folders. Single-component projects just have one entry here.
# Add more sub-DHFs over time with `/medtech-docs add-sub-dhf <name>`.
#
# Fields:
#   path       — required; slug used as folder name under docs/project/dhfs/
#   regulatory — required; concept | in-development | cleared | mixed
#                (mixed = platform sub-DHF whose children carry the regulatory weight)
#   filing     — optional; which submission folder this sub-DHF rolls up into
#                (null means "not yet scoped into a filing")
#   parent     — optional; path of the parent sub-DHF if this is a nested child
#                (null means "top-level")
#
# Leaf-name uniqueness is enforced by `add-sub-dhf` — no two sub-DHFs can
# share the same last path segment, even at different depths. This is what
# lets `/strategy` tag authors write `sub-dhf=<leaf>` without ambiguity.

sub_dhfs:
  - path: {{PRIMARY_SUB_DHF}}
    regulatory: in-development
    filing: null
    parent: null

# ─── Team Roster ───
#
# Every repo collaborator must have a row here.
# task_folder is the lowercase name used under tasks/{folder}/
# GitHub username must be exact (case-sensitive) for API matching.

team:
  active:
    # - name: Jane Smith
    #   github: janesmith
    #   task_folder: jane
    #   role: Role Title
    #   email: jane.smith@company.com
    #   added: YYYY-MM-DD
  inactive: []

# ─── Skill Registries ───
#
# Approved sources for skills, agents, and templates.
# Skills/agents not traceable to an approved registry trigger secops warnings.

registries:
  - name: anthropic
    type: builtin
    description: Anthropic official skills (docx, pptx, xlsx, pdf)
    skills:
      - docx
      - pptx
      - xlsx
      - pdf

  - name: hitachi
    type: github
    repo: GlobalLogic-a-Hitachi-Company/hitachi
    path: skills/manifest.md
    local_path: ../hitachi              # Local clone path — used for skill sync/updates
    description: Internal shared registry — project skills and best practices
    skills:
      - best-practices
      - docflow
      - lessons
      - medtech-docs
      - skill-creator
      - strategy
      - sync-skills
      - task
      - tracker

# ─── Security Policy ───

security:
  approved_email_domains:
    - {{company-domain.com}}

  check_ttl_days: 7
  attestation_ttl_days: 30

  required_gitignore_patterns:
    - ".env"
    - "*.pem"
    - "*.key"
    - "*.p12"
    - "credentials*"
    - "**/PHI/**"
    - "**/patient*data*"

  approved_skills:       # Auto-populated from registries.skills lists above
    {{APPROVED_SKILLS}}
  approved_mcps:
    # chrome-devtools — Google's Chrome DevTools MCP server. Lets Claude
    # drive a real Chrome instance for visual validation: navigate, take
    # screenshots, inspect computed styles, evaluate JS in the page. Useful
    # for any frontend work (dashboards, web UI) where layout/visual
    # correctness can't be verified from source alone.
    # Install: `claude mcp add chrome-devtools -- npx -y chrome-devtools-mcp@latest`
    - chrome-devtools
  approved_plugins: []   # Populated as plugins are added
  approved_agents: []    # Populated as agents are created
```

Substitute the `{{...}}` placeholders using the user's answers:
- `{{PROJECT_NAME}}` — ask the user, or derive from the directory name
- `{{REPO_OWNER/REPO_NAME}}` — ask the user for their GitHub repo path (e.g., `org/repo-name`)
- `{{regulatory_pathway}}` — from question 2 (lowercase: `510k`, `denovo`, `pma`, or `tbd`)
- `{{device_class}}` — infer from pathway if possible (510(k) → II, PMA → III, De Novo → I or II), or ask
- `{{DEVICE_FAMILY}}` — ask the user for the device family slug (lowercase, no spaces — used in filenames like `<device-family>-system-sad.md`). Examples: `hiplink`, `synergy`, `vip`
- `{{PRIMARY_SUB_DHF}}` — from question 9. Lowercase slug, hyphenated (e.g., `pca-device`, `ecg-monitor`). This is the folder name that appears under `docs/project/dhfs/`, so it must be filesystem-safe. Validate: `^[a-z][a-z0-9-]*[a-z0-9]$`. If the user's answer contains uppercase or underscores, prompt to confirm a normalized form.
- `{{company-domain.com}}` — ask the user for their corporate email domain
- `{{APPROVED_SKILLS}}` — **do not ask the user**. Auto-generate by collecting all skill names from the `registries:` section's `skills:` lists, sorted alphabetically, one `- name` per line. This ensures every skill listed in a registry is pre-approved at init time.

If `project.yml` already exists, skip this step and inform the user.

**Step 2b — Add project.yml reference to CLAUDE.md**

After creating (or confirming) `project.yml`, check if `CLAUDE.md` contains a section about the project manifest. If it doesn't, insert the following section. Place it after the "Information Flow" or "Project Structure" section, before "Working Conventions" (or at the end of the structural documentation if those sections don't exist).

**Check**: Search CLAUDE.md for the string `project.yml`. If found, skip — the section already exists.

**Insert this content** (adapt the table rows if the project has different sections in its project.yml):

```markdown
### Project Manifest — `project.yml`

`project.yml` is the **single source of truth** for project identity, team roster, skill registries, and security policy. It lives in the project root and is read by skills, hooks, and automation scripts.

**What it contains:**

| Section | Purpose |
|---------|---------|
| `project:` | Project name, repo, type, regulatory pathway, device class, device family slug |
| `sub_dhfs:` | Ordered list of sub-DHFs in the project. Every project has at least one from day one. Each entry has `path`, `regulatory`, `filing`, and optional `parent` fields. Maintained by `/medtech-docs add-sub-dhf`. Leaf-name uniqueness is enforced so `sub-dhf=<leaf>` tag resolution is unambiguous. |
| `team:` | Active and inactive team members — name, GitHub username, task folder, role, email. Every repo collaborator must have a row here. |
| `registries:` | Approved sources for skills and templates. Skills are either `builtin` (shipped with Claude Code) or fetched from a `github` registry. Each `github` registry has a `local_path` (default `../hitachi`) for local clone-based sync. |
| `security:` | Approved email domains, gitignore patterns, and allowlists for skills, MCPs, plugins, and agents |

**Security allowlists** — when adding new skills, MCP servers, plugins, or agents to the project, add them to the corresponding `approved_*` list in `project.yml` first. The security posture check warns on anything installed but not listed. This ensures the team can audit what tools have access to project data.

**Team roster** — when onboarding a new team member, add their entry to `team.active`. When someone leaves, move them to `team.inactive` with a `removed` date and `reason`. The `setup.sh --check` audit cross-references this roster against actual GitHub repo collaborators.
```

This ensures that Claude (and human readers) know where to find and edit project configuration — team membership, approved tools, security policy — without having to discover `project.yml` by accident.

**Step 3 — Create the folder structure and READMEs**

Create the following hierarchy. Skip folders/files that already exist.

#### Folder tree

The scaffold always uses the **unified sub-DHF shape** — every project has at least one sub-DHF, even single-component projects. The primary sub-DHF name comes from Step 1 question 9. Growth to multi-component is handled by `add-sub-dhf`, not by restructuring.

```
docs/
├── README.md
├── external/                            (shared — upstream truth)
│   ├── README.md
│   ├── fda-guidance/README.md
│   ├── standards/README.md
│   ├── industry-frameworks/README.md
│   └── clinical-literature/README.md
├── internal/                            (shared — corporate SOPs, templates)
│   ├── README.md
│   ├── source/
│   │   └── README.md                    ← Original SOP/procedure/template files (PDF, DOCX)
│   └── source-md/
│       └── README.md                    ← Markdown conversions of source documents
└── project/
    ├── README.md
    ├── input-analysis/                  (shared — customer intelligence across the project)
    │   ├── README.md
    │   ├── predicate-analysis/README.md
    │   ├── competitive-landscape/README.md
    │   ├── kol-feedback/README.md
    │   └── market-research/README.md
    ├── strategies/                      (shared — cross-cutting strategies; commercial, operations)
    │   └── README.md
    ├── dhfs/
    │   └── {{PRIMARY_SUB_DHF}}/         ← per-DHF root; more sub-DHFs added via `add-sub-dhf`
    │       ├── README.md                ← sub-DHF description; regulatory status; filing rollup
    │       ├── design-controls/
    │       │   ├── README.md
    │       │   ├── trace-matrix/
    │       │   │   ├── README.md
    │       │   │   └── formal/
    │       │   │       └── README.md
    │       │   ├── plans/
    │       │   │   ├── README.md
    │       │   │   └── formal/
    │       │   │       └── README.md
    │       │   ├── user-needs/
    │       │   │   ├── README.md
    │       │   │   └── formal/
    │       │   │       └── README.md
    │       │   ├── requirements/
    │       │   │   ├── README.md
    │       │   │   └── formal/
    │       │   │       └── README.md
    │       │   ├── architecture/
    │       │   │   ├── README.md
    │       │   │   └── formal/
    │       │   │       └── README.md
    │       │   ├── vnv/
    │       │   │   ├── README.md
    │       │   │   └── formal/
    │       │   │       └── README.md
    │       │   └── tool-validation/
    │       │       ├── README.md
    │       │       └── formal/
    │       │           └── README.md
    │       ├── clinical/                ← evaluation plans, benefit-risk, literature search
    │       │   ├── README.md
    │       │   ├── evaluation-plans/README.md
    │       │   ├── benefit-risk/README.md
    │       │   └── literature-search/README.md
    │       ├── postmarket/              ← PMCF plans/studies, CAPA, complaints
    │       │   ├── README.md
    │       │   ├── pmcf-plans/README.md
    │       │   ├── pmcf-studies/README.md
    │       │   ├── capa/README.md
    │       │   └── complaints/README.md
    │       ├── risk-management/         ← ISO 14971 hazard analysis, FMEA, risk-benefit
    │       │   ├── README.md
    │       │   └── formal/
    │       │       └── README.md
    │       └── cybersecurity/           ← IEC 81001-5-1 assessment, SBOM, threat model
    │           ├── README.md
    │           └── formal/
    │               └── README.md
    └── submissions/                     (shared — composition manifests reference dhfs/*)
        ├── README.md
        ├── qsub/
        │   ├── README.md
        │   ├── formal/
        │   │   └── README.md            ← Submission-ready deliverables (DOCX, XLSX)
        │   └── correspondence/README.md
        ├── 510k/
        │   ├── README.md
        │   ├── formal/
        │   │   └── README.md
        │   └── correspondence/README.md
        └── pccp/
            ├── README.md
            ├── formal/
            │   └── README.md
            └── correspondence/README.md
```

**Key departures from earlier medtech-docs versions (v11 and earlier):**
- `design-controls/` is now nested under `dhfs/<primary>/`, not at `docs/project/` root.
- `risk-management/` is a **sibling** of `design-controls/` inside the sub-DHF, not a child of `design-controls/`. This matches ISO 14971 scoping — risk management covers the whole device, not just design controls.
- `clinical/`, `postmarket/`, and `cybersecurity/` are new per-DHF folders scaffolded at init time. Early-stage projects will have empty leaves here; that's expected, and best-practices grades empty per-DHF leaves as INFO, not FAIL.
- `strategies/` is a new shared folder at `docs/project/strategies/` for cross-cutting strategies (commercial, operations) that apply to the whole project regardless of how many sub-DHFs exist.

#### README meta-model

Every README.md follows this meta-model. The sections are ordered as shown — not all are required for every folder, but when present they must appear in this order:

```
# Folder Title
_Purpose paragraph — what this folder contains and why it exists._

## Structure / Subfolders               ← If folder has subdirectories (table of subfolders)
## Information Flow / Relationship to…  ← If folder connects to other tiers (data flow diagram)
## Expected Content / Expected Documents ← If leaf folder (what files go here)
## [Domain-specific sections]           ← Standards tables, decision tables, waterfall diagrams, etc.
## Conventions                          ← REQUIRED — naming rules, formatting, linking guidance
## For Claude (optional)                ← AI-specific behavioral instructions beyond conventions
## Changelog                            ← REQUIRED — table with Date, Author, Summary columns
```

**Required sections** (every README must have these):
- **Title + purpose paragraph** — `# Title` followed by a description
- **Conventions** — naming patterns, formatting rules, linking requirements
- **Changelog** — `| Date | Author | Summary |` table

**Conditional sections** (include when applicable):
- **Subfolders** / **Structure** — when the folder has subdirectories (use a `| Folder | Purpose |` table)
- **Information Flow** — when the folder is an overview tier showing how data flows between subfolders
- **Relationship to…** — when the folder's content feeds into or derives from another tier
- **Expected Content** / **Expected Documents** — when the folder is a leaf that receives specific document types
- **For Claude** — only when there are AI-specific behavioral instructions that go beyond naming conventions

#### README content sources

For each README, read the corresponding template from `${CLAUDE_SKILL_DIR}/templates/` and write it to the target path:

**Tier READMEs** (contain information flow, subfolder tables, conventions):

| Target Path | Template File |
|------------|---------------|
| `docs/README.md` | `readme-docs.md` |
| `docs/external/README.md` | `readme-external.md` |
| `docs/internal/README.md` | `readme-internal.md` |
| `docs/project/README.md` | `readme-project.md` |

**Special READMEs** (contain evaluation tables, compliance conventions):

| Target Path | Template File |
|------------|---------------|
| `docs/external/fda-guidance/README.md` | `readme-fda-guidance.md` |
| `docs/external/standards/README.md` | `readme-standards.md` |
| `docs/external/industry-frameworks/README.md` | `readme-industry-frameworks.md` |
| `docs/external/clinical-literature/README.md` | `readme-clinical-literature.md` |
| `docs/project/input-analysis/README.md` | `readme-input-analysis.md` |
| `docs/project/strategies/README.md` | `readme-strategies.md` |
| `docs/project/dhfs/{{PRIMARY_SUB_DHF}}/README.md` | `readme-sub-dhf.md` (substitute `{{SUB_DHF_NAME}}`, `{{REGULATORY_STATUS}}=in-development`, `{{FILING}}=TBD`) |
| `docs/project/dhfs/{{PRIMARY_SUB_DHF}}/design-controls/README.md` | `readme-design-controls.md` |
| `docs/project/dhfs/{{PRIMARY_SUB_DHF}}/design-controls/trace-matrix/README.md` | `readme-trace-matrix.md` |
| `docs/project/dhfs/{{PRIMARY_SUB_DHF}}/clinical/README.md` | `readme-clinical.md` |
| `docs/project/dhfs/{{PRIMARY_SUB_DHF}}/postmarket/README.md` | `readme-postmarket.md` |
| `docs/project/dhfs/{{PRIMARY_SUB_DHF}}/risk-management/README.md` | `readme-risk-management.md` |
| `docs/project/dhfs/{{PRIMARY_SUB_DHF}}/cybersecurity/README.md` | `readme-cybersecurity.md` |
| `docs/project/submissions/README.md` | `readme-submissions.md` |
| `docs/internal/source/README.md` | `readme-source.md` |
| `docs/internal/source-md/README.md` | `readme-source-md.md` |

**Note on per-DHF paths**: every per-DHF folder lives under `docs/project/dhfs/<sub-dhf-name>/`. At `init` time there is exactly one sub-DHF (the primary), so paths above reference `{{PRIMARY_SUB_DHF}}`. When additional sub-DHFs are added via `add-sub-dhf`, the same template set is applied under each new `dhfs/<name>/`.

**Leaf folder READMEs** — use `readme-leaf.md` template, substituting `{{TITLE}}`, `{{PURPOSE}}`, `{{NAMING}}`, and populating `## Expected Content` with the items listed below.

**Note**: All `design-controls/` and `submissions/` leaf folders include a `formal/` subfolder for controlled documents (DOCX, XLSX). Working markdown files live at the folder root; formal deliverables go in `formal/`. Each leaf README should include a `## Structure` section documenting this. The `init` action creates the `formal/` subfolder automatically. Each `formal/` subfolder gets a README using `readme-formal.md` template (substitute `{{PARENT}}` with the parent folder name, e.g., "Plans", "Architecture").

**Internal folder READMEs**: `internal/source/` and `internal/source-md/` each get a README using the dedicated templates `readme-source.md` and `readme-source-md.md`.

**Path conventions in the table below**:
- `input-analysis/<leaf>` is shorthand for `docs/project/input-analysis/<leaf>/`
- `submissions/<leaf>` is shorthand for `docs/project/submissions/<leaf>/`
- `dhfs/<leaf>` is shorthand for `docs/project/dhfs/{{PRIMARY_SUB_DHF}}/<leaf>/` — i.e., the primary sub-DHF at init time. When `add-sub-dhf` runs, the same template rows are applied under each new sub-DHF.

| Folder | `{{TITLE}}` | `{{PURPOSE}}` | `{{NAMING}}` | Expected Content Items |
|--------|------------|---------------|--------------|----------------------|
| `input-analysis/predicate-analysis/` | Predicate Analysis | Predicate device search results, device profiles, comparison tables, and the substantial equivalence argument. Source all data from FDA databases (510(k), De Novo, PMA). Applies across the project portfolio — shared across sub-DHFs. | `company-device-name.md` for profiles; `topic-description.md` for analysis | Device profiles (one per candidate), search result summaries, comparison tables, SE argument drafts |
| `input-analysis/competitive-landscape/` | Competitive Landscape | Competitor analysis — cleared devices, market positioning. Shared across sub-DHFs. | `company-name.md` for company profiles | Company profiles, product portfolio summaries, market positioning analysis |
| `input-analysis/kol-feedback/` | KOL Feedback | Key Opinion Leader interviews, clinical advisory input. Shared across sub-DHFs. | `YYYY-MM-DD-kol-name-topic.md` | Interview notes, clinical workflow observations, advisory board minutes |
| `input-analysis/market-research/` | Market Research | Market landscape, unmet needs analysis, competitive positioning. Shared across sub-DHFs. | `topic-description.md` | Market landscape analysis, unmet needs studies, user surveys |
| `dhfs/design-controls/trace-matrix/` | Trace Matrix | Traceability matrices linking design control artifacts — user needs to requirements, requirements to architecture, requirements to V&V, and risk mitigations. Scoped to this sub-DHF. | `matrix-type.md` at root; matching `.xlsx` in `formal/` | RTM, risk traceability matrix, V&V traceability matrix |
| `dhfs/design-controls/plans/` | Plans | Design and development plans, V&V plans, maintenance plans, and component-level strategy documents. Scoped to this sub-DHF. | `plan-type-name.md` at root; matching `.docx` in `formal/` | Software Development Plan, V&V Plan, Configuration Management Plan, Maintenance Plan |
| `dhfs/design-controls/user-needs/` | User & Stakeholder Needs | Formal user and stakeholder needs for this sub-DHF. Derived from shared `input-analysis/` and scoped down to this component. | `need-category.md` at root; matching `.docx` in `formal/` | User need statements, stakeholder need statements, needs traceability |
| `dhfs/design-controls/requirements/` | Requirements | Design input requirements, SRS, label requirements for this sub-DHF. Each must be verifiable. | `component-srs.md` at root; matching `.docx` in `formal/` | SRS (per module), label requirements, interface requirements |
| `dhfs/design-controls/architecture/` | Architecture | Software architecture documents (SAD), system design, interface specifications for this sub-DHF. | `component-sad.md` at root; matching `.docx` in `formal/` | SAD (per module), system design, interface specifications |
| `dhfs/design-controls/vnv/` | Verification & Validation | V&V protocols, test plans, test results, usability evaluation reports for this sub-DHF. | `test-type-component.md` at root; matching `.docx` in `formal/` | System test plans/reports, integration tests, usability evaluation reports |
| `dhfs/design-controls/tool-validation/` | Tool Validation | Validation records for software tools used in development per IEC 62304. Scoped to this sub-DHF's build/test toolchain. | `tool-name-validation.md` at root; matching `.docx` in `formal/` | Tool validation plans, reports, risk assessments, tool inventory |
| `dhfs/clinical/evaluation-plans/` | Clinical Evaluation Plans | Clinical evaluation plans per MDCG 2020-6 / FDA guidance for this sub-DHF. | `CEP-NNNN.md` at root; matching `.docx` in `formal/` | Clinical evaluation plans, clinical development plans |
| `dhfs/clinical/benefit-risk/` | Benefit-Risk Analysis | Benefit-risk analyses tying clinical evidence to the device's intended use and risk profile. | `BRA-NNNN.md` at root | Benefit-risk analysis documents |
| `dhfs/clinical/literature-search/` | Literature Search | Systematic literature search results, inclusion/exclusion rationale, and evidence tables. | `LSS-NNNN.md` at root | Literature search strategies, evidence tables, PRISMA diagrams |
| `dhfs/postmarket/pmcf-plans/` | PMCF Plans | Post-Market Clinical Follow-up plans for this sub-DHF. | `PMCF-NNNN.md` at root | PMCF study plans, objectives, endpoints |
| `dhfs/postmarket/pmcf-studies/` | PMCF Studies | PMCF study execution records and results for this sub-DHF. | `STUDY-NNNN.md` at root | Study protocols, interim reports, final reports |
| `dhfs/postmarket/capa/` | CAPA | Corrective and Preventive Action records tied to this sub-DHF's post-market experience. | `CAPA-YYYY-NNN.md` at root | CAPA records, root-cause analyses, effectiveness checks |
| `dhfs/postmarket/complaints/` | Complaints | Complaint ledger and adjudicated records for this sub-DHF. | `complaints-ledger.md` + dated records | Complaint ledger, individual complaint files, trending analyses |
| `dhfs/risk-management/` | Risk Management | ISO 14971 hazard analysis, FMEA, risk-benefit analysis for this sub-DHF. Sibling of `design-controls/`, not a child, because risk management is device-level (not design-controls-process-level). | `risk-type.md` at root; matching `.docx` in `formal/` | Risk Management Plan, hazard analysis, FMEA, risk-benefit analysis, risk traceability matrix |
| `dhfs/cybersecurity/` | Cybersecurity | IEC 81001-5-1 assessment, threat model, SBOM, vulnerability management for this sub-DHF. Cross-linked to the filing's 510(k) submission when applicable. | `assessment.md`, `threat-model.md`, `sbom.*` at root; matching `.docx` in `formal/` | Cybersecurity assessment, threat model, SBOM, vulnerability disclosures, SDL evidence |
| `submissions/qsub/` | Q-Sub (Pre-Submission) | Pre-Submission package for FDA engagement. Components: cover letter, device description, proposed intended use, predicate comparison, PCCP summary, specific questions. | `component-name.md` at root; matching `.docx` in `formal/` | Cover letter, device description, proposed intended use, predicate comparison, PCCP summary, FDA questions |
| `submissions/510k/` | 510(k) Submission | 510(k) submission materials. Components: predicate comparison, software documentation, performance data, risk analysis, labeling, SBOM, DICOM conformance statement. | `component-name.md` at root; matching `.docx` in `formal/` | Predicate comparison, software documentation, performance data, risk analysis, labeling, SBOM, DICOM conformance statement |
| `submissions/pccp/` | PCCP | Predetermined Change Control Plan. Components: device and modifications description, change types per module, modification protocols, performance criteria, validation methodology, reporting requirements. | `component-name.md` at root; matching `.docx` in `formal/` | Device/modifications description, change types, modification protocols, performance criteria, validation methodology, reporting requirements |
| `submissions/qsub/correspondence/` | Q-Sub Correspondence | FDA interactions related to the Pre-Submission. Includes acknowledgments, response letters, pre-sub meeting minutes, and follow-up action items. Date-prefixed naming. Capture verbatim FDA language. Action items should be converted into tasks for tracking. | `YYYY-MM-DD-type-topic.md` (e.g., `2026-04-01-fda-response.md`) | Submission acknowledgments, FDA response letters, meeting minutes, action items, outgoing correspondence |
| `submissions/510k/correspondence/` | 510(k) Correspondence | FDA interactions related to the 510(k) submission. Includes acknowledgments, Additional Information requests, response letters, and clearance correspondence. Date-prefixed naming. AI requests have strict response deadlines — note the deadline in the file. | `YYYY-MM-DD-type-topic.md` (e.g., `2026-06-15-fda-ai-request.md`) | Submission acknowledgments, Additional Information requests, responses to FDA, clearance letter, outgoing correspondence |
| `submissions/pccp/correspondence/` | PCCP Correspondence | FDA interactions specific to the PCCP. The PCCP is filed with the 510(k) but may generate separate correspondence if FDA has PCCP-specific questions. File in the most specific location — PCCP-specific here, general 510(k) in the 510k folder. | `YYYY-MM-DD-type-topic.md` (e.g., `2026-07-01-fda-pccp-feedback.md`) | FDA PCCP feedback, responses to PCCP questions, outgoing PCCP correspondence |

**Step 4 — Determine applicable standards and frameworks**

Based on the user's answers, auto-populate the standards and frameworks READMEs:

**Always required** (any medical device software):
- IEC 62304 — Software lifecycle
- ISO 14971 — Risk management
- IEC 62366-1 — Usability engineering
- NIST CSF — Cybersecurity framework
- OWASP — Application security
- NTIA SBOM — Software bill of materials

**Conditionally required**:
- If SaMD → IEC 82304-1 (Health software safety)
- If cybersecurity considerations → IEC 81001-5-1 (Health software security)
- If AI/ML → GMLP (Good Machine Learning Practice)
- If medical imaging → DICOM, IHE Profiles
- If EHR integration → HL7 FHIR
- If surgical navigation → ASTM F2554 (Navigation accuracy)

**Conditionally excluded** (with rationale in README):
- IEC 60601-1 — Only if dedicated medical electrical hardware (not general-purpose computing)
- ISO 13485 / 21 CFR 820 — QMS-level, typically organization-owned not project-owned
- AAMI TIR57 — Covered by IEC 81001-5-1 + NIST CSF
- ISO/IEC 23894 — Covered by GMLP + ISO 14971

For each applicable standard/framework, create a starter file using the template at `${CLAUDE_SKILL_DIR}/templates/standard-file.md`.

For each excluded standard/framework, add a row to the "Evaluated — Not Required" table in the README with the rationale.

**Step 5 — Set up hook infrastructure and run skill setup actions**

1. Create `.claude/hooks/` directory if it doesn't exist
2. Install `register-hook.sh` into `.claude/hooks/` — this is shared infrastructure that skills use to safely register hooks in `settings.json` without overwriting each other. Copy from `${CLAUDE_SKILL_DIR}/templates/register-hook.sh` and make executable.
3. For each skill directory in `.claude/skills/*/SKILL.md`:
   a. Read the SKILL.md and check if it defines a `### \`setup\`` action
   b. If yes → invoke `/skill-name setup` (e.g., `/task setup`)
   c. If no → skip silently
4. Report which skills had setup actions and what they did

This allows skills to self-wire their hooks, config, and dependencies during project creation.

**Step 6 — Report**

Show the user:
- Folder structure created
- Standards and frameworks determined (required vs. excluded)
- Skills installed and setup actions run
- Next steps: populate FDA guidance, begin design controls, run `/medtech-docs dashboard` to see status

### `add-sub-dhf <name> [--parent <path>] [--regulatory <status>] [--filing <filing>]`

Add a new sub-DHF to an existing project. Scaffolds the per-DHF folder layout, adds a new entry to `project.sub_dhfs[]`, and creates the sub-DHF README.

**Arguments**:
- `<name>` — short slug for the new sub-DHF (e.g., `connectivity-adapter`, `cloud-suite`, `drug-library-manager`). Must match `^[a-z][a-z0-9-]*[a-z0-9]$`. Used as the folder name under `dhfs/`.
- `--parent <path>` — optional. Path of the parent sub-DHF (relative to `docs/project/dhfs/`), for nesting a child under a platform sub-DHF. Examples: `cloud-suite`, `cloud-suite/dhfs/fleet-management`. Default: top-level (no parent).
- `--regulatory <status>` — optional. One of `concept | in-development | cleared | mixed`. Default: `in-development`. Use `mixed` only for platform sub-DHFs whose children carry the regulatory weight (the platform itself doesn't ship separately).
- `--filing <filing>` — optional. Name of the submission folder this sub-DHF rolls up into (e.g., `510k-pp3500`). Default: `null` (not yet scoped into a filing).

**Step 1 — Validate the name**:
1. Check that `<name>` matches the slug regex. If not, reject with the error `"invalid sub-DHF name '<name>' — must match ^[a-z][a-z0-9-]*[a-z0-9]$"`.
2. **Leaf-name uniqueness check**: read `project.yml` `sub_dhfs[]` and scan every entry's `path` field. If any existing entry's last path segment equals `<name>`, reject with: `"name '<name>' is already used by '<full-path>'; pick a unique name."` This is the enforcement that lets `/strategy` tag authors write `sub-dhf=<leaf>` without ambiguity (per P3 Q1 decision in task 007).

**Step 2 — Resolve the target path**:
- If `--parent` is omitted: target is `docs/project/dhfs/<name>/`. The new entry's `path` field is just `<name>`.
- If `--parent` is given: target is `docs/project/dhfs/<parent>/dhfs/<name>/`. The new entry's `path` is `<parent>/dhfs/<name>`. Verify the parent exists on disk first; if not, reject with: `"parent sub-DHF '<parent>' not found under docs/project/dhfs/"`.

**Step 3 — Scaffold the per-DHF folder layout** at the target path, identical to what `init` creates for the primary sub-DHF:
```
dhfs/<name>/
├── README.md                ← readme-sub-dhf.md (substitute {{SUB_DHF_NAME}}, {{REGULATORY_STATUS}}, {{FILING}})
├── design-controls/         ← full tree: trace-matrix, plans, user-needs, requirements, architecture, vnv, tool-validation
├── clinical/                ← evaluation-plans, benefit-risk, literature-search
├── postmarket/              ← pmcf-plans, pmcf-studies, capa, complaints
├── risk-management/         ← + formal/
└── cybersecurity/           ← + formal/
```

Use the same templates the `init` action uses — `readme-design-controls.md`, `readme-trace-matrix.md`, `readme-clinical.md`, `readme-postmarket.md`, `readme-risk-management.md`, `readme-cybersecurity.md`, plus `readme-leaf.md` for each leaf folder with substitutions from the leaf-folder table in `init` Step 3.

Skip any folder or README that already exists. This makes `add-sub-dhf` idempotent under re-run — if the user ran it previously and is now adding the `--filing` flag, re-running should update the sub-DHF entry in `project.yml` without disturbing existing content.

**Step 4 — Update `project.yml`**:
Parse `project.yml`, find the `sub_dhfs:` list, and append a new entry:

```yaml
sub_dhfs:
  - path: <name-or-nested-path>
    regulatory: <status>   # default in-development
    filing: <filing>       # default null
    parent: <parent>       # default null
```

Preserve existing entries and all surrounding YAML structure (comments, spacing, other fields). Write `project.yml` atomically — build the new content in memory and write in one operation.

**Step 5 — Report**:
Show the user:
- The new sub-DHF's target path under `docs/project/dhfs/`.
- Which folders and READMEs were created vs. already existed.
- The updated `project.yml` `sub_dhfs[]` entry.
- Next-step suggestions: author the sub-DHF README purpose paragraph, add user needs under `design-controls/user-needs/`, update the composition manifest of any filing that should reference this sub-DHF.

**Depth and recursion**:
`add-sub-dhf` supports arbitrary `--parent` depth via the path form (e.g., `--parent cloud-suite/dhfs/drug-library-manager`). The interactive `init` flow caps nesting at 2 levels to keep the init prompt simple; `add-sub-dhf` has no such cap. For a project that genuinely needs 3+ levels of sub-DHF nesting, run `init` with 2 levels and then `add-sub-dhf` for the deeper children.

**Examples**:
```
# Add a top-level sub-DHF
/medtech-docs add-sub-dhf connectivity-adapter --regulatory in-development

# Add a platform sub-DHF (no filing of its own, children will file)
/medtech-docs add-sub-dhf cloud-suite --regulatory mixed

# Add a child of the platform
/medtech-docs add-sub-dhf drug-library-manager --parent cloud-suite --regulatory in-development --filing 510k-pp3500

# Add a grandchild (nested path)
/medtech-docs add-sub-dhf rule-engine --parent cloud-suite/dhfs/drug-library-manager
```

### `add-standard <name>`

Add a new standard or framework to the project. Creates the file and adds it to the appropriate README.

1. Ask the user:
   - Is this a **standard** (ISO/IEC/ASTM formal standard) or **framework** (industry guidance)?
   - Full title of the document
   - What FDA guidance or regulation references it?
   - Why is it required for this project?
   - Which modules does it apply to?

2. Create the file in the appropriate folder (`docs/external/standards/` or `docs/external/industry-frameworks/`) using the template at `${CLAUDE_SKILL_DIR}/templates/standard-file.md`.

3. Add the entry to the folder's README table.

4. Confirm to the user with the file path.

### `evaluate <name> <required|not-required> <rationale>`

Record an evaluation decision for a standard or framework without creating a full distilled file.

- If **required**: Create a starter file using `${CLAUDE_SKILL_DIR}/templates/standard-file.md` and add to the README's active table.
- If **not-required**: Add to the README's "Evaluated — Not Required" table with the provided rationale. No file created.

This ensures every standard/framework we consider has a documented decision trail.

### `dashboard`

Generate or update `docs/dashboard.html` — a self-contained HTML dashboard showing documentation status across all sections.

**Step 1 — Scan the repository**

For each section, count and classify files:

**External References**:
- `docs/external/fda-guidance/`: Count `.md` files (excluding README)
- `docs/external/standards/`: Count `.md` files (excluding README), read `## Verification Checks` tables and tally pass/fail/pending
- `docs/external/industry-frameworks/`: Count `.md` files (excluding README), check for "Evaluated — Not Required" entries
- `docs/external/clinical-literature/`: Count `.md` files (excluding README)

**Design Controls** (for each subfolder):
- `docs/project/design-controls/plans/`: Count `.md` files (excluding README)
- `docs/project/design-controls/user-needs/`: Count `.md` files
- `docs/project/design-controls/requirements/`: Count `.md` files
- `docs/project/design-controls/architecture/`: Count `.md` files
- `docs/project/design-controls/risk-management/`: Count `.md` files
- `docs/project/design-controls/vnv/`: Count `.md` files
- `docs/project/design-controls/tool-validation/`: Count `.md` files

**Input Analysis**:
- Count `.md` files in each subfolder of `docs/project/input-analysis/`

**Submissions**:
- Count `.md` files in each subfolder of `docs/project/submissions/`

**Standards Compliance**:
- For each standard file in `docs/external/standards/`, read the `## Verification Checks` table
- Count checks by status: `[x]` = passed, `[ ]` = pending, `[!]` = failed, `[~]` = not applicable
- Calculate per-standard and overall compliance percentages

**Step 2 — Generate the HTML**

Read the template from `${CLAUDE_SKILL_DIR}/templates/dashboard.html` and populate it:

1. Replace `{{PROJECT_NAME}}` with the project name from `CLAUDE.md` (first `# ` heading) or the folder name
2. Replace `{{TIMESTAMP}}` with the current date and time
3. For each card, scan the folder and generate section rows:
   - Count `.md` files (excluding README.md) in each subfolder
   - Badge: `complete` (has files), `partial` (some subfolders populated), `empty` (no files)
4. For progress bars:
   - External: percentage of subfolders that have content files
   - Design Controls: percentage of subfolders that have content files
   - Input Analysis: percentage of subfolders that have content files
   - Submissions: percentage of subfolders that have content files
   - Color: `green` (>75%), `yellow` (25-75%), `red` (<25%), `gray` (0%)
5. For Standards Compliance table:
   - Read each `.md` file in `docs/external/standards/`
   - Parse the `## Verification Checks` section
   - Count `[x]`, `[ ]`, `[!]`, `[~]` markers
   - Calculate coverage as `passed / (passed + pending + failed)` (exclude N/A)

Write the populated HTML to `docs/dashboard.html`.

**Step 3 — Report**

Tell the user the dashboard has been generated and provide the file path. Suggest they open it in a browser.

## Best Practices

<!-- Read by /best-practices skill to audit project setup -->

**Scope column** — added in v12 to support the unified sub-DHF shape. Values:
- `shared` — check runs once at project root.
- `per-dhf` — check runs once per entry in `project.sub_dhfs[]`, with the sub-DHF root as the implicit working directory. Path references in "How to Verify" below that start with `dhfs/<path>/` are interpreted relative to that sub-DHF's root; paths without a `dhfs/` prefix are project-relative.
- `per-submission` — check runs once per `submissions/<filing>/` folder.
- `cross-cutting` — check runs once at project root but reads across multiple sub-DHFs (enumerates `project.sub_dhfs[]` and correlates).

Omitted Scope defaults to `shared` (per task 007 ambiguity #1 sign-off).

| Check | How to Verify | Severity | Scope |
|-------|--------------|----------|-------|
| Project manifest exists | `project.yml` exists in project root with `project:`, `sub_dhfs:`, `team:`, `registries:`, and `security:` sections | Required | shared |
| Project has at least one sub-DHF | `project.yml` `sub_dhfs[]` list is non-empty, and every entry's `path` resolves to an existing folder under `docs/project/dhfs/` | Required | cross-cutting |
| Sub-DHF leaf names are unique | For every entry in `project.yml` `sub_dhfs[]`, the last segment of `path` is unique across the list (case-sensitive). | Required | cross-cutting |
| Docs folder exists | `docs/` directory exists with `README.md` | Required | shared |
| Three-tier structure | `docs/external/`, `docs/internal/`, `docs/project/` all exist | Required | shared |
| Strategies folder exists | `docs/project/strategies/` directory exists with `README.md` | Required | shared |
| Sub-DHF README exists | `dhfs/<path>/README.md` exists and contains a purpose paragraph | Required | per-dhf |
| Design controls folder complete | All 7 design control subfolders exist under this sub-DHF: `design-controls/{trace-matrix, plans, user-needs, requirements, architecture, vnv, tool-validation}` | Required | per-dhf |
| Risk management folder exists | `risk-management/` folder exists at the sub-DHF root (sibling of `design-controls/`, not a child) with a `formal/` subfolder | Required | per-dhf |
| Clinical folder complete | `clinical/{evaluation-plans, benefit-risk, literature-search}` all exist under this sub-DHF. Empty leaves are acceptable for early-stage sub-DHFs and reported as INFO. | Recommended | per-dhf |
| Postmarket folder complete | `postmarket/{pmcf-plans, pmcf-studies, capa, complaints}` all exist under this sub-DHF. Empty leaves acceptable and reported as INFO. | Recommended | per-dhf |
| Cybersecurity folder exists | `cybersecurity/` folder exists at sub-DHF root with a `formal/` subfolder. Empty folder acceptable and reported as INFO. | Recommended | per-dhf |
| Platform sub-DHFs have children | For every sub-DHF with `regulatory: mixed`, at least one other `sub_dhfs[]` entry has `parent` pointing to it. Prevents `mixed` from being used to silence the unreferenced-sub-DHF check on leaf components. | Required | cross-cutting |
| Composition manifests referenced | If `sub_dhfs[]` is non-empty AND `submissions/*/composition-manifest.md` glob returns zero matches, emit project-level WARN: "No composition manifests authored — per-submission checks will not run until at least one exists." | Recommended | cross-cutting |
| Standards have verification checks | Every `.md` file in `docs/external/standards/` (excluding README) contains a `## Verification Checks` section | Required | shared |
| Frameworks have evaluation decisions | `docs/external/industry-frameworks/README.md` contains both an active frameworks table and an "Evaluated — Not Required" table | Required | shared |
| Dashboard exists | `docs/dashboard.html` exists | Recommended | shared |
| Dashboard is current | `docs/dashboard.html` was modified within the last 7 days | Recommended | shared |
| No empty design control folders | Every subfolder under `design-controls/` contains at least one `.md` file besides README | Recommended | per-dhf |
| Submissions match pathway | If CLAUDE.md mentions "510(k)", `docs/project/submissions/510k/` exists; if "De Novo", `docs/project/submissions/de-novo/` exists; etc. | Recommended | shared |
| Standards README has exclusion rationale | Every standard/framework in the "Evaluated — Not Required" table has a non-empty rationale | Required | shared |
| READMEs have changelogs | Every `README.md` under `docs/` contains a `## Changelog` section with a table (Date, Author, Summary). In AI-driven workflows, a session may make many edits collapsed into one commit — the changelog captures the rationale that git alone doesn't. | Required | shared |
| READMEs have conventions | Every `README.md` under `docs/` contains a `## Conventions` section documenting naming rules, formatting, and linking guidance for that folder. | Required | shared |
| READMEs follow section order | In every `README.md` under `docs/`, sections appear in meta-model order: Title → Subfolders/Structure → Information Flow/Relationships → Expected Content → Domain-specific → Conventions → For Claude → Changelog. Specifically: `## Conventions` must appear before `## Changelog`, and `## Expected Content` (if present) must appear before `## Conventions`. | Required | shared |
| Leaf READMEs have expected content | Every `README.md` in a leaf folder (no subdirectories) under `docs/` contains a `## Expected Content` or `## Expected Documents` section listing what document types belong in that folder. Exceptions: folders that use domain-specific sections instead (e.g., standards/ uses `## Distilled Standards`, frameworks/ uses `## Active Frameworks`). | Recommended | shared |
| README changelogs are current | When a `README.md` under `docs/` is modified, its `## Changelog` table has an entry matching the current date or the date of the most recent modification. Stale changelogs (last entry significantly older than git last-modified date) should be flagged. | Recommended | shared |

## Notes

- If `$ARGUMENTS` is empty or just "help", show this usage guide
- Every README.md must include a `## Changelog` section. When modifying a README, add a changelog entry with date, author initials, and summary of the change. This is critical in AI-driven workflows where a single session may make many edits that get collapsed into one git commit.
- The `init` action is designed for first-time setup but is safe to re-run — it skips existing folders/files
- The `dashboard` action always regenerates from current state — no stale data
- Standard/framework files should be distilled from actual standard documents, not fabricated. Use `[VERIFY]` markers for content that needs validation against the source document
- The dashboard HTML is self-contained — no external CSS/JS dependencies, viewable by opening directly in a browser

## Changelog

- 13 (2026-04-13): Added `chrome-devtools` to the `project.yml` template's default `approved_mcps:` list in `init` action Step 2. New projects scaffolded by `/medtech-docs init` now get the Chrome DevTools MCP server pre-approved by the secops posture — no separate approval step required when the team first uses it for frontend visual validation. Comment block in the template explains what it does and the `claude mcp add` install command. No functional change to existing projects; only the init-time template is updated. **LOCAL divergence pending upstream push** (hitachi still ships v12).
- 12 (2026-04-13): **Unified sub-DHF shape — every project has at least one sub-DHF from day one.** Rewrote the init folder tree to scaffold `docs/project/dhfs/<primary>/{design-controls, clinical, postmarket, risk-management, cybersecurity}/` instead of the old flat `docs/project/design-controls/...` layout. Single-component and multi-component projects use the same shape; growth is a plain `add-sub-dhf` call, not a migration. Added Step 1 question 9 (primary sub-DHF name, no default). Added `sub_dhfs:` section to the `project.yml` template with leaf-name uniqueness enforcement rule. Added new `add-sub-dhf` action supporting arbitrary `--parent` nesting and `regulatory` / `filing` flags. `risk-management/` is now a sibling of `design-controls/` at the sub-DHF level (it used to be a child of `design-controls/` in v11). Added `clinical/`, `postmarket/`, `cybersecurity/`, and shared `strategies/` to the scaffold. Added Scope column to the Best Practices table classifying every check as `shared`, `per-dhf`, `per-submission`, or `cross-cutting`. Added new per-DHF checks (sub-DHF README exists, risk-management folder exists, platform sub-DHFs have children) and cross-cutting checks (sub_dhfs non-empty, leaf names unique, composition manifests referenced). No migration action — the one-time PDLC_DEMO reorg from the v11 flat shape into `dhfs/pca-device/` is a task 007 P6 execution step, not a skill feature, because there are no other existing projects on the old shape. New templates required but not yet shipped with this version (follow-up): `readme-sub-dhf.md`, `readme-clinical.md`, `readme-postmarket.md`, `readme-risk-management.md`, `readme-cybersecurity.md`, `readme-strategies.md`. See task 007 for design rationale.
- 11 (2026-04-10): Added `tool-validation/` under design-controls (8th subfolder). Tool validation records for software tools used in development per IEC 62304 and FDA guidance — plans, reports, risk assessments, tool inventory. Added to folder tree, leaf table, dashboard scan. Updated best-practices check (7→8 subfolders). Added Step 2b to `init` — after creating `project.yml`, check if CLAUDE.md has a project manifest section and insert one if missing.
- 10 (2026-04-09): Added `project.yml` scaffolding to `init` as new Step 2. Asks user for project name, repo, email domain; pre-populates project identity, team roster template, skill registries, and security policy. Steps renumbered (old 2→3, 3→4, 4→5, 5→6). Added best-practices check for project manifest existence. Replaces `team.md` as the team roster source.
- 9 (2026-04-05): Added trace-matrix/ under design-controls (traceability matrices for DHF cross-referencing). Added default README.md to every folder created by init: internal/source/, internal/source-md/, and all formal/ subfolders. New templates: readme-trace-matrix.md, readme-source.md, readme-source-md.md, readme-formal.md. Updated best practices check (6→7 design control subfolders).
- 8 (2026-03-30): Synced all templates with actual docs/ folder. Rewrote readme-fda-guidance (project-compliance-files model replacing old summary+raw pattern). Added Standards-to-Module Mapping, Supplementary Technical Reports, and For Claude sections to readme-standards. Added For Claude section to readme-design-controls, code-blocked waterfall. Fixed dashboard to scan *.md instead of *-summary.md for FDA guidance. Updated readme-submissions with detailed subfolder descriptions and versioning reference. Updated readme-external with corrected fda-guidance and clinical-literature descriptions. Updated readme-input-analysis with maturation convention. Code-blocked information flow in readme-project.
- 7 (2026-03-30): Added formal/ subfolder pattern for design-controls and submissions. Working markdown at root, controlled documents (DOCX/XLSX) in formal/. Updated init folder tree, leaf table naming conventions, and readme-design-controls template with Document Workflow section.
- 6 (2026-03-30): Restructured docs/internal/ — removed templates/ and correspondence/ leaf folders, replaced with source/ and source-md/ for three-tier SOP pattern (matching FDA guidance). Moved correspondence to submission-specific folders (qsub/, 510k/, pccp/ each get correspondence/). Updated init folder tree, leaf table, readme-internal, readme-docs, and readme-submissions templates.
- 5 (2026-03-30): Formalized README meta-model (section ordering: Title → Subfolders → Relationships → Expected Content → Domain-specific → Conventions → For Claude → Changelog). Added 4 new best practice checks: READMEs have conventions (Required), section order compliance (Required), leaf READMEs have expected content (Recommended), changelog currency (Recommended). Updated leaf template to include Expected Content section. Fixed templates missing Conventions (docs, internal) and Expected Content (clinical-literature, fda-guidance).
- 4 (2026-03-30): Added README changelog requirement — all README.md files must include a ## Changelog section (Date, Author, Summary table). Added as best practice check (Required) and documented in Notes. All 12 README templates updated with changelog section.
- 3 (2026-03-30): Migrated from .claude/commands/ to .claude/skills/ directory structure. Extracted all README templates, standard file template, and dashboard HTML template into `templates/` supporting files. SKILL.md now references templates via `${CLAUDE_SKILL_DIR}` instead of inlining ~400 lines of content.
- 2 (2026-03-30): Embedded full README content for all folders in init action. Tier READMEs (docs, external, internal, project) include information flow and subfolder tables. Special READMEs (standards, frameworks, design-controls) include evaluation tables, waterfall diagrams, and compliance conventions. Leaf folder READMEs include purpose, naming conventions, and linking guidance.
- 1 (2026-03-30): Initial version — init, add-standard, evaluate, and dashboard actions. Self-contained docs/ structure template, standard file template with verification checks, HTML dashboard generation.
