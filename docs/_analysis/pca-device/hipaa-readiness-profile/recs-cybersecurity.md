---
title: "Cybersecurity / HIPAA Security Rule Review — PP3500 ePHI Path"
parent_analysis: hipaa-readiness-profile
advisor: cybersecurity
role: primary
specialty: "IEC 81001-5-1, FDA premarket cybersecurity, HIPAA Security Rule §164.312 technical safeguards, threat modeling, SBOM"
created: 2026-06-04
---
> _Demo sample data — not for clinical use. Regenerated full write-up backing the cybersecurity findings (F-1…F-6) in this analysis._

## What good looks like

For a connected ePHI device, the HIPAA Security Rule (45 CFR Part 164, Subpart C) is a *technical-requirements checklist* that should map almost one-to-one onto a SaMD/cloud SRS. "Ready" — for a hospital BA/procurement review, not a 510(k) — means three things hold together:

1. **The §164.312 technical-safeguard chain is specified and testable.** Each safeguard — access control (a), audit controls (b), integrity (c), authentication (d), transmission security (e) — reaches a verifiable software requirement with a named verification method, not a user-need or design-input that trails off. Per `45-cfr-part-164.md` Appendix A (L1a lines 145–149), that includes the *Required* sub-specs (unique user ID, emergency access, audit, authentication) and the *Addressable* ones (auto-logoff, encryption at rest, integrity-controls, transmission encryption).
2. **"Addressable" decisions are on the record.** §164.306(d)(3) (L1a lines 54–57): an addressable spec is implemented *if reasonable and appropriate*, otherwise the rationale is documented and an equivalent alternative implemented. "Addressable" is the single most-misread word in the rule — skipping one silently is a non-compliance pattern even when the underlying control happens to exist.
3. **The Required keystone — the §164.308(a)(1)(ii)(A) risk analysis — exists as a documented HIPAA-framed view.** OCR enforcement overwhelmingly cites a missing/inadequate risk analysis as the root finding (L1a line 85). The good pattern is *one* risk engine — the ISO 14971 + IEC 81001-5-1 threat model — producing a HIPAA-scoped output per NIST SP 800-66 Rev. 2 method, retained 6 years (§164.316(b)(2)(i)). And the organizational backstop — §164.314(a) BA-contract terms + §164.308(b) subcontractor flow-down — has a home in a quality/regulatory artifact.

## Overall readiness read

**The core technical posture is strong; the gaps are documentation and two specific missing requirements — none of which gate the 510(k), all of which a hospital CISO questionnaire will surface.**

The §164.312 chain that does the load-bearing work (tenant isolation, tamper-evident audit, integrity/purge, mTLS in transit, AES-256-GCM-BYOK at rest) is fully traced UN→DI→SRS with named security tests — this is submission- and procurement-defensible (F-1). The readiness deficit is concentrated and addressable: two access-control sub-specs have *no* SRS row at all (F-3, one of them *Required*); the addressable-implementation decisions are made-in-practice but never *recorded as addressable determinations* (F-2); the *Required* HIPAA risk analysis is implied by the threat model but not scoped or framed as such (F-4); and the BA/BAA organizational posture lives only in external reference files, not in any project work-product (F-6). The contingency-plan and RBAC/authentication safeguards (A6/A7) are solid and testable (F-5). Net: a good engineering baseline with a thin documentation/specification layer on top.

## Safeguard-by-safeguard walk

**A1–A5 — the §164.312 technical chain (F-1, confirmed).** Each reaches a testable SRS row, verified against `cloud-suite/.../software-requirements.md` and `connectivity-adapter/.../software-requirements.md`, and corroborated by the L1b mapping in `hipaa.md` §3:
- **A1 Access control / tenant isolation** §164.312(a)(1) — SW-002 (tenant-claim authz, rejects cross-tenant) + SW-024 (CI cross-tenant probe).
- **A2 Audit controls** §164.312(b) (Required) — SW-011 (hash-chained tamper-evident log ≥7yr); also satisfies §164.316(b)(2)(i) 6-year retention.
- **A3 Integrity** §164.312(c)(1) (Required) — SW-011 mutation detection + SW-021 deterministic purge with cryptographic evidence.
- **A4 Transmission security** §164.312(e)(1) — CA SW-018 (mTLS 1.3, X.509) + cloud SW-005 (mTLS ingest).
- **A5 Encryption at rest** §164.312(a)(2)(iv) (Addressable) — SW-009 (AES-256-GCM, hospital-rotatable BYOK) — *exceeds* the bar.

