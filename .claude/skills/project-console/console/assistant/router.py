"""Unified Assistant drawer routes.

GET  /assistant/api/agents              — JSON list of non-system solo domain agents
POST /assistant/chat/stream             — SSE chat endpoint used by the generic drawer

The drawer is mounted on any console page via the
`_assistant_drawer.html` partial. The page hands the drawer a default
agent, an allowed-agents list, and a grounding URL. The drawer fetches
the grounding content, POSTs `{agent_name, grounding_text, history,
message}` here, and receives `data: {type: token|done|error, ...}` SSE
frames which it renders into the active thread.

Chat memory is not stored server-side — the browser owns it in
localStorage and sends the full history with every request.

Grounding input is capped at GROUNDING_CAP bytes (80 KB) to protect
against accidental context-window overflow on large documents.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import AsyncIterator

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel

from console.chat.domain_agents import DomainAgent, load_all
from console.chat.sdk_client import stream_response
from console.chat.sources import resolve_with_meta
from console.config import get_config

router = APIRouter()

# Hard cap on page-supplied grounding text — matches the documents summary cap.
GROUNDING_CAP = 80 * 1024


def _load_agents() -> dict[str, DomainAgent]:
    agents, _ = load_all(get_config().agents_dir)
    return agents


def _public_agents(agents: dict[str, DomainAgent]) -> list[DomainAgent]:
    """Solo, non-system agents — the set exposed to the drawer picker."""
    return [a for a in agents.values() if not a.is_system and not a.is_panel]


@router.get("/assistant/api/agents")
async def list_agents() -> JSONResponse:
    agents = _load_agents()
    payload = [
        {
            "name": a.name,
            "title": a.title,
            "group": a.group or "",
            "description": a.description,
        }
        for a in sorted(_public_agents(agents), key=lambda x: (x.group or "", x.title))
    ]
    return JSONResponse({"agents": payload})


class AssistantStreamBody(BaseModel):
    agent_name: str
    history: list[dict]
    message: str
    grounding_text: str | None = None
    grounding_label: str | None = None


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


def _build_system_prompt(
    agent: DomainAgent,
    grounding_text: str | None,
    grounding_label: str | None,
    agent_sources_text: str,
) -> str:
    """Compose the agent's own system prompt with grounding data.

    Order: agent system prompt → agent's own resolved sources (if any) →
    page-supplied grounding (doc body, sidecar rendition, etc.).
    Page-supplied grounding wins the last word so it can steer the
    current question without retraining the agent's voice.
    """
    parts = [agent.system_prompt]

    if agent_sources_text:
        parts.append("===== AGENT GROUNDING SOURCES =====")
        parts.append(agent_sources_text)

    if grounding_text:
        capped = grounding_text[:GROUNDING_CAP]
        if len(grounding_text) > GROUNDING_CAP:
            capped += f"\n\n[...truncated at {GROUNDING_CAP} bytes]"
        label = grounding_label or "PAGE CONTEXT"
        parts.append(f"===== {label} =====")
        parts.append(capped)

    return "\n\n".join(parts)


def _sse(event: dict) -> str:
    return f"data: {json.dumps(event)}\n\n"


@router.post("/assistant/chat/stream")
async def assistant_chat_stream(body: AssistantStreamBody):
    agents = _load_agents()
    agent = agents.get(body.agent_name)
    if agent is None:
        raise HTTPException(404, f"Agent '{body.agent_name}' not found")
    if agent.is_system:
        raise HTTPException(400, f"Agent '{body.agent_name}' is not exposable")
    if agent.is_panel:
        # Panel streaming is richer than the generic drawer supports (v1).
        raise HTTPException(
            400,
            f"Agent '{body.agent_name}' is a panel; panels are not supported "
            "by the generic assistant drawer yet.",
        )

    cfg = get_config()
    resolved = resolve_with_meta(cfg.repo_root, agent.sources)

    system = _build_system_prompt(
        agent=agent,
        grounding_text=body.grounding_text,
        grounding_label=body.grounding_label,
        agent_sources_text=resolved.text,
    )
    prompt = _format_prompt(body.history, body.message)

    async def event_stream() -> AsyncIterator[str]:
        try:
            for w in resolved.warnings:
                yield _sse({"type": "warning", "message": w})
            async for token in stream_response(
                system_prompt=system,
                user_message=prompt,
                model=agent.model,
            ):
                yield _sse({"type": "token", "text": token})
            yield _sse({"type": "done"})
        except Exception as e:
            yield _sse({"type": "error", "message": str(e)})

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
