"""Capability tests for the SessionStart security-posture hook
(`.claude/hooks/security-assert.sh`, owned by the secops skill).

The hook derives its project root from its own location, so each test
copies it into a temp project fixture (`<tmp>/.claude/hooks/`) together
with the shared roster resolver it calls, then runs it with a controlled
git identity and a PATH whose `gh` always fails — so the eight network
checks are recorded SKIP and the local checks are what is asserted.
Positive: a compliant fixture reports check 2 (email domain) and check 9
(skills allowlist) PASS with zero critical failures. Negative: an
unapproved skill directory → check 9 WARN naming it (severity Low); an off-domain email → check 2
FAIL (Critical).
"""
from __future__ import annotations

import json
import os
import shutil
import stat
import subprocess
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]                       # repo root: .claude/skills/secops/tests → root
HOOK = ROOT / ".claude" / "hooks" / "security-assert.sh"
RESOLVER = ROOT / ".claude" / "skills" / "shared" / "scripts" / "resolve_user.py"

PROJECT_YML = """\
project:
  name: Fixture Project
  repo: example-org/fixture
security:
  check_ttl_days: 7
  approved_email_domains:
    - example.com
  required_gitignore_patterns:
    - "credentials*"
  approved_skills:
    - alpha
  approved_plugins: []
  approved_mcps: []
team:
  active:
    - name: Test Person
      github: testperson
      task_folder: tp
      email: tp@example.com
      role: engineer
  inactive: []
"""


def _fixture(tmp_path: Path, email: str, skills=("alpha",)) -> Path:
    if not HOOK.is_file() or not RESOLVER.is_file():
        pytest.skip("security-assert.sh / resolve_user.py not present in this checkout")
    for tool in ("git", "jq", "python3"):
        if shutil.which(tool) is None:
            pytest.skip(f"{tool} not installed")
    proj = tmp_path / "proj"
    (proj / ".claude" / "hooks").mkdir(parents=True)
    (proj / ".claude" / "skills" / "shared" / "scripts").mkdir(parents=True)
    shutil.copy2(HOOK, proj / ".claude" / "hooks" / "security-assert.sh")
    shutil.copy2(RESOLVER, proj / ".claude" / "skills" / "shared" / "scripts" / "resolve_user.py")
    for s in skills:
        (proj / ".claude" / "skills" / s).mkdir(parents=True)
        (proj / ".claude" / "skills" / s / "SKILL.md").write_text(f"---\nname: {s}\nversion: 1\n---\n")
    (proj / "project.yml").write_text(PROJECT_YML)
    (proj / ".gitignore").write_text("credentials*\n.env\n")
    (proj / "tasks" / "tp").mkdir(parents=True)
    subprocess.run(["git", "init", "-q"], cwd=proj, check=True)
    subprocess.run(["git", "config", "user.email", email], cwd=proj, check=True)
    subprocess.run(["git", "config", "user.name", "Test Person"], cwd=proj, check=True)
    # A `gh` that always fails → GH_AVAILABLE=false → network checks SKIP.
    fakebin = tmp_path / "bin"; fakebin.mkdir()
    gh = fakebin / "gh"; gh.write_text("#!/bin/sh\nexit 1\n"); gh.chmod(gh.stat().st_mode | stat.S_IEXEC)
    return proj


def _run(proj: Path, tmp_path: Path) -> dict:
    env = dict(os.environ)
    env["PATH"] = f"{tmp_path / 'bin'}:{env.get('PATH', '')}"
    env["HOME"] = str(tmp_path / "home"); (tmp_path / "home").mkdir(exist_ok=True)
    env.pop("CLAUDE_PROJECT_DIR", None)
    r = subprocess.run(["bash", str(proj / ".claude" / "hooks" / "security-assert.sh")],
                       cwd=proj, env=env, capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, r.stderr
    start = r.stdout.find("{")
    assert start != -1, f"no JSON in hook output:\n{r.stdout}\n{r.stderr}"
    return json.loads(r.stdout[start:])


def _check(report: dict, number: int) -> dict:
    for c in report["checks"]:
        if int(c.get("id", -1)) == number:
            c.setdefault("status", c.get("result"))
            return c
    raise AssertionError(f"check {number} not in report: {report['checks']}")


def test_compliant_fixture_passes_local_checks(tmp_path):
    proj = _fixture(tmp_path, "tp@example.com")
    rep = _run(proj, tmp_path)
    assert rep["critical_failures"] == 0
    assert _check(rep, 2)["status"] == "PASS"
    assert _check(rep, 9)["status"] == "PASS"
    assert rep["skips"] >= 6                      # network checks skipped without gh
    assert (proj / "tasks" / "tp" / "SECOPS.md").is_file()


def test_unapproved_skill_fails_allowlist_check(tmp_path):
    proj = _fixture(tmp_path, "tp@example.com", skills=("alpha", "rogue"))
    rep = _run(proj, tmp_path)
    # The allowlist check is severity Low and records WARN (not FAIL) with the
    # unknown skill named — the posture report still surfaces it.
    assert _check(rep, 9)["status"] == "WARN"
    assert "rogue" in json.dumps(_check(rep, 9))


def test_off_domain_email_is_a_critical_failure(tmp_path):
    proj = _fixture(tmp_path, "tp@elsewhere.org")
    rep = _run(proj, tmp_path)
    assert _check(rep, 2)["status"] == "FAIL"
    assert rep["critical_failures"] >= 1
