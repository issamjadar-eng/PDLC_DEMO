#!/usr/bin/env python3
"""
render.py — produce the public artifact for a public-doc draft.

Pipeline:
  1. Strip the `public_doc:` frontmatter + every INTERNAL block (strip_internal).
     Abort if any internal marker survives — never emit a leaking artifact.
  2. --format md   -> write the clean markdown and stop (no external tools).
  3. Pre-render ```mermaid``` fences to inline SVG via mmdc (only if any exist).
  4. pandoc -> standalone HTML with print CSS.  --format html stops here.
  5. headless Chrome -> PDF.  --format pdf (default).

Generalized from the ported whitepaper render pipeline (mermaid sizing + the
pandoc --wrap=none fix are preserved). External deps are checked up front and
reported clearly; md/html-without-mermaid paths need nothing beyond Python.

Usage:
    python3 render.py DRAFT.md [--format pdf|html|md] [--out DIR]
                       [--chrome PATH] [--title TEXT]

Chrome is auto-detected across macOS/Linux; override with --chrome or
$PUBLIC_DOC_CHROME.
"""
from __future__ import annotations
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from strip_internal import strip  # noqa: E402

CHROME_CANDIDATES = [
    os.environ.get("PUBLIC_DOC_CHROME", ""),
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium",
    "/usr/bin/chromium-browser",
    shutil.which("google-chrome") or "",
    shutil.which("chromium") or "",
]
MMDC_PKG = "@mermaid-js/mermaid-cli@10"


def log(msg: str) -> None:
    print(f"[render] {msg}", file=sys.stderr, flush=True)


def find_chrome(override: str | None) -> str | None:
    for c in ([override] if override else []) + CHROME_CANDIDATES:
        if c and Path(c).exists():
            return c
    return None


def read_meta_title(md: str) -> str | None:
    m = re.match(r"\A---\n(.*?)\n---\n", md, re.DOTALL)
    if m and "public_doc:" in m.group(1):
        tm = re.search(r"^\s*title:\s*(.+?)\s*$", m.group(1), re.MULTILINE)
        if tm:
            return tm.group(1).strip().strip("'\"")
    return None


def read_meta_brief(md: str) -> str | None:
    m = re.match(r"\A---\n(.*?)\n---\n", md, re.DOTALL)
    if m and "public_doc:" in m.group(1):
        for key in ("brief", "subtitle"):
            bm = re.search(rf"^\s*{key}:\s*(.+?)\s*$", m.group(1), re.MULTILINE)
            if bm:
                return bm.group(1).strip().strip("'\"")
    return None


def read_public_filename(md: str, default: str) -> str:
    return read_meta_field(md, "public_filename") or default


def read_meta_field(md: str, key: str) -> str | None:
    """Read a scalar field from the `public_doc:` frontmatter block."""
    m = re.match(r"\A---\n(.*?)\n---\n", md, re.DOTALL)
    if m and "public_doc:" in m.group(1):
        fm = re.search(rf"^\s*{key}:\s*(.+?)\s*$", m.group(1), re.MULTILINE)
        if fm:
            return fm.group(1).strip().strip("'\"")
    return None


def read_brand() -> dict:
    """Project-level brand defaults from tools/public-doc/brand.yml (cwd-relative,
    per the skill's repo-root convention). Keeps the skill project-agnostic — the
    copyright line and logo path live in the project, not the skill."""
    out: dict[str, str] = {}
    p = Path("tools/public-doc/brand.yml")
    if p.exists():
        txt = p.read_text()
        for key in ("logo", "copyright", "author"):
            m = re.search(rf"^\s*{key}:\s*(.+?)\s*$", txt, re.MULTILINE)
            if m:
                out[key] = m.group(1).strip().strip("'\"")
    return out


# ---------- mermaid ----------
def extract_mermaid(md: str) -> tuple[str, list[str]]:
    blocks: list[str] = []

    def repl(m: re.Match) -> str:
        blocks.append(m.group(1))
        return f"<!--MERMAID_BLOCK_{len(blocks) - 1}-->"

    return re.sub(r"```mermaid\n(.*?)\n```", repl, md, flags=re.DOTALL), blocks


