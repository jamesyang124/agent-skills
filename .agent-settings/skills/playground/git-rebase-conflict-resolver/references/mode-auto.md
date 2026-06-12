# AUTO MODE — Phases A1–A6

*(Only entered when user selects Auto or passes `--auto`)*

---

## Auto Phase A1 — Announce and Confirm

Print once before starting:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Auto Mode — I will resolve all conflicts autonomously.
  No prompts will be shown during resolution.
  A full audit report will be presented at the end for your approval.
  Declining the report will roll back the entire rebase.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Starting position recorded:
    Branch: <ORIGINAL_BRANCH>
    HEAD:   <ORIGINAL_HEAD>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Proceed? (y/n)
```

- Blank input: re-prompt — must type `y` or `n`.
- `n` → abort, do nothing.

## Auto Phase A2 — Silent Resolution Loop

Loop until the rebase completes or an unresolvable error is hit:

1. Run `git status` — if no conflict, run `git rebase --continue` and loop.
2. For each conflicted file: run the full Phase P2 analysis internally.
3. Select the ★ recommended approach and execute it immediately.
4. Stage the file: `git add <file>`.
5. Record the decision in the audit log (see A3).
6. After all files in the commit are staged, run `git rebase --continue`.
7. Repeat until the rebase exits cleanly or errors out.

**If an unresolvable error occurs** (e.g. binary conflict, corrupt file, unexpected git error):
- Stop immediately.
- Print: `Auto mode cannot resolve <file>: <reason>. Switching to Progressive for this file.`
- Drop into Progressive mode for that one file only, then resume auto for the rest.
- Mark the fallback in the audit log with ⚠.

## Auto Phase A3 — Audit Log (built during A2)

For every conflict encountered, append a record in this format. **No entry may be omitted.**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Entry #<N>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
File:          src/auth/session.ts
Commit:        abc1234 — "feat: migrate token storage to KeyVault"
Position:      commit 2 of 5

HEAD (ours):   Added rate-limit guard around refreshToken()
Incoming:      Migrated token storage to KeyVault API
Orthogonal:    No — both modify refreshToken()
Risk assessed: High — silent discard of either breaks prod

Approach chosen: Merge both — wrap KeyVault call inside rate-limit guard ★
Rationale:     Both sides contain unique production logic. Merge preserves
               the guard and applies the new storage call in correct order.

Discarded:     Nothing — both intents fully preserved in merged output.
Confidence:    High
```

Use ⚠ prefix on `Approach chosen` line for any fallback-to-progressive entries.

## Auto Phase A4 — Rebase Complete Notification

After the rebase loop exits cleanly, print:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Rebase complete — <N> conflict(s) resolved across <M> commit(s)
  Branch tip: <new HEAD SHA>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Preparing audit report for your review...
```

## Auto Phase A5 — Audit Report Presentation

Print the full audit log in sequence (all entries, none skipped).  
Then append a summary table:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  AUDIT SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  #  │ File                      │ Approach              │ Risk  │ Flag
  ───┼───────────────────────────┼───────────────────────┼───────┼─────
  1  │ src/auth/session.ts       │ Merge both            │ High  │ ★
  2  │ src/config/env.ts         │ Keep ours (env guard) │ Low   │ ★
  3  │ tests/auth.test.ts        │ Merge both            │ Med   │ ⚠ (manual)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Total conflicts: 3 | Merged: 2 | Pure-side: 1 | Manual fallback: 1
  New HEAD: <sha>  |  Original HEAD: <ORIGINAL_HEAD>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Review each entry above carefully.

  [Y] Approve — accept the rebased branch as-is
  [N] Decline — roll back the entire rebase, restore original branch position

Your decision (Y/N):
```

- Blank input: re-prompt — must type `Y` or `N`.

## Auto Phase A6 — Approve or Rollback

### If approved (`Y`)
```
✓ Rebase accepted. Branch <ORIGINAL_BRANCH> is now at <new HEAD>.
```
Optionally suggest running the test suite if detectable.

### If declined (`N`)

Execute the full rollback sequence:

```bash
# 1. If still in a rebase (edge case), abort it first
git rebase --abort 2>/dev/null || true

# 2. Force-reset the branch to the original HEAD
git checkout <ORIGINAL_BRANCH>
git reset --hard <ORIGINAL_HEAD>
```

Print:
```
✗ Declined. Rolling back...
  Checked out: <ORIGINAL_BRANCH>
  Reset to:    <ORIGINAL_HEAD>
  Branch is now at its pre-rebase position.
```

Verify with `git log --oneline -3` and show output so the user can confirm the reset was clean.

---

