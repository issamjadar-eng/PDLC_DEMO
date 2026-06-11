# `change-control adopt` — agent procedure (Option A)

This action is **agent-orchestrated**. The Claude turn loop calls Atlassian
MCP tools directly; a small Python helper does the pure ADF→markdown +
frontmatter + snapshot work locally.

## Inputs

The user invokes this with a Confluence page URL or numeric page ID, plus
an optional target path:

    /change-control adopt <page-url-or-id> [--target <repo-path>]

If `--target` is omitted, default to:

    <staging_target_root>/<space-key>/<sanitized-page-path>.md

…where `<staging_target_root>` is read from the configured space in
`project.yml` (`change_control.spaces[].staging_target_root`) — projects
point it at the canonical Confluence-mirror root — and `<sanitized-page-path>` is the human-readable page path with
slashes preserved and unsafe characters replaced with hyphens.

## Step 1 — Resolve the cloudId

Call `mcp__atlassian__getAccessibleAtlassianResources`. Pick the
resource whose `url` matches the configured `confluence.base_url` from
`change-control.yml` (or, if absent, the first resource the user has
access to). Capture its `id` as `<cloud_id>`.

If the call fails or returns no resources, **fail loud**:

> MCP unreachable or no Atlassian site is accessible to this MCP
> session. Run `/mcp`, verify `atlassian` shows Connected, and retry.

## Step 2 — Resolve the page ID

If the user passed a URL of the form
`https://<host>/wiki/spaces/<KEY>/pages/<ID>/<slug>`, extract `<ID>`.

If the user passed a bare numeric ID, use it directly.

If the user passed a non-URL non-numeric string (e.g. a page title),
call `mcp__atlassian__searchConfluenceUsingCql` with
`cql=title="<input>" AND space="<key>"` and pick the first result.

## Step 3 — Fetch the page as ADF

Call:

    mcp__atlassian__getConfluencePage(
        cloudId=<cloud_id>,
        pageId=<page_id>,
        contentFormat="adf",
    )

Capture the full result. **Do not** read it as markdown — Probe A
locked the format choice: push markdown, read ADF.

If the page returns an empty body, surface this to the user and ask
whether to proceed (the helper will write a near-empty file).

## Step 4 — Run the helper

Pipe the JSON result from Step 3 into `actions/adopt_helper.py write`:

    echo "$ADF_RESPONSE_JSON" | python .claude/skills/change-control/actions/adopt_helper.py write \
        --target "<target-path>" \
        --base-url "<configured base_url>" \
        --space-key "<space-key from getAccessibleAtlassianResources>" \
        --parent-page-id "<parent_id from the response, or empty>" \
        --page-path "<human-readable page path>" \
        --cache-root "docs/.change-control" \
        --download-images   # OPTIONAL: download attachment binaries to <target-dir>/images/
        # Drift control (task 130 — adopt-direction non-destructive sync):
        # --on-conflict {prompt|overwrite|abort|merge}   default: prompt
        # --force                                        skip drift detection entirely

Pass `--download-images` whenever you want a fully self-contained
local copy or you intend to round-trip back to Confluence via
`publish`. The download pass requires the user to be signed into
Confluence in the web-control debug Chrome (with "Remember me"
checked). Failures degrade gracefully — the markdown is still written
and individual download errors are surfaced on stderr.

The helper:

1. Normalizes the ADF to markdown via `lib.normalizer.adf_to_markdown`
   (collapses smartlinks, tags `extension` macros as
   `<!-- confluence-side: <key> -->` placeholders, preserves Confluence
   Zones in `<details><summary>__CONFLUENCE_ZONE__: ...</summary>`,
   rewrites media refs to attachment URLs).
2. Writes the markdown with HTML-comment frontmatter at `<target>`:

       <!--
       title: ...
       state: published
       confluence:
         page_id: ...
         space_key: ...
         parent_page_id: ...
         page_path: ...
         adopted_at: <today>
         adopted_from_version: <N>
         last_published_version: <N>
       -->

3. Writes the snapshot to
   `docs/.change-control/snapshots/<page_id>-<version>.md`.
4. Prints a one-block summary (zones / extensions / media / smartlinks).

## Step 4b — Resolve smartcard labels

The helper emits a line on stderr in the form
`NEEDS_RESOLUTION {"target": "...", "smartcards": [{"placeholder_key", "page_id", "tinyui", "url"}, ...]}`.

If the `smartcards` array is non-empty, the agent batch-resolves each
entry and feeds the resulting key→title map back to the helper:

