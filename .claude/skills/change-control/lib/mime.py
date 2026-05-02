"""Mime / extension helpers for image-vs-file decisions.

Used by both inbound (normalizer) and outbound (`_md_to_adf`) paths to
decide whether a media reference renders as an image-card (markdown
`![alt](url)` / ADF `mediaSingle` with image attrs) or a file-card
(markdown `[label](url)` / ADF `mediaInline`/`mediaSingle` with file attrs).

Centralized so the inbound + outbound decisions stay in lock-step — a
file extension that adopt treats as image-card MUST publish back as
image-card on roundtrip, otherwise re-adopt would see drift.
"""
from __future__ import annotations

from typing import Literal

# Authoritative list of image extensions Confluence renders inline as
# image cards. Mirrored across normalizer + publish to ensure consistency.
IMAGE_EXTENSIONS: frozenset[str] = frozenset({
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".svg",
    ".webp",
    ".bmp",
    ".tiff",
    ".tif",
    ".heic",
    ".avif",
})


def is_image_extension(path: str) -> bool:
    """Return True if `path`'s extension matches an image type Confluence
    renders as an image card.

    `path` may include leading directories or query strings — only the
    final basename's extension is examined. Case-insensitive.
    """
    if not path:
        return False
    # Strip any URL query / fragment so `images/foo.png?v=1` still matches
    base = path.split("?", 1)[0].split("#", 1)[0]
    base = base.rsplit("/", 1)[-1]
    if "." not in base:
        return False
    ext = "." + base.rsplit(".", 1)[-1].lower()
    return ext in IMAGE_EXTENSIONS


def decide_card_kind(path: str) -> Literal["image", "file"]:
    """Decide image-card vs file-card based on extension.

    Anything not in `IMAGE_EXTENSIONS` is treated as a file (PDF, DOCX,
    XLSX, CSV, ZIP, TXT, etc.). External URLs that lack a clear extension
    fall through to `"file"` — the publish path keeps them as plain
    markdown links rather than promoting to ADF media nodes.
    """
    return "image" if is_image_extension(path) else "file"


__all__ = ["IMAGE_EXTENSIONS", "is_image_extension", "decide_card_kind"]
