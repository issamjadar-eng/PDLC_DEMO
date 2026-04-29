# 034 — Agent Engineering Whitepaper & Deck

**ID**: 034
**Created**: 2026-04-27
**Status**: In Progress
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
2. **Phase-end batching is OK; drift-batching is not.** Planned phases are a legitimate checkpoint — writing once per phase is fine if the phase is bounded and the write happens **at the phase boundary, before the next phase starts**.
3. **A commit is not a substitute.** Git history records code; this doc records the project narrative — what was done, why, what's left, what surprised us.
4. **Resume-ready before any session boundary.**
5. **Capture strategy + lessons as they happen.** `<!-- STRATEGY CONTENT: domain, topic -->` and `<!-- LESSONS LEARNED: category -->` blocks go in this doc in real time, not in chat alone.

Success test for this doc: a fresh Claude session, given only this file, can re-enter the work without asking the user "what were we doing?"

---

## Goals

Produce a **dual-audience whitepaper + presentation** that makes the case for **agent engineering as the next logical evolution of classical software engineering** (and other engineering disciplines), with concrete value prop, market direction, and opportunities.

**Audiences:**
- **Go-To-Market / Sales** — narrative, value prop, market direction, opportunities, competitive framing, talk-track
- **Pre-Sales Engineering** — project-requirement assessment, skillset needs, reusable assets / accelerators, cost projections

**Deliverables:**
1. Brainstorm + outline captured here (this doc)
2. White paper in markdown (TBD path — likely `docs/external/industry-frameworks/agent-engineering-whitepaper.md` or `docs/project/whitepapers/`)
3. PowerPoint presentation built from the whitepaper

**Success criteria:**
- A GTM rep can read the whitepaper and pitch agent engineering without further prep
- A pre-sales engineer can use it to scope a real engagement (skills, accelerators, rough cost)
- Both audiences agree on the same core value prop and market direction

---

## Todos

### Phase 1 — Discovery / Brainstorm (capture-in-task) — DONE
- [x] Capture raw idea seeds (compiler analog, optics framing, quality-first, differentiator buckets)
- [x] Pull historical analogs (compiler/assembly, CAD, SPICE, FEA, BIM, RTL — referenced in whitepaper §1, §7)
- [x] Define "agent engineering" vs. "AI-assisted coding" vs. "classical SE" — done in §3.1 four-bucket framing
- [x] Land the value prop in one paragraph (whitepaper §5.1)
- [x] Land the market direction in one paragraph (whitepaper §5.2)
- [x] Identify top 5 opportunities for the GTM motion (whitepaper §5.3)
- [x] Identify top 5 reusable assets / accelerators for pre-sales (whitepaper §6.2 — 11 listed)

### Phase 2 — Outline — DONE
- [x] Whitepaper outline locked (see "Whitepaper outline (locked)" section above)
- [ ] Presentation outline (slides, narrative arc, agenda) — deferred to Phase 4
- [x] Decided: one whitepaper with explicit dual-audience cuts (§5 GTM, §6 Pre-Sales) rather than two separate docs

### Phase 3 — Whitepaper draft — DONE
- [x] First-pass markdown draft authored at `/home/benxavier/project/PDLC-DEMO/agent-engineering-whitepaper.md`
- [x] Review pass 1 (substance, claims-grounded): fixed skill count (23→22), softened compiler-era timeline ("FORTRAN, COBOL, then C" → "FORTRAN, COBOL, and the C era that followed"), verified all numerical claims against project state and sister-project survey
- [x] Review pass 2 (tone, dual-audience, anonymization): grep-confirmed zero identifying marks (no PainEase / PP3500 / K-numbers / GlobalLogic / Hitachi / customer names); confirmed dual-audience separation works (GTM section has talk track + objections; Pre-Sales section has scoping + accelerators + cost model + discovery questions); confirmed narrative arc (argument → discipline → differentiator → proof → GTM → Pre-Sales → closing)

### Phase 6 — Skill: Whitepaper authoring + asset generation — NOT STARTED (capture-only this turn)

> User direction (2026-04-29): "Add a todo, we want what you're doing the writing of the whitepaper and generating the assets ultimately as a skill. No need to do the work now, just capture the insights, approaches in the task doc so we can pick it up later." Do **not** build the skill yet; capture the pipeline + gotchas so a future session can lift it cleanly.

- [ ] **6a — Author the `/whitepaper` skill** that takes a markdown source and produces a clean, diagram-rich PDF with tight margins. Should also handle the *"generate the new whitepaper from a deeper source document"* mode that produced `agentic-delivery-whitepaper.md` from `agent-engineering-whitepaper.md` in this task.
- [ ] **6b — Generalize the asset pipeline** so any project's markdown whitepaper can render to PDF with embedded Mermaid diagrams. Include a `--theme` knob (page size, margins, fonts) and a `--branding` knob (cover-page generator).
- [ ] **6c — Migrate the Mermaid renderer** into a shared helper in the registry so other skills (`pptx`, `dhf-manifest` dashboards, etc.) can reuse it.

#### Captured insights from the live PDF build (2026-04-29) — load-bearing for the skill

The full pipeline that worked, in order, after several false starts:

1. **Tooling stack.** `pandoc` (3.9.0.2 via Linuxbrew) + `npx -y @mermaid-js/mermaid-cli@10` (mmdc CLI) + system `google-chrome` (`/usr/bin/google-chrome`) for headless PDF print. **No LaTeX engine required.** This is critical — most pandoc→PDF tutorials assume xelatex; this WSL environment doesn't have it. Going through HTML → Chrome headless is the portable path.
2. **Pre-render Mermaid blocks with `mmdc`, do NOT rely on browser-side rendering.** The browser-side approach (load mermaid.js via CDN, run on `window.load`, then chrome `--print-to-pdf`) is unreliable: Chrome's `--virtual-time-budget` does not guarantee mermaid completes before the print snapshot. Even at 30s budget, diagrams snapshotted partially or as `aria-roledescription="error"`. Pre-rendering with mmdc CLI eliminates the timing dependency entirely.
3. **`mmdc` setup gotchas.**
   - Pass `PUPPETEER_EXECUTABLE_PATH=/usr/bin/google-chrome` so puppeteer reuses the system Chrome instead of trying to download its own.
   - Pass a `puppeteer.json` config with `{"args":["--no-sandbox","--disable-gpu","--disable-dev-shm-usage"],"executablePath":"/usr/bin/google-chrome"}` — the no-sandbox flag is required in many WSL/CI environments.
   - First run downloads packages via npx (~30s); subsequent runs are instant. Cache via `npx -y` (allows non-interactive install).
4. **Each generated SVG carries `id="my-svg"`. With multiple diagrams on one page, this collides.** The first SVG's `<style>` block uses `#my-svg`-scoped selectors, which match only the first element by ID — leaving the second diagram unstyled. Fix during substitution: rewrite `id="my-svg"` to a unique `id="mermaid-diagram-N"` and apply the same rewrite to all `#my-svg` occurrences in the SVG's inline `<style>` block.
5. **Pandoc `--wrap=auto` (default) word-wraps long lines at 72 chars, including INSIDE embedded SVG `<style>` blocks.** This breaks CSS strings — e.g., it inserts a newline inside `font-family:"trebuchet ms"`, which makes the entire CSS rule invalid (CSS strings cannot contain literal newlines). Result: the SVG's inline style is silently dropped and node rectangles render with default browser styling (often dark/black). **Always pass `--wrap=none` when embedding SVGs.** This is the single most-confusing failure mode to diagnose; it looks like a styling issue but it's a pandoc reformatting bug.
6. **Pandoc `--standalone` emits BOTH a `<title>` in `<head>` AND a `<h1 class="title">` in body** when `--metadata title=…` is provided. With the markdown's own first `# Title` line, this gives two visible H1s. Two robust fixes: either (a) drop the metadata title and rely on the markdown's H1 (set `--metadata pagetitle=...` instead, or post-process to inject `<title>`), or (b) post-process the HTML to strip the `<header id="title-block-header">…</header>` wrapper and any `<h1 class="title">` element. Option (b) is what we used — preserves the head `<title>` for PDF metadata while removing the body duplicate.
7. **Substitution approach: replace ````mermaid…```` blocks in the markdown with the rendered SVG wrapped in `<div class="mermaid-fig">`.** Then run `pandoc -f gfm+raw_html -t html` so pandoc passes the inline SVG through unchanged. Cleanest path observed.
8. **Tight-margin CSS for executive whitepapers.** `@page { size: letter; margin: 0.55in 0.55in; }` is the right size for dense tables. Body font-size 10pt, table font-size 8.5pt, line-height 1.4. `page-break-inside: avoid` on `table` and `.mermaid-fig` keeps diagrams and tables intact across page breaks. (Full CSS captured in `/tmp/wp-build/style.css` during this run; should be committed as a template asset for the skill.)
9. **Chrome headless flags that worked.** `--headless --disable-gpu --no-sandbox --hide-scrollbars --no-pdf-header-footer --virtual-time-budget=5000 --print-to-pdf=<out>.pdf file://<in>.html`. The `--no-pdf-header-footer` removes Chrome's default URL/timestamp footer. With pre-rendered SVGs, the virtual-time-budget can be tiny (5s is plenty) — no JS to wait for.
10. **`--print-to-pdf` consumes `file://` URLs cleanly.** No web server needed. CSS via `<link rel="stylesheet" href="style.css">` works as long as the CSS file is alongside the HTML in the same directory.
11. **Verification path.** After printing, use `pdfinfo` (page count + title) and `pdftotext` (extract diagram-label strings to confirm SVG vector text made it into the PDF) and `pdftoppm -r 110 -f N -l N -jpeg` to rasterize specific pages for visual inspection. The diagram-label strings (`"knows the piece"`, `"funds further"`, etc. — strings that appear ONLY in the diagram, not in surrounding prose) are the cheapest "did the diagram render" check.
12. **The docflow PreToolUse hook blocks `pdfinfo` / `pdftotext` / `pdftoppm` direct calls** — those are conversion verbs in the hook's vocabulary. The documented override is `touch .state/docflow-active` in a *separate* tool call before the inspection commands (the hook reads the marker before running the gated tool, so same-call `touch && pdfinfo` does not work). For a permanent skill, the inspection step should either go through the docflow skill or set the marker as part of its own state lifecycle.
13. **Residual polish item (deferred).** Mermaid v10 sometimes clips multi-line `<br/>`-separated node labels at the bottom of node rectangles (the foreignObject content is taller than the auto-computed rect height). Workarounds for the skill: (a) accept slight clipping for dense diagrams, (b) post-process the SVG to enlarge `<rect>` heights proportional to label content, or (c) shorten labels in the markdown source. Document this in the skill so authors can choose.

