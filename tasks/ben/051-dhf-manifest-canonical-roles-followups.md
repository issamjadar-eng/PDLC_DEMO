# 051 — DHF-Manifest Canonical-Roles Follow-ups

**ID**: 051
**Created**: 2026-05-12
**Status**: Complete (all 6 phases done; pushed + merged upstream)
**Created By**: Ben
**Owner**: Ben (with Claude)
**Priority**: Medium

---

## PERMANENT RULES (do not remove)

This task document is the **session-recovery point** for this work. If the current session drops, is compacted, or ends, the next session must be able to load **this file alone** and continue where we left off. That is only possible if the doc is kept current in-flight.

1. **Update at every meaningful checkpoint (HARD RULE).** After each meaningful unit of work — a converted/adopted doc, a committed change, a launched batch, a completed phase, a decision, a discovered blocker, a design pivot — update this task doc:
   - tick the relevant Todo checkbox
   - add a dated Changelog line naming the concrete artifact (commit SHA, file path, decision, blocker)
   - update any progress counts/tables in Goals
2. **Phase-end batching is OK; drift-batching is not.** Planned phases (e.g., "finish Phase 2, then log the whole phase at once") are a legitimate checkpoint — writing once per phase is fine if the phase is bounded and the write happens **at the phase boundary, before the next phase starts**. What's not OK: accumulating updates in your head across arbitrary work, waiting for "end of the session," "after the push," or the user to ask. By then a crash or context-trim has lost the state. Rule of thumb: if you can't name the specific upcoming checkpoint where you'll write the update, write it now.
3. **A commit is not a substitute.** Git history records code; this doc records the project narrative — what was done, why, what's left, what surprised us.
4. **Resume-ready before any session boundary.** Before recommending a fresh session, marking Complete, or ending work, the doc must already contain: (a) what was completed this session with concrete artifacts, (b) status of any in-flight work and temp artifacts, (c) priority-ordered next steps with file paths, (d) open questions blocking progress, (e) the exact `/task` activation command to resume.
5. **Capture strategy + lessons as they happen.** If the session produces option comparisons, scope/boundary decisions, architectural pivots, non-obvious insights, or corrected assumptions, write them into the appropriate section **in-flight** — not just in chat. Harvesting skills can only surface what was written.

Success test for this doc: a fresh Claude session, given only this file, can re-enter the work without asking the user "what were we doing?"

## Goals

Three follow-up improvements to the `dhf-manifest` skill's canonical-role resolution surfaced during the [[task-050]] post-sync `/dhf-manifest discovery-index` run. The skill's v9 `canonical-roles.yaml` ships Title-Case pattern variants that don't match medtech-docs' lowercase-hyphen filename convention, which forced a project-side `evidence_layout.layers` override in `project.yml`. These improvements remove the need for that override in the common case and make resolution more debuggable.

1. **Lowercase-hyphen filename pattern variants in `canonical-roles.yaml`.** Add lowercase-hyphen alternates alongside the existing Title-Case patterns so out-of-the-box discovery resolves correctly for projects following the medtech-docs filename convention. Project-side overrides should remain available but become unnecessary for the canonical role set.
2. **Bug fix — populate `ambiguity_notes[]` on multi-match no-winner.** Currently when discovery finds multiple candidates and no scoring winner, the role resolves to "unresolved" with no diagnostic trail. The expected behavior is that `ambiguity_notes[]` is populated with the candidates considered and the reason no winner was selected, so the user can act on the gap.
3. **Frontmatter `canonical_role` declaration as author-facing opt-in.** Add support for authors to declare `canonical_role: <slug>` in document frontmatter, taking precedence over filename-based discovery. This is the author's escape hatch for non-standard filenames and resolves the ambiguity once and for all.

**Scope boundary**: this task is scoped to deterministic resolution improvements. LLM-subagent-driven ambiguity resolution (`--resolve-ambiguity`) is **deferred indefinitely** per the [[task-050]] decision — deterministic improvements first.

