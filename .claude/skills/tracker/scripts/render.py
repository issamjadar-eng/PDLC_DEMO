#!/usr/bin/env python3
"""
Submission Tracker — HTML Dashboard Generator

Reads docs/project/submissions/submission-tracker.md and generates
docs/project/submissions/submission-tracker.html.

Preserves existing help content from the previous HTML when items haven't changed.
New items get auto-generated help content.

Usage: python3 render.py [--project-dir PATH]
  --project-dir  Project root directory (default: current working directory)
"""

import re
import sys
import os
from collections import OrderedDict, Counter
from datetime import date

def find_project_dir():
    """Find the project root by looking for CLAUDE.md."""
    d = os.getcwd()
    for _ in range(10):
        if os.path.exists(os.path.join(d, 'CLAUDE.md')):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            break
        d = parent
    return os.getcwd()

def _project_subtitle():
    """Build the tracker subtitle from project.yml when available.

    Reads project.name and project.regulatory_pathway from the project manifest.
    Uses regex rather than a YAML dependency to keep this script free of
    external packages. Falls back to a generic subtitle if project.yml is
    missing or unreadable.
    """
    try:
        path = os.path.join(find_project_dir(), 'project.yml')
        with open(path, 'r') as f:
            text = f.read()
        name_m = re.search(r'^\s{2}name:\s*(.+?)\s*$', text, re.MULTILINE)
        pathway_m = re.search(r'^\s{2}regulatory_pathway:\s*(.+?)\s*$', text, re.MULTILINE)
        name = name_m.group(1).strip() if name_m else None
        pathway = pathway_m.group(1).strip() if pathway_m else None
        if name and pathway:
            pathway_label = {
                '510k': '510(k)',
                'denovo': 'De Novo',
                'pma': 'PMA',
                'tbd': 'TBD',
            }.get(pathway.lower(), pathway)
            return f'{name} &mdash; {pathway_label} Submission Package'
        if name:
            return f'{name} &mdash; Submission Package'
    except (OSError, IOError):
        pass
    return 'Submission Package'

def sanitize_help_content(content):
    """Remove inline <table>/<tr>/<td>/<th> from help content.

    Help content lives inside a <td> of the outer item-table. Nested table
    elements confuse the browser's parser — it treats inner <tr> as rows of
    the outer table, breaking the DOM and hiding everything after the bad row.
    Strip all table-related tags (including unclosed/truncated ones).
    """
    if '<table' not in content and '<tr' not in content:
        return content
    # Remove table tags (both closed and unclosed)
    content = re.sub(r'</?table[^>]*>', '', content)
    content = re.sub(r'</?tbody[^>]*>', '', content)
    content = re.sub(r'</?thead[^>]*>', '', content)
    # Convert rows/cells to simple text with separators
    content = re.sub(r'<tr[^>]*>', '<p>', content)
    content = re.sub(r'</tr>', '</p>', content)
    content = re.sub(r'<t[hd][^>]*>', '', content)
    content = re.sub(r'</t[hd]>', ' | ', content)
    # Clean up trailing separators before </p>
    content = re.sub(r'\s*\|\s*</p>', '</p>', content)
    return content

def extract_help_content(html_path):
    """Extract existing help content by item ID from previous HTML."""
    help_content = {}
    if not os.path.exists(html_path):
        return help_content
    with open(html_path) as f:
        html = f.read()
    pattern = r'<td class="id-col">([^<]+)</td>.*?<tr class="help-row"[^>]*><td[^>]*>(.*?)</td>\s*</tr>'
    for m in re.finditer(pattern, html, re.DOTALL):
        content = sanitize_help_content(m.group(2).strip())
        help_content[m.group(1).strip()] = content
    return help_content

def parse_markdown(md_path):
    """Parse submission-tracker.md into structured items."""
    with open(md_path) as f:
        md = f.read()

    items = []
    current_section = ""
    current_section_num = ""
    is_eng = False

    for line in md.split('\n'):
        if line.startswith('### '):
            current_section = line.replace('### ', '').strip()
            m2 = re.match(r'(\d+\.\d+)', current_section)
            current_section_num = m2.group(1) if m2 else ""
            is_eng = current_section.startswith('4.')

        if is_eng:
            m = re.match(r'\| (ENG\w+) \| (.+?) \| (.+?) \| (.+?) \| (.+?) \| (.+?) \| (.+?) \|', line)
            if m:
                items.append({
                    'id': m.group(1).strip(), 'name': m.group(2).strip(),
                    'scope': m.group(3).strip(), 'effort': m.group(4).strip(),
                    'phase': m.group(5).strip(), 'ref': '', 'location': '',
                    'status': m.group(6).strip(), 'evidence': m.group(7).strip(),
                    'section': current_section, 'section_num': current_section_num,
                    'is_eng': True
                })
        else:
            m = re.match(r'\| ([A-Z][A-Z0-9]+[a-c]?) \| (.+?) \| (.+?) \| (.+?) \| (.+?) \| (.+?) \| (.+?) \| (.+?) \| (.+?) \|', line)
            if m:
                items.append({
                    'id': m.group(1).strip(), 'name': m.group(2).strip(),
                    'scope': m.group(3).strip(), 'effort': m.group(4).strip(),
                    'phase': m.group(5).strip(), 'ref': m.group(6).strip(),
                    'location': m.group(7).strip(), 'status': m.group(8).strip(),
                    'evidence': m.group(9).strip(), 'section': current_section,
                    'section_num': current_section_num, 'is_eng': False
                })

    return items


VALID_SCOPES = {'Device', 'Per-Module', 'Both'}
VALID_EFFORTS = {'Low', 'Med', 'High', 'V.High'}
VALID_PHASES = {'Filing', 'Filing (proto)', 'Release 1', 'Release 2', 'Release 3'}
VALID_STATUSES = {'Not Started', 'Partial', 'In Progress', 'Done'}


