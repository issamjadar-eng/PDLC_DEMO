# client-pdlc — composite deck

Single-file composite presentation built mechanically from two sibling decks:

- `../agentic-delivery/index.html` — 47 slides
- `../project-overview/index.html` — 67 slides

Total candidate pool: **114 slides**. Each source slide is harvested verbatim (`<section class="slide ...">`) and re-rendered inside a `<div class="src-{deck}">` wrapper with that deck's CSS scoped to the wrapper.

> **History note**: a third source deck, `project-overview-sp6500` (27 slides), was retired in task ben/070 (2026-05-30). It originated as a md-deck test fixture (task ben/039 — "structurally diverse second source") rather than as a real portfolio program doc. All 27 of its candidates had been curated out during selection (zero kept slides in the final composite), so removing it does not change `index.html` content — only shrinks the candidate pool. The historical final-deck snapshots (`index.html`, `client-pdlc-presentation-v1.html`, `GlobalLogic_Agentic_PDLC.pdf`) are unaffected.

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

`candidate.html` shows all **106** slides in **source order** (agentic-delivery → project-overview). Each slide has only a KEEP/REMOVE toggle — no reorder controls. The topbar pill reads **PASS 1 · SELECT**.

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

Removed slides stay in `picks.json` (appended at the tail with `keep:false`) so a return trip to Pass 1 still sees the full 106-slide catalog with your keep state intact.

### Final

```
python build.py --final
```

Reads `picks.json`, emits `index.html` containing only `keep:true` slides in `order[]` sequence. Keyboard nav: Arrow keys / Space / PageUp / PageDown / Home / End.

### Round-trip rules

You can move back and forth between the two passes freely:

