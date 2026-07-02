#!/usr/bin/env python3
"""
export_formal.py — /docflow export: working markdown → formal DOCX or PDF.

The export half of docflow's round-trip model (WF-1/WF-2): pandoc renders the
markdown to DOCX (real typesetting — styled headings, proper lists, tables);
for PDF, LibreOffice converts the DOCX headlessly (embedding fonts and exporting
the heading outline as PDF bookmarks). An optional post-pass (pikepdf, if
importable in the invoking interpreter) normalizes the PDF version floor —
useful when the PDF must satisfy an electronic-submission admissibility window
(e.g. FDA eSTAR attachments: PDF 1.4–1.7, no encryption, bookmarks, embedded
fonts).

Deterministic + project-agnostic: stdlib only; external tools are the docflow
toolchain (pandoc, soffice). The caller owns any content preparation (e.g.
stripping internal-tier containers) — export converts exactly what it is given.

Usage:
  export_formal.py <input.md> --format docx|pdf [--out PATH] [--title T]
                   [--reference-doc REF.docx] [--min-pdf-version 1.7]
                   [--keep-docx] [--json]
Exit: 0 ok · 2 toolchain missing · 3 conversion failed.
"""
import argparse, json, os, shutil, subprocess, sys, tempfile


def which(*names):
    for n in names:
        p = shutil.which(n)
        if p:
            return p
    return None


def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        sys.stderr.write(r.stdout[-2000:] + r.stderr[-2000:])
        raise RuntimeError(f"{os.path.basename(cmd[0])} failed ({r.returncode})")
    return r


def md_to_docx(pandoc, src, docx_out, title=None, reference_doc=None):
    cmd = [pandoc, src, "-f", "gfm", "-t", "docx", "-o", docx_out]
    if title:
        cmd += ["--metadata", f"title={title}"]
    if reference_doc:
        cmd += ["--reference-doc", reference_doc]
    run(cmd)


# ---------- house-style DOCX post-process (readability rules) ----------
# Basis: the FDA "PDF Specifications" (v4.1, Sep 2016 — nonbinding, adopted as
# the house standard; a consuming project's applicability file records scope):
# Times New Roman 12pt narrative, sizes 9–12pt (tables 9–10), black text/blue
# links, fully-embedded fonts, 8.5x11 with left ≥3/4in & others ≥3/8in (our
# 1in margins exceed both), TOC/bookmarks for docs ≥5 pages.

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
PAGE_CONTENT_TWIPS = 9360          # Letter 8.5in − 2×1in margins = 6.5in
MIN_COL_FRACTION = 0.07            # no column starves below 7% of the width
HEADER_SHADE = "EDEDED"            # header-row fill — table anatomy visible
BORDER = {"val": "single", "sz": "4", "space": "0", "color": "808080"}

# OOXML child-order (Word validates; LO is lenient) — sorted after edits
_TBLPR_ORDER = ["tblStyle", "tblpPr", "tblOverlap", "bidiVisual",
                "tblStyleRowBandSize", "tblStyleColBandSize", "tblW", "jc",
                "tblCellSpacing", "tblInd", "tblBorders", "shd", "tblLayout",
                "tblCellMar", "tblLook", "tblCaption", "tblDescription"]
_TRPR_ORDER = ["cnfStyle", "divId", "gridBefore", "gridAfter", "wBefore",
               "wAfter", "cantSplit", "trHeight", "tblHeader",
               "tblCellSpacing", "jc", "hidden"]
_TCPR_ORDER = ["cnfStyle", "tcW", "gridSpan", "hMerge", "vMerge", "tcBorders",
               "shd", "noWrap", "tcMar", "textDirection", "tcFitText",
               "vAlign", "hideMark"]


def _w(tag):
    return f"{{{W_NS}}}{tag}"


def _sort_pr(pr, order):
    kids = sorted(list(pr), key=lambda e: (
        order.index(e.tag.split("}")[1]) if e.tag.split("}")[1] in order else len(order)))
    for k in list(pr):
        pr.remove(k)
    for k in kids:
        pr.append(k)


