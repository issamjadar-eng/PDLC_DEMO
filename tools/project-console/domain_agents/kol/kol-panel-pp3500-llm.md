---
name: kol-panel-pp3500-llm
title: PP3500 KOL Panel (LLM-moderated)
description: LLM-moderated advisory panel of PP3500 KOLs — a silent moderator picks the next speaker each turn based on the conversation, instead of rotating round-robin.
kind: panel
moderator: llm
members:
  - kol-paul
  - kol-giuliano
  - kol-shah
  - kol-gorski
sources:
  - docs/project/input-analysis/predicate-analysis/portfolio/device_master_catalog.md
  - docs/project/input-analysis/predicate-analysis/portfolio/DEV-PP3500_regulatory_info.md
  - docs/project/input-analysis/predicate-analysis/portfolio/DEV-PP3000_regulatory_info.md
---

LLM-moderated variant of the PP3500 KOL panel. A silent moderator reads each user question and the conversation so far, then picks which panelist should speak next to add the most value. The panel ends when the moderator decides the question has been adequately covered, or after a hard cap of six speaker turns.

Members:

- **James E. Paul** — PCA clinical lead, acute pain management
- **Kathleen K. Giuliano** — IV smart pump usability, human factors
- **Parth Shah** — alert fatigue, medication safety
- **Lisa Gorski** — infusion nursing standards, vascular access

Use this panel when you want an organic, dynamically-routed discussion rather than a fixed rotation — for example, a focused safety question that may only need one or two perspectives.
