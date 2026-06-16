# NIST SP 800-66 Rev. 2 — Implementing the HIPAA Security Rule

🔎 **Finding aid — NOT the authoritative source.** Paraphrased distillation of an external standard/framework; no faithful full-text copy exists in this repository (copyrighted). The original document named in the header above is the sole authority — if a clause-level question isn't answered here, state that the original must be consulted; do not infer clause content. `[VERIFY]` marks are unconfirmed against the source.

**Framework**: NIST Special Publication 800-66 Revision 2, *Implementing the HIPAA Security Rule: A Cybersecurity Resource Guide*
**Source**: National Institute of Standards and Technology (NIST), Computer Security Resource Center
**Published**: February 2024 (final; supersedes Rev. 1, October 2008)
**Referenced In**: HHS/OCR HIPAA Security Rule guidance; FDA premarket cybersecurity expectations (via shared NIST CSF / 800-53 control catalog)
**Companion regulation**: `../regulations/45-cfr-part-164.md` (HIPAA Security Rule, Subpart C)

## Overview

SP 800-66 Rev. 2 is **NIST's implementation guide for the HIPAA Security Rule (45 CFR Part 164, Subpart C)**. It does **not** create new requirements — it is a non-binding resource that helps a regulated entity (or a business associate, such as a connected-device manufacturer handling ePHI) operationalize the Security Rule's standards and implementation specifications using established NIST risk-management methodology and control catalogs.

Its value to a medtech program is leverage: it **crosswalks every Security Rule standard onto the NIST Cybersecurity Framework (CSF) and NIST SP 800-53 Rev. 5 controls** the program is already touching for FDA premarket cybersecurity. That means HIPAA compliance and FDA cybersecurity can be driven from **one control catalog and one risk process** rather than two parallel programs.

Rev. 2 is a substantial rewrite of the 2008 Rev. 1: it reorganizes around risk assessment / risk management, drops the prescriptive Rev. 1 checklist tone, and adds the modern CSF / 800-53 mappings.

## What the document contains

| Part | Content | Why it matters |
|------|---------|----------------|
| Security Rule background | Plain-language summary of Subpart C — covered entities, business associates, ePHI, the Required/Addressable framework | Onboarding for teams new to HIPAA |
| **Risk assessment guidance** | How to conduct the § 164.308(a)(1)(ii)(A) **Risk Analysis** — drawing on NIST SP 800-30 methodology (threat sources, vulnerabilities, likelihood × impact) | Operationalizes the single most-cited OCR enforcement gap |
| **Risk management guidance** | How to satisfy § 164.308(a)(1)(ii)(B) **Risk Management** — reducing risk to a reasonable/appropriate level; draws on the SP 800-37 Risk Management Framework | Closes the loop from "found a risk" to "treated it" |
| **Key Activities / Descriptions / Sample Questions** | For each Security Rule standard: concrete activities, a description, and self-assessment questions | Turns each standard into an auditable checklist |
| **Crosswalk appendix** | Maps each Security Rule standard & implementation spec → NIST CSF Subcategories → NIST SP 800-53 Rev. 5 controls | The load-bearing artifact for a program already running 800-53 / CSF |
| Resources appendices | Pointers to NIST publications, templates, tools (e.g., the HHS Security Risk Assessment (SRA) Tool) | Avoids reinventing assessment instruments |

## The crosswalk — how it ties together

The crosswalk is why this document belongs next to `nist-csf.md` rather than being a redundant copy of the regulation. Illustrative rows (consult the SP 800-66 Rev. 2 appendix for the authoritative, complete mapping):

