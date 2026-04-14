# 015 — Project Console Skill (genericize console bootstrap)

**ID**: 015
**Created**: 2026-04-14
**Status**: In Progress
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: Medium

---

## Goals

Turn the one-off `tools/project-console/` that currently lives inside PDLC_DEMO into a reusable skill (`project-console`) that any medtech-docs-based project can install via `/sync-skills pull` and then run something like `/project-console init` to scaffold an identical console for their own repo.

The skill must be **project-agnostic**: it assumes only the contracts that `medtech-docs`, `task`, `strategy`, `tracker`, `secops`, and `lessons` already impose (project.yml + `docs/` tree + DHF shape + `docs/project/submissions/submission-tracker.html`). It must not carry any PP3500, PainEase, or infusion-pump specifics. All project identity is read at runtime from `project.yml` — exactly how the current console already does it.

Success criteria:
1. A clean medtech-docs project (fresh `/medtech-docs init`) can run `/project-console init` and end up with a working console that shows their agents, their documents, and any dashboards they've registered.
2. The skill updates cleanly via `/sync-skills pull` — the installed console code lives under the skill package, the **project-local** console instance under `tools/project-console/` is the thin shell that imports from the skill.
3. Adding a new dashboard (like the submission tracker) is a one-entry edit to a registry that the skill reads, not a code change.
4. PDLC_DEMO itself migrates off its hand-built console onto the skill-driven version without regressions.

## Non-Goals (for v1)

- Not rewriting the chat, documents, or agents modules — those already work; this task is about packaging and genericization, not re-architecture.
- Not building new dashboards beyond what already exists (submission tracker).
- Not solving multi-tenant / hosted console — this is still a single-project, run-locally console.

## Todos

- [ ] Phase 1 — System boundaries: confirm skill scope, ownership split between skill package vs project-local shell, and how updates flow.
- [ ] Phase 2 — Component inventory: enumerate current console modules (app, chat, documents, dashboards, config, auth, web/templates, web/static) and classify each as `generic` / `project-shaped` / `project-specific`.
- [ ] Phase 3 — Config contract: define what `project.yml` fields + filesystem conventions the skill depends on. Nothing outside that contract is allowed to leak into skill code.
- [x] Phase 4 — Dashboard registry design: **absorbed into Phase 2** (glob scan of `docs/**/*-tracker.html`, `*-dashboard.html`, `dashboard.html`, `*-tree.html` + `console.yaml` `dashboards:` section for overrides).
- [x] Phase 5 — Agent discovery: **absorbed into Phase 2** (skill ships template library at `.claude/skills/project-console/agents/templates/`; `init` materializes into `tools/project-console/agents/`; console reads from there at launch; project owns after init).
- [x] Phase 6 — Init action: `scripts/scaffold.py init` scaffolds `tools/project-console/` (console.yaml, pyproject.toml, run.sh, agents/, themes/, manifest). `SKILL.md` documents `/project-console init` action wired to this scaffolder.
- [x] Phase 7 — Upgrade action: `scripts/scaffold.py sync` implemented (narrow — replaces `run.sh` when it diverges, bumps manifest version). Full 3-way diff reconciliation is future work; stubbed in README.
- [x] Phase 8 — PDLC_DEMO migration: old `tools/project-console/console/` package deleted (code now in skill); `domain_agents/` → `agents/`; new `console.yaml` with `theme: globallogic`; materialized GL theme pack in `themes/globallogic/` (tokens + footer + logo + favicon + Manrope font); new `run.sh` uses `PYTHONPATH` injection. TestClient smoke test: all 7 routes 200 (`/`, `/agents`, `/dashboards`, `/dashboards/submission-tracker`, `/documents`, `/theme/assets/logo.png`, `/theme/assets/favicon.ico`).
- [ ] Phase 9 — Push upstream: not done (waiting on user review + sister-project dry init in Arthrex PCCP).

## Phase 3 — Config Contract

The skill is only allowed to depend on the contract defined here. Anything outside of it must not leak into skill code. The contract is validated by running a dry `init` in both PDLC_DEMO and Arthrex PCCP — if a field is in the contract but not in either project's `project.yml`, either the field is wrong or `project.yml` needs updating (via `medtech-docs` or a documented migration).

### Contract source comparison

Checked both reference projects' `project.yml` on 2026-04-14:

| Field | PDLC_DEMO | Arthrex PCCP | In contract? |
|---|---|---|---|
| `project.name` | ✅ `PDLC_DEMO` | ✅ `Arthrex PCCP` | **required** |
| `project.repo` | ✅ | ✅ | optional (used in about page only) |
| `project.type` | ✅ `medtech` | ✅ `medtech` | required (gate — skill only runs for `medtech`) |
| `project.regulatory_pathway` | ✅ `510k` | ✅ `510k` | optional (cosmetic header) |
| `project.device_class` | ✅ `II` | ✅ `II` | optional (cosmetic header) |
| `project.device_family` | ✅ `patient-controlled-analgesia-pump` | ✅ `hiplink` | optional (cosmetic header) |
| `project.lead_product` | ✅ | ❌ | optional |
| `project.portfolio_context` | ✅ | ❌ | optional |
| `project.composition` | ✅ | ❌ | optional |
| `project.capabilities` | ✅ | ❌ | optional |
| `dhfs[]` | ✅ | ❓ (check) | optional (consumed by documents explorer + dashboard scan, absent OK) |
| `team.active[]` | ✅ | ✅ | required (at least one entry — used for chat author attribution) |
| `security.approved_email_domains[]` | ✅ | ✅ | required (OAuth allowlist) |
| `security.approved_skills[]` | ✅ | ✅ | optional (informational in About panel) |

### Required fields (minimal contract)

The skill refuses to start if any of these are missing:

```yaml
project:
  name: <string>         # shown in landing, topnav, page titles
  type: medtech          # must equal "medtech"

team:
  active:
    - name: <string>     # at least one entry required
      github: <string>
      email: <string>
      role: <string>

security:
  approved_email_domains:
    - <string>           # at least one domain required for OAuth preflight
```

Nothing else is required. The skill runs with just these.

### Optional fields (read if present, fallback if not)

```yaml
project:
  repo: <github-slug>              # shown in about panel
  regulatory_pathway: <string>     # "510k", "de-novo", "pma", etc. — cosmetic subtitle
  device_class: <string>           # "II", "III" — cosmetic subtitle
  device_family: <string>          # cosmetic subtitle, also used by medtech-docs
  lead_product: <string>           # landing-page subtitle
  theme: <string>                  # theme-pack name (per Phase 2 decision) — default: "light"

dhfs:                              # if present, documents explorer adds a DHF nav filter
  - path: <string>
    filing: <string|null>

team:
  active:
    - <same as required, plus:>
      task_folder: <string>        # drives chat author links into tasks/<folder>/
      added: <date>

security:
  approved_email_domains: [...]    # already required above
  approved_skills: [...]           # informational
```

