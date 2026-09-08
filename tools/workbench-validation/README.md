# Workbench Validation — Generated Outputs

_Demo sample data — not for clinical use._

**Everything in this folder is generated** by the `workbench-validation` skill — do
not hand-edit. The authored sources of truth (validation plan with the role-based
WUN register, and the `validation.yml` manifest) live at
`docs/project/workbench-validation/`. Edit those, then re-run
`/workbench-validation validate` to refresh this folder.

| Path | Purpose |
|---|---|
| `results/<run-id>.json` (+ `latest.json`) | Per-run results: case statuses + the configuration baseline (git SHA, per-skill versions, hooks, platform) |
| `results/<run-id>/<TC-ID>.log` | **Evidence of record** per test case: execution header (command, cwd, env changes, timestamps, exit code, judgment rule) + the complete captured output |
| `validation-report.md` | The single validation report — needs × tests × results → per-need verdicts + fitness-for-use conclusion |
| `workbench-validation-index.json` | Console sidecar consumed by the project console's Settings → Validation view |

This data layer is general-purpose: a customer QMS requiring its own validation
document format is served by a new transform over these files, not by redoing the
validation. Viewable in the project console (Settings → Validation; files resolve in
the Documents tab via the `tools/workbench-validation` grounding root).
- 2026-09-08 — BX / AI Assistant — task 119: run/sidecar schema 1.1 — results JSON carries the full `environment` record (tooling, connections, isolation, dirty files, version-pin mismatches), `warnings[]`, per-case `endpoint`; report §1 gains the collapsed "Full environment record"; NOT-APPLICABLE status.
