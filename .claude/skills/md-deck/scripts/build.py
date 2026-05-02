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
    detect_group as _detect_group,
    pick_group as _pick_group_icon,
)

VERSION = "0.2.0"
SKILL_DIR = Path(__file__).resolve().parent.parent  # .claude/skills/md-deck/
CSS_PATH = SKILL_DIR / "styles" / "bold-signal.css"
JS_PATH = SKILL_DIR / "runtime" / "deck-runtime.js"


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def _slugify(s: str) -> str:
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-") or "deck"


def _esc(s: str) -> str:
    return html_mod.escape(s, quote=True)


def _shorten(text: str, n_words: int) -> str:
    words = text.split()
    if len(words) <= n_words:
        return text
    return " ".join(words[:n_words]).rstrip(",;:") + "…"


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

def synthesize_slides(blocks: list[dict], source_path: Path) -> list[dict]:
    """Walk the block stream and synthesize the slide list."""
    slides: list[dict] = []

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
        # Optional lead paragraph
        if cursor < len(blocks) and blocks[cursor]["type"] == "para":
            lead = blocks[cursor]["text"]
            cursor += 1
        # Optional **Key:** value meta paragraph
        while cursor < len(blocks) and blocks[cursor]["type"] == "para":
            t = blocks[cursor]["text"]
            for m in re.finditer(r"\*\*([^*]+):\*\*\s*([^*]+?)(?=\s*\*\*|\s*$)", t):
                meta_pairs.append((m.group(1).strip(), m.group(2).strip()))
            if meta_pairs:
                cursor += 1
                break
            else:
                cursor += 1

    if title_text:
        slides.append({
            "type": "title",
            "title": title_text,
            "lead": lead,
            "meta": meta_pairs,
            "anchor": f"L{blocks[0].get('line', 1)}",
            "section": None,
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
                })
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
                m = re.match(r"^\*\*([^*]+?)\*\*[:.\s—-]*\s*(.*)$", it)
                if m:
                    label = m.group(1).strip()
                    sub = m.group(2).strip()
                else:
                    label = it[:60]
                    sub = ""
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