### Filesystem conventions the skill depends on

These are directory-shape assumptions baked into the console. Both reference projects already meet them (enforced by `/medtech-docs init`):

| Path | Purpose | Required |
|---|---|---|
| `docs/` | Root of the documents explorer tree | **required** |
| `docs/external/`, `docs/internal/`, `docs/project/` | Three-tier doc structure (medtech-docs convention) | required |
| `docs/project/dhfs/` | DHF subfolders (any depth) — scanned by explorer | optional (may be empty pre-init) |
| `docs/project/submissions/` | Submission folders — scanned for `*-tracker.html` + `*-dashboard.html` | optional |
| `docs/project/strategies/` | Shared strategy docs | optional |
| `tasks/<person>/` | Per-person task folders — used for author→task links in chat | optional |
| `tools/project-console/` | Installed scaffold location | **required** (created by `init`) |
| `tools/project-console/agents/` | Materialized agent roster | **required** (created by `init`) |
| `tools/project-console/dashboards.yml` | Dashboard discovery config | **required** (created by `init`) |
| `tools/project-console/themes/` | Materialized theme packs | optional (falls back to skill `light`/`dark`) |
| `tools/project-console/.env` | OAuth secrets + Anthropic key | **required at run time** |
| `.claude/skills/project-console/` | Skill install (source of `console/` package) | **required** (delivered by `/sync-skills pull`) |

### What is explicitly NOT in the contract

The skill must not depend on any of these even if they exist:

- `project.lead_product`, `portfolio_context`, `composition`, `capabilities` — PDLC-isms not present in Arthrex
- A specific DHF count or set of DHFs (Arthrex is just starting, may have zero DHFs committed)
- Specific directory names under `docs/project/` beyond the three-tier convention
- PDLC persona names (the `kol/` group, specific clinician agents) — skill ships templates only
- Any file named `submission-tracker.html` — discovery is glob-pattern driven
- GlobalLogic branding in any form — all brand assets live in project-owned theme packs

### How Arthrex PCCP's dry init would go

Today:

```
Arthrex PCCP
  project.yml          ✅ has name, type=medtech, team, security.approved_email_domains
  docs/                ✅ exists
    external/, internal/, project/    ✅
    project/dhfs/      ✅ (exists but inventory TBD)
    project/submissions/ ✅ (has submission-tracker.html)
  tools/               ❌ does not exist — `init` creates it
  .claude/skills/project-console/   (would need /sync-skills pull)
```

`/project-console init` would:
1. Create `tools/project-console/` and scaffold the project shell
2. Materialize the 10 agent templates → `tools/project-console/agents/`
3. Write `dashboards.yml` with default glob patterns
4. Write `.env.example`
5. Write the manifest and scaffolded README with empty `## Customizations`
6. Print next steps (uv sync, run `theme https://www.arthrex.com`, run)

Nothing in this flow requires any Arthrex-specific field that isn't already in their `project.yml`. Contract validated.

### Phase 3 resolved — tool config location

**Decision (2026-04-14):** Option (b). All tool-specific config (theme selection, dashboard globs + overrides, OAuth callback URL override, port, log level) lives in `tools/project-console/console.yaml`. `project.yml` stays strictly about project identity, team, security, and skill registries — the skill's `init` action never writes to it.

Rationale (settled after weighing downsides):
- **Clean uninstall** — `rm -rf tools/project-console/` removes every trace; no dangling keys in `project.yml`.
- **Clean install** — `init` only writes inside `tools/project-console/`, never touches `project.yml`. Smallest possible blast radius.
- **Tool owns its config** — matches the existing pattern (`pyproject.toml`, `.env`, `agents/`, `themes/` all already live with the tool). One exception for theme would be inconsistent.
- **Theme selector lives with the theme packs** — materialized packs are already in `tools/project-console/themes/`, so the selector belongs in the same directory, not in `project.yml`.

**Consolidation follow-up:** Phase 2 originally planned a separate `tools/project-console/dashboards.yml`. With `console.yaml` as the tool-config home, dashboards become a section inside `console.yaml` rather than a sibling file — fewer files, one place to look. Final layout of the tool-config:

```yaml
# tools/project-console/console.yaml
theme: globallogic              # project-local theme pack name, resolved
                                # against tools/project-console/themes/ first,
                                # then skill defaults (light/dark)

dashboards:
  patterns:                     # filesystem globs, discovery (Phase 2 decision)
    - docs/**/*-tracker.html
    - docs/**/*-dashboard.html
    - docs/**/dashboard.html
    - docs/**/*-tree.html
  overrides:                    # optional per-slug metadata
    submission-tracker:
      title: "Submission Package Tracker"
      group: "Submissions"
      order: 1

server:
  host: 127.0.0.1
  port: 8000
  log_level: info

auth:
  callback_url: null            # null → derive from host:port
```

The separate `dashboards.yml` file is dropped; everything lives in `console.yaml`.

## Phase 2.5 — Drift & Customization Management

**Problem:** The skill scaffolds `tools/project-console/` into a project. Two update paths exist:

1. **Skill-driven updates.** User runs `/project-console sync` after a `/sync-skills pull` brings a newer version of the skill. Skill wants to roll forward improvements (new routes, fixed bugs, new dashboards, refactors).
2. **Direct user edits.** User opens `tools/project-console/console/app.py` and adds a router, or tweaks `console.css`, or drops a new template. No skill involvement.

The skill must not silently clobber #2 when #1 happens. It also can't just "never touch anything" or the skill loses its whole point — updates must flow. So the skill needs to *know* when drift has happened, classify it, and reconcile it.

### Three file ownership classes

The install tracks every file it scaffolds and categorizes each into one of three classes:

| Class | Ownership | Sync behavior |
|---|---|---|
| **skill-owned** | Skill writes, user is expected not to edit. Hash tracked. | On sync: if hash unchanged → replace freely. If hash changed → drift detected, enter reconcile flow. |
| **project-owned** | Skill writes once at init, never touches again. | On sync: skipped entirely. Includes `agents/`, `dashboards.yml`, `themes/<custom>/`, `.env`, `pyproject.toml` (after init), `theme.yaml` overrides. |
| **extension-hook** | Skill ships an empty or minimal sidecar file that the user can freely edit; the main file imports/includes it. | On sync: skill-owned file is replaced; extension-hook file is never touched. |

