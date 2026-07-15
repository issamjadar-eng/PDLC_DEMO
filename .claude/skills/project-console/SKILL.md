---
name: project-console
description: Scaffold and maintain a local FastAPI project console (agents, documents, dashboards) for a medtech-docs project. Provides `init`, `sync`, `theme`, `run`, `start`, and `status` actions. Use when a user asks to "set up project console", "install the console tool", "scaffold a console", "update project console", "start the console", "restart the console", "scrape a company site for a theme pack", or reports a problem with `tools/project-console/`.
version: 1.38.0
updated: 2026-07-15
---

# Project Console

A reusable FastAPI-based local console for medtech-docs projects. Ships:

- A FastAPI app (`console/`) with routes for landing, agents chat, documents explorer, dashboards discovery, trace-matrix, gap-analysis, **strategy** (topline review surface), **submission** (FDA submission-package viewer + Ask-the-advisor), and **setup** (project-settings surface: connectors, skills, agents, plugins, rules & hooks, team & security)
- A **grouped template library** materialized into the project on init: a `core-team` group of 10 common medtech personas (regulatory, clinical, quality, systems, risk, human factors, R&D, V&V, cybersecurity, post-market) plus two advisory panels, and a `red-team` group — an adversarial buyer committee (CEO, CFO, CTO, VP Eng, RA VP, QA VP, PMO skeptics + a panel) for pressure-testing outward-facing documents. Each `agents/templates/<group>/` directory materializes into `agents/<group>/`
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
   Agent templates materialize **by group**: each `agents/templates/<group>/` directory
   (e.g. `core-team`, `red-team`) is copied into `agents/<group>/`, **skip-if-exists**, and a
   per-file baseline SHA is recorded in the manifest's `agent_templates` map (so a later `sync`
   can tell a pristine copy from a customized one). A flat `*.md` directly under `templates/`
   is treated as `core-team` (the original single-group layout).
4. Report what was created and the next steps printed by the scaffolder, including the configured port.
5. Remind the user they can run `/project-console theme <url>` to build a branded theme pack. The port can be changed later by editing `tools/project-console/console.yaml` `server.port` — both `run.sh` and `start.sh` read it at launch.

### `sync [--apply-agent-updates]`
Roll forward the scaffolded tool to match the currently-installed skill version. Use after `/sync-skills pull` brings a newer `project-console` skill.

1. Run:
   ```bash
   uv run python .claude/skills/project-console/scripts/scaffold.py sync
   ```