## Why this matters

The current skill behavior in PDLC_DEMO required a project-side `evidence_layout.layers` override in `project.yml` to map `user_needs` and `software_requirements` because the upstream patterns are Title-Case (e.g., `User_Needs.md`) while medtech-docs convention is lowercase-hyphen (e.g., `user-needs.md`). Every new medtech-docs project will hit the same friction. Fixing the patterns upstream is a low-risk skill change that improves out-of-the-box behavior for the entire registry consumer base.

The ambiguity-note bug compounds the friction — when discovery fails, the user has no breadcrumbs to follow.

The frontmatter opt-in is the author-facing answer to the long-tail case (renamed legacy docs, unusual file conventions) and doesn't require any project-level configuration.

## Source files involved (where the work lives)

To be confirmed by reading `SKILL.md` end-to-end **before** any plan is finalized — per [[feedback_read_skill_before_planning]]. Provisional list based on prior context only:

| File | Likely change |
|---|---|
| `.claude/skills/dhf-manifest/canonical-roles.yaml` | Add lowercase-hyphen pattern variants alongside Title-Case |
| `.claude/skills/dhf-manifest/scripts/*` (TBC) | Bug fix: populate `ambiguity_notes[]` on multi-match no-winner; add frontmatter `canonical_role` precedence |
| `.claude/skills/dhf-manifest/SKILL.md` | Document the frontmatter opt-in and the ambiguity-note contract |
| `.claude/skills/dhf-manifest/README.md` | Bump version, add `## Changelog` row, update `## Best Practices` if applicable |

## Approach (high level)

Per [[feedback_read_skill_before_planning]]: **Read `.claude/skills/dhf-manifest/SKILL.md` end-to-end first**, then design the plan around the skill's documented actions and contracts. Do not infer behavior from filenames or output paths.

Validation per [[feedback_sister_project_compat]]: run any modified skill against `../../projects/arthrex/pccp/` and confirm no regression before pushing upstream.

Versioning per [[feedback_skill_version_bestpractices]]: bump `VERSION`, add a `## Changelog` row in `README.md`, review `## Best Practices` table.

Upstream push per the registry sync flow: only after PDLC_DEMO + sister project both pass; one PR with auto-merge opt-in.

## Todos

### Phase 0 — Read first
- [x] Read `.claude/skills/dhf-manifest/SKILL.md` end-to-end (per [[feedback_read_skill_before_planning]]) (2026-05-13)
- [x] Read `canonical-roles.yaml`, `actions/discovery-index.md`, and `scripts/discovery-index.py` end-to-end (2026-05-13)
- [x] Confirmed the discovery scoring code path that produces "unresolved" — three call sites consume `resolve_one()` and all three silently drop `alternatives[]` when `winner` is None: `resolve_project_role`, `_bind_per_dhf`, `resolve_per_submission_role`
- [x] Confirmed no frontmatter parser exists in the skill yet — Phase 4 will be net-new parsing

### Phase 1 — Plan
- [x] Phase ordering confirmed: bug fix → pattern variants → frontmatter opt-in. Rationale: the bug fix gives diagnostic visibility that helps validate the pattern-variant change. The PDLC_DEMO `user_needs` case is actually a multi-match ambiguity (not a missing-pattern), so the bug fix is the right first move.

