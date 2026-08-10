# 115 — Tooling & Testing/Validation Strategy

**ID**: 115
**Created**: 2026-08-06
**Status**: In Progress
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: High

---

## PERMANENT RULES (do not remove)

This task document is the **session-recovery point** for this work. If the current session drops, is compacted, or ends, the next session must be able to load **this file alone** and continue where we left off.

1. **Update at every meaningful checkpoint (HARD RULE).** After each meaningful unit of work — a decision, a completed phase, a discovered blocker, a design pivot — tick the relevant Todo, add a dated Changelog line naming the concrete artifact, update progress counts, and fill the matching `## Economics` entry in the same edit.
2. **Phase-end batching is OK; drift-batching is not.** Write at the phase boundary, before the next phase starts.
3. **A commit is not a substitute.** Git history records code; this doc records the project narrative.
4. **Resume-ready before any session boundary.** The doc must carry: what was completed with concrete artifacts, in-flight state, priority-ordered next steps with paths, open questions, and the exact activation command.
5. **Capture strategy + lessons as they happen** — in-flight, not as a cleanup pass.
6. **Estimation provenance.** `## Economics` follows `.claude/skills/usage-metrics/references/effort-estimation-rubric.md`.

Success test: a fresh Claude session, given only this file, can re-enter the work without asking "what were we doing?"

## Goals

Author two strategy documents so they render in the project console for review:

| Ask | Domain | Output |
|---|---|---|
| **Tooling strategy** | `operations` | `docs/project/strategies/operations-strategy.md` |
| **Testing & validation strategy** | `testing` | `docs/project/strategies/testing-strategy.md` |

Both domains are currently **stubs** (`<!-- Status: awaiting-content -->`). This task takes them to assembled.

**Progress**: 2 / 2 domains assembled, verified and corrected. Console roll-up moved from **3 domains live / 17 decisions** to **5 live / 48 decisions**.

## Decisions

<!-- STRATEGY CONTENT: operations, tooling, strategy-authoring, domain-registry -->

### Tooling strategy lands in the `operations` domain, not a new `tooling` domain

**Decision.** The tooling strategy is authored into the existing **`operations`** strategy domain rather than a new `tooling` domain. `operations` is already registered in `project.yml strategy_domains[]` under the display name **"Operations & Tooling"**, and its `scope_description` already names *"tooling & agentic infrastructure"*, with `what_belongs_here[]` explicitly listing *"Tooling and agentic infrastructure decisions"*, *"Skill and automation roadmap"*, and *"Team workflow, onboarding, and knowledge management"*.

**Why.** Creating a `tooling` domain would fork a domain that already claims the scope. The project's `audit-wiring-before-adding-fields` rule exists for exactly this: the wiring layer already encodes the fact, so the feature routes through a lookup against existing config rather than a new entry. A second domain would also split one story across two documents — the build/release pipeline, the supply-chain posture and the agentic toolchain are the same operational surface, and the decisions in one constrain the others.

**What this commits us to.** The `operations` document carries both the classic operational content (build/release, SBOM/SOUP, cloud posture, QMS operational readiness, PM approach) and the agentic-toolchain content. This task authors the **tooling half**; the remaining operational facets stay open and are called out as such in the document's Open Items so the gap is visible rather than implied-complete.

**Downstream implications.** A future session that wants a standalone tooling domain should use `/strategy domains add`, migrate the tagged blocks, and accept that `operations` loses half its scope — it is a reversible decision, deliberately taken the cheap way first.

**Open questions.** If the agentic-toolchain content grows past roughly half the `operations` document, revisit the split. The strategy skill's own guidance on incubating subtopics (`clinical` inside `regulatory`, `cybersecurity` inside `architecture`) is the precedent: start as a topic within a parent domain, promote when it outgrows it.

## Tooling Strategy — the agentic workbench

<!-- STRATEGY CONTENT: operations, tooling, agentic-infrastructure, tool-validation, governance, knowledge-management -->

### The workbench is software used in the quality system, and that is the question to answer

**Decision.** The project treats its agentic workbench — the skills, agents, rules, hooks and console under `.claude/` and `tools/` — as **software used in the quality system**, and commits to reaching and maintaining a documented *determination* about its qualification rather than leaving the question open. The workbench is not device software and never becomes part of the released product; it is the instrument that authors, checks and assembles the Design History File.

**Why.** Once an AI-assisted toolchain writes into design-control records, an auditor's question is not "is the tool clever" but "what assurance do you have that the records it produced are trustworthy, and where is the evidence." A program that never frames that question ends up answering it improvisationally under audit. The project already carries the scope flag `tool_validation: true` in `project.yml`, so the obligation is declared; what has been missing is the determination that discharges it.

**What this commits us to.** A standing, dated determination covering: what the workbench is, what it is permitted to produce, what assurance activity backs each use, and what triggers re-examination. The determination is a living record — it is invalidated by change, not by time alone.

**Downstream implications.** The determination is the parent of the tool-validation evidence produced by `workbench-validation`, and it is the document a Q-Sub or inspection response would cite. It also bounds the Testing & Validation strategy: test tooling that produces V&V evidence inherits this posture rather than defining its own.

**Open questions.** `[VERIFY]` The governing external references for this determination — FDA's Computer Software Assurance guidance, ISO 13485 §4.1.6, and the QMSR design-controls anchor — are **not yet distilled into `docs/external/`**. FDA CSA exists in this repo only as undistilled raw source under the registry's `references/fda-guidance/source-md/`, with no project applicability file. The determination must not be finalised on paraphrase; import the guidance first.

### Assurance is risk-based and evidence-led, not classical qualification theatre

**Decision.** Workbench assurance is **risk-tiered**: depth of evidence scales with what a given use could damage if it went wrong undetected. The project does not attempt classical installation/operational/performance qualification against the language model itself, and it does not pretend the model is deterministic. It qualifies the **workbench around** the model — the gates, the deterministic checkers, the record structure, and the human review — and treats model behaviour as something to be *bounded and observed*, never as something to be pinned by a passing test.

**Why.** A language model produces different output for identical input. A test suite that asserts specific model prose would either be rewritten until it passed — which is not evidence — or fail continuously and be ignored, which is worse. The honest structure is the one `workbench-validation` already implements: a need is either backed by **deterministic executable evidence**, or it is declared a **process control** backed by human review and an audit trail, and reported as such. What must never happen is a process control being reported as a scripted PASS.

**What this commits us to.** Every workbench user need carries an explicit coverage class, and the report distinguishes them. The scariest failure mode here is not a red verdict; it is a green one that was never earned. The existing register already does this correctly — of 15 needs, 4 are declared `process-control` and 1 `exploratory`, and the report refuses to score them as tests. That property is load-bearing and must survive any future pressure to make the dashboard look better.

