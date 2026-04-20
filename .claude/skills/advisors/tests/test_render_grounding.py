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
_replace_block = render_grounding._replace_block
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
