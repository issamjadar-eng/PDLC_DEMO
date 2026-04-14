# Industry Frameworks

Non-FDA, non-standard industry frameworks, interoperability standards, and guidance that inform our regulatory and technical approach.

## Active Frameworks

Frameworks with dedicated distilled files in this folder:

| Framework | File | Full Title | Referenced In | Spec URL |
|-----------|------|-----------|---------------|----------|

- **Spec URL** column links to the official spec (e.g., `https://hl7.org/fhir/`, `https://owasp.org/`, `https://www.dicomstandard.org/`). The distilled markdown in this folder is a derivative; the linked spec is the authoritative source.

## Evaluated — Not Required

Frameworks evaluated and determined not needed, with rationale:

| Framework | Full Title | Scope Qualifier | Rationale for Exclusion |
|-----------|-----------|-----------------|------------------------|

- **Scope Qualifier** column should name the *specific slice* of the framework that was evaluated as not applicable (e.g., for IHE: "Radiology profiles only — ITI/Pharmacy may still apply"). Frameworks like IHE and HL7 are umbrella spec families with many independent profiles; a wholesale exclusion based on one slice silences future applicability when project capabilities change. If the entire framework is genuinely out of scope, write "(whole framework)".

## Conventions

- **Naming**: `framework-short-name.md`
- Note the version/date of the framework document
- Document which FDA guidance references this framework and why
- Frameworks evaluated and excluded should remain in the "Evaluated — Not Required" table with rationale

## Changelog

| Date | Author | Summary |
|------|--------|---------|
| YYYY-MM-DD | XX | Initial version — created by /medtech-docs init |
