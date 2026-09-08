---
report_sha256: f1d44c746ae27527bad3e22b868cfde99c2ed72f8cba8aaff6658cb9ab555026
data_sha256: f92274b16910f378b5a804e8469279fafa43d881334747bdaf362164d2af1649
generated_at: '2026-09-08T19:47:13+00:00'
author: AI assistant (grounded on report.md + data.json)
---
## Executive summary

More than half the PP3500 fleet — 56.7% — is running firmware at least one version behind, and 21.9% are two full versions behind [derived: v-main] [src: commercial/internal-fleet@2026-07-27]. This is a patient-safety exposure: an outdated drug-error-reduction library is not an operations metric to manage in the next planning cycle; it belongs in the risk conversation now [src: commercial/internal-fleet@2026-07-27]. The decision this data informs is whether a proactive update campaign is required and which regions to lead with. The single biggest caveat is that only one fleet snapshot exists, so currency trends over time cannot yet be assessed — that picture builds as the 7-day refresh cadence accumulates more data [derived: currency-history].

## PP3500 version posture

Of the 686 PP3500 devices in the fleet, 389 are at least one version behind and 150 are two versions behind [src: commercial/internal-fleet@2026-07-27]. The most important detail in this section is what the connectivity split does not show: connected devices are on the current version at 42.3% versus 44.2% for unconnected devices [derived: currency-by-connectivity] [src: commercial/internal-fleet@2026-07-27]. That near-identical split rules out "no network path" as the explanation and points instead to a gap in the update process itself. Separately, 198 legacy PP3000 units remain in service on the 2.9.x line [src: commercial/internal-fleet@2026-07-27], a phase-out question the report flags at the board level.

## % behind by region

No region has solved the update problem: EMEA runs the highest at 59.7% behind, NA at 56.9%, and APAC at 52.1% — all above half the installed base [src: commercial/internal-fleet@2026-07-27]. The regional spread points to differences in service infrastructure or distributor processes worth investigating, but the more consequential finding is the floor: even the best-performing region, APAC, still has a majority of devices behind [src: commercial/internal-fleet@2026-07-27]. If remediation effort must be sequenced, EMEA is the highest-impact starting point on current data.
