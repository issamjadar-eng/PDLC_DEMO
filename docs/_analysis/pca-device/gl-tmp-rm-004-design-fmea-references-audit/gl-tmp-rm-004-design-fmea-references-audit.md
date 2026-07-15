---
audit_id: RA-gl-tmp-rm-004-design-fmea-001
source_doc: docs/project/dhfs/pca-device/risk-management/GL-TMP-RM-004-design-fmea.md
created: 2026-07-14
status: Findings Posted
schema_version: 1
---

# References Audit — PCA-DEVICE-GL-TMP-RM-004-design-fmea — Design FMEA (dFMEA)

**Source doc:** [`docs/project/dhfs/pca-device/risk-management/GL-TMP-RM-004-design-fmea.md`](../../../../docs/project/dhfs/pca-device/risk-management/GL-TMP-RM-004-design-fmea.md)
**Audit ID:** `RA-gl-tmp-rm-004-design-fmea-001`
**Created:** `2026-07-14`
**Status:** `Findings Posted`

This audit verifies that every citation in the source document actually resolves to a real source and that the source supports the cited claim. Findings carry a verdict band (`sound | unverified | broken`) and a finding kind (open enum). External-formal references are verified against both the medtech-docs registry distillation (L1a) and the project applicability layer (L1b) per the "cite both" mandate. See the `reference-audit` skill SKILL.md for the engine contract; see the `citations` advisor for the verdict semantics.

## Summary

| Class | sound | unverified | broken | Total |
|-------|------:|-----------:|-------:|------:|
| external-formal | 2 | 2 | 0 | 4 |
| internal-formal | 8 | 0 | 0 | 8 |
| informal-link | 0 | 0 | 0 | 0 |
| **Total** | **10** | **2** | **0** | **12** |

_Verified 2026-07-14 by the `citations` advisor (batch fan-out, task ben/102)._

## References (Pending Verification)

```yaml
references:
  - {id: E1, class: external-formal, method: regex, target: "IEC 60812:2018", anchor: "Scope blockquote / Standards Anchor", claim: "The dFMEA methodology is anchored in IEC 60812:2018 (failure modes and effects analysis)."}
  - {id: E2, class: external-formal, method: regex, target: "ISO 14971:2019 §5", anchor: "Standards Anchor", claim: "The FMEA supports the ISO 14971 §5 risk analysis."}
  - {id: E3, class: external-formal, method: regex, target: "IEC 62304", anchor: "FMEA rows (firmware controls)", claim: "Firmware lifecycle/verification controls cited in rows are per IEC 62304."}
  - {id: E4, class: external-formal, method: regex, target: "IEC 60601-1-8", anchor: "FMEA row (alarm annunciation)", claim: "Alarm annunciation control referenced per IEC 60601-1-8."}
  - {id: I1, class: internal-formal, method: regex, target: "GL-WI-RM-002", anchor: "Scope blockquote", claim: "The analysis is performed per GL-WI-RM-002 (FMEA Work Instruction)."}
  - {id: I2, class: internal-formal, method: regex, target: "GL-WI-RM-002 §4", anchor: "Scoring Basis", claim: "GL-WI-RM-002 §4 defers O/D scale definition to the product Risk Management Plan (GL-TMP-RM-001)."}
  - {id: I3, class: internal-formal, method: regex, target: "GL-WI-RM-002 §5", anchor: "Coverage Summary / linkage note", claim: "Every failure mode with potential patient harm must link to a Hazard Analysis row per GL-WI-RM-002 §5."}
  - {id: I4, class: internal-formal, method: regex, target: "GL-STD-RM-001 §3 / §4 / §9 / §5", anchor: "Scoring Basis; RPN note; Coverage Summary", claim: "S from §3; O uses §4 anchors as proxy; D and RPN-for-prioritization-only per §9; unacceptable-region judgment per the §5 matrix."}
  - {id: I5, class: internal-formal, method: regex, target: "GL-TMP-RM-001", anchor: "Scoring Basis [VERIFY]", claim: "The product Risk Management Plan (GL-TMP-RM-001 instance) does not yet define FMEA-specific O anchors for this DHF."}
  - {id: I6, class: internal-formal, method: regex, target: "GL-TMP-RM-003 hazard spine (HAZ-001…HAZ-016)", anchor: "Linked Hazard ID column", claim: "Every Linked Hazard ID exists in the sibling hazard analysis."}
  - {id: I7, class: internal-formal, method: regex, target: "DHF-PP3500-DI-001 (design inputs; DI-### cites in control columns)", anchor: "Scope blockquote; controls columns", claim: "Prevention/detection controls cite implementing design inputs that exist in DHF-PP3500-DI-001."}
  - {id: I8, class: internal-formal, method: regex, target: "../../../../internal/source-md/qms-index.md (GL-TMP-RM-004 link)", anchor: "Header block", claim: "The parent QMS template link resolves to the QMS index."}
```