**Downstream implications.** It follows that **coverage is a first-class metric**: 13 of 39 skills currently ship a regression suite and 14 have direct validation coverage. The strategy's target is not 100% — it is that every skill which *writes into a controlled record* is covered, and that the uncovered remainder is a stated, reviewed list rather than an accident.

**Open questions.** `[VERIFY]` Whether to adopt a formal software-categorisation scheme (e.g. GAMP-style categories separating the vendor CLI from project-authored agents and skills) as the routing mechanism for assurance depth. The sister project `arthrex-pccp` does exactly this, and a category-based route is legible to a QA auditor who already knows the scheme — but no copy of the framework exists in this repo, so adopting it means importing it first.

### Human review is the control that carries the argument — and only if it is real

**Decision.** The compensating control that makes AI-assisted authoring defensible is **human review before a record becomes controlled**, and the project commits to the conditions that make that review a control rather than a signature. Specifically: the reviewer is named and competent for the content; the reviewer is **not** the author of the same record; the review attests to independent verification of correctness, not merely that text was read; the *diff* under review is retained as evidence; and release is blocked when any of those is missing.

**Why.** "A human reviewed it" is the entire load-bearing claim of an AI-assisted quality system, and it is also the easiest claim to hollow out. A review that is a rubber stamp is indistinguishable, in the record, from a review that caught nothing because there was nothing to catch — unless the conditions above are specified and evidenced. This project's own QMS already demands author≠reviewer independence in four separate places, including the requirement that signature dates be contemporaneous with the activity; the AI-assisted path must meet the same bar, not a lesser one designed around the tooling.

**What this commits us to.** The `ai-changelog` convention (recording *that* an edit was AI-assisted, vendor-neutrally, as non-published metadata) is necessary but **not sufficient** — it records provenance, not review. The gap the strategy must close is the attestation and the retained diff. Until that exists, the honest statement of posture is "AI-assisted authoring with human review as a process discipline", not "with human review as an enforced control".

**Downstream implications.** This is where the tooling strategy and the QMS meet: the review conditions above are the same independence conditions the design-control procedures already impose on verification records. Aligning them means one rule, not two.

**Open questions.** `[VERIFY]` A widely-cited enforcement precedent for AI-authored quality records exists in the sister project's operations strategy (a warning letter concerning AI-generated specifications and production records without adequate human review). It is **not** in this project's `docs/external/` and has not been verified against the byte-correct source here. It is a strong anchor if it verifies; it must not be cited until it does.

### What the workbench may and may not produce

**Decision.** The workbench is permitted to **draft, restructure, summarise, cross-check, and assemble** — and is prohibited from **attesting**. Concretely, it may draft controlled documents for human review, restructure existing approved content, generate trace and coverage projections, surface gaps and inconsistencies, and assemble submission packages from reviewed parts. It may **not**: declare a document compliant; author verification or validation evidence (test results, or a protocol signed off as executed); decide which regulations or standards apply; or emit a citation that no human will verify against its source.

**Why.** Each prohibition is the same principle in a different costume: the workbench may do work whose correctness a human can check, and may not perform the act of *certifying* correctness. Drafting is checkable. Attesting is not — an attestation is a claim about the world that the tool has no standing to make. The citation clause is the sharpest of the four in practice: a plausible, well-formatted, non-existent clause number is the highest-frequency and lowest-visibility failure this toolchain produces.

**What this commits us to.** An independent reference audit over citation-bearing controlled documents, run as a separate pass rather than as self-review — because self-review does not re-derive a citation from its source. The project already has this control (`/reference-audit` plus a `citations` verification engine and three source-class researchers) and the authoring rule already mandates it for citation-bearing edits; the commitment here is that it is actually run before a document is declared done.

**Downstream implications.** "May not author verification evidence" is the clause that most constrains the Testing & Validation strategy: drafting a *protocol* is permitted; producing a *result* is not.

**Open questions.** Whether "restructuring approved content" needs a tighter boundary — restructuring can change meaning, and the line between reformatting and rewriting is not self-evident.

### A control that does not execute is not a control

**Decision.** The strategy distinguishes **enforced** controls from **declared** ones, and commits to publishing the difference rather than describing the intended state. A control counts as enforced only if it executes, fails closed, and leaves a record.

**Why.** The gap between the two is currently wide enough to be the single most important thing this strategy can say, and every item is verifiable today:

| Control as described | Actual state (verified 2026-08-06) |
|---|---|
| Frozen controlled documents cannot be edited | The pre-tool-use hook is a **stub that returns success unconditionally**, and it is **not installed or registered at all** — designed, never wired |
| The pull-request trail is the audit record | **No branch protection** on the default branch — and it is not merely unconfigured, it is **unavailable on this repository's plan** (private repo without the required tier). Direct pushes are possible and nothing verifies the PR path was taken |
| CI enforces quality | **Zero** quality gates in CI — both workflows are self-committing artifact refreshers; every check is local and manual |
| The allowlist lets the team audit what has access to project data | The *skill* allowlist is complete (39/39). The **agent** allowlist is not — **18 of 50** skill-owned agents sit outside it. Separately, registry *provenance* is under-declared: `registries[]` accounts for **14 of 39** installed skills |
| The toolchain is validated | Last validation run **2026-07-28**, verdict **FAIL** (13/16), with **34 commits and 36 workbench file changes** since — two of its own revalidation triggers have fired with no re-run |
| A model change triggers revalidation | The run record never captures the model identifier, so the trigger **cannot fire** |

**What this commits us to.** Three things, in priority order. First, **fix or retract** — an inert control is either made to execute or is removed and the residual risk stated; leaving it registered is the worst option because it reads as protection. Second, **capture what makes a trigger fireable** — a revalidation trigger keyed to something the record does not contain is decorative. Third, **move at least the cheap gates into CI** — the security screen and the existing regression suites are already scripted, and a control that only runs when someone remembers is a control with an availability of "sometimes".

**Downstream implications.** This decision is deliberately uncomfortable and belongs in the strategy rather than in a defect list, because the *pattern* is what recurs: this toolchain makes it very cheap to declare a control and comparatively expensive to enforce one, so declarations accumulate faster than enforcement. Any future control added to the workbench should be reviewed against "does it execute, fail closed, and leave a record" before it is written down as a control.

**Open questions.** Whether the security screen's current false-positive class — findings raised against comments and docstrings that merely mention a config file — should be fixed in the scanner or dispositioned in the manifest. Left as-is it makes the screen a permanent red light, which is the standard route to control fatigue.

