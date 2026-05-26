"""Unit tests for scripts/render-grounding.py — the grounding block renderer."""

import sys
import textwrap
from pathlib import Path

import pytest

# Make the skill's lib importable.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Import the renderer's internals (it's a script, so we need to import from path).
import importlib.util
_script = Path(__file__).resolve().parent.parent / "scripts" / "render-grounding.py"
spec = importlib.util.spec_from_file_location("render_grounding", _script)
render_grounding = importlib.util.module_from_spec(spec)
spec.loader.exec_module(render_grounding)

_render_block = render_grounding._render_block
_render_canonical_role_block = render_grounding._render_canonical_role_block
_replace_block = render_grounding._replace_block
_is_grounding_agent = render_grounding._is_grounding_agent
BEGIN_MARKER = render_grounding.BEGIN_MARKER
END_MARKER = render_grounding.END_MARKER

from lib.loader import DomainAgent


def _agent(**kwargs) -> DomainAgent:
    defaults = dict(
        name="test",
        title="Test",
        description="",
        kind="solo",
        model=None,
        context=[],
        sources=[],
        system_prompt="",
    )
    defaults.update(kwargs)
    return DomainAgent(**defaults)


def _canonical_agent(**kwargs) -> DomainAgent:
    """Convenience: canonical-role-mode agent with a sensible default block."""
    cr = kwargs.pop("canonical_roles", None) or {
        "tier_1": [
            {"role": "regulatory_strategy"},
            {"role": "architecture_strategy"},
            {"role": "system_architecture", "dhfs": {"role": "system"}},
        ],
        "tier_2": [
            {"role": "predicate_analysis"},
            {"role": "submission_package", "submissions": "all"},
            {"role": "kol_feedback"},
        ],
        "tier_3": {"researcher": "advisor-researcher"},
    }
    kwargs.setdefault("canonical_roles", cr)
    kwargs.setdefault("researcher", "advisor-researcher")
    return _agent(**kwargs)


class TestRenderBlock:
    def test_context_and_sources_sections(self):
        agent = _agent(
            context=["docs/arch/**/*.md"],
            sources=["docs/fda/**/*.md", "docs/standards/**/*.md"],
        )
        block = _render_block(agent)
        assert "### Context (always read)" in block
        assert "`docs/arch/**/*.md`" in block
        assert "### Sources (triage per question)" in block
        assert "`docs/fda/**/*.md`" in block

    def test_no_sources_message(self):
        agent = _agent()
        block = _render_block(agent)
        assert "no grounding sources configured" in block

    def test_context_only(self):
        agent = _agent(context=["docs/arch/**/*.md"])
        block = _render_block(agent)
        assert "### Context (always read)" in block
        assert "### Sources (triage per question)" not in block

    def test_sources_only(self):
        agent = _agent(sources=["docs/fda/**/*.md"])
        block = _render_block(agent)
        assert "### Context (always read)" not in block
        assert "### Sources (triage per question)" in block

    def test_excludes_rendered(self):
        agent = _agent(
            sources=["docs/**/*.md"],
            excludes=["**/README.md"],
        )
        block = _render_block(agent)
        assert "Exclude paths matching" in block
        assert "`**/README.md`" in block

    def test_markers_present(self):
        agent = _agent(sources=["docs/**/*.md"])
        block = _render_block(agent)
        assert block.startswith(BEGIN_MARKER)
        assert block.rstrip().endswith(END_MARKER)

    def test_workflow_steps(self):
        agent = _agent(context=["c/**"], sources=["s/**"])
        block = _render_block(agent)
        assert "Context pass" in block
        assert "Triage the Sources" in block
        assert "External lookup pass" in block
        assert "Counterpoint pass" in block
        assert "Hard rules" in block
        assert "rubber-stamp" in block


class TestReplaceBlock:
    def test_fresh_insert(self):
        body = "Some persona prose.\n\nMore text."
        block = f"{BEGIN_MARKER}\nNew grounding.\n{END_MARKER}"
        result, changed = _replace_block(body, block)
        assert changed
        assert BEGIN_MARKER in result
        assert "Some persona prose." in result
        assert result.endswith(f"{END_MARKER}\n")

    def test_replace_existing(self):
        body = f"Prose.\n\n{BEGIN_MARKER}\nOld grounding.\n{END_MARKER}\n\nAfter."
        block = f"{BEGIN_MARKER}\nNew grounding.\n{END_MARKER}"
        result, changed = _replace_block(body, block)
        assert changed
        assert "Old grounding" not in result
        assert "New grounding" in result
        assert "After." in result

    def test_idempotent(self):
        block = f"{BEGIN_MARKER}\nSame grounding.\n{END_MARKER}"
        body = f"Prose.\n\n{block}\n"
        result, changed = _replace_block(body, block)
        assert not changed

    def test_mismatched_markers_raises(self):
        body = f"Prose.\n\n{BEGIN_MARKER}\nBroken — no end marker."
        block = f"{BEGIN_MARKER}\nNew.\n{END_MARKER}"
        with pytest.raises(ValueError, match="no matching"):
            _replace_block(body, block)