### Manifest — `tools/project-console/.project-console.manifest.json`

Created by `/project-console init`, updated by every `/project-console sync`. Schema:

```json
{
  "skill_version": "1.0.0",
  "installed_at": "2026-04-14T19:30:00Z",
  "last_synced_at": "2026-04-14T19:30:00Z",
  "files": {
    "console/app.py": {
      "class": "skill-owned",
      "hash": "sha256:abc123...",
      "skill_version_installed": "1.0.0"
    },
    "console/dashboards/router.py": {
      "class": "skill-owned",
      "hash": "sha256:def456...",
      "skill_version_installed": "1.0.0"
    },
    "console/project_extensions.py": {
      "class": "extension-hook",
      "hash": "sha256:empty",
      "skill_version_installed": "1.0.0"
    },
    "agents/": { "class": "project-owned" },
    "dashboards.yml": { "class": "project-owned" },
    "themes/": { "class": "project-owned" }
  }
}
```

Files under `class: project-owned` do not carry hashes — the skill commits to never touching them after init.

### Extension-hook files (first-party customization surface)

Rather than forcing users to hack skill-owned files, the scaffold includes explicit seams for common customizations:

| Extension file | Purpose | How the skill uses it |
|---|---|---|
| `console/project_extensions.py` | User-defined FastAPI routers, middleware, lifespan hooks | `app.py` imports and mounts anything found here, if present |
| `web/static/console.overrides.css` | Arbitrary CSS overrides | `_base.html` links it after `console.css` |
| `web/templates/_project_overrides/` | Jinja template overrides | Jinja loader prefers this dir before the skill's `web/templates/` |

These are the "happy path" for customization: if a user wants to add a new page, a new API route, a CSS tweak, they do it in an extension-hook file, and `sync` is guaranteed to leave it alone. The scaffold's README tells them so.

### Customization declaration — `tools/project-console/README.md` "## Customizations" section

The scaffold's README (installed by `init`, user-owned afterward) includes a dedicated **## Customizations** section that the user is expected to keep current. Format:

```markdown
## Customizations

_Anything you've changed outside of `project_extensions.py`, `console.overrides.css`, or `_project_overrides/` should be declared here so `/project-console sync` knows what to preserve and what to ask about._

- **console/chat/router.py** — Added `/custom-report` endpoint in the patient-review flow. 2026-04-14, ben.
- **web/templates/_base.html** — Added a top-of-page banner for the Q2 release freeze. 2026-04-14, ben. _Temporary — remove after 2026-05-01._
```

The skill **reads** this section during sync. Declared customizations are treated as "known intent" and flow into a guided reconcile flow. Undeclared customizations (hash drift with no README entry) are flagged as "unexpected drift" and surfaced to the user with a stronger warning.

### Sync flow (`/project-console sync`)

```
1. Load manifest
2. For each skill-owned file:
     hash current → compare to manifest.hash
     - hash matches → pristine; replace with new skill version
     - hash differs:
         - if file is in README ## Customizations → declared drift
         - if not → undeclared drift
3. For each project-owned file:
     skip entirely
4. For extension-hook files:
     skip replacement; if skill version introduces a new extension hook, scaffold it
5. Reconcile:
     - Pristine files → replaced silently, reported as "N files updated"
     - Declared drift → show 3-way diff (old skill / user version / new skill), ask user: accept new, keep mine, merge manually
     - Undeclared drift → surface with warning: "You edited this file directly but didn't declare it in README ## Customizations. Do you want to (a) declare it and keep your version, (b) overwrite with new skill version, (c) see the diff?"
6. Write updated manifest with new hashes + new skill_version
7. Report summary + anything the user must act on
```

### Init flow (`/project-console init`)

```
1. Check for existing tools/project-console/ → if present, refuse unless --force or suggest sync
2. Scaffold directory tree from skill
3. Write manifest.json recording every file's class and hash
4. Write scaffolded README.md with an empty ## Customizations section
5. Write scaffolded .env.example, pyproject.toml, dashboards.yml, theme resolver stub
6. Materialize agent templates → tools/project-console/agents/
7. Print next steps: run uv sync, run /project-console theme <url> if desired, run /project-console run
```

### Why this works

- **Most users never hit drift** because extension hooks cover 90% of customizations.
- **Declared drift is respected**: the skill asks rather than clobbers, and the 3-way diff gives the user real choice.
- **Undeclared drift is discoverable**: hash comparison catches silent edits, and the skill forces a decision rather than failing silently.
- **Project-owned state is inviolate**: agents, dashboards, themes, env, and lockfiles are never touched after init, full stop.
- **Upgrade path is honest**: when the skill ships a genuinely incompatible change, the sync flow says so and defers to the user rather than pretending it can auto-merge.

### Phase 2.5 resolved — manifest scope

**Decision (2026-04-14):** Committed-narrowly (option c). The committed manifest contains `skill_version`, `installed_at`, `last_synced_at`, and the file-class map only. Hashes are computed on demand during `sync` by walking the tree and hashing each skill-owned file. The "pristine" reference hashes come from the skill's own installed source at `.claude/skills/project-console/` at the `skill_version_installed` version — i.e., we always compare the project's current file against the skill's current file at install time, not against a stored hash.

Implication: the manifest is a small, stable JSON document that only changes on init, sync, or explicit file-class promotions (e.g., user moves a file to extension-hook class). It will rarely conflict in merges.

## Phase 2 — Component Inventory

Every file under the current `tools/project-console/console/` classified as:
- **G** = generic, moves to skill as-is
- **S** = project-shaped (generic logic, reads from project config)
- **P** = project-specific (does not move to skill)

_Enriched from a walk of `pwd/tools/project-console/` on 2026-04-14. File count: 32 source files under `console/`, plus 20 agent markdowns under `domain_agents/`._

### Console Python package

