---
source_file: "N/A — authored-in-markdown"
source_path: "software-cybersecurity/software-problem-resolution-sop.md"
doc_id: "GL-SOP-SW-003"
doc_type: "SOP"
title: "Software Problem Resolution"
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
  - doc_id: "IEC 62304 §9"
    title: null
    resolved: true
    match: null
    note: null
conversion_history:
  - date: "2026-04-21"
    source: "v1 — initial draft under task ben/022"
notes: null
---

# GL-SOP-SW-003 — Software Problem Resolution

_Demo sample data — not for clinical use._

**Document ID:** GL-SOP-SW-003
**Revision:** 1.0
**Parent SOP:** GL-SOP-SW-001

---

## 1. Purpose

Establish the process for reporting, evaluating, resolving, and tracking software problems, per IEC 62304 §9.

## 2. Scope

Problems observed in released or in-development GlobalLogic medical device software, from any source (developer, tester, user, PMS, supplier).

## 3. Responsibilities

- **Problem Reporter** — initiate the problem report
- **Problem Coordinator** — triage and assign
- **Assigned Engineer** — investigate and resolve
- **Change Control Board** — authorize fixes for released software
- **Risk Manager** — assess risk impact

## 4. Procedure

### 4.1 Problem Report Contents

- Problem description
- Environment (software version, configuration, hardware)
- Steps to reproduce
- Observed vs. expected behavior
- Severity (patient / user / functional) and urgency
- Classification: defect / feature request / documentation / SOUP / security

### 4.2 Triage

Within defined SLA (e.g., 2 business days for released-software issues), the Problem Coordinator assigns priority and owner. Security issues follow the accelerated path defined in GL-SOP-SW-004.

### 4.3 Evaluation and Risk Assessment

The Assigned Engineer performs root-cause analysis. Risk Manager re-evaluates affected hazards per GL-SOP-RM-001. If the problem introduces new or elevated risk, interim controls (field advisory, software patch, labeling change) may be deployed.

### 4.4 Resolution

For in-development problems, resolution is by normal development; for released software, resolution requires change control (GL-SOP-DC-008). Regression testing per the Software Development Plan.

### 4.5 Release and Communication

- Resolved issues are noted in release notes
- User-notification / field-action decisions per GL-SOP-PM-002 and GL-SOP-PM-003
- CAPA linkage (GL-SOP-QM-005) for systemic issues

### 4.6 Records

Problem reports retained per GL-SOP-QM-001. The anomaly list is a required input to each software release decision (per IEC 62304 §5.8.2).

## 5. Revision History

| Rev | Date | Author | Summary |
|---|---|---|---|
| 1.0 | 2026-04-21 | Ben Xavier (via Claude, task ben/022) | Initial demo SOP. |
