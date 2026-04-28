---
source_file: "N/A — authored-in-markdown"
source_path: "risk-management/risk-assessment-criteria.md"
doc_id: "GL-STD-RM-001"
doc_type: "STD"
title: "Risk Assessment Criteria"
format: "md"
conversion_date: "2026-04-27"
conversion_method: "claude-authored"
conversion_fidelity: "faithful"
pages: null
sheets: null
has_images: false
image_count: 0
has_tables: true
has_form_fields: false
references:
  - doc_id: "ISO 14971:2019 §4.5"
    title: "Criteria for risk acceptability"
    resolved: true
    match: null
    note: "Primary anchor"
  - doc_id: "ISO/TR 24971:2020"
    title: "Guidance on the application of ISO 14971"
    resolved: true
    match: null
    note: "Worked-example acceptance matrices"
conversion_history:
  - date: "2026-04-27"
    source: "v1 — added under task ben/036 to fill the explicit-acceptance-matrix gap referenced (but not defined) by GL-SOP-RM-001"
notes: "Reused across every Hazard Analysis (GL-WI-RM-001) and FMEA (GL-WI-RM-002) under this QMS. Project Risk Management Plans cite this document by ID and section."
---

# GL-STD-RM-001 — Risk Assessment Criteria

_Demo sample data — not for clinical use._

**Document ID:** GL-STD-RM-001
**Revision:** 1.0
**Effective Date:** 2026-04-27
**Owner:** VP Quality, GlobalLogic MedTech

---

## 1. Purpose

Define the canonical severity scale, probability scale, risk-acceptance matrix, and benefit-risk-trigger thresholds used across all GlobalLogic medical device risk management activities — per ISO 14971:2019 §4.5 and guided by ISO/TR 24971:2020.

This standard is **the single source of truth** for risk numerical scales. Project-level Risk Management Plans (GL-TMP-RM-001) cite this standard by ID and section rather than redefining scales.

## 2. Scope

Applies to every risk file produced under the GlobalLogic QMS — hardware, firmware, SaMD, SiMD, and combination products. Used by:

- Hazard Analysis (GL-WI-RM-001)
- Design FMEA / Process FMEA (GL-WI-RM-002)
- Use-related risk analysis (per GL-SOP-UC-001)
- Cybersecurity risk (per GL-SOP-SW-004 + IEC 81001-5-1)

## 3. Severity Scale (S)

Severity is the measure of possible consequences if harm occurs. The scale is **5 levels**, defined in clinical-outcome language so it is auditable across device classes.

| S | Label | Definition (clinical outcome) | Examples |
|---|------|------------------------------|---------|
| 5 | Catastrophic | Death or permanent loss of essential body function | Pump runaway delivering lethal opioid dose; failed defib shock |
| 4 | Critical | Permanent injury, life-threatening event, or hospitalization | Severe respiratory depression requiring rescue; nerve injury from miscalibration |
| 3 | Serious | Reversible injury requiring medical intervention | Local infection at infusion site; transient hypotension |
| 2 | Minor | Discomfort, inconvenience, or temporary nuisance not requiring intervention | Skin irritation; alarm fatigue without harm |
| 1 | Negligible | No detectable harm; nuisance only | Display flicker; cosmetic blemish |

**Anchor rule:** when sliding between two levels, anchor to the worst plausible outcome consistent with normal use — not the worst conceivable misuse. Misuse is captured under use-related risk (GL-SOP-UC-001).

## 4. Probability Scale (P)

Probability of occurrence of harm over the device's expected service life and population. The scale is **5 levels** with quantitative anchors expressed as occurrence rate per device-year (or per use, where the per-use frame fits better).

| P | Label | Quantitative anchor (per device-year) | Plain-language anchor |
|---|------|--------------------------------------|----------------------|
| 5 | Frequent | ≥ 1 in 100 (≥ 10⁻²) | Every device, multiple times |
| 4 | Probable | 1 in 100 to 1 in 1,000 (10⁻² to 10⁻³) | Most devices will see it |
| 3 | Occasional | 1 in 1,000 to 1 in 10,000 (10⁻³ to 10⁻⁴) | Some devices will see it in service life |
| 2 | Remote | 1 in 10,000 to 1 in 100,000 (10⁻⁴ to 10⁻⁵) | Rare across the fleet |
| 1 | Improbable | < 1 in 100,000 (< 10⁻⁵) | Effectively never |

