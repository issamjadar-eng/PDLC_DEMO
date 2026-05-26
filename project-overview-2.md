# SP6500 — Smart Pump Program Overview

**Program:** PainEase Smart Pump SP6500 — large-volume IV infusion pump with closed-loop drug-library and on-pump alarm intelligence
**Regulatory path:** 510(k) traditional — predicate SP6000 (K200111), De Novo declined in 2024 pre-sub feedback
**Last updated:** 2026-05-01

> _**Demo scope.**_ The SP6500 device identity, predicate (SP6000 / K200111), clearance numbers, KOL roster, and clinical evidence are **illustrative** for the PDLC_DEMO project. Every fabricated datum carries a `_Demo sample data — not for clinical use._` banner.

This document is the program-level view of SP6500: what we are filing, why the SP6000 predicate carries the substantial-equivalence weight, where the SaMD components sit relative to the filing scope, and how the cross-functional team executes day-to-day with agentic Claude Code tooling. A 16-slide pitch lives at [`project-overview-2.pptx`](project-overview-2.pptx) for the steering committee in 2 weeks.

---

## 1. Program at a Glance

### 1.1 What SP6500 actually is

SP6500 is a **large-volume single-channel IV infusion pump** with a 7" capacitive touchscreen, an on-pump drug library (formulary up to 5,000 entries), and a **predictive-alarm SaMD module** that reduces nuisance alarms by 38% in benchtop testing against historical SP6000 data. It is **not** a multi-channel pump and **not** a syringe pump — those are the SP6500-MC and SP6500-S product line variants, separately classified and separately filed.

The closed-loop title earned in early literature is misleading: SP6500 has **dose-error reduction** software, but the prescriber loop remains open — clinicians authorize each dose against the active formulary entry, the pump enforces the boundary. "Closed-loop" in marketing copy refers only to the pump's internal flow-rate control loop, not to a clinician-out-of-the-loop control system.

### 1.2 Filing scope at a glance

We are filing **one 510(k)** for the SP6500 hardware + firmware + Drug Library Manager (DLM) bundle, with an integrated PCCP that pre-authorizes drug-library updates and bounded firmware revisions.

- **Filing scope = SP6500 pump + DLM.** The Predictive Alarm Module (PAM) is a Class II SaMD accessory and is **out of the SP6500 filing**, scheduled for a separate 510(k) using SP6000-AlarmGuard (K215555) as predicate. The Cloud Sync Service (CSS) and Asset Tracking Service (ATS) are MDDS components, **out of scope** entirely.
- **Critical-requirement carve-out (CtS / CtF / CtP).** Every user need and design input is tagged Critical to Safety / Function / Performance. Only Ct\*-tagged requirements are in scope for the 510(k); commercial features ship post-clearance on the marketing track.
- **PCCP envelope.** The PCCP pre-authorizes formulary updates against fixed acceptance criteria, firmware patches against the locked risk profile, and dose-error-reduction tuning that meets the bounded change protocol.
- **Predicate.** SP6000 (K200111) — direct technical predecessor in the same product family. The PCCP envelope plus the touchscreen UX update are the substantive deltas; clinical equivalence carries the rest.
- **PAM filing posture.** The Predictive Alarm Module is **outside** the SP6500 filing. Its own 510(k) sequences six months later, predicate AlarmGuard. This is a deliberate carve-out — bundling PAM would extend the SP6500 timeline by an estimated 9 months.

### 1.3 Key deliverables

1. **Q-Sub package** (`docs/project/sp6500/qsub/`) — pre-submission cover letter, device description, classification confirmation, PCCP scope questions for FDA pre-feedback.
2. **510(k) submission** (`docs/project/sp6500/510k/`) — substantial-equivalence argument to SP6000, software docs at IEC 62304 enhanced documentation level, performance and validation data, complete risk analysis, draft labeling.
3. **PCCP document** (`docs/project/sp6500/pccp/`) — three change categories (drug library, firmware patch, dose-error tuning), modification protocols, acceptance criteria, post-market reporting plan.
4. **Trace matrix** per DHF (`docs/project/dhfs/sp6500/design-controls/trace-matrix/`) — User Needs ↔ Design Inputs ↔ Architecture ↔ V&V ↔ Risk, with a **Filing Scope** column derived from Ct\* tags and a **PAM-or-pump** column carving the SaMD work.

---

## 2. Team & KOL Network

### 2.1 Core program team

The SP6500 program runs as a **cross-functional pod** with a single program manager driving cadence and the clinical voice carried by two practicing anesthesiologists embedded in design reviews.

- **Program leadership.** PM owns scope and calendar; clinical lead owns the use-case backlog; regulatory lead owns the FDA timeline.
- **Engineering execution.** Firmware, mechanical, and SaMD report into an R&D lead who chairs design reviews.
- **Quality + Risk.** QE owns the QMS evidence chain; risk-management lead owns the ISO 14971 file end-to-end.
- **Human factors.** A dedicated HF engineer runs formative testing in three sites; summative is contracted to a CRO under the program manager's oversight.

### 2.2 KOL persona advisors