def render_mermaid(src: str, idx: int, tmp: Path, chrome: str | None) -> str:
    in_path = tmp / f"diagram-{idx}.mmd"
    out_path = tmp / f"diagram-{idx}.svg"
    in_path.write_text(src)
    cfg = tmp / "mmdc.json"
    cfg.write_text(json.dumps({
        "theme": "default", "fontFamily": "Helvetica, Arial, sans-serif",
        "fontSize": 22,
        "flowchart": {"padding": 22, "useMaxWidth": True, "htmlLabels": True, "curve": "basis"},
    }))
    pcfg = tmp / "puppeteer.json"
    pcfg.write_text(json.dumps({
        "args": ["--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage"],
        **({"executablePath": chrome} if chrome else {}),
    }))
    env = os.environ.copy()
    if chrome:
        env["PUPPETEER_EXECUTABLE_PATH"] = chrome
    cmd = ["npx", "-y", MMDC_PKG, "-i", str(in_path), "-o", str(out_path),
           "-c", str(cfg), "-p", str(pcfg), "-b", "transparent", "--width", "1400"]
    subprocess.run(cmd, check=True, env=env, capture_output=True)
    svg = out_path.read_text()
    svg = re.sub(r'id="my-svg(-[^"]*)?"', lambda m: f'id="d{idx}{m.group(1) or ""}"', svg)
    svg = re.sub(r'#my-svg(-[^)"\s]*)?', lambda m: f'#d{idx}{m.group(1) or ""}', svg)

    def grow(m: re.Match) -> str:
        h = int(m.group("h"))
        return m.group(0).replace(f'height="{h}"', f'height="{int(round(h * 1.3))}"', 1)

    svg = re.sub(r'<foreignObject[^>]*?height="(?P<h>\d+)"[^>]*>', grow, svg)
    return f'<div class="mermaid-fig">{svg}</div>'


PRINT_CSS = """
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { font-family: Georgia, "Palatino Linotype", Palatino, "Times New Roman", serif;
       font-size: 10.5pt; line-height: 1.55; color: #1c1c1c; max-width: 100%; margin: 0;
       text-align: left; hyphens: manual; -webkit-hyphens: manual; }
p, li { text-align: left; }
h1,h2,h3,h4,h5 { font-family: Georgia, Palatino, serif; color: #111; line-height: 1.25;
       page-break-after: avoid; font-weight: 700; }
h1 { font-size: 21pt; margin: 0 0 .4em; }
h2 { font-size: 17pt; margin: 1.9em 0 .5em; }
h3 { font-size: 13pt; margin: 1.3em 0 .35em; }
h4 { font-size: 11.5pt; margin: 1em 0 .25em; color: #333; }
p { margin: 0 0 .75em; }
p,li { orphans: 3; widows: 3; }
a { color: #1a4f8a; text-decoration: none; word-break: break-word; }
table { border-collapse: collapse; margin: 1em 0; width: 100%; font-size: 9.6pt; page-break-inside: avoid; }
th,td { border: 0; border-bottom: 1px solid #e4e4e4; padding: 6px 9px; vertical-align: top; text-align: left; }
th { font-weight: 700; border-bottom: 1.5px solid #bbb; }
code { font-family: "SF Mono", Menlo, Consolas, monospace; font-size: .9em; }
pre code { display: block; padding: 8px 10px; background: #f6f6f6; border-radius: 3px; }
blockquote { border-left: 2px solid #bbb; color: #444; margin: .8em 0; padding: .15em .95em; }
hr { border: 0; border-top: 1px solid #e4e4e4; margin: 1.6em 0; }
.mermaid-fig { margin: 1em 0; text-align: center; page-break-inside: avoid; }
.mermaid-fig svg { max-width: 100%; height: auto; }
/* Title page — centered, clean serif, its own page */
#title-block-header { text-align: center; padding-top: 22vh; page-break-after: always; }
#title-block-header .title { font-size: 33pt; line-height: 1.12; margin: 0 auto; max-width: 92%; font-weight: 700; }
#title-block-header .subtitle { font-size: 14.5pt; font-weight: 400; font-style: italic; color: #555;
       margin: 1.1em auto 0; max-width: 80%; line-height: 1.4; }
#title-block-header .author { font-size: 11.5pt; color: #333; margin-top: 2.2em; }
#title-block-header .date { font-size: 10.5pt; color: #777; margin-top: .4em; }
/* Table of contents — its own page, links preserved as PDF anchors */
nav#TOC { page-break-after: always; }
nav#TOC::before { content: "Contents"; display: block; font-size: 19pt; font-weight: 700;
       font-family: Georgia, serif; margin: 0 0 .8em; }
nav#TOC ul { list-style: none; padding-left: 1.3em; line-height: 1.95; }
nav#TOC > ul { padding-left: 0; }
nav#TOC a { color: #1c1c1c; text-decoration: none; }
"""


