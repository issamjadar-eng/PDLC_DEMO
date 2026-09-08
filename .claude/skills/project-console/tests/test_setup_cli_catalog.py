"""Unit tests for the Setup connector catalog shape and the CLI-tooling probe.

Catalog: every entry must carry the keys the template + write path consume,
and a `spec` must be either stdio-shaped (command) or remote-shaped (url) —
the card form branches on exactly that. Pins the Atlassian entry to the
OAuth endpoint (the /v1/sse endpoint is deprecated and must not come back).

CLI tooling: `parse_gh_auth` is pure and covers gh output variants;
`load_cli_tooling` assertions are machine-independent (shape, not state).

Run from project root:
    python3 .claude/skills/project-console/tests/test_setup_cli_catalog.py
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

_TEST_DIR = Path(__file__).resolve().parent
_CONSOLE_PKG_ROOT = _TEST_DIR.parent  # .claude/skills/project-console/
sys.path.insert(0, str(_CONSOLE_PKG_ROOT))

from console.setup.catalog import CATALOG, get  # noqa: E402
from console.setup.loader import load_cli_tooling, parse_gh_auth  # noqa: E402
from console.setup.writer import validate_spec  # noqa: E402


class CatalogShapeTest(unittest.TestCase):
    REQUIRED_KEYS = {"key", "title", "description", "docs", "spec",
                     "env_required", "editable"}

    def test_every_entry_carries_the_template_contract(self):
        for entry in CATALOG:
            self.assertTrue(self.REQUIRED_KEYS.issubset(entry),
                            f"{entry.get('key')}: missing {self.REQUIRED_KEYS - set(entry)}")

    def test_specs_are_stdio_or_remote_shaped_and_writable(self):
        for entry in CATALOG:
            spec = entry["spec"]
            if spec is None:  # the custom free-form cards
                continue
            if entry.get("url_placeholder") and not spec.get("url"):
                # Catalog rule: never invent an endpoint. A customer-gated
                # server ships with a blank, editable url + placeholder + note;
                # the writer validates it once the user fills the url in.
                self.assertIn("url", entry.get("editable", []),
                              f"{entry['key']}: blank url must be editable")
                self.assertTrue(entry.get("note"),
                                f"{entry['key']}: blank url needs a note saying why")
                continue
            self.assertTrue(
                spec.get("command") or spec.get("url"),
                f"{entry['key']}: spec is neither stdio (command) nor remote (url)",
            )
            # every prefilled spec must pass the writer's validation as-is
            validate_spec(dict(spec))

    def test_atlassian_uses_the_oauth_endpoint(self):
        entry = get("atlassian")
        self.assertIsNotNone(entry)
        self.assertEqual(entry["spec"]["type"], "http")
        self.assertEqual(entry["spec"]["url"], "https://mcp.atlassian.com/v1/mcp/authv2")
        self.assertNotIn("sse", entry["spec"]["url"])  # deprecated 2026-06-30
        self.assertEqual(entry["env_required"], [])  # OAuth in the client, no tokens


class GhAuthParseTest(unittest.TestCase):
    def test_modern_keyring_format(self):
        out = (
            "github.com\n"
            "  ✓ Logged in to github.com account demo-user (keyring)\n"
            "  - Active account: true\n"
        )
        self.assertEqual(parse_gh_auth(out),
                         {"logged_in": True, "host": "github.com", "account": "demo-user"})

    def test_legacy_as_format(self):
        out = "✓ Logged in to github.example.com as demo-user (oauth_token)"
        self.assertEqual(parse_gh_auth(out)["account"], "demo-user")
        self.assertEqual(parse_gh_auth(out)["host"], "github.example.com")

    def test_not_logged_in(self):
        out = "You are not logged into any GitHub hosts. To log in, run: gh auth login"
        self.assertEqual(parse_gh_auth(out)["logged_in"], False)
        self.assertEqual(parse_gh_auth(""), {"logged_in": False, "host": "", "account": ""})


class CliToolingShapeTest(unittest.TestCase):
    """Machine-independent: asserts the row contract, not this host's state."""

    def test_reports_git_and_gh_rows_with_the_row_contract(self):
        data = load_cli_tooling(Path.cwd())
        names = [t["name"] for t in data["tools"]]
        self.assertEqual(names, ["git", "gh"])
        for t in data["tools"]:
            self.assertIn(t["status"], ("ok", "warning"))
            for key in ("title", "installed", "version", "detail", "fix"):
                self.assertIn(key, t)
            if not t["installed"] or t["status"] == "warning":
                self.assertTrue(t["fix"], f"{t['name']}: warning row must carry a fix command")
            if t["status"] == "ok":
                self.assertEqual(t["fix"], "")
        self.assertEqual(data["counts"]["total"], 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
