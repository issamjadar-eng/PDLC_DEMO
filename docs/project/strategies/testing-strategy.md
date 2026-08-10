# Testing & Validation Strategy

<!-- Assembled: 2026-08-06 by /strategy assemble -->
<!-- Domain: testing -->
<!-- Sources: ben/115, ben/110 -->

> This document is auto-assembled from `<!-- STRATEGY CONTENT: testing, ... -->` tags in task documents.
> Do not edit directly — update the source task and run `/strategy assemble testing`.
> Unresolved items are marked with [VERIFY].

## Scope & Approach

This shared testing strategy covers **verification and validation for the PainEase PCA Advanced (PP3500) programme** — how design inputs are verified, how user needs are validated, how software V&V scales by IEC 62304 safety class across the DHF portfolio, how usability validation is run and accepted, how AI-enabled and PCCP-governed behaviour is evidenced, and what standards floor must be in place before bench and safety protocols are authored. Its governing posture is that the QMS already publishes the protocol/report schemas, the trace shape and its gate rule, and the phase-gate criteria — this strategy **tailors and sequences** them per DHF rather than authoring a parallel V&V method.

A second, deliberately separate concern also lives here: **validation of the agentic workbench itself** — the toolchain that authors and audits DHF content. That evidence validates the tools, not the device, and is held apart from device V&V records; it is captured in the final decision below and its artifacts live under `docs/project/workbench-validation/` and `tools/workbench-validation/`.

## Plans Informed

| Formal Plan | DHF | How This Strategy Informs It |
|------------|---------|------------------------------|
| V&V Plan | each DHF | Coverage approach, tailoring position, traceability, test architecture |
| Test protocols | each DHF | Protocol/report structure, acceptance-criteria provenance, failure disposition, reuse across components |
| Usability plan | pca-device (lead) | Formative/summative approach, hazard-related-scenario acceptance, use-error analysis |

_The DHF column identifies which DHF each formal plan lives under — formal outputs remain per-DHF under `docs/project/dhfs/<dhf>/...` even though the upstream strategy is shared._

## Strategy Decisions

_Decisions are ordered newest-first by source-task last-modified date. Per-component nuance is carried inline (per-DHF tailoring, IEC 62304 class scaling). Each decision is wrapped in `D-TEST-*` sentinels for stable addressing by the project-console and downstream tooling._

<!-- DECISION:start id=D-TEST-1.1 status=active source=ben/115 created=2026-08-06 last-edited=2026-08-06 -->
### 1.1 This strategy sequences and tailors an existing QMS; it does not invent a V&V philosophy

**Decision.** The verification and validation approach for the PP3500 programme is a **tailoring** of the procedures and templates the QMS already publishes — not a parallel method. The QMS supplies the verification protocol/report schema, the validation protocol/report schema, the summative usability protocol schema, the per-class software test depth, the traceability-matrix shape and its gate rule, the phase-gate entry/exit criteria, and the in-flight protocol deviation route. This strategy decides **which of those apply to which DHF, at what depth, in what order** — and authors only what the QMS genuinely lacks.

**Why.** Tailoring is the QMS's own expectation — the design-planning procedure requires a risk-based tailoring rationale, and the Design & Development Plan template prompts for exactly four factors: risk classification, software safety class, novelty, and reliance on a predicate. That is precisely the axis a 10-DHF portfolio spanning IEC 62304 Class A through C needs. Writing a fresh V&V philosophy alongside a QMS that already has one produces two sources of truth and an audit finding.

**A caveat that is itself a finding.** Those four factors exist **only as a fill-in prompt inside a template** — no procedure names them, and the design-control SOP has no tailoring clause at all. So the programme is tailoring against a form field rather than an authorised rule. An auditor who asks to see the clause that permits scaled rigor will not find one. Raising the four factors from a template prompt to a procedural clause is a QMS change this strategy should trigger, not assume.

