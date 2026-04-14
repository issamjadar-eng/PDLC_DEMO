# 006 — PP3500 Architecture & Regulatory Strategy

**ID**: 006
**Created**: 2026-04-12
**Status**: Not Started (unblocked 2026-04-13 by tasks 007 + 009; authors into `docs/project/strategies/` shared docs with topic-first + per-component callout shape)
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: High

---

## Goals

_Establish the foundational architecture and regulatory strategy for the PP3500 (PainEase PCA Advanced) DHF. Capture decisions as tagged strategy blocks that the `/strategy` skill will harvest into the shared strategy docs at `docs/project/strategies/architecture-strategy.md` and `docs/project/strategies/regulatory-strategy.md` (all strategy domains are shared as of strategy skill v10 / task 009). Use the topic-first structure with per-component callouts (`### PCA Device`, `### Connectivity Adapter`, `### Cloud Suite`) — strategy describes how the DHFs relate to each other, not each one in isolation._

- Define module boundaries and SaMD / SiMD / HW split, grounded in the 9 functional groups (G1–G9) already established in the user-needs / design-inputs docs
- Capture key architectural decisions: platform, cybersecurity approach, data flow, interoperability, update mechanism, alarm priority scheme
- Establish the regulatory filing strategy: 510(k) pathway (already cleared K210345), predicate lineage, PCCP scope, jurisdictional roadmap, Q-Sub questions
- Tie architecture decisions to design inputs (DI-* IDs from the 34-item list) and regulatory decisions to the predicate/catalog data
- Produce two tagged strategy blocks (`<!-- STRATEGY CONTENT: architecture -->` and `<!-- STRATEGY CONTENT: regulatory -->`) that `/strategy assemble` can harvest

## Todos

- [ ] Discuss architecture strategy content scope with user
- [ ] Discuss regulatory strategy content scope with user
- [ ] Author `## Architecture Strategy` tagged block in this task
- [ ] Author `## Regulatory Strategy` tagged block in this task
- [ ] Run `/strategy assemble architecture`
- [ ] Run `/strategy assemble regulatory`
- [ ] Validate assembled docs with `/strategy validate`
- [ ] Update task 001 to reference 006 as the source of architecture/regulatory strategy decisions

## Context

Anchor product: **PainEase PCA Advanced (DEV-PP3500)**, Class II PCA infusion pump, 510(k) K210345 (cleared 2021-11-01), predicate K190567 (PP3000). Manufacturer: GlobalLogic.

Upstream material already in place (ready to ground strategy decisions):
- `../../docs/project/dhfs/pca-device/design-controls/user-needs/user-needs.md` — 22 UNs in 9 functional groups
- `../../docs/project/dhfs/pca-device/design-controls/requirements/design-inputs.md` — 34 DIs in 9 functional groups (Rev B)
- `../../docs/project/dhfs/pca-device/design-controls/trace-matrix/un-to-di-trace-matrix.md` — bidirectional UN↔DI matrix
- `../../docs/project/input-analysis/predicate-analysis/portfolio/DEV-PP3500_regulatory_info.md` — regulatory identifiers, product codes, UDI
- `../../docs/project/input-analysis/predicate-analysis/portfolio/DEV-PP3000_regulatory_info.md` — direct predicate
- `../../docs/project/dhfs/pca-device/postmarket/capa/CAPA-2023-001.md` — known post-market remediation arc (decimal-point)
- `../../docs/project/dhfs/pca-device/clinical/` and `../../docs/project/dhfs/pca-device/postmarket/` — 25 clinical + PMCF docs as context

## Architecture Strategy

<!-- STRATEGY CONTENT: architecture, system-context, system-components, boundaries -->

_To be authored step by step. We start at the system level — system boundary, component inventory, external integrations — before drilling into any one component's internals._

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

### Deferred — Detailed / module architecture (don't touch until system level is done)

_Everything below is premature thinking from an earlier turn. Do NOT turn into strategy content until the system-level picture above is agreed with the user. Keeping it here only so the thinking isn't lost._

- Module boundaries (G1–G9 mapping to runtime modules)
- SaMD / SiMD / hardware split inside the PCA device
- Compute architecture (MCU + SoC, safety gate between them)
- Cybersecurity controls (signed FW, TLS, RBAC, audit log, SBOM)
- Data architecture (internal event log, HL7 vs FHIR, cloud-or-not)
- Update mechanism (FW updates, library updates, PCCP foothold)
- AI/ML scope (out of baseline for K210345, future PCCP addition)

