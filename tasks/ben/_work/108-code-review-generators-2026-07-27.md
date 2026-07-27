# Code Review Dossier — Commercial Corpus Dataset Generators

_Demo project working artifact (task ben/108). Read-only review — no generator was modified; no snapshot was regenerated._

- **Date**: 2026-07-27
- **Scope**: the eleven `docs/project/corpus/commercial/*/gen.py` dataset generators (fleet, complaints, upgrade-campaign, financials, revenue-plan, sales-accounts, winloss, subscriptions, telemetry-utilization, regulatory-docket, signal-register)
- **Contract read first**: `.claude/skills/corpus/SKILL.md` (v4, 2026-07-27) — generator conventions (seeded determinism, no clocks, demo banner into raw output, staging command contract, shared-model honor system per SKILL.md L199–205); each dataset's `dataset.yml` + `README.md`
- **Method**: static review of every generator against its `dataset.yml` schema and README knob claims; byte-level extraction + hash comparison of every embedded shared block; knob claims verified against the **committed latest snapshots** (read-only — no re-generation, per brief)

## Review lens

1. Shared-model byte-identity (`make_fleet`, `site_segment`, FINANCIAL MODEL block) vs canonical copies
2. Determinism — seeded rng only, no clocks, no set/dict-order dependence
3. Schema conformance — emitted columns vs `dataset.yml` schema
4. README knob honesty — documented rates/counts/sites actually produced
5. Demo banner stamped into raw output
6. RNG-stream hygiene — separate streams so appends don't shift existing draws
7. Edge/robustness — empty categories, division in rate knobs

---

## Shared-Model Identity Matrix

Canonical copies: `make_fleet` + `REGIONS` in `internal-fleet/gen.py`; `site_segment` pair in telemetry-utilization / winloss; FINANCIAL MODEL block pair in financials / sales-accounts.

| Generator | `make_fleet` (fn body) | `REGIONS` const | `site_segment` | FINANCIAL MODEL block | Called before other draws |
|---|---|---|---|---|---|
| internal-fleet | **canonical** (md5 f4ac0fe2d1, 1302 B) | canonical | — | — | ✅ sole consumer of `Random(seed)` |
| internal-complaints | ✅ byte-identical | ✅ identical | — | — | ✅ first (`gen.py:46–47`) |
| internal-upgrade-campaign | ✅ byte-identical | ✅ identical | — | — | ✅ first (`gen.py:48–49`) |
| internal-subscriptions | ✅ byte-identical | ✅ identical | — | — | ✅ first (`gen.py:49–50`) |
| internal-telemetry-utilization | ✅ byte-identical | ✅ identical | ✅ identical (365 B) | — | ✅ first (`gen.py:55–56`) |
| internal-winloss | ✅ byte-identical | ✅ identical | ✅ identical | — | ✅ first (`gen.py:69–70`) |
| internal-sales-accounts | ✅ byte-identical | ✅ identical | ✗ not embedded — segments derived from beds/grouping (see F-SA-1) | ✅ identical except mutual cross-ref comment line (see note) | ✅ first (`gen.py:215–216`) |
| internal-financials | — (not fleet-linked; row grain is period × line × region) | — | — | **canonical** | n/a — single stream |
| internal-revenue-plan | — (no rng consumed; literal plan table) | — | — | ✗ not embedded; duplicates `REGION_SHARE` values only (see F-RP-1) | n/a |
| internal-regulatory-docket | — (records not device-linked; no device_serial column) | — | — | — | n/a |
| internal-signal-register | — (records not device-linked) | — | — | — | n/a |

**Note — FINANCIAL MODEL comment line**: the block is byte-identical between financials and sales-accounts **except** the one-line header comment, which in each file names the *other* file ("embedded identically in internal-sales-accounts/gen.py" vs "…internal-financials/gen.py"). This is the mutual-pointer convention, not drift — every constant and the `quarterly_line_revenue` function body (md5 ad66219a5d) are byte-identical. Disposition: accept.

**Note — an earlier extraction artifact**: a naive function-to-next-`def` extraction shows apparent `make_fleet` "drift" (1479/2492/1432 B variants) — that is trailing module constants (`CATEGORIES`, FINANCIAL MODEL, `WAVES`) landing between `make_fleet` and the next `def`, not function drift. Precise extraction (def through `return sites, fleet`) confirms all seven copies byte-identical.

