#!/usr/bin/env python3
"""md-deck build.py — markdown source → single-file HTML deck.

Pipeline:
    1. parse_markdown(text)  -> list of blocks (heading/para/list/table/quote/image/hr/code)
    2. synthesize_slides()   -> list of slide dicts (title/agenda/divider/table/card-grid/list/quote/prose/image-feature)
    3. _inject_variants()    -> multi-emit variant slides (catalog mosaic + featured, scope-iceberg, concept-canvas, handoff-relay, principle-tiles)
    4. render()              -> HTML body
    5. wrap()                -> full document with provenance metadata, embedded CSS, embedded JS, manifest sidecar

CSS lives in .claude/skills/md-deck/styles/bold-signal.css.
JS lives in .claude/skills/md-deck/runtime/deck-runtime.js.
Icons live in .claude/skills/md-deck/scripts/icons.py.

v0.2 rebuild — Phase 2.6 of ben/039 after the 2026-05-01 session-loss event.
"""

from __future__ import annotations

import argparse
import getpass
import hashlib
import html as html_mod
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# Local icon repository (sibling module) — must resolve regardless of cwd.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from icons import (  # noqa: E402
    pick as _pick_icon_from_repo,
    pick_strict as _pick_icon_strict,
    detect_group as _detect_group,
    pick_group as _pick_group_icon,
    configure_vocabularies as _configure_vocabularies,
)


def _resolve_vocabulary_packs(cli_packs: list[str] | None) -> list[str]:
    """Resolve which icon vocabulary packs to load.

    Resolution order (first non-empty wins):
      1. --vocabulary CLI flag (comma-separated list, may be passed multiple times)
      2. project.yml `md_deck.vocabulary_packs` (list)
      3. Empty (trunk-only / domain-neutral)

    Returns a list of pack names. An empty list means trunk-only behavior.
    """
    # CLI flag — accumulated across all --vocabulary invocations
    if cli_packs:
        flat: list[str] = []
        for entry in cli_packs:
            for name in entry.split(","):
                name = name.strip()
                if name and name not in flat:
                    flat.append(name)
        if flat:
            return flat

    # project.yml fallback — walk up from cwd
    cur = Path.cwd().resolve()
    for parent in [cur, *cur.parents]:
        candidate = parent / "project.yml"
        if candidate.is_file():
            try:
                import yaml  # type: ignore[import-untyped]
            except ImportError:
                return []
            try:
                data = yaml.safe_load(candidate.read_text()) or {}
            except Exception:
                return []
            md_deck_cfg = (data.get("md_deck") or {}) if isinstance(data, dict) else {}
            packs = md_deck_cfg.get("vocabulary_packs") or []
            if isinstance(packs, list):
                return [str(p) for p in packs if p]
            break

    return []

VERSION = "0.6.1"
SKILL_DIR = Path(__file__).resolve().parent.parent  # .claude/skills/md-deck/
SKILLS_ROOT = SKILL_DIR.parent  # .claude/skills/
FRONTEND_SLIDES_DIR = SKILLS_ROOT / "frontend-slides"
COMPONENTS_DIR = FRONTEND_SLIDES_DIR / "components"
JS_PATH = SKILL_DIR / "runtime" / "deck-runtime.js"


# ---------------------------------------------------------------------------
# Component registry (v0.4 PR 1) — scaffolding only; CSS still emitted from the
# monolithic preset stylesheet. Per-component CSS extraction lands in later PRs.
# ---------------------------------------------------------------------------

def _parse_component_readme(path: Path) -> dict | None:
    """Parse a component README.md frontmatter block.

    Returns a dict with keys: name, cluster, purpose, favors, requires, forbids,
    status, body. Returns None if the file is missing or has no frontmatter.

    Hand-rolled YAML-subset parser — no PyYAML dependency. Supports:
      - top-level scalar keys (name, cluster, purpose, status)
      - one-level nested mapping (favors)
      - flow-list `requires: [a, b, c]`
      - empty mapping `favors: {}`
    Anything more exotic should fail loudly so we notice schema drift.
    """
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 4)
    if end == -1:
        return None
    fm_lines = text[4:end].splitlines()
    body = text[end + 5:]

    out: dict = {
        "favors": {},
        "requires": [],
        "forbids": [],
        "body": body,
    }
    current_map_key: str | None = None
    for raw in fm_lines:
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if raw.startswith("  ") and current_map_key:
            # nested mapping under current_map_key
            k, _, v = raw.strip().partition(":")
            if not _:
                continue
            v = v.strip()
            try:
                out[current_map_key][k.strip()] = float(v)
            except ValueError:
                out[current_map_key][k.strip()] = v
            continue
        current_map_key = None
        k, _, v = raw.partition(":")
        if not _:
            continue
        key = k.strip()
        val = v.strip()
        if val == "":
            current_map_key = key
            out.setdefault(key, {})
            continue
        if val == "{}":
            out[key] = {}
            continue
        if val.startswith("[") and val.endswith("]"):
            inner = val[1:-1].strip()
            out[key] = [s.strip() for s in inner.split(",") if s.strip()] if inner else []
            continue
        out[key] = val
    return out


def load_component_registry() -> dict[str, dict]:
    """Walk frontend-slides/components/ and return name → metadata dict.

    Returns an empty dict if the directory is absent (e.g., a project that
    installs md-deck without frontend-slides). The build proceeds either way
    in v0.4 PR 1 — registry is informational at this stage, not yet wired
    into rendering decisions. PR 2 will consume it for classifier scoring.
    """
    registry: dict[str, dict] = {}
    if not COMPONENTS_DIR.exists():
        return registry
    for child in sorted(COMPONENTS_DIR.iterdir()):
        if not child.is_dir():
            continue
        readme = child / "README.md"
        meta = _parse_component_readme(readme)
        if meta is None:
            continue
        name = meta.get("name") or child.name
        meta["name"] = name
        meta["folder"] = str(child.relative_to(SKILLS_ROOT))
        registry[name] = meta
    return registry


def _resolve_style_css(style: str) -> tuple[Path | None, Path | None]:
    """Resolve the (viewport-base, preset) CSS pair for a given style name.

    Prefer the canonical sources in frontend-slides; fall back to md-deck's
    own styles/ directory when frontend-slides is absent. Each returned path
    is None if not found — caller decides how to degrade.

    Owner of viewport rules: frontend-slides/viewport-base.css.
    Owner of style presets: frontend-slides/presets/<name>.css, with a
    legacy fallback to md-deck/styles/<name>.css for the bold-signal preset
    that predates the shared layer.
    """
    fs_viewport = FRONTEND_SLIDES_DIR / "viewport-base.css"
    fs_preset = FRONTEND_SLIDES_DIR / "presets" / f"{style}.css"
    md_legacy = SKILL_DIR / "styles" / f"{style}.css"

    viewport = fs_viewport if fs_viewport.exists() else None
    if fs_preset.exists():
        preset = fs_preset
    elif md_legacy.exists():
        preset = md_legacy
    else:
        preset = None
    return viewport, preset


def _v04_component_css() -> Path | None:
    """Return the v0.4 shared component CSS file if present.

    Holds the styling for the 8 PR-3 components (big-stat, mic-drop,
    timeline-horizontal, phase-stack, before-after, versus-split, bar-chart,
    roster-cards) plus the `candidates.html` chooser strip styling. Loaded
    after the preset CSS so component selectors override preset defaults.
    """
    p = FRONTEND_SLIDES_DIR / "components" / "_v04-components.css"
    return p if p.exists() else None


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def _slugify(s: str) -> str:
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-") or "deck"


def slugify_heading(section_num: str | None, title: str) -> str:
    """Mint a stable slug from a `### N.M Heading Title` heading.

    Examples:
        slugify_heading("8.5", "Rules — project conventions")
            → "s8-5-rules-project-conventions"
        slugify_heading("3", "Architecture overview")
            → "s3-architecture-overview"
        slugify_heading(None, "Untitled")
            → "s-untitled"

    Section identity is `(section_num, title)`; line numbers play no part.
    Callers wanting reserved slugs (`_title`, `_agenda`, `_divider-N`) bypass
    this helper and assemble the literal directly.
    """
    title_slug = _slugify(title or "section")
    if not section_num:
        return f"s-{title_slug}"
    num_slug = re.sub(r"[^0-9a-z]+", "-", str(section_num).lower()).strip("-")
    return f"s{num_slug}-{title_slug}"


def compute_section_sha256(source_text: str, lo: int, hi: int) -> str:
    """SHA-256 of source lines [lo..hi] inclusive (1-indexed) — section validity key.

    Hashes the *exact slice of source text* the section covers, so any content
    edit (heading retitle, body change, list reorder) flips the digest. Cache
    entries keyed by this digest become stale on edit; orphan sweep retires
    them on the next build.
    """
    lines = source_text.splitlines()
    lo = max(1, int(lo))
    hi = max(lo, int(hi))
    block = "\n".join(lines[lo - 1: hi])
    return hashlib.sha256(block.encode("utf-8")).hexdigest()


def _esc(s: str) -> str:
    return html_mod.escape(s, quote=True)


def _slide_slug(s: dict) -> str:
    """Resolve a slide's identity for emission/cache/picks lookups.

    Returns the slug minted at synthesize_slides time; falls back to the
    legacy `anchor` field for slides predating Phase 1 of ben/163. The
    fallback keeps any in-flight third-party slide dicts (e.g. fixtures
    from older tests) addressable.
    """
    return s.get("slug") or s.get("anchor", "")


def _shorten(text: str, n_words: int) -> str:
    words = text.split()
    if len(words) <= n_words:
        return text
    return " ".join(words[:n_words]).rstrip(",;:") + "…"


def _split_label_sub(text: str) -> tuple[str, str]:
    """Split a non-bold-led bullet into (label, subtitle) without losing content.

    Prefers a sentence or em-dash clause boundary so the tail lands in the
    subtitle; short bullets become the label whole. Never slices mid-word and
    never silently drops the tail — the old `text[:60]` fallback amputated
    sentences with no ellipsis.
    """
    t = text.strip()
    m = re.match(r"^(.{10,90}?[.:;!?])\s+(.+)$", t)
    if m:
        return m.group(1).strip(), m.group(2).strip()
    m = re.match(r"^(.{10,60}?)\s+[—–]\s+(.+)$", t)
    if m:
        return m.group(1).strip(), m.group(2).strip()
    if len(t) <= 90:
        return t, ""
    words = t.split()
    label_words: list[str] = []
    ln = 0
    for w in words:
        if ln + len(w) > 60 and label_words:
            break
        label_words.append(w)
        ln += len(w) + 1
    return " ".join(label_words).rstrip(",;:") + "…", " ".join(words[len(label_words):])


def _pick_icon(label: str) -> str:
    """Resolve a label to an SVG via the icons.py repository."""
    return _pick_icon_from_repo(label or "")


# ---------------------------------------------------------------------------
# Inline rendering — bold, italic, inline code, link-text-only, escape
# ---------------------------------------------------------------------------

_INLINE_CODE_RE = re.compile(r"`([^`]+)`")
_BOLD_RE = re.compile(r"\*\*([^*]+)\*\*")
_ITALIC_RE = re.compile(r"(?<![*\w])\*([^*\n]+?)\*(?!\*)")
_LINK_RE = re.compile(r"\[([^\]]+)\]\([^)]+\)")


def render_inline(text: str) -> str:
    """Render a markdown inline string to safe HTML.

    Order matters: extract code spans first (their contents must NOT be
    further parsed for bold/italic), then bold, italic, links.
    """
    if not text:
        return ""
    placeholders: list[str] = []

    def _stash(html: str) -> str:
        placeholders.append(html)
        return f"\x00{len(placeholders) - 1}\x00"

    # Inline code
    text = _INLINE_CODE_RE.sub(
        lambda m: _stash(f"<code>{_esc(m.group(1))}</code>"), text
    )
    # Bold
    text = _BOLD_RE.sub(
        lambda m: _stash(f"<strong>{_esc(m.group(1))}</strong>"), text
    )
    # Italic (single asterisk surrounded by word-bounded content)
    text = _ITALIC_RE.sub(
        lambda m: _stash(f"<em>{_esc(m.group(1))}</em>"), text
    )
    # Link → keep link text only (decks rarely want raw URLs)
    text = _LINK_RE.sub(lambda m: _stash(_esc(m.group(1))), text)

    # Escape remaining text, then re-insert placeholders unescaped
    text = _esc(text)
    for i, html in enumerate(placeholders):
        text = text.replace(_esc(f"\x00{i}\x00"), html)
        text = text.replace(f"\x00{i}\x00", html)
    return text


# ---------------------------------------------------------------------------
# Markdown block parser — line-based, no external deps
# ---------------------------------------------------------------------------

def parse_markdown(text: str) -> list[dict]:
    """Parse markdown text into a flat list of block dicts. Block types:
        - heading {level, text, line}
        - para    {text, line}
        - ulist   {items: [str], line}      (regular bullet list)
        - olist   {items: [str], line}      (numbered list)
        - table   {header: [str], rows: [[str]], line}
        - quote   {text, line}
        - image   {alt, src, line}          (single image block on its own line)
        - hr      {line}
        - code    {lang, body, line}        (kept for completeness; dropped at synthesis)
    """
    lines = text.splitlines()
    blocks: list[dict] = []
    i = 0
    in_code = False
    code_lang = ""
    code_body: list[str] = []
    code_start = 0

    while i < len(lines):
        raw = lines[i]
        line = raw.rstrip()
        line_no = i + 1

        # Fenced code blocks
        if line.startswith("```"):
            if in_code:
                blocks.append({
                    "type": "code", "lang": code_lang,
                    "body": "\n".join(code_body), "line": code_start,
                })
                in_code = False
                code_lang = ""
                code_body = []
            else:
                in_code = True
                code_lang = line[3:].strip()
                code_start = line_no
            i += 1
            continue

        if in_code:
            code_body.append(raw)
            i += 1
            continue

        # Heading
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            level = len(m.group(1))
            blocks.append({
                "type": "heading", "level": level,
                "text": m.group(2).strip(), "line": line_no,
            })
            i += 1
            continue

        # Horizontal rule
        if re.match(r"^-{3,}\s*$|^\*{3,}\s*$|^_{3,}\s*$", line):
            blocks.append({"type": "hr", "line": line_no})
            i += 1
            continue

        # Image-only line
        m = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)\s*$", line)
        if m:
            blocks.append({
                "type": "image", "alt": m.group(1), "src": m.group(2),
                "line": line_no,
            })
            i += 1
            continue

        # Blockquote
        if line.startswith("> "):
            quote_lines = [line[2:]]
            j = i + 1
            while j < len(lines) and lines[j].startswith("> "):
                quote_lines.append(lines[j][2:])
                j += 1
            blocks.append({
                "type": "quote", "text": " ".join(quote_lines),
                "line": line_no,
            })
            i = j
            continue

        # Table — pipe-style with at least one separator row
        if "|" in line and i + 1 < len(lines) and re.match(r"^\s*\|?\s*[-:|\s]+\|?\s*$", lines[i + 1]):
            header = [c.strip() for c in line.strip().strip("|").split("|")]
            rows: list[list[str]] = []
            j = i + 2
            while j < len(lines) and "|" in lines[j]:
                row = [c.strip() for c in lines[j].strip().strip("|").split("|")]
                if any(cell for cell in row):
                    rows.append(row)
                j += 1
            blocks.append({
                "type": "table", "header": header, "rows": rows,
                "line": line_no,
            })
            i = j
            continue

        # Ordered list (1. foo)
        if re.match(r"^\d+\.\s+", line):
            items = [re.sub(r"^\d+\.\s+", "", line)]
            j = i + 1
            while j < len(lines):
                nl = lines[j].rstrip()
                if re.match(r"^\d+\.\s+", nl):
                    items.append(re.sub(r"^\d+\.\s+", "", nl))
                    j += 1
                elif nl.startswith("   ") and items:
                    # Continuation indent
                    items[-1] = items[-1] + " " + nl.strip()
                    j += 1
                else:
                    break
            blocks.append({"type": "olist", "items": items, "line": line_no})
            i = j
            continue

        # Unordered list (- foo or * foo)
        if re.match(r"^[-*]\s+", line):
            items = [re.sub(r"^[-*]\s+", "", line)]
            j = i + 1
            while j < len(lines):
                nl = lines[j].rstrip()
                if re.match(r"^[-*]\s+", nl):
                    items.append(re.sub(r"^[-*]\s+", "", nl))
                    j += 1
                elif nl.startswith("  ") and items:
                    items[-1] = items[-1] + " " + nl.strip()
                    j += 1
                else:
                    break
            blocks.append({"type": "ulist", "items": items, "line": line_no})
            i = j
            continue

        # Paragraph (blank-line separated)
        if line.strip():
            para = [line]
            j = i + 1
            while j < len(lines):
                nl = lines[j].rstrip()
                if not nl.strip() or re.match(
                    r"^(#{1,6}\s|>\s|[-*]\s|\d+\.\s|```|!\[)", nl
                ) or "|" in nl and j + 1 < len(lines) and re.match(
                    r"^\s*\|?\s*[-:|\s]+\|?\s*$", lines[j + 1]
                ):
                    break
                para.append(nl)
                j += 1
            blocks.append({
                "type": "para", "text": " ".join(p.strip() for p in para),
                "line": line_no,
            })
            i = j
            continue

        # Blank
        i += 1

    return blocks


