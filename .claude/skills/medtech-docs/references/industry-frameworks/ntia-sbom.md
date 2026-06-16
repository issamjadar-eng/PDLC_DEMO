# NTIA SBOM Minimum Elements

🔎 **Finding aid — NOT the authoritative source.** Paraphrased distillation of an external standard/framework; no faithful full-text copy exists in this repository (copyrighted). The original document named in the header above is the sole authority — if a clause-level question isn't answered here, state that the original must be consulted; do not infer clause content. `[VERIFY]` marks are unconfirmed against the source.

**Framework**: The Minimum Elements For a Software Bill of Materials (SBOM) (July 2021)
**Source**: National Telecommunications and Information Administration (NTIA), U.S. Department of Commerce
**Referenced In**: FDA Cybersecurity guidance

## Overview

An SBOM is a formal, machine-readable inventory of software components and dependencies that make up a software product. NTIA's minimum elements define the baseline of what an SBOM must contain. FDA's cybersecurity guidance mandates an SBOM as part of the premarket submission for medical devices with cybersecurity considerations.

## Minimum Data Fields

Every SBOM entry must include these fields for each component:

| Field | Description | Example |
|-------|-------------|---------|
| **Supplier Name** | Entity that created, defined, or identifies the component | "OpenCV Project" |
| **Component Name** | Designation assigned to a unit of software by its original supplier | "opencv-python" |
| **Version of the Component** | Identifier used by the supplier to specify a change from a prior version | "4.8.1" |
| **Other Unique Identifiers** | Other identifiers used for identification (e.g., PURL, CPE) | "pkg:pypi/opencv-python@4.8.1" |
| **Dependency Relationship** | Characterizing the relationship that an upstream component has with the software | "opencv-python depends on numpy" |
| **Author of SBOM Data** | Name of the entity that creates the SBOM data | "Manufacturer Inc." |
| **Timestamp** | Record of the date and time of SBOM assembly | "2026-04-15T10:30:00Z" |

## Practices and Processes

Beyond data fields, NTIA defines minimum practices:

### Automation Support
- SBOMs must be machine-readable
- Supported formats:
  - **SPDX** (Software Package Data Exchange) — ISO/IEC 5962:2021
  - **CycloneDX** — OWASP standard
  - **SWID Tags** — ISO/IEC 19770-2
- FDA accepts SPDX and CycloneDX

### Frequency
- SBOM must be generated for each new release or update
- At minimum, generate a new SBOM when:
  - A new version of the software is released
  - A component is added, removed, or updated
  - A security patch is applied

### Depth
- SBOM should include all components at all levels (not just top-level dependencies)
- Transitive dependencies must be included
- If full depth cannot be achieved, document the known unknowns
- Flag components where deeper dependency information is unavailable

### Distribution and Delivery
- SBOM must be available to those who need it (FDA, customers, vulnerability researchers)
- Deliver alongside the software product
- Maintain access to historical SBOMs for previously released versions

### Access Control
- SBOM may contain sensitive information (component versions that reveal attack surface)
- Balance transparency with security — provide to authorized parties
- FDA expects SBOM in the confidential premarket submission

### Errors and Omissions
- Document known gaps in the SBOM
- Establish a process for correcting SBOM errors
- SBOM is a "living document" — accuracy improves over time

## Component Categories

| Category | Examples | SBOM Inclusion |
|----------|---------|----------------|
| Application code | Device application modules | Top-level entries |
| Third-party libraries | Imaging libraries, UI frameworks, math libraries | Required — with full dependency trees |
| AI/ML frameworks | TensorFlow, PyTorch, ONNX Runtime | Required — with all sub-dependencies |
| Operating system | Linux, Windows, embedded OS | Required at component level |
| Firmware | Device-specific firmware if applicable | Required |
| Cloud services | If any module uses cloud infrastructure | Document as external dependencies |
| SOUP items | All Software of Unknown Provenance per IEC 62304 | Required — SOUP list and SBOM must be consistent |

## SBOM Generation Tools

Common tools for generating SBOMs in supported formats:

| Tool | Formats | Language/Ecosystem |
|------|---------|-------------------|
| syft (Anchore) | SPDX, CycloneDX | Multi-language, container images |
| cyclonedx-cli | CycloneDX | Multi-language |
| spdx-sbom-generator | SPDX | Multi-language |
| pip-audit / pip-licenses | CycloneDX | Python |
| npm audit / @cyclonedx/bom | CycloneDX | Node.js |

## Relationship to Vulnerability Management

SBOM enables systematic vulnerability management:

```
SBOM (component inventory)
  → Match against CVE/NVD databases
  → Identify affected components
  → Assess severity and exploitability
  → Prioritize remediation
  → Deploy patches
  → Update SBOM
```
