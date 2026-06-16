# OWASP — Security Guidance for Medical Device Software

🔎 **Finding aid — NOT the authoritative source.** Paraphrased distillation of an external standard/framework; no faithful full-text copy exists in this repository (copyrighted). The original document named in the header above is the sole authority — if a clause-level question isn't answered here, state that the original must be consulted; do not infer clause content. `[VERIFY]` marks are unconfirmed against the source.

**Framework**: OWASP Top 10, OWASP ASVS, OWASP MASTG/MASVS, CycloneDX
**Source**: Open Worldwide Application Security Project
**Referenced In**: FDA Cybersecurity guidance (indirectly — references common vulnerability categories); IEC 81001-5-1

## Overview

OWASP provides multiple security resources relevant to medical device software. Unlike a single standard, OWASP is an ecosystem of projects. The key ones for medical device software development are:

1. **OWASP Top 10** — Most critical web application security risks (for web-based modules)
2. **OWASP ASVS** — Application Security Verification Standard (comprehensive security requirements)
3. **OWASP MASVS/MASTG** — Mobile Application Security (if any module has mobile components)
4. **CycloneDX** — SBOM standard (FDA-accepted format)
5. **OWASP Testing Guide** — Security testing methodology

## OWASP Top 10 (2021)

The most commonly exploited vulnerability categories. Every module with a web interface or API must be evaluated against these.

### A01:2021 — Broken Access Control

- **Risk**: Users acting outside their intended permissions
- **Controls**: Enforce access control server-side; deny by default; implement RBAC; log access control failures

### A02:2021 — Cryptographic Failures

- **Risk**: Failure to protect sensitive data through proper cryptography
- **Controls**: Classify data by sensitivity; encrypt in transit (TLS 1.2+); encrypt at rest; use strong algorithms; manage keys properly

### A03:2021 — Injection

- **Risk**: Untrusted data sent to an interpreter (SQL, OS command, LDAP, etc.)
- **Controls**: Use parameterized queries; validate and sanitize input; use safe APIs; escape output

### A04:2021 — Insecure Design

- **Risk**: Missing or ineffective security controls due to design flaws
- **Controls**: Threat modeling; secure design patterns; reference architectures; abuse case testing

### A05:2021 — Security Misconfiguration

- **Risk**: Insecure default configurations, incomplete configurations, open cloud storage
- **Controls**: Hardened deployment processes; remove unused features; automate configuration verification

### A06:2021 — Vulnerable and Outdated Components

- **Risk**: Using components with known vulnerabilities
- **Controls**: Maintain SBOM; monitor CVE databases; patch management process; only use maintained components
- **Connection**: NTIA SBOM minimum elements, IEC 62304 SOUP requirements

### A07:2021 — Identification and Authentication Failures

- **Risk**: Weak authentication allowing unauthorized access
- **Controls**: Multi-factor authentication where appropriate; secure session handling; credential storage best practices

### A08:2021 — Software and Data Integrity Failures

- **Risk**: Code and infrastructure that doesn't protect against integrity violations
- **Controls**: Signed updates; integrity verification; secure build pipeline; input validation

### A09:2021 — Security Logging and Monitoring Failures

- **Risk**: Insufficient logging, monitoring, and alerting
- **Controls**: Log security-relevant events; ensure log integrity; implement alerting; test detection capability

### A10:2021 — Server-Side Request Forgery (SSRF)

- **Risk**: Application fetches remote resources without validating user-supplied URLs
- **Controls**: Validate and sanitize URLs; use allowlists; segment network access

## OWASP Application Security Verification Standard (ASVS) 4.0

ASVS provides a comprehensive set of security requirements organized by verification level. More granular than Top 10 — useful as a security requirements checklist.

### Verification Levels

| Level | Description |
|-------|-------------|
| **Level 1** | Low assurance — automated verification possible |
| **Level 2** | Standard assurance — most applications |
| **Level 3** | High assurance — critical applications |

### Key ASVS Sections for Medical Devices

| Section | Title | Key Requirements |
|---------|-------|-----------------|
| V1 | Architecture, Design, and Threat Modeling | Documented security architecture; threat model; input validation strategy |
| V2 | Authentication | Password policies; session management; MFA where appropriate |
| V3 | Session Management | Secure session tokens; timeout policies; concurrent session control |
| V4 | Access Control | RBAC; least privilege; access control enforcement at server |
| V5 | Validation, Sanitization, and Encoding | Input validation; output encoding; injection prevention |
| V6 | Stored Cryptography | Key management; algorithm selection; data classification |
| V7 | Error Handling and Logging | Secure error handling; audit logging; log protection |
| V8 | Data Protection | PHI/PII classification; data minimization; retention policies |
| V9 | Communication | TLS configuration; certificate validation; secure API communication |
| V10 | Malicious Code | No backdoors; dependency integrity; build pipeline security |
| V11 | Business Logic | Workflow integrity; rate limiting; anti-automation |
| V12 | Files and Resources | File upload validation; file storage security; path traversal prevention |
| V13 | API and Web Service | API authentication; input validation; rate limiting |
| V14 | Configuration | Security headers; deployment hardening; dependency management |

## CycloneDX (SBOM Format)

OWASP's CycloneDX is one of two FDA-accepted SBOM formats (alongside SPDX).

| Feature | CycloneDX | SPDX |
|---------|-----------|------|
| Focus | Application security | License compliance (expanded to security) |
| Vulnerability data | Native support (VEX) | Via external linkage |
| Format | JSON, XML, Protobuf | JSON, RDF, tag-value, XLSX |
| Ecosystem | Strong in application security tooling | Strong in open source compliance |
| Medical device use | Well-suited — includes vulnerability correlation | Well-suited — ISO standard (5962:2021) |

## Mapping to IEC 81001-5-1

| OWASP Resource | IEC 81001-5-1 Clause |
|---------------|---------------------|
| ASVS security requirements | 5.2 (Security requirements) |
| Top 10 vulnerability categories | 5.4, 5.5 (Secure design and implementation) |
| Testing Guide | 5.7 (Security testing) |
| CycloneDX SBOM | 5.8 (Software release — SBOM) |
| Vulnerability monitoring | 6.1 (Security monitoring) |