def _inject_variants(slide: dict) -> list[dict]:
    """Return zero-or-more variant slides to emit RIGHT AFTER the input slide."""
    out: list[dict] = []
    title = (slide.get("title") or "").lower()

    # Catalog tables → mosaic (paginated) + featured
    if slide["type"] == "table-slide":
        table = slide.get("table") or {}
        rows = table.get("rows", [])
        cols = table.get("header", [])
        if len(rows) >= 6 and len(cols) == 2:
            out.extend(_make_catalog_mosaic_slides(slide))
            out.append(_make_catalog_featured_slide(slide))
            return out  # catalog skips other variants

    # Scope-iceberg
    if any(k in title for k in SCOPE_KEYWORDS):
        v = _make_scope_iceberg(slide)
        if v:
            out.append(v)

    # Concept-canvas
    if any(k in title for k in TEACH_KEYWORDS):
        v = _make_concept_canvas(slide)
        if v:
            out.append(v)

    # Handoff-relay
    if any(k in title for k in HANDOFF_KEYWORDS):
        v = _make_handoff_relay(slide)
        if v:
            out.append(v)

    # Principle-tiles for dense card-grids
    if slide["type"] == "card-grid" and len(slide.get("tiles") or []) >= 4:
        v = _make_principle_tiles(slide)
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
        tiles_out.append({
            "label": label,
            "subtitle": _shorten(sub, 14),
            "icon": _pick_icon(label + " " + sub),
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
    if slide["type"] == "card-grid":
        for t in slide.get("tiles", []):
            line = (t.get("label", "") + " " + t.get("subtitle", "")).lower()
            tag = t.get("label", "")
            if any(k in line for k in ("out of scope", "out-of-scope", "out scope", "carve-out", "delete", "exclude")):
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
<section class="slide title-slide" data-source-anchor="{_esc(s.get("anchor", ""))}">
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
<section class="slide" data-source-anchor="{_esc(s.get("anchor", ""))}">
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
<section class="slide divider-slide" data-source-anchor="{_esc(s.get("anchor", ""))}">
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
<section class="slide" data-source-anchor="{_esc(s.get("anchor", ""))}">
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
        '</div>'
        for i, t in enumerate(s.get("tiles", []))
    )
    return f'''
<section class="slide" data-source-anchor="{_esc(s.get("anchor", ""))}">
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
<section class="slide" data-source-anchor="{_esc(s.get("anchor", ""))}">
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
<section class="slide" data-source-anchor="{_esc(s.get("anchor", ""))}">
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
<section class="slide" data-source-anchor="{_esc(s.get("anchor", ""))}">
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
<section class="slide" data-source-anchor="{_esc(s.get("anchor", ""))}">
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
<section class="slide" data-source-anchor="{_esc(s.get("anchor", ""))}">
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
        # Tagline shown in resting state, full description visible in popup
        cells.append(
            f'<div class="cat-cell {cat_class}" data-full="{_esc(it.get("full_desc", ""))}">'
            f'<div class="cc-icon lg {cat_class}">{it["icon"]}</div>'
            f'<div class="cc-name">{_esc(it.get("name", ""))}</div>'
            f'<div class="cc-cat-row"><span class="cc-cat">{_esc(it.get("category_label", ""))}</span></div>'
            f'<div class="cc-tagline">{render_inline(it.get("tagline", ""))}</div>'
            '</div>'
        )
    page_idx = s.get("page_idx", 0)
    eyebrow = "Variation A · Catalog Mosaic" if page_idx == 0 else f"Variation A · Catalog Mosaic — page {page_idx + 1}"
    return f'''
<section class="slide" data-source-anchor="{_esc(s.get("anchor", ""))}">
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
<section class="slide" data-source-anchor="{_esc(s.get("anchor", ""))}">
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
<section class="slide" data-source-anchor="{_esc(s.get("anchor", ""))}">
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
<section class="slide" data-source-anchor="{_esc(s.get("anchor", ""))}">
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
<section class="slide" data-source-anchor="{_esc(s.get("anchor", ""))}">
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
    css = _load_asset(CSS_PATH)
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
        "schema": "md-deck/manifest@1",
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

def expand_with_variants(slides: list[dict]) -> list[dict]:
    out: list[dict] = []
    for s in slides:
        out.append(s)
        for v in _inject_variants(s):
            out.append(v)
    return out


def build(source_path: Path, output_dir: Path | None, style: str) -> dict:
    text = source_path.read_text(encoding="utf-8")
    sha = hashlib.sha256(text.encode()).hexdigest()
    built_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    blocks = parse_markdown(text)
    base_slides = synthesize_slides(blocks, source_path)
    slides = expand_with_variants(base_slides)

    body = render_slides_html(slides)
    html = wrap_document(
        body=body, source_path=source_path, source_sha=sha,
        built_at=built_at, slide_count=len(slides), style=style,
    )

    slug = _slugify(source_path.stem)
    if output_dir is None:
        # find project root by walking up for .claude/
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

    out_html = out_dir / "index.html"
    out_html.write_text(html, encoding="utf-8")
    out_manifest = write_manifest(
        out_dir=out_dir, source_path=source_path, source_sha=sha,
        built_at=built_at, style=style, slides=slides,
    )
    return {
        "html": out_html,
        "manifest": out_manifest,
        "slide_count": len(slides),
        "size_bytes": out_html.stat().st_size,
        "sha": sha,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="md-deck build")
    parser.add_argument("source", help="Markdown source file")
    parser.add_argument("--style", default="bold-signal",
                        help="Style preset (currently only bold-signal)")
    parser.add_argument("--output-dir", default=None,
                        help="Override output directory (default: <root>/assets/<slug>/)")
    args = parser.parse_args()

    source_path = Path(args.source)
    if not source_path.exists():
        print(f"error: source not found: {source_path}", file=sys.stderr)
        return 2

    out_dir = Path(args.output_dir) if args.output_dir else None
    result = build(source_path, out_dir, args.style)

    size_kb = result["size_bytes"] // 1024
    print(f"✓ md-deck v{VERSION} build complete")
    print(f"  source:   {source_path}")
    print(f"  output:   {result['html'].relative_to(Path.cwd()) if Path.cwd() in result['html'].parents else result['html']}")
    print(f"  slides:   {result['slide_count']}")
    print(f"  size:     {size_kb} KB")
    print(f"  sha256:   {result['sha'][:16]}…")
    return 0


if __name__ == "__main__":
    sys.exit(main())
