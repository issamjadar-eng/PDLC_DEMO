#!/usr/bin/env python3
"""
Submission Tracker — HTML Dashboard Generator (milestone-driven).

Reads docs/project/submissions/submission-tracker.md (milestone-driven shape:
per-Phase sections with sub-tables per binding source, Engineering Prerequisites,
and a Deliverable Details appendix) and emits docs/project/submissions/
submission-tracker.html.

Project-agnostic — no project-specific names hardcoded. Scope/Phase values are
discovered from the markdown; color cycle is stable across runs. Relative file
links in row paths + detail content are rewritten to project-console virtual
paths (/documents#path=<virtual>) so clicks open in the Documents tab.

Usage: python3 render.py [--project-dir PATH]
  --project-dir  Project root directory (default: detected via CLAUDE.md walk)
"""

import re
import sys
import os
from pathlib import Path
from collections import OrderedDict, Counter, defaultdict
from datetime import date


# ─── Project discovery ───

def find_project_dir():
    """Walk up from cwd looking for CLAUDE.md (project root marker)."""
    d = Path(os.getcwd())
    for _ in range(10):
        if (d / 'CLAUDE.md').exists():
            return d
        if d.parent == d:
            break
        d = d.parent
    return Path(os.getcwd())


def last_updated_date(project_dir):
    """Return the tracker's 'last updated' date as 'DD-Mon-YY' (e.g. 01-Jul-26), or None.

    Records when the tracker was genuinely last updated (not when the HTML was
    rendered). Sourced honestly per tracker source file: use the local file
    mtime when the file has uncommitted local changes (git working copy differs
    from HEAD, or the tree is not a git repo) — a locally-edited-but-uncommitted
    doc *was* just updated and its last commit date would be stale — otherwise
    the last git commit date touching it. Most recent across sources wins.
    Returns None only when no source file resolves (caller then falls back to
    the render date). Project-agnostic: degrades to plain mtime outside git."""
    import subprocess
    from datetime import datetime
    project_dir = Path(project_dir)
    sources = [
        'docs/project/submissions/submission-tracker.md',
        'docs/project/submissions/submission-tracker.overlay.yml',
    ]

    def _commit_date(rel):
        try:
            log = subprocess.run(
                ['git', '-C', str(project_dir), 'log', '-1', '--format=%cs', '--', rel],
                capture_output=True, text=True, timeout=5)
            if log.returncode == 0 and log.stdout.strip():
                return datetime.strptime(log.stdout.strip(), '%Y-%m-%d').date()
        except Exception:
            pass
        return None

    candidates = []
    for rel in sources:
        f = project_dir / rel
        if not f.is_file():
            continue
        d = None
        try:
            porcelain = subprocess.run(
                ['git', '-C', str(project_dir), 'status', '--porcelain', '--', rel],
                capture_output=True, text=True, timeout=5)
            clean = (porcelain.returncode == 0 and not porcelain.stdout.strip())
        except Exception:
            clean = False  # git unavailable / not a repo → treat as dirty (use mtime)
        if clean:
            # committer date (YYYY-MM-DD, committer's tz) — matches git log --date=short
            d = _commit_date(rel)
        if d is None:
            # uncommitted change, not a git repo, or git error → local file mtime
            d = datetime.fromtimestamp(f.stat().st_mtime).date()
        candidates.append(d)
    if not candidates:
        return None
    return max(candidates).strftime('%d-%b-%y')


def build_row_last_updated(rows, src_dir, project_dir):
    """Map deliverable row-id -> 'DD-Mon-YY' last-updated date, derived from each
    row's own evidence file (its Path-column link). Same honest sourcing as
    last_updated_date(): git commit date of the evidence file, overridden by the
    file's local mtime when it has uncommitted changes; '—' when the row has no
    resolvable in-repo evidence file (Not Started / "To be created" / external).

    Uses two scoped git calls total (log + status over just the evidence files),
    NOT one-per-row, so it stays cheap on the console live-render. Degrades to
    mtime (or '—') outside git."""
    import subprocess
    import re as _re
    from datetime import datetime
    src_dir = Path(src_dir)
    project_dir = Path(project_dir)

    link_re = _re.compile(r'\]\(([^)]+)\)')
    ev = {}  # iid -> (repo_relative_path, absolute_path)
    for r in rows:
        pf = r.get('path') or ''
        m = link_re.search(pf)
        target = m.group(1) if m else None
        if not target:
            continue
        target = target.split('#')[0].strip()
        if not target or target.startswith(('http://', 'https://', 'mailto:', '/')):
            continue
        ab = (src_dir / target).resolve()
        try:
            rel = os.path.relpath(ab, project_dir).replace(os.sep, '/')
        except Exception:
            continue
        if rel.startswith('..'):
            continue  # outside the repo
        ev[r['id']] = (rel, ab)

    rels = sorted({rel for rel, _ in ev.values()})

    # Dirty set — one git-status call over just the evidence files.
    dirty = set()
    if rels:
        try:
            st = subprocess.run(
                ['git', '-C', str(project_dir), 'status', '--porcelain', '--', *rels],
                capture_output=True, text=True, timeout=10)
            if st.returncode == 0:
                for line in st.stdout.splitlines():
                    p = line[3:].strip()
                    if ' -> ' in p:  # rename: "old -> new"
                        p = p.split(' -> ', 1)[1]
                    dirty.add(p.strip().strip('"'))
        except Exception:
            pass

    # Commit date per file — one `git log -1 --format=%cs` per (non-dirty) file,
    # run CONCURRENTLY (the cost is subprocess spawns, not git). `%cs` is the
    # committer date (YYYY-MM-DD, committer's tz, matching `git log --date=short`)
    # so a late-evening commit doesn't roll to the next day for a viewer.
    #
    # Why per-file rather than one bulk `git log --name-only` pass: a bulk pass
    # attributes the *merge* commit's date (and omits merge-only files) instead
    # of the content-commit date these per-file queries return; parallelising the
    # per-file calls is byte-identical to the sequential version and ~7x faster.
    def _commit_date(rel):
        try:
            r = subprocess.run(
                ['git', '-C', str(project_dir), 'log', '-1', '--format=%cs', '--', rel],
                capture_output=True, text=True, timeout=10)
            if r.returncode == 0 and r.stdout.strip():
                return rel, datetime.strptime(r.stdout.strip(), '%Y-%m-%d').date()
        except Exception:
            pass
        return rel, None

    to_lookup = [rel for rel in rels if rel not in dirty]  # dirty files use mtime
    commit_dates = {}
    if to_lookup:
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=min(16, len(to_lookup))) as ex:
            for rel, d in ex.map(_commit_date, to_lookup):
                commit_dates[rel] = d

    result = {}
    for iid, (rel, ab) in ev.items():
        d = None
        if rel in dirty:
            if ab.is_file():
                d = datetime.fromtimestamp(ab.stat().st_mtime).date()
        else:
            d = commit_dates.get(rel)
            if d is None and ab.is_file():  # untracked / not in history
                d = datetime.fromtimestamp(ab.stat().st_mtime).date()
        result[iid] = d.strftime('%d-%b-%y') if d else '—'
    return result


def project_subtitle(project_dir):
    """Build the tracker subtitle from project.yml if available."""
    try:
        text = (project_dir / 'project.yml').read_text()
        name_m = re.search(r'^\s{2}name:\s*(.+?)\s*$', text, re.MULTILINE)
        pathway_m = re.search(r'^\s{2}regulatory_pathway:\s*(.+?)\s*$', text, re.MULTILINE)
        name = name_m.group(1).strip() if name_m else 'Project'
        pathway = (pathway_m.group(1).strip() if pathway_m else '510k').lower()
        pathway_label = {'510k': '510(k)', '510k+pccp': '510(k) + PCCP', 'denovo': 'De Novo', 'pma': 'PMA',
                         'mdr': 'EU MDR', 'ind': 'IND', 'nda': 'NDA',
                         'ivd': 'IVD', 'ce': 'CE Mark'}.get(pathway, pathway.upper())
        return f'{name} — {pathway_label} milestone-driven readiness'
    except Exception:
        return 'Submission Package Tracker'


# ─── Tracker config from project.yml (R10 portability) ───
# All fields optional — skill defaults are HCLS-sensible; projects override
# only what their tool chain or vocabulary requires. See SKILL.md HCLS
# Portability section for the schema.

DEFAULT_TRACKER_CONFIG = {
    'coverage_thresholds': {
        'in_review_min': 70,
        'draft_min': 30,
        'scaffold_max': 30,
    },
    'display': {
        'scope_label_max_chars': 12,
        'architecture_short_overrides': {},
    },
    'lifecycle_plugin': 'confluence_comala',
}


def load_tracker_config(project_dir):
    """Read project.yml `tracker:` block; merge with defaults.

    Avoids a YAML dependency at this layer — does best-effort regex parse for
    the fields render.py uses today (display.scope_label_max_chars,
    display.architecture_short_overrides). Future fields (status_vocabulary,
    coverage_thresholds, lifecycle_plugin) load via full YAML parse in
    /tracker assess + /tracker generate when those actions ship.
    """
    cfg = {k: dict(v) if isinstance(v, dict) else v for k, v in DEFAULT_TRACKER_CONFIG.items()}
    try:
        text = (project_dir / 'project.yml').read_text()
    except Exception:
        return cfg

    # display.scope_label_max_chars
    m = re.search(r'^\s{4}scope_label_max_chars:\s*(\d+)\s*$', text, re.MULTILINE)
    if m:
        cfg['display']['scope_label_max_chars'] = int(m.group(1))

    # display.architecture_short_overrides — block-scalar style
    m = re.search(r'^\s{4}architecture_short_overrides:\s*\n((?:\s{6}.+\n?)+)', text, re.MULTILINE)
    if m:
        for line in m.group(1).split('\n'):
            kv = re.match(r'^\s{6}([\w-]+):\s*(.+?)\s*(?:#.*)?$', line)
            if kv:
                cfg['display']['architecture_short_overrides'][kv.group(1)] = kv.group(2).strip()

    # lifecycle_plugin
    m = re.search(r'^\s{2}lifecycle_plugin:\s*(\S+)\s*$', text, re.MULTILINE)
    if m:
        cfg['lifecycle_plugin'] = m.group(1)

    # coverage_thresholds — best-effort
    for key in ('in_review_min', 'draft_min', 'scaffold_max'):
        m = re.search(rf'^\s{{4}}{key}:\s*(\d+)\s*$', text, re.MULTILINE)
        if m:
            cfg['coverage_thresholds'][key] = int(m.group(1))

    return cfg


# ─── URL rewriting ───

