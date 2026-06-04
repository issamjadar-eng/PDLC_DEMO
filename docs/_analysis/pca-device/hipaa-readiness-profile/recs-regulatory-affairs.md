---
title: "Regulatory / HIPAA Posture Review — PP3500 (BAA, Breach Rule, Audience)"
parent_analysis: hipaa-readiness-profile
advisor: regulatory-affairs
role: consulting
specialty: "FDA pathway + HHS/OCR HIPAA posture, Business-Associate determination, Breach Notification Rule, regulatory strategy"
created: 2026-06-04
---
> _Demo sample data — not for clinical use. Regenerated full write-up backing the regulatory findings (F-7…F-10) in this analysis._

## What good looks like

The HIPAA bar is **organizational and market-access**, not premarket-FDA. A connected-PCA program acting as a **business associate** clears that bar when five things are present and owned:

1. **A stated audience.** The readiness statement names *who* reads it (HHS/OCR enforcement posture + hospital CISO/DPO procurement due-diligence) and is explicit that HIPAA Security-Rule conformance is **not** a 510(k) acceptance criterion. FDA reviews §524B premarket cybersecurity (`composition-manifest.md:50`) and 21 CFR 801 labeling (`:52`) — not §164 safeguards.
2. **A business-associate determination on record**, decoupled from FDA device classification: BA status attaches the moment a component creates/receives/maintains/transmits ePHI for a covered entity, **regardless** of whether that component is a device, an MDDS, or non-device software (L1a §174; L1b `hipaa.md` §1).
3. **§164.314(a) BA-contract posture** — a BAA per hospital tenant, plus **§164.308(b)** flow-down to subcontractors (cloud IaaS, observability sinks) (L1a §83; L1b §1, §4).
4. **Subpart D Breach Notification (§164.400–414)** proceduralized — specifically the **§164.410** BA→covered-entity report "in no case later than 60 days after discovery" (L1a §151–153), paired with **§164.308(a)(6)** Security Incident Procedures Response/Reporting, a *Required* spec (L1a §137).
5. **§164.310(d) physical/device-media controls determined** for any locally-stored ePHI — Disposal (R) and Media Re-use (R) (L1a §144), with the sanitization-on-disposal/RMA labeling consequence resolved under 21 CFR 801.

## Overall posture read

The *technical* core is strong — F-1 confirms the §164.312 chain is fully traced UN→DI→SRS. The **organizational and audience** layer is where the gaps cluster, and that layer is the regulatory-affairs lane. Three of my four findings (F-7, F-8, F-9) point at things that have **no home in any project artifact**; F-10 is an unresolved determination. None of these gate K210345 — every one gates a hospital BA/procurement review. The danger is the inverse: treating these HIPAA gaps as filing blockers, or burning Q-Sub airtime on conformance FDA does not review (F-7).

## The covered-entity vs business-associate question (why it gates everything)

This single determination is the hinge. The manufacturer is **not a covered entity** (not a plan, clearinghouse, or provider) but **is a business associate** because `cloud-suite` runs multi-tenant and handles hospital ePHI (L1b §1; [VERIFY] against signed BAAs). Everything else cascades from it: if BA, then §164.314(a) + §164.308(b) flow-down apply, Subpart C binds by contract, and the §164.410 breach clock starts on **BAA signature**. The trap the regulatory strategy currently sets is the device-class framing: it classifies the connectivity-adapter as **MDDS (non-device)** (`regulatory-strategy.md:79`) and cloud-suite "all other apps" as **non-medical-device software** with a bare "privacy still applies" (`:81`, `:106`). "Not an FDA device" reads to a procurement reviewer as "out of HIPAA scope" — which is wrong. BA status is independent of FDA class.

## Issue walk

