# 014 — Tracker Skill: Genericize (remove Intra-Op / Pre-Op remnants)

**ID**: 014
**Created**: 2026-04-14
**Status**: Complete
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: Medium

---

## Goals

The `/tracker` skill carries hard-coded assumptions from the original project it was built under (a surgical device with Intra-Op / Pre-Op module split). These leak into SKILL.md docs, the render script's category help strings, per-module help generation, and the Phase Scale legend in the HTML. For PDLC_DEMO (PP3500 PCA pump) we used PCA-specific component splits (a=pca-device, b=drug-library-manager, c=connectivity-adapter) and the Intra-Op/Pre-Op vocabulary in the output is wrong for this project and any non-surgical one going forward.

Genericize the skill so the a/b/c module suffixes carry no project-specific semantics, and the Phase Scale and help text describe phases in terms the hosting project defines — not assumed Intra-Op/Pre-Op roles.

## Scope

### Files with confirmed project-specific leakage

**`.claude/skills/tracker/SKILL.md`**
- Line 51: "Suffix indicates module (a=Intra-Op, b=Pre-Op, c=Mgmt Services)" — hard-coded module taxonomy in a generic column definition
- Line 52: "(e.g., 'SRS — Intra-Op')" — example is project-specific
- Line 55: "Intra-Op items = Filing. Pre-Op items = Filing (proto) per the Pre-Op filing strategy" — baked a project's phase rules into the Phase column definition
- Lines 72–76: Per-Module Naming Convention section hard-codes a=Intra-Op / b=Pre-Op / c=Mgmt Services, plus SW3/SW4 exception carried for "historical reasons" (reasons that belong to the donor project, not the skill)

**`.claude/skills/tracker/scripts/render.py`**
- Lines 185, 187: validator warnings assume every `a`-suffixed item has a `b`-suffixed sibling (Intra-Op/Pre-Op pairing). Wrong for PDLC_DEMO, where per-module items split a/b/c asymmetrically (cyber has c, usability only has a/b, some items are a-only).
- Lines 255, 260: auto-generated help text for per-module rows hard-codes "Pre-Op module version" and "Intra-Op module version" language
- Line 283: category 1.4 help string says "Enhanced level required because Intra-Op failure could cause serious injury" — project-specific risk justification
- Lines 663–666: Phase Scale table in the HTML legend hard-codes "Device-level, Intra-Op, Mgmt Svc submission items", "Pre-Op items", "Intra-Op + Mgmt Svc launch", "Pre-Op commercial" as the meaning of Filing / Filing (proto) / Release 1 / Release 2

### Design approach (not finalized — first pass)

1. **Module taxonomy lives in the project's tracker markdown, not the skill.** The skill should treat a/b/c/... as opaque suffixes with names the hosting project supplies. The "Two-Level Deliverable Model" section the skill's `init` scaffolds should include an editable "Module Key" table that the project fills in (e.g., for PDLC_DEMO: a=pca-device, b=drug-library-manager, c=connectivity-adapter). The renderer reads this key at parse time and injects the project's names into auto-generated help text and Phase Scale legend.
2. **Phase Scale is project-defined.** The skill ships a default vocabulary (Filing / Filing (proto) / Release 1..3) but the *meaning* of each phase is a project-specific table embedded in the tracker markdown. Renderer copies the project's Phase Scale table into the HTML legend verbatim instead of hard-coding the Intra-Op/Pre-Op story.
3. **Validator drops the a/b pairing assumption.** A warning like "has a but missing b" is only meaningful in a 2-module project. Either remove the check entirely or make it opt-in via a flag in the project's Module Key ("pairing required: yes/no").
4. **Category help strings become generic.** 1.4 Software Documentation says something like "Enhanced level required when failure could cause serious injury (IEC 62304 Class C)" instead of naming a specific op phase.
5. **SW3/SW4 historical exception is deleted.** If some project wants to use separate IDs instead of a/b suffixes, that's a choice the project documents — not a carve-out in the shared skill.

### Out of scope for this task

- Contributing the generic version upstream to the hitachi registry. That's a separate push after we validate the generic version against PDLC_DEMO and at least one other project.
- Migrating existing project trackers to the new Module Key format (PDLC_DEMO is the only consumer and will be migrated in place here).

## Todos

