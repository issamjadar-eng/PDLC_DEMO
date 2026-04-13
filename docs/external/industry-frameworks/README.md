# Industry Frameworks

Non-FDA, non-standard industry frameworks, interoperability standards, and guidance that inform our regulatory and technical approach.

## Active Frameworks

Frameworks with dedicated distilled files in this folder:

| Framework | File | Full Title | Referenced In |
|-----------|------|-----------|---------------|
| NIST CSF | [nist-csf.md](./nist-csf.md) | NIST Cybersecurity Framework | Cybersecurity baseline for the connected device (premarket cybersecurity, EHR/FHIR interface, firmware update path) |
| OWASP | [owasp.md](./owasp.md) | OWASP application security guidance (Top 10, ASVS) | Application security for SaMD and the connectivity layer |
| NTIA SBOM | [ntia-sbom.md](./ntia-sbom.md) | NTIA Minimum Elements for a Software Bill of Materials | FDA premarket cybersecurity submission expectation — SBOM minimum elements |
| GMLP | [gmlp.md](./gmlp.md) | Good Machine Learning Practice for Medical Device Development (FDA/Health Canada/MHRA) | AI/ML components in the device |
| HL7 FHIR | [hl7-fhir.md](./hl7-fhir.md) | HL7 Fast Healthcare Interoperability Resources | EHR interoperability — exchange of infusion orders and status with EHR systems |

## Evaluated — Not Required

Frameworks evaluated and determined not needed, with rationale:

| Framework | Full Title | Rationale for Exclusion |
|-----------|-----------|------------------------|
| DICOM | Digital Imaging and Communications in Medicine | No medical imaging in device scope |
| IHE Profiles | Integrating the Healthcare Enterprise profiles | No imaging workflow integrations in scope |
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
