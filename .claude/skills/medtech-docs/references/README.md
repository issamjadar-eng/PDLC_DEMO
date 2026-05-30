# medtech-docs — Reference Library

Source-of-truth distillations of regulatory standards, FDA guidance, and industry frameworks that underpin every medtech-docs project. Authored once in this skill; consumed by many downstream projects.

This is the **reference layer** of a two-tier regulatory-content architecture:

- **Reference (here)** — generic clause-level distillation of the standard or guidance. "What does IEC 62304 §5.3 say?" Maintained in one place; updated when the underlying document changes.
- **Applicability (per project, at `docs/external/<category>/`)** — project-specific analysis of how each clause applies to *this* device, which modules it touches, which sections defer to QMS, what's `[VERIFY]`'d, etc.

Agents grounded against a project should consult **both layers** when citing a standard: the project applicability file for "what this program has decided about this standard," and the reference file here for "what the standard itself says." Only this layer carries authoritative clause text.

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
- Source PDFs (under `source/`) and full-text markdown conversions (under `source-md/`) — raw upstream material, NOT indexed or exposed to agents directly

### Out of Scope (see instead)
- Project-specific applicability analysis — lives at `docs/external/{standards,fda-guidance,industry-frameworks}/` in the consuming project
- Clause-to-requirement trace — that's `docs/project/dhfs/<dhf>/design-controls/trace-matrix/` in the consuming project
- Structured regulatory-obligations catalog (Tier 1 obligations, per `/dhf-manifest`) — see `.claude/skills/dhf-manifest/data/tier1-regulatory/`
- Raw source files (`source/`, `source-md/`) — full-text original docs are pre-conversion artifacts; the project-console grounding surface auto-excludes them via path-segment rules

## Conventions

- Each standard / guidance document has a single distilled `.md` at its parent folder level
- Filenames are lowercase-kebab, typically `<acronym>-<short-name>.md` (`iec-62304.md`, `pccp-aiml-distilled.md`)
- The `-distilled.md` suffix is a legacy marker for FDA-guidance files; being phased out — future additions should use the plain `<name>.md` form seen in `standards/`
- Content starts with a scope paragraph, then a table-of-contents, then clause-by-clause sections
- Amendment citations (e.g. "IEC 62304 + Amd 1:2015") appear in the scope paragraph, not in the filename

## For Claude (when grounded against a consuming project)

When a question invokes a named standard, regulation, or framework:
1. **Start with the project's applicability file** at `docs/external/<category>/<name>.md` — that tells you what *this program* has decided
2. **Then pull the reference file here** for the clause-level content the applicability file is analyzing against
3. **Cite both** in the response footnotes (applicability first, reference second)
4. If the applicability file says `[VERIFY]` or defers a clause to QMS, don't invent an answer — acknowledge the gap and point the user to the right next step

## Changelog

- 2026-04-23: README authored. Motivated by project-console v1.7.4 tiered-grounding architecture exposing this folder as an extra grounding root. Previously the folder existed but was un-indexed by the assistant drawer.
