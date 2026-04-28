---
source_file: "N/A — authored-in-markdown"
source_path: "software-cybersecurity/software-vv-wi.md"
doc_id: "GL-WI-SW-004"
doc_type: "WI"
title: "Software Verification and Validation"
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
  - doc_id: "IEC 62304:2006+A1:2015 §5.5–§5.7"
    title: "Software unit, integration, and system testing"
    resolved: true
    match: null
    note: "Primary anchor"
  - doc_id: "IEC 62304:2006+A1:2015 §9"
    title: "Software problem resolution"
    resolved: true
    match: null
    note: "Defect handling during V&V"
  - doc_id: "21 CFR 820.30(g)"
    title: "Design validation"
    resolved: true
    match: null
    note: null
  - doc_id: "GL-SOP-SW-001"
    title: "Medical Device Software Lifecycle"
    resolved: true
    match: null
    note: "Parent SOP"
  - doc_id: "GL-SOP-DC-006"
    title: "Design Verification and Validation"
    resolved: true
    match: null
    note: "Sister SOP — system-level V&V"
conversion_history:
  - date: "2026-04-27"
    source: "v1 — added under task ben/036 to provide concrete software-V&V process complementing the high-level lifecycle SOP"
notes: "Concrete IEC-62304-aligned WI for unit / integration / system testing depth by Software Safety Class."
---

# GL-WI-SW-004 — Software Verification and Validation

_Demo sample data — not for clinical use._

**Document ID:** GL-WI-SW-004
**Revision:** 1.0
**Effective Date:** 2026-04-27
**Owner:** VP Engineering, GlobalLogic MedTech

---

## 1. Purpose

Define the concrete unit / integration / system test process for medical-device software, scaled by **Software Safety Class** (A / B / C per IEC 62304 §4.3). Operationalizes GL-SOP-SW-001 §6 — which sets the framework but does not specify per-class test depth.

## 2. Scope

Applies to every software item under a GlobalLogic device program — SaMD, SiMD, embedded firmware, and supporting tools when they impact safety. Excludes purely informational software (e.g., reporting dashboards in non-clinical paths) — those remain governed by GL-SOP-SW-001 only.

## 3. Test Levels (IEC 62304 §5.5–§5.7)

Three test levels are defined; their **required execution** depends on Software Safety Class:

| Level | Scope | Required for Class A | Required for Class B | Required for Class C |
|---|---|:-:|:-:|:-:|
| **Unit Test** | Single function / class / module | Recommended | Required | Required |
| **Integration Test** | Two or more units composed | Recommended | Required | Required |
| **System Test** | End-to-end against software requirements | Required | Required | Required |

**Class A** software (no safety impact) still requires system test against software requirements. Unit and integration tests are recommended but not required — author's discretion based on complexity.

## 4. Unit Test Requirements (Class B + C)

### 4.1 Coverage

Per IEC 62304 §5.5:

- Statement coverage: ≥ 80% (target 100% on Class C safety-critical units).
- Branch coverage: ≥ 70% (target 100% on Class C).
- Edge / boundary cases for every input domain.

Coverage is measured automatically (see §8 Tool Validation) and reported in the unit-test report.

### 4.2 Test isolation

Unit tests run **in isolation**: dependencies are mocked, stubbed, or faked. A failing unit test indicates a defect in the unit under test — not a contention with another unit.

### 4.3 Reproducibility

Unit tests run identically in CI, on developer machines, and on the auditor's review environment. Non-deterministic tests (flaky timing, real wall-clock dependency, network calls) are **not acceptable** at unit level.

## 5. Integration Test Requirements (Class B + C)

Integration tests confirm composed units interact correctly. Required scenarios:

- Each module-to-module interface tested in both happy-path and error-path directions.
- Each interface boundary identified in the System Architecture Document tested.
- Integration tests for safety-critical paths (Class C) include negative cases — the integrated system rejects malformed inputs without unsafe behavior.

