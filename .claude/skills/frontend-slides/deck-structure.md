# Deck Structure & Orientation — evidence-based rules

**When to read:** Phase 1 (content discovery / storyboarding) for any deck over ~10 slides or any deck carrying dense technical content (architecture, data, process). Also the playbook for the retrofit case: "the deck feels complicated" feedback on an existing deck.

**Why this file exists:** perceived complexity is usually a *structure* problem, not a styling problem. The evidence below says the fixes are: an answer-first opening, an explicit orientation layer, altitude discipline in diagrams, claim-sentence titles, and moving depth off the projected surface. Every rule here traces to a named source; the strongest carry measured effects.

---

## 1. Storyline before slides

- **Draft the deck as an outline first** — one line per future slide (the claim), sub-lines for the evidence beneath each. Debug the argument as text before building any slide. (McKinsey "dot-dash" / ghost-deck practice.)
- **Every slide title is a full-sentence claim** — ≤15 words, active voice, the conclusion not the topic. "Data Layer Overview" is a label; "One governed layer serves every model" is a title. Measured effect: sentence-assertion headlines + visual evidence improved comprehension, delayed recall, and misconception rates versus topic-phrase + bullets, with *lower* reported cognitive load, in controlled studies with technical audiences (Garner & Alley, Penn State — the "assertion-evidence" framework).
- **The horizontal-flow test (mechanical, run it):** extract all slide titles in order and read them as prose. If the title sequence alone doesn't carry the whole argument, restructure before styling. (Consulting storylining discipline.)
- **Body = visual evidence for the title's claim.** Prefer one strong visual over bullet lists; bullets that transcribe the talk track are the redundancy failure below.

## 2. The orientation layer

A complex deck needs dedicated *orientation slides* — they are not filler, and they are the cheapest fix for "this feels complicated" because they are purely additive (existing detail slides stay untouched).

