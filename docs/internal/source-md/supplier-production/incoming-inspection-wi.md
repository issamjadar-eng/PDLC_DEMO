---
source_file: "N/A — authored-in-markdown"
source_path: "supplier-production/incoming-inspection-wi.md"
doc_id: "GL-WI-SP-001"
doc_type: "WI"
title: "Incoming Inspection"
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
  - doc_id: "GL-SOP-SP-002"
    title: null
    resolved: true
    match: null
    note: "Parent SOP"
  - doc_id: "ISO 13485:2016 §7.4.3"
    title: null
    resolved: true
    match: null
    note: null
  - doc_id: "ANSI/ASQ Z1.4-2003 (R2018)"
    title: "Sampling Procedures and Tables for Inspection by Attributes"
    resolved: true
    match: null
    note: "AQL reference"
conversion_history:
  - date: "2026-04-21"
    source: "v1 — initial draft under task ben/022"
notes: null
---

# GL-WI-SP-001 — Incoming Inspection

_Demo sample data — not for clinical use._

**Document ID:** GL-WI-SP-001
**Revision:** 1.0
**Parent SOP:** GL-SOP-SP-002

---

## 1. Purpose

Procedure for verification of purchased product on receipt.

## 2. Inputs

- Purchase order
- Incoming Inspection Plan (per part)
- Supplier COA / CoC
- Applicable specification

## 3. Steps

1. Identify material and match to PO
2. Verify supplier is on ASL (GL-SOP-SP-001)
3. Select sampling plan (AQL per ANSI/ASQ Z1.4 or equivalent, or 100% inspection per plan)
4. Execute measurements / inspections against spec; record on GL-FORM-SP-002 (inspection section)
5. Review COA / CoC — values within spec
6. **Pass** → release to stock with lot tag and traceability record
7. **Fail** → hold, raise NCR (GL-SOP-SP-004)

## 4. Records

- Incoming Inspection record per lot (retained per GL-SOP-QM-001)
- COA / CoC filed by lot

## 5. Revision History

| Rev | Date | Author | Summary |
|---|---|---|---|
| 1.0 | 2026-04-21 | Ben Xavier (via Claude, task ben/022) | Initial demo WI. |
