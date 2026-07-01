# 055 — SECOPS Roster Reconciliation

**ID**: 055
**Created**: 2026-05-13
**Status**: In Progress
**Created By**: Ben (with Claude)
**Owner**: Ben
**Priority**: High

---

## PERMANENT RULES (do not remove)

This task document is the **session-recovery point** for this work. If the current session drops, is compacted, or ends, the next session must be able to load **this file alone** and continue where we left off. That is only possible if the doc is kept current in-flight.

1. **Update at every meaningful checkpoint (HARD RULE).** After each meaningful unit of work — a converted/adopted doc, a committed change, a launched batch, a completed phase, a decision, a discovered blocker, a design pivot — update this task doc:
   - tick the relevant Todo checkbox
   - add a dated Changelog line naming the concrete artifact (commit SHA, file path, decision, blocker)
   - update any progress counts/tables in Goals
2. **Phase-end batching is OK; drift-batching is not.** Planned phases are a legitimate checkpoint — writing once per phase is fine if the phase is bounded and the write happens **at the phase boundary**. What's not OK: accumulating updates in your head across arbitrary work. If you can't name the specific upcoming checkpoint where you'll write the update, write it now.
3. **A commit is not a substitute.** Git history records code; this doc records the project narrative.
4. **Resume-ready before any session boundary.** Before recommending a fresh session, marking Complete, or ending work, the doc must already contain: (a) what was completed this session with concrete artifacts, (b) status of any in-flight work, (c) priority-ordered next steps with file paths, (d) open questions blocking progress, (e) the exact `/task` activation command to resume.
5. **Capture strategy + lessons as they happen.** Write decisions, scope boundaries, and corrected assumptions into this doc **in-flight**.

Success test for this doc: a fresh Claude session, given only this file, can re-enter the work without asking the user "what were we doing?"

## Goals

The `/secops` automated check (run 2026-05-13, recorded in `tasks/ben/SECOPS.md`) FAILed on **"Collaborators in roster"** — six GitHub collaborators on `GlobalLogic-a-Hitachi-Company/PDLC_DEMO` are not present in `project.yml` `team.active`. Reconcile the roster so authorized collaborators are codified and the audit reflects reality.

**This is a governance action, not just a check-silencing exercise** — two of the six have **admin** access. Each addition is an explicit statement that the person is authorized on this program.

## Why this matters

The SECOPS roster check exists so every repo collaborator is vetted and accounted for in `project.yml`. An unreconciled roster means the audit can't distinguish "authorized but unrecorded" from "genuinely unauthorized access." Closing the gap restores the check's signal value.

## Collaborators to reconcile

GitHub data gathered via `gh api users/<login>` + `gh api repos/.../collaborators`. Identities for private-profile users supplied by Ben.

Live collaborator list (re-checked 2026-05-13) — Ben + 5 others: `vyanovych`, `mykhailochaus-GLO`, `orestdanchak-gl`, `dmytro-savenkov-gl`, `WojtekTGL`. **`tlytvyn` is no longer a collaborator** — the personal-Gmail account was removed from the repo.

| GitHub login | Name | Email | Repo access | Role | Status |
|---|---|---|---|---|---|
| `vyanovych` | Vladyslav Yanovych | `vladyslav.yanovych@globallogic.com` | **admin** | Associate Vice President, Quality Assurance | ✅ added to project.yml |
| `mykhailochaus-GLO` | Mykhailo Chaus | `mykhailo.chaus@globallogic.com` | write | Lead Software Engineer | ✅ added to project.yml |
| `orestdanchak-gl` | Orest Danchak | `orest.danchak@globallogic.com` | write | Senior Manager, Engineering | ✅ added to project.yml |
| `dmytro-savenkov-gl` | [VERIFY] | [VERIFY] | **admin** | [VERIFY] | ⛔ held out — identity unverified |
| `WojtekTGL` | [VERIFY] | [VERIFY] | read | [VERIFY] | ⛔ held out — identity unverified |
| _(Taras Lytvyn — new GL account)_ | Taras Lytvyn | [VERIFY] — globallogic.com | not yet a collaborator | Solution Architect | ⏳ awaiting new GitHub username + repo access |

**Taras Lytvyn:** old `tlytvyn` account (personal Gmail `lytvyn.taras88@gmail.com`) has been **removed** from the repo. He now has a GlobalLogic email on a (new/updated) GitHub account and is a **Solution Architect**. That account is **not yet in the collaborator list** — once it's granted repo access, it gets a fresh roster row. Need: new GitHub username + globallogic.com email.

**Concerns flagged to Ben:**
- `dmytro-savenkov-gl` and `WojtekTGL` identities are **not yet verified** — `dmytro-savenkov-gl` has admin access, so leaving it unverified in an audit artifact is itself a finding.

## Todos

