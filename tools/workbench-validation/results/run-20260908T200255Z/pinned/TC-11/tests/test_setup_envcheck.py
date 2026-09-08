"""Unit tests for the Environment section's setup.sh bridge (envcheck.py).

`parse_check_output` is pure — pins ANSI stripping, `── Step ──` grouping,
`[LEVEL]` classification, counts, and noise tolerance. `load_environment`
is exercised against a temp project (no setup.sh → unavailable; with
setup.sh + cache + stamp → full state incl. staleness). `run_check` is
exercised with a tiny fake setup.sh so no real environment probing happens.

Run from project root:
    python3 .claude/skills/project-console/tests/test_setup_envcheck.py
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

from console.setup import envcheck  # noqa: E402

SAMPLE = (
    "\x1b[1mRunning in check-only mode — no changes will be made.\x1b[0m\n"
    "\n"
    "\x1b[0;32m[OK]\x1b[0m Detected OS: mac\n"
    "\n"
    "\x1b[1m── Homebrew ──\x1b[0m\n"
    "\x1b[0;32m[OK]\x1b[0m Homebrew installed: Homebrew 4.2.0\n"
    "\n"
    "\x1b[1m── Brew Packages (Node.js, Git, GitHub CLI, jq) ──\x1b[0m\n"
    "\x1b[0;32m[OK]\x1b[0m node installed\n"
    "\x1b[1;33m[WARN]\x1b[0m jq: not found (required by hooks)\n"
    "some third-party noise line\n"
    "\x1b[0;31m[ERROR]\x1b[0m LibreOffice headless mode BROKEN\n"
    "\x1b[0;34m[INFO]\x1b[0m Run without --check to install missing tools.\n"
    "\n"
    "\x1b[1m── Summary ──\x1b[0m\n"
    "\x1b[0;32m[OK]\x1b[0m   Homebrew: Homebrew 4.2.0\n"
    "\x1b[0;32m[OK]\x1b[0m   Node.js:  v22.1.0\n"
    "\x1b[1;33m[WARN]\x1b[0m   jq: not found (required by hooks)\n"
    "\n"
    "\x1b[1m── Team Roster Access Audit ──\x1b[0m\n"
    "\x1b[0;32m[OK]\x1b[0m roster matches collaborators\n"
)


class ParseCheckOutputTest(unittest.TestCase):
    def test_groups_levels_counts_and_strips_ansi(self):
        report = envcheck.parse_check_output(SAMPLE)
        # counts exclude the Summary recap (its OK/WARN lines are duplicates)
        self.assertEqual(report["counts"],
                         {"ok": 4, "warn": 1, "error": 1, "info": 1})
        titles = [s["title"] for s in report["sections"]]
        self.assertEqual(titles, ["General", "Homebrew",
                                  "Brew Packages (Node.js, Git, GitHub CLI, jq)",
                                  "Team Roster Access Audit"])
        # pre-step line lands in General; ANSI stripped everywhere
        self.assertEqual(report["sections"][0]["lines"],
                         [{"level": "ok", "text": "Detected OS: mac"}])
        brew_pkgs = report["sections"][2]["lines"]
        self.assertEqual([l["level"] for l in brew_pkgs],
                         ["ok", "warn", "error", "info"])
        for sec in report["sections"]:
            for l in sec["lines"]:
                self.assertNotIn("\x1b", l["text"])

    def test_empty_and_noise_only_output(self):
        self.assertEqual(envcheck.parse_check_output(""),
                         {"sections": [], "counts": {"ok": 0, "warn": 0,
                                                     "error": 0, "info": 0}})
        noise = envcheck.parse_check_output("random\nlines\nwithout markers\n")
        self.assertEqual(noise["sections"], [])


class LoadEnvironmentTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_unavailable_without_setup_sh(self):
        self.assertEqual(envcheck.load_environment(self.root),
                         {"available": False})

    def test_full_state_with_cache_stamp_and_staleness(self):
        script = self.root / "setup.sh"
        script.write_text("#!/bin/bash\n", encoding="utf-8")
        (self.root / "setup.md").write_text("# guide\n", encoding="utf-8")
        state = self.root / ".state"
        state.mkdir()
        (state / "setup-last-run.txt").write_text("2026-07-01T10:00:00Z\n",
                                                  encoding="utf-8")
        # cache recorded BEFORE the script's current mtime → stale
        (state / "setup-check.json").write_text(json.dumps({
            "ran_at": "2026-07-01T10:05:00Z", "exit_code": 0, "duration_s": 3.2,
            "setup_sh_mtime": script.stat().st_mtime - 100,
            "sections": [], "counts": {"ok": 1, "warn": 0, "error": 0, "info": 0},
        }), encoding="utf-8")
        env = envcheck.load_environment(self.root)
        self.assertTrue(env["available"])
        self.assertEqual(env["guide"], "setup.md")
        self.assertEqual(env["last_full_run"], "2026-07-01T10:00:00Z")
        self.assertTrue(env["stale"])
        self.assertEqual(env["last_check"]["counts"]["ok"], 1)

    def test_fresh_check_is_not_stale_and_corrupt_cache_degrades(self):
        script = self.root / "setup.sh"
        script.write_text("#!/bin/bash\n", encoding="utf-8")
        state = self.root / ".state"
        state.mkdir()
        (state / "setup-check.json").write_text(json.dumps({
            "ran_at": "2026-07-15T10:00:00Z", "setup_sh_mtime": time.time() + 100,
            "sections": [], "counts": {"ok": 0, "warn": 0, "error": 0, "info": 0},
        }), encoding="utf-8")
        self.assertFalse(envcheck.load_environment(self.root)["stale"])
        (state / "setup-check.json").write_text("{not json", encoding="utf-8")
        env = envcheck.load_environment(self.root)
        self.assertTrue(env["available"])
        self.assertIsNone(env["last_check"])


class RunCheckTest(unittest.TestCase):
    def test_runs_script_parses_and_caches(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "setup.sh").write_text(
                "#!/bin/bash\n"
                "echo '── Fake Step ──'\n"
                "echo '[OK] all good'\n"
                "echo '[WARN] one thing missing'\n",
                encoding="utf-8",
            )
            report = envcheck.run_check(root)
            self.assertEqual(report["exit_code"], 0)
            self.assertEqual(report["counts"]["ok"], 1)
            self.assertEqual(report["counts"]["warn"], 1)
            self.assertEqual(report["sections"][0]["title"], "Fake Step")
            cached = json.loads(
                (root / ".state" / "setup-check.json").read_text(encoding="utf-8")
            )
            self.assertEqual(cached["counts"], report["counts"])
            # and load_environment picks the cache up, not stale
            env = envcheck.load_environment(root)
            self.assertFalse(env["stale"])
            self.assertEqual(env["last_check"]["counts"]["warn"], 1)

    def test_missing_script_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(RuntimeError):
                envcheck.run_check(Path(tmp))


if __name__ == "__main__":
    unittest.main(verbosity=2)
