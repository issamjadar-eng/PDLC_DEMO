---
source_file: "N/A — authored-in-markdown"
source_path: "design-controls/design-outputs-sop.md"
doc_id: "GL-SOP-DC-004"
doc_type: "SOP"
title: "Design Outputs"
format: "md"
conversion_date: "2026-04-21"
conversion_method: "claude-authored"
conversion_fidelity: "faithful"
pages: null
sheets: null
has_images: false
image_count: 0
has_tables: true
has_form_fields: false
references:
  - doc_id: "ISO 13485:2016 §7.3.4"
    title: "Design and development outputs"
    resolved: true
    match: null
    note: null
  - doc_id: "21 CFR 820.30(d)"
    title: "Design output"
    resolved: true
    match: null
    note: null
conversion_history:
  - date: "2026-04-21"
    source: "v1 — initial draft under task ben/022"
notes: null
---

# GL-SOP-DC-004 — Design Outputs

_Demo sample data — not for clinical use._

**Document ID:** GL-SOP-DC-004
**Revision:** 1.0
**Effective Date:** 2026-04-21
**Owner:** VP R&D, GlobalLogic MedTech

---

## 1. Purpose

Define how Design Outputs are produced, reviewed, approved, and released — per ISO 13485:2016 §7.3.4 and 21 CFR 820.30(d).

## 2. Scope

All Design Outputs of a product covered by the GlobalLogic QMS, including drawings, specifications, software source and build artifacts, labeling, packaging, DMR subsets, and supporting analyses.

## 3. Responsibilities

- **Design Engineering** (HW, FW, SW, mechanical) — produce outputs
- **Quality Engineering** — participate in output review for adequacy vs. inputs
- **Design Owner** — approve Design Output release

## 4. Definitions

- **Design Output** — Results of a design effort at each design phase and at the end of the total design effort (21 CFR 820.3(g)).
- **Essential Output** — An output that is essential for the proper functioning of the device, identified as such in the design output record.

## 5. References

- ISO 13485:2016 §7.3.4
- 21 CFR 820.30(d)
- FDA Design Control Guidance §C

## 6. Procedure

### 6.1 Required Attributes (ISO 13485 §7.3.4)

Design Outputs shall:

- Meet the requirements of the Design Inputs (verified per GL-SOP-DC-006)
- Provide appropriate information for **purchasing, production, and service provision**
- Contain or reference product **acceptance criteria**
- Specify **characteristics of the product that are essential** for its safe and proper use

Each of these is confirmed during Output Review before release.

### 6.2 Categories (non-exhaustive)

| Category | Typical Outputs |
|---|---|
| System | Block diagrams, architecture description, interface control docs |
| Hardware | BOM, schematics, PCB layouts, mechanical drawings, tolerance stacks, material specs |
| Firmware | Source code, build artifacts, flash images, bootloader config |
| Software (SaMD/SiMD) | Source code, unit/integration test code, configuration-management records (GL-SOP-SW-001), SBOM (GL-SOP-SW-005) |
| Labeling | IFU, UDI, user manuals, training materials |
| Manufacturing | Process specs, work instructions (linked to DMR), fixtures, test stations |
| Servicing | Service manuals, calibration procedures |

### 6.3 Output Review

Each output is reviewed before approval. Output Review confirms:

- Output satisfies the corresponding Design Inputs
- Output is unambiguous and usable by its downstream consumer
- Essential characteristics are identified
- Acceptance criteria are stated or referenced

Output Review is captured within the Design Review at the relevant phase gate (GL-SOP-DC-005), OR as a standalone recorded review for high-risk outputs.

### 6.4 Approval and Release

Approved outputs are released under Document Control (GL-SOP-QM-001). Released outputs are subject to change control under GL-SOP-DC-008. Outputs that become part of the Device Master Record (DMR) flow into manufacturing via GL-SOP-DC-007 (Design Transfer).

### 6.5 Traceability

The trace matrix (maintained per GL-SOP-DC-003) must link each Design Input to ≥ 1 Design Output. Orphan inputs (no output) are surfaced during Design Review and must be resolved.

## 7. Records Generated

| Record | Retained by | Retention |
|---|---|---|
| Design Output documents (all revisions) | DHF + DMR | Per GL-SOP-QM-001 |
| Output Review records | DHF | Per GL-SOP-QM-001 |

## 8. Revision History

| Rev | Date | Author | Summary |
|---|---|---|---|
| 1.0 | 2026-04-21 | Ben Xavier (via Claude, task ben/022) | Initial demo SOP. |
