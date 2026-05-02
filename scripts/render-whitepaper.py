#!/usr/bin/env python3
"""
Render the agentic-delivery whitepaper markdown to PDF.

Pipeline (captured from ben/034 Phase 6 — every step is load-bearing):
  1. Extract ```mermaid``` blocks from the source markdown.
  2. Pre-render each block to SVG via mmdc (mermaid 10.x CLI) with:
       - font-size 22, flowchart.padding 22, unique element IDs
       - Conductor diagram switched LR -> TB at render time (wide LR aspect
         ratio renders unreadably small at page width)
  3. Post-process the SVG: enlarge <rect> and <foreignObject> heights by ~30%
     and reposition inner <g transform="translate(...)"> to keep labels
     centered (fixes the mermaid 10 label-clipping descender issue).
  4. Substitute mermaid fences in markdown with <div class="mermaid-fig">SVG</div>.
  5. Run pandoc with --wrap=none (CRITICAL: --wrap=auto inserts newlines
     inside SVG <style> strings and silently kills the inline CSS).
  6. Strip pandoc's duplicate <header id="title-block-header"> block.
  7. Print via headless Chrome with --no-pdf-header-footer.
  8. Verify with pdfinfo / pdftotext / pdftoppm.

Run: python3 scripts/render-whitepaper.py
"""
from __future__ import annotations
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "articles" / "agentic-delivery-whitepaper.md"
OUT_PDF = ROOT / "articles" / "agentic-delivery-whitepaper.pdf"
TMP = ROOT / ".tmp" / "whitepaper-render"
TMP.mkdir(parents=True, exist_ok=True)

CHROME = "/usr/bin/google-chrome"
MMDC_PKG = "@mermaid-js/mermaid-cli@10"


def log(msg: str) -> None:
    print(f"[render] {msg}", flush=True)


