"""GitHub-direct registry catalog — works with read-only repo access.

The Registries section originally read a registry's catalog from its local
clone (`registries[].local_path` — the sync tooling's checkout). That bakes
in an assumption consumer projects can't always satisfy: customer projects
may have READ-ONLY access to the registry repo and no sync tooling at all.
This module makes GitHub itself the catalog source, via the `gh` CLI
(authenticated read access is enough):

- `refresh_catalog` — ONE git-trees API call enumerates every skill and the
  blob SHA of its VERSION / SKILL.md; blob contents are fetched only where
  the local install can't already answer (an installed skill whose local
  VERSION bytes hash to the same git blob SHA needs no fetch at all).
  The resolved catalog is cached at `.state/registry-catalog-<name>.json`
  with a timestamp — page loads read the cache; refresh is a button.
- `download_skill_dir` — fetches the registry tarball and extracts one
  skill's directory (safe `tarfile` data filter), so Add/Update works with
  no clone on disk.

Network calls live ONLY here and run on demand (refresh / install), never
on page load. Everything degrades to a clear error message, not a stack
trace — `RegistryRemoteError` carries the user-facing hint.
"""
from __future__ import annotations

import base64
import datetime as _dt
import hashlib
import json
import re
import subprocess
import tarfile
from pathlib import Path

import yaml

from console.setup.loader import (
    _FRONTMATTER_RE,
    _clip,
    _fallback_fm,
    _first_sentence,
)

GH_TIMEOUT_S = 120


class RegistryRemoteError(Exception):
    """User-facing failure (surfaced as HTTP 400 detail)."""


def _now_iso() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def catalog_cache_path(repo_root: Path, registry_name: str) -> Path:
    slug = re.sub(r"[^A-Za-z0-9_-]", "-", registry_name or "registry")
    return repo_root / ".state" / f"registry-catalog-{slug}.json"


def load_cached_catalog(repo_root: Path, registry_name: str) -> dict | None:
    p = catalog_cache_path(repo_root, registry_name)
    if not p.is_file():
        return None
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) and isinstance(data.get("skills"), dict) else None
    except Exception:
        return None


def blob_sha(content: bytes) -> str:
    """git's blob SHA-1 of raw content — lets us compare a local file against
    a git-trees entry without fetching the blob."""
    return hashlib.sha1(b"blob %d\x00" % len(content) + content).hexdigest()


def frontmatter_text(text: str) -> dict:
    """Best-effort YAML frontmatter of markdown TEXT (same fallback chain as
    the loader's path-based `_frontmatter`)."""
    m = _FRONTMATTER_RE.match(text or "")
    if not m:
        return {}
    block = m.group(1)
    try:
        data = yaml.safe_load(block)
        if isinstance(data, dict):
            return data
    except yaml.YAMLError:
        pass
    return _fallback_fm(block)


def _gh_api(args: list[str], timeout: int = GH_TIMEOUT_S) -> str:
    try:
        r = subprocess.run(
            ["gh", "api", *args], capture_output=True, text=True, timeout=timeout
        )
    except FileNotFoundError:
        raise RegistryRemoteError(
            "GitHub CLI (gh) is not installed — install it and run `gh auth login` "
            "(read access to the registry repo is enough)."
        )
    except subprocess.TimeoutExpired:
        raise RegistryRemoteError("GitHub API call timed out.")
    if r.returncode != 0:
        detail = (r.stderr or r.stdout or "").strip()[:300]
        raise RegistryRemoteError(f"GitHub API call failed: {detail or 'unknown error'}")
    return r.stdout


def fetch_tree(repo: str, branch: str) -> list[dict]:
    out = _gh_api([f"repos/{repo}/git/trees/{branch}?recursive=1"])
    try:
        data = json.loads(out)
    except json.JSONDecodeError:
        raise RegistryRemoteError("GitHub returned an unparseable tree response.")
    return data.get("tree") or []


def parse_skill_entries(tree: list[dict]) -> dict[str, dict]:
    """Pure: git-tree entries → {skill: {skillmd_sha, version_sha?}}.
    A directory counts as a skill only when it ships a SKILL.md."""
    skills: dict[str, dict] = {}
    for e in tree:
        if e.get("type") != "blob":
            continue
        m = re.match(r"^skills/([^/]+)/(VERSION|SKILL\.md)$", str(e.get("path") or ""))
        if not m:
            continue
        d = skills.setdefault(m.group(1), {})
        d["version_sha" if m.group(2) == "VERSION" else "skillmd_sha"] = str(e.get("sha") or "")
    return {k: v for k, v in skills.items() if v.get("skillmd_sha")}


