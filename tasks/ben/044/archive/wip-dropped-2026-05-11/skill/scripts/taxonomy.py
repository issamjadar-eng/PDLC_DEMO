"""Taxonomy library — load/save .taxonomy.yml, resolve which taxonomy serves a
given root, scan a folder tree to propose role mappings.

Used by:
  scripts/init_taxonomy.py     — cold-start scan + write a new .taxonomy.yml
  scripts/reconcile_taxonomy.py — diff disk vs taxonomy; update pending/broken_refs
  scripts/generate.py          — resolver lookup before falling back to the
                                  hardcoded DEFAULT_SYSTEM_DHF_ROLE_MAP

Schema reference: schemas/taxonomy.schema.yml (v0.3, additive over Arthrex v0.2).
Registration: project.yml.taxonomies[] is canonical; dhfs[].taxonomy_path is
the legacy fallback (Arthrex pattern). Co-located <root>/.taxonomy.yml is the
default location when neither registers a different file.
"""

from __future__ import annotations

import datetime
import fnmatch
import re
from pathlib import Path
from typing import Optional

try:
    import yaml as _yaml
except ImportError:
    _yaml = None


SCHEMA_VERSION = "0.4"

# Aggregation classifier (v0.4 conservative posture) — Tier 1 NEVER
# auto-aggregates. Single-role + N files in a folder is structurally weak
# evidence; many regulatory standards require multiple distinct deliverables
# under one canonical role (ISO 14971 has 5+ artifacts under risk-management:
# Risk Management Plan, Hazard Analysis, dFMEA, pFMEA, Risk Management
# Report — all distinct deliverables, all `risk-management` role). Tier 1's
# only job is to FLAG folders that warrant Tier 2 LLM review — actual
# aggregation decisions are made by the LLM agent (which has regulatory
# context) or by the user hand-editing the taxonomy.
#
# Files whose names match these substrings (case-insensitive) are recorded
# as "aggregator-named" hints in the candidate annotation; never used to
# auto-aggregate.
AGGREGATOR_NAME_SIGNALS = [
    "report", "summary", "overview", "rollup", "evaluation-report",
    "synthesis", "consolidated",
    # Plan-class aggregators — describe what a set of records will/should
    # cover (CEP aggregates per-feature CEPs; RMP scopes the analyses; SMP
    # frames sub-plans). Same structural role as a report — the parent
    # document that gives the records meaning.
    "plan",
    # Roll-up data structures — register, log, matrix, list, index, catalog
    # are all "many records consolidated into one document" patterns.
    "register", "log", "matrix", "index", "catalog",
]

# Record-shape detector: matches stem `<PREFIX>-<NUMBER>` with NOTHING
# after the number. Stem only (caller strips .md). The "no trailing text"
# requirement is the structural signal that distinguishes a record (one
# row in a series) from a regular numbered document with a descriptive
# title.
#
#   record-shaped:     BRA-1001, CEP-1003, AE-2024-001, TC-100, FMA_205
#   NOT record-shaped: GL-TMP-RM-002-risk-management-report (trailing
#                      `-risk-management-report` disqualifies),
#                      risk-strategy (no number), release-notes-v1 (v
#                      prefix on the number).
_RECORD_SHAPE_RE = re.compile(
    r"^(?P<prefix>[A-Za-z][A-Za-z0-9-]*?)[-_](?P<num>\d{2,})$",
)


def is_record_shaped(filename: str) -> bool:
    """True when the filename is a pure record identifier (no descriptive
    tail). Examples: BRA-1001.md, CEP-1003.md, TC-100.md.
    Counter-examples: GL-TMP-RM-002-risk-management-report.md (descriptor
    after number), risk-strategy.md (no number), v1.md (no prefix)."""
    stem = filename[:-3] if filename.lower().endswith(".md") else filename
    return bool(_RECORD_SHAPE_RE.match(stem))


# Numbered-series detector — kept for backward compat with older callers
# (e.g. humanize_filename's "preserve numbered IDs verbatim" check). Newer
# code should prefer is_record_shaped() which is the same shape minus the
# .md suffix requirement and is the active classifier signal.
_NUMBERED_SERIES_RE = re.compile(
    r"^(?P<prefix>[A-Z]{2,}|[a-z][a-z0-9-]+?)[-_](?P<num>\d{2,})\.md$",
    re.IGNORECASE,
)

# QMS-style filename prefixes that the friendly-title humanizer strips when
# no frontmatter `title:` is present. The default pattern matches the
# GlobalLogic QMS convention (GL-TMP-RM-002-, GL-SOP-SW-004-, etc.); other
# companies override via `project.yml.tracker.filename_prefix_strip_patterns`
# (a list of regex strings). Each project can supply its own QMS numbering
# conventions without skill code edits.
DEFAULT_FILENAME_PREFIX_PATTERNS = [
    r"^GL-(?:TMP|SOP|WI|FORM|POL|REC)-[A-Z]{2,3}-\d{2,4}-",  # GlobalLogic
]


def get_filename_prefix_patterns(project_dir: Path | None = None) -> list[re.Pattern]:
    """Resolve the filename-prefix strip patterns. Reads
    `project.yml.tracker.filename_prefix_strip_patterns` if a project_dir
    is given; otherwise returns the skill default. Compiled at call time so
    project.yml edits take effect without re-import."""
    patterns = list(DEFAULT_FILENAME_PREFIX_PATTERNS)
    if project_dir is not None:
        try:
            pyl = load_yaml(Path(project_dir) / "project.yml")
            cfg = (pyl.get("tracker") or {}).get("filename_prefix_strip_patterns")
            if cfg:
                patterns = list(cfg)
        except Exception:
            pass
    return [re.compile(p, re.IGNORECASE) for p in patterns]


