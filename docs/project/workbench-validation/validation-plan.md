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

Each need is stated **from a role's perspective, in the role's own language** — the
outcome the role requires, deliberately free of implementation detail (the role does
not know or care how the workbench meets the need). The mechanism appears only in
the *Implemented by* column, as traceability information — it is not part of the
need and may change without the need changing.

Machine-readable copy: `validation.yml` (`user_needs:`) — the manifest is what the
runner and report consume; keep both in sync.

| ID | Role | Need | Tier | Coverage | Implemented by (traceability) |
|---|---|---|---|---|---|
| WUN-01 | DHF author | When I draft a controlled document, its structure must come out matching what the governing QMS form requires — without me having to remember the form's rules | T1 | process-control | medtech-docs scaffolding + `.taxonomy.yml` doctype governance + regulatory-authoring workflow |
| WUN-02 | Reviewer / approver | I can always tell which content in a controlled document came from the AI assistant and which content a human wrote or approved | T1 | process-control | AI-changelog metadata blocks + working-vs-formal split + PR history |
| WUN-03 | Regulatory affairs lead | If the toolchain could not verify a claim it drafted, that claim is visibly flagged for me — never silently asserted as fact | T1 | process-control | `[VERIFY]` flag convention + no-fabrication policy + mandatory reference audit on citation-bearing edits |
| WUN-04 | DHF author | Before my document goes out for review, mechanical writing defects (leaks, jargon, clutter, undefined terms) are caught automatically and reliably | T1 | tests | writing-well + regulatory-authoring deterministic lint scripts |
| WUN-05 | Quality engineer | When a document cites a standard, guidance, or internal source, I get a trustworthy answer on whether the citation really matches the source text | T2 | exploratory | reference-audit skill + citations advisor |
| WUN-06 | Quality engineer | If our documentation drifts from its declared structure, traceability, or tracker baseline, I find out from our own audit run — not from an external auditor | T2 | tests | dhf-manifest coverage audit + trace-matrix graph checks + tracker validation + jira-pull drift rules |
| WUN-07 | Program lead | No project file gets changed without being anchored to a tracked task, so every change is traceable to why it was made | T1 | tests | task-gate PreToolUse hook with exempt-path list |
| WUN-08 | Quality engineer | Documents cannot be converted outside the controlled conversion pipeline without a deliberate, visible override | T1 | tests | docflow conversion-block PreToolUse hook + override marker |
| WUN-09 | DHF author | Auto-generated sections of my documents always reflect the current source of truth, and never damage the text I wrote by hand around them | T1 | tests | sentinel-block renderer + advisor grounding renderer (idempotent) |
| WUN-10 | Program lead | Dashboards and decks show me the real, current state of the project — and tell me when what I'm looking at is stale | T3 | tests | project-console loaders/views (freshness badges) + md-deck |
| WUN-11 | Team member | When I sync shared tooling, my local improvements are never silently overwritten, and I can see at a glance whether I'm in step with the team | T2 | tests | sync-skills three-way merge analysis + status action |
| WUN-12 | Security officer | Any tool added to the workbench is screened for hostile behavior, and unapproved tools cannot operate unnoticed | T2 | tests | secops static scanner + project.yml allowlists + SessionStart posture check |
| WUN-13 | Quality engineer | At any moment I can capture exactly which tool versions the team is working with, so I know what configuration was validated and when to revalidate | T2 | tests | version frontmatter/VERSION files + the runner's per-run configuration baseline |
| WUN-14 | Auditor (internal / external) | For any AI-assisted change to a controlled document, I can trace when it happened, under which task, and who approved it | T1 | process-control | git/PR history + AI-changelog rows + task-first workflow |
| WUN-15 | Document control specialist | When documents move between the repo and the formal systems (Confluence, Google Docs), nothing gets corrupted in transit — and frozen documents stay frozen | T1 | tests | change-control adopt/publish pipeline + review tiers (frozen-state hook currently a stub) |

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

The runner records per run: repository git SHA + dirty flag, per-skill versions
(SKILL.md frontmatter + VERSION files), installed hooks, platform/python, and the
model identifier when available (recorded in the validation evidence only — the
vendor-neutrality rule governs controlled document content, not validation records).

Revalidation triggers: skill/agent/hook file change (skill-tree SHA moves);
underlying model or agent-platform version change (behavior changes with zero repo
diff); `project.yml` security/config change; intended-use change; periodic — per
internal-audit cadence (GL-SOP-QM-004).

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| 2026-07-27 | BX / AI Assistant | task 110: initial plan — 6 intended-use classes, 3 risk tiers, 15-need WUN register, LLM-honesty model, baseline + revalidation triggers. |
