"""Trace Matrix section routes.

GET  /trace-matrix                      — index (one card per DHF)
GET  /trace-matrix/{dhf}                — layered view with filters
POST /trace-matrix/{dhf}/build          — shell to the trace-matrix skill (rebuild)
POST /trace-matrix/build                — rebuild all DHFs
GET  /trace-matrix/{dhf}/raw            — raw JSON (debug)
POST /trace-matrix/{dhf}/chat/stream    — Systems Engineering Assistant SSE chat

The build endpoints shell out to the trace-matrix skill's build.py if the
skill is installed. They return the captured stdout so the console can show
the user what happened.

The chat endpoint injects a compact textual rendition of the sidecar into
the system prompt as grounding context, then streams Agent SDK output back
as SSE events. Chat memory is not stored server-side — the browser owns it
in localStorage and sends the history with every request.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import AsyncIterator

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import (
    HTMLResponse,
    JSONResponse,
    PlainTextResponse,
    RedirectResponse,
    StreamingResponse,
)
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from console.chat.sdk_client import stream_response
from console.config import get_config
from console.trace_matrix.loader import (
    list_dhfs,
    load_drift_overlay,
    load_sidecar,
    skill_build_script,
)

router = APIRouter()
templates = Jinja2Templates(
    directory=str(Path(__file__).parent.parent / "web" / "templates")
)


# Per-layer trace-column model. Each layer projects its trace neighbours into
# typed columns rather than a single forward/reverse split — readers expect to
# see "DI's V&V" not "DI's downstream traces". Missing neighbour layers (e.g.
# no `software` layer in the system DHF) collapse to a `—` cell automatically.
#
# `target_layer` controls click-through navigation — the chip jumps to that
# tab and scrolls to the target row.
LAYER_TRACE_COLUMNS: dict[str, list[dict]] = {
    "user_needs": [
        {"key": "down_di", "label": "→ DI", "target_layer": "design_inputs"},
    ],
    "design_inputs": [
        {"key": "up_un", "label": "← UN", "target_layer": "user_needs"},
        {"key": "down_sw", "label": "→ SW", "target_layer": "software"},
        {"key": "down_vnv", "label": "→ V&V", "target_layer": "vnv"},
        {"key": "ovr_risk", "label": "↔ Risk", "target_layer": "risk", "is_overlay": True},
    ],
    "software": [
        {"key": "up_di", "label": "← DI", "target_layer": "design_inputs"},
        {"key": "down_vnv", "label": "→ V&V", "target_layer": "vnv"},
        {"key": "ovr_risk", "label": "↔ Risk", "target_layer": "risk", "is_overlay": True},
    ],
    "architecture": [
        {"key": "ovr_di", "label": "↔ DI", "target_layer": "design_inputs", "is_overlay": True},
    ],
    "vnv": [
        {"key": "up_di", "label": "← DI", "target_layer": "design_inputs"},
        {"key": "up_sw", "label": "← SW", "target_layer": "software"},
        {"key": "ovr_risk", "label": "↔ Risk", "target_layer": "risk", "is_overlay": True},
    ],
    "risk": [
        {"key": "ovr_di", "label": "↔ DI", "target_layer": "design_inputs", "is_overlay": True},
        {"key": "ovr_sw", "label": "↔ SW", "target_layer": "software", "is_overlay": True},
        {"key": "ovr_vnv", "label": "↔ V&V", "target_layer": "vnv", "is_overlay": True},
    ],
}


def _layer_of_index(sidecar: dict) -> dict[str, str]:
    """Map every item id → its layer key. Used to bucket per-row trace
    neighbours by target-layer column."""
    out: dict[str, str] = {}
    for layer in sidecar.get("layers", []) or []:
        for item in layer.get("items") or []:
            out[item["id"]] = layer["key"]
    return out


def _decorate_trace_columns(sidecar: dict) -> None:
    """For each item, compute `trace_cells` — one entry per trace column
    declared for the item's layer, each containing the neighbours that fall
    into that column. Mutates the sidecar in place."""
    layer_of = _layer_of_index(sidecar)
    for layer in sidecar.get("layers", []) or []:
        cols = LAYER_TRACE_COLUMNS.get(layer["key"], [])
        for item in layer.get("items") or []:
            buckets: dict[str, list[dict]] = {c["key"]: [] for c in cols}
            for ref in item.get("traces_forward", []):
                target_layer = layer_of.get(ref["id"])
                for c in cols:
                    if c["target_layer"] == target_layer:
                        buckets[c["key"]].append(ref)
            for ref in item.get("traces_reverse", []):
                target_layer = layer_of.get(ref["id"])
                for c in cols:
                    if c["target_layer"] == target_layer:
                        # avoid double-listing if both forward + reverse
                        # populated the same edge
                        if not any(r["id"] == ref["id"] for r in buckets[c["key"]]):
                            buckets[c["key"]].append(ref)
            item["trace_cells"] = [
                {
                    "col_key": c["key"],
                    "label": c["label"],
                    "target_layer": c["target_layer"],
                    "is_overlay": c.get("is_overlay", False),
                    # Same Jinja-attribute-vs-dict-method gotcha as in
                    # `_build_groups`: name the list `refs`, not `items`.
                    "refs": buckets[c["key"]],
                }
                for c in cols
            ]


def _build_groups(layer: dict) -> list[dict]:
    """Bucket layer items into ordered groups keyed by `group_label`. Items
    that share the first-seen group_label coalesce into one group; items with
    no group_label coalesce into a single trailing "(ungrouped)" group.
    Group order matches first-seen item order — preserves the layer's
    deterministic sort.
    """
    out: list[dict] = []
    by_label: dict[str, dict] = {}
    for item in layer.get("items") or []:
        label = item.get("group_label") or "(ungrouped)"
        bucket = by_label.get(label)
        if bucket is None:
            bucket = {
                "label": label,
                "key": item.get("group") or "",
                # The bucket's row list is named `rows` (not `items`) so
                # Jinja's attribute lookup `grp.rows` doesn't collide with
                # Python dict's `.items()` method — `grp.items` would resolve
                # to the bound method, not the value.
                "rows": [],
                "drift_count": 0,
                "orphan_count": 0,
            }
            by_label[label] = bucket
            out.append(bucket)
        bucket["rows"].append(item)
        if item.get("violations"):
            bucket["drift_count"] += 1
        if item.get("_is_orphan"):
            bucket["orphan_count"] += 1
    return out


def _doc_view_url(source_files: list[str], item_id: str) -> str:
    """Build a documents-browser URL for the source row of an item.

    Reads the `source_files` field from the sidecar layer (authored by the
    trace-matrix skill from trace-matrix.yml). The console never hardcodes
    file paths — the skill is the single source of truth for where a layer's
    source lives. For multi-file layers we link to the first source; the
    anchor fallback inside the documents browser handles ID resolution.
    """
    if not source_files:
        return ""
    src = source_files[0]
    return f"/documents/view/{src}#{item_id}"


@router.get("/trace-matrix", response_class=HTMLResponse)
async def trace_matrix_index(request: Request, build_error: str | None = None):
    cfg = get_config()
    dhfs = list_dhfs(cfg.repo_root)
    has_skill = skill_build_script(cfg.repo_root) is not None
    return templates.TemplateResponse(
        request,
        "trace_matrix_index.html",
        {
            "config": cfg,
            "dhfs": dhfs,
            "has_skill": has_skill,
            "any_sidecar": any(d.has_sidecar for d in dhfs),
            "build_error": build_error,
        },
    )


@router.get("/trace-matrix/{dhf}", response_class=HTMLResponse)
async def trace_matrix_view(request: Request, dhf: str, build_error: str | None = None):
    cfg = get_config()
    # Verify the DHF is declared in project.yml before doing anything else.
    known = {d.name for d in list_dhfs(cfg.repo_root)}
    if dhf not in known:
        raise HTTPException(
            404,
            f"DHF '{dhf}' is not declared in project.yml `dhfs[]`. Known: {sorted(known) or 'none'}",
        )
    sidecar = load_sidecar(cfg.repo_root, dhf)
    has_skill = skill_build_script(cfg.repo_root) is not None

    if sidecar is None:
        # Empty state — render the view template without a sidecar so the user
        # sees a "Build this DHF" button and, if a previous build failed, the
        # captured stderr with guidance (e.g. "run /trace-matrix init first").
        return templates.TemplateResponse(
            request,
            "trace_matrix_view.html",
            {
                "config": cfg,
                "dhf": dhf,
                "sidecar": None,
                "has_skill": has_skill,
                "build_error": build_error,
            },
        )

    # Pre-compute source-link URLs per item from the sidecar's source_files.
    for layer in sidecar["layers"]:
        layer_sources = layer.get("source_files") or []
        for item in layer["items"]:
            item["source_url"] = _doc_view_url(layer_sources, item["id"])

    # Load any sibling drift.json files (project-agnostic — works for any
    # project that emits drift data colocated with trace sources).
    drift = load_drift_overlay(cfg.repo_root, sidecar)

    # Pre-decorate every row with its violations + worst severity. Violations
    # are looked up against multiple candidate ids per node — the row's own
    # `id` and any auxiliary identifier the adapter recorded (e.g. `jira_key`
    # when the row's primary id is a derived DI prefix). This is what makes
    # the badge/drawer fire on rows whose item.id is a domain-canonical id
    # while the drift's `item_id` is the underlying Jira key.
    severity_rank = {"error": 3, "warning": 2, "info": 1}
    if drift:
        vbi = drift["violations_by_item"]
        for layer in sidecar["layers"]:
            for item in layer["items"]:
                lookup_keys = [item.get("id")]
                aux = item.get("jira_key")
                if aux and aux not in lookup_keys:
                    lookup_keys.append(aux)
                vs: list[dict] = []
                seen_ids: set[int] = set()
                for k in lookup_keys:
                    for v in vbi.get(k, []):
                        if id(v) in seen_ids:
                            continue
                        seen_ids.add(id(v))
                        vs.append(v)
                item["violations"] = vs
                item["worst_severity"] = (
                    max((v.get("severity") for v in vs), key=lambda s: severity_rank.get(s, 0))
                    if vs
                    else None
                )

    # Tag orphan items so groupers can count them. Orphan ids are stored in
    # the sidecar's gaps section; flatten into a per-item flag for cheap
    # access during template rendering and group-bucket aggregation.
    for layer in sidecar["layers"]:
        orphan_ids = set(sidecar.get("gaps", {}).get("orphans", {}).get(layer["key"], []))
        for item in layer.get("items", []):
            item["_is_orphan"] = item["id"] in orphan_ids

    # Decorate items with typed trace columns (one entry per layer-relation),
    # then bucket items into collapsible groups keyed by `group_label`.
    _decorate_trace_columns(sidecar)
    for layer in sidecar["layers"]:
        layer["groups"] = _build_groups(layer)

    # Compact id → [violation, ...] map sent to the browser as JSON. The
    # drift-popover JS pulls from this on demand instead of rendering every
    # violation drawer into the hidden DOM (the canary intra-op DHF has 16
    # violations across 13 items today; sparing 13 hidden drawer-trees per
    # row is cheap, but for projects with hundreds of drift entries it adds
    # up).
    violations_by_id: dict[str, list[dict]] = {}
    for layer in sidecar["layers"]:
        for item in layer.get("items", []):
            if item.get("violations"):
                violations_by_id[item["id"]] = item["violations"]

    # Collect per-source-file mtimes for the help-hover panel. Sources are
    # the per-layer `source_files` plus any sibling drift.json files that
    # were merged in. Keep one row per unique path; tag with the layer keys
    # that referenced it so the reader can see which trace lane the file
    # feeds.
    from datetime import datetime, timezone

    source_meta: list[dict] = []
    seen_paths: dict[str, dict] = {}
    repo_root = Path(cfg.repo_root)
    for layer in sidecar["layers"]:
        for src in layer.get("source_files") or []:
            entry = seen_paths.get(src)
            if entry is None:
                fp = repo_root / src
                mtime_iso: str | None = None
                size: int | None = None
                exists = fp.exists()
                if exists:
                    try:
                        st = fp.stat()
                        mtime_iso = datetime.fromtimestamp(
                            st.st_mtime, tz=timezone.utc
                        ).strftime("%Y-%m-%d %H:%M UTC")
                        size = st.st_size
                    except OSError:
                        pass
                entry = {
                    "path": src,
                    "exists": exists,
                    "mtime": mtime_iso,
                    "size": size,
                    "layers": [],
                    "kind": "trace",
                }
                seen_paths[src] = entry
                source_meta.append(entry)
            if layer["key"] not in entry["layers"]:
                entry["layers"].append(layer["key"])
    if drift:
        for ds in drift.get("sources") or []:
            if ds in seen_paths:
                continue
            fp = repo_root / ds
            mtime_iso = None
            size = None
            exists = fp.exists()
            if exists:
                try:
                    st = fp.stat()
                    mtime_iso = datetime.fromtimestamp(
                        st.st_mtime, tz=timezone.utc
                    ).strftime("%Y-%m-%d %H:%M UTC")
                    size = st.st_size
                except OSError:
                    pass
            entry = {
                "path": ds,
                "exists": exists,
                "mtime": mtime_iso,
                "size": size,
                "layers": [],
                "kind": "drift",
            }
            seen_paths[ds] = entry
            source_meta.append(entry)

    return templates.TemplateResponse(
        request,
        "trace_matrix_view.html",
        {
            "config": cfg,
            "dhf": dhf,
            "sidecar": sidecar,
            "drift": drift,
            "violations_by_id": violations_by_id,
            "source_meta": source_meta,
            "has_skill": has_skill,
            "build_error": build_error,
        },
    )


@router.get("/trace-matrix/{dhf}/raw", response_class=JSONResponse)
async def trace_matrix_raw(dhf: str):
    cfg = get_config()
    sidecar = load_sidecar(cfg.repo_root, dhf)
    if sidecar is None:
        raise HTTPException(404, f"No sidecar for DHF '{dhf}'.")
    return JSONResponse(sidecar)


@router.get("/trace-matrix/{dhf}/grounding", response_class=PlainTextResponse)
async def trace_matrix_grounding(dhf: str):
    """Compact single-line-per-item rendition of the sidecar for the
    generic Assistant drawer. Used when the drawer is mounted on the
    trace-matrix view with ``grounding_source: "url:/trace-matrix/{dhf}/grounding"``."""
    cfg = get_config()
    sidecar = load_sidecar(cfg.repo_root, dhf)
    if sidecar is None:
        raise HTTPException(404, f"No sidecar for DHF '{dhf}'. Build it first.")
    return PlainTextResponse(_compact_context(sidecar))


def _run_build(repo_root: Path, dhf: str | None) -> tuple[int, str]:
    script = skill_build_script(repo_root)
    if script is None:
        return 127, "trace-matrix skill not installed at .claude/skills/trace-matrix/"
    cmd = [sys.executable, str(script), "--repo", str(repo_root)]
    if dhf:
        cmd += ["--dhf", dhf]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    except subprocess.TimeoutExpired:
        return 124, "build timed out after 120s"
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def _hint_from_output(output: str) -> str:
    """Translate common build-failure signatures into an actionable hint."""
    low = output.lower()
    if "trace-matrix.yml" in low and "not found" in low:
        return (
            "trace-matrix.yml doesn't exist yet. Run `/trace-matrix init` from Claude "
            "Code — it reads project.yml, writes a default trace-matrix.yml, and runs "
            "the first build."
        )
    if "not installed" in low and "trace-matrix" in low:
        return (
            "The trace-matrix skill is not installed. Run `/sync-skills pull` to fetch "
            "it from the registry."
        )
    return ""


@router.post("/trace-matrix/build")
async def trace_matrix_build_all():
    cfg = get_config()
    rc, output = _run_build(cfg.repo_root, None)
    if rc != 0:
        hint = _hint_from_output(output)
        err = (hint + "\n\n" if hint else "") + output
        return RedirectResponse(
            url=f"/trace-matrix?build_error={_qs(err)}", status_code=303
        )
    return RedirectResponse(url="/trace-matrix", status_code=303)


@router.post("/trace-matrix/{dhf}/build")
async def trace_matrix_build_one(dhf: str):
    cfg = get_config()
    rc, output = _run_build(cfg.repo_root, dhf)
    if rc != 0:
        hint = _hint_from_output(output)
        err = (hint + "\n\n" if hint else "") + output
        return RedirectResponse(
            url=f"/trace-matrix/{dhf}?build_error={_qs(err)}", status_code=303
        )
    return RedirectResponse(url=f"/trace-matrix/{dhf}", status_code=303)


# ---------------------------------------------------------------------------
# LLM-driven init — runs the `/trace-matrix init` skill action via Agent SDK
# ---------------------------------------------------------------------------
#
# The `build` endpoints shell to the deterministic `build.py` script. The
# `init` endpoint does something heavier: it invokes Claude via the Agent SDK
# to execute the `/trace-matrix init` skill action, which (per
# `.claude/skills/trace-matrix/SKILL.md`) reads project.yml, writes a default
# `trace-matrix.yml`, runs analyze.py per layer, generates tailored parser
# adapters for any layer whose defaults fail, and finally runs build.py.
# Adapter generation is LLM-authored Python and therefore cannot live in
# build.py — it requires Claude. This is the one-click bootstrap.


_INIT_SYSTEM_PROMPT = """\
You are executing the `/trace-matrix init` action for a medtech-docs
project. The current working directory is the project root. You have
Bash, Read, Write, Edit, Glob, and Grep tools.