def _restyle_tables(root):
    """Margin-to-margin tables with content-weighted column widths.
    Pandoc emits even grids + type=auto width; converters render them narrow
    and evenly split (whitespace in short columns, crunched multi-line cells).
    Reweight each grid by column text volume, fixed layout, full page width."""
    import xml.etree.ElementTree as ET
    parent = {c: p for p in root.iter() for c in p}
    n = 0
    for tbl in root.iter(_w("tbl")):
        # skip nested tables — their width is relative to the containing cell
        anc = parent.get(tbl)
        nested = False
        while anc is not None:
            if anc.tag == _w("tc"):
                nested = True
                break
            anc = parent.get(anc)
        if nested:
            continue
        grid = tbl.find(_w("tblGrid"))
        if grid is None:
            continue
        cols = grid.findall(_w("gridCol"))
        ncols = len(cols)
        if ncols < 2:
            continue
        # column text metrics (header + data cells):
        #   totals  — text volume, drives proportional sharing
        #   maxdata — longest DATA cell (headers may wrap between words; data
        #             decides whether a column is "short"/exact-fit)
        #   maxword — longest unbreakable token anywhere in the column
        #             (incl. header) — the hard floor that prevents the
        #             letter-stacking / mid-word-break failure mode
        totals = [0.0] * ncols
        maxdata = [0] * ncols
        maxword = [0] * ncols
        rows = list(tbl.iter(_w("tr")))
        for ri, tr in enumerate(rows):
            ci = 0
            for tc in tr.findall(_w("tc")):
                span = 1
                tcpr = tc.find(_w("tcPr"))
                if tcpr is not None:
                    gs = tcpr.find(_w("gridSpan"))
                    if gs is not None:
                        span = int(gs.get(_w("val"), "1"))
                if span == 1 and ci < ncols:
                    text = "".join(t.text or "" for t in tc.iter(_w("t")))
                    totals[ci] += len(text)
                    if ri > 0:
                        maxdata[ci] = max(maxdata[ci], len(text))
                    for tok in text.split():
                        maxword[ci] = max(maxword[ci], min(len(tok), 20))
                ci += span
        CHAR_TW, PAD_TW, SHORT_LIMIT = 115, 420, 14
        min_w = [max(maxword[i] * CHAR_TW + PAD_TW, 700) for i in range(ncols)]
        short = [i for i in range(ncols) if maxdata[i] <= SHORT_LIMIT]
        widths = [0] * ncols
        for i in range(ncols):
            if i in short:
                # exact fit for the data; header wraps between words above it,
                # but never below the longest-word floor
                widths[i] = max(maxdata[i] * CHAR_TW + PAD_TW, min_w[i])
            else:
                widths[i] = min_w[i]
        # distribute the remaining width to long columns by text volume
        rest = PAGE_CONTENT_TWIPS - sum(widths)
        longs = [i for i in range(ncols) if i not in short]
        if rest > 0 and longs:
            tot = sum(totals[i] for i in longs) or 1.0
            for i in longs:
                widths[i] += int(rest * totals[i] / tot)
        elif rest > 0:                          # all short → spread the slack
            slack = rest // ncols
            widths = [wd + slack for wd in widths]
        elif rest < 0:                          # over-constrained → scale down
            f = PAGE_CONTENT_TWIPS / float(sum(widths))
            widths = [max(int(wd * f), 700) for wd in widths]
        widths[-1] += PAGE_CONTENT_TWIPS - sum(widths)      # rounding remainder
        # apply: full-width fixed-layout table + per-column/cell widths
        tblpr = tbl.find(_w("tblPr"))
        if tblpr is None:
            tblpr = ET.Element(_w("tblPr"))
            tbl.insert(0, tblpr)
        for tag in ("tblW", "tblLayout"):
            el = tblpr.find(_w(tag))
            if el is not None:
                tblpr.remove(el)
        et_w = ET.SubElement(tblpr, _w("tblW"))
        et_w.set(_w("w"), str(PAGE_CONTENT_TWIPS))
        et_w.set(_w("type"), "dxa")
        et_l = ET.SubElement(tblpr, _w("tblLayout"))
        et_l.set(_w("type"), "fixed")
        for col, wd in zip(cols, widths):
            col.set(_w("w"), str(wd))
        for tr in tbl.iter(_w("tr")):
            ci = 0
            for tc in tr.findall(_w("tc")):
                tcpr = tc.find(_w("tcPr"))
                if tcpr is None:
                    tcpr = ET.Element(_w("tcPr"))
                    tc.insert(0, tcpr)
                span = 1
                gs = tcpr.find(_w("gridSpan"))
                if gs is not None:
                    span = int(gs.get(_w("val"), "1"))
                tw = tcpr.find(_w("tcW"))
                if tw is None:
                    tw = ET.SubElement(tcpr, _w("tcW"))
                tw.set(_w("w"), str(sum(widths[ci:ci + span]) if ci + span <= ncols
                                    else widths[-1]))
                tw.set(_w("type"), "dxa")
                ci += span
        # ---- table anatomy: borders + header shading/repeat + row integrity.
        # FDA has no table-format guidance; house rules for reviewer
        # readability, esp. tables spanning pages: visible gridlines, shaded
        # header repeated on every page, rows never split across a break.
        import xml.etree.ElementTree as ET
        tb = tblpr.find(_w("tblBorders"))
        if tb is None:
            tb = ET.SubElement(tblpr, _w("tblBorders"))
        for side in ("top", "left", "bottom", "right", "insideH", "insideV"):
            el = tb.find(_w(side))
            if el is None:
                el = ET.SubElement(tb, _w(side))
            for k, v in BORDER.items():
                el.set(_w(k), v)
        _sort_pr(tblpr, _TBLPR_ORDER)
        for ri, tr in enumerate(rows):
            trpr = tr.find(_w("trPr"))
            if trpr is None:
                trpr = ET.Element(_w("trPr"))
                tr.insert(0, trpr)
            if trpr.find(_w("cantSplit")) is None:
                ET.SubElement(trpr, _w("cantSplit"))
            if ri == 0:
                if trpr.find(_w("tblHeader")) is None:
                    ET.SubElement(trpr, _w("tblHeader"))   # repeat on each page
                for tc in tr.findall(_w("tc")):
                    tcpr = tc.find(_w("tcPr"))
                    if tcpr is None:
                        tcpr = ET.Element(_w("tcPr"))
                        tc.insert(0, tcpr)
                    shd = tcpr.find(_w("shd"))
                    if shd is None:
                        shd = ET.SubElement(tcpr, _w("shd"))
                    shd.set(_w("val"), "clear")
                    shd.set(_w("color"), "auto")
                    shd.set(_w("fill"), HEADER_SHADE)
                    _sort_pr(tcpr, _TCPR_ORDER)
            _sort_pr(trpr, _TRPR_ORDER)
        n += 1
    return n


