# Analysis plans — per-question prose contracts

One plan per business question (`BQ-NN.md`), scaffolded by `/commercial plan-init` and
then **user-owned**: the plan is the human-editable contract the computed answer is held
to. Each edition pins the plan's content hash (`edition.yml`); the `plan-currency` lint
check surfaces a missing plan, an unpinned edition, or a plan edited after its edition
was computed (drift). Whether the answer *honors* the plan's intent is an agent
judgment, filed via `record-verification --type intent-check`.

## Structure

| Item | Purpose |
|------|---------|
| `BQ-NN.md` | The question's plan: Goal, Approach (committed definitions — windows, anchors, denominators), Data (have vs need), Assumptions & expectations, Assertions & limits, Verification plan |

## Expected Content

- One `BQ-NN.md` per catalog question (scaffold with `plan-init`; never overwritten by
  the engine afterward).
- `## Verification plan` — the checklist of quality/audit gates the answer commits to
  (claim-lint, pin-freshness, plan-currency, code-audit, adversarial-verify, red-team,
  plus intent-check / reference-audit / human-review where declared). The checkboxes
  stay `[ ]` **forever** in the file: completion is computed from the edition's actual
  records (lint status, code-audit block, filed verification verdicts) and rendered by
  the console — hand-ticking would create artificial plan drift.

## Conventions

- **Edit freely, then re-answer.** A plan edit changes its hash; affected questions need
  a re-answer to re-pin (drift is a visible callout until then, by design).
- Committed definitions in `## Approach` are binding: an intent-check treats a committed
  definition not followed as a DEVIATION even if the numbers are right.
- Gate tokens in `## Verification plan` come from the commercial skill's recognized
  vocabulary (see its SKILL.md); notes after the `—` are free text.

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| 2026-07-27 | BX / AI Assistant | task 108: README added (readme-before-write gap flagged during verification-plan seeding); all 30 plans carry `## Verification plan` sections as of today. |
