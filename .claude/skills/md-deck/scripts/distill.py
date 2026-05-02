#!/usr/bin/env python3
"""md-deck v0.5 — distill.py

Single-pass deck-wide distillation. One `claude -p` call reads the full source
markdown and produces a structured YAML dossier consumed by every downstream
creative slot generator (slots C and D).

Output structure (assets/<slug>/distillation.yml):

    meta:
        source, source_sha256, distilled_at, distilled_by_agent
    executive_summary: |
        Deck-wide summary in 3–5 sentences.
    executive_takeaways:
        - 4–6 short standalone sentences carrying the deck's load-bearing claims
    key_concepts:
        - { name, role }
    audience:
        inferred: bool
        primary:
            - { role, what_they_care_about, tonal_register }      # always 2–3 personas
    unifying_theme:
        big_idea: |
            One paragraph naming the deck's unifying argument.
        metaphor:
            name, why, confidence (0–1)
        visual_motifs:
            - description
        language_register:
            - guidance
        anti_patterns:
            - language to avoid
    guardrails:
        - facts the agent must not invent or violate
    sections:
        - anchor, section, title, rhetorical_move, primary_takeaway, feeling
          key_facts, data (optional structured viz block), metaphor_candidates
          contrast_pairs, deck_callbacks: { sets_up, pays_off }
          primary_audience_alignment, tone, warnings

The `data:` block per section is populated whenever the source carries
quantified content (percentages, counts, ratios, dated milestones, named
cohorts) — structured for visualization-ready rendering. Absent when the
section is purely qualitative.

Caching: assets/<slug>/distillation.yml carries `meta.source_sha256`. Re-run
only when source SHA changes or `--re-roll-distillation` is passed. The full
file is appended into every slot brief so creative agents see deck-wide
context, not just the section's raw markdown.
"""

from __future__ import annotations

import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from textwrap import dedent

import yaml


