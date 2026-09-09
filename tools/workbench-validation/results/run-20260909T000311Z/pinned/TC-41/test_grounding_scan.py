"""Capability tests for grounding_scan.py — GROUNDING blocks and the
file-locator index must reference canonical sources only."""
from __future__ import annotations

import importlib.util
import json
import sqlite3
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPT = HERE.parent / "scripts" / "grounding_scan.py"
FIX = HERE / "fixtures" / "grounding"


def _load():
    spec = importlib.util.spec_from_file_location("grounding_scan", SCRIPT)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_good_agent_block_is_clean():
    m = _load()
    blocks, findings = m.scan_agents([FIX / "good-agent.md"], m.NON_CANONICAL)
    assert blocks == 1 and findings == []


def test_bad_agent_block_flags_each_non_canonical_source():
    m = _load()
    blocks, findings = m.scan_agents([FIX / "bad-agent.md"], m.NON_CANONICAL)
    paths = sorted(f["path"] for f in findings)
    assert blocks == 1
    assert paths == ["articles/agentic-overview.md",
                     "tasks/alice/_work/market-model.xlsx",
                     "tools/knowledge-packs/demo/pack/kb-01.md"]


def _fake_index(path: Path, rows):
    con = sqlite3.connect(str(path))
    con.execute("CREATE TABLE indexed_files (path TEXT PRIMARY KEY, content_hash TEXT, size_bytes INT, "
                "mtime REAL, indexed_at REAL, summary_method TEXT, kind TEXT)")
    con.executemany("INSERT INTO indexed_files VALUES (?, 'h', 1, 0, 0, 'x', 'md')", [(r,) for r in rows])
    con.commit()
    con.close()


def test_index_check_flags_excluded_rows(tmp_path):
    m = _load()
    idx = tmp_path / "index.db"
    _fake_index(idx, ["docs/project/README.md", "tasks/bob/_scratch/notes.md", "articles/x.md"])
    n, findings = m.scan_index(idx, m.NON_CANONICAL)
    assert n == 3 and sorted(f["path"] for f in findings) == ["articles/x.md", "tasks/bob/_scratch/notes.md"]


def test_cli_reads_corpus_excludes_and_exit_codes(tmp_path):
    (tmp_path / "project.yml").write_text(
        "file_locator:\n  index_path: idx.db\n  corpus_excludes:\n    - \"**/_scratch/**\"\n    - \"**/legacy/**\"\n")
    _fake_index(tmp_path / "idx.db", ["docs/a.md"])
    agents = tmp_path / "agents"; agents.mkdir()
    (agents / "a.md").write_text((FIX / "good-agent.md").read_text())
    r = subprocess.run([sys.executable, str(SCRIPT), "--project-root", str(tmp_path), "--agents",
                        str(agents / "*.md"), "--json"], capture_output=True, text=True)
    out = json.loads(r.stdout)
    assert r.returncode == 0 and out["total_findings"] == 0 and "**/legacy/**" in out["patterns"]
    _fake_index(tmp_path / "idx2.db", ["docs/legacy/old.md"])
    r = subprocess.run([sys.executable, str(SCRIPT), "--project-root", str(tmp_path), "--agents",
                        str(agents / "*.md"), "--index", str(tmp_path / "idx2.db"), "--json"],
                       capture_output=True, text=True)
    assert r.returncode == 1 and json.loads(r.stdout)["total_findings"] == 1
    r = subprocess.run([sys.executable, str(SCRIPT), "--project-root", str(tmp_path), "--agents",
                        str(tmp_path / "none" / "*.md")], capture_output=True, text=True)
    assert r.returncode == 2
