# 039 — Deck-Build Skill Improvements + New `md-deck` Skill

**ID**: 039
**Created**: 2026-04-30
**Status**: Active — Backlog
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: Medium
**References**:
- [`ben/038`](038-agentic-delivery-whitepaper-deck.md) — the deck build that produced this task's evidence base
- [`ben/034`](034-agent-engineering-whitepaper.md) — the source whitepaper that proved the markdown-to-deck pattern
- `.claude/skills/frontend-slides/SKILL.md` — the upstream community skill we built on
- `.claude/skills/skill-creator/SKILL.md` — the meta-skill we'll use to author the new skill

---

## PERMANENT RULES (do not remove)

This task document is the **session-recovery point** for this work.

1. **Update at every meaningful checkpoint (HARD RULE).** After each unit of work — a redesign, a CSS pattern extraction, a template added, a heuristic tuned — tick the relevant Todo box, add a dated Changelog line, and update progress counts.
2. **Phase-end batching is OK; drift-batching is not.**
3. **A commit is not a substitute.** Git records code; this doc records the program narrative.
4. **Resume-ready before any session boundary.**
5. **Capture strategy + lessons as they happen.** `<!-- STRATEGY CONTENT: domain, topic -->` and `<!-- LESSONS LEARNED: category -->` blocks go in this doc in real time.

---

## Goals

Two parallel tracks, one task:

**Track A — Harden `frontend-slides` against the 18 issue patterns we hit in ben/038.** Every issue we re-discovered should land as either (a) a CSS/JS guardrail in the skill, (b) a template/component in `frontend-slides`, or (c) a checklist item the skill enforces. We should never solve "below-axis timeline markers don't connect to the line" by hand again.

**Track B — Author a new `md-deck` skill that builds beautiful decks from any structured markdown source.** `frontend-slides` answers "I want to build a deck"; `md-deck` answers "I have a whitepaper / overview / strategy doc, build me the deck." It should produce ben/038-quality output with one command, on any markdown file the user has, including `project-overview-md`.

**Success criteria:**

| # | Criterion |
|---|---|
| A1 | A non-Ben user authoring a deck does not hit any of the 18 issue patterns in §"Problem analysis" below. |
| A2 | `frontend-slides`'s output passes the new self-test loop (viewport-fitting, marker-axis-connection, label-collision, gradient-contrast, chrome-num-uniqueness) before delivery. |
| A3 | Every load-bearing visual pattern from ben/038 is a named, parameterized component the next deck can call by name. |
| B1 | `md-deck` accepts any structured markdown file (whitepaper, project overview, strategy doc) and produces a viewport-fitting HTML deck on first invocation. |
| B2 | The deck rebuilds from `project-overview-md` are visually polished — board-ready, not template-ish. |
| B3 | The skill is ergonomic for iteration: `/md-deck refine slide N`, `/md-deck swap-style ...`, `/md-deck add-variation slide N`. |
| B4 | Speaker notes are emitted from the source markdown automatically (callouts → speaker-note HTML comments). |
| B5 | Chrome numbering is automatic — never a manual renumber pass after a slide is added or removed. |
| B6 | Every output HTML carries traceable provenance — `<meta>` tags, top-of-file banner, and a `manifest.json` sidecar (per §B.6) — so anyone opening a deck six months later can see its source MD, build time, and how to update it. |
| B7 | Output convention enforced — all decks land at `<root>/assets/<source-slug>/` (per §B.5). Never loose at root, never mixed with hand-authored docs. |
| B8 | Drift detection works — `/md-deck rebuild` emits a what-changed-in-source summary before re-rendering; hand-edits to the HTML between builds are detected and require `--force`. |
| C1 | Brand pack is a single versioned artifact at `.brand/style-guide.json` consumed by both Track A and Track B. |
| C2 | Web scrape (`/md-deck brand-from <url>`) produces a usable brand pack on the first invocation against any reasonable corporate site (globallogic.com, arthrex.com, acme.com), with graceful degradation when fields can't be extracted. |
| C3 | Variant generator produces 4 deterministic variants (Faithful, Bolder Dark, Editorial, Tech-Forward) from any baseline brand pack. The user always has options. |
| C4 | Footer / copyright / corporate-link injection is automatic from the brand pack — no per-slide hand-typing for legal text. |
| C5 | Fallback chain (CLI override → active variant → project brand pack → project.yml → named preset → default) resolves cleanly with no surprise behavior. |
| C6 | License + robots.txt guardrails enforced — scraped logos require `--require-license-confirm` before bundling into a third-party-shipped deck. |

---

## Problem analysis — the 18 issues we hit in ben/038

Categorized so the fix surface is clear. Each row names where the fix lives in the proposed work.

### Geometry & positioning bugs (CSS / SVG layout)

| # | Issue (from ben/038 history) | Root cause | Where the fix lives |
|---|---|---|---|
| 01 | Slide 8 lens labels collided ("REGISTRIES" + "GUARDRAILS" merged) | Hand-positioned SVG text at fixed x, no collision detection | Track A — extract a `svg-axis-labels` helper that computes letter-spacing × char count and bumps neighbours, OR drop labels and use external card row by default |
| 02 | Flywheel nodes overlapped slide header / caption | Container size + radius didn't reserve space for node overhang | Track A — `flywheel` component with `radius = (container/2 − node/2 − pad)` enforced |
| 03 | Margin chart Y-axis range too wide (30–80%) — Y0/Y5 hard to differentiate | Default-to-cover-entire-range without considering visual delta | Track A — `range-chart` component with adaptive Y range (auto-zoom to data band ± padding); also document the rule of thumb |
| 04 | Spec-primacy pyramid — text inside bars was hidden by background; equal weight feeling | Color contrast not calibrated; text inside variable-width bars distorts visual hierarchy | Track A — `weighted-tier` component with text outside bar + gradient on bar; pyramid CSS class library |
| 05 | Below-axis timeline markers disconnected from the axis line | `flex-direction: column-reverse` placed dot at the bottom of the marker block | Track A — fix permanently in `event-timeline` component CSS; both above and below use plain `column` flex with HTML order varying |
| 06 | Two stacked timelines crashing into each other / closing paragraph | No automated vertical-extent calculation for marker overhang | Track A — `event-timeline` component reserves `marker-extent` padding above and below |
| 07 | PDLC nested-containers SVG too small until manually bumped to 64vh | Default `max-height` clamp too conservative | Track A — `nested-containers` component sizes to its column with sensible default |
| 08 | PDLC ring needed Adoption (9th phase) added after the fact | Original was hard-coded to 8 phases | Track A — `lifecycle-ring` component takes a phases array (any length); evenly distributes |

### Numbering / chrome / agenda drift

| # | Issue | Root cause | Where the fix lives |
|---|---|---|---|
| 09 | Chrome num spans clashed with my pyramid `<span class="num">` | I used a CSS class name that collided with the chrome convention | Track A — chrome num span uses a unique class (`chrome-num`) so renumber regexes don't false-match content classes |
| 10 | Agenda slide ranges had to be manually updated 7+ times across ben/038 | Agenda was a static HTML block; insertions/deletions didn't propagate | Track A — `agenda` component reads from a manifest (slide titles + section grouping) and renders ranges automatically; OR the renumber tool also rewrites agenda ranges from a single source |
| 11 | Whitepaper §6.5 vs §6.6 vs §6.7 numbering drifted from chrome crumbs after the whitepaper added a new section | Crumbs were hand-typed | Track A — chrome crumb takes `section_id` (e.g., `6.5.7`) from a per-slide front-matter block; rename a section, all crumbs update |
| 12 | Manual chrome renumber pass (Python script) every time a slide was added | Chrome num was a hardcoded HTML attribute | Track A — JS-time chrome numbering: each slide gets its number from its document position at load. Eliminates the renumber step entirely. |

### Density / readability per slide

