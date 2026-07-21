#!/usr/bin/env python3
from __future__ import annotations
"""
client-pdlc composite-deck builder — two-pass workflow.

Pass 1 (SELECT):
  python build.py --candidate     # candidate.html shows all 126 slides
                                  #   in source order, KEEP/REMOVE only.
                                  #   Default = all keep. Reads existing
                                  #   picks.json if present.

  → user toggles KEEP/REMOVE → clicks Export picks.json → drops the
    downloaded file into ./picks.json

Pass 2 (REORDER):
  python build.py --reorder       # rebuilds candidate.html in place
                                  #   showing only the kept slides
                                  #   from picks.json. No toggles —
                                  #   drag / ▲ / ▼ only.

  → user reorders → Export picks.json → drops over ./picks.json

Final:
  python build.py --final         # reads picks.json and emits
                                  #   index.html with kept slides in
                                  #   the chosen order.

Schema for picks.json:
  {
    "schema": "client-pdlc/picks@1",
    "sources": { "<name>": "<rel path to source index.html>", ... },
    "order":   [ { "src": "<name>", "idx": <int>, "keep": <bool> }, ... ]
  }

  - SELECT writes the full order[] in source order with current keep state.
  - REORDER writes order[] with kept slides in the user's chosen sequence,
    followed by all keep:false slides (preserved at the tail).
"""

import argparse
import html as _html
import json
import re
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent

SOURCES = [
    ("agentic-delivery",  "../agentic-delivery/index.html"),
    ("project-overview",  "../project-overview/index.html"),
]

IMG_REWRITES: dict[str, dict[str, str]] = {}

BADGE_CLASS = {
    "agentic-delivery":   "agentic",
    "project-overview":   "overview",
}


# ---------------------------------------------------------------------------
# CSS scoping
# ---------------------------------------------------------------------------

_AT_BLOCK_NESTABLE = {"media", "supports", "document", "container", "layer"}


def _strip_comments(css: str) -> str:
    return re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)


def _rewrite_selector(sel: str, scope: str) -> str:
    sel = sel.strip()
    if not sel:
        return ""
    for top in ("body", "html", ":root"):
        if sel == top:
            return f".{scope}"
        if sel.startswith(top) and (sel[len(top)] in " .:#[>~+,*"):
            return f".{scope}{sel[len(top):]}"
    if sel == "*":
        return f".{scope} *"
    return f".{scope} {sel}"


def _scope_selector_list(sel_list: str, scope: str) -> str:
    parts = [_rewrite_selector(s, scope) for s in sel_list.split(",")]
    return ", ".join(p for p in parts if p)


def _scope_rules(css: str, scope: str) -> str:
    out = []
    i = 0
    n = len(css)
    while i < n:
        while i < n and css[i] in " \t\r\n":
            out.append(css[i])
            i += 1
        if i >= n:
            break
        if css[i] == "@":
            j = i
            while j < n and css[j] not in ";{":
                j += 1
            if j >= n:
                out.append(css[i:])
                break
            if css[j] == ";":
                out.append(css[i:j + 1]); i = j + 1; continue
            name_m = re.match(r"@([\w-]+)", css[i:])
            at_name = name_m.group(1).lower() if name_m else ""
            prelude = css[i:j + 1]
            depth = 1; k = j + 1
            while k < n and depth > 0:
                if css[k] == "{": depth += 1
                elif css[k] == "}": depth -= 1
                k += 1
            body = css[j + 1:k - 1]
            closer = "}"
            if at_name == "media" and re.search(r"max-(width|height)", prelude):
                # DROP "collapse on small viewport" media queries entirely.
                # The composite deck is always rendered at a fixed 1400x900
                # slide size (HTML view + PDF alike), so these never *should*
                # fire — and Chrome's --print-to-pdf evaluates max-width/height
                # against a narrow default page width, NOT the @page size, so
                # they spuriously fire in print: card grids collapse to one
                # column, content doubles in height, and slides clip.
                i = k; continue
            if at_name in _AT_BLOCK_NESTABLE:
                out.append(prelude + _scope_rules(body, scope) + closer)
            else:
                out.append(prelude + body + closer)
            i = k; continue
        j = i
        while j < n and css[j] != "{":
            j += 1
        if j >= n:
            out.append(css[i:]); break
        sel_list = css[i:j]
        depth = 1; k = j + 1
        while k < n and depth > 0:
            if css[k] == "{": depth += 1
            elif css[k] == "}": depth -= 1
            k += 1
        decls = css[j:k]
        out.append(_scope_selector_list(sel_list, scope) + " " + decls)
        i = k
    return "".join(out)


def scope_css(css: str, scope: str) -> str:
    return _scope_rules(_strip_comments(css), scope)


# ---------------------------------------------------------------------------
# Deck parsing
# ---------------------------------------------------------------------------

_SLIDE_RE = re.compile(r'<section\s+class="slide[^"]*"[^>]*>.*?</section>', re.DOTALL)
_STYLE_RE = re.compile(r'<style[^>]*>(.*?)</style>', re.DOTALL)
_LINK_RE = re.compile(r'<link\b[^>]*?/?>', re.DOTALL)
_BODY_RE = re.compile(r'<body[^>]*>(.*?)</body>', re.DOTALL)
_SECTION_OPEN_RE = re.compile(r'<section\s+class="([^"]*)"')


def _ensure_visible(slide_html: str) -> str:
    def repl(m):
        classes = m.group(1).split()
        if "visible" not in classes:
            classes.append("visible")
        return f'<section class="{" ".join(classes)}"'
    return _SECTION_OPEN_RE.sub(repl, slide_html, count=1)


def parse_deck(name: str, rel_path: str) -> dict:
    src = (ROOT / rel_path).resolve()
    if not src.is_file():
        sys.exit(f"missing source deck: {src}")
    html_text = src.read_text(encoding="utf-8")
    head_m = re.search(r"<head[^>]*>(.*?)</head>", html_text, re.DOTALL)
    head = head_m.group(1) if head_m else ""
    links = _LINK_RE.findall(head)
    style_m = _STYLE_RE.search(html_text)
    style = style_m.group(1) if style_m else ""
    body_m = _BODY_RE.search(html_text)
    body = body_m.group(1) if body_m else html_text
    slides = _SLIDE_RE.findall(body)
    rewrites = IMG_REWRITES.get(name, {})
    if rewrites:
        for old, new in rewrites.items():
            slides = [s.replace(f'src="{old}"', f'src="{new}"') for s in slides]
            slides = [s.replace(f"src='{old}'", f"src='{new}'") for s in slides]
    slides = [_ensure_visible(s) for s in slides]
    return {
        "name": name,
        "links": links,
        "style": style,
        "slides": slides,
        "scope": f"src-{name}",
    }


def load_picks() -> dict | None:
    p = ROOT / "picks.json"
    if not p.is_file():
        return None
    picks = json.loads(p.read_text(encoding="utf-8"))
    if picks.get("schema") != "client-pdlc/picks@1":
        sys.exit(f"unexpected picks.json schema: {picks.get('schema')!r}")
    return picks


# ---------------------------------------------------------------------------
# Candidate page — shared CSS
# ---------------------------------------------------------------------------

CANDIDATE_CSS = """
:root {
  --bg: #0b0d12;
  --panel: #14181f;
  --panel-2: #1c222c;
  --ink: #e6e9ef;
  --muted: #8892a6;
  --accent: #ff7849;
  --keep: #4ade80;
  --remove: #ef4444;
  --border: #2a313d;
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text",
    "Segoe UI", Helvetica, Arial, sans-serif;
}
html, body { margin: 0; padding: 0; background: var(--bg); color: var(--ink); }

.cp-topbar {
  position: sticky; top: 0; z-index: 1000;
  background: var(--panel); border-bottom: 1px solid var(--border);
  padding: 10px 16px; display: flex; gap: 18px; align-items: center;
  font-size: 13px;
}
.cp-topbar h1 { font-size: 14px; margin: 0; font-weight: 600; letter-spacing: 0.02em; }
.cp-topbar .mode {
  background: var(--accent); color: #0b0d12;
  padding: 2px 8px; border-radius: 3px; font-weight: 700;
  font-size: 11px; letter-spacing: 0.08em;
}
.cp-topbar .mode.reorder { background: #60a5fa; }
.cp-topbar .stat { color: var(--muted); }
.cp-topbar .stat b { color: var(--ink); }
.cp-topbar button {
  background: var(--accent); color: #0b0d12; border: 0;
  padding: 6px 12px; border-radius: 4px; font-weight: 600;
  cursor: pointer; font-size: 12px;
}
.cp-topbar button.secondary {
  background: var(--panel-2); color: var(--ink);
  border: 1px solid var(--border);
}
.cp-topbar .spacer { flex: 1; }
.cp-help {
  padding: 10px 16px; background: var(--panel-2); color: var(--muted);
  font-size: 12px; border-bottom: 1px solid var(--border);
}
.cp-help kbd {
  background: var(--bg); border: 1px solid var(--border);
  padding: 1px 6px; border-radius: 3px; font-family: monospace;
  color: var(--ink);
}
.cp-help code {
  background: var(--bg); border: 1px solid var(--border);
  padding: 1px 6px; border-radius: 3px; font-family: monospace;
  color: var(--ink);
}

.cp-list { padding: 16px; display: flex; flex-direction: column; gap: 14px; }

.cp-slide {
  position: relative;
  background: #000;
  border: 2px solid var(--border);
  border-radius: 6px;
  overflow: hidden;
  transition: opacity 0.15s, border-color 0.15s;
}
.cp-slide[data-keep="false"] {
  opacity: 0.35;
  border-color: var(--remove);
}
.cp-slide[data-keep="true"] {
  border-color: var(--keep);
}
.cp-slide.dragging { opacity: 0.5; }
.cp-slide.drop-target-before { border-top: 4px solid var(--accent); }
.cp-slide.drop-target-after  { border-bottom: 4px solid var(--accent); }

.cp-controls {
  position: absolute; top: 8px; right: 8px; z-index: 100;
  display: flex; gap: 6px; align-items: center;
  background: rgba(11, 13, 18, 0.85);
  padding: 6px 8px; border-radius: 4px;
  border: 1px solid var(--border);
  font-size: 11px;
  backdrop-filter: blur(6px);
}
.cp-controls .badge {
  background: var(--panel-2); color: var(--muted);
  padding: 2px 6px; border-radius: 3px;
  font-family: monospace; font-size: 10px;
}
.cp-controls .badge.agentic    { color: #fb923c; }
.cp-controls .badge.overview   { color: #60a5fa; }
.cp-controls .pos {
  background: var(--panel-2); color: var(--ink);
  padding: 2px 6px; border-radius: 3px;
  font-family: monospace; font-size: 10px; font-weight: 700;
  min-width: 28px; text-align: center;
}
.cp-controls button {
  background: var(--panel-2); color: var(--ink);
  border: 1px solid var(--border);
  padding: 2px 8px; border-radius: 3px; cursor: pointer;
  font-size: 11px; font-weight: 600;
}
.cp-controls button:hover { background: var(--border); }
.cp-controls .keep-toggle.keep   { background: var(--keep); color: #000; }
.cp-controls .keep-toggle.remove { background: var(--remove); color: #fff; }
.cp-controls .drag-handle {
  cursor: grab; padding: 2px 6px; color: var(--muted);
  user-select: none;
}
.cp-controls .drag-handle:active { cursor: grabbing; }

.cp-slide .scope-wrapper {
  position: relative;
  width: 100%;
}

/* ---- REORDER mode grid ---- */
body.mode-reorder .cp-list {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
  padding: 16px;
}
body.mode-reorder .cp-slide {
  aspect-ratio: 16 / 9;
  border-radius: 4px;
  cursor: grab;
}
body.mode-reorder .cp-slide.dragging { cursor: grabbing; }
body.mode-reorder .cp-slide .thumb-frame {
  width: 100%;
  height: 100%;
  border: 0;
  display: block;
  pointer-events: none;   /* drag passes through the iframe to the tile */
  background: #000;
}
body.mode-reorder .cp-controls {
  top: 4px; right: 4px;
  padding: 4px 6px;
  font-size: 10px;
  gap: 4px;
}
body.mode-reorder .cp-controls .badge {
  font-size: 9px; padding: 1px 4px;
}
body.mode-reorder .cp-controls button {
  padding: 1px 5px; font-size: 10px;
}
body.mode-reorder .cp-controls .pos-input {
  width: 34px;
  background: var(--panel-2); color: var(--ink);
  border: 1px solid var(--border);
  border-radius: 3px;
  padding: 1px 3px;
  font-family: monospace; font-size: 11px; font-weight: 700;
  text-align: center;
  -moz-appearance: textfield;
}
body.mode-reorder .cp-controls .pos-input::-webkit-outer-spin-button,
body.mode-reorder .cp-controls .pos-input::-webkit-inner-spin-button {
  -webkit-appearance: none; margin: 0;
}
body.mode-reorder .cp-controls .pos-input:focus {
  outline: 2px solid var(--accent); outline-offset: -1px;
}
body.mode-reorder .cp-slide.drop-target-before { border-left:   4px solid var(--accent); border-top: 2px solid var(--border); }
body.mode-reorder .cp-slide.drop-target-after  { border-right:  4px solid var(--accent); border-top: 2px solid var(--border); }
"""


# ---------------------------------------------------------------------------
# Candidate page — mode-specific JS
# ---------------------------------------------------------------------------

