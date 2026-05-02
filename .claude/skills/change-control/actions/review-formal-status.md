# `change-control review-formal-status <doc>` — agent procedure

Refresh the formal-review sentinel block from live Confluence
comments + body diff. Preserves any `[x] addressed` items the user
hand-edited between runs.

## Inputs

    /change-control review-formal-status <doc>

Lifecycle constraint: source `state` must be `review-formal`.

## Steps

  1. Read frontmatter; capture `<page_id>`.
  2. `mcp__atlassian__getAccessibleAtlassianResources` → `<cloud_id>`.
  3. Fetch in parallel:
     - `mcp__atlassian__getConfluencePage(cloudId=<cloud_id>, pageId=<page_id>, contentFormat="adf")`
     - `mcp__atlassian__getConfluencePageInlineComments(cloudId=<cloud_id>, pageId=<page_id>, resolutionStatus="open")`
     - `mcp__atlassian__getConfluencePageFooterComments(cloudId=<cloud_id>, pageId=<page_id>)`
  4. Write each response to a temp file under `/tmp/cc-rfs-*.json`.
  5. Run

         python actions/review_formal_helper.py status \
             --source <doc> \
             --task-doc <task-doc-path> \
             --current-adf /tmp/cc-rfs-page.json \
             --inline-comments /tmp/cc-rfs-inline.json \
             --footer-comments /tmp/cc-rfs-footer.json

     The helper:
     - Re-derives Open items (inline keyed by `inlineMarkerRef`,
       footer keyed by comment id).
     - Preserves the user's `[x] addressed` entries — items the user
       moved are NOT moved back to Open even if Confluence still lists
       them as open.
     - Re-emits the Confluence-side macros listing from a fresh
       ADF normalize (informational; not drift).
     - Updates `last_sync` timestamp.
  6. Print the summary line returned by the helper.

## What it does NOT do

  - No body push (that's `review-formal-update`).
  - No comment replies (also `review-formal-update`).
  - No state transition.