def validate(items, project_dir):
    """Validate tracker items for structural correctness and referential integrity."""
    warnings = []
    errors = []

    all_ids = {i['id'] for i in items}
    reg_ids = {i['id'] for i in items if not i['is_eng']}
    eng_items = [i for i in items if i['is_eng']]

    for item in items:
        iid = item['id']

        # Valid values
        if item['scope'] not in VALID_SCOPES:
            errors.append(f"{iid}: invalid Scope '{item['scope']}' — expected {VALID_SCOPES}")
        if item['effort'] not in VALID_EFFORTS:
            errors.append(f"{iid}: invalid Effort '{item['effort']}' — expected {VALID_EFFORTS}")
        if item['phase'] not in VALID_PHASES:
            errors.append(f"{iid}: invalid Phase '{item['phase']}' — expected {VALID_PHASES}")
        if item['status'] not in VALID_STATUSES:
            errors.append(f"{iid}: invalid Status '{item['status']}' — expected {VALID_STATUSES}")

    # Per-Module completeness: check a/b pairs
    # Exempt: MS* items (single module — Mgmt Services), standalone IDs (SW3, SW4)
    base_ids = set()
    for item in items:
        if not item['is_eng'] and item['scope'] == 'Per-Module' and not item['id'].startswith('MS'):
            base = re.sub(r'[a-c]$', '', item['id'])
            base_ids.add(base)

    for base in base_ids:
        has_a = f'{base}a' in all_ids
        has_b = f'{base}b' in all_ids
        has_standalone = base in all_ids and not has_a and not has_b
        if has_standalone:
            continue  # standalone ID like SW3, SW4 — no suffix convention
        if has_a and not has_b:
            warnings.append(f"{base}: has Intra-Op ({base}a) but missing Pre-Op ({base}b)")
        elif has_b and not has_a:
            warnings.append(f"{base}: has Pre-Op ({base}b) but missing Intra-Op ({base}a)")

    # Engineering gates referential integrity
    for item in eng_items:
        gates = item.get('evidence', '')
        if gates and gates != '—':
            for gate_id in re.split(r',\s*', gates):
                gate_id = gate_id.strip()
                if gate_id and gate_id not in reg_ids and gate_id not in all_ids:
                    warnings.append(f"{item['id']}: gates unknown ID '{gate_id}'")

    # Evidence path existence (spot check)
    for item in items:
        loc = item.get('location', '')
        if loc and loc != '' and not item['is_eng']:
            # Strip backticks and check if directory exists
            clean_loc = loc.strip('`').strip()
            full_path = os.path.join(project_dir, 'docs/project', clean_loc)
            if clean_loc and not os.path.exists(full_path) and not os.path.exists(os.path.join(project_dir, clean_loc)):
                pass  # Don't warn on locations — they're target paths, not existing files

    # Duplicate IDs
    seen = set()
    for item in items:
        if item['id'] in seen:
            errors.append(f"Duplicate ID: {item['id']}")
        seen.add(item['id'])

    return errors, warnings


def status_class(s):
    return 'done' if s == 'Done' else ('partial' if s in ('Partial', 'In Progress') else 'not-started')

def scope_class(s):
    return 'device' if 'Device' in s else ('both' if 'Both' in s else 'per-module')

def effort_class(e):
    return 'vhigh' if 'V.High' in e else ('high' if 'High' in e else ('med' if 'Med' in e else 'low'))

def phase_class(p):
    if 'proto' in p: return 'filing-proto'
    if 'Release 3' in p: return 'release-3'
    if 'Release 2' in p: return 'release-2'
    if 'Release 1' in p: return 'release-1'
    return 'filing'

def phase_label(p):
    if 'proto' in p: return 'Filing (proto)'
    for r in ['Release 3', 'Release 2', 'Release 1']:
        if r in p: return r
    return 'Filing'

def gen_help(item, help_content):
    """Generate help content for items without existing help."""
    iid = item['id']

    if iid.startswith('ENG'):
        gates = item['evidence']
        return (f'<div class="help-content"><span class="help-label">What is it?</span>'
                f'<p>{item["name"]}. This engineering capability must be in place before '
                f'the gated deliverables can be completed.</p>'
                f'<span class="help-label">Gates deliverables</span>'
                f'<p><code>{gates}</code></p></div>')

    parent_id = re.sub(r'[a-c]$', '', iid)
    if iid.endswith('b') and parent_id in help_content:
        return (f'<div class="help-content"><span class="help-label">What is it?</span>'
                f'<p>Pre-Op module version of {parent_id}. Phase: Filing (proto) &mdash; '
                f'prototype quality sufficient for filing. Production upgrade at Release 2.</p></div>')
    elif iid.endswith('a') and parent_id in help_content:
        return help_content[parent_id].replace(
            '<div class="help-content">',
            '<div class="help-content"><p><em>Intra-Op module version.</em></p>')
    elif iid.startswith('MS'):
        descs = {
            'MS1': 'Requirements for Management Services.',
            'MS2': 'Software Design Specification for Management Services sub-modules.',
            'MS3': 'MDDS Class I registration and listing with FDA.',
            'MS4': 'MFD impact assessment &mdash; how Management Services failures affect SaMD modules.',
            'MS5': 'SBOM for Management Services (Section 524B applies to full system).',
            'MS6': 'Basic V&amp;V for Management Services.',
            'MS7': 'Security controls documentation for Management Services.',
        }
        return (f'<div class="help-content"><span class="help-label">What is it?</span>'
                f'<p>{descs.get(iid, item["name"])}</p></div>')

    return (f'<div class="help-content"><span class="help-label">What is it?</span>'
            f'<p>{item["name"]}.</p></div>')