### Phase 2 — Implement (bug fix first) ✓ COMPLETE
- [x] Implemented `ambiguity_notes[]` population on multi-match no-winner in all three call sites (`resolve_project_role`, `_bind_per_dhf`, `resolve_per_submission_role`). New behavior: when no pattern produces exactly-one match BUT alternatives exist, emit an `ambiguity_notes[]` entry with `winning_pattern: null` + `winning_path: null` + full `alternatives[]`, AND a paired `gaps[]` entry whose `reason` references the ambiguity notes. Schema impact: `winning_pattern` / `winning_path` are now nullable.
- [x] Added regression test (case9) modeled on the PDLC_DEMO `user_needs` scenario: two files (`user-needs.md` and `user-needs-register.md`) both matching `*user-needs*.md`. Asserts (a) role resolution is null, (b) ambiguity_notes contains a no-winner entry, (c) alternatives lists both candidates, (d) paired gap references the ambiguity notes. Suite 36 → 40 tests, all passing.
- [x] Diagnostic re-run on PDLC_DEMO with override stripped: surfaces multi-match-no-winner for user_needs on pca-device + connectivity-adapter + cloud-suite (as predicted) and "no file matched any pattern" for software_requirements on those same DHFs (true gap — Phase 3). Override restored.
- [x] Production re-run with override in place: counts unchanged (9 + 133, 221 gaps, 7 ambiguity_notes). 4 of the 7 ambiguity_notes are the new no-winner shape — surfacing previously-hidden ambiguities: `predicate_analysis` (3 README files matching `**/README.md` at different depths) and `fmea` for the 3 system DHFs (`*-fmea.md` matches both `*-design-fmea.md` and `*-process-fmea.md`). These are real diagnostic value-adds out of scope for Phase 2 but visible now for follow-up.
- [x] Sister-project validation per [[feedback_sister_project_compat]]: applied v10 script to `../../projects/arthrex/pccp/`, re-ran discovery-index. Result: bit-for-bit identical to v9 baseline (excluding timestamp). The bug fix is purely additive — no impact on projects without multi-match-no-winner cases. Sister project script reverted; upstream promotion deferred to `/sync-skills push` after Phase 4.
- [x] Version bumped v9 → v10. Frontmatter description + `actions/discovery-index.md` schema doc updated for nullable `winning_pattern` / `winning_path`. `README.md` changelog entry added.

### Phase 3 — Implement (pattern variants) ✓ COMPLETE
- [x] Added lowercase-hyphen variants to `canonical-roles.yaml` (skill v10 → v11). `user_needs` internal patterns prepend exact `user-needs.md` (outranks the broad `*user-needs*.md`). `software_requirements` internal patterns prepend `software-requirements.md` + `*software-requirements*.md` — previously had NO lowercase-hyphen pattern at all (only Title-Case + `*-srs.md`).
- [x] **Full-registry audit done.** Only `user_needs` and `software_requirements` were affected — every other role already carries lowercase-hyphen abbreviation variants (`*-sad.md`, `*-rmp.md`, `*-htm.md`, etc.). The `fmea` multi-match (`*-fmea.md` ↔ `*-design-fmea.md` + `*-process-fmea.md`) is a genuine two-document case, NOT a naming-convention bug — left for separate follow-up, not fixed here.
- [x] Removed the project-side `evidence_layout.layers` override (+ its explanatory comment) from `project.yml`.
- [x] Re-ran `discovery-index` with override removed: **9 + 133 resolutions, 221 gaps, 7 ambiguity_notes — bit-identical to the Phase 2 baseline.** No-winner ambiguity_notes are now just `predicate_analysis` + 3× `fmea` (the `user_needs` no-winner cases are gone — resolved by the exact-match prepend, as designed).
- [x] **Test wrinkle handled:** `case9` was modeled on the `user_needs` multi-match that Phase 3 deliberately fixes — so it broke (4 failures). Re-pointed the fixture to non-exact filenames (`user-needs-register.md` + `user-needs-archive.md`, neither matching exact `user-needs.md`) to keep the no-winner resolver path under test. Suite back to 40/40.
- [x] Version bumped v10 → v11. SKILL.md version-history comment + README.md changelog row added.

