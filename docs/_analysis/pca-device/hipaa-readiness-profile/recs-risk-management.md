---
title: "Risk-Management Review — HIPAA Security-Risk ↔ Patient-Safety Bridge (PP3500)"
parent_analysis: hipaa-readiness-profile
advisor: risk-management
role: consulting
specialty: "ISO 14971 risk management, security-risk ↔ safety-risk bridge (AAMI TIR57), residual-risk acceptability, benefit-risk"
created: 2026-06-04
---
> _Demo sample data — not for clinical use. Regenerated full write-up backing the risk-management findings (F-11…F-14) in this analysis._

## What good looks like

A connected, ePHI-handling, opioid-delivering pump program has to satisfy **two** risk obligations that overlap but are not the same:

- **HIPAA §164.308(a)(1)** (the Required "security management process") wants an accurate, thorough **risk analysis** of threats to the confidentiality, integrity, and availability of ePHI, and risk-management measures sufficient to reduce those risks to a "reasonable and appropriate" level (`45-cfr-part-164.md` §164.308(a)(1)(ii)(A)-(B); `docs/external/regulations/hipaa.md` §4). Its control-selection test is risk-based — §164.306(b)(2)(iv) literally asks for "the probability and criticality of potential risks to ePHI."
- **ISO 14971** wants every *foreseeable sequence of events* that can reach **patient harm** identified, controlled, and its **residual risk** evaluated for acceptability — then a top-level benefit-risk conclusion.

The bridge between them is **AAMI TIR57 / IEC 81001-5-1 §5**: where a security compromise (a CIA loss of ePHI or telemetry) can escalate to patient harm, that security risk must be **cross-referenced into the ISO 14971 file as a safety hazard** and evaluated on the safety severity scale — not left in a parallel security ledger. "Good" is one risk engine: the threat model enumerates threats, the patient-harm-bearing ones promote into the hazard analysis, residual risk is scored once on the safety scale, and the addressable/unacceptable decisions become benefit-risk determinations. This program's own QMS already prescribes exactly this — `cybersecurity-sop.md` §6.4 ("cyber hazards merge into safety-risk tracking where they can lead to patient harm") and `threat-modeling-wi.md` §4.5–§4.6 (attack-tree drilldown for S=4/5 harms; Unacceptable residual → benefit-risk per GL-STD-RM-001 §7). The machinery is specified. The question this review answers is whether it is *running*.

## Overall risk read

It is not running yet. The security→safety bridge exists as QMS machinery and as a pre-built harm taxonomy, but **no project artifact instantiates it**. The discovery index resolves `hazard_analysis: null` and `risk_management_plan: null` for `pca-device`, `connectivity-adapter`, and `cloud-suite` alike; the three threat models are Rev 0.1 DRAFT stubs with `{{}}` placeholders (`cloud-suite/.../GL-TMP-SW-002-threat-model.md`); and `risk-strategy.md` is "awaiting its first assembly." So every confidentiality/integrity/availability harm the cybersecurity pass correctly marked "n/a (safety)" is, in fact, **un-evaluated** — not absent, just unrepresented. That is the material gap behind F-11…F-14: the program is about to stand up a *second* risk process (the HIPAA risk analysis, F-4) before it has populated its *first* one (the ISO 14971 hazard file), with no rule saying which governs when they disagree.

None of this gates the K210345 510(k) — it gates a hospital BA/procurement security review and, more importantly, the integrity of the residual-risk file a reviewer expects to see demonstrated rather than templated.

## The two-risk-processes problem (which governs residual-risk acceptability)

