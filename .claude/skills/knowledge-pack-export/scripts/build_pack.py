#!/usr/bin/env python3
"""
build_pack.py — deterministic assembly engine for the knowledge-pack-export skill.

A "knowledge pack" is the portable bundle an external LLM-assistant platform ingests:
a small set of knowledge files + a system-instructions file + a provenance manifest.
This script owns the *deterministic* half of the hybrid build (verbatim concatenation,
provenance stamping, target-cap enforcement). The *LLM* half — condensing an
overflowing slot and authoring the persona text — is orchestrated by SKILL.md and
runs between `assemble` and `finalize`.

Subcommands
-----------
  validate <manifest>             Dry run: slot count vs target cap, per-slot source
                                  count + bytes, missing sources, condense slots. No writes.
  assemble <manifest>             Deterministic pass: write verbatim slots to <out>/,
                                  write condense slots' raw concatenation to <out>/_staging/,
                                  emit manifest.json + a system-instructions.md skeleton.
  finalize <manifest>            After the LLM has written condensed bundles into <out>/,
                                  re-check the pack (count, sizes, all files present),
                                  flip condense slots to status=done, rewrite manifest.json.

Options
-------
  --target KEY   Target platform key from references/targets.yml (default: manifest's first).
  --out DIR      Output dir (default: tools/knowledge-packs/<pack-slug>/pack relative to repo root).
  --repo DIR     Repo root (default: auto-detected via `git rev-parse --show-toplevel`).

The script is project-agnostic: every project-specific value (which docs, which target,
confidentiality text, persona) comes from the manifest YAML, never from this file.
"""

import argparse
import datetime
import glob
import json
import os
import re
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit(
        "ERROR: PyYAML is required (import yaml failed).\n"
        "Install with: pip install pyyaml   (or: python3 -m pip install pyyaml)"
    )

SKILL_DIR = Path(__file__).resolve().parent.parent
DEFAULT_TARGETS = SKILL_DIR / "references" / "targets.yml"


# ─────────────────────────────── helpers ───────────────────────────────

def repo_root(explicit=None):
    if explicit:
        return Path(explicit).resolve()
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"], stderr=subprocess.DEVNULL
        )
        return Path(out.decode().strip())
    except Exception:
        return Path.cwd()


def git_sha(root):
    try:
        out = subprocess.check_output(
            ["git", "-C", str(root), "rev-parse", "HEAD"], stderr=subprocess.DEVNULL
        )
        return out.decode().strip()
    except Exception:
        return "UNKNOWN"


def today():
    return datetime.date.today().isoformat()


def load_yaml(path):
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def load_targets(targets_path):
    if not Path(targets_path).exists():
        sys.exit(f"ERROR: targets registry not found at {targets_path}")
    data = load_yaml(targets_path)
    return {t["key"]: t for t in data.get("targets", [])}


def resolve_target(manifest, targets, cli_target):
    pack = manifest["pack"]
    declared = pack.get("targets") or []
    key = cli_target or (declared[0] if declared else None)
    if not key:
        sys.exit("ERROR: no target specified and manifest declares no pack.targets[].")
    if key not in targets:
        sys.exit(
            f"ERROR: unknown target '{key}'. Valid keys: {', '.join(sorted(targets))}"
        )
    return key, targets[key]


def expand_sources(root, patterns):
    """Expand repo-relative globs into a sorted, de-duplicated list of existing files."""
    seen = []
    missing = []
    for pat in patterns:
        matches = sorted(glob.glob(str(root / pat), recursive=True))
        files = [m for m in matches if os.path.isfile(m)]
        if not files:
            missing.append(pat)
        for m in files:
            rel = os.path.relpath(m, root)
            if rel not in seen:
                seen.append(rel)
    return seen, missing


def default_out(root, slug):
    return root / "tools" / "knowledge-packs" / slug / "pack"


