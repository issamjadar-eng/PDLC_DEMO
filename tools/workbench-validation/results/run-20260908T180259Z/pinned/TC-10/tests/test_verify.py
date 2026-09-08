#!/usr/bin/env python3
"""Tests for actions/verify.py — config audit + report writing."""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_ROOT))

# Import via path because actions/ isn't a package on sys.path by default.
import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "verify_action",
    str(SKILL_ROOT / "actions" / "verify.py"),
)
verify_mod = importlib.util.module_from_spec(_spec)  # type: ignore
sys.modules["verify_action"] = verify_mod  # required before exec for dataclass
_spec.loader.exec_module(verify_mod)  # type: ignore

from lib.config import ChangeControlConfig, TestTarget  # noqa: E402


def test_validate_test_target_missing():
    cfg = ChangeControlConfig()
    ok, msg = verify_mod._validate_test_target(cfg)
    assert not ok
    assert "test_target" in msg
    print("PASS  test_validate_test_target_missing")


def test_validate_test_target_partial():
    cfg = ChangeControlConfig(
        test_target=TestTarget(space_key="X", parent_page_id="", parent_title=""),
    )
    ok, msg = verify_mod._validate_test_target(cfg)
    assert not ok
    assert "parent_page_id" in msg
    print("PASS  test_validate_test_target_partial")


def test_validate_test_target_complete():
    cfg = ChangeControlConfig(
        test_target=TestTarget(
            space_key="AFAI",
            parent_page_id="123",
            parent_title="X",
        ),
    )
    ok, msg = verify_mod._validate_test_target(cfg)
    assert ok
    assert msg == ""
    print("PASS  test_validate_test_target_complete")


def test_config_summary_redacts_safely():
    cfg = ChangeControlConfig(
        cloud_id="abc",
        base_url="https://x.atlassian.net",
        test_target=TestTarget(
            space_key="AFAI", parent_page_id="9", parent_title="T",
            title_prefix="P",
        ),
    )
    out = verify_mod._config_summary(cfg)
    assert out["cloud_id"] == "abc"
    assert out["base_url"].startswith("https://")
    assert out["test_target"]["parent_page_id"] == "9"
    print("PASS  test_config_summary_redacts_safely")


def test_report_to_json_round_trip():
    r = verify_mod.VerifyReport(
        kind="orphan-file",
        date="2026-05-01",
        config={"foo": "bar"},
    )
    r.steps.append(verify_mod.VerifyStep("step-a", True, "ok"))
    r.steps.append(verify_mod.VerifyStep("step-b", False, "fail"))
    j = r.to_json()
    assert j["kind"] == "orphan-file"
    assert j["ok"] is False  # one failed step
    assert len(j["steps"]) == 2
    assert j["steps"][0]["name"] == "step-a"
    assert j["steps"][0]["ok"] is True
    print("PASS  test_report_to_json_round_trip")


def test_report_ok_when_no_steps_is_false():
    r = verify_mod.VerifyReport(kind="x", date="2026-05-01", config={})
    assert r.ok is False  # no steps == not verified
    print("PASS  test_report_ok_when_no_steps_is_false")


def test_write_report_creates_scratch_path():
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        (root / "project.yml").write_text(
            "team:\n  active:\n    - {name: Test, task_folder: tester}\n",
            encoding="utf-8",
        )
        r = verify_mod.VerifyReport(
            kind="audit",
            date="2026-05-01",
            config={},
        )
        r.steps.append(verify_mod.VerifyStep("config-loaded", True))
        out = verify_mod.write_report(r, project_root=root, person="tester")
        assert out.is_file()
        assert out.parent.name == "_scratch"
        assert out.parent.parent.name == "tester"
        data = json.loads(out.read_text())
        assert data["kind"] == "audit"
        assert data["ok"] is True
    print("PASS  test_write_report_creates_scratch_path")


def test_audit_subaction_runs_against_live_repo_config():
    """End-to-end: invoke the cmd_audit handler against the actual project.yml
    in this repo. Should not raise; ok==True iff the block has been added.
    """
    import argparse
    args = argparse.Namespace(cmd="audit")
    rc = verify_mod.cmd_audit(args)
    # Either passes (config present) or returns 1 (config absent) — neither
    # is an exception.
    assert rc in (0, 1)
    print("PASS  test_audit_subaction_runs_against_live_repo_config")


def main() -> int:
    tests = [
        test_validate_test_target_missing,
        test_validate_test_target_partial,
        test_validate_test_target_complete,
        test_config_summary_redacts_safely,
        test_report_to_json_round_trip,
        test_report_ok_when_no_steps_is_false,
        test_write_report_creates_scratch_path,
        test_audit_subaction_runs_against_live_repo_config,
    ]
    failures = 0
    for t in tests:
        try:
            t()
        except AssertionError as e:
            failures += 1
            print(f"FAIL  {t.__name__}: {e}")
    print()
    print(f"{len(tests) - failures}/{len(tests)} passed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
