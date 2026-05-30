"""Markdown indexer for file-locator.

Walks the corpus, applies the 4 inclusion gates (via common.walk_corpus),
extracts file-level + sub-summaries, generates embeddings, and writes to
SQLite incrementally — only changed files are re-embedded.
"""
from __future__ import annotations

import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from common import (
    ExtractedSummary,
    LocatorConfig,
    SubSummary,
    content_hash,
    extract_summary,
    walk_corpus,
)


SCHEMA = """
CREATE TABLE IF NOT EXISTS metadata (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS indexed_files (
    path             TEXT PRIMARY KEY,
    content_hash     TEXT NOT NULL,
    size_bytes       INTEGER NOT NULL,
    mtime            REAL NOT NULL,
    indexed_at       REAL NOT NULL,
    summary_method   TEXT NOT NULL,
    kind             TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS summaries (
    path             TEXT NOT NULL,
    heading_anchor   TEXT,                     -- NULL for file-level summary
    summary_text     TEXT NOT NULL,
    embedding        BLOB NOT NULL,            -- float32[dim]
    estimated_tokens INTEGER NOT NULL,
    PRIMARY KEY (path, heading_anchor),
    FOREIGN KEY (path) REFERENCES indexed_files(path) ON DELETE CASCADE
);

CREATE VIRTUAL TABLE IF NOT EXISTS summaries_fts USING fts5(
    summary_text,
    path UNINDEXED,
    heading_anchor UNINDEXED,
    content='summaries',
    content_rowid='rowid'
);

CREATE TRIGGER IF NOT EXISTS summaries_ai AFTER INSERT ON summaries BEGIN
    INSERT INTO summaries_fts(rowid, summary_text, path, heading_anchor)
    VALUES (new.rowid, new.summary_text, new.path, new.heading_anchor);
END;

CREATE TRIGGER IF NOT EXISTS summaries_ad AFTER DELETE ON summaries BEGIN
    INSERT INTO summaries_fts(summaries_fts, rowid, summary_text, path, heading_anchor)
    VALUES ('delete', old.rowid, old.summary_text, old.path, old.heading_anchor);
END;

CREATE TRIGGER IF NOT EXISTS summaries_au AFTER UPDATE ON summaries BEGIN
    INSERT INTO summaries_fts(summaries_fts, rowid, summary_text, path, heading_anchor)
    VALUES ('delete', old.rowid, old.summary_text, old.path, old.heading_anchor);
    INSERT INTO summaries_fts(rowid, summary_text, path, heading_anchor)
    VALUES (new.rowid, new.summary_text, new.path, new.heading_anchor);
END;
"""


@dataclass
class IndexStats:
    new: int = 0
    changed: int = 0
    unchanged: int = 0
    removed: int = 0
    elapsed_seconds: float = 0.0


def init_db(db_path: Path, cfg: LocatorConfig) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    # SQLite disables foreign keys per-connection by default, so the schema's
    # ON DELETE CASCADE on summaries(path) is inert unless we opt in here.
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA)
    # Record metadata for status / version skew detection
    conn.execute(
        "INSERT OR REPLACE INTO metadata(key, value) VALUES ('embedding_model', ?)",
        (cfg.embedding_model,),
    )
    conn.execute(
        "INSERT OR REPLACE INTO metadata(key, value) VALUES ('embedding_dimension', ?)",
        (str(cfg.embedding_dimension),),
    )
    conn.execute(
        "INSERT OR REPLACE INTO metadata(key, value) VALUES ('schema_version', '1')",
    )
    conn.commit()
    return conn


def index(cfg: LocatorConfig, *, full: bool = False) -> IndexStats:
    """Incrementally index the corpus into cfg.index_path.

    When full=True, drops all existing rows and re-embeds everything.
    """
    start = time.time()
    stats = IndexStats()
    conn = init_db(cfg.index_path, cfg)

    if full:
        conn.executescript("DELETE FROM summaries; DELETE FROM indexed_files;")
        conn.commit()

    walk = walk_corpus(cfg)
    seen_paths: set[str] = set()
    current_hashes: dict[str, str] = {}

    # First pass: compute hashes, decide NEW/CHANGED/UNCHANGED
    work: list[Path] = []
    for rel in walk.included:
        abs_path = cfg.project_root / rel
        rel_str = str(rel)
        seen_paths.add(rel_str)
        ch = content_hash(abs_path)
        current_hashes[rel_str] = ch
        prior = conn.execute(
            "SELECT content_hash FROM indexed_files WHERE path = ?", (rel_str,)
        ).fetchone()
        if prior is None:
            stats.new += 1
            work.append(rel)
        elif prior[0] != ch:
            stats.changed += 1
            work.append(rel)
        else:
            stats.unchanged += 1

    # Detect removals (rows in indexed_files no longer in seen_paths)
    rows = conn.execute("SELECT path FROM indexed_files").fetchall()
    removed_paths = [r[0] for r in rows if r[0] not in seen_paths]
    if removed_paths:
        placeholders = ",".join("?" * len(removed_paths))
        conn.execute(f"DELETE FROM summaries WHERE path IN ({placeholders})", removed_paths)
        conn.execute(f"DELETE FROM indexed_files WHERE path IN ({placeholders})", removed_paths)
        stats.removed = len(removed_paths)

    # Second pass: extract + embed + write the NEW/CHANGED set
    if work:
        embeddings = _embed_summaries(cfg, work)
        _write_batch(conn, cfg, work, current_hashes, embeddings)

    conn.commit()
    conn.close()
    stats.elapsed_seconds = round(time.time() - start, 2)
    return stats


