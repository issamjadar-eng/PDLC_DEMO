# `docs/project/console/` — Project Console Sidecars

Per-DHF sidecar artifacts consumed by the **project-console** web UI (`tools/project-console/`). One subfolder per DHF, mirroring `project.yml dhfs[].leaf`.

These files are **generated** — never hand-edit. Producers write here; the console reads here. Loose coupling: producers and consumer never share code, only the JSON contract.

## Structure

<!-- AUTO:STRUCTURE kind=subfolder-table source=fs -->
| Folder | Purpose |
|--------|---------|
| `alerts-engine/` | Cloud-suite Class II SaMD alerts engine — sidecars consumed by the project-console UI |
| `analytics-dashboard/` | Cloud-suite non-device analytics dashboard — sidecars |
| `clinical-interface/` | Cloud-suite Class II SaMD clinician-facing interface — sidecars |
| `cloud-suite/` | Cloud-suite system DHF parent — aggregates the 7 cloud child DHFs |
| `compliance-reports/` | Cloud-suite non-device compliance reports module — sidecars |
| `connectivity-adapter/` | MDDS Class I connectivity adapter — sidecars |
| `drug-library-manager/` | Cloud-suite Class II SaMD drug library manager — sidecars |
| `fleet-management/` | Cloud-suite non-device fleet management module — sidecars |
| `inventory-tracker/` | Cloud-suite non-device inventory tracker — sidecars |
| `pca-device/` | PP3500 PCA pump system DHF — sidecars |
<!-- /AUTO:STRUCTURE -->

(Each subfolder is a DHF leaf name from `project.yml dhfs[]`. New DHFs added to `project.yml` will get their own subfolder on next `/trace-matrix build` for that DHF.)

## Expected Content (per DHF subfolder)

| File | Producer | Consumer |
|------|----------|----------|
| `console_trace_matrix.json` | `/trace-matrix build <dhf>` | `/trace-matrix` console route — renders the layered UN ↔ DI ↔ Architecture ↔ V&V ↔ Risk view |
| `console_trace_matrix.md` | `/trace-matrix build <dhf>` | Human-readable rollup of the same |

Additional sidecar JSON files may be added by other skills (`/dhf-manifest`, `/tracker`) following the same `console_<topic>.{json,md}` convention.

## Conventions

- **Generated only.** Never hand-edit any file under `docs/project/console/<dhf>/`. Manual edits will be overwritten on next producer run.
- **One subfolder per DHF leaf** — must match `project.yml dhfs[].leaf` verbatim. Strays are flagged by `/best-practices`.
- **JSON-contract loose coupling** — the console reads the JSON shape, not the producer skill's internals. Changing the JSON schema requires updating both sides; changing the producer's internals does not.
- **Filename prefix** — sidecar files start with `console_` so they're easy to identify as console-bound vs other DHF artifacts.

## For Claude

- To rebuild a DHF's console sidecars after design-controls edits: `/trace-matrix build <dhf-leaf>` writes `console_trace_matrix.{json,md}` here.
- The console reads these on demand — no separate sync step needed; refresh the browser after rebuilding.
- If a DHF subfolder has stale content (older than the corresponding `docs/project/dhfs/<dhf>/` source docs), re-run the producer skill.

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| 2026-05-30 | Ben Xavier | Initial scaffold under ben/068 — closes the `/best-practices` audit FAIL for the missing folder README. |
