# Adversarial verification + red-team — BQ-26 (refit), BQ-28, BQ-29, BQ-30 @ 2026-07-27 (ben/108)

_Personal work artifact (task-support, not a controlled deliverable). Produced by an
independent AI-assistant agent under the strict two-pass protocol: Pass 1 re-derived
every verdict/expectation/series from the pinned corpus snapshots only (`pins.json` +
`data.json`, no report.md, no bq_modules), with throwaway scripts outside the repo;
Pass 2 read the reports, plans, quality sidecars, and (for BQ-26) the prior approved
edition and the red-team dossier the refit actioned. No repo artifacts were modified._

Pins verified on disk: `internal-upgrade-campaign@2026-07-22.2` (389 rows),
`internal-fleet@2026-07-22` (884 rows), `internal-financials@2026-07-27` (480 rows),
`internal-revenue-plan@2026-07-27` (120 rows), `internal-subscriptions@2026-07-27.2`
(42 rows).

## Plain-language summary

This is an independent double-check of the four economics business answers (service
capacity, revenue vs plan, the Cloud Suite attach stage-gate, and update-cost economics).
An independent checker recomputed every published number from the raw pinned data files
alone — without reading the reports or the programs that produced them — and every figure
reproduced exactly, including the full regional capacity table, all variance percentages,
the attach rate, and the cost bounds. The check also confirmed that all four fixes agreed
in the previous round of review of the service-capacity answer were genuinely carried out,
one of them beyond what was asked. The framing challenge raised 8 new concerns: 2
moderate (the published data files do not state which statuses count as "completed", so
an independent re-check has to guess a definition; and the attach-gate answer defended its
denominator choice without showing the reading under the alternative denominator, which
moves the result across the gate) and 6 minor (wording that overstates, labels, and a
dashboard-badge risk where a pass verdict could hide the per-line breaches behind it).
All the concerns were subsequently corrected in the published answers the same day, and
each answer's quality record carries the ACTIONED entries documenting the changes.

## Terms used

- **Pins-only re-derivation** — recomputing every published number from the raw, dated
  data files alone, without reading the report or its code, so agreement is independent
  confirmation rather than circular checking.
- **Basis sensitivity** — testing whether a conclusion still holds under a defensible
  alternative definition (a different anchor date, window, or measure).
- **Denominator** — the "out of what" in any rate; the attach-gate concern here is
  exactly a denominator choice (PP3500-only vs the whole PCA fleet).
- **CONFIRMED-WITH-CAVEAT** — the numbers reproduce exactly, but the verdict depends on a
  definitional choice the reader should know about.

---

## BQ-26 — Service capacity (2026-07-27 refit) — Pass 1: **CONFIRMED** · Pass 2: **CONFIRMED-WITH-CAVEAT**

### Pass 1 — re-derivation (pins only)