# ---------------------------------------------------------------------------
# Slide synthesis — block sequence → slide list
# ---------------------------------------------------------------------------

def synthesize_slides(blocks: list[dict], source_path: Path,
                      source_text: str = "") -> list[dict]:
    """Walk the block stream and synthesize the slide list.

    Each slide carries two parallel identity fields during the slug-migration
    shadow window:
      - `anchor`           — legacy `L<lo>-L<hi>` form, still drives cache/picks.
      - `slug`             — stable identity derived from heading text. Reserved
                             slugs `_title`, `_agenda`, `_divider-<N>` for slides
                             without a content heading. Deduped per build via a
                             counter suffix (`-2`, `-3`, …) when collisions occur.
      - `source_sha256`    — SHA-256 of the source slice (validity key for caches).
      - `source_lines`     — informational `L<lo>-L<hi>` for diagnostics.

    `source_text` is the raw markdown source, needed to compute the SHA. When
    omitted (legacy callers), SHA fields are left empty and slug minting still
    works.
    """
    slides: list[dict] = []
    used_slugs: dict[str, int] = {}

    def _mint(slug: str) -> str:
        n = used_slugs.get(slug, 0)
        used_slugs[slug] = n + 1
        return slug if n == 0 else f"{slug}-{n + 1}"

    def _sha(lo: int, hi: int) -> str:
        return compute_section_sha256(source_text, lo, hi) if source_text else ""

    # 1. Title slide — first H1 + lead paragraph + any **Foo:** bar meta lines
    title_text = ""
    lead = ""
    meta_pairs: list[tuple[str, str]] = []
    cursor = 0
    while cursor < len(blocks) and blocks[cursor]["type"] != "heading":
        cursor += 1
    if cursor < len(blocks) and blocks[cursor]["level"] == 1:
        title_text = blocks[cursor]["text"]
        cursor += 1
        # Walk subsequent paragraphs and classify each as meta vs lead.
        # A paragraph is "meta" if it contains ≥2 `**Key:** value` pairs.
        meta_re = re.compile(r"\*\*([^*]+):\*\*\s*([^*]+?)(?=\s*\*\*[^*]+:\*\*|\s*$)")
        while cursor < len(blocks) and blocks[cursor]["type"] == "para":
            t = blocks[cursor]["text"]
            matches = list(meta_re.finditer(t))
            if len(matches) >= 2 and not meta_pairs:
                meta_pairs = [(m.group(1).strip(), m.group(2).strip()) for m in matches]
            elif not lead:
                lead = t
            else:
                break  # both filled; stop
            cursor += 1

    if title_text:
        title_line = blocks[0].get("line", 1)
        slides.append({
            "type": "title",
            "title": title_text,
            "lead": lead,
            "meta": meta_pairs,
            "anchor": f"L{title_line}",
            "section": None,
            "slug": _mint("_title"),
            "source_lines": f"L{title_line}",
            "source_sha256": _sha(title_line, title_line),
        })

    # 2. Agenda — computed from H2 sections (auto-injected after title)
    h2s = [b for b in blocks if b["type"] == "heading" and b["level"] == 2]
    agenda_items: list[tuple[str, str]] = []
    for h in h2s:
        m = re.match(r"^(\d+)\.?\s+(.*)$", h["text"])
        if m:
            agenda_items.append((m.group(1), m.group(2)))
    if agenda_items:
        slides.append({
            "type": "agenda",
            "title": "Agenda",
            "items": agenda_items,
            "anchor": "computed",
            "section": None,
            "slug": _mint("_agenda"),
            "source_lines": "computed",
            "source_sha256": "",
        })

    # 3. Walk remaining blocks, building one slide per H2/H3/H4 section
    current_section: str | None = None
    current_section_title: str = ""
    i = cursor
    while i < len(blocks):
        b = blocks[i]
        if b["type"] == "heading" and b["level"] == 2:
            m = re.match(r"^(\d+)\.?\s+(.*)$", b["text"])
            if m:
                current_section = m.group(1)
                current_section_title = m.group(2)
                slides.append({
                    "type": "divider",
                    "title": m.group(2),
                    "section": m.group(1),
                    "anchor": f"L{b['line']}",
                    "slug": _mint(f"_divider-{m.group(1)}"),
                    "source_lines": f"L{b['line']}",
                    "source_sha256": _sha(b["line"], b["line"]),
                })
                # If the H2 has body content directly under it (no H3 child
                # before the next H2), emit a content slide for that body.
                peek = i + 1
                direct_body: list[dict] = []
                while peek < len(blocks):
                    nb = blocks[peek]
                    if nb["type"] == "heading" and nb["level"] <= 2:
                        break
                    if nb["type"] == "heading" and nb["level"] >= 3:
                        direct_body = []  # reset; H3 will own its own content
                        break
                    direct_body.append(nb)
                    peek += 1
                if direct_body:
                    body_anchor_end = direct_body[-1].get("line", b["line"])
                    body_slide = _classify_section_slide(
                        title=current_section_title,
                        section=current_section,
                        content=direct_body,
                        anchor=f"L{b['line']}-L{body_anchor_end}",
                    )
                    if body_slide is not None:
                        body_slide["slug"] = _mint(
                            slugify_heading(current_section, current_section_title)
                        )
                        body_slide["source_lines"] = f"L{b['line']}-L{body_anchor_end}"
                        body_slide["source_sha256"] = _sha(b["line"], body_anchor_end)
                        slides.append(body_slide)
                    i = peek
                    continue
            else:
                current_section = None
                current_section_title = b["text"]
            i += 1
            continue
        if b["type"] == "heading" and b["level"] in (3, 4):
            heading_text = b["text"]
            section_match = re.match(r"^([\d.]+)\s+(.*)$", heading_text)
            section_num = section_match.group(1) if section_match else (current_section or "")
            slide_title = section_match.group(2) if section_match else heading_text
            anchor_start = b["line"]

            # Collect content blocks until next heading at same/higher level
            content: list[dict] = []
            j = i + 1
            while j < len(blocks):
                nb = blocks[j]
                if nb["type"] == "heading" and nb["level"] <= b["level"]:
                    break
                content.append(nb)
                j += 1
            anchor_end = blocks[j - 1].get("line", anchor_start) if content else anchor_start

            slide = _classify_section_slide(
                title=slide_title,
                section=section_num,
                content=content,
                anchor=f"L{anchor_start}-L{anchor_end}",
            )
            if slide is not None:
                slide["slug"] = _mint(slugify_heading(section_num, slide_title))
                slide["source_lines"] = f"L{anchor_start}-L{anchor_end}"
                slide["source_sha256"] = _sha(anchor_start, anchor_end)
                slides.append(slide)
            i = j
            continue
        i += 1

    return slides


