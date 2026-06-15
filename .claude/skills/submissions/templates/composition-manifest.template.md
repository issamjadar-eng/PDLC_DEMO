# Composition Manifest — {{FILING_LABEL}}

> **🔒 INTERNAL — NOT TRANSMITTED.** Sponsor-side package-assembly artifact (tracker source of truth, milestone projection, readiness gates). Never sent to FDA; the FDA-facing package listing is the cover letter Attachments section, which must align 1:1 with this manifest before transmission.

_Snapshot of which pieces of which DHF(s) are included in this filing. Source of truth for `/tracker build`, `/submissions render`, and the submission package itself._

## Filing Identification

| Field | Value |
|-------|-------|
| Filing type | {{FILING_TYPE}} |
| Filing ID | {{FILING_ID}} |
| Submission folder | `docs/project/submissions/{{FILING}}/` |
| Milestone | {{MILESTONE}} |
| Regulatory pathway | {{PATHWAY}} |
| Target filing date | {{TARGET_DATE}} |
| DHFs spanned | {{DHFS}} |

## Included Pieces

### Required (per FDA {{FILING_TYPE}} guidance + milestone bindings)

**Formal FDA submission deliverables**

| Piece | Path | Purpose in {{FILING_SHORT}} | Tracker Row |
|-------|------|------------------------------|-------------|
| Cover letter | [`cover-letter.md`](./cover-letter.md) | Formal request / transmittal per FDA template | {{ROW}} |
| Device description | [`device-description.md`](./device-description.md) | FDA-facing architecture + clinical context | {{ROW}} |
| Proposed indications for use | [`intended-use.md`](./intended-use.md) | Draft IFU statement | {{ROW}} |
| {{FILING_SHORT}} summary | [`pccp-summary.md`](./pccp-summary.md) | Distilled scope for FDA discussion | {{ROW}} |
| Questions for FDA | [`fda-questions.md`](./fda-questions.md) | Consolidated primary question set | {{ROW}} |

**Supporting technical architecture**

| Piece | Path | Purpose in {{FILING_SHORT}} | Tracker Row |
|-------|------|------------------------------|-------------|
| System SAD | {{SAD_PATH}} | Three-module architecture + SaMD boundary | {{ROW}} |

**Required-Pre-Meeting strengthener briefs** (package should NOT transmit until these are at status ≥ `draft-v0.1`)

| Piece | Path | Purpose in {{FILING_SHORT}} | Status |
|-------|------|------------------------------|--------|
| {{BRIEF_NAME}} | [`{{BRIEF_FILE}}`](./{{BRIEF_FILE}}) | {{BRIEF_PURPOSE}} | **draft-v0.1 — transmission-blocking** |

### Supporting (advisory bindings — item-level architecture detail)

| Piece | Path | Purpose in {{FILING_SHORT}} | Tracker Row |
|-------|------|------------------------------|-------------|
| {{ITEM_SAD}} | {{ITEM_SAD_PATH}} | Item-module detail | {{ROW}} |

## Excluded Pieces

Intentionally out of scope for this filing. Listed so reviewers know what was not sent and why.

| Piece | Why excluded |
|-------|--------------|
| {{EXCLUDED}} | {{EXCLUDED_REASON}} |

## Cross-References

This manifest spans {{DHF_COUNT}} DHF(s). Folder-name → canonical-role resolution per project conventions.

## Reviewer Sign-off

_Roles only — per QMS. Author/contributor tracking lives in the Changelog below._

| Role | Name | Date | Signature |
|------|------|------|-----------|
| R&D Lead | _TBD_ | — | _pending_ |
| Regulatory Affairs | _TBD_ | — | _pending_ |
| Quality Assurance | _TBD_ | — | _pending_ |

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| {{DATE}} | {{AUTHOR}} | Initial manifest scaffolded via `/submissions scaffold {{FILING}}`. |
