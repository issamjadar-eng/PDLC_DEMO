# Code quality — audit store for the finance analysis code

Engine-managed store for the commercial skill's **code-quality soft gate**, scoped to
the Finance domain: the audit trail over the PROJECT-SIDE analysis code — per-question
computation modules (`../bq_modules/`), the shared `../computations.py`, and the corpus
dataset generators pinned by finance editions (`corpus:finance/<dataset>/gen.py` and
cross-domain `corpus:commercial/<dataset>/gen.py`). The engines themselves
(`commercial.py`, `corpus.py`) are out of scope — they are reviewed at registry level.

## Structure

| Item | Purpose |
|------|---------|
| `records.yml` | Per-artifact entries keyed by sha256: deterministic check results (static lint, poison-pattern scan, determinism replay) written by `code-audit`, plus AI code reviews filed by `record-code-review` |

## Conventions

- **Engine-managed — do not hand-edit.** Entries are written by
  `python3 .claude/skills/commercial/scripts/commercial.py --domain finance code-audit ...`
  and `... --domain finance record-code-review ...`. Newest entry per sha wins.
- **Soft gate.** Statuses (checks-failed / review-outdated / unreviewed /
  reviewed-current) render as badges in edition quality.json and the console sidecar;
  nothing blocks on them — `approve` prints the status, `check` prints a count line.
- **Reviews bind to bytes.** A review is filed against a file's sha256 at filing time;
  an edition whose pinned sha lacks a review while an older sha has one surfaces as
  `review-outdated`.
- Cross-domain generators (`corpus:commercial/...`) may also carry records in the
  commercial domain's store; each domain's store is independent and keyed by sha, so
  the same bytes audit identically in both.
- See the commercial skill SKILL.md ("Code quality — the soft-gate audit layer") for
  the full contract, including the poison-pattern rules and the review failure-class
  list.

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| 2026-09-08 | BX / AI Assistant | task 118: folder created; first deterministic sweep filed over the four FQ modules, computations.py, and the pinned generators. |
