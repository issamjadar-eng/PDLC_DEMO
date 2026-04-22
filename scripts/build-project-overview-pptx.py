#!/usr/bin/env python3
"""Build project-overview.pptx — companion deck for project-overview.md.

Modeled on arthrex-pccp/project-overview.pptx (22 slides, numbered sections
01-06, section chip on every content slide, multi-column card layouts).
"""

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Emu, Inches, Pt

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets" / "project-overview"
OUT = ROOT / "project-overview.pptx"
LOGO = ROOT / "tools" / "project-console" / "themes" / "globallogic" / "logo.png"

PRIMARY = RGBColor(0x7A, 0x00, 0xDF)
PRIMARY_DARK = RGBColor(0x5C, 0x00, 0xA8)
PRIMARY_TINT = RGBColor(0xF3, 0xE8, 0xFF)
ACCENT = RGBColor(0x06, 0x93, 0xE3)
BODY_BG = RGBColor(0xF7, 0xF7, 0xF9)
CARD_BG = RGBColor(0xFB, 0xFA, 0xFF)
TEXT = RGBColor(0x48, 0x4F, 0x6B)
TEXT_DARK = RGBColor(0x1F, 0x25, 0x3D)
TEXT_MUTED = RGBColor(0x6B, 0x72, 0x80)
BORDER = RGBColor(0xE3, 0xE3, 0xE8)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
BLACK = RGBColor(0x12, 0x12, 0x16)

SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)

prs = Presentation()
prs.slide_width = SLIDE_W
prs.slide_height = SLIDE_H
BLANK = prs.slide_layouts[6]


def fill(shape, rgb):
    shape.fill.solid()
    shape.fill.fore_color.rgb = rgb


def noline(shape):
    shape.line.fill.background()


def rect(slide, x, y, w, h, color, border=None):
    r = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, h)
    fill(r, color)
    if border is None:
        noline(r)
    else:
        r.line.color.rgb = border
        r.line.width = Emu(6350)
    return r


def round_rect(slide, x, y, w, h, color, border=None, corner=0.06):
    r = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h)
    r.adjustments[0] = corner
    fill(r, color)
    if border is None:
        noline(r)
    else:
        r.line.color.rgb = border
        r.line.width = Emu(6350)
    return r


def text(slide, x, y, w, h, body, *, size=14, bold=False, color=TEXT,
         align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, italic=False,
         font="Calibri"):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.margin_left = tf.margin_right = Emu(0)
    tf.margin_top = tf.margin_bottom = Emu(0)
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    lines = body.split("\n") if isinstance(body, str) else body
    first = True
    for line in lines:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.alignment = align
        r = p.add_run()
        r.text = line
        r.font.size = Pt(size)
        r.font.bold = bold
        r.font.italic = italic
        r.font.color.rgb = color
        r.font.name = font
    return tb


# ═══ Frame (topbar, section chip, footer) ════════════════════════


def add_topbar(slide, section_num=None, section_name=None):
    rect(slide, 0, 0, SLIDE_W, Inches(0.6), WHITE)
    rect(slide, 0, Inches(0.59), SLIDE_W, Emu(9525), BORDER)
    text(slide, Inches(0.4), Inches(0.1), Inches(6), Inches(0.4),
         "GlobalLogic  ·  PDLC_DEMO",
         size=13, bold=True, color=BLACK, anchor=MSO_ANCHOR.MIDDLE)
    # Logo first so we know where the chip must stop.
    # PNG is 520x121 (~4.3:1). Height 0.32" => width ~1.38".
    logo_h = Inches(0.32)
    logo_w = Inches(1.38)
    logo_right_margin = Inches(0.4)
    logo_x = SLIDE_W - logo_w - logo_right_margin
    if LOGO.exists():
        try:
            slide.shapes.add_picture(
                str(LOGO), logo_x, Inches(0.14),
                height=logo_h, width=logo_w,
            )
        except Exception:  # noqa: BLE001
            pass
    if section_num is not None:
        # Chip ends 0.25" before the logo begins, so no collision.
        chip_x = Inches(5.5)
        chip_end = logo_x - Inches(0.25)
        chip_w = chip_end - chip_x
        text(slide, chip_x, Inches(0.1), chip_w, Inches(0.4),
             f"{section_num}  ·  {section_name}",
             size=11, bold=True, color=PRIMARY,
             align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE)


def add_footer(slide, page=None, total=None):
    rect(slide, 0, Inches(7.1), SLIDE_W, Emu(6350), BORDER)
    text(slide, Inches(0.4), Inches(7.2), Inches(10), Inches(0.25),
         "A GlobalLogic demo of agentic PDLC workflows in MedTech.  ·  Demo sample — not for clinical use.",
         size=9, italic=True, color=TEXT_MUTED, anchor=MSO_ANCHOR.MIDDLE)
    if page is not None and total is not None:
        text(slide, Inches(10.5), Inches(7.2), Inches(2.5), Inches(0.25),
             f"{page} / {total}", size=9, color=TEXT_MUTED,
             align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE)


def add_slide_title(slide, eyebrow, title, subtitle):
    text(slide, Inches(0.6), Inches(0.95), Inches(12), Inches(0.3),
         eyebrow.upper(), size=11, bold=True, color=PRIMARY)
    text(slide, Inches(0.6), Inches(1.2), Inches(12), Inches(0.7),
         title, size=30, bold=True, color=BLACK)
    text(slide, Inches(0.6), Inches(1.85), Inches(12), Inches(0.5),
         subtitle, size=14, color=TEXT_MUTED, italic=True)
    rect(slide, Inches(0.6), Inches(2.35), Inches(0.8), Emu(38100), PRIMARY)


