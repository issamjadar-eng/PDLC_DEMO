# TC-PROTO-CITATIONS — Run 0 (DRY RUN, in-process) — NOT a protocol execution

_Demo sample data — not for clinical use._

**Status of this file:** operator dry run only. It does **not** count as one of the three
protocol runs and no `TC-PROTO-CITATIONS.result.yml` was written — the case remains
**NOT-EXECUTED**. Reason: the executing agent (a worker fork) is barred from spawning
subagents, so the unit under test — the deployed `citations` advisor (`.claude/agents/citations.md`)
with its researcher subagents and `mcp__file-locator__locate` — could **not** be invoked. The
operator instead resolved each item against the byte-correct distilled sources by hand, with the
protocol's answer key in view. That verifies the **challenge set** (every expected verdict is
supported by the sources), not the **agent's judgment**, which is what WUN-05 needs.

| Field | Value |
|---|---|
| Timestamp | 2026-09-08T21:51Z |
| Commit | `e01c4a1` (working tree dirty — 12 files, another session's WIP) |
| Model id (operator) | `claude-fable-5-1` |
| Harness | 2.1.265 (Claude Code) |
| reference-audit / medtech-docs | 4 / 36 |
| Operator | AI assistant (operator) for BX |

## Challenge-set verification against sources (not agent verdicts)

| # | Expected | Source evidence found | Answer key holds? |
|---|---|---|---|
| 1 | sound | `iso-14971.md` L29 `#### 4.4 Risk Management Plan`; citing line `note: "ISO 14971:2019 §4.4"` | yes |
| 2 | sound | `iec-62304.md` L27 `#### 5.1 Software Development Planning`; citing `note: "IEC 62304 §5.1"` | yes |
| 3 | sound | `iec-62366-1.md` L26 `#### 5.1 Use Specification`; citing `note: "IEC 62366-1 §5.1"` | yes |
| 4 | sound | `iso-14971.md` L46 `#### 5.1 Risk Analysis Process` | yes |
| 5 | sound | `iec-62304.md` L76 `#### 5.8 Software Release` | yes |
| 6 | sound | `iec-62366-1.md` L40 `#### 5.2 Use-Related Risk Analysis` | yes |
| 7 | sound | `qsub.md` L28 `### Pre-Submission Package Contents` | yes |
| 8 | sound | `docs/project/submissions/510k/composition-manifest.md` exists; tracker L16 links `../510k/composition-manifest.md` | yes |
| 9 | citation-mislabeled | `iec-62304.md` carries classification at L13 `## Safety Classification (Amd 1:2015)`; no `4.3` heading; citing `software-requirements.md` L14 "per IEC 62304 §4.3" | yes (real defect) |
| 10 | stale-citation | `qmsr-part-820.md` L22: former § 820.30 `[Reserved]`, "no longer exist"; citing `GL-TMP-DC-001` L22 `21 CFR 820.30(b)` | yes (real defect) |
| 11 | registry-gap | no `iso-13485*` under `docs/external/standards/` nor `.claude/skills/medtech-docs/references/standards/`; citing `GL-TMP-DC-001` L22 `ISO 13485 §7.3.2` | yes (real defect) |
| 12 | citation-absent-from-source | `iec-62366-1.md` clause headings end at L82 `#### 5.7`; citing `GL-TMP-UC-003` L22 `IEC 62366-1 §5.9` | yes (real defect) |
| 13 | citation-absent-from-source | `iso-14971.md` 4.x headings end at `4.5` (L39); no 4.9 | yes |
| 14 | citation-absent-from-source | no `Annex` heading in `iec-62366-1.md` | yes |
| 15 | stale-citation | `iec-62304.md` §5.1 is Software Development Planning, not the risk management file | yes |
| 16 | broken-link | `GL-TMP-RM-999-nonexistent.md` does not exist | yes |

Answer key: 16/16 supported by the sources. Items 9–12 are confirmed **real project findings**
(route to the owning documents' tasks per protocol § 4).

## What remains to execute the protocol

Runs 1–3 must invoke the `citations` agent (point-query mode, one Agent call per item or one
batch call per run, fresh session per run) from a session that can spawn subagents, capture the
returned `findings[]` verbatim under `tools/workbench-validation/protocols/TC-PROTO-CITATIONS/run-<n>/`,
then write `TC-PROTO-CITATIONS.result.yml` per `templates/protocol-result.yml`.

## Deviation to carry into the eventual execution record

- step 3: unit under test not invoked (fork cannot spawn subagents); operator verified the
  challenge set against sources instead. Impact: no evidence of agent judgment; case stays
  NOT-EXECUTED.
