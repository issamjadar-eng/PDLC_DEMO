---
name: dhf-manifest
description: "DHF Manifest — 4-tier deliverable catalog that projects regulatory and QMS obligations through a project scope vector into per-DHF manifests with gap reports. Sibling to /trace-matrix (intra-DHF trace); this skill answers: are the right documents present and do they satisfy regulation + QMS?"
version: 5
updated: 2026-04-24
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
                                           build-manifest  ──▶  hiplink-manifest.{md,json} (View 1)
                                                                ├──▶  hiplink-by-section.md (View 2)
                                                                │
                                                        dashboard  ──▶  hiplink-dashboard.md (View 3)
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
| `reproject` | [actions/inspect.md](actions/inspect.md) | scripts/build-manifest.py --delta |
| `scope diff <flag>=<val>` | [actions/inspect.md](actions/inspect.md) | scripts/build-manifest.py --dry-run |

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

## Sibling skills

| Skill | Relationship |
|-------|-------------|
| `/trace-matrix` | Sibling — intra-DHF (UN↔DI↔V&V↔Risk); same sidecar pattern |
| `/medtech-docs` | Sibling — scaffolds folders/READMEs; `init` calls `/dhf-manifest init` |
| `/tracker` | Consumer — composition manifests become Tier 4 filing-phase views |
| `/advisors` | Consumer — reads manifest entry + obligations as authoring context |
| `/best-practices` | Consumer — checks unbound entries, orphan files, Tier 4↔disk drift |
| `/docflow` | Substrate — Tier 2 distillation reads `docs/internal/source-md/` |

## Best Practices
See [README.md](README.md) — consumed by `/best-practices` audit.

## Changelog
See [README.md](README.md) for version history.

