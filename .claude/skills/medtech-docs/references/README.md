# medtech-docs — Reference Library

Source-of-truth distillations of regulatory standards, FDA guidance, and industry frameworks that underpin every medtech-docs project. Authored once in this skill; consumed by many downstream projects.

This is the **reference layer** of a two-tier regulatory-content architecture:

- **Reference (here)** — generic clause-level distillation of the standard or guidance. "What does IEC 62304 §5.3 say?" Maintained in one place; updated when the underlying document changes.
- **Applicability (per project, at `docs/external/<category>/`)** — project-specific analysis of how each clause applies to *this* device, which modules it touches, which sections defer to QMS, what's `[VERIFY]`'d, etc.

Agents grounded against a project should consult **both layers** when citing a standard: the project applicability file for "what this program has decided about this standard," and the reference layer here for "what the source itself says." Within this reference layer there are **two tiers**, and they are not equal in authority:

- **`source-md/<base>.md` (faithful full text) — the authoritative grounding + citation source.** A byte-faithful conversion of the upstream original (FDA-guidance PDF or eCFR XML). Where it exists, ground and cite *this*. Indexed by semantic search.
- **The distilled `<name>.md` at the parent level — a labelled finding aid, NOT a citation source.** A paraphrase for quick orientation and early analysis; it carries a `🔎 Finding aid` banner that routes to the authoritative source. It is the better *findability* surface (it front-loads the key point into the indexed summary), so it stays indexed — but a distilled paraphrase is a *derived* layer and is never the thing you cite, exactly as `articles/` and `tools/knowledge-packs/` are never canonical. For sources with no in-repo full text (copyrighted ISO/IEC standards, most frameworks), the distilled file's banner says so and names the external original as the sole authority.

## Subfolders

| Folder | Content | Example |
|--------|---------|---------|
| [`standards/`](standards/) | IEC / ISO consensus standards | IEC 62304 Software Lifecycle, ISO 14971 Risk Management |
| [`fda-guidance/`](fda-guidance/) | FDA guidance documents — distilled summaries + full-text | 510(k), PCCP, SaMD, CDS, Cybersecurity Premarket, MDDS |
| [`industry-frameworks/`](industry-frameworks/) | Non-standard interoperability & best-practice frameworks | DICOM, HL7 FHIR, NIST CSF, GMLP, OWASP |
| [`regulations/`](regulations/) | US federal regulations (21 CFR) — verbatim text + distilled cross-references | 21 CFR Part 807 (Establishment Registration / 510(k) when required), Part 880 (MDDS), Part 892 (Radiology Devices / QIH) |

## Scope

### In Scope
- Clause-level distillation of each standard / guidance document
- Device-agnostic summaries usable across all medtech projects
- Source originals (under `source/` — PDFs for FDA guidance, XML for eCFR regulations) and faithful full-text markdown conversions (under `source-md/`). **`source-md/` IS the authoritative grounding + citation surface** and IS indexed by semantic search. **`source/` originals are the byte-correct archive** (verify verbatim quotes against them) and are NOT indexed — they are not text the summarizer can usefully embed. The indexer embeds only a ≤400-char per-heading summary, not raw text, so indexing a 50 KB `source-md/` costs a handful of small summaries — there is no "full text competing with the distillation"

### Out of Scope (see instead)
- Project-specific applicability analysis — lives at `docs/external/{standards,fda-guidance,regulations,industry-frameworks}/` in the consuming project
- Clause-to-requirement trace — the consuming project's trace-matrix deliverable (location per its `project.yml dhfs[].path` / trace-matrix config)
- Structured regulatory-obligations catalog (Tier 1 obligations, per `/dhf-manifest`) — see `.claude/skills/dhf-manifest/data/{fda-guidance,standards,industry-frameworks}/`
- `source/` originals (PDF/XML) — the byte-correct archive, excluded from indexing (not the grounding surface — `source-md/` is). Read them only to verify a verbatim quote. (`source-md/` is explicitly **in** scope above — the authoritative grounding tier.)

## Conventions

