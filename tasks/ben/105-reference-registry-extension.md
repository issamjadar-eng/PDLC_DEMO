# 105 — Reference Registry Extension: 21 CFR 820 (QMSR) + Missing Standards Distillations

**ID**: 105
**Created**: 2026-07-14
**Status**: In Progress
**Created By**: Ben Xavier
**Owner**: Ben Xavier
**Priority**: High

---

## PERMANENT RULES (do not remove)

This task document is the **session-recovery point** for this work. If the current session drops, is compacted, or ends, the next session must be able to load **this file alone** and continue where we left off.

1. **Update at every meaningful checkpoint (HARD RULE).** After each meaningful unit of work, update this task doc: tick the Todo, add a dated Changelog line naming the concrete artifact, update progress counts. When you tick a Todo, fill the matching `## Economics` entry in the same edit.
2. **Phase-end batching is OK; drift-batching is not.**
3. **A commit is not a substitute.**
4. **Resume-ready before any session boundary.**
5. **Capture strategy + lessons as they happen.**
6. **Estimation provenance:** `## Economics` per `.claude/skills/usage-metrics/references/effort-estimation-rubric.md`.

Success test: a fresh session, given only this file, can re-enter the work.

## Goals

Close the registry gaps surfaced by the ben/102 reference audits (9 unverified externals across 3 risk docs) so citations in the risk file — and any future DHF doc — have a local verification path:

- Goal 1: **21 CFR Part 820 (QMSR)** imported per the regulations two-tier convention (eCFR XML `source/` + deterministic `source-md/` + distilled finding aid) + L1b applicability doc. User-supplied eCFR PDF (md5 `7cc25deb464dbc84f13c9fa1d6bb4a10`, current 7/13/2026) confirms Part 820 is now the QMSR — **§820.75 no longer exists** (ISO 13485 incorporated by reference via §820.7).
- Goal 2: Fix the pFMEA's stale `21 CFR 820.75` citations against the QMSR structure.
- Goal 3: **Standards distillations (agents)** for the missing L1a entries: IEC 60601-1, IEC 60601-1-2, IEC 60601-1-8, IEC 60601-2-24, ISO 10993 (-1/-5/-10), IEC 60812 — copyrighted, so 🔎 finding-aid convention grounded ONLY in public sources (FDA Recognized Consensus Standards DB, ISO/IEC public abstracts), everything else `[VERIFY]`-flagged. + matching L1b applicability docs under `docs/external/standards/`.
- Goal 4: Registry READMEs indexed; audits' Open Resolutions updated; push to main + registry (`references/**` is registry-shared — sister-project win).

## Todos

