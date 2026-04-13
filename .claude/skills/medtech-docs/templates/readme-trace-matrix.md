# Trace Matrix

Traceability matrices linking design control artifacts across the full design control waterfall. This is the central cross-referencing hub for the Design History File (DHF), ensuring every user need traces to requirements, every requirement traces to architecture and V&V, and every risk mitigation is verified.

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
| YYYY-MM-DD | XX | Initial version — created by /medtech-docs init |
