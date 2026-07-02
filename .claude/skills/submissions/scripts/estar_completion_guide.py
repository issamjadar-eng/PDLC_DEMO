#!/usr/bin/env python3
"""
estar_completion_guide.py — generate an eSTAR/PreSTAR completion guide from a
section-map + a crosswalk.

Since the FDA form is a dynamic XFA + JS PDF that open tooling cannot fill, this
produces the next-best thing: the exact structured answers a human types into
Acrobat + the attachment→source mapping, in two forms —
  • a machine-readable JSON (structured answers + per-section slot/source), shaped
    so a future Acrobat-Pro import step (XFA dataset) can consume it, and
  • a human Acrobat-entry checklist (markdown).

Template-parameterized via --sectionmap (nIVD eSTAR v7.0 by default; point at a
PreSTAR section-map for the Q-Sub). Run under the eStar venv (tools/estar/.venv).

Usage:
  estar_completion_guide.py --crosswalk CW.md [--sectionmap MAP.json]
      --out-json OUT.json --out-md OUT.md
"""
import argparse, json, os, re


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


HAS_VERIFY = re.compile(r"\[VERIFY\]|⚠|\(TBD\)|\bTBD\b")


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
    '**SoftwareCyber → Software** (…)' -> 'Software' (the child after the last →);
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
        out.append({"token": _section_token(r[0]), "label": r[0],
                    "applicability": applic, "mode": r[mo], "source": r[so],
                    "notes": r[no] if no < len(r) else "",
                    "verify": bool(HAS_VERIFY.search(r[so]))})
    return out


def parse_gaps(md):
    rows = _table_after(md, "## C.")
    if not rows:
        return []
    return [" | ".join(r) for r in rows[1:]]


# ---------- section-map slot enumeration ----------

def slots_by_name(mapdata):
    """Map EVERY named subform -> the attachment slots in its subtree, so a
    crosswalk row that names a sub-section (Software / Cybersecurity / Wireless)
    resolves to that sub-section's own slots, not the whole parent's."""
    m = {}
    def walk(node):
        slots = [node["name"]] if node.get("attachment_slot") else []
        for s in node.get("subsections", []):
            slots += walk(s)
        name = node.get("name")
        if name and len(slots) >= len(m.get(name, [])):   # keep richest on collision
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
    for name, slots in name_map.items():           # substring fallback
        if token and (token.lower() in name.lower() or name.lower() in token.lower()):
            return slots
    return []


# ---------- build ----------

def build(mapdata, cw_md):
    answers = parse_accuracy(cw_md)
    sections = parse_sections(cw_md)
    gaps = parse_gaps(cw_md)
    name_map = slots_by_name(mapdata)
    for s in sections:
        s["attachment_slots"] = match_slots(s["token"], name_map)
    verify_items = ([f"answer: {a['characteristic']} = {a['answer']}"
                     for a in answers if a["verify"]] +
                    [f"source: {s['label']} — {s['source']}"
                     for s in sections if s["verify"]])
    return {
        "template_id": mapdata.get("template_id"),
        "template_version": mapdata.get("template_version"),
        "form_technology": mapdata.get("form_technology"),
        "note": ("Human-entered in Acrobat Pro; the form's XFA/JS logic + eSTAR-Complete "
                 "verify run only there. This guide is the answer/attachment source of truth."),
        "structured_answers": answers,
        "sections": sections,
        "verify_before_completion": verify_items,
        "gaps": gaps,
    }


def to_md(g):
    L = [f"# Completion Guide — {g['template_id']} {g['template_version']}", "",
         f"> _Generated — do not hand-edit; re-run the generator. {g['note']}_", "",
         "**How to use:** open the template in Acrobat Pro → enter the § 1 structured "
         "answers → prepare + attach the § 2 exhibits (each an admissible PDF via "
         "`/docflow`; run `estar_lint.py --attachments`) → resolve § 3 → run the in-Acrobat "
         "verify (green banner) → transmit via the CDRH Portal.", ""]

    L += ["## 1. Structured answers to enter", "",
          "| Characteristic | Answer | Source |", "|---|---|---|"]
    for a in g["structured_answers"]:
        flag = " ⚠" if a["verify"] else ""
        L.append(f"| {a['characteristic']} | {a['answer']}{flag} | {a['source']} |")

    L += ["", "## 2. Attachments to prepare + load (in-scope sections)", "",
          "| Section | Source to convert → attach | eSTAR slot(s) | Notes |", "|---|---|---|---|"]
    for s in g["sections"]:
        if s["applicability"] not in ("in-scope", "gap"):
            continue
        slots = ", ".join(f"`{x}`" for x in s["attachment_slots"]) or "—"
        tag = " ⚠GAP" if s["applicability"] == "gap" else ""
        L.append(f"| {s['label']}{tag} | {s['source']} | {slots} | {s['notes']} |")

    na = [s for s in g["sections"] if s["applicability"] == "N/A"]
    if na:
        L += ["", "## 3. N/A sections — answer \"No/N-A\" (do NOT leave blank)", ""]
        L += [f"- {s['label']} — {s['notes'] or 'device-type / scope driven'}" for s in na]

    if g["verify_before_completion"]:
        L += ["", "## 4. ⚠ Resolve before completion (`[VERIFY]` / TBD)", ""]
        L += [f"- {v}" for v in g["verify_before_completion"]]

    if g["gaps"]:
        L += ["", "## 5. Open gap→action items (from crosswalk § C)", ""]
        L += [f"- {gp}" for gp in g["gaps"]]

    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    default_map = os.path.normpath(os.path.join(
        os.path.dirname(__file__), "..", "data", "estar", "sectionmap-nivd-v7.0.json"))
    ap.add_argument("--sectionmap", default=default_map)
    ap.add_argument("--crosswalk", required=True)
    ap.add_argument("--out-json", required=True)
    ap.add_argument("--out-md", required=True)
    a = ap.parse_args()

    mapdata = json.load(open(a.sectionmap))
    cw_md = open(a.crosswalk).read()
    g = build(mapdata, cw_md)

    with open(a.out_json, "w") as fh:
        json.dump(g, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    with open(a.out_md, "w") as fh:
        fh.write(to_md(g))
    print(f"completion guide: {len(g['structured_answers'])} answers, "
          f"{sum(1 for s in g['sections'] if s['applicability'] in ('in-scope','gap'))} "
          f"attachment sections, {len(g['verify_before_completion'])} verify items")
    print(f"  → {a.out_json}\n  → {a.out_md}")


if __name__ == "__main__":
    main()
