---
audit_id: <audit-id>
source_doc: <source-path>
created: <created>
status: Extracting
schema_version: 1
---

# References Audit — <doc-title>

**Source doc:** [`<source-path>`](../../<source-path>)
**Audit ID:** `<audit-id>`
**Created:** `<created>`
**Status:** `Extracting | Researching | Findings Posted | Resolved`

This audit verifies that every citation in the source document actually resolves to a real source and that the source supports the cited claim. Findings carry a verdict band (`sound | unverified | broken`) and a finding kind (open enum). External-formal references are verified against both the medtech-docs registry distillation (L1a) and the project applicability layer (L1b) per the "cite both" mandate. See the `reference-audit` skill SKILL.md for the engine contract; see the `citations` advisor for the verdict semantics.

## Summary

| Class | sound | unverified | broken | Total |
|-------|------:|-----------:|-------:|------:|
| external-formal | 0 | 0 | 0 | 0 |
| internal-formal | 0 | 0 | 0 | 0 |
| informal-link | 0 | 0 | 0 | 0 |
| **Total** | **0** | **0** | **0** | **0** |

_Counts populated by `/reference-audit fan-out`._

## References (Pending Verification)

```yaml
references: []
```

_Populated by `/reference-audit init`. Each entry: `id`, `claim`, `reference_target`, `source_doc`, `source_anchor`, `reference_class` (inferred), `extraction_method` (`regex` | `llm`)._

## Findings (broken)

_Populated by `/reference-audit fan-out`. Each entry below this heading represents a citation that does not resolve OR whose source contradicts the cited claim. These are the highest-priority findings to address._

<!-- per-finding detail blocks go here -->

## Findings (unverified)

_Populated by `/reference-audit fan-out`. Each entry represents a citation the researcher could not fully verify (paywalled source, ambiguous text, fetch failure, source silent on cited clause). In a regulated context, "I couldn't verify" is a real audit output, not a failure — these entries may need manual reviewer attention._

<!-- per-finding detail blocks go here -->

## Findings (sound)

_Populated by `/reference-audit fan-out`. Citations the researcher verified as resolving and supported by their cited source. Listed compactly — one line per finding for inventory; no detail block needed unless something is notable._

<!-- compact per-finding list goes here -->

## Open Resolutions

_Surfaced by the audit but requiring SME adjudication or project decision — not a defect in the citation itself but an action it points at. Examples:_

- _A `unverified` finding citing a paywalled standard where the cited clause exists in L1a but the project's L1b applicability file has not yet analyzed the clause for this project — route to the appropriate SME advisor (risk-management for ISO 14971 clauses, regulatory-affairs for FDA guidance, etc.) for an applicability call._
- _A `broken` finding suggesting that a referenced internal document should be authored — route to the relevant workstream owner._

<!-- adjudication items added here as the audit is read and acted on -->

## Provenance

- Extraction method: regex pass over the source doc + LLM pass over narrative prose with regex-extracted spans masked (D-202.12).
- Verdict bands: three-band — `sound | unverified | broken` (D-202.13).
- External-formal references verified by two-tier L1a + L1b consolidation (D-202.14).
- Finding `kind` enum is open — v1 emits the link-checking subset; v2 candidate kinds reserved per the skill's SKILL.md `## v2 Roadmap` section.
