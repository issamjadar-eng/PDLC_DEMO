# file-locator — design notes

Reference document for humans. Not loaded by Claude. See `SKILL.md` for the
trigger surface and action specs.

## Design summary

A **file-locator MCP** — given a natural-language query, returns ranked
`(repo-relative-path, summary, heading_anchor?, score)` tuples so the calling
agent decides which whole files to read.

Deliberately **not** a chunked-RAG passage retriever. Doc-heavy and code-heavy
agent workloads (advisors, regulated-design-controls work) need whole-file
coherence — strategy docs with DECISION blocks, SADs with architecture
diagrams, predicate analyses with frontmatter. Chunked retrieval returns the
right kind of content from the wrong file and the agent can't tell.

Complementary to `/dhf-manifest`'s **canonical-role discovery index**:
structural queries ("load the SAD") go through discovery; semantic queries
("where do we argue MDDS?") go through this skill.

## Architecture

```
┌─────────────────────────┐    locate(query, k, scope)    ┌──────────────────┐
│  Calling agent          │ ───────────────────────────▶  │  server.py       │
│  (advisor, ad-hoc CC)   │ ◀───── ranked (path,…)   ──── │  stdio MCP       │
└─────────────────────────┘                               └────────┬─────────┘
                                                                   │
                                                              SQLite read
                                                                   ▼
                                                          ┌──────────────────┐
                                                          │  index.db        │
                                                          │  (committed)     │
                                                          └────────▲─────────┘
                                                                   │
                                                              SQLite write
                                                                   │
┌─────────────────────────┐  walk + extract + embed       ┌────────┴─────────┐
│  rebuild.py             │ ───────────────────────────▶  │  indexer_docs.py │
│  (CLI / CI / cron)      │                               │  + common.py     │
└─────────────────────────┘                               └──────────────────┘
```

- **Indexing**: `rebuild.py` → `indexer_docs.py` walks corpus per gates, hashes
  files, extracts summaries (frontmatter override → auto-extract), embeds via
  `fastembed`, writes to `index.db`.
- **Querying**: `server.py` exposes `locate()` over stdio MCP. Embeds the
  query, blends BM25 + cosine, returns confidence-banded hits.
- **No LLM calls anywhere.** Embeddings are produced by a local ONNX model
  (BGE-small, 384-dim). Summaries are auto-extracted from doc structure.

## Why these choices

| Decision | Rationale |
|---|---|
| **File-level + sub-summaries**, not chunked passages | Strategy docs with DECISION blocks need whole-file context; chunks lose decision boundaries, cross-refs, frontmatter. Sub-summaries handle long docs without chunking. |
| **`fastembed` (ONNX), not sentence-transformers** | Drops PyTorch dep (~2GB → ~100MB). Same model quality. Cross-platform via ONNX runtime. |
| **`BGE-small-en-v1.5`** | 384-dim, ~130MB, strong retrieval baseline. Open source. CPU-only is fine at our scale. |
| **SQLite + FTS5 + sqlite-vec (optional)** | One file, no daemon, no process. FTS5 built-in. Vector search via tiny C extension OR brute-force NumPy cosine (decision deferred to bake-off latency measurements). |
| **Index committed to git** | Zero-setup for new clones, one canonical artifact for the team. CI rebuilds on PR merge. Local rebuilds are session-local refreshes. |
| **2-tier summary authorship** (frontmatter override → auto-extract) | Auto-extract is deterministic, fully local, no Anthropic API calls. LLM-elaboration deferred to v2 if P3 surfaces ranking failures. |
| **Curated 8-skill medtech registry** for skill content | Of 26 skills, 8 carry medtech-functional content (dhf-manifest, medtech-docs, trace-matrix, change-control, tracker, secops, jira-pull, docflow). The rest are tooling or self-help. |
| **v1 docs-only; code as v2** | Code indexing wants tree-sitter symbol maps, not summaries. Different architecture, separate justification. v1 ships narrow. |

## Inclusion gates (4)

1. **`corpus_includes` glob** (allowlist) — see `project.yml`.
2. **`corpus_excludes` glob** (denylist) — universal noise + other-skill-owned state.
3. **`.gitignore` honor** — if a file is gitignored, skip it.
4. **In-doc skip sentinel** — `<!-- file-locator: skip -->` or frontmatter `locator_skip: true`.

DHF content is included via gate 1 (`docs/**/*.md`). Sensitive specific files
use gate 4 as the granular escape hatch.

## Read-count rubric (for calling agents)

Surface this in the advisor template so the 13 advisor agents inherit it:

> Call `locate(query, k=10)`. Read the **top-banded result in full**. If it
> answers the question, stop. If it partially answers, read the next result
> whose summary covers the missing angle. **Stop at 3 reads unless the question
> is inherently multi-source** ("compare X across DHFs", "every place we
> discuss Y"). After 3 reads without an answer, surface the gap to the user.

7 design levers govern convergence:
1. Discriminating summary content
2. Reliable score cliffs in ranking
3. Explicit advisor-template rubric (above)
4. Query-shape inference (single vs multi-source)
5. Soft budget hint (`estimated_tokens` per hit)
6. Confidence banding in the response
7. Result clustering (same-topic hits grouped)

## What's not in v1

- LLM-elaborated summaries (v2 reconsideration if P3 surfaces ranking failures)
- Code indexing (`scope=code` returns empty + reasoning hint in v1)
- `file-locator-researcher` Tier-3 subagent (deferred — depends on P3 results)
- Pre-commit freshness hook (warn-only; deferred until rebuild ownership settles)

## Changelog

- **v2** (2026-06-01) — **Self-healing venv bootstrap.** The `.mcp.json`
  `command` now points at a committed wrapper, `tools/file-locator-mcp/bootstrap.sh`
  (new `templates/bootstrap.sh`), instead of `./.venv/bin/python` directly. The
  wrapper ensures the venv exists — building it with `uv` (stdlib `venv`+`pip`
  fallback) and scrubbing `Icon\r` — before exec'ing the interpreter on
  `server.py`. This closes the recurring "venv gone after a fresh clone or repo
  move → MCP fails `ENOENT`, and `/mcp → Reconnect` can't fix it" gap: only
  `index.db` is committed, never the venv, so the interpreter the launcher
  spawned didn't exist. Reconnect re-runs the wrapper, so the venv now
  self-repairs (one slow launch, then instant). **stdout discipline:** the
  wrapper sits on the MCP stdio pipe, so it emits *only* to stderr — stdout is
  the JSON-RPC channel and any stray byte corrupts the protocol; all build
  output is routed `>&2`. `setup` migrates an existing v1 `.mcp.json` entry
  (venv-interp `command` → wrapper) idempotently. Tracks `ben/074`.
- **v1** (2026-05-12) — Initial scaffold. SKILL.md + scripts (common,
  indexer_docs, rebuild, server) + templates (requirements, project.yml
  snippet, .mcp.json snippet, tool README). Stack: fastembed + SQLite FTS5.
  Curated 8-skill medtech registry. 4-gate inclusion. 2-tier summary
  authorship. Confidence-banded hit response with reasoning hint. Tracks
  `ben/193` for the full design history and design-pivot rationale.
