# Architecture Strategy

<!-- Assembled: 2026-04-14 by /strategy assemble -->
<!-- Domain: architecture -->
<!-- Sources: task 006, task 009 -->

> This document is auto-assembled from `<!-- STRATEGY CONTENT: architecture, ... -->` tags in task documents.
> Do not edit directly — update the source task and run `/strategy assemble architecture`.
> Unresolved items are marked with [VERIFY].

## Scope & Approach

_Project-level framing: what this strategy covers, which DHFs it spans, what decisions it records. Populated from the scope subsections of source tasks._

This shared architecture strategy spans every DHF in the PDLC_DEMO portfolio (PCA Device, Connectivity Adapter, Cloud Suite, and the Cloud Suite's nested DHFs). It records the cross-component architecture decisions — system context, component inventory, module/DHF topology, per-component callouts — that inform the per-DHF SAD, SRS, and cybersecurity plans. Per-component nuance is carried as level-3 callouts under each strategic topic.

## Plans Informed

| Formal Plan | DHF | How This Strategy Informs It |
|------------|---------|------------------------------|
| SAD (Software Architecture Description) | each DHF | Module boundaries, component topology, interfaces between DHFs |
| SRS (Software Requirements Specification) | each DHF | Architecture-driven requirements decomposition |
| Cybersecurity Plan | each DHF | Security architecture approach, trust boundaries, shared-secret strategy |

_The DHF column identifies which DHF each formal plan lives under — formal outputs remain per-DHF under `docs/project/dhfs/<dhf>/...` even though the upstream strategy is shared._

## Strategy Decisions

_Each strategic topic is a level-2 section. Per-component nuance is carried in level-3 callout subsections (`### PCA Device`, `### Connectivity Adapter`, etc.) nested under the topic. Callouts are optional — topics that apply uniformly across all DHFs don't need them._

### Decision 1 — All strategy domains are shared

**Decision**: Every domain in the `/strategy` registry has `scope: shared`. No more `per-dhf` scope type for strategy docs.

**Why**: Strategy is a cross-component story. A multi-DHF platform's regulatory filing strategy describes how pca-device, connectivity-adapter, and cloud-suite file together (predicate lineage, PCCP scope, jurisdictional sequence) — splitting it across three files fractures the story that the reviewer most needs to see whole. Same for architecture (platform boundaries span components), development (one SDLC, one CM plan), risk (platform-level hazard chains), testing (integration V&V cuts across modules), and postmarket (field surveillance is one program). The per-component specifics still matter — they live as callouts inside the shared doc, not as separate files.

**Superseded assumption**: Task 007's unified DHF shape correctly pushed design-controls, risk-management, postmarket, and cybersecurity down into `dhfs/<dhf>/`. It incorrectly applied the same logic to *strategy* docs — but strategy is a project-level artifact, not a component-level one. Formal outputs (SDP, SAD, V&V Plan, Risk Mgmt Plan, PMS Plan) still live per-DHF in the dhfs/ tree. Only the strategic **briefs** that inform those formal outputs move up to `docs/project/strategies/`.

<!-- Source: task 009, "Decision 1 — All strategy domains are shared", last modified 2026-04-13 -->

### Decision 2 — Topic-first structure with per-component callouts

**Decision**: Each shared strategy doc is organized by **strategic topic**, with per-component callouts nested under each topic. Not the other way around.

**Why**: Strategy is "one story per topic" — the filing pathway decision is a single decision that happens to express differently for each component, not three independent decisions that happen to share a filename. Topic-first keeps the cross-component tradeoffs adjacent so the reader sees the whole decision surface in one place. Component-first would fracture a single decision across three sections and make comparison impossible.

**Template shape** (applies to `default-strategy.md` and the custom `regulatory-strategy.md`):

```markdown
# <Domain> Strategy

## Scope & Approach
<project-level framing>

## <Strategic Topic 1>
<project-level framing of the topic>

### PCA Device
<component callout: how this topic applies to pca-device>

### Connectivity Adapter
<component callout>

### Cloud Suite
<component callout>

## <Strategic Topic 2>
...
```

Component callouts are optional per topic — some topics apply uniformly and don't need them. The topics themselves are domain-specific (regulatory has "Filing Pathway", "Predicate Lineage", "PCCP Scope", "Jurisdictional Roadmap"; architecture has "Platform Boundaries", "SaMD/SiMD/HW Split", "Interoperability", etc.).

<!-- Source: task 009, "Decision 2 — Topic-first structure with per-component callouts", last modified 2026-04-13 -->

### Decision 3 — `dhf=<leaf>` tag scope key is retired

**Decision**: The `dhf=<leaf>` scope key in `<!-- STRATEGY CONTENT: domain, dhf=<leaf> -->` tags is deprecated. Scanner no longer requires it for routing (every domain is shared → one file per domain regardless). Existing tags that still carry the key are tolerated (scanner ignores it); tags authored going forward should omit it.

**Why**: Shared scope means there's no ambiguity to resolve — every `architecture` tag lands in the one `architecture-strategy.md`. The key was only ever needed to disambiguate per-dhf routing.

**How to apply**: Scanner implementation drops the per-dhf validation branch. The tag grammar doc notes the key as deprecated-but-tolerated.

<!-- Source: task 009, "Decision 3 — `dhf=<leaf>` tag scope key is retired", last modified 2026-04-13 -->

### Open — System context (Step 1, current)

The infusion product is an ecosystem, not just a device. Agreed top-level components (2026-04-12):

1. **PCA device** (PP3500) — the pump itself, with embedded compute for therapy delivery, alarms, UI, local medication safety. Connects wired/wireless to the Connectivity Adapter.
2. **Connectivity Adapter** (on-prem) — GlobalLogic's own on-premises server. Single component (not two). Aggregates a fleet of PCA devices, distributes drug libraries, collects therapy logs and alarms, and translates to hospital IT systems via HL7 v2.5 and/or FHIR R4. Single on-prem footprint (no separate "local server" + "adapter"). Runs on-prem to keep PHI inside hospital boundary.
3. **Our Cloud Suite** — GlobalLogic's multi-app cloud platform hosting a series of apps and SaMDs: manufacturer-side fleet telemetry, analytics, predictive-alarm SaMDs, drug-library authoring tooling, software update distribution, regulatory data pipelines.
4. **Hospital IT systems** (external — not our product) — EHR, pharmacy system, identity provider, time source. We integrate via the Connectivity Adapter.

Not yet decided:

- **Patient / clinician companion apps** (nursing phone, patient app, biomed tablet) — in scope, deferred, or out?
- Whether the Connectivity Adapter talks to Our Cloud Suite directly, only via hospital network egress, or not at all in the cleared baseline

Decisions captured so far:

- **(a) Filing scope — RESOLVED (2026-04-12):** The PP3500 DHF / K210345 covers only the PCA device itself. The Connectivity Adapter and Our Cloud Suite are adjacent products and must be considered for their **own** regulatory paths. Each must be analyzed for whether it contains MDDS functions, SaMD functions, or non-device software, and filed (or not filed) accordingly.
  - Connectivity Adapter: likely contains MDDS-class functions (device data transfer, storage, display). May also contain regulated functions if it distributes drug-library payloads or enforces safety rules — those need classification case-by-case.
  - Our Cloud Suite: explicitly a mix of:
    - MDDS components (fleet telemetry, dashboards, data storage)
    - Non-medical-device software (analytics, regulatory data pipelines, internal tooling)
    - SaMD components (e.g., **drug library manager** — edits the library that the PCA device enforces, making it an accessory / SaMD with regulatory weight)
  - Rule of thumb adopted: nothing in Adapter or Cloud Suite rides on K210345; each component's classification stands on its own.

Remaining step-1 questions (resolve one at a time, in order):

- (b) **What's inside Our Cloud Suite? — RESOLVED (2026-04-12):** Seven baseline components, to be classified individually:
  1. Drug Library Manager (SaMD — pharmacist-authored library edits, directly affects PCA dose enforcement)
  2. Fleet Management (device inventory, registration, device-health)
  3. Telemetry & Analytics Dashboards
  4. Clinical Surveillance Apps (alarm analytics, near-miss detection)
  5. Software Update Distribution (firmware + library updates)
  6. Regulatory Data Pipelines (PMS, complaints, MDRs)
  7. Customer / Administrative Portals
  8. _Future_: AI/ML SaMDs (predictive alarms, dose optimization) — out of baseline, PCCP candidate
- (b.2) **DHF / modular architecture concept — NEW (2026-04-12):** Each top-level component gets its own DHF (or "module") with its own design controls, risk file, V&V, and cybersecurity assessment. A **filing** is not 1:1 with a DHF — filings **compose** selectively from the relevant DHFs. Example: the PP3500 510(k) filing includes the PCA device DHF in full PLUS the cybersecurity assessments from the Connectivity Adapter and Cloud Suite DHFs (because the PCA's cyber posture depends on what touches it). This is the modular DHF pattern.
  - Implication for the folder scaffold: `docs/project/dhfs/pca-device/design-controls/` becomes the PCA device DHF specifically; we need new sibling branches for Adapter and Cloud Suite DHFs (and possibly sub-sub-modules for each Cloud Suite app).
  - Implication for the filing strategy: each 510(k) / MDDS / SaMD submission package gets a "composition manifest" listing which DHF pieces are included and why.
  - Implication for strategy harvesting: the `/strategy` skill's output paths currently point into `design-controls/` which is now the PCA-specific path. Other DHFs will need their own strategy instances.
- (c) **What's inside the Connectivity Adapter?** — same: list its functions, then classify each.
- (d) Trust and network boundaries: what flows over device↔adapter, adapter↔hospital-IT, adapter↔cloud? Where does PHI live?
- (e) Whether patient/clinician companion apps are in scope as a 5th top-level component.
- (f) What diagram shape goes into the strategy block (context diagram showing the 4 components + hospital IT boundary is my default).

Classification taxonomy (to apply once each component's functions are enumerated):

| Class | Rule of thumb | Regulatory implication |
|---|---|---|
| **SaMD** | Software intended for a medical purpose that performs that purpose without being part of a hardware device | Own 510(k) / De Novo / classification; accessory-to-device may inherit device class |
| **MDDS (non-device)** | Electronic transfer, storage, display, or conversion of medical device data without control or active patient monitoring; post-2015 mostly non-device per FDA | Not a regulated device; QMS and cybersecurity still apply |
| **Accessory to medical device** | Supports or extends the function of a cleared device | Classified by impact on the parent device; may require 510(k) |
| **Non-device software** | No medical purpose (internal tooling, regulatory data pipelines, business analytics) | No FDA oversight; still covered by cybersecurity and privacy |

Once all of the above are answered, we drill into each component individually.

<!-- Source: task 006, "Open — System context (Step 1, current)", last modified 2026-04-12 -->

## Open Items

_Unresolved [VERIFY] markers and items needing human decision._

No `[VERIFY]` markers found in current sources. Open architecture questions tracked in task 006 "Open — System context":

- Whether patient / clinician companion apps are in scope as a 5th top-level component (task 006, question (e))
- Whether the Connectivity Adapter talks to Our Cloud Suite directly, only via hospital network egress, or not at all in the cleared baseline (task 006)
- Trust and network boundaries — where PHI lives across device↔adapter↔hospital-IT↔cloud (task 006, question (d))
- Connectivity Adapter function inventory and classification (task 006, question (c))
- Context diagram shape for the strategy block (task 006, question (f))

## Assembly History

_Append-only log of changes across assemblies. Most recent first._

### 2026-04-14 — assembled by benxavier-gl
- **Initial assembly** from tasks 006, 009
- 4 subsections, 0 [VERIFY] markers

## Source Traceability

| Output Section | Source Task | Source Subsection | Last Modified |
|---------------|-----------|-------------------|---------------|
| Strategy Decisions | 009 | Decision 1 — All strategy domains are shared | 2026-04-13 |
| Strategy Decisions | 009 | Decision 2 — Topic-first structure with per-component callouts | 2026-04-13 |
| Strategy Decisions | 009 | Decision 3 — `dhf=<leaf>` tag scope key is retired | 2026-04-13 |
| Strategy Decisions | 006 | Open — System context (Step 1, current) | 2026-04-12 |
