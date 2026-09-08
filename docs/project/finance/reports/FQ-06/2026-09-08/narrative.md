---
report_sha256: 77e5ba403d1a82764588b12199cd58876e6618ec789abd7844b996384830ce2e
data_sha256: 5b98c229554ad585aa54e220c36ccff5bd06a273d6dea6caeda2ad567d08fc04
generated_at: '2026-09-08T19:00:00+00:00'
author: AI assistant (grounded on report.md + data.json)
---
## Executive summary

Working capital is stressed on two fronts as of 2026-08: company DSO is 55.2 days against a 50-day target, and $3.36M in cash is trapped — $1.77M in over-90 receivables and $1.59M in inventory above target cover [derived: v-main] [src: finance/internal-ar-inventory@2026-09-08] [config: finance.yml]. The exposure is concentrated: Northgate Purchasing Group's over-90 share stands at 32.5%, and two product lines — PP3000 at 134.1 days and IP5000 at 120.0 days of cover — account for the full inventory overhang [derived: inventory-days-by-line] [derived: over90-by-channel] [src: finance/internal-ar-inventory@2026-09-08]. This report informs three immediate decisions: a Northgate collections escalation, run-down plans for PP3000 and IP5000, and formal ratification of the three performance targets [config: finance.yml]. The key caveat is that all three targets — the 50-day DSO ceiling, the 15% over-90 threshold, and the 75-day inventory cover limit — are stand-ins with no board-adopted policy on file, so the breach verdicts are directionally clear but formally unvalidated [config: finance.yml].

## Receivables by channel

Three of the four channels perform near or below the 50-day target: direct at 49.2 days, Meridian Health Alliance at 46.5 days, and Cascadia Supply Co-op at 54.1 days [derived: dso-by-channel] [src: finance/internal-ar-inventory@2026-09-08] [config: finance.yml]. Northgate Purchasing Group is the sole outlier, with DSO of 80.0 days and over-90 receivables of $1.20M representing 32.5% of its $3.68M balance — the only channel above the 15% escalation threshold [derived: over90-by-channel] [src: finance/internal-ar-inventory@2026-09-08] [config: finance.yml]. The company-level figures — DSO 55.2 days and over-90 share 13.6% of $12.97M — mask that concentration entirely [derived: dso-stat] [src: finance/internal-ar-inventory@2026-09-08]. Any improvement in the headline DSO depends almost entirely on resolving the Northgate relationship.

## Receivables by region

All three regions carry DSO between 53.7 and 58.2 days, a narrow spread [derived: dso-by-region] [src: finance/internal-ar-inventory@2026-09-08]. North America's over-90 share at 15.8% is the only region above the 15% escalation threshold, and it is the only region where Northgate concentration would show up [src: finance/internal-ar-inventory@2026-09-08] [config: finance.yml]. The regional view adds limited diagnostic value here; APAC at 9.9% and EMEA at 11.8% are both within range [src: finance/internal-ar-inventory@2026-09-08]. Decisions should be driven by the channel cut, not the regional aggregate.

## Inventory by product line

Two lines carry excess inventory that is both large and growing: PP3000 at 134.1 days of cover holds $2.45M with $1.08M above the 75-day target, and IP5000 at 120.0 days holds $1.36M with $0.51M in excess [derived: inventory-days-by-line] [src: finance/internal-ar-inventory@2026-09-08] [config: finance.yml]. The other three lines — PP3500 at 55.9 days, SP6000 at 63.1 days, and SP6500 at 61.4 days — are all within target and show no concern [derived: inventory-days-by-line] [src: finance/internal-ar-inventory@2026-09-08]. The problem is isolated to the two older lines, which sharpens the operational response: run-down plans for PP3000 and IP5000 carry no risk of disrupting the lines that are performing well.

## Cash trapped

The $3.36M figure combines two independent problems with separate owners: $1.77M in over-90 receivables requiring a collections action and $1.59M in inventory above the 75-day cover target requiring a supply run-down [derived: cash-trapped] [src: finance/internal-ar-inventory@2026-09-08] [config: finance.yml]. Neither component resolves automatically — one requires engagement with Northgate, the other requires operational decisions on PP3000 and IP5000. Tracking the two components separately keeps accountability clear and prevents a partial win on inventory from masking a stalled AR recovery.

## Subscription receivables: not in the cube (stated, not approximated)

The working-capital cube contains the five device lines only; cloud-suite subscription billing has no AR-aging feed in the current dataset [derived: subscription-ar] [src: finance/internal-ar-inventory@2026-09-08]. This means the company DSO of 55.2 days [derived: dso-stat] [src: finance/internal-ar-inventory@2026-09-08] is a device-revenue figure, not a total-company receivables figure. Until subscription AR is added to the cube, the headline DSO understates the full receivables exposure and the $3.36M trapped-cash figure is a floor, not a ceiling [derived: cash-trapped] [src: finance/internal-ar-inventory@2026-09-08].

## Assumptions & expectations — plan vs actual

All three expectations are not met as of 2026-08, and all three carry the "unvalidated" flag — the targets have not been confirmed against a treasury, credit, or S&OP policy on file [config: finance.yml]. E-06.1 shows company DSO at 55.2 days against a 50-day ceiling [derived: dso-stat] [derived: dso-by-channel] [config: finance.yml]; E-06.2 shows Northgate Purchasing Group's over-90 share at 32.5% against a 15% threshold [derived: over90-by-channel] [config: finance.yml]; E-06.3 shows 2 of 5 lines above 75 days of cover [derived: inventory-days-by-line] [config: finance.yml]. The "unvalidated" label means the targets themselves should be challenged — but the scale of the breaches (company DSO 5.2 days over, one channel's over-90 share more than double the threshold, two lines carrying more than 45 days of excess cover) [derived: dso-stat] [derived: over90-by-channel] [derived: inventory-days-by-line] [config: finance.yml] means the operational direction of the findings is clear regardless of where the final targets land.

## Narrative — Risks / Mitigations / Issues

The two medium inventory issues and the high-severity Northgate receivables issue are all active and require named owners with deadlines. Northgate's over-90 share rose from 8.7% at 2025-01 to 32.5% at 2026-08 [derived: over90-trend] [src: finance/internal-ar-inventory@2026-09-08] — a sustained, month-on-month climb across the full history window, not a single-period spike, which narrows the plausible cause to a structural collections or contract problem rather than a timing artifact. PP3000 and IP5000 show a similarly consistent upward trend in days of cover throughout the same period [derived: inventory-days-trend] [src: finance/internal-ar-inventory@2026-09-08], reinforcing that replenishment has not been adjusted to match demand. The single medium risk — unvalidated targets — does not block action on any of the three issues, but ratifying the targets with treasury, credit, and operations is the prerequisite for marking E-06.1 through E-06.3 as formally resolved rather than directionally clear [config: finance.yml].
