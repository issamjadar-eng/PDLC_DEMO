# Predicate Analysis — Concept Devices

> _Demo sample data — not for clinical use._

Forward-looking concept-device evaluations. Each file captures a hypothesis for a future device family member, the predicate strategy that would apply if it were developed, and the decision whether to pursue it.

These records are **not cleared devices** — they exist to stress-test the regulatory strategy and capture ideas surfaced during predicate review.

## Expected Content

- Per-concept evaluations (`CONCEPT-<CODE>_evaluation.md`) — intended use, closest predicate, regulatory pathway hypothesis, technical / clinical feasibility, decision (pursue / park / reject)
- Supporting analysis linking each concept back to the portfolio roadmap

## Conventions

- **Naming**: `CONCEPT-<CODE>_evaluation.md` (uppercase `CONCEPT` prefix, kebab-case code).
- Every concept file carries a `status` frontmatter field (`pursue`, `park`, `reject`) and a `decision_date`.
- Do not confuse concept devices with portfolio devices — concept codes are never reused for cleared devices. If a concept graduates to a real device, it gets a new `DEV-<CODE>` identity under `../portfolio/` and the concept file is archived with a pointer to its successor.
- Decisions that drive regulatory or commercial strategy should also land as `<!-- STRATEGY CONTENT -->` blocks in the originating task doc.

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| 2026-04-20 | Ben Xavier | Initial version — created under task 018 to satisfy medtech-docs v17 README-every-docs-folder check. |
