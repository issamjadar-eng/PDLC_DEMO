---
name: dhf-manifest
description: "DHF Manifest — 4-tier deliverable catalog that projects regulatory and QMS obligations through a project scope vector into per-DHF manifests with gap reports. Sibling to /trace-matrix (intra-DHF trace); this skill answers: are the right documents present and do they satisfy regulation + QMS?"
version: 9
updated: 2026-05-12
# v9 (advisor-grounding rollout): canonical-role catalog expansion (16 → 43 roles) + `multi_file: true` flag for folder-pointer artifact families. Resolver emits `{folder, exists, file_count, patterns_used}` for multi_file roles — same shape as `external_data` resolutions — so advisor researcher subagents can be given "look here, N files" hints. New roles span clinical (clinical_evaluation_plan/report, benefit_risk_analysis, literature_search, pmcf_plan, pmcf_studies), postmarket (complaints, capa, adverse_events, field_safety_corrective_actions, psur), cybersecurity (threat_model, sbom, cybersecurity_plan, vulnerability_management), risk additions (fmea, risk_management_report), design-controls additions (user_needs, software_requirements, software_design_specification, verification_plan, verification_protocols, verification_reports), and project-scoped input-analysis subfolders (kol_feedback, market_research, competitive_landscape, filing_strategy). Per-DHF external-mode multi-file deferred. Fixture tests 23 → 36 (added cases 7 + 8 for project-scoped and per-DHF multi-file). README.md rewritten with full Design & Architecture section consolidating pipeline architecture, IoC model, resolution algorithm, multi-file mode, and project-agnostic discipline. (task ben/191 Phase 6)
# v8 (advisor-grounding pilot): add `discovery-index` action — resolves canonical document roles (system_architecture, regulatory_strategy, …) to project file paths via three-level registry pattern (L1+L2 canonical-roles.yaml in skill; L3 generated <project>-dhf-discovery.json + optional project.yml evidence_layout overrides). Handles both `dhf_organization: internal` and `external` modes; external mode reads taxonomy_path and supports both nested (folder/v*.md) and flat (folder.md) sub-conventions. Bootstrap path: new projects need zero role-specific authoring. Designed for advisor-agent grounding consumers; piloted on `regulatory-affairs`.
# v7 (task ben/158 Phase 1): catalog schema clean break — `status` and `location` removed from per-obligation entries; new optional fields `canonical_role`, `criticality`, structured `applies_to: [{role, scope, artifact_pattern}]`, `extracted_requirements` plumbed through; top-level `obligation_set_hash` added as tracker cache key. `reproject` action retired (was tied to the dropped `location` field); `scope diff` retained for PCCP change-impact analysis. Coverage / lifecycle / evidence-binding now exclusively the responsibility of `/tracker assess` (agent sidecar).
---

# DHF Manifest Skill

Build and maintain the obligation → QMS → DHF-document catalog for a medtech-docs project. Usage: `/dhf-manifest <action>`

Answers the meta-question `/trace-matrix` cannot: **are the right documents even present, and which obligations must each one satisfy — with which QMS procedure governing production?** Four layers feed one another; each layer's output is the next layer's input. The skill is readable from layer 1 alone — no need to wait for the full stack.

```
SKILL-OWNED                                       PROJECT-OWNED
  data/fda-guidance/*.md                          docs/project/dhf-manifest/
  data/standards/*.md          ──build-reference──▶  qms-manifest.md  ──build-qms──▶  qms-manifest.json
  data/industry-frameworks/*.md                                                 │
       │                                                                        │
       └── per-source *.json sidecar (built)                                    │
       │                                                                        │
       └── aggregate reference-dhf.yml (built)  × project.yml scope              ▼
                                                           ↓                × qms-manifest.json
                                           build-manifest  ──▶  <project>-dhf-manifest.{md,json} (View 1)
                                                                ├──▶  <project>-dhf-by-section.md (View 2)
                                                                │
                                                        dashboard  ──▶  <project>-dhf-dashboard.md (View 3)
```

Layout is flat on both sides. Skill-side uses category folders mirroring `medtech-docs/references/` (fda-guidance, standards, industry-frameworks) — no tier prefixes. Each source MD has a sibling built JSON sidecar. Project-side holds all 7 user-facing files at its root.

## Actions

