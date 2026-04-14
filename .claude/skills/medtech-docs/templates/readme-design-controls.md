# Design Controls

Design History File core for this DHF — the formal design control documents per ISO 13485 and 21 CFR 820.30. This is the regulated document set that traces from user needs through verification and validation for **this component**. Risk management lives as a sibling of this folder at the DHF root (`../risk-management/`), not as a child here — risk management is device-level and extends beyond the design-controls process.

## Subfolders

| Folder | Purpose |
|--------|---------|
| `trace-matrix/` | Traceability matrices — the cross-referencing hub linking user needs, requirements, architecture, V&V, and risk controls |
| `plans/` | Formal design and development plans for this DHF (SDP, Config Mgmt Plan, V&V Plan, 510(k) submission, PCCP protocol). Upstream strategy **briefs** live in `docs/project/strategies/` — shared across the whole project. |
| `user-needs/` | User and stakeholder needs — formal design inputs derived from shared `input-analysis/` |
| `requirements/` | Design input requirements, software requirements (SRS), label requirements |
| `architecture/` | Software architecture documents (SAD), system design, interface specifications |
| `vnv/` | Verification and validation protocols, results, and traceability matrices |
| `tool-validation/` | Validation records for software tools used in development per IEC 62304 |

## Design Control Waterfall

```
user-needs/       → What users and stakeholders need (informed by ../../../input-analysis/)
requirements/     → Formal requirements derived from user needs (risk controls from ../risk-management/ flow in as requirements)
architecture/     → Design that satisfies requirements
vnv/              → Evidence that design meets requirements and user needs
plans/            → How we execute and govern the above
tool-validation/  → Validation evidence for the tools used to produce the above
trace-matrix/     → Cross-references linking all of the above together, and out to ../risk-management/
```

Risk analysis itself (hazards, FMEA, risk-benefit) lives in `../risk-management/` — this DHF's risk management folder at the DHF root, not inside design-controls/.

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
