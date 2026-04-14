# Standards

Applicable regulatory standards for this device. Each standard has a dedicated markdown file with distilled requirements, clause-by-clause relevance, and module applicability.

For non-standard frameworks (NIST CSF, OWASP, GMLP, etc.), see `docs/external/industry-frameworks/`.

## Distilled Standards

Standards with per-file requirement breakdowns in this folder:

| Standard | File | Title | Category | Applicable Modules | Original Source |
|----------|------|-------|----------|--------------------|-----------------|
| IEC 62304 | [iec-62304.md](./iec-62304.md) | Medical device software — Software life cycle processes | Software lifecycle | All software modules (SaMD + SiMD pump firmware) | [webstore.iec.ch](https://webstore.iec.ch/publication/22794) |
| ISO 14971 | [iso-14971.md](./iso-14971.md) | Application of risk management to medical devices | Risk management | Whole device (hardware + software) | [iso.org](https://www.iso.org/standard/72704.html) |
| IEC 62366-1 | [iec-62366-1.md](./iec-62366-1.md) | Application of usability engineering to medical devices | Usability engineering | User-facing SaMD + device UI hardware | [webstore.iec.ch](https://webstore.iec.ch/publication/61937) |
| IEC 82304-1 | [iec-82304-1.md](./iec-82304-1.md) | Health software — Product safety requirements | Health software product safety | SaMD components | [webstore.iec.ch](https://webstore.iec.ch/publication/29316) |
| IEC 81001-5-1 | [iec-81001-5-1.md](./iec-81001-5-1.md) | Health software and health IT systems safety, effectiveness and security — Security — Activities in the product life cycle | Health software security | All connected software (EHR/FHIR interface, SaMD, firmware updates) | [webstore.iec.ch](https://webstore.iec.ch/publication/76914) |
| IEC 60601-1 | [iec-60601-1.md](./iec-60601-1.md) | Medical electrical equipment — Part 1: General requirements for basic safety and essential performance | Medical electrical equipment | Custom medical electrical hardware (power supply, motor drive, fluid delivery assembly, user-facing electrical interfaces) | [webstore.iec.ch](https://webstore.iec.ch/publication/2603) |

- **Original Source** column links to the publisher (IEC standards are copyrighted and not redistributable; only the distilled markdown ships in the skill library). `iec-60601-1.md` is manually authored — not in the skill library — and is preserved as-is by `update-external-references`.

## Deferred Standards (QMS-Level)

Standards managed at the organizational QMS level, not distilled here:

| Standard | Title | Notes |
|----------|-------|-------|

## Supplementary Technical Reports

Reports that provide guidance on applying their parent standards but are not independently auditable:

| Report | Title | Parent Standard |
|--------|-------|-----------------|

## Standards-to-Module Mapping

_Populate with a table showing which standards apply to which device modules, and under what conditions (e.g., "Required", "If SaMD", etc.)._

| Standard | Module 1 | Module 2 | Module N | Notes |
|----------|----------|----------|----------|-------|

## Evaluated — Not Required

Standards evaluated and determined not applicable, with rationale:

| Standard | Title | Rationale for Exclusion |
|----------|-------|------------------------|
| ISO 13485 | Medical devices — Quality management systems | QMS-level standard — owned at the organization/QMS level, not the project DHF |
| 21 CFR 820 / QMSR | FDA Quality Management System Regulation | QMS-level regulation — organization-owned, not project-scoped |
| AAMI TIR57 | Principles for medical device security — Risk management | Cybersecurity guidance covered by IEC 81001-5-1 + NIST CSF — no incremental obligations |
| ISO/IEC 23894 | Information technology — Artificial intelligence — Guidance on risk management | AI risk management — covered by GMLP + ISO 14971 for this project |

## Conventions

- **One file per standard**: `standard-number-short-name.md`
- Each file contains: overview, clause-by-clause requirements, module applicability, verification checks, key deliverables
- Requirements are distilled for use by compliance evaluation skills
- Every file must include a `## Verification Checks` section (machine-readable, read by `/medtech-docs dashboard`)

## For Claude

- When drafting 510(k) or design control documents, check this folder to ensure referenced standards are addressed
- Flag any standard requirement that may impact the PCCP change categories
- Note that established device companies likely have ISO 13485 QMS in place — verify before assuming gaps

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| YYYY-MM-DD | XX | Initial version — created by /medtech-docs init |
| 2026-04-12 | medtech-docs init | Initial population: added 6 active standards (IEC 62304, ISO 14971, IEC 62366-1, IEC 82304-1, IEC 81001-5-1, IEC 60601-1) and 4 evaluated-not-required entries (ISO 13485, 21 CFR 820/QMSR, AAMI TIR57, ISO/IEC 23894). IEC 60601-1 created as a stub with [VERIFY] markers; remaining standards copied from distilled references. |
| 2026-04-14 | BX | Added "Original Source" column to the Distilled Standards table per medtech-docs v15. All 5 skill-library standards already present from initial population — `update-external-references` reported 0 created / 5 unchanged / 1 unchanged-not-in-skill-library (iec-60601-1). See `tasks/ben/012-medtech-docs-update-external-references.md`. |
