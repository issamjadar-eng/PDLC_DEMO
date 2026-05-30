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

| # | Assertion | Evidence (path / Jira key / clause) | Status |
|---|---|---|---|
| A1 | _e.g., "Every Hazard with `Potential Harms: Annoyance / Dissatisfaction` has `Severity: 1` in the joined FMEA source."_ | _e.g., `_jira/<arch>/<version>/hazards.json` + `_jira/<arch>/<version>/hazard-causes.json`_ | open / confirmed / refuted |
| A2 | _…_ | _…_ | open |

## Findings

_Each finding has a stable identifier (F-N), an evidence pointer, an impact statement (regulatory, safety, filing, schedule), and a resolution proposal._

### F-1: _short descriptive label_

- **What:** _the specific issue or gap_
- **Evidence:**
  - _path or Jira key, with the specific data point cited_
- **Impact:**
  - _Regulatory:_ _e.g., FDA reviewer would question the Class B determination_
  - _Safety:_ _e.g., real patient-harm hazard is under-scored_
  - _Filing:_ _e.g., the pre-authorized modification protocol cannot anchor to this hazard_
- **Resolution proposal:**
  - _Specific change recommended — update which Jira issue, which regulated artifact, what content_
- **Owner / next step:** _person + planned timing_

### F-2: _…_

_(repeat as needed)_

## Recommendations

_Concrete next actions distilled from the findings. Often: open a task, update a regulated document, escalate, file a Q-Sub question._

1. _e.g., "Re-score `JIRA-NNNN` Severity from 1 → 3 with a corresponding Hazardous Situation update in the FMEA source; reflect in the next mirror refresh."_
2. _e.g., "Add this finding to the Q-Sub `fda-questions.md` as a confirmatory question."_
3. _…_

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
