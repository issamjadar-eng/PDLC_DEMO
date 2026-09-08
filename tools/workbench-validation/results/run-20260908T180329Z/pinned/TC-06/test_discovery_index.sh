#!/usr/bin/env bash
# Smoke tests for the discovery-index resolver.
#
# Strategy: build small fixture projects in a tmpdir, run the resolver, and
# assert that resolutions, gaps, and ambiguity_notes come out where expected.
# No dependency on any real project content.
#
# Each test case is self-contained. Exit 0 if all pass, 1 on any failure.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
RESOLVER="$SKILL_DIR/scripts/discovery-index.py"

if [[ ! -f "$RESOLVER" ]]; then
    echo "FAIL: resolver not found at $RESOLVER" >&2
    exit 1
fi

# ──────────────────────────────────────────────────────────────────────
# Test harness
# ──────────────────────────────────────────────────────────────────────

PASS=0
FAIL=0
ERRORS=()

assert_eq() {
    local label="$1" expected="$2" actual="$3"
    if [[ "$expected" == "$actual" ]]; then
        PASS=$((PASS+1))
    else
        FAIL=$((FAIL+1))
        ERRORS+=("$label: expected '$expected', got '$actual'")
    fi
}

assert_path_endswith() {
    local label="$1" suffix="$2" path="$3"
    if [[ "$path" == *"$suffix" ]]; then
        PASS=$((PASS+1))
    else
        FAIL=$((FAIL+1))
        ERRORS+=("$label: expected path ending with '$suffix', got '$path'")
    fi
}

run_resolver() {
    local project_root="$1"
    python3 "$RESOLVER" "$project_root" --skill-dir "$SKILL_DIR" > /dev/null
}

read_json() {
    local project_root="$1"
    local slug="$2"
    cat "$project_root/docs/project/dhf-manifest/$slug-dhf-discovery.json"
}

# ──────────────────────────────────────────────────────────────────────
# Case 1: clean resolution across mixed naming conventions
# ──────────────────────────────────────────────────────────────────────

case1() {
    local TMP
    TMP=$(mktemp -d)
    trap "rm -rf $TMP" RETURN

    mkdir -p "$TMP/docs/project/strategies"
    mkdir -p "$TMP/docs/project/dhfs/sys-dhf/design-controls/architecture"
    mkdir -p "$TMP/docs/project/dhfs/item-a/design-controls/architecture"
    mkdir -p "$TMP/docs/project/dhfs/item-a/risk-management"
    mkdir -p "$TMP/docs/project/dhfs/item-b/design-controls/architecture"
    mkdir -p "$TMP/docs/project/dhfs/item-b/risk-management"
    mkdir -p "$TMP/docs/project/dhf-manifest"

    echo "# Regulatory Strategy" > "$TMP/docs/project/strategies/regulatory-strategy.md"
    echo "# Architecture Strategy" > "$TMP/docs/project/strategies/architecture-strategy.md"

    # System DHF — canonical short-name convention
    echo "# System SAD" > "$TMP/docs/project/dhfs/sys-dhf/design-controls/architecture/widget-system-sad.md"

    # Item A — formal-doc convention; full risk-management complement
    echo "# Item A SAD" > "$TMP/docs/project/dhfs/item-a/design-controls/architecture/Widget Module A - Software Architecture Document (SAD) - 1.0.0.md"
    echo "# Item A SDD" > "$TMP/docs/project/dhfs/item-a/design-controls/architecture/Widget Module A - Software Detailed Design (SDD) - 1.0.0.md"
    echo "# Item A RMP" > "$TMP/docs/project/dhfs/item-a/risk-management/Widget Module A - Risk Management Plan.md"
    echo "# Item A SRA" > "$TMP/docs/project/dhfs/item-a/risk-management/Widget Module A - Software Risk Assessment (SRA) - 1.0.0.md"

    # Item B — intentional gap (no SAD, empty risk-management folder)
    : > "$TMP/docs/project/dhfs/item-b/design-controls/architecture/.gitkeep"

    cat > "$TMP/project.yml" <<EOF
project:
  name: fixture-clean
dhfs:
  - leaf: sys-dhf
    path: docs/project/dhfs/sys-dhf
    role: system
  - leaf: item-a
    path: docs/project/dhfs/item-a
    role: item
  - leaf: item-b
    path: docs/project/dhfs/item-b
    role: item
EOF

    run_resolver "$TMP"
    local OUT
    OUT=$(read_json "$TMP" "fixture-clean")

    # regulatory_strategy resolved
    local reg_path
    reg_path=$(echo "$OUT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['project_roles']['regulatory_strategy']['path'])")
    assert_path_endswith "case1.regulatory_strategy" "regulatory-strategy.md" "$reg_path"

    # sys-dhf system_architecture won via *-system-sad.md
    local sys_pattern
    sys_pattern=$(echo "$OUT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['dhf_roles']['sys-dhf']['system_architecture']['matched_pattern'])")
    assert_eq "case1.sys-dhf.system_architecture.pattern" "*-system-sad.md" "$sys_pattern"

    # item-a system_architecture won via *Software Architecture Document*.md (not SDD pattern)
    local item_a_pattern
    item_a_pattern=$(echo "$OUT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['dhf_roles']['item-a']['system_architecture']['matched_pattern'])")
    assert_eq "case1.item-a.system_architecture.pattern" "*Software Architecture Document*.md" "$item_a_pattern"

    # item-a module_design resolved to SDD
    local item_a_sdd
    item_a_sdd=$(echo "$OUT" | python3 -c "import json,sys; d=json.load(sys.stdin); v=d['dhf_roles']['item-a']['module_design']; print(v['matched_pattern'] if v else 'NULL')")
    assert_eq "case1.item-a.module_design.pattern" "*Software Detailed Design*.md" "$item_a_sdd"

    # item-b system_architecture should be NULL with a corresponding gap
    local item_b_sa
    item_b_sa=$(echo "$OUT" | python3 -c "import json,sys; d=json.load(sys.stdin); v=d['dhf_roles']['item-b']['system_architecture']; print('NULL' if v is None else v.get('path'))")
    assert_eq "case1.item-b.system_architecture" "NULL" "$item_b_sa"

    local item_b_gap_count
    item_b_gap_count=$(echo "$OUT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(sum(1 for g in d['gaps'] if g.get('dhf')=='item-b' and g.get('role')=='system_architecture'))")
    assert_eq "case1.item-b.system_architecture.gap" "1" "$item_b_gap_count"

    # item-a risk_management_plan resolved
    local item_a_rmp
    item_a_rmp=$(echo "$OUT" | python3 -c "import json,sys; d=json.load(sys.stdin); v=d['dhf_roles']['item-a']['risk_management_plan']; print(v['path'] if v else 'NULL')")
    assert_path_endswith "case1.item-a.risk_management_plan" "Widget Module A - Risk Management Plan.md" "$item_a_rmp"

    # ambiguity_notes should be empty for this clean case
    local amb_count
    amb_count=$(echo "$OUT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(len(d['ambiguity_notes']))")
    assert_eq "case1.ambiguity_count" "0" "$amb_count"
}

