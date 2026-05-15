"""Workflow catalog — the 10 candidate workflows from task ben/105 ideation.

Each workflow declares its `backend_status` (live | partial | placeholder)
per the Placeholder Convention. The index page renders a readiness pill
(🟢/🟡/🔴) from this field so users know what to expect before clicking in.

Only `doc-roundtrip-batch` (B1) has a real view wired up in this dry-run;
all others route to the generic `workflow_view.html` placeholder.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Workflow:
    slug: str
    code: str                  # A1, B1, etc.
    group: str                 # Gate-Readiness | Authoring | Feedback-Driven | Daily/Periodic
    title: str
    one_liner: str
    backend_status: str        # live | partial | placeholder
    composition: list[str] = field(default_factory=list)   # bullet list of skill chain
    exists_today: str = ""     # what's already there
    gaps: str = ""             # what's stubbed/missing
    tracking_tasks: list[str] = field(default_factory=list) # task IDs that will light it up
    has_detail_view: bool = False  # True for workflows with a specialized page (just B1 today)

    @property
    def readiness_pill(self) -> str:
        return {"live": "🟢", "partial": "🟡", "placeholder": "🔴"}.get(
            self.backend_status, "❔"
        )

    @property
    def readiness_label(self) -> str:
        return {
            "live": "Ready end-to-end",
            "partial": "Partial — some placeholder zones",
            "placeholder": "UI-only — backend not wired",
        }.get(self.backend_status, "Unknown")


CATALOG: list[Workflow] = [
    # ───── A. Gate-Readiness Composites ─────
    Workflow(
        slug="dhf-gate-check",
        code="A1",
        group="Gate-Readiness",
        title="DHF Gate Check",
        one_liner="Ready/not-ready verdict for a single DHF — composes manifest gaps, trace validation, and BP audit.",
        backend_status="partial",
        composition=[
            "/dhf-manifest gap report (per DHF)",
            "/trace-matrix validate (per DHF)",
            "/best-practices audit (scoped to DHF)",
        ],
        exists_today="All three skills exist and produce structured output today.",
        gaps="Composite 'ready/not-ready' aggregation rule not defined. Tier 4 QMS coverage ~25% (task 103). Per-DHF scoping of BP checks not first-class.",
        tracking_tasks=["103", "104"],
    ),
    Workflow(
        slug="submission-preflight",
        code="A2",
        group="Gate-Readiness",
        title="Submission Pre-Flight",
        one_liner="Per-filing go/no-go — composition manifest + tracker + docflow round-trip + secops attest.",
        backend_status="partial",
        composition=[
            "Read docs/project/submissions/<filing>/composition-manifest.md",
            "/tracker build",
            "/docflow round-trip quality gates on every referenced doc",
            "/secops attest status",
        ],
        exists_today="Composition manifests exist for qsub/510k/pccp. Tracker + docflow + secops all functional individually.",
        gaps="Per-filing secops aggregate surface doesn't exist (SECOPS.md is per-user). Batch docflow check not wired as a single action.",
        tracking_tasks=[],
    ),
    Workflow(
        slug="pr-readiness",
        code="A3",
        group="Gate-Readiness",
        title="PR Readiness (pre-ultrareview)",
        one_liner="Blocking + non-blocking issue list before kicking off /ultrareview.",
        backend_status="partial",
        composition=[
            "/best-practices fix --dry-run",
            "/trace-matrix validate",
            "/docflow phase-7 validators",
            "security-assert.sh",
        ],
        exists_today="Each check runs independently today. Hooks fire at session start.",
        gaps="Unified 'pre-ultrareview' runner doesn't exist. Severity normalization (blocking vs. non-blocking) not defined.",
        tracking_tasks=[],
    ),
    # ───── B. Authoring Loops ─────
    Workflow(
        slug="doc-roundtrip-batch",
        code="B1",
        group="Authoring",
        title="Doc Round-Trip Batch",
        one_liner="Pick N markdown files → preview the /docflow export plan → (later) execute.",
        backend_status="partial",
        composition=[
            "Tree-picker across working markdown under docs/project/dhfs/**",
            "/docflow export per selected file → formal/*.docx",
            "Update tracker rows post-export",
        ],
        exists_today="/docflow export is live. Tracker rows are markdown-editable. File walker is trivial.",
        gaps="DRY-RUN ONLY in this prototype: preview shows the plan; actual export invocation deferred. Post-export tracker updates not yet wired.",
        tracking_tasks=[],
        has_detail_view=True,
    ),
    Workflow(
        slug="trace-refresh-on-save",
        code="B2",
        group="Authoring",
        title="Trace Refresh on Save",
        one_liner="Edit a requirements / UN / V&V file → one-click scoped /trace-matrix rebuild.",
        backend_status="partial",
        composition=[
            "File-change watcher over docs/project/dhfs/**/design-controls/**",
            "Path → affected-DHF inference via project.yml",
            "/trace-matrix rebuild scoped to that DHF",
        ],
        exists_today="/trace-matrix rebuild works. DHF path inference trivial.",
        gaps="File watcher + one-click trigger UI not built.",
        tracking_tasks=[],
    ),
    Workflow(
        slug="strategy-reassembly",
        code="B3",
        group="Authoring",
        title="Strategy Re-Assembly",
        one_liner="Review + promote strategy decisions per domain — Accept / Reject / Modify / Re-Assemble all live.",
        backend_status="live",
        composition=[
            "Scan docs/project/strategies/*-strategy.md",
            "Parse proposed-change callouts + History entries per doc",
            "Accept (live): promote callout body + mark older task STRATEGY REVIEWED:superseded + append ## History",
            "Reject (live): strip callout + marker + append ## History",
            "Modify (live): replace callout body in-place (proposal stays pending) + append ## History",
            "Re-Assemble (live, detection pass): scan task STRATEGY CONTENT tags, diff vs. Sources, update header + ## History",
            "Domain-aware advisor drawer with selected-doc grounding",
        ],
        exists_today="All four actions (Accept, Reject, Modify, Re-Assemble) are live end-to-end: actor resolved via resolve_user.py, requires an active task (reads .state/active-tasks-*.txt), atomic write + ## History entry. Accept also rewrites the older source task's STRATEGY CONTENT tag to `STRATEGY REVIEWED: superseded by <newer>` when the tag covers a single subsection (skips with a diagnostic when multi-subsection). Re-Assemble is a detection pass — scans every task doc for `<!-- STRATEGY CONTENT: <domain> -->` tags, diffs against the strategy doc's Sources line, updates header + History with added/removed tasks. Full-strategy markdown viewer with tabbed domain navigation, 47 hyperlinked task refs → Documents viewer, advisor drawer auto-switches per domain (regulatory→regulatory-affairs, etc.) with the selected doc as grounding.",
        gaps="Full conflict-aware content merge on Re-Assemble still requires `/strategy assemble <domain>` from Claude Code — the console Re-Assemble is detection-only (no `> **Proposed change**` callouts written automatically). Accept's source-task rewrite skips with a warning when the older tag covers multiple subsections — user still splits such tags manually.",
        tracking_tasks=["100"],
        has_detail_view=True,
    ),
    Workflow(
        slug="tracker-status-update",
        code="B4",
        group="Authoring",
        title="Tracker Status Update",
        one_liner="Click a Status badge in the submission-tracker dashboard → pick a new value → accumulate pending changes → Save & Commit writes back to submission-tracker.md, regenerates HTML, commits + pushes, closes the session task.",
        backend_status="placeholder",
        composition=[
            "Worktree-per-workflow at .worktrees/workflow-tracker-status-<date>/ (mirrors B3)",
            "Session task auto-created at tasks/<actor>/NNN-tracker-status-update-<date>.md",
            "Clickable status badges (data-row-id + data-status attributes from /tracker render)",
            "Pending-changeset sidebar (id, deliverable, old → new, optional rationale)",
            "Save & Commit: write to submission-tracker.md → /tracker render → commit on worktree branch → fast-forward main → push origin → close task",
            "Cancel: discard worktree changes (worktree + branch + task left for resume)",
        ],
        exists_today="/tracker render produces the static HTML dashboard. /tracker generate (R9) produces deterministic row inventory + sidecar overlay. B3 worktree/session machinery in b3_session.py is the canonical reference to mirror.",
        gaps="Console workflow scaffold not built (P2). Markdown writer not built (P3). Frontend overlay JS not built (P4). Render.py needs data-attributes added.",
        tracking_tasks=["154"],
        has_detail_view=False,
    ),
    Workflow(
        slug="tracker-advisor",
        code="B5",
        group="Authoring",
        title="Ask the Tracker Advisor",
        one_liner="Open chat panel from dashboard → pick advisor (regulatory/clinical/QA/etc.) → ask questions with full submission-tracker.md as system context → Save persists transcript into session task doc + commits + closes.",
        backend_status="placeholder",
        composition=[
            "Worktree-per-workflow at .worktrees/workflow-tracker-advisor-<date>/",
            "Session task auto-created at tasks/<actor>/NNN-tracker-advisor-<date>.md",
            "Reuses console/chat/ infrastructure (persona loader, streaming)",
            "Pre-loads submission-tracker.md as advisor system prompt context",
            "Save & Close: persist Q&A transcript into Decisions / Findings sections of task doc → commit + push → close task",
            "Cancel: drop conversation, close worktree, abandon task",
        ],
        exists_today="console/chat/ infrastructure exists with persona loader for advisors enabled in project.yml advisors.enabled.",
        gaps="Tracker-context loader not built (P5). 'Ask Advisor' button + chat panel UI not built (P6). Transcript-to-task-doc persistence not built.",
        tracking_tasks=["154"],
        has_detail_view=False,
    ),
    # ───── C. Feedback-Driven Work Generation ─────
    Workflow(
        slug="gap-to-task-stubs",
        code="C1",
        group="Feedback-Driven",
        title="Gap → Task Stubs",
        one_liner="DHF-manifest gap report → one-click create task stubs with owner pre-assigned.",
        backend_status="partial",
        composition=[
            "/dhf-manifest gap report",
            "DHF-owner mapping from project.yml",
            "/task create per gap with stub body",
        ],
        exists_today="/dhf-manifest gaps structured. /task create works.",
        gaps="DHF-owner field not yet modeled in project.yml team roster. Stub template for 'close this gap' not defined.",
        tracking_tasks=[],
    ),
    Workflow(
        slug="lessons-promotion-inbox",
        code="C2",
        group="Feedback-Driven",
        title="Lessons Promotion Inbox",
        one_liner="Lessons past maturity threshold queued for promotion with target surface preselected.",
        backend_status="placeholder",
        composition=[
            "/lessons ledger scan",
            "Maturity threshold filter",
            "Target-surface preselection (skill / CLAUDE.md / rule / glossary)",
            "One-click promote",
        ],
        exists_today="/lessons capture + stage exist.",
        gaps="Maturity threshold not defined in lessons schema. Target preselection logic not modeled. Promotion UX is CLI-only today.",
        tracking_tasks=["036"],
    ),
    # ───── D. Daily / Periodic ─────
    Workflow(
        slug="morning-composite",
        code="D1",
        group="Daily/Periodic",
        title="Morning Composite Card",
        one_liner="/digest briefing + cross-person tasks + SECOPS + stale-frozen-docs in one view.",
        backend_status="partial",
        composition=[
            "/digest SessionStart briefing",
            "Rollup of tasks/<each-person>/000-index.md",
            "SECOPS attestation status per person",
            "Stale frozen-docs list (change-control — scaffold today)",
        ],
        exists_today="/digest runs at SessionStart (tasks 085, 096). Per-person indexes exist.",
        gaps="Cross-person aggregation not built. Change-control freeze concept is scaffold-only.",
        tracking_tasks=[],
    ),
    Workflow(
        slug="sync-skills-review-queue",
        code="D2",
        group="Daily/Periodic",
        title="Sync-Skills Review Queue",
        one_liner="Per-skill accept/reject after sync-skills pull, not all-or-nothing.",
        backend_status="partial",
        composition=[
            "/sync-skills pull → staged diff per skill",
            "Per-skill accept/reject UI",
            "Apply accepted set",
        ],
        exists_today="/sync-skills pull works.",
        gaps="Pull is apply-only today — needs stage → review → apply re-architecture in the skill.",
        tracking_tasks=[],
    ),
]


def get_by_slug(slug: str) -> Workflow | None:
    return next((w for w in CATALOG if w.slug == slug), None)


def grouped() -> list[tuple[str, list[Workflow]]]:
    """Return [(group_name, [workflows...])] in stable group order."""
    order = ["Gate-Readiness", "Authoring", "Feedback-Driven", "Daily/Periodic"]
    by_group: dict[str, list[Workflow]] = {g: [] for g in order}
    for w in CATALOG:
        by_group.setdefault(w.group, []).append(w)
    return [(g, by_group[g]) for g in order if by_group.get(g)]