SELECT_JS = r"""
(function () {
  const STORAGE_KEY = "client-pdlc/picks@1";
  const SOURCES = window.__CP_SOURCES__;
  const INITIAL = window.__CP_INITIAL__;   // [{src, idx, keep}, ...] in source order
  const PRIOR_ORDER = window.__CP_PRIOR_ORDER__;  // picks.json order at build time, or null
  const BUILD_ID = window.__CP_BUILD_ID__;

  function defaultState() {
    return INITIAL.map(o => ({ ...o }));
  }

  function loadState() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return defaultState();
      const parsed = JSON.parse(raw);
      if (parsed._build_id !== BUILD_ID || !Array.isArray(parsed.order)) {
        return defaultState();
      }
      const want = INITIAL.length;
      if (parsed.order.length !== want) return defaultState();
      // Build a keep-map from stored, applied over source-order INITIAL
      const m = new Map(parsed.order.map(o => [`${o.src}#${o.idx}`, !!o.keep]));
      return INITIAL.map(o => ({ ...o, keep: m.has(`${o.src}#${o.idx}`) ? m.get(`${o.src}#${o.idx}`) : o.keep }));
    } catch (e) {
      console.warn("loadState failed:", e);
      return defaultState();
    }
  }

  function payloadFor(state) {
    // Preserve PRIOR_ORDER (Pass-2 reorder) if it exists; only update keep state.
    // Any slides missing from PRIOR_ORDER (shouldn't happen but defensive) appended at end.
    const keepMap = new Map(state.map(o => [`${o.src}#${o.idx}`, !!o.keep]));
    let order;
    if (PRIOR_ORDER && Array.isArray(PRIOR_ORDER) && PRIOR_ORDER.length === state.length) {
      const seen = new Set();
      order = PRIOR_ORDER.map(o => {
        const k = `${o.src}#${o.idx}`;
        seen.add(k);
        return { src: o.src, idx: o.idx, keep: keepMap.has(k) ? keepMap.get(k) : !!o.keep };
      });
      for (const o of state) {
        const k = `${o.src}#${o.idx}`;
        if (!seen.has(k)) order.push({ src: o.src, idx: o.idx, keep: !!o.keep });
      }
    } else {
      order = state.map(o => ({ src: o.src, idx: o.idx, keep: !!o.keep }));
    }
    return {
      schema: "client-pdlc/picks@1",
      _build_id: BUILD_ID,
      sources: Object.fromEntries(SOURCES.map(([n]) => [n, `../${n}/index.html`])),
      order,
    };
  }

  function save(state) {
    const payload = payloadFor(state);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(payload));
    return payload;
  }

  let state = loadState();
  const byKey = new Map(state.map(o => [`${o.src}#${o.idx}`, o]));

  const list = document.getElementById("cp-list");
  const statKept = document.getElementById("stat-kept");
  const statRemoved = document.getElementById("stat-removed");
  const statTotal = document.getElementById("stat-total");
  statTotal.textContent = state.length;

  function refreshStats() {
    const kept = state.filter(o => o.keep).length;
    statKept.textContent = kept;
    statRemoved.textContent = state.length - kept;
  }

  function applyKeep(node, keep) {
    node.dataset.keep = String(keep);
    const btn = node.querySelector(".keep-toggle");
    btn.textContent = keep ? "KEEP" : "REMOVE";
    btn.classList.toggle("keep", keep);
    btn.classList.toggle("remove", !keep);
  }

  Array.from(list.children).forEach(node => {
    const k = node.dataset.key;
    const o = byKey.get(k);
    if (!o) return;
    applyKeep(node, o.keep);
    node.querySelector(".keep-toggle").addEventListener("click", () => {
      o.keep = !o.keep;
      applyKeep(node, o.keep);
      save(state);
      refreshStats();
    });
  });

  document.getElementById("export-picks").addEventListener("click", () => {
    const payload = save(state);
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url; a.download = "picks.json"; a.click();
    URL.revokeObjectURL(url);
  });

  document.getElementById("reset").addEventListener("click", () => {
    if (!confirm("Reset every slide back to KEEP?")) return;
    localStorage.removeItem(STORAGE_KEY);
    location.reload();
  });

  document.getElementById("keep-all").addEventListener("click", () => {
    state.forEach(o => o.keep = true);
    save(state);
    Array.from(list.children).forEach(node => applyKeep(node, true));
    refreshStats();
  });

  document.getElementById("remove-all").addEventListener("click", () => {
    if (!confirm("Mark every slide as REMOVE?")) return;
    state.forEach(o => o.keep = false);
    save(state);
    Array.from(list.children).forEach(node => applyKeep(node, false));
    refreshStats();
  });

  refreshStats();
})();
"""


REORDER_JS = r"""
(function () {
  const STORAGE_KEY = "client-pdlc/picks@1";
  const SOURCES = window.__CP_SOURCES__;
  // Kept slides in their starting (picks.json) order
  const INITIAL_KEPT = window.__CP_INITIAL_KEPT__;
  // keep:false slides preserved for round-trip back to SELECT
  const REMOVED = window.__CP_REMOVED__;
  const BUILD_ID = window.__CP_BUILD_ID__;

  function defaultOrder() {
    return INITIAL_KEPT.map(o => ({ ...o, keep: true }));
  }

  function loadOrder() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return defaultOrder();
      const parsed = JSON.parse(raw);
      if (parsed._build_id !== BUILD_ID || !Array.isArray(parsed.order)) {
        return defaultOrder();
      }
      // pull the kept slides in localStorage order, but only those whose keys
      // are present in the rendered DOM (i.e., kept in this build)
      const present = new Set(INITIAL_KEPT.map(o => `${o.src}#${o.idx}`));
      const kept = parsed.order.filter(o => o.keep && present.has(`${o.src}#${o.idx}`));
      if (kept.length !== INITIAL_KEPT.length) return defaultOrder();
      return kept;
    } catch (e) {
      console.warn("loadOrder failed:", e);
      return defaultOrder();
    }
  }

  function payloadFor(keptOrder) {
    // export full picks: kept slides in chosen order, removed slides appended
    const orderArr = keptOrder.map(o => ({ src: o.src, idx: o.idx, keep: true }))
      .concat(REMOVED.map(o => ({ src: o.src, idx: o.idx, keep: false })));
    return {
      schema: "client-pdlc/picks@1",
      _build_id: BUILD_ID,
      sources: Object.fromEntries(SOURCES.map(([n]) => [n, `../${n}/index.html`])),
      order: orderArr,
    };
  }

  function save(keptOrder) {
    const payload = payloadFor(keptOrder);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(payload));
    return payload;
  }

  let order = loadOrder();

  const list = document.getElementById("cp-list");
  const statTotal = document.getElementById("stat-total");
  statTotal.textContent = order.length;

  function key(o) { return `${o.src}#${o.idx}`; }

  function reorderDom() {
    const map = new Map();
    Array.from(list.children).forEach(node => map.set(node.dataset.key, node));
    for (const o of order) {
      const node = map.get(key(o));
      if (node) list.appendChild(node);
    }
    refreshPos();
  }

  function refreshPos() {
    Array.from(list.children).forEach((node, i) => {
      const input = node.querySelector(".pos-input");
      if (input && document.activeElement !== input) input.value = String(i + 1);
    });
  }

  Array.from(list.children).forEach(node => {
    const k = node.dataset.key;
    node.dataset.keep = "true";
    node.draggable = true;   // whole tile draggable in grid mode
    const ctrls = node.querySelector(".cp-controls");
    ctrls.querySelector(".up").addEventListener("click", () => move(k, -1));
    ctrls.querySelector(".down").addEventListener("click", () => move(k, +1));

    // Position-input — type a 1-based position, press Enter or blur to apply
    const input = ctrls.querySelector(".pos-input");
    input.addEventListener("mousedown", e => e.stopPropagation());   // don't start drag
    input.addEventListener("keydown", e => {
      if (e.key === "Enter") { e.preventDefault(); input.blur(); }
      else if (e.key === "Escape") { refreshPos(); input.blur(); }
    });
    input.addEventListener("change", () => {
      const target = parseInt(input.value, 10);
      if (!Number.isFinite(target)) { refreshPos(); return; }
      moveToPosition(k, target);
    });

    // Don't initiate drag from inside controls (buttons/input)
    ctrls.addEventListener("mousedown", e => { e.stopPropagation(); });

    node.addEventListener("dragstart", e => {
      // Reject drags that started inside the controls overlay
      if (e.target.closest(".cp-controls")) { e.preventDefault(); return; }
      node.classList.add("dragging");
      e.dataTransfer.effectAllowed = "move";
      e.dataTransfer.setData("text/plain", k);
    });
    node.addEventListener("dragend", () => {
      node.classList.remove("dragging");
      list.querySelectorAll(".drop-target-before, .drop-target-after")
        .forEach(n => n.classList.remove("drop-target-before", "drop-target-after"));
    });
    node.addEventListener("dragover", e => {
      e.preventDefault();
      const rect = node.getBoundingClientRect();
      // grid mode: split on x; single-col fallback: split on y
      const horizontal = rect.width < window.innerWidth * 0.6;
      const after = horizontal
        ? (e.clientX - rect.left) > rect.width / 2
        : (e.clientY - rect.top) > rect.height / 2;
      node.classList.toggle("drop-target-before", !after);
      node.classList.toggle("drop-target-after",   after);
    });
    node.addEventListener("dragleave", () => {
      node.classList.remove("drop-target-before", "drop-target-after");
    });
    node.addEventListener("drop", e => {
      e.preventDefault();
      const srcKey = e.dataTransfer.getData("text/plain");
      if (!srcKey || srcKey === k) return;
      const rect = node.getBoundingClientRect();
      const horizontal = rect.width < window.innerWidth * 0.6;
      const after = horizontal
        ? (e.clientX - rect.left) > rect.width / 2
        : (e.clientY - rect.top) > rect.height / 2;
      moveTo(srcKey, k, after);
      node.classList.remove("drop-target-before", "drop-target-after");
    });
  });

  function move(k, delta) {
    const i = order.findIndex(o => key(o) === k);
    const j = i + delta;
    if (i < 0 || j < 0 || j >= order.length) return;
    [order[i], order[j]] = [order[j], order[i]];
    save(order);
    reorderDom();
  }

  function moveTo(srcKey, dstKey, after) {
    const fromIdx = order.findIndex(o => key(o) === srcKey);
    if (fromIdx < 0) return;
    const [moved] = order.splice(fromIdx, 1);
    let toIdx = order.findIndex(o => key(o) === dstKey);
    if (toIdx < 0) {
      order.splice(fromIdx, 0, moved);
      return;
    }
    if (after) toIdx += 1;
    order.splice(toIdx, 0, moved);
    save(order);
    reorderDom();
  }

  function moveToPosition(k, target) {
    // 1-based target → 0-based index
    const dstIdx = Math.max(0, Math.min(order.length - 1, target - 1));
    const fromIdx = order.findIndex(o => key(o) === k);
    if (fromIdx < 0 || fromIdx === dstIdx) { refreshPos(); return; }
    const [moved] = order.splice(fromIdx, 1);
    order.splice(dstIdx, 0, moved);
    save(order);
    reorderDom();
  }

  document.getElementById("export-picks").addEventListener("click", () => {
    const payload = save(order);
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url; a.download = "picks.json"; a.click();
    URL.revokeObjectURL(url);
  });

  document.getElementById("reset").addEventListener("click", () => {
    if (!confirm("Reset slide order back to the picks.json sequence?")) return;
    localStorage.removeItem(STORAGE_KEY);
    location.reload();
  });

  refreshPos();
})();
"""


# ---------------------------------------------------------------------------
# Candidate page — emit
# ---------------------------------------------------------------------------

def _slide_chrome_select(d, idx):
    badge = BADGE_CLASS[d["name"]]
    return (
        f'<div class="cp-controls">'
        f'<span class="badge {badge}">{d["name"]} #{idx}</span>'
        f'<button class="keep-toggle keep">KEEP</button>'
        f'</div>'
    )


def _slide_chrome_reorder(d, idx, total_kept):
    badge = BADGE_CLASS[d["name"]]
    return (
        f'<div class="cp-controls">'
        f'<input class="pos-input" type="number" min="1" max="{total_kept}" value="1" title="Type a position number and press Enter to move this slide there">'
        f'<span class="badge {badge}">{d["name"]} #{idx}</span>'
        f'<button class="up"   title="Move up">▲</button>'
        f'<button class="down" title="Move down">▼</button>'
        f'</div>'
    )


def _slide_article(d, idx, slide_html, chrome_html):
    return textwrap.dedent(f"""\
    <article class="cp-slide" data-key="{d['name']}#{idx}" data-src="{d['name']}" data-idx="{idx}">
    {chrome_html}
      <div class="scope-wrapper">
        <div class="{d['scope']}">
    {slide_html}
        </div>
      </div>
    </article>
    """)


def _iframe_srcdoc_for_slide(d, slide_html):
    """Build the srcdoc HTML for a thumbnail iframe. Inside an iframe the source
    deck's `body`/`html`/`:root`/`vw`/`vh` rules work natively against the iframe
    viewport — no scoping or scaling needed. We just inject the deck's full CSS
    plus the slide HTML; the iframe is sized 16:9 by the parent tile."""
    links_html = "\n".join(d["links"])
    inner = (
        f"<!doctype html><html><head><meta charset=\"utf-8\">{links_html}"
        f"<style>html,body{{margin:0;padding:0;background:#000;overflow:hidden}}"
        f"{d['style']}</style></head>"
        f"<body>{slide_html}</body></html>"
    )
    return _html.escape(inner, quote=True)


def _slide_article_reorder(d, idx, slide_html, chrome_html):
    srcdoc = _iframe_srcdoc_for_slide(d, slide_html)
    return textwrap.dedent(f"""\
    <article class="cp-slide" data-key="{d['name']}#{idx}" data-src="{d['name']}" data-idx="{idx}">
    {chrome_html}
      <iframe class="thumb-frame" srcdoc="{srcdoc}" loading="lazy"></iframe>
    </article>
    """)


