# Local Machine Setup Notes — Dmytro

Personal, machine-specific setup notes for working on PDLC_DEMO. Not a task; not project-wide guidance — these are quirks of **this** local machine (macOS).

## Known issue: advisor agent symlinks break after `git pull`

On this machine (macOS), the advisor agent symlinks under `.claude/agents/` break after **any** `git pull`, due to a path-length issue. They must be repaired after every pull.

**Fix (run from the project root):**

```bash
cp .claude/skills/advisors/agents/*.md .claude/agents/
git checkout .claude/agents/project-secops.md
```

- The `cp` replaces the broken advisor symlinks with real file copies from the skill source.
- The `git checkout` restores the `project-secops.md` symlink, which is **not** an advisors-skill agent and must stay as its committed symlink (the `cp` would otherwise leave it wrong).

## "Pull the latest" — full sequence

When I (Dmytro) say **"pull the latest"**, run this complete sequence:

1. **Pull:**
   ```bash
   git pull
   ```
2. **Repair the advisor symlinks** (the known issue above):
   ```bash
   cp .claude/skills/advisors/agents/*.md .claude/agents/
   git checkout .claude/agents/project-secops.md
   ```
3. **Start the console in the background:**
   ```bash
   cd tools/project-console && ./run.sh
   ```
   (`run.sh` is a long-running uvicorn server — launch it in the background. Console serves on http://127.0.0.1:8765.)

## Changelog

- 2026-06-07: Created — documented the post-pull symlink repair and the "pull the latest" sequence.