## Steps (execute in order, no deviations)

1. **Read `project.yml`** and extract `dhfs[]`. Each entry has a `path`
   field (leaf name OR full `docs/project/dhfs/<leaf>` — normalize to leaf).
2. **If `trace-matrix.yml` does not exist at the repo root**, write one.
   Format (list-of-dicts, NOT dict-of-dicts — `build.py` expects a list):
   ```yaml
   version: 1
   dhfs:
     - name: <leaf>
       layers:
         user_needs:
           source: docs/project/dhfs/<leaf>/design-controls/user-needs/user-needs.md
           id_prefix: UN
         design_inputs:
           source: docs/project/dhfs/<leaf>/design-controls/requirements/design-inputs.md
           id_prefix: DI
         architecture:
           source: <first .md under design-controls/architecture/ — glob for it>
           id_prefix: M
         vnv:
           source: docs/project/dhfs/<leaf>/design-controls/vnv/vnv-plan.md
           id_prefix: VER
         risk:
           source: docs/project/dhfs/<leaf>/risk-management/risk-analysis.md
           id_prefix: R
   ```
   For layers whose source file doesn't exist yet, keep the path anyway —
   the default parser will emit `source_empty` and that's fine.
3. **Run analyze**:
   `python3 .claude/skills/trace-matrix/scripts/analyze.py --repo . --dhf <leaf> --json`
   Parse the JSON output. For any layer where `ok:false` AND `source_empty:false`
   (meaning the source exists but the default parser couldn't extract items),
   proceed to step 4. Otherwise skip to step 5.
4. **Generate a project adapter** for each failing-with-source layer:
   - Read the source doc.
   - Read `.claude/skills/trace-matrix/scripts/adapter_api.py` ONCE to learn
     the `ParserResult` contract (only if you haven't already).
   - Write `tools/project-console/trace-matrix/adapters/<layer>.py` exposing
     `def parse(path, layer_cfg) -> ParserResult`. Tailor to the doc's
     actual shape (column headers, ID format, trace columns).
5. **Run the build**:
   `python3 .claude/skills/trace-matrix/scripts/build.py --repo . --dhf <leaf>`
6. **Print `RESULT: OK — <one-line summary>`** (e.g.
   "6 architecture nodes parsed via generated adapter, other 4 layers empty")
   or `RESULT: FAIL — <reason>` if anything fatal happened.

## Constraints

- Be terse. One status line per step, no file dumps, no philosophical asides.
- Do NOT re-read files you've already read in this session.
- Do NOT read `SKILL.md` — the steps above are authoritative and complete.
- Adapter files go under `tools/project-console/trace-matrix/adapters/`,
  NOT under the skill directory. Writes there are excluded from uvicorn's
  reload watcher so they won't kill this session.

## Task gate

Some projects have a PreToolUse hook that blocks Edit/Write unless a task
is active. If your first Write is denied, the denial message contains the
exact session ID and the command to run — just execute it, reuse any
existing `trace-matrix` or `console` task, and keep going. Do NOT spend
turns reading task templates or the task skill; the denial message is
self-documenting.
"""


def _init_user_message(repo_root: Path, dhf: str | None) -> str:
    target = f"DHF `{dhf}`" if dhf else "every DHF in `project.yml`"
    return (
        f"Run `/trace-matrix init` for {target}. Project root: `{repo_root}`. "
        "Follow SKILL.md exactly. When done, print the RESULT line."
    )


_INIT_ALLOWED_TOOLS = ["Bash", "Read", "Write", "Edit", "Glob", "Grep"]


async def _stream_init(repo_root: Path, dhf: str | None) -> AsyncIterator[dict]:
    """Drive `/trace-matrix init` via the Agent SDK with file+bash tools.

    Unlike the chat stream_response (which is pure text Q&A), init has to
    actually write files and run scripts, so we pass `allowed_tools`,
    `permission_mode='bypassPermissions'` (localhost dev tool — the user
    already owns this repo), `cwd=repo_root` so skill lookup works, and
    `max_turns` to cap a runaway loop.

    Yields dicts of {type, ...} which the route wraps in SSE frames.
    """
    from claude_agent_sdk import (  # local import to keep router lightweight
        AssistantMessage,
        ClaudeAgentOptions,
        ResultMessage,
        StreamEvent,
        SystemMessage,
        TextBlock,
        ToolUseBlock,
        UserMessage,
        query,
    )

    options = ClaudeAgentOptions(
        system_prompt=_INIT_SYSTEM_PROMPT,
        allowed_tools=_INIT_ALLOWED_TOOLS,
        permission_mode="bypassPermissions",
        cwd=str(repo_root),
        max_turns=40,
        include_partial_messages=True,
    )
    prompt = _init_user_message(repo_root, dhf)

    got_any_delta = False
    async for msg in query(prompt=prompt, options=options):
        if isinstance(msg, StreamEvent):
            evt = msg.event or {}
            if evt.get("type") == "content_block_delta":
                delta = evt.get("delta") or {}
                if delta.get("type") == "text_delta":
                    text = delta.get("text") or ""
                    if text:
                        got_any_delta = True
                        yield {"type": "token", "text": text}
        elif isinstance(msg, AssistantMessage):
            # Surface tool calls so the user can see what init is doing.
            for block in msg.content:
                if isinstance(block, ToolUseBlock):
                    yield {
                        "type": "tool",
                        "name": block.name,
                        "brief": _brief_tool(block.name, block.input),
                    }
                elif isinstance(block, TextBlock) and block.text and not got_any_delta:
                    yield {"type": "token", "text": block.text}
        elif isinstance(msg, ResultMessage):
            yield {"type": "result", "summary": getattr(msg, "result", "")}


def _brief_tool(name: str, inp: dict) -> str:
    """One-line summary of a tool call for the live panel."""
    if name == "Bash":
        cmd = (inp.get("command") or "").strip()
        return cmd[:200]
    if name in ("Read", "Write", "Edit"):
        p = inp.get("file_path") or inp.get("path") or ""
        return p
    if name == "Glob":
        return inp.get("pattern") or ""
    if name == "Grep":
        return inp.get("pattern") or ""
    return ""


@router.post("/trace-matrix/{dhf}/init/stream")
async def trace_matrix_init_stream(dhf: str):
    """Stream a live `/trace-matrix init` run via the Agent SDK.

    The browser POSTs here, reads the SSE stream, renders tokens + tool calls
    in a live panel, and reloads the page when `done` fires.
    """
    cfg = get_config()

    async def events() -> AsyncIterator[str]:
        yield _sse({"type": "start", "dhf": dhf})
        try:
            async for payload in _stream_init(cfg.repo_root, dhf):
                yield _sse(payload)
            yield _sse({"type": "done"})
        except Exception as e:
            import traceback
            yield _sse({"type": "error", "message": f"{e}\n{traceback.format_exc()}"})

    return StreamingResponse(
        events(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


def _qs(s: str) -> str:
    from urllib.parse import quote
    # Cap at 4KB so the query string stays reasonable even if build.py dumps a trace.
    return quote(s[:4096], safe="")


# ---------------------------------------------------------------------------
# Systems Engineering Assistant — chat sidecar
# ---------------------------------------------------------------------------


def _compact_context(sidecar: dict) -> str:
    """Build a compact, high-signal textual rendition of the trace matrix
    for use as the system-prompt grounding context.

    JSON is expensive. One line per item keeps the token cost down and is
    easy for Claude to scan for "which DIs are CtS?" / "what traces to
    UN-001?" style questions.
    """
    lines: list[str] = []
    lines.append(f"# Trace Matrix — {sidecar.get('dhf', '?')}")
    lines.append(f"Generated: {sidecar.get('generated_at', '?')}")
    lines.append("")

    stats = sidecar.get("stats", {}) or {}
    for layer in sidecar.get("layers", []):
        key = layer.get("key")
        s = stats.get(key, {}) or {}
        flags = []
        if layer.get("missing_reason"):
            flags.append(layer["missing_reason"])
        if key == "architecture" and not layer.get("edges_known", True):
            flags.append("edges_unknown")
        flag_txt = f" [{', '.join(flags)}]" if flags else ""
        lines.append(
            f"## {layer.get('title', key)} — count={s.get('count', 0)} "
            f"fwd={s.get('with_forward', 0)} rev={s.get('with_reverse', 0)} "
            f"orphan={s.get('orphan', 0)}{flag_txt}"
        )
        if layer.get("source_files"):
            lines.append(f"Source: {', '.join(layer['source_files'])}")
        lines.append("")

        for item in layer.get("items", []) or []:
            parts = [item["id"]]
            crit = item.get("criticality")
            if crit:
                parts.append(f"[{crit}]")
            group = item.get("group")
            if group:
                parts.append(f"({group})")
            summary = item.get("summary") or item.get("full_text", "")
            if summary:
                # Keep the full text — it's the most useful thing for Q&A.
                full = item.get("full_text") or summary
                parts.append(full)
            line = " ".join(parts)
            fwd = [t.get("id", "?") for t in item.get("traces_forward", [])]
            rev = [t.get("id", "?") for t in item.get("traces_reverse", [])]
            if fwd:
                line += f"  → {', '.join(fwd)}"
            if rev:
                line += f"  ← {', '.join(rev)}"
            lines.append(line)
        lines.append("")

    gaps = sidecar.get("gaps", {}) or {}
    if gaps.get("broken_refs"):
        lines.append("## Broken references")
        for br in gaps["broken_refs"]:
            lines.append(f"- {br.get('from')} → {br.get('to')} ({br.get('reason')})")
        lines.append("")

    return "\n".join(lines)


def _chat_system_prompt(sidecar: dict) -> str:
    context = _compact_context(sidecar)
    return (
        "You are the **Systems Engineering Assistant** for the "
        f"{sidecar.get('dhf', '?')} DHF trace matrix. You help the team "
        "reason about requirements traceability, coverage gaps, safety "
        "criticality, verification status, and cross-layer relationships.\n\n"
        "Ground every answer in the trace matrix data below. When the user "
        "asks a question, cite the relevant IDs (e.g. DI-004, UN-003, "
        "VER-PP3500-SW-002). When they ask about gaps, look at orphan counts "
        "and missing forward traces. When they ask about safety coverage, "
        "filter by criticality. Be concise. If a question can't be answered "
        "from the matrix alone, say so and explain what source document "
        "would need to be authored.\n\n"
        "===== TRACE MATRIX CONTEXT =====\n"
        f"{context}"
    )


def _format_chat_prompt(history: list[dict], latest: str) -> str:
    if not history:
        return latest
    parts = ["<conversation>"]
    for m in history:
        role = "user" if m.get("role") == "user" else "assistant"
        content = (m.get("content") or "").strip()
        if not content:
            continue
        parts.append(f'  <turn role="{role}">{content}</turn>')
    parts.append("</conversation>")
    parts.append("")
    parts.append(f"Latest user message:\n{latest}")
    return "\n".join(parts)


def _sse(event: dict) -> str:
    return f"data: {json.dumps(event)}\n\n"


class ChatStreamBody(BaseModel):
    history: list[dict]
    message: str


@router.post("/trace-matrix/{dhf}/chat/stream")
async def trace_matrix_chat_stream(dhf: str, body: ChatStreamBody):
    cfg = get_config()
    sidecar = load_sidecar(cfg.repo_root, dhf)
    if sidecar is None:
        raise HTTPException(404, f"No sidecar for DHF '{dhf}'. Build it first.")

    system = _chat_system_prompt(sidecar)
    prompt = _format_chat_prompt(body.history, body.message)

    async def event_stream() -> AsyncIterator[str]:
        try:
            async for token in stream_response(system_prompt=system, user_message=prompt):
                yield _sse({"type": "token", "text": token})
            yield _sse({"type": "done"})
        except Exception as e:
            yield _sse({"type": "error", "message": str(e)})

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
