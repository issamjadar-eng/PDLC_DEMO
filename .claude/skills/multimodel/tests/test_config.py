"""Config loading from project.yml (multimodel: block) and from TOML."""

from __future__ import annotations

import pytest

from multimodel import ConfigError, external_send_allowed, load_config
from multimodel.config import find_project_file

YAML = """
project:
  name: MedTech Project
multimodel:
  policy:
    external_send: allowed
  providers:
    grok:
      enabled: true
      role: challenger
"""

TOML = """
[policy]
external_send = "forbidden"

[providers.codex]
enabled = true
role = "challenger"
"""


def test_loads_block_from_project_yml(tmp_path, monkeypatch):
    (tmp_path / "project.yml").write_text(YAML, encoding="utf-8")
    sub = tmp_path / "docs" / "deep"
    sub.mkdir(parents=True)
    monkeypatch.chdir(sub)
    cfg = load_config()
    assert cfg["providers"]["grok"]["role"] == "challenger"
    assert find_project_file().parent == tmp_path


def test_loads_whole_document_from_toml(tmp_path):
    path = tmp_path / "models.toml"
    path.write_text(TOML, encoding="utf-8")
    cfg = load_config(path)
    assert cfg["providers"]["codex"]["enabled"] is True
    assert external_send_allowed(cfg) == (False, "policy.external_send is 'forbidden' in the multimodel config")


def test_missing_block_names_the_fix(tmp_path):
    path = tmp_path / "project.yml"
    path.write_text("project:\n  name: x\n", encoding="utf-8")
    with pytest.raises(ConfigError, match="multimodel"):
        load_config(path)


def test_missing_file_and_bad_shape(tmp_path):
    with pytest.raises(ConfigError, match="not found"):
        load_config(tmp_path / "nope.toml")
    bad = tmp_path / "bad.toml"
    bad.write_text("providers = 3\n", encoding="utf-8")
    with pytest.raises(ConfigError, match="providers"):
        load_config(bad)


def test_no_project_yml_anywhere(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(ConfigError, match="project.yml"):
        load_config()


def test_policy_defaults_and_validation():
    assert external_send_allowed({})[0] is True
    assert external_send_allowed({"policy": {"external_send": "maybe"}})[0] is False
