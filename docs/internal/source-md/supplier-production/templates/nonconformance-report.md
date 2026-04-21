---
source_file: "N/A — authored-in-markdown"
source_path: "supplier-production/templates/nonconformance-report.md"
doc_id: "GL-FORM-SP-002"
doc_type: "FORM"
title: "Nonconformance Report (NCR)"
format: "md"
conversion_date: "2026-04-21"
conversion_method: "claude-authored"
conversion_fidelity: "faithful"
pages: null
sheets: null
has_images: false
image_count: 0
has_tables: true
has_form_fields: true
references:
  - doc_id: "GL-SOP-SP-004"
    title: null
    resolved: true
    match: null
    note: "Parent SOP"
  - doc_id: "ISO 13485:2016 §8.3"
    title: null
    resolved: true
    match: null
    note: null
conversion_history:
  - date: "2026-04-21"
    source: "v1 — initial draft under task ben/022"
notes: null
---

# GL-FORM-SP-002 — Nonconformance Report (NCR)

_Demo sample data — not for clinical use._

**Form ID:** GL-FORM-SP-002 (template)
**Revision:** 1.0
**Parent SOP:** GL-SOP-SP-004

---

## 1. Identification

| Field | Value |
|---|---|
| NCR ID | `GL-NCR-{{YYYY}}-{{NNN}}` |
| Date | `{{YYYY-MM-DD}}` |
| Reporter | `{{name, role}}` |
| Source | ☐ Incoming inspection ☐ In-process ☐ Final ☐ Field return ☐ Internal finding ☐ Supplier notification |
| Product / Component | `{{}}` |
| Part Number / Lot / SN | `{{}}` |
| Supplier (if applicable) | `{{}}` |
| PO / Lot Qty | `{{}}` |

## 2. Nonconformance Description

**Requirement:** `{{specification or drawing revision, clause}}`
**Observation:** `{{what was observed, how detected, measurements}}`

## 3. Impact Assessment

- Other units potentially affected: `{{lot range, other builds}}`
- Risk impact (link to RMF — GL-SOP-RM-001): `{{}}`
- Released product at risk? ☐ Yes — `{{qty, customers}}` ☐ No
- Regulatory reportability (21 CFR 806 / MDR Art. 87) — see GL-SOP-PM-003: ☐ Yes ☐ No ☐ Under review

## 4. Disposition

☐ Use-as-is (with rationale)
☐ Rework (per `{{procedure}}`)
☐ Repair (rationale)
☐ Scrap
☐ Return to supplier

**Rationale:**
`{{}}`

## 5. Approvals

| Role | Name | Date | Signature |
|---|---|---|---|
| QE | | | |
| Design Engineering | | | |
| Design Owner (for released product) | | | |
| Regulatory (if reportable) | | | |

## 6. CAPA Linkage

- CAPA required? ☐ Yes — `GL-CAPA-{{}}` ☐ No (rationale)
- SCAR required? ☐ Yes — `{{SCAR-ID}}` ☐ No

## 7. Revision History

| Rev | Date | Author | Summary |
|---|---|---|---|
| 1.0 | 2026-04-21 | Ben Xavier (via Claude, task ben/022) | Initial template. |
