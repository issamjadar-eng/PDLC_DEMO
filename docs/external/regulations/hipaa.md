# HIPAA (45 CFR Part 164) — Project Applicability

_Demo sample data — not for clinical use._

**Regulation**: 45 CFR Part 164 — Security & Privacy of Individually Identifiable Health Information
**L1a source (authoritative text)**: [`.claude/skills/medtech-docs/references/regulations/45-cfr-part-164.md`](../../../.claude/skills/medtech-docs/references/regulations/45-cfr-part-164.md)
**Companion implementation guide**: [`docs/external/industry-frameworks/nist-sp-800-66.md`](../industry-frameworks/nist-sp-800-66.md) (L1b) · [`references/industry-frameworks/nist-sp-800-66.md`](../../../.claude/skills/medtech-docs/references/industry-frameworks/nist-sp-800-66.md) (L1a)
**Scope of this file**: how the HIPAA Security Rule applies to PP3500's ePHI-handling modules. The L1a file says *what the rule requires*; this file says *what this program decided about it*.

---

## 1. Applicability determination

| Question | Determination |
|----------|---------------|
| Does PP3500 handle ePHI? | **Yes.** Pump-originated telemetry (therapy events, alarms, infusion history) is associated with patient identity in the cloud platform. `cloud-suite` SRS SW-009 explicitly encrypts "all persistent **PHI**"; SW-008/021/022 manage PHI residency, retention, and de-identification. |
| Is the manufacturer a covered entity? | **No.** GlobalLogic/Hitachi is not a health plan, clearinghouse, or treating provider. |
| Is the manufacturer a business associate? | **Yes [VERIFY against signed BAAs].** Operating `cloud-suite` as a multi-tenant service that creates/receives/maintains/transmits ePHI **on behalf of hospital covered entities** is the textbook business-associate relationship. A Business Associate Agreement (BAA) with each hospital tenant is required; **§ 164.314(a)** BA-contract terms and **§ 164.308(b)** flow-down to subcontractors (cloud IaaS, observability sinks) apply. |
| Which subparts bind us? | **Subpart C (Security Rule)** — directly, by BA flow-down. **Subpart D (Breach Notification)** — § 164.410 BA-to-covered-entity reporting. **Subpart E (Privacy Rule)** — mostly the covered entity's obligation; our touchpoint is § 164.514 de-identification and minimum-necessary support. |

**Net:** the Security Rule (Subpart C) is the load-bearing subpart for the DHF. The rest of this file maps its technical safeguards to PP3500 modules and SRS requirements.

## 2. ePHI data-flow (what we're protecting)

```
PCA Pump (PP3500 firmware)  ──mTLS 1.3, X.509──▶  Connectivity Adapter  ──mTLS, X.509──▶  Cloud Suite
   therapy/alarm events                            (on-prem, in transit)                    (PHI at rest,
   [VERIFY: patient-id at pump?]                    CA SW-018, SW-005                          BYOK AES-256-GCM)
                                                                                              cloud SW-009
```

- **`cloud-suite`** — ePHI **at rest** (storage, audit log, backups). Primary Security-Rule surface.
- **`connectivity-adapter`** — ePHI **in transit** (pump↔cloud relay, on-prem). Transmission-security surface.
- **`pca-device`** (pump firmware) — local event logs. **[VERIFY]** whether locally-stored events are patient-identifiable ePHI; if so, § 164.310(d) device/media controls (sanitization on disposal/RMA) attach to pump hardware.

## 3. § 164.312 Technical Safeguards → module / SRS mapping

R = Required, A = Addressable (see L1a §164.306(d) — "addressable" means implement-or-document-an-equivalent, **not** optional).

| § 164.312 standard / spec | R/A | Module | Implementing SRS requirement(s) | Status |
|---------------------------|-----|--------|----------------------------------|--------|
| (a)(1) Access control — (a)(2)(i) **Unique user identification** | R | cloud-suite P1, connectivity-adapter A6 | cloud **SW-001** (SAML 2.0/OIDC federated auth, no local accounts), CA **SW-016** (same) | ✅ Covered |
| (a)(1) Access control — tenant/role authorization | R (via §164.308(a)(4)) | cloud P1, CA A5 | cloud **SW-002** (tenant-claim authz, reject cross-tenant), **SW-003** (self-service RBAC, audit-logged), **SW-004** (short-lived workload identity); CA **SW-026** (console RBAC) | ✅ Covered |
| (a)(2)(ii) **Emergency access procedure** | R | cloud P1 | — | ⚠️ **GAP [VERIFY]** — no break-glass/emergency-access requirement found in SRS. Either add an SRS row or document why N/A (multi-tenant SaaS may rely on tenant-admin recovery). |
| (a)(2)(iii) **Automatic logoff** | A | cloud P1 / console, CA A5 | — | ⚠️ **GAP [VERIFY]** — no session-inactivity-timeout requirement found. Addressable → implement or document equivalent. |
| (a)(2)(iv) **Encryption & decryption** (at rest) | A | cloud P3 | cloud **SW-009** (AES-256-GCM, all persistent PHI + auth artifacts, hospital-rotatable BYOK, ≤24 h key rotation) | ✅ Covered (exceeds — BYOK) |
| (b) **Audit controls** | R | cloud P4, CA A5/A6 | cloud **SW-011** (hash-chained tamper-evident log, ≥7 yr), **SW-012** (customer streaming sinks), **SW-023** (forensic query + integrity proof); CA **SW-014** (audit search), **SW-017** (CEF syslog-TLS streamer) | ✅ Covered (strong) |
| (c)(1) **Integrity** — (c)(2) authenticate ePHI | R / A | cloud P4, CA A1 | cloud **SW-011** (hash-chain detects mutation), **SW-023** (cryptographic integrity proof); CA **SW-002** (fsync-before-ACK durability of pump events) | ✅ Covered |
| (d) **Person or entity authentication** | R | cloud P1/P2, CA A6 | cloud **SW-001** (IdP), **SW-005** (mTLS X.509 adapter identity), **SW-004** (workload identity); CA **SW-016** (IdP), **SW-018** (mTLS 1.3 pump X.509 client-cert) | ✅ Covered |
| (e)(1) Transmission security — (e)(2)(i) **Integrity controls** | R / A | cloud P2, CA A6 | cloud **SW-005** (mTLS ingest, reject untrusted); CA **SW-018** (mTLS 1.3 handshake validation), **SW-029** (cert-expiry monitor) | ✅ Covered |
| (e)(2)(ii) **Encryption** (in transit) | A | cloud P2, CA A2/A6 | cloud **SW-005** (mTLS); CA **SW-007** (TLS downstream endpoints), **SW-018** (mTLS 1.3), **SW-017** (syslog-TLS) | ✅ Covered |

