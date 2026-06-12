# DRY-RUN MODE

*(Only entered when user selects [D] or passes `--dry-run`)*

---

## Dry-run Phase D1 — Announce

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Dry-run mode — conflict prediction only.
  No commits, no file changes, no branch modifications.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

If no rebase is in progress, ask: `Which branch do you want to simulate rebasing onto?`

## Dry-run Phase D2 — Predict Conflicts

Without running an actual rebase, identify which commits would conflict:

1. Find merge base:
   ```bash
   git merge-base HEAD <target-branch>
   ```

2. List commits to replay:
   ```bash
   git log --oneline <merge-base>..HEAD
   ```

3. For each commit, find files it touches that are also changed in `<target-branch>` since merge-base:
   ```bash
   git diff-tree --no-commit-id -r --name-only <commit-sha>  # commit's files
   git diff --name-only <merge-base>..<target-branch>         # target's files
   ```
   Intersection = files at risk for that commit.

4. For each at-risk file, run a three-way diff to confirm overlap:
   ```bash
   git diff <merge-base> <commit-sha> -- <file>        # what commit changes
   git diff <merge-base> <target-branch> -- <file>     # what target changes
   ```
   Overlapping line ranges → **confirmed conflict**.  
   Disjoint ranges → **potential only (low risk)**.

## Dry-run Phase D3 — Conflict Prediction Report

Always generate and print in full:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Conflict Prediction Report  [DRY-RUN — branch unchanged]
  Rebasing: <current-branch> → <target-branch>
  Commits to replay: 7
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Predicted conflicts:

  Commit 3/7  abc1234 — "feat: migrate token storage to KeyVault"
  ┌──────────────────────────────────────────────────────────┐
  │ ⚠ CONFLICT  src/auth/session.ts                          │
  │   Both sides modify refreshToken() — overlapping lines  │
  │   Risk: High — production auth path                      │
  └──────────────────────────────────────────────────────────┘
  ┌──────────────────────────────────────────────────────────┐
  │ ~ POTENTIAL  src/config/env.ts                           │
  │   Both sides touch this file but in different sections   │
  │   Risk: Low — may auto-resolve                           │
  └──────────────────────────────────────────────────────────┘

  Commit 5/7  def5678 — "chore: update eslint config"
  ┌──────────────────────────────────────────────────────────┐
  │ ⚠ CONFLICT  .eslintrc.json                               │
  │   Both sides add rules in the same block                 │
  │   Risk: Medium — tooling only, not runtime               │
  └──────────────────────────────────────────────────────────┘

  Commits 1, 2, 4, 6, 7 — no predicted conflicts

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Summary:
    Commits to replay:     7
    Conflict-free:         5
    Confirmed conflicts:   2 files across 2 commits
    Potential (low risk):  1 file
  Branch is UNCHANGED.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Run with --progressive or --auto to resolve conflicts.
```

Dry-run ends here. No git state was modified.

---

---

