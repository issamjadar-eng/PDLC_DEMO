"""Workflows router — index page + per-workflow views + B1/B3 APIs."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from console.config import get_config
from console.workflows import b1_doc_roundtrip, b3_session, b3_strategy_reassembly
from console.workflows.catalog import CATALOG, get_by_slug, grouped


# ── Actor resolution ──────────────────────────────────────────────────────
# Uses the shared resolve_user.py helper (already used by /secops + /digest).
# Emits {"name": "...", "email": "...", "unresolved": bool, ...}. Runs from
# the repo root (the script reads project.yml relative to CWD).

def _resolve_actor(repo_root: Path) -> dict:
    script = repo_root / ".claude/skills/shared/scripts/resolve_user.py"
    if not script.exists():
        return {"unresolved": True, "reason": "resolve_user.py missing"}
    try:
        r = subprocess.run(
            ["python3", str(script)],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            timeout=5,
        )
        if r.returncode != 0:
            return {"unresolved": True, "reason": f"rc={r.returncode}"}
        return json.loads(r.stdout or "{}")
    except Exception as e:
        return {"unresolved": True, "reason": str(e)}

router = APIRouter()
templates = Jinja2Templates(
    directory=str(Path(__file__).parent.parent / "web" / "templates")
)


@router.get("/workflows", response_class=HTMLResponse)
async def workflows_index(request: Request):
    cfg = get_config()
    return templates.TemplateResponse(
        request,
        "workflows_index.html",
        {"config": cfg, "groups": grouped(), "catalog": CATALOG},
    )


@router.get("/workflows/{slug}", response_class=HTMLResponse)
async def workflow_view(request: Request, slug: str):
    cfg = get_config()
    wf = get_by_slug(slug)
    if wf is None:
        raise HTTPException(404, f"Workflow '{slug}' not found")

    if slug == "strategy-reassembly":
        import re as _re
        from console.documents import renderer as doc_renderer

        # Per-domain session read: if an open worktree exists for the active
        # user/domain, read the strategy doc from the worktree so in-flight
        # mutations are visible before Commit & Merge.
        actor_info_view = _resolve_actor(cfg.repo_root)
        actor_folder_view = actor_info_view.get("task_folder") or ""

        # Inside B3, relative task-doc links (e.g. `../../../tasks/ben/NNN-slug.md`)
        # resolve against `/workflows/strategy-reassembly` when clicked — that URL
        # has no such file, so they 404. Rewrite them to the Documents-viewer
        # hash route so clicks open the task inside the existing viewer pane.
        # Keeps the source markdown's canonical relative paths intact on disk;
        # only the B3-rendered HTML gets rewritten.
        _TASK_HREF_RE = _re.compile(
            r'href="(?:\.\./)+tasks/([^"#]+)"'
        )

        def _rewrite_task_links(html: str) -> str:
            def repl(m: _re.Match) -> str:
                virtual = f"tasks/{m.group(1)}"
                return f'href="/documents#path={virtual}" target="_blank" rel="noopener"'
            return _TASK_HREF_RE.sub(repl, html)

        docs = b3_strategy_reassembly.scan(cfg.repo_root)
        domain_views = []
        for d in docs:
            # Prefer the worktree copy if an open session exists for this
            # (actor, domain). Falls back to main-branch file.
            sess = (
                b3_session.snapshot(cfg.repo_root, actor_folder_view, d.slug)
                if actor_folder_view else None
            )
            source_root = (
                Path(sess.worktree_path) if sess else cfg.repo_root
            )
            abs_path = source_root / d.virtual_path
            if not abs_path.is_file():
                abs_path = cfg.repo_root / d.virtual_path
                source_root = cfg.repo_root
            text = abs_path.read_text(encoding="utf-8", errors="ignore")
            proposals = b3_strategy_reassembly._parse_proposals(text)
            history = b3_strategy_reassembly._parse_history(text)
            # Server-render markdown via the documents skill renderer.
            rendered = doc_renderer.render(abs_path, virtual_path=d.virtual_path)
            # Render each history entry body separately so we can show pretty
            # markdown inside collapsible entries.
            import markdown as md_lib
            md_engine = md_lib.Markdown(extensions=["tables", "fenced_code", "sane_lists"])
            history_rendered = []
            for h in history:
                md_engine.reset()
                body_html = md_engine.convert(h.body) if h.body else ""
                history_rendered.append({"date": h.date, "label": h.label, "body_html": body_html, "body": h.body})
            # Render each proposal body as markdown. Use the same dedent
            # helper that powers Accept so the display body is clean
            # (header + Resolution footer stripped, `> ` prefix removed).
            proposals_rendered = []
            for p in proposals:
                stripped = b3_strategy_reassembly._dedent_callout_body(p.raw)
                md_engine.reset()
                body_html = md_engine.convert(stripped)
                existing_md = b3_strategy_reassembly.existing_section_content(text, p)
                if existing_md:
                    md_engine.reset()
                    existing_html = md_engine.convert(existing_md)
                else:
                    existing_html = ""
                proposals_rendered.append({
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
                    "is_new_addition": not bool(existing_md),
                })
            # Parse decisions for the domain pane action bar.
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
            # List of distinct H2 section labels (for the "Add decision" UI).
            section_labels: list[str] = []
            seen_sections: set[str] = set()
            for _dec in decisions_list:
                if _dec.section_label and _dec.section_label not in seen_sections:
                    seen_sections.add(_dec.section_label)
                    section_labels.append(_dec.section_label)

            # Parse all numbered H2 sections (1., 2., 3., …) so the UI can
            # offer per-section "Edit this section" actions even where the
            # section currently has no decisions.
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
                sections_payload.append({
                    "idx": _idx,
                    "label": _label,
                    "heading": _m.group(2).strip(),
                    "raw_md": _raw,
                })

            session_info = None
            if sess is not None:
                # Decompose `git status --porcelain` output `XY <path>` into
                # {code, path} pairs so the UI can list per-file actions.
                pending_files = []
                for ln in sess.diff_summary:
                    code = ln[:2]
                    rel = ln[3:] if len(ln) > 3 else ""
                    pending_files.append({
                        "code": code.strip() or "??",
                        "path": rel,
                    })
                session_info = {
                    "task_id": sess.task_id,
                    "task_path": sess.task_path,
                    "worktree_path": sess.worktree_path,
                    "branch": sess.branch,
                    "has_diff": sess.has_diff,
                    "diff_count": len(sess.diff_summary),
                    "pending_files": pending_files,
                }
            domain_views.append({
                "doc": d,
                "raw_md": text,
                "body_html": _rewrite_task_links(rendered.body_html),
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
            })
        return templates.TemplateResponse(
            request,
            "workflow_b3_index.html",
            {"config": cfg, "workflow": wf, "domain_views": domain_views},
        )

    if slug == "doc-roundtrip-batch":
        candidates = b1_doc_roundtrip.scan(cfg.repo_root)
        # Group candidates by DHF for the UI.
        by_dhf: dict[str, list] = {}
        for c in candidates:
            by_dhf.setdefault(c.dhf or "(other)", []).append(c)
        return templates.TemplateResponse(
            request,
            "workflow_b1.html",
            {
                "config": cfg,
                "workflow": wf,
                "candidates": candidates,
                "by_dhf": sorted(by_dhf.items()),
                "candidate_count": len(candidates),
            },
        )

    # All other workflows render the generic placeholder view for now.
    return templates.TemplateResponse(
        request,
        "workflow_view.html",
        {"config": cfg, "workflow": wf},
    )


def _enrich_plan_with_audit(
    cfg,
    plan,
    proposal=None,
):
    """Return a plan-dict with actor + active-task + history-preview fields."""
    actor_info = _resolve_actor(cfg.repo_root)
    actor_name = "" if actor_info.get("unresolved") else (actor_info.get("name") or "")
    actor_email = "" if actor_info.get("unresolved") else (actor_info.get("email") or "")
    tasks = b3_strategy_reassembly.active_task_ids(cfg.repo_root)

    history_entry = ""
    can_execute_live = False
    # Modify is executed directly from the textarea submit path (different
    # UI surface); Accept/Reject/Re-Assemble use the Execute button in the
    # dry-run plan.
    if proposal is not None and plan.action in {"reject", "accept"}:
        history_entry = b3_strategy_reassembly.build_history_entry_preview(
            plan.action, proposal, actor_name, tasks
        )
        can_execute_live = bool(actor_name and tasks)
    elif plan.action == "re-assemble":
        can_execute_live = bool(actor_name and tasks)
        if can_execute_live:
            history_entry = (
                f"- **Re-assemble** (detection pass) · by {actor_name} · "
                f"under task {tasks[0]}"
            )
    return {
        "dry_run": True,
        "backend_status": plan.backend_status,
        "domain": plan.domain,
        "action": plan.action,
        "proposal_idx": plan.proposal_idx,
        "commands": plan.commands,
        "file_edits": plan.file_edits,
        "actor": actor_name,
        "actor_email": actor_email,
        "actor_unresolved_reason": actor_info.get("reason") if actor_info.get("unresolved") else "",
        "active_task_ids": tasks,
        "history_entry_preview": history_entry,
        "can_execute_live": can_execute_live,
        "note": (
            "Accept / Reject / Modify mutate the strategy doc directly. "
            "Re-Assemble runs a detection-only pass (scan task tags, update "
            "Sources + History); full content merge still requires "
            "`/strategy assemble <domain>` from Claude Code."
        ),
    }


@router.post("/workflows/strategy-reassembly/{domain_slug}/dry-run")
async def b3_dry_run(request: Request, domain_slug: str):
    """Accept `{"action": "accept|reject|modify|re-assemble", "proposal_idx": N, "new_body": "..."}`
    and return the dry-run plan enriched with actor + active-task context."""
    cfg = get_config()
    doc = b3_strategy_reassembly.get_by_slug(cfg.repo_root, domain_slug)
    if doc is None:
        raise HTTPException(404, f"Strategy doc '{domain_slug}' not found")
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(400, "Expected JSON body")
    action = str(body.get("action", "")).strip()
    target = None
    if action == "re-assemble":
        plan = b3_strategy_reassembly.plan_reassemble(doc)
    else:
        idx = body.get("proposal_idx")
        if not isinstance(idx, int):
            raise HTTPException(400, "`proposal_idx` must be an integer for per-proposal actions")
        new_body = body.get("new_body")
        if new_body is not None and not isinstance(new_body, str):
            raise HTTPException(400, "`new_body` must be a string if provided")
        abs_path = cfg.repo_root / doc.virtual_path
        text = abs_path.read_text(encoding="utf-8", errors="ignore")
        proposals = b3_strategy_reassembly._parse_proposals(text)
        target = next((p for p in proposals if p.idx == idx), None)
        if target is None:
            raise HTTPException(404, f"Proposal #{idx} not found in {doc.virtual_path}")
        try:
            plan = b3_strategy_reassembly.plan_proposal_action(doc, target, action, new_body=new_body)
        except ValueError as e:
            raise HTTPException(400, str(e))
    return JSONResponse(_enrich_plan_with_audit(cfg, plan, proposal=target))


@router.post("/workflows/strategy-reassembly/{domain_slug}/execute")
async def b3_execute(request: Request, domain_slug: str):
    """LIVE execution (Reject only in this pass). Requires resolved actor +
    at least one active task. Mutates the strategy doc + appends a `## History`
    entry. Never writes to task docs or runs /strategy.

    Accept / Modify still return 400 here; they remain dry-run only until
    the source-task marker-rewriting path is implemented."""
    cfg = get_config()
    doc = b3_strategy_reassembly.get_by_slug(cfg.repo_root, domain_slug)
    if doc is None:
        raise HTTPException(404, f"Strategy doc '{domain_slug}' not found")
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(400, "Expected JSON body")
    action = str(body.get("action", "")).strip()
    if action not in {"reject", "accept", "modify", "re-assemble", "recategorize"}:
        raise HTTPException(
            400,
            f"Live execution supports action in {{accept, reject, modify, re-assemble, recategorize}} (got {action!r}).",
        )
    idx = None
    if action != "re-assemble":
        idx = body.get("proposal_idx")
        if not isinstance(idx, int):
            raise HTTPException(400, "`proposal_idx` must be an integer")

    # Actor must resolve cleanly.
    actor_info = _resolve_actor(cfg.repo_root)
    if actor_info.get("unresolved"):
        raise HTTPException(
            403,
            f"Actor unresolved ({actor_info.get('reason')}). "
            f"Refusing to mutate without identity.",
        )
    actor = actor_info.get("name") or ""
    actor_folder = actor_info.get("task_folder") or ""
    if not actor_folder:
        raise HTTPException(
            403,
            f"Actor '{actor}' has no task_folder in project.yml team roster.",
        )

    # Session backing: find-or-create a per-domain task doc + open/reuse the
    # per-domain worktree. Every live mutation lands inside the worktree.
    try:
        task_id, task_path, worktree_root = b3_session.resolve_or_create(
            cfg.repo_root, actor_folder, actor, domain_slug
        )
    except RuntimeError as e:
        raise HTTPException(409, f"session bootstrap failed: {e}")
    tasks = [task_id]

    # Re-root the strategy-doc I/O path onto the worktree for this mutation.
    # StrategyDoc.virtual_path stays the same (repo-relative); we just pass
    # the worktree as the repo_root to the perform_* functions.
    doc_wt = b3_strategy_reassembly.get_by_slug(worktree_root, domain_slug)
    if doc_wt is None:
        raise HTTPException(409, f"strategy doc missing inside worktree: {worktree_root}")

    target = None
    if action != "re-assemble":
        abs_path = worktree_root / doc_wt.virtual_path
        text = abs_path.read_text(encoding="utf-8", errors="ignore")
        proposals = b3_strategy_reassembly._parse_proposals(text)
        target = next((p for p in proposals if p.idx == idx), None)
        if target is None:
            raise HTTPException(404, f"Proposal #{idx} not found in {doc_wt.virtual_path}")

    try:
        if action == "re-assemble":
            # Default to the in-proc detection pass; the Agent-SDK stream runs
            # via a separate /execute-assembler endpoint when a full merge is
            # requested. This keeps Execute fast + synchronous.
            result = b3_strategy_reassembly.perform_reassemble(
                worktree_root, doc_wt, actor=actor, active_task_ids_=tasks
            )
        elif action == "accept":
            result = b3_strategy_reassembly.perform_accept(
                worktree_root, doc_wt, target, actor=actor, active_task_ids_=tasks
            )
        elif action == "modify":
            new_body = body.get("new_body")
            if not isinstance(new_body, str) or not new_body.strip():
                raise HTTPException(400, "`new_body` is required for action='modify'")
            result = b3_strategy_reassembly.perform_modify(
                worktree_root, doc_wt, target, new_body=new_body,
                actor=actor, active_task_ids_=tasks,
            )
        elif action == "recategorize":
            new_domain = (body.get("new_domain") or "").strip()
            if not new_domain:
                raise HTTPException(400, "`new_domain` is required for action='recategorize'")
            result = b3_strategy_reassembly.perform_recategorize(
                worktree_root, doc_wt, target, new_domain=new_domain,
                actor=actor, active_task_ids_=tasks,
            )
            # Auto-commit: Recategorize touches a source task doc (cross-file
            # mutation), which is a substantive change worth landing on main
            # immediately rather than leaving in the worktree for manual
            # commit. FF-merges + pushes + closes the session task + tears
            # down the worktree. If the auto-commit fails, the recategorize
            # is still applied inside the worktree and the user can hit
            # Commit & Merge manually.
            commit_msg = (
                f"workflow: strategy recategorize — {target.heading or '(no heading)'} "
                f"· {doc.domain} → {new_domain} · {target.task_id or '?'} "
                f"· by {actor}"
            )
            try:
                commit_result = b3_session.commit_and_merge(
                    cfg.repo_root, actor_folder, actor, domain_slug, commit_msg
                )
                result["auto_commit"] = commit_result
            except RuntimeError as e:
                result["auto_commit"] = {
                    "committed": False,
                    "error": str(e),
                    "note": (
                        "Recategorize succeeded inside the worktree, but the "
                        "auto-commit/merge failed. Click Commit & Merge to "
                        "land manually, or resolve the underlying issue first."
                    ),
                }
        else:
            result = b3_strategy_reassembly.perform_reject(
                worktree_root, doc_wt, target, actor=actor, active_task_ids_=tasks
            )
    except RuntimeError as e:
        raise HTTPException(409, str(e))
    sess = b3_session.snapshot(cfg.repo_root, actor_folder, domain_slug)
    return JSONResponse(
        {
            "executed": True,
            "backend_status": "live",
            "domain": doc.domain,
            "action": action,
            "proposal_idx": idx,
            "session": {
                "task_id": task_id,
                "task_path": str(task_path.relative_to(cfg.repo_root)),
                "worktree_path": str(worktree_root),
                "branch": b3_session.worktree_branch(domain_slug),
                "has_diff": bool(sess and sess.has_diff),
                "diff_summary": sess.diff_summary if sess else [],
            },
            **result,
        }
    )


def _assembler_model(cfg) -> str:
    """Resolve the model used for the strategy assembler.

    Resolution order:
      1. `console.yaml` `models.assembler` (explicit pin per project)
      2. `claude-opus-4-7` (latest Opus — assembler does heavy multi-doc
         reasoning + tool use, so we DON'T inherit the user's CLI default
         which may be Sonnet/Haiku).

    To override per-project, add to `tools/project-console/console.yaml`:

        models:
          assembler: claude-opus-4-7
    """
    pinned = (cfg.console.get("models") or {}).get("assembler")
    return pinned or "claude-opus-4-7"


_ASSEMBLER_SYSTEM_PROMPT = (
    "You are the /strategy assembler agent. Run in NON-INTERACTIVE mode: "
    "when conflicts are detected between sources, do NOT prompt the user. "
    "Instead, write each conflicting newer block as a `> **Proposed change**` "
    "blockquote callout alongside the existing section and add the "
    "`<!-- STRATEGY PROPOSED: vs <older_task>, section \"X\" -->` marker. "
    "The project-console will surface each callout for per-proposal "
    "Accept / Reject / Modify review. Otherwise follow the canonical "
    "assembler.md flow: scan task docs for `<!-- STRATEGY CONTENT -->` tags "
    "in the specified domain, update the strategy doc under "
    "`docs/project/strategies/<domain>-strategy.md`, preserve History, "
    "update Sources + Source Traceability appendix. No git commits."
)
_ASSEMBLER_ALLOWED_TOOLS = ["Read", "Write", "Edit", "Glob", "Grep", "Bash"]


@router.post("/workflows/strategy-reassembly/{domain_slug}/execute-assembler/stream")
async def b3_execute_assembler_stream(request: Request, domain_slug: str):
    """SSE stream: spawn the /strategy assembler agent via the Claude Agent
    SDK against the per-domain worktree, with --non-interactive mode so
    conflicts become `> **Proposed change**` callouts (no prompts).
    Session + actor + task-gate are established first; the worktree backs
    every file write the agent performs."""
    from fastapi.responses import StreamingResponse
    import asyncio
    import json as _json

    cfg = get_config()
    actor_info = _resolve_actor(cfg.repo_root)
    if actor_info.get("unresolved"):
        raise HTTPException(403, f"Actor unresolved ({actor_info.get('reason')}).")
    actor = actor_info.get("name") or ""
    actor_folder = actor_info.get("task_folder") or ""
    if not actor_folder:
        raise HTTPException(403, "Actor has no task_folder in project.yml")

    try:
        task_id, task_path, worktree_root = b3_session.resolve_or_create(
            cfg.repo_root, actor_folder, actor, domain_slug
        )
    except RuntimeError as e:
        raise HTTPException(409, str(e))

    # Pre-activate the auto-created task for the agent's session by
    # generating a UUID, writing `.state/active-tasks-<uuid>.txt` in BOTH
    # the main repo AND the worktree (the agent runs with `cwd=worktree`,
    # so its `CLAUDE_PROJECT_DIR` resolves to the worktree path and the
    # task-gate hook checks `<worktree>/.state/active-tasks-<uuid>.txt`),
    # and exporting `CLAUDE_SESSION_ID=<uuid>` into the subprocess env.
    # Without all three of these, the agent's first Write is denied (root
    # cause of the 14m + 4m + 8m no-op runs).
    import os as _os
    import uuid as _uuid
    agent_session_id = str(_uuid.uuid4())
    _prev_env = _os.environ.get("CLAUDE_SESSION_ID")
    _os.environ["CLAUDE_SESSION_ID"] = agent_session_id

    def _write_state(sid: str) -> list[Path]:
        """Write `.state/active-tasks-<sid>.txt = task_id` in both the main
        repo and the worktree. Returns the list of paths written so they
        can be cleaned up after the run."""
        written: list[Path] = []
        for root in (cfg.repo_root, worktree_root):
            try:
                f = root / ".state" / f"active-tasks-{sid}.txt"
                f.parent.mkdir(parents=True, exist_ok=True)
                f.write_text(f"{task_id}\n")
                written.append(f)
            except Exception:
                pass
        return written

    synthetic_state_files = _write_state(agent_session_id)

    async def event_gen():
        # Header line carrying session metadata.
        yield f"data: {_json.dumps({'type': 'session', 'task_id': task_id, 'worktree': str(worktree_root), 'branch': b3_session.worktree_branch(domain_slug), 'agent_session_id': agent_session_id})}\n\n"
        prompt = (
            f"Run /strategy assemble {domain_slug} in non-interactive mode. "
            f"Working directory is this worktree ({worktree_root}). Target "
            f"doc is docs/project/strategies/{domain_slug}-strategy.md. "
            f"Author attribution: {actor}. When done, print a JSON summary "
            f"line prefixed with `RESULT: ` containing keys "
            f"`scanned_tasks`, `proposals_added`, `history_line`."
        )
        try:
            from claude_agent_sdk import (
                AssistantMessage,
                ClaudeAgentOptions,
                ResultMessage,
                StreamEvent,
                SystemMessage,
                TextBlock,
                ToolUseBlock,
                UserMessage,
                query,
            )
            # ToolResultBlock isn't always exported under the same name; try
            # both shapes defensively.
            try:
                from claude_agent_sdk import ToolResultBlock as _ToolResultBlock
            except Exception:
                _ToolResultBlock = None
        except Exception as e:
            yield f"data: {_json.dumps({'type': 'error', 'message': f'claude-agent-sdk import failed: {e}'})}\n\n"
            return
        model = _assembler_model(cfg)
        options = ClaudeAgentOptions(
            model=model,
            system_prompt=_ASSEMBLER_SYSTEM_PROMPT,
            allowed_tools=_ASSEMBLER_ALLOWED_TOOLS,
            permission_mode="bypassPermissions",
            cwd=str(worktree_root),
            max_turns=30,
            include_partial_messages=True,
        )
        yield f"data: {_json.dumps({'type': 'model_pinned', 'model': model})}\n\n"
        sdk_session_id: str | None = None
        _sdk_state_files: list = []
        denial_count = 0
        tool_count = 0
        write_count = 0
        bail_reason = None

        def _capture_sdk_session_id(msg) -> str | None:
            for attr in ("session_id", "sessionId"):
                v = getattr(msg, attr, None)
                if v:
                    return v
            data = getattr(msg, "data", None)
            if isinstance(data, dict):
                return data.get("session_id") or data.get("sessionId")
            return None

        def _is_gate_denial(text: str) -> bool:
            return ("TASK GATE" in text) or ("No active task for session" in text)

        try:
            async for msg in query(prompt=prompt, options=options):
                # As soon as the SDK emits any message carrying its real
                # session_id, write a state file for THAT id so the gate
                # passes for subsequent Write/Edit tool calls. Race-free in
                # practice because the SDK emits its init/system message
                # before any tool call resolves.
                if sdk_session_id is None:
                    sid = _capture_sdk_session_id(msg)
                    if sid:
                        sdk_session_id = sid
                        try:
                            sdk_state_files_local = _write_state(sdk_session_id)
                            # Mutate the outer list in place — avoids needing
                            # `nonlocal` (annotated names can't be nonlocal).
                            _sdk_state_files.clear()
                            _sdk_state_files.extend(sdk_state_files_local)
                            yield f"data: {_json.dumps({'type': 'session_pinned', 'sdk_session_id': sdk_session_id, 'state_files': len(sdk_state_files_local)})}\n\n"
                        except Exception as e:
                            yield f"data: {_json.dumps({'type': 'error', 'message': f'state-file write failed for sdk_session_id: {e}'})}\n\n"

                if isinstance(msg, StreamEvent):
                    evt = msg.event or {}
                    if evt.get("type") == "content_block_delta":
                        delta = evt.get("delta") or {}
                        if delta.get("type") == "text_delta":
                            text = delta.get("text") or ""
                            if text:
                                yield f"data: {_json.dumps({'type': 'token', 'text': text})}\n\n"
                elif isinstance(msg, AssistantMessage):
                    for block in msg.content:
                        if isinstance(block, ToolUseBlock):
                            tool_count += 1
                            if block.name in ("Write", "Edit", "NotebookEdit"):
                                write_count += 1
                            brief = ""
                            if block.name == "Bash":
                                brief = (block.input.get("command") or "")[:200]
                            elif block.name in ("Read", "Write", "Edit"):
                                brief = block.input.get("file_path") or ""
                            yield f"data: {_json.dumps({'type': 'tool', 'name': block.name, 'brief': brief})}\n\n"
                elif isinstance(msg, UserMessage):
                    # Tool results come back on the next user turn. Watch for
                    # task-gate denials and other tool errors so we fail fast
                    # instead of letting the agent silently improvise.
                    for block in (getattr(msg, "content", None) or []):
                        is_err = getattr(block, "is_error", False) or False
                        content = getattr(block, "content", None)
                        if content is None:
                            continue
                        # Normalize tool-result content (str | list[dict] | list[TextBlock]).
                        if isinstance(content, list):
                            parts = []
                            for c in content:
                                if isinstance(c, dict):
                                    parts.append(c.get("text", "") or "")
                                else:
                                    parts.append(getattr(c, "text", "") or str(c))
                            content_str = " ".join(parts)
                        else:
                            content_str = str(content)
                        if is_err:
                            tag = "tool_denied" if _is_gate_denial(content_str) else "tool_error"
                            if tag == "tool_denied":
                                denial_count += 1
                            yield f"data: {_json.dumps({'type': tag, 'detail': content_str[:300]})}\n\n"
                            # Fail fast: any task-gate denial OR two tool
                            # errors in the run is enough to abort.
                            if tag == "tool_denied" or denial_count + 0 >= 1 or (denial_count == 0 and tool_count > 0 and content_str and "command not found" not in content_str and tag == "tool_error"):
                                # Simpler rule: ANY denial OR two errors abort.
                                pass
                            if denial_count >= 1:
                                bail_reason = (
                                    "task_gate_denial — synthetic session id "
                                    "did not propagate; SDK is using its own "
                                    "session id and the state file we wrote "
                                    "after pinning may have arrived too late."
                                )
                                break
                    if bail_reason:
                        break
                elif isinstance(msg, ResultMessage):
                    yield f"data: {_json.dumps({'type': 'result', 'summary': getattr(msg, 'result', '')})}\n\n"
        except Exception as e:
            bail_reason = bail_reason or f"stream-exception: {e}"
            yield f"data: {_json.dumps({'type': 'error', 'message': str(e)})}\n\n"
        finally:
            # Tear down all state files (synthetic + sdk-pinned, both repo
            # and worktree copies) and restore the parent
            # CLAUDE_SESSION_ID env var.
            for f in (synthetic_state_files + _sdk_state_files):
                try:
                    if f is not None and f.exists():
                        f.unlink()
                except Exception:
                    pass
            if _prev_env is None:
                _os.environ.pop("CLAUDE_SESSION_ID", None)
            else:
                _os.environ["CLAUDE_SESSION_ID"] = _prev_env
            # Post-condition health check — verifies the agent actually
            # produced visible output before claiming success.
            health = {
                "tool_count": tool_count,
                "write_count": write_count,
                "denial_count": denial_count,
                "worktree_diff": [],
            }
            try:
                from console.workflows.b3_session import worktree_diff_summary as _wt_diff
                health["worktree_diff"] = _wt_diff(worktree_root)
            except Exception:
                pass
            terminal = {
                "type": "terminal",
                "status": (
                    "failed" if bail_reason
                    else ("success" if (write_count > 0 and health["worktree_diff"]) else "no_op")
                ),
                "reason": bail_reason or (
                    "no Write tool calls" if write_count == 0
                    else ("worktree clean — agent's writes did not persist" if not health["worktree_diff"]
                          else "agent wrote and worktree shows pending changes")
                ),
                **health,
            }
            yield f"data: {_json.dumps(terminal)}\n\n"
        yield f"data: {_json.dumps({'type': 'done'})}\n\n"

    return StreamingResponse(event_gen(), media_type="text/event-stream")


@router.get("/workflows/strategy-reassembly/{domain_slug}/session")
async def b3_session_snapshot(request: Request, domain_slug: str):
    """Return the current session state for this (actor, domain), or null
    if none exists. UI polls this to show the pending-changes banner +
    Commit button."""
    cfg = get_config()
    actor_info = _resolve_actor(cfg.repo_root)
    actor_folder = actor_info.get("task_folder") or ""
    if not actor_folder:
        return JSONResponse({"session": None})
    sess = b3_session.snapshot(cfg.repo_root, actor_folder, domain_slug)
    if sess is None:
        return JSONResponse({"session": None})
    return JSONResponse(
        {
            "session": {
                "domain": sess.domain,
                "task_id": sess.task_id,
                "task_path": sess.task_path,
                "worktree_path": sess.worktree_path,
                "branch": sess.branch,
                "has_diff": sess.has_diff,
                "diff_summary": sess.diff_summary,
            }
        }
    )


def _decision_session_bootstrap(cfg, domain_slug: str):
    """Common front-half for the three /decision/* endpoints: resolve
    actor + auto-create session task + open worktree. Returns
    (actor, actor_folder, task_id, worktree_root, doc_wt) or raises HTTP."""
    actor_info = _resolve_actor(cfg.repo_root)
    if actor_info.get("unresolved"):
        raise HTTPException(403, f"Actor unresolved ({actor_info.get('reason')}).")
    actor = actor_info.get("name") or ""
    actor_folder = actor_info.get("task_folder") or ""
    if not actor_folder:
        raise HTTPException(403, "Actor has no task_folder in project.yml")
    try:
        task_id, _, worktree_root = b3_session.resolve_or_create(
            cfg.repo_root, actor_folder, actor, domain_slug
        )
    except RuntimeError as e:
        raise HTTPException(409, f"session bootstrap failed: {e}")
    doc_wt = b3_strategy_reassembly.get_by_slug(worktree_root, domain_slug)
    if doc_wt is None:
        raise HTTPException(409, f"strategy doc missing inside worktree: {worktree_root}")
    return actor, actor_folder, task_id, worktree_root, doc_wt


def _auto_commit_after_decision_action(
    cfg, doc, domain_slug: str, actor_folder: str, actor: str, message: str
) -> dict:
    try:
        return b3_session.commit_and_merge(
            cfg.repo_root, actor_folder, actor, domain_slug, message
        )
    except RuntimeError as e:
        return {
            "committed": False,
            "error": str(e),
            "note": (
                "Change applied inside the worktree, but auto-commit/merge failed. "
                "Click Save & Publish to land manually."
            ),
        }


_SYNTHESIS_SYSTEM_PROMPT = (
    "You revise a strategy-decision body based on a discussion between a "
    "user and an advisor. Your job:\n"
    "\n"
    "1. Read the ORIGINAL body of the decision (verbatim, provided below).\n"
    "2. Read the user/advisor conversation transcript (provided below).\n"
    "3. Identify exactly what the user wants changed. The conversation may "
    "cover multiple distinct topics — capture every intent the user "
    "explicitly approved or asked for.\n"
    "4. Produce a REVISED markdown body that:\n"
    "   • PRESERVES the structure, formatting, tone, and existing wording "
    "of the original wherever it isn't being changed (keep tables, lists, "
    "bold/italic, code blocks, line breaks intact).\n"
    "   • APPLIES only what the user explicitly approved or asked for — "
    "do not invent new content, do not rephrase passages the user didn't "
    "discuss, do not add content the user didn't request.\n"
    "   • If the user only asked clarifying questions and did not request "
    "changes, output the original body UNCHANGED.\n"
    "   • Maintains the same heading-line structure (a single H3 at the "
    "top is fine; do not add or remove H3s).\n"
    "\n"
    "Output ONLY the revised markdown body. No preamble, no explanation, "
    "no marker comments, no code-fence wrapping around the entire output. "
    "Start with the first character of the revised body and end with the "
    "last."
)


async def _synthesize_decision_edit(
    cfg, original_body: str, conversation: list, decision_id: str, heading: str
) -> str:
    """Run a focused Opus synthesis pass over the conversation + original
    body, return the revised body markdown verbatim. Falls back to raising
    HTTPException on SDK errors."""
    from claude_agent_sdk import (
        AssistantMessage,
        ClaudeAgentOptions,
        ResultMessage,
        TextBlock,
        query,
    )
    transcript_lines: list[str] = []
    for turn in (conversation or [])[-30:]:  # cap at last 30 turns
        role = (turn.get("role") or "?").strip()
        text = (turn.get("text") or "").strip()
        if not text:
            continue
        transcript_lines.append(f"### {role}\n{text}")
    transcript = "\n\n".join(transcript_lines) or "(no discussion captured)"

    prompt = (
        f"Decision being revised: {decision_id} — {heading}\n\n"
        f"## ORIGINAL BODY\n\n{original_body}\n\n"
        f"## CONVERSATION\n\n{transcript}\n\n"
        f"Produce the revised body now. Preserve fidelity; apply only what "
        f"the user explicitly approved."
    )
    options = ClaudeAgentOptions(
        model=_assembler_model(cfg),  # reuse the same Opus pin as the assembler
        system_prompt=_SYNTHESIS_SYSTEM_PROMPT,
        permission_mode="bypassPermissions",
        cwd=str(cfg.repo_root),
        max_turns=2,
        include_partial_messages=False,
    )
    out_chunks: list[str] = []
    try:
        async for msg in query(prompt=prompt, options=options):
            if isinstance(msg, AssistantMessage):
                for block in (msg.content or []):
                    if isinstance(block, TextBlock) and block.text:
                        out_chunks.append(block.text)
            elif isinstance(msg, ResultMessage):
                # Final summary may carry the body too; keep last assistant text only.
                pass
    except Exception as e:
        raise HTTPException(502, f"synthesis failed: {e}")
    revised = "".join(out_chunks).strip()
    if not revised:
        raise HTTPException(502, "synthesis returned empty body")
    return revised


_SECTION_SYNTHESIS_PROMPT = (
    "You revise an entire H2 section of a strategy document based on a "
    "discussion between a user and an advisor. Each section may contain "
    "narrative + zero-or-more decisions wrapped in DECISION:start/end "
    "sentinels. Your job:\n"
    "\n"
    "1. Read the ORIGINAL section content (provided below).\n"
    "2. Read the user/advisor conversation transcript.\n"
    "3. Identify the user's intent — they may want to ADD new decisions, "
    "EDIT existing ones, restructure narrative, or some combination. "
    "Capture every change the user explicitly approved.\n"
    "4. Produce a REVISED section as clean markdown with these rules:\n"
    "   • Keep the H2 line (`## N. Section Name`) verbatim.\n"
    "   • Each decision is wrapped in `<!-- DECISION:start id=... status=... -->` "
    "and `<!-- DECISION:end id=... -->` sentinels.\n"
    "   • For EXISTING decisions whose content you're keeping or editing, "
    "PRESERVE the id field exactly (e.g. `id=D-REG-2.1`). Keep status=active "
    "unless the user requested otherwise. The H3 heading prefix (e.g. `2.1`) "
    "stays.\n"
    "   • For NEW decisions you're adding, use `id=NEW` as a placeholder — "
    "the system will allocate a real id on save. Use a draft heading prefix "
    "like `2.NEW` followed by the heading text, e.g. "
    "`### 2.NEW Pre-Op Class IIb Reclassification`.\n"
    "   • For decisions the user wanted REMOVED, simply OMIT them from your "
    "output — git history preserves the audit trail.\n"
    "   • PRESERVE fidelity of unchanged decisions (keep their bodies "
    "verbatim — same wording, tables, lists, formatting).\n"
    "\n"
    "Output ONLY the revised section markdown — no preamble, no explanation, "
    "no code-fence wrapping. Start with the H2 line and end with the last "
    "line of the section."
)


async def _synthesize_section_edit(
    cfg, original_section_md: str, conversation: list, section_label: str
) -> str:
    """Run an Opus pass to revise an entire section based on a chat. Returns
    the revised section markdown (with DECISION:start/end sentinels)."""
    from claude_agent_sdk import (
        AssistantMessage, ClaudeAgentOptions, ResultMessage, TextBlock, query,
    )
    transcript_lines: list[str] = []
    for turn in (conversation or [])[-30:]:
        role = (turn.get("role") or "?").strip()
        text = (turn.get("text") or "").strip()
        if not text:
            continue
        transcript_lines.append(f"### {role}\n{text}")
    transcript = "\n\n".join(transcript_lines) or "(no discussion captured)"

    prompt = (
        f"Section being revised: {section_label}\n\n"
        f"## ORIGINAL SECTION CONTENT\n\n{original_section_md}\n\n"
        f"## CONVERSATION\n\n{transcript}\n\n"
        f"Produce the revised section now. Preserve fidelity of unchanged "
        f"decisions; apply only what the user explicitly approved. Use "
        f"`id=NEW` for any decisions added; preserve existing `id=D-...` "
        f"values for kept/edited decisions."
    )
    options = ClaudeAgentOptions(
        model=_assembler_model(cfg),
        system_prompt=_SECTION_SYNTHESIS_PROMPT,
        permission_mode="bypassPermissions",
        cwd=str(cfg.repo_root),
        max_turns=2,
        include_partial_messages=False,
    )
    out_chunks: list[str] = []
    try:
        async for msg in query(prompt=prompt, options=options):
            if isinstance(msg, AssistantMessage):
                for block in (msg.content or []):
                    if isinstance(block, TextBlock) and block.text:
                        out_chunks.append(block.text)
    except Exception as e:
        raise HTTPException(502, f"section synthesis failed: {e}")
    revised = "".join(out_chunks).strip()
    if not revised:
        raise HTTPException(502, "section synthesis returned empty content")
    return revised


@router.post("/workflows/strategy-reassembly/{domain_slug}/section/{section_idx}/synthesize-edit")
async def b3_section_synthesize(request: Request, domain_slug: str, section_idx: int):
    """Run a synthesis pass over the chat to produce a revised SECTION.
    Returns the revised section markdown + rendered HTML for the modal."""
    cfg = get_config()
    actor, actor_folder, task_id, worktree_root, doc_wt = _decision_session_bootstrap(cfg, domain_slug)
    body = await request.json()
    conversation = body.get("conversation") or []
    if not isinstance(conversation, list) or not conversation:
        raise HTTPException(400, "`conversation` must be a non-empty list")
    abs_path = worktree_root / doc_wt.virtual_path
    text = abs_path.read_text(encoding="utf-8")
    bounds = b3_strategy_reassembly.section_block(text, section_idx)
    if bounds is None:
        raise HTTPException(404, f"section {section_idx} not found")
    s, e, label = bounds
    original_md = "\n".join(text.splitlines()[s:e]).rstrip() + "\n"
    revised = await _synthesize_section_edit(cfg, original_md, conversation, label)
    import markdown as _md
    eng = _md.Markdown(extensions=["tables", "fenced_code", "sane_lists"])
    eng.reset(); original_html = eng.convert(original_md)
    eng.reset(); revised_html = eng.convert(revised)
    return JSONResponse(
        {
            "section_idx": section_idx,
            "section_label": label,
            "model": _assembler_model(cfg),
            "original_section_md": original_md,
            "original_section_html": original_html,
            "proposed_section_md": revised,
            "proposed_section_html": revised_html,
            "unchanged": revised.strip() == original_md.strip(),
        }
    )


@router.post("/workflows/strategy-reassembly/{domain_slug}/section/{section_idx}/edit-via-chat")
async def b3_section_edit_via_chat(request: Request, domain_slug: str, section_idx: int):
    """Apply the revised section to the strategy doc, allocate fresh IDs
    for `id=NEW` placeholders, append a History entry + session-task
    changelog row, and auto-commit + auto-publish to main."""
    cfg = get_config()
    actor, actor_folder, task_id, worktree_root, doc_wt = _decision_session_bootstrap(cfg, domain_slug)
    body = await request.json()
    new_section_md = (body.get("new_section_md") or "").strip()
    if not new_section_md:
        raise HTTPException(400, "`new_section_md` is required")
    chat_summary = body.get("chat_summary") or []
    try:
        result = b3_strategy_reassembly.perform_section_edit(
            worktree_root, doc_wt, section_idx, new_section_md,
            actor=actor, active_task_ids_=[task_id],
        )
    except RuntimeError as e:
        raise HTTPException(409, str(e))
    # Append session-task changelog entry.
    try:
        task_path = cfg.repo_root / "tasks" / actor_folder
        for p in task_path.glob(f"{task_id}-*.md"):
            txt = p.read_text(encoding="utf-8")
            from datetime import datetime, timezone
            ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
            entry = (
                f"\n- {ts} — **Edit section via chat**: section {section_idx} "
                f"({domain_slug}) revised by {actor}.\n"
                f"  - Added: {result['added_ids'] or '(none)'}\n"
                f"  - Edited: {result['edited_ids'] or '(none)'}\n"
                f"  - Removed: {result['removed_ids'] or '(none)'}\n"
            )
            if chat_summary:
                entry += "  - Discussion (last turns):\n"
                for turn in chat_summary[-6:]:
                    role = (turn.get("role") or "?").strip()
                    snippet = (turn.get("text") or "").strip()[:140]
                    entry += f"    - **{role}**: {snippet}\n"
            p.write_text(txt.rstrip() + "\n" + entry, encoding="utf-8")
            break
    except Exception as ex:
        result["task_doc_append_error"] = str(ex)
    msg = (
        f"workflow: edit section {section_idx} (via chat) · {domain_slug} · "
        f"by {actor}"
    )
    result["auto_commit"] = _auto_commit_after_decision_action(
        cfg, doc_wt, domain_slug, actor_folder, actor, msg
    )
    return JSONResponse(result)


@router.post("/workflows/strategy-reassembly/render-md")
async def b3_render_md(request: Request):
    """Render arbitrary markdown to HTML — used by the synthesis preview
    modal's Preview/Edit toggle so a hand-edited body can be re-rendered
    without round-tripping the full synthesis pass."""
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(400, "Expected JSON body")
    md = body.get("markdown") or ""
    import markdown as _md
    eng = _md.Markdown(extensions=["tables", "fenced_code", "sane_lists"])
    eng.reset()
    return JSONResponse({"html": eng.convert(md)})


@router.post("/workflows/strategy-reassembly/{domain_slug}/decision/{decision_id}/synthesize-edit")
async def b3_decision_synthesize_edit(request: Request, domain_slug: str, decision_id: str):
    """Run a synthesis pass over the chat to produce a revised body. The
    caller (UI) then shows the body to the user for explicit confirmation
    before posting to /edit-via-chat to commit. No file mutations here."""
    cfg = get_config()
    body = await request.json()
    conversation = body.get("conversation") or []
    if not isinstance(conversation, list) or not conversation:
        raise HTTPException(400, "`conversation` must be a non-empty list of {role, text}")
    original_body = (body.get("original_body") or "").strip()
    heading = (body.get("heading") or "").strip()
    if not original_body:
        raise HTTPException(400, "`original_body` is required")
    revised = await _synthesize_decision_edit(
        cfg, original_body, conversation, decision_id, heading
    )
    # Render both bodies as HTML so the preview modal shows formatted
    # markdown instead of raw text. Reuse the same engine the rest of B3
    # uses (tables, fenced_code, sane_lists).
    import markdown as _md
    md_engine = _md.Markdown(extensions=["tables", "fenced_code", "sane_lists"])
    md_engine.reset()
    original_html = md_engine.convert(original_body)
    md_engine.reset()
    revised_html = md_engine.convert(revised)
    return JSONResponse(
        {
            "decision_id": decision_id,
            "model": _assembler_model(cfg),
            "proposed_body": revised,
            "proposed_body_html": revised_html,
            "original_body_html": original_html,
            "unchanged": revised.strip() == original_body.strip(),
        }
    )


@router.post("/workflows/strategy-reassembly/{domain_slug}/decision/{decision_id}/edit-via-chat")
async def b3_decision_edit_via_chat(request: Request, domain_slug: str, decision_id: str):
    """Edit-via-chat finalize: receives the final proposed body extracted
    from the assistant's latest message + a short chat summary. Mutates
    the decision via the same `perform_decision_edit` path, then appends
    a structured Changelog entry to the session task doc capturing the
    discussion. Auto-commits via the standard worktree path."""
    cfg = get_config()
    actor, actor_folder, task_id, worktree_root, doc_wt = _decision_session_bootstrap(cfg, domain_slug)
    body = await request.json()
    new_body = (body.get("new_body") or "").strip()
    if not new_body:
        raise HTTPException(400, "`new_body` is required (extracted from assistant's last reply)")
    chat_summary = body.get("chat_summary") or []
    if not isinstance(chat_summary, list):
        chat_summary = []
    try:
        result = b3_strategy_reassembly.perform_decision_edit(
            worktree_root, doc_wt, decision_id, new_body,
            actor=actor, active_task_ids_=[task_id],
        )
    except RuntimeError as e:
        raise HTTPException(409, str(e))
    # Append a structured Changelog entry to the session task doc.
    try:
        task_path = cfg.repo_root / "tasks" / actor_folder
        for p in task_path.glob(f"{task_id}-*.md"):
            txt = p.read_text(encoding="utf-8")
            from datetime import datetime, timezone
            ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
            entry = f"\n- {ts} — **Edit via chat**: decision `{decision_id}` revised by {actor} via assistant drawer.\n"
            if chat_summary:
                entry += "  - Discussion (last turns):\n"
                for turn in chat_summary[-6:]:
                    role = (turn.get("role") or "?").strip()
                    text = (turn.get("text") or "").strip()
                    if not text:
                        continue
                    snippet = text if len(text) <= 140 else text[:140] + "…"
                    entry += f"    - **{role}**: {snippet}\n"
            entry += f"  - Final body preview: {new_body[:160]}{'…' if len(new_body) > 160 else ''}\n"
            txt = txt.rstrip() + "\n" + entry
            p.write_text(txt, encoding="utf-8")
            break
    except Exception as e:
        result["task_doc_append_error"] = str(e)
    msg = f"workflow: edit (via chat) decision {decision_id} · {domain_slug} · by {actor}"
    result["auto_commit"] = _auto_commit_after_decision_action(
        cfg, doc_wt, domain_slug, actor_folder, actor, msg
    )
    return JSONResponse(result)


@router.post("/workflows/strategy-reassembly/{domain_slug}/decision/{decision_id}/edit")
async def b3_decision_edit(request: Request, domain_slug: str, decision_id: str):
    cfg = get_config()
    actor, actor_folder, task_id, worktree_root, doc_wt = _decision_session_bootstrap(cfg, domain_slug)
    body = await request.json()
    new_body = (body.get("new_body") or "").strip()
    if not new_body:
        raise HTTPException(400, "`new_body` is required")
    try:
        result = b3_strategy_reassembly.perform_decision_edit(
            worktree_root, doc_wt, decision_id, new_body, actor=actor, active_task_ids_=[task_id]
        )
    except RuntimeError as e:
        raise HTTPException(409, str(e))
    msg = f"workflow: edit decision {decision_id} · {domain_slug} · by {actor}"
    result["auto_commit"] = _auto_commit_after_decision_action(
        cfg, doc_wt, domain_slug, actor_folder, actor, msg
    )
    return JSONResponse(result)


@router.post("/workflows/strategy-reassembly/{domain_slug}/decision/{decision_id}/remove")
async def b3_decision_remove(domain_slug: str, decision_id: str):
    cfg = get_config()
    actor, actor_folder, task_id, worktree_root, doc_wt = _decision_session_bootstrap(cfg, domain_slug)
    try:
        result = b3_strategy_reassembly.perform_decision_remove(
            worktree_root, doc_wt, decision_id, actor=actor, active_task_ids_=[task_id]
        )
    except RuntimeError as e:
        raise HTTPException(409, str(e))
    msg = f"workflow: remove decision {decision_id} (withdrawn) · {domain_slug} · by {actor}"
    result["auto_commit"] = _auto_commit_after_decision_action(
        cfg, doc_wt, domain_slug, actor_folder, actor, msg
    )
    return JSONResponse(result)


@router.post("/workflows/strategy-reassembly/{domain_slug}/decision/add")
async def b3_decision_add(request: Request, domain_slug: str):
    cfg = get_config()
    actor, actor_folder, task_id, worktree_root, doc_wt = _decision_session_bootstrap(cfg, domain_slug)
    body = await request.json()
    section_label = (body.get("section_label") or "").strip()
    heading = (body.get("heading") or "").strip()
    new_body = (body.get("new_body") or "").strip()
    if not section_label or not heading or not new_body:
        raise HTTPException(400, "section_label, heading, and new_body are all required")
    try:
        result = b3_strategy_reassembly.perform_decision_add(
            worktree_root, doc_wt, section_label, heading, new_body,
            actor=actor, active_task_ids_=[task_id],
        )
    except RuntimeError as e:
        raise HTTPException(409, str(e))
    msg = f"workflow: add decision {result['decision_id']} · \"{heading}\" · {domain_slug} · by {actor}"
    result["auto_commit"] = _auto_commit_after_decision_action(
        cfg, doc_wt, domain_slug, actor_folder, actor, msg
    )
    return JSONResponse(result)


@router.get("/workflows/strategy-reassembly/{domain_slug}/file-diff")
async def b3_file_diff(domain_slug: str, path: str):
    """Return both views of the diff for a single file in this domain's
    worktree:
      • `friendly_html` — line-by-line table with semantic added/removed
        rows, no `+`/`-` gutters; for non-technical reviewers.
      • `raw_diff` — git's unified diff output; for power users."""
    cfg = get_config()
    wt = b3_session.worktree_path(cfg.repo_root, domain_slug)
    if not wt.is_dir():
        raise HTTPException(404, f"no open worktree for {domain_slug}")
    return JSONResponse(
        {
            "path": path,
            "friendly_html": b3_session.friendly_file_diff_html(wt, path),
            "raw_diff": b3_session.worktree_file_diff(wt, path),
        }
    )


@router.post("/workflows/strategy-reassembly/{domain_slug}/discard")
async def b3_discard(request: Request, domain_slug: str):
    """Discard a single pending change in this domain's worktree."""
    cfg = get_config()
    wt = b3_session.worktree_path(cfg.repo_root, domain_slug)
    if not wt.is_dir():
        raise HTTPException(404, f"no open worktree for {domain_slug}")
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(400, "Expected JSON body")
    path = (body.get("path") or "").strip()
    if not path:
        raise HTTPException(400, "`path` is required")
    result = b3_session.worktree_discard(wt, path)
    return JSONResponse(result)


@router.post("/workflows/strategy-reassembly/{domain_slug}/commit")
async def b3_commit(request: Request, domain_slug: str):
    """Commit worktree changes, fast-forward merge into main, push to
    origin if configured, tear down the worktree + branch, and mark the
    backing task Complete."""
    cfg = get_config()
    actor_info = _resolve_actor(cfg.repo_root)
    if actor_info.get("unresolved"):
        raise HTTPException(403, f"Actor unresolved ({actor_info.get('reason')}).")
    actor = actor_info.get("name") or ""
    actor_folder = actor_info.get("task_folder") or ""
    try:
        body = await request.json()
    except Exception:
        body = {}
    message = (body.get("message") or "").strip()
    if not message:
        message = (
            f"workflow: strategy re-assembly — {domain_slug} — "
            f"{b3_session.today()} by {actor}"
        )
    try:
        result = b3_session.commit_and_merge(
            cfg.repo_root, actor_folder, actor, domain_slug, message
        )
    except RuntimeError as e:
        raise HTTPException(409, str(e))
    return JSONResponse(result)


@router.post("/workflows/doc-roundtrip-batch/dry-run")
async def b1_dry_run(request: Request):
    """Accept a JSON body `{"selected": ["path1", "path2", ...]}` and return
    the export plan. DRY RUN: does not invoke /docflow."""
    cfg = get_config()
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(400, "Expected JSON body")
    selected = body.get("selected") or []
    if not isinstance(selected, list):
        raise HTTPException(400, "`selected` must be a list of paths")

    plan = b1_doc_roundtrip.build_plan(cfg.repo_root, [str(x) for x in selected])
    return JSONResponse(
        {
            "dry_run": True,
            "backend_status": "placeholder",
            "count": len(plan),
            "plan": [
                {
                    "virtual_path": e.virtual_path,
                    "proposed_docx": e.proposed_docx,
                    "command": e.command,
                    "backend_status": e.backend_status,
                }
                for e in plan
            ],
            "note": (
                "This prototype does not execute /docflow. A real run would "
                "invoke each command above and write the target DOCX."
            ),
        }
    )