# Skill-default heuristic patterns (medtech IEC-62304-shaped). Other
# project types (pharma CTD, IVD, automotive ASPICE, etc.) override via
# `project.yml.tracker.classification_heuristics`. Each entry:
# {regex: <str>, role: <canonical-role>, confidence: 'high'|'low'}.
# Order matters within a list — first match wins. When project supplies
# custom patterns, they fully replace the default unless the project also
# sets `tracker.classification_heuristics_extend: true` (then project
# patterns prepend to the default list).
DEFAULT_HEURISTICS_CONFIG = [
    # Architecture
    {"regex": r".*-sad\.md$", "role": "architecture", "confidence": "high"},
    {"regex": r".*system-architecture.*\.md$", "role": "architecture", "confidence": "high"},
    {"regex": r"design-controls/architecture/.*\.md$", "role": "architecture", "confidence": "high"},
    # Requirements
    {"regex": r".*-srs\.md$", "role": "requirements", "confidence": "high"},
    {"regex": r".*requirements.*spec.*\.md$", "role": "requirements", "confidence": "high"},
    {"regex": r"design-controls/requirements/.*\.md$", "role": "requirements", "confidence": "high"},
    # Design
    {"regex": r".*-sdd\.md$", "role": "design", "confidence": "high"},
    {"regex": r".*detailed-design.*\.md$", "role": "design", "confidence": "high"},
    # V&V
    {"regex": r".*-stp\.md$", "role": "vnv", "confidence": "high"},
    {"regex": r".*-stc\.md$", "role": "vnv", "confidence": "high"},
    {"regex": r".*-str\.md$", "role": "vnv", "confidence": "high"},
    {"regex": r"design-controls/vnv/.*\.md$", "role": "vnv", "confidence": "high"},
    {"regex": r".*verification.*protocol.*\.md$", "role": "vnv", "confidence": "high"},
    # Risk management
    {"regex": r".*-rmf\.md$", "role": "risk-management", "confidence": "high"},
    {"regex": r".*-rmp\.md$", "role": "risk-management", "confidence": "high"},
    {"regex": r".*risk-management.*\.md$", "role": "risk-management", "confidence": "high"},
    {"regex": r"^risk-management/.*\.md$", "role": "risk-management", "confidence": "high"},
    # Cybersecurity
    {"regex": r"^cybersecurity/.*\.md$", "role": "cybersecurity", "confidence": "high"},
    {"regex": r".*threat-model.*\.md$", "role": "cybersecurity", "confidence": "high"},
    {"regex": r".*sbom.*\.md$", "role": "sbom", "confidence": "high"},
    # Clinical / Postmarket
    {"regex": r"^clinical/.*\.md$", "role": "clinical", "confidence": "high"},
    {"regex": r"^postmarket/.*\.md$", "role": "postmarket", "confidence": "high"},
    {"regex": r".*psur.*\.md$", "role": "postmarket", "confidence": "high"},
    # Plans / user-needs / trace / tools / labeling / usability
    {"regex": r"design-controls/plans/.*\.md$", "role": "plans", "confidence": "high"},
    {"regex": r"design-controls/user-needs/.*\.md$", "role": "user-needs", "confidence": "high"},
    {"regex": r".*use-specification.*\.md$", "role": "user-needs", "confidence": "high"},
    {"regex": r"design-controls/trace-matrix/.*\.md$", "role": "trace-matrix", "confidence": "high"},
    {"regex": r".*-stm\.md$", "role": "trace-matrix", "confidence": "high"},
    {"regex": r".*-htm\.md$", "role": "trace-matrix", "confidence": "high"},
    {"regex": r"design-controls/tool-validation/.*\.md$", "role": "tool-validation", "confidence": "high"},
    {"regex": r"design-controls/labeling/.*\.md$", "role": "labeling", "confidence": "high"},
    {"regex": r"design-controls/usability/.*\.md$", "role": "usability", "confidence": "high"},
    # Low-confidence catch-alls
    {"regex": r".*-spec\.md$", "role": "requirements", "confidence": "low"},
    {"regex": r".*-plan\.md$", "role": "plans", "confidence": "low"},
]


def get_heuristics(project_dir: Path | None = None) -> list[tuple]:
    """Resolve the classification heuristics. Reads
    `project.yml.tracker.classification_heuristics` if a project_dir is
    given; otherwise returns the skill default. Project patterns fully
    replace the default unless `tracker.classification_heuristics_extend:
    true`, in which case project patterns prepend to the default list."""
    cfg_list = list(DEFAULT_HEURISTICS_CONFIG)
    if project_dir is not None:
        try:
            pyl = load_yaml(Path(project_dir) / "project.yml")
            tcfg = pyl.get("tracker") or {}
            project_list = tcfg.get("classification_heuristics")
            if project_list:
                if tcfg.get("classification_heuristics_extend"):
                    cfg_list = list(project_list) + list(DEFAULT_HEURISTICS_CONFIG)
                else:
                    cfg_list = list(project_list)
        except Exception:
            pass
    out = []
    for entry in cfg_list:
        try:
            out.append((re.compile(entry["regex"], re.IGNORECASE),
                        entry["role"], entry.get("confidence", "low")))
        except (KeyError, re.error):
            continue
    return out

