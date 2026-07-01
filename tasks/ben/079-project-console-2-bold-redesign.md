# 079 — project-console-2: Bold Redesign Fork (frontend-design, full)

**ID**: 079
**Created**: 2026-06-02
**Status**: Abandoned (superseded)
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: Medium

---

## PERMANENT RULES (do not remove)

This task document is the **session-recovery point** for this work.

1. Update at every meaningful checkpoint (HARD RULE).
2. Phase-end batching OK; drift-batching not.
3. A commit is not a substitute.
4. Resume-ready before any session boundary.
5. Capture strategy + lessons as they happen.

---

## Goals

A **complete, bold redesign** of the project console that actually exercises the `frontend-design` skill's range — distinctive typography, a committed aesthetic POV, atmosphere/texture, and spatial composition (asymmetry, grid-breaking, an editorial hero) — not the conservative token-level polish that ben/073 + ben/078 delivered.

**Why a fork, not an edit:** to protect existing systems, do this as a **new `project-console-2` skill** (fork of `project-console`) rather than mutating the in-use one. The current console is load-bearing (chat, documents, trace-matrix, dashboards, workflows, OAuth, the drift overlay, the tracker iframe) and registry-synced to the hitachi repo + the sister project. A from-scratch redesign that re-lays-out templates and re-thinks the IA is too risky to do in place. The fork lets us redesign freely, run both side-by-side (different port), and cut over only when it's proven.

## Why this task exists (honest assessment of 073/078)

ben/073 (console.css) + ben/078 (tracker dashboard) were **CSS-only, no-markup, theme-preserving, generalize-to-sister-project** changes. Each constraint was defensible; stacked, they guaranteed a *subtle* result — refinement, not redesign. We got ~20% of what `frontend-design` is for. The skill asks for a "BOLD aesthetic direction," "unexpected layouts, asymmetry, grid-breaking," "distinctive characterful fonts," "atmosphere and depth," "make it UNFORGETTABLE." We did almost none of that because:
- The active theme pack (`globallogic-dark`) owns colors + the font (Manrope); skill CSS can't/shouldn't override it.
- We deliberately skipped distinctive typography (offline/CDN + generalization concern) — the single biggest lever.
- No layout/spatial change at all (markup = risk to the JS-coupled features).

<!-- STRATEGY CONTENT: architecture, development; topics: console-redesign, skill-fork-strategy, frontend-design-full -->
## Design directions to commit to (pick ONE at kickoff)

Per `frontend-design`'s Design Thinking: commit to a bold, intentional aesthetic — refined-editorial, atmospheric-data/instrument, brutalist-utility, luxury-clinical, etc. **Decide the direction first, then build to it** (propose 2–3 with mockups before coding). Context: regulated MedTech audience (regulatory/clinical/quality/engineering); credibility + precision matter, but "credible" need not mean "generic."

### Highest impact-per-risk (do these first)
1. **Distinctive typography** — characterful display face for headings + refined body face. Biggest single lever. Self-host the woff2 in the new skill's theme pack (no CDN/offline problem). 
2. **Landing-page redesign** — the current generic card grid is the exact "predictable layout/component pattern" the skill warns against. Landing has **no JS coupling** → safe to fully re-lay-out: editorial hero, oversized type, asymmetry/overlap, real iconography, textured/gradient-mesh background.
3. **Committed color + atmosphere POV** — grain/noise overlay, gradient mesh, dramatic shadows, one sharp accent over a moody base — instead of flat slate.

### Higher risk (scope deliberately)
4. **Navigation re-layout** — vertical sidebar / asymmetric content columns. Touches every template + responsive + some JS.
5. **Distinctive data-viz** — tracker + trace-matrix: hero metrics, sparklines, reimagined progress viz instead of styled tables (markup changes in `render.py` / console templates).
6. **Motion as a system** — orchestrated route transitions, scroll-triggered reveals, surprising hover states (beyond the one entrance stagger we have).

## Boundary / Out of scope (for kickoff to confirm)