KOL advisors run as **digital twins** in the agentic console — each persona has a curated knowledge corpus, opinionated review criteria, and a callable interface from any task that needs their voice during authoring.

| Advisor | Capability |
|---|---|
| `dr-okafor-anesthesia` | PACU & post-op pain anesthesiologist; reviews dose-error use cases and alarm tuning thresholds |
| `dr-shah-icu` | Critical-care intensivist; reviews concomitant-infusion and drug-library multi-drug interaction logic |
| `dr-park-pain-mgmt` | Outpatient pain management; reviews ambulatory PCA workflows and discharge-handoff flows |
| `dr-vega-surgical` | Cardiothoracic surgical anesthesia; reviews high-acuity dose-rate ramps |
| `dr-mendez-pediatric` | Pediatric anesthesia; reviews mg/kg dosing and pediatric-mode formulary curation |
| `dr-yamamoto-research` | Anesthesia research / academic medical center; reviews investigational-use pathway |
| `nurse-osborne-charge` | Charge nurse, 32-bed step-down; reviews shift-handoff alarm acknowledgment workflow |
| `nurse-rivera-icu` | ICU nurse, 18-bed mixed; reviews high-frequency titration use cases |

### 2.3 Investigator sites

We are recruiting four sites for the post-market clinical follow-up plan. Each site brings a different patient mix and care-setting profile.

| Site | Profile |
|---|---|
| Northshore Medical Center | Tertiary care · 800 beds · academic anesthesiology fellowship |
| Cascade Pacific Hospital | Regional · 320 beds · high-volume orthopedic surgical |
| Mercy Children's Health | Pediatric specialty · 200 beds · NICU + general peds |
| Ridgeline Surgical Institute | Ambulatory surgery center · 18 ORs · outpatient pain |

---

## 3. Risk & Quality Posture

### 3.1 Hazard register summary

The ISO 14971 hazard analysis identifies six high-priority hazards driving the V&V scope. Each carries documented residual-risk acceptance after control implementation.

- **Free flow on disconnect.** A break-away on the IV set could deliver an uncontrolled bolus. Controlled by a passive anti-free-flow valve plus active flow detection in firmware.
- **Drug library mismatch.** A drug entry mismapped to a wrong concentration could deliver 10× overdose. Controlled by a dual-witness library deployment workflow plus runtime concentration cross-check against the prescriber's order.
- **Alarm fatigue masking critical events.** Routine occlusion alarms could habituate clinicians, masking a true infiltration. Controlled by predictive-alarm module (PAM, separately filed) with a measured 38% nuisance-alarm reduction.
- **Battery depletion mid-infusion.** A depleted battery without grace-period warning could pause an active infusion. Controlled by 30-minute reserve + visual + audible escalating warnings starting at 60 minutes remaining.
- **Pump tampering during transport.** A jostled pump could drift the rate setting. Controlled by mechanical key-lock plus firmware setting-change audit trail.
- **Software defect introducing dose calculation error.** A regression in the dose-rate path could under- or over-deliver. Controlled by IEC 62304 enhanced documentation, automated regression suite, and field-failure telemetry feedback loop.

### 3.2 Quality system anchors

- **ISO 13485 design controls** govern every input → output → V&V → risk trace.
- **IEC 62304 enhanced documentation** required because PAM is Class C SaMD by safety classification.
- **ISO 14971 risk management file** integrated into the trace matrix as a first-class column, not an after-thought.
- **21 CFR 820 compliance** carries the QMS evidence chain end-to-end through design transfer and post-market.

---

## 4. Human-AI Handoff Pattern

### 4.1 Where the handoff actually happens

Authoring DHF documents in this program is **not fully automated** — it is a deliberate handoff between human judgment and AI execution at known stages. The boundary is documented, audited, and enforced via session hooks.

| Actor | Stage |
|---|---|
| Human · PM | Drafts the task brief and the success criteria |
| Agent · skill | Executes the structural authoring (templates, scaffolds, trace links) |
| Human · clinical | Reviews each dose-related design input for clinical acceptability |
| Agent · clinical-affairs | Generates KOL feedback summary from the digital-twin advisors |
| Human · regulatory | Approves substantial-equivalence argumentation before submission |
| Agent · vnv-lead | Drafts the V&V protocol from design inputs + risk file |

### 4.2 What we measured

> The 12 weeks of SP6500 design-input authoring with the agentic console produced equivalent IEC 62304 documentation in 38% of the calendar time of SP6000's equivalent phase, with reviewer-flagged clinical-correctness defects down 21%.

We attribute the speed gain to template execution (not to clinical judgment shortcuts) and the defect reduction to the always-on KOL persona reviewers catching ambiguous wording before human review.

---

## 5. What's Next

![Console landing](assets/project-overview/console-01-landing.png)

The next 90 days focus on closing the Q-Sub package and locking the predicate-comparison table for the 510(k). The console provides per-document drift detection and an always-on advisor drawer so reviewers can ground feedback against the exact authored version.

- Lock the predicate-comparison table by week 4.
- Submit Q-Sub package by week 8 with FDA pre-feedback target by week 12.
- Begin formative HF testing against the production touchscreen prototype in week 10.
- Open the post-market data plan with the four investigator sites by week 14.
