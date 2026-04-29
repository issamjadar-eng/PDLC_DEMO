# 038 — Agentic Delivery Whitepaper Deck

**ID**: 038
**Created**: 2026-04-29
**Status**: Active — Backlog
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: Medium
**References**: [`ben/034`](034-agent-engineering-whitepaper.md) (the whitepaper this deck presents)

---

## PERMANENT RULES (do not remove)

This task document is the **session-recovery point** for this work. If the current session drops, is compacted, or ends, the next session must be able to load **this file alone** and continue where we left off.

1. **Update at every meaningful checkpoint (HARD RULE).** After each meaningful unit of work — a slide draft, a theme decision, a screenshot pass, a review round — update this task doc:
   - tick the relevant Todo checkbox
   - add a dated Changelog line naming the concrete artifact (commit SHA, file path, decision, blocker)
   - update any progress counts/tables in Goals
2. **Phase-end batching is OK; drift-batching is not.** If you cannot name the specific upcoming checkpoint where you'll write the update, write it now.
3. **A commit is not a substitute.** Git history records code; this doc records the program narrative.
4. **Resume-ready before any session boundary.**
5. **Capture strategy + lessons as they happen.** `<!-- STRATEGY CONTENT: domain, topic -->` and `<!-- LESSONS LEARNED: category -->` blocks go in this doc in real time.

---

## Goals

Build a **beautiful, professional, tech-forward presentation deck** that delivers the agentic-delivery whitepaper's argument as a slide narrative an executive audience can absorb in 30–45 minutes (or scan in 10).

**Source material:**
- Primary: `/home/benxavier/project/PDLC-DEMO/agentic-delivery-whitepaper.md` (executive cut, ~10K words, 23 sections + 6 appendix sub-sections)
- Reference: `/home/benxavier/project/PDLC-DEMO/agent-engineering-whitepaper.md` (full source, ~16K words, with Appendix C addendum and the deeper investment-case detail)
- Rendered PDF: `/home/benxavier/project/PDLC-DEMO/agentic-delivery-whitepaper.pdf` (22 pages — visual reference for diagrams + tables)

**Audience:** Same four cohorts as the whitepaper — GTM Sales leadership, Product Strategy, Pre-Sales Engineering, Delivery Engineering — plus engineering and operating leadership making the investment decision.

**Success criteria:**
- The deck stands alone (a viewer who has not read the whitepaper can follow the argument).
- It also accompanies the whitepaper (a viewer who has read the paper recognizes every claim and sees the visual condensation).
- It is *visually polished* — beautiful, professional, tech-forward design — not the default-template-pptx look. Worthy of being shown to a board, a customer's CTO, or in a keynote.
- It carries the load-bearing diagrams from the whitepaper (the Conductor mental model and the compounding Flywheel) cleanly and legibly.
- Speaker notes accompany every slide.

---

## Open questions for the user before drafting starts

1. **Branding / theme**
   - GlobalLogic-themed (matching ben/025 `scripts/build-project-overview-pptx.py`)?
   - Vendor-neutral / co-brandable for customer-facing use?
   - Or two cuts (GL-internal + customer-facing)?
2. **Length target**
   - Executive cut (~15 slides for a 20-minute pitch)?
   - Standard cut (~25–30 slides for a 45-minute walkthrough)?
   - Long cut (~45 slides covering the full Appendix C addendum)?
   - Or all three from the same source?