**The access-control gaps (F-3, the strongest gap).** Grep of both SRS files returns zero matches for emergency-access/break-glass and zero for session-inactivity/auto-logoff. That leaves **two Appendix-A specs unaddressed**:
- **§164.312(a)(2)(ii) Emergency access procedure — Required.** Its absence is exactly the kind of finding OCR cites. For an opioid-delivering pump's monitoring platform this is *also* an availability concern (see the consulting risk view, F-13), not only a privacy checkbox.
- **§164.312(a)(2)(iii) Automatic logoff — Addressable.** Neither implemented nor documented-why-not — the worst of both addressable states.

**The addressable-rationale gap (F-2).** Encryption at rest (a)(2)(iv), transmission encryption (e)(2)(ii), and integrity controls (e)(2)(i) are all Addressable and all *implemented* (SW-009 / SW-005 / SW-018) — but §164.306(d)(3) requires the *decision* to be documented as an addressable determination, and no artifact does that. Low regulatory risk (controls exist and exceed), but an OCR-style review or security questionnaire expects the analysis on record.

**The Required risk-analysis hook (F-4 — highest-leverage gap).** A8 is only partial. I read `cybersecurity-sop.md` and `threat-modeling-wi.md` end-to-end: the STRIDE process is sound, but HIPAA appears only as a *responsibility row* (SOP line 70) and a *regulatory-input bullet* (SOP line 108); the §7 Records table lists no HIPAA risk-analysis deliverable; and the WI asset inventory names "Patient data — PHI" (line 84) yet anchors harm to the safety Master Harms List, never mapping to Security-Rule safeguards. §164.308(a)(1)(ii)(A) is *Required* (L1a lines 67, 85) and is a distinct documented view (NIST SP 800-66 method, `nist-sp-800-66.md` lines 22, 47), retained 6 years. The machinery exists; the HIPAA-framed instance does not.

**The BAA posture (F-6 — refuted as specified-in-a-DHF-artifact).** Grep of `regulatory-strategy.md` + `submissions/` returns zero hits for "business associate" / "BAA" / "164.314"; the strategy only states "privacy still applies." Yet operating cloud-suite multi-tenant on third-party IaaS is the textbook BA relationship (`hipaa.md` §1), so §164.314(a) BA-contract terms + §164.308(b) flow-down (both Required, L1a lines 83, 140) apply — and have no home in any project artifact.

## Worked example — the missing emergency-access SRS row (F-3)

**Before.** `cloud-suite/.../software-requirements.md` P1 carries SW-001..004, SW-024, SW-025 (federation, tenant authz, self-service RBAC, workload identity, cross-tenant probe). A grep for `emergency|break.?glass|inactiv|auto.?log` returns nothing across both the cloud-suite and connectivity-adapter SRS. §164.312(a)(2)(ii) (Required) and (a)(2)(iii) (Addressable) are simply unrepresented — the readiness statement cannot point to a row, and a hospital CISO checklist line "show me your emergency-access procedure" has no answer.

**After.** Add to cloud-suite P1, each traced to a new DI row:
- *SW-0xx (emergency access, §164.312(a)(2)(ii) Required):* "The platform shall provide an audited break-glass procedure granting a named, time-boxed elevated-access grant to ePHI during a declared emergency, with every break-glass event written to the SW-011 tamper-evident audit log. **Verification:** abuse-case test asserting (a) the grant is time-boxed, (b) the event is logged immutably." If multi-tenant SaaS genuinely relies on tenant-admin recovery, *document that as the N/A rationale* rather than leaving the spec silent.
- *SW-0yy (automatic logoff, §164.312(a)(2)(iii) Addressable):* "Interactive sessions to ePHI-bearing surfaces shall terminate after ≤N minutes of inactivity," mirrored on the connectivity-adapter operator console. Acceptance: session-timeout integration test.