def rewrite_url(url, src_dir, repo_root):
    """Rewrite relative file links to /documents#path=<virtual-path>.

    External URLs (http/https/mailto), absolute paths (/...), and pure
    anchors (#...) are returned unchanged.
    """
    if not url:
        return url
    frag = ''
    if '#' in url and not url.startswith('#'):
        url, frag = url.split('#', 1)
        frag = '#' + frag
    if url.startswith(('http://', 'https://', 'mailto:', '/')) or url.startswith('#'):
        return url + frag if frag else url
    try:
        target = (src_dir / url).resolve()
        rel = target.relative_to(repo_root)
        return f'/documents#path={rel}{frag}'
    except (ValueError, OSError):
        return url + frag


def md_inline_to_html(text, src_dir=None, repo_root=None):
    """Render minimal markdown inline tokens (links, bold, code) to HTML."""
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)

    def link_sub(match):
        label, url = match.group(1), match.group(2)
        if src_dir and repo_root:
            url = rewrite_url(url, src_dir, repo_root)
        return f'<a href="{url}">{label}</a>'
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', link_sub, text)
    return text


# ─── B6 Create Draft button wiring ───
#
# Source markdown carries `<button class="tracker-action-btn" disabled>Create Draft</button>`
# in the Path cell of every row that needs an artifact authored. The renderer
# rewrites those disabled buttons into live ones with `data-row-id` +
# `data-action="create-draft"` so `tracker_interactive.js` picks them up.
#
# When an in-progress draft exists for a row (file at `_drafting/<row-id>-*.md`),
# the button label flips to "Edit Draft" and `data-draft-state` carries the
# stage badge.

_CREATE_DRAFT_BTN_RE = re.compile(
    r'<button\s+class="tracker-action-btn"\s+disabled\s*>\s*Create Draft\s*</button>',
    re.IGNORECASE,
)

_DRAFT_ELIGIBLE_STATUSES = {
    'Not Started', 'Drafting', 'Drafted', 'Needs Revision',
}


def find_draft_stage(project_dir, row_id):
    """Probe project root `_drafting/` for an in-progress draft for this row.

    Returns one of: None (no draft), 'outline', 'drafting', 'drafted'.
    """
    drafting = Path(project_dir) / '_drafting'
    if not drafting.is_dir():
        return None
    matches = list(drafting.glob(f'{row_id}-*.md'))
    if not matches:
        return None
    f = max(matches, key=lambda p: p.stat().st_mtime)
    try:
        head_lines = f.read_text(errors='replace').split('\n', 200)
    except Exception:
        return 'drafting'
    fm = []
    if head_lines and head_lines[0].strip() == '---':
        for line in head_lines[1:]:
            if line.strip() == '---':
                break
            fm.append(line)
    fm_text = '\n'.join(fm)

    def _has_iso_value(key):
        marker = f'{key}:'
        if marker not in fm_text:
            return False
        tail = fm_text.split(marker, 1)[1].split('\n', 1)[0].strip()
        return tail and tail.lower() not in ('null', '~', '')

    if _has_iso_value('synthesis_completed_at'):
        return 'drafted'
    if _has_iso_value('outline_approved_at'):
        return 'drafting'
    return 'outline'


def wire_create_draft_button(html, row_id, status, draft_stage=None):
    """Rewrite a disabled Create Draft button in `html` into a wired one.

    No match or ineligible status → return `html` unchanged. When `draft_stage`
    is set, flip label to 'Edit Draft' and emit `data-draft-state`.
    """
    if not _CREATE_DRAFT_BTN_RE.search(html):
        return html
    if status not in _DRAFT_ELIGIBLE_STATUSES:
        return html
    label = 'Edit Draft' if draft_stage else 'Create Draft'
    attrs = [
        'class="tracker-action-btn"',
        f'data-row-id="{row_id}"',
        'data-action="create-draft"',
    ]
    if draft_stage:
        attrs.append(f'data-draft-state="{draft_stage}"')
    badge = f' <span class="draft-stage-badge" title="Draft stage">{draft_stage}</span>' if draft_stage else ''
    new_btn = f'<button {" ".join(attrs)}>{label}{badge}</button>'
    return _CREATE_DRAFT_BTN_RE.sub(new_btn, html)


def detail_md_to_html(md, src_dir=None, repo_root=None):
    """Convert detail-block markdown to compact HTML for click-row expansion."""
    out = []
    in_list = False
    for raw in md.split('\n'):
        line = raw.rstrip()
        if not line:
            if in_list:
                out.append('</ul>')
                in_list = False
            continue
        if line.startswith('- '):
            if not in_list:
                out.append('<ul>')
                in_list = True
            out.append(f'<li>{md_inline_to_html(line[2:], src_dir, repo_root)}</li>')
        else:
            if in_list:
                out.append('</ul>')
                in_list = False
            out.append(f'<p>{md_inline_to_html(line, src_dir, repo_root)}</p>')
    if in_list:
        out.append('</ul>')
    return '\n'.join(out)


# ─── Parser (milestone-driven shape) ───

def parse_markdown(md_path):
    """Parse milestone-driven submission-tracker.md.

    Returns dict with:
        rows[]    — deliverable rows (id, name, scope, phase, ref, effort, status, path, subsection)
        eng[]     — engineering prereqs (id, name, scope, phase, effort, status, gates)
        details   — dict id → detail markdown body
        scales    — dict {status, phase, effort} → list of {label, definition} rows from Scale sections
    """
    md = Path(md_path).read_text()
    rows, eng, details = [], [], {}
    scales = {'status': [], 'phase': [], 'effort': []}
    in_scale = None  # 'status' | 'phase' | 'effort' | None
    scale_h2 = re.compile(r'^## (Status|Phase|Effort) Scale\s*$')
    current_phase = None
    current_subsection = None
    in_eng = False
    in_details = False
    current_detail_id = None
    current_detail_buf = []

    phase_h2 = re.compile(r'^## Phase:\s*(.+?)\s*$')
    eng_h2 = re.compile(r'^## Engineering Prerequisites')
    details_h2 = re.compile(r'^## Deliverable Details')
    end_h2 = re.compile(r'^## ')
    subsection_h3 = re.compile(r'^### (.+?)\s*$')
    detail_h3 = re.compile(r'^### ([A-Z][A-Z0-9-]+) — (.+?)\s*$')
    # Deliverable row: 8 columns (# | Deliverable | Scope | Phase | REF | Effort | Status | Path)
    row_re = re.compile(
        r'^\| ([A-Z][A-Z0-9-]+) \| (.+?) \| (.+?) \| (.+?) \| (.+?) \| (.+?) \| (.+?) \| (.+?) \|\s*$'
    )
    # ENG row: 7 columns (# | Prerequisite | Scope | Phase | Effort | Status | Gates)
    eng_re = re.compile(
        r'^\| (ENG\d+) \| (.+?) \| (.+?) \| (.+?) \| (.+?) \| (.+?) \| (.+?) \|\s*$'
    )

    def flush_detail():
        nonlocal current_detail_id, current_detail_buf
        if current_detail_id and current_detail_buf:
            details[current_detail_id] = '\n'.join(current_detail_buf).strip()
        current_detail_id = None
        current_detail_buf = []

    for line in md.split('\n'):
        m = phase_h2.match(line)
        if m:
            flush_detail()
            current_phase = m.group(1).strip()
            current_subsection = None
            in_eng = False
            in_details = False
            continue
        if eng_h2.match(line):
            flush_detail()
            in_eng = True; in_details = False
            current_phase = None; current_subsection = None
            continue
        if details_h2.match(line):
            flush_detail()
            in_details = True; in_eng = False
            current_phase = None; current_subsection = None
            continue
        # Scale section heading (## Status Scale / ## Phase Scale / ## Effort Scale)
        # — checked BEFORE the in_details exit so a scale heading immediately after
        # Deliverable Details doesn't get swallowed by the in_details ## exit.
        m_sc = scale_h2.match(line)
        if m_sc:
            flush_detail()
            in_scale = m_sc.group(1).lower()
            current_phase = None; current_subsection = None
            in_eng = False; in_details = False
            continue
        if in_details and end_h2.match(line) and not details_h2.match(line):
            flush_detail()
            in_details = False
            continue

        # Any unrecognized ## heading exits all parsing modes
        if end_h2.match(line):
            current_phase = None; current_subsection = None
            in_eng = False; in_details = False; in_scale = None
            continue

        # Capture Scale section table rows (key | definition[ | extra...])
        if in_scale and line.startswith('|') and '|' in line[1:]:
            cells = [c.strip() for c in line.strip().strip('|').split('|')]
            # Skip header + separator rows
            if not cells or len(cells) < 2:
                continue
            first = cells[0].strip('*').strip()
            if first in ('', 'Status', 'Phase', 'Effort') or set(first).issubset(set(':-')):
                continue
            # Strip surrounding ** from the label
            label = re.sub(r'^\*\*|\*\*$', '', first).strip()
            definition = cells[-1]
            scales[in_scale].append({'label': label, 'definition': definition, 'extra': cells[1:-1]})
            continue

        m_sub = subsection_h3.match(line)
        if m_sub and current_phase:
            heading = m_sub.group(1).strip()
            if '(' in heading:
                heading = heading[:heading.index('(')].rstrip()
            current_subsection = heading
            continue
        if m_sub and in_details:
            flush_detail()
            md_match = detail_h3.match(line)
            if md_match:
                current_detail_id = md_match.group(1)
                current_detail_buf = [f"**{md_match.group(2).strip()}**"]
            continue

        if in_details and current_detail_id:
            current_detail_buf.append(line)
            continue

        if in_eng:
            m = eng_re.match(line)
            if m:
                eng.append({
                    'id': m.group(1).strip(),
                    'name': m.group(2).strip(),
                    'scope': m.group(3).strip(),
                    'phase': m.group(4).strip(),
                    'effort': m.group(5).strip(),
                    'status': coerce_status(re.sub(r'[*:]', '', m.group(6)).strip()),
                    'gates': m.group(7).strip(),
                })
            continue

        if current_phase:
            m = row_re.match(line)
            if not m or m.group(1).strip() == '#':
                continue
            rows.append({
                'id': m.group(1).strip(),
                'name': m.group(2).strip(),
                'scope': m.group(3).strip(),
                'phase': m.group(4).strip(),
                'ref': m.group(5).strip(),
                'effort': m.group(6).strip(),
                'status': coerce_status(re.sub(r'[*]', '', m.group(7)).strip()),
                'path': m.group(8).strip(),
                'subsection': current_subsection or '(all bindings)',
            })

    flush_detail()
    return {'rows': rows, 'eng': eng, 'details': details, 'scales': scales}


# ─── Validation (advisory) ───
#
# 7-state lifecycle vocabulary (locked in 2026-05-03). Source of truth =
# project.yml `tracker.status_vocabulary`. The set below is the canonical
# display-label form. `STATUS_ALIAS_MAP` coerces legacy v7 values + project.yml
# alias entries to their canonical form so the renderer keeps working
# while md rows are migrated row-by-row.

