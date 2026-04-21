# Software Lifecycle & Cybersecurity (`software-cybersecurity/`)

SOPs, work instructions, and templates for IEC 62304 software lifecycle and IEC 81001-5-1 cybersecurity.

_Demo sample data — not for clinical use._

## Contents

| Doc ID | Type | Title | Anchor |
|---|---|---|---|
| GL-SOP-SW-001 | SOP | [Medical Device Software Lifecycle](software-lifecycle-sop.md) | IEC 62304:2006+A1:2015 (all); IEC 82304-1 |
| GL-WI-SW-001 | WI | [Software Safety Classification](software-safety-classification-wi.md) | IEC 62304 §4.3 |
| GL-SOP-SW-002 | SOP | [SOUP / Off-the-Shelf Software Management](soup-management-sop.md) | IEC 62304 §5.3.3/.4, §8; FDA 2019 OTS |
| GL-SOP-SW-003 | SOP | [Software Problem Resolution](software-problem-resolution-sop.md) | IEC 62304 §9 |
| GL-SOP-SW-004 | SOP | [Medical Device Cybersecurity](cybersecurity-sop.md) | IEC 81001-5-1:2021; FDA 2023 cyber guidance; AAMI TIR57 |
| GL-WI-SW-002 | WI | [SBOM Generation](sbom-wi.md) | FDA 2023; NTIA minimum elements; CycloneDX/SPDX |
| GL-TMP-SW-001 | Template | [Software Development Plan](templates/software-development-plan.md) | IEC 62304 §5.1 |
| GL-TMP-SW-002 | Template | [Cybersecurity Plan](templates/cybersecurity-plan.md) | IEC 81001-5-1 §5 |

## Conventions

- Doc IDs follow `GL-<TYPE>-SW-<NNN>`.
- SOUP inventory is part of the SBOM; both are required at each release.
- Cyber risks that can result in patient harm are tracked as safety hazards in the RMF (see GL-SOP-RM-001).
- Classification (Class A/B/C) is determined per GL-WI-SW-001 with rationale captured in GL-TMP-SW-001.

## Changelog

| Date | Author | Summary |
|---|---|---|
| 2026-04-21 | Ben Xavier (via Claude, task ben/022) | Initial scaffold — 4 SOPs, 2 WIs, 2 templates. |
