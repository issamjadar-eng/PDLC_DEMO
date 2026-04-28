---
pack_name: type-e-ui-capture
version: 1.0
applies_to_type: e
loaded_with: shared-fidelity
emit_required: false
status: active
---

# type-e-ui-capture

Rules for **type-e** images — screenshots, photographs, UI mockups, and other
raster content **without graph structure**. Loaded by
`agents/interpret_image.md` when the source image is not a diagram.

Extracted from `agents/converter.md` Phase 4.7 (F11a-e).

## Source characteristics that pick this pack

- Screenshot of an application UI (login screen, dashboard, form)
- Photograph of a physical device, tablet, or surgical setup
- Logo, cover banner, illustration, or other raster artwork
- Anything that is NOT a graph / diagram

Also fires as a **fallback for ambiguous wide/rectangular images** when the
extractor's decorative-score heuristic can't distinguish a cover banner from a
real diagram — the per-image agent reads the image and confirms it's a cover.

## Emit rule: NO Mermaid

Type-e images produce **no** ```mermaid fence. Emit only the marker + alt text
+ caption:

```markdown
<!-- F11-CLASSIFY: descriptor="login-screen" type="e" mermaid-emit="skip" skip-reason="ui-capture" -->

![Screenshot of the MedTech Project IntraOp login screen: email and password fields, a "Sign in" button, and an OKTA SSO alternative link at the bottom.](images/login-screen.png)

*Figure N. MedTech Project IntraOp login screen (source p.5).*
```

No "Authoritative source" line — that disclaimer exists only for Mermaid
supplements. No layout note. Caption is one short sentence with the source
page.

## skip-reason values

| Source | skip-reason |
|--------|-------------|
| Application UI screenshot | `ui-capture` |
| Physical device / surgery photo | `photograph` |
| Logo, banner, decorative header | `decorative` |
| Illustration, icon, diagram-of-a-physical-thing | `photograph` |

## Alt-text target

10-30 words. Describe what's visible — fields, buttons, layout, action being
captured. For device photos, describe the device, orientation, any visible
labels or status indicators.

Do NOT narrate the diagram's implied purpose ("user logs in to begin surgery")
unless the source explicitly labels it. Stick to observable content.

## When a type-e image turns out to have graph structure

If, after reading the image, you find it actually shows a flow or architectural
diagram (descriptor misleading, extractor mis-classified), reclassify as a/b/c
instead. The classifier is advisory — your in-the-loop observation wins. Emit
the appropriate type's marker and load the matching rule pack.

## Decorative images should NOT reach this agent

`scripts/extract_pdf.py` classifies decorative images (≤100px, ≤280px
squarish, alpha-transparent) at extraction time. They're marked
`decorative: true` in the manifest and not dispatched to `interpret_image.md`
at all. If one slips through and you receive a pure-decorative image, emit
Case B with skip-reason="decorative" and a 5-word alt text ("Page footer icon.")
so the MD doesn't accumulate noise.

## Changelog

- 2026-04-21: Stub created during task ben/089 Phase A scaffolding.
- 2026-04-21 (session 2): Populated from `agents/converter.md` Phase 4.7
  (F11a-e). Added skip-reason table and the reclassification hint for
  mis-extracted images.
