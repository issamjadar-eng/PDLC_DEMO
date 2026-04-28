# Standards — Reference Distillations

Clause-level distillations of IEC and ISO consensus standards that govern medical-device software development and safety. Used as the **reference layer** — projects consume these as ground truth for what each standard actually says; project-specific applicability analysis lives separately at `docs/external/standards/` in each consuming project.

## Distilled Standards

| Standard | File | Subject |
|----------|------|---------|
| IEC 62304 (+ Amd 1:2015) | [`iec-62304.md`](iec-62304.md) | Medical device software — Software life cycle processes |
| IEC 82304-1 | [`iec-82304-1.md`](iec-82304-1.md) | Health software — General requirements for product safety |
| ISO 14971 | [`iso-14971.md`](iso-14971.md) | Medical devices — Application of risk management |
| IEC 62366-1 | [`iec-62366-1.md`](iec-62366-1.md) | Medical devices — Usability engineering |
| IEC 81001-5-1 | [`iec-81001-5-1.md`](iec-81001-5-1.md) | Health software & IT security — Security activities in the software lifecycle |

Each file opens with a scope paragraph + TOC, then walks every normative clause with a short "what it requires" paragraph and (where applicable) a mapping to typical downstream deliverables.

## Scope

### In Scope
- Clause numbers, titles, and distilled requirement text for each normative section
- Cross-standard mappings (e.g. IEC 62304 §7 risk management → ISO 14971)
- Where the standard permits tailoring (software safety class, documentation scaling, etc.)
- Amendment coverage notes (Amd 1:2015 for IEC 62304, etc.)

### Out of Scope (see instead)
- **Applicability to a specific device** — see `docs/external/standards/<name>.md` in each consuming project. That's where module applicability, deferred-to-QMS marks, and `[VERIFY]` items live.
- **Per-clause traceability to requirements** — see `docs/project/dhfs/<dhf>/design-controls/trace-matrix/` in the project.
- **Structured regulatory obligations catalog** (what deliverables each clause demands) — see `.claude/skills/dhf-manifest/data/tier1-regulatory/`. That's a sibling view structured for `/dhf-manifest` projection into per-DHF deliverable checklists.
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

## Changelog

- 2026-04-23: README authored as part of project-console v1.7.4 rollout (skill-library exposed to assistant drawer grounding via `grounding.extra_roots`).
