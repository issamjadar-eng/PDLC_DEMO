# Validation Protocol — TC-PROTO-LIVE-MCP: Adopt → edit → publish round trip against the real Confluence and Jira

_Demo sample data — not for clinical use._

**Method**: protocol (operator + agent; verdict PASS / FAIL against §6)
**Scope**: deployment · **endpoint**: live · **connection**: confluence, jira
**Status**: **NOT-APPLICABLE in this deployment** — `validation.yml` declares `deployment.connections.confluence: none` and `jira: none` (`project.yml` has no `change_control` block). This protocol is authored so a connected deployment can execute it unchanged; no execution record exists.

## 1. Purpose

The change-control adopt and publish paths run through the Atlassian MCP server: the agent
makes the call, not a script, so they cannot be exercised from pytest. The mocked-transport
cases prove the transform logic; only a live round trip proves the integration against the
systems of record.

## 2. Need(s) under test

| Need | User story |
|---|---|
| WUN-16 | As a document control specialist, I need the workbench to prove that adopting and publishing a controlled page works against our real Confluence and Jira when the workbench is connected to them, not only against a simulation, so that we rely on integration evidence from the actual systems of record, not a stand-in. |

## 3. Configuration baseline to record

Commit + clean-tree flag, model identifier, `change-control` and `web-control` versions, the
Atlassian MCP server identifier and the `project.yml change_control.test_target` (space key,
parent page id, title prefix), operator, date.

## 4. Challenge set

Derived from `.claude/skills/change-control/SKILL.md` (`adopt`, `pull`, `publish`, `verify`).
All items run inside the deployment's declared sandbox parent page (`change_control.test_target`), never against a controlled page.

| # | Step | Expected outcome | Source of truth |
|---|---|---|---|
| 1 | `adopt` a sandbox page containing a heading, a table, one image, one `<details>` Confluence Zone with a reserved title | Markdown written at `staging_target_root`; frontmatter carries `confluence.page_id`, `confluence.version`, snapshot; image downloaded; zone preserved as `<details>` | `adopt` action + `actions/adopt.md` |
| 2 | Edit one paragraph locally; `publish` | Page version increments by exactly 1; body shows the edit; the Confluence Zone content is unchanged | `publish` divergence + zone-preservation contract |
| 3 | Edit the page in Confluence directly, then `publish` again | Divergence detected; Overwrite / Merge / Abort prompt appears; Abort leaves both sides unchanged | `publish` divergence detection |
| 4 | `pull` the page | `<doc>.confluence-side.md` written; differs from local exactly in the Confluence-side edit | `pull` action |
| 5 | Set frontmatter `state: frozen`; attempt `publish` | Refused | `publish` refuses for `review-formal`, `frozen`, `released` |
| 6 | `verify orphan-file` and `verify drift-detection` | Both report success in their JSON reports | `verify <kind>` action |
| 7 | Jira: expand an `AUTO:JIRA-LIST` sentinel on a sandbox page with a JQL that returns ≥ 1 issue | Rendered issue table spliced between the sentinels; count matches a manual JQL run | `_expand_jira_macros` + Jira search |

## 5. Procedure

1. Confirm the deployment declares the connections and that the sandbox parent exists; record the baseline (§3).
2. Execute items 1–7 in order in one session; capture every command, agent transcript excerpt, page version numbers and JSON verify reports under `tools/workbench-validation/protocols/TC-PROTO-LIVE-MCP/run-<n>/`.
3. Restore the sandbox (delete created pages or note them as retained test artefacts).
4. Repeat for two runs (§7).
5. Evaluate §6; record verdict, deviations, sign-off.

## 6. Acceptance criteria

- Items 1, 2, 4, 6, 7 succeed exactly as described in **both** runs.
- Item 3: divergence detected in both runs; Abort leaves both sides byte-identical to before.
- Item 5: publish refused in both runs.
- **0** controlled pages touched (all page ids created are under the sandbox parent).

## 7. Repeatability

Two independent runs (live systems carry cost and side effects; two is the minimum that shows the result is not a one-off).

## 8. Execution record

`tools/workbench-validation/protocols/TC-PROTO-LIVE-MCP.result.yml`. In this deployment the runner reports the case NOT-APPLICABLE from the `deployment.connections` declaration and does not look for a result file.

## 9. Deviations

_None recorded (unexecuted)._

## 10. Sign-off

| Role | Name | Date |
|---|---|---|
| Executed by | | |
| Reviewed by | | |
