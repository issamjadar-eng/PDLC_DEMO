"""Strategy section — topline promotion of the former B3 'strategy-reassembly'
workflow.

GET /strategy  — full-strategy review surface (tabbed per-domain navigation,
                 proposed-change callouts, advisor drawer). Renders the same
                 `workflow_b3_index.html` template the workflow used, with
                 `topline=True` so the breadcrumb/header present it as a
                 first-class section rather than a workflow card.

The heavy lifting (worktree sessions, Accept/Reject/Modify/Re-Assemble,
decision/section edit-via-chat) still lives in `console.workflows` — its
mutation endpoints stay mounted at `/workflows/strategy-reassembly/*`, and the
template's JS posts there. This module owns only the read-side landing page so
Strategy can sit in the top nav right after Overview. The workflow's GET route
now redirects here (see `workflows.router`).
"""
from __future__ import annotations

import re
from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from console.config import get_config
from console.documents import renderer as doc_renderer
from console.workflows import b3_session, b3_strategy_reassembly
from console.workflows.catalog import get_by_slug
from console.workflows.router import _resolve_actor

router = APIRouter()
templates = Jinja2Templates(
    directory=str(Path(__file__).parent.parent / "web" / "templates")
)

_STRATEGIES_DIR = ("docs", "project", "strategies")


def discover(repo_root: Path) -> dict:
    """Cheap nav-visibility probe (stat only). Nav shows the Strategy tab when
    at least one `*-strategy.md` exists under docs/project/strategies/."""
    root = repo_root.joinpath(*_STRATEGIES_DIR)
    has_any = root.is_dir() and any(root.glob("*-strategy.md"))
    return {"has_any": has_any}


# Inside the strategy view, relative task-doc links (e.g.
# `../../../tasks/<person>/NNN-slug.md`) would resolve against `/strategy`
# when clicked — that URL has no such file, so they 404. Rewrite them to the
# Documents-viewer hash route so clicks open the task inside the viewer pane.
_TASK_HREF_RE = re.compile(r'href="(?:\.\./)+tasks/([^"#]+)"')


def _rewrite_task_links(html: str) -> str:
    def repl(m: re.Match) -> str:
        virtual = f"tasks/{m.group(1)}"
        return f'href="/documents#path={virtual}" target="_blank" rel="noopener"'

    return _TASK_HREF_RE.sub(repl, html)