def _classify_section_slide(*, title: str, section: str, content: list[dict],
                            anchor: str) -> dict | None:
    """Decide what slide-type fits a section's content."""
    # Drop code blocks
    content = [c for c in content if c["type"] != "code"]
    if not content:
        return {
            "type": "prose-slide", "title": title, "section": section,
            "anchor": anchor, "paragraphs": [], "bullets": [],
        }

    images = [c for c in content if c["type"] == "image"]
    tables = [c for c in content if c["type"] == "table"]
    quotes = [c for c in content if c["type"] == "quote"]
    ulists = [c for c in content if c["type"] == "ulist"]
    olists = [c for c in content if c["type"] == "olist"]
    paras = [c for c in content if c["type"] == "para"]

    # Image-feature: a single image block + prose/bullets
    if images:
        img = images[0]
        return {
            "type": "image-feature", "title": title, "section": section,
            "anchor": anchor, "image": img,
            "paragraphs": [p["text"] for p in paras],
            "bullets": (ulists[0]["items"] if ulists else
                        olists[0]["items"] if olists else []),
        }

    # Table slide
    if tables:
        t = tables[0]
        return {
            "type": "table-slide", "title": title, "section": section,
            "anchor": anchor, "table": t,
            "lead": paras[0]["text"] if paras else "",
        }

    # Quote slide
    if quotes:
        q = quotes[0]
        return {
            "type": "quote-slide", "title": title, "section": section,
            "anchor": anchor, "quote": q["text"],
            "lead": paras[0]["text"] if paras else "",
        }

    # Card-grid: bullet list where ≥half items begin with **bold**
    bullet_items = (ulists[0]["items"] if ulists else
                    olists[0]["items"] if olists else [])
    if bullet_items:
        bold_count = sum(1 for it in bullet_items if it.startswith("**"))
        if bold_count >= max(2, len(bullet_items) // 2):
            tiles = []
            for it in bullet_items:
                m = re.match(r"^\*\*([^*]+?)\*\*[:,.\s—-]*\s*(.*)$", it)
                if m:
                    label = m.group(1).strip()
                    sub = m.group(2).strip()
                else:
                    label, sub = _split_label_sub(it)
                tiles.append({"label": label, "subtitle": sub})
            return {
                "type": "card-grid", "title": title, "section": section,
                "anchor": anchor, "tiles": tiles,
                "lead": paras[0]["text"] if paras else "",
            }
        return {
            "type": "list-slide", "title": title, "section": section,
            "anchor": anchor, "items": bullet_items,
            "lead": paras[0]["text"] if paras else "",
        }

    # Prose slide
    return {
        "type": "prose-slide", "title": title, "section": section,
        "anchor": anchor, "paragraphs": [p["text"] for p in paras],
        "bullets": [],
    }


# ---------------------------------------------------------------------------
# Variant injection — multi-emit
# ---------------------------------------------------------------------------

SCOPE_KEYWORDS = (
    "filing scope", "carve-out", "carve out", "in vs out", "in-scope",
    "out of scope", "scope of",
)
TEACH_KEYWORDS = (
    "what an ", "what is ", "what are ", "where the ", "how it works",
    "what \"", "actually is",
)
HANDOFF_KEYWORDS = (
    "handoff", "who does what", "human/agent", "human-agent", "agent/human",
)

CATALOG_MOSAIC_PER_SLIDE = 8


def _slide_text_corpus(slide: dict) -> str:
    """Concatenate everything textual on the slide for keyword-content checks."""
    parts: list[str] = [str(slide.get("title", "")), str(slide.get("lead", ""))]
    for t in slide.get("tiles", []) or []:
        if isinstance(t, dict):
            parts.extend([str(t.get("label", "")), str(t.get("subtitle", ""))])
    for it in slide.get("items", []) or []:
        if isinstance(it, tuple):
            parts.append(" ".join(str(x) for x in it))
        else:
            parts.append(str(it))
    parts.extend(str(p) for p in (slide.get("paragraphs") or []))
    parts.extend(str(b) for b in (slide.get("bullets") or []))
    return " ".join(p for p in parts if p).lower()


def _inject_variants(slide: dict) -> list[dict]:
    """Return zero-or-more variant slides to emit RIGHT AFTER the input slide.

    Detection is broadened in v0.3 so dense card-grids and numbered lists
    always emit at least one variant (principle-tiles by default), without
    requiring a title-keyword match. Scope-iceberg, concept-canvas, and
    handoff-relay also check the slide's content corpus, not just the title.
    """
    out: list[dict] = []
    title = (slide.get("title") or "").lower()
    corpus = _slide_text_corpus(slide)

    # Handoff-relay takes priority on tables whose content reads as a
    # sequence of actor → step. Otherwise, ≥6-row 2-col tables become the
    # catalog mosaic + featured pair.
    if slide["type"] == "table-slide":
        table = slide.get("table") or {}
        rows = table.get("rows", [])
        cols = table.get("header", [])
        if any(k in corpus for k in HANDOFF_KEYWORDS):
            v = _make_handoff_relay(slide)
            if v and len(v.get("steps", [])) >= 2:
                out.append(v)
                return out
        if len(rows) >= 6 and len(cols) == 2:
            out.extend(_make_catalog_mosaic_slides(slide))
            out.append(_make_catalog_featured_slide(slide))
            return out  # catalog skips other variants

    # Scope-iceberg — title OR strong content signal (≥2 scope-keyword mentions).
    # Single passing mentions in unrelated slides are false positives.
    title_has_scope = any(k in title for k in SCOPE_KEYWORDS)
    scope_hits = sum(corpus.count(k) for k in SCOPE_KEYWORDS)
    if title_has_scope or scope_hits >= 2:
        v = _make_scope_iceberg(slide)
        if v and (len(v.get("in_items", [])) + len(v.get("out_items", []))) >= 3:
            out.append(v)

    # Concept-canvas — title OR content keyword
    if any(k in corpus for k in TEACH_KEYWORDS):
        v = _make_concept_canvas(slide)
        if v and len(v.get("facets", [])) >= 3:
            out.append(v)

    # Handoff-relay — title OR content keyword
    if any(k in corpus for k in HANDOFF_KEYWORDS):
        v = _make_handoff_relay(slide)
        if v and len(v.get("steps", [])) >= 2:
            out.append(v)

    # Principle-tiles — broadened: any card-grid with ≥4 tiles, OR any
    # list-slide whose bullets read like principles (≥4 items). v0.3 fix
    # for slides 6/8 of project-overview.
    if slide["type"] == "card-grid" and len(slide.get("tiles") or []) >= 4:
        if not any(v.get("type") == "principle-tiles" for v in out):
            v = _make_principle_tiles(slide)
            if v:
                out.append(v)
    elif slide["type"] == "list-slide" and len(slide.get("items") or []) >= 4:
        # Synthesize tiles from list items (split bold lead from rest if any)
        synthetic_tiles = []
        for it in (slide.get("items") or [])[:6]:
            m = re.match(r"^\*\*([^*]+?)\*\*[:,.\s—-]*\s*(.*)$", it)
            label, sub = (m.group(1).strip(), m.group(2).strip()) if m else _split_label_sub(it)
            synthetic_tiles.append({"label": label, "subtitle": sub})
        synthetic_slide = {**slide, "type": "card-grid", "tiles": synthetic_tiles}
        v = _make_principle_tiles(synthetic_slide)
        if v:
            out.append(v)

    return out


def _categorize_catalog_item(name: str, desc: str) -> dict:
    """Pick a category for a catalog row."""
    n = (name + " " + desc).lower()
    cats = [
        ("process",  "Process · lifecycle",  ["task", "lesson", "digest", "secops", "session", "active task", "lifecycle"]),
        ("docs",     "Docs · format",        ["medtech-docs", "docflow", "docx", "pdf", "xlsx", "pptx", "convert", "round-trip", "markdown"]),
        ("strategy", "Strategy · planning",  ["strategy", "advisor", "trace-matrix", "tracker", "manifest", "predicate", "regulatory", "submission"]),
        ("quality",  "Quality · governance", ["best-practices", "skill-creator", "audit", "compliance", "qms", "iso", "standard"]),
        ("ops",      "Ops · infra",          ["change-control", "sync-skills", "project-console", "console", "infra", "deploy", "pipeline"]),
    ]
    for key, label, kws in cats:
        if any(k in n for k in kws):
            return {"key": key, "label": label}
    return {"key": "default", "label": "Capability"}


def _make_catalog_mosaic_slides(slide: dict) -> list[dict]:
    rows = slide["table"]["rows"]
    title = slide.get("title", "")
    proto = [{"name": r[0].strip().strip("`")} for r in rows]
    group_type = _detect_group(proto, title=title)
    group_icon = _pick_group_icon(group_type) if group_type else None

    items_all: list[dict] = []
    for r in rows:
        name = r[0].strip().strip("`")
        desc = r[1].strip() if len(r) > 1 else ""
        cat = _categorize_catalog_item(name, desc)
        items_all.append({
            "name": name,
            "category": cat["key"],
            "category_label": cat["label"],
            "tagline": _shorten(desc, 8),
            "full_desc": desc,
            "icon": group_icon if group_icon else _pick_icon(name + " " + cat["key"]),
        })

    pages = [items_all[i:i + CATALOG_MOSAIC_PER_SLIDE]
             for i in range(0, len(items_all), CATALOG_MOSAIC_PER_SLIDE)]
    out = []
    total = len(pages)
    for idx, chunk in enumerate(pages):
        suffix = "" if idx == 0 else f" (continued · {idx + 1}/{total})"
        out.append({
            "type": "catalog-mosaic",
            "section": slide.get("section"),
            "title": slide["title"] + suffix,
            "anchor": slide.get("anchor", ""),
            "items": chunk,
            "page_idx": idx,
            "page_total": total,
            "group_type": group_type,
        })
    return out


def _make_catalog_featured_slide(slide: dict) -> dict:
    rows = slide["table"]["rows"]
    title = slide.get("title", "")
    proto = [{"name": r[0].strip().strip("`")} for r in rows]
    group_type = _detect_group(proto, title=title)
    group_icon = _pick_group_icon(group_type) if group_type else None

    featured: list[dict] = []
    rest: list[dict] = []
    for i, r in enumerate(rows):
        name = r[0].strip().strip("`")
        desc = r[1].strip() if len(r) > 1 else ""
        cat = _categorize_catalog_item(name, desc)
        rec = {
            "name": name,
            "desc": desc,
            "tagline": _shorten(desc, 14),
            "category": cat["key"],
            "category_label": cat["label"],
            "icon": group_icon if group_icon else _pick_icon(name + " " + cat["key"]),
        }
        (featured if i < 3 else rest).append(rec)
    return {
        "type": "catalog-featured",
        "section": slide.get("section"),
        "title": slide["title"],
        "anchor": slide.get("anchor", ""),
        "featured": featured,
        "rest": rest,
        "group_type": group_type,
    }


def _make_principle_tiles(slide: dict) -> dict:
    tiles_in = slide.get("tiles") or []
    tiles_out: list[dict] = []
    for t in tiles_in[:6]:
        label = t.get("label", "")
        sub = t.get("subtitle", "")
        # Prioritize the LABEL — that's the author's primary intent for
        # the tile. Try INTENT_PHRASES + KEYWORD_REGISTRY against the label
        # alone first; only widen to label + subtitle if no semantic match.
        # This stops incidental words in the description (e.g. "infusion"
        # in a battery hazard's body, or "module" in an alarm hazard) from
        # dragging the icon away from the actual concept.
        icon = _pick_icon_strict(label) or _pick_icon_strict(label + " " + sub) or _pick_icon(label)
        tiles_out.append({
            "label": label,
            "subtitle": _shorten(sub, 14),
            "icon": icon,
        })
    return {
        "type": "principle-tiles",
        "section": slide.get("section"),
        "title": slide["title"],
        "anchor": slide.get("anchor", ""),
        "tiles": tiles_out,
    }


def _make_scope_iceberg(slide: dict) -> dict | None:
    text = ""
    in_items: list[str] = []
    out_items: list[str] = []
    out_kws = (
        "out of scope", "out-of-scope", "out scope",
        "out of the", "outside",
        "carve-out", "exclude", "not in scope",
        "post-clearance", "ships post",
    )
    if slide["type"] == "card-grid":
        for t in slide.get("tiles", []):
            line = (t.get("label", "") + " " + t.get("subtitle", "")).lower()
            tag = t.get("label", "")
            if any(k in line for k in out_kws):
                out_items.append(tag)
            else:
                in_items.append(tag)
        if slide.get("lead"):
            text = slide["lead"]
    if not in_items and not out_items:
        return None
    return {
        "type": "scope-iceberg",
        "section": slide.get("section"),
        "title": slide["title"],
        "anchor": slide.get("anchor", ""),
        "in_items": in_items[:6],
        "out_items": out_items[:6],
        "lead": _shorten(text, 30) if text else "",
    }


def _make_concept_canvas(slide: dict) -> dict | None:
    bullets: list[str] = []
    if slide["type"] == "card-grid":
        bullets = [t.get("label", "") for t in slide.get("tiles", [])]
    elif slide["type"] == "list-slide":
        bullets = [b for b in slide.get("items", [])]
    if not bullets:
        return None
    return {
        "type": "concept-canvas",
        "section": slide.get("section"),
        "title": slide["title"],
        "anchor": slide.get("anchor", ""),
        "facets": bullets[:4],
        "lead": slide.get("lead", ""),
    }


def _make_handoff_relay(slide: dict) -> dict | None:
    steps: list[tuple[str, str]] = []
    if slide["type"] == "table-slide":
        for r in slide["table"]["rows"][:6]:
            actor = r[0] if r else "—"
            label = r[1] if len(r) > 1 else ""
            steps.append((actor.strip().strip("`"), label.strip()))
    elif slide["type"] in ("card-grid", "list-slide"):
        items = (slide.get("tiles") or
                 [{"label": b, "subtitle": ""} for b in slide.get("items", [])])
        for t in items[:6]:
            steps.append((t.get("label", ""), t.get("subtitle", "")))
    if not steps:
        return None
    return {
        "type": "handoff-relay",
        "section": slide.get("section"),
        "title": slide["title"],
        "anchor": slide.get("anchor", ""),
        "steps": steps,
        "summary": slide.get("lead", ""),
    }


# ---------------------------------------------------------------------------
# Density auto-scaling for tables
# ---------------------------------------------------------------------------

def _table_density(rows: list[list[str]], header: list[str]) -> str:
    cells = max(1, len(rows)) * max(1, len(header))
    if cells >= 50:
        return "density-very-compact"
    if cells >= 30:
        return "density-compact"
    if cells >= 18:
        return "density-tight"
    return ""


# ---------------------------------------------------------------------------
# Renderers
# ---------------------------------------------------------------------------

def _chrome(slide: dict, *, variant_label: str | None = None) -> str:
    """Render the chrome strip (number / brand / breadcrumb)."""
    section = slide.get("section")
    title = slide.get("title", "")
    if slide["type"] == "title":
        crumb = "Cover"
    elif slide["type"] == "agenda":
        crumb = "Agenda"
    elif slide["type"] == "divider":
        crumb = f"§{section}" if section else title
    else:
        crumb = (f"§{section} · {title}" if section else title)
    if variant_label:
        crumb = f"{crumb} · {variant_label}"
    return (
        '<div class="chrome">'
        '<span class="chrome-num">XX</span>'
        '<span class="brand">Project Overview</span>'
        f'<span class="crumb">{_esc(crumb)}</span>'
        '</div>'
    )


def render_title_slide(s: dict) -> str:
    meta_html = ""
    if s.get("meta"):
        rows = "".join(
            f'<div class="t-meta-row"><span class="t-meta-key">{_esc(k)}</span>'
            f'<span class="t-meta-val">{render_inline(v)}</span></div>'
            for k, v in s["meta"]
        )
        meta_html = f'<div class="t-meta-block reveal">{rows}</div>'
    return f'''
<section class="slide title-slide" data-source-anchor="{_esc(_slide_slug(s))}">
    {_chrome(s)}
    <div class="signal-block"></div>
    <div class="slide-content">
        <h1 class="reveal">{render_inline(s["title"])}</h1>
        <p class="lead reveal">{render_inline(s.get("lead", ""))}</p>
        {meta_html}
    </div>
</section>
'''


def render_agenda_slide(s: dict) -> str:
    cards = "".join(
        f'<div class="agenda-card"><div class="a-num">{_esc(num)}</div>'
        f'<div class="a-title">{render_inline(text)}</div></div>'
        for num, text in s["items"]
    )
    return f'''
<section class="slide" data-source-anchor="{_esc(_slide_slug(s))}">
    {_chrome(s)}
    <div class="slide-content">
        <h2 class="reveal">{render_inline(s["title"])}</h2>
        <div class="agenda-grid reveal">{cards}</div>
    </div>
</section>
'''


def render_divider_slide(s: dict) -> str:
    section = s.get("section", "")
    return f'''
<section class="slide divider-slide" data-source-anchor="{_esc(_slide_slug(s))}">
    {_chrome(s)}
    <div class="slide-content divider-content">
        <div class="divider-num reveal">{_esc(section)}</div>
        <h2 class="divider-title reveal">{render_inline(s["title"])}</h2>
    </div>
</section>
'''


def render_table_slide(s: dict) -> str:
    table = s.get("table") or {}
    header = table.get("header", [])
    rows = table.get("rows", [])
    density = _table_density(rows, header)
    th = "".join(f'<th>{render_inline(h)}</th>' for h in header)
    body = "".join(
        '<tr>' + "".join(f'<td>{render_inline(c)}</td>' for c in r) + '</tr>'
        for r in rows
    )
    lead_html = (
        f'<p class="lead reveal">{render_inline(s["lead"])}</p>'
        if s.get("lead") else ""
    )
    return f'''
<section class="slide" data-source-anchor="{_esc(_slide_slug(s))}">
    {_chrome(s)}
    <div class="slide-content">
        <h2 class="reveal">{render_inline(s["title"])}</h2>
        {lead_html}
        <div class="table-wrap reveal">
            <table class="compact-table {density}">
                <thead><tr>{th}</tr></thead>
                <tbody>{body}</tbody>
            </table>
        </div>
    </div>
</section>
'''


def render_card_grid(s: dict) -> str:
    lead_html = (
        f'<p class="lead reveal">{render_inline(s["lead"])}</p>'
        if s.get("lead") else ""
    )
    accents = ["accent-orange", "accent-amber", "accent-coral"]
    tiles = "".join(
        f'<div class="mini-card {accents[i % 3]}">'
        f'<div class="mc-label">{render_inline(t["label"])}</div>'
        f'<div class="mc-sub">{render_inline(t.get("subtitle", ""))}</div>'
        f'<div class="mc-full">'
        f'<div class="mc-full-label">{render_inline(t["label"])}</div>'
        f'<div class="mc-full-body">{render_inline(t.get("subtitle", ""))}</div>'
        '</div>'
        '</div>'
        for i, t in enumerate(s.get("tiles", []))
    )
    return f'''
<section class="slide" data-source-anchor="{_esc(_slide_slug(s))}">
    {_chrome(s)}
    <div class="slide-content">
        <h2 class="reveal">{render_inline(s["title"])}</h2>
        {lead_html}
        <div class="card-grid reveal">{tiles}</div>
    </div>
</section>
'''


def render_list_slide(s: dict) -> str:
    lead_html = (
        f'<p class="lead reveal">{render_inline(s["lead"])}</p>'
        if s.get("lead") else ""
    )
    bullets = "".join(
        f'<li class="reveal">{render_inline(it)}</li>'
        for it in s.get("items", [])
    )
    return f'''
<section class="slide" data-source-anchor="{_esc(_slide_slug(s))}">
    {_chrome(s)}
    <div class="slide-content">
        <h2 class="reveal">{render_inline(s["title"])}</h2>
        {lead_html}
        <ul class="bullets">{bullets}</ul>
    </div>
</section>
'''


def render_quote_slide(s: dict) -> str:
    return f'''
<section class="slide" data-source-anchor="{_esc(_slide_slug(s))}">
    {_chrome(s)}
    <div class="slide-content">
        <h2 class="reveal">{render_inline(s["title"])}</h2>
        <blockquote class="reveal">{render_inline(s["quote"])}</blockquote>
    </div>
</section>
'''


def render_prose_slide(s: dict) -> str:
    paras = "".join(
        f'<p class="reveal">{render_inline(p)}</p>' for p in s.get("paragraphs", [])
    )
    return f'''
<section class="slide" data-source-anchor="{_esc(_slide_slug(s))}">
    {_chrome(s)}
    <div class="slide-content">
        <h2 class="reveal">{render_inline(s["title"])}</h2>
        <div class="prose">{paras}</div>
    </div>
</section>
'''


def render_image_feature(s: dict) -> str:
    img = s.get("image") or {}
    src = img.get("src", "")
    alt = img.get("alt", "")
    paras = "".join(
        f'<p class="reveal">{render_inline(p)}</p>' for p in s.get("paragraphs", [])
    )
    bullets = ""
    if s.get("bullets"):
        bullets = '<ul class="bullets">' + "".join(
            f'<li class="reveal">{render_inline(b)}</li>' for b in s["bullets"]
        ) + '</ul>'
    return f'''
<section class="slide" data-source-anchor="{_esc(_slide_slug(s))}">
    {_chrome(s)}
    <div class="slide-content">
        <h2 class="reveal">{render_inline(s["title"])}</h2>
        <div class="image-feature-grid reveal">
            <div class="image-text">{paras}{bullets}</div>
            <div class="image-hero"><img src="{_esc(src)}" alt="{_esc(alt)}"/></div>
        </div>
    </div>
</section>
'''


def render_principle_tiles(s: dict) -> str:
    accents = ["accent-orange", "accent-amber", "accent-coral",
               "accent-orange", "accent-amber", "accent-coral"]
    tiles = "".join(
        f'<div class="principle-tile {accents[i % 6]}">'
        f'<div class="p-icon">{t["icon"]}</div>'
        f'<div class="p-label">{render_inline(t["label"])}</div>'
        f'<div class="p-sub">{render_inline(t.get("subtitle", ""))}</div>'
        '</div>'
        for i, t in enumerate(s.get("tiles", [])[:6])
    )
    return f'''
<section class="slide" data-source-anchor="{_esc(_slide_slug(s))}">
    {_chrome(s, variant_label="variant A — principle tiles")}
    <div class="slide-content">
        <div class="eyebrow reveal">Variation A · Principle Tiles</div>
        <h2 class="reveal">{render_inline(s["title"])}</h2>
        <div class="principle-tile-grid reveal">{tiles}</div>
    </div>
</section>
'''


def render_catalog_mosaic(s: dict) -> str:
    cells = []
    for it in s.get("items", []):
        cat_class = f'cat-{it.get("category", "default")}'
        # Resting state: icon + name + tagline. Hover popup (.cc-full) is
        # absolutely positioned so it paints above neighbors without
        # displacing them.
        cells.append(
            f'<div class="cat-cell {cat_class}">'
            f'<div class="cc-icon">{it["icon"]}</div>'
            f'<div class="cc-name">{_esc(it.get("name", ""))}</div>'
            f'<div class="cc-tag">{render_inline(it.get("tagline", ""))}</div>'
            f'<div class="cc-full"><div class="cc-full-name">{_esc(it.get("name", ""))}</div>'
            f'<div class="cc-full-cat">{_esc(it.get("category_label", ""))}</div>'
            f'<div class="cc-full-desc">{render_inline(it.get("full_desc", ""))}</div></div>'
            '</div>'
        )
    page_idx = s.get("page_idx", 0)
    eyebrow = "Variation A · Catalog Mosaic" if page_idx == 0 else f"Variation A · Catalog Mosaic — page {page_idx + 1}"
    return f'''
<section class="slide" data-source-anchor="{_esc(_slide_slug(s))}">
    {_chrome(s, variant_label="variant A — catalog mosaic")}
    <div class="slide-content">
        <div class="eyebrow reveal">{_esc(eyebrow)}</div>
        <h2 class="reveal">{render_inline(s["title"])}</h2>
        <div class="cat-mosaic reveal">{"".join(cells)}</div>
    </div>
</section>
'''


def render_catalog_featured(s: dict) -> str:
    heroes = "".join(
        f'<div class="cat-hero cat-{f.get("category", "default")}">'
        f'<div class="ch-icon">{f["icon"]}</div>'
        f'<div class="ch-name">{_esc(f.get("name", ""))}</div>'
        f'<div class="ch-tag">{_esc(f.get("category_label", ""))}</div>'
        f'<div class="ch-desc">{render_inline(f.get("tagline", ""))}</div>'
        '</div>'
        for f in s.get("featured", [])
    )
    chips = "".join(
        f'<span class="cat-chip cat-{r.get("category", "default")}">'
        f'{_esc(r.get("name", ""))}</span>'
        for r in s.get("rest", [])
    )
    chip_block = (
        f'<div class="cat-chip-row">'
        f'<div class="chip-eyebrow">↓ The rest of the catalog</div>'
        f'<div class="chip-grid">{chips}</div>'
        '</div>'
    ) if chips else ""
    return f'''
<section class="slide" data-source-anchor="{_esc(_slide_slug(s))}">
    {_chrome(s, variant_label="variant B — featured")}
    <div class="slide-content">
        <div class="eyebrow reveal">Variation B · Featured</div>
        <h2 class="reveal">{render_inline(s["title"])}</h2>
        <div class="cat-hero-row reveal">{heroes}</div>
        {chip_block}
    </div>
</section>
'''


def render_scope_iceberg(s: dict) -> str:
    in_items = s.get("in_items", [])
    out_items = s.get("out_items", [])
    in_lis = "".join(f'<li>{render_inline(t)}</li>' for t in in_items)
    out_lis = "".join(f'<li>{render_inline(t)}</li>' for t in out_items)
    lead = (f'<p class="lead reveal">{render_inline(s["lead"])}</p>'
            if s.get("lead") else "")
    return f'''
<section class="slide" data-source-anchor="{_esc(_slide_slug(s))}">
    {_chrome(s, variant_label="variant A — scope iceberg")}
    <div class="slide-content">
        <div class="eyebrow reveal">Variation A · Scope Iceberg</div>
        <h2 class="reveal">{render_inline(s["title"])}</h2>
        {lead}
        <div class="iceberg-grid reveal">
            <div class="iceberg-side iceberg-in">
                <div class="iside-label">FILING SCOPE — IN</div>
                <ul>{in_lis}</ul>
            </div>
            <div class="iceberg-side iceberg-out">
                <div class="iside-label">OUT OF SCOPE</div>
                <ul>{out_lis}</ul>
            </div>
        </div>
    </div>
</section>
'''


def render_concept_canvas(s: dict) -> str:
    facets = s.get("facets", [])
    facets_html = "".join(
        f'<div class="cc-facet"><div class="cc-bullet"></div>'
        f'<div class="cc-text">{render_inline(t)}</div></div>'
        for t in facets
    )
    lead = (f'<p class="lead reveal">{render_inline(s["lead"])}</p>'
            if s.get("lead") else "")
    return f'''
<section class="slide" data-source-anchor="{_esc(_slide_slug(s))}">
    {_chrome(s, variant_label="variant A — concept canvas")}
    <div class="slide-content">
        <div class="eyebrow reveal">Variation A · Concept Canvas</div>
        <h2 class="reveal">{render_inline(s["title"])}</h2>
        {lead}
        <div class="concept-canvas-grid reveal">{facets_html}</div>
    </div>
</section>
'''


def render_handoff_relay(s: dict) -> str:
    boxes = []
    for i, (actor, label) in enumerate(s.get("steps", [])[:6]):
        klass = ("human" if "human" in actor.lower()
                 else "agent" if "agent" in actor.lower() or "ai" in actor.lower()
                 else "either")
        boxes.append(
            f'<div class="relay-box {klass}">'
            f'<div class="r-step">{i + 1:02d}</div>'
            f'<div class="r-actor">{_esc(actor)}</div>'
            f'<div class="r-label">{render_inline(label)}</div>'
            '</div>'
        )
    summary = (
        f'<p class="muted reveal" style="text-align:center;margin-top:1rem;">'
        f'{render_inline(s["summary"])}</p>'
        if s.get("summary") else ""
    )
    return f'''
<section class="slide" data-source-anchor="{_esc(_slide_slug(s))}">
    {_chrome(s, variant_label="variant A — handoff relay")}
    <div class="slide-content">
        <div class="eyebrow reveal">Variation A · Handoff Relay</div>
        <h2 class="reveal">{render_inline(s["title"])}</h2>
        <div class="relay-track reveal">{"".join(boxes)}</div>
        {summary}
    </div>
</section>
'''


# Dispatch
# ---------------------------------------------------------------------------
# v0.4 component renderers (PR 3) — 8 new visual components.
# ---------------------------------------------------------------------------

_NUM_TOKEN_RE = re.compile(r"(\d+(?:\.\d+)?)\s*(%|x|×|kg|mg|ms|sec|min|hr)?", re.IGNORECASE)
_TIME_TOKEN_RE = re.compile(
    r"\b("
    r"week\s*\d+|q[1-4]\b|h[12]\b|"
    r"\d{4}[-/]\d{1,2}([-/]\d{1,2})?|"
    r"\d{4}-q[1-4]|"
    r"jan\w*|feb\w*|mar\w*|apr\w*|may|jun\w*|jul\w*|aug\w*|sep\w*|oct\w*|nov\w*|dec\w*"
    r")\b",
    re.IGNORECASE,
)


def _extract_first_number(text: str) -> tuple[str, str] | None:
    """Return (value, unit) for the first number-with-unit found, or None."""
    if not text:
        return None
    m = _NUM_TOKEN_RE.search(text)
    if not m:
        return None
    return (m.group(1), m.group(2) or "")


def _shortest_sentence(text: str) -> str:
    """Pick the shortest sentence from a paragraph — the punchline candidate."""
    if not text:
        return ""
    sents = re.split(r"(?<=[.!?])\s+", text.strip())
    sents = [s for s in sents if s and len(s.split()) >= 4]
    if not sents:
        return text
    return min(sents, key=lambda s: len(s.split()))


def _person_initials(name: str) -> str:
    """Derive a 2-char initials medallion from a name string."""
    cleaned = re.sub(r"[^A-Za-z\s.-]", " ", name.replace("`", ""))
    # Handle dr-okafor-anesthesia → "dr okafor anesthesia"
    cleaned = re.sub(r"[-_]", " ", cleaned)
    tokens = [t for t in cleaned.split() if t and t.lower() not in ("dr", "dr.", "nurse", "the", "a", "an")]
    if not tokens:
        return "•"
    if len(tokens) == 1:
        return tokens[0][:2].upper()
    return (tokens[0][:1] + tokens[-1][:1]).upper()


def render_big_stat(s: dict) -> str:
    """One number + label + supporting line, oversized."""
    title = s.get("title", "")
    section = s.get("section")
    text_pool = s.get("quote") or s.get("lead") or " ".join(s.get("paragraphs") or []) or ""
    num = _extract_first_number(text_pool)
    if num:
        value, unit = num
        hero = f'<div class="stat-hero">{_esc(value)}<span class="unit">{_esc(unit)}</span></div>'
    else:
        # Fall back: render the title prominently
        hero = f'<div class="stat-label">{_esc(title)}</div>'
    label = _esc(title)
    support = _esc(_shorten(text_pool, 36)) if text_pool else ""
    section_label = f'<div class="eyebrow reveal">§{section} · KEY METRIC</div>' if section else '<div class="eyebrow reveal">KEY METRIC</div>'
    return (
        f'<section class="slide big-stat" data-source-anchor="{_esc(_slide_slug(s))}">'
        f'{_chrome(s)}'
        f'<div class="slide-content">'
        f'{section_label}'
        f'<div class="reveal">{hero}</div>'
        f'<div class="stat-label reveal">{label}</div>'
        f'<div class="stat-support reveal">{support}</div>'
        f'</div>'
        f'</section>'
    )


def render_mic_drop(s: dict) -> str:
    """One short sentence, oversized, centered."""
    title = s.get("title", "")
    text_pool = s.get("quote") or s.get("lead") or " ".join(s.get("paragraphs") or []) or title
    line = _shortest_sentence(text_pool)
    return (
        f'<section class="slide mic-drop" data-source-anchor="{_esc(_slide_slug(s))}">'
        f'{_chrome(s)}'
        f'<div class="slide-content">'
        f'<div class="punchline reveal">{render_inline(line)}</div>'
        f'<div class="punchline-source reveal">§{_esc(s.get("section") or "")} · {_esc(title)}</div>'
        f'</div>'
        f'</section>'
    )


def render_timeline_horizontal(s: dict) -> str:
    """Dated milestones as a horizontal axis with dot-and-stem markers."""
    items = s.get("items") or s.get("bullets") or []
    if not items:
        # Try table rows
        table = s.get("table") or {}
        items = [" — ".join(str(c) for c in row) for row in (table.get("rows") or [])]
    items = items[:6]
    stops_html: list[str] = []
    for i, raw in enumerate(items):
        text = raw if isinstance(raw, str) else " ".join(str(x) for x in raw)
        m = _TIME_TOKEN_RE.search(text)
        when = m.group(0).upper() if m else f"STEP {i+1}"
        # Strip the time token from the body
        what = _TIME_TOKEN_RE.sub("", text, count=1).strip(" ,—-:.;")
        stops_html.append(
            f'<div class="stop reveal">'
            f'<span class="when">{_esc(when)}</span>'
            f'<div class="what">{render_inline(what)}</div>'
            f'</div>'
        )
    n = len(items) or 1
    return (
        f'<section class="slide" data-source-anchor="{_esc(_slide_slug(s))}">'
        f'{_chrome(s)}'
        f'<div class="slide-content">'
        f'<h2 class="reveal">{render_inline(s.get("title",""))}</h2>'
        f'<div class="timeline-h reveal">'
        f'<div class="axis"></div>'
        f'<div class="stops" style="--stops:{n};">{"".join(stops_html)}</div>'
        f'</div></div></section>'
    )


def render_phase_stack(s: dict) -> str:
    """Numbered phases with big-numeral blocks."""
    items = s.get("items") or s.get("bullets") or []
    if not items:
        table = s.get("table") or {}
        items = [" — ".join(str(c) for c in row) for row in (table.get("rows") or [])]
    items = items[:4]
    phases_html: list[str] = []
    for i, raw in enumerate(items):
        text = raw if isinstance(raw, str) else " — ".join(str(x) for x in raw)
        # Try to split "Actor — Description" via en-dash, em-dash, or pipe
        parts = re.split(r"\s*[—–|·]\s*", text, maxsplit=1)
        actor = parts[0].strip() if len(parts) > 1 else ""
        desc = (parts[1] if len(parts) > 1 else text).strip()
        phases_html.append(
            f'<div class="phase reveal">'
            f'<div class="phase-num">{i+1:02d}</div>'
            f'<div class="phase-actor">{_esc(actor)}</div>'
            f'<div class="phase-text">{render_inline(desc)}</div>'
            f'</div>'
        )
    cols = len(items) or 1
    return (
        f'<section class="slide" data-source-anchor="{_esc(_slide_slug(s))}">'
        f'{_chrome(s)}'
        f'<div class="slide-content">'
        f'<h2 class="reveal">{render_inline(s.get("title",""))}</h2>'
        f'<div class="phase-stack reveal" style="--phase-cols:{cols};">{"".join(phases_html)}</div>'
        f'</div></section>'
    )


def render_before_after(s: dict) -> str:
    """Two states side-by-side with an arrow + delta line."""
    title = s.get("title", "")
    pool = s.get("quote") or " ".join(s.get("paragraphs") or []) or s.get("lead") or ""
    sentences = re.split(r"(?<=[.!?])\s+", pool.strip()) or [pool]
    # Pick first two non-trivial sentences as before / after states
    before_text = sentences[0] if sentences else title
    after_text = sentences[1] if len(sentences) > 1 else ""
    if not after_text:
        # Try splitting the lead by commas; otherwise reuse title
        parts = re.split(r"[,;]\s+", before_text, maxsplit=1)
        if len(parts) == 2:
            before_text, after_text = parts
        else:
            after_text = title
    before_num = _extract_first_number(before_text)
    after_num = _extract_first_number(after_text)
    delta_match = _RATIO_PHRASE_RE.search(pool)
    delta_html = f'<div class="delta reveal">{_esc(delta_match.group(0))}</div>' if delta_match else ''
    before_stat_html = (
        f'<div class="ba-stat">{_esc(before_num[0])}<span style="font-size:0.5em">{_esc(before_num[1])}</span></div>'
        if before_num else ''
    )
    after_stat_html = (
        f'<div class="ba-stat">{_esc(after_num[0])}<span style="font-size:0.5em">{_esc(after_num[1])}</span></div>'
        if after_num else ''
    )
    return (
        f'<section class="slide" data-source-anchor="{_esc(_slide_slug(s))}">'
        f'{_chrome(s)}'
        f'<div class="slide-content">'
        f'<h2 class="reveal">{render_inline(title)}</h2>'
        f'<div class="before-after reveal">'
        f'<div class="ba-card before"><div class="ba-tag">BEFORE</div>'
        f'{before_stat_html}'
        f'<div class="ba-text">{render_inline(_shorten(before_text, 28))}</div></div>'
        f'<div class="arrow">→</div>'
        f'<div class="ba-card after"><div class="ba-tag">AFTER</div>'
        f'{after_stat_html}'
        f'<div class="ba-text">{render_inline(_shorten(after_text, 28))}</div></div>'
        f'{delta_html}'
        f'</div></div></section>'
    )


_RATIO_PHRASE_RE = re.compile(
    r"\b(reduction|down|up|increase|decrease|improvement|drop|rise|cut)\s+(by\s+)?\d+\S*",
    re.IGNORECASE,
)


def render_versus_split(s: dict) -> str:
    """Two columns with one accent color per column."""
    items = s.get("items") or s.get("bullets") or []
    tiles = s.get("tiles") or []
    if tiles:
        flat = [(t.get("label", "") + (" — " + t["subtitle"] if t.get("subtitle") else "")) for t in tiles]
    else:
        flat = [it if isinstance(it, str) else " ".join(str(x) for x in it) for it in items]
    # Heuristic split: items mentioning "in", "scope", "us", "ours" → left; items with "out", "them" → right
    left, right = [], []
    for f in flat:
        low = f.lower()
        if any(k in low for k in (" out ", "out of", "outside", "them", "theirs", "after")):
            right.append(f)
        elif any(k in low for k in (" in ", "in-scope", "scope =", "ours", "us ", "before")):
            left.append(f)
        else:
            (left if len(left) <= len(right) else right).append(f)
    left, right = left[:4], right[:4]
    if not left or not right:
        # Fallback: simple half-and-half split of all items
        flat = flat[:6]
        mid = len(flat) // 2 or 1
        left, right = flat[:mid], flat[mid:]

    def _li_html(items: list[str]) -> str:
        return "".join(f'<li>{render_inline(_shorten(i, 22))}</li>' for i in items)

    return (
        f'<section class="slide" data-source-anchor="{_esc(_slide_slug(s))}">'
        f'{_chrome(s)}'
        f'<div class="slide-content">'
        f'<h2 class="reveal">{render_inline(s.get("title",""))}</h2>'
        f'<div class="versus-split reveal">'
        f'<div class="vs-side left"><div class="vs-tag">A</div><ul class="vs-list">{_li_html(left)}</ul></div>'
        f'<div class="vs-divider">VS</div>'
        f'<div class="vs-side right"><div class="vs-tag">B</div><ul class="vs-list">{_li_html(right)}</ul></div>'
        f'</div></div></section>'
    )


def render_bar_chart(s: dict) -> str:
    """Labels with values rendered as drawn CSS bars."""
    items = s.get("items") or s.get("bullets") or []
    tiles = s.get("tiles") or []
    if tiles:
        rows_in = [(t.get("label", ""), t.get("subtitle", "")) for t in tiles]
    else:
        rows_in = []
        for raw in items:
            text = raw if isinstance(raw, str) else " ".join(str(x) for x in raw)
            # Split off bold lead if present
            m = re.match(r"^\*\*([^*]+)\*\*\s*[—.:-]\s*(.*)$", text)
            if m:
                rows_in.append((m.group(1).strip(), m.group(2).strip()))
            else:
                rows_in.append((text, text))

    # Extract numeric value per row
    parsed: list[tuple[str, float, str]] = []
    for label, body in rows_in:
        n = _extract_first_number(body) or _extract_first_number(label)
        if n:
            try:
                parsed.append((label, float(n[0]), n[0] + (n[1] or "")))
            except ValueError:
                continue
    if not parsed:
        # Bar chart non-viable when there are no numeric values; render as list
        return render_list_slide(s)
    parsed = parsed[:6]
    max_val = max(v for _, v, _ in parsed) or 1.0
    rows_html: list[str] = []
    for i, (label, val, display) in enumerate(parsed):
        pct = (val / max_val) * 100
        muted = " muted" if i > 0 and val == min(v for _, v, _ in parsed) else ""
        rows_html.append(
            f'<div class="bar-row{muted} reveal">'
            f'<div class="bar-label">{render_inline(_shorten(label, 8))}</div>'
            f'<div class="bar-track"><div class="bar-fill" style="--bar-width:{pct:.1f}%;"></div></div>'
            f'<div class="bar-value">{_esc(display)}</div>'
            f'</div>'
        )
    return (
        f'<section class="slide" data-source-anchor="{_esc(_slide_slug(s))}">'
        f'{_chrome(s)}'
        f'<div class="slide-content">'
        f'<h2 class="reveal">{render_inline(s.get("title",""))}</h2>'
        f'<div class="bar-chart reveal">{"".join(rows_html)}</div>'
        f'</div></section>'
    )


def render_roster_cards(s: dict) -> str:
    """Cohorts of people: initials medallion + name + role."""
    table = s.get("table") or {}
    rows = table.get("rows") or []
    if not rows:
        # Fall back to mosaic-style if no table
        return render_catalog_mosaic(s)
    cards_html: list[str] = []
    for row in rows[:9]:
        if len(row) < 2:
            continue
        name = str(row[0]).strip().strip("`")
        role = str(row[1]).strip()
        initials = _person_initials(name)
        # Friendlier display name
        display = name.replace("dr-", "Dr. ").replace("nurse-", "Nurse ").replace("-", " ").title()
        cards_html.append(
            f'<div class="roster-card reveal">'
            f'<div class="roster-medallion">{_esc(initials)}</div>'
            f'<div>'
            f'<div class="roster-name">{_esc(display)}</div>'
            f'<div class="roster-role">{render_inline(_shorten(role, 14))}</div>'
            f'</div></div>'
        )
    return (
        f'<section class="slide" data-source-anchor="{_esc(_slide_slug(s))}">'
        f'{_chrome(s)}'
        f'<div class="slide-content">'
        f'<h2 class="reveal">{render_inline(s.get("title",""))}</h2>'
        f'<div class="roster-cards reveal">{"".join(cards_html)}</div>'
        f'</div></section>'
    )


RENDERERS = {
    "title": render_title_slide,
    "agenda": render_agenda_slide,
    "divider": render_divider_slide,
    "table-slide": render_table_slide,
    "card-grid": render_card_grid,
    "list-slide": render_list_slide,
    "quote-slide": render_quote_slide,
    "prose-slide": render_prose_slide,
    "image-feature": render_image_feature,
    "principle-tiles": render_principle_tiles,
    "catalog-mosaic": render_catalog_mosaic,
    "catalog-featured": render_catalog_featured,
    "scope-iceberg": render_scope_iceberg,
    "concept-canvas": render_concept_canvas,
    "handoff-relay": render_handoff_relay,
    # v0.4 PR 3
    "big-stat": render_big_stat,
    "mic-drop": render_mic_drop,
    "timeline-horizontal": render_timeline_horizontal,
    "phase-stack": render_phase_stack,
    "before-after": render_before_after,
    "versus-split": render_versus_split,
    "bar-chart": render_bar_chart,
    "roster-cards": render_roster_cards,
    # v0.5 — creative agent-authored slides return raw HTML verbatim
    "raw-html": lambda s: s.get("raw_html", ""),
}


def render_slides_html(slides: list[dict]) -> str:
    out: list[str] = []
    for s in slides:
        renderer = RENDERERS.get(s["type"])
        if renderer:
            out.append(renderer(s))
    return "\n".join(out)


# ---------------------------------------------------------------------------
# Document wrap (provenance + CSS + JS)
# ---------------------------------------------------------------------------

def _load_asset(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def wrap_document(*, body: str, source_path: Path, source_sha: str,
                  built_at: str, slide_count: int, style: str) -> str:
    viewport_path, preset_path = _resolve_style_css(style)
    css_parts: list[str] = []
    if viewport_path is not None:
        css_parts.append(
            "/* === viewport-base.css (frontend-slides canonical viewport contract) === */\n"
            + _load_asset(viewport_path)
        )
    if preset_path is not None:
        css_parts.append(
            f"/* === preset: {style} (from {preset_path.parent.parent.name}/{preset_path.parent.name}/{preset_path.name}) === */\n"
            + _load_asset(preset_path)
        )
    v04_path = _v04_component_css()
    if v04_path is not None:
        css_parts.append(
            "/* === v0.4 component library (frontend-slides/components/_v04-components.css) === */\n"
            + _load_asset(v04_path)
        )
    css = "\n\n".join(css_parts)
    js = _load_asset(JS_PATH)
    built_by = getpass.getuser()
    src_rel = source_path.name
    banner = (
        f"<!--\n"
        f"  md-deck v{VERSION} — DO NOT HAND-EDIT\n"
        f"  Source: {src_rel}\n"
        f"  SHA-256: {source_sha}\n"
        f"  Built:  {built_at} by {built_by}\n"
        f"  Update: python .claude/skills/md-deck/scripts/build.py {src_rel}\n"
        f"-->\n"
    )
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
{banner}<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="generator" content="md-deck v{VERSION}">
<meta name="md-deck:source" content="{_esc(src_rel)}">
<meta name="md-deck:source-sha256" content="{source_sha}">
<meta name="md-deck:built-at" content="{built_at}">
<meta name="md-deck:built-by" content="{_esc(built_by)}">
<meta name="md-deck:style" content="{_esc(style)}">
<meta name="md-deck:slide-count" content="{slide_count}">
<title>{_esc(source_path.stem)}</title>
<style>
{css}
</style>
</head>
<body>
{body}
<div class="progress-bar"><div class="progress-fill"></div></div>
<div class="nav-dots"></div>
<div class="keyboard-hint">← → space · ? for provenance</div>
<div class="provenance-modal" hidden>
  <div class="provenance-card">
    <h3>Deck provenance</h3>
    <dl>
      <dt>Source</dt><dd><code>{_esc(src_rel)}</code></dd>
      <dt>SHA-256</dt><dd><code>{source_sha}</code></dd>
      <dt>Built</dt><dd>{built_at}</dd>
      <dt>By</dt><dd>{_esc(built_by)}</dd>
      <dt>Generator</dt><dd>md-deck v{VERSION} · style={_esc(style)}</dd>
      <dt>Slides</dt><dd>{slide_count}</dd>
    </dl>
    <p class="dim">Update by re-running the source-of-truth build:<br>
    <code>python .claude/skills/md-deck/scripts/build.py {_esc(src_rel)}</code></p>
    <button class="provenance-close">Close (Esc)</button>
  </div>
</div>
<script>
{js}
</script>
</body>
</html>
'''


# ---------------------------------------------------------------------------
# Manifest writer
# ---------------------------------------------------------------------------

def write_manifest(*, out_dir: Path, source_path: Path, source_sha: str,
                   built_at: str, style: str, slides: list[dict]) -> Path:
    manifest = {
        "schema": "md-deck/manifest@2",
        "generator": f"md-deck v{VERSION}",
        "source": {
            "path": str(source_path.name),
            "sha256": source_sha,
            "size_bytes": source_path.stat().st_size,
        },
        "build": {
            "at": built_at,
            "by": getpass.getuser(),
            "style": style,
        },
        "slides": [
            {
                "index": i,
                "type": s["type"],
                "title": s.get("title"),
                "section": s.get("section"),
                "anchor": s.get("anchor"),
                "slug": s.get("slug"),
                "source_lines": s.get("source_lines"),
                "source_sha256": s.get("source_sha256"),
            }
            for i, s in enumerate(slides)
        ],
        "components_used": sorted({s["type"] for s in slides}),
    }
    path = out_dir / "manifest.json"
    path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# v0.4 PR 4: 3-candidate selection + candidates.html + picks.json
# ---------------------------------------------------------------------------

# Slide types that DO get variant proposals — section content slides.
# Title / agenda / divider / image-feature / catalog-mosaic / catalog-featured
# are excluded: title and agenda are layout-fixed; dividers are ornamental;
# image-feature is structurally gated; catalog-mosaic / catalog-featured already
# split a single source into multiple slides with their own contract.
_VARIANT_ELIGIBLE = {
    "card-grid", "list-slide", "quote-slide", "prose-slide", "table-slide",
    "image-feature",  # eligible — image + bullets can score timeline / phase-stack
}


def _adapt_slide_to_component(base: dict, component_name: str) -> dict:
    """Adapt a base slide to a target component's expected data shape.

    Most components inherit the base shape directly (title, lead, items,
    bullets, tiles, paragraphs, table, anchor, section). The legacy variant
    builders (_make_principle_tiles, _make_scope_iceberg, _make_concept_canvas,
    _make_handoff_relay, _make_catalog_featured_slide) need to do data
    transformation — call them through. Otherwise pass through with type retag.
    """
    if component_name == "principle-tiles":
        # Needs tiles → add icons and shorten subtitles
        tiles = base.get("tiles") or []
        if not tiles:
            # Convert items/bullets into bold-led tiles
            items = base.get("items") or base.get("bullets") or []
            tiles = []
            for it in items:
                text = it if isinstance(it, str) else " ".join(str(x) for x in it)
                m = re.match(r"^\*\*([^*]+)\*\*\s*[—,.:-]?\s*(.*)$", text)
                if m:
                    tiles.append({"label": m.group(1).strip(), "subtitle": m.group(2).strip()})
                else:
                    lbl, sub = _split_label_sub(text)
                    tiles.append({"label": lbl, "subtitle": sub})
            base = dict(base, tiles=tiles)
        return _make_principle_tiles(base) | {"_base_type": base["type"], "_picked_component": component_name, "anchor": base.get("anchor", "")}
    if component_name == "scope-iceberg":
        out = _make_scope_iceberg(base)
        if out is None:
            # Fallback: synthesize a 2-column scope
            items = base.get("items") or base.get("bullets") or []
            half = max(1, len(items) // 2)
            out = {
                "type": "scope-iceberg", "title": base.get("title", ""), "section": base.get("section"),
                "anchor": base.get("anchor", ""),
                "in_items": [str(i) for i in items[:half]][:4],
                "out_items": [str(i) for i in items[half:]][:4],
            }
        out["_base_type"] = base["type"]
        out["_picked_component"] = component_name
        return out
    if component_name == "concept-canvas":
        out = _make_concept_canvas(base)
        if out is None:
            items = base.get("items") or base.get("bullets") or [base.get("lead", "")]
            out = {
                "type": "concept-canvas", "title": base.get("title", ""), "section": base.get("section"),
                "anchor": base.get("anchor", ""),
                "facets": [str(i)[:60] for i in items[:4]],
            }
        out["_base_type"] = base["type"]
        out["_picked_component"] = component_name
        return out
    if component_name == "handoff-relay":
        out = _make_handoff_relay(base)
        if out is None:
            # Fallback: take items as actor strings
            items = base.get("items") or []
            tiles = base.get("tiles") or []
            actors = [str(it) for it in items] or [t.get("label", "") for t in tiles]
            out = {
                "type": "handoff-relay", "title": base.get("title", ""), "section": base.get("section"),
                "anchor": base.get("anchor", ""), "actors": actors[:6],
            }
        out["_base_type"] = base["type"]
        out["_picked_component"] = component_name
        return out
    if component_name == "catalog-mosaic":
        # Reuse the first emitted mosaic slide for preview purposes
        slides = _make_catalog_mosaic_slides(base) if (base.get("table") or {}).get("rows") else []
        if slides:
            slides[0]["_base_type"] = base["type"]
            slides[0]["_picked_component"] = component_name
            return slides[0]
    if component_name == "catalog-featured":
        if (base.get("table") or {}).get("rows"):
            out = _make_catalog_featured_slide(base)
            out["_base_type"] = base["type"]
            out["_picked_component"] = component_name
            return out

    # Default: pass through with type retag — components that read directly
    # from base shape (card-grid, list-slide, prose-slide, quote-slide,
    # table-slide, big-stat, mic-drop, timeline-horizontal, phase-stack,
    # before-after, versus-split, bar-chart, roster-cards).
    adapted = dict(base)
    adapted["_base_type"] = base["type"]
    adapted["_picked_component"] = component_name
    adapted["type"] = component_name
    return adapted


def propose_candidates(
    base_slide: dict,
    registry: dict[str, dict],
    *,
    top_k: int = 2,
) -> list[tuple[dict, "ComponentScore"]]:
    """Return the top-K (adapted_slide, ComponentScore) pairs for a base slide.

    The first slot is always a no-op variant (the base slide unchanged) so the
    user can pick "the original card-grid" as a candidate. Slots 2 and 3 are
    drawn from the classifier's top picks, excluding the base slide's component.
    """
    from classify import extract_features, score_components, ComponentScore  # local import to keep top clean

    if base_slide.get("type") not in _VARIANT_ELIGIBLE:
        return []

    features = extract_features(base_slide)
    scored = score_components(features, registry, top_k=8, cluster_spread=True)

    # Filter to renderers we actually have wired up
    renderable = {n for n in RENDERERS}
    scored = [s for s in scored if s.name in renderable]

    # Always include the base type as the "safe" candidate at slot 1.
    base_type = base_slide["type"]
    base_meta = registry.get(base_type) or {"cluster": "uncategorized"}
    base_score = ComponentScore(
        name=base_type, cluster=base_meta.get("cluster", "uncategorized"),
        score=0.50, rationale="base classification (md-deck heuristic)", viable=True,
    )

    result: list[tuple[dict, ComponentScore]] = [
        (_adapt_slide_to_component(base_slide, base_type), base_score)
    ]
    seen_clusters = {base_score.cluster}
    seen_names = {base_score.name}

    for cs in scored:
        if len(result) >= top_k:
            break
        if cs.name in seen_names:
            continue
        # Cluster-spread rule: max 2 per cluster
        if list(seen_clusters).count(cs.cluster) >= 2:
            continue
        result.append((_adapt_slide_to_component(base_slide, cs.name), cs))
        seen_names.add(cs.name)
        seen_clusters.add(cs.cluster)

    # Top up with raw-score order if cluster-spread left us short
    if len(result) < top_k:
        for cs in scored:
            if len(result) >= top_k:
                break
            if cs.name in seen_names:
                continue
            result.append((_adapt_slide_to_component(base_slide, cs.name), cs))
            seen_names.add(cs.name)

    return result


# ---------------------------------------------------------------------------
# picks.json — assets-folder persistence (open question 5, revised 2026-05-02:
# picks.json lives inside the deck's assets folder alongside index.html /
# candidates.html / manifest.json, not next to the source markdown).
# ---------------------------------------------------------------------------

def _picks_path(out_dir: Path) -> Path:
    """Path to picks.json inside the deck's assets folder."""
    return out_dir / "picks.json"


def load_picks(out_dir: Path) -> dict[str, list[dict]]:
    """Return {anchor: [pick_entry, ...]} where each entry has {component, html?, rolled_at}.

    Schema v3 (current): `picks[anchor].selected = [pick_entry, ...]` — a list,
    so the user can pick multiple slides for one section. The build emits one
    final slide per pick in selection order.

    Schema v2 (legacy): `picks[anchor] = pick_entry` — a single dict. Auto-
    migrated to a one-element list.
    """
    p = _picks_path(out_dir)
    if not p.exists():
        return {}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    picks_block = data.get("picks") or {}
    out: dict[str, list[dict]] = {}
    for anchor, entry in picks_block.items():
        if not entry:
            continue
        # v3 — entry is a dict with `selected: [...]`
        if isinstance(entry, dict) and isinstance(entry.get("selected"), list):
            out[anchor] = [e for e in entry["selected"] if e.get("component")]
        # v2 legacy — entry is a single pick dict
        elif isinstance(entry, dict) and entry.get("component"):
            out[anchor] = [entry]
        # extreme legacy — entry is a flat list
        elif isinstance(entry, list):
            out[anchor] = [e for e in entry if isinstance(e, dict) and e.get("component")]
    return {a: picks for a, picks in out.items() if picks}


def _slice_source_markdown(source_text: str, anchor: str) -> str:
    """Extract the source markdown lines covered by a `data-source-anchor`
    string like "L13-L25" or "L116" so the creative agent sees the original
    section text. Falls back to the whole source if the anchor can't be parsed.
    """
    m = re.match(r"L(\d+)(?:-L(\d+))?", str(anchor or ""))
    if not m:
        return source_text
    lo = int(m.group(1))
    hi = int(m.group(2)) if m.group(2) else lo
    lines = source_text.splitlines()
    return "\n".join(lines[lo - 1: hi])


def expand_with_variants(slides: list[dict]) -> list[dict]:
    out: list[dict] = []
    for s in slides:
        out.append(s)
        for v in _inject_variants(s):
            # Variant builders only carry section/title/anchor — propagate the
            # slug-era identity fields from the parent so the manifest covers
            # variant slides too.
            for k in ("slug", "source_lines", "source_sha256"):
                if s.get(k) and not v.get(k):
                    v[k] = s[k]
            out.append(v)
    return out


# Per-slide-type density limits (frontend-slides density-limits table).
# When a slide exceeds the limit, it is split into N continuation slides
# instead of relying on shrinking type to fit. Tables are intentionally
# absent — table density is owned by the catalog-mosaic / table-density
# path, which paginates rows instead of shrinking columns.
DENSITY_LIMITS = {
    "card-grid": 6,   # 2x3 / 3x2 max
    "list-slide": 6,  # 4-6 bullets sweet spot
}


def _split_dense_slide(slide: dict) -> list[dict]:
    """If `slide` exceeds its density limit, split into N continuation slides.

    Continuation slides carry "(cont.)" suffix in title; numbering chrome
    auto-renumbers from DOM position via deck-runtime.js. The original
    `data-source-anchor` is preserved on every part for drift detection.
    """
    stype = slide.get("type")
    limit = DENSITY_LIMITS.get(stype)
    if limit is None:
        return [slide]
    if stype == "card-grid":
        tiles = slide.get("tiles") or []
        if len(tiles) <= limit:
            return [slide]
        parts: list[dict] = []
        for chunk_i, start in enumerate(range(0, len(tiles), limit)):
            part = dict(slide)
            part["tiles"] = tiles[start:start + limit]
            if chunk_i > 0:
                part["title"] = f"{slide['title']} (cont.)"
                part["lead"] = ""  # lead only on first part
                # Continuation parts need their own slug — the section/picks
                # machinery keys sections by slug, and a shared slug makes the
                # last part overwrite the head part (head slide silently
                # dropped, (cont.) part emitted twice). Head keeps the minted
                # slug so existing picks.json entries stay bound to it.
                if slide.get("slug"):
                    part["slug"] = f"{slide['slug']}--cont{chunk_i + 1}"
            parts.append(part)
        return parts
    if stype == "list-slide":
        items = slide.get("items") or []
        if len(items) <= limit:
            return [slide]
        parts = []
        for chunk_i, start in enumerate(range(0, len(items), limit)):
            part = dict(slide)
            part["items"] = items[start:start + limit]
            if chunk_i > 0:
                part["title"] = f"{slide['title']} (cont.)"
                part["lead"] = ""
                # Same slug-uniqueness requirement as the card-grid branch.
                if slide.get("slug"):
                    part["slug"] = f"{slide['slug']}--cont{chunk_i + 1}"
            parts.append(part)
        return parts
    return [slide]


def apply_density_splits(slides: list[dict]) -> list[dict]:
    """Pre-pass: enforce per-slide-type density limits by splitting, not shrinking."""
    out: list[dict] = []
    for s in slides:
        out.extend(_split_dense_slide(s))
    return out


def _emit_candidates_html(
    section_candidates: list[dict],
    *,
    source_path: Path,
    source_sha: str,
    built_at: str,
    style: str,
) -> str:
    """Render the candidates.html review page — every variant-eligible section
    shown three-up with its scoring rationale. Picks persist via a download flow
    that writes picks.json into the deck's assets folder.
    """
    parts: list[str] = []
    parts.append('<header class="candidates-header">')
    parts.append('<h1>md-deck candidates · review &amp; pick</h1>')
    parts.append(
        '<p>Multiple visual treatments per variant-eligible section — 2 templates + 2 agents by default. '
        '<strong>Pick toggles independently</strong>: click Pick on multiple cards in a section and the deck '
        'will emit one slide per picked card (in selection order). Save into the deck assets folder as '
        '<code>picks.json</code> (same directory as <code>index.html</code> / <code>candidates.html</code>) '
        'when you are done. Re-run the build to lock the picks into <code>index.html</code>.</p>'
        f'<p style="margin-top:0.6rem;font-family:var(--font-mono,monospace);font-size:0.8em;color:var(--text-muted);">'
        f'source: {_esc(source_path.name)} · sha256: {source_sha[:16]}… · built: {built_at}'
        '</p>'
    )
    parts.append('</header>')

    for section in section_candidates:
        # `anchor` here is the slug — the var name is kept for parity with the
        # baked JS, which treats this as an opaque pick key.
        anchor = section["slug"]
        title = section["title"] or "(untitled)"
        parts.append(f'<div class="candidate-section" data-anchor="{_esc(anchor)}">')
        parts.append(f'<h2>{_esc(title)} <span class="section-pick-count" style="font-size: 0.55em; color: var(--card-orange); font-family: var(--font-mono, monospace); letter-spacing: 0.08em; text-transform: uppercase; margin-left: 0.8em;"></span></h2>')
        parts.append(f'<div class="anchor-tag">§{_esc(section.get("section") or "?")} · {_esc(anchor)}</div>')
        parts.append('<div class="candidate-grid">')
        for i, cand in enumerate(section["candidates"]):
            letter = chr(ord("A") + i)
            slide_html = cand["html"]
            kind = cand.get("kind", "template")
            agent_badge = ' <span style="color: var(--card-amber, #ffb400); font-weight: 700;">✨ AGENT</span>' if kind == "creative" else ""
            parts.append(
                f'<div class="candidate-card" data-component="{_esc(cand["component"])}" data-kind="{_esc(kind)}">'
                f'<div class="candidate-header">'
                f'<span class="pick-letter">{letter}</span>'
                f'<span class="pick-name">{_esc(cand["component"])}{agent_badge}</span>'
                f'<span class="pick-score">score {cand["score"]:.2f}</span>'
                f'</div>'
                f'<div class="candidate-preview">{slide_html}</div>'
                f'<div class="candidate-rationale">{_esc(cand["rationale"])} · cluster: {_esc(cand["cluster"])}</div>'
                f'<div class="candidate-actions"><button onclick="pick(this, \'{_esc(anchor)}\', \'{_esc(cand["component"])}\')">Pick {letter}</button></div>'
                f'</div>'
            )
        parts.append('</div></div>')

    body = "\n".join(parts)
    chooser_js = '''
<script>
// PICKS shape (v3): { <anchor>: { selected: [ {component, html?, rolled_at}, ... ] } }
// Each card toggles independently — you can pick 1, 2, 3 or all 4 candidates per
// section. The build emits one final slide per pick in selection order. Pick
// order is preserved (the array is append/remove rather than re-sorted).
const PICKS = JSON.parse(localStorage.getItem('md-deck-picks-' + DECK_KEY) || '{}');

// Migrate v2 (single pick dict) → v3 (selected list)
Object.entries(PICKS).forEach(([anchor, entry]) => {
    if (entry && !entry.selected && entry.component) {
        PICKS[anchor] = { selected: [entry] };
    } else if (entry && !entry.selected) {
        PICKS[anchor] = { selected: [] };
    }
});

function pick(btn, anchor, component) {
    const card = btn.closest('.candidate-card');
    const isCreative = card && card.dataset.kind === 'creative';
    if (!PICKS[anchor]) PICKS[anchor] = { selected: [] };
    const list = PICKS[anchor].selected;
    const existingIdx = list.findIndex(e => e.component === component);

    if (existingIdx >= 0) {
        // Toggle off — un-pick
        list.splice(existingIdx, 1);
        card.classList.remove('picked');
    } else {
        // Add to selection
        const entry = { component: component, rolled_at: new Date().toISOString() };
        if (isCreative) {
            const previewWrap = card.querySelector('.candidate-preview');
            if (previewWrap) entry.html = previewWrap.innerHTML;
        }
        list.push(entry);
        card.classList.add('picked');
    }

    localStorage.setItem('md-deck-picks-' + DECK_KEY, JSON.stringify(PICKS));
    updateSummary();
    updateSectionCount(anchor);
}

function updateSectionCount(anchor) {
    const sec = document.querySelector(`.candidate-section[data-anchor="${anchor}"]`);
    if (!sec) return;
    const tag = sec.querySelector('.section-pick-count');
    const n = ((PICKS[anchor] || {}).selected || []).length;
    if (tag) tag.textContent = n === 0 ? '' : `${n} picked`;
}

function updateSummary() {
    const summary = document.getElementById('picks-summary');
    const totalPicks = Object.values(PICKS).reduce((sum, e) => sum + ((e.selected || []).length), 0);
    const sectionsWithPicks = Object.values(PICKS).filter(e => (e.selected || []).length > 0).length;
    summary.textContent = `${totalPicks} pick${totalPicks!==1?'s':''} across ${sectionsWithPicks} section${sectionsWithPicks!==1?'s':''} · download picks.json`;
}

function downloadPicks() {
    const out = {
        schema: 'md-deck/picks@3',
        source: SOURCE_NAME,
        source_sha256: SOURCE_SHA,
        picks: PICKS,
    };
    const blob = new Blob([JSON.stringify(out, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'picks.json';
    a.click();
    URL.revokeObjectURL(url);
}

// Restore picked state from localStorage on load
document.addEventListener('DOMContentLoaded', () => {
    Object.entries(PICKS).forEach(([anchor, entry]) => {
        const sec = document.querySelector(`.candidate-section[data-anchor="${anchor}"]`);
        if (!sec) return;
        ((entry.selected) || []).forEach(picked => {
            const card = sec.querySelector(`.candidate-card[data-component="${picked.component}"]`);
            if (card) card.classList.add('picked');
        });
        updateSectionCount(anchor);
    });
    updateSummary();
});
</script>
'''
    return body + (
        f'<div id="picks-summary" class="picks-summary" onclick="downloadPicks()">0 picks · download picks.json</div>'
        f'<script>'
        f'const DECK_KEY = "{_esc(source_path.stem)}";'
        f'const SOURCE_NAME = "{_esc(source_path.name)}";'
        f'const SOURCE_STEM = "{_esc(source_path.stem)}";'
        f'const SOURCE_SHA = "{source_sha}";'
        f'</script>'
        + chooser_js
    )


def _cache_dir(out_dir: Path) -> Path:
    """Per-deck successful-creative cache root. Committed (unlike `.debug/`)."""
    return out_dir / ".creative-cache"


_CACHE_HEADER_RE = re.compile(
    r"<!--\s*md-deck/cache@1\s+(.*?)\s*-->",
    re.DOTALL,
)


def _parse_cache_header(text: str) -> tuple[dict, str] | None:
    """Parse `<!-- md-deck/cache@1 k=v k=v -->` header → (meta, body) or None.

    Body is the HTML after the header (and a single newline). Values are bare
    tokens — no quoting, no equals signs, no whitespace inside values.
    """
    m = _CACHE_HEADER_RE.match(text)
    if not m:
        return None
    meta: dict = {}
    for tok in m.group(1).split():
        if "=" in tok:
            k, _, v = tok.partition("=")
            meta[k] = v
    body = text[m.end():].lstrip("\n")
    return meta, body


_CACHE_SLUG_BYTE_CAP = 180


def _cache_file_path(out_dir: Path, slug: str, sha7: str, slot: str) -> Path:
    name_slug = slug
    if len(name_slug.encode("utf-8")) > _CACHE_SLUG_BYTE_CAP:
        digest = hashlib.sha1(slug.encode("utf-8")).hexdigest()[:8]
        prefix = slug.encode("utf-8")[: _CACHE_SLUG_BYTE_CAP - 9].decode("utf-8", errors="ignore")
        name_slug = f"{prefix.rstrip('-')}-{digest}"
    return _cache_dir(out_dir) / f"{name_slug}__{sha7}-{slot}.html"


def _save_creative_cache(out_dir: Path, source_sha: str, source_name: str, cache: dict) -> None:
    """Persist creative-slot HTML cache.

    On disk: one file per (slug, sha, slot) at `.creative-cache/<slug>__<sha7>-<slot>.html`.
    Each file carries a `<!-- md-deck/cache@1 ... -->` header naming the source
    SHA, personality, and generation timestamp; the body is the agent's HTML.

    Picks.json is rewritten alongside (schema bumped to `md-deck/picks@3`) and
    has its legacy `creative_cache` block stripped — cache lives in files now.
    """
    cache_dir = _cache_dir(out_dir)
    cache_dir.mkdir(exist_ok=True)

    # Track files we're writing this run; sweep stale `<slug>__<sha7>-<slot>.html`
    # entries for the same (slug, slot) at different SHAs lives in `--sweep-cache`
    # (sub-task 1.11), not here.
    written: set[Path] = set()
    for slug, slot_map in (cache or {}).items():
        if not slug or not isinstance(slot_map, dict):
            continue
        for slot, entry in slot_map.items():
            if not isinstance(entry, dict):
                continue
            html_frag = entry.get("html")
            entry_sha = entry.get("source_sha")
            if not html_frag or not entry_sha:
                continue
            full_sha = str(entry_sha)
            sha7 = full_sha[:7]
            personality = str(entry.get("personality") or "")
            generated_at = str(entry.get("generated_at") or "")
            # `source_sha` carries the full digest (load-bearing for staleness);
            # `sha7` is mirrored in the filename for human-readable listing.
            header = (
                f"<!-- md-deck/cache@1 slug={slug} slot={slot} "
                f"source_sha={full_sha} personality={personality} "
                f"generated_at={generated_at} -->"
            )
            path = _cache_file_path(out_dir, slug, sha7, slot)
            path.write_text(header + "\n" + html_frag, encoding="utf-8")
            written.add(path)

    # Rewrite picks.json: bump schema, strip creative_cache block.
    p = _picks_path(out_dir)
    if p.exists():
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            data = {}
    else:
        data = {}
    data["schema"] = "md-deck/picks@3"
    data["source"] = source_name
    data["source_sha256"] = source_sha
    data.setdefault("picks", {})
    data.pop("creative_cache", None)
    p.write_text(json.dumps(data, indent=2), encoding="utf-8")


def sweep_creative_cache(out_dir: Path, current_slugs: set[str],
                          current_sha: str | dict[str, str],
                          *, dry_run: bool = False) -> tuple[list[Path], list[Path]]:
    """Remove orphan + stale-SHA files from `.creative-cache/`.

    A cache file is **orphan** when its slug is not in `current_slugs` (the
    section was renamed or deleted in the source). A cache file is **stale**
    when its slug is current but its `source_sha` header does not match the
    expected SHA. Both go.

    `current_sha` accepts two shapes for compatibility with how the cache is
    keyed: a `dict[slug, source_sha256]` (preferred — validates each entry
    against its own section's content SHA, which is what `_save_creative_cache`
    writes today), or a single deck-wide SHA string (legacy fallback used by
    older deck folders that stamped every entry with the deck-wide SHA).

    Returns (orphan_paths, stale_paths) — the files that were removed (or
    would be removed if `dry_run=True`).
    """
    cache_dir = _cache_dir(out_dir)
    if not cache_dir.is_dir():
        return [], []
    orphan: list[Path] = []
    stale: list[Path] = []
    for path in cache_dir.glob("*.html"):
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        parsed = _parse_cache_header(text)
        if not parsed:
            # Unparseable header — treat as orphan; the file is unreadable
            # by the cache layer regardless.
            orphan.append(path)
            continue
        meta, _body = parsed
        slug = meta.get("slug")
        sha = meta.get("source_sha", "")
        if not slug or slug not in current_slugs:
            orphan.append(path)
            continue
        if isinstance(current_sha, dict):
            expected = current_sha.get(slug, "")
        else:
            expected = current_sha
        if sha != expected:
            stale.append(path)
    if not dry_run:
        for p in (*orphan, *stale):
            try:
                p.unlink()
            except OSError:
                pass
    return orphan, stale


def _write_deck_readme(out_dir: Path, source_path: Path, *, force: bool = False) -> bool:
    """Auto-generate `assets/<slug>/README.md` so every deck folder ships
    with the project-required README. Idempotent — does not overwrite an
    existing README unless `force=True`.

    Returns True when a file was written, False when one already existed
    (so the caller can leave user-authored notes in place).
    """
    readme = out_dir / "README.md"
    if readme.exists() and not force:
        return False
    slug = out_dir.name
    src_rel: str
    try:
        src_rel = str(source_path.resolve().relative_to(out_dir.resolve().parent.parent))
    except ValueError:
        src_rel = source_path.name
    body = f"""# {slug} — md-deck output

Auto-generated deck folder. Source: `{src_rel}`.

## Structure

| File | Owner | Purpose |
|---|---|---|
| `index.html` | md-deck | Final single-file slide deck — open in a browser. |
| `candidates.html` | md-deck | 4-up review UI; emitted on first build or with `--review`. |
| `picks.json` | user (curated) | Per-section pick selection. Keyed by section **slug**. |
| `distillation.yml` | md-deck | Deck-wide brief + per-section dossiers. Sections keyed by slug. |
| `manifest.json` | md-deck | Build provenance (slug, source_lines, source_sha256 per slide). |
| `.creative-cache/` | md-deck (committed) | Per-(slug, sha, slot) successful agent HTML. Survives across builds; stale entries swept by `--sweep-cache`. |
| `.debug/` | md-deck (gitignored) | Failure dumps from the creative fan-out. Safe to delete. |

## Iterate

- Refresh one section's creatives only:
  `python3 .claude/skills/md-deck/scripts/build.py {src_rel} --creative --re-roll-creative <slug>`
- Re-distill + re-roll one section in one step:
  `... --re-roll-section <slug>`
- Retire orphan / stale cache:
  `... --sweep-cache`
- Forensic / cache-bypass:
  `... --creative --no-cache`

## Identity model

Sections are identified by **slug** (derived from `### N.M Heading`),
not by source line range. Cache validity is keyed on the section's
content-SHA. Inserting / deleting unrelated sections does not invalidate
this section's cache. See task ben/163 for design notes.
"""
    out_dir.mkdir(parents=True, exist_ok=True)
    readme.write_text(body, encoding="utf-8")
    return True


def _load_creative_cache(out_dir: Path) -> dict:
    """Load the creative-slot HTML cache.

    Walks `.creative-cache/<slug>__<sha7>-<slot>.html` and rebuilds the dict
    shape `{slug: {slot: {html, source_sha, personality, generated_at}}}`.
    Falls back to the legacy `picks.json:creative_cache` block when no cache
    files are present yet — one-time migration window so picks/caches built
    under the previous schema continue to work without manual intervention.
    """
    out: dict[str, dict] = {}
    cache_dir = _cache_dir(out_dir)
    if cache_dir.is_dir():
        for path in cache_dir.glob("*.html"):
            try:
                text = path.read_text(encoding="utf-8")
            except OSError:
                continue
            parsed = _parse_cache_header(text)
            if not parsed:
                continue
            meta, body = parsed
            slug = meta.get("slug")
            slot = meta.get("slot")
            if not slug or not slot:
                continue
            out.setdefault(slug, {})[slot] = {
                "html": body,
                "source_sha": meta.get("source_sha", ""),
                "personality": meta.get("personality", ""),
                "generated_at": meta.get("generated_at", ""),
            }
        if out:
            return out

    # Legacy fallback — picks@2 stored cache inside picks.json.
    p = _picks_path(out_dir)
    if not p.exists():
        return {}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return data.get("creative_cache") or {}


def build(
    source_path: Path,
    output_dir: Path | None,
    style: str,
    *,
    review: bool = False,
    creative_mode: bool = False,
    creative_section: str | None = None,
    re_roll_creative: list[str] | None = None,
    re_roll_distillation: bool = False,
    creative_parallelism: int = 5,
    template_slots: int = 1,
    agent_slots: int = 3,
    disable_cache: bool = False,
    auto_re_roll_on_lint: bool = False,
) -> dict:
    text = source_path.read_text(encoding="utf-8")
    sha = hashlib.sha256(text.encode()).hexdigest()
    built_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    blocks = parse_markdown(text)
    base_slides = synthesize_slides(blocks, source_path, source_text=text)
    base_slides = apply_density_splits(base_slides)

    # Resolve the output directory first — picks.json now lives inside it
    # (revised location 2026-05-02: assets folder, not source-adjacent).
    slug = _slugify(source_path.stem)
    if output_dir is None:
        cur = source_path.resolve().parent
        root = cur
        while root != root.parent:
            if (root / ".claude").exists() or (root / "project.yml").exists():
                break
            root = root.parent
        out_dir = root / "assets" / slug
    else:
        out_dir = output_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    # v0.4 PR 4 — load picks from the assets folder + load component registry
    picks = load_picks(out_dir)
    registry = load_component_registry()
    # ben/163 1.12 — `--no-cache` forensic bypass: load nothing, persist nothing.
    # Distinct from `--re-roll-creative` (which still persists fresh cache).
    if disable_cache and creative_mode:
        creative_cache = {}
    else:
        creative_cache = _load_creative_cache(out_dir) if creative_mode else {}
    re_roll_set = set(re_roll_creative or [])

    # ben/163 1.13 — drop a per-deck README on first build so every assets/<slug>/
    # folder satisfies the project "every folder has a README" rule. Does not
    # overwrite user-authored notes once they exist.
    _write_deck_readme(out_dir, source_path)

    # ben/163 — auto-migrate legacy `L<lo>-L<hi>` keys in picks + creative_cache
    # to slug keys. Keys are remapped via the source_lines → slug index built
    # from this build's slides; un-resolvable legacy keys pass through (orphan
    # sweep retires them in sub-task 1.11). Re-saving picks.json / cache after
    # the build persists the migration.
    legacy_to_slug: dict[str, str] = {}
    for s in base_slides:
        sl = s.get("source_lines")
        sg = s.get("slug")
        if sl and sg and sl not in legacy_to_slug:
            legacy_to_slug[sl] = sg

    def _remap_legacy_keys(d: dict) -> tuple[dict, int]:
        out: dict = {}
        migrated = 0
        for k, v in d.items():
            if k in legacy_to_slug:
                out[legacy_to_slug[k]] = v
                migrated += 1
            else:
                out[k] = v
        return out, migrated

    picks, picks_migrated = _remap_legacy_keys(picks)
    creative_cache, cache_migrated = _remap_legacy_keys(creative_cache)
    if picks_migrated or cache_migrated:
        print(
            f"  · auto-migrated legacy line-range keys: "
            f"{picks_migrated} picks, {cache_migrated} cache entries → slug",
            file=sys.stderr,
        )

    # Re-roll set may carry either form; normalize to slugs so the comparison
    # in the loop works regardless of how the user typed the flag.
    re_roll_set = {legacy_to_slug.get(k, k) for k in re_roll_set}

    # v0.5 — when --creative is on, run the deck-wide distillation pass first.
    # Cached at out_dir/distillation.yml, source-SHA-tagged. Slot briefs ingest
    # both the deck-wide intelligence and the per-section dossier.
    distillation: dict = {}
    if creative_mode:
        from distill import distill_source
        # ben/163 1.8 — build the slug_index from synthesized slides so distill.py
        # can rewrite per-section identity to slug form on load. Each entry maps
        # the agent-emitted `L<lo>-L<hi>` legacy anchor → its slug + content-SHA.
        slug_index_for_distill: dict[str, dict] = {}
        for s in base_slides:
            sl = s.get("source_lines")
            sg = s.get("slug")
            if not sl or not sg or sl in slug_index_for_distill:
                continue
            slug_index_for_distill[sl] = {
                "slug": sg,
                "source_sha256": s.get("source_sha256", ""),
                "title": s.get("title", ""),
            }
        try:
            distillation = distill_source(
                source_path, out_dir, source_sha=sha,
                force=bool(re_roll_distillation),
                slug_index=slug_index_for_distill,
            )
        except Exception as e:
            print(f"  ⚠ distillation failed: {e}; creative slots will fall back to raw markdown only", file=sys.stderr)
            distillation = {}

    # For each base slide, propose 2 template candidates + (optionally) 2
    # creative agent-authored candidates. Pick the locked component if a pick
    # exists for the anchor; otherwise pick the top-scoring template.
    section_candidates: list[dict] = []  # for candidates.html
    final_slides: list[dict] = []
    slide_plan: list[dict] = []  # ordered: {"kind": "passthrough"|"chosen", "base"?, "anchor"?}
    components_used: set[str] = set()
    creative_calls = 0
    creative_pending: list[dict] = []   # tasks for parallel fan-out
    base_slide_by_anchor: dict[str, dict] = {}   # for finalize-pass lookups
    cands_by_anchor: dict[str, list] = {}

    # Slot-personality plan derived from --candidate-mix N,M
    # M ∈ {0..4}; mapping creative-c → bold-metaphor, creative-d →
    # structured-diagram, creative-e → free-creative (first wild card),
    # creative-f → free-creative (second wild card; independent roll).
    _slot_plan_creative = [
        ("creative-c", "bold-metaphor"),
        ("creative-d", "structured-diagram"),
        ("creative-e", "free-creative"),
        ("creative-f", "free-creative"),
    ][:max(0, min(4, agent_slots))]

    for base in base_slides:
        cands = propose_candidates(base, registry, top_k=max(1, template_slots))
        if not cands:
            slide_plan.append({"kind": "passthrough", "base": base})
            continue
        slug = _slide_slug(base)
        # Eligible — record the position; chosen slide materializes after fan-out.
        slide_plan.append({"kind": "chosen", "slug": slug})

        pick_entries = picks.get(slug) or []  # list of {component, html?}
        # First pick's component drives the candidate's "is locked" state
        # (used to highlight in candidates.html); the full list drives how
        # many final slides this section emits.
        locked_name = pick_entries[0].get("component") if pick_entries else None
        locked_html = pick_entries[0].get("html") if pick_entries else None
        locked_set = {p.get("component") for p in pick_entries if p.get("component")}

        # Render the two template candidates' HTML
        template_rendered: list[dict] = []
        for adapted, cs in cands:
            try:
                renderer = RENDERERS.get(adapted["type"], render_prose_slide)
                template_rendered.append({
                    "component": cs.name,
                    "score": cs.score,
                    "rationale": cs.rationale,
                    "cluster": cs.cluster,
                    "kind": "template",
                    "html": renderer(adapted),
                })
            except Exception as e:
                template_rendered.append({
                    "component": cs.name,
                    "score": cs.score,
                    "rationale": f"render failed: {e}",
                    "cluster": cs.cluster,
                    "kind": "template",
                    "html": f'<section class="slide"><div class="slide-content"><h2>render failed</h2><p>{_esc(str(e))}</p></div></section>',
                })

        # Reuse cached creative slots inline; queue uncached ones for parallel
        # fan-out below. We need template_rendered for ref_a/ref_b in the brief,
        # so cached entries materialize here and pending entries are placeholders.
        creative_rendered: list[dict] = []
        # `creative_section` may be either slug or legacy line-range; auto-migrate.
        target_section = legacy_to_slug.get(creative_section, creative_section) if creative_section else None
        if creative_mode and (target_section is None or target_section == slug):
            section_cache = creative_cache.get(slug) or {}
            # ben/166 — cache is keyed on the per-section content SHA. The
            # deck-wide `sha` was the wrong validity key (it changes whenever
            # any line in the source moves, invalidating sections that didn't
            # actually change). Section-level SHA matches `_save_creative_cache`
            # and the seeded migration.
            section_sha = base.get("source_sha256", sha)
            for slot, personality in _slot_plan_creative:
                cached = section_cache.get(slot) or {}
                cached_html = cached.get("html")
                stale = cached.get("source_sha") != section_sha
                if cached_html and not stale and slug not in re_roll_set:
                    creative_rendered.append({
                        "component": slot,
                        "score": 0.95 if slot == "creative-c" else 0.92,
                        "rationale": f"agent-authored ({personality}) · cached",
                        "cluster": "creative",
                        "kind": "creative",
                        "html": cached_html,
                    })
                else:
                    # Queue this slot for parallel generation. The placeholder
                    # carries the metadata needed to fill in the html later.
                    # ben/167 v2 — when this is a manual `--re-roll-creative
                    # <slug>` and a previous cached entry for this (slug, slot)
                    # exists, attach previous HTML + lint critique so the agent
                    # iterates against feedback rather than rolling blind.
                    prev_html_for_iter = ""
                    prev_critique_for_iter = ""
                    if slug in re_roll_set:
                        prev_entry = (creative_cache.get(slug) or {}).get(slot) or {}
                        prev_html_candidate = prev_entry.get("html") or ""
                        if prev_html_candidate:
                            try:
                                from importlib.util import spec_from_file_location, module_from_spec
                                lint_path = Path(__file__).resolve().parent / "lint-creative.py"
                                spec = spec_from_file_location("lint_creative", lint_path)
                                lc = module_from_spec(spec); spec.loader.exec_module(lc)  # type: ignore
                                # Synthesize a "single-file" lint by writing a temp file
                                # is overkill — just call the per-file linter directly.
                                import tempfile
                                with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as tf:
                                    tf.write(prev_html_candidate); tmp_path = Path(tf.name)
                                prev_warnings = lc.lint_file(tmp_path)
                                tmp_path.unlink(missing_ok=True)
                                if prev_warnings:
                                    prev_html_for_iter = prev_html_candidate
                                    prev_critique_for_iter = lc.format_critique(prev_warnings)
                            except Exception:
                                pass
                    creative_pending.append({
                        "slug": slug,
                        "source_lines": base.get("source_lines", ""),
                        "section_sha": section_sha,
                        "slot": slot,
                        "personality": personality,
                        "section_title": base.get("title", ""),
                        "section_number": base.get("section"),
                        "ref_a": template_rendered[0]["html"] if template_rendered else "",
                        "ref_b": template_rendered[1]["html"] if len(template_rendered) > 1 else "",
                        "previous_html": prev_html_for_iter,
                        "previous_critique": prev_critique_for_iter,
                        "pass": 1,  # iteration counter; auto-re-roll bumps to 2
                    })
                    creative_rendered.append({
                        "component": slot,
                        "score": 0.95 if slot == "creative-c" else 0.92,
                        "rationale": f"agent-authored ({personality}) · pending",
                        "cluster": "creative",
                        "kind": "creative",
                        "html": "",  # filled in after parallel fan-out
                        "_pending": True,
                    })
            creative_cache[slug] = section_cache

        all_candidates = template_rendered + creative_rendered

        # Stash for the finalize-pass below. Final chosen-slide computation
        # happens AFTER the parallel creative fan-out so pending HTML is filled.
        section_candidates.append({
            "slug": slug,
            "section": base.get("section"),
            "title": base.get("title", ""),
            "candidates": all_candidates,
            "_locked_name": locked_name,
            "_locked_html": locked_html,
            "_pick_entries": pick_entries,  # list — emit one slide per entry
        })
        base_slide_by_anchor[slug] = base
        cands_by_anchor[slug] = cands

    # ── Parallel fan-out: generate all pending creative slots concurrently ──
    if creative_pending:
        import threading
        from concurrent.futures import ThreadPoolExecutor, as_completed
        from creative import generate_creative_slide
        from distill import deck_brief_block, section_brief_block, section_dossier

        deck_block = deck_brief_block(distillation)
        max_workers = max(1, min(creative_parallelism, len(creative_pending)))
        cache_lock = threading.Lock()
        print(
            f"  · creative fan-out: {len(creative_pending)} agent calls × parallelism={max_workers}"
            f" (~{15 * (len(creative_pending) // max_workers + 1)}s estimated)",
            file=sys.stderr,
        )

        def _generate(task: dict) -> tuple[dict, str | None, str]:
            # Slice on source_lines (still `L<lo>-L<hi>`); slug is for identity,
            # not for line lookup.
            section_md = _slice_source_markdown(text, task["source_lines"])
            dossier = section_dossier(distillation, task["slug"])
            section_block = section_brief_block(dossier)
            try:
                html_frag, raw = generate_creative_slide(
                    section_markdown=section_md,
                    section_title=task["section_title"],
                    section_anchor=task["slug"],
                    section_number=task["section_number"],
                    slot_personality=task["personality"],
                    reference_html_a=task["ref_a"],
                    reference_html_b=task["ref_b"],
                    deck_brief=deck_block,
                    section_brief=section_block,
                    previous_html=task.get("previous_html", ""),
                    previous_critique=task.get("previous_critique", ""),
                )
                return task, html_frag, raw
            except Exception as e:
                return task, None, f"(exception: {e})"

        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            futures = [pool.submit(_generate, t) for t in creative_pending]
            for fut in as_completed(futures):
                task, html_frag, raw = fut.result()
                slug = task["slug"]
                slot = task["slot"]
                personality = task["personality"]
                creative_calls += 1
                # Thread-safe read-modify-write on creative_cache. Without the
                # lock, two threads writing slots for the same section (or even
                # different sections via dict-rehash races) could clobber the
                # other's entry, leading to a partially-populated picks.json
                # at the end of the run.
                with cache_lock:
                    section_cache = creative_cache.get(slug) or {}
                    if html_frag:
                        section_cache[slot] = {
                            "html": html_frag,
                            "personality": personality,
                            # ben/166 — stamp with per-section content SHA, not
                            # deck-wide. Matches the cache validity check at
                            # load time (line ~2891) and the seeded migration.
                            "source_sha": task.get("section_sha", sha),
                            "generated_at": built_at,
                        }
                    creative_cache[slug] = section_cache
                if html_frag:
                    print(f"    ✓ {slot} for {slug} ({personality})", file=sys.stderr)
                else:
                    # Failure dump → assets/<deck>/.debug/ (gitignored). Filename
                    # keys on slug + slot; sweep on next build per ben/163.
                    debug_dir = out_dir / ".debug"
                    debug_dir.mkdir(exist_ok=True)
                    debug_path = debug_dir / f"{slug}-{slot}.txt"
                    debug_path.write_text(raw or "(empty response)", encoding="utf-8")
                    print(f"    ⚠ {slot} for {slug} ({personality}) — extraction failed; raw saved to {debug_path.relative_to(out_dir)}", file=sys.stderr)

                # Splice the generated html into the placeholder candidate card
                for sec in section_candidates:
                    if sec["slug"] != slug:
                        continue
                    for c in sec["candidates"]:
                        if c.get("component") == slot and c.get("_pending"):
                            c["html"] = html_frag or ""
                            c["rationale"] = (
                                f"agent-authored ({personality})"
                                if html_frag else
                                f"agent-authored ({personality}) · extraction failed"
                            )
                            c.pop("_pending", None)
                            if not html_frag:
                                # Drop the score so a working candidate wins
                                c["score"] = 0.0

        # ben/167 v2 — auto-re-roll-on-lint pass.
        # After the initial fan-out, lint each newly-rolled slot's HTML; for any
        # whose weighted score ≥ threshold AND whose pass count is still 1,
        # queue a second pass with previous HTML + critique attached. Hard cap
        # at 2 passes total per (slug, slot). Off by default — opt-in via
        # --auto-re-roll-on-lint.
        if auto_re_roll_on_lint:
            try:
                from importlib.util import spec_from_file_location, module_from_spec
                lint_path = Path(__file__).resolve().parent / "lint-creative.py"
                spec = spec_from_file_location("lint_creative", lint_path)
                lc = module_from_spec(spec); spec.loader.exec_module(lc)  # type: ignore
                import tempfile
                second_pass: list[dict] = []
                for t in creative_pending:
                    if t.get("pass", 1) >= 2:
                        continue  # already a second pass; cap reached
                    section_cache = creative_cache.get(t["slug"]) or {}
                    entry = section_cache.get(t["slot"]) or {}
                    html_frag = entry.get("html") or ""
                    if not html_frag:
                        continue
                    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as tf:
                        tf.write(html_frag); tmp_path = Path(tf.name)
                    warnings = lc.lint_file(tmp_path)
                    tmp_path.unlink(missing_ok=True)
                    score = lc.slide_score(warnings)
                    if score < lc.RE_ROLL_THRESHOLD:
                        continue
                    new_task = dict(t)
                    new_task["previous_html"] = html_frag
                    new_task["previous_critique"] = lc.format_critique(warnings)
                    new_task["pass"] = 2
                    second_pass.append(new_task)
                if second_pass:
                    print(
                        f"  · auto-re-roll-on-lint: queueing {len(second_pass)} slot(s) "
                        f"(weighted score ≥ {lc.RE_ROLL_THRESHOLD}, max 2 passes)",
                        file=sys.stderr,
                    )
                    with ThreadPoolExecutor(max_workers=max_workers) as pool:
                        futures = [pool.submit(_generate, t) for t in second_pass]
                        for fut in as_completed(futures):
                            task, html_frag, raw = fut.result()
                            slug = task["slug"]; slot = task["slot"]
                            personality = task["personality"]
                            creative_calls += 1
                            with cache_lock:
                                section_cache = creative_cache.get(slug) or {}
                                if html_frag:
                                    section_cache[slot] = {
                                        "html": html_frag,
                                        "personality": personality,
                                        "source_sha": task.get("section_sha", sha),
                                        "generated_at": built_at,
                                    }
                                creative_cache[slug] = section_cache
                            if html_frag:
                                print(f"    ✓ pass-2 {slot} for {slug} ({personality})", file=sys.stderr)
                                # Splice into the candidate card
                                for sec in section_candidates:
                                    if sec["slug"] != slug:
                                        continue
                                    for c in sec["candidates"]:
                                        if c.get("component") == slot:
                                            c["html"] = html_frag
                                            c["rationale"] = f"agent-authored ({personality}) · pass-2 critique"
            except Exception as exc:
                print(f"  · auto-re-roll-on-lint skipped — {exc}", file=sys.stderr)

    # ── Finalize pass: walk slide_plan in source order; choose per eligible section now that all html exists ──
    sec_by_slug = {sec["slug"]: sec for sec in section_candidates}

    def _choose(sec: dict, base: dict, cands_list: list) -> dict | None:
        all_candidates = sec["candidates"]
        locked_name = sec.pop("_locked_name", None)
        locked_html = sec.pop("_locked_html", None)
        viable = [c for c in all_candidates if c.get("html")]
        if not viable:
            viable = all_candidates  # last-resort fallback
        chosen_idx = 0
        if locked_name:
            found = False
            for i, c in enumerate(all_candidates):
                if c["component"] == locked_name and c.get("html"):
                    chosen_idx = i
                    found = True
                    break
            if not found and locked_html:
                all_candidates.insert(0, {
                    "component": locked_name,
                    "score": 1.0,
                    "rationale": "locked from picks.json",
                    "cluster": "locked",
                    "kind": "creative" if str(locked_name).startswith("creative-") else "template",
                    "html": locked_html,
                })
                chosen_idx = 0
            elif not found:
                chosen = max(viable, key=lambda c: c["score"])
                chosen_idx = all_candidates.index(chosen)
        else:
            chosen = max(viable, key=lambda c: c["score"])
            chosen_idx = all_candidates.index(chosen)
        return all_candidates[chosen_idx]

    def _emit_chosen(chosen: dict, base: dict, cands_list: list, slug: str) -> None:
        """Append the right kind of final slide for `chosen` candidate dict."""
        components_used.add(chosen["component"])
        if chosen.get("kind") == "creative":
            # Cached creative HTML may carry a stale `data-source-anchor` attribute
            # (the agent baked the legacy line-range form into the HTML when the
            # cache entry was rolled). Rewrite to the slug so the rendered deck
            # is consistent with picks/cache identity.
            raw_html = chosen.get("html", "")
            if raw_html and slug:
                raw_html = re.sub(
                    r'data-source-anchor="[^"]*"',
                    f'data-source-anchor="{_esc(slug)}"',
                    raw_html,
                    count=1,
                )
            final_slides.append({
                "type": "raw-html",
                "title": base.get("title", ""),
                "section": base.get("section"),
                "anchor": base.get("anchor", slug),
                "slug": slug,
                "source_lines": base.get("source_lines"),
                "source_sha256": base.get("source_sha256"),
                "raw_html": raw_html,
            })
        else:
            for adapted, cs in cands_list:
                if cs.name == chosen["component"]:
                    final_slides.append(adapted)
                    return
            final_slides.append(base)

    for entry in slide_plan:
        if entry["kind"] == "passthrough":
            final_slides.append(entry["base"])
            continue
        slug = entry["slug"]
        sec = sec_by_slug.get(slug)
        base = base_slide_by_anchor.get(slug)
        cands_list = cands_by_anchor.get(slug) or []
        if sec is None or base is None:
            if base is not None:
                final_slides.append(base)
            continue

        pick_entries = sec.pop("_pick_entries", None) or []
        if pick_entries:
            # Multi-pick: emit one slide per pick in selection order. Each pick
            # finds its candidate by component name; locked html (from picks.json)
            # wins over candidate html, so a creative pick re-emits the cached
            # HTML rather than re-rolling.
            for pe in pick_entries:
                comp = pe.get("component")
                cached_html = pe.get("html")
                # Find the matching candidate card to determine kind/template-vs-creative
                match = next((c for c in sec["candidates"] if c.get("component") == comp), None)
                if cached_html and (not match or not match.get("html")):
                    # Splice in a synthetic chosen card carrying the cached html
                    match = {
                        "component": comp,
                        "kind": "creative" if str(comp).startswith("creative-") else "template",
                        "html": cached_html,
                    }
                if match is None:
                    continue  # picked component not present in current candidates AND no cached html
                _emit_chosen(match, base, cands_list, slug)
        else:
            # No picks → fall back to the top-scoring candidate
            chosen = _choose(sec, base, cands_list)
            _emit_chosen(chosen, base, cands_list, slug)

    # Persist the creative cache (and create empty picks.json scaffolding if absent).
    # `--no-cache` (1.12) suppresses persistence so a forensic run leaves the
    # on-disk cache untouched.
    if creative_mode and not disable_cache:
        _save_creative_cache(out_dir, source_sha=sha, source_name=source_path.name, cache=creative_cache)

    # Variant injection (v0.2 multi-emit) runs on the locked slide list
    slides = expand_with_variants(final_slides)

    body = render_slides_html(slides)
    html = wrap_document(
        body=body, source_path=source_path, source_sha=sha,
        built_at=built_at, slide_count=len(slides), style=style,
    )

    out_html = out_dir / "index.html"
    out_html.write_text(html, encoding="utf-8")
    out_manifest = write_manifest(
        out_dir=out_dir, source_path=source_path, source_sha=sha,
        built_at=built_at, style=style, slides=slides,
    )

    # Emit candidates.html when:
    #   (a) --review explicitly requested, or
    #   (b) no picks.json exists yet (first-build auto-open per open-question 6)
    candidates_html_path: Path | None = None
    if section_candidates and (review or not picks):
        cand_body = _emit_candidates_html(
            section_candidates, source_path=source_path,
            source_sha=sha, built_at=built_at, style=style,
        )
        full = wrap_document(
            body=f'<div class="candidates-page">{cand_body}</div>',
            source_path=source_path, source_sha=sha,
            built_at=built_at, slide_count=len(section_candidates), style=style,
        )
        candidates_html_path = out_dir / "candidates.html"
        candidates_html_path.write_text(full, encoding="utf-8")

    return {
        "html": out_html,
        "candidates_html": candidates_html_path,
        "manifest": out_manifest,
        "slide_count": len(slides),
        "section_count": len(section_candidates),
        "components_used": sorted(components_used),
        "picks_loaded": len(picks),
        "size_bytes": out_html.stat().st_size,
        "sha": sha,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="md-deck build")
    parser.add_argument("source", help="Markdown source file")
    parser.add_argument("--style", default="bold-signal",
                        help="Style preset (resolved against frontend-slides/presets/<name>.css; "
                             "falls back to md-deck/styles/<name>.css)")
    parser.add_argument("--output-dir", default=None,
                        help="Override output directory (default: <root>/assets/<slug>/)")
    parser.add_argument("--review", action="store_true",
                        help="Always emit candidates.html for the 4-up review UI; "
                             "without --review, candidates.html only emits when no "
                             "picks.json exists yet (first build).")
    parser.add_argument("--creative", action="store_true",
                        help="Generate slots C and D as agent-authored bespoke slides "
                             "via `claude -p`. Off by default; opt-in adds ~5–30s of "
                             "latency per build (cached after first run).")
    parser.add_argument("--creative-section", default=None,
                        help="When set, only generate creative slots for the section "
                             "with this slug (e.g., s8-5-rules-conventions). Other "
                             "sections still render template slots but skip creative "
                             "slots. Legacy `L<lo>-L<hi>` form is auto-migrated.")
    parser.add_argument("--re-roll-creative", action="append", default=[],
                        help="Force re-generation of creative slots for a section, "
                             "ignoring the cache. Can be passed multiple times. "
                             "Argument is the section slug (e.g., s8-5-rules-conventions); "
                             "legacy `L<lo>-L<hi>` form is auto-migrated. "
                             "Example: --re-roll-creative s8-5-rules-conventions")
    parser.add_argument("--re-roll-section", action="append", default=[],
                        help="Stronger than --re-roll-creative: also forces the "
                             "deck-wide distillation to regenerate, so the named "
                             "section's dossier is fresh before the agent rolls. "
                             "Use when you've edited the source markdown for a "
                             "section and want both the dossier + creatives "
                             "refreshed in one step. Implies --re-roll-creative "
                             "<slug> + --re-roll-distillation.")
    parser.add_argument("--re-roll-distillation", action="store_true",
                        help="Force the deck-wide distillation to regenerate "
                             "even if the cached distillation.yml is current.")
    parser.add_argument("--sweep-cache", action="store_true",
                        help="Remove orphan and stale-SHA files from the deck's "
                             ".creative-cache/ before building. Orphan = slug no "
                             "longer in source. Stale = slug present but the "
                             "section's source_sha changed. No agent calls; "
                             "exits after the sweep when no other build flags "
                             "trigger downstream work.")
    parser.add_argument("--sweep-cache-dry-run", action="store_true",
                        help="Report what --sweep-cache would remove without "
                             "deleting. Implies --sweep-cache.")
    parser.add_argument("--no-cache", action="store_true",
                        help="Forensic / debug bypass: load no creative cache, "
                             "persist no creative cache. Every creative slot is "
                             "rolled fresh and the result is discarded after "
                             "rendering. Implies --creative when paired with "
                             "agent slots; otherwise no-op.")
    parser.add_argument("--auto-re-roll-on-lint", action="store_true",
                        help="After the initial creative fan-out, lint each "
                             "newly-rolled slot and queue a critique-aware "
                             "second pass for any whose weighted lint score "
                             "meets the threshold. Hard-capped at 2 passes "
                             "per slot. Off by default — opt-in because the "
                             "linter is heuristic and re-rolls cost agent "
                             "calls. Manual `--re-roll-creative <slug>` is "
                             "always critique-aware when previous cache "
                             "exists, regardless of this flag.")
    parser.add_argument("--creative-parallelism", type=int, default=5,
                        help="Max concurrent `claude -p` calls during the creative "
                             "fan-out (default: 5). Higher values speed up the "
                             "pass but may hit rate limits.")
    parser.add_argument("--dump-distillation", action="store_true",
                        help="Print the loaded distillation YAML to stdout after build "
                             "(implies --creative — runs distillation if needed).")
    parser.add_argument("--vocabulary", action="append", default=[],
                        help="Activate one or more icon vocabulary packs for "
                             "domain-specific keyword routing. Comma-separated "
                             "or repeated. Example: '--vocabulary medtech' or "
                             "'--vocabulary medtech,finance'. Available packs: "
                             "medtech, finance, manufacturing (and project-"
                             "supplied packs). When omitted, falls back to "
                             "project.yml `md_deck.vocabulary_packs`, then to "
                             "trunk-only (domain-neutral) behavior.")
    parser.add_argument("--candidate-mix", default="1,3",
                        help="Mix of candidate slots: '<templates>,<agents>'. Default '1,3' "
                             "(1 template + 3 agents: bold-metaphor / structured-diagram / "
                             "free-creative wild card). '2,2' is the conservative mix "
                             "(2 templates + bold-metaphor + structured-diagram). '0,4' is "
                             "agents-only (the 4th slot is a second independent free-creative "
                             "roll for divergent options). Sum must be ≥ 1 and ≤ 4.")
    args = parser.parse_args()

    # Resolve + activate icon vocabulary packs (CLI flag → project.yml → none).
    # Configure once for the duration of the build; later imports / calls of
    # icons.pick / icons.detect_group consult the loaded packs automatically.
    _vocab_packs = _resolve_vocabulary_packs(args.vocabulary)
    if _vocab_packs:
        try:
            _configure_vocabularies(_vocab_packs)
        except ImportError as exc:
            print(f"warning: vocabulary pack load failed: {exc}", file=sys.stderr)

    source_path = Path(args.source)
    if not source_path.exists():
        print(f"error: source not found: {source_path}", file=sys.stderr)
        return 2

    out_dir = Path(args.output_dir) if args.output_dir else None
    creative_mode = args.creative or args.dump_distillation
    # Parse --candidate-mix N,M
    try:
        ts, ags = (int(x.strip()) for x in args.candidate_mix.split(","))
    except (ValueError, AttributeError):
        print(f"error: --candidate-mix must be 'N,M' (got: {args.candidate_mix!r})", file=sys.stderr)
        return 2
    if ts < 0 or ags < 0 or (ts + ags) < 1 or (ts + ags) > 4:
        print(f"error: --candidate-mix sum must be 1..4 with both ≥ 0 (got: {ts},{ags})", file=sys.stderr)
        return 2

    # --sweep-cache (and dry-run variant) — short-circuit before the build pipeline
    if args.sweep_cache or args.sweep_cache_dry_run:
        text = source_path.read_text(encoding="utf-8")
        blocks = parse_markdown(text)
        slides = synthesize_slides(blocks, source_path, source_text=text)
        current_slugs = {s["slug"] for s in slides if s.get("slug")}
        # Per-section SHA index — sweep validates each cache entry against its
        # own section's content SHA (matches what _save_creative_cache writes).
        slug_to_sha: dict[str, str] = {}
        for s in slides:
            sg = s.get("slug")
            sha = s.get("source_sha256", "")
            if sg and sha and sg not in slug_to_sha:
                slug_to_sha[sg] = sha
        # Resolve out_dir the same way build() does
        if out_dir is None:
            cur = source_path.resolve().parent
            root = cur
            while root != root.parent:
                if (root / ".claude").exists() or (root / "project.yml").exists():
                    break
                root = root.parent
            sweep_dir = root / "assets" / _slugify(source_path.stem)
        else:
            sweep_dir = out_dir.resolve()
        orphan, stale = sweep_creative_cache(
            sweep_dir, current_slugs, slug_to_sha,
            dry_run=args.sweep_cache_dry_run,
        )
        verb = "would remove" if args.sweep_cache_dry_run else "removed"
        print(f"✓ md-deck sweep: {verb} {len(orphan)} orphan + {len(stale)} stale cache files")
        for p in orphan[:10]:
            print(f"   orphan: {p.name}")
        if len(orphan) > 10:
            print(f"   … and {len(orphan) - 10} more orphans")
        for p in stale[:10]:
            print(f"   stale:  {p.name}")
        if len(stale) > 10:
            print(f"   … and {len(stale) - 10} more stale")
        return 0

    # --re-roll-section <slug> = --re-roll-creative <slug> + --re-roll-distillation
    re_roll_creative_combined = list(args.re_roll_creative or []) + list(args.re_roll_section or [])
    re_roll_distillation_combined = bool(args.re_roll_distillation) or bool(args.re_roll_section)

    result = build(
        source_path, out_dir, args.style,
        review=args.review,
        creative_mode=creative_mode,
        creative_section=args.creative_section,
        re_roll_creative=re_roll_creative_combined,
        re_roll_distillation=re_roll_distillation_combined,
        creative_parallelism=args.creative_parallelism,
        template_slots=ts,
        agent_slots=ags,
        disable_cache=args.no_cache,
        auto_re_roll_on_lint=args.auto_re_roll_on_lint,
    )

    size_kb = result["size_bytes"] // 1024
    print(f"✓ md-deck v{VERSION} build complete")
    print(f"  source:   {source_path}")
    print(f"  output:   {result['html'].relative_to(Path.cwd()) if Path.cwd() in result['html'].parents else result['html']}")
    print(f"  slides:   {result['slide_count']} ({result['section_count']} variant-eligible sections)")
    print(f"  picks:    {result['picks_loaded']} loaded from picks.json")
    print(f"  used:     {', '.join(result['components_used']) or '(only existing components)'}")
    print(f"  size:     {size_kb} KB")
    print(f"  sha256:   {result['sha'][:16]}…")
    if result.get("candidates_html"):
        print(f"  review:   {result['candidates_html'].relative_to(Path.cwd()) if Path.cwd() in result['candidates_html'].parents else result['candidates_html']}")

    # ben/167 — soft layout-risk lint over the cache. Warnings only, never
    # blocks the build. Suppressed when no lint script is present.
    try:
        from importlib.util import spec_from_file_location, module_from_spec
        lint_path = Path(__file__).resolve().parent / "lint-creative.py"
        if lint_path.exists():
            spec = spec_from_file_location("lint_creative", lint_path)
            mod = module_from_spec(spec); spec.loader.exec_module(mod)  # type: ignore
            lint = mod.lint_deck(result["html"].parent)
            if lint["warnings"] > 0:
                print(f"  lint:     {lint['warnings']} warning(s) across {len(lint['by_file'])} slide(s) — see `lint-creative.py`")
                for cls in sorted(lint["by_class"]):
                    label = {"A": "edge-bleed", "B": "half-empty-grid",
                             "C": "under-constrained-absolute", "D": "tiny-font"}.get(cls, cls)
                    print(f"            · {cls} {label:32s} {lint['by_class'][cls]:4d}")
    except Exception as exc:
        print(f"  lint:     (skipped — {exc})", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
