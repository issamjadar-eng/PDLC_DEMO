---
source_file: "N/A — authored-in-markdown"
source_path: "pca-device/risk-management/GL-TMP-RM-004-design-fmea.md"
doc_id: "PCA-DEVICE-GL-TMP-RM-004-design-fmea"
doc_type: "QSD"
title: "Design FMEA (dFMEA) — pca-device"
format: "md"
conversion_date: "2026-04-21"
conversion_method: "claude-authored"
conversion_fidelity: "faithful"
pages: null
sheets: null
has_images: false
image_count: 0
has_tables: true
has_form_fields: true
references:
  - doc_id: "GL-TMP-RM-004"
    title: "Parent QMS template"
    resolved: true
    match: null
    note: "ISO 14971 §5; IEC 60812"
conversion_history:
  - date: "2026-04-21"
    source: "v0.1 DRAFT — placeholder stub via task ben/023"
  - date: "2026-07-14"
    source: "v0.2 DRAFT — FMEA backfilled under task ben/102"
notes: "dFMEA for PP3500 per GL-WI-RM-002 and GL-TMP-RM-004. 21 failure modes; S per GL-STD-RM-001 §3; Linked Hazard IDs reference the GL-TMP-RM-003 hazard analysis spine (HAZ-001…HAZ-016)."
---

<!-- AI-CHANGELOG — internal provenance of AI-assisted edits. Metadata only:
     NOT published downstream, NOT part of the controlled record.
| Date       | Task | Summary |
|------------|------|---------|
| 2026-07-14 | 102  | FMEA backfilled: failure modes, GL-STD-RM-001 S scale, Linked Hazard IDs to GL-TMP-RM-003 spine. |
| 2026-07-14 | 102  | QA-conformance pass: CONFORMANT; coverage-summary region wording corrected (action rows split ALARP/Acceptable). |
-->

# PCA-DEVICE-GL-TMP-RM-004-design-fmea — Design FMEA (dFMEA)

_Demo sample data — not for clinical use._

**DHF:** `pca-device`
**Parent QMS Template:** [`GL-TMP-RM-004`](../../../../internal/source-md/qms-index.md)
**Standards Anchor:** ISO 14971 §5; IEC 60812
**Revision:** 0.2 DRAFT
**Effective Date:** — (not released)

> Bottom-up design failure analysis of the PainEase PCA Advanced (PP-3500) per GL-WI-RM-002, methodology anchored in IEC 60812:2018. Each failure mode is analyzed at local, next-higher, and end-effect (patient/user) levels; every failure mode with patient-harm potential links upward into the top-down hazard analysis (GL-TMP-RM-003) via the `Linked Hazard ID` column. Prevention and detection controls cite the implementing design inputs (DHF-PP3500-DI-001) in parentheses where they exist.

---

## Identification

| Field | Value |
|---|---|
| FMEA Type | ☒ dFMEA ☐ pFMEA |
| Product / Process | PainEase PCA Advanced (PP-3500) |
| Revision | 0.2 DRAFT |
| Team | BX (Risk Management lead), Systems Engineering, R&D Firmware, R&D Electrical/Mechanical, Quality Engineering |

## Scoring Basis

- **Severity (S)** — GL-STD-RM-001 §3 five-level clinical-outcome scale (5 Catastrophic → 1 Negligible).
- **Occurrence (O)** — 1–5, using the GL-STD-RM-001 §4 probability anchors applied to failure-mode occurrence as a proxy. GL-WI-RM-002 §4 defers O/D scale definition to the product Risk Management Plan (GL-TMP-RM-001), which does not yet define FMEA-specific O anchors for this DHF [VERIFY — confirm O anchors when the PP3500 RM Plan is baselined].
- **Detection (D)** — GL-STD-RM-001 §9: D=1 (detected before harm) → D=5 (undetectable until harm occurs).

## FMEA Table

