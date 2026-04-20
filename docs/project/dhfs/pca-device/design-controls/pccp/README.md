# Predetermined Change Control Plan — pca-device

> _Demo sample data — not for clinical use._

Predetermined Change Control Plan (PCCP) for the PainEase PCA Advanced (PP3500). Defines the envelope of post-market changes (drug library updates, firmware updates, targeted algorithm refinements) the manufacturer may implement without a new 510(k) submission, and the protocol for validating each change.

## Expected Content

- `pccp-protocol.md` — change envelope scope, modification types, pre-specification
- `change-impact-matrix.md` — per-change-type impact on safety, effectiveness, intended use
- `pccp-validation-plan.md` — test protocols exercised before each deployed change
- `pccp-traceability.md` — which Critical-Requirement tags (CtS / CtF / CtC / CtP) are in PCCP scope vs. out
- `formal/` — controlled deliverables for submission

## Conventions

- **Naming**: kebab-case filenames. Every change-type carries a `class` label (drug-library, firmware, algorithm, data-set-refresh, etc.).
- PCCP must not alter intended use, indications for use, device classification, or the safety class of any in-scope software module. Changes that would cross those boundaries fall outside the envelope and require a new submission.
- Every change execution is logged post-hoc in `postmarket/` with the PCCP protocol step that authorized it.
- Linked to: FDA PCCP AI/ML guidance, FDA PCCP General guidance, IEC 62304 (software class boundaries), ISO 14971 (residual risk acceptability).

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| 2026-04-20 | Ben Xavier | Stub folder — created under task 018 so the 510(k) composition manifest's PCCP piece resolves. Awaiting content. |
