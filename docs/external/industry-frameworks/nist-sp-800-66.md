# NIST SP 800-66 Rev. 2 — Project Applicability

_Demo sample data — not for clinical use._

**Framework**: NIST SP 800-66 Rev. 2, *Implementing the HIPAA Security Rule: A Cybersecurity Resource Guide* (Feb 2024)
**Source**: NIST Computer Security Resource Center
**L1a source (distilled framework)**: [`.claude/skills/medtech-docs/references/industry-frameworks/nist-sp-800-66.md`](../../../.claude/skills/medtech-docs/references/industry-frameworks/nist-sp-800-66.md)
**Referenced In**: PP3500's HIPAA Security-Rule compliance method — see [`docs/external/regulations/hipaa.md`](../regulations/hipaa.md)

## Why PP3500 adopts it

PP3500 operates `cloud-suite` as a business associate handling hospital ePHI, so the HIPAA Security Rule (45 CFR 164 Subpart C) applies. SP 800-66 Rev. 2 is the chosen **method** for satisfying it — specifically the **§ 164.308(a)(1)(ii)(A) Risk Analysis** (the keystone Required spec, and the single most-cited OCR enforcement gap).

The leverage: SP 800-66 **crosswalks each Security-Rule standard onto NIST CSF and SP 800-53 controls** — and PP3500 already runs NIST CSF for FDA premarket cybersecurity (see [`nist-csf.md`](./nist-csf.md)). So HIPAA and FDA cybersecurity are driven from **one control catalog and one risk process**, not two parallel programs.

## How it's applied here

| SP 800-66 element | PP3500 application |
|-------------------|--------------------|
| Risk-assessment guidance (SP 800-30 method) | The cybersecurity threat model / risk assessment is documented as the HIPAA risk analysis. **[VERIFY]** a HIPAA-framed view exists. |
| Security-Rule → CSF → 800-53 crosswalk | Technical safeguards (§164.312) are authored as `cloud-suite` / `connectivity-adapter` SRS security requirements rather than a separate HIPAA checklist — see the mapping table in [`../regulations/hipaa.md`](../regulations/hipaa.md) §3. |
| Key Activities / Sample Questions | Used as the per-standard audit checklist during design review. |
| 6-year retention (§164.316) | cloud SRS SW-021 (min 6 yr HIPAA records) + SW-011 (≥7 yr audit log). |

## Citation discipline (cite-both)

Cite **both** this file (L1b — how PP3500 applies the guide) and the L1a distillation (what the guide recommends). The control-ID rows in the L1a crosswalk carry `[VERIFY]` markers — confirm against the published SP 800-66 Rev. 2 appendix before relying on a specific 800-53 mapping.

**Knowledge cutoff / currency**: SP 800-66 Rev. 2 is current (Feb 2024, no later revision as of 2026-06). If the 2025 HIPAA Security Rule NPRM finalizes, expect a future SP 800-66 update reflecting the removed addressable/required distinction.