| Action | Details | Script / Agent |
|--------|---------|---------------|
| `init` | [actions/init.md](actions/init.md) | — |
| `build-reference` | [actions/build.md](actions/build.md) | scripts/build-reference.py |
| `build-qms` | [actions/build.md](actions/build.md) | scripts/build-qms.py |
| `build-manifest` | [actions/build.md](actions/build.md) | scripts/build-manifest.py |
| `dashboard` | [actions/inspect.md](actions/inspect.md) | scripts/dashboard.py |
| `distill-qms [topic]` | [actions/distill.md](actions/distill.md) | agents/dhf-distiller.md |
| `validate` | [actions/inspect.md](actions/inspect.md) | scripts/validate.py |
| `scope diff <flag>=<val>` | [actions/inspect.md](actions/inspect.md) | scripts/build-manifest.py --dry-run |
| `discovery-index` | [actions/discovery-index.md](actions/discovery-index.md) | scripts/discovery-index.py |

## Scope flags (`project.yml`)

`build-manifest` reads two locations — no separate project-scope.yml:

| Field | Location in project.yml | Example value |
|-------|------------------------|---------------|
| `iec62304` class per item | `dhfs[].classification.iec62304` | B or C per item |
| `ai_enabled` per item | `dhfs[].classification.ai_enabled` | true / false per item |
| `samd` per item | `dhfs[].classification.samd` | true / false per item |
| `hardware` | `scope.hardware` | false |
| `cloud_hosted` | `scope.cloud_hosted` | true |
| `tool_validation` | `scope.tool_validation` | true |
| `multi_function_device` | `scope.multi_function_device` | false |
| `ota_updates` | `scope.ota_updates` | true |
| `usability_hf` | `scope.usability_hf` | true |
| `clinical_evaluation` | `scope.clinical_evaluation` | literature |
| `interoperability` | `scope.interoperability` | true |
| `geography` | `scope.geography` | [us] |

## Output filename derivation

The four output files emitted by `build-manifest` and `dashboard` are prefixed with a project-specific slug so each project's manifests are visually self-identifying:

```
<project-slug>-dhf-manifest.md
<project-slug>-dhf-manifest.json
<project-slug>-dhf-by-section.md
<project-slug>-dhf-dashboard.md
```

`<project-slug>` resolves in this order (`scripts/_project_slug.py`):

1. `dhf_manifest.output_prefix` in `project.yml` (explicit override)
2. `project.name` slugified (default) — lowercase, whitespace + `_` → `-`, strip non-alphanumeric except `-`, collapse repeats, trim leading/trailing
3. `dhf` literal fallback (no `project.yml` found — surfaces the missing config as a smell)

Examples: `project.name: ACME_DEMO` → `acme-demo` → `acme-demo-dhf-manifest.md`; `project.name: MedTech Project` → `medtech-project` → `medtech-project-dhf-manifest.md`.

## Sibling skills

| Skill | Relationship |
|-------|-------------|
| `/trace-matrix` | Sibling — intra-DHF (UN↔DI↔V&V↔Risk); same sidecar pattern |
| `/medtech-docs` | Sibling — scaffolds folders/READMEs; `init` calls `/dhf-manifest init` |
| `/tracker` | Consumer — composition manifests become Tier 4 filing-phase views |
| `/advisors` | Consumer — reads manifest entry + obligations as authoring context |
| `/best-practices` | Consumer — checks unbound entries, orphan files, Tier 4↔disk drift |
| `/docflow` | Substrate — Tier 2 distillation reads `docs/internal/source-md/` |

## Boundary contract — `dhf-manifest` (catalog) vs `tracker` (analysis)

This skill owns the **catalog of what should exist** — the obligation set
projected from regulatory frameworks (FDA, IEC 62304, ISO 14971, etc.) +
QMS clauses through a project's scope vector. Output is intentionally
**static and purely declarative** — it changes only when a regulatory
framework distillation is added or a project's scope vector shifts.

The catalog is **never resolved against project files here**. Each obligation
declares a `canonical_role` (mechanical join key), structured `applies_to`
patterns (`[{role, scope, artifact_pattern}]`), `criticality` (regulatory
weight), `reg_source` (citation + anchor), `qms_grounding` (QMS clause IDs),
and `extracted_requirements` (section-level checklist of what the doc must
show). It does NOT carry per-project `location` paths, per-obligation
status, or coverage data — those are runtime project-state, not catalog
content.

