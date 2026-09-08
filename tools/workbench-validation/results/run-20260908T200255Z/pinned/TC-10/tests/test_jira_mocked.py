"""Jira-list renderer — `mocked` tier (fake transport, canned payloads) plus
one opt-in `live` smoke test.

Tier contract lives in tests/conftest.py. Everything here is hermetic: the
cookie bridge and `urlopen` are replaced via tests/fakes.py, and the
autouse socket guard would fail the test if a real connection were tried.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

SKILL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib.normalizer import NormalizationReport  # noqa: E402
from fakes import (  # noqa: E402
    FakeResponse,
    http_error,
    install_fake_cookie_bridge,
    install_fake_urlopen,
    load_fixture,
)

BASE_URL = "https://example.atlassian.net"


def _md_with_macro(position: int = 0) -> str:
    return (
        "Before\n\n"
        f"<!-- AUTO:JIRA-LIST source=jira jql=project%3DPROJ position={position} -->\n"
        f"<!-- /AUTO:JIRA-LIST position={position} -->\n\n"
        "After\n"
    )


def _report(jql: str = "project=PROJ", position: int = 0) -> NormalizationReport:
    report = NormalizationReport()
    report.jira_macros.append({
        "position": position, "jql": jql,
        "columns": None, "count": None, "server_id": None,
        "max_issues": None, "raw_params": {},
    })
    return report


@pytest.mark.mocked
def test_renders_table_from_canned_two_issue_payload(monkeypatch) -> None:
    from actions.adopt_helper import _expand_jira_macros

    install_fake_cookie_bridge(monkeypatch, cookie="fake=cookie")
    seen = install_fake_urlopen(
        monkeypatch, [FakeResponse.from_fixture("jira_search_two_issues.json")]
    )

    new_md, warnings = _expand_jira_macros(_md_with_macro(), BASE_URL, _report())

    assert warnings == [], warnings
    assert "| Key | Summary | Status | Updated |" in new_md
    assert f"[PROJ-1]({BASE_URL}/browse/PROJ-1)" in new_md
    assert "Define user need for alarm escalation" in new_md
    assert "In Progress" in new_md
    # Pipe inside a summary is escaped so the table stays well-formed.
    assert "Verify infusion rate \\| boundary values" in new_md
    # Sentinels survive (round-trip preserved).
    assert "AUTO:JIRA-LIST" in new_md and "/AUTO:JIRA-LIST" in new_md
    # The request carried the cookie header and hit the search endpoint.
    assert len(seen) == 1
    req = seen[0]
    assert req.full_url.startswith(f"{BASE_URL}/wiki/rest/api/3/search?jql=project%3DPROJ")
    assert req.get_header("Cookie") == "fake=cookie"


@pytest.mark.mocked
def test_empty_result_renders_no_match_placeholder(monkeypatch) -> None:
    from actions.adopt_helper import _expand_jira_macros

    install_fake_cookie_bridge(monkeypatch, cookie="fake=cookie")
    install_fake_urlopen(monkeypatch, [FakeResponse.from_fixture("jira_search_empty.json")])

    new_md, warnings = _expand_jira_macros(_md_with_macro(), BASE_URL, _report())

    assert warnings == [], warnings
    assert "_(no Jira issues match this query)_" in new_md


@pytest.mark.mocked
def test_http_401_degrades_to_deferred_render_comment(monkeypatch) -> None:
    from actions.adopt_helper import _expand_jira_macros

    install_fake_cookie_bridge(monkeypatch, cookie="stale=cookie")
    body = load_fixture("jira_search_401.json")
    assert body["errorMessages"]  # fixture documents what the server says
    install_fake_urlopen(monkeypatch, [http_error(401, "Unauthorized")])

    new_md, warnings = _expand_jira_macros(_md_with_macro(), BASE_URL, _report())

    assert "<!-- jira-list render deferred: HTTPError -->" in new_md, new_md
    assert any("jira position=0" in w and "401" in w for w in warnings), warnings
    # Adopt never fails on a renderer problem: surrounding content intact.
    assert new_md.startswith("Before") and new_md.rstrip().endswith("After")


@pytest.mark.mocked
def test_cookie_bridge_failure_degrades_without_any_request(monkeypatch) -> None:
    from actions.adopt_helper import _expand_jira_macros

    install_fake_cookie_bridge(monkeypatch, cookie=RuntimeError("no cookies"))
    seen = install_fake_urlopen(monkeypatch, [])  # any request would assert

    new_md, warnings = _expand_jira_macros(_md_with_macro(), BASE_URL, _report())

    assert "<!-- jira-list render deferred: no auth cookies -->" in new_md, new_md
    assert any("cookie bridge failed" in w for w in warnings), warnings
    assert seen == []


@pytest.mark.live
def test_live_jira_search_smoke() -> None:
    """Opt-in (`--live`). Proves the REST search path against the project's
    configured Jira. Skips — never fails — when no connection is configured,
    so a deployment without Jira reports the case as not applicable."""
    import yaml

    project_root = SKILL_ROOT.parent.parent.parent
    project_yml = project_root / "project.yml"
    base_url = None
    if project_yml.is_file():
        cfg = yaml.safe_load(project_yml.read_text(encoding="utf-8")) or {}
        base_url = ((cfg.get("change_control") or {}).get("jira") or {}).get("base_url")
    if not base_url:
        pytest.skip("no live connection configured (project.yml change_control.jira.base_url)")

    from actions.adopt_helper import _expand_jira_macros

    new_md, warnings = _expand_jira_macros(
        _md_with_macro(), base_url, _report(jql="order by created DESC")
    )
    assert "AUTO:JIRA-LIST" in new_md
    assert not any("cookie bridge failed" in w for w in warnings), warnings