def _restyle_codeblocks(root):
    """ASCII art / code blocks: fit-to-width mono sizing + keep-together.
    Pandoc renders a code block as one SourceCode paragraph with <w:br/> line
    breaks; at body size, wide ASCII diagrams wrap mid-line (mangled art) and
    split across page boundaries. Compute each block's longest line and size
    it to fit the 6.5in text width (mono advance ≈ 0.6em), floor 6pt, cap
    9.5pt; add keepLines so a block stays on one page when it fits."""
    import xml.etree.ElementTree as ET
    n = 0
    for p in root.iter(_w("p")):
        ppr = p.find(_w("pPr"))
        st = ppr.find(_w("pStyle")) if ppr is not None else None
        if st is None or st.get(_w("val")) not in ("SourceCode", "VerbatimChar"):
            continue
        lines = [[]]
        for r in p.iter(_w("r")):
            for ch in r:
                if ch.tag == _w("br"):
                    lines.append([])
                elif ch.tag == _w("t"):
                    lines[-1].append(ch.text or "")
        maxw = max((len("".join(l)) for l in lines), default=0)
        if maxw == 0:
            continue
        size_pt = max(6.0, min(9.5, (PAGE_CONTENT_TWIPS / 20.0) / (maxw * 0.6)))
        half = str(int(size_pt * 2))
        for r in p.findall(_w("r")):
            rpr = r.find(_w("rPr"))
            if rpr is None:
                rpr = ET.Element(_w("rPr"))
                r.insert(0, rpr)
            for tag in ("sz", "szCs"):
                el = rpr.find(_w(tag))
                if el is None:
                    el = ET.SubElement(rpr, _w(tag))
                el.set(_w("val"), half)
        if ppr.find(_w("keepLines")) is None:
            ET.SubElement(ppr, _w("keepLines"))
        # pPr schema order: keepNext, keepLines, ... then pStyle first overall
        kids = sorted(list(ppr), key=lambda e: 0 if e.tag == _w("pStyle") else
                      (1 if e.tag in (_w("keepNext"), _w("keepLines")) else 2))
        for k in list(ppr):
            ppr.remove(k)
        for k in kids:
            ppr.append(k)
        n += 1
    return n


