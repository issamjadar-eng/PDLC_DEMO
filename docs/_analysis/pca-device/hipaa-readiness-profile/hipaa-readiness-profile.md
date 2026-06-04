---
id: hipaa-readiness-profile
title: HIPAA Readiness Profile — PP3500 System
status: draft                 # draft | review | accepted | superseded
component: pca-device         # system DHF leaf — cross-component / system-level analysis
topic: cybersecurity          # closest topic in the vocabulary; HIPAA = ePHI safeguards (privacy + security)
created: 2026-06-02
last_updated: 2026-06-02
authored_by:
  - human:benxavier-gl
grounded_against:
  - dhf: docs/project/dhfs/pca-device/                                   # system DHF (device + telemetry path)
  - dhf: docs/project/dhfs/cloud-suite/design-controls/                  # ePHI concentration — UN / DI / SRS
  - dhf: docs/project/dhfs/connectivity-adapter/design-controls/         # ePHI-in-transit telemetry transport
  - internal: docs/internal/source-md/software-cybersecurity/cybersecurity-sop.md
  - internal: docs/internal/source-md/software-cybersecurity/threat-modeling-wi.md
  - external: docs/external/regulations/hipaa.md                        # L1b project applicability — §164.312 → SRS mapping
  - external: docs/external/industry-frameworks/nist-sp-800-66.md        # L1b project applicability — implementation method
  - standard: 45 CFR Part 164 (HIPAA Security Rule §§164.308 / .310 / .312 / .314 / .316) — .claude/skills/medtech-docs/references/regulations/45-cfr-part-164.md
  - framework: NIST SP 800-66 Rev. 2 (HIPAA Security Rule implementation) — .claude/skills/medtech-docs/references/industry-frameworks/nist-sp-800-66.md
  - submissions: docs/project/submissions/
recommended_agents:
  - cybersecurity           # primary
  - risk-management         # consulting
  - regulatory-affairs      # consulting
superseded_by: null
---

# HIPAA Readiness Profile — PP3500 System

_Demo sample data — not for clinical use._

> **What this is.** A system-level readiness assessment of whether the PP3500 program's design-control artifacts demonstrate conformance to the **HIPAA Security Rule (45 CFR Part 164, Subpart C)** safeguards for electronic protected health information (ePHI) flowing through the device → connectivity-adapter → cloud-suite data path. This is a *content-gap* analysis: it asks whether the project's own work product (user needs, design inputs, software requirements, cybersecurity procedures) already carries the safeguard obligations HIPAA requires — not whether the folder structure is correct (`/best-practices`) or whether documents are present (`/dhf-manifest`).

## Goal of this analysis

Assess the PP3500 program's **HIPAA readiness posture across the whole ePHI data path** and surface where safeguard obligations are (a) explicitly carried in design-control artifacts with traceable evidence, (b) implied but not yet specified, or (c) absent. The PP3500 is a connected PCA pump whose telemetry and cloud platform store and transmit ePHI; the HIPAA Security Rule is therefore load-bearing for the cloud-suite and connectivity-adapter modules and relevant to the device's telemetry origination.

- **Motivating question:** _"Does the project's design-control content demonstrate that each required HIPAA Security Rule safeguard (administrative §164.308, physical §164.310, technical §164.312, organizational §164.314, documentation §164.316) is specified and traceable for ePHI across device → adapter → cloud — or are there readiness gaps a HIPAA risk assessment (required by §164.308(a)(1)(ii)(A)) would flag?"_
- **Decision the analysis informs:** _whether to open targeted design-input / SRS additions (or a dedicated HIPAA security risk assessment artifact) before a customer security review or a hospital procurement due-diligence, and whether the regulatory strategy needs a privacy/security-posture section._
- **Stakeholders:** cybersecurity lead, regulatory affairs, risk management, cloud-suite R&D, program management; downstream: hospital CISO/DPO procurement reviewers (the external audience for this readiness statement).

## Source being analyzed

_Grounded against the artifacts below. Cited by path; source content is not duplicated here._

### Primary sources (project work product under analysis)

- `docs/project/dhfs/cloud-suite/design-controls/user-needs/user-needs.md` — Privacy (PRIV) + Cybersecurity (CYBR) user needs; specifically **UN-002** (P1, tenant isolation, cites §164.312(a)), **UN-010** (P3, point-in-time restore ≤24h, cites contingency §164.308(a)(7)), **UN-011** (P4, tamper-evident audit log ≥7yr, cites §164.312(b)), **UN-015** (P5, region-loss RPO 15min/RTO 8h, cites §164.308(a)(7)), **UN-021** (P7, per-tenant retention + cryptographic purge, cites §164.530(j)).
- `docs/project/dhfs/cloud-suite/design-controls/requirements/design-inputs.md` — Privacy (PRIV) + security design inputs derived from the above.
- `docs/project/dhfs/cloud-suite/design-controls/requirements/software-requirements.md` — SRS rows that should carry the testable safeguard specifications.
- `docs/project/dhfs/connectivity-adapter/design-controls/` — ePHI-in-transit (telemetry transport) user needs / design inputs / SRS.
- `docs/project/dhfs/pca-device/design-controls/` — device-side telemetry origination (where ePHI enters the path).
- `docs/internal/source-md/software-cybersecurity/cybersecurity-sop.md` + `threat-modeling-wi.md` — the QMS cybersecurity process the safeguards should hook into.

### Reference standards / external

- **45 CFR Part 164, Subpart C — HIPAA Security Rule.** Administrative safeguards §164.308 (incl. (a)(1)(ii)(A) risk analysis, (a)(4) access management, (a)(7) contingency plan); Physical safeguards §164.310; Technical safeguards §164.312 (access control (a)(1) incl. encryption (a)(2)(iv) [addressable], audit controls (b), integrity (c), person/entity authentication (d), transmission security (e) incl. encryption (e)(2)(ii) [addressable]); Organizational §164.314 (Business Associate contracts); Documentation §164.316. Registry distillation: `.claude/skills/medtech-docs/references/regulations/45-cfr-part-164.md`.
- **NIST SP 800-66 Rev. 2** — HIPAA Security Rule implementation guidance + Security-Rule → CSF/800-53 crosswalk. Registry distillation: `.claude/skills/medtech-docs/references/industry-frameworks/nist-sp-800-66.md`.
- **HIPAA Privacy Rule** cross-refs cited by project user needs: §164.524 (Right of Access), §164.530(j) (documentation/retention).