### Phase 4 — Implement (frontmatter opt-in) ✓ COMPLETE
- [x] Added frontmatter `canonical_role:` parsing (skill v11 → v12). New resolver helpers `parse_frontmatter_role()` (reads leading YAML frontmatter, returns the `canonical_role` slug) + `frontmatter_winner()` (scans immediate `*.md` children of the role's resolved folder). `resolve_one()` gains an optional `role_name` param; when supplied, a frontmatter declarer wins outright ahead of all filename patterns (`matched_pattern: "frontmatter:canonical_role"`). Threaded through all three call sites (`resolve_project_role`, `_bind_per_dhf`, `resolve_per_submission_role`).
- [x] **Precedence + conflict semantics:** single declarer → wins, patterns NOT consulted. Multiple declarers in one folder → no winner, surfaced via `ambiguity_notes[]` (`winning_pattern: null`) + paired `gaps[]`; resolver does NOT fall through to patterns (contradictory author intent needs human resolution). Scope: internal mode + project + per-submission; external-mode flat-file and `multi_file` folder-pointer roles unaffected.
- [x] Added `case10` — folder holds `user-needs.md` (would win via v11 exact pattern) + `legacy-un-doc.md` (declares `canonical_role: user_needs`). Asserts the frontmatter declarer wins, `matched_pattern` is `frontmatter:canonical_role`, and no ambiguity_notes emitted (clean win). Suite 40 → 43.
- [x] Documented in `SKILL.md` (v12 version-history comment), `actions/discovery-index.md` (new L0 layer in inputs table + algorithm step 0 + self-test count 9→10), `README.md` changelog. Resolver module docstring updated with algorithm step 0.
- [x] PDLC_DEMO re-run: 9+133 / 221 gaps / 7 ambiguity_notes — unchanged (no PDLC_DEMO doc declares `canonical_role` yet, so v12 is a clean no-op here).

### Phase 5 — Validate + Document
- [x] **Sister-project validation done** (per [[feedback_sister_project_compat]]). Applied all of task 051's skill changes (v9 → v12: bug fix + pattern variants + frontmatter opt-in) to `../../projects/arthrex/pccp/`. Clean apples-to-apples diff (v9 resolver vs v12 resolver, **same** working tree — the first diff attempt was contaminated by the sister's own uncommitted doc edits): **8 leaf differences, all in `gaps[].patterns_tried` arrays for `user_needs` + `software_requirements`** — both roles remain gaps (sister has no matching files), the only delta is the v11 patterns now appearing in the diagnostic `patterns_tried` list. Zero resolution changes, zero ambiguity changes, counts identical (10 project + 28 per-dhf, 97 gaps, 11 ambiguity_notes). Test suite 43/43 in the sister context. Sister skill dir reverted to v9. **⚠️ Caveat:** the sister had a pre-existing uncommitted change to its generated `arthrex-pccp-dhf-discovery.json`; the validation run overwrote it and the revert (`git checkout --`) restored it to HEAD — that prior regeneration is lost. Low impact (generated artifact, rebuildable) but should have been stashed first.
- [x] Version bumped across all three phases (v9 → v10 → v11 → v12); `README.md` changelog rows added per phase.
- [x] `SKILL.md` + `actions/discovery-index.md` documentation updated for all three changes.
- [ ] Commit (one commit per improvement — easier to revert individually) — **still pending; all v10–v12 changes uncommitted in the working tree**

