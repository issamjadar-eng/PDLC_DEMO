---
name: handoff-relay
cluster: process-handoff
purpose: Sequential who-does-what relay — actor cards in a flowing sequence with passing-the-baton arrows between.
favors:
  enumerative: 0.4
  hierarchical: 0.3
requires: []
forbids: []
status: existing
---

## When to use

When the title or content corpus contains handoff-keywords: "handoff", "who does what", "human/agent", "human-agent", "agent/human". Particularly strong for human-AI collaboration workflows where each step has a named actor.

## Source shape

```markdown
### 4.1 Where the handoff actually happens

| Actor | Stage |
|---|---|
| Human · PM | Drafts the task brief and the success criteria |
| Agent · skill | Executes the structural authoring |
| Human · domain SME | Reviews each substantive design input for accuracy |
| Agent · summarizer | Generates the cross-team status summary |
| Human · approver | Signs off on the release-blocking decisions |
| Agent · qa | Drafts the test protocol and traceability matrix |
```

(Use handoff-relay for any sequential collaboration: a software release pipeline, a regulatory submission flow, a finance close cycle, a manufacturing changeover, a content-publication chain. Each row is one actor + one stage.)

## Gotchas

- For non-sequential parallel processes (multiple actors working concurrently), prefer the v0.4 `swimlane` variant.
- For cyclic feedback loops, prefer the v0.4 `loop-diagram`.
