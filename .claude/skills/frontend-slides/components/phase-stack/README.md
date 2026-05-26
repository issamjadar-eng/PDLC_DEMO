---
name: phase-stack
cluster: time-sequence
purpose: Numbered steps as big-numeral phase blocks — each phase has a giant numeral, a label, and a one-line description.
favors:
  enumerative: 0.6
  hierarchical: 0.3
requires: []
forbids: []
status: new-v0.4
---

## When to use

When the section is an ordered process — `1.→2.→3.` or sequential phases. Inspired by agentic-delivery's `phase-num` / `phase-text` / `phase-label` treatment.

## Source shape

```markdown
### 4.1 Where the handoff actually happens

| Actor | Stage |
|---|---|
| Human · PM | Drafts the task brief and the success criteria |
| Agent · skill | Executes the structural authoring |
| Human · clinical | Reviews each dose-related design input |
```

## Gotchas

- Up to 4 phases per slide; >4 prefers `handoff-relay` (which paginates) or splits.
- Numerals are 1-indexed regardless of source numbering.
