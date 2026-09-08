"""Per-agent tests for the file-locator (`mcp__file-locator__locate`) wiring.

Two layers, both project-agnostic:

1. Renderer-level — `_render_canonical_role_block` emits a self-gated
   "Semantic file locator" section whenever the agent declares a Tier-3
   researcher. Uses synthetic agents; touches no real project content.
2. Per-agent structural — iterates the bundled (registry-agnostic) agent
   files under `agents/` and asserts each canonical-role advisor is wired
   for the locator: the MCP tool is granted (or the agent runs all-tools)
   and the rendered grounding block carries the locator section.

The bundled agent files are project-agnostic by hard rule (no device or
company names), so iterating them here introduces no project specifics.
"""

import importlib.util
import sys
from pathlib import Path

import pytest

_SKILL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_SKILL_ROOT))

from lib.loader import DomainAgent, load_agent_file  # noqa: E402

_script = _SKILL_ROOT / "scripts" / "render-grounding.py"
spec = importlib.util.spec_from_file_location("render_grounding", _script)
render_grounding = importlib.util.module_from_spec(spec)
spec.loader.exec_module(render_grounding)

_render_canonical_role_block = render_grounding._render_canonical_role_block

LOCATOR_TOOL = "mcp__file-locator__locate"
LOCATOR_HEADING = "### Semantic file locator"
# The self-gating sentence — proves the section is safe to ship to projects
# that have not installed the locator.
SELF_GATE = f"If `{LOCATOR_TOOL}` is not in your tool set, skip this"

_AGENTS_DIR = _SKILL_ROOT / "agents"


def _canonical_agent(researcher: str | None = "advisor-researcher") -> DomainAgent:
    """A minimal canonical-role-mode agent for renderer tests."""
    tier_3 = {"researcher": researcher} if researcher else {}
    return DomainAgent(
        name="test-advisor",
        title="Test Advisor",
        description="",
        kind="solo",
        model=None,
        context=[],
        sources=[],
        system_prompt="",
        canonical_roles={
            "tier_1": [{"role": "regulatory_strategy"}],
            "tier_2": [{"role": "predicate_analysis"}],
            "tier_3": tier_3,
        },
        researcher=researcher,
    )


# ---------------------------------------------------------------------------
# Layer 1 — renderer-level
# ---------------------------------------------------------------------------

class TestRendererEmitsLocatorSection:
    def test_section_present_when_researcher_declared(self):
        block = _render_canonical_role_block(_canonical_agent())
        assert LOCATOR_HEADING in block
        assert LOCATOR_TOOL in block

    def test_section_is_self_gated(self):
        """The section must tell the agent to skip it when the tool is absent —
        otherwise it is unsafe to propagate to locator-less projects."""
        block = _render_canonical_role_block(_canonical_agent())
        assert SELF_GATE in block

    def test_section_references_the_declared_researcher(self):
        block = _render_canonical_role_block(_canonical_agent(researcher="custom-researcher"))
        # The locator section names the researcher as the heavier fallback.
        head, _, _ = block.partition("### Tier 3 — Independent search")
        assert "custom-researcher" in head

    def test_section_absent_without_researcher(self):
        """No Tier-3 researcher → no Tier-3 section at all, locator included."""
        block = _render_canonical_role_block(_canonical_agent(researcher=None))
        assert LOCATOR_HEADING not in block

    def test_section_precedes_tier_3_researcher_section(self):
        block = _render_canonical_role_block(_canonical_agent())
        assert block.index(LOCATOR_HEADING) < block.index(
            "### Tier 3 — Independent search"
        )


# ---------------------------------------------------------------------------
# Layer 2 — per-agent structural (over the real bundled agent files)
# ---------------------------------------------------------------------------

def _bundled_canonical_agents() -> list[tuple[str, DomainAgent]]:
    out = []
    for path in sorted(_AGENTS_DIR.glob("*.md")):
        agent = load_agent_file(path)
        if agent.is_canonical_role_mode and agent.researcher:
            out.append((agent.name, agent))
    return out


_CANONICAL_AGENTS = _bundled_canonical_agents()


def test_there_are_canonical_agents_to_check():
    """Guard: the glob actually found agents — a silent empty set would make
    every parametrized test below vacuously pass."""
    assert _CANONICAL_AGENTS, f"no canonical-role agents found under {_AGENTS_DIR}"


@pytest.mark.parametrize(
    "name,agent", _CANONICAL_AGENTS, ids=[n for n, _ in _CANONICAL_AGENTS]
)
class TestBundledAgentLocatorWiring:
    def test_locator_tool_granted(self, name, agent):
        """Solo advisors have a restricted tool set — the MCP tool must be
        explicitly granted. Panels declare no `tools:` (all-tools), so an
        empty list is also acceptable."""
        if agent.tools:
            assert LOCATOR_TOOL in agent.tools, (
                f"{name}: restricted tool set without {LOCATOR_TOOL}"
            )

    def test_grounding_block_has_locator_section(self, name, agent):
        block = _render_canonical_role_block(agent)
        assert LOCATOR_HEADING in block, f"{name}: grounding block missing locator section"
        assert SELF_GATE in block, f"{name}: locator section is not self-gated"

    def test_rendered_block_matches_file(self, name, agent):
        """The grounding block on disk is in sync with the renderer — i.e.
        `render-grounding.py --all` has been run since the last template edit."""
        raw = (_AGENTS_DIR / f"{name}.md").read_text(encoding="utf-8")
        assert LOCATOR_HEADING in raw, (
            f"{name}: file out of sync — run render-grounding.py --all"
        )
