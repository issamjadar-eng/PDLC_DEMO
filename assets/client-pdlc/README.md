# client-pdlc — composite deck

Single-file composite presentation built mechanically from the three sibling decks:

- `../agentic-delivery/index.html` — 47 slides
- `../project-overview/index.html` — 52 slides
- `../project-overview-sp6500/index.html` — 27 slides

Total candidate pool: **126 slides**. Each source slide is harvested verbatim (`<section class="slide ...">`) and re-rendered inside a `<div class="src-{deck}">` wrapper with that deck's CSS scoped to the wrapper.

## Workflow — two passes

```
            ──── Pass 1 ────         ──── Pass 2 ────
            (SELECT keep/remove)     (REORDER kept)
                                                          ──── Final ────
sources ──▶ candidate.html ──▶ picks.json ──▶ candidate.html ──▶ picks.json ──▶ index.html
            (KEEP toggles)               (drag / ▲ / ▼)
```

Selection and ordering are separated into two passes so each one is a focused tool. Both passes write to the same `candidate.html` file (the build regenerates in place).

### Pass 1 — SELECT (keep / remove)

```
python build.py --candidate
```

`candidate.html` shows all **126** slides in **source order** (agentic-delivery → project-overview → project-overview-sp6500). Each slide has only a KEEP/REMOVE toggle — no reorder controls. The topbar pill reads **PASS 1 · SELECT**.

- Click **KEEP / REMOVE** per slide. Default = all KEEP.
- **Keep all** / **Remove all** sweep toggles.
- State auto-saves to `localStorage` (key: `client-pdlc/picks@1`).
- When done, click **Export picks.json**. Save the downloaded file as `assets/client-pdlc/picks.json`.

If a `picks.json` already exists when you run `--candidate`, the build preloads its keep state and ordering (so a Pass 2 reorder you've already done isn't lost when you revisit Pass 1).

### Pass 2 — REORDER

```
python build.py --reorder
```

`candidate.html` rebuilds in place showing **only the kept slides** from `picks.json`, in `order[]` sequence. No KEEP toggles. The topbar pill reads **PASS 2 · REORDER** and each slide has a position number (1 of N).

- Drag the **⋮⋮** handle, or click **▲ / ▼**, to reorder.
- **Reset order** reverts to the picks.json sequence.
- When done, click **Export picks.json**. Save over `assets/client-pdlc/picks.json`.

Removed slides stay in `picks.json` (appended at the tail with `keep:false`) so a return trip to Pass 1 still sees the full 126-slide catalog with your keep state intact.

### Final

```
python build.py --final
```

Reads `picks.json`, emits `index.html` containing only `keep:true` slides in `order[]` sequence. Keyboard nav: Arrow keys / Space / PageUp / PageDown / Home / End.

### Round-trip rules

You can move back and forth between the two passes freely:

- **Pass 1 → Pass 2**: SELECT export preserves the kept-order if a prior `picks.json` already had one (i.e., Pass 2's earlier ordering survives a Pass 1 visit). Only the `keep` field is updated.
- **Pass 2 → Pass 1**: REORDER export writes the kept slides in your chosen order, then appends removed slides at the tail with `keep:false`. On the next `--candidate` build, all 126 slides reappear in source order with the correct keep state.
- **Resetting**: delete `picks.json` to start from scratch (all keep, source order).

Both `picks.json` and `index.html` are git-committable. The final deck is fully regenerable from `picks.json` + the source decks.

## File map

| File | Generator | Committable | Notes |
|---|---|---|---|
| `build.py` | hand-authored | ✓ | Single Python script; stdlib-only. |
| `candidate.html` | `build.py --candidate` (Pass 1) or `build.py --reorder` (Pass 2) | ✓ | Same path; the two passes overwrite it in place. ~640 KB in SELECT mode (126 slides), shrinks in REORDER mode (kept slides only). |
| `picks.json` | exported from `candidate.html` | ✓ | Curation state — schema `client-pdlc/picks@1`. |
| `index.html` | `build.py --final` | ✓ | The final deliverable. Contains only kept slides, no curation chrome. |

## picks.json schema (`client-pdlc/picks@1`)

```json
{
  "schema": "client-pdlc/picks@1",
  "sources": {
    "agentic-delivery":   "../agentic-delivery/index.html",
    "project-overview":   "../project-overview/index.html",
    "project-overview-sp6500": "../project-overview-sp6500/index.html"
  },
  "order": [
    {"src": "project-overview",   "idx":  0, "keep": true },
    {"src": "agentic-delivery",   "idx": 12, "keep": false},
    {"src": "project-overview-sp6500", "idx": 26, "keep": true }
  ]
}
```

The `order` array is the source of truth — sequence == final slide sequence; removed slides stay in the list (with `keep:false`) so they can be flipped back on without losing position.

## What the build does

- **Parses** each source `<index.html>`: extracts the `<style>` block, all `<section class="slide ...">` containers, and any `<link>` tags (Google Fonts etc.).
- **Drops** each source's inline `<script>` (per-deck nav handlers conflict if combined) and body-level chrome (`.progress-bar`, `.nav-dots`, `.keyboard-hint`).
- **CSS-scopes** every source rule: `.foo { ... }` → `.src-{deck} .foo { ... }`. Top-level `body`/`html`/`:root` selectors are remapped to `.src-{deck}` so the scope wrapper plays the role of the page root. `@media` / `@supports` recurse; `@keyframes` / `@font-face` left intact.
- **Stamps `visible`** on every `<section class="slide ...">` — source decks gate `.reveal` animations on `.slide.visible`, normally added by IntersectionObserver. Static stamping lands every element at its post-animation state without needing the deck's runtime JS.
- **Rewrites** image src paths that point into a sibling asset folder (currently just `project-overview-sp6500`'s one screenshot).

## Limitations

- No thumbnail / grid view in `candidate.html` — slides render at native size in a vertical scroll. 126 × ~900px ≈ 115k px of scroll. Use browser zoom-out for an overview.
- The candidate page is single-user single-browser. Curation state lives in `localStorage` until you Export.
- This pipeline is HTML-to-HTML only. It is **not** a `/md-deck` action — there's no markdown source, no `data-source-anchor` round-trip, no theme harmonization between source decks. Each slide carries forward exactly the look it had in its source deck.
