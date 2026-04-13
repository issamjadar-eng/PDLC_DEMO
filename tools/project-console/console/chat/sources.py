from pathlib import Path
from typing import Iterable

MAX_BYTES = 200_000


def resolve_files(repo_root: Path, patterns: Iterable[str]) -> list[Path]:
    seen: set[Path] = set()
    paths: list[Path] = []
    for pattern in patterns:
        for path in sorted(repo_root.glob(pattern)):
            if not path.is_file() or path in seen:
                continue
            seen.add(path)
            paths.append(path)
    return paths


def resolve(repo_root: Path, patterns: Iterable[str]) -> str:
    seen: set[Path] = set()
    chunks: list[str] = []
    total = 0
    for pattern in patterns:
        for path in sorted(repo_root.glob(pattern)):
            if not path.is_file() or path in seen:
                continue
            seen.add(path)
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            rel = path.relative_to(repo_root)
            chunk = f"\n\n===== FILE: {rel} =====\n\n{text}"
            if total + len(chunk) > MAX_BYTES:
                chunks.append(f"\n\n[... truncated at {MAX_BYTES} byte cap ...]\n")
                return "".join(chunks)
            chunks.append(chunk)
            total += len(chunk)
    return "".join(chunks)
