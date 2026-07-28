# Verification + red-team dossier — field-safety trio (BQ-20 / BQ-21 / BQ-22), editions 2026-07-27

_Task ben/108 — independent adversarial verification (pass 1, pins-only) and red-team (pass 2)
of the newest editions under `docs/project/commercial/reports/`. Author: verification agent
(AI assistant), 2026-07-27. Findings only — no report/plan/module/corpus files were modified._

**Method**: strict two-pass. Pass 1 re-derived every verdict/expectation/series from the pinned
snapshots only (`internal-complaints@2026-07-27.2`, `internal-signal-register@2026-07-27`,
`internal-regulatory-docket@2026-07-27`, `openfda-maude-pca-monthly@2026-07-27`) with throwaway
scripts outside the repo (session scratchpad: `verify_bq20.py`, `verify_bq21_22.py`), params from
`commercial.yml` — no report.md, no bq_modules read. Pass 2 then attacked framing, plans,
modules, and the datasets themselves.

## Plain-language summary

This is an independent double-check of the three field-safety business answers (the
franchise-killer safety watch, regulatory filing exposure, and the field-signal
closed-loop). An independent checker recomputed every published number from the raw pinned
data files alone — without reading the reports or the programs that produced them — and
then compared. Nearly every figure reproduced exactly; the one exception was a
time-to-disposition median published as 106 days where the correct value is 103.5 (a
calculation bug that picked the upper of the two middle values), and the on-time filing
rate, while exactly reproduced, turned out to be the most favorable of four defensible
ways to compute it. The framing challenge raised 10 concerns in total: 1 serious (a
regulatory-docket reference stated as fact without being grounded in this answer's pinned
data), 3 moderate (a data-lag adjustment shallower than the dataset's own warning, summary
sentences typed as fixed text rather than computed from the data, and a complaint
marked as MDR-filed with no matching record in the MDR docket — a demo-data seam the two
reports read together would expose), and the rest minor.
All the concerns — including the median correction — were subsequently corrected in the
published answers the same day, and each answer's quality record carries the ACTIONED
entries documenting the changes.

## Terms used

- **Pins-only re-derivation** — recomputing every published number from the raw, dated
  data files alone, without reading the report or its code, so agreement is independent
  confirmation rather than circular checking.
- **Basis sensitivity** — testing whether a conclusion still holds under a defensible
  alternative definition (e.g. anchoring the filing window on filed dates vs opened
  dates); the on-time rate here was checked under four bases.
- **Denominator** — the "out of what" in any rate; e.g. which filings count in the
  on-time-rate calculation.
- **CONFIRMED-WITH-CAVEAT** — the numbers reproduce exactly, but the verdict depends on a
  definitional choice (or carries a small correction) the reader should know about.

---

## BQ-20 — Franchise-killer watch (over-delivery / PCA-by-proxy)

### Pass 1 verdict: **CONFIRMED**

Every number reproduces exactly from the pins:

| Claim | Published | Recomputed | Match |
|---|---|---|---|
| over-delivery complaint records | 3 | 3 (C-2025-0431, C-2026-0432, C-2026-0433) | ✓ |
| pca-by-proxy-suspected records | 2 | 2 (C-2025-0434, C-2026-0435) | ✓ |
| MDR-filed / under-investigation | 2 / 1 | 2 (0431, 0433) / 1 (0433) | ✓ |
| watch-monthly series (18 months) | as charted | identical, incl. zero-fill span 2025-02→2026-07 | ✓ |
| watch signals → upgrade refs | 2 | SIG-2025-028→UPG-0051, SIG-2026-005→UPG-0052 | ✓ |
| MAUDE monthly series (40 months) | as charted | all 40 values identical | ✓ |
| MAUDE total, lag-trimmed window | 12,891 | 12,891 (Σ 2023-01→2026-04) | ✓ |
| record-level table fields (dates/region/model/firmware/status/MDR) | — | all 5 rows byte-checked vs CSV | ✓ |

**Alternative-basis probes:**

- **No MAUDE rate anywhere**: confirmed. `class-event-rate` series is `evidence_class:
  unavailable` with empty points; no rate, ratio, or per-device figure appears in report.md or
  data.json. The 12,891 count is never juxtaposed numerically with the internal 5.
- **Lag-trim honesty**: pinned MAUDE data runs 2023-01→2026-06 (915 daily buckets, 13,359
  events). Published series ends 2026-04; exactly the trailing 2 months (2026-05: 232,
  2026-06: 236) are trimmed. Trimming *reduces* the headline total (12,891 < 13,359) — the trim
  does not inflate anything. But see finding RT-20-2 on trim depth.
