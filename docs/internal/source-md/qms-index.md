---
source_file: "N/A — authored-in-markdown"
source_path: "qms-index.md"
doc_id: "GL-IDX-QM-001"
doc_type: "QSD"
title: "GlobalLogic QMS Master Index"
format: "md"
conversion_date: "2026-04-21"
conversion_method: "claude-authored"
conversion_fidelity: "faithful"
pages: null
sheets: null
has_images: false
image_count: 0
has_tables: true
has_form_fields: false
references: []
conversion_history:
  - date: "2026-04-21"
    source: "v1 — initial draft under task ben/022"
notes: "Master index of the GlobalLogic QMS scaffold landed across phases P1–P6 of task ben/022."
---

# GL-IDX-QM-001 — GlobalLogic QMS Master Index

_Demo sample data — not for clinical use._

**Document ID:** GL-IDX-QM-001
**Revision:** 1.0
**Effective Date:** 2026-04-21
**Owner:** QMS Administrator / VP Quality, GlobalLogic MedTech

---

## 1. Purpose

Central index for all controlled documents in the demo GlobalLogic QMS. Required by **GL-SOP-QM-001 — Document and Records Control** (§6.6). Every released document is registered here. Orphan documents (not listed) are out-of-control and shall be remediated.

## 2. Categories (by folder)

| Category | Folder | Owner |
|---|---|---|
| Quality Management | [`quality-management/`](quality-management/README.md) | VP Quality |
| Design Controls | [`design-controls/`](design-controls/README.md) | VP R&D |
| Risk Management | [`risk-management/`](risk-management/README.md) | VP Quality |
| Software & Cybersecurity | [`software-cybersecurity/`](software-cybersecurity/README.md) | VP Engineering / Cybersecurity Lead |
| Usability & Clinical | [`usability-clinical/`](usability-clinical/README.md) | Human Factors Lead / Clinical Affairs Director |
| Supplier & Production | [`supplier-production/`](supplier-production/README.md) | VP Operations |
| Post-Market | [`post-market/`](post-market/README.md) | VP Quality / PMS Lead |

## 3. Master Index

### 3.1 Quality Management

| Doc ID | Type | Title | Rev | Effective | Standard Anchor |
|---|---|---|---|---|---|
| GL-MAN-QM-001 | Manual | [Quality Manual](quality-management/quality-manual.md) | 1.0 | 2026-04-21 | ISO 13485:2016; 21 CFR 820; EU MDR 2017/745 |
| GL-SOP-QM-001 | SOP | [Document and Records Control](quality-management/document-and-records-control-sop.md) | 1.0 | 2026-04-21 | ISO 13485 §4.2.4/.5; 21 CFR 820.40; 21 CFR Part 11 |
| GL-SOP-QM-002 | SOP | [Management Review](quality-management/management-review-sop.md) | 1.0 | 2026-04-21 | §5.6; 820.20(c) |
| GL-SOP-QM-003 | SOP | [Training and Competence](quality-management/training-sop.md) | 1.0 | 2026-04-21 | §6.2; 820.25 |
| GL-SOP-QM-004 | SOP | [Internal Audit](quality-management/internal-audit-sop.md) | 1.0 | 2026-04-21 | §8.2.4; 820.22; ISO 19011:2018 |
| GL-SOP-QM-005 | SOP | [CAPA](quality-management/capa-sop.md) | 1.0 | 2026-04-21 | §8.5; 820.100 |
| GL-FORM-QM-001 | Form | [CAPA Form](quality-management/templates/capa-form.md) | 1.0 | 2026-04-21 | GL-SOP-QM-005 |
| GL-FORM-QM-002 | Form | [Management Review Minutes](quality-management/templates/management-review-minutes.md) | 1.0 | 2026-04-21 | GL-SOP-QM-002 |
| GL-FORM-QM-003 | Form | [Training Record](quality-management/templates/training-record.md) | 1.0 | 2026-04-21 | GL-SOP-QM-003 |
| GL-FORM-QM-004 | Form | [Internal Audit Plan](quality-management/templates/audit-plan.md) | 1.0 | 2026-04-21 | GL-SOP-QM-004 |
| GL-FORM-QM-005 | Form | [Document Change Request](quality-management/templates/document-change-request.md) | 1.0 | 2026-04-21 | GL-SOP-QM-001 |

### 3.2 Design Controls