### Measurement stays honest about what is measured and what is modelled

**Decision.** The program measures agentic cost directly and models human-effort savings, and the two are **never** blended into a single headline number. Measured quantities (tokens, spend, sessions, user turns) are reported as measured; the effort-saved comparison is reported as **modelled and uncalibrated**, with its conservative bound leading.

**Why.** The measured side is real — at the time of writing, 28 sessions, 6.49 M output tokens and $2,124.29 over 22 active days, and already moving as sessions land (a figure quoted from this dataset should carry the date it was read). The modelled side carries a self-reported ~88% mean deviation between independent estimators on a blind re-estimate of the same tasks. Presenting a savings multiple derived from the second as though it had the precision of the first is the fastest way to lose a finance or quality audience permanently — and this program has already done the honest work of measuring that deviation, which most have not.

**What this commits us to.** The uncalibrated label travels with the number wherever it is rendered — task doc, dashboard, console, and any external retelling. A derived figure that reaches a slide without its provenance is a defect, not a rounding.

**Downstream implications.** The load-bearing weakness is coverage, not accuracy: telemetry exists for **1 of 5** roster members, so every per-team claim is really a per-person claim wearing a team label. A second, milder one is that the dataset is regenerated continuously by scheduled aggregation, so any figure lifted into a slide is a snapshot — it needs its as-of date attached or it silently ages.

**Open questions.** Whether to calibrate the effort model against even a small set of genuinely hand-executed tasks. Without that, the ratio stays order-of-magnitude forever.

### The knowledge loop stages but does not promote

**Decision.** Captured lessons must reach a **permanent home** — a skill, a rule, an agent prompt, project instructions, a glossary entry, or a folder README — or they are not knowledge management, they are an append-only log with a growing session-start cost.

**Why.** The ledger currently holds **76 staged entries, 0 promoted, 0 archived**. Every one of those loads into every session. The pipeline was designed with three stages and has only ever used the first, so the mechanism intended to make the project cheaper to work in has become a fixed tax that grows monotonically. This is a clean example of a capture habit succeeding while the promotion habit never started.

**What this commits us to.** A promotion pass with a real cadence, and an explicit archival path for lessons that were true once and are not anymore. Promotion is the step that changes future behaviour; staging only records that someone noticed.

**Downstream implications.** The same shape appears elsewhere in the workbench and is worth naming as a general property: **capture is cheap and self-reinforcing; consolidation is expensive and has no natural trigger.** Anything in this toolchain that accumulates — lessons, staged decisions, unassembled strategy blocks, task docs — needs a scheduled consolidation step or it will grow until it is unusable.

**Open questions.** Who owns the promotion pass, and at what cadence. Unowned, it will not happen — the evidence for that is the ledger itself.

### The evidence base is one operator, and the strategy should not pretend otherwise

**Decision.** Claims about team workflow, onboarding and ways of working are scoped to what the evidence supports: **114 of 115** task documents belong to one person, telemetry exists for **1 of 5** roster members, and every validation run, registry push and security record was produced by the same operator.

**Why.** A tooling strategy that describes a team practice which only one person has exercised is describing an intention. The onboarding material, the task-first workflow and the rules are genuinely designed for a team, and they may well work for one — but that is a hypothesis, and the honest framing distinguishes a designed practice from a demonstrated one.

**What this commits us to.** Treating multi-operator use as the **next real test of the workbench**, not as a solved property. The most informative signal available would be a second operator completing a full task cycle — activate, author, review, validate, push — and reporting where the workflow assumed context they did not have.

**Downstream implications.** Concentration is also a continuity risk: the knowledge required to operate the toolchain is currently mostly undocumented tacit knowledge held by one person, which is precisely the failure mode the lessons-promotion gap above prevents fixing.

**Open questions.** Whether the four other roster members are blocked by tooling friction, by access, or simply by not having had work routed to them — these have very different fixes and the current data cannot distinguish them.

## Testing & Validation Strategy — PP3500 programme

<!-- STRATEGY CONTENT: testing, verification, validation, usability, ai-ml, trace, acceptance-criteria, regression -->

### This strategy sequences and tailors an existing QMS; it does not invent a V&V philosophy

**Decision.** The verification and validation approach for the PP3500 programme is a **tailoring** of the procedures and templates the QMS already publishes — not a parallel method. The QMS supplies the verification protocol/report schema, the validation protocol/report schema, the summative usability protocol schema, the per-class software test depth, the traceability-matrix shape and its gate rule, the phase-gate entry/exit criteria, and the in-flight protocol deviation route. This strategy decides **which of those apply to which DHF, at what depth, in what order** — and authors only what the QMS genuinely lacks.

**Why.** Tailoring is the QMS's own expectation — the design-planning procedure requires a risk-based tailoring rationale, and the Design & Development Plan template prompts for exactly four factors: risk classification, software safety class, novelty, and reliance on a predicate. That is precisely the axis a 10-DHF portfolio spanning IEC 62304 Class A through C needs. Writing a fresh V&V philosophy alongside a QMS that already has one produces two sources of truth and an audit finding.

**A caveat that is itself a finding.** Those four factors exist **only as a fill-in prompt inside a template** — no procedure names them, and the design-control SOP has no tailoring clause at all. So the programme is tailoring against a form field rather than an authorised rule. An auditor who asks to see the clause that permits scaled rigor will not find one. Raising the four factors from a template prompt to a procedural clause is a QMS change this strategy should trigger, not assume.

**What this commits us to.** For each DHF, a stated tailoring position against those four factors, with the reasoning visible. A Class A cloud component and the Class C pump firmware should not carry the same test depth, and the *justification* for the difference is a design-control record, not a preference.

**Downstream implications.** The formal V&V Plan per DHF becomes a short document that names its tailoring and points at QMS schemas, rather than a long document that restates them. That is the difference between a plan that stays current and one that rots.

**Open questions.** The QMS publishes **five numbered phase gates** in one document and **six named design-review points** in another, with no published mapping between them, and one of the two contradicts itself in its own front matter. The V&V cadence hangs off that model, so the strategy must author the mapping before the gate schedule means anything. `[VERIFY]` against both governing documents before fixing the mapping.

### Verification and validation answer different questions and are evidenced differently

**Decision.** The programme holds the distinction strictly. **Verification** asks whether each design input was met, is keyed to `DI` identifiers, and is evidenced by protocol-and-report pairs with measurable acceptance criteria and a stated sample-size rationale. **Validation** asks whether user needs are met in the real use environment, is keyed to `UN` identifiers, and — per the QMS — is executed on **production-equivalent units, in the intended use environment, with representative users**, with summative usability evaluation forming part of it for any device with a user interface.

