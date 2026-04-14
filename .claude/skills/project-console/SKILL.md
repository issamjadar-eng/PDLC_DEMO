---
name: project-console
description: Scaffold and maintain a local FastAPI project console (agents, documents, dashboards) for a medtech-docs project. Provides `init`, `sync`, `theme`, `run`, and `status` actions. Use when a user asks to "set up project console", "install the console tool", "scaffold a console", "update project console", "scrape a company site for a theme pack", or reports a problem with `tools/project-console/`.
---

# Project Console

A reusable FastAPI-based local console for medtech-docs projects. Ships:

- A FastAPI app (`console/`) with routes for landing, agents chat, documents explorer, and dashboards discovery
- A **template library** of 10 common medtech personas (regulatory, clinical, quality, systems, risk, human factors, R&D, V&V, cybersecurity, post-market) materialized into the project on init
- Two generic **theme packs** (`light`, `dark`) plus a scraping action that builds project-specific theme packs from a company website
- A scaffold action that creates `tools/project-console/` and wires the launcher to import the skill package via `PYTHONPATH`

The skill is **company-agnostic** — no project-specific content, branding, or persona names ever live inside the skill package. Company theme packs are scraped and materialized into the project at `tools/project-console/themes/<slug>/`.

## Dependencies

| Requirement | Needed for | How to satisfy |
|---|---|---|
| `project.yml` | All actions | `/medtech-docs init`, or create manually |
| `project.type: medtech` | Console refuses to run without this | Set in `project.yml` |
| `team.active[]` (≥1 entry) | OAuth attribution, chat author links | Add team roster |
| `security.approved_email_domains[]` (≥1) | OAuth allowlist | Configure in `project.yml` |
| `docs/` tree | Documents explorer + dashboard discovery | `/medtech-docs init` |
| `uv` | Python runtime/venv for the tool | `brew install uv` or `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Claude Code CLI (`claude`) | OAuth for chat | Already installed if using Claude Code |

If any required field is missing, report exactly what's missing and point the user to `/medtech-docs init` or the relevant section of `project.yml`.

## Actions

Parse the user's argument string to determine which action to run.

### `init [--force]`
Scaffold `tools/project-console/` into the current project.

1. Verify `project.yml` exists and has required fields (`project.name`, `project.type: medtech`, `team.active`, `security.approved_email_domains`). If missing, stop with a clear error.
2. Run the scaffolder:
   ```bash
   uv run python .claude/skills/project-console/scripts/scaffold.py init
   ```
   (Add `--force` only if the user explicitly asks to overwrite an existing scaffold.)
3. Report what was created and the next steps printed by the scaffolder.
4. Remind the user they can run `/project-console theme <url>` to build a branded theme pack.

### `sync`
Roll forward the scaffolded tool to match the currently-installed skill version. Use after `/sync-skills pull` brings a newer `project-console` skill.

1. Run:
   ```bash
   uv run python .claude/skills/project-console/scripts/scaffold.py sync
   ```
2. Report which files were updated (skill-owned files only).
3. If the scaffolder reports drift in files not declared in `tools/project-console/README.md`'s `## Customizations` section, surface the drift to the user and ask before overwriting.

### `theme <url> [--name <slug>]`
Scrape a company website and materialize a project-local theme pack at `tools/project-console/themes/<slug>/`.

1. Use WebFetch to pull the given URL.
2. Extract best-effort signals:
   - **Logo** — see the Logo Selection Heuristics block below. This matters most: a bad logo pick is the most visible failure mode of the scrape.
   - **Primary color** — parse inline styles, CSS custom properties, and any linked stylesheet for brand colors
   - **Header/body contrast** — determine light vs dark header from visible styles
   - **Font family** — check `@font-face` declarations and Google Fonts links
   - **Tagline** — pull `<meta name="description">` or a prominent `<h1>`/`<h2>`
3. Write `theme.yaml` into `tools/project-console/themes/<slug>/` with every uncertain token annotated `# [VERIFY] scraped from <url> on <date>`.
4. Write `source.json` recording the URL, fetch timestamp, and a confidence map of which fields were confidently extracted vs guessed.
5. Write a minimal `footer.html.j2` using the scraped tagline.
6. Do **not** auto-select the new theme — report what was extracted, flag what needs verification, and tell the user how to activate it (edit `tools/project-console/console.yaml` `theme: <slug>`).

Default slug (when `--name` is omitted) is derived from the hostname (e.g., `www.arthrex.com` → `arthrex`).

#### Logo Selection Heuristics

