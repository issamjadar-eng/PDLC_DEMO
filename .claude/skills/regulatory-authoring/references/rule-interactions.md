# Rule Interactions — precedence & routing

Load this when **two rules touch the same span** or you're unsure which rule owns a finding. It consolidates every precedence pair and routing decision from the standard into one place, so collisions resolve here rather than in scattered notes.

## Precedence pairs (when two rules apply, the winner)

| Pair | Winner | Why |
|------|--------|-----|
| **D9 vs D8** | **D9** | A link to a `submissions/` proposal is a *wrong trace target* (D9), not merely a citation-format issue (D8). Fix the target, not the path. |
| **D15.6 vs D14.1** | **D15.6** for an EU-routed doc | D14.1 allows ≤1 PCCP cross-reference; D15.6 requires **zero** in EU text. For an EU doc, zero governs. |
| **D12 vs R7** | **D12** | A brand/vendor token flagged for removal by D12 is **not** an acronym for R7 to define. Remove it; don't add a Terms row. |
| **R1 vs W10** | **R1** in the filed body | W10 permits `will` only *outside* the filed body; inside it, R1's "no promissory language" is absolute. |

## Claim routing (R2 / R3 / R9 — what to do with a declarative statement)

Decide what kind of statement you have, then route:

```
Is it a design REQUIREMENT (a "shall" / "the system <does X>" spec)?
   → R2: keep it; ensure it has an acceptance criterion + a trace target (D9). NEVER delete for lacking inline evidence.
Is it a CLAIM of an achieved property / performed activity (performance, safety, security, quality)?
   ├─ evidence exists (or is planned)? → R3: pair it to the evidence artifact (or a managed TBD, D10).
   └─ no evidence and none planned?    → R9: remove it, or convert to a managed TBD. NEVER re-voice into confident prose.
Is it a scope-boundary NEGATIVE / limitation ("MRI is not supported")?
   → R1 / R5: state it flatly. NOT an R9 target.
```

The trap R9 guards: applying R5 (no hedging) + R1 (declarative) mechanically turns "we believe X is robust" → "X is robust" — a confident, unsupported, harder-to-detect false claim. R9 stops that. But R9 must not swallow a legitimate **requirement** (its evidence is the downstream trace, not an inline pointer) or a **limitation** (R1/R5 own it).

## Adjective routing (W2 / W11 / R5 + fallthrough)

| The adjective is… | Route | Action |
|-------------------|-------|--------|
| Measurable but vague ("fast", "accurate", "robust", "real-time") | **W2** | Replace with number+unit+tolerance, or a managed-TBD placeholder (never bare, never invented) |
| Marketing/hype ("seamless", "best-in-class", "cutting-edge") | **W11** | Delete; state the capability |
| A hedge phrase ("we believe", "should generally", "it appears") | **R5** | State flatly |
| Vague qualifier matching none of the above ("industry-standard", "sufficient", "appropriate") | **fallthrough → R3 / W2** | It's an underspecified claim — name the evidence (R3) or gate it as a TBD (W2/D10) |

Route each adjective to exactly one bucket; don't double-report one span (note: "robust" appears in both the W2 lint list and R9's examples — count it once).

## Tier-scope quick reference

- **`[filed-only]`** rules apply only to the Filed tier: R1 (+R1.1–R1.4), R3, R5, R6, R7 (Terms-*completeness* only — *consistency* applies all tiers), R9, W2, W11, and the filed-body D-rules D5, D8, D9, D10, D11, D12, D13, D14, D15.
- **Cross-tier** (apply to internal rendered tiers too): the other W craft rules, and the structural D-rules D1, D2, D3, D4, D6, D7.
- **Never** applies to Metadata HTML comments.
- **Document-control header** (D3) is *visible controlled metadata* — present and never `🔒`-wrapped, distinct from the internal draft-status banner (which *is* wrapped) and from comment-metadata (not rendered).

## Where a rule's own tag and a list disagree

The **rule-level tag wins** over any summary list. If the standard's `[filed-only]` enumeration and a rule header ever diverge, follow the header.
