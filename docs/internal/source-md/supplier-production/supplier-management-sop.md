---
source_file: "N/A — authored-in-markdown"
source_path: "supplier-production/supplier-management-sop.md"
doc_id: "GL-SOP-SP-001"
doc_type: "SOP"
title: "Supplier Management"
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
  - doc_id: "ISO 13485:2016 §7.4"
    title: "Purchasing"
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

# GL-SOP-SP-001 — Supplier Management

_Demo sample data — not for clinical use._

**Document ID:** GL-SOP-SP-001
**Revision:** 1.0
**Effective Date:** 2026-04-21
**Owner:** Director of Supplier Quality, GlobalLogic MedTech

---

## 1. Purpose

Establish how GlobalLogic qualifies, monitors, and disqualifies suppliers of components, materials, services, and software that affect medical-device quality — per ISO 13485:2016 §7.4.1 and 21 CFR 820.50.

## 2. Scope

All external providers whose output affects product quality — component manufacturers, contract manufacturers, test labs, sterilization providers, software/SOUP providers, calibration services, critical service providers.

## 3. Responsibilities

| Role | Responsibility |
|---|---|
| Director of Supplier Quality | Own Approved Supplier List (ASL) |
| Sourcing | Execute supplier selection |
| Quality Engineering | Supplier evaluations, audits, SCAR |
| Design Engineering | Specify requirements to suppliers |

## 4. Definitions

- **Supplier** — An organization providing a product or service.
- **ASL** — Approved Supplier List.
- **SCAR** — Supplier Corrective Action Request.

## 5. References

- ISO 13485:2016 §7.4 Purchasing
- 21 CFR 820.50 Purchasing controls
- ISO 19011:2018 (when auditing)

## 6. Procedure

### 6.1 Supplier Classification

Each supplier is classified by **risk to product quality**:

| Class | Examples | Controls |
|---|---|---|
| **Critical** | Active pharmaceutical ingredient, sterilant, active electronic components, contract manufacturer, SOUP vendors | On-site audit; QA agreement; close monitoring |
| **Major** | Key mechanical parts, packaging | Desk audit + quality agreement |
| **Minor** | Commodity / indirect | Evidence of business system; COAs |

### 6.2 Initial Qualification

Qualification Package (GL-FORM-SP-001):
- Supplier questionnaire
- Certifications (ISO 13485, ISO 9001, FDA registration, CE MDR)
- Sample quality plans
- Financial / capacity stability indicators (for Critical)
- For Critical: on-site audit per GL-SOP-QM-004 (applied to external audits)

### 6.3 Quality Agreement

For Critical and Major suppliers, a quality agreement codifies: change-notification obligations, NCR/SCAR handling, audit rights, data retention, subcontracting rules, labeling/segregation, cybersecurity responsibilities (for SOUP/software suppliers — see GL-SOP-SW-002), and right-to-know for regulatory inspections.

### 6.4 Approved Supplier List (ASL)

Maintained by Supplier Quality. Each entry: supplier, scope (what they supply), class, qualification date, next re-eval due, quality agreement ref, open SCAR count.

### 6.5 Ongoing Monitoring

- Incoming inspection data (GL-WI-SP-001) trended per supplier
- NCRs linked to supplier (GL-SOP-SP-004)
- SCAR issued for recurring or high-impact issues
- Scheduled re-evaluation cadence (Critical ≤ 2y, Major ≤ 3y, Minor on-demand)

### 6.6 Disqualification

Triggers: repeated failures, loss of certification, unresolved SCARs, regulatory action against the supplier, supply-chain risk (sanctions, insolvency). Disqualification follows Document Change Control for any affected documents and may trigger CAPA (GL-SOP-QM-005).

## 7. Records Generated

| Record | Retained by | Retention |
|---|---|---|
| Qualification Packages (GL-FORM-SP-001) | Supplier Quality | 10 years after disqualification |
| Quality Agreements | Supplier Quality + Legal | Term + 10 years |
| ASL (current + archive) | Supplier Quality | — |
| SCARs | Supplier Quality | 10 years |

## 8. Revision History

| Rev | Date | Author | Summary |
|---|---|---|---|
| 1.0 | 2026-04-21 | Ben Xavier (via Claude, task ben/022) | Initial demo SOP. |