**Why.** Collapsing the two is the most common way a design-control record fails: a programme runs a thorough bench campaign, calls it V&V, and arrives at transfer with no evidence that a clinician can actually use the device safely. For a PCA pump the distinction is not academic — the delivery-accuracy question and the "can a nurse program this correctly under time pressure" question have almost nothing in common, and only the second is validation.

**What this commits us to.** Two-stage sign-off, as the QMS templates already mandate: the **protocol is approved before execution** (author, independent reviewer, quality) and the report after (test lead, independent reviewer, quality, design owner). A protocol approved after the fact is not a protocol; it is a description of what happened.

**And a correction to the obvious assumption.** Validation is *not* simply verification's sign-off plus more names. The validation template adds usability, clinical, risk-management and quality-leadership signatures — but it **drops the independent-reviewer row at the protocol stage and the quality-engineering reviewer row on the report**. Given that this decision's own thesis is that independence is a hard constraint, the heavier-looking approval chain is weaker at exactly the point that matters. The programme adds those two rows rather than inheriting the template's omission.

**Downstream implications.** Independence is a hard constraint, not a preference. The QMS mandates it in at least four places — test engineers cannot test what they wrote, design reviews require a participant without direct responsibility for the stage under review, software test reports need an executor plus an independent reviewer with independent code review at Class C, and reviewers may not be the author of the same record with signatures contemporaneous to the activity. **No executed V&V record yet exercises any of it** — the DHF holds stubs, not signed records — and the resourcing consequence — you cannot staff verification with only the people who built the thing — belongs in the programme plan now rather than at Gate 4.

**Open questions.** The QMS has **no standalone V&V Plan template and no V&V Summary Report schema**, despite both being required records and the summary reports being a pre-transfer gate condition. The planning obligation is partially covered — the Design & Development Plan and the Software Development Plan each carry a V&V section — but there is no schema for the summary reports the transfer gate depends on. These are the most load-bearing absent artifacts and this strategy should trigger their authoring.

### Acceptance criteria are born in the requirements, not in the protocol

**Decision.** Every design input carries its **acceptance criterion, verification method, upstream user-need trace, and risk-control linkage at the point the requirement is written** — not deferred to whoever later writes the protocol. The verification method is drawn from the template's four-value set (test / inspection / analysis / demonstration), which the programme adopts as the controlled vocabulary. Two things need aligning to make that real: the parent procedure names only three of the four, and the PP3500 requirements currently use **15 distinct free-text method values**, only one of which overlaps the set.

**Why.** A criterion invented at protocol-writing time is a criterion authored by the person most motivated for it to pass. Worse, it silently changes what "verified" means relative to what the team agreed to build. Putting the criterion in the requirements document makes the acceptance bar a reviewed design decision rather than a testing convenience.

**What this commits us to.** This is the contract the programme is **closest to already satisfying**, and that is worth saying plainly: the PP3500 design inputs carry genuinely quantitative, standard-anchored criteria, including explicit sample sizes and gravimetric methods. Two specific breaks remain. First, **30 of the 34** design inputs hold a bare method *label* where they should hold a verification-activity *identifier* — only four carry one — so almost no requirement points at the protocol that discharges it. Second, the requirements document has **no risk-control linkage column**, even though the QMS template carries one: the column was dropped in the instance, not missing from the standard. That means the question "which verification proves this risk control is effective" cannot be answered from the requirements document, and risk-control effectiveness is exactly what a reviewer will probe on an infusion pump.

**Downstream implications.** Closing the second break is a prerequisite for the risk file's residual-risk argument, not merely a traceability nicety.

**Open questions.** The verification-identifier namespace is inconsistent across three forms in the QMS and the DHF. Pick one, publish the mapping, and migrate — this is cheap now and expensive after protocols exist.

### Trace is the spine, and the current gate rule is unsatisfiable

**Decision.** The design traceability matrix is maintained **continuously across the gates** — user needs to design inputs early, design outputs at the design gate, verification and validation at the V&V gate — and never reconstructed at the end. The mandated shape is five columns: user need → design input → **design output** → V&V → risk control, with Class B and C software additionally tracing each requirement to architecture elements and to unit, integration and system tests.

**Why.** The QMS states the operative rule bluntly: a V&V activity with no upstream trace is testing something nobody agreed to build. And the gate rule has teeth — **gate disposition shall not be Pass while any orphan check fails**, with *Conditional* available only when the orphans are identified, time-bounded and owned. That converts trace from documentation into a schedule dependency, which is the only framing under which it gets maintained.

**What this commits us to.** Three concrete gaps between the mandated shape and what exists, all verifiable today:

1. **There is no design-output layer in the trace matrix, and none is possible.** The configured layers are user needs, design inputs, software requirements, architecture, V&V and risk. The `DO` rung the QMS mandates is not merely unconfigured — it is **not expressible in the trace skill's schema**, which enumerates those six as the only valid layer keys. So the chain from requirement to the thing actually built is broken by construction, and closing it requires a change to the tooling, not just to a config file.
2. **The architecture layer produces no edges — for want of source data, not configuration.** The layer *is* configured against the software architecture document; that document simply contains no design-input references, so there is nothing for the adapter to bind and the layer reports its edges as unknown.
3. **Verification is barely connected to anything.** The V&V layer holds **3 nodes against 34 design inputs**, and **28 of 32 software requirements are orphaned**. Design inputs themselves are well-connected downstream (1 orphan of 34) — the break is not at the top of the chain, it is that almost nothing reaches verification.

**Downstream implications.** Since unit and integration test code is classified by the QMS as a **design output** rather than a V&V record, the missing `DO` layer also means test code currently has no home in the trace chain — and test code that is a design output must itself be verified.

**Open questions.** Whether to add the `DO` layer to the existing trace configuration or to treat design outputs as a per-DHF register that the matrix references. The first is cheaper; the second may model reality better for hardware.

### What happens when a verification test fails — the QMS is silent, so this strategy says it

**Decision.** A failed verification or validation result is **dispositioned through a defined route before any retest**, and the disposition is a record. The route: classify the failure (test-setup or protocol defect / product defect / criterion defect), and route accordingly — protocol defects through the deviation procedure with quality approval, product defects into the design-change and corrective-action path, and criterion defects back to the requirement with a design review, never by adjusting the criterion inside the protocol. **Re-running a failed test without a recorded disposition is prohibited.**

**Why.** This is a genuine hole, and a specific one. The design verification and validation procedure is silent on failure; the corrective-action procedure's list of sources covers complaints, audits, supplier non-conformities, process monitoring, servicing, post-market surveillance and management review — **it does not name design verification or validation failure**; and the non-conforming product procedure is scoped to product, not to test results.

