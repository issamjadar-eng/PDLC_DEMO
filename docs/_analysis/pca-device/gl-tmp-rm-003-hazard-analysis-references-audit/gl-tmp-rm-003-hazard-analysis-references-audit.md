---
audit_id: RA-gl-tmp-rm-003-hazard-analysis-001
source_doc: docs/project/dhfs/pca-device/risk-management/GL-TMP-RM-003-hazard-analysis.md
created: 2026-07-14
status: Findings Posted
schema_version: 1
---

# References Audit — PCA-DEVICE-GL-TMP-RM-003-hazard-analysis — Hazard Analysis

**Source doc:** [`docs/project/dhfs/pca-device/risk-management/GL-TMP-RM-003-hazard-analysis.md`](../../../../docs/project/dhfs/pca-device/risk-management/GL-TMP-RM-003-hazard-analysis.md)
**Audit ID:** `RA-gl-tmp-rm-003-hazard-analysis-001`
**Created:** `2026-07-14`
**Status:** `Findings Posted`

This audit verifies that every citation in the source document actually resolves to a real source and that the source supports the cited claim. Findings carry a verdict band (`sound | unverified | broken`) and a finding kind (open enum). External-formal references are verified against both the medtech-docs registry distillation (L1a) and the project applicability layer (L1b) per the "cite both" mandate. See the `reference-audit` skill SKILL.md for the engine contract; see the `citations` advisor for the verdict semantics.

## Summary

| Class | sound | unverified | broken | Total |
|-------|------:|-----------:|-------:|------:|
| external-formal | 4 | 8 | 1 | 13 |
| internal-formal | 8 | 0 | 0 | 8 |
| informal-link | 1 | 1 | 0 | 2 |
| **Total** | **13** | **9** | **1** | **23** |

_Verified 2026-07-14 by the `citations` advisor (batch fan-out, task ben/102). Method note: 13 of 23 verifications were performed directly by the engine after its researcher dispatches failed to return; the remaining 10 carry researcher verdicts unmodified._

## References (Pending Verification)