1. Build a Python dict `title_map = {}` keyed by `placeholder_key`.
2. For each entry with a `page_id`: call
   `mcp__atlassian__getConfluencePage(cloudId=<cloud_id>, pageId=<page_id>)`,
   capture `result.title`, set `title_map[entry.placeholder_key] = title`.
3. For each entry with a `tinyui` (and no `page_id`): call
   `mcp__atlassian__getConfluencePage(cloudId=<cloud_id>, pageId=<tinyui>)`
   — Atlassian MCP accepts the tinyui id directly. Capture `result.title`,
   set `title_map["x" + tinyui] = title`.
4. Pipe the JSON dump of `title_map` into the helper's resolve subcommand:
   ```
   echo '<json>' | python actions/adopt_helper.py resolve-smartcards \
       --target <target>
   ```
5. The helper rewrites the file in place: each
   `[<<smartcard:KEY>>](URL)` becomes `[<resolved title>](URL)`. The
   round-trip marker `<!-- smartcard -->` after each link is preserved
   so `publish` re-emits it as an ADF inlineCard, not a plain link.

If MCP fetch fails for a particular page (deleted page, restricted
access), leave that entry out of `title_map` — the helper will leave
its placeholder untouched, and the user can re-resolve later by
re-running the resolve step with a more complete map.

## Step 5 — Report and commit

Report the helper's summary to the user. Then create a single-purpose
git commit:

    git add <target> docs/.change-control/snapshots/<page_id>-<version>.md
    git commit -m "adopt: <page title> (<page_id>)"

If the user passed `--no-commit`, skip the commit step and tell them
which files were created.

## Drift detection on re-adopt (task 130, v0.9.0)

When the target file already exists, the helper performs a three-way
classification before any write:

  - **fresh**       — target absent → safe write (legacy path)
  - **in_sync**     — local body == current Confluence body → no-op,
                      exit 0 with `(in_sync, no-op)` message on stderr
  - **only_theirs** — local body matches the snapshot at v_anc but
                      Confluence has moved → safe overwrite, snapshot
                      advances to v_new
  - **only_yours**  — local body diverges from the snapshot but
                      Confluence has not changed since v_anc → preserve
                      local edits; only the frontmatter pointer
                      `adopted_from_version` advances
  - **conflict**    — both sides have changed since v_anc → controlled
                      by `--on-conflict`

On `conflict` the helper emits two side-by-side files next to the
target so the user can reconcile by hand:

  - `<doc>.confluence-side.md` — current Confluence body (verbatim)
  - `<doc>.local-diff.md`      — unified diff of (snapshot, local-current)

The helper then writes a structured prompt to stderr starting with the
machine-parseable line:

    CHANGE_CONTROL_ADOPT_CONFLICT page_id=<id> target=<path>

…followed by the reason and the three reconciliation options. Exit
codes:

  - 0 — fresh / in_sync / only_theirs / only_yours / conflict-overwrite
  - 2 — conflict + `--on-conflict abort`
  - 3 — conflict + `--on-conflict prompt|merge` (default; user must
        review the side-by-side files before continuing)

`--force` overrides the entire mechanism — overwrites the target and
refreshes the snapshot exactly as the legacy adopt did. Use only for
explicit destructive re-pulls.

## AUTO-sentinel macro expanders (task 131, v0.10.0)

When `--manifest-path` (and optionally `--repo-root`) are passed, the
adopt pipeline runs three additional expanders after `normalize()` but
before the snapshot is written, so the cached body and the on-disk
markdown both contain the rendered content:

### Children / pagetree macro

Whenever the ADF body contains an `extension` node with
`extensionKey ∈ {children, pagetree}`, the normalizer captures the
macro's `depth` / `sort` / `excerpt` / `root` / `style` parameters and
emits a sentinel pair:

    <!-- AUTO:CHILD-INDEX source=<kind> [depth=<n>] position=<n> -->
    <!-- /AUTO:CHILD-INDEX position=<n> -->

The action layer then looks up children of the current page in the
manifest (via `parent_id == this.page_id`), sorts by manifest order
(Confluence child_position), and splices a markdown bullet list of
`- [<title>](<rel-target-path>)` between the sentinels — clickable in
GitHub markdown preview and in VS Code.

If `--manifest-path` is not provided, the sentinels stay empty with a
`<!-- child-index render skipped: --manifest-path not provided -->`
note inside.

### Stub-container synthesis (Q5b)

