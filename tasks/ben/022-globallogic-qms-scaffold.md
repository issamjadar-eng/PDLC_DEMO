# 022 — GlobalLogic QMS Scaffold (internal/source-md)

**ID**: 022
**Created**: 2026-04-21
**Status**: In Progress
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: High

---

## Goals

Build a representative **Quality Management System (QMS)** for **GlobalLogic** (parent company of the PDLC_DEMO PainEase PCA project) under `docs/internal/source-md/`, organized by functional category. Each process area gets:
- A top-level **policy / manual section**
- **Standard Operating Procedures (SOPs)**
- **Work Instructions** where useful
- **Templates and Forms** referenced by the SOPs

All documents cite applicable **ISO / IEC / FDA** standards and clauses so the section structure is traceable to an authoritative source, not invented. This scaffold demonstrates how an agentic PDLC workflow would seed a MedTech QMS; demo content is clearly marked.

**Standards anchored:**
- ISO 13485:2016 — Medical devices QMS
- ISO 14971:2019 — Risk management
- IEC 62304:2006+A1:2015 — Medical device software lifecycle
- IEC 62366-1:2015 — Usability engineering
- IEC 81001-5-1:2021 — Health software / cybersecurity
- ISO 14155:2020 — Clinical investigation
- 21 CFR Part 820 — FDA QSR
- 21 CFR Part 11 — Electronic records / signatures
- EU MDR 2017/745 — European Medical Device Regulation

## Phases

The work is split into **six phases**. Each phase ends with a commit to `main` (no PR — single-user demo). No human review mid-stream; user reviews the whole thing at the end.

### Phase 1 — QMS foundation & quality-management core
`quality-management/` — Quality Manual, Document & Records Control SOP, Management Review SOP, Training SOP, Internal Audit SOP, CAPA SOP.
Anchors: ISO 13485 §4, §5, §6, §8.2.4, §8.5 · 21 CFR 820.20, 820.22, 820.25, 820.40, 820.100 · 21 CFR Part 11.

### Phase 2 — Design controls & planning
`design-controls/` — Design Control SOP, Design Planning SOP, Design Inputs SOP, Design Outputs SOP, Design Review SOP, Design Verification & Validation SOP, Design Transfer SOP, Design Change Control SOP.
Anchors: ISO 13485 §7.3 · 21 CFR 820.30 · FDA Design Control Guidance.

### Phase 3 — Risk management
`risk-management/` — Risk Management SOP, FMEA Work Instruction, Hazard Analysis Work Instruction, Risk Management Plan template, Risk Management File/Report template.
Anchor: ISO 14971:2019 · ISO/TR 24971:2020.

### Phase 4 — Software lifecycle & cybersecurity
`software-cybersecurity/` — Software Development Lifecycle SOP, Software Safety Classification Work Instruction, SOUP / OTS Management SOP, Cybersecurity SOP, SBOM Work Instruction.
Anchors: IEC 62304 · IEC 81001-5-1 · IEC 82304-1 · FDA Premarket Cybersecurity Guidance (2023).

### Phase 5 — Usability engineering & clinical evaluation
`usability-clinical/` — Usability Engineering SOP, Clinical Evaluation SOP, Use Specification template, Usability Validation Report template, Clinical Evaluation Plan template.
Anchors: IEC 62366-1:2015 · ISO 14155:2020 · FDA HFE/UE Guidance (2016) · MDCG 2020-6 (EU MDR clinical evaluation).

### Phase 6 — Supplier, production, and post-market
`supplier-production/` and `post-market/` — Supplier Management SOP, Purchasing Controls SOP, Production & Process Controls SOP, Incoming Inspection SOP, Post-Market Surveillance SOP, Complaint Handling SOP, Adverse Event / MDR Reporting SOP.
Anchors: ISO 13485 §7.4, §7.5, §8.2 · 21 CFR 820.50, 820.70, 820.80, 820.198 · 21 CFR 803 · EU MDR Annex III.

### Phase 7 (wrap) — Category READMEs + QMS index + commit
Top-level `source-md/qms-index.md` listing every document with standard anchors and doc IDs. Category READMEs with `## Conventions` and `## Changelog` per CLAUDE.md. Final commit.

## Conventions for this scaffold

- Every document has **docflow-compatible frontmatter** (source_file set to `N/A — authored-in-markdown`, doc_id assigned per GL-QMS numbering scheme, conversion_fidelity: `faithful`).
- Doc IDs follow the pattern `GL-<TYPE>-<AREA>-<NNN>` where TYPE ∈ {POL, SOP, WI, FORM, TMP, MAN}, AREA is a two-letter category code (QM, DC, RM, SW, UC, SP, PM), and NNN is a zero-padded sequence.
- Every SOP has these sections: Purpose · Scope · Responsibilities · Definitions · References (ISO/IEC/FDA) · Procedure · Records · Revision History.
- Every Template/Form is a fillable markdown stub with `{{PLACEHOLDER}}` tokens.
- `_Demo sample data — not for clinical use._` banner near the top of every file (per CLAUDE.md rule).
- Parent company **GlobalLogic** named in the Quality Manual and referenced from each SOP's header.

## Todos

- [x] P1 — Quality-management core (Quality Manual, Doc Control, Records, Mgmt Review, Training, Audit, CAPA) + commit
- [x] P2 — Design-controls SOPs + commit
- [x] P3 — Risk-management SOPs + templates + commit
- [x] P4 — Software lifecycle + cybersecurity SOPs + commit
- [x] P5 — Usability + clinical evaluation SOPs + templates + commit
- [x] P6 — Supplier + production + post-market SOPs + commit
- [x] P7 — Category READMEs + QMS index + final commit

## Changelog

- 2026-04-21: Task created. Plan split across 6 content phases + 1 wrap phase.
