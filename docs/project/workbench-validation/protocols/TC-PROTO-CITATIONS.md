# Validation Protocol — TC-PROTO-CITATIONS: Citation verification tells the truth

_Demo sample data — not for clinical use._

**Method**: protocol (operator + agent; verdict PASS / FAIL against §6)
**Scope**: deployment (challenge set drawn from this project's documents and distilled sources)
**Version**: v2 (2026-09-08) — answer key and grouping revised after the v1 execution of 2026-09-08 (see § 11)
**Status**: v1 EXECUTED 2026-09-08 → FAIL (record `tools/workbench-validation/protocols/TC-PROTO-CITATIONS.result.yml`); v2 not yet executed

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

Expected verdicts use the `citations` engine's **deterministic paywalled-standard band rule** (reference-audit v6 / `citations-external-researcher` rows 1–8): a paywalled ISO/IEC clause with two-tier agreement is `sound-by-distillation` (band **sound**); a clause under the IEC 62366-1 clause-numbering quarantine is `ambiguous-source` (band **unverified**) regardless of what the body text says; a label absent from an enumerated skeleton is `citation-absent-from-source`; a label absent where the aid does not inventory that part is `ambiguous-source`. Source-md-backed references (FDA guidance, CFR) are judged against source-md.

Groups: **S** = known-sound (expected band `sound`), **U** = known-unverified (expected band `unverified`, exact kind stated), **B** = known-broken (expected band `broken`, exact kind stated).

| # | Group | Citation (as it appears / would appear) | Where | Expected kind (band) | Source of truth |
|---|---|---|---|---|---|
| 1 | S | ISO 14971:2019 §4.4 (risk management plan) | `docs/project/dhfs/pca-device/design-controls/plans/GL-TMP-RM-001-risk-management-plan.md` L22 | `sound-by-distillation` (sound) | L1a `standards/iso-14971.md` L31 "4.4 Risk Management Plan"; L1b `docs/external/standards/iso-14971.md` L29 — two-tier agreement, no quarantine |
| 2 | S | IEC 62304 §5.1 (software development planning) | `.../plans/GL-TMP-SW-001-software-development-plan.md` L22 | `sound-by-distillation` (sound) | L1a `iec-62304.md` L58; L1b L27 |
| 3 | U | IEC 62366-1 §5.1 (use specification) | `.../user-needs/GL-TMP-UC-001-use-specification.md` L22 | `ambiguous-source` (unverified) | L1a `iec-62366-1.md` L9 clause-numbering quarantine banner — band rule row 1 applies even though the audited sequence agrees |
| 4 | S | ISO 14971 §5.1 (risk analysis process) — constructed positive | operator-supplied test document | `sound-by-distillation` (sound) | L1a `iso-14971.md` L46–52; L1b L44–50 (the L1b `[VERIFY]` at L167 is a document-level caveat, not a clause quarantine) |
| 5 | S | IEC 62304 §5.8 (software release) — constructed positive | operator-supplied | `sound-by-distillation` (sound) | L1a `iec-62304.md` L107; L1b L76 |
| 6 | U | IEC 62366-1 §5.2 (use-related risk analysis) — constructed | operator-supplied | `ambiguous-source` (unverified) | L1a L9 quarantine (real 5.2 = UI characteristics related to safety; the aid's "5.2 Use-Related Risk Analysis" label is invented) — v1 expected `sound`; that expectation was itself built on the invented label |
| 7 | B | FDA Q-Submission guidance, section "Pre-Submission Package Contents" — constructed | operator-supplied | `citation-mislabeled` (broken) | source-md `fda-guidance/source-md/qsub.md` has no such heading; content is III.B(1) "Submission Content" (L82, L720) and III.B(4)(a)(1) "Additional Recommended Submission Contents" (L1116). The aids that carried the invented label were relabeled 2026-09-08 — a citer using the old label is now mislabeled by construction |
| 8 | S | Internal link to `510k/composition-manifest.md` | `docs/project/submissions/submission-tracker.md` L16 | `sound` (sound) | file exists: `docs/project/submissions/510k/composition-manifest.md`. v1 wrote the href as `../510k/…`, which resolved to the non-existent `docs/project/510k/` — the engine correctly returned `broken-link`; the href was fixed 2026-09-08 |
| 9 | S | IEC 62304 §4.3 (software safety class C) | `.../requirements/software-requirements.md` L14 | `sound-by-distillation` (sound) | L1a `iec-62304.md` L23 heading "4.3 Software Safety Classification (as amended by A1:2015)" — the label exists; the L31 `[VERIFY]` covers sub-clause lettering only (does not trigger quarantine); L1b L13/L165 cover the topic. v1 expected `citation-mislabeled` on the basis of the L1b file alone — wrong |
| 10 | B | 21 CFR 820.30(b) (design & development planning) | `.../plans/GL-TMP-DC-001-design-and-development-plan.md` L22 | `stale-citation` (broken) | source-md `regulations/source-md/21-cfr-part-820.md` L113: §§ 820.20–820.30 [Reserved] under the QMSR; L1b `qmsr-part-820.md` L22 |
| 11 | U | ISO 13485 §7.3.2 (design planning) | same document, L22 | `registry-gap` (unverified) | no ISO 13485 distillation in L1a or L1b (both READMEs now state the gap) |
| 12 | U | IEC 62366-1 §5.9 (summative evaluation) | `.../vnv/GL-TMP-UC-003-summative-usability-evaluation.md` L22 | `ambiguous-source` (unverified) | L1a L9 quarantine — the banner's audited sequence places summative at 5.9, so the citation is probably right, but the rule forbids a local `sound` or `broken`; v1 expected `citation-absent-from-source` from the aid's body text — wrong |
| 13 | B | ISO 14971 §4.9 — constructed | operator-supplied | `citation-absent-from-source` (broken) | L1a `iso-14971.md` L17–44 enumerates Clause 4 as 4.1–4.5 (complete skeleton) — band rule row 5 |
| 14 | U | IEC 62366-1 Annex Q — constructed | operator-supplied | `ambiguous-source` (unverified) | L1a names only Annex C and carries no annex inventory — band rule row 6 (absence in a finding aid is not proof); v1 expected `citation-absent-from-source` |
| 15 | B | IEC 62304 §5.1 cited for "the risk management file shall be maintained" — constructed wrong predicate | operator-supplied | `stale-citation` (broken) | §5.1 is software development planning; RMF maintenance is ISO 14971 §4.5 |
| 16 | B | Link to `docs/project/dhfs/pca-device/design-controls/plans/GL-TMP-RM-999-nonexistent.md` — constructed | operator-supplied | `broken-link` (broken) | path does not exist |

S = {1, 2, 4, 5, 8, 9} (6 items) · U = {3, 6, 11, 12, 14} (5) · B = {7, 10, 13, 15, 16} (5).

## 5. Procedure

1. Record the baseline (§3).
2. Assemble the operator-supplied items (4–7, 13–16) into one markdown test document under `tasks/<person>/_scratch/` with each citation in its own paragraph; keep items 1–3 and 8–12 in their real documents.
3. Run `/reference-audit` over the test document and over each real document named above (or the `citations` advisor in point-query mode per citation). Capture the findings reports verbatim into `tools/workbench-validation/protocols/TC-PROTO-CITATIONS/run-<n>/`.
4. For each of the 16 items record: expected verdict, returned verdict, match (Y/N). Treat `unverified`-band verdicts (`unreachable-source`, `ambiguous-source`, `registry-gap`) as **non-sound**; the criteria below only require that a known-non-sound item is never reported `sound` and that a known-sound item is reported `sound`.
5. Repeat steps 3–4 for three runs (§7).
6. Evaluate §6; record verdict, deviations, sign-off.

## 6. Acceptance criteria

- **A.** **0** items of groups U or B reported band `sound` in any run.
- **B.** **≥ 5 of 6** group-S items reported band `sound` in every run (one miss permitted per run; the missed item must be recorded and adjudicated).
- **C.** Group-B kinds match the expected kind in **≥ 4 of 5** items in every run; group-U items are band `unverified` in every run (kind recorded; a kind mismatch within `unverified` is noted, not failed).
- **D. Repeatability (new in v2).** For every item, the **band** is identical across all three runs. This criterion exists because v1 execution found the band drifting for the same evidence.
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

## 11. Revision history

| Version | Date | Change | Why |
|---|---|---|---|
| v1 | 2026-09-08 | Initial protocol (task ben/121). | — |
| v2 | 2026-09-08 | Answer key regrouped into S / U / B with exact expected kinds; items 3, 6, 12, 14 → `ambiguous-source` (quarantine / no annex inventory); item 7 → `citation-mislabeled`; item 9 → `sound-by-distillation`; item 8 keeps `sound` after the tracker href fix; criterion D (band repeatability) added. | v1 executed 2026-09-08 (three runs, FAIL): (a) the engine's band for paywalled clauses drifted between runs — fixed in reference-audit v6 with a deterministic band rule, which v2 encodes; (b) four answer-key entries were wrong (7: heading existed only in finding aids; 8: the href really was broken; 9: L1a carries the 4.3 label; 12/14: the aid's body text is quarantined / not an inventory). Registry defects fixed alongside: L1b `iec-62366-1.md` re-synced with the quarantine banner; qsub aid headings relabeled to the source-md sections; ISO 13485 gap stated in both tier READMEs. Deviations recorded in `TC-PROTO-CITATIONS.result.yml`. |