**What this commits us to.** For each DHF, a stated tailoring position against those four factors, with the reasoning visible. A Class A cloud component and the Class C pump firmware should not carry the same test depth, and the *justification* for the difference is a design-control record, not a preference.

**Downstream implications.** The formal V&V Plan per DHF becomes a short document that names its tailoring and points at QMS schemas, rather than a long document that restates them. That is the difference between a plan that stays current and one that rots.

**Open questions.** The QMS publishes **five numbered phase gates** in one document and **six named design-review points** in another, with no published mapping between them, and one of the two contradicts itself in its own front matter. The V&V cadence hangs off that model, so the strategy must author the mapping before the gate schedule means anything. `[VERIFY]` against both governing documents before fixing the mapping.
<!-- Source: ben/115, "This strategy sequences and tailors an existing QMS; it does not invent a V&V philosophy", last modified 2026-08-06 -->
<!-- DECISION:end id=D-TEST-1.1 -->

<!-- DECISION:start id=D-TEST-1.2 status=active source=ben/115 created=2026-08-06 last-edited=2026-08-06 -->
### 1.2 Verification and validation answer different questions and are evidenced differently

**Decision.** The programme holds the distinction strictly. **Verification** asks whether each design input was met, is keyed to `DI` identifiers, and is evidenced by protocol-and-report pairs with measurable acceptance criteria and a stated sample-size rationale. **Validation** asks whether user needs are met in the real use environment, is keyed to `UN` identifiers, and — per the QMS — is executed on **production-equivalent units, in the intended use environment, with representative users**, with summative usability evaluation forming part of it for any device with a user interface.

**Why.** Collapsing the two is the most common way a design-control record fails: a programme runs a thorough bench campaign, calls it V&V, and arrives at transfer with no evidence that a clinician can actually use the device safely. For a PCA pump the distinction is not academic — the delivery-accuracy question and the "can a nurse program this correctly under time pressure" question have almost nothing in common, and only the second is validation.

**What this commits us to.** Two-stage sign-off, as the QMS templates already mandate: the **protocol is approved before execution** (author, independent reviewer, quality) and the report after (test lead, independent reviewer, quality, design owner). A protocol approved after the fact is not a protocol; it is a description of what happened.

**And a correction to the obvious assumption.** Validation is *not* simply verification's sign-off plus more names. The validation template adds usability, clinical, risk-management and quality-leadership signatures — but it **drops the independent-reviewer row at the protocol stage and the quality-engineering reviewer row on the report**. Given that this decision's own thesis is that independence is a hard constraint, the heavier-looking approval chain is weaker at exactly the point that matters. The programme adds those two rows rather than inheriting the template's omission.

**Downstream implications.** Independence is a hard constraint, not a preference. The QMS mandates it in at least four places — test engineers cannot test what they wrote, design reviews require a participant without direct responsibility for the stage under review, software test reports need an executor plus an independent reviewer with independent code review at Class C, and reviewers may not be the author of the same record with signatures contemporaneous to the activity. **No executed V&V record yet exercises any of it** — the DHF holds stubs, not signed records — and the resourcing consequence — you cannot staff verification with only the people who built the thing — belongs in the programme plan now rather than at Gate 4.

**Open questions.** The QMS has **no standalone V&V Plan template and no V&V Summary Report schema**, despite both being required records and the summary reports being a pre-transfer gate condition. The planning obligation is partially covered — the Design & Development Plan and the Software Development Plan each carry a V&V section — but there is no schema for the summary reports the transfer gate depends on. These are the most load-bearing absent artifacts and this strategy should trigger their authoring.
<!-- Source: ben/115, "Verification and validation answer different questions and are evidenced differently", last modified 2026-08-06 -->
<!-- DECISION:end id=D-TEST-1.2 -->

<!-- DECISION:start id=D-TEST-1.3 status=active source=ben/115 created=2026-08-06 last-edited=2026-08-06 -->
### 1.3 Acceptance criteria are born in the requirements, not in the protocol

