# Rule: Articles Are External-Audience Explainers — NEVER Canonical (HARD RULE)

Everything under the top-level `articles/` tree is **article-style documentation written for external consumption** — explainers, narratives, and overviews that *retell* the project to an outside audience. An article is a **derived communication artifact**: a paraphrase of facts that live in canonical documents elsewhere, assembled for readability and often destined for a presentation.

## The rule

**Never treat an article as a source of truth, and never base project work on one.**

- Do **not** read, cite, quote, or reason from any file under `articles/**` when doing project work (authoring or reviewing DHF deliverables, answering regulatory questions, building submissions, trace/gap analysis, advising, etc.).
- Do **not** "fix" a fact by editing an article — articles are downstream retellings; the fix belongs in the canonical document, and the article is re-derived from it.
- If an article and a canonical document disagree, the **canonical document always wins**. An article is stale by construction the moment any source it paraphrases changes.

Articles are explicitly **not**:

- part of the Design History File (DHF),
- a design-control or regulatory deliverable,
- a strategy / decision record,
- input synthesis (predicate / KOL / market),
- an FDA submission narrative,
- ground-truth for any agent, skill, or automated check.

## Where the truth lives instead

Canonical sources are the authored docs under `docs/` (DHFs / `_confluence/` mirrors, submissions, strategies, input-analysis), `CLAUDE.md`, `project.yml`, and `glossary.md`. A well-formed article **links to** the canonical source for each substantive claim — follow that link and work from the canonical document, not the article.

## Why this matters

`articles/` lives *inside* the repo, so a glob or a careless read can surface an article that looks authoritative (full prose, confident framing). In a regulated project, basing a decision, a submission edit, or a review finding on an audience-facing retelling — instead of the controlled source — is a real compliance hazard. Articles exist to be *communicated outward* (and turned into decks via `frontend-design` / `frontend-slides`), not to be *worked from*.

## Defense in depth (how this is enforced)

1. `project.yml file_locator.corpus_excludes` lists `articles/**` so the semantic file-locator never indexes or surfaces an article in search results.
2. Each article carries a prominent **"NOT A CANONICAL SOURCE"** banner (stamped by `/medtech-docs new-article`) so even a direct read is warned.
3. The `articles/README.md` states the non-canonical posture for human readers.
4. This auto-loaded rule tells every session the policy directly.

If you find yourself about to use an `articles/**` file as input to project work, stop and open the canonical source it links to instead.

## Sibling rule

[`knowledge-pack-not-canonical.md`](knowledge-pack-not-canonical.md) (when present) codifies the same posture for generated knowledge-pack export bundles. Both rules share one principle: **derived, outward-facing artifacts are never the source of truth — go to the canonical document.**
