# 001 — Project Init

**ID**: 001
**Created**: 2026-04-12
**Status**: Completed
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: High

---

## Goals

_Stand up the PDLC_DEMO project as a working demonstration of agentic MedTech product development workflows, anchored on a general-purpose infusion device family._

- Initialize the repo, project manifest, and documentation scaffold
- Install the Hitachi skill registry (medtech-docs, task, docflow, strategy, tracker, lessons, best-practices, skill-creator) and the project-secops agent
- Populate starter standards, frameworks, and the three-tier docs hierarchy via `/medtech-docs init`
- Map the `../pdlc_sample_docs/docs/` sample corpus into the new scaffold (planned, not blind-copied)
- Produce a minimal `src/` placeholder for SaMD + pump firmware code
- Finalize functional modules and revisit requirements/architecture partitioning

## Todos

- [x] Clone Hitachi skills repo and install all 9 skills + project-secops agent
- [x] `git init` + set remote to `GlobalLogic-a-Hitachi-Company/PDLC_DEMO`
- [x] Write `project.yml` manifest (identity, team, registries, security)
- [x] Write `CLAUDE.md` with manifest reference section
- [x] Write `.gitignore` with PHI/credential patterns
- [x] Run `/medtech-docs init` to scaffold `docs/` (42 folders, 42 READMEs)
- [x] Populate applicable standards (IEC 62304, ISO 14971, IEC 62366-1, IEC 82304-1, IEC 81001-5-1, IEC 60601-1)
- [x] Populate applicable frameworks (NIST CSF, OWASP, NTIA SBOM, GMLP, HL7 FHIR)
- [x] Record exclusion rationale for DICOM, IHE, ASTM F2554, ISO 13485, 21 CFR 820, AAMI TIR57, ISO/IEC 23894
- [x] Install `register-hook.sh` + run `task` skill `setup` action (hook registered in settings.json)
- [x] Decide on functional modules — landed as the 9 functional groups G1–G9 in `design-inputs.md` Rev B (therapy delivery, drug library, alarms, hazard controls, UI, power/portability, connectivity, cybersecurity, regulatory)
- [x] Map `../pdlc_sample_docs/docs/` categories into `docs/` scaffold — Phases 3–7 executed (input analysis, design controls, V&V, clinical, postmarket). Phase 1 (FDA guidance) was superseded wholesale by task 012's `update-external-references` action.
- [x] First commit + push to origin/main — origin set, branch tracks `main`
- [~] ~~Create `src/` placeholder structure for demo code~~ — **Deprecated.** Architecture expressed via design-control SADs (`docs/project/dhfs/*/design-controls/architecture/`) rather than a code placeholder; the demo never needed illustrative `src/`.
- [~] ~~Generate initial `docs/dashboard.html` via `/medtech-docs dashboard`~~ — **Deprecated.** Dashboard concept replaced by `tools/project-console/` (task 003/008/015) and per-DHF `/trace-matrix` view (task 016). No static `docs/dashboard.html` is needed.

## References

| Ref | Description | Location |
|-----|-------------|----------|
| Hitachi skills | Source registry for all installed skills | `../hitachi/skills/` |
| Sample docs | Source corpus to be mapped into the scaffold | `../pdlc_sample_docs/docs/` |
| Skill SKILL.md | medtech-docs init action spec | `.claude/skills/medtech-docs/SKILL.md` |
| Project manifest | Identity, team, security policy | `project.yml` |

## Plan — Sample Doc Ingestion

Source: `../pdlc_sample_docs/docs/` — 18 categories, ~180 files (mix of FDA PDFs and authored markdown). Goal: selective, adapted ingestion into the three-tier scaffold. Nothing copied blindly; everything reviewed for relevance to the **PainEase PCA Advanced (PP3500)** as the DHF anchor product.

**Anchor decision (2026-04-12)**: PP3500 is the lead product. The sample design inputs (18 UN-/DI- files), 3 VER-PP3500 engineering studies, and the PP3000→PP3500 predicate chain all glue together naturally. The broader 5-device portfolio (IP5000, PP3000, PP3500, SP6000, SP6500) is retained as predicate/portfolio context, not as separate DHF streams. CLAUDE.md and `project.yml` reframed accordingly.

**SY2000 engineering studies** (7 files): held as **reference material only** — not imported into the PP3500 DHF. These may later be used as source patterns when authoring new sample engineering studies for the PCA (biocompat, electrical safety, bench testing templates). Quarantined under `docs/internal/source-md/reference-patterns/sy2000-eng-studies/` in Phase 5, not in the V&V stream.

