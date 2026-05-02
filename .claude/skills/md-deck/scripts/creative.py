#!/usr/bin/env python3
"""md-deck v0.5 — creative.py

Slot C and Slot D in candidates.html — agent-authored bespoke slides.

Shells out to `claude -p --output-format text` per the project's existing
pattern (`skill-creator/scripts/improve_description.py`). Reuses the user's
Claude Max session — no separate ANTHROPIC_API_KEY needed. CLAUDECODE env
var is stripped to allow nesting the call inside an active Claude Code
session.

Two slot personalities are built into separate briefs:

- `bold-metaphor` — lead with a visual primitive (drawn diagram, conic donut,
  diagonal split, layered stack). Aggressive use of color and CSS-art.
- `restrained-takeaway` — oversized typography, generous whitespace, one or
  two visual elements max. Rhetorical force through restraint.

Output contract: each call returns one self-contained
`<section class="slide creative">...</section>` HTML fragment, ready to be
embedded directly into the candidates.html grid and (when picked) into the
final deck index.html.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path
from textwrap import dedent

SKILL_DIR = Path(__file__).resolve().parent.parent  # .claude/skills/md-deck/
SKILLS_ROOT = SKILL_DIR.parent
FRONTEND_SLIDES_DIR = SKILLS_ROOT / "frontend-slides"
CREATIVE_PALETTE = FRONTEND_SLIDES_DIR / "creative-palette.md"


# ---------------------------------------------------------------------------
# Brief construction
# ---------------------------------------------------------------------------

SLOT_PERSONALITIES = {
    "bold-metaphor": dedent("""
        Personality: BOLD METAPHOR — illustrative / atmospheric.

        Lead with a visual primitive that ENCODES the content's meaning. Drawn
        diagrams, conic-gradient figures, diagonal/clip-path splits, layered
        stacks of cards, CSS-art motifs, layered shapes with depth, gradients
        as texture. Aesthetic-first. The goal is "this slide is a THING that
        carries the idea visually" — color, layout, and form do the talking.

        Pick a metaphor that is HONEST to the content. Free-flow on disconnect
        is not a daisy chain. A 38% reduction is not a sunset. Reach for the
        metaphor the content itself implies, then render it with brand colors,
        gradients, shapes — not just type.

        At least 60% of the slide-content area must be NON-TEXT visual primitives
        (drawn shapes, gradients, geometric figures, illustrative SVG-style
        compositions). Text is supporting, never the main element.
        """).strip(),
    "structured-diagram": dedent("""
        Personality: STRUCTURED DIAGRAM — precise / data-driven.

        Build a clean, information-dense visualization that a stakeholder can
        SCAN and UNDERSTAND in seconds. Drawn bar charts, donut/conic gradients,
        timelines with stops, process loops, swimlanes, before/after deltas,
        threat-mitigation pair grids, hazard-control chains, treemaps,
        feature-matrix grids with checks/crosses, sankey flows. Function-first.
        The goal is "this slide IS a chart or diagram, not a paragraph with
        decoration."

        **Hard rule: this slide must not be primarily typography.** No oversized
        headline as the hero. No "big phrase + small phrase" stacks. No
        eyebrow-headline-supporting-line restraint plays. If you find yourself
        reaching for `font-family: var(--font-display)` at clamp(2rem, 6vw, 5rem)
        as the centerpiece, STOP and choose a structural diagram instead.

        When the section dossier carries a `data:` block, ENCODE THAT DATA into
        the diagram — bars proportional to values, donut segments matching the
        ratios, timeline stops at the named milestones. Use the data's accent
        color hints. When no `data:` block exists, look for relationships you
        can structure: "in vs out", "before vs after", "actor → action → outcome",
        "cause → control → residual", "phase → phase → phase".

        At least 70% of the slide-content area must be drawn structural elements
        (axes, bars, dots, connecting lines, grids, shapes encoding values or
        relationships). Text is annotation, never the main element.
        """).strip(),
    # Legacy alias — `restrained-takeaway` redirects to structured-diagram so
    # cached briefs from older runs still resolve. The personality name in the
    # build pipeline (slot identifier "creative-d") stays the same.
    "restrained-takeaway": dedent("""
        Personality: STRUCTURED DIAGRAM — precise / data-driven.

        (slot D — replaces the v0.5 "restrained-takeaway" typography play.)

        Build a clean, information-dense visualization a stakeholder can SCAN
        in seconds. Drawn bar charts, donut/conic gradients, timelines with
        stops, process loops, swimlanes, before/after deltas, threat-mitigation
        pair grids, treemaps, feature-matrix grids, sankey flows.

        **Hard rule: not primarily typography.** No oversized headline as the
        hero. No "big phrase + small phrase" stacks. If you find yourself
        reaching for `font-family: var(--font-display)` at the largest clamp()
        size as the centerpiece, STOP and choose a structural diagram instead.

        When the section dossier carries a `data:` block, ENCODE THAT DATA — bars
        proportional to values, donut segments matching ratios, timeline stops
        at named milestones. When no data block exists, look for structural
        relationships: in vs out, before vs after, actor→action→outcome,
        cause→control→residual, phase→phase→phase.

        At least 70% of the slide-content area must be drawn structural elements
        (axes, bars, dots, connecting lines, shapes encoding values or
        relationships). Text is annotation, never the main element.
        """).strip(),
}


def build_brief(
    *,
    section_markdown: str,
    section_title: str,
    section_anchor: str,
    section_number: str | None,
    slot_personality: str,
    palette_text: str,
    reference_html_a: str,
    reference_html_b: str,
    deck_brief: str = "",
    section_brief: str = "",
) -> str:
    """Compose the system+user prompt for one creative slide generation.

    `deck_brief` and `section_brief` are pre-formatted text blocks produced by
    `distill.deck_brief_block()` and `distill.section_brief_block()`. When
    present they replace raw-markdown context with a structured intelligence
    dossier — the agent designs against a shared deck understanding instead of
    re-reading the markdown.
    """
    personality_block = SLOT_PERSONALITIES.get(slot_personality, SLOT_PERSONALITIES["bold-metaphor"])

    distillation_section = ""
    if deck_brief or section_brief:
        distillation_section = dedent(f"""
            ────────────────────────────────────────────
            DECK + SECTION DISTILLATION
            (your primary context — DESIGN AGAINST THIS, not the raw markdown)
            ────────────────────────────────────────────
            {deck_brief}

            {section_brief}
            ────────────────────────────────────────────
        """).strip()

    return dedent(f"""
        You are a slide designer for md-deck, building one bespoke slide of an HTML presentation. You are not selecting from a fixed component library — you are AUTHORING a custom layout that fits this specific content.

        {distillation_section}

        ────────────────────────────────────────────
        SECTION SOURCE MARKDOWN (for reference only — distillation above is canonical)
        ────────────────────────────────────────────
        {section_markdown.strip()}
        ────────────────────────────────────────────

        Section number: §{section_number or "?"}
        Section title:  {section_title}
        Section anchor: {section_anchor}

        ────────────────────────────────────────────
        SLOT PERSONALITY
        ────────────────────────────────────────────
        {personality_block}
        ────────────────────────────────────────────

        ────────────────────────────────────────────
        CREATIVE PALETTE (grounding patterns + chrome contract)
        ────────────────────────────────────────────
        {palette_text}
        ────────────────────────────────────────────

        ────────────────────────────────────────────
        DETERMINISTIC SLOTS A AND B (already filled — do NOT repeat their layout)
        ────────────────────────────────────────────
        SLOT A:
        {reference_html_a or "(no slot A reference available)"}

        SLOT B:
        {reference_html_b or "(no slot B reference available)"}
        ────────────────────────────────────────────

        Your task:

        Produce ONE slide HTML fragment that fits this section's content using the slot personality above. The slide must:

        1. Honor the chrome contract from the creative-palette (a `<section class="slide creative">` with `<div class="chrome">` strip and a `<div class="slide-content">` body).
        2. Carry `data-source-anchor="{section_anchor}"` on the `<section>` element.
        3. Carry `data-creative-rationale="<one-sentence reason this layout fits this content + how it connects to the deck's big idea or visual motif>"` on the `<section>` element.
        4. Use only the CSS variables listed in the creative-palette. Use `clamp()` for sizes. No `<style>` block — inline `style="..."` attributes are fine. No external font @import (the deck loads Archivo Black, Space Grotesk, Space Mono via the preset).
        5. Fit at 100vh with overflow:hidden. No scrolling within the slide.
        6. Differ visually from slot A and slot B in *layout shape*, not just colors.
        7. **When the section dossier carries a `data:` block, prefer encoding that data visually** (drawn bars, donuts, timelines, ladders, comparison pairs) over running prose. Honor the data's `accent` color hints when present.
        8. **Lean into the deck's unifying metaphor and visual motifs** when their confidence is high — coherence with sibling slides is a feature, not a constraint. Use language register from the distillation; avoid the anti-patterns it lists.

        Output: emit the `<section>` tag and nothing else. No prose, no Markdown fence, no commentary. The very first character of your response must be `<` and the very last character must be `>`.
    """).strip()


# ---------------------------------------------------------------------------
# Subprocess invocation — same pattern as skill-creator/scripts/improve_description.py
# ---------------------------------------------------------------------------

def _call_claude(prompt: str, *, model: str | None = None, timeout: int = 240) -> str:
    """Run `claude -p` with the prompt on stdin and return the raw text response.

    Same auth pattern as run_eval.py / improve_description.py — uses the
    session's Claude Code auth, no separate ANTHROPIC_API_KEY needed. Strip
    CLAUDECODE from env to allow nesting inside an active Claude Code session.
    """
    cmd = ["claude", "-p", "--output-format", "text"]
    if model:
        cmd.extend(["--model", model])

    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}

    result = subprocess.run(
        cmd,
        input=prompt,
        capture_output=True,
        text=True,
        env=env,
        timeout=timeout,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"claude -p exited {result.returncode}\nstderr:\n{result.stderr}"
        )
    return result.stdout


# ---------------------------------------------------------------------------
# HTML extraction
# ---------------------------------------------------------------------------

_SECTION_RE = re.compile(
    r"<section\s+class\s*=\s*[\"'][^\"']*\bslide\b[^\"']*[\"'][^>]*>.*?</section>",
    re.DOTALL | re.IGNORECASE,
)


def extract_slide_html(raw: str) -> str | None:
    """Pull the first `<section class="slide ...">…</section>` block from the
    agent's response. Tolerate accidental Markdown fences or leading prose."""
    if not raw:
        return None
    # Strip Markdown code fences if present
    text = raw.strip()
    text = re.sub(r"^```(?:html)?\s*\n", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\n```\s*$", "", text)
    m = _SECTION_RE.search(text)
    if not m:
        return None
    return m.group(0)


# ---------------------------------------------------------------------------
# Public API — generate one creative slide
# ---------------------------------------------------------------------------

def load_palette() -> str:
    if CREATIVE_PALETTE.exists():
        return CREATIVE_PALETTE.read_text(encoding="utf-8")
    return "(palette file not found — agent works without grounding patterns)"


def generate_creative_slide(
    *,
    section_markdown: str,
    section_title: str,
    section_anchor: str,
    section_number: str | None,
    slot_personality: str,
    reference_html_a: str = "",
    reference_html_b: str = "",
    deck_brief: str = "",
    section_brief: str = "",
    model: str | None = None,
    timeout: int = 240,
) -> tuple[str | None, str]:
    """Generate one creative slide. Returns (html_or_none, raw_response).

    The raw_response is preserved for diagnostic logging — when extraction
    fails (None HTML), the caller can write the raw text to a debug file.
    """
    palette = load_palette()
    brief = build_brief(
        section_markdown=section_markdown,
        section_title=section_title,
        section_anchor=section_anchor,
        section_number=section_number,
        slot_personality=slot_personality,
        palette_text=palette,
        reference_html_a=reference_html_a,
        reference_html_b=reference_html_b,
        deck_brief=deck_brief,
        section_brief=section_brief,
    )
    raw = _call_claude(brief, model=model, timeout=timeout)
    html = extract_slide_html(raw)
    return html, raw


if __name__ == "__main__":
    # Smoke test: generate a slide for a fixture section and print the result.
    sample = {
        "markdown": "### 4.2 What we measured\n\n> The 12 weeks produced equivalent IEC 62304 documentation in 38% of the calendar time.",
        "title": "What we measured",
        "anchor": "L116-L120",
        "number": "4.2",
    }
    html, raw = generate_creative_slide(
        section_markdown=sample["markdown"],
        section_title=sample["title"],
        section_anchor=sample["anchor"],
        section_number=sample["number"],
        slot_personality=sys.argv[1] if len(sys.argv) > 1 else "bold-metaphor",
    )
    print("=== HTML ===" if html else "=== EXTRACTION FAILED ===")
    print(html or raw)