| File | Class | Notes |
|---|---|---|
| `console/__init__.py` | G | Empty. |
| `console/__main__.py` | G | `uvicorn console.app:app` entry. Moves as-is. |
| `console/app.py` | G | Lifespan + router wiring. Moves as-is. |
| `console/auth.py` | S | OAuth preflight. Reads client id / allowed domains from env + `project.yml` `security` — already config-driven. Moves as-is. |
| `console/config.py` | S | Loads `project.yml`, derives `repo_root`, `domain_agents_dir`, `data_dir`. **Refactor needed**: currently computes `repo_root = console_root.parent.parent` (walks up from `tools/project-console/console/` → repo). In the skill version, `console_root` is inside `.claude/skills/project-console/`; `repo_root` must come from `CLAUDE_PROJECT_DIR` env (set by the launcher). Also: `domain_agents_dir` must change from `console_root / "domain_agents"` to `repo_root / "tools/project-console/agents"` (per decision 1). |
| `console/chat/__init__.py` | G | Empty. |
| `console/chat/domain_agents.py` | G | Loads `.md` files with frontmatter into `DomainAgent` / `Group` dataclasses. Pure loader — takes a directory, returns data. Moves as-is. |
| `console/chat/panels.py` | G | Round-robin + LLM-moderator streaming logic. No project assumptions. Moves as-is. |
| `console/chat/router.py` | G | Landing + agent routes. References `config.project_name` / `config.device` — already config-driven. Moves as-is. |
| `console/chat/sdk_client.py` | G | Anthropic SDK wrapper with prompt caching. Moves as-is. |
| `console/chat/sources.py` | G | Resolves glob patterns against `repo_root`. Moves as-is (once `repo_root` fix in `config.py` lands). |
| `console/dashboards/__init__.py` | G | Empty (committed earlier today). |
| `console/dashboards/router.py` | S | **Refactor needed**: replace the hard-coded `DASHBOARDS` dict with a loader that reads `tools/project-console/dashboards.yml` + scans the glob patterns (per decision 2). Routes and templates stay as-is. |
| `console/documents/__init__.py` | G | Empty. |
| `console/documents/renderer.py` | G | Markdown/HTML/text renderer. Moves as-is. |
| `console/documents/router.py` | G | Documents explorer + raw/download endpoints. Moves as-is. |
| `console/documents/summary.py` | G | Streams LLM summary of a file. Moves as-is. |
| `console/documents/tree.py` | G | Virtual-path tree walker with exclusions. Moves as-is. |

### Templates

| File | Class | Notes |
|---|---|---|
| `web/templates/_base.html` | G | Topnav + GlobalLogic footer. **Footer branding should become configurable**: the `<footer>` is hard-coded GlobalLogic. Options: (a) read `project.yml` `project.brand` block for logo + links, (b) make the whole footer a template `include` that projects can override, (c) accept GlobalLogic branding as-is since both PDLC and Arthrex are GlobalLogic projects. Leaning (a). |
| `web/templates/index.html` | G | Landing page cards. Pulls `config.project_name` / `config.device`. |
| `web/templates/agents_index.html` | G | Lists groups + agents from the loaded roster. |
| `web/templates/chat.html` | G | Chat UI. |
| `web/templates/documents_explorer.html` | G | Split-pane tree + viewer. |
| `web/templates/dashboards_index.html` | G | Registry-driven card grid. |
| `web/templates/dashboard_view.html` | G | Full-bleed iframe embed with header/actions. |

### Static assets

| File | Class | Notes |
|---|---|---|
| `web/static/console.css` | S | Uses GlobalLogic palette variables (`--gl-purple`, etc.). Follows the footer-branding decision above. |
| `web/static/chat.js` | G | Chat stream + thread persistence. |
| `web/static/explorer.js` | G | Docs explorer interactions. |
| `web/static/markdown.js` | G | Client-side markdown rendering helpers. |
| `web/static/fonts/manrope-latin.woff2` | S | Brand font — same decision as CSS palette. |
| `web/static/img/favicon.ico` | S | Same decision. |
| `web/static/img/globallogic-logo.png` | S | Same decision. |

### Project-level (under `tools/project-console/`, not `console/`)

| File | Class | Notes |
|---|---|---|
| `tools/project-console/ARCHITECTURE.md` | P | Becomes the skill's `README.md` (adapted). |
| `tools/project-console/README.md` | P | Replaced by a shorter project-local README generated by `/project-console init`. |
| `tools/project-console/pyproject.toml` | S | Template shipped by skill; `init` materializes into the project. Deps: fastapi, uvicorn, anthropic, jinja2, pyyaml, python-dotenv, httpx. |
| `tools/project-console/run.sh` | S | Launcher — this is where `sys.path.insert(0, ...)` goes (per decision 3). Template shipped by skill. |
| `tools/project-console/uv.lock` | P | Generated per project, never shipped. |
| `tools/project-console/domain_agents/core-team/*` | **P → template source** | These 10 files *are* the personas the skill should ship. Distill them into `.claude/skills/project-console/agents/templates/` (strip PP3500-specific content from prompts, keep the generic role + suggested source globs). |
| `tools/project-console/domain_agents/kol/*` | P | KOL agents are named physicians grounded in PDLC literature — project-specific, stay in PDLC_DEMO, never ship as templates. |

### Component inventory summary

- **21 files move as-is** (generic, no refactor)
- **8 files refactor** (config.py path resolution, dashboards/router.py discovery, and 6 branding files)
- **3 files do not move** (PDLC-specific README/ARCHITECTURE/uv.lock)
- **10 files become the template library** (`core-team/*.md` distilled into skill)
- **10 files stay in PDLC_DEMO as KOL roster** (named physicians — project-specific)

### Phase 2 resolved — theming

**Decision (2026-04-14, revised):** The skill is company-agnostic. It ships only two generic theme packs (`light` and `dark`), and a separate action scrapes a company website on request to *materialize* a branded theme pack into the **project**, not the skill. Materialized themes are remembered locally in `tools/project-console/themes/` so subsequent launches don't re-scrape. No company-specific content ever lives inside the skill.

**Architecture — skill defaults + project-owned materialized themes:**

```
.claude/skills/project-console/themes/            # generic, ships with skill
  light/
    theme.yaml          # neutral light tokens
    footer.html.j2      # generic footer ("Powered by project-console")
  dark/
    theme.yaml          # neutral dark tokens
    footer.html.j2

tools/project-console/themes/                     # project-owned, gitignored or committed
  <company-slug>/
    theme.yaml          # scrape-derived tokens, editable
    logo.png            # downloaded logo asset
    logo-dark.png       # optional dark-bg variant
    favicon.ico
    fonts/              # webfonts if downloadable
    footer.html.j2      # company tagline + links
    source.json         # metadata: source URL, scrape date, confidence flags
```

**`theme.yaml` shape (same for both skill defaults and materialized themes):**

