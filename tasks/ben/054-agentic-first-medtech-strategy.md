# 054 — Agentic-First MedTech Development: Strategy + Agent Team Design

**ID**: 054
**Created**: 2026-05-13
**Status**: Not Started
**Created By**: Ben
**Owner**: Ben
**Priority**: High

---

## PERMANENT RULES (do not remove)

This task document is the **session-recovery point** for this work. If the current session drops, is compacted, or ends, the next session must be able to load **this file alone** and continue where we left off. That is only possible if the doc is kept current in-flight.

1. **Update at every meaningful checkpoint (HARD RULE).** After each meaningful unit of work — a converted/adopted doc, a committed change, a launched batch, a completed phase, a decision, a discovered blocker, a design pivot — update this task doc: tick the relevant Todo checkbox, add a dated Changelog line naming the concrete artifact, update progress counts in Goals.
2. **Phase-end batching is OK; drift-batching is not.** Write at the phase boundary, before the next phase starts. If you can't name the specific upcoming checkpoint where you'll write the update, write it now.
3. **A commit is not a substitute.** Git history records code; this doc records the project narrative.
4. **Resume-ready before any session boundary.** Doc must contain: what was completed this session, status of in-flight work, priority-ordered next steps with file paths, open questions, exact `/task` activation command.
5. **Capture strategy + lessons as they happen.** Write inline `<!-- STRATEGY CONTENT: ... -->` and `<!-- LESSONS LEARNED: ... -->` blocks the same turn the insight surfaces.

Success test: a fresh Claude session, given only this file, can re-enter the work without asking "what were we doing?"

---

## Goals

Define a strategy and a working agent-team blueprint for running an **agentic-first MedTech product development lifecycle** on this project (PainEase PCA Advanced PP3500 as the anchor). The output should make it possible to take a feature from idea → design input → implementation → V&V → DHF evidence with agents driving the bulk of the work and humans gating the regulated checkpoints.

Concretely:

- **G1 — Agentic-first PDLC strategy.** A written position on which parts of the PDLC are agent-led, agent-assisted, or human-only, mapped against ISO 13485 design controls, IEC 62304 software lifecycle, ISO 14971 risk, and IEC 62366 usability. Identify the regulated control points where a human signature is non-negotiable.
- **G2 — Agent team blueprint.** A roster of agents (development, testing, validation, plus supporting roles like regulatory/QE/risk reviewers) with explicit responsibilities, inputs, outputs, hand-offs, and escalation rules. Cross-checked against the existing project agents under `.claude/agents/` so we extend rather than duplicate.
- **G3 — New skills / agents to build.** A prioritized list of new (or modified) skills and agents needed to operationalize the blueprint — each with a one-paragraph charter, trigger surface, and DHF-evidence contract.
- **G4 — Control + compliance harness.** How the agent team produces traceable, audit-grade DHF evidence (design inputs, design outputs, V&V records, risk file updates, change control) without humans hand-curating every artifact. Leverage existing skills: `trace-matrix`, `dhf-manifest`, `tracker`, `jira-pull`, `change-control`, `medtech-docs`, `task`, `lessons`.
- **G5 — Pilot scope.** A small, demoable feature slice on PP3500 (or a SaMD component) where the agent team executes end-to-end and produces real DHF artifacts — to prove the model before generalizing.

Out of scope for this task: actually building the new skills/agents (those will spawn child tasks once chartered).

## Todos

### Phase 0 — Frame
- [x] Read existing project agents in `.claude/agents/` and inventory their charters, inputs, outputs ✅ 2026-05-13
- [x] Inventory existing skills (`SKILL.md` headers) for what's already automated vs. what's not — group by PDLC phase ✅ 2026-05-13
- [ ] Re-read CLAUDE.md project structure + information flow to anchor the strategy in this project's reality (not a generic template)
- [ ] Capture working definitions: "agent-led", "agent-assisted", "human-only" — record in Strategy section
- **Phase-0 finding**: existing 15 agents are uniformly Tier-3 reviewer/advisor shape (Read/Glob/Grep only). The agentic-first gap is Tier-1 execution agents + Tier-2 orchestrator, NOT new skills. See Strategy block in task doc.

### Phase 1 — Agentic-first PDLC strategy (G1)
_Approach pivoted from a "PDLC-phase × control-posture matrix" to a chunked role-group discussion at user request (2026-05-13). Chunks 1–4 below replace the original matrix-first plan._
- [x] Chunk 1 — group model: THREE peer groups (Spec / Dev / V&V) ✅ 2026-05-13
- [x] Chunk 2 — edge topology: V-shape + two test universes + independence-by-charter ✅ 2026-05-13
- [x] Chunk 3 — constraint corpora: per-axis cross-group strategies (Architecture / Tooling / Technology) ✅ 2026-05-13
- [x] Chunk 4 — TDD linkage: form-neutral TC meta-pattern + content-hash audit + test-node anchoring ✅ 2026-05-13
- [ ] Chunk 5 — current-structure fit: mark each skill/agent Reuse / Extend / Create-new (feeds Phase 3)
- [ ] Map non-negotiable human checkpoints (design review approvals, risk acceptance, V&V sign-off, release authorization) onto the V-shape edges
- [ ] Walk one end-to-end agent flow for a sample PP3500 requirement to validate the frame

### Phase 2 — Agent team blueprint (G2)
- [ ] Draft roster: development agents (architecture, SW dev, FW dev, HW dev), test/V&V agents, validation agents, plus quality / regulatory / risk / human-factors / clinical-affairs reviewer agents
- [ ] For each agent: charter, trigger surface, inputs, outputs, escalation rules, hand-off contracts
- [ ] Define orchestration: which agent owns the feature ticket end-to-end, how reviewers are invoked, how disagreements escalate
- [ ] Cross-check against existing `.claude/agents/` to mark Reuse / Extend / Create-new

