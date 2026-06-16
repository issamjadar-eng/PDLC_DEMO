# 45 CFR Part 164 — Security and Privacy of Individually Identifiable Health Information (HIPAA)

🔎 **Finding aid — NOT the authoritative source.** Distilled summary with selected commentary. Ground and cite the faithful verbatim full text [`source-md/45-cfr-part-164.md`](source-md/45-cfr-part-164.md) (a no-LLM transcription of the eCFR XML), not this file. Regulations change — verify currency against the live eCFR before relying on it in a submission. `[VERIFY]` marks are unconfirmed.

**Citation**: 45 CFR Part 164 (Title 45, Subtitle A, Subchapter C — "Administrative Data Standards and Related Requirements")
**Authority**: 42 U.S.C. 1302(a), 1320d–1320d-9, 1320d-2 note; sec. 264 of Pub. L. 104-191 (HIPAA); secs. 13400–13424 of Pub. L. 111-5 (HITECH Act)
**Promulgating Agency**: HHS / Office for Civil Rights (OCR)
**Status**: Active (current at retrieval date — see Source provenance). A major Security Rule overhaul is **proposed but not final** — see "Pending rulemaking" below.
**Source**: eCFR API — `https://www.ecfr.gov/api/versioner/v1/full/<date>/title-45.xml?part=164`

## Scope

