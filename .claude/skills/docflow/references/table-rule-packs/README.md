# Table Rule Packs

**Status (2026-04-21)**: Phase A scaffold under task ben/089. Stubs only — populated in Phase D.

## Purpose

Each pack defines docflow's table emission rules for one source-table structure type. The table classifier (`scripts/classify_tables.py`, written in Phase D) probes source structure (`gridSpan`/`vMerge`/cell-color from `word/document.xml`; PDF table-extraction equivalents) and returns `(table_type, emit_mode, table_pack, classify_confidence)`. Most decisions are deterministic; only ambiguous cases (semantic vs decorative gray, unclear positional intent) escalate to `agents/classify_table.md`.

This is the table-side analogue of the mermaid-rule-packs split. Today's table emission rules live in scattered places: converter.md Phase 3 default markdown tables, R1 v22 detail-tables (HTML with `<colgroup>`), T1 v25 composite tables (HTML with `colspan`/`rowspan`). Phase D consolidates these into a uniform classify-then-pack discipline.

## Pack registry

| Pack | Table type | Trigger (source probe) | Emit mode |
|------|-----------|------------------------|-----------|
| `table-md.md` | (t-1) uniform grid | No `gridSpan`, no `vMerge`, no cell color, ≤6 cols | Markdown table |
| `table-composite.md` | (t-2) composite | `gridSpan` headers OR `vMerge` rowspans OR legend in corner | HTML `<table>` with `colspan`/`rowspan` mirroring source (T1 from v25) |
| `table-colored.md` | (t-3) colored | Cell shading is semantic (risk matrix, RACI, heatmap) | HTML `<table>` with cell `style="background-color"` matching source palette |
| `table-positional.md` | (t-4) positional | Position-as-meaning grid (button-state matrix, color-key, geometric layout) | HTML `<table>` with explicit `<colgroup>` widths |
| `table-nested.md` | (t-5) nested | Multi-paragraph cells with sub-tables | HTML `<table>` with nested `<table>` inside `<td>` (R1 v22 + nested-table extension) |
| `table-as-diagram.md` | (t-6) diagram-shaped | Table used to lay out flow / region / hierarchy (not data) | Don't render as table — render as Mermaid (escalate to image classifier with type-a/b/c) |

## Conventions

- Each pack starts with a YAML frontmatter block declaring `pack_name`, `version`, `applies_to_type`, `emit_mode`.
- Pack body is ≤80 lines.
- Every pack defines: source probe signature, emission template, fidelity rules, validation gates.

## Phase 7 contract

Every emitted table carries a `<!-- TABLE-CLASSIFY: descriptor="..." type="(t-1|...|t-6)" emit-mode="(md|html|html-nested|mermaid|skip)" -->` marker. `scripts/validate_phase7.py` (Phase G) enforces:

- Every emitted `<table>` or `|...|` markdown table has a TABLE-CLASSIFY marker within 5 lines above
- Every TABLE-CLASSIFY marker's `emit-mode` is allowed by the active doc-type pack (e.g., `qms-form` allows t-4 positional; `requirement` allows t-5 nested for R1 detail tables; `trace-matrix` requires t-2 composite)
- Every t-2/t-3/t-4 emits HTML, not markdown (deterministic check on the markup that follows)

## Source for the split

R1 detail-tables: `agents/converter.md` Phase 3 → R1 section (~220 lines).
T1 composite tables: `agents/converter.md` Phase 3 → T1 section (~80 lines).
Default markdown tables: `agents/converter.md` Phase 3 → Tables section (~60 lines).

Phase D extracts and reorganizes — does not rewrite.

## Changelog

- 2026-04-21: README created during task ben/089 Phase A scaffolding.
