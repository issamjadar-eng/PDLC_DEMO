# DICOM — Digital Imaging and Communications in Medicine

**Framework**: DICOM Standard (PS3.x series, continuously updated)
**Source**: NEMA (National Electrical Manufacturers Association) / DICOM Standards Committee
**Referenced In**: Fundamental to any imaging-based SaMD; FDA expects DICOM conformance for devices that import/process medical images

## Overview

DICOM is the universal standard for storing, transmitting, and processing medical images. Any software that reads, writes, or displays medical imaging data must handle DICOM correctly.

Getting DICOM right affects:
- **Data integrity**: Measurements and plans derived from imaging are only valid if the DICOM data is correctly interpreted
- **Interoperability**: The platform must work with imaging from any scanner/vendor in any hospital
- **Regulatory**: FDA expects DICOM conformance statements for imaging-based devices

## Key DICOM Parts

### PS3.3 — Information Object Definitions (IODs)

Defines the data structures for different types of medical images and related objects.

| IOD | Description |
|-----|-------------|
| CT Image | Computed Tomography slices |
| MR Image | Magnetic Resonance slices |
| Digital X-Ray (DX) | 2D radiographs |
| Secondary Capture (SC) | Screenshots, processed images |
| RT Structure Set | Contour/segmentation data |
| Surface Segmentation | 3D surface mesh data |
| Structured Report (SR) | Machine-readable clinical reports |

### PS3.4 — Service Class Specifications

Defines how DICOM objects are exchanged between systems.

| Service Class | Role | Description |
|---------------|------|-------------|
| Storage SCP/SCU | Receive/send DICOM objects | Import images from PACS/scanner; export planning results |
| Query/Retrieve (C-FIND, C-MOVE, C-GET) | Search and retrieve studies | Browse and pull patient studies from hospital PACS |
| Worklist Management | Query scheduled procedures | Match planning cases to scheduled procedures |
| WADO-RS (Web Access to DICOM Objects) | HTTP-based retrieval | Cloud/web-based image access |

### PS3.5 — Data Structures and Encoding

Defines how DICOM data is encoded in files and network transfers.

Key considerations:
- Transfer syntaxes (encoding formats) — must support common syntaxes used by hospital scanners
- Character sets — international character support for patient names
- Value representations — correct data type handling

Common transfer syntaxes:

| Transfer Syntax | Description | Priority |
|----------------|-------------|----------|
| Implicit VR Little Endian | Default DICOM encoding | Required |
| Explicit VR Little Endian | Most common modern encoding | Required |
| JPEG Lossless | Lossless compressed CT/MR | Required |
| JPEG 2000 Lossless | Newer lossless compression | Recommended |
| JPEG Baseline (Lossy) | Lossy compressed (DX images) | Required for X-ray support |
| RLE Lossless | Run-length encoding | Recommended |

### PS3.6 — Data Dictionary

The master list of all DICOM data elements (tags). Key tag groups:

| Tag Group | Description |
|-----------|-------------|
| Patient (0010,xxxx) | Patient demographics |
| Study (0008,xxxx) | Study-level metadata |
| Series (0020,xxxx) | Series-level metadata |
| Image (0028,xxxx) | Pixel data attributes |
| Frame of Reference (0020,0052) | Spatial reference frame — links images to a common coordinate system |
| Pixel Spacing (0028,0030) | Physical size of pixels — all measurements depend on correct pixel spacing |
| Image Position Patient (0020,0032) | 3D position of image — 3D reconstruction accuracy depends on this |
| Image Orientation Patient (0020,0037) | Image plane orientation — correct anatomical orientation |
| Slice Thickness (0018,0050) | Distance between slices — 3D reconstruction accuracy |
| Spacing Between Slices (0018,0088) | Physical spacing — may differ from slice thickness |

### PS3.10 — Media Storage and File Format

Defines the DICOM file format (.dcm files).

Key elements:
- File Meta Information header (preamble, DICM prefix, file meta elements)
- Dataset encoding per the transfer syntax
- Multi-frame support for 3D/4D data

### PS3.15 — Security and System Management Profiles

Defines security profiles for DICOM communication.

| Profile | Description |
|---------|-------------|
| TLS Secure Transport | Encrypted DICOM network communication |
| Digital Signatures | Integrity verification of DICOM objects |
| Attribute Confidentiality | De-identification profiles |
| Audit Trail | Logging of DICOM transactions |

### PS3.17 — Explanatory Information

Contains informative annexes with implementation guidance. Useful reference for:
- Coordinate system conventions (patient, image, frame of reference)
- Transformation matrices between coordinate spaces
- Measurement derivation from imaging data

### PS3.18 — Web Services (DICOMweb)

RESTful APIs for DICOM data access. Increasingly used in modern architectures.

| Service | Description |
|---------|-------------|
| WADO-RS | Retrieve DICOM objects via REST |
| STOW-RS | Store DICOM objects via REST |
| QIDO-RS | Query DICOM objects via REST |

## Critical Accuracy Considerations

For surgical planning platforms, DICOM accuracy directly affects patient safety.

### Coordinate Systems
- **Patient coordinate system**: LPS (Left, Posterior, Superior) or RAS (Right, Anterior, Superior)
- DICOM uses **LPS** by default — verify all processing maintains correct orientation
- Frame of Reference UID links images that share a coordinate space
- Registration between image series requires matching Frame of Reference or explicit registration

### Measurement Accuracy
- All linear measurements derive from Pixel Spacing and Slice Thickness/Spacing
- Pixel Spacing source matters: detector vs. calibrated (magnification correction for X-ray)
- For CT: spacing is typically accurate from reconstruction parameters
- For X-ray: magnification factor must be accounted for (calibration marker or known distance)
- **Risk**: Incorrect pixel spacing interpretation leads to incorrect measurements and wrong implant sizing

### 3D Reconstruction
- Volume reconstruction from CT depends on: Image Position Patient, Image Orientation Patient, Pixel Spacing, Slice Thickness
- Non-uniform slice spacing must be handled correctly
- Gantry tilt (CT) must be accounted for in reconstruction
- Missing slices must be detected and flagged

## DICOM Conformance Statement

FDA expects a DICOM Conformance Statement for imaging-based SaMD. This document describes:
- Which DICOM services the device supports (SCP/SCU roles)
- Which IODs are supported (import/export)
- Which transfer syntaxes are supported
- Security profiles implemented
- Networking capabilities and configuration
- Limitations and known issues