**F-7 — Audience unstated.** The structural separation is actually *correct* (the 510(k) manifest carries §524B + 21 CFR 801 and zero HIPAA), but correct-by-accident, not stated. Without an explicit audience-routing line, the reader can conflate market-access posture with filing evidence in either direction. Fix: a routing statement — HIPAA findings → BA-contract + operational QMS owners; §524B findings → FDA. Shared evidence (threat model, encryption SRS) is *referenced* across audiences, not *re-submitted*.

**F-8 — Subpart D + incident response unowned.** A1–A10 covered only Subpart C. The §164.410 ≤60-day BA report (L1a §151–153) and §164.308(a)(6) Required incident response (L1a §137) are neither asserted nor proceduralized anywhere in `submissions/` or `strategies/`. This is a *Required* obligation with a statutory clock and no owner. The encryption safe harbor (SW-009 AES-256-GCM = "unsecured PHI" mitigant) belongs in that procedure as the documented analysis.

**F-9 — Strategy posture section missing.** Extends F-6. The BA determination must be written into `regulatory-strategy.md` with the explicit device-class decoupling, §164.314(a) per-tenant BAA, and §164.308(b) IaaS flow-down. One section closes both F-6 and F-9.

**F-10 — Local-ePHI physical/labeling [VERIFY].** The one HIPAA thread that can legitimately reach an FDA artifact. If pump firmware stores patient-identifiable events, §164.310(d) Disposal/Media Re-use attach to pump *hardware*, with a sanitization instruction under 21 CFR 801 labeling. Open `[VERIFY]` (L1b §2, §6 item 3). Privacy is **not** an indication-for-use — keep it out of IFU; only servicing/disposal instructions land in labeling.

## Worked example — the missing privacy/security-posture section

**Before** (`regulatory-strategy.md:81`):
> Cloud Suite — all other apps … Non-medical-device software … Not filed. QMS, cybersecurity, and privacy still apply.

That bare clause invites the inference "non-device ⇒ outside HIPAA." **After** (new "Privacy & Security Posture (HIPAA)" section):
> Covered entity: **No**. Business associate: **Yes** — `cloud-suite` creates/receives/maintains/transmits ePHI for hospital covered entities. **BA status attaches independent of FDA device classification**: the connectivity-adapter (MDDS) and non-device cloud apps remain in HIPAA scope wherever they touch ePHI. Obligations: §164.314(a) BAA per hospital tenant; §164.308(b) flow-down to cloud IaaS + observability subcontractors; Subpart C technical safeguards (mapped in `hipaa.md` §3); Subpart D §164.410 breach reporting (≤60 days). HIPAA conformance is **not** a 510(k) criterion — it is a procurement/BA-contract obligation. See `docs/external/regulations/hipaa.md`.

## Why this matters for THIS system

PP3500 is an **opioid-delivering** PCA pump whose telemetry concentrates therapy-event ePHI in a multi-tenant cloud on third-party IaaS — the textbook BA fact pattern (L1b §1). A hospital CISO will demand the BAA, the breach procedure, and the §164.310(d) disposal story *before* purchase. The technical safeguards are already strong (F-1); leaving the organizational layer unowned means a defensible product fails the procurement gate on paperwork that doesn't exist yet — and risks the inverse error of inflating the 510(k)/PCCP change envelope with HIPAA evidence FDA never asked for (F-7).

## Prescriptions

