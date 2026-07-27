# BQ-30 — Cost per update: remote vs on-site, and the remote-first case

_Demo sample data — not for clinical use._

**Verdict**: A remote update costs $120 vs an on-site update between $193 (labor-time floor) and $950 (full-day ceiling) — remote is 12.6–62.1% of on-site depending on unmeasured travel; a $380 adapter pays back in 0.5–5.2 update campaigns at the top non-connected accounts [derived: v-main] [src: commercial/internal-upgrade-campaign@2026-07-27] [src: commercial/internal-fleet@2026-07-27] [config: commercial.yml]

## Cost per completed update

_What the campaign rows carry: status, method, completed_date, duration_min, tickets — no per-attempt timestamps, no retry counts, no travel fields [src: commercial/internal-upgrade-campaign@2026-07-27]. Costing works from that; what it cannot support is bounded or marked unavailable, never guessed._

| Method | Completed | Mean hands-on min | Cost per update | Basis |
|---|---|---|---|---|
| remote [derived: cost-per-update] [src: commercial/internal-upgrade-campaign@2026-07-27] [config: commercial.yml] | 143 | 31.6 | $120 | flat session rate (floor — retry sessions uncounted) |
| on-site [derived: cost-per-update] [src: commercial/internal-upgrade-campaign@2026-07-27] [config: commercial.yml] | 101 | 97.6 | $193–$950 | labor-time floor ↔ full-day ceiling (travel unmeasured) |

- On-site floor = mean hands-on duration 97.6 min ÷ 480 min/day × $950/day; ceiling = one FSE day per visit [derived: onsite-cost-bounds] [src: commercial/internal-upgrade-campaign@2026-07-27] [config: commercial.yml]
- Method↔connectivity join check: 143 of 143 remote completions are on connected devices and 101 of 101 on-site completions are on unconnected devices [derived: method-connectivity] [src: commercial/internal-upgrade-campaign@2026-07-27] [src: commercial/internal-fleet@2026-07-27]
- Weekly completions by method are charted [derived: weekly-by-method] [src: commercial/internal-upgrade-campaign@2026-07-27]

## Remote-first business case — adapters at the top non-connected accounts

_Top 47 accounts by non-connected PP3500 count (all accounts with any, capped at 50 [config: commercial.yml]): 355 devices [derived: adapter-case] [src: commercial/internal-fleet@2026-07-27]._

| Site | Non-connected PP3500 | Adapter capex | On-site cost per campaign (floor–ceiling) |
|---|---|---|---|
| S-APAC-06 [derived: adapter-case] [src: commercial/internal-fleet@2026-07-27] [config: commercial.yml] | 28 | $10,640 | $5,409–$26,600 |
| S-APAC-02 [derived: adapter-case] [src: commercial/internal-fleet@2026-07-27] [config: commercial.yml] | 25 | $9,500 | $4,829–$23,750 |
| S-NA-17 [derived: adapter-case] [src: commercial/internal-fleet@2026-07-27] [config: commercial.yml] | 19 | $7,220 | $3,670–$18,050 |
| S-APAC-08 [derived: adapter-case] [src: commercial/internal-fleet@2026-07-27] [config: commercial.yml] | 17 | $6,460 | $3,284–$16,150 |
| S-EMEA-02 [derived: adapter-case] [src: commercial/internal-fleet@2026-07-27] [config: commercial.yml] | 17 | $6,460 | $3,284–$16,150 |
| S-APAC-05 [derived: adapter-case] [src: commercial/internal-fleet@2026-07-27] [config: commercial.yml] | 15 | $5,700 | $2,898–$14,250 |
| S-EMEA-01 [derived: adapter-case] [src: commercial/internal-fleet@2026-07-27] [config: commercial.yml] | 14 | $5,320 | $2,704–$13,300 |
| S-EMEA-06 [derived: adapter-case] [src: commercial/internal-fleet@2026-07-27] [config: commercial.yml] | 14 | $5,320 | $2,704–$13,300 |
| S-EMEA-14 [derived: adapter-case] [src: commercial/internal-fleet@2026-07-27] [config: commercial.yml] | 13 | $4,940 | $2,511–$12,350 |
| S-APAC-01 [derived: adapter-case] [src: commercial/internal-fleet@2026-07-27] [config: commercial.yml] | 12 | $4,560 | $2,318–$11,400 |
| _…total, top 47 accounts_ [derived: adapter-case] [src: commercial/internal-fleet@2026-07-27] [config: commercial.yml] | 355 | $134,900 | $68,575–$337,250 |