def pandoc_html(md: str, title: str, brief: str | None, tmp: Path,
                toc: bool = True, title_page: bool = True,
                author: str | None = None, date: str | None = None) -> Path:
    src = tmp / "clean.md"
    out = tmp / "out.html"
    src.write_text(md)
    cmd = ["pandoc", "-f", "gfm+raw_html+tex_math_dollars", "-t", "html",
           "--standalone", "--wrap=none",
           "--metadata", f"title={title}", "--metadata", "lang=en"]
    if title_page:
        if brief:
            cmd += ["--metadata", f"subtitle={brief}"]   # renders under the title
        if author:
            cmd += ["--metadata", f"author={author}"]
        if date:
            cmd += ["--metadata", f"date={date}"]
    if toc:
        cmd += ["--toc", "--toc-depth=2"]
    cmd += ["-o", str(out), str(src)]
    subprocess.run(cmd, check=True)
    html = out.read_text()
    if not title_page:
        # no dedicated title page: drop pandoc's title block (old behavior)
        html = re.sub(r'<header id="title-block-header">.*?</header>', "", html, count=1, flags=re.DOTALL)
    html = html.replace("</head>", f"<style>{PRINT_CSS}</style>\n</head>", 1)
    final = tmp / "final.html"
    final.write_text(html)
    return final


