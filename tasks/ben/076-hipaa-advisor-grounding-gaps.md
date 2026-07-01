# 076 — HIPAA Advisor Grounding Gaps (registry descriptions + L1b applicability)

**ID**: 076
**Created**: 2026-06-02
**Status**: Complete
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: High

---

## PERMANENT RULES (do not remove)

This task document is the **session-recovery point**. Keep it current in-flight.
1. Update at every meaningful checkpoint (HARD RULE).
2. Phase-end batching OK; drift-batching not.
3. A commit is not a substitute.
4. Resume-ready before any session boundary.
5. Capture strategy + lessons as they happen.

## Goals

Follow-up to ben/075 (which added the HIPAA + NIST SP 800-66 L1a registry references). An assessment of advisor grounding found the references are *retrievable* (file-locator index rebuilt, registry roles resolve by folder membership, regulatory/clinical/cybersecurity advisors all declare `registry_regulations` + `registry_industry_frameworks` in tier_2) but two gaps weaken "HIPAA against our architecture and requirements":

- **Gap 1 (medium) — stale role descriptions.** `dhf-manifest/data/canonical-roles.yaml` `registry_regulations` description enumerates only "21 CFR parts" (807/880/892/820/803/11/812) — no HIPAA/45 CFR. Advisors triage Tier 2 by reading these descriptions, so a HIPAA question can be steered *away* from the folder that now holds the HIPAA file. `registry_industry_frameworks` similarly omits NIST SP 800-66 (softer — ends "etc."). Fix in the wiring source (`canonical-roles.yaml`), then `/advisors sync` re-renders all grounding blocks. Do NOT hand-edit agent files (auto-generated).
- **Gap 2 (high, for the stated goal) — no L1b applicability layer.** `docs/external/regulations/` doesn't exist (no `hipaa.md`); `docs/external/industry-frameworks/nist-sp-800-66.md` absent. Cite-both Hard Rule (advisors v1.5.0) can't be satisfied, and — more importantly — there's no artifact mapping HIPAA → PP3500 modules/data-flows. Advisors can say *what HIPAA requires* (L1a) but must infer *how the device applies it* rather than retrieve a decided posture.

**Deliverables:**
1. `canonical-roles.yaml`: broaden `registry_regulations` + `registry_industry_frameworks` descriptions (Title 21 + Title 45/HIPAA; add NIST SP 800-66). `/advisors sync` + discovery-index rebuild if needed.
2. `docs/external/regulations/` tier scaffolded (README + `hipaa.md` L1b applicability mapping §164.312 technical safeguards → ePHI-handling modules cloud-suite / connectivity-adapter + SRS security requirements).
3. `docs/external/industry-frameworks/nist-sp-800-66.md` L1b applicability.
4. Sister-project compat (canonical-roles.yaml is registry-shared — must generalize). `/sync-skills push` the canonical-roles.yaml change after user review.

## Grounding established (ben/075 assessment)
- advisors SKILL.md read end-to-end: 3-tier model; registry_* roles = L1a; cite-both Hard Rule; folder+glob resolution for external_data roles.
- canonical-roles.yaml: `registry_regulations` → `folder: .claude/skills/medtech-docs/references/regulations`, `*.md`, `triage_only`. Both new files are members. consumers lists confirm wiring.
- file-locator index.db already contains both files (9 embedded summaries for HIPAA file). CI rebuilt on PR #32 merge.
- discovery index `docs/project/dhf-manifest/pdlc-demo-dhf-discovery.json` lists both registry roles as folder pointers (no filename enumeration → no rebuild strictly needed, but re-run to refresh descriptions).

<!-- STRATEGY CONTENT: regulatory, privacy applicability -->
The L1b HIPAA applicability is the load-bearing artifact for the user's goal: it ties §164.312 technical safeguards (access control, audit, integrity, authentication, transmission security) to the device's ePHI data-flow (PCA pump → connectivity-adapter → cloud-suite). The manufacturer's role is business-associate; the applicability doc must make the BA determination explicit and map each safeguard to a concrete module + SRS requirement so the trace is auditable, not inferred.
<!-- /STRATEGY CONTENT -->