```yaml
name: Arthrex
primary: "#003478"          # [VERIFY] scraped from arthrex.com 2026-04-14
primary_dark: "#00264d"
primary_tint: "#e6edf5"
topnav_bg: "#000000"
topnav_text: "#ffffff"
body_bg: "#ffffff"
text: "#1a1a1a"
font_body: "Inter"          # [VERIFY] placeholder
font_heading: "Inter"
tagline: "Helping Surgeons Treat Their Patients Better®"
source_url: "https://www.arthrex.com"
```

**Project selects theme in `project.yml`:**

```yaml
project:
  theme: arthrex      # project-local theme in tools/project-console/themes/arthrex/
  # or: light / dark  (skill defaults)
```

**Resolution order at launch time:**

1. Read `project.theme` from `project.yml`.
2. Look first in `tools/project-console/themes/<name>/` (project-owned).
3. Fall back to `.claude/skills/project-console/themes/<name>/` (skill defaults — `light` and `dark` only).
4. If neither exists, log a warning and fall back to `light`.

Optional per-project overrides still go in `tools/project-console/theme.yaml` and merge on top of whatever was resolved. This lets a project run `light` or `dark` and tweak a handful of tokens without creating a full theme pack.

**New skill action — `/project-console theme <url> [--name <slug>]`:**

Scrapes a company website and materializes a theme pack into `tools/project-console/themes/<slug>/`. The action:

1. Fetches the given URL via WebFetch (respects the sandboxed fetch rules the skill runs under).
2. Extracts best-effort signals:
   - **Logo**: finds `<img>` in `<header>` region, downloads it; if both a white-on-dark and a full-color variant are discoverable (as arthrex.com has), downloads both.
   - **Primary color**: inspects linked stylesheets / inline styles / brand CSS variables; if nothing parseable, leaves `[VERIFY]` placeholder.
   - **Topnav vs body backgrounds**: computes approximate light/dark posture from the header styling.
   - **Font family**: reads `@font-face` or Google Fonts links.
   - **Tagline**: pulls `<meta name="description">` or hero-region `<h1>`/`<h2>` text.
3. Writes `theme.yaml` with every uncertain token flagged `# [VERIFY] scraped from <url> on <date>`.
4. Writes `source.json` with the source URL, fetch timestamp, and a confidence map (which fields were confidently extracted vs guessed) so `/project-console theme --refresh` can re-scrape and show a diff later.
5. Reports what was extracted and what needs manual verification. Does not auto-select the theme — user updates `project.yml` `project.theme: <slug>` when they've reviewed the pack.

**"Remember" semantics:** the materialized pack is persisted under `tools/project-console/themes/<slug>/`. Whether it's gitignored or committed is a project choice — `/project-console init` adds an entry to `.gitignore` that users can delete if they want theme packs in version control.

**v1 ships with:**

1. **`themes/light/`** — neutral light theme: white body, light gray topnav, blue-gray accent, system sans-serif. Generic footer.
2. **`themes/dark/`** — neutral dark theme: near-black body, slightly lighter topnav, same blue-gray accent, system sans-serif. Generic footer.
3. **The `theme <url>` action** — scrape-and-materialize, with `[VERIFY]` annotation convention.

PDLC_DEMO and Arthrex PCCP each run `/project-console theme https://www.globallogic.com` and `/project-console theme https://www.arthrex.com` respectively after install, review the result, tweak as needed, commit (or not), and set `project.theme` in `project.yml`. The skill never carries either company's assets.

**Branding-adjacent file classifications updated:**

| File | Previous class | New class | Notes |
|---|---|---|---|
| `web/static/console.css` | S | S (refactor) | Route all palette literals through CSS variables; resolved theme supplies `<style id="theme-overrides">` block injected into `_base.html`. |
| `web/static/fonts/manrope-latin.woff2` | S | **P (stays in PDLC_DEMO)** | PDLC's `globallogic` theme pack lives in `tools/project-console/themes/globallogic/fonts/` after a `/project-console theme https://www.globallogic.com` run; it is project-local, not shipped with the skill. |
| `web/static/img/favicon.ico` | S | **P (stays in PDLC_DEMO)** | Same — project-local GL theme pack. |
| `web/static/img/globallogic-logo.png` | S | **P (stays in PDLC_DEMO)** | Same — project-local GL theme pack. |
| `web/templates/_base.html` footer | G (refactor) | G | Renders `{% include resolved_theme_footer %}`. The GL footer markup (services/industries/social links) gets adapted into PDLC_DEMO's materialized `globallogic/footer.html.j2`; the skill defaults ship minimal generic footers. |

## Phase 1 — System Architecture (DRAFT)

_Starting top-down per the standing "architecture-top-down" rule. This is the initial sketch; refine with the user before drilling into modules._

### Boundaries

The project-console skill sits **outside** the medtech-docs documentation tree and **downstream** of every other skill. Its inputs are:

```
                ┌─────────────────┐
project.yml ───►│                 │
                │                 │
docs/*       ──►│ project-console │──► FastAPI app on localhost
                │     skill       │    serving agents, documents,
agents (local)─►│                 │    dashboards, chat
                │                 │
dashboards   ──►│                 │
(registry)      └─────────────────┘
```

It never writes into `docs/`. It only reads. This is the same contract medtech-docs's own tools observe.

### Ownership split — skill vs project

| Layer | Where it lives | Why |
|---|---|---|
| FastAPI app code (routers, templates, static, renderer, tree, chat SDK wiring) | **skill package** (`.claude/skills/project-console/console/`) | Reusable; upgrades via `/sync-skills pull` |
| uv workspace, `.env`, `pyproject.toml`, launcher script | **project** (`tools/project-console/`) | Each project has its own venv + secrets |
| Agent roster (domain_agents YAMLs) | **project** (new home TBD — likely `docs/project/agents/` or `.claude/project-console/agents/`) | Every project has its own KOL panel |
| Dashboard registry | **project** (TBD — project.yml section vs dashboards.yml vs filesystem glob) | Each project has its own set of dashboards |
| Auth config (OAuth client id, allowed domains) | **project** `.env` + `project.yml` security section | Already the case today |

The key inversion vs today: the skill package holds **all** the Python code; the project holds **data + config**. Today it's the opposite — code lives under `tools/project-console/console/` and there is no skill.

### Update flow

```
hitachi registry                 project
─────────────────                ───────
.claude/skills/                  .claude/skills/
  project-console/                 project-console/   ◄── /sync-skills pull
    SKILL.md                         (symlinked or cloned)
    console/
      app.py                       tools/project-console/
      chat/                          pyproject.toml    (imports skill package)
      documents/                     .env              (gitignored)
      dashboards/                    launcher.sh
      web/
```

