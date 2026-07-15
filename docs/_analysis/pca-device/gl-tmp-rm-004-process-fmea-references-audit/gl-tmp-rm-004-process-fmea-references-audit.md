---
audit_id: RA-gl-tmp-rm-004-process-fmea-001
source_doc: docs/project/dhfs/pca-device/risk-management/GL-TMP-RM-004-process-fmea.md
created: 2026-07-14
status: Findings Posted
schema_version: 1
---

# References Audit — PCA-DEVICE-GL-TMP-RM-004-process-fmea — Process FMEA (pFMEA)

**Source doc:** [`docs/project/dhfs/pca-device/risk-management/GL-TMP-RM-004-process-fmea.md`](../../../../docs/project/dhfs/pca-device/risk-management/GL-TMP-RM-004-process-fmea.md)
**Audit ID:** `RA-gl-tmp-rm-004-process-fmea-001`
**Created:** `2026-07-14`
**Status:** `Findings Posted`

This audit verifies that every citation in the source document actually resolves to a real source and that the source supports the cited claim. Findings carry a verdict band (`sound | unverified | broken`) and a finding kind (open enum). External-formal references are verified against both the medtech-docs registry distillation (L1a) and the project applicability layer (L1b) per the "cite both" mandate. See the `reference-audit` skill SKILL.md for the engine contract; see the `citations` advisor for the verdict semantics.

## Summary

| Class | sound | unverified | broken | Total |
|-------|------:|-----------:|-------:|------:|
| external-formal | 0 | 2 | 0 | 2 |
| internal-formal | 7 | 0 | 0 | 7 |
| informal-link | 0 | 0 | 0 | 0 |
| **Total** | **7** | **2** | **0** | **9** |

_Verified 2026-07-14 by the `citations` advisor (batch fan-out, task ben/102). Post-audit: E2 escalated from unverified to stale-citation once the QMSR was imported, and was fixed in the source doc (task ben/105) — see the E2 entry._

## References (Pending Verification)

```yaml
references:
  - {id: E1, class: external-formal, method: regex, target: "IEC 60812:2018", anchor: "Scope blockquote / Standards Anchor", claim: "The pFMEA methodology is anchored in IEC 60812:2018."}
  - {id: E2, class: external-formal, method: regex, target: "21 CFR 820.75", anchor: "FMEA rows (process validation controls)", claim: "Process-validation controls for special processes are per 21 CFR 820.75."}
  - {id: I1, class: internal-formal, method: regex, target: "GL-WI-RM-002 (incl. §4, §5)", anchor: "Scope blockquote; Scoring Basis", claim: "The analysis is per GL-WI-RM-002; §4 defers O/D scales to the RM Plan; §5 requires harm-bearing modes to link to the hazard analysis."}
  - {id: I2, class: internal-formal, method: regex, target: "GL-STD-RM-001 §3 / §4 / §9 / §5", anchor: "Scoring Basis; RPN note; Coverage Summary", claim: "S from §3; O per §4 anchors as proxy; D + RPN-for-prioritization-only per §9; region judgment per §5."}
  - {id: I3, class: internal-formal, method: regex, target: "GL-TMP-RM-001", anchor: "Scoring Basis [VERIFY]", claim: "The PP3500 Risk Management Plan does not yet define FMEA-specific O anchors."}
  - {id: I4, class: internal-formal, method: regex, target: "GL-TMP-RM-003 hazard spine (HAZ IDs)", anchor: "Linked Hazard ID column", claim: "Every Linked Hazard ID exists in the sibling hazard analysis."}
  - {id: I5, class: internal-formal, method: regex, target: "GL-SOP-DC-007", anchor: "FMEA row controls (design transfer)", claim: "Design-transfer controls are governed by GL-SOP-DC-007."}
  - {id: I6, class: internal-formal, method: regex, target: "DHF-PP3500-DI-001 (DI-### cites)", anchor: "Controls columns", claim: "Cited design inputs exist in DHF-PP3500-DI-001."}
  - {id: I7, class: internal-formal, method: regex, target: "../../../../internal/source-md/qms-index.md (GL-TMP-RM-004 link)", anchor: "Header block", claim: "The parent QMS template link resolves to the QMS index."}
```

## Findings (broken)

<!-- per-finding detail blocks go here -->

## Findings (unverified)

