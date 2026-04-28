# Industry Frameworks — Reference Distillations

Non-FDA, non-ISO/IEC frameworks that medtech projects commonly use when there's no prescriptive standard to follow — interoperability profiles, security frameworks, AI/ML best-practice guidance, and industry-consensus technical reports.

## Distilled Frameworks

| Framework | File | Subject |
|-----------|------|---------|
| ASTM F2554 | [`astm-f2554.md`](astm-f2554.md) | Standard practice for navigation accuracy |
| DICOM | [`dicom.md`](dicom.md) | Digital Imaging & Communications in Medicine — standard for medical imaging interoperability |
| HL7 FHIR | [`hl7-fhir.md`](hl7-fhir.md) | Fast Healthcare Interoperability Resources |
| IHE Profiles | [`ihe-profiles.md`](ihe-profiles.md) | Integrating the Healthcare Enterprise profiles (how standards compose in clinical workflows) |
| GMLP | [`gmlp.md`](gmlp.md) | FDA/Health Canada/MHRA Good Machine Learning Practice guiding principles |
| NIST CSF | [`nist-csf.md`](nist-csf.md) | Cybersecurity Framework (Identify / Protect / Detect / Respond / Recover) |
| NTIA SBOM | [`ntia-sbom.md`](ntia-sbom.md) | Software Bill of Materials minimum elements |
| OWASP | [`owasp.md`](owasp.md) | OWASP medical device security guidance |

## Scope

### In Scope
- Key principles, components, and expected outputs from each framework
- Typical interaction points with IEC/ISO standards (e.g. NIST CSF ↔ IEC 81001-5-1)
- When and why a project would invoke the framework

### Out of Scope (see instead)
- **Project-specific framework selection** — `docs/external/industry-frameworks/` in each project documents which frameworks this program chose and why
- **Consensus standards** (IEC/ISO) — `../standards/`
- **FDA guidance documents** — `../fda-guidance/`

## Conventions

- Files use short-name `.md` (no `-distilled` suffix — newer convention than the fda-guidance folder uses)
- H1 is "`<Framework name> — <Subject>`"

## For Claude (when grounded against a consuming project)

Frameworks are usually invoked as *chosen alternatives* rather than hard requirements. When citing one:
1. Check the project's applicability file (`docs/external/industry-frameworks/<name>.md`) — it should say why this project adopted that framework
2. Cite both that file and the distilled copy here
3. If the project file doesn't document the adoption rationale, flag it — the rationale is usually what an auditor would want to see

## Changelog

- 2026-04-23: README authored as part of project-console v1.7.4 rollout.