# ═══ Cards ══════════════════════════════════════════════════════


def card(slide, x, y, w, h, title, tags, body, *, accent=PRIMARY):
    round_rect(slide, x, y, w, h, CARD_BG, border=BORDER, corner=0.04)
    round_rect(slide, x, y, w, Inches(0.08), accent, corner=0.45)
    text(slide, x + Inches(0.25), y + Inches(0.18),
         w - Inches(0.5), Inches(0.5),
         title, size=16, bold=True, color=BLACK)
    text(slide, x + Inches(0.25), y + Inches(0.58),
         w - Inches(0.5), Inches(0.3),
         tags, size=10, bold=True, color=accent)
    text(slide, x + Inches(0.25), y + Inches(0.9),
         w - Inches(0.5), h - Inches(1.0),
         body, size=12, color=TEXT)


def number_card(slide, x, y, w, h, num, title, body, *, accent=PRIMARY):
    round_rect(slide, x, y, w, h, WHITE, border=BORDER, corner=0.04)
    badge = slide.shapes.add_shape(
        MSO_SHAPE.OVAL, x + Inches(0.3), y + Inches(0.3),
        Inches(0.55), Inches(0.55))
    fill(badge, accent)
    noline(badge)
    tb = badge.text_frame
    tb.margin_left = tb.margin_right = Emu(0)
    tb.margin_top = tb.margin_bottom = Emu(0)
    p = tb.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = num
    r.font.size = Pt(14)
    r.font.bold = True
    r.font.color.rgb = WHITE
    text(slide, x + Inches(1.0), y + Inches(0.25),
         w - Inches(1.2), Inches(0.4),
         title, size=14, bold=True, color=BLACK)
    text(slide, x + Inches(1.0), y + Inches(0.7),
         w - Inches(1.2), h - Inches(0.85),
         body, size=11, color=TEXT)


def bullet_card(slide, x, y, w, h, title, items, *, accent=PRIMARY):
    round_rect(slide, x, y, w, h, WHITE, border=BORDER, corner=0.04)
    rect(slide, x, y, Inches(0.06), h, accent)
    text(slide, x + Inches(0.3), y + Inches(0.2),
         w - Inches(0.5), Inches(0.4),
         title, size=15, bold=True, color=BLACK)
    tb = slide.shapes.add_textbox(
        x + Inches(0.3), y + Inches(0.7), w - Inches(0.5), h - Inches(0.85))
    tf = tb.text_frame
    tf.margin_left = tf.margin_right = Emu(0)
    tf.margin_top = tf.margin_bottom = Emu(0)
    tf.word_wrap = True
    first = True
    for item in items:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.space_after = Pt(5)
        r = p.add_run()
        r.text = "•  "
        r.font.size = Pt(11)
        r.font.bold = True
        r.font.color.rgb = accent
        if isinstance(item, tuple):
            head, rest = item
            r = p.add_run()
            r.text = head
            r.font.size = Pt(11)
            r.font.bold = True
            r.font.color.rgb = BLACK
            r = p.add_run()
            r.text = "  " + rest
            r.font.size = Pt(11)
            r.font.color.rgb = TEXT
        else:
            r = p.add_run()
            r.text = item
            r.font.size = Pt(11)
            r.font.color.rgb = TEXT


def new_slide(section_num=None, section_name=None):
    s = prs.slides.add_slide(BLANK)
    rect(s, 0, 0, SLIDE_W, SLIDE_H, WHITE)
    if section_num is not None:
        add_topbar(s, section_num, section_name)
    return s


# ── Slide 1: Cover ──────────────────────────────────────────────
s = prs.slides.add_slide(BLANK)
rect(s, 0, 0, SLIDE_W, SLIDE_H, WHITE)
rect(s, 0, 0, Inches(4.6), SLIDE_H, PRIMARY)
rect(s, Inches(4.6), 0, Inches(0.1), SLIDE_H, ACCENT)
if LOGO.exists():
    s.shapes.add_picture(
        str(LOGO), Inches(0.55), Inches(0.55),
        height=Inches(0.5), width=Inches(2.15))
text(s, Inches(0.55), Inches(1.25), Inches(3.8), Inches(0.35),
     "GlobalLogic", size=11, bold=True, color=WHITE)
text(s, Inches(0.55), Inches(1.55), Inches(3.8), Inches(0.5),
     "PDLC_DEMO", size=22, bold=True, color=WHITE)
text(s, Inches(0.55), Inches(6.3), Inches(3.8), Inches(0.8),
     "A GlobalLogic demo of agentic PDLC workflows in MedTech.",
     size=11, italic=True, color=WHITE)
text(s, Inches(5.1), Inches(1.3), Inches(7.8), Inches(0.5),
     "PROJECT OVERVIEW", size=13, bold=True, color=PRIMARY)
text(s, Inches(5.1), Inches(1.7), Inches(7.8), Inches(1.5),
     "PainEase PCA Advanced\nPP3500 program",
     size=40, bold=True, color=BLACK)
text(s, Inches(5.1), Inches(3.6), Inches(7.8), Inches(0.7),
     "A patient-controlled analgesia infusion pump — with connectivity adapter and Cloud Suite\n"
     "510(k) with Predetermined Change Control Plan (PCCP)",
     size=15, color=TEXT)