## Todos
- [x] Read dhf-manifest SKILL.md (v14: canonical-roles description edit is append-only/safe, no resolver change; re-render after)
- [x] Read docs/external READMEs (parent + industry-frameworks sibling) per readme-before-write; pulled real SRS security reqs from cloud-suite (P1-P7, SW-001/002/004/005/009/011/012/021/022) + connectivity-adapter (A1/A5/A6, SW-016/017/018/026) — strong §164.312 mapping available, incl. explicit HIPAA 6-yr retention (cloud SW-021) and AES-256-GCM BYOK PHI encryption (SW-009)
- [x] Gap 1: edit canonical-roles.yaml descriptions (registry_regulations now names HIPAA/45 CFR + "consult for HIPAA/ePHI not only 21 CFR"; registry_industry_frameworks names NIST SP 800-66)
- [x] Gap 1: render-grounding --all — 11 advisors updated; HIPAA now in clinical-affairs + cybersecurity + regulatory-affairs Tier 2 grounding (verified grep). **Blocker hit + fixed:** see lessons below.
- [x] Gap 1: dhf-manifest discovery-index rebuilt (10 project + 133 per-dhf; HIPAA-aware registry description now in index)
- [x] Gap 2: docs/external/regulations/README.md + hipaa.md authored (maps §164.312 → cloud SW-001/002/004/005/009/011/012/021/022/023 + CA SW-016/017/018/026; flags 6 [VERIFY]/gaps incl. emergency-access, auto-logoff, pca-device media)
- [x] Gap 2: docs/external/industry-frameworks/nist-sp-800-66.md authored + README row + parent docs/external README subfolder row + changelogs
- [x] Verify: HIPAA in advisor Tier 2 grounding (grep); file-locator rebuilt (5 new) → semantic query "HIPAA safeguards vs our cloud/CA architecture" returns L1a reg + 800-66 + CA SAD + cloud SRS in HIGH-confidence band. End-to-end retrieval proven.
- [x] DECISION (user: cybersecurity only): added L1b `regulations` role to cybersecurity tier_2 + broadened the `regulations` role description (was "21 CFR parts" only → now Title 21 + Title 45/HIPAA) + added cybersecurity to its consumers. Re-rendered; cybersecurity now does full structured cite-both for HIPAA. clinical-affairs left as-is (semantic-search route).
- [x] Gap 3 (folded in): advisors skill conformance — frontmatter added, BP+Changelog → README, VERSION removed, project refs scrubbed, validated
- [x] Pushed both repos. **PDLC_DEMO**: PR #39 merged (`983446f`; main now `a3b79ff` incl. CI index rebuild). **hitachi registry**: PR #194 merged (`cd3f800`) — canonical-roles.yaml + advisors SKILL/README + 11 agents + VERSION deletion. Staged only my files; other agents' work (docs/_analysis, task 077, SECOPS, index.db) untouched. Excluded core-team/design-review panels (pre-existing drift). index.db left to CI. Local main ff-recovered after gh left it stale (see lessons).

## Gap 3 (folded in) — advisors skill conformance to skill-creator conventions

User spotted during review that the advisors skill doesn't conform to skill-creator's structure guidance. Audit (vs conformant task/skill-creator/dhf-manifest/trace-matrix) found:
1. **No YAML frontmatter** — SKILL.md started with a literal `Base directory for this skill: ${CLAUDE_SKILL_DIR}` line; the skill's description showed as that line → effectively undiscoverable by natural language. (CRITICAL)
2. `## Changelog` + `## Best Practices` were in SKILL.md (should be README.md).
3. Changelog entries carried forbidden project refs (`ben/204`, `ben/203`, `ben/193`, `ben/191`, `PR #151`, `task 057/058/059/060`).
4. Used a semver `VERSION` file (1.5.1) instead of integer frontmatter `version`.

