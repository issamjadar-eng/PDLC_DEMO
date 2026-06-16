# 090 — Registry Sync + Drift Reconcile + Post-Reference-Correction Doc Evaluation

**ID**: 090
**Created**: 2026-06-15
**Status**: Complete
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: High

---

## PERMANENT RULES (do not remove)

This task document is the **session-recovery point** for this work. Keep it current in-flight.

1. **Update at every meaningful checkpoint (HARD RULE).** Tick todos, add dated changelog lines naming concrete artifacts, update counts.
2. **Phase-end batching is OK; drift-batching is not.**
3. **A commit is not a substitute** for the task-doc narrative.
4. **Resume-ready before any session boundary.**
5. **Capture strategy + lessons as they happen.**

## Goals

The user's directive (2026-06-15): **before any pushes**, pull and reconcile the skill registry (there are upstream updates), handle the surfaced drifts, then — because the medtech-docs regulatory references were just corrected (ben/089 B1/B4) — **evaluate project documents** for any corrections those reference changes imply. **HARD CONSTRAINT: no pushes until the user explicitly says so.**

Phases:
1. **Sync** — `/sync-skills status` → `check --analyzed` → `pull` (three-way bucketed; LOCAL_AHEAD/BOTH_DIVERGED never auto-applied). Run the mandatory **Project Impact Report** on anything pulled.
2. **Reconcile drifts** — apply the safe upstream pulls; surface our LOCAL_AHEAD work (submissions v2, tracker v14, `21-cfr-part-807.md` edit, new `21-cfr-part-814.md`) as push candidates **held for later**; walk any BOTH_DIVERGED.
3. **Document evaluation** — given the corrected references (§807.87 (a)–(m) lettering; new Part 814 distillation), check project documents (`docs/**`) for citations needing correction — esp. any `807.87(k)` miscitations and PMA-pathway references. Consider `/reference-audit` on affected docs.

## Tracked residuals (carryover from ben/089 — MUST address)

These were flagged out-of-scope in ben/089 PR #60 and are now owned here:

- [ ] **R1 — `807.87(k)` miscite in a project-console test fixture.** `.claude/skills/project-console/tests/test_tracker_workflow_e2e.py:73` has a demo row `"... | 21 CFR 807.87(k) | ..."` for a "Truthful & Accuracy" deliverable — same (k)↔(l) error we fixed in the templates. It's test data, but it perpetuates the wrong citation. Fix to `807.87(l)` (verify the test asserts on the string; update the expected value if so). _Note: project-console is a registry skill — fixing here is a LOCAL_AHEAD change to push later._
- [ ] **R2 — De Novo WI `GL-WI-RA-002` reserved/unauthored.** `GL-WI-RA-001` §2 and `GL-WI-RA-003` §2 both defer De Novo to `GL-WI-RA-002`; the RA README marks it reserved. Author a representative De Novo Submission Process WI (mirror GL-WI-RA-001/003) to complete the RA pathway set. Lower priority than the sync/eval work.

## Todos

- [x] P1 — `/sync-skills status`: project repo was BEHIND 1 (file-locator CI index.db `7e80881`) → ff-pulled, now current. hitachi clone SYNCED (`88e793d`). 137 files drift.
- [x] P1 — `check --analyzed` buckets: **UPSTREAM_ONLY 22 · LOCAL_ONLY 23 · UPSTREAM_NEWER 92** (UPSTREAM_ADVANCE 71 · LOCAL_AHEAD 8 · UNDETERMINED 13).
- [x] P1 — `pull` executed (full reconcile, user-approved): pulled 86, merged 807.md + regs/README, skipped 7 superseded flat templates, held our work. + Project Impact Report done.
- [x] P2 — reconcile/post-update: `file_locator.corpus_excludes: articles/**` + symlinked `.claude/rules/articles-not-canonical.md` (medtech-docs v34). Allowlists already current. `/advisors sync` re-render flagged (not run). sync-log entry written.
- [x] P3 — doc-eval: **project docs clean** vs the v32/v33 reference corrections — no §807.85/§807.100/§807.87(k) miscites in `docs/`; only §807.81(a)(3) (correct). Optional enhancement only: cite §807.81(b) PCCP carve-out in `pccp-summary.md`.

