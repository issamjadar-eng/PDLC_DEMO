# 123 — Workbench Validation: Defect Correction and QMS Template Coverage

**ID**: 123
**Created**: 2026-09-08
**Status**: Complete
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: High

---

## PERMANENT RULES (do not remove)

This task document is the **session-recovery point** for this work. If the current session drops, is compacted, or ends, the next session must be able to load **this file alone** and continue where we left off.

1. **Update at every meaningful checkpoint (HARD RULE).** Tick the Todo, add a dated Changelog line naming the concrete artifact, refresh progress and the matching `## Economics` entry in the same edit.
2. **Phase-end batching is OK; drift-batching is not.**
3. **A commit is not a substitute.**
4. **Resume-ready before any session boundary.**
5. **Capture strategy + lessons as they happen.**
6. **Estimation provenance.** `## Economics` follows `.claude/skills/usage-metrics/references/effort-estimation-rubric.md`.

**Resume command**: `bash .claude/hooks/task-activate.sh add <SESSION_ID> ben/123`

## Goals

Follow-on to ben/121 (honest red report). Two asks from the user on 2026-09-08:

1. **Sync everything** — registry PR hitachi #301 merged (`fc38555`), hitachi main fast-forwarded, local `main` brought current around another live session's uncommitted work (stashed → pulled → popped; three conflicts resolved preserving its newer edits).
2. **Correct the defects** behind the nine failing needs, and — the design point — make validation **QMS-import aware**: a project acquires QMS templates/forms over time, so the validation must (a) validate what has been imported, and (b) for project-content tests, show **which imported QMS templates/forms have validation evidence and which do not**, plus which project doctypes have **no template imported at all**.

<!-- STRATEGY CONTENT: testing, tool-validation, qms-coverage, deployment-tests -->

### D1 — QMS template coverage is a first-class, always-current inventory

**Decision.** A deployment-scope inventory (`qms_coverage`) is derived at every validation run from the imported QMS registry (`docs/internal/source-md/qms-index.md` + document frontmatter) joined with the form-conformance results: for every imported template/form — how many project documents instantiate it, whether the conformance check exercised it (tested / untested), and its pass/fail state; for every project document — which template governs it, or **"no template imported for this doctype"**. Templates imported but unused are listed as *unvalidated by project content*; project doctypes without a template are listed as *QMS gap*. The inventory renders as a report section, a sidecar block and a console panel, and is asserted by a scripted deployment case (the inventory must generate and every instantiated template must have been exercised).

**Why.** Validation of a deployed workbench is only as complete as the QMS content it was run against. When a customer imports a new template next quarter, the question "is anything using it, and is it tested?" must answer itself from the record — not from someone remembering to add a test.

**What it commits us to.** The form-conformance checker resolves only true templates/forms (doc_type TMP/FORM) as structural governors — an SOP or WI reference is "governed by procedure, no template structure" (informational). Documents get a *Parent QMS template* frontmatter reference where a template exists; where none exists, the gap is recorded, not papered over.

## Todos

