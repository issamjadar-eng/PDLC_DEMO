from typing import AsyncIterator

from console.chat.domain_agents import DomainAgent
from console.chat.sdk_client import stream_response
from console.chat.sources import resolve
from console.config import Config


PANEL_FRAMING = (
    "You are participating as a member of a clinical advisory panel reviewing "
    "a patient-controlled analgesia (PCA) infusion device. Speak in first "
    "person, stay in character as the KOL described below, and draw only on "
    "that KOL's expertise. Keep your contribution focused — three to six "
    "sentences — since other panelists will speak in turn.\n\n"
)


def build_member_system_prompt(
    panel: DomainAgent,
    member: DomainAgent,
    config: Config,
) -> str:
    sources_text = resolve(
        config.repo_root,
        list(panel.sources) + list(member.sources),
    )
    return (
        PANEL_FRAMING
        + member.system_prompt
        + "\n\n===== GROUNDING SOURCES =====\n"
        + sources_text
    )


async def stream_panel(
    *,
    panel: DomainAgent,
    members: dict[str, DomainAgent],
    user_message: str,
    config: Config,
) -> AsyncIterator[dict]:
    for member_name in panel.members:
        member = members.get(member_name)
        if member is None:
            yield {
                "type": "error",
                "message": f"Panel member '{member_name}' not found",
            }
            continue
        yield {"type": "speaker", "name": member.name, "title": member.title}
        system = build_member_system_prompt(panel, member, config)
        async for token in stream_response(
            system_prompt=system,
            user_message=user_message,
            model=member.model or panel.model,
        ):
            yield {"type": "token", "text": token}
        yield {"type": "speaker_done", "name": member.name}
    yield {"type": "done"}
