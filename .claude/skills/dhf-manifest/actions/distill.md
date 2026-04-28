# Action: `distill-qms [topic]`

Draft Tier 2 QMS topic files from `docs/internal/source-md/` using the `dhf-distiller` agent.

## Usage

```
/dhf-manifest distill-qms <topic>
/dhf-manifest distill-qms --all
```

## Steps

1. **Resolve topic** — validate that `<topic>` is one of the 16 DHF topics. If `--all`, queue all 16.

2. **Find relevant source files** — scan `docs/internal/source-md/` for files whose title, section headings, or index entry suggest relevance to the topic. Use `docs/internal/source-md/INDEX.md` and `qms-reference-graph.md` as the discovery map. Do not read all 123 files; use index-driven triage.

   Topic → primary source types to check:
   - `architecture`: WI-000100050 (Design Output), WI-000101591 (HAA SDLC §4.5), POL-000100035 (Design Control)
   - `requirements`: WI-000100049 (Risk Management), SOP for design inputs
   - `risk-management`: SOP-000355609, POL-000100241, POL-000355608, WI-000100049, QSD-000108614, QSD-000106175, RM FORMs
   - `software-lifecycle`: WI-000101591 (HAA SDLC), SDP WI
   - `configuration-change`: CM WIs, change-control SOPs
   - `design-reviews`: Design review WIs, phase-gate FORMs
   - `verification` / `validation`: V&V WIs, test protocol FORMs
   - `traceability`: Design control SOP traceability sections
   - `cybersecurity`: Cybersecurity SOPs/WIs if present
   - `human-factors`: HF/UE WIs if present
   - `labeling-ifu`: Labeling SOPs
   - `clinical`: Clinical evaluation SOPs
   - `post-market`: PMS SOPs, complaint handling WIs
   - `regulatory-submission`: Regulatory SOPs (SOP-000143689, WI-000100423)
   - `design-outputs`: WI-000100050 (Design Output WI) primarily
   - `design-reviews`: Design review WIs and phase-gate checklists

3. **Invoke `dhf-distiller` agent** — pass the topic, source file list, relevant Tier 1 obligation IDs for cross-linking, and the `tier2-topic.md.tmpl` template.

4. **Append a draft H2 section + `<!-- QMS-DATA -->` block per source SOP to `docs/project/dhf-manifest/qms-manifest.md`** — one H2 per SOP/WI/FORM/POL the distiller extracts records from. Each section carries a compact markdown table and a single `<!-- QMS-DATA ... -->` HTML comment block with the structured YAML records. If a section for that SOP already exists, flag the new records under a `**Draft (pending merge):**` note so a human can merge without clobbering reviewed content.

5. **Report** — number of records extracted, source files scanned, any paragraphs flagged as ambiguous scope.

## Title style guide (required per record, as of task 104 Phase 4)

Every record emitted by the distiller MUST carry a `title:` field. The title is rendered everywhere as `[QMS-XXX · Title](source.md#QMS-XXX)` — bad titles surface in every dashboard and become load-bearing for reviewer / auditor readability.

Style rules:
- **3–6 words, Title Case, ≤ 60 chars**
- Describes *what the procedure covers* — not a fragment of the first requirement, not generic SOP language
- Prefer the source document's title when 1 record is extracted (e.g., `Risk Management Plan` for FORM-000364987)
- When 2+ records share a source document, disambiguate by section (`Design Control Policy §4.4`) or topic suffix (`Design Control Policy — Verification`)
- No pipe chars, no markdown link syntax, no trailing punctuation

Worked examples:

| QMS-ID | source_title | Good title | Bad title (why) |
|--------|-------------|-----------|------------------|
| QMS-RM-004 | Risk Management Plan | `Risk Management Plan` | `Plan Shall State It is Created` (requirement fragment) |
| QMS-RM-011 | Risk Management Report | `Risk Management Report` | `Has the Risk Management Plan Been` (fragment, incomplete) |
| QMS-ARCH-005 | Design Control Policy | `Design Control Policy` | `MedTech Project is a New Project` (project-specific, not procedure-level) |
| QMS-RM-013 | Risk Management and Device Safety Policy §5.3 | `RM Device Safety Policy §5.3` | `Risk Management and Device Safety Policy` (collides with QMS-RM-014 same source_title) |

**Enforcement**: `build-manifest.py` and `build-qms.py` run a post-build grep check for bare `QMS-\w+` / `OBL-\w+` occurrences outside markdown link syntax. Any bare ID in produced dashboards fails the build.

## Output file format

Records conform to the schema inside `<!-- QMS-DATA -->` blocks (id / source / source_title / topic / artifact_type / dhf_owner / applies_to / regulatory_grounding / verbatim / extracted_requirements / context). Status is always `draft` on first emit. After human review, run `/dhf-manifest build-qms` to regenerate `qms-manifest.json`.

## Quality gates

- Agent must not fabricate source document numbers — only cite docs present in source-md corpus
- Verbatim field must be exact text from the source-md file (copy-paste, not paraphrase)
- If no relevant obligations found in the scanned sources, emit a file with a single `# No obligations found` section and a note on what was scanned — do not emit empty records
