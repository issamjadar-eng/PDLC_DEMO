# `change-control publish` — agent procedure (Option A)

Push a local markdown source to its Confluence page. Either creates a
new page (when no `confluence.page_id` in frontmatter) or updates the
existing page with **divergence detection** + **Confluence Zone
preservation**.

## Inputs

    /change-control publish <doc>

The doc must be in `state: draft` or `state: published`. Refuse if
state is `review-formal`, `frozen`, or `released`.

## Pre-flight

1. Read the doc's HTML-comment YAML frontmatter (`lib/frontmatter`).
2. Validate state ∈ {`draft`, `published`}. Otherwise fail loud with a
   one-line message: "publish requires state in {draft, published}; got <state>."
3. Read `confluence.base_url` + `confluence.space_key` from
   `change-control.yml`. If missing, fail loud.

## Step 1 — Resolve cloudId

`mcp__atlassian__getAccessibleAtlassianResources`. Pick the resource
matching `base_url`, capture `<cloud_id>`.

## Step 2 — Branch on first-publish vs update

If frontmatter has no `confluence.page_id`:
  - First publish. Skip divergence detection.
  - The existing-ADF path is empty.

If frontmatter has `confluence.page_id`:
  - Existing page. Fetch its current ADF:
        mcp__atlassian__getConfluencePage(
            cloudId=<cloud_id>,
            pageId=<page_id>,
            contentFormat="adf",
        )
  - Write the response to a temp file `/tmp/cc-publish-current-adf.json`.

## Step 3 — Run `precheck`

    python actions/publish_helper.py precheck \
        --source <doc> \
        --current-adf /tmp/cc-publish-current-adf.json  # only for existing pages
        [--page-index docs/.change-control/page-index.json]

The helper prints a JSON precheck packet:

    {
      "page_id": "<id or empty>",
      "last_published_version": <N>,
      "is_first_publish": true|false,
      "transformed_body_chars": <int>,
      "transform_report": {...},
      "zones_captured": [{name, title, content}, ...],
      "diverged": true|false,
      "current_version": <int>,
      "their_diff": "<unified diff or empty>",
      "snapshot_present": true|false
    }

Save `zones_captured` to `/tmp/cc-publish-zones.json` for use in the
splice step. Display the `transform_report` summary to the user
(rewrote N links, missed M, swapped K fences, stripped frontmatter).

## Step 4 — Divergence prompt

If `diverged == false`, skip this step.

If `diverged == true`, present:

    Confluence has been updated since your last push (their version: <N>; your last: <M>).
    What do you want to do?
      [O] Overwrite — push your version, discard their body changes
                      (Confluence Zones survive; comments are unaffected)
      [M] Merge — write Confluence-side as `<doc>.confluence-side.md`;
                  open both in your editor; reconcile manually; re-run publish
      [A] Abort — no push

Default for first-publish: not applicable.

  - **Overwrite**: continue to Step 5.
  - **Merge**: run

        python actions/publish_helper.py write-confluence-side \
            --source <doc> --current-adf /tmp/cc-publish-current-adf.json

    then exit. Tell the user which file to reconcile + that re-running
    `publish` will resume after they save.
  - **Abort**: exit, no changes.

## Step 5 — Get the body bytes (markdown + ADF + images sidecar)

For first-tier markdown push:

    python actions/publish_helper.py body \
        --source <doc> [--page-index ...] > /tmp/cc-publish-body.md

For the second-tier ADF push (zone splice + image media-nodes), build
the ADF body and capture the images sidecar in one shot:

    python actions/publish_helper.py adf-body \
        --source <doc> [--page-index ...] \
        --emit-images-sidecar /tmp/cc-publish-images.json \
        > /tmp/cc-publish-adf.json

The sidecar is a JSON list of every local-image placeholder the ADF
emitter laid down — each entry `{placeholder, source_relpath, alt}`.
Empty list = no images on this page = skip the upload step in Step 7b.