### Phase 3 — New skills/agents catalog (G3)
- [ ] List candidate new skills/agents with one-paragraph charters
- [ ] Rank by leverage and prerequisite order (what depends on what)
- [ ] Each entry names: trigger surface, primary action, DHF-evidence contract, integration points with existing skills

### Phase 4 — Control + compliance harness (G4)
- [ ] Map every agent-produced artifact to its DHF home (which manifest slot, which trace layer, which Jira mirror)
- [ ] Define the audit trail: how does a regulator see "this design input came from agent A, was reviewed by human H on date D, traces to test T"?
- [ ] Identify gaps where current skills (`trace-matrix`, `dhf-manifest`, `tracker`, `jira-pull`, `change-control`) need extension to support agent provenance metadata

### Phase 5 — Pilot scope (G5)
- [ ] Pick a feature slice on PP3500 (candidate: a small new SaMD requirement or a firmware safety control)
- [ ] Walk the slice through the blueprint on paper — call out every artifact produced, every hand-off, every checkpoint
- [ ] Identify the minimum set of new skills/agents the pilot would actually need (vs. nice-to-have)

### Phase 6 — Wrap
- [ ] Strategy + blueprint consolidated in this task doc, ready to harvest via `/strategy`
- [ ] Child task IDs created (or proposed) for each new skill/agent in the prioritized build list
- [ ] Lessons learned captured inline with `<!-- LESSONS LEARNED -->` blocks
- [ ] Resume-ready summary at top of doc

## Phase 0 — Inventory of Existing Agents & Skills (completed 2026-05-13)

### Agents (15 installed under `.claude/agents/`)

| Agent | Role | PDLC Phase | Type |
|-------|------|-----------|------|
| advisor-researcher | Lightweight file-finder helper for advisor agents (Read/Glob/Grep) | Cross-cutting | Helper |
| clinical-affairs | Clinical evidence strategy, KOL engagement, user-needs validation | Inputs / Design / V&V | Single |
| core-team-panel | Cross-functional advisory panel (PM, Reg, Clinical, QE, R&D) | Program | Panel |
| cybersecurity | Threat modeling, SBOM, IEC 81001-5-1, pre/post-market cyber controls | Design / V&V | Single |
| design-review-panel | Technical design review (Systems, R&D, V&V, HF, Risk, QE) | Design / V&V | Panel |
| human-factors | IEC 62366 usability, use-related risk, formative/summative evaluation | Design / V&V | Single |
| post-market | Surveillance, complaint handling, trend analysis, PSUR/PMSR | Post-market | Single |
| program-manager | Schedule, scope, stakeholder alignment, cross-functional coordination | Program | Single |
| project-secops | Security operations, remediation guidance, attestation | Cross-cutting | Single |
| quality-engineering | ISO 13485 compliance, design-controls adherence, traceability, CAPA, audits | Program / V&V | Single |
| rd-lead | R&D engineering execution, design output quality, architecture↔code alignment | Dev / V&V | Single |
| regulatory-affairs | 510k/De Novo/PMA/PCCP, substantial equivalence, standards mapping | Inputs / Design / Program | Single |
| risk-management | ISO 14971 hazards, risk controls, residual risk, benefit-risk | Design / V&V / Post-market | Single |
| systems-engineering | System architecture, requirements decomposition, interfaces, traceability | Inputs / Design | Single |
| vnv-lead | V&V strategy, test protocols, evidence sufficiency, design-transfer gates | V&V | Single |

### Skills (24 + 2 internals under `.claude/skills/`)

| Skill | Purpose | PDLC Function | DHF Artifact |
|-------|---------|--------------|--------------|
| advisors | Persona subagent infrastructure (canonical roles, 3-tier grounding) for the advisor agents above | Cross-cutting | No |
| best-practices | Audit project setup vs. shared registry + local skills | Cross-cutting | No |
| change-control | Bridge to Confluence / Comala / Windchill / Jira (inbound + outbound + freeze + release) | Program | Sometimes |
| dhf-manifest | 4-tier obligation catalog (FDA + standards + QMS + per-DHF) with gap reports | Program | Yes |
| digest | Project activity summarization + CHANGELOG.md append | Cross-cutting | No |
| docflow | DOCX/PDF/XLSX ↔ markdown round-trip with image, cross-ref, quality gates | Dev | Sometimes |
| docx · pdf · pptx · xlsx | Format-specific document operations | Dev | Sometimes |
| frontend-slides · md-deck | HTML slide-deck builders (stylist + pipeline) | Cross-cutting | No |
| jira-pull | Jira mirroring + drift detection vs. design-controls trace | Program | No |
| lessons | Capture, stage, promote lessons learned from tasks | Cross-cutting | Sometimes |
| medtech-docs | Scaffold regulated-project documentation, manage DHFs/standards, compliance dashboard | Program | Yes |
| project-console | FastAPI local console — agents chat, documents explorer, dashboards | Program | No |
| secops | Security posture (hooks, secops agent, permissions allow list) | Cross-cutting | No |
| skill-creator | Create / modify / audit / measure skills (trigger surface, actions, evals) | Cross-cutting | No |
| strategy | Scan tasks for strategy by domain (regulatory, commercial, arch, dev, test, risk, post-market, ops) | Program | Yes |
| sync-skills | Bidirectional sync with hitachi registry | Cross-cutting | No |
| task | Task management with active-task gating | Program | No |
| trace-matrix | Bidirectional design-controls trace builder (UN ↔ DI ↔ SW ↔ Arch ↔ V&V ↔ Risk) | Program | Yes |
| tracker | Submission-package readiness dashboard | Program | Yes |
| web-control | Browser automation shared infrastructure (Chrome + DevTools) | Cross-cutting | No |

### Gap analysis — what's missing for "agentic-first"

<!-- STRATEGY CONTENT: development, architecture
Topic: Existing agent fleet is review-shaped, not execution-shaped — the structural gap that motivates this task

