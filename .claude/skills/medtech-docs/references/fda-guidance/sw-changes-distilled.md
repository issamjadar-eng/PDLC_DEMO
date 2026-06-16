# FDA Guidance: Deciding When to Submit a 510(k) for a Change to an Existing Device

🔎 **Finding aid — NOT the authoritative source.** Distilled summary for quick orientation and early analysis. Ground and cite the authoritative full text [`source-md/sw-changes.md`](source-md/sw-changes.md); verify any quote against the byte-correct `source/` PDF before treating it as verbatim. This paraphrases and omits (appendices/worked examples are routinely dropped) — a section's absence here is never evidence the source is silent.

**Full Title**: Deciding When to Submit a 510(k) for a Change to an Existing Device
**Document Date**: October 25, 2017 (final); draft issued August 8, 2016
**Status**: Final (Contains Nonbinding Recommendations)
**PDF Source**: https://www.fda.gov/media/99812/download
**Issuing Body**: CDRH, CBER
**Supersedes**: K97-1 Guidance (January 10, 1997)

## Scope

This guidance helps manufacturers decide whether a change to an existing 510(k)-cleared device (or preamendments/De Novo device) exceeds the regulatory threshold in **21 CFR 807.81(a)(3)** requiring a new 510(k).

The regulatory threshold: a premarket notification is required when the device is about to be significantly changed or modified in design, components, method of manufacture, or intended use -- specifically:
- (i) A change that could significantly affect safety or effectiveness
- (ii) A major change or modification in intended use

**This guidance explicitly does NOT cover software changes.** Software changes are addressed in the separate guidance "Deciding When to Submit a 510(k) for a Software Change to an Existing Device." However, the principles and frameworks here DO apply to non-software changes made to devices that contain software, including labeling changes and hardware/materials changes.

### What This Guidance Covers
- Labeling changes (Flowchart A)
- Technology, engineering, and performance changes (Flowchart B) -- non-IVD
- Materials changes (Flowchart C) -- non-IVD
- Technology, engineering, performance, and materials changes for IVDs (Flowchart D)
- Risk-based assessment framework (Section E)

### What This Guidance Does NOT Cover
- Software changes (separate guidance)
- Combination products (explicitly noted as not specifically addressed, though general principles may be helpful)
- *(By inference — not stated as exclusions in § III:* 510(k)-exempt devices and PMA devices; this guidance addresses changes to **510(k)-cleared** devices.*)*

## Key Requirements

### The 10 Guiding Principles

1. **Intent-based threshold**: If a change is intended to significantly affect safety or effectiveness (improve outcomes, mitigate known risk, respond to adverse events), a new 510(k) is likely required regardless of other considerations.

2. **Initial risk-based assessment**: Every change should begin with a risk-based assessment of whether it could significantly affect safety or effectiveness, positively or negatively.

3. **Unintended consequences**: Consider whether a change could have downstream effects on other device aspects.

4. **Use of risk management**: Risk assessment should follow established methods (e.g., ISO 14971) and consider both safety and effectiveness.

5. **Role of testing (V&V)**: If initial assessment says no new 510(k), V&V should confirm. If V&V produces unexpected results, reconsider.

6. **Simultaneous changes**: Assess each change separately AND in aggregate.

7. **Cumulative effect**: Compare the changed device to the "original device" (most recently cleared 510(k) version). When cumulative changes exceed the threshold, submit a new 510(k).

8. **Documentation requirement**: All changes must be documented per QS regulation (21 CFR Part 820), even if no new 510(k) is required.

9. **510(k) for modified devices**: When a new 510(k) is submitted, describe ALL changes since the last clearance -- both those requiring and not requiring submission.

10. **SE not assured**: Following this guidance does not guarantee an SE determination.

### Decision Flowcharts

#### Main Entry Flowchart

1. Is the change made with intent to significantly improve safety or effectiveness? -- If YES: New 510(k) likely required
2. Is it a labeling change? -- Go to Flowchart A
3. Is it a technology, engineering, or performance change? -- Go to Flowchart B (non-IVD) or D (IVD)
4. Is it a materials change? -- Go to Flowchart C (non-IVD) or D (IVD)
5. None of the above? -- Documentation only

#### Flowchart A: Labeling Changes

Key decision points:
- **A1**: Change in indications for use statement?
  - Single use to reusable? -- New 510(k)
  - Rx to OTC? -- New 510(k)
  - Name/readability change only? -- Documentation
  - New disease, condition, or patient population? -- New 510(k)
  - Does risk-based assessment identify new/significantly modified risks? -- If yes, New 510(k)
