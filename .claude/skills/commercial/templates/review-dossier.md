# Review Dossier Template

The mandatory structure for any dossier a `--detail-ref` points at — filed via
`record-code-review` or `record-verification`. Dossiers are an audit surface: consoles
render them inline in a fold, where non-engineers (executives, quality reviewers,
regulators) read them alongside the badges. Write the top half of the dossier for that
reader; keep the code talk in the appendix.

Display constraints (apply to the WHOLE document):

- No table anywhere may exceed **4 columns**, and no cell may exceed **~25 words**.
- Content wider than that becomes stacked definition-list entries (the Findings shape).
- Findings are NEVER a table — one entry per finding.

Copy the skeleton; a filled mini-example follows it.

---

## Skeleton

````markdown
# <Plain-words title of what was reviewed> — review dossier

**Reviewed**: <what, in plain words — e.g. "the two scripts that compute the campaign
answers"> (`path/to/artifact-a.py`, `path/to/artifact-b.py`)
**Date**: YYYY-MM-DD · **Reviewer**: <who> · **Verdict**: <one line, plain words>

## Summary

<3–6 sentences a non-engineer reads standalone: what was reviewed, the verdict in
plain words, how many issues were found and of what consequence, and what has since
happened to them. No code identifiers, no reviewer jargon.>

## What we checked

- <plain-language bullet per review dimension>
- <...>

## Findings

### F-1 (high) — <plain-language title>

- **What's wrong:** <plain language first; code terms in parentheses after.>
- **Why it matters:** <the consequence in business/quality terms — what could go
  wrong for a reader of the reports.>
- **Resolution:** FIXED — <what changed, verified in current code.>
  <!-- or: ACCEPTED — <rationale>; or, pre-fix only: NOT YET FIXED — <planned
       change>. UPDATE to the outcome when it is known — a dossier displayed on
       an audit surface must carry outcomes, and the dossier lint errors on the
       word "proposed" in a Resolution line. -->

### F-2 (low) — <plain-language title>

- **What's wrong:** <...>
- **Why it matters:** <...>
- **Resolution:** ACCEPTED — <rationale.>

## Terms used

- **<term>** — <one-line plain definition of a reviewer term the dossier uses.>

## Technical appendix

<Line refs, per-artifact detail, narrow tables (≤4 columns; long text becomes
stacked entries). The machine-readable JSON block goes last.>

```json
{"reviews": [
  {"path": "path/to/artifact-a.py", "verdict": "<verdict>",
   "findings": [
     {"id": "F-1", "severity": "high", "summary": "<short>", "resolution": "FIXED"},
     {"id": "F-2", "severity": "low", "summary": "<short>", "resolution": "ACCEPTED"}
   ]}
]}
```
````

---

## Filled mini-example

````markdown
# Campaign-coverage computation — review dossier

**Reviewed**: the script that computes the weekly campaign-coverage answer
(`computations/coverage.py`), against its analysis plan (`plans/BQ-23.md`)
**Date**: 2026-07-01 · **Reviewer**: AI code-review agent · **Verdict**: sound
overall; two issues found, both since fixed.

## Summary

We reviewed the program code that calculates the weekly campaign-coverage answer
shown on the console. The calculation follows the committed analysis plan and the
numbers it produces are correct today. We found two issues that could have made a
future answer wrong without anyone noticing: one sentence in the report was written
as fixed text instead of being calculated, and one comparison used a rounded number
where the plan committed to the exact one. Both issues have been fixed and the
fixes verified in the current code.

## What we checked

- Does the code compute what the analysis plan committed to?
- Could any sentence or number in the report become wrong when the data refreshes?
- Are thresholds compared against exact values, not display-rounded ones?
- Would the same inputs always produce the same answer (no clocks, no randomness)?

## Findings

### F-1 (medium) — A conclusion sentence was typed in, not calculated

- **What's wrong:** The report line "coverage improved in every region" was written
  as fixed text (a string literal), not generated from the data (narrated, not
  computed).
- **Why it matters:** If a future data refresh shows a region getting worse, the
  report would still claim improvement everywhere — a false statement on an
  approved answer, with nothing to catch it.
- **Resolution:** FIXED — the sentence is now generated from a per-region
  comparison and states the count it computed; verified in current code.

### F-2 (low) — A pass/fail check used a rounded number

- **What's wrong:** The coverage figure was rounded for display first and then
  compared against the 95% target (rounded-compare), where the plan commits to
  comparing the exact value.
- **Why it matters:** An answer sitting exactly at the line (e.g. 94.96% rounding
  to 95.0%) could be declared on-target when it is not.
- **Resolution:** FIXED — the check now compares the exact value and rounds only
  for display; verified in current code.

## Terms used

- **narrated, not computed** — a sentence typed as fixed text rather than generated
  from the data, so it can silently become false when the data changes.
- **rounded-compare** — testing a threshold against a display-rounded value instead
  of the exact one, which can flip a verdict right at the boundary.

## Technical appendix

| Finding | Location | Fix verified at |
|---|---|---|
| F-1 | `coverage.py` L84 | L84–L91 (computed per-region delta) |
| F-2 | `coverage.py` L52 | L52 (raw fraction vs target) |

```json
{"reviews": [
  {"path": "computations/coverage.py", "verdict": "APPROVED-WITH-FINDINGS",
   "findings": [
     {"id": "F-1", "severity": "med", "summary": "Report conclusion narrated, not computed", "resolution": "FIXED"},
     {"id": "F-2", "severity": "low", "summary": "Threshold compared on rounded value", "resolution": "FIXED"}
   ]}
]}
```
````
