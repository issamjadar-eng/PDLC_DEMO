from dataclasses import dataclass, field
from pathlib import Path

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


def render(path: Path) -> RenderedFile:
    ext = path.suffix.lower()
    size = path.stat().st_size

    if ext == ".md":
        return _render_markdown(path, size)
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


def _render_markdown(path: Path, size: int) -> RenderedFile:
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
    return RenderedFile(
        kind="markdown",
        extension=".md",
        size=size,
        body_html=html,
        frontmatter=frontmatter,
    )