def _restyle_fonts(styles_xml, family, half_points):
    """Serif throughout (FDA PDF-spec recommendation): set the font family on
    docDefaults and EVERY style — headings included — except code/verbatim
    styles, which keep their monospace. Body size applies to docDefaults +
    body styles only; heading sizes keep their hierarchy."""
    import re as _re
    out, count = styles_xml, 0
    CODE = _re.compile(r'w:styleId="[^"]*(Verbatim|SourceCode|Code|Macro)[^"]*"', _re.I)
    BODY = _re.compile(r'w:styleId="(Normal|BodyText|Compact|FirstParagraph|TableText)"')

    def font_sub(m):
        nonlocal count
        count += 1
        return (f'<w:rFonts w:ascii="{family}" w:hAnsi="{family}" '
                f'w:eastAsia="{family}" w:cs="{family}"/>')

    for block in _re.finditer(
            r'(<w:docDefaults>.*?</w:docDefaults>|<w:style [^>]*>.*?</w:style>)',
            styles_xml, _re.S):
        seg = block.group(0)
        if CODE.search(seg):
            continue                              # monospace stays monospace
        new = _re.sub(r"<w:rFonts [^/]*/>", font_sub, seg)
        if seg.startswith("<w:docDefaults") or BODY.search(seg):
            new = _re.sub(r'<w:sz w:val="\d+"\s*/>', f'<w:sz w:val="{half_points}"/>', new)
            new = _re.sub(r'<w:szCs w:val="\d+"\s*/>', f'<w:szCs w:val="{half_points}"/>', new)
        out = out.replace(seg, new)
    return out, count



FOOTER_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:ftr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
<w:p><w:pPr><w:jc w:val="center"/><w:rPr><w:sz w:val="20"/></w:rPr></w:pPr>
<w:r><w:rPr><w:sz w:val="20"/></w:rPr><w:t xml:space="preserve">Page </w:t></w:r>
<w:r><w:rPr><w:sz w:val="20"/></w:rPr><w:fldChar w:fldCharType="begin"/></w:r>
<w:r><w:rPr><w:sz w:val="20"/></w:rPr><w:instrText xml:space="preserve"> PAGE </w:instrText></w:r>
<w:r><w:rPr><w:sz w:val="20"/></w:rPr><w:fldChar w:fldCharType="end"/></w:r>
<w:r><w:rPr><w:sz w:val="20"/></w:rPr><w:t xml:space="preserve"> of </w:t></w:r>
<w:r><w:rPr><w:sz w:val="20"/></w:rPr><w:fldChar w:fldCharType="begin"/></w:r>
<w:r><w:rPr><w:sz w:val="20"/></w:rPr><w:instrText xml:space="preserve"> NUMPAGES </w:instrText></w:r>
<w:r><w:rPr><w:sz w:val="20"/></w:rPr><w:fldChar w:fldCharType="end"/></w:r>
</w:p></w:ftr>"""

R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"

HEADER_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:hdr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
<w:p><w:pPr><w:jc w:val="right"/><w:rPr><w:sz w:val="18"/></w:rPr></w:pPr>
<w:r><w:rPr><w:sz w:val="18"/></w:rPr><w:t xml:space="preserve">{TEXT}</w:t></w:r>
</w:p></w:hdr>"""


