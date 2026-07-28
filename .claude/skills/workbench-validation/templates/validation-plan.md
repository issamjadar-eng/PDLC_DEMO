# Workbench Validation Plan — <MedTech Project>

<BANNER — for demonstration projects: _Demo sample data — not for clinical use._ This
validation package is illustrative of method only; clause citations not verified
against licensed source text are flagged [VERIFY].>

## 1. Purpose & scope

Validation of the AI workbench — the `.claude/` toolchain (skills, agents, hooks,
scripts, rules) used to author and manage controlled artifacts — for its intended
uses, proportionate to risk. This validates the **toolchain**, not the device; device
V&V lives in the DHF.

**QMS anchor:** <cite the project's tool-validation SOP/WI, e.g. a Software V&V work
instruction's tool-validation clause; flag [VERIFY] anything cited from standards not
distilled in-project (ISO 13485 §4.1.6, FDA CSA, 21 CFR Part 11).>

## 2. Intended-use classes

| Class | Intended-use pattern | Example tools |
|---|---|---|
| authoring | Draft/structure controlled artifacts; all output human-reviewed before entering the record; the tool does not release, sign, or transmit | <skills> |
| audit | Detect and report nonconformities/gaps; advisory; false negatives are the risk | <skills> |
| gates | Automatically enforce a rule by blocking a tool call; failure mode is silent non-enforcement | <hooks> |
| renderers | Derive display/structural content from a declared source of truth; mechanically reproducible | <scripts> |
| console | Display status for situational awareness; not a decision-of-record system | <console> |
| config-control | Control the workbench configuration itself (versions, allowlists, sync) | <skills> |

## 3. Risk tiers → assurance depth

| Tier | Definition | Assurance |
|---|---|---|
| T1 High | Output enters controlled record, or tool gates record integrity | Scripted tests for deterministic parts; exploratory challenge + process controls for LLM parts; revalidate on version/config change |
| T2 Medium | Advisory detection / config control; false negative degrades quality | Scripted smoke tests; seeded-error spot checks |
| T3 Low | Display/telemetry; errors self-evident | Intended-use note; verified by use |

## 4. Workbench user needs (WUN register)

Each need is stated **from a role's perspective, in the role's own language** — the
outcome the role requires, free of implementation detail. The mechanism appears only
in the *Implemented by* column (traceability, not part of the need).

| ID | Role | Need | Tier | Coverage | Implemented by (traceability) |
|---|---|---|---|---|---|
| WUN-01 | <role> | <plain-language outcome> | T1 | tests / process-control / exploratory | <mechanism> |

_The machine-readable copy of this register lives in `validation.yml` — keep both in
sync (the manifest is what the runner and report consume)._

## 4a. Canonical data layer & customer-QMS transforms

The framework is data-first: the manifest, run-results JSON, and per-case evidence
logs are the canonical machine-readable layer; the markdown report is one generated
projection. A customer QMS needing its own report format gets a new transform over
the same data — the validation itself never has to be redone for formatting.

## 5. Assurance of LLM-driven behavior

Deterministic components are tested scripted and repeatably. LLM-driven behavior is
not repeatably testable and is assured by process controls: mandatory human review
before record entry, deterministic gates wrapped around the non-deterministic core,
grounding rules, and the git/PR audit trail. These needs are labeled process-control
or exploratory in the report — never a scripted PASS.

## 6. Configuration baseline & revalidation triggers

Baseline per run: repository git SHA (+ dirty flag), per-skill versions, installed
hooks, platform/python, model identifier when available. Revalidation triggers: tool
file change, model/platform change, security/config change, intended-use change,
periodic audit cadence.

## Changelog

- YYYY-MM-DD: Initial plan.
