# 012 — medtech-docs `update-external-references` action

**ID**: 012
**Created**: 2026-04-14
**Status**: In Progress
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: Medium

---

## Goals

Add a new context-driven action to the `medtech-docs` skill that imports the bundled distilled FDA guidance, standards, and industry-framework reference files into `docs/external/` based on the project's actual signals (project.yml + CLAUDE.md + strategy briefs + per-DHF READMEs). Idempotent so the team can re-run it as the project evolves.

- Add `update-external-references` action to `.claude/skills/medtech-docs/SKILL.md` (v15).
- Define a deterministic per-file rubric across all 23 bundled distilled files (10 FDA + 5 standards + 8 frameworks).
- Update the three subfolder README templates (`readme-fda-guidance.md`, `readme-standards.md`, `readme-industry-frameworks.md`) so each table carries an "Original Source" / "Spec URL" column linking back to the bundled originals (FDA: source PDF + source-md in skill library; standards/frameworks: publisher URL).
- Run the action against PDLC_DEMO and populate `docs/external/fda-guidance/` (currently empty save for README) and any newly-applicable standards/frameworks.
- Push v15 of the skill upstream to hitachi via `/sync-skills push`.

## Todos

- [x] Add `update-external-references` action to medtech-docs SKILL.md
- [x] Bump skill version 14 → 15 + update frontmatter description + add changelog entry
- [x] Rewrite `templates/readme-fda-guidance.md` from "applicability reports" model to unified "distilled copies hosted here, originals linked" model (model B)
- [x] Add "Original Source" column to `templates/readme-standards.md` Distilled Standards table
- [x] Add "Spec URL" column to `templates/readme-industry-frameworks.md` Active Frameworks table
- [x] Run the action against PDLC_DEMO — copy applicable distilled files into `docs/external/`
- [x] Rewrite `docs/external/fda-guidance/README.md` to match v15 template + populate Active Guidances table with the 10 imported FDA guidances
- [x] Update `docs/external/standards/README.md` with Original Source column populated
- [x] Update `docs/external/industry-frameworks/README.md` with Spec URL column populated
- [x] Re-imported `ihe-profiles.md` and moved IHE row from "Evaluated — Not Required" to Active — the prior exclusion only considered the imaging angle and missed the ITI profiles applicable to EHR integration
- [x] Update the action so when the rubric flags a file that exists in an existing "Evaluated — Not Required" table, it surfaces the conflict to the user (rather than auto-importing or auto-skipping) — landed as **medtech-docs v16** (PR #14, merge `2d88ce6`); also added the Scope Qualifier column to all three subfolder readme templates so future exclusions are auditable per slice
- [ ] Run `/medtech-docs dashboard` to confirm new files are picked up
- [ ] `/sync-skills push` v15 upstream to hitachi
- [ ] Mark task Complete

## Strategy

<!-- STRATEGY CONTENT: development, skill-design, idempotency, external-references-model -->

### Model decision: distilled copies live in the project (model B), not applicability reports (model A)

When designing this action there were two viable models for what `docs/external/<subfolder>/` should hold:

- **Model A** — project folder holds project-specific *applicability reports* per guidance (one `topic.md` each), and the distilled requirement text stays in the skill library. This was the model the existing `templates/readme-fda-guidance.md` (v14) implied.
- **Model B** — project folder hosts a *copy* of the distilled file itself. Originals are linked by URL.

Model B was chosen for three reasons:

1. **Consistency with existing project state.** `docs/external/standards/` and `docs/external/industry-frameworks/` already host distilled content directly (`iec-62304.md`, `nist-csf.md`, etc.). Model A only matched fda-guidance, and only by template — not by practice. Picking model B unifies all three.
2. **Travels with the repo.** A reviewer cloning the project repo gets the distilled content in the same checkout, without needing the skill library installed. Important for handoffs and audits where the skill registry isn't available.
3. **Edit-in-place is the natural workflow.** Teams want to add `[VERIFY]` markers, project-specific notes, and applicability deltas on top of the distilled content. Model B keeps those edits next to the source they're annotating.

The trade-off accepted: distilled copies will drift from the bundled originals over time as the skill library is updated. This is acceptable because (a) the README links back to the originals so drift is auditable, and (b) the action **never overwrites** existing project files on re-run, so any team annotations are sacred. To pick up updates from the skill library, a team must explicitly delete the project file and re-run.

### Idempotency model: never-overwrite, never-delete, drift-tolerant

The action's three states (`created` / `unchanged` / `newly-not-applicable`) are designed so the action can be invoked many times across a project's life without surprising side effects:

- `created` — distilled file copied verbatim from skill library because the project file did not exist.
- `unchanged` — project file already exists; we leave it alone, even if the bundled distilled file has been updated upstream. User edits are sacred.
- `newly-not-applicable` — project file exists but the rubric no longer marks it applicable (e.g., strategy doc removed PCCP scope). The README table row gets a `[~] retained — no longer applicable per current strategy` annotation but the file stays on disk. We never delete user content.

Project files not present in the skill library at all (e.g., manually-authored `iec-60601-1.md`) are left untouched and reported as `unchanged (not in skill library)`. This is critical because some projects will have jurisdiction-specific or hardware-specific standards that aren't in the bundled set.

### Rubric source-of-truth: signals over structured flags

Earlier in the design I asked whether to add structured `capabilities:` flags to `project.yml` (e.g., `samd: true`, `connectivity: true`, `ai_ml: true`) so the rubric could be deterministic. The user chose to **rely only on existing signal sources** — `project.yml`, `CLAUDE.md`, and `docs/project/strategies/*.md`. Reasons:

- PDLC_DEMO already has `project.yml capabilities:` (ai_ml, ehr_integration, medical_imaging, surgical_navigation) and `composition:` (samd, simd, hardware), so most signals are already structured.
- The strategy docs are where the *interpretation* lives ("we're filing a PCCP, here's the scope") — duplicating that into project.yml flags would just create two places to keep in sync.
- New rubric entries can be added without a project.yml schema change.

The cost is that the rubric's "applies when X" rules have to read prose from strategy briefs in some cases (e.g., "PCCP applicable" is determined by reading regulatory-strategy.md, not by a flag). This is acceptable for a Claude-driven action — it's exactly the kind of judgment Claude is good at.

### Action discoverability via natural-language aliases

The action's name is `update-external-references` (precise but verbose). Users will reach for natural phrasings like "import fda docs", "pull reference guidances", "refresh external references". The SKILL.md description for v15 explicitly lists those aliases as triggers, and the medtech-docs skill description in the registry was updated to mention "import FDA guidance / standards / industry frameworks" so the skill auto-trigger picks it up. This is a small but important UX detail — the user should not have to remember the exact action name.

## Lessons Learned

<!-- LESSONS LEARNED: skill-design, task-discipline, project-conventions -->

### Skill-design lesson: check existing project state before committing to a doc model

While designing this action I almost shipped model A (applicability reports), based purely on what the v14 `readme-fda-guidance.md` template said. A 30-second `ls` of `docs/external/standards/` and `docs/external/industry-frameworks/` immediately showed the project was already practicing model B for the other two folders — the v14 fda-guidance template was the outlier, not the norm. Lesson: when a skill action touches a folder whose template prescribes a model, validate against actual project state before designing around the template. Templates can be wrong or stale; the project's lived structure is the better signal.

### Task-discipline lesson: activate the task before any writes, not after the design phase

I started this work without an active task and got blocked by the task-gate hook on the very first `Write` call (rewriting `docs/external/fda-guidance/README.md`). The skill edits earlier in the session (`SKILL.md`, three template files) had slipped through because I happened to use `Edit` on files that were already part of an active session context — but the moment I tried a fresh `Write`, the gate fired correctly. The gate is doing its job; my discipline was off. Lesson: when starting any non-trivial work session, the first action should be `/task find` or `/task create`, before any tool calls. Don't wait until the gate denies you.

### Rubric-vs-existing-exclusion lesson: surface conflicts, don't silently defer either way

The first rubric run flagged `ihe-profiles.md` as applicable based on PDLC_DEMO's `ehr_integration: true` capability. The existing `docs/external/industry-frameworks/README.md` had IHE Profiles in its "Evaluated — Not Required" table with the rationale "No imaging workflow integrations in scope". I initially reverted the import on the assumption that the existing project decision should win.

The user corrected me: **IHE Profiles is applicable.** The prior exclusion was incomplete — it only considered IHE's imaging angle (the radiology profiles most people associate with IHE) and missed the ITI / Pharmacy / Patient Care domain profiles (PIX/PDQ for patient identity reconciliation, XDS for cross-enterprise document exchange, ITI cross-enterprise workflows) that absolutely apply to PDLC_DEMO's EHR/FHIR integration and its drug-library / fleet / clinical-interface DHFs. The exclusion rationale was framed too narrowly.

So: the rubric was right and the captured human judgment was wrong-because-incomplete. The right behavior for the action is **neither** "defer to rubric" **nor** "defer to existing exclusion" — it is to **surface the conflict to the user** and let them decide. Concretely, the v15 action should:

1. Before applying the rubric, read each subfolder's "Evaluated — Not Required" table and note any rows.
2. Apply the rubric.
3. For any file where the rubric says "applicable" but the exclusion table contains it, do NOT silently import and do NOT silently skip. Instead, print a conflict block:

   ```
   CONFLICT: ihe-profiles.md
     rubric says: applicable (trigger: EHR / health data exchange or imaging interop)
     existing exclusion: "No imaging workflow integrations in scope" (industry-frameworks README)
     Resolve: import + move row to Active, OR keep excluded with refined rationale.
   ```

4. Wait for user resolution before touching either the file or the README table.

The general principle: when a Claude action's heuristic disagrees with a captured human decision, **the action's job is to surface the disagreement, not to pick a side.** Both the rubric and the captured decision can be wrong. Only the user has the context to resolve the conflict, and silencing it in either direction loses signal. This applies to all idempotent context-aware actions, not just `update-external-references`.

A secondary lesson: exclusion rationales should be auditable. "No imaging workflow integrations in scope" was a fine reason to exclude the imaging slice of IHE but a bad reason to exclude IHE wholesale. Exclusion entries that name a framework should also name *which slice* they apply to, so that future runs (or future humans) can tell whether new project capabilities reopen the question. The framework README should probably grow a "scope qualifier" column to make this explicit — adding to remaining todos.

### Project-conventions lesson: "one task, one file" applies to skill work that touches the project

The CLAUDE.md "one task, one file" rule applies even when the work is inside `.claude/skills/` rather than `docs/`. Skill changes that are scoped to a project (designed in conversation with the user, applied to this project's folders) should still be captured in a task doc — both for the strategy/lessons capture pipeline and so future sessions can find the rationale. The fact that the skill itself lives outside `docs/` doesn't change that.

## Changelog

- 2026-04-14: Task created. Captured the design conversation that led to v15 of medtech-docs:
  - User asked whether the skill could pull FDA documents into the external folder. Discovered the skill bundles distilled FDA guidance + standards + frameworks but had no action to import them.
  - User asked for option (2) — extend the skill to context-drive the import. Confirmed model A (applicability reports linking to skill library) initially, then unified on model B (distilled copies hosted in the project, originals linked) after I surfaced the divergence between the v14 fda-guidance template and the actual practice in standards/frameworks.
  - Confirmed action name `update-external-references` with natural-language aliases ("import fda docs", "pull reference guidances", etc.).
  - Confirmed the rubric's signal sources are project.yml + CLAUDE.md + `docs/project/strategies/*.md` only — no new structured flags in project.yml.
- 2026-04-14: Implemented v15 of medtech-docs:
  - `SKILL.md` — added `update-external-references` action (Step 1 read context, Step 2 apply rubric across all 23 bundled distilled files, Step 3 copy never-overwrite, Step 4 update each subfolder README table, Step 5 print summary). Bumped version 14 → 15. Added v15 changelog entry.
  - `templates/readme-fda-guidance.md` — full rewrite from model A to model B.
  - `templates/readme-standards.md` — added "Original Source" column.
  - `templates/readme-industry-frameworks.md` — added "Spec URL" column.
- 2026-04-14: Ran the action against PDLC_DEMO. Applied the rubric to PDLC_DEMO's signals (510k pathway, predicate PP3000 K190567, samd+simd+hardware composition, ai_ml=true, ehr_integration=true, medical_imaging=false, surgical_navigation=false, PCCP central per regulatory-strategy.md, connected via cloud-suite + connectivity-adapter, multi-function via cloud-suite's 7 child apps). Result:
  - **fda-guidance**: 10 created (qsub, 510k-se, sw-functions, sw-changes, cybersecurity, mfd, cds, pccp-general, pccp-aiml, ai-dsf-lifecycle). All 10 bundled FDA guidances apply. None skipped.
  - **standards**: 0 created, 5 unchanged (iso-14971, iec-62366-1, iec-62304, iec-82304-1, iec-81001-5-1 already present from earlier project work), 1 unchanged-not-in-skill-library (iec-60601-1 — manually authored for the hardware DHF, retained as-is).
  - **industry-frameworks**: 1 created (ihe-profiles for EHR/imaging interop), 5 unchanged (gmlp, hl7-fhir, nist-csf, ntia-sbom, owasp). 2 skipped (dicom: medical_imaging=false; astm-f2554: surgical_navigation=false).
- 2026-04-14: Task gate blocked the first `Write` call (rewriting the fda-guidance README). Created this task and activated it under the current session ID before continuing the README writes.
- 2026-04-14: Rewrote `docs/external/fda-guidance/README.md` to v15 model (model B, distilled copies hosted here, originals linked back to skill library). Populated the Active Guidances table with all 10 imported FDA guidances and their PDF + source-md links into `.claude/skills/medtech-docs/references/fda-guidance/`. Each row has a Trigger column documenting which project signal drove the decision (qsub: always; 510k-se: pathway; sw-functions: composition; sw-changes: predicate; cybersecurity: connected; mfd: cloud-suite multi-function; cds: predictive-alarm SaMDs; pccp-general: PCCP filing; pccp-aiml: PCCP+AI; ai-dsf-lifecycle: AI/ML).
- 2026-04-14: Updated `docs/external/standards/README.md` — added "Original Source" column with publisher URLs for all 6 standards (5 from skill library + iec-60601-1 manually authored). Added changelog entry noting the 0/5/1 result.
- 2026-04-14: Updated `docs/external/industry-frameworks/README.md` — added "Spec URL" column for all 5 active frameworks. Initially reverted the `ihe-profiles.md` import on the (wrong) assumption that the existing "No imaging workflow integrations in scope" exclusion should override the rubric.
- 2026-04-14: User correction: **IHE Profiles is applicable** to PDLC_DEMO. The prior exclusion only considered IHE's imaging angle and missed the ITI / Pharmacy / Patient-Care domain profiles (PIX, PDQ, XDS, cross-enterprise document exchange) that apply to the EHR/FHIR integration and to the cloud-suite child DHFs (drug-library-manager, clinical-interface, fleet-management). Re-imported `ihe-profiles.md` into `docs/external/industry-frameworks/`, moved the IHE row from the "Evaluated — Not Required" table to the Active Frameworks table with a Referenced In note that captures the ITI-domain rationale. Rewrote the Lessons Learned entry: the right behavior for the action is to **surface the conflict to the user**, not to silently defer in either direction. Added two follow-up todos: (1) extend the v15 action to print a conflict block when the rubric and an existing exclusion disagree; (2) add a "scope qualifier" column to the framework README's exclusion table so exclusion rationales are auditable per slice.
- 2026-04-14: medtech-docs v15 pushed to hitachi as PR #13 (squash-merge `d30a7f3`). All four files merged: SKILL.md, readme-fda-guidance.md (full rewrite), readme-standards.md, readme-industry-frameworks.md.
- 2026-04-14: Implemented medtech-docs v16 — both follow-ups landed in one PR:
  - **SKILL.md Step 2.5**: new step between rubric application and file copy that reads each subfolder README's exclusion table and detects collisions with the rubric's applicable set. On conflict, prints a CONFLICT block per file (rubric trigger + existing exclusion rationale + scope qualifier) and waits for the user to resolve as IMPORT (rubric wins, move row to Active), KEEP EXCLUDED (refine rationale + scope qualifier), or DEFER (leave both untouched, log a TODO). Backwards-compatible — degrades gracefully when no exclusion table is present.
  - **All three subfolder readme templates**: gained a "Scope Qualifier" column on their exclusion tables. Prevents the failure mode where a too-broad rationale silences future applicability for an umbrella spec family.
  - Pushed as hitachi PR #14 (squash-merge `2d88ce6`).
