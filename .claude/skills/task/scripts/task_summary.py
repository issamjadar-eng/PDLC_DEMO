#!/usr/bin/env python3
"""task_summary.py — derive the project activity summary the console Tasks
tab renders. Owned by the `task` skill; run via `/task summary`.

Walks every person folder under tasks/ (excluding _-prefixed sandboxes),
parses each task doc's header (id, title, status, priority, created), dated
changelog entries (bullet `- YYYY-MM-DD: …` and table `| YYYY-MM-DD | … |`
forms), and the `## Economics` block, plus the person's 000-index.md Summary
column (the curated one-liners). Emits tasks/task-summary.json:

  generated / window_days
  narrative / watch      — Claude-composed prose (passed via --narrative /
                           --watch; the script never writes prose and
                           preserves the previous values when omitted)
  counts                 — by status, total
  open_tasks             — every non-Complete task: id, title, status
                           (ALWAYS a canonical key: In Progress / Blocked /
                           Not Started — decorations go to status_note,
                           clamped), priority, category, summary (from the
                           index), age_days, doc path
  categories             — category -> open-task count
  category_icons         — category -> icon (from config; console fallback 📌)
  recent                 — last-N-days window: tasks touched, created, closed,
                           highlights (closure/shipped changelog rows)
  economics              — modeled by-hand hours (min/max) + self-reported
                           agentic supervised hours from in-doc Economics
                           blocks; evidence classes labeled, never conflated

Categories are keyword-mapped (first match wins, against title + summary,
lowercased). The defaults below are generic; a project tunes them WITHOUT
touching this skill by writing `tasks/task-summary-config.json`:

  {"categories": [{"name": "...", "icon": "🛠", "keywords": ["...", ...]}, ...]}

(JSON, not YAML — this script must stay stdlib-only so `/task summary` runs
on bare python3 with no venv.)

Deterministic given the tree + today's date.

Usage:
  python3 task_summary.py [--root R] [--window 30]
                          [--narrative "text"] [--watch "text"] [--print]
"""
from __future__ import annotations

import argparse
import datetime
import json
import re
import sys
from pathlib import Path

# Generic defaults — first match wins. Override per-project via
# tasks/task-summary-config.json (see module docstring); never edit these
# with project-specific vocabulary (registry-shared skill).
DEFAULT_CATEGORIES = [
    {"name": "Console & Tooling", "icon": "🛠",
     "keywords": ["console", "tab", "dashboard", "mcp", "tooling", "metrics",
                  "file-locator", "tracker", "statusline", "status line"]},
    {"name": "Skills & Framework", "icon": "🧱",
     "keywords": ["skill", "agent", "advisor", "rule", "hook", "sync",
                  "registry", "framework", "grounding", "workflow"]},
    {"name": "Docs & Strategy", "icon": "🧭",
     "keywords": ["strategy", "strategies", "doc", "readme", "article",
                  "whitepaper", "deck", "glossary", "changelog", "narrative"]},
    {"name": "Regulatory & Submission", "icon": "📋",
     "keywords": ["regulatory", "submission", "510(k)", "510k", "q-sub", "qsub",
                  "pccp", "fda", "predicate", "guidance", "standard", "sop",
                  "qms", "reference", "citation"]},
    {"name": "Design Controls & Risk", "icon": "🧪",
     "keywords": ["risk", "hazard", "fmea", "trace", "requirement", "srs",
                  "sad", "v&v", "verification", "validation", "dhf",
                  "architecture", "design input"]},
]
FALLBACK_ICON = "📌"


def load_categories(root: Path) -> list[dict]:
    cfg = root / "tasks" / "task-summary-config.json"
    if cfg.is_file():
        try:
            cats = json.loads(cfg.read_text(encoding="utf-8")).get("categories")
            if isinstance(cats, list) and cats:
                return cats
        except (OSError, json.JSONDecodeError) as e:
            print(f"[task summary] warning: {cfg.name} unreadable ({e}); "
                  "using default categories", file=sys.stderr)
    return DEFAULT_CATEGORIES


def categorize(cats: list[dict], text: str) -> str:
    low = text.lower()
    for c in cats:
        if any(k in low for k in c.get("keywords", [])):
            return c["name"]
    return "Other"


def find_repo_root(start: Path) -> Path | None:
    for cand in (start.resolve(), *start.resolve().parents):
        if (cand / "project.yml").is_file():
            return cand
    return None


