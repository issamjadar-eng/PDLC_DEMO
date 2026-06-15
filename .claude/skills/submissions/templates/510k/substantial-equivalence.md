---
version: v0.1
status: draft
summary: Substantial-equivalence discussion — same-intended-use argument + technological-characteristics comparison to the predicate, with a side-by-side comparison table and a "different characteristics raise no new questions of safety/effectiveness" analysis.
---

<!-- AI-CHANGELOG — internal provenance of AI-assisted edits. Metadata only:
     NOT published downstream, NOT part of the controlled record, vendor-neutral.
| Date       | Task   | Summary                                                |
|------------|--------|--------------------------------------------------------|
| {{DATE}} | {{TASK}} | Substantial-equivalence discussion scaffolded from the submissions template. |
-->

# Substantial Equivalence Discussion — {{DEVICE}}

_Demo sample data — not for clinical use._

> **🔒 INTERNAL — working status.** Document control v0.1 · status: draft · authored under {{TASK}}. This is the core of the 510(k). Ground every claim in the predicate analysis and the device's V&V evidence — do not assert equivalence the test data doesn't support. Internal source mapping: {{D_REG_REFS}}.

## 1. Predicate Identification 📤

Primary predicate: {{PREDICATE}}. Reference device(s), if any: `[VERIFY]`. Basis for predicate selection per the predicate analysis.

## 2. Same Intended Use 📤

The subject device and predicate share the same intended use. Quote both indications-for-use statements and show they match (or explain why a narrower/identical use is still the same intended use). See [`indications-for-use.md`](./indications-for-use.md).

## 3. Technological Characteristics Comparison 📤

| Characteristic | {{DEVICE}} (subject) | {{PREDICATE}} (predicate) | Same / Different |
|---|---|---|---|
| Intended use / indications | `[VERIFY]` | `[VERIFY]` | — |
| Operating principle | `[VERIFY]` | `[VERIFY]` | — |
| Energy / delivery mechanism | `[VERIFY]` | `[VERIFY]` | — |
| Key materials / patient contact | `[VERIFY]` | `[VERIFY]` | — |
| Software / firmware level of concern | `[VERIFY]` | `[VERIFY]` | — |
| Performance specifications | `[VERIFY]` | `[VERIFY]` | — |

## 4. Different Characteristics — No New Questions of Safety or Effectiveness 📤

For each **Different** row above, explain why the difference does **not** raise new questions of safety or effectiveness, and identify the performance data (in [`performance-testing.md`](./performance-testing.md)) that supports the conclusion. This is the load-bearing SE argument — a difference left unaddressed is a deficiency.

## 5. Conclusion 📤

The subject device is substantially equivalent to the predicate {{PREDICATE}}. `[VERIFY] state the conclusion only after §§3–4 are complete and supported by test evidence.`

## Internal source mapping 📝

Predicate facts (K-numbers, product code, classification) reference the predicate analysis and `regulatory-strategy.md` D-REG-* blocks — they are not redeclared here as new facts.
