---
name: versus-split
cluster: comparison
purpose: Two columns side-by-side with one accent color per column — us vs. them, in scope vs. out of scope, ours vs. theirs.
favors:
  bipolar: 0.7
  factual_density: 0.3
requires: []
forbids: []
status: new-v0.4
---

## When to use

When content is a side-by-side comparison without a temporal arrow (which would prefer `before-after`). Each column carries its own bullets.

## Source shape

```markdown
### 1.2 Filing scope at a glance

- **Filing scope = SP6500 pump + DLM.** PAM is out of scope…
- **PAM filing posture.** PAM is outside the SP6500 filing.
```

When the section is dominated by an in/out / mine/yours framing, the renderer splits items by polarity keywords ("scope", "in", "out", "us", "them"). Falls back to first-half / second-half split.

## Gotchas

- Best with 4 items (2 per column); 6 max.
- For 3-state comparisons (good/neutral/bad), prefer `delta-table`.
