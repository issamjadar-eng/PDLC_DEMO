# Project Console Skill — Design & Architecture

This document describes the design decisions behind the `project-console` skill. It is not loaded by Claude during normal skill operation — it exists for human understanding.

For skill usage and instructions, see `SKILL.md`.

## Role in the Ecosystem

`project-console` sits downstream of every other skill in the registry. It reads `project.yml` (owned by the project), the `docs/` tree (owned by `medtech-docs`), per-person task folders (owned by `task`), and strategy docs (owned by `strategy`). It writes only into `tools/project-console/` and never touches `project.yml`, `docs/`, or any other skill's territory.

```
project.yml ──────┐
docs/ ────────────┤
tasks/ ───────────┼──► project-console ──► http://127.0.0.1:8765
docs/project/**/  │    (reads)              (chat, docs, dashboards)
  *-tracker.html ─┘
```

## Ownership Split: Skill Package vs Project

The skill package holds all Python code and generic assets. The project holds all data, config, and branded assets.

| Layer | Lives in | Rationale |
|---|---|---|
| FastAPI app (routers, templates, static, dashboards discovery, theme resolver) | `.claude/skills/project-console/console/` | Upgraded via `/sync-skills pull` |
| Generic theme packs (`light`, `dark`) | `.claude/skills/project-console/themes/` | Fallback so the console works out of the box |
| Agent template library (10 common medtech personas) | `.claude/skills/project-console/agents/templates/` | Shared starting point; materialized into project on init |
| Scaffold script (`scaffold.py`) | `.claude/skills/project-console/scripts/` | Runs init/sync/status |
| Materialized agent roster (user-editable after init) | `tools/project-console/agents/` | Project owns its concrete personas |
| Theme selection, dashboards, server, auth overrides | `tools/project-console/console.yaml` | Tool owns its own config |
| Project-specific theme packs (e.g., scraped from company URL) | `tools/project-console/themes/<slug>/` | Project owns its branded assets |
| Runtime deps (`pyproject.toml`, `uv.lock`, `.env`) | `tools/project-console/` | Standard Python tool layout |
| Launcher (`run.sh`) | `tools/project-console/` | Injects skill's `console/` onto PYTHONPATH |

The launcher is the lynchpin of the "skill package is the install" model: `run.sh` sets `PYTHONPATH` to the skill's parent directory and runs `uvicorn console.app:app`. No `uv add`, no wheel, no publishing step.

## Config Contract

The skill only depends on a minimal contract from `project.yml`:

**Required** — skill refuses to start without these:
- `project.name` — shown in landing, topnav, titles
- `project.type: medtech` — gate
- `team.active[]` with at least one entry (name, github, email, role)
- `security.approved_email_domains[]` with at least one domain (OAuth allowlist)

**Optional** — read if present, sensible fallbacks otherwise:
- `project.repo`, `regulatory_pathway`, `device_class`, `device_family`, `lead_product`
- `dhfs[]` (drives documents explorer DHF filter)
- `team.active[].task_folder` (drives chat author → task links)

**Not in the contract** (skill must not depend on):
- Any PDLC-specific fields (`lead_product`, `portfolio_context`, `composition`, `capabilities`) — present in PDLC_DEMO but absent in Arthrex PCCP
- Specific DHF counts or names
- Specific file paths under `docs/project/submissions/` — discovery is glob-pattern driven
- Any brand asset (logo, palette, font) — all brand state lives in project-owned theme packs

The contract was validated against both PDLC_DEMO and Arthrex PCCP before v1 shipped.

## Theme Packs: Skill-Agnostic via Scrape-and-Materialize

Skills that hard-code customer branding aren't reusable — they're larger per-customer skills. `project-console` solves the multi-project branding problem by shipping only generic defaults (`light`, `dark`) and a scraping action (`/project-console theme <url>`) that materializes a branded theme pack into the **project** at `tools/project-console/themes/<slug>/`.

Each materialized theme pack is a self-contained directory:

```
tools/project-console/themes/<slug>/
  theme.yaml          # tokens (primary, topnav_bg, font_body, tagline, ...)
  source.json         # { source_url, scraped_at, confidence: {...} }
  logo.png            # downloaded from the source site
  favicon.ico         # downloaded or derived
  footer.html.j2      # rendered into _base.html at request time
```

`theme.yaml` tokens map to CSS custom properties:

| YAML key | CSS variable | Used for |
|---|---|---|
| `primary` | `--brand-primary` | Links, buttons, card hovers, topnav underline |
| `primary_dark` | `--brand-primary-dark` | Hover states |
| `topnav_bg` | `--topnav-bg` | Topnav background |
| `topnav_text` | `--topnav-text` | Topnav text/logo |
| `body_bg` | `--body-bg` | Main content background |
| `text` | `--body-text` | Body text |
| `font_body` | `--font-body` | Body font stack |