info = [
    ("Device", "PP3500 — PainEase PCA Advanced"),
    ("Predicate", "PP3000 / K190567  (illustrative)"),
    ("Composition", "SaMD + SiMD firmware + custom medical-electrical hardware"),
    ("DHFs", "10 total — 3 top-level + 7 nested under Cloud Suite"),
    ("Prepared by", "Ben Xavier  ·  2026-04-21"),
]
for i, (k, v) in enumerate(info):
    y = Inches(4.7 + i * 0.35)
    text(s, Inches(5.1), y, Inches(2.3), Inches(0.3), k,
         size=11, bold=True, color=PRIMARY_DARK)
    text(s, Inches(7.5), y, Inches(5.5), Inches(0.3), v,
         size=11, color=TEXT)
rect(s, 0, Inches(7.1), SLIDE_W, Inches(0.4), PRIMARY_TINT)
text(s, 0, Inches(7.1), SLIDE_W, Inches(0.4),
     "Demonstration only — device identity, predicate, clearance number, and all clinical data are illustrative. Not a real submission.",
     size=10, color=PRIMARY_DARK, align=PP_ALIGN.CENTER,
     anchor=MSO_ANCHOR.MIDDLE, italic=True)


# ── Slide 2: Agenda ─────────────────────────────────────────────
s = new_slide("00", "Agenda")
add_slide_title(s, "Agenda", "How this deck is organized",
                "Five content sections plus the appendix. ~20 minutes.")
agenda = [
    ("01", "Project Overview & Strategy",
     "Device composition, DHF topology, regulatory approach (510(k) + PCCP)."),
    ("02", "Agentic Approach",
     "Project shape, structure, skills, and 23 persona agents."),
    ("03", "Quality & Process",
     "How skills, hooks, and rules turn conventions into automatic guardrails."),
    ("04", "Agents advise. Humans decide.",
     "Cross-functional advisory panel with the human sign-off always required."),
    ("05", "The Project Console",
     "Local FastAPI browser app — agents, documents, dashboards, trace matrix."),
]
row_w = Inches(12.1)
row_h = Inches(0.72)
row_gap = Inches(0.12)
start_y = Inches(2.8)
for i, (num, title, body) in enumerate(agenda):
    y = start_y + i * (row_h + row_gap)
    round_rect(s, Inches(0.6), y, row_w, row_h, WHITE, border=BORDER, corner=0.04)
    # Number badge — big circle on the left
    badge = s.shapes.add_shape(
        MSO_SHAPE.OVAL, Inches(0.85), y + Inches(0.11),
        Inches(0.5), Inches(0.5),
    )
    fill(badge, PRIMARY)
    noline(badge)
    tb = badge.text_frame
    tb.margin_left = tb.margin_right = Emu(0)
    tb.margin_top = tb.margin_bottom = Emu(0)
    p = tb.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = num
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.color.rgb = WHITE
    # Title — single line at 17pt
    text(s, Inches(1.55), y, Inches(4.0), row_h,
         title, size=17, bold=True, color=BLACK,
         anchor=MSO_ANCHOR.MIDDLE)
    # Body — to the right of the title
    text(s, Inches(5.7), y, Inches(7.0), row_h,
         body, size=12, color=TEXT, anchor=MSO_ANCHOR.MIDDLE)
add_footer(s, 2, 22)


# ── Slide 3: §1 What PP3500 is ─────────────────────────────────
s = new_slide("01", "Project Overview & Strategy")
add_slide_title(s, "Project Overview & Strategy",
                "What PP3500 is",
                "Single composite system — SaMD + SiMD firmware + custom medical-electrical hardware.")
card(s, Inches(0.6), Inches(2.7), Inches(4.0), Inches(4.1),
     "PCA Device",
     "pca-device  ·  Class II medical device  ·  IEC 62304 Class C",
     "SiMD pump firmware + SaMD modules + custom hardware. "
     "On-pump delivery, dose-limit enforcement, alarms, touchscreen UI, "
     "barcode scan, self-test. The 510(k) anchor DHF.",
     accent=PRIMARY)
card(s, Inches(4.7), Inches(2.7), Inches(4.0), Inches(4.1),
     "Connectivity Adapter",
     "connectivity-adapter  ·  MDDS (non-device, post-2015 FDA)",
     "On-prem bridge carrying PCA telemetry + drug-library pushes to "
     "and from the Cloud Suite. Named as adjacent infrastructure in the "
     "PP3500 510(k); only its cybersecurity posture is pulled in.",
     accent=ACCENT)
card(s, Inches(8.8), Inches(2.7), Inches(4.0), Inches(4.1),
     "Cloud Suite",
     "cloud-suite  ·  platform DHF  ·  7 child DHFs",
     "Drug Library Manager is Class II SaMD (PCA accessory, mutates "
     "the dose-limit table). The other six children (Fleet, Compliance "
     "Reports, Analytics, Inventory, Alerts, Clinical Interface) are "
     "non-device software.",
     accent=PRIMARY_DARK)
add_footer(s, 3, 22)


# ── Slide 4: §1 Regulatory strategy ────────────────────────────
s = new_slide("01", "Project Overview & Strategy")
add_slide_title(s, "Project Overview & Strategy",
                "Regulatory strategy",
                "One 510(k) for the PCA device, with an integrated PCCP — pre-authorized post-market change.")
bullet_card(s, Inches(0.6), Inches(2.7), Inches(4.0), Inches(4.1),
            "Filing scope",
            [
                ("PP3500 510(k)", "covers only the PCA device itself."),
                ("Connectivity Adapter", "MDDS — not separately filed, cybersecurity only."),
                ("Drug Library Manager", "Class II SaMD accessory — bundled vs. standalone TBD."),
                ("Other Cloud Suite components", "non-device — out of filing."),
                ("Predicate", "PP3000 / K190567  (illustrative)."),
            ])
