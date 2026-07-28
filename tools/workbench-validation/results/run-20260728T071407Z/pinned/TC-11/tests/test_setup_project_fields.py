"""Unit tests for the Setup → Project section: the loader's field/section
rows (with skill-shipped descriptions from project_meta.py) and the writer's
scalar-field editor (surgical, comment-preserving, restore-on-failure).

Run from project root:
    python3 .claude/skills/project-console/tests/test_setup_project_fields.py
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

import yaml

_TEST_DIR = Path(__file__).resolve().parent
_CONSOLE_PKG_ROOT = _TEST_DIR.parent  # .claude/skills/project-console/
sys.path.insert(0, str(_CONSOLE_PKG_ROOT))

from console.setup import writer  # noqa: E402
from console.setup.loader import load_project_settings  # noqa: E402
from console.setup.project_meta import PROJECT_FIELDS, SECTIONS  # noqa: E402

PROJECT = {
    "project": {
        "name": "MedTech Project",
        "repo": "org/medtech-project",
        "type": "medtech",
        "device_class": "II",
        "portfolio_context": ["A100", "B200"],
        "capabilities": {"ai_ml": True},
        "mystery_field": "no catalog entry",
    },
    "team": {"active": [], "inactive": []},
    "registries": [{"name": "r1"}],
    "custom_block": {"x": 1},
}

BASE_YML = """\
project:
  name: MedTech Project
  # identity comment that must survive edits
  repo: org/medtech-project
  type: medtech
  device_class: II
  portfolio_context:
  - A100
team:
  active: []
"""


class LoaderTest(unittest.TestCase):
    def test_fields_editability_descriptions_and_unknown_flag(self):
        out = load_project_settings(PROJECT)
        rows = {f["key"]: f for f in out["fields"]}
        self.assertTrue(rows["name"]["editable"])
        self.assertTrue(rows["name"]["known"])
        self.assertEqual(rows["name"]["description"], PROJECT_FIELDS["name"])
        self.assertFalse(rows["portfolio_context"]["editable"])  # list
        self.assertEqual(rows["portfolio_context"]["value"], "A100, B200")
        self.assertFalse(rows["capabilities"]["editable"])       # dict
        self.assertFalse(rows["mystery_field"]["known"])
        self.assertIn("add it to the project-console", rows["mystery_field"]["description"])

    def test_sections_inventory_with_managed_and_unknown(self):
        out = load_project_settings(PROJECT)
        secs = {s["key"]: s for s in out["sections"]}
        self.assertNotIn("project", secs)  # rendered as fields, not a section
        self.assertEqual(secs["team"]["description"], SECTIONS["team"]["description"])
        self.assertEqual(secs["registries"]["size"], "1 item")
        self.assertFalse(secs["custom_block"]["known"])
        # expansion preview: real YAML of the block, order preserved
        self.assertIn("active: []", secs["team"]["preview"])
        self.assertEqual(secs["team"]["preview_truncated"], 0)

    def test_section_preview_caps_long_blocks(self):
        big = {"project": {"name": "x"}, "bigblock": [f"item-{i}" for i in range(100)]}
        sec = load_project_settings(big)["sections"][0]
        self.assertEqual(len(sec["preview"].splitlines()), 40)
        self.assertEqual(sec["preview_truncated"], 60)


class WriterTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.tool = self.root / "tool"
        self.tool.mkdir()
        self.yml = self.root / "project.yml"
        self.yml.write_text(BASE_YML, encoding="utf-8")

    def tearDown(self):
        self._tmp.cleanup()

    def test_scalar_edit_preserves_comments_and_validates(self):
        writer.set_project_field(self.root, self.tool, "device_class", "III")
        text = self.yml.read_text(encoding="utf-8")
        self.assertIn("# identity comment that must survive edits", text)
        data = yaml.safe_load(text)
        self.assertEqual(data["project"]["device_class"], "III")
        # other fields untouched
        self.assertEqual(data["project"]["repo"], "org/medtech-project")

    def test_idempotent_same_value_is_a_noop(self):
        note = writer.set_project_field(self.root, self.tool, "type", "medtech")
        self.assertIn("nothing changed", note)

    def test_rejects_missing_nonscalar_and_hostile_values(self):
        with self.assertRaisesRegex(writer.SetupWriteError, "does not exist"):
            writer.set_project_field(self.root, self.tool, "absent_key", "x")
        with self.assertRaisesRegex(writer.SetupWriteError, "not a single-line scalar"):
            writer.set_project_field(self.root, self.tool, "portfolio_context", "x")
        with self.assertRaises(writer.SetupWriteError):
            writer.set_project_field(self.root, self.tool, "name", "a: b")  # yaml-hostile
        with self.assertRaises(writer.SetupWriteError):
            writer.set_project_field(self.root, self.tool, "name", "")
        # file unchanged after all rejections
        self.assertEqual(self.yml.read_text(encoding="utf-8"), BASE_YML)

    def test_audit_and_backup_written(self):
        writer.set_project_field(self.root, self.tool, "name", "Renamed Project")
        audit = (self.tool / ".data" / "setup-audit.log").read_text(encoding="utf-8")
        self.assertIn("project-field | name", audit)
        backups = list((self.tool / ".data" / "setup-backups").glob("project.yml.*.bak"))
        self.assertEqual(len(backups), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