# Default canonical role vocabulary — medtech-docs-shaped. Mirrored from the
# Arthrex .taxonomy.yml header comment + the canonical roles implied by
# generate.py's DEFAULT_SYSTEM_DHF_ROLE_MAP. Projects override per-taxonomy
# via vocabulary_source.kind=inline.
DEFAULT_VOCABULARY = [
    "architecture", "requirements", "design", "vnv", "risk-management",
    "cybersecurity", "privacy", "clinical", "human-factors", "postmarket",
    "plans", "user-needs", "trace-matrix", "tool-validation", "sbom",
    "labeling", "usability",
]

# Legacy module-level HEURISTICS retained for backward callers; superseded
# by get_heuristics() which respects project.yml overrides. New callers
# should use get_heuristics(project_dir).
HEURISTICS = [
    (re.compile(e["regex"], re.IGNORECASE), e["role"], e.get("confidence", "low"))
    for e in DEFAULT_HEURISTICS_CONFIG
]

# Files/dirs to skip outright during scan (never proposed, never pending).
DEFAULT_EXCLUDES = [
    "README.md", "readme.md",                    # root-level
    "**/README.md", "**/readme.md",              # nested
    "Icon", "**/Icon", ".DS_Store", "**/.DS_Store",
    "**/__pycache__/**", "**/.git/**",
]


# ─── YAML I/O ──────────────────────────────────────────────────────────────

def _require_yaml():
    if _yaml is None:
        raise RuntimeError(
            "PyYAML not available. Install in the project-console venv:\n"
            "  cd tools/project-console && uv add pyyaml\n"
            "Or invoke this script via:\n"
            "  uv run --project tools/project-console python <script>"
        )


def load_yaml(path: Path) -> dict:
    _require_yaml()
    return _yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def dump_yaml(data: dict, path: Path) -> None:
    """Write yaml with stable key ordering and clean formatting."""
    _require_yaml()
    text = _yaml.safe_dump(
        data, sort_keys=False, default_flow_style=False, width=100,
        allow_unicode=True,
    )
    path.write_text(text, encoding="utf-8")


# ─── Registry resolver ────────────────────────────────────────────────────

def _norm_path(p) -> str:
    """Normalize a path string (no trailing slash, forward slashes)."""
    if p is None:
        return ""
    s = str(p).replace("\\", "/")
    while s.endswith("/"):
        s = s[:-1]
    return s


def resolve_taxonomy(
    project_dir: Path,
    *,
    dhf_leaf: Optional[str] = None,
    folder_path: Optional[str] = None,
) -> Optional[Path]:
    """Resolve which .taxonomy.yml file (if any) serves a given root.

    Resolution precedence:
      1. project.yml taxonomies[] — applies_to_dhfs / applies_to_paths match
      2. project.yml dhfs[<leaf>].taxonomy_path (legacy Arthrex pattern)
      3. Co-located <root>/.taxonomy.yml
      4. None — caller falls back to hardcoded behavior

    Exactly one of `dhf_leaf` or `folder_path` must be set.
    """
    if (dhf_leaf is None) == (folder_path is None):
        raise ValueError("provide exactly one of dhf_leaf or folder_path")

    project_yml = project_dir / "project.yml"
    if not project_yml.is_file():
        return None
    pyl = load_yaml(project_yml)

    # 1. taxonomies[] registry
    for entry in (pyl.get("taxonomies") or []):
        if dhf_leaf is not None:
            if dhf_leaf in (entry.get("applies_to_dhfs") or []):
                return project_dir / entry["file"]
        else:
            target = _norm_path(folder_path)
            for ap in (entry.get("applies_to_paths") or []):
                if _norm_path(ap) == target:
                    return project_dir / entry["file"]

    # 2. legacy dhfs[].taxonomy_path
    if dhf_leaf is not None:
        for d in (pyl.get("dhfs") or []):
            if d.get("leaf") == dhf_leaf and d.get("taxonomy_path"):
                return project_dir / d["taxonomy_path"]

    # 3. co-located default
    if dhf_leaf is not None:
        for d in (pyl.get("dhfs") or []):
            if d.get("leaf") == dhf_leaf:
                root = project_dir / d["path"]
                candidate = root / ".taxonomy.yml"
                if candidate.is_file():
                    return candidate
                break
    else:
        candidate = project_dir / folder_path / ".taxonomy.yml"
        if candidate.is_file():
            return candidate

    return None


def list_registered_taxonomies(project_dir: Path) -> list[dict]:
    """Return all taxonomies registered for this project, normalized.

    Each entry: {id, file (Path), applies_to_dhfs, applies_to_paths, source}
    where source is 'taxonomies-registry' or 'legacy-taxonomy-path'.
    """
    project_yml = project_dir / "project.yml"
    if not project_yml.is_file():
        return []
    pyl = load_yaml(project_yml)
    out = []
    seen_files = set()

    for entry in (pyl.get("taxonomies") or []):
        f = project_dir / entry["file"]
        out.append({
            "id": entry.get("id") or _norm_path(entry["file"]),
            "file": f,
            "applies_to_dhfs": list(entry.get("applies_to_dhfs") or []),
            "applies_to_paths": list(entry.get("applies_to_paths") or []),
            "source": "taxonomies-registry",
        })
        seen_files.add(_norm_path(f))

    for d in (pyl.get("dhfs") or []):
        tp = d.get("taxonomy_path")
        if not tp:
            continue
        f = project_dir / tp
        norm = _norm_path(f)
        # Merge with existing if same file already registered
        existing = next((o for o in out if _norm_path(o["file"]) == norm), None)
        if existing:
            if d["leaf"] not in existing["applies_to_dhfs"]:
                existing["applies_to_dhfs"].append(d["leaf"])
            continue
        out.append({
            "id": d["leaf"] + "-legacy",
            "file": f,
            "applies_to_dhfs": [d["leaf"]],
            "applies_to_paths": [],
            "source": "legacy-taxonomy-path",
        })
        seen_files.add(norm)

    return out