def _build_domain_views(cfg) -> list[dict]:
    """Assemble the per-domain view payloads the template renders. Mirrors the
    former `/workflows/strategy-reassembly` GET handler verbatim — it reads the
    worktree copy when an open per-(actor, domain) session exists so in-flight
    mutations are visible before Commit & Merge."""
    import markdown as md_lib

    actor_info_view = _resolve_actor(cfg.repo_root)
    actor_folder_view = actor_info_view.get("task_folder") or ""

    docs = b3_strategy_reassembly.scan(cfg.repo_root)
    domain_views: list[dict] = []
    for d in docs:
        sess = (
            b3_session.snapshot(cfg.repo_root, actor_folder_view, d.slug)
            if actor_folder_view
            else None
        )
        source_root = Path(sess.worktree_path) if sess else cfg.repo_root
        abs_path = source_root / d.virtual_path
        if not abs_path.is_file():
            abs_path = cfg.repo_root / d.virtual_path
            source_root = cfg.repo_root
        text = abs_path.read_text(encoding="utf-8", errors="ignore")
        proposals = b3_strategy_reassembly._parse_proposals(text)
        history = b3_strategy_reassembly._parse_history(text)
        rendered = doc_renderer.render(abs_path)

        md_engine = md_lib.Markdown(extensions=["tables", "fenced_code", "sane_lists"])
        history_rendered = []
        for h in history:
            md_engine.reset()
            body_html = md_engine.convert(h.body) if h.body else ""
            history_rendered.append(
                {"date": h.date, "label": h.label, "body_html": body_html, "body": h.body}
            )

        proposals_rendered = []
        for p in proposals:
            stripped = b3_strategy_reassembly._dedent_callout_body(p.raw)
            md_engine.reset()
            body_html = md_engine.convert(stripped)
            is_new_add = b3_strategy_reassembly.is_new_addition_proposal(text, p)
            if is_new_add:
                existing_html = ""
            else:
                existing_md = b3_strategy_reassembly.existing_section_content(text, p)
                if existing_md:
                    md_engine.reset()
                    existing_html = md_engine.convert(existing_md)
                else:
                    existing_html = ""
            proposals_rendered.append(
                {
                    "idx": p.idx,
                    "task_id": p.task_id,
                    "heading": p.heading,
                    "author": p.author,
                    "date": p.date,
                    "section": p.section,
                    "start_line": p.start_line,
                    "end_line": p.end_line,
                    "raw": p.raw,
                    "stripped": stripped,
                    "body_html": body_html,
                    "existing_html": existing_html,
                    "is_new_addition": is_new_add or not existing_html,
                }
            )

        decisions_list = b3_strategy_reassembly.parse_decisions(text)
        decisions_payload = [
            {
                "id": _dx.id,
                "status": _dx.status,
                "source": _dx.source,
                "created": _dx.created,
                "last_edited": _dx.last_edited,
                "section_label": _dx.section_label,
                "heading": _dx.heading,
                "body": _dx.body,
            }
            for _dx in decisions_list
        ]
        section_labels: list[str] = []
        seen_sections: set[str] = set()
        for _dec in decisions_list:
            if _dec.section_label and _dec.section_label not in seen_sections:
                seen_sections.add(_dec.section_label)
                section_labels.append(_dec.section_label)

        sections_payload: list[dict] = []
        _seen_section_idx: set[int] = set()
        for _ln in text.splitlines():
            _m = re.match(r"^##\s+(\d+)\.\s+(.+?)\s*$", _ln)
            if not _m:
                continue
            _idx = int(_m.group(1))
            if _idx in _seen_section_idx:
                continue
            _seen_section_idx.add(_idx)
            _bounds = b3_strategy_reassembly.section_block(text, _idx)
            if _bounds is None:
                continue
            _s, _e, _label = _bounds
            _raw = "\n".join(text.splitlines()[_s:_e]).rstrip() + "\n"
            sections_payload.append(
                {"idx": _idx, "label": _label, "heading": _m.group(2).strip(), "raw_md": _raw}
            )

        session_info = None
        strategy_doc_diff_html = ""
        strategy_doc_dirty = False
        if sess is not None:
            pending_files = []
            for ln in sess.diff_summary:
                code = ln[:2]
                rel = ln[3:] if len(ln) > 3 else ""
                pending_files.append({"code": code.strip() or "??", "path": rel})
            strategy_doc_dirty = b3_session.worktree_strategy_doc_dirty(
                Path(sess.worktree_path), d.slug
            )
            if strategy_doc_dirty:
                strategy_doc_diff_html = b3_session.friendly_file_diff_html(
                    Path(sess.worktree_path), d.virtual_path
                )
            session_info = {
                "task_id": sess.task_id,
                "task_path": sess.task_path,
                "worktree_path": sess.worktree_path,
                "branch": sess.branch,
                "has_diff": sess.has_diff,
                "diff_count": len(sess.diff_summary),
                "pending_files": pending_files,
                "strategy_doc_dirty": strategy_doc_dirty,
            }

        domain_views.append(
            {
                "doc": d,
                "raw_md": text,
                "body_html": _rewrite_task_links(rendered.body_html),
                "strategy_doc_diff_html": strategy_doc_diff_html,
                "strategy_doc_dirty": strategy_doc_dirty,
                "proposals": [
                    {**p, "body_html": _rewrite_task_links(p["body_html"])}
                    for p in proposals_rendered
                ],
                "history": [
                    {**h, "body_html": _rewrite_task_links(h["body_html"])}
                    for h in history_rendered
                ],
                "session": session_info,
                "decisions": decisions_payload,
                "section_labels": section_labels,
                "sections": sections_payload,
            }
        )
    return domain_views


@router.get("/strategy", response_class=HTMLResponse)
async def strategy_index(request: Request):
    cfg = get_config()
    wf = get_by_slug("strategy-reassembly")
    domain_views = _build_domain_views(cfg)
    return templates.TemplateResponse(
        request,
        "workflow_b3_index.html",
        {"config": cfg, "workflow": wf, "domain_views": domain_views, "topline": True},
    )
