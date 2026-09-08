"""Unit tests for the GitHub-direct registry catalog (registry_remote.py)
and the loader's catalog-source ordering.

Everything network-shaped is factored pure and tested without gh:
blob-SHA computation (pinned against git's own hash), tree parsing,
frontmatter-from-text, tarball extraction (incl. traversal rejection via
the tarfile data filter), cache round-trip, and load_registries preferring
the cached GitHub catalog over the clone with statuses recomputed against
the live local install.

Run from project root:
    python3 .claude/skills/project-console/tests/test_setup_registry_remote.py
"""
from __future__ import annotations

import io
import json
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path

_TEST_DIR = Path(__file__).resolve().parent
_CONSOLE_PKG_ROOT = _TEST_DIR.parent  # .claude/skills/project-console/
sys.path.insert(0, str(_CONSOLE_PKG_ROOT))

from console.setup import registry_remote as rr  # noqa: E402
from console.setup.loader import _registry_status, load_registries  # noqa: E402


class PureHelpersTest(unittest.TestCase):
    def test_blob_sha_matches_git(self):
        # git hash-object of "hello\n" — the canonical test vector
        self.assertEqual(rr.blob_sha(b"hello\n"),
                         "ce013625030ba8dba906f756967f9e9ca394464a")

    def test_parse_skill_entries(self):
        tree = [
            {"path": "skills/alpha/SKILL.md", "type": "blob", "sha": "a1"},
            {"path": "skills/alpha/VERSION", "type": "blob", "sha": "a2"},
            {"path": "skills/beta/SKILL.md", "type": "blob", "sha": "b1"},
            {"path": "skills/orphan/VERSION", "type": "blob", "sha": "o1"},  # no SKILL.md
            {"path": "skills/alpha", "type": "tree", "sha": "t1"},
            {"path": "agents/x.md", "type": "blob", "sha": "x1"},
            {"path": "skills/alpha/scripts/run.py", "type": "blob", "sha": "s1"},
        ]
        out = rr.parse_skill_entries(tree)
        self.assertEqual(sorted(out), ["alpha", "beta"])
        self.assertEqual(out["alpha"], {"skillmd_sha": "a1", "version_sha": "a2"})
        self.assertEqual(out["beta"], {"skillmd_sha": "b1"})

    def test_frontmatter_text_strict_and_fallback(self):
        strict = "---\nname: demo\nversion: 1.2.0\ndescription: Clean text.\n---\n# T\n"
        self.assertEqual(rr.frontmatter_text(strict).get("version"), "1.2.0")
        hostile = ("---\nname: demo\nversion: 2.0.0\n"
                   "description: prose with a colon: which breaks yaml\n---\nbody\n")
        fm = rr.frontmatter_text(hostile)
        self.assertEqual(fm.get("version"), "2.0.0")
        self.assertIn("breaks yaml", fm.get("description", ""))
        self.assertEqual(rr.frontmatter_text("no frontmatter here"), {})

    def test_registry_status_matrix(self):
        self.assertEqual(_registry_status("1.2.0", None), "not-installed")
        self.assertEqual(_registry_status("1.3.0", "1.2.0"), "update")
        self.assertEqual(_registry_status("1.2.0", "1.3.0"), "local-ahead")
        self.assertEqual(_registry_status("1.2.0", "1.2.0"), "current")


def _make_tarball(path: Path, members: dict[str, bytes]) -> None:
    with tarfile.open(path, "w:gz") as tf:
        for name, content in members.items():
            info = tarfile.TarInfo(name)
            info.size = len(content)
            tf.addfile(info, io.BytesIO(content))