## 4. Other Security-Rule clauses with project hooks

| Clause | R/A | PP3500 disposition |
|--------|-----|--------------------|
| § 164.308(a)(1)(ii)(A) **Risk analysis** | R | Satisfied via the cybersecurity threat model + risk process (cross-ref `cybersecurity` advisor / threat-model artifact). The HIPAA risk analysis should be a documented view of that same assessment — see NIST SP 800-66 (`../industry-frameworks/nist-sp-800-66.md`). **[VERIFY]** an explicit HIPAA-framed risk analysis exists. |
| § 164.308(a)(7) **Contingency plan** | R | cloud **SW-010** (PITR ≤35 days), **SW-026** (tenant backup/restore), **SW-016** (chaos exercises incl. region loss). |
| § 164.310(d) **Device & media controls** (disposal, re-use) | R | Cloud: **SW-021** (deterministic end-of-retention purge w/ cryptographic evidence), **SW-022** (non-prod de-identification gate). Pump hardware: **[VERIFY]** sanitization on RMA/disposal if pca-device stores identifiable ePHI. |
| § 164.314(a) **BA contract terms** | R | Requires BAA with each hospital tenant + flow-down to cloud subcontractors. **[VERIFY]** BAA template and subcontractor agreements exist. |
| § 164.316(b)(2)(i) **6-year documentation retention** | R | cloud **SW-021** explicitly enforces "minimum 6 years for HIPAA-covered records"; **SW-011** retains audit log ≥7 yr. ✅ |
| § 164.410 **Breach notification (BA→CE)** | R (Subpart D) | **[VERIFY]** a documented breach-response procedure with the ≤60-day BA reporting clock. Mitigant: **SW-009** AES-256-GCM at rest is the "unsecured PHI" **safe harbor** — encrypted-data loss is outside breach-notification scope. |

## 5. Privacy-Rule (Subpart E) touchpoints

Mostly the covered entity's obligation; PP3500 supports it via:
- § 164.514 **de-identification** — cloud **SW-022** (non-prod de-id gate), supporting analytics/AI-training data leaving HIPAA scope.
- Data-subject rights (overlaps GDPR Art. 15-17) — cloud **SW-020** (DSR API). _Note: GDPR, not HIPAA; tracked separately if an EU path is pursued._

## 6. Gaps & open questions (for Q-Sub / design review)

1. **Emergency access procedure (§164.312(a)(2)(ii), Required)** — no SRS row. Add one or document N/A rationale. ⚠️
2. **Automatic logoff (§164.312(a)(2)(iii), Addressable)** — no SRS row. Implement or document equivalent. ⚠️
3. **pca-device ePHI determination (§164.310(d))** — does the pump store patient-identifiable events locally? Drives whether hardware sanitization controls apply. **[VERIFY]**
4. **HIPAA-framed risk analysis (§164.308(a)(1))** — confirm the cybersecurity risk assessment is documented as a HIPAA Security-Rule risk analysis (NIST SP 800-66 method). **[VERIFY]**
5. **BAA + subcontractor flow-down (§164.314(a))** — confirm template + executed agreements. **[VERIFY]**
6. **Breach-response procedure (§164.410)** — confirm the ≤60-day BA clock is proceduralized. **[VERIFY]**

## 7. Citation discipline (cite-both)

Any advisor or document citing a HIPAA clause must reference **both** layers:
- **L1a** — [`references/regulations/45-cfr-part-164.md`](../../../.claude/skills/medtech-docs/references/regulations/45-cfr-part-164.md) for *what the clause requires* (verbatim text).
- **L1b** — this file for *how PP3500 applies it* (module + SRS mapping + gaps).

Citing only one layer masks a verification gap (medtech-docs cite-both mandate; advisors v1.5.0 Hard Rule).

---

**SRS sources cited (demo content):**
- `docs/project/dhfs/cloud-suite/design-controls/requirements/software-requirements.md`
- `docs/project/dhfs/connectivity-adapter/design-controls/requirements/software-requirements.md`

**Knowledge cutoff / currency**: HIPAA text current to eCFR Title 45 issue 2026-05-29; the 2025 Security Rule NPRM (would make encryption + MFA Required, remove the addressable/required split) is **proposed, not final** — see the L1a "Pending rulemaking" section. PP3500's design already satisfies the proposed encryption/MFA direction (SW-009 / SW-001).
