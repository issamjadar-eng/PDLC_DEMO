#!/usr/bin/env python3
"""
estar_completion_guide.py — generate an eSTAR/PreSTAR completion guide from a
section-map + a crosswalk (+ optionally the assembly manifest and a narrative
profile).

Since the FDA form is a dynamic XFA + JS PDF that open tooling cannot fill, this
produces the next-best thing: the exact structured answers a human types into
Acrobat + the attachment->source mapping, in two forms —
  • a machine-readable JSON (structured answers + per-section slot/source), shaped
    so a future Acrobat-Pro import step (XFA dataset) can consume it, and
  • a human Acrobat-entry checklist (markdown).

Template-parameterized via --sectionmap (nIVD eSTAR v7.0 by default; point at a
PreSTAR section-map for the Q-Sub). Run under the eStar venv (tools/estar/.venv).

Two optional inputs make the markdown guide a genuine last-mile document:
  --assembly-manifest  When present, § 2 is built from the REAL exhibit PDFs the
                       assembler produced (attachments[]), grouped by form section
                       — not from section-map slot-ID enumeration (those XFA field
                       IDs have no human labels and mislead the filer). Falls back
                       to a section listing when absent.
  --narrative          A generic, template-keyed profile (JSON) supplying the
                       plain-language intro / glossary / how-to steps / transmit
                       context. Injected only when its `template_match` matches the
                       section-map template_id. Keeps this shared generator generic:
                       the PreSTAR profile never leaks into the nIVD eSTAR guide.
                       Auto-resolved from data/estar/narrative-<template>.json when
                       not given explicitly.

Usage:
  estar_completion_guide.py --crosswalk CW.md [--sectionmap MAP.json]
      [--assembly-manifest ASM.json] [--narrative PROFILE.json]
      --out-json OUT.json --out-md OUT.md
"""
import argparse, json, os, re, glob


# ---------- crosswalk markdown table parsing ----------

def _table_after(md, heading_prefix):
    lines = md.splitlines()
    start = next((i for i, ln in enumerate(lines)
                  if ln.strip().startswith(heading_prefix)), None)
    if start is None:
        return None
    rows, in_tbl = [], False
    for ln in lines[start + 1:]:
        s = ln.strip()
        if s.startswith("|"):
            in_tbl = True
            cells = [c.strip() for c in s.strip("|").split("|")]
            if set("".join(cells)) <= set("-: "):
                continue
            rows.append(cells)
        elif in_tbl:
            break
    return rows or None


def _col(hdr, *names, default=None):
    for i, h in enumerate(hdr):
        if any(n.lower() in h.lower() for n in names):
            return i
    return default


# Match "[VERIFY]" AND "[VERIFY — note]" / "[VERIFY framing …]" (bracketed marker
# with trailing text) — the \b after VERIFY is the fix for the latter form.
HAS_VERIFY = re.compile(r"\[VERIFY\b|⚠|\(TBD\)|\bTBD\b")

# "§A #10" / "§ A #1–2" -> "§1 row 10" — the crosswalk's answer set is § A there,
# but it is renumbered § 1 in the guide, so the copied note refs must transpose.
# The number class deliberately stops at the range so it does not swallow a
# following space/paren (e.g. "§A #8 (SaMD)" -> "§1 row 8 (SaMD)").
_SECA_REF = re.compile(r"§\s*A\s*#\s*(\d+(?:\s*[–—-]\s*\d+)?)")


def transpose_refs(text):
    return _SECA_REF.sub(lambda m: "§1 row " + m.group(1).strip(), text or "")


def _verify_spans(text):
    """The specific unresolved markers in a cell — '[VERIFY …]' / '(TBD)' — so
    § 4 lists exactly what to resolve, not the whole surrounding cell."""
    return re.findall(r"\[VERIFY[^\]]*\]|\(TBD[^)]*\)", text or "")


def _first_bold(cell):
    """The section name — first **bold** run of a § B label cell (e.g.
    '**AdministrativeInformation** (…)' -> 'AdministrativeInformation'),
    preferred over _section_token for display since that one follows arrows
    into slot IDs."""
    m = re.search(r"\*\*([A-Za-z][\w /]*?)\*\*", cell)
    return m.group(1).strip() if m else (cell.split()[0] if cell.split() else "")


def parse_accuracy(md):
    rows = _table_after(md, "## A.")
    if not rows:
        return []
    hdr = rows[0]
    ci = _col(hdr, "Characteristic", default=1)
    ai = _col(hdr, "Answer", default=2)
    si = _col(hdr, "Source", default=3)
    out = []
    for r in rows[1:]:
        if len(r) <= max(ci, ai, si):
            continue
        out.append({"characteristic": r[ci], "answer": r[ai], "source": r[si],
                    "verify": bool(HAS_VERIFY.search(r[ai]))})
    return out