The project-local `tools/project-console/` becomes a **thin workspace shell** whose only job is: (1) hold a uv venv, (2) hold secrets, (3) import the skill's `console` package and run it.

### Ship common personas as templates (refinement 2026-04-14)

Every medtech project tends to want the same roster of domain voices — regulatory affairs, clinical, quality/QMS, systems engineering, cybersecurity, human factors, software/firmware, risk management, V&V, post-market. The **personas** are common; only the **sources** (which files in `docs/` ground them) and the **project-specific details** (device name, predicate, pathway) differ.

This reframes the skill's role with respect to agents:

- **Skill ships**: a library of template persona definitions under `.claude/skills/project-console/agents/templates/` — YAML files with a generic system prompt, suggested source glob patterns (e.g., `docs/external/fda-guidance/**/*.md`, `docs/project/dhfs/*/design-controls/risk-management/**`), and a default panel membership recommendation.
- **Project owns**: its concrete roster, materialized on `/project-console init` by copying the templates into the project's agent home. Once materialized, the project can edit prompts, add project-specific context, swap sources, add or remove personas, and define panels. The skill never overwrites them after init.
- **Upgrade path**: `/project-console sync` offers to re-diff the templates against the project's materialized agents (opt-in, never destructive — probably shows a diff and asks), so projects can pull in improved template prompts as they evolve upstream.

This is the same pattern `medtech-docs update-external-references` uses for FDA guidance imports (task 012): skill ships distilled references, action imports them into the project on request, project owns its copies.

**Implication**: the skill now has **two** agent directories conceptually:
1. `.claude/skills/project-console/agents/templates/` — reusable persona library (read-only, upgraded via `/sync-skills pull`).
2. `<project agent home>` — materialized project-specific roster (owned by project, read by console at runtime).

Question 1 below now specifically means: where does #2 live?

### Resolved decisions

1. **Project-owned agent roster home** → `tools/project-console/agents/` (option c). Colocated with the uv shell, `.env`, and the launcher. Outside both `docs/` (so reviewers don't mistake persona prompts for DHF deliverables) and `.claude/` (so agents aren't buried in tool-config state). The template library continues to ship inside the skill at `.claude/skills/project-console/agents/templates/`; `/project-console init` copies templates → `tools/project-console/agents/`.

2. **Dashboard discovery** → filesystem scan of configurable glob patterns, overlaid by an optional metadata file. Real-world signal from both projects:
   - PDLC_DEMO: `docs/project/submissions/submission-tracker.html`
   - Arthrex PCCP: `docs/dashboard.html`, `docs/project-tree.html`, `docs/project/submissions/submission-tracker.html`

   No single hard-coded suffix covers both projects. The skill will ship with a default pattern list:
   ```
   docs/**/*-tracker.html
   docs/**/*-dashboard.html
   docs/**/dashboard.html
   docs/**/*-tree.html
   ```
   These live in `tools/project-console/dashboards.yml` as an editable `patterns:` list. Projects can add, remove, or override patterns without touching the skill.

   Each discovered file becomes a dashboard with:
   - **slug**: derived from the filename (`submission-tracker.html` → `submission-tracker`)
   - **title**: pulled from the HTML `<title>` tag (fallback: slugified filename)
   - **description**: pulled from `<meta name="description">` (fallback: empty)
   - **source**: the file's path relative to repo root
   - **group**: derived from the parent directory (`submissions/` → "Submissions")

   Optional `dashboards.yml` overrides: authors can add a `dashboards:` map keyed by slug to customize title/description/group/order without editing the HTML. The skill merges discovery + overrides at load time.

   This gets us: (a) zero-config works for both PDLC_DEMO and Arthrex PCCP out of the box, (b) projects can author new dashboards just by dropping `*-tracker.html` or `*-dashboard.html` files under `docs/`, and (c) curated metadata stays authorable when needed.

3. **Python package shape** → `sys.path` injection at launcher time. The skill's `.claude/skills/project-console/console/` directory *is* the install; no separate `uv add` step. `tools/project-console/pyproject.toml` owns only runtime deps (fastapi, uvicorn, anthropic, jinja2, pyyaml, python-dotenv, httpx). The launcher script resolves `CLAUDE_PROJECT_DIR/.claude/skills/project-console/console` and `sys.path.insert(0, ...)` before `import console.app`. Matches the existing skill-install model — `/sync-skills pull` updates the skill directory and the next launch picks up the changes with no rebuild.

4. **Skill package contents** — the skill ships the same two-file pattern as `task` and `medtech-docs`:
   - `SKILL.md` — loaded by Claude; actions (`init`, `sync`, `run`, `add-dashboard`), dependency declarations, usage guide
   - `README.md` — design & architecture doc for humans; explains the ownership split, the template-library pattern, dashboard discovery, the sys.path launcher, and the sister-project compatibility bar. Not loaded by Claude at runtime.
   Directory layout:
   ```
   .claude/skills/project-console/
     SKILL.md
     README.md
     console/            # Python package (FastAPI app — the reusable code)
       app.py
       config.py
       auth.py
       chat/
       documents/
       dashboards/
       web/
         templates/
         static/
     agents/
       templates/        # common medtech personas shipped with the skill
         regulatory.yaml
         clinical.yaml
         quality.yaml
         systems-engineering.yaml
         cybersecurity.yaml
         human-factors.yaml
         software.yaml
         risk-management.yaml
         verification-validation.yaml
         post-market.yaml
     scripts/
       scaffold-project-console.sh   # materializes tools/project-console/ into a project
   ```

5. **`dashboards.yml` lifecycle** — written by `/project-console init` to `tools/project-console/dashboards.yml` alongside `agents/`, `pyproject.toml`, and `.env.example`. Confirming the user's question: **yes**, the skill creates and stores it there. Initial contents are the default pattern list (the four globs from decision 2) and an empty `dashboards:` override map. Projects can edit freely; `/project-console sync` never overwrites an existing file, only offers to merge newly-shipped default patterns if the upstream skill adds any.

### Open decisions (remaining)

_(none — Phase 1 complete)_

2. **Dashboard discovery strategy.** Three candidates:
   - (a) Project.yml section: declarative, auditable, matches security allowlist pattern.
   - (b) `tools/project-console/dashboards.yml`: colocated with the console, looks like a config file.
   - (c) Filesystem glob: drop any `*.dashboard.html` file into `docs/project/` and it auto-shows up. Most hands-off, hardest to validate.
