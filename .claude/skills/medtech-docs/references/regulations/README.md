# Federal Regulations — Reference Distillations

Section-level distillations of federal regulations that bind medical-device manufacturers. Used as the **reference layer** — projects consume these as ground truth for what each regulation actually says; project-specific applicability analysis lives separately at `docs/external/regulations/` in each consuming project.

Most entries are **FDA / CDRH device regulations (Title 21)**, but the folder also holds **other federal regulations that reach a device program** — e.g., **HIPAA (Title 45, HHS / OCR)** binds a manufacturer that handles ePHI as a business associate. All are retrieved verbatim from the eCFR public API; only the Title differs.

Distinct from `../standards/` (consensus standards — ISO/IEC) and `../fda-guidance/` (FDA guidance documents — interpretive, nonbinding). Regulations carry the force of law; standards are voluntary unless invoked; guidance is FDA's interpretive position.

## Distilled Regulations

| Citation | File | Subject |
|----------|------|---------|
| 21 CFR Part 807 | [`21-cfr-part-807.md`](21-cfr-part-807.md) | Establishment Registration and Device Listing — including § 807.81 (when a 510(k) is required), § 807.85 (exemption for custom devices + distributors/repackagers), and the § 807.87 (a)–(m) required-content lettering |
| 21 CFR Part 814 | [`21-cfr-part-814.md`](21-cfr-part-814.md) | Premarket Approval (PMA) of Medical Devices — including § 814.20(b)(1)–(13) PMA content/format (the PMA submission backbone), § 814.39 PMA supplements, § 814.44 FDA action + the SSED, Subpart E postapproval, and Subpart H (HDE) |
| 21 CFR Part 880 | [`21-cfr-part-880.md`](21-cfr-part-880.md) | General Hospital and Personal Use Devices — including § 880.6310 (MDDS — hardware-only since 86 FR 20283 (2021); Class I exempt) and § 880.9 (exemption limitations) |
| 21 CFR Part 892 | [`21-cfr-part-892.md`](21-cfr-part-892.md) | Radiology Devices — including § 892.2050 (medical image management & processing — QIH/PACS) and the broader image-system regulatory chain (§§ 892.2010–892.2080) |
| 21 CFR Part 820 | [`21-cfr-part-820.md`](21-cfr-part-820.md) | Quality Management System Regulation (**QMSR**) — the post-2024 Part 820 that incorporates ISO 13485:2016 by reference (§ 820.7/§ 820.10) and reserves the former QSR body; includes the legacy-citation crosswalk (former §§ 820.30/.75/.100/.181/.198 → ISO 13485 clauses) that citation-repair passes need |
| 45 CFR Part 164 | [`45-cfr-part-164.md`](45-cfr-part-164.md) | HIPAA Security & Privacy of health information — anchored on **Subpart C, the Security Rule** (§§ 164.302–164.318 + Appendix A matrix): administrative / physical / technical safeguards for ePHI that flow down to a device manufacturer acting as a business associate. Breach Notification (Subpart D) and Privacy (Subpart E) summarized + pointered. Forward-looking note on the 2025 Security Rule NPRM. |

Each file opens with a citation block + scope paragraph + section index, then walks every cited section with the **verbatim regulatory text** (CFR is in the public domain — verbatim is permitted and preferred) plus distilled notes on practical regulatory implications and cross-references to companion FDA guidance.

## Scope

### In Scope
- Section-by-section verbatim text for every regulation a medtech project commonly cites
- Cross-references to companion FDA guidance documents (`../fda-guidance/`)
- Cross-references to companion consensus standards (`../standards/`)
- 510(k) exemption status with applicable limitations (the § 880.9 / § 892.9 / § 807.85 framework)
- Amendment/reclassification history when load-bearing for the project's regulatory posture (e.g., § 880.6310 reclassification from Class III to Class I in 2011)
- Retrieval provenance: every file's "Source provenance" section names the eCFR API endpoint and retrieval date.
- **Faithful full text** — `source/<base>.xml` (the byte-correct eCFR versioner XML) + `source-md/<base>.md` (a deterministic, no-LLM transcription of that XML; public-domain verbatim text). These are the **authoritative in-repo grounding + citation tier** for the regulation; the distilled file at the parent level is a finding aid that points here. `source-md/` is indexed by semantic search; `source/` XML is not (raw archive). Mirrors the `../fda-guidance/` two-tier shape.