_H = {
    "title": re.compile(r"^#\s+\d+\s+—\s+(.+)$", re.M),
    "status": re.compile(r"^\*\*Status\*\*:\s*(.+)$", re.M),
    "priority": re.compile(r"^\*\*Priority\*\*:\s*(.+)$", re.M),
    "created": re.compile(r"^\*\*Created\*\*:\s*(\d{4}-\d{2}-\d{2})", re.M),
}
# Dated changelog entries come in two shapes across projects/eras:
#   bullet: - 2026-07-14: message            (this project's convention)
#   table:  | 2026-07-14 | message |         (table-changelog projects)
_CHANGELOG_BULLET = re.compile(r"^\s*-\s*(\d{4}-\d{2}-\d{2}):\s*(.+?)\s*$", re.M)
_CHANGELOG_ROW = re.compile(r"^\|\s*(\d{4}-\d{2}-\d{2})\s*\|\s*(.+?)\s*\|\s*$", re.M)
_ECON = re.compile(r'"economics":\s*{', re.S)


def changelog_entries(text: str) -> list[tuple[str, str]]:
    return _CHANGELOG_BULLET.findall(text) + _CHANGELOG_ROW.findall(text)


def parse_index_summaries(person_dir: Path) -> dict[str, str]:
    """Task NNN -> curated Summary cell from the person's 000-index.md."""
    out: dict[str, str] = {}
    idx = person_dir / "000-index.md"
    if not idx.is_file():
        return out
    for line in idx.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if cells and re.match(r"^\d{3}$", cells[0]):
            out[cells[0]] = cells[-1]
    return out


def parse_econ(text: str) -> dict | None:
    m = _ECON.search(text)
    if not m:
        return None
    depth = 0
    start = m.end() - 1
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(text[start:i + 1])
                except json.JSONDecodeError:
                    return None
    return None