## Regulatory Strategy

<!-- STRATEGY CONTENT: regulatory, submission, classification, dhf, filing-composition -->

### Filing Scope: PCA Device Alone

**Decision**: The PP3500 510(k) submission (K210345) covers only the PCA device itself. The Connectivity Adapter and Our Cloud Suite are **not** part of the PP3500 filing. Each must be analyzed and filed (or not filed) on its own regulatory merits.

**Why**: The real K210345 clearance was obtained for the PCA device. The adapter and cloud suite are adjacent products whose regulatory classification depends on their specific functions (MDDS vs SaMD vs non-device software). Folding them into the PP3500 filing would couple unrelated regulatory paths and create unnecessary review burden.

**How to apply**: Any future strategy, plan, or filing scoped to PP3500 references only the PCA device DHF. Cross-cutting evidence (cybersecurity, interoperability) is pulled in via filing composition rather than by expanding the PP3500 DHF boundary.

### Classification Taxonomy for Adjacent Components

**Decision**: Adjacent product components (Adapter functions, Cloud Suite apps) are classified per the following four-class taxonomy before any filing decision is made:

| Class | Rule of thumb | Regulatory implication |
|---|---|---|
| **SaMD** | Software intended for a medical purpose, performing it without being part of a hardware device | Own 510(k) / De Novo / classification; accessory-to-device may inherit device class |
| **MDDS (non-device)** | Electronic transfer, storage, display, or conversion of medical device data without control or active patient monitoring; post-2015 mostly non-device per FDA | Not a regulated device; QMS and cybersecurity still apply |
| **Accessory to medical device** | Supports or extends the function of a cleared device | Classified by impact on the parent device; may require 510(k) |
| **Non-device software** | No medical purpose (internal tooling, regulatory data pipelines, business analytics) | No FDA oversight; still covered by cybersecurity and privacy |

**Why**: Cloud Suite is explicitly a mix — Drug Library Manager (SaMD), fleet management (likely MDDS), regulatory data pipelines (non-device software), etc. Component-by-component classification is the only way to avoid lumping them into a single filing decision. Post-2015 FDA MDDS reclassification means many data-transport functions are no longer regulated devices and should not be force-fit into a submission.

**How to apply**: For each component in the Adapter and each app in the Cloud Suite, produce a classification record (class + rationale + applicable rule) **before** deciding its filing path. The classification feeds the composition manifest.

### DHF Filing Composition Pattern

**Decision**: Each top-level component (PCA device, Connectivity Adapter, Cloud Suite, and each individual Cloud Suite app) has its **own DHF** with its own design controls, risk file, V&V, and cybersecurity assessment. **Filings are not 1:1 with DHFs** — a filing composes from the relevant DHF pieces via a **composition manifest**.