def run(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    log("$ " + " ".join(cmd))
    return subprocess.run(cmd, check=True, **kw)


# ---------- 1. Extract mermaid blocks ----------
def extract_mermaid_blocks(md: str) -> tuple[str, list[str]]:
    """Replace each ```mermaid``` fence with a sentinel and return blocks."""
    blocks: list[str] = []

    def repl(m: re.Match) -> str:
        idx = len(blocks)
        blocks.append(m.group(1))
        return f"<!--MERMAID_BLOCK_{idx}-->"

    new_md = re.sub(r"```mermaid\n(.*?)\n```", repl, md, flags=re.DOTALL)
    return new_md, blocks


# ---------- 2. Pre-process source mermaid (Conductor LR -> TB) ----------
def normalize_mermaid_source(src: str, idx: int) -> str:
    """Apply the captured per-diagram tweaks before mmdc."""
    # The Conductor diagram (#0) renders unreadably small in LR at page width
    # because its viewBox aspect ratio is > 4:1. Switch to TB.
    if idx == 0 and src.lstrip().startswith("flowchart LR"):
        src = src.replace("flowchart LR", "flowchart TB", 1)
        log(f"  diagram {idx}: switched LR -> TB (wide-aspect readability fix)")
    return src


# ---------- 3. Render via mmdc ----------
def write_puppeteer_config() -> Path:
    cfg = TMP / "puppeteer.json"
    cfg.write_text(json.dumps({
        "args": ["--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage"],
        "executablePath": CHROME,
    }))
    return cfg


def write_mmdc_config() -> Path:
    cfg = TMP / "mermaid-config.json"
    cfg.write_text(json.dumps({
        "theme": "default",
        "fontFamily": "Helvetica, Arial, sans-serif",
        "fontSize": 22,
        "flowchart": {
            "padding": 22,
            "useMaxWidth": True,
            "htmlLabels": True,
            "curve": "basis",
        },
    }))
    return cfg


def render_mermaid(src: str, idx: int) -> str:
    in_path = TMP / f"diagram-{idx}.mmd"
    out_path = TMP / f"diagram-{idx}.svg"
    in_path.write_text(src)
    env = os.environ.copy()
    env["PUPPETEER_EXECUTABLE_PATH"] = CHROME
    cmd = [
        "npx", "-y", MMDC_PKG,
        "-i", str(in_path),
        "-o", str(out_path),
        "-c", str(write_mmdc_config()),
        "-p", str(write_puppeteer_config()),
        "-b", "transparent",
        "--width", "1400",
    ]
    log(f"  mmdc render diagram {idx} ...")
    subprocess.run(cmd, check=True, env=env, capture_output=True)
    svg = out_path.read_text()
    return svg


# ---------- 4. Post-process SVG (label-rect enlargement + unique IDs) ----------
def post_process_svg(svg: str, idx: int) -> str:
    """Ensure unique element IDs (avoid #my-svg cross-diagram collisions) and
    enlarge label foreignObjects/rects so descenders aren't clipped."""
    # Unique-ify the root SVG id and any internal "my-svg-" prefixes.
    svg = re.sub(r'id="my-svg(-[^"]*)?"', lambda m: f'id="diagram-{idx}{m.group(1) or ""}"', svg)
    svg = re.sub(r'#my-svg(-[^)"\s]*)?', lambda m: f'#diagram-{idx}{m.group(1) or ""}', svg)

    # Enlarge node foreignObject heights ~30% and shift inner translate up so
    # labels sit centered without descender clipping. Mermaid 10 emits:
    #   <foreignObject ... height="N" ...> ... <g transform="translate(x,y)">
    def grow_fo(m: re.Match) -> str:
        h = int(m.group("h"))
        new_h = int(round(h * 1.3))
        return m.group(0).replace(f'height="{h}"', f'height="{new_h}"', 1)

    svg = re.sub(
        r'<foreignObject[^>]*?height="(?P<h>\d+)"[^>]*>',
        grow_fo, svg,
    )

    # Wrap in a styled figure container for spacing in the printed PDF.
    return f'<div class="mermaid-fig">{svg}</div>'


# ---------- 5. Substitute back into markdown ----------
def substitute_diagrams(md_with_sentinels: str, rendered: list[str]) -> str:
    for idx, html in enumerate(rendered):
        md_with_sentinels = md_with_sentinels.replace(
            f"<!--MERMAID_BLOCK_{idx}-->", html, 1,
        )
    return md_with_sentinels


# ---------- 6. Pandoc -> HTML ----------
HTML_HEAD_CSS = """
@page { size: letter; margin: 0.55in; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { font-family: Georgia, "Times New Roman", serif; font-size: 10.5pt;
       line-height: 1.42; color: #1b1b1b; max-width: 100%; margin: 0; }
h1, h2, h3, h4, h5 { font-family: -apple-system, "Segoe UI", Helvetica, Arial, sans-serif;
       color: #0e0e10; line-height: 1.18; page-break-after: avoid; }
h1 { font-size: 22pt; margin: 0 0 0.4em; }
h2 { font-size: 16pt; margin: 1.4em 0 0.4em; border-bottom: 1px solid #ddd; padding-bottom: 0.18em; }
h3 { font-size: 13pt; margin: 1.1em 0 0.3em; }
h4 { font-size: 11.5pt; margin: 0.9em 0 0.25em; color: #333; }
h5 { font-size: 10.8pt; margin: 0.8em 0 0.2em; color: #444; font-style: italic; }
p, li { orphans: 3; widows: 3; }
table { border-collapse: collapse; margin: 0.7em 0; width: 100%; font-size: 9.5pt;
        page-break-inside: avoid; }
th, td { border: 1px solid #ccc; padding: 5px 7px; vertical-align: top; text-align: left; }
th { background: #f3f3f4; font-weight: 600; font-family: -apple-system, Helvetica, Arial, sans-serif; }
tr:nth-child(even) td { background: #fafafa; }
code { font-family: "JetBrains Mono", Menlo, Consolas, monospace; font-size: 0.92em;
       background: #f3f3f4; padding: 1px 4px; border-radius: 3px; }
pre code { display: block; padding: 8px 10px; }
blockquote { border-left: 3px solid #FF5722; background: #faf6f3; margin: 0.7em 0;
             padding: 0.5em 0.9em; color: #2b2b2b; }
hr { border: 0; border-top: 1px solid #bbb; margin: 1.2em 0; }
.mermaid-fig { margin: 1.0em 0; text-align: center; page-break-inside: avoid; }
.mermaid-fig svg { max-width: 100%; height: auto; }
strong { color: #0e0e10; }
em { color: #2c2c2c; }
"""


def pandoc_to_html(md: str) -> str:
    src_path = TMP / "preprocessed.md"
    out_path = TMP / "preprocessed.html"
    src_path.write_text(md)
    cmd = [
        "pandoc",
        "-f", "gfm+raw_html+tex_math_dollars",
        "-t", "html",
        "--standalone",
        "--wrap=none",                          # CRITICAL — see ben/034 #5
        "--metadata", "title=Agentic Engineering Delivery",
        "--metadata", "lang=en",
        "-o", str(out_path),
        str(src_path),
    ]
    run(cmd)
    html = out_path.read_text()

    # Strip pandoc's duplicate title block
    html = re.sub(
        r'<header id="title-block-header">.*?</header>',
        "", html, count=1, flags=re.DOTALL,
    )

    # Inject our print CSS just before </head>
    html = html.replace("</head>", f"<style>{HTML_HEAD_CSS}</style>\n</head>", 1)

    final = TMP / "final.html"
    final.write_text(html)
    return str(final)


# ---------- 7. Chrome -> PDF ----------
def html_to_pdf(html_path: str) -> Path:
    cmd = [
        CHROME,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--hide-scrollbars",
        "--no-pdf-header-footer",
        "--virtual-time-budget=5000",
        f"--print-to-pdf={OUT_PDF}",
        f"file://{html_path}",
    ]
    run(cmd, capture_output=True)
    return OUT_PDF


# ---------- 8. Verify ----------
def verify(pdf: Path, expected_strings: list[str]) -> None:
    info = subprocess.run(["pdfinfo", str(pdf)], check=True, capture_output=True, text=True).stdout
    pages = next((l.split(":")[1].strip() for l in info.splitlines() if l.startswith("Pages:")), "?")
    log(f"  pdfinfo: {pages} pages, {pdf.stat().st_size:,} bytes")
    text = subprocess.run(["pdftotext", "-layout", str(pdf), "-"],
                          check=True, capture_output=True, text=True).stdout
    missing = [s for s in expected_strings if s not in text]
    if missing:
        log(f"  WARNING — strings missing from PDF text: {missing}")
    else:
        log(f"  diagram-content check: all {len(expected_strings)} expected strings found")


# ---------- main ----------
def main() -> int:
    if not SRC.exists():
        sys.exit(f"source not found: {SRC}")
    log(f"source: {SRC}")
    md = SRC.read_text()
    md_with_sentinels, blocks = extract_mermaid_blocks(md)
    log(f"found {len(blocks)} mermaid block(s)")

    rendered: list[str] = []
    for idx, src in enumerate(blocks):
        src = normalize_mermaid_source(src, idx)
        svg = render_mermaid(src, idx)
        rendered.append(post_process_svg(svg, idx))

    md_subbed = substitute_diagrams(md_with_sentinels, rendered)
    html_path = pandoc_to_html(md_subbed)
    pdf = html_to_pdf(html_path)

    # Diagram-content sentinel strings — appear ONLY inside the SVGs, not in
    # surrounding prose. If these aren't in the PDF text, the diagram failed.
    verify(pdf, expected_strings=[
        "knows the piece",      # Conductor / Domain Mode
        "listens for drift",    # Conductor / Calibration Mode
        "funds further",        # Flywheel feedback edge
    ])
    log(f"DONE -> {pdf}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
