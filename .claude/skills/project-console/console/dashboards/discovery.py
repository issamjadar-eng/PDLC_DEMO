"""Dashboard discovery — glob-scan `docs/` + merge with console.yaml overrides."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Dashboard:
    slug: str
    title: str
    description: str
    source: str  # virtual path under repo_root
    group: str
    order: int

    @property
    def embed_url(self) -> str:
        return f"/documents/raw/{self.source}"

    @property
    def source_url(self) -> str:
        return f"/documents#path={self.source}"


_TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)
_META_DESC_RE = re.compile(
    r'<meta\s+name=["\']description["\']\s+content=["\']([^"\']*)["\']',
    re.IGNORECASE,
)


def _extract_title(html: str, fallback: str) -> str:
    m = _TITLE_RE.search(html)
    return m.group(1).strip() if m else fallback


def _extract_description(html: str) -> str:
    m = _META_DESC_RE.search(html)
    return m.group(1).strip() if m else ""


def _slugify(filename: str) -> str:
    return Path(filename).stem


def _groupize(virtual_path: str) -> str:
    parts = Path(virtual_path).parts
    if len(parts) >= 2:
        return parts[-2].replace("-", " ").replace("_", " ").title()
    return "Dashboards"


def discover(repo_root: Path, config: dict) -> list[Dashboard]:
    """Discover dashboards by scanning configured glob patterns.

    config is the `dashboards:` section of console.yaml:
      {
        "patterns": [...],
        "overrides": {slug: {title, description, group, order}, ...}
      }
    """
    patterns = config.get("patterns") or []
    overrides = config.get("overrides") or {}

    seen: dict[str, Dashboard] = {}
    for pattern in patterns:
        for abs_path in sorted(repo_root.glob(pattern)):
            if not abs_path.is_file():
                continue
            rel = abs_path.relative_to(repo_root).as_posix()
            slug = _slugify(abs_path.name)
            if slug in seen:
                continue
            try:
                html = abs_path.read_text(encoding="utf-8", errors="ignore")[:8192]
            except Exception:
                html = ""
            title = _extract_title(html, slug.replace("-", " ").title())
            description = _extract_description(html)
            group = _groupize(rel)
            order = 100

            ov = overrides.get(slug) or {}
            title = ov.get("title", title)
            description = ov.get("description", description)
            group = ov.get("group", group)
            order = int(ov.get("order", order))

            seen[slug] = Dashboard(
                slug=slug,
                title=title,
                description=description,
                source=rel,
                group=group,
                order=order,
            )
    return sorted(seen.values(), key=lambda d: (d.order, d.title))