| Doc ID | Type | Title | Rev | Effective | Standard Anchor |
|---|---|---|---|---|---|
| GL-SOP-DC-001 | SOP | [Design Control (Master)](design-controls/design-control-sop.md) | 1.0 | 2026-04-21 | §7.3; 820.30 |
| GL-SOP-DC-002 | SOP | [Design and Development Planning](design-controls/design-planning-sop.md) | 1.0 | 2026-04-21 | §7.3.2; 820.30(b) |
| GL-SOP-DC-003 | SOP | [Design Inputs](design-controls/design-inputs-sop.md) | 1.0 | 2026-04-21 | §7.3.3; 820.30(c) |
| GL-SOP-DC-004 | SOP | [Design Outputs](design-controls/design-outputs-sop.md) | 1.0 | 2026-04-21 | §7.3.4; 820.30(d) |
| GL-SOP-DC-005 | SOP | [Design Review](design-controls/design-review-sop.md) | 1.0 | 2026-04-21 | §7.3.5; 820.30(e) |
| GL-SOP-DC-006 | SOP | [Design V&V](design-controls/design-verification-validation-sop.md) | 1.0 | 2026-04-21 | §7.3.6–.7; 820.30(f)–(g) |
| GL-SOP-DC-007 | SOP | [Design Transfer](design-controls/design-transfer-sop.md) | 1.0 | 2026-04-21 | §7.3.8; 820.30(h); 820.181 |
| GL-SOP-DC-008 | SOP | [Design Change Control](design-controls/design-change-control-sop.md) | 1.0 | 2026-04-21 | §7.3.9; 820.30(i); FDA 510(k) change guidance |
| GL-TMP-DC-001 | Template | [Design and Development Plan](design-controls/templates/design-and-development-plan.md) | 1.0 | 2026-04-21 | GL-SOP-DC-002 |
| GL-TMP-DC-002 | Template | [Design Input Specification](design-controls/templates/design-input-specification.md) | 1.0 | 2026-04-21 | GL-SOP-DC-003 |
| GL-FORM-DC-001 | Form | [Design Review Record](design-controls/templates/design-review-record.md) | 1.0 | 2026-04-21 | GL-SOP-DC-005 |
| GL-TMP-DC-003 | Template | [Design Verification Protocol & Report](design-controls/templates/verification-protocol-report.md) | 1.0 | 2026-04-21 | GL-SOP-DC-006 |
| GL-TMP-DC-004 | Template | [Design Validation Protocol & Report](design-controls/templates/validation-protocol-report.md) | 1.0 | 2026-04-21 | GL-SOP-DC-006 |

### 3.3 Risk Management

| Doc ID | Type | Title | Rev | Effective | Standard Anchor |
|---|---|---|---|---|---|
| GL-SOP-RM-001 | SOP | [Risk Management (Master)](risk-management/risk-management-sop.md) | 1.0 | 2026-04-21 | ISO 14971:2019 |
| GL-WI-RM-001 | WI | [Hazard Analysis](risk-management/hazard-analysis-wi.md) | 1.0 | 2026-04-21 | ISO 14971 §5; TR 24971 §5 |
| GL-WI-RM-002 | WI | [FMEA (dFMEA / pFMEA)](risk-management/fmea-wi.md) | 1.0 | 2026-04-21 | IEC 60812:2018 |
| GL-TMP-RM-001 | Template | [Risk Management Plan](risk-management/templates/risk-management-plan.md) | 1.0 | 2026-04-21 | ISO 14971 §4.4 |
| GL-TMP-RM-002 | Template | [Risk Management Report](risk-management/templates/risk-management-report.md) | 1.0 | 2026-04-21 | ISO 14971 §9 |
| GL-TMP-RM-003 | Template | [Hazard Analysis Worksheet](risk-management/templates/hazard-analysis.md) | 1.0 | 2026-04-21 | ISO 14971 §5 |
| GL-TMP-RM-004 | Template | [FMEA Worksheet](risk-management/templates/fmea-worksheet.md) | 1.0 | 2026-04-21 | IEC 60812 |

### 3.4 Software & Cybersecurity

