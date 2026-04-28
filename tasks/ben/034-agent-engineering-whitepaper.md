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

### Phase 4 — Deck build — NOT STARTED
- [ ] Slide outline mapped from whitepaper
- [ ] Build via `pptx` skill (likely a `scripts/build-agent-engineering-pptx.py` like ben/025)
- [ ] Speaker notes
- [ ] Review pass

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
- 2026-04-27: Authored short whitepaper at `/home/benxavier/project/PDLC-DEMO/agent-engineering-whitepaper.md` (~5,500 words / 396 lines, plus appendix). Structure: exec summary → argument (compiler analog + four divergences + optics + probabilistic-knowledge-work + quality-first sequencing) → discipline (new artifacts, probability-shaping stack, two-phase engagement) → differentiation (4-bucket framing + 14-row differentiator table + 3 one-line counters) → proof points (parity / scale / cross-project leverage / self-measurement / self-improvement) → GTM cut (value prop, market direction, 5 opportunity wedges, talk track, objection table) → Pre-Sales cut (engagement scoping, 11 accelerators, skillset profile, three-component cost model, 6 discovery questions) → closing → glossary. Two review passes complete: pass 1 fixed skill count (23→22) and softened compiler timeline; pass 2 grep-verified zero identifying marks and confirmed dual-audience usability.

---

## Resume Instructions

If a fresh session picks this up:
1. Read this file top to bottom.
2. **Status:** Phases 1–3 complete. Whitepaper landed at `/home/benxavier/project/PDLC-DEMO/agent-engineering-whitepaper.md`. **Phase 4 (deck build) is the open work.**
3. Activate the task: `bash .claude/hooks/task-activate.sh add 85d005cb-b12e-4703-aec2-0d012fa2c017 034`
4. Phase 4 plan: build a `scripts/build-agent-engineering-pptx.py` modeled on the ben/025 `scripts/build-project-overview-pptx.py` (GlobalLogic theme, full-bleed agenda + thank-you slides, 3-column cards, numbered section chips). Slides should map to whitepaper sections — opener, exec summary, the argument (compiler + optics), the discipline, the differentiator table, proof points (parity + scale + leverage), GTM call-outs, pre-sales call-outs, talk-track summary, closing. Speaker notes per slide. Output to repo root.
5. Open question for the user before starting Phase 4: brand the deck (GlobalLogic theme as ben/025), or vendor-neutral / co-brandable? Length target: ~20 slides like project-overview.pptx, or shorter executive cut?
