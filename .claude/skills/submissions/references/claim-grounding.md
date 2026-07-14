# Rule: A factual claim about an external primary source must be grounded in that source

A submission document (device description, predicate/substantial-equivalence summary,
intended-use, PCCP summary) routinely states facts **about an external primary source** —
a predicate device's cleared 510(k), a De Novo decision summary, a PMA SSED, a competitor
filing. Examples: *"the predicate's software documentation level is Basic," "the predicate
IFU covers skeletally mature patients," "the reference device's output is an interactive
report."*

Every such fact must be **grounded in the primary source itself** — the actual filing PDF,
at a specific page, with a verbatim quote — **not** paraphrased from a sibling analysis
`.md` while the primary source sits unread.

## Why this exists (the failure it prevents)

The most common way a wrong fact about a predicate reaches a regulator:

1. An analyst extracts a fact into a working `.md` (e.g. `predicate-selection.md`).
2. A later document restates the fact from that sibling `.md`.
3. The **primary source PDF is in the repo but is never opened** — it gets parked in the
   provenance sidecar's `sources_not_consulted_but_potentially_relevant` with a reason like
   *"facts already extracted into sibling .md docs."*
4. The fact is now two hops from the source, with no gate forcing verification. If it was
   wrong (or terminology-shifted, or the source's own comparison table said something
   different), nothing catches it — a reviewer reading the actual filing does.

Source-**drift** pinning (`provenance stamp/check`) does not catch this: it watches whether
a *consulted* source changed, not whether an *asserted fact* is supported by a source that
was never consulted.

## The rule

1. **Consult the primary source.** If a document asserts a fact about an external filing,
   open that filing (the PDF / summary), do not rely on a sibling summary alone.
2. **Record it as consulted, with a quote.** In `_provenance/<doc>.provenance.yml`, the
   source goes in `sources_consulted` (never only in `sources_not_consulted`), and the fact
   goes in `claims_to_source[]` with structured grounding:
   ```yaml
   claims_to_source:
     - claim: "<the exact factual assertion>"
       source_path: <repo-relative path to the primary source, e.g. a cleared-filing PDF>
       source_page: <int>                     # page in the PDF
       quote: "<verbatim substring of the source that supports the claim>"
   ```
3. **Let the gate verify it.** `provenance check` confirms the quote resolves in the pinned
   source and blocks transmit on **ungrounded-claim**. Re-run after any source re-pin.
4. **Terminology transitions are claims too.** When a source uses a vocabulary that has since
   changed (e.g. an older filing's *Level of Concern: Minor/Moderate/Major* vs the current
   *Documentation Level: Basic/Enhanced*), quote the source's actual words and add a
   reconciliation note in the document body — do not silently map one scale onto the other.

## Scope

Applies to factual claims about **external primary sources** (other parties' cleared/decided
filings, standards text, guidance text). It does **not** require a quote for:
- claims grounded in the project's own in-repo documents (those are covered by source-drift
  pinning — the `sections`/`decisions`/`terms` + `stamp` path), or
- narrative/rationale that interprets rather than asserts a source fact.

## Interaction with other conventions

- **Source-drift pinning** (`provenance stamp/check`, this skill) — the sibling mechanism;
  drift watches *consulted in-repo sources*, grounding watches *asserted claims about primary
  sources*. Both run under `provenance check`; both are transmit-blocking.
- **Reference-audit** (`/reference-audit`, `regulatory-authoring`) — verifies *cited*
  references against the byte-correct source. Grounding is upstream of that: it forces a
  factual claim to *carry* a source pin in the first place, so there is something to audit.
- **Ground-in-contracts / audit-wiring rules** — same principle one layer down: assert from
  the canonical source, not from a paraphrase or from memory.