### Smartcard round-trip contract (REQUIRED)

`adopt` writes Confluence smartcards as
`[<resolved title>](<URL>)<!-- smartcard -->` (markdown link followed by
an HTML-comment marker). The marker is invisible in normal markdown
rendering. **The publish-side body builder MUST detect this marker and
emit an ADF `inlineCard` node, not a plain link mark.** Otherwise
round-trip turns smartcards into ordinary links, losing Confluence's
smart-rendering semantics on push.

Builder pseudocode:
```
for each [text](url)<!-- smartcard --> match:
    emit ADF inlineCard {"type": "inlineCard", "attrs": {"url": url}}
    (drop the resolved label — Confluence client re-resolves it)
for each plain [text](url):
    emit ADF text node with link mark
```

Same contract applies to autolink form `<URL><!-- smartcard -->` (rare
— used when no page-id was extractable during adopt). Round-tripping
must preserve marker comments verbatim through the markdown_transform
pipeline.

## Step 6 — Push (markdown)

For first publish:

    mcp__atlassian__createConfluencePage(
        cloudId=<cloud_id>,
        spaceId=<space_id from getAccessibleAtlassianResources>,
        title=<doc title from frontmatter>,
        parentId=<parent_page_id from frontmatter, if set>,
        body=<contents of /tmp/cc-publish-body.md>,
        contentFormat="markdown",
        versionMessage="publish: <doc>",
    )

For subsequent publish:

    mcp__atlassian__updateConfluencePage(
        cloudId=<cloud_id>,
        pageId=<page_id>,
        title=<doc title>,
        body=<contents of /tmp/cc-publish-body.md>,
        contentFormat="markdown",
        versionMessage="publish: <doc>",
    )

Capture the response's `id` and `version.number` as `<new_page_id>` and
`<new_version>`.

## Step 7 — Re-fetch + zone splice

This step is skipped if `zones_captured` was empty.

    mcp__atlassian__getConfluencePage(
        cloudId=<cloud_id>,
        pageId=<new_page_id>,
        contentFormat="adf",
    )

Write the response to `/tmp/cc-publish-new-adf.json`. Run:

    cat /tmp/cc-publish-new-adf.json | python actions/publish_helper.py splice \
        --zones /tmp/cc-publish-zones.json > /tmp/cc-publish-spliced.json

Then push the spliced ADF body:

    mcp__atlassian__updateConfluencePage(
        cloudId=<cloud_id>,
        pageId=<new_page_id>,
        title=<doc title>,
        body=<contents of /tmp/cc-publish-spliced.json>,
        contentFormat="adf",
        versionMessage="publish: <doc> (zones spliced)",
    )

Capture the new version as `<final_version>`.

## Step 7b — Image upload + ADF media-id patch

This step is skipped if the images sidecar from Step 5 was empty.

**Orphan-file (no-marker) round-trip (task 134, v0.11.0)**: Users can drop
a file in `<page>/images/` and reference it from markdown with a plain
`[label](images/X.pdf)` link OR `![alt](images/X.png)` image — NO
`<!-- media -->` round-trip marker required. `_md_to_adf` recognizes any
markdown link/image whose destination starts with `images/` (relative,
no scheme) as a Confluence-attachment binding regardless of marker
presence. Image extensions (`.png`, `.jpg`, `.gif`, `.svg`, `.webp`, etc.
— see `lib/mime.py:IMAGE_EXTENSIONS`) emit `mediaSingle` with image
attrs; everything else (`.pdf`, `.docx`, `.xlsx`, `.csv`, `.zip`) emits a
file-card. The sidecar collects orphan files and marker-tagged ones
uniformly, so `upload-images` picks them all up. After publish + re-adopt,
the markdown gets a proper round-trip marker — symmetric, no manual
marker bookkeeping.