def _embed_summaries(cfg: LocatorConfig, work: list[Path]) -> dict[str, list[bytes]]:
    """Return {rel_path: [file_summary_embedding, sub1_embedding, ...]} as raw bytes."""
    try:
        from fastembed import TextEmbedding  # type: ignore
    except ImportError:
        raise RuntimeError(
            "fastembed is not installed. Run: pip install -r tools/file-locator-mcp/requirements.txt"
        )

    model = TextEmbedding(model_name=cfg.embedding_model)

    # Flatten all texts so we embed them in one batch (much faster).
    flat_texts: list[str] = []
    flat_map: list[tuple[str, str | None]] = []  # (path, heading_anchor or None)
    file_summary_cache: dict[str, ExtractedSummary] = {}
    sub_summary_cache: dict[str, list[SubSummary]] = {}

    for rel in work:
        abs_path = cfg.project_root / rel
        summary, subs = extract_summary(abs_path, cfg)
        rel_str = str(rel)
        file_summary_cache[rel_str] = summary
        sub_summary_cache[rel_str] = subs
        flat_texts.append(summary.text)
        flat_map.append((rel_str, None))
        for sub in subs:
            flat_texts.append(sub.text)
            flat_map.append((rel_str, sub.heading_anchor))

    # Run embedding model once for the whole batch
    vectors = list(model.embed(flat_texts))

    # Group back by path
    out: dict[str, list[bytes]] = {}
    out_meta: dict[str, list[tuple[str | None, str]]] = {}  # path -> [(anchor, text), ...]
    for (rel_str, anchor), vec in zip(flat_map, vectors):
        out.setdefault(rel_str, []).append(vec.astype("float32").tobytes())
        text = (
            file_summary_cache[rel_str].text if anchor is None
            else next(s.text for s in sub_summary_cache[rel_str] if s.heading_anchor == anchor)
        )
        out_meta.setdefault(rel_str, []).append((anchor, text))

    # Stash the metadata so _write_batch can consume it without re-extracting
    _embed_summaries._last_meta = out_meta  # type: ignore[attr-defined]
    _embed_summaries._last_file_summaries = file_summary_cache  # type: ignore[attr-defined]
    _embed_summaries._last_subs = sub_summary_cache  # type: ignore[attr-defined]
    return out


def _write_batch(
    conn: sqlite3.Connection,
    cfg: LocatorConfig,
    work: list[Path],
    current_hashes: dict[str, str],
    embeddings: dict[str, list[bytes]],
) -> None:
    meta: dict[str, list[tuple[str | None, str]]] = getattr(_embed_summaries, "_last_meta", {})
    file_summaries: dict[str, ExtractedSummary] = getattr(_embed_summaries, "_last_file_summaries", {})
    now = time.time()

    for rel in work:
        rel_str = str(rel)
        abs_path = cfg.project_root / rel
        stat = abs_path.stat()
        summary = file_summaries[rel_str]

        # Delete prior rows for this path. We delete summaries explicitly rather
        # than relying solely on the ON DELETE CASCADE — a re-index of a CHANGED
        # file must not leave stale summary rows that collide with the re-inserts
        # below on the (path, heading_anchor) primary key.
        conn.execute("DELETE FROM summaries WHERE path = ?", (rel_str,))
        conn.execute("DELETE FROM indexed_files WHERE path = ?", (rel_str,))

        conn.execute(
            """INSERT INTO indexed_files
               (path, content_hash, size_bytes, mtime, indexed_at, summary_method, kind)
               VALUES (?, ?, ?, ?, ?, ?, 'doc')""",
            (
                rel_str,
                current_hashes[rel_str],
                stat.st_size,
                stat.st_mtime,
                now,
                summary.method,
            ),
        )

        # Insert summary rows (file-level + sub-summaries)
        for (anchor, text), emb in zip(meta[rel_str], embeddings[rel_str]):
            est_tokens = max(1, len(text) // 4)  # crude approximation
            conn.execute(
                """INSERT INTO summaries
                   (path, heading_anchor, summary_text, embedding, estimated_tokens)
                   VALUES (?, ?, ?, ?, ?)""",
                (rel_str, anchor, text, emb, est_tokens),
            )