VALID_STATUSES = {
    'Not Started', 'Drafting', 'Drafted', 'In Review',
    'Needs Revision', 'Approved', 'N/A',
}

# Legacy values (v7 vocab) → canonical 7-state value. Renderer coerces at
# parse time; validator no longer warns on legacy values that have a known
# alias mapping. Drives both Status and AI Status columns.
STATUS_ALIAS_MAP = {
    'Done': 'Approved',
    'Complete': 'Approved',
    'Released': 'Approved',
    'In Progress': 'Drafting',
    'Partial': 'Drafting',
    'WIP': 'Drafting',
    # Inherited is provenance, not lifecycle — coerce to Approved until the
    # 🔗 provenance marker lands as a separate row attribute.
    'Inherited': 'Approved',
    'Needs Rev': 'Needs Revision',
}


def coerce_status(s):
    """Normalize a legacy status value to its canonical 7-state form.
    Returns the input unchanged if already canonical."""
    if not s:
        return s
    s = s.strip()
    if s in VALID_STATUSES:
        return s
    return STATUS_ALIAS_MAP.get(s, s)


# ─── Human overlay (submission-tracker.human.json) — render-time merge ───
#
# The overlay is the durable record of human-curated divergence from the
# generator's structural view. Console writes (Save & Publish) update the
# overlay JSON, NOT the md cell. At render time we merge:
#     md row    (generator-owned: id, name, scope, phase, ref, effort,
#                status-baseline, path)
#   + overlay   (human-curated: status, ref override, notes, owner,
#                target_date, blockers, pinned_decision, updated_at,
#                updated_by)
#   = resolved row rendered to html.
#
# Schema (per task-154 design contract):
#   {
#     "schema_version": "0.1",
#     "rows": {
#       "<row_id>": {
#         "status": "Drafted" | ... ,    # overrides md cell
#         "ref": "..." | null,           # overrides generator's REF pick
#         "notes": "free-form text",
#         "owner": "BX" | null,
#         "target_date": "2026-06-15" | null,
#         "blockers": ["ENG3", "..."] | null,
#         "pinned_decision": "docs/project/strategies/..." | null,
#         "updated_at": "ISO8601",
#         "updated_by": "actor name"
#       }
#     }
#   }


def load_human_overlay(project_dir):
    """Return the per-row overlay map keyed by row ID. Reads the unified
    tracker overlay sidecar (`submission-tracker.overlay.yml`, `rows` section).

    Falls back to the legacy `submission-tracker.human.json` location when the
    unified sidecar is absent, so projects that adopted the older JSON-format
    overlay continue to work without migration. Empty dict if neither file is
    present or both are malformed (best-effort; never raises).
    """
    # Preferred: unified YAML overlay
    overlay_yml = Path(project_dir) / 'docs/project/submissions/submission-tracker.overlay.yml'
    if overlay_yml.is_file():
        try:
            import yaml  # type: ignore
        except ImportError:
            # PyYAML missing but an overlay exists → the render would silently
            # ignore every human-curated status/path/ref override and emit the
            # raw generator markdown, producing output that looks correct but
            # diverges from what a yaml-enabled environment (e.g. the project
            # console venv) serves. Warn loudly rather than mislead; do NOT run
            # `render.py` with a bare interpreter when an overlay is present.
            sys.stderr.write(
                "WARNING: submission-tracker.overlay.yml exists but PyYAML is "
                "not installed — overlay overrides (status/path/ref) are being "
                "IGNORED. This render will NOT match the console. Install "
                "PyYAML or run via the console venv.\n"
            )
        else:
            try:
                data = yaml.safe_load(overlay_yml.read_text(encoding='utf-8')) or {}
                rows = data.get('rows') if isinstance(data, dict) else None
                if isinstance(rows, dict):
                    return rows
                return {}
            except Exception:
                pass  # malformed overlay — fall through to legacy
    # Legacy: human.json (pre-overlay-unification)
    import json
    sidecar = Path(project_dir) / 'docs/project/submissions/submission-tracker.human.json'
    if not sidecar.is_file():
        return {}
    try:
        data = json.loads(sidecar.read_text(encoding='utf-8'))
    except Exception:
        return {}
    rows = data.get('rows') if isinstance(data, dict) else None
    return rows if isinstance(rows, dict) else {}


def apply_human_overlay(rows, overlay):
    """Merge overlay onto generated rows in place. Each row dict gains a
    `human` key with the overlay payload; cell-level overrides for
    `name` / `status` / `effort` / `ref` / `path` are applied when the
    overlay supplies them. Unmatched overlay row IDs are silently ignored
    (operators see them via /tracker generate's stderr orphan warnings —
    not the renderer's concern).

    Field-override set (per-row):
      - `name`   → renders in the Deliverable column (overrides whatever
                   generate.py emitted, including the per-(DHF, role)
                   default from overlay.defaults.by_dhf_role)
      - `status` → Status column (coerced via STATUS_ALIAS_MAP)
      - `effort` → Effort column
      - `ref`    → REF column
      - `path`   → Path column (may be raw HTML, e.g. the B6 Create Draft
                   disabled-button placeholder that render.py later wires
                   into a live button)

    Metadata fields (`owner` / `target_date` / `blockers` / `notes`)
    pass through in `target['human']` for downstream consumers (detail
    panels, etc.) but don't directly override a cell.
    """
    if not overlay:
        return rows
    by_id = {r['id']: r for r in rows}
    # Renderer's parsed rows use `name` (not `name_token` — that's generate.py's
    # internal field). Accept either key from the overlay author so the same
    # sidecar shape works whether you think in render-side or generate-side terms.
    for row_id, entry in overlay.items():
        target = by_id.get(row_id)
        if target is None:
            continue
        # Carry the full overlay payload as a nested block (renderer can
        # surface owner / target_date / blockers / notes in the Detail panel).
        target['human'] = dict(entry)
        # Apply the cell-level overrides.
        name_val = entry.get('name') or entry.get('name_token')
        if name_val:
            target['name'] = name_val
        if entry.get('status'):
            target['status'] = coerce_status(entry['status'])
        if entry.get('effort'):
            target['effort'] = entry['effort']
        if entry.get('ref'):
            target['ref'] = entry['ref']
        if entry.get('path'):
            target['path'] = entry['path']
    return rows


def validate(data):
    warnings, errors = [], []
    seen_ids = set()
    for r in data['rows']:
        if r['id'] in seen_ids:
            errors.append(f"Duplicate row ID: {r['id']}")
        seen_ids.add(r['id'])
        canon = coerce_status(r['status'])
        if canon not in VALID_STATUSES:
            warnings.append(f"{r['id']}: unknown Status '{r['status']}'")
    for e in data['eng']:
        if e['id'] in seen_ids:
            errors.append(f"Duplicate ID (eng vs row): {e['id']}")
        seen_ids.add(e['id'])
        canon = coerce_status(e['status'])
        if canon not in VALID_STATUSES:
            warnings.append(f"{e['id']}: unknown Status '{e['status']}'")
    return errors, warnings


# ─── Slugification + class helpers ───

def slug(s):
    return re.sub(r'[^a-z0-9]+', '-', (s or '').lower()).strip('-') or 'unset'


def status_class(s):
    return f'status-badge {slug(s)}'


# ─── AI Status (R7) — separate first-class column sourced from
# `submission-tracker.agent.json` sidecar. Render-time only; the agent that
# populates the sidecar is owned by `/tracker assess` (separate action).

def load_agent_sidecar(project_dir):
    """Return per-row AI-status map keyed by row ID. Schema:
        {row_id: {"value": str, "rationale": str?, "analyzed_at": str?,
                  "source_hash": str?, "sources_consulted": list?}}
    Returns {} when the sidecar is missing or malformed."""
    import json
    sidecar = Path(project_dir) / 'docs/project/submissions/submission-tracker.agent.json'
    if not sidecar.is_file():
        return {}
    try:
        data = json.loads(sidecar.read_text(encoding='utf-8'))
    except Exception:
        return {}
    rows = data.get('rows') if isinstance(data, dict) else None
    if not isinstance(rows, dict):
        return {}
    return rows


def load_details_sidecar(project_dir):
    """Return per-row deterministic detail map, keyed by row ID. Schema:
        {row_id: detail_md_body}
    The sidecar's `entries[]` list each carries `row_ids: [...]` (multi-row
    attachment); we expand to one entry per row id. Each row's body is
    composed from the structured fields (phase_text, scope, path,
    primary_ref, all_applicable_refs, notes) into the same markdown shape
    the inline `## Deliverable Details` blocks use, so detail_md_to_html()
    can render it without changes.

    When the sidecar is missing or malformed, returns {}.

    Populated by /tracker enrich-details (details-author agent) — see
    .claude/skills/tracker/agents/details-author.md."""
    import json
    sidecar = Path(project_dir) / 'docs/project/submissions/submission-tracker.details.json'
    if not sidecar.is_file():
        return {}
    try:
        data = json.loads(sidecar.read_text(encoding='utf-8'))
    except Exception:
        return {}
    entries = data.get('entries') if isinstance(data, dict) else None
    if not isinstance(entries, list):
        return {}
    out = {}
    for e in entries:
        if not isinstance(e, dict):
            continue
        row_ids = e.get('row_ids') or []
        if not isinstance(row_ids, list) or not row_ids:
            continue
        body = _details_entry_to_md(e)
        if not body:
            continue
        for rid in row_ids:
            if isinstance(rid, str):
                out[rid] = body
    return out


def _details_entry_to_md(entry):
    """Compose a structured details entry into the same markdown shape that
    inline `### <ID> — <name>` blocks use. detail_md_to_html() then renders
    it identically to the legacy path."""
    parts = []
    phase_text = entry.get('phase_text')
    scope = entry.get('scope')
    path = entry.get('path')
    primary_ref = entry.get('primary_ref')
    refs = entry.get('all_applicable_refs') or []
    notes = entry.get('notes')

    if phase_text or scope or path:
        meta_bits = []
        if phase_text:
            meta_bits.append(f'**Phase**: {phase_text}')
        if scope:
            meta_bits.append(f'**Scope**: {scope}')
        if path:
            meta_bits.append(f'**Path**: `{path}`')
        parts.append(' · '.join(meta_bits))
    if primary_ref:
        parts.append(f'- **Primary REF**: {primary_ref}')
    if refs:
        parts.append('- **All applicable REFs**:')
        for r in refs:
            parts.append(f'  - {r}')
    if notes:
        parts.append(f'- **Notes**: {notes}')

    return '\n'.join(parts).strip()


