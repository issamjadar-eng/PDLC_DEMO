---
title: <Document Title>
doc_class: design-input         # one of: design-input, vv-protocol, risk-file, working-analysis, ...
state: draft                    # draft | frozen | released — managed by the skill
frozen_at: null
frozen_commit: null
confluence_page_id: null
confluence_version_at_publish: null
jira_ecr: null
windchill_eco: null
---

<!--
  This frontmatter block is the canonical state contract for a controlled
  document under change-control management.

  - `state` is the field the PreToolUse hook checks. Never edit by hand
    once the doc enters the lifecycle — use `change-control:freeze` and
    `change-control:unfreeze` to transition.
  - `doc_class` is keyed to the policy table in change-control.yml.
  - All other fields are populated by the skill at freeze/release time.

  See .claude/skills/change-control/README.md for the full design.
-->
