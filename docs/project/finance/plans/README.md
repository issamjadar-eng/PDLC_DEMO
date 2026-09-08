# Analysis plans — per-question prose contracts (Finance)

One plan per finance question (`FQ-NN.md`), scaffolded by
`commercial.py --domain finance plan-init FQ-NN` and then **user-owned**: the plan is
the human-editable contract the computed answer is held to. Each edition pins the
plan's content hash (`edition.yml`); the `plan-currency` lint check surfaces a missing
plan, an unpinned edition, or a plan edited after its edition was computed (drift).
Whether the answer *honors* the plan's intent is an agent judgment, filed via
`record-verification --type intent-check`.

## Structure

| Item | Purpose |
|------|---------|
| `FQ-NN.md` | The question's plan: Goal, Approach (committed definitions — windows, anchors, denominators, aggregation rules), Data (have vs need), Assumptions & expectations, Assertions & limits, Verification plan |

## Expected Content

- One `FQ-NN.md` per catalog question (scaffold with `plan-init`; never overwritten by
  the engine afterward). Roadmap questions carry a plan too — it states what the answer
  will need before a computation exists.
- `## Verification plan` — the checklist of quality/audit gates the answer commits to.
  The checkboxes stay `[ ]` **forever** in the file: completion is computed from the
  edition's actual records and rendered by the console — hand-ticking would create
  artificial plan drift.

## Conventions

- **Edit freely, then re-answer.** A plan edit changes its hash; affected questions need
  a re-answer to re-pin (drift is a visible callout until then, by design).
- Committed definitions in `## Approach` are binding: an intent-check treats a committed
  definition not followed as a DEVIATION even if the numbers are right.
- Finance-specific committed definitions to state explicitly: the window (closed quarters
  / YTD months and their prior-year comparators), the denominator source for any per-unit
  figure, and the flow-weighted aggregation rule for days-type ratios.
- Gate tokens in `## Verification plan` come from the commercial skill's recognized
  vocabulary (see its SKILL.md); notes after the `—` are free text.

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| 2026-09-08 | BX / AI Assistant | task 118: folder created with plans for FQ-01..FQ-10 (four implemented, six roadmap). |