def _section_token(cell):
    """Pull the most specific section-map identifier from a § B first cell.
    '**SoftwareCyber -> Software** (…)' -> 'Software' (child after the last arrow);
    '**CoverLetter** (…)' -> 'CoverLetter'."""
    if "→" in cell:
        m = re.search(r"([A-Za-z][\w]*)", cell.rsplit("→", 1)[1])
        if m:
            return m.group(1)
    m = re.search(r"\*\*([A-Za-z][\w/]*)", cell)
    return m.group(1) if m else (cell.split()[0] if cell.split() else "")


def parse_sections(md):
    rows = _table_after(md, "## B.")
    if not rows:
        return []
    hdr = rows[0]
    ap = _col(hdr, "Applic", default=1)
    mo = _col(hdr, "Mode", default=2)
    so = _col(hdr, "source", "Our source", default=3)
    no = _col(hdr, "Notes", default=len(hdr) - 1)
    out = []
    for r in rows[1:]:
        if len(r) <= max(ap, mo, so):
            continue
        applic = ("N/A" if "⛔" in r[ap] else "gap" if "⚠" in r[ap]
                  else "in-scope" if "✅" in r[ap] else "other")
        notes = r[no] if no < len(r) else ""
        out.append({"token": _section_token(r[0]), "label": r[0],
                    "applicability": applic, "mode": r[mo], "source": r[so],
                    "notes": notes,
                    "verify": bool(HAS_VERIFY.search(r[so]) or HAS_VERIFY.search(notes))})
    return out


def parse_gaps(md):
    """§ C rows. Returns dicts with a `kind` ('action'|'context') when the table
    carries a Kind column; otherwise every row is 'action' (back-compat)."""
    rows = _table_after(md, "## C.")
    if not rows:
        return []
    hdr = rows[0]
    ki = _col(hdr, "Kind")
    ii = _col(hdr, "Item", default=(2 if ki is not None else 1))
    oi = _col(hdr, "Owner")
    ni = _col(hdr, "Note")
    idi = _col(hdr, "#", default=0)
    out = []
    for r in rows[1:]:
        if ii is None or len(r) <= ii:
            continue
        kind = (r[ki].strip().lower() if ki is not None and ki < len(r) else "action")
        kind = "context" if kind.startswith("context") else "action"
        out.append({
            "id": r[idi].strip() if idi is not None and idi < len(r) else "",
            "kind": kind,
            "item": r[ii].strip(),
            "owner": r[oi].strip() if oi is not None and oi < len(r) else "",
            "note": r[ni].strip() if ni is not None and ni < len(r) else "",
            # legacy flat string (JSON consumers / no-Kind fallback rendering)
            "text": " | ".join(r),
        })
    return out


# ---------- narrative profile ----------

def load_narrative(path, mapdata, script_dir):
    """Load a narrative profile if one matches this template. Explicit --narrative
    wins; else auto-resolve data/estar/narrative-*.json by template_id match.
    Returns the profile dict or None (None => minimal generic header, no leakage)."""
    tid = (mapdata.get("template_id") or "").lower()
    candidates = [path] if path else sorted(
        glob.glob(os.path.join(script_dir, "..", "data", "estar", "narrative-*.json")))
    for c in candidates:
        if not c or not os.path.exists(c):
            continue
        try:
            prof = json.load(open(c))
        except (ValueError, OSError):
            continue
        match = (prof.get("template_match") or "").lower()
        if path or (match and match in tid):
            return prof
    return None


# ---------- section-map slot enumeration (fallback § 2 only) ----------

def slots_by_name(mapdata):
    m = {}
    def walk(node):
        slots = [node["name"]] if node.get("attachment_slot") else []
        for s in node.get("subsections", []):
            slots += walk(s)
        name = node.get("name")
        if name and len(slots) >= len(m.get(name, [])):
            m[name] = slots
        return slots
    for sec in mapdata["sections"]:
        walk(sec)
    return m


def match_slots(token, name_map):
    if token in name_map:
        return name_map[token]
    for name, slots in name_map.items():
        if token and token.lower() == name.lower():
            return slots
    for name, slots in name_map.items():
        if token and (token.lower() in name.lower() or name.lower() in token.lower()):
            return slots
    return []


# ---------- exhibits from the assembly manifest (primary § 2) ----------

_CAMEL = re.compile(r"(?<=[a-z0-9])(?=[A-Z])")


