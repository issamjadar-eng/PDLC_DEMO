"""Metrics section — team token-usage + cost dashboard.

Generic consumer of the `usage-metrics` skill's team JSON contract
(`tools/usage-metrics/usage.json`, schema `usage-metrics/team/v1`). The nav tab
appears only when that file exists; the view renders entirely from the JSON.
The data is anonymized at the source (Member N labels) — no names here.
"""
