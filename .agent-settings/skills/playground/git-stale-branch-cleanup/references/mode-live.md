# Git Stale Branch Cleanup — Live Mode

This file is loaded dynamically when the user selects **Live mode**.
It contains Phase 5–8: multi-select → confirm → execute → deletion report.

Shared context from `SKILL.md` is already loaded (BASE_BRANCH, THRESHOLD_DAYS, branch list with cards).

---

## Phase 5 — Multi-Select

After the scan report, present the selection menu using the same numbered list from Phase 4:

```
  [A] Select ALL
  [M] Select all MERGED only  (recommended — safest)
  [0] Cancel — delete nothing

Select branches to delete (number to toggle, A, M, or 0 to cancel):
```

Use the same checkbox-style toggle loop as import-skills: type a number to toggle that entry,
`A` to select all, `M` to select merged-only, `0` to cancel. Redisplay the list with `[✓]`/`[ ]`
state after each toggle. Empty Enter confirms the current selection.

---

## Phase 6 — Confirmation

After selection is confirmed, show a pre-deletion summary:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Branches to delete
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Remote delete (primary):
    • origin/feat/old-login-refactor      (187 days, merged)
    • origin/fix/legacy-auth-patch        (134 days, UNMERGED ⚠)

  Local prune (if local copy exists — best effort):
    • feat/old-login-refactor    → local copy found, will delete
    • fix/legacy-auth-patch      → local copy found, will delete

⚠ UNMERGED branches selected. These contain commits not in origin/main.
  Deleting them may lose work permanently.

Proceed? (y/n)
```

- Blank input: re-prompt — must type `y` or `n`.
- `n` → cancel, return to Phase 5 (re-show selection menu).

Highlight unmerged selections with `⚠ UNMERGED`. Do not block — just ensure the user sees the risk.

---

## Phase 7 — Execute Deletion

Process each selected branch in two steps:

### Step 1 — Remote delete (primary)

```bash
git push origin --delete <branch>
```

- On success: report ✓ and proceed to local prune.
- On failure: report ✗ with error message — **never abort the loop**. Still attempt local prune.

### Step 2 — Local prune (best effort, only if local copy exists)

If `LOCAL_EXISTS=yes` for this branch:

```bash
git branch -D <branch>
```

- On success: report ✓ (local pruned).
- On failure: report ✗ with error — non-fatal, continue to next branch.
- If `LOCAL_EXISTS=no`: skip silently (nothing to prune).

---

## Phase 8 — Deletion Report

Always print a full summary after all deletions are attempted:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Cleanup Report
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Remote deletions (primary):
    ✓ origin/feat/old-login-refactor   deleted
    ✗ origin/fix/legacy-auth-patch     FAILED — remote: refusing to delete current branch

  Local prune (secondary):
    ✓ feat/old-login-refactor          pruned
    ✓ fix/legacy-auth-patch            pruned
    — chore/cleanup-unused-deps        skipped (no local copy)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Remote:  1 deleted, 1 failed
  Local:   2 pruned, 0 failed, 1 skipped (no local copy)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

For any remote failures, print the manual retry command:
```
  To retry manually:
    git push origin --delete fix/legacy-auth-patch
```

---

## Live Mode Rules

- **Confirmation (Phase 6) is mandatory** — never skip it.
- **Remote delete is the primary action** — execute first; local prune is secondary and always best-effort.
- **Local prune is skipped silently** when no local copy exists (`LOCAL_EXISTS=no`).
- **Remote delete failures are non-fatal** — still attempt local prune and continue the loop.
- **Always use `git branch -D` for local prune** — user has confirmed; `-d` would fail on unmerged branches.
- Unmerged selections must show ⚠ in Phase 6 confirmation — never silently delete unmerged work.