**Decision.** Every design input carries its **acceptance criterion, verification method, upstream user-need trace, and risk-control linkage at the point the requirement is written** — not deferred to whoever later writes the protocol. The verification method is drawn from the template's four-value set (test / inspection / analysis / demonstration), which the programme adopts as the controlled vocabulary. Two things need aligning to make that real: the parent procedure names only three of the four, and the PP3500 requirements currently use **15 distinct free-text method values**, only one of which overlaps the set.

**Why.** A criterion invented at protocol-writing time is a criterion authored by the person most motivated for it to pass. Worse, it silently changes what "verified" means relative to what the team agreed to build. Putting the criterion in the requirements document makes the acceptance bar a reviewed design decision rather than a testing convenience.

**What this commits us to.** This is the contract the programme is **closest to already satisfying**, and that is worth saying plainly: the PP3500 design inputs carry genuinely quantitative, standard-anchored criteria, including explicit sample sizes and gravimetric methods. Two specific breaks remain. First, **30 of the 34** design inputs hold a bare method *label* where they should hold a verification-activity *identifier* — only four carry one — so almost no requirement points at the protocol that discharges it. Second, the requirements document has **no risk-control linkage column**, even though the QMS template carries one: the column was dropped in the instance, not missing from the standard. That means the question "which verification proves this risk control is effective" cannot be answered from the requirements document, and risk-control effectiveness is exactly what a reviewer will probe on an infusion pump.

**Downstream implications.** Closing the second break is a prerequisite for the risk file's residual-risk argument, not merely a traceability nicety.

**Open questions.** The verification-identifier namespace is inconsistent across three forms in the QMS and the DHF. Pick one, publish the mapping, and migrate — this is cheap now and expensive after protocols exist.
<!-- Source: ben/115, "Acceptance criteria are born in the requirements, not in the protocol", last modified 2026-08-06 -->
<!-- DECISION:end id=D-TEST-1.3 -->

<!-- DECISION:start id=D-TEST-1.4 status=active source=ben/115 created=2026-08-06 last-edited=2026-08-06 -->
### 1.4 Trace is the spine, and the current gate rule is unsatisfiable

**Decision.** The design traceability matrix is maintained **continuously across the gates** — user needs to design inputs early, design outputs at the design gate, verification and validation at the V&V gate — and never reconstructed at the end. The mandated shape is five columns: user need → design input → **design output** → V&V → risk control, with Class B and C software additionally tracing each requirement to architecture elements and to unit, integration and system tests.

**Why.** The QMS states the operative rule bluntly: a V&V activity with no upstream trace is testing something nobody agreed to build. And the gate rule has teeth — **gate disposition shall not be Pass while any orphan check fails**, with *Conditional* available only when the orphans are identified, time-bounded and owned. That converts trace from documentation into a schedule dependency, which is the only framing under which it gets maintained.

**What this commits us to.** Three concrete gaps between the mandated shape and what exists, all verifiable today:

1. **There is no design-output layer in the trace matrix, and none is possible.** The configured layers are user needs, design inputs, software requirements, architecture, V&V and risk. The `DO` rung the QMS mandates is not merely unconfigured — it is **not expressible in the trace skill's schema**, which enumerates those six as the only valid layer keys. So the chain from requirement to the thing actually built is broken by construction, and closing it requires a change to the tooling, not just to a config file.
2. **The architecture layer produces no edges — for want of source data, not configuration.** The layer *is* configured against the software architecture document; that document simply contains no design-input references, so there is nothing for the adapter to bind and the layer reports its edges as unknown.
3. **Verification is barely connected to anything.** The V&V layer holds **3 nodes against 34 design inputs**, and **28 of 32 software requirements are orphaned**. Design inputs themselves are well-connected downstream (1 orphan of 34) — the break is not at the top of the chain, it is that almost nothing reaches verification.

**Downstream implications.** Since unit and integration test code is classified by the QMS as a **design output** rather than a V&V record, the missing `DO` layer also means test code currently has no home in the trace chain — and test code that is a design output must itself be verified.