Confluence renders a child page list via UI chrome on every container
page, even when the body has no explicit macro. To match that locally:
when the manifest says `is_container == True` AND no child-index macro
fired, the action layer appends a synthesized AUTO block at end of
body:

    ## Child pages

    <!-- AUTO:CHILD-INDEX source=stub-container position=0 -->
    - [Child A](child-a.md)
    - [Child B](child-b.md)
    <!-- /AUTO:CHILD-INDEX position=0 -->

`source=stub-container` distinguishes from a real macro — publish-side
fully strips it (no extension node emitted). Round-trip is loss-free.

### Jira macro

When the body contains `extensionKey == "jira"`, the normalizer
captures `jqlQuery` / `count` / `serverId` / `maximumIssues` and emits:

    <!-- AUTO:JIRA-LIST source=jira jql=<percent-encoded> position=<n> -->
    <!-- /AUTO:JIRA-LIST position=<n> -->

The action layer issues a cookie-bridge GET against
`/wiki/rest/api/3/search?jql=<encoded>&fields=summary,status,updated&maxResults=<n>`
and renders a `| Key | Summary | Status | Updated |` table inside the
sentinels. On auth failure or HTTP error a deferred-render comment is
inserted instead — never fails the adopt. Sentinels carry the original
JQL so re-adopt fills in the table once cookies are available.

### Page-title chrome (task 140, v0.13.0)

After every adopt, the markdown body opens with an AUTO:PAGE-TITLE
block that mirrors Confluence's title bar locally:

    <!-- AUTO:PAGE-TITLE -->
    # <Page Title>
    <!-- /AUTO:PAGE-TITLE -->

The title is sourced from frontmatter `title:` (populated from the
`getConfluencePage` response). When the body's first content block is
already `# <Page Title>` (matching exactly after stripping leading
zone sentinels and blank lines), the AUTO block is suppressed so
markdown viewers don't double-render.

The block is emitted BEFORE every other expander. Subsequent passes
(child-index, jira, attachments macro, TOC) skip AUTO regions, so the
title chrome is invisible to them.

### TOC chrome (task 140, v0.13.0)

When the source body has `extension key="toc"` (Confluence's Table of
Contents macro), the normalizer captures macroParams (`minLevel`,
`maxLevel`, `style`, `outline`, `printable`, `include`, `exclude`)
and emits:

    <!-- AUTO:TOC source=toc minLevel=N maxLevel=M position=P -->
    <!-- /AUTO:TOC position=P -->

