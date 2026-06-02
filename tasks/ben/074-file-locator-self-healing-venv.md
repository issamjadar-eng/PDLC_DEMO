# 074 — File-Locator Self-Healing venv Bootstrap

**ID**: 074
**Created**: 2026-06-01
**Status**: In Progress
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: Medium

---

## PERMANENT RULES (do not remove)

This task document is the **session-recovery point** for this work. If the current session drops, is compacted, or ends, the next session must be able to load **this file alone** and continue where we left off. That is only possible if the doc is kept current in-flight.

1. **Update at every meaningful checkpoint (HARD RULE).** After each meaningful unit of work — a converted/adopted doc, a committed change, a launched batch, a completed phase, a decision, a discovered blocker, a design pivot — update this task doc: tick the relevant Todo, add a dated Changelog line naming the concrete artifact, update progress counts.
2. **Phase-end batching is OK; drift-batching is not.** Write at the phase boundary, before the next phase starts.
3. **A commit is not a substitute.** Git records code; this doc records the project narrative.
4. **Resume-ready before any session boundary.** Doc must contain what was completed (with artifacts), in-flight state, priority-ordered next steps with paths, open questions, and the exact `/task` activation command to resume.
5. **Capture strategy + lessons as they happen.** Write option comparisons, scope decisions, pivots, and corrected assumptions into the doc in-flight.

Success test: a fresh Claude session, given only this file, can re-enter the work without asking "what were we doing?"

## Goals

_Make the file-locator MCP self-heal its missing Python venv so a failed-to-connect server can recover without out-of-band shell commands._

- **G1 — Root context.** This session diagnosed the live failure: `tools/file-locator-mcp/.venv/` was missing (not committed; only `index.db` is the canonical committed artifact), so `.mcp.json`'s `./tools/file-locator-mcp/.venv/bin/python` spawn failed with `ENOENT`. Fixed for this machine by recreating the venv (`uv venv` + `uv pip install`). The venv is gone again after any fresh clone or repo move — a recurring, predictable failure with no in-product fix.
- **G2 — Self-healing wrapper.** Change the file-locator skill so `.mcp.json`'s `command` points at a **bootstrap wrapper** that ensures the venv exists (creates + installs deps if missing) before `exec`-ing the real `server.py`. First `/mcp → Reconnect` after a clone becomes self-repairing (slow once, instant after); steady state unchanged.
- **G3 — Generalize + validate.** This is generic skill infrastructure, not project-specific. Validate against the sister project `../../projects/arthrex/pccp/` per [[feedback_sister_project_compat]] before marking complete. Bump skill `VERSION`/`## Changelog`; keep `## Best Practices` per [[feedback_skill_version_bestpractices]]. Route through `/skill-creator`.

## Background — why `/mcp` can't fix it today (decision context)

<!-- STRATEGY CONTENT: architecture, mcp-lifecycle, self-healing-tooling -->
`/mcp` exposes only **Reconnect / View tools / Enable-Disable** for a stdio server (Authenticate is OAuth-only). Reconnect re-runs the exact configured `command`/`args` verbatim — it has **no hook to build a venv or run setup**. Because `.mcp.json` points *directly* at the venv interpreter, there is no seam at which to bootstrap. The fix is to introduce that seam: a wrapper script as the `command`, so a plain Reconnect can repair the environment. This mirrors what `rebuild.sh` already does in its preflight (venv-existence check + guidance) — the wrapper makes that preflight *active* (build) rather than *advisory* (print-and-exit) and moves it onto the MCP launch path.
<!-- /STRATEGY CONTENT -->

## Design

<!-- STRATEGY CONTENT: architecture, mcp-bootstrap, cross-platform -->

### Confirmed launch contract (Phase 0)

