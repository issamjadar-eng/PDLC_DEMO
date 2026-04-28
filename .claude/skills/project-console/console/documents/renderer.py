import posixpath
import re
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import quote, urlsplit

import markdown as md_lib
import yaml

HTML_EXTS = {".html", ".htm"}
TEXT_EXTS = {
    ".txt", ".yml", ".yaml", ".json", ".csv", ".py", ".js",
    ".ts", ".css", ".sh", ".toml", ".ini", ".cfg", ".log", ".xml",
}
PDF_EXTS = {".pdf"}
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"}


@dataclass
class RenderedFile:
    kind: str
    extension: str
    size: int
    body_html: str = ""
    body_text: str = ""
    frontmatter: dict = field(default_factory=dict)


_md = md_lib.Markdown(extensions=["tables", "fenced_code", "toc", "sane_lists"])

_REL_LINK_RE = re.compile(
    r'''(<(?P<tag>a|img)\b[^>]*?\s(?P<attr>href|src)=)(?P<q>["'])(?P<url>[^"']+)(?P=q)''',
    re.IGNORECASE,
)
_ABSOLUTE_URL_SCHEMES = (
    "http://", "https://", "mailto:", "tel:", "data:",
    "javascript:", "ftp://", "ws://", "wss://",
)


def _rewrite_relative_links(html: str, virtual_path: str) -> str:
    """Rewrite relative hrefs/srcs in rendered markdown to console deep-links.

    Markdown authors write paths relative to the source file. After conversion
    the browser would resolve them against /documents (the explorer URL) and
    404. We resolve each non-absolute href against the source doc's virtual
    directory and rewrite to /documents/view/<virtual> for navigation or
    /documents/raw/<virtual> for inline media.
    """
    base_dir = posixpath.dirname(virtual_path.strip("/"))

    def repl(m: re.Match) -> str:
        prefix = m.group(1)
        quote_ch = m.group("q")
        url = m.group("url")
        is_img = m.group("tag").lower() == "img"

        if not url or url.startswith("#"):
            return m.group(0)
        if url.lower().startswith(_ABSOLUTE_URL_SCHEMES):
            return m.group(0)
        if url.startswith("//"):
            return m.group(0)
        if url.startswith("/"):
            return m.group(0)

        parts = urlsplit(url)
        path_part = parts.path
        if not path_part:
            return m.group(0)

        joined = (
            posixpath.normpath(posixpath.join(base_dir, path_part))
            if base_dir else posixpath.normpath(path_part)
        )
        if joined.startswith("../") or joined == ".." or joined == ".":
            return m.group(0)

        encoded = quote(joined, safe="/")
        route = "/documents/raw/" if is_img else "/documents/view/"
        new_url = f"{route}{encoded}"
        if parts.query:
            new_url += f"?{parts.query}"
        if parts.fragment:
            new_url += f"#{parts.fragment}"
        return f'{prefix}{quote_ch}{new_url}{quote_ch}'

    return _REL_LINK_RE.sub(repl, html)


def render(path: Path, virtual_path: str | None = None) -> RenderedFile:
    ext = path.suffix.lower()
    size = path.stat().st_size

    if ext == ".md":
        return _render_markdown(path, size, virtual_path)
    if ext in HTML_EXTS:
        return RenderedFile(kind="html", extension=ext, size=size)
    if ext in TEXT_EXTS or path.name == "project.yml":
        text = path.read_text(encoding="utf-8", errors="replace")
        return RenderedFile(kind="text", extension=ext, size=size, body_text=text)
    if ext in PDF_EXTS:
        return RenderedFile(kind="pdf", extension=ext, size=size)
    if ext in IMAGE_EXTS:
        return RenderedFile(kind="image", extension=ext, size=size)
    return RenderedFile(kind="binary", extension=ext, size=size)


def _render_markdown(path: Path, size: int, virtual_path: str | None) -> RenderedFile:
    text = path.read_text(encoding="utf-8", errors="replace")
    frontmatter: dict = {}
    body = text
    if text.startswith("---"):
        try:
            _, fm, body = text.split("---", 2)
            parsed = yaml.safe_load(fm) or {}
            if isinstance(parsed, dict):
                frontmatter = parsed
        except Exception:
            body = text
            frontmatter = {}
    _md.reset()
    html = _md.convert(body.strip())
    if virtual_path:
        html = _rewrite_relative_links(html, virtual_path)
    return RenderedFile(
        kind="markdown",
        extension=".md",
        size=size,
        body_html=html,
        frontmatter=frontmatter,
    )
