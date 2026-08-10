# Operations & Tooling Strategy

<!-- Assembled: 2026-08-06 by /strategy assemble -->
<!-- Domain: operations -->
<!-- Sources: ben/002, ben/007, ben/057, ben/059, ben/060, ben/061, ben/062, ben/104, ben/108, ben/109, ben/111, ben/112, ben/115 -->

> This document is auto-assembled from `<!-- STRATEGY CONTENT: operations, ... -->` tags in task documents.
> Do not edit directly — update the source task and run `/strategy assemble operations`.
> Unresolved items are marked with [VERIFY].

## Scope & Approach

This shared **Operations & Tooling** strategy covers the operational surface of the PainEase PP3500 program: build/release pipeline, SBOM/SOUP supply chain, cloud infrastructure, QMS operational posture, project management, tooling & agentic infrastructure, and team workflow & onboarding (per `project.yml strategy_domains[]`, key `operations`, display name "Operations & Tooling"). It is a **shared** domain — one document spanning every DHF, not a per-DHF instance.

**Coverage at this assembly is uneven, deliberately.** The agentic-toolchain half is authored in depth (D-OPS-1.1 – D-OPS-1.9). The classic operational facets — build/release pipeline, SBOM/SOUP supply chain, cloud infrastructure, QMS operational readiness, and the project-management plan — are **not yet authored**; they are listed in [Open Items](#open-items) so the gap stays visible rather than implied-complete, which is exactly the commitment D-OPS-1.9 makes. The remaining decisions (D-OPS-1.10 – D-OPS-1.21) are accumulated repo-governance, registry-governance, cost-model, advisor-roster and skill-topology decisions harvested from task work spanning 2026-04-13 through 2026-08-06.

This is the domain's **initial assembly** — no prior version of this document existed.

## Plans Informed

| Formal Plan | DHF | How This Strategy Informs It |
|------------|---------|------------------------------|
| CI/CD & release pipeline | program-wide | Build, release, signing. **Not yet authored.** D-OPS-1.5 sets the bar every CI gate must meet (executes, fails closed, leaves a record) and records that CI currently carries zero quality gates. |
| SBOM/SOUP supply chain | program-wide | Supply-chain posture. **Not yet authored** — see Open Items. |
| Cloud infrastructure | program-wide | Hosting, facility equivalent. **Not yet authored** — see Open Items. |
| QMS operational posture | program-wide | Design-controls readiness. D-OPS-1.1 commits the workbench to a documented software-used-in-the-quality-system determination; D-OPS-1.3 aligns AI-assisted review with the QMS author≠reviewer independence conditions; D-OPS-1.4 bounds what the workbench may produce. |
| PM plan | program-wide | Ways of working. D-OPS-1.8 scopes ways-of-working claims to the single-operator evidence that exists; D-OPS-1.14 sets the teaching-project repo access posture; D-OPS-1.16 fixes the git workflow as project-authored. |
| Tooling & agentic-infra roadmap | program-wide | Agentic infrastructure and automation — the core of this document. D-OPS-1.1 – D-OPS-1.8 (workbench qualification, assurance, enforcement, measurement), plus registry/repo governance and skill topology in D-OPS-1.16 – D-OPS-1.21. |
| Team onboarding | program-wide | Knowledge transfer. D-OPS-1.7 (lessons staged but never promoted), D-OPS-1.8 (tacit knowledge concentrated in one operator), D-OPS-1.15 (`how-to-guide.md` / `setup.md` split as peer entry points). |

_The DHF column identifies which DHF each formal plan lives under — formal outputs remain per-DHF under `docs/project/dhfs/<dhf>/...` even though the upstream strategy is shared. Every plan in this domain is program-wide rather than DHF-scoped._

## Strategy Decisions

_Each decision is wrapped in `D-OPS-*` sentinels for stable addressing by the project console and downstream tooling. Ordered newest-first by source-task last-modified date; ties broken by higher task ID._

<!-- DECISION:start id=D-OPS-1.1 status=active source=ben/115 created=2026-08-06 last-edited=2026-08-06 -->
### 1.1 The workbench is software used in the quality system, and that is the question to answer

**Decision.** The project treats its agentic workbench — the skills, agents, rules, hooks and console under `.claude/` and `tools/` — as **software used in the quality system**, and commits to reaching and maintaining a documented *determination* about its qualification rather than leaving the question open. The workbench is not device software and never becomes part of the released product; it is the instrument that authors, checks and assembles the Design History File.

**Why.** Once an AI-assisted toolchain writes into design-control records, an auditor's question is not "is the tool clever" but "what assurance do you have that the records it produced are trustworthy, and where is the evidence." A program that never frames that question ends up answering it improvisationally under audit. The project already carries the scope flag `tool_validation: true` in `project.yml`, so the obligation is declared; what has been missing is the determination that discharges it.

**What this commits us to.** A standing, dated determination covering: what the workbench is, what it is permitted to produce, what assurance activity backs each use, and what triggers re-examination. The determination is a living record — it is invalidated by change, not by time alone.

**Downstream implications.** The determination is the parent of the tool-validation evidence produced by `workbench-validation`, and it is the document a Q-Sub or inspection response would cite. It also bounds the Testing & Validation strategy: test tooling that produces V&V evidence inherits this posture rather than defining its own.

**Open questions.** `[VERIFY]` The governing external references for this determination — FDA's Computer Software Assurance guidance, ISO 13485 §4.1.6, and the QMSR design-controls anchor — are **not yet distilled into `docs/external/`**. FDA CSA exists in this repo only as undistilled raw source under the registry's `references/fda-guidance/source-md/`, with no project applicability file. The determination must not be finalised on paraphrase; import the guidance first.
<!-- Source: ben/115, "The workbench is software used in the quality system, and that is the question to answer", last modified 2026-08-06 -->
<!-- DECISION:end id=D-OPS-1.1 -->

<!-- DECISION:start id=D-OPS-1.2 status=active source=ben/115 created=2026-08-06 last-edited=2026-08-06 -->
### 1.2 Assurance is risk-based and evidence-led, not classical qualification theatre

**Decision.** Workbench assurance is **risk-tiered**: depth of evidence scales with what a given use could damage if it went wrong undetected. The project does not attempt classical installation/operational/performance qualification against the language model itself, and it does not pretend the model is deterministic. It qualifies the **workbench around** the model — the gates, the deterministic checkers, the record structure, and the human review — and treats model behaviour as something to be *bounded and observed*, never as something to be pinned by a passing test.

**Why.** A language model produces different output for identical input. A test suite that asserts specific model prose would either be rewritten until it passed — which is not evidence — or fail continuously and be ignored, which is worse. The honest structure is the one `workbench-validation` already implements: a need is either backed by **deterministic executable evidence**, or it is declared a **process control** backed by human review and an audit trail, and reported as such. What must never happen is a process control being reported as a scripted PASS.

**What this commits us to.** Every workbench user need carries an explicit coverage class, and the report distinguishes them. The scariest failure mode here is not a red verdict; it is a green one that was never earned. The existing register already does this correctly — of 15 needs, 4 are declared `process-control` and 1 `exploratory`, and the report refuses to score them as tests. That property is load-bearing and must survive any future pressure to make the dashboard look better.

**Downstream implications.** It follows that **coverage is a first-class metric**: 13 of 39 skills currently ship a regression suite and 14 have direct validation coverage. The strategy's target is not 100% — it is that every skill which *writes into a controlled record* is covered, and that the uncovered remainder is a stated, reviewed list rather than an accident.

**Open questions.** `[VERIFY]` Whether to adopt a formal software-categorisation scheme (e.g. GAMP-style categories separating the vendor CLI from project-authored agents and skills) as the routing mechanism for assurance depth. The sister project `arthrex-pccp` does exactly this, and a category-based route is legible to a QA auditor who already knows the scheme — but no copy of the framework exists in this repo, so adopting it means importing it first.
<!-- Source: ben/115, "Assurance is risk-based and evidence-led, not classical qualification theatre", last modified 2026-08-06 -->
<!-- DECISION:end id=D-OPS-1.2 -->

<!-- DECISION:start id=D-OPS-1.3 status=active source=ben/115 created=2026-08-06 last-edited=2026-08-06 -->
### 1.3 Human review is the control that carries the argument — and only if it is real

**Decision.** The compensating control that makes AI-assisted authoring defensible is **human review before a record becomes controlled**, and the project commits to the conditions that make that review a control rather than a signature. Specifically: the reviewer is named and competent for the content; the reviewer is **not** the author of the same record; the review attests to independent verification of correctness, not merely that text was read; the *diff* under review is retained as evidence; and release is blocked when any of those is missing.

**Why.** "A human reviewed it" is the entire load-bearing claim of an AI-assisted quality system, and it is also the easiest claim to hollow out. A review that is a rubber stamp is indistinguishable, in the record, from a review that caught nothing because there was nothing to catch — unless the conditions above are specified and evidenced. This project's own QMS already demands author≠reviewer independence in four separate places, including the requirement that signature dates be contemporaneous with the activity; the AI-assisted path must meet the same bar, not a lesser one designed around the tooling.

**What this commits us to.** The `ai-changelog` convention (recording *that* an edit was AI-assisted, vendor-neutrally, as non-published metadata) is necessary but **not sufficient** — it records provenance, not review. The gap the strategy must close is the attestation and the retained diff. Until that exists, the honest statement of posture is "AI-assisted authoring with human review as a process discipline", not "with human review as an enforced control".

**Downstream implications.** This is where the tooling strategy and the QMS meet: the review conditions above are the same independence conditions the design-control procedures already impose on verification records. Aligning them means one rule, not two.

**Open questions.** `[VERIFY]` A widely-cited enforcement precedent for AI-authored quality records exists in the sister project's operations strategy (a warning letter concerning AI-generated specifications and production records without adequate human review). It is **not** in this project's `docs/external/` and has not been verified against the byte-correct source here. It is a strong anchor if it verifies; it must not be cited until it does.
<!-- Source: ben/115, "Human review is the control that carries the argument — and only if it is real", last modified 2026-08-06 -->
<!-- DECISION:end id=D-OPS-1.3 -->

<!-- DECISION:start id=D-OPS-1.4 status=active source=ben/115 created=2026-08-06 last-edited=2026-08-06 -->
### 1.4 What the workbench may and may not produce

**Decision.** The workbench is permitted to **draft, restructure, summarise, cross-check, and assemble** — and is prohibited from **attesting**. Concretely, it may draft controlled documents for human review, restructure existing approved content, generate trace and coverage projections, surface gaps and inconsistencies, and assemble submission packages from reviewed parts. It may **not**: declare a document compliant; author verification or validation evidence (test results, or a protocol signed off as executed); decide which regulations or standards apply; or emit a citation that no human will verify against its source.

**Why.** Each prohibition is the same principle in a different costume: the workbench may do work whose correctness a human can check, and may not perform the act of *certifying* correctness. Drafting is checkable. Attesting is not — an attestation is a claim about the world that the tool has no standing to make. The citation clause is the sharpest of the four in practice: a plausible, well-formatted, non-existent clause number is the highest-frequency and lowest-visibility failure this toolchain produces.

**What this commits us to.** An independent reference audit over citation-bearing controlled documents, run as a separate pass rather than as self-review — because self-review does not re-derive a citation from its source. The project already has this control (`/reference-audit` plus a `citations` verification engine and three source-class researchers) and the authoring rule already mandates it for citation-bearing edits; the commitment here is that it is actually run before a document is declared done.

**Downstream implications.** "May not author verification evidence" is the clause that most constrains the Testing & Validation strategy: drafting a *protocol* is permitted; producing a *result* is not.

**Open questions.** Whether "restructuring approved content" needs a tighter boundary — restructuring can change meaning, and the line between reformatting and rewriting is not self-evident.
<!-- Source: ben/115, "What the workbench may and may not produce", last modified 2026-08-06 -->
<!-- DECISION:end id=D-OPS-1.4 -->

<!-- DECISION:start id=D-OPS-1.5 status=active source=ben/115 created=2026-08-06 last-edited=2026-08-06 -->
### 1.5 A control that does not execute is not a control

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
<!-- Source: ben/115, "A control that does not execute is not a control", last modified 2026-08-06 -->
<!-- DECISION:end id=D-OPS-1.5 -->

<!-- DECISION:start id=D-OPS-1.6 status=active source=ben/115 created=2026-08-06 last-edited=2026-08-06 -->
### 1.6 Measurement stays honest about what is measured and what is modelled

**Decision.** The program measures agentic cost directly and models human-effort savings, and the two are **never** blended into a single headline number. Measured quantities (tokens, spend, sessions, user turns) are reported as measured; the effort-saved comparison is reported as **modelled and uncalibrated**, with its conservative bound leading.

**Why.** The measured side is real — at the time of writing, 28 sessions, 6.49 M output tokens and $2,124.29 over 22 active days, and already moving as sessions land (a figure quoted from this dataset should carry the date it was read). The modelled side carries a self-reported ~88% mean deviation between independent estimators on a blind re-estimate of the same tasks. Presenting a savings multiple derived from the second as though it had the precision of the first is the fastest way to lose a finance or quality audience permanently — and this program has already done the honest work of measuring that deviation, which most have not.

**What this commits us to.** The uncalibrated label travels with the number wherever it is rendered — task doc, dashboard, console, and any external retelling. A derived figure that reaches a slide without its provenance is a defect, not a rounding.

**Downstream implications.** The load-bearing weakness is coverage, not accuracy: telemetry exists for **1 of 5** roster members, so every per-team claim is really a per-person claim wearing a team label. A second, milder one is that the dataset is regenerated continuously by scheduled aggregation, so any figure lifted into a slide is a snapshot — it needs its as-of date attached or it silently ages.

**Open questions.** Whether to calibrate the effort model against even a small set of genuinely hand-executed tasks. Without that, the ratio stays order-of-magnitude forever.
<!-- Source: ben/115, "Measurement stays honest about what is measured and what is modelled", last modified 2026-08-06 -->
<!-- DECISION:end id=D-OPS-1.6 -->

<!-- DECISION:start id=D-OPS-1.7 status=active source=ben/115 created=2026-08-06 last-edited=2026-08-06 -->
### 1.7 The knowledge loop stages but does not promote

**Decision.** Captured lessons must reach a **permanent home** — a skill, a rule, an agent prompt, project instructions, a glossary entry, or a folder README — or they are not knowledge management, they are an append-only log with a growing session-start cost.

**Why.** The ledger currently holds **76 staged entries, 0 promoted, 0 archived**. Every one of those loads into every session. The pipeline was designed with three stages and has only ever used the first, so the mechanism intended to make the project cheaper to work in has become a fixed tax that grows monotonically. This is a clean example of a capture habit succeeding while the promotion habit never started.

**What this commits us to.** A promotion pass with a real cadence, and an explicit archival path for lessons that were true once and are not anymore. Promotion is the step that changes future behaviour; staging only records that someone noticed.

**Downstream implications.** The same shape appears elsewhere in the workbench and is worth naming as a general property: **capture is cheap and self-reinforcing; consolidation is expensive and has no natural trigger.** Anything in this toolchain that accumulates — lessons, staged decisions, unassembled strategy blocks, task docs — needs a scheduled consolidation step or it will grow until it is unusable.

**Open questions.** Who owns the promotion pass, and at what cadence. Unowned, it will not happen — the evidence for that is the ledger itself.
<!-- Source: ben/115, "The knowledge loop stages but does not promote", last modified 2026-08-06 -->
<!-- DECISION:end id=D-OPS-1.7 -->

<!-- DECISION:start id=D-OPS-1.8 status=active source=ben/115 created=2026-08-06 last-edited=2026-08-06 -->
### 1.8 The evidence base is one operator, and the strategy should not pretend otherwise

**Decision.** Claims about team workflow, onboarding and ways of working are scoped to what the evidence supports: **114 of 115** task documents belong to one person, telemetry exists for **1 of 5** roster members, and every validation run, registry push and security record was produced by the same operator.

**Why.** A tooling strategy that describes a team practice which only one person has exercised is describing an intention. The onboarding material, the task-first workflow and the rules are genuinely designed for a team, and they may well work for one — but that is a hypothesis, and the honest framing distinguishes a designed practice from a demonstrated one.

**What this commits us to.** Treating multi-operator use as the **next real test of the workbench**, not as a solved property. The most informative signal available would be a second operator completing a full task cycle — activate, author, review, validate, push — and reporting where the workflow assumed context they did not have.

**Downstream implications.** Concentration is also a continuity risk: the knowledge required to operate the toolchain is currently mostly undocumented tacit knowledge held by one person, which is precisely the failure mode the lessons-promotion gap above prevents fixing.

**Open questions.** Whether the four other roster members are blocked by tooling friction, by access, or simply by not having had work routed to them — these have very different fixes and the current data cannot distinguish them.
<!-- Source: ben/115, "The evidence base is one operator, and the strategy should not pretend otherwise", last modified 2026-08-06 -->
<!-- DECISION:end id=D-OPS-1.8 -->

<!-- DECISION:start id=D-OPS-1.9 status=active source=ben/115 created=2026-08-06 last-edited=2026-08-06 -->
### 1.9 Tooling strategy lands in the `operations` domain, not a new `tooling` domain

**Decision.** The tooling strategy is authored into the existing **`operations`** strategy domain rather than a new `tooling` domain. `operations` is already registered in `project.yml strategy_domains[]` under the display name **"Operations & Tooling"**, and its `scope_description` already names *"tooling & agentic infrastructure"*, with `what_belongs_here[]` explicitly listing *"Tooling and agentic infrastructure decisions"*, *"Skill and automation roadmap"*, and *"Team workflow, onboarding, and knowledge management"*.

**Why.** Creating a `tooling` domain would fork a domain that already claims the scope. The project's `audit-wiring-before-adding-fields` rule exists for exactly this: the wiring layer already encodes the fact, so the feature routes through a lookup against existing config rather than a new entry. A second domain would also split one story across two documents — the build/release pipeline, the supply-chain posture and the agentic toolchain are the same operational surface, and the decisions in one constrain the others.

**What this commits us to.** The `operations` document carries both the classic operational content (build/release, SBOM/SOUP, cloud posture, QMS operational readiness, PM approach) and the agentic-toolchain content. This task authors the **tooling half**; the remaining operational facets stay open and are called out as such in the document's Open Items so the gap is visible rather than implied-complete.

**Downstream implications.** A future session that wants a standalone tooling domain should use `/strategy domains add`, migrate the tagged blocks, and accept that `operations` loses half its scope — it is a reversible decision, deliberately taken the cheap way first.

**Open questions.** If the agentic-toolchain content grows past roughly half the `operations` document, revisit the split. The strategy skill's own guidance on incubating subtopics (`clinical` inside `regulatory`, `cybersecurity` inside `architecture`) is the precedent: start as a topic within a parent domain, promote when it outgrows it.
<!-- Source: ben/115, "Tooling strategy lands in the `operations` domain, not a new `tooling` domain", last modified 2026-08-06 -->
<!-- DECISION:end id=D-OPS-1.9 -->

<!-- DECISION:start id=D-OPS-1.10 status=active source=ben/112 created=2026-08-06 last-edited=2026-08-06 -->
### 1.10 Why this metric — user turns as a measured human-effort signal

**Why this metric.** The program already measures the agentic side automatically (tokens, cost, wall-clock) but the human side only through hand-written `agentic_hours` estimates in each task's `## Economics` block. Those are self-reported and uncalibrated — task ben/098 red-teamed them and landed on "modeled, uncalibrated." User turns are a **measured** human-effort signal sitting unused in transcripts already on disk, so they cost nothing to acquire and are not subject to estimation bias.

**Decision — the existing `messages` counter cannot be reused, and the gap is not a constant.** `collect.py` increments `messages` only on rows carrying `message.usage`, which user messages never have. So `messages` counts *assistant API responses* — every tool call, every subagent reply, every intermediate step. Measured inflation over three real transcripts:

| session | assistant msgs | real user turns | tool results | inflation |
|---|---:|---:|---:|---:|
| `c05c62a3` | 118 | 12 | 166 | 9.8× |
| `62ff8841` | 17 | 7 | 20 | 2.4× |
| `ccbcd1a9` | 72 | 13 | 67 | 5.5× |

The ratio swings with how tool-heavy the work is, so turns **cannot** be derived by scaling `messages` — a separate counter is required. This is the finding that motivates the task.

**Decision — turns bucket by day and task, never by model.** The existing per-session buckets (`by_model`, `by_day`, `by_task`) all share the `_zero()` shape. Adding `user_turns` to that shared shape would emit the field inside `by_model`, where it is meaningless: a user turn is not attributable to a model (the human types before any model is selected, and one turn can span several models via subagents). Rather than publish an always-zero or arbitrarily-attributed field, turns live in their own top-level `user_turns` block with `total` / `by_day` / `by_task`. Cost of the choice: one more branch in the aggregator. Benefit: no field that looks like data but is not.

**Decision — main transcript only, never subagent transcripts.** Subagent transcripts contain `role: user` rows, but those are the harness feeding the subagent its prompt — not a human typing. Counting them would inflate turns by exactly the amount of delegation a task used, which is the opposite of what the metric is for. Turn detection therefore reads only the session's main transcript, while token collection continues to walk subagents recursively.

**Detection rule.** A row counts as a user turn when it is `type: "user"` (or `message.role == "user"`) **and** its content is either a plain string, or a block list containing a `text` block and **no** `tool_result` block. The `tool_result` exclusion is load-bearing: the harness returns every tool result as a `user`-role message, and those outnumber real turns roughly 5–13× in the sampled sessions.
<!-- Source: ben/112, "Strategy" (heading substituted — see History), last modified 2026-08-06 -->
<!-- DECISION:end id=D-OPS-1.10 -->

<!-- DECISION:start id=D-OPS-1.11 status=active source=ben/111 created=2026-08-06 last-edited=2026-08-06 -->
### 1.11 Standard list prices, not introductory rates

**Decision — standard list prices, not introductory rates.** Claude Sonnet 5 currently carries an introductory rate of $2.00/$10.00 per MTok through 2026-08-31, versus its standard $3.00/$15.00. The user directed we use **standard** rates. Rationale: the rate card is an indicative API-equivalent valuation of subscription usage, not an invoice — pinning it to a promotional rate that expires in 26 days would bake in a scheduled inaccuracy and a maintenance trigger nobody owns. Standard rates are the stable, defensible basis and are conservative (they overstate rather than understate).

**Finding — this refresh moves no dollar figure, and that is worth stating plainly.** The rate card as retrieved 2026-06-22 already prices every model present in the collected data at correct standard rates (`claude-fable-5` $10/$50, `claude-opus-4-8` $5/$25, `claude-sonnet-4-6` $3/$15, `claude-haiku-4-5-20251001` $1/$5), with correct cache multipliers (write 1.25× at 5m, 2× at 1h; read 0.1× of input). The only gap was that Opus 5 and Sonnet 5 post-date the card. Because `_rates_for()` falls back to the first `families` key that is a **substring** of the model id, `claude-opus-5` already resolved to the `opus` family and `claude-sonnet-5` to `sonnet` — the same numbers the explicit entries carry. So the edit is correctness and legibility, not a repricing.

**Why add the explicit entries anyway.** Depending on substring fallback for the two current-generation flagships is fragile in a way that fails silently: the fallback resolves against whichever family key matches first, and a future model id whose name does not contain its family token (or contains another family's token) would price wrong with no error and no log line. Explicit entries make the flagships' rates auditable at a glance and remove the dependency on iteration order over the `families` dict.

**Architecture note — pricing is applied at aggregate time, never at collect time.** Per-session records under `tasks/*/_usage-metrics/**` carry token counts only (`input`, `output`, `cache_read`, `cache_write_5m`, `cache_write_1h`) and no cost field. Every dollar figure in `usage.json` — per member, per month, per task, `daily_cost`, `value_summary` — is derived by `aggregate.py` from those tokens × `pricing.json`. This makes the rate card fully retroactive: changing it and re-aggregating re-prices all history, and the GitHub Action triggers on pushes touching `tools/usage-metrics/pricing.json`. No historical figure is ever frozen at a stale rate.

**Known divergence (not in scope).** `statusline.sh` sources its cost from Claude Code's own `.cost.total_cost_usd` on stdin, not from `pricing.json`. The status line and the dashboard are independent cost paths and can legitimately disagree; this task does not attempt to reconcile them.
<!-- Source: ben/111, "Strategy" (heading substituted — see History), last modified 2026-08-05 -->
<!-- DECISION:end id=D-OPS-1.11 -->

<!-- DECISION:start id=D-OPS-1.12 status=active source=ben/108 created=2026-08-06 last-edited=2026-08-06 -->
### 1.12 Commercial analytics layer — `corpus` grounding engine + `commercial` analysis skill

**Decision (2026-07-22, ben/108): Commercial analytics layer = `corpus` grounding engine + `commercial` analysis skill + versioned snapshot corpus + verification stack.**

- **Two skills, not one**: `corpus` (cross-cutting grounding engine — acquire / snapshot / validate / refresh / diff / assumptions / freshness) + `commercial` (analysis consumer — `field` / `market` / `roadmap` actions + deterministic computation library + claim lint). Mirrors the docflow pattern: an engine other skills can adopt (regulatory guidance-monitoring, post-market MAUDE trends are future tenants). Rejected: folding snapshot machinery into `commercial` (would trap a general capability in one consumer).
- **Corpus lives at `docs/project/corpus/<domain>/<dataset>/`** — shared project tree; immutable dated snapshots (`raw/` byte-pinned + `normalized/` schema-validated + `provenance.yml` with parent-by-hash + usage-rights), `latest` pointer, first-class A-NNN assumption records, delta reports on refresh. Extends the existing `docs/external/` document-provenance discipline (md5-pinned source → source-md → distilled) to structured data.
- **Real external data over fabrication**: acquire from public sources (openFDA 510(k)/MAUDE/recalls — public domain; competitor spec sheets; market reports) with real competitor names; fabricate only OUR internal data (fictional company), routed through the same snapshot machinery so it's swappable for real ERP/CRM/service exports in a client deployment. Where data doesn't exist, record an assumption — never silently invent.
- **Anti-hallucination architecture**: (a) the LLM orchestrates and interprets, scripts compute — no model-typed numbers; (b) asserts + schema validation at acquisition; (c) provenance completeness checks; (d) semantic guards as asserts (no MAUDE rate without a denominator assumption); (e) claim lint — every numeric claim in narrative carries a `dataset@snapshot` citation, mechanically recomputed; (f) adversarial re-derivation of headline claims by an independent subagent; (g) honesty labels measured/derived/assumed/unavailable; (h) freshness enforcement — per-dataset `max_age_days`, stale snapshots block current-state claims unless visibly waived.
- **Build order: field performance first** — most novel demo story, reuses post-market + fleet-management assets, and "are we to plan?" resonates with every commercial audience.
- **Visualization tier fully separated (confirmed 2026-07-22)**: analysis skills emit only data (markdown reports + schema-versioned JSON sidecars with chart series); the project console is a pure consumer rendering charts client-side — the same loose-coupling contract Submission/Tasks already use. One topline Commercial section, question-centric UI (the BQ catalog is the navigation spine).
- **Editions lifecycle for answers (confirmed 2026-07-22)**: each BQ answer is an immutable edition series (draft → approved → superseded); refresh opens a new draft, never mutates approved; approval is GATED on green checks (claim lint + freshness/waiver + adversarial verify) and hash-pins content; console shows approved by default with draft watermarking and per-question history + deltas. Formal Part 11 escalation stays with `change-control`, not rebuilt.
- **Plan expectations are first-class records (Ben review feedback 2026-07-22)**: actuals come from data, but the EXPECTATIONS they're judged against (close dates, targets, thresholds) must themselves be stated objects — id, statement, expected, basis, set_by, `validated:` flag — evaluated every edition (met / at-risk / not-met / not-evaluable) and rendered with an `unvalidated` chip when the expectation is a stand-in never grounded in a plan of record or the risk file. "Are the assumptions correct?" becomes an on-screen question, not an implicit trust. Companion additions from the same review: deterministic Risks/Mitigations/Issues narrative blocks (marker-cited, mirrored in the linted report) and timeseries trend charts (zero-filled so stalls render as flatlines).
- **Reader aids are catalog content, not report content (Ben review feedback 2026-07-27)**: plain-language term definitions and per-series explainers live in `commercial.yml` (top-level `terms:` dictionary + per-question `terms:`/`explainers:`), rendered into the sidecar (schema 1.1) — NOT in the reports. Rationale: reports are edition-pinned and regenerated per answer, so explainer text there would be re-authored every edition and tempt pin-dependent phrasing; catalog-side text is written once, TIMELESS by rule (defines the metric and its significance; no counts/dates/current values), and survives every re-answer. Engine resolves term references and never fabricates a definition (unresolved key = warning + skip). Explainers key on real data.json series ids — a mis-keyed explainer renders nowhere, so authoring requires reading the latest edition's data.json.
- **Provenance layer is end-to-end and mandatory (confirmed 2026-07-22)**: every figure machine-walkably traces report claim → data series → normalized hash → raw source (or → stated A-NNN assumption); an unsubstantiated claim is a lint ERROR; the console renders the chain as a click-through panel.

**Why**: Commercial buyers ask "are we winning?" — the answers must be data-backed, reproducible, and honest about what's measured vs assumed; exposed epistemics are the differentiator over standard BI demos, and non-negotiable in a regulated industry.
**How to apply**: New analytics capabilities = new `commercial` actions + new corpora under `docs/project/corpus/`; any skill needing versioned external grounding should consume `corpus`, not roll its own snapshotting; every published figure must be script-computed and citation-carrying.
<!-- Source: ben/108, "Strategy & Lessons capture" (heading substituted — see History), last modified 2026-07-29 -->
<!-- DECISION:end id=D-OPS-1.12 -->

<!-- DECISION:start id=D-OPS-1.13 status=active source=ben/109 created=2026-08-06 last-edited=2026-08-06 -->
### 1.13 Commercial advisor added to the persona bundle

**Decision — commercial advisor added to the persona bundle (2026-07-22).** The project had a full commercial stack (commercial skill BQ editions, corpus data tier, `commercial-strategy.md`, market-research/competitive-landscape input analysis) with no advisor grounding on any of it; `commercial-strategy.md` was referenced nowhere in the canonical-roles catalog. Tier 1 deliberately deviates from the default (`architecture_strategy` + system SAD) to `commercial_strategy` + `regulatory_strategy` — commercial questions gate on filing pathway/timing, not system architecture. Catalog gaps were closed by extending `canonical-roles.yaml` (per advisors SKILL.md L43 — never papered over with literal globs). Deferred candidates, revisit if demo scope grows: manufacturing/design-transfer persona (hardware device, no owner for production readiness); reimbursement/health-economics folded into commercial rather than split out.
<!-- Source: ben/109, "Todos" (heading substituted — see History), last modified 2026-07-22 -->
<!-- DECISION:end id=D-OPS-1.13 -->

<!-- DECISION:start id=D-OPS-1.14 status=active source=ben/104 created=2026-08-06 last-edited=2026-08-06 -->
### 1.14 Teaching-project access posture

**Decision — teaching-project access posture (2026-07-15):** Repo access audit severity is keyed to GitHub permission level, not roster membership alone. Read/triage collaborators outside the roster are **expected observers** (info) — this demo/teaching project grants visibility broadly; the roster tracks *contributors*, not viewers. Unrostered write/maintain/admin is a **warning** (roster them or reduce to read); an offboarded (team.inactive) member retaining any access is an **error**. CLAUDE.md roster policy updated accordingly ("every collaborator" → "every collaborator with write access").
**Why:** the prior all-error posture buried real signal in observer noise (18 identical errors). Permission-awareness preserves the security property that matters — *who can change the regulated record* — while accommodating the teaching mission.
**How to apply:** grant observers read access only. The 2026-07-15 audit found 15 unrostered write + 1 unrostered admin grants that contradict the observer premise — pending user decision (bulk-reduce to read vs roster).
<!-- Source: ben/104, "Strategy" (heading substituted — see History), last modified 2026-07-16 -->
<!-- DECISION:end id=D-OPS-1.14 -->

<!-- DECISION:start id=D-OPS-1.15 status=active source=ben/002 created=2026-08-06 last-edited=2026-08-06 -->
### 1.15 `how-to-guide.md` stays at repo root, sibling to `setup.md`

**Decision — `how-to-guide.md` stays at repo root, as a sibling of `setup.md`, with a one-line cross-reference between them.** The two docs answer different questions for different audiences: `setup.md` = "I'm joining *this* repo, get me wired up safely" (contributor onboarding + security posture); `how-to-guide.md` = "I have a *new* device program, stand it up the way PDLC_DEMO was built" (project bootstrap using the skills). Keeping both at root mirrors that they're peer entry points; neither belongs under `docs/` (which is the *output* of the process the guide describes, not meta-documentation about it). Resolves the open question in the skeleton. The "should Phase 6 become its own skill" question stays open — flagged in-guide as a future capability, deferred until the prose flow is exercised on a second project.
<!-- Source: ben/002, "Authoring session 2026-05-21 — source-of-truth verification + fill-in" (heading substituted — see History), last modified 2026-06-08 -->
<!-- DECISION:end id=D-OPS-1.15 -->

<!-- DECISION:start id=D-OPS-1.16 status=active source=ben/062 created=2026-08-06 last-edited=2026-08-06 -->
### 1.16 Tier-3 rule — `git-workflow` is project-authored, never registry-distributed

**Tier-3 rule.** `git-workflow` is project-authored, never registry-distributed — each project chooses its own git workflow. Copied from arthrex as the starting point. **Open question flagged to user:** the copied rule defines "push" as PR-then-auto-merge, but PDLC-DEMO has been operating direct-to-`main` this session — the rule may need adapting to match actual practice.
<!-- Source: ben/062, "Goals" (heading substituted — see History), last modified 2026-05-16 -->
<!-- DECISION:end id=D-OPS-1.16 -->

<!-- DECISION:start id=D-OPS-1.17 status=active source=ben/061 created=2026-08-06 last-edited=2026-08-06 -->
### 1.17 Rule-ownership model, batch 3 — `claude-md-references` + `audit-wiring` → `medtech-docs`

**Rule-ownership model, batch 3.** `claude-md-references` + `audit-wiring` → `medtech-docs`. medtech-docs now owns 4 auto-loaded rules. The `audit-wiring` dedup resolves a self-ironic case — the rule existed both as a promoted `.claude/rules/` file *and* a medtech-docs-seeded CLAUDE.md block (duplication is exactly what the rule forbids). Resolution: single `.claude/rules/` symlinked file; CLAUDE.md block dropped. Rule-creation routes observed across the batches: extraction (claude-md-references, from CLAUDE.md slimming), lesson-promotion (audit-wiring), direct authoring (git-workflow).
<!-- Source: ben/061, "Goals" (heading substituted — see History), last modified 2026-05-15 -->
<!-- DECISION:end id=D-OPS-1.17 -->

<!-- DECISION:start id=D-OPS-1.18 status=active source=ben/060 created=2026-08-06 last-edited=2026-08-06 -->
### 1.18 Rule-ownership model, batch 2 — `readme-before-write` + `sentinel-blocks` → `medtech-docs`

**Rule-ownership model, batch 2.** `readme-before-write` + `sentinel-blocks` → `medtech-docs` (owns the `docs/` tree + README scaffolding + `render-sentinels.py`). Same symlink-install pattern as task v25. sentinel-blocks' real coupling is to `/best-practices fix` (calls the renderer), not Confluence — origin traced to sister-project task 072 (README drift detection + auto-remediation), not change-control. Remaining unowned rules: `claude-md-references`, `audit-wiring-before-adding-fields` (tier-2 candidates), `git-workflow` (tier-3, project-authored, never registry).
<!-- Source: ben/060, "Background — current state (recon 2026-05-15)" (heading substituted — see History), last modified 2026-05-15 -->
<!-- DECISION:end id=D-OPS-1.18 -->

<!-- DECISION:start id=D-OPS-1.19 status=active source=ben/059 created=2026-08-06 last-edited=2026-08-06 -->
### 1.19 Rule-ownership model — auto-loaded rules are owned by their most-related skill

**Rule-ownership model.** Auto-loaded `.claude/rules/` files are owned by their most-related skill, which installs them during its `setup` action. scratch-and-tmp → task skill. This is the per-rule disposition pass the user is running ("find the right home for each type of rule"); other rules (sentinel-blocks, readme-before-write, git-workflow, etc.) will be dispositioned separately.
<!-- Source: ben/059, "Background" (heading substituted — see History), last modified 2026-05-15 -->
<!-- DECISION:end id=D-OPS-1.19 -->

<!-- DECISION:start id=D-OPS-1.20 status=active source=ben/057 created=2026-08-06 last-edited=2026-08-06 -->
### 1.20 Accept-then-correct over edit-then-merge (registry PR governance)

**Decision — accept-then-correct over edit-then-merge.** When a registry PR is mechanically safe but content-stale, merge the contributor's work untouched (preserves attribution + a clean `#163` merge commit), then layer corrections as a separate commit. Avoids rewriting someone else's branch and keeps the "what was contributed" vs "what we fixed" history legible.

**Decision — canonical version source is `SKILL.md` frontmatter, not `VERSION` files.** The registry's Project Practices table checks `version:` in `SKILL.md` YAML frontmatter. When the two disagree, the manifest follows frontmatter; `VERSION`-file drift is logged as a separate skill bug rather than papered over in the manifest.
<!-- Source: ben/057, "Review Findings" (heading substituted — see History), last modified 2026-05-13 -->
<!-- DECISION:end id=D-OPS-1.20 -->

<!-- DECISION:start id=D-OPS-1.21 status=active source=ben/007 created=2026-08-06 last-edited=2026-08-06 -->
### 1.21 Cross-skill topology awareness

> **Staleness note (2026-08-06 assembly):** this decision predates the `/strategy` v10 shared-domain model. The `sub-dhf=` tag-scoping mechanism proposed below was **not** adopted — every strategy domain is now `shared`, one document per domain, and the `dhf=`/`sub-dhf=` scope key is deprecated and stripped by the scanner. Retained for design history; see [Open Items](#open-items).

#### Decision: all consuming skills become topology-aware in task 007

**Decision**: The four skills that read project-scoped paths — `/strategy`, `/tracker`, `/best-practices`, `/task` — will be updated **as part of task 007**, not as a follow-up. The migration action is not considered done until every consuming skill handles both `single-dhf` and `multi-sub-dhf` topologies correctly.

**Why**: A half-migrated ecosystem where the folder structure is multi-sub-DHF but `/strategy assemble` writes to the wrong (pre-migration) path, or `/best-practices` audits a nonexistent `docs/project/design-controls/` — is worse than no migration at all. Partial readiness becomes silent breakage the team debugs later. Folding the skill updates into the same task guarantees a coherent cutover.

**How to apply**: Task 007's "Done" definition includes the skill updates below. No skill is allowed to keep hardcoded `docs/project/design-controls/...` paths after this task completes.

#### Per-skill updates required

| Skill | What reads a project path today | Topology-aware behavior |
|---|---|---|
| **`medtech-docs`** | `init` writes to `docs/project/{design-controls,clinical,postmarket,...}/` | Branches on topology; in multi-sub-dhf mode writes under `docs/project/dhfs/<name>/`. Also gains `check-topology`, `add-sub-dhf`, `migrate-to-multi-dhf` actions. |
| **`strategy`** | SKILL.md domain registry hardcodes output paths like `docs/project/design-controls/plans/regulatory-strategy.md` | Reads `project.topology` from `project.yml`. In multi-sub-dhf mode, each sub-DHF gets its own strategy instance (e.g., `dhfs/pca-device/design-controls/plans/regulatory-strategy.md`). Scope tag in strategy content tags (`<!-- STRATEGY CONTENT: regulatory, sub-dhf=pca-device, ... -->`) routes content to the correct sub-DHF's strategy doc. Shared `external/internal/input-analysis` stay at the top level. |
| **`tracker`** | Renders dashboards from folder trees under `docs/project/` | In multi-sub-dhf mode, renders one dashboard per sub-DHF plus a roll-up across sub-DHFs. Composition manifests in `submissions/` show which sub-DHF pieces are in each filing. |
| **`best-practices`** | Audits well-known paths; current checks assume single-dhf | Reads topology from `project.yml`. In multi-sub-dhf mode, runs per-DHF checks and rolls up; verifies every `submissions/<filing>/` has a `composition-manifest.md`. |
| **`task`** | Does not read project-scoped paths directly | No changes required, but task template may gain an optional `sub-dhf:` field for tagging which sub-DHF a task targets. |

#### `project.yml` additions

To support topology-aware skills:

```yaml
project:
  # ... existing fields ...
  topology: multi-sub-dhf          # or "single-dhf"
  sub_dhfs:                        # present only when topology == multi-sub-dhf
    - name: pca-device
      parent: null
      regulatory: cleared          # cleared | in-development | concept
      filing: K210345
    - name: connectivity-adapter
      parent: null
      regulatory: in-development
      filing: null
    - name: cloud-suite
      parent: null
      regulatory: mixed
      filing: null
    - name: drug-library-manager
      parent: cloud-suite
      regulatory: in-development
      filing: null
    # ... etc ...
```

Skills read this manifest to discover the topology and enumerate sub-DHFs. It becomes the single source of truth for "what does this project contain."

#### Strategy content tag extension — sub-DHF scoping

The `/strategy` skill currently uses tags like `<!-- STRATEGY CONTENT: regulatory, topic1, topic2 -->`. In a multi-sub-dhf project, the same task might contain strategy decisions for multiple sub-DHFs (e.g., a cross-cutting cybersecurity decision affecting both PCA and Cloud Suite). To route correctly, the tag grows an optional scope:

```markdown
<!-- STRATEGY CONTENT: regulatory, sub-dhf=pca-device, classification, filing -->
```

- No `sub-dhf=` key → shared strategy (routes to a top-level strategy doc, or applies to all sub-DHFs depending on the domain)
- `sub-dhf=<name>` → routes to that sub-DHF's strategy doc
- `sub-dhf=<name1>,<name2>` → routes to multiple sub-DHFs' strategy docs (rare; cross-cutting concerns)

The `assemble` action picks up the scope, finds the right output path via `project.yml`, and writes accordingly.

#### Execution phasing inside task 007

Given the scope expansion, task 007 runs in phases:

| Phase | What ships | Gate |
|---|---|---|
| **P1. `medtech-docs` topology foundation** | Topology model in SKILL.md, `project.yml` schema, `check-topology` action, brief template updates | Design review before coding |
| **P2. `medtech-docs` migration action** | `migrate-to-multi-dhf` (dry-run + apply), `add-sub-dhf`, cross-link sweeper | Dry-run on PDLC_DEMO clean |
| **P3. `strategy` topology awareness** | Reads `project.yml` topology, per-sub-DHF output paths, `sub-dhf=` scope key in tags | `/strategy scan` and `assemble` work in both topologies |
| **P4. `tracker` topology awareness** | Per-sub-DHF dashboards and roll-up | Renders PDLC_DEMO in multi-sub-dhf mode |
| **P5. `best-practices` topology awareness** | Per-sub-DHF checks, composition-manifest validation | Audit PDLC_DEMO in multi-sub-dhf mode clean |
| **P6. PDLC_DEMO migration (live fire)** | Run the upgraded skill on PDLC_DEMO end to end | Full validation suite passes post-migration |
| **P7. Upstream contribution** | PR to hitachi registry | Merged or queued |

Phases P3–P5 can run in parallel once P1 and P2 land.
<!-- Source: ben/007, "Cross-Skill Topology Awareness (in scope for this task)", last modified 2026-04-13 -->
<!-- DECISION:end id=D-OPS-1.21 -->

## Open Items

_Unresolved [VERIFY] markers and items needing human decision._

### `[VERIFY]` markers carried from source tasks

- **[VERIFY]** (D-OPS-1.1, [ben/115](../../../tasks/ben/115-tooling-and-testing-validation-strategy.md) — "The workbench is software used in the quality system") The governing external references for the workbench determination — FDA's Computer Software Assurance guidance, ISO 13485 §4.1.6, and the QMSR design-controls anchor — are **not yet distilled into `docs/external/`**. FDA CSA exists in this repo only as undistilled raw source under the registry's `references/fda-guidance/source-md/`, with no project applicability file. The determination must not be finalised on paraphrase; import the guidance first.
- **[VERIFY]** (D-OPS-1.2, [ben/115](../../../tasks/ben/115-tooling-and-testing-validation-strategy.md) — "Assurance is risk-based and evidence-led") Whether to adopt a formal software-categorisation scheme (e.g. GAMP-style categories separating the vendor CLI from project-authored agents and skills) as the routing mechanism for assurance depth. No copy of the framework exists in this repo, so adopting it means importing it first.
- **[VERIFY]** (D-OPS-1.3, [ben/115](../../../tasks/ben/115-tooling-and-testing-validation-strategy.md) — "Human review is the control that carries the argument") A widely-cited enforcement precedent for AI-authored quality records exists in the sister project's operations strategy (a warning letter concerning AI-generated specifications and production records without adequate human review). It is **not** in this project's `docs/external/` and has not been verified against the byte-correct source here. It must not be cited until it does.

### Scope gaps — operational facets not yet authored

Per D-OPS-1.9, this document deliberately carries only the **tooling half** of the `operations` domain at this assembly. The following `what_belongs_here[]` facets from `project.yml strategy_domains[]` have **no assembled decision**:

- **Build, release, and CI/CD pipeline decisions** — D-OPS-1.5 names the enforcement bar and records that CI carries zero quality gates today, but no pipeline strategy is authored.
- **Supply chain and SOUP/SBOM management** — no coverage.
- **Cloud infrastructure and hosting posture** — no coverage.
- **QMS operational readiness** — partially implied by D-OPS-1.1 / D-OPS-1.3 / D-OPS-1.4, not authored as a facet.
- **Project management approach** — partially implied by D-OPS-1.8 / D-OPS-1.14 / D-OPS-1.16, not authored as a facet.

### Stale content flagged during assembly

- **D-OPS-1.21 ([ben/007](../../../tasks/ben/007-sub-dhf-migration.md)) is superseded in part by the `/strategy` v10 shared-domain model.** The block proposes a `sub-dhf=<name>` scope key routing strategy content to per-sub-DHF strategy documents. The operative model routes every domain to a single shared document and the scanner strips `dhf=`/`sub-dhf=` keys as deprecated. This was **not** treated as a strategy-block conflict (no other tagged `operations` block decides the same question), so no `STRATEGY REVIEWED: superseded by` marker was written to the source task. **Human decision needed:** either mark the ben/007 block superseded at source, or split it so the still-current topology-awareness decisions survive without the retired tag-scoping proposal.
- **D-OPS-1.16 ([ben/062](../../../tasks/ben/062-git-workflow-rule.md)) carries an open question that D-OPS-1.5 has since answered with evidence.** ben/062 flagged that the copied `git-workflow` rule defines "push" as PR-then-auto-merge while the project had been operating direct-to-`main`. The 2026-08-06 verification in D-OPS-1.5 confirms there is **no branch protection** on the default branch and nothing verifies the PR path was taken. The two are complementary, not conflicting — but the open question is now answerable and should be closed at source.

### Other items needing human decision

- **Unassembled multi-line tags in [ben/054](../../../tasks/ben/054-agentic-first-medtech-strategy.md).** That task carries a `<!-- STRATEGY CONTENT: operations, regulatory, risk` block (the Gate Maturity Ladder) written as a multi-line HTML comment whose body sits *inside* the comment rather than below a self-closing tag line. It does not match the scanner's tag form and was **not** assembled here — consistent with every other domain (no strategy document in this folder cites ben/054). The block explicitly asks whether the "Agentic Process Validation" deliverable folds into `operations-strategy.md`. **Decision needed:** reformat the ben/054 blocks to the single-line tag convention so they harvest, or leave them as design history.

## History


### 2026-08-06 — post-assembly correction pass (ben/115)
- An independent verification pass re-checked every quantitative and factual claim in the ben/115-sourced decisions against the repository, briefed to falsify rather than confirm.
- **6 corrections applied** to decision bodies in this document, mirrored into the source blocks in [ben/115](../../../tasks/ben/115-tooling-and-testing-validation-strategy.md) so the next assembly reproduces them.
- No decision was added, removed, or re-identified; no heading changed. Corrections were confined to claim wording and figures.
- Notable: the frozen-document hook is **designed but never installed** (previously stated as registered); the agent allowlist gap is **18 of 50** (was 19); registry provenance accounts for **14 of 39** skills while the skill allowlist is complete at 39/39; and a claim that the usage data file carried conflict markers and would not parse was **retracted as false** — it parses cleanly, and the earlier incident had a different cause.


_Append-only log of changes across assemblies. Most recent first._

### 2026-08-06 — assembled by benxavier-gl

- **Initial assembly** from ben/002, ben/007, ben/057, ben/059, ben/060, ben/061, ben/062, ben/104, ben/108, ben/109, ben/111, ben/112, ben/115
- **Added**: The workbench is software used in the quality system (ben/115), Assurance is risk-based and evidence-led (ben/115), Human review is the control that carries the argument (ben/115), What the workbench may and may not produce (ben/115), A control that does not execute is not a control (ben/115), Measurement stays honest about what is measured and what is modelled (ben/115), The knowledge loop stages but does not promote (ben/115), The evidence base is one operator (ben/115), Tooling strategy lands in the `operations` domain (ben/115), Why this metric — user turns (ben/112), Standard list prices, not introductory rates (ben/111), Commercial analytics layer (ben/108), Commercial advisor added to the persona bundle (ben/109), Teaching-project access posture (ben/104), `how-to-guide.md` stays at repo root (ben/002), Tier-3 rule — `git-workflow` is project-authored (ben/062), Rule-ownership model batch 3 (ben/061), Rule-ownership model batch 2 (ben/060), Rule-ownership model (ben/059), Accept-then-correct over edit-then-merge (ben/057), Cross-skill topology awareness (ben/007)
- **Heading substitutions** (source H2 was task-doc scaffolding; replacement derived from the block's own first bolded decision phrase, per the assembly brief):

  | Decision | Source task | Source H2 | Assembled heading |
  |---|---|---|---|
  | D-OPS-1.10 | ben/112 | `## Strategy` | Why this metric — user turns as a measured human-effort signal |
  | D-OPS-1.11 | ben/111 | `## Strategy` | Standard list prices, not introductory rates |
  | D-OPS-1.12 | ben/108 | `## Strategy & Lessons capture` | Commercial analytics layer — `corpus` grounding engine + `commercial` analysis skill |
  | D-OPS-1.13 | ben/109 | `## Todos` | Commercial advisor added to the persona bundle |
  | D-OPS-1.14 | ben/104 | `## Strategy` | Teaching-project access posture |
  | D-OPS-1.15 | ben/002 | `## Authoring session 2026-05-21 — source-of-truth verification + fill-in` | `how-to-guide.md` stays at repo root, sibling to `setup.md` |
  | D-OPS-1.16 | ben/062 | `## Goals` | Tier-3 rule — `git-workflow` is project-authored, never registry-distributed |
  | D-OPS-1.17 | ben/061 | `## Goals` | Rule-ownership model, batch 3 — `claude-md-references` + `audit-wiring` → `medtech-docs` |
  | D-OPS-1.18 | ben/060 | `## Background — current state (recon 2026-05-15)` | Rule-ownership model, batch 2 — `readme-before-write` + `sentinel-blocks` → `medtech-docs` |
  | D-OPS-1.19 | ben/059 | `## Background` | Rule-ownership model — auto-loaded rules are owned by their most-related skill |
  | D-OPS-1.20 | ben/057 | `## Review Findings` | Accept-then-correct over edit-then-merge (registry PR governance) |

  Source block content is unmodified in every case; only the heading differs. D-OPS-1.9 and D-OPS-1.21 kept their source headings (a real `###` and a descriptive `##` respectively). D-OPS-1.1 – D-OPS-1.8 use their source `###` headings verbatim.
- **Structural note**: ben/007's tagged block contains five `###` subsections, but only one of them is a decision — the other four (per-skill updates, `project.yml` additions, tag extension, execution phasing) are its supporting apparatus. It was therefore emitted as **one** decision (D-OPS-1.21) headed by the block's `##`, with the internal `###` headings demoted to `####`. Content is intact. By contrast, ben/115's tooling block contains eight genuinely independent decisions and was emitted as eight decision blocks.
- **Conflicts resolved**: none — **zero same-question conflicts detected**. Tier-1 heading overlap fires on D-OPS-1.17 / D-OPS-1.18 / D-OPS-1.19 (all "Rule-ownership model"), but these are sequential batches of one decision applied to different rule sets, not competing answers; treated as complementary per the Tier-2 different-facets rule. Tier-2 semantic overlap was assessed across all 21 decisions (default template routes everything into one output section): the blocks cover registry governance, repo governance, access policy, commercial-analytics tooling architecture, advisor roster, cost model, skill topology, and workbench qualification — genuinely different facets. No `STRATEGY REVIEWED` / `STRATEGY PROPOSED` markers were written to any source task.
- **Conflicts deferred**: none.
- **Not assembled**: ben/054's `operations`-domain block (Gate Maturity Ladder) — multi-line tag form the scanner does not match; recorded in Open Items.
- 21 decisions from 14 tagged blocks across 13 tasks, 3 [VERIFY] markers, 0 Uncategorized.

## Source Traceability

| Output Section | Source Task | Source Subsection | Last Modified |
|---------------|-----------|-------------------|---------------|
| Strategy Decisions | [ben/115](../../../tasks/ben/115-tooling-and-testing-validation-strategy.md) | The workbench is software used in the quality system, and that is the question to answer | 2026-08-06 |
| Strategy Decisions | [ben/115](../../../tasks/ben/115-tooling-and-testing-validation-strategy.md) | Assurance is risk-based and evidence-led, not classical qualification theatre | 2026-08-06 |
| Strategy Decisions | [ben/115](../../../tasks/ben/115-tooling-and-testing-validation-strategy.md) | Human review is the control that carries the argument — and only if it is real | 2026-08-06 |
| Strategy Decisions | [ben/115](../../../tasks/ben/115-tooling-and-testing-validation-strategy.md) | What the workbench may and may not produce | 2026-08-06 |
| Strategy Decisions | [ben/115](../../../tasks/ben/115-tooling-and-testing-validation-strategy.md) | A control that does not execute is not a control | 2026-08-06 |
| Strategy Decisions | [ben/115](../../../tasks/ben/115-tooling-and-testing-validation-strategy.md) | Measurement stays honest about what is measured and what is modelled | 2026-08-06 |
| Strategy Decisions | [ben/115](../../../tasks/ben/115-tooling-and-testing-validation-strategy.md) | The knowledge loop stages but does not promote | 2026-08-06 |
| Strategy Decisions | [ben/115](../../../tasks/ben/115-tooling-and-testing-validation-strategy.md) | The evidence base is one operator, and the strategy should not pretend otherwise | 2026-08-06 |
| Strategy Decisions | [ben/115](../../../tasks/ben/115-tooling-and-testing-validation-strategy.md) | Tooling strategy lands in the `operations` domain, not a new `tooling` domain | 2026-08-06 |
| Strategy Decisions | [ben/112](../../../tasks/ben/112-usage-metrics-user-turn-counting.md) | Strategy _(heading substituted)_ | 2026-08-06 |
| Strategy Decisions | [ben/111](../../../tasks/ben/111-usage-metrics-rate-card-refresh.md) | Strategy _(heading substituted)_ | 2026-08-05 |
| Strategy Decisions | [ben/108](../../../tasks/ben/108-commercial-analytics-suite.md) | Strategy & Lessons capture _(heading substituted)_ | 2026-07-29 |
| Strategy Decisions | [ben/109](../../../tasks/ben/109-commercial-advisor.md) | Todos _(heading substituted)_ | 2026-07-22 |
| Strategy Decisions | [ben/104](../../../tasks/ben/104-console-setup-redesign.md) | Strategy _(heading substituted)_ | 2026-07-16 |
| Strategy Decisions | [ben/002](../../../tasks/ben/002-how-to-guide-project-setup.md) | Authoring session 2026-05-21 — source-of-truth verification + fill-in _(heading substituted)_ | 2026-06-08 |
| Strategy Decisions | [ben/062](../../../tasks/ben/062-git-workflow-rule.md) | Goals _(heading substituted)_ | 2026-05-16 |
| Strategy Decisions | [ben/061](../../../tasks/ben/061-medtech-docs-references-and-audit-wiring-rules.md) | Goals _(heading substituted)_ | 2026-05-15 |
| Strategy Decisions | [ben/060](../../../tasks/ben/060-medtech-docs-rules-symlink-migration.md) | Background — current state (recon 2026-05-15) _(heading substituted)_ | 2026-05-15 |
| Strategy Decisions | [ben/059](../../../tasks/ben/059-codify-scratch-tmp-convention.md) | Background _(heading substituted)_ | 2026-05-15 |
| Strategy Decisions | [ben/057](../../../tasks/ben/057-review-and-correct-skills-manifest.md) | Review Findings _(heading substituted)_ | 2026-05-13 |
| Strategy Decisions | [ben/007](../../../tasks/ben/007-sub-dhf-migration.md) | Cross-Skill Topology Awareness (in scope for this task) | 2026-04-13 |
