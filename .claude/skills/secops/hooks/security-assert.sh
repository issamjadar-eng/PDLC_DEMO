#!/usr/bin/env bash
# =============================================================================
# security-assert.sh — SessionStart security posture check
#
# Runs 16 automated checks against project.yml security policy.
# Results cached in tasks/{person}/SECOPS.md with 7-day TTL.
# Silent exit on cache hit (zero overhead on happy path).
#
# Output: JSON to stdout (for Claude to parse and optionally spawn secops agent)
# Exit: Always 0 (security failures are warnings, never block session start)
# =============================================================================

# Consume hook JSON from stdin (Claude Code passes this to all hooks)
INPUT=$(cat)

# ---------------------------------------------------------------------------
# Resolve project directory
# ---------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
CONFIG_FILE="$PROJECT_DIR/project.yml"

if [[ ! -f "$CONFIG_FILE" ]]; then
    exit 0  # No project.yml — nothing to check
fi

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
has_command() { command -v "$1" &>/dev/null; }

# Portable timeout (macOS lacks `timeout`; use perl one-liner)
run_with_timeout() {
    local secs="$1"; shift
    perl -e 'alarm shift; exec @ARGV' "$secs" "$@" 2>/dev/null
}

# Extract a simple scalar value from project.yml (top-level or nested)
yaml_val() {
    grep -m1 "^[[:space:]]*$1:" "$CONFIG_FILE" 2>/dev/null | sed "s/.*$1:[[:space:]]*//" | xargs
}

# Extract all values from a YAML list section (lines starting with "- ")
# Usage: yaml_list "approved_skills" → one value per line
yaml_list() {
    local key="$1"
    local in_section=false
    while IFS= read -r line; do
        if echo "$line" | grep -q "^[[:space:]]*${key}:"; then
            in_section=true
            continue
        fi
        if $in_section; then
            # End of list: line is a new key (not indented with -)
            if echo "$line" | grep -q '^[[:space:]]*[a-z_]*:' && ! echo "$line" | grep -q '^[[:space:]]*-'; then
                break
            fi
            if echo "$line" | grep -q '^[[:space:]]*$\|^[[:space:]]*#'; then
                continue  # skip blanks and comments
            fi
            if echo "$line" | grep -q '^[[:space:]]*-'; then
                echo "$line" | sed 's/^[[:space:]]*-[[:space:]]*//' | sed 's/[[:space:]]*#.*//' | sed 's/^"//' | sed 's/"$//' | tr -d '\r' | xargs
            fi
        fi
    done < "$CONFIG_FILE"
}

# Extract github usernames from team.active section
yaml_team_github() {
    local section="$1"  # "active" or "inactive"
    local in_section=false
    while IFS= read -r line; do
        if echo "$line" | grep -q "^[[:space:]]*${section}:"; then
            in_section=true
            continue
        fi
        if $in_section; then
            if echo "$line" | grep -q '^[a-z#]'; then
                in_section=false
                continue
            fi
            if echo "$line" | grep -q '^[[:space:]]*github:'; then
                echo "$line" | sed 's/.*github:[[:space:]]*//' | xargs
            fi
        fi
    done < "$CONFIG_FILE"
}

# Extract task_folder for a given github username
yaml_task_folder_for() {
    local target_github="$1"
    local found_user=false
    local in_active=false
    while IFS= read -r line; do
        if echo "$line" | grep -q '^[[:space:]]*active:'; then
            in_active=true
            continue
        fi
        if $in_active && echo "$line" | grep -q '^[a-z#]'; then
            in_active=false
            continue
        fi
        if $in_active; then
            if echo "$line" | grep -q "^[[:space:]]*github:[[:space:]]*${target_github}[[:space:]]*$"; then
                found_user=true
            fi
            if $found_user && echo "$line" | grep -q '^[[:space:]]*task_folder:'; then
                echo "$line" | sed 's/.*task_folder:[[:space:]]*//' | xargs
                return 0
            fi
            # Reset if we hit a new list item without finding task_folder
            if $found_user && echo "$line" | grep -q '^[[:space:]]*-[[:space:]]*name:'; then
                found_user=false
            fi
        fi
    done < "$CONFIG_FILE"
}

# ---------------------------------------------------------------------------
# Read config
# ---------------------------------------------------------------------------
REPO=$(yaml_val "repo")
CHECK_TTL=$(yaml_val "check_ttl_days")
[[ -z "$CHECK_TTL" ]] && CHECK_TTL=7