def _build_id(decks: list[dict]) -> str:
    # cheap content fingerprint: per-deck (name, slide-count, len(style))
    return "|".join(f"{d['name']}:{len(d['slides'])}:{len(d['style'])}" for d in decks)


def build_candidate_select() -> Path:
    decks = [parse_deck(name, path) for name, path in SOURCES]
    picks = load_picks()

    # build (src, idx) → keep map from existing picks.json
    keep_map = {}
    if picks:
        for o in picks.get("order", []):
            keep_map[(o["src"], int(o["idx"]))] = bool(o.get("keep", True))

    # initial state in source order
    initial = []
    for d in decks:
        for idx in range(len(d["slides"])):
            initial.append({
                "src": d["name"], "idx": idx,
                "keep": keep_map.get((d["name"], idx), True),
            })

    seen = set(); head_links = []
    for d in decks:
        for link in d["links"]:
            if link not in seen:
                seen.add(link); head_links.append(link)

    css_chunks = [
        f"/* === {d['name']} (scoped) === */\n" + scope_css(d["style"], d["scope"])
        for d in decks
    ]
    scoped_css = "\n\n".join(css_chunks)

    list_items = []
    for d in decks:
        for idx, slide_html in enumerate(d["slides"]):
            list_items.append(_slide_article(d, idx, slide_html, _slide_chrome_select(d, idx)))

    sources_js = "[" + ",".join(f'["{d["name"]}",{len(d["slides"])}]' for d in decks) + "]"
    initial_js = json.dumps(initial, separators=(",", ":"))
    # Bake prior picks.json order so Pass-2 reorder survives a Pass-1 visit.
    if picks and isinstance(picks.get("order"), list):
        prior_order_js = json.dumps(
            [{"src": o["src"], "idx": int(o["idx"]), "keep": bool(o.get("keep", True))} for o in picks["order"]],
            separators=(",", ":"),
        )
    else:
        prior_order_js = "null"
    build_id = _build_id(decks)

    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>client-pdlc — candidate (SELECT)</title>
{chr(10).join(head_links)}
<style>
{CANDIDATE_CSS}
{scoped_css}
</style>
</head>
<body>
<div class="cp-topbar">
  <h1>client-pdlc · candidate</h1>
  <span class="mode">PASS 1 · SELECT</span>
  <span class="stat"><b id="stat-kept">0</b> kept</span>
  <span class="stat"><b id="stat-removed">0</b> removed</span>
  <span class="stat">of <b id="stat-total">0</b></span>
  <div class="spacer"></div>
  <button class="secondary" id="keep-all">Keep all</button>
  <button class="secondary" id="remove-all">Remove all</button>
  <button class="secondary" id="reset">Reset</button>
  <button id="export-picks">Export picks.json</button>
</div>
<div class="cp-help">
  <b>Pass 1 — Selection.</b> Toggle <b>KEEP / REMOVE</b> per slide. Slides stay in source order — reordering happens in Pass 2. State auto-saves to localStorage. When done, click <b>Export picks.json</b>, drop the file into <code>assets/client-pdlc/picks.json</code>, then run <code>python build.py --reorder</code>.
</div>
<div class="cp-list" id="cp-list">
{''.join(list_items)}
</div>
<script>
window.__CP_SOURCES__ = {sources_js};
window.__CP_BUILD_ID__ = {json.dumps(build_id)};
window.__CP_INITIAL__ = {initial_js};
window.__CP_PRIOR_ORDER__ = {prior_order_js};
</script>
<script>
{SELECT_JS}
</script>
</body>
</html>
"""
    out = ROOT / "candidate.html"
    out.write_text(html, encoding="utf-8")
    return out


def build_candidate_reorder() -> Path:
    picks = load_picks()
    if not picks:
        sys.exit("--reorder requires picks.json — run --candidate, curate, Export picks.json into this directory first")

    decks_list = [parse_deck(name, path) for name, path in SOURCES]
    decks = {d["name"]: d for d in decks_list}

    # split picks into kept (in picks.json order) and removed (preserved)
    kept = []
    removed = []
    for o in picks.get("order", []):
        entry = {"src": o["src"], "idx": int(o["idx"])}
        if o.get("keep"):
            kept.append(entry)
        else:
            removed.append(entry)

    if not kept:
        sys.exit("picks.json has 0 kept slides — go back to Pass 1 and keep at least one before reordering")

    total_kept = len(kept)

    list_items = []
    for o in kept:
        d = decks.get(o["src"])
        if not d:
            print(f"warn: unknown source {o['src']!r}, skipping", file=sys.stderr)
            continue
        if not (0 <= o["idx"] < len(d["slides"])):
            print(f"warn: idx {o['idx']} out of range for {o['src']!r}, skipping", file=sys.stderr)
            continue
        slide_html = d["slides"][o["idx"]]
        list_items.append(_slide_article_reorder(
            d, o["idx"], slide_html, _slide_chrome_reorder(d, o["idx"], total_kept)
        ))

    sources_js = "[" + ",".join(f'["{d["name"]}",{len(d["slides"])}]' for d in decks_list) + "]"
    initial_kept_js = json.dumps(kept, separators=(",", ":"))
    removed_js = json.dumps(removed, separators=(",", ":"))
    build_id = _build_id(decks_list)

    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>client-pdlc — candidate (REORDER)</title>
<style>
{CANDIDATE_CSS}
</style>
</head>
<body class="mode-reorder">
<div class="cp-topbar">
  <h1>client-pdlc · candidate</h1>
  <span class="mode reorder">PASS 2 · REORDER</span>
  <span class="stat"><b id="stat-total">0</b> kept slides</span>
  <span class="stat">({len(removed)} removed, hidden)</span>
  <div class="spacer"></div>
  <button class="secondary" id="reset">Reset order</button>
  <button id="export-picks">Export picks.json</button>
</div>
<div class="cp-help">
  <b>Pass 2 — Reorder · 4-column grid.</b> Drag a tile, click <kbd>▲</kbd>/<kbd>▼</kbd>, or type a target position into the number box (then press Enter) to move a slide there. State auto-saves. When done, click <b>Export picks.json</b>, drop into <code>assets/client-pdlc/picks.json</code>, then run <code>python build.py --final</code>. To re-open selection, run <code>python build.py --candidate</code>.
</div>
<div class="cp-list" id="cp-list">
{''.join(list_items)}
</div>
<script>
window.__CP_SOURCES__ = {sources_js};
window.__CP_BUILD_ID__ = {json.dumps(build_id)};
window.__CP_INITIAL_KEPT__ = {initial_kept_js};
window.__CP_REMOVED__ = {removed_js};
</script>
<script>
{REORDER_JS}
</script>
</body>
</html>
"""
    out = ROOT / "candidate.html"
    out.write_text(html, encoding="utf-8")
    return out


# ---------------------------------------------------------------------------
# Decorations (title slide, agenda, section dividers) for the final deck
# ---------------------------------------------------------------------------
# Visual language matches agentic-delivery's `.title-slide` and `.divider`
# slide classes. Self-contained CSS — no dependency on any source deck's
# stylesheet, so the decoration slides render correctly even if the user's
# curation includes zero agentic-delivery content.

CHAPTERS = [
    # No anchor → inserted right after the agenda (no kept slide to consume).
    {"num": "01", "title": "Agentic PDLC Overview", "anchor": None,
     "lead": "What the operating model is, what it changes, and why the regulated stack benefits first."},
    # `replace` chapters consume their anchor kept-slide and emit the divider in its place
    # (the source-deck divider is dropped because we're issuing a unified one).
    {"num": "02", "title": "What is Agent Engineering?", "anchor": ("agentic-delivery", 8), "replace": True,
     "lead": "Above autocomplete-with-chat. The conductor, the orchestra, the score, and the six layers of guardrails."},
    {"num": "03", "title": "Sample Project Overview & Strategy", "anchor": ("project-overview", 2), "replace": True,
     "lead": "PDLC_DEMO · PainEase PCA Advanced — the device, the regulatory strategy, and the deliverables shape."},
    {"num": "04", "title": "Project Shape & Capabilities", "anchor": ("project-overview", 9), "replace": True,
     "lead": "Operating rules, project-level skills, and persona agents — the machinery underneath the work."},
    {"num": "05", "title": "Quality & Process", "anchor": ("project-overview", 23), "replace": True,
     "lead": "How the guardrails actually work — hooks, traces, and the audit surface a regulator can read."},
    {"num": "06", "title": "Humans in Charge", "anchor": ("project-overview", 38), "replace": True,
     "lead": "Where the handoff lands. Agents advise; humans decide; the regulated record is human-attributed."},
    {"num": "07", "title": "The Project Console", "anchor": ("project-overview", 51), "replace": True,
     "lead": "The single pane: advisors, documents, task activity, dashboards, trace, strategy review, the FDA package, gap analyses, team metrics, and project settings.",
     # Subsections carry no `anchor` — they no longer inject divider slides.
     # They drive the agenda card's sub-list AND the §7 screenshot slides
     # (one slide per section: compact title strip + console screenshot).
     "subsections": [
        {"num": "01", "title": "Landing Page",       "image": "console-landing.png",
         "caption": "One local console over the same agents and artifacts the engineering environment works with."},
        {"num": "02", "title": "Agents",             "image": "console-agents.png",
         "caption": "31 grounded advisors — every answer cites the project document it came from."},
        {"num": "03", "title": "Documents Explorer", "image": "console-documents.png",
         "caption": "The whole project tree, rendered and summarized, with an advisor drawer on every file."},
        {"num": "04", "title": "Tasks",              "image": "console-tasks.png",
         "caption": "What's moving and what's open — derived from the task docs, not a separate tracker."},
        {"num": "05", "title": "Submission Tracker", "image": "console-dashboards.png",
         "caption": "154 deliverables across Q-Sub and 510(k)+PCCP scopes — status editable in the browser."},
        {"num": "06", "title": "Trace Matrix",       "image": "console-trace-matrix.png",
         "caption": "All ten DHFs traced across six layers, from user needs to risk."},
        {"num": "07", "title": "Strategy Review",    "image": "console-strategy.png",
         "caption": "Eight strategy domains as a live review surface — accept, reject, or modify harvested proposals."},
        {"num": "08", "title": "Submission Package", "image": "console-submission.png",
         "caption": "The FDA-facing package: composition manifests, documents, and open questions in one place."},
        {"num": "09", "title": "Gap Analysis",       "image": "console-gap-analysis.png",
         "caption": "The project critiques its own work product against standards, with advisor panels per finding."},
        {"num": "10", "title": "Value & ROI",        "image": "console-metrics.png",
         "caption": "104 tasks · 920–3,050 modeled person-hours saved vs ~$623 token spend — modeled, uncalibrated."},
        {"num": "11", "title": "Project Settings",   "image": "console-setup.png",
         "caption": "Every skill, agent, hook, and registry audited against the project manifest."},
        {"num": "12", "title": "Workflows",          "image": "console-workflows.png",
         "caption": "Composed automation with honest readiness labels: live, prototype, or proposed."},
     ]},
]

# After this kept slide is emitted, append the §7 console-section screenshot
# slides (one per CHAPTERS[-1]["subsections"] entry). PO #58 ("How the console
# relates to Claude Code") is the §7 intro slide; the screenshots follow it.
SLIDE_APPENDS = {
    ("project-overview", 66): "console-sections",
}

# Replace the original "Agenda" slide (project-overview #1) with our generated agenda.
AGENDA_REPLACES = ("project-overview", 1)

# Slide moves (anchor-relative reordering) — none active after the sp6500
# source deck was retired in task ben/070 (the only move was a KOL slide
# from sp6500). Keep the structure so future moves drop in cleanly.
SLIDE_MOVES: dict = {}