### Out of Scope (see instead)
- **Project-specific applicability analysis** — `docs/external/regulations/<name>.md` in each consuming project. That's where module applicability, classification-decision rationale, `[VERIFY]` markers, and Q-Sub questions live.
- **Statutory text (FD&C Act sections)** — those are upstream of CFR; not distilled here. Refer to govinfo.gov USC Title 21.
- **QMS-level regulations** — 21 CFR Part 11 (Electronic Records / Electronic Signatures) remains out of scope. Part 820 (QMSR) **is now distilled** (a consuming project's risk file leaned on former § 820.75, exposing the QSR→QMSR citation-staleness class of defect).
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
5. If a regulation has been amended/reclassified (e.g., § 880.6310 — reclassified 2011, software removed 2021), note the amendment date and the prior state in your response. Older citations to a superseded status are common defect patterns the `citations` audit will catch.
6. **For exact regulatory wording, ground and cite `source-md/<base>.md`** — the faithful in-repo transcription of the eCFR XML — not the distilled parent file (a finding aid that paraphrases and omits). The distilled file routes you here.
7. **Escalate to the live eCFR when *currency* matters.** Regulations change; each `source-md/` snapshot is dated (see its header). If the retrieval date is more than ~6 months old, the question touches a pending rulemaking, or a submission turns on the current text, fetch the live eCFR versioner API: `https://www.ecfr.gov/api/versioner/v1/full/<YYYY-MM-DD>/title-<N>.xml?part=<NNN>` (the human-viewer `ecfr.gov/current/...` URLs redirect automated fetchers — use the API). Quote what the API returns, and flag the snapshot for re-pull if it has drifted.

## Changelog

- 2026-07-14: Added `21-cfr-part-820.md` — the **QMSR** (current Part 820), full two-tier (`source/21-cfr-part-820.xml` eCFR versioner XML @ point-in-time 2026-07-13 + deterministic `source-md/` transcription + distilled finding aid). Key content: § 820.7 ISO 13485:2016/ISO 9000:2015 incorporation by reference, § 820.10 QMS requirement + clause-to-CFR-part add-ons, § 820.35/§ 820.45 supplemental record/labeling provisions, and a legacy-citation crosswalk (former QSR §§ 820.30/.75/.100/.181/.198 no longer exist — repealed by the QMSR; obligations carried by ISO 13485 clauses). Driven by a reference audit that caught a live former-§ 820.75 citation.
- 2026-06-15: Added `21-cfr-part-814.md` — Premarket Approval (PMA); § 814.20 content/format verified verbatim against the eCFR API. Also re-applied (after merging the upstream source-md refresh) the **§ 807.87 (a)–(m) subsection lettering** into `21-cfr-part-807.md` + a citation-discipline note ((k) = Class III cert, (l) = truthful-&-accuracy) — closes the unlettered-bullets ambiguity that let a 807.87(k)↔(l) miscitation slip into a submission template. (PMA distillation predates the `source/`+`source-md/` faithful-tier convention; a verbatim 814 source archive is a follow-up.)
- 2026-06-15: Added the **faithful full-text tier** — `source/<base>.xml` (eCFR versioner XML) + `source-md/<base>.md` (deterministic no-LLM transcription) for all four parts (807/880/892 @ Title-21 issue 2026-06-11; 164 @ Title-45 issue 2026-06-09). Bidirectional fidelity verified (0 invented / 0 dropped-clause runs). Regulations now match `../fda-guidance/`'s two-tier shape: `source-md/` is the authoritative grounding + citation source, the distilled file is a finding aid that points to it. Updated In-Scope + "For Claude" escalation order accordingly. CFR text is public domain — verbatim archiving permitted and preferred.
- 2026-06-02: Added `45-cfr-part-164.md` — HIPAA Security & Privacy (Subpart C Security Rule anchored verbatim from eCFR Title 45, §§ 164.302–164.318 + Appendix A; Subparts D/E summarized; 2025 NPRM noted). First non-Title-21 entry — broadened the README framing from "FDA Regulations" to "Federal Regulations" (HIPAA is HHS/OCR, not FDA) and noted that the folder holds any federal reg reaching a device program, not only CDRH device rules. Closes the privacy/data-protection gap (the library previously had zero HIPAA/GDPR references — only incidental PHI/PII mentions in OWASP / IEC 81001-5-1 / AI-DSF). Companion implementation guide added at `../industry-frameworks/nist-sp-800-66.md`.
- 2026-05-29: README authored as part of adding the `regulations/` category to the registry. Three CFR distillations (21 CFR Parts 807, 880, 892) ship together to close the `registry-gap` finding from the first `/reference-audit` batch pilot. Source content fetched from the eCFR public API (`https://www.ecfr.gov/api/versioner/v1/full/<date>/title-21.xml`) — the AI-accessible federal-regulation endpoint.
