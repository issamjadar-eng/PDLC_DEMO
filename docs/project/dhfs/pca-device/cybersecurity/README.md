# Cybersecurity — pca-device

Cybersecurity posture for the PP3500 patient-controlled analgesia pump — IEC 81001-5-1 security assessment, threat model, SBOM, vulnerability management, and Secure Development Lifecycle (SDL) evidence. Feeds into the 510(k) cybersecurity documentation required by the FDA 2023 cybersecurity guidance.

## Structure

```
cybersecurity/
├── README.md (this file)
├── security-assessment.md       ← IEC 81001-5-1 security risk assessment (TBD)
├── threat-model.md              ← STRIDE threat modeling (TBD)
├── sbom.md                      ← pointer to SBOM artifact, SPDX/CycloneDX in formal/ (TBD)
├── vulnerability-management.md  ← CVE tracking, disclosure process, response plan (TBD)
├── sdl-evidence.md              ← secure coding, static analysis, pen test evidence (TBD)
└── formal/
    └── README.md                ← controlled cybersecurity deliverables for DHF/filing
```

_This folder is newly scaffolded as part of task 007 P6 (unified DHF shape reorg). Contents are to be authored — no existing cybersecurity artifacts were carried over from PDLC_DEMO's pre-reorg flat layout because the old layout had no cybersecurity folder._

## Relationship to other folders

```
../risk-management/hazard-analysis/ ↔  ./security-assessment/   (cybersecurity risks are a subset of overall risk; cross-referenced)
../design-controls/architecture/    →  ./threat-model/          (architecture defines the attack surface)
../design-controls/requirements/    ←  ./                       (security controls become requirements)
../design-controls/vnv/             ←  ./                       (security controls require verification)
../../../external/standards/iec-81001-5-1.md        →  ./security-assessment/
../../../external/fda-guidance/cybersecurity-distilled.md  →  ./
../../../submissions/510k/formal/   ←  ./                       (510(k) cybersecurity package pulls from here)
```

## Conventions

- **Threat model before requirements** — the threat model should be drafted early in design and updated as architecture evolves
- **SBOM is machine-readable** — `sbom.md` is a human-readable pointer; the actual SBOM is SPDX JSON or CycloneDX under `formal/`
- **CVE references** use the full `CVE-YYYY-NNNNN` identifier with CVSS v3.1 score and the mitigation applied
- **Cross-link to risk management** — every security risk in `security-assessment.md` must map to either a safety hazard in `../risk-management/hazard-analysis.md` or be explicitly classified as non-safety-impacting with rationale

## For Claude

- Cross-reference `docs/external/standards/iec-81001-5-1.md` and `docs/external/fda-guidance/cybersecurity-distilled.md` for the governing requirements when drafting cybersecurity content
- Do not invent CVE numbers, CVSS scores, or vulnerability data — use `[VERIFY]` for anything not pulled from an authoritative source
- When a new component, third-party library, or external interface is added to PP3500's architecture, update the threat model before approving the design change
- `_Demo sample data — not for clinical use._`

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| 2026-04-13 | BX | Initial version — folder scaffolded during task 007 P6 reorg. Contents to be authored. |
