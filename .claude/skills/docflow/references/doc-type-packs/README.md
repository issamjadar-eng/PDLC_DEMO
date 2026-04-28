# Doc-Type Packs

**Status (2026-04-21)**: Phase A scaffold under task ben/089. Stubs only — populated in Phase E.

## Purpose

Each pack defines docflow's behavior for one document type. The doc-type classifier (`scripts/classify_doc.py`, written in Phase B) inspects the source file's path + filename + first-page probe and returns `(doc_type, pack_path, confidence)`. The orchestrator (`scripts/adopt.py`, written in Phase F) loads the matching pack to govern that adopt run.

A pack defines:

- **Required structural sections** for self-validation
- **Frontmatter type-specific aggregate fields** (e.g., `requirements:` for requirement docs, `hazards:` for risk docs)
- **Allowed/disallowed element behaviors** (e.g., trace-matrix forbids Mermaid emission entirely; form requires t-4 positional table handling)
- **Round-trip / round-back rules** specific to type

## Pack registry (canonical project taxonomy — matches existing frontmatter `doc_type` values)

The doc-type names below match the project's existing 122 adopted DHF MDs (validated by `scripts/classify_doc.py --self-test` at 95.1% script accuracy as of 2026-04-21).

### DHF doc types (16)

| Pack | Doc Type | Triggers | Notes |
|------|----------|----------|-------|
| `architecture.md` | architecture | `<dhf>/design-controls/architecture/`; `SAD`, `SDD` in filename | Mermaid heavy (image packs apply); the SAD/SDD pattern |
| `cybersecurity.md` | cybersecurity | `<dhf>/cybersecurity/`; covers threat models, SBOMs, CSRA, PSRA, vulnerability assessments, cyber management plans | `threats:`/`sbom:` aggregate |
| `vnv.md` | vnv | `<dhf>/design-controls/vnv/`; covers Test Protocols, Test Plans, Software Test Cases, Reliability Testing, Test Reports | Test-protocol shape; trace-back to requirements |
| `plan.md` | plan | `<dhf>/design-controls/plans/`; `<dhf>/risk-management/` for RMP; covers DDP, SDP, RMP, deployment/configuration plans | Phase gates, sign-off blocks, milestone tables |
| `report.md` | report | `<dhf>/design-controls/release-closure/`; covers SWR, SVI, SOD, Software Release, Open Defects | Status summary + tables |
| `form-instance.md` | form-instance | Filled-in form records (any folder); recognized by FORM-XXX prefix or "Worksheet"/"Inventory List"/"OTS_" patterns | Preserves field values from blank template |
| `requirement.md` | requirement | `<dhf>/design-controls/requirements/`; `SRS`, `FRS`, `NFR` in filename | R1 two-table per-requirement shape; CtX inference |
| `assessment.md` | assessment | `<dhf>/risk-management/`; covers Risk Assessment, Master Harms, Residual Risk, Benefit-Risk | Narrative + risk tables |
| `tool-validation.md` | tool-validation | `<dhf>/design-controls/tool-validation/`; IEC 62304 SDLC tool validation evidence | Tool validation packages |
| `hazard-analysis.md` | hazard-analysis | `<dhf>/risk-management/`; `Hazard Analysis` in filename | Hazard taxonomy + cause/effect chains |
| `trace-matrix.md` | trace-matrix | Risk-management trace matrices; `Software Traceability Matrix` in filename | Note: docs in `design-controls/trace-matrix/` are typically `form-instance` (filled-in trace matrix forms), not `trace-matrix` |
| `user-need.md` | user-need | `<dhf>/design-controls/user-needs/`; `URS`, `User Needs` in filename | Distinct from `requirement` — end-user perspective |
| `form.md` | form | Blank form template artifacts (rare in DHFs; e.g., `tool-validation/c-arm-video-stream-simulator/`) | Preserves blank field structure |
| `phase-closure-review.md` | phase-closure-review | Phase gate review minutes/records | Sign-off block structure |
| `fmea.md` | fmea | `<dhf>/risk-management/`; `FMEA`, `dFMEA` in filename | Multi-row failure mode tables |
| `other.md` | other | Fallback when no rule fires | Generic; flag-for-human-classification |

### QMS source-doc types (5) — for `docs/internal/source/` adoptions

| Pack | Doc Type | Trigger (definitive path) | Notes |
|------|----------|---------------------------|-------|
| `qms-sop.md` | qms-sop | `docs/internal/source/SOPs/` | Process-flow Mermaid (type-a); responsibilities table; revision history |
| `qms-form.md` | qms-form | `docs/internal/source/Forms/` | Blank-field preservation (X1 — `faithful` not `partial`); input-guidance preservation |
| `qms-wi.md` | qms-wi | `docs/internal/source/Work Instructions/` | Step-by-step procedural shape; screenshot-heavy (type-e ui-capture) |
| `qms-policy.md` | qms-policy | `docs/internal/source/Policies/` | Narrative-heavy; light tables |
| `qms-standard.md` | qms-standard | `docs/internal/source/Standards/` | External standards (ISO/IEC) adopted as reference |

### Other (1) — for clinical/postmarket docs (low-volume in this project)

| Pack | Doc Type | Trigger | Notes |
|------|----------|---------|-------|
| `clinical-doc.md` | clinical-doc | `<dhf>/clinical/`, `<dhf>/postmarket/` | CER/literature shape (low volume in current project) |

## Conventions

- Pack files are markdown with a YAML frontmatter block at the top declaring `doc_type`, `version`, `applies_to`, `required_sections`, `frontmatter_overlay`, `allowed_element_behaviors`, `disallowed_element_behaviors`.
- Each pack body is ≤150 lines. If a pack grows beyond that, consider splitting into sub-packs (e.g., `risk-doc-fmea.md` + `risk-doc-rmp.md`).
- Cross-references to mermaid packs and table packs use the form `mermaid-rule-packs/<name>.md` / `table-rule-packs/<name>.md` so the orchestrator can resolve them.

## Changelog

- 2026-04-21: README created during task ben/089 Phase A scaffolding.
