---
id: {{ id }}
title: {{ title }}
status: draft                 # draft | review | accepted | superseded
component: {{ component }}    # arch_slug from project.yml (or system DHF leaf for cross-cutting)
topic: {{ topic }}            # one of: risk | regulatory | vnv | cybersecurity | clinical | human-factors | filing | postmarket | quality | software-architecture | systems-engineering
created: {{ today }}
last_updated: {{ today }}
authored_by:
{{ authored_by_block }}       # rendered as list: - human:<name> / - agent:<advisor-name>
grounded_against:
{{ grounded_against_block }}  # rendered as list of typed pointers
recommended_agents:
{{ recommended_agents_block }} # primary first, then consulting — from data/topic-advisor-map.yml
superseded_by: null           # set to another gap-analysis id when this becomes obsolete
---

# {{ title }}

## Goal of this analysis

_State the specific question or concern this gap analysis exists to answer. One paragraph._

- **Motivating question:** _e.g., "Are the Hazard severity scores consistent with the harm descriptions per ISO 14971 § 5.5?"_
- **Decision the analysis informs:** _e.g., "whether to escalate a specific mis-scoring to a Hazard re-review before the next submission milestone"_
- **Stakeholders:** _who consumes the findings (regulatory affairs, risk management, the program manager, …)_

## Expected methodology

_REQUIRED. State the expected technique set / methodology / framework against which the project's artifact will be critiqued. "Missing X" findings are unanchored opinion unless the expected set is declared up front. Default per-topic technique tables follow — extend or override for the specific analysis._

For risk-topic analyses, the expected technique union per **ISO/TR 24971:2020 Annex B**:

| Technique | Direction | Cause family it surfaces | Anchor |
|---|---|---|---|
| **PHA** (Preliminary Hazard Analysis) | Top-down brainstorm | Hazard families up front | ISO/TR 24971 § B.5 |
| **FMEA / dFMEA** | Bottom-up: component / function fault → effect | Single-fault, component-level failure modes | IEC 60812 |
| **FTA** (Fault Tree Analysis) | Top-down: hazardous situation → causes | Multi-fault paths, combinations of events | IEC 61025 |
| **HAZOP / STPA** | Deviation- or control-loop-driven | Interaction, integration, control hazards | IEC 61882; STPA Handbook |
| **URRA** (Use-Related Risk Analysis) | Task-analysis-driven | Use-error causes | IEC 62366-1 § 5.4 |
| **Threat modeling** | Adversarial | Cybersecurity causes | AAMI TIR57; FDA premarket cyber 2023 |
| **AI/ML failure-mode analysis** | Model-failure-driven | Drift, OOD, miscalibration, subgroup bias, silent failure | AAMI TIR34971:2023; FDA GMLP |

For other topics, declare the equivalent expected set:
- **vnv** — IEC 62304 § 5.6 / § 5.7; FDA "Content of Premarket Submissions for Device Software Functions"; ISO/IEC/IEEE 29119
- **cybersecurity** — AAMI TIR57:2016 / ANSI/AAMI SW96:2023 CIA + Authorization + Accountability axes; IEC 81001-5-1:2021; FDA "Cybersecurity in Medical Devices" (Sep 2023)
- **human-factors** — IEC 62366-1:2015+A1:2020 §§ 5.1–5.7; FDA "Applying Human Factors and Usability Engineering" (Feb 2016); AAMI HE75
- **clinical** — ISO 14155; clinical evaluation per MDR Annex XIV / MEDDEV 2.7.1 rev 4; FDA Q-Sub clinical-data expectations
- **regulatory / filing** — FDA submission guidance for the chosen pathway (510(k) SE, De Novo, PMA, PCCP); relevant product-code-specific guidance

State here whether the project artifact under analysis is expected to draw on the **union** across these techniques, or only a subset, and why. The methodology-critique findings (typically the "single-technique sourcing" / "missing-technique" / "wrong-technique-for-cause-family" findings) anchor to this declaration.

### What information lives at which layer (REQUIRED for `risk` topic; recommended for others)

Per the relevant standard, the quantitative ratings (severity, probability, controls, residual risk) live at a finer-grained layer than the parent concept (Hazard for ISO 14971; Use-error for IEC 62366-1; Threat for AAMI TIR57; etc.). The parent layer is a **taxonomic anchor**; the ratings live below it. Several downstream findings (mis-rating, missing dimensions, mitigation-chain gaps) depend on this layer model — declare it explicitly up front.

