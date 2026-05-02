---
name: md-deck
description: Build a beautiful single-file HTML slide deck from any structured markdown source (whitepaper, project overview, strategy doc). v0.2 rebuild — handles title, agenda, dividers, table-slides, card-grids, list-slides, quote-slides, prose-slides, image-feature slides; auto-scales table density; injects scope-iceberg / concept-canvas / handoff-relay / principle-tiles / catalog-mosaic / catalog-featured variants; detects homogeneous groups (KOLs, test cases, rules, sites, …) and gives them a shared kind-icon. Output lands at `<root>/assets/<source-slug>/` with full provenance metadata.
---

# md-deck

Author a beautiful, single-file HTML slide deck from any structured markdown source.

## Status

- **v0.1** — proved the pipeline (parse, slide synthesis, Bold Signal HTML, provenance metadata).
- **v0.2 (current — rebuild after 2026-05-01 session-loss event)** — restoring the parity capabilities lost when `.claude/skills/md-deck/` was deleted before commit:
  - **Table density auto-scaling.** Tables sized for the slide via `density-{compact,tight,very-compact}` modifiers based on column×row count. Eliminates the "scrollable table → clipped in PDF" problem.
  - **Variant injection (multi-emit).** When a slide matches a teaching/explaining/handoff/scope/catalog heuristic, one or more visual-variant slides are auto-generated alongside the detail slide. The user gets A/B options without modifying the source markdown.
  - **Six metaphor templates:** `scope-iceberg` (carve-out / in-vs-out), `concept-canvas` (teaching / mental models), `handoff-relay` (sequential who-does-what), `principle-tiles` (dense card-grid → low-text icon grid), `catalog-mosaic` (paginated 8-per-slide grid for ≥6-row catalogs), `catalog-featured` (3 featured cards + chip cohort).
  - **Image-feature slides.** Image blocks on their own line render as a hero on the right + prose+bullets on the left.
  - **86-icon repository** (`icons.py`) covering healthcare, regulatory, engineering, software, documents, people, security, analytics, workflow, AI domains. Keyword-matched first, hash-keyed fallback so unmapped labels still get visual variety.
  - **Group detection.** When a catalog represents N instances of the same kind of thing (KOLs, advisors, personas, test cases, rules, sites, predicates, hazards, milestones, metrics), every cell shares one kind-icon and differentiates by name / accent color, not by glyph.
- **v0.3 (planned, ben/039 Phase 2.6 + Phase 2.5)** — broader variant detection (any dense card-grid or numbered list with bold leads gets at least one variant, no title-keyword required); lexical-homogeneity for group detection; group-cell numbering badges; brand-pack-aware (`/md-deck brand-from <url>`, 4 variants, footer/copyright auto-injection).

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

## Heuristic registry — markdown shape → slide type

| Markdown shape | Maps to |
|---|---|
| `# Title` + paragraph + `**Foo:** bar` meta | Title slide |
| (computed from `## §N` headings) | Agenda slide |
| `## N. Section Name` | Section divider with massive numeral N |
| `### N.M Subsection` containing a table | Table slide (density auto-scaled) |
| `### N.M Subsection` containing a 6+-row catalog table | Mosaic + featured variants auto-emitted |
| `### N.M Subsection` with a bold-led bullet list | Card-grid slide |
| `### N.M Subsection` with a regular bullet list | List slide |
| `### N.M Subsection` with a short blockquote | Quote slide |
| `### N.M Subsection` with paragraphs only | Prose slide |
| `### N.M Subsection` with a single `![alt](path)` block | Image-feature slide |
| `#### N.M.K Sub-subsection` | Same rules as `### N.M`, finer numbering |

Code blocks (`````) are dropped from output.

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

## What v0.2 still does NOT do

These are tracked under ben/039 Phase 2.6 + later phases:

- **No 18-issue-pattern guardrails yet.** Single Python script with embedded CSS. Track-A component library extraction (Phase 1) is still ahead.
- **No brand pack support.** Bold Signal preset hardcoded. Track C (Phase 2.5) will add `.brand/style-guide.json`, web scraping, variant generation, and footer/copyright injection.
- **No iteration commands.** `refine`, `swap-style`, `add-variation`, `cull`, `rebuild`, `check` are spec'd but not yet implemented. Today: re-run the build script.
- **No drift detection.** ben/039 Phase 2 todo.
- **No PDF export action wrapper.** Use `frontend-slides`'s `scripts/export-pdf.sh` directly.
- **Variant detection still title-keyword-gated** for the non-catalog cases. v0.3 will broaden this so any dense card-grid or numbered list emits at least one variant by default.

## Design notes

- The CSS is embedded in `build.py` as a single `CSS = "…"` string — extracted from the surviving v0.2 `index.html` after the session-loss event. Track A will move this out into a real component library.
- Markdown parsing is line-based, no external dependencies. Inline rendering covers bold, italic, inline code, link-text-only.
- Chrome numbering is automatic from DOM position via inline JS (eliminates the manual renumber pass that plagued ben/038).
- Each slide carries `data-source-anchor` so a future drift detector can ask "which slides changed when the source updated."
- Icon repository (`icons.py`) is a sibling module imported by `build.py` via a path-aware `sys.path.insert`.

## References

- Task: `tasks/ben/039-deck-build-skill-improvements.md`
- Predecessor: ben/038's `assets/agentic-delivery/index.html` (Bold Signal CSS extracted from here)
- Companion skill: `frontend-slides` (consumed for `export-pdf.sh`)