Example: the PP3500 510(k) submission package includes the PCA device DHF in full, **plus** the cybersecurity assessments from the Connectivity Adapter and Cloud Suite DHFs (because the PCA's cybersecurity posture depends on everything that touches it), **plus** any interoperability evidence that affects the PCA. It does not pull in functional design controls from Adapter or Cloud.

**Why**: Modular DHFs let components evolve at different cadences, carry their own regulatory classifications, and be reused across multiple filings (e.g., a PCCP update to the PCA draws from a different slice than the original 510(k)). The composition manifest makes the reuse explicit and auditable.

**How to apply**:
- New top-level folder shape: `docs/project/dhfs/<component>/` for each DHF.
- Each DHF carries its own `design-controls/`, `risk-management/`, `clinical/` (if applicable), and `cybersecurity/` files.
- Each submission gets a `docs/project/submissions/<filing>/composition-manifest.md` listing which DHF pieces it pulls in and why.
- Strategy documents (`architecture-strategy.md`, `regulatory-strategy.md`, etc.) may need per-DHF instances; the `/strategy` skill's current single-output-path registry will need a revisit once DHFs are created.

### DHF Folder Structure — Options Analysis

**Context**: The current scaffold was generated by `/medtech-docs init` which assumes a single-DHF project: everything for one product lives under `docs/project/{input-analysis, design-controls, clinical, postmarket, submissions}/`. That doesn't account for the modular DHF pattern we just adopted. Our PP3500 DHF content already sits in those top-level folders. We need to decide how to evolve the scaffold.

**Framing principle**: The project is ultimately about **filing**. We will file one thing at a time (e.g., PP3500 alone), but the evidence behind each filing is composed from multiple DHFs. The folder structure must make this composition explicit.

**Option A — Full migration to `dhfs/` tree (cleanest, most work)**

```
docs/project/
├── dhfs/                               ← NEW top-level container
│   ├── pca-device/                     ← PP3500 content moves here
│   │   ├── design-controls/
│   │   ├── clinical/
│   │   ├── risk-management/
│   │   ├── postmarket/
│   │   └── cybersecurity/
│   ├── connectivity-adapter/
│   │   └── (same structure, empty for now)
│   └── cloud-suite/
│       ├── drug-library-manager/       ← each a child DHF
│       ├── fleet-management/
│       └── (7 total)
├── input-analysis/                     ← stays shared (KOL, market, predicates)
├── external/                           ← stays shared (FDA, standards, frameworks)
├── internal/                           ← stays shared (corp SOPs, templates)
└── submissions/
    ├── K210345-pp3500-510k/
    │   └── composition-manifest.md     ← lists which dhfs/*/... pieces this filing pulls
    └── future-filings/
```

Pros: symmetric — PP3500 is a DHF like everything else; composition model is obvious; each DHF self-contained. Matches the filing-composition strategy cleanly.

Cons: migration — existing PP3500 content (22 UNs, 34 DIs, trace matrix, 25 clinical MDs, 2 synthesized postmarket files, all READMEs with cross-links) has to move into `dhfs/pca-device/`. Every relative path across those docs needs revisiting.

Effort: ~1–2 hours of careful file moves + cross-link updates, ideally delegated.

**Option B — Leave PP3500 in place, add `dhfs/` siblings for the new components (asymmetric)**

```
docs/project/
├── design-controls/          ← PP3500 content stays put (primary)
├── clinical/                 ← PP3500
├── postmarket/               ← PP3500
├── dhfs/                 ← NEW — only for non-PP3500
│   ├── connectivity-adapter/
│   └── cloud-suite/
└── submissions/
```

Pros: zero migration. Fast.

Cons: inconsistent — PP3500 is "primary in place" while everything else is "in a sub-folder." Mental model breaks. Future DHFs always feel second-class. The strategy skill's hardcoded output paths still work for PP3500 only. Tech debt compounds.

**Option C — Overlay: create `dhfs/` but leave PP3500 content where it is, with a symlink or pointer (hybrid)**

```
docs/project/
├── dhfs/
│   ├── pca-device/ → ../design-controls/   (symlink or README pointer)
│   ├── connectivity-adapter/
│   └── cloud-suite/
├── design-controls/          ← physical PP3500 content
├── clinical/
└── postmarket/
```

Pros: no physical file moves; the `dhfs/` entry for PP3500 is a pointer to its real location.

Cons: confusing — two valid paths to the same content; symlinks don't work everywhere; future readers won't know which is canonical. Tech debt from day one.

**Recommendation — Option A.** It's the only one that holds up long-term. Migration cost is contained (one delegated pass) and we do it now while the content is fresh and no real commits depend on the paths. B and C both accumulate debt that will bite when the second and third DHFs come online.

### Medtech-docs skill gap (follow-up, not in this task)

The `medtech-docs` skill was built for single-DHF projects. To support multi-DHF projects properly it needs:

- An `init` option that scaffolds the `dhfs/` container plus a per-DHF template
- A `new-dhf <name>` action to scaffold one DHF at a time
- A convention for what's shared (external/internal/input-analysis) vs per-DHF (design-controls/clinical/risk/postmarket/cybersecurity)
- Cross-link awareness — trace matrices and cross-DHF references need consistent path anchors
- Composition manifest scaffolding in the `submissions/` tree

This should be a new task (candidate task 008 or similar, after 007 task-close validator) — **not** something we do inside task 006. Recording here so the gap isn't forgotten.

### Pending Regulatory Decisions

These have been discussed but not yet resolved and are not yet in the strategy content above:

- Classification of each Connectivity Adapter function (MDDS vs non-device vs accessory)
- Classification of each Cloud Suite app (SaMD for Drug Library Manager; others TBD)
- Jurisdictional roadmap (US only, or EU MDR / Canada included)
- Predicate lineage beyond PP3000 — whether to cite secondary reference devices
- Initial Q-Sub question set
- Document reuse matrix from PP3000 → PP3500 submission
- PCCP scope for post-clearance changes

## Lessons Learned

<!-- LESSONS LEARNED: process, skill-usage, proactive-capture -->

### Proactively capture strategy and lessons during task work — do not wait to be asked

**Lesson**: When working through non-trivial decisions, strategy content and lessons learned must be captured in the active task document with the proper tags (`<!-- STRATEGY CONTENT: domain, topics -->` and `<!-- LESSONS LEARNED: category -->`) **at the moment the decision or lesson emerges**, not as a deferred cleanup pass and never only after the user asks.

**How it surfaced**: The user asked "did you capture them as strategies in our task doc?" while we were mid-discussion on architecture. The architectural working notes were under the strategy block (so scan would find them), but they were in discussion form, not decision form. Worse, several *regulatory* decisions — filing scope, classification taxonomy, DHF filing composition — were sitting in the architecture block instead of the regulatory block. The user then escalated: "I don't want to have to ask if you captured lessons learned or strategy." The proactive-capture behavior has to be a reflex, not a prompt-driven action.

**Applied fix**:

1. Saved feedback memory: `feedback_proactive_strategy_lessons.md` (personal, survives across sessions).
2. Added a bullet to `CLAUDE.md` → Working Conventions: _"Capture strategy and lessons as they happen."_ — project-wide rule loaded into every session's context.
3. Dogfooded the fix in this same task: the Regulatory Strategy block was cleaned up immediately, with each decision written as `### Heading` + **Decision**: + **Why**: + **How to apply**: — and this lesson was captured under `## Lessons Learned` in the same turn the correction landed.

**Root cause**: Task SKILL.md documents the Strategy and Lessons Learned sections as "optional" parts of the task template. That framing let me treat them as optional. They are not optional when real decisions or real lessons are present — they are mandatory in those cases. The CLAUDE.md rule now says so explicitly.

**Applies to**: All future task work in this project and any future project that inherits this CLAUDE.md rule, until the task skill itself is updated to promote these sections from "optional" to "required when decisions/lessons are present."

## References

| Ref | Description | Location |
|-----|-------------|----------|
| Strategy skill | Harvester that assembles tagged blocks into formal docs | `.claude/skills/strategy/` |
| Architecture brief | Awaiting-content stub at output path | `docs/project/strategies/architecture-strategy.md` |
| Regulatory brief | Awaiting-content stub at output path | `docs/project/strategies/regulatory-strategy.md` |
| Design inputs | Source of truth for module / requirement grounding | `docs/project/dhfs/pca-device/design-controls/requirements/design-inputs.md` |
| PP3500 regulatory info | 510(k), predicate, product code, UDI | `docs/project/input-analysis/predicate-analysis/portfolio/DEV-PP3500_regulatory_info.md` |

## Changelog

- 2026-04-12: Task created. Strategy briefs initialized via `/strategy init`. Task skeleton includes both tagged blocks (architecture, regulatory); content pending user discussion.
- 2026-04-12: User feedback — start architecture at the system level, not module/detailed level. Detailed thinking moved to a "Deferred" section under Architecture Strategy. New "System context" section opened as Step 1 of the architecture discussion, listing 5 candidate top-level components (PCA device, local server, on-prem adapter, cloud platform, hospital IT) and the open questions that need to be resolved before drilling into any one component. Regulatory strategy discussion is paused until system architecture is agreed, so the reg scope can match the system scope.
- 2026-04-13: **Blocked on task 007.** Decision to go with Option A (full migration to `dhfs/` tree) means the folder shape this task writes into doesn't exist yet. Task 007 created to perform the migration; this task will resume once 007 is complete, at which point the strategy content authoring will target `docs/project/dhfs/pca-device/design-controls/architecture/` and `.../plans/` instead of the current top-level paths. The pending regulatory and architecture decisions captured here (DHF shape, remaining step-1 questions) remain valid across the migration.
