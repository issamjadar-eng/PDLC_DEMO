# Cybersecurity

Cybersecurity posture for this sub-DHF — IEC 81001-5-1 security assessment, threat model, Software Bill of Materials (SBOM), vulnerability management, and Secure Development Lifecycle (SDL) evidence. Feeds into the 510(k) cybersecurity documentation required by the FDA 2023 cybersecurity guidance.

## Structure

```
cybersecurity/
├── README.md (this file)
├── security-assessment.md       ← IEC 81001-5-1 security risk assessment
├── threat-model.md              ← STRIDE or equivalent threat modeling
├── sbom.md                      ← pointer to SBOM artifact (SPDX or CycloneDX)
├── vulnerability-management.md  ← disclosure process, CVE tracking, response plan
├── sdl-evidence.md              ← secure coding, code review, static analysis evidence
└── formal/
    └── *.docx                   ← controlled deliverables for DHF/filing
```

## Relationship to other folders

```
risk-management/hazard-analysis/   ↔  cybersecurity/security-assessment/   (cybersecurity risks are a subset of overall risk; cross-referenced)
design-controls/architecture/      →  cybersecurity/threat-model/          (architecture defines the attack surface)
design-controls/requirements/      ←  cybersecurity/                       (security controls become requirements)
design-controls/vnv/               ←  cybersecurity/                       (security controls require verification)
docs/external/standards/iec-81001-5-1.md  →  cybersecurity/security-assessment/
docs/external/fda-guidance/cybersecurity-distilled.md  →  cybersecurity/
submissions/510k/formal/           ←  cybersecurity/                       (510(k) cybersecurity package pulls from here)
```

## Conventions

- **Threat model before requirements** — the threat model should be drafted early in design and updated as architecture evolves
- **SBOM is machine-readable** — `sbom.md` is a human-readable pointer; the actual SBOM is SPDX JSON or CycloneDX under `formal/`
- **CVE references** use the full `CVE-YYYY-NNNNN` identifier; include CVSS v3.1 score and the mitigation applied
- **SDL evidence** should include quantifiable metrics: static-analysis findings closed, code review coverage, penetration test results
- **Cross-link to risk management** — every security risk in `security-assessment.md` must either map to a safety hazard in `risk-management/hazard-analysis.md` (if it can cause harm) or be explicitly classified as non-safety-impacting with rationale

## For Claude

- When drafting cybersecurity content, cross-reference `docs/external/standards/iec-81001-5-1.md` and `docs/external/fda-guidance/cybersecurity-distilled.md` for the governing requirements
- Do not invent CVE numbers or CVSS scores — use `[VERIFY]` for anything not pulled from an authoritative source
- Flag any security control that lacks a corresponding requirement in `design-controls/requirements/` — security controls that aren't verified are gaps
- When a new component, third-party library, or external interface is added, ask whether the threat model needs updating before approving

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| YYYY-MM-DD | XX | Initial version — created by /medtech-docs init or add-sub-dhf |