# Per-slide text-level rewrites — client-facing language scrub. Each entry maps
# a source-anchor key to a list of (search, replace) pairs applied to that
# slide's raw HTML before emitting. Use exact substrings (no regex) so
# review is straightforward.
SLIDE_PATCHES = {
    # PO #4 — "Regulatory strategy at a glance". Replace raw repo paths with
    # plain-language pointers; internal file paths read as a leak on a
    # client-facing deck (the source doc keeps the precise paths).
    ("project-overview", 4): [
        ("See <code>docs/project/strategies/regulatory-strategy.md</code> §1 <em>Filing Scope: PCA Device Alone</em>.",
         "See the regulatory strategy, §1 <em>Filing Scope: PCA Device Alone</em>."),
        ("See regulatory-strategy.md §1 <em>Filing Strategy — Critical-Requirement Carve-out</em>.",
         "See the regulatory strategy, §1 <em>Filing Strategy — Critical-Requirement Carve-out</em>."),
        ("see <code>docs/project/submissions/510k/composition-manifest.md</code>",
         "see the 510(k) composition manifest"),
    ],
    # PO #8 — "Key deliverables" tiles: strip repo-path parentheticals.
    ("project-overview", 8): [
        ("(<code>docs/project/submissions/qsub/</code>) — ", ""),
        ("(<code>docs/project/submissions/510k/</code>) — ", ""),
        ("(<code>docs/project/submissions/pccp/</code>) — ", ""),
        ("per DHF (<code>docs/project/dhfs/&lt;dhf&gt;/design-controls/trace-matrix/</code>) — ", "per DHF — "),
        ("(<code>docs/project/dhfs/pca-device/risk-management/</code>) — ", ""),
    ],
    # PO #11 / #15 / #28 — replace literal HTML-comment marker syntax with
    # plain language; the mechanism matters to a client, the sigil doesn't.
    ("project-overview", 11): [
        ("as <code>&lt;!-- STRATEGY CONTENT: domain, topics --&gt;</code> / <code>&lt;!-- LESSONS LEARNED: category --&gt;</code> blocks",
         "as tagged strategy / lessons blocks"),
    ],
    ("project-overview", 15): [
        ("Harvests <code>&lt;!-- STRATEGY CONTENT: domain --&gt;</code> blocks",
         "Harvests tagged strategy blocks"),
    ],
    ("project-overview", 28): [
        ("as <code>&lt;!-- STRATEGY CONTENT: domain --&gt;</code> blocks",
         "as tagged strategy blocks"),
    ],
    # AD #6 — "Three external signals". Drop internal delivery-firm framing
    # from the "Cost of waiting" card; rewrite for the client/program reader.
    # Source has an inner `<span style="color: white">18–24 months behind</span>`
    # we must not split, so the patches break the sentence into three chunks
    # around that span.
    ("agentic-delivery", 6): [
        # "Cost of waiting" callout: center it and line its width up with the
        # stat cards above (was left-pinned at a narrower max-width).
        ("align-self: flex-start; max-width: min(95vw, 1100px)",
         "align-self: center; width: 100%; max-width: min(95vw, 1200px)"),
        ("A delivery firm that waits will be",
         "An organization that delays adoption will be"),
        ("competitors who front-fund",
         "peers that invest now"),
        ("The asymmetry is not linear; it compounds.",
         "The asymmetry compounds — every month widens the gap."),
    ],
    # AD #13 — full slide-content rewrite. The original was a 4-row table where
    # bucket 4 (ours) appeared as just another row, which buried the "wrapper vs
    # purpose-built" thesis. New layout splits the slide into two panels and
    # leads with a one-sentence thesis as the H2. See `_AD13_NEW_BODY` below.
    ("agentic-delivery", 13): [
        ("The Competitive Frame", "Our Difference"),   # rename the eyebrow
        # Body replacement (h2 + table + bottom quote → two-panel layout)
        # The find string below is the exact source body — captured verbatim.
        (_AD13_OLD_BODY := """<h2 class="reveal">The four buckets of "agentic" claims.</h2>
        <table class="compact-table reveal">
            <thead><tr><th style="width: 22%">Bucket</th><th style="width: 36%">What it actually is</th><th>Why it fails in regulated work</th></tr></thead>
            <tbody>
                <tr><td>1 · Code-completion rebranded</td><td>Copilot, Cursor, Codeium. Inline completions. Speeds up <em>typing</em>.</td><td>No process enforcement. No domain grounding. No audit trail beyond a git diff.</td></tr>
                <tr><td>2 · Chatbot bolted onto delivery</td><td>"We added an LLM to our workflow." Model-in-the-loop, not a system.</td><td>Work product unchanged. Only input method changed.</td></tr>
                <tr><td>3 · Vendor-locked agentic platform</td><td>Big-SI agentic studios. Closed product, vendor-rented capability.</td><td>Audit trail in the vendor's hands, not the customer's. Capability rented, not owned.</td></tr>
                <tr style="background: rgba(255, 87, 34, 0.08)"><td><strong>4 · Agentic project shape <em>as the deliverable</em></strong></td><td><strong>Every artifact, hook, skill, agent, rule, and registry lives in the customer's repository — versioned, reusable, auditable.</strong></td><td><strong>This is the discipline.</strong></td></tr>
            </tbody>
        </table>
        <p class="lead reveal" style="margin-top: clamp(0.6rem, 1.3vh, 1rem); font-size: clamp(0.8rem, 1.35vw, 1.05rem); max-width: 75ch">"Most teams have an LLM in their workflow. <strong>We have a workflow that is itself the LLM operating model</strong> — versioned, audit-trailed, domain-ground, and reusable across projects."</p>""",
         """<h2 class="reveal">Most &ldquo;agentic&rdquo; MedTech is a wrapper.<br/><span style="color: var(--card-orange)">Ours is a purpose-built harness.</span></h2>
        <div class="od-split reveal">
          <div class="od-panel od-panel-market">
            <div class="od-panel-head">
              <div class="od-panel-title">WHAT VENDORS SHIP</div>
              <div class="od-panel-sub">Context and a UI wrapped around someone else&rsquo;s model.</div>
            </div>
            <div class="od-cards">
              <div class="od-card">
                <div class="od-card-title">1 &middot; Code-completion rebranded</div>
                <p>Copilot, Cursor, Codeium with a vendor wrapper. <strong>Productive on the keystroke &mdash; blind to everything else.</strong> No idea your work product needs IEC 62304 traceability, that an audit trail must name a human, or that an output is going into a 510(k).</p>
              </div>
              <div class="od-card">
                <div class="od-card-title">2 &middot; Chatbot on a data lake</div>
                <p>RAG over your docs. <strong>No provenance from answer to source</strong> &mdash; you can&rsquo;t tell which document fragment shaped the response. Embeddings shift on every rebuild; data ages silently. <em>Same question, different answer next month.</em> No full-context grounding &mdash; just whatever the nearest-neighbor lookup returns.</p>
              </div>
              <div class="od-card">
                <div class="od-card-title">3 &middot; Hosted autonomous-agent studio</div>
                <p>A closed-box agent running in someone else&rsquo;s cloud. <strong>The audit trail is theirs, not yours.</strong> <strong>Not purpose-built for MedTech</strong> &mdash; no IEC 62304, ISO 14971, or DHF grounding. <strong>Not portable</strong> &mdash; change vendors and both the capability and your history walk away.</p>
              </div>
            </div>
          </div>
          <div class="od-panel od-panel-ours">
            <div class="od-panel-head">
              <div class="od-panel-title">WHAT WE BUILT</div>
              <div class="od-panel-sub">A purpose-built MedTech agentic harness &mdash; versioned, audited, and yours.</div>
            </div>
            <ul class="od-bullets">
              <li><strong>Domain-grounded.</strong> IEC 62304, ISO 14971, and ISO 13485 encoded directly into skills, agents, hooks, and rules — with a Part 11-aware publishing flow into the formal review system.</li>
              <li><strong>Audit-trailed by construction.</strong> Every decision attributable; every change links design inputs to verification to the DHF record.</li>
              <li><strong>Lives in your repository.</strong> Versioned alongside the device. No vendor tenant. No platform you have to log into.</li>
              <li><strong>Built for regulated delivery.</strong> DHF-shaped outputs, submission-ready by construction, reusable across programs in your portfolio.</li>
            </ul>
          </div>
        </div>"""),
    ],
    # AD #14 — "Six capabilities" matrix. Mirror the AD #13 reframing so the
    # column headers and the row labels match the new vocabulary, broaden the
    # productivity row beyond "coding", and recast the "customer's hands /
    # customer repository / cross-project" framing into client-facing "your
    # hands / your repository / cross-program" language.
    ("agentic-delivery", 14): [
        # Column headers — align with slide 5's bucket names
        ("Chatbot bolted<br/>onto delivery",
         "Chatbot on a<br/>data lake"),
        ("Vendor-locked<br/>platform",
         "Hosted autonomous-<br/>agent studio"),
        ("Agentic project<br/>shape <em>as deliverable</em>",
         "Purpose-built<br/>MedTech harness"),
        # Row 1 — broader than just coding
        ("Speeds up engineer typing",
         "Productivity gains across coding, documentation, and analysis"),
        # Possessive language — client-facing
        ("Audit trail in <em>customer's</em> hands",
         "Audit trail in <em>your</em> hands"),
        ("Lives in customer repository · versioned",
         "Lives in your repository · versioned"),
        ("Cross-project IP propagation (registry)",
         "Cross-program IP propagation (registry)"),
    ],
    # AD #16 — "Specs first." The phrase "across customer programs" treats the
    # reader as a firm with a client portfolio. Neutralize.
    ("agentic-delivery", 16): [
        ("propagatable across customer programs", "propagatable across program work"),
        # "The invariant" callout: center it and line its width up with the
        # pyramid content above (same fix as AD #6's "Cost of waiting").
        ("align-self: flex-start; max-width: min(95vw, 1100px)",
         "align-self: center; width: 100%; max-width: min(95vw, 1200px)"),
    ],
    # AD #11 — "SDLC sits inside PDLC" — bottom caption was whitepaper-voiced
    # ("our delivery", "what this paper is about"). Rewrite client-facing.
    ("agentic-delivery", 11): [
        ('Most "AI in our delivery" pitches treat these three as the same thing — they aren\'t. The team\'s tooling (the dashed arrow from outside) is what this paper is about.',
         'Most "AI in delivery" pitches conflate these three. The agentic PDLC harness operates on the team\'s working method — the dashed arrow that enters the lifecycle from outside.'),
    ],
    # AD #9 — "A bulb gives you light. Optics give you a laser." The closer
    # referenced "the product, the moat, and the IP" — internal-vendor framing.
    # Name the GlobalLogic Agentic PDLC harness directly so the client reader
    # knows which "optics" is being claimed.
    ("agentic-delivery", 9): [
        ("<strong>The product, the moat, and the IP are the optics — not the bulb.</strong>",
         "<strong>The GlobalLogic Agentic PDLC harness is the optics — not the bulb.</strong>"),
    ],
}


# Slides inserted BEFORE a kept-anchor slide is emitted. Used for one-off
# "concept" introductions that frame the content slides that follow. Keyed by
# the anchor slide's (src, idx); value is the concept-slide spec.
INTERSTITIALS = {
    # Before PO #3 ("What PP3500 is") — first content slide of Section 3.
    # Frames the section's slides as outputs of the strategy harness.
    ("project-overview", 3): {
        "data_id": "strategy-intro",
        "eyebrow": "STRATEGY HARNESS · IN ACTION",
        "h2": "Strategies are managed artifacts — the basis for everything downstream.",
        "lead": "Regulatory, clinical, architectural, post-market — each strategy is a curated, versioned artifact in the harness, the canonical reference every downstream document derives from.",
        "callout": "What follows are generated outputs from the sample project — a working strategy harness in action.",
    },
}


# Custom-authored replacement slides. Keyed by the kept anchor slide's
# (src, idx); the anchor is consumed and a bespoke deco slide is emitted in
# its place (same pattern as `replace` chapters). Used where a harvested
# source slide is the right *position* but the wrong *presentation* — e.g.
# a catalog mosaic collapsed into one authored overview, or a tile grid
# replaced by an illustration.
CUSTOM_REPLACES = {
    ("project-overview", 8): "key-deliverables",
    ("project-overview", 11): "operating-rules",
    ("project-overview", 15): "skills-overview",
    ("project-overview", 20): "agents-overview",
    ("project-overview", 25): "skills-catalog",
    ("project-overview", 35): "adds-up-to",
}


# Regex to strip "Variation X · " (or "Variation X — ", "Variation X - ") prefixes
# from eyebrow / heading text in any slide. The variants used in source decks
# include "Variation A · ", "Variation B — ", "Variation C - ".
_VARIATION_PREFIX_RE = re.compile(r"Variation\s+[A-Z]+\s*[·\-—–]\s*")