def load_row_source_sidecar(project_dir):
    """Return per-row source_kind map from submission-tracker.row-source.json
    written by /tracker generate (Model D). Schema:
        {row_id: {source_kind: "user"|"derived", reason?: str, ...}}
    Returns {} when the sidecar is missing or malformed. When present,
    user-injected rows get a small "user-added" badge in the row chrome
    with the `reason` as a hover-tooltip."""
    import json
    sidecar = Path(project_dir) / 'docs/project/submissions/submission-tracker.row-source.json'
    if not sidecar.is_file():
        return {}
    try:
        data = json.loads(sidecar.read_text(encoding='utf-8'))
    except Exception:
        return {}
    rows = data.get('rows') if isinstance(data, dict) else None
    return rows if isinstance(rows, dict) else {}


def source_badge_html(iid, row_source_map):
    """Return a small inline badge for user-injected rows; empty string for
    catalog-derived rows. Tooltip surfaces the `reason` so reviewers can
    see why this row is user-injected vs. catalog-derived."""
    entry = row_source_map.get(iid) or {}
    if entry.get('source_kind') != 'user':
        return ''
    reason = (entry.get('reason') or 'user-injected row (not derived from milestone catalog)')
    return (f'<span class="row-icon source-user" '
            f'title="user-added: {_esc(reason)}">★</span>')


def load_help_sidecar(project_dir):
    """Return per-row LLM-generated help map, keyed by row ID. Schema:
        {row_id: {"title": str, "description": str, "why_important_in_project": str,
                  "main_topics": [{"name": str, "summary": str}],
                  "regulatory_anchors": [{"citation": str, "role": str}],
                  "generated_at": str?, "context_signature": dict?}}
    Returns {} when the sidecar is missing or malformed. Populated by the
    /tracker help (help-author agent) — see .claude/skills/tracker/agents/help-author.md."""
    import json
    sidecar = Path(project_dir) / 'docs/project/submissions/submission-tracker.help.json'
    if not sidecar.is_file():
        return {}
    try:
        data = json.loads(sidecar.read_text(encoding='utf-8'))
    except Exception:
        return {}
    rows = data.get('rows') if isinstance(data, dict) else None
    if not isinstance(rows, dict):
        return {}
    return rows


def _esc(s):
    """Minimal HTML-escape for help content text fields."""
    if s is None:
        return ''
    return (str(s).replace('&', '&amp;').replace('<', '&lt;')
                  .replace('>', '&gt;').replace('"', '&quot;'))


def help_row_html(row_id, help_map, colspan):
    """Return the `<tr class="help-row">` HTML for a row's LLM-generated help
    panel. Falls back to a 'not generated yet' placeholder when no entry."""
    entry = help_map.get(row_id) if isinstance(help_map, dict) else None
    if not entry:
        return (f'<tr class="help-row"><td colspan="{colspan}">'
                f'<div class="help-content help-empty">'
                f'❓ No help generated yet for <code>{_esc(row_id)}</code> &mdash; '
                f'run <code>/tracker help</code> to populate via the help-author agent.'
                f'</div></td></tr>')
    parts = ['<div class="help-content">']
    title = entry.get('title') or row_id
    parts.append(f'<h4>What is {_esc(title)}?</h4>')
    parts.append(f'<p>{_esc(entry.get("description") or "")}</p>')
    why = entry.get('why_important_in_project') or entry.get('why_important')
    if why:
        parts.append('<h4>Why it matters in this project</h4>')
        parts.append(f'<p>{_esc(why)}</p>')
    topics = entry.get('main_topics') or []
    if topics:
        parts.append('<h4>Main topics</h4><ul>')
        for t in topics:
            if isinstance(t, dict):
                name = _esc(t.get('name') or '')
                summary = _esc(t.get('summary') or '')
                parts.append(f'<li><strong>{name}</strong>: {summary}</li>')
            else:
                parts.append(f'<li>{_esc(t)}</li>')
        parts.append('</ul>')
    anchors = entry.get('regulatory_anchors') or []
    if anchors:
        rendered = []
        for a in anchors:
            if isinstance(a, dict):
                cit = _esc(a.get('citation') or '')
                role = a.get('role') or ''
                if role and role != 'primary':
                    rendered.append(f'<code>{cit}</code> <span style="opacity:.7">({_esc(role)})</span>')
                else:
                    rendered.append(f'<code>{cit}</code>')
            else:
                rendered.append(f'<code>{_esc(a)}</code>')
        parts.append('<div class="anchors"><strong>Regulatory anchors:</strong> ' +
                     ' · '.join(rendered) + '</div>')
    parts.append('</div>')
    return f'<tr class="help-row"><td colspan="{colspan}">{"".join(parts)}</td></tr>'


def ai_status_cell(row_id, agent_map):
    """Return the `<td>` HTML for the AI Status column. Falls back to a
    `not-analyzed` placeholder when the row has no sidecar entry."""
    entry = agent_map.get(row_id) if isinstance(agent_map, dict) else None
    if not entry:
        return ('<td class="ai-status-col"><span class="status-badge ai-status not-analyzed" '
                'title="not analyzed yet — run /tracker assess">🤖 —</span></td>')
    value = (entry.get('value') or '').strip() or '—'
    klass = f'status-badge ai-status {slug(value)}'
    title_bits = []
    if entry.get('analyzed_at'):
        title_bits.append(f"analyzed_at: {entry['analyzed_at']}")
    if entry.get('rationale'):
        rat = entry['rationale']
        if len(rat) > 200:
            rat = rat[:197] + '…'
        title_bits.append(rat)
    title_attr = ''
    if title_bits:
        title_attr = ' title="' + ' · '.join(b.replace('"', '&quot;') for b in title_bits) + '"'
    return f'<td class="ai-status-col"><span class="{klass}"{title_attr}>🤖 {value}</span></td>'


def scope_class(s):
    return f'scope-badge {slug(s)}'


def phase_class(p):
    return f'phase-badge {slug(p)}'


def effort_class(e):
    # Normalize V.High → vhigh; Low/Med/High pass through slug
    s = slug(e).replace('v-high', 'vhigh')
    return f'effort-badge {s}'


SCOPE_COLOR_CYCLE = [
    ('--accent', 'rgba(56,189,248,.15)'),
    ('--cyan', 'rgba(6,182,212,.15)'),
    ('--accent2', 'rgba(129,140,248,.15)'),
    ('--orange', 'rgba(249,115,22,.15)'),
    ('--pink', 'rgba(236,72,153,.15)'),
    ('--text-muted', 'rgba(148,163,184,.15)'),
]
PHASE_COLOR_CYCLE = [
    ('--accent', 'rgba(56,189,248,.2)'),
    ('--accent2', 'rgba(129,140,248,.2)'),
    ('--green', 'rgba(34,197,94,.15)'),
    ('--orange', 'rgba(249,115,22,.15)'),
    ('--text-muted', 'rgba(148,163,184,.15)'),
]


def gen_dynamic_css(scope_values, phase_values):
    out = []
    for i, val in enumerate(sorted(scope_values)):
        fg, bg = SCOPE_COLOR_CYCLE[i % len(SCOPE_COLOR_CYCLE)]
        out.append(f'.scope-badge.{slug(val)}{{background:{bg};color:var({fg})}}')
    for i, val in enumerate(sorted(phase_values)):
        fg, bg = PHASE_COLOR_CYCLE[i % len(PHASE_COLOR_CYCLE)]
        out.append(f'.phase-badge.{slug(val)}{{background:{bg};color:var({fg})}}')
    return '\n'.join(out)


# ─── Brand theme alignment (optional project-console coupling) ───
#
# Best-effort: if the project ships a project-console with an active theme pack,
# pull its brand `primary` + `font_body` so the embedded dashboard visually
# belongs to the console it renders inside (iframe = isolated document; it does
# NOT inherit the console's CSS or theme tokens, so we mirror them here).
#
# The brand color lives in the theme pack — read it, don't redeclare it. Falls
# back silently to the self-contained slate+sky defaults baked into
# `_CSS_BASE_INNER`, so the skill stays standalone and project-agnostic with no
# hard dependency on project-console. Regex line-parsed to avoid a YAML dep
# (same approach as load_tracker_config).

def _read_theme_yaml(path):
    """Best-effort scalar parse of a theme.yaml (key: value lines)."""
    out = {}
    try:
        for line in path.read_text().splitlines():
            m = re.match(r'^([a-z_]+):\s*(.+?)\s*$', line)
            if not m:
                continue
            # Strip a trailing inline comment only when the `#` is whitespace-
            # preceded — otherwise it would eat hex color values like "#a855f7".
            val = re.sub(r'\s+#.*$', '', m.group(2)).strip().strip('"\'')
            if val:
                out[m.group(1)] = val
    except Exception:
        pass
    return out


def load_brand_theme(project_dir):
    """Resolve {brand, font} from the active project-console theme pack, or {}.

    console.yaml `theme:` -> theme pack `theme.yaml` (project themes dir first,
    then the skill's bundled themes), following `extends:` up the chain.
    """
    project_dir = Path(project_dir)
    try:
        ctext = (project_dir / 'tools/project-console/console.yaml').read_text()
    except Exception:
        return {}
    tm = re.search(r'^theme:\s*(.+?)\s*$', ctext, re.MULTILINE)
    if not tm:
        return {}
    theme_name = tm.group(1).split('#', 1)[0].strip().strip('"\'')

    search_dirs = [
        project_dir / 'tools/project-console/themes',
        project_dir / '.claude/skills/project-console/themes',
    ]

    def resolve(name, seen):
        if name in seen:            # cycle guard
            return {}
        seen.add(name)
        for base in search_dirs:
            ty = base / name / 'theme.yaml'
            if ty.exists():
                data = _read_theme_yaml(ty)
                merged = {}
                if data.get('extends'):
                    merged.update(resolve(data['extends'], seen))
                merged.update(data)  # child wins
                return merged
        return {}

    data = resolve(theme_name, set())
    tokens = {}
    if data.get('primary'):
        tokens['brand'] = data['primary']
    if data.get('font_body'):
        tokens['font'] = data['font_body']
    return tokens


def gen_theme_css(tokens):
    """Emit a :root override for brand/font when a theme was resolved (else '')."""
    if not tokens:
        return ''
    decls = []
    if tokens.get('brand'):
        decls.append(f"--brand:{tokens['brand']}")
    if tokens.get('font'):
        decls.append(f"--font:{tokens['font']}")
    return ':root{' + ';'.join(decls) + '}' if decls else ''


# ─── CSS — preserved dark-theme aesthetic ───
#
# `_CSS_BASE_INNER` is the raw CSS (no `<style>` wrapper) — single source of
# truth, served as `/workflows/tracker/dashboard.css` for the inline-rendered
# dashboard view, and wrapped into `CSS_BASE` for the standalone `.html` file.

