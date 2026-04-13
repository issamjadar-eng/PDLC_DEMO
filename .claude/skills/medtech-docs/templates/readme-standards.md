# Standards

Applicable regulatory standards for this device. Each standard has a dedicated markdown file with distilled requirements, clause-by-clause relevance, and module applicability.

For non-standard frameworks (NIST CSF, OWASP, GMLP, etc.), see `docs/external/industry-frameworks/`.

## Distilled Standards

Standards with per-file requirement breakdowns in this folder:

| Standard | File | Title | Category |
|----------|------|-------|----------|

## Deferred Standards (QMS-Level)

Standards managed at the organizational QMS level, not distilled here:

| Standard | Title | Notes |
|----------|-------|-------|

## Supplementary Technical Reports

Reports that provide guidance on applying their parent standards but are not independently auditable:

| Report | Title | Parent Standard |
|--------|-------|-----------------|

## Standards-to-Module Mapping

_Populate with a table showing which standards apply to which device modules, and under what conditions (e.g., "Required", "If SaMD", etc.)._

| Standard | Module 1 | Module 2 | Module N | Notes |
|----------|----------|----------|----------|-------|

## Evaluated — Not Required

Standards evaluated and determined not applicable, with rationale:

| Standard | Title | Rationale for Exclusion |
|----------|-------|------------------------|

## Conventions

- **One file per standard**: `standard-number-short-name.md`
- Each file contains: overview, clause-by-clause requirements, module applicability, verification checks, key deliverables
- Requirements are distilled for use by compliance evaluation skills
- Every file must include a `## Verification Checks` section (machine-readable, read by `/medtech-docs dashboard`)

## For Claude

- When drafting 510(k) or design control documents, check this folder to ensure referenced standards are addressed
- Flag any standard requirement that may impact the PCCP change categories
- Note that established device companies likely have ISO 13485 QMS in place — verify before assuming gaps

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| YYYY-MM-DD | XX | Initial version — created by /medtech-docs init |
