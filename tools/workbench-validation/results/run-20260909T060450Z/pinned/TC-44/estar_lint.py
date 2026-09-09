#!/usr/bin/env python3
"""
estar_lint.py — eSTAR/PreSTAR package admissibility + coverage linter.

Advisory by default (reports findings, never blocks); `--transmit-gate` makes it
a hard gate (exit non-zero on any BLOCK finding) for a pre-transmission check.

Template-parameterized: it keys off a section-map (default: nIVD eSTAR v7.0) so
pointing it at PreSTAR (Q-Sub) later is just a different --sectionmap, not a
rewrite — the eSTAR/PreSTAR format family shares the same admissibility rules.

The FDA form itself is a dynamic XFA + JS PDF whose "eSTAR Complete" verify runs
only in Acrobat; this linter pre-flights everything a third party robustly can:
  1. structure   — section-map loads, version-pinned, totals sane
  2. attachments — each prepared exhibit PDF is eSTAR-admissible (format-correct)
  3. coverage    — every applicable attachment slot has a prepared exhibit
  4. accuracy    — the structured-answer accuracy set is complete, no [VERIFY]
  5. gaps        — open crosswalk gap→action items

Run under the eStar venv (tools/estar/.venv) — see the /submissions eStar setup.

Usage:
  estar_lint.py --sectionmap MAP.json [--crosswalk CW.md] [--attachments DIR]
                [--transmit-gate] [--json]
"""
import argparse, json, os, re, sys

# eSTAR/eCopy attachment technical rules (FDA PDF specs; see 510k-estar.md).
PDF_MIN, PDF_MAX = (1, 4), (1, 7)          # PDF 1.4–1.7 (PDF/A-1/2 also fine)
MAX_ATTACH_BYTES = 1_000_000_000            # ~1 GB/attachment
BOOKMARK_PAGE_THRESHOLD = 5                 # long PDFs should carry bookmarks

SEV = {"INFO": 0, "WARN": 1, "BLOCK": 2}

# Readability/format rules per the FDA "PDF Specifications" (v4.1, Sep 2016 —
# nonbinding, adopted as the house standard; project applicability:
# docs/external/fda-guidance/pdf-specifications.md; full text in the
# medtech-docs registry source-md). The eSTAR guidance itself is structure-only.
LETTER = (612.0, 792.0)
MIN_TEXT_PT = 9.0            # spec § FONTS: sizes 9–12pt; "smaller ... avoided"
# spec Table 1 standard set (+ metric-compatible LO substitutes + PDF base-14)
COMMON_FONT_HINTS = ("times", "arial", "helvetica", "liberation", "calibri",
                     "cambria", "georgia", "courier", "symbol", "carlito",
                     "caladea", "dejavu", "noto", "zapf", "dingbat")
# HARD RULE: filed exhibits never contain emoji. Emoji glyphs pull unembeddable
# bitmap fonts into the PDF and read as informal in a regulatory submission.
# WARN in advisory runs; BLOCK under --transmit-gate.
EMOJI_FONT_HINTS = ("emoji", "applecoloremoji", "segoeuiemoji", "notocoloremoji")


class Findings:
    def __init__(self):
        self.items = []

    def add(self, sev, check, msg, hint=""):
        self.items.append({"severity": sev, "check": check, "message": msg, "hint": hint})

    def by_gate(self):
        return sum(1 for f in self.items if f["severity"] == "BLOCK")

    def counts(self):
        c = {"INFO": 0, "WARN": 0, "BLOCK": 0}
        for f in self.items:
            c[f["severity"]] += 1
        return c


# ---------- markdown table parsing (crosswalk §A/§B/§C) ----------