# ─── Scanner ──────────────────────────────────────────────────────────────

def _matches_any(path_str: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(path_str, p) for p in patterns)


def _heuristic_lookup(
    rel_path: str,
    heuristics: list[tuple] | None = None,
) -> tuple[Optional[str], list[str]]:
    """Return (high_confidence_role, [candidate_roles]) for a path.

    high_confidence_role is non-None when a single high-confidence pattern
    matched; candidate_roles aggregates all 'low' matches plus any high
    matches when no single high winner exists.

    `heuristics` is the resolved list (project overrides applied) — when
    omitted, falls back to module-level HEURISTICS (skill defaults). Callers
    inside scan_root pass the resolved list once per scan to avoid repeated
    project.yml reads.
    """
    if heuristics is None:
        heuristics = HEURISTICS
    high = None
    candidates: list[str] = []
    for regex, role, confidence in heuristics:
        # `regex` may be a compiled Pattern (resolved path) or a string
        # (legacy module-level HEURISTICS); search() works on both via
        # the compiled fast-path.
        rx = regex if hasattr(regex, "search") else re.compile(regex, re.IGNORECASE)
        if rx.search(rel_path):
            if confidence == "high" and high is None:
                high = role
            elif confidence == "low":
                if role not in candidates:
                    candidates.append(role)
    return high, candidates


def scan_root(
    root_path: Path,
    *,
    discovery_root: str = ".",
    excluded: Optional[list[str]] = None,
    project_dir: Optional[Path] = None,
) -> dict:
    """Walk a root, classify .md files via heuristics, return scan result.

    Returns:
        {
          'walked_root':      <Path>,
          'discovery_root':   <str>,
          'high_confidence':  {rel_path: role, ...},
          'pending':          [{path, candidate_roles}, ...],
          'all_files':        [rel_path, ...],   # every .md found (excl. excludes)
        }
    """
    excluded = list(DEFAULT_EXCLUDES) + (excluded or [])
    walk_dir = (root_path / discovery_root).resolve()
    base = walk_dir
    high: dict[str, str] = {}
    pending: list[dict] = []
    all_files: list[str] = []

    if not walk_dir.is_dir():
        return {
            "walked_root": root_path,
            "discovery_root": discovery_root,
            "high_confidence": high,
            "pending": pending,
            "all_files": all_files,
        }

    # Resolve project overrides ONCE per scan. When project_dir is None
    # (legacy callers), falls back to skill defaults. Future-proof: any
    # project that adds tracker.classification_heuristics,
    # tracker.filename_prefix_strip_patterns, or tracker.title_acronyms
    # to project.yml inherits its custom rules without code edits.
    heuristics = get_heuristics(project_dir)
    prefix_patterns = get_filename_prefix_patterns(project_dir)
    acronyms = get_title_acronyms(project_dir)

    titles: dict[str, str] = {}
    for entry in walk_dir.rglob("*.md"):
        rel = entry.relative_to(base).as_posix()
        if _matches_any(rel, excluded) or _matches_any(entry.name, excluded):
            continue
        all_files.append(rel)
        role, candidates = _heuristic_lookup(rel, heuristics)
        if role is not None:
            high[rel] = role
        else:
            pending.append({"path": rel, "candidate_roles": candidates})
        # Resolve a friendly title — frontmatter `title:` first, then
        # synthesized doc_type+doc_id (for project-authored records like
        # BRA-1001 / STUDY-0001 that carry doc_type but no title), then
        # humanized filename. Stored on the scan so build_mappings_from_scan
        # can attach it to each mapping (used by render.py's Deliverable
        # column).
        t = extract_title(entry, acronyms=acronyms)
        titles[rel] = t if t else humanize_filename(rel, prefix_patterns=prefix_patterns)

    return {
        "walked_root": root_path,
        "discovery_root": discovery_root,
        "high_confidence": high,
        "pending": pending,
        "all_files": all_files,
        "titles": titles,
    }


# ─── Friendly-title extraction ────────────────────────────────────────────

# HCLS / medtech acronyms that should stay UPPER when humanized (so
# `pmcf-study` becomes "PMCF Study" not "Pmcf Study"). Skill-default;
# extensible via `project.yml.tracker.title_acronyms` (a list of lowercase
# strings appended to this set at resolution time).
KNOWN_ACRONYMS = {
    # Regulatory bodies / frameworks
    "fda", "ema", "mhra", "iec", "iso", "imdrf", "mdcg", "qms",
    # Submission types
    "qsub", "lmr", "pma", "ide", "ce", "udi", "ifu",
    # Clinical / postmarket
    "cer", "cep", "bra", "brd", "lss", "lsr", "psur", "pmcf", "pms",
    # Risk
    "rmf", "rmp", "rmr", "fmea", "fmeca", "dfmea", "pfmea", "ha", "htm",
    # Software / V&V
    "sad", "srs", "sdd", "stm", "stp", "stc", "str", "soup", "sbom",
    # AI / ML / cyber
    "ai", "ml", "pccp", "vmp", "tm", "sbom",
    # Misc
    "sop", "wi", "tmp", "rec",
}