# ──────────────────────────────────────────────────────────────────────
# Case 2: deliberate ambiguity — DHF has both canonical and formal-doc SAD
# ──────────────────────────────────────────────────────────────────────

case2() {
    local TMP
    TMP=$(mktemp -d)
    trap "rm -rf $TMP" RETURN

    mkdir -p "$TMP/docs/project/strategies"
    mkdir -p "$TMP/docs/project/dhfs/dual-dhf/design-controls/architecture"
    mkdir -p "$TMP/docs/project/dhf-manifest"

    echo "# Reg" > "$TMP/docs/project/strategies/regulatory-strategy.md"
    # Two candidate SADs — canonical short-name AND formal-doc convention
    echo "# Canonical SAD" > "$TMP/docs/project/dhfs/dual-dhf/design-controls/architecture/widget-system-sad.md"
    echo "# Formal SAD" > "$TMP/docs/project/dhfs/dual-dhf/design-controls/architecture/Widget - Software Architecture Document (SAD).md"

    cat > "$TMP/project.yml" <<EOF
project:
  name: fixture-ambiguity
dhfs:
  - leaf: dual-dhf
    path: docs/project/dhfs/dual-dhf
    role: system
EOF

    run_resolver "$TMP"
    local OUT
    OUT=$(read_json "$TMP" "fixture-ambiguity")

    # The higher-ranked pattern (*-system-sad.md) should win
    local winner_pattern
    winner_pattern=$(echo "$OUT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['dhf_roles']['dual-dhf']['system_architecture']['matched_pattern'])")
    assert_eq "case2.dual-dhf.winner" "*-system-sad.md" "$winner_pattern"

    # An ambiguity_note should record the formal-doc alternative
    local amb_count
    amb_count=$(echo "$OUT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(sum(1 for a in d['ambiguity_notes'] if a.get('dhf')=='dual-dhf' and a.get('role')=='system_architecture'))")
    assert_eq "case2.dual-dhf.ambiguity_count" "1" "$amb_count"
}

# ──────────────────────────────────────────────────────────────────────
# Case 3: L3 override via project.yml patterns_extra
# ──────────────────────────────────────────────────────────────────────