def _tables_after_heading(md: str, heading_prefix: str):
    """Return list-of-rows (each row a list of cell strings) for the first pipe
    table appearing after a heading line starting with heading_prefix."""
    lines = md.splitlines()
    start = None
    for i, ln in enumerate(lines):
        if ln.strip().startswith(heading_prefix):
            start = i
            break
    if start is None:
        return None
    rows, in_tbl = [], False
    for ln in lines[start + 1:]:
        s = ln.strip()
        if s.startswith("|"):
            in_tbl = True
            cells = [c.strip() for c in s.strip("|").split("|")]
            if set("".join(cells)) <= set("-: "):   # separator row
                continue
            rows.append(cells)
        elif in_tbl and not s.startswith("|"):
            break
    return rows or None


# ---------- checks ----------

def _quality_findings(pdf, fn, gate=False):
    """Per-PDF readability/quality findings (advisory; the no-emoji rule
    escalates to BLOCK under --transmit-gate). Returns (sev,msg,hint) tuples."""
    out = []
    # page size — Letter expected for US submissions
    try:
        box = [float(x) for x in pdf.pages[0].MediaBox]
        w, h = box[2] - box[0], box[3] - box[1]
        if abs(w - LETTER[0]) > 4 or abs(h - LETTER[1]) > 4:
            out.append(("WARN", f"{fn}: page size {w:.0f}x{h:.0f}pt is not Letter (612x792)",
                        "US submissions expect 8.5x11in pages"))
    except Exception:
        pass
    # fonts — per-descriptor embedding + family advisory
    families, unembedded = set(), set()
    try:
        for page in pdf.pages:
            fonts = page.get("/Resources", {}).get("/Font", {})
            for _, font in (fonts.items() if fonts else []):
                base = str(font.get("/BaseFont", "?")).lstrip("/")
                families.add(base.split("+")[-1].split("-")[0].split(",")[0])
                desc = font.get("/FontDescriptor")
                if desc is None and "/DescendantFonts" in font:      # Type0/CID
                    desc = font.DescendantFonts[0].get("/FontDescriptor")
                if desc is not None and not any(k in desc for k in
                        ("/FontFile", "/FontFile2", "/FontFile3")):
                    unembedded.add(base)
    except Exception:
        pass
    if unembedded:
        out.append(("WARN", f"{fn}: font(s) not embedded: {', '.join(sorted(unembedded)[:4])}",
                    "embed all fonts (FDA PDF-spec requirement)"))
    emoji = {f for f in families if any(h in f.lower().replace(" ", "")
                                        for h in EMOJI_FONT_HINTS)}
    if emoji:
        out.append(("BLOCK" if gate else "WARN",
                    f"{fn}: emoji glyphs present ({', '.join(sorted(emoji))})",
                    "HARD RULE — filed exhibits never contain emoji; transliterate "
                    "(Yes / N-A / [!]) or remove at the source"))
    odd = {f for f in families
           if f != "?" and not any(hint in f.lower() for hint in COMMON_FONT_HINTS)}
    if odd:
        out.append(("INFO", f"{fn}: uncommon font families: {', '.join(sorted(odd)[:4])}",
                    "FDA PDF-spec recommends common serif/sans (e.g. Times New Roman 12pt)"))
    # prohibited content (spec § VERSION): JavaScript, embedded files,
    # annotations. JS/attachments impair review/archival — BLOCK; annotations
    # (non-link) — WARN.
    try:
        root = pdf.Root
        names = root.get("/Names", {})
        if "/JavaScript" in names or "/OpenAction" in root and \
                "/JS" in str(root.get("/OpenAction", "")):
            out.append(("BLOCK", f"{fn}: contains JavaScript — prohibited",
                        "spec § VERSION: PDF files must not contain JavaScript"))
        if "/EmbeddedFiles" in names:
            out.append(("BLOCK", f"{fn}: contains embedded file attachments — prohibited",
                        "spec § VERSION: no attachments inside submission PDFs"))
        annots = 0
        for page in pdf.pages:
            for a in (page.get("/Annots") or []):
                if str(a.get("/Subtype", "")) != "/Link":
                    annots += 1
        if annots:
            out.append(("WARN", f"{fn}: {annots} non-link annotation(s) present",
                        "spec § VERSION: do not include PDF annotations"))
    except Exception:
        pass
    # file naming (spec § NAMING): lowercase; only hyphen/underscore specials
    stem = fn[:-4] if fn.lower().endswith(".pdf") else fn
    if stem != stem.lower():
        out.append(("WARN", f"{fn}: filename contains uppercase characters",
                    "spec § NAMING: use lower case characters"))
    # minimum text size — scan content-stream Tf operators (approximation).
    # Monospace runs are exempt: ASCII-art/code blocks are figures sized to
    # fit the page width, not narrative text (spec § FONTS covers narrative).
    try:
        sizes = []
        for page in pdf.pages:
            mono_res = set()
            fonts = page.get("/Resources", {}).get("/Font", {})
            for name, font in (fonts.items() if fonts else []):
                base = str(font.get("/BaseFont", "")).lower()
                if any(h in base for h in ("mono", "courier", "consol")):
                    mono_res.add(str(name).lstrip("/").encode())
            raw = b""
            cont = page.get("/Contents")
            if cont is None:
                continue
            try:
                raw = cont.read_bytes()
            except Exception:
                try:
                    raw = b"".join(c.read_bytes() for c in cont)
                except Exception:
                    continue
            for m in re.finditer(rb"/(\w+)\s+([\d.]+)\s+Tf", raw):
                if m.group(1) in mono_res:
                    continue
                try:
                    s = float(m.group(2))
                    if s > 0.1:                     # ignore degenerate/scaled ops
                        sizes.append(s)
                except ValueError:
                    pass
        real = [s for s in sizes if s >= 1.0]        # sizes <1 are matrix-scaled
        if real and min(real) < MIN_TEXT_PT:
            out.append(("WARN", f"{fn}: text as small as {min(real):.1f}pt found",
                        f"spec § FONTS: 9–12pt range; tables 9–10pt; avoid smaller"))
    except Exception:
        pass
    return out


