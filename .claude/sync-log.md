# Sync Log

Append-only record of `/sync-skills` pull/push actions. Most recent entries at the top.

---

## 2026-06-23 — merge + pull (usage-metrics skill + project-console Metrics view) [ben/093]

- **Context:** the new `usage-metrics` skill (cross-team token/cost telemetry) was the user's own work, authored from the **arthrex-pccp** project, sitting on hitachi branch `sync/arthrex-pccp-usage-metrics-console-2026-06-23` (`e23c6d1`) with **open PR #231** — not yet on origin/main (which is why a plain `check` reported "no new skills").
- **Merged hitachi PR #231** → main (squash, branch deleted). Merge commit `94653c7`. Local hitachi checkout fast-forwarded to main; local sync branch removed.
- **Pulled 23 files** (all auto-pull bucket: 16 UPSTREAM_ONLY + 7 UPSTREAM_ADVANCE; byte-identical to `94653c7`): new `skills/usage-metrics/**` (11), `project-console` Metrics view (5 new `console/metrics/**` + metrics.js + metrics_view.html; 5 mod: SKILL/README/VERSION/app.py/_base.html), `shared/scripts/resolve_user.py`, `task/rules/scratch-and-tmp.md` (adds `_usage-metrics/` sandbox row).
- **project.yml:** added `usage-metrics` to `security.approved_skills`; `/usage-metrics setup` appended the `usage_metrics:` block (method=local, publish.enabled=true→branch main) and added `**/_usage-metrics/**` to `file_locator.corpus_excludes`.
- **Setup (full team loop):** symlinked+registered 2 hooks (SessionStart `usage-metrics-refresh`, SessionEnd `usage-metrics-publish`); seeded `tools/usage-metrics/pricing.json`; installed `.github/workflows/usage-metrics-aggregate.yml` (daily cron). project-console synced 1.25.0→1.28.0 + restarted; Metrics view live on :8765 (200 on `/metrics`, `/metrics/data`).
- **Bugfix (local, diverges from main — push candidate):** `usage-metrics/scripts/collect.py` slug did `/`→`-` only; missed the `_` in `PDLC_DEMO` (real transcript dir `-Users-…-PDLC-DEMO`). Fixed to replicate CC's all-non-alphanumeric→`-` encoding (+ legacy fallback). After fix: collect wrote 6 ben sessions; aggregate rendered the dashboard. **Affects any underscore/dot-named project → push upstream.**
- **Nothing committed** — all changes are in the PDLC_DEMO working tree pending user's push decision.
- Follow-ups: (a) project PR for PDLC_DEMO; (b) `/sync-skills push` the `collect.py` slug fix to hitachi.

## 2026-06-23 — pull (task hook checkpoint-marker TTL)

