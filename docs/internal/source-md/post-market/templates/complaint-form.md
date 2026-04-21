---
source_file: "N/A — authored-in-markdown"
source_path: "post-market/templates/complaint-form.md"
doc_id: "GL-FORM-PM-001"
doc_type: "FORM"
title: "Complaint Form"
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
  - doc_id: "GL-SOP-PM-002"
    title: null
    resolved: true
    match: null
    note: "Parent SOP"
  - doc_id: "21 CFR 820.198"
    title: null
    resolved: true
    match: null
    note: null
conversion_history:
  - date: "2026-04-21"
    source: "v1 — initial draft under task ben/022"
notes: null
---

# GL-FORM-PM-001 — Complaint Form

_Demo sample data — not for clinical use._

**Form ID:** GL-FORM-PM-001 (template)
**Revision:** 1.0
**Parent SOP:** GL-SOP-PM-002

---

## 1. Intake

| Field | Value |
|---|---|
| Complaint ID | `GL-CPL-{{YYYY}}-{{NNNN}}` |
| Received Date | `{{YYYY-MM-DD}}` |
| Received By | `{{}}` |
| Channel | ☐ Phone ☐ Email ☐ Web ☐ Sales ☐ Service ☐ Regulator ☐ Social |

## 2. Complainant

| Field | Value |
|---|---|
| Name / Organization | `{{}}` |
| Role | ☐ Patient ☐ User / Clinician ☐ Biomed / Service ☐ Distributor ☐ Other |
| Contact | `{{HIPAA/GDPR-compliant record}}` |

## 3. Device

| Field | Value |
|---|---|
| Device / Model | `{{}}` |
| Serial / UDI | `{{}}` |
| Lot | `{{}}` |
| Configuration / SW version | `{{}}` |

## 4. Event Description

**Date of event:** `{{}}`
**Location / environment:** `{{}}`
**What happened:** `{{narrative, reproducibility, frequency}}`
**Patient involvement:** ☐ None ☐ Potential ☐ Injury — `{{details}}` ☐ Death

## 5. Triage

| Check | Result |
|---|---|
| Meets complaint definition per 21 CFR 820.3(b) | ☐ Yes ☐ No (filed as feedback) |
| Reportable assessment (GL-SOP-PM-003) | ☐ US 21 CFR 803 ☐ EU MDR Art. 87 ☐ Other — `{{}}` ☐ Not reportable |
| Field action review needed | ☐ Yes ☐ No |
| Risk — new or elevated? | ☐ Yes — feed RMF ☐ No |

## 6. Investigation

**Device returned:** ☐ Yes ☐ No
**Root cause:** `{{}}`
**Linked RMF / Hazard ID:** `{{}}`
**CAPA:** ☐ `GL-CAPA-{{}}` ☐ Not required — rationale: `{{}}`
**NCR:** ☐ `GL-NCR-{{}}` ☐ N/A
**SCAR:** ☐ `{{}}` ☐ N/A

## 7. Reportable Event Record

(If reportable per GL-SOP-PM-003, cross-reference the vigilance file.)

## 8. Closure

| Role | Name | Date | Signature |
|---|---|---|---|
| Complaint Handler | | | |
| Vigilance Lead (if reportable) | | | |
| Complaint Lead / VP Quality | | | |

## 9. Revision History

| Rev | Date | Author | Summary |
|---|---|---|---|
| 1.0 | 2026-04-21 | Ben Xavier (via Claude, task ben/022) | Initial template. |
