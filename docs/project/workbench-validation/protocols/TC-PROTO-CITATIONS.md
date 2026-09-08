# Validation Protocol — TC-PROTO-CITATIONS: Citation verification tells the truth

_Demo sample data — not for clinical use._

**Method**: protocol (operator + agent; verdict PASS / FAIL against §6)
**Scope**: deployment (challenge set drawn from this project's documents and distilled sources)
**Status**: UNEXECUTED — no execution record at `tools/workbench-validation/protocols/TC-PROTO-CITATIONS.result.yml`

## 1. Purpose

Validates the reference-audit capability (the `citations` advisor and its researchers, per
`.claude/skills/reference-audit/SKILL.md`): for a cited standard clause, guidance section,
regulation, or internal document, does the workbench return the right verdict? The judgment
is the assistant's (semantic match of claim to source), so it cannot be scripted; it can be
challenged with citations whose truth is known from the byte-correct distilled sources.

## 2. Need(s) under test

| Need | User story |
|---|---|
| WUN-05 | As a quality engineer, I need the workbench to give me a trustworthy answer on whether a cited standard, guidance, or internal source really says what the document claims, so that citations in the controlled record survive an auditor checking them against the source text. |

## 3. Configuration baseline to record

Commit + clean-tree flag, model identifier, `reference-audit` and `medtech-docs` versions,
harness version, operator, date — into the result file.

## 4. Challenge set

Verdict vocabulary is the reference-audit v1.1 enum (`sound`, `broken-link`,
`citation-absent-from-source`, `citation-mislabeled`, `stale-citation`, `unresolved-anchor`,
`unreachable-source`, `ambiguous-source`, `registry-gap`). "Known-sound" items are real
citations in this project whose source exists in `docs/external/`; "known-non-sound" items
are either real project citations that the distilled sources show to be wrong (real
findings — items 9–12) or constructed defects (items 13–16).

| # | Citation (as it appears / would appear) | Where | Expected verdict | Source of truth |
|---|---|---|---|---|
| 1 | ISO 14971:2019 §4.4 (risk management plan) | `docs/project/dhfs/pca-device/design-controls/plans/GL-TMP-RM-001-risk-management-plan.md` L22 | `sound` | `docs/external/standards/iso-14971.md` heading `#### 4.4 Risk Management Plan` |
| 2 | IEC 62304 §5.1 (software development planning) | `.../plans/GL-TMP-SW-001-software-development-plan.md` L22 | `sound` | `docs/external/standards/iec-62304.md` `#### 5.1 Software Development Planning` |
| 3 | IEC 62366-1 §5.1 (use specification) | `.../user-needs/GL-TMP-UC-001-use-specification.md` L22 | `sound` | `docs/external/standards/iec-62366-1.md` `#### 5.1 Use Specification` |
| 4 | ISO 14971 §5.1 (risk analysis process) — constructed positive: "risk analysis is performed per ISO 14971 §5.1" | operator-supplied test document | `sound` | `iso-14971.md` `#### 5.1 Risk Analysis Process` |
| 5 | IEC 62304 §5.8 (software release) — constructed positive | operator-supplied | `sound` | `iec-62304.md` `#### 5.8 Software Release` |
| 6 | IEC 62366-1 §5.2 (use-related risk analysis) — constructed positive | operator-supplied | `sound` | `iec-62366-1.md` `#### 5.2 Use-Related Risk Analysis` |
| 7 | FDA Q-Submission guidance, "Pre-Submission Package Contents" (cover letter, device description …) — constructed positive | operator-supplied | `sound` | `docs/external/fda-guidance/qsub.md` `### Pre-Submission Package Contents` |
| 8 | Internal link to `../510k/composition-manifest.md` | `docs/project/submissions/submission-tracker.md` L16 | `sound` | file exists: `docs/project/submissions/510k/composition-manifest.md` |
| 9 | IEC 62304 §4.3 (software safety class C) | `.../requirements/software-requirements.md` L14 | `citation-mislabeled` | `iec-62304.md` carries safety classification under `## Safety Classification (Amd 1:2015)`, no `4.3` label |
| 10 | 21 CFR 820.30(b) (design & development planning) | `.../plans/GL-TMP-DC-001-design-and-development-plan.md` L22 | `stale-citation` | `docs/external/regulations/qmsr-part-820.md` L22: former § 820.30 is `[Reserved]` under the QMSR |
| 11 | ISO 13485 §7.3.2 (design planning) | same document, L22 | `registry-gap` | no `iso-13485.md` in `docs/external/standards/` nor in `.claude/skills/medtech-docs/references/standards/` |
| 12 | IEC 62366-1 §5.9 (summative evaluation) | `.../vnv/GL-TMP-UC-003-summative-usability-evaluation.md` L22 | `citation-absent-from-source` | `iec-62366-1.md` clause headings end at `#### 5.7`; no `5.9` label |
| 13 | ISO 14971 §4.9 — constructed: "per ISO 14971 §4.9 the risk management file shall …" | operator-supplied | `citation-absent-from-source` | `iso-14971.md` has no clause 4.9 |
| 14 | IEC 62366-1 Annex Q — constructed: "Annex Q provides the summative sample-size table" | operator-supplied | `citation-absent-from-source` | no Annex Q in `iec-62366-1.md` |
| 15 | IEC 62304 §5.1 cited for "the risk management file shall be maintained" — constructed wrong predicate | operator-supplied | `stale-citation` | §5.1 is software development planning, not the risk file |
| 16 | Link to `docs/project/dhfs/pca-device/design-controls/plans/GL-TMP-RM-999-nonexistent.md` — constructed | operator-supplied | `broken-link` | path does not exist |

Items 9–12 are also **real findings** about this project's documents; if the protocol is
executed and confirms them, route each to the owning document's task for correction.

## 5. Procedure

1. Record the baseline (§3).
2. Assemble the operator-supplied items (4–7, 13–16) into one markdown test document under `tasks/<person>/_scratch/` with each citation in its own paragraph; keep items 1–3 and 8–12 in their real documents.
3. Run `/reference-audit` over the test document and over each real document named above (or the `citations` advisor in point-query mode per citation). Capture the findings reports verbatim into `tools/workbench-validation/protocols/TC-PROTO-CITATIONS/run-<n>/`.
4. For each of the 16 items record: expected verdict, returned verdict, match (Y/N). Treat `unverified`-band verdicts (`unreachable-source`, `ambiguous-source`, `registry-gap`) as **non-sound**; the criteria below only require that a known-non-sound item is never reported `sound` and that a known-sound item is reported `sound`.
5. Repeat steps 3–4 for three runs (§7).
6. Evaluate §6; record verdict, deviations, sign-off.

## 6. Acceptance criteria

- **0** known-non-sound items (9–16) reported `sound` in any run.
- **≥ 7 of 8** known-sound items (1–8) reported `sound` in every run (one miss permitted per run; the missed item must be recorded and adjudicated).
- For items 9–12 (real defects), the returned verdict kind matches the expected kind in **≥ 3 of 4** items (kind confusion between `citation-absent-from-source` and `citation-mislabeled` is recorded but does not fail the protocol; a `sound` does).
- All criteria met in all three runs.

## 7. Repeatability

Three independent runs, same baseline and challenge set, fresh session each run.

## 8. Execution record

`tools/workbench-validation/protocols/TC-PROTO-CITATIONS.result.yml` per the skill's
`templates/protocol-result.yml`. Absent → NOT-EXECUTED → FAIL for WUN-05.

## 9. Deviations

_None recorded (unexecuted)._

## 10. Sign-off

| Role | Name | Date |
|---|---|---|
| Executed by | | |
| Reviewed by | | |
