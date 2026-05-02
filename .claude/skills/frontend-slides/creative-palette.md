# Creative Palette — bespoke slide patterns

This file is loaded by md-deck's creative slot generator (slots C and D in candidates.html) every time the agent is asked to author a custom slide. It grounds the agent's inventiveness in known-good patterns rather than re-deriving from scratch on every call.

Each entry is a **pattern**, not a component. Patterns are reusable visual primitives the agent can borrow, combine, and adapt to fit specific content.

---

## Slide chrome contract (inviolable)

Every creative slide MUST honor this skeleton:

```html
<section class="slide creative" data-source-anchor="<anchor>" data-creative-rationale="<one-sentence why this layout fits this content>">
    <div class="chrome">
        <span class="chrome-num">XX</span>
        <span class="brand">Project Overview</span>
        <span class="crumb">§N.M · <Section Title></span>
    </div>
    <div class="slide-content">
        <!-- Agent-authored body — full freedom inside this container -->
    </div>
</section>
```

`XX` in chrome-num is auto-renumbered by `deck-runtime.js` from DOM position. Don't hardcode a number.

The slide must fit at exactly `100vh` height with `overflow: hidden`. Use `clamp()` for all sizes — never fixed px or rem.

## Available CSS tokens (from preset)

```
--bg-primary       (e.g., #1a1a1a)        — slide background
--bg-gradient      (e.g., linear-gradient) — atmospheric backgrounds
--card-orange      (#FF5722)              — primary accent
--card-amber       (#ffb400)              — secondary accent
--card-coral       (#ff7043)              — tertiary accent
--text-primary     (#ffffff)              — primary text
--text-secondary   (rgba white 0.78)      — secondary text
--text-muted       (rgba white 0.55)      — muted text
--text-on-card     (#1a1a1a)              — text on accent backgrounds

--font-display     (Archivo Black)        — display headlines
--font-mono        (Space Mono)           — monospace meta
default body font is Space Grotesk
```

The `.reveal` class triggers a stagger-in animation on slide visibility. Use it on top-level body elements you want to appear in sequence.

---

## Pattern library

### 1. Conic-gradient donut

Parts of a whole rendered as a single CSS conic gradient — no JS, no library. Strong when the content is *one number out of N*.

```html
<div class="donut" style="background: conic-gradient(var(--card-orange) 0 38%, rgba(255,255,255,0.08) 38% 100%); width: clamp(180px, 24vw, 320px); height: clamp(180px, 24vw, 320px); border-radius: 50%; display: flex; align-items: center; justify-content: center;">
    <div style="width: 70%; height: 70%; border-radius: 50%; background: var(--bg-primary); display: flex; flex-direction: column; align-items: center; justify-content: center;">
        <div style="font-family: var(--font-display); font-size: clamp(2rem, 5vw, 4rem); color: var(--card-orange);">38%</div>
        <div style="font-size: clamp(0.7rem, 1vw, 0.9rem); color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.1em;">of baseline</div>
    </div>
</div>
```

### 2. Diagonal split (us vs. them)

Two halves of the slide separated by a diagonal `clip-path`. Each half carries one accent color. Use when the content is bipolar but you want more visual energy than `versus-split`.

```html
<div style="position: absolute; inset: 0; clip-path: polygon(0 0, 60% 0, 40% 100%, 0 100%); background: linear-gradient(135deg, rgba(255,87,34,0.12), transparent);"></div>
<div style="position: absolute; inset: 0; clip-path: polygon(60% 0, 100% 0, 100% 100%, 40% 100%); background: linear-gradient(225deg, rgba(255,180,0,0.12), transparent);"></div>
```

### 3. Drawn timeline (single-row)

Horizontal axis with dot markers. Use for date-tagged bullets that progress in a clear sequence.

```html
<div style="position: relative; height: 4px; background: linear-gradient(90deg, var(--card-orange), rgba(255,87,34,0.2)); border-radius: 2px; margin: 4rem 0;">
    <!-- N dots positioned with left: <pct>% -->
    <div style="position: absolute; left: 8%; top: -8px; width: 20px; height: 20px; border-radius: 50%; background: var(--card-orange); box-shadow: 0 0 0 4px rgba(255,87,34,0.18);"></div>
    <div style="position: absolute; left: 8%; top: 32px; font-family: var(--font-mono); font-size: 0.8em; color: var(--card-orange);">WEEK 4</div>
    <div style="position: absolute; left: 8%; top: 60px; font-size: 0.95em; color: var(--text-primary); max-width: 14ch;">Lock predicate-comparison table</div>
</div>
```