# Section metadata: id, help text, part number
SECTION_META = {
    '1.1 Administrative & Cover': ('cat-admin', 'Standard FDA paperwork. Mostly fill-in forms completed last.', 1),
    '1.2 Device Description & Intended Use': ('cat-device', 'Core description of what the device does. Foundation for predicate comparison and testing.', 1),
    '1.3 Predicate Comparison & Substantial Equivalence': ('cat-pred', 'Proving substantial equivalence to an already-cleared predicate device.', 1),
    '1.4 Software Documentation (Enhanced Level)': ('cat-sw', 'Software development documentation. Enhanced level required because Intra-Op failure could cause serious injury.', 1),
    '1.5 Risk Management': ('cat-risk', 'ISO 14971-based risk management. One of the most scrutinized sections.', 1),
    '1.6 Performance Testing & Clinical Data': ('cat-perf', 'Evidence the device performs as intended. Measurement accuracy, algorithm correctness.', 1),
    '1.7 Labeling': ('cat-label', 'User manuals, IFU, in-app text. Must match cleared indications.', 1),
    '1.8 Cybersecurity': ('cat-cyber', 'Mandatory since FDORA 2023. SBOM is statutory (Section 524B).', 1),
    '1.9 Human Factors & Usability': ('cat-hf', 'IEC 62366-1 usability engineering. Formative + summative studies.', 1),
    '1.10 Standards & Conformity': ('cat-std', 'Declarations of conformity to recognized consensus standards.', 1),
    '1.11 Design Controls (DHF Supporting)': ('cat-dc', 'Core DHF documents per 21 CFR 820.30. Parent DDP references child DDPs.', 1),
    '1.12 Q-Sub (Pre-Submission)': ('cat-qsub', 'Formal request to FDA for feedback before filing. Validates strategy.', 1),
    '2.1 PCCP Core Document': ('cat-pccp-core', 'The PCCP itself &mdash; modifications, protocols, impact assessments.', 2),
    '2.2 PCCP Integration into 510(k)': ('cat-pccp-int', 'How the PCCP is referenced throughout the submission.', 2),
    '2.3 PCCP-Specific Labeling': ('cat-pccp-label', 'Labeling requirements for PCCP devices.', 2),
    '2.4 PCCP Support Documentation': ('cat-pccp-support', 'Monitoring, rollback, surveillance, and deviation plans.', 2),
    '2.5 AI/ML-Specific Documentation (PCCP-Driven)': ('cat-ai', 'Required because PCCP covers AI-enabled modules. Per-model documentation.', 2),
    '2.6 PCCP Qualification Framework (Internal)': ('cat-pccp-qual', 'Internal frameworks for PCCP qualification decisions.', 2),
    '3.1 Management Services (Non-Submission)': ('cat-mgmt', 'MDDS/non-device items not in the 510(k) but required for compliance.', 3),
    '4.1 Requirements & Architecture': ('cat-eng-req', 'Requirements engineering and architecture design that gates SRS, SAD, and risk deliverables.', 4),
    '4.2 AI/ML Development': ('cat-eng-ai', 'AI model development, training data, and clinical dataset curation.', 4),
    '4.3 Software Development': ('cat-eng-sw', 'Production/prototype software, cloud infrastructure, device connectivity.', 4),
    '4.4 Testing & Tooling': ('cat-eng-test', 'Test infrastructure, build pipelines, CI/CD.', 4),
    '4.5 User Research & Cybersecurity': ('cat-eng-ux', 'Usability studies and cybersecurity implementation.', 4),
}

PART_DIVIDERS = {
    1: ('base', 'Base 510(k) Requirements'),
    2: ('pccp', 'PCCP Additive Requirements'),
    3: ('mgmt', 'Management Services (Non-Submission)'),
    4: ('eng', 'Engineering Prerequisites'),
}

