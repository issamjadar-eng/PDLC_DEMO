# {{PROJECT_NAME}} — Project Changelog

Reverse-chronological record of significant project activity. Populated by the `/digest log` action of the `digest` skill. New sections land at the top of this file after every run; the `## YYYY-MM-DD HH:MM UTC — <title>` header on the most recent section is the since-cursor for the next build.

**What lands here:**
- Tasks completed (by ID)
- Skill additions, removals, and version bumps
- Project-structure changes (CLAUDE.md, project.yml, new DHFs, composition manifests)
- Strategy / standards / submissions documentation changes

**What does NOT land here** (by design — intentional noise filtering):
- Commits without a `task NNN:` subject ref that don't touch a trigger path
- `chore:` / `fmt:` / `lint:` / `typo:` style commits (unless they hit a trigger path)
- Individual README stub edits

To capture the full audit trail, use `git log` or `/digest daily`. This file is a curated overview — the 30-second version of "what happened."

**To rebuild:** `/digest log` — Claude will propose a new section, you approve/edit/decline before it's written.

---

<!-- Initial bootstrap entry — /digest log will insert future sections above this line on each run. -->

## {{DATE}} 00:00 UTC — Project changelog initialized

CHANGELOG.md seeded from the `medtech-docs` `changelog-project.md` template. Run `/digest log` to populate the first retrospective section covering project history to date.
