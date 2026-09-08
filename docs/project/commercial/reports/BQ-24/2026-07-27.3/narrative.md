---
report_sha256: 7038e619f2579eb6edfe7a3a6de0b36b4a1fd8b26ea059a3fe0c87cd3dbd8e05
data_sha256: 057c55c43b8ffe82c569b5d97361ad61aeadf2f8459cf0b2d7ca1c59f5c779ae
generated_at: '2026-09-08T19:44:05+00:00'
author: AI assistant (grounded on report.md + data.json)
---
## Executive summary

The upgrade wave must pause for hardware revision B devices running firmware 3.1.2: 31.4% of the 35 attempted devices in that cohort failed — more than double the 15.0% trigger threshold [derived: v-main] [src: commercial/internal-upgrade-campaign@2026-07-27] [config: commercial.yml]. The failure pattern is cohort-specific: every other qualifying cohort sits well below the threshold, pointing to a hardware-revision × firmware interaction rather than a general campaign problem [derived: failure-by-cohort] [src: commercial/internal-upgrade-campaign@2026-07-27]. The decision this data requires is immediate: halt new attempts on the affected cohort, open an engineering investigation, and hold resumption until a corrected package or cohort-specific procedure is in place. The main caveat is that the 15.0% pause threshold is a demo stand-in, not yet derived from the risk file's acceptability criteria, so the trigger level itself remains unvalidated [config: commercial.yml].

## Attempt-failure rate by cohort (hw rev × from-version)

The critical signal is not the overall 9.6% per-attempt rate but the single cohort that dominates it [derived: failure-by-cohort] [src: commercial/internal-upgrade-campaign@2026-07-27]. Hardware revision B upgrading from 3.1.2 fails on 31.4% of attempted devices — a rate more than three times higher than the next-worst cohort at 9.2% [src: commercial/internal-upgrade-campaign@2026-07-27]. Hardware revision B on the later firmware (from 3.2.0) fails at just 6.3%, showing the problem is version-specific, not a hardware-revision defect across the board [src: commercial/internal-upgrade-campaign@2026-07-27]. Measuring failure against attempted devices rather than total enrolled devices matters here: the whole-cohort rate for hw B / from 3.1.2 is 21.2%, but the per-attempt rate of 31.4% is the right denominator for assessing whether the upgrade procedure itself is safe to continue [src: commercial/internal-upgrade-campaign@2026-07-27] [config: commercial.yml]. The reading would change if the 35 attempted devices in the hw B / 3.1.2 cohort are not representative of the remaining 17 unattempted — but that is a reason to investigate, not to continue the wave.

## Assumptions & expectations — plan vs actual

There is one monitored expectation and it is not met: no cohort should exceed a 15.0% per-attempt failure rate among cohorts with 20 or more attempted devices, and the hw B / from 3.1.2 cohort came in at 31.4% [derived: failure-by-cohort] [config: commercial.yml]. The more important qualifier is that expectation E-24.1 is flagged unvalidated — the 15.0% threshold is a stand-in, not grounded in the risk file's acceptability criteria [config: commercial.yml]. That means the pause trigger fired correctly given the configured rule, but the rule itself has not been formally justified; tightening or relaxing it without a risk-file basis would be unsupported.

## Narrative — Risks / Mitigations / Issues

Issue I1 is high-severity and requires immediate action: 11 of 35 attempted devices in the hw B / from 3.1.2 cohort failed, triggering the pause rule at 31.4% [derived: failure-by-cohort] [src: commercial/internal-upgrade-campaign@2026-07-27] [config: commercial.yml]. The engineering investigation should focus on the interaction between hardware revision B and the 3.1.2 → target firmware path, since the same hardware revision upgrading from 3.2.0 stays within bounds at 6.3% [src: commercial/internal-upgrade-campaign@2026-07-27]. Risk R1 sits at medium severity and is structural: until the 15.0% threshold is traced back to the risk file's acceptability criteria, the program cannot assert that resumption at a lower failure rate is formally safe — this validation step should precede any decision to restart the paused cohort [config: commercial.yml].
