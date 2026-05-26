# `change-control pull` — agent procedure

Read the current Confluence page body, normalize ADF→markdown, and
write `<doc>.confluence-side.md` next to the source. Does NOT push,
does NOT modify the source's frontmatter or snapshot.

Used:
  - On the Merge branch of `publish` divergence handling
  - As an explicit "what does Confluence look like right now" check
  - Before a manual reconciliation when the source has drifted from
    Confluence and the user wants both side by side

## Inputs

    /change-control pull <doc>

`<doc>` must have `confluence.page_id` in frontmatter; otherwise fail
loud — `pull` requires a published doc.

## Steps

  1. Read frontmatter; extract `confluence.page_id`.
  2. `mcp__atlassian__getAccessibleAtlassianResources` → `<cloud_id>`.
  3. `mcp__atlassian__getConfluencePage(cloudId=<cloud_id>, pageId=<page_id>, contentFormat="adf")`
     → write to `/tmp/cc-pull-current-adf.json`.
  4. Run

         python actions/publish_helper.py write-confluence-side \
             --source <doc> --current-adf /tmp/cc-pull-current-adf.json

     The helper normalizes the ADF (collapses smartlinks, tags
     extensions as `<!-- confluence-side: <key> -->`, rewrites media
     to attachment URLs) and writes
     `<doc>.confluence-side.md` next to the source.
  5. Tell the user the file path. Suggest opening it side-by-side
     with the source.

## What `pull` does NOT do

  - No frontmatter mutation (state, last_published_version unchanged)
  - No snapshot writes
  - No commit
  - No three-way merge — just normalizes the current page to markdown

If you want to push reconciled changes, run `publish` after editing
the source.