def banner(pack, slot, sha, mode_label, sources):
    src_lines = "\n".join(f"#   - {s}" for s in sources)
    return (
        "<!-- ════════════════════════════════════════════════════════════\n"
        f"  KNOWLEDGE PACK BUNDLE — {pack.get('title', pack.get('slug'))}\n"
        "  ⚠ EXPORTED SNAPSHOT — not the canonical repository source. Repo agents/tools:\n"
        "    do not treat as authoritative or edit; use each section's `Source:` path.\n"
        f"  Slot: {slot['file']} — {slot.get('title', '')}\n"
        f"  CONFIDENTIALITY: {pack.get('confidentiality', 'Unspecified')}\n"
        f"  Built from commit {sha} on {today()}\n"
        f"  Mode: {mode_label}\n"
        "  Sources:\n"
        f"{src_lines}\n"
        "  ════════════════════════════════════════════════════════════ -->\n\n"
    )


RULE = "─" * 72


def extract_outline(root, rel):
    """Deterministic outline of a source doc: (title, [h2 headings]).
    Title = first markdown H1, else the filename stem. Headings = the `##` lines.
    Skips a leading YAML frontmatter block (--- ... ---) so its `# --- Identity ---`
    comment lines are never mistaken for the document title/headings."""
    title = None
    h2 = []
    try:
        lines = (root / rel).read_text(encoding="utf-8", errors="replace").splitlines()
        i = 0
        # skip leading YAML frontmatter delimited by --- on the first line
        if lines and lines[0].strip() == "---":
            for j in range(1, len(lines)):
                if lines[j].strip() == "---":
                    i = j + 1
                    break
        for ln in lines[i:]:
            s = ln.strip()
            if title is None and s.startswith("# ") and not s.startswith("## "):
                title = s[2:].strip()
            elif s.startswith("## ") and not s.startswith("### "):
                h2.append(s[3:].strip())
    except Exception:
        pass
    if not title:
        title = os.path.splitext(os.path.basename(rel))[0]
    return title, h2


def concat_verbatim(root, sources, sha):
    """Join sources verbatim with VISIBLE, greppable segment markers between documents.
    Agents segment a bundle by splitting on lines matching `^\\*\\*▌DOCUMENT \\d+ of \\d+`.
    The HTML `<!-- source: ... -->` marker is kept for machine provenance."""
    parts = []
    n = len(sources)
    for i, rel in enumerate(sources, 1):
        title, _ = extract_outline(root, rel)
        body = (root / rel).read_text(encoding="utf-8", errors="replace")
        seg = (
            f"{RULE}\n"
            f"**▌DOCUMENT {i} of {n} — {title}**  \n"
            f"Source: `{rel}` @ `{sha[:7]}`\n"
            f"{RULE}\n\n"
            f"<!-- source: {rel} @ {sha} -->\n\n"
            f"{body.rstrip()}\n"
        )
        parts.append(seg)
    return "\n\n".join(parts)


def bundle_preamble(pack, slot, sources, root, sha, idx, total, derived=False):
    """Generated-navigation header placed at the top of each bundle (visible markdown).
    Lets a human reviewer and a reading agent see, at a glance, what the bundle holds
    and how it is segmented. Fully deterministic."""
    title = slot.get("title", slot["file"])
    nn = slot["file"].split("-", 1)[0]
    lines = [
        f"# {nn} · {title}",
        "",
        "> ⚠️ **EXPORTED SNAPSHOT — not the canonical repository source.** "
        "If you are an agent or tool operating on the source repository, do **not** treat "
        "this file as authoritative and do **not** edit it — open each document's "
        "`Source:` path for the canonical version. (If you are the external assistant this "
        "pack was built for, this is your knowledge base — but it is a point-in-time "
        "snapshot that may lag the live source.)",
        ">",
        f"> **Knowledge pack:** {pack.get('title', pack.get('slug'))} · bundle **{idx} of {total}**  ",
        f"> **Confidentiality:** {pack.get('confidentiality', 'Unspecified')}  ",
        f"> **Built:** `{sha[:7]}` · {today()} · _{'derived (summarized)' if derived else 'verbatim'}_  ",
        ">",
        "> _Generated navigation. The source document(s) begin below the "
        "`BUNDLED DOCUMENTS` line; each is delimited by a `▌DOCUMENT k of N` marker._",
        "",
    ]
    if derived:
        lines += [
            f"**This bundle is a DERIVED summary** condensed from {len(sources)} source "
            "document(s) — treat it as a summary, not source-of-truth. Sources:",
            "",
        ]
        for rel in sources:
            lines.append(f"- `{rel}`")
        lines += ["", f"{RULE}", "═══ BUNDLED CONTENT (derived summary below) ═══", f"{RULE}"]
        return "\n".join(lines) + "\n\n"

    lines += [
        f"**This bundle contains {len(sources)} source document(s)**, each preserved "
        "verbatim and delimited by a `▌DOCUMENT k of N` marker so a reader (human or "
        "agent) can segment them into independent documents.",
        "",
        "| # | Document | Source | Key sections |",
        "|---|----------|--------|--------------|",
    ]
    for i, rel in enumerate(sources, 1):
        dtitle, h2 = extract_outline(root, rel)
        secs = "; ".join(h2[:5]) + (" …" if len(h2) > 5 else "")
        secs = secs.replace("|", "\\|") or "—"
        dtitle = dtitle.replace("|", "\\|")
        lines.append(f"| {i} | {dtitle} | `{rel}` | {secs} |")
    lines += ["", f"{RULE}", "═══ BUNDLED DOCUMENTS (verbatim below) ═══", f"{RULE}"]
    return "\n".join(lines) + "\n\n"


