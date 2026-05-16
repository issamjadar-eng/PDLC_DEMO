"""stdio MCP server exposing the `locate` tool.

Reads the committed index at `tools/file-locator-mcp/index.db`, ranks hits via
blended BM25 + cosine-similarity scoring (weights from project.yml), returns
confidence-banded results.

No network I/O. Embedding model runs locally via fastembed/ONNX. No LLM calls.
"""
from __future__ import annotations

import asyncio
import json
import math
import sqlite3
import sys
from pathlib import Path
from typing import Any

# Resolve common.py relative to this script.
sys.path.insert(0, str(Path(__file__).parent))

from common import LocatorConfig, load_config  # noqa: E402


# ─── Embedding + ranking ────────────────────────────────────────────────────

_MODEL_CACHE: dict[str, Any] = {}


def _embed_query(cfg: LocatorConfig, query: str) -> list[float]:
    from fastembed import TextEmbedding  # type: ignore
    model = _MODEL_CACHE.get(cfg.embedding_model)
    if model is None:
        model = TextEmbedding(model_name=cfg.embedding_model)
        _MODEL_CACHE[cfg.embedding_model] = model
    return next(model.embed([query])).tolist()


def _cosine(a: list[float], b: list[float]) -> float:
    if len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def _decode_embedding(blob: bytes, dim: int) -> list[float]:
    import struct
    return list(struct.unpack(f"{dim}f", blob))


# ─── Search ────────────────────────────────────────────────────────────────

def locate(
    cfg: LocatorConfig,
    query: str,
    k: int = 10,
    scope: str = "all",
    min_score: float = 0.0,
) -> dict[str, Any]:
    """Run a locator query. Returns the response dict per task 193 P1 spec."""
    if scope not in {"docs", "code", "all"}:
        return {
            "query": query,
            "hits": {"high_confidence": [], "partial_match": [], "likely_irrelevant": []},
            "total_corpus_size": 0,
            "reasoning_hint": f"invalid scope '{scope}' — use 'docs', 'code', or 'all'",
        }
    if scope == "code":
        # v1 ships docs-only; reserve scope=code for v2.
        return {
            "query": query,
            "hits": {"high_confidence": [], "partial_match": [], "likely_irrelevant": []},
            "total_corpus_size": 0,
            "reasoning_hint": "code scope not enabled in v1 — only docs are indexed",
        }

    if not cfg.index_path.exists():
        return {
            "query": query,
            "hits": {"high_confidence": [], "partial_match": [], "likely_irrelevant": []},
            "total_corpus_size": 0,
            "reasoning_hint": (
                f"index not found at {cfg.index_path}. "
                "Run /file-locator rebuild first."
            ),
        }

    conn = sqlite3.connect(cfg.index_path)
    conn.row_factory = sqlite3.Row

    total = conn.execute("SELECT COUNT(*) FROM indexed_files WHERE kind='doc'").fetchone()[0]
    if total == 0:
        conn.close()
        return {
            "query": query,
            "hits": {"high_confidence": [], "partial_match": [], "likely_irrelevant": []},
            "total_corpus_size": 0,
            "reasoning_hint": "index is empty — run /file-locator rebuild",
        }

    # BM25 candidates via FTS5 — take a wider net than k to allow re-ranking.
    fts_query = _to_fts_query(query)
    fts_rows = conn.execute(
        """SELECT s.rowid, s.path, s.heading_anchor, s.summary_text, s.embedding,
                  s.estimated_tokens, bm25(summaries_fts) AS bm25_raw
           FROM summaries_fts JOIN summaries s ON summaries_fts.rowid = s.rowid
           WHERE summaries_fts MATCH ?
           ORDER BY bm25_raw LIMIT ?""",
        (fts_query, max(k * 5, 50)),
    ).fetchall()

    # Re-rank with blended score.
    query_emb = _embed_query(cfg, query)
    bm25_max = max((-r["bm25_raw"] for r in fts_rows), default=0.0) or 1.0

    scored: list[dict[str, Any]] = []
    for row in fts_rows:
        emb = _decode_embedding(row["embedding"], cfg.embedding_dimension)
        cos = max(0.0, _cosine(query_emb, emb))
        bm25_norm = min(1.0, (-row["bm25_raw"]) / bm25_max)
        blended = cfg.embedding_weight * cos + cfg.bm25_weight * bm25_norm
        if blended < min_score:
            continue
        scored.append({
            "path": row["path"],
            "heading_anchor": row["heading_anchor"],
            "summary": row["summary_text"],
            "score": round(blended, 4),
            "embedding_cosine": round(cos, 4),
            "bm25_normalized": round(bm25_norm, 4),
            "estimated_tokens": row["estimated_tokens"],
            "kind": "doc",
        })

    # Collapse: if both a file-level and a sub-summary hit for the same path appear,
    # keep whichever scores higher (per granularity decision in P1).
    scored.sort(key=lambda h: h["score"], reverse=True)
    seen_paths: dict[str, dict[str, Any]] = {}
    for hit in scored:
        existing = seen_paths.get(hit["path"])
        if existing is None or hit["score"] > existing["score"]:
            seen_paths[hit["path"]] = hit
    hits = list(seen_paths.values())
    hits.sort(key=lambda h: h["score"], reverse=True)
    hits = hits[:k]

    # Band the hits.
    banded = {"high_confidence": [], "partial_match": [], "likely_irrelevant": []}
    for hit in hits:
        if hit["score"] >= cfg.band_high:
            hit["banding_reason"] = "score above high-confidence threshold"
            banded["high_confidence"].append(hit)
        elif hit["score"] >= cfg.band_partial:
            hit["banding_reason"] = "score in partial-match range"
            banded["partial_match"].append(hit)
        else:
            hit["banding_reason"] = "score below partial-match threshold"
            banded["likely_irrelevant"].append(hit)

    conn.close()
    return {
        "query": query,
        "hits": banded,
        "total_corpus_size": total,
        "reasoning_hint": _reasoning_hint(banded),
    }


