# DHFs

Design History Files for the PDLC_DEMO platform. This folder contains one subfolder per DHF — each is a regulated document set for a coherent component that has its own design controls, risk file, V&V, post-market surveillance, and (usually) its own regulatory pathway.

## Source of Truth

`project.yml` `dhfs[]` is the authoritative list. Each entry records:

| Field | Meaning |
|---|---|
| `path` | Folder under `docs/project/dhfs/` (top-level) or a nested path like `cloud-suite/dhfs/<child>` |
| `regulatory` | `concept` / `in-development` / `cleared` / `mixed` |
| `filing` | Submission folder this DHF rolls up into (`510k`, `qsub`, `pccp`, or null) |
| `parent` | Parent DHF path, or null for top-level |

A DHF with `regulatory: mixed` is a **platform** — it doesn't file directly; its children carry the regulatory weight (e.g., `cloud-suite` hosts 7 child DHFs, each filing on its own).

## Per-DHF Shape

Every DHF, top-level or nested, has the same shape:

```
<dhf-name>/
├── README.md                ← this DHF's purpose, regulatory status, filing rollup
├── design-controls/         ← trace-matrix, plans, user-needs, requirements, architecture, vnv, tool-validation
├── clinical/                ← evaluation-plans, benefit-risk, literature-search
├── postmarket/              ← pmcf-plans, pmcf-studies, capa, complaints
├── risk-management/         ← sibling of design-controls (ISO 14971 is device-level)
├── cybersecurity/           ← IEC 81001-5-1 assessment, SBOM, threat model
└── dhfs/                    ← optional; only present when a platform DHF hosts children
    └── <child-dhf>/
```

## Upstream Strategy

Strategy briefs are **shared across the whole project** and live at `../strategies/`, not per-DHF. Each shared strategy doc (regulatory, architecture, development, testing, risk, postmarket, commercial, operations) uses topic-first sections with per-component callout subsections (`### PCA Device`, `### Connectivity Adapter`, etc.) nested under each topic. Formal outputs in each DHF's own folders are downstream of those shared briefs.

## Current Roster

| DHF | Regulatory | Filing | Parent |
|---|---|---|---|
| `pca-device` | in-development | 510k | — |
| `connectivity-adapter` | in-development | 510k | — |
| `cloud-suite` | mixed (platform) | — | — |
| `cloud-suite/dhfs/drug-library-manager` | in-development | 510k | cloud-suite |
| `cloud-suite/dhfs/fleet-management` | in-development | 510k | cloud-suite |
| `cloud-suite/dhfs/compliance-reports` | in-development | 510k | cloud-suite |
| `cloud-suite/dhfs/analytics-dashboard` | in-development | 510k | cloud-suite |
| `cloud-suite/dhfs/inventory-tracker` | in-development | 510k | cloud-suite |
| `cloud-suite/dhfs/alerts-engine` | in-development | 510k | cloud-suite |
| `cloud-suite/dhfs/clinical-interface` | in-development | 510k | cloud-suite |

Canonical check: `project.yml` beats this table. If they drift, trust `project.yml`.

## Conventions

- Add a new DHF with `/medtech-docs add-dhf <name>` (optional `--parent <path>` for nesting)
- DHF leaf names must be unique across the entire `dhfs[]` list (enforced at `add-dhf` time)
- Formal outputs stay per-DHF; strategic decisions go to `../strategies/`

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| 2026-04-13 | Ben Xavier | Initial version — created as part of task 009 README review (gap flagged by README audit). |