### Inventory snapshot

| Category | Files | Type | Tier |
|---|---|---|---|
| 510k-assessment-policies | 1 PDF | FDA guidance | external/fda-guidance |
| Consolidated_Rules_Label_&_Marketing | 1 PDF | FDA framework | external/fda-guidance |
| EU_MDR_IVDDR | 1 PDF (CELEX 32017R0745) | EU regulation | external/standards (new EU subfolder) |
| Import_Export_Final_Guiances | 2 PDFs | FDA guidance | external/fda-guidance (low priority) |
| fda-final | 56 PDFs | FDA final guidance | external/fda-guidance (filtered) |
| fda-draft | 25 PDFs | FDA draft guidance | external/fda-guidance (filtered) |
| doc-templates | 11 MD | Authoring templates | internal/source-md/templates |
| design-inputs | 18 MD (UN-/DI- PP3500) | User needs + design inputs | project/design-controls/{user-needs,requirements} |
| engingineering-studies | 10 MD (VER- PP3500/SY2000) | V&V studies | project/design-controls/vnv |
| clinical-evaluation-plans | 5 MD (CEP-) | Clinical eval plans | project/design-controls/plans (clinical-eval) |
| clinical-benifit-risk-analysis | 10 MD (BRA-/LSS-) | Benefit-risk + lit | project/design-controls/risk-management |
| clinical-litature-search-strategies | 5 MD (LSS-) | Lit search | project/design-controls/plans (clinical-eval) |
| clinical-post-market-clinical-follow-up-plans | 5 MD (PMCF-) | PMCF plans | project/submissions (new postmarket subfolder) |
| clinical-post-market-clinical-follow-up-studies | 5 MD (STUDY-) | PMCF studies | project/submissions (postmarket) |
| company_devices_regulatory_filings | 9 MD (CONCEPT-/DEV-) | Internal device portfolio | project/input-analysis/predicate-analysis |
| kols | 8 MD + 1 PDF | KOL profiles | project/input-analysis/kol-feedback |
| labeling_rulesets | 3 MD (FDA/EU/HC) | Advertising rules | external/industry-frameworks (new labeling) |
| market-analysis | 4 PDFs | Market & competitive | project/input-analysis/{market-research,competitive-landscape} |

### Relevance filter (infusion device family)

**Keep** (FDA guidance directly relevant): Q-Sub (GUI00001677), Premarket Cybersecurity (GUI00001825), 510k eSubmission, DeNovo eSTAR, Off-The-Shelf SW, Computer Software Assurance, Premarket Software Functions, Predetermined Change Control AI + Draft PCCP, AI-Enabled Device SW Functions (draft), Physiologic Control (highly relevant — closed-loop infusion), Non-Invasive Remote Monitoring, Real-World Evidence, ASCA, Breakthrough Devices, GUDID, Electronic Product User Manuals, ISO 10993-1 Biocompat, Biocompatibility (draft), Chemical Analysis Biocomp (draft), 510k Sterility, Highest-Priority Devices for Human Factors Review (draft), Evidentiary Expectations 510k, Practices Predicate 510k, Recommendations Clinical Data 510k, Deciding When to Submit 510k for a Change, Credibility Modeling, VLPPI TPLC, Test Validation (draft).

**Defer / drop** (out of scope for infusion demo): all dental (cements, ceramics, handpieces, impression, implants, bone-grafting), LASIK, contact lens, MRI/x-ray/mammography/ultrasound/diathermy, COVID-specific guidances, atherectomy/PTA catheters, weight-loss, photobiomodulation, pulse oximeter draft, opioid use disorder, ortho coatings/patient-matched guides, in-vitro companion diagnostic, viral mutations, BSEP, LASIK, animal studies (dental).

Net: ~25–30 of the 81 FDA PDFs are in scope.

### Phased plan

**Phase 1 — External: FDA guidance triage** _(review gate before bulk copy)_
- Apply the relevance filter above; produce a final keep/drop list as a checklist
- Copy kept PDFs to `docs/external/fda-guidance/source/` preserving final-vs-draft distinction
- For each kept PDF, generate a `[VERIFY]`-flagged markdown stub via `docflow` (one-line purpose + applicability to infusion device)
- Add EU MDR (CELEX 32017R0745) under `docs/external/standards/eu-mdr/`
- **Review point**: confirm the keep list before any copy/convert operations run