def add_running_header(data, text):
    """Small, tasteful running header (right-aligned, 9pt — the spec's minimum
    narrative size; content stays outside the outer 3/8in per § PAGE SIZE AND
    MARGINS). Typical use: "<Sponsor> — <Document Title>"."""
    from xml.sax.saxutils import escape
    data["word/header1.xml"] = HEADER_XML.replace("{TEXT}", escape(text)).encode("utf-8")
    ct = data["[Content_Types].xml"].decode("utf-8")
    if "header1.xml" not in ct:
        ct = ct.replace("</Types>",
            '<Override PartName="/word/header1.xml" ContentType='
            '"application/vnd.openxmlformats-officedocument.wordprocessingml.header+xml"/></Types>')
        data["[Content_Types].xml"] = ct.encode("utf-8")
    rels = data["word/_rels/document.xml.rels"].decode("utf-8")
    if 'Target="header1.xml"' not in rels:
        rels = rels.replace("</Relationships>",
            '<Relationship Id="rIdHeaderHS" Type="http://schemas.openxmlformats.org/'
            'officeDocument/2006/relationships/header" Target="header1.xml"/></Relationships>')
        data["word/_rels/document.xml.rels"] = rels.encode("utf-8")
    import re as _re
    doc = data["word/document.xml"].decode("utf-8")
    if "headerReference" not in doc:
        doc = _re.sub(r"<w:sectPr(\s[^>]*)?>",
                      lambda m: m.group(0) + '<w:headerReference '
                      f'xmlns:r="{R_NS}" w:type="default" r:id="rIdHeaderHS"/>',
                      doc, count=1)
        data["word/document.xml"] = doc.encode("utf-8")
    return True


def add_page_footer(data):
    """Page-number footer per the FDA PDF Specifications: § PAGE NUMBERING
    expects the document page = PDF page, first page = 1; § PAGE SIZE AND
    MARGINS keeps header/footer content outside the outer 3/8in (the standard
    0.5in footer position complies). Centered "Page N of M", 10pt."""
    import re as _re
    import xml.etree.ElementTree as ET
    data["word/footer1.xml"] = FOOTER_XML.encode("utf-8")
    # content type
    ct = data["[Content_Types].xml"].decode("utf-8")
    if "footer1.xml" not in ct:
        ct = ct.replace("</Types>",
            '<Override PartName="/word/footer1.xml" ContentType='
            '"application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/></Types>')
        data["[Content_Types].xml"] = ct.encode("utf-8")
    # relationship
    rels = data["word/_rels/document.xml.rels"].decode("utf-8")
    if 'Target="footer1.xml"' not in rels:
        rels = rels.replace("</Relationships>",
            '<Relationship Id="rIdFooterHS" Type="http://schemas.openxmlformats.org/'
            'officeDocument/2006/relationships/footer" Target="footer1.xml"/></Relationships>')
        data["word/_rels/document.xml.rels"] = rels.encode("utf-8")
    # sectPr reference (footerReference must lead the sectPr children)
    doc = data["word/document.xml"].decode("utf-8")
    if "footerReference" not in doc:
        doc = _re.sub(r"<w:sectPr(\s[^>]*)?>",
                      lambda m: m.group(0) + '<w:footerReference '
                      f'xmlns:r="{R_NS}" w:type="default" r:id="rIdFooterHS"/>',
                      doc, count=1)
        data["word/document.xml"] = doc.encode("utf-8")
    return True

def apply_house_style(docx_path, family, size_pt, header_text=None):
    """Post-process the pandoc DOCX: full-width content-weighted tables +
    default body font. Returns stats dict."""
    import io, zipfile
    import xml.etree.ElementTree as ET
    ET.register_namespace("w", W_NS)
    with zipfile.ZipFile(docx_path) as z:
        names = z.namelist()
        data = {nm: z.read(nm) for nm in names}
    root = ET.fromstring(data["word/document.xml"])
    tables = _restyle_tables(root)
    codeblocks = _restyle_codeblocks(root)
    buf = io.BytesIO()
    ET.ElementTree(root).write(buf, xml_declaration=True, encoding="UTF-8")
    data["word/document.xml"] = buf.getvalue()
    fonts = 0
    if "word/styles.xml" in data and family:
        styled, fonts = _restyle_fonts(data["word/styles.xml"].decode("utf-8"),
                                       family, int(size_pt * 2))
        data["word/styles.xml"] = styled.encode("utf-8")
    footer = add_page_footer(data)
    header = add_running_header(data, header_text) if header_text else False
    with zipfile.ZipFile(docx_path, "w", zipfile.ZIP_DEFLATED) as z:
        for nm in list(dict.fromkeys(list(names) + [k for k in data if k not in names])):
            z.writestr(nm, data[nm])
    return {"tables_normalized": tables, "codeblocks_fitted": codeblocks,
            "font_runs_restyled": fonts, "body_font": family,
            "body_size_pt": size_pt, "page_footer": footer, "running_header": header}


