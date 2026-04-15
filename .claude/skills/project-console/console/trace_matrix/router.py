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
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from console.chat.sdk_client import stream_response
from console.config import get_config
from console.trace_matrix.loader import list_dhfs, load_sidecar, skill_build_script

router = APIRouter()
templates = Jinja2Templates(
    directory=str(Path(__file__).parent.parent / "web" / "templates")
)


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
async def trace_matrix_index(request: Request):
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
        },
    )


@router.get("/trace-matrix/{dhf}", response_class=HTMLResponse)
async def trace_matrix_view(request: Request, dhf: str):
    cfg = get_config()
    sidecar = load_sidecar(cfg.repo_root, dhf)
    if sidecar is None:
        raise HTTPException(404, f"No trace-matrix sidecar for DHF '{dhf}'.")
    # Pre-compute source-link URLs per item from the sidecar's source_files.
    for layer in sidecar["layers"]:
        layer_sources = layer.get("source_files") or []
        for item in layer["items"]:
            item["source_url"] = _doc_view_url(layer_sources, item["id"])

    has_skill = skill_build_script(cfg.repo_root) is not None
    return templates.TemplateResponse(
        request,
        "trace_matrix_view.html",
        {
            "config": cfg,
            "dhf": dhf,
            "sidecar": sidecar,
            "has_skill": has_skill,
        },
    )


@router.get("/trace-matrix/{dhf}/raw", response_class=JSONResponse)
async def trace_matrix_raw(dhf: str):
    cfg = get_config()
    sidecar = load_sidecar(cfg.repo_root, dhf)
    if sidecar is None:
        raise HTTPException(404, f"No sidecar for DHF '{dhf}'.")
    return JSONResponse(sidecar)


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


@router.post("/trace-matrix/build")
async def trace_matrix_build_all():
    cfg = get_config()
    rc, output = _run_build(cfg.repo_root, None)
    return RedirectResponse(url="/trace-matrix", status_code=303)


@router.post("/trace-matrix/{dhf}/build")
async def trace_matrix_build_one(dhf: str):
    cfg = get_config()
    rc, output = _run_build(cfg.repo_root, dhf)
    return RedirectResponse(url=f"/trace-matrix/{dhf}", status_code=303)


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
