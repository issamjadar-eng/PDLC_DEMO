---
source_file: "N/A — authored-in-markdown"
source_path: "regulatory-affairs/regulatory-operations-sop.md"
doc_id: "GL-SOP-RA-001"
doc_type: "SOP"
title: "Regulatory Operations"
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
  - doc_id: "ISO 13485:2016 §7.2.1"
    title: "Determination of requirements related to product"
    resolved: true
    match: null
    note: "Regulatory requirements as input"
  - doc_id: "21 CFR Part 807"
    title: "Establishment registration and device listing"
    resolved: true
    match: null
    note: null
  - doc_id: "EU MDR 2017/745 Article 10"
    title: "General obligations of manufacturers"
    resolved: true
    match: null
    note: null
conversion_history:
  - date: "2026-04-27"
    source: "v1 — added under task ben/036 as the top-level Regulatory Affairs SOP for the new RA QMS category"
notes: "Top-level Regulatory Operations SOP. Defines pathway selection, registrations & listings, agency interactions, and the regulatory-strategy ↔ design-controls handoff."
---

# GL-SOP-RA-001 — Regulatory Operations

_Demo sample data — not for clinical use._

**Document ID:** GL-SOP-RA-001
**Revision:** 1.0
**Effective Date:** 2026-04-27
**Owner:** VP Regulatory Affairs, GlobalLogic MedTech

---

## 1. Purpose

Define how GlobalLogic conducts regulatory affairs across product lifecycles: pathway determination, agency interactions, establishment registration and device listing, regulatory submissions, and the handoff between Regulatory Affairs and Design Controls / Post-Market.

## 2. Scope

Applies to every GlobalLogic medical device program — pre-market through post-market. Covers FDA (US), EU (MDR), Health Canada, TGA (Australia), MHRA (UK), PMDA (Japan), and ANVISA (Brazil) when those markets are in scope. Specific submission processes for each pathway live in pathway-specific Work Instructions.

## 3. Responsibilities

| Role | Responsibility |
|---|---|
| VP Regulatory Affairs | Strategic oversight; escalation authority |
| Regulatory Affairs Lead (per program) | Authors regulatory strategy; owns pathway determination |
| Regulatory Affairs Specialist | Executes submissions; tracks agency interactions |
| Quality Assurance | Co-signs regulatory commitments that bind QMS |
| Design Owner | Provides DHF artifacts for inclusion in submissions; receives change-impact assessments back |

## 4. Definitions

- **Pathway** — the regulatory route through which a device is brought to market (510(k), De Novo, PMA, MDR Annex IX, etc.).
- **Predicate / Comparator** — a legally cleared device used to establish substantial equivalence (510(k)) or clinical equivalence (MDR).
- **PCCP** — Predetermined Change Control Plan: pre-authorized changes that may be made post-clearance without a new submission.
- **Letter to File (LTF)** — internal documentation of a non-significant change that does not require a new submission per FDA's 2017 guidance.
- **Significant change** — a change that triggers a new submission (510(k) amendment, De Novo amendment, etc.) per the relevant agency's significance test.

## 5. Procedure

### 5.1 Pathway Determination (per program, at Gate 1)

For each new device program, the Regulatory Affairs Lead produces a **Regulatory Strategy** memo at Gate 1 (Concept → Feasibility) of the project. The strategy:

1. Classifies the device per the product code system of each target market.
2. Recommends a pathway (e.g., 510(k) traditional, 510(k) abbreviated, De Novo, PMA; MDR Annex IX or X; etc.).
3. Identifies predicate / comparator devices for substantial-equivalence pathways.
4. Identifies whether a Pre-Submission (Q-Sub) interaction is recommended before submission.
5. Recommends whether a PCCP is in scope (per FDA's 2024 PCCP guidance for AI/ML-enabled SaMD) or a similar mechanism in non-US markets.
6. Identifies clinical-evidence pathway: literature-only (per MDR Annex XIV Part A), clinical investigation under ISO 14155, or post-market follow-up only.

The strategy is reviewed at every phase gate and updated as the design and regulatory landscape evolve.

### 5.2 Agency Interactions

| Interaction Type | When | Required Records |
|---|---|---|
| Pre-Submission (Q-Sub) | Before formal submission, when novel issues warrant agency feedback | Q-Sub package, agency response, internal post-meeting memo |
| Submission | Per device-program plan | Submission package, agency acknowledgements, deficiency responses |
| Additional Information / Major / Minor Deficiencies | In response to agency requests | Deficiency response, supporting evidence, internal review record |
| Post-Approval Reporting | Per regulation cadence | PSUR / annual reports / change notifications |
| Inspections | Per agency schedule | Inspection record, observations, response to observations (Form 483 / Warning Letter) |

All agency communications are **logged in the Regulatory Communications Register** maintained by RA. Originals are stored in the controlled regulatory archive.

### 5.3 Establishment Registration & Device Listing

| Market | Requirement | Cadence |
|---|---|---|
| US (FDA) | 21 CFR Part 807 — establishment registration + device listing in FURLS | Annual; updates within 30 days of changes |
| EU (MDR) | Eudamed actor and device registration | At market entry; updates per Article 31 |
| Other markets | Per local regulation (Health Canada MDEL, TGA ARTG, etc.) | Per local cadence |

Registrations are **maintained** by RA (not just established). Lapses can void marketing authorization.

### 5.4 Submission Lifecycle Handoff

The handoff between Design Controls and Regulatory Affairs follows this sequence:

1. **Pre-submission DHF freeze** — at Gate 4 (V&V → Transfer), the DHF artifacts cited in the planned submission are baselined per GL-WI-DC-001 §8.
2. **Submission package assembly** — RA assembles per the pathway-specific WI (e.g., GL-WI-RA-001 for 510(k)).
3. **Quality + RA review** — package signed off by Quality + RA before transmission.
4. **Submission transmittal** — via the pathway-specific portal (eSTAR for 510(k), Eudamed for MDR, etc.).
5. **Tracking** — Regulatory Communications Register maintains submission status until clearance / rejection.

### 5.5 Post-Clearance Change Management

After a device is cleared, design changes route through GL-SOP-DC-008 (Design Change Control). RA's role in the change-control board:

- Apply the agency's change-significance test (e.g., FDA's 2017 510(k) change guidance flowcharts).
- Determine whether the change qualifies as Letter to File, requires a 510(k) Amendment, or triggers a new 510(k).
- For MDR markets, apply Article 120 substantial-change analysis.
- For PCCP-covered changes, confirm the change falls within the cleared PCCP scope.
- Document the determination in the regulatory file.

### 5.6 Regulatory Strategy Updates

The Regulatory Strategy is **a living document**, not a one-time deliverable. Triggers for update:

- New agency guidance is published (e.g., FDA AI/ML guidance updates).
- A predicate is removed from market or has a recall.
- A new market is added to the program scope.
- A design change materially shifts the pathway analysis.

## 6. Cross-References

- GL-SOP-DC-001 — Design Control (Master) — provides DHF artifacts cited in submissions
- GL-SOP-DC-008 — Design Change Control — determines submission triggers from design changes
- GL-SOP-PM-003 — Adverse Event Reporting (vigilance) — separate post-market regulatory obligation
- GL-WI-RA-001 — 510(k) Submission Process (pathway-specific WI)
- ISO 13485:2016 §7.2.1
- 21 CFR Part 807, 814; FDA 510(k) / De Novo / PMA guidances
- EU MDR 2017/745
- FDA Predetermined Change Control Plans (2024 guidance)

## 7. Revision History

| Rev | Date | Author | Summary |
|---|---|---|---|
| 1.0 | 2026-04-27 | Ben Xavier (via Claude, task ben/036) | Initial release. Top-level Regulatory Operations SOP for the new Regulatory Affairs QMS category. |
