---
source_file: "N/A — authored-in-markdown"
source_path: "risk-management/master-harms-list.md"
doc_id: "GL-STD-RM-002"
doc_type: "STD"
title: "Master Harms List"
format: "md"
conversion_date: "2026-04-27"
conversion_method: "claude-authored"
conversion_fidelity: "faithful"
pages: null
sheets: null
has_images: false
image_count: 0
has_tables: true
has_form_fields: false
references:
  - doc_id: "ISO 14971:2019 §C.2"
    title: "Categories of harm"
    resolved: true
    match: null
    note: "Anchor for harm taxonomy"
  - doc_id: "GL-STD-RM-001"
    title: "Risk Assessment Criteria"
    resolved: true
    match: null
    note: "Severity scale"
conversion_history:
  - date: "2026-04-27"
    source: "v1 — added under task ben/036 to standardize harm taxonomy across DHF risk files"
notes: "Pre-classified severity anchors per harm. Hazard Analysis authors (GL-WI-RM-001) cite Harm-IDs from this list rather than redefining harms per project."
---

# GL-STD-RM-002 — Master Harms List

_Demo sample data — not for clinical use._

**Document ID:** GL-STD-RM-002
**Revision:** 1.0
**Effective Date:** 2026-04-27
**Owner:** VP Quality, GlobalLogic MedTech

---

## 1. Purpose

Provide a canonical, pre-classified list of harms applicable to GlobalLogic medical devices. Each harm has a stable Harm-ID, a clinical definition, and a default severity anchor (per GL-STD-RM-001 §3). Project-level hazard analyses cite Harm-IDs rather than redefining harms.

## 2. Scope

Applies to every device produced under the GlobalLogic QMS. Project hazard analyses **may** introduce additional product-specific harms but **shall** cite Harm-IDs from this list when an existing entry fits.

## 3. Master Harm Taxonomy

Harms are grouped into eight categories aligned with ISO 14971:2019 Annex C.2. Severity (S) is the **default anchor** — project hazard analyses may justify a different severity in writing if device-specific context warrants.

### 3.1 Patient — Cardiovascular

| Harm-ID | Harm | Default S | Notes |
|---|---|:-:|---|
| HARM-PCV-001 | Cardiac arrhythmia | 4 | Catastrophic if sustained ventricular |
| HARM-PCV-002 | Hypotension (transient) | 3 | |
| HARM-PCV-003 | Hypotension (severe / sustained) | 4 | |
| HARM-PCV-004 | Hemorrhage requiring intervention | 4 | |
| HARM-PCV-005 | Cardiac arrest | 5 | |

### 3.2 Patient — Respiratory

| Harm-ID | Harm | Default S | Notes |
|---|---|:-:|---|
| HARM-PRS-001 | Respiratory depression (transient) | 3 | |
| HARM-PRS-002 | Respiratory depression (severe) | 4 | Common opioid AE; catastrophic if not rescued |
| HARM-PRS-003 | Respiratory arrest | 5 | |
| HARM-PRS-004 | Hypoxemia | 3 | Severity escalates with duration |

### 3.3 Patient — Neurological / Cognitive

| Harm-ID | Harm | Default S | Notes |
|---|---|:-:|---|
| HARM-PNL-001 | Sedation (excessive) | 3 | |
| HARM-PNL-002 | Loss of consciousness | 4 | |
| HARM-PNL-003 | Seizure | 4 | |
| HARM-PNL-004 | Permanent neurological deficit | 5 | |

### 3.4 Patient — Drug-related

| Harm-ID | Harm | Default S | Notes |
|---|---|:-:|---|
| HARM-PDR-001 | Underdose — therapeutic failure | 3 | Severity escalates if pain control critical |
| HARM-PDR-002 | Overdose — non-life-threatening | 3 | |
| HARM-PDR-003 | Overdose — life-threatening | 5 | |
| HARM-PDR-004 | Wrong drug delivered | 4 | Severity depends on substituted drug |
| HARM-PDR-005 | Drug interaction (clinically significant) | 3 | |
| HARM-PDR-006 | Allergic / anaphylactic reaction | 4 | Catastrophic if anaphylaxis |

### 3.5 Patient — Local / Site-of-use

| Harm-ID | Harm | Default S | Notes |
|---|---|:-:|---|
| HARM-PLS-001 | Skin irritation | 2 | |
| HARM-PLS-002 | Local infection | 3 | |
| HARM-PLS-003 | Tissue extravasation | 3 | Severity escalates with vesicants |
| HARM-PLS-004 | Burn (thermal / electrical) | 3 | Up to 4 if deep |
| HARM-PLS-005 | Pressure injury | 2 | |

### 3.6 Patient — Infection / Sepsis

| Harm-ID | Harm | Default S | Notes |
|---|---|:-:|---|
| HARM-PIS-001 | Local infection (see HARM-PLS-002) | 3 | Cross-reference |
| HARM-PIS-002 | Bacteremia | 4 | |
| HARM-PIS-003 | Sepsis | 5 | |
| HARM-PIS-004 | Cross-contamination between patients | 4 | |

### 3.7 User / Operator

| Harm-ID | Harm | Default S | Notes |
|---|---|:-:|---|
| HARM-USR-001 | Needlestick / sharps exposure | 3 | |
| HARM-USR-002 | Electrical shock — operator | 3 | Up to 4 depending on energy |
| HARM-USR-003 | Pinch / strike injury during use | 2 | |
| HARM-USR-004 | Acoustic injury (alarm volume) | 2 | |

### 3.8 Data / Privacy / Security

| Harm-ID | Harm | Default S | Notes |
|---|---|:-:|---|
| HARM-DPS-001 | PHI exposure (unauthorized read) | 3 | Maps to HIPAA category; not direct patient harm but reportable |
| HARM-DPS-002 | PHI corruption (data integrity loss) | 3 | Up to 4 if affects clinical decision |
| HARM-DPS-003 | Loss of device availability during use | 4 | Maps to clinical harm via the disrupted function |
| HARM-DPS-004 | Unauthorized device control / tampering | 4 | Severity = severity of the resulting clinical harm |

## 4. How to Use This List

1. During hazard analysis (per GL-WI-RM-001), identify the harm at the **end of the foreseeable sequence** — what physical injury, damage, or data event ultimately occurs?
2. Match to a Harm-ID. If no entry fits, propose a new entry on a Document Change Request (per GL-SOP-QM-001) so future projects benefit.
3. Cite the Harm-ID and default S in the hazard table. If you justify a non-default S for your device context, document the rationale in the same row.

## 5. Cross-References

- GL-STD-RM-001 — Severity scale anchored on these defaults
- GL-WI-RM-001 — Hazard Analysis WI (consumer)
- GL-WI-RM-002 — FMEA WI (consumer)
- ISO 14971:2019 Annex C.2 — Categories of harm

## 6. Revision History

| Rev | Date | Author | Summary |
|---|---|---|---|
| 1.0 | 2026-04-27 | Ben Xavier (via Claude, task ben/036) | Initial release. 8 categories, 35 harms, default severities anchored on GL-STD-RM-001. |