Treating completed = {`completed`, `completed-after-retry`} (see friction log — this
status set is NOT stated in data.json's derivation strings), anchor = snapshot as-of
2026-07-22, close 2026-09-30 (10.0 weeks):

| Region | Remaining (reported) | On-site rem. | Current/wk | Required/wk | Last completion |
|---|---|---|---|---|---|
| APAC | 42 (42 ✓) | 38 (38 ✓) | 4.50 (4.5 ✓) | 4.20 (4.2 ✓) | 2026-07-18 |
| EMEA | 59 (59 ✓) | 34 (34 ✓) | 0.00 (0.0 ✓) | 5.90 (5.9 ✓) | 2026-06-22 ✓ (I1) |
| NA | 44 (44 ✓) | 25 (25 ✓) | 0.00 (0.0 ✓) | 4.40 (4.4 ✓) | 2026-05-11 ✓ (I2) |

- Totals: remaining 145 ✓, stalled load 103 (59+44) ✓, on-site remaining 97 ✓.
- **Uniform stall rule catches exactly the regions claimed**: 28-day window ending
  2026-07-22 has APAC 18, EMEA 0, NA 0 completions → EMEA + NA stalled, APAC not. ✓
- **Anchor sensitivity table verified against the alternative (latest-completion
  2026-07-18) anchor**: weeks-to-close 10.571; APAC current 4.50/required 3.97→4.0 ✓;
  EMEA current 0.25→0.2 ✓ / required 5.58→5.6 ✓; NA 0.00 / 4.16→4.2 ✓. Verdict
  unchanged under both anchors, as the report states. ✓
- **Remote-convertible 0/97 confirmed**: every one of the 97 on-site-remaining
  devices (scheduled + failed-pending-retry) joins to `connected == no` in the fleet
  pin; zero join misses. ✓
- **FSE-days confirmed**: mean completed on-site duration 97.60 min (n=101);
  APAC 7.73→7.7 ✓, EMEA 6.91→6.9 ✓, NA 5.08→5.1 ✓; total 19.7 ✓ (R2).
- Weekly-trend series in data.json reproduces bar-for-bar from the pin (zero-filled,
  ISO-week Monday buckets). ✓
- E-26.1 `not-met` verified (two regions below required). ✓

### Pass 2 — red-team of the refit vs the prior approved edition + dossier

Diffed against `reports/BQ-26/2026-07-22` (approved) and
`tasks/ben/_work/108-redteam-BQ-26-2026-07-22.3.md` (4 findings):

| Dossier finding | Actioned in the refit? |
|---|---|
| 1 (med) EMEA stall framed as Risk, not Issue; criterion not uniform | **Yes, fully** — uniform stall criterion stated in the report and committed in plans/BQ-26.md; EMEA and NA are both high-severity Issues (I1/I2) |
| 2 (med) Optimistic latest-completion anchor, sensitivity undisclosed | **Yes, fully** — primary anchor moved to snapshot as-of; dedicated "Anchor sensitivity (disclosed, not absorbed)" section; direction of error named ("the optimistic choice"); verdict-unchanged statement present and verified true |
| 3 (med) APAC thin margin + largest on-site load absent from verdict | **Yes, fully** — APAC in the verdict headline ("on track but thin, 38 on-site remaining") + W1 Watch tied to the configured 20% headroom guard (`thin_margin_headroom_pct`) |
| 4 (low) Remote-conversion mitigation unsized; add duration-based workload | **Yes, beyond the ask** — mitigation actually sized via the fleet connectivity join (0/97, per region) and FSE-days lower bound added per region |

The refit is a genuine strengthening of the prior approved edition (which reported
EMEA 0.2/wk current and required rates 4.0/5.6/4.2 under the optimistic anchor and
carried no stall framing at all). No finding was papered over.

Residual findings (new):

- **(med) F26-1 — data.json derivation strings under-specify the completed-status
  set.** `capacity-stat.derivation.method` says "remaining = targeted − completed"
  without stating that completed = {completed, completed-after-retry}. An independent
  re-deriver working from pins + data.json alone (this protocol's Pass 1 contract)
  first computes remaining = 162, current APAC 4.25 — a false-REFUTED hazard. The
  definition lives only in plans/BQ-26.md § Approach, which Pass 1 forbids. _Fix:_
  state the status set (and the on-site-remaining set: scheduled +
  failed-pending-retry) inside the derivation `method` strings of capacity-stat,
  required-rate, remote-convertible, and fse-days-remaining.
- **(low) F26-2 — the prior dossier's finding-4 note that the remote path carries the
  implicated failure mode (all 3 NA rollbacks were remote installs) did not carry into
  the refit's R1.** Largely moot while remote-convertible = 0, and BQ-30 R2 carries
  the retry caveat, but if adapters convert the backlog the rollback signal becomes
  relevant to the conversion lever. _Fix:_ one clause in R1's mitigation.

## BQ-28 — Revenue vs plan — Pass 1: **CONFIRMED** · Pass 2: **CONFIRMED**

### Pass 1 — re-derivation (pins only)

Closed quarters of FY2026 in the actuals pin = 2026-Q1, 2026-Q2 (H1). All recomputed
values match the pinned data.json/verdict exactly:

- **Total**: actual $46.33M vs plan $48.30M → **−4.09% → −4.1% ✓** (within ±5%).
- **By quarter**: Q1 −2.56%→−2.6 ✓; Q2 **−5.49%→−5.5 ✓ (breaches ±5% alone)** ✓.
- **By line** (variance % / $M contribution): IP5000 +24.28/+0.78 ✓, PP3000
  +16.13/+0.89 ✓, PP3500 −6.34/−1.52 ✓, SP6000 −9.07/−0.50 ✓, SP6500 −15.65/−0.65 ✓,
  cloud-suite −16.42/−0.98 ✓ — the four downside breaches (cloud-suite, SP6500,
  SP6000, PP3500) are exactly the ones flagged as I1–I4. ✓
- **By region**: APAC −3.24→−3.2 ✓, EMEA −4.51→−4.5 ✓, NA −4.09→−4.1 ✓ — no region
  breaches; the miss is line-mix, not region-mix, and the report's decomposition
  (variance-by-line + variance-contribution) shows exactly the netting. ✓
- **price-volume-split unavailable is genuine**: the plan pin has no units column
  (`period, product_line, region, revenue_usd, regulatory_dependency`) — a plan-side
  volume bridge is impossible from the pinned data. ✓
- E-28.1 `met` on the stated total-YTD basis (−4.1% inside ±5%) ✓; the `actual` string
  itself discloses "4 line(s) beyond tolerance on the downside". ✓

### Pass 2 — red-team (headline honesty)

**Does the total-basis "within tolerance" verdict hide the line breaches it claims to
surface? No.** The verdict headline leads with the composite but names all four
downside breaches, the two over-plan masks, and the Q2 standalone breach *in the same
sentence*; W1 states the masking mechanism explicitly; R1 escalates the Q2
deterioration and tells the reader not to wait for the composite to breach; R2 flags
the ±5% threshold itself as unratified. The plan (plans/BQ-28.md) pre-commits this
verdict rule (total = verdict; per-line = flagging), so `met` is rule-following, not
gamed. The ⚠️ flags are applied symmetrically to over-plan lines (+24.3%, +16.1%) —
no favorable-direction suppression.

- **(low) F28-1 — rollup-badge risk on E-28.1.** Any console surface that shows only
  the expectation verdict (`met`) drops the "4 lines beyond tolerance" context. The
  report itself is honest; the risk is downstream summarization. _Fix (optional):_ a
  qualified verdict band (e.g., `met-with-breaches`) or keep the breach count in every
  rollup rendering of E-28.1.

## BQ-29 — Attach stage-gate — Pass 1: **CONFIRMED-WITH-CAVEAT** · Pass 2: **CONFIRMED-WITH-CAVEAT**

### Pass 1 — re-derivation (pins only)

- **Gate reading**: numerator = Σ `pumps_connected` over `status=active` rows = 295;
  denominator = PP3500 devices in fleet pin = 686 → **43.00% ✓**; 295 of 686 ✓;
  +3.0 points above the 40% stand-in ✓.
- **Breakdown** 295 / 36 / 355 sums to 686 ✓; shares 43.0 / 5.2 / 51.7% ✓.
- **By region**: APAC 28/146 = 19.2% ✓, EMEA 79/201 = 39.3% ✓, NA 188/339 = 55.5% ✓.
- **Gap sites** (7, with histories) reproduce exactly: S-NA-11 17 churned, S-APAC-08 5,
  S-NA-21 4, S-EMEA-08 3, S-EMEA-13 3 never-subscribed, S-NA-04 3 churned, S-NA-01 1
  churned ✓ — 4 never-subscribed + 3 churned ✓.
- **Alternative-basis probes — the decisive test (gate sits 3.0 points from the
  reading):**

| Basis | Attach | Gate at 40% |
|---|---|---|
| PP3500 pumps, active subs (the report's basis) | 295/686 = **43.0%** | HOLDS |
| Include churned subs in numerator | 316/686 = 46.1% | holds (more favorable — report takes the conservative side) |
| Sites basis (active-sub sites / PP3500 sites) | 39/48 = 81.2% | holds |
| Connected-base attach | 295/331 = 89.1% | holds |
| **PP3500 + PP3000 (whole PCA installed base)** | 295/884 = **33.4%** | **FLIPS below 40%** |

  One reasonable alternative basis flips the gate: the whole-PCA-fleet denominator
  (commercial.yml's own BQ-02 comment says "Cloud Suite rides on the PCA installed
  base", and PP3000 is 198 PCA pumps). The report's exclusion is defensible on the
  pinned data — 0 of 198 PP3000 devices are connected and the corpus has no PP3000
  adapter path — and is disclosed with rationale in Method & provenance. But with a
  gate whose *number* is already unratified, the *metric definition* (denominator) is
  equally unratified, and the flip margin is material (43.0% vs 33.4% spans the gate).

### Pass 2 — red-team (is the caveat load-bearing or decorative?)

**Load-bearing.** The unratified-gate caveat is in the verdict headline itself ("the
$24M releases on a gate NUMBER nobody has ratified"), is the only high-severity risk
(R1, with the flip-neighborhood warning "any ratified threshold in that neighborhood
flips the verdict"), is the E-29.1 basis AND actual, and the plan commits to stating
it in both the holds and not-holds branches. This is the opposite of decorative.

- **(med) F29-1 — no denominator sensitivity shown.** The report defends the
  PP3500-only denominator qualitatively but never prints the number under the
  portfolio alternative (33.4%). For a $24M release decision sitting 3 points above a
  stand-in gate, the reader should see that the metric definition — not just the
  threshold — moves the reading across the gate. _Fix:_ one sensitivity line/series
  (analogous to BQ-26's anchor-sensitivity section): "under a whole-PCA denominator
  (884 incl. 198 unconnectable PP3000): 33.4% — below the stand-in gate; ratify the
  metric definition together with the number."
- **(low) F29-2 — "the project's only sanctioned installed-base denominator"** (report
  Method) slightly overreads the fleet dataset.yml, which sanctions the fleet registry
  as the only denominator source *for internal complaint rates (BQ-18)*. Same
  conclusion, stretched citation. _Fix:_ cite it as the project's installed-base
  registry without the "only sanctioned" borrow, or extend the dataset.yml wording.

## BQ-30 — Update economics — Pass 1: **CONFIRMED** · Pass 2: **CONFIRMED**

### Pass 1 — re-derivation (pins only)

- **Cost per update**: mean completed on-site duration 97.60 min (n=101) →
  floor = 97.60/480 × $950 = **$193.17 ✓**; ceiling $950 ✓; remote $120 (config) ✓;
  mean remote hands-on 31.55→31.6 min (n=143) ✓.
- **Envelope ratio**: 120/950 = 12.6% ✓ ↔ 120/193.17 = 62.1% ✓.
- **Adapter payback**: 380/(193.17−120) = 5.19→**5.2 ✓** (floor);
  380/(950−120) = 0.458→**0.5 ✓** (ceiling).
- **143/101 connectivity join verified independently**: completed (incl.
  after-retry) remote = 143, all 143 on `connected=yes`; on-site = 101, all 101 on
  `connected=no`; zero join misses, zero crossovers. ✓
- **Finish-current-campaign**: 97 on-site-remaining × floor = $18,737 ✓;
  × ceiling = $92,150 ✓; × ($380+$120) = $48,500 ✓.
- **Adapter-case table**: 47 sites with ≥1 non-connected PP3500 (cap 50), 355 devices
  ✓; per-site spot-checks exact (S-APAC-06: 28 × $380 = $10,640; floor $5,409;
  ceiling $26,600 ✓); totals $134,900 / $68,575–$337,250 / $42,600 remote ✓.
- **Retry caveat counts**: completed-after-retry = 10 remote + 7 on-site ✓ (R2).
- E-30.1 **at-risk** is the correct output of the plan's deterministic bound rule:
  62.1% > 25% at the floor, 12.6% ≤ 25% at the ceiling → indeterminate on the
  unmeasured travel component. ✓

### Pass 2 — red-team (envelope honesty)

**The range survives everywhere.** The verdict, the cost table, E-30.1's actual, R1,
and W1 all carry the $193–$950 bound; no sentence collapses it to a point; the
"fully-loaded" number the question asks for is explicitly published as an
`unavailable` series rather than a midpoint guess; payback is refused annualization
(no campaign-frequency figure exists); the remote figure is labeled a floor with the
retry counts quantified. R1 states plainly that the remote-first decision flips
inside the band.

- **(low) F30-1 — W1's "conversion wins only near the full-day end of the bound"
  understates conversion's case.** Within-campaign breakeven is $500/update
  (48,500/97); on-site cost exceeds $500 across ~59% of the $193–$950 band
  (950−500 = 450 of 757). Imprecise but *conservative* — it biases against the capex
  ask, and W1's real point (adapters persist across campaigns) stands. _Fix:_ "wins
  in roughly the upper half of the bound" or state the $500 breakeven.
- **(low) F30-2 — "payback … at the top non-connected accounts" (verdict) is
  account-independent.** Payback per device is the same everywhere; the top accounts
  only concentrate the capex. Harmless framing; tighten if the verdict is reused.

---

## Data audit (Pass 2)

### Schema declarations vs actual CSV columns

| Dataset | Declared vs actual | Finding |
|---|---|---|
| `internal-upgrade-campaign` | **Under-declares 3 columns**: CSV carries `site_id`, `hw_rev`, `wave` — none in `dataset.yml schema.columns` | **Confirmed** (as flagged in the tasking). Impact: `schema_valid: true` in provenance is weaker than it looks — BQ-23 (site coverage), BQ-24 (hw_rev failure cohorts) and BQ-26/30 consume columns the schema never validates; a renamed/dropped `hw_rev` or `site_id` would pass acquisition checks and silently break those computations. Fix: declare all 13 columns. |
| `internal-fleet` | **Under-declares 1 column**: CSV carries `hw_rev`, absent from schema | Same class of gap, smaller blast radius (BQ-24 joins hw_rev from campaign, not fleet). Fix: declare it. |
| `internal-financials` | 7/7 columns match | Clean |
| `internal-revenue-plan` | 5/5 columns match | Clean |
| `internal-subscriptions` | 7/7 columns match | Clean |

### README knob claims vs actual rows (all re-measured from the pinned snapshots)

- `internal-financials`: FY2025 total $80.49M (~$80.5M claimed ✓); subscription share
  7.93% (~7.9% ✓); H1 2026 $46.33M (~$46.3M ✓); 480 rows ✓.
- `internal-revenue-plan`: FY2026 quarterly plan sums $105.0M ✓ ($103M cleared + $2M
  cloud-suite letter-to-file ✓); FY2027–30 = 130/170/245/350 ✓; FY2030 cloud-suite
  pccp $140M + new-submission $70M = $210M ✓; FY2028 cloud-suite 40-of-60 behind
  future events ✓; 120 rows ✓.
- `internal-subscriptions` (README "measured on snapshot 2026-07-27.2"): 42 rows ✓;
  ARR/pump range 430.0–469.0 (claimed 430..470 ✓); 3 churned = S-NA-01/S-NA-04/S-NA-11
  ✓; 4 deliberate attach-gap sites = S-NA-21/S-EMEA-08/S-EMEA-13/S-APAC-08 ✓; all 26
  sites ≤6 pumps negative-margin ✓; all 10 sites ≥12 pumps profitable ✓; 30/42
  net-negative ✓; median cost/pump $971 small vs $343 large ✓; mean hardware discount
  5.88% (claimed 5.9% ✓).

### Cross-dataset reconciliation claims (re-verified independently)

- **Accounts vs financials (±5% contract)** — `internal-sales-accounts` README claims
  FY2024 $32.5M vs $32.6M (−0.4%), FY2025 $40.7M vs $40.6M (+0.1%), FY2026H1 $25.1M
  vs $24.9M (+0.9%). Recomputed: accounts by FY = 32.49 / 40.70 / 25.13; financials
  hardware+subscription = 32.61 / 40.64 / 24.90 → −0.4% / +0.1% / +0.9%. **All three
  figures and all three deltas reproduce exactly; the ±5% contract holds.** ✓
- **Subscriptions vs fleet (exact-match contract)** — for every one of the 42
  subscription rows (including the 3 churned), `pumps_connected` equals the fleet
  pin's `connected=yes` PP3500 count for that site: **0 mismatches**. Numerator-side
  consistency also holds: 295 active-sub pumps = connected PP3500 at active-sub
  sites; 36 connected pumps at the 7 no-active-sub sites; 331 connected total. ✓

### Quality sidecars

All four editions: lint `pass` on all 8 checks, all references resolved, no
verifications recorded yet (this dossier's filings are the first two per edition).

---

## Severity roll-up

| ID | BQ | Sev | Finding (short) |
|---|---|---|---|
| F26-1 | BQ-26 | med | derivation.method strings omit the completed-status set — false-REFUTED hazard for independent re-derivation |
| F26-2 | BQ-26 | low | remote-path rollback signal (prior finding 4) not carried into refit R1 |
| F28-1 | BQ-28 | low | E-28.1 `met` badge loses breach context in verdict-only rollups |
| F29-1 | BQ-29 | med | no denominator sensitivity shown; whole-PCA basis (33.4%) flips the unratified gate |
| F29-2 | BQ-29 | low | "only sanctioned denominator" stretches the fleet dataset.yml's complaint-rate wording |
| F30-1 | BQ-30 | low | W1 understates conversion's share of the bound (breakeven $500 ≈ 41% up the band) — conservative direction |
| F30-2 | BQ-30 | low | "payback at the top accounts" is account-independent |
| DA-1 | corpus | med | upgrade-campaign schema under-declares `site_id`/`hw_rev`/`wave` (confirmed); fleet under-declares `hw_rev` |

No finding rises to REFUTED or blocks approval; F26-1 and F29-1 are the two worth
fixing before the next edition.

## Friction log

- **Pins-only re-derivation nearly mis-fired on status semantics.** data.json's
  derivation strings say "completed" without defining the status set; the pin has 5
  statuses (`completed`, `completed-after-retry`, `failed-pending-retry`,
  `rolled-back`, `scheduled`). First pass computed remaining = 162 (vs 145) until the
  `completed-after-retry` inclusion was inferred by fitting the reported totals. The
  operational definition lives in plans/BQ-26.md, which Pass 1 forbids reading — the
  derivation strings should be self-sufficient (filed as F26-1). Same inference needed
  for on-site-remaining (= scheduled + failed-pending-retry).
- **Snapshot as-of date is implicit.** The 28-day window anchors on "the snapshot
  as-of date", but provenance.yml carries only `created_at`; the anchor is the date
  part of the snapshot id (2026-07-22 for edition `2026-07-22.2`). Worked, but an
  explicit `as_of:` field in provenance.yml would remove the inference.
- **BQ-26/27 have no bq_modules file** (`bq_modules/` jumps bq_22 → bq_28); their
  computation lives elsewhere in `computations.py`. Not needed for this protocol
  (Pass 1 is pins-only and every number reproduced), but the asymmetry cost a lookup.
- **`record-verification --help` is minimal** — verdict vocabulary had to be inferred
  from prior editions' quality.json (CONFIRMED / CONFIRMED-WITH-CAVEAT / REFUTED).
- Dataset row-count asserts (`min_rows`) and sha256 chains in provenance.yml made the
  pin-integrity portion of the audit fast — good affordance.