#### Skill scaffolding sketch (for future session)

```
.claude/skills/whitepaper/
├── SKILL.md                      # entry point, --action render | distill | cover
├── README.md                     # post-update notes, version history
├── actions/
│   ├── render.md                 # MD → PDF pipeline (this captured workflow)
│   └── distill.md                # long whitepaper → executive cut (the agent-engineering → agentic-delivery rewrite pattern)
├── scripts/
│   ├── render_pipeline.py        # orchestrator: substitute mermaid → pandoc → strip-title → chrome print
│   ├── render_mermaid.sh         # wrapper around mmdc with the puppeteer.json + ID rewrite
│   └── inspect_pdf.sh            # pdfinfo + pdftotext + pdftoppm verification (sets docflow marker)
├── templates/
│   ├── style.css                 # tight-margin executive style (this run's CSS)
│   ├── puppeteer.json            # mmdc config
│   └── cover-page.html           # optional cover-page template (logo, version, audience)
└── lib/
    └── titles.py                 # post-process to strip duplicate title block
```

**Sister-project applicability.** Other regulated-medtech projects in the registry will benefit immediately — every customer engagement that produces an executive deck or whitepaper currently regenerates this pipeline by hand. Promoting it to the registry is the cross-surface correction (per §C.3.2 of the source whitepaper). Estimated effort: ~1-2 days to lift this captured pipeline into a skill, plus ~1 day for documentation and tests.

### Phase 4 — Deck build — NOT STARTED
- [ ] Slide outline mapped from whitepaper
- [ ] Build via `pptx` skill (likely a `scripts/build-agent-engineering-pptx.py` like ben/025)
- [ ] Speaker notes
- [ ] Review pass

### Phase 5 — Technical Addendum: "How the Optics Were Actually Built" — IN PLANNING
> A new addendum to the whitepaper documenting **the human-driven process** behind the agentic project shape — how Ben's redirections, challenges, and on-the-go strategy calls produced the skills, hooks, and conventions that the body of the whitepaper treats as finished artifacts. Sources: PDLC-DEMO + arthrex-pccp task corpora (~165 task docs combined), CHANGELOGs, sync-logs, and chat history. This is **R9** on the revision backlog.