bullet_card(s, Inches(4.7), Inches(2.7), Inches(4.0), Inches(4.1),
            "Ct* carve-out",
            [
                ("CtS", "Critical to Safety — failure can cause patient harm."),
                ("CtF", "Critical to Function — failure breaks the therapy."),
                ("CtC", "Critical to Compliance — required by standard."),
                ("CtP", "Critical to Performance — degrades claimed spec."),
                ("In scope = any Ct* tag.", "Commercial-only requirements ship post-clearance."),
            ], accent=ACCENT)
bullet_card(s, Inches(8.8), Inches(2.7), Inches(4.0), Inches(4.1),
            "PCCP envelope",
            [
                ("Drug-library updates", "new drugs, limit changes inside bounds."),
                ("Firmware patches", "against a fixed, frozen risk profile."),
                ("Predictive-alarm SaMDs", "that meet change-protocol acceptance criteria."),
                ("Out of envelope", "anything that changes the risk profile or indications."),
            ], accent=PRIMARY_DARK)
add_footer(s, 4, 22)


# ── Slide 5: §1 Key deliverables ───────────────────────────────
s = new_slide("01", "Project Overview & Strategy")
add_slide_title(s, "Project Overview & Strategy",
                "Key deliverables",
                "Four work products, sequenced from FDA dialogue through substantial equivalence.")
deliv = [
    ("1", "Q-Sub (Pre-Submission) package",
     "Cover letter · device description · proposed indications · predicates · PCCP summary · specific FDA questions. "
     "Validates classification and PCCP scope with FDA before the 510(k)."),
    ("2", "PCCP document",
     "Device description · change categories per module · modification protocols · performance criteria · "
     "validation methodology · reporting plan."),
    ("3", "510(k) submission",
     "Substantial-equivalence argument · software docs · performance / validation data · "
     "risk analysis · labeling. Composition driven by composition-manifest.md."),
    ("4", "Trace matrix per DHF",
     "User Needs ↔ Design Inputs ↔ Architecture ↔ V&V ↔ Risk. "
     "Filing Scope column derived from Ct* tags."),
]
cw = Inches(6.0)
ch = Inches(1.9)
for i, (num, title, body) in enumerate(deliv):
    col = i % 2
    row = i // 2
    x = Inches(0.6 + col * 6.2)
    y = Inches(2.7 + row * 2.1)
    number_card(s, x, y, cw, ch, num, title, body,
                accent=PRIMARY if row == 0 else ACCENT)
add_footer(s, 5, 22)


# ── Slide 6: §2 Project shape ──────────────────────────────────
s = new_slide("02", "Agentic Approach")
add_slide_title(s, "Agentic Approach",
                "Project shape — flat multi-DHF",
                "IEC 62304 § 5 software-system / software-item split, expressed in folders.")
round_rect(s, Inches(0.6), Inches(2.7), Inches(12.1), Inches(4.1),
           CARD_BG, border=BORDER, corner=0.02)
tree = (
    "PDLC_DEMO/\n"
    "├── CLAUDE.md                  · project operating rules (always loaded)\n"
    "├── project.yml                · single source of truth — identity, DHFs, team, registries, secops\n"
    "├── project-overview.md        · this overview\n"
    "├── tasks/<person>/            · per-person task folders; every edit is task-gated\n"
    "├── docs/external/             · FDA guidance, ISO/IEC standards, frameworks, literature\n"
    "├── docs/internal/             · GlobalLogic QMS — Manual + 25 SOPs + 6 WIs + 14 Templates + 9 Forms\n"
    "├── docs/project/strategies/   · 8 shared strategy docs (regulatory, architecture, dev, testing, …)\n"
    "├── docs/project/dhfs/\n"
    "│   ├── pca-device/            · TOP DHF — PP3500 (lead product)\n"
    "│   ├── connectivity-adapter/  · TOP DHF — MDDS bridge\n"
    "│   └── cloud-suite/           · PLATFORM DHF — 7 nested children\n"
    "├── docs/project/submissions/  · qsub/ · 510k/ · pccp/  (each with composition-manifest.md)\n"
    "├── tools/project-console/     · local FastAPI console (scaffolded from project-console skill)\n"
    "└── .claude/                   · skills/  agents/  hooks/  settings.json"
)
text(s, Inches(0.85), Inches(2.9), Inches(11.6), Inches(3.8),
     tree, size=11, color=TEXT_DARK, font="Consolas")
add_footer(s, 6, 22)


# ── Slide 7: §2 Operating rules ────────────────────────────────
s = new_slide("02", "Agentic Approach")
add_slide_title(s, "Agentic Approach",
                "Operating rules baked into the project",
                "Hooks and conventions that make Claude work with regulatory-grade discipline.")
rules = [
    ("Task-first gate",
     "PreToolUse hook denies any Edit/Write/NotebookEdit unless the session has an active task document. Every change is owned."),
    ("One task, one file",
     "All analysis, drafts, and phase deliverables live in the task's numbered markdown file — never sibling notes."),
    ("Strategy / lessons capture",
     "UserPromptSubmit + Stop hooks detect strategic-intent signals and block session end if content wasn't captured."),
    ("Session-start secops",
     "project-secops agent audits the session against project.yml allowlists. Results cached with a 7-day TTL."),
    ("Docflow entry enforcement",
     "Bash hook refuses direct pandoc / soffice / pdftotext calls so all conversions round-trip through /docflow."),
    ("project.yml as single source of truth",
     "Identity, DHF topology, team, registries, secops allowlists, advisor curation — all in one manifest."),
]
col_w = Inches(6.0)
row_h = Inches(1.3)
for i, (title, body) in enumerate(rules):
    col = i % 2
    row = i // 2
    x = Inches(0.6 + col * 6.2)
    y = Inches(2.7 + row * 1.4)
    round_rect(s, x, y, col_w, row_h, WHITE, border=BORDER, corner=0.04)
    rect(s, x, y, Inches(0.06), row_h, PRIMARY)
    text(s, x + Inches(0.25), y + Inches(0.15),
         col_w - Inches(0.4), Inches(0.35),
         title, size=13, bold=True, color=BLACK)
    text(s, x + Inches(0.25), y + Inches(0.55),
         col_w - Inches(0.4), row_h - Inches(0.65),
         body, size=11, color=TEXT)
