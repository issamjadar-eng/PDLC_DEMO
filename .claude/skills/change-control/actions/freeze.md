# `change-control freeze` — agent procedure (Option A)

Verify that the configured review plugin reports the doc's Confluence
page as approved, then lock the doc by transitioning state to `frozen`
and writing an audit-trail snapshot to frontmatter.

## Inputs

    /change-control freeze <doc>

Lifecycle constraint: `state` must be `review-formal`. (For projects
without a formal-review tier in v0.6, you can pass `--from published`
to allow the simpler `published → frozen` shape — but the standard
flow goes through `review-formal-start` first.)

## Step 1 — Resolve cloudId

`mcp__atlassian__getAccessibleAtlassianResources` → match
`change-control.yml` `confluence.base_url` → `<cloud_id>`.

## Step 2 — Fetch the page as ADF

    mcp__atlassian__getConfluencePage(
        cloudId=<cloud_id>,
        pageId=<page_id from frontmatter>,
        contentFormat="adf",
    )

Save the response JSON.

## Step 3 — Verify approval via the plugin

The plugin type comes from `change-control.yml` `review_plugin.type`
(default `document_control`).

    cat <mcp-response>.json | python actions/freeze_helper.py verify \
        --source <doc> \
        --plugin <plugin-type>

The helper:
  1. Reads frontmatter; refuses if state is not `review-formal`.
  2. Loads the plugin via `lib.review_plugin.load_plugin(<type>)`.
  3. Calls `plugin.detect_approval(page_id, mcp_shim)`. The shim wraps
     the MCP response so the plugin's `get_page(...)` returns the live
     ADF without another network round-trip.
  4. On `approved=True`: updates frontmatter with
     `confluence.approval = {plugin, approved, page_version, evidence_kind, signers[]}`
     and `confluence.frozen_at_version`, transitions
     `state: review-formal → frozen`, prints a plugin-named success
     line ("DocumentControlPlugin detected approval signatures
     [Alice, Bob] on page <id> v<N>. Transitioning state to 'frozen'.").
  5. On `approved=False`: prints the plugin's named reason and exits
     non-zero. **No interactive fallback** — fail loud per design.

## Step 4 — Commit

    git add <doc>
    git commit -m "freeze: <doc title> (page <page_id> v<page_version>)"

## What `freeze` does NOT do

  - Does not transition the review-tool's workflow state. v0.6 is
    manual UI handoff for that — Document Control's e-signature
    capture happens in the Confluence UI before this command.
  - Does not push the body. The frozen doc is locked for further
    edits, but the Confluence page is whatever it was at the version
    the plugin saw.
  - Does not create or update Jira ECRs. Inline-ECR creation is
    deferred to v0.7.

## Failure modes

| Situation | What to do |
|---|---|
| Plugin returns `approved=False, reason="...page-signatures macro present"` | Surface verbatim; tell the user to complete signatures in the Confluence UI and retry. |
| Plugin not implemented for the configured type (Comala/SoftComply) | The helper prints which plugin is configured and that v0.6 only ships document_control; suggest pinning `review_plugin.type: document_control` or contributing the impl upstream. |
| Doc state is wrong (e.g., `published`, not `review-formal`) | Helper exits 66; tell the user to run `review-formal-start` first. |
| Frontmatter has no `confluence.page_id` | Helper exits 66; tell the user the doc isn't published yet — run `publish` first. |