3. **Python package shape.** Does the skill ship a real installable Python package (so `tools/project-console/pyproject.toml` can `uv add git+<registry>` or path-import), or does the project-local shell just `sys.path.insert(0, skill_dir)` at launch? The former is cleaner; the latter is simpler and matches how other skills (task, medtech-docs) are just shell+markdown.

## Changelog

- 2026-04-14: Task created. Drafted Phase 1 architecture (boundaries, ownership split, update flow, three open decisions). Awaiting user decision on open question 1 (agent roster home) before moving to Phase 2 component inventory.
- 2026-04-14: Refinement — skill will ship a library of common medtech personas as templates (regulatory, clinical, QA, systems, cybersecurity, human factors, software, risk, V&V, post-market) under `.claude/skills/project-console/agents/templates/`. `/project-console init` materializes them into the project; project owns and customizes from there. `/project-console sync` will offer non-destructive diffs against upstream templates. Question 1 now specifically scopes the project-owned (materialized) roster location; the template library always ships with the skill.
- 2026-04-14: Compatibility constraint — every design decision must validate against the sister project at `../../projects/arthrex/pccp/`. Both PDLC_DEMO and Arthrex PCCP use the medtech-docs skill stack; skills must generalize to both. Persona templates in particular must be generic enough for a PCA infusion pump (PDLC) *and* an Arthrex surgical device without PDLC-specific assumptions leaking through. Before pushing project-console upstream, run a dry init in Arthrex PCCP as the minimum compatibility bar.
- 2026-04-14: Decision — project-owned agent roster lives at `tools/project-console/agents/` (option c). Colocated with uv shell and `.env`. Template library still ships in the skill.
- 2026-04-14: Decision — dashboard discovery = filesystem glob scan + optional `dashboards.yml` overrides. Checked sister project (`../../projects/arthrex/pccp/`) and found three file-name patterns in use (`*-tracker.html`, `dashboard.html`, `*-tree.html`), confirming no single suffix generalizes. Skill ships default pattern list; projects can extend. Title/description/group inferred from HTML meta; overrides keyed by slug. See resolved decisions 2 in task body.
- 2026-04-14: Decision — Python package shape = `sys.path` injection at launcher. Skill directory *is* the install; no `uv add` step. Matches existing skill-install model and means `/sync-skills pull` delivers skill updates with no rebuild step downstream.
- 2026-04-14: Decisions 4 & 5 — skill package matches the `task` / `medtech-docs` two-file convention (`SKILL.md` for Claude, `README.md` for humans, design & architecture). Sampled `.claude/skills/task/README.md` and `.claude/skills/medtech-docs/README.md` to confirm the house style before committing. Full directory layout drafted. Confirmed that `/project-console init` creates `tools/project-console/dashboards.yml` with the default pattern list and empty overrides map, and that `sync` never clobbers an existing file. Phase 1 complete.
- 2026-04-14: Phase 2 component inventory complete. Walked all 32 files under `tools/project-console/console/` + 20 agent markdowns under `tools/project-console/domain_agents/`. Classified: 21 generic (move as-is), 8 refactor (config.py path resolution, dashboards discovery, branding files), 3 not-moving (project README/ARCHITECTURE/uv.lock), 10 template-library source (core-team agents — distill into skill), 10 PDLC-only (KOL roster). Key finding: the existing PDLC core-team roster *already is* the generic persona list the skill needs — major shortcut for the template library. Key refactor: `config.py` must read `CLAUDE_PROJECT_DIR` instead of walking up from its own path, because in the skill world `console/` lives inside `.claude/skills/`, not inside the repo. Branding decision (CSS palette + logo) surfaced as Phase 2 open question — three candidates (accept GL default / CSS-var overrides / full theming).
- 2026-04-14: Decision — full theming via named theme packs + optional project overrides. Initially proposed shipping `themes/globallogic/` and `themes/arthrex/` inside the skill.
- 2026-04-14: **Revision** — skill must stay company-agnostic. Skill ships only generic `themes/light/` and `themes/dark/`. New action `/project-console theme <url>` scrapes a company website and materializes a branded pack into `tools/project-console/themes/<slug>/` (project-owned, remembered locally). Resolution order: project-local → skill defaults → `light` fallback. PDLC_DEMO runs the action against globallogic.com after install; Arthrex PCCP runs it against arthrex.com. The skill itself ships no company assets. Materialized packs carry `source.json` with fetch metadata so `theme --refresh` can re-scrape. Every uncertain token carries `# [VERIFY] scraped from <url> on <date>`. Phase 2 complete (revised).
- 2026-04-14: Phase 2.5 drafted — drift & customization management. Three file ownership classes (skill-owned, project-owned, extension-hook). Manifest at `tools/project-console/.project-console.manifest.json` tracks class + hash + skill_version per file. Extension hooks (`console/project_extensions.py`, `console.overrides.css`, `_project_overrides/` template dir) are the happy-path customization surface. The scaffolded project README carries a `## Customizations` section that users maintain; the skill reads it on `sync` to classify drift as declared vs undeclared. Sync flow: pristine files replaced silently, declared drift gets a 3-way diff with accept/keep/merge, undeclared drift surfaces with a warning and forces a decision. Project-owned paths (agents/, dashboards.yml, themes/, .env) never touched after init. One open question: should the manifest be committed, gitignored, or committed-narrowly (hashes recomputed)? Lean: committed-narrowly.
- 2026-04-14: Decision — manifest committed-narrowly (option c). Committed fields: `skill_version`, `installed_at`, `last_synced_at`, file-class map. Hashes computed on demand during sync; pristine reference comes from the skill's own source at the installed version. Manifest rarely conflicts in merges; stays a small stable contract. Phase 2.5 complete.
- 2026-04-14: Phase 3 drafted — config contract. Cross-referenced `project.yml` in PDLC_DEMO and Arthrex PCCP. Minimal required contract: `project.name`, `project.type=medtech`, `team.active[]` (≥1), `security.approved_email_domains[]` (≥1). Optional fields (all with fallbacks): repo, regulatory_pathway, device_class, device_family, lead_product, theme, dhfs[], task_folder. Explicitly NOT in contract: PDLC-specific fields (`lead_product`, `portfolio_context`, `composition`, `capabilities`), specific DHF counts, PDLC persona names, `submission-tracker.html` as a literal path. Filesystem contract: three-tier `docs/` structure required (already enforced by medtech-docs); `tools/project-console/` created by `init`. Arthrex PCCP dry init walked — nothing blocks. One open question: where does tool-specific config live — `project.yml`, `tools/project-console/console.yaml`, or hybrid (identity in project.yml, operations in tool-local)? Lean: hybrid.
- 2026-04-14: Decision — tool config option (b). Everything tool-specific (theme selection, dashboards, server, auth overrides) lives in `tools/project-console/console.yaml`. `project.yml` is never written to by `/project-console init`. Follow-up consolidation: the separately-planned `dashboards.yml` is folded into `console.yaml` as a `dashboards:` section — one tool-config file total. Phase 3 complete. **Implication for Phases 4 & 5:** dashboard discovery (Phase 4) and agent discovery (Phase 5) designs are fully covered by Phase 2 decisions (glob scan + console.yaml overrides for dashboards; skill-shipped templates materialized into `tools/project-console/agents/` for agents). No separate Phase 4 or 5 work needed — marking them absorbed.
- 2026-04-14: **Phases 6, 7, 8 executed.** Built `.claude/skills/project-console/` (53 files): `SKILL.md`, `README.md`, `VERSION` (1.0.0), `console/` package (refactored `config.py` to read `CLAUDE_PROJECT_DIR` and `console.yaml`; new `themes.py` resolver with project→skill→fallback chain; new `dashboards/discovery.py` with glob scan + overrides merge; rewrote `_base.html` to inject theme CSS variables via middleware and render theme-supplied footer; refactored `console.css` to route all brand literals through `--brand-*` CSS variables with neutral fallbacks and legacy `--gl-*` aliases); two skill theme packs (`themes/light`, `themes/dark`) with `theme.yaml` + `footer.html.j2`; 11 agent template markdowns (`agents/templates/_group.md` + 10 personas — distilled from PDLC core-team with all PP3500/PDLC_DEMO specifics stripped); `scripts/scaffold.py` with init/sync/status actions. Migrated PDLC `tools/project-console/`: deleted old `console/` package (code now in skill), renamed `domain_agents/` → `agents/` via `git mv`, wrote new `console.yaml` with `theme: globallogic` + submission-tracker override, wrote `run.sh` using `PYTHONPATH` injection, created materialized `themes/globallogic/` pack (tokens + footer.html.j2 + logo.png + favicon.ico + Manrope font restored from git HEAD), wrote `.project-console.manifest.json`. Added `project-console` to `project.yml` security.approved_skills. **TestClient smoke test: all 7 routes 200** (`/`, `/agents`, `/dashboards`, `/dashboards/submission-tracker`, `/documents`, `/theme/assets/logo.png`, `/theme/assets/favicon.ico`). Skill is ready for sister-project (Arthrex PCCP) dry init and upstream push to hitachi.
<!-- STRATEGY CONTENT: architecture, drift-management, scaffold-lifecycle -->