Fixes (user: convert-to-integer + fold-into-076):
- Added conformant frontmatter (name/description/version:9/updated) with a real pushy description.
- Replaced SKILL.md BP+Changelog with stubs pointing to README (the task-skill pattern).
- Moved BP table + a scrubbed, project-agnostic changelog into README.md; integer versioning from v9, semver history preserved as labels.
- Scrubbed pre-existing `task 057/191` refs from README Key Decisions too.
- Removed the `VERSION` file (nothing reads it; verified).
- Validated: frontmatter parses (version=9 int, 4 fields); zero project refs remain; best-practices "Skills are versioned" check will now pass (was previously exempted as a no-frontmatter external skill).

<!-- LESSONS LEARNED: git-workflow -->
**`gh pr merge --merge` can leave local `main` stale (and the working tree reverted) when `main` advanced during the task.** Concurrent agents merged PR #38 (ben/078-renumber) into `main` while this task ran. After my PR #39 merged on the remote, `gh pr merge --delete-branch` deleted my local branch and checked out the now-stale local `main` (`fc871e8`) — which reverted my edits in the working tree (advisors SKILL.md lost its frontmatter again, regulations/ vanished). The work was never lost — it was on `origin/main` (`983446f`). **Recovery:** `git fetch`; confirm `git merge-base --is-ancestor HEAD origin/main` (clean-ff safe); discard only the CI-owned `index.db` local change (`git checkout -- tools/file-locator-mcp/index.db`) since it blocked the ff; `git merge --ff-only origin/main`. Other agents' uncommitted files (docs/_analysis, task 077, SECOPS.md) are preserved by ff-only because the incoming commits don't touch them. **How to apply:** after `gh pr merge` prints `! not possible to fast-forward`, don't panic about reverted files — `fetch` + `merge --ff-only origin/main` restores them; never `reset --hard` (it would nuke concurrent agents' uncommitted work).
<!-- /LESSONS LEARNED -->

<!-- LESSONS LEARNED: skill-authoring -->
**A skill with no YAML frontmatter is silently undiscoverable — its description degrades to the first content line.** The advisors SKILL.md had a stray `Base directory for this skill: ${CLAUDE_SKILL_DIR}` as line 1 and no `---` frontmatter, so Claude Code surfaced that literal line as the skill's "description" — meaning the skill could only be reached by typing `/advisors`, never by natural-language triggering. **Why:** the skill loader falls back to leading content when frontmatter/description is absent; `/best-practices` even *exempts* no-frontmatter skills as "external," so the gap passes the audit silently. **How to apply:** when auditing a skill, check `head -1 SKILL.md` for `---`; a skill that starts with anything else (especially an unexpanded `${CLAUDE_SKILL_DIR}`) is missing frontmatter and won't auto-trigger. The conformant pattern: frontmatter first (name/description/version/updated), BP+Changelog as stubs in SKILL.md pointing to README, real BP+Changelog in README, no VERSION file. See [[feedback_skill_version_bestpractices]].
<!-- /LESSONS LEARNED -->

## Open Questions
- Which DHFs actually handle ePHI? Assumed cloud-suite (platform) + connectivity-adapter (telemetry path); pca-device firmware may log ePHI locally (§164.310(d) device/media). Confirm against architecture during Gap 2.

<!-- LESSONS LEARNED: tooling, environment -->
**`core.symlinks=false` in a local clone silently breaks `render-grounding.py` and advisor subagent invocation.** This macOS clone had `git config core.symlinks=false`, so all 15 `.claude/agents/*.md` (and 6 more under `.claude/{commands,hooks,rules}/`) were checked out as 47-byte regular files containing the symlink target path instead of real symlinks. Symptom: `render-grounding.py --all` skipped every agent with "agent file must start with YAML frontmatter" (it was reading the path string, not the agent). The git blobs are correct (mode 120000) — it's purely a local-config issue, harmless to the repo but breaking in this working tree (advisors can't be rendered, and CC subagent discovery would read 47 bytes instead of the persona). **Fix:** `git config core.symlinks true` → `rm` the affected files → `git checkout -- <paths>` to re-materialize as real symlinks (content matches blob, so this reverts nothing). This is exactly the ben/066 Windows trap; G3 (the rule documenting it) was deferred — this is a second sighting on macOS, arguing G3 is worth writing. **How to apply:** when a symlink-installed skill artifact behaves as if empty/unparseable, check `ls -la` for `lrwxr-xr-x` vs `-rw-`; if regular, the clone has `core.symlinks=false` — heal it before debugging the tool.
<!-- /LESSONS LEARNED -->

