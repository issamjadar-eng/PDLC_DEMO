# Federal Regulations — Reference Distillations

Section-level distillations of federal regulations that bind medical-device manufacturers. Used as the **reference layer** — projects consume these as ground truth for what each regulation actually says; project-specific applicability analysis lives separately at `docs/external/regulations/` in each consuming project.

Most entries are **FDA / CDRH device regulations (Title 21)**, but the folder also holds **other federal regulations that reach a device program** — e.g., **HIPAA (Title 45, HHS / OCR)** binds a manufacturer that handles ePHI as a business associate. All are retrieved verbatim from the eCFR public API; only the Title differs.

Distinct from `../standards/` (consensus standards — ISO/IEC) and `../fda-guidance/` (FDA guidance documents — interpretive, nonbinding). Regulations carry the force of law; standards are voluntary unless invoked; guidance is FDA's interpretive position.

## Distilled Regulations

| Citation | File | Subject |
|----------|------|---------|
| 21 CFR Part 807 | [`21-cfr-part-807.md`](21-cfr-part-807.md) | Establishment Registration and Device Listing — including § 807.81 (when a 510(k) is required) and § 807.85 (510(k) exemptions) |
| 21 CFR Part 880 | [`21-cfr-part-880.md`](21-cfr-part-880.md) | General Hospital and Personal Use Devices — including § 880.6310 (MDDS, Class I exempt) and § 880.9 (exemption limitations) |
| 21 CFR Part 892 | [`21-cfr-part-892.md`](21-cfr-part-892.md) | Radiology Devices — including § 892.2050 (medical image management & processing — QIH/PACS) and the broader image-system regulatory chain (§§ 892.2010–892.2080) |
| 45 CFR Part 164 | [`45-cfr-part-164.md`](45-cfr-part-164.md) | HIPAA Security & Privacy of health information — anchored on **Subpart C, the Security Rule** (§§ 164.302–164.318 + Appendix A matrix): administrative / physical / technical safeguards for ePHI that flow down to a device manufacturer acting as a business associate. Breach Notification (Subpart D) and Privacy (Subpart E) summarized + pointered. Forward-looking note on the 2025 Security Rule NPRM. |

Each file opens with a citation block + scope paragraph + section index, then walks every cited section with the **verbatim regulatory text** (CFR is in the public domain — verbatim is permitted and preferred) plus distilled notes on practical regulatory implications and cross-references to companion FDA guidance.

## Scope

### In Scope
- Section-by-section verbatim text for every regulation a medtech project commonly cites
- Cross-references to companion FDA guidance documents (`../fda-guidance/`)
- Cross-references to companion consensus standards (`../standards/`)
- 510(k) exemption status with applicable limitations (the § 880.9 / § 892.9 / § 807.85 framework)
- Amendment/reclassification history when load-bearing for the project's regulatory posture (e.g., § 880.6310 reclassification from Class III to Class I in 2011)
- Source XML retrieved from the eCFR API stored under `source/`; markdown conversion under `source-md/` — both excluded from project-console grounding surfaces (path-segment rules) so agents don't pull the full title into context

### Out of Scope (see instead)
- **Project-specific applicability analysis** — `docs/external/regulations/<name>.md` in each consuming project. That's where module applicability, classification-decision rationale, `[VERIFY]` markers, and Q-Sub questions live.
- **Statutory text (FD&C Act sections)** — those are upstream of CFR; not distilled here. Refer to govinfo.gov USC Title 21.
- **QMS-level regulations** (21 CFR Part 820 Quality System Regulation, 21 CFR Part 11 Electronic Records / Electronic Signatures) — those are organizational compliance, not per-device classification. Add as separate distilled files only if a project's QMS leans on them.
- **Federal Register notices** announcing reclassifications, guidance availability, or rulemaking — those are in `../fda-guidance/source/` or referenced inline.
- **Compliance interpretation** — that's FDA guidance territory; see `../fda-guidance/`.

## Conventions

- Files are named `<title>-cfr-part-<NNN>.md` — lowercase, kebab-case (e.g., `21-cfr-part-807.md`).
- H1 is `` `<Title> CFR Part <NNN> — <Full Title>` `` (e.g., `21 CFR Part 807 — Establishment Registration and Device Listing`).
- H2 sections match the regulation's Subpart structure (`## Subpart E — Premarket Notification Procedures`).
- Per-section content uses H3 with the full citation (`### § 807.81 — When a premarket notification submission is required`).
- Verbatim quoted text uses blockquote (`> ...`) with the source URL footnoted to the eCFR API endpoint.
- Distillation notes (project-relevant commentary, cross-references) follow the verbatim block as plain prose — clearly separated.
- Source URL provenance: every regulation file ends with a "Source provenance" section naming the eCFR API endpoint and retrieval date.

## For Claude (when grounded against a consuming project)

When asked about a 21 CFR citation:
1. Look for the regulation text answer **here** (this folder) — the regulatory text itself.
2. Look for the project-applicability answer at **`docs/external/regulations/<name>.md`** — how this program has decided to apply the regulation to its modules.
3. Cite **both** in footnotes — the regulation file for "what the rule says," the applicability file for "what this device program has decided about it."
4. If the project's applicability file is thin or missing, say so explicitly — don't answer from training knowledge without flagging the gap.
5. If a regulation has been amended/reclassified (e.g., § 880.6310 in 2011), note the reclassification date and the prior class in your response. Older citations to the reclassified status are common defect patterns the `citations` audit will catch.

## Changelog

- 2026-06-02: Added `45-cfr-part-164.md` — HIPAA Security & Privacy (Subpart C Security Rule anchored verbatim from eCFR Title 45, §§ 164.302–164.318 + Appendix A; Subparts D/E summarized; 2025 NPRM noted). First non-Title-21 entry — broadened the README framing from "FDA Regulations" to "Federal Regulations" (HIPAA is HHS/OCR, not FDA) and noted that the folder holds any federal reg reaching a device program, not only CDRH device rules. Closes the privacy/data-protection gap (the library previously had zero HIPAA/GDPR references — only incidental PHI/PII mentions in OWASP / IEC 81001-5-1 / AI-DSF). Companion implementation guide added at `../industry-frameworks/nist-sp-800-66.md`.
- 2026-05-29: README authored as part of adding the `regulations/` category to the registry. Three CFR distillations (21 CFR Parts 807, 880, 892) ship together to close the `registry-gap` finding from the first `/reference-audit` batch pilot. Source content fetched from the eCFR public API (`https://www.ecfr.gov/api/versioner/v1/full/<date>/title-21.xml`) — the AI-accessible federal-regulation endpoint.
