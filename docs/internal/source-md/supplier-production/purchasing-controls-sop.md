---
source_file: "N/A — authored-in-markdown"
source_path: "supplier-production/purchasing-controls-sop.md"
doc_id: "GL-SOP-SP-002"
doc_type: "SOP"
title: "Purchasing Controls"
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
  - doc_id: "ISO 13485:2016 §7.4.2–§7.4.3"
    title: "Purchasing information; verification of purchased product"
    resolved: true
    match: null
    note: null
  - doc_id: "21 CFR 820.50"
    title: "Purchasing controls"
    resolved: true
    match: null
    note: null
conversion_history:
  - date: "2026-04-21"
    source: "v1 — initial draft under task ben/022"
notes: null
---

# GL-SOP-SP-002 — Purchasing Controls

_Demo sample data — not for clinical use._

**Document ID:** GL-SOP-SP-002
**Revision:** 1.0
**Parent SOP:** GL-SOP-SP-001

---

## 1. Purpose

Ensure purchased product and services meet specified requirements — per ISO 13485:2016 §7.4.2–§7.4.3 and 21 CFR 820.50.

## 2. Scope

All purchase orders for components, materials, services, and software affecting product quality.

## 3. Procedure

### 3.1 Purchasing Information (§7.4.2)

Each purchase order references or embeds:

- Part number and revision
- Material or service specification
- Acceptance criteria
- Requirements for product, services, procedures, processes and equipment
- Requirements for qualification of supplier personnel (where applicable)
- Quality management system requirements (per quality agreement)
- Change notification obligations

### 3.2 Supplier Selection

Only suppliers on the Approved Supplier List (GL-SOP-SP-001) may receive purchase orders for affected products. Emergency off-ASL purchases require documented deviation approval by Supplier Quality and Design Owner.

### 3.3 Verification of Purchased Product (§7.4.3)

Each incoming lot/shipment is verified per GL-WI-SP-001 — one or more of:

- Review of certificate of analysis (COA) / certificate of conformance (CoC)
- Incoming inspection per approved plan (AQL / skip-lot / 100%)
- Source inspection or audit (for critical, high-risk items)

### 3.4 Disposition

- Conforming → release to stock / WIP
- Nonconforming → hold + NCR (GL-SOP-SP-004)

### 3.5 Change Notification

Supplier change notifications are assessed by Design Engineering + Supplier Quality for impact, and routed through Design Change Control (GL-SOP-DC-008) when significant.

## 4. Records Generated

| Record | Retained by | Retention |
|---|---|---|
| Purchase Orders | Sourcing / Finance | Per GL-SOP-QM-001 |
| Incoming verification records | Quality | Per GL-SOP-QM-001 |

## 5. Revision History

| Rev | Date | Author | Summary |
|---|---|---|---|
| 1.0 | 2026-04-21 | Ben Xavier (via Claude, task ben/022) | Initial demo SOP. |