## Changelog
- 2026-06-02: **Status → Complete.** Both HIPAA grounding gaps + advisors skill conformance shipped to both repos (PDLC_DEMO PR #39 `983446f`; hitachi PR #194 `cd3f800`). Local main ff-recovered after the cross-agent merge race. The 6 `[VERIFY]` items in `docs/external/regulations/hipaa.md` (emergency access, auto-logoff, pca-device media controls, HIPAA-framed risk analysis, BAA flow-down, breach procedure) are device-team follow-ups, not blockers for this task.
- 2026-06-02: **Gap 3 (folded in) — advisors skill conformance.** User caught that advisors didn't follow skill-creator conventions. Audited + fixed: added missing YAML frontmatter (the headline — skill had none, so its description was a stray `Base directory` line → undiscoverable), moved BP+Changelog SKILL.md→README.md (stubs left behind), scrubbed all project task refs, dropped the semver VERSION file for integer `version: 9`. Validated frontmatter + zero project refs. Captured the no-frontmatter lesson.
- 2026-06-02: **Gap 2 done + validated end-to-end.** Authored L1b applicability tier: `docs/external/regulations/{README,hipaa}.md` (first regulations L1b in the project) + `docs/external/industry-frameworks/nist-sp-800-66.md`; updated 2 READMEs + parent subfolder table. hipaa.md maps §164.312 to real SRS IDs and flags 6 gaps/[VERIFY]. Rebuilt discovery-index + file-locator index. **Validation:** file-locator query for HIPAA-vs-architecture returns L1a reg + 800-66 + connectivity-adapter SAD + cloud-suite SRS in the high-confidence band — proves a HIPAA question now retrieves regulation + guide + architecture + requirements together. Discovered a pre-existing `docs/_analysis/pca-device/hipaa-readiness-profile.md` (gap-analysis) — complementary to the new applicability doc. Residual: only regulatory-affairs is fully cite-both-wired (L1b `regulations` role); cybersecurity/clinical reach L1b via semantic search only — surfaced as a user decision. **Not yet committed/pushed.**
- 2026-06-02: **Gap 1 done.** Broadened both registry role descriptions in `canonical-roles.yaml` (HIPAA/45 CFR + NIST SP 800-66); re-rendered all 11 canonical-role advisors → HIPAA now surfaces in regulatory/clinical/cybersecurity Tier 2. **Hit + fixed a `core.symlinks=false` blocker** (agent files were de-materialized symlinks — see lessons); healed 21 broken symlinks across `.claude/{agents,commands,hooks,rules}`. Working tree clean except intended changes. Next: discovery-index rebuild + Gap 2 L1b docs.
- 2026-06-02: Task created from ben/075 assessment. Two gaps scoped (stale registry descriptions; missing L1b applicability). Grounding from assessment captured.

## Economics

_Retrospective estimate (rough; from task summary). See effort-estimation-rubric.md._

```json
{
  "economics": {
    "method_version": 1,
    "retrospective": true,
    "agentic_hours": 7,
    "todos": [
      {
        "todo": "HIPAA advisor grounding gaps",
        "personas": [
          "regulatory-affairs",
          "cybersecurity",
          "rd-lead"
        ],
        "manual_hours": {
          "min": 16,
          "max": 40
        },
        "confidence": "low",
        "basis": "advisor grounding + L1b tier authoring + conformance"
      }
    ]
  }
}
```
