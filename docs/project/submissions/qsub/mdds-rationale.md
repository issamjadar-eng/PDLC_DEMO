---
version: v0.0
status: draft
summary: Strengthener brief anchoring Q1.2 — why the Connectivity Adapter is a Non-Device MDDS and need not be separately filed.
---

# Connectivity-Adapter MDDS Rationale — PP3500 Q-Sub

_Demo sample data — not for clinical use._

> **🔒 INTERNAL.** Strengthener brief (transmission-blocking) anchoring Q1.2. Status draft-v0.0 — stub for the demo.

## 1. Position 📤

The PP3500 Connectivity Adapter is a Non-Device Medical Device Data System (MDDS): it transfers, stores, and forwards orders and infusion events without analyzing or modifying clinical data and without controlling the pump.

## 2. Code-Path Walkthrough 📤

Transfer / store / forward only — no dose computation, no alarm logic, no display of clinical decisions. `[VERIFY] against the adapter SAD.`

## 3. Software-Update & Integrity Commitments 📤

Signed updates, anti-rollback, and DICOM/HL7 integrity checks per the cybersecurity evidence carried in the 510(k) by composition.
