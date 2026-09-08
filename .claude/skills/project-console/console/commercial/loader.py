"""Business-domain sidecar loader (Commercial, Finance, Manufacturing, ...).

The console never computes a business answer and never parses answer markdown for
structure. It reads only what the `commercial` skill engine publishes under a
DOMAIN ROOT — `docs/project/<domain>/` — one root per business domain. A domain
is DISCOVERED, never wired: any `docs/project/<slug>/.console/<slug>-index.json`
is a domain tab. `commercial` is simply the first such domain.

    .console/<domain>-index.json           — question roster + per-BQ statuses (schema 1.x;
                                             1.5+ carries a `domain` identity block)
    reports/BQ-NN/<edition>/data.json      — chart series + verdicts (evidence-classed)
    reports/BQ-NN/<edition>/edition.yml    — lifecycle metadata (draft/approved/superseded, pins)
    reports/BQ-NN/<edition>/approval.yml   — approver, checks, content hashes (approved editions)

Loose-coupling rule (same contract as Submission / Tasks / Gap-Analysis): sidecars
missing → empty state with a hint to run the skill's `render`; the console knows
nothing about how the numbers were produced — that's the point. Report *bodies*
render via the documents renderer using the repo-relative path in the sidecar.
"""
from __future__ import annotations

import json
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover — PyYAML ships with the console deps
    yaml = None

DOMAINS_PARENT = ("docs", "project")
DEFAULT_DOMAIN = "commercial"
# Nav icons the base template ships a sprite for; anything else falls back.
KNOWN_ICONS = {"commercial", "finance", "manufacturing"}


def _root(repo_root: Path, domain: str = DEFAULT_DOMAIN) -> Path:
    return repo_root.joinpath(*DOMAINS_PARENT, domain)


def _index_path(repo_root: Path, domain: str = DEFAULT_DOMAIN) -> Path:
    return _root(repo_root, domain) / ".console" / f"{domain}-index.json"


def _safe_slug(domain: str) -> bool:
    return bool(domain) and domain.replace("-", "").replace("_", "").isalnum()


def list_domains(repo_root: Path) -> list[dict]:
    """Every discoverable business domain, nav-ordered: the historical
    `commercial` root first, then the rest alphabetically. Each entry carries the
    sidecar's `domain` identity block (schema 1.5+) with folder-derived fallbacks
    so a 1.4 sidecar still renders a tab."""
    parent = repo_root.joinpath(*DOMAINS_PARENT)
    out = []
    if not parent.is_dir():
        return out
    for d in sorted(parent.iterdir()):
        if not d.is_dir() or not _safe_slug(d.name):
            continue
        idx = d / ".console" / f"{d.name}-index.json"
        if not idx.is_file():
            continue
        out.append(domain_meta(repo_root, d.name))
    out.sort(key=lambda m: (0 if m["key"] == DEFAULT_DOMAIN else 1, m["key"]))
    return out


def domain_meta(repo_root: Path, domain: str) -> dict:
    """Identity block for one domain (title, nav label, icon, base URL)."""
    blk = (load_index(repo_root, domain) or {}).get("domain") or {}
    title = blk.get("name") or domain.replace("-", " ").title()
    icon = blk.get("icon") or domain
    return {
        "key": domain,
        "name": title,
        "nav_title": blk.get("nav_title") or title,
        "tagline": blk.get("tagline") or "business questions answered with data",
        "icon": icon if icon in KNOWN_ICONS else "commercial",
        "id_prefix": blk.get("id_prefix") or "BQ",
        "href": f"/domains/{domain}",
        "root_rel": "/".join(DOMAINS_PARENT + (domain,)),
    }


def discover(repo_root: Path) -> dict:
    """Nav probe: the discovered domain list (cheap — one stat per candidate folder
    plus one small JSON read per domain for its title)."""
    domains = list_domains(repo_root)
    return {"has_index": bool(domains), "has_any": bool(domains), "domains": domains}


def _read_json(p: Path) -> dict | None:
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _read_yaml(p: Path) -> dict | None:
    if yaml is None:
        return None
    try:
        return yaml.safe_load(p.read_text(encoding="utf-8"))
    except (OSError, Exception):
        return None


def load_index(repo_root: Path, domain: str = DEFAULT_DOMAIN) -> dict | None:
    if not _safe_slug(domain):
        return None
    return _read_json(_index_path(repo_root, domain))


def question_row(repo_root: Path, bq: str, domain: str = DEFAULT_DOMAIN) -> dict | None:
    index = load_index(repo_root, domain) or {}
    for q in index.get("questions", []):
        if q.get("id") == bq:
            return q
    return None


def load_edition(repo_root: Path, bq: str, edition: str, domain: str = DEFAULT_DOMAIN) -> dict | None:
    """One edition's full detail: data.json + lifecycle + approval + report path."""
    edir = _root(repo_root, domain) / "reports" / bq / edition
    data = _read_json(edir / "data.json")
    meta = _read_yaml(edir / "edition.yml") or {}
    if data is None and not meta:
        return None
    approval = _read_yaml(edir / "approval.yml")
    quality = _read_json(edir / "quality.json")
    rel = edir.relative_to(repo_root)
    return {
        "quality": quality,
        "plan_pin": meta.get("plan"),
        "bq": bq,
        "edition": edition,
        "status": meta.get("status", "draft"),
        "created_at": meta.get("created_at"),
        "pins": meta.get("pins", {}),
        "data": data or {},
        "approval": approval,
        "report_path": str(rel / "report.md"),
        "data_path": str(rel / "data.json"),
    }


def load_pinned_table(repo_root: Path, dataset: str, snapshot: str) -> dict | None:
    """Rows of a pinned snapshot's normalized CSV — the tabular truth behind an
    answer's charts. Read-only; the console never mutates corpus data."""
    import csv as _csv

    ndir = repo_root / "docs" / "project" / "corpus" / dataset / "snapshots" / snapshot / "normalized"
    if not ndir.is_dir():
        return None
    csvs = sorted(ndir.glob("*.csv"))
    if not csvs:
        return None
    try:
        with open(csvs[0], newline="", encoding="utf-8") as f:
            reader = _csv.DictReader(f)
            columns = reader.fieldnames or []
            rows = [dict(r) for r in reader]
    except OSError:
        return None
    return {"dataset": dataset, "snapshot": snapshot, "file": csvs[0].name,
            "columns": columns, "rows": rows}


def team_names(repo_root: Path) -> list[str]:
    """Active roster names from project.yml — the approver choices for the UI
    approve action (who-may-approve: any rostered member, recorded by name)."""
    if yaml is None:
        return []
    try:
        data = yaml.safe_load((repo_root / "project.yml").read_text(encoding="utf-8"))
        return [m.get("name") for m in (data.get("team", {}).get("active") or []) if m.get("name")]
    except Exception:
        return []


def skill_render_script(repo_root: Path) -> Path | None:
    p = repo_root / ".claude" / "skills" / "commercial" / "scripts" / "commercial.py"
    return p if p.is_file() else None