The "before" is a silent gap an external reviewer finds in thirty seconds; the "after" is a traced, tested requirement with an explicit addressable-or-N/A disposition.

## Why this matters for THIS system

The architecture strategy (`architecture-strategy.md` System Context) fixes the ePHI path: **PP3500 pump firmware → on-prem Connectivity Adapter → multi-tenant Cloud Suite.** Three consequences for the safeguard map:

- **The adapter is the transmission-security surface** (§164.312(e)) — ePHI-in-transit, on-prem, mTLS 1.3. The adapter runs on-prem deliberately "to keep PHI inside the hospital boundary," which is itself a defensible design posture worth stating in the readiness narrative.
- **The cloud-suite is the concentration point** (§164.312 at-rest + audit + integrity, and §164.314(a) BA exposure) — it creates/receives/maintains ePHI *on behalf of hospital covered entities*, the textbook BA relationship (F-6). Critically, BA status attaches regardless of FDA device class: the strategy classifies the adapter as MDDS and several cloud apps as non-device, but "not an FDA device" ≠ "not a HIPAA business associate" (consulting view F-9).
- **The pump may be a physical-safeguard surface** (§164.310(d)) — *if* firmware persists patient-identifiable events locally, sanitization-on-disposal/RMA attaches to hardware. That determination is still an open `[VERIFY]` (`hipaa.md` §2/§6 item 3) and is the one HIPAA thread that can legitimately reach FDA labeling (consulting view F-10).

The modular-DHF + composition-manifest pattern (architecture-strategy b.2) means the §524B cybersecurity evidence (threat model, SBOM, encryption SRS) is *referenced* into the 510(k), while the HIPAA-framed view of that same evidence is a *separate, procurement-facing* deliverable — same controls, two audiences (consulting view F-7). Do not re-submit; reference.

## Prescriptions

1. **Author a HIPAA Security Risk Analysis artifact (Required keystone).** Under cloud-suite design-controls or a cross-component cybersecurity-file deliverable, structured per NIST SP 800-66 Rev. 2, hooked into the existing threat-model output (one risk engine, not a parallel process); add it to `cybersecurity-sop.md` §7 Records. Use `hipaa.md` §3 as the safeguard→SRS scaffold. *Owner:* Cybersecurity Lead + Privacy/Regulatory. *Acceptance:* a retained (§164.316 6-yr) document that scopes ePHI, frames §164.308(a)(1)(ii)(A), and references the implementing SRS rows. (F-4)
2. **Add the two missing access-control SRS rows.** Emergency access §164.312(a)(2)(ii) (Required, or documented N/A) + automatic logoff §164.312(a)(2)(iii), each traced to a DI row; mirror auto-logoff on the connectivity-adapter console. *Owner:* Cloud-suite R&D + Cybersecurity Lead. *Acceptance:* two SRS rows with named verification methods (or a recorded N/A rationale for emergency access). (F-3)
3. **Record the addressable-implementation determinations.** Add an "addressable determinations" table (in the F-4 risk analysis or `hipaa.md` §3): per addressable spec — encryption at rest (a)(2)(iv), transmission (e)(2)(ii), integrity (e)(2)(i) — the decision (implement / equivalent / N/A-with-rationale) and the implementing SRS row. No new SRS row. *Owner:* Cybersecurity Lead + Privacy/Regulatory. *Acceptance:* every Addressable §164.312 spec carries a documented decision. (F-2)
4. **Give the §164.314(a) BA/BAA posture a home.** Add a privacy/security-posture section to `regulatory-strategy.md`: covered-entity = No, business-associate = Yes, BAA-per-tenant + §164.308(b) IaaS flow-down. *Owner:* Regulatory Affairs (cybersecurity consulting). *Acceptance:* the strategy states the BA determination and the flow-down obligation, referencing `hipaa.md`. (F-6)
5. **Disposition the confirmed safeguards in the readiness statement.** Mark A1–A7 confirmed; cite the L1b mapping rather than re-deriving the trace. Add a one-line HIPAA §164.524 Right-of-Access mapping note over the GDPR-framed DSR API (SW-020/SW-023). *Owner:* Cybersecurity Lead. *Acceptance:* readiness statement cites `hipaa.md` §3 for A1–A5 and §4 for A6/A7. (F-1, F-5)