**The gap is narrower than "the QMS is silent", and stating it precisely is what makes it defensible.** Software V&V failure *is* routed — the software V&V work instruction sends defects into the software problem-resolution procedure. What has no defined destination is a failed **system-level or hardware** verification or validation: exactly the bench, electrical, alarm and delivery-accuracy campaigns that dominate a PCA pump's evidence base. Left unstated, the default behaviour under schedule pressure is universal and well documented across the industry: adjust the criterion until the test passes.

**What this commits us to.** The adjacent procedure that *does* exist — the deviation route for departing from an approved protocol mid-execution — is explicitly on the V&V critical path, requires independent quality approval, requires that pre-execution deviations be approved *before* the activity starts, names "forgot to file" and "faster to ask later" as unacceptable rationales, and escalates a deviation repeated three times within twelve months to corrective action. This strategy adopts it as the in-flight route. **But its form does not exist** — the procedure points at a document-change form as a placeholder. That gap sits directly on the V&V path and should be closed before protocol execution begins.

**Downstream implications.** This is the missing half of "acceptance criteria philosophy": a criterion is only meaningful if the consequence of missing it is defined in advance.

**Open questions.** Whether design V&V failure should be added as a named corrective-action source in the QMS, or handled entirely within design change control. The first is more conservative and more auditable.

### Software V&V scales by safety class — but not from the distillations currently in this repo

**Decision.** Software verification depth scales with IEC 62304 safety class across the portfolio, and the authoritative per-class requirement mapping is taken from **the standard's own normative summary table**, not from any secondary distillation held in this project.

**Why.** This is a live correctness hazard, not a hypothetical. **Three** distillations of this standard exist in the repo and they **disagree with each other** about whether system-level testing is required for Class A — two say it is, one says it is not — and the registry-side copy explicitly flags its own table as needing verification against the standard's normative table. Building the programme's class-scaling rules from any of them would bake a known-uncertain mapping into the document that decides how much testing the pump firmware receives.

**What this commits us to.** Obtaining the class mapping from the standard itself, and recording that provenance in the V&V plan so a reviewer can see the table was not derived from a paraphrase.

**Downstream implications.** The same caution applies more sharply to two other standards in this repo. The project-tier copies of the usability-engineering and health-software standards **carry invented clause numbering**, and — verified directly — the quarantine banner warning about it exists **only on the registry copy, not on the project copy an author would naturally open**. Any clause number cited from the project tier for those two standards is untrustworthy. Until the banners are propagated, cite the QMS's own verified clause mapping for usability, and do not cite sub-clause numbers for the health-software standard at all.

**Open questions.** Whether to fix this at the source by propagating the quarantine banners to the project tier. It is a small edit that removes a standing trap, and it protects every future author, not just this document.

### Usability validation is validation, and its acceptance is safety, not satisfaction

**Decision.** Summative usability evaluation is part of **design validation**, executed on production-equivalent devices with representative users in the intended use environment, with acceptance keyed to **hazard-related use scenarios** — every such scenario completed safely by every participant, or residual risk demonstrated acceptable through analysis. Participant counts follow the QMS floor of at least 15 per distinct user group unless a documented rationale justifies fewer, and observed use errors are classified with root cause attributed to user-interface design, training, or the instructions for use.

**Why.** For a PCA pump this is the highest-consequence validation activity in the programme. FDA's current human-factors submission guidance names infusion pumps explicitly as a device type with known use-error history requiring human-factors validation data — this device class does not get to argue its way out of summative testing. And the acceptance basis matters: aggregate task-success rates can look excellent while the specific hazard-related scenario fails, which is the scenario that harms a patient.

**What this commits us to.** The programme is better positioned here than it may appear — the design inputs already carry participant counts consistent with the QMS floor, and the summative protocol schema exists as a QMS template with hazard-scenario acceptance and participant-rationale sections built in. **Unpopulated Rev 0.1 draft instances of both the summative protocol and the usability engineering file already exist in the DHF**; what is genuinely absent is the **use-related risk analysis**. So the work is to populate two stubs and author one missing document, not to start from nothing.

**Downstream implications.** Two sequencing consequences. The summative protocol cannot be populated until the use-related risk analysis identifies which scenarios are hazard-related — so the URRA is on the critical path to validation, not parallel to it. And distinct user groups for a PCA pump plausibly include the clinician who programs the pump, the nurse who responds to alarms, and the patient who presses the bolus button, whereas the two design inputs carrying participant counts currently name **one** group. That tension is a participant-count decision with real cost implications, and it should be made deliberately and early rather than discovered when the protocol is written.

**Open questions.** `[VERIFY]` The FDA *process* guidance on applying human factors engineering — as distinct from the current guidance on human-factors *content in submissions* — is **absent from every tier in this repo**. It is the document that governs how summative testing is actually run. Import it before authoring the protocol.

### AI-enabled behaviour and PCCP changes are verified against a frozen baseline

**Decision.** For AI-enabled components and any change executed under the Predetermined Change Control Plan, performance evidence is generated against a **locked, version-controlled test set** that is not modified without a documented change-control decision, and every change must demonstrate non-inferiority against **two** baselines: the cleared version **and** the most recently modified version.

**Why.** The locked test set exists so performance is comparable across model versions; a test set that drifts with the model makes every comparison meaningless while looking rigorous. The dual baseline exists to stop cumulative drift: a sequence of changes each non-inferior to the *cleared* version can still ratchet performance steadily downward relative to what is actually in the field. For a device where the algorithm influences dose delivery, that ratchet is a patient-safety mechanism, not a metrics concern.

**What this commits us to.** Dataset governance as a design-control activity — partitioning with a frozen test partition, versioning, per-model archival, a documented representativeness position with its limitations stated honestly, and a pre-specified subgroup analysis plan. Selecting a decision threshold by sweeping it on the test set and choosing the best point is **test-set contamination** and should be treated as a defect, not a tuning step.

**Downstream implications.** Where a review or confirmation step is credited as a risk control, verifying it requires treating it as a **classifier** — measuring whether it fires on the right cases, with a confidence bound, rather than counting how often it fired. A tally tells you the gate is active; it never tells you the gate is correct. This applies directly to any PP3500 dose-limit, occlusion or alarm gate.

**Open questions.** Which PP3500 behaviours are genuinely AI-enabled versus rule-based, and therefore which fall under this decision at all. The manifest carries an AI-enabled flag per DHF; the strategy should state the resulting scope explicitly rather than leaving it to be inferred.

### The standards floor for an infusion pump is not yet in this repository

