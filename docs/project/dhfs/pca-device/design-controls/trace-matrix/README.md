# Trace Matrix

> _Demo sample data — not for clinical use. Illustrative content for the PDLC_DEMO project._

Traceability matrices linking design control artifacts across the full design control waterfall. This is the central cross-referencing hub for the Design History File (DHF), ensuring every user need traces to requirements, every requirement traces to architecture and V&V, and every risk mitigation is verified.

## Current Contents

| File | Document ID | Rev | Description |
|---|---|---|---|
| `un-to-di-trace-matrix.md` | DHF-PP3500-TM-001 | A | Bidirectional UN ↔ DI trace matrix for the PainEase PCA Advanced (DEV-PP3500). Forward (UN → DI) and reverse (DI → UN) traces, organized by the same 9 functional groups (G1–G9) used in upstream documents. 22 UNs, 34 DIs, 100% bidirectional coverage. |

Future additions as the DHF matures: DI ↔ Risk Control trace matrix, DI ↔ V&V trace matrix, and cross-module traceability between SaMD, pump firmware, and hardware subsystems.

## Structure

| Folder | Purpose |
|--------|---------|
| `formal/` | Controlled traceability matrices (XLSX, DOCX) — the DHF record |

Working markdown at the folder root; formal deliverables in `formal/`.

## Expected Content

- **Requirements Traceability Matrix (RTM)** — user needs → requirements → architecture → V&V
- **Risk Traceability Matrix** — hazards → mitigations → verification evidence
- **V&V Traceability Matrix** — test cases → requirements → test results
- **Cross-module traceability** — inter-module dependencies and shared requirements

## Conventions

- **Naming**: `matrix-type.md` at root; matching `.xlsx` in `formal/`
- Each matrix must reference the specific document IDs it traces (e.g., UN-001, REQ-001, TC-001)
- Update matrices when upstream or downstream documents change
- Link back to the originating task document

## For Claude

- When creating or updating design control documents in other folders, check whether trace-matrix entries need updating
- Flag any requirement, user need, or test case that lacks traceability coverage
- Cross-reference: user-needs/ ↔ requirements/ ↔ architecture/ ↔ vnv/ ↔ risk-management/

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| 2026-04-12 | Ben Xavier | Phase 4 authoring — created `un-to-di-trace-matrix.md` (DHF-PP3500-TM-001 Rev A), the bidirectional UN ↔ DI trace matrix aligned with user-needs.md Rev B and design-inputs.md Rev B. |
| YYYY-MM-DD | XX | Initial version — created by /medtech-docs init |
