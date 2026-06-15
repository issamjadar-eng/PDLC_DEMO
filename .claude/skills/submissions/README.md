# submissions — design & best practices

Authors and maintains a medtech project's FDA submission **content package**
(`docs/project/submissions/<filing>/`) and the JSON sidecars the project-console
**Submission** section renders. See [SKILL.md](SKILL.md) for actions and the
console JSON contract.

## Why this skill exists

Submission content has a distinctive shape that no other skill owns:

- A **three-tier document model** (leading metadata → `🔒 INTERNAL` working
  apparatus → FDA-facing filed body) so one markdown file serves both internal
  review and external transmission, with the 📤/📝/⏸️/📖 scope labels marking
  which content routes where.
- A **`composition-manifest.md`** package-assembly artifact (Required /
  Supporting / strengthener-brief / Excluded buckets, transmission-blocking
  gates, reviewer sign-off) that is itself internal-not-transmitted.
- Per-doc **`_provenance/*.provenance.yml`** audit sidecars mapping every claim
  to its source.

`/tracker` answers *deliverable × phase readiness*; `/dhf-manifest` answers
*are the right documents present per regulation+QMS*; `/change-control` *publishes*
to Confluence/Windchill; `/medtech-docs` *scaffolds the DHF*. None of them author
the FDA-facing Q-Sub narrative or render it for the console. This skill does.

## Producer / consumer split

`render` is the **producer** of the console contract; the project-console
`submission/` package is the **consumer**. The two are loose-coupled exactly like
the gap-analysis and trace-matrix sidecars: the console reads only the JSON; if
the JSON is missing it degrades to "run `/submissions render`". This keeps the
console company-agnostic and lets any producer that emits the same shape light up
the view.

## Design rules followed

- **Ground, don't redeclare.** Submission docs reference canonical facts
  (classifications, predicate K-numbers, PCCP categories) from
  `regulatory-strategy.md` D-REG-* blocks, the system SAD, and `project.yml` —
  per `audit-wiring-before-adding-fields` and `claude-md-references`.
- **Never fabricate** standard / clinical / regulatory content; flag `[VERIFY]`.
- **Vendor-neutral AI provenance** per the `ai-changelog` rule.
- **Demo banners** — every demo doc carries `_Demo sample data — not for clinical use._`.
- **Read READMEs before writing** under `docs/` per `readme-before-write`.

## Best Practices (consumed by `/best-practices`)

- Every filing folder with content has a `composition-manifest.md` and a
  `_provenance/` sidecar per content doc.
- `.console/*.json` is regenerable from the docs via `render` (run `render --check`
  in CI to catch drift).
- Content docs follow the three-tier model; the filed body uses scope labels.
- No fabricated K-numbers, FDA contacts, or guidance titles.

## Changelog

| Version | Date | Summary |
|---------|------|---------|
| 1 | 2026-06-15 | Initial skill (task ben/087). `scaffold` + `render` + `list` actions; `render_sidecars.py` producer of the console `schema_version: 1.0` contract; templates modeled on the arthrex-pccp Q-Sub package shape (three-tier doc model, composition manifest, provenance sidecars). Paired with the project-console Submission section. |