```yaml
references:
  - {id: E1, class: external-formal, method: regex, target: "ISO 14971:2019 §5", anchor: "Scope paragraph / Standards Anchor", claim: "The document records the ISO 14971 §5 hazard analysis (hazard identification, hazardous situations, risk estimation) for the PP-3500."}
  - {id: E2, class: external-formal, method: regex, target: "ISO 14971:2019 Annex C", anchor: "Scope paragraph / table column header", claim: "Hazards were identified using the ISO 14971 Annex C stimulus classes (energy, biological & chemical, operational, information, environmental)."}
  - {id: E3, class: external-formal, method: regex, target: "IEC 60601-1 (3rd edition + A1)", anchor: "Scope paragraph; HAZ-008/009/016 controls", claim: "IEC 60601-1 hazard clauses informed identification; electrical-safety design (insulation, leakage-current limits, applied-part isolation) and mechanical robustness are per IEC 60601-1."}
  - {id: E4, class: external-formal, method: regex, target: "IEC 81001-5-1 §5", anchor: "Scope paragraph", claim: "The IEC 81001-5-1 §5 threat catalog was used for the connected functions."}
  - {id: E5, class: external-formal, method: regex, target: "IEC 60601-2-24 §201.12.1.101", anchor: "HAZ-001 Verification(s)", claim: "Gravimetric bench flow-rate accuracy testing is performed per IEC 60601-2-24 §201.12.1.101."}
  - {id: E6, class: external-formal, method: regex, target: "IEC 60601-2-24 §201.12.1.103", anchor: "HAZ-004 Verification(s)", claim: "Free-flow (door-open under head pressure) testing is per IEC 60601-2-24 §201.12.1.103."}
  - {id: E7, class: external-formal, method: regex, target: "IEC 60601-2-24 §201.12.4.4.103", anchor: "HAZ-006 Verification(s)", claim: "Occlusion alarm response-time testing is per IEC 60601-2-24 §201.12.4.4.103."}
  - {id: E8, class: external-formal, method: regex, target: "IEC 62366-1", anchor: "HAZ-002 Verification(s)", claim: "Summative usability testing (n≥15 nurses, zero decimal misreads) is per IEC 62366-1."}
  - {id: E9, class: external-formal, method: regex, target: "IEC 60601-1-8", anchor: "HAZ-008 Controls", claim: "The high/medium/low-priority audible alarm scheme with SPL 45–80 dB(A) at 1 m is IEC 60601-1-8-compliant."}
  - {id: E10, class: external-formal, method: regex, target: "IEC 60601-1-2 (4th edition)", anchor: "HAZ-010 Controls", claim: "EMC immunity/emissions design for professional healthcare facility environments is per IEC 60601-1-2 4th edition."}
  - {id: E11, class: external-formal, method: regex, target: "ISO 10993-1 / ISO 10993-5 / ISO 10993-10", anchor: "HAZ-011 Controls + Verification(s)", claim: "Biocompatibility evaluation per ISO 10993-1 with cytotoxicity/sensitization/irritation testing per ISO 10993-5/-10."}
  - {id: E12, class: external-formal, method: regex, target: "21 CFR 801", anchor: "HAZ-014 Verification(s)", claim: "Labeling (incl. patient-only-activation opioid warnings) is reviewed per 21 CFR 801."}
  - {id: E13, class: external-formal, method: llm, target: "FDA premarket cybersecurity guidance", anchor: "HAZ-012 Verification(s)", claim: "Cybersecurity testing incl. penetration test is per IEC 81001-5-1 and FDA premarket cybersecurity guidance."}
  - {id: I1, class: internal-formal, method: regex, target: "GL-WI-RM-001", anchor: "Scope paragraph; Revision History", claim: "Hazards were identified per GL-WI-RM-001 (Hazard Analysis WI)."}
  - {id: I2, class: internal-formal, method: regex, target: "GL-STD-RM-001 §3 / §4 / §5", anchor: "Scope paragraph; scoring columns; Summary", claim: "S, P, and the risk-acceptance regions are taken exclusively from GL-STD-RM-001 §3, §4 and the §5 acceptance matrix; S5 rows cannot reach Acceptable by matrix construction."}
  - {id: I3, class: internal-formal, method: regex, target: "GL-STD-RM-001 §6", anchor: "Summary", claim: "Every pre-control Unacceptable risk is reduced by design or protective measures, not information for safety alone, per GL-STD-RM-001 §6."}
  - {id: I4, class: internal-formal, method: regex, target: "GL-STD-RM-001 §7", anchor: "Summary", claim: "Residual S5 ALARP hazards feed the benefit-risk considerations of GL-STD-RM-001 §7."}
  - {id: I5, class: internal-formal, method: regex, target: "DHF-PP3500-DI-001 (../design-controls/requirements/design-inputs.md) incl. 27 DI IDs + VER-PP3500-BT-005/SW-002/SW-006", anchor: "Scope paragraph; Design Input(s) + Verification(s) columns", claim: "Each hazard traces to implementing design inputs in DHF-PP3500-DI-001; all cited DI-### and VER-PP3500-### identifiers exist there."}
  - {id: I6, class: internal-formal, method: regex, target: "CAPA-2023-001", anchor: "Scope paragraph; HAZ-002 sequence", claim: "The decimal-point misread hazard reflects predicate CAPA-2023-001 heritage."}
  - {id: I7, class: internal-formal, method: regex, target: "../../../../internal/source-md/qms-index.md (GL-TMP-RM-003 link)", anchor: "Header block", claim: "The parent QMS template link resolves to the QMS index."}
  - {id: I8, class: internal-formal, method: llm, target: "GL-SOP-QM-001", anchor: "Frontmatter notes", claim: "Transition to Rev 1.0 happens via GL-SOP-QM-001."}
  - {id: L1, class: informal-link, method: llm, target: "GL-TMP-RM-004 sibling docs (design-fmea / process-fmea)", anchor: "Scope paragraph", claim: "Bottom-up dFMEA/pFMEA in sibling GL-TMP-RM-004 documents link back to these HAZ IDs via their Linked Hazard ID column."}
  - {id: L2, class: informal-link, method: llm, target: "Risk Management Report (GL-TMP-RM-002 instance)", anchor: "Summary", claim: "Residual ALARP risks are dispositioned in the Risk Management Report."}
```