**Decision.** Before bench and safety verification protocols are authored, the programme imports and distils the device-specific standards and guidance that govern them, and treats their current absence as a **blocking gap** rather than a documentation backlog.

**Why.** The electrical, alarm and infusion-pump-specific standards are present and genuinely project-specific — that tier works. The gaps are at the two ends that matter most for this device. The FDA guidance covering infusion pumps across the total product lifecycle — the document a reviewer would expect a pump submission to be built against — is **absent from every tier**, appearing only as a mention inside another file. The AAMI technical report covering patient-controlled analgesia mode specifically is FDA-recognised and **distilled nowhere**.

**What this commits us to.** A concrete blocker with a name: the electromagnetic-compatibility acceptance criterion is currently "essential performance maintained", while the record that formally defines essential performance for this device is marked to-be-determined, and no QMS procedure covers essential performance at all. **The EMC test plan cannot be written until essential performance is defined.** That is a sequencing fact the programme plan should carry, not a detail for the test engineer to discover.

**Downstream implications.** The project-side guidance tier is currently functioning as a duplicate distillation set rather than an applicability set — none of its content files carries device-specific applicability commentary, and **11 of 12 lack the finding-aid banner** that marks the registry distillations as paraphrase-not-source. They do cite their source documents, so the defect is not missing provenance; it is that nothing on the page warns a reader that the text is a summary. Verification protocols grounded on that tier inherit the problem.

**Open questions.** Whether the QMS-level quality-system standard is genuinely out of project scope. It is currently recorded as evaluated-and-not-required on the grounds that it is owned at the organisation level, but the project's own regulatory anchor makes its design-controls clause the reference for this programme — those two positions are inconsistent and one of them should move.

## Research Findings

<!-- LESSONS LEARNED: strategy-authoring, tooling -->

**R1 — The `operations` stub is not an empty domain. It is an unassembled one.** A scan of every `tasks/*/NNN-*.md` for `<!-- STRATEGY CONTENT -->` tags found **12 pre-existing `operations` blocks** (tasks 002, 007, 057, 059, 060, 061, 062, 104, 108, 109, 111, 112) totalling roughly **4,900 words** of already-authored strategic content — registry governance, repo governance, teaching-project access policy, commercial-analytics tooling architecture, advisor roster, cost model, skill topology. The document reads `awaiting-content` only because **`/strategy assemble operations` has never been run**. The domain has been accumulating decisions for months with no assembly pass.

Two consequences for this task:
1. Assembling `operations` is not a blank-page exercise — it will surface a substantial existing record, and the tooling content authored here has to sit coherently *alongside* that history rather than pretend to be the whole story.
2. Most of those blocks carry **no `###` subsections** (only 007 and this task do) — they are prose under an H2, so the assembler will use each block's H2 as the decision heading. Several of those H2s are poor section titles inherited from their source task's structure (`Background`, `Goals`, `Todos`, `Review Findings`). Expect an assembled document whose older decisions are titled after task-doc scaffolding rather than after the decision they record. That is a cosmetic defect in the historical content, **not** something to fix by hand-editing the assembled output — the assembled doc is a generated artifact.

**R2 — The `testing` domain has almost nothing: exactly 1 tagged block.** Only `ben/110` has tagged testing content (workbench-validation reviewer-readability + reproducibility). So unlike `operations`, the testing & validation strategy is genuinely a blank page and must be authored substantially here, grounded in the V&V ground-truth research rather than assembled from history.

**R4 — Sister project `arthrex-pccp`: they have the regulatory wrapper, we have the executable evidence.** Their `operations-strategy.md` is an assembled 7-decision document that reaches a formal **determination** — that classical IQ/OQ/PQ tool validation is not required for the AI authoring toolchain *provided the human-review controls are real and evidenced* — supported by executed QMS forms (a GAMP-category assessment splitting the workbench into CLI+API = Category 4, agents = Category 5, output-producing skills = Category 5; and a non-product-software-validation package that renames IQ/OQ/PQ to Setup / Functional-Use / Workflow Verification because classical qualification does not map to a non-deterministic tool). But their validation test cases are **all Pending**, their AI-authoring SOP does not exist, and the enforcement their controls table claims (`change-control release`) is a documented stub.

We are the mirror image: `workbench-validation` has **4 executed runs** with pinned test artifacts and sha256 manifests, a 15-need register, tiered coverage classes and an explicit honesty model for non-deterministic behavior — and **no regulatory wrapper at all**. The highest-value move is to join the two: adopt their determination structure and GAMP framing, and populate the evidence column they left empty with our actual run records.

Their `testing-strategy.md` **does not exist**, and their own V&V-lead gap analysis names that absence as the reason system-integration verification is "owned by no current artifact". That is a direct warning about the cost of leaving a declared domain unassembled.

**R5 — The toolchain inventory is materially different from the toolchain narrative.** Ground truth (2026-08-06): 39 skills, 30 top-level agents (25 symlinked, **5 are copies that will silently drift on the next sync** — the open defect `ben/066`), 50 skill-owned agents, 12 auto-loaded rules, 12 registered hooks. Against that:

| Claim a tooling strategy would want to make | What is actually true |
|---|---|
| "The toolchain is validated" | `workbench-validation` verdict is **FAIL** (13/16), last run **2026-07-28**, with **34 commits and 36 `.claude/` file changes since**. Two of its own revalidation triggers have fired with no re-run. |
| "A model change triggers revalidation" | `model_id` is **null** in every run record — the runner never captures it, so the trigger is structurally unfirable. |
| "Controlled documents cannot be edited when frozen" | `change-control/hooks/pre_tool_use_frozen.py` is a **stub that exits 0**. The control is designed, registered, and inert. |
| "The PR trail is the audit control" | There is **no branch protection on `main`** (secops check, 2026-08-05). The audit posture rests on convention. |
| "CI enforces quality" | **Zero** quality gates in CI. Both workflows are self-committing artifact refreshers with `[skip ci]`. Every control is local-and-manual. |
| "The allowlist lets the team audit what has access to project data" | The *skill* allowlist is complete (39/39); the **agent** allowlist is not — **18 of 50** skill-owned agents are unapproved. Registry *provenance* is separately under-declared: `registries[]` accounts for **14 of 39**. _(Corrected from 19/50 and 9/39 by the verification pass — see R7.)_ |
| "We capture lessons" | Lessons ledger: **76 staged, 0 promoted, 0 archived** — the promotion pipeline has never run, and all 76 load every session. |
| "The team uses this" | **114 of 115** task docs are one person's; telemetry exists for **1 of 5** roster members. _(The 120 figure counted the five `000-index.md` files as task docs.)_ |