CSS = '''<style>
:root{--bg:#0f172a;--surface:#1e293b;--surface2:#334155;--border:#475569;--text:#e2e8f0;--text-muted:#94a3b8;--accent:#38bdf8;--accent2:#818cf8;--green:#22c55e;--yellow:#eab308;--red:#ef4444;--orange:#f97316;--cyan:#06b6d4;--pink:#ec4899;--help-bg:#1a2744;--eng:#a78bfa}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:var(--bg);color:var(--text);line-height:1.6;padding:2rem}
.header{text-align:center;margin-bottom:2rem;padding-bottom:1.5rem;border-bottom:1px solid var(--border)}
.header h1{font-size:1.8rem;font-weight:700;color:var(--accent);margin-bottom:.3rem}
.header .subtitle{color:var(--text-muted);font-size:.95rem}
.header .timestamp{color:var(--text-muted);font-size:.8rem;margin-top:.5rem}
.controls{display:flex;gap:.4rem;justify-content:center;flex-wrap:wrap;margin-bottom:1.5rem}
.controls button{background:var(--surface);color:var(--text-muted);border:1px solid var(--border);border-radius:8px;padding:.35rem .7rem;font-size:.72rem;cursor:pointer;transition:all .2s}
.controls button:hover{background:var(--surface2);color:var(--text)}
.controls button.active{background:var(--accent);color:#000;border-color:var(--accent)}
.controls .sep{border-left:1px solid var(--border);height:24px;margin:0 .15rem}
.summary-grid{display:grid;grid-template-columns:repeat(5,1fr);gap:.8rem;margin-bottom:1.5rem}
.summary-card{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:1rem;text-align:center}
.summary-card .label{font-size:.7rem;text-transform:uppercase;letter-spacing:.05em;color:var(--text-muted);margin-bottom:.3rem}
.summary-card .number{font-size:2rem;font-weight:700}
.summary-card .detail{font-size:.72rem;color:var(--text-muted);margin-top:.2rem}
.summary-card.base .number{color:var(--accent)}.summary-card.pccp .number{color:var(--accent2)}
.summary-card.mgmt .number{color:var(--cyan)}.summary-card.eng .number{color:var(--eng)}
.summary-card.total .number{color:var(--text)}
.progress-section{margin-bottom:1.5rem}
.progress-row{display:flex;align-items:center;gap:.8rem;margin-bottom:.5rem}
.progress-label{width:100px;font-size:.78rem;font-weight:600;text-align:right;flex-shrink:0}
.progress-bar-container{flex:1;background:var(--surface);border-radius:8px;height:22px;overflow:hidden;display:flex;border:1px solid var(--border)}
.progress-segment{height:100%;display:flex;align-items:center;justify-content:center;font-size:.6rem;font-weight:600}
.progress-segment.done{background:var(--green);color:#000}.progress-segment.partial{background:var(--yellow);color:#000}
.progress-stats{width:60px;font-size:.75rem;color:var(--text-muted);text-align:left;flex-shrink:0}
.tier-divider{display:flex;align-items:center;gap:1rem;margin:2rem 0 1.2rem}
.tier-divider .line{flex:1;height:1px;background:var(--border)}
.tier-divider .badge{padding:.4rem 1rem;border-radius:20px;font-size:.75rem;font-weight:700;text-transform:uppercase;letter-spacing:.08em}
.tier-divider .badge.base{background:rgba(56,189,248,.15);color:var(--accent);border:1px solid rgba(56,189,248,.3)}
.tier-divider .badge.pccp{background:rgba(129,140,248,.15);color:var(--accent2);border:1px solid rgba(129,140,248,.3)}
.tier-divider .badge.mgmt{background:rgba(6,182,212,.15);color:var(--cyan);border:1px solid rgba(6,182,212,.3)}
.tier-divider .badge.eng{background:rgba(167,139,250,.15);color:var(--eng);border:1px solid rgba(167,139,250,.3)}
.category{background:var(--surface);border:1px solid var(--border);border-radius:10px;margin-bottom:.8rem;overflow:hidden}
.category-header{display:flex;align-items:center;justify-content:space-between;padding:.7rem 1rem;cursor:pointer;user-select:none;transition:background .2s}
.category-header:hover{background:var(--surface2)}
.category-header .cat-title{font-weight:600;font-size:.9rem;display:flex;align-items:center;gap:.5rem}
.category-header .cat-stats{display:flex;gap:.5rem;font-size:.75rem}
.cat-stats .stat{display:flex;align-items:center;gap:.25rem}
.stat .dot{width:7px;height:7px;border-radius:50%;display:inline-block}
.dot.done{background:var(--green)}.dot.partial{background:var(--yellow)}.dot.not-started{background:var(--border)}
.chevron{transition:transform .2s;color:var(--text-muted)}
.category.open .chevron{transform:rotate(180deg)}
.category.open .category-header{border-bottom:1px solid var(--border)}
.category-body{display:none;padding:0}.category.open .category-body{display:block}
.cat-help{background:var(--help-bg);border-bottom:1px solid var(--border);padding:.6rem 1rem;font-size:.82rem;color:var(--text-muted)}
.cat-help strong{color:var(--text)}
.item-table{width:100%;border-collapse:collapse;font-size:.78rem}
.item-table th{text-align:left;padding:.35rem .6rem;background:var(--surface2);color:var(--text-muted);font-weight:600;font-size:.67rem;text-transform:uppercase;letter-spacing:.04em}
.item-table td{padding:.35rem .6rem;border-top:1px solid rgba(71,85,105,.4);vertical-align:top}
.item-row{cursor:pointer;transition:background .15s}.item-row:hover td{background:rgba(56,189,248,.05)}
.help-row{display:none!important}.help-row.visible{display:table-row!important}
.help-row td{padding:.5rem .8rem .6rem 3rem;background:var(--help-bg);border-top:none}
.help-content{font-size:.8rem;color:var(--text-muted);line-height:1.5}
.help-content .help-label{font-size:.68rem;text-transform:uppercase;letter-spacing:.05em;color:var(--accent);font-weight:600;margin-top:.6rem;display:block}
.help-content .help-label:first-child{margin-top:0}
.help-content p{margin:.2rem 0}.help-content ul{margin:.2rem 0 .2rem 1.2rem}.help-content li{margin:.1rem 0}
.help-content code{font-size:.75rem;color:var(--cyan);background:rgba(6,182,212,.1);padding:.1rem .3rem;border-radius:3px}
.reg-quote{border-left:3px solid var(--accent2);background:rgba(129,140,248,.06);padding:.4rem .7rem;margin:.3rem 0;font-size:.75rem;font-style:italic;color:var(--text);border-radius:0 4px 4px 0}
.reg-quote .reg-src{display:block;font-style:normal;font-size:.68rem;color:var(--accent2);margin-top:.2rem}
.example-grid{display:grid;grid-template-columns:1fr 1fr;gap:.5rem;margin:.3rem 0}
.example-box{border:1px solid var(--border);border-radius:6px;padding:.4rem .6rem;font-size:.75rem}
.example-box.ai{border-color:rgba(236,72,153,.3);background:rgba(236,72,153,.05)}
.example-box.nonai{border-color:rgba(6,182,212,.3);background:rgba(6,182,212,.05)}
.example-box .ex-title{font-size:.65rem;text-transform:uppercase;letter-spacing:.04em;font-weight:600;margin-bottom:.2rem}
.example-box.ai .ex-title{color:var(--pink)}.example-box.nonai .ex-title{color:var(--cyan)}
.example-box ul{margin:0 0 0 1rem}.example-box li{margin:.1rem 0}
@media(max-width:768px){.example-grid{grid-template-columns:1fr}}
.info-hint{color:var(--accent);font-size:.68rem;margin-left:.3rem;opacity:.5;transition:opacity .2s}
.item-row:hover .info-hint{opacity:1}
.status-badge{display:inline-block;padding:.12rem .45rem;border-radius:10px;font-size:.67rem;font-weight:600;white-space:nowrap}
.status-badge.done{background:rgba(34,197,94,.15);color:var(--green)}
.status-badge.partial{background:rgba(234,179,8,.15);color:var(--yellow)}
.status-badge.not-started{background:rgba(71,85,105,.3);color:var(--text-muted)}
.scope-badge{display:inline-block;padding:.1rem .35rem;border-radius:10px;font-size:.62rem;font-weight:600;white-space:nowrap}
.scope-badge.device{background:rgba(56,189,248,.15);color:var(--accent)}
.scope-badge.per-module{background:rgba(6,182,212,.15);color:var(--cyan)}
.scope-badge.both{background:rgba(129,140,248,.15);color:var(--accent2)}
.effort-badge{display:inline-block;padding:.1rem .35rem;border-radius:10px;font-size:.62rem;font-weight:600;white-space:nowrap}
.effort-badge.low{background:rgba(34,197,94,.15);color:var(--green)}
.effort-badge.med{background:rgba(234,179,8,.15);color:var(--yellow)}
.effort-badge.high{background:rgba(249,115,22,.15);color:var(--orange)}
.effort-badge.vhigh{background:rgba(239,68,68,.15);color:var(--red)}
.phase-badge{display:inline-block;padding:.1rem .35rem;border-radius:10px;font-size:.62rem;font-weight:600;white-space:nowrap}
.phase-badge.filing{background:rgba(56,189,248,.2);color:var(--accent)}
.phase-badge.filing-proto{background:transparent;color:var(--accent);border:1px dashed rgba(56,189,248,.5)}
.phase-badge.release-1{background:rgba(34,197,94,.15);color:var(--green)}
.phase-badge.release-2{background:rgba(249,115,22,.15);color:var(--orange)}
.phase-badge.release-3{background:rgba(129,140,248,.15);color:var(--accent2)}
.id-col{width:48px;color:var(--text-muted);font-family:monospace;font-size:.72rem}
.status-col{width:85px}.ref-col{color:var(--text-muted);font-size:.75rem}
.evidence-col{font-size:.75rem;color:var(--text-muted)}
.gates-col{font-size:.72rem;color:var(--cyan);font-family:monospace}
.additive-callout{background:rgba(129,140,248,.08);border:1px solid rgba(129,140,248,.2);border-radius:10px;padding:.8rem 1.2rem;margin-bottom:1.2rem;font-size:.85rem;color:var(--text-muted)}
.additive-callout strong{color:var(--accent2)}
.legend{display:flex;gap:1rem;justify-content:center;flex-wrap:wrap;margin-bottom:1.2rem;font-size:.75rem;color:var(--text-muted)}
.legend-item{display:flex;align-items:center;gap:.3rem}
.scale-section{background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:1rem 1.2rem;margin-top:1.5rem}
.scale-section h3{font-size:.85rem;margin-bottom:.6rem;color:var(--accent)}
.scale-table{width:100%;border-collapse:collapse;font-size:.78rem}
.scale-table th{text-align:left;padding:.3rem .6rem;border-bottom:1px solid var(--border);color:var(--text-muted);font-size:.67rem;text-transform:uppercase}
.scale-table td{padding:.3rem .6rem;border-bottom:1px solid rgba(71,85,105,.3);vertical-align:top}
.footer{text-align:center;margin-top:1.5rem;padding-top:.8rem;border-top:1px solid var(--border);color:var(--text-muted);font-size:.72rem}
.help-mode-banner{background:rgba(56,189,248,.08);border:1px solid rgba(56,189,248,.2);border-radius:10px;padding:.5rem 1rem;margin-bottom:1.2rem;font-size:.82rem;color:var(--text-muted);text-align:center;display:none}
.help-mode-banner.visible{display:block}.help-mode-banner strong{color:var(--accent)}
@media(max-width:768px){
body{padding:.8rem}
.header h1{font-size:1.4rem}
.controls{gap:.3rem}
.controls button{padding:.3rem .5rem;font-size:.65rem}
.summary-grid{grid-template-columns:repeat(3,1fr);gap:.5rem}
.summary-card{padding:.6rem}
.summary-card .number{font-size:1.5rem}
.summary-card .detail{font-size:.6rem}
.progress-label{width:70px;font-size:.7rem}
.progress-stats{width:45px;font-size:.65rem}
.category-header{padding:.6rem .8rem}
.category-header .cat-title{font-size:.82rem}
.item-table{font-size:.68rem;display:block;overflow-x:auto;-webkit-overflow-scrolling:touch}
.item-table th,.item-table td{padding:.25rem .4rem;white-space:nowrap}
.item-table td:nth-child(2){white-space:normal;min-width:150px}
.help-row td{padding:.4rem .6rem .5rem 1rem;white-space:normal}
.help-content{font-size:.75rem}
.reg-quote{font-size:.7rem;padding:.3rem .5rem}
.example-grid{grid-template-columns:1fr}
.scope-badge,.effort-badge,.phase-badge,.status-badge{font-size:.58rem;padding:.08rem .3rem}
.scale-section{padding:.8rem}
.scale-table{font-size:.7rem;display:block;overflow-x:auto}
.tier-divider{margin:1.5rem 0 1rem}
.tier-divider .badge{font-size:.65rem;padding:.3rem .7rem}
.footer{font-size:.65rem}
.info-hint{display:none}
}
@media(max-width:480px){
.summary-grid{grid-template-columns:1fr 1fr}
.controls button{padding:.25rem .4rem;font-size:.6rem}
.item-table{font-size:.62rem}
}
</style>'''

