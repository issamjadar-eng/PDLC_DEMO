---
source_file: "N/A — authored-in-markdown"
source_path: "quality-management/good-documentation-practices-sop.md"
doc_id: "GL-SOP-QM-006"
doc_type: "SOP"
title: "Good Documentation Practices"
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
  - doc_id: "ISO 13485:2016 §4.2.4"
    title: "Control of documents"
    resolved: true
    match: null
    note: null
  - doc_id: "ISO 13485:2016 §4.2.5"
    title: "Control of records"
    resolved: true
    match: null
    note: null
  - doc_id: "21 CFR Part 11"
    title: "Electronic records; electronic signatures"
    resolved: true
    match: null
    note: null
  - doc_id: "GL-SOP-QM-001"
    title: "Document and Records Control"
    resolved: true
    match: null
    note: "Parent SOP — this one fills the practitioner-level guidance gap"
conversion_history:
  - date: "2026-04-27"
    source: "v1 — added under task ben/036 to provide practitioner-level GDP guidance complementing GL-SOP-QM-001"
notes: "Practitioner-level companion to GL-SOP-QM-001. Covers the day-to-day mechanics of authoring, dating, signing, redlining, and amending QMS records."
---

# GL-SOP-QM-006 — Good Documentation Practices

_Demo sample data — not for clinical use._

**Document ID:** GL-SOP-QM-006
**Revision:** 1.0
**Effective Date:** 2026-04-27
**Owner:** QMS Administrator / VP Quality, GlobalLogic MedTech

---

## 1. Purpose

Define the day-to-day mechanics of authoring, executing, and amending GMP / GDP records under the GlobalLogic QMS — the **how to actually fill out a form** that GL-SOP-QM-001 (Document and Records Control) operates above. Aligned with ISO 13485:2016 §4.2.4–.5, 21 CFR 820.40, and 21 CFR Part 11.

## 2. Scope

Applies to every record generated under the GlobalLogic QMS — paper, electronic, or hybrid. Project DHFs, risk files, V&V reports, supplier records, complaints, CAPAs, and management-review minutes are all in scope.

## 3. Responsibilities

- **Author** — produces the record; responsible for accuracy and traceability.
- **Reviewer** — independent of authoring activity; verifies completeness and conformance.
- **Approver** — has signature authority per the document's approval matrix.
- **QMS Administrator** — maintains the record-control infrastructure (electronic system + paper archive).

## 4. Definitions

- **GDP** — Good Documentation Practices: the set of conventions that make records auditable.
- **Contemporaneous** — recorded at the time the activity occurs (not reconstructed later).
- **Attributable** — every entry traces to a specific person.
- **Legible** — readable by any subsequent reviewer without inference.
- **Original** — the first record (or a true certified copy); not transcribed from working notes.
- **Accurate** — the record states what actually happened, not what was supposed to happen.

These five attributes — **A**ttributable, **L**egible, **C**ontemporaneous, **O**riginal, **A**ccurate (ALCOA) — plus **C**omplete, **C**onsistent, **E**nduring, **A**vailable (ALCOA+) are the audit yardstick.

## 5. Procedure — Authoring

### 5.1 Filling out forms (paper)

- Use **black or dark blue indelible ink**. No pencil. No erasable pen.
- **Print clearly** — if illegible to a peer, the entry is non-conformant.
- **Date every entry** — `YYYY-MM-DD` is the QMS standard. Avoid ambiguous formats (`MM/DD/YY`).
- **Initial every entry** with the author's standard 2-or-3 letter initials registered with QMS.
- **No blank fields** — write `N/A` (not applicable) and initial. A blank field is interpreted as incomplete.
- **No erasures, white-out, or scratch-outs** — see §5.3.

### 5.2 Filling out forms (electronic)

- Use the QMS-approved electronic system. Sessions are 21 CFR Part 11 compliant by virtue of the system; **do not export** records to uncontrolled tools (Word, Sheets, personal laptops).
- Authentication uses the system's enforced login. **Do not share credentials.**
- The system stamps each entry with username + UTC timestamp; the author **shall** verify the stamp matches the contemporaneous activity time.
- Entries are immutable once committed; corrections follow §5.3.

### 5.3 Corrections

If an entry is wrong:

**Paper:** Draw a single line through the error so the original entry **remains legible**. Initial, date, and write a brief reason next to the change. Never obliterate, white-out, or use correction tape.

```
[Wrong]:  100 mL  →  150 mL                    ★ NEVER
[Right]:  ̶1̶0̶0̶ ̶m̶L̶  150 mL · BX 2026-04-27 · misread label
```

**Electronic:** Use the system's amendment workflow (a new entry that supersedes the prior). The audit trail preserves both. **Do not** request the QMS Administrator to "delete" an entry; correction is via amendment, never deletion.

### 5.4 Signatures

Each signature implies the signer has personally reviewed the content above the signature line and accepts responsibility for its accuracy at the time of signing. Sign with full legal name (paper) or registered electronic identity (e-system). Signature dates **shall** be contemporaneous with the activity.

If a record requires a signer who is unavailable, use the documented **delegation** procedure (per GL-SOP-QM-001 §6.4) — never sign on behalf of another person.

## 6. Procedure — Reviewing

- Reviewers **shall not** be the author of the same record.
- Review every field — including `N/A` entries (confirm "not applicable" is genuinely the case).
- Use a checklist when the record's parent SOP supplies one (e.g., GL-FORM-DC-002 phase-gate review).
- Sign and date the review block **after** review is complete, not in advance of opening the record.

## 7. Procedure — Storage and Retrieval

- Paper records → controlled archive room per GL-SOP-QM-001 retention schedules.
- Electronic records → QMS-approved system with daily backup and Part 11 audit trail.
- Hybrid records → both copies, cross-indexed.
- Retention periods follow the device class and applicable regulations (typically the device service life + 2 years minimum; longer for implantable / long-life devices per §820.180 and MDR Article 10).

## 8. Common Pitfalls (training emphasis)

| Pitfall | Why it fails an audit |
|---|---|
| Signing today for an activity completed last week | Violates contemporaneous principle |
| Filling in `N/A` after the audit asks why a field is blank | Violates ALCOA — backdating a correction |
| Using "ditto marks" or arrows to copy down a column | Each row must stand on its own |
| White-out / correction tape | Obliterates the prior entry — looks like fraud |
| Sharing electronic credentials | Breaks attribution; violates Part 11 |
| Storing a working copy of a controlled doc on a personal laptop | Creates uncontrolled instances |

## 9. References

- ISO 13485:2016 §4.2.4 — Control of documents
- ISO 13485:2016 §4.2.5 — Control of records
- 21 CFR 820.40 — Document controls
- 21 CFR Part 11 — Electronic records; electronic signatures
- GL-SOP-QM-001 — Document and Records Control (parent SOP)
- ALCOA+ principles (FDA / WHO / EMA convergent guidance)

## 10. Revision History

| Rev | Date | Author | Summary |
|---|---|---|---|
| 1.0 | 2026-04-27 | Ben Xavier (via Claude, task ben/036) | Initial release. Practitioner-level GDP companion to GL-SOP-QM-001. |