**Open questions.** Whether to add the `DO` layer to the existing trace configuration or to treat design outputs as a per-DHF register that the matrix references. The first is cheaper; the second may model reality better for hardware.
<!-- Source: ben/115, "Trace is the spine, and the current gate rule is unsatisfiable", last modified 2026-08-06 -->
<!-- DECISION:end id=D-TEST-1.4 -->

<!-- DECISION:start id=D-TEST-1.5 status=active source=ben/115 created=2026-08-06 last-edited=2026-08-06 -->
### 1.5 What happens when a verification test fails — the QMS is silent, so this strategy says it

**Decision.** A failed verification or validation result is **dispositioned through a defined route before any retest**, and the disposition is a record. The route: classify the failure (test-setup or protocol defect / product defect / criterion defect), and route accordingly — protocol defects through the deviation procedure with quality approval, product defects into the design-change and corrective-action path, and criterion defects back to the requirement with a design review, never by adjusting the criterion inside the protocol. **Re-running a failed test without a recorded disposition is prohibited.**

**Why.** This is a genuine hole, and a specific one. The design verification and validation procedure is silent on failure; the corrective-action procedure's list of sources covers complaints, audits, supplier non-conformities, process monitoring, servicing, post-market surveillance and management review — **it does not name design verification or validation failure**; and the non-conforming product procedure is scoped to product, not to test results.

**The gap is narrower than "the QMS is silent", and stating it precisely is what makes it defensible.** Software V&V failure *is* routed — the software V&V work instruction sends defects into the software problem-resolution procedure. What has no defined destination is a failed **system-level or hardware** verification or validation: exactly the bench, electrical, alarm and delivery-accuracy campaigns that dominate a PCA pump's evidence base. Left unstated, the default behaviour under schedule pressure is universal and well documented across the industry: adjust the criterion until the test passes.

**What this commits us to.** The adjacent procedure that *does* exist — the deviation route for departing from an approved protocol mid-execution — is explicitly on the V&V critical path, requires independent quality approval, requires that pre-execution deviations be approved *before* the activity starts, names "forgot to file" and "faster to ask later" as unacceptable rationales, and escalates a deviation repeated three times within twelve months to corrective action. This strategy adopts it as the in-flight route. **But its form does not exist** — the procedure points at a document-change form as a placeholder. That gap sits directly on the V&V path and should be closed before protocol execution begins.

**Downstream implications.** This is the missing half of "acceptance criteria philosophy": a criterion is only meaningful if the consequence of missing it is defined in advance.

**Open questions.** Whether design V&V failure should be added as a named corrective-action source in the QMS, or handled entirely within design change control. The first is more conservative and more auditable.
<!-- Source: ben/115, "What happens when a verification test fails — the QMS is silent, so this strategy says it", last modified 2026-08-06 -->
<!-- DECISION:end id=D-TEST-1.5 -->

<!-- DECISION:start id=D-TEST-1.6 status=active source=ben/115 created=2026-08-06 last-edited=2026-08-06 -->
### 1.6 Software V&V scales by safety class — but not from the distillations currently in this repo

**Decision.** Software verification depth scales with IEC 62304 safety class across the portfolio, and the authoritative per-class requirement mapping is taken from **the standard's own normative summary table**, not from any secondary distillation held in this project.

**Why.** This is a live correctness hazard, not a hypothetical. **Three** distillations of this standard exist in the repo and they **disagree with each other** about whether system-level testing is required for Class A — two say it is, one says it is not — and the registry-side copy explicitly flags its own table as needing verification against the standard's normative table. Building the programme's class-scaling rules from any of them would bake a known-uncertain mapping into the document that decides how much testing the pump firmware receives.

**What this commits us to.** Obtaining the class mapping from the standard itself, and recording that provenance in the V&V plan so a reviewer can see the table was not derived from a paraphrase.