- [x] **5a — Wide scan + categorization.** Read both project task indexes (40 PDLC + 125 arthrex), CHANGELOGs, sync-logs. Locked **10 candidate categories** below; tentative thesis stated.
- [x] **5b — Per-category deep dive.** Ran 5 parallel Explore agents (paired categories) against the source corpus. Hard examples with task IDs / commit SHAs / quoted redirects gathered for all 10. Categories C1+C7 partially merged (substance vs shape iteration) but kept distinct in the addendum because the C7 role-clarification sub-pattern (emitter vs viewer) is its own lesson; C2+C8 kept distinct (Claude-behavior promotions vs. Ben-pain process rules).
- [x] **5c — Cross-cutting synthesis.** Five meta-insights identified: M1 (corrections-that-became-skills), M2 (diminishing-returns-triggers-layer-up), M3 (built-then-retired-is-a-feature), M4 (verification ratchet), M5 (cost-named-not-hidden). **Working thesis was sharpened, not replaced.** The eval-engineer framing held against ~70% of evidence, but a second mode emerged: the lead also brings *outside knowledge the model could not have* (PDLC-vs-SDLC scope, IEC 62304 §5.1.11 framing, four-bucket competitive frame). The synthesized thesis is **eval engineer + domain expert as a hybrid role** — and the addendum makes this explicit as the counter-thesis the evidence forced.
- [x] **5d — Addendum drafted.** Authored as **Appendix C — How the Optics Were Actually Built** appended to `agent-engineering-whitepaper.md` (chose in-paper appendix over sibling file per the strategy block — readers who skip it still get the body's argument; readers who read it leave with a much harder-to-dispute version). Structure: C.1 why-this-exists → C.2 method → C.3 thesis + counter-thesis + honest synthesis → C.4 ten patterns → C.5 five meta-insights → **C.6 counterpoints (added beyond the original outline because the user explicitly asked for them)** → C.7 hiring/staffing closer → provenance note. ~2,800 words; whitepaper now 581 lines / ~11,344 words.
- [x] **5e — Review passes.**
  - **Pass 1 (substance):** Every example in the addendum is anchored to a real artifact in the source corpus surfaced by the deep-dive agents. The 7-story SRS cost (13 min / 90 calls / 225k tokens) is a verbatim quote from the docflow CHANGELOG. The ~610-line context audit is from arthrex `ben/095`. The 25%/75% capture-hook bypass ratio is from arthrex `ben/100`. The IEC 62304 §5.1.11 determination is from arthrex `ben/070`. The 86-files-14-skills anonymization push is from PDLC `ben/032`.
  - **Pass 2 (tone):** Re-read for self-flattery. Counterpoints section (C.6) added explicitly to pressure-test the thesis: (i) multi-pass-is-sometimes-a-tax (task gate triple-overhaul); (ii) eval-engineer-thesis-under-weights-domain-expert mode; (iii) built-then-retired implies prior over-engineering. The closing paragraph is intentionally unhedged ("the discipline is reproducible. the bench is hireable.") — this is the GTM punch the body has earned by C.6.
  - **Pass 3 (anonymization):** `grep -niE "ben|arthrex|hiplink|painease|pp3500|hitachi|pdlc.demo"` returned only "bench" / "Ben" matches that are in the existing body (line 19, 21, 158, 363, 410, 422, 455 — all pre-existing GL-internal cuts already approved in pass-2 of the body). Zero new identifying marks introduced. The lead is referenced as "the lead" throughout the addendum; programs are referenced as "Program A / Program B" or "the demonstration program" / "an active customer program."

**Outstanding (deferred to Phase 4 deck and the wordsmith backlog):**
- **R8 length re-check is now urgent** — whitepaper went from 8,500 → 11,344 words with the addendum. Still defensible because the addendum is opt-in / appendix-ranked, and Section Map work (R1) hasn't run yet. Resolve order: do R1 first, then re-check whether the addendum needs trimming.
- **Section Map (R1) has not yet been built** — the addendum drop did not change R1's status. R1 still next on the wordsmith backlog.
- **Phase 4 deck build** still pending; addendum may seed 2–3 slides ("how the optics were actually built" → trait list / propagation example / counterpoint).

**Working thesis (to test, revise, or replace in 5c)** — *Most of the skills, hooks, conventions, and rules in this project look like they were authored as a coherent system. They weren't. They were each crystallized from a moment in which Ben observed a Claude-generated draft, redirected it with a specific reason, and then promoted that redirection from a one-shot correction into a durable artifact (a skill, a hook, a CLAUDE.md rule, a glossary entry). The agentic project shape isn't an authored design — it's the **codified residue of a year's worth of human eval signal**, with the registry acting as the propagation channel. Agent engineering, in practice, looks less like writing a system and more like running an eval suite where the eval is the human and the fixes propagate as scaffolding.*

**10 candidate categories (locked from 5a; deep dives in 5b will validate or split/merge)**

| # | Category | One-line | 2–3 representative task seeds |
|---|----------|----------|-------------------------------|
| C1 | **Iteration-cycle / shape-discovery** | Ben observed Claude's output, named what was wrong, and the next version absorbed the fix — over many rounds. | arthrex `ben/075` docflow v16 → v22 → v25 → v26 → v30 (15+ rounds across SAD/SRS/Mermaid faithfulness, column reorder, link preservation, sub-tables, perf optimizations); arthrex `ben/087` docflow F11 Mermaid reliability |
| C2 | **Process-failure-as-engineering-input** | A Claude behavior failure (forgetting to update task doc, over-asking, dropping context on compaction) was promoted into a permanent rule or hook, not just a scolding. | arthrex `ben/078` task-doc freshness hook; arthrex `ben/119` default-to-action rubric (one user correction → skill v23 → v24 → all projects); PDLC `ben/021` digest-readable-format |
| C3 | **Scope / architecture redirection** | Ben challenged the scope of a Claude-proposed framing or design and rewrote it (PDLC vs SDLC, "is Copilot agentic?", task gate scope, hook regex tightening). | PDLC `ben/034` PDLC-vs-SDLC rewrite + four-bucket framing (this whitepaper); arthrex `ben/027` task-gate overhaul; arthrex `ben/066` task-gate skill-source scoping; arthrex `ben/082` docflow hook regex tightening |
| C4 | **Cross-project leverage / registry-mediated propagation** | A correction made on one project was promoted upstream and pulled by every sister project — proving the loop closes. | arthrex `ben/046` publish skills → hitachi registry; arthrex `ben/047` sync from registry; PDLC `ben/032` skill-tree anonymization (86 files, 14 skills, 200 lines, full prose pass + new `best-practices` check, all upstream); PDLC `ben/029` sync-skills v6→v7→v8 (three sequential PRs in one session) |
| C5 | **Verification / claim-grounding / fabrication discipline** | Ben demanded measurement (gap reports, audits, [VERIFY] flags, demo banners, anonymization lint) instead of accepting Claude's vibes claims. | PDLC `ben/032` anonymization regression-guard lint; arthrex `ben/070` tool-validation operations strategy + IEC 62304 §5.1.11 intended-use determination; arthrex `ben/072` `/best-practices fix` three-tier safety model around CLAUDE.md edits |
| C6 | **Performance / context-economy redirection** | Ben spotted that the optics were leaky — too much in session context, too many hook invocations — and re-engineered the loading model. | arthrex `ben/095` skill-context-optimization (17 skills × 610 lines = always-loaded waste, moved to README); arthrex `ben/096` session-start hook performance; arthrex `ben/097` per-turn hook efficiency; arthrex `ben/098` shared-code consolidation |
| C7 | **UX / output-shape feedback loops** | Ben used the artifact (a render, a console view, a converted doc) and reported what was unreadable; the next round fixed exactly that. | docflow `v20→v21` (column reorder, none-backticked, perf A/C/F — three orthogonal asks in one round); docflow `v21→v21.1` (bold keywords, per-bullet newlines, sub-table block); arthrex `ben/094` console-assistant-chat-errors; arthrex `ben/106` workflow-b3-ux-polish |
| C8 | **Discipline-of-the-process discovery** | A meta-rule about how Claude should *work* (capture-as-you-go, one-task-one-file, scratch folder, retire hooks that hurt flow) — discovered by Ben observing his own pain. | arthrex `ben/100` capture-harvest-redesign (retired multi-hook strategy/lessons capture flow that killed conversation flow); arthrex `ben/112` scratch folder convention; arthrex `ben/050` task-capture strategy/lessons; PDLC's "one task, one file" CLAUDE.md rule |
| C9 | **Multi-perspective / advisor-design insight** | Ben designed the panel-of-advisors topology and the three-tier grounding model — both are decisions that don't appear in any individual skill but shape every interaction. | arthrex `ben/058` advisors-skill-scaffold; arthrex `ben/059` agent-design-best-practices; arthrex `ben/061` migrate console agents → advisors; arthrex `ben/099` tiered grounding architecture (universal + shape-stable + project-overlay) |
| C10 | **Self-improving feedback loop authoring** | Ben built the meta-tools (`/best-practices`, `/lessons`, `/sync-skills`, `/digest`) that let the system observe and improve itself — these are the optics-grinding wheel, not just optics. | arthrex `ben/005` best-practices skill; arthrex `ben/036` lessons-learned skill; PDLC `ben/021` digest-readable-format; arthrex `ben/100` capture-harvest-redesign (system retiring its own bad design) |

**Notes on category boundaries** — C1 vs C7 are close (both feedback-driven iteration); the working split is *C1 = the artifact's substance got iterated*, *C7 = the artifact's user-facing shape got iterated*. Likely to merge or split during 5b. C8 vs C2 are also close; working split is *C2 = a Claude behavior got promoted into a rule*, *C8 = a Ben pain-point got promoted into a process convention*. May collapse.

**Stop conditions for Phase 5** — (a) all 10 categories covered with hard examples, OR (b) thesis pressure-tests well after first 5–6 categories and the remainder repeat the pattern (then we collapse the back half into a "and similarly…" treatment instead of full deep dives — this is the more likely path).

<!-- STRATEGY CONTENT: development, agent-engineering-discipline -->
The Phase 5 addendum is the **honest companion** to the main whitepaper. The body of the whitepaper makes a clean structural argument ("we sell agentic project shape"); the addendum makes the messier process argument ("…and here's how that shape actually got built — by a human running an eval loop in real time, with skills/hooks/registries as the propagation mechanism for the corrections"). Both audiences benefit: GTM gets a credibility-builder ("this isn't speculation, here are 100+ task receipts"), pre-sales gets a staffing argument (the role we're describing isn't a prompt engineer — it's an eval engineer with strong domain instinct + writing skill, exactly the §6.3 profile). Recommend keeping the addendum *in* the whitepaper rather than as a sibling doc — readers who skip it still get the body's argument; readers who read it leave with a much harder-to-dispute version of the thesis.
<!-- /STRATEGY CONTENT -->

<!-- LESSONS LEARNED: process-discipline -->
**Plan-first when scoping a meta-analysis of project history.** When the user asked for a build-process addendum, the temptation was to start pulling examples and writing prose. The right move was the wide-scan-then-categorize approach we ran in 5a: read the index files / CHANGELOGs / sync-logs first, lock 10 candidate categories with seed task IDs, state the tentative thesis, *then* propose phased deep dives. This both produces a better artifact and gives the user a clean review surface — they can redirect categories before any expensive content is written.

**Why:** The corpus is large (165 task docs, two CHANGELOGs, two sync-logs, plus chat history). Diving into examples without a category map produces a list, not a synthesis.
**How to apply:** For any "summarize a year of work" ask — always do the index-level read + category lock first, in the task doc, with example seeds; never go straight to long-form writing.
<!-- /LESSONS LEARNED -->

---

## Brainstorm — Raw Idea Bank

> Working space. Bullet ideas without filtering. We'll cluster and refine in Phase 2.

### Seed: "Compilers / assembly review" analog *(Ben, 2026-04-27)*

**The parallel:**
- 1950s–60s: engineers wrote in early HLLs (FORTRAN, COBOL, then C) but **manually inspected the compiler's assembly output** to confirm it did what they expected. Trust was earned line-by-line.
- 2024–2026: engineers prompt LLMs to produce code, then **read every line of the diff** to confirm intent. Trust is again being earned line-by-line.
- In both cases, the higher-level abstraction is *generative* — you describe intent, the system produces a lower-level artifact you used to write by hand.

**Where it parallels:**
- Productivity multiplier vs. trust deficit — same shape of curve.
- "Old guard" skepticism: "I can write better assembly than the compiler." → "I can write better code than the LLM."
- Tooling co-evolves with trust: optimizing compilers + lint + type systems made assembly review unnecessary; evals + tests + agent harnesses + verification will make line-by-line LLM diff review unnecessary for routine cases.
- The job didn't disappear — it moved up the stack. Compiler authors became a specialty; *most* engineers stopped reading assembly. Same shape coming for prompt/agent authors vs. code-consumers.

**Where it differs (this is the more interesting half):**
- **Compilers are deterministic; LLMs are stochastic.** Same input → same output for `gcc`. Same prompt → distribution of outputs for an LLM. So the trust-building mechanism can't be "I checked it once and it's correct forever."
- **Compilers have a formal spec; LLMs do not.** A compiler bug is a deviation from a language standard. An LLM "bug" is a fuzzy notion — wrong output, hallucinated API, subtly wrong semantics. There's no reference implementation to diff against.
- **Compilers narrow possibility space; LLMs widen it.** A compiler turns one HLL program into one binary. An LLM turns a fuzzy intent into a *family* of plausible programs — the engineer is now choosing across a generation, not just verifying a transformation.
- **Compilers do one job; agents do open-ended jobs.** A compiler doesn't decide what your program should do. An agent is increasingly making product/architecture decisions inside its loop — that's a category shift from "tool" to "collaborator."
- **Verification surface differs.** Compiler output you verify by running the binary. Agent output you verify by reading code AND inspecting the *process* (which tools did it call? what did it search? did it commit before testing?). Process auditing is new.
- **Feedback loop is in-the-loop, not post-hoc.** With compilers you reviewed assembly after the fact and either trusted it or didn't. With agents you steer mid-generation — interrupt, redirect, give it a memory file, restrict its tools. That's a different engineering discipline: **shaping the agent's environment, not just reviewing its output.**

**Implication for "agent engineering" as a discipline:**
- Classical SE: write correct code.
- Agent engineering: design the **scaffolding** (prompts, tools, memory, evals, guardrails, hooks, permission model, escalation paths) such that a non-deterministic generator reliably produces correct work *and you can prove it did*.
- The artifact you ship isn't the code — it's the **system that produces and verifies the code**.

<!-- STRATEGY CONTENT: development, agent-engineering-discipline -->
The compiler/assembly analog is a **useful framing tool but breaks at the determinism boundary**. Use it in the whitepaper as a "you've seen this movie before" device for skeptics, but follow immediately with the four divergences (stochastic, no spec, widens possibility space, in-loop steering). The deeper claim — and the one we should anchor the whitepaper on — is that **agent engineering is the discipline of building reliable systems out of non-deterministic generators**, and that this is genuinely new ground that classical SE didn't have to solve.
<!-- /STRATEGY CONTENT -->

### Seed: Scaffolding as a beam-focuser *(Ben, 2026-04-27)*

**The compiler analog is incomplete.** A bare LLM is closer to a *raw light source* than a compiler — broadband, scatters in every direction. What we've built in this project — the **skills, rules, agents, hooks, project structure, task gate, memory, evals, registries, glossary, allowlists, scaffolds** — is the **optics**: lenses, mirrors, apertures, collimators that take that broadband output and **focus it into a coherent beam**.

- A model alone is a **bulb**. Useful, but illuminates the whole room — and a lot of what it lights up isn't what you wanted.
- Agentic scaffolding is the **optical assembly** that turns the bulb into a **laser**: same underlying photons, dramatically narrower beam, dramatically more useful work per watt.
- "Even lasers scatter" — non-determinism doesn't disappear. But the scatter cone shrinks from "wide-angle floodlight" to "tight beam with a known divergence angle." That residual scatter is what evals, human review, and guardrails catch.

**What that reframes:**
- The **product** isn't the model. The product is the **optics around the model.**
- The **moat** isn't access to the model (everyone has that). The moat is the **engineered scaffolding** that focuses a generic model onto a specific domain (medtech DHFs, regulatory submissions, etc.).
- "Prompt engineering" → too narrow a term. We're doing **probability-shaping engineering**: every skill, rule, hook, and agent narrows the distribution of what the model is likely to do next.
- This is *also* why the compiler analog breaks — a compiler's optics are fixed by the language spec. With agents, **we author the optics** for our domain.

**Concrete examples from this project as evidence:**
- Task gate hook → narrows "what files can be touched right now" from "all files" to "files relevant to the active task."
- Skill registry + glossary → narrows vocabulary from "anything in training data" to "this project's controlled terminology."
- Agent panel + advisors → narrows perspective from "generic helpful assistant" to "regulatory affairs / clinical / V&V / quality engineer / R&D lead viewpoints."
- DHF topology + medtech-docs skill → narrows document structure from "any plausible org" to "21 CFR 820 / ISO 13485 design controls layout."
- `/trace-matrix` + `/dhf-manifest` → narrows "is this a complete submission" from a fuzzy judgment to a measured gap report.
- Evals + lessons ledger + best-practices audit → close the feedback loop so the optics get *re-ground* over time as we learn where the beam is still scattering.

**One-liner candidate for the whitepaper:**
> "A model is a light source. Agent engineering is the optics. The product is the focused beam."

<!-- STRATEGY CONTENT: development, agent-engineering-discipline -->
The compiler/assembly analog gets us to "abstraction-up-the-stack" — useful for skeptics. The **laser/optics analog** is the better load-bearing metaphor for the whitepaper because it (a) explicitly accounts for non-determinism (residual scatter), (b) names what we actually build and sell (the optics, not the bulb), (c) explains why generic-model access doesn't commoditize the work (the optics are domain-specific IP), and (d) frames evals/hooks/guardrails as part of the same beam-shaping discipline rather than disconnected QA. Recommend: open the whitepaper with the compiler analog as familiar ground, then pivot to the optics framing as the main thesis.
<!-- /STRATEGY CONTENT -->

### Seed: Quality-first, then productivity *(Ben, 2026-04-27)*

**Agentic systems are always probabilistic — but so is knowledge work.** Humans don't make deterministic decisions either. That's exactly *why* great decision-making is so critical, and why teams invest in diverse datasets, multiple perspectives, peer review, and structured deliberation: those are all techniques to **shape the probability distribution of the decisions a team produces.**

So the real question isn't "is the agent deterministic?" — it's "**is the agent's output distribution better than the team's baseline distribution?**"

**The sequencing claim — quality before productivity:**

1. **First, raise the quality bar above your current baseline.**
   - Use agentic approaches to lift the floor: catch the things humans miss, enforce consistency humans drift on, surface the trace links humans skip, run the audits humans defer.
   - This is where agents earn trust — by demonstrably producing *better-quality work than the unaided team* on tasks the team already does.
   - Quality wins are also more politically palatable than productivity wins (no one is threatened by "fewer defects"; some people are threatened by "fewer headcount needed").

2. **Then, unleash productivity with human-in-the-loop calibrated to the task.**
   - Once the quality bar is raised, *now* you can start automating — because you've established the trust and the measurement infrastructure to know when automation is safe.
   - Human-in-the-loop is not a binary; it's a **dial** that varies by stakes: full review for safety-critical work, sample review for routine work, exception-only review for high-volume / low-stakes work.
   - The right HITL level is itself an engineering decision — and it changes over time as evals improve and the optics get re-ground.

**Why this sequencing matters for GTM and pre-sales:**
- "Agents will save you 30% on engineering cost" — credible only if quality is at least matched. Otherwise it's a discount, not a value prop.
- "Agents will raise the quality of your work AND eventually save you cost" — that's a defensible, durable pitch.
- Pre-sales should scope engagements as **quality-baseline-then-productivity**, not "drop in agents to write code faster." The first phase is measurement + scaffolding; productivity is the second phase that gets unlocked.

**Diversity-of-datasets parallel:**
- Just as humans make better decisions with diverse data and diverse perspectives, agent panels (advisors, multi-agent reviews) replicate that pattern in software.
- Single-agent: one perspective, one distribution. Council-of-agents: a *mixture* of distributions, with the ability to weight, reconcile, or escalate disagreement.
- This is why our project-console agent panels, the design-review-panel, and the core-team-panel exist: not gimmicks — they're the structural way to import "diversity of perspectives" into a probabilistic system.

**One-liners candidate for the whitepaper:**
> "Knowledge work has always been probabilistic. The discipline isn't eliminating uncertainty — it's shaping the distribution."
> "Agentic systems earn productivity by first earning quality."
> "Human-in-the-loop is a dial, not a switch."

<!-- STRATEGY CONTENT: development, agent-engineering-discipline -->
The "quality first, then productivity" sequencing is the **GTM-defensible pitch** and should be a load-bearing section of the whitepaper. It directly counters two failure modes: (a) the cynical "this is just a cost-cut" framing that triggers organizational antibodies, and (b) the naive "let agents drive" framing that produces low-quality work and burns trust. Pair this with the diversity-of-perspectives → multi-agent-panel mapping as evidence that we treat decision-quality as an engineering problem, not just a model-selection problem.
<!-- /STRATEGY CONTENT -->

### Seed: Differentiators — "we use Copilot, doesn't that make us agentic?" *(Ben + review pass on project-overview / how-to-guide / repo, 2026-04-27)*

The market is full of "we are agentic" claims. They fall into three buckets — and our approach sits in a fourth.

**Bucket 1 — Code-completion vendors rebranded.** GitHub Copilot, Cursor, Codeium, Gemini Code Assist. Inline completions and a chat sidebar. Speeds up *typing*. Doesn't change the SDLC, doesn't enforce process, doesn't know your domain, leaves no audit trail beyond a git diff.

**Bucket 2 — Chatbot bolted onto an existing delivery process.** "We added an LLM to our dev workflow." A model-in-the-loop, not a system. The work product is unchanged; only the input method changed.

**Bucket 3 — Vendor-locked agentic platforms.** Big SI claims (EPAM, Cognizant, Wipro, etc.) of an "agentic delivery platform" or "agentic studio." Often: a closed product, a small library of internal agents, a marketing skin over a chat UI, or a pilot project with hand-tuned prompts that doesn't generalize. The agentic capability is rented from the vendor; the customer gets a deliverable, not the system that produced it.

**Bucket 4 — Where our approach sits: agentic *project shape* as the deliverable.** We don't sell labor that happens to use agents. We sell **a project structure that is itself the agentic operating model** — every artifact, hook, skill, agent, rule, and registry is in the customer's repo, versioned, reusable, and auditable.

**Concrete differentiators visible in PDLC_DEMO right now:**

| # | Differentiator | What it actually is in this repo | Why bucket 1–3 don't have it |
|---|---|---|---|
| 1 | **Hard task gate on every edit** | `.claude/hooks/check-active-task.sh` denies Edit/Write unless the session has an active task. No orphan AI edits, ever. | Copilot/Cursor have no concept of a task; chatbot wrappers can't enforce on filesystem; SI platforms don't ship a hook into the customer's workstation. |
| 2 | **Domain-ground optics, not horizontal** | `medtech-docs`, `dhf-manifest`, `trace-matrix`, `change-control`, IEC 62304 / ISO 13485 / 21 CFR 820 baked into the scaffold + advisor grounding. | Horizontal tools are deliberately domain-agnostic. SI platforms claim verticals but rarely ship the verticalization as inspectable code. |
| 3 | **Multi-perspective panels, not single answers** | `core-team-panel`, `design-review-panel`, `kol-panel-pp3500` — round-robin advisors with citations + counterpoints. | Copilot/Cursor are single-voice. Most SI offerings are also single-voice with a personality skin. |
| 4 | **Same agents, two runtimes** | `tools/project-console/` (browser/FastAPI) and Claude Code (CLI) read the same `.claude/agents/*.md` files. Update once, both surfaces update. | Vendor platforms decouple their chatbot from the IDE; updates drift. |
| 5 | **Public-method scaffolding** | Every skill is markdown + shell + Python, all in-repo, all readable. The optics are *transparent IP*, not a black box. | SI platforms sell the output of their black box; you can't audit it, fork it, or extend it. |
| 6 | **Probability-shaping infrastructure** | Hooks, rules, `<!-- STRATEGY CONTENT -->` capture, `[VERIFY]` discipline, demo-banner discipline, advisor counterpoint pass — every layer narrows the model's output distribution. | Copilot has temperature controls and a system prompt. That's it. |
| 7 | **Auditable trace from intent → artifact** | `tasks/<person>/NNN-*.md` → strategy harvest → DHF doc → trace matrix → V&V → submission. Every leaf is traced back to a human-owned task. | Bucket 1 has git diffs; bucket 2/3 have chat logs. Neither is an audit trail a regulator will accept. |
| 8 | **Measurable gap reports, not vibes** | `/trace-matrix` finds 30 DI orphans on PP3500. `/dhf-manifest` projects regulation+QMS through a scope vector and tells you what's missing. `/best-practices` runs a standing audit. | "Our agent reviewed your code" is a claim. A gap report with line numbers is a measurement. |
| 9 | **Shared, versioned skill registry** | `hitachi` registry → `/sync-skills` pull/push with PR + opt-in auto-merge. Improvements made on one project flow to all sister projects. | SI platforms version their internal tooling; you never see the changelog. Copilot updates on a vendor schedule outside your control. |
| 10 | **Bidirectional change control to enterprise systems** | `change-control` skill bridges GitHub draft → Confluence + Comala (Part 11 review) → Windchill (release vault). Freeze-point lifecycle enforced by hook. | Bucket 1–3 stop at the IDE / chat. None of them handle the QMS-of-record handoff. |
| 11 | **Configurable human-in-the-loop dial** | `advisors.enabled` curates which agents are on. Hooks gate which actions need an active task. Roles like "agent never occupies decision step 3 or QMS sign-off step 6" are explicit and enforced. | Other tools have an on/off switch, not a dial keyed to risk class. |
| 12 | **Lessons + best-practices feedback loop** | `/lessons` harvests insights → ledger → promotes to skill / rule / glossary / agent prompt. `/best-practices` is itself authored against the project. The system *re-grinds its own optics* over time. | Vendor models improve on the vendor's roadmap. Our system improves on the project's roadmap. |
| 13 | **`project.yml` as single source of truth** | One manifest defines identity, DHF topology, team, registries, security allowlists, advisor curation. Drift between settings, hooks, agents, and policy is mechanically detectable. | Vendor stacks scatter config across consoles, dashboards, and admin UIs — drift is invisible. |
| 14 | **Three-tier advisor grounding** | Universal (FDA + ISO/IEC) + shape-stable (medtech-docs paths) + project-overlay (`project.yml → advisors.overlays.<name>`). | Most "agents" use a single system prompt + RAG dump. No structured grounding model. |
| 15 | **Built-in fabrication discipline** | `[VERIFY]` flag rule + `_Demo sample data — not for clinical use._` banner rule + "never fabricate standards/clinical/regulatory content" rule, all encoded in `CLAUDE.md` and enforced via review. | "Hallucination prevention" in vendor pitches is a model parameter. Ours is a project convention with auditable artifacts. |
| 16 | **Open-architecture, not vendor-trapped** | Skills are markdown + scripts. Agents are markdown. Hooks are shell. `project.yml` is YAML. Run it on-prem, sovereign-cloud, or air-gapped. | Vendor platforms require their cloud / their model / their license. |

**The one-sentence differentiator:**

> "Most teams have an LLM in their workflow. **We have a workflow that is itself the LLM operating model** — versioned, audit-trailed, domain-ground, and reusable across projects."

**Or, against a specific competitor pitch:**

> "EPAM (or any SI) will sell you a project they delivered with their agentic stack. We hand you the project *and* the stack, in your repo, under your audit."

**What this means for the whitepaper:**
- The "doesn't using Copilot make us agentic?" objection is the **most-asked GTM question** and deserves a dedicated section. Pin it down with the bucket-1-through-4 framing.
- The differentiator table should appear in the whitepaper near-verbatim — it's the answer to "what makes you different" for a buyer who is comparing vendors.
- For pre-sales: every row in the table is an **accelerator** they can point at on day one of an engagement. The customer isn't paying for them to be invented; they're paying to have them tuned.

<!-- STRATEGY CONTENT: commercial, agent-engineering-positioning -->
**Positioning thesis:** the market is saturated with "agentic" claims that are really code-completion-plus-chat. Our durable differentiator is **agentic project shape as the deliverable** — every guardrail, agent, hook, skill, and registry lives in the customer's repo, versioned, public-method, and auditable. SI competitors (EPAM et al.) sell labor that uses their internal agentic stack; we sell *the stack* alongside the labor, embedded in the customer's project, transferable. This is the load-bearing claim that justifies premium pricing in regulated verticals (medtech, fintech, defense) where audit transparency is a feature, not a tax. The whitepaper's competitive section should call out the four buckets explicitly so buyers have a framework to evaluate other "agentic" pitches against ours.
<!-- /STRATEGY CONTENT -->

<!-- LESSONS LEARNED: commercial-positioning -->
When a prospect says "we already use Copilot/Cursor/Gemini, we're already agentic," the right move is **not** to argue about agents — it's to ask: *"can your auditor open your repo today and see every guardrail enforced?"* Copilot users say no. The pivot is from "do you use AI?" (everyone does) to "is your AI usage auditable, reusable, and project-shape-bonded?" (almost no one's is).

**Why:** Reframes the conversation from feature-comparison (Copilot vs. Claude) to system-property comparison (auditable agentic shape vs. ad-hoc usage). Buyers in regulated industries respond to the second framing because it's the one their compliance org will ask about.
**How to apply:** In GTM conversations, lead with audit-trail and project-shape, not model brand or productivity %.
<!-- /LESSONS LEARNED -->

### LOCKED THESIS (2026-04-27)

> **Agent engineering is the next logical evolution of software engineering — the discipline of building reliable systems out of non-deterministic generators by engineering the optics around them.** The deliverable is not the model, and not the labor that uses it: the deliverable is an **agentic project shape** — a versioned, audit-trailed, domain-ground operating model that lives in the customer's repo, **raises the quality bar before harvesting productivity**, and **improves itself over time** through a registry-mediated feedback loop.

Three load-bearing claims under the thesis:
1. **Evolution claim.** Just as compilers, CAD, SPICE, FEA, and BIM each turned a "describe intent → machine produces the lower-level artifact" relationship into a discipline, agents are doing this now for the synthesis-of-knowledge-work layer above code.
2. **Optics claim.** A bare model is a broadband light source. Skills, rules, agents, hooks, registries, and trace tooling are the optics that focus it. The product, the moat, and the IP are the optics — not the bulb.
3. **Sequencing claim.** Quality first, productivity second. Once the floor is raised and the audit trail exists, productivity gains are durable; without that floor, productivity gains are a discount that erodes trust.

### Cross-project proof points — collected

Sister-project survey (anonymized, structural facts only):

**Same-shape evidence (parity).**
- Identical core scaffold: 23 skills under `.claude/skills/` with 100% overlap (advisors, best-practices, change-control, dhf-manifest, digest, docflow, docx, lessons, medtech-docs, pdf, pptx, project-console, secops, skill-creator, strategy, sync-skills, task, trace-matrix, tracker, web-control, xlsx, plus shared/).
- Identical agent roster: 14 persona agents (clinical-affairs, core-team-panel, cybersecurity, design-review-panel, human-factors, post-market, program-manager, project-secops, quality-engineering, rd-lead, regulatory-affairs, risk-management, systems-engineering, vnv-lead).
- Identical hook backbone: task-gate (`check-active-task.sh`), session-env, session-cleanup, secops-assert, docflow direct-conversion blocker, digest session-briefing.
- Identical artifact spine: `CLAUDE.md`, `project.yml`, `glossary.md`, `CHANGELOG.md`, `project-overview.{md,pptx}`, `tasks/<person>/NNN-*.md` with `000-index.md`, `tools/project-console/`, `trace-matrix.yml`.

**Scale & maturity signals.**
- Sister project: ~163 task documents across 12 active team members. PDLC_DEMO: ~37 task documents across one. Same shape; 4.4× more task corpus and 12× the team size on the sister side. The shape *holds at scale*.
- `CHANGELOG.md` automatically curated by `/digest log` — 892 lines on the sister project. Continuous, not episodic.
- `.claude/sync-log.md` is itself a lessons registry — every sync entry names the originating task, the change rationale, the affected scope, and the merge status.

**Registry-driven leverage (improvements flow across projects).**
- Most recent registry push (2026-04-27): a "default-to-action" task-skill rubric originated as a per-team-member behavioral correction, was promoted into the shared `task` skill v23 → v24 via PR, and is now the default behavior on every project that pulls the registry. **One person's correction; all projects' improvement.**
- Sequential skill iteration tied to task numbers: `project-console` v1.4.1 → v1.7.6 in five days, each version tagged to the originating task. The skill is *evolving in production*, not delivered as a static artifact.
- Setup hardening (cross-platform Python discovery for `web-control` and `change-control` setup) originated on the sister project, merged into the registry, verified across four harnesses (28/28 + 31/31 + 30/30 + 26/26 test suites). Same fix landed in PDLC_DEMO on the next pull.
- `docflow` skill: 15 versions tracked in CHANGELOG, each version citing the specific task and user feedback that triggered the change. Tight loop: observation → fix → registry → adoption.

**Self-improving evidence.**
- Hook redesign logged in CHANGELOG: an early multi-hook strategy/lessons capture flow killed conversational flow; was retired and replaced with a strategy-doc-centric conflict flow (registry PR #75, 2026-04-23). The system *retired its own bad design*.
- Performance optimization cycle: an audit found 17 SKILL.md files were loading ~610 lines of best-practices/changelog content into every session. The audit task fixed it project-wide by moving content to README.md. Live context footprint reduced everywhere.
- Tool-validation infrastructure (IEC 62304 §8 compliance: tool inventory + validation workstream) was built on the sister project as a task, then canonicalized into project structure available to any project that needs it.
- Title-field enforcement audit on 229 obligation/QMS records added three enforcement gates (validation script + grep guard + post-build audit). The skill version bumped, synced to registry, propagated.

**Conclusion of the survey.** The shape generalizes. **100% structural parity** on the agentic-infrastructure layer; the variation is **only in domain content** (which device, which pathway, which classification). The agentic project shape is reproducible.

### Whitepaper revision backlog (open items — capture-only, work sequentially)

> Items we've identified that need work on the whitepaper. **Don't fix yet — work through them one at a time so we can review each pass together.** Priority is the order I'd suggest tackling, not strict.

| # | Pri | Item | Source | Notes / approach |
|---|----|------|--------|------------------|
| **R1** | 1 | **Add a "Section Map" table after the Intents section** — small table: column 1 = section number/name, column 2 = the *one or two key points* that section is supposed to land. Used to validate that the order makes sense and each section earns its place before any further wordsmithing. | User, 2026-04-27 | Should be ~9 rows (Exec Summary, §1, §2, §3, §4, §5, §6, §7, Appendices). One-line claim per row, max two. This becomes the contract for what each section must do. |
| **R2** | 2 | **§1 doesn't land — too much detail.** Five subsections (1.1–1.5) is too many for the opening argument; the reader is in the weeds before they have the thesis. Tighten the whole section. | User, 2026-04-27 | Likely consolidation: collapse §1.1 (engineering-discipline table) + §1.2 (trust-building + AI-in-PDLC vs. AI-in-product) + §1.3 (optics) into a single tighter argument. The discipline-explainer table can be moved to an appendix or kept as a smaller inline reference. The "AI-in-product carve-out" must stay topline (Intent #4) but can be 2–3 sentences not a sub-section. |
| **R3** | 3 | **Title is too long.** "Agent Engineering: The Next Logical Evolution of the Product Development Life Cycle" is descriptive but not memorable. Need something short, sharp, and quotable. | User, 2026-04-27 | Candidates to brainstorm later: e.g., *Bulb & Optics*, *Engineering Up the Stack*, *The Optics Are the Discipline*, *Generate. Inspect. Accept. Compound.* Don't lock until R1/R2 are done — the title should reflect the tightened argument. |
| **R4** | 4 | **Tagline wordsmith pass (both GL-internal and Customer-facing).** Currently sit in §7.1 as working drafts. | Standing item, 2026-04-27 | Defer until structural revisions (R1, R2) settle. Wordsmithing taglines before the body is final invites rework. |
| **R5** | 5 | **Audit the Intents section vs. exec summary "Key claims" list for redundancy.** Both currently sit at the top and may be saying overlapping things in different shapes. | Latent, noticed during review | After R1 and R2 land, re-read the top 30 lines cold. If Intents + Key Claims feel duplicative, collapse one. |
| **R6** | 6 | **Pressure-test §3 (differentiation) and §4 (proof points)** — most likely to need revision once §1 is tightened. | Latent | The 4-bucket framing in §3.1 may need softening; "vendor-locked agentic platform" is true but pointed. The §4 "Project A / Project B" labeling could be cleaner. |
| **R7** | 7 | **§6.3 is now long (~50+ lines after the org-design expansion).** Worth checking it doesn't overshadow §6.1, §6.2, §6.4 in the Pre-Sales cut. | Latent, 2026-04-27 | After the body settles, decide whether to keep the full skillset treatment in §6.3 or move part of it to an appendix. Intent #3 must still pass. |
| **R8** | 8 | **Length re-check.** Whitepaper is now ~8,500 words / 481 lines — at the upper edge of "short." If R2 tightens §1 substantially, recheck whether the rest still holds proportions. | Latent | Target: stay under 7,500 words after the §1 tightening. |
| **R9** | — | **Technical Addendum: "How the Optics Were Actually Built."** New addendum capturing the human-driven process behind the agentic project shape — Ben's redirections, on-the-go strategy calls, and the iteration loops that produced the skills/hooks/conventions. Tracked as Phase 5 with its own sub-phases (5a–5e). | User, 2026-04-28 | Distinct deliverable from R1–R8 (which are wordsmith/structural passes on the existing body). R9 is additive: a new section that the existing body doesn't have. Sources: PDLC-DEMO + arthrex-pccp task corpora, CHANGELOGs, sync-logs, chat history. Plan locked in §"Phase 5" todos above. |

**How we'll work this:** one item per pass, review together at each step, then move on. R1 is the natural starting point — building the Section Map first will surface whether other sections share §1's "too much detail" problem before we go fix them piecemeal.

### Whitepaper outline (locked)

1. **Executive summary** — one page, both audiences.
2. **The argument: agent engineering as the next logical evolution** — compiler/assembly analog, where it parallels and where it breaks; the laser/optics framing; knowledge work as probabilistic.
3. **The discipline: what agent engineering actually is** — new artifacts (skills, hooks, rules, agents, registries, evals); the probability-shaping stack; quality before productivity sequencing.
4. **What makes our approach different** — four-bucket framing of "agentic" claims; differentiator table; the one-line counter.
5. **Proof points** — cross-project parity, registry-driven leverage, self-improvement, measured gap reports.
6. **For Go-To-Market teams** — value prop, market direction, opportunities, talk-track.
7. **For Pre-Sales Engineering teams** — engagement scoping, accelerators, skillset profile, cost model.
8. **Objections & answers** — hallucination, IP, regulatory acceptance, lock-in, talent flight, skill atrophy.
9. **Call to action.**

### Other seeds to develop (placeholders — kept for reference)

- **Other engineering analogs:** mech engg before CAD/CAM; EE before SPICE/Verilog; structural before FEA; civil before BIM; chip design RTL → synthesis; control theory → autopilot.
- **What's actually new vs. classical SE:** non-determinism, evaluation-as-engineering, prompt/scaffold as source artifact, tool-use design, memory design, agent topology, governance.
- **Skillset shifts:** prompt/scaffold designer, eval engineer, agent ops, governance/auditor, human-in-the-loop UX designer.
- **Cost projection model:** scaffolding cost (one-time, amortized) + run cost (per-token / per-task) + human review cost (declining curve) — vs. classical staffing model.
- **Risk/objection bank:** "hallucination," "IP contamination," "regulatory acceptance," "lock-in," "talent flight," "skill atrophy."

---

## Open Questions

- Whitepaper length target — 8 pages? 15? 25?
- One whitepaper with GTM/Pre-Sales callouts, or two cuts of the same source?
- Public-facing or internal-only first?
- Brand: GlobalLogic-branded? Vendor-neutral? Co-branded?
- Does PDLC_DEMO show up as the worked example, or is the whitepaper abstract?

---

## Strategy & Lessons Learned

> Strategy and lessons captured inline above with `<!-- STRATEGY CONTENT -->` and `<!-- LESSONS LEARNED -->` markers. The `/strategy` and `/lessons` harvest skills will pull from those blocks.

---

## Changelog

- 2026-04-27: Task created. Captured opening seed (compiler/assembly → LLM analog) with full where-it-parallels / where-it-differs analysis. Strategy block recorded the framing decision: use the analog as a hook, anchor on "agent engineering = building reliable systems out of non-deterministic generators." Phase 1 brainstorm placeholders staged for the next turns (other engineering analogs, value prop, market direction, GTM/pre-sales cuts, accelerators, cost model, objections).
- 2026-04-27: Captured laser/optics extension to compiler analog. Strategy block recommended using compiler analog as the hook and pivoting to optics framing as load-bearing thesis (accounts for non-determinism via residual scatter, names what we sell, explains why model access doesn't commoditize the work, frames evals/hooks/guardrails as part of the same beam-shaping discipline).
- 2026-04-27: Captured quality-first-then-productivity sequencing seed. Strategy block flagged this as the GTM-defensible pitch that counters both the cynical cost-cut framing and the naive let-agents-drive framing. Mapped diversity-of-perspectives → multi-agent-panel as the structural way to import human decision-quality techniques into a probabilistic system.
- 2026-04-27: Reviewed `project-overview.md`, `how-to-guide.md`, `CLAUDE.md`, `.claude/skills/`, `.claude/agents/`, `.claude/hooks/`. Authored 16-row differentiator table contrasting "agentic project shape as the deliverable" against three competitor buckets (code-completion vendors rebranded, chatbot bolted onto existing process, vendor-locked agentic platforms). Strategy block recorded positioning thesis. Lessons block captured the "evidence-not-agent" reframe move for GTM conversations.
- 2026-04-27: User upgraded effort to max and authorized go-to-completion. Locked thesis at top of brainstorm. Spawned Explore agent against sister project `/home/benxavier/project/arthrex-pccp/` to harvest cross-project structural proof points (anonymized). Captured proof points: 100% structural parity (22 skills, 14 agents, 6 hooks, identical artifact spine), 4.4× task corpus / 12× team scale on sister, registry-driven leverage (task v23→v24, console v1.4→v1.7, 115-test cross-harness verification, 15-version docflow iteration), self-improvement evidence (hook redesign, ~610-line context audit, tool-validation infra, 229-record title enforcement).
- 2026-04-27: **Topline-message rewrite of §1.2 (post-author review).** User flagged that the original §1.2 ("Where the analog breaks") was true but technical-appendix material, not topline messaging. Reframed §1.2 around the load-bearing distinction: *the generation step is stochastic, but the accepted artifact is deterministic and version-controlled — the same kind of artifact the customer's QMS already accepts.* Added explicit AI-in-SDLC vs. AI-in-product split (the latter is a different discipline with different controls; called out so the two aren't conflated, but explicitly out of scope here). Demoted the four-divergence table to Appendix A as craft-level detail. Aligned exec-summary key claims (#2 now: "the accepted artifact is deterministic"), §1.3 laser-scatter framing (residual scatter is caught *before* acceptance), and §1.4 ("probabilistic deliberation → deterministic signed artifact" parallel). Glossary appendix renumbered to Appendix B.
- 2026-04-27: **Three further user-driven structural changes.** (a) Scope corrected from "SDLC" to **HCLS PDLC** throughout — title, scope note, exec summary, §1.2, §2, §6, §7, §3.1 differentiator table all rewritten so the same agentic thinking applies across code, DHFs, V&V, submissions, post-market, and the corrective-action loop. (b) Added **business-friendly explainer table for CAD/SPICE/FEA/BIM** at the top of §1.1 — each tool given a plain-English "before world / after world / what it's called" row so a non-technical reader doesn't have to know the acronyms ahead of time. (c) Added **Intents — the rubric this paper holds itself to** as a new section just before the Executive Summary: five testable intents (GTM mental model, memorable analogies, organizational shift, scope honesty, claim grounding) plus pass criteria each anchored to a specific section. The Intents are designed as a quality contract a reviewer can hold us to.
- 2026-04-27: **§6.3 expanded to answer Intent #3 explicitly.** Now contains: 5-role delivery team table (with the genuinely new role flagged), the three load-bearing traits of a great agent engineer (writes clearly and expertly, has strong domain "good vs. not-good" instinct, thinks in systems), supporting strengths, three org-design implications (senior-engineer track gets a new artifact: skill authoring; technical writing becomes load-bearing; domain experts step into the optics), and a "how to identify the people you already have" finder list. Whitepaper grew from ~5,500 words to ~8,500 words with these additions.
- 2026-04-27: **Closing restructured to carry two taglines (working drafts).** §7.1 now explicitly identifies a **GL-internal tagline** (current working draft: *"We don't sell labor that uses agents. We sell the agentic project shape that produces the labor's best work."*) and a **customer-facing tagline** (current working draft: *"Own the way your team builds — not just the work they ship."*). Each carries an Audience / Job-to-be-done / Why-this-audience block so the wordsmith pass has explicit constraints to optimize against. Both flagged as working drafts to revisit in a marketing pass. Decision recorded: structural shape (one inward, one outward, both anchored on project-shape thesis) is locked; specific wording is not.
- 2026-04-27: **Captured whitepaper revision backlog (R1–R8).** User flagged three structural concerns: title is too long / not memorable (R3); §1 doesn't land — too much detail (R2); paper needs a Section Map table after the Intents to validate sequencing before further work (R1). Plus R4 (tagline wordsmith — already a known item) and four latent items I added from review (R5–R8: redundancy between Intents and Key Claims, §3/§4 pressure-test, §6.3 length check, total length re-check). Approach: work items sequentially, one pass at a time, with review at each step. Starting point per user direction: **R1 next** — build the Section Map. **No content changes made this turn — backlog only.**
- 2026-04-29: **Stopping point — both whitepapers and PDF locked at user-approved state. Deck deferred to new task ben/038.** Final state: source whitepaper `agent-engineering-whitepaper.md` (~199 KB, ~16K words) + executive cut `agentic-delivery-whitepaper.md` (~89 KB, ~10K words) + PDF `agentic-delivery-whitepaper.pdf` (634 KB, 22 pages letter, 0.55in margins). Investment case grounded in tiered model (Tier 1 ~$8K, Tier 2 ~$2.5–3K, Tier 3 ~$0.5–0.8K) with three-cost-center geographic mix (US / EE+India International). Margin trajectory uses non-linear compounding curve (+1–2 / +4–5 / +9–10 / +13–15 / +18–20 pp over Years 1–5) with eight explicit assumptions beneath the table. Industry benchmark table grounds the firm position (35–47% Int'l / 40–60% US already above HCLS / Engineering R&D / IT-mainstream / Automotive averages). Both Mermaid diagrams (Conductor in §C.3.1 and Flywheel in §6.6) render correctly in PDF — Conductor cluster contains both Calibration Mode + Domain Mode, Flywheel shows all six nodes with revised labels — and the source mermaid syntax now parses in mermaid 8.x markdown viewers. Italic-merge bug, tex_math_dollars escape, --wrap=none, and duplicate-title strip all baked into pipeline. Self-test loop (render → JPG → Read tool visual inspection → only commit if diagrams pass) added to working memory for future renders. Final commit: `ce3bd06` on `main`. **Phase 4 deck work spun out as ben/038 — beautiful, professional, tech-forward presentation of the whitepaper.**
- 2026-04-29: **PDF diagram polish — Mermaid label-clipping + LR aspect-ratio fixes added to the captured pipeline.** The label-clipping issue from Phase 6 insight #13 has a working fix: post-process the mmdc-rendered SVG to enlarge `<rect>` heights *and* `<foreignObject>` heights by ~30% (with proportional repositioning of the inner label `<g transform="translate(...)">` to keep content centered). Combined with bumping the mermaid render config to `fontSize: 22` and `flowchart.padding: 22`, this eliminated label clipping in the §6.6 Flywheel. **Aspect-ratio finding:** wide LR diagrams scaled to page width render with very small text (a 2074:230 viewBox at 614px page-width = 68px tall). Fix: switch wide LR diagrams to TB layout in the source mermaid block. Did this for the Conductor diagram — now renders TB at full readable scale on a single page. Both fixes belong in the `/whitepaper` skill's render action: an automatic post-process pass for label-rect enlargement, plus a heuristic ("if viewBox aspect ratio > 4:1, suggest TB layout") that warns at render time.
- 2026-04-29: **PDF generation pipeline built end-to-end and captured for skill extraction.** Authored `/home/benxavier/project/PDLC-DEMO/agentic-delivery-whitepaper.pdf` (516 KB, 17 pages, letter, 0.55in margins) from the new `agentic-delivery-whitepaper.md` source. Pipeline: pandoc → HTML (with `--wrap=none`!) + mmdc-pre-rendered Mermaid SVGs (with unique IDs to avoid `#my-svg` collision) + Chrome headless `--print-to-pdf`. Surfaced and corrected three load-bearing failures along the way: (a) browser-side mermaid render is unreliable under chrome `--print-to-pdf` (timing/snapshot race) — fix is mmdc CLI pre-rendering; (b) pandoc default `--wrap=auto` inserts newlines inside SVG `<style>` strings (`"trebuchet ms"` becomes `"trebuchet\nms"`) which kills CSS and makes diagram nodes render with default browser styling — fix is `--wrap=none`; (c) pandoc `--standalone` + `--metadata title=` emits a duplicate `<h1 class="title">` body block alongside the markdown's own first H1 — fix is post-process strip of the `<header id="title-block-header">` wrapper. Also added Phase 6 to this task doc capturing the full pipeline + a skill-scaffolding sketch for future lift into `.claude/skills/whitepaper/`. **Insight is in the doc; skill build is deferred per user direction.**
- 2026-04-28: **Phase 5 expansion — C.7 Spec Primacy, C.8 One-Shot vs Scale, C.9 Guardrails as Layered Defense added.** User authorized unbounded length, formatting/categorization-first, with three explicit asks: (1) why specs > model choice, (2) why one-shot doesn't scale and what does, (3) guardrails as layered defense — pattern, layers, why layers matter. Ran 2 more parallel Explore agents to harvest hard evidence. Drafted three new top-level subsections totaling ~4,000 words, all heavily tabled for skim-readability: **C.7 Spec primacy** (4-row diagnosis-vs-root-cause table; 4 properties of a sharp spec; 7-row spec catalog by category; explicit ranked investment recommendation: specs first, scaffolding second, model choice third; one counter-evidence note for cases where model choice mattered first); **C.8 One-shot vs scale** (3 reasons one-shot fails for HCLS; 3-row table of scaffolding optimizations A/C/F with 80%+ re-run cost reduction; idempotency as repeatability contract; 6-row scale-numbers table); **C.9 Guardrails as layered defense** (6-row layer table L1–L6 with purpose / when-runs / cost / examples for each; the four-property pattern that every layer shares; 4 hard cases of higher-layer-catches-lower-layer-miss with verbatim evidence; 4-row cost-of-layers table; one-line synthesis; HCLS multiplier subsection). Section C.10 (formerly C.7) "Hiring and staffing" preserved at the end. Final whitepaper: **770 lines / ~15,359 words.** Anonymization grep clean. The new sections deliberately use heavy table formatting throughout — every pattern lookup, every layer comparison, every cost is in a table that a reader can scan in seconds rather than parse from prose. The argument shape: C.7 names the lever; C.8 shows why scaffolding makes the lever operational at scale; C.9 shows the safety architecture that makes scale survivable; the HCLS multiplier in C.9.6 closes the regulatory case.

- 2026-04-28: **Phase 5 complete — Appendix C "How the Optics Were Actually Built" landed.** User authorized run-to-completion with explicit ask for counterpoints. Ran 5a (wide scan + 10-category lock) → 5b (5 parallel Explore agents covering paired categories against the corpus; hard examples with task IDs and verbatim quotes returned for all 10) → 5c (synthesized 5 meta-insights M1–M5; thesis sharpened: eval-engineer-mode + domain-expert-mode as a hybrid, not eval-engineer alone) → 5d (drafted ~2,800-word appendix with C.1–C.7 structure, including a C.6 counterpoints section explicitly added per user direction) → 5e (3 review passes: substance, tone/self-flattery, anonymization — all clean). Whitepaper is now 581 lines / ~11,344 words. **R8 length re-check is now urgent** but defensible because the addendum is appendix-ranked. **R1 Section Map remains the next wordsmith pass** for the body. The thesis-and-counter-thesis framing is the most load-bearing change from the original Phase 5 plan: the corpus showed a second class of corrections (outside-knowledge framings) that the eval-engineer thesis alone could not explain — so the addendum runs both modes as a hybrid, which is also the §6.3 trait list. Two genuine pressure-test counterpoints in C.6: multi-pass-is-sometimes-a-tax (task-gate triple-overhaul); built-then-retired implies prior over-engineering (real cost on the deleted capture hooks).
- 2026-04-28: **Phase 5 opened — wide scan + categorization done (5a).** User asked for a new addendum on the human-driven process behind the agentic project shape — how Ben's redirections, challenges, and on-the-go strategy guided the build. Wide-scanned both project corpora: 40 PDLC tasks + 125 arthrex tasks + 2 CHANGELOGs + 2 sync-logs. Locked **10 candidate categories** in the Phase 5 section above (C1 iteration-cycle, C2 process-failure-as-input, C3 scope/architecture redirect, C4 cross-project leverage, C5 verification/grounding, C6 performance/context-economy, C7 UX feedback, C8 process-discipline, C9 advisor-design, C10 self-improving meta-tools). Stated **working thesis** to test in deep dives: *the agentic project shape is the codified residue of a year's worth of human eval signal, with the registry as propagation channel — Ben played eval engineer in real time, not system architect after the fact.* Added R9 to the revision backlog. Phase 5b–5e are sequential, one category at a time with review at each step, with a stop condition that allows collapsing the back half if the thesis pressure-tests well after 5–6 categories. **No addendum content drafted this turn — plan only.**
- 2026-04-27: Authored short whitepaper at `/home/benxavier/project/PDLC-DEMO/agent-engineering-whitepaper.md` (~5,500 words / 396 lines, plus appendix). Structure: exec summary → argument (compiler analog + four divergences + optics + probabilistic-knowledge-work + quality-first sequencing) → discipline (new artifacts, probability-shaping stack, two-phase engagement) → differentiation (4-bucket framing + 14-row differentiator table + 3 one-line counters) → proof points (parity / scale / cross-project leverage / self-measurement / self-improvement) → GTM cut (value prop, market direction, 5 opportunity wedges, talk track, objection table) → Pre-Sales cut (engagement scoping, 11 accelerators, skillset profile, three-component cost model, 6 discovery questions) → closing → glossary. Two review passes complete: pass 1 fixed skill count (23→22) and softened compiler timeline; pass 2 grep-verified zero identifying marks and confirmed dual-audience usability.

---

## Resume Instructions

If a fresh session picks this up:
1. Read this file top to bottom.
2. **Status:** Phases 1–3 complete. Whitepaper landed at `/home/benxavier/project/PDLC-DEMO/agent-engineering-whitepaper.md`. **Phase 4 (deck build) is the open work.**
3. Activate the task: `bash .claude/hooks/task-activate.sh add 85d005cb-b12e-4703-aec2-0d012fa2c017 034`
4. Phase 4 plan: build a `scripts/build-agent-engineering-pptx.py` modeled on the ben/025 `scripts/build-project-overview-pptx.py` (GlobalLogic theme, full-bleed agenda + thank-you slides, 3-column cards, numbered section chips). Slides should map to whitepaper sections — opener, exec summary, the argument (compiler + optics), the discipline, the differentiator table, proof points (parity + scale + leverage), GTM call-outs, pre-sales call-outs, talk-track summary, closing. Speaker notes per slide. Output to repo root.
5. Open question for the user before starting Phase 4: brand the deck (GlobalLogic theme as ben/025), or vendor-neutral / co-brandable? Length target: ~20 slides like project-overview.pptx, or shorter executive cut?