- [x] Fetch eCFR Part 820 XML → `source/21-cfr-part-820.xml` (21.5 KB, point-in-time 2026-07-13); deterministic python transcription → `source-md/21-cfr-part-820.md` (163 lines); fidelity: TOC + §§820.1/.3/.7 match the user PDF verbatim; §820.75 CONFIRMED ABSENT (QMSR)
- [x] Author distilled `21-cfr-part-820.md` (QMSR structure, §820.7/§820.10 IBR model, §820.35/§820.45 supplements, legacy-QSR crosswalk table with [VERIFY]s on ISO 13485 clause numbers) + regulations README (table row, Out-of-Scope amendment, changelog)
- [x] Author L1b `docs/external/regulations/qmsr-part-820.md` (applicability determination, the program citation rule for repealed QSR numbers, module mapping) + folder README row/changelog
- [x] Fix pFMEA: 2× `21 CFR 820.75` → `ISO 13485 §7.5.6 process validation (via 21 CFR 820.7 QMSR incorporation)` incl. frontmatter note + Standards Anchor; AI-CHANGELOG row; audit report E2 → stale-citation RESOLVED
- [x] Agents: 6 standards distillations (L1a) + applicability docs (L1b), all public-source-grounded with [VERIFY] discipline. Public determinations: IEC 60601-1 FDA rec 19-49 (Ed 3.2 — DHF's "3rd ed + A1" needs DoC reconciliation); IEC 60601-1-2 rec 19-36 (Ed 4.1 ONLY, partial, 2 carve-outs — DI-012 "4th ed" edition question); IEC 60601-1-8 rec 5-131 (Ed 2.2; SPL range stays licensed-copy-gated); **IEC 60601-2-24: NO current FDA recognition (verified null)** + publisher-preview front matter contradicts §201.12.1.103-as-free-flow and casts doubt on .101/.4.4.103 (Table 201.101: accuracy = .102–.107, occlusion/bolus = .4.4.104) — subclause confirmation BLOCKING for HA Rev 1.0, controlled docs NOT renumbered from preview; ISO 10993 -10/-23 irritation split (2021) pinned; IEC 60812 rec 5-120 (complete)
- [x] READMEs indexed (registry standards README +6 rows + changelog; docs/external/standards README +5 rows + 60601-1 stale-link fix 2603→67497 + changelog); all 3 audit reports' Open Resolutions updated (gaps CLOSED with the escalated E5/E6/E7 counter-evidence recorded)
- [ ] Task docs + index; push to main; `/sync-skills push` the references additions upstream

## Open Questions

- (none yet)

## Resume

### In-flight artifacts
- User PDF staged at scratchpad `part820.pdf` (source: ~/Downloads).

### First action on resume
- Activate: `bash .claude/hooks/task-activate.sh add <SESSION_ID> 105`
- Continue from the last unchecked Todo.

## Economics

_Filled at checkpoint per the effort-estimation rubric._

```json
{
  "economics": {
    "method_version": 1,
    "method_ref": ".claude/skills/usage-metrics/references/effort-estimation-rubric.md",
    "agentic_hours": {"min": 1.0, "max": 2.0},
    "todos": [
      {
        "todo": "QMSR two-tier import (eCFR XML + deterministic transcription + finding aid + L1b applicability + program citation rule) + pFMEA repair",
        "personas": ["regulatory-affairs", "quality-engineering"],
        "manual_hours": {"min": 8, "max": 16},
        "confidence": "med",
        "basis": "doc authoring 3-7 hr/pg x ~3 pg + regulatory analysis of the QSR->QMSR transition and citation-rule decision (judgment-adjacent)"
      },
      {
        "todo": "Six standards distillations + six applicability docs, each requiring FDA-recognition-database and publisher-source research",
        "personas": ["regulatory-affairs", "risk-management"],
        "manual_hours": {"min": 24, "max": 48},
        "confidence": "med",
        "basis": "doc authoring 3-7 hr/pg x ~1.5 pg x 12 files + per-standard recognition/edition research (judgment-tier adder ~1-2 hr/standard)"
      },
      {
        "todo": "README indexing + audit-report reconciliation",
        "personas": ["quality-engineering"],
        "manual_hours": {"min": 1, "max": 3},
        "confidence": "high",
        "basis": "doc maintenance, sub-page scale x 5 files"
      }
    ]
  }
}
```

## Changelog

- 2026-07-14: Task created from ben/102 reference-audit registry-gap findings + user direction (Part 820 PDF import + agent-authored standards distillations).
- 2026-07-14/15: Part 820 workstream shipped: two-tier QMSR import (XML + deterministic source-md + finding aid), L1b applicability with program citation rule, pFMEA repaired (§820.75 was repealed by the QMSR — the audit's E2 suspicion confirmed), both READMEs indexed. 6 standards agents launched (60601-1/-1-2/-1-8/-2-24, ISO 10993 series, IEC 60812).

- 2026-07-15: All 6 agents returned; 12 standards files + READMEs + audit-report reconciliation landed. Headline: IEC 60601-2-24 non-recognition + public front-matter contradiction of the cited free-flow subclause (blocking item for HA Rev 1.0 recorded, docs not renumbered from preview).