def docx_to_pdf(soffice, docx_path, out_dir):
    # dedicated LO profile: no clash with a running LibreOffice instance
    profile = tempfile.mkdtemp(prefix="docflow-lo-")
    try:
        run([soffice, "--headless", "--norestore",
             f"-env:UserInstallation=file://{profile}",
             "--convert-to", "pdf", "--outdir", out_dir, docx_path])
    finally:
        shutil.rmtree(profile, ignore_errors=True)
    pdf = os.path.join(out_dir, os.path.splitext(os.path.basename(docx_path))[0] + ".pdf")
    if not os.path.isfile(pdf):
        raise RuntimeError("soffice reported success but produced no PDF")
    return pdf


def normalize_pdf(pdf_path, min_version):
    """Optional admissibility post-pass — silently skipped without pikepdf."""
    try:
        import pikepdf
    except ImportError:
        return {"normalized": False, "reason": "pikepdf not importable"}
    with pikepdf.open(pdf_path, allow_overwriting_input=True) as p:
        info = {"normalized": True, "pages": len(p.pages),
                "pdf_version_in": str(p.pdf_version),
                "encrypted": p.is_encrypted,
                "has_outline": "/Outlines" in p.Root and
                               bool(p.Root.get("/Outlines", {}).get("/First"))}
        p.save(pdf_path, min_version=min_version)
    return info


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("--format", choices=["docx", "pdf"], default="docx")
    ap.add_argument("--out", help="output path (default: alongside input)")
    ap.add_argument("--title")
    ap.add_argument("--reference-doc")
    ap.add_argument("--min-pdf-version", default="1.7")
    ap.add_argument("--keep-docx", action="store_true",
                    help="with --format pdf, keep the intermediate DOCX next to the PDF")
    ap.add_argument("--house-style", dest="house_style", action="store_true", default=True,
                    help="full-width content-weighted tables + body font (default on)")
    ap.add_argument("--no-house-style", dest="house_style", action="store_false")
    ap.add_argument("--body-font", default="Times New Roman",
                    help="body font family (FDA PDF-spec recommendation; headings/code keep style)")
    ap.add_argument("--body-size", type=float, default=12.0, help="body font size in points")
    ap.add_argument("--header-text", default=None,
                    help='small right-aligned 9pt running header, e.g. "<Sponsor> — <Title>"')
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    pandoc = which("pandoc")
    soffice = which("soffice", "libreoffice")
    if not pandoc or (a.format == "pdf" and not soffice):
        missing = [t for t, p in (("pandoc", pandoc), ("soffice", soffice)) if not p]
        print(f"toolchain missing: {', '.join(missing)} — see /docflow setup", file=sys.stderr)
        return 2

    src = os.path.abspath(a.input)
    base = os.path.splitext(os.path.basename(src))[0]
    default_out = os.path.join(os.path.dirname(src), f"{base}.{a.format}")
    out = os.path.abspath(a.out or default_out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    result = {"input": a.input, "format": a.format, "output": out, "steps": []}

    try:
        with tempfile.TemporaryDirectory(prefix="docflow-export-") as tmp:
            docx_path = out if a.format == "docx" else os.path.join(tmp, base + ".docx")
            md_to_docx(pandoc, src, docx_path, a.title, a.reference_doc)
            result["steps"].append("pandoc:md->docx")
            if a.house_style:
                result["house_style"] = apply_house_style(docx_path, a.body_font, a.body_size, a.header_text)
                result["steps"].append("house-style:tables+font")
            if a.format == "pdf":
                pdf = docx_to_pdf(soffice, docx_path, tmp)
                result["steps"].append("soffice:docx->pdf")
                shutil.move(pdf, out)
                if a.keep_docx:
                    kept = os.path.splitext(out)[0] + ".docx"
                    shutil.copy2(docx_path, kept)
                    result["docx"] = kept
                result["post"] = normalize_pdf(out, a.min_pdf_version)
                if result["post"].get("normalized"):
                    result["steps"].append(f"pikepdf:min-version={a.min_pdf_version}")
    except RuntimeError as e:
        print(f"export failed: {e}", file=sys.stderr)
        return 3

    print(json.dumps(result, indent=2) if a.json
          else f"exported: {out}" + (f"  ({result.get('post', {}).get('pages', '?')}p, "
               f"outline={result.get('post', {}).get('has_outline')})"
               if a.format == "pdf" else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