Measured usage is real and substantial: 28 sessions, 6.49 M output tokens, 1.71 B cache-read, **$2,124.29** over 22 active days. The value model self-labels as *modeled and uncalibrated* (~88% inter-estimator deviation on a blind re-estimate) — a rare and correct piece of honesty the strategy should preserve rather than launder.

~~Also live right now: `tools/usage-metrics/usage.json` carries 26 unresolved git conflict markers and does not parse.~~ **RETRACTED — this was false.** The verification pass and an independent check both found the file parses cleanly with zero conflict markers, in the working tree and at HEAD, across its last 40 revisions. The incident was real but had already been fixed by regeneration on 2026-08-06, and its cause was a conflicted `git stash pop` on locally-uncommitted generated files — **not** the force-publish transport. See R7.

**R6 — 15 strategy tags in `ben/054` are malformed and have been silently invisible to the harvester across six domains.** Surfaced by the testing assembler and verified independently: every `<!-- STRATEGY CONTENT: … -->` tag in `tasks/ben/054-agentic-first-medtech-strategy.md` is written **without the closing `-->` on the tag line**. Repo-wide the split is **139 well-formed / 15 malformed, and all 15 malformed are in 054**.

Two consequences, both bad and neither visible:
1. The scanner's tag regex requires a self-closed tag on its own line, so **none of these blocks has ever been harvested** — by any domain, ever. The affected first-values span `testing`, `architecture`, `development`, `operations`, `regulatory` and `risk`, so this one file has been silently absent from six strategy domains.
2. Because the tag never closes, each block's body sits **inside an unterminated HTML comment** — so the content is also invisible when reading the task document as rendered markdown. It has been doubly hidden: not harvested, and not readable.

**Deliberately NOT fixed in this task.** Repairing the tags would inject a large volume of previously-unreviewed historical content into six strategy documents in one unreviewed sweep — including `operations` and `testing`, the two being assembled here. That is a separate, reviewable change: fix the tags, read what emerges, then re-assemble each affected domain. Recorded as a follow-up rather than folded in.

**R7 — The independent verification pass found 8 real errors in 17 authored decisions, and the pattern in them is the lesson.** After assembly, every quantitative and factual claim in the ben/115-sourced decisions was re-checked against the repository by an agent briefed to **falsify, not confirm**. It returned 8 errors and 4 overstatements. All were corrected in both the source blocks and the assembled documents. The three worst:

1. **"30 orphaned design inputs and 28 orphaned software requirements"** — off by 30× on the first figure. The current sidecar reports **1** orphaned design input and 28 orphaned software requirements; the 30 came from a **superseded April 2026 artifact that has no software layer at all**, so the two numbers could not have come from one build. This was the entire quantitative basis for "the gate rule is unsatisfiable". Replaced with the verified and more damning statement: the V&V layer holds **3 nodes against 34 design inputs**.
2. **"the usage data file carries conflict markers and does not parse"** — false. It parses cleanly in the working tree and at HEAD, with zero markers across its last 40 revisions. The incident was real but had been fixed by regeneration hours earlier, and its cause was a conflicted `git stash pop`, not the publish transport as claimed. **The tell was internal to the document**: the same decision quoted session and spend figures *out of the file it said would not parse*, and I did not notice.
3. **"the design-control procedure authorises scaling against four factors"** — the four factors exist **only as a `{{}}` fill-in prompt inside a template**. No procedure names them. This was the load-bearing premise of the whole "tailor rather than invent" posture, citing an authority that does not exist. Reframed — and the absence is now stated as a finding in its own right.

**Why this matters beyond the corrections.** Every one of these came from a research agent's report that I transcribed without re-deriving. The reports were largely excellent — most claims verified exactly, including the sharpest and most falsifiable one — but *a confident, well-sourced-looking number is exactly what does not get re-checked*. Two structural habits follow:

- **Absence claims are the most dangerous class.** "X does not exist anywhere" is cheap to write, reads as thorough, and is falsified by one search. Two of the eight errors were absence claims (the usability stubs; the failed-test routing), and a third was a near-miss. Any absence claim in a regulated document needs its own search before it ships.
- **A number quoted from a source contradicts a claim about that source.** The usage-file error was self-detectable from the document alone. Internal consistency is a free check and was not run.

The verification pass cost one agent invocation and prevented a document that would have been discredited by its own most-quotable number. It should be a standing final stage for any strategy assembled from research, not a one-off.

**R8 — The two assemblers emitted different history headings, because the template and the contract disagree.** `operations-strategy.md` came out with `## History`; `testing-strategy.md` with `## Assembly History`. Neither agent was wrong: the `default-strategy.md` template specifies `## Assembly History` (and the existing `commercial-strategy.md` follows it), while the assembler contract and `strategy/SKILL.md` both specify `## History`. Two of three sources say one thing, the templates say another, and each assembler picked a defensible authority.

Left as-is deliberately — hand-fixing the heading in an assembled document would be reverted by the next assembly. The real fix is upstream: reconcile the templates with the contract in the `strategy` skill so every future assembly agrees. Logged as a follow-up.

**R3 — Strategy documents are generated artifacts; authoring them directly would be destroyed on next assembly.** Per `strategy/SKILL.md`, the assembled documents carry `> Do not edit directly — update the source task and run /strategy assemble`. The authoring path is therefore: write tagged blocks in *this* task doc → assemble. Writing `operations-strategy.md` by hand would have looked correct and been silently overwritten the first time anyone ran an assembly.

## Todos

- [x] Research: sister project `arthrex-pccp` surveyed for borrowable patterns
- [x] Research: PDLC_DEMO toolchain ground truth established (skills, agents, hooks, CI, governance, measurement, tool validation)
- [x] Research: PDLC_DEMO V&V ground truth established (DHF roster, V&V artifacts, trace integrity, risk linkage, usability, standards, AI/ML, submission expectations)
- [x] Author `operations` (tooling) STRATEGY CONTENT blocks — 8 decisions, 2,641 words, 3 `[VERIFY]`
- [x] Author `testing` (V&V) STRATEGY CONTENT blocks — 9 decisions, 3,019 words, 2 `[VERIFY]`
- [x] `/strategy assemble operations` → 21 decisions (`D-OPS-1.1`–`1.21`) from 14 blocks across 13 tasks, ~8,970 words
- [x] `/strategy assemble testing` → 10 decisions (`D-TEST-1.1`–`1.10`) from 2 blocks, ~4,690 words
- [x] Verify both render in the console — roll-up now **5 domains live / 48 decisions / 3 awaiting content** (was 3 / 17 / 5); `/strategy/operations` and `/strategy/testing` both 200; sentinels paired 21/21 and 10/10
- [x] Independent verification pass over every quantitative/factual claim in the ben/115-sourced decisions — **8 errors + 4 overstatements found** (see R7)
- [x] Corrections applied — 6 to `operations`, 15 to `testing` — in **both** the source blocks and the assembled documents, plus 3 in the research-findings table; correction pass recorded in each document's history
- [ ] Follow-up (separate task): repair the 15 malformed tags in `ben/054` and re-assemble the six affected domains — see R6