def check_structure(mapdata, F):
    ver = mapdata.get("template_version")
    tid = mapdata.get("template_id")
    if not ver:
        F.add("BLOCK", "structure", "section-map has no template_version (not version-pinned)")
    else:
        F.add("INFO", "structure", f"section-map: {tid} {ver} "
              f"({mapdata['totals']['subforms']} subforms, "
              f"{mapdata['totals']['attachment_slots']} attachment slots, "
              f"{mapdata['totals']['fields']} fields)")
    if mapdata.get("form_technology") == "XFA-dynamic":
        F.add("INFO", "structure", "form technology is XFA-dynamic — final field entry + "
              "eSTAR-Complete verify are Acrobat-only; this linter pre-flights attachments.")


def _iter_slots(node, path=""):
    p = f"{path}/{node['name']}" if path else node["name"]
    if node.get("attachment_slot"):
        yield node["name"], p
    for sub in node.get("subsections", []):
        yield from _iter_slots(sub, p)


def check_attachments(attach_dir, F, gate=False):
    """PDF admissibility of every prepared exhibit in attach_dir."""
    try:
        import pikepdf
    except ImportError:
        F.add("WARN", "attachments", "pikepdf not available — skipping PDF admissibility "
              "(run tools/estar/bootstrap.sh).")
        return {}
    prepared = {}
    pdfs = [f for f in sorted(os.listdir(attach_dir)) if f.lower().endswith(".pdf")]
    if not pdfs:
        F.add("WARN", "attachments", f"no PDF exhibits found in {attach_dir}")
        return {}
    for fn in pdfs:
        full = os.path.join(attach_dir, fn)
        prepared[fn] = full
        # filename hygiene
        if re.search(r"[^A-Za-z0-9._-]", fn):
            F.add("WARN", "attachments", f"{fn}: filename has spaces/special chars",
                  "use only [A-Za-z0-9._-]; controls FDA load order")
        size = os.path.getsize(full)
        if size > MAX_ATTACH_BYTES:
            F.add("BLOCK", "attachments", f"{fn}: {size/1e9:.2f} GB exceeds ~1 GB/attachment cap")
        try:
            pdf = pikepdf.open(full)
        except pikepdf.PasswordError:
            F.add("BLOCK", "attachments", f"{fn}: password-protected/encrypted — prohibited",
                  "remove all security settings")
            continue
        except Exception as e:
            F.add("BLOCK", "attachments", f"{fn}: not a readable PDF ({e})")
            continue
        # encryption
        if pdf.is_encrypted:
            F.add("BLOCK", "attachments", f"{fn}: encrypted / has security settings — prohibited")
        # PDF version
        try:
            vt = tuple(int(x) for x in str(pdf.pdf_version).split("."))
            if not (PDF_MIN <= vt <= PDF_MAX):
                F.add("BLOCK", "attachments",
                      f"{fn}: PDF {pdf.pdf_version} outside allowed 1.4–1.7 / PDF-A")
        except Exception:
            pass
        # attachments must be flat documents, not live forms
        if "/AcroForm" in pdf.Root:
            F.add("BLOCK", "attachments", f"{fn}: contains a live form (AcroForm/XFA) — "
                  "attachments must be flattened", "print/flatten to a static PDF")
        # bookmarks for long docs
        npages = len(pdf.pages)
        has_outline = "/Outlines" in pdf.Root and bool(pdf.Root.get("/Outlines", {}).get("/First"))
        if npages >= BOOKMARK_PAGE_THRESHOLD and not has_outline:
            F.add("WARN", "attachments", f"{fn}: {npages} pages, no bookmarks",
                  "add bookmarks / a ToC for navigability")
        # readability/quality best practices (advisory — see note at top)
        for sev, msg, hint in _quality_findings(pdf, fn, gate):
            F.add(sev, "quality", msg, hint)
    F.add("INFO", "attachments", f"checked {len(pdfs)} exhibit PDF(s) in {attach_dir}")
    return prepared