class TarballExtractTest(unittest.TestCase):
    def test_extracts_one_skill_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            tb = root / "reg.tar.gz"
            _make_tarball(tb, {
                "org-repo-abc123/skills/demo/SKILL.md": b"---\nname: demo\n---\n",
                "org-repo-abc123/skills/demo/VERSION": b"1.0.0\n",
                "org-repo-abc123/skills/other/SKILL.md": b"---\nname: other\n---\n",
                "org-repo-abc123/README.md": b"# registry\n",
            })
            src = rr.extract_skill_from_tarball(tb, "demo", root / "x")
            self.assertTrue((src / "SKILL.md").is_file())
            self.assertEqual((src / "VERSION").read_text().strip(), "1.0.0")
            self.assertFalse((root / "x" / "org-repo-abc123" / "skills" / "other").exists())
            self.assertFalse((root / "x" / "org-repo-abc123" / "README.md").exists())

    def test_missing_skill_and_missing_skillmd_raise(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            tb = root / "reg.tar.gz"
            _make_tarball(tb, {"o/skills/demo/VERSION": b"1.0.0\n"})
            with self.assertRaises(rr.RegistryRemoteError):
                rr.extract_skill_from_tarball(tb, "absent", root / "a")
            with self.assertRaises(rr.RegistryRemoteError):
                rr.extract_skill_from_tarball(tb, "demo", root / "b")  # no SKILL.md

    def test_path_traversal_member_is_rejected(self):
        # enough ".." to escape the extraction dir — the tarfile data
        # filter must refuse it (a shallower ".." that normalizes to a path
        # still INSIDE the dest is harmless and allowed)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            tb = root / "reg.tar.gz"
            _make_tarball(tb, {
                "o/skills/demo/SKILL.md": b"---\nname: demo\n---\n",
                "o/skills/demo/../../../../../evil.txt": b"boom",
            })
            with self.assertRaises(rr.RegistryRemoteError):
                rr.extract_skill_from_tarball(tb, "demo", root / "x")
            self.assertFalse((root / "evil.txt").exists())
            self.assertFalse((root.parent / "evil.txt").exists())


class CatalogCacheAndLoaderTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        demo = self.root / ".claude" / "skills" / "demo"
        demo.mkdir(parents=True)
        (demo / "SKILL.md").write_text(
            "---\nname: demo\nversion: 1.2.0\ndescription: Local demo skill.\n---\n",
            encoding="utf-8",
        )
        (demo / "VERSION").write_text("1.2.0\n", encoding="utf-8")

    def tearDown(self):
        self._tmp.cleanup()

    def _write_cache(self, name: str, skills: dict) -> None:
        p = rr.catalog_cache_path(self.root, name)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps({
            "repo": "org/reg", "branch": "main",
            "fetched_at": "2026-07-15T12:00:00Z", "skills": skills,
        }), encoding="utf-8")

    def test_cached_github_catalog_preferred_and_statuses_live(self):
        self._write_cache("acme", {
            "demo": {"version": "1.3.0", "description": "", "full_description": ""},
            "newskill": {"version": "0.1.0", "description": "Fresh skill.",
                         "full_description": "Fresh skill."},
        })
        project = {"registries": [
            {"name": "acme", "type": "github", "repo": "org/reg",
             "local_path": "../nonexistent-clone"},
        ]}
        out = load_registries(self.root, project)
        reg = out["registries"][0]
        self.assertEqual(reg["source"], "github")
        self.assertEqual(reg["fetched_at"], "2026-07-15T12:00:00Z")
        rows = {r["name"]: r for r in reg["skills"]}
        self.assertEqual(rows["demo"]["status"], "update")  # 1.3.0 > local 1.2.0
        # cached desc empty for installed skill → filled from the local install
        self.assertIn("Local demo skill", rows["demo"]["description"])
        self.assertEqual(rows["newskill"]["status"], "not-installed")
        self.assertEqual(out["actionable"], 2)

    def test_no_cache_no_clone_degrades_with_hint(self):
        project = {"registries": [
            {"name": "acme", "type": "github", "repo": "org/reg"},
        ]}
        reg = load_registries(self.root, project)["registries"][0]
        self.assertFalse(reg["reachable"])
        self.assertEqual(reg["skills"], [])

    def test_corrupt_cache_ignored(self):
        p = rr.catalog_cache_path(self.root, "acme")
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("{not json", encoding="utf-8")
        self.assertIsNone(rr.load_cached_catalog(self.root, "acme"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
