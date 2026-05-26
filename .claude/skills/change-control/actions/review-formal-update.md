# `change-control review-formal-update <doc>` — agent procedure

Push reconciled local changes; reply to addressed comments; update
the task-doc block. Stays in `state: review-formal`.

## Inputs

    /change-control review-formal-update <doc>

Lifecycle constraint: source `state` must be `review-formal`.

## Steps

  1. Read the task-doc block; collect the `Already Addressed` items
     (each carries an inlineMarkerRef or footer comment id).
  2. For each addressed item, post a reply via:
     - inline: `mcp__atlassian__createConfluenceInlineComment`
       with `parentCommentId=<original comment id>` (use the helper's
       resolution-note text as the reply body).
     - footer: `mcp__atlassian__createConfluenceFooterComment` with
       `parentCommentId=<comment id>`.
  3. Run the publish push pipeline (delegate to the `publish`
     procedure). On divergence, default to **Overwrite** — the task
     doc has already captured reviewer-side body changes via
     `review-formal-status`.
  4. Run

         python actions/review_formal_helper.py update \
             --source <doc> \
             --task-doc <task-doc-path>

     The helper moves Already Addressed → Recently Synced and clears
     the macros listing (it'll be re-populated on the next
     `review-formal-status`).
  5. Commit:

         git add <doc> <task-doc-path> docs/.change-control/snapshots/
         git commit -m "review-formal-update: <doc title> (page <id> v<new-version>)"