| # | Issue | Root cause | Where the fix lives |
|---|---|---|---|
| 13 | Two redirects "way too dense as 1 box with a paragraph of text" — required a layered restructure | I emitted prose where structured-rows would have read better | Track B — markdown-to-slide heuristic: tables and structured lists become layered cards by default; long prose triggers a "warning: dense" lint |
| 14 | Multiple slides needed 2–3 visual variations before the user picked one | The user iterates by comparison; one-shot guesses miss | Track B — `md-deck` always produces variations for load-bearing slides (mental models, hero metaphors, multi-axis charts); the user picks; cull is a post-step |
| 15 | Initial visualizations were generic until I added analogies (lens, sealed record, NPV transformation) | No metaphor library | Track B — metaphor catalog (lens · sealed record · NPV transformation · onion-of-defenses · flywheel · funnel · iceberg · split-screen before/after) callable by name |

### Theme & visual coherence

| # | Issue | Root cause | Where the fix lives |
|---|---|---|---|
| 16 | The "agentic lens" got reused across 3 slides — manually each time | No shared SVG-symbol pattern | Track A — extract reusable SVG `<symbol>` library (`agentic-lens`, `commit-disc`, `seal`, `compass-rose`, etc.); reference via `<use>` |
| 17 | Cards "felt visually equal" when content didn't justify it | No "weight" prop on cards | Track A — `mini-card` accepts `weight = 1.0 / 0.7 / 0.4` modifier that maps to width and shadow intensity |
| 18 | Solid backgrounds vs gradients — applied gradient pass globally late in ben/038 | No design-system layer | Track A — package the Bold Signal preset's gradient palette as CSS custom-properties from the start (`--card-bg-orange-grad`, etc.); presets become drop-in |

### Cross-cutting

- **Speaker notes were HTML comments** — readable in source but invisible in the rendered deck. Track B should keep this convention but ALSO emit a "presenter view" companion artifact.
- **The user's iteration loop was always "compare 2-3 visual options."** Both tracks should make this the default, not a special request.
- **PDF export worked first try** — no fix needed, but document it as part of the deliverable surface.

---

## Track A — Concrete improvements to `frontend-slides`

### A.1 — Component library (drop-in classes)

Each is a CSS class set + optional small JS, designed so a Phase-3 generation pass can emit them by name.

| Component | Replaces (in ben/038) | Default props |
|---|---|---|
| `chrome` | hand-typed `<div class="chrome">…</div>` per slide | Auto-numbers from DOM position; reads `data-section` for the crumb |
| `agenda` | static 6-7-card grid | Reads from a `<script type="application/json" id="deck-manifest">` block at the top of the doc |
| `event-timeline` | the two timelines on Slide 8 | Fixes the below-marker bug; reserves marker-extent padding |
| `range-chart` | margin trajectory + BU breakout + cost-of-inaction | Auto-zoom Y axis; range-bar mode; categorical or numeric X |
| `dual-line-chart` | yearly view variation C | Two series + delta callouts; takeoff-marker option |
| `stacked-area` | yearly view variation B | N-layer stacked-area with optional overlay line on right axis |
| `flywheel` | the compounding flywheel | N-node circular layout; computes radius from container size; SVG dashed connectors to optional callouts |
| `lifecycle-ring` | PDLC ring | N-phase circular layout; subset arc (highlight a contiguous range); orbiting badges |
| `nested-containers` | PDLC nested rectangles | Outer + N inner subset boxes; phase-boundary arrows |
| `weighted-tier` | spec primacy pyramid | Bar widths from weight prop; text outside bar; gradient + drop-shadow |
| `comparison-card` | story-shift old/new | Two-column structured comparison from a row-based data spec |
| `severity-badge` | redirect severity tags | Med / High variants |
| `persona-card` | CFO/CRO/CEO frames | Role + quote + stat |
| `signal-card` | section closers | Already exists; needs gradient-default fix and `align-self` defaults |
| `npv-arc` | NPV transformation slide | Before-bar + arrow + after-bar with gain callout |
| `multiplier-stack` | three top-line vectors var B | Nested rectangles showing × compound |

### A.2 — SVG symbol library

A single inline `<svg style="display:none"><defs>…</defs></svg>` block at the top of every deck, with reusable symbols:

- `agentic-lens` (vertical glowing ellipse)
- `commit-disc` (artifact + glow + version metadata slot)
- `seal` (regulatory seal)
- `flow-arrow` (dashed + solid variants)
- `bulb-bare` (amber filament bulb)
- `laser-beam` (animated focused line)
- `record-disc` (vinyl-style audit-trail icon)
- `score-page` (sheet music staves)
- `gauge-meter`
- `compass-rose`

Each `<symbol>` has its own viewBox and color via `currentColor` so a `<use>` tag inherits the surrounding palette.

### A.3 — Self-test loop (lints that fail-fast)

A `scripts/lint-deck.sh` (or inline JS check on load) that flags:

