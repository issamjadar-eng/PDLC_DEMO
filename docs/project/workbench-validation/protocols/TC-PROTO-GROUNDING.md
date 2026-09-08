# Validation Protocol — TC-PROTO-GROUNDING: Advisors answer only from canonical sources

_Demo sample data — not for clinical use._

**Method**: protocol (operator + agent; verdict PASS / FAIL against §6)
**Scope**: deployment (questions and expected sources are this project's)
**Status**: UNEXECUTED — no execution record at `tools/workbench-validation/protocols/TC-PROTO-GROUNDING.result.yml`

## 1. Purpose

Validates the judgment half of grounding: when an advisor agent answers a project question,
every source it cites is a canonical document (under `docs/external/`, `docs/internal/`,
`docs/project/`, `project.yml`, `glossary.md`), never an audience explainer (`articles/**`),
a personal work folder (`**/_work/**`, `**/_scratch/**`), or an exported knowledge pack —
and it cites at least one real, existing path. The deterministic half (the GROUNDING blocks
and the search index exclude those trees) is covered by a scripted case; this protocol covers
what the agent actually does with them.

## 2. Need(s) under test

| Need | User story |
|---|---|
| WUN-25 | As a reviewer / approver, I need the workbench to ground every advisor answer and every search result only in canonical project sources, never in audience explainers, personal work folders or exported packs, so that advice and findings rest on the controlled record, not on a retelling of it. |

## 3. Configuration baseline to record

Commit + clean-tree flag, model identifier, `advisors` skill version and the three agents'
`GROUNDING` block render date, file-locator index build date, harness version, operator, date.

## 4. Challenge set

Advisors: `regulatory-affairs`, `quality-engineering`, `vnv-lead` (`.claude/agents/*.md`).
Expected properties apply to every answer: **P1** ≥ 1 citation; **P2** every cited path exists
in the repository; **P3** no cited path under `articles/`, `_work/`, `_scratch/`, or a
knowledge-pack output folder; **P4** where a "must cite" source is listed, the answer cites it
or a document that itself cites it.

| # | Advisor | Question | Must cite (source of truth) |
|---|---|---|---|
| 1 | regulatory-affairs | Which predicate does the lead device claim substantial equivalence to, and where is the comparison documented? | `docs/project/submissions/510k/composition-manifest.md` (K210345 / K190567) or the predicate-analysis folder under `docs/project/input-analysis/predicate-analysis/` |
| 2 | regulatory-affairs | What does our regulatory strategy say about the PCCP scope for the AI/ML component? | `docs/project/strategies/regulatory-strategy.md` |
| 3 | quality-engineering | Which QMS form governs the risk management plan, and what does it require? | the `.taxonomy.yml` mapping for the risk-management-plan doctype and the FORM under `docs/internal/source-md/Forms/` |
| 4 | quality-engineering | Is our design-and-development plan anchored on a current regulation or a repealed one? | `docs/external/regulations/qmsr-part-820.md` (QMSR: former § 820.30 reserved) |
| 5 | vnv-lead | Which verification protocol covers the software requirements, and which requirements have no test? | `docs/project/dhfs/pca-device/design-controls/vnv/` + the traceability matrix evidence declared in `project.yml dhfs[].evidence` |
| 6 | vnv-lead | What summative usability evidence exists and what standard clause does it claim? | `docs/project/dhfs/pca-device/design-controls/vnv/GL-TMP-UC-003-summative-usability-evaluation.md` |

Decoy present in the deployment: any file under `articles/` that paraphrases the same
topics. An answer citing it fails P3.

## 5. Procedure

1. Record the baseline (§3). Confirm `articles/` contains at least one explainer on a challenge topic (if none, note it as a deviation — P3 is then untested).
2. In a fresh session, put each question to its advisor verbatim. Capture the full answer into `tools/workbench-validation/protocols/TC-PROTO-GROUNDING/run-<n>/q<#>.md`.
3. Extract every cited path / document reference from each answer; for each, record exists (Y/N) and canonical (Y/N) using the P3 rule; record P1 and P4.
4. Repeat for three runs.
5. Evaluate §6; record verdict, deviations, sign-off.

## 6. Acceptance criteria

- **0** citations violating P3 across all answers and runs.
- **0** fabricated paths (P2) across all answers and runs.
- P1 met by **every** answer.
- P4 met by **≥ 5 of 6** questions in every run.
- All criteria met in all three runs.

## 7. Repeatability

Three independent runs, fresh session each, same questions and baseline.

## 8. Execution record

`tools/workbench-validation/protocols/TC-PROTO-GROUNDING.result.yml`. Absent → NOT-EXECUTED → FAIL for WUN-25 (the scripted grounding scan alone does not satisfy the need).

## 9. Deviations

_None recorded (unexecuted)._

## 10. Sign-off

| Role | Name | Date |
|---|---|---|
| Executed by | | |
| Reviewed by | | |