Part 164 is the operative regulatory text of the **HIPAA Administrative Simplification** rules. It binds **covered entities** (health plans, clearinghouses, and health-care providers who transmit health information electronically) and their **business associates**. For a connected medical device program, the device manufacturer is typically **not itself a covered entity**, but it is very often a **business associate** (or a business associate's subcontractor) the moment its SaMD, cloud platform, or telemetry path creates, receives, maintains, or transmits **electronic protected health information (ePHI)** on a covered entity's behalf. When that relationship exists, the Security Rule (Subpart C) flows down to the manufacturer by contract (§ 164.314 / § 164.308(b)).

Part 164 has three load-bearing subparts:

| Subpart | Title | Common name |
|---------|-------|-------------|
| C | Security Standards for the Protection of Electronic Protected Health Information (§§ 164.302–164.318) | **Security Rule** |
| D | Notification in the Case of Breach of Unsecured Protected Health Information (§§ 164.400–164.414) | **Breach Notification Rule** |
| E | Privacy of Individually Identifiable Health Information (§§ 164.500–164.534) | **Privacy Rule** |

(Subpart A is general provisions; Subpart B is reserved.)

**This distillation anchors on Subpart C (the Security Rule)** — it is the device-relevant subpart, governing the safeguards a manufacturer's software/cloud must implement to protect ePHI. Subparts D and E are summarized and pointered, not distilled section-by-section: the Privacy Rule mostly governs a covered entity's *use and disclosure* practices (not device safeguards), and the Breach Rule's obligations reach a business-associate manufacturer chiefly through the § 164.410 reporting duty.

## Section Index — Subpart C (Security Rule)

| Section | Title | Notes |
|---------|-------|-------|
| § 164.302 | Applicability | Covered entities **and** business associates must comply w.r.t. ePHI |
| § 164.304 | Definitions | Defines *access, encryption, integrity, availability, confidentiality, authentication, information system,* etc. |
| § 164.306 | Security standards: General rules | CIA triad; flexibility-of-approach; the **Required vs. Addressable** framework |
| § 164.308 | **Administrative safeguards** | Risk analysis, risk management, workforce security, contingency planning, evaluation, BA contracts |
| § 164.310 | **Physical safeguards** | Facility access, workstation use/security, device & media controls |
| § 164.312 | **Technical safeguards** | Access control, audit controls, integrity, authentication, transmission security |
| § 164.314 | Organizational requirements | Business-associate contract content; group-health-plan requirements |
| § 164.316 | Policies and procedures and documentation requirements | Written policies; 6-year retention |
| § 164.318 | Compliance dates | Original 2005/2006 dates (historical) |
| Appendix A | Security Standards: Matrix | The canonical standards × implementation-specs (R/A) table |

## Subpart C — Security Standards (the Security Rule)

### § 164.306 — Security standards: General rules

The Security Rule's spine. Two ideas a device program must internalize: the **CIA triad obligation** and the **Required-vs-Addressable** framework.

> **(a) General requirements.** Covered entities and business associates must do the following:
> (1) Ensure the confidentiality, integrity, and availability of all electronic protected health information the covered entity or business associate creates, receives, maintains, or transmits.
> (2) Protect against any reasonably anticipated threats or hazards to the security or integrity of such information.
> (3) Protect against any reasonably anticipated uses or disclosures of such information that are not permitted or required under subpart E of this part.
> (4) Ensure compliance with this subpart by its workforce.
>
> **(b) Flexibility of approach.** (1) Covered entities and business associates may use any security measures that allow [them] to reasonably and appropriately implement the standards and implementation specifications … (2) In deciding which security measures to use, a covered entity or business associate must take into account the following factors: (i) The size, complexity, and capabilities …; (ii) The … technical infrastructure, hardware, and software security capabilities; (iii) The costs of security measures; (iv) The probability and criticality of potential risks to electronic protected health information.

> **(d) Implementation specifications.** (1) Implementation specifications are **required** or **addressable**. … (3) When a standard … includes addressable implementation specifications, a covered entity or business associate must — (i) Implement the … specification if reasonable and appropriate; or (ii) If implementing … is not reasonable and appropriate — (A) Document why …; and (B) Implement an equivalent alternative measure if reasonable and appropriate.

**Why this matters.**
- **"Addressable" ≠ "optional."** This is the single most-misread word in the Security Rule. An addressable spec must be implemented *if reasonable and appropriate*; if not, the entity must **document the rationale and implement an equivalent alternative.** Skipping an addressable spec silently is a non-compliance pattern. (Note: the 2025 NPRM proposes to **remove the addressable/required distinction entirely** — see Pending rulemaking.)
- **Flexibility-of-approach maps cleanly onto ISO 14971 risk thinking.** § 164.306(b)(2)(iv) — "probability and criticality of potential risks" — is a risk-based control-selection mandate. A device program already running an ISO 14971 risk process and an IEC 81001-5-1 / FDA-premarket cybersecurity threat model can route Security Rule compliance through the same risk machinery rather than standing up a parallel process.

### § 164.308 — Administrative safeguards

The largest standard. Verbatim of the load-bearing first standard (the **security management process** — where the mandatory risk analysis lives):

> **(a)** A covered entity or business associate must, in accordance with § 164.306:
> **(1)(i) Standard: Security management process.** Implement policies and procedures to prevent, detect, contain, and correct security violations.
> (ii) Implementation specifications:
> (A) **Risk analysis (Required).** Conduct an accurate and thorough assessment of the potential risks and vulnerabilities to the confidentiality, integrity, and availability of electronic protected health information held by the covered entity or business associate.
> (B) **Risk management (Required).** Implement security measures sufficient to reduce risks and vulnerabilities to a reasonable and appropriate level to comply with § 164.306(a).
> (C) **Sanction policy (Required).** Apply appropriate sanctions against workforce members who fail to comply …
> (D) **Information system activity review (Required).** Implement procedures to regularly review records of information system activity, such as audit logs, access reports, and security incident tracking reports.

The other § 164.308(a) standards (with their implementation-spec R/A status — see Appendix A for the full matrix):

| Standard | Citation | Key implementation specs |
|----------|----------|--------------------------|
| Assigned security responsibility | (a)(2) | Identify the security official (R) |
| Workforce security | (a)(3) | Authorization/supervision (A); workforce clearance (A); termination procedures (A) |
| Information access management | (a)(4) | Isolating clearinghouse function (R); access authorization (A); access establishment & modification (A) |
| Security awareness and training | (a)(5) | Security reminders (A); protection from malicious software (A); log-in monitoring (A); password management (A) |
| Security incident procedures | (a)(6) | Response and reporting (R) |
| Contingency plan | (a)(7) | Data backup plan (R); disaster recovery plan (R); emergency mode operation plan (R); testing & revision (A); applications & data criticality analysis (A) |
| Evaluation | (a)(8) | Periodic technical & non-technical evaluation (R) |
| Business associate contracts | (b) | Written contract / flow-down to subcontractors (R) — see § 164.314(a) |

**Why this matters.** **Risk analysis (a)(1)(ii)(A) is the keystone Required spec** — OCR enforcement actions overwhelmingly cite a missing or inadequate risk analysis as the root finding. NIST SP 800-66 Rev. 2 (`../industry-frameworks/nist-sp-800-66.md`) exists primarily to operationalize this section.

### § 164.310 — Physical safeguards

> A covered entity or business associate must, in accordance with § 164.306:
> **(a)(1) Standard: Facility access controls.** Implement policies and procedures to limit physical access to its electronic information systems and the facility or facilities in which they are housed …
> **(b) Standard: Workstation use.** … specify the proper functions to be performed, the manner …, and the physical attributes of the surroundings of a specific workstation or class of workstation …
> **(c) Standard: Workstation security.** Implement physical safeguards for all workstations that access electronic protected health information, to restrict access to authorized users.
> **(d)(1) Standard: Device and media controls.** Implement policies and procedures that govern the receipt and removal of hardware and electronic media that contain electronic protected health information into and out of a facility, and the movement of these items within the facility.

Implementation specs: contingency operations (A), facility security plan (A), access control & validation (A), maintenance records (A); device/media — **disposal (R), media re-use (R)**, accountability (A), data backup & storage (A).

**Why this matters for a device program.** The **device and media controls (d)** standard is directly on point for medical-device hardware that stores ePHI (pump logs, local cache, removable media). Sanitization-before-disposal and media re-use are **Required** — a manufacturer's servicing, RMA, and end-of-life processes must enforce them.

### § 164.312 — Technical safeguards

The subpart most directly satisfied by the device's own software architecture.

> A covered entity or business associate must, in accordance with § 164.306:
> **(a)(1) Standard: Access control.** Implement technical policies and procedures for electronic information systems that maintain electronic protected health information to allow access only to those persons or software programs that have been granted access rights as specified in § 164.308(a)(4).
> (2) Implementation specifications:
> (i) **Unique user identification (Required).** Assign a unique name and/or number for identifying and tracking user identity.
> (ii) **Emergency access procedure (Required).** Establish (and implement as needed) procedures for obtaining necessary electronic protected health information during an emergency.
> (iii) **Automatic logoff (Addressable).** Implement electronic procedures that terminate an electronic session after a predetermined time of inactivity.
> (iv) **Encryption and decryption (Addressable).** Implement a mechanism to encrypt and decrypt electronic protected health information.
> **(b) Standard: Audit controls.** Implement hardware, software, and/or procedural mechanisms that record and examine activity in information systems that contain or use electronic protected health information.
> **(c)(1) Standard: Integrity.** Implement policies and procedures to protect electronic protected health information from improper alteration or destruction.
> (2) Implementation specification: **Mechanism to authenticate electronic protected health information (Addressable).** …
> **(d) Standard: Person or entity authentication.** Implement procedures to verify that a person or entity seeking access to electronic protected health information is the one claimed.
> **(e)(1) Standard: Transmission security.** Implement technical security measures to guard against unauthorized access to electronic protected health information that is being transmitted over an electronic communications network.
> (2) Implementation specifications: (i) **Integrity controls (Addressable).** … (ii) **Encryption (Addressable).** Implement a mechanism to encrypt electronic protected health information whenever deemed appropriate.

**Why this matters for a device program.** This section is the **technical-requirements checklist** for SaMD/cloud handling ePHI, and it maps almost one-to-one onto requirements a SRS already carries: unique user IDs, RBAC, session auto-logoff, audit logging, integrity/anti-tamper, authentication, and TLS-in-transit / encryption-at-rest. **Encryption is "Addressable"** in the current rule — but addressable means "do it or document a defensible alternative," and for a networked pump/cloud, electing *not* to encrypt is rarely defensible. The 2025 NPRM proposes to make encryption (and MFA) **Required**.

### § 164.316 — Policies, procedures, and documentation

> **(b)(2)(i) Time limit (Required).** Retain the documentation … for **6 years** from the date of its creation or the date when it last was in effect, whichever is later.
> **(iii) Updates (Required).** Review documentation periodically, and update as needed, in response to environmental or operational changes affecting the security of the electronic protected health information.

**Why this matters.** The **6-year documentation retention** is a hard records-management requirement that interacts with DHF retention. Security risk analyses, policies, and the addressable-spec rationales must be retained and kept current.

### Appendix A to Subpart C — Security Standards Matrix

The regulation's own canonical table of every standard and its implementation specifications, marked **(R) Required** or **(A) Addressable**. Reproduced (abridged) as the authoritative checklist:

| Safeguard group | Standard | Citation | Implementation specs (R/A) |
|-----------------|----------|----------|----------------------------|
| Administrative | Security Management Process | 164.308(a)(1) | Risk Analysis (R); Risk Management (R); Sanction Policy (R); Information System Activity Review (R) |
| Administrative | Assigned Security Responsibility | 164.308(a)(2) | (R) |
| Administrative | Workforce Security | 164.308(a)(3) | Authorization/Supervision (A); Workforce Clearance (A); Termination Procedures (A) |
| Administrative | Information Access Management | 164.308(a)(4) | Isolating Clearinghouse Function (R); Access Authorization (A); Access Establishment & Modification (A) |
| Administrative | Security Awareness and Training | 164.308(a)(5) | Security Reminders (A); Protection from Malicious Software (A); Log-in Monitoring (A); Password Management (A) |
| Administrative | Security Incident Procedures | 164.308(a)(6) | Response and Reporting (R) |
| Administrative | Contingency Plan | 164.308(a)(7) | Data Backup Plan (R); Disaster Recovery Plan (R); Emergency Mode Operation Plan (R); Testing & Revision (A); Applications & Data Criticality Analysis (A) |
| Administrative | Evaluation | 164.308(a)(8) | (R) |
| Administrative | Business Associate Contracts | 164.308(b) | Written Contract or Other Arrangement (R) |
| Physical | Facility Access Controls | 164.310(a) | Contingency Operations (A); Facility Security Plan (A); Access Control & Validation (A); Maintenance Records (A) |
| Physical | Workstation Use | 164.310(b) | (R) |
| Physical | Workstation Security | 164.310(c) | (R) |
| Physical | Device and Media Controls | 164.310(d) | Disposal (R); Media Re-use (R); Accountability (A); Data Backup & Storage (A) |
| Technical | Access Control | 164.312(a) | Unique User Identification (R); Emergency Access Procedure (R); Automatic Logoff (A); Encryption & Decryption (A) |
| Technical | Audit Controls | 164.312(b) | (R) |
| Technical | Integrity | 164.312(c) | Mechanism to Authenticate ePHI (A) |
| Technical | Person or Entity Authentication | 164.312(d) | (R) |
| Technical | Transmission Security | 164.312(e) | Integrity Controls (A); Encryption (A) |

## Subpart D — Breach Notification Rule (§§ 164.400–164.414) — summary

Governs notification when **unsecured PHI** is breached. The device-program hook is **§ 164.410 — Notification by a business associate**: a business associate that discovers a breach must notify the covered entity "without unreasonable delay and in no case later than **60 days** after discovery." "Unsecured PHI" means PHI not rendered unusable/unreadable via an HHS-specified method — i.e., **encryption per the HHS guidance is the safe harbor** that takes a data loss out of breach-notification scope entirely. This is the practical reason a device program encrypts ePHI even where § 164.312 lists encryption as merely "addressable." Not distilled section-by-section here; pull on demand if a breach-response procedure is being authored.

## Subpart E — Privacy Rule (§§ 164.500–164.534) — summary

Governs the **use and disclosure** of PHI (minimum-necessary, permitted purposes, individual rights of access/amendment, notice of privacy practices). Primarily binds the **covered entity's** information practices rather than a device's technical safeguards, so it is the least device-relevant of the three subparts for a manufacturer acting as a business associate. Relevant pointers: § 164.502 (general rules / business-associate disclosures), § 164.514 (de-identification — the Safe Harbor and Expert Determination methods, directly useful when a device program wants its analytics/AI-training data out of HIPAA scope). Not distilled here; pull on demand.

## Pending rulemaking — 2025 Security Rule NPRM `[VERIFY status before relying]`

HHS/OCR published a Notice of Proposed Rulemaking, *"HIPAA Security Rule To Strengthen the Cybersecurity of Electronic Protected Health Information,"* in the **Federal Register on January 6, 2025** — the first major Security Rule overhaul since the 2013 Omnibus Rule. As **proposed** (not final at this distillation's retrieval date), it would:

- **Remove the "addressable" vs. "required" distinction** — making essentially all implementation specifications mandatory (with limited, documented exceptions).
- **Mandate encryption of ePHI** at rest and in transit, and **multi-factor authentication**, as required controls.
- Require **network segmentation, vulnerability scanning (≥ every 6 months), penetration testing (≥ annually)**, an asset inventory and network map, and 72-hour restoration of certain systems.
- Require **annual compliance audits** and written verification of business-associate safeguards.

**Treat this as forward-looking only.** It changes nothing today, but a device program designing a new connected product should design *toward* the proposed controls (encryption + MFA + segmentation are already cybersecurity best practice and align with FDA premarket cybersecurity expectations), so a later final rule is a documentation exercise rather than a redesign.

## Practical Cross-References

| Question | Look here |
|----------|-----------|
| Is my device program in scope for HIPAA at all? | Business-associate analysis — does the SaMD/cloud create/receive/maintain/transmit ePHI for a covered entity? If yes, § 164.314(a) BA-contract flow-down applies. |
| What technical controls must my SaMD/cloud implement? | § 164.312 (access control, audit, integrity, authentication, transmission security) — maps to SRS security requirements |
| How do I operationalize the required risk analysis? | NIST SP 800-66 Rev. 2 — `../industry-frameworks/nist-sp-800-66.md` |
| How does HIPAA relate to my FDA premarket cybersecurity work? | Shared control catalog via NIST CSF / 800-53; IEC 81001-5-1 (`../standards/iec-81001-5-1.md`) data-protection line item; one risk process (ISO 14971) drives both |
| Does encryption let me avoid breach notification? | Yes — Subpart D safe harbor for "unsecured PHI"; encryption per HHS guidance removes a loss from breach scope |
| Can I use ePHI to train/validate AI models? | § 164.514 de-identification (Safe Harbor / Expert Determination) takes data out of HIPAA scope; see also AI-DSF lifecycle guidance |

## Source Provenance

- **eCFR API endpoint**: `https://www.ecfr.gov/api/versioner/v1/full/<date>/title-45.xml?part=164`
- **Retrieval date**: 2026-06-02 (eCFR latest issue date for Title 45: 2026-05-29)
- **Verbatim scope retrieved**: Part 164 Subpart C (§§ 164.302–164.318 + Appendix A)
- **Current text basis**: 2013 Omnibus Rule (78 FR 5566, Jan. 25, 2013), as the most recent finalized amendment to Subpart C. The 2025 Security Rule NPRM (90 FR ___, Jan. 6 2025) is **not** reflected in the verbatim text — it is proposed only.
- **Companion references**: `../industry-frameworks/nist-sp-800-66.md` (Security Rule implementation guide), `../standards/iec-81001-5-1.md` (health-software security; data-protection requirements), `../industry-frameworks/owasp.md` (V8 Data Protection — PHI/PII classification)
- **Project applicability**: lives separately at `docs/external/regulations/hipaa.md` in a consuming project (per the regulations-README "cite both" convention) — how *this* device program decides HIPAA applies to its modules, with `[VERIFY]` markers and a documented business-associate determination.

[VERIFY all clause numbers, R/A markings, and verbatim text against the live eCFR snapshot before relying on this distillation in a regulated submission. VERIFY the 2025 NPRM's status — it may have been finalized, withdrawn, or amended after this retrieval date.]
