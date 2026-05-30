# `docs/project/console/drug-library-manager/` — Console Sidecars for `drug-library-manager`

Generated sidecar artifacts for the `drug-library-manager` DHF, consumed by the project-console web UI. **Generated only — never hand-edit.**

See [`../README.md`](../README.md) for the producer/consumer contract, file conventions, and rebuild commands.

## Structure

| File | Producer |
|------|----------|
| `console_trace_matrix.json` | `/trace-matrix build drug-library-manager` |
| `console_trace_matrix.md` | `/trace-matrix build drug-library-manager` |

Additional `console_*.{json,md}` files may appear here as other skills register sidecars for this DHF.

## Expected Content

Generated sidecar files following the `console_<topic>.{json,md}` naming convention (see the Structure table above for the current producer set). New sidecars added by other skills must use the same prefix to be discoverable by the project-console UI.

## Conventions

Inherits the conventions of [`docs/project/console/`](../README.md):
- Generated outputs only; manual edits are overwritten on next producer run.
- The folder name must match `project.yml dhfs[].leaf` (`drug-library-manager` for this DHF).
- The console reads these via the JSON contract; loose coupling.

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| 2026-05-30 | Ben Xavier | Initial scaffold under ben/068 — closes the `/best-practices` audit FAIL for the missing folder README. |
