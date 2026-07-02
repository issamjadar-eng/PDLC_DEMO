# FDA Portable Document Format (PDF) Specifications — Distilled

🔎 **Finding aid** — this file orients and routes; it is a paraphrase, not the source's text. Ground and cite the authoritative full text at [`source-md/pdf-specifications.md`](source-md/pdf-specifications.md); verify verbatim quotes against the byte-correct [`source/pdf-specifications.pdf`](source/pdf-specifications.pdf).

**Document**: *Portable Document Format (PDF) Specifications* — Technical Specifications Document, **v4.1, September 2016** (CDER/CBER; fda.gov/media/76797). **Nonbinding recommendations.** Incorporated by reference into the eCTD electronic-submissions guidance; device-side eSubmissions (eCopy/eSTAR attachments) conventionally follow it as the PDF best-practice baseline.

## The rules at a glance

| Topic | Requirement/Recommendation | § |
|-------|---------------------------|---|
| **Version** | PDF 1.4–1.7, PDF/A-1, PDF/A-2 acceptable; readable in Acrobat X; text-searchable; no plug-ins needed | VERSION |
| **Prohibited content** | **No JavaScript; no dynamic content (audio/video/animation); no attachments; no 3D; no annotations** (promo-material exception) | VERSION |
| **Security** | No security settings or password protection (FDA-downloaded forms keep their as-provided security) | SECURITY |
| **Fonts — embedding** | Fully embed all non-standard fonts (all characters, not just a subset) | FONTS |
| **Fonts — standard set (Table 1)** | Serif: **Times New Roman** family · Sans: **Arial** family · Mono: **Courier New** family · Other: Symbol, Zapf Dingbats | FONTS |
| **Font sizes** | **9–12pt range**; **Times New Roman 12pt recommended for narrative**; **9–10pt for tables** (avoid smaller); 10pt footnotes | FONTS |
| **Colors** | **Black text; blue for hypertext links**; test colors on grayscale print | FONTS |
| **Page/margins** | 8.5×11 in; **left margin ≥3/4 in**; other sides ≥3/8 in; landscape top ≥3/4 in; headers/footers stay out of margins; A4-printable | PAGE SIZE AND MARGINS |
| **Source** | Avoid image-based/scanned PDFs; text-searchable; OCR verified | SOURCE |
| **Scanning (Table 2)** | 300 dpi documents; 600 dpi photos/gels; lossless compression (Zip/Flate, CCITT G4) | METHODS / COMPRESSION |
| **Navigation** | **TOC + bookmarks for documents ≥5 pages**; hyperlinks blue or thin rectangles; relative paths; bookmark hierarchy = TOC, ≤4 levels; Inherit Zoom | DOCUMENT NAVIGATION |
| **Initial view** | Open to "Bookmarks Panel and Page" (or "Page Only" if no bookmarks); default layout/magnification | INITIAL VIEW |
| **Page numbering** | PDF page number = document page number, first page = 1 | PAGE NUMBERING |
| **File naming** | **Lowercase**; no special characters except hyphens and underscores | NAMING PDF FILES |
| **Promo materials** | Exempt from font-size/color/annotation restrictions; actual size; ≥600 dpi | SPECIAL CONSIDERATIONS |

## Routing

- Project applicability (what this program adopted, incl. the device-side scope note): `docs/external/fda-guidance/pdf-specifications.md`
- Enforced by: the `/docflow export` house-style pass (producer) and the `/submissions` eStar lint `quality` group (verifier)
