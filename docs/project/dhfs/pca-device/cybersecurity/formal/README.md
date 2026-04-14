# Cybersecurity — Formal Deliverables

Controlled cybersecurity deliverables for the PP3500 pca-device sub-DHF. Working markdown lives at `../` (the parent `cybersecurity/` folder); this folder holds the formal DOCX, PDF, and machine-readable artifacts that make it into the filing or the DHF record.

## Expected Content

- `security-assessment.docx` — signed IEC 81001-5-1 security risk assessment
- `threat-model.docx` — reviewed threat model
- `sbom.spdx.json` or `sbom.cyclonedx.json` — machine-readable Software Bill of Materials
- `vulnerability-management-plan.docx` — formal VM plan
- `penetration-test-report.pdf` — if applicable, third-party pen test report

_This folder is newly scaffolded as part of task 007 P6 (unified sub-DHF shape reorg). Contents are to be authored when the working markdown at `../` reaches formal-review quality._

## Conventions

- **Filename matches working markdown** — `../security-assessment.md` → `security-assessment.docx`
- **Generated, not hand-edited** — formal deliverables are produced from the markdown via `/docflow` or equivalent toolchain
- **Version controlled** — commit formal deliverables alongside their markdown sources; never overwrite without a changelog note

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| 2026-04-13 | BX | Initial version — folder scaffolded during task 007 P6 reorg. |
