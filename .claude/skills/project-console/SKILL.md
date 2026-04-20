---
name: project-console
description: Scaffold and maintain a local FastAPI project console (agents, documents, dashboards) for a medtech-docs project. Provides `init`, `sync`, `theme`, `run`, `start`, and `status` actions. Use when a user asks to "set up project console", "install the console tool", "scaffold a console", "update project console", "start the console", "restart the console", "scrape a company site for a theme pack", or reports a problem with `tools/project-console/`.
version: 1.4.0
updated: 2026-04-15
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

### `init [--force] [--port N]`
Scaffold `tools/project-console/` into the current project.

1. Verify `project.yml` exists and has required fields (`project.name`, `project.type: medtech`, `team.active`, `security.approved_email_domains`). If missing, stop with a clear error.
2. **Ask the user to confirm the port** before running the scaffolder:
   - Default is `8765`.
   - Check whether the default is already in use with `lsof -ti tcp:8765`. If it is, tell the user who holds it (another project's console, for example) and **suggest the next free port** (8766, 8767, …) instead.
   - If the user has another preference, honor it. Pass the confirmed value to `--port N`.
3. Run the scaffolder:
   ```bash
   uv run python .claude/skills/project-console/scripts/scaffold.py init --port <N>
   ```
   (Add `--force` only if the user explicitly asks to overwrite an existing scaffold.)
4. Report what was created and the next steps printed by the scaffolder, including the configured port.
5. Remind the user they can run `/project-console theme <url>` to build a branded theme pack. The port can be changed later by editing `tools/project-console/console.yaml` `server.port` — both `run.sh` and `start.sh` read it at launch.

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
Start the console locally. **Fails fast** if another console is already listening on the configured port — for an idempotent start that automatically stops any existing instance, use `start` instead.

1. Verify `tools/project-console/.project-console.manifest.json` exists (meaning it's been initialized).
2. Run `tools/project-console/run.sh`. This:
   - Reads `server.host` and `server.port` from `console.yaml` (falls back to `127.0.0.1` / `8765`).
   - Runs `uv sync` on first launch.
   - Strips macOS Finder junk (`Icon\r`, `._*`) from `.venv/` before launch — these can crash `jsonschema.iterdir()` at import if they leak into `site-packages/`.
   - Starts uvicorn on `http://<host>:<port>`.

### `start`
Idempotent launcher — **start or restart** in one command. If a console is already running on the configured port, `start` stops it first (TERM, then KILL if needed) and then launches fresh. This is the recommended way to reload after skill code changes, since `uvicorn --reload` does **not** watch the skill package.

1. Verify `tools/project-console/.project-console.manifest.json` exists.
2. Run `tools/project-console/start.sh`. The script:
   - Reads `server.port` from `console.yaml` (falls back to `8765` if absent)
   - Checks `lsof -ti tcp:$PORT` for any existing listener
   - If found, sends SIGTERM to the PID(s); waits briefly; escalates to SIGKILL for any straggler
   - Then `exec`s `run.sh` so the process table stays clean
3. Exits with whatever `run.sh` exits with — typical foreground `uvicorn --reload`.

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

- 1.4.1 (2026-04-16): **Drop `xargs -r` from scaffolded `start.sh`** (`START_SH_TEMPLATE` lines 229, 234 of `scaffold.py`). `xargs -r` (no-run-if-empty) is a GNU extension; BSD xargs rejects it with `xargs: illegal option -- r`, silently swallowed by `|| true`. Net effect on macOS: the TERM-then-KILL cascade for stopping an existing listener was a no-op — `start.sh` would print "stopping existing console" and then fail to actually stop it, resulting in port-in-use errors on the subsequent bind. The outer `if [ -n "$existing" ]` already guards empty input, making `-r` redundant on both platforms. Discovered during task 067 cross-platform audit.
  **Post-update:** Run `/project-console sync` on any existing console scaffold to regenerate `tools/project-console/start.sh` without `-r`. Projects that never ran `/project-console start` on Mac are unaffected.
- 1.4.0 (2026-04-15): **Trace Matrix: one-click init via Claude Agent SDK.** New `POST /trace-matrix/{dhf}/init/stream` SSE endpoint that runs the full `/trace-matrix init` skill action — including LLM-authored adapter generation — via the `claude-agent-sdk.query()` interface with `allowed_tools=[Bash, Read, Write, Edit, Glob, Grep]`, `permission_mode='bypassPermissions'` (localhost dev tool), `cwd=repo_root` so the skill lookup resolves, and `max_turns=40` to cap a runaway loop. The empty-state view template now has two buttons: **Initialize with Claude** (runs the LLM flow; uses tokens) and **Build this DHF now** (runs the deterministic `build.py`; fast, no LLM). Live output panel consumes the SSE stream via `fetch` + `ReadableStream` and renders token text, tool calls (e.g. `[tool] Write: path/to/file`), and the final `ResultMessage` summary, then auto-reloads on `done`.
  **Bug found + fixed during implementation:** uvicorn `--reload` watches `tools/project-console/` recursively. When the init flow writes a generated parser adapter to `tools/project-console/trace-matrix/adapters/<layer>.py`, watchfiles would kill uvicorn mid-stream and abort the init subprocess. `run.sh` now passes `--reload-exclude` patterns for `trace-matrix/**`, `.venv/**`, `__pycache__/*`, and `.data/*` so file writes under those paths don't trigger a reload.
  Verified live on Arthrex PCCP (task ben/054): clicked the button, watched the stream render 30+ tool calls over 10 minutes (Read SKILL.md → Read project.yml → Bash `ls` various dirs → Write `trace-matrix.yml` → Read `analyze.py` → Bash `analyze.py` → Read SAD doc → Write custom `architecture.py` adapter), then ran `build.py` to produce `docs/project/dhfs/hiplink-suite/design-controls/trace-matrix/trace-matrix.{md,json}` with 6 architecture nodes parsed via the generated adapter.
  **Post-update:** Run `/project-console sync` to regenerate `tools/project-console/run.sh` with the new `--reload-exclude` patterns. Existing scaffolds already have `console.yaml` and don't need config changes. The `Initialize with Claude` button only appears on the empty-state view (when a DHF has no sidecar yet) — builds after that continue to use `Rebuild this DHF` on the populated view.
- 1.3.0 (2026-04-15): **Trace Matrix: path normalization, empty-state UX, surfaced build errors.** Three bugs surfaced on Arthrex PCCP when clicking the `Build this DHF` button before `/trace-matrix init` had been run:
  1. **Loader double-nested the sidecar path.** `list_dhfs()` joined `repo_root / docs/project/dhfs / <path>` under the assumption that `project.yml` `dhfs[].path` holds a leaf name (the PDLC_DEMO convention). Arthrex PCCP uses the full path there (`docs/project/dhfs/hiplink-suite`), which produced `docs/project/dhfs/docs/project/dhfs/hiplink-suite/...` and 404'd every lookup. Loader now normalizes: accepts `leaf:` as an explicit field, accepts `path:` as either a leaf (`pca-device`) or an already-prefixed full path (`docs/project/dhfs/pca-device`), and resolves to a single canonical `dhf_root`.
  2. **Router raised raw HTTPException 404 on missing sidecar.** `GET /trace-matrix/{dhf}` now renders `trace_matrix_view.html` in empty-state mode when the DHF is known but no sidecar exists yet — same template, different branch — so the user sees a "Build this DHF now" button plus guidance instead of `{"detail": "No trace-matrix sidecar..."}` as JSON.
  3. **Build endpoints silently swallowed failures.** `POST /trace-matrix/build` and `POST /trace-matrix/{dhf}/build` now inspect `returncode` and, on failure, capture stdout+stderr, pattern-match for common signatures (`trace-matrix.yml not found` → "run `/trace-matrix init` first"; skill missing → "run `/sync-skills pull`"), and redirect with a `build_error` query string that both the index and view templates render as a warning banner with the full captured output. The previous behavior — unconditional redirect — made a failed build look like a successful one until the user noticed the page was still empty.
  Discovered by Ben on PCCP task ben/054 clicking the Build button before running `/trace-matrix init`.
  **Post-update:** Run `/project-console sync` to note the version bump (no scaffold file changes). Restart the console via `/project-console start` to pick up the new router + loader + templates (uvicorn `--reload` doesn't watch the skill package).
- 1.2.0 (2026-04-15): **Config-driven launch + macOS venv hygiene.** `run.sh` now reads `server.host` + `server.port` from `console.yaml` (falls back to `127.0.0.1:8765`) instead of hardcoding `--host 127.0.0.1 --port 8765`. This matches what `start.sh` already did — they share the same awk block now. `scaffold.py init` gains a `--port N` flag (default `8765`) so Claude can ask the user to confirm the default before scaffolding, which prevents silently colliding with an already-running console on the same box. `run.sh` also strips macOS Finder junk (`Icon\r` custom-folder-icon files, AppleDouble `._*` resource forks) from `.venv/` on every launch — on at least one machine these had leaked into `site-packages/jsonschema_specifications/schemas/` and crashed `jsonschema.iterdir()` at import time with `NotADirectoryError: 'Icon\r'`. Skill `.gitignore` extended to exclude `Icon?`, `._*`, `.DS_Store` so the junk can't be committed upstream through `sync-skills push`. SKILL.md `init` action updated to require port confirmation (check `lsof -ti tcp:8765`; suggest next free port if occupied); `run` action documents the new config-driven launch and the venv cleanup step. Discovered while installing this skill on Arthrex PCCP where a PDLC_DEMO console was already holding `:8765` and the arthrex venv had 311 stray `Icon\r` files inherited from a previous `uv sync`.
  **Post-update:** Run `/project-console sync` to regenerate `tools/project-console/run.sh` from the new template. Existing `console.yaml` files already contain a `server.port` field, so no migration is needed. Next launch of `run.sh` / `start.sh` reads the config value. If the console is currently running on a hardcoded port, restart it via `/project-console start` to pick up the new behavior.
- 1.1.0 (2026-04-15): **New `start` action — idempotent launcher.** Adds `start.sh` to the scaffold alongside `run.sh`. `start` detects any process already listening on the configured port (`server.port` from `console.yaml`, fallback `8765`), stops it (SIGTERM, then SIGKILL on stragglers), and execs `run.sh`. Use this after pulling skill updates (`uvicorn --reload` does not watch the skill package), after a crashed session left a stale listener, or any time you want "start or restart" as a single command. `run` stays as the fail-fast launcher. Also adds `start.sh` to `PROJECT_OWNED` set and to the `sync` action's tracked file list so the scaffold upgrade path installs it into existing projects. **Post-update**: run `/project-console sync` to install `start.sh` into any existing `tools/project-console/` directory.
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
