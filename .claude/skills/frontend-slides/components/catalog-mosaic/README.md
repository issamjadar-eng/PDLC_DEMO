---
name: catalog-mosaic
cluster: catalog-cohort
purpose: Paginated 8-per-slide grid for ≥6-row catalog tables — every cell shares one kind-icon when group detection fires.
favors:
  homogeneous_cohort: 0.7
  factual_density: 0.4
requires: [is_catalog_table]
forbids: []
status: existing
---

## When to use

Auto-emitted when a section contains a 2-column table with ≥6 rows representing a homogeneous cohort (teams, integrations, milestones, deliverables, metrics, plus pack-specific cohorts). Splits into 8/slide pages with shared kind-iconography.

## Source shape

```markdown
### 2.2 Source connectors at GA

| Connector | Capability |
|---|---|
| `salesforce-sync` | Bi-directional sync of accounts, contacts, opportunities |
| `stripe-events` | Subscription, invoice, dispute, refund event stream |
| `zendesk-tickets` | Ticket lifecycle + macro / SLA breach signals |
| `segment-cdp` | User-event firehose with identity resolution |
| ...8+ rows ... |
```

## Gotchas

- Triggers `detect_group()`; trunk group whitelist nouns: `persona`, `team`, `rule`, `document`, `milestone`, `metric`. Vocabulary packs (e.g. `medtech`) extend this with domain-specific cohort nouns. Cohorts not on the list still render as mosaic but each cell gets its own keyword-matched icon.
- For people-cohorts specifically, the v0.4 `roster-cards` variant (initials, role, one-liner) is usually a better candidate — md-deck's classifier should propose both.