- **"Confirmed" vs "suspected"**: the complaints schema has no confirmed/dismissed field. The
  plan (plans/BQ-20.md § Approach) pre-commits "confirmed = any watch-category record not
  dismissed as unfounded... a zero-tolerance watch escalates on suspicion", and the report
  preamble restates it. Counting the under-investigation record (C-2026-0433) against E-20.1 is
  the conservative, plan-committed direction — defensible. A stricter "investigation-closed
  only" basis would still breach (≥2 closed records), so the not-met verdict is
  basis-insensitive.

### Pass 2 findings

- **RT-20-1 (HIGH) — cross-BQ docket reference is not grounded in this edition's pins.**
  Report L22 and I1 name docket item **MDR-2026-0005**, citing
  `[src: commercial/internal-complaints@2026-07-27.2]` — but the complaints schema carries no
  MDR id and no docket linkage; the id is a **hard-coded string literal** in
  `bq_modules/bq_20.py` (L106, L166–168), and `internal-regulatory-docket` is neither in BQ-20's
  `corpus_deps` nor its pins.json. The claim happens to be true against
  docket@2026-07-27 (verified), and the plan authorizes a category-level narrative join — but
  the join as *implemented* reads nothing: if the docket refreshes (MDR filed, id changes), BQ-20
  keeps asserting a stale id under a resolving-but-wrong marker. This is precisely the
  documented lesson: a correct-but-misleading basis that passes lint (marker resolves; source
  doesn't support the claim). **Not defensible as done.** Fix: add the docket to BQ-20
  `corpus_deps`, pin it, derive the open over-delivery MDR id from the pinned docket and cite it
  `[src: commercial/internal-regulatory-docket@…]`; or drop the id and say "an open over-delivery
  docket item (see BQ-21)" with no src marker on the docket fact.
- **RT-20-2 (MEDIUM) — 2-month lag trim is shallower than the dataset's own lag warning, and
  the plan's promised caveat is missing from the report.** The MAUDE README (Epistemic
  constraints) warns "apparent declines in the last **~3–6 months** are reporting lag";
  `bq_20.py` trims `LAG_TRIM_MONTHS = 2`. The plan concedes this is "a convention borrowed from
  the sibling analyses, not a measured lag model — the dataset README warns the lag can run
  longer; **the report states this**" — but the report does *not* state it: L35 presents the
  2-month trim as sufficient ("MAUDE reporting lag makes them artificially low"), implying the
  charted tail (2026-02→2026-04, inside the 3–6-month incomplete zone) is clean. A reader could
  misread the recent dip (2026-01: 169) as signal. Fix: emit the "lag may run longer than the
  trim" sentence in the report (module change), or deepen the trim to match the README.
- **RT-20-3 (LOW) — hard-coded signal ids in W1.** "SIG-2025-028 → UPG-0051, SIG-2026-005 →
  UPG-0052" are string literals in `bq_20.py` L134 while the count is computed — same latent-rot
  pattern as RT-20-1 (currently true; verified). Also L166: "the under-investigation
  over-delivery event" is rendered as `over[-1]` (newest record) — true today by coincidence of
  ordering, not selected by status.
- **Real-vs-fabricated separation: PASS (airtight).** Verdict says "on our internal log
  (demo-fabricated)"; the MAUDE section is headed "real ... (counts only)" with an explicit
  "REAL public data ... never compared numerically" bullet; series labels carry "(demo)" and
  "(REAL)"; charts are separate series; the demo banner tops the report; the plan commits
  never-blended. No sentence or chart mixes the two populations.
- **Tone vs subject: PASS.** "WATCH TRIGGERED", I1/I2 at high severity, CMO-review-this-cycle
  actions, MDR-deadline escalation — the franchise-killer register is treated as such, not as
  routine.

---

## BQ-21 — Regulatory exposure (docket, MDR timeliness)

### Pass 1 verdict: **CONFIRMED-WITH-CAVEAT**

Reproduced from `internal-regulatory-docket@2026-07-27` (33 records):