**Downstream implications.** The same caution applies more sharply to two other standards in this repo. The project-tier copies of the usability-engineering and health-software standards **carry invented clause numbering**, and — verified directly — the quarantine banner warning about it exists **only on the registry copy, not on the project copy an author would naturally open**. Any clause number cited from the project tier for those two standards is untrustworthy. Until the banners are propagated, cite the QMS's own verified clause mapping for usability, and do not cite sub-clause numbers for the health-software standard at all.

**Open questions.** Whether to fix this at the source by propagating the quarantine banners to the project tier. It is a small edit that removes a standing trap, and it protects every future author, not just this document.
<!-- Source: ben/115, "Software V&V scales by safety class — but not from the distillations currently in this repo", last modified 2026-08-06 -->
<!-- DECISION:end id=D-TEST-1.6 -->

<!-- DECISION:start id=D-TEST-1.7 status=active source=ben/115 created=2026-08-06 last-edited=2026-08-06 -->
### 1.7 Usability validation is validation, and its acceptance is safety, not satisfaction

**Decision.** Summative usability evaluation is part of **design validation**, executed on production-equivalent devices with representative users in the intended use environment, with acceptance keyed to **hazard-related use scenarios** — every such scenario completed safely by every participant, or residual risk demonstrated acceptable through analysis. Participant counts follow the QMS floor of at least 15 per distinct user group unless a documented rationale justifies fewer, and observed use errors are classified with root cause attributed to user-interface design, training, or the instructions for use.

**Why.** For a PCA pump this is the highest-consequence validation activity in the programme. FDA's current human-factors submission guidance names infusion pumps explicitly as a device type with known use-error history requiring human-factors validation data — this device class does not get to argue its way out of summative testing. And the acceptance basis matters: aggregate task-success rates can look excellent while the specific hazard-related scenario fails, which is the scenario that harms a patient.

**What this commits us to.** The programme is better positioned here than it may appear — the design inputs already carry participant counts consistent with the QMS floor, and the summative protocol schema exists as a QMS template with hazard-scenario acceptance and participant-rationale sections built in. **Unpopulated Rev 0.1 draft instances of both the summative protocol and the usability engineering file already exist in the DHF**; what is genuinely absent is the **use-related risk analysis**. So the work is to populate two stubs and author one missing document, not to start from nothing.

**Downstream implications.** Two sequencing consequences. The summative protocol cannot be populated until the use-related risk analysis identifies which scenarios are hazard-related — so the URRA is on the critical path to validation, not parallel to it. And distinct user groups for a PCA pump plausibly include the clinician who programs the pump, the nurse who responds to alarms, and the patient who presses the bolus button, whereas the two design inputs carrying participant counts currently name **one** group. That tension is a participant-count decision with real cost implications, and it should be made deliberately and early rather than discovered when the protocol is written.

**Open questions.** `[VERIFY]` The FDA *process* guidance on applying human factors engineering — as distinct from the current guidance on human-factors *content in submissions* — is **absent from every tier in this repo**. It is the document that governs how summative testing is actually run. Import it before authoring the protocol.
<!-- Source: ben/115, "Usability validation is validation, and its acceptance is safety, not satisfaction", last modified 2026-08-06 -->
<!-- DECISION:end id=D-TEST-1.7 -->

<!-- DECISION:start id=D-TEST-1.8 status=active source=ben/115 created=2026-08-06 last-edited=2026-08-06 -->
### 1.8 AI-enabled behaviour and PCCP changes are verified against a frozen baseline

**Decision.** For AI-enabled components and any change executed under the Predetermined Change Control Plan, performance evidence is generated against a **locked, version-controlled test set** that is not modified without a documented change-control decision, and every change must demonstrate non-inferiority against **two** baselines: the cleared version **and** the most recently modified version.

**Why.** The locked test set exists so performance is comparable across model versions; a test set that drifts with the model makes every comparison meaningless while looking rigorous. The dual baseline exists to stop cumulative drift: a sequence of changes each non-inferior to the *cleared* version can still ratchet performance steadily downward relative to what is actually in the field. For a device where the algorithm influences dose delivery, that ratchet is a patient-safety mechanism, not a metrics concern.

