# Requirements

> _Demo sample data — not for clinical use. Illustrative content for the PDLC_DEMO project._

Design input requirements, software requirements specifications (SRS), label requirements. Formal requirements derived from user needs — each must be verifiable.

## Current Contents

| File | Document ID | Rev | Description |
|---|---|---|---|
| `design-inputs.md` | DHF-PP3500-DI-001 | B | Document of record. 34 design inputs for the PainEase PCA Advanced (DEV-PP3500), organized into 9 functional groups (G1–G9), classified by Category (FUNC/PERF/SAFE/USAB/INTE) and Criticality (CTS/CTF/CTC/S). |

Each design input traces upstream to one or more user needs in `../user-needs/user-needs.md` (DHF-PP3500-UN-001) and forward to verification activities. The bidirectional UN ↔ DI trace matrix lives in `../trace-matrix/un-to-di-trace-matrix.md`.

**Classification taxonomy** — every DI carries exactly one Category (Functional, Performance, Safety, Usability, Interface) and exactly one Criticality (Critical to Safety, Critical to Function, Critical to Compliance, Supporting). See the Classification section in `design-inputs.md` for definitions.

## Expected Content

- Software Requirements Specifications (per module)
- Label requirements
- Interface requirements

## Conventions

- **Naming**: `component-srs.md` at root; matching `.docx` in `formal/`
- Link back to the originating task document
- Note date and source of any data or finding

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| 2026-04-12 | Ben Xavier | Phase 4 authoring — `design-inputs.md` rewritten to Rev B with 34 DIs in 9 functional groups (G1–G9) and added by-group traceability breakdown. Document of record for DHF-PP3500-DI-001. |
| YYYY-MM-DD | XX | Initial version — created by /medtech-docs init |
