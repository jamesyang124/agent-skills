# PROGRESSIVE MODE — Phases P1–P5

*(Skip to AUTO MODE section if running auto)*

---

## Progressive/Auto Phase P1 — Conflict Inventory

1. Collect all conflicted files:
   ```bash
   git diff --name-only --diff-filter=U
   ```
2. Print a numbered list of conflicted files with their status (both modified, deleted-by-us, deleted-by-them, etc.).
3. Show the current commit being applied:
   ```bash
   git log --oneline -1 REBASE_HEAD
   ```
4. Show position in the rebase sequence:
   ```bash
   cat "$(git rev-parse --git-dir)/rebase-merge/msgnum" 2>/dev/null || cat "$(git rev-parse --git-dir)/rebase-apply/next" 2>/dev/null
   cat "$(git rev-parse --git-dir)/rebase-merge/end" 2>/dev/null || cat "$(git rev-parse --git-dir)/rebase-apply/last" 2>/dev/null
   ```

In **Auto mode**: print inventory silently as a log line, do not pause for input.  
In **Progressive mode**: display inventory and wait for acknowledgement before continuing.

---

## Progressive/Auto Phase P2 — Per-File Conflict Analysis (MANDATORY)

For **each** conflicted file, perform the full analysis. Never skip.

### 2a. Show the raw conflict markers
```bash
cat <file>
```
Display the full conflict block(s) with `<<<<<<< HEAD`, `=======`, `>>>>>>> <commit>` clearly visible.

### 2b. Semantic analysis — answer ALL of the following:

| Question | What to determine |
|---|---|
| **What changed on HEAD (ours)?** | Summarize the intent of the HEAD changes in plain English |
| **What changed in the incoming commit (theirs)?** | Summarize the intent of the incoming changes |
| **Are the changes orthogonal?** | Do they touch different logic / lines of responsibility? |
| **Is one a superset of the other?** | Does one side already contain or supersede what the other does? |
| **Risk of data loss** | Would accepting one side silently discard important logic? |
| **Dependency impact** | Do other files depend on the shape of the code being changed? Run `git grep` if needed |
| **Test coverage** | Are there tests that validate the conflicting code paths? |

### 2c. Derive approaches and act

Always derive 2–4 named, conflict-specific approaches (never generic "Accept OURS"). Mark the recommended one ★.

**Progressive mode** → present the approach menu and wait for user input (see Progressive Phase P3 below).

**Auto mode** → silently select the ★ recommended approach and execute immediately. Append a full decision record to the audit log (see Auto Phase A3 below). Do NOT pause or ask the user anything.

---

---

# PROGRESSIVE MODE — Phases P3–P5

*(Skip to AUTO MODE section if running auto)*

---

## Progressive Phase P3 — Present Approaches and Wait

Display the conflict summary + named approach menu:

```
Conflict in: src/auth/session.ts  [commit 2/5]
─────────────────────────────────────────────────────────────
  HEAD:     Added rate-limit guard around refreshToken()
  Incoming: Migrated token storage from localStorage to KeyVault API
  Risk:     Both modify refreshToken() — silent discard of either breaks prod
─────────────────────────────────────────────────────────────

My recommendation: Approach B — merge both changes ★

  [A] Keep rate-limit guard only (discard KeyVault migration)
      Risk: KeyVault migration must be re-applied separately or it's lost.

  [B] Merge both — wrap KeyVault call inside the rate-limit guard ★
      Risk: Low — both intents preserved. Verify call order in tests.

  [C] Apply KeyVault migration only (discard rate-limit guard)
      Risk: Rate-limit protection removed from refresh path.

  [D] Skip this commit — apply it later manually
  [E] Abort the entire rebase
  [R] I want to explain my intent before choosing

─────────────────────────────────────────────────────────────
Your choice [A/B/C/D/E/R]:
```

If user selects **[R]**: ask for intent, re-derive approaches, re-present with updated ★.

## Progressive Phase P4 — Execute Resolution (user-directed)

### Pure-side approach
```bash
git checkout --ours <file>    # or --theirs
git add <file>
```

### Merge approach
1. Show the complete proposed merged file in a fenced code block.
2. Explain every decision made (what was kept from each side and where).
3. Ask: `Apply this merged version? [y/edit/abort]`
   - `y` → write file, `git add <file>`
   - `edit` → show content again, ask user to paste corrected version
   - `abort` → return to approach menu

### Skip commit
```bash
git rebase --skip
```

### Abort rebase
```bash
git rebase --abort
```
Confirm: `Rebase aborted. Branch restored to pre-rebase state.`

## Progressive Phase P5 — Continue or Loop

After all files in the current commit are staged:
1. `git diff --name-only --diff-filter=U` — if any remain, return to Phase P2.
2. `git rebase --continue`
3. If new conflicts → loop to Phase P1. If complete → generate and print the **Progressive Resolution Report**.

## Progressive Resolution Report

Always printed when the rebase completes in Progressive mode:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Progressive Resolution Report
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  #  │ File                      │ Approach chosen            │ Note
  ───┼───────────────────────────┼────────────────────────────┼──────
  1  │ src/auth/session.ts       │ Merge both (KeyVault+guard) │
  2  │ src/config/env.ts         │ Keep ours (env guard)       │
  3  │ tests/auth.test.ts        │ Manual edit by user         │ user-edited

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Conflicts resolved: 3 | New HEAD: <sha>
  Original HEAD: <ORIGINAL_HEAD>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

---

