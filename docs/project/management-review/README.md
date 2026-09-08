# Management review — assembled input packs

_Demo sample data — not for clinical use._

Dated **Management Review Packs** assembled by the commercial-skill engine's `pack`
action: for every business domain (Commercial, Finance, Manufacturing, …) the latest
**approved** answer edition of each question — verdict, expectation verdicts, materialized
issues, open risks, and the pinned snapshots with their freshness — plus the roster of
questions with no approved answer. A pack is an **assembly, not a computation**: every
figure was emitted by a claim-linted edition of the cited question, and each section names
the edition and report it came from.

The pack is the quantitative *input set* for the QMS management review — the SOP
[`GL-SOP-QM-002` Management Review](../../internal/source-md/quality-management/management-review-sop.md) §6.2 lists the required inputs (complaint handling, audits incl. supplier, data
analysis and CAPA effectiveness, CAPA status, …) and §6.1 sets the cadence (at least
quarterly). The review itself — agenda, minutes, outputs — is governed by that SOP, not
by this folder. ISO 13485 is deliberately not distilled under `docs/external/standards/`
(QMS-level, per that folder's README), so the SOP is the citable source here.

## Structure

| Item | Purpose |
|------|---------|
| `YYYY-MM-DD/pack.md` | The dated pack (markdown, reviewer-facing) |
| `YYYY-MM-DD/pack.json` | Machine summary — per domain: answered ids + editions, unanswered ids, issue/risk counts, expectation verdict tallies |

## Expected Content

- One dated subfolder per assembled pack. Packs are regenerated, never hand-edited.
- Produced by `python3 .claude/skills/commercial/scripts/commercial.py pack --domains
  commercial,finance,manufacturing [--as-of YYYY-MM-DD] [--include-drafts]` — from the
  console (Workflows → Management Review Pack) or by the monthly
  `business-evidence-refresh` GitHub Action (approved editions only).

## Conventions

- **Approved editions only** in a pack of record. `--include-drafts` exists for internal
  preview and flags every draft inline; a pack containing drafts is not review input.
- The as-of date is the freshness anchor for the pins table; re-assemble rather than
  edit when the date moves.
- Packs reference reports by repo-relative path; they never copy report bodies.

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| 2026-09-08 | BX / AI Assistant | task 118: reference-audit fixes — the ISO 13485 `[VERIFY]` repointed to `GL-SOP-QM-002` Management Review §6.1/§6.2 (cadence + required inputs) |
| 2026-09-08 | BX / AI Assistant | task 118: folder created with the engine's `pack` action (commercial skill v15); surfaced in the console Workflows catalog and the monthly evidence-refresh Action. |