DECO_CSS = """
/* ===== client-pdlc decorations: title / agenda / dividers ===== */
.deco-slide {
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  position: relative;
  background: radial-gradient(circle at 20% 30%, #2a1810 0%, #181820 40%, #0e0e10 100%);
  color: #ffffff;
  font-family: "Space Grotesk", "Helvetica Neue", sans-serif;
  --orange: #FF5722;
  --muted: #8a8a99;  /* was #6b6b7d — 3.7:1 on #0e0e10 failed WCAG AA for small text */
  --secondary: #a8a8b3;
  --display: "Archivo Black", "Helvetica Neue", sans-serif;
  --mono: "JetBrains Mono", monospace;
  --pad: clamp(1.25rem, 4vw, 4rem);
}
.deco-slide::before {
  content: "";
  position: absolute; inset: 0;
  background-image:
    linear-gradient(rgba(255,255,255,0.04) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,0.04) 1px, transparent 1px);
  background-size: clamp(40px, 5vw, 80px) clamp(40px, 5vw, 80px);
  pointer-events: none;
  z-index: 1;
}
.deco-slide .chrome {
  position: absolute;
  top: clamp(0.75rem, 2vh, 1.25rem);
  left: var(--pad); right: var(--pad);
  display: flex; justify-content: space-between; align-items: center;
  font-size: clamp(0.72rem, 0.9vw, 0.8rem);
  font-family: var(--mono);
  letter-spacing: 0.06em;
  z-index: 5;
}
.deco-slide .chrome .num    { color: var(--orange); font-weight: 500; }
.deco-slide .chrome .brand  { color: var(--secondary); }
.deco-slide .chrome .crumb  { color: var(--muted); }
.deco-slide .content {
  flex: 1;
  display: flex; flex-direction: column; justify-content: center;
  padding: var(--pad);
  position: relative; z-index: 2;
  max-height: 100%; overflow: hidden;
}

/* ---- TITLE SLIDE ---- */
.deco-title .content {
  justify-content: center; align-items: flex-start;
  gap: clamp(1.2rem, 3vh, 2rem);
}
.deco-title .eyebrow {
  font-family: var(--display);
  color: var(--orange);
  font-size: clamp(0.9rem, 1.4vw, 1.1rem);
  letter-spacing: 0.18em;
}
.deco-title h1 {
  font-family: var(--display);
  font-size: clamp(2.5rem, 8vw, 7rem);
  line-height: 0.92;
  max-width: 20ch;
  margin: 0;
}
.deco-title h1 .accent { color: var(--orange); display: inline-block; }
.deco-title .lead {
  font-size: clamp(0.95rem, 1.7vw, 1.35rem);
  color: var(--secondary);
  line-height: 1.5;
  max-width: 70ch;
  margin: 0;
}
.deco-title .lead strong { color: var(--orange); }
.deco-title .meta {
  display: flex; gap: clamp(1rem, 3vw, 2.5rem);
  font-family: var(--mono);
  font-size: clamp(0.65rem, 1vw, 0.85rem);
  color: var(--secondary);
  letter-spacing: 0.04em;
  margin-top: clamp(0.5rem, 2vh, 1.5rem);
}
.deco-title .meta .name { color: var(--orange); }
.deco-title .signal-block {
  position: absolute;
  bottom: 0; right: 0;
  width: clamp(180px, 28vw, 360px);
  height: clamp(180px, 28vw, 360px);
  background: var(--orange);
  transform: translate(20%, 20%) rotate(8deg);
  box-shadow: -30px -30px 80px -10px rgba(255, 87, 34, 0.55);
  z-index: 1;
}
.deco-title .logo {
  position: absolute;
  top: clamp(2.5rem, 6vh, 3.5rem);
  right: var(--pad);
  height: clamp(28px, 4vh, 44px);
  width: auto;
  filter: invert(1) brightness(1.05);
  opacity: 0.92;
  z-index: 5;
}
.deco-title .legal {
  position: absolute;
  bottom: clamp(1rem, 3vh, 1.5rem);
  left: var(--pad);
  max-width: 55ch;
  display: flex; flex-direction: column;
  gap: clamp(0.2rem, 0.5vh, 0.4rem);
  font-family: var(--mono);
  font-size: clamp(0.6rem, 0.85vw, 0.75rem);
  color: var(--muted);
  letter-spacing: 0.08em; text-transform: uppercase;
  z-index: 5;   /* above the signal-block */
}
.deco-title .legal .nda { color: var(--orange); font-weight: 700; }
.deco-title .legal .sep { color: rgba(255,255,255,0.18); margin: 0 0.4em; }

/* ---- AGENDA SLIDE ---- */
.deco-agenda .content {
  justify-content: center;
  gap: clamp(0.8rem, 2vh, 1.4rem);
}
.deco-agenda h2 {
  font-family: var(--display);
  font-size: clamp(1.5rem, 4vw, 3rem);
  margin: 0 0 clamp(0.6rem, 1.6vh, 1.2rem) 0;
}
.deco-agenda .agenda-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(28ch, 100%), 1fr));
  gap: clamp(0.6rem, 1.4vw, 1rem);
  max-width: 110ch;
}
.deco-agenda .chapter-card {
  background: rgba(255, 255, 255, 0.025);
  border-left: 3px solid var(--orange);
  padding: clamp(0.7rem, 1.4vw, 1rem) clamp(0.9rem, 1.6vw, 1.2rem);
  border-radius: 2px;
}
.deco-agenda .chapter-card .ch-num {
  font-family: var(--display);
  color: var(--orange);
  font-size: clamp(1.4rem, 2.6vw, 2rem);
  line-height: 1;
  margin-bottom: clamp(0.15rem, 0.5vh, 0.35rem);
}
.deco-agenda .chapter-card .ch-title {
  font-size: clamp(0.95rem, 1.4vw, 1.15rem);
  font-weight: 600;
  line-height: 1.25;
  margin-bottom: clamp(0.2rem, 0.6vh, 0.45rem);
}
.deco-agenda .chapter-card .ch-subs {
  font-family: var(--mono);
  font-size: clamp(0.65rem, 0.9vw, 0.8rem);
  color: var(--muted);
  letter-spacing: 0.04em;
  line-height: 1.5;
}
.deco-agenda .chapter-card .ch-subs span:not(:last-child)::after {
  content: " · ";
  color: rgba(255, 255, 255, 0.18);
}

/* ---- SECTION DIVIDER ---- */
.deco-divider .content {
  justify-content: center; align-items: flex-start;
  gap: clamp(0.7rem, 2vh, 1.4rem);
}
.deco-divider .section-num {
  font-family: var(--display);
  font-size: clamp(4rem, 18vw, 18rem);
  line-height: 0.85;
  color: var(--orange);
  margin-left: -0.05em;
}
.deco-divider h2 {
  font-family: var(--display);
  font-size: clamp(1.5rem, 5vw, 4rem);
  line-height: 1;
  max-width: 22ch;
  margin: 0;
}
.deco-divider .lead {
  font-size: clamp(0.95rem, 1.7vw, 1.35rem);
  color: var(--secondary);
  line-height: 1.5;
  max-width: 60ch;
  margin: 0;
}
.deco-divider .eyebrow {
  font-family: var(--mono);
  color: var(--orange);
  font-size: clamp(0.75rem, 1.05vw, 0.9rem);
  letter-spacing: 0.14em;
  text-transform: uppercase;
}
.deco-subsection .section-num {
  font-size: clamp(3rem, 12vw, 12rem);
  color: var(--secondary);
}
.deco-subsection .section-num .parent {
  color: var(--muted);
  font-size: 0.45em;
  margin-right: 0.15em;
  vertical-align: 0.45em;
}

/* ---- CONCEPT SLIDE (interstitial, e.g. "Strategy Harness in Action") ---- */
.deco-concept .content {
  justify-content: center;
  align-items: flex-start;
  gap: clamp(0.7rem, 1.8vh, 1.4rem);
  max-width: 76ch;
}
.deco-concept .eyebrow {
  font-family: var(--mono);
  color: var(--orange);
  font-size: clamp(0.75rem, 1.05vw, 0.9rem);
  letter-spacing: 0.16em;
  text-transform: uppercase;
}
.deco-concept h2 {
  font-family: var(--display);
  font-size: clamp(1.5rem, 3.6vw, 3rem);
  line-height: 1.1;
  max-width: 22ch;
  margin: 0;
  color: #ffffff;
}
.deco-concept .lead {
  font-size: clamp(0.95rem, 1.55vw, 1.3rem);
  color: var(--secondary);
  line-height: 1.5;
  margin: 0;
  max-width: 68ch;
}
.deco-concept .callout {
  margin-top: clamp(0.7rem, 1.4vh, 1.2rem);
  padding-top: clamp(0.55rem, 1.1vh, 0.9rem);
  border-top: 1px solid rgba(255,255,255,0.12);
  font-family: var(--mono);
  font-size: clamp(0.85rem, 1.2vw, 1.05rem);
  color: var(--orange);
  letter-spacing: 0.02em;
  line-height: 1.5;
  max-width: 70ch;
}
.deco-concept .callout::before {
  content: "↓  ";
  font-weight: bold;
}

/* ---- CONSOLE SECTION SCREENSHOT SLIDE ---- */
.deco-screenshot .content {
  padding-top: clamp(2.6rem, 6vh, 4rem);
  padding-bottom: clamp(1.2rem, 3vh, 2.2rem);
  justify-content: flex-start;
  gap: clamp(0.4rem, 1vh, 0.8rem);
}
.deco-screenshot .shot-head {
  display: flex;
  align-items: baseline;
  gap: clamp(0.6rem, 1.5vw, 1.3rem);
  border-bottom: 1px solid rgba(255,255,255,0.12);
  padding-bottom: clamp(0.4rem, 0.9vh, 0.7rem);
}
.deco-screenshot .shot-num {
  font-family: var(--display);
  color: var(--orange);
  font-size: clamp(1.3rem, 2.6vw, 2.2rem);
  line-height: 1;
}
.deco-screenshot .shot-title {
  font-family: var(--display);
  color: #ffffff;
  font-size: clamp(1.3rem, 2.6vw, 2.2rem);
  line-height: 1;
}
.deco-screenshot .shot-eyebrow {
  margin-left: auto;
  font-family: var(--mono);
  color: var(--muted);
  font-size: clamp(0.72rem, 0.85vw, 0.8rem);
  letter-spacing: 0.14em;
  text-transform: uppercase;
}
.deco-screenshot .shot-caption {
  margin-top: clamp(0.35rem, 0.9vh, 0.7rem);
  font-family: var(--mono);
  font-size: clamp(0.78rem, 1vw, 0.95rem);
  color: var(--secondary);
  letter-spacing: 0.02em;
  text-align: center;
}
#cp-progress {
  position: fixed; top: 0; left: 0; height: 3px; width: 0;
  background: linear-gradient(90deg, #FF5722, #FFB400);
  z-index: 99; transition: width 0.25s ease;
}
@media print { #cp-progress { display: none; } }

/* ---- CUSTOM SLIDES (authored replacements) — shared scaffold ---- */
.deco-custom .content {
  position: relative; z-index: 2; flex: 1;
  display: flex; flex-direction: column; justify-content: center;
  padding: clamp(2.6rem, 6vh, 4rem) var(--pad) clamp(1.2rem, 3vh, 2rem);
  gap: clamp(0.7rem, 1.6vh, 1.2rem);
}
.deco-custom .eyebrow {
  font-family: var(--mono); font-size: clamp(0.72rem, 0.9vw, 0.8rem);
  letter-spacing: 0.22em; text-transform: uppercase; color: var(--orange);
}
.deco-custom h2 {
  font-family: var(--display); font-size: clamp(1.6rem, 3.2vw, 2.7rem);
  line-height: 1.05; margin: 0;
}
.deco-custom .lead { color: var(--secondary); font-size: clamp(0.9rem, 1.25vw, 1.1rem); max-width: 62rem; }
.deco-custom .takeaway {
  border-left: 3px solid var(--orange);
  background: rgba(255, 87, 34, 0.08);
  padding: clamp(0.5rem, 1.2vh, 0.8rem) clamp(0.8rem, 1.6vw, 1.2rem);
  font-size: clamp(0.9rem, 1.2vw, 1.1rem);
}
.deco-custom .takeaway strong { color: var(--orange); }

/* key-deliverables: pathway rail + evidence backbone */
.dlv-rail { display: flex; align-items: stretch; gap: 0; }
.dlv-node {
  flex: 1; border: 1px solid rgba(255,255,255,0.16); border-radius: 10px;
  background: rgba(255,255,255,0.035);
  padding: clamp(0.7rem, 1.6vh, 1.1rem) clamp(0.8rem, 1.6vw, 1.2rem);
  display: flex; flex-direction: column; gap: 0.35rem;
}
.dlv-node.lit { border-color: rgba(255,87,34,0.55); background: rgba(255,87,34,0.07); }
.dlv-step { font-family: var(--mono); font-size: clamp(0.68rem, 0.85vw, 0.78rem); color: var(--muted); letter-spacing: 0.14em; }
.dlv-name { font-family: var(--display); font-size: clamp(1.05rem, 1.8vw, 1.5rem); }
.dlv-desc { color: var(--secondary); font-size: clamp(0.8rem, 1.05vw, 0.95rem); line-height: 1.35; }
.dlv-arrow {
  align-self: center; padding: 0 clamp(0.4rem, 1vw, 0.9rem);
  color: var(--orange); font-family: var(--display);
  font-size: clamp(1.2rem, 2.2vw, 1.9rem);
}
.dlv-flow { display: flex; justify-content: space-around; color: var(--orange); font-size: clamp(1rem, 1.8vw, 1.5rem); line-height: 1; }
.dlv-backbone {
  display: flex; gap: clamp(0.8rem, 1.8vw, 1.4rem);
  border: 1px solid rgba(255,180,0,0.35); border-radius: 10px;
  background: rgba(255,180,0,0.05);
  padding: clamp(0.7rem, 1.6vh, 1.1rem) clamp(0.8rem, 1.6vw, 1.2rem);
}
.dlv-backbone .bb-cell { flex: 1; }
.dlv-backbone .bb-tag { font-family: var(--mono); font-size: clamp(0.68rem, 0.85vw, 0.78rem); color: #FFB400; letter-spacing: 0.14em; }
.dlv-backbone .bb-name { font-family: var(--display); font-size: clamp(0.95rem, 1.5vw, 1.25rem); margin: 0.2rem 0; }
.dlv-backbone .bb-desc { color: var(--secondary); font-size: clamp(0.78rem, 1vw, 0.92rem); line-height: 1.35; }

/* skills-overview / agents-overview: grouped chip columns */
.ovw-groups { display: flex; gap: clamp(0.9rem, 2vw, 1.6rem); align-items: stretch; }
.ovw-col { flex: 1; display: flex; flex-direction: column; gap: clamp(0.45rem, 1vh, 0.7rem); }
.ovw-head {
  font-family: var(--mono); font-size: clamp(0.72rem, 0.9vw, 0.8rem);
  letter-spacing: 0.18em; text-transform: uppercase; color: var(--orange);
  border-bottom: 2px solid rgba(255,87,34,0.5); padding-bottom: 0.35rem;
}
.ovw-head .count { color: var(--muted); letter-spacing: 0.05em; }
.ovw-chip {
  border: 1px solid rgba(255,255,255,0.13); border-radius: 8px;
  background: rgba(255,255,255,0.03);
  padding: clamp(0.45rem, 1vh, 0.7rem) clamp(0.6rem, 1.2vw, 0.9rem);
}
.ovw-chip .c-name { font-family: var(--mono); color: #fff; font-size: clamp(0.82rem, 1.05vw, 0.95rem); font-weight: 500; }
.ovw-chip .c-tag { color: var(--secondary); font-size: clamp(0.76rem, 0.95vw, 0.88rem); line-height: 1.3; margin-top: 0.15rem; }
.ovw-chip.mini { padding: clamp(0.3rem, 0.7vh, 0.5rem) clamp(0.55rem, 1.1vw, 0.8rem); }
.ovw-grid3 {
  display: grid; grid-template-columns: repeat(3, 1fr);
  gap: clamp(0.5rem, 1.2vh, 0.9rem) clamp(0.6rem, 1.4vw, 1.1rem);
}
.ovw-grid4 {
  display: grid; grid-template-columns: repeat(4, 1fr);
  gap: clamp(0.5rem, 1.2vh, 0.9rem) clamp(0.6rem, 1.4vw, 1.1rem);
}
.deco-screenshot .shot-frame {
  flex: 1;
  min-height: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: clamp(0.3rem, 0.8vh, 0.6rem);
}
.deco-screenshot .shot-frame img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  border: 1px solid rgba(255,255,255,0.14);
  border-radius: 5px;
  box-shadow: 0 24px 70px -18px rgba(0,0,0,0.75);
}

/* ===== AD#13 — Our Difference two-panel layout (SLIDE_PATCHES body) ===== */
.src-agentic-delivery .od-split {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: clamp(0.7rem, 1.6vw, 1.4rem);
  flex: 1;
  min-height: 0;
  margin-top: clamp(0.4rem, 1vh, 0.9rem);
}
.src-agentic-delivery .od-panel {
  background: rgba(255, 255, 255, 0.025);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 4px;
  padding: clamp(0.7rem, 1.3vw, 1.2rem);
  display: flex; flex-direction: column;
  min-height: 0;
}
.src-agentic-delivery .od-panel-market { border-left: 3px solid #6b6b7d; }
.src-agentic-delivery .od-panel-ours {
  border-left: 3px solid #FF5722;
  background: linear-gradient(135deg, rgba(255, 87, 34, 0.06), rgba(255, 87, 34, 0.01));
}
.src-agentic-delivery .od-panel-head {
  margin-bottom: clamp(0.5rem, 1vh, 0.9rem);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  padding-bottom: clamp(0.35rem, 0.7vh, 0.6rem);
}
.src-agentic-delivery .od-panel-title {
  font-family: "JetBrains Mono", monospace;
  font-size: clamp(0.7rem, 1.05vw, 0.9rem);
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: #ffffff;
  font-weight: 600;
}
.src-agentic-delivery .od-panel-ours .od-panel-title { color: #FF5722; }
.src-agentic-delivery .od-panel-sub {
  font-size: clamp(0.7rem, 0.95vw, 0.85rem);
  color: #a8a8b3;
  margin-top: clamp(0.15rem, 0.3vh, 0.3rem);
  line-height: 1.4;
}
.src-agentic-delivery .od-cards {
  display: flex; flex-direction: column;
  gap: clamp(0.35rem, 0.7vh, 0.6rem);
  flex: 1; min-height: 0;
}
.src-agentic-delivery .od-card {
  background: rgba(0, 0, 0, 0.22);
  padding: clamp(0.45rem, 0.9vw, 0.8rem);
  border-radius: 3px;
}
.src-agentic-delivery .od-card-title {
  font-size: clamp(0.78rem, 1.1vw, 0.95rem);
  font-weight: 700;
  color: #ffffff;
  margin-bottom: clamp(0.12rem, 0.3vh, 0.25rem);
  font-family: "JetBrains Mono", monospace;
  letter-spacing: 0.03em;
}
.src-agentic-delivery .od-card p {
  font-size: clamp(0.65rem, 0.92vw, 0.82rem);
  line-height: 1.4;
  color: #a8a8b3;
  margin: 0;
}
.src-agentic-delivery .od-card p strong { color: #ffffff; font-weight: 600; }
.src-agentic-delivery .od-card p em { color: #FFB400; font-style: italic; }

.src-agentic-delivery .od-bullets {
  list-style: none;
  padding: 0; margin: 0;
  display: flex; flex-direction: column;
  gap: clamp(0.5rem, 1.1vh, 1rem);
  flex: 1; min-height: 0;
}
.src-agentic-delivery .od-bullets li {
  font-size: clamp(0.78rem, 1.1vw, 0.95rem);
  line-height: 1.45;
  color: #a8a8b3;
  padding-left: clamp(0.9rem, 1.5vw, 1.3rem);
  position: relative;
}
.src-agentic-delivery .od-bullets li::before {
  content: "▸";
  position: absolute; left: 0;
  color: #FF5722;
  font-weight: bold;
}
.src-agentic-delivery .od-bullets li strong { color: #ffffff; font-weight: 700; }
"""