- [ ] Audit SKILL.md for every Intra-Op / Pre-Op / surgical-specific reference
- [ ] Audit render.py for same
- [ ] Draft Module Key format (table shape, parser contract)
- [ ] Draft project-defined Phase Scale contract (how renderer pulls it)
- [ ] Rewrite SKILL.md Column Definitions (Phase, #, Scope) to be taxonomy-agnostic
- [ ] Rewrite render.py category help strings, per-module help, Phase Scale legend
- [ ] Drop or gate the a/b pairing validator
- [ ] Delete the SW3/SW4 "historical reasons" exception
- [ ] Update PDLC_DEMO's `submission-tracker.md` to carry an explicit Module Key (a=pca-device, b=drug-library-manager, c=connectivity-adapter)
- [ ] Re-run `/tracker render` and confirm no surgical-vocabulary strings in the HTML output
- [ ] Bump skill version to 6 with changelog entry
- [ ] Follow-up: `/sync-skills push` to contribute the generic version to hitachi (new task)

## Notes

### Discovery context

Found during task 013 (tracker prerequisites) while running `/tracker build` against PDLC_DEMO for the first time. The per-module letter suffixes in the SKILL's Column Definitions section said a=Intra-Op / b=Pre-Op but we needed a=pca-device / b=drug-library-manager / c=connectivity-adapter. The skill still worked (suffixes are opaque to the renderer for the most part) but:
- The validator emitted false-positive warnings about "has a but missing b" for items that only split across a and c
- Auto-generated help rows (visible when clicking a row in the HTML) were correctly blank for items with `_help` overrides but would have said "Pre-Op module version" for others
- The Phase Scale legend at the bottom of the HTML still says "Intra-Op items" / "Pre-Op items" — visible to any reviewer opening the dashboard

The pragmatic decision for task 013 was to ship the tracker as-is (the dashboard is functional and the legend is cosmetic) and open this follow-up. The user's framing in chat: *"It's not generic. There are elements that relate to another project in which we built the skill from."*

### Related tasks

- 013 — where this was discovered
- 004, 009, 012 — prior skill-genericization / shared-output refactors (similar shape)

## Strategy

_No strategy content this session — this is a plumbing / skill-cleanup task, not a regulatory or architectural decision._

## Lessons Learned

<!-- LESSONS LEARNED: skill-portability -->

### Skills built inside one project leak that project's taxonomy

**Insight**: A skill authored against a single project's vocabulary will bake that vocabulary into its docs, examples, auto-generated help text, and validator rules — even when the author believes they kept the skill "generic." The leakage is hard to spot until the skill runs against a second project with a different module taxonomy.

**Why it matters**: The tracker skill's a/b suffix semantics (Intra-Op / Pre-Op) were documented as "both conventions are valid" in SKILL.md but in practice the validator and help generator assumed the original project's naming throughout. PDLC_DEMO ran fine because the renderer tolerates unknown suffixes, but any reviewer opening the HTML saw stale Intra-Op/Pre-Op terminology in the Phase Scale legend.

**How to apply going forward**:
- When promoting a project-local skill into a shared registry, budget for a **second-project validation pass** where you actually run it against a different project's taxonomy before calling it generic.
- Treat every hard-coded example, help string, validator message, and category description as a candidate leak site. Examples are especially insidious because they read as "illustrative" but the skill's users copy them as templates.
- Prefer **project-defined vocabulary tables** (e.g., a Module Key in the tracker markdown) over skill-defined defaults. The skill should consume vocabulary, not ship it.

## Changelog

- 2026-06-08: Closed Complete via task-doc audit — shipped — render.py is project-agnostic; zero intra-op/pre-op strings remain. Moved to Completed in 000-index.md.
- 2026-04-14: Task created — discovered during task 013 while running `/tracker build` against PDLC_DEMO for the first time.

## Economics

_Retrospective estimate (rough; from task summary). See effort-estimation-rubric.md._

```json
{
  "economics": {
    "method_version": 1,
    "retrospective": true,
    "agentic_hours": 5,
    "todos": [
      {
        "todo": "Tracker skill genericize",
        "personas": [
          "rd-lead"
        ],
        "manual_hours": {
          "min": 10,
          "max": 24
        },
        "confidence": "low",
        "basis": "genericize tracker skill (discover vocab from md)"
      }
    ]
  }
}
```
