---
public_doc:
  title: "{{TITLE}}"
  doc_type: whitepaper        # whitepaper | article | one-pager | brief
  status: draft               # draft | in-review | approved | published
  goals:
    - "{{What this document should achieve — outcome, not topic}}"
  audience:
    primary: "{{Who must act on this}}"
    secondary: "{{Optional}}"
  campaign: none              # campaign name/id, or `none`
  owner: "{{Name}}"
  version: 0.1
  updated: {{DATE}}
  public_filename: "{{slug}}" # output name (no extension): <slug>.pdf / <slug>.html
  brand_profile: default      # which profile in tools/public-doc/brand.yml to apply
---

# {{TITLE}}

<!-- INTERNAL:BEGIN metadata -->
<details>
<summary>🔒 INTERNAL — purpose, audience, goals, planning (stripped on publish)</summary>

Everything before the first public section is internal. The `public_doc:` frontmatter
above and this block are removed by `/public-doc build`; the public artifact is the
title plus the sections below.

**Purpose:** {{why this doc exists — outcome}}
**Audience:** primary {{…}} · secondary {{…}}
**Goals:**
- {{outcome 1}}
**Thesis:** {{the one-sentence argument}}
**Key points:** {{the 3–7 load-bearing claims}}

Keep this rich — it also grounds a companion conversational agent (Gem).
</details>
<!-- INTERNAL:END -->

_{{One-line subtitle / who this is for.}}_

## Executive summary

{{The whole argument in one page. Lead with the consequence for the reader.}}

<!-- INTERNAL:BEGIN evidence
Back the summary's load-bearing claims here: sources, data points, the strongest
counter-argument and how we answer it. Flag anything unverified with [VERIFY].
(Single-comment form — fine for short notes; no '-->' inside.)
INTERNAL:END -->

## {{Section}}

{{Body. One idea per section; lead with the point.}}

<!-- INTERNAL:BEGIN rationale -->
<details>
<summary>🔒 INTERNAL — rationale & evidence for this section</summary>

Why this section is framed this way; what we deliberately left out and why;
sources; positioning notes vs. competitors. None of this ships.
</details>
<!-- INTERNAL:END -->

## Takeaways

- {{What the reader should remember / do next.}}