def _decoration_chrome(num: str, brand: str = "", crumb: str = "© 2026 GlobalLogic") -> str:
    """Unified chrome: page-number left, copyright right. `brand` and `crumb`
    kept as params for legacy callsites but defaults match the new design —
    only the page number changes per slide; the right-side text is the
    GlobalLogic copyright on every slide (except the title, which has no
    chrome — the logo replaces it)."""
    return (
        f'<div class="chrome">'
        f'<span class="num">{num}</span>'
        f'<span class="brand">{_html.escape(brand)}</span>'
        f'<span class="crumb">{_html.escape(crumb)}</span>'
        f'</div>'
    )


# Chrome rewriter for source slides. Replaces the inner contents of the
# slide's `<div class="chrome">...</div>` with the unified pattern: 1-based
# slide-number on the left, "© 2026 GlobalLogic" on the right. Empty `.brand`
# in the middle so flex space-between continues to push the two ends apart.
_CHROME_RE = re.compile(r'(<div\s+class="chrome">)(.*?)(</div>)', re.DOTALL)


def _rewrite_chrome(slide_html: str, position: int) -> str:
    replacement = (
        f'<span class="num">{position:02d}</span>'
        f'<span class="brand"></span>'
        f'<span class="crumb">© 2026 GlobalLogic</span>'
    )
    new_html, n = _CHROME_RE.subn(lambda m: m.group(1) + replacement + m.group(3),
                                  slide_html, count=1)
    return new_html


def _strip_variation_prefix(slide_html: str) -> str:
    """Drop 'Variation A · ' / 'Variation B — ' style prefixes from any text in
    the slide. Preserves the rest of the eyebrow/label after the separator."""
    return _VARIATION_PREFIX_RE.sub("", slide_html)


def _apply_slide_patches(slide_html: str, src: str, idx: int) -> str:
    """Apply per-source-anchor text substitutions from SLIDE_PATCHES."""
    patches = SLIDE_PATCHES.get((src, idx), [])
    for find, repl in patches:
        slide_html = slide_html.replace(find, repl)
    return slide_html


def _transform_source_slide(slide_html: str, src: str, idx: int, position: int) -> str:
    """All pre-emit transforms in one place. Order matters: language patches
    first (so the chrome rewrite doesn't conflict with anything), variation-
    prefix strip, then chrome renumber + copyright."""
    slide_html = _apply_slide_patches(slide_html, src, idx)
    slide_html = _strip_variation_prefix(slide_html)
    slide_html = _rewrite_chrome(slide_html, position)
    return slide_html


def _render_title_slide() -> str:
    # No chrome bar on the title — the GlobalLogic logo occupies the
    # top-right slot where the copyright would otherwise sit.
    return f"""
<section class="deco-slide deco-title" data-deco="title">
  <img class="logo" src="globallogic-logo.png" alt="GlobalLogic">
  <div class="content">
    <div class="eyebrow">— AGENTIC PDLC —</div>
    <h1>Agentic<br/><span class="accent">PDLC.</span></h1>
    <p class="lead">Raising the <strong>quality bar</strong> and <strong>accelerating delivery</strong> for MedTech.</p>
    <div class="meta">
      <span class="name">Ben Xavier · CTO HCLS</span>
      <span>GlobalLogic · 2026</span>
    </div>
  </div>
  <div class="legal">
    <span><span class="nda">Confidential — NDA only.</span><span class="sep">·</span>Not for external distribution.</span>
    <span>© 2026 GlobalLogic Inc. · All rights reserved.</span>
  </div>
  <div class="signal-block" aria-hidden="true"></div>
</section>
"""


def _render_closing_slide() -> str:
    # Bookend to the title slide — reuses `.deco-title` styling. No chrome
    # (the GlobalLogic logo occupies the top-right slot, same as the title).
    return f"""
<section class="deco-slide deco-title deco-closing" data-deco="closing">
  <img class="logo" src="globallogic-logo.png" alt="GlobalLogic">
  <div class="content">
    <div class="eyebrow">— QUESTIONS & NEXT STEPS —</div>
    <h1>Thank<br/><span class="accent">you.</span></h1>
    <p class="lead">Let&rsquo;s bring a <strong>purpose-built agentic harness</strong> to your MedTech programs.</p>
    <div class="meta">
      <span class="name">Ben Xavier · CTO HCLS</span>
      <span>GlobalLogic · 2026</span>
    </div>
  </div>
  <div class="legal">
    <span><span class="nda">Confidential — NDA only.</span><span class="sep">·</span>Not for external distribution.</span>
    <span>© 2026 GlobalLogic Inc. · All rights reserved.</span>
  </div>
  <div class="signal-block" aria-hidden="true"></div>
</section>
"""


def _render_agenda_slide(chapters: list[dict], slide_num: int) -> str:
    cards = []
    for i, ch in enumerate(chapters, 1):
        subs_html = ""
        if ch.get("subsections"):
            sub_spans = "".join(f'<span>{_html.escape(s["title"])}</span>' for s in ch["subsections"])
            subs_html = f'<div class="ch-subs">{sub_spans}</div>'
        cards.append(
            f'<div class="chapter-card">'
            f'<div class="ch-num">{ch["num"]}</div>'
            f'<div class="ch-title">{_html.escape(ch["title"])}</div>'
            f'{subs_html}'
            f'</div>'
        )
    return f"""
<section class="deco-slide deco-agenda" data-deco="agenda">
  {_decoration_chrome(f"{slide_num:02d}")}
  <div class="content">
    <h2>Agenda</h2>
    <div class="agenda-grid">
      {''.join(cards)}
    </div>
  </div>
</section>
"""


def _render_section_divider(ch: dict, slide_num: int) -> str:
    lead_html = f'<p class="lead">{_html.escape(ch["lead"])}</p>' if ch.get("lead") else ""
    return f"""
<section class="deco-slide deco-divider" data-deco="section-{ch['num']}">
  {_decoration_chrome(f"{slide_num:02d}")}
  <div class="content">
    <div class="section-num">{ch['num']}</div>
    <h2>{_html.escape(ch['title'])}</h2>
    {lead_html}
  </div>
</section>
"""


def _render_concept_slide(c: dict, slide_num: int) -> str:
    eyebrow_html = f'<div class="eyebrow">{_html.escape(c["eyebrow"])}</div>' if c.get("eyebrow") else ""
    lead_html    = f'<p class="lead">{_html.escape(c["lead"])}</p>'             if c.get("lead")    else ""
    callout_html = f'<div class="callout">{_html.escape(c["callout"])}</div>'   if c.get("callout") else ""
    return f"""
<section class="deco-slide deco-concept" data-deco-id="{c.get('data_id', 'concept')}">
  {_decoration_chrome(f"{slide_num:02d}")}
  <div class="content">
    {eyebrow_html}
    <h2>{_html.escape(c["h2"])}</h2>
    {lead_html}
    {callout_html}
  </div>
</section>
"""


def _render_console_section_slide(section: dict, parent: dict, slide_num: int) -> str:
    """One §7 console-section slide: a compact title strip + a full-bleed
    screenshot. No explanatory body — the screenshot is the content."""
    eyebrow = f"§{int(parent['num'])} · {parent['title']}"
    return f"""
<section class="deco-slide deco-screenshot" data-deco-id="console-{section['num']}">
  {_decoration_chrome(f"{slide_num:02d}")}
  <div class="content">
    <div class="shot-head">
      <span class="shot-num">{section['num']}</span>
      <span class="shot-title">{_html.escape(section['title'])}</span>
      <span class="shot-eyebrow">{_html.escape(eyebrow)}</span>
    </div>
    <div class="shot-frame">
      <img src="{section['image']}" alt="{_html.escape(section['title'])} — project console">
    </div>
    {f'<div class="shot-caption">{_html.escape(section["caption"])}</div>' if section.get("caption") else ''}
  </div>
</section>
"""


def _render_key_deliverables_slide(slide_num: int) -> str:
    """Authored replacement for the Key-deliverables tile grid: the three
    filings drawn as a pathway rail, standing on the shared evidence backbone."""
    return f"""
<section class="deco-slide deco-custom" data-deco-id="key-deliverables">
  {_decoration_chrome(f"{slide_num:02d}")}
  <div class="content">
    <div class="eyebrow">KEY DELIVERABLES</div>
    <h2>Three filings. One evidence backbone.</h2>
    <div class="dlv-rail">
      <div class="dlv-node">
        <div class="dlv-step">STEP 1 · DIALOGUE</div>
        <div class="dlv-name">Q-Sub package</div>
        <div class="dlv-desc">Pre-submission conversation with FDA — device description, classification validation, and the PCCP scope questions we want answered before filing.</div>
      </div>
      <div class="dlv-arrow">→</div>
      <div class="dlv-node lit">
        <div class="dlv-step">STEP 2 · CLEARANCE</div>
        <div class="dlv-name">510(k) submission</div>
        <div class="dlv-desc">Substantial equivalence to the PP3000 predicate — software documentation, performance and validation data, risk analysis, labeling.</div>
      </div>
      <div class="dlv-arrow">→</div>
      <div class="dlv-node">
        <div class="dlv-step">STEP 3 · CHANGE ENVELOPE</div>
        <div class="dlv-name">PCCP document</div>
        <div class="dlv-desc">Pre-authorized post-market changes — categories, modification protocols, performance criteria, and the reporting plan.</div>
      </div>
    </div>
    <div class="dlv-flow"><span>▲</span><span>▲</span><span>▲</span></div>
    <div class="dlv-backbone">
      <div class="bb-cell">
        <div class="bb-tag">EVIDENCE BACKBONE</div>
        <div class="bb-name">Trace matrix — per DHF</div>
        <div class="bb-desc">User Needs ↔ Design Inputs ↔ SW Requirements ↔ Architecture ↔ V&amp;V ↔ Risk, with the filing scope derived from criticality tags. Rebuilt from source on demand.</div>
      </div>
      <div class="bb-cell">
        <div class="bb-tag">&nbsp;</div>
        <div class="bb-name">Risk file — ISO 14971</div>
        <div class="bb-desc">Hazard analysis (16 hazards) plus design and process FMEAs, QMS-form-conformant and wired into the trace matrix as a live risk layer.</div>
      </div>
    </div>
    <div class="takeaway">Every filing draws on the <strong>same</strong> trace and risk evidence — built once, cited everywhere, never copy-pasted.</div>
  </div>
</section>
"""


