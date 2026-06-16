# ASTM F2554 — Positional Accuracy of Computer Assisted Surgical Systems

🔎 **Finding aid — NOT the authoritative source.** Paraphrased distillation of an external standard/framework; no faithful full-text copy exists in this repository (copyrighted). The original document named in the header above is the sole authority — if a clause-level question isn't answered here, state that the original must be consulted; do not infer clause content. `[VERIFY]` marks are unconfirmed against the source.

**Framework**: ASTM F2554-18 (Standard Practice for Measurement of Positional Accuracy of Computer Assisted Surgical Systems) `[VERIFY edition — a later revision (F2554-22) is believed current and FDA-recognized; re-pin and re-distill against it]`
**Source**: ASTM International (Committee F04 on Medical and Surgical Materials and Devices) — astm.org/f2554
**Referenced In**: Surgical navigation device submissions; FDA expects accuracy validation for CAS systems. ASTM F2554 is an **FDA-recognized consensus standard** — it carries more regulatory weight than the typical entry in this `industry-frameworks/` category.

## Overview

ASTM F2554 defines standardized methods for measuring the positional accuracy of Computer Assisted Surgery (CAS) systems. It establishes how to quantify the accuracy of a navigation system's ability to indicate the position and orientation of surgical instruments relative to patient anatomy.

## Key Concepts

### Types of Accuracy

| Accuracy Type | Definition |
|--------------|------------|
| **Registration Accuracy** | Error between the patient's anatomy and the digital model/plan |
| **Tracking Accuracy** | Error in the tracking system's ability to determine instrument position |
| **Navigation Accuracy** | Combined accuracy of the entire system (registration + tracking + display) |
| **Target Registration Error (TRE)** | Error at a target point after registration — the most clinically relevant metric |
| **Fiducial Registration Error (FRE)** | Error at the registration landmarks themselves. **FRE is NOT a bound on or predictor of TRE** — the two are essentially uncorrelated (Fitzpatrick et al.); a small FRE does not imply a small TRE, and TRE can be smaller than FRE. Never use FRE as a TRE acceptance surrogate in a V&V protocol — measure TRE at clinically relevant targets directly. (A prior version of this file wrongly called FRE a "lower bound of TRE.") |

### Error Metrics

| Metric | Description | Typical Units |
|--------|-------------|---------------|
| **RMS Error** | Root mean square of positional errors | mm |
| **Mean Error** | Average positional error | mm |
| **Max Error** | Worst-case positional error | mm |
| **95th Percentile Error** | Error exceeded by only 5% of measurements | mm |
| **Angular Error** | Orientation/alignment error | degrees |
| **Standard Deviation** | Variability of error | mm |

## Test Methodology

### Test Environment

- Tests should be performed under conditions representative of clinical use
- Environmental factors to control: lighting (for optical tracking), electromagnetic interference (for EM tracking), temperature
- Use calibrated reference instruments (e.g., coordinate measuring machine, optical tracker as ground truth)

### Test Phantoms

- Use phantoms with known geometry and precisely located fiducial markers
- Phantom should represent the clinical anatomy (e.g., pelvis/femur phantom for hip surgery)
- Fiducial locations should be distributed across the clinically relevant volume
- Include both surface points and deep targets to evaluate depth-dependent accuracy

### Test Procedure (per ASTM F2554)

1. **Set up the CAS system** in the intended clinical configuration
2. **Register the phantom** using the system's registration method (same method used clinically)
3. **Navigate to known target points** on the phantom
4. **Record the system-indicated position** and the actual position (ground truth)
5. **Calculate positional error** as the Euclidean distance between indicated and actual positions
6. **Repeat** across multiple target points, multiple registrations, and multiple configurations
7. **Report** error statistics (mean, RMS, max, 95th percentile, standard deviation)

### Sample Size Considerations

`[Heuristics, NOT standard content — the figures below are common-practice illustrations; the standard's actual sampling requirements must be taken from the standard itself]`

- Minimum number of target points per registration: typically 20-30
- Multiple independent registrations: typically 5-10
- Multiple configurations (phantom positions, tracking volumes): as clinically representative
- Statistical significance: sufficient to characterize the error distribution

## Accuracy Thresholds — Application-Specific, NOT Standard Content

ASTM F2554 defines the measurement *method* only. Acceptable accuracy *thresholds* come from the clinical application, the predicate comparison, and the device's own risk analysis — never from F2554 itself.

### Example thresholds — total hip ARTHROPLASTY literature (uncited; illustrative only)

`[The table below is drawn from arthroplasty clinical literature (e.g., the Lewinnek acetabular safe zone) without per-row citations. It applies to IMPLANT-PLACEMENT (THA) navigation. Other hip applications — e.g., hip-preservation/resection workflows with no implants — need different, application-specific accuracy metrics (resection depth/extent, morphological angle measurement accuracy) derived from their own clinical analysis. Do not transplant these THA numbers into a non-THA protocol.]`

| Measurement | Literature Threshold | Rationale |
|-------------|-------------------|-----------|
| Cup placement angle (inclination) | ≤ 5° | Safe zone for acetabular cup: 30-50° inclination |
| Cup placement angle (anteversion) | ≤ 5° | Safe zone: 5-25° anteversion |
| Leg length discrepancy | ≤ 5 mm | Patient-perceivable threshold ~6mm |
| Femoral offset | ≤ 5 mm | Affects abductor function and stability |
| Stem alignment | ≤ 2° | Varus/valgus alignment affects load distribution |
| Point-to-point navigation | ≤ 2 mm RMS | General navigation accuracy expectation for orthopedic CAS |

## Related Standards

| Standard | Description | Relationship |
|----------|-------------|-------------|
| ASTM F2554 | Positional accuracy measurement (this document) | Primary accuracy validation standard |
| ISO 5725 | Accuracy (trueness and precision) of measurement methods | General metrology framework referenced by F2554 |
| IEC 62304 | Software lifecycle | Development process for the navigation software |

(A prior version of this table listed "ASTM F2101 — Evaluating performance of CAS systems (withdrawn, content merged)". That row was fabricated — ASTM F2101 is the bacterial filtration efficiency test for medical face mask materials, unrelated to CAS. Removed.)

## Tracking Technologies

The tracking/guidance approach affects which parts of ASTM F2554 apply:

| Technology | Description | ASTM F2554 Applicability |
|-----------|-------------|-------------------------|
| Optical (infrared) tracking | Cameras track reflective markers on instruments | Full F2554 testing required |
| Electromagnetic tracking | EM field generator + sensors on instruments | Full F2554 testing required |
| Imageless navigation (IMU/accelerometer) | Sensor-based without external tracker | Adapted F2554 testing |
| Image overlay / AR guidance | Camera-based registration without tracking hardware | Adapted F2554 testing |
| Planning-only guidance | Pre-op plan displayed for surgeon reference, no real-time tracking | F2554 may not apply — measurement accuracy (DICOM) is the key standard |