_CSS_BASE_INNER = '''
:root{--bg:#0f172a;--surface:#1e293b;--surface2:#334155;--border:#475569;--text:#e2e8f0;--text-muted:#94a3b8;--accent:#38bdf8;--accent2:#818cf8;--green:#22c55e;--yellow:#eab308;--red:#ef4444;--orange:#f97316;--cyan:#06b6d4;--pink:#ec4899;--help-bg:#1a2744;--eng:#a78bfa;--brand:var(--accent);--font:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;--shadow-sm:0 1px 2px rgba(0,0,0,.25),0 4px 14px rgba(0,0,0,.22);--shadow-md:0 2px 4px rgba(0,0,0,.3),0 12px 30px rgba(0,0,0,.34)}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:var(--font);background:var(--bg);color:var(--text);line-height:1.6;padding:2rem}
.header{text-align:center;margin-bottom:2rem;padding-bottom:1.5rem;border-bottom:1px solid var(--border)}
.header h1{font-size:1.85rem;font-weight:700;letter-spacing:-.02em;color:var(--brand);margin-bottom:.3rem}
.header .subtitle{color:var(--text-muted);font-size:.95rem}
.header .timestamp{color:var(--text-muted);font-size:.8rem;margin-top:.5rem}
.tracker-embed>.timestamp{color:var(--text-muted);font-size:.8rem;text-align:center;margin:0 0 1rem}
.controls{display:flex;gap:.4rem;justify-content:center;flex-wrap:wrap;margin-bottom:1.5rem;align-items:center}
.controls .label{font-size:.65rem;text-transform:uppercase;letter-spacing:.06em;color:var(--text-muted);font-weight:600;margin-right:.2rem}
.controls button{background:var(--surface);color:var(--text-muted);border:1px solid var(--border);border-radius:8px;padding:.35rem .7rem;font-size:.72rem;cursor:pointer;transition:all .2s}
.controls button:hover{background:var(--surface2);color:var(--text)}
.controls button.active{background:var(--brand);color:#fff;border-color:var(--brand)}
.controls .sep{border-left:1px solid var(--border);height:24px;margin:0 .15rem}
.controls label.filter-dd{display:inline-flex;align-items:center;gap:.3rem}
.controls select{background:var(--surface);color:var(--text);border:1px solid var(--border);border-radius:8px;padding:.32rem .5rem;font-size:.72rem;cursor:pointer;font-family:inherit;transition:all .2s}
.controls select:hover{background:var(--surface2)}
.controls select.filter-active{border-color:var(--brand);color:var(--brand);box-shadow:inset 0 0 0 1px var(--brand)}
.summary-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:.8rem;margin-bottom:1.5rem}
.summary-card{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:1rem;text-align:center;border-left-width:4px;box-shadow:var(--shadow-sm)}
.summary-card .label{font-size:.7rem;text-transform:uppercase;letter-spacing:.05em;color:var(--text-muted);margin-bottom:.3rem}
.summary-card .number{font-size:2rem;font-weight:700}
.summary-card .detail{font-size:.72rem;color:var(--text-muted);margin-top:.2rem}
.summary-card.total{border-left-color:var(--text)}.summary-card.total .number{color:var(--text)}
.summary-card.eng{border-left-color:var(--eng)}.summary-card.eng .number{color:var(--eng)}
.progress-section{margin-bottom:1.5rem}
.progress-row{display:flex;align-items:center;gap:.8rem;margin-bottom:.5rem}
.progress-label{width:130px;font-size:.78rem;font-weight:600;text-align:right;flex-shrink:0}
.progress-bar-container{flex:1;background:var(--surface);border-radius:8px;height:22px;overflow:hidden;display:flex;border:1px solid var(--border)}
.progress-segment{height:100%;display:flex;align-items:center;justify-content:center;font-size:.6rem;font-weight:600}
.progress-segment.done{background:var(--green);color:#000}
.progress-segment.partial{background:var(--yellow);color:#000}
.progress-segment.inherited{background:var(--accent);color:#000}
.progress-stats{width:80px;font-size:.75rem;color:var(--text-muted);text-align:left;flex-shrink:0}
.tier-divider{display:flex;align-items:center;gap:1rem;margin:2rem 0 1.2rem}
.tier-divider .line{flex:1;height:1px;background:var(--border)}
.tier-divider .badge{padding:.4rem 1rem;border-radius:20px;font-size:.75rem;font-weight:700;text-transform:uppercase;letter-spacing:.08em}
.phase-divider .badge{background:rgba(56,189,248,.15);color:var(--accent);border:1px solid rgba(56,189,248,.3)}
.eng-divider .badge{background:rgba(167,139,250,.15);color:var(--eng);border:1px solid rgba(167,139,250,.3)}
.phase-meta{text-align:center;font-size:.78rem;color:var(--text-muted);margin:-.4rem 0 1rem}
.phase-meta strong{color:var(--text)}
.category{background:var(--surface);border:1px solid var(--border);border-radius:10px;margin-bottom:.8rem;overflow:hidden;box-shadow:var(--shadow-sm)}
.category-header{display:flex;align-items:center;justify-content:space-between;padding:.7rem 1rem;cursor:pointer;user-select:none;transition:background .2s}
.category-header:hover{background:var(--surface2)}
.category-header .cat-title{font-weight:600;font-size:.9rem;display:flex;align-items:center;gap:.5rem}
.category-header .cat-stats{display:flex;gap:.5rem;font-size:.75rem}
.cat-stats .stat{display:flex;align-items:center;gap:.25rem}
.stat .dot{width:7px;height:7px;border-radius:50%;display:inline-block}
.dot.done{background:var(--green)}.dot.partial{background:var(--yellow)}.dot.not-started{background:var(--border)}.dot.inherited{background:var(--accent)}
.dot.in-review{background:var(--accent2)}.dot.drafted{background:var(--cyan)}.dot.needs-revision{background:var(--orange)}
.progress-segment.drafted{background:var(--cyan);color:#000}
.chevron{transition:transform .2s;color:var(--text-muted)}
.category.open .chevron{transform:rotate(180deg)}
.category.open .category-header{border-bottom:1px solid var(--border)}
.category-body{display:none;padding:0}.category.open .category-body{display:block}
.item-table{width:100%;border-collapse:collapse;font-size:.78rem}
.item-table th{text-align:left;padding:.35rem .6rem;background:var(--surface2);color:var(--text-muted);font-weight:600;font-size:.67rem;text-transform:uppercase;letter-spacing:.04em;position:sticky;top:0;z-index:1}
.item-table td{padding:.35rem .6rem;border-top:1px solid rgba(71,85,105,.4);vertical-align:top}
.item-table .updated-col{white-space:nowrap;color:var(--text-muted);font-size:.72rem}
.item-row{cursor:pointer;transition:background .15s}.item-row:hover td{background:rgba(56,189,248,.05)}
.item-row.expanded-info td{background:rgba(56,189,248,.08)}
.item-row.expanded-help td{background:rgba(168,85,247,.08)}
/* Info row — deterministic Deliverable Details (Phase, Scope, Path, REFs).
   Toggled by clicking the row body or the (i) icon. */
.info-row{display:none!important}.info-row.visible{display:table-row!important}
.info-row td{padding:.5rem .8rem .6rem 3rem;background:var(--help-bg);border-top:none;border-left:3px solid var(--accent)}
.info-content{font-size:.8rem;color:var(--text-muted);line-height:1.5}
.info-content strong{color:var(--text)}
.info-content p{margin:.2rem 0}.info-content ul{margin:.2rem 0 .2rem 1.2rem}.info-content li{margin:.1rem 0}
.info-content code{font-size:.75rem;color:var(--cyan);background:rgba(6,182,212,.1);padding:.1rem .3rem;border-radius:3px}
.info-content a{color:var(--accent);text-decoration:none}.info-content a:hover{text-decoration:underline}
.info-empty{color:var(--text-muted);font-style:italic;font-size:.78rem}
/* Help row — LLM-generated artifact help from submission-tracker.help.json.
   Toggled by clicking the (?) icon only. Distinct purple accent so it does
   not visually conflict with the cyan info-row. */
.help-row{display:none!important}.help-row.visible{display:table-row!important}
.help-row td{padding:.5rem .8rem .6rem 3rem;background:rgba(168,85,247,.06);border-top:none;border-left:3px solid #a855f7}
.help-content{font-size:.8rem;color:var(--text);line-height:1.55}
.help-content h4{font-size:.78rem;color:#c084fc;text-transform:uppercase;letter-spacing:.05em;margin:.6rem 0 .15rem 0}
.help-content h4:first-child{margin-top:0}
.help-content p{margin:.2rem 0;color:var(--text-muted)}
.help-content ul{margin:.2rem 0 .4rem 1.2rem}.help-content li{margin:.15rem 0;color:var(--text-muted)}
.help-content li strong{color:var(--text)}
.help-content code{font-size:.75rem;color:#c084fc;background:rgba(168,85,247,.1);padding:.1rem .3rem;border-radius:3px}
.help-content .anchors{font-size:.72rem;color:var(--text-muted);margin-top:.3rem}
.help-content .anchors code{color:#c084fc}
.help-empty{color:var(--text-muted);font-style:italic;font-size:.78rem}
.help-empty code{color:#c084fc}
/* Per-row icon affordances. Clickable; spaced; tooltip on hover. */
.row-icons{display:inline-flex;gap:.25rem;margin-left:.4rem;vertical-align:middle}
.row-icon{display:inline-block;width:1.1rem;height:1.1rem;line-height:1.1rem;text-align:center;border-radius:50%;font-size:.7rem;font-weight:600;cursor:pointer;user-select:none;opacity:.55;transition:opacity .15s,background .15s}
.row-icon.info{color:var(--accent);background:rgba(56,189,248,.12)}
.row-icon.info:hover{opacity:1;background:rgba(56,189,248,.25)}
.row-icon.help{color:#c084fc;background:rgba(168,85,247,.12)}
.row-icon.help:hover{opacity:1;background:rgba(168,85,247,.25)}
.item-row:hover .row-icon{opacity:.85}
.status-badge{display:inline-block;padding:.12rem .45rem;border-radius:10px;font-size:.67rem;font-weight:600;white-space:nowrap}
/* 7-state lifecycle vocabulary (canonical) */
.status-badge.not-started{background:rgba(71,85,105,.3);color:var(--text-muted)}
.status-badge.drafting{background:rgba(234,179,8,.15);color:var(--yellow)}
.status-badge.drafted{background:rgba(6,182,212,.15);color:var(--cyan)}
.status-badge.in-review{background:rgba(129,140,248,.15);color:var(--accent2)}
.status-badge.needs-revision{background:rgba(249,115,22,.15);color:var(--orange)}
.status-badge.approved{background:rgba(34,197,94,.15);color:var(--green)}
.status-badge.n-a{background:rgba(148,163,184,.15);color:var(--text-muted)}
/* Legacy v7 classes — kept so any md row that hasn't been coerced yet
   still gets a sane badge color (matches the canonical mapping). */
.status-badge.done{background:rgba(34,197,94,.15);color:var(--green)}
.status-badge.partial{background:rgba(234,179,8,.15);color:var(--yellow)}
.status-badge.in-progress{background:rgba(234,179,8,.15);color:var(--yellow)}
.status-badge.inherited{background:rgba(34,197,94,.15);color:var(--green)}
.scope-badge,.phase-badge,.effort-badge{display:inline-block;padding:.1rem .35rem;border-radius:10px;font-size:.62rem;font-weight:600;white-space:nowrap}
.effort-badge.low{background:rgba(34,197,94,.15);color:var(--green)}
.effort-badge.med{background:rgba(234,179,8,.15);color:var(--yellow)}
.effort-badge.high{background:rgba(249,115,22,.15);color:var(--orange)}
.effort-badge.vhigh{background:rgba(239,68,68,.15);color:var(--red)}
.scale-section{background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:1rem 1.2rem;margin-top:1rem;margin-bottom:1rem;box-shadow:var(--shadow-sm)}
.scale-section h3{font-size:.95rem;margin-bottom:.6rem;color:var(--brand);text-transform:uppercase;letter-spacing:.05em}
.scale-table{width:100%;border-collapse:collapse;font-size:.78rem}
.scale-table th{text-align:left;padding:.3rem .6rem;border-bottom:1px solid var(--border);color:var(--text-muted);font-size:.67rem;text-transform:uppercase;letter-spacing:.04em}
.scale-table td{padding:.4rem .6rem;border-bottom:1px solid rgba(71,85,105,.3);vertical-align:top;color:var(--text-muted)}
.scale-table td:first-child{width:120px}
.scale-table strong{color:var(--text)}
.scales-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(380px,1fr));gap:1rem;margin-top:1.5rem}
.id-col{width:84px;white-space:nowrap;color:var(--text-muted);font-family:monospace;font-size:.72rem}
.status-col{width:90px}.ai-status-col{width:108px}.scope-col{width:90px}.phase-col{width:100px}
.status-badge.ai-status{background:rgba(129,140,248,.12);color:var(--accent2);border:1px dashed rgba(129,140,248,.4);font-style:italic;cursor:help}
.status-badge.ai-status.not-analyzed{background:rgba(148,163,184,.08);color:var(--text-muted);border-color:rgba(148,163,184,.25)}
.ref-col{color:var(--text-muted);font-size:.72rem;max-width:180px}
.path-col{color:var(--text-muted);font-size:.7rem;font-family:monospace;max-width:280px;overflow:hidden;text-overflow:ellipsis}
.path-col a{color:var(--accent);text-decoration:none}.path-col a:hover{text-decoration:underline}
/* Tracker action buttons (e.g., "Create Draft") authored inline in the source markdown.
   Visually match the .controls filter-chip style so the dashboard's button language
   stays consistent. Project-console skill ships a parallel rule for the docs-view render. */
.tracker-action-btn{background:var(--surface2);color:var(--text);border:1px solid var(--border);border-radius:8px;padding:.3rem .65rem;font-size:.72rem;font-family:inherit;font-weight:500;cursor:pointer;white-space:nowrap;transition:all .2s}
.tracker-action-btn:hover:not(:disabled):not([disabled]){background:var(--brand);color:#fff;border-color:var(--brand)}
.tracker-action-btn:disabled,.tracker-action-btn[disabled]{cursor:not-allowed;background:transparent;color:var(--text-muted);border-style:dashed;opacity:.85}
.tracker-action-btn[data-draft-state]{background:var(--accent-soft,rgba(255,193,7,.12));border-color:var(--accent,#ffc107)}
.tracker-action-btn .draft-stage-badge{display:inline-block;margin-left:.4em;padding:0 .4em;border-radius:6px;background:var(--accent,#ffc107);color:#000;font-size:.65rem;font-weight:600;text-transform:uppercase;letter-spacing:.04em}
.gates-col{font-size:.72rem;color:var(--cyan);font-family:monospace}
.legend{display:flex;gap:1rem;justify-content:center;flex-wrap:wrap;margin-bottom:1.2rem;font-size:.75rem;color:var(--text-muted)}
.legend-item{display:flex;align-items:center;gap:.3rem;font-weight:600}
.legend-item.l-done{color:var(--green)}
.legend-item.l-in-review{color:var(--accent2)}
.legend-item.l-drafted{color:var(--cyan)}
.legend-item.l-partial{color:var(--yellow)}
.legend-item.l-needs-revision{color:var(--orange)}
.legend-item.l-not-started{color:var(--text-muted)}
.help-mode-banner{background:rgba(56,189,248,.08);border:1px solid rgba(56,189,248,.2);border-radius:10px;padding:.5rem 1rem;margin-bottom:1.2rem;font-size:.82rem;color:var(--text-muted);text-align:center;display:none}
.help-mode-banner.visible{display:block}.help-mode-banner strong{color:var(--accent)}
.info-mode-banner{background:rgba(56,189,248,.08);border:1px solid rgba(56,189,248,.2);border-radius:10px;padding:.5rem 1rem;margin-bottom:.6rem;font-size:.82rem;color:var(--text-muted);text-align:center;display:none}
.info-mode-banner.visible{display:block}.info-mode-banner strong{color:var(--accent)}
.help-mode-banner.purple{background:rgba(168,85,247,.08);border-color:rgba(168,85,247,.2)}
.help-mode-banner.purple strong{color:#c084fc}
.footer{text-align:center;margin-top:1.5rem;padding-top:.8rem;border-top:1px solid var(--border);color:var(--text-muted);font-size:.72rem}
.footer code{color:var(--cyan)}
@media(max-width:768px){
  body{padding:.8rem}
  .header h1{font-size:1.4rem}
  .controls{gap:.3rem}
  .controls button{padding:.3rem .5rem;font-size:.65rem}
  .summary-grid{grid-template-columns:repeat(2,1fr);gap:.5rem}
  .summary-card{padding:.6rem}
  .summary-card .number{font-size:1.5rem}
  .progress-label{width:90px;font-size:.7rem}
  .item-table{font-size:.68rem;display:block;overflow-x:auto}
  .item-table td:nth-child(2){white-space:normal;min-width:150px}
  .scope-badge,.phase-badge,.status-badge{font-size:.58rem;padding:.08rem .3rem}
  .tier-divider .badge{font-size:.65rem;padding:.3rem .7rem}
}
/* One orchestrated page-load reveal on the summary cards. Guarded by
   prefers-reduced-motion: the initial opacity:0 lives ONLY inside the
   no-preference query, and fill is `backwards`, so reduced-motion users (and
   any non-animating context) always see fully-visible content. */
@keyframes pc-rise{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}
@media(prefers-reduced-motion:no-preference){
  .summary-grid .summary-card{animation:pc-rise .42s cubic-bezier(.22,1,.36,1) backwards}
  .summary-grid .summary-card:nth-child(1){animation-delay:40ms}
  .summary-grid .summary-card:nth-child(2){animation-delay:100ms}
  .summary-grid .summary-card:nth-child(3){animation-delay:160ms}
  .summary-grid .summary-card:nth-child(4){animation-delay:220ms}
  .summary-grid .summary-card:nth-child(5){animation-delay:280ms}
  .summary-grid .summary-card:nth-child(n+6){animation-delay:330ms}
}
'''