- `.mcp.json` `file-locator` entry: `command: ./tools/file-locator-mcp/.venv/bin/python`, `args: [./.claude/skills/file-locator/scripts/server.py]`, `env: {}`. Launcher **cwd = project root**, so project-root-relative paths resolve.
- The launcher **does PATH-resolve bare command names** — the sibling `chrome-devtools` entry uses `command: npx` and connects fine. The documented `ENOENT` failure mode is specifically about a *literal* `${CLAUDE_PROJECT_DIR}` string in the path (never expanded), **not** about bare names. → A bare `command: python3`/`bash` is viable; a `${...}` path is not.
- `server.py` needs `fastembed` + `mcp` + `PyYAML` in the venv and resolves `common.py` relative to itself. The venv is the only thing missing after a clone/move; the skill scripts and `index.db` are committed.
- `requirements.txt` is **copied into `tools/file-locator-mcp/`** by `setup` (a committed tool file) — so a bootstrap script has the dep list available at the fixed tool path without reaching into the skill package.
- The generated `rebuild.sh` already encodes the exact build recipe we need (`uv venv --python 3.12` + `uv pip install -r requirements.txt`) **and** the `Icon\r` scrub. Today it only *prints instructions* when the venv is missing (advisory). The wrapper makes that recipe *active* (build) and moves it onto the **MCP launch path**.

### The seam

Replace the direct `command: ./…/.venv/bin/python` with a **committed wrapper** as the `command`. The wrapper ensures the venv exists (builds + installs if missing, scrubs `Icon\r`), then `exec`s the real `.venv` interpreter on `server.py`. Steady state = one extra `exec`; cold state (post-clone) = one slow self-repairing launch, then instant. `/mcp → Reconnect` now actually repairs, because Reconnect re-runs the wrapper.

### Two candidate wrapper shapes

**Option A — committed `bootstrap.sh` (POSIX shebang script).**
- `.mcp.json`: `command: ./tools/file-locator-mcp/bootstrap.sh`, `args: [./.claude/skills/file-locator/scripts/server.py]`.
- Body: if `.venv/bin/python` absent → `uv venv --python 3.12` then `uv pip install -r requirements.txt` (fallback `python3 -m venv` + `pip install`); scrub `Icon\r`; `exec ./.venv/bin/python "$@"` with `CLAUDE_PROJECT_DIR` exported.
- ➕ Minimal delta — it's the existing `rebuild.sh` preflight made active; DRY (both can share one `ensure-venv` snippet). Shebang scripts exec fine through the launcher.
- ➖ POSIX-only (no `sh` on native Windows). But the current snippet already hardcodes `.venv/bin/python`, so **Windows is already unsupported — no regression.** Needs the exec bit preserved in git.

**Option B — system `python3` → committed `bootstrap.py` (stdlib-only).**
- `.mcp.json`: `command: python3`, `args: [./tools/file-locator-mcp/bootstrap.py, ./.claude/skills/file-locator/scripts/server.py]`.
- `bootstrap.py`: compute per-OS venv interp (`bin/python` vs `Scripts/python.exe`); if missing, build (prefer `uv`, else stdlib `venv`+`pip`); `os.execv` the venv interp on `server.py`.
- ➕ Cross-platform incl. Windows; no exec-bit/shebang concerns; pure stdlib; one language.
- ➖ Relies on `python3` being on PATH (true on mac/Linux; Windows is often `python`, not `python3`). Slightly more logic than the existing sh recipe; doesn't reuse `rebuild.sh` directly.

### Recommendation

**Option A.** It is the smallest, lowest-risk change: it reuses the build+scrub recipe `rebuild.sh` already carries, keeps a single POSIX toolchain, and loses no platform support we currently have (the snippet is already `bin/python`-only). Windows support for file-locator is a separate, larger effort (the whole skill assumes `.venv/bin/python`); folding it into this fix would scope-creep. If we later genericize the skill for Windows, the `bootstrap.py` shape (Option B) becomes the natural carrier and we switch then.

### Open design points (regardless of A/B)

