"""Unit tests for the Team & Security repo-access audit (team_access.py).

`classify` is pure — pins the permission-aware teaching-project semantics
(rostered ok / unrostered-read observer / unrostered-write warning /
inactive-with-access error / active-without-access warning) and the
worst-first ordering. Cache round-trip + roster-staleness exercised on a
temp tree; the gh call itself is a thin wrapper left to live use.

Run from project root:
    python3 .claude/skills/project-console/tests/test_setup_team_access.py
"""
from __future__ import annotations

import json
import sys
import tempfile
import time
import unittest
from pathlib import Path

_TEST_DIR = Path(__file__).resolve().parent
_CONSOLE_PKG_ROOT = _TEST_DIR.parent  # .claude/skills/project-console/
sys.path.insert(0, str(_CONSOLE_PKG_ROOT))

from console.setup.team_access import classify, load_audit  # noqa: E402


class ClassifyTest(unittest.TestCase):
    def test_full_matrix_and_ordering(self):
        collaborators = [
            {"login": "alice", "role": "admin"},      # rostered active → ok
            {"login": "viewer", "role": "read"},      # unrostered read → observer
            {"login": "triager", "role": "triage"},   # unrostered triage → observer
            {"login": "rogue", "role": "write"},      # unrostered write → warning
            {"login": "boss", "role": "admin"},       # unrostered admin → warning
            {"login": "ghost", "role": "read"},       # inactive w/ access → error
        ]
        out = classify(collaborators, active=["alice", "unplugged"],
                       inactive=["ghost"])
        by = {r["login"]: r for r in out["rows"]}
        self.assertEqual(by["alice"]["status"], "ok")
        self.assertEqual(by["viewer"]["status"], "info")
        self.assertEqual(by["triager"]["status"], "info")
        self.assertEqual(by["rogue"]["status"], "warning")
        self.assertEqual(by["boss"]["status"], "warning")
        self.assertEqual(by["ghost"]["status"], "error")
        # active member with no repo access → warning row with role 'none'
        self.assertEqual(by["unplugged"]["status"], "warning")
        self.assertEqual(by["unplugged"]["role"], "none")
        self.assertEqual(out["counts"],
                         {"ok": 1, "info": 2, "warning": 3, "error": 1})
        # worst-first: error, then warnings, then observers, members last
        statuses = [r["status"] for r in out["rows"]]
        self.assertEqual(statuses,
                         ["error", "warning", "warning", "warning",
                          "info", "info", "ok"])

    def test_all_healthy(self):
        out = classify([{"login": "alice", "role": "write"},
                        {"login": "obs", "role": "read"}],
                       active=["alice"], inactive=[])
        self.assertEqual(out["counts"],
                         {"ok": 1, "info": 1, "warning": 0, "error": 0})


class CacheTest(unittest.TestCase):
    def test_load_audit_roundtrip_and_staleness(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertIsNone(load_audit(root))
            state = root / ".state"
            state.mkdir()
            (state / "team-access-audit.json").write_text(json.dumps({
                "repo": "org/repo", "checked_at": "2026-07-15T10:00:00Z",
                "rows": [], "counts": {"ok": 0, "info": 0, "warning": 0, "error": 0},
            }), encoding="utf-8")
            # project.yml written AFTER checked_at → stale
            (root / "project.yml").write_text("team:\n  active: []\n", encoding="utf-8")
            data = load_audit(root)
            self.assertTrue(data["stale"])
            # corrupt cache degrades to None
            (state / "team-access-audit.json").write_text("{oops", encoding="utf-8")
            self.assertIsNone(load_audit(root))


if __name__ == "__main__":
    unittest.main(verbosity=2)