JS = '''<script>
function toggle(id){document.getElementById(id).classList.toggle('open')}
function toggleAllSections(o){document.querySelectorAll('.category').forEach(function(c){if(o)c.classList.add('open');else c.classList.remove('open')})}
var allHelpVisible=false;
function toggleAllHelp(){allHelpVisible=!allHelpVisible;document.querySelectorAll('.help-row').forEach(function(h){if(allHelpVisible){h.classList.add('visible');h.previousElementSibling.classList.add('expanded')}else{h.classList.remove('visible');h.previousElementSibling.classList.remove('expanded')}});document.getElementById('btn-help').textContent=allHelpVisible?'Hide All Help':'Show All Help';document.getElementById('btn-help').classList.toggle('active',allHelpVisible);document.getElementById('help-banner').classList.toggle('visible',allHelpVisible)}
var filters={status:'all',scope:'all',phase:'all',part:'all'};
function setFilter(t,v){filters[t]=v;document.querySelectorAll('[id^="btn-'+t+'-"]').forEach(function(b){b.classList.remove('active')});document.getElementById('btn-'+t+'-'+v).classList.add('active');applyFilters()}
function applyFilters(){document.querySelectorAll('.item-row').forEach(function(r){var s=true;if(filters.status!=='all'&&r.getAttribute('data-status')!==filters.status)s=false;if(filters.scope!=='all'&&r.getAttribute('data-scope')!==filters.scope)s=false;if(filters.phase!=='all'&&r.getAttribute('data-phase')!==filters.phase)s=false;if(filters.part!=='all'&&r.getAttribute('data-part')!==filters.part)s=false;r.style.display=s?'':'none';var h=r.nextElementSibling;if(h&&h.classList.contains('help-row')){if(!s){h.classList.remove('visible');h.style.display='none';r.classList.remove('expanded')}else{h.style.display=''}}})}
document.addEventListener('click',function(e){var r=e.target.closest('.item-row');if(!r)return;var h=r.nextElementSibling;if(h&&h.classList.contains('help-row')){h.classList.toggle('visible');r.classList.toggle('expanded')}})
</script>'''


