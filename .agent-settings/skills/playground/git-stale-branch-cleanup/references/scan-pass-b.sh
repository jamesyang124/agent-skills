#!/bin/bash
# scan-pass-b.sh — Pass B: per-branch deep data collection
#
# Usage:
#   scan-pass-b.sh <BRANCH> <BASE_BRANCH>
#
# Example:
#   scan-pass-b.sh feat/old-login-refactor origin/main
#
# Output: structured sections for the agent to read and render into a branch card.
# Exit code 0 on success, 1 if branch does not exist remotely.
#
# ─────────────────────────────────────────────────────────────────────────────
# AGENT INSTRUCTIONS — read and render after running this script
# ─────────────────────────────────────────────────────────────────────────────
# Render one card per branch using the output sections. Card format:
#
#   [N] <branch-name>
#       Age: <age_days> days  |  Behind: <behind>  |  Merged: ✓          ← or ✗ unmerged ⚠
#       Local:   yes (local branch exists)                                 ← or: no (remote only)
#       Jira:    <TICKET-123>                                              ← or: (none)
#       Intent:  <1–2 sentence summary you write — see Intent Rules below>
#       Commits: <count>  — "<subject1>", "<subject2>", ...               ← truncate subjects at ~40 chars
#
# Field rules:
#   Age / Behind  : from the TSV line produced by scan-pass-a.sh
#   Merged        : from LOCAL line ("yes" → ✓, "no" → ✗ unmerged ⚠); also set from MERGED section
#   Local         : from LOCAL line
#   Jira          : all lines under === JIRA === deduplicated; mark (none) if empty
#   Intent        : synthesize from COMMITS + CHANGED_FILES + DIFF_STAT — must be specific,
#                   reference actual file paths or feature names; NEVER write generic filler
#   Commits       : COMMIT_COUNT value + first few subjects from === COMMITS ===,
#                   each truncated to ~40 chars with ...
#
# After all cards, print the summary block:
#
#   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#     Summary: <N> stale remote branches found
#       Merged:     <n>  (safe to delete)
#       Unmerged:   <n>  ⚠ (unique commits not in <BASE_BRANCH>)
#       With Jira:  <n>  |  With local copy: <n>  |  Remote only: <n>
#   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#
# If no branches matched Pass A:
#   ✓ No stale branches found older than <THRESHOLD_DAYS> days behind <BASE_BRANCH>
#     (excluding release/*, hotfix/*).
#   Exit cleanly in both modes.
# ─────────────────────────────────────────────────────────────────────────────

set -e

BRANCH="${1:?Usage: scan-pass-b.sh BRANCH BASE_BRANCH}"
BASE_BRANCH="${2:?Missing BASE_BRANCH}"
REMOTE_REF="origin/$BRANCH"

# Verify branch exists
if ! git show-ref --verify --quiet "refs/remotes/$REMOTE_REF" 2>/dev/null; then
  echo "ERROR: remote branch $REMOTE_REF not found" >&2
  exit 1
fi

echo "=== BRANCH: $BRANCH ==="

# Local counterpart
if git branch --list "$BRANCH" | grep -q .; then
  echo "LOCAL: yes"
else
  echo "LOCAL: no"
fi

# Merged status
if git merge-base --is-ancestor "$REMOTE_REF" "$BASE_BRANCH" 2>/dev/null; then
  echo "MERGED: yes"
else
  echo "MERGED: no"
fi

# Jira tickets — from branch name first, then commit messages
echo "=== JIRA ==="
{
  echo "$BRANCH" | grep -oE '[A-Z]{2,10}-[0-9]+' || true
  git log "$REMOTE_REF" --not "$BASE_BRANCH" --format="%s %b" 2>/dev/null \
    | grep -oE '[A-Z]{2,10}-[0-9]+' || true
} | sort -u | head -5

# Commit subjects (for intent synthesis)
echo "=== COMMITS ==="
git log "$REMOTE_REF" --not "$BASE_BRANCH" --format="%s" 2>/dev/null | head -10

# Commit count
echo "=== COMMIT_COUNT ==="
git rev-list --count "$BASE_BRANCH".."$REMOTE_REF" 2>/dev/null || echo 0

# Diff summary
echo "=== DIFF_STAT ==="
git diff --stat "$BASE_BRANCH".."$REMOTE_REF" -- 2>/dev/null | tail -1

# Changed files
echo "=== CHANGED_FILES ==="
git diff --name-only "$BASE_BRANCH".."$REMOTE_REF" -- 2>/dev/null | head -15