3. **Tooling**
   - `pptx` skill via Python (matches ben/025 — generates PowerPoint that's editable downstream)?
   - HTML/CSS slides via reveal.js or similar (web-deliverable, easier to make visually striking)?
   - Hybrid (HTML for design pass, exported to PPTX for PowerPoint editing)?
4. **Visuals**
   - Re-author the Conductor and Flywheel diagrams as native slide elements (more design control)?
   - Or render via mermaid-cli and embed as SVG/PNG (matches PDF, less design control)?
   - Add new visuals (timeline, before/after, hero numbers) — yes/no/specific list?
5. **Speaker notes depth**
   - Talk-track for sales (key phrases, transitions)?
   - Bullet rationale for the slide author (why this slide, what the argument)?
   - Both?

---

## Todos

### Phase 1 — Discovery / Outline
- [ ] User answers the five open questions above (or delegates).
- [ ] Map every whitepaper section to a candidate slide. Output: numbered slide outline with titles + 1-line gist + speaker-note seed.
- [ ] Decide narrative arc: deal-flow (market → offer → engagement → execution → invest) or investment-first (pitch → defend → invest)?
- [ ] Lock the slide count target.

### Phase 2 — Visual / theme design
- [ ] Lock theme: colors, type, hero treatment, table style, diagram style.
- [ ] Build a reusable "design system" module (or `scripts/build-…pptx.py` style helpers) so every slide is consistent.
- [ ] Author the cover, agenda, section dividers, and thank-you slides as the visual baseline.

### Phase 3 — Content draft
- [ ] Author each slide from the slide outline.
- [ ] Reauthor Conductor + Flywheel diagrams as native deck elements.
- [ ] Speaker notes per slide.
- [ ] First-pass review pass (substance, anonymization, dual-audience cuts).

### Phase 4 — Polish & delivery
- [ ] Visual polish pass — every slide gets typography review, alignment, color balance.
- [ ] Anonymization grep matching the whitepaper's bar (no customer names, no K-numbers, no product names beyond `MedTech customer` / `digital-surgery customer`).
- [ ] Output formats: `.pptx` for PowerPoint editing; PDF export for share-ability; optionally HTML/web slides if Q3 above lands on hybrid.
- [ ] Speaker rehearsal pass (30-minute pitch out loud — does it land?).

### Phase 5 — Skill extraction
- [ ] Promote the slide-build pipeline into the `/whitepaper` skill (defined in ben/034 Phase 6) so any future whitepaper-to-deck conversion is one command.
- [ ] Capture insights from this build in the skill's `actions/distill.md` (compress whitepaper → deck) and `actions/render.md` (style + diagram pipeline).

---

## Inheritance from ben/034

The whitepaper task (ben/034) Phase 6 captured the full markdown-to-PDF rendering pipeline (pandoc + mmdc + chrome) along with 13 numbered insights (the `--wrap=none` fix, the `\$` escape, italic-merge repair, mermaid 8.x compatibility, cluster-bounds preservation, etc.). **The deck pipeline should reuse all of those guardrails** for any rendered diagrams, plus the self-test loop (render → JPG → Read-tool visual inspection → only commit if visuals pass).

Additional inheritances:
- The four-bucket competitive frame (§3.2 of the whitepaper) — every deck must defend against bucket-1, bucket-2, and bucket-3 vendors.
- The two mental models — Conductor (organizational) and the Flywheel (commercial) — are load-bearing and should be hero slides, not afterthoughts.
- The compounding 5-year margin curve + eight assumptions (§6.4 / §7.5.4) is a likely investment-case hero slide.
- The tiered investment model (Tier 1 / Tier 2 / Tier 3 with geographic mix) is the right shape for a "what we're asking for" slide.
- Anonymization bar matches the whitepaper's: `MedTech customer` / `digital-surgery customer` only; no K-numbers, no product names.

---

## Strategy & Lessons Learned

> Strategy and lessons captured inline above with `<!-- STRATEGY CONTENT -->` and `<!-- LESSONS LEARNED -->` markers. The `/strategy` and `/lessons` harvest skills will pull from those blocks.

---

## Changelog

- 2026-04-29: Task created. Spun out of ben/034 (whitepaper) at the user-approved stopping point. Five open questions captured for the user to answer before drafting starts (branding, length target, tooling, visuals, speaker-notes depth). Phase 1–5 todo skeleton in place. Inheritance from ben/034 documented (rendering pipeline, four-bucket framing, two mental models, compounding 5-year curve, tiered investment model, anonymization bar).

---

## Resume Instructions

If a fresh session picks this up:
1. Read this file top to bottom.
2. Read the whitepaper source: `/home/benxavier/project/PDLC-DEMO/agentic-delivery-whitepaper.md`.
3. Read the rendered PDF for visual reference: `/home/benxavier/project/PDLC-DEMO/agentic-delivery-whitepaper.pdf`.
4. Read ben/034's Phase 6 captured pipeline insights — the deck build inherits the rendering guardrails (`--wrap=none`, `\$` escape, italic-merge repair, mermaid 8.x compatibility, cluster-bounds preservation, self-test loop).
5. Activate the task: `bash .claude/hooks/task-activate.sh add <SESSION_ID> 038`.
6. **Status:** Active — Backlog. The five open questions in this doc must be answered before Phase 1 outline drafting begins.