**What this commits us to.** Dataset governance as a design-control activity — partitioning with a frozen test partition, versioning, per-model archival, a documented representativeness position with its limitations stated honestly, and a pre-specified subgroup analysis plan. Selecting a decision threshold by sweeping it on the test set and choosing the best point is **test-set contamination** and should be treated as a defect, not a tuning step.

**Downstream implications.** Where a review or confirmation step is credited as a risk control, verifying it requires treating it as a **classifier** — measuring whether it fires on the right cases, with a confidence bound, rather than counting how often it fired. A tally tells you the gate is active; it never tells you the gate is correct. This applies directly to any PP3500 dose-limit, occlusion or alarm gate.

**Open questions.** Which PP3500 behaviours are genuinely AI-enabled versus rule-based, and therefore which fall under this decision at all. The manifest carries an AI-enabled flag per DHF; the strategy should state the resulting scope explicitly rather than leaving it to be inferred.
<!-- Source: ben/115, "AI-enabled behaviour and PCCP changes are verified against a frozen baseline", last modified 2026-08-06 -->
<!-- DECISION:end id=D-TEST-1.8 -->

<!-- DECISION:start id=D-TEST-1.9 status=active source=ben/115 created=2026-08-06 last-edited=2026-08-06 -->
### 1.9 The standards floor for an infusion pump is not yet in this repository

**Decision.** Before bench and safety verification protocols are authored, the programme imports and distils the device-specific standards and guidance that govern them, and treats their current absence as a **blocking gap** rather than a documentation backlog.

**Why.** The electrical, alarm and infusion-pump-specific standards are present and genuinely project-specific — that tier works. The gaps are at the two ends that matter most for this device. The FDA guidance covering infusion pumps across the total product lifecycle — the document a reviewer would expect a pump submission to be built against — is **absent from every tier**, appearing only as a mention inside another file. The AAMI technical report covering patient-controlled analgesia mode specifically is FDA-recognised and **distilled nowhere**.

**What this commits us to.** A concrete blocker with a name: the electromagnetic-compatibility acceptance criterion is currently "essential performance maintained", while the record that formally defines essential performance for this device is marked to-be-determined, and no QMS procedure covers essential performance at all. **The EMC test plan cannot be written until essential performance is defined.** That is a sequencing fact the programme plan should carry, not a detail for the test engineer to discover.

**Downstream implications.** The project-side guidance tier is currently functioning as a duplicate distillation set rather than an applicability set — none of its content files carries device-specific applicability commentary, and **11 of 12 lack the finding-aid banner** that marks the registry distillations as paraphrase-not-source. They do cite their source documents, so the defect is not missing provenance; it is that nothing on the page warns a reader that the text is a summary. Verification protocols grounded on that tier inherit the problem.

**Open questions.** Whether the QMS-level quality-system standard is genuinely out of project scope. It is currently recorded as evaluated-and-not-required on the grounds that it is owned at the organisation level, but the project's own regulatory anchor makes its design-controls clause the reference for this programme — those two positions are inconsistent and one of them should move.
<!-- Source: ben/115, "The standards floor for an infusion pump is not yet in this repository", last modified 2026-08-06 -->
<!-- DECISION:end id=D-TEST-1.9 -->

<!-- DECISION:start id=D-TEST-1.10 status=active source=ben/110 created=2026-07-28 last-edited=2026-07-28 -->
### 1.10 Workbench Validation Evidence — Reviewer Readability and Run Reproducibility

