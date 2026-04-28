# Tier 1 Regulatory Distillation — FDA PCCP General Guidance

**Guidance**: Predetermined Change Control Plans for Medical Devices
**Date**: August 22, 2024 (Draft)
**Statutory basis**: FD&C Act §515C (added by FDORA, December 29, 2022)
**Topic coverage**: regulatory-submission, configuration-change, validation
**Distillation date**: 2026-04-21
**Source references**:
- `.claude/skills/medtech-docs/references/fda-guidance/pccp-general-distilled.md`

> **Note**: FDA guidance is nonbinding. Obligations represent FDA's stated expectations for premarket submissions. "Verbatim" fields quote the distilled reference, not the original FDA document.

---

<a id="OBL-PCCP-001"></a>

```yaml
id: OBL-PCCP-001
title: "PCCP Guiding Principles"
source: FDA PCCP General Guidance (2024) §III Guiding Principles
section: "Guiding Principles 1–5"
scope_flags: [pccp, 510k]
topic: regulatory-submission
artifact_type: submission-content
dhf_owner: system
min_iec62304_class: A
applies_to: [PCCP Document, 510(k) Submission Cover Letter, Device Description]
verbatim: "A PCCP is part of the device marketing authorization. The manufacturer is required to implement modifications consistent with the authorized PCCP. A PCCP must include specific modifications the manufacturer intends to make — not any/all possible modifications. PCCPs work alongside the existing Device Modifications guidances, which still apply for modifications not covered by or not consistent with the PCCP."
extracted_requirements:
  - A PCCP must be filed as part of the 510(k) marketing submission — it is NOT a separate post-market document
  - PCCP must specify only a few, specific verifiable/validatable modifications — overly broad modifications prevent FDA review
  - The authorized PCCP is binding — device considered adulterated/misbranded if PCCP is not followed
  - Modifications outside the PCCP scope must be evaluated under standard Device Modifications guidances
  - PCCP referenced in the letter of authorization (title and version number)
```

**Context**: The PCCP is a core component of HipLink's 510(k) submission — not an optional add-on. The HipLink PCCP must specify only the specific modifications Arthrex plans to make post-clearance (not every conceivable AI improvement). FDA's review determines reasonable assurance that even post-PCCP modifications maintain safety and effectiveness. Once authorized, every modification implemented under the PCCP must follow the Modification Protocol exactly.

---

<a id="OBL-PCCP-002"></a>

```yaml
id: OBL-PCCP-002
title: "PCCP Description of Modifications"
source: FDA PCCP General Guidance (2024) §IV Three-Component Structure
section: "Description of Modifications"
scope_flags: [pccp, 510k]
topic: regulatory-submission
artifact_type: submission-content
dhf_owner: system
min_iec62304_class: A
applies_to: [PCCP Document — Description of Modifications section]
verbatim: "Enumerate each individual proposed modification. Provide specific rationale for each change. Reference labeling sections anticipated to be impacted. Present at detail level permitting understanding of specific modifications. Link each modification to a specific performance evaluation activity. Keep to a limited number of specific, verifiable/validatable modifications."
extracted_requirements:
  - For each planned modification: enumerate it individually with specific rationale
  - Link each modification to at least one specific performance evaluation activity in the Modification Protocol
  - Identify which labeling sections will be updated when each modification is implemented
  - Modifications must stay within the authorized intended use and indications for use
  - All modifications must be verifiable and/or validatable — vague modifications are rejected
```

**Context**: For HipLink, the Description of Modifications must separately enumerate each planned change type: e.g., "Re-train anatomy segmentation algorithm on expanded dataset to improve Pre-Op sizing accuracy," "Add support for new C-arm model for Intra-Op guidance," "Update UI for anatomical landmark confirmation workflow." Each is a separate enumerated modification with specific rationale and linked V&V activity.

---

<a id="OBL-PCCP-003"></a>

```yaml
id: OBL-PCCP-003
title: "PCCP Modification Protocol"
source: FDA PCCP General Guidance (2024) §IV Three-Component Structure
section: "Modification Protocol"
scope_flags: [pccp, 510k]
topic: regulatory-submission
artifact_type: submission-content
dhf_owner: system
min_iec62304_class: A
applies_to: [PCCP Document — Modification Protocol section, V&V Plan]
verbatim: "Plans to V&V the modified device meets specifications for each modification. Plans to verify unmodified specifications are not impacted. Plans for V&V of entire device following each individual modification AND in aggregate. Study design, performance metrics, pre-defined acceptance criteria, and statistical tests. Affirmative statement: unresolvable performance failures prevent implementation."
extracted_requirements:
  - Define V&V methods and pre-specified acceptance criteria for each modification before implementing it
  - Include plans to verify that unmodified portions of the device are not degraded by each modification
  - Define V&V of the entire device (not just the modified function) following each modification
  - Include study design, performance metrics, statistical tests, and acceptance criteria
  - Include affirmative statement: if acceptance criteria cannot be met (unresolvable failure), the modification must not be implemented
  - Describe how the modification will be deployed to users (update procedure)
  - A traceability table linking each modification to its performance evaluation methods is required
```