# ─────────────────────────────── actions ───────────────────────────────

IMG_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")


def count_image_refs(root, sources):
    """Count markdown image references across a slot's sources. Images do NOT travel
    into a text knowledge pack (the platform ingests markdown text, and relative
    `images/...` links break), so the build surfaces the count as a caveat."""
    n = 0
    for rel in sources:
        try:
            n += len(IMG_RE.findall((root / rel).read_text(encoding="utf-8", errors="replace")))
        except Exception:
            pass
    return n


def do_validate(manifest, targets, root, cli_target):
    pack = manifest["pack"]
    key, target = resolve_target(manifest, targets, cli_target)
    slots = manifest.get("slots", [])
    max_files = target.get("max_files")
    print(f"Pack:    {pack.get('slug')}  ({pack.get('title', '')})")
    print(f"Target:  {key}  (max_files={max_files})")
    print(f"Slots:   {len(slots)}")
    over = max_files is not None and len(slots) > max_files
    if over:
        print(f"  ✗ OVERFLOW: {len(slots)} slots > {max_files} file cap for '{key}'")
    else:
        print(f"  ✓ within file cap")
    print("-" * 64)
    total = 0
    problems = 0
    img_total = 0
    for slot in slots:
        srcs, missing = expand_sources(root, slot.get("sources", []))
        size = sum((root / s).stat().st_size for s in srcs)
        total += size
        imgs = count_image_refs(root, srcs)
        img_total += imgs
        mode = slot.get("mode", "verbatim")
        flag = " [condense]" if mode == "condense" else ""
        imgflag = f"  🖼 {imgs} img-refs" if imgs else ""
        print(f"  {slot['file']:<34} {len(srcs):>3} src  {size//1024:>5} KB{flag}{imgflag}")
        for pat in missing:
            problems += 1
            print(f"      ✗ pattern matched no files: {pat}")
    print("-" * 64)
    print(f"  total raw knowledge: {total//1024} KB across {len(slots)} slots")
    if img_total:
        print(f"  ⚠ {img_total} image reference(s) across the pack — images do NOT travel into a "
              f"text knowledge pack; relative `images/...` links will not resolve in the assistant.")
    if over or problems:
        print(f"\nRESULT: {'OVERFLOW; ' if over else ''}{problems} missing-source problem(s).")
        return 1
    print("\nRESULT: ok — ready to assemble.")
    return 0