2. Report which skill-owned files were updated (`run.sh`, `start.sh`).
3. **Agent templates are handled idempotently and never clobber a project file** — the project owns its roster (`agents/` is project-owned). Sync sorts each template into one of four buckets and **guides** the user:
   - **New** (a template/whole group the project lacks, e.g. `red-team/`) → materialized automatically; reported as "Added".
   - **Update available** (the project's copy is byte-identical to the baseline recorded at materialize time, but the template advanced upstream) → **reported, not applied**. The copy is provably unmodified, so it's safe to update — re-run `sync --apply-agent-updates` to overwrite just those files (it never touches a customized one), or copy the template manually.
   - **Review drift** (the project's copy differs from both the current template and any recorded baseline — i.e. customized, or a pre-baseline legacy install) → **reported only, never overwritten**. The user merges manually if they want the upstream change.
   - **In sync** → silent.
4. This is how an upstream agent fix (e.g. a corrected grounding glob) or a new group reaches existing projects: the fix lands in the template; `sync` surfaces it as "update available" (auto-applied only with the explicit flag) so customizations are always preserved.
5. If the scaffolder reports drift in skill-owned files not declared in `tools/project-console/README.md`'s `## Customizations` section, surface the drift to the user and ask before overwriting.

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

Default slug (when `--name` is omitted) is derived from the hostname — strip the leading `www.` and the TLD, then lowercase (e.g., `www.example.com` → `example`).

#### Logo Selection Heuristics

The console topnav constrains logos to `height: 28px; max-width: 160px; object-fit: contain` — the image is resized to fit without stretching. That means a tall square logo shrinks to ~28px wide (often unreadable) while a horizontal wordmark scales cleanly. **Prefer horizontal wordmarks.**

When scraping, look in this priority order and stop at the first viable hit:

1. **`<header>` or topnav `<img>`** — whatever the live site renders in its own top bar. This is almost always the authoritative brand logo at a header-friendly aspect ratio.
2. **`<link rel="icon">` or SVG favicon** — fall back if no header `<img>` found. Square, but usually high-resolution.
3. **`/brand/`, `/press/`, `/media-kit/` paths** — many companies publish logo assets at these URLs. Try `og:logo` / `og:image` meta tags first.
4. **Open Graph `og:image`** — often a hero image, not a logo. Only accept if nothing else is available and annotate it `[VERIFY] og:image fallback — may not be a logo`.

**Format priority:** SVG > PNG with transparency > PNG > JPG. SVGs scale losslessly and play nicely with both light and dark topnavs.

**Light/dark variants:** if the scraped site's header is dark, also look for a white-on-transparent logo variant (common filenames: `logo-white.svg`, `Logo_White_RGB.png`, `logo-reversed.svg`). Save as `logo.png` (primary, matches the active topnav) and `logo-dark.png` (optional secondary).

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
    metrics/                  # topline Metrics section — generic consumer of the
                              #   usage-metrics skill's tools/usage-metrics/usage.json
    strategy/                 # topline Strategy section (reuses workflows/ B3 machinery)
    submission/               # topline Submission section — loader + router (reads
                              #   submissions-skill JSON sidecars; renders doc bodies inline)
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
    templates/                # grouped agent template library (materialized into project on init)
      <flat *.md>             #   → core-team group (10 medtech personas + panels; legacy flat layout)
      red-team/               #   → red-team group (7 buyer-committee skeptics + panel + _group.md)
  scripts/
    scaffold.py               # init / sync / status implementation
```

The `console/` package is imported by the project's `run.sh` via `PYTHONPATH` injection — there is no install step, no `uv add`, no separate publishing. A `/sync-skills pull` that updates `.claude/skills/project-console/` is immediately effective on the next launch.

## Trace-matrix drift overlay (read-side data contract)

The trace-matrix view in the console renders an optional drift overlay when a
sibling `drift.json` is colocated with any of the trace-matrix sources. The
console is a generic consumer — it knows nothing about how the drift was
computed; it only reads the JSON contract.

**Discovery rule:** for each `source_files[]` path declared by the
trace-matrix skill in the JSON sidecar, the console checks whether
`<same-dir>/drift.json` exists. Each unique `drift.json` is loaded once,
violations are grouped by `item_id`, and the worst severity per item is
computed (rank: `error > warning > info`). Multiple drift files merge their
summaries.

**`drift.json` contract** (project-agnostic — any producer can emit this):

```json
{
  "summary": {
    "violations_total": 16,
    "by_severity": { "error": 0, "warning": 0, "info": 16 },
    "by_category": { "A": 0, "B": 0, "C": 16 },
    "by_rule":     { "A1": 0, "...": 0, "C2": 13, "C5": 3 }
  },
  "violations": [
    {
      "rule": "C2",
      "severity": "info",
      "item_id": "<row id matching trace-matrix item.id>",
      "item_kind": "epic",
      "message": "human-readable description of the drift",
      "resolution_hint": "what to do about it",
      "references": { "<key>": "<value-or-url>" }
    }
  ]
}
```

**What the overlay renders:**
- Per-DHF KPI bar (totals + by-severity + by-category badges + source list).
- Per-row severity badge (`✗`/`⚠`/`ℹ` + count) on the trace-matrix table.
- Click-row drawer listing every violation with rule, severity, message,
  resolution hint, and references (URLs auto-linked).
- A "Drift only" filter chip beside the existing "Orphans only" toggle.

**The first concrete producer is `jira-pull`'s `audit` action**, which writes
`drift.json` under `_jira/<arch>/<version>/` next to the mirror tables. Any
other skill that emits the same JSON shape next to a trace-matrix source
gets the overlay automatically — no console changes required.

## Topline sections: Strategy & Submission

Two first-class top-nav sections sit right after Overview:

- **Strategy** (`/strategy`) — the program's per-domain strategy review surface
  (proposed-change callouts, Accept/Reject/Modify, advisor drawer). It reuses the
  `console/workflows/` B3 machinery in place; the former workflow card was removed
  and `/workflows/strategy-reassembly` now redirects to `/strategy`. Nav shows
  when `docs/project/strategies/*-strategy.md` exist.
- **Submission** (`/submission`) — an FDA submission-package viewer (Q-Sub / 510(k)
  / PCCP) with composition manifest, an inline tabbed document viewer, an FDA-
  questions panel, and an Ask-the-advisor drawer (defaults to `regulatory-affairs`).

The Submission section is a **generic consumer** of the `submissions` skill's JSON
contract (`schema_version: 1.0`) — same loose-coupling rule as the gap-analysis /
trace-matrix sidecars. It reads:

- `docs/project/submissions/.console/submission-index.json` (roll-up of filings)
- `docs/project/submissions/<filing>/<filing>.submission.json` (per-filing detail)

If the sidecars are absent the section degrades to an empty state with a hint to
run `/submissions render`; a `POST /submission/render` button shells to the skill's
`render_sidecars.py`. Document *bodies* are rendered inline via the documents
renderer using the repo-relative paths in the sidecar. The full contract lives in
the `submissions` skill SKILL.md.

## Topline section: Setup (project settings)

**Setup** (`/setup`) — the project-settings surface. Always visible in the
topnav. A settings shell (inner sidebar + content pane) with six sections:

| Section | Sources | Writable? |
|---|---|---|
| **Connectors** | `.mcp.json` × `security.approved_mcps` × catalog; plus a read-only **Command-line tooling** panel (git/gh presence, version, `gh auth status`, origin remote — detection + copy-paste fix commands only; the console never installs or runs interactive auth) | Yes (the original MCP config editor — see below) |
| **Skills** | `.claude/skills/*/` (SKILL.md frontmatter + VERSION) × `security.approved_skills`; `registries[].type: builtin` marks built-ins | Read-only |
| **Agents** | Both surfaces: `.claude/agents/*.md` (registered top-level; symlink target → owning skill) AND `.claude/skills/*/agents/*.md` (bundled skill-internal workers) × `security.approved_agents` (matched on final path segment). Bundled agents inherit approval from their owning skill in `approved_skills`; explicit listing still honored | Read-only |
| **Plugins** | `security.approved_plugins` (allowlist only — installs live outside the repo) | Read-only |
| **Automation** | `.claude/rules/*.md` (session rules) + `.claude/settings.json` `hooks` + `.github/workflows/*.yml` (GitHub Actions — name, triggers parsed from `on:`, jobs, and the owning skill resolved by filename mention in skill trees) | Read-only |
| **Registries** | `project.yml` `registries[]` + the registry catalog, sourced **GitHub-direct** by preference: a **Refresh from GitHub** button fetches the catalog via `gh` (`console/setup/registry_remote.py` — one git-trees call + minimal blob fetches; read-only repo access suffices, no clone or sync tooling required) and caches it at `.state/registry-catalog-<name>.json`; the local clone (`local_path`) is the fallback before the first fetch. Statuses recomputed per request against the live local install: not-installed / update (registry strictly newer) / current / local-ahead (push candidate — never a downgrade button) | Yes — Add/Update installs from the local clone when present, else downloads the registry **tarball from GitHub** and extracts just that skill (safe tarfile data filter); either way the skill is allowlisted in `approved_skills` in lockstep, updates are strictly-newer-only with a whole-dir backup under `.data/setup-backups/`. Reconciliation of diverged skills stays with the registry sync tooling |
| **Environment** (shown only when the project has a root `setup.sh`) | `setup.sh` (the project's machine bootstrapper), `setup.md`/`SETUP.md` guide, `.state/setup-check.json` (cached check report), `.state/setup-last-run.txt` (full-run stamp, when the project's script writes one) | Partial — a **Run check** button executes the script's own read-only `--check` mode server-side (`console/setup/envcheck.py`, 300s timeout), parses the `[OK]/[WARN]/[ERROR]` output into a grouped report and caches it; a staleness banner appears when `setup.sh` changed after the last check. The **full install never runs from the browser** — the section shows the terminal command (`bash setup.sh`) and points at the guide for manual steps |
| **Team & Security** | `project.yml` `team.*`, `security.*` | Yes — roster edits. **Add member** appends to `team.active` (name / github / task_folder / role / email + today's `added:`; email domain validated against `security.approved_email_domains`, github + task_folder uniqueness enforced). **Deactivate** moves the member's block to `team.inactive` with `removed:` (today) + a required `reason:`. Surgical comment-preserving line edits (never a yaml.dump round-trip), backup + audit + re-parse-validate-or-restore like every writer path. Roster of record only — GitHub repo access is granted/revoked in GitHub; the posture check cross-references the two. Re-activating a former member stays a manual edit (one history row per person) |

Skills/agents/rules/plugins sections are deliberately read-only: those are
managed by the registry sync tooling, and duplicating that merge logic behind
a browser button would fork it. Each read-only section reuses the connectors'
installed-vs-approved status triad (ok / warning "not in allowlist" / info
"approved, not installed") so the security-posture semantics are identical
across the whole tool surface. All loaders are defensive — a missing or
malformed file degrades to an empty section plus a surfaced warning.

### Connectors (the writable section)

Merges three sources into one per-connector status model:

- `.mcp.json` `mcpServers` — server definitions (transport, command/args or url,
  env **keys** — values are always masked and never editable from the browser)
- `project.yml` `security.approved_mcps` — the team's security allowlist
- a skill-shipped, company-agnostic catalog (`console/setup/catalog.py`) of
  connectors the console can configure, plus custom stdio / HTTP forms

Status per connector: configured + approved → OK; configured but unapproved →
warning (the security posture check would flag it); approved but not defined →
"approved, not installed". Stdio launch commands get a cheap existence probe
(repo-relative path stat / `shutil.which`) — advisory only; the console never
launches servers.

**Write path** (all writes via `console/setup/writer.py`):

- Add/update a connector writes `.mcp.json` **and** ensures the name is in
  `project.yml security.approved_mcps` in the same operation — installs and the
  allowlist move in lockstep.
- `project.yml` is edited with **surgical line inserts/removals** inside the
  `approved_mcps:` block (never a yaml round-trip, which would destroy the
  file's comments); the file is re-parsed after every edit and restored on
  validation failure.
- Every write takes a timestamped backup under
  `tools/project-console/.data/setup-backups/` and appends to
  `.data/setup-audit.log`.
- Removing a connector deliberately leaves its allowlist row (removal ≠
  un-approval); the UI surfaces the resulting "approved, not installed" state.

The console edits configuration only — Claude Code owns the MCP server
lifecycle, so the UI banners that changes take effect at the next session
start (or `/mcp` → Reconnect).

## Theme tokens (theme.yaml fields)

A theme pack's `theme.yaml` may set any subset of the following keys; each maps to a CSS variable injected into a `<style id="theme-overrides">` block at the top of every page. Unset keys fall through to the defaults in `console.css` `:root`.

| `theme.yaml` key | CSS var | Purpose |
|---|---|---|
| `primary` | `--brand-primary` | Brand accent — link color, active filter chip, primary buttons |
| `primary_dark` | `--brand-primary-dark` | Hover state for primary |
| `primary_tint` | `--brand-primary-tint` | Soft fill — `.pc-msg-user` chat bubble bg |
| `accent` | `--brand-accent` | Secondary accent (info badges, citation links) |
| `topnav_bg` / `topnav_text` | `--topnav-bg` / `--topnav-text` | Topnav surface + text |
| `body_bg` / `text` / `text_muted` | `--body-bg` / `--body-text` / `--body-text-muted` | Page bg + body copy + secondary text |
| `border` | `--border` | Default border color for cards, panels, separators |
| `font_body` / `font_heading` | `--font-body` / `--font-heading` | Type stack |
| `logo_filter` | `--logo-filter` | CSS `filter` applied to `.brand-logo`. Set to `invert(1) brightness(1.05)` for dark themes when only a dark-on-transparent logo asset is available |
| `surface` | `--surface` | Primary card / panel / drawer fill (light themes: `#ffffff`; dark themes: e.g. slate-800) |
| `surface_2` | `--surface-2` | Slightly lifted surface — table headers, toolbars, hover states |
| `surface_muted` | `--surface-muted` | Recessed surface — assistant message bubble, input wells |
| `code_bg` / `code_text` | `--code-bg` / `--code-text` | Inline code + `<pre>` blocks |
| `banner_warning_bg` / `banner_warning_text` | `--banner-warning-bg` / `--banner-warning-text` | `.pc-msg-warning` and similar soft-warning panels |
| `footer_bg` / `footer_text` / `footer_heading` / `footer_muted` / `footer_divider` | `--footer-*` | Site footer pill — decoupled from `--body-text` so dark themes can keep the footer visually grounded (e.g. slate-900 below a slate-950 body) instead of inheriting light-on-light or dark-on-dark |
| `icon_folder` | `--icon-folder` | Color of the folder glyph in the docs explorer tree. Defaults to amber so folders pop against either light or dark surfaces |
| `badge_bg` / `badge_text` | `--badge-bg` / `--badge-text` | Pill background + text for `.badge` (agents page "Panel · N members" and similar). Decoupled from primary so themes can hit a high-contrast pair without having to bend the brand palette |

### Theme inheritance (`extends:`)

A theme pack may declare `extends: <theme-name>` at the top of its `theme.yaml` to inherit every key from a named parent and override only the keys it cares about. The resolver looks up the parent the same way it looks up any theme — project `themes_dir/<name>/` first, then skill `themes/<name>/`. Inheritance is shallow (every theme value is a scalar; child wins on conflict) and recursive (the parent itself may extend another theme; cycles raise `ValueError`).

```yaml
# tools/project-console/themes/<your-pack>/theme.yaml
extends: dark            # inherit slate+sky palette + all semantic tokens

name: My Project Dark
brand_name: My Project
tagline: "..."
logo_filter: "invert(1)"  # if your stock logo is dark-on-transparent
accent: "#f59e0b"          # optional: override only this token
```

**Adding a new project theme pack:** start with `extends: dark` and override only `brand_name`, `tagline`, and `logo_filter`. Add color overrides only when the brand differs from the slate+sky default.

## Inline action buttons in markdown content

Markdown rendered inside the console (submission tracker, dashboards, any doc-explorer page) can embed inline buttons for row-level actions without inline styles. The console ships theme-aware styling for one shared class:

| Class | Purpose | Example |
|-------|---------|---------|
| `tracker-action-btn` | Inline placeholder/action button — typically used in tracker tables for row-level CTAs (e.g., "Create Draft", "Open Worktree"). Theme-aware (derives all colors from `--brand-*` / `--gl-*` tokens). Honors the standard HTML `disabled` attribute. | `<button class="tracker-action-btn" disabled>Create Draft</button>` |

**Scope:** the skill provides styling only. Click handlers (slash-command dispatch, worktree creation, draft scaffolding) are intentionally **not implemented** — projects wire those up themselves when ready. Until then, mark buttons `disabled` to make the deferred state visible to readers.

## Best Practices
See [README.md](README.md) — consumed by `/best-practices` audit.

## Changelog
See [README.md](README.md) for version history.

