# Protocol execution records

## Structure

One file per executed protocol / inspection case: `<TC-ID>.result.yml`, following the
`workbench-validation` skill's `templates/protocol-result.yml` schema (verdict, executed,
operator, model_id, git_sha, harness_version, runs[], evidence[], deviations[], signed_off_by).

## Expected Content

- Records only — the written protocols live under `docs/project/workbench-validation/protocols/`.
- A record is appended by the operator after executing the protocol; the runner reads the
  latest record at run time, derives the case status from `verdict`, and pins a copy into
  the run's evidence folder.
- No record → the case is **NOT-EXECUTED** and its need **FAILS** (untested is not passed).

## Conventions

- Never edit a record after sign-off; re-execute and write a new record (git history keeps the old).
- `model_id` is mandatory — a protocol result is valid only for the model it was executed under.
- Evidence paths are repo-relative and point at transcripts/exports kept under
  `tools/workbench-validation/results/` or the task's `_work/` folder.

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| 2026-09-08 | BX / AI Assistant | task 121: folder created with the execution-record convention; no records yet (all protocols unexecuted). |
