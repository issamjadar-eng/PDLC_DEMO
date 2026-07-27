<!--
title: {{DEVICE}} - Predetermined Change Control Plan - 0.1.0
state: draft
confluence:
  space_key: ''
  parent_page_id: ''
  page_id: ''
  strip_internal: true
-->

<!-- AI-CHANGELOG — internal provenance of AI-assisted edits. Metadata only:
     NOT published downstream, NOT part of the controlled record, stripped on export.
| Date       | Task     | Summary                                              |
|------------|----------|------------------------------------------------------|
| {{DATE}}   | {{TASK}} | Initial full-PCCP scaffold from the submissions template. |
-->

<!-- VERSION CHANGELOG — metadata tier: NOT published downstream, stripped on export.
     NOTE: this comment-tier log does NOT satisfy the controlled change-history
     obligation — the filed Document Control header below carries the visible one.
| Date | Version | Author | Summary |
|------|---------|--------|---------|
| {{DATE}} | v0.1.0 (Draft) | {{AUTHOR}} | Initial scaffold. |
-->

<!-- AUTO:PAGE-TITLE -->
# Predetermined Change Control Plan — {{DEVICE}}
<!-- /AUTO:PAGE-TITLE -->

## Document Control 📤

_Visible controlled-record header (never 🔒-wrapped). Populate the sign-off chain from the project's governing submission WI/SOP._

| Field | Value |
|-------|-------|
| Document ID | `[VERIFY] assign per QMS (e.g., PCCP-0001)` |
| Version | v0.1.0 |
| Status | Draft |
| Effective date | `[TBD — gate: approval]` |
| Device | {{DEVICE}} |
| Submitter | {{SUBMITTER}} |
| Parent filing | {{FILING_SHORT}} (PCCP rides inside the marketing submission) |

**Approvals** (owner + date at sign-off):

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Author | `[TBD]` | — | _pending_ |
| Regulatory Affairs | `[TBD]` | — | _pending_ |
| Quality Assurance | `[TBD]` | — | _pending_ |
| _add roles per governing WI_ | | | |

**Change history** (visible controlled record):

| Version | Date | Author | Summary |
|---------|------|--------|---------|
| v0.1.0 | {{DATE}} | {{AUTHOR}} | Initial draft. |

## Terms 📤

_Define every filed-body acronym once (R7). Add rows as authored._

| Term | Definition |
|------|------------|
| PCCP | Predetermined Change Control Plan |
| SaMD | Software as a Medical Device |
| SAP | Statistical Analysis Plan |
| _…_ | |

## 1. Purpose and Scope 📤

This PCCP is filed with the {{FILING_SHORT}} for {{DEVICE}}. Upon authorization it pre-specifies a bounded set of modifications that may be implemented **without a new marketing submission**, provided each conforms to its Modification Protocol and passes the residual-risk acceptance gate. The PCCP comprises the three FDA-recommended components: **Description of Modifications** (§ 3), **Modification Protocols** (§§ 4–7), and **Impact Assessment** (§ 9), plus the required **Traceability table** (§ 8), performance criteria, change routing, post-market monitoring, and reporting. The intended use and indications for use are unchanged by every modification herein. `[VERIFY] confirm scope against regulatory-strategy + device description.`

## 2. Device and PCCP Scope 📤

Which functions/modules are in PCCP scope vs. out. `[VERIFY] pull classifications from project.yml dhfs[] — reference, don't redeclare.` State the guidance basis (AI/ML PCCP final for AI-enabled functions; General PCCP draft for non-AI). If a single unified document spans multiple modules, note that this is the sponsor's position (guidance constrains one authorized PCCP *version* per device — § V.F — not one *document*), pending FDA confirmation.

## 3. Component 1 — Description of Modifications 📤

Enumerate the pre-authorized modifications. Keep the set **few and specific** (General PCCP Guiding Principle 4). For EACH modification, author a full entry (do not defer to the § 8 table):

### 3.1 Required metadata (per modification)

| Metadatum | Value |
|-----------|-------|
| Implementation mode | automatic / manual / combination |
| Global vs. local | global (or local + local factors) |
| Expected update frequency | `[locked at design transfer]` |
| Labeling sections impacted | … |

### 3.2 Modification entries

**M1 — `<short name>` (`<AI-DSF | non-AI>`).**
*Pattern source: `[VERIFY] FDA guidance Example/Scenario`.*
Specific change; specific **rationale**; **post-modification performance specifications** (the characteristics/performance the device will have after the change); statement that intended use / indications / substantial equivalence are preserved. **Worked in full at §§ 5–7 and § 9** *(designate 1 AI + 1 non-AI exemplar to work end-to-end; prioritize a "hard shape" — imaging-equipment/input expansion, a real-time/latency-coupled function, or a computation-logic change where Data Management is not N/A).*

**M2 … Mn —** one entry each, same shape.

### 3.3 Explicit exclusions (generally not appropriate for a PCCP) 📤

