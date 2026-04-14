# Regulatory Strategy

<!-- Assembled: 2026-04-14 by /strategy assemble -->
<!-- Domain: regulatory -->
<!-- Sources: task 006 -->

> This document is auto-assembled from `<!-- STRATEGY CONTENT: regulatory, ... -->` tags in task documents.
> Do not edit directly — update the source task and run `/strategy assemble regulatory`.
> Unresolved items are marked with [VERIFY].
>
> **Structure**: Each level-2 section below is one **strategic topic**. Per-component nuance is carried as level-3 **callout subsections** (`### PCA Device`, `### Connectivity Adapter`, `### Cloud Suite`, etc.) nested under each topic. Callouts are optional — topics that apply uniformly across all DHFs don't need them. Authors: write source subsections in task docs using the same shape.

## Plans Informed

| Formal Plan | DHF | How This Strategy Informs It |
|------------|---------|------------------------------|
| 510(k) Submission | pca-device (lead) + per composition manifest | Filing pathway, predicate selection, submission structure, module scope |
| PCCP | as scoped per DHF | Change categories, modification protocols, which modules are covered |
| Q-Sub (Pre-Submission) | cross-DHF | Questions for FDA, predicted responses, classification validation |
| Lifecycle Management Report (LMR) | per DHF | Post-clearance change tracking cadence, reporting structure |

## 1. Device & Submission Overview

_Strategy decisions about what the device is, how it's submitted, and the overall filing approach._

### Filing Strategy — Critical-Requirement Carve-out (2026-04-14)

**Decision**: The PP3500 510(k) + PCCP filing is scoped to the **critical** subset of requirements. Every user need and design input is tagged with one or more of four criticality categories:

| Tag | Meaning | Examples (illustrative) |
|---|---|---|
| **CtS — Critical to Safety** | Failure can cause patient harm | Occlusion detection, air-in-line, dose limits, alarm priorities |
| **CtF — Critical to Function** | Failure breaks the core therapy | Pump motor control, bolus delivery, drug library enforcement |
| **CtC — Critical to Compliance** | Required by standard / regulation regardless of harm | IEC 60601 leakage, IEC 62304 SDLC, cybersecurity 524B, labeling |
| **CtP — Critical to Performance** | Failure degrades clinical performance below claimed spec | Flow accuracy, latency, alarm response time |

Requirements carrying **any** Ct* tag are **in scope for the 510(k) + PCCP**. Requirements carrying **none** of them are deferred — they continue development on the commercial track and ship post-clearance (PCCP-permitted updates, post-market changes, or next filing).

**Why**: Two pressures pull in opposite directions: regulatory wants the smallest, cleanest filing possible (faster review, narrower change-control surface, smaller PCCP envelope); commercial wants the full feature set at launch. The criticality carve-out resolves both — file the minimum necessary to be safe, functional, compliant, and performant; continue developing nice-to-haves in parallel and release them under the PCCP or as post-clearance updates. This also keeps the V&V burden on the filing tractable: only Ct* requirements need full design-controls rigor for the submission.

**How to apply**:
- Every UN and DI in the PCA device DHF gets one or more Ct* tags (or none, marking it commercial-only). Tagging happens in the existing user-needs.md / design-inputs.md docs.
- The trace matrix grows a "Filing Scope" column derived from the tags: `In 510(k)`, `In PCCP envelope`, or `Commercial-only`.
- The **PCCP envelope** is defined as: change types that touch Ct* requirements but stay within pre-specified bounds (drug library updates, firmware patches against a fixed risk profile, predictive-alarm SaMDs that meet the change-protocol acceptance criteria).
- V&V planning splits into two tracks: filing-scope V&V (Ct*-tagged requirements, full design-controls evidence) vs commercial V&V (everything else, internal QMS evidence only).
- Commercial-only features may still depend on Ct* infrastructure — tag accordingly and pull the dependency into the filing.
- Submission package composition manifest references the trace matrix's Filing Scope column as the authoritative inclusion list.

**Implications for downstream task work**:
- Tagging pass on the existing 22 UNs and 34 DIs is a follow-up task (candidate: a new 011 or fold into 006 closeout).
- The Drug Library Manager SaMD inherits the same tagging discipline — its own requirements get Ct* tagged for its own filing.
- Connectivity Adapter, being MDDS, is out of the Ct* tagging scope (no design-controls filing); its requirements live under QMS/cyber posture instead.

**Supersedes / refines**: The "PCCP scope" pending decision below — PCCP scope is now defined structurally (Ct*-tagged change envelope) rather than as a free-form list.

<!-- Source: task 006, "Filing Strategy — Critical-Requirement Carve-out (2026-04-14)", last modified 2026-04-14 -->

### Filing Scope: PCA Device Alone

**Decision**: The PP3500 510(k) submission (K210345) covers only the PCA device itself. The Connectivity Adapter and Our Cloud Suite are **not** part of the PP3500 filing. Each must be analyzed and filed (or not filed) on its own regulatory merits.

