---
name: project-console
description: Scaffold and maintain a local FastAPI project console (agents, documents, dashboards) for a medtech-docs project. Provides `init`, `sync`, `theme`, `run`, `start`, and `status` actions. Use when a user asks to "set up project console", "install the console tool", "scaffold a console", "update project console", "start the console", "restart the console", "scrape a company site for a theme pack", or reports a problem with `tools/project-console/`.
version: 1.66.0
updated: 2026-09-08
---

# Project Console

A reusable FastAPI-based local console for medtech-docs projects. Ships:

- A FastAPI app (`console/`) with routes for landing, agents chat, documents explorer, dashboards discovery, trace-matrix, gap-analysis, **business domains** (`/domains/<slug>` — Commercial, Finance, Manufacturing, … one tab per discovered `docs/project/<slug>/.console/<slug>-index.json` published by the `commercial` skill engine; `/commercial` redirects), **journey** (project standup + device program, evaluated from a skill-owned map), **document pipeline** (how documentation moves, derived live across four lanes), **strategy** (landing index + per-domain review surface), **submission** (FDA submission-package viewer + Ask-the-advisor), **setup** (project-settings surface: connectors, skills, agents, plugins, rules & hooks, team & security), and **tasks** (activity summary from the task skill's derived JSON)
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
    journey/                  # topline Journey section — evaluates a SKILL-OWNED map
                              #   (medtech-docs/registry/journey.yaml); authors nothing
    doc_pipeline/             # topline Document Pipeline section — live projection of
                              #   every owning skill's artifacts across four lanes
    mdlite.py                 # shared display-only markdown helpers (md_to_html,
                              #   md_inline) for views that render one-liners
    strategy/                 # topline Strategy section — landing index (loader.py)
                              #   + per-domain detail (reuses workflows/ B3 machinery)
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

- **Strategy** — split into a landing index and a per-domain review surface:
  - `/strategy` — roll-up (domains live · decisions · proposed changes ·
    awaiting content) plus one card per domain. Backed by
    `console/strategy/loader.py`, which **counts without rendering**: it
    aggregates the parsers already in `console/workflows/b3_strategy_reassembly`
    (`scan`, `parse_decisions`, `_parse_proposals`, `_parse_history`) rather
    than adding a second parser.
  - `/strategy/{slug}` — the review surface (proposed-change callouts,
    Accept/Reject/Modify, advisor drawer), opened on that domain via
    `active_slug`. It reuses the `console/workflows/` B3 machinery in place and
    still renders every domain's pane, because the panes carry a cross-domain
    "move to another domain" selector and the tab JS expects them all in the DOM.
  - `?domain=<slug>` redirects to the detail route; an unknown slug redirects to
    the index; `/workflows/strategy-reassembly` still redirects to `/strategy`.
    Nav shows when `docs/project/strategies/*-strategy.md` exist.

  **Two decision formats coexist and must never be summed.** Structured
  `<!-- DECISION:start … -->` blocks carry a lifecycle `status=`; legacy
  `**Decision**:` prose does not — and the sentinels **wrap** the prose rather
  than replacing it, so summing double-counts a migrated document. The rule is
  `structured if any, else prose`, and each card labels which format it counted.
  A prose-format document therefore shows a decision count with **no** lifecycle
  bar: those documents genuinely record no per-decision status, and drawing one
  would invent a fact the document does not state.
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

## Topline section: Commercial (business questions answered with data)

**Commercial** (`/commercial`) — the display tier of the corpus → commercial → console
stack. Nav shows when the `commercial` skill has published
`docs/project/commercial/.console/commercial-index.json` (`schema_version: 1.0`).

The console is a **pure consumer** of that sidecar (same loose-coupling rule as
Submission/Tasks): it plots each edition's `data.json` series verbatim and computes
nothing — figures exist only because the skill's deterministic computation emitted and
claim-linted them. The catalog page renders every question (unimplemented ones as
"Planned" — roadmap, never silence); the answer view renders the verdict banner,
in-console bar charts with per-series evidence badges (measured / derived / assumed /
no-data, icon + label) and provenance lines linking pinned `dataset@snapshot`, a
**DRAFT — NOT APPROVED watermark** over unapproved editions, the pinned-snapshots +
approval-record panel, edition history (`?edition=`), and the full marker-cited report
via the documents renderer. Commercial-skill v2 extensions render as first-class
panels: **Assumptions & expectations** (plan vs actual, met/not-met verdicts, an
`unvalidated` chip on stand-in expectations), **Narrative** (Risks / Mitigations /
Issues with severity + evidence), and **timeseries line charts** (`kind: timeseries`
series; server-computed SVG geometry — pixels, never data), plus a newer-draft banner
on approved answers. Sidecar schema 1.2's per-question `code` block (the commercial
skill's code-quality layer) renders as a **Computation code** panel on the Quality &
audit tab — per-artifact role/path/hash rows, static-lint / poison-scan / determinism
chips, review verdict + findings folds, and SOFT-GATE badges (checks failed / review
outdated / unreviewed — badges only, nothing blocks) plus a compact question-level
code chip on the tab header; rows without the field (schema ≤1.1) degrade to an honest
empty state. Sidecar schema 1.3 adds per-artifact `review_history` — reviews filed
against earlier, now-superseded hashes of the same file — rendered as expandable
**Previous review** folds (verdict + date + superseded-sha pill + findings table);
rows without it (schema ≤1.2) degrade to no history chrome. Any repo-relative
markdown `detail_ref` (reviews, history entries, verification records) additionally
renders as an in-place **Full review dossier** fold, lazy-loaded on first expand via
`GET /commercial/review-detail?path=…` (documents-renderer HTML fragment, client-side
cached, scrolling body) — the endpoint resolves paths strictly inside the repo root
and serves only `.md` files (traversal / absolute / non-markdown → 403/404); the
Documents-viewer link stays as a secondary affordance. Sidecar schema 1.4 adds a
per-question `verification_plan` — the plan's declared gate checklist with
engine-COMPUTED done-marks — rendered on the **Plan tab** as a checklist (✓ done /
○ not done / • informational for custom gates, evidence line per gate; marks are
rendered verbatim, the console never re-derives them — the plan's literal `[ ]`
checkboxes are never hand-ticked) plus a compact "verification N/M" chip next to the
lint + code chips on the Quality & audit tab header; rows without the field
(schema ≤1.3) render no chip and no checklist, zero errors. `POST /commercial/render`
shells to the skill's `render`; the assistant drawer grounds in
`/commercial/{bq}/grounding`. Full contract lives in the `commercial` skill's
SKILL.md.

## Topline section: Journey (where the project stands)

**Journey** (`/journey`) — two phase paths with live artifact probes: **Project
standup** (empty clone → scaffolded DHF, titles parsed from
`new-project-bootstrap.md`) and **Device program** (the regulatory milestone
sequence, expanded from `docs/project/milestones/regulatory.yml`).

**The map is owned by a skill, not by the console.** Phase predicates,
`requires` edges, producer commands, `levels`, `derivations` and a binding
`rendering:` block are authored at
`.claude/skills/medtech-docs/registry/journey.yaml`. The console evaluates the
authored predicates; a hardcoded phase table in the loader would make it the
author of the semantics it renders. **Add or change a phase by editing the
yaml, never the loader.** Predicate vocabulary: `all_exist`, `any_exist`,
`yaml_nonempty`, `file_contains`, `derived` (ANDed when a phase declares more
than one).

Four contracts this section holds, each of which has already prevented a wrong
render — do not relax them:

| Contract | Why |
|---|---|
| **Artifact language, never completion language** (`rendering.language`) | States read *artifacts present / partly present / next up / blocked / in the loop / evidence in motion*. No "complete", no "done", no bare ✓ anywhere in the page, the CSS or the grounding text. Every predicate detects a file, never its quality — and in a regulated project a checkmark against a DHF artifact is a claim someone may be asked to substantiate. |
| **Inverted discovery** (`rendering.always_discoverable`) | `discover()` returns true whenever the **map** exists, not when a producer artifact does. Every other section lights only once its data lands; a journey tab that hides while the project is immature hides exactly when it is needed. |
| **Milestones are gauges, never checkboxes** (`state_model: evidence-gauge`) | A regulatory milestone completes when a package is filed and a regulator responds — unobservable from the repo. Milestones render in-motion / next-up / blocked and never "present". Without this, four milestones each holding a few drafting rows all read "artifacts present", i.e. the whole device program read as finished. |
| **Consume `/tracker`; never re-derive readiness** | Milestone evidence comes from the tracker's **published** artifacts — `submission-tracker.row-source.json` for row attribution, `submission-tracker.overlay.yml` for recorded status (the tracker's durable, curated home). The tracker's markdown is deliberately **not** parsed: the tracker merges markdown with the overlay at render time and the overlay wins, so a second parse would disagree with the dashboard the team reads. No readiness verdict is emitted — that belongs to `/tracker assess`. |

