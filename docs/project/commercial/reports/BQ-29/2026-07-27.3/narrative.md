---
report_sha256: b12e1ce89a8d668185447fcc6300b59753e9290f9fce44386eab8c0f02cae1eb
data_sha256: ebc852eb07096abe024a6abafff0d8d723366f882f2b8837f3f2e00b508d452a
generated_at: '2026-09-08T19:51:07+00:00'
author: AI assistant (grounded on report.md + data.json)
---
## Executive summary

The Cloud Suite attach gate holds on the primary metric: 295 of 686 PP3500 pumps carry an active subscription, a 43.0% rate against the 40% stand-in threshold [derived: attach-stat] [src: commercial/internal-subscriptions@2026-07-27.2] [src: commercial/internal-fleet@2026-07-27]. But the $24M predictive-monitoring spend should not release on this reading: neither the gate number nor the denominator that produces the attach rate is ratified in the commercial strategy of record, which conditions the spend only on "traction" [config: commercial.yml] [derived: v-main]. Under a whole-PCA denominator, attach reads 33.4% against the same 40% gate — below it — so the denominator choice alone determines whether the gate holds or fails [derived: denominator-sensitivity]. The decision this report informs is the $24M release; the action it requires is a board or CFO ratification of both a numeric gate and a metric definition before the spend is triggered [derived: attach-stat] [derived: denominator-sensitivity] [config: commercial.yml].

## The gate reading

The headline reads clean: 43.0% of the PP3500 installed base is under an active Cloud Suite subscription, clearing the 40% stand-in by 3.0 points [derived: attach-stat] [src: commercial/internal-subscriptions@2026-07-27.2] [src: commercial/internal-fleet@2026-07-27]. The problem is that the 40% figure is a stand-in, not a number of record — the commercial strategy conditions the $24M spend on "Y1/Y2 Cloud Suite traction" and sets no threshold [config: commercial.yml]. Churned sites do not pad the numerator: 3 churned sites sit in the gap pool rather than in the subscribed count [src: commercial/internal-subscriptions@2026-07-27.2]. A 3.0-point margin against an unratified gate is not a green light — it is a prompt to ratify the gate [derived: attach-stat] [config: commercial.yml].

## Denominator sensitivity (disclosed, not absorbed)

The primary basis reads 43.0% (holds) while the whole-PCA basis reads 33.4% (below the 40% stand-in gate) — a swing produced entirely by whether 198 PP3000 pumps are counted in the denominator [derived: denominator-sensitivity] [src: commercial/internal-fleet@2026-07-27]. Including PP3000 is not defensible on connection grounds: 0 of those 198 PP3000 devices are connected and no adapter path exists [src: commercial/internal-fleet@2026-07-27]. The deeper issue is that the metric definition has not been ratified alongside the gate number, so both remain stand-ins [derived: denominator-sensitivity] [config: commercial.yml]. Ratifying the gate number without also ratifying the denominator definition leaves the measurement as unresolved as before.

## Where the rest of the base sits

Of 686 PP3500 pumps, 295 are subscribed, 36 are connected but unsubscribed, and 355 are not connected at all [derived: attach-breakdown] [src: commercial/internal-fleet@2026-07-27]. The 36 connected-unsubscribed pumps require no infrastructure work to convert — they are a sales motion [derived: attach-breakdown] [src: commercial/internal-fleet@2026-07-27]. The 355 unconnected pumps are a structurally different challenge: reaching them runs through a connectivity and adapter path, not through subscription sales [derived: attach-breakdown] [src: commercial/internal-fleet@2026-07-27]. These two segments need different owners and different strategies if the 43.0% rate is to grow [derived: attach-stat].

## Attach by region

NA leads at 55.5% (188 of 339 PP3500 pumps), EMEA sits at 39.3% (79 of 201), and APAC trails at 19.2% (28 of 146) [derived: attach-by-region] [src: commercial/internal-subscriptions@2026-07-27.2] [src: commercial/internal-fleet@2026-07-27]. NA's outperformance is the primary reason the global rate clears the 40% stand-in gate at 43.0% [derived: attach-by-region] [derived: attach-stat] [config: commercial.yml]. EMEA at 39.3% sits just below the gate threshold and represents the most immediate regional improvement opportunity [derived: attach-by-region]. APAC at 19.2% is the largest regional gap; the global rate's dependence on NA performance becomes more visible once regional figures are read separately [derived: attach-by-region].

## Go-get gap by site

Seven sites hold 36 connected-but-unsubscribed pumps — the entire go-get pool is reachable without new connectivity work [derived: gap-sites] [src: commercial/internal-fleet@2026-07-27]. S-NA-11 is the single largest opportunity at 17 pumps and is a churn recovery, not a first-time conversion [derived: gap-sites] [src: commercial/internal-fleet@2026-07-27]. Three of those sites are churn losses (S-NA-01, S-NA-04, S-NA-11) and the rest never subscribed, so the sales approach differs meaningfully by site history [derived: gap-sites] [src: commercial/internal-subscriptions@2026-07-27.2] [src: commercial/internal-fleet@2026-07-27]. These 36 pumps are the nearest-term lever for moving the attach rate before the gate definition is finalized [derived: gap-sites] [src: commercial/internal-fleet@2026-07-27].

## Assumptions & expectations — plan vs actual

E-29.1 records a "met" verdict at 43.0% against the 40% stand-in, but is explicitly flagged unvalidated because no ratified gate number exists in the strategy of record [derived: attach-stat] [derived: denominator-sensitivity] [config: commercial.yml]. The commercial strategy conditions the $24M on "traction" only — no threshold, no metric definition [config: commercial.yml]. Switching to the whole-PCA denominator produces a 33.4% reading that would flip E-29.1 to "not met" under the same stand-in gate [derived: denominator-sensitivity]. The path to a validated expectation requires ratifying both the numeric threshold and the denominator definition together, not one at a time.

## Narrative — Risks / Mitigations / Issues

R1 is the report's central finding: a $24M spend decision rests on a gate number nobody has ratified, and the denominator choice alone moves the reading from 43.0% (holds) to 33.4% (below gate) [derived: attach-stat] [derived: denominator-sensitivity] [config: commercial.yml]. The mitigation is explicit — board or CFO must ratify a numeric threshold AND the metric definition before the spend releases, treating them as a single governance action. W1 flags 36 connected-unsubscribed pumps across 7 sites as the near-term go-get pool, with S-NA-11's 17 pumps representing the single largest winback target [derived: gap-sites] [src: commercial/internal-subscriptions@2026-07-27.2] [src: commercial/internal-fleet@2026-07-27]. W2 points to the harder structural limit: 355 of 686 PP3500 pumps are not connected, and growing attach into that pool is a connectivity and adapter problem, not a subscription sales problem [derived: attach-breakdown] [src: commercial/internal-fleet@2026-07-27].