def do_assemble(manifest, targets, root, cli_target, out):
    pack = manifest["pack"]
    key, target = resolve_target(manifest, targets, cli_target)
    slots = manifest.get("slots", [])
    max_files = target.get("max_files")
    if max_files is not None and len(slots) > max_files:
        sys.exit(
            f"ERROR: {len(slots)} slots exceeds the {max_files}-file cap for target "
            f"'{key}'. Merge slots or split into multiple packs before assembling."
        )
    sha = git_sha(root)
    out.mkdir(parents=True, exist_ok=True)
    staging = out / "_staging"
    record = {
        "pack": pack.get("slug"),
        "title": pack.get("title"),
        "target": key,
        "built_commit": sha,
        "built_date": today(),
        "confidentiality": pack.get("confidentiality"),
        "slots": [],
    }
    total = len(slots)
    for idx, slot in enumerate(slots, 1):
        srcs, missing = expand_sources(root, slot.get("sources", []))
        mode = slot.get("mode", "verbatim")
        slot_rec = {
            "file": slot["file"],
            "title": slot.get("title"),
            "mode": "verbatim" if mode == "verbatim" else "derived",
            "sources": srcs,
            "missing_patterns": missing,
        }
        if mode == "verbatim":
            content = (banner(pack, slot, sha, "verbatim", srcs)
                       + bundle_preamble(pack, slot, srcs, root, sha, idx, total)
                       + concat_verbatim(root, srcs, sha))
            (out / slot["file"]).write_text(content, encoding="utf-8")
            slot_rec["status"] = "done"
            slot_rec["bytes"] = (out / slot["file"]).stat().st_size
        else:
            staging.mkdir(parents=True, exist_ok=True)
            raw = (banner(pack, slot, sha, "raw (pre-condense)", srcs)
                   + bundle_preamble(pack, slot, srcs, root, sha, idx, total, derived=True)
                   + concat_verbatim(root, srcs, sha))
            raw_path = staging / (slot["file"] + ".raw")
            raw_path.write_text(raw, encoding="utf-8")
            slot_rec["status"] = "pending-condense"
            slot_rec["staging_raw"] = os.path.relpath(raw_path, out)
            slot_rec["condense_brief"] = slot.get("condense_brief", "")
        record["slots"].append(slot_rec)

    (out / "manifest.json").write_text(json.dumps(record, indent=2), encoding="utf-8")
    write_system_instructions(pack, out, sha, record["slots"])

    pending = [s for s in record["slots"] if s["status"] == "pending-condense"]
    print(f"Assembled {len(slots)} slots → {out}")
    print(f"  verbatim: {len(slots) - len(pending)}   pending-condense: {len(pending)}")
    if pending:
        print("\nNext (LLM step — orchestrated by SKILL.md):")
        for s in pending:
            print(f"  • condense {s['staging_raw']}  →  {s['file']}")
            print(f"      brief: {s['condense_brief']}")
        print("\nThen run:  build_pack.py finalize <manifest> --out", out)
    else:
        print("No condense slots — run finalize to verify the pack.")
    return 0


def write_system_instructions(pack, out, sha, slot_records=None):
    persona = pack.get("persona", "").strip()
    conf = pack.get("confidentiality", "")
    audience = pack.get("audience", "")
    body = [
        f"# System Instructions — {pack.get('title', pack.get('slug'))}",
        "",
        f"> **CONFIDENTIALITY:** {conf}",
        f"> **Audience:** {audience}" if audience else "",
        f"> _Generated from commit `{sha}` on {today()} by knowledge-pack-export._",
        "",
        "**Always consult the attached knowledge files before answering.** "
        "Ground every answer in their content and name the source bundle you used. "
        "If the files do not cover the question, say so plainly rather than guessing.",
        "",
        "## Role",
        "",
        persona or "<!-- TODO: persona — describe the assistant's role, scope, and tone. -->",
        "",
        "## Guardrails",
        "",
        "- This pack carries controlled material. Treat it as confidential — never imply "
        "the content is public, and do not reproduce it outside this approved assistant.",
        "- Do not invent regulatory facts, citations, dates, or identifiers. Quote the "
        "attached files.",
        "- When content is summarized/derived (see manifest), flag that it is a summary, "
        "not source-of-truth.",
    ]
    body += _pack_map_section(slot_records or [])
    text = "\n".join(line for line in body if line is not None)
    (out / "system-instructions.md").write_text(text + "\n", encoding="utf-8")


