# `change-control review-formal-abort <doc>` — agent procedure

Cancel an active formal review. Removes the sentinel block from the
task doc and transitions the source back to `published`. Pure-local
— no MCP. The agent is responsible for warning the user to cancel the
review-tool workflow in the Confluence UI.

## Inputs

    /change-control review-formal-abort <doc>

Lifecycle constraint: source `state` must be `review-formal`.

## Steps

  1. Run

         python actions/review_formal_helper.py abort \
             --source <doc> \
             --task-doc <task-doc-path>

     The helper removes the formal-review block from the task doc
     (preserving everything else, including any internal-review block
     for the same source) and transitions the frontmatter
     `state: review-formal → published`.
  2. Print to the user:

         WARNING: This abort is local. To cancel the review-tool
         workflow, open the page in Confluence and:
           - Document Control: cancel the active workflow.
           - Comala: terminate the workflow instance.
           - SoftComply: cancel the active sign-off.
  3. Commit:

         git add <doc> <task-doc-path>
         git commit -m "review-formal-abort: <doc title>"
