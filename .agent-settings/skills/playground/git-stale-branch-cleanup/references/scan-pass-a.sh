#!/bin/bash
# scan-pass-a.sh — Pass A: fast metadata scan of all remote branches
#
# Usage:
#   scan-pass-a.sh <BASE_BRANCH> <THRESHOLD_DAYS> <SCAN_LIMIT>
#
# Example:
#   scan-pass-a.sh origin/main 90 6
#
# Output: TSV lines, one per selected branch (merged-first, capped at SCAN_LIMIT):
#   <branch>  <age_days>  <behind>  <merged|unmerged>
#
# Excludes: origin/HEAD, release/*, hotfix/*, BASE_BRANCH itself,
#           and the currently checked-out branch's remote counterpart.
#
# ─────────────────────────────────────────────────────────────────────────────
# AGENT INSTRUCTIONS — read after running this script
# ─────────────────────────────────────────────────────────────────────────────
# 1. Count ALL lines printed = SCAN_RESULT_COUNT (for the report header).
#
# 2. Also track TOTAL_QUALIFYING = all branches that passed the age+behind
#    filter before the cap. This comes from the internal MERGED_OUT +
#    UNMERGED_OUT counts. To get it, re-run with a large limit and count, or
#    simply note when the output equals SCAN_LIMIT (meaning more exist).
#    If SCAN_RESULT_COUNT == SCAN_LIMIT, add "Run again after cleanup to see
#    the rest." to the report header. Otherwise, the output IS the full set.
#
# 3. Print the report banner before listing branch cards:
#
#   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#     Stale Branch Scan Report  [DRY-RUN — no changes will be made]
#     Base: <BASE_BRANCH>  |  Threshold: ><THRESHOLD_DAYS> days  |  Scanned: N remote branches
#     Excluded: release/*, hotfix/*  |  Showing <SCAN_RESULT_COUNT> of <TOTAL_QUALIFYING> qualifying branches (merged-first)
#   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#   Use [LIVE MODE] instead of [DRY-RUN...] when in live mode.
#   If SCAN_RESULT_COUNT == TOTAL_QUALIFYING, omit "of N qualifying".
#
# 4. For each TSV line, run scan-pass-b.sh and render a branch card.
#    See scan-pass-b.sh header for card format and field rules.
#
# 5. After all cards, print the summary block (also described in scan-pass-b.sh).
# ─────────────────────────────────────────────────────────────────────────────

set -e

BASE_BRANCH="${1:?Usage: scan-pass-a.sh BASE_BRANCH THRESHOLD_DAYS SCAN_LIMIT}"
THRESHOLD_DAYS="${2:?Missing THRESHOLD_DAYS}"
SCAN_LIMIT="${3:?Missing SCAN_LIMIT}"

NOW=$(date +%s)

# Detect currently checked-out branch to exclude its remote
CURRENT_BRANCH=$(git symbolic-ref --short HEAD 2>/dev/null || true)

MERGED_OUT=""
UNMERGED_OUT=""

while IFS= read -r branch; do
  # Skip base branch and HEAD
  [ "origin/$branch" = "$BASE_BRANCH" ] && continue
  [ "$branch" = "$BASE_BRANCH" ] && continue
  [ "$branch" = "HEAD" ] && continue

  # Skip currently checked-out branch's remote
  [ -n "$CURRENT_BRANCH" ] && [ "$branch" = "$CURRENT_BRANCH" ] && continue

  # Last commit timestamp
  last_ts=$(git log -1 --format="%ct" "origin/$branch" 2>/dev/null) || continue
  [ -z "$last_ts" ] && continue

  age=$(( (NOW - last_ts) / 86400 ))
  [ "$age" -lt "$THRESHOLD_DAYS" ] && continue

  behind=$(git rev-list --count "origin/$branch".."$BASE_BRANCH" 2>/dev/null) || continue
  [ "$behind" -eq 0 ] && continue

  if git merge-base --is-ancestor "origin/$branch" "$BASE_BRANCH" 2>/dev/null; then
    merged="merged"
    MERGED_OUT="${MERGED_OUT}${branch}	${age}	${behind}	${merged}"$'\n'
  else
    merged="unmerged"
    UNMERGED_OUT="${UNMERGED_OUT}${branch}	${age}	${behind}	${merged}"$'\n'
  fi

done < <(git branch -r 2>/dev/null \
  | sed 's|^[[:space:]]*origin/||' \
  | grep -v '^HEAD' \
  | grep -v '^release/' \
  | grep -v '^hotfix/')

# Tier 1: merged, sorted by age desc, capped at SCAN_LIMIT
TIER1=$(printf '%s' "$MERGED_OUT" | grep . | sort -t'	' -k2 -rn | head -"$SCAN_LIMIT")
TIER1_COUNT=0
if [ -n "$TIER1" ]; then
  TIER1_COUNT=$(printf '%s\n' "$TIER1" | grep -c .)
fi

REMAINING=$(( SCAN_LIMIT - TIER1_COUNT ))

# Tier 2: unmerged, backfill remaining slots only
TIER2=""
if [ "$REMAINING" -gt 0 ] && [ -n "$UNMERGED_OUT" ]; then
  TIER2=$(printf '%s' "$UNMERGED_OUT" | grep . | sort -t'	' -k2 -rn | head -"$REMAINING")
fi

# Emit result
[ -n "$TIER1" ] && printf '%s\n' "$TIER1"
[ -n "$TIER2" ] && printf '%s\n' "$TIER2"