def cdp_pdf(html: Path, out_pdf: Path, chrome: str,
            logo: str | None, footer: str | None) -> None:
    """Render to PDF. Prefer the CDP helper (node) — it paginates correctly and
    gives a custom logo header + copyright footer with NO file-path stamp. Fall
    back to the Chrome CLI (old headless, which at least paginates) if node is
    absent, warning that the logo/footer customization is unavailable there."""
    script = Path(__file__).resolve().parent / "cdp_print.js"
    if shutil.which("node") and script.exists():
        cmd = ["node", str(script), "--html", str(html), "--out", str(out_pdf),
               "--chrome", chrome]
        if logo and Path(logo).exists():
            cmd += ["--logo", logo]
        if footer:
            cmd += ["--footer", footer]
        subprocess.run(cmd, check=True)
        return
    log("node not found — falling back to Chrome CLI (no logo header / custom footer). "
        "Install Node to enable them.")
    # --headless=old + compositor flag paginates correctly; --headless=new truncates.
    subprocess.run([chrome, "--headless=old", "--disable-gpu", "--no-sandbox",
                    "--hide-scrollbars", "--run-all-compositor-stages-before-draw",
                    "--virtual-time-budget=10000",
                    f"--print-to-pdf={out_pdf}", f"file://{html}"],
                   check=True, capture_output=True)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", type=Path)
    ap.add_argument("--format", choices=["pdf", "html", "md"], default="pdf")
    ap.add_argument("--out", type=Path, help="output directory (default: alongside source)")
    ap.add_argument("--chrome")
    ap.add_argument("--title")
    ap.add_argument("--brief", help="title-page brief/subtitle (overrides frontmatter)")
    ap.add_argument("--author", help="title-page byline (else public_doc.author / brand.yml)")
    ap.add_argument("--date", help="title-page date line (else public_doc.updated)")
    ap.add_argument("--logo", help="PNG/SVG logo for the running page header (else brand.yml)")
    ap.add_argument("--footer", help="footer copyright line (else brand.yml copyright)")
    ap.add_argument("--no-toc", action="store_true", help="omit the table-of-contents page")
    ap.add_argument("--no-title-page", action="store_true", help="omit the dedicated title page")
    args = ap.parse_args()

    if not args.input.exists():
        print(f"error: input not found: {args.input}", file=sys.stderr)
        return 1

    raw = args.input.read_text()
    brand = read_brand()
    title = args.title or read_meta_title(raw) or args.input.stem
    brief = args.brief or read_meta_brief(raw)
    author = args.author or read_meta_field(raw, "author") or brand.get("author")
    # Title-page version line: compose status + version + date so a draft is
    # always marked as such (e.g. "Draft · v0.4 · 2026-06-29"). An explicit
    # --date overrides the whole composition.
    date = args.date
    if not date:
        updated = read_meta_field(raw, "updated")
        status = read_meta_field(raw, "status")
        version = read_meta_field(raw, "version")
        parts = []
        if status:
            parts.append(status.strip().capitalize())
        if version:
            parts.append(f"v{version}")
        if updated:
            parts.append(str(updated))
        date = " · ".join(parts) if parts else updated
    logo = args.logo or brand.get("logo")
    footer = args.footer or brand.get("copyright")
    stem = read_public_filename(raw, args.input.stem)
    out_dir = args.out or args.input.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. strip (leak-safe). keep_title=False: the draft body already opens with an
    # H1 (the template convention), and the title is passed to pandoc via metadata
    # for the <title> tag — re-injecting it would duplicate the visible heading.
    try:
        cleaned, _ = strip(raw, keep_title=False)
    except ValueError as e:
        print(f"error (malformed draft): {e}", file=sys.stderr)
        return 3
    except RuntimeError as e:
        print(f"error (leak): {e}", file=sys.stderr)
        return 2
    log(f"stripped INTERNAL + metadata; title={title!r}")

    # 2. md
    if args.format == "md":
        out_md = out_dir / f"{stem}.public.md"
        out_md.write_text(cleaned)
        log(f"wrote {out_md}")
        print(str(out_md))
        return 0

    # external-tool preflight
    if not shutil.which("pandoc"):
        print("error: pandoc not found — needed for html/pdf. Install pandoc, or use --format md.",
              file=sys.stderr)
        return 4

    tmp = out_dir / ".tmp" / "public-doc-render"
    tmp.mkdir(parents=True, exist_ok=True)
    chrome = find_chrome(args.chrome)

    # 3. mermaid
    md_s, blocks = extract_mermaid(cleaned)
    if blocks:
        if not shutil.which("npx"):
            print("error: doc has mermaid diagrams but npx (for mermaid-cli) not found. "
                  "Install Node, or remove mermaid, or use --format md.", file=sys.stderr)
            return 4
        log(f"rendering {len(blocks)} mermaid diagram(s)")
        for i, b in enumerate(blocks):
            md_s = md_s.replace(f"<!--MERMAID_BLOCK_{i}-->", render_mermaid(b, i, tmp, chrome), 1)
    cleaned = md_s

    # 4. html
    html = pandoc_html(cleaned, title, brief, tmp,
                       toc=not args.no_toc, title_page=not args.no_title_page,
                       author=author, date=date)
    if args.format == "html":
        out_html = out_dir / f"{stem}.html"
        shutil.copy(html, out_html)
        log(f"wrote {out_html}")
        print(str(out_html))
        return 0

    # 5. pdf
    if not chrome:
        print("error: no Chrome/Chromium found for PDF. Set $PUBLIC_DOC_CHROME or --chrome, "
              "or use --format html. Looked at: " + ", ".join(c for c in CHROME_CANDIDATES if c),
              file=sys.stderr)
        return 4
    out_pdf = out_dir / f"{stem}.pdf"
    cdp_pdf(html, out_pdf, chrome, logo, footer)
    size = out_pdf.stat().st_size
    log(f"wrote {out_pdf} ({size:,} bytes)")
    print(str(out_pdf))
    return 0


if __name__ == "__main__":
    sys.exit(main())
