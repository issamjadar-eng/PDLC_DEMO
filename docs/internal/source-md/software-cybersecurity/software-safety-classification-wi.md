---
source_file: "N/A — authored-in-markdown"
source_path: "software-cybersecurity/software-safety-classification-wi.md"
doc_id: "GL-WI-SW-001"
doc_type: "WI"
title: "Software Safety Classification"
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
  - doc_id: "GL-SOP-SW-001"
    title: "Medical Device Software Lifecycle"
    resolved: true
    match: null
    note: "Parent SOP"
  - doc_id: "IEC 62304 §4.3"
    title: null
    resolved: true
    match: null
    note: null
conversion_history:
  - date: "2026-04-21"
    source: "v1 — initial draft under task ben/022"
notes: null
---

# GL-WI-SW-001 — Software Safety Classification

_Demo sample data — not for clinical use._

**Document ID:** GL-WI-SW-001
**Revision:** 1.0
**Parent SOP:** GL-SOP-SW-001

---

## 1. Purpose

Provide the procedure and decision flow to assign a software safety class (A/B/C) per IEC 62304 §4.3.

## 2. Prerequisites

- Preliminary architecture / data flow
- Preliminary hazard analysis (GL-WI-RM-001)
- Understanding of external (non-software) risk controls

## 3. Decision Flow

```
For each software system (and decomposable software item):

  1. Could a failure of this software contribute to a hazardous
     situation that results in harm to the patient, user, or a
     bystander?
      │
      ▼
     No  →  Class A
      │
      Yes
      │
      ▼
  2. Are there EXTERNAL risk control measures (not implemented in
     software) that PREVENT the hazardous situation or REDUCE the
     harm to minor injury or less?
      │
      ▼
     Yes, reduce to "not serious"    →  Class B
     Yes, prevent entirely           →  Class A
     No                              →  Class C

  3. Could the hazardous situation result in DEATH or SERIOUS INJURY?
      │
      ▼
     Class B if Yes-with-external-controls sufficient to prevent serious injury
     Class C otherwise
```

## 4. Documentation

Record in the Software Development Plan (GL-TMP-SW-001):

- Software system and decomposable items
- Preliminary hazards each contributes to
- External risk controls relied upon (and how they are verified)
- Assigned class
- Rationale
- Reviewed by Risk Manager and QE

## 5. Revision History

| Rev | Date | Author | Summary |
|---|---|---|---|
| 1.0 | 2026-04-21 | Ben Xavier (via Claude, task ben/022) | Initial demo WI. |