## Verification

1. `/strategy scan` shows this task's blocks under both domains with no unrecognized-domain warnings.
2. `/strategy validate operations` and `/strategy validate testing` — `[VERIFY]` markers enumerated, no unresolved conflicts, no `## Uncategorized` content.
3. Console: `/strategy` roll-up shows both domains live (not "awaiting content"); each detail page renders its decisions.
4. **Reference audit** (`/reference-audit`) over both assembled documents before the task is declared done — both are citation-bearing (standards clauses, FDA guidances, QMS document IDs). Per `regulatory-authoring.md`, this is a final-stage todo run as an independent subagent, verifying each citation against the byte-correct source rather than a distilled finding-aid.
5. Every claim about what the project currently HAS is grounded in the research agents' ground-truth reports — demo-grade content is labelled as such and never presented as real V&V evidence.

## Open Questions

- Does the team want a standalone `tooling` domain eventually, or is `operations` the durable home? (Decided the cheap way for now — see Decisions.)

## Resume

### In-flight artifacts
- Three research agents dispatched 2026-08-06: arthrex-pccp survey, PDLC_DEMO toolchain inventory, PDLC_DEMO V&V inventory. Findings land in this doc's Research Findings section.
- Nothing assembled yet. Both target documents are still `awaiting-content` stubs.

### First action on resume
1. Read the Research Findings section below before authoring — the strategies must be grounded in it, not in assumption.
2. Author the tagged blocks, then `/strategy assemble operations` and `/strategy assemble testing`.
3. Activation: `bash .claude/hooks/task-activate.sh add <SESSION_ID> 115`

## Economics

_By-hand person-hour estimate, filled at checkpoint per the effort-estimation rubric (`usage-metrics` skill)._

```json
{
  "economics": {
    "method_version": 1,
    "method_ref": ".claude/skills/usage-metrics/references/effort-estimation-rubric.md",
    "agentic_hours": {
      "min": 2.5,
      "max": 4
    },
    "todos": [
      {
        "todo": "Three-front ground-truth research \u2014 sister-project survey, toolchain inventory, V&V/QMS inventory",
        "personas": [
          "quality-engineering",
          "regulatory-affairs",
          "rd-lead"
        ],
        "manual_hours": {
          "min": 24,
          "max": 40
        },
        "confidence": "med",
        "basis": "audit/gap-assessment anchor (~1-3 auditor-days + reporting for a focused audit, x3 fronts); the V&V front alone read 72 controlled QMS documents and cross-checked three standards-distillation tiers"
      },
      {
        "todo": "Author the tooling strategy \u2014 8 decisions, ~2,600 words grounded in the inventory",
        "personas": [
          "quality-engineering",
          "rd-lead"
        ],
        "manual_hours": {
          "min": 18,
          "max": 40
        },
        "confidence": "med",
        "basis": "document-authoring anchor 3-7 hr/page at the regulated top end (~6 pages); cost is judgment not prose \u2014 the enforced-vs-declared control table required verifying six separate claims about live system state"
      },
      {
        "todo": "Author the testing & validation strategy \u2014 9 decisions, ~3,000 words spanning V&V, trace, usability, AI/ML and standards grounding",
        "personas": [
          "vnv-lead",
          "quality-engineering",
          "human-factors",
          "regulatory-affairs"
        ],
        "manual_hours": {
          "min": 24,
          "max": 49
        },
        "confidence": "med",
        "basis": "document-authoring anchor at the regulated top end (~7 pages) plus a specialist analysis adder; four personas because the decisions span V&V method, trace schema, human factors and standards applicability \u2014 judgment-tier per the rubric's note that no published hour norm exists for QE/HF analysis"
      },
      {
        "todo": "Assembly of both domains (14 blocks across 13 tasks for operations; 2 for testing) incl. heading substitutions, ID allocation and conflict assessment",
        "personas": [
          "quality-engineering"
        ],
        "manual_hours": {
          "min": 6,
          "max": 12
        },
        "confidence": "high",
        "basis": "mechanical assembly plus a Tier-2 semantic conflict assessment across 21 decisions; judgment, mid-range"
      },
      {
        "todo": "Independent falsification pass over every quantitative claim + applying 24 corrections across source, assembled docs and findings table",
        "personas": [
          "quality-engineering",
          "vnv-lead"
        ],
        "manual_hours": {
          "min": 12,
          "max": 24
        },
        "confidence": "med",
        "basis": "document/design-review inspection anchor at the rigorous regulated rate (1-3 pg/hr over ~13 pages, x2 reviewers) \u2014 the pass that caught a 30x error in the document's most quotable figure"
      }
    ]
  }
}
```

## Changelog

- 2026-08-06: **Both strategies assembled, verified and corrected.** `operations-strategy.md` — 21 decisions (`D-OPS-1.1`-`1.21`, ~9,180 words) from 14 tagged blocks across 13 tasks; the 8-decision tooling strategy leads and 12 previously-unassembled historical blocks came with it. `testing-strategy.md` — 10 decisions (`D-TEST-1.1`-`1.10`, ~5,400 words), 9 of them new device-V&V content. Console roll-up moved 3 to 5 domains live and 17 to 48 decisions; 19 routes green, zero server exceptions.
- 2026-08-06: **Independent falsification pass found 8 errors and 4 overstatements** in the 17 authored decisions; all corrected in source blocks, assembled documents and the findings table (24 edits), with a correction note added to each document's history. Worst three: a 30x error in the orphan count that was the entire basis for one decision; a claimed live data-file corruption that was false and already fixed (and self-detectable — the same decision quoted figures out of the file it said would not parse); and a load-bearing citation to a tailoring authority that turned out to be a template fill-in prompt. Lesson recorded as R7.
- 2026-08-06: Two structural defects found and logged rather than fixed — **15 malformed strategy tags in `ben/054`** that have made that task invisible to the harvester across six domains (R6), and a **template-vs-contract disagreement on the history heading** in the `strategy` skill (R8).
- 2026-08-06: Task created. Scope: author the tooling strategy (`operations` domain) and the testing & validation strategy (`testing` domain), both currently stubs. Established that tooling belongs in `operations` — already named "Operations & Tooling" with agentic infrastructure in its registered scope — rather than a new domain. Three research agents dispatched to establish ground truth before authoring.
