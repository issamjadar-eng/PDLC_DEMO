# ASTM F2554 — Positional Accuracy of Computer Assisted Surgical Systems

**Framework**: ASTM F2554-18 (Standard Practice for Measurement of Positional Accuracy of Computer Assisted Surgical Systems)
**Source**: ASTM International (Committee F04 on Medical and Surgical Materials and Devices)
**Referenced In**: Surgical navigation device submissions; FDA expects accuracy validation for CAS systems

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
| **Fiducial Registration Error (FRE)** | Error at the registration landmarks themselves — lower bound of TRE |

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

- Minimum number of target points per registration: typically 20-30
- Multiple independent registrations: typically 5-10
- Multiple configurations (phantom positions, tracking volumes): as clinically representative
- Statistical significance: sufficient to characterize the error distribution

## Accuracy Requirements for Hip Surgery Navigation

While ASTM F2554 defines the measurement *method*, the acceptable accuracy *thresholds* are determined by the clinical application and predicate comparison.

### Clinically Relevant Accuracy Thresholds

| Measurement | Clinical Threshold | Rationale |
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
| ASTM F2101 | Evaluating performance of CAS systems (withdrawn, content merged) | Historical — content now in F2554 |
| ISO 5725 | Accuracy (trueness and precision) of measurement methods | General metrology framework referenced by F2554 |
| IEC 62304 | Software lifecycle | Development process for the navigation software |

## Tracking Technologies

The tracking/guidance approach affects which parts of ASTM F2554 apply:

| Technology | Description | ASTM F2554 Applicability |
|-----------|-------------|-------------------------|
| Optical (infrared) tracking | Cameras track reflective markers on instruments | Full F2554 testing required |
| Electromagnetic tracking | EM field generator + sensors on instruments | Full F2554 testing required |
| Imageless navigation (IMU/accelerometer) | Sensor-based without external tracker | Adapted F2554 testing |
| Image overlay / AR guidance | Camera-based registration without tracking hardware | Adapted F2554 testing |
| Planning-only guidance | Pre-op plan displayed for surgeon reference, no real-time tracking | F2554 may not apply — measurement accuracy (DICOM) is the key standard |
