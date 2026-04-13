# FDA Guidance -- Project Compliance Files

Project-specific applicability reports for each FDA guidance document relevant to this project. Each file contains module impact analysis, deliverables mapping, PCCP considerations, and a machine-readable verification report.

Full guidance text and distilled requirements are maintained in the skill reference library at `.claude/skills/medtech-docs/references/fda-guidance/` (structure: `source/` for PDFs, `source-md/` for markdown conversions, `*-distilled.md` at root for distilled requirements).

## Guidance Documents

| # | Guidance | Status | Project File | Full Text Reference |
|---|---------|--------|-------------|-------------------|

## How These Guidances Map to Our Work

_Populate this section with a text diagram showing which guidance documents feed into which project activities (Q-Sub prep, device classification, PCCP development, 510(k) submission, etc.)._

## File Format

Each project compliance file follows a standard structure:

1. **Header** -- Guidance title, reference links to skill library, applicability status, review date
2. **Applicability** -- Why the guidance applies, key implications for our device
3. **Module Impact** -- How guidance affects each device module
4. **Key Deliverables -- Repo Mapping** -- Table mapping deliverables to repo locations with existence status
5. **PCCP Considerations** -- How guidance interacts with PCCP strategy
6. **Verification Report** -- Machine-readable checklist with status markers (`[x]` passed, `[ ]` pending, `[!]` failed, `[~]` not applicable)
7. **Changelog** -- Date, author, summary of changes

## Conventions

- One file per guidance document, named by short topic: `topic.md` (e.g., `pccp-aiml.md`, `qsub.md`)
- Status markers in verification reports: `[x]` passed, `[ ]` pending, `[!]` failed, `[~]` not applicable
- `[VERIFY]` markers indicate areas where information needs confirmation against source documents
- Reference links point to skill library at `.claude/skills/medtech-docs/references/fda-guidance/source-md/`
- Note knowledge cutoff -- flag if guidance may have been updated

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| YYYY-MM-DD | XX | Initial version -- created by /medtech-docs init |