**Why**: The real K210345 clearance was obtained for the PCA device. The adapter and cloud suite are adjacent products whose regulatory classification depends on their specific functions (MDDS vs SaMD vs non-device software). Folding them into the PP3500 filing would couple unrelated regulatory paths and create unnecessary review burden.

**How to apply**: Any future strategy, plan, or filing scoped to PP3500 references only the PCA device DHF. Cross-cutting evidence (cybersecurity, interoperability) is pulled in via filing composition rather than by expanding the PP3500 DHF boundary.

<!-- Source: task 006, "Filing Scope: PCA Device Alone", last modified 2026-04-12 -->

## 2. Module Classification

_Per-module regulatory classification across jurisdictions._

### Component Classification & Filing Posture (2026-04-14)

**Decision**: The baseline regulatory architecture for the PP3500 program is:

| Component | Class / Type | Filing posture |
|---|---|---|
| **PCA Device (PP3500)** | Class II medical device | Own 510(k) **with PCCP**. PCCP scopes the post-clearance change envelope (drug library updates, firmware updates, predictive-alarm SaMD additions). |
| **Connectivity Adapter (on-prem)** | **MDDS** (non-device per post-2015 FDA reclassification) | Not separately filed. Identified in the PP3500 510(k) as adjacent infrastructure; QMS + cybersecurity evidence still produced. |
| **Cloud Suite — Drug Library Manager** | **Class II SaMD** (accessory to PCA; directly affects dose enforcement) | Own 510(k) (or bundled into PP3500 filing as accessory — TBD in submission planning). |
| **Cloud Suite — all other apps** (Fleet Mgmt, Telemetry, Surveillance, Update Distribution, Reg Data Pipelines, Customer Portals) | **Non-medical-device software** | Not filed. QMS, cybersecurity, and privacy still apply. |
| **Future AI/ML SaMDs** (predictive alarms, dose optimization) | Class II SaMD candidates | Out of baseline; introduced via PCCP or future filings. |

**Why**: This locks the regulatory architecture in one decision instead of dragging it through component-by-component classification debate. The PCA gets a PCCP because the post-market change pressure (drug library cadence, firmware, future ML) is the whole point of going modular. The Adapter as MDDS keeps it out of the device review path while preserving the cybersecurity story. Drug Library Manager has to be a regulated SaMD because it directly mutates the safety table the pump enforces — calling it anything else would be regulatory malpractice. Everything else in the cloud is non-device by function.

**How to apply**:
- The PP3500 510(k) submission package **identifies** the Adapter and Cloud Suite as named adjacent components (block diagram + classification rationale), and pulls in their cybersecurity assessments via composition manifest. It does not pull in their functional design controls.
- The PCCP scope must be drafted as part of the PP3500 filing (separate sub-task); covers drug library updates, firmware update mechanism, and the predictive-alarm SaMD pathway.
- Drug Library Manager gets its own DHF under `dhfs/cloud-suite/drug-library-manager/` and its own filing decision (accessory bundle vs standalone 510(k)) — flag for submission planning.
- Non-medical Cloud Suite apps still live under `dhfs/cloud-suite/<app>/` for QMS/cyber traceability but carry a "non-device" classification record instead of design controls.
- Connectivity Adapter DHF (`dhfs/connectivity-adapter/`) carries MDDS classification record + cybersecurity assessment; no 510(k) artifacts.

**Supersedes**: The earlier "classify each component case-by-case" framing in the Filing Scope and Classification Taxonomy sections above. Those sections still describe the *taxonomy*; this section is the *applied result* for the baseline.

<!-- Source: task 006, "Component Classification & Filing Posture (2026-04-14)", last modified 2026-04-14 -->

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

<!-- Source: task 006, "Classification Taxonomy for Adjacent Components", last modified 2026-04-12 -->

## 3. Jurisdictional Differences

_Key differences between US, EU, and Canada that affect the filing strategy._

_No strategy content assembled yet for this section._

## 4. Filing Sequence

_The order and rationale for multi-market submissions._

_No strategy content assembled yet for this section._

## 5. DHF & Design Planning

_Design History File structure, Design and Development Plans, deliverable scoping._

### DHF Filing Composition Pattern

**Decision**: Each top-level component (PCA device, Connectivity Adapter, Cloud Suite, and each individual Cloud Suite app) has its **own DHF** with its own design controls, risk file, V&V, and cybersecurity assessment. **Filings are not 1:1 with DHFs** — a filing composes from the relevant DHF pieces via a **composition manifest**.

