---
source_file: "N/A — authored-in-markdown"
source_path: "post-market/complaint-handling-sop.md"
doc_id: "GL-SOP-PM-002"
doc_type: "SOP"
title: "Complaint Handling"
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
  - doc_id: "ISO 13485:2016 §8.2.2"
    title: "Complaint handling"
    resolved: true
    match: null
    note: null
  - doc_id: "21 CFR 820.198"
    title: "Complaint files"
    resolved: true
    match: null
    note: null
conversion_history:
  - date: "2026-04-21"
    source: "v1 — initial draft under task ben/022"
notes: null
---

# GL-SOP-PM-002 — Complaint Handling

_Demo sample data — not for clinical use._

**Document ID:** GL-SOP-PM-002
**Revision:** 1.0
**Owner:** Complaint Handling Lead / VP Quality, GlobalLogic MedTech

---

## 1. Purpose

Receive, evaluate, investigate, and respond to customer complaints — per ISO 13485:2016 §8.2.2 and 21 CFR 820.198.

## 2. Scope

All complaints received through any channel regarding GlobalLogic devices in the field.

## 3. Definitions

- **Complaint** — Any written, electronic, or oral communication that alleges deficiencies related to the identity, quality, durability, reliability, usability, safety, or performance of a device after it is released for distribution (21 CFR 820.3(b)).

## 4. Procedure

### 4.1 Intake

Complaints received via customer support, field, sales, email, phone, social media, or regulator channels are logged within **1 business day** in the Complaint Register.

### 4.2 Initial Assessment

Within defined SLA:
- Is it a complaint per §820.3(b)? If not — file as feedback (still useful for PMS)
- Severity: patient harm reported? device malfunction?
- **Reportability triage** per GL-SOP-PM-003 — if reportable, regulatory clock starts
- Is field action required (hold/recall/advisory)?

### 4.3 Investigation

For each complaint:
- Obtain device return where feasible
- Root-cause analysis
- Link to risk management (GL-SOP-RM-001) — known vs. new hazard
- Determine if CAPA is required (GL-SOP-QM-005)
- Link to NCRs (GL-SOP-SP-004) if production-related

### 4.4 Response to Complainant

- Acknowledge receipt promptly
- Communicate final outcome per HIPAA / GDPR / applicable privacy rules

### 4.5 Records

Each complaint file contains:
- The complaint and all communications
- Investigation record
- Disposition and rationale
- Whether a 21 CFR 803 / EU MDR report was made
- Whether CAPA was initiated

### 4.6 Trending

Complaints are trended by device, failure mode, user error, and clinical outcome — feeds PMS (GL-SOP-PM-001).

## 5. Records Generated

- Complaint files per §820.198 — retained per GL-SOP-QM-001
- Complaint trend reports

## 6. Revision History

| Rev | Date | Author | Summary |
|---|---|---|---|
| 1.0 | 2026-04-21 | Ben Xavier (via Claude, task ben/022) | Initial demo SOP. |