List what is **not** pre-authorized (intended-use expansion, new patient population, new input modality/class, significant architecture change, new clinical risk profile, recall-driven changes, labeling shifts that change clinical positioning). Mirror this list in the § 10 routing tree.

## 4. Component 2 — Modification Protocol structure 📤

Every modification carries a four-sub-component Modification Protocol (AI/ML § VII.B(1)–(4); General § VII.B):
1. **Data Management Practices** — data sources, inclusion/exclusion, representativeness/covariate plan, reference-standard determination, train/tune/test independence + sequestration procedures, descriptive statistics, multi-reader sub-studies. *(State N/A explicitly where a change alters no data/computation.)*
2. **Re-Training / Update Methodology** — what changes; explicit update triggers; overfitting/bias mitigations; QMS linkage.
3. **Performance Evaluation** — the pre-specified **Statistical Analysis Plan** (see the § 5 worked SAP structure); acceptance criteria vs. cleared baseline **and** last-authorized version; subgroup analyses; regression; the unresolvable-failure statement.
4. **Update Procedures** — integrated-environment V&V; deployment; cybersecurity re-assessment; usability re-evaluation where UI changes; labeling + UDI; real-world monitoring; tested rollback.

§§ 5–6 work one AI + one non-AI exemplar end-to-end. § 7 states the ISO 14971 acceptance gate. The other modifications are authored to the same depth (or the set is deliberately narrowed — see [`references/pccp-full-document-structure.md`](../../../../.claude/skills/submissions/references/pccp-full-document-structure.md)).

## 5. Worked Modification Protocol — M1 (`<AI exemplar>`) 📤

### 5.1 Data Management Practices 📤
Data sources & cohort; inclusion/exclusion; **representativeness** (covariate plan: sex, age, race/ethnicity, disease severity, acquisition conditions — each numeric floor `[locked at design transfer]`); independence + **sequestration procedures**; reference-standard / ground-truth protocol (readers, qualifications, adjudication, uncertainty); per-dataset descriptive statistics.

### 5.2 Re-Training / Update Methodology 📤
Objective; what changes (freeze architecture, update coefficients only — the intended-use-preservation lever); update triggers (data-volume / drift / performance-deviation / cadence, thresholds `[locked at design transfer]`); overfitting + bias mitigations; QMS change-control linkage.

### 5.3 Performance Evaluation — Statistical Analysis Plan 📤
Author every SAP element (methodology now; numbers `[locked at design transfer]`):

| SAP element | Content |
|-------------|---------|
| Primary / secondary endpoints + hypotheses | … |
| Comparison vs. original **and** last-authorized version | dual comparison |
| NI / equivalence margin **+ clinical justification** | margin `[locked]`; justification prose **now** |
| Sample-size determination method | power, α, assumed effect size/SD → n (method now; constants `[locked]`) |
| Analysis population | … |
| Missing-data + outlier handling | … |
| Reference-standard-variability treatment | … |
| Subgroup / high-risk-subpopulation analysis | acceptance per subgroup |
| Sensitivity/specificity trade-off protection | … |
| Metrics + challenging/edge cases | … |
| Acceptance criteria vs. authorized-version criteria | … |
| Additional-testing determination (bench vs. clinical) | `[VERIFY] per-category; may be a Q-Sub question]` |
| **Unresolvable-failure statement** | failure recorded → modification NOT implemented; root-cause may permit re-test |

### 5.4 Update Procedures 📤
Integrated-environment V&V + impact on other functions; deployment criteria/timeline/mechanism; cybersecurity re-assessment; labeling + UDI; user communication; **tested rollback** (exercised at design transfer).

## 6. Worked Modification Protocol — M2 (`<non-AI exemplar>`) 📤

Same four sub-components, adapted for a non-AI change (Data Management may be N/A — state why; Performance Evaluation is usability/regression or computation-logic SAP as applicable). Work it to the same depth as § 5.

## 7. ISO 14971 residual-risk acceptance gate (all modifications) 📤