This skill does NOT walk the project DHF tree, does NOT bind obligations
to evidence file paths, does NOT compute coverage, does NOT determine
required-vs-optional per milestone, does NOT analyze evidence content,
does NOT render readiness verdicts. Those are `/tracker assess`'s job.
This skill produces the contract; the tracker reports against it.

Mental model: **dhf-manifest is the syllabus; `/tracker` is the scorecard.**

### Catalog schema (per-obligation, v7+)

Each entry under `dhf_manifest[<dhf_leaf>][]` carries:

| Field | Type | Source | Notes |
|-------|------|--------|-------|
| `id` | str | distillation | OBL-xxx, stable across builds |
| `title` | str | distillation | Short human label |
| `topic` | str | distillation | One of the 16 DHF topics (validate.py enforces) |
| `artifact_type` | str | distillation | Coarse artifact classification |
| `canonical_role` | str \| null | distillation | **Mechanical join key** with tracker rows. Vocabulary is the medtech-IEC-62304 default in `tracker/scripts/generate.py:CANONICAL_ROLE_INDEX`, overridable via `project.yml tracker.canonical_role_index`. Phase 2 distillation backfills; Phase 1 emits `null`. |
| `criticality` | `must-have` \| `should-have` \| `may-have` \| null | distillation | Distillation-time inference from regulatory wording (shall→must-have, should→should-have, may→may-have). Tracker uses this to split required-vs-optional obligation sets per row. Phase 1 emits `null`; Phase 2 backfills. |
| `applies_to` | list | distillation | Phase 1: list of strings (free-text, legacy). Phase 2+: list of dicts `{role, scope, artifact_pattern}` where `artifact_pattern` is a glob relative to a DHF root (e.g., `design-controls/architecture/*-sad.md`). Tracker resolves patterns against the DHF tree. |
| `extracted_requirements` | list[str] | distillation | Section-level checklist (shall/should bullets) the bound evidence must address. Tracker reads this for per-obligation coverage analysis. Already populated in existing distillations. |
| `dhf_owner` | `system` \| `item` \| `both` | distillation | Routing input |
| `source` | str | distillation | Citation text (legacy column) |
| `reg_source` | object | build-time | `{citation, category, source_file, anchor_url}` — deep link to the distillation MD anchor |
| `qms_grounding` | object | qms-manifest | `{direct: [QMS-ids], topic_fallback}` |

**Removed in v7 (clean break, task ben/158 Phase 1):**

| Field | Why removed | Replacement |
|-------|-------------|-------------|
| per-obligation `status` | Runtime project-state; not catalog content. Tracker re-derives lifecycle per row from frontmatter + Comala signals. | `submission-tracker.agent.json` per-row `value` + `obligations[].coverage_state` |
| per-obligation `location` | Project-tree binding; not catalog content. Catalog declares `applies_to` patterns; tracker resolves them at runtime. | `submission-tracker.agent.json` per-obligation `bound_evidence_paths` (Phase 5) |

**Top-level fields:**

- `schema_version` — catalog format version (currently `"1.0"`)
- `obligation_set_hash` — `sha256:` over canonical-sorted obligation content (id + canonical_role + criticality + applies_to + extracted_requirements + reg_source citation + qms direct grounding). **Tracker cache-invalidation key**: `/tracker assess` skips re-analysis when this hash matches the agent sidecar's recorded hash.
- `source_obligations`, `skipped_out_of_scope`, `generated`, `dhf_manifest` (per-DHF entry lists)

Tracker's synthesis layer reads this catalog and at runtime: resolves the
`artifact_pattern`s against each row's DHF tree → reads the resolved
evidence file content → computes per-obligation coverage against
`extracted_requirements` → assembles required-vs-optional split (catalog
`criticality` × milestone posture × `regulatory.yml` `required:` flag) →
derives the row's lifecycle state. Results land in
`submission-tracker.agent.json` — the agent sidecar mutates as evidence
changes; the catalog stays stable.

Tracker also layers in **project-tactical expectations** (Q-Sub questions,
strategy commitments, predicate findings) that aren't regulatory-cataloged
but matter for that project's filing. Those are tagged by source and never
flow back into this catalog automatically. Promotion of a tactical
expectation into the regulatory catalog is a deliberate change to this
skill's source data (a new framework distillation or scope-dimension entry).

## Best Practices
See [README.md](README.md) — consumed by `/best-practices` audit.

## Changelog
See [README.md](README.md) for version history.

