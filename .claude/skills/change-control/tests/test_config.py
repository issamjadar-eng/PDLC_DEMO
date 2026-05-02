#!/usr/bin/env python3
"""Tests for lib/config.py — the project.yml change_control loader."""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_ROOT))

from lib.config import (  # noqa: E402
    ChangeControlConfig,
    CrossPageSourceEntry,
    SpaceConfig,
    TestTarget,
    find_project_root,
    parse_change_control_config,
    read_change_control_config,
)


_FIXTURE = """
project:
  name: Test
change_control:
  cloud_id: 9829416d-7e21-4f52-9f71-c88d5b2c05ad
  base_url: https://example.atlassian.net
  spaces:
    - key: AFAI
      name: ADI FAI
      staging_target_root: docs/project/_confluence
      title_prefixes_to_strip:
        - "HipLink IntraOp - "
        - "HipLink Planning "
  test_target:
    space_key: AFAI
    parent_page_id: "6768394270"
    parent_title: AI_PDLC_INT_TEST
    title_prefix: "ROUNDTRIP TEST"
  cross_page_source_map:
    "5619318892":
      - filename: "FORM-000105316 - DTM.xlsx"
        source_page_title: "FORM-000105316 - DTM"
    "5622562963": []
"""


def test_parse_full_block():
    import yaml  # type: ignore
    raw = yaml.safe_load(_FIXTURE)
    cfg = parse_change_control_config(raw)
    assert isinstance(cfg, ChangeControlConfig)
    assert not cfg.is_empty
    assert cfg.cloud_id == "9829416d-7e21-4f52-9f71-c88d5b2c05ad"
    assert cfg.base_url == "https://example.atlassian.net"
    assert len(cfg.spaces) == 1
    s = cfg.spaces[0]
    assert isinstance(s, SpaceConfig)
    assert s.key == "AFAI"
    assert s.name == "ADI FAI"
    assert s.staging_target_root == "docs/project/_confluence"
    assert s.title_prefixes_to_strip == ["HipLink IntraOp - ", "HipLink Planning "]
    assert cfg.space_by_key("AFAI") is s
    assert cfg.space_by_key("MISSING") is None
    assert isinstance(cfg.test_target, TestTarget)
    assert cfg.test_target.parent_page_id == "6768394270"
    assert cfg.test_target.title_prefix == "ROUNDTRIP TEST"
    # Source map
    assert "5619318892" in cfg.cross_page_source_map
    entries = cfg.cross_page_source_map["5619318892"]
    assert len(entries) == 1
    assert isinstance(entries[0], CrossPageSourceEntry)
    assert entries[0].filename == "FORM-000105316 - DTM.xlsx"
    assert entries[0].source_page_title == "FORM-000105316 - DTM"
    assert cfg.cross_page_source_map["5622562963"] == []
    print("PASS  test_parse_full_block")


def test_parse_missing_block_is_empty():
    cfg = parse_change_control_config({"project": {"name": "X"}})
    assert isinstance(cfg, ChangeControlConfig)
    assert cfg.is_empty
    assert cfg.cloud_id == ""
    assert cfg.base_url == ""
    assert cfg.spaces == []
    assert cfg.test_target is None
    assert cfg.cross_page_source_map == {}
    print("PASS  test_parse_missing_block_is_empty")


def test_parse_none_input_is_empty():
    cfg = parse_change_control_config(None)
    assert cfg.is_empty
    print("PASS  test_parse_none_input_is_empty")


def test_parse_inner_block_directly():
    """Caller can pass the inner block too — handy for tests."""
    cfg = parse_change_control_config({
        "cloud_id": "abc",
        "base_url": "https://x.atlassian.net",
    })
    assert cfg.cloud_id == "abc"
    assert cfg.base_url == "https://x.atlassian.net"
    print("PASS  test_parse_inner_block_directly")


def test_source_map_attachments_nested_shape():
    """Accept the legacy nested {attachments: [...]} dict form."""
    cfg = parse_change_control_config({
        "change_control": {
            "cross_page_source_map": {
                "111": {
                    "attachments": [
                        {"filename": "a.docx", "source_page_title": "Page A"},
                    ],
                },
            },
        },
    })
    assert "111" in cfg.cross_page_source_map
    assert cfg.cross_page_source_map["111"][0].filename == "a.docx"
    print("PASS  test_source_map_attachments_nested_shape")


def test_read_from_disk_empty_when_no_yaml():
    with tempfile.TemporaryDirectory() as d:
        cfg = read_change_control_config(Path(d))
        assert cfg.is_empty
    print("PASS  test_read_from_disk_empty_when_no_yaml")


def test_read_from_disk_loads_real_yaml():
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        (root / "project.yml").write_text(_FIXTURE, encoding="utf-8")
        cfg = read_change_control_config(root)
        assert cfg.cloud_id == "9829416d-7e21-4f52-9f71-c88d5b2c05ad"
        assert cfg.test_target is not None
        assert cfg.test_target.space_key == "AFAI"
    print("PASS  test_read_from_disk_loads_real_yaml")


def test_read_handles_garbage_yaml():
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        (root / "project.yml").write_text("::: not valid : yaml :::", encoding="utf-8")
        cfg = read_change_control_config(root)
        assert cfg.is_empty  # graceful, never raises
    print("PASS  test_read_handles_garbage_yaml")


def test_find_project_root_walks_up():
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        (root / "project.yml").write_text("project: {}\n", encoding="utf-8")
        nested = root / "a" / "b" / "c"
        nested.mkdir(parents=True)
        found = find_project_root(nested)
        assert found == root.resolve()
    print("PASS  test_find_project_root_walks_up")


def test_repo_project_yml_loads():
    """Smoke test: the actual project.yml in this repo loads cleanly and
    has the expected v0.12.0 shape (cloud_id, AFAI space, test_target).
    """
    here = Path(__file__).resolve()
    # Walk up to find a project.yml — the repo root.
    found_root: Path | None = None
    for cand in here.parents:
        if (cand / "project.yml").is_file():
            found_root = cand
            break
    if found_root is None:
        print("SKIP  test_repo_project_yml_loads (no project.yml found)")
        return
    cfg = read_change_control_config(found_root)
    if cfg.is_empty:
        # Repo hasn't adopted the block yet; skip rather than fail.
        print("SKIP  test_repo_project_yml_loads (config block empty)")
        return
    assert cfg.cloud_id, "expected non-empty cloud_id"
    assert cfg.base_url.startswith("https://"), "expected base_url"
    assert cfg.test_target is not None
    print("PASS  test_repo_project_yml_loads")


def main() -> int:
    tests = [
        test_parse_full_block,
        test_parse_missing_block_is_empty,
        test_parse_none_input_is_empty,
        test_parse_inner_block_directly,
        test_source_map_attachments_nested_shape,
        test_read_from_disk_empty_when_no_yaml,
        test_read_from_disk_loads_real_yaml,
        test_read_handles_garbage_yaml,
        test_find_project_root_walks_up,
        test_repo_project_yml_loads,
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
