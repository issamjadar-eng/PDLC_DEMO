---
name: frontend-design
description: |
  Create distinctive, production-grade frontend interfaces with high design quality. Use when the user asks to build, style, polish, refresh, or beautify any web UI — components, pages, artifacts, posters, dashboards, landing pages, marketing sites, internal tools, React/Vue/Svelte components, or raw HTML/CSS/JS layouts. Generates code with an intentional aesthetic point of view that avoids generic "AI slop" output (overused fonts like Inter/Roboto/Arial, purple-gradient-on-white palettes, cookie-cutter layouts).

  TRIGGER when the user wants to:
    - Build a new web UI from scratch — "build a landing page for X", "design a dashboard", "make a portfolio site", "create a React component for Y"
    - Style or refresh an existing UI — "make this look better", "give it a [aesthetic] feel", "redesign the hero", "polish this card", "tighten the typography"
    - Convert a wireframe / spec / written brief into a styled implementation
    - Author an HTML artifact (poster, invitation, one-pager, microsite) where the visual quality is the point
    - Ask Claude to "be creative" with a UI, pick a vibe, or commit to an aesthetic direction

  This skill is **distinct from `frontend-slides`** (which is for HTML slide decks specifically). Use `frontend-slides` for presentations / decks / slide-based artifacts; use `frontend-design` for everything else in the web-UI space.
version: 1
updated: 2026-06-01
license: Apache-2.0 (see LICENSE.txt) — adapted from anthropics/skills · pinned upstream SHA in .pinned-sha
---

# Frontend Design

Guide creation of distinctive, production-grade frontend interfaces that avoid generic "AI slop" aesthetics. Implement real working code with exceptional attention to aesthetic details and creative choices.

The user provides frontend requirements: a component, page, application, or interface to build. They may include context about the purpose, audience, or technical constraints.

## Design Thinking

Before coding, understand the context and commit to a BOLD aesthetic direction:

- **Purpose**: What problem does this interface solve? Who uses it?
- **Tone**: Pick an extreme — brutally minimal, maximalist chaos, retro-futuristic, organic/natural, luxury/refined, playful/toy-like, editorial/magazine, brutalist/raw, art deco/geometric, soft/pastel, industrial/utilitarian, etc. Use these for inspiration but design one that is true to the aesthetic direction.
- **Constraints**: Technical requirements (framework, performance, accessibility).
- **Differentiation**: What makes this UNFORGETTABLE? What's the one thing someone will remember?

**CRITICAL**: Choose a clear conceptual direction and execute it with precision. Bold maximalism and refined minimalism both work — the key is intentionality, not intensity.

Then implement working code (HTML/CSS/JS, React, Vue, etc.) that is:

- Production-grade and functional
- Visually striking and memorable
- Cohesive with a clear aesthetic point-of-view
- Meticulously refined in every detail

## Frontend Aesthetics Guidelines

Focus on:

- **Typography**: Choose fonts that are beautiful, unique, and interesting. Avoid generic fonts like Arial and Inter; opt instead for distinctive choices that elevate the frontend's aesthetics; unexpected, characterful font choices. Pair a distinctive display font with a refined body font.
- **Color & Theme**: Commit to a cohesive aesthetic. Use CSS variables for consistency. Dominant colors with sharp accents outperform timid, evenly-distributed palettes.
- **Motion**: Use animations for effects and micro-interactions. Prioritize CSS-only solutions for HTML. Use Motion library for React when available. Focus on high-impact moments: one well-orchestrated page load with staggered reveals (animation-delay) creates more delight than scattered micro-interactions. Use scroll-triggering and hover states that surprise.
- **Spatial Composition**: Unexpected layouts. Asymmetry. Overlap. Diagonal flow. Grid-breaking elements. Generous negative space OR controlled density.
- **Backgrounds & Visual Details**: Create atmosphere and depth rather than defaulting to solid colors. Add contextual effects and textures that match the overall aesthetic. Apply creative forms like gradient meshes, noise textures, geometric patterns, layered transparencies, dramatic shadows, decorative borders, custom cursors, and grain overlays.

NEVER use generic AI-generated aesthetics like overused font families (Inter, Roboto, Arial, system fonts), cliched color schemes (particularly purple gradients on white backgrounds), predictable layouts and component patterns, and cookie-cutter design that lacks context-specific character.

Interpret creatively and make unexpected choices that feel genuinely designed for the context. No design should be the same. Vary between light and dark themes, different fonts, different aesthetics. NEVER converge on common choices (Space Grotesk, for example) across generations.

**IMPORTANT**: Match implementation complexity to the aesthetic vision. Maximalist designs need elaborate code with extensive animations and effects. Minimalist or refined designs need restraint, precision, and careful attention to spacing, typography, and subtle details. Elegance comes from executing the vision well.

Remember: Claude is capable of extraordinary creative work. Don't hold back, show what can truly be created when thinking outside the box and committing fully to a distinctive vision.

## Supporting Files

| File | Purpose |
|------|---------|
| `README.md` | Design doc — lineage (Anthropic skills repo), Best Practices, Changelog. Not loaded by Claude during normal skill operation. |
| `LICENSE.txt` | Apache License 2.0 — preserved verbatim from upstream `anthropics/skills`. |
| `.pinned-sha` | Upstream commit SHA at fork time (provenance for `/sync-skills`-style reconciliation). |

## Notes

This skill is **guidance-only** — it ships no actions, hooks, agents, scripts, or templates. The body above is the entire surface; no `setup` step is required, and `.claude/hooks/` / `.claude/agents/` / `.claude/rules/` are untouched by this skill.

Sibling skill `frontend-slides` covers the slide-deck surface. The two coexist without trigger conflict because `frontend-slides` constrains itself to presentations/decks and `frontend-design` covers everything else.