add_footer(s, 7, 22)


# ── Slide 8: §2 Skills inventory ───────────────────────────────
s = new_slide("02", "Agentic Approach")
add_slide_title(s, "Agentic Approach",
                "Skills — reusable, expert-grade playbooks",
                "15 project skills installed + 4 builtin format skills. Highest-leverage shown.")
skills = [
    ("task",         "Task lifecycle · enforces the task-first gate · manages capture hooks."),
    ("medtech-docs", "Scaffolds docs/ tree · manages DHFs · imports FDA guidance and ISO/IEC standards."),
    ("docflow",      "Round-trip DOCX / DOC / PDF / XLSX ↔ markdown with image and cross-ref fidelity."),
    ("strategy",     "Harvests tagged blocks from tasks into 8 shared strategy docs."),
    ("tracker",      "Builds 510(k) + PCCP submission tracker from strategy + composition manifests."),
    ("trace-matrix", "Bidirectional design-controls trace per DHF; emits md + json sidecar."),
    ("advisors",     "Installs and curates 23 persona advisors; shared between Claude Code and the console."),
    ("project-console","Scaffolds and maintains the local FastAPI console (agents / docs / dashboards / trace)."),
    ("lessons",      "Harvests lessons-learned blocks into the team ledger; promotes mature ones."),
    ("best-practices","Audits project setup against registry checks and each skill's best-practices table."),
    ("secops",       "Session-start security posture check, attestations, allowlists."),
    ("change-control","(Scaffold.) Bridge to Confluence / Comala and Windchill for Part 11 review & release."),
    ("sync-skills",  "Bidirectional sync with the shared hitachi skill registry."),
    ("digest",       "Morning briefing + on-demand append to the project CHANGELOG.md."),
]
tbl_x = Inches(0.6)
tbl_y = Inches(2.7)
tbl_w = Inches(12.1)
rect(s, tbl_x, tbl_y, tbl_w, Inches(0.35), PRIMARY)
text(s, tbl_x + Inches(0.25), tbl_y, Inches(2.4), Inches(0.35),
     "SKILL", size=11, bold=True, color=WHITE, anchor=MSO_ANCHOR.MIDDLE)
text(s, tbl_x + Inches(2.7), tbl_y, Inches(9.2), Inches(0.35),
     "WHAT IT AUTOMATES", size=11, bold=True, color=WHITE, anchor=MSO_ANCHOR.MIDDLE)
row_h = Inches(0.29)
for i, (name, what) in enumerate(skills):
    y = tbl_y + Inches(0.35) + i * row_h
    if i % 2 == 0:
        rect(s, tbl_x, y, tbl_w, row_h, BODY_BG)
    text(s, tbl_x + Inches(0.25), y, Inches(2.4), row_h,
         "/" + name, size=11, bold=True, color=PRIMARY_DARK,
         anchor=MSO_ANCHOR.MIDDLE, font="Consolas")
    text(s, tbl_x + Inches(2.7), y, Inches(9.2), row_h,
         what, size=10, color=TEXT, anchor=MSO_ANCHOR.MIDDLE)
add_footer(s, 8, 22)


# ── Slide 9: §2 Agents ─────────────────────────────────────────
s = new_slide("02", "Agentic Approach")
add_slide_title(s, "Agentic Approach",
                "Agents — persona advisors",
                "23 total — 11 Core Team Assistants + 8 KOLs + 4 panels. Same definitions feed Claude Code and the console.")
bullet_card(s, Inches(0.6), Inches(2.7), Inches(6.0), Inches(4.1),
            "11 Core Team Assistants",
            [
                "Regulatory Affairs  ·  Clinical Affairs",
                "Systems Engineering  ·  R&D Lead",
                "V&V Lead  ·  Risk Management",
                "Human Factors  ·  Quality Engineering",
                "Cybersecurity  ·  Post-Market  ·  Program Manager",
                ("+ 2 panels:", "Core Team (PM/RA/Clinical/QE/R&D) and Design Review (Sys/R&D/V&V/HFE/Risk/QE)."),
            ])
bullet_card(s, Inches(6.7), Inches(2.7), Inches(6.0), Inches(4.1),
            "8 KOLs + 2 panels (project-specific)",
            [
                ("James E. Paul", "PCA pump safety, acute pain — primary PP3500 anchor KOL"),
                ("Kathleen K. Giuliano", "IV smart-pump usability, medication safety"),
                ("Priyadarshini Pennathur", "Human factors engineering"),
                ("Lisa Gorski", "Infusion nursing standards, vascular access"),
                ("Evan Kirkendall / Parth Shah / Sini Kuitunen / Susan Braithwaite",
                 "smart-pump safety, alert fatigue, pediatric dosing, insulin protocols"),
                ("+ 2 panels:", "round-robin and LLM-moderated PP3500 KOL panels."),
            ], accent=ACCENT)
add_footer(s, 9, 22)


# ── Slide 10: §2 Three-tier grounding ──────────────────────────
s = new_slide("02", "Agentic Approach")
add_slide_title(s, "Agentic Approach",
                "Three-tier grounding model",
                "Every advisor has grounding sources layered from most-portable to most-specific.")
