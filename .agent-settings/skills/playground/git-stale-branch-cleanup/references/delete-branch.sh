#!/bin/bash
# delete-branch.sh — Delete a remote branch and prune its local counterpart
#
# Usage:
#   delete-branch.sh <BRANCH>
#
# Example:
#   delete-branch.sh feat/old-login-refactor
#
# Behaviour:
#   1. Deletes origin/<BRANCH> (remote — primary target)
#   2. If a local branch with the same name exists, deletes it too (best-effort)
#   3. Runs `git remote prune origin` to clean up stale tracking refs
#
# Exit code 0 on success, non-zero if remote delete fails.

set -e

BRANCH="${1:?Usage: delete-branch.sh BRANCH}"

echo "Deleting remote: origin/$BRANCH"
git push origin --delete "$BRANCH"

# Prune stale remote-tracking refs
git remote prune origin --dry-run 2>/dev/null | grep -q "would prune" \
  && git remote prune origin \
  || true

# Remove local counterpart if it exists (best-effort, not fatal)
if git branch --list "$BRANCH" | grep -q .; then
  echo "Removing local: $BRANCH"
  git branch -D "$BRANCH" || {
    echo "Warning: could not delete local branch $BRANCH (may be checked out)" >&2
  }
fi

echo "Done: $BRANCH"