Passing Performance Evaluation is necessary but not sufficient. Before deployment, a documented residual-risk re-evaluation is recorded in the integrated risk file, scaled to the change class: **§ 7.5** (does the change introduce new hazards / alter risk?), **§ 7.3** (each affected hazard's residual risk still acceptable?), **§ 8** (cumulative overall residual risk acceptable?). For AI changes, § 7.5 covers the AI hazard set (drift, out-of-distribution inputs, subpopulation underperformance, silent failure, model-version mismatch). Work a **before/after re-scoring** on the project risk matrix for at least the exemplars; trace the hazard set to the device hazard register. Acceptability thresholds resolve against the Risk Management Plan / QMS criteria.

## 8. Traceability table (Table 1) — REQUIRED 📤

Map each modification to the specific protocol components that govern it. This table is a required PCCP element (AI/ML § VII.C) and doubles as a completeness tracker (stub cells expose un-worked protocols).

| Modification | Data Management | Re-Training / Update | Performance Evaluation (SAP) | Update Procedures | Impact Assessment |
|--------------|-----------------|----------------------|------------------------------|-------------------|-------------------|
| M1 | § 5.1 | § 5.2 | § 5.3 | § 5.4 | § 9 |
| M2 | § 6 (N/A?) | § 6 | § 6 | § 6 | § 9 |
| … | | | | | |

### 8.1 Performance-criteria index (all modifications) 📤

At-a-glance acceptance patterns across the set — an **index over** the per-modification protocols, not a substitute for them. Numbers are `[locked at design transfer]`; each references a `[cleared-baseline, locked at design transfer]` reference point.

| ID | Change | Primary acceptance pattern | Threshold | Evidence artifact |
|----|--------|----------------------------|-----------|-------------------|
| M1 | … | improvement + non-inferiority | `[locked]` | `[named test protocol — TBD, owner, gate]` |
| M2 | … | … | `[locked]` | `[named]` |

## 9. Component 3 — Impact Assessment 📤

For every modification and for the set (AI/ML § VIII):
1. Each modification vs. the unmodified device.
2. **Benefits and risks (incl. bias) of each individual modification** — a worked benefit-risk determination per modification (benefit named; risks incl. per-subgroup bias; acceptability conclusion in light of benefit).
3. How the Modification Protocol's V&V ensures continued safety/effectiveness.
4. **Interaction between modifications** — a pairwise screen; work the material couplings.
5. **Cumulative impact** — the method + **pre-specified aggregate thresholds** (stacked-change count, aggregate drift budget, accumulated subgroup-delta ceiling) that escalate to full re-baselining; against which baseline.
6. Impact on overall device functionality incl. non-AI functions, infrastructure, and any multi-function "other functions" boundary.

Cross-reference into the submission's populated risk assessment / MP sections. Work all six for at least the exemplars; carry a compact per-modification benefit-risk block for the rest.

## 10. Change Routing — PCCP / Letter-to-File / new submission 📤

The three-step decision tree (anchored in 21 CFR 807.81(a)(3) + the Oct 2017 software-changes guidance): (1) listed in an authorized category → PCCP (apply its Modification Protocol); (2) on the explicit out-of-scope list → new submission; (3) else, significant-effect test → new submission or Letter-to-File. A change matching an authorized category **must** route through the PCCP. `[VERIFY] name the project's internal memo-to-file WI/FORM for the Letter-to-File leg.`

## 11. Post-Market Monitoring 📤

Monitored signals; cadence per signal; ownership; subpopulation tracking (same covariates as the data-management plan); **rollback criteria + tested mechanism** (thresholds `[locked at design transfer]`); bias/performance disclosure; feedback to the post-market risk file (ISO 14971 § 10); periodic Risk Management Report (the cumulative-impact home).

## 12. Reporting to FDA 📤

What is filed (this PCCP, inside the marketing submission); change documentation (DHF + post-clearance change log); that a change to the **authorized PCCP itself** requires a new marketing submission (one authorized version per device, § V.F); deviation handling (CAPA + FDA notification per the Modification Protocol); continued MDR/complaint + periodic safety reporting.

---

<details>
<summary>🔒 INTERNAL — Open items & pre-transmission checklist</summary>

> **Reading convention.** 🔒 INTERNAL sections are working apparatus, never transmitted.

**Internal source mapping:** {{D_REG_REFS}}

**Pre-transmission checklist:**
1. Lock every `[locked at design transfer]` value from executed V&V (and Q-Sub feedback where applicable); if a demonstrative draft used representative sample values, swap them and remove the tags/banner.
2. Author all modifications' Modification Protocols to the exemplar depth (or narrow the set with FDA agreement).
3. Confirm draft-vs-final status of any General PCCP (non-AI) reliance.
4. Populate the cleared-baseline reference numbers the margins measure against.
5. **Reconcile against the transmitted Q-Sub** (if one was sent): every Q-Sub commitment (summary position, question framing, brief provision) has a home in this plan; nothing contradicts/narrows a transmitted position; no filed claim asserts an "FDA agreement" only requested. The transmitted document sets the floor. (Best run as a `quality-engineering` + `regulatory-affairs` agent walk over transmitted-Q-Sub × filed-plan — see the depth-contract reference.)
6. Confirm the commonly-missed required elements are present: data-governance back half (storage/retention/QA/anti-tampering/human-subjects); baseline labeling PCCP+ML disclosure; per-modification methods-comparison statement; user-visible version display; labeling-review-before-update; the public 510(k)-summary PCCP content (in the 510(k)-summary doc).
7. Run `/reference-audit` over every guidance §, Appendix example, K-number, and standard clause against the byte-correct source (rung 3) — not the distilled finding-aid.
8. Run the authoring lint (`/regulatory-authoring lint`) + copy-editor + QA-conformance passes.

**🔒 END INTERNAL**

</details>