| FM ID | Item / Function | Failure Mode | Local Effect | Next-Higher Effect | End Effect (patient/user) | Cause(s) | Existing Prevention Controls | Existing Detection Controls | S | O | D | Linked Hazard ID | Recommended Action | Action Owner | Action Due | S' | O' | D' | Action Status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| FM-D-001 | Pump motor & drive train — deliver programmed flow | Uncommanded over-speed (runaway) | Motor stroke rate exceeds commanded rate | Delivered volume exceeds programmed rate/bolus | Opioid overdose — respiratory depression, death | Motor-driver FET short; encoder feedback fault; drive firmware command corruption | Closed-loop motor control with redundant encoder; flow-accuracy qualification (DI-001); dose-calc limits (DI-004, DI-005) | Independent delivered-volume supervision halts motor and annunciates over-infusion alarm within 60 s (DI-009) | 5 | 2 | 2 | HAZ-001 | — | — | — | — | — | — | — |
| FM-D-002 | Pump motor & drive train — deliver programmed flow | Chronic under-delivery (gear-train wear, missed steps) | Reduced stroke volume per cycle | Delivered volume gradually falls below programmed rate | Inadequate analgesia — uncontrolled pain requiring intervention | Gear-train wear over service life; stepper missed steps under load; cam surface degradation | Drive-train life qualification against flow accuracy spec (DI-001, DI-002); preventive-maintenance interval | Volume-deviation monitoring (DI-009); alarm threshold (±10 %/hr) may not catch 5–10 % chronic drift | 3 | 3 | 3 | HAZ-006 | Add periodic pump-accuracy self-test and cumulative delivered-volume trend alert; tighten PM wear criteria | R&D Mech Eng | 2026-Q3 | 3 | 2 | 2 | Open |
| FM-D-003 | Occlusion pressure sensor — sense downstream pressure | Output drift high (reads pressure above actual) | False high pressure signal | Spurious occlusion alarms; therapy interruptions | Alarm fatigue; delayed analgesia — discomfort, no direct injury | Sensor offset drift with temperature/age; amplifier bias drift | Sensor spec + burn-in; occlusion detection range qualified 3–15 psi (DI-007) | Power-on sensor zero check; nuisance-alarm trending via audit log (DI-034) | 2 | 3 | 2 | HAZ-008 | — | — | — | — | — | — | — |
| FM-D-004 | Occlusion pressure sensor — sense downstream pressure | Stuck at baseline / drift low (pressure rise not sensed) | Occlusion pressure rise not reported | Downstream occlusion undetected; no alarm | Therapy interruption without annunciation — untreated pain; post-occlusion bolus on release | Sensor element failure (stuck-at); disconnected/creased sensor coupling; drift below alarm threshold | Sensor selection and qualification per DI-007; design for positive mechanical coupling | Occlusion alarm response verification at 3 flow rates (DI-007); no in-service stuck-at diagnostic | 3 | 2 | 4 | HAZ-006 | Add in-service sensor plausibility self-check (dynamic signal / stuck-at detection each pump cycle) | R&D FW | 2026-Q3 | 3 | 2 | 2 | Open |
| FM-D-005 | Air-in-line ultrasonic sensor — detect air bubbles | Missed bubble (sensitivity degradation) | Bubble ≥50 µL passes undetected | Air delivered downstream without alarm (DI-008 limit not met) | Air embolism — life-threatening event | Transducer aging; acoustic coupling degradation; detection threshold drift | Sensor qualified at 50 µL single-bubble and 1 mL cumulative limits (DI-008) | Bench detection verification (DI-008); no in-service sensor self-test | 4 | 2 | 4 | HAZ-005 | Add automatic power-on and periodic air-sensor self-test against reference target; dual-window redundant detection | R&D EE | 2026-Q3 | 4 | 2 | 2 | Open |
| FM-D-006 | Air-in-line ultrasonic sensor — detect air bubbles | False air-in-line alarm | Air reported when none present | Spurious high-priority alarm; therapy pause | Alarm fatigue; brief analgesia interruption — discomfort only | Micro-bubble adhesion on tubing wall; sensor gain set conservatively; electrical noise | Detection threshold set per DI-008 with qualified margin; EMC immunity (DI-012) | Immediate annunciation to staff (DI-019); nuisance alarms trended via audit log (DI-034) | 2 | 3 | 1 | HAZ-008 | — | — | — | — | — | — | — |
| FM-D-007 | Anti-free-flow mechanism — block gravity flow when set removed | Spring fatigue — valve fails to close on set removal | Anti-siphon valve remains partially open | Unregulated gravity flow through administration set | Free-flow opioid bolus — overdose, respiratory depression, death | Spring material fatigue over cycle life; spring relaxation at temperature extremes | Anti-free-flow mechanism on dedicated set qualified to ≤0.1 mL/60 s (DI-006); spring cycle-life design margin | Free-flow bench test at design verification (DI-006); no in-service detection once set removed | 5 | 2 | 3 | HAZ-004 | Redesign spring for 2× cycle-life margin; add secondary mechanical flow-stop engaged by door-open interlock | R&D Mech Eng | 2026-Q4 | 5 | 1 | 2 | Open |
| FM-D-008 | Battery pack — sustain therapy on battery power | Premature depletion (cell capacity fade) | Runtime below 150 hr spec | Pump shuts down earlier than clinician expects | Therapy interruption — untreated pain until staff response | Li-ion cell aging; high-drain duty cycle beyond nominal profile | Battery endurance qualified ≥150 hr (DI-017); charge-time spec (DI-018); battery life on home screen (DI-021) | Staged low-battery alarms before shutdown (DI-019) | 3 | 3 | 2 | HAZ-007 | — | — | — | — | — | — | — |
| FM-D-009 | Battery charging circuit — recharge battery | Charge failure (charge-IC fault, connector damage) | Battery does not accept charge | Device unavailable or fails during next therapy period | Therapy delay/interruption — untreated pain in supervised setting | Charge-management IC fault; charging-port connector wear/damage | Charging performance qualified 0→100 % ≤4 hr (DI-018); connector cycle-life rating | Charging-status indication; low-battery alarms (DI-019); battery state on home screen (DI-021) | 3 | 2 | 2 | HAZ-007 | — | — | — | — | — | — | — |
| FM-D-010 | Battery fuel gauge — report state of charge | Gauge over-reports state of charge | Displayed SoC higher than actual | Unexpected shutdown with no or late low-battery warning | Silent therapy interruption — untreated pain; missed alarm window | Coulomb-counter drift without recalibration; gauge learn-cycle corruption | Fuel-gauge qualification across endurance profile (DI-017) | Low-battery alarm chain (DI-019) — compromised by the same gauge error; shutdown event logged (DI-034) | 3 | 2 | 4 | HAZ-007 | Add independent voltage-model cross-check of coulomb gauge; annunciate gauge-disagreement fault | R&D EE | 2026-Q4 | 3 | 2 | 2 | Open |
| FM-D-011 | Touchscreen — accept programming input | Ghost touch (phantom input events) | Uncommanded touch events registered | Therapy parameter field changed without user intent | Programming error — potential over-infusion if confirmed | Touch-controller fault; ESD transient; moisture film on screen after cleaning | Confirmation screen with explicit decimal confirmation before start (DI-013); hard limits block out-of-range values (DI-004, DI-005); cleaning-agent compatibility (DI-030) | Programming review screen requires active confirmation (DI-013); audit log of parameter changes (DI-034) | 4 | 2 | 2 | HAZ-002 | — | — | — | — | — | — | — |
| FM-D-012 | Touchscreen — accept programming input | Dead zone (region unresponsive) | Touch targets in affected region unusable | User cannot complete or adjust programming at bedside | Programming delay in supervised care — inconvenience, no direct harm | Touch-panel lamination defect; controller channel failure | Touchscreen functional qualification incl. touch response (DI-014) | User immediately perceives unresponsive control; service diagnostics (DI-031) | 2 | 2 | 2 | — | — | — | — | — | — | — | — |
| FM-D-013 | Display rendering — present dose values | Decimal-point rendering defect (glyph missing/illegible) | Decimal separator not legibly rendered | Displayed dose misread by 10× (e.g., 1.0 read as 10) | Programming confirmed at 10× intended dose — overdose | Font-asset corruption; rendering-pipeline defect at specific zoom/contrast states | Unambiguous decimal display + explicit decimal confirmation, contrast ≥4.5:1 (DI-013); summative usability validation of misread rate (DI-013, DI-020) | Display built-in test pattern at power-on; drug-library hard limits bound worst-case entry (DI-005) | 5 | 1 | 3 | HAZ-002 | — | — | — | — | — | — | — |
| FM-D-014 | Barcode scanner — verify medication against library | Misread/decode error matching wrong library entry | Scanned container resolved to wrong medication record | Wrong drug/concentration parameters loaded | Wrong-drug or wrong-concentration delivery — overdose or ineffective therapy | Symbol decode error on damaged/low-quality print; look-alike NDC entries | ≥98 % first-read qualification with mismatch blocking alert (DI-016); library hard limits cap programmable values (DI-005) | Blocking medication-mismatch alert (DI-016); clinician confirmation of drug name/concentration before start (DI-013) | 4 | 2 | 2 | HAZ-003 | — | — | — | — | — | — | — |
| FM-D-015 | Firmware dose engine — compute delivery parameters | Arithmetic overflow in dose/rate computation | Computed motor command incorrect | Delivered dose deviates from programmed values | Incorrect dose delivery — overdose potential | Integer overflow at boundary dose × concentration combinations; unit-conversion defect | IEC 62304 Class C lifecycle with boundary-value unit testing (DI-026); range/hard-limit validation on all inputs (DI-004, DI-005) | Independent delivered-volume supervision and over-infusion halt (DI-009) | 5 | 1 | 3 | HAZ-001 | — | — | — | — | — | — | — |
| FM-D-016 | Firmware watchdog — recover from processor hang | Watchdog fails to reset hung processor | Hung task not detected; no reset to safe state | Pump continues in undefined state or stalls silently without alarm | Uncontrolled delivery or silent therapy stop — overdose or untreated pain | Watchdog misconfiguration; watchdog serviced by the hung loop itself (kick from timer ISR) | IEC 62304 Class C design and code review of safe-state logic (DI-026) | Watchdog reset events logged (DI-034); no independent supervision of the watchdog itself | 4 | 2 | 4 | HAZ-001, HAZ-008 | Add independent hardware watchdog on separate supervisor IC with direct motor-power cutoff to safe state | R&D FW | 2026-Q3 | 4 | 1 | 2 | Open |
| FM-D-017 | Firmware drug-library loader — load active library | Corrupted library file accepted at load | Malformed limit records parsed into active library | Wrong hard/soft limits active for one or more medications | Programming beyond intended safe limits — overdose | Flash corruption; truncated transfer; library build error | Signed and integrity-checked library content (DI-024); library version displayed at home screen and therapy start (DI-015) | Load-time integrity hash rejects corrupt file (DI-024); library version recorded in audit log (DI-015, DI-034) | 4 | 2 | 2 | HAZ-003 | — | — | — | — | — | — | — |
| FM-D-018 | Speaker / annunciator — audible alarm output | Audio output failure (speaker open, amp fault) | No sound pressure produced | Audible alarms silent; visual-only annunciation remains | Delayed response to high-priority alarm — harm from underlying condition | Speaker coil open circuit; audio-amplifier failure; connector fault | Alarm system qualified to IEC 60601-1-8 SPL range 45–80 dB(A) (DI-019) | Power-on speaker self-test with fault annunciation; alarm events mirrored to EHR (DI-023) | 4 | 2 | 2 | HAZ-008 | — | — | — | — | — | — | — |
| FM-D-019 | Wi-Fi / EHR link — publish therapy and alarm events | Event message loss (network drop, buffer overflow) | Events not delivered to EHR endpoint | EHR therapy record incomplete or out of sequence | Clinical decisions on incomplete record — delayed or wrong intervention | Wi-Fi roaming drop (DI-022); send-buffer overflow during outage; endpoint misconfiguration | Store-and-forward event queue; HL7 interface qualified over 1000-event run (DI-023) | Device-side audit log retains all events for reconciliation (DI-034); link-status indication | 3 | 3 | 2 | HAZ-015 | — | — | — | — | — | — | — |
| FM-D-020 | Lockbox latch — secure drug cassette | Latch failure or tamper bypass | Latch does not hold or can be defeated without evidence | Unauthorized access to opioid cassette | Opioid diversion; patient receives tampered/depleted drug supply | Latch mechanism wear; misaligned strike; picking/prying attack path | Key/PIN-released tamper-evident latch, 50-cycle tamper qualification (DI-032) | Visible tamper evidence on inspection (DI-032); access events in audit log (DI-034) | 4 | 2 | 3 | HAZ-013 | Redesign latch with dual detent + electronic tamper switch logging open events to audit log (DI-034) | R&D Mech Eng | 2026-Q4 | 4 | 1 | 2 | Open |
| FM-D-021 | Housing & IV-pole clamp — mechanical support and protection | Housing crack or clamp release after drop/impact | Structural damage; device falls from pole | Loss of mounting; possible internal damage or fluid ingress | Device failure mid-therapy; falling-device impact injury | Drop/impact beyond design margin; clamp knob wear; over-torqued clamp cracking boss | Housing and mounting-interface qualification (DI-033); cleaning-agent compatibility avoids embrittlement (DI-030) | Visible damage on inspection; post-drop functional check per IFU; pump fault alarms if internals damaged (DI-019) | 3 | 2 | 2 | HAZ-016 | — | — | — | — | — | — | — |

