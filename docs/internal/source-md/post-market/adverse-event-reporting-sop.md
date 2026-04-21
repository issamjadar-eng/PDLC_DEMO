---
source_file: "N/A — authored-in-markdown"
source_path: "post-market/adverse-event-reporting-sop.md"
doc_id: "GL-SOP-PM-003"
doc_type: "SOP"
title: "Adverse Event Reporting (Vigilance)"
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
  - doc_id: "21 CFR Part 803"
    title: "Medical Device Reporting (MDR)"
    resolved: true
    match: null
    note: "US anchor"
  - doc_id: "21 CFR Part 806"
    title: "Medical Devices; Reports of Corrections and Removals"
    resolved: true
    match: null
    note: null
  - doc_id: "EU MDR 2017/745 Art. 87–89"
    title: "Reporting of serious incidents and FSCAs"
    resolved: true
    match: null
    note: "EU anchor"
  - doc_id: "MDCG 2023-3 Rev.1"
    title: "Vigilance terms and concepts"
    resolved: true
    match: null
    note: null
  - doc_id: "ISO 13485:2016 §8.2.3"
    title: "Reporting to regulatory authorities"
    resolved: true
    match: null
    note: null
conversion_history:
  - date: "2026-04-21"
    source: "v1 — initial draft under task ben/022"
notes: null
---

# GL-SOP-PM-003 — Adverse Event Reporting (Vigilance)

_Demo sample data — not for clinical use._

**Document ID:** GL-SOP-PM-003
**Revision:** 1.0
**Owner:** VP Regulatory / Vigilance Lead, GlobalLogic MedTech

---

## 1. Purpose

Determine reportability and submit required reports to regulatory authorities — per **21 CFR Part 803** (US MDR), **21 CFR Part 806** (corrections/removals), **EU MDR Art. 87–89**, and informed by **MDCG 2023-3 Rev.1**. Align with ISO 13485:2016 §8.2.3.

## 2. Scope

All events, complaints (GL-SOP-PM-002), and field observations concerning GlobalLogic devices placed on markets where reporting obligations apply.

## 3. Responsibilities

- **Vigilance Lead (RA)** — assess reportability; submit reports; maintain files
- **Complaint Handling Lead** — escalate per-event
- **PRRC (EU, per MDR Art. 15)** — oversight for EU markets
- **VP Quality** — ensure CAPA integration

## 4. Definitions

- **21 CFR 803**: *Reportable event* — a death, serious injury, or malfunction that would be likely to cause or contribute to death or serious injury if the malfunction were to recur.
- **EU MDR**: *Serious incident* (Art. 87) — any malfunction, deterioration, inaccuracy of labeling, or IFU of a device, and use error, that led or might have led to any of: death of a patient/user/other person, serious deterioration of health, serious public-health threat.
- **FSCA** — Field Safety Corrective Action.
- **FSN** — Field Safety Notice.

## 5. References

- 21 CFR Part 803 (MDR) and 806 (corrections/removals)
- EU MDR 2017/745 Art. 87, 88, 89
- MDCG 2023-3 Rev.1 — Vigilance terms and concepts
- MDCG 2023-4 — Medical Device Incident Reporting
- Health Canada / Swissmedic / MHRA / PMDA obligations as applicable

## 6. Procedure

### 6.1 Reportability Assessment

Within **2 calendar days** of receiving a complaint or event:

1. Is the device a GlobalLogic product placed on a market with reporting obligations?
2. Does the event meet the jurisdictional reportability criteria?
3. Determine report type (US 3500A MDR report; EU MIR — Manufacturer Incident Report via Eudamed; other jurisdictions)

### 6.2 Reporting Timelines

| Jurisdiction | Event | Timeline |
|---|---|---|
| US (21 CFR 803) | Death / serious injury (from manufacturer) | 30 calendar days |
| US (21 CFR 803) | Event requiring remedial action to prevent unreasonable risk of substantial harm | 5 business days |
| US (21 CFR 803) | Malfunction (likely to cause/contribute to death or SI if recurred) | 30 calendar days |
| EU (MDR Art. 87) | Serious public-health threat | 2 calendar days |
| EU (MDR Art. 87) | Death or unanticipated serious deterioration | 10 calendar days |
| EU (MDR Art. 87) | Other serious incidents | 15 calendar days |
| EU (MDR Art. 88) | FSCA | Trend & FSCA reports per MDCG 2023-4 |

Timelines are maximum — submit sooner when possible. Supplemental / follow-up reports filed as investigation progresses.

### 6.3 Submission

- US: eMDR via FDA ESG
- EU: Eudamed Vigilance module (MIR)
- Other: jurisdiction-specific portals; retain confirmation of submission

### 6.4 FSCA / FSN

When a field action is needed:
- Draft FSCA rationale, scope (lot/SN/model), action, and customer instructions
- FSN drafted in plain language; translated where required
- Coordinate with notified body and competent authorities
- Track customer acknowledgement

### 6.5 Trend Reporting

Per MDR Art. 88 and MDCG 2023-4, statistically significant increases in non-serious incidents or expected side effects are trended and reported.

### 6.6 Records

- Event / report file (inputs, reportability analysis, submitted report(s), follow-ups, closure)
- FSCA / FSN records
- CAPA linkage

## 7. Records Generated

Per GL-SOP-QM-001 records retention — at least 10 years for implantables and per jurisdictional rules for others. FSCA records retained per EU MDR Annex III §1.1(d).

## 8. Revision History

| Rev | Date | Author | Summary |
|---|---|---|---|
| 1.0 | 2026-04-21 | Ben Xavier (via Claude, task ben/022) | Initial demo SOP. |