# ---------------------------------------------------------------------------
# Identify current user
#
# Primary path: resolve via the shared roster-matcher helper (git-email +
# fuzzy heuristics, no network). Emits JSON with task_folder + name + github
# + email. This replaces ~90 lines of hand-rolled YAML parsing (the old
# yaml_task_folder_for + email-match loop) with a single tested resolver.
#
# Fallback path: if resolve_user.py doesn't match (unusual — e.g., missing
# helper on an older clone), fall back to the legacy gh-api-user → yaml
# lookup. This keeps the hook working during a partial rollout.
# ---------------------------------------------------------------------------
GH_AVAILABLE=false
GH_USER=""
TASK_FOLDER=""
FULL_NAME=""

RESOLVER="$PROJECT_DIR/.claude/skills/shared/scripts/resolve_user.py"
if [[ -f "$RESOLVER" ]] && has_command python3 && has_command jq; then
    resolve_json=$(python3 "$RESOLVER" 2>/dev/null || true)
    if [[ -n "$resolve_json" ]]; then
        unresolved=$(echo "$resolve_json" | jq -r '.unresolved // false' 2>/dev/null || echo "true")
        if [[ "$unresolved" == "false" ]]; then
            TASK_FOLDER=$(echo "$resolve_json" | jq -r '.task_folder // ""' 2>/dev/null || true)
            FULL_NAME=$(echo "$resolve_json" | jq -r '.name // ""' 2>/dev/null || true)
        fi
    fi
fi

if has_command gh && has_command jq; then
    if run_with_timeout 3 gh auth status &>/dev/null 2>&1; then
        GH_AVAILABLE=true
        GH_USER=$(run_with_timeout 3 gh api /user --jq '.login' 2>/dev/null || true)
    fi
fi

# Legacy fallback — only used if resolve_user.py failed to match.
if [[ -z "$TASK_FOLDER" && -n "$GH_USER" ]]; then
    TASK_FOLDER=$(yaml_task_folder_for "$GH_USER")
fi

if [[ -z "$TASK_FOLDER" ]]; then
    # Can't identify user — skip silently
    exit 0
fi

SECOPS_FILE="$PROJECT_DIR/tasks/$TASK_FOLDER/SECOPS.md"

# ---------------------------------------------------------------------------
# TTL check — fast path
# ---------------------------------------------------------------------------
if [[ -f "$SECOPS_FILE" ]]; then
    last_check_date=$(grep -m1 "^- Date:" "$SECOPS_FILE" 2>/dev/null | sed 's/^- Date:[[:space:]]*//' | xargs)
    if [[ -n "$last_check_date" ]]; then
        # Calculate days since last check
        if has_command python3; then
            days_ago=$(python3 -c "
from datetime import datetime
try:
    d = datetime.strptime('$last_check_date', '%Y-%m-%d')
    print((datetime.now() - d).days)
except:
    print(999)
" 2>/dev/null)
        else
            days_ago=999
        fi

        if [[ "$days_ago" -lt "$CHECK_TTL" ]]; then
            exit 0  # Cache hit — silent exit
        fi
    fi
fi

# ---------------------------------------------------------------------------
# Run checks
# ---------------------------------------------------------------------------
declare -a CHECK_RESULTS=()
CRITICAL_FAILS=0
HIGH_FAILS=0
WARNINGS=0
PASSES=0
SKIPS=0
TODAY=$(date +%Y-%m-%d)

# Helper: record a check result
# Usage: record_check ID NAME SEVERITY RESULT [NOTE]
record_check() {
    local id="$1" name="$2" severity="$3" result="$4" note="${5:-}"
    CHECK_RESULTS+=("{\"id\":$id,\"name\":\"$name\",\"severity\":\"$severity\",\"result\":\"$result\",\"note\":\"$note\"}")
    case "$result" in
        PASS) ((PASSES++)) ;;
        FAIL)
            case "$severity" in
                Critical) ((CRITICAL_FAILS++)) ;;
                High) ((HIGH_FAILS++)) ;;
                *) ((WARNINGS++)) ;;
            esac
            ;;
        WARN) ((WARNINGS++)) ;;
        SKIP) ((SKIPS++)) ;;
    esac
}

# --- Check 2: Git email on approved domain ---
git_email=$(git config user.email 2>/dev/null || true)
if [[ -n "$git_email" ]]; then
    email_domain="${git_email##*@}"
    approved_domains=$(yaml_list "approved_email_domains")
    domain_match=false
    while IFS= read -r domain; do
        [[ "$email_domain" == "$domain" ]] && domain_match=true
    done <<< "$approved_domains"
    if $domain_match; then
        record_check 2 "Git email domain" "Critical" "PASS"
    else
        record_check 2 "Git email domain" "Critical" "FAIL" "Domain '$email_domain' not in approved list"
    fi
