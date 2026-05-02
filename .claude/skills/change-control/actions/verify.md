# Action: `/change-control verify`

Repeatable smoke tests for the change-control skill. Each sub-action runs an end-to-end probe against the `test_target` configured in `project.yml` `change_control.test_target` and emits a structured JSON report under `tasks/<person>/_scratch/verify-<kind>-<date>.json`.

The Python helper (`actions/verify.py`) handles config audit + report writing; the live MCP / cookie-bridge calls are orchestrated by the agent following this procedure.

## Sub-actions

| Sub-action | What it proves |
|---|---|
| `audit` | The `change_control` block in `project.yml` is well-formed and `test_target` is set. No live calls. |
| `orphan-file` | A new attachment dropped under a page round-trips publish → live render → re-adopt and the marker is restored. Validates the orphan-file workflow added in task 134. |
| `cross-page-resolution` | A page known to contain `UNKNOWN_MEDIA_ID` adopts cleanly — the resolver swaps the placeholder for a real filename + downloaded binary (or graceful-warning blockquote when source-page is unresolvable). |
| `drift-detection` | A locally hand-edited adopted page, when re-adopted with `--on-conflict prompt`, emits the structured stderr conflict prompt + writes side-by-side files. |
| `all` | Runs every sub-action above and writes one report per kind. |

## Pre-flight (every sub-action)

1. Run `python3 .claude/skills/change-control/actions/verify.py audit` and confirm `ok: true`. If the audit fails, fix the project.yml block before any live sub-action.
2. Confirm Chrome / web-control is up: `python3 .claude/skills/web-control/actions/status.py`. If not, abort and ask the user to run `/web-control launch`.

## `verify orphan-file` procedure (live)

Pre-conditions: `audit` passed; web-control up; cookie session active.

1. Pick a target Pre-Op leaf page that has no attachments yet. Note its local markdown path.
2. **Synthesize** a small PDF (e.g. via `python3 -c "import reportlab..."` or a fixed test fixture under `templates/`). Drop it at `<page-dir>/images/test-orphan-file.pdf`.
3. **Edit** the markdown body — append a single line: `[Test Orphan File](images/test-orphan-file.pdf)` (no marker comment; this is what makes it an orphan attachment).
4. **Build ADF body**:
   ```
   python3 actions/publish_helper.py adf-body --source <page>.md --emit-images-sidecar /tmp/sidecar.json
   ```
5. **Create a NEW page** under `change_control.test_target.parent_page_id` via `mcp__atlassian__createConfluencePage`. Title = `<title_prefix> orphan-file <YYYY-MM-DD>`. Capture the new page id.
6. **Upload images**:
   ```
   python3 actions/publish_helper.py upload-images \
     --sidecar /tmp/sidecar.json --source-dir <page-dir> \
     --page-id <NEW> --base-url <from config>
   ```
7. **Patch ADF + update the page** with the upload-images media id map.
8. **Re-fetch** via `mcp__atlassian__getConfluencePage` — confirm the attachment exists in the page's attachment listing and the file-card renders in the body.
9. **Re-adopt** the new page via `adopt_helper.py write` and confirm the local markdown's `[Test Orphan File](images/test-orphan-file.pdf)` line was rewritten with the round-trip marker (`<!-- media id=... -->`).
10. **Persist report**: collect each step's outcome as a JSON list and pipe to:
    ```
    python3 actions/verify.py orphan-file < /tmp/orphan-steps.json
    ```
    The helper writes `tasks/<person>/_scratch/verify-orphan-file-<date>.json` and exits non-zero on any step failure.
11. **Cleanup** local synthetic content via `git checkout -- <page>.md <page-dir>/images/test-orphan-file.pdf` so the local repo is unchanged. The new Confluence page in `AI_PDLC_INT_TEST` is left as a fixture for future audits — note its page-id in the report.

The report `steps[]` should include at minimum: `synthesize-pdf`, `build-adf-body`, `create-page`, `upload-images`, `update-page`, `verify-attachment-rendered`, `re-adopt`, `verify-marker-restored`, `cleanup-local`.

## `verify cross-page-resolution` procedure (live)

1. Pick a page id known to carry `UNKNOWN_MEDIA_ID` (e.g. one of the IntraOp pages from `change_control.cross_page_source_map`).
2. Run `adopt_helper.py write` against it. The resolver should consult the config map first, then fall through to live storage XHTML / CQL.
3. Inspect the resulting markdown: confirm `<<file:UNKNOWN_MEDIA_ID>>` is gone and the file-card has either a real binary in `images/` (success) or a graceful-warning blockquote (acceptable degraded path when the source page can't be resolved).
4. Report steps: `adopt`, `placeholder-removed`, `binary-downloaded` (or `graceful-warning-emitted`).
5. Pipe steps JSON to `verify.py cross-page-resolution`.

## `verify drift-detection` procedure (live)

1. Pick an already-adopted page with a current snapshot under `docs/.change-control/snapshots/`.
2. Make a hand-edit to the local markdown — change one sentence. Don't touch the snapshot.
3. Re-fetch the page via MCP (no actual remote change). Run `adopt_helper.py write --on-conflict prompt`.
4. Confirm the helper exits non-zero AND writes `<page>.confluence-side.md` + `<page>.local-diff.md` AND emits the structured `CONFLICT` prompt to stderr.
5. Report steps: `apply-local-edit`, `re-adopt`, `conflict-prompt-fired`, `side-files-written`.
6. Pipe steps JSON to `verify.py drift-detection`.
7. **Cleanup**: `git checkout -- <page>.md` and remove the side-by-side files.

## `verify all` procedure

Run each of the three live sub-actions in order: orphan-file → cross-page-resolution → drift-detection. Each writes its own dated JSON report under `_scratch/`. End with one summary line listing the report paths.

## Notes for the agent

- **Never write to anywhere outside `test_target`**. The whole point of this action is repeatability; a verify run that mutates production pages defeats the purpose.
- **Reports are personal scratch** — gitignored, never committed. Don't add them to PRs.
- **If pre-flight fails** (no test_target, Chrome down, etc.), exit early with a single descriptive error rather than running degraded checks.
- **The Python helper is purposely thin** — every live call belongs in this procedure. The helper's job is config loading + JSON report writing, not orchestration.
