# 121 — Workbench Validation: GxP Verdict Model and Capability/Deployment Test Split

**ID**: 121
**Created**: 2026-09-08
**Status**: Complete
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: High

---

## PERMANENT RULES (do not remove)

This task document is the **session-recovery point** for this work. If the current session drops, is compacted, or ends, the next session must be able to load **this file alone** and continue where we left off.

1. **Update at every meaningful checkpoint (HARD RULE).** Tick the Todo, add a dated Changelog line naming the concrete artifact, refresh progress and the matching `## Findings — the honest red report (2026-09-08)

All nine failing needs are genuine. None is a labelling artefact.

| Need | Why it fails | Kind | Close by |
|---|---|---|---|
| WUN-01 form structure | TC-28: 195 of 241 DHF documents are missing sections of their governing QMS template (order fine); 43 declare no parent template | **Deployment content finding** | DHF authors: align documents to templates (or record template deviations); 43 docs need a `Parent QMS template` reference |
| WUN-02 / WUN-14 provenance | TC-30: 198 documents whose frontmatter says an AI produced them carry no `AI-CHANGELOG` block; 3 system SADs name a product in content | **Deployment content finding** | Backfill provenance blocks (docflow/medtech-docs can script it); neutralise the 3 vendor mentions |
| WUN-03 / WUN-20 transmit gate | TC-25: qsub cover letter carries 2 unresolved `[VERIFY]` tags (lines 18, 44) — caught by the new S7 check | **Deployment content finding** | RA lead resolves the two tags |
| WUN-21 harvest | TC-36: 22 malformed strategy/lessons tags across task docs (15 unclosed comments in one task, 5 prose-on-line, 1 marker text, 1 unknown domain) | **Deployment content finding** | Fix the tags; re-harvest |
| WUN-29 frozen documents | TC-39: `pre_tool_use_frozen.py` is a stub that exits 0 — the deny test fails by design | **Capability gap (build)** | Implement the hook in change-control; the test already exists |
| WUN-05 citation truth | TC-PROTO-CITATIONS not executed | **Protocol to execute** | Operator runs the 16-item protocol (3 runs) and records the result |
| WUN-25 grounding | TC-PROTO-GROUNDING not executed (scripted half TC-41/42 PASS) | **Protocol to execute** | Operator runs the 6-question protocol (3 runs) and records the result |

Not applicable here by declaration: WUN-16 live MCP round trip (no Confluence/Jira connection). Side findings surfaced while building: 4 real citation defects found composing the challenge set (IEC 62304 §4.3 mislabeled, 21 CFR 820.30(b) stale, ISO 13485 §7.3.2 registry gap, IEC 62366-1 §5.9 absent); the submissions checker's transmitted-document parser only sees numbered attachment rows (the project's bulleted list is invisible to S1/S3/S5/S7); docflow's `validate_phase7.py --self-test` skips on a hard-coded path from another project; the 510k package exits 2 (no cover-letter.md — eStAR shape) so it has no deployment case yet.

<!-- LESSONS LEARNED: validation, process -->
- **The labels were hiding real defects.** Retiring PROCESS-CONTROL/EXPLORATORY and building the checks produced seven substantive project findings in one afternoon (template drift in 195 documents, 198 missing provenance blocks, two unverified regulatory claims in a cover letter, 22 harvest-invisible tags). Every one of them had been "assured by process" in the previous report.
- **Capability/deployment scope is what makes a red report bearable.** The tools themselves pass (32/43, every capability case green except the deliberately failing freeze-hook test); the red is this instance's content and two unexecuted protocols. Without the split the report would read as "the workbench is broken"; with it, it reads as a build list with owners.

## Economics` entry in the same edit.
2. **Phase-end batching is OK; drift-batching is not.**
3. **A commit is not a substitute.**
4. **Resume-ready before any session boundary.**
5. **Capture strategy + lessons as they happen.**
6. **Estimation provenance.** `## Economics` follows `.claude/skills/usage-metrics/references/effort-estimation-rubric.md`.

**Resume command**: `bash .claude/hooks/task-activate.sh add <SESSION_ID> ben/121`

## Goals