| Doc ID | Type | Title | Rev | Effective | Standard Anchor |
|---|---|---|---|---|---|
| GL-SOP-SW-001 | SOP | [Medical Device Software Lifecycle](software-cybersecurity/software-lifecycle-sop.md) | 1.0 | 2026-04-21 | IEC 62304:2006+A1:2015; IEC 82304-1 |
| GL-WI-SW-001 | WI | [Software Safety Classification](software-cybersecurity/software-safety-classification-wi.md) | 1.0 | 2026-04-21 | IEC 62304 §4.3 |
| GL-SOP-SW-002 | SOP | [SOUP / OTS Software Management](software-cybersecurity/soup-management-sop.md) | 1.0 | 2026-04-21 | IEC 62304 §5.3/.8; FDA 2019 OTS |
| GL-SOP-SW-003 | SOP | [Software Problem Resolution](software-cybersecurity/software-problem-resolution-sop.md) | 1.0 | 2026-04-21 | IEC 62304 §9 |
| GL-SOP-SW-004 | SOP | [Medical Device Cybersecurity](software-cybersecurity/cybersecurity-sop.md) | 1.0 | 2026-04-21 | IEC 81001-5-1:2021; FDA 2023; AAMI TIR57 |
| GL-WI-SW-002 | WI | [SBOM Generation](software-cybersecurity/sbom-wi.md) | 1.0 | 2026-04-21 | FDA 2023; NTIA; CycloneDX/SPDX |
| GL-TMP-SW-001 | Template | [Software Development Plan](software-cybersecurity/templates/software-development-plan.md) | 1.0 | 2026-04-21 | IEC 62304 §5.1 |
| GL-TMP-SW-002 | Template | [Cybersecurity Plan](software-cybersecurity/templates/cybersecurity-plan.md) | 1.0 | 2026-04-21 | IEC 81001-5-1 §5 |

### 3.5 Usability & Clinical

| Doc ID | Type | Title | Rev | Effective | Standard Anchor |
|---|---|---|---|---|---|
| GL-SOP-UC-001 | SOP | [Usability Engineering](usability-clinical/usability-engineering-sop.md) | 1.0 | 2026-04-21 | IEC 62366-1:2015; IEC/TR 62366-2; FDA 2016 HFE/UE |
| GL-SOP-UC-002 | SOP | [Clinical Evaluation](usability-clinical/clinical-evaluation-sop.md) | 1.0 | 2026-04-21 | EU MDR Art. 61 + Annex XIV; MDCG 2020-6, 2020-13; ISO 14155:2020; 21 CFR 812 |
| GL-TMP-UC-001 | Template | [Use Specification](usability-clinical/templates/use-specification.md) | 1.0 | 2026-04-21 | IEC 62366-1 §5.1 |
| GL-TMP-UC-002 | Template | [Usability Engineering File](usability-clinical/templates/usability-engineering-file.md) | 1.0 | 2026-04-21 | IEC 62366-1 §5 |
| GL-TMP-UC-003 | Template | [Summative Usability Evaluation Protocol & Report](usability-clinical/templates/summative-evaluation-protocol.md) | 1.0 | 2026-04-21 | IEC 62366-1 §5.9; FDA 2016 |
| GL-TMP-UC-004 | Template | [Clinical Evaluation Plan](usability-clinical/templates/clinical-evaluation-plan.md) | 1.0 | 2026-04-21 | MDR Annex XIV Part A; MDCG 2020-6 |
| GL-TMP-UC-005 | Template | [Clinical Evaluation Report](usability-clinical/templates/clinical-evaluation-report.md) | 1.0 | 2026-04-21 | MDCG 2020-13 |

### 3.6 Supplier & Production

| Doc ID | Type | Title | Rev | Effective | Standard Anchor |
|---|---|---|---|---|---|
| GL-SOP-SP-001 | SOP | [Supplier Management](supplier-production/supplier-management-sop.md) | 1.0 | 2026-04-21 | ISO 13485 §7.4.1; 21 CFR 820.50 |
| GL-SOP-SP-002 | SOP | [Purchasing Controls](supplier-production/purchasing-controls-sop.md) | 1.0 | 2026-04-21 | §7.4.2/.3; 820.50 |
| GL-SOP-SP-003 | SOP | [Production and Process Controls](supplier-production/production-process-controls-sop.md) | 1.0 | 2026-04-21 | §7.5; 820.70/.75; GHTF/SG3/N99-10 |
| GL-SOP-SP-004 | SOP | [Control of Nonconforming Product](supplier-production/nonconformance-control-sop.md) | 1.0 | 2026-04-21 | §8.3; 820.90 |
| GL-WI-SP-001 | WI | [Incoming Inspection](supplier-production/incoming-inspection-wi.md) | 1.0 | 2026-04-21 | §7.4.3; ANSI/ASQ Z1.4 |
| GL-FORM-SP-001 | Form | [Supplier Qualification Package](supplier-production/templates/supplier-qualification-package.md) | 1.0 | 2026-04-21 | GL-SOP-SP-001 |
| GL-FORM-SP-002 | Form | [Nonconformance Report](supplier-production/templates/nonconformance-report.md) | 1.0 | 2026-04-21 | GL-SOP-SP-004 |

### 3.7 Post-Market