## Evidence base

- **Analysis:** `docs/_analysis/pca-device/hipaa-readiness-profile/hipaa-readiness-profile.md` (A1–A12; findings F-1…F-6).
- **Project work-product (SRS/UN):** `docs/project/dhfs/cloud-suite/design-controls/requirements/software-requirements.md` (SW-001/002/005/009/011/021/024); `docs/project/dhfs/connectivity-adapter/design-controls/requirements/software-requirements.md` (SW-018); `docs/project/dhfs/cloud-suite/design-controls/user-needs/user-needs.md` (UN-002/010/011/015/021).
- **QMS process:** `docs/internal/source-md/software-cybersecurity/cybersecurity-sop.md` (HIPAA only at lines 70, 108; §7 Records lines 152–161 carry no HIPAA risk analysis); `docs/internal/source-md/software-cybersecurity/threat-modeling-wi.md` (asset inventory line 84 "Patient data — PHI"; harm anchored to Master Harms List, §4.5/§4.6).
- **Architecture context:** `docs/project/strategies/architecture-strategy.md` (System Context — device→adapter→cloud path; modular-DHF/composition-manifest pattern b.2).
- **HIPAA clauses (cite-both):** L1a `.claude/skills/medtech-docs/references/regulations/45-cfr-part-164.md` — §164.306(d)(3) (lines 54–57), §164.308(a)(1)(ii)(A) (lines 67, 85), §164.312 Appendix A matrix (lines 145–149), §164.314(a)/§164.308(b) (lines 83, 140), §164.316(b)(2)(i) (line 121). L1b `docs/external/regulations/hipaa.md` — §3 technical-safeguard→SRS map, §4 other clauses, §6 gap items 1–6.
- **Method:** L1a `.claude/skills/medtech-docs/references/industry-frameworks/nist-sp-800-66.md` (lines 22, 47 — operationalizing the §164.308(a)(1) risk analysis; one assessment, two drivers); L1b `docs/external/industry-frameworks/nist-sp-800-66.md`.

## Cross-discipline open questions

| # | Question | Owner / advisor | Why it's cross-discipline |
|---|----------|-----------------|---------------------------|
| 1 | Is HIPAA readiness purely a hospital-procurement/BA-contract concern, or is any HIPAA-adjacent evidence intended for an FDA Q-Sub? (HIPAA conformance is not a 510(k) criterion.) | Regulatory Affairs (F-7) | Determines whether F-3/F-4/F-6 are routed to operational QMS/contracts or risk inflating the filing envelope. |
| 2 | When the F-4 HIPAA risk analysis stands up alongside the ISO 14971 file, which governs residual-risk acceptability? | Risk Management (F-12) | The cybersecurity-authored risk analysis cannot down-rate a 14971-unacceptable residual; precedence rule is unwritten. |
| 3 | Should the emergency-access SRS row (F-3) also carry a HARM-DPS-003 availability hazard row, treating break-glass as a safety control? | Risk Management (F-13) | Clinician lockout during an auth outage on an opioid pump is a credible S4 chain — security gap with a safety tail. |
| 4 | Does pca-device firmware persist patient-identifiable events locally (resolving §164.310(d) + the 21 CFR 801 sanitization labeling consequence)? | pca-device R&D + Regulatory (F-10) | The only HIPAA thread that can legitimately reach an FDA artifact. |
| 5 | Are the v0.1-stub threat models / hazard analyses scheduled to be populated in the same increment as the F-4 risk analysis? | Risk Management (F-11) | The security→safety bridge F-4 assumes is operating is currently uninstantiated. |