| Claim | Published | Recomputed | Match |
|---|---|---|---|
| roll-up: mdr 30 (1 open / 4 filed / 25 closed); correction 2 closed; fsca 1 open | — | identical | ✓ |
| on-time rate, trailing 12 mo (filed-date basis, window 2025-06-29→2026-06-29) | 94.7% (18 of 19) | 94.7% (18/19) | ✓ |
| late in window | MDR-2025-0018 +9d | same | ✓ |
| lifetime late | MDR-2025-0007 +4d, MDR-2025-0018 +9d | same | ✓ |
| MDR-2026-0005 days-to-deadline at pin date 2026-07-27 | 2 | 2 (deadline 2026-07-29) | ✓ |
| FSCA-2026-001 report timeliness | filed on time | filed 2026-05-20 ≤ deadline 2026-05-26 | ✓ |
| filing-trend monthly series (incl. zero months, late marks 2025-05 / 2025-10) | — | identical | ✓ |

**Alternative-basis probe — does 94.7% flatter?** Yes, mildly: it is the **highest of the four
defensible bases**, though all agree within ~2 pp and none flips any verdict:

| Basis | Rate |
|---|---|
| filed-date window, latest-event anchor (published) | **94.7%** (18/19) |
| filed-date window, pin-date anchor (2025-07-27→2026-07-27) | 93.3% (14/15) |
| opened-date window, latest-event anchor | 93.3% (14/15) |
| lifetime (all 29 filed MDRs) | 93.1% (27/29) |

Mitigating: the filed-date basis and the dual-anchor scheme are **pre-committed in
plans/BQ-21.md** (with rationale: "the rate measures filing behavior"; "urgency is about now"),
the window endpoints are printed in the report (L17), both anchors are named in Method (L69),
and both lifetime late filings are enumerated (L19, W1) — "the window narrows the rate, it does
not hide the record" is accurate. In every basis the trailing window contains exactly 1 late
filing, so E-21.1 not-met is basis-insensitive. Caveat stands because the most favorable basis
was chosen and the ~93% alternates are not shown as a sensitivity note.

**Days-to-deadline under the two anchors**: pin-date anchor → 2 days (published); latest-event
anchor (2026-06-29) → 30 days. The report's choice of the *pin-date* anchor for urgency is the
conservative/urgent one and is the plan-committed anchor for deadlines. Correct as done.

### Pass 2 findings

- **RT-21-1 (MEDIUM) — narrative facts hard-coded in the computation, not parsed from data.**
  `bq_modules/bq_21.py` embeds as string literals: I2's rollout summary "NA complete, EMEA in
  progress, APAC pending" and "(drug-library correction)" (L134–136 — the plan says rollout
  state "is parsed from the record's description"; the module never parses it), I1's "the
  over-delivery event under investigation (see BQ-20)" (L125 — emitted for *any* unfiled-urgent
  MDR, whatever its category), W1's "one predates the trailing window" and the report line
  "MDR-2025-0007 predates the trailing window" (L165, L191). All are true against this pin
  (verified against the FSCA description verbatim), but a refreshed docket would silently ship
  stale, data-looking claims. The qualitative parse is faithful **today by construction of the
  demo data, not by computation**. Fix: derive the rollout phrase from the description (or only
  quote it verbatim, as the report body already does at L29), gate the "over-delivery" phrasing
  on `r["category"]`, and compute the predates-window clause.
- **RT-21-2 (LOW) — verdict evidence-class.** `v-main` is tagged `evidence_class: measured` but
  its headline carries the derived 94.7% rate (the `ontime-rate` series is correctly tagged
  `derived`). BQ-22 tags its verdict `derived`; BQ-21 should too. Cosmetic taxonomy
  inconsistency on the audit surface.
- **Exposure framing: PASS.** The exposure list enumerates ids, never just counts; R1 concedes
  the repeat-observation pattern "even at a 94.7% rate"; R2 states the under-docketing blind
  spot. E-21.1 fails honestly (no expectation gaming).

---

## BQ-22 — Closed loop (signals → design inputs, or died in a spreadsheet)

### Pass 1 verdict: **CONFIRMED-WITH-CAVEAT**

Reproduced from `internal-signal-register@2026-07-27` (40 signals; anchor = max event date
2026-07-17; results identical under a pin-date anchor):

| Claim | Published | Recomputed | Match |
|---|---|---|---|
| died lifetime | 16/40 = 40.0% (10 no-action + 6 open>90d) | identical | ✓ |
| died trailing-12-mo cohort | 6/21 = 28.6% | identical (cohort n=21) | ✓ |
| funnel (all 6 buckets, both columns) | 4/5/4/4/2/2 vs 9/6/7/10/6/2 | identical | ✓ |
| landed | 9 trailing, 15 lifetime | identical | ✓ |
| SLA compliance | 7 within / 12 breached (incl 2 stale-open) / 2 pending → 36.8% | identical | ✓ |
| time-to-disposition buckets | 0/3/11/9/9/0 | identical (n=32) | ✓ |
| exemplar table (15 rows, refs, day counts) | — | spot-checked; identical | ✓ |
| **median time to disposition** | **106 days** | **103.5 days** | ✗ |

