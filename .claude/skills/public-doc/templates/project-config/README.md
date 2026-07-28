# tools/public-doc — project brand/style/lint config

This directory holds **this project's** brand, style, and lint values for the
`public-doc` skill. The skill is project-agnostic and ships no company values; it
reads them from here at `lint` / `build` time. This is the "subfolder binding"
between the generic skill and this project's specifics.

| File | Purpose | Parsed by |
|------|---------|-----------|
| `brand.yml` | Canonical naming, banned phrases, required disclaimers, per-profile | `lint` (and `build`'s lint pass) |
| `lint-rules.yml` | Banned/weasel words + regex style flags | `lint` |
| `style.md` | Human-readable house style (not machine-parsed) | people |

Scaffolded by `/public-doc init` from the skill's seed templates. Edit freely —
`init` never overwrites an existing file here. Add named profiles in `brand.yml`
and select one per document via the draft's `public_doc.brand_profile` field.