def prettify_section(token):
    """CamelCase section token -> human label. 'DeviceDescription' ->
    'Device Description'; 'CoverLetter' -> 'Cover Letter'."""
    return _CAMEL.sub(" ", token).strip() or token


def build_exhibits(manifest):
    """Group assembler attachments[] by form section, preserving order. Each
    exhibit -> {file, section_label, what} where `what` is the doc title."""
    atts = manifest.get("attachments", []) if manifest else []
    exhibits = []
    for a in atts:
        fname = os.path.basename(a.get("output", "")) or a.get("output", "")
        exhibits.append({
            "n": a.get("n"),
            "file": fname,
            "section_label": prettify_section(a.get("section", "")),
            "what": (a.get("title") or "").strip(),
        })
    return exhibits


# ---------- build ----------

def build(mapdata, cw_md, manifest=None, narrative=None):
    answers = parse_accuracy(cw_md)
    sections = parse_sections(cw_md)
    gaps = parse_gaps(cw_md)
    exhibits = build_exhibits(manifest) if manifest else []

    if not exhibits:                      # fallback § 2 uses section-map slots
        name_map = slots_by_name(mapdata)
        for s in sections:
            s["attachment_slots"] = match_slots(s["token"], name_map)

    # § 4 items — extract the specific bracketed marker(s) rather than dumping the
    # whole source cell, so the filer sees exactly what to resolve.
    verify_items = []
    for a in answers:
        if a["verify"]:
            for sp in (_verify_spans(a["answer"]) or [a["answer"]]):
                verify_items.append(f"{a['characteristic']}: {sp}")
    for s in sections:
        if s["verify"]:
            name = _first_bold(s["label"])
            spans = _verify_spans(s["source"]) + _verify_spans(s["notes"])
            for sp in (spans or [f"see the {name} source"]):
                verify_items.append(f"{name}: {sp}")
    return {
        "template_id": mapdata.get("template_id"),
        "template_version": mapdata.get("template_version"),
        "form_technology": mapdata.get("form_technology"),
        "note": ("Human-entered in Acrobat Pro; the form's XFA/JS logic + eSTAR-Complete "
                 "verify run only there. This guide is the answer/attachment source of truth."),
        "structured_answers": answers,
        "sections": sections,
        "exhibits": exhibits,
        "verify_before_completion": verify_items,
        "gaps": gaps,
        "has_narrative": bool(narrative),
    }


def _emit_narrative_head(L, g, prof):
    tid = g["template_id"] or ""
    ver = g["template_version"] or ""
    L += [f"# Completion Guide — {tid} {ver}".rstrip(), "",
          f"> _Generated — do not hand-edit; re-run the generator._", ""]
    if prof.get("one_liner"):
        L += [f"**In one line:** {prof['one_liner']}", "", "---", ""]
    if prof.get("start_here"):
        L += list(prof["start_here"]) + [""]
    if prof.get("glossary"):
        L += ["### Words you'll see", "", "| Term | What it means here |", "|---|---|"]
        L += [f"| **{t}** | {d} |" for t, d in prof["glossary"]]
        L += [""]
    if prof.get("steps"):
        L += ["### How to fill it out — %d steps" % len(prof["steps"]), ""]
        if prof.get("steps_intro"):
            L += [prof["steps_intro"], ""]
        L += [f"{i}. {s}" for i, s in enumerate(prof["steps"], 1)]
        L += ["", "---", ""]