def _render_skills_overview_slide(slide_num: int) -> str:
    """Authored replacement for the three-page skills catalog mosaic: one
    slide, the load-bearing skills grouped by what they do for the program."""
    groups = [
        ("AUTHOR", "", [
            ("medtech-docs", "Scaffolds the DHF and documentation tree per FDA / IEC 62304 expectations."),
            ("docflow", "Audited DOCX / PDF / XLSX round-trips — images, cross-references, metadata preserved."),
            ("submissions", "Builds the Q-Sub / 510(k) / PCCP package structure and its composition manifests."),
            ("regulatory-authoring", "Lint, copy-edit, and QA-conformance for every regulator-facing sentence."),
        ]),
        ("VERIFY", "", [
            ("trace-matrix", "Six-layer bidirectional trace, rebuilt from source on demand."),
            ("dhf-manifest", "Are the right documents present for the regulatory obligations we carry?"),
            ("gap-analysis", "Critiques our own work product against the standards it claims to meet."),
            ("red-team", "A hostile buyer committee stress-tests outward documents before they ship."),
            ("reference-audit", "Every citation independently re-derived from the byte-correct source."),
        ]),
        ("OPERATE", "", [
            ("task", "The task-first gate: no change without an owning task document."),
            ("tracker", "Milestone-driven submission-readiness dashboard, editable in the browser."),
            ("project-console", "The browser workbench over the same agents and artifacts."),
            ("usage-metrics", "Token cost and modeled hours-saved, per task, honestly framed."),
            ("lessons", "Corrections harvested, staged, and promoted into permanent guardrails."),
        ]),
    ]
    cols = "".join(
        '<div class="ovw-col"><div class="ovw-head">' + head + '</div>' +
        "".join(f'<div class="ovw-chip"><div class="c-name">{n}</div><div class="c-tag">{t}</div></div>' for n, t in chips) +
        '</div>'
        for head, _, chips in groups
    )
    return f"""
<section class="deco-slide deco-custom" data-deco-id="skills-overview">
  {_decoration_chrome(f"{slide_num:02d}")}
  <div class="content">
    <div class="eyebrow">SKILLS · PACKAGED EXPERT PLAYBOOKS</div>
    <h2>35 skills. These carry the program.</h2>
    <div class="lead">Every skill is allow-listed in the project manifest and pulled from an auditable registry — the same playbook, run the same way, by everyone.</div>
    <div class="ovw-groups">{cols}</div>
  </div>
</section>
"""


def _render_agents_overview_slide(slide_num: int) -> str:
    """Authored replacement for the two-page agents catalog mosaic: the whole
    advisory bench in four groups, with the two-runtimes takeaway folded in."""
    groups = [
        ("CORE TEAM", "11 assistants", [
            ("regulatory-affairs · clinical-affairs · risk-management …",
             "One specialist per discipline — regulatory, clinical, risk, cybersecurity, quality, V&amp;V, human factors, systems, R&amp;D, post-market, program — each grounded in the project's own DHF and strategies, citing its sources."),
        ]),
        ("KOL PERSONAS", "8 voices", [
            ("clinicians &amp; domain experts",
             "Outside clinical voices that pressure-test user needs, workflows, and claims the way a real advisory board would."),
        ]),
        ("RED TEAM", "7 skeptics", [
            ("CEO · CFO · CTO · VP-Eng · QA-VP · RA-VP · PMO",
             "A hostile buyer committee. Every outward-facing document faces them — and their objections — before a real buyer ever sees it."),
        ]),
        ("PANELS", "5 boards", [
            ("core-team panel · design-review panel …",
             "Cross-functional boards that answer as one — program questions get multi-perspective input in a single pass."),
        ]),
    ]
    cols = "".join(
        f'<div class="ovw-col"><div class="ovw-head">{head} <span class="count">— {count}</span></div>' +
        "".join(f'<div class="ovw-chip"><div class="c-name">{n}</div><div class="c-tag">{t}</div></div>' for n, t in chips) +
        '</div>'
        for head, count, chips in groups
    )
    return f"""
<section class="deco-slide deco-custom" data-deco-id="agents-overview">
  {_decoration_chrome(f"{slide_num:02d}")}
  <div class="content">
    <div class="eyebrow">AGENTS · THE ADVISORY BENCH</div>
    <h2>One bench. Thirty-one advisors. Four jobs.</h2>
    <div class="ovw-groups">{cols}</div>
    <div class="takeaway"><strong>Same agents, two runtimes.</strong> One definition serves both the engineering environment and the browser console — and a security agent audits every session against the project manifest. Updating an advisor updates every surface at once.</div>
  </div>
</section>
"""


def _render_operating_rules_slide(slide_num: int) -> str:
    """Authored replacement merging the two-page Operating-rules card grid:
    all nine baked-in rules on one slide."""
    rules = [
        ("Task-first gate", "No file edit without an owning task document — a hook refuses otherwise. No orphan changes, ever."),
        ("One task, one file", "All analysis, drafts, and decisions live inside the task's own document. The trail stays auditable."),
        ("Real-time capture", "Strategy decisions and lessons land in the task doc the same turn they happen — not in a cleanup pass."),
        ("Session security check", "Every session opens with an audit against the project manifest's tool allowlists; drift triggers remediation."),
        ("Checkpoint &amp; recovery", "A session that ends without a checkpoint leaves a marker; the next session recovers the narrative from git history."),
        ("Audited conversions", "Raw document-conversion commands are blocked — every DOCX/PDF round-trip goes through one audited pipeline."),
        ("Local semantic search", "Ranked search over the whole documentation corpus, fully local — no cloud calls, one shared index."),
        ("Usage telemetry", "Token spend is collected per session and published through git into the console's metrics view."),
        ("Single source of truth", "Identity, DHF topology, team roster, registries, and security policy live in one project manifest."),
    ]
    chips = "".join(
        f'<div class="ovw-chip"><div class="c-name">{n}</div><div class="c-tag">{t}</div></div>'
        for n, t in rules
    )
    return f"""
<section class="deco-slide deco-custom" data-deco-id="operating-rules">
  {_decoration_chrome(f"{slide_num:02d}")}
  <div class="content">
    <div class="eyebrow">OPERATING RULES · BAKED INTO THE PROJECT</div>
    <h2>Nine rules the tooling enforces.</h2>
    <div class="ovw-grid3">{chips}</div>
  </div>
</section>
"""


def _render_skills_catalog_slide(slide_num: int) -> str:
    """Authored replacement for the 6-row skills-playbook mosaic: the FULL
    skill roster as a grouped name catalog."""
    groups = [
        ("DHF &amp; REGULATORY", ["medtech-docs", "docflow", "dhf-manifest", "trace-matrix",
                                  "submissions", "change-control", "regulatory-authoring", "reference-audit"]),
        ("QUALITY &amp; REVIEW", ["gap-analysis", "red-team", "best-practices", "secops",
                                  "writing-well", "lessons"]),
        ("PROGRAM OPS", ["task", "tracker", "strategy", "digest", "jira-pull",
                          "usage-metrics", "project-console", "advisors"]),
        ("AUTHORING &amp; FORMATS", ["docx", "pptx", "xlsx", "pdf", "md-deck", "frontend-design",
                                     "frontend-slides", "explain", "knowledge-pack-export"]),
        ("PLATFORM", ["file-locator", "skill-creator", "sync-skills", "web-control"]),
    ]
    cols = "".join(
        '<div class="ovw-col"><div class="ovw-head">' + head + '</div>' +
        "".join(f'<div class="ovw-chip mini"><div class="c-name">{n}</div></div>' for n in names) +
        '</div>'
        for head, names in groups
    )
    return f"""
<section class="deco-slide deco-custom" data-deco-id="skills-catalog">
  {_decoration_chrome(f"{slide_num:02d}")}
  <div class="content">
    <div class="eyebrow">SKILLS · THE FULL TOOLBOX</div>
    <h2>Thirty-five playbooks. One auditable registry.</h2>
    <div class="ovw-groups">{cols}</div>
    <div class="takeaway">Every skill is <strong>allow-listed</strong> in the project manifest and synced from a shared registry — consistency is installed, not trained.</div>
  </div>
</section>
"""


def _render_adds_up_to_slide(slide_num: int) -> str:
    """Authored replacement merging the two-page 'What this adds up to' grid:
    all seven by-construction properties on one slide."""
    props = [
        ("Owned", "By a named, dated task document — the task gate makes ownership automatic."),
        ("Located", "In a folder whose rules were read before the write."),
        ("Traced", "To a design input, architecture node, V&amp;V item, and risk control."),
        ("Audited", "Against a standing best-practices registry."),
        ("Security-checked", "At session start, against the project's tool allowlists."),
        ("Recoverable", "Every session's narrative is checkpointed; a dropped session auto-recovers."),
        ("Measured", "Token spend and modeled hours-saved, rolled up per task."),
    ]
    chips = "".join(
        f'<div class="ovw-chip"><div class="c-name">{i+1} · {n}</div><div class="c-tag">{t}</div></div>'
        for i, (n, t) in enumerate(props)
    )
    return f"""
<section class="deco-slide deco-custom" data-deco-id="adds-up-to">
  {_decoration_chrome(f"{slide_num:02d}")}
  <div class="content">
    <div class="eyebrow">QUALITY &amp; PROCESS · THE SUM</div>
    <h2>Every change is, by construction —</h2>
    <div class="ovw-grid4">{chips}</div>
    <div class="takeaway">None of the seven depends on a person remembering. <strong>Compliance stops being a tax on velocity and becomes a property of the toolchain.</strong></div>
  </div>
</section>
"""


CUSTOM_RENDERERS = {
    "key-deliverables": _render_key_deliverables_slide,
    "operating-rules": _render_operating_rules_slide,
    "skills-overview": _render_skills_overview_slide,
    "skills-catalog": _render_skills_catalog_slide,
    "agents-overview": _render_agents_overview_slide,
    "adds-up-to": _render_adds_up_to_slide,
}


def _render_subsection_divider(parent: dict, sub: dict, slide_num: int) -> str:
    eyebrow = f"§{int(parent['num'])} · {parent['title']}"
    return f"""
<section class="deco-slide deco-divider deco-subsection" data-deco="sub-{parent['num']}-{sub['num']}">
  {_decoration_chrome(f"{slide_num:02d}")}
  <div class="content">
    <div class="eyebrow">{_html.escape(eyebrow)}</div>
    <div class="section-num"><span class="parent">{parent['num']}·</span>{sub['num']}</div>
    <h2>{_html.escape(sub['title'])}</h2>
  </div>
</section>
"""


def _decorated_sequence(kept):
    """Walk kept slides; emit an ordered list of {kind, ...} dicts that build_final
    renders into HTML. Replaces source dividers with chapter dividers, replaces the
    old agenda slide, inserts Section 1 right after the agenda, inserts subsection
    dividers in Section 7, and moves the KOL slide into Project Console → Agents."""
    chapter_by_anchor = {}
    no_anchor_chapters = []
    subsection_by_anchor = {}
    for ch in CHAPTERS:
        if ch["anchor"] is None:
            no_anchor_chapters.append(ch)
        else:
            chapter_by_anchor[tuple(ch["anchor"])] = ch
        for sub in ch.get("subsections", []):
            # Only anchored subsections inject divider slides; anchor-less
            # subsections (e.g. §7's) are agenda-display + screenshot-config only.
            if sub.get("anchor"):
                subsection_by_anchor[tuple(sub["anchor"])] = (ch, sub)

    move_after = {}        # destination-anchor → [moved keys, …]
    moved_keys = set()
    for src_key, dest in SLIDE_MOVES.items():
        if "after" in dest:
            move_after.setdefault(tuple(dest["after"]), []).append(tuple(src_key))
            moved_keys.add(tuple(src_key))

    out = [{"kind": "title"}]
    for src, idx in kept:
        key = (src, idx)
        if key == AGENDA_REPLACES:
            out.append({"kind": "agenda"})
            for ch in no_anchor_chapters:
                out.append({"kind": "chapter", "chapter": ch})
            continue
        if key in moved_keys:
            continue
        # Inject interstitial(s) BEFORE this slide is emitted (after any
        # section/subsection divider — those still go via chapter_by_anchor /
        # subsection_by_anchor branches below if the slide is also an anchor).
        if key in INTERSTITIALS:
            out.append({"kind": "concept", "concept": INTERSTITIALS[key]})
        if key in CUSTOM_REPLACES:
            out.append({"kind": "custom", "name": CUSTOM_REPLACES[key]})
            continue
        if key in chapter_by_anchor:
            ch = chapter_by_anchor[key]
            out.append({"kind": "chapter", "chapter": ch})
            if not ch.get("replace"):
                out.append({"kind": "slide", "src": src, "idx": idx})
        elif key in subsection_by_anchor:
            parent, sub = subsection_by_anchor[key]
            out.append({"kind": "subsection", "parent": parent, "subsection": sub})
            out.append({"kind": "slide", "src": src, "idx": idx})
        else:
            out.append({"kind": "slide", "src": src, "idx": idx})
        for moved in move_after.get(key, []):
            out.append({"kind": "slide", "src": moved[0], "idx": moved[1]})
        # Append §7 console-section screenshot slides after the trigger slide.
        if SLIDE_APPENDS.get(key) == "console-sections":
            console_ch = next((c for c in CHAPTERS if c["num"] == "07"), None)
            if console_ch:
                for section in console_ch.get("subsections", []):
                    out.append({"kind": "screenshot", "section": section, "parent": console_ch})
    out.append({"kind": "closing"})
    return out


# ---------------------------------------------------------------------------
# Final index.html
# ---------------------------------------------------------------------------

