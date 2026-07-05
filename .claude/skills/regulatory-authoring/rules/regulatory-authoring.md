# Rule: Controlled regulated documents follow the Regulatory Authoring Standard

Any edit to a **controlled document that faces a regulator (FDA, EU Notified Body) or an auditor** — Design History File deliverables and FDA/EU submission narratives — follows the project's **Regulatory Authoring Standard**, owned by the `regulatory-authoring` skill.

## When this applies

Edit/Write to the **filed body** of a controlled DHF or submission document — content that is transmitted to a regulator or examined by an auditor. Typical homes (project-configured): the controlled DHF mirror tree and the submission package trees. It does **not** apply to working/scratch notes, engineering working source, strategy docs, or READMEs (those have their own conventions).

## The rule

1. **Before editing**, consult the standard. The `regulatory-authoring` SKILL.md carries the one-line rule index (the default load); load `references/authoring-standard.md` **on demand** for the full rule + example of the rule(s) in play, and `references/rule-interactions.md` when two rules touch one span.
2. **For a new or substantively restructured FORM-instance document, do the D1 pre-flight FIRST:** read the governing QMS FORM/SOP/WI (from the taxonomy `governing_qms`), write the FORM-schema map, start from the three-tier skeleton, and quote-verify every QMS citation at the moment of writing it. Structure before content.
3. **While editing**, apply the W/R/D rules for the document's tier and filing route (determine FDA / EU / dual from `project.yml` `dhfs[].filing` or the doc front-matter; absent a signal, treat as FDA-routed and flag it).
4. **After editing**, run the lint (`/regulatory-authoring lint <file>`) over the changed sections. A clean lint is **necessary, not sufficient**.
5. **For a substantive edit** (new content, restructure, new/changed rows or sections — not typo or metadata-only touches), run the full check: the **copy-editor** redline (prose only, never substance) and then the **QA-conformance** pass (`quality-engineering`) against the doctype's governing FORM and the three-tier structure, before the edit is declared done. Apply or explicitly defer each finding (deferrals recorded as managed TBDs / issues with owner + gate). Record the verdict in the document's AI-CHANGELOG row.
6. **For a citation-bearing edit** (adds/changes a standards clause, a guidance example/appendix/§, a K-number/precedent, or a cross-doc reference), ensure the **active task doc carries a final-stage todo to run an independent reference audit** (`/reference-audit`) over the document before the task is declared done — verifying each citation against the **byte-correct source** (rung 3: `source-md/` or the md5-pinned `source/` PDF), never the distilled finding-aid. Batched once per task and run as a subagent (independent of the authoring reasoning), it is the control that catches a cited label that does not exist in the source; the per-edit lint/copy-editor/QA stages do not, because self-review does not re-derive a citation from its source.

Multi-lens review (regulatory, traceability) is added per the content's risk — mandatory for net-new documents and intended-use-adjacent edits; the QA lens alone suffices for routine maintenance.

## Why this exists

Self-review demonstrably misses structural contracts. Reading the rules "for content" is not the same as applying their structural contract (the three-tier 🔒 model, FORM conformance, contiguous numbering, claim↔evidence pairing). The lint catches mechanical defects; the copy-editor improves prose without touching substance; the QA pass verifies conformance the lint cannot. The three stages together are the control.

## Interaction with other rules

- **`doctype-governance.md`** — still applies: read the governing FORM/SOP/WI before editing a `.taxonomy.yml`-governed doctype. This rule layers the authoring standard + the 3-stage workflow on top.
- **`ai-changelog.md`** — the QA verdict and the authoring pass are recorded in the non-published AI-CHANGELOG block; vendor-neutral ("AI assistant(s)").
- **`readme-before-write.md`** — unchanged; read folder + parent READMEs before writing under `docs/`.
