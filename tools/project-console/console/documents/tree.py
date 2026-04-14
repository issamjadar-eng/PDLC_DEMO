from dataclasses import dataclass
from pathlib import Path

import yaml

ROOT_NAMES = ["docs", "tasks"]
TOP_FILES = ["project.yml"]


@dataclass(frozen=True)
class Entry:
    name: str
    path: str
    is_dir: bool
    size: int | None
    excerpt: str = ""


def _roots(repo_root: Path) -> dict[str, Path]:
    return {name: repo_root / name for name in ROOT_NAMES if (repo_root / name).is_dir()}


def resolve_virtual_path(repo_root: Path, virtual: str) -> Path | None:
    virtual = virtual.strip("/")
    if not virtual:
        return None
    parts = virtual.split("/")
    head = parts[0]
    if head in TOP_FILES and len(parts) == 1:
        p = (repo_root / head).resolve()
        return p if p.is_file() else None
    root_map = _roots(repo_root)
    if head not in root_map:
        return None
    root = root_map[head].resolve()
    try:
        target = (root / "/".join(parts[1:])).resolve()
    except (OSError, ValueError):
        return None
    try:
        target.relative_to(root)
    except ValueError:
        return None
    if not target.exists():
        return None
    return target


def list_dir(repo_root: Path, virtual: str) -> list[Entry]:
    virtual = virtual.strip("/")
    if not virtual:
        entries: list[Entry] = []
        for name in ROOT_NAMES:
            p = repo_root / name
            if p.is_dir():
                entries.append(Entry(name=name, path=name, is_dir=True, size=None))
        for f in TOP_FILES:
            p = repo_root / f
            if p.is_file():
                entries.append(
                    Entry(
                        name=f,
                        path=f,
                        is_dir=False,
                        size=p.stat().st_size,
                        excerpt=_excerpt(p),
                    )
                )
        return entries

    abs_path = resolve_virtual_path(repo_root, virtual)
    if abs_path is None or not abs_path.is_dir():
        return []

    entries = []
    for child in sorted(abs_path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower())):
        if child.name.startswith("."):
            continue
        entries.append(
            Entry(
                name=child.name,
                path=f"{virtual}/{child.name}",
                is_dir=child.is_dir(),
                size=child.stat().st_size if child.is_file() else None,
                excerpt=_excerpt(child) if child.is_file() else "",
            )
        )
    return entries


def _dir_has_any_children(abs_path: Path) -> bool:
    try:
        for child in abs_path.iterdir():
            if not child.name.startswith("."):
                return True
    except OSError:
        pass
    return False


def _entry_dict(name: str, virtual_path: str, abs_path: Path) -> dict:
    is_dir = abs_path.is_dir()
    return {
        "name": name,
        "path": virtual_path,
        "is_dir": is_dir,
        "size": abs_path.stat().st_size if not is_dir else None,
        "excerpt": _excerpt(abs_path) if not is_dir else "",
        "has_children": _dir_has_any_children(abs_path) if is_dir else False,
    }


def list_tree(repo_root: Path, max_depth: int = 3) -> list[dict]:
    """Return the top of the virtual tree nested to ``max_depth`` levels.

    Each node is a plain dict with ``name``, ``path``, ``is_dir``, ``size``,
    ``excerpt``, ``has_children``, and (for dirs within depth) ``children``.
    Dirs at exactly ``max_depth`` are returned without ``children`` but with
    ``has_children`` set so the UI knows to lazy-load on expand.
    """
    nodes: list[dict] = []
    # Virtual roots: docs/, tasks/, project.yml
    for name in ROOT_NAMES:
        p = repo_root / name
        if p.is_dir():
            node = _entry_dict(name, name, p)
            node["children"] = _children(repo_root, p, name, depth=1, max_depth=max_depth)
            nodes.append(node)
    for f in TOP_FILES:
        p = repo_root / f
        if p.is_file():
            nodes.append(_entry_dict(f, f, p))
    return nodes


def _children(
    repo_root: Path,
    abs_dir: Path,
    virtual: str,
    depth: int,
    max_depth: int,
) -> list[dict]:
    out: list[dict] = []
    try:
        children = sorted(
            abs_dir.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower())
        )
    except OSError:
        return out
    for child in children:
        if child.name.startswith("."):
            continue
        child_virtual = f"{virtual}/{child.name}"
        node = _entry_dict(child.name, child_virtual, child)
        if child.is_dir() and depth < max_depth:
            node["children"] = _children(
                repo_root, child, child_virtual, depth + 1, max_depth
            )
        out.append(node)
    return out


README_CANDIDATES = ("README.md", "readme.md", "Readme.md", "README.markdown", "readme.markdown")


def find_folder_readme(abs_dir: Path) -> Path | None:
    """Return the first README-like file inside ``abs_dir``, case-insensitive."""
    if not abs_dir.is_dir():
        return None
    try:
        by_lower = {p.name.lower(): p for p in abs_dir.iterdir() if p.is_file()}
    except OSError:
        return None
    for name in README_CANDIDATES:
        hit = by_lower.get(name.lower())
        if hit is not None:
            return hit
    return None


def list_children(repo_root: Path, virtual: str) -> list[dict]:
    """Flat list of one directory's immediate children (for lazy-load)."""
    abs_path = resolve_virtual_path(repo_root, virtual)
    if abs_path is None or not abs_path.is_dir():
        return []
    return _children(repo_root, abs_path, virtual, depth=1, max_depth=1)


def breadcrumbs(virtual: str) -> list[tuple[str, str]]:
    crumbs = [("Documents", "")]
    virtual = virtual.strip("/")
    if not virtual:
        return crumbs
    parts = virtual.split("/")
    for i, part in enumerate(parts):
        crumbs.append((part, "/".join(parts[: i + 1])))
    return crumbs


def _excerpt(path: Path, max_chars: int = 240) -> str:
    if path.suffix.lower() != ".md":
        return ""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""
    body = text
    if text.startswith("---"):
        try:
            _, fm, body = text.split("---", 2)
            meta = yaml.safe_load(fm) or {}
            desc = meta.get("description")
            if isinstance(desc, str) and desc.strip():
                return desc.strip()[:max_chars]
        except Exception:
            body = text
    for para in body.split("\n\n"):
        para = para.strip()
        if para and not para.startswith("#") and not para.startswith(">"):
            return para.replace("\n", " ")[:max_chars]
    return ""