Routes: `/journey`, `/journey/data.json`, `/journey/grounding` (plain text for
the assistant drawer). **No mutation or refresh endpoint by design** — every
probe is a `stat()` against repo truth (2s TTL), and advancing a phase is a
skill action the user runs in their own session.

## Topline section: Document Pipeline (how documentation moves)

**Document Pipeline** (`/doc-pipeline`) — the documentation flow rendered live.
Nav shows when `docs/README.md` exists. Every figure is derived at request time
(15s TTL); the console authors no data. Four lanes:

1. **Authoring** — seven ordered stage cards: input analysis → strategies →
   design controls → trace → obligations → gap analysis → submission, each read
   from its owning skill's artifact and each degrading to a producer-command
   hint when absent.
2. **Ingestion** — `docs/internal/source/` binaries vs `source-md/` markdown vs
   `docs/external/` distilled references, plus a genuine `docflow:`
   conversion-provenance count.
3. **Regulated publish** — the `change-control` 5-state lifecycle
   (`draft → published → review-formal → frozen → released`), read from
   `docs/.change-control/state.json` or `state:` frontmatter. Built
   contract-first: it renders an honest empty state until the first document is
   adopted or published.
4. **Terms & information flow** — terms projected live from `glossary.md`, and
   the External → Project ← Internal model parsed from `CLAUDE.md § Information
   Flow`. Both files stay canonical; this is a view, never a copy.