The console topnav constrains logos to `height: 28px; max-width: 160px; object-fit: contain` — the image is resized to fit without stretching. That means a tall square logo shrinks to ~28px wide (often unreadable) while a horizontal wordmark scales cleanly. **Prefer horizontal wordmarks.**

When scraping, look in this priority order and stop at the first viable hit:

1. **`<header>` or topnav `<img>`** — whatever the live site renders in its own top bar. This is almost always the authoritative brand logo at a header-friendly aspect ratio.
2. **`<link rel="icon">` or SVG favicon** — fall back if no header `<img>` found. Square, but usually high-resolution.
3. **`/brand/`, `/press/`, `/media-kit/` paths** — many companies publish logo assets at these URLs. Try `og:logo` / `og:image` meta tags first.
4. **Open Graph `og:image`** — often a hero image, not a logo. Only accept if nothing else is available and annotate it `[VERIFY] og:image fallback — may not be a logo`.

**Format priority:** SVG > PNG with transparency > PNG > JPG. SVGs scale losslessly and play nicely with both light and dark topnavs.

**Light/dark variants:** if the scraped site's header is dark (like arthrex.com), also look for a white-on-transparent logo variant (common filenames: `logo-white.svg`, `Logo_White_RGB.png`, `logo-reversed.svg`). Save as `logo.png` (primary, matches the active topnav) and `logo-dark.png` (optional secondary).

**Aspect ratio sanity check:** after download, examine the image dimensions. If width/height > 2 it's a clean horizontal wordmark and works great at the header size. If width/height < 1.2 it's roughly square — still works via `object-fit: contain` but will render small in the topnav; prefer a horizontal alternative if one exists. Don't try to "fix" a square logo with CSS — that's what stretches it. Just pick a better source.

**Write a `logo.meta.json`** alongside the downloaded logo recording the source URL, dimensions, format, and which heuristic tier picked it. This lets the user see why the skill chose what it did and swap to a better asset if they know of one.

### `run`
Start the console locally.

