---
name: md-deck
description: Build a beautiful single-file HTML slide deck from any structured markdown source (whitepaper, project overview, strategy doc, board briefing, investor memo, ops report). Non-interactive markdown → HTML pipeline; the builder sibling to the `frontend-slides` stylist. v0.6 — domain-neutral trunk + opt-in icon vocabulary packs (medtech / finance / manufacturing / …) loaded via project.yml `md_deck.vocabulary_packs` or the `--vocabulary` flag. Consumes the canonical viewport contract and preset registry from `frontend-slides` (no duplication); content-split rules replace shrink-to-fit density modifiers; handles title, agenda, dividers, table-slides, card-grids, list-slides, quote-slides, prose-slides, image-feature slides; injects scope-iceberg / concept-canvas / handoff-relay / principle-tiles / catalog-mosaic / catalog-featured variants; detects homogeneous groups (cohorts, teams, deliverables, milestones, metrics, plus pack-specific groups) and gives them a shared kind-icon. Output lands at `<root>/assets/<source-slug>/` with full provenance metadata.
version: 0.6.3
updated: 2026-07-21
---

# md-deck

Author a beautiful, single-file HTML slide deck from any structured markdown source. md-deck is the **markdown-pipeline builder**; for interactive style discovery, PPTX ingest, or in-browser editing use the sibling `frontend-slides` skill.

## Relationship to `frontend-slides`

md-deck and `frontend-slides` are sibling skills with a shared infrastructure layer. `frontend-slides` is the **canonical source** for slide-rendering infrastructure; md-deck consumes it.

| Asset | Owner | Consumed by md-deck |
|---|---|---|
| `frontend-slides/viewport-base.css` | frontend-slides | Yes — prepended to every preset, owns the `.slide` / `100vh` / `clamp()` contract |
| `frontend-slides/STYLE_PRESETS.md` | frontend-slides | Reference — md-deck `--style <name>` resolves against this registry |
| `frontend-slides/presets/<name>.css` | frontend-slides | Yes — full preset stylesheet for `<name>` (bold-signal canonical lives here) |
| `frontend-slides/scripts/export-pdf.sh` | frontend-slides | Yes — md-deck has no PDF export of its own |
| `frontend-slides/scripts/deploy.sh` | frontend-slides | Yes — md-deck has no deploy of its own |
| `md-deck/scripts/build.py` | md-deck | n/a — markdown parser, slide synthesis, variant injection, manifest |
| `md-deck/scripts/icons.py` | md-deck | n/a — icon repository for variant slides |
| `md-deck/runtime/deck-runtime.js` | md-deck | n/a — chrome auto-numbering, provenance modal, key nav |

**Path-aware fallback.** If `frontend-slides/` is absent, md-deck falls back to its own `styles/<name>.css` legacy copy and skips the viewport-base prepend with a soft warning. Co-installation is recommended.

## Non-goals

These belong to `frontend-slides`, not md-deck:

- **Interactive style discovery / mood wizard.** md-deck is non-interactive (regulated-doc pipeline, scriptable from CI). Use `frontend-slides` Phases 1–2 if you need AskUserQuestion-driven style selection.
- **PPTX ingest.** md-deck consumes markdown only. PPTX → HTML is `frontend-slides/scripts/extract-pptx.py`.
- **Inline / in-browser editing.** Conflicts with the provenance contract — every slide carries `data-source-anchor` back to a markdown line range; the markdown is the source of truth, not the rendered HTML.
- **Vercel deploy / share workflow.** Lives in `frontend-slides/scripts/deploy.sh`.

## Status

## Status

- **v0.1** — proved the pipeline (parse, slide synthesis, Bold Signal HTML, provenance metadata).
- **v0.2** — table density auto-scaling, variant injection (multi-emit), six metaphor templates, image-feature slides, 86→144-icon repository, group detection. Single-skill build with embedded CSS.
- **v0.3 (current — ben/042 shared-layer refactor)** — the infrastructure split:
  - **Shared layer with `frontend-slides`.** Viewport CSS, preset registry, and PDF/deploy scripts now live in `frontend-slides`; md-deck imports them at build time. See "Relationship to `frontend-slides`" above.
  - **Content-split rules replace density modifiers.** Card-grids and list-slides exceeding 6 items split into N continuation slides ("(cont.)" suffix) instead of shrinking type to fit. Replaces the `density-{compact,tight,very-compact}` band-aid path. Tables still paginate via catalog-mosaic.
  - **Multi-preset support.** `--style <name>` resolves against `frontend-slides/presets/<name>.css` first, with legacy fallback to `md-deck/styles/<name>.css`. Bold Signal remains the default.
  - **Iconography continued from v0.2.** 144-icon repository, group detection, variant injection unchanged.
