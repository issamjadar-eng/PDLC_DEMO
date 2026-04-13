# Predicate Analysis

> _Demo sample data — not for clinical use. Illustrative content for the PDLC_DEMO project (anchor product: PP3500 / PainEase PCA Advanced)._

Predicate device analysis and GlobalLogic's own infusion device portfolio. For the PP3500 DHF, the **direct predicate is DEV-PP3000 (K190567 — PainEase PCA)**. The broader 5-device portfolio (IP5000, PP3000, PP3500, SP6000, SP6500) is retained as portfolio/predicate context.

## Subfolders

- **`portfolio/`** — GlobalLogic's cleared infusion device portfolio (5 devices). PP3500 is the lead product for this DHF; PP3000 is its direct predicate. Also contains the device master catalog.
- **`concepts/`** — Pre-clearance concept evaluations (AI7000 SmartFlow AI, AMB2500, NEO1200). **NOT FDA cleared.** Retained for the demo to show how concept evaluations feed future DHFs; quarantined from the cleared portfolio.

## Current Contents

### `portfolio/` (cleared devices)

| File | Device | 510(k) | Role |
|---|---|---|---|
| `device-master-catalog.md` | — | — | Master catalog of all 5 cleared devices |
| `DEV-IP5000_regulatory_info.md` | FlexFlow Pro (general-purpose IV pump) | K180234 | Portfolio context |
| `DEV-PP3000_regulatory_info.md` | PainEase PCA (PCA pump) | K190567 | **Direct predicate to PP3500** |
| `DEV-PP3500_regulatory_info.md` | PainEase PCA Advanced (PCA pump) | K210345 | **Lead product** |
| `DEV-SP6000_regulatory_info.md` | MicroDose Pro (syringe pump) | K170423 | Portfolio context |
| `DEV-SP6500_regulatory_info.md` | MicroDose Elite (syringe pump) | K220678 | Portfolio context |

### `concepts/` (not cleared)

| File | Concept | Status |
|---|---|---|
| `CONCEPT-AI7000_evaluation.md` | SmartFlow AI | Concept / internal evaluation only |
| `CONCEPT-AMB2500_evaluation.md` | Ambulatory 2500 | Concept / internal evaluation only |
| `CONCEPT-NEO1200_evaluation.md` | Neonatal 1200 | Concept / internal evaluation only |

## Conventions

- **Naming**: `DEV-<id>_regulatory_info.md` for cleared devices; `CONCEPT-<id>_evaluation.md` for concepts (preserved from source corpus)
- Each file carries the demo banner
- `[Your Company Name]` placeholders have been swept to **GlobalLogic**
- Concept files carry the source's "NOT FDA CLEARED" warning prominently — do not remove

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| 2026-04-12 | Ben Xavier | Phase 3 import — 9 device files (5 cleared + 3 concepts + master catalog) added under `portfolio/` and `concepts/`. PP3500 confirmed as lead product and PP3000 confirmed as direct predicate. GlobalLogic company name applied. |
| YYYY-MM-DD | XX | Initial version — created by /medtech-docs init |
