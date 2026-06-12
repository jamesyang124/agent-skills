---
name: git-rebase-conflict-resolver
description: Interactive git rebase conflict resolver with Dry-run, Progressive, and Auto modes. Dry-run predicts conflict paths without touching the branch. Progressive mode is interactive per-conflict. Auto mode resolves autonomously then presents an audit report for approval or rollback. All modes generate a report. Use when rebasing branches, resolving merge conflicts, or asked to help with git rebase.
allowed-tools: Bash(git *), Bash(cat *), Bash(diff *), Bash(grep *), Bash(find *), Bash(echo *), Bash(printf *), Bash(tee *)
---

# Git Rebase Conflict Resolver

Three modes — all generate a report:

- **Dry-run mode**: predicts which commits and files would conflict without touching the branch. Zero side effects.
- **Progressive mode** (default): interactive per-conflict — analysis + named approaches for every file. You decide each resolution. Generates a resolution summary at the end.
- **Auto mode**: resolves all conflicts autonomously, tracks every decision, presents a full audit report for approval or rollback.

## Usage

```
/git-rebase-conflict-resolver              # prompts for mode
/git-rebase-conflict-resolver --dry-run    # conflict prediction report, no changes
/git-rebase-conflict-resolver --progressive  # interactive per-conflict
/git-rebase-conflict-resolver --auto       # autonomous resolution + audit report
```

---

## Mode Selection (when no flag given)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Git Rebase Conflict Resolver
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  [D] Dry-run mode
      Predict which commits and files would conflict — no branch changes.
      Generates a conflict prediction report.

  [P] Progressive mode  (default)
      Analyze each conflict interactively. You choose every resolution.
      Generates a resolution report at the end.

  [A] Auto mode
      Resolve all conflicts autonomously. Review audit report at the end
      and approve or roll back the entire rebase.

Select mode [D/P/A]:
```

Enter with no input → **Progressive**.

---

## Target Branch Selection (all modes)

After mode is chosen, ask for the rebase target branch:

```
Target branch to rebase onto:

  [1] origin/main  ← from upstream tracking ref (@{upstream})

  Or type a branch name directly to use a custom target.

Select [1] or type branch name:
```

**Auto-detection order** (try each, use first that succeeds):
1. `git rev-parse --abbrev-ref --symbolic-full-name @{upstream} 2>/dev/null` → label as `← from upstream tracking ref (@{upstream})`
2. `git remote show origin 2>/dev/null | grep 'HEAD branch'` → label as `← from repo default (origin HEAD)`
3. If both fail, skip option `[1]` and show only: `Type the target branch name:`

If the user's input is `1` → use the detected branch. Any other non-empty input → use it as the branch name directly. Store as `TARGET_BRANCH`.

---

## ⚠ BLOCKING: Load mode file before proceeding

**Always run before any git operation:**

```bash
git rev-parse HEAD           # stored as ORIGINAL_HEAD
git branch --show-current    # stored as ORIGINAL_BRANCH
```

Then detect rebase state via `git status`:
- **No rebase in progress**: proceed to rebase onto `TARGET_BRANCH`. In dry-run mode, **do not start the rebase** — use `TARGET_BRANCH` for prediction only.
- **Rebase in progress, no conflicts**: `git rebase --continue` and loop (not applicable in dry-run).
- **Conflicts detected**: proceed to Phase P1 (Progressive/Auto) or — in dry-run — this state is not applicable.
- **Paused, no conflicts**: ask `--continue`, `--skip`, or `--abort` (not applicable in dry-run).

---


## ⚠ BLOCKING: Load mode file before proceeding

After the user selects a mode (or a flag is passed), you MUST immediately read the corresponding
mode file before taking any further action. Do NOT proceed without loading it.

**If Dry-run mode selected or `--dry-run` flag given:**
→ read_file: `.agent-settings/skills/git-rebase-conflict-resolver/references/mode-dry-run.md`

**If Progressive mode selected or `--progressive` flag given (or default):**
→ read_file: `.agent-settings/skills/git-rebase-conflict-resolver/references/mode-progressive.md`

**If Auto mode selected or `--auto` flag given:**
→ read_file: `.agent-settings/skills/git-rebase-conflict-resolver/references/mode-auto.md`

**Immediately after mode is determined and file is loaded, proceed with Phase 0 below.**

---
## Global Rules

- **Always capture `ORIGINAL_HEAD` and `ORIGINAL_BRANCH` before any git operation** — all modes.
- **Dry-run never modifies any git state** — no rebase is started, no files are written.
- **All modes generate a report** — dry-run produces a prediction report; progressive produces a resolution summary; auto produces a full audit log with approve/rollback.
- **Auto mode never skips an entry** in the audit log — every conflict must appear.
- **Never use generic labels** like "Accept OURS" — name approaches by what they preserve or achieve.
- **Never auto-resolve in Progressive mode** without user confirmation.
- **Never run `git add -A`** or stage unrelated files.
- **Always show full conflict blocks** — never truncate with `...`.
- In Auto mode, if confidence is Low on any entry, mark it ⚠ in the audit log and flag it prominently in the summary.
- After rebase completes in either mode, suggest running the test suite if one is detectable (`package.json`, `Makefile`, `pytest.ini`, etc.).
---