**RPN consistency note:** RPN = S×O×D is used for prioritization only, per GL-STD-RM-001 §9 — final residual-risk acceptability is judged against the GL-STD-RM-001 §5 acceptance matrix (S and O used as the S,P proxy), not the RPN. Per GL-WI-RM-002 §4, D prioritizes mitigation effort and is never used to discount an unacceptable risk.

## Coverage Summary

| Metric | Value |
|---|---|
| Total failure modes | 21 |
| Modes with harm potential (end-effect S ≥ 3) | 18 |
| Modes linked to Hazard Analysis | 20 (all except FM-D-012; every S ≥ 3 mode is linked per GL-WI-RM-002 §5 step 7) |
| Unacceptable (per RM Plan criteria) — open | 0 (no (S, O) pair falls in the GL-STD-RM-001 §5 Unacceptable region) |
| Unacceptable — closed with evidence | 0 (none entered the Unacceptable region; 7 rows carry open recommended actions (RPN/detection-driven; 5 ALARP-region, 2 Acceptable-region)) |

## Approvals

| Role | Name | Date | Signature |
|---|---|---|---|
| | | | |

## Revision History

| Rev | Date | Author | Summary |
|---|---|---|---|
| 0.1 DRAFT | 2026-04-21 | Placeholder (task ben/023) | Stub created from QMS template. |
| 0.2 DRAFT | 2026-07-14 | BX / AI Assistant | dFMEA backfilled: 21 failure modes across drive train, sensors, power, UI, firmware, connectivity, and mechanical subsystems; scored per GL-STD-RM-001; linked to GL-TMP-RM-003 hazard spine; 7 recommended actions opened. |