**Phase 2 — Internal: doc templates**
- Copy `doc-templates/*.md` to `docs/internal/source-md/templates/` (already markdown — no docflow needed)
- Cross-reference templates against the standards already populated (IEC 62304, ISO 14971, IEC 62366-1) — note which template satisfies which clause
- **Review point**: confirm template scope vs. existing standards

**Phase 3 — Project: input analysis** _(market intelligence and predicate landscape)_
- `kols/KOL-*.md` → `docs/project/input-analysis/kol-feedback/` (8 profiles — adapt names if any are real practitioners; flag `[VERIFY]`)
- `kols/AI KOL Personality...pdf` → `docs/internal/source/` as methodology reference
- `market-analysis/*.pdf` → split: "Competitive Product Assessment" + "State of the Art" → `competitive-landscape/source/`; "Strategic Market...Infusion Therapy" → `market-research/source/` (highest value — directly infusion); "User Needs Assessment...Released Products" → `market-research/source/`
- Convert each via docflow; produce reviewable markdown
- `company_devices_regulatory_filings/*.md` → `docs/project/input-analysis/predicate-analysis/` — these become the in-house device portfolio that the demo device is positioned against (PP3500/PP3000 = legacy pumps; treat as predicates)
- **Review point**: confirm device-family naming convention before rebranding sample IDs

**Phase 4 — Project: design controls (user needs + requirements)**
- `design-inputs/UN-PP3500-*.md` (5 files) → `docs/project/dhfs/pca-device/design-controls/user-needs/`
- `design-inputs/DI-PP3500-*.md` (13 files, grouped FUNC/PERF/SAFE/USAB/INTE) → `docs/project/dhfs/pca-device/design-controls/requirements/` organized by category
- Build a stub trace matrix tying UN → DI in `docs/project/dhfs/pca-device/design-controls/trace-matrix/`
- Rebrand `PP3500` → demo device family name (deferred until Phase 3 review point lands)
- **Review point**: confirm requirement category structure (FUNC/PERF/SAFE/USAB/INTE) before bulk import

**Phase 5 — Project: V&V engineering studies**
- `engingineering-studies/VER-PP3500-*.md` (3 files — SW-002, SW-006, BT-005) → `docs/project/dhfs/pca-device/design-controls/vnv/`
- `engingineering-studies/VER-SY2000-*.md` (7 files) → `docs/internal/source-md/reference-patterns/sy2000-eng-studies/` as **reference-only** patterns (not part of PP3500 DHF)
- Group PP3500 VER records by study type (SW verification, bench testing) and link each to its DI in the trace matrix
- **Review point**: PP3500 V&V coverage is thin (only 3 studies). Flag the gap — the demo may later need synthesized additions (biocompat, electrical safety, EMC) modeled after SY2000 patterns

**Phase 6 — Project: clinical evaluation + risk**
- `clinical-evaluation-plans/CEP-*.md` (5) + `clinical-litature-search-strategies/LSS-*.md` (5) → `docs/project/dhfs/pca-device/design-controls/plans/clinical-evaluation/` (new subfolder)
- `clinical-benifit-risk-analysis/BRA-*.md` (5) + LSS duplicates → `docs/project/dhfs/pca-device/risk-management/benefit-risk/`
- Cross-link BRA to ISO 14971 risk management file
- **Review point**: are CEP/BRA/LSS document IDs internally consistent across folders? (LSS appears in two places — dedupe)

**Phase 7 — Project: post-market**
- Create `docs/project/dhfs/pca-device/postmarket/` (new top-level under project — not in current scaffold)
- `clinical-post-market-clinical-follow-up-plans/PMCF-*.md` → `postmarket/pmcf-plans/`
- `clinical-post-market-clinical-follow-up-studies/STUDY-*.md` → `postmarket/pmcf-studies/`
- Update `docs/README.md` and project tree to register the new branch
- **Review point**: confirm postmarket belongs under `project/` (vs. its own tier)

**Phase 8 — Labeling & EU regulatory**
- `labeling_rulesets/{FDA,EU_MDR,Health_Canada}_advertising_requirements.md` → `docs/external/industry-frameworks/labeling/` (new subfolder)
- `Consolidated_Rules_Label_&_Marketing/` PDF → same location, source/
- Decide whether EU MDR + Health Canada are in demo scope or excluded with rationale (the project is currently 510(k)-pathway focused)
- **Review point**: in-scope geographies for the demo

