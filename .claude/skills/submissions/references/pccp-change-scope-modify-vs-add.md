# PCCP change scope — "modify an existing output" vs "add a new output"

A recurring authoring trap when scoping a **Predetermined Change Control Plan (PCCP)**: conflating two *different kinds of change* because the underlying feature is in the *same clinical/technical family*. Getting this wrong either over-claims PCCP coverage (a scope defect) or needlessly routes an eligible change to a new submission.

## The two rulers

A candidate change to a device's outputs is measured against **two independent axes**. They frequently disagree, and the disagreement is the trap.

| Ruler | Question | Determines |
|-------|----------|------------|
| **Same family?** (clinical / engineering) | Is the new thing the same *kind* of measurement/output as ones the device already has — same inputs, same clinical purpose, same computation neighborhood? | Whether it is *conceptually* an extension. Necessary, **not sufficient**, for PCCP eligibility. |
| **Already in the cleared output set?** (regulatory) | Does the *cleared* device already **produce** this exact output? | Whether the change is a **modify** (improve an existing output) or an **add** (a new output). This is the axis FDA's PCCP boundary is drawn on. |

## Modify vs add

| Change type | What it is | Typical PCCP treatment |
|-------------|-----------|------------------------|
| **Modify** an existing output | Improve the accuracy/robustness/UI of an output the cleared device **already produces** (e.g., retrain the model behind an existing measurement; refine existing non-AI logic; add a new *display* of already-computed data) | Commonly pre-authorizable under standard "retraining / refinement / UI" change categories, with a Modification Protocol + acceptance criteria. |
| **Add** a new output | Produce a measurement/output the cleared device **does not currently produce** | **Generally outside a PCCP** — most PCCP guidance treats a new output type / new output class as a change that routes to a new marketing submission, **unless** it is pre-specified as its own **bounded** change category and the regulator agrees. |

## The trap, stated plainly

> "The new output is the same family as our existing outputs → therefore adding it is just an *improvement* of our existing capability → therefore an existing 'improve/retrain' category already covers it."

The first step is often true (same family). The error is the second step: it uses the *same-family* (clinical) answer to justify a *coverage* (regulatory) claim. FDA's PCCP line is not drawn on family — it is drawn on **"is this output already cleared?"** Calling an **add** a **modify** to fit an existing category replaces one over-claim (the device does X now — false) with another (the PCCP already covers X — also false). Same defect, one layer up.

## Authoring rules of thumb

1. **Establish the cleared output set first.** Before scoping any output change, confirm exactly what the *cleared* device produces. A claimed-but-absent output is its own defect; a change to it is undefined until the baseline is known.
2. **Classify modify vs add against the cleared set — not against the clinical family.** "It's the same kind of measurement" does not make it a modification.
3. **To pre-authorize an addition, write a dedicated bounded category** — name the specific output(s) (never an open "future outputs" bucket), constrain the derivation (no new input/model/anatomy/population), give it a Modification Protocol with its own acceptance criteria, and **ask the regulator explicitly** (a pre-submission is the venue). Do **not** relabel it under a "modify existing" category.
4. **Keep the exclusion list consistent.** If the PCCP's exclusions forbid "new output types," adding a bounded exception category requires a matching carve-out in the exclusions — or the package both authorizes and forbids the same change.
5. **Predicate coverage helps but is separate.** If the predicate is already cleared for the output, an "inside the cleared envelope" argument strengthens the case; if not, the addition must stand on its own validation evidence. Verify predicate coverage against the actual clearance record — do not assume it from clinical familiarity.

## Where this bites

- Device description / IFU: don't list an output the device doesn't produce (capability over-claim).
- PCCP summary: don't file a new output under a "retrain / refine existing" category (coverage over-claim).
- Substantial-equivalence: don't assert predicate coverage of an output the predicate isn't cleared for (SE over-claim).

All three are the same root error viewed from different documents: a **new output** dressed as an **improvement of an existing one**.
