"""Unit tests for the Setup team-roster write path (writer.py).

Verifies that `add_team_member()` / `deactivate_team_member()`:
- append/move multi-line member blocks with surgical, comment-preserving edits,
- expand inline-empty `active: []` / `inactive: []` forms and write
  `active: []` back when the roster empties,
- enforce the guards: approved email domains, github/task_folder uniqueness,
  inactive re-add rejection, YAML-hostile scalar rejection,
- keep project.yml parseable (restore-on-failure discipline) and leave a
  backup + audit trail under the tool's .data/ directory.

Project-agnostic — placeholder people and example.com domains.

Run from project root:
    python3 .claude/skills/project-console/tests/test_setup_team_writer.py
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

BASE_YML = """\
project:
  name: MedTech Project
# roster comment that must survive edits
team:
  active:
  - name: Alice Smith
    github: alice-gh
    task_folder: alice
    role: Demo Owner
    email: alice.smith@example.com
    added: 2026-01-01
  - name: Bob Jones
    github: bob-gh
    task_folder: bob
    role: QA Lead
    email: bob.jones@example.com
    added: 2026-02-01
  inactive: []
security:
  approved_email_domains:
  - example.com
  approved_mcps: []
"""

NEW_MEMBER = {
    "name": "Carol White",
    "github": "carol-gh",
    "task_folder": "carol",
    "role": "Systems Engineer",
    "email": "Carol.White@Example.com",
}


class TeamWriterTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.tool = self.root / "tool"
        self.tool.mkdir()
        self.yml = self.root / "project.yml"
        self.yml.write_text(BASE_YML, encoding="utf-8")

    def tearDown(self):
        self._tmp.cleanup()

    def _team(self) -> dict:
        return (yaml.safe_load(self.yml.read_text(encoding="utf-8")) or {})["team"]

    # ── add ──────────────────────────────────────────────────────────────

    def test_add_appends_normalized_block_and_preserves_comments(self):
        writer.add_team_member(self.root, self.tool, dict(NEW_MEMBER))
        team = self._team()
        self.assertEqual([m["github"] for m in team["active"]],
                         ["alice-gh", "bob-gh", "carol-gh"])
        carol = team["active"][-1]
        self.assertEqual(carol["email"], "carol.white@example.com")  # lowercased
        self.assertEqual(carol["task_folder"], "carol")
        self.assertTrue(carol["added"])  # stamped with today's date
        self.assertIn("# roster comment that must survive edits",
                      self.yml.read_text(encoding="utf-8"))

    def test_add_rejects_unapproved_email_domain(self):
        bad = dict(NEW_MEMBER, email="carol@elsewhere.org")
        with self.assertRaisesRegex(writer.SetupWriteError, "elsewhere.org"):
            writer.add_team_member(self.root, self.tool, bad)

    def test_add_accepts_any_domain_when_none_declared(self):
        self.yml.write_text(
            BASE_YML.replace("  approved_email_domains:\n  - example.com\n", ""),
            encoding="utf-8",
        )
        writer.add_team_member(
            self.root, self.tool, dict(NEW_MEMBER, email="carol@elsewhere.org")
        )
        self.assertEqual(self._team()["active"][-1]["email"], "carol@elsewhere.org")

    def test_add_rejects_duplicate_github_and_task_folder(self):
        with self.assertRaisesRegex(writer.SetupWriteError, "already on the active roster"):
            writer.add_team_member(
                self.root, self.tool,
                dict(NEW_MEMBER, github="bob-gh", task_folder="carol2"),
            )
        with self.assertRaisesRegex(writer.SetupWriteError, "already used"):
            writer.add_team_member(
                self.root, self.tool, dict(NEW_MEMBER, task_folder="bob"),
            )

    def test_add_rejects_former_member_pointing_to_manual_reactivation(self):
        writer.deactivate_team_member(self.root, self.tool, "bob-gh", "left the program")
        with self.assertRaisesRegex(writer.SetupWriteError, "team.inactive"):
            writer.add_team_member(
                self.root, self.tool,
                dict(NEW_MEMBER, github="bob-gh", task_folder="bob2",
                     email="bob.jones@example.com"),
            )

    def test_add_rejects_yaml_hostile_scalars_and_bad_slugs(self):
        with self.assertRaises(writer.SetupWriteError):
            writer.add_team_member(
                self.root, self.tool, dict(NEW_MEMBER, role="Lead: Engineering"),
            )
        with self.assertRaises(writer.SetupWriteError):
            writer.add_team_member(
                self.root, self.tool, dict(NEW_MEMBER, github="not a user!"),
            )
        with self.assertRaises(writer.SetupWriteError):
            writer.add_team_member(
                self.root, self.tool, dict(NEW_MEMBER, task_folder="Carol Dir"),
            )
        # nothing above may have dirtied the file
        self.assertEqual(len(self._team()["active"]), 2)

    def test_add_expands_inline_empty_active(self):
        self.yml.write_text(
            "team:\n  active: []\n  inactive: []\nsecurity:\n"
            "  approved_email_domains:\n  - example.com\n",
            encoding="utf-8",
        )
        writer.add_team_member(self.root, self.tool, dict(NEW_MEMBER))
        self.assertEqual([m["github"] for m in self._team()["active"]], ["carol-gh"])

    def test_add_without_team_block_is_a_clear_error(self):
        self.yml.write_text("project:\n  name: MedTech Project\n", encoding="utf-8")
        with self.assertRaisesRegex(writer.SetupWriteError, "team:"):
            writer.add_team_member(self.root, self.tool, dict(NEW_MEMBER))

    # ── deactivate ───────────────────────────────────────────────────────

    def test_deactivate_moves_block_with_removed_and_reason(self):
        writer.deactivate_team_member(self.root, self.tool, "bob-gh", "left the program")
        team = self._team()
        self.assertEqual([m["github"] for m in team["active"]], ["alice-gh"])
        bob = team["inactive"][0]
        self.assertEqual(bob["name"], "Bob Jones")
        self.assertEqual(bob["reason"], "left the program")
        self.assertEqual(str(bob["added"]), "2026-02-01")  # history carried over
        self.assertTrue(bob["removed"])

    def test_deactivate_requires_known_member_and_reason(self):
        with self.assertRaisesRegex(writer.SetupWriteError, "not on the active roster"):
            writer.deactivate_team_member(self.root, self.tool, "nobody-gh", "x")
        with self.assertRaisesRegex(writer.SetupWriteError, "Reason"):
            writer.deactivate_team_member(self.root, self.tool, "bob-gh", "  ")

    def test_deactivating_last_member_leaves_parseable_empty_roster(self):
        writer.deactivate_team_member(self.root, self.tool, "bob-gh", "left")
        writer.deactivate_team_member(self.root, self.tool, "alice-gh", "role change")
        team = self._team()
        self.assertEqual(team["active"], [])
        self.assertEqual(len(team["inactive"]), 2)
        # and the roster is usable again afterwards
        writer.add_team_member(self.root, self.tool, dict(NEW_MEMBER))
        self.assertEqual([m["github"] for m in self._team()["active"]], ["carol-gh"])

    # ── write discipline ─────────────────────────────────────────────────

    def test_writes_leave_backup_and_audit_trail(self):
        writer.add_team_member(self.root, self.tool, dict(NEW_MEMBER))
        writer.deactivate_team_member(self.root, self.tool, "carol-gh", "test cycle")
        backups = list((self.tool / ".data" / "setup-backups").glob("project.yml.*.bak"))
        self.assertGreaterEqual(len(backups), 2)
        audit = (self.tool / ".data" / "setup-audit.log").read_text(encoding="utf-8")
        self.assertIn("team-add | carol-gh", audit)
        self.assertIn("team-deactivate | carol-gh", audit)


class UpsertPreservationTest(unittest.TestCase):
    """Connector updates must never drop env/headers — the browser never
    sends them, so an edit that omits them is not a request to delete them.
    Pins the fix for URL specs, which carry no env key at all (the old
    `"env" in spec` guard silently lost a remote server's env/headers)."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.tool = self.root / "tool"
        self.tool.mkdir()
        (self.root / "project.yml").write_text(
            "security:\n  approved_mcps: []\n", encoding="utf-8"
        )
        import json
        (self.root / ".mcp.json").write_text(json.dumps({
            "mcpServers": {
                "local-server": {"type": "stdio", "command": "run.sh", "args": [],
                                 "env": {"API_KEY": "secret"}},
                "remote-server": {"type": "http", "url": "https://old.example.com/mcp",
                                  "env": {"TOKEN": "secret"},
                                  "headers": {"X-Org": "demo"}},
            }
        }), encoding="utf-8")

    def tearDown(self):
        self._tmp.cleanup()

    def _servers(self) -> dict:
        import json
        return json.loads(
            (self.root / ".mcp.json").read_text(encoding="utf-8")
        )["mcpServers"]

    def test_stdio_update_preserves_env(self):
        writer.upsert_server(self.root, self.tool, "local-server",
                             {"type": "stdio", "command": "run2.sh", "args": ["-v"]})
        s = self._servers()["local-server"]
        self.assertEqual(s["command"], "run2.sh")
        self.assertEqual(s["env"], {"API_KEY": "secret"})

    def test_url_update_preserves_env_and_headers(self):
        writer.upsert_server(self.root, self.tool, "remote-server",
                             {"type": "http", "url": "https://new.example.com/mcp"})
        s = self._servers()["remote-server"]
        self.assertEqual(s["url"], "https://new.example.com/mcp")
        self.assertEqual(s["env"], {"TOKEN": "secret"})
        self.assertEqual(s["headers"], {"X-Org": "demo"})


if __name__ == "__main__":
    unittest.main(verbosity=2)
