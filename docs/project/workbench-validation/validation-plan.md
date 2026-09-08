<!-- Changelog
| Version | Date | Author | Summary |
|---------|------|--------|---------|
| 0.1 | 2026-07-27 | BX / AI Assistant | Initial plan — intended-use classes, risk tiers, WUN register (15 needs), assurance model |
-->
<!-- AI-CHANGELOG — internal provenance of AI-assisted edits. Metadata only:
     NOT published downstream, NOT part of the controlled record.
| Date       | Task | Summary                                                    |
|------------|------|------------------------------------------------------------|
| 2026-07-27 | 110  | Initial authoring from three-agent research synthesis       |
-->

# Workbench Validation Plan — PDLC_DEMO AI Workbench

_Demo sample data — not for clinical use._ This validation package is **illustrative
of method only**. It does not assert compliance with ISO 13485 §4.1.6, 21 CFR
Part 11, or FDA CSA guidance; clause citations marked [VERIFY] have not been checked
against licensed source text; fitness-for-use conclusions are teaching examples, not
quality records.

## 1. Purpose & scope

Risk-based validation of the AI workbench — the `.claude/` toolchain (skills, agents,
hooks, scripts, rules) plus the project console — used to author and manage this
project's design-control and submission artifacts. This validates the **toolchain,
not the device**: device V&V lives in `docs/project/dhfs/<dhf>/`.