### Sync analysis (2026-06-15) — the registry did a full `medtech-docs/references/` refresh

- **Reference-library refresh (UPSTREAM_ADVANCE, safe pull):** ~71 files — all FDA-guidance distillations (incl. `510k-se`, `510k-estar` that our submission work grounds against) + regs 880/892/164 advanced; advisors skill + 13 advisor agents advanced (1 commit each).
- **New upstream files (UPSTREAM_ONLY, 22):** verbatim eCFR archives `references/regulations/source-md/*.md` + `source/*.xml` (807/880/892/164); the `citations` advisor + 3 `citations-*-researcher` agents (reference-audit tooling — **useful for the doc-eval**); medtech-docs `rules/articles-not-canonical.md`, `templates/readme-articles.md`, `scripts/verify-conversion.py`.
- **⚠️ 7 `submissions/templates/*` UPSTREAM_ONLY = the OLD flat v1 templates we replaced** (cover-letter.md, device-description.md, fda-questions.md, intended-use.md, pccp-summary.md, composition-manifest.template.md, provenance.template.yml at root). **SKIP — do not pull** (would resurrect the old layout). Registry submissions is still v1; our v2 reorg is the divergence.
- **⚠️ 13 UNDETERMINED agents = symlink artifact** (`.claude/agents/*` → `skills/advisors/agents/*`); real content is UPSTREAM_ADVANCE. Pull advisors skill; symlinks need nothing.
- **🔀 `21-cfr-part-807.md` = genuine BOTH_DIVERGED merge.** Upstream advanced it: added a "🔎 finding-aid / cite the verbatim `source-md/` instead" banner + **corrected §807.85 (custom devices/repackagers — our local has the WRONG "veterinary/research" text), §807.81(a)(1), §807.100**. We advanced it with the §807.87 (a)–(m) lettering table (upstream still has unlettered bullets). **Resolve: pull upstream's corrected file, re-apply our §807.87 table on top → merged; push candidate.**
- **🔀 `regulations/README.md` = likely BOTH_DIVERGED** (upstream refresh + our 814 row). Merge: upstream + re-add our 814 row + changelog.
- **Hold for push (our work):** all 23 LOCAL_ONLY (submissions v2 profiled templates, `21-cfr-part-814.md`, `pccp-aiml-full.md`) + the 8 LOCAL_AHEAD (submissions SKILL/README/VERSION/render_sidecars, tracker SKILL/README) — minus the two merge files above.
- **DOC-EVAL PIVOT:** upstream **fixed §807.85 in 807.md** → our local 807.md carries a wrong §807.85; any project doc citing §807.85 may be wrong. Plus the finding-aid pattern says "cite the verbatim `source-md/`, not the distilled file." Both feed P3.
- [ ] P2 — reconcile: project.yml allowlist updates, re-run any skill `setup`, flag template/best-practices impacts from pulled changes
- [ ] P3 — document evaluation: grep/audit `docs/**` for `807.87` miscites + PMA citation needs vs the corrected references; `/reference-audit` on affected docs if warranted
- [x] R1 — fixed `807.87(k)`→`(l)` in `project-console/tests/test_tracker_workflow_e2e.py:73` (verified no assertion depends on PA3's REF — asserts are on PA1 + IDs)
- [x] R2 — authored `GL-WI-RA-002` (De Novo WI) + registered (qms-index WI 12→13, Total 70, rev 1.3; RA README row + removed "reserved" note). RA pathway set now complete: 510(k)+De Novo+PMA.
- [x] Optional PCCP enhancement — added §807.81(b) cleared-PCCP carve-out citation (FD&C §515C/FDORA 2022) to `pccp-summary.md`
- [x] `/advisors sync` — re-rendered grounding; all **unchanged** (pulled advisors already current); project-secops skipped (no frontmatter, expected)
- [x] sync-log written
- [x] Persisted all to PDLC_DEMO — **PR #61 merged** (`e077d73`): 93-file pull + 2 merges + R1/R2/PCCP + project.yml + rule symlink + task docs.
- [x] Registry push (`/sync-skills push`): **hitachi PR #226** (references 814/807-lettering/regs-README + tracker v14 + R1 fixture) + **PR #227** (submissions v1→v2 migration w/ rename-preserving moves + 7 flat-template deletions). Hitachi HEAD `82b867b`.
- [x] `/sync-skills prune` — removed 8 merged `sync/*` branches (0 unmerged).
- [x] Pulled trailing docflow re-advance; **SYNCED** except `pccp-aiml-full.md` (project-local, unverified — left intentionally).
- [x] Final trailing commit (docflow re-advance + sync-log push entry + this doc) → PDLC_DEMO (PR #62, `1186505`).
- [x] Closed the last residual: confirmed `pccp-aiml-full.md` was **deleted upstream** (hitachi `297565c`/PR #218 — superseded by the `source-md/` verbatim tier); deleted our stale local copy → **skill drift now 0, fully synced**.

## Open Questions

- Does upstream also touch `21-cfr-part-807.md` (→ BOTH_DIVERGED with our B4 edit) or the submissions/tracker skills (→ divergence with our v2/v14)? The `check --analyzed` buckets will tell.
- Scope of doc evaluation: full `/reference-audit` of affected docs, or a targeted grep sweep first? Decide after seeing how many docs cite §807.87 / PMA.

## Changelog

- 2026-06-15: **Closed — all changes landed.** Persisted the full sync+reconcile+doc-eval to PDLC_DEMO (PR #61, `e077d73`). Content follow-ups: R1 (807.87(k)→(l) fixture), R2 (GL-WI-RA-002 De Novo WI → RA pathway set complete, qms-index Total 70), PCCP §807.81(b) carve-out citation, `/advisors sync` (no-op). Pushed contributions upstream: hitachi PR #226 (references + tracker v14 + R1) + #227 (submissions v1→v2 migration). Pruned 8 merged sync branches. Registry SYNCED (HEAD `82b867b`) except the one project-local `pccp-aiml-full.md`. Status → Complete (pending the trailing-commit of this doc + docflow re-advance + sync-log).
- 2026-06-15: Task created. Holds (a) the ben/089 residuals R1 (807.87(k) test-fixture miscite) + R2 (De Novo WI), and (b) the sync→reconcile→doc-evaluation workflow the user directed. HARD CONSTRAINT recorded: no pushes until user says.
- 2026-06-15: **Sync + reconcile + doc-eval complete (no pushes).** ff-pulled project repo (CI index.db). `/sync-skills` three-way pull: pulled 86 clean upstream files (full `medtech-docs/references/` refresh — fda-guidance distillations + regs 880/892/164 + new verbatim source-md/source archives; advisors skill + 13 agents; new articles rule/template + verify-conversion script; citations agents); **merged** `21-cfr-part-807.md` (upstream §807.85/§807.100/§807.81 corrections + finding-aid tier ⊕ re-applied our §807.87 (a)–(m) table) and regs `README.md` (⊕ our 814 row); **skipped** 7 superseded flat submissions templates; **held** 23 LOCAL_ONLY + 6 LOCAL_AHEAD for push. Post-update: `articles/**` corpus-exclude + `articles-not-canonical.md` rule symlink (medtech-docs v34). **Doc-eval: project docs clean** — the upstream §807.85/§807.100/§807.87(k) corrections aren't cited anywhere in `docs/` (only §807.81(a)(3), correct); one optional enhancement (cite §807.81(b) PCCP carve-out). sync-log written. **Still held / open:** push of our LOCAL work (awaiting user); `/advisors sync` re-render (recommended); R1 + R2; `/sync-skills prune` (6 stale branches).
