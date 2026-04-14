import json
from pathlib import Path
from typing import AsyncIterator

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from console.chat.domain_agents import DomainAgent, Group, load_all
from console.chat.panels import stream_panel
from console.chat.sdk_client import stream_response
from console.chat.sources import resolve_files, resolve_with_meta
from console.config import get_config

router = APIRouter()
templates = Jinja2Templates(
    directory=str(Path(__file__).parent.parent / "web" / "templates")
)


def _load() -> tuple[dict[str, DomainAgent], list[Group]]:
    return load_all(get_config().domain_agents_dir)


def _agent_count(groups: list[Group]) -> int:
    return sum(len(g.agents) for g in groups)


@router.get("/", response_class=HTMLResponse)
async def landing(request: Request):
    cfg = get_config()
    _, groups = _load()
    return templates.TemplateResponse(
        request,
        "index.html",
        {"config": cfg, "agent_count": _agent_count(groups)},
    )


@router.get("/agents", response_class=HTMLResponse)
async def agents_index(request: Request):
    cfg = get_config()
    _, groups = _load()
    return templates.TemplateResponse(
        request,
        "agents_index.html",
        {"config": cfg, "groups": groups},
    )


def _agent_detail(agent: DomainAgent, cfg, extra_patterns: list[str] | None = None) -> dict:
    patterns = list(extra_patterns or []) + list(agent.sources)
    files = resolve_files(cfg.repo_root, patterns)
    return {
        "agent": agent,
        "sources": [str(p.relative_to(cfg.repo_root)) for p in files],
        "system_prompt": agent.system_prompt,
    }


@router.get("/agents/{name}", response_class=HTMLResponse)
async def agent_chat_page(request: Request, name: str):
    agents, _ = _load()
    agent = agents.get(name)
    if agent is None or agent.is_system:
        raise HTTPException(404, f"Domain agent '{name}' not found")
    cfg = get_config()
    members = (
        [agents[m] for m in agent.members if m in agents] if agent.is_panel else []
    )
    detail = _agent_detail(agent, cfg) if not agent.is_panel else None
    panel_detail = _agent_detail(agent, cfg) if agent.is_panel else None
    member_details = (
        [_agent_detail(m, cfg, extra_patterns=agent.sources) for m in members]
        if agent.is_panel
        else []
    )
    return templates.TemplateResponse(
        request,
        "chat.html",
        {
            "config": cfg,
            "agent": agent,
            "members": members,
            "detail": detail,
            "panel_detail": panel_detail,
            "member_details": member_details,
        },
    )


class StreamBody(BaseModel):
    history: list[dict]
    message: str


def _format_prompt(history: list[dict], latest: str) -> str:
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


@router.post("/agents/{name}/stream")
async def agent_stream(name: str, body: StreamBody):
    agents, _ = _load()
    agent = agents.get(name)
    if agent is None or agent.is_system:
        raise HTTPException(404, f"Domain agent '{name}' not found")

    cfg = get_config()
    prompt = _format_prompt(body.history, body.message)

    async def event_stream() -> AsyncIterator[str]:
        try:
            if agent.is_panel:
                async for evt in stream_panel(
                    panel=agent,
                    members=agents,
                    user_message=prompt,
                    config=cfg,
                ):
                    yield _sse(evt)
            else:
                resolved = resolve_with_meta(cfg.repo_root, agent.sources)
                system = (
                    agent.system_prompt
                    + "\n\n===== GROUNDING SOURCES =====\n"
                    + resolved.text
                )
                for w in resolved.warnings:
                    yield _sse({"type": "warning", "message": w})
                yield _sse(
                    {"type": "speaker", "name": agent.name, "title": agent.title}
                )
                async for token in stream_response(
                    system_prompt=system,
                    user_message=prompt,
                    model=agent.model,
                ):
                    yield _sse({"type": "token", "text": token})
                yield _sse({"type": "speaker_done", "name": agent.name})
                yield _sse({"type": "done"})
        except Exception as e:
            yield _sse({"type": "error", "message": str(e)})

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