- Payback per device: $380 adapter ÷ (on-site − remote per-update saving) = 5.2 campaigns at the labor floor, 0.5 at the full-day ceiling [derived: adapter-payback] [config: commercial.yml]
- Once converted, each campaign over the top accounts runs $42,600 remote vs $68,575–$337,250 on-site [derived: adapter-case] [config: commercial.yml]
- No campaign-frequency figure exists in any dataset, so payback is stated per update campaign — never annualized [derived: adapter-payback]

## Assumptions & expectations — plan vs actual

_`unvalidated` means the expectation itself is a stand-in that has not been grounded
in a plan of record or the risk file — challenge the assumption, not just the actual._

| ID | Expectation | Expected | Actual | Verdict | Basis |
|---|---|---|---|---|---|
| E-30.1 | A remote update costs a fraction of an on-site visit [derived: cost-per-update] [derived: onsite-cost-bounds] [config: commercial.yml] | remote cost per completed update <= 25% of on-site | remote $120 = 62.1% of the on-site labor floor ($193) but 12.6% of the full-day ceiling ($950) — the ≤25% test depends on the unmeasured travel component | at-risk (unvalidated) | business-case stand-in; not yet validated by finance |

## Narrative — Risks / Mitigations / Issues

### Risks (potential — mitigation identified)

- **R1 (high)** — The fully-loaded on-site cost is unresolvable from campaign data — the $193–$950 bound spans 12.6% to 62.1% on the remote-vs-onsite ratio, and the adapter payback spans 0.5 to 5.2 campaigns — the remote-first decision flips inside that band [derived: onsite-cost-bounds] [derived: adapter-payback] [derived: fully-loaded-onsite]
  - _Mitigation_: Acquire FSE travel/visit data (the same roster dataset BQ-26 needs) to collapse the bound before committing adapter capex [derived: onsite-cost-bounds] [derived: adapter-payback] [derived: fully-loaded-onsite]
- **R2 (medium)** — All three cost rates are demo stand-ins, not finance-validated (FSE day $950, remote session $120, adapter $380) — and the remote figure is a floor: 10 remote and 7 on-site completions needed a retry whose extra sessions the data does not count [config: commercial.yml] [src: commercial/internal-upgrade-campaign@2026-07-27]
  - _Mitigation_: Have finance validate the rates and add per-attempt session counts to the campaign export; mark E-30.1 validated when done [config: commercial.yml] [src: commercial/internal-upgrade-campaign@2026-07-27]

### Watch

- **W1 (medium)** — Finishing the current campaign's 97 on-site-remaining devices costs $18,737–$92,150 on-site vs $48,500 to adapter-convert and run remote — within this campaign conversion breaks even where on-site cost exceeds $500/update (adapter + remote session), a point 40.5% of the way up the $193–$950 bound, so conversion wins across the upper 59.5% of it — and the adapters persist for every future campaign (BQ-26 shows zero of the on-site backlog is remote-convertible today) [derived: finish-current-campaign] [derived: onsite-cost-bounds] [src: commercial/internal-upgrade-campaign@2026-07-27] [src: commercial/internal-fleet@2026-07-27] [config: commercial.yml]

## Data gap (stated, not papered over)

- Travel and overhead per on-site visit, FSE roster/day structure, and per-attempt
  session counts are not in any corpus dataset — the true fully-loaded on-site cost is
  published as unavailable [derived: fully-loaded-onsite]; the bounds above are the
  honest envelope, and the remote figure is a floor.

## Method & provenance

- Durations, methods, statuses measured from [src: commercial/internal-upgrade-campaign@2026-07-27]; connectivity joined from [src: commercial/internal-fleet@2026-07-27] by device_serial; all rates are declared plan constants [config: commercial.yml] (demo stand-ins, not finance-validated).
