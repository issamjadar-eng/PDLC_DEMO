---
source_file: "N/A — authored-in-markdown"
source_path: "design-controls/design-traceability-matrix-wi.md"
doc_id: "GL-WI-DC-002"
doc_type: "WI"
title: "Design Traceability Matrix"
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
  - doc_id: "ISO 13485:2016 §7.3.4"
    title: "Design and development outputs"
    resolved: true
    match: null
    note: "Outputs traceable to inputs"
  - doc_id: "21 CFR 820.30(g)"
    title: "Design validation"
    resolved: true
    match: null
    note: "Validates design conforms to user needs"
  - doc_id: "IEC 62304:2006+A1:2015 §5.1.1"
    title: "Software development planning"
    resolved: true
    match: null
    note: "Software requirements trace"
  - doc_id: "GL-SOP-DC-001"
    title: "Design Control (Master)"
    resolved: true
    match: null
    note: "Parent SOP"
conversion_history:
  - date: "2026-04-27"
    source: "v1 — added under task ben/036 to define the trace-matrix process referenced (but not described) across GL-SOP-DC-003 / -004 / -006"
notes: "Defines the canonical trace shape (UN ↔ DI ↔ DO ↔ V&V ↔ Risk Control), the maintenance cadence, and the orphan-detection rules used at phase gates."
---

# GL-WI-DC-002 — Design Traceability Matrix

_Demo sample data — not for clinical use._

**Document ID:** GL-WI-DC-002
**Revision:** 1.0
**Effective Date:** 2026-04-27
**Owner:** Systems Engineering Lead, GlobalLogic MedTech

---

## 1. Purpose

Define the canonical structure, maintenance cadence, and quality bar for the **Design Traceability Matrix** (DTM) — the artifact that demonstrates every Design Input flows from a User Need, every Design Output realizes Design Inputs, and every requirement is verified or validated. Required by ISO 13485 §7.3.4 / 21 CFR 820.30 design controls and by IEC 62304 §5.1 for software items.

## 2. Scope

One DTM per DHF. The matrix is a deliverable of design controls (cited in the DDP) and a key audit artifact at every phase gate from Gate 3 onward (per GL-FORM-DC-002).

## 3. Canonical Trace Shape

The five-column trace shape is required for every device DHF:

```
User Need (UN)  ─→  Design Input (DI)  ─→  Design Output (DO)  ─→  V&V (Verification or Validation Activity)  ─→  Risk Control (if any)
```

Each row in the matrix is one trace path, identified by a stable Trace-ID. Cells may contain multiple comma-separated IDs (one DI may satisfy multiple UNs; one DO may realize multiple DIs).

| Column | ID format | Source SOP |
|---|---|---|
| User Need | `UN-NNN` | GL-SOP-DC-003 (User Needs register) |
| Design Input | `DI-NNN` | GL-SOP-DC-003 (Design Input Specification) |
| Design Output | `DO-NNN` (or filename for code-level outputs) | GL-SOP-DC-004 |
| V&V | `VER-NNN` (verification) or `VAL-NNN` (validation) | GL-SOP-DC-006 |
| Risk Control | `RC-NNN` (linked to Hazard Analysis / FMEA control row) | GL-SOP-RM-001 |

## 4. Required Trace Properties

### 4.1 Forward completeness (UN → DI → DO → V&V)

Every User Need shall trace **forward** to at least one Design Input, then to at least one Design Output, then to at least one V&V activity. A UN with no downstream trace is an **orphan**.

### 4.2 Backward completeness (V&V → DI → UN)

Every V&V activity shall trace **backward** to at least one Design Input, then to at least one User Need. A V&V activity with no upstream trace is testing something we never agreed to build — escalate.

### 4.3 Risk-control linkage (where applicable)

Every Risk Control of type "protective measure" or "inherently safe design" shall trace to at least one Design Input and one V&V activity. Risk controls of type "information for safety" trace to labeling DOs.

### 4.4 Software item trace (IEC 62304)

For software items (IEC 62304 Class B and C), each Software Requirement (a sub-class of DI) shall additionally trace to:

- One or more Software Architecture elements
- One or more Software Unit / Integration / System tests

This is the IEC 62304 §5.1.1 requirement; in practice, it lives as additional columns on the same DTM row.

## 5. Maintenance Cadence

- **Initial baseline** at Gate 2 (Feasibility → Design): UN ↔ DI columns populated.
- **Design-output fill** at Gate 3 (Design → V&V): DO column complete.
- **V&V fill** at Gate 4 (V&V → Transfer): VER/VAL column complete; gaps surfaced before transfer.
- **Change-control updates** thereafter: every DCR per GL-SOP-DC-008 updates the DTM if any traced row is affected.

The DTM is **never** built once at the end of V&V — that pattern guarantees gaps are discovered too late to fix.

## 6. Orphan Detection (Phase-Gate Check)

At Gates 3 and 4, the DTM is run through these checks (use `/trace-matrix` skill if installed, otherwise manual):

| Check | Failure mode | Action |
|---|---|---|
| Every UN has ≥ 1 DI | Forward orphan | Add the missing DI or justify UN as out-of-scope |
| Every DI has ≥ 1 DO | Mid-stream orphan | Author the missing output |
| Every DI has ≥ 1 V&V | V&V orphan | Add a verification or validation activity |
| Every V&V has ≥ 1 DI | Backward orphan | Either remove the V&V or add a DI it tests |
| Every Risk Control has ≥ 1 V&V | Risk-control orphan | Add V&V evidence the control works |

Gate disposition shall not be Pass while any orphan check fails. **Conditional** is acceptable when orphans are identified, time-bounded, and have action owners.

## 7. Format

The DTM is a structured artifact, not free prose. Two acceptable forms:

1. **Markdown table** in `docs/project/dhfs/<dhf-name>/design-controls/trace-matrix/trace-matrix.md` — readable in any viewer, greppable, diffable.
2. **JSON sidecar** at `trace-matrix.json` — machine-readable; consumed by the `/trace-matrix` skill and downstream tooling.

The skill produces both from a single source. Hand-authored projects shall keep the markdown as the source of truth.

## 8. Common Failure Modes (training emphasis)

| Pattern | Why it fails |
|---|---|
| One DI traces to "All Design Outputs" | Not specific enough — a real audit asks "which output realizes this input?" |
| One V&V traces to "All Design Inputs" | Same — V&V tests specific inputs, not abstractly "all" |
| A UN has no downstream trace because "we decided not to do it" | Mark it explicitly out-of-scope with rationale; don't leave it dangling |
| A DI exists but has no UN | Reverse-engineered from implementation; usually means a real UN was missed |
| The DTM is rebuilt from scratch at the end of V&V | Defeats the purpose; gaps surface at audit, not at gate |

## 9. Cross-References

- GL-SOP-DC-001 — Design Control (Master)
- GL-SOP-DC-003 — Design Inputs
- GL-SOP-DC-004 — Design Outputs
- GL-SOP-DC-006 — Design Verification and Validation
- GL-SOP-RM-001 — Risk Management (risk-control linkage)
- GL-SOP-SW-001 — Software Lifecycle (per-IEC-62304 software trace)
- GL-WI-DC-001 — DHF Process (DTM is required DHF content)

## 10. Revision History

| Rev | Date | Author | Summary |
|---|---|---|---|
| 1.0 | 2026-04-27 | Ben Xavier (via Claude, task ben/036) | Initial release. Defines canonical trace shape, maintenance cadence, and orphan checks. |
