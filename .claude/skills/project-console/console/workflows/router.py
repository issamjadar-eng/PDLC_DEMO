"""Workflows router — index page + per-workflow views + B1/B3 APIs."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from console.commercial.loader import list_domains, skill_render_script
from console.config import get_config
from console.documents import renderer as doc_renderer
from console.workflows import b1_doc_roundtrip, b3_session, b3_strategy_reassembly
from console.workflows import tracker_session, tracker_writer
from console.workflows import draft_session, draft_writer
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

    if slug == "tracker-status-update":
        return templates.TemplateResponse(
            request, "workflow_tracker.html", {"config": cfg, "workflow": wf},
        )

    if slug == "tracker-advisor":
        return templates.TemplateResponse(
            request, "workflow_tracker_advisor.html", {"config": cfg, "workflow": wf},
        )

    if slug == "strategy-reassembly":
        # Strategy was promoted to a topline section (task ben/087). The GET
        # landing now lives at /strategy; the mutation endpoints below
        # (/workflows/strategy-reassembly/<domain>/*) stay put — the template
        # JS still posts to them. Redirect the old page URL to the new home.
        return RedirectResponse(url="/strategy", status_code=307)

    if slug == "management-review-pack":
        return templates.TemplateResponse(
            request, "workflow_mgmt_review.html",
            {"config": cfg, "workflow": wf, **_mgmt_review_ctx(cfg, request)},
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


PACK_ROOT = ("docs", "project", "management-review")


def _mgmt_review_ctx(cfg, request: Request) -> dict:
    """Packs on disk (newest first) + the newest rendered in place + the domain roster
    the generate action will pass to the engine. Pure read; the engine assembles."""
    root = cfg.repo_root.joinpath(*PACK_ROOT)
    packs = []
    if root.is_dir():
        for d in sorted((p for p in root.iterdir() if p.is_dir()), reverse=True):
            if not (d / "pack.md").is_file():
                continue
            summary = None
            try:
                summary = json.loads((d / "pack.json").read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                pass
            packs.append({"date": d.name, "rel": str((d / "pack.md").relative_to(cfg.repo_root)),
                          "summary": summary})
    show = request.query_params.get("pack") or (packs[0]["date"] if packs else None)
    current = next((p for p in packs if p["date"] == show), None)
    html = ""
    if current:
        try:
            html = doc_renderer.render(cfg.repo_root / current["rel"]).body_html or ""
        except Exception:
            html = "<p><em>pack failed to render — open it in Documents.</em></p>"
    return {"packs": packs, "current": current, "pack_html": html,
            "domains": list_domains(cfg.repo_root),
            "has_engine": skill_render_script(cfg.repo_root) is not None,
            "gen_error": request.query_params.get("gen_error"),
            "generated": request.query_params.get("generated")}


@router.post("/workflows/management-review-pack/generate")
async def mgmt_review_generate(request: Request):
    """Shell the engine's `pack` over every discovered domain. Approved editions only
    unless the form asks for a draft preview (flagged inline by the engine)."""
    from urllib.parse import quote
    cfg = get_config()
    form = await request.form()
    script = skill_render_script(cfg.repo_root)
    back = "/workflows/management-review-pack"
    if script is None:
        return RedirectResponse(back + "?gen_error=" + quote("commercial skill not installed", safe=""), status_code=303)
    doms = ",".join(d["key"] for d in list_domains(cfg.repo_root)) or "commercial"
    cmd = ["python3", str(script), "pack", "--domains", doms, "--out", "/".join(PACK_ROOT)]
    as_of = str(form.get("as_of") or "").strip()
    if as_of:
        cmd += ["--as-of", as_of]
    if form.get("include_drafts"):
        cmd.append("--include-drafts")
    try:
        proc = subprocess.run(cmd, cwd=str(cfg.repo_root), capture_output=True, text=True, timeout=120)
    except subprocess.TimeoutExpired:
        return RedirectResponse(back + "?gen_error=" + quote("pack timed out", safe=""), status_code=303)
    if proc.returncode != 0:
        return RedirectResponse(back + "?gen_error=" + quote(((proc.stdout or "") + (proc.stderr or ""))[:1500], safe=""), status_code=303)
    return RedirectResponse(back + "?generated=1", status_code=303)


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
                "branch": b3_session.worktree_branch(cfg.repo_root, domain_slug),
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
    "do NOT prompt the user under any circumstances. Every newly-introduced "
    "or modified decision must be emitted as a `> **Proposed change**` "
    "blockquote callout so the user can review each one independently in "
    "the project-console. There are TWO callout flavors:\n"
    "\n"
    "Every callout's first line MUST be exactly:\n"
    "    > **Proposed change** — <task_folder>/<NNN> (\"<Heading>\", <Author>, <YYYY-MM-DD>)\n"
    "with `<task_folder>/<NNN>` written as PLAIN TEXT (NOT a markdown link). "
    "Example: `> **Proposed change** — ben/136 (\"Corpus & Retrieval Architecture\", Ben Xavier, 2026-05-01)`. "
    "The console's parser depends on this exact shape — markdown-link "
    "decoration like `[ben/136](path)` will break it.\n"
    "\n"
    "1. CONFLICT — a newer source rewrites an existing decision in the "
    "strategy doc. Write the newer block as a `> **Proposed change**` "
    "callout placed immediately after the existing decision, and emit the "
    "marker `<!-- STRATEGY PROPOSED: vs <older_task>, section \"X\" -->` "
    "right after the callout's closing line.\n"
    "\n"
    "2. NEW ADDITION — a source contributes a decision that has no existing "
    "equivalent in the strategy doc. Do NOT append this directly into the "
    "doc body. Instead, write it as a `> **Proposed change**` callout at "
    "the END of the relevant `## N. <Section>` block, with marker "
    "`<!-- STRATEGY PROPOSED: new addition, section \"X\" -->` right after. "
    "Inside the callout body, include the decision wrapped in placeholder "
    "DECISION sentinels: `<!-- DECISION:start id=NEW status=proposed "
    "source=<task_id> created=<YYYY-MM-DD> -->` ... body ... "
    "`<!-- DECISION:end id=NEW -->`. The console assigns a real id when the "
    "user clicks Accept. Use heading prefix `N.NEW` (e.g. `### 3.NEW Title`) "
    "as a placeholder; the real index is allocated at Accept time too.\n"
    "\n"
    "Every callout body must be the FULL decision body the user would see "
    "if accepted (including any tables, lists, formatting). The user reviews "
    "each callout independently — they may Accept, Reject, Modify, or "
    "Re-categorize each one.\n"
    "\n"
    "Aside from emitting callouts, follow the canonical assembler.md flow: "
    "scan task docs for `<!-- STRATEGY CONTENT -->` tags in the specified "
    "domain, update the strategy doc's header metadata "
    "(`<!-- Assembled: ... -->` and `<!-- Sources: ... -->`) and append "
    "Source Traceability + History entries. NEVER write a new authoritative "
    "decision (DECISION:start/end with a real id) directly into the doc — "
    "always go through the callout path. NEVER make git commits."
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

    # Concurrent-run guard: refuse to start a new assembler run if the
    # strategy doc inside the worktree already has uncommitted changes
    # from a prior run. The user must Save & Publish or Throw Away first
    # — otherwise the agent's writes silently overwrite their prior
    # unresolved diff.
    if b3_session.worktree_strategy_doc_dirty(worktree_root, domain_slug):
        raise HTTPException(
            409,
            (
                "There's already a pending assembler run for this domain. "
                "Save & Publish it (commits + merges to main) or Throw Away "
                "the pending diff before running the assembler again."
            ),
        )

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
        yield f"data: {_json.dumps({'type': 'session', 'task_id': task_id, 'worktree': str(worktree_root), 'branch': b3_session.worktree_branch(cfg.repo_root, domain_slug), 'agent_session_id': agent_session_id})}\n\n"
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
            # Loud server-log line so the user can correlate run outcomes
            # against the timestamped console-out.log without piecing together
            # SSE frames from the browser.
            print(
                f"[b3-assembler] domain={domain_slug} status={terminal['status']} "
                f"tool_count={tool_count} write_count={write_count} "
                f"denial_count={denial_count} worktree_diff_files={len(health['worktree_diff'])} "
                f"reason={terminal['reason']!r}",
                flush=True,
            )
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
    # Same per-proposal-review semantics as decision edits: queue as a
    # `> **Proposed change**` callout in the worktree, ship via Save & Publish
    # in the tab bar — never auto-merge mid-review.
    try:
        result = b3_strategy_reassembly.perform_section_edit_as_proposal(
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
    # Skip auto-commit — the section edit is now a `> **Proposed change**`
    # callout awaiting review alongside any other pending proposals.
    result["auto_commit"] = {
        "committed": False,
        "deferred": True,
        "note": "Queued as proposal — review in '📝 Awaiting your review' and ship via Save & Publish on the tab bar.",
    }
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
    # When a review session is active, decision edits land as `> **Proposed
    # change**` callouts in the worktree — not direct in-place rewrites
    # followed by auto-merge. The user reviews them in 📝 Awaiting your review
    # alongside assembler proposals and ships everything together via Save &
    # Publish on the tab bar. This keeps decision edits inside the same
    # per-proposal review pipeline (Accept / Reject / Modify / Re-categorize)
    # instead of bypassing the queue and silently shipping any unreviewed
    # callouts that already exist in the worktree.
    try:
        result = b3_strategy_reassembly.perform_decision_edit_as_proposal(
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
    # Skip auto-commit: the edit is now a `> **Proposed change**` callout
    # awaiting review. User ships it via Save & Publish on the tab bar
    # alongside any other pending proposals.
    result["auto_commit"] = {
        "committed": False,
        "deferred": True,
        "note": "Queued as proposal — review in '📝 Awaiting your review' and ship via Save & Publish on the tab bar.",
    }
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


@router.post("/workflows/strategy-reassembly/{domain_slug}/throw-away-all")
async def b3_throw_away_all(domain_slug: str):
    """Whole-doc Throw Away: revert ALL pending changes in this domain's
    worktree (the assembler's strategy-doc edits + any other staged-in
    files), but KEEP the worktree, branch, and backing session task open
    so the user can Run Assembler again. Use `/cancel-workflow` to also
    tear down the session."""
    cfg = get_config()
    wt = b3_session.worktree_path(cfg.repo_root, domain_slug)
    if not wt.is_dir():
        raise HTTPException(404, f"no open worktree for {domain_slug}")
    return JSONResponse(b3_session.worktree_discard_all(wt))


@router.post("/workflows/strategy-reassembly/{domain_slug}/cancel-workflow")
async def b3_cancel_workflow(domain_slug: str):
    """Tear down the entire workflow session for this domain: discard any
    pending diff, remove the worktree, delete the branch, mark the backing
    session task Abandoned. The opposite of Save & Publish."""
    cfg = get_config()
    actor_info = _resolve_actor(cfg.repo_root)
    if actor_info.get("unresolved"):
        raise HTTPException(403, f"Actor unresolved ({actor_info.get('reason')}).")
    actor_folder = actor_info.get("task_folder") or ""
    if not actor_folder:
        raise HTTPException(403, "Actor has no task_folder in project.yml")
    return JSONResponse(b3_session.cancel_workflow(cfg.repo_root, actor_folder, domain_slug))


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


# ── B4 / B5 Tracker workflows (task ben/154 P3) ──────────────────────────
#
# Two workflow kinds share the same session/worktree machinery:
#   * "status"  — interactive status updates (B4)
#   * "advisor" — Ask the Tracker Advisor (B5)
#
# All four endpoints (session / apply / save / cancel) are kind-parameterized.
# Apply is status-only today (advisor uses chat infra in P5/P6).


def _tracker_actor_or_error(cfg) -> tuple[str, str]:
    """Resolve actor → (name, task_folder) or raise HTTPException."""
    actor_info = _resolve_actor(cfg.repo_root)
    if actor_info.get("unresolved"):
        raise HTTPException(403, f"Actor unresolved ({actor_info.get('reason')}).")
    name = actor_info.get("name") or ""
    folder = actor_info.get("task_folder") or ""
    if not folder:
        raise HTTPException(403, "Actor has no task_folder in project.yml")
    return name, folder


@router.get("/workflows/tracker/{kind}/session")
async def tracker_session_snapshot(request: Request, kind: str):
    """Return the current session state for (actor, kind), plus the
    pending-changes list (parsed from the session task doc's changelog).
    UI polls this to render the sidebar pending-changes panel."""
    if kind not in tracker_session.VALID_KINDS:
        raise HTTPException(400, f"invalid kind {kind!r}")
    cfg = get_config()
    actor_info = _resolve_actor(cfg.repo_root)
    actor_folder = actor_info.get("task_folder") or ""
    if not actor_folder:
        return JSONResponse({"session": None, "pending": []})
    sess = tracker_session.snapshot(cfg.repo_root, actor_folder, kind)
    if sess is None:
        return JSONResponse({"session": None, "pending": []})
    pending = []
    if kind == "status":
        pending = tracker_writer.parse_pending_changes(
            cfg.repo_root / sess.task_path
        )
    return JSONResponse(
        {
            "session": {
                "kind": sess.kind,
                "task_id": sess.task_id,
                "task_path": sess.task_path,
                "worktree_path": sess.worktree_path,
                "branch": sess.branch,
                "has_diff": sess.has_diff,
                "diff_summary": sess.diff_summary,
            },
            "pending": pending,
        }
    )


@router.post("/workflows/tracker/status/apply")
async def tracker_status_apply(request: Request):
    """Apply ONE status change. Auto-creates session + worktree on first
    call (lazy bootstrap). Body:
        {"row_id": "PA1", "new_status": "Done", "rationale": "..." | null}
    Returns the structured write result (old/new status + side effects)."""
    cfg = get_config()
    actor, actor_folder = _tracker_actor_or_error(cfg)
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(400, "Expected JSON body")
    row_id = (body.get("row_id") or "").strip()
    new_status = (body.get("new_status") or "").strip()
    rationale = body.get("rationale") or None
    if not row_id or not new_status:
        raise HTTPException(400, "row_id and new_status required")
    if new_status not in tracker_writer.VALID_STATUSES:
        raise HTTPException(
            400,
            f"new_status {new_status!r} not in valid set "
            f"{sorted(tracker_writer.VALID_STATUSES)}",
        )
    try:
        task_id, task_path, wt = tracker_session.resolve_or_create(
            cfg.repo_root, actor_folder, actor, "status"
        )
    except RuntimeError as e:
        raise HTTPException(409, f"session bootstrap failed: {e}")
    try:
        result = tracker_writer.write_status_change(
            wt=wt,
            row_id=row_id,
            new_status=new_status,
            rationale=rationale,
            actor=actor,
            task_path=task_path,
            repo_root=cfg.repo_root,
        )
    except FileNotFoundError as e:
        raise HTTPException(409, str(e))
    except LookupError as e:
        raise HTTPException(404, str(e))
    except (tracker_writer.RowParseError, ValueError) as e:
        raise HTTPException(400, str(e))
    return JSONResponse({"task_id": task_id, "result": result})


@router.post("/workflows/tracker/{kind}/save")
async def tracker_save(request: Request, kind: str):
    """Stage + commit pending changes inside the worktree, ff-merge into
    main, push to origin, tear down worktree, mark session task Complete.
    Returns commit_and_merge result."""
    if kind not in tracker_session.VALID_KINDS:
        raise HTTPException(400, f"invalid kind {kind!r}")
    cfg = get_config()
    actor, actor_folder = _tracker_actor_or_error(cfg)
    try:
        body = await request.json()
    except Exception:
        body = {}
    msg = (body.get("message") or "").strip() or _default_commit_message(
        cfg, actor_folder, kind
    )
    try:
        result = tracker_session.commit_and_merge(
            cfg.repo_root, actor_folder, actor, kind, msg
        )
    except RuntimeError as e:
        raise HTTPException(409, str(e))
    return JSONResponse({"saved": True, "kind": kind, "result": result})


@router.post("/workflows/tracker/{kind}/cancel")
async def tracker_cancel(request: Request, kind: str):
    """Discard pending changes, remove worktree + branch, mark task
    Abandoned. Idempotent."""
    if kind not in tracker_session.VALID_KINDS:
        raise HTTPException(400, f"invalid kind {kind!r}")
    cfg = get_config()
    _, actor_folder = _tracker_actor_or_error(cfg)
    result = tracker_session.cancel_workflow(cfg.repo_root, actor_folder, kind)
    return JSONResponse({"kind": kind, "result": result})


@router.get("/workflows/tracker/embed", response_class=HTMLResponse)
async def tracker_embed(request: Request):
    """Serve submission-tracker.html with the interactive overlay
    (tracker_interactive.css + tracker_interactive.js) injected before
    `</body>`. If a tracker-status worktree is open for this actor, serve
    the worktree's tracker html instead of main's so badge state reflects
    pending changes."""
    cfg = get_config()
    actor_info = _resolve_actor(cfg.repo_root)
    actor_folder = actor_info.get("task_folder") or ""
    # Prefer worktree HTML when a session is active (so the human sees the
    # current state including pending edits).
    html_path = cfg.repo_root / tracker_session.TRACKER_HTML_REL
    if actor_folder:
        sess = tracker_session.snapshot(cfg.repo_root, actor_folder, "status")
        if sess is not None:
            wt_html = Path(sess.worktree_path) / tracker_session.TRACKER_HTML_REL
            if wt_html.is_file():
                html_path = wt_html
    if not html_path.is_file():
        raise HTTPException(404, f"tracker html missing: {html_path}")
    html = html_path.read_text(encoding="utf-8")
    inject = (
        '<link rel="stylesheet" href="/static/tracker_interactive.css">\n'
        '<script src="/static/tracker_interactive.js" defer></script>\n'
        '</body>'
    )
    if "</body>" in html:
        html = html.replace("</body>", inject, 1)
    else:
        html = html + inject
    return HTMLResponse(content=html)


@router.get("/workflows/tracker-status-update", response_class=HTMLResponse)
async def tracker_status_update_page(request: Request):
    """Override the generic placeholder page for the tracker-status-update
    workflow with the interactive view (iframe + sidebar)."""
    cfg = get_config()
    return templates.TemplateResponse(
        request,
        "workflow_tracker.html",
        {"config": cfg, "workflow": get_by_slug("tracker-status-update")},
    )


# ── Dashboard inline-render assets ────────────────────────────────────────
# `_load_tracker_render()` dynamically imports `.claude/skills/tracker/scripts/
# render.py` so the dashboard inline-render path can reach `_CSS_BASE_INNER`,
# `_JS_INNER`, and `render_embed_fragment()` directly. Cached by mtime so
# edits to render.py take effect without restarting the console (uvicorn's
# auto-reload reloads `router.py` on its own change but does not invalidate
# importlib-loaded modules from outside the watched tree).

_TRACKER_RENDER_CACHE = {"mtime": None, "module": None}


def _load_tracker_render():
    cfg = get_config()
    script = cfg.repo_root / ".claude/skills/tracker/scripts/render.py"
    if not script.is_file():
        raise HTTPException(503, f"tracker render.py missing: {script}")
    mtime = script.stat().st_mtime
    if _TRACKER_RENDER_CACHE["mtime"] == mtime and _TRACKER_RENDER_CACHE["module"] is not None:
        return _TRACKER_RENDER_CACHE["module"]
    import importlib.util
    spec = importlib.util.spec_from_file_location("tracker_render", script)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    _TRACKER_RENDER_CACHE["mtime"] = mtime
    _TRACKER_RENDER_CACHE["module"] = mod
    return mod


@router.get("/workflows/tracker/dashboard.css")
async def tracker_dashboard_css():
    """Serve the tracker grid's base CSS for inline-rendered dashboards
    (dashboard_view.html). Single source of truth: render.py's
    `_CSS_BASE_INNER` constant."""
    from fastapi.responses import Response
    mod = _load_tracker_render()
    return Response(content=mod._CSS_BASE_INNER, media_type="text/css")


@router.get("/workflows/tracker/dashboard.js")
async def tracker_dashboard_js():
    """Serve the tracker grid's base JS for inline-rendered dashboards.
    Single source of truth: render.py's `_JS_INNER` constant."""
    from fastapi.responses import Response
    mod = _load_tracker_render()
    return Response(content=mod._JS_INNER, media_type="application/javascript")


def _tracker_embed_fragment_for_actor(cfg, actor_folder: str,
                                      theme_name: str | None = None) -> str:
    """Return the embed-mode HTML fragment for the tracker dashboard.

    Renders against the actor's worktree md if a status-session is open
    (so pending edits are visible); otherwise renders against main.

    `theme_name` is the viewer's per-browser theme selection. This path
    renders the dashboard live, so unlike the committed standalone .html it
    CAN follow a personal theme — without it the inline dashboard would stay
    on the project default while the console around it changed.
    """
    mod = _load_tracker_render()
    project_dir = cfg.repo_root
    if actor_folder:
        sess = tracker_session.snapshot(cfg.repo_root, actor_folder, "status")
        if sess is not None and Path(sess.worktree_path).is_dir():
            project_dir = Path(sess.worktree_path)
    return mod.render_embed_fragment(str(project_dir), theme_name=theme_name)


@router.get("/workflows/tracker/grounding")
async def tracker_grounding():
    """Serve the live submission-tracker.md as advisor grounding context.
    Returns the actor's worktree version when a status-session is open
    (so the advisor sees pending edits); otherwise main's. Consumed by
    the dashboard's `_assistant_drawer.html` via `grounding_source=
    "url:/workflows/tracker/grounding"`."""
    from fastapi.responses import Response
    cfg = get_config()
    actor_info = _resolve_actor(cfg.repo_root)
    actor_folder = actor_info.get("task_folder") or ""
    md_path = cfg.repo_root / tracker_session.TRACKER_MD_REL
    if actor_folder:
        sess = tracker_session.snapshot(cfg.repo_root, actor_folder, "status")
        if sess is not None:
            wt_md = Path(sess.worktree_path) / tracker_session.TRACKER_MD_REL
            if wt_md.is_file():
                md_path = wt_md
    if not md_path.is_file():
        return Response(content="", media_type="text/plain")
    return Response(
        content=md_path.read_text(encoding="utf-8"),
        media_type="text/plain",
    )


@router.get("/workflows/tracker/advisor/agents")
async def tracker_advisor_agents(request: Request):
    """Return the list of solo (non-panel, non-system) advisor agents
    available for B5. UI's persona picker calls this on page load."""
    from console.chat.domain_agents import load_all

    cfg = get_config()
    agents, _ = load_all(cfg.agents_dir)
    out = []
    for name, agent in sorted(agents.items()):
        if agent.is_panel or agent.is_system:
            continue
        out.append({
            "name": name,
            "title": agent.title,
            "description": agent.description,
        })
    return JSONResponse({"agents": out})


@router.post("/workflows/tracker/advisor/stream")
@router.post("/workflows/tracker/advisor/stream/{agent_name}")
async def tracker_advisor_stream(request: Request, agent_name: str | None = None):
    """B5 Ask-the-Advisor — stream a single advisor turn with the
    submission-tracker.md loaded as additional grounding context.

    Auto-bootstraps the tracker-advisor session+worktree on first turn.
    After the stream completes, appends the Q&A turn to the session task
    doc's `## Changelog` so Save & Close persists the transcript.

    Body: {"agent_name": "...", "history": [...], "message": "..."}.
    `agent_name` may be provided in URL (legacy `/stream/{agent_name}` for
    `workflow_tracker_advisor.html`) or in body (new shape used by the
    `_assistant_drawer.html` partial that drives the dashboard).
    """
    from console.chat.domain_agents import load_all
    from console.chat.sdk_client import stream_response
    from console.chat.sources import resolve_with_meta
    from fastapi.responses import StreamingResponse

    cfg = get_config()
    actor, actor_folder = _tracker_actor_or_error(cfg)
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(400, "Expected JSON body")
    if not agent_name:
        agent_name = (body.get("agent_name") or "").strip()
        if not agent_name:
            raise HTTPException(400, "agent_name required (URL or body)")
    history = body.get("history") or []
    message = (body.get("message") or "").strip()
    if not message:
        raise HTTPException(400, "message required")

    agents, _ = load_all(cfg.agents_dir)
    agent = agents.get(agent_name)
    if agent is None or agent.is_system or agent.is_panel:
        raise HTTPException(404, f"Advisor '{agent_name}' not found / not solo")

    # Bootstrap session (lazy on first turn).
    try:
        task_id, task_path, wt = tracker_session.resolve_or_create(
            cfg.repo_root, actor_folder, actor, "advisor"
        )
    except RuntimeError as e:
        raise HTTPException(409, f"session bootstrap failed: {e}")

    # Build the augmented system prompt: persona + agent's normal grounding
    # + the tracker md as primary tracker context (D3 — full md).
    resolved = resolve_with_meta(cfg.repo_root, agent.sources)
    tracker_md_path = wt / tracker_session.TRACKER_MD_REL
    tracker_text = ""
    if tracker_md_path.is_file():
        tracker_text = tracker_md_path.read_text(encoding="utf-8")
    elif (cfg.repo_root / tracker_session.TRACKER_MD_REL).is_file():
        tracker_text = (cfg.repo_root / tracker_session.TRACKER_MD_REL).read_text(encoding="utf-8")

    system = (
        agent.system_prompt
        + "\n\n===== GROUNDING SOURCES =====\n"
        + resolved.text
        + "\n\n===== SUBMISSION TRACKER (PRIMARY CONTEXT) =====\n"
        + "_The user is asking about the submission package tracker. The full "
        "current state of `docs/project/submissions/submission-tracker.md` "
        "follows. Cite specific row IDs (PA1, PP3, ENG7, …) when answering "
        "row-specific questions._\n\n"
        + tracker_text
    )
    user_prompt = _format_prompt(history, message) if history else message

    # Stream + capture full response for the task-doc transcript.
    captured: list[str] = []

    def _sse(event: dict) -> str:
        return f"data: {json.dumps(event)}\n\n"

    async def event_stream():
        try:
            yield _sse({"type": "session", "task_id": task_id, "kind": "advisor"})
            yield _sse({"type": "speaker", "name": agent.name, "title": agent.title})
            async for token in stream_response(
                system_prompt=system,
                user_message=user_prompt,
                model=agent.model,
            ):
                captured.append(token)
                yield _sse({"type": "token", "text": token})
            yield _sse({"type": "speaker_done", "name": agent.name})
            # Persist the Q&A turn to the session task doc Changelog.
            full_response = "".join(captured).strip()
            entry = (
                f"{tracker_writer._today()} — Advisor `{agent_name}` — "
                f"Q: {_truncate(message, 240)} — A: {_truncate(full_response, 480)} "
                f"(by {actor})"
            )
            tracker_writer.append_task_changelog(task_path, entry)
            yield _sse({"type": "persisted", "entry_chars": len(entry)})
            yield _sse({"type": "done"})
        except Exception as e:
            yield _sse({"type": "error", "message": str(e)})

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


def _format_prompt(history: list[dict], latest: str) -> str:
    if not history:
        return latest
    parts = ["<conversation>"]
    for m in history:
        role = "user" if m.get("role") == "user" else "assistant"
        content = (m.get("content") or "").strip()
        if not content:
            continue
        parts.append(f'  <turn role="{role}">{content}</turn>')
    parts.append("</conversation>\n")
    parts.append(f"Latest user message:\n{latest}")
    return "\n".join(parts)


def _truncate(s: str, n: int) -> str:
    s = s.strip().replace("\n", " ")
    return s if len(s) <= n else s[:n - 1] + "…"


def _default_commit_message(cfg, actor_folder: str, kind: str) -> str:
    """Compose a default commit message from pending-changes count."""
    sess = tracker_session.snapshot(cfg.repo_root, actor_folder, kind)
    if sess is None or kind != "status":
        return f"tracker {kind}: console workflow save"
    pending = tracker_writer.parse_pending_changes(cfg.repo_root / sess.task_path)
    return f"tracker status: {len(pending)} change(s) via console workflow"


# ── B6 Create Draft endpoints ────────────────────────────────────────────

def _build_draft_context_for_row(repo_root: Path, row_id: str) -> dict:
    """Run scripts/build-draft-context.py for a single row, return JSON.
    Falls back to a minimal stub if the script is missing or errors."""
    script = repo_root / ".claude/skills/tracker/scripts/build-draft-context.py"
    if not script.is_file():
        return {"row": {"id": row_id}, "error": "build-draft-context.py missing"}
    try:
        r = subprocess.run(
            ["python3", str(script), "--row", row_id, "--json", "--project-dir", str(repo_root)],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            timeout=30,
        )
        if r.returncode != 0:
            return {"row": {"id": row_id}, "error": (r.stderr or "").strip()}
        return json.loads(r.stdout)
    except Exception as e:
        return {"row": {"id": row_id}, "error": str(e)}


@router.post("/workflows/tracker-draft/begin")
async def draft_begin(request: Request):
    """Open (or reuse) a draft session for `row_id`. Body: {row_id}.

    Returns the seed payload the drawer needs to call pcAssistantPrefill().
    """
    cfg = get_config()
    actor, actor_folder = _tracker_actor_or_error(cfg)
    try:
        body = await request.json()
    except Exception:
        body = {}
    row_id = (body.get("row_id") or "").strip()
    if not row_id:
        raise HTTPException(400, "row_id required")
    try:
        task_id, task_path, wt = draft_session.resolve_or_create(
            cfg.repo_root, actor_folder, actor, row_id
        )
    except (RuntimeError, ValueError) as e:
        raise HTTPException(409, f"draft session bootstrap failed: {e}")
    bundle = _build_draft_context_for_row(cfg.repo_root, row_id)
    sess = draft_session.snapshot(cfg.repo_root, actor_folder, row_id)
    return JSONResponse({
        "row_id": row_id,
        "task_id": task_id,
        "task_path": str(task_path.relative_to(cfg.repo_root)),
        "worktree_path": str(wt),
        "branch": draft_session.worktree_branch(cfg.repo_root, row_id),
        "scope": f"tracker:draft:{row_id}",
        "mode": (
            "draft-pending" if (sess and sess.has_synthesis)
            else "drafting" if (sess and sess.has_outline)
            else "outline-pending"
        ),
        "context_bundle": bundle,
        "grounding_label": f"Draft seed for {row_id}",
    })


@router.get("/workflows/tracker-draft/session")
async def draft_session_snapshot(request: Request):
    """Return current state for `(actor, row_id)`. Query: ?row_id=Q4."""
    cfg = get_config()
    actor_info = _resolve_actor(cfg.repo_root)
    actor_folder = actor_info.get("task_folder") or ""
    row_id = (request.query_params.get("row_id") or "").strip()
    if not row_id:
        raise HTTPException(400, "row_id required")
    if not actor_folder:
        return JSONResponse({"session": None})
    try:
        sess = draft_session.snapshot(cfg.repo_root, actor_folder, row_id)
    except ValueError as e:
        raise HTTPException(400, str(e))
    if sess is None:
        return JSONResponse({"session": None})
    return JSONResponse({
        "session": {
            "row_id": sess.row_id,
            "task_id": sess.task_id,
            "task_path": sess.task_path,
            "worktree_path": sess.worktree_path,
            "branch": sess.branch,
            "staging_file": sess.staging_file,
            "has_outline": sess.has_outline,
            "has_synthesis": sess.has_synthesis,
            "target_path": sess.target_path,
            "mode": (
                "draft-pending" if sess.has_synthesis
                else "drafting" if sess.has_outline
                else "outline-pending"
            ),
        }
    })


@router.post("/workflows/tracker-draft/propose-outline")
async def draft_propose_outline(request: Request):
    """Persist an agent-proposed outline as the staging file's frontmatter.
    Body:
        {row_id, outline (JSON), agent_name, approved? bool}
    If `approved: true`, also stamps `agent.outline_approved_at`.
    """
    cfg = get_config()
    actor, actor_folder = _tracker_actor_or_error(cfg)
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(400, "JSON body required")
    row_id = (body.get("row_id") or "").strip()
    outline = body.get("outline") or {}
    agent_name = (body.get("agent_name") or "program-manager").strip()
    approved = bool(body.get("approved"))
    if not row_id:
        raise HTTPException(400, "row_id required")
    if not isinstance(outline, dict):
        raise HTTPException(400, "outline must be a JSON object")
    sess = draft_session.snapshot(cfg.repo_root, actor_folder, row_id)
    if sess is None:
        raise HTTPException(409, f"no open draft session for {row_id}; call /begin first")
    wt = Path(sess.worktree_path)
    branch = sess.branch
    session_task_rel = sess.task_path
    write_result = draft_writer.write_outline_stub(
        wt, row_id, outline, agent_name, actor, branch, session_task_rel,
    )
    approval_result = None
    if approved:
        approval_result = draft_writer.mark_outline_approved(wt, row_id)
        draft_session.append_changelog(
            cfg.repo_root / sess.task_path,
            f"Outline approved (agent={agent_name})",
        )
    else:
        draft_session.append_changelog(
            cfg.repo_root / sess.task_path,
            f"Outline proposed (agent={agent_name})",
        )
    return JSONResponse({
        "row_id": row_id,
        "outline": write_result,
        "approval": approval_result,
    })


@router.post("/workflows/tracker-draft/synthesize")
async def draft_synthesize(request: Request):
    """Persist a synthesized body into the staging file. Body:
        {row_id, body_md}
    The router does NOT invoke the agent here (that lives in the assistant
    chat stream); this endpoint accepts the markdown body the chat surface
    captured from the agent's synthesize-draft turn.
    """
    cfg = get_config()
    _, actor_folder = _tracker_actor_or_error(cfg)
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(400, "JSON body required")
    row_id = (body.get("row_id") or "").strip()
    body_md = body.get("body_md") or ""
    if not row_id or not body_md:
        raise HTTPException(400, "row_id and body_md required")
    sess = draft_session.snapshot(cfg.repo_root, actor_folder, row_id)
    if sess is None:
        raise HTTPException(409, f"no open draft session for {row_id}")
    wt = Path(sess.worktree_path)
    try:
        result = draft_writer.write_synthesis(wt, row_id, body_md)
    except LookupError as e:
        raise HTTPException(404, str(e))
    draft_session.append_changelog(
        cfg.repo_root / sess.task_path,
        f"Draft synthesized (citations={result['counts']['inline_citations']}, verify={result['counts']['verify_markers']})",
    )
    return JSONResponse({"row_id": row_id, "result": result})


@router.post("/workflows/tracker-draft/save")
async def draft_save(request: Request):
    """git-mv staging file to `target.path`, update tracker md, ff-merge.
    Body: {row_id, target_path? (override)}.
    """
    cfg = get_config()
    actor, actor_folder = _tracker_actor_or_error(cfg)
    try:
        body = await request.json()
    except Exception:
        body = {}
    row_id = (body.get("row_id") or "").strip()
    target_override = (body.get("target_path") or "").strip() or None
    if not row_id:
        raise HTTPException(400, "row_id required")
    sess = draft_session.snapshot(cfg.repo_root, actor_folder, row_id)
    if sess is None:
        raise HTTPException(409, f"no open draft session for {row_id}")
    wt = Path(sess.worktree_path)
    try:
        save_result = draft_writer.save_to_target(wt, row_id, target_override)
    except (LookupError, ValueError) as e:
        raise HTTPException(400, str(e))
    msg = f"draft({row_id}): {save_result['target_path']}"
    try:
        merge_result = draft_session.commit_and_merge(
            cfg.repo_root, actor_folder, actor, row_id, msg,
        )
    except RuntimeError as e:
        raise HTTPException(409, str(e))
    return JSONResponse({
        "saved": True,
        "row_id": row_id,
        "save": save_result,
        "merge": merge_result,
    })


@router.get("/workflows/tracker-draft/file")
async def draft_file(request: Request):
    """Return the staging file content (markdown) for the LEFT pane.
    Query: ?row_id=Q4. Reads from the worktree (so live edits show).
    """
    cfg = get_config()
    actor_info = _resolve_actor(cfg.repo_root)
    actor_folder = actor_info.get("task_folder") or ""
    row_id = (request.query_params.get("row_id") or "").strip()
    if not row_id or not actor_folder:
        raise HTTPException(400, "row_id required")
    sess = draft_session.snapshot(cfg.repo_root, actor_folder, row_id)
    if sess is None or not sess.staging_file:
        return JSONResponse({"content": "", "staging_file": None})
    f = Path(sess.worktree_path) / sess.staging_file
    if not f.is_file():
        return JSONResponse({"content": "", "staging_file": sess.staging_file})
    return JSONResponse({
        "content": f.read_text(encoding="utf-8"),
        "staging_file": sess.staging_file,
    })


@router.get("/workflows/tracker-draft/{row_id}", response_class=HTMLResponse)
async def draft_page(request: Request, row_id: str):
    """Two-panel draft authoring page. LEFT = live staging-file view;
    RIGHT = assistant drawer + session-mode-bar."""
    if not re.match(r"^[A-Z][A-Z0-9-]+$", row_id):
        raise HTTPException(400, f"invalid row_id {row_id!r}")
    cfg = get_config()
    return templates.TemplateResponse(
        request,
        "workflow_tracker_draft.html",
        {
            "config": cfg,
            "row_id": row_id,
            "assistant": {
                "scope": f"tracker:draft:{row_id}",
                "title": f"Draft Author — {row_id}",
                "subtitle": row_id,
                "default_agent": "program-manager",
                "allowed_agents": [],
                "grounding_label": f"DRAFT CONTEXT — {row_id}",
                "grounding_source": "",
                "open_button_id": "pc-assistant-noop",
                "placeholder": f"Walk the discovery rubric for {row_id}, propose an outline…",
                "empty_hint": "Propose an outline first; approve to create the staging file; then synthesize the body.",
            },
        },
    )


@router.post("/workflows/tracker-draft/cancel")
async def draft_cancel(request: Request):
    """Discard worktree + branch, mark task Abandoned. Body: {row_id}."""
    cfg = get_config()
    _, actor_folder = _tracker_actor_or_error(cfg)
    try:
        body = await request.json()
    except Exception:
        body = {}
    row_id = (body.get("row_id") or "").strip()
    if not row_id:
        raise HTTPException(400, "row_id required")
    try:
        result = draft_session.cancel_workflow(cfg.repo_root, actor_folder, row_id)
    except ValueError as e:
        raise HTTPException(400, str(e))
    return JSONResponse({"row_id": row_id, "result": result})
