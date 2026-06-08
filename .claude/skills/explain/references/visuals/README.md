# Visual gallery — index

Fill-in visual snippets the `explain` skill picks from when rendering an explainer. Each `.html` file is a **standalone, browser-previewable** page: open it to see the pattern, then copy only the markup between its `<!-- BEGIN SNIPPET -->` / `<!-- END SNIPPET -->` markers into the document being built.

**Two rules that make this work:**

1. **Canonical CSS lives in `../../templates/explainer.html`.** The `<style>` block in each file here is **preview-only** — it exists so the file renders on its own. The generated explainer uses the template's CSS, so a snippet pasted into a templated document is styled automatically. (If you change the palette/styles, change the template; the preview copies here are non-authoritative.)
2. **Copy the snippet, not the page.** Only the markup between the SNIPPET markers belongs in an explainer. The `<html>/<head>/<style>` wrapper and the preview note are scaffolding.

**Where "when to use which" lives:** the canonical selection guide is the **render-step selection table in `../../SKILL.md`** — that is what the skill reads to choose a visual. This file is just the snippet **store + catalog**; it does not restate the selection criteria (one source of truth, no drift). The catalog below is for human navigation.

Pick the **1–3** visuals that genuinely clarify the answer — not one of each. Prefer a clean table or prose when a diagram wouldn't add understanding.

## Catalog

**Diagrams (SVG):**

- `diagram-layered-architecture.html` — layered architecture
- `diagram-linear-flow.html` — linear flow / pipeline
- `diagram-feedback-loop.html` — flow with feedback loop
- `diagram-decision-flow.html` — decision flow
- `diagram-lifecycle.html` — lifecycle / state machine
- `diagram-sequence-handshake.html` — sequence / handshake
- `diagram-convergence-fanin.html` — convergence / fan-in
- `diagram-tree-hierarchy.html` — tree / hierarchy
- `diagram-comparison-mapping.html` — side-by-side comparison / mapping
- `diagram-matrix-quadrant.html` — 2×2 matrix / quadrant
- `diagram-swimlane.html` — swimlane

**Components (CSS):**

- `component-legend-cards.html` — legend / category cards
- `component-stat-tiles.html` — stat / metric tiles
- `component-comparison-table.html` — comparison table (✓/✗)
- `component-progress-bars.html` — status / progress bars
- `component-spec-sheet.html` — spec-sheet key–value panel
- `component-do-dont.html` — do / don't (pros / cons)
- `component-horizontal-timeline.html` — horizontal dated timeline
- `component-pull-quote.html` — pull-quote / highlight

## Adding a new visual

1. Copy an existing file of the same kind as a starting point (keeps the preview-CSS shape consistent).
2. Wrap the copy-me markup in `<!-- BEGIN SNIPPET: <name> -->` / `<!-- END SNIPPET -->`.
3. If it needs new CSS classes, add the canonical rules to `../../templates/explainer.html` `<style>` **and** mirror just those rules into the new file's preview `<style>`.
4. Add it to the catalog list above, and — with its *when-to-use* criteria — to the selection table in `../../SKILL.md` (the canonical selection guide; criteria live there only).