| Lint | What it catches |
|---|---|
| `viewport-overflow` | Any `.slide` whose `scrollHeight > 100vh` at 1280×720 |
| `chrome-num-uniqueness` | Two `.chrome` blocks with identical num |
| `marker-axis-connection` | A timeline `.marker.below` whose dot top isn't within ±2px of the axis line |
| `label-collision` | Two SVG `<text>` elements within 8px horizontally and same y row |
| `bare-css-fn-negation` | A CSS rule with `:-(clamp|min|max)\(` (the gotcha from `frontend-slides` STYLE_PRESETS.md) |
| `gradient-text-contrast` | Display text on a gradient bg whose dark stop has < 4.5:1 contrast |
| `dense-prose-warning` | A `.mini-card .desc` longer than ~30 words (warns; doesn't fail) |
| `chrome-class-collision` | Any `<span class="num">` outside `.chrome` (the bug we hit with the pyramid) |
| `provenance-present` | `<meta name="md-deck:source">` + top-of-file generator banner + `manifest.json` all present and consistent |
| `output-path-correct` | HTML lives at `assets/<slug>/index.html` (warns if at the project root or in `docs/`) |

### A.4 — Frontmatter convention for slides

Each `<section class="slide">` accepts `data-*` attributes:

```html
<section class="slide"
         data-section="6.5.7"
         data-title="Aggregated yearly view"
         data-section-group="investment-top-line"
         data-speaker-notes="Walk left then right; the bottom line outpaces the top line is the punchline"
         data-source-anchor="L747-L770">
  …
</section>
```

This drives:
- chrome num (from DOM position)
- chrome crumb (from `data-section` + `data-title`)
- agenda manifest (from `data-section-group` aggregation)
- presenter-view companion artifact (from `data-speaker-notes`)
- per-slide provenance trace back to source markdown line range (`data-source-anchor`) → emitted into `manifest.json` `slides[].source_anchor`

Eliminates the manual renumber pass.

### A.5 — Documentation upgrade

`SKILL.md` updates: capture the 18 issue patterns above as "Common pitfalls" with the fix patterns inline. Capture the metaphor library. Capture the `data-*` frontmatter contract.

---

## Track B — New skill: `md-deck`

### B.1 — What it is

A skill that takes a structured markdown source and produces a beautiful single-file HTML deck following the same Bold Signal (or chosen) preset, in one command:

```
/md-deck build agentic-delivery-whitepaper.md \
  --style "bold-signal" \
  --target-minutes 45 \
  --variations 2
```

Output: `assets/<source-stem>/index.html` + speaker-notes companion + agenda manifest.

### B.2 — Why a new skill, not just an action on `frontend-slides`

Three reasons:

1. **Workflow shape is different.** `frontend-slides` is conversational ("ask 5 questions, generate 3 styles, pick one"). `md-deck` is one-shot from a structured source — the conversation is replaced by markdown structure.
2. **Heuristic surface is large.** Mapping `## §N — Section` → divider slide, `### N.M.K — Subsection` → content slide, table → range-chart, callout → metaphor SVG — that's a non-trivial decision tree that doesn't belong in a generic slide-builder skill.
3. **Reusability cost is asymmetric.** A user with a 2-page strategy doc shouldn't have to learn `frontend-slides`'s 6-phase conversation. A user who wants a custom-designed presentation shouldn't have to thread their content through whitepaper conventions.

`md-deck` *uses* `frontend-slides` as its component library — they compose, not compete.

### B.3 — Pipeline

```
markdown source
    ↓
[1] parse ── headings tree + tables + callouts + frontmatter
    ↓
[2] map ── heading-to-slide-type heuristic registry
    ↓
[3] enrich ── metaphor injection · variation generation · SVG selection
    ↓
[4] template ── render against `frontend-slides` Track-A component library
    ↓
[5] assemble ── single self-contained HTML + agenda + speaker-notes
    ↓
[6] validate ── Track A.3 self-test loop
    ↓
[7] deliver ── open in browser · optionally export PDF
```

### B.4 — Heuristic registry (markdown → slide)

| Markdown shape | Maps to |
|---|---|
| `## §N — <title>` | Section divider with massive numeral N |
| `### N.M <title>` | Content slide with eyebrow `§N.M` |
| `#### N.M.K <title>` | Content sub-slide |
| Top-level table with 2 columns | Comparison-card slide |
| Top-level table with 4–8 rows × 3+ columns | Compact-table slide |
| Top-level table with numeric ranges (low–high) | Range-chart slide |
| Bullet list with bold leads ("**Foo.** description") | Mini-card grid |
| `> blockquote` | Pull-quote slide |
| `[VERIFY]` / `[!metaphor name]` callouts | Metaphor SVG injection from the catalog |
| Numbered list of 3–6 items with parallel structure | Vector-stack or weighted-tier |
| H1 + subtitle + author block | Title slide |

### B.5 — Output convention (where the deck lands)

**Hard rule:** every deck output goes to `<project-root>/assets/<source-stem>/` — one folder per source markdown, never loose at the project root.

| Input | Output folder | Output files |
|---|---|---|
| `agentic-delivery-whitepaper.md` | `assets/agentic-delivery-whitepaper/` | `index.html` · `index.pdf` (after PDF export) · `presenter-notes.html` (optional) · `manifest.json` |
| `project-overview.md` | `assets/project-overview/` | `index.html` · `manifest.json` |
| `docs/project/strategy/regulatory-strategy.md` | `assets/regulatory-strategy/` | (slug from final filename, not full path) |

`<source-stem>` rule: filename without extension, slugified (lowercase, hyphens, no path components). Collisions are detected and the user is asked to disambiguate (e.g., `regulatory-strategy-v2/`).

The `assets/` directory is the canonical home for **rendered, source-derived artifacts** — distinct from `docs/` (authored documents) and `tools/` (executable code). One source → one folder → one stable URL.

### B.6 — Provenance metadata (the deck never forgets where it came from)

Every md-deck output **must carry traceable provenance** so anyone opening the HTML knows it is md-deck-managed and where the source is. This is the mechanism that prevents the deck from drifting silently from the markdown over time.

**B.6.1 — HTML `<head>` metadata.** Required `<meta>` tags emitted on every build:

```html
<meta name="generator" content="md-deck v<X.Y.Z>" />
<meta name="md-deck:source" content="../../agentic-delivery-whitepaper.md" />
<meta name="md-deck:source-sha256" content="<hash of source file at build time>" />
<meta name="md-deck:built-at" content="2026-04-30T18:42:11Z" />
<meta name="md-deck:built-by" content="<git user.name from project.yml>" />
<meta name="md-deck:style" content="bold-signal" />
<meta name="md-deck:slide-count" content="47" />
<meta name="md-deck:track-a-version" content="<frontend-slides component-library version>" />
```

**B.6.2 — Top-of-file HTML comment banner.** Visible the moment anyone opens the source:

```html
<!--
  ════════════════════════════════════════════════════════════════════
  Generated by md-deck — DO NOT EDIT THIS FILE BY HAND.
  ════════════════════════════════════════════════════════════════════

  Source:   agentic-delivery-whitepaper.md (sha256: 3f8a4e2c…)
  Built:    2026-04-30 18:42 UTC by Ben Xavier
  Style:    bold-signal
  Version:  md-deck v<X.Y.Z> · components v<X.Y>

  To update this deck:
    /md-deck refine slide N           — change one slide
    /md-deck rebuild                  — re-render from current source
    /md-deck export-pdf               — re-export the PDF companion

  Hand-edits will be overwritten on the next /md-deck rebuild.
  If you need a permanent change, edit the source markdown and rebuild.
  ════════════════════════════════════════════════════════════════════
-->
```

**B.6.3 — Sidecar manifest (`manifest.json`).** Machine-readable record of what was built:

```json
{
  "generator": "md-deck",
  "version": "0.3.0",
  "source": {
    "path": "../../agentic-delivery-whitepaper.md",
    "sha256": "3f8a4e2c...",
    "size_bytes": 67423,
    "modified_at": "2026-04-29T22:50:06Z"
  },
  "build": {
    "built_at": "2026-04-30T18:42:11Z",
    "built_by": "Ben Xavier <ben.xavier@globallogic.com>",
    "command": "/md-deck build agentic-delivery-whitepaper.md --style bold-signal --target-minutes 45 --variations 2"
  },
  "style": { "preset": "bold-signal", "overrides": {} },
  "slides": [
    { "n": 1,  "id": "title",          "section": null,    "title": "Agentic Engineering Delivery", "source_anchor": "L1-L9" },
    { "n": 2,  "id": "agenda",         "section": null,    "title": "How we'll build the case",     "source_anchor": "computed" },
    { "n": 3,  "id": "six-transitions","section": "1.1",   "title": "Every engineering field…",     "source_anchor": "L33-L48" },
    ...
  ],
  "components_used": ["chrome", "agenda", "event-timeline", "range-chart", ...],
  "track_a_version": "0.4.1"
}
```

**B.6.4 — Drift detection.** On every `/md-deck rebuild` (or via a scheduled `/md-deck check` action):

1. Compute current source-md sha256.
2. Compare to `manifest.json` → `source.sha256`.
3. If different → emit a one-line summary of WHAT changed in the source (which `## §` sections, which tables, etc.) before regenerating, so the user sees what slide(s) will change.
4. If the user has edited the HTML by hand since the last build (detect via deck content sha256 mismatch from a recorded build hash), warn loudly and require `--force` to overwrite.

**B.6.5 — `View Source` keyboard shortcut.** Press `?` in the deck → modal showing the provenance card (source path, build time, style, link to source MD). Lightweight; just reads from the meta tags.

**Why this matters.** Six months from now, someone opens an HTML deck off a colleague's laptop, doesn't know its origin, edits a number, and ships it. The provenance contract makes that impossible to do silently — the meta tags + banner + sidecar + drift detection together keep the source-of-truth invariant intact.

### B.7 — Project-overview-md → deck (worked example)

The user's specific test case. The new skill should:

1. Detect that `project-overview.md` is a project-overview shape (different schema than a whitepaper).
2. Apply the `project-overview` template variant — typically: title, agenda, mission/scope, scope-out, architecture, milestones, team, risk, ask.
3. Render with the same Bold Signal palette (or auto-detect a brand from `project.yml` `theme.colors`).
4. Output to `assets/project-overview/index.html` with full provenance metadata per §B.6.
5. Produce a 10–15 slide deck on first run. User iterates from there.

### B.8 — Style-pack mechanism

Each preset (Bold Signal, Swiss Modern, Vintage Editorial, …) is a CSS custom-properties bundle plus a SVG-symbol bundle. Users can:

- Pick by name: `--style bold-signal`
- Override colors only: `--style bold-signal --accent "#0ea5e9"`
- Pull from `project.yml`: `--style auto` (reads `theme.colors` and font preferences)

The presets ship with `frontend-slides` (Track A); `md-deck` consumes them.

### B.9 — Iteration commands

| Command | Effect |
|---|---|
| `/md-deck build <md>` | Initial generation. Output lands at `assets/<slug>/index.html` (per §B.5) with full provenance metadata (per §B.6). |
| `/md-deck rebuild` | Re-render from current source. Detects source-MD drift; warns on hand-edits to the HTML. |
| `/md-deck refine <slide-N>` | Conversational refinement of one slide. Updates `manifest.json` `slides[N]`. |
| `/md-deck swap-style <preset>` | Re-render with new theme; content unchanged. |
| `/md-deck add-variation <slide-N>` | Generate 1–2 additional variations of slide N. |
| `/md-deck cull <slide-N…>` | Remove slides; auto-renumber chrome + agenda. |
| `/md-deck speaker-view` | Emit a presenter-view HTML companion in the same folder. |
| `/md-deck export-pdf` | Wraps `frontend-slides`'s `export-pdf.sh`; output at `assets/<slug>/index.pdf`. |
| `/md-deck check` | Source-vs-deck drift report. Exits non-zero if drift detected; useful in CI. |

---

## Track C — Brand pack & web-derived theming

A self-contained capability layer consumed by both `frontend-slides` (Track A) and `md-deck` (Track B). The product is a versioned **brand pack** — a single JSON artifact that defines colors, typography, logo, footer / legal text, and corporate-link metadata for a project. The skill can derive a baseline brand pack from a website via scraping, then generate bolder variants the user picks from.

### C.1 — Current state (today)

- `frontend-slides` ships with 12 named visual presets (Bold Signal, Swiss Modern, etc.). Selection is conversational.
- `project.yml` does **not** currently carry a brand block. Theme overrides are manual edits to inline `<style>` `:root` custom properties.
- No scrape mechanism. No project-level brand persistence. Logo / copyright / corporate-link injection is per-slide hand-typing.
- Result on ben/038: every brand-adjacent decision (orange accent, "Agentic Delivery" brand string in chrome, no logo, no footer) was a hand decision repeated per slide. A re-skin to GlobalLogic-themed colors would have been a multi-edit pass.

### C.2 — The brand pack — single source of truth

Lives at **`<root>/.brand/style-guide.json`** (versioned with the project). One file. Both Track A and Track B read from it.

```json
{
  "version": "1.0.0",
  "name": "GlobalLogic — corporate",
  "derived_from": {
    "url": "https://www.globallogic.com",
    "scraped_at": "2026-04-30T19:14:02Z",
    "sha256": "<scrape result hash>",
    "user_overrides": ["accent_primary", "background_mode"]
  },
  "colors": {
    "background": "#0a0a0a",
    "background_mode": "dark",
    "surface": "#171a21",
    "text_primary": "#ffffff",
    "text_secondary": "#9aa0aa",
    "text_muted": "#5a606a",
    "accent_primary": "#FF5722",
    "accent_secondary": "#FFB400",
    "accent_tertiary": "#FF7043",
    "good": "#5fd97c",
    "bad":  "#ff5e7e",
    "rule": "rgba(255,255,255,0.08)"
  },
  "typography": {
    "display":   { "family": "Archivo Black",   "weight": 900, "source": "google" },
    "body":      { "family": "Space Grotesk",   "weight": 400, "source": "google" },
    "monospace": { "family": "JetBrains Mono",  "weight": 400, "source": "google" }
  },
  "logo": {
    "primary":   { "src": ".brand/logo-primary.svg",   "alt": "GlobalLogic", "max_height_px": 32 },
    "monochrome":{ "src": ".brand/logo-mono.svg",      "alt": "GlobalLogic" },
    "favicon":   { "src": ".brand/favicon.png" }
  },
  "footer": {
    "copyright": "© 2026 GlobalLogic Inc. All rights reserved.",
    "legal_lines": [
      "Confidential — internal use only",
      "Forward-looking statements subject to safe-harbor disclaimers"
    ],
    "corporate_link": { "text": "globallogic.com", "href": "https://www.globallogic.com" },
    "contact_email": "info@globallogic.com"
  },
  "presentation_defaults": {
    "preset_baseline": "bold-signal",
    "show_logo_on": ["title", "section-divider", "demo-handoff"],
    "show_footer_on": ["title", "demo-handoff"],
    "chrome_brand_string": "GlobalLogic · Agentic Delivery"
  }
}
```

### C.3 — Scrape mechanism (`/md-deck brand-from <url>`)

```
/md-deck brand-from https://www.globallogic.com
/md-deck brand-from https://www.arthrex.com
/md-deck brand-from https://acme.com --output .brand/acme-style-guide.json
```

Pipeline (each step graceful — partial scrapes still produce a usable pack):

| Step | Source | Extracts | Library |
|---|---|---|---|
| 1 | HTML `<head>` | `<title>` (brand name), `<meta name="theme-color">`, `<link rel="icon">` (favicon), Open Graph image | requests + lxml |
| 2 | CSS sweep | Top 20 most-used colors → cluster by HSL → primary/secondary/tertiary; background dominant; surface; text colors via contrast | tinycss2 + colorthief |
| 3 | Computed style sample | Headless browser visits the page, samples computed `font-family` on `h1`, `h2`, `body`, `code` | playwright (already installed for PDF export) |
| 4 | Logo discovery | `header img`, `nav img`, structured-data `Organization.logo`, common patterns (`/wp-content/uploads/*logo*`); SVG preferred over raster | playwright DOM query |
| 5 | Copyright + legal | Footer `<footer>` element text, common patterns (© / "All rights reserved" / "Privacy" / "Terms") | regex + text density |
| 6 | Contact + links | Footer + nav: corporate URL, contact email, social profiles (the `linktree` of a corporate site) | regex |
| 7 | Sanity + license | Filter out noisy CSS values, validate min-contrast, check `robots.txt` allows scraping, store provenance with timestamp + URL + sha256 | guardrails |

Output: a `style-guide.json` at `.brand/style-guide.json` (default) or user-specified path.

**Network and legal guardrails.** The skill respects `robots.txt`, sets a polite User-Agent, rate-limits, and stores the source URL + scrape timestamp in `derived_from`. The skill does **not** bundle the corporate logo into a deck shipped to a third party without confirming the user has rights to do so — a `--require-license-confirm` flag forces an interactive checkbox before bundling external logos.

### C.4 — Variant generator (`/md-deck brand-variants`)

After the baseline scrape, the skill **always** produces three additional variants alongside the scraped baseline so the user picks rather than settles. Each variant is a `style-guide-<n>.json` next to the baseline.

| Variant | Treatment | When it lands |
|---|---|---|
| **A — Faithful** | The scraped baseline. Colors and fonts match the website exactly. Conservative. | Default. Use for customer-facing decks where corporate fidelity matters. |
| **B — Bolder dark** | Background flipped to deep neutral (`#0a0a0a` or `#0e0e10`); brand primary kept; secondary/tertiary boosted in saturation; type weight bumped on display. Like the ben/038 deck. | Internal pitch decks where you want presence over fidelity. |
| **C — Editorial / restrained** | Light surface (`#faf9f7` cream); brand primary as the singular accent; serif display font swap (Fraunces / Cormorant); generous whitespace. | Strategy docs, board-room decks, longer-read formats. |
| **D — Tech-forward** | Dark base + neon accent borrowed from the secondary brand color; mono-display font (JetBrains Mono / Space Mono); grid-overlay background pattern. | Engineering audiences, technical demos, capability decks. |

Each variant is generated by **derivation rules** — e.g., "Variant B = baseline with `background_mode = 'dark'` and `accent_primary` saturated +15% and `display.weight` ≥ 800." Rules are deterministic and live in the skill source so a re-run produces the same variants.

The user picks via:
```
/md-deck brand-variants                         # generate all 4 variants from .brand/style-guide.json
/md-deck use-variant B                          # active variant for subsequent builds
/md-deck preview-variants                       # render the title slide of an existing deck under each variant for side-by-side
```

### C.5 — Footer / legal / link-back injection

Every deck built under a brand pack gets a footer + legal layer **without** the user authoring it slide-by-slide. Brand pack `footer` block drives:

- **Title slide:** logo top-left (small, `max_height_px`), copyright + "confidential" line at the bottom, corporate link inline with author meta.
- **Section dividers:** small chrome-strip footer with copyright + corporate link.
- **Demo-handoff / closing slide:** full footer block — copyright, legal lines, contact email, corporate link as a CTA.
- **All other slides:** chrome `brand` string is set from `presentation_defaults.chrome_brand_string` (no per-slide author hand-typing).
- **`<head>` `<link rel="icon">`:** favicon from brand pack.

Per-slide opt-out via `data-no-footer` attribute when needed (e.g., a hero stat slide that wants no chrome).

### C.6 — Fallback chain (where the theme actually comes from)

When `md-deck` builds a deck, it resolves the active style by walking this chain top-to-bottom:

1. **Command-line override** — `/md-deck build foo.md --style my-custom-pack.json`
2. **Active variant** — last `/md-deck use-variant <X>` choice → `.brand/style-guide-<X>.json`
3. **Project brand pack** — `.brand/style-guide.json`
4. **Project.yml brand block** — `project.yml` `theme:` (declarative, hand-edited; small block)
5. **Named preset** — `--style bold-signal` (or any `frontend-slides` preset name)
6. **Default** — `bold-signal` if nothing above resolves

The active brand pack's `derived_from` field is recorded in `manifest.json` per §B.6 so the deck's provenance includes "this is the style guide that was active when I was built."

### C.7 — Re-scrape and brand drift

`/md-deck brand-refresh <url>` re-runs the scrape, diffs against the current `.brand/style-guide.json` `derived_from.sha256`, and surfaces what changed (e.g., "their primary changed from `#FF5722` to `#E0411D`"). User chooses to accept, partial-merge, or reject. Useful when a customer rebrands.

### C.8 — Worked example: GlobalLogic

```
$ /md-deck brand-from https://www.globallogic.com
✓ Scraped 14 colors → clustered to {primary: #ED1C24, secondary: #FFB400, dark: #0a0a0a}
✓ Detected fonts: display "Founders Grotesk" (custom · cannot redistribute), body "Inter" (Google · OK)
  ⚠ Display font is licensed; substituting closest Google equivalent: "Space Grotesk"
✓ Logo extracted: .brand/logo-primary.svg (12 KB)
✓ Footer parsed: copyright + "Privacy Policy" + "Cookie Policy"
✓ Wrote .brand/style-guide.json

$ /md-deck brand-variants
✓ Generated 4 variants:
    A · faithful    — light surface, GL-red primary
    B · bolder dark — deep neutral bg, GL-red boosted, white display type
    C · editorial   — cream surface, GL-red as singular accent, Fraunces serif
    D · tech-forward — dark bg + GL-red + grid overlay, mono display

$ /md-deck use-variant B
✓ Active variant: B (bolder dark). Stored in .brand/.active

$ /md-deck build agentic-delivery-whitepaper.md
✓ Building under brand pack: GlobalLogic — corporate · variant B
✓ Output: assets/agentic-delivery-whitepaper/index.html
✓ Footer injected: title, section-dividers, demo-handoff
```

The user gets a brand-correct deck on first build. They can then `/md-deck use-variant A` to compare. The brand pack is committed; subsequent builds and rebuilds inherit it with no further input.

### C.9 — Out of scope (deliberately)

- **Animation / motion theming** — variants don't change animation timings; that's a Track A component-level concern.
- **Template variants per audience** (e.g., GlobalLogic-internal vs GlobalLogic-customer-facing) — the brand pack is one per project; per-audience cuts are a `presentation_defaults` override only, not a separate pack.
- **Non-web brand sources** — PDFs, brand guideline documents, Figma files. v1 is web-only. v2 could add `brand-from-pdf` if needed.

---

## Open questions for the user before drafting starts

1. **Should the new skill ship to the team registry (`hitachi`) or stay project-local first?**
   - Local first → faster iteration; promote when stable.
   - Registry first → other projects benefit immediately; review surface is bigger.
2. **Do we need a "preset library" on top of the 12 `frontend-slides` presets?**
   - Brand-specific presets (GlobalLogic-themed) for customer-facing decks.
   - Sub-vertical presets (HCLS-formal, BFSI-conservative, retail-bold).
3. **How much of Track A should land before Track B starts?**
   - Sequential — A1+A2+A3 first, then B uses the hardened components.
   - Parallel — B drives the requirements for A; A consolidates after the first B build.
4. **How should `project-overview-md` rebuild be validated?**
   - Side-by-side comparison against the existing PPTX overview (ben/025)?
   - Visual review only?
5. **Speaker-notes deliverable format?**
   - HTML comments only (current ben/038 convention).
   - + Markdown export.
   - + Presenter-view HTML companion.
6. **Brand-scrape policy — what's the user's appetite for "scrape and bundle"?**
   - Conservative — never bundle a scraped logo into a deck shipped externally without `--require-license-confirm` interaction (proposed default).
   - Liberal — bundle by default; log the source URL in `manifest.json` and trust the user.
   - Per-target — different policy for own-corporate (globallogic.com, liberal) vs third-party (arthrex.com, conservative).
7. **Brand-pack precedence vs `project.yml`'s `theme:` block — should the existing project.yml mechanism stay, get retired, or get auto-migrated into the new `.brand/style-guide.json`?**
   - Keep both — `project.yml` `theme:` is the lightweight declarative path for users who don't want a brand pack at all.
   - Retire — single source of truth wins; auto-migrate any existing `project.yml` `theme:` block on first `/md-deck build`.
   - Auto-migrate — bidirectional sync; either file can be edited.

---

## Todos

### Phase 1 — Track A foundation (component library + self-test)

- [ ] User answers the five open questions above (or delegates).
- [ ] Inventory every visual pattern used in ben/038. Output: `frontend-slides/components/` with one CSS+HTML+example per pattern.
- [ ] Implement automatic chrome numbering (drop manual `<span class="num">XX</span>` requirement).
- [ ] Implement `data-section` / `data-section-group` frontmatter contract.
- [ ] Implement automatic agenda generation from frontmatter manifest.
- [ ] Author the SVG `<symbol>` library (`agentic-lens`, `commit-disc`, `seal`, etc.).
- [ ] Author `scripts/lint-deck.sh` covering all 8 lints in §A.3.
- [ ] Update `frontend-slides/SKILL.md` to document the new contract and the 18 pitfalls.

### Phase 2 — Track B skill scaffold

- [ ] Run `/skill-creator new md-deck`. Locate at `.claude/skills/md-deck/`.
- [ ] Implement parser: markdown → AST (headings tree, tables, callouts, lists).
- [ ] Implement heuristic registry (§B.4) — markdown shape → slide type.
- [ ] Implement enrichment pass (metaphor catalog + variation generation).
- [ ] Implement template pass (assemble HTML using Track A components).
- [ ] Implement output-path convention (`<root>/assets/<source-slug>/`) — collision detection + slug rules from §B.5.
- [ ] Implement provenance metadata emission per §B.6 — `<meta>` tags, top-of-file banner, `manifest.json` sidecar, `data-source-anchor` per slide.
- [ ] Implement drift detection — `/md-deck rebuild` reads `manifest.json`, compares source sha256, summarizes what-changed before regenerating; hand-edit detection on the HTML side requires `--force` to overwrite.
- [ ] Implement `/md-deck check` action (CI-friendly drift report; non-zero exit on drift).
- [ ] Wire `lint-deck.sh` self-test into the skill (now includes `provenance-present` and `output-path-correct` lints).

### Phase 2.5 — Track C brand pack (parallel with Phase 2)

- [ ] Define brand pack JSON schema (formalize §C.2 example as a JSON Schema, validate on read).
- [ ] Implement `/md-deck brand-from <url>` — 7-step scrape pipeline (head, CSS sweep, computed-style sample, logo, footer, links, sanity).
- [ ] Implement license + robots.txt guardrails (polite UA, rate limit, `--require-license-confirm` flag).
- [ ] Implement variant generator — deterministic derivation rules for Faithful / Bolder Dark / Editorial / Tech-Forward.
- [ ] Implement `/md-deck use-variant <X>` and `/md-deck preview-variants`.
- [ ] Implement footer / legal / link-back injection per the brand pack `footer` block.
- [ ] Implement fallback chain resolver (CLI → active variant → project pack → project.yml theme → named preset → default).
- [ ] Implement `/md-deck brand-refresh` — re-scrape + diff against existing pack, accept/partial-merge/reject UI.
- [ ] Validate against three corporate sites: globallogic.com (anchor), arthrex.com (HCLS comparator), and one user-chosen third site.
- [ ] Document the brand pack contract + scrape pipeline in `md-deck/SKILL.md`.

### Phase 2.6 — Rebuild after session-loss event (2026-05-01)

**Context.** During an extended session that took md-deck from v0.1 → v0.2, the entire `.claude/skills/md-deck/` directory was deleted from the working tree before any of the v0.2 work was committed. The deletion was surgical (only `md-deck/`; the rest of `.claude/` was rolled back in unstaged form and recoverable from HEAD via `git restore`). Cause undetermined — likely an external `rm -rf` or sync-skills cull from another terminal/process; not from this session's tool calls. The last good-state `assets/project-overview/index.html` (169 KB, 49 slides) survived on disk and is the visual reference for the rebuild.

**What was lost (uncommitted v0.2 work):**

- `.claude/skills/md-deck/SKILL.md`
- `.claude/skills/md-deck/scripts/build.py` (~1700 lines — parse, synthesize, variant injection, render, CSS, JS, manifest writer)
- `.claude/skills/md-deck/scripts/icons.py` (~400 lines — 86 SVG icon repository, KEYWORD_REGISTRY, FALLBACK_POOL, GROUP_ICONS, detect_group, pick_group)

**What survived as reference material:**

- `assets/project-overview/index.html` — last good build, all CSS embedded, all rendered slide types visible.
- `assets/project-overview/manifest.json` — provenance sidecar with per-slide source anchors.
- This task doc (§B.1–B.9 design) and the §"Changelog" entries above.
- Browser DevTools session — still loaded with the working deck for inspection.
- Conversation transcript with every keyword fix, design decision, and screenshot review.

**Rebuild plan — what v0.2 must restore on day one (parity):**

- [ ] Re-author `.claude/skills/md-deck/SKILL.md` (skill manifest, status, usage, heuristic table, provenance contract, output convention, what-it-does-not-do, design notes, references). Keep wording aligned with §B.1–B.9.
- [ ] Re-author `scripts/icons.py` from scratch:
  - [ ] 86-icon `ICONS` dict across 11 categories — Healthcare/Clinical (stethoscope, heartbeat, heart, pill, syringe, iv-drip, dna, microscope, brain, lungs, test-tube, hospital, clipboard-medical), Regulatory/QMS (shield-check, shield, certificate, stamp, scale-justice, ribbon, signature), Engineering (gear, wrench, circuit, microchip, ruler, compass-tool, blueprint), Software (terminal, code-brackets, git-branch, git-merge, container, database, cloud, api-sync, plug, pipeline, lens), Documents/Process (document, stack-sheets, folder, archive, search, tag, calendar, timer, flag, bookmark, link), People (users, user-single, chat, megaphone, mail, handshake), Security (lock, key, fingerprint, eye-watch), Data/Analytics (chart-bar, chart-line, chart-pie, gauge, trending-up, dashboard), Workflow (check-circle, x-circle, warn, info-circle, lightning, refresh, queue, star, compass-rose, sync), AI (robot, brain-circuit, sparkles), Generic Fallback Pool (hexagon, diamond, triangle-up, circle-target, square-rounded, asterisk, ring, plus). Each is a 24×24 viewBox SVG using `currentColor`.
  - [ ] `KEYWORD_REGISTRY` (ordered list, first-match-wins), with the substring-bug fixes from this session preserved:
    - `"rate"` narrowed to `"heart-rate"` (was hijacking `strat[egy]`).
    - `"pr"` removed from the merge entry; keep only `merge`, `pull-request`, `pull request` (was hijacking `pr[actices]`, `pr[oject]`).
    - Order: `["task-first", "hard gate", "gating"] → "lock"` BEFORE `["one task", "task, one", "one file"] → "stack-sheets"` BEFORE `["session-start", "security check"] → "shield"` BEFORE `["task", "lifecycle", "active"] → "queue"`. More-specific phrases must come first so they don't get shadowed.
    - Project-specific entries placed BEFORE the generic `strateg` entry: `tracker → chart-line`, `trace-matrix → git-branch`, `dhf-manifest → compass-rose`, `advisors → users`. Otherwise the categorizer's "strategy" key for catalog items hijacks them via `name + " " + category_key`.
  - [ ] `FALLBACK_POOL` (8 generic icons) + hash-based `pick(label)` so unmapped labels still get visual variety instead of all-hexagon.
  - [ ] `GROUP_ICONS` map (10 group types: persona, team, test-case, rule, site, predicate, document, hazard, milestone, metric) and `GROUP_TITLE_HINTS` whitelist (KOL, advisor, persona, test case, rule, site, predicate, hazard, milestone, KPI, metric, team, cohort, …).
  - [ ] `detect_group(items, title, hint)` — returns group-type key when ≥4 items and (a) explicit hint OR (b) title noun match. Conservative; lexical-homogeneity (signal 3) deferred.
  - [ ] `pick_group(group_type)` returns the kind-icon SVG.
  - [ ] `list_icons()` for debugging.
- [ ] Re-author `scripts/build.py`:
  - [ ] Markdown parser — line-based, no external deps. Headings, tables, blockquotes, fenced code (dropped from output), ordered/unordered lists, paragraphs, hr, image blocks (`![alt](path)` on its own line). Inline rendering: bold, italic, inline code, link-text-only.
  - [ ] Slide synthesis — title (H1 + lead + bold meta), agenda (auto-computed from `## §N`), divider (`## N. Section`), table-slide, card-grid (bold-led bullets), list-slide, quote-slide, prose-slide, image-feature (image-block on its own line → hero on the right + prose+bullets on the left).
  - [ ] **Variant injection (multi-emit)** — `_inject_variants(slide)` returns a list:
    - Catalog tables (≥6 rows × 2 cols) emit `_make_catalog_mosaic_slides(slide)` (paginated `CATALOG_MOSAIC_PER_SLIDE = 8` items per slide with `(continued · N/M)` suffix) AND `_make_catalog_featured_slide(slide)` (3 featured cards + chip cohort).
    - Title containing `SCOPE_KEYWORDS` ("filing scope", "carve-out", "in vs out", "scope of") → `scope-iceberg` variant.
    - Title containing `TEACH_KEYWORDS` ("what X actually is", "what is", "where the … happens", "how it works") → `concept-canvas` variant.
    - Title containing `HANDOFF_KEYWORDS` ("handoff", "who does what", "human/agent", "human-agent") → `handoff-relay` variant.
    - Dense card-grid (≥4 bullets) → `principle-tiles` variant. **NEW for v0.3 (slide 6/8 fix):** require this fallback always; do not require a title keyword.
    - Numbered ordered list with bold leads (≥3 items) → `principle-tiles` AND optionally a sequential/relay variant. **NEW for v0.3.**
  - [ ] Group-detection wired into BOTH catalog renderers — `detect_group(items, title=…)` called once before the per-cell loop; if a group type is returned, ALL cells share the kind-icon.
  - [ ] Density auto-scaling for tables: tier the CSS class on the table element by rows × cols (`density-compact` ≥ 30, `density-tight` ≥ 18, `density-very-compact` ≥ 50, otherwise default).
  - [ ] Bold Signal CSS preset embedded as a single `CSS = "…"` string. Extract verbatim from the surviving `assets/project-overview/index.html` (search for `<style>` tags). Palette: `--card-orange #FF5722`, `--card-amber #FFB400`, `--card-coral #FF7043`. Title slide: clean rectangle, gradient, 6px border-radius, NO `rotate(8deg)`. Title text guard: `max-width: min(60ch, calc(100vw - 28vw - 4rem))` on h1, lead, t-meta-block. `t-meta-row` uses `display: grid` (not flex) so values wrap. Cell hover popup: absolutely-positioned overlay (`position: absolute; top/left/right: -4px`), no `transform: scale()` so neighbors don't shift. Tagline cells: `min-height: clamp(95px, 14vh, 130px)`. No section eyebrow on detail slides; KEEP the descriptive eyebrow on variant slides ("Variation A · Catalog Mosaic", etc.). Animations: laser pulses, baton swings, ring rotations, soundwave pulses, "now" marker glow.
  - [ ] Chrome auto-numbering — inline JS computes and writes slide numbers from DOM position on load (eliminates manual renumber pass).
  - [ ] Provenance emission — `<meta>` tags (`generator`, `md-deck:source`, `md-deck:source-sha256`, `md-deck:built-at`, `md-deck:built-by`, `md-deck:style`, `md-deck:slide-count`), top-of-file HTML banner with source + sha + how-to-update, `manifest.json` sidecar (full source provenance, per-slide source anchors, components used), per-slide `data-source-anchor="L<lo>-L<hi>"`, `?` key opens provenance modal.
  - [ ] Output path enforced: `<project-root>/assets/<slug>/index.html` with `<slug>` = source-filename slugified (lowercase, hyphenated, no extension).
  - [ ] CLI: `build.py <source.md> [--style bold-signal] [--output-dir custom/path/]`.
- [ ] **Commit discipline (HARD RULE for the rebuild).** After each working iteration — once a stage compiles and produces visually correct output — commit immediately. No silent in-flight v0.2.x sessions. Every screenshot the user signs off on gets a commit. The rebuild ends with v0.2 fully back AND committed.

**Rebuild plan — v0.3 work AFTER parity is restored:**

- [ ] **Slide-6/8 fix.** Broaden variant detection so card-grids with ≥4 dense bullets and numbered lists with bold leads ALWAYS get at least one variant injected (principle-tiles by default; scope-iceberg if filing/scope content; sequence/handoff if the list reads as a workflow). Do not require a title keyword to trigger any variant. Source for v0.3 design rationale: §B.4 + the slide-6/8 conversation in this task's transcript.
- [ ] **Lexical-homogeneity detection (group signal 3).** Catch homogeneous catalogs that don't have a whitelisted title noun, by checking shared name suffix / shared description-leading-noun across ≥4 items. Behind a flag initially.
- [ ] **Group-cell differentiation.** When a group icon repeats across cells, add a numbering badge or name-initial overlay so the repetition reads as "intentional series" rather than "uniform."
- [ ] **Variant-eyebrow consistency.** Every variant slide gets a "Variation [A/B] · [type]" descriptive eyebrow; detail slides get none.
- [ ] **PDF export action wrapper.** A thin `/md-deck export-pdf <slug>` wrapping `frontend-slides/scripts/export-pdf.sh`. Per the user's standing instruction (saved to memory), the build pipeline does NOT auto-export PDF — only on explicit user request.

**v0.3 — pending iteration commands (carry-over from §B.9):**

- [ ] `refine`, `swap-style`, `add-variation`, `cull`, `rebuild`, `check`.

### Phase 3 — Validation

- [ ] Re-build ben/038's deck from the whitepaper using `md-deck`. Diff against the hand-built version. Capture every divergence as a heuristic gap.
- [ ] Build a `project-overview-md` deck from scratch. Side-by-side review with the user.
- [ ] Build at least one third-party markdown source (volunteer task doc, strategy doc) to validate generality.

### Phase 4 — Polish & promotion

- [ ] Polish the iteration commands (`refine`, `swap-style`, `add-variation`, `cull`).
- [ ] Speaker-view companion artifact.
- [ ] PDF export wired through `frontend-slides`'s `export-pdf.sh`.
- [ ] Decide promotion path: local-only, hitachi registry, or upstream PR to `frontend-slides`.

### Phase 5 — Documentation & lessons

- [ ] Author `md-deck/SKILL.md` covering the heuristic registry, metaphor catalog, and example invocations.
- [ ] Add a `references/metaphor-catalog.md` with each metaphor's intended use, anti-pattern, and example.
- [ ] Capture lessons learned from ben/038 (every redirect that became a Track-A fix is a lesson worth promoting via `/lessons`).

---

## Inheritance from ben/038

The 47-slide deck at `assets/agentic-delivery/index.html` (320 KB single-file HTML, exported to a 23 MB PDF at `assets/agentic-delivery/agentic-delivery-deck.pdf`) is the evidence base. Every Track-A component should be **directly extractable from a specific slide range** in that file:

| Component | Extract from slide(s) |
|---|---|
| `chrome` | every slide |
| `agenda` | slide 02 |
| `event-timeline` | slides 7–8 |
| `range-chart` | slides 27, 35, 36, 47 (margin, firm-scale, BU breakout, cost-of-inaction) |
| `dual-line-chart` | slide 40 (yearly view C) |
| `stacked-area` | slide 39 (yearly view B) |
| `flywheel` | slide 43 (with callouts) |
| `lifecycle-ring` | slide 13 (PDLC ring with adoption phase) |
| `nested-containers` | slide 12 (PDLC nested with phase-boundary arrows) |
| `weighted-tier` | slide 17 (spec primacy pyramid v2) |
| `comparison-card` | slide 25 (story shift old/new) |
| `severity-badge` | slides 22, 23, 24 (redirect deep dives) |
| `persona-card` | slide 41 (CFO/CRO/CEO) |
| `npv-arc` | slide 28 (digital surgery NPV) |
| `multiplier-stack` | slide 30 (top-line vectors B) |
| `agentic-lens` SVG | slides 6, 9 |
| `commit-disc` SVG | slides 6, 9 |
| `seal` SVG | slide 9 |

---

## Strategy & Lessons Learned

> Captured inline above with `<!-- STRATEGY CONTENT -->` and `<!-- LESSONS LEARNED -->` markers when the work begins. Initial seed below.

<!-- STRATEGY CONTENT: development, tooling -->
**Two-skill split is the right factoring.** `frontend-slides` stays the generic conversational deck-builder. `md-deck` is the markdown-driven productivity layer that consumes `frontend-slides`'s components. They compose.

**Why:** ben/038 proved that conversational style discovery is overhead when the source is structured. The user thrashed through "build the deck" 12 turns before the conversational flow caught up to their actual content. A markdown-first skill collapses those 12 turns into one.

**How to apply:** When the user has a structured source (whitepaper, project overview, strategy doc), default to `md-deck`. When they're starting from a topic only or rough notes, default to `frontend-slides`.
<!-- END STRATEGY -->

<!-- STRATEGY CONTENT: development, operations -->
**Provenance metadata is non-negotiable for the new skill.** Every md-deck output carries `<meta name="md-deck:source">`, `<meta name="md-deck:source-sha256">`, a top-of-file generator banner with "do not hand-edit", and a `manifest.json` sidecar. Drift detection reads this on rebuild.

**Why:** Decks live longer than memory. A six-month-old HTML on a colleague's laptop with no traceable origin is the failure mode we are designing against. The provenance contract makes "where did this come from / how do I update it" answerable from the file alone, without context.

**How to apply:** No build path skips the provenance emission. Lint it (`provenance-present` in §A.3). The output-path convention (`<root>/assets/<source-slug>/`, §B.5) plus the metadata contract (§B.6) together keep the source-of-truth invariant intact across hand-offs.
<!-- END STRATEGY -->

<!-- STRATEGY CONTENT: development, commercial -->
**Brand-correct on first build is a commercial primitive, not a polish concern.** A deck that looks GlobalLogic-correct on slide 1 is sellable. A deck that looks generic-orange — no logo, no footer, wrong fonts — requires a brand pass before it leaves the building, and that brand pass is a 4-hour task per deck under the current ben/038 conventions.

**Why:** The Track C brand pack collapses the brand pass from 4 hours/deck to 0. `/md-deck brand-from https://customer.com` produces a usable scrape; `/md-deck brand-variants` gives the user three bolder treatments to pick from; the footer / copyright / corporate-link injection is automatic. The deck is brand-correct on first build, every build.

**How to apply:** Track C is a peer of Tracks A and B, not a polish layer. It gates "this deck is sellable to a customer" in a way the component library and content pipeline cannot. Sequence: A first (components are the foundation), C second (brand pack is the customer-facing shell), B third (md-deck consumes both).
<!-- END STRATEGY -->

<!-- LESSONS LEARNED: tooling, operations -->
**Commit early and often when the work lives outside HEAD.** On 2026-05-01 the entire `.claude/skills/md-deck/` directory was deleted between iterations of an extended v0.2 rebuild session — surgically, while the rest of `.claude/` was rolled back in unstaged form (recoverable from HEAD). md-deck specifically was unrecoverable from git because no commit had ever staged it. ~2000 lines of working Python (build.py + icons.py) plus a session of design decisions had to be reconstructed from the conversation transcript and the surviving rendered `index.html`.

**Why:** WSL's ext4 has no recycle bin for in-WSL deletes. Filesystem-level recovery from the WSL vhdx requires shutting WSL down and is unreliable once subsequent writes have landed. Git is the only durable safety net, and it only catches what's been staged or committed.

**How to apply:** When a skill or any non-trivial code artifact is being authored in `.claude/skills/<new-skill>/`, stage and commit after every working iteration — minimum once per "this output looks right in the browser" milestone. Use a WIP branch if needed, or atomic `git add -p` with a one-line message; do not let an evening's work sit untracked. The cost of a noisy commit history is trivial compared to the cost of reconstructing from a transcript.
<!-- END LESSONS -->

<!-- LESSONS LEARNED: tooling, design-systems -->
**Component extraction is the load-bearing investment.** The 18 issues in §"Problem analysis" are mostly NOT bugs — they're the cost of hand-rolling each slide instead of calling a named, parameterized component. Authoring time on ben/038 was ~80% on geometry math and renumbering, ~20% on actual content decisions.

**Why:** Once a component is named and parameterized (e.g., `event-timeline` knows how to position above/below markers correctly), the bug class disappears for the next deck.

**How to apply:** Track A's first deliverable should be the component library. Track B can wait — but Track A makes Track B 5× cheaper.
<!-- END LESSONS -->

---

## Resume Instructions

If a fresh session picks this up:
1. Read this file top to bottom.
2. Read `tasks/ben/038-agentic-delivery-whitepaper-deck.md` for the deck-build narrative.
3. Open `assets/agentic-delivery/index.html` in a browser; walk slides 06, 13, 17, 27, 35, 40, 43, 47 — these are the load-bearing visual patterns we need to extract.
4. Read `.claude/skills/frontend-slides/SKILL.md` and `.claude/skills/skill-creator/SKILL.md`.
5. Activate the task: `bash .claude/hooks/task-activate.sh add <SESSION_ID> 039`.
6. **Status:** Active — Backlog. The five open questions in this doc must be answered before Phase 1 component extraction begins.

---

## Changelog

- 2026-05-01: **Session-loss event + Phase 2.6 rebuild scope captured.** During an extended v0.2 work session that took md-deck from v0.1 → v0.2 (icon repository, group detection, variant injection, table density, image-feature, hover popup, eyebrow cleanup, multi-emit catalog mosaic + featured), the entire `.claude/skills/md-deck/` directory was deleted from disk before any of the work was committed. The rest of `.claude/` was rolled back in unstaged form and restored cleanly via `git restore .claude/`; md-deck was unrecoverable from git because it had never been staged. The surviving `assets/project-overview/index.html` (169 KB, 49 slides) is the visual reference. Phase 2.6 (rebuild) added with explicit parity TODOs — every keyword fix, group-detection table, CSS guard (title overflow, no-rotate, popup-hover), and substring-bug correction from the lost v0.2 must be restored before any v0.3 work begins. New HARD RULE captured: commit after every working iteration of an unstaged skill, no exceptions. Lessons-learned block added on commit discipline + WSL has no recycle bin for in-WSL deletes.
- 2026-05-02: **md-deck v0.2.0 — visual variants + table auto-scaling.** Two user-flagged issues from v0.1 addressed: (a) scrollable tables clip in PDF export, (b) defaults are text-heavy "details" mode without alternative visual treatments. **Table density auto-scaling** adds three CSS density tiers (`compact`, `tight`, `very-compact`) auto-applied per column/row count — the 15-row Skills table now fits the viewport without horizontal scroll, and PDF export captures the full table cleanly. **Metaphor catalog v1** ships three visual variant templates: `scope-iceberg` (carve-out / in-vs-out — applied to §1.2 regulatory strategy), `concept-canvas` (teaching / mental models — applied to §3.4 and §4.1), `handoff-relay` (sequential who-does-what flows — applied to §4.4 handoff table). **Auto-detection heuristics** match slide titles against keyword sets (`SCOPE_KEYWORDS`, `CONCEPT_KEYWORDS`, `HANDOFF_KEYWORDS`, `LIFECYCLE_KEYWORDS`); when a match fires, a variant slide is injected RIGHT AFTER the detail slide so the user has A/B options without editing the source markdown. Project-overview deck went from 32 → 36 slides (4 variant slides auto-injected), HTML 72 KB → 86 KB. Visual validation via chrome-devtools at 1920×1080: scope-iceberg renders with above-water filing scope (orange) + below-water out-of-scope (muted) + side-labeled in/out items; handoff-relay shows 6 color-coded sequential boxes (HUMAN orange · AGENT amber · MIXED coral); concept-canvas pairs a concentric ring SVG with 4 property cards. PDF re-exported in compact mode.
- 2026-04-30: **md-deck v0.1.0 spike landed.** End-to-end pipeline working on `project-overview.md`. Artifacts: `.claude/skills/md-deck/SKILL.md` (skill manifest), `.claude/skills/md-deck/scripts/build.py` (single-file Python builder, no external deps), `assets/project-overview/index.html` (32-slide deck, 72 KB), `assets/project-overview/manifest.json` (provenance sidecar). Components produced: 1 title · 1 agenda · 6 dividers · 9 table-slides · 11 card-grids · 3 prose · 1 list. Bold Signal preset extracted to inline CSS. Heuristic registry from §B.4 implemented end-to-end (H1 → title; H2 with `N.` prefix → divider; H3 → content slide; tables → table-slides; bold-led bullets → card-grid; quotes → quote-slides). Provenance contract from §B.6 fully shipped: meta tags, top-of-file banner, manifest.json sidecar with per-slide source anchors, `?` keyboard shortcut → provenance modal. Output convention from §B.5 enforced: `<root>/assets/<slug>/index.html`. Chrome numbering automatic via DOM-position JS (no manual renumber pass needed). Validated visually via chrome-devtools at 1920×1080: title, agenda, divider, table-slide, card-grid, list-slide all render cleanly with consistent typography and spacing. Provenance modal renders correctly on `?` keypress. PDF export wraps `frontend-slides`'s `export-pdf.sh` cleanly. Track A (component library extraction) and Track C (brand pack) still ahead — this is the v0.1 spike that proves the pipeline.

- 2026-04-30: Task created. Spun out of ben/038 at the natural stopping point — 47-slide deck shipped, 23 MB PDF exported. Core insight: ~80% of authoring time on ben/038 was geometry math + renumbering, not content. Two-track proposal: (A) harden `frontend-slides` with a component library + 10-lint self-test loop covering the 18 issue patterns, and (B) author a new `md-deck` skill that takes any structured markdown and produces a beautiful single-file HTML deck via the Track-A components. Heuristic registry and metaphor catalog defined. Project-overview-md rebuild named as the validation target.
- 2026-04-30: Skill name finalized as `md-deck` (renamed from `whitepaper-deck` — the input is any structured markdown, not whitepapers specifically). Output convention added (§B.5): every deck lands at `<root>/assets/<source-slug>/`. Provenance contract added (§B.6): `<meta>` tags, top-of-file generator banner, `manifest.json` sidecar, per-slide `data-source-anchor`, drift detection on rebuild. Two new self-test lints (`provenance-present`, `output-path-correct`) and four new success criteria (B6–B8) gating the skill on traceability and source-of-truth invariants. Strategy block captured: provenance is non-negotiable — decks live longer than memory.
- 2026-04-30: **Track C added — brand pack & web-derived theming.** Self-contained capability layer consumed by both Track A (`frontend-slides` presets) and Track B (`md-deck` builds). Single versioned artifact at `.brand/style-guide.json` carrying colors, typography, logo, footer/legal/copyright, and corporate-link metadata. `/md-deck brand-from <url>` runs a 7-step scrape pipeline (HTML head, CSS color sweep + clustering, computed-style font sample, logo discovery, footer/legal text extraction, contact + link extraction, sanity + license guardrails) — graceful degradation on partial fields. Variant generator produces 4 deterministic variants from any baseline (Faithful, Bolder Dark, Editorial, Tech-Forward) so the user always picks rather than settles. Footer / copyright / corporate-link injection is automatic per slide-class — title, dividers, and demo-handoff get the full footer block; other slides get the chrome brand string. Six-step fallback chain resolves the active style (CLI → active variant → project pack → project.yml theme → preset → default). License + robots.txt guardrails (`--require-license-confirm` flag for third-party logos). Six new success criteria (C1–C6) and Phase 2.5 todos. Two new open questions on brand-scrape policy and project.yml-theme precedence. Worked example for globallogic.com walks the full flow. Strategy block: brand-correct on first build is a commercial primitive — it gates "this deck is sellable to a customer" the way component library and content pipeline cannot.

