# Development Specification (dev-spec)

The **upstream engineering working tier**. Low-level developer / QA / RA / test working detail that **informs and confirms** the controlled record — implementation/design notes, tool-validation working evidence, simulator source, draft test protocols, and the architect's living design material from which the formal/controlled deliverables are derived.

**dev-spec is _source material_, not a controlled deliverable.** It is deliberately **not** under document control (no version numbers, approval signatures, or sign-off), and it is **not** the legacy waterfall DHF. It is a sanctioned, living, multi-role working layer that feeds the controlled record.

## What belongs here (and what does not)

| Belongs in dev-spec | Does NOT belong in dev-spec |
|---|---|
| Architect's working design notes / "working SAD" source | Controlled design outputs (SAD, SRS, SDD, plans) → controlled-record tier |
| Tool-validation working packages, simulator source, fixtures | Released/approved deliverables with sign-off → controlled-record tier |
| Draft / engineering test protocols and analysis scratch | Submission narratives (Q-Sub/510(k)/PCCP) → `submissions/` |
| Low-level implementation detail below the controlled doc | Strategy / decision framework docs → `strategies/` |
| Cross-functional (dev/QA/RA/test) iteration material | Upstream input synthesis (KOL, market, predicate) → `input-analysis/` |

## Relationship to the controlled record

```
dev-spec/<dhf>/        author / iterate (engineering working source)
      │  informs + confirms (parity: the controlled doc must stay faithful to this)
      ▼
<controlled-record tier>   the regulated mirror — controlled, versioned, governed
      │  publish
      ▼
<system of record>     the formal vault (Confluence / Windchill / etc.)
```

The flow is **dev-spec → controlled record → published**, the reverse of "adopt a controlled page and extract it." dev-spec is also used to **confirm** the controlled record: it is the working detail the controlled document must remain faithful to (a parity/reconciliation relationship).

## Structure

dev-spec mirrors the DHF roster — one subfolder per DHF leaf:

```
dev-spec/
├── README.md          ← you are here
└── <dhf>/             ← one per DHF leaf (system + items)
    ├── README.md      ← per-DHF dev-spec index
    └── <area>/        ← e.g. architecture/, tool-validation/ — engineering working material
```

## Grounding posture (for Claude + advisor agents)

- **Groundable as UPSTREAM SOURCE.** dev-spec is legitimate, current engineering material — agents may read and reason from it as *source/working detail*.
- **NEVER cite it as the canonical/controlled record.** When using dev-spec in any output, state that the source is engineering working material, not a controlled deliverable. The controlled record is the regulated-mirror tier; cite that for any regulatory/DHF claim.
- This is the opposite posture from the deactivated legacy waterfall tree, which must not be grounded on at all.

## Conventions

- **Not under document control** — no version numbers, approval signatures, or change-history requirements on individual files.
- **Naming**: `topic-description.md` (kebab-case), or a numbered series for a multi-part working document.
- Diagrams (Mermaid, etc.) are encouraged — this is working/analysis material.
- Do not move dev-spec files into a controlled tier without going through that tier's formal authoring/governance process.

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| YYYY-MM-DD | XX | Initial version — created by /medtech-docs (dev-spec tier) |