Example: the PP3500 510(k) submission package includes the PCA device DHF in full, **plus** the cybersecurity assessments from the Connectivity Adapter and Cloud Suite DHFs (because the PCA's cybersecurity posture depends on everything that touches it), **plus** any interoperability evidence that affects the PCA. It does not pull in functional design controls from Adapter or Cloud.

**Why**: Modular DHFs let components evolve at different cadences, carry their own regulatory classifications, and be reused across multiple filings (e.g., a PCCP update to the PCA draws from a different slice than the original 510(k)). The composition manifest makes the reuse explicit and auditable.

**How to apply**:
- New top-level folder shape: `docs/project/dhfs/<component>/` for each DHF.
- Each DHF carries its own `design-controls/`, `risk-management/`, `clinical/` (if applicable), and `cybersecurity/` files.
- Each submission gets a `docs/project/submissions/<filing>/composition-manifest.md` listing which DHF pieces it pulls in and why.
- Strategy documents (`architecture-strategy.md`, `regulatory-strategy.md`, etc.) may need per-DHF instances; the `/strategy` skill's current single-output-path registry will need a revisit once DHFs are created.

<!-- Source: task 006, "DHF Filing Composition Pattern", last modified 2026-04-12 -->

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

<!-- Source: task 006, "DHF Folder Structure — Options Analysis", last modified 2026-04-12 -->

## 6. Document Reuse

_Which documents serve which filings, and jurisdiction-neutral vs. jurisdiction-specific guidance._

_No strategy content assembled yet for this section._

## 7. Pre-Market Strategy

_Prototype validation, phased launch, and pre-market evidence strategy._

_No strategy content assembled yet for this section._

## 8. Q-Sub Questions

_Pre-submission questions and predicted FDA responses._

_No strategy content assembled yet for this section._

## 9. Open Items

_Unresolved [VERIFY] markers and items needing human decision._

No `[VERIFY]` markers were found in assembled content.

### Pending Regulatory Decisions (from task 006)

These have been discussed but not yet resolved and are not yet in the strategy content above:

- Classification of each Connectivity Adapter function (MDDS vs non-device vs accessory)
- Classification of each Cloud Suite app (SaMD for Drug Library Manager; others TBD)
- Jurisdictional roadmap (US only, or EU MDR / Canada included)
- Predicate lineage beyond PP3000 — whether to cite secondary reference devices
- Initial Q-Sub question set
- Document reuse matrix from PP3000 → PP3500 submission
- PCCP scope for post-clearance changes (note: partially refined by the Critical-Requirement Carve-out decision in §1)

<!-- Source: task 006, "Pending Regulatory Decisions", last modified 2026-04-14 -->

## Uncategorized

_Subsections whose heading and topics did not match any output section in the topic-to-section mapping. If these accumulate, the mapping table in SKILL.md needs updating._

### Medtech-docs skill gap (follow-up, not in this task)

The `medtech-docs` skill was built for single-DHF projects. To support multi-DHF projects properly it needs:

- An `init` option that scaffolds the `dhfs/` container plus a per-DHF template
- A `new-dhf <name>` action to scaffold one DHF at a time
- A convention for what's shared (external/internal/input-analysis) vs per-DHF (design-controls/clinical/risk/postmarket/cybersecurity)
- Cross-link awareness — trace matrices and cross-DHF references need consistent path anchors
- Composition manifest scaffolding in the `submissions/` tree

This should be a new task (candidate task 008 or similar, after 007 task-close validator) — **not** something we do inside task 006. Recording here so the gap isn't forgotten.

<!-- Source: task 006, "Medtech-docs skill gap (follow-up, not in this task)", last modified 2026-04-12 -->

## Assembly History

_Append-only log of changes across assemblies. Most recent first._

### 2026-04-14 — assembled by benxavier-gl
- **Initial assembly** from task 006
- **Added**: Filing Strategy — Critical-Requirement Carve-out (task 006), Filing Scope: PCA Device Alone (task 006), Component Classification & Filing Posture (task 006), Classification Taxonomy for Adjacent Components (task 006), DHF Filing Composition Pattern (task 006), DHF Folder Structure — Options Analysis (task 006), Pending Regulatory Decisions (task 006), Medtech-docs skill gap (task 006)
- 8 subsections, 0 [VERIFY] markers, 1 Uncategorized

## Source Traceability

| Output Section | Source Task | Source Subsection | Last Modified |
|---------------|-----------|-------------------|---------------|
| 1. Device & Submission Overview | 006 | Filing Strategy — Critical-Requirement Carve-out (2026-04-14) | 2026-04-14 |
| 1. Device & Submission Overview | 006 | Filing Scope: PCA Device Alone | 2026-04-12 |
| 2. Module Classification | 006 | Component Classification & Filing Posture (2026-04-14) | 2026-04-14 |
| 2. Module Classification | 006 | Classification Taxonomy for Adjacent Components | 2026-04-12 |
| 5. DHF & Design Planning | 006 | DHF Filing Composition Pattern | 2026-04-12 |
| 5. DHF & Design Planning | 006 | DHF Folder Structure — Options Analysis | 2026-04-12 |
| 9. Open Items | 006 | Pending Regulatory Decisions | 2026-04-14 |
| Uncategorized | 006 | Medtech-docs skill gap (follow-up, not in this task) | 2026-04-12 |