- Hitachi HEAD at sync: `b6067e0` (registry clone already current; `git fetch` confirmed 0 behind).
- Three-way buckets: UPSTREAM_ONLY 0 · LOCAL_ONLY 0 · UPSTREAM_NEWER 1 (ADVANCE 1).
- **Pulled 1 file**: `skills/task/hooks/check-active-task.sh` (UPSTREAM_ADVANCE, hitachi #230) — adds a 7-day TTL purge of `uncheckpointed-*.txt` checkpoint-recovery markers alongside the existing `active-tasks-*.txt` purge. Additive bugfix; no contract change.
- **No new skills.** Project was fully in lockstep with the registry except this one hook (the references / dhf-manifest / submissions-v2 advances from #226–#229 were already present from the 2026-06-15 sessions).
- project.yml: no changes. No new skills/agents/allowlist edits.
- Setup impact: **none** — the hook is referenced in-place via settings.json; pulling the file updates it live, no re-registration. No `uncheckpointed-*` markers currently accumulating in `.state/`.
- Follow-ups: none from this pull. (Pre-existing, unchanged: advisor GROUNDING re-render `/advisors sync`; R1/R2 from ben/090.)

## 2026-06-15 — push (references + tracker + submissions v2) + prune

- **PR #226** (hitachi, squash-merged): `references/regulations/21-cfr-part-814.md` (new PMA distillation), `21-cfr-part-807.md` (§807.87 (a)–(m) lettering pin), regs `README.md` (814 row), `tracker/{SKILL,README}.md` (v14 manifest-ownership), `project-console/tests/test_tracker_workflow_e2e.py` (807.87(k)→(l) fixture fix).
- **PR #227** (hitachi, squash-merged): `submissions` v1→v2 — filing-type template profiles (`_shared/qsub/510k/pma`, renames preserve history), 510(k) + PMA template sets, `render_sidecars.py` pma registration, composition-manifest contract; deletes the 7 superseded flat templates.
- Hitachi HEAD after merges: `82b867b`.
- **prune**: removed 8 merged `sync/*` branches (0 unmerged kept).
- Post-push: pulled a docflow re-advance (registry was active — advanced several times mid-session). Residual drift: only `references/fda-guidance/pccp-aiml-full.md`.
- Follow-up: confirmed `pccp-aiml-full.md` was a registry file **deleted upstream** in hitachi `297565c` (PR #218 — source-md-authoritative refactor; the standalone "full" distillation was superseded by the verbatim `source-md/` tier). Our copy (from the initial scaffold) was a stale leftover that surfaced as LOCAL_ONLY because the analyzer can't distinguish "we added" from "they deleted." **Deleted locally → skill drift now 0 (fully synced).**

## 2026-06-15 — pull (medtech-docs references refresh + advisors advance)

- Hitachi HEAD at sync: `88e793d` → advanced to `f3ee6f5` mid-session (a docflow update landed upstream; pulled in a second pass). Project repo also ff-pulled 1 commit: file-locator CI index.db `7e80881`.
- Three-way buckets: UPSTREAM_ONLY 22 · LOCAL_ONLY 23 · UPSTREAM_NEWER 92 (ADVANCE 71 · LOCAL_AHEAD 8 · UNDETERMINED 13)
- **Pulled 93 files** (86 first pass + 7 docflow in the mid-session second pass: docflow SKILL.md/agents/scripts advance + new `fidelity_adjudicator.md` agent + `verify_conversion_fidelity.py`, all clean UPSTREAM_ADVANCE/ONLY, no local docflow edits to collide): all `medtech-docs/references/fda-guidance/*` + `references/regulations/{880,892,164}` distillations advanced; new verbatim `references/regulations/source-md/*.md` + `source/*.xml` archives (807/880/892/164); advisors skill + 13 advisor agents (1-commit advance each); new `medtech-docs/rules/articles-not-canonical.md`, `templates/readme-articles.md`, `scripts/verify-conversion.py`; top-level `agents/citations*` (reference-audit). 13 UNDETERMINED agents = symlink artifact (real content pulled via advisors).
- **Merged 2 (BOTH_DIVERGED)**: `references/regulations/21-cfr-part-807.md` (took upstream's §807.85/§807.100/§807.81 corrections + finding-aid/source-md tier, re-applied our §807.87 (a)–(m) table) and `references/regulations/README.md` (upstream refresh + re-added our Part 814 row/changelog).
- **Skipped 7** `submissions/templates/*` UPSTREAM_ONLY — the old flat v1 templates superseded by our v2 profile reorg (do not resurrect).
- **Held for push (no push this session, per user)**: 23 LOCAL_ONLY (submissions v2 profiled templates, `21-cfr-part-814.md`, `pccp-aiml-full.md`) + 6 LOCAL_AHEAD (submissions SKILL/README/VERSION/render_sidecars, tracker SKILL/README) + the 2 merged files above.
- project.yml: added `file_locator.corpus_excludes: "articles/**"` (medtech-docs v34 post-update); allowlists already current (citations agents + reference-audit present).
- Post-update: symlinked `.claude/rules/articles-not-canonical.md` (medtech-docs v34). Advisor GROUNDING re-render (`/advisors sync`) recommended but not yet run.
- Doc-eval (medtech-docs v32/v33 reference corrections): project docs clean — no §807.85/§807.100/§807.87(k) miscitations in `docs/`; only §807.81(a)(3) cited (correct). Optional enhancement: cite §807.81(b) PCCP carve-out in `pccp-summary.md`.
- Follow-ups: 6 stale `sync/*` branches (run `/sync-skills prune`); held push candidates above; R1/R2 (ben/090).

## 2026-06-01 — push (file-locator v2 — self-healing venv bootstrap wrapper)

- Files: `skills/file-locator/SKILL.md`, `skills/file-locator/README.md`, `skills/file-locator/templates/bootstrap.sh` (new, `100755`), `skills/file-locator/templates/mcp.json.snippet`
- Branch: `sync/pdlc-demo-file-locator-self-healing-2026-06-01`
- PR: https://github.com/GlobalLogic-a-Hitachi-Company/hitachi/pull/192
- Commit: "file-locator v2: self-healing venv bootstrap wrapper"
- Status: merged
- Merge commit: `f3524ff` (squash, PR #192)
- Hitachi HEAD after sync: `f3524ff`
- Origin: pdlc_demo task ben/074. Excluded `skills/file-locator/scripts/indexer_docs.py` (pre-existing unrelated drift, UNDETERMINED/race — not part of v2).

## 2026-05-16 — push (advisors v1.3.1 — pytest test runner + build-artifact gitignore)

- Files: `skills/advisors/SKILL.md`, `skills/advisors/README.md`, `skills/advisors/VERSION`, `skills/advisors/.gitignore` (new), `skills/advisors/tests/run.sh` (new)
- Branch: `sync/pdlc-demo-advisors-v1.3.1-2026-05-16`
- PR: https://github.com/GlobalLogic-a-Hitachi-Company/hitachi/pull/169
- Commit: "advisors v1.2.0 → v1.3.1: pytest test runner + build-artifact gitignore"
- Status: merged 2026-05-16 (squash, branch deleted; local sync branch also cleaned up per v8.2)
- Merge commit: `95dde22`
- Hitachi HEAD after sync: `95dde22`
- Note: `check` flagged the 3 modified advisors files `UPSTREAM_NEWER`, but `--analyzed` refined to `LOCAL_AHEAD` — local advisors (v1.3.1) was *ahead* of hitachi (v1.2.0). Verified by diff (local = hitachi `9d7d6e6` + ben/058's v1.3.1 work). This push lands that work upstream — a push, not a pull.
- Originating task: ben/058

## 2026-05-16 — pull (sentinel-blocks rule — v23 backfill)

- Hitachi HEAD after sync: `cda0eaa`
- Pulled: 1 file
  - `skills/medtech-docs/rules/sentinel-blocks.md` — hitachi PR #168 (`cda0eaa`) backfilled the v23 renderer capabilities into the rule: `depth=<N>` attribute, `dhf-table` variants section, updated `exclude=` (adds `assets`) + `preserve-column` defaults. `UPSTREAM_ADVANCE` — local matched the `b0beab3` blob, upstream advanced 1 commit.
- Skipped (`LOCAL_AHEAD` / `LOCAL_ONLY` — ben/058 advisors work, push candidates not pull): `skills/advisors/{README.md,SKILL.md,VERSION,.gitignore,tests/run.sh}`
- project.yml: no changes
- Follow-ups: none — `render-sentinels.py` is already v23 here; this is a rule-text-only sync (doc caught up to existing code). The `.claude/rules/sentinel-blocks.md` symlink resolves unchanged.
- Originating task: ben/064

## 2026-05-16 — push (sync-skills v8.2 — auto-clean merged branches + `prune` action)

- Files: `skills/sync-skills/SKILL.md`, `skills/sync-skills/README.md`, `skills/sync-skills/scripts/sync.sh`, `skills/sync-skills/tests/test_prune.sh` (new)
- Branch: `sync/pdlc-demo-sync-skills-v8.2-prune-2026-05-16`
- PR: https://github.com/GlobalLogic-a-Hitachi-Company/hitachi/pull/167
- Commit: "sync-skills v8.2: auto-clean merged branches + prune action"
- Status: merged 2026-05-16 (squash, branch deleted)
- Merge commit: `cc9add3`
- Hitachi HEAD after sync: `cc9add3`
- Note: dogfooded the new `prune` action immediately after — it found and removed this push's own leftover local `sync/*` branch in the hitachi checkout.
- Originating task: ben/063

## 2026-05-16 — push (medtech-docs v25 — claude-md-references + audit-wiring rules, dedup)

- Files: `skills/medtech-docs/SKILL.md`, `skills/medtech-docs/README.md`, `skills/medtech-docs/rules/audit-wiring-before-adding-fields.md` (new), `skills/medtech-docs/rules/claude-md-references.md` (new); deleted `skills/medtech-docs/templates/claude-md-config-audit.md`
- Branch: `sync/pdlc-demo-medtech-docs-rules-batch3-2026-05-16`
- PR: https://github.com/GlobalLogic-a-Hitachi-Company/hitachi/pull/166
- Commit: "medtech-docs v25: own claude-md-references + audit-wiring rules; remove duplication"
- Status: merged 2026-05-16 (squash, branch deleted)
- Merge commit: `69fb6cc`
- Hitachi HEAD after sync: `69fb6cc`
- Note: push included a template **deletion** (`templates/claude-md-config-audit.md`) — removed via manual `git -C <hitachi> rm` before `push-finalize`, since `push-stage` only copies.
- Originating task: ben/061

## 2026-05-15 — push (medtech-docs v24 — rules/ dir + symlink-install)

- Files: `skills/medtech-docs/SKILL.md`, `skills/medtech-docs/README.md`, `skills/medtech-docs/rules/readme-before-write.md` (new), `skills/medtech-docs/rules/sentinel-blocks.md` (relocated from `templates/rule-sentinel-blocks.md`)
- Branch: `sync/pdlc-demo-medtech-docs-rules-symlink-2026-05-15`
- PR: https://github.com/GlobalLogic-a-Hitachi-Company/hitachi/pull/165
- Commit: "Migrate readme-before-write + sentinel-blocks rules to symlink install (medtech-docs v24)"
- Status: merged 2026-05-16 (squash, branch deleted)
- Merge commit: `b0beab3`
- Hitachi HEAD after sync: `b0beab3`
- Note: this push includes a file **rename** — `templates/rule-sentinel-blocks.md` → `rules/sentinel-blocks.md`. `sync.sh push-stage` only copies; the old path was removed with a manual `git -C <hitachi> rm` before `push-finalize`, which git recorded as a 99% rename.
- Originating task: ben/060


## 2026-05-15 — push (task v25 scratch/tmp convention + skill-creator v7 rules/ pattern)

- Files: `skills/task/SKILL.md`, `skills/task/README.md`, `skills/task/rules/scratch-and-tmp.md` (new), `skills/skill-creator/SKILL.md`, `skills/skill-creator/README.md`
- Branch: `sync/pdlc-demo-scratch-tmp-convention-2026-05-15`
- PR: https://github.com/GlobalLogic-a-Hitachi-Company/hitachi/pull/164
- Commit: "Add scratch/tmp convention install to task skill setup"
- Status: merged 2026-05-16 (squash, branch deleted)
- Merge commit: `eb8a9f2`
- Hitachi HEAD after sync: `b0beab3` (after PR #165 also merged)
- Note: `check` initially mislabeled the 4 modified files `BOTH_DIVERGED`; verified false positive (committed HEAD was byte-identical to upstream) — caused by the blob-probe keying recency off commit timestamps while hashing uncommitted working-tree edits. Committing the work locally (project commit `3d552b8`) reclassified them to `LOCAL_AHEAD`, then pushed cleanly.
- Originating task: ben/059

## 2026-05-15 — pull (advisors file-locator integration + new file-locator skill)

- Hitachi HEAD after sync: `9d7d6e6` (local hitachi checkout fast-forwarded 25 commits)
- Pulled: 28 files
  - `skills/advisors/SKILL.md`, `scripts/render-grounding.py`, 13× `skills/advisors/agents/*.md`, `tests/test_file_locator_wiring.py` — advisors update: adds the `mcp__file-locator__locate` semantic-search retrieval mode (degrades gracefully when MCP absent)
  - `skills/manifest.md` — registry version listing refresh
  - `skills/file-locator/**` (11 files) — NEW skill: local semantic file-search MCP (fastembed + SQLite FTS5)
- Auto-resolved: 13 top-level `.claude/agents/*.md` symlinks (point into `skills/advisors/agents/`) updated transitively — no separate pull
- project.yml: pending — add `file-locator` to `approved_skills` and `approved_mcps`
- Follow-ups: run `/file-locator setup` (new skill ships a `setup` action: writes `.mcp.json`, `project.yml`, `.github/workflows/`)

## 2026-05-13 — push (secops 2FA check v7→v8 — null-handling fix)

- Files: `skills/secops/SKILL.md`, `skills/secops/README.md`, `skills/secops/hooks/security-assert.sh`
- Branch: `sync/pdlc-demo-secops-2fa-check-2026-05-13`
- PR: https://github.com/GlobalLogic-a-Hitachi-Company/hitachi/pull/162
- Commit: "secops v7→v8: 2FA check — distinguish undeterminable from disabled"
- Status: merged (--merge requested)
- Merge commit: `255eed8d608dedbbcbcf3eb75135c7d2d1144b21`
- Hitachi HEAD after sync: `255eed8`
- Origin: pdlc_demo task ben/056 (surfaced during ben/055 roster reconciliation). Check #1 FAILed on `two_factor_authentication: null` because the `// false` jq fallback collapsed undeterminable→false. Fix: tri-state branching, null/empty→SKIP. Validated on PDLC_DEMO + sister project arthrex/pccp.

---

## 2026-05-13 — push (dhf-manifest canonical-roles resolution improvements v9→v12)

- Files: `skills/dhf-manifest/README.md`, `skills/dhf-manifest/SKILL.md`, `skills/dhf-manifest/actions/discovery-index.md`, `skills/dhf-manifest/data/canonical-roles.yaml`, `skills/dhf-manifest/scripts/discovery-index.py`, `skills/dhf-manifest/tests/test_discovery_index.sh`
- Branch: `sync/pdlc-demo-dhf-manifest-canonical-roles-2026-05-13`
- PR: https://github.com/GlobalLogic-a-Hitachi-Company/hitachi/pull/161
- Commit: "dhf-manifest: canonical-roles resolution improvements (v9→v12)"
- Status: merged (--merge requested)
- Merge commit: `a85260dc3b93664abafea18d02ed733c6290d605`
- Hitachi HEAD after sync: `a85260d`
- Origin: pdlc_demo task ben/051. Three discovery-index follow-ups — v10 multi-match no-winner bug fix (ambiguity_notes + paired gap), v11 lowercase-hyphen pattern variants for user_needs/software_requirements, v12 frontmatter `canonical_role:` author opt-in. Test suite 36 → 43. Sister project arthrex/pccp validated with zero functional regression.

---

## 2026-05-12 — pull (advisors v1.2.0 + dhf-manifest v9, post-trace-matrix-push sync)

- Source: hitachi HEAD `d3c3429` (post my own #159 merge)
- Pulled: 27 files
  - `skills/advisors/*` (19 files) — v1.2.0: canonical-role grounding model now default; literal-glob retained as legacy fallback. Rollout to all 11 advisor agents (clinical-affairs, core-team-panel, cybersecurity, design-review-panel, human-factors, post-market, program-manager, quality-engineering, rd-lead, regulatory-affairs, risk-management, systems-engineering, vnv-lead). New `advisor-researcher` helper agent. (hitachi PRs #156 / #158)
  - `skills/dhf-manifest/*` (2 SKILL + 4 new) — v9 catalog expansion (43 roles total) + `multi_file: true` flag; v8 new `discovery-index` action with `data/canonical-roles.yaml`, `scripts/discovery-index.py`, `tests/test_discovery_index.sh`. (hitachi PRs from arthrex-pccp ben/191)
  - `agents/advisor-researcher.md` — new agent at registry-root path (project pulls because it didn't exist locally).
- Post-update actions required:
  - **Run `/dhf-manifest discovery-index`** to bootstrap the per-project discovery index at `docs/project/dhf-manifest/pdlc-demo-dhf-discovery.json`. Without this, advisor agents fall back to literal-glob mode (still works, lower fidelity grounding).
  - No other actions surfaced — no new approved_skills / approved_agents entries required; no setup re-runs.
- Skipped:
  - `agents/<name>.md` registry-root copies (13 files) reported as BOTH_DIVERGED — expected drift: the project installs advisor agents as symlinks `.claude/agents/<n>.md` → `.claude/skills/advisors/agents/<n>.md` (skill-internal source of truth), while hitachi keeps a parallel registry-root `agents/<n>.md` copy with different content. This is the project's design choice, not real divergence.
  - `skills/project-console/console/web/static/console.overrides.css` — LOCAL_AHEAD push candidate (Manrope font fix from prior session); deferred for a later push.

---

## 2026-05-12 — push (trace-matrix v7→v8: bidirectional edge engine)

- Files: `skills/trace-matrix/SKILL.md`, `skills/trace-matrix/README.md`, `skills/trace-matrix/scripts/graph.py`, `skills/trace-matrix/scripts/analyze.py`, `skills/trace-matrix/tests/test_graph_bidirectional.py`
- Branch: `sync/pdlc-demo-trace-matrix-v8-2026-05-12`
- PR: https://github.com/GlobalLogic-a-Hitachi-Company/hitachi/pull/159
- Commit subject: `trace-matrix v7→v8: bidirectional edge engine + scope-filter refinement`
- Status: merged (--merge requested)
- Merge commit: `d3c3429`
- Hitachi HEAD after sync: `d3c3429`
- Source: ben/050 — surfaced by ben/049 SRS authoring; v7 V&V scope filter dropped DI-derived VER nodes when SW was added. Refactor introduces bidirectional canonical-edge model, adds SW→VER edges, refines scope filter to run only when V&V has independent source and accept any-requirement reciprocation. Sister-project (Arthrex/PCCP) validated zero regression before push.

---

## 2026-05-12 — push (tracker: unified overlay sidecar — supersedes #153)

- Files: `skills/tracker/scripts/generate.py`, `skills/tracker/scripts/render.py`
- Branch: `sync/pdlc-demo-tracker-unified-overlay-2026-05-12`
- PR: https://github.com/GlobalLogic-a-Hitachi-Company/hitachi/pull/154
- Commit subject: `tracker: unified overlay sidecar (supersedes deliverable-names.yml + human.json)`
- Status: merged (--merge requested; atomic supersede of #153)
- Merge commit: `735fc17`
- Hitachi HEAD after sync: `735fc17`
- Context: task `ben/047` Stage 5c — consolidates `deliverable-names.yml` (#153) + legacy `human.json` into one `submission-tracker.overlay.yml` with `defaults.by_dhf_role` + `rows.<id>` sections. Closes the `effort` + `path` override gaps that neither prior overlay supported. Per-row `name` flexibility enables milestone-distinct titles ("System SAD — Draft (Q-Sub Review)" vs "System SAD — LMR1 Release"). `render.py::load_human_overlay()` falls back to legacy `human.json` for back-compat (no project has adopted the JSON format yet anyway). Atomic supersede valid because #153 was merged 30 min prior with no downstream adopters.

---

## 2026-05-12 — push (tracker: deliverable-names sidecar)

- Files: `skills/tracker/scripts/generate.py`
- Branch: `sync/pdlc-demo-tracker-deliverable-names-sidecar-2026-05-12`
- PR: https://github.com/GlobalLogic-a-Hitachi-Company/hitachi/pull/153
- Commit subject: `tracker: deliverable-names sidecar — persistent friendly per-DHF row names`
- Status: merged (--merge requested)
- Merge commit: `faae97e`
- Hitachi HEAD after sync: `faae97e`
- Context: task `ben/047` Stage 5b — adds optional `docs/project/submissions/submission-tracker.deliverable-names.yml` sidecar with v0.1 schema (per-DHF × canonical-role mapping; "*" wildcard supported; precedence: specific > wildcard > folder.name fallback). 3 hunks / ~60 lines added / zero removed. Backward-compatible: projects without sidecar fall back to current behavior. Local PDLC_DEMO now renders friendly names ("System Software Architecture Document (SAD)", "Risk Management Report (ISO 14971)", etc.) across all 11 canonical roles × 4 phases.

---

## 2026-05-11 — push (sync-skills SKILL.md genericization)

- Files: `skills/sync-skills/SKILL.md`
- Branch: `sync/pdlc-demo-sync-skills-leak-fix-2026-05-11`
- PR: https://github.com/GlobalLogic-a-Hitachi-Company/hitachi/pull/148
- Commit subject: `sync-skills: genericize project-name examples in SKILL.md`
- Status: merged (--merge requested)
- Merge commit: `bd753b0`
- Hitachi HEAD after sync: `bd753b0`
- Context: task `ben/048` #1 — adopted from arthrex/pccp sister (they had it locally; never pushed upstream). 3 example-string substitutions in §Step-2 and §"2026-04-12 push" example block. No behavior change.

---

## 2026-05-11 — pull (visual polish + regulatory-affairs grounding)

- Hitachi origin/main: `f17e3bc` (was `4751abd` earlier today)
- Pulled (14 files, all clean — no local mods on any):
  - **`tracker` v12** (PR #145): `skills/tracker/README.md` only (changelog backfill for color-coded legend + readable disabled action buttons; the `render.py` changes shipped earlier with #143 are already local)
  - **`project-console` v1.17.0 → v1.21.1** (PR #146): `SKILL.md`, `README.md`, `VERSION`, `console/themes.py`, `console/web/static/{console.css, explorer.js}`, `console/web/templates/{_assistant_drawer.html, trace_matrix_index.html, trace_matrix_view.html, workflow_b3_index.html}`, `themes/dark/theme.yaml` — theme-token system, B6 workflow polish, asset-card CSS merge, full hardcoded-color sweep on B3 strategy-reassembly modals + chat textarea + diff buttons (no white-bg elements left on dark theme)
  - **`regulatory-affairs` agent** (PR #147): `agents/regulatory-affairs.md` + `skills/advisors/agents/regulatory-affairs.md` — grounding glob aligned to flat-strategies layout
- Post-update actions required: none (no `**Post-update:**` blocks in any changelog)
- project-console scaffold: synced 1.17.0 → 1.21.1
- Console restarted, all endpoints 200 (`/`, `/dashboards/submission-tracker`, `/trace-matrix`, `/workflows`, `/workflows/tracker-draft/Q1`)

---

## 2026-05-11 — pull (reset-to-upstream)

- Hitachi origin/main: `4751abd` (md-deck/build.py py3.9 fix, on top of `7fbaa3b` B6 Create Draft v1)
- Pulled (15 files):
  - **New B6 Create Draft workflow** — `skills/project-console/console/workflows/{draft_session.py,draft_writer.py}`, `skills/project-console/console/web/templates/workflow_tracker_draft.html`, `skills/project-console/tests/test_draft_workflow_e2e.py`, `skills/tracker/agents/draft-author.md`, `skills/tracker/scripts/build-draft-context.py`, `skills/tracker/tests/test_create_draft_wiring.py`
  - **B6 wiring updates** — `skills/project-console/console/workflows/router.py`, `skills/project-console/console/web/static/{assistant.js,tracker_interactive.js}`, `skills/tracker/scripts/render.py`
  - **md-deck py3.9 compat** — `skills/md-deck/scripts/build.py`
  - **Tracker baseline reset** — `skills/tracker/{SKILL.md,README.md,scripts/generate.py}` overwriting local v16/v17 WIP (init-taxonomy, classify-folders, assess-phases, reconcile-taxonomy actions; folder-classifier + phase-mapper agents; taxonomy.py + 6 helper scripts; schemas/taxonomy.schema.yml). Local WIP archived to `tasks/ben/044/archive/wip-dropped-2026-05-11/skill/`.
- project.yml: no changes
- project-console scaffold: synced 1.7.6 → 1.17.0
- Submission tracker regenerated from upstream v11 generator: `submission-tracker.md` (5.8KB / 52 table rows) + `submission-tracker.html` (24.7KB / 44 item rows / 6 Create Draft buttons). Project-side sidecars + candidate from the dropped WIP also archived under the same task-044 archive folder.
- Follow-ups: ben/047 captures the project-data + small upstream-pushable improvements to reach 118-row demo depth.

---

## 2026-05-05 — push + merge (project-console asset card selector)

- Files: 5
  - `skills/project-console/console/app.py` (mount `/assets` static dir)
  - `skills/project-console/console/overview/router.py` (asset discovery + context)
  - `skills/project-console/console/web/templates/overview.html` (card grid + viewer)
  - `skills/project-console/console/web/static/console.css` (card + viewer styles)
  - `skills/project-console/console/web/templates/index.html` (Workflows navigation)
- Branch: `sync/pdlc-demo-project-console-asset-cards-2026-05-05`
- PR: https://github.com/GlobalLogic-a-Hitachi-Company/hitachi/pull/142
- Commit: "project-console: Add asset card selector to /overview"
- Status: merged (`--merge` requested)
- Merge commit: `980e14f634a2f599c115b997a7a013559455cd4a`
- Hitachi HEAD after sync: `980e14f`
- Feature: Asset discovery via `assets/*/index.html` scan, card-based selector, inline iframe viewer, consolidated bottom button bar. Company-agnostic, portable across projects.

---

## 2026-05-01 — pull + push (3 PRs) + 1 cleanup PR

**Hitachi HEAD before sync**: `222ddf1` (project-console v1.7.8 → v1.9.0 PR #112)

### Pull (committed locally)

- **skill-creator v5 → v6** (5 files): non-blocking PreToolUse `skill-md-watch` hook + `audit-triggers` action. Hook will need `/skill-creator setup` re-run to register in `settings.json`.
- **project-console v1.5.0 → v1.9.0** (10 files): workflow B3 strategy reassembly + assistant.js / console.css updates.
- **change-control major expansion** (61 files): new INBOUND triggers (`adopt`, `adopt-tree`, `pull`, `promote`) for Confluence → repo, plus formal-review and internal-review action sets, lib/ rewrite, ~10 new test files.

### Skipped on pull

- 3 `.pyc` files leaked into `hitachi/skills/shared/scripts/office/__pycache__/` — flagged for upstream cleanup (PR #115 below).

### Push (PR-only, no `--merge`)

- **md-deck (PR #113)** — new skill from PDLC_DEMO task ben/039. 5 files. Note: README.md not yet authored (Best Practices follow-up).
- **secops audit (PR #114)** — bumps secops v6 → v7. Adds `audit` action + `audit_artifacts.py` static-analysis scanner from task ben/041.

### Cleanup (separate PR against hitachi)

- **gitignore + pyc removal (PR #115)** — hitachi had no `.gitignore`; added one and `git rm --cached` removed the three leaked `.pyc` files.

### project.yml change

- Added third registry entry `community-zarazhangrui` recording the upstream provenance and pinned SHA (`8dca834`) for `frontend-slides`. `sync_policy: pull-only` — never push to third-party upstream.

### Held from upstream push

- `frontend-slides/*` (11 files) — third-party MIT skill from `zarazhangrui/frontend-slides`. Not GlobalLogic-authored; belongs in our project as a local install only.

### Merged 2026-05-02

- **PR #115 merged** (squash) — commit `21bd076`. Hitachi `.gitignore` added; 3 leaked `.pyc` files removed.
- **PR #114 merged** (squash) — commit `e0c7422`. secops v6 → v7 with `audit` action + `audit_artifacts.py`.
- **PR #113 merged** (squash) — commit `0b64361`. md-deck skill added to registry.

**Hitachi HEAD after sync**: `0b64361` (fast-forwarded local clone).

### Final state

`check` after merges: only the 11 expected `frontend-slides/*` entries remain `LOCAL_ONLY` (held from push by design — third-party MIT skill recorded under registry `community-zarazhangrui` with `sync_policy: pull-only`). Zero `UPSTREAM_NEWER`, zero `UPSTREAM_ONLY`.

### Local follow-ups (done)

- `/skill-creator setup` re-run — `skill-md-watch` PreToolUse + `cleanup` SessionEnd hooks registered, smoke-tested.
- `/secops setup` re-run — agent + `security-assert.sh` already in place; permissions merged (71 → 71 unique); git identity already aligned.

---

## 2026-04-28 — push + merge (sync-skills v6 → v7 → v8: closes task ben/029 Bug A + Bug B)

- Three sequential PRs in the same session, each squash-merged immediately to validate the next:
  - **PR #96** — sync-skills v6 — symlink-aware `check` content compare. Detects local symlinks and hashes link target text (no trailing newline) to mirror upstream symlink blob storage. Merge commit: `a45c928`.
  - **PR #97** — sync-skills v7 — mixed-mode symlink-aware comparison; corrects v6 regression. Selects local-side hash strategy by upstream mode (`git ls-tree`) so the canonical "local symlink → upstream regular file" pattern is no longer flagged. Verified 28→0 false positives against PDLC_DEMO. Merge commit: `3586493`.
  - **PR #98** — sync-skills v8 — `pull-file` reads from `origin/main` via git plumbing instead of the working tree (Bug A). Fetches origin first; preserves symlink mode (recreates as symlink, doesn't flatten); preserves `+x` bit for `100755` files. Merge commit: `a6958a0`.
- Hitachi HEAD after sync: `a6958a0`
- Local PDLC-DEMO files updated by manual copy of `skills/sync-skills/{scripts/sync.sh, SKILL.md, README.md}` (the script self-excludes from `pull-file`).
- Final `check` against PDLC-DEMO: zero false positives — only the 3 expected `__pycache__/*.pyc` upstream-only entries remain.
- Closes task ben/029 (both bugs).

---

## 2026-04-28 — pull (broad upstream sync — change-control internal-review tier, project-console v1.7.6, web-control 0.2.0, best-practices v15)

- Hitachi HEAD after sync: `00e53bb`
- Pulled: 47 files (3 `__pycache__/*.pyc` upstream-only entries skipped as noise)
- Highlights:
  - `change-control` 0.5.0 — new internal-review tier: `review_start/status/update/abort`, `diagnose`, `help` actions + lib (`_runtime`, `gdoc`, `internal_review`, `path_convention`); `freeze.py` updated
  - `web-control` 0.2.0 — new `actions/diagnose.py`, `actions/purge_stale.py`, `lib/python_runtime.py`; updated `lib/platform.py` and chrome install/launch scripts
  - `project-console` v1.7.4 → v1.7.6 — configurable grounding roots, two-layer standards citation, browsable skill-library roots, relative-link resolution, content-wrap fixes
  - `task` SKILL.md / README.md — capture-discipline doc refresh (UserPromptSubmit/Stop hooks retired in v23, state file at `.state/`)
  - `best-practices` v15 — new Required check `Skill content is project-agnostic` + Recommended `Skill changelogs are skill-scoped`; v14 added 4 personal-scratch checks; v13 moved Best Practices/Changelog to README.md
  - `medtech-docs` — Best Practices table now uses `Scope` column (shared/per-dhf/per-submission/cross-cutting); added Platform-DHFs-have-children + composition-manifest-referenced checks
  - `skill-creator` v5 — explicit project-agnostic HARD RULE + skill-scoped changelog format
  - `agents/project-secops.md` — agent prompt update
  - New READMEs: `trace-matrix/`, `tracker/`, `xlsx/`
- project.yml: no changes (all pulled files are updates to already-approved skills/agents)
- Follow-ups:
  - Re-run `/web-control setup` for new action symlinks
  - Re-run `/change-control setup` if using the new internal-review tier
  - Run `/project-console sync` + restart console + browser hard-refresh (per v1.7.5/v1.7.6 post-update notes)
  - Verify `tools/project-console/console.yaml` `grounding.extra_roots` includes `.claude/skills/medtech-docs/references` and `.claude/skills/dhf-manifest/data`
  - Run `/best-practices` when ready to triage new v15/v14 findings (expect new flags around project-agnostic skill content)

---

## 2026-04-27 — push (dhf-manifest dynamic project name in titles)

- Files: `skills/dhf-manifest/scripts/{_project_slug,dashboard,gap-report}.py`
- Branch: `sync/pdlc-demo-dhf-manifest-display-name-2026-04-27`
- PR: https://github.com/GlobalLogic-a-Hitachi-Company/hitachi/pull/91
- Commit: "dhf-manifest: dynamic project name in dashboard + gap-report titles"
- Status: merged (--merge requested)
- Merge commit: `b57d469eb01c124241ff85c1c098e3e9f97dbb93`
- Hitachi HEAD after sync: `b57d469`
- Trigger: small polish caught while smoke-testing the dhf-manifest pipeline on PDLC_DEMO under ben/035. Dashboard + gap-report H1 titles were the only remaining hardcoded "MedTech Project" placeholder literals — now they read the project name from `project.yml`. Output renders `# PDLC_DEMO DHF — Dashboard` on PDLC_DEMO; arthrex-pccp will render `# Arthrex PCCP DHF — Dashboard` after pull.

---

## 2026-04-27 — push (dhf-manifest output filename parameterization)

- Files: 12 across `skills/dhf-manifest/` (SKILL.md, README.md, 3× actions/, 4× scripts/, new `scripts/_project_slug.py`) + `skills/best-practices/SKILL.md` + `skills/skill-creator/SKILL.md`
- Branch: `sync/pdlc-demo-dhf-manifest-rename-2026-04-27`
- PR: https://github.com/GlobalLogic-a-Hitachi-Company/hitachi/pull/90
- Commit: "dhf-manifest: parameterize output filenames from project.yml project.name"
- Status: merged (--merge requested)
- Merge commit: `a17f9be6e111714aeddf506901a0870990c13c8f`
- Hitachi HEAD after sync: `a17f9be`
- Trigger: closes the structural follow-up to ben/032's prose-only audit. Output filenames now derive from `project.yml` `project.name` (slugified, with optional `dhf_manifest.output_prefix` override). The hardcoded `hiplink-intra-op` leaf-name branch in `build-manifest.py` is replaced with a project-supplied `dhfs[].classification.subtitle_extra` field. Skill bumped 5 → 6. The `best-practices` anonymization lint dropped the `hiplink-*` exception clause (no longer needed) and added explicit exceptions for the glossary doc + post-update changelog notes.
- Discovered + executed under PDLC_DEMO ben/033. arthrex-pccp picks up on next `/sync-skills pull`; their existing `hiplink-*` built outputs remain on disk until they delete or rerun.

---

## 2026-04-27 — push (anonymization regression-guard lint)

- Files: `skills/best-practices/SKILL.md`, `skills/skill-creator/SKILL.md`
- Branch: `sync/pdlc-demo-anonymization-lint-2026-04-27`
- PR: https://github.com/GlobalLogic-a-Hitachi-Company/hitachi/pull/88
- Commit: "best-practices + skill-creator: anonymization regression-guard"
- Status: merged (--merge requested)
- Merge commit: `696359985c2a915dd7397bf06825c9e33511afb5`
- Hitachi HEAD after sync: `6963599`
- Trigger: closes the regression-guard story for ben/032. New Required `best-practices` check greps the named-entity vocabulary across `.claude/skills/**` and `.claude/agents/**` with documented exceptions (registry URL + deferred `hiplink-*` filenames). New `skill-creator` "Anonymization (Required)" section documents the canonical glossary so future skill authors land on the rule while reading the conventions doc.
- Discovered + executed under PDLC_DEMO ben/032 Phase 4. Companion follow-up ben/033 will tighten the lint by dropping the `hiplink-*` exception once dhf-manifest output filenames get parameterized.

---

## 2026-04-27 — push (skill tree anonymization — prose-only)

- Files: 86 across 14 skills (dhf-manifest 47, docflow 11, project-console 8, change-control 5, strategy 2, advisors 1, best-practices 1, digest 1, medtech-docs 1, secops/shared 1, sync-skills 1, trace-matrix 1, web-control 1) — full list in PDLC_DEMO commits `bd2ddd3` + `3f76013`
- Branch: `sync/pdlc-demo-skill-anonymization-2026-04-27`
- PR: https://github.com/GlobalLogic-a-Hitachi-Company/hitachi/pull/87
- Commit: "skill tree: anonymize product/customer references (prose-only)"
- Status: merged (--merge requested)
- Merge commit: `56d631bdc86bcb961c48564624686bbd3380cbc0`
- Hitachi HEAD after sync: `56d631b`
- Trigger: user observed `dhf-manifest` skill carries `HipLink`/`Arthrex` references; skills meant to be reusable by any project. Phase 1 survey found 200 lines across 11 skills. Phase 2 prose pass applied locked glossary (Arthrex/GlobalLogic → MedTech Company; HipLink/Arthrex PCCP/PDLC_DEMO → MedTech Project; HipLink Pre-Op/Intra-Op/Mgmt Services → MFD A/B/C; PP3500 → PROJECT identifier-style; etc.). Programmatic strings (output filenames, leaf-name branches) verified safe or raised in PDLC_DEMO ben/033 — not touched. Built artifacts in `dhf-manifest/data/` regenerated via `build-reference.py`.
- Reconciliation: `change-control/SKILL.md` was fast-evolving upstream (v0.4 landed in #84/#85/#86 mid-task); reset local to upstream HEAD then re-applied anonymization. Net upstream diff is exactly the `PP3500` → `PROJECT` example-string change.
- Cleanup: removed `skills/secops/scripts/resolve_user.py` from the push branch — was a duplicate of `shared/scripts/resolve_user.py` and shouldn't have been introduced upstream. Force-pushed amended branch before opening PR.
- Discovered + executed under PDLC_DEMO task ben/032. Follow-up: PDLC_DEMO task ben/033 (structural rename of `hiplink-*` output filenames in dhf-manifest scripts) staged but not yet started.

---

## 2026-04-27 — push (project-console relative-link rewriter)

- Files: `skills/project-console/console/documents/renderer.py`, `skills/project-console/console/documents/router.py`, `skills/project-console/console/workflows/router.py`
- Branch: `sync/pdlc-demo-console-link-rewriter-2026-04-27`
- PR: https://github.com/GlobalLogic-a-Hitachi-Company/hitachi/pull/83
- Commit: "project-console: rewrite relative md links in rendered HTML"
- Status: merged (--merge requested)
- Merge commit: `8ddfbe1db08c141cdfa9cc5b2639fff0c28842e0`
- Hitachi HEAD after sync: `8ddfbe1`
- Trigger: every cross-doc link in rendered markdown (qms-index → SOPs, DHF stubs → parent QMS templates, README cross-links) 404'd because the renderer emitted raw author-written hrefs that the browser resolved against `/documents`. Fix is a post-processing pass in `_render_markdown` that resolves relative `<a href>` / `<img src>` against the source doc's virtual dir and rewrites to `/documents/view/<vp>` (links) or `/documents/raw/<vp>` (images). Absolute / protocol-relative / root-relative / anchor-only / `..`-escape links pass through unchanged.
- Discovered under task ben/031 while reviewing the QMS scaffold from ben/022. Same bug shipped in arthrex-pccp at 1.7.6 — fix benefits both projects on next pull.

---

## 2026-04-22 — pull (docflow hook bash 3.2 fix + accumulated skill updates)

- Hitachi HEAD after sync: `219d46d`
- Pulled: 20 files
  - `agents/project-secops.md` (symlink-follow-through; sync-skills still flags as UPSTREAM_NEWER — known bug: `check` compares upstream symlink-target text vs local resolved-content sha)
  - `skills/digest/{SKILL.md, hooks/session-briefing.sh}` (→ v6 — sync-check on brief builds)
  - `skills/docflow/SKILL.md` + agents (adopter, converter, reviewer), `hooks/block-direct-conversion.sh`, `references/classification-taxonomy.md`, `templates/frontmatter-project.md`, `scripts/splice_hyperlinks.py` (new) — v27 → v29 (hyperlink preservation + link-count validation, F11-CLASSIFY markers Required, **bash 3.2 parser bug workaround in block-direct-conversion.sh — task ben/092**)
  - `skills/medtech-docs/SKILL.md` (→ v22 — `init` invokes `/dhf-manifest init` when installed)
  - `skills/project-console/console/{app.py, trace_matrix/router.py, web/static/console.css, web/templates/_base.html, documents_explorer.html, index.html, trace_matrix_view.html}` (→ v1.4.1)
  - `skills/task/SKILL.md` (v18 → v20 — PERMANENT RULES template + phase-end batching clarification)
- Trigger: after fast-forward pulling 19 commits on PDLC_DEMO `main`, the newly-installed `.claude/hooks/block-direct-conversion.sh` (symlink to the docflow skill hook) had a heredoc-inside-command-substitution pattern that macOS bash 3.2 can't parse — blocked every Bash tool call. Bypassed temporarily via `.state/docflow-active`; removed after the upstream fix landed.
- Caveat: on first pass, `pull-file` copied from the stale hitachi working-tree checkout (`e027eba`) and reported 13 files as "deleted-locally (upstream removed)" when upstream-head actually had them — fast-forwarded the hitachi working copy to `origin/main` (`219d46d`) and re-pulled. Root cause: `check` fetches `origin/main` but `pull-file` reads from the working tree. Logged as a sync-skills bug to file separately.
- project.yml: no changes — all affected skills already in `approved_skills`.
- Follow-ups (offered):
  - `/project-console sync` to regenerate `tools/project-console/start.sh`+`run.sh` against v1.4.1 (new templates, `--reload-exclude` patterns, BSD `xargs` fix)
  - `/task setup` to refresh `.claude/hooks/task-activate.sh` copy against v20 source
  - `/docflow setup` to confirm bypass marker lives at `.state/docflow-active` (already the case)
  - 22 `LOCAL_ONLY` files remain — task 024 (Unified Assistant Drawer) partials + advisor agents not yet pushed. Separate push decision.
- **Outcome note (added 2026-04-22 in the follow-on push session):** The project-console files in this pull were momentarily reverted to v1.4.1 in `origin/main`. A parallel session's `/sync-skills push` (the follow-on entry below) re-landed v1.5.0 on both hitachi and PDLC_DEMO, carrying the Overview section + unified Assistant drawer. Net effect across both entries: hitachi 1.4.1 → 1.5.0; PDLC_DEMO picks up the other pulled skill updates (docflow/task/medtech-docs/digest) AND keeps 1.5.0 project-console.

---

## 2026-04-22 — push (project-console 1.5.0 — Overview + unified Assistant drawer)

- Files: 17
  - `skills/project-console/VERSION` (1.4.1 → 1.5.0)
  - `skills/project-console/SKILL.md` (1.5.0 changelog entry)
  - `skills/project-console/console/overview/{__init__,router}.py` (new module)
  - `skills/project-console/console/assistant/{__init__,router}.py` (new module)
  - `skills/project-console/console/app.py` (wires overview_router + assistant_router + middleware overview_nav flag)
  - `skills/project-console/console/trace_matrix/router.py` (swapped custom drawer endpoint for generic)
  - `skills/project-console/console/web/static/assistant.js` (new — generic drawer JS)
  - `skills/project-console/console/web/static/docs-assistant-glue.js` (new — Documents-page wiring)
  - `skills/project-console/console/web/static/console.css` (new `.overview-*` + `.pc-assistant-*` rules)
  - `skills/project-console/console/web/templates/_assistant_drawer.html` (new)
  - `skills/project-console/console/web/templates/_base.html` (conditional Overview nav)
  - `skills/project-console/console/web/templates/documents_explorer.html` (mounts generic drawer)
  - `skills/project-console/console/web/templates/index.html` (conditional Overview tile)
  - `skills/project-console/console/web/templates/overview.html` (new)
  - `skills/project-console/console/web/templates/trace_matrix_view.html` (swapped to generic drawer)
- Branch: `sync/pdlc-demo-console-overview-assistant-drawer-2026-04-22`
- PR: https://github.com/GlobalLogic-a-Hitachi-Company/hitachi/pull/62
- Status: merged (--merge requested)
- Merge commit: `dd65333`
- Hitachi HEAD after sync: `dd65333`
- Follow-ups: sister project (Arthrex PCCP) can `/sync-skills pull` to receive 1.5.0 and the Overview section will light up if `project-overview.{pdf,pptx,md}` exists at repo root.

---

## 2026-04-20 — pull (bulk sync to pick up `.claude/state/` → `.state/` relocation + docflow tripwire)

- Hitachi HEAD after sync: `7c6e388`
- Pulled: 35 files
  - `agents/project-secops.md` (symlink unchanged — skill-side content identical; false-positive drift from sync.sh comparing across registries' symlinks)
  - `skills/best-practices/SKILL.md` (10 → 12 — new task-auto-create flow for `/best-practices fix`)
  - `skills/digest/{README,SKILL,hooks/session-briefing.sh,scripts/build_changelog.py}` (v4 → v5 — state relocation)
  - `skills/docflow/{README,SKILL,agents/converter,agents/refresher,templates/frontmatter-project,agents/adopter,agents/reviewer,hooks/block-direct-conversion.sh,references/classification-taxonomy.md}` (14 → 27 — new PreToolUse tripwire, T1 composite-table rules, shlex tokenization, state relocation)
  - `skills/lessons/SKILL.md` (1 → 2 — doc-only path update)
  - `skills/medtech-docs/{SKILL,templates/readme-strategies,scripts/render-sentinels.py,templates/claude-md-task-discipline,templates/rule-sentinel-blocks}` (17 → 21 — sentinel-block rendering infrastructure)
  - `skills/skill-creator/{README,SKILL,templates/skill-md}` (2 → 3)
  - `skills/strategy/{SKILL,agents/assembler,agents/scanner}` (10 → 11 — Domain Registry now rendered from `project.yml:strategy_domains[]`)
  - `skills/task/{README,SKILL,hooks/capture-check,hooks/capture-signals,hooks/check-active-task,hooks/session-cleanup,hooks/task-activate,tests/test-task-gate.sh}` (17 → 18 — state relocation, belt-and-suspenders `.state/docflow-active` cleanup)
- Post-update actions performed:
  - Created `.state/` at project root; migrated 3 files from `.claude/state/`: `active-tasks-3c4ade18-b44a-42ca-8fba-83930610b3bc.txt`, `briefing-last-shown-ben.txt`, `digest-llm-cache.json`. Session's active-task tracking survives the migration (verified via `task-activate.sh list`).
  - `.gitignore`: added `.state/` above the existing `.claude/state/` line (kept both).
  - Refreshed `.claude/hooks/task-activate.sh` (copy, not symlink) from v18 source — now reads state from `.state/`.
  - Installed docflow tripwire: `.claude/hooks/block-direct-conversion.sh` symlinked to skill source; registered `PreToolUse "Bash"` in `.claude/settings.json` via `register-hook.sh`. Smoke-tested: `pandoc --version` allowed (exit 0), `pandoc foo.docx -o foo.md` denied (exit 2) with the `/docflow` routing message.
  - 3 `/skill setup` re-runs subsumed by the manual steps above — all hooks already correctly symlinked to skill sources, so no full setup invocation was needed (v18/v5/v27 behavior activates on next tool call).
- project.yml: no changes — all affected skills already in `approved_skills`.
- Follow-ups:
  - 13 `LOCAL_ONLY` agents under `agents/` remain — these are project-console materialized personas (clinical-affairs, cybersecurity, core-team-panel, etc.); project-owned, not pushed upstream.
  - `strategy` v11 sentinel-block rendering is documented but not wired — `/strategy domains add|edit|remove` + `project.yml:strategy_domains[]` seeding + `/best-practices` drift check are all listed as upstream follow-ups in the v11 changelog.

---

## 2026-04-20 — push --merge (ben/020 secops v3 identity alignment)

- Files: `skills/secops/SKILL.md`, `skills/secops/scripts/resolve_user.py`
- Branch: `sync/pdlc-demo-secops-v3-2026-04-20`
- PR: https://github.com/GlobalLogic-a-Hitachi-Company/hitachi/pull/45
- Commit subject: "secops v3: roster-driven git identity alignment"
- Status: merged (`--merge` requested)
- Merge commit: `077d4b4`
- Hitachi HEAD after sync: `077d4b4`
- Notes: Adds `scripts/resolve_user.py` — YAML-roster parser with four-heuristic identity match (email / single-member / name-fuzzy / `$USER`) and `--align-git` to write repo-local git config. Paired with the digest skill (PR #44), which consumes the same helper via `--task-folder` for its SessionStart throttle state key. No upstream regressions; `/secops setup` gains step 6 (align-git) idempotently.

---

## 2026-04-20 — push --merge (ben/019 + ben/021 digest skill + medtech-docs template)

- Files: 7
  - 6 under `skills/digest/` — SKILL.md, README.md, VERSION, hooks/session-briefing.sh, scripts/digest.py, scripts/build_changelog.py
  - 1 under `skills/medtech-docs/templates/` — `changelog-project.md` (CHANGELOG.md seed)
- Branch: `sync/pdlc-demo-digest-skill-2026-04-20`
- PR: https://github.com/GlobalLogic-a-Hitachi-Company/hitachi/pull/44
- Commit subject: "Add digest skill + changelog-project template"
- Status: merged (`--merge` requested)
- Merge commit: `5f5bb9c`
- Hitachi HEAD after sync: `077d4b4` (after the paired PR #45 also merged)
- Notes: New `/digest` skill with two actions (`daily` SessionStart briefing + `log` CHANGELOG.md appender). Readable format: bold headline + optional body line + muted italic trace footer. Hybrid source — mechanical commit-body extraction by default, batched `claude -p` call on `--llm` (auto-on for `--retrospective`) for polished rewrites. Critical: sub-invocation runs with `cwd=/tmp` + stripped `CLAUDE_*` env to isolate from project context/hooks. Per-SHA LLM cache at `.claude/state/digest-llm-cache.json`. Medtech-docs template seeded automatically by `/digest setup`. Built and dogfooded on PDLC_DEMO.

---

## 2026-04-20 — pull (bulk sync, 53 files)

- Hitachi HEAD after sync: `765d3b6` (2 commits ahead of `origin/main` — unpushed docflow v3→v14 work; `sync.sh pull-file` reads working tree, so we picked up the unpushed content intentionally)
- Pulled: 53 files
  - Version bumps: task (14→17), secops (1→2), docflow (2→14), best-practices (9→10), medtech-docs (14→17), skill-creator (1→3), project-console (1.0.2→1.4.1)
  - New skill bundle: `skills/advisors/` (20 files — 12 persona agents + 2 panels + loader lib + render-grounding script + tests + overlay-defaults)
  - New shared references: `skills/shared/agent-design-principles.md`, `skills/shared/task-content-scanner.md`
  - New skill-creator templates: `hook-template.sh`, `readme-skill.md`, `skill-md.md`
  - `agents/project-secops.md` registry-root blob is now a symlink pointing at `skills/secops/agents/` (cp follows the link, so local content matches the skill source)

- Project Impact Analysis (mandatory per sync-skills v3 Step 5b):
  - **task v15 narrows task-gate exempt list.** `.claude/skills/**`, `.claude/agents/*`, `.claude/hooks/*`, CLAUDE.md, and `project.yml` now require an active task for Edit/Write. Exempt: `tasks/*`, `.claude/state/*`, `.claude/settings*.json`, `.claude/sync-log.md`, `.claude/MEMORY.md`, `.claude/memory/*`.
  - **task v16 fixes a silent Linux/WSL bug** where `task-activate.sh remove` was a no-op (GNU sed `-i ''` mismatch). Required a fresh copy of the script into `.claude/hooks/` — ran `/task setup`, which refreshed the copy.
  - **secops v2** no-op on Linux (was a macOS-only fix).
  - **best-practices v10 adds Required check** "Per-skill agents installed as symlinks". `/secops setup` (this run) converted `.claude/agents/project-secops.md` from a regular file into a symlink pointing at `../skills/secops/agents/project-secops.md`. Note: secops SKILL.md v2 still prescribes `cp`; there's a latent contradiction with best-practices v10 that should be resolved in a future secops bump.
  - **medtech-docs v17** adds Required check "Every docs folder has README" and new `update-external-references` action (v15) + rubric-vs-exclusion conflict surfacing (v16). Additive — no regeneration needed, but `/best-practices` may surface new findings for any docs/ folder lacking a README.
  - **project-console 1.4.1** scaffold template updates — ran `/project-console sync`, which regenerated `tools/project-console/run.sh` and `start.sh`. `run.sh` now reads `server.host`/`server.port` from `console.yaml` and passes `--reload-exclude` for `trace-matrix/**`, `.venv/**`, `__pycache__/*`, `.data/*`; `start.sh` is new (idempotent launcher) and no longer uses GNU-only `xargs -r`.
  - **skill-creator v2** codifies agent-symlink mandate. No project-owned files derived from its templates yet — no action.
  - **advisors skill (new)** — not activated. Requires `/advisors init` to install the agent symlinks into `.claude/agents/` and seed an `advisors:` block in `project.yml`. Deferred to user.

- Post-update actions run this session:
  - `/task setup` — refreshed `.claude/hooks/task-activate.sh` (v16 bugfix), all 5 hooks already registered
  - `/secops setup` — converted `project-secops.md` to symlink, hook + permissions already wired
  - `/project-console sync` — updated `run.sh` + `start.sh` to 1.4.1 template

- Post-update follow-ups completed later in the same session (under task 018):
  - Added `advisors`, `change-control`, `trace-matrix` to `project.yml` `security.approved_skills` (closed 3-skill secops drift)
  - `/advisors init` — installed 13 persona-advisor symlinks into `.claude/agents/`, seeded `advisors:` block in `project.yml` (enabled: regulatory-affairs, clinical-affairs, risk-management), regenerated grounding blocks
  - `/project-console start` — skipped, console not running
  - `/best-practices` audit — ran against full multi-DHF (10 DHFs), identified 16 Required FAILs (mostly pre-existing debt exposed by new v17 Required-severity checks)
  - Hygiene pass closed all 16 Required FAILs: CLAUDE.md Project Overview / For Claude / Task-First / Lessons sections, new `setup.md` (security posture), new `tasks/README.md` + `tasks/lessons-ledger.md`, 5 standards files got Verification Checks stubs, 6 missing docs folder READMEs created, 261 stub DHF READMEs got `## Conventions` via scripted pass, `.claude/skills/project-console/console/**` pycache cleaned (local-only, never tracked), 510(k) composition manifest updated to use actual folder names + 5 stub design-control folders created so every referenced piece resolves. Remaining debt is all WARN severity (Recommended). (agents-as-symlinks, docs-folder-has-README)

---

## 2026-04-15 — push --merge (task 017 change-control skill scaffold)

- Files: 20 (`skills/change-control/` — full scaffold)
- Branch: `sync/pdlc-demo-change-control-2026-04-15`
- PR: https://github.com/GlobalLogic-a-Hitachi-Company/hitachi/pull/19
- Commit subject: "Add change-control skill scaffold (design-captured, stubs)"
- Status: merged (`--merge` requested)
- Merge commit: `0588d71`
- Hitachi HEAD after sync: `0588d71`
- Notes: Design-captured scaffold only. Strategy C hybrid freeze-point model (draft → frozen → released), PreToolUse hook consent prompt, 6 extensibility seams + 8 open questions documented in SKILL.md. No live connectors yet.

---

## 2026-04-15 — push --merge (task 016 trace-matrix skill + project-console Trace Matrix section)

- Files: 23
  - 16 new files under `skills/trace-matrix/` — full v2 skill package (adapter_api.py, build.py, analyze.py, emit.py, graph.py, 5 default parsers, markdown_table.py, SKILL.md, .gitignore)
  - 5 new files under `skills/project-console/console/trace_matrix/` + `web/templates/` — loader, router, two Jinja templates, package init
  - 2 modified files in `skills/project-console/` — `console/app.py` (router include) + `console/web/templates/_base.html` (nav link). Both diffs purely additive; no upstream advances to merge.
- Branch: `sync/pdlc-demo-trace-matrix-2026-04-15`
- PR: https://github.com/GlobalLogic-a-Hitachi-Company/hitachi/pull/18
- Commit subject: "Add trace-matrix skill + project-console Trace Matrix section"
- Status: merged (`--merge` requested)
- Merge commit: `fed4644`
- Hitachi HEAD after sync: `fed4644` (→ advanced to `0588d71` by the subsequent change-control push)
- Notes: Adapter-generation model — skill ships sensible defaults plus a `rational_check` at init time; when defaults fail on a source doc, `/trace-matrix init` generates a per-project adapter file into `tools/project-console/trace-matrix/adapters/`. Build is always deterministic. Sidecar bumped to v1.1 with `source_files` + per-layer `warnings`. Console section is loose-coupled: reads JSON sidecars only, never imports from the skill. Includes the Systems Engineering Assistant drawer (resizable, localStorage-persisted threads, inline vanilla-JS markdown renderer with table support).
- Pre-push hygiene: scrubbed `__pycache__` from `skills/project-console/console/`. `sync.sh check` walks the filesystem directly and doesn't honor `.gitignore`, so build artifacts would otherwise have been staged into the hitachi PR. Filed as a follow-up for `sync-skills` v4.

---

## 2026-04-14 — push --merge (project-console 1.0.2 — default panels + assistant-framing rename)

- Files: 17 (13 rewritten persona templates + 2 new panels + SKILL.md + scaffold.py + VERSION)
  - `skills/project-console/agents/templates/` — all 12 persona files + `_group.md` rewritten with assistant framing. Titles suffixed "Assistant" (solo) or "Advisory Panel" (panels). System prompts rewritten from "You are the X lead" to "You are an AI assistant supporting the X team... You help the human X leads by...". STAY IN CHARACTER clauses rewritten to "never claim to BE the lead or commit the program to anything."
  - `skills/project-console/agents/templates/core-team-panel.md` — new, 5 members (PM + RA + Clinical + QE + R&D)
  - `skills/project-console/agents/templates/design-review-panel.md` — new, 6 members (Systems + R&D + V&V + HFE + Risk + QE), with instructions for projects to add cybersecurity if relevant
  - `skills/project-console/scripts/scaffold.py` — extended `sync` action to copy new agent templates into existing installs (previously `sync` only rewrote `run.sh`)
  - `skills/project-console/SKILL.md` — 1.0.2 changelog entry, corrects 1.0.1 uvicorn reload claim
  - `skills/project-console/VERSION` — 1.0.2
- Branch: `sync/pdlc-demo-project-console-1.0.2-default-panels-2026-04-14`
- PR: https://github.com/GlobalLogic-a-Hitachi-Company/hitachi/pull/17
- Commit: "project-console 1.0.2: default Core Team + Design Review panels"
- Status: merged (--merge requested)
- Merge commit: `fca1db9`
- Hitachi HEAD after sync: `fca1db9`
- Context: User feedback during PDLC testing flagged that the original "You are the X lead" framing risked implying the AI was replacing the real team. The 1.0.2 rename makes the support-not-substitute relationship unambiguous at every response. Same version also ships the default panels requested earlier in the session.

---

## 2026-04-14 — push --merge (project-console 1.0.1 — macOS/Windows junk filter)

- Files: 3
  - `skills/project-console/console/documents/tree.py` — new `_is_hidden()` helper centralizing the junk-file filter (dotfiles + `Icon\r` + `Icon` + `Thumbs.db` + `desktop.ini` + `._*` + `__MACOSX`); applied at all three walker sites (`list_children`, `_dir_has_any_children`, `_children`)
  - `skills/project-console/VERSION` — bumped to 1.0.1
  - `skills/project-console/SKILL.md` — 1.0.1 changelog entry with post-update annotation
- Branch: `sync/pdlc-demo-project-console-1.0.1-icon-filter-2026-04-14`
- PR: https://github.com/GlobalLogic-a-Hitachi-Company/hitachi/pull/16
- Commit: "project-console 1.0.1: hide macOS Icon files + Windows junk from docs tree"
- Status: merged (--merge requested)
- Merge commit: `78da92c`
- Hitachi HEAD after sync: `78da92c`
- Context: Bug reported from Arthrex PCCP immediately after pulling v1 — `Icon\r` files at several directory roots were cluttering the documents explorer. Fix landed same day. Project-side action: none (uvicorn `--reload` picks up the updated `tree.py` on next launch).

---

## 2026-04-14 — push --merge (project-console v1 — new reusable FastAPI console skill)

- Files: 54 (first release)
  - `skills/project-console/SKILL.md` — v1.0.0 initial. Actions: init, sync, theme <url>, run, status. Company-agnostic; ships light/dark theme packs + scrape-and-materialize `theme` action + 10 medtech persona templates + glob-scan dashboard discovery. Config in `tools/project-console/console.yaml` (project.yml never touched). PYTHONPATH launcher pattern so sync-skills pull is immediately effective. Three file ownership classes, narrow committed manifest.
  - `skills/project-console/README.md` — human-facing design & architecture doc
  - `skills/project-console/VERSION` — 1.0.0
  - `skills/project-console/.gitignore` — blocks `__pycache__/`, `*.pyc`
  - `skills/project-console/console/` — 18 files: FastAPI app (app.py, config.py, themes.py, auth.py, chat/, documents/, dashboards/ with discovery.py, web/templates/, web/static/)
  - `skills/project-console/themes/{light,dark}/` — 4 files: theme.yaml + footer.html.j2 each
  - `skills/project-console/agents/templates/` — 11 files: _group.md + 10 personas (regulatory, clinical, quality, systems, risk, HFE, R&D, V&V, cybersecurity, post-market)
  - `skills/project-console/scripts/scaffold.py` — init/sync/status implementation
- Branch: `sync/pdlc-demo-add-project-console-2026-04-14`
- PR: https://github.com/GlobalLogic-a-Hitachi-Company/hitachi/pull/15
- Commit: "Add project-console skill — scaffold + theme + dashboards"
- Status: merged (--merge requested)
- Merge commit: `a8e817a`
- Hitachi HEAD after sync: `a8e817a`
- Project context: Built in task 015. PDLC_DEMO's hand-built `tools/project-console/` extracted, genericized, and migrated onto the skill-driven version in the same task. Config contract dry-validated against Arthrex PCCP `project.yml` before push (all required fields present; sister-project compat bar satisfied).

---

## 2026-04-14 — push --merge (medtech-docs v16: rubric-vs-exclusion conflict surfacing)

- Files: 4
  - `skills/medtech-docs/SKILL.md` — bumped 15 → 16; new Step 2.5 in `update-external-references` action that detects rubric-vs-existing-exclusion conflicts and surfaces them with IMPORT / KEEP EXCLUDED / DEFER resolution; new v16 changelog entry
  - `skills/medtech-docs/templates/readme-fda-guidance.md` — added Scope Qualifier column to Evaluated — Not Applicable table
  - `skills/medtech-docs/templates/readme-standards.md` — added Scope Qualifier column to Evaluated — Not Required table
  - `skills/medtech-docs/templates/readme-industry-frameworks.md` — added Scope Qualifier column to Evaluated — Not Required table
- Branch: `sync/pdlc-demo-medtech-docs-v16-2026-04-14`
- PR: https://github.com/GlobalLogic-a-Hitachi-Company/hitachi/pull/14
- Commit: "medtech-docs v16: surface rubric-vs-existing-exclusion conflicts"
- Status: merged (--merge requested)
- Merge commit: `2d88ce6`
- Hitachi HEAD after sync: `2d88ce6`
- Source task: PDLC_DEMO `tasks/ben/012-medtech-docs-update-external-references.md` (closes the rubric-override follow-up captured under v15)

---

## 2026-04-14 — push --merge (medtech-docs v15: update-external-references action)

- Files: 4
  - `skills/medtech-docs/SKILL.md` — bumped 14 → 15; new `update-external-references` action; updated frontmatter description
  - `skills/medtech-docs/templates/readme-fda-guidance.md` — full rewrite from "applicability reports" model to "distilled copies + linked originals" model (model B)
  - `skills/medtech-docs/templates/readme-standards.md` — added Original Source column to Distilled Standards table
  - `skills/medtech-docs/templates/readme-industry-frameworks.md` — added Spec URL column to Active Frameworks table
- Branch: `sync/pdlc-demo-medtech-docs-v15-2026-04-14`
- PR: https://github.com/GlobalLogic-a-Hitachi-Company/hitachi/pull/13
- Commit: "medtech-docs v15: add update-external-references action"
- Status: merged (--merge requested)
- Merge commit: `d30a7f3`
- Hitachi HEAD after sync: `d30a7f3`
- Source task: PDLC_DEMO `tasks/ben/012-medtech-docs-update-external-references.md`
- Known follow-up not in this PR: rubric-vs-existing-exclusion conflict surfacing (IHE Profiles case). Tracked on task 012.

---

## 2026-04-13 — push --merge (sync-skills v3: mandatory project impact analysis on pull)

- Files: 1
  - `skills/sync-skills/SKILL.md` — adds mandatory Step 5b Project Impact Analysis to the `pull` action; new v3 changelog entry with post-update annotation
- Branch: `sync/pdlc-demo-sync-skills-pull-impact-analysis-2026-04-13`
- PR: https://github.com/GlobalLogic-a-Hitachi-Company/hitachi/pull/12
- Commit: "sync-skills v3: mandatory project impact analysis on pull"
- Status: merged (--merge requested)
- Merge commit: `b19debe`
- Hitachi HEAD after sync: `b19debe`

---

## 2026-04-13 — pull

- Hitachi HEAD after sync: `a908aa2`
- Pulled: 1 file
  - `skills/secops/SKILL.md` — adds `version: 1` / `updated: 2026-04-12` YAML frontmatter so `/best-practices` "Skills are versioned" check passes (upstream PR #11, commit `a908aa2`)
- Analysis: trivial, additive, no behavior change. No setup re-run needed. No project action required beyond the pull itself. Next `/best-practices audit` will flip secops "versioned" check FAIL → PASS.
- project.yml: no changes
- Follow-ups: none

---

## 2026-04-13 — push --merge (task 009: shared strategy docs + sub-DHF → DHF rename)

- Files: 19 (18 edited, 1 new via rename, 1 deleted via rename)
  - medtech-docs v14 SKILL.md + 6 readme templates + new `readme-dhf.md` (rename of `readme-sub-dhf.md`)
  - strategy v10 SKILL.md + scanner.md + assembler.md + default-strategy.md + regulatory-strategy.md
  - tracker v5 SKILL.md
  - best-practices v9 SKILL.md (rename pass)
  - task v14 SKILL.md (rename pass)
  - docflow v2 SKILL.md + README.md (rename pass)
  - Deleted: `readme-sub-dhf.md` (replaced by `readme-dhf.md`)
- Branch: `sync/pdlc-demo-shared-strategy-2026-04-13`
- PR: https://github.com/GlobalLogic-a-Hitachi-Company/hitachi/pull/10
- Commit: "Shared strategy docs + sub-DHF → DHF rename"
- Status: merged (--merge requested)
- Merge commit: `54cc8edd76b311cbd331cc3b6a8991ccbd7d340a`
- Hitachi HEAD after sync: `54cc8ed`
- Follow-ups: run `/best-practices audit` on PDLC_DEMO to verify compliance with the updated v9/v10/v14 skills

---

## 2026-04-13 — push --merge (task 007: topology-aware skills)

- Files: 18
  - `agents/project-secops.md`
  - `skills/medtech-docs/SKILL.md` + 7 templates (readme-sub-dhf, readme-clinical, readme-postmarket, readme-risk-management, readme-cybersecurity, readme-strategies, readme-design-controls)
  - `skills/best-practices/SKILL.md`
  - `skills/strategy/SKILL.md` + `agents/scanner.md` + `agents/assembler.md`
  - `skills/tracker/SKILL.md`
  - `skills/task/SKILL.md`
  - `skills/docflow/SKILL.md` + `README.md`
  - `skills/secops/templates/permissions.json`
- Branch: `sync/pdlc-demo-topology-2026-04-13`
- PR: https://github.com/GlobalLogic-a-Hitachi-Company/hitachi/pull/9
- Commit: "Topology-aware skills: unified sub-DHF shape"
- Status: merged (--merge requested)
- Merge commit: `58e601debb2e90f691a03f0dafb96653b97373a4`
- Hitachi HEAD after sync: `58e601d`
- Follow-ups: none — closes task 007

---

## 2026-04-12 — pull (task v11 + new secops skill)

- Hitachi HEAD after sync: `03f5849`
- Pulled: 8 files
  - `skills/manifest.md` — registry index updated for task v11 and new secops skill
  - `skills/task/SKILL.md` — bumped to v11; setup grew from 8 to 12 steps (now symlinks `session-env.sh` + `session-cleanup.sh` and registers SessionStart/SessionEnd hooks)
  - `skills/task/hooks/session-env.sh` — moved into task skill (was previously in `.claude/hooks/`)
  - `skills/task/hooks/session-cleanup.sh` — moved into task skill
  - `skills/secops/SKILL.md` — new skill v1 packaging the security posture
  - `skills/secops/agents/project-secops.md` — agent moved from registry `agents/` to `skills/secops/agents/`
  - `skills/secops/hooks/security-assert.sh` — new SessionStart hook (16 security checks, cached in SECOPS.md)
  - `skills/secops/templates/permissions.json` — canonical 70-entry Bash/Read/Edit/Write allow list
- Setup re-runs:
  - `/task setup` — symlinked `session-env.sh` + `session-cleanup.sh` into `.claude/hooks/`; registered SessionStart and SessionEnd hooks (PreToolUse task gate already registered, was a no-op).
  - `/secops setup` — copied agent into `.claude/agents/project-secops.md` (replaced the orphan at the same path); symlinked `security-assert.sh`; registered SessionStart hook; merged 70 entries into `permissions.allow` (0 already present).
- `project.yml` — added `secops` to `security.approved_skills`. `approved_agents` already contained `project-secops`.
- Note: hitachi local checkout was 1 commit behind `origin/main` at the start of the run; ran `git pull --ff-only` mid-flow because `sync.sh pull-file` reads from the working tree, not `origin/main`. Worth flagging upstream — first attempt silently no-op'd six pulls.
- Follow-ups: start a new session to fire `security-assert.sh` for the first time (or run `/secops check`).

---

## 2026-04-12 — pull

- Hitachi HEAD after sync: `8dacc72` ("Update best-practices and medtech-docs with registry sync improvements (#4)")
- Pulled: 2 files
  - `skills/best-practices/SKILL.md` — `audit` and `sync` actions now prefer `local_path` from `project.yml` before `gh` CLI / raw URL; `sync` also runs `git pull --ff-only` on the local clone first. Pure improvement, benefits us now that we already have `local_path` set.
  - `skills/medtech-docs/SKILL.md` — `init` template evolved: new `device_family` field in `project:` block; `local_path` added to hitachi registry template; `registries.hitachi.skills` list alphabetized and extended with `lessons`, `strategy`, `sync-skills`, `task`, `tracker`; `approved_skills` now auto-populated from registry skills lists; new `{{DEVICE_FAMILY}}` and `{{APPROVED_SKILLS}}` substitutions; CLAUDE.md manifest table row for `registries:` mentions `local_path`.
- Project alignment follow-ups (done):
  - **`project.yml`** — alphabetized `registries.hitachi.skills` and added `sync-skills` (now in the upstream registry after PR #3/#4). Rebuilt `approved_skills` as the union of anthropic builtin + hitachi registry skills (13 entries, alphabetized). Added a comment noting the list should mirror the registries' skills lists.
  - **`CLAUDE.md`** — updated the `registries:` row in the project manifest table to mention `local_path` for clone-based sync (matches new template wording).
- No new `### setup` actions introduced by this pull, no new best-practices checks that would break our audit.
- Upstream commit was authored by this user from another project (`arthrex-pccp` task 047) — same pattern we used in PR #2 (Arthrex genericization).

---

## 2026-04-12 — push --merge

- Files: `skills/sync-skills/SKILL.md`, `skills/sync-skills/scripts/sync.sh`
- Branch: `sync/pdlc-demo-add-sync-skills-2026-04-12`
- PR: https://github.com/GlobalLogic-a-Hitachi-Company/hitachi/pull/3
- Commit subject: "Add sync-skills skill for bidirectional registry sync"
- Status: merged (`--merge` requested)
- Merge commit: `2d5e7c3`
- Hitachi HEAD after sync: `2d5e7c3`
- Notes: First publication of `sync-skills` to the registry. Dogfooded — used `/sync-skills push --merge` to upstream itself.

---

## 2026-04-12 — baseline

- Hitachi HEAD: `4e54855` (post-merge of PR #2 "Genericize project-specific references in skills")
- Local skills installed from hitachi: best-practices, docflow, lessons, medtech-docs, skill-creator, strategy, task, tracker
- Local agents installed from hitachi: project-secops
- Project-local skill (not in hitachi yet): **sync-skills** — added during PDLC_DEMO task 008
- `check` output: clean (zero `UPSTREAM_ONLY`, zero `UPSTREAM_NEWER`; one `LOCAL_ONLY` for `sync-skills` itself, excluded from the diff by design)
- Follow-ups: consider pushing `sync-skills` upstream once exercised in this project

## 2026-04-27 — pull

- Hitachi HEAD after sync: `731b09f`
- Pulled: 284 files (incl. 1 agent symlink restoration)
  - **Modified existing skills:** digest, docflow, lessons, project-console, secops, strategy, task, shared, agents/project-secops
  - **New skills installed:** dhf-manifest, web-control, docx, pdf, pptx, xlsx
  - **New supporting libraries:** skills/shared/scripts/office/* (soffice, pack, unpack, validate, validators, schemas)
  - **Major content additions:** docflow doc-type-packs (24 packs), mermaid + table rule packs, new agents (interpret_image, structure_body, structure_requirement_body)
- Skipped: 3 LOCAL_ONLY (push candidates) — `skills/secops/scripts/resolve_user.py`, `skills/task/hooks/{capture-check,capture-signals}.sh` (the latter two are deprecated by task v23)
- project.yml: needs `dhf-manifest` and `web-control` added to `security.approved_skills`
- Follow-ups required:
  - Run `/task setup` — v23 migration removes orphan `capture-signals.sh` + `capture-check.sh` symlinks and their `settings.json` hook entries
  - Run `/secops setup` — v3+ git-identity alignment via `resolve_user.py`
  - Run `/project-console sync` then `/project-console start` — scaffold is at 1.4.1, skill is at 1.7.6 (Overview section, Unified Assistant drawer, tiered grounding, footnote citations, sticky auto-scroll, configurable grounding roots, browsable skill-library roots)
- Follow-ups optional:
  - `/dhf-manifest init` to bootstrap the new sibling-of-/trace-matrix manifest skill
  - `/web-control setup` if/when a consumer skill needs Chrome automation

## 2026-05-02 — push (md-deck v0.5 + frontend-slides registration)

- Files: 43
  - md-deck (5): SKILL.md, scripts/build.py, scripts/classify.py, scripts/creative.py, scripts/distill.py
  - frontend-slides (38): SKILL.md, STYLE_PRESETS.md, viewport-base.css, animation-patterns.md, html-template.md, README.md, LICENSE, .pinned-sha, components/ (16 READMEs + _v04-components.css), presets/bold-signal.css, creative-palette.md, scripts/{deploy.sh, export-pdf.sh, extract-pptx.py}
- Branch: `sync/pdlc-demo-md-deck-v0.5-creative-agents-2026-05-02`
- PR: https://github.com/GlobalLogic-a-Hitachi-Company/hitachi/pull/116
- Commit: "md-deck v0.5 + frontend-slides shared layer + creative agent slots"
- Status: merged
- Merge commit: `58738c1`
- Hitachi HEAD after sync: `58738c1`
- Provenance: PDLC_DEMO task ben/042; local commits 946e710 → e9e5386 → 57298c8 → a185bfb

## 2026-05-13 — pull

- Hitachi HEAD: `d3c3429` (checkout 0 behind / 0 ahead of origin/main)
- Pulled: 0 files — nothing in the auto-pull bucket.
- `check --analyzed` found 18 UPSTREAM_NEWER files, all cases where **local is the newer/better version**:
  - **12 agents** (`agents/*.md` — clinical-affairs, core-team-panel, cybersecurity, design-review-panel, human-factors, post-market, program-manager, quality-engineering, rd-lead, risk-management, systems-engineering, vnv-lead) → `BOTH_DIVERGED`. Local has the **three-tier `canonical_roles:` grounding** refactor (committed `620e15e`, 2026-04-20); hitachi's `3393bab` (2026-04-23) *added* these agents to the registry for the first time but sourced the **older `context:`/`sources:` glob-list format** from the Arthrex PCCP project. Pulling would regress the local refactor → not pulled; surfaced as push candidates.
  - **5 dhf-manifest files** (`README.md`, `SKILL.md`, `actions/discovery-index.md`, `scripts/discovery-index.py`, `tests/test_discovery_index.sh`) → `LOCAL_AHEAD`. **Uncommitted WIP** in the working tree (task ben/051, status Not Started) — not pull-eligible and not push-ready.
  - **1 file** `skills/project-console/console/web/static/console.overrides.css` → `LOCAL_AHEAD`, committed locally, clean push candidate.
- project.yml: no changes
- Follow-ups: push decision pending user — see push candidates above.

## 2026-05-13 — push (12 advisor agents → three-tier canonical-role grounding)

- Files: 13
  - agents (12): clinical-affairs, core-team-panel, cybersecurity, design-review-panel, human-factors, post-market, program-manager, quality-engineering, rd-lead, risk-management, systems-engineering, vnv-lead — refactored from `context:`/`sources:` glob-list grounding to three-tier `canonical_roles:` grounding (tier_1 / tier_2 / tier_3 advisor-researcher) + `Agent` tool
  - skills/project-console/console/web/static/console.overrides.css (local-ahead styling override)
- Branch: `sync/pdlc-demo-agent-canonical-roles-2026-05-13`
- PR: https://github.com/GlobalLogic-a-Hitachi-Company/hitachi/pull/160
- Commit: "Refactor 12 advisor agents to three-tier canonical-role grounding"
- Status: merged (--merge requested)
- Merge commit: `4b43fff`
- Hitachi HEAD after sync: `4b43fff`
- Provenance: PDLC_DEMO — local agent refactor committed `620e15e` (2026-04-20). These agents had entered the registry via hitachi #63 (`3393bab`) in the pre-refactor Arthrex-sourced format.
- Not pushed: 5 dhf-manifest files (uncommitted WIP, task ben/051 — Not Started).

## 2026-05-30 — push (sync-skills v8.3 — Windows symlink corruption guard)

- Files: 4
  - `skills/sync-skills/SKILL.md` (version 8.2 → 8.3, +new test in Supporting Files)
  - `skills/sync-skills/README.md` (v8.3 changelog entry)
  - `skills/sync-skills/scripts/sync.sh` (+`_is_tracked_symlink`, `_read_symlink_target`, `_smart_content_hash`, `_sha1_stdin` helpers; `cmd_analyze` symlink branch via index instead of `-L`; `_walk_registry_tree` uses `_smart_content_hash`; `cmd_push_stage` hard guard refuses corrupt-symlink content with exit 8)
  - `skills/sync-skills/tests/test_windows_symlink_guard.sh` (new, 4 cases)
- Branch: `sync/sync-skills-v8.3-windows-symlink-guard-2026-05-30`
- PR: https://github.com/GlobalLogic-a-Hitachi-Company/hitachi/pull/185
- Commit: "sync-skills v8.3 — Windows-clone symlink corruption guard"
- Status: merged (squash)
- Merge commit: `8ebe1f2`
- Hitachi HEAD after sync: `8ebe1f2`
- Provenance: PDLC_DEMO task ben/066. Bug surfaced when upstream commit `07574e9` overwrote 14 `.claude/agents/*.md` symlinks with full markdown content under preserved 120000 mode, blocking `git pull --ff-only` on Linux/macOS. Root cause: pre-v8.3 `[[ -L ]]` filesystem check returns false on Windows clones where `core.symlinks=false` materializes tracked symlinks as plain text files. Repair PR for the corrupted project state: PDLC_DEMO PR #11 (commit `bc2f698`) — git-plumbing restoration of the 14 entries to pre-vlad blobs.
- Local sync: not needed — fix was authored against the local copy first, then pushed; local is already at v8.3.

## 2026-05-30 — pull (bulk registry sync; ben/067)

- Hitachi HEAD after sync: `8ebe1f2`
- Pulled: 79 files in two passes
  - **38 UPSTREAM_ADVANCE** (clean fast-forwards): `advisors/` (16 incl. SKILL/VERSION/13 agents/render-grounding.py); `dhf-manifest/` (5: README/SKILL/discovery-index.{md,py}/canonical-roles.yaml); `file-locator/scripts/indexer_docs.py`; `frontend-slides/SKILL.md`; `jira-pull/SKILL.md`; `medtech-docs/` (10: README/SKILL/4 references/sentinel-blocks rule/render-sentinels.py/readme-risk-management template); `task/` (3: README/SKILL/session-cleanup.sh); `tracker/scripts/render.py`
  - **41 UPSTREAM_ONLY** (new content):
    - **3 new skills** added to `project.yml` `approved_skills`: `gap-analysis` (8 files), `knowledge-pack-export` (7), `reference-audit` (7)
    - **4 new agents** from `reference-audit` added to `approved_agents`: citations + citations-{external,informal,internal}-researcher
    - **3 new auto-loaded medtech-docs rules** symlinked into `.claude/rules/` + listed in `CLAUDE.md` Auto-loaded Rules section: `doctype-governance.md`, `ground-in-contracts-not-assumptions.md`, `internal-vs-external-scope-labels.md`
    - **New medtech-docs hook**: `taxonomy-freshness.sh` (NOT yet wired — see follow-up)
    - **FDA guidance pack**: MDDS (distilled + source PDF + FR notice), qSub eSTAR draft, qSub FR 2025-09615
    - **3 new 21 CFR regulation refs**: parts 807, 880, 892
    - **New task tooling**: `task/commands/checkpoint.md` + `task/hooks/checkpoint-recover.sh` (NOT yet wired)
  - **13 UNDETERMINED `agents/*.md`** auto-reconciled (transitive — they're symlinks to `skills/advisors/agents/*.md` which were pulled)
- project.yml: `approved_skills` +3 (gap-analysis, knowledge-pack-export, reference-audit); `approved_agents` +4 (reference-audit citations agents)
- Follow-ups (captured as todos in `tasks/ben/067-bulk-registry-sync-2026-05-30.md`):
  - Per Step 5b Project Impact Analysis: verify each pulled SKILL.md's changelog for required post-update actions (setup re-runs, hook installs, schema changes); current commit installs the 3 medtech-docs rule symlinks but does not run `/medtech-docs init` end-to-end.
  - `file-locator/scripts/indexer_docs.py` change is likely the registry-side fix for ben/065 (CI `UNIQUE constraint failed: summaries.path, summaries.heading_anchor`) — validate post-pull and close ben/065 if confirmed.
  - `medtech-docs/hooks/taxonomy-freshness.sh` pulled but not wired into `settings.json` — needs `/medtech-docs setup` re-run to register.
  - `task/commands/checkpoint.md` + `task/hooks/checkpoint-recover.sh` pulled but checkpoint command/hook not wired — needs `/task setup` re-run.
  - Read each of the 3 new skills' SKILL.md end-to-end (per the project's "read the skill before planning" rule) before invoking.

## 2026-06-02 — push

- Files: `skills/medtech-docs/references/regulations/45-cfr-part-164.md`, `skills/medtech-docs/references/regulations/README.md`, `skills/medtech-docs/references/industry-frameworks/nist-sp-800-66.md`, `skills/medtech-docs/references/industry-frameworks/README.md`
- Branch: `sync/pdlc-demo-hipaa-nist-references-2026-06-02`
- PR: https://github.com/GlobalLogic-a-Hitachi-Company/hitachi/pull/193
- Commit: "medtech-docs: add HIPAA Security Rule + NIST SP 800-66 references"
- Status: merged (--merge requested)
- Merge commit: `502841c`
- Hitachi HEAD after sync: `502841c`
- Origin: PDLC_DEMO task ben/075. Two new reference distillations (HIPAA Security Rule + NIST SP 800-66 Rev. 2); README edits verified purely additive over upstream. GDPR deferred.

## 2026-06-02 — push (advisors conformance + HIPAA grounding)

- Files: `skills/dhf-manifest/data/canonical-roles.yaml`, `skills/advisors/SKILL.md`, `skills/advisors/README.md`, 11 `skills/advisors/agents/*.md` (clinical-affairs, cybersecurity, human-factors, post-market, program-manager, quality-engineering, rd-lead, regulatory-affairs, risk-management, systems-engineering, vnv-lead); deleted `skills/advisors/VERSION`
- Branch: `sync/pdlc-demo-advisors-hipaa-grounding-2026-06-02`
- PR: https://github.com/GlobalLogic-a-Hitachi-Company/hitachi/pull/194
- Status: merged (--squash)
- Origin: PDLC_DEMO task ben/076. (1) advisors skill-creator conformance — frontmatter added, BP+Changelog→README, semver VERSION→integer version, project refs scrubbed. (2) canonical-roles HIPAA/45 CFR + NIST SP 800-66 descriptions + cybersecurity L1b regulations consumer. Excluded core-team-panel/design-review-panel (pre-existing drift, not this task's work).

## 2026-06-02 — pull

- Hitachi HEAD before: `cd3f800`
- Pulled: 11 files (auto-pull bucket — UPSTREAM_ADVANCE + UPSTREAM_ONLY)
  - `skills/advisors/agents/core-team-panel.md`, `design-review-panel.md`, `scripts/render-grounding.py` (v1.5.2 "show the bytes" verify-claim rule, #187)
  - `skills/knowledge-pack-export/{README,SKILL}.md`, `scripts/build_pack.py` (v3→v5: snapshot banner, image-ref counts, segment markers)
  - `skills/skill-creator/SKILL.md`
  - `skills/gap-analysis/actions/list.md`, `templates/gap-analysis.md` (v4 folder-per-analysis — 2-line diffs)
  - `skills/medtech-docs/references/fda-guidance/{source-md/csa-qms.md, source/guidance-computer-software-assurance-production-quality-system.pdf}` (new CSA guidance)
- project.yml: no changes (all pulled skills already in approved lists; reference files are content)
- Project impact: none requiring action. No built knowledge-packs exist (banner moot); advisors GROUNDING re-render optional (prompt-rule change only).
- Skipped: `gap-analysis` SKILL/README/init/fan-out (LOCAL_AHEAD but DIVERGED — local v3 vs upstream v4; held for v3⊕v4→v5 merge). Top-level `agents/*-panel.md` are symlinks into advisors (false-positive UNDETERMINED).

## 2026-06-02 — push

- Files (18): `skills/project-console/` (README, VERSION, console/app.py, web/static/console.css, web/templates/_base.html, console/gap_analysis/{__init__,loader,router}.py, web/static/gap_analysis.css, web/templates/gap_analysis_{index,view}.html); `skills/tracker/` (README, SKILL, scripts/render.py); `skills/frontend-design/` (.pinned-sha, LICENSE.txt, README, SKILL)
- Branch: `sync/pdlc-demo-console-tracker-frontend-2026-06-02`
- PR: https://github.com/GlobalLogic-a-Hitachi-Company/hitachi/pull/195
- Commit: "project-console 1.23, tracker v13, + new frontend-design skill"
- Status: merged (--merge requested)
- Merge commit: `09d643c`
- Hitachi HEAD after sync: `09d643c`
- Origin: PDLC_DEMO tasks ben/073 (console.css refresh), ben/077 (console Gap Analysis section), ben/078 (tracker dashboard refresh). project-console 1.21.1→1.23.0 + tracker v11→v13 both verified linearly-ahead (changelog contains upstream version); frontend-design net-new vendored fork. gap-analysis EXCLUDED (diverged — separate v3⊕v4→v5 merge to follow). Generalization validated against arthrex/pccp.

## 2026-06-02 — push (gap-analysis v5 convergence)

- Files (10): `skills/gap-analysis/` (SKILL, README, actions/{render,init,fan-out,list}.md, scripts/render_sidecars.py); `skills/project-console/` (console/gap_analysis/loader.py, VERSION, README)
- Branch: `sync/pdlc-demo-gap-analysis-v5-2026-06-02`
- PR: https://github.com/GlobalLogic-a-Hitachi-Company/hitachi/pull/196
- Commit: "gap-analysis v5 (folder-per-analysis convergence) + project-console 1.23.1"
- Status: merged (--merge requested)
- Merge commit: `a3f9959`
- Hitachi HEAD after sync: `a3f9959`
- Origin: PDLC_DEMO task ben/077 Phase E. Resolves the gap-analysis divergence held out of PR #195: 3-way merged our render/console work (parallel v3) onto upstream v4 folder-per-analysis (#188) → v5. Producer (render_sidecars.py `*/*/*.md`) + consumer (loader.py `*/*/*.gap.json`) migrated to nested layout; existing HIPAA analysis migrated into its folder; project-console → 1.23.1.

## 2026-06-03 — push (gap-analysis contrast fix)

- Files (3): `skills/project-console/console/web/static/gap_analysis.css`, `VERSION`, `README.md`
- Branch: `sync/pdlc-demo-console-contrast-1232-2026-06-03`
- PR: https://github.com/GlobalLogic-a-Hitachi-Company/hitachi/pull/197
- Status: merged (--merge requested)
- Merge commit: `7cc6a93`
- Hitachi HEAD after sync: `7cc6a93`
- Origin: PDLC_DEMO task ben/077 B1.2. project-console 1.23.1 → 1.23.2 — theme-robust semantic pills (color-mix tint + text toward --body-text); fixes dark-theme WCAG AA failures (2.07–4.04) found via Chrome DevTools. Project repo: PR #44 (`af5b057`).

## 2026-06-04 — push (gap-analysis v6 + console 1.25.0)

- Files (10): `skills/gap-analysis/` (SKILL, README, scripts/render_sidecars.py, templates/gap-analysis.md); `skills/project-console/` (README, VERSION, console/gap_analysis/{loader,router}.py, console/web/static/gap_analysis.css, console/web/templates/gap_analysis_view.html)
- Branch: `sync/pdlc-demo-gapanalysis-console-positions-2026-06-04`
- PR: https://github.com/GlobalLogic-a-Hitachi-Company/hitachi/pull/198
- Commit: "gap-analysis v6 + project-console 1.25.0: agent panels, goals, assertion positions"
- Status: merged (--merge requested)
- Merge commit: `e3a369b`
- Hitachi HEAD after sync: `e3a369b`
- Preflight: all 10 files `UPSTREAM_NEWER` by content but verified upstream == local committed baseline (divergence is purely local edits → safe LOCAL_AHEAD advance). `__pycache__` scrubbed pre-push.
- Origin: PDLC_DEMO task ben/081. gap-analysis v5→v6 (optional `## Assertion positions` → additive `assertions[].positions[]`, schema_version unchanged 1.0); project-console 1.23.2→1.25.0 (1.24.0 Goals banner + agent-response viewer; 1.25.0 Report/Advisors tabs + per-advisor assertion positions). Design via frontend-design.

## 2026-06-08 — pull (explain skill + advisor advances)

- Hitachi HEAD after sync: `3535fe7` (local mirror was 9 commits behind; fast-forwarded clean)
- Pulled (35 files):
  - `skills/explain/**` (24) — NEW skill: project-question → self-contained visualization-rich HTML explainer saved to personal scratch. Guidance-only (no hooks/scripts/setup action).
  - `skills/advisors/agents/*.md` (11) — 1-commit advance (HIPAA-grounding follow-on, `cd3f800`). The 11 top-level `agents/*.md` symlinks resolved automatically once these targets updated (same content, double-counted in raw drift).
- Drift after pull: 0 files (SYNCED).
- project.yml: added `explain` to `security.approved_skills`.
- Follow-ups: none — `explain` has no setup action, no hooks; no `/best-practices` re-run triggered. 17 stale `sync/*` branches pruned separately (hygiene).
- Origin: PDLC_DEMO task ben/084. Surfaced when user asked "are we synced?"

## 2026-06-11 — pull (bulk: 65 files, 8 skills advanced)

- Hitachi HEAD after sync: `9fb865e` (local mirror already in lockstep with origin/main)
- Pulled (65 files): 42 UPSTREAM_ADVANCE + 23 UPSTREAM_ONLY; 0 LOCAL_AHEAD, 0 BOTH_DIVERGED.
  - `skills/task/` v29 — `_work/` committed personal sandbox wired in (`rules/scratch-and-tmp.md` + create/setup steps)
  - `skills/medtech-docs/` v32 — new auto-loaded rule `rules/ai-changelog.md`; 8 new FDA-guidance distillations + source PDFs/MDs; reference-library escalation-contract pass; `templates/readme-dev-spec.md`
  - `skills/file-locator/` v3 — `**/_work/**` excluded from corpus by default; new `scripts/binary_coverage.py`
  - `skills/change-control/` 0.13.1 — retired staging→promote inbound model (adopt lands at `staging_target_root` directly)
  - `skills/dhf-manifest/` — new `scripts/audit-coverage.py` (taxonomy mapping completeness) + audit row
  - `skills/docflow/` v32–v35 — adopt explicit-location + `_confluence` SPLICE mode + faithfulness policy; new `scripts/locate_md_target.py`
  - `skills/advisors/` 10 — advisor-researcher registry carve-out (may read `medtech-docs/references/**`)
  - `skills/reference-audit/` 4 — `regulations/` category wired into citations stack
- Deleted (mirroring upstream): `skills/change-control/actions/promote.py` (local blob `954935b` bit-identical to the blob upstream removed in `ef75911`)
- Drift after pull: 0 files (SYNCED).
- project.yml: added `**/_work/**` to `file_locator.corpus_excludes` (no allowlist changes — no new skills/agents).
- Follow-ups applied in-line: `.claude/rules/ai-changelog.md` symlink + CLAUDE.md pointer (medtech-docs init Check 7d); CLAUDE.md `scratch-and-tmp.md` pointer line updated for `_work/` (task v29). index.db rebuild not needed locally (CI-owned on PR merge).
- Origin: PDLC_DEMO task ben/085. User asked "pull the latest from project + skill repo, then push."

## 2026-06-12 — push (project-console 1.26.0)

- Files: `skills/project-console/VERSION`, `skills/project-console/SKILL.md`, `skills/project-console/README.md`, `skills/project-console/console/gap_analysis/router.py`, `skills/project-console/console/web/templates/gap_analysis_view.html`, `skills/project-console/console/web/templates/_assistant_drawer.html`
- Branch: `sync/pdlc-demo-project-console-gap-advisor-2026-06-12`
- PR: https://github.com/GlobalLogic-a-Hitachi-Company/hitachi/pull/216
- Commit: "project-console 1.26.0: Gap Analysis ask-the-advisor drawer + hidden-banner fix"
- Status: merged (user asked to land in both repos)
- Merge commit: `9e6a305`
- Hitachi HEAD after sync: `9e6a305` (local checkout fast-forwarded; sync branch deleted local + remote)
- Origin: PDLC_DEMO task ben/086 (project PR #54, merged `6cda697`).

## 2026-06-15 — push

- Files: project-console (1.17.0→1.27.0): `VERSION`, `SKILL.md`, `README.md`, `console/app.py`, `console/web/static/console.css`, `console/web/templates/_base.html`, `console/web/templates/workflow_b3_index.html`, `console/workflows/{catalog,router}.py` (modified) + `console/strategy/{__init__,router}.py`, `console/submission/{__init__,loader,router}.py`, `console/web/static/submission.css`, `console/web/templates/submission_{index,view}.html` (new); new `submissions` skill (SKILL/README/VERSION + `scripts/render_sidecars.py` + 7 templates); `skills/manifest.md` (project-console row bump + new Submissions row).
- Branch: `sync/pdlc-demo-console-strategy-submission-2026-06-15`
- PR: https://github.com/GlobalLogic-a-Hitachi-Company/hitachi/pull/217
- Commit: "project-console 1.27.0: Strategy + Submission topline sections; new submissions skill"
- Status: merged (--merge requested; user asked to land in both repos)
- Merge commit: `e93442f`
- Hitachi HEAD after sync: `e93442f` (local checkout fast-forwarded; sync branch deleted local + remote)
- Pre-push hitachi was at `9e6a305` (project-console 1.26.0); the 9 modified project-console files were LOCAL_AHEAD (clean advance, no divergence).
- Origin: PDLC_DEMO task ben/087 (project PR #56, merged `c69b821`).

## 2026-06-22 — push

- Files: `skills/medtech-docs/SKILL.md`, `skills/medtech-docs/references/fda-guidance/README.md`, `skills/medtech-docs/references/fda-guidance/accessories-distilled.md`, `skills/medtech-docs/references/fda-guidance/source-md/accessories.md`, `skills/medtech-docs/references/fda-guidance/source/accessories.pdf`
- Branch: `sync/pdlc-demo-accessories-fda-guidance-2026-06-22`
- PR: https://github.com/GlobalLogic-a-Hitachi-Company/hitachi/pull/229
- Commit: "medtech-docs: add FDA Medical Device Accessories guidance to references"
- Status: merged (--merge requested)
- Merge commit / Hitachi HEAD after sync: `4d27a97`
- Origin: PDLC_DEMO task ben/092 (import FDA Medical Device Accessories guidance)

## 2026-06-22 — pull

- Hitachi HEAD after sync: `4d27a97`
- Pulled: 5 files (all dhf-manifest; UPSTREAM_ADVANCE, clean fast-forward)
  - `skills/dhf-manifest/README.md`
  - `skills/dhf-manifest/actions/discovery-index.md`
  - `skills/dhf-manifest/data/canonical-roles.yaml`
  - `skills/dhf-manifest/scripts/discovery-index.py`
  - `skills/dhf-manifest/tests/test_discovery_index.sh`
- Source: hitachi #228 — external client-slug override seam for the discovery-index resolver (`evidence_layout.layers[<role>].external`). **Backward-compatible: no override ⇒ unchanged output.**
- project.yml: no changes (PDLC_DEMO uses no `external` override; resolver output unchanged)
- Project impact: **none required.** Opt-in override seam only; no new skills/agents (no allowlist change), no setup-action change, no schema migration. Discovery-index regeneration would produce identical output — not required.
- Follow-ups: dhf-manifest test suite couldn't run here (`pyyaml` not installed in shell) — pulled files are byte-identical to origin/main per sync check; validation deferred to a pyyaml-equipped env.

## 2026-06-29 — pull

- Hitachi HEAD after sync: `788df8c`
- Pulled: 44 files (scope: updates + new skills, per user)
  - Updates to installed skills (4): `skills/manifest.md`, `skills/usage-metrics/README.md`, `skills/usage-metrics/SKILL.md`, `skills/usage-metrics/scripts/setup.py`
  - New skill `red-team` (+ 7 skeptic agents + researcher) — agents wired as symlinks via setup
  - New skill `regulatory-authoring` (+ `regulatory-copy-editor` agent, `.claude/rules/regulatory-authoring.md`)
  - New skill `writing-well` (+ `prose-editor` agent)
  - New file `skills/usage-metrics/statusline.sh`
- Kept local (LOCAL_AHEAD, NOT pulled): `skills/usage-metrics/scripts/collect.py` — local blob newer than registry; remains a push candidate
- project.yml: approved_skills += red-team, regulatory-authoring, writing-well; approved_agents += 10 new agents (pending)
- Follow-ups: commit + push the synced skills/agents; reconcile usage-metrics divergence (push collect.py) if desired
