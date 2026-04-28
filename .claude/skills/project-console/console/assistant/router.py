"""Unified Assistant drawer routes.

GET  /assistant/api/agents              — JSON list of non-system solo domain agents
POST /assistant/chat/stream             — SSE chat endpoint used by the generic drawer
GET  /assistant/api/index/status        — index stats + missing-README warnings
POST /assistant/api/index/rebuild       — rebuild the README index on demand

The drawer is mounted on any console page via the
`_assistant_drawer.html` partial. The page hands the drawer a default
agent, an allowed-agents list, and a grounding URL. The drawer fetches
the grounding content, POSTs `{agent_name, grounding_text, history,
message}` here, and receives `data: {type: token|done|error, ...}` SSE
frames which it renders into the active thread.

Chat memory is not stored server-side — the browser owns it in
localStorage and sends the full history with every request.

Grounding architecture (task 099 Phase 2):
  - Tier 1 Focus   : page-supplied grounding_text (doc body / sidecar)
  - Tier 2 Core    : agent's `core:` list (files/folders/globs) concatenated
  - Tier 3 Index   : shared README tree (`docs/**/README.md` concatenated)
  - Tool           : `read_files(paths)` for on-demand fetch (see sdk_client.py)

Caps are model-aware — resolved per-request from
`config.caps_for_model(effective_model)`. The index itself is not capped
(it's ~200-300 KB on a well-organized project and well inside the Sonnet
context window); cap-trimming applies to the Core and Focus tiers only.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import AsyncIterator

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel

from console.chat.domain_agents import DomainAgent, load_all
from console.chat.index_builder import (
    IndexResult,
    build_index,
    concatenate_files,
    resolve_core,
)
from console.chat.sdk_client import stream_response
from console.config import get_config

router = APIRouter()


# ---------- cached README index ----------
# Rebuilt at startup (via app startup hook) and on POST /rebuild.
# Stored in module state; simple invalidation.

_INDEX_CACHE: IndexResult | None = None


def _ensure_index() -> IndexResult:
    global _INDEX_CACHE
    if _INDEX_CACHE is None:
        _INDEX_CACHE = build_index(get_config().repo_root)
    return _INDEX_CACHE


def invalidate_index() -> IndexResult:
    global _INDEX_CACHE
    _INDEX_CACHE = build_index(get_config().repo_root)
    return _INDEX_CACHE


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


@router.get("/assistant/api/index/status")
async def index_status() -> JSONResponse:
    idx = _ensure_index()
    return JSONResponse(
        {
            "readme_count": idx.readme_count,
            "total_bytes": idx.total_bytes,
            "missing_readme_folders": idx.missing_readme_folders,
        }
    )


@router.post("/assistant/api/index/rebuild")
async def index_rebuild() -> JSONResponse:
    idx = invalidate_index()
    return JSONResponse(
        {
            "readme_count": idx.readme_count,
            "total_bytes": idx.total_bytes,
            "missing_readme_folders": idx.missing_readme_folders,
        }
    )


class AssistantStreamBody(BaseModel):
    agent_name: str
    history: list[dict]
    message: str
    grounding_text: str | None = None
    grounding_label: str | None = None


_DISCOVERY_RUBRIC = """\
===== DISCOVERY RUBRIC =====

Before answering, work through these steps:

1. Read your CORE documents in full (already in this system prompt).
2. Scan the INDEX below — it is every folder's README in tree order.
   Each entry describes scope, expected content, and conventions.