- **Executive-summary slide at position 2–3 (BLUF — bottom line up front):** the whole argument before any detail. Anatomy: one-sentence governing claim as the headline; 2–3 supporting claims (not topics); the ask or next step; one honest line about risk. Readable in 30 seconds. (Minto pyramid / military BLUF doctrine; "if the recommendation sits on slide 14, the room checked out on slide 6.")
- **Summary and agenda are different slides:** the summary previews the *claims*; the agenda previews the *route*. A complex deck can carry both, in that order. A persistent section rail in fixed chrome can do the agenda's job.
- **Section dividers with a "you are here" tracker:** repeat the same section map at every boundary with the current section highlighted — identical every time except the highlight (repeating it *without* the highlight is a named anti-pattern). Each divider carries one plain-language line: what the next slides show, and the one idea to hold through them. Thresholds from consulting practice: agenda above ~15 slides; recurring dividers for multi-section or 30+ decks.
- **Pre-training beat before the big diagram:** a "name the parts" slide (the system at its simplest, components named, nothing else) before any complex explanation. Measured effect ≈ d 0.75 on comprehension of the explanation that follows (Mayer's pre-training principle). The parts named here must keep those names for the rest of the deck.

## 3. Altitude discipline (architecture and system diagrams)

- **Overview first, zoom next, detail on demand — never open on a zoomed-in view.** (Shneiderman's visual information-seeking mantra, applied as slide ordering.)
- **One altitude per diagram.** A cloud icon next to a class name is the canonical mixed-altitude defect. C4's ladder (system context → container → component) exists because ad-hoc diagrams mix levels; context altitude is explicitly designed for "everybody, technical and non-technical," and most decks never need the bottom levels.
- **Redraw the executive view; never shrink the detailed one.** Zooming out is editorial (cluster, drop attributes, omit by relevance) — like a map changing scale, the high-altitude view shows *different* information, not the same information smaller (Hohpe, "semantic zooming").
- **Names, boundaries, and interfaces stay identical across altitudes.** The detailed diagram must be a refinement of the simple one — it may open boxes up, but never rename, merge, or contradict them (arc42 "refine building-blocks consistently"). If the two views disagree, the audience concludes one is wrong.
- **Label the simplification:** "simplified on purpose — the full map comes in section N." A declared scale pre-empts "where's X?" derailment from experts in the room.
- **On zoom-in slides, keep the link to the overview** — a dimmed mini-map locator with the active region highlighted, or at minimum a divider that says which box is being opened. Without the link, each zoom re-imposes full orientation cost.
- **Walk dense diagrams with numbered callouts** (① ② ③ narrated in order), and label the arrows — unlabeled arrows are a named diagramming anti-pattern.

## 4. Cognitive-load mechanics (slide-level)

Ranked by measured effect:

1. **Delete before restyling (coherence, d ≈ 0.86 — the largest lever):** anything not supporting the slide's one claim goes — to the appendix, the talk track, or the companion doc. "Interesting but tangential" is the definition of extraneous.
2. **When you can't delete, signal (g ≈ 0.5, works for experts too):** highlight the active path or element, dim the rest. This is how a genuinely 9-box diagram *feels* simple without lying about the complexity.
3. **Build complex diagrams in presenter-paced semantic layers** (segmenting): a diagram above ~5–7 interacting elements appears layer by layer on click. Only layer-reveals earn animation; decorative motion is extraneous load.
4. **Never put the talk track on the slide (redundancy):** identical spoken + written text measurably worsens learning. On-slide text is anchor keywords and claims, not the narration.
5. **Calibrate scaffolding to the declared audience (expertise reversal):** for expert rooms, raise the density budget and cut explanatory captions and glossary callouts of familiar terms — novice scaffolds actively cost experts. But keep signaling; that helps everyone.
6. **Depth goes behind interaction, not into smaller type (progressive disclosure):** detail-on-demand costs the curious expert one click and saves everyone else the clutter. Concentrate layout rigor (no crossing connectors, integrated labels) on the densest slides — that's where defects cost the most.

## 5. The live deck is not the leave-behind

A deck that "feels complicated" is often secretly the leave-behind wearing the projected deck's clothes. Split the roles (Duarte's slidedoc; Reynolds' "slideument" warning): the projected surface stays sparse; the depth lives in the source content doc, speaker notes, appendix slides, or a companion resource. Nothing is deleted — it is re-homed.

## 6. The structure pass (checklist)

Run this before the geometry and visual-QA passes on any deck > ~10 slides:

- [ ] Cold-reader test: every term on a slide is defined on or before its first use — run one or two persona critics (an exec and a specialist, neither shown the source docs) slide-by-slide over the built deck asking "what does this assume I already know?"; numbered references to lists the deck never shows ("rule 10", "§6") are defects, as are terms that mean something else to the room (a "recall" layer in a medical-device deck)
- [ ] Titles read in sequence as the complete argument (horizontal-flow test)
- [ ] The governing claim appears by slide 3 (BLUF)
- [ ] A context-altitude "name the parts" picture precedes the first dense diagram
- [ ] Section dividers exist at each boundary, identical tracker, current section highlighted, one hold-this-idea line each
- [ ] Every diagram is single-altitude; names identical across zoom levels; simplifications labeled
- [ ] No slide transcribes the talk track; each slide is one claim + evidence
- [ ] Depth demoted (popup / flip / appendix / companion doc), not compressed
- [ ] 4–7 sections max; sections MECE at the same altitude

## Sources (abbreviated)

Minto, *The Pyramid Principle* (answer-first, SCQA, MECE) · BLUF doctrine (US military comms) · Slideworks / StrategyU (action titles, horizontal flow, dot-dash) · Garner & Alley, Penn State (assertion-evidence, measured) · Mayer, *Multimedia Learning* (coherence, signaling, redundancy, segmenting, pre-training — meta-analytic effects) · Kalyuga et al. (expertise reversal) · Nielsen Norman Group (progressive disclosure) · Shneiderman 1996 (overview → zoom → detail) · Simon Brown, C4 model (altitude per audience) · arc42 §5 (consistent refinement) · Hohpe, *Architect Elevator* (semantic zooming) · Duarte (slidedoc) / Reynolds (slideument) · TED speaker guidance (several slides beat one dense slide) · Deckary / Macabacus (agenda + tracker thresholds).