- [x] Sync: hitachi #301 merged (`fc38555`), hitachi main ff, local main current (other session's WIP preserved)
- [x] Checker precision (medtech-docs 37): SOP/WI/STD references → `procedure` (informational); per-doc `template_id` + `resolved_via`
- [x] Form-conformance fixer applied: fail 195 → **0** (warn 177 = extras appended; procedure 30; no-form 43 → 34); 165 restructured, 9 newly mapped (CEP-* → GL-TMP-UC-004, CAPA → GL-FORM-QM-001, design-inputs → GL-TMP-DC-002). **34 QMS gaps — no template imported** for: architecture/SAD, benefit-risk analysis, complaints ledger, literature-search strategy, PMCF plan, PMCF study, software requirements, user needs, trace matrix, V&V testing strategy (+ `risk-strategy.md` judgement). **Regression found by two advisor reviews and corrected (medtech-docs 38):** appended legacy sections had kept their numbering → 139 docs with restarted numbers → **0**; retained extras now live under one `## Appendix — Sections retained from the previous structure` (67 sections in 13 docs), 380 empty template skeletons dropped (1096 placeholder lines, 0 prose), re-headed sections 302, idempotent second run; conformance now pass 152 / warn 25 / fail 0
- [x] AI-changelog backfill: fail 198 → **0** (195 blocks added; 3 vendor mentions in `*-system-sad.md` changelog tables → "AI assistant")
- [x] QMS coverage inventory (`qms_coverage.py`, exit 0 here): 27 templates/forms imported — 19 instantiated & tested, 0 failing, **8 unused** (GL-FORM-DC-002, QM-002…005, RA-001, SP-001, SP-002); 45 procedures (30 docs governed by procedure); 241 docs — 177 template-governed, 34 without template. Rendered in report §3, sidecar, console; WUN-30 + TC-43
- [x] Submissions 12: `strip_zones` recognises `🔒 INTERNAL` blockquote containers; cover-letter § 5 rewritten (open item moved to the INTERNAL container as a managed TBD, owner RA lead) + AI-CHANGELOG row; bulleted attachment lists parsed (5 transmitted docs now, was 1); eSTAR-shaped folder → clear precondition + TC-44 (N/A until an eSTAR crosswalk exists; `content.estar_crosswalk_510k: false`). **New real findings:** 8 unresolved `[VERIFY]` in filed bodies the gate never scanned before — `device-description.md` 28/44/56, `intended-use.md` 19/23/35, `pccp-summary.md` 29/49 — regulatory judgments (pediatric weight floor vs predicate IFU, precedent K-numbers, documentation level per the software-functions guidance, contraindications per predicate labeling); verifiable ones to be checked against project sources, the rest stay open with owner RA lead
- [x] docflow 38: `validate_phase7.py --self-test` runs 11 inline assertions (no foreign path), exit 1 on mismatch
- [x] 22 malformed harvest tags → 0 (`scan_tags.py`: 226 well-formed): ben/054 15 unclosed comments (content had been hidden from render and harvest), ben/053 5 prose-on-line (+ `branding` → `commercial, branding`), ben/080 marker text, ben/114 unknown domain; changelog lines added
- [x] Frozen-document hook implemented (change-control 0.15.0): denies Edit/Write/NotebookEdit/MultiEdit on `state: frozen|released` markdown with a briefing, fails open on bad payloads; registered via `register-hook.sh` as `.claude/hooks/change-control-frozen.py` in `.claude/settings.json`; `freeze_gate` tests 2/2 PASS
- [x] Protocols executed by the main session (forks cannot spawn the agents under test):
  - **TC-PROTO-CITATIONS: v1 → FAIL (3 runs), then v2 → PASS (3 runs)**. v1 failed for two reasons that were themselves findings: the citations agent's verdict band for the same evidence varied across runs (paywalled-standard cap applied inconsistently), and four answer-key entries were wrong (item 8 was a genuinely broken tracker link; item 7 a heading that exists only in finding aids; items 9/12 contradicted by L1a evidence). Corrected at the source: reference-audit 6 deterministic band rule (`sound-by-distillation`, quarantine → `ambiguous-source`), L1b `iec-62366-1.md` quarantine banner, qsub aid headings relabelled, ISO 13485 gap stated, tracker link fixed; protocol v2 with corrected key + new criterion D (band identical across runs). v2: 48/48 bands identical, all criteria met. Records: `TC-PROTO-CITATIONS.result.yml` (v2 PASS) with `TC-PROTO-CITATIONS.v1.result.yml` retained.
  - **TC-PROTO-GROUNDING: PASS (3 runs × 6 advisors)**. P3 0 non-canonical citations (decoy articles present, never cited), P2 0 fabricated paths (3 scorer false positives adjudicated), P1 all, P4 6/6, 5/6, 5/6 (q3's must-cite does not exist in this deployment — scored against the governing template; deviation recorded for protocol v2). Advisors surfaced six further real project findings (product code LZG/LZH vs MEA; no SE comparison; repealed 820.30(b) inherited from SOP/template; no software verification protocols; §5.9 vs §5.6 usability clause; no RMP in any DHF) — recorded in the execution record for their owners.
- [x] Runner defect found by the first real execution record and fixed (workbench-validation 7): YAML bare-date `executed:` broke the JSON write; values now normalised; regression test added (27 tests)
- [x] Run of record `run-20260909T000311Z` on a clean worktree at `1abb544`: **PASS — 40/45, 0 FAIL, 5 NOT-APPLICABLE, 0 NOT-EXECUTED; needs 29 PASS / 1 N/A**, model captured, no warnings. Commits `1abb544` (corrections) · `aad5196` (run of record) → PR #193 merged (`336c5cf`). Registry: hitachi PR #302 (`87eeb97`, 39 files, PR-only)

## Economics

```json
{
  "economics": {
    "method_version": 1,
    "method_ref": ".claude/skills/usage-metrics/references/effort-estimation-rubric.md",
    "agentic_hours": null,
    "todos": [
      {"id": "sync", "title": "Registry merge + local main sync around a concurrent session (stash/pull/pop with three hand-resolved conflicts)", "hours_low": 1, "hours_high": 2, "persona": "senior-engineer"},
      {"id": "content", "title": "195 DHF documents restructured to template (fixer + regression correction), 198 provenance blocks, 9 template mappings, 34 QMS gaps recorded", "hours_low": 40, "hours_high": 80, "persona": "quality-engineer"},
      {"id": "coverage", "title": "QMS template coverage inventory (script, report/sidecar/console, need + case)", "hours_low": 6, "hours_high": 10, "persona": "senior-engineer"},
      {"id": "gates", "title": "Submissions gate widening + 8 VERIFY adjudications applied; freeze hook implemented + registered; 22 tag repairs; docflow self-test", "hours_low": 10, "hours_high": 16, "persona": "regulatory-affairs"},
      {"id": "protocols", "title": "Two protocols executed for real (6 batch runs + 18 advisor calls), v1 FAIL adjudicated, tool + registry + protocol v2 corrections, v2 re-executed, records written", "hours_low": 16, "hours_high": 28, "persona": "quality-engineer"}
    ]
  }
}
```

## Changelog

- 2026-09-08: Task created. Sync done (hitachi #301 → `fc38555`; local main e01c4a1 with the other session's WIP preserved through a stash/pull/pop and three hand-resolved conflicts). D1 recorded (QMS template coverage inventory). Correction forks launched.
- 2026-09-08: workbench-validation 7 — `qms_coverage:` manifest key, renderer §3 coverage section (templates × instances × evidence × status; procedures; doctypes with no template), sidecar block, console panel (1.67.3); WUN-30 + TC-43 added (30 needs / 44 cases). Five correction forks running (medtech-docs structure+provenance+inventory; submissions+docflow; tags+frozen hook; two protocol executions).
- 2026-09-08: Forks landed: tags 22→0; freeze hook enforcing (0.15.0, registered); submissions 12 (blockquote INTERNAL, bulleted attachments, eSTAR precondition + TC-44, § 5 resolved) — widening the gate surfaced 8 more real `[VERIFY]` tags in qsub attachments; docflow 38 self-test real. Protocol forks correctly declined (a fork cannot spawn the agents under test); the main session is executing both protocols directly (3 citations batch runs + 18 advisor calls; concurrency cap 20 reached once). medtech-docs fork (structure fix, provenance backfill, QMS coverage) still running.
- 2026-09-08 (later): medtech-docs fork landed (structure 195→0, provenance 198→0, coverage inventory exit 0, 34 QMS gaps named); citations protocol executed 3× → FAIL with tool-repeatability + answer-key findings, record written; grounding runs 1–2 captured; correction forks running (fixer numbering regression; citations band determinism + registry + tracker link + protocol v2); RA adjudication of the 8 `[VERIFY]` tags running.
- 2026-09-08 (later): RA adjudication of the 8 `[VERIFY]` tags applied to `device-description.md`, `intended-use.md`, `pccp-summary.md` (+ 510(k) manifest § 3.1 names all three PCCP families); AI-CHANGELOG rows added; **transmit gate on qsub now exit 0, 0 findings**. Notable: the "no new contraindications" claim was contradicted by the project's own predicate record (paralytic ileus added; pediatric exclusion relaxed) and is now stated truthfully; pediatric floor stated (≥6 y/≥20 kg vs predicate ≥8 y/≥25 kg); no PCCP precedent K-numbers exist in project sources — reference replaced by that statement. Citations/registry fork landed: deterministic band rule in reference-audit (6), L1b `iec-62366-1.md` quarantine banner + `[VERIFY]` clause labels, qsub aid headings relabelled to source-md sections, ISO 13485 gap stated in both tier READMEs, tracker link fixed + dashboard re-rendered, protocol TC-PROTO-CITATIONS **v2** (corrected answer key, new cross-run consistency criterion D). Grounding runs 1–2 scored: P3 0 violations, P1 all, P4 11/12 (q3 deviation), three scorer false positives adjudicated.
- 2026-09-08 (rate limit): session limit hit mid-flight — killed the fixer-numbering fork (partial rework on disk, syntax ok, not applied), citations v2 runs 1–3, and grounding run 3 q2/q5/q6. Run 3 q1/q3/q4 completed and captured. After reset: all seven relaunched (fixer fork resumes from the partial file; citations v2 ×3; grounding q2/q5/q6).
- 2026-09-08 (later): fixer numbering correction applied (139 → 0 restarts; 174 docs reshaped; provenance rows added per the one-row-per-pass rule). Waiting on citations v2 ×3 and grounding run 3 q2/q6.
- 2026-09-09: All correction work landed on disk. Citations v2 3× PASS (bands identical); grounding 3× PASS; runner date-serialisation defect fixed; full debug run **PASS 40/45 + 5 N/A, 0 FAIL**, needs 29/30 PASS + 1 N/A. Landing now.
- 2026-09-09: **Landed.** PR #193 merged (`336c5cf`) with the run of record PASS 40/45; registry PR hitachi #302 open (39 files). Task Complete.

## Resume / follow-up

Everything is on `main` (origin). Open items, each with an owner, are carried in `tools/workbench-validation/protocols/TC-PROTO-GROUNDING.result.yml` (`findings_surfaced_by_advisors`) and the report's known anomalies:
1. **RA lead** — product code (LZG/LZH vs MEA) across manifest and device records; SE comparison table (OBL-510K-001); the four managed TBDs in the qsub INTERNAL containers; `regulatory-strategy.md` L62 demo-K-number wording; precedent PCCP research.
2. **Quality Engineering** — QMS remediation backlog: repealed 21 CFR 820.30(b) in GL-SOP-DC-002 / GL-TMP-DC-001 and ~15 sibling QMS documents (program rule of 2026-07-14); GL-TMP-RM-001 §3 scales vs GL-STD-RM-001; no Risk Management Plan in any DHF; IEC 62366-1 clause (§5.9 vs §5.6) confirmed against the licensed standard, then rebuild `docs/external/standards/iec-62366-1.md` and `OBL-62366-008`.
3. **V&V lead** — no software verification protocols (28/32 SRS rows untraced; hazard analysis cites non-existent protocol IDs; ID scheme `VER-PP3500-*` vs `GL-VER-*`); URRA before the summative protocol.
4. **Registry owners** — merge hitachi #302 then `/sync-skills pull`; import the QMS templates for the 34 template-less doctypes (architecture/SAD, benefit-risk, complaints ledger, literature search, PMCF plan/study, software requirements, user needs, trace matrix, V&V strategy) or record them as intentionally template-free; port project-console 1.64.0 → 1.67.3 Settings → Validation changes to the registry fork by hand.
5. **Validation** — protocol v2 for TC-PROTO-GROUNDING (q3 must-cite → governing template); sign-off of the three execution records by BX; re-run `/workbench-validation validate --model-id <model>` after any skill change (the console flags named differences).
6. **Local checkout note** — the local `main` of the shared clone is behind origin because another live session holds uncommitted work (task 122 multimodel) that collides with its own merged copy; that session should reconcile and pull. Nothing of this task depends on it.
Reactivate with `bash .claude/hooks/task-activate.sh add <SESSION_ID> ben/123` only if these follow-ups are worked under this task.
