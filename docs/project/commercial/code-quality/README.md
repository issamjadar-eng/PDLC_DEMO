# Code quality — audit store for the commercial analysis code

Engine-managed store for the commercial skill's **code-quality soft gate**: the audit
trail over the PROJECT-SIDE analysis code — per-BQ computation modules
(`../bq_modules/`), the shared `../computations.py`, and the corpus dataset generators
(`corpus:<domain>/<dataset>/gen.py`). The engines themselves (`commercial.py`,
`corpus.py`) are out of scope — they are reviewed at registry level.

## Structure

| Item | Purpose |
|------|---------|
| `records.yml` | Per-artifact entries keyed by sha256: deterministic check results (static lint, poison-pattern scan, determinism replay) written by `code-audit`, plus AI code reviews filed by `record-code-review` |

## Conventions

- **Engine-managed — do not hand-edit.** Entries are written by
  `python3 .claude/skills/commercial/scripts/commercial.py code-audit ...` and
  `... record-code-review ...`. Newest entry per sha wins.
- **Soft gate.** Statuses (checks-failed / review-outdated / unreviewed /
  reviewed-current) render as badges in edition quality.json and the console sidecar
  (`schema_version` 1.2 `code:` block); nothing blocks on them — `approve` prints the
  status, `check` prints a count line, both informational.
- **Reviews bind to bytes.** A review is filed against a file's sha256 at filing time;
  an edition whose pinned sha lacks a review while an older sha has one surfaces as
  `review-outdated`.
- See the commercial skill SKILL.md ("Code quality — the soft-gate audit layer") for
  the full contract, including the poison-pattern rules and the review failure-class
  list.

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| 2026-07-27 | BX / AI Assistant | task 108: folder created (commercial skill v11) — first deterministic sweep filed for 33 artifacts (21 BQ modules, computations.py, 11 generators): all lint/poison/determinism green. |