- **A2**: Add or delete a contraindication? -- New 510(k)
- **A3**: Change in warnings/precautions? -- Evaluate through A1 decision points
- **A4**: Could the change affect directions for use? -- If yes, evaluate through A1; if no, Documentation

#### Flowchart B: Technology, Engineering, and Performance Changes (non-IVD)

Key decision points:
- **B2**: Control mechanism, operating principle, or energy type change? -- New 510(k)
- **B3**: Sterilization, cleaning, or disinfection change?
  - Category B/novel method, lower SAL, or change in how provided? -- New 510(k)
  - Could it affect performance/biocompatibility? -- If yes, New 510(k)
- **B4**: Packaging or expiration dating change?
  - Same method/protocol as previous 510(k)? -- Documentation; otherwise New 510(k)
- **B5**: Any other design change (dimensions, performance specs, wireless, components, user interface)?
  - Significantly affects use? -- New 510(k)
  - Risk-based assessment identifies new/modified risks? -- New 510(k)
  - Clinical data necessary? -- New 510(k)
  - Unexpected issues from V&V? -- New 510(k); otherwise Documentation

#### Flowchart C: Materials Changes (non-IVD)

Key decision points:
- **C2**: Change in material type, formulation, composition, or processing? -- If no, Documentation
- **C3**: Will changed material contact body tissues/fluids? -- If no, go to C5
- **C4**: Risk assessment identifies biocompatibility concerns? -- If no, go to C5
  - Manufacturer used same material in similar legally marketed device? -- If yes, go to C5; otherwise New 510(k)
- **C5**: Could change affect performance specifications? -- If yes, go to B5; otherwise Documentation

#### Flowchart D: IVD-Specific Changes

- **D1**: Alters operating principle? -- New 510(k)
- **D2**: Change identified in a device-specific final guidance or classification regulation? -- New 510(k) likely required
- **D3**: Risk-based assessment identifies new/modified risks? -- New 510(k)
- **D4**: Unexpected issues from V&V? -- New 510(k); otherwise Documentation

### Risk-Based Assessment Framework (Section E)

**When required:** Throughout the flowcharts, several decision points direct manufacturers to conduct a risk-based assessment.

**Key factors to evaluate:**
- Relationship between hazards and harm (initiating events, hazardous situations, likelihood, severity)
- Likelihood/probability of occurrence (historical data, literature, engineering analysis)
- Severity of harm (worst-case and most-likely scenarios)
- Both safety AND effectiveness (unlike traditional risk analysis focused only on safety/harm)

**Definition of "New Risk":** A new hazard or hazardous situation that did not exist for the original device, where the pre-mitigation risk level is not considered acceptable.

**Definition of "Significantly Modified Risk":** A change that alters the risk score, risk acceptability category, or duration of risk.

### QS Regulation Interaction

For changes not requiring a new 510(k), the Quality System regulation (21 CFR Part 820) is the primary mechanism:
- Review and approval of design/production changes
- Documentation in the device master record
- Process validation
- Records available to FDA investigators

This creates a two-tier system: FDA premarket review for significant changes; QS-regulated internal processes for non-significant changes.

## Key Definitions

| Term | Definition |
|------|-----------|
| **Original device** | The device as described in the most recently cleared 510(k) -- the baseline for cumulative change comparison |
| **New risk** | A new hazard or hazardous situation not present in the original device, with unacceptable pre-mitigation risk |
| **Significantly modified risk** | A change altering risk score, acceptability category, or duration of risk |
| **21 CFR 807.81(a)(3)** | Regulatory threshold requiring a new 510(k) for significant changes |

## Submission Requirements

When a new 510(k) is required:
- Describe ALL changes since the last clearance (both those requiring and not requiring submission)

When a new 510(k) is NOT required:
- Document all changes per QS regulation (21 CFR Part 820)
- Maintain design controls, device master record, and process validation records

## Cross-References

- **Software Changes Guidance**: "Deciding When to Submit a 510(k) for a Software Change to an Existing Device" -- for software-specific changes
- **PMA Modifications Guidance**: "Modifications to Devices Subject to Premarket Approval (PMA) -- The PMA Supplement Decision-Making Process"
- **PCCP Guidances**: General PCCP and AI/ML PCCP -- for pre-specifying anticipated changes in the original submission
- **510(k) SE Guidance**: "The 510(k) Program: Evaluating Substantial Equivalence"
- **ISO 14971**: Risk Management for Medical Devices
- **21 CFR Part 820**: Quality System Regulation (amended Feb 2, 2024 (89 FR 7496); retitled the Quality Management System Regulation (QMSR), effective Feb 2, 2026, incorporating ISO 13485:2016 by reference)