**Median discrepancy**: true median of the 32 disposition intervals is 103.5 (16th/17th values
101 and 106). `bq_modules/bq_22.py` L83 computes `sorted(...)[len(...)//2]` — the **upper
middle element**, not the median, for even n. Direction is anti-flattering (overstates slowness
by 2.5 days) and no verdict depends on it, but a published number labeled "Median" is wrong
under the standard definition. This is the caveat.

**Alternative-definition probes — does the chosen basis flatter?** No; it sits mid-range and is
plan-committed:

| "Died" definition | Lifetime | Cohort |
|---|---|---|
| no-action only (looser) | 25.0% | 19.0% |
| no-action + open>90d (**published**) | **40.0%** | **28.6%** |
| + monitoring counted as died (stricter) | 57.5% | 47.6% |

The plan explicitly rejects the looser basis ("counting only no-action would flatter the
process") and argues monitoring is an explicit closed decision — both defensible. The headline
leads with the *worse* number (lifetime 40.0%), not the flattering cohort 28.6%.

**SLA denominator probe — do the pending exclusions flatter?** Published 36.8% excludes the 2
recent-open (≤90d) signals from the denominator: with pending in the denominator 33.3%; with
pending counted compliant 42.9%. The exclusion is the methodologically honest choice (an
un-adjudicable signal can neither comply nor breach), the 2 excluded are counted and stated in
E-22.1's actual text, and stale-open signals are counted as breaches (the anti-flattering call).
No gaming.

### Pass 2 findings

- **RT-22-1 (LOW) — median bug** as above (`bq_22.py` L83): report L35 / I2 say 106 days; true
  103.5. Fix: `statistics.median`.
- **RT-22-2 (LOW) — hard-coded exemplar ids in W1** ("SIG-2025-028 → UPG-0051, SIG-2026-005 →
  UPG-0052" literal in `bq_22.py` L161–162 while the count is computed; report body derives the
  same pair dynamically at L216–218). Same latent-rot pattern as RT-20-3; currently true.
- **Framing: PASS.** The ref-verification gap (register refs trusted, no cross-system trace) is
  surfaced twice (R2 + exemplar-table footnote), the SLA stand-in status is R1 with a [VERIFY]
  basis, and E-22.1 fails honestly.

---

## Data audit (pass 2)

**`internal-regulatory-docket`** — README knob claims all verified against the snapshot:
exactly 2 late MDRs (+4d, +9d); on-time margins 3–12 days (recomputed min 3 / max 12, n=27);
pre-2026 MDRs closed, 2026 filed/open; 0 removals; MDR-2026-0005 opened 2026-06-29, deadline
2026-07-29; FSCA description verbatim as claimed. Schema matches the CSV; `min_rows: 30` vs 33 ✓.
The FSCA free-text encoding of rollout state is a legitimate demo seam, but see RT-21-1 — the
computation's "parse" of it is hard-coded, not parsed.

**`internal-signal-register`** — README knobs verified: 10 no-action + 6 stale-open = 16/40;
2 recent-open (2026-05/06) excluded; both over-delivery signals → UPG refs with the stated
sources (maude-screen / complaint-trend); `closed_date` empty only for `open`; closure spans
36–179 days (claimed 30–180, capped ≤2026-07-20; max event 2026-07-17) ✓. **Finding
DA-1 (LOW): `dataset.yml` description says "42 signals"; the register holds 40 (README and
snapshot agree on 40).** Schema matches the CSV; `min_rows: 40` ✓.

**`internal-complaints`** — the .2 snapshot's delta-report cleanly documents the severity
1→3 convention fix on exactly the 5 watch records (+0/−0/~5); README's rare-category knobs match
the CSV (ids, MDR flags, all severity 3; "MDR only at severity 3" holds: all 27 mdr_filed=yes
rows are severity 3). `latest` → 2026-07-27.2 ✓. **Finding DA-2 (LOW): README "Consumed by"
lists BQ-21 and BQ-22, but per `commercial.yml` neither declares `internal-complaints` in
`corpus_deps`** (BQ-21: docket only; BQ-22: register only) — stale/overbroad consumer list.

**Cross-dataset consistency** — **Finding DA-3 (MEDIUM): complaint C-2025-0431 (over-delivery,
2025-08-14, `mdr_filed: yes`) has no corresponding over-delivery MDR in the docket**, whose
stated coverage is 2025-01→2026-07 and which contains exactly one over-delivery MDR
(MDR-2026-0005, matching C-2026-0433's 2026-06-27 event). An auditor reading BQ-20 and BQ-21
together sees an MDR-filed over-delivery complaint absent from the MDR docket — unintentionally
enacting the very under-docketing blind spot BQ-21's R2 warns about. Fix: plant a 2025
over-delivery MDR row in the docket generator, or note the seam in both READMEs. (Aggregate
counts are merely loose, not contradictory: 27 complaints flagged mdr_filed vs 30 docket MDRs —
plausible given the docket's wider window and non-complaint channels.)

**`openfda-maude-pca-monthly`** — README search string, `dataset.yml` `acquisition.search`, and
the provenance URL are byte-identical (`device.device_report_product_code:MEA AND
date_received:[20230101 TO 20301231]`, `count=date_received`); the MEA-not-FRN scoping rationale
is consistent with the config (no FRN term present) and with the sibling-dataset split. First
snapshot claims (915 daily buckets; 13,359 events; 2023-01-01→2026-06-30) all recomputed ✓;
provenance sha256 chain and row_count present. Unverifiable offline (flagged, not suspicious):
the 32,392 all-time MEA count and the 41-event generic-name probe. **Lag-tail claim vs data
shape**: the README's "~3–6 months" warning is *stronger* than BQ-20's 2-month trim — see
RT-20-2; the trimmed months (232, 236) are indeed below the charted tail (~277–306), consistent
with lag.

---

## Consolidated verdicts

| BQ | Adversarial-verify (pass 1) | Red-team (pass 2) |
|---|---|---|
| BQ-20 | **CONFIRMED** — all numbers reproduce; no rate published; trim honest in direction | 1 high (unpinned hard-coded docket ref under a complaints marker), 1 medium (lag-trim shallower than dataset warning + missing promised caveat), 1 low |
| BQ-21 | **CONFIRMED-WITH-CAVEAT** — 94.7% exact under the plan-committed basis, but it is the most favorable of four defensible bases (others 92.9–94.7%); verdicts basis-insensitive | 1 medium (hard-coded narrative facts vs plan's "parsed" commitment), 1 low (verdict evidence-class) |
| BQ-22 | **CONFIRMED-WITH-CAVEAT** — all shares/funnel/SLA exact; "median 106" is wrong (true 103.5; upper-median bug) | 2 low; definitions and denominators mid-range and anti-flattering; no gaming |

Cross-cutting pattern worth a lesson: **string-literal "facts" inside deterministic computation
modules** (RT-20-1, RT-20-3, RT-21-1, RT-22-2). Everything hard-coded is true against today's
pins, so lint and re-derivation pass — but none of it is *computed*, so a refresh can silently
decouple prose from data while every marker still resolves. Suggested control: modules may
interpolate only values they read from a pin, a param, or a derivation; cross-dataset ids
require the dataset in `corpus_deps` + pins.

## Friction log

- **Pass-1 discipline worked**: pins.json + data.json + commercial.yml params were sufficient to
  re-derive every number without touching report.md or the modules; data.json's per-series
  `derivation.method` strings (anchor + basis) were the deciding disambiguator for BQ-21's
  window and BQ-22's cohort. That contract is good — keep methods that precise.
- **Anchor archaeology**: BQ-21's dual anchors (latest-event for windows, pin date for urgency)
  are only discoverable pass-1 from the derivation text; a `params`-style echo of resolved
  anchors in data.json (e.g. `anchors: {event: 2026-06-29, urgency: 2026-07-27}`) would make
  adversarial recomputation one step instead of an inference.
- **`record-verification --help`** was clear; free-form verdict string; no edition-listing
  subcommand needed since editions are single per BQ here.
- **Scratchpad vs /tmp**: task brief said /tmp; the environment mandates the session scratchpad —
  used the scratchpad (outside the repo, same isolation intent).
- **Minor tooling quirks**: zsh ate a `<(sort ...)` process substitution in one compound command
  (worked around); `Bash` cwd resets between calls required absolute paths throughout.
- **Docs quality**: corpus README "Deterministic knobs" sections made the data audit fast and
  falsifiable — every knob was checkable and checked. The complaints delta-report for the .2
  severity fix is exactly the audit trail one wants.
