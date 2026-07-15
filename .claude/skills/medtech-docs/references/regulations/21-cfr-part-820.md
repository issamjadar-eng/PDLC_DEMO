# 21 CFR Part 820 — Quality Management System Regulation (QMSR)

**Citation**: 21 CFR Part 820 (Title 21, Chapter I, Subchapter H)
**Authority**: 21 U.S.C. 351, 352, 360, 360c, 360d, 360e, 360h, 360i, 360j, 360l, 371, 374, 381, 383; 42 U.S.C. 216, 262, 263a, 264
**Promulgating Agency**: FDA / CDRH
**Status**: Active — the **QMSR** (Quality Management System Regulation), which replaced the former Quality System Regulation (QSR). Source: 89 FR 7523, Feb. 2, 2024 (final rule publication); the QMSR framework is the current text of Part 820 as of the retrieval date. `[VERIFY the QMSR compliance/effective date (widely stated as February 2, 2026) against the final rule's DATES section before citing it in a filed document — the eCFR snapshot carries the source citation, not the effective-date narrative]`
**Source**: eCFR versioner API — `https://www.ecfr.gov/api/versioner/v1/full/2026-07-13/title-21.xml?chapter=I&subchapter=H&part=820`
**Faithful text**: [`source-md/21-cfr-part-820.md`](source-md/21-cfr-part-820.md) (deterministic transcription of [`source/21-cfr-part-820.xml`](source/21-cfr-part-820.xml)) — ground exact wording there, not here.

## Scope

Part 820 sets the **current good manufacturing practice (CGMP)** requirements for finished-device manufacturers as a **quality management system regulation**. The load-bearing structural fact about the modern Part 820: it is short, and it works by **incorporating ISO 13485:2016 by reference** (§ 820.7) rather than by enumerating its own quality-system requirements. Most of the former QSR's section inventory is **gone** — the part now consists of Subpart A (General Provisions) and Subpart B (Supplemental Provisions), with §§ 820.20–820.30, § 820.40, and Subparts C–O **[Reserved]**.

**The single most important citation-hygiene consequence:** legacy QSR section numbers — § 820.30 design controls, § 820.75 process validation, § 820.100 CAPA, § 820.181 DMR, § 820.198 complaint files, and the rest — **no longer exist in the current CFR text**. A document citing them cites a repealed structure. The substantive obligations live on through the incorporated ISO 13485 clauses; cite the ISO 13485 clause **via § 820.7/§ 820.10**, or cite the legacy section explicitly as historical (e.g., "former § 820.75 (pre-QMSR)").

## Section inventory (current)

| Section | Title | What it does |
|---------|-------|--------------|
| § 820.1 | Scope | Applicability (finished devices; components excluded; HCT/Ps regulated as devices included), conflicts rule (FD&C Act controls over ISO 13485 on conflict), foreign manufacturers, exemptions/variances |
| § 820.3 | Definitions | ISO 13485 + ISO 9000 Clause 3 definitions apply; adds/supersedes specific terms (batch/lot, component, finished device, remanufacturer, manufacturer, organization…); FD&C Act §201 definitions supersede correlating ISO terms |
| § 820.5 | [Reserved] | — |
| § 820.7 | Incorporation by reference | IBRs **ISO 9000:2015 Clause 3** (for § 820.3) and **ISO 13485:2016** (for §§ 820.1, 820.3, 820.10, 820.35, 820.45) |
| § 820.10 | Requirements for a QMS | The operative requirement: document a QMS complying with ISO 13485 (a); regulatory add-ons mapping ISO clauses to CFR parts (b): 7.5.8 UDI→Part 830, 7.5.9.1 traceability→Part 821, 8.2.3 reporting→Part 803, advisory notices→Part 806; design-and-development applicability (c): Class II/III + listed Class I devices must comply with ISO 13485 **Clause 7.3**; life-supporting/sustaining traceability (d): Clause 7.5.9.2; enforcement (e): noncompliance = adulteration under FD&C §501(h) |
| §§ 820.20–820.30 | [Reserved] | (former management responsibility / design controls sections — repealed by QMSR) |
| § 820.35 | Control of records | Supplements ISO 13485 4.2.5: complaint-record content (a)(1)–(7), servicing-record content (b)(1)–(6), UDI recording (c), confidentiality marking (d) |
| § 820.40 | [Reserved] | — |
| § 820.45 | Device labeling and packaging controls | Supplements ISO 13485 7.5.1: labeling/packaging integrity procedures and pre-release accuracy examination (UDI/UPC, expiration date, …) |
| Subparts C–O | [Reserved] | The former QSR body (process validation, CAPA, DHF/DMR/DHR, etc.) — repealed; obligations continue via the incorporated ISO 13485 clauses |