- [x] Read `project.yml` `team:` block — schema confirmed: `name / github / task_folder / role / email / added`; `task_folder` is lowercase first name; `added` is ISO date.
- [x] Added 3 fully-verified collaborators to `team.active`: `vyanovych` (AVP Quality Assurance), `mykhailochaus-GLO` (Lead Software Engineer), `orestdanchak-gl` (Senior Manager, Engineering). All identities + roles confirmed by Ben.
- [x] Removed `tlytvyn` — re-check of the live collaborator list confirms the personal-Gmail account is no longer on the repo. The row briefly added earlier was reverted.
- [x] Created `tasks/{vladyslav,mykhailo,orest}/000-index.md` — adding roster rows tripped check #13 ("Task folders exist", High) since `task_folder` must map to a real directory. Minimal index files created; checks #13 + #14 now PASS.
- [x] Re-ran `/secops check` (had to age the `- Date:` line in SECOPS.md past the 7-day TTL twice — the cache is the file itself, no `--force` flag). Result: **12/16 pass, 3 critical, 0 high, 1 warn**. Check #12 "Collaborators in roster" went from `Unauthorized: tlytvyn vyanovych mykhailochaus-GLO orestdanchak-gl dmytro-savenkov-gl WojtekTGL` (6) → `Unauthorized: dmytro-savenkov-gl WojtekTGL` (2).
- [ ] Add Taras Lytvyn's **new** GL GitHub account (Solution Architect) once it's granted repo access — need new username + globallogic.com email
- [ ] Get verified identity for `dmytro-savenkov-gl` and `WojtekTGL` from Ben, then add them — **deliberately left OUT of project.yml** rather than adding `[VERIFY]`-only rows to a live security config consumed by hooks/scripts
- [ ] Commit `project.yml` + `tasks/ben/SECOPS.md` + the 3 new task-folder index files + this task doc

## SECOPS check results (2026-05-13, post-reconciliation)

| # | Check | Result | Note |
|---|---|---|---|
| 12 | Collaborators in roster | ❌ FAIL (Critical) | `dmytro-savenkov-gl`, `WojtekTGL` still unauthorized — blocked on identity verification |
| 13 | Task folders exist | ✅ PASS | fixed this task — created vladyslav/mykhailo/orest folders |
| 14 | No orphan task folders | ✅ PASS | — |

**Out-of-scope pre-existing failures** (not roster-related — separate remediation, not task 055):
- #1 GitHub 2FA — Critical — not enabled on Ben's GitHub account
- #3 GitHub email domain — Critical — no verified email on an approved domain
- #6 Branch protection — WARN (High) — no branch protection on `main`

## Open Questions

- `dmytro-savenkov-gl` + `WojtekTGL` — verified name / email / role?
- Taras Lytvyn's new GL GitHub account — username + globallogic.com email? (Not yet a repo collaborator; add the row once access is granted.)

## Resume Command

```bash
bash .claude/hooks/task-activate.sh add <SESSION_UUID> 055
```

## Strategy + Lessons (inline captures)

_None yet._

## Changelog

| Date | Author | Summary |
|---|---|---|
| 2026-05-13 | Ben (with Claude) | Task created. SECOPS roster check FAILed on 6 unauthorized collaborators. GitHub lookups recovered full identity for `tlytvyn` + `orestdanchak-gl`; Ben supplied `vyanovych` + `mykhailochaus-GLO`. `dmytro-savenkov-gl` + `WojtekTGL` still unverified. Two concerns surfaced: `tlytvyn` personal-Gmail will still fail the domain check; `dmytro-savenkov-gl` has admin access but unverified identity. |
| 2026-05-13 | Ben (with Claude) | Added 4 collaborators to `project.yml` `team.active` (`vyanovych`, `mykhailochaus-GLO`, `orestdanchak-gl`, `tlytvyn`). `dmytro-savenkov-gl` + `WojtekTGL` deliberately held out of project.yml — won't put `[VERIFY]`-only rows into a live security config. Not yet committed; secops re-check pending. |
| 2026-05-13 | Ben (with Claude) | Ben: `tlytvyn` personal-Gmail account removed from the repo; Taras has a new GL GitHub account, role Solution Architect, not yet a collaborator. Re-checked live collaborator list — confirmed `tlytvyn` gone. **Reverted the `tlytvyn` row** from project.yml. Orest Danchak role confirmed: Senior Manager, Engineering ([VERIFY] cleared). Roster now has 3 fully-verified additions; 2 unverified collaborators (`dmytro-savenkov-gl`, `WojtekTGL`) + Taras's pending new account remain. |
| 2026-05-13 | Ben (with Claude) | Created `tasks/{vladyslav,mykhailo,orest}/000-index.md` — roster additions tripped check #13 (task_folder must be a real dir). Re-ran `/secops check`: 12/16 pass, check #12 down from 6→2 unauthorized, checks #13+#14 now PASS. Remaining #12 failures (`dmytro-savenkov-gl`, `WojtekTGL`) blocked on identity verification. Pre-existing non-roster failures (#1 2FA, #3 email domain, #6 branch protection) noted as out-of-scope. Not yet committed. |

## Economics

_Retrospective estimate (rough; from task summary). See effort-estimation-rubric.md._

```json
{
  "economics": {
    "method_version": 1,
    "retrospective": true,
    "agentic_hours": 3,
    "todos": [
      {
        "todo": "SecOps roster reconciliation",
        "personas": [
          "rd-lead",
          "cybersecurity"
        ],
        "manual_hours": {
          "min": 6,
          "max": 16
        },
        "confidence": "low",
        "basis": "secops roster reconciliation"
      }
    ]
  }
}
```