The 15 installed agents are uniformly **advisor / reviewer / grounder** agents (Tier-3 in `advisors` parlance): they read source documents, ground answers in tiered context, and emit guidance. Their tool surface confirms this — Read / Glob / Grep / WebFetch / Agent for the discipline agents, no Edit / Write / Bash.

For an agentic-first PDLC, the missing layer is **execution agents** — agents that actually produce design outputs, write code, author test protocols, run verification, update the risk file. The reviewer agents become the human-proxy review/gate around them, not the workforce.

Working hypothesis (to be validated in Phase 1):

- **Tier-1 — Execution agents** (NEW). Feature-owner, software-developer, firmware-developer, test-author, verification-runner, requirement-author, risk-author, traceability-keeper. Tools include Edit / Write / Bash. Each owns a class of artifact and is accountable for its DHF home.
- **Tier-2 — Orchestrator** (NEW). Owns a feature ticket end-to-end; sequences Tier-1 agents; invokes Tier-3 reviewers at design-control checkpoints; escalates to human at non-negotiable gates.
- **Tier-3 — Reviewer / advisor agents** (EXISTING, mostly reusable). The current 15 agents map cleanly to design-review-panel + core-team-panel roles; they become the agentic stand-in for cross-functional review meetings, surfacing concerns that route back to the orchestrator or escalate to a human.

The existing skills already cover most of the **regulated-artifact infrastructure** (trace-matrix, dhf-manifest, tracker, jira-pull, change-control, medtech-docs, strategy, lessons, task, secops). The agentic-first design likely doesn't need many new skills — it needs new **agents that drive those existing skills** under orchestration.

Non-obvious implication: the agentic-first investment is mostly **agents + orchestration**, not **skills**. That changes the build order in Phase 3.
-->

_(Strategy block above captures the Phase-0 insight. Phase 1 will turn this into the led/assisted/human-only mapping per PDLC phase.)_

## Strategy

### Phase 1 Discussion Frame — Two Groups + the Bridge

<!-- STRATEGY CONTENT: architecture, development
Topic: Reframing the agentic-first PDLC as two groups with a contract between them

User's framing (2026-05-13, chat): rather than slicing by PDLC phase, slice by **role-group**.

- **Group A — Specification group.** Owns *what* is being built and *why*. Authors: user needs, design inputs, software requirements, risk file, regulatory strategy, clinical evidence, usability use-scenarios. Produces the regulated input artifacts that bind the dev team.
- **Group B — Development group.** Owns *how* it is built. Authors: architecture decisions, code, firmware, hardware specs, build/CI toolchain, technology selections, design outputs.
- **The Bridge.** The contract between A and B: how a design input becomes a buildable, testable, traceable design output. Historically informal (a person reads the SRS and writes code); the agentic-first opportunity is to make this contract **machine-enforceable** so test-driven, trace-driven, constraint-driven development falls out naturally.

Open question the user raised: are we missing **constraint corpora** that the development group needs as upstream truth before agents can build under control? Candidates:
- **Architecture Strategy** — system topology, module boundaries, interface contracts (we have arch SADs per DHF but no top-level system arch doc — surfaced in task 046 already).
- **Tooling Strategy** — what toolchain, what CI/CD, what static analysis, what coverage targets, what release pipeline. Today: not authored anywhere in `docs/project/strategies/`.
- **Technology Strategy** — language/platform/framework selections, dependency policy, OSS posture, supply-chain controls. Today: not authored.

These three strategy docs would be the **constraint surface** that development agents read before generating any design output — analogous to how the strategy skill currently slots regulatory / commercial / development / testing / risk / post-market / operations.

TDD linkage hypothesis: the bridge enforces "no SW requirement without a test, no test without a verifying SW requirement" — and an agent at the bridge auto-drafts test cases from requirements + risk controls. The `trace-matrix` skill already models this trace (DI → SW → V&V), but today the V&V layer is hand-authored, not generated. Agentic-first turns that into a generation step gated by human review.

Live discussion — to be chunked across multiple turns.
-->

