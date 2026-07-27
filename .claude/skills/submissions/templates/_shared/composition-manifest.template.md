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

<!-- scaffold: emit one row per content doc in THIS filing's profile (see
     submissions SKILL.md § Filing-type profiles) — do NOT carry another
     profile's pieces. A 510(k) lists indications-for-use / 510(k)-summary /
     substantial-equivalence / performance-testing / truthful-accuracy; a Q-Sub
     lists intended-use / pccp-summary / fda-questions; a PMA lists SSED / etc.
     DHF-derived exhibits (proposed labeling PDF, consensus-standards list /
     declarations of conformity) are listed in the "attached from DHF" table
     below — they are controlled-record PDFs, not ./<file>.md docs. The cover
     letter's Attachments section must align 1:1 with this list.
     PCCP co-filing: if this 510(k) co-files a PCCP, the 510(k)-Summary row MUST
     note it carries the public-facing PCCP content (planned modifications,
     testing methods, validation activities + performance requirements, user-
     communication means — General PCCP draft § V.C; 510k-summary template § 8).
     This is a cross-filing handoff (authored in the PCCP, delivered in the 510(k)
     Summary) — track it here so it can't fall through at assembly time. -->

**Formal FDA submission deliverables** (authored in this filing folder)

| Piece | Path | Purpose in {{FILING_SHORT}} | Tracker Row |
|-------|------|------------------------------|-------------|
| {{PIECE}} | [`{{PIECE_FILE}}`](./{{PIECE_FILE}}) | {{PIECE_PURPOSE}} | {{ROW}} |

**Attached from the DHF** (controlled-record PDFs — not authored here)

| Piece | DHF source | Purpose in {{FILING_SHORT}} | Tracker Row |
|-------|------------|------------------------------|-------------|
| {{DHF_EXHIBIT}} | {{DHF_EXHIBIT_PATH}} | {{DHF_EXHIBIT_PURPOSE}} | {{ROW}} |

**Supporting technical architecture**

| Piece | Path | Purpose in {{FILING_SHORT}} | Tracker Row |
|-------|------|------------------------------|-------------|
| System SAD | {{SAD_PATH}} | Module architecture + SaMD boundary | {{ROW}} |

**Transmission-blocking briefs** (optional — where a filing has gating pre-work, e.g. Q-Sub pre-meeting strengtheners; omit if none)

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