## Legacy-citation crosswalk (most-cited former QSR sections)

Practical mapping for citation repair — the ISO 13485:2016 clause that now carries each former QSR obligation. `[VERIFY each mapping against ISO 13485:2016 (copyrighted; no source copy in this repository) before relying on it in a filed document — the CFR text itself does not publish this crosswalk; FDA's QMSR final-rule preamble discusses the correspondence]`

| Former QSR section (repealed) | Obligation | Now carried by |
|---|---|---|
| § 820.30 | Design controls | ISO 13485 **Clause 7.3** (explicitly invoked by § 820.10(c)) |
| § 820.75 | Process validation | ISO 13485 **Clause 7.5.6** `[VERIFY]` — via § 820.10(a) |
| § 820.100 | CAPA | ISO 13485 **Clause 8.5.2/8.5.3** `[VERIFY]` |
| § 820.181 / .184 / .186 | DMR / DHR / QSR records | ISO 13485 **Clause 4.2** documentation requirements `[VERIFY]` (+ § 820.35 supplements) |
| § 820.198 | Complaint files | ISO 13485 **Clause 8.2.2** + § 820.35(a) record content |

## Practical implications for a device program

- **QMS documents citing "21 CFR 820.x" legacy numbers need a citation-repair pass.** In this registry's consuming projects, the reference-audit `citations` engine treats a repealed-section citation as stale; restate against ISO 13485 clause + § 820.7/§ 820.10, or mark explicitly historical.
- **Design controls survive with CFR force** for Class II/III (and listed Class I) via § 820.10(c) → ISO 13485 Clause 7.3 — the DHF concept continues even though the § 820.30(j) DHF text is gone.
- **§ 820.35 and § 820.45 are the only supplemental content sections** — they add U.S.-specific record content (complaints, servicing, UDI) and labeling-inspection specifics on top of ISO 13485.
- **ISO 13485:2016 becomes load-bearing U.S. law** for manufacturers in scope — but the standard itself remains copyrighted; this registry carries no ISO 13485 source text. `[VERIFY clause-level ISO 13485 statements against a licensed copy]`

## Cross-references

- Companion standards: ISO 13485:2016 (incorporated by reference — no distillation in this registry yet), ISO 9000:2015 Clause 3
- Companion regulations: Part 830 (UDI), Part 821 (tracing), Part 803 (MDR), Part 806 (corrections/removals), Part 4 (combination products — cGMP interplay `[VERIFY]`)
- Companion guidance: FDA QMSR transition communications (`../fda-guidance/` — not yet imported)

## Source provenance

- Retrieved 2026-07-14 from the eCFR versioner API (point-in-time 2026-07-13).
- Corroborated against a user-supplied eCFR "enhanced display" PDF, "up to date as of 7/13/2026" (md5 `7cc25deb464dbc84f13c9fa1d6bb4a10`) — TOC and §§ 820.1/820.3/820.7 text match the XML transcription.
- CFR text is public domain; the faithful tier at `source/` + `source-md/` is the authoritative in-repo grounding for exact wording.