**Context**: The Modification Protocol is the operational core of the PCCP — it pre-authorizes the V&V approach so Arthrex can implement modifications without a new 510(k). For HipLink AI modifications (algorithm re-training), the protocol must define: what datasets are used for testing (multi-site, representative), what metrics are required (sensitivity/specificity with acceptance thresholds), and how a performance failure triggers a halt. Pre-specification before implementation is essential — modifying acceptance criteria after seeing results requires FDA concurrence.

---

<a id="OBL-PCCP-004"></a>

```yaml
id: OBL-PCCP-004
title: "PCCP Impact Assessment"
source: FDA PCCP General Guidance (2024) §IV Three-Component Structure
section: "Impact Assessment"
scope_flags: [pccp, 510k]
topic: regulatory-submission
artifact_type: submission-content
dhf_owner: system
min_iec62304_class: A
applies_to: [PCCP Document — Impact Assessment section, Risk Management File]
verbatim: "Compare the version with each modification to the version without any modifications. Discuss benefits and risks (including risks of harm per ISO 14971) of each individual modification. Discuss how V&V activities continue to ensure safety and effectiveness. Discuss interactions — how implementation of one modification impacts another. Describe cumulative impact of implementing all modifications together."
extracted_requirements:
  - For each modification: compare modified vs. unmodified device version (benefit-risk analysis)
  - Discuss risks of harm using ISO 14971 framework for each modification
  - Explain how the Modification Protocol V&V activities ensure continued safety and effectiveness
  - Assess interaction effects: how implementing modification A affects the safety/effectiveness of modification B
  - Assess cumulative impact of implementing all PCCP modifications together — not just individually
  - For HipLink (MFD): discuss impact on overall device functionality including both SaMD modules and Management Services
```

**Context**: The Impact Assessment is where Arthrex demonstrates that the PCCP modifications are safe. It must show that the cumulative effect of all planned modifications (individually and together) does not introduce new safety risks or degrade effectiveness. For HipLink, this means analyzing interactions between Pre-Op AI updates and Intra-Op guidance — a Pre-Op algorithm change may affect the quality of the plan that Intra-Op imports, which could have downstream patient safety implications.

---

<a id="OBL-PCCP-005"></a>

```yaml
id: OBL-PCCP-005
title: "PCCP Scope Risk Assessment"
source: FDA PCCP General Guidance (2024) §V Risk Assessment for 510(k) Devices
section: "Risk-Based Assessment"
scope_flags: [pccp, 510k]
topic: regulatory-submission
artifact_type: analysis
dhf_owner: system
min_iec62304_class: A
applies_to: [PCCP Scope Determination, Change Impact Analysis]
verbatim: "Could the modification be a major change to the intended use? If YES: generally NOT appropriate for PCCP. Could the modification introduce a NEW risk? If YES: generally NOT appropriate for PCCP. Could the modification significantly MODIFY an existing risk? If YES and risks adequately mitigated: generally MAY be appropriate."
extracted_requirements:
  - Conduct a risk-based assessment for each proposed modification to confirm PCCP appropriateness
  - Modifications that constitute major intended use changes are NOT eligible for PCCP
  - Modifications that introduce new risks (not existing in the cleared device) are NOT eligible for PCCP
  - Modifications that modify (not introduce) existing risks may be eligible if risks are adequately mitigated through the Modification Protocol
  - Document the risk assessment reasoning for each modification's PCCP eligibility in the Impact Assessment
```

**Context**: This gate-keeps what goes INTO the HipLink PCCP. For each planned modification category, Arthrex must document why it doesn't constitute a major intended use change and doesn't introduce new patient risks. Examples of modifications likely NOT eligible: adding a new clinical indication (hip dysplasia correction); modifications likely eligible: improving anatomy segmentation accuracy on the same patient population and imaging types.

---

<a id="OBL-PCCP-006"></a>

```yaml
id: OBL-PCCP-006
title: "PCCP Version Control"
source: FDA PCCP General Guidance (2024) §VI Version Control
section: "Version Control and Maintenance"
scope_flags: [pccp, 510k]
topic: configuration-change
artifact_type: process-record
dhf_owner: system
min_iec62304_class: A
applies_to: [PCCP Document, Design Change Records, UDI Records]
verbatim: "Only one version of an authorized PCCP should exist per device at any time. A PCCP can evolve over time through future marketing submissions. FDA does not intend to re-review adequacy of modifications already implemented consistent with an authorized PCCP. For 510(k) devices: Predicate comparison is to the version pre-PCCP changes."
extracted_requirements:
  - Maintain only one version of the authorized PCCP per device at any time
  - PCCP modifications require a new marketing submission (new 510(k) to amend the PCCP)
  - Each PCCP-implemented change must be documented under the QMS design control process (§7.3.9)
  - New UDIs required when version/model numbers change following PCCP modifications
  - Labeling must NOT include descriptions of unimplemented modifications
  - Subsequent 510(k)s using a PCCP-modified device as predicate compare to the version BEFORE PCCP changes
```

**Context**: PCCP version control is a post-market quality system obligation. After clearance, Arthrex must maintain a single authoritative PCCP version and document each modification implementation as a QMS design change. If the PCCP itself needs to change (e.g., to add a new modification category), a new 510(k) is required. This creates the rhythm: initial 510(k) with PCCP → implement modifications under PCCP → future 510(k) to expand the PCCP → repeat.