case3() {
    local TMP
    TMP=$(mktemp -d)
    trap "rm -rf $TMP" RETURN

    mkdir -p "$TMP/docs/project/strategies"
    mkdir -p "$TMP/docs/project/dhfs/quirky-dhf/design-controls/architecture"
    mkdir -p "$TMP/docs/project/dhf-manifest"

    echo "# Reg" > "$TMP/docs/project/strategies/regulatory-strategy.md"
    # A SAD with a project-specific naming convention not in L2
    echo "# Quirky SAD" > "$TMP/docs/project/dhfs/quirky-dhf/design-controls/architecture/MyProduct.SAD.v3.md"

    cat > "$TMP/project.yml" <<EOF
project:
  name: fixture-override
dhfs:
  - leaf: quirky-dhf
    path: docs/project/dhfs/quirky-dhf
    role: system
evidence_layout:
  layers:
    system_architecture:
      patterns_extra:
        - "*.SAD.v*.md"
EOF

    run_resolver "$TMP"
    local OUT
    OUT=$(read_json "$TMP" "fixture-override")

    # Override pattern should be prepended (highest precedence) and win
    local winner_pattern
    winner_pattern=$(echo "$OUT" | python3 -c "import json,sys; d=json.load(sys.stdin); v=d['dhf_roles']['quirky-dhf']['system_architecture']; print(v['matched_pattern'] if v else 'NULL')")
    assert_eq "case3.quirky-dhf.override_winner" "*.SAD.v*.md" "$winner_pattern"

    local winner_path
    winner_path=$(echo "$OUT" | python3 -c "import json,sys; d=json.load(sys.stdin); v=d['dhf_roles']['quirky-dhf']['system_architecture']; print(v['path'] if v else 'NULL')")
    assert_path_endswith "case3.quirky-dhf.override_path" "MyProduct.SAD.v3.md" "$winner_path"
}

# ──────────────────────────────────────────────────────────────────────
# Case 4: external roles count files, never gap on per-file basis
# ──────────────────────────────────────────────────────────────────────

case4() {
    local TMP
    TMP=$(mktemp -d)
    trap "rm -rf $TMP" RETURN

    mkdir -p "$TMP/docs/project/strategies"
    mkdir -p "$TMP/docs/external/fda-guidance"
    mkdir -p "$TMP/docs/external/standards"
    # Deliberately no industry-frameworks/ directory
    mkdir -p "$TMP/docs/project/dhf-manifest"

    echo "# Reg" > "$TMP/docs/project/strategies/regulatory-strategy.md"
    echo "# FDA 1" > "$TMP/docs/external/fda-guidance/g1.md"
    echo "# FDA 2" > "$TMP/docs/external/fda-guidance/g2.md"
    echo "# Std 1" > "$TMP/docs/external/standards/s1.md"

    cat > "$TMP/project.yml" <<EOF
project:
  name: fixture-external
dhfs: []
EOF

    run_resolver "$TMP"
    local OUT
    OUT=$(read_json "$TMP" "fixture-external")

    local fda_count
    fda_count=$(echo "$OUT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['external_roles']['fda_guidance']['file_count'])")
    assert_eq "case4.fda_guidance.file_count" "2" "$fda_count"

    local std_count
    std_count=$(echo "$OUT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['external_roles']['standards']['file_count'])")
    assert_eq "case4.standards.file_count" "1" "$std_count"

    # industry-frameworks folder missing → gap, but role still listed
    local frameworks_exists
    frameworks_exists=$(echo "$OUT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['external_roles']['industry_frameworks']['exists'])")
    assert_eq "case4.industry_frameworks.exists" "False" "$frameworks_exists"

    local frameworks_gap
    frameworks_gap=$(echo "$OUT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(sum(1 for g in d['gaps'] if g.get('role')=='industry_frameworks'))")
    assert_eq "case4.industry_frameworks.gap" "1" "$frameworks_gap"
}

# ──────────────────────────────────────────────────────────────────────
# Case 5: external-mode DHF — nested sub-convention (folder/v*.md + index.md)
# ──────────────────────────────────────────────────────────────────────

