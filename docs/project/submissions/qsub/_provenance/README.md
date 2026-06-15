# Q-Sub Provenance Sidecars

Per-document audit sidecars for the Q-Sub package. One `<doc>.provenance.yml` per
content doc, mapping every substantive claim to its source, recording which
references were consulted (and which were deliberately skipped), and tracking
open gaps before transmission.

## Conventions

- One file per content doc: `<doc-stem>.provenance.yml`.
- Schema is documented in `.claude/skills/submissions/SKILL.md` (provenance schema) and
  `templates/provenance.template.yml`.
- Authored alongside the doc; never published to FDA — internal QMS provenance only.

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| 2026-06-15 | BX / AI Assistant | Initial provenance sidecars for the demo Q-Sub seed (task ben/087). |