def build(root: Path, window_days: int, narrative: str | None) -> dict:
    today = datetime.date.today()
    cutoff = today - datetime.timedelta(days=window_days)
    tasks_root = root / "tasks"
    cats = load_categories(root)

    counts: dict[str, int] = {}
    open_tasks: list[dict] = []
    categories: dict[str, int] = {}
    touched: set[str] = set()
    created_in_window = 0
    closed_in_window = 0
    highlights: list[dict] = []
    econ = {"manual_min": 0.0, "manual_max": 0.0,
            "agentic_min": 0.0, "agentic_max": 0.0, "tasks_with_economics": 0}

    for person_dir in sorted(p for p in tasks_root.iterdir()
                             if p.is_dir() and not p.name.startswith("_")):
        summaries = parse_index_summaries(person_dir)
        for f in sorted(person_dir.glob("[0-9][0-9][0-9]-*.md")):
            if f.name.startswith("000-"):
                continue
            try:
                text = f.read_text(encoding="utf-8")
            except OSError:
                continue
            nnn = f.name[:3]
            tid = f"{person_dir.name}/{nnn}"
            title_m = _H["title"].search(text)
            title = title_m.group(1).strip() if title_m else f.stem[4:].replace("-", " ")
            status_m = _H["status"].search(text)
            if status_m:
                status = status_m.group(1).strip()
            else:
                fm = re.search(r"^status:\s*(.+)$", text[:400], re.M)
                status = fm.group(1).strip() if fm else "Unknown"
            low = status.lower()
            # Decorated status lines ("✅ Complete (date) — …") classify on the
            # leading clause, not a strict prefix.
            head_clause = low.split("—")[0]
            if "complete" in head_clause or "✅" in status:
                status_key = "Complete"
            elif "progress" in head_clause:
                status_key = "In Progress"
            elif "block" in head_clause:
                status_key = "Blocked"
            elif "abandon" in head_clause or "supersed" in head_clause or "stale" in head_clause:
                status_key = "Abandoned"
            else:
                status_key = "Not Started"
            counts[status_key] = counts.get(status_key, 0) + 1
            prio_m = _H["priority"].search(text)
            created_m = _H["created"].search(text)
            summary = summaries.get(nnn, "")
            cat = categorize(cats, title + " " + summary)

            rows = changelog_entries(text)
            row_dates = [datetime.date.fromisoformat(d) for d, _ in rows] if rows else []
            last_activity = max(row_dates) if row_dates else None

            if created_m and datetime.date.fromisoformat(created_m.group(1)) >= cutoff:
                created_in_window += 1
            if last_activity and last_activity >= cutoff:
                touched.add(tid)
            if status_key == "Complete" and last_activity and last_activity >= cutoff:
                closed_in_window += 1
                # Newest in-window closure/shipped row as the highlight line.
                in_window = [(d, m) for d, m in rows
                             if datetime.date.fromisoformat(d) >= cutoff]
                in_window.sort(key=lambda r: r[0], reverse=True)
                for d, msg in in_window:
                    if re.search(r"shipped|closed|pushed|merged|complete|landed", msg, re.I):
                        line = re.sub(r"\*\*", "", msg).strip()
                        if len(line) < 40 and len(in_window) > 1:
                            # stub row — fall back to the longest in-window row
                            line = max((re.sub(r"\*\*", "", m).strip() for _, m in in_window),
                                       key=len)
                        highlights.append({
                            "task": tid, "title": title, "date": d, "category": cat,
                            "path": f.relative_to(root).as_posix(),
                            "line": (line[:220] + "…") if len(line) > 220 else line,
                        })
                        break

            if status_key in ("In Progress", "Blocked", "Not Started"):
                age = ((today - datetime.date.fromisoformat(created_m.group(1))).days
                       if created_m else None)
                # CONTRACT: `status` is ALWAYS one of the canonical keys — never
                # the raw doc line. Authors decorate status lines freely
                # ("Not Started — captured during …", "Active (awaiting X)"),
                # and a raw pass-through blew up the console's status chip
                # (one giant nowrap pill). The decoration survives in
                # `status_note`, clamped to a rendering-safe length.
                note = ""
                if "—" in status:
                    note = status.split("—", 1)[1].strip()
                elif "(" in status:
                    pm = re.search(r"\((.*?)\)\s*$", status)
                    note = pm.group(1).strip() if pm else ""
                open_tasks.append({
                    "id": tid, "title": title, "status": status_key,
                    "status_note": (note[:140] + "…") if len(note) > 140 else note,
                    "priority": (prio_m.group(1).strip() if prio_m else "—"),
                    "category": cat, "summary": summary, "age_days": age,
                    "path": f.relative_to(root).as_posix(),
                    "last_activity": last_activity.isoformat() if last_activity else None,
                })
                categories[cat] = categories.get(cat, 0) + 1

            ee = parse_econ(text)
            if isinstance(ee, dict):
                todos = ee.get("todos") or []
                if todos:
                    econ["tasks_with_economics"] += 1
                    for td in todos:
                        mh = td.get("manual_hours") or {}
                        econ["manual_min"] += float(mh.get("min") or 0)
                        econ["manual_max"] += float(mh.get("max") or 0)
                ah = ee.get("agentic_hours")
                if isinstance(ah, dict):
                    econ["agentic_min"] += float(ah.get("min") or 0)
                    econ["agentic_max"] += float(ah.get("max") or 0)

    highlights.sort(key=lambda h: (h["date"], h["task"]), reverse=True)
    open_tasks.sort(key=lambda t: (t["status"].lower().find("progress") < 0, t["id"]))

    return {
        "generated": today.isoformat(),
        "window_days": window_days,
        "narrative": narrative,
        "counts": {**counts, "total": sum(counts.values())},
        "open_tasks": open_tasks,
        "categories": dict(sorted(categories.items(), key=lambda kv: -kv[1])),
        "category_icons": {**{c["name"]: c.get("icon", FALLBACK_ICON) for c in cats},
                           "Other": FALLBACK_ICON},
        "recent": {
            "since": cutoff.isoformat(),
            "tasks_touched": len(touched),
            "created": created_in_window,
            "closed": closed_in_window,
            "highlights": highlights[:12],
        },
        "economics": {
            **{k: round(v, 1) for k, v in econ.items() if isinstance(v, float)},
            "tasks_with_economics": econ["tasks_with_economics"],
            "note": ("manual hours are MODELED (retrospective rubric estimates, "
                     "order-of-magnitude — lead with min); agentic hours are "
                     "self-reported supervised attention; sums cover only task "
                     "docs carrying an in-doc Economics block"),
        },
    }


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root")
    ap.add_argument("--window", type=int, default=30)
    ap.add_argument("--watch", default=None,
                    help="One-line 'the thing to watch' callout (Claude-composed). "
                         "Preserved from the previous file when omitted.")
    ap.add_argument("--narrative", default=None,
                    help="Claude-composed month-in-review prose (2-4 sentences). "
                         "Without it the previous narrative is preserved if present.")
    ap.add_argument("--print", action="store_true", dest="do_print")
    args = ap.parse_args(argv)

    root = Path(args.root).resolve() if args.root else find_repo_root(Path.cwd())
    if root is None:
        print("error: no project.yml found", file=sys.stderr)
        return 1

    out_path = root / "tasks" / "task-summary.json"
    narrative, watch = args.narrative, args.watch
    if (narrative is None or watch is None) and out_path.is_file():
        try:
            prev = json.loads(out_path.read_text(encoding="utf-8"))
            narrative = prev.get("narrative") if narrative is None else narrative
            watch = prev.get("watch") if watch is None else watch
        except (OSError, json.JSONDecodeError):
            pass

    data = build(root, args.window, narrative)
    data["watch"] = watch
    out_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8")
    print(f"[task summary] wrote {out_path.relative_to(root)} — "
          f"{data['counts'].get('total', 0)} tasks, {len(data['open_tasks'])} open, "
          f"{data['recent']['closed']} closed in last {args.window}d"
          + (" (narrative present)" if data["narrative"]
             else " (narrative EMPTY — compose one and re-run with --narrative)"))
    if args.do_print:
        print(json.dumps(data, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
