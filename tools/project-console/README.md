# project-console

Local web UI for the PDLC_DEMO project. See [`ARCHITECTURE.md`](./ARCHITECTURE.md) for the definitive rules.

## Quickstart

**Prerequisites:**
- [`uv`](https://docs.astral.sh/uv/) on PATH
- [Claude Code](https://docs.claude.com/en/docs/claude-code) installed and logged in (`claude login`)
- `ANTHROPIC_API_KEY` **must not** be set — this tool authenticates via Claude Pro/Max OAuth only

**Run:**
```bash
./run.sh
```

Open http://127.0.0.1:8765.

## What's here (v1)

- **Agents** — chat with KOL domain agents individually or as a panel. Each agent is a markdown file under `domain_agents/` that references its grounding sources (KOL profile, device registry, regulatory filings).
- Dashboards and workflows are scaffolded in `ARCHITECTURE.md` but not yet built.

## Adding a domain agent

Drop a new `.md` file into `domain_agents/` with YAML frontmatter. See existing KOL files for the shape.
