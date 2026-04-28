---
source_file: "N/A — authored-in-markdown"
source_path: "software-cybersecurity/threat-modeling-wi.md"
doc_id: "GL-WI-SW-003"
doc_type: "WI"
title: "Threat Modeling"
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
  - doc_id: "IEC 81001-5-1:2021 §5"
    title: "Security risk management process"
    resolved: true
    match: null
    note: "Primary anchor"
  - doc_id: "FDA Cybersecurity in Medical Devices (2023)"
    title: "Quality system considerations and content of premarket submissions"
    resolved: true
    match: null
    note: "Threat modeling required premarket"
  - doc_id: "AAMI TIR57:2016"
    title: "Principles for medical device security — risk management"
    resolved: true
    match: null
    note: null
  - doc_id: "GL-SOP-SW-004"
    title: "Medical Device Cybersecurity"
    resolved: true
    match: null
    note: "Parent SOP"
conversion_history:
  - date: "2026-04-27"
    source: "v1 — added under task ben/036 to operationalize threat modeling required by GL-SOP-SW-004 and FDA 2023 cybersecurity guidance"
notes: "Concrete WI for threat-modeling work-product: data-flow diagrams, trust boundaries, STRIDE, attack-tree fallback for high-impact threats."
---

# GL-WI-SW-003 — Threat Modeling

_Demo sample data — not for clinical use._

**Document ID:** GL-WI-SW-003
**Revision:** 1.0
**Effective Date:** 2026-04-27
**Owner:** Cybersecurity Lead, GlobalLogic MedTech

---

## 1. Purpose

Define the executable mechanics of producing a **threat model** for a GlobalLogic medical device — required by IEC 81001-5-1 §5 and by FDA's 2023 Cybersecurity in Medical Devices premarket guidance. Operationalizes GL-SOP-SW-004 §6 — which establishes that a threat model exists per device but does not specify the modeling technique.

## 2. Scope

Applies to every device with one or more of the following: software (SaMD, SiMD), network connectivity, USB/serial/wireless interfaces, OTA update capability, cloud back-end, or persisted patient/user data. Effectively every modern medical device.

The threat model is a **living artifact** of the cybersecurity file (per GL-SOP-SW-004), updated at every design change with security implications and at every CVE / vulnerability discovery affecting a SOUP component.

## 3. Required Outputs

A complete threat model produces five artifacts, all stored in the project's cybersecurity file under the DHF:

| Artifact | Purpose |
|---|---|
| Asset inventory | What we are protecting |
| Data-flow diagram (DFD) | Where data moves; reveals trust boundaries |
| Trust-boundary list | Where authentication / authorization / integrity must be enforced |
| Threat list (STRIDE-derived) | Threat per asset per boundary |
| Mitigation map | Each threat → control(s) → V&V evidence (links to GL-WI-SW-004) |

## 4. Procedure

### 4.1 Asset Inventory

List every asset whose **confidentiality, integrity, or availability** matters for safety, privacy, or regulatory commitment. Asset categories:

- **Patient data** — PHI, treatment data, audit trails
- **Device-control data** — therapy parameters, dose limits, drug libraries
- **Device-state data** — firmware version, configuration, calibration constants
- **Operator credentials** — authentication tokens, session keys
- **Audit / logging data** — tamper-evident records of device use
- **Update channels** — OTA / firmware update paths
- **External interfaces** — DICOM, HL7, FHIR, MQTT, USB, BLE

Each asset gets a stable Asset-ID (`AS-NNN`).

### 4.2 Data-Flow Diagram

Produce a DFD showing every flow of every asset between every component. Required notation:

- **Boxes** = processes (running components)
- **Cylinders** = data stores
- **Stick figures** = external entities (users, other systems)
- **Arrows** = data flow direction with the asset(s) flowing
- **Dashed lines** = trust boundaries

The DFD is **not optional** — text-only threat models miss boundary issues that are visually obvious in a DFD. Use a tool that produces a versioned source format (Mermaid, Draw.io XML, Threat Dragon JSON) so the diagram lives in source control.

### 4.3 Trust-Boundary List

For each dashed line in the DFD, document:

- What is on each side
- What kind of identity / authentication crosses it (none / username-pw / mTLS / signed token)
- What integrity guarantees apply (none / message signing / channel integrity / replay protection)
- What confidentiality guarantees apply (none / channel encryption / payload encryption / both)

Boundaries with **no protection** are explicit findings — either add a control or document the threat acceptance.

### 4.4 Threat Enumeration — STRIDE

For each asset crossing each trust boundary, walk the STRIDE categories and identify plausible threats:

| Letter | Category | Asks |
|---|---|---|
| **S** | Spoofing | Can someone impersonate a legitimate identity? |
| **T** | Tampering | Can the asset be modified in transit or at rest? |
| **R** | Repudiation | Can an action be denied later? |
| **I** | Information disclosure | Can the asset leak to an unauthorized reader? |
| **D** | Denial of service | Can availability be disrupted? |
| **E** | Elevation of privilege | Can a low-privileged actor gain higher privilege? |

Each identified threat gets a stable Threat-ID (`TH-NNN`). Mark threats that **cannot apply** with a brief rationale ("S: not applicable — no inbound traffic crosses this boundary in the current design").

### 4.5 Attack-Tree Drilldown (high-impact only)

For threats whose successful exploitation maps to **patient harm** (per GL-STD-RM-002 Master Harms List), construct an attack tree showing the steps an attacker would take. Attack trees expose the **easiest** path to harm — the mitigation should target the easiest path first.

Attack trees are not produced for every threat — only for those linked to S=4 or S=5 patient harms.

### 4.6 Mitigation Map

For each Threat-ID, map to:

- **Control** — the design or process control that mitigates it (cite Risk Control ID from GL-SOP-RM-001 risk file)
- **V&V evidence** — how do we know the control works? (cite VER-NNN from GL-WI-SW-004 software V&V or pen-test report)
- **Residual risk** — after the control, what's left? (severity × likelihood per GL-STD-RM-001)
- **Acceptance** — Acceptable / ALARP / Unacceptable per GL-STD-RM-001 §5

Threats in the **Unacceptable** region after all feasible controls trigger a benefit-risk analysis (GL-STD-RM-001 §7).

## 5. Cadence

| Trigger | Action |
|---|---|
| Project initiation (Gate 1 → 2) | Initial threat model produced; covers high-level architecture |
| Architecture freeze (Gate 2 → 3) | Threat model updated to reflect baselined SAD; trust boundaries finalized |
| Cybersecurity testing (Gate 3 → 4) | Threat model verified by penetration testing; mitigation evidence linked |
| Post-market vulnerability disclosure | Threat model re-evaluated for newly-disclosed CVEs against SOUP register |
| Design change with security impact | Per GL-SOP-DC-008 + GL-SOP-SW-004 |

## 6. Pen-Test Tie-In

Pen-testing is the empirical confirmation of the threat model. The pen-test scope shall **derive from** the threat model:

- For every Threat-ID with S ≥ 3 mapped to a control, the pen-test attempts that exploitation path.
- Pen-test findings that don't appear in the threat model indicate a gap in the model — add the missing threat **before** treating it as a closed pen-test finding.

## 7. SOUP / SBOM Integration

The threat model references the SBOM (per GL-WI-SW-002). When a SOUP component has a known vulnerability (CVE):

1. Map the CVE to one or more Threat-IDs in the model.
2. If the existing controls already mitigate, document the analysis and close.
3. If not, open a new Threat-ID, route through risk management, and patch / mitigate.

## 8. Cross-References

- GL-SOP-SW-004 — Medical Device Cybersecurity (parent SOP)
- GL-WI-SW-002 — SBOM Generation
- GL-WI-SW-004 — Software Verification and Validation (mitigation evidence)
- GL-SOP-RM-001 — Risk Management (Master)
- GL-STD-RM-001 — Risk Assessment Criteria (severity × probability)
- GL-STD-RM-002 — Master Harms List (S anchors for safety-impact threats)
- IEC 81001-5-1:2021 §5
- FDA Cybersecurity in Medical Devices (2023)
- AAMI TIR57:2016

## 9. Revision History

| Rev | Date | Author | Summary |
|---|---|---|---|
| 1.0 | 2026-04-27 | Ben Xavier (via Claude, task ben/036) | Initial release. STRIDE + attack-tree fallback; cadence tied to phase gates. |
