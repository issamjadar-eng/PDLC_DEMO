#!/usr/bin/env python3
"""
estar_extract_sectionmap.py — derive a machine-readable eSTAR section-map from
the FDA eSTAR template's XFA layer.

The FDA eSTAR PDF is a dynamic XFA form (not a plain AcroForm): every section,
attachment slot, and structured field lives in the XFA `template` packet (XML),
not in the AcroForm `/Fields` array. This script extracts that packet with
pikepdf and walks the subform/field tree to emit a version-pinned section-map
(sections -> subsections -> attachment slots + structured fields), plus a
human-readable outline.

Project-agnostic: reads a public FDA template binary, emits FDA-structure data.
Run under the project's eStar venv (tools/estar/.venv) — see the /submissions
skill's eStar setup action.

Usage:
  python estar_extract_sectionmap.py <template.pdf> --json OUT.json [--outline OUT.md]
"""
import argparse, json, sys
import xml.etree.ElementTree as ET

ATTACH_HINT = ("attachment", "attach")


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def extract_template_xml(pdf_path: str) -> bytes:
    import pikepdf
    pdf = pikepdf.open(pdf_path)
    root = pdf.Root
    if "/AcroForm" not in root or "/XFA" not in root.AcroForm:
        raise SystemExit(f"{pdf_path}: no XFA layer found (not an eSTAR-style dynamic form?)")
    xfa = list(root.AcroForm.XFA)
    for i in range(len(xfa) - 1):
        if str(xfa[i]) == "template":
            return bytes(xfa[i + 1].read_bytes())
    raise SystemExit("XFA present but no `template` packet found")


def _caption_text(el) -> str:
    """Best-effort human label: the field/subform caption <value><text>."""
    for cap in el:
        if _local(cap.tag) == "caption":
            for v in cap.iter():
                if _local(v.tag) == "text" and (v.text or "").strip():
                    return " ".join((v.text or "").split())
    return ""


def _field_kind(el) -> str:
    for ui in el:
        if _local(ui.tag) == "ui":
            for child in ui:
                return _local(child.tag)  # textEdit, choiceList, checkButton, imageEdit, button, ...
    return "?"


def parse_sectionmap(xml_bytes: bytes, template_id: str, version: str) -> dict:
    """Stream the XFA template; build sections = top-level subforms under root."""
    root_el = ET.fromstring(xml_bytes)
    # find the outermost <template><subform name="root"> ... </subform>
    def find_root_subform(node):
        for child in node:
            if _local(child.tag) == "subform":
                return child
        return None

    top = find_root_subform(root_el)
    if top is None:
        raise SystemExit("no top-level subform in XFA template")

    def walk_fields(node):
        out = []
        for ch in node:
            lt = _local(ch.tag)
            if lt in ("field", "exclGroup"):
                name = ch.get("name") or ""
                out.append({
                    "name": name,
                    "label": _caption_text(ch),
                    "kind": _field_kind(ch) if lt == "field" else "exclGroup",
                })
        return out

    def is_attach(name: str) -> bool:
        n = name.lower()
        return any(h in n for h in ATTACH_HINT)

    def build(node):
        name = node.get("name") or ""
        entry = {"name": name, "label": _caption_text(node),
                 "attachment_slot": is_attach(name),
                 "subsections": [], "fields": walk_fields(node)}
        for ch in node:
            if _local(ch.tag) == "subform" and (ch.get("name") or ""):
                entry["subsections"].append(build(ch))
        return entry

    sections = [build(ch) for ch in top
                if _local(ch.tag) == "subform" and (ch.get("name") or "")]

    def counts(nodes):
        s = a = f = 0
        for n in nodes:
            s += 1
            if n["attachment_slot"]:
                a += 1
            f += len(n["fields"])
            cs, ca, cf = counts(n["subsections"])
            s += cs; a += ca; f += cf
        return s, a, f

    tot_s, tot_a, tot_f = counts(sections)
    return {
        "schema_version": "1.0",
        "template_id": template_id,
        "template_version": version,
        "form_technology": "XFA-dynamic",
        "source": "derived from the FDA eSTAR template XFA `template` packet via pikepdf",
        "totals": {"subforms": tot_s, "attachment_slots": tot_a, "fields": tot_f},
        "sections": sections,
    }


def to_outline(m: dict) -> str:
    lines = [f"# eSTAR section-map outline — {m['template_id']} {m['template_version']}",
             "",
             f"_Form technology: {m['form_technology']}. "
             f"{m['totals']['subforms']} subforms · {m['totals']['attachment_slots']} attachment slots · "
             f"{m['totals']['fields']} structured fields. {m['source']}._", ""]

    def emit(node, depth):
        tag = " 📎" if node["attachment_slot"] else ""
        label = f" — {node['label']}" if node["label"] else ""
        lines.append(f"{'  ' * depth}- **{node['name']}**{tag}{label} "
                     f"({len(node['fields'])} fields)")
        for sub in node["subsections"]:
            emit(sub, depth + 1)

    for s in m["sections"]:
        emit(s, 0)
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("--template-id", default="nIVD_eSTAR")
    ap.add_argument("--version", default="v7.0")
    ap.add_argument("--json", required=True)
    ap.add_argument("--outline")
    a = ap.parse_args()

    xml_bytes = extract_template_xml(a.pdf)
    m = parse_sectionmap(xml_bytes, a.template_id, a.version)
    with open(a.json, "w") as fh:
        json.dump(m, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print(f"wrote {a.json}: {m['totals']['subforms']} subforms, "
          f"{m['totals']['attachment_slots']} attachment slots, "
          f"{m['totals']['fields']} fields")
    if a.outline:
        with open(a.outline, "w") as fh:
            fh.write(to_outline(m))
        print(f"wrote {a.outline}")


if __name__ == "__main__":
    main()