The `console.css` file defines structural colors (borders, shadows, disabled states) as hard-coded neutrals and brand colors as `var(--brand-*)` with fallback. Legacy `--gl-*` variables are aliased to the new `--brand-*` names so the existing CSS keeps working during the refactor.

Every scraped token is annotated `# [VERIFY] scraped from <url> on <date>` in the materialized `theme.yaml`, so the user knows what to eyeball against an official brand guide before treating the theme as production-ready.

## Drift & Customization Management

The scaffolded `tools/project-console/` directory tracks every file it writes in `.project-console.manifest.json`. Each file is classified:

- **skill-owned** — replaced on sync if pristine, reconciled if drifted
- **project-owned** — never touched after init
- **extension-hook** — seams the skill expects users to edit, never touched

Extension hooks are the happy path for customization — most users never hit the reconcile flow because the seams cover 90% of what they need:

| Extension file | Purpose |
|---|---|
| `console.overrides.css` | Arbitrary CSS overrides loaded after `console.css` |
| `project_extensions.py` | User-defined FastAPI routers, middleware, lifespan hooks |
| `_project_overrides/` | Jinja template overrides loaded first by the template loader |

For anything outside the extension-hook surface, the user declares their changes in the scaffolded `tools/project-console/README.md` `## Customizations` section. On sync, drift that's declared triggers a 3-way diff (accept / keep / merge); drift that isn't declared triggers a stronger warning that forces a decision.

The manifest is committed narrowly: `skill_version`, `installed_at`, `last_synced_at`, and a file-class map. Hashes are recomputed on demand at sync time by comparing the project's current file against the skill's current file at the installed version. This avoids merge noise while keeping the "contract" reviewable.

## Dashboard Discovery

Dashboards are discovered by glob-scanning `docs/` for HTML files matching configurable patterns. Default patterns (shipped in the `console.yaml` default):

```yaml
dashboards:
  patterns:
    - docs/**/*-tracker.html
    - docs/**/*-dashboard.html
    - docs/**/dashboard.html
    - docs/**/*-tree.html
```

Each discovered file becomes a dashboard with:
- **slug** — derived from filename (`submission-tracker.html` → `submission-tracker`)
- **title** — pulled from `<title>` tag; fallback to slug
- **description** — pulled from `<meta name="description">`
- **group** — derived from parent directory (`submissions/` → "Submissions")
- **source** — the virtual path relative to repo root

Projects can add curated metadata via `console.yaml` `dashboards.overrides: {slug: {title, description, group, order}}`. The scan + overrides merge at load time.

## Compatibility Bar

Before any `project-console` skill update ships to the hitachi registry, a dry `init` must run successfully in both PDLC_DEMO (the demo) and Arthrex PCCP (a real adjacent project). This enforces that the skill generalizes and catches PDLC-specific assumptions that might otherwise leak in.

## Why This Shape

The design evolved through several iterations during task 015 (see `tasks/ben/015-project-console-skill.md` for the full trail):

1. **Agent roster** — initially considered `docs/project/agents/`, settled on `tools/project-console/agents/` because personas are tool config, not DHF content. Skill ships templates; init materializes.
2. **Dashboard discovery** — initially a hard-coded dict, then considered a `dashboards.yml` sidecar, finally settled on glob scan + `console.yaml` overrides after observing that both PDLC_DEMO (`*-tracker.html`) and Arthrex PCCP (`dashboard.html`, `*-tree.html`) use different file-name conventions.
3. **Python package shape** — rejected installable package in favor of `PYTHONPATH` injection so `/sync-skills pull` is immediately effective without a rebuild step.
4. **Theming** — initially shipped GlobalLogic and Arthrex theme packs inside the skill, reverted after realizing "a reusable skill that knows its customers isn't reusable." Now the skill is company-agnostic; branding is a scrape-and-materialize user action.
5. **Config home** — rejected `project.yml` as the tool-config home in favor of `tools/project-console/console.yaml` for clean install/uninstall semantics and consistency with other per-tool configs.
6. **Drift management** — three ownership classes, extension-hook files as the happy path, declared drift via the tool README `## Customizations` section, narrow committed manifest.

## Future Work

- **sync drift detection** — current `scaffold.py sync` only rewrites `run.sh` when it diverges from the template. Full 3-way diff reconciliation against `console.css`, template files, etc., is not yet implemented.
- **theme scrape action** — the `SKILL.md` documents the action but `scaffold.py` doesn't yet implement the scraping pipeline. Intended to be driven by Claude via WebFetch rather than by the scaffold script directly.
- **Extension-hook surfaces** — `project_extensions.py` and `_project_overrides/` are documented but not yet loaded by `app.py`. Scheduled for v1.1.
- **Dark mode switching** — right now the theme is fixed at launch. A runtime toggle would be nice but requires cookies + render-time theme resolution.