**Cross-dataset alignment verified on snapshots** (the identity contract's observable outcome):
- subscriptions `pumps_connected` == fleet per-site connected count for **all 42 rows** (0 mismatches)
- telemetry device set == fleet connected set exactly (331 == 331, symmetric diff 0)
- upgrade-campaign target set (389 rows) == fleet PP3500 not on 3.4.0 (389) exactly

**Systemic observation (SKILL.md L199–205)**: the skill itself flags the embedded-copy convention as an honor system and recommends a shared fixture or an `asserts.command` checksum cross-check. **No dataset implements a drift-detection assert today** — this review is the detection mechanism. Filed as F-FL-1 on the canonical dataset.

---

## Per-Generator Reviews

### 1. `internal-fleet/gen.py` — VERDICT: APPROVED

Canonical shared-model owner. 54 lines. `Random(seed)` consumed exclusively by `make_fleet`; literal `last_seen` dates (2026-07-21 / 2026-06-30, no clocks); banner in raw `export.json`; emitted columns (device_serial, model, site_id, region, hw_rev, firmware_version, connected, last_seen) all declared (hw_rev added in the DA-1 schema-completion pass). Snapshot: 884 devices / 686 PP3500 / 198 PP3000 / 331 connected — matches README and the counts sales-accounts' README cites.

| ID | Sev | Finding | Disposition |
|---|---|---|---|
| F-FL-1 | low | No mechanical drift detection for the 6 downstream embedded `make_fleet` copies (+`REGIONS`) — SKILL.md L199–205 explicitly recommends a shared fixture or `asserts.command` checksum cross-check; today drift would split the world silently | fix: add an `asserts.command` that checksums the embedded block in each consumer against the canonical copy (or move to a shared fixture file) |

### 2. `internal-complaints/gen.py` — VERDICT: APPROVED-WITH-FINDINGS

Shared model identical, called first. Clean two-stream design: `rng2 = seed+1` for the 430 base records, `rng3 = seed+2` for the 5 appended rare-category rows — base draws provably undisturbed (snapshot delta 2026-07-27: +5/−0/~0). No clocks. Banner ✅. All README rare-record claims verified on snapshot 2026-07-27.2: C-2025-0431 (over-delivery, 2025-08-14, MDR yes), C-2026-0432/0433, C-2025-0434, C-2026-0435, all severity 3; C-2026-0433 ties to docket MDR-2026-0005 ✅. The intentional C-2025-0431 under-docketing seam is documented on both READMEs.

| ID | Sev | Finding | Disposition |
|---|---|---|---|
| F-CO-1 | **medium** | Schema under-declaration: CSV emits `site_id`, `model`, `firmware_version` (snapshot header confirmed) but `dataset.yml` declares neither — validation never covers them. Same defect class the DA-1 pass fixed on fleet (`hw_rev`) and upgrade-campaign (`site_id`/`hw_rev`/`wave`); complaints was missed. The README's own narrative knob (battery skew to PP3000 + older fw) rides on the undeclared columns | fix: declare `site_id`, `model`, `firmware_version` in `dataset.yml` schema (config-only; no regeneration needed, matching DA-1 precedent) |
| F-CO-2 | low | Battery-reroll `rng2.choice([x for x in fleet if x["model"] == "PP3000"])` (gen.py:57) crashes on an empty list if the 0.78 model-mix knob is ever pushed to ~1.0 | accept: population is ~198 at the locked seed; note for future knob edits |

### 3. `internal-upgrade-campaign/gen.py` — VERDICT: APPROVED-WITH-FINDINGS

Shared model identical, called first; dataset-local stream `rng3 = seed+2`. No clocks (WAVES dates, as-of 2026-07-20 literal). Banner ✅. Schema: all 13 emitted columns declared ✅ (post-DA-1). Knobs verified on snapshot: 389 targets == fleet PP3500 not-yet-3.4.0 exactly; EMEA 51% vs NA 77% completed (README "~50% vs ~77%" ✅); B+3.1.2 failure cluster 21% vs 4% baseline (README "~23% vs ~4%" — within rounding of "~", counting fail/rollback/retry statuses). Remote only where connected ✅ (method derived from `connected`).

| ID | Sev | Finding | Disposition |
|---|---|---|---|
| F-UC-1 | low | All 4 `rolled-back` rows retain a non-empty `completed_date` and positive `duration_min` (gen.py:73–74 keeps `cdate` on rollback). Status-based consumers (BQ-23/24) are correct, but a date-based completion count would over-count by 4 | accept: defensible semantics (completed, then rolled back) — but document in README, or fix by blanking `completed_date` on rollback at next refresh |

### 4. `internal-financials/gen.py` — VERDICT: APPROVED

FINANCIAL MODEL canonical owner. Deterministic trend model + ±4% per-cell `rng.uniform` noise on a single `Random(seed)` stream; no clocks (literal `as_of: 2026-07-25`). Banner ✅. Schema exact match (7 columns) ✅; 480 rows = 10 quarters × 16 line-type combos × 3 regions ✅. README knobs verified arithmetically and on snapshot: FY2025 $80.5M, subscription 7.9%, FY2026H1 $46.3M, growth rates 1.10/0.97/0.96/1.16, legacy COGS slope +1.2 pts/qtr capped 0.78. No division hazards (ASP constants non-zero). Dict iteration is insertion-ordered — deterministic.

No findings.

### 5. `internal-revenue-plan/gen.py` — VERDICT: APPROVED

Literal negotiated plan table — no rng draws (seed accepted for interface consistency and documented as unused, gen.py:74). Trivially deterministic; no clocks. Banner + `as_of` + `plan_version` in raw ✅. Schema exact match (5 columns) ✅; 120 rows = 84 FY2026 quarterly + 36 annual ✅. All README totals re-derived from the tables: 105/130/170/245/350 $M; FY2030 pccp+new-submission = 210 (inside the 180–240 band); FY2028 cloud 40-of-60 behind future regulatory events; QW quarterly weights sum to 1.00.

| ID | Sev | Finding | Disposition |
|---|---|---|---|
| F-RP-1 | low | `REGION_SHARE` (0.55/0.30/0.15) duplicates the FINANCIAL MODEL values but sits outside any marked shared block — a future region-mix change in financials/sales-accounts would silently leave the plan's regional split behind | accept: plan-vs-actuals joins are by period × line (region ALL for FY2027+); add a "keep in sync" comment at next touch |

### 6. `internal-sales-accounts/gen.py` — VERDICT: APPROVED-WITH-FINDINGS

Both shared blocks byte-identical (`make_fleet` + FINANCIAL MODEL); `make_fleet` first on `Random(seed)`, accounts on `rng2 = seed+1`. No clocks. Banner ✅. Schema exact match (9 columns) ✅. README measured claims all reproduced on snapshot: H+S reconciliation FY2024 32.5 vs 32.6, FY2025 40.7 vs 40.6, FY2026H1 25.1 vs 24.9 $M (inside ±5% contract); Meridian 38.4% of FY2025; top-3 25.5%, Northgate 11.0%; 39 accounts (33 + 6 prospects), 554 rows; 686/198/331 unit anchors. Revenue allocation `target * w / total_w` cannot divide by zero (loop only runs over non-empty `alloc`, each weight ≥ 0.7). GPO greedy check-before-add matches the "~34% weight → 35–40% revenue" comment.

| ID | Sev | Finding | Disposition |
|---|---|---|---|
| F-SA-1 | low | Segments here are beds/grouping-derived, not the shared `site_segment` hash used by telemetry/winloss — the same underlying site can carry different segments across datasets. No key-level contradiction (ACC- ids vs S- ids never join directly), but BQ-07 segment mix from this dataset is not comparable row-for-row with winloss/telemetry segments | accept: account-level vs site-level entities differ by design; worth one README sentence so BQ authors don't cross-tabulate segments across the two conventions |
| F-SA-2 | low | `NAME_STEMS[stem_i]` has no wraparound guard (56 stems, 39 consumed) — an IndexError only if site count grows ~40% | accept: headroom is ample at the locked REGIONS |

### 7. `internal-winloss/gen.py` — VERDICT: APPROVED-WITH-FINDINGS

Shared `make_fleet` + `site_segment` byte-identical; fleet burned first; `rng2 = seed+10` dataset-local. No clocks; deterministic sort key (close_date, opp_id). Banner ✅. Schema exact match (12 columns) ✅. README measured knobs reproduced exactly on 2026-07-27.2: win 45.0% (54/120); predictive-monitoring-gap in 29.8% of 47 losses; disruption group 65.6% (21/32) vs 37.5% (33/88) with denominators now named (red-team fix on record). Disruption logic correctly applies the elevated rate to the whole measurable group, not only window-drawn months (gen.py:98–104).

| ID | Sev | Finding | Disposition |
|---|---|---|---|
| F-WL-1 | **medium** | Prospect identity incoherence: `PRO-NN` ids are drawn per-opportunity (`randint(1,30)`, gen.py:85) with region/segment re-drawn independently each time, while `account_name` is cached from first encounter. Snapshot: **14 prospect accounts carry conflicting segments and 11 conflicting regions** across their rows (e.g. PRO-16), and a cached name suffix ("University Medical Center") can sit on a row whose segment says `community`. Any BQ grouping opportunities by account inherits contradictory attributes | fix: cache region/segment per PRO id exactly as names are cached (or make prospect ids unique per opportunity); needs a refresh + delta report; verify pinned editions unaffected |

### 8. `internal-subscriptions/gen.py` — VERDICT: APPROVED

Shared model identical, burned first; `rng2 = seed+20` dataset-local. No clocks (literal start dates). Banner ✅ (plus `attach_gap_sites` recorded in raw for auditability — nice). Schema exact match (7 columns) ✅. `eligible = sorted(connected)` kills dict-order dependence. Knobs verified on 2026-07-27.2: 42 rows; churned = S-NA-01/-04/-11 ✅; attach-gap = S-NA-21, S-EMEA-08, S-EMEA-13, S-APAC-08 ✅ (recomputed independently as fleet-connected minus subscribed); `pumps_connected` matches fleet for all rows; rate 430–470 (~$450) ✅; cost floor $2,800 + $150/pump per the same-day .2 re-knob documented in the changelog.

| ID | Sev | Finding | Disposition |
|---|---|---|---|
| F-SU-1 | low | `rng2.sample([s for s in eligible if connected[s] >= 3], 4)` and `sample(subscribed, 3)` raise ValueError if the pools shrink below k under future knob changes (attach probabilities, REGIONS) | accept: pools are ~40+ at the locked seed; note for knob edits |

### 9. `internal-telemetry-utilization/gen.py` — VERDICT: APPROVED

Shared `make_fleet` + `site_segment` identical; fleet burned first; `rng2 = seed+30` dataset-local. No clocks (literal months). Banner ✅ (+ `underused_sites` in raw). Schema exact match (6 columns) ✅; 1,986 rows = 331 connected × 6 months. Underused sample drawn from a `sorted()` list — deterministic. Knobs verified **exactly** on snapshot: the six README-named sites at 34.9–37.1% utilization, all <50%; all other sites span 85.7–97.0% (README claim verbatim); `expected_hours` matches the segment hash for **all 1,986 rows** (0 mismatches); underused sites all have ≥5 connected devices per the not-one-pump-noise rule.

No findings. (The `sample(…, 6)` pool-size fragility mirrors F-SU-1; same accept rationale.)

### 10. `internal-regulatory-docket/gen.py` — VERDICT: APPROVED

Not fleet-linked (no device linkage by design — no shared blocks expected). Single `Random(seed)` stream; literal `DATA_THROUGH = 2026-07-25`; no clocks. Banner ✅. Schema exact match (9 columns; `filed_date` optional, empty for the open MDR) ✅. Planted knobs verified on snapshot: exactly 2 late filings and they are **MDR-2025-0007 (+4d) / MDR-2025-0018 (+9d)** as the README names; MDR-2026-0005 is the open over-delivery MDR (opened 2026-06-29, deadline 2026-07-29) and the docket's **only** over-delivery item — the seed-42 draws happen to produce zero additional over-delivery MDRs and exactly 4 prior 2026 MDRs, so the cross-dataset id cited by internal-complaints' README/comment ("ties to MDR-2026-0005") resolves correctly. 33 records = 30 MDR + 2 corrections + 1 FSCA, 0 removals ✅. Id assignment is post-sort per-year counting — deterministic.

| ID | Sev | Finding | Disposition |
|---|---|---|---|
| F-RD-1 | low | The late-filing knob targets sorted positions 6/17 and the record ids README + the complaints tie cite (`MDR-2025-0007/0018`, `MDR-2026-0005`) are emergent from the seed-42 draw distribution, not pinned by construction. Any seed/knob/count change silently re-numbers them and breaks the cross-dataset comment + README references | accept: ids verified correct at the locked seed; if the generator is ever re-knobbed, re-verify the two READMEs and the complaints tie in the same pass |

### 11. `internal-signal-register/gen.py` — VERDICT: APPROVED-WITH-FINDINGS

Not fleet-linked. Single `Random(seed)` stream for the 38 bucketed rows; the 2 planted over-delivery rows are literal (consume no rng), so appending them cannot shift base draws — sound append hygiene. Literal `DATA_THROUGH`; no clocks. Banner ✅. Schema + enums (disposition, source) satisfied; `category` deliberately has no enum, so the planted `over-delivery` category (absent from the base CATEGORIES list) passes ✅. Knobs verified: 40 signals; 10 no-action + 6 stale-open (>90d at horizon) = 16/40 with 2 fresh opens excluded ✅; closed_date empty iff `open` for all rows ✅; SIG-2025-028→UPG-0051 (maude-screen) and SIG-2026-005→UPG-0052 (complaint-trend) exist as README states ✅.

| ID | Sev | Finding | Disposition |
|---|---|---|---|
| F-SR-1 | **medium** | Duplicate `disposition_ref`s: the ref counter (`refno = 40`, incrementing across DI/REQ/UPG buckets) emits UPG-0050..0053 for the 4 random upgrade-items, colliding with the two hand-planted literals UPG-0051/UPG-0052. Snapshot: **UPG-0051 is shared by SIG-2025-028 (over-delivery) and SIG-2026-009 (battery); UPG-0052 by SIG-2026-005 (over-delivery) and SIG-2025-017 (battery)**. README's literal claims still hold, but the over-delivery loop-closure refs are not unique to the over-delivery beat — a ref-level BQ-22 trace or the docket/complaints tie-out picks up unrelated battery signals | fix: renumber the planted refs outside the generated range (e.g. UPG-0061/0062) or start `refno` above the planted values; land via `refresh` so the delta report records it; pinned editions on 2026-07-27 stay valid |

---

## Cross-cutting summary

- **Shared-model identity: PASS everywhere it is claimed.** All 7 `make_fleet` embeds (+ `REGIONS`), both `site_segment` embeds, and the FINANCIAL MODEL pair are byte-identical (the FINANCIAL MODEL header comment line intentionally names the sibling file). Every embedding generator burns the fleet stream first, and the observable alignment holds on snapshots (subscriptions/telemetry/campaign reconcile with fleet row-for-row).
- **Determinism: PASS.** Seeded `random.Random` only; every date/month/as-of is a literal; sorts have deterministic keys; dict iteration relies only on insertion order.
- **Banner: PASS** — all 11 stamp `_Demo sample data - not for clinical use._` into raw `export.json` (normalized CSVs correctly carry no banner row, per SKILL.md).
- **Most material findings**: F-SR-1 (signal-register duplicate UPG refs — the one genuine data defect), F-CO-1 (complaints schema still under-declares 3 emitted columns — the DA-1 defect class, incompletely swept), F-WL-1 (winloss prospect accounts with contradictory segment/region across rows).
- **Systemic**: no dataset implements the SKILL.md-recommended checksum cross-check for embedded shared blocks (F-FL-1) — this review found identity intact, but nothing keeps it that way mechanically.

```json
{
  "reviews": [
    {
      "path": "corpus:commercial/internal-fleet/gen.py",
      "verdict": "APPROVED",
      "summary": "Canonical shared-model owner; deterministic, no clocks, banner stamped, schema exact; 884/686/198/331 counts verified on snapshot.",
      "findings": [
        {"severity": "low", "summary": "No mechanical drift detection for the 6 embedded make_fleet copies; SKILL.md recommends checksum assert or shared fixture", "disposition": "fix: add asserts.command checksum cross-check (or shared fixture) in consuming datasets"}
      ]
    },
    {
      "path": "corpus:commercial/internal-complaints/gen.py",
      "verdict": "APPROVED-WITH-FINDINGS",
      "summary": "make_fleet byte-identical and called first; clean seed+1/seed+2 stream split keeps base 430 draws stable; all rare-record README claims verified on snapshot.",
      "findings": [
        {"severity": "medium", "summary": "CSV emits site_id, model, firmware_version but dataset.yml does not declare them - DA-1 under-declaration class, missed here", "disposition": "fix: declare site_id, model, firmware_version in dataset.yml schema (config-only, no regeneration)"},
        {"severity": "low", "summary": "Battery-reroll PP3000 filter crashes on empty list if model-mix knob approaches 1.0", "disposition": "accept: ~198 PP3000 devices at locked seed; note for future knob edits"}
      ]
    },
    {
      "path": "corpus:commercial/internal-upgrade-campaign/gen.py",
      "verdict": "APPROVED-WITH-FINDINGS",
      "summary": "make_fleet byte-identical and first; 389 targets equal fleet PP3500 non-3.4.0 exactly; EMEA-lag and hw_rev-B/3.1.2 cluster knobs verified on snapshot.",
      "findings": [
        {"severity": "low", "summary": "All 4 rolled-back rows keep completed_date and duration_min; date-based completion counts would over-count", "disposition": "accept: status-based consumers correct; document in README or blank the date at next refresh"}
      ]
    },
    {
      "path": "corpus:commercial/internal-financials/gen.py",
      "verdict": "APPROVED",
      "summary": "FINANCIAL MODEL canonical; deterministic trend + noise on one seeded stream; schema exact; FY2025 $80.5M / 7.9% subscription / FY2026H1 $46.3M verified.",
      "findings": []
    },
    {
      "path": "corpus:commercial/internal-revenue-plan/gen.py",
      "verdict": "APPROVED",
      "summary": "Literal plan table, no rng draws (documented); all plan totals and regulatory-dependency splits re-derived and correct; schema exact, 120 rows.",
      "findings": [
        {"severity": "low", "summary": "REGION_SHARE values duplicate the FINANCIAL MODEL constants outside any marked shared block", "disposition": "accept: joins are region-insensitive; add keep-in-sync comment at next touch"}
      ]
    },
    {
      "path": "corpus:commercial/internal-sales-accounts/gen.py",
      "verdict": "APPROVED-WITH-FINDINGS",
      "summary": "Both shared blocks byte-identical; fleet burned first, accounts on seed+1; reconciliation and concentration knobs reproduced exactly on snapshot.",
      "findings": [
        {"severity": "low", "summary": "Segments are beds-derived, not the shared site_segment hash - not row-comparable with winloss/telemetry segments", "disposition": "accept: account-level vs site-level entities differ by design; add README sentence for BQ authors"},
        {"severity": "low", "summary": "NAME_STEMS indexing has no wraparound guard (56 stems, 39 used)", "disposition": "accept: ample headroom at locked REGIONS"}
      ]
    },
    {
      "path": "corpus:commercial/internal-winloss/gen.py",
      "verdict": "APPROVED-WITH-FINDINGS",
      "summary": "make_fleet + site_segment byte-identical; fleet burned first; win-rate, pm-gap, and disruption-window knobs reproduced exactly on snapshot 2026-07-27.2.",
      "findings": [
        {"severity": "medium", "summary": "PRO-NN prospect ids redrawn per opportunity: 14 accounts carry conflicting segments, 11 conflicting regions across rows", "disposition": "fix: cache region/segment per PRO id (as names are) or make prospect ids unique; land via refresh"}
      ]
    },
    {
      "path": "corpus:commercial/internal-subscriptions/gen.py",
      "verdict": "APPROVED",
      "summary": "make_fleet byte-identical, burned first; churned/attach-gap sites and per-site pumps_connected verified against fleet row-for-row on snapshot.",
      "findings": [
        {"severity": "low", "summary": "rng2.sample pools (gap 4, churn 3) raise ValueError if knob changes shrink them below k", "disposition": "accept: pools ~40+ at locked seed; note for knob edits"}
      ]
    },
    {
      "path": "corpus:commercial/internal-telemetry-utilization/gen.py",
      "verdict": "APPROVED",
      "summary": "make_fleet + site_segment byte-identical; device set equals fleet connected exactly; all six underused sites and utilization bands verified to the decimal.",
      "findings": []
    },
    {
      "path": "corpus:commercial/internal-regulatory-docket/gen.py",
      "verdict": "APPROVED",
      "summary": "Deterministic, no clocks, fixed DATA_THROUGH; exactly-2-late and open MDR-2026-0005 knobs verified, including the complaints cross-dataset id tie.",
      "findings": [
        {"severity": "low", "summary": "Knob record ids (MDR-2025-0007/0018, MDR-2026-0005) are emergent from seed-42 draws, not pinned; re-knobbing renumbers them", "disposition": "accept: verified at locked seed; re-verify README + complaints tie on any regeneration"}
      ]
    },
    {
      "path": "corpus:commercial/internal-signal-register/gen.py",
      "verdict": "APPROVED-WITH-FINDINGS",
      "summary": "Deterministic; literal planted rows consume no rng (sound append hygiene); 16/40 died-in-spreadsheet knob verified; but planted UPG refs collide with generated ones.",
      "findings": [
        {"severity": "medium", "summary": "UPG-0051/0052 each assigned to two signals: planted literals collide with counter-generated refs UPG-0050..0053", "disposition": "fix: renumber planted refs outside generated range (e.g. UPG-0061/0062) or start refno above 53; land via refresh"}
      ]
    }
  ]
}
```