tiers = [
    ("1", "Universal",
     "FDA guidance · ISO/IEC standards · industry frameworks · clinical literature. "
     "Identical across every medtech project scaffolded by /medtech-docs."),
    ("2", "Shape-stable",
     "Paths guaranteed by /medtech-docs — DHF layout, strategies/, submissions/, "
     "input-analysis/. The advisor knows where to look, regardless of project."),
    ("3", "Project-specific overlay",
     "project.yml → advisors.overlays.<name>.add / .exclude narrows the file set to "
     "what this program actually cares about (e.g. PCA regs, not hip-surgery regs)."),
]
cw = Inches(4.0)
for i, (num, title, body) in enumerate(tiers):
    x = Inches(0.6 + i * 4.15)
    number_card(s, x, Inches(2.9), cw, Inches(3.9), num, title, body,
                accent=[PRIMARY, ACCENT, PRIMARY_DARK][i])
add_footer(s, 10, 22)


# ── Slide 11: §3 Guardrails overview ───────────────────────────
s = new_slide("03", "Quality & Process")
add_slide_title(s, "Quality & Process",
                "Guardrails that make quality automatic",
                "Skills, hooks, and rules turn written conventions into executed ones.")
g = [
    ("Skills — reusable playbooks",
     "Named, one-command actions that every team member runs the same way. "
     "Remove inconsistency at the source. /task, /medtech-docs, /docflow, "
     "/tracker, /trace-matrix, /best-practices."),
    ("Hooks — automatic tripwires",
     "Small automations fired at a specific moment (session start, before an edit, "
     "when work ends) that allow, block, or add context. The system refuses to "
     "let you drift."),
    ("Rules — conventions the tool obeys",
     "Short conventions in CLAUDE.md / .claude/rules/ that Claude reads before "
     "acting. One task one file · READMEs have Conventions + Changelog · "
     "never fabricate standards or clinical content · demo banner everywhere."),
]
cw = Inches(4.0)
for i, (title, body) in enumerate(g):
    x = Inches(0.6 + i * 4.15)
    round_rect(s, x, Inches(2.9), cw, Inches(3.9), CARD_BG,
               border=BORDER, corner=0.04)
    rect(s, x, Inches(2.9), cw, Inches(0.12),
         [PRIMARY, ACCENT, PRIMARY_DARK][i])
    text(s, x + Inches(0.3), Inches(3.15), cw - Inches(0.5), Inches(0.8),
         title, size=16, bold=True, color=BLACK)
    text(s, x + Inches(0.3), Inches(3.95), cw - Inches(0.5), Inches(2.7),
         body, size=12, color=TEXT)
add_footer(s, 11, 22)


# ── Slide 12: §3 Hooks, in plain language ──────────────────────
s = new_slide("03", "Quality & Process")
add_slide_title(s, "Quality & Process",
                "Concrete automations, in plain language",
                "The hooks running today. What each one refuses to let you skip.")
hooks = [
    ("Task-first gate",        "No file edit without an active, owned task."),
    ("Session security check", "16 automated checks (identity, access, supply chain). High-severity failures block work."),
    ("Session env",            "Exports CLAUDE_SESSION_ID — the task gate keys its state on this."),
    ("Strategy / lessons capture",
     "If a prompt shows strategic intent but the task never captured a STRATEGY block, Stop is blocked."),
    ("Docflow entry",          "Raw pandoc / soffice / pdftotext Bash calls refused — must go through /docflow."),
    ("Session cleanup",        "Per-session state files purged on SessionEnd."),
]
col_w = Inches(6.0)
row_h = Inches(1.25)
for i, (title, body) in enumerate(hooks):
    col = i % 2
    row = i // 2
    x = Inches(0.6 + col * 6.2)
    y = Inches(2.7 + row * 1.35)
    round_rect(s, x, y, col_w, row_h, WHITE, border=BORDER, corner=0.04)
    rect(s, x, y, Inches(0.06), row_h, ACCENT)
    text(s, x + Inches(0.25), y + Inches(0.15),
         col_w - Inches(0.4), Inches(0.35),
         title, size=13, bold=True, color=BLACK)
    text(s, x + Inches(0.25), y + Inches(0.55),
         col_w - Inches(0.4), row_h - Inches(0.65),
         body, size=11, color=TEXT)
add_footer(s, 12, 22)


# ── Slide 13: §4 Humans in charge ──────────────────────────────
s = new_slide("04", "Humans in Charge")
add_slide_title(s, "Humans in Charge",
                "Agents advise. Humans decide.",
                "Cross-functional expertise on tap — with the decision-maker of record always a named human.")
bullet_card(s, Inches(0.6), Inches(2.7), Inches(4.0), Inches(4.1),
            "Advisors do",
            [
                "Brief the human with a structured, grounded analysis.",
                "Cite sources for every claim.",
                "Surface counterpoints automatically.",
                "Refuse to fabricate — say \"source doesn't support this.\"",
                "Leave a paper trail of what they read and said.",
            ])
bullet_card(s, Inches(4.7), Inches(2.7), Inches(4.0), Inches(4.1),
            "Humans do",
            [
                "Review the analysis · ask follow-ups.",
                "Choose the answer (agent may have given three).",
                "Write the decision into the task document.",
                "Sign off in the QMS of record — Part 11 signature by a named human.",
                "No AI-generated content enters a controlled artifact without human review.",
            ], accent=ACCENT)
