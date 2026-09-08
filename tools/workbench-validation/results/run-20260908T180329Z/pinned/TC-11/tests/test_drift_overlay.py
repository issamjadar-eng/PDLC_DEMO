"""Unit tests for the trace-matrix drift overlay loader.

Verifies that `load_drift_overlay()` correctly:
- discovers `drift.json` files colocated with sidecar layer source files,
- merges summaries across multiple drift sources,
- groups violations by item_id,
- computes worst severity per item.

Project-agnostic — uses placeholder paths and DEMO/DI/PHA fixtures.

Run from project root:
    python3 .claude/skills/project-console/tests/test_drift_overlay.py
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

# Add console package root to path. The package is at
# .claude/skills/project-console/console/, the repo root is two parents up
# from the test file's grandparent.
_TEST_DIR = Path(__file__).resolve().parent
_CONSOLE_PKG_ROOT = _TEST_DIR.parent  # .claude/skills/project-console/
sys.path.insert(0, str(_CONSOLE_PKG_ROOT))

from console.trace_matrix.loader import _worst_severity, load_drift_overlay  # noqa: E402


def _drift_doc(violations: list[dict], cat_c: int = 0) -> dict:
    by_sev = {"error": 0, "warning": 0, "info": 0}
    for v in violations:
        by_sev[v["severity"]] = by_sev.get(v["severity"], 0) + 1
    return {
        "summary": {
            "violations_total": len(violations),
            "by_severity": by_sev,
            "by_category": {"A": 0, "B": 0, "C": cat_c},
            "by_rule": {},
        },
        "violations": violations,
    }


class DriftOverlayTest(unittest.TestCase):
    def test_worst_severity_ranks_error_above_warning_above_info(self):
        self.assertEqual(_worst_severity([]), None)
        self.assertEqual(
            _worst_severity([{"severity": "info"}, {"severity": "warning"}]),
            "warning",
        )
        self.assertEqual(
            _worst_severity(
                [{"severity": "info"}, {"severity": "error"}, {"severity": "warning"}]
            ),
            "error",
        )

    def test_no_drift_files_returns_none(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            # Sidecar references a layer source that has no drift sibling.
            (repo / "src").mkdir()
            (repo / "src" / "layer.md").write_text("# layer\n")
            sidecar = {
                "layers": [{"key": "design_inputs", "source_files": ["src/layer.md"]}]
            }
            self.assertIsNone(load_drift_overlay(repo, sidecar))

    def test_single_drift_loads_and_groups_by_item_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            d = repo / "_jira" / "demo" / "v1.0.0"
            d.mkdir(parents=True)
            (d / "epics.md").write_text("# epics\n")
            (d / "drift.json").write_text(
                json.dumps(
                    _drift_doc(
                        [
                            {
                                "rule": "C2",
                                "severity": "info",
                                "item_id": "DEMO-5",
                                "item_kind": "epic",
                                "message": "summary drift",
                                "resolution_hint": "align text",
                                "references": {"sim": "0.20"},
                            },
                            {
                                "rule": "C5",
                                "severity": "warning",
                                "item_id": "DEMO-5",
                                "item_kind": "epic",
                                "message": "stale xlsx",
                                "resolution_hint": "refresh DTM",
                                "references": {},
                            },
                            {
                                "rule": "A1",
                                "severity": "error",
                                "item_id": "DEMO-99",
                                "item_kind": "epic",
                                "message": "missing in DTM",
                                "resolution_hint": "",
                                "references": {},
                            },
                        ],
                        cat_c=2,
                    )
                )
            )

            sidecar = {
                "layers": [
                    {
                        "key": "design_inputs",
                        "source_files": ["_jira/demo/v1.0.0/epics.md"],
                    }
                ]
            }
            overlay = load_drift_overlay(repo, sidecar)
            self.assertIsNotNone(overlay)
            self.assertEqual(overlay["summary"]["violations_total"], 3)
            # Worst severity per item.
            self.assertEqual(overlay["worst_by_item"]["DEMO-5"], "warning")
            self.assertEqual(overlay["worst_by_item"]["DEMO-99"], "error")
            # Grouping by item_id.
            self.assertEqual(len(overlay["violations_by_item"]["DEMO-5"]), 2)
            self.assertEqual(len(overlay["violations_by_item"]["DEMO-99"]), 1)
            # Source list is repo-relative.
            self.assertIn("_jira/demo/v1.0.0/drift.json", overlay["sources"])

    def test_multiple_drift_files_dedupe_and_merge_summaries(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            for arch in ("alpha", "beta"):
                d = repo / "_jira" / arch / "v1.0.0"
                d.mkdir(parents=True)
                (d / "epics.md").write_text("# x\n")
                (d / "stories.md").write_text("# x\n")
                (d / "drift.json").write_text(
                    json.dumps(
                        _drift_doc(
                            [
                                {
                                    "rule": "C2",
                                    "severity": "info",
                                    "item_id": f"{arch.upper()}-1",
                                    "item_kind": "epic",
                                    "message": "x",
                                    "resolution_hint": "",
                                    "references": {},
                                }
                            ],
                            cat_c=1,
                        )
                    )
                )

            sidecar = {
                "layers": [
                    {
                        "key": "design_inputs",
                        "source_files": ["_jira/alpha/v1.0.0/epics.md"],
                    },
                    {
                        "key": "software",
                        "source_files": ["_jira/alpha/v1.0.0/stories.md"],
                    },
                    {
                        "key": "vnv",
                        "source_files": ["_jira/beta/v1.0.0/epics.md"],
                    },
                ]
            }
            overlay = load_drift_overlay(repo, sidecar)
            self.assertIsNotNone(overlay)
            # Two unique drift.json files (alpha, beta) — alpha referenced by
            # both design_inputs+software but should only load once.
            self.assertEqual(len(overlay["sources"]), 2)
            self.assertEqual(overlay["summary"]["violations_total"], 2)
            self.assertEqual(overlay["summary"]["by_severity"]["info"], 2)
            self.assertEqual(overlay["summary"]["by_category"]["C"], 2)


if __name__ == "__main__":
    unittest.main()