CSS_BASE = '<style>' + _CSS_BASE_INNER + '</style>'


# `_JS_INNER` is the raw JS (no `<script>` wrapper) — single source of truth,
# served as `/workflows/tracker/dashboard.js` for the inline-rendered dashboard
# view, and wrapped into `JS` for the standalone `.html` file.

_JS_INNER = '''
function toggle(id){document.getElementById(id).classList.toggle('open')}
function toggleAllSections(o){document.querySelectorAll('.category').forEach(function(c){if(o)c.classList.add('open');else c.classList.remove('open')})}
var allInfoVisible=false;
function toggleAllInfo(){allInfoVisible=!allInfoVisible;document.querySelectorAll('.info-row').forEach(function(h){var prev=h.previousElementSibling;if(allInfoVisible){h.classList.add('visible');if(prev&&prev.classList.contains('item-row'))prev.classList.add('expanded-info')}else{h.classList.remove('visible');if(prev&&prev.classList.contains('item-row'))prev.classList.remove('expanded-info')}});var b=document.getElementById('btn-info');if(b){b.textContent=allInfoVisible?'Hide All Info':'Show All Info';b.classList.toggle('active',allInfoVisible)}var bn=document.getElementById('info-banner');if(bn)bn.classList.toggle('visible',allInfoVisible)}
var allHelpVisible=false;
function toggleAllHelp(){allHelpVisible=!allHelpVisible;document.querySelectorAll('.help-row').forEach(function(h){var prev=h.previousElementSibling;while(prev&&!prev.classList.contains('item-row'))prev=prev.previousElementSibling;if(allHelpVisible){h.classList.add('visible');if(prev)prev.classList.add('expanded-help')}else{h.classList.remove('visible');if(prev)prev.classList.remove('expanded-help')}});var b=document.getElementById('btn-help');if(b){b.textContent=allHelpVisible?'Hide All Help':'Show All Help';b.classList.toggle('active',allHelpVisible)}var bn=document.getElementById('help-banner');if(bn)bn.classList.toggle('visible',allHelpVisible)}
function findItemRow(el){var r=el;while(r&&!r.classList.contains('item-row'))r=r.parentElement;return r}
function siblingByClass(itemRow,cls){var n=itemRow.nextElementSibling;while(n&&!n.classList.contains('item-row')){if(n.classList.contains(cls))return n;n=n.nextElementSibling}return null}
function toggleRowInfo(itemRow){var info=siblingByClass(itemRow,'info-row');if(!info)return;info.classList.toggle('visible');itemRow.classList.toggle('expanded-info')}
function toggleRowHelp(itemRow){var help=siblingByClass(itemRow,'help-row');if(!help)return;help.classList.toggle('visible');itemRow.classList.toggle('expanded-help')}
var filters={status:'all',scope:'all',phase:'all',effort:'all'};
function setFilter(t,v){filters[t]=v;var btns=document.querySelectorAll('button[data-group="'+t+'"]');btns.forEach(function(b){b.classList.remove('active')});var ab=document.querySelector('button[data-group="'+t+'"][data-value="'+v+'"]');if(ab)ab.classList.add('active');var dd=document.querySelector('select[data-group="'+t+'"]');if(dd){if(dd.value!==v)dd.value=v;dd.classList.toggle('filter-active',v!=='all')}applyFilters()}
function applyFilters(){document.querySelectorAll('.item-row').forEach(function(r){var s=true;if(filters.status!=='all'&&r.getAttribute('data-status')!==filters.status)s=false;if(filters.scope!=='all'&&r.getAttribute('data-scope')!==filters.scope)s=false;if(filters.phase!=='all'&&r.getAttribute('data-phase')!==filters.phase)s=false;if(filters.effort!=='all'&&r.getAttribute('data-effort')!==filters.effort)s=false;r.style.display=s?'':'none';var n=r.nextElementSibling;while(n&&!n.classList.contains('item-row')){if(n.classList.contains('info-row')||n.classList.contains('help-row')){if(!s){n.classList.remove('visible')}}n=n.nextElementSibling}if(!s){r.classList.remove('expanded-info');r.classList.remove('expanded-help')}});document.querySelectorAll('.category').forEach(function(c){var visibleRows=c.querySelectorAll('.item-row:not([style*="display: none"])').length;c.style.display=visibleRows===0?'none':''})}
document.addEventListener('click',function(e){var t=e.target;if(t.tagName==='A'||t.tagName==='BUTTON'||t.tagName==='SELECT'||t.tagName==='OPTION')return;if(t.classList&&t.classList.contains('row-icon')){var ri=findItemRow(t);if(!ri)return;if(t.classList.contains('info'))toggleRowInfo(ri);else if(t.classList.contains('help'))toggleRowHelp(ri);e.stopPropagation();return}var r=t.closest('.item-row');if(!r)return;toggleRowInfo(r)})
'''

