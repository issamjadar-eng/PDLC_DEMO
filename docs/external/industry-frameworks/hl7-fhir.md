# HL7 FHIR — Fast Healthcare Interoperability Resources

**Framework**: HL7 FHIR R4 (v4.0.1, normative) / R5 (v5.0.0)
**Source**: Health Level Seven International (HL7)
**Referenced In**: Healthcare interoperability; ONC Cures Act requirements; increasingly expected by FDA for connected devices

## Overview

FHIR is the modern standard for exchanging healthcare data via RESTful APIs. It uses a resource-based model where clinical concepts (Patient, Observation, Procedure, DiagnosticReport, etc.) are represented as discrete, addressable resources that can be created, read, updated, and searched via HTTP.

## Key FHIR Resources

### Patient and Demographics

| Resource | Description |
|----------|-------------|
| **Patient** | Patient demographics, identifiers |
| **Practitioner** | Clinician information |
| **Organization** | Hospital/facility information |
| **Encounter** | Patient visit/episode of care |

### Clinical — Pre-Operative

| Resource | Description |
|----------|-------------|
| **ImagingStudy** | Reference to DICOM imaging studies |
| **Condition** | Diagnosis (e.g., osteoarthritis, fracture) |
| **Procedure** | Planned surgical procedure |
| **ServiceRequest** | Order for surgery |
| **DiagnosticReport** | Imaging reports, pre-op assessments |

### Clinical — Intra-Operative

| Resource | Description |
|----------|-------------|
| **Procedure** | Performed procedure record |
| **Device** | Medical device used (implant details) |
| **Observation** | Intra-operative measurements |

### Clinical — Post-Operative

| Resource | Description |
|----------|-------------|
| **Observation** | Clinical measurements over time (range of motion, pain scores, functional scores) |
| **QuestionnaireResponse** | Patient-reported outcomes |
| **CarePlan** | Recovery plan |
| **CommunicationRequest** | Patient communication (reminders, alerts) |
| **DetectedIssue** | Flagged clinical concerns |
| **Goal** | Recovery targets |

### Administrative

| Resource | Description |
|----------|-------------|
| **Bundle** | Collection of resources for batch operations |
| **Subscription** | Event notifications when patient data changes |
| **AuditEvent** | Security audit trail |

## FHIR Operations

### RESTful API Basics

| Operation | HTTP Method | Description | Example |
|-----------|------------|-------------|---------|
| Read | GET | Retrieve a resource | `GET /Patient/123` |
| Search | GET | Find resources by criteria | `GET /ImagingStudy?patient=123&modality=CT` |
| Create | POST | Create a new resource | `POST /DiagnosticReport` |
| Update | PUT | Update a resource | `PUT /Observation/456` |
| Batch/Transaction | POST | Multiple operations at once | `POST /` with Bundle |

## SMART on FHIR

SMART (Substitutable Medical Applications, Reusable Technologies) on FHIR provides:
- **OAuth 2.0-based authorization** for FHIR API access
- **Launch framework** — applications can be launched from within the EHR context
- **Scopes** — fine-grained permission control (e.g., `patient/Observation.read`)

SMART on FHIR enables:
- Single sign-on from the EHR
- Context-aware launch (patient already selected)
- Scoped data access (only what the application needs)

## US Core Implementation Guide

For US-based deployments, the **US Core Implementation Guide** (based on FHIR R4) defines:
- Minimum required data elements for each resource type
- Required search parameters
- Terminology bindings (SNOMED CT, LOINC, RxNorm, ICD-10)
- Conformance expectations

Targeting US Core compliance for FHIR resources ensures EHR interoperability.

## Terminology / Code Systems

| Code System | Use | Example |
|-------------|-----|---------|
| SNOMED CT | Clinical terms (diagnoses, procedures, anatomy) | Hip osteoarthritis: 239872002 |
| LOINC | Observations, measurements | Range of motion: 41950-7 |
| ICD-10-CM | Diagnosis codes (billing) | Primary osteoarthritis, right hip: M16.11 |
| CPT | Procedure codes (billing) | Total hip arthroplasty: 27130 |
| UCUM | Units of measure | Degrees: deg; millimeters: mm |