## Findings (broken)

### E4 — IEC 81001-5-1 §5 · `stale-citation` — **RESOLVED 2026-07-14**
- **Claim:** hazards were identified using "the IEC 81001-5-1 §5 threat catalog for the connected functions."
- **Evidence:** both tiers contradict the clause attribution — L1a registry distillation: "Clause 5 — Software Development Process Security Requirements (5.1 planning … 5.8 release)"; threat identification lives in Clause 7: "7.1 Threat Modeling — Identify threat agents … using a systematic method (STRIDE, attack trees)". L1b applicability doc carries the same clause map. Same standard, wrong clause topic.
- **Fix applied:** the source Scope paragraph now cites IEC 81001-5-1 §7.1 (threat modeling). Final wording check against the copyrighted original remains advisable at Rev 1.0.

## Findings (unverified)

### E2 — ISO 14971:2019 Annex C · `ambiguous-source` — [VERIFY] tag added to source
- The L1a distillation characterizes Annex C as safety-characteristic **questions**; it does not enumerate the five class names cited (energy / biological & chemical / operational / information / environmental) — the taxonomy may be edition-dependent (the 2019 edition moved the questions list toward ISO/TR 24971). Fix applied: inline `[VERIFY]` added at the citation; confirm against the original and extend the L1a distillation.

### E3 — IEC 60601-1 (3rd ed + A1) · `ambiguous-source`
- L1b applicability doc exists but every clause line is a `[VERIFY]` placeholder; no L1a distillation. General scope (basic safety / essential performance) plausible; edition designation unconfirmed. Fix: populate the L1b stub + add an L1a distillation; confirm edition against the FDA recognized-standards list.

### E5 / E6 / E7 — IEC 60601-2-24 §201.12.1.101 / §201.12.1.103 / §201.12.4.4.103 · `registry-gap`
- The infusion-pump particular standard has no distillation at either tier (only a `[VERIFY]` list mention in the IEC 60601-1 applicability doc); the three subclause numbers (flow-accuracy, free-flow, occlusion-alarm tests) cannot be verified locally. Fix: add the IEC 60601-2-24 distillation + applicability doc — the single most-cited verification anchor in this DHF.

### E9 — IEC 60601-1-8 · `registry-gap`
- Alarms collateral: topic corroborated by the collateral list only; the priority scheme and the numeric SPL range 45–80 dB(A) at 1 m have no local source. Fix: distillation + applicability doc.

### E10 — IEC 60601-1-2 (4th edition) · `registry-gap`
- EMC collateral: topic corroborated; edition (4th vs 4.1) and the professional-healthcare-facility environment framing unverifiable locally. Fix: distillation + applicability doc.

### E11 — ISO 10993-1 / -5 / -10 · `registry-gap`
- No ISO 10993 distillations at either tier. Note for authoring: in the 2021 revision, irritation moved from ISO 10993-10 to ISO 10993-23 — the "-10 = sensitization/irritation" attribution is edition-dependent.

### L2 — Risk Management Report (GL-TMP-RM-002 instance) · `ambiguous-source` — **RESOLVED 2026-07-14**
- The RMR path resolves but is a Rev 0.1 placeholder (all `{{…}}` template variables; zero matches for HAZ-IDs / "residual" / "ALARP") — the Summary asserted dispositions exist. Fix applied: Summary softened to "will be dispositioned in the Risk Management Report." Authoring the RMR ALARP dispositions (7 residual-ALARP hazards) remains open.

## Findings (sound)

