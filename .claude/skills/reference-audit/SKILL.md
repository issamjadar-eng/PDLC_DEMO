---
name: reference-audit
description: Verify references and citations in a project document — broken links, stale standards clauses, mismatched anchors, prose pointers that don't resolve. Builds a structured findings report at `docs/_analysis/<doc-slug>/references-audit.md`. Two-tier verification by default — L1a registry distillation (`.claude/skills/medtech-docs/references/`) + L1b project applicability (`docs/external/`) per the medtech-docs "cite both" mandate. Owns the `citations` advisor and three researcher subagents (external-formal / internal-formal / informal-link). TRIGGER when the user wants to audit, verify, validate, or check the references / citations / sources / links in a specific document (e.g. "audit the references in regulatory-strategy.md", "are the citations in our SRS sound?", "check for broken links in the system SAD", "verify the standards citations in this doc"); also trigger on broken-link / stale-citation troubleshooting and on requests for FDA-reviewer-style citation pen-testing. Project-agnostic.
version: 6
updated: 2026-09-08
---

# Reference Audit

Verify that every citation in a project document actually resolves to a real source and that the source supports the cited claim. The skill scaffolds a structured audit report under `docs/_analysis/<doc-slug>/references-audit.md`, fans out to the `citations` advisor (and its three researcher subagents) to verify each reference, and writes findings back into the report.

Distinct from `/gap-analysis` (which audits content methodology against standards) and `/dhf-manifest` (which audits structural document coverage of regulatory obligations): this skill verifies the **references themselves** — that paths resolve, anchors exist, standards clauses say what they're cited as saying, and external records exist.

## Supporting Files

| File | Purpose |
|------|---------|
| `README.md` | Design document — architecture, lineage, dependencies |
| `agents/citations.md` | Engine advisor — classifies a reference, dispatches to a researcher, returns a finding |
| `agents/citations-external-researcher.md` | Researcher for external-formal references (standards, CFR, FDA guidance, K-numbers); does the two-tier L1a + L1b lookup |
| `agents/citations-internal-researcher.md` | Researcher for internal-formal references (SOPs, DHF artifacts, strategies, `project.yml`, glossary) |
| `agents/citations-informal-researcher.md` | Researcher for informal references (anchors, cross-doc links, prose pointers) |
| `templates/references-audit.md` | Output-document scaffolding template for `docs/_analysis/<doc-slug>/references-audit.md` |

## Subagent Delegation

| Scenario | Agent Type | Prompt |
|----------|-----------|--------|
| Verify a single (claim, reference) pair (point query) | `citations` | Inline — caller passes the reference and gets a finding back |
| Verify all references in a document (batch) | `citations` | The `fan-out` action passes each extracted reference to `citations` and consolidates findings |

The three researcher subagents (`citations-external-researcher`, `citations-internal-researcher`, `citations-informal-researcher`) are invoked by the `citations` advisor itself, not directly by this skill. Other domain advisors (regulatory-affairs, quality-engineering, etc.) may invoke `citations` directly for point-query verification of their own citations.

## Actions

Parse the user's argument string `$ARGUMENTS` to determine which action to perform.

### `setup`

Wire up the skill's bundled agents into `.claude/agents/` so they are discoverable by the Agent tool. Idempotent — safe to re-run.