1. Verify `tools/project-console/.project-console.manifest.json` exists (meaning it's been initialized).
2. Run `tools/project-console/run.sh`. This runs `uv sync` on first launch, then starts uvicorn on `http://127.0.0.1:8765`.

### `status`
Report the install state: skill version, installed version, drift summary, theme in use, and count of agents/dashboards discovered.

```bash
uv run python .claude/skills/project-console/scripts/scaffold.py status
```

## File ownership classes

The scaffolded directory `tools/project-console/` contains files of three classes, tracked in `.project-console.manifest.json`:

- **skill-owned** — replaced on `sync` if pristine; skill pulls updates forward. Example: `run.sh`.
- **project-owned** — never touched after `init`. Examples: `console.yaml`, `agents/`, `themes/`, `.env`, `pyproject.toml`.
- **extension-hook** — seams explicitly provided for customization; always left alone on sync. Examples: `console.overrides.css`, `_project_overrides/` template dir, `project_extensions.py`.

When sync detects drift in a skill-owned file that the user hasn't declared in the tool README's `## Customizations` section, prompt the user: accept, keep, or diff — never clobber silently.

## Where code lives

```
.claude/skills/project-console/
  SKILL.md                    # this file
  README.md                   # design & architecture (human-facing)
  VERSION                     # semver
  console/                    # FastAPI app — the reusable Python package
    app.py
    config.py                 # reads project.yml + tools/project-console/console.yaml
    themes.py                 # theme resolver
    auth.py                   # OAuth preflight
    chat/                     # chat routes + domain agent loader + SDK wiring
    documents/                # explorer + renderer + summary + tree
    dashboards/               # routes + glob-scan discovery
    web/
      templates/              # Jinja templates
      static/                 # brand-neutral CSS, JS, favicon, console.overrides.css
  themes/
    light/                    # neutral light fallback
      theme.yaml
      footer.html.j2
    dark/                     # neutral dark fallback
      theme.yaml
      footer.html.j2
  agents/
    templates/                # 10 common medtech personas (materialized into project on init)
  scripts/
    scaffold.py               # init / sync / status implementation
```

The `console/` package is imported by the project's `run.sh` via `PYTHONPATH` injection — there is no install step, no `uv add`, no separate publishing. A `/sync-skills pull` that updates `.claude/skills/project-console/` is immediately effective on the next launch.

## Best Practices

<!-- Read by /best-practices skill to audit project setup -->

| Check | How to Verify | Severity | Scope |
|---|---|---|---|
| Skill installed | `.claude/skills/project-console/SKILL.md` exists | Required | shared |
| Tool scaffolded | `tools/project-console/.project-console.manifest.json` exists | Recommended | shared |
| Theme selected | `tools/project-console/console.yaml` has `theme:` key | Recommended | shared |
| Approved skill listed | `project.yml` `security.approved_skills` includes `project-console` | Required | shared |
| Launcher executable | `tools/project-console/run.sh` is executable | Recommended | shared |
| No pycache in skill | `find .claude/skills/project-console -name __pycache__ -o -name '*.pyc'` returns nothing | Required | shared |
| Tool gitignore blocks pycache | `tools/project-console/.gitignore` contains `__pycache__/` and `*.pyc` | Required | shared |
| Skill gitignore blocks pycache | `.claude/skills/project-console/.gitignore` contains `__pycache__/` and `*.pyc` | Required | shared |

## Changelog

- 1.0.2 (2026-04-14): Two changes — default panels + assistant-framing rename.

  **Default panels.** Adds two default panels to the template library so newly-initialized projects get working cross-functional voices out of the box.
  - **Core Team Advisory Panel** (`agents/templates/core-team-panel.md`) — 5 members: program-manager, regulatory-affairs, clinical-affairs, quality-engineering, rd-lead. Covers program-level decisions across execution, regulatory, clinical, quality, and engineering-feasibility lenses.
  - **Design Review Advisory Panel** (`agents/templates/design-review-panel.md`) — 6 members: systems-engineering, rd-lead, vnv-lead, human-factors, risk-management, quality-engineering. Technical review body for architecture decisions, use-safety trade-offs, test-readiness, and DHF gate reviews. Projects with cybersecurity-critical devices are instructed to append `cybersecurity` as a seventh member.

  **Assistant-framing rename.** Every persona and panel in the template library is renamed and its system prompt rewritten so the nomenclature unambiguously positions these as AI **assistants supporting** the real human team, not replacements for them. Examples:
  - Title: "Regulatory Affairs" → "Regulatory Affairs Assistant"
  - System prompt opener: "You are the Regulatory Affairs lead for this device program" → "You are an AI assistant supporting the Regulatory Affairs team for this device program. You help the human RA leads by..."
  - STAY IN CHARACTER clause rewritten to "never claim to BE the lead or commit the program to anything"
  - Panels retitled: "Core Team Panel" → "Core Team Advisory Panel", "Design Review Panel" → "Design Review Advisory Panel"
  - Group description updated: "These assistants help the real human team think — they do not replace them."

  Also extends `scripts/scaffold.py` `sync` action to copy newly-added agent templates into existing installs (previously `sync` only rewrote `run.sh`). Running `/project-console sync` after pulling this version will materialize the new panel templates while leaving existing project-owned files alone.

  **Post-update:** Run `/project-console sync` to materialize the new panel templates into `tools/project-console/agents/core-team/`. Note that sync does **not** overwrite existing agent files — if you want the assistant-framing rewrite applied to your project's existing personas, you need to either (a) delete your local copies and re-run `init`, or (b) hand-edit to apply the new framing. Then **restart the console** (Ctrl+C the running `run.sh` and relaunch) so the agent loader picks up the new panels and any rewrites — uvicorn `--reload` does not watch the skill package.
- 1.0.1 (2026-04-14): Bugfix — documents tree walker now hides macOS `Icon\r` custom-folder-icon files, Windows `Thumbs.db` / `desktop.ini`, and AppleDouble resource forks (`._*`) in addition to dotfiles. Discovered in Arthrex PCCP where `Icon\r` files at several directory roots were cluttering the explorer. New `_is_hidden()` helper in `console/documents/tree.py` centralizes the junk-file filter so all three walker call sites (`list_children`, `_dir_has_any_children`, `_children`) share the same rules.
  **Post-update:** **Restart the console if it's running.** Uvicorn's `--reload` watches the project's `tools/project-console/` directory (the launcher's CWD), **not** the skill package under `.claude/skills/project-console/console/`. Skill updates require a restart — Ctrl+C the running process and re-run `tools/project-console/run.sh`. (Earlier versions of this changelog entry incorrectly said `--reload` handled it automatically.)
- 1 (2026-04-14): Initial version. Extracted from PDLC_DEMO's hand-built `tools/project-console/`. Generic template library (10 personas), two skill theme packs (light/dark), glob-scan dashboard discovery, manifest-based install tracking, sys.path launcher pattern. Company-agnostic: no brand assets or project names inside the skill package. Ships with `init`, `sync`, `theme`, `run`, `status` actions. Includes a skill-root `.gitignore` to keep `__pycache__/` and `*.pyc` out of the registry; `scaffold.py init` writes the same patterns into every `tools/project-console/.gitignore`. Three Best Practices checks enforce the gitignore coverage and skill cleanliness.
