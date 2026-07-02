# 089 — Submission Reference + QMS Backlog (B1–B4 from ben/088 verification)

**ID**: 089
**Created**: 2026-06-15
**Status**: Complete
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: Medium

---

## PERMANENT RULES (do not remove)

This task document is the **session-recovery point** for this work. Keep it current in-flight.

1. **Update at every meaningful checkpoint (HARD RULE).** Tick todos, add dated changelog lines naming concrete artifacts, update counts.
2. **Phase-end batching is OK; drift-batching is not.**
3. **A commit is not a substitute** for the task-doc narrative.
4. **Resume-ready before any session boundary.**
5. **Capture strategy + lessons as they happen.**

## Goals

Close the four follow-up gaps surfaced by ben/088's two-agent verification of the new submission templates. These are **references + QMS authoring**, not submissions-skill work (which shipped in PR #59).

- **B1 — 21 CFR Part 814 reference distillation.** No PMA regulation distillation exists (`.claude/skills/medtech-docs/references/regulations/` holds 807, 880, 892, 45-164 only). The PMA templates' `814.20(b)(...)` citations are therefore **unverified against project grounding**. Author `references/regulations/21-cfr-part-814.md` (mirror the 807 distillation's shape) so the PMA profile is grounded before any build-out.
- **B2 — `GL-FORM-RA-001`.** QMS has no Form for submission package assembly (only SOP `GL-SOP-RA-001` + WI `GL-WI-RA-001`). Author a representative **Submission Package Assembly & Sign-off Record** form under `docs/internal/source-md/regulatory-affairs/`, register it (qms-index + README), and note the composition-manifest → form mapping.
- **B3 — `GL-WI-RA-003`.** PMA has no governing QMS doc (`GL-WI-RA-001` §2 defers PMA to a future WI). Author a representative PMA-pathway Work Instruction, mirroring `GL-WI-RA-001`'s shape; register it.
- **B4 — Pin §807.87 subsection letters.** `references/regulations/21-cfr-part-807.md` lists the §807.87 required-content elements as **unlettered bullets** — the ambiguity that let the `807.87(k)` vs `(l)` slip into the templates. Pin the authoritative subsection letters.

## Grounding rules

- **B1 / B4 are regulatory distillations** — ground in the authoritative regulation text (eCFR Title 21 Part 814 / §807.87), never fabricate. Mirror the existing `references/regulations/*.md` distillation shape + verification-checks convention. These are **project-agnostic registry** content (medtech-docs skill).
- **B2 / B3 are representative demo QMS docs** — the project's QMS (ben/022) is a representative GlobalLogic QMS. Mirror existing QMS doc shapes (`GL-WI-RA-001`, `capa-form.md`, existing `GL-FORM-*`). Carry docflow frontmatter + standards anchors + `_Demo_` banner; register in `qms-index.md` + `regulatory-affairs/README.md`.

## Todos

- [x] B4 — fetched §807.87 lettering via eCFR API; pinned (a)–(m) table in `21-cfr-part-807.md` + citation-discipline note ((k)=Class III cert, (l)=T&A); source-provenance re-verify note
- [x] B1 — authored `references/regulations/21-cfr-part-814.md` (PMA) grounded in eCFR §814.20 (a)–(e), (b)(1)–(13), (b)(3)(i)–(vi); §814.39/814.44/Subparts E&H summarized w/ [VERIFY]; added to regulations README index + changelog
- [x] B2 — authored `GL-FORM-RA-001` (Submission Package Assembly & Sign-off Record) at `regulatory-affairs/templates/` (+ new templates/README); registered in qms-index + RA README; noted manifest→form taxonomy mapping
- [x] B3 — authored `GL-WI-RA-003` (PMA WI) at `regulatory-affairs/` mirroring GL-WI-RA-001; registered in qms-index + RA README
- [x] Re-verified PMA template `814.20(b)(...)` citations against B1 — fixed two stubs: device-description `(b)(3)`→`(b)(4)` (complete description); manufacturing `(b)(4)(v)`→`(b)(4)` (eCFR shows no (b)(4)(v) sub-item)
- [x] qms-index counts updated (WI 11→12, Forms 10→11, Total 67→69) + rev 1.2 row
- [x] Verify + push — PR #60 merged to `main` (`8a48b1d`); branch deleted. Status → Complete.

## Open Questions

- B2 "taxonomy-map the manifest": the submissions composition-manifest is a working markdown, not (yet) under a `.taxonomy.yml`-governed mirror folder. Author the form + register it now; the `governing_qms` taxonomy mapping applies when/if the submissions folder gets a taxonomy. Confirm scope.
- Web/eCFR access from this environment — if unavailable, fall back to the in-repo grounding the ben/088 reg-affairs agent already eCFR-verified (807.87 letters: (e) labeling · (h) 510(k) summary/statement · (i) financial cert · (k) Class III cert · (l) truthful-&-accuracy) + the PMA template self-citations, and flag any element not independently confirmed.

## Changelog

- 2026-06-15: Task created — B1–B4 follow-up backlog spun out of ben/088's verification. Scope: references (B1/B4, project-agnostic) + representative QMS docs (B2/B3).
- 2026-06-15: **All four closed + shipped.** B4 pinned §807.87 (a)–(m) letters (eCFR-verified) in `21-cfr-part-807.md`; B1 authored `21-cfr-part-814.md` PMA distillation (§814.20 verbatim-verified) + regulations README index; re-verified PMA template citations (2 stubs fixed); B3 authored `GL-WI-RA-003` (PMA WI); B2 authored `GL-FORM-RA-001` + `regulatory-affairs/templates/` README; registered both in qms-index (67→69, rev 1.2) + RA README. `render --check` clean; new links resolve. **PR #60 merged to `main` (`8a48b1d`)**, branch deleted. Status → Complete. Residual (out of scope, flagged): a latent `807.87(k)` in a project-console test fixture; De Novo WI `GL-WI-RA-002` still reserved.

