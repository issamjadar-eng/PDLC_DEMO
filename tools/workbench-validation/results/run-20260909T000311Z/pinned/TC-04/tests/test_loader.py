"""Unit tests for lib/loader.py — the shared agent + overlay loader."""

import sys
import textwrap
from pathlib import Path

import pytest

# Make the skill's lib importable.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lib.loader import (
    DomainAgent,
    Group,
    apply_overlay,
    load_agent_file,
    load_all,
    resolve_effective_sources,
)


# ---------------------------------------------------------------------------
# Fixtures: write temporary agent files
# ---------------------------------------------------------------------------

def _write(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / f"{name}.md"
    p.write_text(textwrap.dedent(content))
    return p


def _write_project_yml(tmp_path: Path, content: str) -> Path:
    p = tmp_path / "project.yml"
    p.write_text(textwrap.dedent(content))
    return p


# ---------------------------------------------------------------------------
# load_agent_file
# ---------------------------------------------------------------------------

class TestLoadAgentFile:
    def test_cc_native_with_console_block(self, tmp_path):
        path = _write(tmp_path, "regulatory-affairs", """\
            ---
            name: regulatory-affairs
            description: Use for regulatory strategy.
            tools: Read, Glob, Grep, WebFetch
            console:
              title: Regulatory Affairs Assistant
              kind: solo
              group: core-team
              context:
                - docs/architecture/**/*.md
              sources:
                - docs/fda-guidance/**/*.md
                - docs/standards/**/*.md
            ---

            You are an RA assistant.
        """)
        agent = load_agent_file(path)
        assert agent.name == "regulatory-affairs"
        assert agent.title == "Regulatory Affairs Assistant"
        assert agent.description == "Use for regulatory strategy."
        assert agent.kind == "solo"
        assert agent.group == "core-team"
        assert agent.tools == ["Read", "Glob", "Grep", "WebFetch"]
        assert agent.context == ["docs/architecture/**/*.md"]
        assert agent.sources == ["docs/fda-guidance/**/*.md", "docs/standards/**/*.md"]
        assert "RA assistant" in agent.system_prompt

    def test_legacy_flat_frontmatter(self, tmp_path):
        path = _write(tmp_path, "legacy-agent", """\
            ---
            name: legacy-agent
            title: Legacy Agent
            description: Old format.
            kind: solo
            sources:
              - docs/foo/**/*.md
            ---

            Legacy persona.
        """)
        agent = load_agent_file(path)
        assert agent.name == "legacy-agent"
        assert agent.title == "Legacy Agent"
        assert agent.kind == "solo"
        assert agent.sources == ["docs/foo/**/*.md"]
        assert agent.context == []
        assert agent.tools == []

    def test_defaults_when_console_block_absent(self, tmp_path):
        path = _write(tmp_path, "minimal", """\
            ---
            name: minimal
            description: Bare minimum.
            ---

            Just a prompt.
        """)
        agent = load_agent_file(path)
        assert agent.title == "Minimal"  # titleized from name
        assert agent.kind == "solo"
        assert agent.group is None
        assert agent.sources == []
        assert agent.context == []

    def test_comma_separated_tools_split(self, tmp_path):
        path = _write(tmp_path, "comma-tools", """\
            ---
            name: comma-tools
            description: Test.
            tools: Read, Glob, Grep
            ---

            Body.
        """)
        agent = load_agent_file(path)
        assert agent.tools == ["Read", "Glob", "Grep"]

    def test_yaml_list_tools(self, tmp_path):
        path = _write(tmp_path, "list-tools", """\
            ---
            name: list-tools
            description: Test.
            tools:
              - Read
              - Glob
            ---

            Body.
        """)
        agent = load_agent_file(path)
        assert agent.tools == ["Read", "Glob"]

    def test_no_frontmatter_raises(self, tmp_path):
        path = _write(tmp_path, "no-fm", "# Just markdown\nNo frontmatter here.")
        with pytest.raises(ValueError, match="frontmatter"):
            load_agent_file(path)

    def test_name_from_stem_when_missing(self, tmp_path):
        path = _write(tmp_path, "from-stem", """\
            ---
            description: No name field.
            ---

            Body.
        """)
        agent = load_agent_file(path)
        assert agent.name == "from-stem"


# ---------------------------------------------------------------------------
# apply_overlay
# ---------------------------------------------------------------------------

class TestApplyOverlay:
    def _base_agent(self) -> DomainAgent:
        return DomainAgent(
            name="test",
            title="Test",
            description="",
            kind="solo",
            model=None,
            context=["ctx/**/*.md"],
            sources=["src/a/**/*.md", "src/b/**/*.md"],
            system_prompt="prompt",
        )

    def test_add_deduped(self):
        agent = self._base_agent()
        result = apply_overlay(agent, {"add": ["src/c/**/*.md", "src/a/**/*.md"]})
        assert result.sources == ["src/a/**/*.md", "src/b/**/*.md", "src/c/**/*.md"]

    def test_exclude_stored(self):
        agent = self._base_agent()
        result = apply_overlay(agent, {"exclude": ["**/README.md"]})
        assert result.excludes == ["**/README.md"]

    def test_none_overlay_passthrough(self):
        agent = self._base_agent()
        result = apply_overlay(agent, None)
        assert result is agent

    def test_empty_overlay_passthrough(self):
        agent = self._base_agent()
        result = apply_overlay(agent, {})
        assert result is agent


# ---------------------------------------------------------------------------
# load_all
# ---------------------------------------------------------------------------

class TestLoadAll:
    def test_flat_layout_with_overlay(self, tmp_path):
        agents_dir = tmp_path / "agents"
        agents_dir.mkdir()
        _write(agents_dir, "alpha", """\
            ---
            name: alpha
            description: Alpha agent.
            console:
              group: team-a
              sources:
                - docs/alpha/**/*.md
            ---

            Alpha prompt.
        """)
        _write(agents_dir, "beta", """\
            ---
            name: beta
            description: Beta agent.
            console:
              group: team-a
              sources:
                - docs/beta/**/*.md
            ---

            Beta prompt.
        """)
        yml = _write_project_yml(tmp_path, """\
            advisors:
              enabled: [alpha, beta]
              overlays:
                alpha:
                  add:
                    - docs/extra/**/*.md
                  exclude: []
        """)

        agents, groups = load_all(agents_dir, yml)
        assert "alpha" in agents
        assert "beta" in agents
        assert "docs/extra/**/*.md" in agents["alpha"].sources
        assert len(groups) == 1
        assert groups[0].name == "team-a"
        assert len(groups[0].agents) == 2

    def test_enabled_filter(self, tmp_path):
        agents_dir = tmp_path / "agents"
        agents_dir.mkdir()
        _write(agents_dir, "included", """\
            ---
            name: included
            description: In.
            console:
              group: g
            ---
            Prompt.
        """)
        _write(agents_dir, "excluded", """\
            ---
            name: excluded
            description: Out.
            console:
              group: g
            ---
            Prompt.
        """)
        yml = _write_project_yml(tmp_path, """\
            advisors:
              enabled: [included]
        """)

        agents, groups = load_all(agents_dir, yml)
        # Both loaded into dict (for panel member resolution)
        assert "included" in agents
        assert "excluded" in agents
        # But only enabled shows in groups
        group_names = [a.name for g in groups for a in g.agents]
        assert "included" in group_names
        assert "excluded" not in group_names

    def test_no_project_yml(self, tmp_path):
        agents_dir = tmp_path / "agents"
        agents_dir.mkdir()
        _write(agents_dir, "solo", """\
            ---
            name: solo
            description: Alone.
            ---
            Prompt.
        """)
        agents, groups = load_all(agents_dir, None)
        assert "solo" in agents
        assert len(groups) == 1  # ungrouped

    def test_skips_underscore_files(self, tmp_path):
        agents_dir = tmp_path / "agents"
        agents_dir.mkdir()
        _write(agents_dir, "_system", """\
            ---
            name: _system
            description: System file.
            ---
            Prompt.
        """)
        agents, groups = load_all(agents_dir)
        assert "_system" not in agents


# ---------------------------------------------------------------------------
# resolve_effective_sources
# ---------------------------------------------------------------------------

class TestResolveEffectiveSources:
    def test_returns_context_and_sources(self):
        agent = DomainAgent(
            name="test",
            title="Test",
            description="",
            kind="solo",
            model=None,
            context=["ctx/**/*.md"],
            sources=["src/**/*.md"],
            system_prompt="",
        )
        ctx, src = resolve_effective_sources(agent)
        assert ctx == ["ctx/**/*.md"]
        assert src == ["src/**/*.md"]