**Round-2 refinements decided with user (2026-07-28):**
1. **UUT (unit under test)** — `test_cases[].uut:` names the component(s) a case actually runs against (multiple allowed; `all-skills` sentinel); the runner pins each named skill to the version exercised (`uut_versions` from the run-start baseline) — stamped into results, evidence-log headers, report, sidecar, console column.
2. **Reviewer-friendly test cases** — titles/description/approach rewritten in plain language for non-specialists; console test rows click-to-expand (description, approach, pass rule, command, links); report gains "What each test case checks (for reviewers)".
3. **TC hyperlinks** — TC ids link to the actual test source (derived from cmd; env-flag args like `--project` excluded — that mistake initially pinned the console's whole `.venv`); `.claude/skills` added to console.yaml `grounding.extra_roots` so sources resolve in Documents.
4. **Validation setup record** — every run records configuration under test + operator (git user/email, OS user, hostname, OS) + invocation source (`--invoked-via cli|console`; console endpoint passes `console`) + timestamps. Report §1 is now the setup record; console shows a setup-record line.
5. **Test-artifact pinning** — the run folder receives byte copies of `validation.yml` and each case's test source (`pinned/<TC-ID>/`, `__pycache__` excluded), sha256-manifested in the run JSON — so the exact tests executed stay reviewable across validation runs as skills evolve.
<!-- Source: ben/110, "Workbench Validation Evidence — Reviewer Readability and Run Reproducibility", last modified 2026-07-28 -->
<!-- DECISION:end id=D-TEST-1.10 -->

## Open Items

_Unresolved [VERIFY] markers and items needing human decision._

- **[VERIFY]** (D-TEST-1.1 — [ben/115](../../../tasks/ben/115-tooling-and-testing-validation-strategy.md), "This strategy sequences and tailors an existing QMS; it does not invent a V&V philosophy", *Open questions*) The QMS publishes **five numbered phase gates** in one document and **six named design-review points** in another, with no published mapping between them, and one of the two contradicts itself in its own front matter. The V&V cadence hangs off that model, so the strategy must author the mapping before the gate schedule means anything. `[VERIFY]` against both governing documents before fixing the mapping.
- **[VERIFY]** (D-TEST-1.7 — [ben/115](../../../tasks/ben/115-tooling-and-testing-validation-strategy.md), "Usability validation is validation, and its acceptance is safety, not satisfaction", *Open questions*) The FDA *process* guidance on applying human factors engineering — as distinct from the current guidance on human-factors *content in submissions* — is **absent from every tier in this repo**. It is the document that governs how summative testing is actually run. Import it before authoring the protocol.
- **Assembly gap**: four blocks in `tasks/ben/054-agentic-first-medtech-strategy.md` open with `<!-- STRATEGY CONTENT: testing, architecture` but are **malformed** — the tag comment is never closed on its own line, so each block body sits *inside* an unterminated HTML comment and the assembler's block-boundary rule (tag → next `## ` heading) would swallow ~320 lines of unrelated content. They were therefore excluded from this assembly. Repair the tags in the source task (self-close each tag as `... -->` and un-comment the body) and re-run `/strategy assemble testing` to bring that content in.

## Assembly History


### 2026-08-06 — post-assembly correction pass (ben/115)
- An independent verification pass re-checked every quantitative and factual claim in the ben/115-sourced decisions against the repository, briefed to falsify rather than confirm.
- **15 corrections applied** to decision bodies in this document, mirrored into the source blocks in [ben/115](../../../tasks/ben/115-tooling-and-testing-validation-strategy.md) so the next assembly reproduces them.
- No decision was added, removed, or re-identified; no heading changed. Corrections were confined to claim wording and figures.
- Notable: the orphan figures were corrected — the V&V layer holds **3 nodes against 34 design inputs** and 28 of 32 software requirements are orphaned (a previously stated "30 orphaned design inputs" came from a superseded artifact); the four tailoring factors are a **template fill-in prompt, not a procedural authorisation**, and that absence is now stated as a finding; failed-test routing exists for **software** V&V (the gap is system-level and hardware); and Rev 0.1 stub instances of the summative protocol and usability engineering file **do exist** — only the use-related risk analysis is absent.

_Append-only log of changes across assemblies. Most recent first._

### 2026-08-06 — assembled by benxavier-gl
- **Initial assembly** from ben/115, ben/110 (target was an `awaiting-content` stub; replaced in full)
- **Added**: This strategy sequences and tailors an existing QMS; it does not invent a V&V philosophy, Verification and validation answer different questions and are evidenced differently, Acceptance criteria are born in the requirements, not in the protocol, Trace is the spine, and the current gate rule is unsatisfiable, What happens when a verification test fails — the QMS is silent, so this strategy says it, Software V&V scales by safety class — but not from the distillations currently in this repo, Usability validation is validation, and its acceptance is safety, not satisfaction, AI-enabled behaviour and PCCP changes are verified against a frozen baseline, The standards floor for an infusion pump is not yet in this repository (all ben/115)
- **Added**: Workbench Validation Evidence — Reviewer Readability and Run Reproducibility (ben/110)
- **Heading substituted**: the ben/110 block carries no `### ` subsection heading — its content sits as a numbered list under the task-scaffolding heading `## Phase 0 — Research Findings`, which is not a decision title. The assembler derived the heading "Workbench Validation Evidence — Reviewer Readability and Run Reproducibility" from the block's own content (UUT pinning, reviewer-friendly test cases, TC hyperlinks, validation setup record, test-artifact pinning). No content was altered.
- **Conflicts**: none. The two source blocks are complementary, not overlapping — ben/115 decides device V&V for the PP3500 programme; ben/110 decides evidence mechanics for validating the agentic workbench. No heading overlap and no shared strategic decision.
- **Excluded (malformed tags)**: 4 candidate `testing` blocks in ben/054 — unterminated tag comments; see Open Items.
- 10 subsections, 2 [VERIFY] markers

## Source Traceability

| Output Section | Source Task | Source Subsection | Last Modified |
|---------------|-----------|-------------------|---------------|
| Strategy Decisions (D-TEST-1.1) | [ben/115](../../../tasks/ben/115-tooling-and-testing-validation-strategy.md) | This strategy sequences and tailors an existing QMS; it does not invent a V&V philosophy | 2026-08-06 |
| Strategy Decisions (D-TEST-1.2) | [ben/115](../../../tasks/ben/115-tooling-and-testing-validation-strategy.md) | Verification and validation answer different questions and are evidenced differently | 2026-08-06 |
| Strategy Decisions (D-TEST-1.3) | [ben/115](../../../tasks/ben/115-tooling-and-testing-validation-strategy.md) | Acceptance criteria are born in the requirements, not in the protocol | 2026-08-06 |
| Strategy Decisions (D-TEST-1.4) | [ben/115](../../../tasks/ben/115-tooling-and-testing-validation-strategy.md) | Trace is the spine, and the current gate rule is unsatisfiable | 2026-08-06 |
| Strategy Decisions (D-TEST-1.5) | [ben/115](../../../tasks/ben/115-tooling-and-testing-validation-strategy.md) | What happens when a verification test fails — the QMS is silent, so this strategy says it | 2026-08-06 |
| Strategy Decisions (D-TEST-1.6) | [ben/115](../../../tasks/ben/115-tooling-and-testing-validation-strategy.md) | Software V&V scales by safety class — but not from the distillations currently in this repo | 2026-08-06 |
| Strategy Decisions (D-TEST-1.7) | [ben/115](../../../tasks/ben/115-tooling-and-testing-validation-strategy.md) | Usability validation is validation, and its acceptance is safety, not satisfaction | 2026-08-06 |
| Strategy Decisions (D-TEST-1.8) | [ben/115](../../../tasks/ben/115-tooling-and-testing-validation-strategy.md) | AI-enabled behaviour and PCCP changes are verified against a frozen baseline | 2026-08-06 |
| Strategy Decisions (D-TEST-1.9) | [ben/115](../../../tasks/ben/115-tooling-and-testing-validation-strategy.md) | The standards floor for an infusion pump is not yet in this repository | 2026-08-06 |
| Strategy Decisions (D-TEST-1.10) | [ben/110](../../../tasks/ben/110-workbench-validation.md) | Workbench Validation Evidence — Reviewer Readability and Run Reproducibility | 2026-07-28 |
