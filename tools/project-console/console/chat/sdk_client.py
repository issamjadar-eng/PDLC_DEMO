from typing import AsyncIterator

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    StreamEvent,
    TextBlock,
    query,
)


async def stream_response(
    *,
    system_prompt: str,
    user_message: str,
    model: str | None = None,
) -> AsyncIterator[str]:
    """Yield text deltas as they arrive from the Agent SDK.

    Uses ``include_partial_messages=True`` so the SDK emits ``StreamEvent``
    objects wrapping raw Anthropic API stream events. We extract text from
    ``content_block_delta`` events (for streaming text chunks). The final
    ``AssistantMessage`` is ignored to avoid duplicating text that already
    arrived via deltas.
    """
    options = ClaudeAgentOptions(
        system_prompt=system_prompt,
        model=model,
        include_partial_messages=True,
    )
    got_any_delta = False
    async for msg in query(prompt=user_message, options=options):
        if isinstance(msg, StreamEvent):
            evt = msg.event or {}
            etype = evt.get("type")
            if etype == "content_block_delta":
                delta = evt.get("delta") or {}
                if delta.get("type") == "text_delta":
                    text = delta.get("text") or ""
                    if text:
                        got_any_delta = True
                        yield text
        elif isinstance(msg, AssistantMessage) and not got_any_delta:
            # Fallback: no deltas arrived (older CLI, or partial messages
            # disabled upstream) — yield the full block text as one chunk.
            for block in msg.content:
                if isinstance(block, TextBlock) and block.text:
                    yield block.text


async def collect_response(
    *,
    system_prompt: str,
    user_message: str,
    model: str | None = None,
) -> str:
    parts: list[str] = []
    async for token in stream_response(
        system_prompt=system_prompt, user_message=user_message, model=model
    ):
        parts.append(token)
    return "".join(parts)
