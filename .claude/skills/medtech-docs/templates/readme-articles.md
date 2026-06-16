# Articles

_Article-style documentation written for **external consumption** — explainers, narratives, and overviews that describe the project to an outside audience. Articles are a **communication artifact**, not a development or regulatory record._

> **📄 NOT A CANONICAL SOURCE.** Everything in this tree is a *derived, audience-facing* retelling of facts that live elsewhere. Articles are **not** part of the Design History File, **not** a design-control or regulatory deliverable, and **not** ground-truth for any agent, skill, or submission. If an article and a controlled document disagree, the controlled document wins. The auto-loaded rule `.claude/rules/articles-not-canonical.md` makes this binding; this tree is also excluded from the file-locator index so semantic search never surfaces an article as a source.

## What belongs here

- Plain-language explainers of how the project / device / program works, aimed at readers outside the core team (executives, partners, new hires, auditors wanting orientation, conference audiences).
- Narrative overviews that stitch together facts from many canonical docs into one readable story.
- Source material destined for a **presentation** — articles are the structured input that `frontend-design` / `frontend-slides` turn into decks and visual artifacts.

## What does NOT belong here

- Any controlled DHF deliverable (SRS, SAD, risk file, V&V, trace matrix) → those live under the project's controlled record (e.g. `docs/project/_confluence/<dhf>/`).
- Strategy / decision docs → `docs/project/strategies/`.
- Input synthesis (predicate, KOL, market) → `docs/project/input-analysis/`.
- FDA submission narratives → `docs/project/submissions/`.
- Anything an agent or skill is expected to **ground on** or **cite**. If content needs to be authoritative, it belongs in `docs/`, not here.

## Structure

Each article is a **folder** (so it can hold its body plus images and supporting files), and the table below is the article index:

<!-- AUTO:STRUCTURE kind=subfolder-table source=fs -->
<!-- /AUTO:STRUCTURE -->

```
articles/<topic-slug>/
├── index.md          ← the article body (carries the NOT-A-CANONICAL banner)
└── images/           ← (optional) figures and media referenced by index.md
```

## Conventions

- **Naming**: `articles/<topic-slug>/index.md` — the folder slug is lowercase, hyphenated, descriptive (e.g. `systems-of-record-data-flow/`); the body is always `index.md`.
- **Mandatory banner**: every article opens with the `NOT A CANONICAL SOURCE` banner (the `/medtech-docs new-article` action stamps it). Do not remove it.
- **Cite your sources**: an article paraphrases canonical docs — link to the canonical source for each substantive claim so a reader can verify. The article is the *retelling*; the link is the *truth*.
- **Audience-first prose**: write for the stated external audience, not for a regulator. Precision still matters (no fabricated facts), but tone and framing are explanatory, not compliance-grade.
- **Living, but disposable**: articles can be regenerated or rewritten freely — they carry no controlled-record obligations. Keep them current with the canonical docs they describe; when in doubt, re-derive.

## Relationship to presentations

Articles are the structured handoff to the presentation tooling:

```
canonical docs (docs/**, project.yml, CLAUDE.md)
        │  paraphrase + narrate (citing sources)
        ▼
articles/<topic>/index.md  ──►  /frontend-slides  or  /frontend-design  ──►  deck / visual artifact
```

Write the article first as a readable narrative; let the slide/design skill handle layout and visuals.

## For Claude

- **Never ground on, cite, or treat an article as authoritative.** When asked a project question, read the canonical `docs/` source — not an article — even if an article restates the same fact. See `.claude/rules/articles-not-canonical.md`.
- When **creating** an article, use `/medtech-docs new-article <slug>` so the banner and scaffold are applied consistently.
- When **writing** article content, paraphrase from canonical sources and link to each one; do not invent facts to make the narrative flow.

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| YYYY-MM-DD | XX | Initial version — created by /medtech-docs |