- **v0.4 (planned)** — lexical-homogeneity for group detection; group-cell numbering badges; brand-pack ingestion (`/md-deck brand-from <url>`) feeding new entries into the shared `STYLE_PRESETS.md`; iteration commands (`refine`, `swap-style`, `add-variation`, `cull`); drift detection against source SHA-256.

## Usage

```bash
# Generate a deck from a markdown source
python .claude/skills/md-deck/scripts/build.py project-overview.md

# Specify a different style preset (currently only bold-signal supported)
python .claude/skills/md-deck/scripts/build.py whitepaper.md --style bold-signal

# Override the output directory
python .claude/skills/md-deck/scripts/build.py source.md --output-dir custom/path/
```

Output:
- `<root>/assets/<slug>/index.html` — single-file HTML deck (Bold Signal preset).
- `<root>/assets/<slug>/manifest.json` — machine-readable build sidecar (provenance, slide list, components used).

PDF export is **not** auto-run on rebuild. Generate explicitly only when needed:

```bash
bash .claude/skills/frontend-slides/scripts/export-pdf.sh assets/<slug>/index.html assets/<slug>/index.pdf
```

### PDF export caveats (v0.6.3)

Two export paths, different failure modes:

- **`export-pdf.sh` (screenshot-based, preferred)** — Playwright rasters each slide; immune to viewer-dependent rendering.
- **Chrome `--print-to-pdf` (vector print)** — every generated deck carries a hardened `@media print` block (`PRINT_HARDENING_CSS` in `build.py`): page box pinned to the authored viewport in **inches** (Chrome mis-handles px in `@page size`), one slide per page, and **all box/text-shadows stripped**. The shadow strip is load-bearing: several PDF viewers (macOS Preview included) rasterize Chrome's printed shadow groups as hard-edged translucent slabs painted over neighboring content — a soft glow becomes a giant opaque rectangle.

**Verification discipline:** always eyeball a Chrome-printed PDF in the viewer the audience actually uses (e.g. Preview). Poppler-based page extractors render shadows softly and will not reproduce the slab defect — a single-renderer check can pass while the deliverable is broken.

## Heuristic registry — markdown shape → slide type

| Markdown shape | Maps to |
|---|---|
| `# Title` + paragraph + `**Foo:** bar` meta | Title slide |
| (computed from `## §N` headings) | Agenda slide |
| `## N. Section Name` | Section divider with massive numeral N |
| `### N.M Subsection` containing a table | Table slide (rows ≥6 paginate via catalog-mosaic) |
| `### N.M Subsection` containing a 6+-row catalog table | Mosaic + featured variants auto-emitted |
| `### N.M Subsection` with a bold-led bullet list | Card-grid slide (split at >6 tiles into "(cont.)" continuation) |
| `### N.M Subsection` with a regular bullet list | List slide (split at >6 items into "(cont.)" continuation) |
| `### N.M Subsection` with a short blockquote | Quote slide |
| `### N.M Subsection` with paragraphs only | Prose slide |
| `### N.M Subsection` with a single `![alt](path)` block | Image-feature slide |
| `#### N.M.K Sub-subsection` | Same rules as `### N.M`, finer numbering |