### E1 — IEC 60812:2018 · `registry-gap`
- **Claim:** pFMEA methodology anchored in IEC 60812:2018.
- **Evidence:** L1a silent (registry distills ISO 14971 / IEC 62304 / 62366-1 / 81001-5-1 / 82304-1 — no IEC 60812); L1b silent (`docs/external/standards/` has no iec-60812 applicability doc). Citation present as claimed at the source's Standards Anchor; note the header cites undated "IEC 60812" while the scope blockquote pins ":2018". IEC source paywalled — no L4 fetch.
- **Suggested fix:** extend the registry with an IEC 60812 distillation (from a licensed copy) + author `docs/external/standards/iec-60812.md` applicability; reconcile dated-vs-undated citation form in the source header.

### E2 — 21 CFR 820.75 · `registry-gap` → **stale-citation, RESOLVED 2026-07-14**
- **Claim:** process-validation controls for special processes are per 21 CFR 820.75.
- **Evidence:** L1a silent (regulations registry covers Parts 807/814/880/892 + 45 CFR 164 — no Part 820); L1b silent (`docs/external/regulations/` has only hipaa.md). Predicate confirmed against the govinfo 2024 CFR edition ("§820.75 Process validation… cannot be fully verified by subsequent inspection and test… shall be validated with a high degree of assurance") — but that edition predates the QMSR final rule (effective Feb 2026); current-edition eCFR fetch was bot-blocked, so post-QMSR currency is unconfirmed.
- **Resolution (task ben/105):** Part 820 imported two-tier from the eCFR (point-in-time 2026-07-13, corroborated by a user-supplied current PDF): the current Part 820 is the **QMSR** — §820.75 was **repealed** (Subparts C–O reserved; ISO 13485:2016 incorporated by reference via §820.7). The audit's currency suspicion was correct: the citation was stale against current law. Fixed in the source doc: process-validation citations restated as "ISO 13485 §7.5.6 process validation (via 21 CFR 820.7 QMSR incorporation)". Registry: `references/regulations/21-cfr-part-820.md` (+ source/source-md); applicability + program citation rule: `docs/external/regulations/qmsr-part-820.md`.

## Findings (sound)

- **I1** GL-WI-RM-002 (§4, §5) — resolved via `docs/internal/source-md/risk-management/fmea-wi.md`; §4 defers scales to the RM Plan, §5 step 7 requires harm-bearing modes to link to the hazard analysis. Quote-verified.
- **I2** GL-STD-RM-001 §3/§4/§9/§5 — all four sections exist in `risk-assessment-criteria.md` and say what's claimed (§9: RPN prioritization-only; §4 P-scale used as O-proxy is consistent with the claim's framing).
- **I3** GL-TMP-RM-001 — a pca-device RM Plan instance exists (`design-controls/plans/GL-TMP-RM-001-risk-management-plan.md`, v0.1 stub) with zero O-anchor content: the negative claim is verified; the source's `[VERIFY]` marker stays until the plan is baselined.
- **I4** GL-TMP-RM-003 spine — 7/7 distinct Linked Hazard IDs resolve (HAZ-001/-005/-006/-008/-011/-012/-013); FM-P-008 intentionally unlinked, matching the Coverage Summary.
- **I5** GL-SOP-DC-007 — resolves to `docs/internal/source-md/design-controls/design-transfer-sop.md` (Design Transfer, ISO 13485 §7.3.8 / 820.30(h)); predicate matches.
- **I6** DHF-PP3500-DI-001 — 9/9 cited DI IDs exist as requirement rows in `design-inputs.md`.
- **I7** qms-index link — relative path resolves; index lists GL-TMP-RM-004 (FMEA Worksheet).

## Open Resolutions

- **E1 registry gap — CLOSED (task ben/105, 2026-07-15):** `iec-60812.md` authored at both tiers; IEC 60812:2018 is FDA-recognized (rec 5-120, complete standard). ~~E2 (21 CFR 820)~~ closed earlier: QMSR imported, citation repaired (see E2 above).
- **GL-TMP-RM-001 RM Plan** — still a v0.1 stub; the pFMEA's O-anchor `[VERIFY]` resolves when the plan is baselined.

## Provenance

- Extraction method: regex pass over the source doc + LLM pass over narrative prose with regex-extracted spans masked.
- Verdict bands: three-band — `sound | unverified | broken`.
- External-formal references verified by two-tier L1a + L1b consolidation.
- Batched per task ben/102 final-stage requirement (regulatory-authoring rule §6); verification runs as independent subagents.
