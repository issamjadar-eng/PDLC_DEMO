# Articles

Long-form thought-leadership writing for this project. Each article is a self-contained markdown source plus, when applicable, a rendered PDF.

## Contents

| File | Type | Audience | Length |
|---|---|---|---|
| [`agentic-delivery-whitepaper.md`](agentic-delivery-whitepaper.md) | Executive cut | Engineering leadership, product strategy, GTM, pre-sales engineering, delivery teams | ~12,000 words / ~45 PDF pages |
| [`agentic-delivery-whitepaper.pdf`](agentic-delivery-whitepaper.pdf) | Rendered PDF of the executive cut | Same | 45 pp |
| [`agent-engineering-whitepaper.md`](agent-engineering-whitepaper.md) | Long-form source | Same, with deeper appendices on the optics build, hiring, and counterpoints | ~16,000 words |

## Rendering

The executive cut renders to PDF via the captured pipeline:

```bash
python3 scripts/render-whitepaper.py
```

The script:

1. Pre-renders Mermaid diagrams via `mmdc` (mermaid-cli 10.x) with `fontSize: 22` and `flowchart.padding: 22`. The Conductor diagram is auto-switched LR→TB at render time (wide-aspect readability fix).
2. Post-processes SVG to enlarge `<foreignObject>` heights ~30% (descender-clip fix) and assigns unique per-diagram element IDs (no `#my-svg` cross-diagram collision).
3. Substitutes mermaid blocks with inline SVG in a `<div class="mermaid-fig">` wrapper.
4. Runs pandoc with `--wrap=none` (CRITICAL — `--wrap=auto` inserts newlines inside SVG `<style>` strings and silently kills the inline CSS).
5. Strips pandoc's duplicate `<header id="title-block-header">` block.
6. Prints to PDF via headless Chrome with `--no-pdf-header-footer`.
7. Self-tests via `pdfinfo` + `pdftotext` against three sentinel strings unique to the diagrams (`"knows the piece"`, `"listens for drift"`, `"funds further"`).

The long-form whitepaper has not been wired into the render script; only the executive cut renders to PDF here.

## Conventions

- **Currency must be escaped as `\$`**, never bare `$`. Pandoc treats unescaped `$` as a math-mode delimiter; pairing crosses paragraph and section boundaries and silently fuses words. Run a document-wide sweep when introducing new currency content — the regex `(?<!\\)\$[0-9]` should return zero matches outside `\`\`\`mermaid` fences.
- **Mermaid blocks are render-time inputs.** Edit the source mermaid in the markdown; the script regenerates SVG on every run. Do not hand-edit SVG.
- **Anonymization bar.** Customer programs are referenced as `MedTech customer` / `digital surgery customer`; no K-numbers, no product names beyond demo placeholders.
- **Demo content carries the `_Demo sample data — not for clinical use._` banner** when applicable (per project CLAUDE.md). The articles in this folder are illustrative, not regulatory submission material.
- **Versioning** lives in the article frontmatter (e.g., `Version: 1.0 — 2026-04-29`). Bump on substantive content change, not on render.
- **Every README has `## Conventions` and `## Changelog` sections.** When you edit a README, add a changelog row.

## Changelog

| Date | Change | Why |
|---|---|---|
| 2026-05-01 | Folder created; whitepapers + executive PDF relocated from project root | Consolidate long-form writing under `articles/` for discoverability |
| 2026-05-01 | README authored | Document contents, render pipeline, and conventions |