Code blocks (`````) are dropped from output.

## Content-split rules (replaces v0.2 density modifiers)

md-deck honors `frontend-slides`' density-limits table. When a slide's content count exceeds the per-type maximum, the slide **splits into N continuation slides** rather than shrinking type to fit. Continuation slides carry a "(cont.)" suffix in the title and a `--contN` suffix on their slug (v0.6.2 — parts must not share a slug: the section/picks machinery keys by slug, and a shared slug made the last part overwrite the head slide). All parts share the original `source_lines` / `source_sha256` provenance for drift detection; the head part keeps the unsuffixed slug so existing `picks.json` entries stay bound to it. Deck-runtime auto-renumbers chrome from DOM position.

| Slide type | Limit | Behavior on overflow |
|---|---|---|
| `card-grid` | 6 tiles | Split into ⌈N/6⌉ continuation card-grid slides |
| `list-slide` | 6 items | Split into ⌈N/6⌉ continuation list slides |
| `table-slide` (catalog) | 6 rows → mosaic | Paginate via `catalog-mosaic` (8/slide) — unchanged from v0.2 |
| `prose-slide` | n/a | Single slide; long prose is a content-authoring concern, not a build-time concern |

The `density-{compact,tight,very-compact}` shrink-to-fit modifiers from v0.2 are retired. Content-splitting yields readable type at every viewport, including the 1280×720 PDF export path.

## Variant detection (multi-emit)

`_inject_variants(slide)` returns a list of variant slides (zero or more) emitted right after the detail slide.

| Trigger | Variant |
|---|---|
| Table with ≥6 rows × 2 cols | `catalog-mosaic` (paginated 8/slide) + `catalog-featured` |
| Title contains `SCOPE_KEYWORDS` ("filing scope", "carve-out", "in vs out") | `scope-iceberg` |
| Title contains `TEACH_KEYWORDS` ("what … is", "where the … happens", "how it works") | `concept-canvas` |
| Title contains `HANDOFF_KEYWORDS` ("handoff", "who does what", "human/agent") | `handoff-relay` |
| Card-grid with ≥4 dense bullets | `principle-tiles` (v0.3 — always; do not require title keyword) |

## Group detection (`detect_group`)

Catalog mosaic + featured renderers call `detect_group(items, title=…)` before per-cell icon selection. When a homogeneous group is detected (≥4 items + whitelisted title noun), all cells share one kind-icon. Group types: `persona`, `team`, `test-case`, `rule`, `site`, `predicate`, `document`, `hazard`, `milestone`, `metric`.

## Provenance contract (per ben/039 §B.6)

Every output HTML carries:

- `<head>` `<meta>` tags: `generator`, `md-deck:source`, `md-deck:source-sha256`, `md-deck:built-at`, `md-deck:built-by`, `md-deck:style`, `md-deck:slide-count`.
- Top-of-file HTML comment banner with source path, SHA-256, build time, and how-to-update commands.
- `manifest.json` sidecar with full source provenance, build metadata, per-slide source anchors, components used.
- Per-slide `data-source-anchor="L<lo>-L<hi>"` attribute mapping the slide back to the source line range.
- Press `?` in the running deck to view the provenance card modal.

## Output convention (per ben/039 §B.5)

Hard rule: every deck lands at `<project-root>/assets/<source-slug>/`. Slug = source filename without extension, slugified (lowercase, hyphens). One source → one folder → one stable URL.

## What v0.3 still does NOT do

Tracked under ben/042 follow-on + ben/039 deferrals:

- **No iteration commands.** `refine`, `swap-style`, `add-variation`, `cull`, `rebuild`, `check` are spec'd but not yet implemented. Today: re-run the build script.
- **No drift detection.** Source SHA-256 is captured in head meta + manifest, but no command yet diffs current source against a deck's recorded SHA. Planned for v0.4.
- **No PDF export action wrapper.** Use `frontend-slides/scripts/export-pdf.sh` directly. Wrapping it inside md-deck would duplicate the dependency relationship.
- **No brand-pack ingestion.** v0.4 will add `/md-deck brand-from <url>` that scrapes a brand site, generates a new entry in the shared `frontend-slides/STYLE_PRESETS.md`, and emits the matching `frontend-slides/presets/<brand>.css`.
- **Variant detection still partially title-keyword-gated.** Catalog mosaics fire on row count alone; scope-iceberg, concept-canvas, and handoff-relay still require keyword hits in title or content corpus.

## Design notes

- CSS is composed at build time from two sources: `frontend-slides/viewport-base.css` (canonical viewport contract) followed by `frontend-slides/presets/<style>.css` (preset stylesheet). Cascade order is intentional — preset rules override viewport-base where needed.
- Markdown parsing is line-based, no external dependencies. Inline rendering covers bold, italic, inline code, link-text-only.
- Chrome numbering is automatic from DOM position via `runtime/deck-runtime.js` (eliminates the manual renumber pass that plagued ben/038).
- Each slide carries `data-source-anchor` so a future drift detector can ask "which slides changed when the source updated."
- Icon repository (`icons.py`) is a sibling module imported by `build.py` via a path-aware `sys.path.insert`.
- Density splits run **before** variant injection, so a 12-tile card-grid first becomes two 6-tile slides, then each gets its own variants if applicable.

## References

- Task: `tasks/ben/042-md-deck-frontend-slides-shared-layer.md` (current — shared-layer refactor)
- Prior task: `tasks/ben/039-deck-build-skill-improvements.md` (v0.2 rebuild after session-loss event)
- Predecessor build: ben/038's `assets/agentic-delivery/index.html` (Bold Signal CSS first extracted here)
- Sibling skill: `frontend-slides` — owns viewport-base.css, presets/, scripts/{export-pdf,deploy}.sh, anti-AI-slop authoring guidance