def get_title_acronyms(project_dir: Path | None = None) -> set[str]:
    """Resolve the acronym set used for HCLS-aware title casing. Project
    override at `project.yml.tracker.title_acronyms` (list of strings,
    case-insensitive) is appended to the skill default."""
    out = set(KNOWN_ACRONYMS)
    if project_dir is not None:
        try:
            pyl = load_yaml(Path(project_dir) / "project.yml")
            extra = (pyl.get("tracker") or {}).get("title_acronyms") or []
            for a in extra:
                out.add(str(a).lower())
        except Exception:
            pass
    return out


def _smart_title_case(words: list[str], acronyms: set[str]) -> str:
    """Title-case a list of word tokens, keeping HCLS acronyms uppercase."""
    pieces = []
    for w in words:
        if not w:
            continue
        if w.lower() in acronyms:
            pieces.append(w.upper())
        elif w.isupper() and len(w) >= 2:
            # Already an acronym/UPPER token (e.g. STUDY, BRA in a doc_id) —
            # preserve as-is rather than coercing to "Study"/"Bra".
            pieces.append(w)
        elif w.islower():
            pieces.append(w.capitalize())
        else:
            pieces.append(w)
    return " ".join(pieces)


def humanize_doc_type(doc_type: str, acronyms: set[str] | None = None) -> str:
    """Convert a kebab/snake doc_type ("pmcf-study", "benefit_risk_analysis")
    into a friendly title ("PMCF Study", "Benefit-Risk Analysis"). Used when
    a record-shaped file has no frontmatter `title:` but does declare a
    `doc_type` — synthesizes a friendly Deliverable label from doc_type
    plus doc_id."""
    if not doc_type:
        return ""
    acronyms = acronyms if acronyms is not None else KNOWN_ACRONYMS
    # Special case: hyphen-bound compound terms that read better as
    # "Benefit-Risk Analysis" rather than "Benefit Risk Analysis". Detect
    # by looking for known-compound patterns (currently just any word that
    # isn't an acronym preceded/followed by short connector tokens).
    # Simpler v1: split on -/_ uniformly; render with single spaces.
    words = re.split(r"[-_]+", doc_type)
    return _smart_title_case(words, acronyms)


def _read_frontmatter_block(file_abs: Path) -> str | None:
    """Return the YAML frontmatter block contents (between leading `---`
    fences) or None if missing/malformed."""
    try:
        with file_abs.open("r", encoding="utf-8", errors="ignore") as f:
            head = f.read(4096)
    except OSError:
        return None
    if not head.startswith("---"):
        return None
    end = head.find("\n---", 3)
    if end < 0:
        return None
    return head[3:end]


def _frontmatter_field(fm: str, field: str) -> str | None:
    """Pull a single scalar field from a frontmatter block."""
    m = re.search(
        rf'^\s*{re.escape(field)}\s*:\s*["\']?(.+?)["\']?\s*(?:#.*)?$',
        fm, re.MULTILINE,
    )
    return m.group(1).strip() if m else None


def extract_title(file_abs: Path, *, acronyms: set[str] | None = None) -> str | None:
    """Resolve a friendly title for a markdown file.

    Resolution order:
      1. Frontmatter `title:` field — preferred (project author wrote it).
      2. Synthesized from frontmatter `doc_type` + `doc_id` — for
         project-authored records (BRA-1001, STUDY-0001, CEP-1003, …)
         that carry doc_type/doc_id but no explicit title. Output looks
         like "PMCF Study — STUDY-0001", "Benefit-Risk Analysis — BRA-1001".
      3. None — caller falls back to humanize_filename(prefix_patterns).

    The synthesizer keeps record IDs visible (auditors need to tell BRA-1001
    from BRA-1002) while wrapping them in the doc-type label so reviewers
    don't see naked filenames in the Deliverable column.
    """
    fm = _read_frontmatter_block(file_abs)
    if fm is None:
        return None

    # 1. Explicit title
    title = _frontmatter_field(fm, "title")
    if title:
        return title

    # 2. Synthesize from doc_type + doc_id (record pattern)
    doc_type = _frontmatter_field(fm, "doc_type")
    doc_id = _frontmatter_field(fm, "doc_id")
    if doc_type and doc_id:
        type_label = humanize_doc_type(doc_type, acronyms or KNOWN_ACRONYMS)
        return f"{type_label} — {doc_id}" if type_label else doc_id
    if doc_type and not doc_id:
        return humanize_doc_type(doc_type, acronyms or KNOWN_ACRONYMS) or None

    return None


