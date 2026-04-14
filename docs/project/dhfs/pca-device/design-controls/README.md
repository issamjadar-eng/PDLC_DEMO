# Design Controls

Design History File core — the formal design control documents per ISO 13485 and 21 CFR 820.30. This is the regulated document set that traces from user needs through verification and validation.

## Subfolders

| Folder | Purpose |
|--------|---------|
| `trace-matrix/` | Traceability matrices — the cross-referencing hub linking user needs, requirements, architecture, V&V, and risk |
| `plans/` | Design and development plans, V&V plans, project strategy documents |
| `user-needs/` | User and stakeholder needs — formal design inputs derived from input-analysis |
| `requirements/` | Design input requirements, software requirements (SRS), label requirements |
| `architecture/` | Software architecture documents (SAD), system design |
| `risk-management/` | Risk analysis per ISO 14971, hazard analysis, FMEA |
| `vnv/` | Verification and validation protocols, results, and traceability matrices |

## Design Control Waterfall

```
user-needs/       → What users and stakeholders need (informed by input-analysis/)
requirements/     → Formal requirements derived from user needs
architecture/     → Design that satisfies requirements
risk-management/  → Hazards and mitigations across all phases
vnv/              → Evidence that design meets requirements and user needs
plans/            → How we execute and govern the above
trace-matrix/     → Cross-references linking all of the above together
```

## Document Workflow

Each subfolder follows a **markdown-first authoring** pattern:

```
subfolder/
├── formal/              ← Controlled documents (DOCX, XLSX) — the DHF record
│   └── document.docx
└── document.md          ← Working markdown — where we draft and iterate
```

- **Working markdown** (root): where we author and iterate with AI assistance — diffable, reviewable
- **Formal documents** (`formal/`): controlled deliverables for the DHF — generated from markdown when ready for review/signature
- SOPs and templates governing document creation live in `docs/internal/`

## Conventions

- Cross-reference traceability: requirements trace to user needs, architecture traces to requirements, V&V traces to both
- One document per file — each deliverable section gets its own markdown file
- **Naming**: `component-name.md` (kebab-case) at root; matching `component-name.docx` in `formal/`

## For Claude

- When drafting design control documents, check `docs/external/standards/` to ensure referenced standards are addressed
- Flag any design control gap that may impact the PCCP change categories or submission readiness
- Cross-reference traceability: requirements trace to user needs, architecture traces to requirements, V&V traces to both

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| YYYY-MM-DD | XX | Initial version — created by /medtech-docs init |