### Related context

- **L1b project applicability (now present):** `docs/external/regulations/hipaa.md` (authored under task `ben/076`) maps the §164.312 technical safeguards to ePHI-handling modules + SRS rows and carries `[VERIFY]` flags for the open obligations (emergency access, automatic logoff, HIPAA risk analysis, BAA posture, breach procedure, pca-device-local ePHI determination). This analysis grounds against it directly and the fan-out below corroborates / extends its mapping. _(Earlier draft incorrectly noted this file as absent — corrected 2026-06-02.)_
- Regulatory strategy at `docs/project/strategies/regulatory-strategy.md` — check whether a HIPAA/privacy posture section exists.
- Predicate analysis under `docs/project/input-analysis/predicate-analysis/` — predicate connectivity posture for comparison.

## Assertions

_Each assertion is a falsifiable claim about the project artifacts, keyed to a HIPAA Security Rule safeguard. The fan-out advisors confirm / refute / extend each with evidence (source path + the specific data point) and the standard clause._

| # | Assertion | Safeguard (clause) | Evidence (path / data point) | Status |
|---|-----------|--------------------|------------------------------|--------|
| A1 | Logical tenant isolation of ePHI (no cross-tenant read/enumerate) is carried from user need → design input → a testable software requirement. | Technical · Access Control §164.312(a)(1) | `cloud-suite/.../user-needs.md` UN-002 (P1); trace into `design-inputs.md` + `software-requirements.md` | **confirmed** (F-1) |
| A2 | A tamper-evident audit log of all ePHI read/write/admin actions, retained ≥ 6 years, is specified with an integrity (tamper-evidence) mechanism in the SRS. | Technical · Audit Controls §164.312(b); Documentation retention §164.316(b)(2)(i) | `cloud-suite/.../user-needs.md` UN-011 (P4, ≥7yr); trace into SRS | **confirmed** (F-1) |
| A3 | ePHI integrity protection against improper alteration/destruction — including deterministic end-of-retention purge with cryptographic evidence — is specified. | Technical · Integrity §164.312(c)(1) | UN-021 (P7, cryptographic purge); trace into DI + SRS | **confirmed** (F-1) |
| A4 | ePHI transmitted device → adapter → cloud is encrypted in transit (e.g. TLS) with a corresponding design input on the connectivity-adapter path. | Technical · Transmission Security §164.312(e)(1) (encryption (e)(2)(ii) addressable) | `connectivity-adapter/design-controls/` telemetry transport DI/SRS | **confirmed** (F-1) |
| A5 | ePHI at rest in cloud-suite stores is encrypted, with the addressable-implementation decision documented (implement or document-why-not). | Technical · Access Control — Encryption §164.312(a)(2)(iv) (addressable) | `cloud-suite/.../software-requirements.md` — encryption-at-rest SRS row | **confirmed** — addressable rationale gap (F-2) |
| A6 | Data backup + disaster recovery with measurable objectives (point-in-time restore, RPO/RTO) are specified for ePHI. | Administrative · Contingency Plan §164.308(a)(7)(ii)(A)-(C) | UN-010 (restore ≤24h), UN-015 (RPO 15min / RTO 8h); trace into SRS | **confirmed** (F-5) |
| A7 | Role-based / minimum-necessary access control over ePHI is specified (authorization + access establishment/modification). | Administrative · Information Access Management §164.308(a)(4); Technical · Authentication §164.312(d) | `cloud-suite/design-controls/` access-control UN/DI/SRS | **confirmed** (F-5) |
| A8 | A HIPAA security risk analysis + risk management process is present (or explicitly hooked into the existing cybersecurity SOP / threat model), as §164.308(a)(1) requires. | Administrative · Security Management §164.308(a)(1)(ii)(A)-(B) | `cybersecurity-sop.md` + `threat-modeling-wi.md` — does either scope ePHI/HIPAA explicitly? | **partial** — no HIPAA-framed risk analysis (F-4) |
| A9 | Per-tenant configurable PHI retention (default ≥6yr) and a data-subject Right-of-Access/export capability are specified. | Documentation/retention §164.316(b)(2); Privacy §164.524 / §164.530(j) | UN-021 (retention), P7 (Right of Access); trace into DI/SRS | **partial** — right-of-access only GDPR-framed (F-5) |
| A10 | Business Associate Agreement posture for cloud sub-processors (the cloud-suite runs on third-party infrastructure) is addressed in a regulatory/quality artifact. | Organizational · BA Contracts §164.314(a); §164.308(b) | `docs/project/strategies/regulatory-strategy.md` / submissions — any BAA mention? | **refuted** — no BAA posture in any project artifact (F-6) |
| A11 | A documented breach-response procedure (BA→covered-entity, ≤60-day clock) and a security-incident response/reporting procedure exist. | Breach Notification §164.410 (R); Security Incident Procedures §164.308(a)(6) (R) | Grep `submissions/` + `strategies/` — no breach/notification procedure; `hipaa.md` §4/§6 item 6 | **refuted** — Subpart D / incident response wholly unowned (F-8) |
| A12 | Physical device/media controls for pca-device-local ePHI (sanitization on disposal/RMA) are determined and, if applicable, specified + labeled. | Physical · Device & Media Controls §164.310(d) (R) | `hipaa.md` §2 / §6 item 3 `[VERIFY]` pump-firmware local ePHI; `composition-manifest.md:52` (21 CFR 801 labeling) | **partial / [VERIFY]** — determination open (F-10) |

## Assertion positions

_Per-advisor stance on each assertion (Positive = advisor judges the safeguard satisfied / traced; Negative = a real gap / absent; Neutral = partial / addressable-rationale-or-determination open / depends). Rendered as the click-to-expand detail behind each assertion in the project-console. Distilled from the three advisors' full responses (`recs-*.md`) in this folder._

### A1
- positive — cybersecurity: tenant isolation traced UN-002→DI→SRS (SW-002 + CI probe SW-024)
- neutral — risk-management: traced; the confidentiality-breach safety tail is unrepresented in the hazard file

### A2
- positive — cybersecurity: tamper-evident audit log SW-011 (≥7yr) also satisfies §164.316 retention
- neutral — risk-management: audit strong; repudiation/integrity harms not promoted to a hazard row