def check_coverage(mapdata, crosswalk_md, prepared, attach_dir, F):
    slots = []
    for sec in mapdata["sections"]:
        slots.extend(_iter_slots(sec))
    F.add("INFO", "coverage", f"template exposes {len(slots)} attachment slots total "
          "(many are N/A for a SaMD — applicability comes from the crosswalk).")
    if crosswalk_md is None:
        F.add("WARN", "coverage", "no --crosswalk given — cannot resolve which slots are in scope")
        return
    rowsB = _tables_after_heading(crosswalk_md, "## B.")
    if not rowsB:
        F.add("WARN", "coverage", "crosswalk § B section table not found/parseable")
        return
    hdr = rowsB[0]
    applic_i = next((i for i, h in enumerate(hdr) if "Applic" in h), 1)
    src_i = next((i for i, h in enumerate(hdr) if "source" in h.lower()), 3)
    inscope = gaps = na = 0
    for r in rowsB[1:]:
        if len(r) <= max(applic_i, src_i):
            continue
        ap, src = r[applic_i], r[src_i]
        if "⛔" in ap:
            na += 1
        elif "⚠" in ap:
            gaps += 1
        elif "✅" in ap:
            inscope += 1
            if "(TBD)" in src or "GAP" in src or not src.strip():
                F.add("WARN" if not prepared else "BLOCK", "coverage",
                      f"in-scope section '{r[0]}' has no ready source ({src or 'empty'})")
    F.add("INFO", "coverage", f"crosswalk § B: {inscope} in-scope, {gaps} gap/verify, {na} N/A sections")
    if attach_dir is None:
        F.add("INFO", "coverage", "no --attachments dir — attachment-vs-slot matching skipped "
              "(content docs still being authored).")


