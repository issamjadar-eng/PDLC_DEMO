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
- Any demo-specific fields (`lead_product`, `portfolio_context`, `composition`, `capabilities`) — present in the demo project but absent in an adopting project
- Specific DHF counts or names
- Specific file paths under `docs/project/submissions/` — discovery is glob-pattern driven
- Any brand asset (logo, palette, font) — all brand state lives in project-owned theme packs

The contract was validated against both the demo project and an adopting project before v1 shipped.

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

Before any `project-console` skill update ships to the hitachi registry, a dry `init` must run successfully in both the demo project (the demo) and an adopting project (a real adjacent project). This enforces that the skill generalizes and catches demo-specific assumptions that might otherwise leak in.

## Why This Shape

The design evolved through several iterations during task 015 (see `tasks/ben/015-project-console-skill.md` for the full trail):

1. **Agent roster** — initially considered `docs/project/agents/`, settled on `tools/project-console/agents/` because personas are tool config, not DHF content. Skill ships templates; init materializes.
2. **Dashboard discovery** — initially a hard-coded dict, then considered a `dashboards.yml` sidecar, finally settled on glob scan + `console.yaml` overrides after observing that both the demo project (`*-tracker.html`) and an adopting project (`dashboard.html`, `*-tree.html`) use different file-name conventions.
3. **Python package shape** — rejected installable package in favor of `PYTHONPATH` injection so `/sync-skills pull` is immediately effective without a rebuild step.
4. **Theming** — initially shipped two example branded theme packs inside the skill, reverted after realizing "a reusable skill that knows its customers isn't reusable." Now the skill is company-agnostic; branding is a scrape-and-materialize user action.
5. **Config home** — rejected `project.yml` as the tool-config home in favor of `tools/project-console/console.yaml` for clean install/uninstall semantics and consistency with other per-tool configs.
6. **Drift management** — three ownership classes, extension-hook files as the happy path, declared drift via the tool README `## Customizations` section, narrow committed manifest.

## Future Work

- **sync drift detection** — current `scaffold.py sync` only rewrites `run.sh` when it diverges from the template. Full 3-way diff reconciliation against `console.css`, template files, etc., is not yet implemented.
- **theme scrape action** — the `SKILL.md` documents the action but `scaffold.py` doesn't yet implement the scraping pipeline. Intended to be driven by Claude via WebFetch rather than by the scaffold script directly.
- **Extension-hook surfaces** — `project_extensions.py` and `_project_overrides/` are documented but not yet loaded by `app.py`. Scheduled for v1.1.
- **Dark mode switching** — right now the theme is fixed at launch. A runtime toggle would be nice but requires cookies + render-time theme resolution.

## Markdown Rendering Conventions

The documents view (and chat assistant) renders markdown via `console/web/static/console.css`'s `.md-content` rule block. Two rendering decisions are load-bearing and should not drift:

1. **Tables size to content, not to the pane.** Tables use `display: block; width: max-content; max-width: 100%; overflow-x: auto` — the GitHub / VS Code pattern. Tables that fit naturally stay narrow; wide tables scroll horizontally rather than crushing column widths. Do **not** re-introduce `width: 100%` on `table` — combined with auto-layout it pushes 2-col tables to span the pane and lets short-label columns get squeezed when the same table contains a long-paragraph cell.
2. **Cells wrap at word boundaries.** Cell `<th>` / `<td>` use `word-break: normal; overflow-wrap: break-word` (browser default for prose). Character-level breaking (`overflow-wrap: anywhere`) is **scoped to `<code>` and `<a>` inside cells** — the only places where unbreakable tokens (URLs, paths, kebab IDs) appear and need it.

The CSS comment at `.md-content table` records the rationale.

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

- 1.12.0 (2026-05-04): **Trace-matrix UX overhaul — typed columns + chip-based click-through + group-row collapsing + two-axis disclosure.** Six coordinated changes that replace the previous one-size-fits-all row expansion + Forward/Reverse columns with a domain-aware typed-relation model and follow-the-trace navigation. (1) **ID column compaction** — caret + ID on line 1, badges (orphan + drift) on line 2; frees horizontal width for the new trace columns. (2) **Two-axis disclosure** — drift drawer pulled out of the row expansion into a popover anchored to the drift badge; clicking the row toggles only the requirement detail panel; clicking the badge toggles only the drift popover. Independent gestures, no coupling. (3) **Requirement detail panel restructure** — scrollable subsection cards (Full Text, Acceptance Criteria, Verification Method) with a collapsed "More metadata" disclosure for category/stakeholder/priority/status/IEC class/module; footer surfaces source-doc + Jira links. Cap height 240px; scrolls when content exceeds. (4) **Per-layer trace columns** — replaced the old single Forward/Reverse columns with per-layer-typed relation columns (e.g. DI shows `← UN`, `→ SW`, `→ V&V`, `↔ Risk`). Router pre-computes neighbour buckets per row using the sidecar's edges; template iterates `item.trace_cells`. Risk column carries an `ⓘ` tooltip noting "FMEA source not configured — showing HA only" because today's `_jira/<arch>/v1.0.0/hazards.md` is HA-only. (5) **Click-through navigation** — every neighbour renders as a `tm-trace-chip` button; clicking jumps to the target tab and scrolls + pulse-highlights the target row (no auto-expand). URL hash sync (`#tab=...&row=...`) so back-button works. Beyond 5 chips per cell, the rest collapse into a `+N` overflow chip that opens a popover. Breadcrumb path bar appears beneath the tab strip and persists across tab switches; clicking a breadcrumb truncates the path and re-jumps; `× clear path` chip empties it. (6) **Group-row collapsing** — items now bucketed into collapsible groups keyed by `group_label`; the standalone Group column is dropped. Group headers show `▾ <label> (N items, M with drift, K orphans)`. Filter chips replace "Expand/Collapse all rows" with "Expand/Collapse all groups". **Files touched:** `console/trace_matrix/router.py` (added `LAYER_TRACE_COLUMNS`, `_decorate_trace_columns`, `_build_groups`; new `violations_by_id` JSON island for the popover JS); `console/web/templates/trace_matrix_view.html` (full table-body rewrite, new singleton popover elements, JS rewrite covering popover positioning, chip click-through, breadcrumb path, URL hash sync, group toggle, filter composition with `tm-row-filtered-out`/`tm-row-group-collapsed` classes; new CSS section under `/* ═══ v1.12.0 trace-matrix UX overhaul ═══ */`). **Backward-compatible** — DHFs without violations or without group_labels render identically to before, just with the new column model. **Performance** — drift drawer no longer pre-rendered into hidden DOM; popover JS reads from a single JSON island and renders on demand.