**Why validation is owed at all:** tools that produce or gate controlled records are
QMS software. The corporate anchor is **GL-WI-SW-004 §8 "Tool Validation"**
(`docs/internal/source-md/software-cybersecurity/software-vv-wi.md`): tools impacting
a result shall be validated for intended use via (1) documented intended use, (2) a
risk assessment ("what could the tool get wrong, and how would that affect a release
decision?"), (3) risk-scaled evidence, (4) a configuration baseline — revalidated on
tool upgrade or use-case change. GL-SOP-QM-001 (§ electronic records: "validated
systems, audit trails, access controls") and GL-SOP-QM-006 extend the obligation to
the systems handling controlled records. External drivers not distilled in-project
and therefore [VERIFY]: ISO 13485:2016 §4.1.6 (QMS software validation), FDA CSA
guidance (risk-based assurance), 21 CFR Part 11 source text, GAMP 5. Note:
GL-WI-SW-004's own "IEC 62304 §6.1" citation is itself flagged for reference audit.

**Standing mitigating control (cited throughout):** no workbench output enters the
controlled record without human review and the git/PR audit trail (git-workflow rule;
regulatory-authoring 3-stage check). The workbench is *assistive with
human-in-the-loop* — never direct release without review — which legitimately lowers
the assurance tier under CSA-style logic [VERIFY].

## 2. Intended-use classes

| Class | Intended-use pattern | Representative tools |
|---|---|---|
| authoring | Draft/structure controlled artifacts; all output human-reviewed before entering the record; the tool does not release, sign, or transmit | medtech-docs, submissions, regulatory-authoring, docflow, change-control, strategy |
| audit | Detect and report nonconformities/gaps; advisory; the risk is false negatives | best-practices, reference-audit, gap-analysis, dhf-manifest, tracker, trace-matrix, jira-pull |
| gates | Automatically enforce a rule by blocking a tool call; failure mode is silent non-enforcement | task gate hook, docflow conversion-block hook |
| renderers | Derive display/structural content deterministically from a declared source of truth | render-sentinels.py, advisor grounding renderer, sidecar generators |
| console | Display status for situational awareness; not a decision-of-record system | project-console, md-deck, digest, usage-metrics |
| config-control | Control the workbench configuration itself — versions, allowlists, registry sync, security posture | sync-skills, secops, project.yml allowlists |

## 3. Risk tiers → assurance depth

| Tier | Definition | Assurance |
|---|---|---|
| **T1 High** | Output enters the DHF/submission record, or the tool gates record integrity | Scripted tests for every deterministic component; exploratory challenge + process controls for LLM-driven parts; revalidate on version/config/model change |
| **T2 Medium** | Advisory detection or configuration control; a false negative degrades (not defeats) quality | Scripted smoke/regression tests; seeded-error spot checks where practical |
| **T3 Low** | Display/telemetry; errors self-evident against the underlying repo | Intended-use note; verified by use; vendor/platform reliance |

## 4. Workbench user needs (WUN register)

Each need is a **user story**: _As a `<role>`, I need the workbench to `<outcome>`, so
that `<purpose>`._ The outcome is what the role can observe, deliberately free of
implementation detail (the role does not know or care how the workbench meets the
need); the purpose is required — it is what a reviewer uses to judge whether the
mapped evidence really assures the need, and what the risk tier follows from. The
mechanism appears only in the *Implemented by* column, as traceability information —
it is not part of the need and may change without the need changing. "The workbench"
is used deliberately: in this project "the system" means the device.

Machine-readable copy: `validation.yml` (`user_needs[]` — `role` / `need` / `so_that`);
the runner and report consume the manifest, and this table is regenerated from it.

| ID | Role | I need the workbench to… | So that… | Tier | Coverage | Implemented by (traceability) |
|---|---|---|---|---|---|---|
| WUN-01 | DHF author | produce a controlled document whose structure matches the governing QMS form, without me having to remember the form's rules | my draft passes document control without structural rework | T1 | process-control | medtech-docs scaffolding + .taxonomy.yml doctype governance + regulatory-authoring workflow |
| WUN-02 | Reviewer / approver | show me which content in a controlled document came from the AI assistant and which a human wrote or approved | I review AI-drafted content with the scrutiny it needs and sign off only on what a person has owned | T1 | process-control | AI-changelog metadata blocks + working-vs-formal document split + PR history |
| WUN-03 | Regulatory affairs lead | visibly flag any claim it drafted but could not verify, never asserting it silently as fact | an unverified regulatory claim can never reach a submission unnoticed | T1 | process-control | [VERIFY] flag convention + no-fabrication policy + mandatory reference audit on citation-bearing edits |
| WUN-04 | DHF author | catch mechanical writing defects (leaks, jargon, clutter, undefined terms) automatically and reliably before my document goes out for review | reviewers spend their time on substance, not copy-editing | T1 | tests | writing-well + regulatory-authoring deterministic lint scripts |
| WUN-05 | Quality engineer | give me a trustworthy answer on whether a cited standard, guidance, or internal source really says what the document claims | citations in the controlled record survive an auditor checking them against the source text | T2 | exploratory | reference-audit skill + citations advisor (LLM-driven verification against byte-correct sources) |
| WUN-06 | Quality engineer | tell me from our own audit run which required design-history documents are missing, unmapped or out of place against the declared structure | we find documentation gaps before an external auditor does | T2 | tests | dhf-manifest discovery index + coverage audit (validate.py / audit-coverage.py) |
| WUN-07 | Program lead | refuse any change to a project file that is not anchored to a tracked task | every change is traceable to why it was made | T1 | tests | task-gate PreToolUse hook (check-active-task.sh) with exempt-path list |
| WUN-08 | Quality engineer | block document conversion outside the controlled pipeline unless someone deliberately and visibly overrides it | every formal document has a known conversion provenance | T1 | tests | docflow conversion-block PreToolUse hook with .state/docflow-active override marker |
| WUN-09 | DHF author | keep the auto-generated sections of my documents current with their source of truth without damaging the text I wrote by hand around them | I can trust generated content and never lose my own | T1 | tests | sentinel-block renderer (render-sentinels.py) + advisor grounding renderer, both idempotent |
| WUN-10 | Program lead | show me the real, current state of the project in dashboards and decks, and tell me when what I am looking at is stale | I make decisions on today's state, not last month's | T2 | tests | project-console loaders/views (freshness badges) + md-deck rendering |
| WUN-11 | Team member | sync shared tooling without silently overwriting my local improvements, and show me at a glance whether I am in step with the team | no one's work is lost to a sync and drift is visible before it causes confusion | T2 | tests | sync-skills three-way merge analysis (LOCAL_AHEAD protection) + status action |
| WUN-12 | Security officer | screen every tool added to the workbench for hostile behavior and stop unapproved tools from operating unnoticed | a compromised or unvetted skill cannot reach project data silently | T2 | tests | secops static artifact scanner + project.yml security allowlists + SessionStart posture check |
| WUN-13 | Quality engineer | capture at any moment exactly which tool versions and environment the team is working with | I know what configuration was validated and when to revalidate | T2 | tests | per-skill version frontmatter/VERSION files + the validation runner's per-run configuration baseline |
| WUN-14 | Auditor (internal / external) | let me trace, for any AI-assisted change to a controlled document, when it happened, under which task, and who approved it | AI assistance never weakens the audit trail of the controlled record | T1 | process-control | git/PR history + AI-changelog provenance rows + task-first workflow |
| WUN-15 | Document control specialist | move documents between the repo and the formal systems (Confluence, Google Docs) without corrupting content, images, or review state in transit | the controlled copy in the formal system is faithful to what was reviewed | T1 | tests | change-control adopt/publish pipeline + review tiers (frozen-state hook currently a stub — see known anomalies) |
| WUN-16 | Document control specialist | prove that adopting and publishing a controlled page works against our real Confluence and Jira when the workbench is connected to them, not only against a simulation | we rely on integration evidence from the actual systems of record, not a stand-in | T1 | exploratory | change-control adopt/publish over the Atlassian MCP server (agent-mediated) + REST/cookie bridge; jira-pull search over MCP |
| WUN-17 | Marketing / communications lead | publish an external-facing document with every internal note, evidence block and draft metadata removed, and refuse to publish if any internal marker survives | nothing meant for internal eyes ever leaves the building in a white paper, article or brief | T1 | tests | public-doc strip_internal.py (verifies no marker survives; exit 2 on a surviving marker, 3 on a malformed block) + lint_doc.py |
| WUN-18 | Program lead | tell me when a knowledge pack shared with an external assistant platform has drifted from the repository documents it was built from, and refuse to build a pack whose sources are missing | an outside team is never working from stale or contradicted project knowledge | T2 | process-control | knowledge-pack-export build_pack.py validate + freshness_check.py |
| WUN-19 | Commercial analyst | block approval of a business answer whose numbers are not each traceable to a pinned data snapshot, assumption, derivation or config value, or whose snapshot is stale without a waiver | no figure reaches leadership or a customer without a resolvable, current source | T1 | process-control | commercial.py lint (claim markers) + check (edition integrity, approved-lint, freshness, corpus chain) + corpus.py check |
| WUN-20 | Regulatory affairs lead | stop a submission package from being marked transmittable while any cross-document inconsistency, unresolved [VERIFY] tag or scope violation remains | what we send to the regulator is internally consistent and contains no unverified claim | T1 | tests | submissions check_package_consistency.py (--transmit-gate), qsub_scope_lint.py, estar_lint.py, provenance reconciliation |
| WUN-21 | Program lead | carry every strategy decision and lesson tagged in a task document into the shared strategy documents and lessons ledger, and tell me about any tagged block it could not harvest | a decision made during task work is never silently lost between the task and the durable record | T2 | process-control | strategy scan/assemble/validate + lessons scan/assemble/validate (agent-executed procedures; no deterministic harvester script today) |
| WUN-22 | Team member | start every session with an accurate security posture, a briefing that reflects the team's actual recent activity, and recovery of any task left uncheckpointed | I never begin work on a wrong picture of the project or lose an interrupted task | T2 | process-control | SessionStart hooks: security-assert.sh (16 checks), session-briefing.sh, checkpoint-recover.sh, taxonomy-freshness.sh; digest |
| WUN-23 | Program lead | attribute the team's assistant spend to the task that was active when it was incurred, and never report a number it did not measure | cost per task is real, and an unmeasured slot reads as unknown rather than zero | T3 | process-control | task-activate.sh activation ledger + usage-metrics collect.py / aggregate.py (null for unmeasured) + publish hook |
| WUN-24 | DHF author | convert a formal document to markdown and back without losing content, images, cross-references or requirement metadata, and tell me when fidelity could not be verified | the working copy and the controlled file always say the same thing | T1 | process-control | docflow verify_conversion_fidelity.py + validate_phase7.py quality gates + round-trip frontmatter (scripts exist; no fixture-based regression suite yet) |
| WUN-25 | Reviewer / approver | ground every advisor answer and every search result only in canonical project sources, never in audience explainers, personal work folders or exported packs | advice and findings rest on the controlled record, not on a retelling of it | T1 | process-control | file-locator corpus_excludes (articles/**, **/_work/**, _scratch) + advisors three-tier grounding (render idempotence exercised by TC-04) + articles-not-canonical rule |
| WUN-26 | Quality engineer | trust the validation tooling itself — its runner, report and verdict rules — to the same standard as the tools it validates | a PASS on this report is evidence, not an artifact of an untested checker | T2 | tests | workbench-validation tests/test_runner_renderer.py (need-format lint, frontmatter parsing, story composition, NOT-APPLICABLE verdicts, end-to-end synthetic manifest); every run pins manifest + test sources by sha256 |
| WUN-27 | Quality engineer | tell me when a trace link between user needs, design inputs, outputs and verification is broken or one-directional, or when the Jira mirror and the trace matrix disagree | traceability gaps are found by our own run, not by the reviewer | T1 | tests | trace-matrix integrity checks + jira-pull drift rules (A/B/C categories) |
| WUN-28 | Program lead | keep the submission tracker's rows, statuses and draft actions consistent with its own inventory, so that every row I can act on actually works | the readiness dashboard the team steers by is not lying about what exists or what can be drafted | T2 | tests | tracker generate / render / build-draft-context wiring (md-only rows merged into the inventory) |
| WUN-29 | Document control specialist | keep a frozen controlled document frozen — refuse edits to it from inside the workbench until it is formally unfrozen | a document under formal review or released cannot drift while its approval is in flight | T1 | process-control | change-control lifecycle states + hooks/pre_tool_use_frozen.py (designed; currently a stub that exits 0 — see known anomalies) |

## 4a. Canonical data layer & customer-QMS transforms

The validation framework is deliberately **data-first and general-purpose**. The
canonical layer is machine-readable: `validation.yml` (roles, needs, tiers,
coverage, controls, test catalog), `results/<run-id>.json` (statuses + configuration
baseline), `results/<run-id>/*.log` (per-case execution evidence), and the console
sidecar JSON. The markdown validation report is **one generated projection** of that
data — not the data itself.

This is what makes the package portable: a customer QMS that requires its own
validation-report form (a specific FORM template, column set, or sign-off layout)
gets a **new transform over the same canonical data**, not a rewrite of the
validation itself. Needs, evidence, and verdicts survive unchanged; only the
rendering is customer-specific. Never author content directly in the report — it
would be lost on regeneration and would fork the data from its projections.

## 5. Assurance of LLM-driven behavior (honesty statement)

Deterministic components (hooks, scripts, lints, renderers) are tested scripted and
repeatably. LLM-driven behavior (drafting, judgment, advisory output) is **not
repeatably testable** and is never mapped to a scripted PASS. It is assured by
process controls, named per-need in the manifest: mandatory human review before
record entry; deterministic gates wrapped around the non-deterministic core
(WUN-04/07/08/09); grounding rules (`ground-in-contracts`, `readme-before-write`,
no-fabrication + `[VERIFY]` policy, `doctype-governance`); and the git/PR audit trail
(WUN-14). WUN-05 is `exploratory`: reference-audit runs are LLM-driven verification
whose own quality is assured by spot-check re-derivation against byte-correct
sources, recorded per run in `docs/_analysis/`.

## 6. Configuration baseline & revalidation triggers

**Environment record.** Every run writes the canonical setup record into its results JSON (`environment:`), and the report and console render it in full as an expandable section: configuration under test (commit, branch, dirty-file list, per-skill version with frontmatter/`VERSION` disagreements flagged, hooks, agents, rules), runtime (Python, OS, architecture, host, harness version, model identifier), tooling (every binary a case requires — resolved path and version — plus the test-harness package versions actually resolved), connections (declared tier per external system, MCP servers approved/configured, reachability probe of any declared endpoint) and isolation (environment variables stripped or set for cases, socket-guard posture, working directory). A verdict is only interpretable together with this record; two records compared field by field are what turns "re-run needed" from a hunch into a diff.

**Run of record.** A run counts as the run of record only when it carries no warnings: clean working tree at a committed SHA, model identifier captured (`--model-id`), no ambiguous skill version pin, every case carrying an `endpoint:` tier. A run with warnings is a debugging run — useful, but not evidence.

**Revalidation triggers** (canonical list lives in `validation.yml` `revalidation_triggers:` and is rendered into the report):

- any `.claude/` diff since the recorded commit — affected cases; a full run before a run of record;
- model or harness version change — full run plus exploratory review of Tier-1 LLM paths;
- tooling change (any recorded binary or package version differs) — full run;
- connection declaration change (`connections:` flips, or a declared endpoint's reachability changes) — the affected `live` cases and the WUN-16 probe record;
- `project.yml` security/config change; intended-use change; the internal-audit cycle.

## 7. Evidence tiers and hermeticity

Every test case declares what it touched — `endpoint: none | mocked | live`:

| Tier | What it proves | Hermetic | Runs here |
|---|---|---|---|
| `none` | Pure logic, hooks, renderers — no external system | yes | always |
| `mocked` | The real client code paths against a fake Jira/Confluence transport with canned payloads (pagination, auth failure, graceful degradation, ADF splice) | yes | always |
| `live` | The integration against the deployment's real endpoint | no | only where `connections:` declares the endpoint |

The manifest's `connections:` block states what this deployment has (`jira`, `confluence`, `browser` — all `none` for this project). A `live` case whose connection is declared `none` is reported **NOT-APPLICABLE**: a statement about the deployment, not a gap, and it never lowers a need or the overall verdict. A connection declared present but unreachable is a real SKIP or FAIL. Each need carries a plain-language "strongest evidence" line so a reader can tell mock-verified from live-verified at a glance.

**Hermeticity rule.** A `none` or `mocked` case may not depend on the live network, live browser cookies, or unpinned live project content. The skills' own suites enforce the first two with a `conftest.py` socket guard that blocks socket connections outside the `live` marker; where a case deliberately checks a property of this project instance (for example, that every dashboard row with a Create Draft button can build a draft bundle), the case says so in its `approach:` and skips cleanly in a bare checkout.

**MCP-mediated paths.** Where an integration runs through an MCP server, the agent makes the call, not a script; those paths cannot be pytest-live. They are `exploratory` needs (WUN-16) assured by recorded live probes — a scripted transcript with expected outcomes, re-run whenever a deployment declares a connection — and are never reported as a scripted PASS.

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| 2026-07-27 | BX / AI Assistant | task 110: initial plan — 6 intended-use classes, 3 risk tiers, 15-need WUN register, LLM-honesty model, baseline + revalidation triggers. |
| 2026-09-08 | BX / AI Assistant | task 119: §6 rewritten around the full environment record and the run-of-record rule; new §7 evidence tiers (`none`/`mocked`/`live`, `connections:`, NOT-APPLICABLE semantics), hermeticity rule, MCP-mediated paths as exploratory (WUN-16). |
| 2026-09-08 | BX / AI Assistant | task 120: §4 register rewritten as user stories (role / I need the workbench to… / so that…), regenerated from the manifest; WUN-16 included. |
| 2026-09-08 | BX / AI Assistant | task 120: register scrub against all installed skills and their coordinated chains — 13 needs added (WUN-17…29: external publishing, knowledge packs, business-answer gate, submission transmit gate, strategy/lessons harvest, session-start truth, cost attribution, conversion fidelity, grounding, the validation tooling itself, trace/Jira drift, tracker consistency, frozen documents); WUN-06 narrowed to document coverage; WUN-15 freeze half split out; WUN-10 raised to T2. Coverage stated honestly: 4 new `tests` needs backed by executables (TC-22, TC-25, TC-26 + remapped cases), the rest process-control. |