- Each standard / guidance document has a single distilled `.md` at its parent folder level
- **Every distilled file MUST carry the finding-aid banner (MANDATORY).** Immediately under the H1 — as a **plain bold paragraph, not a blockquote** — place a banner that leads with the exact greppable token `🔎 **Finding aid — NOT the authoritative source.**` and names the authoritative source. Plain-paragraph placement is load-bearing: the file-locator's first-paragraph extractor skips lines starting with `>`, so a blockquote banner would be invisible to the embedded search summary; a plain paragraph under H1 leads the summary, so a search hit on a distilled file immediately signals "finding aid → authoritative source." Three banner shapes by source tier:
  - **In-repo full text exists (FDA guidance):** "Ground and cite the authoritative full text `source-md/<base>.md`; verify any quote against the byte-correct `source/` PDF."
  - **In-repo full text exists (CFR regulations):** "Ground and cite the faithful full text `source-md/<base>.md` (no-LLM eCFR transcription); verify currency against the live eCFR."
  - **No in-repo full text (copyrighted ISO/IEC standards, most frameworks):** "No faithful full-text copy exists in this repository (copyrighted); the original named in the header above is the sole authority — do not infer clause content."
- Filenames are lowercase-kebab, typically `<acronym>-<short-name>.md` (`iec-62304.md`, `pccp-aiml-distilled.md`)
- The `-distilled.md` suffix is a legacy marker for FDA-guidance files; being phased out — future additions should use the plain `<name>.md` form seen in `standards/`
- Content starts with a scope paragraph, then a table-of-contents, then clause-by-clause sections
- Amendment citations (e.g. "IEC 62304 + Amd 1:2015") appear in the scope paragraph, not in the filename

## For Claude (when grounded against a consuming project)

**The consumption ladder has four rungs — climb in order, never skip downward, never stop short when the claim needs more fidelity:**

1. **Project applicability** — `docs/external/<category>/<name>.md`: what *this program* has decided about the source (module applicability, `[VERIFY]`s, QMS deferrals). Start here. If it says `[VERIFY]` or defers a clause to QMS, don't invent an answer — acknowledge the gap and point the user to the right next step.
2. **Registry distillation (this folder)** — `<category>/<name>.md`: a **finding aid only** — use it to orient and locate the relevant section quickly. It is a paraphrase; do **not** cite it as the source's text. Its `🔎 Finding aid` banner names the authoritative source for the claim.
3. **Faithful full text — the grounding + citation source (where an in-repo copy exists)** — `<category>/source-md/<basename>.md`: a byte-faithful conversion of the original. **This is what you ground on and cite** for the source's text. Bundled for **fda-guidance** and **regulations** (eCFR). Cite **both** the project-applicability file (rung 1) and this source-md (applicability first, source-md second) in response footnotes. Where no in-repo full text exists (copyrighted ISO/IEC standards, most frameworks — rung 4), the distilled file is the best available local text but is explicitly non-authoritative: say the original must be consulted and do not infer clause content.
4. **The open web (last resort)** — only when rungs 1–3 can't answer:
   - **Regulations (CFR)** — fetch the live eCFR versioner API (`https://www.ecfr.gov/api/versioner/v1/full/<date>/title-21.xml?part=<N>`; the human-viewer URLs redirect automated fetchers). CFR text is public domain and regulations change — also use this rung for *currency* checks when a distillation's retrieval date is stale.
   - **FDA guidance / FR notices / FDA databases** — prefer machine-readable endpoints (Federal Register API, openFDA); `fda.gov` HTML and media downloads are frequently bot-blocked — note the block and return unverified rather than guessing.
   - **Standards (ISO/IEC) and most frameworks** — clause text is paywalled and is on **no rung**: web search may locate TOCs/previews, but say the original standard must be consulted rather than inferring clause content.

A section's absence from a distillation is never evidence the source is silent.

## Changelog

- 2026-06-15: **Grounding-posture inversion.** `source-md/` (faithful full text) is now the authoritative grounding + citation source and IS indexed; the distilled file is recast as a labelled **finding aid** that routes to it (never the citation). Made the `🔎 Finding aid` banner MANDATORY for every distilled file (plain-paragraph-under-H1 so it lands in the search summary) and rewrote the "For Claude" ladder (rung 2 = finding aid, rung 3 = source-md = cite-this). Corrects the prior "source-md is not a grounding surface / 50 KB competes with distillation" framing — the indexer embeds only ≤400-char summaries, so indexing source-md is cheap. Aligns the reference library with the project's `*-not-canonical` posture (derived layers are never canonical — go to source). Regulations gained a `source-md/` tier (verbatim eCFR transcription) in the same pass.
- 2026-04-23: README authored. Motivated by project-console v1.7.4 tiered-grounding architecture exposing this folder as an extra grounding root. Previously the folder existed but was un-indexed by the assistant drawer.
