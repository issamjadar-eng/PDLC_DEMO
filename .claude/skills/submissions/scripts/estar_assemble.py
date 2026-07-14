#!/usr/bin/env python3
"""
estar_assemble.py — assemble an eSTAR/PreSTAR attachment package from a filing's
crosswalk: gather sources, strip internal tiers, render draft exhibit PDFs,
lint them, and emit the completion guide — one command, one output folder.

Pipeline (per filing):
  crosswalk § B (+ supporting-briefs paragraph) → local markdown sources
    → strip internal tiers (HTML comments, 🔒 INTERNAL <details> containers,
      🔒-marked table columns) — the filed body is exactly what FDA sees
    → render a draft exhibit PDF per source (embedded TTF font, heading
      bookmarks/outline), normalized to PDF 1.7 via pikepdf
    → <out>/attachments/NNN_<Section>_<slug>.pdf (eCopy-style numbered names)
    → <out>/assembly-manifest.json  (what mapped where, source hashes, strip stats)
    → <out>/<template>-completion-guide.{json,md}  (via estar_completion_guide.py)
    → <out>/lint-report.json + human lint summary  (via estar_lint.py)

Draft-exhibit note: /docflow `export` (working-MD → formal DOCX/PDF) is Phase 2 /
not yet implemented; until it lands, these rendered PDFs are DRAFT exhibits for
package dry-runs and linting — the filing-time conversion of controlled documents
routes through the formal-doc pipeline.

Run under the eStar venv:  tools/estar/bootstrap.sh <this script> ...

Usage:
  estar_assemble.py --crosswalk CW.md --sectionmap MAP.json --out DIR
                    [--font /path/to/font.ttf] [--transmit-gate]
"""
import argparse, hashlib, json, os, re, subprocess, sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_FONTS = ["/System/Library/Fonts/Supplemental/Arial.ttf",
                 "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]


# ---------- crosswalk parsing (same table conventions as the linter/guide) ----------

def _table_after(md, heading_prefix):
    lines = md.splitlines()
    start = next((i for i, ln in enumerate(lines)
                  if ln.strip().startswith(heading_prefix)), None)
    if start is None:
        return None, None
    rows, in_tbl, end = [], False, start
    for j, ln in enumerate(lines[start + 1:], start + 1):
        s = ln.strip()
        if s.startswith("|"):
            in_tbl = True
            cells = [c.strip() for c in s.strip("|").split("|")]
            if set("".join(cells)) <= set("-: "):
                continue
            rows.append(cells)
            end = j
        elif in_tbl:
            break
    return (rows or None), end


def _section_token(cell):
    if "→" in cell:
        m = re.search(r"([A-Za-z][\w]*)", cell.rsplit("→", 1)[1])
        if m:
            return m.group(1)
    m = re.search(r"\*\*[^A-Za-z]*([A-Za-z][\w/]*)", cell)   # skip ⭐/emoji markers
    if m:
        return m.group(1)
    m = re.search(r"[A-Za-z][\w]*", cell)
    return m.group(0) if m else "Section"


MD_LINK = re.compile(r"\[[^\]]*\]\(([^)#\s]+\.md)\)")


def gather_sources(cw_md, cw_dir):
    """Return ordered [(section_token, resolved_md_path)] from § B in-scope/gap
    rows plus the 'Supporting briefs' paragraph (assigned to Questions)."""
    rows, end = _table_after(cw_md, "## B.")
    out, seen = [], set()
    if rows:
        hdr = rows[0]
        ap = next((i for i, h in enumerate(hdr) if "Applic" in h), 1)
        mo = next((i for i, h in enumerate(hdr) if "Mode" in h), 2)
        so = next((i for i, h in enumerate(hdr) if "source" in h.lower()), 3)
        for r in rows[1:]:
            if len(r) <= max(ap, mo, so) or "⛔" in r[ap]:
                continue
            # only rows whose Mode declares an attachment slot yield exhibits;
            # Structured-only rows are typed into the form, not attached
            if "attachment" not in r[mo].lower() and "📎" not in r[mo]:
                continue
            token = _section_token(r[0])
            for rel in MD_LINK.findall(r[so]):
                p = os.path.normpath(os.path.join(cw_dir, rel))
                if os.path.isfile(p) and p not in seen:
                    seen.add(p)
                    out.append((token, p))
    # supporting-briefs paragraph (PreSTAR: question-context attachments)
    m = re.search(r"\*\*Supporting briefs[^\n]*\*\*.*?(?=\n##|\Z)", cw_md, re.S)
    if m:
        for rel in MD_LINK.findall(m.group(0)):
            p = os.path.normpath(os.path.join(cw_dir, rel))
            if os.path.isfile(p) and p not in seen:
                seen.add(p)
                out.append(("Questions", p))
    return out


# ---------- internal-tier strip ----------

# Formal-exhibit symbol policy: emoji/dingbats in a filed body pull unembeddable
# bitmap fonts (e.g. AppleColorEmoji) into the PDF and read as informal to a
# reviewer. Transliterate the conventional ones; drop the rest.
_SYMBOL_MAP = {"✅": "Yes", "❌": "No", "⛔": "N/A", "⚠️": "[!]", "⚠": "[!]",
               "📎": "", "⭐": "", "🔒": "", "📤": "", "📝": "", "⏸️": "", "⏸": "",
               "📖": "", "🚧": "[draft]"}
# strip emoji/dingbat planes only — arrows (→), math (≥ ≤), interpunct etc. are
# real typographic characters present in common serif fonts; leave them alone
_NON_TEXT = re.compile("[\U0001F000-\U0001FAFF☀-➿⬀-⯿️]")


def sanitize_symbols(md):
    for k, v in _SYMBOL_MAP.items():
        md = md.replace(k, v)
    return _NON_TEXT.sub("", md)


def _is_fence(ln):
    t = ln.lstrip()
    return t.startswith("```") or t.startswith("~~~")


def strip_internal(md):
    """Strip the internal tiers — **fence-aware throughout**. A 🔒 container can
    contain fenced code, and fenced examples can contain comment/details-like
    text; a naive regex strip eats a fence delimiter and turns the rest of the
    document into one giant code block (renders as raw monospace markdown)."""
    stats = {"comments": 0, "containers": 0, "columns": 0}
    lines = md.splitlines()

    # pass 1 — HTML comments + 🔒 <details> containers (outside fences only)
    kept, i, in_fence = [], 0, False
    while i < len(lines):
        ln = lines[i]
        if _is_fence(ln):
            in_fence = not in_fence
            kept.append(ln)
            i += 1
            continue
        if in_fence:
            kept.append(ln)
            i += 1
            continue
        if "<!--" in ln:
            new, n = re.subn(r"<!--.*?-->", "", ln)
            stats["comments"] += n
            if "<!--" in new:                     # multi-line comment
                pre = new[:new.index("<!--")]
                j = i + 1
                while j < len(lines) and "-->" not in lines[j]:
                    j += 1
                post = lines[j].split("-->", 1)[1] if j < len(lines) else ""
                stats["comments"] += 1
                merged = (pre + post).rstrip()
                if merged.strip():
                    kept.append(merged)
                i = j + 1
                continue
            if new.strip() or not ln.strip():
                kept.append(new)
            i += 1
            continue
        if ln.lstrip().startswith("<details"):
            # find the matching closer, tracking fence state INSIDE the block
            j, depth, f2 = i + 1, 1, False
            while j < len(lines):
                t = lines[j].lstrip()
                if _is_fence(t):
                    f2 = not f2
                elif not f2:
                    if t.startswith("<details"):
                        depth += 1
                    elif t.startswith("</details"):
                        depth -= 1
                        if depth == 0:
                            break
                j += 1
            head = "\n".join(lines[i:min(i + 6, j + 1)])
            if "🔒" in head:
                stats["containers"] += 1
                i = j + 1
                continue
            kept.append(ln)                       # non-internal container: keep
            i += 1
            continue
        kept.append(ln)
        i += 1

    # pass 2 — 🔒-marked table columns + symbol policy (outside fences only)
    def flush(buf):
        if not buf:
            return []
        hdr = [c.strip() for c in buf[0].strip().strip("|").split("|")]
        drop = [k for k, h in enumerate(hdr) if "🔒" in h]
        if not drop:
            return buf
        stats["columns"] += len(drop)
        fixed = []
        for ln in buf:
            cells = [c for c in ln.strip().strip("|").split("|")]
            keep = [c for k, c in enumerate(cells) if k not in drop]
            fixed.append("| " + " | ".join(c.strip() for c in keep) + " |")
        return fixed

    out_lines, buf, in_fence = [], [], False
    for ln in kept:
        if _is_fence(ln):
            if buf:
                out_lines += flush(buf)
                buf = []
            in_fence = not in_fence
            out_lines.append(ln)
            continue
        if in_fence:
            out_lines.append(ln)                  # code verbatim — no sanitize
            continue
        if ln.strip().startswith("|"):
            buf.append(ln)                # RAW — flush needs 🔒 header markers
            continue
        if buf:
            out_lines += [sanitize_symbols(x) for x in flush(buf)]
            buf = []
        out_lines.append(sanitize_symbols(ln))
    if buf:
        out_lines += [sanitize_symbols(x) for x in flush(buf)]

    # collapse blank runs outside fences
    final, blanks, in_fence = [], 0, False
    for ln in out_lines:
        if _is_fence(ln):
            in_fence = not in_fence
            blanks = 0
            final.append(ln)
            continue
        if not in_fence and not ln.strip():
            blanks += 1
            if blanks > 1:
                continue
        else:
            blanks = 0
        final.append(ln)
    return "\n".join(final).strip() + "\n", stats


# ---------- document-reference resolution ----------

_LINK = re.compile(r"(!?)\[([^\]]*)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")


def resolve_refs(md, src_dir, pkg):
    """Resolve document references for a filed exhibit:
    - links to docs IN the package → textual cross-ref "(Attachment NNN)"
      (FDA PDF-spec navigation is per-document; cross-file links break once
      attachments are loaded into eSTAR slots — attachment numbers don't)
    - links to repo docs NOT in the package → link dropped, text kept, and the
      reference is REPORTED (assembly manifest + lint) so RA can disposition:
      mark it 🔒 INTERNAL in the source md, or add the doc to the package
    - http/mailto + same-doc #anchors kept; image paths absolutized so pandoc
      embeds them when rendering from a temp file."""
    stats = {"attachment_refs": 0, "external_kept": 0, "images_embedded": 0,
             "internal_dropped": []}
    out, in_fence = [], False
    for ln in md.splitlines():
        if _is_fence(ln):
            in_fence = not in_fence
            out.append(ln)
            continue
        if in_fence:
            out.append(ln)
            continue

        def sub(m):
            bang, text, target = m.groups()
            if target.startswith(("http://", "https://", "mailto:")):
                stats["external_kept"] += 1
                return m.group(0)
            if target.startswith("#"):
                return m.group(0)                  # same-doc nav — survives
            path = os.path.normpath(os.path.join(src_dir, target.split("#")[0]))
            if bang:                                # image
                if os.path.isfile(path):
                    stats["images_embedded"] += 1
                    return f"![{text}]({path})"
                stats["internal_dropped"].append({"text": text, "target": target,
                                                  "image": True})
                return f"[figure: {text}]" if text else ""
            if path in pkg:
                n, _ = pkg[path]
                stats["attachment_refs"] += 1
                return f"{text} (Attachment {n:03d})"
            stats["internal_dropped"].append({"text": text, "target": target})
            return text
        out.append(_LINK.sub(sub, ln))
    return "\n".join(out), stats


# ---------- draft PDF rendering ----------

_BMP = re.compile("[^\\u0020-\\uffff\\n]")   # strip non-BMP (emoji) + controls for TTF safety
_INLINE = re.compile(r"\*\*|__|`|(?<!\w)[*_](?!\s)|(?<!\s)[*_](?!\w)")


def _soften(text, limit=60):
    """Break unwrappable tokens (long URLs/paths) so multi_cell can wrap them."""
    out = []
    for tok in text.split(" "):
        while len(tok) > limit:
            out.append(tok[:limit])
            tok = tok[limit:]
        out.append(tok)
    return " ".join(out)


def _clean(text):
    return _soften(_BMP.sub("", _INLINE.sub("", text)).strip())


def render_pdf_docflow(md, title, out_path, header_tpl=None):
    """Preferred renderer: /docflow export (pandoc → DOCX → LibreOffice → PDF).
    Real typesetting — styled headings, proper lists/tables, embedded fonts,
    heading outline as PDF bookmarks. Returns page count."""
    import tempfile
    export = os.path.normpath(os.path.join(
        SCRIPT_DIR, "..", "..", "docflow", "scripts", "export_formal.py"))
    first = next((ln for ln in md.splitlines() if ln.strip()), "")
    if not first.startswith("# "):                 # give pandoc a document title
        md = f"# {title}\n\n{md}"
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as tf:
        tf.write(md)
        tmp_md = tf.name
    try:
        cmd = [sys.executable, export, tmp_md, "--format", "pdf",
               "--out", out_path, "--json"]
        if header_tpl:
            cmd += ["--header-text", header_tpl.replace("{title}", title)]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError(f"docflow export failed: {r.stderr[-500:]}")
        return json.loads(r.stdout).get("post", {}).get("pages", 0)
    finally:
        os.unlink(tmp_md)


def docflow_toolchain_present():
    import shutil as _sh
    return bool(_sh.which("pandoc") and (_sh.which("soffice") or _sh.which("libreoffice")))


_HTML_TAG = re.compile(r"^\s*</?(details|summary)[^>]*>\s*$")


def render_pdf(md, title, out_path, font_path):
    from fpdf import FPDF
    pdf = FPDF(format="letter")
    pdf.set_margins(20, 18, 20)
    pdf.set_auto_page_break(True, margin=18)
    fam = "helvetica"
    if font_path:
        pdf.add_font("Body", "", font_path)
        pdf.add_font("Body", "B", font_path)
        fam = "Body"
    pdf.add_page()
    first = next((ln for ln in md.splitlines() if ln.strip()), "")
    if not first.startswith("# "):        # body has no own H1 → render the title
        pdf.set_font(fam, "B", 15)
        pdf.multi_cell(0, 8, _clean(title), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)
    for raw in md.splitlines():
        s = raw.rstrip()
        if not s.strip():
            pdf.ln(2)
            continue
        # skip horizontal rules + residual html container tags (render as noise)
        if re.match(r"^\s*[-*_]{3,}\s*$", s) or _HTML_TAG.match(s):
            continue
        h = re.match(r"^(#{1,4})\s+(.*)", s)
        if h:
            level = len(h.group(1))
            text = _clean(h.group(2))
            if not text:
                continue
            pdf.start_section(text, level=level - 1)   # → PDF outline/bookmarks
            pdf.set_font(fam, "B", max(15 - level, 10))
            pdf.ln(2)
            pdf.multi_cell(0, 7, text, new_x="LMARGIN", new_y="NEXT")
            pdf.set_font(fam, "", 9.5)
            continue
        pdf.set_font(fam, "", 9.5)
        if s.strip().startswith("|"):
            cells = [_clean(c) for c in s.strip().strip("|").split("|")]
            if set("".join(cells)) <= set("-: ") or not any(cells):
                continue
            pdf.multi_cell(0, 5, "   " + "  ·  ".join(c for c in cells if c), new_x="LMARGIN", new_y="NEXT")
        elif s.strip().startswith(">"):
            # blockquote — indented plain text, not a bullet
            txt = _clean(s.strip().lstrip("> "))
            if txt:
                pdf.multi_cell(0, 5, "    " + txt, new_x="LMARGIN", new_y="NEXT")
        elif s.strip().startswith(("-", "*")):
            txt = _clean(s.strip().lstrip("-* "))
            if txt:                                # never emit an empty bullet
                pdf.multi_cell(0, 5, "  • " + txt, new_x="LMARGIN", new_y="NEXT")
        else:
            txt = _clean(s)
            if txt:
                pdf.multi_cell(0, 5, txt, new_x="LMARGIN", new_y="NEXT")
    raw = bytes(pdf.output())
    # normalize to PDF 1.7 (linter admissibility window) via pikepdf
    import pikepdf, io
    with pikepdf.open(io.BytesIO(raw)) as p:
        n_pages = len(p.pages)
        p.save(out_path, min_version="1.7")
    return n_pages


# ---------- main ----------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--crosswalk", required=True)
    ap.add_argument("--sectionmap", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--font", default=next((f for f in DEFAULT_FONTS if os.path.isfile(f)), None))
    ap.add_argument("--header", default=None,
                    help='running-header template for exhibits, "{title}" interpolates '
                         '(e.g. "MedTech Co., Inc. — {title}")')
    ap.add_argument("--renderer", choices=["auto", "docflow", "fpdf2"], default="auto",
                    help="auto: /docflow export (pandoc+soffice) when present, else fpdf2")
    ap.add_argument("--transmit-gate", action="store_true")
    a = ap.parse_args()

    renderer = a.renderer
    if renderer == "auto":
        renderer = "docflow" if docflow_toolchain_present() else "fpdf2"

    cw_md = open(a.crosswalk).read()
    cw_dir = os.path.dirname(os.path.abspath(a.crosswalk))
    mapdata = json.load(open(a.sectionmap))
    tpl = f"{mapdata.get('template_id','tpl')}-{mapdata.get('template_version','v?')}"
    att_dir = os.path.join(a.out, "attachments")
    os.makedirs(att_dir, exist_ok=True)
    for stale in os.listdir(att_dir):                 # clear prior run's exhibits
        if re.match(r"\d{3}_.*\.pdf$", stale):
            os.remove(os.path.join(att_dir, stale))

    sources = gather_sources(cw_md, cw_dir)
    if not sources:
        print("no local markdown sources found in the crosswalk — nothing to assemble",
              file=sys.stderr)
        return 2

    manifest = {"template_id": mapdata.get("template_id"),
                "template_version": mapdata.get("template_version"),
                "crosswalk": os.path.relpath(a.crosswalk),
                "sectionmap": os.path.relpath(a.sectionmap),
                "renderer": renderer, "header": a.header,
                "font_embedded": bool(a.font) or renderer == "docflow",
                "note": ("DRAFT exhibits rendered from the stripped filed body of each "
                         "working markdown source; filing-time conversion of controlled "
                         "documents routes through the formal-doc pipeline "
                         "(/docflow export, Phase 2)."),
                "attachments": []}

    # pass 1 — assign attachment numbers + names, build the package map so
    # cross-references can resolve forward AND backward
    entries, pkg = [], {}
    for idx, (section, src) in enumerate(sources, 1):
        stem = os.path.splitext(os.path.basename(src))[0]
        if re.fullmatch(r"v?\d+([.-]\d+)*", stem):     # versioned leaf (v1.0.0.md) → use folder name
            stem = os.path.basename(os.path.dirname(src))
        slug = re.sub(r"[^A-Za-z0-9]+", "-", stem).strip("-")
        sec_safe = re.sub(r"[^A-Za-z0-9]+", "", section) or "Section"
        # spec § NAMING (FDA PDF Specifications): lowercase; only - and _
        fname = f"{idx:03d}_{sec_safe}_{slug}.pdf".lower()
        entries.append((idx, section, src, fname))
        pkg[os.path.normpath(os.path.abspath(src))] = (idx, fname)

    # pass 2 — strip, resolve references, render
    for idx, section, src, fname in entries:
        raw_md = open(src).read()
        body, stats = strip_internal(raw_md)
        body, refs = resolve_refs(body, os.path.dirname(os.path.abspath(src)), pkg)
        m = re.search(r"^#\s+(.+)$", body, re.M)
        title = m.group(1).strip() if m else os.path.splitext(os.path.basename(src))[0]
        out_path = os.path.join(att_dir, fname)
        if renderer == "docflow":
            pages = render_pdf_docflow(body, title, out_path, a.header)
        else:
            pages = render_pdf(body, title, out_path, a.font)
        manifest["attachments"].append({
            "n": idx, "section": section, "title": title,
            "source": os.path.relpath(src),
            "source_sha256": hashlib.sha256(raw_md.encode()).hexdigest()[:16],
            "output": os.path.join("attachments", fname), "pages": pages,
            "stripped": stats, "refs": refs})
        drop = len(refs["internal_dropped"])
        print(f"  [{idx:03d}] {section:24s} {os.path.basename(src):44s} → {fname} "
              f"({pages}p; -{stats['comments']}c/-{stats['containers']}🔒/-{stats['columns']}col; "
              f"refs {refs['attachment_refs']}→att"
              + (f", {drop} internal-dropped" if drop else "") + ")")

    with open(os.path.join(a.out, "assembly-manifest.json"), "w") as fh:
        json.dump(manifest, fh, indent=2)
        fh.write("\n")

    # completion guide into the same output folder
    guide_base = os.path.join(a.out, f"{tpl}-completion-guide")
    subprocess.run([sys.executable, os.path.join(SCRIPT_DIR, "estar_completion_guide.py"),
                    "--sectionmap", a.sectionmap, "--crosswalk", a.crosswalk,
                    "--assembly-manifest", os.path.join(a.out, "assembly-manifest.json"),
                    "--out-json", guide_base + ".json", "--out-md", guide_base + ".md"],
                   check=True)

    # lint the assembled attachments (JSON report + human output)
    lint = [sys.executable, os.path.join(SCRIPT_DIR, "estar_lint.py"),
            "--sectionmap", a.sectionmap, "--crosswalk", a.crosswalk,
            "--attachments", att_dir]
    if a.transmit_gate:
        lint.append("--transmit-gate")
    with open(os.path.join(a.out, "lint-report.json"), "w") as fh:
        subprocess.run(lint + ["--json"], stdout=fh)
    rc = subprocess.run(lint).returncode

    print(f"\nassembled {len(manifest['attachments'])} exhibit(s) → {a.out}")
    return rc


if __name__ == "__main__":
    sys.exit(main())
