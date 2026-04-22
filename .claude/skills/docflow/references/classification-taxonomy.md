# Classification Taxonomy — Requirements & Design Controls

Canonical, industry-informed classification tags for regulated-project requirements. Anchored in standards the project is reviewed against (ISO/IEC 25010, ISO 14971, IEC 62304, IEC 62366, IEC 81001-5-1, 21 CFR 820/Part 11, MDR GSPR, HIPAA/GDPR).

Used by `/docflow adopt` Phase 5e (requirement-metadata inference) and the R1 two-table requirement convention in `converter.md` Phase 3. Read this file when adopting requirement documents; do not duplicate the taxonomy inline.

## Scope rule

This list is **NOT project-editable**. Keeping it canonical across projects lets submission reviewers (FDA, notified bodies) run comparable queries regardless of which project authored the docs ("how many safety-classified reqs?" returns meaningfully across projects). If a project needs a tag that isn't in this list, propose a registry-level update — don't fork locally.

Classification is **multi-valued**: a requirement can carry several tags simultaneously (e.g., `[functional, safety, regulatory]`). Tags are independent dimensions, not a single category.

Default: if no tag matches beyond the generic "does what the system does," apply `functional` alone.

## The 9 canonical tags

| Tag | Anchor standard(s) | What the tag means | Inference pattern (case-insensitive regex) |
|-----|---------------------|---------------------|-------------------------------------------|
| `functional` | ISO/IEC 25010 § Functional Suitability | Describes what the system does — a capability, action, output. Every req has at least this tag. | (default — always applied) |
| `safety` | ISO 14971, IEC 62304 | Mitigates a hazard, implements a risk control, or addresses patient/user harm per ISO 14971 risk file. Links to risk register. | `\b(hazard\w*\|harm\w*\|injur\w*\|adverse event\|risk control\|mitigat\w*\|patient safety\|use.?safety\|hazardous situation)\b` |
| `security` | IEC 81001-5-1, FDA pre-market cybersecurity guidance | Cybersecurity posture: auth, encryption, integrity controls, access logs, vulnerability mitigation. | `\b(encrypt\w*\|authentic\w*\|authoriz\w*\|token\w*\|credential\w*\|session\|permission\w*\|access control\|audit log\|cybersec\w*\|vulnerab\w*\|tamper\w*\|SPDF\|threat model)\b` |
| `privacy` | HIPAA, GDPR, MDR Art. 62 | PHI/PII protection, consent capture, data minimization, subject-access rights. Distinct from security (which is how data is protected) — privacy is whose data is protected and on what grounds. | `\b(PHI\|PII\|patient privacy\|data protection\|consent\w*\|data subject\|HIPAA\|GDPR\|anonymiz\w*\|pseudonymiz\w*\|de.?identif\w*)\b` |
| `usability` | IEC 62366-1, ANSI/AAMI HE75 | Use-error mitigation, clinical ergonomics, human factors. Covers readable UI, unambiguous alerts, workflow safety. | `\b(use.?error\|human factor\w*\|usability\|ergonom\w*\|clinical workflow\|UX\|UI.*clinical\|alert\w*\|warning message\|confirm dialog)\b` |
| `performance` | ISO/IEC 25010 § Performance Efficiency | Speed, latency, throughput, resource utilization, response time bounds. | `\b(latency\|throughput\|response time\|performance\|speed\|capacity\|resource util\w*\|concurrent users\|load\w*\|scale\w*)\b` |
| `reliability` | ISO/IEC 25010 § Reliability | Availability, fault tolerance, error recovery, mean-time-between-failures, graceful degradation. | `\b(availab\w*\|failover\|recover\w*\|fault toler\w*\|resilien\w*\|uptime\|redundan\w*\|graceful degrad\w*\|MTBF\|backup\w*\|restore\w*)\b` |
| `interoperability` | DICOM, HL7 FHIR, IHE profiles, ISO/IEC 25010 § Compatibility | Standards-compliant data exchange: medical imaging (DICOM), clinical data (HL7/FHIR), workflow profiles (IHE). | `\b(DICOM\|HL7\|FHIR\|IHE\|interop\w*\|integration profile\|standard.*(compliance\|conform\w*)\|data exchange\|LDAP)\b` |
| `regulatory` | 21 CFR 820, 21 CFR Part 11, MDR GSPR, ISO 13485 | Specific regulatory compliance: records control, audit trails, electronic signatures, data integrity (ALCOA+), regulatory-specific requirements. | `\b(21.?CFR\|Part.?11\|audit trail\w*\|electronic record\w*\|ALCOA\|MDR\|GSPR\|ISO.?13485\|regulator\w*\|compliance (check\|requirement)\w*\|traceability)\b` |

## Priority and conflict rules

- **Order of evaluation**: Every regex runs independently. All matches apply. A requirement citing "encrypt PHI for HIPAA audit trail" gets `[functional, security, privacy, regulatory]`.
- **No suppression**: do not deduplicate by taxonomy precedence. A req is what it is.
- **`functional` always included**: the default tag is additive, not mutually exclusive. A safety-classified req is ALSO functional (it implements a safety function).
- **Confidence**: tags that matched via regex get `inferred: true, confidence: high` (the pattern is definitional). Tags that a human adds manually get `inferred: false`.

## What does NOT get a tag

- **Maintainability / portability / testability** (ISO/IEC 25010 dimensions) — typically SDLC concerns, rarely in user-facing SRS. Propose adding if a project starts authoring these.
- **Localization / internationalization** — proposed-but-deferred; emerging concern for medical device global launches. Revisit when a project's SRS surfaces the requirement.
- **Traceability** as a standalone tag — handled by the structured `Traces To` field per requirement, not a classification.

## Using this taxonomy

Adopt-time inference: the adopter scans the requirement's Description + AC text, applies each regex, collects all matches, adds `functional` as the baseline. Emits to the attributes table's `Classification` column as a comma-separated list: `` `functional`, `safety`, `regulatory` ``.

Review-time check: the reviewer's Phase 4 audit flags requirements with only `functional` when the Description + AC text contains regex-matching content for other tags (suggests under-classification). Also flags requirements with tags not in the canonical list (either taxonomy drift or a project-forked tag — surface for harmonization).

Dashboard aggregation: the working MD's frontmatter `requirements.classification` block counts occurrences per tag. Cross-DHF and cross-project dashboards pivot on these counts.

## Changelog

- 2026-04-21: Stem-matching fix (task ben/090 Phase 1). Added `\w*` suffix to every stem alternative (`encrypt` → `encrypt\w*`, `authentic` → `authentic\w*`, `hazard` → `hazard\w*`, etc.) so inflected forms match (encrypted / encrypting / encryption; authenticate / authentication; hazards / hazardous). Full-word alternatives (DICOM, HL7, PHI, HIPAA, etc.) retain exact `\b...\b` boundaries. Root cause: original `\bstem\b` patterns required a word boundary after the stem, which prevented stems from matching their inflected forms — causing silent under-classification observed in task 089 session 5's Pre-Op SRS re-adopt (safety=0 vs v29's 3; privacy=0 vs 1; usability=0 vs 2). `infer_requirement_metadata.py` `_CLASSIFICATION_PATTERNS` list updated in lockstep.
- 2026-04-20: Initial version. 9 tags anchored in ISO 25010, ISO 14971, IEC 62304, IEC 62366, IEC 81001-5-1, 21 CFR Part 11, MDR GSPR, HIPAA/GDPR, DICOM/HL7. Created during task 075 Phase 1f for the R1 requirements-table convention.