- **Read SKILL.md first** (`feedback_read_skill_before_planning`): read `project-console/SKILL.md` end-to-end before planning the fork — its IoC patterns (scaffold manifest, file-ownership classes, theme resolver, drift-overlay contract, embed vs standalone render) shape what "fork" actually means.
- **Fork mechanics**: likely route via `/skill-creator` (new skill `project-console-2`), copying `console/` + `themes/` + `scripts/scaffold.py`, with its own `tools/project-console-2/` scaffold + port. Decide: full copy vs. shared core + redesigned templates. Decide registry/sync posture.
- **Don't break the live console.** project-console stays as-is and in use until console-2 is proven; run side-by-side on a second port.
- **Preserve the data contracts** the console consumes (trace-matrix JSON sidecar, `drift.json`, tracker `submission-tracker.html`, dashboards glob patterns, advisor wiring) so console-2 is a drop-in re-skin of the same data, not a re-plumb.

## Todos

### Phase 0 — Decide & scope (next session)
- [ ] Read `project-console/SKILL.md` + `README.md` (ARCHITECTURE.md) end-to-end before any plan.
- [ ] Decide fork shape: standalone `project-console-2` skill vs. shared-core + redesigned view layer. Capture rationale here.
- [ ] Propose 2–3 bold aesthetic directions (with quick mockups/screenshots) → user picks ONE.
- [ ] Confirm scope tiers (which of directions 1–6 above are in v1).

### Phase 1 — Fork scaffold
- [ ] Create `project-console-2` skill via `/skill-creator` (copy console package, themes, scaffold). Versioned + Best Practices + Changelog per skill conventions.
- [ ] Scaffold `tools/project-console-2/` on a second port; confirm it boots and serves the same data as the live console.

### Phase 2 — Redesign (build to the chosen direction)
- [ ] Typography system (self-hosted display + body faces).
- [ ] Landing redesign (editorial hero, asymmetry, atmosphere).
- [ ] Color/atmosphere POV + motion system.
- [ ] Re-skin remaining routes (agents, documents, trace-matrix, dashboards, workflows) to the new system.

### Phase 3 — Verify & cutover
- [ ] Side-by-side Chrome verification of every route; confirm all features intact (chat, explorer, filters, drift overlay, tracker iframe, OAuth).
- [ ] Sister-project (`arthrex/pccp`) compatibility check before any registry push.
- [ ] Decide cutover: replace project-console, or keep both; update docs.

## Open Questions

- **Q1**: One bold direction for the whole console, or per-surface (e.g., editorial landing + instrument-panel dashboards)?
- **Q2**: Fork as fully-independent skill, or shared core (`console/`) + redesigned templates/CSS only (less duplication, but couples the two)?
- **Q3**: Is this project-only, or intended to go upstream to the hitachi registry eventually (affects how project-specific we can be)?
- **Q4**: Cutover intent — is console-2 meant to *replace* project-console, or coexist as a showcase?

## Resume

### In-flight artifacts
- None. Task is a captured backlog item; no code yet.

### First action on resume
1. `/task` activate 079.
2. Phase 0: read `project-console/SKILL.md` end-to-end, then bring 2–3 aesthetic directions + the fork-shape decision (Q2) to the user.

## Changelog

- 2026-06-02: Task created as the backlog home for a full, bold console redesign via a `project-console-2` skill fork. Captures the honest 073/078 retro (we were conservative), the design directions ranked by impact/risk, fork rationale, and open questions. Not started — deferred per user ("add a todo, continue another time"). Continuation of the frontend-design thread (ben/072 install → 073 console.css → 078 tracker → 079 full redesign).
- 2026-06-08: **Closed ABANDONED (superseded) per user.** Superseded by other work; the shipped frontend-design console refreshes (ben/073 + ben/078) covered the console-visual-quality need without a full project-console-2 fork. Moved to Abandoned in 000-index.md.

## Economics

_Retrospective estimate (rough; from task summary). See effort-estimation-rubric.md._

```json
{
  "economics": {
    "method_version": 1,
    "retrospective": true,
    "agentic_hours": 2,
    "todos": [
      {
        "todo": "project-console-2 bold redesign (superseded)",
        "personas": [
          "rd-lead"
        ],
        "manual_hours": {
          "min": 2,
          "max": 6
        },
        "confidence": "low",
        "basis": "superseded \u2014 fork not carried forward"
      }
    ]
  }
}
```