def render(project_dir):
    md_path = os.path.join(project_dir, 'docs/project/submissions/submission-tracker.md')
    html_path = os.path.join(project_dir, 'docs/project/submissions/submission-tracker.html')

    help_content = extract_help_content(html_path)
    items = parse_markdown(md_path)

    # Validate before rendering
    errors, warnings = validate(items, project_dir)
    if errors:
        print(f"  ERRORS ({len(errors)}):")
        for e in errors:
            print(f"    ✗ {e}")
    if warnings:
        print(f"  WARNINGS ({len(warnings)}):")
        for w in warnings:
            print(f"    ⚠ {w}")
    if errors:
        print("  Rendering anyway (errors should be fixed)")

    # Group by section
    sections = OrderedDict()
    for item in items:
        s = item['section']
        if s not in sections:
            sections[s] = []
        sections[s].append(item)

    # Stats
    reg_items = [i for i in items if not i['is_eng']]
    eng_items = [i for i in items if i['is_eng']]
    base = [i for i in reg_items if not i['id'].startswith(('PC', 'PI', 'PL', 'PS', 'AI', 'PQ', 'MS'))]
    pccp = [i for i in reg_items if i['id'].startswith(('PC', 'PI', 'PL', 'PS', 'AI', 'PQ'))]
    ms = [i for i in reg_items if i['id'].startswith('MS')]
    total = len(items)
    phase_counts = Counter(phase_class(i['phase']) for i in items)

    lines = []
    w = lines.append

    # Header
    w(f'<!DOCTYPE html>\n<html lang="en"><head><meta charset="UTF-8">'
      f'<meta name="viewport" content="width=device-width,initial-scale=1.0">'
      f'<title>Submission Package Tracker</title>')
    w(CSS)
    w('</head><body>')
    w(f'<div class="header"><h1>Submission Package Tracker</h1>'
      f'<div class="subtitle">{_project_subtitle()}</div>'
      f'<div class="timestamp">Generated: {date.today().isoformat()}</div></div>')

    # Controls
    w('<div class="controls">'
      '<button onclick="toggleAllSections(true)">Expand All</button>'
      '<button onclick="toggleAllSections(false)">Collapse All</button>'
      '<button onclick="toggleAllHelp()" id="btn-help">Show All Help</button>'
      '<span class="sep"></span>'
      '<button onclick="setFilter(\'status\',\'all\')" class="active" id="btn-status-all">All</button>'
      '<button onclick="setFilter(\'status\',\'not-started\')" id="btn-status-not-started">Not Started</button>'
      '<button onclick="setFilter(\'status\',\'partial\')" id="btn-status-partial">Partial</button>'
      '<button onclick="setFilter(\'status\',\'done\')" id="btn-status-done">Done</button>'
      '<span class="sep"></span>'
      '<button onclick="setFilter(\'scope\',\'all\')" class="active" id="btn-scope-all">All Scopes</button>'
      '<button onclick="setFilter(\'scope\',\'device\')" id="btn-scope-device">Device</button>'
      '<button onclick="setFilter(\'scope\',\'per-module\')" id="btn-scope-per-module">Per-Module</button>'
      '<button onclick="setFilter(\'scope\',\'both\')" id="btn-scope-both">Both</button>'
      '<span class="sep"></span>'
      '<button onclick="setFilter(\'phase\',\'all\')" class="active" id="btn-phase-all">All Phases</button>'
      '<button onclick="setFilter(\'phase\',\'filing\')" id="btn-phase-filing">Filing</button>'
      '<button onclick="setFilter(\'phase\',\'filing-proto\')" id="btn-phase-filing-proto">Filing (proto)</button>'
      '<button onclick="setFilter(\'phase\',\'release-1\')" id="btn-phase-release-1">Release 1</button>'
      '<button onclick="setFilter(\'phase\',\'release-2\')" id="btn-phase-release-2">Release 2</button>'
      '<span class="sep"></span>'
      '<button onclick="setFilter(\'part\',\'all\')" class="active" id="btn-part-all">All Parts</button>'
      '<button onclick="setFilter(\'part\',\'1\')" id="btn-part-1">Base</button>'
      '<button onclick="setFilter(\'part\',\'2\')" id="btn-part-2">PCCP</button>'
      '<button onclick="setFilter(\'part\',\'3\')" id="btn-part-3">Mgmt Svc</button>'
      '<button onclick="setFilter(\'part\',\'4\')" id="btn-part-4">Engineering</button>'
      '</div>')
    w('<div class="help-mode-banner" id="help-banner"><strong>Help mode active</strong> &mdash; click any row for details.</div>')

    # Summary cards
    def count_status(group, s): return sum(1 for i in group if i['status'] == s)
    w(f'<div class="summary-grid">'
      f'<div class="summary-card base"><div class="label">Base 510(k)</div><div class="number">{len(base)}</div>'
      f'<div class="detail">{count_status(base,"Partial")} partial &middot; {count_status(base,"Not Started")} not started</div></div>'
      f'<div class="summary-card pccp"><div class="label">PCCP Additive</div><div class="number">{len(pccp)}</div>'
      f'<div class="detail">{count_status(pccp,"Done")} done &middot; {count_status(pccp,"Not Started")} not started</div></div>'
      f'<div class="summary-card mgmt"><div class="label">Mgmt Services</div><div class="number">{len(ms)}</div>'
      f'<div class="detail">{len(ms)} not started</div></div>'
      f'<div class="summary-card eng"><div class="label">Engineering</div><div class="number">{len(eng_items)}</div>'
      f'<div class="detail">{count_status(eng_items,"Partial")} partial &middot; {count_status(eng_items,"Not Started")} not started</div></div>'
      f'<div class="summary-card total"><div class="label">Grand Total</div><div class="number">{total}</div>'
      f'<div class="detail">{phase_counts.get("filing",0)} Filing &middot; {phase_counts.get("filing-proto",0)} Proto &middot; '
      f'{phase_counts.get("release-1",0)} R1 &middot; {phase_counts.get("release-2",0)} R2</div></div></div>')

    # Legend
    w('<div class="legend">'
      '<div class="legend-item"><span class="dot done"></span> Done</div>'
      '<div class="legend-item"><span class="dot partial"></span> Partial</div>'
      '<div class="legend-item"><span class="dot not-started"></span> Not Started</div>'
      '<div class="legend-item" style="color:var(--accent)">&#9432; Click row for help</div></div>')

    # Progress bars
    for label, color, group in [('Base 510(k)', 'var(--accent)', base), ('PCCP Additive', 'var(--accent2)', pccp),
                                 ('Mgmt Services', 'var(--cyan)', ms), ('Engineering', 'var(--eng)', eng_items)]:
        d = count_status(group, 'Done')
        p = count_status(group, 'Partial') + count_status(group, 'In Progress')
        t = len(group)
        segs = ''
        if d: segs += f'<div class="progress-segment done" style="width:{round(d/t*100,1)}%">{d}</div>'
        if p: segs += f'<div class="progress-segment partial" style="width:{round(p/t*100,1)}%">{p}</div>'
        w(f'<div class="progress-section"><div class="progress-row">'
          f'<div class="progress-label" style="color:{color}">{label}</div>'
          f'<div class="progress-bar-container">{segs}</div>'
          f'<div class="progress-stats">{d}/{t}</div></div></div>')

    # Sections
    last_part = 0
    for sec_name, sec_items in sections.items():
        meta = SECTION_META.get(sec_name)
        if not meta:
            cat_id = 'cat-' + re.sub(r'[^a-z0-9]', '-', sec_name.lower())[:20]
            meta = (cat_id, '', 1)
        cat_id, help_text, part = meta

        if part != last_part:
            cls, lbl = PART_DIVIDERS[part]
            w(f'<div class="tier-divider"><div class="line"></div><div class="badge {cls}">{lbl}</div><div class="line"></div></div>')
            if part == 2:
                w('<div class="additive-callout"><strong>Additional work required ONLY because we include a PCCP.</strong></div>')
            last_part = part

        done_c = count_status(sec_items, 'Done')
        partial_c = count_status(sec_items, 'Partial') + count_status(sec_items, 'In Progress')
        ns_c = len(sec_items) - done_c - partial_c
        stats = ''
        if done_c: stats += f'<div class="stat"><span class="dot done"></span> {done_c}</div>'
        if partial_c: stats += f'<div class="stat"><span class="dot partial"></span> {partial_c}</div>'
        if ns_c: stats += f'<div class="stat"><span class="dot not-started"></span> {ns_c}</div>'

        is_eng_section = sec_items[0]['is_eng'] if sec_items else False
        if is_eng_section:
            header_row = '<tr><th class="id-col">ID</th><th>Prerequisite</th><th>Scope</th><th>Effort</th><th>Phase</th><th class="status-col">Status</th><th>Gates</th></tr>'
            colspan = 7
        else:
            header_row = '<tr><th class="id-col">ID</th><th>Deliverable</th><th>Scope</th><th>Effort</th><th>Phase</th><th>FDA Ref</th><th class="status-col">Status</th><th>Notes</th></tr>'
            colspan = 8

        w(f'<div class="category open" id="{cat_id}" data-part="{part}">'
          f'<div class="category-header" onclick="toggle(\'{cat_id}\')">'
          f'<div class="cat-title"><span class="chevron">&#9662;</span> {sec_name}</div>'
          f'<div class="cat-right"><div class="cat-stats">{stats}</div></div></div>'
          f'<div class="category-body">'
          f'<div class="cat-help"><strong>What is this?</strong> {help_text}</div>'
          f'<table class="item-table">{header_row}')

        for item in sec_items:
            sc = scope_class(item['scope']); ec = effort_class(item['effort'])
            stc = status_class(item['status']); pc = phase_class(item['phase'])
            pl = phase_label(item['phase'])

            if is_eng_section:
                gates = item['evidence'] if item['evidence'] != '—' else '&mdash;'
                w(f'<tr class="item-row" data-status="{stc}" data-scope="{sc}" data-phase="{pc}" data-part="{part}">'
                  f'<td class="id-col">{item["id"]}</td><td>{item["name"]} <span class="info-hint">&#9432;</span></td>'
                  f'<td><span class="scope-badge {sc}">{item["scope"]}</span></td>'
                  f'<td><span class="effort-badge {ec}">{item["effort"]}</span></td>'
                  f'<td><span class="phase-badge {pc}">{pl}</span></td>'
                  f'<td><span class="status-badge {stc}">{item["status"]}</span></td>'
                  f'<td class="gates-col">{gates}</td></tr>')
            else:
                ev = item['evidence'] if item['evidence'] != '—' else '&mdash;'
                w(f'<tr class="item-row" data-status="{stc}" data-scope="{sc}" data-phase="{pc}" data-part="{part}">'
                  f'<td class="id-col">{item["id"]}</td><td>{item["name"]} <span class="info-hint">&#9432;</span></td>'
                  f'<td><span class="scope-badge {sc}">{item["scope"]}</span></td>'
                  f'<td><span class="effort-badge {ec}">{item["effort"]}</span></td>'
                  f'<td><span class="phase-badge {pc}">{pl}</span></td>'
                  f'<td class="ref-col">{item["ref"]}</td>'
                  f'<td><span class="status-badge {stc}">{item["status"]}</span></td>'
                  f'<td class="evidence-col">{ev}</td></tr>')

            hc = help_content.get(item['id'], gen_help(item, help_content))
            w(f'<tr class="help-row"><td colspan="{colspan}">{hc}</td></tr>')

        w('</table></div></div>')

    # Scale sections
    w('<div class="scale-section"><h3>Effort Scale</h3><table class="scale-table">'
      '<tr><th>Level</th><th>Meaning</th><th>Examples</th></tr>'
      '<tr><td><span class="effort-badge low">Low</span></td><td>Template-driven; boilerplate</td><td>Cover letter, forms, version history</td></tr>'
      '<tr><td><span class="effort-badge med">Med</span></td><td>Bounded analysis; days</td><td>Predicate table, SOUP report, model card</td></tr>'
      '<tr><td><span class="effort-badge high">High</span></td><td>Cross-functional; weeks</td><td>SRS, risk plan, threat model, child SAD</td></tr>'
      '<tr><td><span class="effort-badge vhigh">V.High</span></td><td>Engineering data/testing; months</td><td>Performance studies, summative usability, dFMEA</td></tr>'
      '</table></div>')
    w('<div class="scale-section" style="margin-top:.8rem"><h3>Phase Scale</h3><table class="scale-table">'
      '<tr><th>Phase</th><th>When</th><th>Quality</th><th>Scope</th></tr>'
      '<tr><td><span class="phase-badge filing">Filing</span></td><td>510(k)+PCCP</td><td>Production</td><td>Device-level, Intra-Op, Mgmt Svc submission items</td></tr>'
      '<tr><td><span class="phase-badge filing-proto">Filing (proto)</span></td><td>510(k)+PCCP</td><td>Prototype</td><td>Pre-Op items</td></tr>'
      '<tr><td><span class="phase-badge release-1">Release 1</span></td><td>Intra-Op + Mgmt Svc launch</td><td>Production</td><td>Mgmt Svc non-submission items</td></tr>'
      '<tr><td><span class="phase-badge release-2">Release 2</span></td><td>Pre-Op commercial</td><td>Production</td><td>Pre-Op upgrades from prototype</td></tr>'
      '</table></div>')

    # Footer + JS
    w(f'<div class="footer">Source: <code>submission-tracker.md</code> &middot; '
      f'{total} items ({len(base)} base + {len(pccp)} PCCP + {len(ms)} Mgmt Svc + {len(eng_items)} engineering) &middot; '
      f'Click any row for help</div>')
    w(JS)
    w('</body></html>')

    with open(html_path, 'w') as f:
        f.write('\n'.join(lines))

    print(f"Generated {html_path}")
    print(f"  {total} items: {len(base)} base + {len(pccp)} PCCP + {len(ms)} Mgmt Svc + {len(eng_items)} engineering")
    print(f"  Status: {count_status(items, 'Done')} done, {count_status(items, 'Partial')} partial, {count_status(items, 'Not Started')} not started")
    print(f"  Help content: {len(help_content)} preserved, {total - len([i for i in items if i['id'] in help_content])} generated")


if __name__ == '__main__':
    project_dir = find_project_dir()
    for i, arg in enumerate(sys.argv[1:]):
        if arg == '--project-dir' and i + 2 < len(sys.argv):
            project_dir = sys.argv[i + 2]
    render(project_dir)