- **Idempotency:** wrapper is a no-op fast-path when `.venv/bin/python` is present (single `-x` test) — must not add latency in steady state.
- **Build-tool fallback:** prefer `uv` (matches `rebuild.sh`); fall back to stdlib `python3 -m venv` + `pip` so machines without `uv` still self-heal.
- **`index.db` absence:** wrapper ensures **venv only**, not the index. `index.db` is committed; its absence is an unusual state worth surfacing (server already handles a missing/empty index), not silently rebuilding on the launch path. (Q3 → resolved: venv only.)
- **Migration:** `setup` must (a) write `bootstrap.sh`, (b) rewrite an already-installed `.mcp.json` `file-locator.command` from `./…/.venv/bin/python` to the wrapper (idempotent jq), (c) leave a hand-forked entry alone. Update Troubleshooting Cause-1/2 text accordingly.
- **Versioning:** bump skill `version` (1 → 2), add `## Changelog` + `## Best Practices` rows; route through `/skill-creator`; validate against `../../projects/arthrex/pccp/`.
<!-- /STRATEGY CONTENT -->

## Todos

- [x] Read file-locator skill templates end-to-end — launch contract confirmed (see Design).
- [x] Design the bootstrap wrapper; captured in Design section.
- [x] Decide wrapper shape — **Option A (`bootstrap.sh`)** selected by user.
- [x] Update `templates/mcp.json.snippet` `command` → `bootstrap.sh`.
- [x] Add `templates/bootstrap.sh` (self-heal wrapper, stderr-only).
- [x] Update `setup` action (copy+chmod bootstrap.sh; v1→v2 `.mcp.json` migration) in SKILL.md.
- [x] Bump version 1→2; SKILL.md Supporting-Files row + Troubleshooting (Cause 0 + v2 self-heal note); README changelog v2.
- [x] Dogfood in this project: installed live `tools/file-locator-mcp/bootstrap.sh` (chmod +x), rewrote live `.mcp.json`. Fast-path + cold-path (venv removed → rebuilt) both verified; **0 stdout bytes** in both.
- [x] Validate against sister project — `/Users/ben.xavier/projects/arthrex-pccp/` is in the **identical broken state** (v1, direct-venv command, `.venv` missing). Change is project-agnostic; fixes it too. Registry (`hitachi`) still v1.
- [ ] **Restart Claude Code** to load the v2 wrapper (this session's MCP is still on the old spawn). — user action
- [ ] `/sync-skills push` the v2 skill upstream to hitachi (→ sister pulls + re-runs `setup` to migrate). — pending user approval

## Validation — sister project (arthrex-pccp)

`/Users/ben.xavier/projects/arthrex-pccp/`:
- `SKILL.md` version `1`; `.mcp.json` `file-locator.command` = `./tools/file-locator-mcp/.venv/bin/python`; `tools/file-locator-mcp/` has **no `.venv/`** (README/index.db/rebuild.sh/requirements.txt only).
- → Same latent `ENOENT`-on-clone failure we hit here. Confirms the bug is **cross-project and recurring**, not a one-off, and that the fix **generalizes** (fixed relative paths, zero project-specific content). The `setup` v1→v2 migration is what carries the fix into the sister once it `/sync-skills pull`s.

## CI rebuild workflow — interaction with v2 (no change required)

`.github/workflows/file-locator-rebuild.yml` (installed by `setup`; present in this project — see commit `ee1cf42`, and in the sister) rebuilds the **committed `index.db`** on push to `main` touching `docs/**` / `project.yml` / `.claude/skills/**` / `*.md`. It builds its **own** venv in the runner (explicit "Create venv + install deps" step) and runs `tools/file-locator-mcp/rebuild.sh` (the index builder), **not** `bootstrap.sh` (the MCP launcher). Different entry points, different venvs (CI runner vs developer-local).

- **No conflict with v2.** The wrapper is on the local MCP launch path only; the workflow is on the index-freshness path only. v2 changes neither `rebuild.sh` nor the workflow template — both are untouched.
- **Reinforces Q3 (venv-only bootstrap).** Because CI owns index freshness and `index.db` is committed, the local wrapper correctly ensures the **venv only** and never rebuilds the index on launch. The two mechanisms compose.
- **Optional DRY (out of scope for ben/074):** CI's venv-create step duplicates the `uv venv` + `uv pip install` recipe also in `bootstrap.sh` and `rebuild.sh`'s error text. A future cleanup could extract a shared `ensure-venv.sh` sourced by `bootstrap.sh` + `rebuild.sh` (the latter auto-building instead of exit-1), collapsing the CI step to one call. Deferred — touches `rebuild.sh` + the workflow template; current state is correct and low-risk.

## Lessons Learned

<!-- LESSONS LEARNED: tooling, mcp, infra -->
**A committed-index + uncommitted-venv MCP has a built-in cold-start trap.** file-locator commits `index.db` but (correctly) never the `.venv`. So every fresh clone / repo move spawns an interpreter that doesn't exist → `ENOENT`, and `/mcp → Reconnect` can't fix it because Reconnect re-runs the *same* failing `command` with no build hook. Any MCP whose `command` points directly at a build-artifact interpreter inherits this. **Fix pattern:** make `command` a committed wrapper that ensures its runtime exists before exec'ing it — the build step then lives *on the launch path*, so Reconnect self-heals.
**Why:** the failure is invisible until someone clones/moves, then looks like "the MCP is broken" with no in-product remedy.
**How to apply:** for any stdio MCP backed by a venv/node_modules/build dir, point `.mcp.json` `command` at a thin wrapper that builds-if-missing then execs; commit the wrapper (and its exec bit), never the build dir.

<!-- LESSONS LEARNED: mcp, stdio, correctness -->
**A stdio-MCP launch wrapper must write nothing to stdout.** stdout is the JSON-RPC channel; one stray byte (a build log line, an `echo`, pip's progress) corrupts the protocol and the server appears to fail. Route every diagnostic and every build subcommand's output to stderr (`>&2`), and keep the success fast-path silent before `exec`.
**Why:** the corruption is non-obvious — the venv builds fine, the server starts, yet the client rejects the stream.
**How to apply:** in any MCP `command` wrapper, `>&2` all chatter; verify with a launch test asserting **0 stdout bytes** on both the warm and cold paths (we did — see Changelog).
<!-- /LESSONS LEARNED -->

## Changelog

- 2026-06-01: Task created. Live file-locator failure diagnosed + fixed for this machine (missing venv → recreated via `uv venv` + `uv pip install`; server smoke-tested healthy). Opened this task to make the recovery self-healing in the skill. Design pending — Phase 0 is reading the skill templates end-to-end per [[feedback_read_skill_before_planning]].
- 2026-06-01: Phase 0 done (launch contract confirmed) + design authored. User chose **Option A (`bootstrap.sh`)**. Implemented: new `.claude/skills/file-locator/templates/bootstrap.sh`; `templates/mcp.json.snippet` command → wrapper; SKILL.md v1→v2 (Supporting-Files row, setup copy+chmod + `.mcp.json` v1→v2 jq migration, Troubleshooting Cause-0 + v2 self-heal note); README changelog v2. Dogfooded live (`tools/file-locator-mcp/bootstrap.sh` +x, `.mcp.json` rewritten). **Verified:** fast-path execs server with 0 stdout bytes; cold-path (venv moved aside) rebuilt the venv on stderr in seconds, exec'd server, 0 stdout bytes; rebuilt venv imports `fastembed`/`mcp`/`yaml` OK. Validated against sister `arthrex-pccp` (identical broken state → fix generalizes). Two lessons captured. Not yet committed/pushed. Restart required to load v2 in this project.

## Open Questions

- Q1 — Wrapper language: POSIX `sh` wrapper that builds the venv then execs `.venv/bin/python server.py`, **or** keep `command: python3` (system) pointing at a tiny `bootstrap.py` that re-execs into the venv? (Windows has no `sh`; system `python3` is the more portable entry. Leaning system-`python3` → `bootstrap.py`.)
- Q2 — Build tool: assume `uv` present, fall back to `python -m venv` + `pip`? Sister project + CI must both work.
- Q3 — Should the wrapper also run the **first index build** if `index.db` is absent, or only the venv? (Lean: venv only — `index.db` is committed; absence is an unusual state better surfaced than silently rebuilt.)

## Changelog

- 2026-06-01: Task created. Live file-locator failure diagnosed + fixed for this machine (missing venv → recreated via `uv venv` + `uv pip install`; server smoke-tested healthy). Opened this task to make the recovery self-healing in the skill. Design pending — Phase 0 is reading the skill templates end-to-end per [[feedback_read_skill_before_planning]].
