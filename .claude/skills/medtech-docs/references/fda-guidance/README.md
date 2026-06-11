# FDA Guidance — Reference Distillations

Distilled summaries of every FDA guidance document medtech projects commonly rely on. Generic reference text — project-specific applicability analysis lives at `docs/external/fda-guidance/` in each consuming project.

## Distilled Guidances

| Guidance | File | Subject |
|----------|------|---------|
| 510(k) Substantial Equivalence | [`510k-se-distilled.md`](510k-se-distilled.md) | What's required to demonstrate substantial equivalence in a 510(k) |
| 510(k) Electronic Submission Template (eSTAR) | [`510k-estar-distilled.md`](510k-estar-distilled.md) | Mandatory electronic format for ALL 510(k) types since Oct 1, 2023 per FD&C § 745A(b)(3) — eSTAR structure, technical screening replacing RTA, exemptions, no waivers; Oct 2, 2023 final (GUI00019006), partially binding |
| Abbreviated 510(k) Program | [`abbreviated-510k-distilled.md`](abbreviated-510k-distilled.md) | SE via reliance on FDA guidance / special controls / recognized consensus standards, reviewed as summary reports + declarations of conformity; standard review clock; PCCP-introduction-capable type (with Traditional); Sep 2019 final (doc 905, supersedes the 1998 New 510(k) Paradigm Abbreviated content) |
| AI/DSF Lifecycle | [`ai-dsf-lifecycle-distilled.md`](ai-dsf-lifecycle-distilled.md) | FDA expectations across the AI Device Software Function lifecycle |
| CDS (Clinical Decision Support) | [`cds-distilled.md`](cds-distilled.md) | Criteria for device vs non-device CDS software |
| Cybersecurity Premarket | [`cybersecurity-distilled.md`](cybersecurity-distilled.md) | FDA's premarket cybersecurity submission expectations |
| Human Factors — Submission Content | [`human-factors-distilled.md`](human-factors-distilled.md) | Risk-based HF Submission Categories 1/2/3 (Figure 1 Decision Points A–D), URRA / comparative-URRA tabular formats, 8-section HFE/UE report outline — May 29, 2026 final (GUI01500052; finalizes the Dec 2022 draft; complements, does not supersede, the 2016 Applying HF/UE process guidance) |
| MDDS (Medical Device Data Systems) | [`mdds-distilled.md`](mdds-distilled.md) | Transfer / store / convert / display of medical device data — Non-Device-MDDS (software, statutorily not a device per Cures Act § 3060) vs Device-MDDS (hardware, enforcement discretion); 2022 update to original 2015 guidance |
| MFD (Multiple Function Device) | [`mfd-distilled.md`](mfd-distilled.md) | Impact analysis across device / non-device functions in one product |
| PCCP — General | [`pccp-general-distilled.md`](pccp-general-distilled.md) | Predetermined Change Control Plan — general guidance |
| PCCP — AI/ML | [`pccp-aiml-distilled.md`](pccp-aiml-distilled.md) · [`pccp-aiml-full.md`](pccp-aiml-full.md) | AI/ML-specific PCCP guidance + full-text reference |
| Predicate Selection Best Practices (**DRAFT**) | [`predicate-selection-distilled.md`](predicate-selection-distilled.md) | Four best-practice factors for narrowing valid predicates to *the* predicate (well-established methods; real-world safety/performance via MAUDE/MDR/MedSun; no unmitigated safety signals; no design-related recall) + 510(k) Summary selection narrative — Draft, Sep 7, 2023 (GUI00020006); not for implementation |
| Q-Submission | [`qsub-distilled.md`](qsub-distilled.md) | The 5 Q-Sub types (Pre-Sub, SIR, Study Risk Determination, Informational Meeting, PMA Day 100), MDUFA timelines, Pre-Sub content checklist — May 29, 2025 final guidance (GUI00001677, supersedes June 2023 + Feb 1998 PMA Day 100) |
| Q-Submission eSTAR (Draft) | [`qsub-estar-draft-distilled.md`](qsub-estar-draft-distilled.md) | Electronic submission template (eSTAR) for Q-Subs — currently Pre-Subs only; future required format per FD&C § 745A(b)(3). Draft May 29, 2025 (GUI00007041); FR Doc 2025-09615 announced availability; comment deadline Jul 28, 2025 |
| Special 510(k) Program | [`special-510k-distilled.md`](special-510k-distilled.md) | Which *kind* of 510(k) a change to the manufacturer's own device can ride — Special (30-day, design-control summary review) vs Traditional/Abbreviated; Sep 2019 final (doc 18008, supersedes the 1998 New 510(k) Paradigm Special content) |
| Device Changes (parent) | [`sw-changes-distilled.md`](sw-changes-distilled.md) | When a change to an existing device requires a new 510(k) — parent guidance for **non-software** changes (labeling / technology / materials flowcharts + Section E risk-based assessment); Oct 25, 2017 final (doc 1500054) |
| Software Changes (software-specific sibling) | [`sw-changes-software-distilled.md`](sw-changes-software-distilled.md) | When a **software** (incl. firmware) change to an existing device requires a new 510(k) — the software-specific sibling of the parent device-changes guidance above; cybersecurity / return-to-spec / risk & risk-control / clinical-performance gates + § VI change-type factors; Oct 25, 2017 final (doc 1500055, docket FDA-2016-D-2021) |
| Software Functions | [`sw-functions-distilled.md`](sw-functions-distilled.md) | Software-functions-scoping across the Cures Act categories |

## Scope

### In Scope
- Key requirements, decision criteria, and deliverable expectations from each guidance
- Cross-guidance interaction notes (e.g. PCCP + AI/ML, sw-changes + 510(k))
- `-distilled.md` = concise summary; `-full.md` (rare) = fuller-fidelity reference

### Out of Scope (see instead)
- **Device-specific applicability analysis** — `docs/external/fda-guidance/<name>.md` in each project. That's where module-level applicability, `[VERIFY]`s, and deferrals live.
- **Full source PDFs and markdown conversions** — under `source/` and `source-md/` in this folder. Grounding/search surfaces exclude them (path-segment rules) so agents don't pull ~50 KB full texts into routine grounding — but `source-md/` is deliberately kept as the **escalation tier**: read it directly when a distillation isn't enough (see "For Claude" step 5 below).
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
5. **Escalate to the full text when the distillation isn't enough.** Every guidance here bundles its full text at `source-md/<basename>.md` (strip the `-distilled` suffix: `pccp-general-distilled.md` → `source-md/pccp-general.md`). Read it when the question needs **exact guidance wording** (e.g., Q-Sub/510(k) text quoting FDA), content the distillation omits (appendices and worked examples are routinely dropped from distillations), or footnote-level detail. The distillation stays the entry point and the citation; source-md is the fidelity backstop. (`source/<basename>.pdf` is the archived original — for humans and re-distillation; agents read source-md.)

## Changelog

- 2026-04-23: README authored as part of project-console v1.7.4 rollout (skill-library exposed to assistant drawer grounding).