### Phase 6 — Upstream ✓ COMPLETE
- [x] User confirmed ("push and merge").
- [x] Local commits: `3c06281` (skill changes v9→v12 + project.yml override removal + regenerated discovery JSON + this task doc), `bb86f7c` (sync-log entry). Note: consolidated into one skill commit rather than one-per-improvement — the three improvements are intermingled across the same 6 files, so hunk-splitting would be fragile; each is still a discrete skill version (v10/v11/v12) traceable via the changelog.
- [x] `/sync-skills push --merge` — branch `sync/pdlc-demo-dhf-manifest-canonical-roles-2026-05-13`, hitachi PR [#161](https://github.com/GlobalLogic-a-Hitachi-Company/hitachi/pull/161), squash-merged as `a85260d`. Local hitachi checkout fast-forwarded to `a85260d`. Recorded in `.claude/sync-log.md`.
- [x] The `evidence_layout.layers` override was removed in Phase 3 (not deferred to a post-merge pull) — already covered. No project-side `/sync-skills pull` needed; local skill files already match the merged upstream.

## Resume Command

```bash
bash .claude/hooks/task-activate.sh add <SESSION_UUID> 051
```

## Strategy + Lessons (inline captures)

<!-- STRATEGY CONTENT: architecture, development -->
**Pattern-ranking discipline for canonical-roles registries.** In a pattern-ordered registry like `canonical-roles.yaml`, broad wildcards (`*user-needs*.md`) at the top of the list will swallow specific filenames (`user-needs.md`) into multi-match ambiguity whenever any "register/log/scratch" sibling file also matches the wildcard. The robust ordering is **exact-match patterns first, then specific suffixes, then broad wildcards** — most-specific to least-specific. This is a load-bearing convention for any registry that uses "highest-ranked exactly-one match wins" semantics. Phase 3 of this task implements this for `user_needs` (exact `user-needs.md` prepended) and `software_requirements` (exact + lowercase-hyphen variants prepended). Should be audited across the full registry.
<!-- /STRATEGY -->

<!-- LESSONS LEARNED: skill-resilience, debuggability -->
**Silent-drop failure modes hide real bugs and blunt the diagnostic surface.** The discovery-index resolver was silently dropping multi-match-no-winner cases into a misleading "no file matched any pattern" gap reason — both lying about the cause AND throwing away the candidate list that would have made the gap actionable. The cost was invisible until [[task-050]] surfaced it via a project-side override that papered over the symptom. **Rule of thumb for resolver/diagnostic code: never drop information at a branch.** If a function gathers candidates that the happy path doesn't consume, the unhappy path must still surface them — and the gap/error message must accurately name the actual cause (multi-match-no-winner ≠ no-match). Applies to other discovery layers in the skill registry: `/trace-matrix` adapters, `/tracker` evidence-walks, `/best-practices` audit findings.
<!-- /LESSONS -->

## Open Questions

- Are there roles beyond `user_needs` / `software_requirements` in `canonical-roles.yaml` that also need lowercase-hyphen variants? Audit during Phase 0.
- Does the skill already have a frontmatter-aware parser elsewhere (e.g., the discovery walker reads frontmatter for other purposes) that the `canonical_role:` opt-in should plug into, or is this net-new parsing? TBC after reading `SKILL.md`.
- Should the frontmatter opt-in also accept a list (`canonical_role: [user_needs, design_inputs]`) for hybrid docs, or strictly a single slug? Default to single-slug; revisit if a real use case emerges.

## Changelog

| Date | Author | Summary |
|---|---|---|
| 2026-05-12 | Ben (with Claude) | Task created from [[task-050]] wrap-up. Three deferred dhf-manifest follow-ups scoped: (1) bug fix `ambiguity_notes[]` population on multi-match no-winner, (2) lowercase-hyphen pattern variants in `canonical-roles.yaml`, (3) frontmatter `canonical_role:` author-facing opt-in. LLM-subagent ambiguity resolution remains deferred indefinitely. Phase 0 (read `SKILL.md` end-to-end) is the first action per [[feedback_read_skill_before_planning]]. |
| 2026-05-13 | Ben (with Claude) | **Phase 4 complete (skill v11 → v12) + sister-project validation done.** Frontmatter `canonical_role:` opt-in implemented: new `parse_frontmatter_role()` + `frontmatter_winner()` helpers; `resolve_one()` gains optional `role_name`, threaded from all three call sites. A frontmatter declarer wins ahead of all filename patterns; multiple declarers in one folder → no-winner conflict (ambiguity_notes + paired gap, no fall-through to patterns). New `case10` (suite 40 → 43). Documented in SKILL.md / actions/discovery-index.md (new L0 layer) / README.md. PDLC_DEMO unchanged (no doc declares `canonical_role`). **Sister validation:** applied cumulative v9→v12 to arthrex/pccp; clean v9-vs-v12 diff (same working tree) = 8 leaf diffs, all in `gaps[].patterns_tried` for `user_needs`/`software_requirements` (still gaps, just updated diagnostic arrays) — zero functional regression, 43/43 tests, sister reverted to v9. Caveat: sister's pre-existing uncommitted change to its generated discovery JSON was lost in the revert (should have stashed). **Remaining: Phase 6 (commit + upstream push) — all v10–v12 changes still uncommitted. Next session: confirm with user, then commit (one per improvement) + `/sync-skills push`.** |
| 2026-05-13 | Ben (with Claude) | **Phase 3 complete (skill v10 → v11).** Added lowercase-hyphen pattern variants to `canonical-roles.yaml`: `user_needs` prepends exact `user-needs.md`; `software_requirements` prepends `software-requirements.md` + `*software-requirements*.md` (it had no lowercase-hyphen pattern at all before). Full-registry audit: those two were the only affected roles — the `fmea` `*-fmea.md` multi-match is a genuine two-document case (design + process FMEA), not a naming bug, left for separate follow-up. Removed the now-redundant `evidence_layout.layers` override from `project.yml`. Re-ran `discovery-index`: 9+133 / 221 gaps / 7 ambiguity_notes — bit-identical to the Phase 2 baseline, with the `user_needs` no-winner cases now resolved. `case9` test was modeled on the very `user_needs` ambiguity Phase 3 fixes, so it broke; re-pointed its fixture to non-exact filenames (`user-needs-register.md` + `user-needs-archive.md`) to keep the no-winner path tested — suite 40/40. SKILL.md + README.md version metadata updated. **Not yet done:** sister-project (arthrex/pccp) validation — deferred to Phase 5 per task structure; all Phase 2 + 3 skill changes still uncommitted in the working tree. Next session resumes from Phase 4 (frontmatter `canonical_role:` opt-in). |
| 2026-05-13 | Ben (with Claude) | Phases 0–2 complete. Read SKILL.md + discovery-index resolver end-to-end before planning. **Bug fix shipped (skill v9 → v10):** multi-match no-winner now surfaces as `ambiguity_notes[]` entry with nullable `winning_pattern`/`winning_path` + paired `gaps[]` reason. Three call sites updated (`resolve_project_role`, `_bind_per_dhf`, `resolve_per_submission_role`). Test suite 36 → 40 with new case9. PDLC_DEMO counts unchanged at 9+133 / 221 gaps / 7 ambiguity_notes (4 of which are the new no-winner shape — surfaced predicate_analysis README ambiguity + 3× fmea design-vs-process ambiguity in the system DHFs as diagnostic value-add). Sister-project (arthrex/pccp) bit-for-bit identical at v10 — zero regression. Sister script reverted; upstream push deferred to after Phase 4. **Mid-task refinement (worth surfacing for Phase 3):** the PDLC_DEMO `user_needs` override was masking a *multi-match ambiguity*, not a *missing-pattern* gap as task 050's wrap-up framed it. The two cases need different Phase 3 fixes: `user_needs` needs an exact-match `user-needs.md` pattern at top rank (to outrank the broad `*user-needs*.md`); `software_requirements` needs a lowercase-hyphen variant alongside the Title-Case patterns. Next session resumes from Phase 3. |
| 2026-06-08 | Ben (with Claude) | 2026-06-08: Confirmed Complete via task-doc audit — dhf-manifest v12 (canonical_role/frontmatter_winner); hitachi PR #161; index was stale. Filed under Completed in 000-index.md. |

