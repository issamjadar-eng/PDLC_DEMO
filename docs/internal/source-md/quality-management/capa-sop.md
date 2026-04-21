---
source_file: "N/A — authored-in-markdown"
source_path: "quality-management/capa-sop.md"
doc_id: "GL-SOP-QM-005"
doc_type: "SOP"
title: "Corrective Action / Preventive Action (CAPA)"
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
  - doc_id: "ISO 13485:2016 §8.5"
    title: "Improvement (including corrective and preventive action)"
    resolved: true
    match: null
    note: null
  - doc_id: "21 CFR 820.100"
    title: "Corrective and preventive action"
    resolved: true
    match: null
    note: null
conversion_history:
  - date: "2026-04-21"
    source: "v1 — initial draft under task ben/022"
notes: null
---

# GL-SOP-QM-005 — Corrective Action / Preventive Action (CAPA)

_Demo sample data — not for clinical use._

**Document ID:** GL-SOP-QM-005
**Revision:** 1.0
**Effective Date:** 2026-04-21
**Owner:** VP Quality, GlobalLogic MedTech

---

## 1. Purpose

Establish procedures for identifying, investigating, and acting on actual nonconformities (Corrective Action) and potential nonconformities (Preventive Action), per ISO 13485:2016 §8.5.2–§8.5.3 and 21 CFR 820.100.

## 2. Scope

Applies to all nonconformities and potential nonconformities identified via any source, including:

- Complaints and field events (GL-SOP-PM-002)
- Internal audits (GL-SOP-QM-004)
- External audits and regulatory inspections
- Supplier nonconformances
- Process monitoring and trending
- Servicing and installation issues
- Post-market surveillance (GL-SOP-PM-001)
- Management Review inputs (GL-SOP-QM-002)

## 3. Responsibilities

| Role | Responsibility |
|---|---|
| CAPA Owner | Investigate root cause; define and implement actions; verify effectiveness |
| CAPA Coordinator (Quality) | Maintain CAPA register; chair CAPA Review Board; track aging; escalate overdue |
| CAPA Review Board | Cross-functional review of major CAPAs; approve closure |
| Management Representative | Approve CAPA effectiveness for major events; report CAPA status to Management Review |

## 4. Definitions

- **Correction** — Action to eliminate a detected nonconformity (e.g., rework, replacement).
- **Corrective action** — Action to eliminate the **cause** of a detected nonconformity or other undesirable situation.
- **Preventive action** — Action to eliminate the cause of a **potential** nonconformity.
- **Root cause** — Underlying reason that, if eliminated, prevents recurrence.

## 5. References

- ISO 13485:2016 §8.5
- 21 CFR 820.100
- FDA Guidance — "Quality System Regulation — Process Validation" (where relevant to process CAPAs)

## 6. Procedure

### 6.1 Initiation

Any employee may initiate a CAPA by filing a **CAPA Form (GL-FORM-QM-001)**. The CAPA Coordinator logs it in the CAPA register and assigns a CAPA-ID `GL-CAPA-YYYY-NNN`.

### 6.2 Triage and Risk Assessment

Within **5 business days** of initiation, the CAPA Coordinator and appropriate process owner assess:

- Issue severity (patient harm potential, regulatory exposure, customer impact)
- Scope (single event vs. systemic)
- CAPA classification: **Minor, Major, or Critical**

Critical CAPAs involve potential serious public-health issues, regulatory reporting obligations, or field corrections; they are escalated immediately to the Management Representative.

### 6.3 Investigation and Root-Cause Analysis

The CAPA Owner conducts a root-cause analysis using appropriate technique (5 Whys, Ishikawa/fishbone, Fault Tree). Findings documented on GL-FORM-QM-001.

### 6.4 Action Plan

The CAPA Owner defines:

- Correction (contain the current issue)
- Corrective Action (eliminate root cause)
- Preventive Action (where applicable — prevent in related processes/products)
- Action owner and due date per step
- Effectiveness check — what evidence will show the cause was eliminated and how long to monitor

For product-affecting CAPAs, the Action Plan is reviewed for **risk-management impact** (GL-SOP-RM-001) — update Risk Management File if new or altered risks are identified.

### 6.5 Implementation

Actions executed per plan. Interim controls remain in place until the CAPA is closed.

### 6.6 Effectiveness Verification

After implementation, the CAPA Owner provides objective evidence (trend data, re-audit, re-verification) over a defined monitoring window (typically ≥ 3 months or 3 production cycles, whichever is longer). The CAPA Review Board (or Management Representative for Critical) approves closure.

### 6.7 Trending

The CAPA Coordinator trends CAPA data quarterly — aging, categories, recurring root causes, effectiveness rate. Trends are an input to Management Review.

### 6.8 Regulatory Notification

If a CAPA corresponds to a reportable event (21 CFR 803, EU MDR Art. 87), the Post-Market Surveillance / Regulatory team follows **GL-SOP-PM-003 — Adverse Event / MDR Reporting**. CAPA and regulatory reporting proceed in parallel.

## 7. Records Generated

| Record | Retained by | Retention |
|---|---|---|
| CAPA Form (GL-FORM-QM-001) — per CAPA | Quality | 10 years |
| CAPA Register | Quality | Current + archive |
| Effectiveness evidence | Quality | 10 years |

## 8. Revision History

| Rev | Date | Author | Summary |
|---|---|---|---|
| 1.0 | 2026-04-21 | Ben Xavier (via Claude, task ben/022) | Initial demo SOP. |