JS = '<script>' + _JS_INNER + '</script>'


def emit_controls_html(scope_values, phase_values):
    """Build the controls bar HTML — view-toggle buttons + filter dropdowns.

    Rendered *below* the summary cards and progress bars: those are computed
    from all rows and do not react to the filters, so the controls belong
    adjacent to the detail tables they actually filter. View toggles stay as
    buttons (fire-and-forget actions); the four filters are compact <select>
    dropdowns wired to the same setFilter()/applyFilters() contract as before
    (row data-* attributes and applyFilters() are untouched)."""
    status_values = ['Approved', 'In Review', 'Drafted', 'Drafting', 'Needs Revision', 'Not Started', 'N/A']
    effort_values = ['Low', 'Med', 'High', 'V.High']

    def dropdown(group, label, values):
        opts = ['<option value="all">All</option>']
        opts += [f'<option value="{v}">{v}</option>' for v in values]
        return (f'<label class="filter-dd"><span class="label">{label}</span>'
                f'<select data-group="{group}" onchange="setFilter(\'{group}\',this.value)">'
                + ''.join(opts) + '</select></label>')

    parts = ['<div class="controls">']
    # View toggles — actions, kept as buttons.
    parts.append('<button onclick="toggleAllSections(true)">Expand All</button>')
    parts.append('<button onclick="toggleAllSections(false)">Collapse All</button>')
    parts.append('<button onclick="toggleAllInfo()" id="btn-info">Show All Info</button>')
    parts.append('<button onclick="toggleAllHelp()" id="btn-help">Show All Help</button>')
    # Filters — compact dropdowns.
    parts.append('<span class="sep"></span>')
    parts.append(dropdown('status', 'Status', status_values))
    parts.append(dropdown('scope', 'Scope', scope_values))
    parts.append(dropdown('phase', 'Phase', phase_values))
    parts.append(dropdown('effort', 'Effort', effort_values))
    parts.append('</div>')
    # Mode banners relocate with the controls.
    parts.append('<div class="info-mode-banner" id="info-banner"><strong>Info mode active</strong> &mdash; per-row deterministic details (Phase, Scope, Path, References) expanded.</div>')
    parts.append('<div class="help-mode-banner purple" id="help-banner"><strong>Help mode active</strong> &mdash; LLM-generated artifact help (what is this, why it matters in this project) expanded. Run <code>/tracker help</code> to populate empty rows.</div>')
    return ''.join(parts)


# ─── Render ───