1. Create `.claude/agents/` directory if it does not exist.
2. For each agent file in `agents/` (the skill's `agents/` folder is the source of truth):
   - Create symlink `.claude/agents/<agent-name>.md` → `../skills/reference-audit/agents/<agent-name>.md`
   - If the symlink already exists and points at the correct target: skip.
   - If the symlink exists but points elsewhere: replace.
   - If a regular file exists at the symlink path (project fork): leave it alone — `/sync-skills` and `/advisors sync` detect forks intentionally.
3. Report what was wired vs already present vs left as a fork.

The four agents installed:
- `citations` — verification engine.
- `citations-external-researcher` — L1a + L1b two-tier resolver.
- `citations-internal-researcher` — path / anchor / file-locator MCP resolver.
- `citations-informal-researcher` — intra-doc / cross-doc / prose-pointer resolver.

No hooks, no rules — this skill ships agents only.

### `init <doc-path>`

Scaffold an audit for the target document. Extracts the document's references and writes a structured report ready for `fan-out` to verify.

1. **Validate** the doc-path exists and lives under `docs/` (no audits of files outside the project's documentation tree).
2. **Compute doc-slug** — kebab-case basename of the source doc without extension (e.g., `regulatory-strategy`, `qsub-composition-manifest`, `system-sad`).
3. **Determine component segment** by reading `docs/_analysis/README.md` (if present) and consulting `project.yml dhfs[]`. The `_analysis/` tree in a medtech project is keyed by component (per `arch_slug` for item DHFs and `leaf` for the system DHF) — same convention `/gap-analysis` uses. Match the source doc to a component:
   - If the source path is under `docs/project/dhfs/<dhf>/` or `docs/project/_confluence/<arch>/`: use that DHF's `arch_slug` (or `leaf` for the system DHF).
   - If the source path is under `docs/project/strategies/`, `docs/project/submissions/`, `docs/project/input-analysis/`, `docs/external/`, or `docs/internal/`: these are cross-cutting / device-level — route to the **system DHF's `leaf`** (the canonical home for cross-component analysis, per `docs/_analysis/README.md`'s "cross-component findings live in the system folder" convention).
   - If no `docs/_analysis/README.md` exists and `project.yml dhfs[]` is unavailable, fall back to `docs/_analysis/<doc-slug>/` (degenerate single-folder convention).
4. **Compute analysis-id** — `<doc-slug>-references-audit` (mirrors `/gap-analysis`'s `<id>` convention: kebab-case identity that names the topic; the references-audit suffix distinguishes from a gap-analysis on the same doc).
5. **Create** `docs/_analysis/<component>/<analysis-id>/` if missing. If `<analysis-id>.md` already exists in that folder, do not clobber — report "audit exists; run `/reference-audit fan-out <analysis-id>` to refresh findings, or delete the file to re-init from scratch" and stop.
6. **Scaffold a folder README** at `docs/_analysis/<component>/<analysis-id>/README.md` — name, purpose, file inventory, scope, conventions, changelog. Required by the readme-before-write rule for any new folder under `docs/`.
7. **Read the template** at `templates/references-audit.md` and scaffold the report at `docs/_analysis/<component>/<analysis-id>/<analysis-id>.md`, substituting:
   - `<doc-title>` — title of the source doc (first `#` heading).
   - `<source-path>` — repo-relative path to the source.
   - `<audit-id>` — `RA-<doc-slug>-001` (NNN increments if there are multiple audits for the same doc).
   - `<created>` — today's date in ISO-8601.
8. **Extract references** from the source doc using the hybrid two-pass strategy:
   - **Regex pass** — find structured citations and links. Default pattern catalog (project-agnostic):
     - `ISO \d+(:\d+)?(?: § \S+)?`
     - `IEC \d+(?:-\d+)?(?::\d+)?(?: § \S+)?`
     - `\d+ CFR \d+(?:\.\d+)*(?:\([a-z0-9]+\))?`
     - `K\d{6}`, `DEN\d+`, `P\d+`
     - markdown links: `\[([^\]]+)\]\(([^)]+)\)`
     - FDA guidance titles matching files under `.claude/skills/medtech-docs/references/fda-guidance/`
     - Decision-ID anchors of the form `D-[A-Z]+-\d+(\.\d+)?` when they appear as references rather than as the cited block itself.
   - **LLM pass** — read the source doc's narrative prose (skipping spans already extracted by regex) and identify prose pointers: "see X", "per the Y strategy doc", "as established in §Z", "the predicate analysis shows…". These are informal-link references — emit them with `reference_class: informal-link` and `extraction_method: llm`.
9. **Write the extracted references** into the scaffold's `## References (Pending Verification)` section as a YAML block — one entry per reference with `id`, `claim` (the surrounding sentence or, for prose pointers, the inferred claim), `reference_target`, `source_doc` = the source path, `source_anchor` = a heading or line reference where the citation appears.
10. **Report** number of references extracted by class + path to the scaffolded report.

### `fan-out <analysis-id>`

Verify every pending reference in an existing audit scaffold. Invokes the `citations` advisor in batch mode and writes findings into the report.

1. **Locate** the audit file by `<analysis-id>` — glob `docs/_analysis/*/<analysis-id>/<analysis-id>.md` (the component segment is determined by where `init` placed the audit). Parse the `## References (Pending Verification)` YAML block.
2. **Group references by class** if needed for efficiency, but invocation itself is per-reference — the `citations` advisor's two invocation modes are point-query (one reference) and batch (a list). For larger audits, pass references to `citations` in one batch invocation so the advisor can dispatch its researchers in parallel internally.
3. **Invoke the `citations` advisor** via the Agent tool, passing the references list and asking for a `findings[]` response. The advisor handles classification and researcher dispatch per its contract.
4. **Consolidate findings** into the report:
   - Update the `## Summary` table (counts by class × status).
   - Move each entry from `## References (Pending Verification)` into one of `## Findings (broken)`, `## Findings (unverified)`, or `## Findings (sound)` per the verdict.
   - Each finding entry carries: reference target, claim, status, kind, evidence (resolving source paths + excerpts), suggested fix (omit for `sound`).
5. **Update status** in the report frontmatter: `Extracting → Researching → Findings Posted`.
6. **Report** summary counts and the report path back to the user.

### `list`

Roll-up of open reference audits across `docs/_analysis/`.

1. **Glob** `docs/_analysis/*/*-references-audit/*-references-audit.md` (component-keyed; matches the project convention `/gap-analysis` already uses).
2. For each, read the frontmatter for `Status`, `Audit ID`, and the summary counts.
3. **Render** a markdown table — Audit ID, source doc, status, counts (sound / unverified / broken), last updated.
4. Tail with a hint: `/reference-audit fan-out <analysis-id>` to refresh.

## Notes

- **The `citations` advisor enforces the "cite both" mandate for external-formal references** — L1a registry distillation + L1b project applicability are checked in tandem. The skill does not need to re-implement this; trust the advisor's verdict.
- **`docs/_analysis/` is the conventional home for analysis artifacts** — same folder pattern as `/gap-analysis`. Both skills can coexist there without conflict (different filenames: `gap-analysis.md` vs `references-audit.md`).
- **Project-agnostic.** The skill ships no project-specific paths, names, or examples. Layer paths (`docs/external/`, `docs/internal/`, `docs/project/`, `glossary.md`, `project.yml`) are conventional defaults defined by the `medtech-docs` skill and apply to every medtech project from the registry.
- **Re-running `init` is non-destructive.** If a report exists, the skill stops rather than clobber it. Use `fan-out` to refresh findings or delete the report to start over.
- **No hooks.** This skill does not register any hooks. Hook-based audits (e.g., "audit references on commit") are explicitly out of scope for v1 — too easy to be noisy. Audits are user-invoked.
- If `$ARGUMENTS` is empty or just "help", show this usage guide.

## v1.1 enum + v2 Roadmap

**Emitted in v1.1:**

- `sound` — reference resolves and content supports the claim (per semantic-predicate match — see `citations-external-researcher` Step 3.5; not just clause-existence). Source-md-backed (fda-guidance, regulations) or internal.
- `sound-by-distillation` (v1.2, band `sound`) — paywalled standard with no bundled source-md: L1a covers the clause number, predicate matches, L1b agrees or is silent, no clause-numbering quarantine. The kind carries the limitation ("original not on file"); the band is `sound` because the two-tier cite-both mandate is met. **Deterministic** — see the paywalled-standard band rule in `citations-external-researcher` (rows 1–8): quarantined numbering → `ambiguous-source`; exact-wording claim → `unreachable-source`; label absent from an enumerated skeleton → `citation-absent-from-source`; label absent where the aid does not inventory that part → `ambiguous-source`.
- `broken-link` — internal link / path does not exist.
- `citation-absent-from-source` — a cited external label (Example/Scenario/§/clause/table/appendix **number**) does not appear anywhere in the byte-correct source; the citation names a location that does not exist. Emitted by the external researcher's Step 3.5 label-existence check.
- `citation-mislabeled` — the cited *content* exists in the source but under a *different* label/number than cited (right analog, wrong coordinates); suggested fix names the correct label.
- `stale-citation` — external source exists but its **predicate** does not match the claim's — same clause number, different topic. Emitted by Step 3.5 predicate match.
- `unresolved-anchor` — doc + heading does not resolve.
- `unreachable-source` — fetch failure / paywalled / 404. **Includes K-number WebFetch failures** (v1.1) — do not fall back to internal-corroboration → `sound`.
- `ambiguous-source` — source exists but its support of the claim is unclear.
- `registry-gap` (v1.1) — neither L1a nor L1b has a distillation for the cited standard/regulation. Suggested fix extends the registry (cross-project win via `/sync-skills push`).

**Reserved for v2 (not emitted):**

- `applicability-gap` — L1a covers, L1b silent for this project; suggested fix extends the project's applicability file.
- `applicability-conflict` — L1b contradicts the citing claim.
- `obligation-unmapped` — citation references a regulation that has no obligation entry in the dhf-manifest Tier-1 obligation catalog (`.claude/skills/dhf-manifest/data/`).
- `unsourced-claim-candidate` — paragraph asserts a regulatory/clinical/standards fact with no citation; routed to SME advisor for adjudication.
- `weak-reference` / `stronger-source-exists` — a stronger source exists for the same claim.

v1.2 (2026-09-08) adds the **paywalled-standard band rule** after a validation protocol (workbench TC-PROTO-CITATIONS, three runs) showed the band for the same paywalled-clause evidence drifting `sound` → `unverified` between runs. Same evidence, same band, always: the decision table in the external researcher is the contract; `sound-by-distillation` is the new kind that keeps the limitation visible without sacrificing determinism.

v1.1 captures the three engine-quality fixes from the first batch pilot's findings: tighter semantic-predicate match (catches stale-citations the v1 researcher rubber-stamped), `registry-gap` as a first-class verdict (so missing distillations are surfaced rather than masked by internal-cross-reference fallback), and stricter web-fetch-failure posture (K-number `unverified` rather than internal-fallback `sound`). v2 kinds extend into adjudication-adjacent territory.