Follow-on to ben/119 and ben/120, from the user's challenge on 2026-09-08: *in a traditional GxP validation every need is pass or fail; PROCESS-CONTROL and EXPLORATORY are not verdicts.* Agreed — they were evidence methods standing in for verdicts, i.e. untested needs dressed up.

1. **Verdict model.** Verdicts become **PASS / FAIL / NOT-APPLICABLE** only. A need with no executed evidence is **FAIL (no evidence)**. The method (scripted / protocol / inspection) is an attribute of the test case, never a verdict. Non-determinism moves to a limitations statement.
2. **Capability vs deployment scope (user's design point).** Every test case declares `scope: capability | deployment`. *Capability* cases ship with the skill and run against skill-owned fixtures — portable to any project. *Deployment* cases run the deployed workbench against this instance's content (its QMS forms, taxonomy, submission packages, corpus, Jira…) and are the part a customer authors for their instance from the skill's guidance and templates. A `deployment:` declaration in the manifest states what this instance has; a deployment case whose `requires_deployment` is absent is **NOT-APPLICABLE with justification**, never a silent skip.
3. **Protocols for judgment needs.** Where the outcome is the assistant's judgment (citation truth, grounding, harvest), the case is a `protocol` with acceptance criteria and an execution record; unexecuted → FAIL (not executed).
4. **Build the tests.** For every need that hid behind the two labels, build the deterministic checker where the design is clear (form conformance, AI-changelog, VERIFY/transmit gate negative fixture, audit trail, pack validation, claim lint, harvest tag scanner, session hooks, cost attribution, grounding scan, frozen-document hook) and author protocols where it is not.
5. **Run and report red honestly**, with the build list attached.

## Schema (manifest 2.0, workbench-validation 6)

```yaml
deployment:                     # what THIS instance has — drives NOT-APPLICABLE
  connections: {jira: none, confluence: none, browser: none}
  content:
    qms_forms: true             # docs/internal/source-md Forms present
    taxonomy: true              # .taxonomy.yml with governing_qms mappings
    submission_package: true    # docs/project/submissions/<filing>/
    knowledge_packs: false
    commercial_corpus: true
    jira_mirror: false
    controlled_mirror: true     # Confluence-mirror tree under docs/
test_cases:
  - id: TC-xx
    scope: capability | deployment
    method: scripted | protocol | inspection
    requires_deployment: [content.qms_forms]   # optional; any missing → NOT-APPLICABLE
    endpoint: none | mocked | live
    cmd: [...]                                  # scripted
    protocol: docs/project/workbench-validation/protocols/TC-xx.md   # protocol/inspection
    # protocol result recorded at tools/workbench-validation/protocols/TC-xx.result.yml
```

Need verdict: applicable cases (not N/A) must all be PASS → PASS; any FAIL/ERROR/NOT-EXECUTED → FAIL; no applicable cases → FAIL (no evidence). Overall: FAIL if any need FAIL. `coverage:` on needs is retired.

## Todos

- [x] Task 121 created; schema decided (this section)
- [x] workbench-validation 6: runner (scope/method/requires_deployment/protocol records/NOT-EXECUTED), renderer (binary verdicts + reasons, grouping by scope, deployment declaration, findings list, limitations §), templates (manifest, protocol.md, protocol-result.yml), SKILL/README, 25-case suite green
- [x] Checkers built (4 forks): medtech-docs 36 `form_conformance_check.py` + `ai_changelog_check.py` (22 fixture tests); submissions 11 (new S7 unresolved-[VERIFY] gate check + fixture package, 7 tests); commercial 18 claim-gate tests (4); knowledge-pack-export 6 (4); docflow 37 fidelity tests (7); strategy 21 `scan_tags.py` (4) + lessons 5 pointer; secops 10 session-hook tests (3); task 36 checkpoint-recover tests (3); usage-metrics 13 aggregate tests (3); advisors 13 `grounding_scan.py` (4); change-control 0.14.2 `test_frozen_hook.py` (expected FAIL, `freeze_gate` marker); three written protocols (citations 16-item challenge set, grounding 6 questions, live MCP 7 steps) + templates
- [x] Manifest 2.0: `deployment:` declaration (connections + 12 content keys), 43 cases all scoped/methoded, every one of 29 needs mapped; `coverage:` retired; plan §4 regenerated, §5 rewritten; protocols/ folder + records folder READMEs
- [x] Debug run `run-20260908T195841Z`: **FAIL** — 32/43 PASS · 5 FAIL · 2 NOT-EXECUTED · 4 NOT-APPLICABLE; needs 19 PASS / 9 FAIL / 1 N/A (see Findings)
- [x] Commits `bfc70e0` (model + checks) · `cc5fcd0` (run of record, red) · merge `07c8fcc` → PR #190 merged (`2ce5cc3`); hitachi sync branch +`b88427f` (PR #301 now 3 commits, awaiting review)

## Economics

```json
{
  "economics": {
    "method_version": 1,
    "method_ref": ".claude/skills/usage-metrics/references/effort-estimation-rubric.md",
    "agentic_hours": null,
    "todos": [
      {"id": "model", "title": "Verdict model redesign: runner/renderer/templates/tests to schema 2.0, plan §5, console", "hours_low": 8, "hours_high": 14, "persona": "senior-engineer"},
      {"id": "checkers", "title": "Twelve skills: new checkers/fixtures/protocols with docs and versions (4 parallel builds)", "hours_low": 30, "hours_high": 50, "persona": "senior-engineer"},
      {"id": "integration", "title": "Manifest 2.0 integration of 19 new cases, deployment declaration, red-run triage and findings table", "hours_low": 4, "hours_high": 7, "persona": "quality-engineer"}
    ]
  }
}
```

## Changelog

- 2026-09-08: Task created from the user's GxP challenge; verdict model + capability/deployment split decided; schema 2.0 drafted; four build forks launched.
- 2026-09-08: Verdict model implemented (workbench-validation 6, schema 2.0, 25 tests); 19 new cases from four forks integrated (43 total, 29 needs all mapped); plan §4/§5, protocols folder + records folder; console 1.67.2. Debug run FAIL 32/43 — nine failing needs, all genuine (table above). Next: commit, run of record (red), PR, registry sync.
- 2026-09-08: Landed via PR #190 (`2ce5cc3`) with the honest red run of record `run-20260908T200255Z`; registry sync branch updated (`b88427f`). Task Complete — its deliverable was the model, the checks and the truthful report. Open follow-ups are the build list in Findings, each with an owner.

## Resume / follow-up

Everything is on `main`. The red is the true state; closing it is content and build work, not validation work:
1. **Content owners** — DHF authors: align 195 documents to their governing templates (or record deviations) and add a parent-template reference to the 43 without one (`form_conformance_check.py --json docs/project/dhfs` lists them); backfill the AI-CHANGELOG block on 198 AI-authored documents and neutralise 3 vendor mentions (`ai_changelog_check.py`); RA lead: resolve the 2 `[VERIFY]` tags in `docs/project/submissions/qsub/cover-letter.md` (lines 18, 44); task owners: fix 22 malformed harvest tags (`scan_tags.py --json`).
2. **Build** — implement `change-control/hooks/pre_tool_use_frozen.py` (TC-39 already asserts the deny); give the submissions checker a parser for bulleted attachment lists and a 510k (eStAR) entry point; docflow `validate_phase7.py --self-test` should not depend on a foreign path.
3. **Execute protocols** — run `protocols/TC-PROTO-CITATIONS.md` and `TC-PROTO-GROUNDING.md` (3 runs each, pinned model), write `tools/workbench-validation/protocols/<TC>.result.yml`, re-run `/workbench-validation validate --model-id <model>`.
4. **Registry** — merge hitachi #301, then `/sync-skills pull`; port the project-console Settings → Validation changes (1.64.0 → 1.67.2) to the registry fork by hand.
5. Also found while building: 4 real citation defects listed in `TC-PROTO-CITATIONS.md` (IEC 62304 §4.3 mislabeled, 21 CFR 820.30(b) stale, ISO 13485 §7.3.2 registry gap, IEC 62366-1 §5.9 absent) — route to the reference-audit owner.
Reactivate with `bash .claude/hooks/task-activate.sh add <SESSION_ID> ben/121` only if these follow-ups are worked under this task rather than their owners' tasks.
