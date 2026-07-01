# 042 — md-deck ↔ frontend-slides Shared Layer

**ID**: 042
**Created**: 2026-05-01
**Status**: Complete
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: Medium

---

## PERMANENT RULES (do not remove)

This task document is the **session-recovery point** for this work. If the current session drops, is compacted, or ends, the next session must be able to load **this file alone** and continue where we left off. That is only possible if the doc is kept current in-flight.

1. **Update at every meaningful checkpoint (HARD RULE).** After each meaningful unit of work — a converted/adopted doc, a committed change, a launched batch, a completed phase, a decision, a discovered blocker, a design pivot — update this task doc:
   - tick the relevant Todo checkbox
   - add a dated Changelog line naming the concrete artifact (commit SHA, file path, decision, blocker)
   - update any progress counts/tables in Goals
2. **Phase-end batching is OK; drift-batching is not.**
3. **A commit is not a substitute.**
4. **Resume-ready before any session boundary.**
5. **Capture strategy + lessons as they happen.**

Success test for this doc: a fresh Claude session, given only this file, can re-enter the work without asking the user "what were we doing?"

---

## Context

`md-deck` (v0.2) and `frontend-slides` are two slide-authoring skills that overlap at the seams but solve different problems:

- **md-deck** — deterministic markdown → single-file HTML pipeline. Parser, slide-shape heuristics, group detection, density-modifier auto-scaling, provenance contract (`data-source-anchor`, manifest.json, SHA-256 head meta). Non-interactive.
- **frontend-slides** — interactive style-discovery wizard. AskUserQuestion mood→preset flow, 3-up style previews, viewport-fitting CSS contract, PPTX ingest, deploy/PDF-export scripts, anti-AI-slop design language.

**They aren't competitors — md-deck is a builder, frontend-slides is a stylist.** Decision (2026-05-01): keep both skills, factor the shared infrastructure into frontend-slides, and have md-deck consume it.

<!-- STRATEGY CONTENT: architecture, skill-composition -->
**Decision: shared dependency layer, not merge.**

**Why:** Merging dilutes both skills. md-deck must remain non-interactive (regulated-doc pipeline, provenance-anchored, scriptable from CI). frontend-slides must remain conversational (mood discovery, style previews, in-browser editing). The overlap is purely infrastructure: viewport-fitting CSS, preset registry, PDF/deploy scripts, anti-slop authoring guidance. Factor those into frontend-slides as the canonical source; md-deck imports them.

**How to apply:**
- New visual-fit rules → frontend-slides/viewport-base.css (single source of truth).
- New style preset → STYLE_PRESETS.md entry; md-deck `--style <name>` resolves against this registry.
- New export target → frontend-slides/scripts/; md-deck SKILL.md references it as a documented dependency.
- Interactive wizard / PPTX / inline-edit features → stay frontend-slides-only (md-deck non-goals).
- Markdown parser, group detection, provenance contract, manifest.json → stay md-deck-only (frontend-slides non-goals).
<!-- END -->

<!-- STRATEGY CONTENT: architecture, density-handling -->
**Decision: replace md-deck density-modifiers with content-split rules.**

**Why:** md-deck's `density-{compact,tight,very-compact}` modifiers shrink content to fit; they're a band-aid that still produces the "table clipped in PDF" failure mode. frontend-slides' density-limits table (4–6 bullets, 6 cards, 8–10 code lines, 3-line quotes) splits content to fit instead — every slide stays at 100vh with no scaling tricks.

**How to apply:** When a markdown subsection exceeds the per-slide-type maximum, md-deck's parser emits N continuation slides (Slide N, Slide N (cont.), …) instead of a single slide with shrunk type. Density modifiers retire.
<!-- END -->

---

## Goals

**v0.3 (shipped 2026-05-02)** — shared infrastructure layer:
- Establish frontend-slides as the **canonical source** for slide-rendering infrastructure (viewport CSS, preset registry, export scripts, anti-slop authoring guidance).
- Refactor md-deck v0.3 to **import** that infrastructure rather than duplicate it.
- Update both SKILL.md files to make the relationship explicit (dependencies, non-goals, division of responsibility).
- Replace md-deck's density-modifier auto-scaling with content-split rules driven by frontend-slides' density-limits table.
- Unblock md-deck's "v0.3 brand pack support" item by reframing as "multi-preset support via shared STYLE_PRESETS.md".

