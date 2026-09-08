# finance-readme-references-audit

References audit for [`docs/project/finance/README.md`](../../../../docs/project/finance/README.md) — verifies that every citation, relative pointer, engine-action reference and standards mention in the source resolves and supports its claim. Produced by `/reference-audit` (task-batched final-stage audit of the newly authored Finance business-domain README).

## Expected Content

| File | Purpose |
|------|---------|
| `finance-readme-references-audit.md` | The audit report — extracted references, findings by verdict band, summary counts |

## Conventions

- Written only by `/reference-audit init` / `fan-out`; assertional workspace — never modifies the source doc.
- Verdict bands: `sound | unverified | broken`; external-formal refs verified two-tier (L1a registry distillation + L1b project applicability).
- Doc-slug is parent-folder-qualified (`finance-readme`) because the source basename is `README.md`, which would collide with the sibling README audits under the plain basename rule; inferred from SKILL.md `init` step 2, which is silent on basename collisions.

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| 2026-09-08 | AI assistant (reference-audit skill) | Scaffolded audit + extracted references (task 118). |
