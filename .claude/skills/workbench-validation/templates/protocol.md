# Validation Protocol — <TC-ID>: <plain-language title>

<banner — for demonstration projects: _Demo sample data — not for clinical use._>

**Method**: protocol (executed by an operator with the agent; verdict PASS / FAIL against the acceptance criteria below)
**Scope**: capability | deployment
**Status**: UNEXECUTED — no execution record exists yet at `tools/workbench-validation/protocols/<TC-ID>.result.yml`

## 1. Purpose

_One paragraph: which workbench behaviour this protocol validates and why a scripted test cannot (the outcome is the assistant's judgment, an agent-mediated integration, or a human-in-the-loop step)._

## 2. Need(s) under test

| Need | User story |
|---|---|
| WUN-xx | As a <role>, I need the workbench to <outcome>, so that <purpose>. |

## 3. Configuration baseline to record

Record at execution start, in the result file:

- repository commit (`git rev-parse HEAD`) and whether the tree is clean
- model identifier operating the workbench
- versions of the skills / agents under test (`SKILL.md` frontmatter `version`)
- harness version, operator, date

## 4. Challenge set

_Fixed inputs with known expected outcomes. The expected outcome must be derivable from a named source of truth, never from a prior run of the tool._

| # | Input | Expected outcome | Source of truth |
|---|---|---|---|
| 1 | | | |

## 5. Procedure

1. Confirm the configuration baseline (§3) and record it.
2. For each challenge item, run <the action> exactly as a user would; capture the tool's output verbatim into the evidence folder.
3. Compare each output to the expected outcome; record match / mismatch per item.
4. Repeat steps 2–3 for the number of runs in §7.
5. Evaluate §6; record the verdict and any deviations (§9); sign off (§10).

## 6. Acceptance criteria

_Explicit, numeric, and independent of the operator's opinion._ Examples:

- 0 known-negative items judged positive (no false pass)
- ≥ 95 % of known-positive items judged positive
- every criterion met in **every** run of §7

## 7. Repeatability

_Number of independent runs (e.g. 3) and what may vary between them (nothing but the run index; same baseline, same challenge set)._

## 8. Execution record

Results are recorded in `tools/workbench-validation/protocols/<TC-ID>.result.yml` (schema: the skill's `templates/protocol-result.yml`). The validation runner reads the file: `verdict: PASS|FAIL` becomes the case status; an absent file is reported **NOT-EXECUTED**, which counts as FAIL for the need.

## 9. Deviations

_Any departure from §5 during execution, with rationale and impact on the verdict._

## 10. Sign-off

| Role | Name | Date |
|---|---|---|
| Executed by | | |
| Reviewed by | | |