### A3
- positive — cybersecurity: integrity + cryptographic end-of-retention purge specified (SW-011 / SW-021)
- neutral — risk-management: controls present; the HARM-DPS-002 corruption→clinical-decision chain has no hazard row

### A4
- positive — cybersecurity: ePHI encrypted in transit — mTLS 1.3 (CA SW-018 + cloud ingest SW-005)
- neutral — risk-management: transit encryption traced; the telemetry-corruption safety tail is un-evaluated

### A5
- neutral — cybersecurity: AES-256-GCM BYOK implemented (exceeds), but the §164.306(d)(3) addressable decision is not recorded as such
- neutral — risk-management: the addressable encrypt-or-document decision is an unrecorded ALARP trade

### A6
- positive — cybersecurity: backup/DR with measurable RPO/RTO reach testable SRS rows (UN-010/UN-015)
- positive — risk-management: contingency/DR specified — though availability-during-use still needs a hazard row

### A7
- positive — cybersecurity: RBAC + federated authentication specified and verifiable
- neutral — risk-management: RBAC specified; the unauthorized-control HARM-DPS-004 (S4) chain is unrepresented

### A8
- negative — cybersecurity: no HIPAA-framed §164.308(a)(1) risk analysis; STRIDE threat model only, HIPAA as a bare responsibility row
- neutral — regulatory-affairs: the Required risk analysis is implied via the threat model, not documented as such
- neutral — risk-management: must reconcile with ISO 14971 — name which governs residual-risk acceptability

### A9
- neutral — cybersecurity: retention solid; §164.524 Right-of-Access only GDPR-framed, no HIPAA mapping note
- neutral — regulatory-affairs: right-of-access carried only as a GDPR DSR capability

### A10
- negative — cybersecurity: no BAA posture in any project work-product (zero §164.314 hits in strategy/submissions)
- negative — regulatory-affairs: BA determination unanchored to the device-class interaction; "not a device" ≠ "out of HIPAA"

### A11
- negative — regulatory-affairs: Subpart D §164.410 (≤60-day clock) + §164.308(a)(6) incident response wholly unowned
- negative — risk-management: breach/incident response carries no safety-tail residual evaluation

### A12
- neutral — regulatory-affairs: §164.310(d) local-ePHI determination open [VERIFY]; the 21 CFR 801 labeling consequence is unresolved
- neutral — risk-management: pca-device-local-ePHI determination gates the device-tier DPS harms

## Findings

_Populated by the fan-out advisors (cybersecurity primary; risk-management + regulatory-affairs consulting). Each finding: stable F-N id, author, evidence pointer, impact, resolution. Append-only — advisors add findings here; human author owns disposition._

### F-1: Core §164.312 technical-safeguard chain (tenant isolation, audit, integrity, transit, at-rest) is fully traced UN→DI→SRS

- **Author:** agent:cybersecurity
- **What:** A1–A5 each have a complete, testable chain reaching a verifiable SRS row with a named verification method — not stopping at the user-need or design-input layer.
- **Evidence:**
  - A1 — `cloud-suite/.../user-needs.md` UN-002 → `design-inputs.md` DI-002 → `software-requirements.md` SW-002 (tenant-claim authz middleware, rejects cross-tenant) + SW-024 (CI cross-tenant probe). §164.312(a)(1). Verification VER-CLOUD-ST-002.
  - A2 — UN-011 → DI-011 → SW-011 (tamper-evident hash-chained log ≥7yr). §164.312(b) + §164.316(b)(2)(i).
  - A3 — UN-021 → DI-021 → SW-021 (deterministic purge w/ cryptographic evidence). §164.312(c)(1).
  - A4 — `connectivity-adapter/.../design-inputs.md` DI-017 → SW-018 (mTLS 1.3, X.509) + cloud SW-005 (mTLS ingest). §164.312(e)(1).
  - A5 — DI-009 → SW-009 (AES-256-GCM at rest, BYOK). §164.312(a)(2)(iv) addressable.
- **Impact:**
  - _Regulatory:_ The load-bearing §164.312 technical safeguards are specified with named security tests — submission/procurement-defensible.
  - _Safety:_ n/a.
  - _Filing:_ Strengthens the K210345 cybersecurity posture narrative and a hospital-CISO procurement package.
- **Resolution proposal:** No SRS change. Mark A1–A5 confirmed; cite the L1b mapping at `docs/external/regulations/hipaa.md` §3 rather than re-deriving the trace.
- **Owner / next step:** Cybersecurity lead — fold into the readiness statement; no engineering action.

### F-2: §164.312(a)(2)(iv) at-rest encryption is implemented but the "addressable" decision rationale is not recorded as such

- **Author:** agent:cybersecurity
- **What:** A5 is technically satisfied (SW-009), but §164.306(d)(3) requires the addressable-implementation *decision* to be documented. No artifact records the addressable-spec rationale; the same applies to transmission encryption §164.312(e)(2)(ii) and integrity controls (e)(2)(i) — implemented (SW-005/SW-018) but not framed as addressable determinations.
- **Evidence:** Control present: `cloud-suite/.../software-requirements.md` SW-009. Framework: `45-cfr-part-164.md` §164.306(d)(3); §164.312(a)(2)(iv) marked **(A)** in Appendix A. L1b `docs/external/regulations/hipaa.md` §3 marks it "✅ Covered (exceeds — BYOK)" but carries no recorded addressable-decision rationale.
- **Impact:**
  - _Regulatory:_ Low — controls exist and exceed the bar; the gap is documenting *why* each addressable spec was implemented. An OCR-style review or hospital security questionnaire expects the addressable analysis on record.
  - _Safety:_ n/a.
  - _Filing:_ Minor; closes inside the HIPAA risk-analysis artifact (F-4).
- **Resolution proposal:** Add an "addressable implementation specification determinations" table to the HIPAA security risk analysis (or `hipaa.md` §3): per addressable spec, the decision (implement / equivalent / N/A-with-rationale) and the implementing SRS row. No new SRS row.
- **Owner / next step:** Cybersecurity lead + Privacy/Regulatory — author alongside F-4 before the next customer security review.

### F-3: Two §164.312(a) access-control sub-specs have NO SRS row — emergency access (Required) and automatic logoff (Addressable)