The HIPAA registry text invites the right answer: a program already running ISO 14971 plus a cyber threat model "can route Security Rule compliance through the same risk machinery rather than standing up a parallel process" (`45-cfr-part-164.md` §164.306). But the durable artifact that would *record* this — `risk-strategy.md` — names "How cybersecurity risk (IEC 81001-5-1) feeds into overall risk" and "Risk/benefit determination approach" as unwritten section headers, and names a "Risk-Benefit Report" that does not exist. The two processes use different bases: HIPAA scores on confidentiality/availability impact and "reasonable and appropriate"; ISO 14971 scores patient-harm severity × probability against GL-STD-RM-001 acceptability bands. Run independently, they will reach **divergent residual verdicts on the same threat** — an audit-exposable inconsistency, and OCR's modal enforcement finding is precisely an inadequate or inconsistent risk analysis. The fix is a one-paragraph precedence rule, written *before* the F-4 artifact: **ISO 14971 is the single residual-risk authority for any threat with a patient-harm tail; the HIPAA §164.308(a)(1) analysis is a confidentiality/availability-scoped input whose patient-harm items promote into the 14971 hazard analysis; no HIPAA-side acceptance overrides a 14971 "unacceptable" verdict.**

## Issue walk

- **F-11 — Uninstantiated safety bridge.** The Master Harms List §3.8 pre-bakes the escalation: `HARM-DPS-001` PHI exposure (S3), `HARM-DPS-002` PHI corruption ("up to 4 if affects clinical decision"), `HARM-DPS-003` loss of availability during use (S4), `HARM-DPS-004` unauthorized device control (S4). The harms are defined; the hazard analyses that should carry their foreseeable sequences are empty stubs. Net: a telemetry-corruption→wrong-clinical-decision chain and an ePHI-confidentiality harm have **no row in any risk file**.
- **F-12 — No reconciliation rule.** Covered above. The precedence statement is cheap and prevents the divergent-record finding; it must land in `risk-strategy.md` ahead of the F-4 HIPAA risk analysis.
- **F-13 — Emergency-access is an availability tail, not just a compliance checkbox.** F-3 found §164.312(a)(2)(ii) Emergency access (Required) has no SRS row. But emergency access is an *availability* control: a clinician unable to reach ePHI/remote monitoring of a PCA pump during an auth outage is a concrete instance of `HARM-DPS-003` (S4). Closing F-3 as a bare SRS row leaves the harm unjustified; the availability-loss scenario should appear as a hazard whose residual is evaluated, with break-glass as its control — "documented N/A" only if residual is shown acceptable without it. This also aligns the F-3 remediation with §164.306(b)(2)(iv)'s risk-based control selection.
- **F-14 — No benefit-risk home for safety-tail HIPAA gaps.** F-2 (addressable-encryption rationale) and F-3 (emergency access / auto-logoff) are dispositioned as documentation items. But an addressable-spec decision is itself a risk-based determination (§164.306(d)(3) + (b)(2)(iv)) — "implement vs document-why-not" is a residual-risk-vs-burden trade, i.e. a benefit-risk/ALARP judgment under ISO 14971 §7. The threat-modeling WI's own escalation to a benefit-risk analysis (§4.6) cannot fire because no threat has been scored, and the Risk-Benefit Report it would feed does not exist.

## Worked example (before → after)

**Scenario:** the cloud-suite emergency-access spec (F-3).

*Before (compliance-only framing):* "§164.312(a)(2)(ii) is Required and we have no SRS row. Multi-tenant SaaS may rely on tenant-admin recovery, so document N/A." The decision is made on a *privacy/compliance* rationale, and the safety consequence is never weighed.

*After (bridge framing):* The hazard analysis carries a row — **Hazardous situation:** during an IdP/federation outage, an authorized clinician cannot reach the remote PCA-monitoring view. **Foreseeable sequence → harm:** delayed recognition of an evolving over-sedation/respiratory event on an opioid pump → `HARM-DPS-003` availability-during-use (S4), escalating toward `HARM-PRS-002` respiratory depression (S4). **Control:** audited break-glass emergency-access procedure (the F-3 SRS row), cross-referenced from the threat model's mitigation map. **Residual:** S×P scored per GL-STD-RM-001; if the team still elects "documented N/A," that N/A is now an **ALARP/benefit-risk determination** recorded in the Risk-Benefit Report — burden of a break-glass path vs the residual availability risk — not a privacy footnote. Same decision, but now traceable to a harm and defensible on the safety scale. This is exactly the single-sourcing F-12's precedence rule and F-14's benefit-risk home are meant to produce.