## Strategy

**Scaffold lifecycle: three ownership classes + declared-drift reconciliation.** Any skill that scaffolds code into a project faces the "vendored-with-local-edits" problem. The project-console skill resolves it by categorizing every scaffolded file into one of three ownership classes (skill-owned / project-owned / extension-hook), tracking pristine hashes in a committed manifest, and reading a user-maintained `## Customizations` section of the tool's README as the declaration of intentional divergence. Pristine skill-owned files replace silently on sync; declared drift enters a 3-way diff flow; undeclared drift surfaces with a warning and forces an explicit user decision.

**Why:** Two failure modes are both unacceptable. (1) "Sync never touches anything" means the skill can't deliver improvements — users pull the registry, nothing changes, the skill might as well not ship updates. (2) "Sync overwrites blindly" means any user edit is a landmine that explodes on the next sync. The middle path requires knowing which files the user *owns*, which files they've *legitimately customized*, and which files they've *silently drifted*. Hash tracking plus declared customizations gives the skill enough information to reconcile forward without either being useless or destructive. Extension hooks further reduce the problem by giving users a first-class customization surface that sync is guaranteed not to touch — most drift should never hit the reconcile flow at all.

**How to apply:** Any skill that scaffolds tool code into a project should use this pattern. Ship a manifest at install time, classify every file up front, provide explicit extension-hook files for common customization needs, document the `## Customizations` declaration convention in the scaffolded README, and treat sync as an interactive flow that asks rather than clobbers when drift is detected. Never make sync silent on drift, in either direction.
<!-- STRATEGY CONTENT: architecture, theming, multi-project-skill, generalization -->

## Strategy

**Skill-agnostic theming via scrape-and-materialize.** The project-console skill treats branding as project-owned, not skill-owned. The skill ships two generic defaults (`light`, `dark`) and a scraping action; company-specific theme packs live exclusively in the project under `tools/project-console/themes/`. No company name, color, logo, or asset ever lives inside the skill package.

**Why:** The initial design shipped `themes/globallogic/` and `themes/arthrex/` inside the skill. This was wrong — a reusable skill that knows the names of its customers isn't actually reusable, it's just a larger two-project skill. Every future downstream project would need another PR to ship its theme pack upstream. Flipping it so the skill ships *only* a scraping capability + neutral fallbacks means (a) the skill has zero knowledge of any specific company, (b) materializing a new brand is a user action, not a skill edit, and (c) the theme pack lives where the rest of the project's branded assets live, which is the project.

**How to apply:** Any reusable skill that renders UI should avoid baking customer-specific branding into the skill package. Ship neutral defaults plus an action to materialize customizations into the project. When a scraping-based approach is viable (brand inference from a public site), use it with explicit `[VERIFY]` annotations on uncertain tokens and a `source.json` metadata file so the materialized artifact is re-derivable later. Treat materialized assets as project-owned from the moment they land — never overwrite without explicit user opt-in.
<!-- STRATEGY CONTENT: architecture, skill-design, template-vs-materialized -->

## Strategy

**Skill-as-template-library pattern.** The project-console skill follows the same "skill ships distilled content, project owns its materialized copy" pattern already used by `medtech-docs update-external-references` (FDA guidance imports, task 012). This avoids the trap of either (a) hard-coding project-specific personas into skill code — which would require a skill edit every time a project wants a different regulatory persona — or (b) shipping an empty skill that gives every new project a blank-canvas problem.

**Why:** Users of a "start a medtech console" skill overwhelmingly want the same 10-ish domain voices with prompts already written; what differs between projects is *which documents ground those voices* and *device-specific context*. So the high-value default is "pre-built personas with generic prompts + source-glob hints"; the customization surface is "point them at the right docs and add your device context."

**How to apply:** Any project console installed via this skill gets a usable agent panel immediately after `/project-console init` without hand-writing YAML. The skill owns the persona library (upgraded via `/sync-skills pull`), the project owns the materialized roster (never overwritten). New personas added upstream are offered via `/project-console sync` as opt-in imports, not forced updates.