Local images are referenced in the ADF body as `mediaSingle` nodes
whose `attrs.id` is the placeholder string `PLACEHOLDER:images/<file>`.
Confluence's renderer accepts unknown placeholder ids on the initial
push (the image just renders as broken until patched), so the
sequencing is:

  1. Initial create/update push (Step 6) lays the page down with
     placeholder media nodes — page exists with a known `<new_page_id>`.
  2. Upload each binary as an attachment to `<new_page_id>` and
     collect the resulting `{placeholder: real_attachment_id}` map.
  3. Patch the ADF body, replacing every placeholder with its real
     id, then `updateConfluencePage` again with the patched ADF.

Concretely:

    # 1. Upload binaries — emits a {placeholder: media_id} map on stdout.
    python actions/publish_helper.py upload-images \
        --sidecar /tmp/cc-publish-images.json \
        --source-dir "$(dirname <doc>)" \
        --page-id <new_page_id> \
        --base-url <base_url> \
        > /tmp/cc-publish-image-map.json

    # 2. Patch the ADF body with real ids.
    cat /tmp/cc-publish-adf.json | python actions/publish_helper.py patch-adf \
        --map /tmp/cc-publish-image-map.json \
        > /tmp/cc-publish-adf-patched.json

    # 3. Push the patched ADF.
    mcp__atlassian__updateConfluencePage(
        cloudId=<cloud_id>,
        pageId=<new_page_id>,
        title=<doc title>,
        body=<contents of /tmp/cc-publish-adf-patched.json>,
        contentFormat="adf",
        versionMessage="publish: <doc> (image media-ids patched)",
    )

Failure modes the agent should watch for:
  - **Cookie bridge unavailable** — `upload-images` exits non-zero with
    a stderr hint. Recovery: run `/web-control launch`, sign in to
    Confluence (check "Remember me"), retry. The page is still
    published; only inline images are missing.
  - **One image upload fails** — that placeholder stays as
    `PLACEHOLDER:...` in the patched ADF. Confluence renders it as a
    broken image. The user can re-run publish to retry just the
    failed binaries.

## Step 8 — Commit frontmatter + snapshot

    python actions/publish_helper.py commit \
        --source <doc> \
        --page-id <new_page_id> \
        --version <final_version>

This updates frontmatter (`state: published`, `confluence.last_published_version`,
`confluence.last_published_at`) and writes the new snapshot at
`docs/.change-control/snapshots/<page_id>-<version>.md`. Older
snapshots for that page are pruned automatically.

## Step 9 — Git commit

    git add <doc> docs/.change-control/snapshots/
    git commit -m "publish: <doc title> (page <new_page_id> v<final_version>)"

If the user passed `--no-commit`, skip and report which files changed.

## Failure modes

