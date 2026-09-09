# FDA Guidance

Distilled FDA guidance documents that apply to this project. Each file is a copy of the bundled distilled guidance from the `medtech-docs` skill library, imported here so it travels with the project repository and can be edited / annotated in place.

Files are imported via `/medtech-docs update-external-references`. Re-run that action whenever project scope or strategy changes — it adds newly-applicable guidances without overwriting anything you have already edited here.

## Active Guidances

| Topic | File | Title | Original Source (skill library) | Trigger |
|-------|------|-------|---------------------------------|---------|
| qsub | [qsub.md](qsub.md) | Requests for Feedback and Meetings for Medical Device Submissions (Q-Sub) | [PDF](../../../.claude/skills/medtech-docs/references/fda-guidance/source/qsub.pdf) · [MD](../../../.claude/skills/medtech-docs/references/fda-guidance/source-md/qsub.md) | always (active FDA engagement) |
| 510k-se | [510k-se.md](510k-se.md) | The 510(k) Program: Evaluating Substantial Equivalence | [PDF](../../../.claude/skills/medtech-docs/references/fda-guidance/source/510k-se.pdf) · [MD](../../../.claude/skills/medtech-docs/references/fda-guidance/source-md/510k-se.md) | `regulatory_pathway == 510k` |
| sw-functions | [sw-functions.md](sw-functions.md) | Policy for Device Software Functions and Mobile Medical Applications | [PDF](../../../.claude/skills/medtech-docs/references/fda-guidance/source/sw-functions.pdf) · [MD](../../../.claude/skills/medtech-docs/references/fda-guidance/source-md/sw-functions.md) | composition includes `samd` and `simd` |
| sw-changes | [sw-changes.md](sw-changes.md) | Deciding When to Submit a 510(k) for a Software Change to an Existing Device | [PDF](../../../.claude/skills/medtech-docs/references/fda-guidance/source/sw-changes.pdf) · [MD](../../../.claude/skills/medtech-docs/references/fda-guidance/source-md/sw-changes.md) | 510(k) pathway + predicate PP3000 (K190567) |
| cybersecurity | [cybersecurity.md](cybersecurity.md) | Cybersecurity in Medical Devices: Quality System Considerations and Content of Premarket Submissions | [PDF](../../../.claude/skills/medtech-docs/references/fda-guidance/source/cybersecurity.pdf) · [MD](../../../.claude/skills/medtech-docs/references/fda-guidance/source-md/cybersecurity.md) | software + connected device (cloud-suite, connectivity-adapter) |
| mfd | [mfd.md](mfd.md) | Multiple Function Device Products: Policy and Considerations | [PDF](../../../.claude/skills/medtech-docs/references/fda-guidance/source/mfd.pdf) · [MD](../../../.claude/skills/medtech-docs/references/fda-guidance/source-md/mfd.md) | cloud-suite hosts 7 functions, mix of device + non-device (analytics, inventory, fleet) |
| accessories | [accessories.md](accessories.md) | Medical Device Accessories: Describing Accessories and Classification Pathways | [PDF](../../../.claude/skills/medtech-docs/references/fda-guidance/source/accessories.pdf) · [MD](../../../.claude/skills/medtech-docs/references/fda-guidance/source-md/accessories.md) | multi-function PCA system; connectivity-adapter + cloud-suite modules and hardware accessories support/supplement/augment the parent PP3500 pump — accessory classification (own-risk per FDARA 2017) in scope |
| cds | [cds.md](cds.md) | Clinical Decision Support Software | [PDF](../../../.claude/skills/medtech-docs/references/fda-guidance/source/cds.pdf) · [MD](../../../.claude/skills/medtech-docs/references/fda-guidance/source-md/cds.md) | predictive-alarm SaMDs in PCCP envelope (regulatory-strategy.md §1, §2) |
| pccp-general | [pccp-general.md](pccp-general.md) | Marketing Submission Recommendations for a Predetermined Change Control Plan | [PDF](../../../.claude/skills/medtech-docs/references/fda-guidance/source/pccp-general.pdf) · [MD](../../../.claude/skills/medtech-docs/references/fda-guidance/source-md/pccp-general.md) | PCCP filed with PP3500 510(k) (regulatory-strategy.md) |
| pccp-aiml | [pccp-aiml.md](pccp-aiml.md) | PCCP for AI/ML-Enabled Device Software Functions | [PDF](../../../.claude/skills/medtech-docs/references/fda-guidance/source/pccp-aiml.pdf) · [MD](../../../.claude/skills/medtech-docs/references/fda-guidance/source-md/pccp-aiml.md) | PCCP + `capabilities.ai_ml: true` |
| ai-dsf-lifecycle | [ai-dsf-lifecycle.md](ai-dsf-lifecycle.md) | AI-Enabled Device Software Functions: Lifecycle Management and Marketing Submission Recommendations | [PDF](../../../.claude/skills/medtech-docs/references/fda-guidance/source/ai-dsf-lifecycle.pdf) · [MD](../../../.claude/skills/medtech-docs/references/fda-guidance/source-md/ai-dsf-lifecycle.md) | `capabilities.ai_ml: true` |

- **Original Source** column links to the bundled originals in the skill library:
  - PDF: `.claude/skills/medtech-docs/references/fda-guidance/source/<topic>.pdf`
  - Markdown conversion: `.claude/skills/medtech-docs/references/fda-guidance/source-md/<topic>.md`
  - Distilled (the file copied here): `.claude/skills/medtech-docs/references/fda-guidance/<topic>-distilled.md`

## Evaluated — Not Applicable

Guidances evaluated by `update-external-references` and not currently applicable. If a guidance moves from "applicable" to "not applicable" on a re-run, its row is moved here but the file on disk is retained.

| Topic | File | Rationale |
|-------|------|-----------|
| _(none — all 11 applicable bundled FDA guidances apply to PDLC_DEMO at this time)_ | | |

## Conventions

- **One file per guidance**, named by short topic (e.g., `qsub.md`, `pccp-aiml.md`). Filename matches the bundled distilled file with the `-distilled` suffix removed.
- Files are imported verbatim from the skill library by `update-external-references`. Edits made here are never overwritten on re-run — the action only creates files that don't yet exist.
- Use `[VERIFY]` markers for any project-specific assertions added on top of the distilled content.
- Note knowledge cutoff — flag if guidance may have been updated since the bundled version.

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| 2026-06-22 | BX / AI Assistant | Imported `accessories.md` (Medical Device Accessories guidance) via the accessories rubric trigger added to `/medtech-docs update-external-references`; applicability driven by the multi-function PCA system (software modules + hardware accessories used with the parent PP3500 pump). |
| 2026-04-14 | BX | Imported 10 distilled FDA guidances via /medtech-docs update-external-references; rewrote README to v15 model (distilled copies hosted here, originals linked to skill library). See `tasks/ben/012-medtech-docs-update-external-references.md`. |
| 2026-04-12 | BX | Initial version — created by /medtech-docs init |
| 2026-09-08 | BX / AI Assistant | task 123: `qsub.md` heading "Pre-Submission Package Contents" relabeled to the guidance's own section names (III.B(1) Submission Content; III.B(4)(a)(1) Additional Recommended Submission Contents) — the invented label had propagated into project citations (validation protocol TC-PROTO-CITATIONS item 7). |