def _pack_map_section(slot_records):
    """The 'agent guide' — how the pack is organized + how to read/segment/cite it.
    Lives in the system prompt (does NOT cost a knowledge-file slot)."""
    out = [
        "",
        "## How this pack is organized (read first)",
        "",
        "Each attached knowledge file is a **bundle** that may combine several source "
        "documents, preserved verbatim. To use the pack well:",
        "",
        "1. **Find the right bundle** from the map below.",
        "2. **Segment within a bundle:** each bundle opens with a generated navigation "
        "preamble (its title, a table of the documents it contains, and their key "
        "sections). The verbatim documents follow the `BUNDLED DOCUMENTS` line, each "
        "delimited by a line of the form `▌DOCUMENT k of N — <title>`. Treat the text "
        "between two such markers (or to end-of-file) as one independent document.",
        "3. **Cite precisely:** every segment carries a `Source:` line with the document's "
        "repository path — name that path (and the bundle) when you answer.",
        "4. A bundle marked **derived** in its preamble is a summary, not source-of-truth — "
        "say so when you rely on it.",
        "",
        "### Bundle map",
        "",
        "| File | Bundle | Documents inside |",
        "|------|--------|------------------|",
    ]
    for s in slot_records:
        docs = "; ".join(os.path.basename(x) for x in s.get("sources", [])) or "—"
        mode = " _(derived)_" if s.get("mode") == "derived" else ""
        out.append(f"| `{s['file']}` | {s.get('title', '')}{mode} | {docs} |")
    return out


def do_finalize(manifest, targets, root, cli_target, out):
    key, target = resolve_target(manifest, targets, cli_target)
    max_files = target.get("max_files")
    mpath = out / "manifest.json"
    if not mpath.exists():
        sys.exit(f"ERROR: {mpath} not found — run `assemble` first.")
    record = json.loads(mpath.read_text(encoding="utf-8"))

    bundle_files = [s["file"] for s in record["slots"]]
    if max_files is not None and len(bundle_files) > max_files:
        sys.exit(f"ERROR: {len(bundle_files)} bundles exceeds cap {max_files} for '{key}'.")

    problems = 0
    for s in record["slots"]:
        fpath = out / s["file"]
        if not fpath.exists():
            problems += 1
            print(f"  ✗ missing bundle file: {s['file']} (condense step not completed?)")
            continue
        s["bytes"] = fpath.stat().st_size
        if s.get("status") == "pending-condense":
            s["status"] = "done"
    record["finalized_date"] = today()
    mpath.write_text(json.dumps(record, indent=2), encoding="utf-8")

    if problems:
        print(f"\nRESULT: {problems} problem(s) — pack not ready.")
        return 1
    total = sum(s.get("bytes", 0) for s in record["slots"])
    print(f"Finalized pack at {out}")
    print(f"  {len(bundle_files)} bundle files / cap {max_files}   total {total//1024} KB")
    print(f"  + system-instructions.md + manifest.json")
    print("\nRESULT: ready to upload / publish.")
    return 0


# ─────────────────────────────── cli ───────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="Deterministic assembly engine for knowledge packs.")
    ap.add_argument("action", choices=["validate", "assemble", "finalize"])
    ap.add_argument("manifest", help="path to <pack-slug>.pack.yml")
    ap.add_argument("--target", help="target platform key (default: manifest's first)")
    ap.add_argument("--out", help="output dir (default: tools/knowledge-packs/<slug>/pack)")
    ap.add_argument("--repo", help="repo root (default: git toplevel)")
    ap.add_argument("--targets", default=str(DEFAULT_TARGETS), help="targets registry yml")
    args = ap.parse_args()

    root = repo_root(args.repo)
    manifest = load_yaml(args.manifest)
    if not manifest or "pack" not in manifest:
        sys.exit("ERROR: manifest must have a top-level `pack:` block.")
    targets = load_targets(args.targets)
    out = Path(args.out).resolve() if args.out else default_out(root, manifest["pack"]["slug"])

    if args.action == "validate":
        rc = do_validate(manifest, targets, root, args.target)
    elif args.action == "assemble":
        rc = do_assemble(manifest, targets, root, args.target, out)
    else:
        rc = do_finalize(manifest, targets, root, args.target, out)
    sys.exit(rc)


if __name__ == "__main__":
    main()