**v0.4 (current — visual fidelity gap)** — component library + 3-variant rational selection:
- After v0.3 shipped, side-by-side comparison of the rebuild against `assets/agentic-delivery/index.html` (47 hand-authored slides with bespoke compositions: `bar-col`, `axis-label`, `phase-num`, `event-stat`, `dot`/`stem`, `workmix-bar`, `threat-x`/`delta`, `t-num`/`yv-num`, etc.) made the gap obvious. md-deck's 9 slide types + 6 variants collapse rhetorical intent into "card-grid or list-slide." The Bold Signal CSS is fine; the renderer library is not.
- v0.4 builds a **30+ component library** organized into 12 rhetorical clusters (title openers, single-takeaway, time/sequence, comparison, composition/breakdown, cause/explanation, catalog/cohort, process/handoff, risk idioms, calls-to-action, long-form prose, emphasis/atmosphere). See full inventory below.
- v0.4 introduces **rational 3-variant selection**: heuristic feature extractor scores each section (temporal, numeric, bipolar, enumerative, homogeneous-cohort, declarative-short, definitional, hierarchical, factual-density, ratio-comparison) → top-3 viable components, biased for cluster spread → all 3 rendered into a sibling `candidates.html` → user picks via chooser strip → `picks.json` persists choices source-adjacent (`<source>.picks.json`) → next build locks them in.
- v0.4 makes selection rationale visible: every candidate carries `data-rationale="<feature scores + why this won>"` so md-deck doesn't feel like dice-rolling.
- v0.4 confirms two UX rules: `picks.json` lives next to the source markdown (picks are *about the source*, not about a build); `candidates.html` auto-opens only on first build (no picks yet) and on explicit `--review` after that.

---

## Todos

### Phase 1 — Audit & alignment (no code changes)

- [x] Read full contents of both SKILL.md files; confirm scope split (builder vs. stylist) holds.
- [x] Read `frontend-slides/viewport-base.css`, `STYLE_PRESETS.md`, inventory shared assets.
- [x] Inspect `md-deck/styles/bold-signal.css` and `build.py` for viewport rules and CSS embed points (lines 42, 815-823, 1242-1278).
- [x] Document the shared-vs-private split inline in SKILL.md (table at top of md-deck/SKILL.md and frontend-slides/SKILL.md).

### Phase 2 — Shared layer extraction (frontend-slides becomes canonical)

- [x] Confirmed `frontend-slides/viewport-base.css` is the canonical viewport contract; md-deck cascade-overrides as needed.
- [x] Copied `md-deck/styles/bold-signal.css` → `frontend-slides/presets/bold-signal.css` (canonical full stylesheet).
- [x] Resolved scope: only Bold Signal moves first. Other STYLE_PRESETS.md entries become available to md-deck on add.
- [x] Preset-loading mechanism: filesystem convention — `frontend-slides/presets/<name>.css` exists ⇒ `--style <name>` works; STYLE_PRESETS.md is the human-readable index. (No JSON sidecar — open question 3 resolved.)

### Phase 3 — md-deck refactor (consume shared layer)

