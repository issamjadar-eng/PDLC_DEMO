# FDA Guidance — Reference Distillations

Distilled summaries of every FDA guidance document medtech projects commonly rely on. Generic reference text — project-specific applicability analysis lives at `docs/external/fda-guidance/` in each consuming project.

## Distilled Guidances

| Guidance | File | Subject |
|----------|------|---------|
| 510(k) Substantial Equivalence | [`510k-se-distilled.md`](510k-se-distilled.md) | What's required to demonstrate substantial equivalence in a 510(k) |
| AI/DSF Lifecycle | [`ai-dsf-lifecycle-distilled.md`](ai-dsf-lifecycle-distilled.md) | FDA expectations across the AI Device Software Function lifecycle |
| CDS (Clinical Decision Support) | [`cds-distilled.md`](cds-distilled.md) | Criteria for device vs non-device CDS software |
| Cybersecurity Premarket | [`cybersecurity-distilled.md`](cybersecurity-distilled.md) | FDA's premarket cybersecurity submission expectations |
| MFD (Multiple Function Device) | [`mfd-distilled.md`](mfd-distilled.md) | Impact analysis across device / non-device functions in one product |
| PCCP — General | [`pccp-general-distilled.md`](pccp-general-distilled.md) | Predetermined Change Control Plan — general guidance |
| PCCP — AI/ML | [`pccp-aiml-distilled.md`](pccp-aiml-distilled.md) · [`pccp-aiml-full.md`](pccp-aiml-full.md) | AI/ML-specific PCCP guidance + full-text reference |
| Q-Submission | [`qsub-distilled.md`](qsub-distilled.md) | Pre-Sub meeting mechanics and package expectations |
| Software Changes | [`sw-changes-distilled.md`](sw-changes-distilled.md) | When a software change requires a new 510(k) |
| Software Functions | [`sw-functions-distilled.md`](sw-functions-distilled.md) | Software-functions-scoping across the Cures Act categories |

## Scope

### In Scope
- Key requirements, decision criteria, and deliverable expectations from each guidance
- Cross-guidance interaction notes (e.g. PCCP + AI/ML, sw-changes + 510(k))
- `-distilled.md` = concise summary; `-full.md` (rare) = fuller-fidelity reference

### Out of Scope (see instead)
- **Device-specific applicability analysis** — `docs/external/fda-guidance/<name>.md` in each project. That's where module-level applicability, `[VERIFY]`s, and deferrals live.
- **Full source PDFs and markdown conversions** — under `source/` and `source-md/` in this folder, but the project-console grounding surface auto-excludes those (path-segment rules) so agents don't pull the ~50 KB full-text into grounding. Humans can still read them directly from the filesystem.
- **Consensus standards** (IEC/ISO) — see `../standards/`
- **Industry frameworks** (DICOM, NIST CSF, GMLP, etc.) — see `../industry-frameworks/`

## Conventions

- Distilled files use the `<short-name>-distilled.md` pattern (legacy; new additions should consider dropping the suffix)
- H1 is "`FDA Guidance — <Title>`"
- Opens with a scope paragraph + key-question TL;DR, then section-by-section distillation
- Cross-references to other guidances use relative links

## For Claude (when grounded against a consuming project)

When asked about an FDA guidance document:
1. Check `docs/external/fda-guidance/<name>.md` in the project for the applicability call — that's how this program has decided to scope against it
2. Check the distilled file here for the guidance's actual requirements
3. Cite both in footnotes
4. If the question involves PCCP or AI/ML, cross-check against both `pccp-general-distilled.md` AND `pccp-aiml-distilled.md` — they interact

## Changelog

- 2026-04-23: README authored as part of project-console v1.7.4 rollout (skill-library exposed to assistant drawer grounding).