**Where the discussion is heading (chunked — won't tackle all at once):**

1. **The model** — is "Group A = spec, Group B = dev, with a contract between them" the right cut? Or is V&V/quality a third group?
2. **The bridge contract** — what flows across (artifacts) and what enforces it (agents + skills)?
3. **Constraint corpora** — do we need Architecture / Tooling / Technology strategy docs as upstream constraints for dev agents? What's missing today?
4. **TDD linkage** — how does a requirement deterministically produce test cases? Agent? Skill? Where does it sit?
5. **Current-structure fit** — walk through existing skills/agents and mark Reuse / Extend / Create-new.

_(Each chunk gets its own discussion section below as we work through it.)_

#### Chunk 1 — Group model: THREE groups (decided 2026-05-13)

<!-- STRATEGY CONTENT: architecture, testing
Topic: Three-group agentic PDLC model (Spec / Dev / V&V) with V&V as a peer, not a method

Decision: V&V is a **third peer group**, not a method folded into the Spec↔Dev bridge.

User's reason: V&V owns its **own tooling strategy and architecture** — test frameworks, simulation rigs, HW-in-the-loop fixtures, coverage tooling, test-data management, release-qualification pipelines. Treating V&V as a method inside a bridge implicitly subordinates it to Dev's toolchain, which collapses an axis of independent design choice. As a peer group, V&V can author its own Architecture/Tooling/Technology strategy that constrains its agents the same way Dev's does.

Implications:

- Three peer groups: **Spec / Dev / V&V**. Each gets its own constraint-corpus surface (Architecture + Tooling + Technology strategies — see Chunk 3).
- Bridges become a *graph*, not a single hand-off line. At least three directed edges to design: Spec→Dev (build to spec), Spec→V&V (test to spec), Dev→V&V (verify built thing). Possibly back-edges from V&V (findings route to Spec or Dev). To be detailed in Chunk 2.
- Independence claims (ISO 13485 §7.3 verification independence, IEC 62304 §5.7 test independence) align cleanly: V&V agents do not share a toolchain or codebase with Dev agents, by design.
- The trace-matrix layer model already supports this: UN/DI ↔ SW (Dev artifact) ↔ V&V (V&V artifact) are distinct layers. Three groups maps 1:1.
-->

**Decided**: three peer groups — **Spec** (what+why), **Dev** (how — implementation), **V&V** (how — verification). Each owns its own Architecture / Tooling / Technology strategy.

#### Chunk 2 — Edge topology: V-shape with parallel test design + two test universes (decided 2026-05-13)

<!-- STRATEGY CONTENT: architecture, testing, development
Topic: Three-group V-shape topology and the Dev-Tests / V&V-Tests split

Decision: topology **(ii) Triangle / V-shape**.

Edges (5 total):
- **Spec → Dev** (forward). Requirements + risk controls flow into implementation.
- **Spec → V&V** (forward, in parallel with Spec→Dev). Requirements + risk controls flow into test design. V&V does NOT wait for Dev outputs to begin test design — this is the parallelism win.
- **Dev → V&V** (forward). Design outputs (built code, FW, HW) flow to V&V for test *execution*. V&V cannot execute black-box functional tests until this edge fires.
- **V&V → Spec** (back). Findings that indicate a requirement gap, ambiguity, or unverifiable claim route back to Spec.
- **V&V → Dev** (back). Findings that indicate an implementation defect (built thing doesn't satisfy a verified-as-good spec) route back to Dev.

Critical nuance from user (2026-05-13 chat): there are **two distinct test universes**, both contributing to the overall V&V effort:

| Test universe | Owner group | Style | Standards anchor | Trace-matrix layer |
|---------------|-------------|-------|------------------|--------------------|
| **Dev Tests** | Dev | White-box; unit + integration tests; TDD-style; built alongside implementation | IEC 62304 §5.5.5 (unit), §5.6 (integration) | New layer (DT) sitting alongside SW |
| **V&V Tests** | V&V | Black-box; functional + system tests; built independently from implementation against Spec | IEC 62304 §5.7 (system/system-of-systems); ISO 13485 §7.3.6 (design verification) | Existing VER layer in trace-matrix |

Both contribute to the overall design-verification evidence package — they cover different abstraction levels and are not substitutes.

**Independence preservation.** V&V agents are constrained by their charter to NEVER read Dev implementation source. They read Spec artifacts (UN, DI, SRS, risk controls) and design outputs at black-box interfaces only (APIs, UI, HW signals). Dev agents own Dev Tests and may read implementation freely. This honors IEC 62304 §5.7 independence by *agent-charter construction*, not by org-chart separation — an interesting agentic-first move worth highlighting in the strategy.

**Parallelism win.** Spec→Dev and Spec→V&V agents can run truly in parallel because the V&V agent's input is Spec, not Dev. The Dev→V&V edge only blocks on *test execution*, not test design or test coding. This is one of the strongest agentic-first dividends — V&V is no longer a serial tail of the schedule.

**Trace-matrix implication (concrete).** The existing trace-matrix layer model needs a new **DT (Dev Tests)** layer between SW and VER:

```
UN ↔ DI ↔ SW ↔ DT (white-box, Dev-owned)
              ↘ ↓
                VER (black-box, V&V-owned) ↔ Risk
```

Both DT and VER rows trace back to SW (and through to DI/UN). Both must be present for the overall verification evidence to be sufficient. Today the trace-matrix skill has only VER — adding DT is a discrete extension worth tracking as a child task.
-->

**Decided**:
- Topology **V-shape** — Spec governs both Dev and V&V; V&V test design parallel with Dev implementation; V&V test execution blocks on Dev outputs; V&V back-edges to Spec (req issues) and Dev (impl issues).
- **Two test universes** — Dev Tests (white-box, unit + integration, IEC 62304 §5.5–§5.6) and V&V Tests (black-box, functional + system, IEC 62304 §5.7). Both contribute to design-verification evidence.
- **Independence by agent charter** — V&V agents are charter-bound not to read Dev implementation source. Charter enforcement replaces org-chart separation.
- **Trace-matrix needs a new DT layer** alongside the existing VER layer — child task candidate.

#### Chunk 3 — Constraint corpora: per-axis cross-group strategies (decided 2026-05-13)

<!-- STRATEGY CONTENT: architecture, development, operations
Topic: Three per-axis cross-group strategy docs as the constraint surface for agents

Decision: shape **(β) per-axis cross-group strategies**. Three docs, each with internal Spec / Dev / V&V sections:

| Axis | Doc | Today | Action |
|------|-----|-------|--------|
| Architecture | `docs/project/strategies/architecture-strategy.md` | EXISTS — but no explicit Spec/Dev/V&V sectioning | Refactor to add per-group sections (or first-class subsections) |
| Tooling | `docs/project/strategies/tooling-strategy.md` | **MISSING** | Author new; covers CI/CD, build pipelines, static analysis, coverage tooling, test harnesses, simulation rigs, HIL fixtures, release pipeline — with Spec/Dev/V&V sections |
| Technology | `docs/project/strategies/technology-strategy.md` | **MISSING** | Author new; covers language/platform/framework selections, dependency policy, OSS posture, supply-chain controls — with Spec/Dev/V&V sections |

**What about existing `development-strategy.md` and `testing-strategy.md`?** These are group-narrative docs (how the Dev group operates; how the V&V group operates), not per-axis constraints. They stay as-is for now — they answer "how does this group work" rather than "what are the architecture/tooling/technology constraints." When the three axis docs land, `development-strategy.md` should be edited to *reference* the axis docs for technology/tooling rather than duplicate.

**Existing Spec-side strategies** (regulatory, commercial, risk, postmarket, operations) are orthogonal — they constrain *what* gets built (Spec group's domain), not *how* it's built. They remain Spec-group inputs and don't fit the 3-axis model. Operations-strategy may have overlap with Tooling-strategy (release pipeline) — handle that overlap with a cross-reference, not a merger.

**`/strategy` skill implication**: today the skill harvests 8 domains (regulatory, commercial, architecture, development, testing, risk, post-market, operations). Adding `tooling` and `technology` is a discrete two-domain extension — child task candidate against the `/strategy` skill.

**Agent-constraint-reading contract**: each group's execution agents read a fixed set of constraint docs before generating any artifact, called out in the agent charter:
- **Spec agents** read: regulatory, commercial, risk, postmarket, operations, clinical inputs.
- **Dev agents** read: architecture (Dev section), tooling (Dev section), technology (Dev section), development-strategy.
- **V&V agents** read: architecture (V&V section), tooling (V&V section), technology (V&V section), testing-strategy.

This is the *constraint contract* — the agent's deterministic read list. Output is non-deterministic; inputs are not.
-->

**Decided**:
- 3 per-axis cross-group docs: **architecture** (exists, refactor needed), **tooling** (new), **technology** (new). Each has internal Spec / Dev / V&V sections.
- Existing `development-strategy.md` + `testing-strategy.md` stay as group-narrative docs alongside the axis docs.
- Existing Spec-side strategies (regulatory / commercial / risk / postmarket / operations) remain Spec-group inputs — orthogonal to the 3 axes.
- `/strategy` skill needs `tooling` and `technology` added as harvest domains — child task candidate.
- **Agent-constraint-reading contract**: each agent charter names a fixed list of constraint docs the agent must read before producing artifacts. Spec agents read Spec-side strategies; Dev agents read all 3 axis docs (Dev sections) + development-strategy; V&V agents read all 3 axis docs (V&V sections) + testing-strategy.

#### Chunk 4 — TDD linkage: form-neutral Testable-Claim atom (decided 2026-05-13)

<!-- STRATEGY CONTENT: architecture, testing, development
Topic: Form-neutral Testable-Claim atom + project-pluggable adapter (meta-pattern, not Gherkin-locked)

Decision: (Q-generalized) — introduce **Testable Claim (TC)** as a form-neutral atomic unit between requirements and tests. The atom is conceptual; the **form** is project-pluggable.

User's framing (2026-05-13 chat): companies use different requirement-management strategies — behavioral languages (Gherkin/BDD), UML use-case diagrams, discrete shall-statements, user stories, decision tables, state-machine transitions. The agentic infrastructure must be a **meta-pattern** that fits all of these, mirroring how `trace-matrix` uses project-adaptive parsers rather than locking a layout.

**Meta-pattern shape:**

```
[requirement form]              [adapter]                 [canonical layer]
─────────────────              ─────────                ─────────────────
Gherkin scenarios       ─┐
UML use-case steps      ─┤
Discrete shall stmts    ─┼──▶  project TC adapter  ──▶  Testable Claims (TC layer)
User stories + AC       ─┤                              one row per TC,
Decision-table rows     ─┤                              1:N to tests
State transitions       ─┘                              provenance → source form
```

**Canonical TC row** (project-form-neutral):

| Field | Meaning |
|-------|---------|
| `tc_id` | Stable identifier (e.g., TC-0042) |
| `claim` | Single testable claim in natural-language canonical form |
| `source_ref` | Pointer back to its origin in the requirement-management form (Gherkin scenario id, use-case step number, SRS-N.N, story id + AC index, decision-table cell, state-machine edge label, …) |
| `requirement_trace` | Up-trace to the parent SW/DI/UN row(s) |
| `risk_trace` | Up-trace to the risk control(s) it satisfies, if any |
| `criticality` | Inherited or overridden (CtS/CtF/CtC/CtP — task 011 vocabulary) |
| `test_ids` | Down-trace to V&V tests + Dev tests covering it; **floor = 1 V&V test; ceiling = unbounded** |

**Test cardinality policy (1:N with 1:1 floor):**

- **Minimum**: every TC has at least one V&V test (the floor). The system blocks design-transfer if any TC has zero V&V tests — same gate as today's "DI without verification" orphan check.
- **Maximum**: unbounded. Agents (V&V test-author, Dev test-author) may author multiple tests per TC at their discretion — e.g., boundary cases for a numeric range, parametric variants, negative tests, hazard-specific tests against the same TC.
- **Authoring discretion drivers** (agent decides 1 vs N): TC complexity, risk classification of the parent requirement (high-risk → more coverage), boundary/edge-case density, hazard-trace presence, regulatory-criticality tags (CtS items typically warrant more tests).
- **Dev Tests** are independent of the floor — Dev agents author Dev Tests against the TC freely; their count doesn't satisfy the floor, but they contribute to overall coverage evidence.

**Project-adapter contract (the meta-pattern's plug surface):**

Each project supplies (in `project.yml` or a sibling config) a **TC adapter declaration**:
- `tc_form: gherkin | usecase | shall | story | decision-table | state-machine | custom`
- `tc_source_paths:` — globs where the requirement-management form lives
- `tc_extractor:` — script/module path that takes a source file and emits a list of canonical TC rows (analogous to `trace-matrix` layer parsers)
- `tc_provenance_format:` — string template for the `source_ref` back-pointer

This makes the agentic-first skill portable: a Gherkin shop, a UML shop, and a shall-statement shop all use the same TC layer, same agent contracts, same test cardinality policy — only the extractor changes.

**Trace-matrix layer impact (concrete):**

```
UN ↔ DI ↔ SW ↔ TC ↔ DT (Dev Tests, white-box)
                 ↘
                  VER (V&V Tests, black-box) ↔ Risk
```

Two new layers since this task started: TC (Chunk 4) and DT (Chunk 2). Both candidate child tasks against `/trace-matrix` skill.

**Why not (R) — test-as-spec.** User confirmed (Q-generalized) over (P) and (R). (R) collapses the Spec/V&V boundary and contradicts the V-shape governance principle. The TC atom keeps the boundary clean: Spec authors the claim, V&V verifies it; the adapter is just the syntactic bridge between the project's requirement form and the canonical claim.
-->

**Decided**:
- **Testable Claim (TC)** as form-neutral atomic unit between requirements and tests.
- **Project-pluggable adapter** maps the project's requirement-management form (Gherkin / UML use-case / discrete shall / user-story+AC / decision-table / state-machine / custom) → canonical TC rows.
- **Test cardinality 1:N with 1:1 floor** — every TC must have ≥1 V&V test; agents have authoring discretion to add more based on risk, complexity, hazard trace, regulatory criticality.
- **Dev Tests** are independent of the floor — they're additive coverage, not floor-satisfying.
- **Trace-matrix gains two new layers**: TC (between SW and tests) and DT (Dev Tests, parallel to VER). Both candidate child tasks.
- **Adapter contract** lives in `project.yml`: `tc_form`, `tc_source_paths`, `tc_extractor`, `tc_provenance_format` — same project-adapter pattern as `trace-matrix`.

##### Chunk 4 addendum — Content-hash audit + test linkage convention (decided 2026-05-13)

<!-- STRATEGY CONTENT: testing, architecture
Topic: Content-hash of the Testable Claim drives change-audit; version fields are insufficient

User's framing (2026-05-13 chat): "Hash against requirement statement or acceptance criteria, ignoring title/version/metadata. Version fields can bump without content change, so we can't rely on version as a change signal."

Decision: every test artifact stores the **content hash of the TC it traces to, at the moment the test was authored**. Drift audit compares stored hash vs. current TC hash. Hash mismatch ⇒ test flagged for re-review.

**Hash domain — what's in vs. out:**

| In (semantic content — affects pass/fail) | Out (informational metadata) |
|-------------------------------------------|------------------------------|
| TC `claim` text (the canonical claim) | Title, heading |
| Acceptance criteria text (Given/When/Then, decision-table conditions, table cells) | Version number, status, author, dates |
| Load-bearing constants (numeric thresholds, units, enum values, error codes) | Rationale / commentary / notes |
| Structured-form fields that change behavior (e.g., Gherkin step parameters) | Trace links / IDs / cross-refs (relational, not semantic) |

**Normalization (light-touch):** strip leading/trailing whitespace; collapse internal whitespace runs to single spaces. **Do NOT** lowercase, stem, or strip punctuation — in regulated language "shall" vs "should", "≤" vs "<", "and" vs "or", "must" vs "may" carry semantic weight and must affect the hash. Preserve Unicode (don't ASCII-fold).

**Hash storage: inside the test artifact** (user decision 2026-05-13).

Test case frontmatter convention:
```yaml
---
test_id: TC-VV-1042
traces:
  - tc_id: TC-0042
    tc_hash: sha256:abc123…
    authored: 2026-05-13
---
```

The stored hash is the **authoring-time hash** — frozen evidence. The drift audit:
1. Re-extract TCs via the project adapter.
2. For each test, compute current `tc_hash` from the live TC text.
3. If `stored_tc_hash != current_tc_hash`, surface the test in a drift report; flag for re-review.
4. After re-review (test still adequate, or test updated), the stored hash is bumped to the new value with an audit-trail line.

Why this matters: rationale-only edits don't trigger spurious re-review; substantive content edits (changed threshold, flipped condition) always do — regardless of whether the requirement's `version:` field was incremented.

**Rationale-drift audit (separate, softer):** rationale changes don't invalidate test hashes but may indicate a stale requirement. Run as a separate, advisory check — output a "rationale changed but claim didn't" list for Spec-side review.

**Implementation surface:** new action `/trace-matrix audit-drift` (or new sibling skill) walks all test artifacts, recomputes TC hashes, emits a drift report. The hash function itself is a 5-line utility — the work is the audit policy + reporting UI.
-->

**Decided**:
- **Hash domain**: TC `claim` + structured AC fields + load-bearing constants. Exclude title, version, status, author, dates, rationale, trace links.
- **Normalization**: trim + collapse whitespace; preserve case, punctuation, Unicode.
- **Storage**: inside the test artifact frontmatter (`traces[].tc_id` + `traces[].tc_hash` + `traces[].authored`). Single source of truth, audit-friendly, survives sidecar rebuilds.
- **Drift audit**: re-extract TC → recompute hash → diff vs. stored. Mismatch flags test for re-review. Separate **rationale-drift advisory** runs alongside but doesn't invalidate hashes.
- **Implementation lands as**: new audit action on `/trace-matrix` (or sibling skill) — child task candidate.

##### Chunk 4 addendum 2 — Test-side structure: case + procedures, aggregate by AND (decided 2026-05-13)

<!-- STRATEGY CONTENT: testing, architecture
Topic: Test-side two-level structure — test case is the trace atom, procedures aggregate

User simplified an over-layered first draft (had proposed case/file/suite as three concerns). Final model — TWO levels:

- **Test case** — the trace atom on the test side. Often a physical file, but project-defined. Carries:
  - a stable declared `test_id` (one per case, in the file header / frontmatter — NOT per-procedure decorators; this resolves the earlier ID-ceremony concern)
  - the trace link(s): `traces: [{node_id, node_hash, authored}]`
  - a roll-up result
- **Test procedure** — a sub-unit inside a test case (a test function, a numbered protocol step). Procedures do NOT individually trace. **Aggregate rule: all procedures pass ⇒ case passes; any fail ⇒ case fails** (logical AND).

**Why this shape:** high-level requirements (broad design inputs) naturally need many procedures to cover their breadth. The procedure count absorbs requirement breadth — no new trace layer needed. A single test case can therefore legitimately verify a high-level node with 20 procedures, or a fine-grained TC with 2.

**Trace-target granularity is project-author's choice.** The test case's `traces[].node_id` points to a requirement-side node *at whatever granularity the project's adapter exposes*:
- Atomic-shop: test case → TC (the form-neutral testable claim).
- High-level-tracing shop: test case → DI or SW requirement directly.
- The content hash is computed over **whatever node is linked** — hash the TC claim if linked to a TC, hash the DI statement if linked to a DI. The hashing rules (Chunk 4 addendum 1) are node-type-agnostic: they always hash semantic claim text, exclude metadata.

This keeps the meta-pattern maximally general — it does not force every project into the TC layer; the TC layer is *available* for shops that want atomic determinism, but a shop that traces test files straight to design inputs is equally supported.

**"Suite" demoted.** Suite/tags are optional organizational metadata on the test case (`tags: [smoke, release-qual]`) for CI/execution selection — not a trace node, not a layer. No further design needed.

**Open implication for the trace-matrix DT/VER layers:** the layer rows represent **test cases** (with roll-up results), not procedures. Procedure-level detail is internal to the case artifact. The skill's parser reads the case's declared `test_id` + `traces[]` + result; it does not descend into procedures.
-->

**Decided** (superseded by addendum 3 below — kept for history):
- ~~Test side has two levels: test case (trace atom) and test procedure (no individual trace)~~ — corrected: procedures CAN trace.

##### Chunk 4 addendum 3 — Trace anchor is a *test node* at author-chosen depth (decided 2026-05-13)

<!-- STRATEGY CONTENT: testing, architecture
Topic: Test-side trace anchoring is depth-flexible — symmetric with the requirement side

User correction (2026-05-13): addendum 2's "procedures do not individually trace" was too rigid. Some requirements are specific enough that individual test procedures within a file trace directly. Both modes must be supported — "you can do both."

Final model — the **trace anchor is a *test node***, and a test node may be a **test case** OR a **test procedure**. The author picks the depth, exactly as the requirement-side trace target may be a TC or a DI/SW.

| Requirement side | Test side |
|------------------|-----------|
| Trace target = TC **or** DI/SW (project choice) | Trace anchor = test case **or** test procedure (author choice) |

**The principle that falls out:** `test_id` + `traces[]` + content-hash + result live **wherever the author draws the trace, and nowhere else.**

- **Case-level trace** — broad file → one (often high-level) requirement node. The *case* carries `test_id` + `traces[]` + hash. Procedures are sub-units with no IDs; aggregate by logical AND → case result.
- **Procedure-level trace** — specific procedures → specific requirement nodes. Each tracing *procedure* carries its own `test_id` + `traces[]` + hash + result. The enclosing file is a pure organizational container (same demotion "suite" received).

**ID ceremony is now proportional** — a stable `test_id` is declared only at a node that anchors a trace. No trace → no ID. This is strictly better than "every procedure needs a decorator": ceremony scales with traceability need, not with code structure.

**Aggregate-by-AND scoping** — the AND roll-up rule applies *only when the case is the trace anchor*. When procedures are the anchors, each has its own result and the file-level roll-up is informational only (useful for CI dashboards, not for trace).

**Trace-matrix DT/VER layer rows** therefore represent **test nodes** (case or procedure, whichever is the anchor) — not "always cases." The skill's test extractor must emit a node regardless of depth; the `location` field disambiguates (`file.py` vs `file.py::procedure_7`).

**Open sub-question for next turn:** can the two modes be *mixed within a single file* — e.g., the file as a whole traces to a high-level DI AND procedure 3 inside it independently traces to a specific TC? Or is it one-mode-per-file? Affects the test-extractor adapter design.
-->

**Decided**:
- **Trace anchor is a *test node*** — may be a **test case** or a **test procedure**, at the author's chosen depth. Symmetric with the requirement-side TC-or-DI/SW choice.
- `test_id` + `traces[]` + content-hash + result live **only where a trace is anchored** — ID ceremony is proportional to traceability need.
- **Aggregate-by-AND** applies only when the *case* is the anchor; when procedures are anchors, each carries its own result.
- Trace-matrix DT/VER rows represent **test nodes** (case or procedure); `location` field disambiguates depth.

##### Chunk 4 addendum 4 — Mixed anchoring within a file IS allowed (decided 2026-05-13)

<!-- STRATEGY CONTENT: testing, architecture
Topic: Mixed-depth trace anchoring within a single test file + the carve-out and dedup rules it forces

Decision: a single test file MAY mix anchoring depths — the file as a whole traces to a (typically high-level) requirement node AND individual procedures inside it independently trace to specific nodes. User chose maximum flexibility "matches how real test files evolve."

Two design rules this forces (both belong in the trace-matrix test-extractor + coverage-rollup logic):

1. **Carve-out rule.** An independently-anchored procedure is *removed from the enclosing case's AND aggregate*. The file-level case trace covers "everything in the file EXCEPT the independently-anchored procedures." Test-node scopes are therefore disjoint by construction — a procedure is governed by exactly one trace anchor (its own, or its enclosing case's, never both). This is what prevents the file-level result and the procedure-level result from contradicting or double-asserting.

2. **Coverage dedup rule.** Trace EDGES are never deduped — every authored edge is retained for audit (file→DI-005 and procedure3→TC-0042→…→DI-005 are both real, both kept). But COVERAGE METRICS dedup by *target node*: when answering "is DI-005 verified?", multiple trace paths to DI-005 count once. Dedup lives in the metrics/rollup layer, not the edge layer. Redundant coverage is legitimate and visible; it just isn't double-counted.

Extractor implication: the test extractor must walk BOTH file-level markers AND procedure-level markers in the same file, emit a test node per anchor found, and tag each emitted node with its `location` depth so the carve-out rule can be applied. This is a moderate increase in extractor complexity over one-mode-per-file — accepted as the cost of matching real-world test-file evolution.
-->

**Decided**:
- **Mixed anchoring within one file is allowed** — file-level trace + independently-anchored procedures can coexist in the same file.
- **Carve-out rule**: an independently-anchored procedure is removed from its enclosing case's AND aggregate — test-node scopes are disjoint by construction.
- **Coverage dedup rule**: trace edges are never deduped (all retained for audit); coverage metrics dedup by target node so redundant coverage isn't double-counted.
- Extractor must walk both file-level and procedure-level markers — accepted complexity cost.

**Chunk 4 is now fully closed.** TC meta-pattern, 1:N cardinality, content-hash audit (domain + normalization + storage), test-node anchoring (case/procedure, mixed allowed), carve-out + dedup rules — all decided.

_(Strategy content gets filled in-flight as Phase 1 / Phase 2 produce decisions. Tag each decision with the appropriate `<!-- STRATEGY CONTENT: domain, topic -->` block so `/strategy` can harvest it.)_

## Open Questions

- Does "agent-led" require a named human signer per artifact, or can a class-of-reviewer suffice for low-risk artifacts?
- How do we represent agent provenance in the trace matrix and DHF manifest without polluting the regulated deliverable view?
- For Class II (PP3500), what's the smallest auditable unit of agent work — a tool call, a task, an artifact?
- Where does the existing `core-team-panel` / `design-review-panel` round-robin model fit vs. a single feature-owning agent?

## Resume-ready Summary

_(Updated at every checkpoint. On a fresh session, read this section first.)_

- **Status**: In Progress — Phase 0 done, Phase 1 chunks 1–4 decided. 2026-05-13.
- **What's decided** (see Strategy section for full detail):
  - Three peer groups: Spec / Dev / V&V (V&V is a peer because it owns independent tooling + architecture).
  - V-shape topology; two test universes (Dev Tests white-box / V&V Tests black-box); independence enforced by agent charter.
  - Constraint corpora = 3 per-axis cross-group strategy docs (Architecture exists; Tooling + Technology are new).
  - TC = form-neutral testable-claim atom with project-pluggable adapter; 1:N test cardinality, 1:1 floor.
  - Content-hash audit on the linked requirement node (semantic text only, light normalization); hash stored in the test artifact.
  - Trace anchor = a test node at author-chosen depth (case or procedure); mixed anchoring within a file allowed; carve-out + coverage-dedup rules defined.
- **Next step**: Chunk 5 — current-structure fit (mark each skill/agent Reuse / Extend / Create-new), OR walk one end-to-end agent flow for a sample PP3500 requirement. User to choose.
- **Child-task candidates surfaced so far**: (a) trace-matrix new TC layer; (b) trace-matrix new DT layer; (c) trace-matrix content-hash drift-audit action; (d) `/strategy` skill — add `tooling` + `technology` harvest domains; (e) author `tooling-strategy.md` + `technology-strategy.md`; (f) refactor `architecture-strategy.md` into per-group sections.
- **Activation command**:
  ```bash
  bash .claude/hooks/task-activate.sh add 8ea04f14-b3fc-4049-9dac-8da0c59bbac7 054
  ```

## Lessons Learned

_(Tag with `<!-- LESSONS LEARNED: category -->` blocks in-flight.)_

## Changelog

- **2026-05-13** — Task created. Scope: agentic-first PDLC strategy + agent team blueprint + new skills/agents catalog, anchored on PP3500. Six phases: frame → strategy → blueprint → catalog → control harness → pilot.
- **2026-05-13** — Phase 0 inventory completed. 15 agents + 24 skills tabled in task doc. Key finding: existing agents are uniformly Tier-3 reviewer-shape (Read/Glob/Grep, no Edit/Write/Bash); the agentic-first gap is Tier-1 execution agents + Tier-2 orchestrator, not new skills. Most regulated-artifact skills (trace-matrix, dhf-manifest, tracker, jira-pull, change-control, medtech-docs) already exist — agentic-first investment is agents + orchestration on top.
- **2026-05-13** — Phase 1 chunks 1–3 decided in discussion: (1) THREE peer groups Spec/Dev/V&V (V&V is peer, not method, because it has independent tooling+architecture); (2) V-shape edge topology, two test universes (Dev Tests white-box IEC 62304 §5.5–§5.6 + V&V Tests black-box §5.7, both contribute to verification evidence), independence by agent charter; (3) per-axis cross-group constraint docs — Architecture / Tooling / Technology, each with Spec/Dev/V&V sections. Two new strategy docs needed (tooling, technology); `/strategy` skill needs two new harvest domains. Trace-matrix needs new DT layer. Agent charters carry an explicit constraint-reading contract.
- **2026-05-13** — Phase 1 chunk 4 decided: form-neutral **Testable Claim (TC)** atom with project-pluggable adapter (Gherkin / UML use-case / discrete shall / user-story / decision-table / state-machine / custom). 1:N test cardinality with 1:1 V&V-test floor; agents have authoring discretion above the floor. Dev Tests are additive, not floor-satisfying. Trace-matrix gains a TC layer (in addition to DT from chunk 2) — two child-task candidates against `/trace-matrix`. Adapter contract lives in `project.yml` mirroring trace-matrix's adapter pattern.
- **2026-05-13** — Phase 1 chunk 4 fully closed via 4 addenda: (1) content-hash audit — hash semantic claim text + AC + load-bearing constants, exclude title/version/metadata/rationale, light whitespace normalization, hash stored inside the test artifact; (2) test-side structure — test case + procedures, aggregate by AND; (3) corrected: trace anchor is a *test node* at author-chosen depth (case OR procedure), ID/hash/traces live only where a trace is anchored; (4) mixed anchoring within a file allowed → carve-out rule (independently-anchored procedures leave the enclosing case's aggregate) + coverage-dedup rule (edges never deduped, metrics dedup by target node). Phase 1 todos updated to reflect the chunked-discussion pivot. Six child-task candidates now tracked in Resume-ready Summary.