| Situation | What to do |
|---|---|
| MCP unreachable | Fail loud — print "Run `/mcp` and verify atlassian shows Connected". Exit non-zero. |
| createConfluencePage rejects (e.g., title collision) | Surface the MCP error verbatim; do NOT retry; tell the user. |
| Divergence + user picks Merge | Stop after writing `.confluence-side.md`. Do not push. Do not modify frontmatter. Snapshots untouched. |
| Splice step fails (e.g., new page has no zone markers because the markdown didn't lay them down) | Skip the splice push — log a warning that captured zones were not re-spliced. The body push from Step 6 still landed. |
| First publish has zones in source | The first push lays the zone markers down with empty interiors; agent should fetch ADF + splice anything we wanted to preserve. (Edge case — usually first publish has no captured zones because there's no prior page.) |

## Sentinel attribute conventions

The publish path round-trips Confluence-owned macros via sentinel
comments in the markdown source. Most are single-line placeholders the
publish helper turns into ADF `extension` nodes (TOC, children,
page-signatures). The **Attachments macro** uses an OPEN/CLOSE pair
so the action layer can splice a per-pull rendered file list between
them at adopt time without contaminating the publish-side ADF:

    <!-- confluence-side: attachments labels=actual position=0 -->
    | Filename | Size | Modified | Labels |
    | --- | --- | --- | --- |
    | [foo.docx](images/foo.docx) | 12.1 KB | 2026-01-15 | actual |
    <!-- /confluence-side: attachments position=0 -->

On publish:

- `_md_to_adf` recognizes the OPEN sentinel, **skips everything until
  the matching CLOSE sentinel** (paired by `position=<n>`), and emits
  a single `extension` ADF node with `extensionKey="attachments"`.
- The macro's `parameters.macroParams` are reconstructed from the
  OPEN sentinel's attribute slot. Currently honored attributes:
  `labels=<value>` and `name=<value>`. The position marker is
  publish-internal and is not emitted into ADF.
- The rendered file-list table is **dropped** — the live attachment
  list is per-pull metadata that the rendering server fills in
  natively. Only the macro-with-its-params survives the round-trip.

When extending the sentinel attribute schema in future (e.g., for
a `jira` macro expander), follow the same convention: lowercase
`key=value` separated by single spaces inside the OPEN sentinel,
unique `position=<n>` per occurrence, `/key` prefix on the CLOSE.
The publish-side parser is regex-based and accepts any leading
attribute order.

### AUTO sentinel kinds (task 131, v0.10.0)

In addition to the lowercase `confluence-side: <kind>` form, v0.10.0
introduces an uppercase / dashed AUTO form for content the action layer
**regenerates** on every adopt — the sentinels live in the markdown,
the rendered content between them is treated as auto-output:

    <!-- AUTO:CHILD-INDEX source=children depth=2 position=0 -->
    - [Child A](child-a.md)
    - [Child B](child-b.md)
    <!-- /AUTO:CHILD-INDEX position=0 -->

    <!-- AUTO:JIRA-LIST source=jira jql=project%3DSEC%20AND%20status%3DOpen position=0 -->
    | Key | Summary | Status | Updated |
    ...
    <!-- /AUTO:JIRA-LIST position=0 -->

On publish, `_md_to_adf` recognizes both AUTO kinds, skips to the
matching CLOSE, and emits a single ADF `extension` node:

| AUTO kind | `source=` | Reconstructed extensionKey | Reconstructed params |
|-----------|-----------|----------------------------|----------------------|
| `CHILD-INDEX` | `children` | `children` | `depth` (if present) |
| `CHILD-INDEX` | `pagetree` | `pagetree` | `depth` (if present) |
| `CHILD-INDEX` | `stub-container` | (none — fully stripped, no extension emitted; preceding `## Child pages` heading also dropped) | n/a |
| `JIRA-LIST` | `jira` | `jira` | `jqlQuery` (decoded from percent-encoded `jql=` attribute) |
| `PAGE-TITLE` | (none) | (none — fully stripped, no extension emitted; the title goes through the API's `title` argument, not the body) | n/a |
| `TOC` | `toc` | `toc` | `minLevel`, `maxLevel` (both reconstructed from sentinel attrs when present) |

**Round-trip contract**: the rendered content inside the AUTO region is
per-pull metadata. Confluence regenerates child indexes and jira tables
natively from the source macro on the rendering server, so the action
layer never tries to push the rendered table back. Only the source
macro (or, for `stub-container`, nothing at all) survives the round-trip.

**Diff-canonical form**: `lib/divergence.py:strip_auto_regions` removes
every AUTO/zone region (open through close inclusive) before any
divergence diff. This is what makes auto regions safe — re-adopting an
unmodified file always classifies as `in_sync` even though the literal
bytes inside the AUTO region may differ between renders.

## Why agent-orchestrated?

`publish` is interactive: divergence prompts, conditional push paths,
zone splicing, and commit-message authoring all benefit from the
agent being in the loop. The bulk pattern (Option B) wouldn't help —
we never publish more than one doc at a time, and the value of the
agent's judgment on a divergence outweighs the per-doc turn cost.