## Why this matters for THIS system

The PP3500 is an opioid-delivering PCA pump whose differentiator is connectivity. The SAD §7 maps ISO 14971 only to the on-device safety modules (M1 Therapy Control, M2 Safety Monitor, M3 Drug Library) — the classic mechanical hazard chains (occlusion, air-in-line, overinfusion). But the device's *new* risk surface is the telemetry/remote-monitoring path (M6 Cybersecurity & Comms) and the cloud concentration of ePHI — and that surface is where HARM-DPS-002/003/004 live. For an opioid pump, "loss of availability during use" and "telemetry corruption affecting a clinical decision" are not abstract privacy concerns; they are credible S4 chains toward respiratory depression. Leaving them out of the hazard file means the residual-risk and benefit-risk conclusions for the connected product are computed on the legacy mechanical surface only — understating the connected residual the program most needs to demonstrate it has thought through.

## Prescriptions

1. **Write the precedence rule first.** Add a reconciliation paragraph to `risk-strategy.md`: ISO 14971 is the single residual-risk authority; the §164.308(a)(1) HIPAA analysis is a CIA-scoped input; patient-harm items promote into the 14971 hazard analysis; no HIPAA acceptance overrides a 14971 unacceptable verdict. **Owner:** Risk Manager (+ Cybersecurity, Privacy/Regulatory). **Acceptance:** paragraph present and referenced by the F-4 artifact before that artifact is authored. (F-12)
2. **Populate the security→safety bridge.** Fill the three Rev-0.1 hazard analyses with the DPS-class chains — telemetry integrity loss → wrong clinical decision (`HARM-DPS-002`, S≤4); availability loss during use (`HARM-DPS-003`, S4); ePHI exposure (`HARM-DPS-001`, S3) — each with its cyber control cross-referenced from the threat model/SRS, residual S×P, and acceptance per GL-STD-RM-001. **Owner:** Risk Manager + Cybersecurity Lead. **Acceptance:** every HARM-DPS harm appears as ≥1 hazard row with a named control and an evaluated residual; same milestone as F-4. (F-11)
3. **Give emergency-access a harm anchor.** When the F-3 emergency-access SRS row opens, add the `HARM-DPS-003` availability hazard row with emergency-access as its control; permit "documented N/A" only if residual is shown acceptable without it. **Owner:** Risk Manager + Cloud-suite R&D + Cybersecurity. **Acceptance:** F-3 row traces to the HARM-DPS-003 hazard; N/A (if chosen) carries a residual justification. (F-13)
4. **Route safety-tail addressable/access decisions through benefit-risk.** Any F-2/F-3 item touching a HARM-DPS chain is dispositioned via the GL-STD-RM-001 §7 benefit-risk path and recorded in the (to-be-created) Risk-Benefit Report, cross-referenced with the HIPAA risk analysis so the residual verdict is single-sourced. **Owner:** Risk Manager + Cybersecurity + Privacy/Regulatory. **Acceptance:** each safety-tail addressable/emergency-access decision carries an ALARP rationale in one place; sequence after prescription 2. (F-14)

## Evidence base