else
    record_check 2 "Git email domain" "Critical" "FAIL" "No git email configured"
fi

# --- Check 7: .gitignore has required patterns ---
gitignore="$PROJECT_DIR/.gitignore"
if [[ -f "$gitignore" ]]; then
    missing_patterns=()
    while IFS= read -r pattern; do
        [[ -z "$pattern" ]] && continue
        # Strip leading/trailing wildcards but keep path separators
        # "credentials*" → "credentials", "**/PHI/**" → "PHI", "**/patient*data*" → "patient"
        base_pattern=$(echo "$pattern" | sed 's/^\*\*\///' | sed 's/\/\*\*$//' | sed 's/\*.*$//' | sed 's/^\*//')
        if ! grep -qF "$base_pattern" "$gitignore" 2>/dev/null; then
            missing_patterns+=("$pattern")
        fi
    done <<< "$(yaml_list "required_gitignore_patterns")"
    if [[ ${#missing_patterns[@]} -eq 0 ]]; then
        record_check 7 ".gitignore patterns" "High" "PASS"
    else
        record_check 7 ".gitignore patterns" "High" "FAIL" "Missing: ${missing_patterns[*]}"
    fi
else
    record_check 7 ".gitignore patterns" "High" "FAIL" "No .gitignore found"
fi

# --- Check 8: SSH key exists ---
if [[ -f "$HOME/.ssh/id_ed25519" ]] || [[ -f "$HOME/.ssh/id_rsa" ]]; then
    record_check 8 "SSH key exists" "Medium" "PASS"
else
    record_check 8 "SSH key exists" "Medium" "WARN" "No SSH key found"
fi

# --- Check 9: Skills on approved list ---
approved_skills=$(yaml_list "approved_skills")
unknown_skills=()
for skill_dir in "$PROJECT_DIR"/.claude/skills/*/; do
    [[ -d "$skill_dir" ]] || continue
    skill_name=$(basename "$skill_dir")
    [[ "$skill_name" == "shared" ]] && continue  # shared/ is not a skill
    found=false
    while IFS= read -r approved; do
        [[ "$skill_name" == "$approved" ]] && found=true
    done <<< "$approved_skills"
    if ! $found; then
        unknown_skills+=("$skill_name")
    fi
done
if [[ ${#unknown_skills[@]} -eq 0 ]]; then
    record_check 9 "Skills allowlist" "Low" "PASS"
else
    record_check 9 "Skills allowlist" "Low" "WARN" "Unknown: ${unknown_skills[*]}"
fi

# --- Check 10: Local MCPs on approved list ---
# Check .claude/settings.json and ~/.claude/settings.json for mcpServers
local_mcps=()
for settings_file in "$PROJECT_DIR/.claude/settings.json" "$HOME/.claude/settings.json"; do
    if [[ -f "$settings_file" ]] && has_command jq; then
        while IFS= read -r mcp; do
            [[ -n "$mcp" ]] && local_mcps+=("$mcp")
        done < <(jq -r '.mcpServers // {} | keys[]' "$settings_file" 2>/dev/null)
    fi
done
if [[ ${#local_mcps[@]} -eq 0 ]]; then
    record_check 10 "Local MCPs allowlist" "Low" "PASS" "No local MCPs configured"
else
    approved_mcps=$(yaml_list "approved_mcps")
    unknown_mcps=()
    for mcp in "${local_mcps[@]}"; do
        found=false
        while IFS= read -r approved; do
            [[ "$mcp" == "$approved" ]] && found=true
        done <<< "$approved_mcps"
        $found || unknown_mcps+=("$mcp")
    done
    if [[ ${#unknown_mcps[@]} -eq 0 ]]; then
        record_check 10 "Local MCPs allowlist" "Low" "PASS"
    else
        record_check 10 "Local MCPs allowlist" "Low" "WARN" "Unknown: ${unknown_mcps[*]}"
    fi
fi

# --- Check 11: Plugins on approved list ---
if [[ -f "$PROJECT_DIR/.claude/settings.json" ]] && has_command jq; then
    enabled_plugins=$(jq -r '.enabledPlugins // {} | keys[]' "$PROJECT_DIR/.claude/settings.json" 2>/dev/null)
    if [[ -n "$enabled_plugins" ]]; then
        approved_plugins=$(yaml_list "approved_plugins")
        unknown_plugins=()
        while IFS= read -r plugin; do
            [[ -z "$plugin" ]] && continue
            found=false
            while IFS= read -r approved; do
                [[ "$plugin" == "$approved" ]] && found=true
            done <<< "$approved_plugins"
            $found || unknown_plugins+=("$plugin")
        done <<< "$enabled_plugins"
        if [[ ${#unknown_plugins[@]} -eq 0 ]]; then
            record_check 11 "Plugins allowlist" "Low" "PASS"
        else
            record_check 11 "Plugins allowlist" "Low" "WARN" "Unknown: ${unknown_plugins[*]}"
        fi
    else
        record_check 11 "Plugins allowlist" "Low" "PASS" "No plugins enabled"
    fi
else
    record_check 11 "Plugins allowlist" "Low" "SKIP" "No settings.json or jq"
fi

# --- Check 13: Active members have task folders ---
missing_folders=()
while IFS= read -r line; do
    if echo "$line" | grep -q '^[[:space:]]*task_folder:'; then
        tf=$(echo "$line" | sed 's/.*task_folder:[[:space:]]*//' | xargs)
        if [[ ! -f "$PROJECT_DIR/tasks/$tf/000-index.md" ]]; then
            missing_folders+=("$tf")
        fi
    fi
done < <(sed -n '/active:/,/inactive:/p' "$CONFIG_FILE")
if [[ ${#missing_folders[@]} -eq 0 ]]; then
    record_check 13 "Task folders exist" "High" "PASS"
else
    record_check 13 "Task folders exist" "High" "FAIL" "Missing: ${missing_folders[*]}"
fi

# --- Check 14: No orphan task folders ---
orphan_folders=()
active_folders=$(sed -n '/active:/,/inactive:/p' "$CONFIG_FILE" | grep 'task_folder:' | sed 's/.*task_folder:[[:space:]]*//' | xargs -n1)
for task_dir in "$PROJECT_DIR"/tasks/*/; do
    [[ -d "$task_dir" ]] || continue
    folder_name=$(basename "$task_dir")
    found=false
    for af in $active_folders; do
        [[ "$folder_name" == "$af" ]] && found=true
    done
    $found || orphan_folders+=("$folder_name")
done
if [[ ${#orphan_folders[@]} -eq 0 ]]; then
    record_check 14 "No orphan task folders" "High" "PASS"
else
    record_check 14 "No orphan task folders" "High" "FAIL" "Orphans: ${orphan_folders[*]}"
fi

# ---------------------------------------------------------------------------
# Network-dependent checks (skip if gh unavailable)
# ---------------------------------------------------------------------------
if $GH_AVAILABLE && [[ -n "$GH_USER" ]]; then

    # --- Check 1: GitHub 2FA enabled ---
    tfa=$(run_with_timeout 3 gh api /user --jq '.two_factor_authentication // false' 2>/dev/null || echo "error")
    if [[ "$tfa" == "true" ]]; then
        record_check 1 "GitHub 2FA" "Critical" "PASS"
    elif [[ "$tfa" == "error" ]]; then
        record_check 1 "GitHub 2FA" "Critical" "SKIP" "API call failed"
    else
        record_check 1 "GitHub 2FA" "Critical" "FAIL" "2FA not enabled on GitHub"
    fi

    # --- Check 3: GitHub email on approved domain ---
    gh_emails=$(run_with_timeout 3 gh api /user/emails --jq '.[].email' 2>/dev/null || true)
    if [[ -n "$gh_emails" ]]; then
        gh_domain_match=false
        while IFS= read -r email; do
            [[ -z "$email" ]] && continue
            domain="${email##*@}"
            while IFS= read -r approved; do
                [[ "$domain" == "$approved" ]] && gh_domain_match=true
            done <<< "$approved_domains"
        done <<< "$gh_emails"
        if $gh_domain_match; then
            record_check 3 "GitHub email domain" "Critical" "PASS"
        else
            record_check 3 "GitHub email domain" "Critical" "FAIL" "No verified email on approved domain"
        fi
    else
        record_check 3 "GitHub email domain" "Critical" "SKIP" "Could not fetch emails"
    fi

    # --- Check 4: User in project.yml active roster ---
    active_users=$(yaml_team_github "active")
    user_in_roster=false
    while IFS= read -r u; do
        [[ "$GH_USER" == "$u" ]] && user_in_roster=true
    done <<< "$active_users"
    if $user_in_roster; then
        record_check 4 "User in active roster" "Critical" "PASS"
    else
        record_check 4 "User in active roster" "Critical" "FAIL" "'$GH_USER' not in project.yml active roster"
    fi

    # --- Check 5: Repo is private ---
    if [[ -n "$REPO" ]]; then
        is_private=$(run_with_timeout 3 gh api "repos/$REPO" --jq '.private' 2>/dev/null || echo "error")
        if [[ "$is_private" == "true" ]]; then
            record_check 5 "Repo is private" "Critical" "PASS"
        elif [[ "$is_private" == "error" ]]; then
            record_check 5 "Repo is private" "Critical" "SKIP" "API call failed"
        else
            record_check 5 "Repo is private" "Critical" "FAIL" "Repository is public"
        fi
    else
        record_check 5 "Repo is private" "Critical" "SKIP" "No repo in project.yml"
    fi

    # --- Check 6: Branch protection on main ---
    if [[ -n "$REPO" ]]; then
        bp_status=$(run_with_timeout 3 gh api "repos/$REPO/branches/main/protection" --jq '.url' 2>/dev/null && echo "ok" || echo "none")
        if [[ "$bp_status" == *"ok"* ]]; then
            record_check 6 "Branch protection" "High" "PASS"
        else
            record_check 6 "Branch protection" "High" "WARN" "No branch protection on main"
        fi
    else
        record_check 6 "Branch protection" "High" "SKIP" "No repo in project.yml"
    fi

    # --- Check 12: Every collaborator in roster ---
    if [[ -n "$REPO" ]]; then
        collaborators=$(run_with_timeout 5 gh api "repos/$REPO/collaborators" --jq '.[].login' 2>/dev/null || true)
        if [[ -n "$collaborators" ]]; then
            unauthorized=()
            while IFS= read -r collab; do
                [[ -z "$collab" ]] && continue
                found=false
                while IFS= read -r active; do
                    [[ "$collab" == "$active" ]] && found=true
                done <<< "$active_users"
                $found || unauthorized+=("$collab")
            done <<< "$collaborators"
            if [[ ${#unauthorized[@]} -eq 0 ]]; then
                record_check 12 "Collaborators in roster" "Critical" "PASS"
            else
                record_check 12 "Collaborators in roster" "Critical" "FAIL" "Unauthorized: ${unauthorized[*]}"
            fi
        else
            record_check 12 "Collaborators in roster" "Critical" "SKIP" "Could not fetch collaborators"
        fi
    fi

    # --- Check 15: Inactive members have no repo access ---
    inactive_users=$(yaml_team_github "inactive")
    if [[ -n "$inactive_users" && -n "$collaborators" ]]; then
        stale_access=()
        while IFS= read -r inactive; do
            [[ -z "$inactive" ]] && continue
            while IFS= read -r collab; do
                [[ "$inactive" == "$collab" ]] && stale_access+=("$inactive")
            done <<< "$collaborators"
        done <<< "$inactive_users"
        if [[ ${#stale_access[@]} -eq 0 ]]; then
            record_check 15 "No inactive access" "Critical" "PASS"
        else
            record_check 15 "No inactive access" "Critical" "FAIL" "Stale: ${stale_access[*]}"
        fi
    else
        record_check 15 "No inactive access" "Critical" "PASS" "No inactive members or no collaborator data"
    fi

    # --- Check 16: Inactive members have no active tasks ---
    if [[ -n "$inactive_users" ]]; then
        active_task_issues=()
        while IFS= read -r inactive_gh; do
            [[ -z "$inactive_gh" ]] && continue
            inactive_folder=$(yaml_task_folder_for "$inactive_gh")
            [[ -z "$inactive_folder" ]] && continue
            index_file="$PROJECT_DIR/tasks/$inactive_folder/000-index.md"
            if [[ -f "$index_file" ]]; then
                # Check if Active table has any rows (non-header, non-separator)
                active_count=$(sed -n '/^## Active/,/^## /p' "$index_file" | grep -c '^|' | head -1)
                # Subtract 2 for header + separator
                active_count=$((active_count - 2))
                if [[ $active_count -gt 0 ]]; then
                    active_task_issues+=("$inactive_folder")
                fi
            fi
        done <<< "$inactive_users"
        if [[ ${#active_task_issues[@]} -eq 0 ]]; then
            record_check 16 "No inactive active tasks" "High" "PASS"
        else
            record_check 16 "No inactive active tasks" "High" "FAIL" "Active tasks: ${active_task_issues[*]}"
        fi
    else
        record_check 16 "No inactive active tasks" "High" "PASS" "No inactive members"
    fi

else
    # gh not available — skip all network checks
    record_check 1 "GitHub 2FA" "Critical" "SKIP" "gh CLI not available"
    record_check 3 "GitHub email domain" "Critical" "SKIP" "gh CLI not available"
    record_check 4 "User in active roster" "Critical" "SKIP" "gh CLI not available"
    record_check 5 "Repo is private" "Critical" "SKIP" "gh CLI not available"
    record_check 6 "Branch protection" "High" "SKIP" "gh CLI not available"
    record_check 12 "Collaborators in roster" "Critical" "SKIP" "gh CLI not available"
    record_check 15 "No inactive access" "Critical" "SKIP" "gh CLI not available"
    record_check 16 "No inactive active tasks" "High" "SKIP" "gh CLI not available"
fi

# ---------------------------------------------------------------------------
# Determine overall result
# ---------------------------------------------------------------------------
TOTAL=$((PASSES + CRITICAL_FAILS + HIGH_FAILS + WARNINGS + SKIPS))
if [[ $CRITICAL_FAILS -gt 0 ]]; then
    OVERALL="FAIL"
elif [[ $HIGH_FAILS -gt 0 ]]; then
    OVERALL="WARN"
else
    OVERALL="PASS"
fi

# ---------------------------------------------------------------------------
# Write/update SECOPS.md
# ---------------------------------------------------------------------------
# FULL_NAME is already populated by resolve_user.py in the happy path;
# fall back to TASK_FOLDER if the legacy gh-api path was taken.
[[ -z "$FULL_NAME" ]] && FULL_NAME="$TASK_FOLDER"

NEXT_CHECK=$(python3 -c "
from datetime import datetime, timedelta
print((datetime.now() + timedelta(days=$CHECK_TTL)).strftime('%Y-%m-%d'))
" 2>/dev/null || echo "unknown")

# Build check history entry
FAILURE_LIST=""
for result in "${CHECK_RESULTS[@]}"; do
    r=$(echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['result'])" 2>/dev/null || true)
    n=$(echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['name'])" 2>/dev/null || true)
    note=$(echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('note',''))" 2>/dev/null || true)
    if [[ "$r" == "FAIL" || "$r" == "WARN" ]]; then
        [[ -n "$FAILURE_LIST" ]] && FAILURE_LIST+=", "
        FAILURE_LIST+="$n"
        [[ -n "$note" ]] && FAILURE_LIST+=" ($note)"
    fi
done
[[ -z "$FAILURE_LIST" ]] && FAILURE_LIST="—"

cat > "$SECOPS_FILE" << SECOPSEOF
# Security Posture — $FULL_NAME

## Last Check
- Date: $TODAY
- Result: $OVERALL
- Checks passed: $PASSES/$TOTAL automated
- Skipped: $SKIPS (gh unavailable or API timeout)
- Next check due: $NEXT_CHECK

## Attestations

| Check | Last Confirmed | Expires |
|-------|---------------|---------|
| Claude training opt-out | — | — |
| Claude account 2FA | — | — |
| Connected integrations reviewed | — | — |

## Allowlist Warnings

| Date | Type | Name | Status |
|------|------|------|--------|
| — | — | — | No warnings |

## Check History

| Date | Result | Failures | Notes |
|------|--------|----------|-------|
| $TODAY | $OVERALL | $FAILURE_LIST | Automated check |
SECOPSEOF

# ---------------------------------------------------------------------------
# Output JSON for Claude
# ---------------------------------------------------------------------------
CHECKS_JSON=$(IFS=,; echo "${CHECK_RESULTS[*]}")

cat << JSONEOF
{
  "result": "$OVERALL",
  "critical_failures": $CRITICAL_FAILS,
  "high_failures": $HIGH_FAILS,
  "warnings": $WARNINGS,
  "passes": $PASSES,
  "skips": $SKIPS,
  "total": $TOTAL,
  "checks": [$CHECKS_JSON],
  "secops_file": "tasks/$TASK_FOLDER/SECOPS.md",
  "message": "Security posture: $PASSES/$TOTAL passed, $CRITICAL_FAILS critical, $HIGH_FAILS high, $WARNINGS warnings, $SKIPS skipped. See tasks/$TASK_FOLDER/SECOPS.md"
}
JSONEOF

exit 0
