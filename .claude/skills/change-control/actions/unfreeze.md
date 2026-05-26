# `change-control unfreeze` — agent procedure

Reopen a frozen doc back to `published`. Pure-local frontmatter
mutation — no MCP, no Jira write. The agent is responsible for warning
the user that the prior approval is invalidated.

## Inputs

    /change-control unfreeze <doc>

Lifecycle constraint: `state` must be `frozen`.

## Steps

  1. Run

         python actions/freeze_helper.py unfreeze --source <doc>

     The helper checks state, clears `confluence.frozen_at_version`,
     records `confluence.unfrozen_at`, transitions
     `state: frozen → published`, and prints a WARNING line about
     informing the review tool to mark the page Superseded.
  2. Surface the WARNING to the user verbatim.
  3. Commit the frontmatter change:

         git add <doc>
         git commit -m "unfreeze: <doc title> (page <page_id>)"

## What `unfreeze` does NOT do

  - Does not transition the review tool's workflow back. v0.6 is
    manual UI handoff — the user marks the page Superseded in
    Confluence themselves.
  - Does not push the body. The Confluence page is unchanged.
  - Does not delete the prior `confluence.approval` evidence
    snapshot — it stays in frontmatter as audit history. A future
    `freeze` will overwrite it on the next approval.