| HIPAA Security Rule | NIST CSF 2.0 | NIST SP 800-53 Rev. 5 (illustrative) |
|---------------------|--------------|--------------------------------------|
| § 164.308(a)(1) Security management process / Risk Analysis | ID.RA (Risk Assessment), GV.RM | RA-3, RA-5, PM-9 |
| § 164.308(a)(5) Security awareness & training | PR.AT | AT-2, AT-3 |
| § 164.308(a)(6) Security incident procedures | RS.MA, RS.AN, RS.CO | IR-4, IR-6, IR-8 |
| § 164.308(a)(7) Contingency plan | RC.RP, PR.IR | CP-2, CP-9, CP-10 |
| § 164.310(d) Device & media controls | PR.DS | MP-6 (media sanitization), MP-7 |
| § 164.312(a) Access control | PR.AA | AC-2, AC-3, AC-7, IA-2 |
| § 164.312(b) Audit controls | DE.CM, PR.PS | AU-2, AU-6, AU-12 |
| § 164.312(e) Transmission security | PR.DS | SC-8, SC-12, SC-13 |

`[VERIFY exact control IDs against the published SP 800-66 Rev. 2 crosswalk appendix before relying on a specific mapping — the table above is illustrative of the mapping's shape, not a verbatim reproduction.]`

## How a medtech program uses it

1. **Run the required Risk Analysis once, against the shared catalog.** Use the SP 800-66 risk-assessment guidance (800-30 methodology) to produce the § 164.308(a)(1)(ii)(A) risk analysis. The same threat-model / risk-assessment artifact feeds FDA premarket cybersecurity (`nist-csf.md` → ID.RA) — one assessment, two regulatory drivers.
2. **Derive technical requirements from the crosswalk.** The § 164.312 technical safeguards map to 800-53 AC/AU/IA/SC controls — author them as SRS security requirements rather than as a separate HIPAA checklist.
3. **Use the Key Activities / Sample Questions as the audit checklist** for each standard.
4. **Retain the artifacts** — § 164.316(b)(2)(i) requires 6-year retention of the risk analysis, policies, and addressable-spec rationales.

## Relationship to sibling references

| Reference | Relationship |
|-----------|--------------|
| `../regulations/45-cfr-part-164.md` | The **regulation** SP 800-66 implements — what the law requires; SP 800-66 is *how* to satisfy it |
| `nist-csf.md` | The **control framework** SP 800-66 crosswalks the Security Rule onto; also FDA's recommended cybersecurity framework — the bridge that lets HIPAA + FDA cyber share one program |
| `../standards/iec-81001-5-1.md` | Health-software security lifecycle standard; its "data protection requirements (PHI/PII if applicable)" line item is satisfied in part via the HIPAA Security Rule + this guide |
| `owasp.md` | OWASP ASVS V8 (Data Protection) overlaps the § 164.312 technical safeguards at the application layer |

## For Claude (when grounded against a consuming project)

SP 800-66 is **guidance, not a requirement** — it is invoked as the chosen *method* for satisfying the HIPAA Security Rule. When citing it:
1. Check the project's applicability file (`docs/external/industry-frameworks/nist-sp-800-66.md`) — it should say the program adopted SP 800-66 as its Security Rule implementation method and point at the actual risk analysis artifact.
2. Cite both that file, the distilled copy here, **and** the regulation it implements (`../regulations/45-cfr-part-164.md`) — the regulation for "what the law requires," SP 800-66 for "how this program satisfies it."
3. If the project has no documented Security Rule risk analysis, flag it — a missing/inadequate risk analysis is the most common OCR enforcement finding, and SP 800-66 exists precisely to close that gap.

## Source Provenance

- **Document**: NIST SP 800-66 Rev. 2, *Implementing the HIPAA Security Rule: A Cybersecurity Resource Guide* (Feb 2024). DOI: 10.6028/NIST.SP.800-66r2.
- **Retrieval date**: 2026-06-02
- **Authoritative copy**: NIST CSRC publication page (`https://csrc.nist.gov/pubs/sp/800/66/r2/final`)
- **Distilled from**: published NIST document structure + the Security Rule crosswalk concept. Specific 800-53 control IDs in the illustrative crosswalk above are marked `[VERIFY]` and must be confirmed against the published appendix.

[VERIFY the crosswalk control IDs and any quoted "Key Activities" against the published SP 800-66 Rev. 2 before relying on them in a regulated submission.]
