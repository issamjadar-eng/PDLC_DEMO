---
report_sha256: 13edc8defd3c78e04b0d75b18b5fee24a6fb008e6196e1ef7c2305df573ed858
data_sha256: e3f6c07b02ca1a79c79c79c030a2bd275dbaf14d8aeb1c32adf874b1e889dad6
generated_at: '2026-09-08T19:44:22+00:00'
author: AI assistant (grounded on report.md + data.json)
---
## Executive summary

The upgrade campaign is generating friction at a rate that warrants action before the remaining scheduled sites attempt the update. NA leads all regions with 21.7 tickets per 100 attempted upgrades [src: commercial/internal-upgrade-campaign@2026-07-27], and 4 sites have already rolled back entirely [derived: rollback-sites] [src: commercial/internal-upgrade-campaign@2026-07-27]. Remote updates produce more tickets per 100 attempts than on-site visits — 22.3 versus 19.4 — which challenges any assumption that remote is the lower-friction path [derived: tickets-by-method] [src: commercial/internal-upgrade-campaign@2026-07-27]. The customer-side cost of the on-site portion alone is $7,272–$16,412 for completed updates [derived: v-main], but that range rests entirely on modeled hours and benchmark labor rates [assume: A-002], so the true customer burden could be materially higher or lower. The key decision this data informs is whether to pause or modify the campaign — particularly for remote-method NA sites — before the pattern compounds across the still-scheduled population.

## Tickets per 100 attempted upgrades

NA generated 21.7 tickets per 100 attempted upgrades, with EMEA close behind at 21.5; APAC was lower at 17.6 [src: commercial/internal-upgrade-campaign@2026-07-27]. The three-region spread is narrow, which suggests the friction is largely campaign-wide rather than a single-region deployment problem. The 4 rollback sites — S-EMEA-15, S-NA-13, S-NA-18, and S-NA-23 — represent the hardest failures, where sites could not hold the new version at all [derived: rollback-sites] [src: commercial/internal-upgrade-campaign@2026-07-27]. What would change this reading: evidence that rollback sites share a common device configuration or firmware baseline would point to a fixable root cause rather than a systemic upgrade-readiness gap.

## Customer cost of taking the update (stated assumption)

The $7,272–$16,412 range covers only the on-site portion of customer biomed effort across 101 completed on-site updates [assume: A-002] [derived: v-main]. Because customer labor rates and hours-per-device are not in internal systems, this entire figure is modeled rather than measured [assume: A-002]. At the low end the per-site cost is manageable; at the high end it begins to represent a meaningful unplanned cost that customers may push back on in renewal conversations. The single most important action to firm up this number is the reference-account validation flagged as the A-002 refresh trigger — until that lands, any cost conversation with a customer should treat the range as directional only.
