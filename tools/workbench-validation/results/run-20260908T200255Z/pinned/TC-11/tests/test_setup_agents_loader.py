"""Unit tests for the Setup agents loader (loader.load_agents).

Encodes the regression that motivated them: the description fallback chain
(frontmatter description → first body paragraph) must hold on BOTH install
surfaces — top-level `.claude/agents/*.md` AND skill-bundled
`.claude/skills/*/agents/*.md` — because the two are read by separate loops.
Also pins `_body_summary()` joining a hard-wrapped first paragraph instead of
cutting it mid-sentence at the first line break.

Project-agnostic — synthetic .claude tree in a temp dir.

Run from project root:
    python3 .claude/skills/project-console/tests/test_setup_agents_loader.py
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

_TEST_DIR = Path(__file__).resolve().parent
_CONSOLE_PKG_ROOT = _TEST_DIR.parent  # .claude/skills/project-console/
sys.path.insert(0, str(_CONSOLE_PKG_ROOT))

from console.setup.loader import _body_summary, load_agents  # noqa: E402

FRONTMATTER_AGENT = """\
---
name: registered-agent
description: Frontmatter description wins over the body.
tools: [Read, Grep]
---

# Registered Agent

Body paragraph that must NOT be used when frontmatter has a description.
"""

BARE_TOP_AGENT = """\
# Bare Top-Level Agent

You are the top-level agent whose first prose paragraph is the summary of
record because the file ships no YAML frontmatter.
"""

BARE_BUNDLED_AGENT = """\
# Bundled Worker Agent

You receive one work item from the orchestrating skill and produce its
fragment; this paragraph is hard-wrapped and must surface joined, not cut
at the first line break.

## Parameters
"""

PROJECT = {
    "security": {
        "approved_skills": ["demo-skill"],
        "approved_agents": ["registered-agent", "bare-top"],
    }
}


class AgentsLoaderTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        agents = self.root / ".claude" / "agents"
        agents.mkdir(parents=True)
        (agents / "registered-agent.md").write_text(FRONTMATTER_AGENT, encoding="utf-8")
        (agents / "bare-top.md").write_text(BARE_TOP_AGENT, encoding="utf-8")
        bundled = self.root / ".claude" / "skills" / "demo-skill" / "agents"
        bundled.mkdir(parents=True)
        (bundled / "bundled-worker.md").write_text(BARE_BUNDLED_AGENT, encoding="utf-8")

    def tearDown(self):
        self._tmp.cleanup()

    def _rows(self) -> dict:
        data = load_agents(self.root, PROJECT)
        return {r["name"]: r for r in data["rows"]}

    def test_every_surface_yields_a_description(self):
        missing = [n for n, r in self._rows().items() if not r["description"]]
        self.assertEqual(missing, [])

    def test_frontmatter_description_wins_over_body(self):
        row = self._rows()["registered-agent"]
        self.assertIn("Frontmatter description wins", row["description"])
        self.assertNotIn("Body paragraph", row["full_description"])

    def test_top_level_body_fallback(self):
        row = self._rows()["bare-top"]
        self.assertTrue(row["description"].startswith("You are the top-level agent"))

    def test_bundled_body_fallback_joins_wrapped_paragraph(self):
        row = self._rows()["bundled-worker"]
        self.assertEqual(row["source"], "bundled")
        # the full paragraph, joined across hard-wrapped lines
        self.assertIn("produce its fragment", row["full_description"])
        self.assertNotIn("\n", row["full_description"])
        # bundled worker inherits approval from its approved owning skill
        self.assertEqual(row["status"], "ok")

    def test_body_summary_stops_at_paragraph_boundary(self):
        p = self.root / "para.md"
        p.write_text(
            "# Title\n\nFirst line of para\ncontinues here.\n\nSecond paragraph.\n",
            encoding="utf-8",
        )
        self.assertEqual(_body_summary(p), "First line of para continues here.")


if __name__ == "__main__":
    unittest.main(verbosity=2)