class TestCanonicalRoleMode:
    """Tests for canonical-role-mode rendering (the post-pilot opt-in path)."""

    def test_dispatch_on_canonical_roles(self):
        """An agent with canonical_roles populated routes to the 3-tier renderer."""
        agent = _canonical_agent()
        assert agent.is_canonical_role_mode
        block = _render_block(agent)
        # 3-tier markers
        assert "### Tier 1 — Required grounding" in block
        assert "### Tier 2 — Index-driven discovery" in block
        assert "### Tier 3 — Independent search" in block
        # Should NOT fall through to legacy mode
        assert "### Context (always read)" not in block
        assert "### Sources (triage per question)" not in block

    def test_legacy_path_preserved_for_non_canonical_agents(self):
        """An agent with literal globs (no canonical_roles) renders legacy mode."""
        agent = _agent(
            context=["docs/arch/**/*.md"],
            sources=["docs/fda/**/*.md"],
        )
        assert not agent.is_canonical_role_mode
        block = _render_block(agent)
        assert "### Context (always read)" in block
        assert "### Sources (triage per question)" in block
        assert "### Tier 1 — Required grounding" not in block

    def test_role_descriptions_come_from_registry(self):
        """Tier 1 role lines include the description text from canonical-roles.yaml."""
        agent = _canonical_agent()
        block = _render_canonical_role_block(agent)
        # These strings live in the dhf-manifest registry, not in the agent file.
        assert "Regulatory pathway, predicate posture" in block
        assert "System-level architectural strategy" in block

    def test_selectors_render_inline(self):
        """yaml-native selectors (dhfs: {role: system}, submissions: all) format readably."""
        agent = _canonical_agent()
        block = _render_canonical_role_block(agent)
        assert "dhfs where role='system'" in block
        assert "all submissions" in block

    def test_researcher_name_threaded_through(self):
        """The researcher name from frontmatter appears in Tier 3 narrative + invocation."""
        agent = _canonical_agent(
            canonical_roles={
                "tier_1": [{"role": "regulatory_strategy"}],
                "tier_2": [{"role": "fda_guidance"}],
                "tier_3": {"researcher": "custom-researcher"},
            },
            researcher="custom-researcher",
        )
        block = _render_canonical_role_block(agent)
        assert "custom-researcher" in block
        # Used in narrative AND in the Agent(subagent_type:...) example
        assert block.count("custom-researcher") >= 2

    def test_no_tier_3_when_researcher_absent(self):
        """If frontmatter doesn't declare a researcher, Tier 3 invocation block is omitted."""
        agent = _canonical_agent(
            canonical_roles={
                "tier_1": [{"role": "regulatory_strategy"}],
                "tier_2": [{"role": "fda_guidance"}],
                # tier_3 omitted
            },
            researcher=None,
        )
        block = _render_canonical_role_block(agent)
        # Tier 3 narrative paragraph + invocation should be absent
        assert "### Tier 3 — Independent search via researcher subagent" not in block

    def test_multi_file_handling_documented(self):
        """The Tier 2 narrative mentions folder-pointer handling for multi-file roles."""
        agent = _canonical_agent()
        block = _render_canonical_role_block(agent)
        assert "folder-pointer" in block.lower() or "folder pointer" in block.lower()
        assert "file_count" in block

    def test_tool_constraint_accommodation_preserved(self):
        """Tier 1 hardening — 25K Read-cap rule with slicing must remain in output."""
        agent = _canonical_agent()
        block = _render_canonical_role_block(agent)
        assert "25 K tokens" in block or "~25 K" in block
        assert "non-overlapping line ranges" in block

    def test_idempotent_when_already_rendered(self):
        """Replacing an already-rendered canonical-role block produces no change."""
        agent = _canonical_agent()
        block = _render_block(agent)
        body = f"Persona prose.\n\n{block}\n"
        new_body, changed = _replace_block(body, block)
        assert not changed
        assert new_body == body


class TestIsGroundingAgent:
    """Renderer must skip agents with no context/sources/canonical_roles."""

    def test_skip_helper_agent_no_console_block(self):
        """Helper subagents (e.g., advisor-researcher) have no grounding declaration."""
        agent = _agent()  # empty context, sources, canonical_roles
        assert not _is_grounding_agent(agent)

    def test_legacy_advisor_recognized(self):
        agent = _agent(context=["docs/**"], sources=["docs/fda/**"])
        assert _is_grounding_agent(agent)

    def test_canonical_role_advisor_recognized(self):
        agent = _canonical_agent()
        assert _is_grounding_agent(agent)

    def test_sources_only_recognized(self):
        agent = _agent(sources=["docs/**"])
        assert _is_grounding_agent(agent)
