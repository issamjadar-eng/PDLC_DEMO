# {{DOMAIN_NAME}} Strategy

<!-- Assembled: {{TIMESTAMP}} by /strategy assemble -->
<!-- Domain: {{DOMAIN_KEY}} -->
<!-- Sources: {{SOURCE_TASKS}} -->

> This document is auto-assembled from `<!-- STRATEGY CONTENT: {{DOMAIN_KEY}}, ... -->` tags in task documents.
> Do not edit directly — update the source task and run `/strategy assemble {{DOMAIN_KEY}}`.
> Unresolved items are marked with [VERIFY].

## Scope & Approach

_Project-level framing: what this strategy covers, which DHFs it spans, what decisions it records. Populated from the scope subsections of source tasks._

## Plans Informed

| Formal Plan | DHF | How This Strategy Informs It |
|------------|---------|------------------------------|
{{PLANS_INFORMED}}

_The DHF column identifies which DHF each formal plan lives under — formal outputs remain per-DHF under `docs/project/dhfs/<dhf>/...` even though the upstream strategy is shared._

## Strategy Decisions

_Each strategic topic is a level-2 section. Per-component nuance is carried in level-3 callout subsections (`### PCA Device`, `### Connectivity Adapter`, etc.) nested under the topic. Callouts are optional — topics that apply uniformly across all DHFs don't need them._

**Template shape** (authors: follow this pattern when writing tagged strategy content in task docs):

```markdown
## <Strategic Topic>

<project-level framing — the one decision, stated once>

### PCA Device
<how the topic applies to pca-device — specifics, constraints, tradeoffs>

### Connectivity Adapter
<connectivity-adapter specifics — or omit this callout if the topic applies uniformly>

### Cloud Suite
<cloud-suite specifics — or omit>
```

Subsections assembled from tagged task content follow below, in task-ID order.

## Open Items

_Unresolved [VERIFY] markers and items needing human decision._

## Assembly History

_Append-only log of changes across assemblies. Most recent first._

## Source Traceability

| Output Section | Source Task | Source Subsection | Last Modified |
|---------------|-----------|-------------------|---------------|
