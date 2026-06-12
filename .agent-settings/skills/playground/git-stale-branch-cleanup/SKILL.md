---
name: git-stale-branch-cleanup
description: Scans remote origin branches behind the base branch, filters by staleness threshold, generates a per-branch scan report with intent analysis and Jira detection, then optionally deletes remote branches and prunes local counterparts. Dry-run mode reports without deleting. Use when cleaning up stale branches, pruning old feature branches, or asked to remove merged/abandoned branches.
allowed-tools: Bash(git *), Bash(date *), Bash(echo *), Bash(printf *), Bash(grep *), Bash(awk *), Bash(sed *), Bash(sort *), Bash(wc *), Bash(bash *)
---

# Git Stale Branch Cleanup

Two modes — both always generate a full scan report before any action:

- **Dry-run** (default): scan → report only, nothing deleted.
- **Live**: scan → report → multi-select → confirm → delete remote → prune local.

## Usage

```
/git-stale-branch-cleanup             # prompts for mode
/git-stale-branch-cleanup --dry-run
/git-stale-branch-cleanup --live
```

## Reference Scripts

Run directly — **do not regenerate these commands inline**. Agent instructions are embedded in each script header; read them after running.

| Script | Run as |
|--------|--------|
| `references/scan-pass-a.sh` | `bash references/scan-pass-a.sh "$BASE_BRANCH" "$THRESHOLD_DAYS" "$SCAN_LIMIT"` |
| `references/scan-pass-b.sh` | `bash references/scan-pass-b.sh "<branch>" "$BASE_BRANCH"` |
| `references/delete-branch.sh` | `bash references/delete-branch.sh "<branch>"` |

---

## ⚠ BLOCKING: Load mode file before proceeding

**If Live mode / `--live`:**
→ read_file: `.agent-settings/skills/git-stale-branch-cleanup/references/mode-live.md`

**If Dry-run / `--dry-run` / default:**
→ No extra file needed — dry-run exits after Phase 4.

---

## Phase 0 — Mode Selection

```
  [D] Dry-run  (default) — scan and report only, nothing deleted
  [L] Live               — scan, report, then select branches to delete

Select mode [D/L]:
```

Default (Enter) → **Dry-run**. Load mode file immediately per BLOCKING rule above.

---

## Phase 1 — Base Branch

```
  [1] origin/main    (default)
  [2] origin/master
  [3] origin/develop
  [4] Other — type the branch name

Select [1-4]:
```

Auto-detect default via `git remote show origin | grep 'HEAD branch'`. Store as `BASE_BRANCH`.
Then: `git fetch --prune origin`

---

## Phase 2 — Staleness Threshold

```
  [1]  90 days  (3 months)
  [2] 180 days  (6 months)
  [3] 365 days  (1 year)
  [4] 730 days  (2 years)
  [5] Other — enter number of days

Select [1-5]:
```

Store as `THRESHOLD_DAYS`.

---

## Phase 2b — Scan Limit

```
  [1]  6  (default — fast)
  [2] 10
  [3] 15
  [4] 20
  [5] 30  (slowest)

Select [1-5]:
```

Default (Enter) → **6**. Store as `SCAN_LIMIT`.

---

## Phase 3 — Branch Scan

```bash
bash references/scan-pass-a.sh "$BASE_BRANCH" "$THRESHOLD_DAYS" "$SCAN_LIMIT"
```

Read the AGENT INSTRUCTIONS in `scan-pass-a.sh` header. For each TSV line:

```bash
bash references/scan-pass-b.sh "<branch>" "$BASE_BRANCH"
```

Read the AGENT INSTRUCTIONS in `scan-pass-b.sh` header to render branch cards and the summary block.

---

## Phase 4 — Scan Report

Render the report from script output per `scan-pass-b.sh` instructions.

**Dry-run stops here.** Print:
```
Dry-run complete. Run with --live (or select Live mode) to proceed with deletion.
```

*(Live mode: continue with `references/mode-live.md`.)*

---

## Global Rules

- **Use reference scripts** — never regenerate scan or delete commands inline.
- **Never delete** the remote of `BASE_BRANCH` or the currently checked-out branch.
- **Dry-run is the safe default** — never assume live mode without explicit selection.
- **Scan report is always shown** in both modes before any further action.
- **Unmerged selections must show ⚠** in confirmation — never silently delete unmerged work.
