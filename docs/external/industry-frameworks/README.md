# Industry Frameworks

Non-FDA, non-standard industry frameworks, interoperability standards, and guidance that inform our regulatory and technical approach.

## Active Frameworks

Frameworks with dedicated distilled files in this folder:

| Framework | File | Full Title | Referenced In | Spec URL |
|-----------|------|-----------|---------------|----------|
| NIST CSF | [nist-csf.md](./nist-csf.md) | NIST Cybersecurity Framework | Cybersecurity baseline for the connected device (premarket cybersecurity, EHR/FHIR interface, firmware update path) | [nist.gov/cyberframework](https://www.nist.gov/cyberframework) |
| OWASP | [owasp.md](./owasp.md) | OWASP application security guidance (Top 10, ASVS) | Application security for SaMD and the connectivity layer | [owasp.org](https://owasp.org/) |
| NTIA SBOM | [ntia-sbom.md](./ntia-sbom.md) | NTIA Minimum Elements for a Software Bill of Materials | FDA premarket cybersecurity submission expectation — SBOM minimum elements | [ntia.gov/SBOM](https://www.ntia.gov/SBOM) |
| GMLP | [gmlp.md](./gmlp.md) | Good Machine Learning Practice for Medical Device Development (FDA/Health Canada/MHRA) | AI/ML components in the device | [fda.gov/.../gmlp](https://www.fda.gov/medical-devices/software-medical-device-samd/good-machine-learning-practice-medical-device-development-guiding-principles) |
| HL7 FHIR | [hl7-fhir.md](./hl7-fhir.md) | HL7 Fast Healthcare Interoperability Resources | EHR interoperability — exchange of infusion orders and status with EHR systems | [hl7.org/fhir](https://hl7.org/fhir/) |
| IHE Profiles | [ihe-profiles.md](./ihe-profiles.md) | Integrating the Healthcare Enterprise — ITI / Pharmacy domain profiles | EHR integration patterns: PIX/PDQ for patient identity, XDS for document exchange, ITI profiles for cross-enterprise workflows. Complements HL7 FHIR. | [ihe.net/resources/profiles](https://www.ihe.net/resources/profiles/) |

- **Spec URL** column links to the official spec — the distilled markdown in this folder is a derivative; the linked spec is the authoritative source.

## Evaluated — Not Required

Frameworks evaluated and determined not needed, with rationale:

| Framework | Full Title | Rationale for Exclusion |
|-----------|-----------|------------------------|
| DICOM | Digital Imaging and Communications in Medicine | No medical imaging in device scope |
| ASTM F2554 | Standard Practice for Measurement of Positional Accuracy of Computer Assisted Surgical Systems | No surgical navigation — infusion devices do not provide spatial guidance |

## Conventions

- **Naming**: `framework-short-name.md`
- Note the version/date of the framework document
- Document which FDA guidance references this framework and why
- Frameworks evaluated and excluded should remain in the "Evaluated — Not Required" table with rationale

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| YYYY-MM-DD | XX | Initial version — created by /medtech-docs init |
| 2026-04-12 | medtech-docs init | Initial population: added 5 active frameworks (NIST CSF, OWASP, NTIA SBOM, GMLP, HL7 FHIR) and 3 evaluated-not-required entries (DICOM, IHE Profiles, ASTM F2554). All active framework files copied from distilled references. |
| 2026-04-14 | BX | Added "Spec URL" column to the Active Frameworks table per medtech-docs v15. `update-external-references` rubric run: 1 created (ihe-profiles), 5 unchanged, 0 newly-N/A. **Moved IHE Profiles from "Evaluated — Not Required" to Active** — the prior exclusion only considered IHE's imaging angle and missed the ITI/Pharmacy profiles (PIX, PDQ, XDS) that apply to PDLC_DEMO's EHR integration. Captured as a lesson in `tasks/ben/012`: existing exclusions can be incomplete; the rubric is allowed to challenge them, and conflicts should be surfaced to the user rather than auto-reverted. |