**Phase 9 — Adaptation pass** _(no rebranding — device IDs are preserved)_
- Add `_Demo sample data — not for clinical use._` banner to every imported file
- Add `[VERIFY]` markers wherever clinical numbers, citations, or KOL names appear
- Confirm CONCEPT-* devices (AI7000, AMB2500, NEO1200) remain quarantined as "concept evaluations" — not added to the active portfolio
- Update `docs/README.md` changelogs

### Execution order
Phases 1, 2 run independently. Phases 3–9 should run sequentially because each builds on the device-family naming decision made at the Phase 3 review point. Each phase ends at a review gate — the user signs off before the next phase begins.

## Changelog

- 2026-04-12: Task created. Completed: repo init, skill install, project.yml, CLAUDE.md, docs scaffold (42 folders/READMEs), standards + frameworks population, task-skill hook setup. Remaining: module list, sample-doc mapping, src/ placeholder, dashboard, first commit.
- 2026-04-12: Drafted phased ingestion plan for `../pdlc_sample_docs/docs/` (18 categories, ~180 files). Nine phases with review gates; relevance filter narrows 81 FDA PDFs to ~25–30 in-scope for infusion devices.
- 2026-04-12: Anchor product locked: **PP3500 (PainEase PCA Advanced)**. Demo reframed from "general-purpose infusion" to PCA pump. Updated `CLAUDE.md` and `project.yml` (device_family, lead_product, portfolio_context). 5-device portfolio retained as predicate/portfolio reference. SY2000 engineering studies quarantined as reference-only patterns (not imported into PP3500 DHF). Phase 9 rebranding step removed — device IDs preserved.
- 2026-04-12: **Phase 3 complete** — input analysis imported. 8 KOL profiles → `kol-feedback/` (KOL-0006 Paul flagged primary); 4 market PDFs → `market-research/` + `competitive-landscape/` with summary markdowns via Claude Read extraction; 9 device files → `predicate-analysis/{portfolio,concepts}/` (PP3500 lead, PP3000 predicate). Demo banner applied to 22 markdowns. `[Your Company Name]` → **GlobalLogic** swept across imports. All 4 folder READMEs updated with rosters and changelog entries. Phase 1 (FDA guidance) deferred at user request.
- 2026-04-12: **Phase 3 cleanup** — naming normalization applied to market summary MDs. `user-needs-traceability-released-products.md`: `IV5000` → `IP5000` (typo, same as FlexFlow Pro); `SY2000` and `AMB400` flagged as out-of-portfolio (neither matches any cleared GlobalLogic device). `state-of-the-art-analysis.md`: marketing names mapped to canonical device IDs; `PainEase Pro` normalized to `PainEase PCA (DEV-PP3000)`. Document-control convention recorded in Conversion Notes: MD is working-doc-of-record; source PDFs are starting-point artifacts, to be retired and regenerated from MD when a PDF is next needed.
- 2026-04-12: **Phase 4 draft complete** — user needs and design inputs authored as single tabular documents of record. `user-needs.md` (22 UNs) and `design-inputs.md` (34 DIs; by category FUNC 10 / PERF 2 / SAFE 10 / USAB 4 / INTE 8). Shared header block with device identity, 510(k), predicate, Intended Use, Indications for Use. Classification taxonomy: Category (FUNC/PERF/SAFE/USAB/INTE) orthogonal to Criticality (CTS/CTF/CTC/S). Sample corpus used as reference only; content adapted for realism. CAPA-2023-001 decimal-point remediation arc woven in via UN-007 and DI-013.
- 2026-04-12: **Phase 4 reorganized into 9 functional groups** — G1 Therapy Delivery, G2 Drug Library & Med Safety, G3 Alarms & Annunciation, G4 Hazard Controls & Essential Performance, G5 UI & Usability, G6 Power/Portability/Physical, G7 Connectivity & Interop, G8 Cybersecurity & Data Integrity, G9 Regulatory/Labeling/Lifecycle. `user-needs.md` and `design-inputs.md` both bumped to Rev B with H3 group sections and a Group column prepended to the tables. Content preserved verbatim; no text changes. UN distribution: G1 3, G2 3, G3 2, G4 2, G5 2, G6 4, G7 2, G8 1, G9 3 = 22. DI distribution: G1 4, G2 3, G3 4, G4 4, G5 4, G6 5, G7 2, G8 2, G9 6 = 34.
- 2026-04-12: **Trace matrix created** — `un-to-di-trace-matrix.md` (DHF-PP3500-TM-001 Rev A), bidirectional (UN→DI forward, DI→UN reverse), organized by the same 9 groups. 46 UN↔DI trace links total. Coverage: 22/22 UNs (100%), 34/34 DIs (100%), zero orphans. Avg 2.09 DIs per UN; avg 1.35 UNs per DI. Three folder READMEs (user-needs, requirements, trace-matrix) updated with current-contents tables and Phase 4 changelog rows.
- 2026-04-12: **Fixed arithmetic bug** in `design-inputs.md` Traceability Summary by-Category table: INTE row was `2|2|2|2|8` (incorrect) — actual counts `1|2|3|2|8`. Totals corrected from `14|13|4|3` to `13|13|5|3` (total 34 unchanged). Found by the reorganization subagent while building the by-group table.
- 2026-04-12: **Scaffold refactor — two new top-level branches**: `docs/project/dhfs/pca-device/clinical/` (evaluation-plans, benefit-risk, literature-search) and `docs/project/dhfs/pca-device/postmarket/` (pmcf-plans, pmcf-studies, capa, complaints). Option A adopted over burying clinical under design-controls; aligns with MedTech discipline boundaries and MDR/FDA lifecycle split. BRA placed under `clinical/benefit-risk/` (clinical benefit-risk determinations) with cross-link from `design-controls/risk-management/` (ISO 14971 hazard analysis).
- 2026-04-12: **Clinical + postmarket ingestion complete (replaces deferred Phases 6+7)** — 25 clinical MDs imported (5 CEP, 5 BRA, 5 LSS, 5 PMCF plans, 5 PMCF studies), each with YAML frontmatter schema (`doc_id`, `doc_type`, `device_ids`, `patient_populations`, `care_settings`, `therapy_context`, `evidence_grade`, `primary_endpoints`, `related_user_needs`, `related_design_inputs`, `status`, `last_updated`) and demo banner. `related_user_needs`/`related_design_inputs` left empty for the customer-insights agent to populate. All files tagged with `DEV-PP3500` since source docs use generic IDs.
- 2026-04-12: **Synthesized 2 postmarket records** to complete the customer feedback loop: `postmarket/capa/CAPA-2023-001.md` (decimal-point legibility CAPA, opened 2023-01-10, closed 2023-05-15, effectiveness verified — ties to DI-013 / UN-007 / FSN-2023-001 / software v1.2.4 and v1.3.0) and `postmarket/complaints/complaints-ledger.md` (27 complaints 2022–2025: 12 decimal-point pre-CAPA all linked to CAPA-2023-001 and 15 assorted post-fix; zero decimal-point complaints after May 2023 demonstrating CAPA effectiveness).
- 2026-04-12: **10 new READMEs authored** (clinical/ + 3 subfolders, postmarket/ + 4 subfolders, docs/project/README.md updated with the two new branches). Cross-links added to `design-controls/risk-management/README.md` → `clinical/benefit-risk/` and `predicate-analysis/portfolio/DEV-PP3500_regulatory_info.md` → `postmarket/capa/` + `postmarket/complaints/`.
- 2026-04-12: **Known follow-ups flagged**: (1) the 25 imported clinical MDs all reference generic `DEV-1001..1005` in body text — a future rebrand pass may normalize to PP3500-specific content; (2) complaints ledger mentions software v1.4.0/v1.4.1 which extend beyond the device_master_catalog's v1.3 — minor forward-looking inconsistency, acceptable for demo; (3) the `related_user_needs`/`related_design_inputs` frontmatter fields await population by the customer-insights agent.
- 2026-04-12: **Customer-insights domain agent split out to task 005.** The clinical + postmarket ingestion in this task prepared the source corpora and frontmatter schema; the agent design, spec, build, and population of `related_user_needs`/`related_design_inputs` + authoring of `insights-index.md` are scoped separately under `005-customer-insights-agent.md`.
- 2026-04-20: **Task closed.** Three of five remaining todos landed organically through downstream work (functional modules → 9 groups in Rev B design-inputs; sample-doc mapping → Phases 3–7 + task 012 absorbing Phase 1; first commit → origin live). Two remaining items deprecated: `src/` placeholder (architecture is expressed in SADs, not illustrative code) and `/medtech-docs dashboard` (replaced by project-console + /trace-matrix).