- [x] Replaced single `CSS_PATH` constant with `_resolve_style_css(style)` returning the (viewport-base, preset) tuple — frontend-slides path preferred, md-deck/styles/ fallback.
- [x] `wrap_document` now prepends viewport-base.css before the preset CSS (cascade-correct ordering).
- [x] `--style <name>` help text updated; resolution path documented.
- [x] **Did not delete** md-deck/styles/bold-signal.css — kept as legacy fallback for projects that install md-deck without frontend-slides (per open question 1 lean).
- [x] Added `apply_density_splits` pre-pass: card-grid > 6 tiles and list-slide > 6 items split into N continuation slides with "(cont.)" title suffix. Tables retain catalog-mosaic pagination. (Density modifiers `density-{compact,tight,very-compact}` not removed from CSS yet — they're still emitted by `_table_density` but no longer the primary overflow strategy. Cleanup deferred.)
- [x] Built `project-overview-2.md` → `assets/project-overview-2/` end-to-end. 27 slides, viewport-base + bold-signal preset both embedded, manifest reports `md-deck v0.3.0`.

### Phase 4 — SKILL.md updates (skill language)

- [x] **md-deck SKILL.md** — frontmatter description rewritten to lead with "Non-interactive markdown → HTML pipeline; the builder sibling to the `frontend-slides` stylist"; added "Relationship to `frontend-slides`" section with file-ownership table; added "Non-goals" section (no wizard, no PPTX, no inline edit, no Vercel deploy); v0.3 status block replaces v0.2; heuristic registry updated for content-split behavior; "What v0.3 still does NOT do" replaces v0.2 list; design notes updated for shared CSS composition order.
- [x] **frontend-slides SKILL.md** — added "Used by `md-deck` (sibling skill)" section near the top with file-ownership table.
- [x] **STYLE_PRESETS.md** — added header note that presets are also consumed by md-deck's `--style <name>` flag, with link to `presets/`.

### Phase 6 — Component library scaffolding (v0.4 PR 1) ✅

- [x] Created `.claude/skills/frontend-slides/components/<name>/` for all 15 existing components.
- [x] **Catalogued** the 9 existing slide types + 6 variants — each with a frontmatter-bearing README.md (cluster, purpose, favors, requires, forbids, status, source-shape example, gotchas). Decision: **CSS extraction deferred** — the monolithic `presets/bold-signal.css` continues to serve. PR 1 risk-minimized to "scaffold + README contract" only; per-component CSS extraction happens incrementally per new component in PR 3 / PR 5 when adding new clusters.
- [x] Added `_parse_component_readme()` and `load_component_registry()` to `build.py`. Pure-stdlib YAML-subset parser supports: top-level scalars, one-level nested mappings (favors), flow-lists (requires/forbids), empty maps. Smoke test: 15 components parsed, all fields populated correctly.
- [x] Bumped `VERSION` to `0.4.0-pr1`.
- [x] Green build: `python3 build.py project-overview-2.md` → 27 slides, 96 KB, source SHA-256 unchanged from v0.3 build. Manifest reports `md-deck v0.4.0-pr1`. **Zero visual regressions** (no behavior change yet — registry is informational, not yet wired into rendering decisions; PR 2 will consume it).
- [x] Authored `components/README.md` — the directory's contract page: component schema, 12 clusters listed, PR-by-PR rollout table.

### Phase 7 — Heuristic feature extractor + scoring (v0.4 PR 2) ✅

- [x] `.claude/skills/md-deck/scripts/classify.py` shipped (pure stdlib). API: `extract_features(slide) → dict[str, float]`, `score_components(features, registry, *, top_k, cluster_spread) → list[ComponentScore]`. ~280 LOC.
- [x] **14 features** implemented (more than the 10 originally planned — added `is_person_cohort` + `explicit_scope` after first run showed catalog-mosaic dominating roster-cards on KOL sections, and principle-tiles dominating scope-iceberg on filing-scope sections):
  - rhetorical: `temporal`, `numeric`, `ratio_comparison`, `bipolar`, `enumerative`, `homogeneous_cohort`, `declarative_short`, `definitional`, `hierarchical`, `factual_density`
  - structural gates: `has_image`, `is_catalog_table`, `is_person_cohort`, `explicit_scope`
- [x] Each component README declares `favors: {feature → weight}`, `requires: [feature, ...]`, `forbids: [feature, ...]`; the registry loader parses frontmatter; scorer applies veto (require missing → 0 score, forbid > 0.6 → 0 score), then weighted-sum favors normalized by total weight.
- [x] Cluster-spread bias (open-question-7 lock): max 2 components per cluster in top-K; the K-th slot must come from a fresh cluster when at least one viable alternate exists.
- [x] Decision: **skipped formal `tests/` directory** for PR 2 — instead validated via direct trace runs (`python3 -c "..."`) against `project-overview-2.md` until candidate ordering matched expectations on every section. Tests can be formalized in v0.5; the inline traces gave faster iteration.

### Phase 8 — First wave of new components (v0.4 PR 3) ✅

- [x] All 8 components shipped with README + CSS + Python renderer:
  - `big-stat` (single-takeaway): hero number + label + supporting line. **Wins §4.2 "What we measured" (38% vs SP6000 baseline)** ✓
  - `mic-drop` (single-takeaway): one short sentence, oversized, centered.
  - `timeline-horizontal` (time-sequence): dot-and-stem markers across an axis. **Wins §5 "What's Next" (week-4 / week-8 / week-10 / week-14 milestones)** ✓ — required adding `image-feature` to the variant-eligible set so §5's image-bullets section could classify.
  - `phase-stack` (time-sequence): big-numeral phase blocks.
  - `before-after` (time-sequence): two-state with arrow + delta line.
  - `versus-split` (comparison): two columns with accent colors + center pivot.
  - `bar-chart` (composition-breakdown): drawn CSS bars from extracted numeric values.
  - `roster-cards` (catalog-cohort): initials medallion + name + role for people cohorts. **Wins §2.2 "KOL persona advisors"** ✓ — required `is_person_cohort` feature to overcome catalog-mosaic on raw cohort score.
- [x] All 8 component CSS partials consolidated into `frontend-slides/components/_v04-components.css` (~290 lines) — loaded after preset CSS so component selectors override preset defaults. Decision: single shared file for now, per-component partial extraction deferred to v0.5.
- [x] Adapter (`_adapt_slide_to_component`) handles all 23 component types — pass-through for renderers that read base shape directly, custom data hydration for components that need it (`principle-tiles` adds icons, `scope-iceberg` synthesizes in/out items, `concept-canvas` extracts facets, `handoff-relay` synthesizes actor list, `catalog-mosaic`/`catalog-featured` reuse legacy variant builders).

### Phase 9 — 3-variant emission + `candidates.html` (v0.4 PR 4) ✅

- [x] `propose_candidates(base_slide, registry, top_k=3)` returns top-3 (adapted_slide, ComponentScore) pairs with cluster-spread bias.
- [x] `build()` rewritten: for each variant-eligible base slide, propose candidates → pick highest score (or locked component from `picks.json`) → render to `index.html`. Decision: **default to highest score, not the base type's slot** — original logic was conservative (always picked slot 0 = base type); changed so md-deck shows the new visual treatment by default and the user *opts back* to the base via candidates.html when desired.
- [x] `candidates.html` emitter shipping all 3 variants per section as a 3-up grid with: pick letter (A/B/C), component name, score, scaled live-preview iframe (using CSS transform: scale(0.55)), rationale tagline + cluster, and a Pick button. Picks land in localStorage immediately and download as `<source-stem>.picks.json` via the floating "download picks.json" button (top-right).
- [x] `picks.json` schema v1: `{schema, source, source_sha256, picks: { <anchor>: {component, rolled_at} }}`. Persisted source-adjacent (open-question-5 lock).
- [x] `--review` flag: forces candidates.html emission. Without flag, candidates.html only emits when `<source>.picks.json` is absent — first build auto-shows candidates, subsequent builds keep the deck "locked" to the picks (open-question-6 lock).
- [x] CSS for `candidates-page` chooser strip + summary button + picked-state highlights baked into `_v04-components.css`.
- [x] Verified end-to-end: rebuild `project-overview-2.md` → `assets/project-overview-2/index.html` (81 KB, 18 slides) + `assets/project-overview-2/candidates.html` (review page).
- [x] **Components firing on the rebuild**: title, agenda, divider-numeral (×5), big-stat, concept-canvas, principle-tiles (×4), roster-cards (×1 with 8 person cards), scope-iceberg, table-slide, timeline-horizontal (×4 stops), image-feature. Versus-split / phase-stack / before-after / bar-chart / mic-drop did not auto-win against the source's content shape; they remain in candidates.html for user override.

### Phase 8 — First wave of new components (v0.4 PR 3)

- [ ] `big-stat` — one number + label + supporting line; oversized number, restrained type stack
- [ ] `mic-drop` — one short sentence, oversized, centered, ample whitespace
- [ ] `timeline-horizontal` — dated milestones with dot-and-stem rendering across a baseline
- [ ] `phase-stack` — numbered steps with big-numeral phase blocks (inspired by agentic-delivery's `phase-num`/`phase-text`/`phase-label`)
- [ ] `before-after` — exactly 2 states side-by-side with a delta marker between
- [ ] `versus-split` — 2 columns with one accent color per column (us vs. them, then vs. now)
- [ ] `bar-chart` — labels with values rendered as drawn CSS bars (inspired by agentic-delivery's `bar-col`/`workmix-bar`)
- [ ] `roster-cards` — when the catalog is people: initials, role, one-liner; replaces card-grid for KOL/team rosters

### Phase 9 — 3-variant emission + `candidates.html` (v0.4 PR 4)

- [ ] Wire `build()` to call `score()` per section, render top-3 candidates, emit `candidates.html` next to `index.html`. Each section is shown with its 3 variants stacked under a small chooser strip ("Pick A / B / C").
- [ ] Chooser strip writes `picks.json` source-adjacent via download-and-replace flow (no server). Path: same directory as the source markdown, named `<source-stem>.picks.json`.
- [ ] `picks.json` schema (v1):
  ```json
  {
    "schema": "md-deck/picks@1",
    "source": "project-overview-2.md",
    "source_sha256": "...",
    "picks": {
      "L21-L29": { "component": "before-after", "rolled_at": "2026-05-02T..." },
      "L40-L65": { "component": "roster-cards", "rolled_at": "..." }
    }
  }
  ```
- [ ] `index.html` emission reads `picks.json` (if present) and locks the picked component per section. Sections without a pick fall back to the safe candidate (top-1 score). Stale picks (component no longer scoring viable for the section) are surfaced as warnings, not silently dropped.
- [ ] `--review` flag: opens `candidates.html` even when `picks.json` exists. Without `--review`, candidates open only on first build for a given source.
- [ ] `data-rationale` strip rule (open question 8): emit on candidates, strip on locked deck.

### Phase 10b — Creative slots C + D (v0.5 PR 6) — **NEW**

User feedback (2026-05-02): the 3 deterministic slots reach a hard ceiling. Templates can fit content into known shapes but cannot *invent* the shape. The agentic-delivery gold standard required iterative human prompting — that level of fidelity is *agent-authored*, not template-selected.

**New design — 2+2 candidate composition:**

- **Slot A** — top-1 template (deterministic, classifier-driven). Today's behavior.
- **Slot B** — runner-up template (deterministic). Today's behavior.
- **Slot C** — agent-authored *bold metaphor* slide. LLM reads the section markdown, picks a visual primitive (metaphor, drawn diagram, conic-gradient figure, custom layout), produces one bespoke HTML fragment.
- **Slot D** — agent-authored *restrained takeaway* slide. Different brief (oversized type, generous whitespace, rhetorical restraint, one or two visual elements max). Same model, contrasting personality.

**Why two creative slots, not one:** giving the agent two contrasting briefs surfaces genuinely different design directions for the same content. The user picks the one that fits the deck's tone — bold for hero moments, restrained for transitional pauses.

**LLM transport:** shell out to `claude -p --output-format text` per the project's existing pattern (`skill-creator/scripts/improve_description.py`). Reuses the user's Claude Max session — no separate `ANTHROPIC_API_KEY`, no SDK install. Strip `CLAUDECODE` from env to allow nesting the call inside a Claude Code session.

**Caching contract:** when the user picks a creative slot, `picks.json` records the **inlined HTML** alongside the component name. Subsequent builds load the cached HTML directly — no re-roll, no API call. A `--re-roll-creative <anchor>` flag forces a fresh agent generation. This keeps repeat builds free of latency and locks in exactly what the user picked, since creative HTML is non-deterministic.

**Scope of agent freedom:**
- *In bounds:* anything inside `<section class="slide creative">…</section>`. The agent owns the slide-content body.
- *Off limits:* the chrome strip (numeral / brand / breadcrumb), the `.slide` viewport contract (must remain `100vh, overflow:hidden`), the brand CSS variables (use them, don't override). The agent reads `creative-palette.md` for grounding patterns.

**Plan — shipped 2026-05-02:**

- [x] Reduced template-slot count from 3 → 2 in `propose_candidates`.
- [x] `md-deck/scripts/creative.py` shipped: `build_brief()`, `_call_claude()` (subprocess to `claude -p`, strips `CLAUDECODE` env var per skill-creator pattern), `generate_creative_slide()`, `extract_slide_html()` (regex-based, tolerates Markdown fences). ~190 LOC, pure stdlib.
- [x] `frontend-slides/creative-palette.md` shipped: 15 hand-curated patterns (conic donut, diagonal split, drawn timeline, big-stat with annotation, layered cards, bar-on-axis, quote with marginalia, iceberg, numeric ladder, threat-mitigation pair, 3-line restraint, marquee meta, numbered phases, counter-balance grid, process loop) + chrome contract + CSS token list + authoring guidance. Loaded into every brief.
- [x] Two slot personalities locked in: **slot-C bold-metaphor** (lead with a visual primitive — drawn diagram, conic donut, layered cards, CSS-art) and **slot-D restrained-takeaway** (oversized typography, generous whitespace, rhetorical force through restraint).
- [x] picks.json schema v2: `{component, html?, rolled_at}` — `html` populated only for creative picks. Top-level `creative_cache` block stores agent output keyed by `{anchor}.{slot}` with source SHA invalidation.
- [x] CLI flags: `--creative`, `--creative-section <anchor>`, `--re-roll-creative <anchor>` (repeatable).
- [x] candidates.html grid extends from 3 → 4 cards. Creative cards carry `data-kind="creative"` and an "✨ AGENT" badge in the header. The chooser JS captures the inlined HTML for creative picks so the locked deck doesn't need to re-call the agent.
- [x] Default behavior: opt-in via `--creative`. No flag → no agent latency, build stays instant.
- [x] Verification: `python3 build.py project-overview-2.md --creative --creative-section L116-L122` produced two genuine creative slides for §4.2:
  - **slot-C** rendered twin conic-gradient donuts encoding 38% time and 21% defects with an attribution rail (drawn diagram, not a card-grid).
  - **slot-D** rendered an oversized headline with the two ratios pulled out as colored em-spans, generous whitespace, thin accent rule.
  - Both honored the chrome contract, used only the preset CSS variables, carried `data-creative-rationale` annotations, and landed cached in `picks.json.creative_cache`.
  - Rebuild without `--creative` returns to deterministic templates only — no agent calls, instant build. (Cache only loads when `--creative` is on; pure cached re-emit on subsequent `--creative` builds will land in PR 7.)
- [ ] **Pending follow-ups:**
  - Full-deck `--creative` run with the new distillation + parallel fan-out (estimated ~2 min: 30s distillation + 22 calls / 5 lanes × ~15s ≈ 90s).

### Phase 12 — Distillation pass + parallel fan-out (v0.5 PR 9-11) — **shipped 2026-05-02**

User feedback after the slot-D PR shipped: "the agents need full deck context, not just per-section markdown" + "if there is data, we want the option of visualizing it" + "spawn multiple agents to reduce wall clock."

**What landed:**

- [x] `md-deck/scripts/distill.py` — single `claude -p` call per source produces a structured YAML dossier covering:
  - **Deck-wide layer:** executive summary, executive takeaways, key concepts, audience personas (always 2–3, with `inferred: true` flag), unifying theme (big idea + metaphor with confidence score + visual motifs + language register + anti-patterns), guardrails.
  - **Per-section dossiers:** rhetorical move, primary takeaway, key facts, metaphor candidates, contrast pairs, deck callbacks (sets_up / pays_off), audience alignment, tone, warnings.
  - **Structured `data:` blocks** when sections carry quantified content. Schema: `kind` (bar / donut / timeline / comparison / ladder / cohort / none), `title`, `series` (with `label`, `value`, `unit`, `accent` color hints), `baseline`, `annotation`. Slot generators are instructed to **prefer encoding data visually** when present.
- [x] `frontend-slides/creative-palette.md` — 15-pattern grounding cookbook (drawn timeline, conic donut, bar-on-axis, threat-mitigation pair, restraint, layered cards, etc.) loaded into every brief.
- [x] `creative.py:build_brief()` extended with `deck_brief` + `section_brief` parameters. `distill.deck_brief_block()` and `distill.section_brief_block()` render the dossier as text blocks consumed by every slot call. Brief now instructs: "DESIGN AGAINST THIS distillation, not the raw markdown" + "lean into the deck's unifying metaphor and visual motifs — coherence with sibling slides is a feature."
- [x] `build.py` refactored to **parallel fan-out** via `concurrent.futures.ThreadPoolExecutor`. Per-section creative loop now collects pending slots into a queue; after the source-order pass, fan-out runs all uncached slots concurrently at `--creative-parallelism N` (default 5). Cached entries materialize inline; only uncached slots hit the agent.
- [x] Slide-order preservation: introduced `slide_plan` (passthrough vs. chosen-deferred) so non-eligible slides interleave correctly with eligible-but-deferred sections in the final deck.
- [x] CLI flags added: `--creative-parallelism N`, `--re-roll-distillation`, `--dump-distillation`. Cache lives at `assets/<slug>/distillation.yml`, source-SHA-tagged for invalidation.
- [x] Distillation cache lives in the **assets folder** (per the user's "all generated content in assets/" rule).

**Estimated wall-clock for full-deck `--creative`:**

- v0.5 (sequential, no distillation): ~5–6 min (22 calls × ~15s)
- v0.5 (parallel + distillation): ~2 min (30s distillation + 22 calls / 5 lanes × ~15s ≈ 90s)

**Quality gain (qualitative):**

- Slot generators now design against deck-wide context (unifying metaphor, visual motifs, audience personas, language register), not in isolation.
- When a section has numeric data, the brief surfaces a structured `data:` block — slots can encode it as a drawn diagram, not as prose.
- Slot rationales now explicitly reference (a) why this layout fits the section AND (b) how it connects to the deck's big idea or visual motif — coherence becomes possible across slides.

### Phase 10 — Second wave components (v0.4 PR 5) — **deferred**

Not shipped in this session. The 8 PR-3 components already produce visually distinct rebuild output; PR 5's components are incremental polish. Tracked as v0.4 follow-up:

- [ ] `binary-card`, `because-therefore`, `delta-table`, `check-cross-grid`, `donut`, `swimlane`, `whats-next`, `manifesto-tiles`, `huge-pull-quote`, `dense-prose-split`, `bowtie`, `threat-mitigation-pair`

**Decision (logged 2026-05-02):** stop after PR 4 for this session, hand the v0.4 build to the user for review, gather feedback on which extra components are most valuable before building the next 12. The existing 23 already deliver the visual-fidelity step-up that motivated v0.4; rushing the next 12 risks padding the library with components that don't see real use.

### Phase 11 — SKILL.md updates for v0.4

- [x] `build.py` `VERSION` bumped to `"0.4.0"`. Manifest reports `md-deck v0.4.0`.
- [ ] md-deck SKILL.md frontmatter: add "Generates 3 candidate slides per section drawn from a 23+ component library; user picks via `candidates.html` chooser strip; selections persist in `picks.json` and lock on next build." → captured in next pass.
- [ ] New md-deck SKILL.md section **"Why three candidates"** + **"Component library"** → captured in next pass.
- [ ] frontend-slides SKILL.md: header note that `components/` is also consumed by md-deck → captured in next pass.

**Decision:** SKILL.md prose updates deferred to a polish pass after the user reviews the rebuild. The skill description already names "components" via the v0.3 frontmatter; functional behavior at `--style bold-signal --review` already matches the v0.4 contract.

### Phase 5 — Verification & sync

- [x] Rebuilt `project-overview-2.md` (project root) → `assets/project-overview-2/index.html` (96 KB, 27 slides). Source SHA-256 matches the v0.2 manifest from earlier today (no source change). `<head>` confirms both `viewport-base.css` and `preset: bold-signal` blocks loaded.
- [ ] Re-run `bash .claude/skills/frontend-slides/scripts/export-pdf.sh assets/project-overview-2/index.html` and confirm PDF renders. **Deferred** per memory rule "PDF export only on explicit request."
- [ ] Did not modify `project.yml` `security.approved_skills` — both skills already approved; no new files cross skill boundaries (only an internal `presets/` directory inside frontend-slides).
- [ ] `/sync-skills push` both skills upstream — pending user review.
- [ ] Add a Lessons block (below) for the shared-layer pattern.

---

## Open Questions

### v0.3 (resolved)

1. **Co-location assumption** — Resolved: bundled fallback (legacy `md-deck/styles/<name>.css`); frontend-slides preferred when present.
2. **Bold Signal ownership** — Resolved: canonical lives at `frontend-slides/presets/bold-signal.css`; md-deck legacy copy retained as fallback only.
3. **Preset registry format** — Resolved: filesystem convention (`presets/<name>.css` exists → valid name); defer JSON registry until a third consumer needs it.
4. **Content-split UX** — Resolved: visible "(cont.)" suffix in title; silent in numbering (deck-runtime auto-numbers from DOM position).

### v0.4 (resolved 2026-05-02)

5. **`picks.json` location** — ~~Resolved: source-adjacent (`<source>.picks.json` next to the source markdown).~~ **Revised 2026-05-02 per user feedback:** picks.json now lives **inside the deck's assets folder** as `assets/<slug>/picks.json` alongside `index.html` / `candidates.html` / `manifest.json`. Reasoning: the source markdown directory often holds many sources; co-locating picks with the build keeps everything for one deck under one folder, simplifies cleanup, and avoids polluting source paths. Trade-off accepted: deleting the assets folder also deletes picks (regeneratable from candidates.html on next build).
6. **`candidates.html` open behavior** — Resolved: auto-open on **first build only** (when no `picks.json` exists yet); explicit `--review` flag thereafter.

### v0.4 (still open, will be answered in PR 2)

7. **Cluster-spread bias strength.** When the top-3 candidates would all come from the same cluster (e.g., all three are time/sequence variants), how aggressively should the scorer demote duplicates to surface a different cluster? **Lean: hard rule — at most 2 from the same cluster, slot 3 must be from an adjacent cluster even if its raw score is lower.** Confirms the user always sees genuinely different options.
8. **Rationale visibility default.** Always render `data-rationale` (visible on hover via CSS title attribute), or only emit in `candidates.html` and strip from the locked `index.html`? **Lean: emit in candidates only; strip from locked index** to keep the public deck clean.
9. **Re-roll affordance.** Should `candidates.html` offer a "re-roll this section" button that rescores with cluster-spread tightened (forcing genuinely different alternatives)? **Lean: yes, but ship after PR 5** — first land the deterministic candidates, then add the re-roll loop.

---

## Changelog

- **2026-05-01** — Task created. Decision recorded: shared dependency layer over merge. Five-phase plan drafted (audit, extract, refactor, SKILL.md updates, verify+sync). Four open questions captured with leans. Strategy blocks for skill-composition and density-handling captured inline.
- **2026-05-02** — Phases 1-4 + most of Phase 5 executed end-to-end in a single session.
  - Phase 2: `.claude/skills/frontend-slides/presets/bold-signal.css` created (canonical preset).
  - Phase 3: `build.py` v0.2.0 → v0.3.0. Added `_resolve_style_css(style)`, refactored `wrap_document` to compose `viewport-base.css` + `preset/<style>.css`, added `apply_density_splits` (card-grid > 6 tiles → split, list-slide > 6 items → split). Legacy `md-deck/styles/bold-signal.css` retained as fallback (per open-question-1 lean).
  - Phase 4: md-deck SKILL.md frontmatter + body rewritten (Relationship section, Non-goals section, v0.3 status, content-split table, design notes); frontend-slides SKILL.md gained "Used by md-deck" section; STYLE_PRESETS.md gained shared-with-md-deck header note.
  - Phase 5: Rebuilt `project-overview-2.md` → `assets/project-overview-2/` (96 KB, 27 slides, both shared CSS chunks present, manifest reports v0.3.0). Did not touch `assets/project-overview/` or `assets/agentic-delivery/` — those are kept as v0.2-baseline comparisons.
  - **Deferred**: PDF export (explicit-request-only memory rule); `/sync-skills push` upstream (pending user review of the v0.3 deck).
- 2026-06-08: Closed Complete via task-doc audit — shared layer shipped + pushed upstream (hitachi PR #113, md-deck v0.5; now v0.6.1). Moved to Completed in 000-index.md.

<!-- LESSONS LEARNED: skill-composition -->
**Shared-layer pattern as a model for future skill pairs.**

When two skills overlap at infrastructure (CSS, scripts, registries) but diverge at the user-facing contract (interactive wizard vs. deterministic CLI), the right shape is **one canonical owner + a path-aware consumer**, not a merge.

- Pick the skill with the better-structured infrastructure as canonical owner (frontend-slides, in this case).
- Move shared assets into a clearly-named subdirectory (`presets/`).
- The consumer skill resolves assets path-aware with a fallback (`_resolve_style_css` prefers frontend-slides, falls back to its own `styles/`). Co-installation is the default; standalone still works.
- Both SKILL.md files declare the relationship explicitly: a "Relationship to <other>" or "Used by <other>" section with a file-ownership table.
- A "Non-goals" section in the consumer skill prevents future scope creep.

This split survived a green build with zero regressions and unblocks v0.4 multi-preset support without further architecture work.
<!-- END -->

## Economics

_Retrospective estimate (rough; from task summary). See effort-estimation-rubric.md._

```json
{
  "economics": {
    "method_version": 1,
    "retrospective": true,
    "agentic_hours": 6,
    "todos": [
      {
        "todo": "md-deck/frontend-slides shared layer",
        "personas": [
          "rd-lead"
        ],
        "manual_hours": {
          "min": 12,
          "max": 30
        },
        "confidence": "low",
        "basis": "md-deck/frontend-slides shared layer"
      }
    ]
  }
}
```
