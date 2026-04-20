# Cloud Suite — Child DHFs

> _Demo sample data — not for clinical use._

Child DHFs for the cloud-suite platform. The platform itself (at `docs/project/dhfs/cloud-suite/`) carries `regulatory: mixed` in `project.yml` — the regulatory weight is carried by the individual children listed here.

Every file / folder under this directory represents a cloud-suite component whose design controls are tracked independently and referenced from the parent platform's submission composition manifest.

## Structure

Each subfolder follows the standard per-DHF layout scaffolded by `/medtech-docs init`:

```
<child-dhf>/
├── README.md
├── clinical/
├── cybersecurity/
├── design-controls/
├── postmarket/
└── risk-management/
```

See the parent platform's `README.md` (one level up) for the composition rationale and which children are in-scope for each filing.

## Current Children

| DHF | Regulatory Status | Filing | Notes |
|-----|-------------------|--------|-------|
| `alerts-engine` | in-development | 510k | Alerting service for the cloud suite |
| `analytics-dashboard` | in-development | 510k | Analytics UI and pipelines |
| `clinical-interface` | in-development | 510k | Clinician-facing UI on top of the suite |
| `compliance-reports` | in-development | 510k | Compliance reporting surface |
| `drug-library-manager` | in-development | 510k | Drug library management (referenced by PP3500 510k composition manifest) |
| `fleet-management` | in-development | 510k | Fleet device management |
| `inventory-tracker` | in-development | 510k | Inventory tracking |

## Conventions

- **Naming**: Each child folder is lowercase kebab-case and matches its `path` leaf in `project.yml` `dhfs[]`. Never rename — the leaf is referenced by `/trace-matrix`, `/tracker`, and composition manifests.
- Every child has a `parent: cloud-suite` entry in `project.yml` `dhfs[]`.
- Adding a new child: run `/medtech-docs add-dhf <name> --parent cloud-suite --regulatory in-development --filing <filing>`.
- Children currently not referenced in any composition manifest surface as WARN in `/best-practices` — document the scope call in the relevant submission's Excluded section or add them when they enter filing scope.

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| 2026-04-20 | Ben Xavier | Initial version — created under task 018 to satisfy medtech-docs v17 README-every-docs-folder check. |
