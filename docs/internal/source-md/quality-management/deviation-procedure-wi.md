---
source_file: "N/A — authored-in-markdown"
source_path: "quality-management/deviation-procedure-wi.md"
doc_id: "GL-WI-QM-001"
doc_type: "WI"
title: "Deviation Procedure"
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
  - doc_id: "ISO 13485:2016 §8.3"
    title: "Control of nonconforming product"
    resolved: true
    match: null
    note: "Adjacent — process deviations vs product nonconformity"
  - doc_id: "ISO 13485:2016 §4.1.5"
    title: "Outsourced processes"
    resolved: true
    match: null
    note: null
  - doc_id: "GL-SOP-SP-004"
    title: "Control of Nonconforming Product"
    resolved: true
    match: null
    note: "Sister procedure — product NCs"
  - doc_id: "GL-SOP-QM-005"
    title: "CAPA"
    resolved: true
    match: null
    note: "Escalation path when deviation indicates systemic issue"
conversion_history:
  - date: "2026-04-27"
    source: "v1 — added under task ben/036 to fill the process-deviation gap (PDLC has nonconformance for product but no deviation pathway for process)"
notes: "Distinguishes process deviations (this WI) from product nonconformities (GL-SOP-SP-004). Same QMS — different artifact."
---

# GL-WI-QM-001 — Deviation Procedure

_Demo sample data — not for clinical use._

**Document ID:** GL-WI-QM-001
**Revision:** 1.0
**Effective Date:** 2026-04-27
**Owner:** QMS Administrator / VP Quality, GlobalLogic MedTech

---

## 1. Purpose

Define the controlled pathway when an approved QMS procedure cannot be followed exactly as written for a specific instance — and the resulting record-keeping, approval, and re-conformance steps. Distinguishes **process deviations** (covered here) from **product nonconformities** (covered by GL-SOP-SP-004).

## 2. Scope

Applies to every approved SOP, WI, and Form under the GlobalLogic QMS. Common deviation triggers:

- Equipment unavailable at the time the SOP requires it
- A required reviewer or approver is unavailable beyond the documented delegation matrix
- An emergency clinical or safety condition requires an off-procedure action
- A novel project condition not anticipated by the SOP

A deviation **is not** a substitute for a Document Change Request (per GL-SOP-QM-001) — deviations are **per-instance**. Recurring deviations from the same SOP **shall** trigger a CAPA review (per GL-SOP-QM-005).

## 3. Responsibilities

- **Requestor** — identifies the deviation need; files the form before (preferred) or as soon as practical after the deviating activity.
- **Functional Area Lead** — assesses impact on safety, quality, and regulatory commitments; recommends acceptance or rejection.
- **Quality Approver** — independent approval authority; required for any deviation affecting a controlled DHF artifact, V&V protocol, or released product.
- **QMS Administrator** — logs the deviation in the deviation register; tracks closure.

## 4. Definitions

- **Pre-execution deviation** — identified before the activity; approved before deviating action is taken.
- **Post-execution deviation** — identified during or after the activity; documented as soon as practical with a written rationale for why pre-approval was infeasible.
- **Deviation register** — a controlled list maintained by QMS of all open and closed deviations with disposition.

## 5. Procedure

### 5.1 Identify

When a planned activity cannot follow the approved procedure, the Requestor pauses (if safe to do so) and assesses:

1. Can the SOP be followed as written? (If yes — do that. No deviation needed.)
2. Is there a documented delegation or alternate path in the SOP? (If yes — follow it. No deviation needed.)
3. Otherwise — proceed to §5.2 to file a deviation.

If pausing is unsafe (e.g., active clinical event), document the deviation post-execution per §5.4.

### 5.2 File a Deviation Request

The Requestor opens a Deviation Form (use GL-FORM-QM-005 Document Change Request as the placeholder until a dedicated Deviation form is added) and completes:

| Field | Content |
|---|---|
| Deviation ID | Assigned by QMS — e.g., `DEV-2026-0001` |
| Date | YYYY-MM-DD of identification |
| SOP / WI affected | Doc ID and revision |
| Section affected | E.g., GL-SOP-DC-003 §6.4 |
| Deviation description | What is being done differently and why |
| Pre / post execution | Pre or Post (post requires §5.4 rationale) |
| Impact assessment | Safety, quality, regulatory, V&V, and labeling impact |
| Mitigations | Any compensating controls being used |
| Re-conformance plan | When and how the activity returns to procedure |
| Functional Area Lead approval | Signature + date |
| Quality approval | Signature + date |

### 5.3 Impact Assessment Triggers

The Functional Area Lead **shall** flag for elevated review when the deviation affects any of:

| Trigger | Action |
|---|---|
| A V&V protocol (in-flight) | Notify V&V Lead; assess test integrity |
| A released DHF artifact | Mandatory Quality + Regulatory approval |
| A risk-control measure | Mandatory Risk Manager approval; update RMF |
| A 510(k) commitment | Mandatory Regulatory Affairs approval; assess if Letter to File or 510(k) amendment is needed |
| A supplier-controlled process | Notify Supplier Quality |

### 5.4 Post-Execution Deviation Rationale

If the deviation was identified during or after the activity (rather than before), the Requestor **shall** include a written rationale on the form explaining why pre-approval was infeasible. Acceptable rationales include:

- Clinical emergency (patient safety required immediate action)
- Equipment failure mid-activity with no rollback path
- Late-discovered SOP ambiguity exposed only by the activity itself

Unacceptable rationales (these should result in CAPA):

- "Forgot to file the deviation form" — process gap; CAPA
- "Was faster to do it and ask later" — discipline gap; CAPA

### 5.5 Approval

A deviation is **not** authorized until it is approved per §5.2's signatures. For pre-execution deviations, the deviating activity does not start until approval is recorded.

For post-execution deviations, the activity is already complete — approval here ratifies (or rejects) the action taken. If rejected, the situation escalates immediately to:

1. Containment (per GL-SOP-SP-004 if product is implicated)
2. CAPA opening (per GL-SOP-QM-005)
3. Possible field action (per GL-SOP-PM-001 if released product is affected)

### 5.6 Closure

A deviation is closed when:

1. Re-conformance to the procedure has been achieved (or the SOP has been changed via DCR to absorb the new pathway).
2. All affected records have been updated to reference the deviation ID.
3. The deviation register entry is marked "Closed" with date and verifier.

## 6. CAPA Trigger

If the same deviation (same SOP / same section / same root cause) recurs **3 times within 12 months**, the QMS Administrator shall open a CAPA (per GL-SOP-QM-005) to investigate the underlying procedure for inadequacy. The CAPA may result in an SOP revision, training change, or process redesign.

## 7. Cross-References

- GL-SOP-QM-001 — Document and Records Control (parent for DCR vs deviation distinction)
- GL-SOP-QM-005 — CAPA (escalation path for systemic deviation patterns)
- GL-SOP-QM-006 — Good Documentation Practices (record hygiene applies to deviation forms too)
- GL-SOP-SP-004 — Control of Nonconforming Product (sister procedure for product-side NCs)
- ISO 13485:2016 §8.3 — Nonconformance control

## 8. Revision History

| Rev | Date | Author | Summary |
|---|---|---|---|
| 1.0 | 2026-04-27 | Ben Xavier (via Claude, task ben/036) | Initial release. Process-deviation pathway distinct from product-NC pathway in GL-SOP-SP-004. |