def _blob_text(repo: str, sha: str) -> str:
    out = _gh_api([f"repos/{repo}/git/blobs/{sha}", "--jq", ".content"])
    try:
        return base64.b64decode(out).decode("utf-8", errors="replace")
    except Exception:
        raise RegistryRemoteError("GitHub returned an unparseable blob response.")


def _installed_state(repo_root: Path) -> dict[str, dict]:
    """{name: {version, version_blob_sha}} for locally installed skills."""
    out: dict[str, dict] = {}
    skills_dir = repo_root / ".claude" / "skills"
    if not skills_dir.is_dir():
        return out
    for d in skills_dir.iterdir():
        if not d.is_dir() or not (d / "SKILL.md").is_file():
            continue
        version = sha = ""
        vfile = d / "VERSION"
        if vfile.is_file():
            try:
                raw = vfile.read_bytes()
                version = raw.decode("utf-8", errors="replace").strip()
                sha = blob_sha(raw)
            except OSError:
                pass
        out[d.name] = {"version": version, "version_blob_sha": sha}
    return out


def refresh_catalog(repo_root: Path, registry: dict) -> dict:
    """Fetch a registry's skill catalog straight from GitHub and cache it.

    Blob fetches are minimized: an installed skill whose local VERSION bytes
    hash to the remote blob SHA is resolved locally; otherwise the VERSION
    blob (tiny) is fetched, and SKILL.md is fetched only for skills not
    installed locally (their description isn't available anywhere else)."""
    repo = str(registry.get("repo") or "")
    if not repo:
        raise RegistryRemoteError("Registry has no `repo` configured in project.yml.")
    branch = str(registry.get("branch") or "main")
    entries = parse_skill_entries(fetch_tree(repo, branch))
    installed = _installed_state(repo_root)

    skills: dict[str, dict] = {}
    for name in sorted(entries):
        e = entries[name]
        loc = installed.get(name)
        version = description = full_description = ""
        if loc and e.get("version_sha") and loc["version_blob_sha"] == e["version_sha"]:
            version = loc["version"]  # byte-identical VERSION — no fetch needed
        elif e.get("version_sha"):
            version = _blob_text(repo, e["version_sha"]).strip()
        if loc is None or not version:
            fm = frontmatter_text(_blob_text(repo, e["skillmd_sha"]))
            version = version or str(fm.get("version") or "")
            desc = str(fm.get("description") or "")
            description = _first_sentence(desc)
            full_description = _clip(desc, 900)
        skills[name] = {
            "version": version,
            "description": description,
            "full_description": full_description,
        }

    catalog = {
        "repo": repo,
        "branch": branch,
        "fetched_at": _now_iso(),
        "skills": skills,
    }
    cache = catalog_cache_path(repo_root, str(registry.get("name") or ""))
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")
    return catalog


# ── skill download (install path when no local clone exists) ─────────────────

def extract_skill_from_tarball(tarball: Path, name: str, dest: Path) -> Path:
    """Extract `*/skills/<name>/**` from a GitHub tarball into dest.
    Returns the extracted skill dir. tarfile's 'data' filter blocks path
    traversal, absolute paths, and out-of-tree links."""
    prefix_re = re.compile(rf"^[^/]+/skills/{re.escape(name)}(/|$)")
    try:
        with tarfile.open(tarball) as tf:
            members = [m for m in tf.getmembers() if prefix_re.match(m.name)]
            if not members:
                raise RegistryRemoteError(
                    f"skills/{name} not found in the registry tarball."
                )
            tf.extractall(dest, members=members, filter="data")
            top = members[0].name.split("/", 1)[0]
    except tarfile.TarError as e:
        raise RegistryRemoteError(f"Registry tarball could not be read ({e}).")
    src = dest / top / "skills" / name
    if not (src / "SKILL.md").is_file():
        raise RegistryRemoteError(
            f"skills/{name} in the registry tarball has no SKILL.md."
        )
    return src


def download_skill_dir(repo: str, branch: str, name: str, workdir: Path) -> Path:
    """Download the registry tarball via `gh api` and extract one skill."""
    tarball = workdir / "registry.tar.gz"
    try:
        with tarball.open("wb") as fh:
            r = subprocess.run(
                ["gh", "api", f"repos/{repo}/tarball/{branch}"],
                stdout=fh, stderr=subprocess.PIPE, timeout=GH_TIMEOUT_S,
            )
    except FileNotFoundError:
        raise RegistryRemoteError(
            "GitHub CLI (gh) is not installed — install it and run `gh auth login`."
        )
    except subprocess.TimeoutExpired:
        raise RegistryRemoteError("Registry tarball download timed out.")
    if r.returncode != 0:
        detail = (r.stderr or b"").decode(errors="replace").strip()[:300]
        raise RegistryRemoteError(f"Registry tarball download failed: {detail}")
    return extract_skill_from_tarball(tarball, name, workdir)