- 1.10.0 (2026-05-04): **Trace-matrix drift overlay.** Added a generic drift overlay that renders alongside the trace-matrix view whenever a sibling `drift.json` is colocated with any of a DHF's trace-matrix source files. The console reads only the drift JSON shape (`summary`, `violations[]` with `rule`/`severity`/`item_id`/`message`/`resolution_hint`/`references`); it has no awareness of any specific drift producer. Renders: per-DHF KPI bar (totals + by-severity + by-category), per-row severity badges (`✗`/`⚠`/`ℹ` + count), click-row drawer listing every violation with rule + message + hint + auto-linked reference URLs, and a "Drift only" filter chip. **Files:** `console/trace_matrix/loader.py` (added `load_drift_overlay`, `_worst_severity`); `console/trace_matrix/router.py` (passes overlay into template context); `console/web/templates/trace_matrix_view.html` (KPI bar, badges, drawer, filter chip, CSS). Project-agnostic — any project that emits `drift.json` next to trace data picks up the overlay automatically. **Tests:** `tests/test_drift_overlay.py` (4 cases — severity ranking, no-drift fallback, single-file load, multi-file dedupe + summary merge).

- 1.9.0 (2026-05-01): **B3 strategy reassembly — single-button "Run Assembler" + Original/Diff tabs + per-callout review for edits.** Replaces the prior B3 UX (separate detection-pass button, manual `/strategy assemble` from Claude Code, single static doc preview) with a one-button flow plus a tabbed Original / Diff view of the strategy document. After Run Assembler, the Diff tab appears with **Save & Publish** and **Throw Away** controls; the existing **Awaiting your review** section continues to surface per-callout Accept / Reject / Modify cards. Two layers of control: whole-doc Save & Publish / Throw Away at the Diff tab; per-callout Accept / Reject / Modify in the review section. Fixes the "I clicked Re-assemble and nothing changed" failure mode — detection-pass-only behavior is correct under the hood but invisible to the user; one button + diff makes the result visible. Worktree model is canonical: B3 runs in `.worktrees/workflow-strategy-<domain>-<date>/` on a `workflow/strategy-<domain>-<date>` branch backed by a session task. **Throw Away** discards the pending assembler run only — keeps the worktree open so the user can retry. **Cancel Workflow** is a separate explicit control that tears down the entire session (worktree + branch + task). **Save & Publish** commits, fast-forward merges to main, pushes, tears down the worktree, and marks the session task Complete. Diff format is unified (GitHub-style single pane). Concurrent runs blocked with "Save & Publish or Throw Away the pending diff first." Conflict-aware merge logic stays in `/strategy assemble` (the console invokes it; doesn't re-implement it).

  **Files (5):** `console/web/static/assistant.js` + `console/web/templates/workflow_b3_index.html` (front-end tabs + Run Assembler button + Save & Publish / Throw Away controls); `console/workflows/b3_session.py` (session lifecycle, worktree management); `console/workflows/b3_strategy_reassembly.py` (assembler invocation, diff computation, per-callout review wiring); `console/workflows/router.py` (B3 endpoint surface).

  **Post-update:** Run `/project-console sync` and restart the console (Python module state needs full restart). Browser hard-refresh for the JS/HTML.

- 1.7.8 (2026-05-01): **Markdown table rendering — match VS Code / GitHub preview behavior.** Replace `width: 100%; word-break: break-word; overflow-wrap: anywhere` on `.md-content table` (and parallel `.markdown-body table`) with `display: block; width: max-content; max-width: 100%; overflow-x: auto`. Cell text now wraps at word boundaries; character-level breaking scoped to `<code>` / `<a>` inside cells. New "Markdown Rendering Conventions" section documents the invariants so they survive future drift.
- 1.7.7 (2026-05-01): **Documents view: folder landing prefers `index.md` over `README.md`.** Page trees adopted from external CMS (e.g., Confluence) use `index.md` as the canonical landing file; legacy folders use `README.md`. When both are present, `index.md` wins. Single change in `documents/tree.py` (`README_CANDIDATES` → `FOLDER_LANDING_CANDIDATES`).
- 1.7.6 (2026-04-24): **Documents viewer: browsable skill-library roots + top-level docs in sidebar + relative-link resolution + md/yaml/json wrap fixes.** Several related UX polish items discovered while validating v1.7.5 in-product.

  **Tree sidebar now shows everything the agent can ground on.** `tree.py` `list_dir` + `list_tree` extended to render each multi-segment grounding root (from `Config.grounding_roots`) as a top-level node alongside `docs/` and `tasks/`. Display name strips `.claude/skills/` so the label reads e.g. `medtech-docs/references` rather than the noisy full path. New helper `_extra_root_entries()`.

  **`TOP_FILES` expanded** to surface the canonical repo-root docs in the tree: `CLAUDE.md`, `getting-started.md`, `glossary.md`, `setup.md`, `CHANGELOG.md`, `project-overview.{md,pdf,pptx}`, `project.yml`, `trace-matrix.yml`. Missing entries are silently skipped, so the list is universal across projects.

  **Relative-link resolution in rendered markdown.** Source `.md` files use standard relative paths like `[Full text](source-md/510k-se.md)` so they stay portable (VS Code, GitHub, git tools resolve them natively). The browser can't: it'd resolve against `/documents#path=...` and 404. New `rewriteRelativeLinks(div, basePath)` + `resolveRelativeVirtualPath()` helpers in `explorer.js` walk every `<a href>` in the rendered markdown body, resolve the relative href against the source file's virtual path (handles `..`, `.`, absolute `/`, hash fragments), and rewrite to `/documents#path=<resolved>`. Click handler navigates via `revealAndSelect()` without full page reload; heading-anchor fragments scroll into view after navigation. External schemes (`http`, `mailto`, `tel`, `javascript`, `data`) are left alone. Meta-click / Ctrl-click / middle-click preserve browser defaults (open-in-new-tab).

  **Content-wrap fixes for md, text/yaml/json, and frontmatter.** Three layout issues surfaced on files with long values (FDA guidance `verbatim:` fields, JSON config strings):
  - `.md-content pre` (body code fences — `` ```yaml ``, `` ```json ``): had no CSS rules at all; long lines extended past the pane. Added `white-space: pre-wrap; word-break: break-word; overflow-wrap: anywhere; max-width: 100%`.
  - `.docs-text.lang-yaml` (raw YAML/JSON files rendered with syntax highlighter): had `white-space: pre` explicitly overriding the `pre-wrap` from `.docs-text`, so long lines didn't wrap or scroll. Removed the override — inherits wrap behavior from parent.
  - `.docs-frontmatter pre` (frontmatter YAML preview): added `min-width: 0` on container + `max-width: 100%; white-space: pre-wrap; word-break: break-word` so long `verbatim:` values wrap inside the 180-px panel.
  - `.docs-content-pane` gets `min-width: 0` + `overflow-x: hidden` — belt-and-braces so any rogue child that tries to stretch is clipped, not allowed to push the layout.
  - Also `.docs-rendered { max-width: 80ch }` removed — markdown body now fills the pane.
  - `.md-content table` + `.md-content code` (inline) get `word-break: break-word` so long paths in cells/code don't overflow.

  **Config:** `console.yaml` extra_roots updated to `.claude/skills/dhf-manifest/data` (covers the reorganized fda-guidance/standards/industry-frameworks subfolders under the new `/dhf-manifest` v2 structure; previous path was `.claude/skills/dhf-manifest/data/tier1-regulatory` before the skill refactor).

  **Files:** `console/documents/tree.py` (extended-roots rendering + TOP_FILES expansion); `console/web/static/console.css` (wrap + min-width fixes across md-content, docs-text, docs-frontmatter, docs-content-pane, tables); `console/web/static/explorer.js` (`rewriteRelativeLinks`, `resolveRelativeVirtualPath`).

  **Post-update:** Run `/project-console sync` and restart (tree.py is Python, needs full restart). Browser hard-refresh for the JS/CSS. After that, the Documents sidebar shows all canonical docs at root level; relative links in markdown click-navigate within the viewer; long lines in YAML/JSON files wrap within the pane.

- 1.7.5 (2026-04-23): **Documents viewer accepts grounding roots + `source-md` groundability.** Two follow-up fixes discovered during in-product testing of v1.7.4:
  1. **Citations to skill-library paths were 404ing.** `documents/tree.py` `ROOT_NAMES = ["docs", "tasks"]` rejected paths like `.claude/skills/medtech-docs/references/standards/iec-62304.md`, so clicking `[N]` citation superscripts landed on an empty viewer. New `_extended_roots()` helper merges `Config.grounding_roots` into the resolver (longest-prefix match) while keeping the single-segment `ROOT_NAMES` for the sidebar tree display. Hash-fragment URLs (`/documents#path=<virtual>`), `/documents/api/file?path=...`, and `/documents/raw/...` all now serve skill paths correctly.
  2. **`source-md/` inside skill folders was being excluded.** These are the full-text markdown conversions of FDA guidance PDFs — agents need them for clause-level citations. Removed `source-md` from `_EXCLUDE_SEGMENTS`; added new `_COVERAGE_SKIP_SEGMENTS = {"source-md"}` so these bulk-conversion folders don't generate missing-README coverage warnings (they're groundable but not curated).

  Kept excluded: `source/` (pre-conversion originals — DOCX/PDF, not markdown), `formal/` (post-conversion exports — DOCX/PDF), `images/`, `.staging/`.

  **Effect on grounding:** agents can now fetch the full-text FDA guidance conversions at `.claude/skills/medtech-docs/references/fda-guidance/source-md/*.md` via `read_files`, cite them with GFM heading anchors, and users click the citations to open the doc viewer at that section. The full two-layer citation model from v1.7.4 now has working hyperlinks end-to-end on both layers.

  **Files:** `console/documents/tree.py` (`_extended_roots`, multi-segment `resolve_virtual_path`); `console/chat/index_builder.py` (exclusion set trimmed, `_COVERAGE_SKIP_SEGMENTS` added, missing-README walker honors it).

  **Post-update:** Run `/project-console sync` and restart. No config changes needed — the existing `grounding.extra_roots` in `console.yaml` continues to drive both index scanning and Documents-viewer path resolution through the same `Config.grounding_roots`.