bullet_card(s, Inches(8.8), Inches(2.7), Inches(4.0), Inches(4.1),
            "What the regulator sees",
            [
                "A human-signed decision.",
                "In a task document owned by a named person.",
                "Backed by a trace matrix rebuilt from source.",
                "Supported by structured analysis with cited sources.",
                "Vetted by multiple specialist perspectives.",
                "Produced in a toolchain whose compliance properties are enforced by hooks, not hope.",
            ], accent=PRIMARY_DARK)
add_footer(s, 13, 22)


# ── Slide 14: §4 Handoff table ─────────────────────────────────
s = new_slide("04", "Humans in Charge")
add_slide_title(s, "Humans in Charge",
                "Where the handoff happens",
                "The AI never occupies step 3 or step 6. That is the design, not a limitation.")
handoff = [
    ("1", "Draft analysis", "Agent",
     "Reads grounded sources, drafts structured answer with citations + counterpoints."),
    ("2", "Review & redirect", "Human",
     "Reviews the analysis, asks follow-ups, rejects or redirects."),
    ("3", "Decision", "Human",
     "Chooses the path forward and writes it into the task document."),
    ("4", "Implementation", "Human + agent",
     "Human directs; agent drafts; task-first gate ensures every edit is owned and traced."),
    ("5", "Verification", "Human (or panel)",
     "Independent panel agent reviews before the change is finalized."),
    ("6", "Sign-off in QMS of record", "Human only",
     "Controlled artifact promoted; signatures applied by named humans in the system of record."),
]
tbl_x = Inches(0.6)
tbl_y = Inches(2.7)
tbl_w = Inches(12.1)
rect(s, tbl_x, tbl_y, tbl_w, Inches(0.4), PRIMARY)
headers = [("#", Inches(0.6)), ("STEP", Inches(2.8)),
           ("WHO", Inches(2.4)), ("WHAT", Inches(6.3))]
x = tbl_x + Inches(0.25)
for h, w in headers:
    text(s, x, tbl_y, w, Inches(0.4), h, size=11, bold=True, color=WHITE,
         anchor=MSO_ANCHOR.MIDDLE)
    x += w
row_h = Inches(0.56)
for i, (n, step, who, what) in enumerate(handoff):
    y = tbl_y + Inches(0.4) + i * row_h
    if i % 2 == 0:
        rect(s, tbl_x, y, tbl_w, row_h, BODY_BG)
    x = tbl_x + Inches(0.25)
    row_color = PRIMARY_DARK if i in (2, 5) else TEXT
    badge_color = PRIMARY_DARK if who == "Human only" else (
        ACCENT if who == "Human" else PRIMARY)
    text(s, x, y, Inches(0.6), row_h, n, size=14, bold=True,
         color=badge_color, anchor=MSO_ANCHOR.MIDDLE)
    x += Inches(0.6)
    text(s, x, y, Inches(2.8), row_h, step, size=12, bold=True,
         color=BLACK, anchor=MSO_ANCHOR.MIDDLE)
    x += Inches(2.8)
    text(s, x, y, Inches(2.4), row_h, who, size=11, bold=True,
         color=badge_color, anchor=MSO_ANCHOR.MIDDLE)
    x += Inches(2.4)
    text(s, x, y, Inches(6.2), row_h, what, size=11,
         color=row_color, anchor=MSO_ANCHOR.MIDDLE)
add_footer(s, 14, 22)


# ── Console screenshot slides (15-20) ──────────────────────────
def console_slide(page, title, subtitle, image_path, url, notes=None):
    s = new_slide("05", "The Project Console")
    # Compact header (eyebrow + title + url) — frees vertical room for image
    text(s, Inches(0.6), Inches(0.95), Inches(12), Inches(0.3),
         "THE PROJECT CONSOLE", size=11, bold=True, color=PRIMARY)
    text(s, Inches(0.6), Inches(1.2), Inches(12), Inches(0.55),
         title, size=24, bold=True, color=BLACK)
    text(s, Inches(0.6), Inches(1.7), Inches(12), Inches(0.35),
         subtitle, size=12, color=TEXT_MUTED, italic=True)
    text(s, Inches(0.6), Inches(2.05), Inches(12), Inches(0.3),
         url, size=11, italic=True, color=ACCENT, font="Consolas")

    # Image area — compute actual display size, then size the FRAME to match,
    # centered on the slide. Leaves no empty whitespace around the screenshot.
    area_top = Inches(2.5)
    notes_h = Inches(0.3) if notes else Inches(0.0)
    area_bottom = Inches(7.0) - notes_h
    max_w = Inches(12.0)
    max_h = area_bottom - area_top

    if image_path.exists():
        from PIL import Image as PILImage
        im = PILImage.open(image_path)
        iw, ih = im.size
        ratio = iw / ih
        if max_w / ratio <= max_h:
            w = max_w
            h = int(w / ratio)
        else:
            h = max_h
            w = int(h * ratio)
        # Center horizontally, top-anchored in the available area
        x = int((SLIDE_W - w) / 2)
        y = area_top + int((max_h - h) / 2)
        # Frame sized to match the image exactly (plus a 3pt padding)
        pad = Emu(38100)
        rect(s, x - pad, y - pad, w + 2 * pad, h + 2 * pad, BORDER)
        s.shapes.add_picture(str(image_path), x, y, width=w, height=h)

    if notes:
        text(s, Inches(0.6), Inches(6.8), Inches(12.1), Inches(0.25),
             notes, size=10, italic=True, color=TEXT_MUTED)
    add_footer(s, page, 22)