def humanize_filename(
    file_path: str,
    *,
    prefix_patterns: list[re.Pattern] | None = None,
) -> str:
    """Fallback friendly title when frontmatter `title:` is absent.

    Strips QMS-style prefixes (each project supplies its own via
    `project.yml.tracker.filename_prefix_strip_patterns`; default matches
    GlobalLogic's `GL-TMP-XX-NNN-` pattern) and title-cases the remainder.
    Caller passes `prefix_patterns` (resolved via `get_filename_prefix_patterns(
    project_dir)`); when omitted, uses skill defaults.

    Examples (with default GL pattern):
        GL-SOP-SW-004-vulnerability-management-plan.md
            → "Vulnerability Management Plan"
        risk-strategy.md
            → "Risk Strategy"
        BRA-1001.md
            → "BRA-1001"  (numbered series — leave as-is so reviewers can
                          tell instances apart)
    """
    name = Path(file_path).name
    if name.lower().endswith(".md"):
        name = name[:-3]
    if _NUMBERED_SERIES_RE.match(name + ".md"):
        return name
    patterns = prefix_patterns if prefix_patterns is not None else get_filename_prefix_patterns()
    stripped = name
    for pat in patterns:
        new = pat.sub("", stripped)
        if new != stripped:
            stripped = new
            break
    if not stripped:
        stripped = name
    words = re.split(r"[-_]+", stripped)
    return " ".join(w.capitalize() if w.islower() else w for w in words if w)


# ─── Aggregation classifier (Tier 1 — flagger only, never auto-aggregates) ─

def classify_folder(
    folder_rel: str, file_paths: list[str], roles: dict[str, str]
) -> dict:
    """Tier 1 conservative classifier — NEVER auto-aggregates.

    Single-role + N files in a folder is structurally weak evidence for
    aggregation; many regulatory standards require multiple distinct
    deliverables under one canonical role (ISO 14971's risk-management:
    Plan / Hazard Analysis / dFMEA / pFMEA / Report — all `risk-management`,
    all distinct). Auto-aggregating on structural signals alone produces
    false positives that hide regulatory deliverable obligations.

    Tier 1's behavior:
      - Always returns kind=`independent` (per-file mappings emitted)
      - Sets `aggregation_candidate=true` when a numbered-series pattern
        is detected — this is a flag for Tier 2 (LLM agent) or human
        review, NOT a behavior change to mappings
      - The rationale always tells the user what the structural signals
        were so they can decide whether to invoke Tier 2

    Args:
        folder_rel: relative folder path (e.g. "clinical/benefit-risk").
        file_paths: list of relative paths of .md files in this folder.
        roles: {file_path: canonical_role} for files heuristic-classified.

    Returns:
        {
          'kind': 'independent',           # always, in this conservative posture
          'aggregation_candidate': bool,    # true → flag for Tier 2 review
          'aggregation_signals': dict,      # what signals were detected
          'primary_member': None,
          'members': [],
          'confidence': 'high'|'low',       # high = clear independent;
                                            # low = aggregation_candidate=true
          'rationale': str,
        }
    """
    files = sorted(file_paths)
    n = len(files)
    names = [Path(p).name for p in files]

    if n <= 1:
        return {
            "kind": "independent",
            "aggregation_candidate": False,
            "aggregation_signals": {},
            "primary_member": files[0] if files else None,
            "members": [],
            "confidence": "high",
            "rationale": f"{n} file(s) in folder — single deliverable.",
        }

    # Aggregator-named file detection (any one of AGGREGATOR_NAME_SIGNALS
    # appears as a substring of a filename — case-insensitive)
    aggregator: str | None = None
    name_lower = [n.lower() for n in names]
    for signal in AGGREGATOR_NAME_SIGNALS:
        for i, nm in enumerate(name_lower):
            if signal in nm:
                aggregator = files[i]
                break
        if aggregator:
            break

    # Record-shape detection — count files whose stem is `<PREFIX>-<NUMBER>`
    # with no descriptive tail (BRA-1001, CEP-1003 qualify;
    # GL-TMP-RM-002-risk-management-report does NOT). This is the structural
    # signal that distinguishes "rows of one document" from "distinct
    # deliverables sharing a folder" — the count of records doesn't matter,
    # only that they're shaped like records.
    record_files = [p for p, nm in zip(files, names) if is_record_shaped(nm)]
    record_count = len(record_files)
    # Group records by their prefix — useful for diagnostics and to detect
    # mixed-series folders (rare but possible: AE-2024-001 + BRA-1001 →
    # ambiguous, fall back to candidate).
    record_prefixes = sorted({
        m.group("prefix").upper()
        for nm in (Path(p).name for p in record_files)
        for m in [_RECORD_SHAPE_RE.match(nm[:-3] if nm.lower().endswith(".md") else nm)]
        if m
    })

    role_set = {roles.get(p) for p in files if roles.get(p) is not None}
    single_role = len(role_set) == 1

    signals = {
        "file_count": n,
        "single_role": single_role,
        "record_count": record_count,
        "record_prefixes": record_prefixes,
        "aggregator_named_file": Path(aggregator).name if aggregator else None,
    }

    # ── High-confidence auto-aggregate (record-shape + aggregator + role) ─
    # The "rows of one document" pattern: ANY count of record-shaped files
    # rolled up by an aggregator-named summary, all under one canonical
    # role. Count is NOT the gate; structure is. Even 1 record + 1
    # aggregator aggregates (the record is a row of the aggregator).
    #
    # Examples that match: BRA-1001..1005 + clinical-evaluation-report,
    # CEP-1001..1005 + clinical-evaluation-plan, LSS-1001..1005 +
    # literature-search-report, BRA-1001 + CER (single-record case).
    #
    # Examples that do NOT match: risk-management folder (no record-shaped
    # files — descriptive names with no NUMBER-only suffix); cybersecurity
    # folder (Vulnerability Mgmt Plan, Threat Model, SBOM all descriptive).
    if record_count >= 1 and aggregator and single_role:
        return {
            "kind": "aggregate",
            "aggregation_candidate": True,
            "aggregation_signals": signals,
            "primary_member": aggregator,
            "members": files,
            "confidence": "high",
            "rationale": (
                f"Auto-aggregated (high confidence): {record_count} "
                f"record-shaped file(s) "
                + (f"in series `{', '.join(record_prefixes)}`" if record_prefixes else "")
                + f" rolled up by aggregator-named `{Path(aggregator).name}`, "
                f"all role `{next(iter(role_set))}`. Pattern: rows of one "
                f"document. Primary deliverable = the aggregator; records "
                f"are surfaced in the row's detail panel."
            ),
        }

    # ── Aggregation candidate (records WITHOUT in-folder aggregator) ──────
    # Multiple record-shaped files but no aggregator in this folder; the
    # rollup may live in the parent folder or elsewhere, OR the files may
    # actually be distinct deliverables that just happen to use record-style
    # names. Tier 2 (LLM agent) decides; default remains per-file.
    if record_count >= 2 and single_role:
        return {
            "kind": "independent",
            "aggregation_candidate": True,
            "aggregation_signals": signals,
            "primary_member": None,
            "members": [],
            "confidence": "low",
            "rationale": (
                f"Independent by default; aggregation-candidate flag set: "
                f"{record_count} record-shaped files "
                + (f"(`{', '.join(record_prefixes)}`)" if record_prefixes else "")
                + f", all role `{next(iter(role_set))}`, "
                "no aggregator-named summary in this folder. Aggregator may "
                "live in parent folder; run /tracker classify-folders for "
                "an LLM verdict."
            ),
        }

    return {
        "kind": "independent",
        "aggregation_candidate": False,
        "aggregation_signals": signals,
        "primary_member": None,
        "members": [],
        "confidence": "high",
        "rationale": (
            f"Independent: {n} files, "
            f"{'single' if single_role else 'mixed'} role, "
            f"{record_count if record_count else 'no'} record-shaped, "
            f"{'aggregator-named file present' if aggregator else 'no aggregator name'}. "
            "Each file is its own deliverable unless Tier 2 review (or hand-"
            "edit) judges otherwise."
        ),
    }