3. If any folder's description might relate to the question, call the
   tool `read_files(paths=[...])` to fetch specific .md files from that
   folder. A path can be:
     - a specific .md file:  docs/project/dhfs/.../some-doc.md
     - a folder path:        docs/project/dhfs/.../architecture/
       (folder paths expand to the folder's README + direct-child .md files)
   Batch multiple paths into a single call when you can; it halves turns.
4. Prefer over-fetching. The cost of missing context is worse than the
   cost of an extra read. When in doubt, fetch.
5. Only answer once you have reviewed every possibly-relevant doc.

===== CITATION FORMAT (required) =====

Cite every factual claim with a numbered footnote. Use this exact
format so the console can render each footnote as a clickable link to
the source document:

  - Inline:  write "[1]", "[2]", etc. directly after the sentence that
             draws from the source. Multiple citations in one sentence
             are fine: "per Section 3 [1][3]".
  - Footnotes: at the very end of your response, list every cited
               source on its own line:

                 [1]: docs/project/dhfs/.../hiplink-system-sad.md
                 [2]: docs/project/dhfs/.../architecture/README.md
                 [3]: docs/project/strategies/architecture-strategy.md

When you can identify a specific section you drew from, append a
GitHub-style heading anchor (lowercase, spaces→dashes, punctuation
stripped):

                 [4]: docs/.../hiplink-system-sad.md#module-boundaries

Rules:
  - Every `[N]` inline MUST have a matching `[N]:` footnote at the end.
  - Every footnote path MUST be a path you actually read (via CORE,
    INDEX, or a read_files call) — never a guess.
  - Don't invent footnotes to pad the response. If you answered from
    knowledge not in the provided grounding, say so explicitly rather
    than attaching a spurious citation.

===== EXTERNAL STANDARDS & GUIDANCE — MANDATORY GROUNDING =====

When your answer references, invokes, or relies on a named regulatory
standard or FDA/industry guidance document — IEC 62304, IEC 62366,
ISO 14971, ISO 13485, IEC 81001-5-1, 21 CFR Part 820, 510(k), PCCP,
SaMD, CDS, GMLP, DICOM, HL7 FHIR, NIST CSF, AAMI TIR, etc. — regulatory
content lives in TWO LAYERS. You must check BOTH and cite BOTH.

Layer 1 — Applicability analysis (per-project, device-specific):
  - docs/external/standards/<name>.md            IEC/ISO applicability
  - docs/external/fda-guidance/<name>.md         FDA guidance applicability
  - docs/external/industry-frameworks/<name>.md  framework adoption rationale

  These files answer "how does this standard apply to THIS device?" —
  module mapping, deferred-to-QMS clauses, [VERIFY] calls, gap notes.

Layer 2 — Source distillation (shared across projects):
  - .claude/skills/medtech-docs/references/standards/<name>.md
  - .claude/skills/medtech-docs/references/fda-guidance/<name>.md
  - .claude/skills/medtech-docs/references/industry-frameworks/<name>.md
  - .claude/skills/dhf-manifest/data/tier1-regulatory/<name>.md

  These files answer "what does the standard actually say?" — clause-
  level distillation, obligations, cross-references. They are device-
  agnostic upstream reference material.

Your workflow when a named standard appears:

  1. Fetch Layer-1 applicability file via `read_files` — start here to
     see what this program has decided about the standard.

  2. Fetch Layer-2 source distillation via `read_files` for clause-
     level content the applicability file is analyzing against.

  3. Cite BOTH in footnotes, applicability first, source second:
       [1]: docs/external/standards/iec-62304-software-lifecycle.md
       [2]: .claude/skills/medtech-docs/references/standards/iec-62304.md

  4. Training knowledge of what "IEC 62304 says" is strictly inferior
     to the Layer-2 source file. Never cite training data when a
     Layer-2 file exists.

  5. If Layer-1 (applicability) is missing or thin, say so — that's a
     gap for the team to close, not one for you to paper over with
     training knowledge.

  6. If Layer-2 (source) is missing for a specific standard you need
     (rare — the skill library is comprehensive), acknowledge it
     explicitly rather than inventing a citation.

This rule applies whether the standard appears in the user's question
or in your own reasoning as justification. A response that invokes
"per IEC 62304 §5.3" without both a Layer-1 and a Layer-2 footnote is
incomplete.
"""


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
    core_text: str,
    index_text: str,
    grounding_cap_bytes: int,
) -> str:
    """Compose the agent's system prompt with tiered grounding.

    Order:
      1. Agent persona (the agent's own system_prompt body)
      2. Tier 2 CORE — agent's declared core .md files, in full
      3. Discovery rubric — instructs the agent to scan the INDEX and
         use read_files() on demand
      4. Tier 3 INDEX — README tree
      5. Tier 1 FOCUS — page-supplied grounding (last word; steers the
         current question without overriding agent persona)
    """
    parts = [agent.system_prompt]

    if core_text:
        parts.append("===== CORE GROUNDING =====")
        parts.append(core_text)

    parts.append(_DISCOVERY_RUBRIC)

    if index_text:
        parts.append("===== INDEX (folder READMEs) =====")
        parts.append(index_text)

    if grounding_text:
        capped = grounding_text[:grounding_cap_bytes]
        if len(grounding_text) > grounding_cap_bytes:
            capped += f"\n\n[...truncated at {grounding_cap_bytes} bytes]"
        label = grounding_label or "PAGE CONTEXT"
        parts.append(f"===== {label} (current focus) =====")
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
        raise HTTPException(
            400,
            f"Agent '{body.agent_name}' is a panel; panels are not supported "
            "by the generic assistant drawer yet.",
        )

    cfg = get_config()
    effective_model = cfg.resolve_model(agent.model)
    caps = cfg.caps_for_model(effective_model)
    core_cap_bytes = caps["source_cap_kb"] * 1024
    grounding_cap_bytes = caps["grounding_cap_kb"] * 1024

    # Resolve agent's Tier 2 core. `core` includes the agent's declared
    # entries (or legacy `sources:` via backwards-compat shim).
    core_paths = resolve_core(cfg.repo_root, agent.core)
    core_text = concatenate_files(cfg.repo_root, core_paths)
    core_truncated = False
    if len(core_text) > core_cap_bytes:
        core_text = core_text[:core_cap_bytes] + (
            f"\n\n[... core truncated at {core_cap_bytes} bytes; "
            f"total was {len(core_text)} bytes ...]"
        )
        core_truncated = True

    # Tier 3 index (cached).
    idx = _ensure_index()

    system = _build_system_prompt(
        agent=agent,
        grounding_text=body.grounding_text,
        grounding_label=body.grounding_label,
        core_text=core_text,
        index_text=idx.text,
        grounding_cap_bytes=grounding_cap_bytes,
    )
    prompt = _format_prompt(body.history, body.message)

    async def event_stream() -> AsyncIterator[str]:
        try:
            # Pre-flight info: number of core files + index size. Helpful for
            # debugging grounding decisions.
            yield _sse({
                "type": "info",
                "message": (
                    f"Core: {len(core_paths)} file(s), {len(core_text)//1024} KB"
                    + (f" (truncated from orig)" if core_truncated else "")
                    + f"; Index: {idx.readme_count} READMEs, {idx.total_bytes//1024} KB"
                ),
            })
            if core_truncated:
                yield _sse({
                    "type": "warning",
                    "message": (
                        f"Core grounding exceeded {core_cap_bytes//1024} KB cap. "
                        f"Consider tightening this agent's `core:` list; the rest "
                        f"of the project is still reachable via read_files()."
                    ),
                })
            if idx.missing_readme_folders:
                yield _sse({
                    "type": "warning",
                    "message": (
                        f"Index has {len(idx.missing_readme_folders)} folder(s) "
                        f"with content but no README.md: "
                        f"{', '.join(idx.missing_readme_folders[:3])}"
                        + ("..." if len(idx.missing_readme_folders) > 3 else "")
                    ),
                })
            async for token in stream_response(
                system_prompt=system,
                user_message=prompt,
                model=agent.model,
                enable_read_files=True,
                max_turns=15,
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