| Doc ID | Type | Title | Rev | Effective | Standard Anchor |
|---|---|---|---|---|---|
| GL-SOP-PM-001 | SOP | [Post-Market Surveillance](post-market/post-market-surveillance-sop.md) | 1.0 | 2026-04-21 | EU MDR Art. 83–86 + Annex III; ISO 13485 §8.2.1; ISO/TR 20416; MDCG 2022-21 |
| GL-SOP-PM-002 | SOP | [Complaint Handling](post-market/complaint-handling-sop.md) | 1.0 | 2026-04-21 | §8.2.2; 21 CFR 820.198 |
| GL-SOP-PM-003 | SOP | [Adverse Event Reporting (Vigilance)](post-market/adverse-event-reporting-sop.md) | 1.0 | 2026-04-21 | 21 CFR 803, 806; EU MDR Art. 87–89; MDCG 2023-3 Rev.1 |
| GL-TMP-PM-001 | Template | [PMS Plan](post-market/templates/pms-plan.md) | 1.0 | 2026-04-21 | EU MDR Annex III §1.1 |
| GL-FORM-PM-001 | Form | [Complaint Form](post-market/templates/complaint-form.md) | 1.0 | 2026-04-21 | 21 CFR 820.198 |

## 4. Cross-Category Relationships

```
Design Controls (§7.3)
        │
        ├── drives ──▶ Risk Management (§7.1 risk-based)  ◀── feeds ── PMS / Complaints / Vigilance
        │                     │                                                  │
        │                     └── integrates ──▶ Usability (IEC 62366-1)          │
        │                                        Clinical Evaluation (MDR)        │
        │                                        Software (IEC 62304)             │
        │                                        Cybersecurity (IEC 81001-5-1)    │
        │                                                                         │
        └── transfers to ──▶ Production / Supplier (§7.4–§7.5) ──▶ Field  ───────┘
                                                                    │
                                                    Lifecycle ←── Management Review (§5.6) ←── all above
                                                                    │
                                                            CAPA (§8.5) ── closes loops
```

## 5. Standards Coverage

| Standard | Referencing documents |
|---|---|
| ISO 13485:2016 | GL-MAN-QM-001; all QM SOPs; DC SOPs; SP SOPs; PM SOPs |
| 21 CFR Part 820 | GL-MAN-QM-001; QM, DC, SP, PM SOPs |
| 21 CFR Part 11 | GL-SOP-QM-001 |
| EU MDR 2017/745 | GL-MAN-QM-001; GL-SOP-DC-008; GL-SOP-UC-002; GL-SOP-PM-001/-003 |
| ISO 14971:2019 | GL-SOP-RM-001 + all RM artifacts |
| ISO/TR 24971:2020 | GL-SOP-RM-001; GL-WI-RM-001 |
| IEC 60812:2018 | GL-WI-RM-002; GL-TMP-RM-004 |
| IEC 62304:2006+A1:2015 | GL-SOP-SW-001/-002/-003; GL-WI-SW-001; GL-TMP-SW-001 |
| IEC 82304-1:2016 | GL-SOP-SW-001 |
| IEC 81001-5-1:2021 | GL-SOP-SW-004; GL-TMP-SW-002 |
| IEC 62366-1:2015 | GL-SOP-UC-001 + all UC artifacts |
| FDA HFE/UE Guidance (2016) | GL-SOP-UC-001; GL-TMP-UC-003 |
| FDA Cybersecurity Guidance (2023) | GL-SOP-SW-004; GL-WI-SW-002 |
| FDA 510(k) Change Guidance (2017) | GL-SOP-DC-008 |
| ISO 14155:2020 | GL-SOP-UC-002 |
| ISO 19011:2018 | GL-SOP-QM-004 |
| GHTF/SG3/N99-10:2004 | GL-SOP-SP-003 |
| ANSI/ASQ Z1.4 | GL-WI-SP-001 |
| MDCG 2020-6, 2020-13, 2022-21, 2023-3 Rev.1 | GL-SOP-UC-002; GL-SOP-PM-001/-003 |
| NTIA SBOM; CycloneDX 1.5 / SPDX 2.3 | GL-WI-SW-002 |

## 6. Counts

- Manuals: 1
- SOPs: 25
- Work Instructions: 6
- Templates: 14
- Forms: 9
- **Total released documents: 55** (all Rev 1.0, 2026-04-21)

## 7. Revision History

| Rev | Date | Author | Summary |
|---|---|---|---|
| 1.0 | 2026-04-21 | Ben Xavier (via Claude, task ben/022) | Initial index. Captures all 55 documents released across P1–P6. |