Two places where the obvious read is the wrong read — both are load-bearing:

- **Obligation coverage is not computed from the manifest's `status`/`location`
  fields.** `dhf-manifest` v7 removed both and moved coverage to
  `/tracker assess` exclusively. A pre-v7 manifest still carries them with every
  entry reading `GAP`, which looks like a 0%-coverage dataset and is retired
  schema. The stage reports catalogued counts, flags the stale schema, and
  points coverage at the tracker.
- **A large `source-md/` corpus is not evidence that `source/` was converted.**
  When no document carries `docflow:` provenance, the lane says the markdown was
  *authored*, not converted — rather than printing a conversion ratio that would
  invent a pipeline that never ran.

Routes: `/doc-pipeline`, `/doc-pipeline/data.json`, `/doc-pipeline/grounding`.
No mutation or refresh endpoint — the console is a router, the skill is the actor.

## Topline section: Tasks (activity summary)

**Tasks** (`/tasks`) — an *activity summary*, deliberately not a task list: what's
moving, what's open (categorized cards with the index's curated one-liners), a
recently-shipped timeline, and an effort-picture footnote. Nav shows when
`tasks/task-summary.json` exists.

The console is a **pure consumer** of the `task` skill's `/task summary`
artifact (same loose-coupling rule as the submission/gap-analysis sidecars):

- `tasks/task-summary.json` — counts, `open_tasks[]`, `categories`,
  `category_icons` (project-tunable via `tasks/task-summary-config.json`,
  owned by the task skill), `recent{}` window with `highlights[]`,
  `economics{}` rollup, plus Claude-composed `narrative` / `watch` prose.
- The page shows the `generated` stamp's age (fresh ≤ 7 d, aging ≤ 21 d,
  stale beyond) with a "regenerate with `/task summary`" hint; missing file →
  empty state with the same hint. `GET /tasks/summary.json` exposes the raw
  artifact.
- Task-doc deep links render via the documents explorer
  (`/documents/view/tasks/...` — `tasks` is a documents-tree root).
- Category icons come from the artifact; the console holds no project
  vocabulary of its own (fallback icon only).

## Topline section: Setup (project settings)

**Setup** (`/setup`) — the project-settings surface. Always visible in the
topnav. A settings shell (inner sidebar + content pane) with these sections:

| Section | Sources | Writable? |
|---|---|---|
| **Project** | `project.yml` `project:` block (identity + classification fields) + an inventory of every other top-level section. Field/section descriptions ship with the skill (`console/setup/project_meta.py`) so all consuming projects render the same explanations; a field the catalog doesn't know renders with a "no description" badge — the signal to add it to the catalog | Partial — single-line scalar `project.*` fields get an inline edit (`writer.set_project_field`: surgical comment-preserving line replacement, backup + audit + re-parse-validate-restore; structured values and new fields stay with project.yml / their owning tooling) |
| **Connectors** | `.mcp.json` × `security.approved_mcps` × catalog; plus a read-only **Command-line tooling** panel (git/gh presence, version, `gh auth status`, origin remote — detection + copy-paste fix commands only; the console never installs or runs interactive auth) | Yes (the original MCP config editor — see below) |
| **Skills** | `.claude/skills/*/` (SKILL.md frontmatter + VERSION) × `security.approved_skills`; `registries[].type: builtin` marks built-ins | Read-only |
| **Agents** | Both surfaces: `.claude/agents/*.md` (registered top-level; symlink target → owning skill) AND `.claude/skills/*/agents/*.md` (bundled skill-internal workers) × `security.approved_agents` (matched on final path segment). Bundled agents inherit approval from their owning skill in `approved_skills`; explicit listing still honored | Read-only |
| **Plugins** | `security.approved_plugins` (allowlist only — installs live outside the repo) | Read-only |
| **Automation** | `.claude/rules/*.md` (session rules) + `.claude/settings.json` `hooks` + `.github/workflows/*.yml` (GitHub Actions — name, triggers parsed from `on:`, jobs, and the owning skill resolved by filename mention in skill trees) | Read-only |
| **Registries** | `project.yml` `registries[]` + the registry catalog, sourced **GitHub-direct** by preference: a **Refresh from GitHub** button fetches the catalog via `gh` (`console/setup/registry_remote.py` — one git-trees call + minimal blob fetches; read-only repo access suffices, no clone or sync tooling required) and caches it at `.state/registry-catalog-<name>.json`; the local clone (`local_path`) is the fallback before the first fetch. Statuses recomputed per request against the live local install: not-installed / update (registry strictly newer) / current / local-ahead (push candidate — never a downgrade button) | Yes — Add/Update installs from the local clone when present, else downloads the registry **tarball from GitHub** and extracts just that skill (safe tarfile data filter); either way the skill is allowlisted in `approved_skills` in lockstep, updates are strictly-newer-only with a whole-dir backup under `.data/setup-backups/`. Reconciliation of diverged skills stays with the registry sync tooling |
| **Environment** (shown only when the project has a root `setup.sh`) | `setup.sh` (the project's machine bootstrapper), `setup.md`/`SETUP.md` guide, `.state/setup-check.json` (cached check report), `.state/setup-last-run.txt` (full-run stamp, when the project's script writes one) | Partial — a **Run check** button executes the script's own read-only `--check` mode server-side (`console/setup/envcheck.py`, 300s timeout), parses the `[OK]/[WARN]/[ERROR]` output into a grouped report and caches it; a staleness banner appears when `setup.sh` changed after the last check. The **full install never runs from the browser** — the section shows the terminal command (`bash setup.sh`) and points at the guide for manual steps |
| **Validation** (labeled "Validation" in the nav; shown only when the `workbench-validation` skill or its sidecar is present) | The workbench-validation skill's sidecar (`tools/workbench-validation/workbench-validation-index.json`, `schema_version: 1.0`) — role-based user-needs register with per-need verdicts, test-case results with per-case evidence-log links, config-baseline (git SHA, skills/hooks counts), links to the generated validation report + plan via the Documents tab (requires `tools/workbench-validation` in the project console.yaml `grounding.extra_roots`). A staleness banner appears when repo HEAD has moved past the recorded baseline. Pure consumer — the console computes nothing | Partial — a **Run validation** button executes the owning skill's `run_validation.py --render` server-side (`POST /setup/workbench/render`, 1800s timeout); a FAIL verdict is a valid reportable outcome, not an HTTP error. All authoring (plan, manifest, triage) stays with the `workbench-validation` skill |
| **Team & Security** | `project.yml` `team.*`, `security.*`; plus the **Repo access audit** — GitHub collaborators (`gh api`, on demand, cached at `.state/team-access-audit.json`) cross-referenced against the roster with permission-aware verdicts: rostered ok / unrostered read = observer / unrostered write = warning / inactive-with-access = error / active-without-access = warning; staleness flagged when project.yml changed after the audit. Report-only — access changes happen in GitHub | Yes — roster edits. **Add member** appends to `team.active` (name / github / task_folder / role / email + today's `added:`; email domain validated against `security.approved_email_domains`, github + task_folder uniqueness enforced). **Deactivate** moves the member's block to `team.inactive` with `removed:` (today) + a required `reason:`. Surgical comment-preserving line edits (never a yaml.dump round-trip), backup + audit + re-parse-validate-or-restore like every writer path. Roster of record only — GitHub repo access is granted/revoked in GitHub; the posture check cross-references the two. Re-activating a former member stays a manual edit (one history row per person) |

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

**Catalog curation contract.** A catalog row is not a suggestion — clicking
Configure writes `.mcp.json` *and* adds the name to `approved_mcps`, so the row
is effectively a pre-blessed allowlist entry. Three rules follow:

- **Vendor-official servers only.** Third-party or individual-authored servers
  are not catalogued even when they exist and work. A team that has vetted one
  adds it through the custom stdio / HTTP forms — the deliberate escape hatch
  that keeps it an explicit act with a named owner.
- **No invented endpoints.** Where a vendor's MCP is real but its endpoint is
  customer-gated, the entry ships an empty `url` plus a `url_placeholder` hint
  and a `note` naming where to obtain the real one. A guessed path is
  indistinguishable from a verified one once it is in `.mcp.json`.
- **Researched absence is catalogued, not omitted.** A tool with no vendor
  server carries `availability: "none"` and renders as an informational card
  (dimmed, "no vendor MCP" badge, no Configure button). An absent card is
  ambiguous; a card that says so is a dated answer.

Optional entry fields beyond the base shape: `note` (caveat line under the
description — instance-specific endpoints, licensing prerequisites, scope
limits), `url_placeholder`, and `availability` (`vendor` default | `none`).

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
| `category_colors` | _(not emitted by the console)_ | Ordered categorical ramp, comma-separated hex. See below |

### `category_colors` — the categorical ramp

A comma-separated list of hex colours a **consumer** assigns to a repeating dimension it renders. The console itself does not emit these as CSS variables; the `tracker` skill reads the same pack directly and uses them for milestone cards and phase badges.

The contract is deliberately two-part — the pack supplies the *palette*, the consumer decides what the entries *mean*:

- **The ramp is sequential**, running cool → warm, so an ordinal dimension (milestone 1, 2, 3 …) reads as progression rather than as arbitrary colour coding. Consumers assign entries in **document order**, not alphabetically.
- **The last entry is reserved** for a category that sits outside the ordering. Consumers must not assign it positionally. (The tracker gives it to Engineering Prereqs, a parallel workstream rather than a milestone.)
- Entries must clear WCAG AA 4.5:1 against both `surface` and `body_bg` — the ramp is used for large numerals and 4px card borders, but also for badge text.
- Keep it distinct from status colours. Status (approved / blocked / in flight) is a *different* dimension and must not drift when the palette changes.

Comma-separated rather than a YAML list because the consumers that read theme packs do so with line-based parsers and no YAML dependency.

### Pack assets and the footer — identity vs palette

A pack's `theme.yaml` carries the **palette**. Its optional files — `logo.png`, `favicon.ico`, `fonts/`, `footer.html.j2` — carry **project identity**. Those two travel differently:

- **Tokens** resolve through `extends:` (see below).
- **Assets and the footer do NOT.** `pack_dir` is the child's directory, so `/theme/assets/*` and the footer read from the active pack only.

Both therefore **fall back to the project default pack** when the active pack does not supply them. A viewer switching palette must not lose the project's logo, web font or copyright line — a personal colour choice is not a branding change. The bundled `light` / `dark` packs deliberately ship **no** assets and **no** footer for exactly this reason: they are palettes, so a project's own identity shows through under them.

A project whose packs contain no footer at all renders no footer element (not an empty bar). The footer template receives `theme` and `year` — use `{{ year }}` rather than hardcoding one; Jinja has no `now` global here.

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