- **Author:** agent:cybersecurity
- **What:** **§164.312(a)(2)(ii) Emergency access procedure (Required)** and **(a)(2)(iii) Automatic logoff (Addressable)** have no requirement in the cloud-suite or connectivity-adapter SRS. Confirmed by grep — no break-glass / emergency-access row and no session-inactivity / auto-logoff row anywhere.
- **Evidence:** Searched `cloud-suite/.../software-requirements.md` + `connectivity-adapter/.../software-requirements.md` — zero matches for emergency-access / break-glass / inactivity / auto-logoff. P1 rows (SW-001..004, 024, 025) and CA A6 (SW-016..018) cover federation/authz/identity/mTLS — none covers these two specs. Clause: `45-cfr-part-164.md` §164.312(a)(2)(ii) **(R)** / (a)(2)(iii) **(A)**; already flagged in `hipaa.md` §3 + §6 items 1–2.
- **Impact:**
  - _Regulatory:_ Emergency access is a **Required** spec — its absence is the kind of finding OCR enforcement cites. Automatic logoff is addressable but unaddressed (neither implemented nor documented-why-not).
  - _Safety:_ n/a directly (platform performs no clinical decisioning).
  - _Filing:_ A reviewable gap a hospital CISO questionnaire will surface.
- **Resolution proposal:** Add two SRS rows to cloud-suite P1 (mirror auto-logoff on the connectivity-adapter operator console): an audited break-glass/emergency-access procedure (or documented N/A rationale), and session-inactivity auto-logout with a defined timeout. Trace each to a new DI row.
- **Owner / next step:** Cloud-suite R&D + Cybersecurity lead — open the SRS/DI rows next requirements increment.

### F-4: §164.308(a)(1)(ii)(A) Required HIPAA risk analysis is not explicitly scoped into the cybersecurity SOP or threat-model WI — the keystone Required spec is implied, not specified

- **Author:** agent:cybersecurity
- **What:** A8 is only partially satisfied. The cybersecurity SOP + threat-modeling WI run a STRIDE security-risk process, but neither scopes ePHI or frames its output as the HIPAA §164.308(a)(1)(ii)(A) risk analysis, and no HIPAA-framed risk-analysis artifact / requirement to produce one exists.
- **Evidence:** `cybersecurity-sop.md` line 70 (HIPAA as a responsibility-row only), line 108 (HIPAA among regulatory inputs); no ePHI risk-analysis deliverable in §7 Records. `threat-modeling-wi.md` §4.1 asset inventory includes "Patient data — PHI" (ePHI is in scope) but never maps to Security-Rule safeguards; harm anchor is the safety Master Harms List, not ePHI confidentiality. Clause: `45-cfr-part-164.md` §164.308(a)(1)(ii)(A) **(R)**; `hipaa.md` §4/§6 item 4 marks this **[VERIFY]**.
- **Impact:**
  - _Regulatory:_ Highest-leverage gap in this pass — the Required keystone spec. The threat model is a strong foundation, but a HIPAA risk analysis is a distinct documented view (NIST SP 800-66 method), retained 6 years (§164.316(b)(2)(i)).
  - _Safety:_ n/a.
  - _Filing:_ Directly relevant to a Q-Sub cybersecurity discussion and hospital BA due-diligence.