def to_md(g, prof=None):
    L = []
    if prof:
        _emit_narrative_head(L, g, prof)
    else:
        L += [f"# Completion Guide — {g['template_id']} {g['template_version']}".rstrip(), "",
              f"> _Generated — do not hand-edit; re-run the generator. {g['note']}_", ""]

    # § 1 — structured answers
    L += ["## 1. Structured answers to enter", "",
          "| Characteristic | Answer | Source |", "|---|---|---|"]
    for a in g["structured_answers"]:
        flag = " ⚠" if a["verify"] else ""
        L.append(f"| {a['characteristic']} | {a['answer']}{flag} | {a['source']} |")

    # § 2 — exhibits (manifest-driven) or fallback section listing
    L += ["", "## 2. Exhibits to attach", ""]
    if g["exhibits"]:
        ex = g["exhibits"]
        by_sec = {}
        for e in ex:
            by_sec.setdefault(e["section_label"], []).append(e)
        multi = [s for s, items in by_sec.items() if len(items) > 1]
        intro = (f"You were given **{len(ex)} PDF file%s** (in the `attachments/` folder). "
                 "Attach each one under the form section shown below. "
                 % ("s" if len(ex) != 1 else ""))
        if multi:
            intro += ("Most sections take a **single** file — "
                      + ", ".join(f"**{s}** takes {len(by_sec[s])}" for s in multi)
                      + ". ")
        intro += ("You never attach the same file twice, and you don't need to fill "
                  "every attachment box the form offers — only the ones listed here.")
        L += [intro, "",
              "| # | PDF to attach | Attach under form section | What it is |",
              "|---|---|---|---|"]
        for e in ex:
            L.append(f"| {e['n']} | `{e['file']}` | {e['section_label']} | {e['what']} |")
        if multi:
            L += ["", "> **When a section holds more than one file.** "
                  + "; ".join(f"**{s}** takes {len(by_sec[s])} PDFs" for s in multi)
                  + " — add them all under that one section's attachment area, not a "
                    "separate box for each."]
    else:
        L += ["_Run the eStar `assemble` action to resolve the exhibit PDFs; without the "
              "assembly manifest this lists the in-scope sections only._", "",
              "| Section | Source | Notes |", "|---|---|---|"]
        for s in g["sections"]:
            if s["applicability"] not in ("in-scope", "gap"):
                continue
            tag = " ⚠GAP" if s["applicability"] == "gap" else ""
            L.append(f"| {s['label']}{tag} | {s['source']} | {transpose_refs(s['notes'])} |")

    # § 3 — N/A sections
    na = [s for s in g["sections"] if s["applicability"] == "N/A"]
    if na:
        L += ["", "## 3. N/A sections — answer \"No/N-A\" (do NOT leave blank)", ""]
        L += [f"- {s['label']} — {transpose_refs(s['notes']) or 'device-type / scope driven'}"
              for s in na]

    # § 4 — resolve before completion (always emit -> contiguous numbering)
    L += ["", "## 4. Resolve before completion (`[VERIFY]` / TBD)", ""]
    if g["verify_before_completion"]:
        L += [f"- {transpose_refs(v)}" for v in g["verify_before_completion"]]
    else:
        L += ["- None outstanding."]

    # § 5 — before you transmit (action / context split)
    actions = [gp for gp in g["gaps"] if gp.get("kind") == "action"]
    context = [gp for gp in g["gaps"] if gp.get("kind") == "context"]
    if g["gaps"]:
        L += ["", "## 5. Before you transmit", ""]
        if actions:
            L += ["**Confirm before you send:**", ""]
            for gp in actions:
                owner = f" _({gp['owner']})_" if gp.get("owner") else ""
                note = f" — {gp['note']}" if gp.get("note") else ""
                L.append(f"- ☐ {transpose_refs(gp['item'])}{note}{owner}")
        ctx_lines = [f"- {transpose_refs(gp['item'])}" for gp in context]
        if prof and prof.get("transmit_context"):
            ctx_lines = list(prof["transmit_context"]) + ctx_lines
        if ctx_lines:
            L += ["", "**Deliberately open — *not* things to fix (context only):**", ""]
            L += ctx_lines

    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    default_map = os.path.normpath(os.path.join(
        os.path.dirname(__file__), "..", "data", "estar", "sectionmap-nivd-v7.0.json"))
    ap.add_argument("--sectionmap", default=default_map)
    ap.add_argument("--crosswalk", required=True)
    ap.add_argument("--assembly-manifest", default=None,
                    help="assembly-manifest.json — makes § 2 exhibit-driven")
    ap.add_argument("--narrative", default=None,
                    help="narrative profile JSON (auto-resolved by template if omitted)")
    ap.add_argument("--out-json", required=True)
    ap.add_argument("--out-md", required=True)
    a = ap.parse_args()

    mapdata = json.load(open(a.sectionmap))
    cw_md = open(a.crosswalk).read()
    manifest = None
    if a.assembly_manifest and os.path.exists(a.assembly_manifest):
        manifest = json.load(open(a.assembly_manifest))
    prof = load_narrative(a.narrative, mapdata, os.path.dirname(__file__))

    g = build(mapdata, cw_md, manifest=manifest, narrative=prof)

    with open(a.out_json, "w") as fh:
        json.dump(g, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    with open(a.out_md, "w") as fh:
        fh.write(to_md(g, prof))
    print(f"completion guide: {len(g['structured_answers'])} answers, "
          + (f"{len(g['exhibits'])} exhibits (manifest)"
             if g['exhibits'] else
             f"{sum(1 for s in g['sections'] if s['applicability'] in ('in-scope','gap'))} "
             "attachment sections (fallback)")
          + f", {len(g['verify_before_completion'])} verify items, "
          + f"narrative={'yes' if prof else 'no'}")
    print(f"  → {a.out_json}\n  → {a.out_md}")


if __name__ == "__main__":
    main()
