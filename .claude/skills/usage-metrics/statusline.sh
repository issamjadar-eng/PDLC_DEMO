#!/bin/bash
# usage-metrics · Claude Code status line (skill-owned source of truth).
# Installed by `setup` as a symlink at .claude/statusline.sh and wired via the
# settings.json "statusLine" block, so the whole team inherits it with no
# per-person setup.
#
# Renders: [model] <bar> IN/SIZE ctx · ↑OUT resp · $cost
#   e.g.   [Opus 4.8] ▓▓░░░░░░░░ 45.2k/1M ctx · ↑3.1k resp · $0.42
#
# Reads the status JSON from stdin. Field reference + SEMANTICS:
#   .model.display_name                 -> model label (trailing "(...)" suffix stripped)
#   .context_window.used_percentage     -> context-window fullness 0..100 (drives the bar)
#   .context_window.total_input_tokens  -> tokens CURRENTLY in the context window (a live
#                                          snapshot, not a session sum) — includes cache r/w
#   .context_window.total_output_tokens -> output tokens of the MOST RECENT response only
#   .context_window.context_window_size -> max context (200000 | 1000000)
#   .cost.total_cost_usd                -> CUMULATIVE session cost estimate
# So "45.2k/1M ctx" = context holds 45.2k of 1M; "↑3.1k resp" = last response was 3.1k out;
# "$0.42" = session-to-date cost. NOTE: before Claude Code v2.1.132 the context token fields
# were cumulative session totals, not a snapshot — older builds will read differently.
# Older builds that omit .context_window.* degrade gracefully (model + cost only).

input=$(cat)

# jq missing -> emit a minimal line rather than nothing.
if ! command -v jq >/dev/null 2>&1; then
  echo "[claude] (install jq for token/context usage)"
  exit 0
fi

MODEL=$(printf '%s' "$input" | jq -r '.model.display_name // "claude"')
PCT=$(printf '%s'   "$input" | jq -r '.context_window.used_percentage    // empty')
TIN=$(printf '%s'   "$input" | jq -r '.context_window.total_input_tokens  // empty')
TOUT=$(printf '%s'  "$input" | jq -r '.context_window.total_output_tokens // empty')
SIZE=$(printf '%s'  "$input" | jq -r '.context_window.context_window_size // empty')
COST=$(printf '%s'  "$input" | jq -r '.cost.total_cost_usd // empty')

# Drop a trailing parenthetical from the model label, e.g. "Opus 4.8 (1M context)" -> "Opus 4.8".
MODEL=$(printf '%s' "$MODEL" | sed -E 's/[[:space:]]*\([^)]*\)[[:space:]]*$//')

# Compact token formatter: 45230 -> 45.2k, 1000000 -> 1M, 200000 -> 200k, 820 -> 820.
fmt() {
  awk -v n="$1" 'BEGIN{
    if (n >= 1000000)   { v=n/1000000; u="M" }
    else if (n >= 1000) { v=n/1000;    u="k" }
    else                { printf "%d", n; exit }
    if (v == int(v)) printf "%d%s", v, u; else printf "%.1f%s", v, u;
  }'
}

OUT="[$MODEL]"

# Context segment: visual bar (from %) + absolute "IN/SIZE ctx".
CTX=""
if [ -n "$PCT" ]; then
  PCT_INT=${PCT%.*}                      # strip any decimal
  [ -z "$PCT_INT" ] && PCT_INT=0
  [ "$PCT_INT" -gt 100 ] 2>/dev/null && PCT_INT=100
  FILLED=$((PCT_INT * 10 / 100))
  EMPTY=$((10 - FILLED))
  BAR=""
  [ "$FILLED" -gt 0 ] && { printf -v F "%${FILLED}s" ""; BAR="${F// /▓}"; }
  [ "$EMPTY"  -gt 0 ] && { printf -v E "%${EMPTY}s"  ""; BAR="${BAR}${E// /░}"; }
  CTX="$BAR"
fi
if [ -n "$TIN" ]; then
  NUM=$(fmt "$TIN")
  [ -n "$SIZE" ] && NUM="$NUM/$(fmt "$SIZE")"
  CTX="${CTX:+$CTX }${NUM} ctx"
elif [ -n "$PCT" ]; then
  CTX="$CTX ${PCT_INT}% ctx"             # no absolute available -> label the bar with %
fi
[ -n "$CTX" ] && OUT="$OUT $CTX"

# Last response output tokens.
[ -n "$TOUT" ] && OUT="$OUT · ↑$(fmt "$TOUT") resp"

# Cumulative session cost.
[ -n "$COST" ] && OUT="$OUT · $(printf '$%.2f' "$COST" 2>/dev/null || echo "$COST")"

echo "$OUT"