1. **Add an explicit audience-routing statement** to the readiness statement and the planned strategy section: HIPAA → procurement/BA-contract + operational QMS; §524B → FDA; shared evidence referenced, not re-submitted. _Owner: Regulatory Affairs._ **Acceptance:** routing line present; no HIPAA artifact listed in the 510(k) composition manifest. (F-7)
2. **Author a "Privacy & Security Posture (HIPAA)" section** in `regulatory-strategy.md`: covered-entity=No / BA=Yes; device-class-vs-ePHI decoupling; §164.314(a) per-tenant BAA + §164.308(b) flow-down; pointer to `hipaa.md`. _Owner: Regulatory Affairs._ **Acceptance:** section exists; resolves both F-6 and F-9; the two bare "privacy still applies" lines are superseded. (F-6, F-9)
3. **Proceduralize Subpart D + incident response** — a breach-response procedure (or extension of the cybersecurity/postmarket complaint-handling SOP) carrying the §164.410 ≤60-day BA clock and §164.308(a)(6) response/reporting, with the SW-009 encryption safe-harbor analysis. _Owner: Regulatory Affairs + Cybersecurity + Postmarket._ **Acceptance:** procedure exists with the 60-day clock named, *before any BAA is executed* (signature triggers the clock). (F-8)
4. **Resolve the pca-device-local-ePHI [VERIFY]** with a pca-device R&D determination. If Yes: add a sanitization SRS/DI + service-manual/IFU instruction under 21 CFR 801 and open assertion A12. If No: document the N/A rationale. Privacy stays out of indications-for-use. _Owner: Regulatory Affairs + pca-device R&D._ **Acceptance:** §6 item-3 `[VERIFY]` closed before 510(k) labeling is finalized. (F-10)

## Evidence base

- `docs/_analysis/pca-device/hipaa-readiness-profile/hipaa-readiness-profile.md` — Assertions A8–A12; findings F-6…F-10.
- `docs/project/strategies/regulatory-strategy.md:79,81,106` — MDDS / non-device classifications + bare "privacy still applies".
- `docs/project/submissions/510k/composition-manifest.md:50,52` — FDA package = §524B + 21 CFR 801; no HIPAA rollup.
- `docs/external/regulations/hipaa.md` (L1b) §1 (BA determination), §2 (data flow + pca-device [VERIFY]), §4 (§164.314 / §164.410 rows), §6 items 3/5/6.
- `.claude/skills/medtech-docs/references/regulations/45-cfr-part-164.md` (L1a) §18 (Subpart D index), §83 (§164.308(b) flow-down), §137 (§164.308(a)(6) R), §144 (§164.310(d) Disposal/Media Re-use R), §151–153 (§164.410 ≤60-day clock + safe harbor), §174 (BA-analysis cross-ref).
- Clauses cited: 45 CFR §§164.308(a)(6)/(b), 164.310(d), 164.314(a), 164.400–414 (Subpart D, esp. §164.410); FDA §524B; 21 CFR 801.

> **Governance note:** the discovery index resolves `regulatory-strategy.md` through `project_roles` (internal-mode strategy doc) with **no `governing_qms`** attached — these prescriptions are made against 45 CFR Part 164 + the regulatory strategy's own assembly convention (`/strategy assemble regulatory`), not a QMS FORM template. Author the strategy section via the source-task → assemble flow, not by hand-editing the assembled output.

## Cross-discipline open questions

| Question | Owner discipline | Why it's cross-cutting |
|----------|------------------|------------------------|
| Does pca-device firmware persist patient-identifiable events locally? | pca-device R&D (eng) | Resolves A12/F-10 §164.310(d) scope + the 21 CFR 801 labeling consequence — a regulatory artifact. |
| Where does the breach-response procedure live — new SOP, cybersecurity SOP, or postmarket complaint-handling? | Cybersecurity + Postmarket | §164.410 BA clock vs the MDR/complaint clock are different statutory timers needing reconciliation. |
| Does the §164.308(a)(1) HIPAA risk analysis (F-4) and ISO 14971 file agree on residual-risk authority? | Risk Management | F-12 precedence rule must name 14971 as governing; my breach/incident posture feeds that risk engine. |
| Is any HIPAA-adjacent evidence intended for an FDA Q-Sub at all? | Program Mgmt + Regulatory | Confirms the F-7 routing; prevents inflating the PCCP change envelope. |
| Are signed BAAs / a BAA template in existence, or is BA status still [VERIFY]? | Legal/Contracts + Regulatory | BAA signature starts the §164.410 clock; the determination in L1b §1 is unverified until a BAA is on file. |
