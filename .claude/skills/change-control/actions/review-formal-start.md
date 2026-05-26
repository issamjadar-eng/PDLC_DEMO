# `change-control review-formal-start <doc>` — agent procedure

Capture the current Confluence page version as the review baseline,
write a sentinel block to the active task doc, transition the source
to `state: review-formal`, and print Document-Control workflow start
instructions for the user to follow in the Confluence UI.

## Inputs

    /change-control review-formal-start <doc>

Lifecycle constraint: source `state` must be `published`. The doc must
have `confluence.page_id` already (i.e., it has been published once).

## Steps

  1. Find the active task doc (`tasks/<person>/<NNN>-*.md`).
  2. `mcp__atlassian__getAccessibleAtlassianResources` → `<cloud_id>`.
  3. `mcp__atlassian__getConfluencePage(cloudId=<cloud_id>, pageId=<page_id>, contentFormat="adf")`
     → capture `version.number` as `<baseline>` and webui URL as
     `<page_url>`.
  4. Run

         python actions/review_formal_helper.py start \
             --source <doc> \
             --task-doc <task-doc-path> \
             --page-url <page_url> \
             --baseline-version <baseline> \
             --plugin <change-control.yml review_plugin.type>

     The helper writes a sentinel block to the task doc (preserving
     anything else there), transitions the source's frontmatter
     (`state: published → review-formal`, `confluence.review_baseline_version`).
  5. Print Document-Control workflow start instructions to the user
     (open the Confluence page → click Document Control → Start
     workflow → assign reviewers). Wording matches the
     Google-Docs internal-review handoff style.
  6. Commit:

         git add <doc> <task-doc-path>
         git commit -m "review-formal-start: <doc title> (page <id> v<baseline>)"