def _call_claude(prompt: str, *, model: str | None = None, timeout: int = 600) -> str:
    """Run `claude -p` with the prompt on stdin and return the raw text response.

    Same auth pattern as creative.py / skill-creator/scripts/improve_description.py.
    Strips CLAUDECODE from env to allow nesting inside an active Code session.
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


def build_distillation_brief(source_text: str, *, source_path: str, source_sha: str) -> str:
    """Build the prompt that produces a deck-wide distillation YAML."""
    return dedent(f"""
        You are an analyst preparing a structured intelligence brief for a slide-deck design pipeline. Read the entire source markdown below and produce ONE YAML document covering both deck-wide context and per-section dossiers. Downstream agents author creative slides using your output as their primary context.

        Three priorities for your brief:

        1. **Deck-wide intelligence.** Capture the executive summary, load-bearing takeaways, key concepts, audience personas, the unifying theme/metaphor, and language guardrails. Every section dossier downstream borrows from these.

        2. **Per-section dossiers.** For every H3-or-deeper section that has body content (skip H2-only dividers, skip the title block), produce a structured dossier. Each dossier names: rhetorical move, primary takeaway, key facts, metaphor candidates, contrast pairs, callbacks to other sections, audience alignment, tone, warnings. Anchor each dossier to its source line range as `anchor: L<lo>-L<hi>` matching the H3's first line and last body line.

        3. **Structured data blocks.** When a section carries quantified content (percentages, counts, ratios, dated milestones, named cohorts, before/after comparisons), populate a `data:` block in that section's dossier with shape:

            data:
                kind: bar | donut | timeline | comparison | ladder | cohort | none
                title: short caption for the visualization
                series:
                    - {{ label: "...", value: <number>, unit: "%" | "$" | etc., accent: "orange" | "amber" | "coral" | "muted" }}
                baseline: optional number for percent-of-baseline scales
                annotation: optional short rationale string

           Use `kind: timeline` when the data is a sequence of dated events (each series item is a milestone with `when` instead of `value`). Use `kind: cohort` when the data is N members of a homogeneous group (each series item names a member with optional role). Set `kind: none` (or omit `data:`) when the section is purely qualitative.

        Audience inference rule: ALWAYS produce 2–3 personas, even when the source names an audience. The named audience is one persona; surface 1–2 secondary stakeholders the deck implicitly addresses. Set `audience.inferred: true` when the source did not name an audience explicitly.

        Unifying metaphor rule: ALWAYS propose one with a `confidence` 0–1 score. Slot generators can ignore low-confidence metaphors. Forcing articulation is better than silence — slots get a fallback hook.

        Output format constraints (strict subset of YAML 1.2):

        - Top-level keys: `meta`, `executive_summary`, `executive_takeaways`, `key_concepts`, `audience`, `unifying_theme`, `guardrails`, `sections`. Use them all.
        - Use block-style mappings with two-space indent. No flow-style maps inside lists.
        - Use pipe-string `|` for multi-line strings (executive_summary, big_idea).
        - Use plain or single-quoted scalars. Avoid double-quotes.
        - No anchors (`&`), no aliases (`*`), no tags (`!!`).
        - Numbers as numbers (not strings). Booleans as `true`/`false`.

        Set `meta.source` to `{source_path}` and `meta.source_sha256` to `{source_sha}`. Set `meta.distilled_by_agent` to `claude-opus-4-7`. Leave `meta.distilled_at` as `__BUILD_TIME__` (the wrapping build script will substitute).

        ────────────────────────────────────────────
        SOURCE MARKDOWN
        ────────────────────────────────────────────
        {source_text}
        ────────────────────────────────────────────

        Output: emit the YAML document and nothing else. No prose, no Markdown fence, no commentary. The very first characters of your response must be `meta:` (or `---\\nmeta:`) and the document must parse with PyYAML's safe_load. Aim for ~150-300 lines.
    """).strip()


def _strip_yaml_fence(raw: str) -> str:
    """Tolerate accidental ```yaml ... ``` fences from the agent."""
    text = raw.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text
    if text.endswith("```"):
        text = text.rsplit("\n", 1)[0] if "\n" in text else text
    return text.strip()


def distill_source(
    source_path: Path,
    out_dir: Path,
    *,
    source_sha: str,
    force: bool = False,
    model: str | None = None,
) -> dict:
    """Produce or load a distillation for `source_path`.

    Cached at `out_dir/distillation.yml`. Returns the parsed dict. Re-runs
    when source SHA mismatches, when `force=True`, or when the cache file is
    absent or unparseable.
    """
    cache_path = out_dir / "distillation.yml"

    # Try the cache first
    if cache_path.exists() and not force:
        try:
            cached = yaml.safe_load(cache_path.read_text(encoding="utf-8"))
            if cached and cached.get("meta", {}).get("source_sha256") == source_sha:
                return cached
        except yaml.YAMLError:
            pass  # fall through to regenerate

    # Build the brief and call the agent
    source_text = source_path.read_text(encoding="utf-8")
    brief = build_distillation_brief(
        source_text,
        source_path=source_path.name,
        source_sha=source_sha,
    )
    print(f"  · distilling source ({len(source_text)} chars) via claude -p…", file=sys.stderr)
    raw = _call_claude(brief, model=model)
    text = _strip_yaml_fence(raw)

    # Substitute the build time
    text = text.replace("__BUILD_TIME__", datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))

    try:
        parsed = yaml.safe_load(text)
    except yaml.YAMLError as e:
        debug_path = out_dir / "distillation-debug.txt"
        debug_path.write_text(raw or "(empty)", encoding="utf-8")
        raise RuntimeError(
            f"distillation YAML parse failed: {e}. Raw response saved to {debug_path}"
        )

    if not isinstance(parsed, dict) or "meta" not in parsed:
        raise RuntimeError("distillation missing required top-level structure (meta + …)")

    cache_path.write_text(text, encoding="utf-8")
    print(f"  · distillation cached to {cache_path.relative_to(Path.cwd()) if Path.cwd() in cache_path.parents else cache_path}", file=sys.stderr)
    return parsed


def section_dossier(distillation: dict, anchor: str) -> dict | None:
    """Look up the per-section dossier for a given source-line anchor."""
    for section in (distillation.get("sections") or []):
        if section.get("anchor") == anchor:
            return section
    return None


def deck_brief_block(distillation: dict) -> str:
    """Render the deck-wide intelligence as a text block for slot briefs."""
    if not distillation:
        return "(no deck-wide distillation available)"
    parts: list[str] = []
    parts.append("DECK-WIDE INTELLIGENCE")
    parts.append("──────────────────────")
    summary = (distillation.get("executive_summary") or "").strip()
    if summary:
        parts.append(f"Executive summary:\n{summary}\n")
    takeaways = distillation.get("executive_takeaways") or []
    if takeaways:
        parts.append("Executive takeaways:")
        parts.extend(f"  · {t}" for t in takeaways)
        parts.append("")
    theme = distillation.get("unifying_theme") or {}
    big = theme.get("big_idea")
    if big:
        parts.append(f"Big idea:\n{big.strip()}\n")
    # `metaphor` may come back as either {name, why, confidence} or a flat string
    # (agent variance). Tolerate both.
    metaphor = theme.get("metaphor")
    if isinstance(metaphor, dict):
        if metaphor.get("name"):
            conf = metaphor.get("confidence", "")
            parts.append(f"Unifying metaphor: {metaphor['name']} (confidence: {conf})")
            if metaphor.get("why"):
                parts.append(f"  why: {metaphor['why']}")
            parts.append("")
    elif isinstance(metaphor, str) and metaphor.strip():
        conf = theme.get("confidence", "")
        parts.append(f"Unifying metaphor: {metaphor.strip()}" + (f" (confidence: {conf})" if conf else ""))
        parts.append("")
    motifs = theme.get("visual_motifs") or []
    if motifs:
        parts.append("Visual motifs to reinforce across the deck:")
        parts.extend(f"  · {m}" for m in motifs)
        parts.append("")
    register = theme.get("language_register") or []
    if register:
        parts.append("Language register:")
        parts.extend(f"  · {r}" for r in register)
        parts.append("")
    anti = theme.get("anti_patterns") or []
    if anti:
        parts.append("Anti-patterns to avoid:")
        parts.extend(f"  · {a}" for a in anti)
        parts.append("")
    aud_block = distillation.get("audience") or {}
    audience = aud_block.get("primary") or aud_block.get("personas") or []
    if audience:
        parts.append("Audience personas:")
        for p in audience:
            if isinstance(p, dict):
                role = p.get("role", "?")
                cares = p.get("what_they_care_about") or p.get("cares_about") or p.get("lens") or "?"
                register = p.get("tonal_register") or p.get("register") or ""
                line = f"  · {role} — cares about: {cares}"
                if register:
                    line += f" · register: {register}"
                parts.append(line)
            else:
                parts.append(f"  · {p}")
        parts.append("")
    guard = distillation.get("guardrails") or []
    if guard:
        parts.append("Guardrails:")
        parts.extend(f"  · {g}" for g in guard)
        parts.append("")
    concepts = distillation.get("key_concepts") or []
    if concepts:
        parts.append("Key concepts:")
        for c in concepts:
            if isinstance(c, dict):
                name = c.get("name", "?")
                gloss = c.get("role") or c.get("definition") or c.get("description") or "?"
                parts.append(f"  · {name} — {gloss}")
            else:
                parts.append(f"  · {c}")
        parts.append("")
    return "\n".join(parts)


def section_brief_block(dossier: dict | None) -> str:
    """Render one section's dossier as a text block for the slot brief."""
    if not dossier:
        return "(no section dossier — fall back to raw markdown only)"
    parts: list[str] = []
    parts.append("THIS SECTION'S DOSSIER")
    parts.append("──────────────────────")
    parts.append(f"§{dossier.get('section','?')} — {dossier.get('title','?')}")
    if dossier.get("rhetorical_move"):
        parts.append(f"Rhetorical move: {dossier['rhetorical_move']}")
    if dossier.get("primary_takeaway"):
        parts.append(f"Primary takeaway: {dossier['primary_takeaway']}")
    if dossier.get("feeling"):
        parts.append(f"Feeling: {dossier['feeling']}")
    facts = dossier.get("key_facts") or []
    if facts:
        parts.append("Key facts:")
        parts.extend(f"  · {f}" for f in facts)
    data = dossier.get("data")
    if data and data.get("kind") and data.get("kind") != "none":
        parts.append(f"Structured data block (kind: {data['kind']}):")
        if data.get("title"):
            parts.append(f"  title: {data['title']}")
        for s in (data.get("series") or []):
            if isinstance(s, dict):
                fields = " · ".join(f"{k}={v}" for k, v in s.items())
                parts.append(f"  · {fields}")
        if data.get("baseline") is not None:
            parts.append(f"  baseline: {data['baseline']}")
        if data.get("annotation"):
            parts.append(f"  annotation: {data['annotation']}")
    metaphors = dossier.get("metaphor_candidates") or []
    if metaphors:
        parts.append("Metaphor candidates:")
        parts.extend(f"  · {m}" for m in metaphors)
    pairs = dossier.get("contrast_pairs") or []
    if pairs:
        parts.append("Contrast pairs:")
        parts.extend(f"  · {p}" for p in pairs)
    callbacks = dossier.get("deck_callbacks") or {}
    if callbacks.get("sets_up"):
        parts.append(f"Sets up: {', '.join(callbacks['sets_up'])}")
    if callbacks.get("pays_off"):
        parts.append(f"Pays off: {', '.join(callbacks['pays_off'])}")
    if dossier.get("primary_audience_alignment"):
        parts.append(f"Primary audience alignment: {dossier['primary_audience_alignment']}")
    if dossier.get("tone"):
        parts.append(f"Tone: {dossier['tone']}")
    warnings = dossier.get("warnings") or []
    if warnings:
        parts.append("Warnings:")
        parts.extend(f"  · {w}" for w in warnings)
    return "\n".join(parts)


if __name__ == "__main__":
    # CLI helper: dump or generate the distillation for a source.
    import argparse
    parser = argparse.ArgumentParser(description="md-deck distillation utility")
    parser.add_argument("source", help="Markdown source file")
    parser.add_argument("--out-dir", default=None, help="Override output directory")
    parser.add_argument("--force", action="store_true", help="Re-roll the distillation even if cached")
    parser.add_argument("--dump", action="store_true", help="Dump the parsed distillation as YAML to stdout")
    args = parser.parse_args()

    import hashlib
    src = Path(args.source)
    sha = hashlib.sha256(src.read_text(encoding="utf-8").encode()).hexdigest()
    out_dir = Path(args.out_dir) if args.out_dir else (Path.cwd() / "assets" / src.stem)
    out_dir.mkdir(parents=True, exist_ok=True)

    distillation = distill_source(src, out_dir, source_sha=sha, force=args.force)
    if args.dump:
        print(yaml.safe_dump(distillation, sort_keys=False, allow_unicode=True))