FINAL_NAV_JS = r"""
(function () {
  const slides = Array.from(document.querySelectorAll(".cp-slide-final"));
  if (!slides.length) return;

  // Wayfinding: 3px top progress bar + "NN / total" counters + chapter crumb.
  const bar = document.createElement("div");
  bar.id = "cp-progress";
  document.body.appendChild(bar);
  let chapter = "";
  slides.forEach(sl => {
    const divider = sl.querySelector(".deco-divider:not(.deco-subsection)");
    if (divider) {
      const numEl = divider.querySelector(".section-num");
      const hEl = divider.querySelector("h2");
      if (numEl && hEl) chapter = "§" + parseInt(numEl.textContent, 10) + " · " + hEl.textContent.trim();
    }
    const crumb = sl.querySelector(".chrome .crumb");
    // Screenshot slides already carry the chapter in their own shot-eyebrow.
    if (crumb && chapter && !sl.querySelector(".shot-eyebrow")) crumb.textContent = chapter;
    const num = sl.querySelector(".chrome .num");
    if (num) num.textContent = num.textContent.trim() + " / " + slides.length;
  });

  function idxFromScroll() {
    return Math.max(0, Math.min(slides.length - 1, Math.round(window.scrollY / window.innerHeight)));
  }
  function paint() { bar.style.width = (((idxFromScroll() + 1) / slides.length) * 100) + "%"; }
  window.addEventListener("scroll", paint, { passive: true });
  paint();

  let cur = 0;
  function go(n) {
    cur = Math.max(0, Math.min(slides.length - 1, n));
    slides[cur].scrollIntoView({ behavior: "smooth", block: "start" });
  }
  document.addEventListener("keydown", e => {
    // Re-derive position from scroll first — wheel/trackpad scrolling would
    // otherwise leave `cur` stale and a keypress would jump backwards.
    cur = idxFromScroll();
    if (e.key === "ArrowRight" || e.key === " " || e.key === "PageDown") {
      e.preventDefault(); go(cur + 1);
    } else if (e.key === "ArrowLeft" || e.key === "PageUp") {
      e.preventDefault(); go(cur - 1);
    } else if (e.key === "Home") {
      e.preventDefault(); go(0);
    } else if (e.key === "End") {
      e.preventDefault(); go(slides.length - 1);
    }
  });
})();
"""

# Composite-scoped CSS overrides — appended AFTER the scoped source-deck CSS
# so they win the cascade. Fixes systemic issues in project-overview-sourced
# slides: line-clamped card text (full text was hover-only — dead in PDF) and
# the sub-AA muted-text token.
COMPOSITE_OVERRIDES_CSS = """
/* ===== composite overrides (win over scoped source CSS) ===== */
.src-project-overview, .src-agentic-delivery { --text-muted: #8a8a99; }
.src-project-overview .mini-card .mc-sub {
  display: block;
  -webkit-line-clamp: unset;
  overflow: visible;
  max-height: none;
}
.src-project-overview .mini-card .mc-full { display: none; }
"""

# Scale-to-fit: a handful of source slides carry more content than fits a
# 900px-tall box (AD#6 "Three external signals" is the worst — 2-line h2 +
# 3 stat cards + a callout). The source CSS uses `overflow: hidden`, so the
# overflow gets *clipped* top and bottom rather than shrunk. This measures
# each slide's content box and applies a uniform downscale transform when it
# overflows — so dense slides shrink to fit instead of clipping. Runs on the
# screen view AND re-runs on `beforeprint` (Chrome headless print-to-PDF fires
# it with print layout active), so the PDF and the browser stay consistent.
FINAL_FIT_JS = r"""
(function () {
  function fitOne(box) {
    if (!box || !box.children.length) return;
    box.style.transform = "";
    box.style.transformOrigin = "center center";
    // The content boxes use `justify-content: center`, so overflow spills
    // both above AND below the box — scrollHeight only sees the downward
    // half. Measure the true span from the first child's top to the last
    // child's bottom instead.
    var kids = box.children;
    var top = kids[0].getBoundingClientRect().top;
    var bottom = kids[kids.length - 1].getBoundingClientRect().bottom;
    var needed = Math.max(bottom - top, box.scrollHeight);
    var avail = box.clientHeight;
    if (avail > 0 && needed > avail) {
      // 0.97 leaves a hair of breathing room above/below.
      box.style.transform = "scale(" + ((avail / needed) * 0.97).toFixed(4) + ")";
    }
  }
  function fitAll() {
    var slides = document.querySelectorAll(".cp-slide-final");
    for (var i = 0; i < slides.length; i++) {
      fitOne(
        slides[i].querySelector("section.slide > .slide-content") ||
        slides[i].querySelector(".deco-slide > .content")
      );
    }
  }
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(fitAll);
  window.addEventListener("load", fitAll);
  window.addEventListener("resize", fitAll);
  window.addEventListener("beforeprint", fitAll);
  window.addEventListener("afterprint", fitAll);
  fitAll();
})();
"""

FINAL_CSS = """
html, body { margin: 0; padding: 0; background: #000; }
.cp-slide-final { position: relative; }

/* ---- Print / PDF: one slide per page. Page box == 1440x900 CSS px — the
       SAME viewport the deck is authored and browser-reviewed at — but
       expressed in INCHES (15in x 9.375in = 1440x900 at 96dpi). Chrome's
       print engine mis-handles px units in `@page size` — vw/vh then resolve
       against a wrong box and content renders ~2x too tall. Inches resolve
       correctly. Matching the authored viewport exactly matters: fonts and
       paddings sit at fixed px/rem clamp caps, so any smaller page box makes
       them proportionally larger than the browser view (the old 1400x900 box
       rendered callouts/cards visibly bigger than index.html). ---- */
@media print {
  @page { size: 15in 9.375in; margin: 0; }
  * { -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }
  html, body { margin: 0; padding: 0; background: #000; }
  .cp-slide-final {
    width: 1440px;
    height: 900px;
    overflow: hidden;
    break-after: page;
    page-break-after: always;
  }
  .cp-slide-final:last-child { break-after: auto; page-break-after: avoid; }
  /* Pin the slide + scope wrappers to the page box so 100vw/100vh content
     fills exactly one page. */
  .cp-slide-final > div,
  .cp-slide-final > section,
  .cp-slide-final .slide,
  .cp-slide-final .deco-slide {
    width: 1440px !important;
    height: 900px !important;
  }
}
"""


def build_final() -> Path:
    picks = load_picks()
    if not picks:
        sys.exit("missing picks.json — run --candidate, curate, --reorder, then re-export picks.json before --final")

    decks = {name: parse_deck(name, path) for name, path in SOURCES}

    used = {o["src"] for o in picks["order"] if o.get("keep")}
    if not used:
        sys.exit("picks.json has no kept slides — refusing to emit an empty deck")

    # Always include Google Fonts that the decorations rely on (Archivo Black,
    # Space Grotesk, JetBrains Mono — same families agentic-delivery loads).
    deco_font_link = (
        '<link rel="preconnect" href="https://fonts.googleapis.com">'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
        '<link href="https://fonts.googleapis.com/css2?'
        'family=Archivo+Black&family=Space+Grotesk:wght@300;400;500;600;700&'
        'family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">'
    )
    seen_links = set([deco_font_link])
    head_links = [deco_font_link]
    css_chunks = []
    for name in [n for n, _ in SOURCES if n in used]:
        d = decks[name]
        for link in d["links"]:
            if link not in seen_links:
                seen_links.add(link); head_links.append(link)
        css_chunks.append(f"/* === {d['name']} (scoped) === */\n" +
                          scope_css(d["style"], d["scope"]))
    scoped_css = "\n\n".join(css_chunks)

    kept = [(o["src"], int(o["idx"])) for o in picks["order"] if o.get("keep")]
    sequence = _decorated_sequence(kept)

    # Slide numbering for chrome — every emitted slide gets a 1-based number
    pieces = []
    slide_num = 0
    for item in sequence:
        slide_num += 1
        kind = item["kind"]
        if kind == "title":
            pieces.append(f'<div class="cp-slide-final" data-deco="title">{_render_title_slide()}</div>')
        elif kind == "agenda":
            pieces.append(f'<div class="cp-slide-final" data-deco="agenda">{_render_agenda_slide(CHAPTERS, slide_num)}</div>')
        elif kind == "chapter":
            pieces.append(f'<div class="cp-slide-final" data-deco="chapter-{item["chapter"]["num"]}">{_render_section_divider(item["chapter"], slide_num)}</div>')
        elif kind == "subsection":
            pieces.append(f'<div class="cp-slide-final" data-deco="sub-{item["parent"]["num"]}-{item["subsection"]["num"]}">{_render_subsection_divider(item["parent"], item["subsection"], slide_num)}</div>')
        elif kind == "concept":
            pieces.append(f'<div class="cp-slide-final" data-deco="concept">{_render_concept_slide(item["concept"], slide_num)}</div>')
        elif kind == "custom":
            pieces.append(f'<div class="cp-slide-final" data-deco="custom-{item["name"]}">{CUSTOM_RENDERERS[item["name"]](slide_num)}</div>')
        elif kind == "screenshot":
            pieces.append(f'<div class="cp-slide-final" data-deco="console-{item["section"]["num"]}">{_render_console_section_slide(item["section"], item["parent"], slide_num)}</div>')
        elif kind == "closing":
            pieces.append(f'<div class="cp-slide-final" data-deco="closing">{_render_closing_slide()}</div>')
        elif kind == "slide":
            src = item["src"]; idx = item["idx"]
            d = decks.get(src)
            if not d:
                print(f"warn: unknown source {src!r}, skipping", file=sys.stderr); slide_num -= 1; continue
            if not (0 <= idx < len(d["slides"])):
                print(f"warn: idx {idx} out of range for {src!r}, skipping", file=sys.stderr); slide_num -= 1; continue
            slide_html = _transform_source_slide(d["slides"][idx], src, idx, slide_num)
            pieces.append(
                f'<div class="cp-slide-final" data-src="{d["name"]}" data-idx="{idx}">'
                f'<div class="{d["scope"]}">{slide_html}</div>'
                f'</div>'
            )

    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Agentic PDLC — GlobalLogic</title>
{chr(10).join(head_links)}
<style>
{FINAL_CSS}
{DECO_CSS}
{scoped_css}
{COMPOSITE_OVERRIDES_CSS}
</style>
</head>
<body>
{''.join(pieces)}
<script>
{FINAL_NAV_JS}
</script>
<script>
{FINAL_FIT_JS}
</script>
</body>
</html>
"""
    out = ROOT / "index.html"
    out.write_text(html, encoding="utf-8")
    return out


# ---------------------------------------------------------------------------
# PDF export (Chrome headless print-to-PDF)
# ---------------------------------------------------------------------------

def _find_chrome() -> str | None:
    candidates = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
    ]
    for c in candidates:
        if Path(c).is_file():
            return c
    for name in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome"):
        found = shutil.which(name)
        if found:
            return found
    return None


def build_pdf() -> Path:
    """Render index.html to GlobalLogic_Agentic_PDLC.pdf via Chrome headless print-to-PDF.
    The @media print rules in FINAL_CSS pin each slide to a 13.333in x 7.5in
    page (16:9 widescreen), one slide per page."""
    index = ROOT / "index.html"
    if not index.is_file():
        sys.exit("missing index.html — run `python build.py --final` first")
    chrome = _find_chrome()
    if not chrome:
        sys.exit("Chrome/Chromium not found — install Google Chrome, or print "
                 "index.html to PDF manually (the @media print CSS is already in place)")
    out = ROOT / "GlobalLogic_Agentic_PDLC.pdf"
    cmd = [
        chrome,
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        "--hide-scrollbars",
        "--allow-file-access-from-files",
        # Window size == the @page box (1440x900 — the authored viewport) so
        # the scale-to-fit script (FINAL_FIT_JS, runs on `load`) measures
        # slides against the same box the print engine uses — headless
        # --print-to-pdf does not reliably fire `beforeprint`, so the on-load
        # measurement must already be right.
        "--window-size=1440,900",
        "--virtual-time-budget=20000",   # let Google Fonts + console PNGs settle
        f"--print-to-pdf={out}",
        index.as_uri(),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    if result.returncode != 0 or not out.is_file():
        sys.exit(f"chrome print-to-pdf failed (rc={result.returncode}):\n"
                 f"{(result.stderr or result.stdout)[-1000:]}")
    return out


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--candidate", action="store_true", help="Pass 1: build candidate.html in SELECT mode (KEEP/REMOVE per slide, source order)")
    g.add_argument("--reorder",   action="store_true", help="Pass 2: rebuild candidate.html in REORDER mode (drag/▲/▼ for kept slides only). Requires picks.json.")
    g.add_argument("--final",     action="store_true", help="Build index.html from picks.json (kept slides in chosen order)")
    g.add_argument("--pdf",       action="store_true", help="Render index.html to GlobalLogic_Agentic_PDLC.pdf via Chrome headless (run --final first)")
    args = ap.parse_args()

    if args.candidate:
        out = build_candidate_select()
        text = out.read_text(encoding="utf-8")
        n = text.count('class="cp-slide"')
        print(f"wrote {out}  (SELECT mode, {out.stat().st_size:,} bytes, {n} slides)")
    elif args.reorder:
        out = build_candidate_reorder()
        text = out.read_text(encoding="utf-8")
        n = text.count('class="cp-slide"')
        print(f"wrote {out}  (REORDER mode, {out.stat().st_size:,} bytes, {n} kept slides)")
    elif args.final:
        out = build_final()
        text = out.read_text(encoding="utf-8")
        n = text.count('class="cp-slide-final"')
        print(f"wrote {out}  ({out.stat().st_size:,} bytes, {n} kept slides)")
    elif args.pdf:
        out = build_pdf()
        print(f"wrote {out}  ({out.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
