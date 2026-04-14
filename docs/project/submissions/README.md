# Submissions

Packages assembled for regulatory submission. These reference and incorporate content from design controls and input analysis but are organized by submission type.

## Subfolders

| Folder | Purpose |
|--------|---------|
| `qsub/` | Q-Sub (Pre-Submission) package — cover letter, device description, proposed intended use, predicate comparison, PCCP summary, FDA questions. Includes `correspondence/` for FDA interactions. |
| `510k/` | 510(k) submission materials — full predicate comparison, software documentation, performance data, risk analysis, labeling. Includes `correspondence/` for FDA interactions. |
| `pccp/` | Predetermined Change Control Plan — change types, modification protocols, performance criteria, validation methodology. Includes `correspondence/` for PCCP-specific FDA interactions. |

## Relationship to Design Controls

Submissions are assembled from per-DHF design controls (`docs/project/dhfs/<dhf>/`), not authored independently:
- Q-Sub references the device description, intended use, and PCCP summary from the relevant DHF
- 510(k) packages the full design control output of one or more DHFs (requirements, architecture, risk, V&V) — the composition manifest in each DHF lists which artifacts roll up here
- PCCP defines the change control framework for the device(s) described in their DHFs
- Cross-component strategic framing (filing pathway, predicate lineage, PCCP scope) is sourced from `docs/project/strategies/regulatory-strategy.md`

## Conventions

- Documents follow the versioning convention in `docs/project/README.md`
- **Naming**: `component-name.md` (kebab-case)
- Submission documents use formal, regulatory-appropriate language

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| YYYY-MM-DD | XX | Initial version — created by /medtech-docs init |
| 2026-04-13 | BX | task 009: pointed at per-DHF source under `dhfs/<dhf>/` and shared `strategies/regulatory-strategy.md` for upstream framing. |
