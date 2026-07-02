import re
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


_md = md_lib.Markdown(
    extensions=["tables", "fenced_code", "toc", "sane_lists", "md_in_html"]
)

_DETAILS_OPEN_RE = re.compile(r"^(\s*)<details>\s*$")
_FENCE_RE = re.compile(r"^\s*(```+|~~~+)")


def _enable_md_in_details(body: str) -> str:
    """Mark block-level ``<details>`` tags so ``md_in_html`` parses markdown
    both *inside* and *after* them.

    Documents in this project wrap internal (non-filed) regions in
    ``<details>🔒 INTERNAL…</details>`` containers. Python-Markdown's raw-HTML
    block parser mishandles these — it stops converting the markdown that
    follows, so filed-body headings and tables leak through as literal text.
    Adding ``markdown="1"`` to each real container tag switches Python-Markdown
    to its robust HTML parser, which fixes both the inner and the trailing
    content.

    Only tags on their own line and outside code are rewritten, so the doc's
    inline ``<details>`` code-span mentions and fenced ```` ```html ```` example
    blocks are left untouched.
    """
    out = []
    in_fence = False
    for line in body.split("\n"):
        if _FENCE_RE.match(line):
            in_fence = not in_fence
            out.append(line)
            continue
        if not in_fence and _DETAILS_OPEN_RE.match(line):
            out.append(line.replace("<details>", '<details markdown="1">', 1))
        else:
            out.append(line)
    return "\n".join(out)


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
    html = _md.convert(_enable_md_in_details(body.strip()))
    return RenderedFile(
        kind="markdown",
        extension=".md",
        size=size,
        body_html=html,
        frontmatter=frontmatter,
    )