case5() {
    local TMP
    TMP=$(mktemp -d)
    trap "rm -rf $TMP" RETURN

    mkdir -p "$TMP/docs/project/strategies"
    mkdir -p "$TMP/docs/project/_mirror/widget/product-overview/software-architecture-document-sad"
    mkdir -p "$TMP/docs/project/_mirror/widget/product-overview/software-detailed-design-sdd"
    mkdir -p "$TMP/docs/project/_mirror/widget/product-overview/software-risk-assessment-sra"
    mkdir -p "$TMP/docs/project/dhf-manifest"

    echo "# Reg" > "$TMP/docs/project/strategies/regulatory-strategy.md"
    # Nested external layout — both v*.md (substantive) and index.md (Confluence summary)
    echo "# SAD index" > "$TMP/docs/project/_mirror/widget/product-overview/software-architecture-document-sad/index.md"
    echo "# SAD v1.0.0" > "$TMP/docs/project/_mirror/widget/product-overview/software-architecture-document-sad/v1.0.0.md"
    echo "# SDD index only" > "$TMP/docs/project/_mirror/widget/product-overview/software-detailed-design-sdd/index.md"
    echo "# SRA v2.1.0" > "$TMP/docs/project/_mirror/widget/product-overview/software-risk-assessment-sra/v2.1.0.md"

    # Fixture taxonomy
    cat > "$TMP/docs/project/_mirror/.taxonomy.yml" <<EOF
schema_version: 0.2
discovery_root: product-overview
mappings:
  software-architecture-document-sad: { canonical_role: architecture }
  software-detailed-design-sdd: { canonical_role: design }
  software-risk-assessment-sra: { canonical_role: risk-management }
  hazard-traceability-matrix-htm: { canonical_role: trace-matrix }
EOF

    cat > "$TMP/project.yml" <<EOF
project:
  name: fixture-external-nested
dhfs:
  - leaf: widget-dhf
    path: docs/project/_mirror/widget
    role: item
    dhf_organization: external
    taxonomy_path: docs/project/_mirror/.taxonomy.yml
EOF

    run_resolver "$TMP"
    local OUT
    OUT=$(read_json "$TMP" "fixture-external-nested")

    # system_architecture should pick v1.0.0.md (higher-ranked than index.md)
    local sa_pattern
    sa_pattern=$(echo "$OUT" | python3 -c "import json,sys; d=json.load(sys.stdin); v=d['dhf_roles']['widget-dhf']['system_architecture']; print(v['matched_pattern'] if v else 'NULL')")
    assert_eq "case5.system_architecture.pattern" "v*.md" "$sa_pattern"

    # module_design has only index.md — should fall back
    local md_pattern
    md_pattern=$(echo "$OUT" | python3 -c "import json,sys; d=json.load(sys.stdin); v=d['dhf_roles']['widget-dhf']['module_design']; print(v['matched_pattern'] if v else 'NULL')")
    assert_eq "case5.module_design.fallback_to_index" "index.md" "$md_pattern"

    # SRA resolves to v2.1.0.md
    local sra_path
    sra_path=$(echo "$OUT" | python3 -c "import json,sys; d=json.load(sys.stdin); v=d['dhf_roles']['widget-dhf']['software_risk_assessment']; print(v['path'] if v else 'NULL')")
    assert_path_endswith "case5.software_risk_assessment" "v2.1.0.md" "$sra_path"

    # mode recorded
    local mode
    mode=$(echo "$OUT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['dhf_roles']['widget-dhf']['dhf_organization'])")
    assert_eq "case5.mode_recorded" "external" "$mode"

    # risk_management_plan has no external mapping → informational gap
    local rmp_informational
    rmp_informational=$(echo "$OUT" | python3 -c "
import json,sys
d=json.load(sys.stdin)
gaps=[g for g in d['gaps'] if g.get('dhf')=='widget-dhf' and g.get('role')=='risk_management_plan']
print(str(gaps[0].get('informational', False)) if gaps else 'NO_GAP')
")
    assert_eq "case5.rmp.informational_gap" "True" "$rmp_informational"
}

# ──────────────────────────────────────────────────────────────────────
# Case 6: external-mode DHF — flat sub-convention (folder.md instead of folder/)
# ──────────────────────────────────────────────────────────────────────

case6() {
    local TMP
    TMP=$(mktemp -d)
    trap "rm -rf $TMP" RETURN

    mkdir -p "$TMP/docs/project/strategies"
    mkdir -p "$TMP/docs/project/_mirror/flatdhf/product-overview"
    mkdir -p "$TMP/docs/project/dhf-manifest"

    echo "# Reg" > "$TMP/docs/project/strategies/regulatory-strategy.md"
    # Flat external layout — folder name becomes .md filename at parent level
    echo "# Flat SAD" > "$TMP/docs/project/_mirror/flatdhf/product-overview/software-architecture-document-sad.md"

    cat > "$TMP/docs/project/_mirror/.taxonomy.yml" <<EOF
schema_version: 0.2
discovery_root: product-overview
mappings:
  software-architecture-document-sad: { canonical_role: architecture }
EOF

    cat > "$TMP/project.yml" <<EOF
project:
  name: fixture-external-flat
dhfs:
  - leaf: flat-dhf
    path: docs/project/_mirror/flatdhf
    role: item
    dhf_organization: external
    taxonomy_path: docs/project/_mirror/.taxonomy.yml
EOF

    run_resolver "$TMP"
    local OUT
    OUT=$(read_json "$TMP" "fixture-external-flat")

    # system_architecture should resolve via flat-file fallback
    local sa_path
    sa_path=$(echo "$OUT" | python3 -c "import json,sys; d=json.load(sys.stdin); v=d['dhf_roles']['flat-dhf']['system_architecture']; print(v['path'] if v else 'NULL')")
    assert_path_endswith "case6.system_architecture.flat_resolution" "software-architecture-document-sad.md" "$sa_path"

    local sa_pattern
    sa_pattern=$(echo "$OUT" | python3 -c "import json,sys; d=json.load(sys.stdin); v=d['dhf_roles']['flat-dhf']['system_architecture']; print(v['matched_pattern'] if v else 'NULL')")
    assert_eq "case6.system_architecture.flat_marker" "software-architecture-document-sad.md (flat-file)" "$sa_pattern"
}

# ──────────────────────────────────────────────────────────────────────
# Case 7: project-scoped multi_file role — folder pointer with file_count
# ──────────────────────────────────────────────────────────────────────

case7() {
    local TMP
    TMP=$(mktemp -d)
    trap "rm -rf $TMP" RETURN

    mkdir -p "$TMP/docs/project/strategies"
    mkdir -p "$TMP/docs/project/input-analysis/kol-feedback"
    mkdir -p "$TMP/docs/project/input-analysis/competitive-landscape"
    # Deliberately no market-research folder
    mkdir -p "$TMP/docs/project/dhf-manifest"

    echo "# Reg" > "$TMP/docs/project/strategies/regulatory-strategy.md"
    echo "# KOL interview 1" > "$TMP/docs/project/input-analysis/kol-feedback/sme-r1.md"
    echo "# KOL interview 2" > "$TMP/docs/project/input-analysis/kol-feedback/sme-r2.md"
    echo "# KOL interview 3" > "$TMP/docs/project/input-analysis/kol-feedback/sme-r3.md"
    echo "# Comp A" > "$TMP/docs/project/input-analysis/competitive-landscape/competitor-a.md"

    cat > "$TMP/project.yml" <<EOF
project:
  name: fixture-multifile-project
dhfs: []
EOF

    run_resolver "$TMP"
    local OUT
    OUT=$(read_json "$TMP" "fixture-multifile-project")

    # kol_feedback: 3 files, folder exists
    local kol_count
    kol_count=$(echo "$OUT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['project_roles']['kol_feedback']['file_count'])")
    assert_eq "case7.kol_feedback.file_count" "3" "$kol_count"

    local kol_exists
    kol_exists=$(echo "$OUT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['project_roles']['kol_feedback']['exists'])")
    assert_eq "case7.kol_feedback.exists" "True" "$kol_exists"

    local kol_path_key
    kol_path_key=$(echo "$OUT" | python3 -c "import json,sys; d=json.load(sys.stdin); e=d['project_roles']['kol_feedback']; print('folder' if 'folder' in e else 'path')")
    assert_eq "case7.kol_feedback.shape" "folder" "$kol_path_key"

    # competitive_landscape: 1 file
    local comp_count
    comp_count=$(echo "$OUT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['project_roles']['competitive_landscape']['file_count'])")
    assert_eq "case7.competitive_landscape.file_count" "1" "$comp_count"

    # market_research folder missing → emits entry with exists=False + gap
    local mr_exists
    mr_exists=$(echo "$OUT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['project_roles']['market_research']['exists'])")
    assert_eq "case7.market_research.exists" "False" "$mr_exists"

    local mr_gap
    mr_gap=$(echo "$OUT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(sum(1 for g in d['gaps'] if g.get('role')=='market_research' and not g.get('informational')))")
    assert_eq "case7.market_research.gap" "1" "$mr_gap"
}

# ──────────────────────────────────────────────────────────────────────
# Case 8: per-dhf multi_file role (internal mode) — folder pointer
# ──────────────────────────────────────────────────────────────────────

case8() {
    local TMP
    TMP=$(mktemp -d)
    trap "rm -rf $TMP" RETURN

    mkdir -p "$TMP/docs/project/strategies"
    mkdir -p "$TMP/docs/project/dhfs/sys-dhf/postmarket/complaints"
    mkdir -p "$TMP/docs/project/dhfs/sys-dhf/postmarket/capa"
    # Deliberately no adverse-events/ folder
    mkdir -p "$TMP/docs/project/dhfs/empty-dhf/postmarket/complaints"  # exists but empty
    mkdir -p "$TMP/docs/project/dhf-manifest"

    echo "# Reg" > "$TMP/docs/project/strategies/regulatory-strategy.md"
    echo "# C1" > "$TMP/docs/project/dhfs/sys-dhf/postmarket/complaints/c1.md"
    echo "# C2" > "$TMP/docs/project/dhfs/sys-dhf/postmarket/complaints/c2.md"
    echo "# CAPA1" > "$TMP/docs/project/dhfs/sys-dhf/postmarket/capa/capa-001.md"

    cat > "$TMP/project.yml" <<EOF
project:
  name: fixture-multifile-dhf
dhfs:
  - leaf: sys-dhf
    path: docs/project/dhfs/sys-dhf
    role: system
  - leaf: empty-dhf
    path: docs/project/dhfs/empty-dhf
    role: item
EOF

    run_resolver "$TMP"
    local OUT
    OUT=$(read_json "$TMP" "fixture-multifile-dhf")

    # sys-dhf complaints: 2 files
    local c_count
    c_count=$(echo "$OUT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['dhf_roles']['sys-dhf']['complaints']['file_count'])")
    assert_eq "case8.sys-dhf.complaints.file_count" "2" "$c_count"

    local c_shape
    c_shape=$(echo "$OUT" | python3 -c "import json,sys; d=json.load(sys.stdin); e=d['dhf_roles']['sys-dhf']['complaints']; print('folder' if 'folder' in e else 'path')")
    assert_eq "case8.sys-dhf.complaints.shape" "folder" "$c_shape"

    # sys-dhf capa: 1 file
    local capa_count
    capa_count=$(echo "$OUT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['dhf_roles']['sys-dhf']['capa']['file_count'])")
    assert_eq "case8.sys-dhf.capa.file_count" "1" "$capa_count"

    # sys-dhf adverse_events: folder missing → exists=False, file_count=0
    local ae_exists
    ae_exists=$(echo "$OUT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['dhf_roles']['sys-dhf']['adverse_events']['exists'])")
    assert_eq "case8.sys-dhf.adverse_events.exists" "False" "$ae_exists"

    # empty-dhf complaints: folder exists but empty → exists=True, file_count=0, NO gap
    local e_count
    e_count=$(echo "$OUT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['dhf_roles']['empty-dhf']['complaints']['file_count'])")
    assert_eq "case8.empty-dhf.complaints.file_count" "0" "$e_count"

    local e_exists
    e_exists=$(echo "$OUT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['dhf_roles']['empty-dhf']['complaints']['exists'])")
    assert_eq "case8.empty-dhf.complaints.exists" "True" "$e_exists"

    # Empty-but-existing folder must NOT emit a gap (zero count is valid signal)
    local e_gap
    e_gap=$(echo "$OUT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(sum(1 for g in d['gaps'] if g.get('dhf')=='empty-dhf' and g.get('role')=='complaints' and not g.get('informational')))")
    assert_eq "case8.empty-dhf.complaints.no_gap" "0" "$e_gap"
}

# ──────────────────────────────────────────────────────────────────────
# Case 9: multi-match no-winner — every pattern hits >1 file, none wins.
# A user-needs folder holding `user-needs-register.md` + `user-needs-archive.md`:
# both match the broad `*user-needs*.md`, neither matches the exact-match
# `user-needs.md` (v11) or any other more-specific pattern, so no pattern
# resolves to exactly-one. Expectation: an ambiguity_notes[] entry with
# winning_* fields null + alternatives listing all candidates, AND a paired
# gaps[] entry referencing the ambiguity_notes for visibility.
# NOTE: the original PDLC_DEMO repro (`user-needs.md` + `user-needs-register.md`)
# is no longer a no-winner case — v11 added the exact-match `user-needs.md`
# pattern that resolves it. This fixture uses non-exact filenames to keep the
# no-winner resolver path under test.
# ──────────────────────────────────────────────────────────────────────

case9() {
    local TMP
    TMP=$(mktemp -d)
    trap "rm -rf $TMP" RETURN

    mkdir -p "$TMP/docs/project/strategies"
    mkdir -p "$TMP/docs/project/dhfs/ambig-dhf/design-controls/user-needs"
    mkdir -p "$TMP/docs/project/dhf-manifest"

    echo "# Reg" > "$TMP/docs/project/strategies/regulatory-strategy.md"
    # Two files BOTH match the broad pattern *user-needs*.md; neither matches
    # the exact `user-needs.md` (v11) or any other more-specific pattern.
    echo "# Register" > "$TMP/docs/project/dhfs/ambig-dhf/design-controls/user-needs/user-needs-register.md"
    echo "# Archive" > "$TMP/docs/project/dhfs/ambig-dhf/design-controls/user-needs/user-needs-archive.md"

    cat > "$TMP/project.yml" <<EOF
project:
  name: fixture-multi-match-no-winner
dhfs:
  - leaf: ambig-dhf
    path: docs/project/dhfs/ambig-dhf
    role: system
EOF

    run_resolver "$TMP"
    local OUT
    OUT=$(read_json "$TMP" "fixture-multi-match-no-winner")

    # user_needs resolution should be null
    local un_value
    un_value=$(echo "$OUT" | python3 -c "import json,sys; d=json.load(sys.stdin); v=d['dhf_roles']['ambig-dhf']['user_needs']; print('NULL' if v is None else v.get('path'))")
    assert_eq "case9.ambig-dhf.user_needs" "NULL" "$un_value"

    # ambiguity_notes should contain a no-winner entry for this role
    local amb_no_winner
    amb_no_winner=$(echo "$OUT" | python3 -c "
import json, sys
d = json.load(sys.stdin)
notes = [n for n in d['ambiguity_notes']
         if n.get('dhf') == 'ambig-dhf'
         and n.get('role') == 'user_needs'
         and n.get('winning_pattern') is None
         and n.get('winning_path') is None]
print(len(notes))
")
    assert_eq "case9.ambig-dhf.user_needs.ambiguity_no_winner" "1" "$amb_no_winner"

    # The ambiguity note should list BOTH candidates as alternatives
    local alt_count
    alt_count=$(echo "$OUT" | python3 -c "
import json, sys
d = json.load(sys.stdin)
notes = [n for n in d['ambiguity_notes']
         if n.get('dhf') == 'ambig-dhf'
         and n.get('role') == 'user_needs'
         and n.get('winning_pattern') is None]
print(len(notes[0]['alternatives']) if notes else 0)
")
    assert_eq "case9.ambig-dhf.user_needs.alternatives_count" "2" "$alt_count"

    # A paired gap entry should exist with a reason that references ambiguity_notes
    local gap_refs_amb
    gap_refs_amb=$(echo "$OUT" | python3 -c "
import json, sys
d = json.load(sys.stdin)
gaps = [g for g in d['gaps']
        if g.get('dhf') == 'ambig-dhf'
        and g.get('role') == 'user_needs'
        and 'ambiguity_notes' in (g.get('reason') or '')]
print(len(gaps))
")
    assert_eq "case9.ambig-dhf.user_needs.gap_refs_ambiguity" "1" "$gap_refs_amb"
}

# ──────────────────────────────────────────────────────────────────────
# Case 10: frontmatter `canonical_role:` opt-in takes precedence over
# filename patterns. The user-needs folder holds TWO files:
#   - user-needs.md          — would win via the exact-match pattern (v11)
#   - legacy-un-doc.md       — declares `canonical_role: user_needs` in frontmatter
# Expectation: the frontmatter declarer wins, NOT the pattern match, and the
# winning entry's matched_pattern is `frontmatter:canonical_role`.
# ──────────────────────────────────────────────────────────────────────

case10() {
    local TMP
    TMP=$(mktemp -d)
    trap "rm -rf $TMP" RETURN

    mkdir -p "$TMP/docs/project/strategies"
    mkdir -p "$TMP/docs/project/dhfs/fm-dhf/design-controls/user-needs"
    mkdir -p "$TMP/docs/project/dhf-manifest"

    echo "# Reg" > "$TMP/docs/project/strategies/regulatory-strategy.md"
    # This file would win via the exact-match `user-needs.md` pattern...
    echo "# Conventionally-named user needs" \
        > "$TMP/docs/project/dhfs/fm-dhf/design-controls/user-needs/user-needs.md"
    # ...but this non-conventionally-named file declares the role explicitly,
    # and the frontmatter opt-in must outrank the filename pattern.
    cat > "$TMP/docs/project/dhfs/fm-dhf/design-controls/user-needs/legacy-un-doc.md" <<'EOF'
---
title: Legacy User Needs Document
canonical_role: user_needs
---

# Legacy user needs
EOF

    cat > "$TMP/project.yml" <<EOF
project:
  name: fixture-frontmatter-optin
dhfs:
  - leaf: fm-dhf
    path: docs/project/dhfs/fm-dhf
    role: system
EOF

    run_resolver "$TMP"
    local OUT
    OUT=$(read_json "$TMP" "fixture-frontmatter-optin")

    # user_needs should resolve to the frontmatter declarer, not user-needs.md
    local un_path
    un_path=$(echo "$OUT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['dhf_roles']['fm-dhf']['user_needs']['path'])")
    assert_path_endswith "case10.fm-dhf.user_needs.path" "legacy-un-doc.md" "$un_path"

    # ...and the winning entry must record the frontmatter match, not a glob pattern
    local un_pat
    un_pat=$(echo "$OUT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['dhf_roles']['fm-dhf']['user_needs']['matched_pattern'])")
    assert_eq "case10.fm-dhf.user_needs.matched_pattern" "frontmatter:canonical_role" "$un_pat"

    # no ambiguity_notes for user_needs — frontmatter wins cleanly, patterns not consulted
    local amb
    amb=$(echo "$OUT" | python3 -c "
import json, sys
d = json.load(sys.stdin)
print(len([n for n in d['ambiguity_notes']
           if n.get('dhf') == 'fm-dhf' and n.get('role') == 'user_needs']))
")
    assert_eq "case10.fm-dhf.user_needs.no_ambiguity" "0" "$amb"
}

# ──────────────────────────────────────────────────────────────────────
# Case 11: external-mode CLIENT-SLUG override (L3a `external:` block).
# The registry speaks generic role names; this client's vault uses its OWN
# slugs (none matching any registry external slug). The project.yml
# evidence_layout.layers[<canonical_role>].external mapping bridges them:
#   - fmea            → client slug `client-fmea-doc` (flat folder, default patterns)
#   - threat_model    → NESTED client path `security/client-threat-model`
#   - verification_protocols → external multi_file folder `client-test-cases`
# Asserts: client-slug resolution, governing_qms attaches from the taxonomy
# leaf, nested-path resolution, and external multi-file folder-pointer shape.
# ──────────────────────────────────────────────────────────────────────

case11() {
    local TMP
    TMP=$(mktemp -d)
    trap "rm -rf $TMP" RETURN

    mkdir -p "$TMP/docs/project/strategies"
    local POV="$TMP/docs/project/_mirror/widget/product-overview"
    mkdir -p "$POV/client-fmea-doc"
    mkdir -p "$POV/security/client-threat-model"
    mkdir -p "$POV/client-test-cases"
    mkdir -p "$TMP/docs/project/dhf-manifest"

    echo "# Reg" > "$TMP/docs/project/strategies/regulatory-strategy.md"
    # Client uses its OWN slugs — none match the generic registry external slugs.
    echo "# FMEA v1" > "$POV/client-fmea-doc/v1.0.0.md"
    echo "# Threat model v1 (nested)" > "$POV/security/client-threat-model/v1.0.0.md"
    echo "# TC v1" > "$POV/client-test-cases/v1.0.0.md"
    echo "# TC v2" > "$POV/client-test-cases/v2.0.0.md"

    cat > "$TMP/docs/project/_mirror/.taxonomy.yml" <<EOF
schema_version: 0.3
discovery_root: product-overview
mappings:
  client-fmea-doc:
    canonical_role: reliability
    governing_qms:
      forms: [FORM-000000001]
  client-threat-model:
    canonical_role: cybersecurity
  client-test-cases:
    canonical_role: verification
EOF

    cat > "$TMP/project.yml" <<EOF
project:
  name: fixture-client-slug-override
dhfs:
  - leaf: widget-dhf
    path: docs/project/_mirror/widget
    role: item
    dhf_organization: external
    taxonomy_path: docs/project/_mirror/.taxonomy.yml
evidence_layout:
  base: product-overview
  layers:
    fmea:
      external:
        taxonomy_folder: client-fmea-doc
    threat_model:
      external:
        taxonomy_folder: security/client-threat-model
    verification_protocols:
      external:
        multi_file: true
        taxonomy_folder: client-test-cases
EOF

    run_resolver "$TMP"
    local OUT
    OUT=$(read_json "$TMP" "fixture-client-slug-override")

    # 1. fmea resolves via the client slug (default external patterns) to v1.0.0.md
    local fmea_path
    fmea_path=$(echo "$OUT" | python3 -c "import json,sys; d=json.load(sys.stdin); v=d['dhf_roles']['widget-dhf']['fmea']; print(v['path'] if v else 'NULL')")
    assert_path_endswith "case11.fmea.client_slug" "client-fmea-doc/v1.0.0.md" "$fmea_path"

    # 2. fmea carries governing_qms resolved from the taxonomy leaf
    local fmea_gov
    fmea_gov=$(echo "$OUT" | python3 -c "import json,sys; d=json.load(sys.stdin); v=d['dhf_roles']['widget-dhf']['fmea']; print('YES' if v and v.get('governing_qms') else 'NO')")
    assert_eq "case11.fmea.governing_qms" "YES" "$fmea_gov"

    # 3. threat_model resolves via a NESTED client path
    local tm_path
    tm_path=$(echo "$OUT" | python3 -c "import json,sys; d=json.load(sys.stdin); v=d['dhf_roles']['widget-dhf']['threat_model']; print(v['path'] if v else 'NULL')")
    assert_path_endswith "case11.threat_model.nested_path" "security/client-threat-model/v1.0.0.md" "$tm_path"

    # 4. verification_protocols resolves as an external multi-file folder-pointer (count=2)
    local vp_count
    vp_count=$(echo "$OUT" | python3 -c "import json,sys; d=json.load(sys.stdin); v=d['dhf_roles']['widget-dhf']['verification_protocols']; print(v.get('file_count') if v else 'NULL')")
    assert_eq "case11.verification_protocols.multi_file_count" "2" "$vp_count"

    # 5. the multi-file entry is a folder pointer (has 'folder', no 'path')
    local vp_shape
    vp_shape=$(echo "$OUT" | python3 -c "import json,sys; d=json.load(sys.stdin); v=d['dhf_roles']['widget-dhf']['verification_protocols']; print('YES' if v and 'folder' in v and 'path' not in v else 'NO')")
    assert_eq "case11.verification_protocols.folder_pointer" "YES" "$vp_shape"
}

# ──────────────────────────────────────────────────────────────────────
# Drive
# ──────────────────────────────────────────────────────────────────────

echo "── discovery-index tests ──"
case1; echo "case1: clean resolution across mixed naming conventions"
case2; echo "case2: ambiguity — higher-ranked pattern wins, alternative recorded"
case3; echo "case3: L3 override via patterns_extra prepends to ranking"
case4; echo "case4: external_data roles count files and surface missing-folder gaps"
case5; echo "case5: external-mode DHF — nested sub-convention (folder/v*.md)"
case6; echo "case6: external-mode DHF — flat sub-convention (folder.md)"
case7; echo "case7: project-scoped multi_file role — folder pointer with file_count"
case8; echo "case8: per-dhf multi_file role (internal mode) — folder pointer"
case9; echo "case9: multi-match no-winner — ambiguity_notes + paired gap (was silently lost pre-fix)"
case10; echo "case10: frontmatter canonical_role: opt-in outranks filename patterns"
case11; echo "case11: external CLIENT-SLUG override — client slug, nested path, multi-file, governance"

echo
echo "Results: $PASS passed, $FAIL failed"
if [[ $FAIL -gt 0 ]]; then
    echo
    echo "Failures:"
    for e in "${ERRORS[@]}"; do
        echo "  - $e"
    done
    exit 1
fi
exit 0
