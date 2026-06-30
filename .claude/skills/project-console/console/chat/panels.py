from typing import AsyncIterator

from console.chat.domain_agents import DomainAgent
from console.chat.sdk_client import collect_response, stream_response
from console.chat.sources import resolve_with_meta
from console.config import Config


MAX_LLM_TURNS = 6


def _panel_framing(panel: DomainAgent) -> str:
    """Generic, project-agnostic wrapper for a panel member's turn.

    What KIND of panel this is and how members should interact comes from the
    panel's OWN body (injected as THIS PANEL below) — never hardcoded here, so
    a KOL clinical panel, a cross-functional core-team panel, and a red-team
    buyer committee each read correctly. This wrapper only guarantees the
    mechanics every panel turn needs, regardless of panel type.
    """
    return (
        f"You are participating as one member of the {panel.title}. "
        "Speak in the first person and stay in character as the persona "
        "described under YOUR ROLE below — draw only on that persona's "
        "expertise and remit. Keep your contribution focused (about three to "
        "six sentences); the other panelists each speak in turn, so make your "
        "own point and leave theirs to them.\n\n"
    )


def build_member_system_prompt(
    panel: DomainAgent,
    member: DomainAgent,
    config: Config,
) -> tuple[str, list[str]]:
    resolved = resolve_with_meta(
        config.repo_root,
        list(panel.sources) + list(member.sources),
    )
    panel_body = panel.system_prompt.strip()
    panel_context = (
        f"===== THIS PANEL: {panel.title} =====\n{panel_body}\n\n"
        if panel_body
        else ""
    )
    prompt = (
        _panel_framing(panel)
        + panel_context
        + "===== YOUR ROLE =====\n"
        + member.system_prompt
        + "\n\n===== GROUNDING SOURCES =====\n"
        + resolved.text
    )
    return prompt, resolved.warnings


async def _run_member(
    member: DomainAgent,
    panel: DomainAgent,
    config: Config,
    user_message: str,
    transcript_so_far: str,
) -> AsyncIterator[dict]:
    system, warnings = build_member_system_prompt(panel, member, config)
    for w in warnings:
        yield {"type": "warning", "message": f"[{member.name}] {w}"}
    yield {"type": "speaker", "name": member.name, "title": member.title}
    prompt = user_message
    if transcript_so_far:
        prompt = (
            "Conversation so far in this panel turn:\n"
            + transcript_so_far
            + "\n\nNow respond to the user message:\n"
            + user_message
        )
    async for token in stream_response(
        system_prompt=system,
        user_message=prompt,
        model=member.model or panel.model,
        subagents=member.subagents,
    ):
        yield {"type": "token", "text": token}
    yield {"type": "speaker_done", "name": member.name}


async def _llm_pick_next(
    panel: DomainAgent,
    members: dict[str, DomainAgent],
    user_message: str,
    transcript_so_far: str,
    spoken: list[str],
) -> str | None:
    candidates = [members[m] for m in panel.members if m in members]
    roster = "\n".join(
        f"- {m.name}: {m.title} — {m.description}" for m in candidates
    )
    spoken_line = (
        f"Already spoke this turn: {', '.join(spoken)}" if spoken else "No one has spoken yet."
    )
    moderator_system = (
        "You are the silent moderator of a clinical advisory panel. "
        "Given the user's question, the conversation so far, and the panel roster, "
        "decide which single panelist should speak next to add the most value. "
        "Prefer voices that have not yet spoken unless a follow-up is clearly needed. "
        "Reply with EXACTLY one panelist name from the roster, or the word DONE if "
        "the panel has covered the question well enough to stop. No other text."
    )
    prompt = (
        f"User question:\n{user_message}\n\n"
        f"{spoken_line}\n\n"
        f"Conversation so far:\n{transcript_so_far or '(none yet)'}\n\n"
        f"Panel roster:\n{roster}\n\n"
        "Next speaker (name only) or DONE:"
    )
    reply = (await collect_response(
        system_prompt=moderator_system,
        user_message=prompt,
        model=panel.model,
        enable_read_files=False,
        enable_file_locator=False,
    )).strip()
    first = reply.splitlines()[0].strip().strip(".").strip()
    if first.upper().startswith("DONE"):
        return None
    for m in candidates:
        if m.name == first or m.title == first:
            return m.name
    for m in candidates:
        if m.name in reply or m.title in reply:
            return m.name
    return None


async def stream_panel(
    *,
    panel: DomainAgent,
    members: dict[str, DomainAgent],
    user_message: str,
    config: Config,
) -> AsyncIterator[dict]:
    moderator = (panel.moderator or "round-robin").lower()
    if moderator == "llm":
        async for evt in _stream_panel_llm(panel, members, user_message, config):
            yield evt
    else:
        async for evt in _stream_panel_round_robin(panel, members, user_message, config):
            yield evt


async def _stream_panel_round_robin(
    panel: DomainAgent,
    members: dict[str, DomainAgent],
    user_message: str,
    config: Config,
) -> AsyncIterator[dict]:
    for member_name in panel.members:
        member = members.get(member_name)
        if member is None:
            yield {"type": "error", "message": f"Panel member '{member_name}' not found"}
            continue
        async for evt in _run_member(member, panel, config, user_message, ""):
            yield evt
    yield {"type": "done"}


async def _stream_panel_llm(
    panel: DomainAgent,
    members: dict[str, DomainAgent],
    user_message: str,
    config: Config,
) -> AsyncIterator[dict]:
    spoken: list[str] = []
    transcript: list[str] = []
    for _ in range(MAX_LLM_TURNS):
        next_name = await _llm_pick_next(
            panel, members, user_message, "\n\n".join(transcript), spoken
        )
        if next_name is None:
            break
        member = members.get(next_name)
        if member is None:
            yield {"type": "error", "message": f"Moderator picked unknown member '{next_name}'"}
            break
        member_buffer: list[str] = []
        async for evt in _run_member(
            member, panel, config, user_message, "\n\n".join(transcript)
        ):
            if evt.get("type") == "token":
                member_buffer.append(evt["text"])
            yield evt
        spoken.append(member.name)
        transcript.append(f"{member.title}: {''.join(member_buffer).strip()}")
    yield {"type": "done"}