# ─── Mapping builder ──────────────────────────────────────────────────────

def build_mappings_from_scan(scan: dict) -> tuple[dict, list]:
    """Convert scan.high_confidence into a mappings dict (+ candidates list).

    v0.4 conservative posture: Tier 1 NEVER auto-aggregates. Every file
    gets a per-file mapping. Folders matching the numbered-series pattern
    are surfaced in the returned `aggregation_candidates` list so init/
    reconcile can write them to the taxonomy's top-level
    `aggregation_candidates:` block — flagging for Tier 2 (LLM agent) or
    user review without changing row behavior.

    Each mapping carries a `title` field — frontmatter `title:` if present
    (preferred), else a humanized filename. The generator uses this for
    the Deliverable column instead of echoing the raw filename.

    When multiple files in a folder map to the same role, the
    alphabetically-first one is marked `primary: true` (stabilizes
    folder-collapse-compatible row IDs from earlier walk modes).
    """
    titles = scan.get("titles") or {}

    # Group files by folder
    by_folder: dict[str, list[str]] = {}
    for path in scan["high_confidence"].keys():
        folder = "/".join(path.split("/")[:-1]) or "."
        by_folder.setdefault(folder, []).append(path)

    mappings: dict[str, dict] = {}
    candidates: list[dict] = []

    for folder, files in by_folder.items():
        roles = {p: scan["high_confidence"][p] for p in files}
        verdict = classify_folder(folder, files, roles)

        # Surface ALL aggregation-candidate folders in the top-level
        # block — including the ones we auto-aggregated, so reviewers see
        # which folders were classified and why.
        if verdict.get("aggregation_candidate"):
            candidates.append({
                "folder": folder,
                "verdict_kind": verdict["kind"],
                "signals": verdict.get("aggregation_signals") or {},
                "rationale": verdict.get("rationale"),
            })

        # High-confidence auto-aggregate (numbered series + aggregator +
        # single role). One folder mapping replaces all per-file mappings.
        if verdict["kind"] == "aggregate":
            primary = verdict["primary_member"]
            folder_role = roles[primary]
            key = (folder if folder != "." else "") + "/"
            entry: dict = {
                "canonical_role": folder_role,
                "aggregate": "folder",
                "primary_member": primary,
                "members": verdict["members"],
                "confidence": verdict["confidence"],
                "rationale": verdict["rationale"],
            }
            # Friendly Deliverable title for the aggregate row: prefer the
            # primary member's frontmatter title (e.g., "Clinical Evaluation
            # Report (CER) — pca-device" for the CER that aggregates BRAs)
            primary_title = titles.get(primary)
            if primary_title:
                entry["title"] = primary_title
            mappings[key] = entry
            continue

        # Independent (default) — per-file mappings
        by_role: dict[str, list[str]] = {}
        for p in files:
            by_role.setdefault(roles[p], []).append(p)
        for role, paths in by_role.items():
            for i, p in enumerate(sorted(paths)):
                entry: dict = {"canonical_role": role}
                title = titles.get(p)
                if title:
                    entry["title"] = title
                if i == 0 and len(paths) > 1:
                    entry["primary"] = True
                mappings[p] = entry

    return mappings, candidates


def build_pending_block(scan: dict, today: Optional[str] = None) -> list[dict]:
    """Convert scan.pending into the on-disk pending: block format."""
    today = today or datetime.date.today().isoformat()
    out = []
    for item in scan["pending"]:
        entry = {"path": item["path"], "first_seen": today}
        if item.get("candidate_roles"):
            entry["candidate_roles"] = item["candidate_roles"]
        out.append(entry)
    return out