### 4. Big stat with annotated context

One oversized number, with thin lead-in lines pointing to clarifying labels. Use for measurement reveals where the number itself is the slide.

```html
<div style="display: grid; grid-template-columns: 1fr auto 1fr; gap: 2rem; align-items: center;">
    <div style="text-align: right; color: var(--text-muted);">SP6000 baseline<br><strong style="color: var(--text-primary);">100%</strong></div>
    <div style="font-family: var(--font-display); font-size: clamp(5rem, 18vw, 14rem); line-height: 1; color: var(--card-orange); letter-spacing: -0.04em;">38<span style="font-size: 0.4em; color: var(--text-secondary);">%</span></div>
    <div style="color: var(--text-muted);">SP6500 with agents<br><strong style="color: var(--card-orange);">↓ 62 pts</strong></div>
</div>
```

### 5. Layered cards (depth)

3+ cards stacked at slight offsets and rotations to suggest depth. Use when content is "the top item is the headliner, the others are the cohort."

```html
<div style="position: relative; height: 60vh;">
    <div style="position: absolute; top: 20%; left: 30%; width: 40%; transform: rotate(-3deg); background: var(--card-amber); padding: 2rem;">Card 3</div>
    <div style="position: absolute; top: 15%; left: 32%; width: 40%; transform: rotate(1deg); background: var(--card-coral); padding: 2rem;">Card 2</div>
    <div style="position: absolute; top: 10%; left: 30%; width: 40%; transform: rotate(-1deg); background: var(--card-orange); padding: 2rem;">Card 1 — headliner</div>
</div>
```

### 6. Bar-on-axis chart

Bars drawn with CSS, baseline annotation, optional reference lines. Stronger than the vanilla `bar-chart` component when the comparison is *multi-dimensional* or *signed*.

```html
<div style="display: grid; grid-template-columns: minmax(140px, 22%) 1fr; gap: 1rem 1.4rem; align-items: center;">
    <div>SP6000 baseline</div>
    <div style="position: relative; height: 24px; background: rgba(255,255,255,0.06);">
        <div style="position: absolute; inset: 0 0 0 0; width: 100%; background: var(--text-muted);"></div>
    </div>
    <div>SP6500 with agents</div>
    <div style="position: relative; height: 24px; background: rgba(255,255,255,0.06);">
        <div style="position: absolute; inset: 0; width: 38%; background: var(--card-orange);"></div>
    </div>
</div>
```

### 7. Quote with marginalia

A pulled quote in the center, with smaller commentary in the margins (left or right rail). Use when the section *is* a quote but needs context.

```html
<div style="display: grid; grid-template-columns: 1fr 14rem; gap: 3rem;">
    <blockquote style="font-family: var(--font-display); font-size: clamp(1.5rem, 3.5vw, 2.8rem); line-height: 1.2; color: var(--text-primary);">
        The 12 weeks produced equivalent IEC 62304 documentation in <em style="color: var(--card-orange); font-style: normal;">38%</em> of the calendar time.
    </blockquote>
    <aside style="font-size: 0.85em; color: var(--text-muted); border-left: 2px solid var(--card-orange); padding-left: 1rem;">
        Speed gain attributed to template execution. Defect reduction (down 21%) attributed to KOL persona reviewers.
    </aside>
</div>
```

### 8. Iceberg / above-below

Above-line: visible scope. Below-line: hidden / out-of-scope. Strong for filing carve-outs, scope reveals, "what you see / what's underneath."

```html
<div style="display: grid; grid-template-rows: 1fr 4px 1fr; height: 70vh;">
    <div style="display: flex; flex-direction: column; justify-content: flex-end; padding-bottom: 1rem;">
        <h2 style="color: var(--card-orange);">In scope</h2>
        <ul>...</ul>
    </div>
    <div style="background: var(--card-orange);"></div>
    <div style="opacity: 0.45; padding-top: 1rem;">
        <h2>Out of scope</h2>
        <ul>...</ul>
    </div>
</div>
```

