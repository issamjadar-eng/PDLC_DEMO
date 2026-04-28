from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

# Fallback cap when callers don't pass `cap_bytes` (e.g. internal tests,
# legacy call sites). Production chat path receives a model-aware cap
# from `config.caps_for_model()` via router.py.
MAX_BYTES = 200_000


@dataclass
class ResolvedSources:
    text: str
    included: list[Path] = field(default_factory=list)
    skipped: list[Path] = field(default_factory=list)
    truncated: bool = False
    cap_bytes: int = MAX_BYTES

    @property
    def warnings(self) -> list[str]:
        msgs: list[str] = []
        if self.truncated:
            n = len(self.skipped)
            msgs.append(
                f"Source budget exceeded ({self.cap_bytes // 1000}KB cap): "
                f"included {len(self.included)} file(s), skipped {n}."
            )
            for p in self.skipped[:5]:
                msgs.append(f"  · skipped: {p}")
            if n > 5:
                msgs.append(f"  · …and {n - 5} more")
        return msgs


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


def resolve_with_meta(
    repo_root: Path,
    patterns: Iterable[str],
    cap_bytes: int = MAX_BYTES,
) -> ResolvedSources:
    chunks: list[str] = []
    included: list[Path] = []
    skipped: list[Path] = []
    truncated = False
    total = 0
    for path in resolve_files(repo_root, patterns):
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            skipped.append(path.relative_to(repo_root))
            continue
        rel = path.relative_to(repo_root)
        chunk = f"\n\n===== FILE: {rel} =====\n\n{text}"
        if total + len(chunk) > cap_bytes:
            truncated = True
            skipped.append(rel)
            continue
        chunks.append(chunk)
        included.append(rel)
        total += len(chunk)
    if truncated:
        chunks.append(f"\n\n[... truncated at {cap_bytes} byte cap ...]\n")
    return ResolvedSources(
        text="".join(chunks),
        included=included,
        skipped=skipped,
        truncated=truncated,
        cap_bytes=cap_bytes,
    )


def resolve(repo_root: Path, patterns: Iterable[str]) -> str:
    return resolve_with_meta(repo_root, patterns).text