## Findings (broken)

<!-- per-finding detail blocks go here -->

## Findings (unverified)

### E1 — IEC 60812:2018 · `registry-gap`
- **Claim:** dFMEA methodology anchored in IEC 60812:2018.
- **Evidence:** citation present as claimed (Standards Anchor + scope blockquote); L1a registry has no IEC 60812 distillation and L1b `docs/external/standards/` has no applicability file; IEC source paywalled — no web fallback.
- **Suggested fix:** registry distillation + `docs/external/standards/iec-60812.md` applicability doc.

### E4 — IEC 60601-1-8 · `registry-gap`
- **Claim:** FM-D-018 alarm system qualified to IEC 60601-1-8 with SPL range 45–80 dB(A).
- **Evidence:** only local mention is a content-free "[VERIFY — populate from source]" collateral-standards row in `docs/external/standards/iec-60601-1.md`; no L1a distillation, no L1b file; paywalled — the numeric SPL-range claim is unverifiable against any local source.
- **Suggested fix:** add an IEC 60601-1-8 distillation + applicability file so the alarm-annunciation control and SPL range can be verified.

## Findings (sound)

- **E2** ISO 14971:2019 §5 — L1a + L1b both map Clause 5 to Risk Analysis (hazard identification / estimation); cite-both satisfied.
- **E3** IEC 62304 — FM-D-015/-016 Class C lifecycle claims consistent with L1a §4.3/§5.4/§5.5 and the L1b process-area table.
- **I1** GL-WI-RM-002 — resolves to `fmea-wi.md` (FMEA WI, parent GL-SOP-RM-001).
- **I2** GL-WI-RM-002 §4 — quote-verified: §4 defers S/O/D scales to the product RM Plan (GL-TMP-RM-001); the narrower O/D claim is entailed.
- **I3** GL-WI-RM-002 §5 — step 7 verbatim: harm-bearing failure modes must link to a Hazard Analysis row.
- **I4** GL-STD-RM-001 §3/§4/§9/§5 — all four sub-cites verified incl. §9's RPN-prioritization-only rule.
- **I5** GL-TMP-RM-001 — instance exists at `design-controls/plans/GL-TMP-RM-001-risk-management-plan.md` as a v0.1 stub with no O anchors: the negative claim is confirmed; `[VERIFY]` stays until baselined.
- **I6** GL-TMP-RM-003 spine — 11/11 distinct Linked Hazard IDs resolve; FM-D-012 intentionally unlinked per Coverage Summary.
- **I7** DHF-PP3500-DI-001 — 27/27 distinct cited DI IDs exist (contiguous DI-001–DI-034 defined).
- **I8** qms-index link — resolves; index registers GL-TMP-RM-004 (FMEA Worksheet, anchor IEC 60812).

## Open Resolutions

- **E1/E4 registry gaps — CLOSED (task ben/105, 2026-07-15):** `iec-60812.md` and `iec-60601-1-8.md` now exist at both tiers (public-source-grounded finding aids). IEC 60812:2018 is FDA-recognized (rec 5-120, complete); IEC 60601-1-8 recognized at Ed 2.2 (rec 5-131). E4's SPL numeric range (45–80 dB(A)) remains licensed-copy-gated — carried as the top open item in `docs/external/standards/iec-60601-1-8.md`.
- **Observation (not a citation defect):** the Coverage Summary operationalizes "potential patient harm" as S ≥ 3 (18 modes) while 20 are linked — a local scoping interpretation, noted for the adjudicator.
- **GL-TMP-RM-001 RM Plan** — v0.1 stub; the O-anchor `[VERIFY]` resolves at baseline.

## Provenance

- Extraction method: regex pass over the source doc + LLM pass over narrative prose with regex-extracted spans masked.
- Verdict bands: three-band — `sound | unverified | broken`.
- External-formal references verified by two-tier L1a + L1b consolidation.
- Batched per task ben/102 final-stage requirement (regulatory-authoring rule §6); verification runs as independent subagents.