## 6. System Test Requirements (All Classes)

System tests verify that the software meets the **Software Requirements Specification** (a sub-class of Design Inputs per GL-SOP-DC-003).

| Required element | Detail |
|---|---|
| Trace to software requirements | Every system test cites the SRS-ID(s) it verifies |
| Trace to risk controls | Every Risk Control of type "software-implemented" has a system test |
| Realistic data | Production-equivalent test data; no debug stubs in the system under test |
| Production-equivalent build | Tests run against the build artifact intended for release |
| Negative testing | Class C software requires explicit negative test of every safety-critical input |

## 7. Test Protocol and Report (Required)

For every test execution event (unit-test run, integration suite, system-test campaign):

| Section | Content |
|---|---|
| Test Identification | Test plan ID, build under test (commit SHA), date, executor |
| Scope | What is tested, what is excluded |
| Acceptance Criteria | Quantitative (coverage %, pass rate) |
| Results | Pass / Fail per test case |
| Deviations | Any deviation from the protocol (per GL-WI-QM-001) |
| Defects raised | Cross-reference to defect-tracking IDs |
| Sign-Off | Executor + reviewer (independent) signatures |

The test report is a controlled DHF artifact (per GL-WI-DC-001 §3).

## 8. Tool Validation (IEC 62304 §6.1)

Software tools used in V&V — coverage analyzers, test runners, static analyzers — that impact the test result **shall** be validated for their intended use. Validation includes:

- Documented intended use of the tool in the V&V workflow
- Risk assessment: what could the tool get wrong, and how would that affect a release decision?
- Validation evidence: vendor IQ/OQ data, in-house test of representative inputs, or open-source community evidence — depending on risk
- Configuration baseline: tool version + plugin versions captured in the test report

Tool validation is a one-time activity per (tool version, intended use); it is re-validated on tool upgrade or use-case change.

## 9. Defect Handling During V&V

Defects discovered during V&V are routed through GL-SOP-SW-003 (Software Problem Resolution) — every defect gets a unique ID, severity classification, root-cause analysis, fix verification, and regression confirmation. Critical defects affecting safety-critical paths block the release until closed.

## 10. Per-Class Cheat-Sheet

| Activity | Class A | Class B | Class C |
|---|:-:|:-:|:-:|
| Unit test (statement coverage ≥ 80%) | Recommended | Required | Required (target 100%) |
| Integration test | Recommended | Required | Required |
| System test against SRS | Required | Required | Required |
| Negative testing on safety paths | N/A | Optional | Required |
| Code review | Recommended | Required | Required (independent reviewer) |
| Static analysis | Optional | Recommended | Required |
| Coverage report in DHF | Optional | Required | Required |
| Tool validation per IEC 62304 §6.1 | Recommended | Required | Required |

## 11. Cybersecurity V&V Tie-In

Software V&V intersects threat modeling (GL-WI-SW-003): every Threat-ID with a software control has a corresponding system test that exercises the control. Penetration tests complement (do not replace) software V&V — they verify the model's assumptions against an adversarial mindset.

## 12. Cross-References

- GL-SOP-SW-001 — Medical Device Software Lifecycle (parent SOP)
- GL-WI-SW-001 — Software Safety Classification (input — class drives required activities here)
- GL-SOP-SW-003 — Software Problem Resolution (defect handling)
- GL-WI-SW-002 — SBOM Generation (SOUP CVE response)
- GL-WI-SW-003 — Threat Modeling (cybersecurity tie-in)
- GL-SOP-DC-006 — Design Verification and Validation (system-level V&V)
- GL-WI-DC-002 — Design Traceability Matrix (system tests trace to SRS / DI)

## 13. Revision History

| Rev | Date | Author | Summary |
|---|---|---|---|
| 1.0 | 2026-04-27 | Ben Xavier (via Claude, task ben/036) | Initial release. Per-IEC-62304 unit / integration / system test depth scaled by Software Safety Class. |