def _to_fts_query(query: str) -> str:
    """Tokenize a natural-language query into an FTS5 query.

    Strips punctuation, splits on whitespace, joins with OR so any term hit
    contributes. Embeddings handle the semantic side; BM25 handles the lexical.
    """
    import re
    tokens = re.findall(r"[a-zA-Z0-9_]{2,}", query.lower())
    if not tokens:
        return '""'
    return " OR ".join(tokens)


def _reasoning_hint(banded: dict[str, list]) -> str:
    high = banded["high_confidence"]
    partial = banded["partial_match"]
    if len(high) == 1 and len(partial) == 0:
        return "single dominant hit — read it and stop"
    if len(high) >= 3:
        return "multiple high-confidence hits — likely multi-source question, read all"
    if len(high) == 0 and len(partial) == 0:
        return "no hits above partial-match threshold — rephrase or broaden the query"
    if len(high) == 0:
        return "no high-confidence hits — read top partial-match and confirm relevance"
    return "clear top hit with supporting partial matches — read top then descend"


# ─── MCP server ─────────────────────────────────────────────────────────────

async def run_server() -> None:
    from mcp.server import Server  # type: ignore
    from mcp.server.stdio import stdio_server  # type: ignore
    from mcp.types import TextContent, Tool  # type: ignore

    cfg = load_config()
    server: Server = Server("file-locator")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name="locate",
                description=(
                    "Semantic file-locator over the medtech project corpus. "
                    "Returns ranked (path, summary, heading_anchor?, score) hits "
                    "banded by confidence. Use for 'where is X discussed' / "
                    "'find files about Y' queries. Read the top-banded hit first; "
                    "stop when answered; cap at 3 reads unless multi-source."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Natural-language query."},
                        "k": {"type": "integer", "default": 10, "minimum": 1, "maximum": 50},
                        "scope": {
                            "type": "string",
                            "enum": ["docs", "code", "all"],
                            "default": "all",
                            "description": "v1: 'code' returns empty + hint.",
                        },
                        "min_score": {
                            "type": "number",
                            "default": 0.0,
                            "minimum": 0.0,
                            "maximum": 1.0,
                            "description": "Filter hits below this blended score.",
                        },
                    },
                    "required": ["query"],
                },
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
        if name != "locate":
            return [TextContent(type="text", text=json.dumps({"error": f"unknown tool: {name}"}))]
        result = locate(
            cfg,
            query=arguments.get("query", ""),
            k=int(arguments.get("k", 10)),
            scope=arguments.get("scope", "all"),
            min_score=float(arguments.get("min_score", 0.0)),
        )
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


def main() -> int:
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
