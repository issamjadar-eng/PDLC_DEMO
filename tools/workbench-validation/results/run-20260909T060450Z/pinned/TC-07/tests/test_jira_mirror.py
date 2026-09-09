"""Unit tests for the `jira-mirror` adapter.

Generic fixtures only — no project-specific names. Uses placeholder Jira
project key `DEMO`, DI prefix `DI`, and PHA prefix `PHA`. Mirrors the
fixture convention enforced by the sibling `jira-pull` skill's
`tests/test_drift_rules.py`.

Run from the project root:
    python3 -m unittest .claude/skills/trace-matrix/tests/test_jira_mirror.py
or:
    python3 .claude/skills/trace-matrix/tests/test_jira_mirror.py
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
SCRIPT_DIR = SKILL_DIR / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from parsers.jira_mirror import parse  # noqa: E402


def _write(tmpdir: str, name: str, body: str) -> Path:
    p = Path(tmpdir) / name
    p.write_text(body, encoding="utf-8")
    return p


EPICS_FIXTURE = """# Epics — DEMO v1.0.0

| DI Prefix | Jira Key | Summary | Status | Story Count | Labels |
|---|---|---|---|---|---|
| — | [DEMO-3](https://example.atlassian.net/browse/DEMO-3) | Foundational technical infrastructure | Working | 0 |  |
| DI-0001 | [DEMO-5](https://example.atlassian.net/browse/DEMO-5) | DI-0001 first design input | Working | 6 | approved |
| DI-0002 | [DEMO-12](https://example.atlassian.net/browse/DEMO-12) | DI-0002 second design input | Working | 9 | approved |
"""

STORIES_FIXTURE = """# Stories — DEMO v1.0.0

| Jira Key | Summary | Parent (DI) | Status | Labels |
|---|---|---|---|---|
| [DEMO-6](https://example.atlassian.net/browse/DEMO-6) | First story under DI-0001 | DI-0001 | Closed | approved |
| [DEMO-7](https://example.atlassian.net/browse/DEMO-7) | Second story under DI-0001 | DI-0001 | Closed | approved |
| [DEMO-13](https://example.atlassian.net/browse/DEMO-13) | First story under DI-0002 | DI-0002 | Working | approved |
"""

HAZARDS_FIXTURE = """# Hazards — DEMO v1.0.0

| PHA Prefix | Jira Key | Summary | Status | Issuelink Count |
|---|---|---|---|---|
| PHA 12 | [DEMO-200](https://example.atlassian.net/browse/DEMO-200) | PHA 12: Image is pre-processed incorrectly | OPEN | 0 |
| PHA 26 | [DEMO-201](https://example.atlassian.net/browse/DEMO-201) | PHA 26: Image is not available | OPEN | 0 |
"""

TESTS_FIXTURE = """# Tests — DEMO v1.0.0

| Jira Key | Summary | Status | Verifies (Story) | Defect Links |
|---|---|---|---|---|
| [DEMO-300](https://example.atlassian.net/browse/DEMO-300) | Test execution for DEMO-6 | Closed | [DEMO-6](https://example.atlassian.net/browse/DEMO-6) | 0 |
| [DEMO-301](https://example.atlassian.net/browse/DEMO-301) | Test execution for DEMO-6 + DEMO-13 | Closed | [DEMO-6](https://example.atlassian.net/browse/DEMO-6), [DEMO-13](https://example.atlassian.net/browse/DEMO-13) | 0 |
"""


class JiraMirrorAdapterTest(unittest.TestCase):
    def test_epics_parses_di_prefixed_rows_skips_unprefixed(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = _write(tmp, "epics.md", EPICS_FIXTURE)
            r = parse(p, {"id_prefix": "DI"})
            ids = [n["id"] for n in r.nodes]
            self.assertEqual(ids, ["DI-0001", "DI-0002"])
            # source_ref carries the Jira browse URL so the console can
            # build a back-link.
            self.assertTrue(
                all(n["source_ref"].startswith("https://example") for n in r.nodes)
            )
            self.assertEqual(r.extras.get("jira_mirror_kind"), "epics")

    def test_stories_extract_parent_di_into_traces_forward_ids(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = _write(tmp, "stories.md", STORIES_FIXTURE)
            r = parse(p, {"id_prefix": "DEMO"})
            keys = [n["id"] for n in r.nodes]
            self.assertEqual(keys, ["DEMO-6", "DEMO-7", "DEMO-13"])
            # Every story should point at the parent DI prefix.
            self.assertEqual(r.nodes[0]["traces_forward_ids"], ["DI-0001"])
            self.assertEqual(r.nodes[2]["traces_forward_ids"], ["DI-0002"])
            self.assertEqual(r.extras.get("jira_mirror_kind"), "stories")

    def test_hazards_normalise_pha_space_into_pha_hyphen(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = _write(tmp, "hazards.md", HAZARDS_FIXTURE)
            r = parse(p, {"id_prefix": "PHA"})
            ids = [n["id"] for n in r.nodes]
            # `PHA 12` (whitespace) must be normalised to `PHA-12`.
            self.assertEqual(ids, ["PHA-12", "PHA-26"])
            self.assertEqual(r.extras.get("jira_mirror_kind"), "hazards")

    def test_tests_collect_multiple_verifies_keys_into_traces_forward(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = _write(tmp, "tests.md", TESTS_FIXTURE)
            r = parse(p, {"id_prefix": "DEMO"})
            ids = [n["id"] for n in r.nodes]
            self.assertEqual(ids, ["DEMO-300", "DEMO-301"])
            self.assertEqual(r.nodes[0]["traces_forward_ids"], ["DEMO-6"])
            self.assertEqual(r.nodes[1]["traces_forward_ids"], ["DEMO-6", "DEMO-13"])
            self.assertEqual(r.extras.get("jira_mirror_kind"), "tests")

    def test_missing_source_returns_warning_no_crash(self):
        r = parse(Path("/nonexistent/file.md"), {"id_prefix": "DI"})
        self.assertEqual(r.nodes, [])
        self.assertTrue(any("source missing" in w for w in r.warnings))

    def test_unknown_shape_records_warning(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = _write(
                tmp,
                "weird.md",
                "# Weird\n\n| Foo | Bar |\n|---|---|\n| 1 | 2 |\n",
            )
            r = parse(p, {"id_prefix": "DI"})
            self.assertEqual(r.nodes, [])
            self.assertTrue(any("could not detect kind" in w for w in r.warnings))


if __name__ == "__main__":
    unittest.main()