- 1.7.4 (2026-04-23): **Configurable grounding roots + two-layer standards citation.** The v1.7.3 rubric tightening instructed agents to cite project-distilled standards at `docs/external/standards/...`, but the project-side files hold *applicability analysis* (module mapping, deferred clauses, `[VERIFY]`s), while the *source distillation* (clause text) lives upstream in skill libraries at `.claude/skills/medtech-docs/references/` and `.claude/skills/dhf-manifest/data/tier1-regulatory/`. Agents couldn't reach those skill-library files — so even with mandatory-standards-citation, they were citing applicability without the source text.

  **New:** `config.yaml grounding.extra_roots` — extend the grounding surface with additional filesystem roots beyond the project's docs tree. The `index_builder` and `read_files` tool now honor `Config.grounding_roots`. Exclusion rules (`source/source-md/formal/images/.staging`) apply **below** each root, so `docs/internal/source-md/*` (explicit root) stays visible while `.claude/skills/.../fda-guidance/source-md/*` (raw full-text conversions, inside a skill root) is excluded.

  **Configured on this project:** `console.yaml` exposes `.claude/skills/medtech-docs/references` and `.claude/skills/dhf-manifest/data/tier1-regulatory` so agents can cite authoritative clause text + structured obligations alongside project applicability analysis.

  **Rubric upgrade:** the EXTERNAL STANDARDS & GUIDANCE section of `_DISCOVERY_RUBRIC` now instructs the agent to fetch and cite **both layers**: Layer 1 (project applicability — `docs/external/...`) and Layer 2 (source distillation — `.claude/skills/medtech-docs/references/...`). Every standards citation carries two footnotes, applicability first.

  **New READMEs** authored for every exposed skill folder so the shared INDEX picks them up with scope + "For Claude" framing:
  - `.claude/skills/medtech-docs/references/README.md`
  - `.claude/skills/medtech-docs/references/standards/README.md`
  - `.claude/skills/medtech-docs/references/fda-guidance/README.md`
  - `.claude/skills/medtech-docs/references/industry-frameworks/README.md`
  - `.claude/skills/dhf-manifest/data/tier1-regulatory/README.md`

  **Updated project-side READMEs** to make the applicability-vs-source distinction explicit:
  - `docs/external/README.md` — now leads with "applicability analysis — NOT the source material itself" and tables the skill-library locations
  - `docs/external/standards/README.md` — directs readers to `.claude/skills/medtech-docs/references/standards/` for clause text

  **Index growth:** 118 → 123 READMEs, 206 KB → 232 KB (~26 KB added, well within Sonnet's budget). Missing-README warnings dropped from 5 to 2 (the 2 remaining are legitimate project-side gaps flagged for cleanup).

  **Files:** `console/config.py` (`grounding_roots` property); `console/chat/index_builder.py` (root-aware exclusion via `_is_excluded_under_root`, new public `is_groundable()`; added `source-md` to exclude segments); `console/chat/sdk_client.py` (`_expand_one_path` uses `get_config().grounding_roots` + `is_groundable`); `console/assistant/router.py` (rubric two-layer expansion); `console.yaml` + `scaffold.py` template (commented `grounding.extra_roots` example).

  **Post-update:** Run `/project-console sync` and **restart** the console. New projects that want the skill-library grounding should uncomment the `grounding.extra_roots` block in `console.yaml`. The rubric change is universal — agents everywhere will now cite both layers on standards questions.

- 1.7.3 (2026-04-23): **Rubric: mandatory grounding for regulatory standards & guidance.** Observed in-product that assistants were answering "per IEC 62304 §5.3..." from training-data knowledge rather than fetching the project's distilled copy at `docs/external/standards/iec-62304-software-lifecycle.md` and citing it. The content was always reachable (every `docs/**/README.md` is in the shared INDEX), but the agent was taking the cheaper training-data path when a standard showed up in its own reasoning.

  New section added to `_DISCOVERY_RUBRIC` — **EXTERNAL STANDARDS & GUIDANCE — MANDATORY GROUNDING** — instructs the agent that when any named standard or FDA/industry guidance document is referenced (IEC/ISO standards, 510(k), PCCP, SaMD, CDS, GMLP, DICOM, HL7, NIST, AAMI, etc.), it MUST (1) scan the INDEX for a distilled copy under `docs/external/{standards,fda-guidance,industry-frameworks}/`, (2) fetch via `read_files` and cite the distilled file, (3) treat the distilled copy as ground truth (including module-applicability and deferred-section notes that training data can't know), (4) if no distilled copy exists, say so explicitly rather than citing training knowledge. Applies whether the standard appears in the user's question or in the agent's own reasoning as justification.

  Why project-level distilled copies beat training knowledge: they capture *this program's* decisions (e.g., which sections apply to which modules, which clauses are deferred to QMS, what's VERIFY'd). Training-data IEC 62304 doesn't know about this program's module split or the project's deferred-to-QMS marks.

  **Post-update:** Run `/project-console sync` and **restart** the console (Python rubric change, not watched by uvicorn `--reload`). No agent-file changes needed — the rubric is centrally composed into every system prompt. Agents' answers should now include `[N]: docs/external/standards/iec-62304-software-lifecycle.md` style footnotes whenever they invoke a standard.

- 1.7.2 (2026-04-23): **Assistant drawer: sticky auto-scroll + "Jump to latest" pill.** Fixes the common streaming-UX annoyance where scrolling up to re-read earlier content while the model is still responding was impossible because each new token force-yanked you back to the bottom. Now:
  - Token streaming checks `scrollHeight - scrollTop - clientHeight < 60px` before each content update; only auto-scrolls if the user was already near the tail
  - When the user has scrolled up during streaming, a small blue "↓ Jump to latest" pill fades in above the composer; click to snap to bottom + hide
  - Pill auto-hides when the user manually scrolls back to within 60 px of the bottom, and on any new message append (user-sent turn + assistant placeholder both force-scroll + hide)
  - New message append paths (user send, assistant placeholder, thread replay) continue to force-scroll — intentional; those are new turns, not streamed continuations

  **Files:** `console/web/static/assistant.js` (`mountJumpToLatest` IIFE adds the pill + scroll listener; token-stream path captures `nearBottom` pre-update and gates the scroll; `appendMessageEl` hides the pill on any new turn); `console/web/static/console.css` (new `.pc-jump-latest` + `.pc-jump-latest.visible` rules).

  Tiny change, one of the most visible UX improvements since the drawer shipped.

- 1.7.1 (2026-04-23): **Clickable footnote citations in the assistant drawer.** Extends the task 099 Phase 2 grounding architecture with source-attribution UX. The discovery rubric now requires the assistant to cite every factual claim with numbered footnotes (`[1]`, `[2]` inline + `[N]: docs/path/to/doc.md[#anchor]` definitions at the end of the response). The client post-processes the rendered markdown to:
  - Extract trailing `[N]:` footnote definitions from the raw body, stripping them from display
  - Wrap each inline `[N]` reference as `<sup><a class="pc-cite">` pointing at `/documents#path=<path>[#anchor]` (opens in a new tab)
  - Append a collapsed `<details class="pc-sources">Sources (N)</details>` block listing all cited paths
  - Tolerant: unmatched `[N]` tokens pass through unchanged; bad anchors degrade to doc-top navigation

  Heading anchors use GitHub-flavored slugs (lowercase, spaces→dashes, punctuation stripped); the Documents viewer is reached via the existing hash-routed SPA (`/documents#path=...`) so no new backend routes required.

  **Files:** `console/assistant/router.py` (`_DISCOVERY_RUBRIC` grows a **Citation Format** section with rules + examples); `console/web/static/assistant.js` (`extractCitations`, `wrapInlineCitations`, `renderSourcesBlock` helpers; `setMessageContent` composes body + sources-details); `console/web/static/console.css` (new `.pc-cite-sup`, `.pc-cite`, `.pc-sources`, `.pc-cite-list`, `.pc-msg-info` rules).

  **Post-update:** Run `/project-console sync` and **restart** the console. Agents' prompts get the citation rubric automatically on next request — no agent frontmatter changes needed. Existing docs work without modification; authors can improve citation precision by keeping `##`-level headings stable and descriptive so the agent's anchor guesses hit.

- 1.7.0 (2026-04-23): **Tiered grounding architecture — Phase 2 of task 099.** Solves the fundamental problem that motivated Phase 1 (content-heavy agents 6× over cap on Sonnet) by restructuring how grounding reaches the assistant drawer instead of just raising the cap.

  **Three tiers** (replace the old monolithic `sources:` blob):
  - **Tier 1 — Focus** (page grounding): unchanged. The currently-open doc on Documents pages.
  - **Tier 2 — Core** (agent `core:` frontmatter): small curated list of "north star" files or folders loaded in full. Typical size: 50–150 KB.
  - **Tier 3 — Index** (shared): concatenated `docs/**/README.md` tree, built at startup, ~200 KB on a well-organized project. Every agent sees it. Human-authored; no LLM summarization; always current.
  - **Tool — `read_files(paths: list[str])`**: custom in-process MCP tool (`console-grounding` server). Agent fetches specific .md content on demand. Folder paths expand to `README.md` + direct-child .md files; source/formal/images/.staging paths rejected; max 200 KB per file inlined.

  **Discovery rubric** (baked into every agent's system prompt): "Read Core → scan Index → for any folder whose README matches the question, call `read_files(paths=[...])`. Prefer over-fetching. Cite specific paths in your response." Raises `max_turns` from SDK default to 15 so agents can iterate.

  **New:**
  - `console/chat/index_builder.py` — `build_index()`, `resolve_core()`, `concatenate_files()`, `_is_excluded()`. Pure functions, <10 ms cold.
  - `console/chat/sdk_client.py` — `@tool` decorator + `create_sdk_mcp_server` register `_read_files_tool`; `stream_response` takes `enable_read_files` + `max_turns`.
  - `console/assistant/router.py` — three-section `_build_system_prompt(agent_persona + CORE + discovery rubric + INDEX + FOCUS)`. New endpoints: `GET /assistant/api/index/status`, `POST /assistant/api/index/rebuild`. SSE `info` frame reports Core/Index sizing per request.
  - `console/app.py` — lifespan warms the index at startup and logs coverage warnings (folders with `.md` content but no README.md).
  - `assistant.js` — renders new `info` SSE event as a muted info line above the response.

  **Agent schema change** (`domain_agents.DomainAgent`): new `core: list[str]` field (paths, folders, or globs). Legacy `sources:` agents auto-map to `core` for backwards compatibility — one release before removal. All 13 core-team agents migrated on this project to tight `core:` lists (1–2 north-star entries; biggest is program-manager at 140 KB, smallest is clinical-affairs at 2.6 KB).

  **Exclusion rule** (hardcoded; not configurable): paths with any segment named `source`, `formal`, `images`, or `.staging` are never inlined into Core/Index and never accepted by `read_files`. Pre/post-conversion artifacts stay out of grounding.

  **Deleted from v1.6.1 Phase 2 design:** `groundings.yaml` schema + `/project-console groundings init` scaffolder + LLM catalog summarizer + `.data/grounding-catalog.json` content-hash cache — all obsoleted by the README-as-index pivot.

  **Post-update:** Run `/project-console sync` + **restart** the console (`/project-console start`). Agents written against earlier versions with `sources:` still work (auto-mapped to `core`) but should be migrated: change `sources:` → `core:` and trim to a tight 1–3-entry list of north-star files/folders. Every `docs/**/<folder>/` should have a `README.md` — the startup logs a warning for any folder with `.md` content but no README; see also task 101 for the parallel README-convention robustness sweep (explicit In Scope / Out of Scope subsections recommended for better index quality).

- 1.6.1 (2026-04-23): **Model-aware source + grounding caps — Phase 1 of tiered grounding (task 099).** Unblocks content-heavy agents on Sonnet: the previous 200 KB `MAX_BYTES` / 80 KB `GROUNDING_CAP` cap forced a 6× truncation on Systems Engineering (1.2 MB of grounding across 118 files).

  **Resolution.** `Config` gains `resolve_model(model)` and `caps_for_model(model)` as single source of truth. `router.assistant_chat_stream` now resolves the effective model (agent frontmatter → `models.default` → code default), looks up caps, and passes `cap_bytes` to `resolve_with_meta` + `grounding_cap_bytes` to `_build_system_prompt`. Resolution order for caps (highest wins): `console.yaml models.caps.<model>` → `console.yaml models.caps.default` → code defaults `_MODEL_CAP_DEFAULTS[<model>]` → `DEFAULT_CAPS` (Sonnet-tier fallback).

  **Defaults** (baked in `config.py`):
  - `claude-sonnet-4-6`: 500 KB sources, 80 KB grounding (fits ~125K tokens inside 200K window)
  - `claude-opus-4-7`: 2 MB sources, 200 KB grounding (fits ~500K inside 1M window)
  - `claude-haiku-4-5`: 300 KB sources, 80 KB grounding

  **Deprecated.** `sources.MAX_BYTES` module-level constant is now a fallback only for callers that don't pass `cap_bytes`; the production chat path always passes a resolved model-aware value. `router.GROUNDING_CAP` constant removed — `_build_system_prompt` now takes `grounding_cap_bytes` as a required parameter. `sdk_client._resolve_model` now delegates to `Config.resolve_model` for single source of truth.

  **Config template.** Both the live project `console.yaml` and `scaffold.py`'s `CONSOLE_YAML_DEFAULT` now include a commented example `models.caps` block showing the three-model defaults; also seeds `models.summarizer: claude-haiku-4-5` for the Phase 2 catalog builder (task 099).

  Fixes the Systems Engineering drawer's "Source budget exceeded (200KB cap): included 18 file(s), skipped 100" warning at the default cap. Actual usage on an adopting project with default Sonnet cap (500 KB) against SE's current source globs: 118 files × ~10 KB avg ≈ 1.2 MB — still over-budget but only after the task 099 `core_sources`/catalog split in v1.7.0 will that fully resolve. For now, raising the cap from 200 KB to 500 KB cuts skipped files from 100 to ~60 and includes the top-priority architecture + requirements docs.

  **Post-update:** Run `/project-console sync` to pull the scaffold template update (adds `models.summarizer` + commented `models.caps` example) and then **restart** the console (`/project-console start`) — uvicorn's `--reload` does not watch the skill package. No breaking changes; agents with explicit `model:` entries in frontmatter continue to work. To tune caps beyond the defaults, uncomment the `models.caps` block in `tools/project-console/console.yaml`.

- 1.6.0 (2026-04-23): **Fix `[Errno 7] Argument list too long` + model configuration.**

  **`[Errno 7]` fix.** `sdk_client.py` now writes `system_prompt` to a `NamedTemporaryFile` and passes `SystemPromptFile(type="file", path=...)` to `ClaudeAgentOptions` instead of inlining the string. The SDK translates this to `--system-prompt-file <path>`, avoiding the OS `ARG_MAX` limit that fires when combined agent sources + grounding can reach ~285 KB. The temp file is always cleaned up in a `finally` block. `TODO: make source/grounding caps model-aware` comments added to `sources.py` and `router.py`.

  **Model configuration.** New `_resolve_model()` helper in `sdk_client.py` enforces the resolution hierarchy: agent frontmatter `model: <id>` (explicit) → sentinel `model: default` or absent → `console.yaml models.default` → `config.py DEFAULT_MODEL` fallback (never falls through to uncontrolled CLI default). `config.py` gains `DEFAULT_MODEL = "claude-sonnet-4-6"` constant, `models: {default: DEFAULT_MODEL}` in `_DEFAULT_CONSOLE_YAML`, and a `Config.model_default` property. `scaffold.py` `CONSOLE_YAML_DEFAULT` template now includes `models: default: claude-sonnet-4-6`. All 13 agent files under `tools/project-console/agents/core-team/` now declare `model: default` in frontmatter — explicit intent rather than silent absence.

  **Warning display.** Source budget warnings (⚠ SSE frames from `sources.py`) are no longer rendered as prominent inline alerts. They accumulate in `pendingWarnings[]` and flush as a single `<details><summary>⚠ Source budget notice (N)</summary>…</details>` block, collapsed by default, inserted above the response. The warnings themselves are kept — they give teams visibility into source glob truncation.

  **Post-update:** Run `/project-console sync` (scaffold.py template change) then **restart** the console (`/project-console start`). Add `models: default: claude-sonnet-4-6` to `tools/project-console/console.yaml` if updating an existing install (or let `sync` regenerate it). Agent files already updated in this project — if other projects use cloned agent files they should also add `model: default` to frontmatter.

- 1.5.0 (2026-04-22): **Two new sections — Overview + Unified Assistant drawer.**

  **Overview section.** New `console/overview/` module auto-detects `project-overview.{pdf,pptx,md}` at repo root. When any exist, an "Overview" entry is injected as the **first nav item** (left of Agents) and as the first landing-page tile. Routes: `GET /overview` embeds the PDF in a full-height `<iframe>` with download buttons for `.pptx` and a link to the markdown; `GET /overview/raw.pdf` serves inline; `GET /overview/download.pptx` serves as attachment. Falls back cleanly on projects without any overview file — the nav entry, tile, and template simply don't render. Middleware attaches `request.state.overview_nav` so `_base.html` and `index.html` can branch on it with one conditional each. Styled via new `.overview-*` rules in `console.css` (hero layout, primary/secondary action buttons, full-height iframe viewer, no-viewer fallback). Discovered while writing `project-overview.md` + `.pptx` for the demo project (task ben/025) — the overview was invisible from the console until this landed.

  **Unified Assistant drawer.** New `console/assistant/` module + `_assistant_drawer.html` Jinja partial + `assistant.js` (generic drawer JS: thread select, history, SSE streaming, markdown render) + `docs-assistant-glue.js` (Documents-page wiring that grounds the drawer on whatever file is currently open). Replaces the bespoke Systems Engineering Assistant drawer that lived inline in `trace_matrix_view.html` — the drawer is now a shared partial that any page mounts via `data-*` attributes (`data-scope`, `data-default-agent`, `data-agents`, `data-grounding-url`). Trace Matrix swaps in the generic drawer with `default-agent: systems-engineering`; Documents explorer mounts it with an agent picker and per-doc grounding. Single implementation across the console. One SSE endpoint at `/assistant/chat/stream` handles both (page-supplied grounding URL is fetched server-side at request time, capped). Thread history stays client-side (localStorage), keyed by page-supplied scope. Discovered while the SE-only drawer accumulated three near-duplicate implementations across trace-matrix, documents, and a proposed dashboards sidecar (task ben/024).

  **Post-update:** Run `/project-console sync` to pull in any scaffold deltas, then **restart** the console (`/project-console start`) — uvicorn `--reload` does not watch the skill package, so module additions (overview/, assistant/) only load on fresh process start. Existing projects with no `project-overview.*` at repo root see no change. Existing projects with a `project-overview.pdf` (or `.pptx`, or `.md`) at root get the new Overview section automatically on next restart. Build the PDF with `soffice --headless --convert-to pdf project-overview.pptx` if you already have a `.pptx` but no `.pdf` — the console only embeds the PDF (`.pptx` is a download link).
- 1.4.1 (2026-04-16): **Drop `xargs -r` from scaffolded `start.sh`** (`START_SH_TEMPLATE` lines 229, 234 of `scaffold.py`). `xargs -r` (no-run-if-empty) is a GNU extension; BSD xargs rejects it with `xargs: illegal option -- r`, silently swallowed by `|| true`. Net effect on macOS: the TERM-then-KILL cascade for stopping an existing listener was a no-op — `start.sh` would print "stopping existing console" and then fail to actually stop it, resulting in port-in-use errors on the subsequent bind. The outer `if [ -n "$existing" ]` already guards empty input, making `-r` redundant on both platforms. Discovered during task 067 cross-platform audit.
  **Post-update:** Run `/project-console sync` on any existing console scaffold to regenerate `tools/project-console/start.sh` without `-r`. Projects that never ran `/project-console start` on Mac are unaffected.
- 1.4.0 (2026-04-15): **Trace Matrix: one-click init via Claude Agent SDK.** New `POST /trace-matrix/{dhf}/init/stream` SSE endpoint that runs the full `/trace-matrix init` skill action — including LLM-authored adapter generation — via the `claude-agent-sdk.query()` interface with `allowed_tools=[Bash, Read, Write, Edit, Glob, Grep]`, `permission_mode='bypassPermissions'` (localhost dev tool), `cwd=repo_root` so the skill lookup resolves, and `max_turns=40` to cap a runaway loop. The empty-state view template now has two buttons: **Initialize with Claude** (runs the LLM flow; uses tokens) and **Build this DHF now** (runs the deterministic `build.py`; fast, no LLM). Live output panel consumes the SSE stream via `fetch` + `ReadableStream` and renders token text, tool calls (e.g. `[tool] Write: path/to/file`), and the final `ResultMessage` summary, then auto-reloads on `done`.
  **Bug found + fixed during implementation:** uvicorn `--reload` watches `tools/project-console/` recursively. When the init flow writes a generated parser adapter to `tools/project-console/trace-matrix/adapters/<layer>.py`, watchfiles would kill uvicorn mid-stream and abort the init subprocess. `run.sh` now passes `--reload-exclude` patterns for `trace-matrix/**`, `.venv/**`, `__pycache__/*`, and `.data/*` so file writes under those paths don't trigger a reload.
  Verified live on an adopting project (task ben/054): clicked the button, watched the stream render 30+ tool calls over 10 minutes (Read SKILL.md → Read project.yml → Bash `ls` various dirs → Write `trace-matrix.yml` → Read `analyze.py` → Bash `analyze.py` → Read SAD doc → Write custom `architecture.py` adapter), then ran `build.py` to produce `docs/project/dhfs/<device>-suite/design-controls/trace-matrix/trace-matrix.{md,json}` with 6 architecture nodes parsed via the generated adapter.
  **Post-update:** Run `/project-console sync` to regenerate `tools/project-console/run.sh` with the new `--reload-exclude` patterns. Existing scaffolds already have `console.yaml` and don't need config changes. The `Initialize with Claude` button only appears on the empty-state view (when a DHF has no sidecar yet) — builds after that continue to use `Rebuild this DHF` on the populated view.
- 1.3.0 (2026-04-15): **Trace Matrix: path normalization, empty-state UX, surfaced build errors.** Three bugs surfaced on an adopting project when clicking the `Build this DHF` button before `/trace-matrix init` had been run:
  1. **Loader double-nested the sidecar path.** `list_dhfs()` joined `repo_root / docs/project/dhfs / <path>` under the assumption that `project.yml` `dhfs[].path` holds a leaf name (the the demo project convention). an adopting project uses the full path there (`docs/project/dhfs/<device>-suite`), which produced `docs/project/dhfs/docs/project/dhfs/<device>-suite/...` and 404'd every lookup. Loader now normalizes: accepts `leaf:` as an explicit field, accepts `path:` as either a leaf (`pca-device`) or an already-prefixed full path (`docs/project/dhfs/pca-device`), and resolves to a single canonical `dhf_root`.
  2. **Router raised raw HTTPException 404 on missing sidecar.** `GET /trace-matrix/{dhf}` now renders `trace_matrix_view.html` in empty-state mode when the DHF is known but no sidecar exists yet — same template, different branch — so the user sees a "Build this DHF now" button plus guidance instead of `{"detail": "No trace-matrix sidecar..."}` as JSON.
  3. **Build endpoints silently swallowed failures.** `POST /trace-matrix/build` and `POST /trace-matrix/{dhf}/build` now inspect `returncode` and, on failure, capture stdout+stderr, pattern-match for common signatures (`trace-matrix.yml not found` → "run `/trace-matrix init` first"; skill missing → "run `/sync-skills pull`"), and redirect with a `build_error` query string that both the index and view templates render as a warning banner with the full captured output. The previous behavior — unconditional redirect — made a failed build look like a successful one until the user noticed the page was still empty.
  Discovered by Ben on PCCP task ben/054 clicking the Build button before running `/trace-matrix init`.
  **Post-update:** Run `/project-console sync` to note the version bump (no scaffold file changes). Restart the console via `/project-console start` to pick up the new router + loader + templates (uvicorn `--reload` doesn't watch the skill package).
- 1.2.0 (2026-04-15): **Config-driven launch + macOS venv hygiene.** `run.sh` now reads `server.host` + `server.port` from `console.yaml` (falls back to `127.0.0.1:8765`) instead of hardcoding `--host 127.0.0.1 --port 8765`. This matches what `start.sh` already did — they share the same awk block now. `scaffold.py init` gains a `--port N` flag (default `8765`) so Claude can ask the user to confirm the default before scaffolding, which prevents silently colliding with an already-running console on the same box. `run.sh` also strips macOS Finder junk (`Icon\r` custom-folder-icon files, AppleDouble `._*` resource forks) from `.venv/` on every launch — on at least one machine these had leaked into `site-packages/jsonschema_specifications/schemas/` and crashed `jsonschema.iterdir()` at import time with `NotADirectoryError: 'Icon\r'`. Skill `.gitignore` extended to exclude `Icon?`, `._*`, `.DS_Store` so the junk can't be committed upstream through `sync-skills push`. SKILL.md `init` action updated to require port confirmation (check `lsof -ti tcp:8765`; suggest next free port if occupied); `run` action documents the new config-driven launch and the venv cleanup step. Discovered while installing this skill on an adopting project where a the demo project console was already holding `:8765` and the the adopting project's venv had 311 stray `Icon\r` files inherited from a previous `uv sync`.
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
- 1.0.1 (2026-04-14): Bugfix — documents tree walker now hides macOS `Icon\r` custom-folder-icon files, Windows `Thumbs.db` / `desktop.ini`, and AppleDouble resource forks (`._*`) in addition to dotfiles. Discovered in an adopting project where `Icon\r` files at several directory roots were cluttering the explorer. New `_is_hidden()` helper in `console/documents/tree.py` centralizes the junk-file filter so all three walker call sites (`list_children`, `_dir_has_any_children`, `_children`) share the same rules.
  **Post-update:** **Restart the console if it's running.** Uvicorn's `--reload` watches the project's `tools/project-console/` directory (the launcher's CWD), **not** the skill package under `.claude/skills/project-console/console/`. Skill updates require a restart — Ctrl+C the running process and re-run `tools/project-console/run.sh`. (Earlier versions of this changelog entry incorrectly said `--reload` handled it automatically.)
- 1 (2026-04-14): Initial version. Extracted from the demo project's hand-built `tools/project-console/`. Generic template library (10 personas), two skill theme packs (light/dark), glob-scan dashboard discovery, manifest-based install tracking, sys.path launcher pattern. Company-agnostic: no brand assets or project names inside the skill package. Ships with `init`, `sync`, `theme`, `run`, `status` actions. Includes a skill-root `.gitignore` to keep `__pycache__/` and `*.pyc` out of the registry; `scaffold.py init` writes the same patterns into every `tools/project-console/.gitignore`. Three Best Practices checks enforce the gitignore coverage and skill cleanliness.
