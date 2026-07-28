# The INTERNAL-block & metadata conventions (full spec)

Read this when authoring a public-doc draft or extending the strip/lint logic. SKILL.md carries the short version; this is the complete reference.

## Why these conventions exist

An external document has two layers:
- **The public layer** — what ships in the PDF/HTML the audience reads.
- **The internal layer** — goals, target audience, campaign linkage, source citations, positioning rationale, talk-track, and "why we framed it this way." This substantiates the public claims and grounds a companion conversational agent (e.g., a Gem), but must never appear in the published artifact.

Keeping both layers in **one source file** (rather than a public doc + a separate notes doc) means the evidence lives right next to the claim it backs, and the two can't drift apart. The strip step is what separates them at publish time.

## The metadata frontmatter

A draft opens with a YAML frontmatter block keyed under `public_doc:`. It is internal metadata — `strip` removes it entirely (pulling out `title` so the renderer can still set the document title).

| Field | Meaning |
|-------|---------|
| `title` | Document title (also becomes the rendered `<title>` / H1). |
| `doc_type` | `whitepaper` \| `article` \| `one-pager` \| `brief`. |
| `status` | `draft` \| `in-review` \| `approved` \| `published`. Lifecycle state. |
| `goals` | List — what the document should *achieve* (outcomes, not topics). |
| `audience.primary` / `audience.secondary` | Who must act; who else reads. |
| `campaign` | Campaign name/id this doc is tied to, or `none`. |
| `owner` | Accountable author. |
| `version` / `updated` | Draft version + ISO date. |
| `public_filename` | Output basename (no extension) for `build`. |
| `brand_profile` | Which profile in `tools/public-doc/brand.yml` to apply (e.g., `default`). |

The schema is open — projects may add fields. Anything under `public_doc:` is internal by definition and is stripped.

## The INTERNAL block

Both markers must always sit **inside HTML comments** — that is the invariant that keeps internal content out of the published artifact. There are two valid forms.

### Form 1 — collapsible block (primary; use for metadata + multi-line context)

Paired comment sentinels wrap a `<details>` element. The block **folds away** in any view that renders `<details>` (GitHub, VS Code preview), so the author sees the public content by default and can expand the internal context on demand:

```markdown
<!-- INTERNAL:BEGIN <label> -->
<details>
<summary>🔒 INTERNAL — <what's inside> (stripped on publish)</summary>

... internal metadata / context / evidence, any markup, even `-->` ...

</details>
<!-- INTERNAL:END -->
```

- **Collapsible** — the point of this form. Use it for the pre-Section-1 metadata block (purpose, audience, goals, key points, thesis) and for any multi-paragraph rationale/evidence.
- **Everything before the first public section should be one of these.** The title stays public; purpose/audience/planning go inside.
- Tolerates `-->` and arbitrary markup in the body, because `strip` anchors on the `INTERNAL:END` sentinel, not on the first `-->`.
- **Tradeoff:** the `<details>` body is in the HTML DOM until stripped (collapsed, but present). So **always publish via `build`** (which strips + verifies); never publish the raw `.md`.

### Form 2 — single comment (terse alternative; one-line notes)

Both markers inside one HTML comment. Fully hidden in every view, even unstripped:

```markdown
<!-- INTERNAL:BEGIN <label>
one short note or citation
INTERNAL:END -->
```

- Best for a quick inline note next to the claim it backs.
- **Constraint:** the body must not contain `-->` (it closes the comment early). `lint` flags that as a leak. For anything longer than a line, use Form 1.

`<label>` (optional, both forms): `metadata`, `evidence`, `rationale`, `citation`, `talk-track`, `todo` — surfaced by lint.

### The invariant: markers live inside comments

Whichever form, every `INTERNAL:BEGIN` / `INTERNAL:END` must be inside an HTML comment. The one thing that does **not** work is a bare marker in plain text:

```markdown
INTERNAL:BEGIN          ← NOT inside <!-- -->; this line and the content render
content that will ship
INTERNAL:END
```

`lint` computes the HTML-comment spans and flags any INTERNAL marker that falls outside one as a **leak** (this also catches a Form-2 block whose stray `-->` closed the comment early, leaving `INTERNAL:END` exposed).

## How strip decides what to remove

`scripts/strip_internal.py`:
1. Errors if `INTERNAL:BEGIN` / `INTERNAL:END` counts are unbalanced (malformed).
2. Removes the leading `public_doc:` frontmatter (keeps `title` for the renderer).
3. Removes every block from `<!-- INTERNAL:BEGIN …` through the next `INTERNAL:END -->` — this single rule covers **both forms** (collapsible and single-comment), including any `<details>`, markup, or `-->` between the sentinels.
4. Collapses the blank lines the removals leave behind.
5. **Verifies** no `INTERNAL:` marker remains; if one does, it aborts with a non-zero exit. The safety net — a leak is the one failure this skill must never allow.

## Lint categories

`scripts/lint_doc.py` is advisory (always exits 0) and reports:
- **leak** — unbalanced markers, or any INTERNAL marker not inside an HTML comment (covers bare markers and Form-2 early `-->` close). (Slated to become a hard gate later — see README roadmap.)
- **brand** — banned phrases, non-canonical names, missing required disclaimers (from `brand.yml`).
- **style** — banned/weasel words, regex style flags (from `lint-rules.yml`).
- **verify** — `[VERIFY]` flags left in *public* text (a `[VERIFY]` inside an INTERNAL block is fine — it's a note to self).

Brand and style checks run against the *public text only* (INTERNAL blocks are blanked first), so internal notes never trip a brand/style finding.