def render(project_dir, embed=False):
    """Render the submission tracker.

    `embed=False` (default): emit a complete self-contained HTML document and
    write it to `docs/project/submissions/submission-tracker.html`.
    `embed=True`: emit only the body fragment (no doctype, no `<style>` shell
    other than the data-derived dynamic-css block, no `<script>` shell, no
    page header) and return the HTML string. The caller provides chrome and
    loads `_CSS_BASE_INNER` + `_JS_INNER` via separate static routes.
    """
    project_dir = Path(project_dir)
    brand_theme = load_brand_theme(project_dir)  # {} when no project-console theme is found
    md_path = project_dir / 'docs/project/submissions/submission-tracker.md'
    html_path = project_dir / 'docs/project/submissions/submission-tracker.html'
    src_dir = md_path.parent

    # "Last updated" — when the tracker content genuinely changed,
    # not when this HTML was rendered. Falls back to the render date if it can't
    # be resolved. Rendered in both standalone and embed (console) modes below.
    _last_updated = last_updated_date(project_dir)
    updated_line = (f'Last updated: {_last_updated}' if _last_updated
                    else f'Generated: {date.today().strftime("%d-%b-%y")}')

    data = parse_markdown(md_path)
    rows, eng, details, scales = data['rows'], data['eng'], data['details'], data.get('scales', {'status':[],'phase':[],'effort':[]})

    # Per-deliverable "Last Updated" — each row's evidence-file date (DD-Mon-YY).
    row_updated = build_row_last_updated(rows, src_dir, project_dir)

    # Sidecar override: when submission-tracker.details.json exists, its
    # entries take precedence over the inline `## Deliverable Details`
    # markdown. Sidecar entries support multi-row attachment (one entry,
    # many row IDs) — collapsing the duplication that hand-authoring of
    # paired rows (e.g. early-phase readiness + final-package row for
    # the same artifact) used to require.
    details_sidecar = load_details_sidecar(project_dir)
    if details_sidecar:
        details = {**details, **details_sidecar}
    agent_map = load_agent_sidecar(project_dir)
    help_map = load_help_sidecar(project_dir)
    row_source_map = load_row_source_sidecar(project_dir)

    # Apply human overlay so the rendered dashboard / standalone html show
    # the resolved md+overlay union. The md itself stays generator-owned;
    # the overlay is the durable record of human-curated divergence.
    human_overlay = load_human_overlay(project_dir)
    apply_human_overlay(rows, human_overlay)
    apply_human_overlay(eng, human_overlay)

    errors, warnings = validate(data)
    if errors:
        print(f"  ERRORS ({len(errors)}):")
        for e in errors:
            print(f"    ✗ {e}")
    if warnings:
        print(f"  WARNINGS ({len(warnings)}):")
        for w in warnings[:10]:
            print(f"    ⚠ {w}")
        if len(warnings) > 10:
            print(f"    ... ({len(warnings)-10} more)")

    by_phase = OrderedDict()
    for r in rows:
        if r['phase'] not in by_phase:
            by_phase[r['phase']] = OrderedDict()
        sub = r['subsection']
        if sub not in by_phase[r['phase']]:
            by_phase[r['phase']][sub] = []
        by_phase[r['phase']][sub].append(r)

    scope_values = sorted({r['scope'] for r in rows} | {e['scope'] for e in eng})
    phase_values = list(by_phase.keys())

    def count_status(items, s):
        return sum(1 for i in items if i['status'] == s)

    out = []
    w = out.append

    if not embed:
        w('<!DOCTYPE html>\n<html lang="en"><head><meta charset="UTF-8">')
        w('<meta name="viewport" content="width=device-width,initial-scale=1.0">')
        w('<title>Submission Package Tracker</title>')
        w(CSS_BASE)
        theme_css = gen_theme_css(brand_theme)
        if theme_css:
            w(f'<style>{theme_css}</style>')
        w(f'<style>{gen_dynamic_css(scope_values, phase_values)}</style>')
        w('</head><body>')

        w(f'<div class="header"><h1>Submission Package Tracker</h1>'
          f'<div class="subtitle">{project_subtitle(project_dir)}</div>'
          f'<div class="timestamp">{updated_line}</div></div>')
    else:
        # Embed mode: only the data-derived dynamic CSS goes inline (the
        # base CSS + JS are loaded via separate static routes by the host).
        theme_css = gen_theme_css(brand_theme)
        if theme_css:
            w(f'<style>{theme_css}</style>')
        w(f'<style>{gen_dynamic_css(scope_values, phase_values)}</style>')
        w('<div class="tracker-embed">')
        w(f'<div class="timestamp">{updated_line}</div>')

    # Controls bar (filters + view toggles) is emitted BELOW the summary cards
    # and progress bars — see emit_controls_html() and the call after the
    # progress section. The summary/progress are filter-independent, so the
    # controls sit adjacent to the detail tables they actually filter.

    # `inflight` = active work between Not Started and Approved
    INFLIGHT_STATES = ('Drafting', 'Drafted', 'In Review', 'Needs Revision')

    def count_inflight(items):
        return sum(1 for i in items if i['status'] in INFLIGHT_STATES)

    # Summary cards
    w('<div class="summary-grid">')
    for p in phase_values:
        flat = [r for sub in by_phase[p].values() for r in sub]
        n = len(flat)
        d = count_status(flat, 'Approved')
        inflight = count_inflight(flat)
        ns = count_status(flat, 'Not Started')
        pct = round(d / n * 100) if n else 0
        w(f'<div class="summary-card"><div class="label">{p}</div>'
          f'<div class="number">{n}</div>'
          f'<div class="detail">{d} approved · {inflight} in flight · {ns} not started · {pct}% ready</div></div>')
    eng_done = count_status(eng, 'Approved')
    eng_inflight = count_inflight(eng)
    w(f'<div class="summary-card eng"><div class="label">Engineering Prereqs</div>'
      f'<div class="number">{len(eng)}</div>'
      f'<div class="detail">{eng_done} approved · {eng_inflight} in flight</div></div>')
    total = len(rows)
    overall_done = count_status(rows, 'Approved')
    w(f'<div class="summary-card total"><div class="label">Grand Total</div>'
      f'<div class="number">{total}</div>'
      f'<div class="detail">{overall_done}/{total} approved · {round(overall_done/total*100) if total else 0}%</div></div>')
    w('</div>')

    w('<div class="legend">'
      '<div class="legend-item l-done"><span class="dot done"></span> Approved</div>'
      '<div class="legend-item l-in-review"><span class="dot in-review"></span> In Review</div>'
      '<div class="legend-item l-drafted"><span class="dot drafted"></span> Drafted</div>'
      '<div class="legend-item l-partial"><span class="dot partial"></span> Drafting</div>'
      '<div class="legend-item l-needs-revision"><span class="dot needs-revision"></span> Needs Revision</div>'
      '<div class="legend-item l-not-started"><span class="dot not-started"></span> Not Started</div>'
      '<div class="legend-item" style="color:var(--accent)">&#9432; Click row for help</div></div>')

    # Per-Phase progress bars
    w('<div class="progress-section">')
    for p in phase_values:
        flat = [r for sub in by_phase[p].values() for r in sub]
        n = len(flat)
        if n == 0:
            continue
        d = count_status(flat, 'Approved')
        rev = count_status(flat, 'In Review')
        drft = count_status(flat, 'Drafted')
        ing = count_status(flat, 'Drafting') + count_status(flat, 'Needs Revision')
        segs = ''
        if d:
            segs += f'<div class="progress-segment done" style="width:{round(d/n*100,1)}%">{d}</div>'
        if rev:
            segs += f'<div class="progress-segment inherited" style="width:{round(rev/n*100,1)}%">{rev}</div>'
        if drft:
            segs += f'<div class="progress-segment drafted" style="width:{round(drft/n*100,1)}%">{drft}</div>'
        if ing:
            segs += f'<div class="progress-segment partial" style="width:{round(ing/n*100,1)}%">{ing}</div>'
        w(f'<div class="progress-row">'
          f'<div class="progress-label">{p}</div>'
          f'<div class="progress-bar-container">{segs}</div>'
          f'<div class="progress-stats">{d}/{n} done</div></div>')
    w('</div>')

    # Controls bar — filters + view toggles, placed below the (filter-independent)
    # summary + progress, adjacent to the detail tables they filter.
    w(emit_controls_html(scope_values, phase_values))

    # Per-Phase sections
    for p in phase_values:
        w(f'<div class="tier-divider phase-divider">'
          f'<div class="line"></div>'
          f'<div class="badge">{p}</div>'
          f'<div class="line"></div></div>')

        for sub, sub_items in by_phase[p].items():
            cat_id = f'cat-{slug(p)}-{slug(sub)}'
            d = count_status(sub_items, 'Approved')
            rev = count_status(sub_items, 'In Review')
            drft = count_status(sub_items, 'Drafted')
            ing = count_status(sub_items, 'Drafting') + count_status(sub_items, 'Needs Revision')
            ns = count_status(sub_items, 'Not Started')
            stats = ''
            if d:
                stats += f'<div class="stat"><span class="dot done"></span>{d}</div>'
            if rev:
                stats += f'<div class="stat"><span class="dot in-review"></span>{rev}</div>'
            if drft:
                stats += f'<div class="stat"><span class="dot drafted"></span>{drft}</div>'
            if ing:
                stats += f'<div class="stat"><span class="dot partial"></span>{ing}</div>'
            if ns:
                stats += f'<div class="stat"><span class="dot not-started"></span>{ns}</div>'

            w(f'<div class="category open" id="{cat_id}">'
              f'<div class="category-header" onclick="toggle(\'{cat_id}\')">'
              f'<div class="cat-title">{sub} <span style="color:var(--text-muted);font-weight:400;font-size:.78rem">({len(sub_items)})</span></div>'
              f'<div class="cat-stats">{stats}<span class="chevron">▼</span></div></div>'
              f'<div class="category-body">'
              f'<table class="item-table"><thead><tr>'
              f'<th class="id-col">ID</th><th>Deliverable</th>'
              f'<th class="scope-col">Scope</th><th class="phase-col">Phase</th>'
              f'<th class="ref-col">REF</th><th>Effort</th>'
              f'<th class="ai-status-col">AI Status</th><th class="status-col">Status</th>'
              f'<th class="updated-col">Last Updated</th>'
              f'<th class="path-col">Path</th></tr></thead><tbody>')

            for r in sub_items:
                iid = r['id']
                w(f'<tr class="item-row" data-id="{iid}" data-status="{r["status"]}" data-scope="{r["scope"]}" data-phase="{r["phase"]}" data-effort="{r.get("effort","")}">'
                  f'<td class="id-col">{iid}<span class="row-icons">'
                  f'<span class="row-icon info" title="Show details (Phase, Scope, Path, References)">&#9432;</span>'
                  f'<span class="row-icon help" title="Show artifact help (what is this, why it matters)">?</span>'
                  f'{source_badge_html(iid, row_source_map)}'
                  f'</span></td>'
                  f'<td>{md_inline_to_html(r["name"], src_dir, project_dir)}</td>'
                  f'<td><span class="{scope_class(r["scope"])}">{r["scope"]}</span></td>'
                  f'<td><span class="{phase_class(r["phase"])}">{r["phase"]}</span></td>'
                  f'<td class="ref-col">{md_inline_to_html(r["ref"], src_dir, project_dir)}</td>'
                  f'<td><span class="{effort_class(r.get("effort",""))}">{r.get("effort","")}</span></td>'
                  f'{ai_status_cell(iid, agent_map)}'
                  f'<td><span class="{status_class(r["status"])}" data-row-id="{iid}" data-status="{r["status"]}">{r["status"]}</span></td>'
                  f'<td class="updated-col">{row_updated.get(iid, "—")}</td>'
                  f'<td class="path-col">{wire_create_draft_button(md_inline_to_html(r["path"], src_dir, project_dir), iid, r["status"], find_draft_stage(project_dir, iid))}</td>'
                  f'</tr>')
                if iid in details:
                    detail_html = detail_md_to_html(details[iid], src_dir, project_dir)
                    w(f'<tr class="info-row"><td colspan="10"><div class="info-content">{detail_html}</div></td></tr>')
                else:
                    w(f'<tr class="info-row"><td colspan="10"><div class="info-content info-empty">No detail entry yet for <code>{iid}</code> &mdash; populate via Deliverable Details section in the markdown.</div></td></tr>')
                w(help_row_html(iid, help_map, colspan=10))

            w('</tbody></table></div></div>')

    # Engineering Prerequisites
    w(f'<div class="tier-divider eng-divider">'
      f'<div class="line"></div>'
      f'<div class="badge">Engineering Prerequisites</div>'
      f'<div class="line"></div></div>')
    w('<div class="phase-meta"><strong>Cross-cutting</strong> — capabilities that gate multiple deliverables across milestones</div>')

    cat_id = 'cat-engineering'
    d = count_status(eng, 'Approved')
    inflight = count_inflight(eng)
    ns = count_status(eng, 'Not Started')
    stats = ''
    if d:
        stats += f'<div class="stat"><span class="dot done"></span>{d}</div>'
    if inflight:
        stats += f'<div class="stat"><span class="dot partial"></span>{inflight}</div>'
    if ns:
        stats += f'<div class="stat"><span class="dot not-started"></span>{ns}</div>'

    w(f'<div class="category open" id="{cat_id}">'
      f'<div class="category-header" onclick="toggle(\'{cat_id}\')">'
      f'<div class="cat-title">Engineering Prerequisites <span style="color:var(--text-muted);font-weight:400;font-size:.78rem">({len(eng)})</span></div>'
      f'<div class="cat-stats">{stats}<span class="chevron">▼</span></div></div>'
      f'<div class="category-body">'
      f'<table class="item-table"><thead><tr>'
      f'<th class="id-col">ID</th><th>Prerequisite</th>'
      f'<th class="scope-col">Scope</th><th class="phase-col">Phase</th>'
      f'<th>Effort</th>'
      f'<th class="ai-status-col">AI Status</th><th class="status-col">Status</th>'
      f'<th class="updated-col">Last Updated</th>'
      f'<th>Gates</th></tr></thead><tbody>')

    for e in eng:
        w(f'<tr class="item-row" data-id="{e["id"]}" data-status="{e["status"]}" data-scope="{e["scope"]}" data-phase="{e["phase"]}" data-effort="{e.get("effort","")}">'
          f'<td class="id-col">{e["id"]}<span class="row-icons">'
          f'<span class="row-icon info" title="Show details">&#9432;</span>'
          f'<span class="row-icon help" title="Show artifact help">?</span>'
          f'</span></td>'
          f'<td>{md_inline_to_html(e["name"], src_dir, project_dir)}</td>'
          f'<td><span class="{scope_class(e["scope"])}">{e["scope"]}</span></td>'
          f'<td><span class="{phase_class(e["phase"])}">{e["phase"]}</span></td>'
          f'<td><span class="{effort_class(e.get("effort",""))}">{e.get("effort","")}</span></td>'
          f'{ai_status_cell(e["id"], agent_map)}'
          f'<td><span class="{status_class(e["status"])}" data-row-id="{e["id"]}" data-status="{e["status"]}">{e["status"]}</span></td>'
          f'<td class="updated-col">&mdash;</td>'
          f'<td class="gates-col">{md_inline_to_html(e["gates"], src_dir, project_dir)}</td>'
          f'</tr>')
        w(f'<tr class="info-row"><td colspan="9"><div class="info-content info-empty">Engineering prerequisite — see project README for capability ownership.</div></td></tr>')
        w(help_row_html(e["id"], help_map, colspan=9))
    w('</tbody></table></div></div>')

    # Scale sections (Status / Phase / Effort) — definitions of each badge value
    has_any_scale = any(scales.get(k) for k in ('status', 'phase', 'effort'))
    if has_any_scale:
        w('<div class="scales-grid">')
        for kind, title in [('status', 'Status Scale'), ('phase', 'Phase Scale'), ('effort', 'Effort Scale')]:
            entries = scales.get(kind, [])
            if not entries:
                continue
            w(f'<div class="scale-section"><h3>{title}</h3>')
            w('<table class="scale-table"><tbody>')
            for s in entries:
                # Render the label with appropriate badge styling
                if kind == 'status':
                    badge = f'<span class="{status_class(s["label"])}">{s["label"]}</span>'
                elif kind == 'phase':
                    badge = f'<span class="{phase_class(s["label"])}">{s["label"]}</span>'
                else:
                    badge = f'<span class="{effort_class(s["label"])}">{s["label"]}</span>'
                w(f'<tr><td>{badge}</td><td>{md_inline_to_html(s["definition"], src_dir, project_dir)}</td></tr>')
            w('</tbody></table></div>')
        w('</div>')

    w('<div class="footer">Generated by <code>/tracker render</code> · '
      'Source: <code>docs/project/submissions/submission-tracker.md</code> · '
      'Plan: <code>docs/project/milestones/regulatory.yml</code></div>')

    if not embed:
        w(JS)
        w('</body></html>')

        html_path.write_text('\n'.join(out))
        print(f"  Wrote {html_path.relative_to(project_dir)} ({html_path.stat().st_size:,} bytes)")
        print(f"  rows: {len(rows)} · eng: {len(eng)} · details: {len(details)}")
        by_phase_counts = Counter(r['phase'] for r in rows)
        print(f"  phases: {dict(by_phase_counts)}")
        by_status_counts = Counter(r['status'] for r in rows)
        print(f"  statuses: {dict(by_status_counts)}")
        return None

    # Embed mode: close wrapper and return HTML string (no file write).
    w('</div>')
    return '\n'.join(out)


def render_embed_fragment(project_dir):
    """Convenience wrapper — returns the embed-mode HTML fragment string."""
    return render(project_dir, embed=True)


def main():
    args = sys.argv[1:]
    project_dir = None
    if '--project-dir' in args:
        i = args.index('--project-dir')
        project_dir = args[i + 1]
    if not project_dir:
        project_dir = find_project_dir()
    print(f"Tracker render — project_dir={project_dir}")
    render(project_dir)


if __name__ == '__main__':
    main()