def check_accuracy(crosswalk_md, gate, F):
    if crosswalk_md is None:
        F.add("WARN", "accuracy", "no --crosswalk — structured-answer accuracy set not checked")
        return
    rowsA = _tables_after_heading(crosswalk_md, "## A.")
    if not rowsA:
        F.add("WARN", "accuracy", "crosswalk § A accuracy set not found/parseable")
        return
    hdr = rowsA[0]
    ans_i = next((i for i, h in enumerate(hdr) if h.strip().lower() == "answer"), 2)
    n = verify = blank = 0
    for r in rowsA[1:]:
        if len(r) <= ans_i:
            continue
        n += 1
        a = r[ans_i]
        if not a.strip() or a.strip() in ("—", "TBD"):
            blank += 1
        if "[VERIFY]" in a or "⚠" in a:
            verify += 1
    F.add("INFO", "accuracy", f"structured-answer accuracy set: {n} characteristics answered")
    if blank:
        F.add("BLOCK", "accuracy", f"{blank} accuracy-set answer(s) blank/TBD")
    if verify:
        F.add("BLOCK" if gate else "WARN", "accuracy",
              f"{verify} accuracy-set answer(s) still carry [VERIFY]/⚠ — resolve vs the SAD before transmit")


def check_references(attach_dir, F, gate=False):
    """Document-reference hygiene from the assembly manifest: references to
    package docs resolve to attachment numbers; references to repo docs NOT in
    the package are reported so RA can disposition each (mark 🔒 INTERNAL in
    the source md, or add the doc to the package)."""
    mpath = os.path.join(os.path.dirname(os.path.abspath(attach_dir)),
                         "assembly-manifest.json")
    if not os.path.isfile(mpath):
        return
    try:
        m = json.load(open(mpath))
    except Exception:
        return
    atts = m.get("attachments", [])
    resolved = sum(a.get("refs", {}).get("attachment_refs", 0) for a in atts)
    dropped = [(a["output"], d) for a in atts
               for d in a.get("refs", {}).get("internal_dropped", [])]
    if resolved:
        F.add("INFO", "references",
              f"{resolved} cross-reference(s) resolved to package attachment numbers")
    if dropped:
        F.add("BLOCK" if gate else "WARN", "references",
              f"{len(dropped)} internal doc reference(s) not in the package "
              "(link dropped, text kept in the exhibit)",
              "disposition each: mark 🔒 INTERNAL in the source md, or add the doc to the package")
        for outp, d in dropped[:8]:
            F.add("INFO", "references", f"  {os.path.basename(outp)}: "
                  f"'{(d.get('text') or '')[:40]}' → {d.get('target','')[:60]}")


def check_manifest_coverage(crosswalk_path, attach_dir, gate, F):
    """Composition-manifest ↔ package cross-check: every REQUIRED manifest
    piece whose Path is a local md doc must be in the assembled package (or be
    deliberately structured-only). This is the systematic catch for 'the cover
    letter cites a Required doc that never got attached'."""
    cm = os.path.join(os.path.dirname(os.path.abspath(crosswalk_path)),
                      "composition-manifest.md")
    am = os.path.join(os.path.dirname(os.path.abspath(attach_dir)),
                      "assembly-manifest.json")
    if not (os.path.isfile(cm) and os.path.isfile(am)):
        return
    try:
        assembled = {os.path.normpath(os.path.join(os.getcwd(), a["source"]))
                     for a in json.load(open(am)).get("attachments", [])}
    except Exception:
        return
    md = open(cm).read()
    cm_dir = os.path.dirname(os.path.abspath(cm))
    m = re.search(r"###\s*Required.*?(?=###\s*Supporting|## Excluded|\Z)", md, re.S)
    if not m:
        return
    seg = m.group(0)
    # transmitted-piece scope: the formal-deliverables block (before the
    # "Supporting technical architecture" grounding rows, which are internal
    # by design) + strengthener-brief rows marked transmission-blocking
    formal = seg.split("Supporting technical architecture")[0]
    blocking_rows = [ln for ln in seg.splitlines()
                     if "transmission-blocking" in ln and ln.strip().startswith("|")]
    scope = formal + "\n" + "\n".join(blocking_rows)
    missing = []
    for text, rel in re.findall(r"\[([^\]]*)\]\((\./[^)#\s]+\.md|[^)/#\s][^)#\s]*\.md)\)", scope):
        path = os.path.normpath(os.path.join(cm_dir, rel))
        if os.path.isfile(path) and path not in assembled:
            missing.append((text.strip("`"), rel))
    seen = set()
    missing = [x for x in missing if not (x[1] in seen or seen.add(x[1]))]
    if missing:
        F.add("BLOCK" if gate else "WARN", "manifest",
              f"{len(missing)} REQUIRED manifest piece(s) not in the assembled package",
              "attach via the crosswalk (Mode must declare 📎), or record the piece "
              "as deliberately structured-only / not-transmitted in the manifest")
        for text, rel in missing[:6]:
            F.add("INFO", "manifest", f"  missing: {text} → {rel}")
    else:
        F.add("INFO", "manifest",
              "all Required manifest pieces with local docs are in the package")