console_slide(
    15, "Landing page",
    "Top-level tiles for Agents, Documents, Dashboards, and Trace Matrix — branded with the GlobalLogic theme.",
    ASSETS / "console-01-landing.png",
    "http://127.0.0.1:8765/",
    "Start / restart:  /project-console start    or    ./tools/project-console/run.sh",
)
console_slide(
    16, "Agents — 23 domain agents",
    "11 Core Team Assistants + 8 KOLs + 4 panels. Curated via project.yml → advisors.enabled.",
    ASSETS / "console-02-agents.png",
    "http://127.0.0.1:8765/agents",
)
console_slide(
    17, "A single agent chat",
    "Threaded, renameable, with a collapsible grounding-sources + system-prompt panel.",
    ASSETS / "console-07-agent-chat.png",
    "http://127.0.0.1:8765/agents/regulatory-affairs",
)
console_slide(
    18, "Documents explorer",
    "Full project tree · inline markdown rendering · unified Assistant drawer (ben/024) grounded on the open doc.",
    ASSETS / "console-03-documents.png",
    "http://127.0.0.1:8765/documents",
)
console_slide(
    19, "Dashboards — submission tracker",
    "Glob-discovered HTML dashboards rendered inline. Today: Submission Package Tracker (built by /tracker).",
    ASSETS / "console-05-submission-tracker.png",
    "http://127.0.0.1:8765/dashboards/submission-tracker",
)
console_slide(
    20, "Trace matrix — pca-device detail",
    "UN 22 · DI 34 · Arch 7 · V&V 3. Ct* filters, orphans-only toggle, SE Assistant drawer.",
    ASSETS / "console-08-trace-matrix-detail.png",
    "http://127.0.0.1:8765/trace-matrix/pca-device",
    "Headline gap — 30 Design-Input orphans — surfaced exactly as the trace matrix is designed to.",
)


# ── Slide 21: Appendix ─────────────────────────────────────────
s = new_slide("06", "Appendix")
add_slide_title(s, "Appendix", "Quick links",
                "Everything referenced in this deck.")
links = [
    ("Project operating rules", "CLAUDE.md"),
    ("Project manifest", "project.yml"),
    ("Companion markdown", "project-overview.md"),
    ("Regulatory strategy", "docs/project/strategies/regulatory-strategy.md"),
    ("Architecture strategy", "docs/project/strategies/architecture-strategy.md"),
    ("PCA device DHF", "docs/project/dhfs/pca-device/"),
    ("Cloud Suite DHF", "docs/project/dhfs/cloud-suite/"),
    ("510(k) composition manifest", "docs/project/submissions/510k/composition-manifest.md"),
    ("Submission tracker (md)", "docs/project/submissions/submission-tracker.md"),
    ("Console landing",      "http://127.0.0.1:8765/"),
    ("Console agents",       "http://127.0.0.1:8765/agents"),
    ("Console documents",    "http://127.0.0.1:8765/documents"),
    ("Console dashboards",   "http://127.0.0.1:8765/dashboards"),
    ("Console trace matrix", "http://127.0.0.1:8765/trace-matrix"),
]
tbl_x = Inches(0.6)
tbl_y = Inches(2.7)
tbl_w = Inches(12.1)
rect(s, tbl_x, tbl_y, tbl_w, Inches(0.4), PRIMARY)
text(s, tbl_x + Inches(0.25), tbl_y, Inches(4), Inches(0.4),
     "RESOURCE", size=11, bold=True, color=WHITE, anchor=MSO_ANCHOR.MIDDLE)
text(s, tbl_x + Inches(4.3), tbl_y, Inches(7.6), Inches(0.4),
     "LOCATION", size=11, bold=True, color=WHITE, anchor=MSO_ANCHOR.MIDDLE)
row_h = Inches(0.28)
for i, (name, loc) in enumerate(links):
    y = tbl_y + Inches(0.4) + i * row_h
    if i % 2 == 0:
        rect(s, tbl_x, y, tbl_w, row_h, BODY_BG)
    text(s, tbl_x + Inches(0.25), y, Inches(4), row_h, name,
         size=11, bold=True, color=BLACK, anchor=MSO_ANCHOR.MIDDLE)
    text(s, tbl_x + Inches(4.3), y, Inches(7.6), row_h, loc,
         size=10, color=ACCENT, anchor=MSO_ANCHOR.MIDDLE, font="Consolas")
add_footer(s, 21, 22)


# ── Slide 22: Thank you ────────────────────────────────────────
s = prs.slides.add_slide(BLANK)
rect(s, 0, 0, SLIDE_W, SLIDE_H, PRIMARY)
rect(s, 0, Inches(6.4), SLIDE_W, Inches(0.08), ACCENT)
if LOGO.exists():
    s.shapes.add_picture(
        str(LOGO), Inches(0.55), Inches(0.55),
        height=Inches(0.5), width=Inches(2.15))
text(s, Inches(0.6), Inches(2.5), Inches(12.1), Inches(1.5),
     "Thank you", size=64, bold=True, color=WHITE)
text(s, Inches(0.6), Inches(3.8), Inches(12.1), Inches(0.5),
     "Questions & discussion", size=20, color=WHITE)
text(s, Inches(0.6), Inches(6.6), Inches(12.1), Inches(0.35),
     "ben.xavier@globallogic.com  ·  PDLC_DEMO  ·  PainEase PCA Advanced (PP3500)",
     size=12, color=WHITE)
text(s, Inches(0.6), Inches(6.95), Inches(12.1), Inches(0.3),
     "A GlobalLogic demo of agentic PDLC workflows in MedTech.",
     size=11, italic=True, color=PRIMARY_TINT)


prs.save(str(OUT))
print(f"Wrote {OUT} ({OUT.stat().st_size:,} bytes, {len(prs.slides)} slides)")