**Estimation hierarchy** (most preferred → least):
1. Field data from the same device under post-market surveillance (GL-SOP-PM-001).
2. Field data from a predicate or similar device cleared under a comparable indication.
3. Reliability calculations (FMEA failure rates, MTBF analysis) for hardware items.
4. SME estimation when no quantitative basis exists — must be documented and revisited at the next risk-file review.

## 5. Risk Acceptance Matrix

Risk = S × P. The acceptance matrix below assigns each (S, P) combination to one of three regions.

|       | P5 Frequent | P4 Probable | P3 Occasional | P2 Remote | P1 Improbable |
|-------|:----------:|:----------:|:-------------:|:--------:|:-------------:|
| **S5 Catastrophic** | Unacceptable | Unacceptable | Unacceptable | ALARP | ALARP |
| **S4 Critical**     | Unacceptable | Unacceptable | ALARP | ALARP | Acceptable |
| **S3 Serious**      | Unacceptable | ALARP | ALARP | Acceptable | Acceptable |
| **S2 Minor**        | ALARP | ALARP | Acceptable | Acceptable | Acceptable |
| **S1 Negligible**   | ALARP | Acceptable | Acceptable | Acceptable | Acceptable |

**Region semantics:**

- **Unacceptable** — risk control measures **shall** be implemented to move the residual risk into ALARP or Acceptable. If no further reduction is feasible, the risk shall be evaluated under benefit-risk analysis (§7); if benefits do not outweigh residual risk, the design **shall not** be released.
- **ALARP** (As Low As Reasonably Practicable) — additional risk controls **shall** be considered; controls shall be implemented unless the cost-benefit analysis shows further reduction is not practicable. Disposition documented in the Risk Management Report.
- **Acceptable** — no further controls required. Risk is accepted as-is and recorded.

## 6. Risk Control Hierarchy (ISO 14971 §7.1)

When applying controls, follow this priority order:

1. **Inherently safe design** — eliminate the hazard or reduce P or S through design choices (e.g., material change, redundancy, fail-safe defaults).
2. **Protective measures in the device or manufacturing process** — alarms, interlocks, mechanical guards, software input validation.
3. **Information for safety** — warnings in IFU, labels, training. **Information alone is the weakest control** and is not sufficient for risks that fall in the Unacceptable region.

## 7. Benefit-Risk Analysis Trigger

Conduct a documented benefit-risk analysis (per ISO 14971 §8) when:

- Any individual residual risk remains in the Unacceptable region after all feasible controls are applied; OR
- The overall residual risk profile of the device is judged by the Risk Manager to warrant explicit benefit-risk justification (e.g., novel intended use, high-severity ALARP cluster).

The analysis is recorded in the Risk Management Report (GL-TMP-RM-002).

## 8. Cross-References

| Document | Relationship |
|---|---|
| GL-SOP-RM-001 | Master risk management SOP — invokes this standard |
| GL-WI-RM-001 | Hazard Analysis WI — uses S, P, and matrix |
| GL-WI-RM-002 | dFMEA / pFMEA WI — uses S × P × Detectability variant (see §9) |
| GL-TMP-RM-001 | Risk Management Plan template — cites this standard |
| GL-STD-RM-002 | Master Harms List — pre-classified S anchors per harm type |

## 9. dFMEA / pFMEA Detectability Note

When applying the FMEA tool (per IEC 60812:2018), an additional **Detectability (D)** dimension is used: D=1 (detected before harm) → D=5 (undetectable until harm occurs). The composite Risk Priority Number (RPN = S × P × D) is used for *prioritization within an FMEA only* — final residual-risk acceptability is judged against the §5 matrix, not the RPN.

## 10. Revision History

| Rev | Date | Author | Summary |
|---|---|---|---|
| 1.0 | 2026-04-27 | Ben Xavier (via Claude, task ben/036) | Initial release. Filled the explicit-acceptance-matrix gap referenced (but not defined) by GL-SOP-RM-001. |