def check_gaps(crosswalk_md, F):
    if crosswalk_md is None:
        return
    rowsC = _tables_after_heading(crosswalk_md, "## C.")
    if not rowsC:
        return
    open_gaps = len(rowsC) - 1
    if open_gaps > 0:
        F.add("WARN", "gaps", f"{open_gaps} open crosswalk gap→action item(s) (§ C) — "
              "content/RA follow-ups, not format blockers")


def main():
    ap = argparse.ArgumentParser(description="eSTAR/PreSTAR admissibility + coverage linter")
    default_map = os.path.join(os.path.dirname(__file__), "..", "data", "estar",
                               "sectionmap-nivd-v7.0.json")
    ap.add_argument("--sectionmap", default=os.path.normpath(default_map))
    ap.add_argument("--crosswalk")
    ap.add_argument("--attachments")
    ap.add_argument("--transmit-gate", action="store_true",
                    help="strict: exit non-zero on any BLOCK finding")
    ap.add_argument("--json", action="store_true", help="emit findings as JSON")
    a = ap.parse_args()

    F = Findings()
    try:
        mapdata = json.load(open(a.sectionmap))
    except Exception as e:
        print(f"FATAL: cannot load section-map {a.sectionmap}: {e}", file=sys.stderr)
        return 3
    crosswalk_md = open(a.crosswalk).read() if a.crosswalk else None

    check_structure(mapdata, F)
    prepared = check_attachments(a.attachments, F, a.transmit_gate) if a.attachments else {}
    check_coverage(mapdata, crosswalk_md, prepared, a.attachments, F)
    check_accuracy(crosswalk_md, a.transmit_gate, F)
    if a.attachments:
        check_references(a.attachments, F, a.transmit_gate)
        if a.crosswalk:
            check_manifest_coverage(a.crosswalk, a.attachments, a.transmit_gate, F)
    check_gaps(crosswalk_md, F)

    if a.json:
        print(json.dumps({"findings": F.items, "counts": F.counts(),
                          "transmit_gate": a.transmit_gate}, indent=2))
    else:
        icon = {"INFO": "·", "WARN": "⚠", "BLOCK": "✗"}
        for f in sorted(F.items, key=lambda x: -SEV[x["severity"]]):
            line = f"  {icon[f['severity']]} [{f['check']}] {f['message']}"
            if f["hint"]:
                line += f"\n      → {f['hint']}"
            print(line)
        c = F.counts()
        mode = "TRANSMIT-GATE" if a.transmit_gate else "advisory"
        print(f"\n{mode}: {c['BLOCK']} blocking · {c['WARN']} warnings · {c['INFO']} info")

    if a.transmit_gate and F.by_gate() > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