- **Pass 1 → Pass 2**: SELECT export preserves the kept-order if a prior `picks.json` already had one (i.e., Pass 2's earlier ordering survives a Pass 1 visit). Only the `keep` field is updated.
- **Pass 2 → Pass 1**: REORDER export writes the kept slides in your chosen order, then appends removed slides at the tail with `keep:false`. On the next `--candidate` build, all 106 slides reappear in source order with the correct keep state.
- **Resetting**: delete `picks.json` to start from scratch (all keep, source order).

Both `picks.json` and `index.html` are git-committable. The final deck is fully regenerable from `picks.json` + the source decks.

## File map

| File | Generator | Committable | Notes |
|---|---|---|---|
| `build.py` | hand-authored | ✓ | Single Python script; stdlib-only. |
| `candidate.html` | `build.py --candidate` (Pass 1) or `build.py --reorder` (Pass 2) | ✓ | Same path; the two passes overwrite it in place. ~550 KB in SELECT mode (106 slides), shrinks in REORDER mode (kept slides only). |
| `picks.json` | exported from `candidate.html` | ✓ | Curation state — schema `client-pdlc/picks@1`. |
| `index.html` | `build.py --final` | ✓ | The final deliverable. Contains only kept slides, no curation chrome. |

## picks.json schema (`client-pdlc/picks@1`)

```json
{
  "schema": "client-pdlc/picks@1",
  "sources": {
    "agentic-delivery": "../agentic-delivery/index.html",
    "project-overview": "../project-overview/index.html"
  },
  "order": [
    {"src": "project-overview", "idx":  0, "keep": true },
    {"src": "agentic-delivery", "idx": 12, "keep": false}
  ]
}
```

The `order` array is the source of truth — sequence == final slide sequence; removed slides stay in the list (with `keep:false`) so they can be flipped back on without losing position.

## What the build does

- **Parses** each source `<index.html>`: extracts the `<style>` block, all `<section class="slide ...">` containers, and any `<link>` tags (Google Fonts etc.).
- **Drops** each source's inline `<script>` (per-deck nav handlers conflict if combined) and body-level chrome (`.progress-bar`, `.nav-dots`, `.keyboard-hint`).
- **CSS-scopes** every source rule: `.foo { ... }` → `.src-{deck} .foo { ... }`. Top-level `body`/`html`/`:root` selectors are remapped to `.src-{deck}` so the scope wrapper plays the role of the page root. `@media` / `@supports` recurse; `@keyframes` / `@font-face` left intact.
- **Stamps `visible`** on every `<section class="slide ...">` — source decks gate `.reveal` animations on `.slide.visible`, normally added by IntersectionObserver. Static stamping lands every element at its post-animation state without needing the deck's runtime JS.
- **Rewrites** image src paths that point into a sibling asset folder (no active rewrites since the sp6500 source was retired in ben/070; the `IMG_REWRITES` dict in `build.py` remains as the extension point).

## Limitations

- No thumbnail / grid view in `candidate.html` — slides render at native size in a vertical scroll. 106 × ~900px ≈ 95k px of scroll. Use browser zoom-out for an overview.
- The candidate page is single-user single-browser. Curation state lives in `localStorage` until you Export.
- This pipeline is HTML-to-HTML only. It is **not** a `/md-deck` action — there's no markdown source, no `data-source-anchor` round-trip, no theme harmonization between source decks. Each slide carries forward exactly the look it had in its source deck.

## Changelog

- 2026-07-21 — **PDF glow-shadow fix** (task ben/106). The real culprit behind "orange blocking larger in the PDF": big-blur glow shadows (e.g. `.signal-card`'s `0 30px 80px` orange `box-shadow`). Some PDF viewers — macOS Preview included — rasterize Chrome's printed shadow groups as hard-edged translucent slabs painted over neighboring content, so the callout's soft halo became a giant orange rectangle covering the stat cards. `@media print` now strips `box-shadow`/`text-shadow` on everything (borders + backgrounds carry card definition on paper; no kept slide used ring-shadows, verified). PDF 8.6 → 7.3MB.
- 2026-07-21 — **PDF viewport parity fix** (task ben/106). The print pipeline pinned pages to 1400×900 while the deck is authored and reviewed at 1440×900. Because fonts/paddings sit at fixed px/rem clamp caps, the smaller print box made every fixed-size element — the orange callouts, card chrome — render proportionally larger than index.html, and the fit-to-slide script computed a different scale. `@page` is now `15in × 9.375in` (= 1440×900 @ 96dpi) and the export window `--window-size=1440,900`, so the PDF is pixel-proportional to the browser view (verified pages 4, 12, 34 against live measurements).
- 2026-07-21 — **Deck-review round 2** (task ben/106). Removed the "Two programs" proof slide (AD 19) and the lessons-loop prose slide (PO 34). Three more `CUSTOM_REPLACES` slides: **operating-rules** (two-page card grid → one 3×3 slide, all nine rules), **skills-catalog** (6-row playbook mosaic → the full 35-skill roster in five grouped name-chip columns), **adds-up-to** (two-page grid → one slide, all seven by-construction properties + the compliance-as-toolchain-property takeaway). Final deck 54 → **50 slides**; candidate + PDF (8.7MB) regenerated, page-verified.
- 2026-07-21 — **Deck-review fixes** (task ben/106, user review round 1). New `CUSTOM_REPLACES` mechanism: a kept anchor slide is consumed and a bespoke authored deco slide is emitted in its place. Three custom slides: **key-deliverables** (tile grid → pathway-rail illustration: Q-Sub → 510(k) → PCCP standing on the trace-matrix + risk-file evidence backbone), **skills-overview** (three-page catalog mosaic → one slide, 14 load-bearing skills grouped AUTHOR / VERIFY / OPERATE), **agents-overview** (two-page mosaic → one slide, four advisor groups + the same-agents-two-runtimes takeaway folded in). "Cost of waiting" (AD 6) and "The invariant" (AD 16) callouts centered and width-matched to their card rows (`align-self: center; max-width 1200px` — pixel-verified 120..1320). Fixed a latent duplicate-dict-key hazard in SLIDE_PATCHES (two `("agentic-delivery", 16)` entries — last-wins silently dropped the first). Final deck 57 → **54 slides**; PDF regenerated (9.5MB, page-verified).
- 2026-07-20 — **Gap-assessment corrections** (task ben/106). Four-agent assessment (skills coverage / console drift / narrative / styling) drove a coordinated fix pass. Upstream: md-deck 0.6.2 fixed a head-slide-loss bug (density-split parts shared a slug; the section machinery dropped every over-limit card-grid's head slide, leaving orphaned "(cont.)" fragments) and a 60-char label-slice truncation — restoring the Operating rules / Rules / What-this-adds-up-to head slides that had silently been missing from every build since the split rules landed. Source deck rebuilt 59 → **67 slides** (restored heads + new §3.4 authoring-pipeline, §3.5 lessons-loop, §5.4 console Tasks sections); pool now **114**. picks.json remapped (title+type verified) + re-curated: +op-rules head, +rules head+cont, +adds-up head, +skills-playbook mosaic, +Key-deliverables tiles, +authoring-pipeline tiles, +lessons-loop, +AD "Two programs" proof slide. build.py: anchors 22→23/31→38/44→51, SLIDE_APPENDS 58→66, §7 gallery 11 → **12 slides** (+Tasks, fresh 1.41.0 capture), per-shot caption strips, SLIDE_PATCHES scrub (repo paths, HTML-comment sigils, Part 11 phrasing), wayfinding (3px progress bar, n/57 counters, chapter crumbs, scroll-desync fix), WCAG muted-token lift (#6b6b7d→#8a8a99), unclamped project-overview cards (hover-only text was dead in PDF), closing eyebrow → QUESTIONS & NEXT STEPS. Final deck 47 → **57 slides**; PDF regenerated (10.3MB, spot-verified).
- 2026-07-16 — **June→July refresh** (task ben/106). `project-overview.md` updated with everything since June 12 (console 1.26→1.40, risk file, submissions, value/ROI) and its deck rebuilt: 52 → **59 slides**, so the candidate pool is now **106**. `picks.json` project-overview indices auto-remapped by title ({0..15} same, 16→17, {17..50}+1, 51→58); the new Skills mosaic page 3/3 (idx 16) added to keeps; the six new console text slides (idx 52–57) left removed because the §7 screenshot gallery covers them. `build.py`: CHAPTERS anchors 21→22 / 30→31 / 43→44, SLIDE_APPENDS 51→58, §7 gallery expanded 6 → **11 slides** (adds Strategy Review, Submission Package, Gap Analysis, Value & ROI, Project Settings; Dashboards slide retitled Submission Tracker). All 11 console screenshots recaptured live at 1440×900 (console 1.40.0). Final deck 41 → **47 slides**; PDF regenerated.
