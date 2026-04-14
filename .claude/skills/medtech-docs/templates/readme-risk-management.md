# Risk Management

ISO 14971 risk management for this DHF — risk management plan, hazard analysis, FMEA, and risk-benefit analysis. A **sibling** of `design-controls/`, not a child, because risk management is device-level and extends beyond the design-controls process (it covers production, postmarket, and end-of-life considerations too).

## Structure

```
risk-management/
├── README.md (this file)
├── risk-management-plan.md     ← the governing plan for this DHF's risk work
├── hazard-analysis.md          ← hazard identification and risk estimation
├── fmea.md                     ← failure modes and effects analysis
├── risk-benefit.md             ← summary risk-benefit determination
└── formal/
    └── *.docx                  ← controlled deliverables for DHF/filing
```

Working markdown files live at the folder root. Controlled deliverables (DOCX for signature, XLSX for risk registers) go in `formal/`. Each working markdown file should correspond to a formal deliverable; when the formal version is generated, note the pairing in the markdown changelog.

The upstream **risk strategy brief** (approach to ISO 14971, platform-level hazard chains, cross-component risk controls) lives at `docs/project/strategies/risk-strategy.md` — shared across the whole project, with per-component callouts. The files in this folder are the formal outputs that the strategy informs.

## Relationship to other folders

```
design-controls/user-needs/        →  risk-management/hazard-analysis/   (user needs frame the use environment and expected users)
design-controls/architecture/      →  risk-management/fmea/              (architecture defines failure modes to analyze)
clinical/benefit-risk/             →  risk-management/risk-benefit/      (clinical benefit evidence feeds the risk-benefit determination)
risk-management/hazard-analysis/   →  design-controls/requirements/      (risk controls become requirements)
risk-management/                   →  cybersecurity/                     (cybersecurity risks are a subset of overall risk; IEC 81001-5-1 assessment cross-links here)
postmarket/capa/                   →  risk-management/hazard-analysis/   (postmarket findings update the hazard analysis)
```

## Conventions

- **One ISO 14971 risk file** — `hazard-analysis.md` is the single source of truth for identified hazards. FMEA files may be structured per module but should roll up into the hazard analysis
- **Risk controls as requirements** — every accepted risk control must trace to a design input requirement in `design-controls/requirements/` and a verification in `design-controls/vnv/`
- **ALARP / risk acceptability** — document the criteria used (ISO 14971 §4.2) explicitly in `risk-management-plan.md`
- **Changes trigger re-review** — any design or postmarket change that affects a hazard must bump the hazard analysis changelog with a new entry, and the risk-benefit must be revisited

## For Claude

- Risk management content is safety-critical. Do not fabricate hazard severity or probability values — use `[VERIFY]` and mark as needing clinical/SME review
- When a new feature or design change is proposed, ask whether the hazard analysis needs updating before approving the design-controls change
- Cross-reference ISO 14971 clauses explicitly (e.g., "per ISO 14971 §5.4, residual risk is evaluated against acceptability criteria defined in §4.2")
- Flag any risk control that is not traceable to a verified requirement — this is a common DHF gap

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| YYYY-MM-DD | XX | Initial version — created by /medtech-docs init or add-dhf |