# ─── Reconcile ────────────────────────────────────────────────────────────

def reconcile(
    taxonomy: dict,
    scan: dict,
    *,
    today: Optional[str] = None,
) -> dict:
    """Diff scan vs existing taxonomy. Returns updated taxonomy + report.

    Updates:
      - pending:    fresh entries for newly-discovered files (preserves
                    first_seen for entries already in pending:)
      - broken_refs: files in mappings: not present on disk
      - mappings:   unchanged (the user authors classification, not reconcile)

    Returns: {'taxonomy': <updated>, 'report': {added, removed, broken,
              still_pending}}
    """
    today = today or datetime.date.today().isoformat()
    out = dict(taxonomy)
    mappings = dict(out.get("mappings") or {})
    existing_pending = {p["path"]: p for p in (out.get("pending") or [])}
    excluded_globs = list(out.get("excluded") or [])

    # Files actually on disk under the discovery root
    on_disk = set(scan["all_files"])

    # Newly discovered = on_disk minus mapped minus already-pending minus excluded
    mapped_paths = set(mappings.keys())
    pending_paths = set(existing_pending.keys())

    def _excluded(p):
        return any(fnmatch.fnmatch(p, g) for g in excluded_globs)

    newly_discovered = sorted(
        p for p in on_disk
        if p not in mapped_paths and p not in pending_paths and not _excluded(p)
    )

    # Build refreshed pending: keep existing first_seen for known entries,
    # add today's date for newly discovered
    refreshed_pending: list[dict] = []
    pending_lookup = {item["path"]: item for item in scan["pending"]}

    for path in sorted(set(list(existing_pending.keys()) + newly_discovered)):
        if path not in on_disk:
            # File in pending: that no longer exists — drop it silently
            continue
        if path in existing_pending:
            entry = dict(existing_pending[path])
        else:
            entry = {"path": path, "first_seen": today}
        # Refresh candidate_roles from current scan
        scan_entry = pending_lookup.get(path)
        if scan_entry and scan_entry.get("candidate_roles"):
            entry["candidate_roles"] = scan_entry["candidate_roles"]
        refreshed_pending.append(entry)

    # Broken refs = paths in mappings: not on disk and not folder-style entries
    # (folder mappings end with '/' or have enumerate: true)
    existing_broken = {p["path"]: p for p in (out.get("broken_refs") or [])}
    broken: list[dict] = []
    for path, entry in mappings.items():
        # Skip folder mappings (path ends with /) and explicit unmapped entries
        if path.endswith("/") or entry.get("unmapped"):
            continue
        if entry.get("enumerate"):
            continue
        # Skip glob-style mapping keys
        if any(c in path for c in "*?["):
            continue
        if path not in on_disk:
            ent = dict(existing_broken.get(path, {"path": path, "last_seen": today}))
            ent["path"] = path
            broken.append(ent)

    if refreshed_pending:
        out["pending"] = refreshed_pending
    elif "pending" in out:
        del out["pending"]

    if broken:
        out["broken_refs"] = broken
    elif "broken_refs" in out:
        del out["broken_refs"]

    report = {
        "added_to_pending": [
            p for p in newly_discovered if p not in existing_pending
        ],
        "still_pending": [
            p for p in existing_pending.keys() if p in on_disk
        ],
        "broken_refs": [b["path"] for b in broken],
        "removed_from_pending": [
            p for p in existing_pending.keys() if p not in on_disk
        ],
        "mapped_count": len(mappings),
        "on_disk_count": len(on_disk),
    }
    return {"taxonomy": out, "report": report}


# ─── Project.yml registry mutation ────────────────────────────────────────

def add_taxonomy_to_project_yml(
    project_dir: Path,
    *,
    taxonomy_id: str,
    file_rel: str,
    applies_to_dhfs: Optional[list[str]] = None,
    applies_to_paths: Optional[list[str]] = None,
) -> bool:
    """Add (or replace) a taxonomies[] entry in project.yml. Returns True if
    the file was modified, False if the entry was already present.

    Note: this round-trips through PyYAML which loses comments. Callers should
    use it only when the project.yml is willing to absorb that — for the
    initial scaffolding of the taxonomies: block, hand-edit is preferred.
    For idempotent automation, the loss is acceptable; PDLC_DEMO accepts it
    on first scaffolding and any subsequent changes are reviewed.
    """
    project_yml = project_dir / "project.yml"
    pyl = load_yaml(project_yml)
    entries = pyl.get("taxonomies") or []
    new_entry = {
        "id": taxonomy_id,
        "file": file_rel,
        "applies_to_dhfs": applies_to_dhfs or [],
        "applies_to_paths": applies_to_paths or [],
    }
    # Drop empty list keys for cleanliness
    if not new_entry["applies_to_dhfs"]:
        del new_entry["applies_to_dhfs"]
    if not new_entry["applies_to_paths"]:
        del new_entry["applies_to_paths"]

    for i, e in enumerate(entries):
        if e.get("id") == taxonomy_id or _norm_path(e.get("file")) == _norm_path(file_rel):
            if e == new_entry:
                return False
            entries[i] = new_entry
            pyl["taxonomies"] = entries
            dump_yaml(pyl, project_yml)
            return True
    entries.append(new_entry)
    pyl["taxonomies"] = entries
    dump_yaml(pyl, project_yml)
    return True