### 9. Numeric ladder

Vertical stack of values from smallest to largest, each visually proportional. Use for comparative magnitudes (small / medium / large).

```html
<div style="display: flex; flex-direction: column; gap: 0.6rem;">
    <div style="font-family: var(--font-display); font-size: 2rem; color: var(--text-muted);">2 sites</div>
    <div style="font-family: var(--font-display); font-size: 4rem; color: var(--card-amber);">4 KOLs</div>
    <div style="font-family: var(--font-display); font-size: 7rem; color: var(--card-orange); line-height: 1;">38%</div>
</div>
```

### 10. Threat-mitigation pair grid

For risk content (medtech idiom): N rows of `<threat → mitigation>` with a colored connector. Inspired by agentic-delivery's `threat-x` / `delta` pattern.

```html
<div style="display: grid; gap: 1rem;">
    <div style="display: grid; grid-template-columns: 1fr auto 1fr; gap: 1rem; align-items: center;">
        <div style="background: rgba(220,40,40,0.12); border-left: 3px solid #dc2828; padding: 1rem;">Free flow on disconnect</div>
        <div style="font-size: 1.5em; color: var(--card-orange);">→</div>
        <div style="background: rgba(255,87,34,0.12); border-left: 3px solid var(--card-orange); padding: 1rem;">Anti-free-flow valve + active flow detection</div>
    </div>
    <!-- repeat -->
</div>
```

### 11. Restraint — the 3-line slide

Sometimes the most creative answer is *less*. One eyebrow, one oversized line, one supporting line. No card, no diagram, all whitespace. Use when the section's punchline is rhetorical, not informational.

```html
<div style="display: flex; flex-direction: column; justify-content: center; height: 100%; gap: 1.4rem; padding-left: 4rem;">
    <div style="font-family: var(--font-mono); font-size: 0.85rem; color: var(--text-muted); letter-spacing: 0.2em; text-transform: uppercase;">§4.1 — THE HANDOFF</div>
    <h1 style="font-family: var(--font-display); font-size: clamp(2rem, 6vw, 5rem); line-height: 1.05; max-width: 22ch; margin: 0;">Authoring isn't fully automated. <em style="color: var(--card-orange); font-style: normal;">It's a deliberate handoff.</em></h1>
    <p style="font-size: 1.1rem; color: var(--text-secondary); max-width: 50ch;">Audited, documented, enforced via session hooks.</p>
</div>
```

### 12. Marquee meta

Eyebrow + display headline with one foreground word colored. Echoes editorial-magazine layouts. Use as section-opener alternative to the numeral divider.

### 13. Numbered phases with progress dots

Three to five numbered phases laid out horizontally with the active phase visually emphasized. Suggests "you are here on a journey."

### 14. Counter-balance grid

3 columns × 1 row, but the middle column is wider (e.g., 1fr 2fr 1fr). Use when the middle item is the punchline and the flanking items are supporting.

### 15. Process loop (cyclic)

Items arranged in a circle around a central anchor — for cyclic processes (RACI loop, feedback loop, continuous improvement).

---

## Authoring guidance

- **Earn every element.** Decoration is debt. If a visual element doesn't carry meaning, drop it.
- **Stay inside the chrome contract.** Don't replace the chrome strip. Don't break the 100vh / overflow:hidden rule. Don't introduce viewport-scaling tokens — use the existing CSS variables and `clamp()`.
- **Borrow primitives, don't copy patterns whole.** A pattern from this palette is a starting point; adapt it to the specific content. The goal is custom-fit, not template-fit (we already have templates).
- **Tag your work.** Set `data-creative-rationale="<one-sentence reason this layout fits this content>"` on the `<section>` so the user can hover to see your reasoning.
- **Two slot personalities:**
  - **Slot C (bold metaphor):** lead with a visual primitive — a drawn diagram, a conic donut, a diagonal split, a layered stack, a CSS-art figure. Use color aggressively. The goal is "this slide is a *thing*, not just type."
  - **Slot D (restrained takeaway):** strip to the essential message. Oversized typography, generous whitespace, one or two visual elements max. Rhetorical force through restraint. The goal is "this slide makes you stop and read."