- **E1** ISO 14971:2019 §5 — both tiers map Clause 5 to risk analysis / hazard identification / estimation.
- **E8** IEC 62366-1 — summative-evaluation predicate confirmed by both tiers (the n≥15 / zero-misread figures are project acceptance criteria, not attributed to the standard).
- **E12** 21 CFR 801 — public regulation; Part-level labeling predicate confirmed via L4 (Cornell LII mirror; ecfr/fda fetches blocked). Registry has no Part 801 distillation — extension candidate.
- **E13** FDA premarket cybersecurity guidance — both tiers confirm the four recommended testing types incl. penetration testing.
- **I1** GL-WI-RM-001 — resolves; purpose is HA per ISO 14971 §5 with ISO/TR 24971 §5 guidance.
- **I2** GL-STD-RM-001 §3/§4/§5 — scales + matrix verified; S5 row has no Acceptable cell, confirming the matrix-construction claim; spot-recomputes match.
- **I3** GL-STD-RM-001 §6 — "information alone… not sufficient for Unacceptable" quote-verified.
- **I4** GL-STD-RM-001 §7 — high-severity-ALARP-cluster benefit-risk trigger verified.
- **I5** DHF-PP3500-DI-001 — doc ID matches; 7/7 spot-checked DI IDs + 3/3 VER IDs resolve.
- **I6** CAPA-2023-001 — record exists (decimal-point legibility, closed 2023-05-15, related DI-013/UN-007); "predicate" framing consistent with the canonical layer (domain call, not a defect).
- **I7** qms-index link — resolves; index registers GL-TMP-RM-003 with the matching ISO 14971 §5 anchor.
- **I8** GL-SOP-QM-001 — resolves to the Document & Records Control SOP (via qms-index; basename doesn't carry the ID — resolvability nit).
- **L1** GL-TMP-RM-004 siblings — Linked Hazard ID columns present and back-linking as claimed (spot-checked both directions).

## Open Resolutions

- **Registry extension — DONE (task ben/105, 2026-07-15):** six L1a distillations + L1b applicability docs authored from public sources (IEC 60601-1 / -1-2 / -1-8 / -2-24, ISO 10993 series, IEC 60812 — plus 21 CFR 820/QMSR two-tier). Public determinations that sharpen this audit's findings:
  - **E5/E6/E7 escalation (still licensed-copy-gated, but now with public counter-evidence):** a publisher-authorized preview of IEC 60601-2-24:2012 front matter shows Table 201.101 pairing **§201.12.1.103 with ambulatory-pump accuracy tests** (contradicting its citation as the free-flow test), the accuracy family as **§201.12.1.102–.107** (the cited .101 unconfirmed), and occlusion/bolus protection at **§201.12.4.4.104** (the cited .103 unconfirmed). Do NOT renumber from the preview alone (front matter, not clause bodies) — confirmation against a licensed copy is **blocking for Hazard Analysis Rev 1.0**; see `docs/external/standards/iec-60601-2-24.md`.
  - **IEC 60601-2-24 has no current FDA recognition** (verified null in the Recognized Consensus Standards DB) — a declaration-of-conformity claim is unavailable for it.
  - **E3 edition question sharpened:** FDA recognizes IEC 60601-1 at Ed 3.2 consolidated (rec 19-49); the DHF's "3rd edition + A1" (Ed 3.1) needs reconciliation before a DoC.
  - **E10:** FDA recognizes IEC 60601-1-2 only at **Ed 4.1** (rec 19-36, partial) — the DHF's "4th edition" needs the same reconciliation.
  - **E11:** the -10/-23 irritation split (2021) is pinned; the HA's "-10 = sensitization/irritation" is correct only against the :2010 edition — edition pin open.
- **GL-TMP-RM-002 Risk Management Report** — author the residual-ALARP dispositions (HAZ-001/002/003/004/008/012/014) and the §7 benefit-risk analysis; the hazard-analysis Summary now uses forward tense until then.
- **E2 Annex C taxonomy** — confirm the five-class list against the ISO 14971:2019 original (possible prior-edition/TR 24971 provenance); resolve the inline `[VERIFY]`.

## Provenance

- Extraction method: regex pass over the source doc + LLM pass over narrative prose with regex-extracted spans masked.
- Verdict bands: three-band — `sound | unverified | broken`.
- External-formal references verified by two-tier L1a + L1b consolidation.
- Batched per task ben/102 final-stage requirement (regulatory-authoring rule §6); verification runs as independent subagents.
