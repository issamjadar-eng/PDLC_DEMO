# trace-matrix — Design & Architecture

This document is not loaded by Claude during normal skill operation — it exists for human understanding.

For skill usage and instructions, see `SKILL.md`.

## Best Practices

| # | Practice | Why |
|---|---|---|
| 1 | **Skill is the only writer.** Console (or any other reader) must never compute traces — only read the JSON sidecar. | Single source of truth for trace logic. Bugs fixed in one place. |
| 2 | **Show missing as missing.** Never paper over empty layers, broken refs, or absent trace data. Render them as visible gaps. | The trace matrix is most valuable as a scoreboard for what's not done yet. |
| 3 | **Build is deterministic.** LLM work only at `init`. Build imports files, runs Python, writes outputs. | Predictable, debuggable, and cheap to run in hooks or CI. |
| 4 | **Project adapters beat shipped defaults.** Presence of `tools/project-console/trace-matrix/adapters/<layer>.py` is the override signal. No registry, no flags. | Minimum ceremony. The file system is the registry. |
| 5 | **The JSON shape is the contract.** Bumping `version` requires a coordinated release with project-console. | Loose coupling depends on shape stability. Minor additive fields are backwards-compatible (1.0 → 1.1 ok). |
| 6 | **Atomic emits.** Write to `.tmp` and rename. Never leave a partially written `trace-matrix.json`. | The console may be reading at the same moment a build runs. |
| 7 | **Inline labels in the sidecar.** Each item carries its own summary; each trace edge carries the target's summary too. | Console renders expandable rows with no second fetch. |
| 8 | **Per-DHF independence.** A failure parsing one DHF must not block others. | Demo projects often have uneven DHFs. |
| 9 | **Rational check before adapter generation.** Defaults are the fast path. Only generate an adapter when defaults *and* project data are both present and the defaults fail to extract what's clearly there. | Avoid generating adapters that mask a missing-data gap as a parser gap. |

## Changelog

- **v4 (2026-05-04)** — Added shared cross-layer adapter tier and a new `software` layer. New `adapter:` field on per-layer config in `trace-matrix.yml` resolves to `scripts/parsers/<name>.py`, taking priority over project overrides and defaults. Shipped first shared adapter `jira-mirror` for parsing Jira-mirror tables (epics/stories/hazards/tests). Added `software` layer to `LAYER_ORDER`/`LAYER_TITLES`, with new edge handlers in `graph.py` for DI→SW and SW→V&V edges (driven by `traces_forward_ids` carrying parent/verifies references). Added `parsers/defaults/software.py` no-op fallback so DHFs without a software layer continue to build. Added `tests/test_jira_mirror.py` with project-agnostic fixtures (`DEMO`, `DI`, `PHA` placeholders).
- **v3 (2026-04-23)** — Maintenance pass; documentation refinements.
- **v2 (2026-04-15)** — Adapter generation pass. Refactored parsers into `parsers/defaults/`, introduced `adapter_api.py` with `ParserResult` and `load_adapter`, added `analyze.py` rational-check CLI, added `source_files` + `warnings` to the sidecar (`version: 1.1`), removed hardcoded file paths from the console's doc-link. Project overrides live at `tools/project-console/trace-matrix/adapters/`. Build remains deterministic. Backwards-compatible with v1 sidecars on the console side.
- **v1 (2026-04-15)** — Initial release. UN + DI parsers complete; V&V derived from DI verification column; architecture nodes-only with `edges_known` banner; risk overlay surfaces empty-layer state. Bidirectional graph, orphan and broken-ref detection. Markdown + JSON emitters.
