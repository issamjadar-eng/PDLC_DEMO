---
name: scope-iceberg
cluster: cause-explanation
purpose: "What's in / What's out" carve-out rendered as the iceberg metaphor — visible above the line, hidden below.
favors:
  explicit_scope: 1.0
  bipolar: 0.5
requires: []
forbids: []
status: existing
---

## When to use

When the title or content corpus contains scope-keywords: "filing scope", "carve-out", "carve out", "in vs out", "in-scope", "out of scope", "scope of". Pulls the bipolar split into above-water / below-water layout.

## Source shape

```markdown
### 1.2 Filing scope at a glance

We are filing one 510(k) for the SP6500 hardware…

- **Filing scope = SP6500 pump + DLM.** PAM is out of scope…
- **Critical-requirement carve-out (CtS / CtF / CtP).**
- **PCCP envelope.** ...
- **PAM filing posture.** PAM is **outside** the SP6500 filing.
```

## Gotchas

- Without scope-keywords, this variant doesn't fire today. v0.4's classifier broadens detection via the `bipolar` feature score (presence of "in vs out", "us vs them", "before / after" patterns).
- For carve-outs that aren't truly bipolar (3+ scope tiers), prefer the v0.4 `treemap-grid` (hierarchical breakdown).
