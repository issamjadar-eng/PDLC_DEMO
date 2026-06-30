#!/usr/bin/env python3
"""usage-metrics · aggregate — roll up per-session token-usage records across
ALL teammates into a per-user report. Pure script, NO LLM. Owned by the
`usage-metrics` skill.

git-as-aggregator: every teammate commits their own
tasks/{task_folder}/_usage-metrics/YYYY-MM/<session>.json; once pulled, this
script walks tasks/*/_usage-metrics/ and sums by task_folder × month × model.
The folder IS the identity — no email join needed; name/email are pulled from
project.yml team.active[] only as display labels.

Output (per month): {output_dir}/YYYY-MM.md  +  YYYY-MM.json

Usage:
  aggregate.py [--month YYYY-MM] [--pull] [--project-root PATH] [--quiet]
    --month   restrict to one month (default: every month found)
    --pull    `git pull --ff-only` first (the daily routine uses this)
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

sys.dont_write_bytecode = True   # keep __pycache__ out of the skill/shared trees


def _find_shared_scripts() -> Path | None:
    """Locate .claude/skills/shared/scripts (robust to where this script lives)."""
    for base in (Path(__file__).resolve(), Path.cwd().resolve()):
        for anc in (base, *base.parents):
            cand = anc / ".claude" / "skills" / "shared" / "scripts"
            if cand.is_dir():
                return cand
    return None


_shared = _find_shared_scripts()
if _shared:
    sys.path.insert(0, str(_shared))
import resolve_user  # noqa: E402  (canonical roster parser + resolver)

TOKENS = ("input", "output", "cache_read", "cache_creation")
# Fields used only for cost (kept out of the display table).
COST_FIELDS = ("cache_write_5m", "cache_write_1h")


def load_pricing(project_root: Path) -> dict | None:
    """Load the rate card. Project-local copy wins (editable per project);
    falls back to the skill's bundled seed so a fresh install still prices."""
    candidates = [
        project_root / "tools" / "usage-metrics" / "pricing.json",   # project-local (editable)
        Path(__file__).resolve().parent.parent / "templates" / "pricing.json",  # skill seed
    ]
    for p in candidates:
        if p.is_file():
            try:
                return json.loads(p.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue
    return None


def _rates_for(model: str, pricing: dict) -> dict:
    models = pricing.get("models") or {}
    if model in models:
        return models[model]
    fams = pricing.get("families") or {}
    low = (model or "").lower()
    # First family key that appears as a substring of the model id.
    for fam, rates in fams.items():
        if fam in low:
            return rates
    return fams.get(pricing.get("default_family", "opus"), {})


COST_COMPONENTS = ("input", "cache_read", "cache_write_5m", "cache_write_1h", "output")


def effective_rates(all_plain: dict, pricing: dict | None) -> dict:
    """Token-weighted $/MTok per cost-component across the whole dataset.

    For a single model this equals that model's rates exactly; for a mix it
    blends by token share — used to price the daily series for projection.
    """
    if not pricing:
        return {c: 0.0 for c in COST_COMPONENTS}
    tok = {c: 0 for c in COST_COMPONENTS}
    cost = {c: 0.0 for c in COST_COMPONENTS}
    for month in all_plain.values():
        for rec in month.values():
            for model, s in rec.get("by_model", {}).items():
                r = _rates_for(model, pricing)
                for c in COST_COMPONENTS:
                    n = s.get(c, 0) or 0
                    tok[c] += n
                    cost[c] += n * r.get(c, 0) / 1_000_000
    return {c: (cost[c] / tok[c] * 1_000_000 if tok[c] else 0.0) for c in COST_COMPONENTS}


def daily_cost_series(all_plain: dict, eff: dict) -> dict:
    """{YYYY-MM-DD: $cost} summed across all members/months using effective rates."""
    dc: dict = defaultdict(float)
    for month in all_plain.values():
        for rec in month.values():
            for day, ds in rec.get("by_day", {}).items():
                dc[day] += sum((ds.get(c, 0) or 0) * eff[c] / 1_000_000 for c in COST_COMPONENTS)
    return {d: round(v, 2) for d, v in sorted(dc.items())}


def cost_of(by_model: dict, pricing: dict | None) -> float:
    """Estimated equivalent API cost (USD) from per-model token sums."""
    if not pricing:
        return 0.0
    total = 0.0
    for model, s in by_model.items():
        r = _rates_for(model, pricing)
        if not r:
            continue
        total += (
            s.get("input", 0) * r.get("input", 0)
            + s.get("output", 0) * r.get("output", 0)
            + s.get("cache_read", 0) * r.get("cache_read", 0)
            + s.get("cache_write_5m", 0) * r.get("cache_write_5m", 0)
            + s.get("cache_write_1h", 0) * r.get("cache_write_1h", 0)
        ) / 1_000_000
    return round(total, 2)


def find_project_root(start: Path) -> Path:
    p = start.resolve()
    for cand in (p, *p.parents):
        if (cand / "project.yml").is_file():
            return cand
    raise SystemExit("aggregate: could not locate project root (no project.yml)")


def read_cfg(project_yml: Path) -> dict:
    import re
    text = project_yml.read_text(encoding="utf-8")
    m = re.search(r"^usage_metrics:\s*$", text, re.MULTILINE)
    cfg = {"output_dir": None}
    if not m:
        return cfg
    block = text[m.end():]
    end = re.search(r"^\S", block, re.MULTILINE)
    if end:
        block = block[: end.start()]
    mm = re.search(r"^\s+output_dir:\s*([^\n#]+)", block, re.MULTILINE)
    if mm:
        cfg["output_dir"] = mm.group(1).strip()
    return cfg


def roster_labels(project_root: Path) -> dict[str, dict]:
    """task_folder -> {name, email} from project.yml (display labels only)."""
    txt = (project_root / "project.yml").read_text(encoding="utf-8")
    out = {}
    for e in resolve_user.parse_roster(txt):
        tf = e.get("task_folder")
        if tf:
            out[tf] = {"name": e.get("name", tf), "email": e.get("email", "")}
    return out


def collect_records(project_root: Path, month_filter: str | None):
    """Walk tasks/*/_usage-metrics/<month>/*.json.

    Returns nested: {month: {task_folder: {"totals": {...}, "by_model": {...},
    "sessions": int}}}.
    """
    from collections import defaultdict as _dd

    def _slot():
        return {
            "totals": _dd(int),
            "by_model": _dd(lambda: _dd(int)),
            "by_day": _dd(lambda: _dd(int)),
            "sessions": 0,
        }

    data: dict = defaultdict(lambda: defaultdict(_slot))

    def _task_slot():
        return {"by_model": _dd(lambda: _dd(int)), "totals": _dd(int), "sessions": 0}

    # Per-task rollup across all months/sessions (the value dimension). Keyed by
    # "<task_folder>/<task_id>" so it can later join to per-task economics
    # estimates that live under tasks/<person>/NNN-*.md.
    task_data: dict = defaultdict(_task_slot)

    def _merge(dst, src):
        for k, v in (src or {}).items():
            if isinstance(v, (int, float)):
                dst[k] += v

    tasks_dir = project_root / "tasks"
    for person_dir in sorted(tasks_dir.glob("*/_usage-metrics")):
        task_folder = person_dir.parent.name
        for month_dir in sorted(person_dir.iterdir()):
            if not month_dir.is_dir() or month_dir.name == "aggregate":
                continue
            month = month_dir.name
            if month_filter and month != month_filter:
                continue
            for jf in sorted(month_dir.glob("*.json")):
                try:
                    rec = json.loads(jf.read_text(encoding="utf-8"))
                except (json.JSONDecodeError, OSError):
                    continue
                slot = data[month][task_folder]
                slot["sessions"] += 1
                _merge(slot["totals"], rec.get("totals"))
                for model, ms in (rec.get("by_model") or {}).items():
                    _merge(slot["by_model"][model], ms)
                for day, ds in (rec.get("by_day") or {}).items():
                    _merge(slot["by_day"][day], ds)
                # Per-task: by_task = {task_id: {model: stats}} (incl. "_unattributed").
                for task_id, tmap in (rec.get("by_task") or {}).items():
                    tslot = task_data[f"{task_folder}/{task_id}"]
                    tslot["sessions"] += 1
                    for model, ms in (tmap or {}).items():
                        _merge(tslot["by_model"][model], ms)
                        _merge(tslot["totals"], ms)
    return data, task_data


def fmt(n: int) -> str:
    return f"{n:,}"


def tokM(n: int) -> str:
    """Token quantity normalized to millions (MTok), to match the $/MTok rates."""
    return f"{(n or 0) / 1e6:,.2f}M"


def render_markdown(month: str, per_person: dict, anon: dict, pricing: dict | None = None) -> str:
    rows = []
    grand = {t: 0 for t in TOKENS} | {"messages": 0, "sessions": 0}
    grand_cost = 0.0
    for tf in sorted(per_person, key=lambda k: per_person[k]["totals"]["input"]
                     + per_person[k]["totals"]["output"], reverse=True):
        slot = per_person[tf]
        tot = slot["totals"]
        name = anon.get(tf, tf)   # anonymized label — no real names in the team view
        cost = cost_of(slot["by_model"], pricing)
        grand_cost += cost
        total_in = tot["input"] + tot["cache_read"] + tot["cache_creation"]
        rows.append(
            f"| {name} | {slot['sessions']} | {tokM(tot['input'])} | "
            f"{tokM(tot['cache_read'])} | {tokM(tot['cache_creation'])} | {tokM(total_in)} | "
            f"{tokM(tot['output'])} | {fmt(tot['messages'])} | ${cost:,.2f} |"
        )
        for t in TOKENS:
            grand[t] += tot[t]
        grand["messages"] += tot["messages"]
        grand["sessions"] += slot["sessions"]
    grand_total_in = grand["input"] + grand["cache_read"] + grand["cache_creation"]

    lines = [
        f"# Token Usage — {month}",
        "",
        "_Generated by `tools/usage-metrics/aggregate.py` (no LLM). "
        "Source: per-session transcript records under `tasks/*/_usage-metrics/`. "
        "Non-canonical; not a controlled record._",
        "",
        "_**Total input** = uncached input + cache read + cache write (Anthropic's `input_tokens` "
        "is only the uncached sliver; with prompt caching, cache reads dominate input). "
        "Token quantities are in **millions (MTok)** to match the $/MTok rates._",
        "",
        "| Member | Sessions | Input (uncached) | Cache read | Cache write | Total input | Output | Messages | Est. cost |",
        "|--------|---------:|-----------------:|-----------:|------------:|------------:|-------:|---------:|----------:|",
        *rows,
        f"| **Total** | **{grand['sessions']}** | **{tokM(grand['input'])}** | "
        f"**{tokM(grand['cache_read'])}** | **{tokM(grand['cache_creation'])}** | "
        f"**{tokM(grand_total_in)}** | **{tokM(grand['output'])}** | "
        f"**{fmt(grand['messages'])}** | **${grand_cost:,.2f}** |",
        "",
        "_Est. cost = measured tokens × list prices in `pricing.json`; indicative API-equivalent "
        "value, not subscription billing. Verify rates against current Anthropic pricing._",
    ]
    return "\n".join(lines)


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Claude Code Token Usage</title>
<style>
  :root { --bg:#0f1115; --card:#181b22; --line:#2a2f3a; --txt:#e6e9ef; --mut:#8b93a7;
          --accent:#6ea8fe; --accent2:#7ee0c0; --bar:#3b82f6;
          --c-in:#6ea8fe; --c-cread:#4fc3a1; --c-cwrite:#9b8cff; --c-out:#f0a93b; --c-cost:#7ee0c0; }
  * { box-sizing:border-box; }
  body { margin:0; font:14px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
         background:var(--bg); color:var(--txt); padding:24px; }
  h1 { font-size:20px; margin:0 0 4px; }
  .note { color:var(--mut); font-size:12px; margin:0 0 18px; }
  .controls { display:flex; gap:12px; align-items:center; margin-bottom:18px; flex-wrap:wrap; }
  select { background:var(--card); color:var(--txt); border:1px solid var(--line);
           border-radius:8px; padding:6px 10px; font-size:13px; }
  .cards { display:flex; gap:12px; flex-wrap:wrap; margin-bottom:22px; }
  .card { background:var(--card); border:1px solid var(--line); border-radius:10px;
          padding:12px 16px; min-width:130px; }
  .card .k { color:var(--mut); font-size:11px; text-transform:uppercase; letter-spacing:.04em; }
  .card .v { font-size:20px; font-weight:600; margin-top:2px; }
  .panel { background:var(--card); border:1px solid var(--line); border-radius:10px;
           padding:16px; margin-bottom:22px; }
  .panel h2 { font-size:13px; color:var(--mut); margin:0 0 12px; text-transform:uppercase;
              letter-spacing:.04em; font-weight:600; }
  table { width:100%; border-collapse:collapse; }
  th,td { padding:8px 10px; text-align:right; border-bottom:1px solid var(--line); white-space:nowrap; }
  th:first-child,td:first-child { text-align:left; }
  th { color:var(--mut); font-weight:600; font-size:12px; cursor:pointer; user-select:none; }
  th:hover { color:var(--txt); }
  tbody tr:hover { background:rgba(110,168,254,.06); }
  tfoot td { font-weight:700; border-top:2px solid var(--line); border-bottom:none; }
  .mono { font-variant-numeric:tabular-nums; }
  .barrow { display:grid; grid-template-columns:160px 1fr 150px; gap:10px; align-items:center;
            margin-bottom:7px; }
  .barrow .lbl { color:var(--txt); font-size:13px; overflow:hidden; text-overflow:ellipsis; }
  .bartrack { background:#11141a; border-radius:6px; overflow:hidden; height:18px; display:flex; }
  .seg-in { background:var(--c-in); height:100%; }
  .seg-cread { background:var(--c-cread); height:100%; }
  .seg-cwrite { background:var(--c-cwrite); height:100%; }
  .seg-out { background:var(--c-out); height:100%; }
  .barval { color:var(--mut); font-size:12px; text-align:right; }
  .legend { display:flex; gap:16px; margin-bottom:12px; font-size:12px; color:var(--mut); }
  .legend span { display:inline-flex; align-items:center; gap:6px; }
  .swatch { width:11px; height:11px; border-radius:3px; display:inline-block; }
  .cost { color:var(--c-cost); }
  .disclaimer { color:var(--mut); font-size:11px; margin-top:10px; font-style:italic; }
  .ts { display:flex; align-items:flex-end; gap:4px; height:180px; padding-top:8px; overflow-x:auto; }
  .tscol { display:flex; flex-direction:column; align-items:center; justify-content:flex-end;
           min-width:30px; height:100%; }
  .tsbar-out { width:20px; background:var(--c-out); border-radius:4px 4px 0 0; }
  .tsbar-cwrite { width:20px; background:var(--c-cwrite); }
  .tsbar-cread { width:20px; background:var(--c-cread); }
  .tsbar-in { width:20px; background:var(--c-in); }
  .tscol:hover > div { filter:brightness(1.25); }
  .tslbl { font-size:10px; color:var(--mut); margin-top:5px; white-space:nowrap; }
  .tsbar-cost { width:20px; background:var(--c-cost); border-radius:4px 4px 0 0; min-height:1px; }
  .tsbar-proj { width:20px; background:var(--c-cost); opacity:.30; border-radius:4px 4px 0 0; min-height:1px; }
  .projstart { box-shadow:-2px 0 0 0 var(--mut); }
  code { color:var(--accent); }
</style>
</head>
<body>
  <h1>Claude Code — Token Usage</h1>
  <p class="note">Generated by <code>tools/usage-metrics/aggregate.py</code> (no LLM). Source: per-session
  transcript records under <code>tasks/*/_usage-metrics/</code>. Non-canonical; not a controlled record.
  Token quantities are shown in <strong>millions of tokens (MTok)</strong> to match the $/MTok rates.</p>
  <div class="controls">
    <label>Month <select id="month"></select></label>
  </div>
  <div class="cards" id="cards"></div>
  <div class="panel"><h2>30-day cost projection</h2>
    <div class="cards" id="projcards"></div>
    <div class="ts" id="costts"></div>
    <p class="disclaimer" id="projnote"></p>
  </div>
  <div class="panel"><h2>Daily token volume (stacked composition)</h2>
    <div class="legend">
      <span><i class="swatch" style="background:var(--c-in)"></i> Input (uncached)</span>
      <span><i class="swatch" style="background:var(--c-cread)"></i> Cache read</span>
      <span><i class="swatch" style="background:var(--c-cwrite)"></i> Cache write</span>
      <span><i class="swatch" style="background:var(--c-out)"></i> Output</span>
    </div>
    <div class="ts" id="timeseries"></div>
  </div>
  <div class="panel"><h2>Token composition by member (input ≫ output — most input is cache reads)</h2>
    <div class="legend">
      <span><i class="swatch" style="background:var(--c-in)"></i> Input (uncached)</span>
      <span><i class="swatch" style="background:var(--c-cread)"></i> Cache read</span>
      <span><i class="swatch" style="background:var(--c-cwrite)"></i> Cache write</span>
      <span><i class="swatch" style="background:var(--c-out)"></i> Output</span>
    </div>
    <div id="chart"></div>
  </div>
  <div class="panel"><h2>By model</h2>
    <table id="modeltbl">
      <thead><tr>
        <th>Model</th><th>Input (uncached)</th><th>Cache read</th><th>Cache write</th>
        <th>Total input</th><th>Output</th><th>Messages</th><th>Est. cost</th>
      </tr></thead>
      <tbody></tbody>
    </table>
  </div>
  <div class="panel"><h2>Detail (by member)</h2>
    <table id="tbl">
      <thead><tr>
        <th data-k="name">Member</th><th data-k="sessions">Sessions</th>
        <th data-k="input">Input (uncached)</th><th data-k="cache_read">Cache read</th>
        <th data-k="cache_creation">Cache write</th><th data-k="total_in">Total input</th>
        <th data-k="output">Output</th>
        <th data-k="messages">Messages</th><th data-k="cost">Est. cost</th>
      </tr></thead>
      <tbody></tbody><tfoot></tfoot>
    </table>
    <p class="disclaimer" id="costnote"></p>
  </div>
  <div class="panel"><h2>Rate card</h2>
    <p class="disclaimer" id="ratesrc"></p>
    <table id="ratetbl">
      <thead><tr>
        <th>Model</th><th>Input</th><th>Write</th><th>Cache read</th><th>Output</th>
      </tr></thead>
      <tbody></tbody>
    </table>
  </div>
<script>
const DATA = __USAGE_DATA__;
const COST_NOTE = __COST_NOTE__;
const DAILY_COST = __DAILY_COST__;
const RATE_CARD = __RATE_CARD__;
const TOK = ["input","output","cache_read","cache_creation"];
const fmt = n => (n||0).toLocaleString();
const usd = n => '$'+(n||0).toLocaleString(undefined,{minimumFractionDigits:2,maximumFractionDigits:2});
// Token quantities are shown normalized to MILLIONS of tokens (MTok) to match the
// $/MTok rate card. Counts (sessions/messages/members) stay whole numbers.
const tokM = n => (((n||0)/1e6).toLocaleString(undefined,{minimumFractionDigits:2,maximumFractionDigits:2}))+'M';
let sortKey = "total_in", sortDir = -1;

function months(){ return Object.keys(DATA).sort(); }

function rowsFor(sel){
  // merge members across selected month(s)
  const acc = {};
  const ms = sel === "all" ? months() : [sel];
  for(const m of ms){
    for(const [tf, rec] of Object.entries(DATA[m]||{})){
      if(!acc[tf]) acc[tf] = {name:rec.name||tf, tf, sessions:0,
                              input:0,output:0,cache_read:0,cache_creation:0,messages:0,cost:0};
      acc[tf].sessions += rec.sessions||0;
      acc[tf].messages += (rec.totals&&rec.totals.messages)||0;
      acc[tf].cost += rec.cost||0;
      for(const t of TOK) acc[tf][t] += (rec.totals&&rec.totals[t])||0;
    }
  }
  const rows = Object.values(acc);
  // Total input = uncached input + cache reads + cache writes (all input-side).
  // Anthropic's input_tokens is ONLY the uncached sliver; cache_read is the bulk.
  rows.forEach(r => r.total_in = r.input + r.cache_read + r.cache_creation);
  rows.sort((a,b)=>{ const x=a[sortKey],y=b[sortKey];
    if(typeof x==="string") return sortDir*x.localeCompare(y); return sortDir*((x>y)-(x<y)); });
  return rows;
}

function modelsFor(sel){
  const acc = {};
  const ms = sel === "all" ? months() : [sel];
  for(const m of ms) for(const rec of Object.values(DATA[m]||{}))
    for(const [model, s] of Object.entries(rec.by_model||{})){
      if(!acc[model]) acc[model] = {model, input:0,cache_read:0,cache_creation:0,output:0,messages:0,cost:0};
      for(const t of TOK) acc[model][t] += (s[t]||0);
      acc[model].messages += (s.messages||0);
      acc[model].cost += (s.cost||0);
    }
  const rows = Object.values(acc);
  rows.forEach(r => r.total_in = r.input + r.cache_read + r.cache_creation);
  rows.sort((a,b)=> b.cost - a.cost);
  return rows;
}

function render(){
  const sel = document.getElementById("month").value;
  const rows = rowsFor(sel);
  const tot = {sessions:0,input:0,output:0,cache_read:0,cache_creation:0,messages:0,total_in:0,cost:0};
  rows.forEach(r=>{ for(const k in tot) tot[k]+=r[k]||0; });

  // cards
  const cardDefs = [
    ["Members", fmt(rows.length)],["Sessions", fmt(tot.sessions)],
    ["Total input", tokM(tot.total_in)],["Output", tokM(tot.output)],
    ["Cache read", tokM(tot.cache_read)],["Messages", fmt(tot.messages)],
    ["Est. cost", usd(tot.cost), "cost"],
  ];
  document.getElementById("cards").innerHTML = cardDefs.map(([k,v,cls])=>
    `<div class="card"><div class="k">${k}</div><div class="v mono ${cls||''}">${v}</div></div>`).join("");

  // time-series — daily stacked composition (input/cache-read/cache-write/output)
  const daily = {};
  const ms = sel === "all" ? months() : [sel];
  for(const m of ms) for(const rec of Object.values(DATA[m]||{}))
    for(const [day, ds] of Object.entries(rec.by_day||{})){
      if(!daily[day]) daily[day] = {input:0, cache_read:0, cache_creation:0, output:0};
      for(const t of TOK) daily[day][t] += (ds[t]||0);
    }
  const days = Object.keys(daily).sort();
  const dtot = d => daily[d].input + daily[d].cache_read + daily[d].cache_creation + daily[d].output;
  const dmax = Math.max(1, ...days.map(dtot));
  const h = (v) => (v/dmax*100).toFixed(2);
  document.getElementById("timeseries").innerHTML = days.map(d=>{
    const v = daily[d];
    return `<div class="tscol" title="${d}: total input ${tokM(v.input+v.cache_read+v.cache_creation)} (uncached ${tokM(v.input)}, cache read ${tokM(v.cache_read)}, cache write ${tokM(v.cache_creation)}), output ${tokM(v.output)}">
      <div class="tsbar-out" style="height:${h(v.output)}%"></div>
      <div class="tsbar-cwrite" style="height:${h(v.cache_creation)}%"></div>
      <div class="tsbar-cread" style="height:${h(v.cache_read)}%"></div>
      <div class="tsbar-in" style="height:${h(v.input)}%"></div>
      <div class="tslbl">${d.slice(5)}</div></div>`;
  }).join("") || '<div class="note">No daily data.</div>';

  // chart — stacked composition per member; bar length = (total_in+output)/max
  const max = Math.max(1, ...rows.map(r=>r.total_in + r.output));
  const w = v => (v/max*100).toFixed(2);
  document.getElementById("chart").innerHTML = rows.map(r=>`
    <div class="barrow" title="${r.name} — total input ${tokM(r.total_in)} (uncached ${tokM(r.input)}, cache read ${tokM(r.cache_read)}, cache write ${tokM(r.cache_creation)}), output ${tokM(r.output)}, est. cost ${usd(r.cost)}">
      <div class="lbl">${r.name}</div>
      <div class="bartrack">
        <div class="seg-in" style="width:${w(r.input)}%"></div>
        <div class="seg-cread" style="width:${w(r.cache_read)}%"></div>
        <div class="seg-cwrite" style="width:${w(r.cache_creation)}%"></div>
        <div class="seg-out" style="width:${w(r.output)}%"></div>
      </div>
      <div class="barval mono">${tokM(r.total_in)} in · <span class="cost">${usd(r.cost)}</span></div>
    </div>`).join("") || '<div class="note">No data.</div>';

  // table
  document.querySelector("#tbl tbody").innerHTML = rows.map(r=>`
    <tr><td>${r.name}</td><td class="mono">${fmt(r.sessions)}</td>
    <td class="mono">${tokM(r.input)}</td><td class="mono">${tokM(r.cache_read)}</td>
    <td class="mono">${tokM(r.cache_creation)}</td><td class="mono">${tokM(r.total_in)}</td>
    <td class="mono">${tokM(r.output)}</td>
    <td class="mono">${fmt(r.messages)}</td><td class="mono cost">${usd(r.cost)}</td></tr>`).join("");
  document.querySelector("#tbl tfoot").innerHTML = `
    <tr><td>Total</td><td class="mono">${fmt(tot.sessions)}</td>
    <td class="mono">${tokM(tot.input)}</td><td class="mono">${tokM(tot.cache_read)}</td>
    <td class="mono">${tokM(tot.cache_creation)}</td><td class="mono">${tokM(tot.total_in)}</td>
    <td class="mono">${tokM(tot.output)}</td>
    <td class="mono">${fmt(tot.messages)}</td><td class="mono cost">${usd(tot.cost)}</td></tr>`;

  // by-model table
  const mrows = modelsFor(sel);
  document.querySelector("#modeltbl tbody").innerHTML = mrows.map(r=>`
    <tr><td><code>${r.model}</code></td><td class="mono">${tokM(r.input)}</td>
    <td class="mono">${tokM(r.cache_read)}</td><td class="mono">${tokM(r.cache_creation)}</td>
    <td class="mono">${tokM(r.total_in)}</td><td class="mono">${tokM(r.output)}</td>
    <td class="mono">${fmt(r.messages)}</td><td class="mono cost">${usd(r.cost)}</td></tr>`).join("")
    || '<tr><td colspan="8" class="note">No data.</td></tr>';

  document.getElementById("costnote").textContent = COST_NOTE;
}

function renderProjection(){
  const ents = Object.entries(DAILY_COST).sort((a,b)=> a[0]<b[0]?-1:1);
  const pc = document.getElementById("projcards");
  if(!ents.length){ pc.innerHTML='<div class="note">No cost data to project.</div>'; return; }
  const first = ents[0][0], last = ents[ents.length-1][0];
  const total = ents.reduce((a,[,v])=>a+v,0);
  const spanDays = Math.max(1, Math.round((new Date(last)-new Date(first))/86400000)+1);
  const perDayAll = total/spanDays;
  const cut = new Date(last); cut.setDate(cut.getDate()-6);   // recent 7 calendar days
  const perDay7 = ents.filter(([d])=> new Date(d)>=cut).reduce((a,[,v])=>a+v,0)/7;
  pc.innerHTML = [
    ["Projected 30-day", usd(perDay7*30), "cost"],
    ["Recent pace ($/day, 7d)", usd(perDay7)],
    ["Avg pace ($/day, all)", usd(perDayAll)],
    ["Proj. 30-day (avg pace)", usd(perDayAll*30)],
    ["Data window", spanDays+" days"],
  ].map(([k,v,cls])=>`<div class="card"><div class="k">${k}</div><div class="v mono ${cls||''}">${v}</div></div>`).join("");

  // cost chart: actual daily $ (solid) + 30 projected days at recent pace (faded)
  const cmax = Math.max(0.01, perDay7, ...ents.map(e=>e[1]));
  let html = ents.map(([d,v])=>`<div class="tscol" title="${d}: ${usd(v)} actual">
     <div class="tsbar-cost" style="height:${(v/cmax*100).toFixed(1)}%"></div>
     <div class="tslbl">${d.slice(5)}</div></div>`).join("");
  for(let i=1;i<=30;i++){
    const dt=new Date(last); dt.setDate(dt.getDate()+i);
    const ds=dt.toISOString().slice(0,10);
    html += `<div class="tscol" title="${ds} (projected): ${usd(perDay7)}">
      <div class="tsbar-proj ${i===1?'projstart':''}" style="height:${(perDay7/cmax*100).toFixed(1)}%"></div>
      <div class="tslbl">${i%5===0?ds.slice(5):''}</div></div>`;
  }
  document.getElementById("costts").innerHTML = html;
  document.getElementById("projnote").textContent =
    `Projection = recent 7-day run-rate ($${perDay7.toFixed(2)}/day) × 30. Linear; assumes usage continues at the same pace. `
    + `Solid bars = actual daily cost; faded = projected. Based on ${spanDays} days of data (${first} to ${last}). `
    + `Indicative API-equivalent cost, not subscription billing.`;
}

function renderRateCard(){
  const models = RATE_CARD.models || {};
  const fams = RATE_CARD.families || {};
  const entries = Object.keys(models).length ? Object.entries(models) : Object.entries(fams);
  const m2 = n => '$'+(n==null?'—':Number(n).toFixed(2));
  document.querySelector("#ratetbl tbody").innerHTML = entries.map(([m,r])=>`
    <tr><td><code>${m}</code></td><td class="mono">${m2(r.input)}</td>
    <td class="mono">${m2(r.cache_write_1h)}</td>
    <td class="mono">${m2(r.cache_read)}</td><td class="mono">${m2(r.output)}</td></tr>`).join("")
    || '<tr><td colspan="5" class="note">No rate card loaded.</td></tr>';
  document.getElementById("ratesrc").textContent =
    `Rates in $/MTok. Source: ${RATE_CARD._source||'pricing.json'} (retrieved ${RATE_CARD._retrieved||'?'}). `
    + `"Write" = 1-hour cache-write rate (what Claude Code uses); cost prices each write at its actual 5m/1h rate. `
    + `Edit tools/usage-metrics/pricing.json to update.`;
}

// build month dropdown (All + each)
const msel = document.getElementById("month");
msel.innerHTML = `<option value="all">All months</option>` +
  months().map(m=>`<option value="${m}">${m}</option>`).join("");
msel.value = "all";
msel.addEventListener("change", render);
document.querySelectorAll("#tbl th").forEach(th=>th.addEventListener("click",()=>{
  const k = th.dataset.k; if(sortKey===k) sortDir*=-1; else { sortKey=k; sortDir = k==="name"?1:-1; }
  render();
}));
render();
renderProjection();
renderRateCard();
</script>
</body>
</html>
"""


def render_html(all_plain: dict, cost_note: str, daily_cost: dict, pricing: dict | None) -> str:
    """Single self-contained HTML file embedding all months (no external deps)."""
    return (HTML_TEMPLATE
            .replace("__USAGE_DATA__", json.dumps(all_plain, sort_keys=True))
            .replace("__COST_NOTE__", json.dumps(cost_note))
            .replace("__DAILY_COST__", json.dumps(daily_cost, sort_keys=True))
            .replace("__RATE_CARD__", json.dumps(pricing or {}, sort_keys=True)))


def main() -> int:
    ap = argparse.ArgumentParser(description="Aggregate per-user Claude Code token usage.")
    ap.add_argument("--month", default=None, help="YYYY-MM (default: all months found)")
    ap.add_argument("--pull", action="store_true", help="git pull --ff-only first")
    ap.add_argument("--project-root", type=Path, default=None)
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    project_root = find_project_root(args.project_root or Path.cwd())

    if args.pull:
        subprocess.run(["git", "pull", "--ff-only"], cwd=str(project_root), check=False)

    cfg = read_cfg(project_root / "project.yml")
    runner_tf = None
    try:
        runner_tf = subprocess.run(
            [sys.executable, str(project_root / ".claude/skills/shared/scripts/resolve_user.py"),
             "--task-folder"],
            capture_output=True, text=True, cwd=str(project_root), check=True,
        ).stdout.strip()
    except Exception:
        runner_tf = None

    # Team dashboard lives in tools/usage-metrics/ (shared, generated — not per-person).
    out_tmpl = cfg.get("output_dir") or "tools/usage-metrics"
    out_dir = project_root / out_tmpl.format(task_folder=runner_tf or "")
    out_dir.mkdir(parents=True, exist_ok=True)

    pricing = load_pricing(project_root)
    data, task_data = collect_records(project_root, args.month)

    if not data:
        if not args.quiet:
            print("aggregate: no per-session records found under tasks/*/_usage-metrics/")
        return 0

    # Anonymize: stable "Member N" labels by sorted task_folder. NO real names or
    # task_folder identifiers appear in the team view — it aggregates everyone.
    folders = sorted({tf for month in data.values() for tf in month})
    anon = {tf: f"Member {i + 1}" for i, tf in enumerate(folders)}

    all_plain: dict = {}
    for month in sorted(data):
        md = render_markdown(month, data[month], anon, pricing)
        (out_dir / f"{month}.md").write_text(md, encoding="utf-8")
        # Anonymized per-member rollup keyed by the Member-N label (no PII).
        plain = {
            anon[tf]: {
                "sessions": slot["sessions"],
                "totals": dict(slot["totals"]),
                "by_model": {m: {**dict(ms), "cost": cost_of({m: ms}, pricing)}
                             for m, ms in slot["by_model"].items()},
                "by_day": {d: dict(ds) for d, ds in sorted(slot["by_day"].items())},
                "name": anon[tf],
                "cost": cost_of(slot["by_model"], pricing),
            }
            for tf, slot in data[month].items()
        }
        all_plain[month] = plain

    cost_note = (
        ("Est. cost = measured tokens × list prices in tools/usage-metrics/pricing.json "
         f"(updated {pricing.get('_updated','?')}). Indicative API-equivalent cost — "
         "Claude Code subscription billing is a flat fee, not this. Verify rates against "
         "current Anthropic pricing.") if pricing else
        "Cost unavailable — tools/usage-metrics/pricing.json missing."
    )
    eff = effective_rates(all_plain, pricing)
    daily_cost = daily_cost_series(all_plain, eff)

    # 1) Self-contained HTML team dashboard.
    html_path = out_dir / "index.html"
    html_path.write_text(render_html(all_plain, cost_note, daily_cost, pricing), encoding="utf-8")

    # 2) Consolidated JSON — the machine-readable team view (consumed by
    #    project-console's Metrics view). Anonymized; no names, no task_folders.
    # Per-task cost rollup — the value dimension. Task-IDENTIFIED (<tf>/<task_id>)
    # so it can join to per-task economics estimates downstream; "_unattributed"
    # is honest overhead (work with no active task). NOTE: unlike the `months`
    # member view, this block is NOT person-anonymized — value is task-scoped, and
    # the join to estimates needs the real task ref. The console (Phase 5) decides
    # how to present it. Estimates/person-hours are added in a later phase.
    tasks_out = {
        ref: {
            "by_model": {m: {**dict(ms), "cost": cost_of({m: ms}, pricing)}
                         for m, ms in slot["by_model"].items()},
            "totals": dict(slot["totals"]),
            "sessions": slot["sessions"],
            "cost": cost_of(slot["by_model"], pricing),
        }
        for ref, slot in sorted(task_data.items())
    }

    usage_json = {
        "schema": "usage-metrics/team/v2",
        "anonymized": True,           # applies to the `months`/member view
        "members": len(folders),
        "months": all_plain,
        "tasks": tasks_out,           # v2: per-task cost (task-identified; value dimension)
        "daily_cost": daily_cost,
        "rate_card": pricing or {},
        "cost_note": cost_note,
    }
    json_path = out_dir / "usage.json"
    json_path.write_text(json.dumps(usage_json, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if not args.quiet:
        print(f"aggregate: wrote team dashboard → {html_path.relative_to(project_root)}")
        print(f"aggregate: wrote team JSON      → {json_path.relative_to(project_root)} "
              f"({len(folders)} member(s), {len(all_plain)} month(s), anonymized)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
