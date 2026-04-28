from pathlib import Path
from typing import AsyncIterator

from console.chat.sdk_client import stream_response

SUMMARY_SYSTEM = """You are a concise technical summarizer for documents in a MedTech (medical device) project's Design History File (DHF). Your job is to produce a short, accurate summary of the document provided.

Guidelines:
- Start with a one-sentence statement of what the document is.
- Follow with 2-4 bullet points covering the key content, decisions, or data.
- If the document references a specific device (e.g., PROJECT), standard (ISO/IEC), or regulation, mention it.
- Keep the total under 150 words.
- Do not invent details. If the document is short or has little content, say so and be brief.
- Do not wrap the response in code fences.
"""

MAX_DOC_BYTES = 80_000


async def summarize(path: Path) -> AsyncIterator[str]:
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        content = "[could not read file as text]"
    if len(content) > MAX_DOC_BYTES:
        content = content[:MAX_DOC_BYTES] + "\n\n[... truncated ...]"
    prompt = (
        f"Document path: {path.name}\n\n"
        f"Document content:\n\n{content}\n\n"
        f"Produce the summary now."
    )
    async for token in stream_response(
        system_prompt=SUMMARY_SYSTEM,
        user_message=prompt,
    ):
        yield token