- **Resolution proposal:** Author a HIPAA Security Risk Analysis artifact under cloud-suite design-controls (or as a cross-component cybersecurity-file deliverable), hooked into the threat-model output, structured per NIST SP 800-66 Rev. 2; amend the cybersecurity SOP §7 Records to list it. Use `hipaa.md` §3 as the safeguard→SRS scaffold.
- **Owner / next step:** Cybersecurity lead + Privacy/Regulatory — gate before the next customer security review (the analysis's stated decision driver).

### F-5: Contingency-plan and RBAC/authentication safeguards (A6, A7, A9) reach testable SRS rows

- **Author:** agent:cybersecurity
- **What:** A6 (backup/DR), A7 (RBAC + authentication), A9 (retention) all reach verifiable SRS rows, crossing administrative §164.308 into concrete technical implementation. (A9 right-of-access caveat below.)
- **Evidence:** A6 — UN-010/015 → DI-010/015 → SW-010 (PITR ≤35d/≤24h), SW-015 (RPO ≤15min / RTO ≤8h), SW-016 (quarterly chaos). §164.308(a)(7). A7 — DI-001/002/003 → SW-001 (federated IdP, no local accounts), SW-002 (tenant authz), SW-003 (self-service RBAC) + CA SW-026. §164.308(a)(4) + §164.312(d). A9 — UN-021 → DI-021 → SW-021 ("minimum 6 years for HIPAA-covered records"), SW-030 retention editor.
- **Impact:**
  - _Regulatory:_ Confirms contingency-plan Required specs and access-management are specified and verifiable.
  - _Safety:_ n/a.
  - _Filing:_ Supports the readiness statement.
- **Resolution proposal:** Mark A6, A7 confirmed; A9 partially-confirmed — retention solid, but HIPAA §164.524 Right-of-Access is implemented only via a GDPR-framed DSR API (SW-020 + SW-023). Add a one-line HIPAA §164.524 mapping note.
- **Owner / next step:** Cybersecurity lead — disposition in the readiness statement; optional §164.524 mapping note for Privacy/Regulatory.

### F-6: Organizational §164.314(a) BAA posture is absent from project work-product artifacts

- **Author:** agent:cybersecurity
- **What:** A10 refuted as specified-in-a-DHF-artifact: no business-associate / BAA / §164.314(a) content in the regulatory strategy or submissions. The obligation lives only in external/registry files.
- **Evidence:** Grepped `docs/project/strategies/regulatory-strategy.md` + `docs/project/submissions/` — zero "business associate"/"BAA"/"164.314" hits (strategy only states "privacy still applies", lines 81/106). Project-wide, BAA appears only in the analysis + external/registry files. `hipaa.md` §1 ("business associate: Yes [VERIFY against signed BAAs]"), §4 row §164.314(a), §6 item 5. Clause: `45-cfr-part-164.md` §164.314(a) / §164.308(b) **(R)**.
- **Impact:**
  - _Regulatory:_ BA-contract flow-down to cloud sub-processors (§164.308(b)) is a Required organizational safeguard with no home in a regulatory/quality artifact — material for a multi-tenant cloud on third-party IaaS.
  - _Safety:_ n/a.
  - _Filing:_ Operational/procurement-facing; a hospital BA due-diligence will demand it.
- **Resolution proposal:** Add a privacy/security-posture section to `docs/project/strategies/regulatory-strategy.md` covering the business-associate determination + BAA / subcontractor flow-down, referencing `hipaa.md`.
- **Owner / next step:** Regulatory Affairs (BAA posture) — before customer procurement due-diligence.

### F-7: HIPAA readiness audience is unstated — risk of conflating HHS/OCR market-access posture with FDA filing evidence

- **Author:** agent:regulatory-affairs
- **What:** HIPAA (HHS/OCR + hospital procurement) and FDA premarket cybersecurity (§524B) are distinct audiences with no overlap of obligation — HIPAA Security-Rule conformance is **not** a 510(k) acceptance criterion. The project's structural separation is actually correct (the 510(k) manifest carries §524B + 21 CFR 801, no HIPAA), but that correctness is accidental, not stated; this analysis's own framing (F-1/F-4 calling the §164.312 chain "Q-Sub-relevant") risks the inverse conflation.
- **Evidence:**
  - `docs/project/submissions/510k/composition-manifest.md:50,52` — FDA package = `§524B` cybersecurity + `21 CFR 801` labeling; zero HIPAA/§164/BAA rollup.
  - `docs/external/regulations/hipaa.md` §1 — manufacturer is **business associate, not covered entity**; obligation arrives by **contract** (§164.314 / §164.308(b)), not FDA mandate.
  - This file's Open Questions already asks whether HIPAA evidence is filed with FDA — genuinely undecided in-doc.
- **Impact:**
  - _Regulatory:_ Conflation wastes Q-Sub airtime on conformance FDA doesn't review, OR treats HIPAA gaps (F-3/F-4/F-6) as filing blockers when they don't gate K-clearance.
  - _Safety:_ n/a.
  - _Filing:_ HIPAA conformance is not a 510(k) deficiency surface; mis-routing inflates the filing + PCCP change envelope.
- **Resolution proposal:** Add an explicit "audience routing" statement (here + the planned regulatory-strategy privacy section): HIPAA findings → procurement/BA-contract + operational QMS owners; §524B cybersecurity findings → FDA submission. Shared evidence (threat model, encryption SRS) is *referenced*, not *re-submitted*, across audiences.
- **Owner / next step:** Regulatory Affairs — resolve the audience split before issuing the readiness statement to any hospital CISO.

### F-8: Breach Notification Rule (Subpart D §164.400–414) + §164.308(a)(6) incident response have no home in any project artifact

- **Author:** agent:regulatory-affairs
- **What:** A1–A10 / F-1…F-6 cover Subpart C; **Subpart D breach notification is neither an assertion nor a finding**. As a business associate the manufacturer owes the §164.410 BA→covered-entity breach report within ≤60 days of discovery — a Required obligation with a hard clock that no DHF/SOP/strategy/submission proceduralizes. The Security Rule's own §164.308(a)(6) incident-response (Required) is likewise unmapped.
- **Evidence:**
  - Grep of `docs/project/submissions/` + `strategies/` — no breach/§164.410/notification procedure (only an unrelated "breach" security-control term in pca-device SRS + tracker JSON strings).
  - `docs/external/regulations/hipaa.md` §4 (`§164.410 … [VERIFY] documented breach-response procedure with the ≤60-day BA clock`) + §6 item 6.
  - `45-cfr-part-164.md` §164.410 (≤60-day BA clock; encryption = "unsecured PHI" safe harbor) + §164.308(a)(6) Response/Reporting **(R)**.
- **Impact:**
  - _Regulatory:_ A Required Subpart D obligation with a statutory clock is wholly unowned; §164.308(a)(6) incident response is a parallel unprobed gap.
  - _Safety:_ n/a (but a breach of therapy-event ePHI is a postmarket/complaint-handling trigger).
  - _Filing:_ Not FDA — a BA-contract + operational-SOP item a hospital BA due-diligence will demand.
- **Resolution proposal:** (1) Add assertion **A11** (Subpart D §164.410 + §164.308(a)(6)), disposition refuted/absent. (2) Author a breach-response procedure (or extend the cybersecurity / postmarket complaint-handling SOP) carrying the ≤60-day clock + the encryption safe-harbor analysis (SW-009 AES-256-GCM as the documented mitigant).
- **Owner / next step:** Regulatory Affairs + Cybersecurity + Postmarket — proceduralize before any BAA is executed (the BAA contractually triggers the clock on signature).

### F-9: Regulatory strategy needs a privacy/security-posture section anchoring the BA determination to the classification interaction

- **Author:** agent:regulatory-affairs
- **What:** Extends F-6: the BA determination is module-specific and turns on the existing component classification. The strategy classifies cloud-suite "all other apps" as **non-medical-device software** and the connectivity-adapter as **MDDS (non-device)** — yet both handle ePHI, so HIPAA business-associate status attaches **regardless of FDA device classification**. "Not an FDA device" ≠ "not a HIPAA business associate." The two bare "privacy still applies" lines don't capture this; §164.308(b) flow-down also reaches the third-party IaaS.
- **Evidence:**
  - `docs/project/strategies/regulatory-strategy.md:79,81,106` — Connectivity Adapter = MDDS (non-device); Cloud Suite "all other apps" = non-medical-device, "privacy still applies" (bare, no BA determination / flow-down).
  - `docs/external/regulations/hipaa.md` §1 — multi-tenant cloud creating/receiving ePHI on behalf of hospitals is "the textbook business-associate relationship"; §164.308(b) flow-down to "cloud IaaS, observability sinks."
  - `45-cfr-part-164.md` — BA status triggers the moment a component transmits ePHI, **independent of FDA device classification**.
- **Impact:**
  - _Regulatory:_ Without stating the device-class-vs-ePHI decoupling, the strategy invites the reader to assume non-device/MDDS components are out of HIPAA scope — they are not.
  - _Safety:_ n/a.
  - _Filing:_ Doesn't affect the 510(k); it's the artifact a hospital procurement/BA negotiation reads first.
- **Resolution proposal:** Add a "Privacy & Security Posture (HIPAA)" section to `regulatory-strategy.md`: (a) covered-entity = No, business-associate = Yes; (b) the explicit decoupling (BA status attaches to MDDS + non-device ePHI components regardless of FDA class); (c) §164.314(a) BAA-per-tenant + §164.308(b) IaaS flow-down; (d) pointer to `hipaa.md`. One section closes both F-6 and F-9.
- **Owner / next step:** Regulatory Affairs — author alongside the F-6 resolution.

### F-10: pca-device-local ePHI determination drives §164.310(d) physical safeguards + labeling (sanitization) — currently an unresolved [VERIFY]

- **Author:** agent:regulatory-affairs
- **What:** The one HIPAA thread that can legitimately touch an FDA artifact (labeling). Whether the pump firmware stores patient-identifiable events locally is an open `[VERIFY]`; if Yes, §164.310(d) **Device & media controls — Disposal (R) / Media re-use (R)** attach to pump *hardware*, with a sanitization-on-disposal/RMA labeling consequence under 21 CFR 801. Privacy is **not** an indication-for-use, but any encryption-safe-harbor claim (F-8) must be consistent wherever it appears.
- **Evidence:**
  - `docs/external/regulations/hipaa.md` §2 + §6 item 3 — "pca-device (pump firmware) — local event logs. **[VERIFY]** whether locally-stored events are patient-identifiable ePHI; if so, §164.310(d) … attach to pump hardware."
  - `45-cfr-part-164.md` §164.310(d) Disposal **(R)** / Media re-use **(R)** — manufacturer servicing/RMA/EOL processes must enforce them.
  - `composition-manifest.md:52` — Labeling under 21 CFR 801 is in the filing (where sanitization guidance would land). A1–A10 never asserts the §164.310 physical-safeguard determination.
- **Impact:**
  - _Regulatory:_ An unresolved Required physical-safeguard scope question with no assertion row.
  - _Safety:_ n/a.
  - _Filing:_ The only HIPAA-adjacent item that can legitimately reach FDA labeling (servicing/disposal instructions).
- **Resolution proposal:** Resolve the `hipaa.md` §6 item-3 `[VERIFY]` with a pca-device R&D determination. If Yes: add an SRS/DI sanitization requirement + service-manual/IFU sanitization instruction (21 CFR 801) + assertion **A12** for §164.310(d). If No: document the N/A rationale. Keep privacy out of indications-for-use.
- **Owner / next step:** Regulatory Affairs + pca-device R&D — close before finalizing 510(k) labeling.

### F-11: The ePHI/telemetry security-risk → patient-safety bridge exists as QMS machinery but is uninstantiated — device hazard analyses + threat models are empty stubs

- **Author:** agent:risk-management
- **What:** The IEC 81001-5-1 → ISO 14971 bridge F-4 assumes is operating is not yet wired. The QMS provides the machinery, but no project hazard analysis instantiates it — so no confidentiality/integrity/availability compromise of ePHI or telemetry is currently represented as a *safety hazard* in the PP3500 risk file. The threat models and hazard analyses are v0.1 DRAFT placeholder stubs, so neither the ePHI-confidentiality harm **nor** the telemetry-corruption→clinical-decision safety harm is captured anywhere. (This is the safety dimension every F-1…F-6 finding marked "n/a".)
- **Evidence:**
  - `docs/internal/source-md/risk-management/master-harms-list.md` §3.8 — `HARM-DPS-001` PHI exposure (S3), `HARM-DPS-002` "PHI corruption … up to 4 if affects clinical decision", `HARM-DPS-003` "Loss of device availability during use (S4)", `HARM-DPS-004` unauthorized device control (S4). Security→safety escalation pre-baked into the harm taxonomy.
  - `cybersecurity-plan.md` §3 / `cybersecurity-sop.md` §6.4 — explicit rule: "if a cyber risk can lead to patient harm, it is tracked as a safety hazard"; threat-model outputs feed Hazard Analysis (IEC 81001-5-1 §5).
  - `docs/project/dhfs/{pca-device,cloud-suite,connectivity-adapter}/risk-management/GL-TMP-RM-003-hazard-analysis.md` — Rev 0.1 DRAFT, empty worksheet rows. `pca-device/cybersecurity/GL-TMP-SW-002-threat-model.md` — Rev 0.1 DRAFT, `{{}}` placeholders; no `HARM-`/telemetry/patient anchoring.
- **Impact:**
  - _Regulatory:_ IEC 81001-5-1 §5 requires security risk cross-referenced into the ISO 14971 file where patient-safety impact is possible; that cross-reference is unpopulated.
  - _Safety:_ The material safety gap the cybersecurity pass didn't reach — CIA compromise of telemetry/ePHI can escalate to patient harm (HARM-DPS-002/003) and has no row in any risk file.
  - _Filing:_ A reviewer expects the threat-model→hazard-analysis linkage demonstrated, not templated.
- **Resolution proposal:** Populate the three hazard analyses with DPS-class chains: (a) telemetry integrity loss → wrong clinical decision (HARM-DPS-002, S≤4), (b) telemetry/remote-monitoring availability loss during use (HARM-DPS-003, S4), (c) ePHI confidentiality exposure (HARM-DPS-001, S3). Each with cyber control (cross-ref'd from threat model/SRS), residual S×P, acceptance per GL-STD-RM-001.
- **Owner / next step:** Risk Manager + Cybersecurity Lead — populate before the threat models leave v0.1; same milestone as F-4.

### F-12: Two parallel risk-evaluation processes (HIPAA §164.308(a)(1) vs ISO 14971) risk divergence — no reconciliation rule names which governs residual-risk acceptability

- **Author:** agent:risk-management
- **What:** The program is about to stand up a HIPAA risk analysis (F-4) while already owning an ISO 14971 risk file, with no stated reconciliation. The HIPAA registry distillation explicitly invites routing both through one risk engine, but the durable artifact that would record this — `risk-strategy.md` — is an unassembled stub. The two processes use different severity/probability bases, so without a precedence rule they can produce divergent residual-risk verdicts on the same threat.
- **Evidence:**
  - `docs/project/strategies/risk-strategy.md:3–17,24–29` — "awaiting its first assembly"; "What Belongs Here" names "How cybersecurity risk (IEC 81001-5-1) feeds into overall risk" + "Risk/benefit determination approach" — both unwritten. "Plans This Informs" names a Risk-Benefit Report that doesn't exist.
  - `45-cfr-part-164.md` §164.306 — a program running ISO 14971 + a cyber threat model "can route Security Rule compliance through the same risk machinery rather than standing up a parallel process."
  - `cybersecurity-plan.md` §3 — names "Inputs from Risk Management Plan (GL-TMP-RM-001)"; no Risk Management Plan instance exists under any DHF.
- **Impact:**
  - _Regulatory:_ Divergent HIPAA vs 14971 conclusions on the same threat is an audit-exposable inconsistency; OCR cites inadequate risk analysis as the modal finding.
  - _Safety:_ ISO 14971 must remain authority for any threat with a patient-harm tail; the HIPAA analysis cannot down-rate a 14971-unacceptable residual. That precedence is unwritten.
  - _Filing:_ Naming ISO 14971 as governing authority is a one-paragraph decision preventing a divergent-record finding.
- **Resolution proposal:** Add a reconciliation paragraph to `risk-strategy.md` before authoring the F-4 artifact: ISO 14971 is the single residual-risk authority; the §164.308(a)(1) HIPAA analysis is a confidentiality/availability-scoped input whose patient-harm items promote into the 14971 hazard analysis; no HIPAA-side acceptance overrides a 14971 unacceptable verdict.
- **Owner / next step:** Risk Manager + Cybersecurity + Privacy/Regulatory — author the precedence rule ahead of the F-4 artifact.

### F-13: Emergency-access (F-3) is an availability gap with a residual-risk tail, not only a §164.312(a)(2)(ii) compliance gap

- **Author:** agent:risk-management
- **What:** Emergency access is an *availability* control whose absence has a residual-risk consequence: clinicians unable to reach ePHI/telemetry during an auth outage / break-glass scenario is an instance of HARM-DPS-003 ("Loss of device availability during use," S4). The F-3 remediation should not close purely as a checkbox SRS row — the availability-loss scenario should appear as a hazard with a residual-risk evaluation justifying the chosen control (break-glass vs documented N/A).
- **Evidence:**
  - `45-cfr-part-164.md` §164.312(a)(2)(ii) — Emergency access procedure (Required): "obtaining necessary ePHI during an emergency."
  - `master-harms-list.md` §3.8 HARM-DPS-003 — availability loss during use, default S4, mapped to clinical harm via the disrupted function.
  - F-3 confirms no emergency-access SRS row; the hazard view of that absence is unrepresented (the empty stubs of F-11).
- **Impact:**
  - _Regulatory:_ Aligns the F-3 remediation with §164.306(b)(2)(iv) risk-based control selection.
  - _Safety:_ A clinician locked out of remote PCA-pump monitoring during an availability incident is a credible S4 chain for an opioid-delivering pump — emergency access is a safety control, not only a privacy control.
  - _Filing:_ Gives the F-3 SRS row a harm anchor satisfying trace-to-risk-control expectations.
- **Resolution proposal:** When the F-3 SRS row is opened, also add the HARM-DPS-003 availability hazard row to the cloud-suite/connectivity-adapter hazard analysis, with emergency-access as its control and residual evaluated per GL-STD-RM-001. Use "documented N/A" only if residual is shown acceptable without it.
- **Owner / next step:** Risk Manager + Cloud-suite R&D + Cybersecurity — same increment as F-3.

### F-14: No benefit-risk framing exists for HIPAA gaps that carry a safety tail — addressable-spec and emergency-access decisions need an ALARP/benefit-risk justification

- **Author:** agent:risk-management
- **What:** F-2 (addressable rationale) and F-3 (emergency access/auto-logoff) are dispositioned as documentation/compliance items. Any addressable-spec or access-control trade that touches a HARM-DPS chain is a benefit-risk / ALARP determination under ISO 14971 §7–§8 — "implement vs document-why-not" is exactly a residual-risk-vs-burden trade. The program has no benefit-risk home: the Risk-Benefit Report named in the risk strategy doesn't exist, and the threat-model template's own escalation to a benefit-risk analysis can't fire because no threat has been scored.
- **Evidence:**
  - `risk-strategy.md:24–29` — "Plans This Informs" lists a "Risk-Benefit Report | pca-device (lead)"; strategy is an unassembled stub; no RMP / Risk-Benefit Report instance under any DHF.
  - `threat-modeling-wi.md` §4.6 — "Threats in the Unacceptable region … trigger a benefit-risk analysis (GL-STD-RM-001 §7)" — mechanism exists, no instantiated input.
  - `45-cfr-part-164.md` §164.306(d)(3) + (b)(2)(iv) — the addressable decision is itself a risk-based ("probability and criticality") determination, i.e. a benefit-risk judgment.
- **Impact:**
  - _Regulatory:_ Recording addressable + emergency-access decisions as benefit-risk/ALARP determinations satisfies HIPAA §164.306(d)(3) **and** ISO 14971 residual-risk evidence with one artifact (avoiding the F-12 divergence).
  - _Safety:_ Without a benefit-risk home, a decision not to implement an addressable control on a telemetry path with a HARM-DPS-002 tail is made on a privacy rationale alone, safety consequence unweighed.
  - _Filing:_ A benefit-risk conclusion addressing connected/cyber residual risks strengthens the K210345 risk-file narrative.
- **Resolution proposal:** Route any F-2/F-3 item with a HARM-DPS tail through the GL-STD-RM-001 §7 benefit-risk path; record the ALARP disposition in the (to-be-created) Risk-Benefit Report, cross-referenced with the HIPAA risk-analysis artifact so the residual verdict is single-sourced.
- **Owner / next step:** Risk Manager + Cybersecurity + Privacy/Regulatory — sequence after F-11 populates the feeding hazard rows.

## Recommendations

_Distilled from F-1…F-14. Priority order (P1 = highest readiness leverage). None of these gate the 510(k); they gate a hospital BA / procurement review._

1. **P1 — Author a HIPAA Security Risk Analysis artifact** (§164.308(a)(1)(ii)(A), the Required keystone) under cloud-suite design-controls / cross-component cybersecurity file, structured per NIST SP 800-66 Rev. 2, hooked into the threat-model output; add it to the cybersecurity SOP §7 Records. (F-4) **Precede it** with a reconciliation rule in `risk-strategy.md` naming ISO 14971 as the single residual-risk authority and the HIPAA analysis as a feeding input. (F-12)
2. **P1 — Populate the security→safety bridge.** Fill the three v0.1-stub hazard analyses (`pca-device`, `cloud-suite`, `connectivity-adapter`) with the `HARM-DPS` chains (telemetry integrity loss → wrong clinical decision; availability loss during use; ePHI exposure), cross-referencing the threat model the cybersecurity-plan §3 rule already mandates. (F-11)
3. **P2 — Close the two missing access-control specs:** add SRS/DI rows for emergency access §164.312(a)(2)(ii) (Required) + automatic logoff §164.312(a)(2)(iii) — and add the corresponding HARM-DPS-003 availability hazard row so the control is justified against a harm. (F-3, F-13)
4. **P2 — Author the breach-response + incident-response procedure** (§164.410 ≤60-day BA clock + §164.308(a)(6)), with the SW-009 encryption safe-harbor analysis. (F-8)
5. **P2 — Add a "Privacy & Security Posture (HIPAA)" section to `regulatory-strategy.md`:** BA determination, the device-class-vs-ePHI decoupling (MDDS/non-device still in HIPAA scope), §164.314(a) BAA-per-tenant + §164.308(b) IaaS flow-down, and the FDA-vs-HIPAA audience routing. (F-6, F-7, F-9)
6. **P3 — Document the addressable-implementation determinations** (encryption at rest §164.312(a)(2)(iv), in transit (e)(2)(ii), integrity (e)(2)(i)) as ALARP/benefit-risk decisions in the Risk-Benefit Report + HIPAA risk analysis. (F-2, F-14)
7. **P3 — Resolve the pca-device-local-ePHI `[VERIFY]`** (§164.310(d)); if positive, add sanitization SRS/DI + service-manual labeling (21 CFR 801). (F-10)

## Open Questions

- **Audience (raised by F-7):** Is HIPAA readiness purely a hospital-procurement / BA-contract concern (route to operational QMS + contracts), or does the program intend any HIPAA-adjacent evidence in an FDA Q-Sub? HIPAA Security-Rule conformance is **not** a 510(k) criterion — confirming this routing prevents inflating the filing.
- Is there an existing security risk assessment that covers ePHI, or is the (v0.1-stub) threat model the only cybersecurity risk artifact today? (F-11 found the latter.)
- EU/GDPR is cited alongside HIPAA in the cloud-suite user needs — in scope for this readiness pass, or deferred (task 075 deferred GDPR references until an EU market path is real)?
- pca-device firmware: does it persist patient-identifiable events locally? (Resolves A12 / F-10 and the §164.310(d) labeling consequence.)

### Resolved this session
- ~~"Does `docs/external/regulations/hipaa.md` exist?"~~ — **Yes** (task ben/076). Added to `grounded_against`; the L1b mapping corroborated by the fan-out.

## References

_Consolidated as findings land._

- **Standards clauses:** 45 CFR §§164.306(b)(2)/(d)(3), 164.308(a)(1)/(a)(4)/(a)(6)/(a)(7)/(b), 164.310(d), 164.312(a)/(b)/(c)/(d)/(e), 164.314(a), 164.316(b), 164.410 (Subpart D); Privacy §164.524, §164.530(j). FDA §524B; 21 CFR 801 (labeling). IEC 81001-5-1 §5; ISO 14971 §7–§8.
- **Frameworks:** NIST SP 800-66 Rev. 2.
- **Internal artifacts:** cloud-suite UN/DI/SRS (SW-001/002/005/009/010/011/015/016/021/024/030); connectivity-adapter DI/SRS (DI-017/SW-018/SW-026); cybersecurity SOP §6.4 + cybersecurity-plan §3; threat-modeling WI §4.6; Master Harms List §3.8 (HARM-DPS-001…004); risk-strategy.md; per-DHF `GL-TMP-RM-003-hazard-analysis.md` (v0.1 stubs); `GL-TMP-SW-002-threat-model.md` (v0.1 stubs); regulatory-strategy.md; `submissions/510k/composition-manifest.md`.
- **Project applicability (L1b):** `docs/external/regulations/hipaa.md`, `docs/external/industry-frameworks/nist-sp-800-66.md`.
- **Registry distillations (L1a):** `45-cfr-part-164.md`, `nist-sp-800-66.md`.

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| 2026-06-02 | human:benxavier-gl | Initial draft scaffolded from `gap-analysis` skill template (system-wide HIPAA readiness). Authored Goal / Source / Assertions (A1–A10 across admin/physical/technical/org/documentation safeguards). Findings left for advisor fan-out (cybersecurity + risk-management + regulatory-affairs). |
| 2026-06-02 | agent:cybersecurity | Primary fan-out. Read DHF UN/DI/SRS + cybersecurity SOP/WI + L1b `hipaa.md` + registry refs. Appended F-1…F-6 and disposed A1–A10: A1–A7 confirmed (core §164.312 + contingency + RBAC chains reach testable SRS rows w/ named verification), A8/A9 partial, A10 refuted. Key gaps: emergency-access (Required) + auto-logoff missing (F-3); no ePHI-scoped §164.308(a)(1) risk analysis (F-4); no BAA posture (F-6). Corrected stale grounding premise — `docs/external/regulations/hipaa.md` exists; added to `grounded_against`. |
| 2026-06-02 | agent:regulatory-affairs | Consulting fan-out. Appended F-7…F-10: HIPAA-vs-FDA(§524B) audience separation — HIPAA not a 510(k) criterion (F-7); Breach Notification Subpart D §164.410 + incident response §164.308(a)(6) wholly absent → new assertion A11 (F-8); BA determination must decouple from FDA device class (MDDS/non-device still in HIPAA scope) → regulatory-strategy privacy section (F-9); pca-device-local ePHI §164.310(d) + 21 CFR 801 labeling determination → new assertion A12 (F-10). Inline citation check: all clauses sound vs L1a/L1b. |
| 2026-06-02 | agent:risk-management | Consulting fan-out. Appended F-11…F-14: security-risk→safety-risk bridge machinery (Master Harms List HARM-DPS, cybersecurity-plan §3) exists but hazard analyses + threat models are empty v0.1 stubs — no ePHI/telemetry compromise represented as a safety hazard (F-11); HIPAA §164.308(a)(1) vs ISO 14971 need a reconciliation/precedence rule, risk-strategy.md is an unassembled stub (F-12); emergency-access (F-3) carries a HARM-DPS-003 S4 availability tail (F-13); no benefit-risk/ALARP home for HIPAA gaps with safety tails (F-14). Surfaced the safety dimension every F-1…F-10 marked n/a. |
