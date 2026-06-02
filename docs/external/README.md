# External References

Reference material we consume but don't author. FDA guidance documents, industry standards, clinical literature, and frameworks that inform our regulatory strategy and design controls.

## Subfolders

| Folder | Purpose |
|--------|---------|
| `fda-guidance/` | Project compliance files for each applicable FDA guidance document |
| `regulations/` | Project applicability of federal regulations (Title 21 device rules; Title 45 / HIPAA for ePHI) — L1b of the medtech-docs two-tier model |
| `standards/` | Applicable regulatory standards (ISO/IEC) and compliance tracking |
| `industry-frameworks/` | Non-standard frameworks (NIST CSF, OWASP, GMLP, DICOM, etc.) |
| `clinical-literature/` | Published studies, clinical evidence, clinical workflow references |

## Conventions

- Always note the date and source of any data or finding — external references age quickly
- Note knowledge cutoff — flag if guidance, standards, or frameworks may have been updated
- Link back to the originating task document

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| YYYY-MM-DD | XX | Initial version — created by /medtech-docs init |
| 2026-06-02 | BX | Added `regulations/` subfolder (task ben/076) — the L1b applicability tier for federal regulations (first entry: HIPAA). Previously the project had no regulations L1b tier; added so advisors can cite both layers for HIPAA/ePHI questions per the medtech-docs cite-both mandate. |