- `docs/_analysis/pca-device/hipaa-readiness-profile/hipaa-readiness-profile.md` — Assertions A1–A12; findings F-1…F-14.
- `docs/internal/source-md/risk-management/master-harms-list.md` §3.8 — HARM-DPS-001 (S3), -002 ("up to 4 if affects clinical decision"), -003 (S4), -004 (S4).
- `docs/internal/source-md/software-cybersecurity/cybersecurity-sop.md` §6.4 — threat-model outputs feed Hazard Analysis; cyber hazards merge into safety-risk tracking where they can lead to patient harm.
- `docs/internal/source-md/software-cybersecurity/threat-modeling-wi.md` §4.5 (attack-tree for S=4/5 harms), §4.6 (residual + acceptance per GL-STD-RM-001; Unacceptable → benefit-risk per §7).
- `docs/project/strategies/risk-strategy.md` — unassembled stub; "How cybersecurity risk feeds into overall risk" and "Risk/benefit determination approach" unwritten; Risk-Benefit Report named but absent.
- `docs/project/dhfs/{pca-device,cloud-suite,connectivity-adapter}/cybersecurity/GL-TMP-SW-002-threat-model.md` — Rev 0.1 DRAFT `{{}}` stubs; discovery index resolves `hazard_analysis: null` / `risk_management_plan: null` for all three DHFs.
- `docs/project/dhfs/pca-device/design-controls/architecture/pca-device-system-sad.md` §7 — ISO 14971 mapped to M1/M2/M3 only; M6 Cybersecurity & Comms carries the telemetry surface.
- **L1a:** `.claude/skills/medtech-docs/references/regulations/45-cfr-part-164.md` — §164.306(b)(2)(iv) / (d)(3); §164.308(a)(1)(ii)(A)-(B); §164.312(a)(2)(ii)/(iii). **L1b:** `docs/external/regulations/hipaa.md` §3–§4, §6 items 1–2/4.

## Cross-discipline open questions

| # | Question | Owner / advisor | Blocks |
|---|----------|-----------------|--------|
| RM-Q1 | Does pca-device firmware persist patient-identifiable events locally? If yes, telemetry/local-store CIA harms widen to the device tier (F-10/§164.310(d)). | pca-device R&D / cybersecurity | Scope of HARM-DPS rows in the pca-device hazard analysis |
| RM-Q2 | Is the F-4 HIPAA risk analysis a standalone artifact or a documented *view* of the ISO 14971 file? Determines whether the precedence rule (RM prescription 1) is a pointer or a merge. | Cybersecurity + Risk Manager | Sequencing of F-4 vs prescriptions 1–2 |
| RM-Q3 | What probability basis does the threat model assign cyber threats, and is it commensurable with GL-STD-RM-001's probability scale used for safety? Divergent P-scales reintroduce the F-12 divergence even with the precedence rule. | Cybersecurity + Risk Manager | Single-scale residual scoring (prescription 2) |
| RM-Q4 | Is HIPAA readiness purely procurement/BA-facing, or does any of this residual-risk narrative reach the FDA Q-Sub/510(k) cyber section? (F-7 audience routing.) | Regulatory Affairs | Where the Risk-Benefit Report's cyber-residual conclusion is filed |

## Counterpoints & considerations

- **"The hazard analyses are stubs across the board, so this isn't HIPAA-specific."** True — the empty risk file is a program-maturity gap, not a HIPAA gap. But the HIPAA readiness pass is the first lens that *surfaces* the DPS harms concretely (emergency access, telemetry integrity), so it is a legitimate forcing function even though the underlying fix is general. Frame prescription 2 as "populate the risk file, starting with the DPS chains," not "add a HIPAA annex."
- **"ISO-14971-governs is obvious — why spend a paragraph on it?"** Because the program is about to author a HIPAA risk analysis with its own scoring, and the un-stated default is that two analyses coexist. The cost of *not* writing the precedence rule is a divergent-record audit finding; the cost of writing it is one paragraph. Cheap insurance.
- **Severity-inflation risk.** HARM-DPS-002/003 carry "up to S4" qualifiers that depend on *whether* the compromise reaches a clinical decision. Populating the bridge must not reflexively score every CIA loss at S4 — the foreseeable-sequence discipline (is there a real path to a clinical decision/availability-during-use?) is what keeps the residual file credible. Over-scoring is as much a defect as the current under-representation.
