#!/usr/bin/env python3
"""
estar_viewcheck.py — visual-verification worklist for assembled exhibits.

Automated rendering checks (lint) can't judge how a page *looks* — mangled
ASCII art, awkward table breaks, cramped layouts need eyes. This tool makes
the eyeballing cheap: it scans each exhibit and emits a short, prioritized
worklist of pages to view (a reviewing agent opens them with its PDF page
reader; a human opens them in a viewer):

  - pages using monospace fonts        → ASCII art / code blocks (top risk)
  - the page with the smallest text    → fit-to-width art or crunched tables
  - first + last page of each exhibit  → title layout / trailing content

Run under the eStar venv after `assemble`:
  estar_viewcheck.py --attachments DIR [--json]
"""
import argparse, json, os, re, sys


def scan_pdf(path):
    import pikepdf
    pdf = pikepdf.open(path)
    pages = []
    for i, page in enumerate(pdf.pages, 1):
        mono_res, families = set(), set()
        fonts = page.get("/Resources", {}).get("/Font", {})
        for name, font in (fonts.items() if fonts else []):
            base = str(font.get("/BaseFont", "")).lower()
            families.add(base.split("+")[-1])
            if any(h in base for h in ("mono", "courier", "consol")):
                mono_res.add(str(name).lstrip("/").encode())
        raw = b""
        cont = page.get("/Contents")
        if cont is not None:
            try:
                raw = cont.read_bytes()
            except Exception:
                try:
                    raw = b"".join(c.read_bytes() for c in cont)
                except Exception:
                    raw = b""
        mono_ops, min_sz = 0, None
        for m in re.finditer(rb"/(\w+)\s+([\d.]+)\s+Tf", raw):
            try:
                sz = float(m.group(2))
            except ValueError:
                continue
            if sz < 1.0:
                continue
            if m.group(1) in mono_res:
                mono_ops += 1
            min_sz = sz if min_sz is None else min(min_sz, sz)
        pages.append({"page": i, "mono_ops": mono_ops,
                      "min_size": round(min_sz, 1) if min_sz else None})
    return pages


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--attachments", required=True)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    report = []
    for fn in sorted(os.listdir(a.attachments)):
        if not fn.lower().endswith(".pdf"):
            continue
        pages = scan_pdf(os.path.join(a.attachments, fn))
        n = len(pages)
        art = [p["page"] for p in pages if p["mono_ops"] > 0]
        smallest = min((p for p in pages if p["min_size"]), default=None,
                       key=lambda p: p["min_size"])
        review = sorted(set(art[:6] + ([smallest["page"]] if smallest else [])
                            + [1] + ([n] if n > 1 else [])))
        report.append({"file": fn, "pages": n, "art_pages": art,
                       "smallest_text": smallest, "review_pages": review})

    if a.json:
        print(json.dumps({"exhibits": report}, indent=2))
        return 0
    total = 0
    for r in report:
        flags = []
        if r["art_pages"]:
            flags.append(f"art/code on p.{','.join(map(str, r['art_pages'][:8]))}")
        if r["smallest_text"]:
            flags.append(f"min {r['smallest_text']['min_size']}pt @p.{r['smallest_text']['page']}")
        print(f"  {r['file']}  ({r['pages']}p)  review p.{','.join(map(str, r['review_pages']))}"
              + ("  — " + "; ".join(flags) if flags else ""))
        total += len(r["review_pages"])
    print(f"\nview-check worklist: {total} page(s) across {len(report)} exhibit(s) — "
          "open each listed page and verify art integrity, table breaks, layout.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
