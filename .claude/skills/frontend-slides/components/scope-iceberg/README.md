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
### 1.2 Launch scope at a glance

We are shipping one v1.0 release for the Atlas product line…

- **In scope = Atlas core + dashboards.** The reporting add-on is out of scope for v1.0…
- **Critical-path carve-out (security, billing, telemetry).** Every requirement and design input is tagged.
- **Roadmap envelope.** ...
- **Reporting add-on posture.** Reporting ships **after** the v1.0 release.
```

(The pattern is bipolar scope splits — what's IN vs what's OUT. Substitute your own domain: a feature cut for a SaaS launch, a deal terms split in an investor memo, a plant-cell scope vs deferred lines for a manufacturing rollout, a regulatory filing scope vs out-of-scope modules in a regulated-industry briefing.)

## Gotchas

- Without scope-keywords, this variant doesn't fire today. v0.4's classifier broadens detection via the `bipolar` feature score (presence of "in vs out", "us vs them", "before / after" patterns).
- For carve-outs that aren't truly bipolar (3+ scope tiers), prefer the v0.4 `treemap-grid` (hierarchical breakdown).
