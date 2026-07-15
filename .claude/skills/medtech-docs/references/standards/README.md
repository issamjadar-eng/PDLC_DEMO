# Standards — Reference Distillations

Clause-level distillations of IEC and ISO consensus standards that govern medical-device software development and safety. Used as the **reference layer** — the registry's best-effort distillation of what each standard says; project-specific applicability analysis lives separately at `docs/external/standards/` in each consuming project.

**These files are distillations, not the standards.** No source copies exist in the repository (copyrighted), so distillation accuracy is bounded by what has been verified — per-file provenance/quarantine banners and `[VERIFY]` markers record the current confidence. The original standard is always the sole normative authority; treat a distillation as an index into the standard, never as a substitute for it in submission-grade work.

## Distilled Standards

| Standard | File | Subject |
|----------|------|---------|
| IEC 62304 (+ Amd 1:2015) | [`iec-62304.md`](iec-62304.md) | Medical device software — Software life cycle processes |
| IEC 82304-1 | [`iec-82304-1.md`](iec-82304-1.md) | Health software — General requirements for product safety |
| ISO 14971 | [`iso-14971.md`](iso-14971.md) | Medical devices — Application of risk management |
| IEC 62366-1 | [`iec-62366-1.md`](iec-62366-1.md) | Medical devices — Usability engineering |
| IEC 81001-5-1 | [`iec-81001-5-1.md`](iec-81001-5-1.md) | Health software & IT security — Security activities in the software lifecycle |
| IEC 60601-1 | [`iec-60601-1.md`](iec-60601-1.md) | Medical electrical equipment — basic safety & essential performance (FDA rec 19-49, Ed 3.2 consolidated) |
| IEC 60601-1-2 | [`iec-60601-1-2.md`](iec-60601-1-2.md) | Medical electrical equipment — EMC (FDA rec 19-36, Ed 4.1 only, partial — two carve-outs) |
| IEC 60601-1-8 | [`iec-60601-1-8.md`](iec-60601-1-8.md) | Medical electrical equipment — alarm systems (FDA rec 5-131, Ed 2.2) |
| IEC 60601-2-24 | [`iec-60601-2-24.md`](iec-60601-2-24.md) | Infusion pumps & controllers particular standard (**no current FDA recognition** — verified null; publisher-preview-verified 201.x front matter incl. Table 201.101) |
| ISO 10993 series | [`iso-10993.md`](iso-10993.md) | Biological evaluation series (-1 evaluation, -5 cytotoxicity, -10 sensitization, -23 irritation — the 2021 -10/-23 split is pinned) |
| IEC 60812 | [`iec-60812.md`](iec-60812.md) | FMEA/FMECA method standard, 2018 3rd ed (FDA rec 5-120, complete) |

Each file opens with a header block (edition/amendment, FDA-recognition note, distillation notice or quarantine banner where applicable), then clause-by-clause sections with distilled requirement text and (where applicable) mappings to typical downstream deliverables. Coverage is not guaranteed to be complete — absence of a clause from a file does **not** mean the standard is silent there.

## Scope

### In Scope
- Clause numbers, titles, and distilled requirement text for each normative section
- Cross-standard mappings (e.g. IEC 62304 §7 risk management → ISO 14971)
- Where the standard permits tailoring (software safety class, documentation scaling, etc.)
- Amendment coverage notes (Amd 1:2015 for IEC 62304, etc.)

### Out of Scope (see instead)
- **Applicability to a specific device** — see `docs/external/standards/<name>.md` in each consuming project. That's where module applicability, deferred-to-QMS marks, and `[VERIFY]` items live.
- **Per-clause traceability to requirements** — the consuming project's trace-matrix deliverable (location per the project's `project.yml dhfs[].path` / trace-matrix config).
- **Structured regulatory obligations catalog** (what deliverables each clause demands) — see `.claude/skills/dhf-manifest/data/{fda-guidance,standards,industry-frameworks}/`. That's a sibling view structured for `/dhf-manifest` projection into per-DHF deliverable checklists.
- **Verbatim standard text** — copyrighted; not reproduced. These files are distillations, not transcriptions.
- **QMS-level standards** (ISO 13485, 21 CFR Part 820) — not distilled here; those are organizational compliance, not per-device.

## Conventions

- Files are named `<acronym>-<short-subject>.md` — lowercase, kebab-case
- H1 is "`<ACRONYM> — <Full Title>`"
- H2 sections match the standard's top-level clause numbering (`## 5 Software Development Process`)
- Deeper clauses use H3/H4
- Hyphens between acronym and version when present (e.g., `iec-62366-1.md`, not `iec-623661.md`)

## For Claude (when grounded against a consuming project)

When asked about a named IEC/ISO standard:
1. Look for the clause-text answer here (in this folder)
2. Look for the project-applicability answer at `docs/external/standards/<name>.md`
3. Cite BOTH in footnotes — the reference file for "what the standard says," the applicability file for "what this device program has decided about it"
4. If the project's applicability file is thin or missing, say so explicitly — don't answer from training knowledge without flagging the gap
5. **If the distillation can't answer, say the standard is needed.** Honor quarantine banners and `[VERIFY]` markers; when the distilled file is silent on the cited clause, carries a banner over it, or the question turns on exact normative wording, state that the original standard must be consulted (no source copy exists in the repo) rather than inferring clause content. A clause's absence from the distillation is not evidence the standard is silent.

## Changelog

- 2026-07-15: Added six distillations driven by a consuming project's risk-file reference audit (the L1a layer previously covered only 5 software-adjacent standards, leaving the 60601 family / ISO 10993 / IEC 60812 unverifiable): `iec-60601-1.md`, `iec-60601-1-2.md`, `iec-60601-1-8.md`, `iec-60601-2-24.md`, `iso-10993.md` (series file), `iec-60812.md`. All are 🔎 finding aids grounded ONLY in public sources (FDA Recognized Consensus Standards DB entries with recognition numbers, IEC/ISO webstore abstracts, publisher-authorized preview front matter) with recall-derived content `[VERIFY]`-flagged — no verbatim standard text. Notable public determinations recorded: IEC 60601-2-24 has NO current FDA recognition (verified null); IEC 60601-1-2 recognized only at Ed 4.1 (partial); ISO 10993-10:2021 lost irritation to ISO 10993-23:2021.

- 2026-04-23: README authored as part of project-console v1.7.4 rollout (skill-library exposed to assistant drawer grounding via `grounding.extra_roots`).
