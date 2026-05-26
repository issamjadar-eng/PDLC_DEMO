"""Medtech / regulated-life-sciences vocabulary pack.

Activates clinical / medical / regulatory keyword routing in md-deck's icon
classification. Load via:

    from icons import configure_vocabularies
    configure_vocabularies(["medtech"])

Covered domains:
    - Clinical & patient care
    - Pharmacology & dosing
    - Surgical / interventional
    - Anatomy & lab
    - Regulatory submissions (FDA, EMA, MHRA, PMDA, …)
    - QMS / standards (ISO 13485, ISO 14971, IEC 62304)
    - Risk management (hazards, FMEA, failure modes)
    - Medical-device-specific failure modes (alarm fatigue, dose-calc errors,
      pump tampering, free flow, drug-library mismatch, battery depletion)
    - Cohorts of clinical interest (KOLs, persona advisors, test protocols,
      sites/clinics, predicate devices)

The icon NAMES referenced here (`stethoscope`, `heartbeat`, `pill`, `scalpel`,
`hospital`, `clipboard-medical`, `circuit`, `shield-check`, `certificate`,
`scale-justice`, `circle-target`, `warn`, `pill`, `bell-alarm`, `battery-low`,
`tamper-shield`, `bug-defect`, `leak-drop`, `user-single`, `users`) must exist
in trunk `icons.py`'s `ICONS` dict. The trunk keeps every glyph; this pack
only contributes routing rules.
"""

# Keyword routing — first-token-substring match.
# Order: most-specific first.
KEYWORD_REGISTRY: list[tuple[list[str], str]] = [
    # Clinical / patient care
    (["clinical", "patient", "diagnos"],                   "stethoscope"),
    (["heart", "cardiac", "ecg", "ekg", "heart-rate"],     "heartbeat"),
    (["pain", "ease", "pca", "analgesia", "anesthet"],     "pill"),
    (["drug", "pharmac", "dose", "formular"],              "pill"),
    (["bandage", "wound", "dressing", "first-aid"],        "bandage"),
    (["scalpel", "surgery", "surgical", "incision"],       "scalpel"),
    (["vital", "monitor-vitals", "patient-monitor"],       "vitals"),
    (["ambulance", "emergency-vehicle", "ems", "911"],     "ambulance"),
    (["prescription", "rx", "script"],                     "prescription"),
    (["wheelchair", "mobility", "accessibility"],          "wheelchair"),
    (["needle", "vaccin", "injecti"],                      "syringe"),
    (["infusion", "iv", "drip", "intraven"],               "iv-drip"),
    (["dna", "gene", "genom", "sequenc"],                  "dna"),
    (["lab", "biolog", "molecul", "specimen"],             "microscope"),
    (["brain", "cogniti", "neuro"],                        "brain"),
    (["respirat", "breath", "lung"],                       "lungs"),
    (["sample", "test-tube", "assay"],                     "test-tube"),
    (["hospital", "clinic", "facility"],                   "hospital"),
    (["medical-record", "medical record", "ehr", "emr"],   "clipboard-medical"),
    (["device", "samd", "simd"],                           "circuit"),

    # Regulatory / QMS / standards
    (["regulator", "fda", "510(k)", "510k", "submission",
      "pccp", "ema", "mhra", "pmda", "tga", "anvisa"],     "shield-check"),
    (["audit", "iso 13485", "iso 14971", "iec 62304"],     "certificate"),
    (["risk-management", "iso 14971", "hazard", "fmea"],   "scale-justice"),

    # Cohorts (pack-specific cohort terms; icons inherit from trunk)
    (["kol", "kols", "investigator", "investigators"],     "users"),
]

# Multi-word intent phrases — failure modes, regulatory concepts, cohort terms.
# These match BEFORE single-word keywords so the slide's actual subject
# (e.g. "alarm fatigue", "substantial equivalence") wins over incidental
# vocabulary in surrounding prose.
INTENT_PHRASES: list[tuple[list[str], str]] = [
    # Hazards / failure modes — medical-device specific
    (["free flow", "uncontrolled bolus", "anti-free-flow", "runaway flow"], "leak-drop"),
    (["drug library mismatch", "wrong concentration", "overdose",
      "underdose", "mismapped"], "pill"),
    (["alarm fatigue", "alarm masking", "nuisance alarm",
      "alarm habituate", "alert habituate"], "bell-alarm"),
    (["battery depletion", "depleted battery", "battery low",
      "battery reserve", "grace-period"], "battery-low"),
    (["pump tampering", "tamper", "unauthorized access",
      "intrusion", "tamper-evident"], "tamper-shield"),
    (["software defect", "regression", "calculation error",
      "code defect", "dose calculation", "field-failure"], "bug-defect"),
    # Cohort / regulatory concepts that should not lose to incidental substrings
    (["digital twin", "persona advisor"],                  "user-single"),
    (["filing scope", "in-scope", "out of scope"],         "scale-justice"),
    (["substantial equivalence", "predicate device"],      "circle-target"),
    (["risk register", "hazard register"],                 "warn"),
    (["change control", "change protocol"],                "git-merge"),
    (["dose-error reduction", "dose reduction"],           "shield-check"),
]

# Group-icon registry — kind-icons for catalog slides representing N
# instances of the same medtech-flavored cohort.
GROUP_ICONS: dict[str, str] = {
    "test-case": "clipboard-medical",
    "site":      "hospital",
    "predicate": "circle-target",
    "hazard":    "warn",
}

# Title-hint routing for medtech-specific homogeneous groups.
GROUP_TITLE_HINTS: list[tuple[list[str], str]] = [
    (["kol", "advisor", "advisors", "persona", "personas",
      "digital twin", "digital twins", "expert reviewer"], "persona"),
    (["test case", "test cases", "test protocol", "test protocols",
      "v&v", "verification protocol", "validation protocol"], "test-case"),
    (["site", "sites", "facility", "facilities", "clinic", "clinics"], "site"),
    (["predicate", "predicates", "comparator"],            "predicate"),
    (["hazard", "hazards", "risk register", "failure mode"], "hazard"),
]