Render a layer table appropriate to the topic:

**For `risk` topic** (per ISO 14971 § 5.4 / § 5.5 / § 7.4 / § 8):

| Field | Lives at layer... | Why |
|---|---|---|
| Hazard statement (device-property label) | Hazard (parent) | Taxonomic; no score. |
| Unique harm set across children | Hazard (parent) | Categorical roll-up; tells the harm domain, not the magnitude. |
| Control-coverage status | Hazard (parent) | Aggregates child status. |
| Worst-case severity across children | Hazard (parent, derived) | Triage / dashboard sorting only — `max()` over children, NOT the hazard's severity. |
| Sequence of events / Cause description | Cause (sub-task) | One of potentially many causes per hazard. |
| Hazardous situation | Cause (sub-task — each cause leads to its situation) | Circumstance of exposure. |
| Harm (categorical) | Cause (sub-task — each situation leads to its harm) | A hazard can produce different harms via different causes. |
| Severity of harm | Cause (sub-task) | ISO 14971 § 5.5. Distinct per (cause × situation × harm). |
| P1 (sequence-of-events → situation) | Cause (sub-task) | ISO 14971 § 5.5. |
| P2 (situation → harm) | Cause (sub-task) | ISO 14971 § 5.5. |
| Risk controls | Cause (sub-task) | Map to specific (cause × situation). |
| Residual risk rating | Cause (sub-task) | ISO 14971 § 7.4. |
| Overall device residual risk acceptability | Risk Management Report (above hazard layer) | ISO 14971 § 8. Holistic, not aggregated severity. |

**For other topics**, mirror this pattern with the relevant standard's vocabulary (e.g., for `human-factors`: Use Specification / Use Scenario / Use-Error / Hazardous Situation / Harm — per IEC 62366-1 § 5.1-5.4; for `cybersecurity`: Threat / Attack Vector / Vulnerability / Impact — per AAMI TIR57 / SW96; for `vnv`: Requirement / Test Case / Test Result — per IEC 62304 § 5.6).

**Worked example.** Include at least one worked example using a real entity from the artifact under analysis — show a parent + 2-3 of its children with their distinct ratings, then explicitly list what rolls up to the parent (e.g., unique harm set, control coverage, worst-case severity) and what does NOT roll up (e.g., a single severity number, a single residual rating).

**Implications subsection.** Close with 2-4 operational consequences of getting the layer model right — typically how it affects the Jira/tooling projection, how it changes dashboard/sidecar rendering, and how it constrains where external risk-control claims can validly act.

### How artifact evolution relates to regulatory submission triggers (REQUIRED for `risk` / `regulatory` / `filing` topics)

A recurring source of confusion in regulated-device teams: does editing the risk file / hazard register / design history file trigger a new regulatory submission (510(k), De Novo, PMA supplement, MDR design-change notification)?

State the framework's answer up front for the team. For an FDA 510(k) program (adapt for other regulators):

- **No, not in itself.** Per ISO 14971 § 10, the risk file is expected to evolve through the lifecycle — adding causes, refining situations, updating mitigations as post-market data accrues is *required practice*, not a submission trigger.
- **The submission trigger is the change to the DEVICE, not the change to the DOCUMENTATION.** FDA *Deciding When to Submit a 510(k) for a Software Change to an Existing Device* (Oct 2017) and the parallel hardware-change guidance define this trigger as: changes that "could significantly affect safety or effectiveness" — typically a new function, a new indication, a change in clinical-risk profile beyond the cleared envelope, or (for AI/ML) a change in model input space / training scope / output behavior beyond what was cleared.
- **A cause added to refine a cleared hazard, or to document a newly-recognized failure mode within the cleared envelope, does NOT trigger a new 510(k).** It routes through the sw-changes decision tree and typically lands as Letter-to-File.
- **PCCPs convert per-change questions into per-change-type questions pre-authorized in advance.** Document where the pre-authorization envelope sits and what the cause-level implications are for changes within vs. outside the envelope.

