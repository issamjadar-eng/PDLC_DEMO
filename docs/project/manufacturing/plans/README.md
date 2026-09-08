# Analysis plans — per-question prose contracts (Manufacturing)

One plan per manufacturing business question (`MQ-NN.md`), scaffolded by
`commercial.py --domain manufacturing plan-init MQ-NN` and then **user-owned**: the plan
is the human-editable contract the computed answer is held to. Each edition pins the
plan's content hash (`edition.yml`); the `plan-currency` lint check surfaces a missing
plan, an unpinned edition, or a plan edited after its edition was computed (drift).
Whether the answer *honors* the plan's intent is an agent judgment, filed via
`record-verification --type intent-check`.

## Structure

| Item | Purpose |
|------|---------|
| `MQ-NN.md` | The question's plan: Goal, Approach (committed definitions — windows, anchors, denominators, status semantics), Data (have vs need), Assumptions & expectations, Assertions & limits, Verification plan |

## Expected Content

- One `MQ-NN.md` per catalog question (scaffold with `plan-init`; never overwritten by
  the engine afterward). Roadmap questions (no computation yet) carry a plan too — it
  states the data gap that keeps them `not-implemented`.
- `## Verification plan` — the checklist of quality/audit gates the answer commits to.
  The checkboxes stay `[ ]` **forever** in the file: completion is computed from the
  edition's actual records and rendered by the console — hand-ticking would create
  artificial plan drift.

## Conventions

- **Edit freely, then re-answer.** A plan edit changes its hash; affected questions need
  a re-answer to re-pin (drift is a visible callout until then, by design).
- Committed definitions in `## Approach` are binding: an intent-check treats a committed
  definition not followed as a DEVIATION even if the numbers are right.
- Every plan anchors "as-of" on the pinned snapshot's provenance `as_of`
  (`data_through` in the dataset config), never the run date.
- Gate tokens in `## Verification plan` come from the commercial skill's recognized
  vocabulary (see its SKILL.md); notes after the `—` are free text.

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| 2026-09-08 | BX / AI Assistant | task 118: folder created with plans for MQ-01..MQ-10 (four implemented, six roadmap with stated data gaps). |