The action layer runs LAST in `cmd_write` (after every other
expander) so the heading hierarchy reflects the fully-resolved body.
It walks all ATX headings outside any AUTO region (skips
CHILD-INDEX, JIRA-LIST, PAGE-TITLE, fenced code blocks), filters by
minLevel / maxLevel, and renders an anchored bullet list with
GitHub-style slugs:

    <!-- AUTO:TOC source=toc minLevel=1 maxLevel=6 position=0 -->

    - [Purpose](#purpose)
    - [Process and Methods](#process-and-methods)
      - [Grooming](#grooming)
      - [Planning](#planning)
    - [Updates](#updates)

    <!-- /AUTO:TOC position=0 -->

When source has NO toc macro, no AUTO:TOC block is emitted — nothing
rides on round-trip.

### Sentinel-aware diff

All `AUTO:<KIND>` regions (open through close inclusive) are stripped
from `normalize_for_diff` before computing any divergence diff. This
means re-rendering an AUTO region — even with different child names or
issue rows — is treated as a no-op by `classify_adopt`. Re-adopting an
unmodified file returns `in_sync` regardless of how the manifest or
the Jira backend changed.

The same strip rule covers the older `confluence-side: <kind>` paired
zone-marker form (0.7.0+) and solo zone-marker comment lines.

## Cross-page attachment resolution (task 134, v0.11.0)

The Atlassian REST `body.atlas_doc_format` endpoint emits the literal
string `"UNKNOWN_MEDIA_ID"` for media nodes whose attachment lives on a
different page than the one being fetched. Storage XHTML preserves the
original `<ri:attachment ri:filename="X.docx" ri:content-title="Source Page">`,
so the adopt pipeline dual-fetches and pairs:

1. Normalizer detects `media.attrs.id == "UNKNOWN_MEDIA_ID"` (or the
   `__fileName=="UNKNOWN_ATTACHMENT"` / empty `id`+`collection` variant)
   and tracks each occurrence in `NormalizationReport.cross_page_unknowns`
   with structural position. The markdown carries a `<<crosspage:N>>`
   placeholder.
2. Action layer fetches `body.storage` for THIS page (or reads
   `--storage-xhtml-input` if supplied), runs `parse_storage_xhtml`,
   and pairs ADF unknowns with `<ri:attachment>` elements by traversal
   order (`pair_unknowns_to_storage` filters Storage to those with a
   `ri:content-title`, since same-page attachments lack that attribute).
3. For each pair the resolver:
   - Looks up source-page-id from `--cross-page-source-map` (a JSON
     object the agent supplies with `{title: page_id}` mappings — agent
     resolves these via `searchConfluenceUsingCql title="..."` MCP calls)
   - Calls `list_attachments_by_filename(source_page_id)` to find the
     attachment record and its `fileId` (v2 media UUID)
   - Downloads the binary into THIS page's `<page-folder>/images/<filename>`
     via the cookie bridge
   - Rewrites the markdown placeholder with a clean file-card link plus
     the round-trip marker carrying `source-page=<id>` for provenance:
     `[<filename>](images/<filename>)<!-- media id=<uuid> collection=contentId-<source-id> source-page=<source-id> source-page-title="<title>" -->`
4. Graceful degradation: if any step fails (cookies unavailable, source
   page not in map, attachment not found, download error), emits a
   `> ⚠️ Cross-page attachment: **<filename>** lives on Confluence page
   [<source page title>](<base-url>/wiki/...). Local copy unavailable;
   view on Confluence.` blockquote — never `UNKNOWN_MEDIA_ID` literal in
   committed markdown. Unresolved entries surface in
   `report.cross_page_unresolved` for follow-up reporting.

New flags on `adopt write`:
- `--storage-xhtml-input <path>`: pre-fetched Storage XHTML file (offline
  workflow / mocked tests)
- `--cross-page-source-map <path>`: JSON object mapping source-page-title
  → source-page-id; lets the agent supply pre-resolved CQL search results

## Common edge cases

| Situation | Action |
|---|---|
| Page contains `page-signatures` macro | The helper tags it as a `<!-- confluence-side: page-signatures -->` placeholder. The plugin layer (`lib/review_plugin/document_control.py`) recognizes the actual macro on `freeze`; adoption preserves it as informational signal only. |
| Page contains macros we don't render | Each becomes a `<!-- confluence-side: <key> -->` placeholder; the report's `extensions` count surfaces them so the user knows. |
| Page contains the **Attachments macro** (`extensionKey="attachments"`) | The normalizer captures the macro's `labels` / `name` / `pageSize` / `_parentId` parameters into `report.attachment_macros` and emits an OPEN+CLOSE sentinel pair with a position marker: `<!-- confluence-side: attachments labels=<x> position=<n> -->` ... `<!-- /confluence-side: attachments position=<n> -->`. After `normalize()` returns and before the snapshot is written, the action layer fetches the page's full attachment list once (with `metadata.labels` expanded), filters per-macro by labels (comma-separated → OR semantics) and optional name substring, renders a `\| Filename \| Size \| Modified \| Labels \|` markdown table between the sentinels, and queues unique attachment filenames for download via the existing `--download-images` cookie-bridge path. The `labels` parameter is preserved on the OPEN sentinel attribute slot so publish reconstructs the macro on round-trip. The `attach macros` count in the adopt summary surfaces how many were expanded. Failure modes (cookie/auth/HTTP) degrade gracefully — sentinels stay in place so a re-adopt can fill them in later. |
| Page contains attachments | Pass `--download-images` to the helper. Binaries are downloaded via the web-control cookie bridge to `<target-dir>/images/<filename>`, and ADF media refs are rewritten to relative `images/<file>` paths so the markdown renders correctly without authentication. Without the flag, images stay as live Confluence URLs (auth-required to view). The flag is REQUIRED for full bidirectional roundtrip — the publish path expects the relpath form to emit ADF `mediaSingle` nodes. The Attachments-macro expander above also relies on `--download-images` for its file-list downloads. |
| Page was already adopted (target file exists) | Confirm with the user before overwriting. The frontmatter's `adopted_at` would change. |
| Confluence version is 0 / missing | Helper defaults to version 1; surface a warning. |

## Why agent-orchestrated?

Single-page adoption is the right place for the agent to be in the
loop: it judges target-path mapping, surfaces unexpected macros,
decides whether to overwrite an existing file, and writes the commit
message. Bulk adoption (`adopt-tree`) uses the JSON-directive shim
because 95+ pages in a row should not be 95+ agent turns.