**Render this as a change-routing table organized by submission cost**, not as a prose narrative. Three rows of categories:
- **Category A — Letter-to-File under BOTH traditional and PCCP** (PCCP adds no differential value): bug fixes, UI iterations that don't change function, post-market signal incorporation, vendor / SOUP swaps with equivalent function, performance optimization with identical outputs, refinements to existing risk controls. Volume is high but regulatory cost is low.
- **Category B — Traditional = NEW submission; PCCP-authorized = no submission** (PCCP's real value): the changes the PCCP modification categories explicitly cover. For AI/ML SaMD, typically model retraining, expanded training data, imaging-input expansion within pre-specified envelope, UI iterations that materially change AI-output presentation. Quantify the per-year saved-submission count at full operating cadence.
- **Category C — NEW submission under BOTH** (PCCP-blind): new indication / patient population, new clinical function, new modality, change from decision-support to autonomous control, fundamentally different AI model architecture, cross-module function expansion. PCCP doesn't help — the team needs a checklist for when a change-control discussion has to escalate.

Columns: example change (project-specific) | module / scope | under traditional → outcome | under traditional+PCCP → outcome | risk-file action | PCCP differential value.

After the table, include three short narrative subsections: (1) reading the differential — how many submissions does the PCCP envelope realistically save per year; (2) risk-management perspective — risk file evolves the same way under both, with the PCCP modification protocol pre-specifying data-management + acceptance criteria + post-market monitoring; (3) feature-update / engineering perspective — Category A doesn't change velocity; Category B changes velocity from "release every N months gated on FDA" to "release per protocol with monitoring"; Category C still requires full submission cycle. Close with the strategic question: "for any planned roadmap feature, is this Category A, B, or C — and if it's at the boundary, what design choice would keep it in the lower-cost category?"

## Source being analyzed

_What artifacts is this analysis grounded against? Mirror files, regulated artifacts, standards. Cite by path or stable ID — never duplicate the source content here._

### Primary sources

- _e.g., `docs/project/_jira/<arch>/<version>/hazards.md` — N Hazards (refresh date)_
- _e.g., `docs/project/_confluence/<arch>/product-overview/software-risk-assessment-sra/<version>.md`_

### Reference standards / external

- _e.g., `docs/external/standards/iso-14971-risk-management.md` § 5.4 (hazard identification) and § 5.5 (risk estimation)_
- _e.g., FDA guidance: "Content of Premarket Submissions for Device Software Functions"_

### Related context

- _e.g., predicate device analysis at `docs/project/input-analysis/predicate-analysis/...`_
- _e.g., KOL feedback synthesis at `docs/project/input-analysis/kol-feedback/...`_
- _e.g., prior task / decision document_

## Assertions

_Each assertion is a falsifiable claim about the project artifacts. The point of this section is to make hypotheses explicit so the analysis can confirm or refute them with evidence._

_Table columns (the renderer expects all five): `#` | `Assertion` | `Clause / decision` | `Evidence (path / Jira key)` | `Status`._

| # | Assertion | Clause / decision | Evidence (path / Jira key) | Status |
|---|---|---|---|---|
| A1 | _e.g., "Every Hazard with `Potential Harms: Annoyance / Dissatisfaction` has `Severity: 1` in the joined FMEA source."_ | _e.g., ISO 14971 §5.5_ | _e.g., `_jira/<arch>/<version>/hazards.json`_ | open / confirmed / refuted |
| A2 | _…_ | _…_ | _…_ | open |

## Assertion positions

_OPTIONAL. Per-advisor stance on each assertion — the substantive "who thinks the claim holds, and why" behind the single overall `Status`. When present, the project-console renders these as a click-to-expand detail beneath each assertion, with a Positive / Neutral / Negative icon and the note per advisor._

- **Stance vocabulary**: `positive` (advisor judges the claim holds / the artifact satisfies it) · `negative` (a real gap) · `neutral` (partial / depends / out of the advisor's lane).
- **Format**: one `### A<n>` subheading per assertion (matching the table `#`), then `- <stance> — <advisor>: <few-words note>` rows. Advisor names match the agents the analysis lists (e.g. the `recommended_agents` / fan-out advisors). Omit assertions that have no recorded positions.

```markdown
### A2
- negative — risk-management: severity score inconsistent with the harm described
- neutral  — regulatory-affairs: defensible if the harm taxonomy is clarified first
```

## Findings

_Each finding has a stable identifier (F-N), an evidence pointer, an impact statement (regulatory, safety, filing, schedule), and a resolution proposal._

**Coverage scope** _(state explicitly)_: _e.g., "All F-N findings analyze the in-scope artifact set only — [enumerate what is and is not in scope]. Items intentionally out of scope appear in the Recommendations section, not in Findings."_

### Summary table

Render this table **before** the detailed F-N sections so readers can triage by category / severity / effort without reading every entry. Especially valuable when fan-out produces 10+ findings and the reader needs to know "is this just administrative, or substantive?" at a glance.

**Category** taxonomy (project-agnostic — extend per analysis if needed):

- **Drift** — internal inconsistency between two project artifacts (e.g., artifact A says X, artifact B says Y; the inconsistency itself is the finding).
- **Manifest** — supporting-document / attachment / package-composition gap (administrative — no preliminary-position change required).
- **Substantiation** — claim needs better evidence/citation, or claim is overstated and should soften.
- **Coverage** — missing required commitment / dimension / hazard category / methodology in a preliminary position or deliverable.
- **Methodology** — process / methodology gap against the standard being audited (use when the issue is *how* the work was done, not *what* it claims).
- **Probe-preempt** — anticipated reviewer / auditor / downstream-stakeholder probe not addressed by the current artifact (preempting it strengthens the position).
- **Format/Tone** — authoring discipline against the framework / template / SOP (length, tone, attribution, density).

**Effort** estimate: **low** = single-paragraph wording edit / table reorder; **med** = new commitment paragraph requiring cross-team alignment; **high** = depends on a forthcoming brief / open project decision / external evidence gathering.

**Blocks-`<gate>`?** column — rename `<gate>` to the gate this analysis is feeding (e.g., "Blocks transmit?" for a submission-readiness analysis, "Blocks release?" for a design-transfer audit, "Blocks audit?" for an external-audit readiness review). "YES" = the package should NOT pass the gate until this is resolved.

**Multi-agent** column — when fan-out spawns multiple advisors, flag findings raised independently by 2+ agents as consensus (e.g., "RA + SE", or "**3-agent**"). Consensus findings tend to be the highest-confidence calls.

**Depends on** — name any other finding, recommendation, forthcoming brief, or open decision this finding's resolution depends on. Useful for sequencing.

**Status** column values — track resolution as edits land in the subject artifact:

- **open** (default — not yet addressed)
- **resolved** _YYYY-MM-DD_ (edit applied; note the date and reference the F-N detail block's `Resolution applied` paragraph for the diff summary)
- **deferred** (intentionally not addressing this round — capture rationale in the F-N detail's Resolution-applied paragraph)
- **superseded** (replaced by another finding — link the successor's F-N id)

When an F-N's status changes, **update both** (a) the row in this summary table and (b) the `Status` line at the top of the F-N detail block. Add a `**Resolution applied (YYYY-MM-DD)**:` paragraph at the bottom of the resolved F-N detail block summarizing the diff and citing the tracking task. Add a `Resolution progress: N / total` line below the table.

| # | Status | Short label | Artifact(s) affected | Category | Severity | Effort | Blocks `<gate>`? | Multi-agent | Depends on |
|---|---|---|---|---|---|---|---|---|---|
| F-1 | open | _e.g., Class drift between cover letter and project.yml_ | _e.g., cover-letter + manifest_ | Drift | high | med | YES | no | _decision X_ |
| F-2 | open | _…_ | _…_ | _…_ | _…_ | _…_ | _…_ | _…_ | _…_ |

**Resolution progress**: _N / total resolved. M open. P deferred. Q superseded._

After the table, add a **Headline reads** paragraph (3–6 bullets) calling out: (a) gate-blockers, (b) strongest multi-agent consensus, (c) administrative cheap-wins count, (d) substantive package-improvement count, (e) brief-gated count. This is the executive summary readers will skim before diving into F-N detail.

### F-1: _short descriptive label_

- **Status:** open _(open | resolved YYYY-MM-DD | deferred | superseded)_
- **Category:** _Drift | Manifest | Substantiation | Coverage | Methodology | Probe-preempt | Format-Tone_
- **Severity:** _high | med | low_
- **Effort:** _high | med | low_
- **What:** _the specific issue or gap_
- **Evidence:**
  - _path or Jira key, with the specific data point cited_
- **Worked example (before / after):** _REQUIRED. Concrete artifact fragment showing the current shape, then what the corrected shape would look like. Use the actual Jira keys / file paths / standard-clause anchors of this project — not generic "Item X" placeholders. Tables, mock JSON, ISO 14971 chain layouts (hazard → sequence → situation → harm) are all fair game. This is the most teachable content the analysis produces — do not omit._
- **Impact:**
  - _Regulatory:_ _e.g., reviewer would question the Class B determination_
  - _Safety:_ _e.g., real patient-harm hazard is under-scored_
  - _Filing:_ _e.g., the pre-authorized modification protocol cannot anchor to this hazard_
- **Resolution proposal:**
  - _Specific change recommended — update which Jira issue, which regulated artifact, what content_
- **Depends on:** _other F-N, R-N, forthcoming brief, or open decision_
- **Owner / next step:** _person + planned timing_
- **Resolution applied (YYYY-MM-DD):** _populate when status flips to resolved — summarize the diff (paths + line numbers) and cite the tracking task. Omit when status is `open`._

### F-2: _…_

_(repeat as needed)_

## Recommendations

_Concrete next actions distilled from the findings. Often: open a task, update a regulated document, escalate, file a Q-Sub question._

1. _e.g., "Re-score `JIRA-NNNN` Severity from 1 → 3 with a corresponding Hazardous Situation update in the FMEA source; reflect in the next mirror refresh."_
2. _e.g., "Add this finding to the Q-Sub `fda-questions.md` as a confirmatory question."_
3. _…_

## Cross-discipline open questions

_REQUIRED section. List the items this analysis needs from other disciplines to fully close — even if empty. Each item names the owning advisor/role for resolution. When `/gap-analysis fan-out` is used, this section is auto-aggregated across all sibling files into the aggregate's open-questions roll-up._

| # | Question | Owning discipline | Why blocked here |
|---|---|---|---|
| 1 | _e.g., "Does the harm taxonomy carry a tier above 'Additional surgery'?"_ | Risk Management | _the F-N rating depends on this schema decision_ |

## Self-review checklist

_REQUIRED before status moves from `draft` → `review`. Each box checked is an explicit attestation that the listed verification ran. Pass the checklist to the `/gap-analysis self-review <id>` action where available; otherwise check by hand._

- [ ] **Aggregate counts re-verified** against the source `.json` files (not just rendered `.md`), including any `_global/` sidecar / untagged-items files in the mirror's README "Computed fields" / "Untagged items" sections.
- [ ] **Every Jira-key / artifact-path claim re-grepped** in the mirror at analysis-write time.
- [ ] **Every standard-clause citation verified** for designation (CR vs TIR), year suffix, and superseded-by relationship — standards get reissued, citations rot.
- [ ] **Every "missing X" claim cross-checked** against the mirror's README + sidecar files for X — a coverage gap may be a tooling-projection artifact, not a real gap.
- [ ] **Internal consistency** — no two verdicts in the same file contradict each other; no aggregate count contradicts the per-finding detail.
- [ ] **Worked example** present under every F-N section (not just for the marquee findings).
- [ ] **Cross-discipline open questions** section present even if empty.
- [ ] **Standards-designation drift check** — for risk-topic files, AAMI TIR34971:2023 (not CR34971:2022); for cyber, ANSI/AAMI SW96:2023 (TIR57's successor); update the references list when standards reissue.

## Open Questions

_Questions this analysis could not resolve with the available data. Each should suggest what new evidence would close it._

- _e.g., "What was the original rationale for scoring `JIRA-NNNN` as Annoyance? — would need to review the original risk-review meeting notes."_

## References

_Inline citations consolidated. Useful for downstream consumers (filings, agent reports) that need to pick up the trail._

- **Jira keys cited:** _JIRA-NNNN, JIRA-MMMM, …_
- **Standards clauses:** _ISO 14971:2019 § 5.4, § 5.5; IEC 62304:2015 § 4.3.c; 21 CFR 820.30(g)_
- **Internal artifacts:** _SRA v2.0.0, HTM v2.0.0, dFMEA xlsx, system SAD § 5.5_
- **External:** _FDA guidance documents, predicate-device 510(k) numbers, published literature_

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| {{ today }} | {{ author }} | Initial draft scaffolded from `gap-analysis` skill template. |
