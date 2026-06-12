---
name: ado-pr-resolve-comments
description: Read active review comments on an Azure DevOps PR and resolve them by applying the suggested fixes with user consent. Trivial fixes are shown as before/after diffs for quick approval. Non-trivial changes produce a refactoring plan for user review before execution. Companion to ado-pr-code-review. Use when asked to resolve PR comments, apply review suggestions, fix PR feedback, or address code review findings.
argument-hint: "<azure-devops-pr-url>"
allowed-tools: mcp_azure_devops__repo_list_pull_request_threads, mcp_azure_devops__repo_list_pull_request_thread_comments, mcp_azure_devops__repo_get_file_content, mcp_azure_devops__repo_get_pull_request_by_id, mcp_azure_devops__repo_reply_to_comment, mcp_azure_devops__repo_update_pull_request_thread
---

# Azure DevOps PR — Resolve Review Comments

## ⚙️ Required: install the `diagnose` skill

Install `diagnose` globally for your agent **once**, then it is available in all projects.

### Claude (global)
```bash
mkdir -p ~/.claude/skills/diagnose
curl -fsSL https://raw.githubusercontent.com/mattpocock/skills/main/skills/engineering/diagnose/SKILL.md \
  -o ~/.claude/skills/diagnose/SKILL.md
# Then add to ~/.claude/CLAUDE.md:
# - **diagnose** (`~/.claude/skills/diagnose/SKILL.md`) — bug diagnosis loop
```

### GitHub Copilot (global)
```bash
mkdir -p ~/.copilot/skills/diagnose
curl -fsSL https://raw.githubusercontent.com/mattpocock/skills/main/skills/engineering/diagnose/SKILL.md \
  -o ~/.copilot/skills/diagnose/SKILL.md
# Then reference it from your global Copilot instructions file.
```

### Gemini (global)
```bash
mkdir -p ~/.gemini/skills/diagnose
curl -fsSL https://raw.githubusercontent.com/mattpocock/skills/main/skills/engineering/diagnose/SKILL.md \
  -o ~/.gemini/skills/diagnose/SKILL.md
```

### Via agent-settings import-skills.sh (project-local)
```bash
# If using this agent-settings repo, import it into a project:
.agent-settings/skills/import-skills.sh claude diagnose     # Claude / Copilot
.agent-settings/skills/import-skills.sh gemini diagnose     # Gemini
```

> The diagnose skill must be visible to your agent before proceeding.

---

Reads active PR threads and resolves them by applying fixes, with user consent at every step.

---

## Step 1 — Parse the PR URL

Extract `org`, `project`, `repo`, `prId` from the URL:
```
https://dev.azure.com/{org}/{project}/_git/{repo}/pullrequest/{prId}
https://{org}.visualstudio.com/{project}/_git/{repo}/pullrequest/{prId}
```

---

## Step 2 — Fetch active comment threads

Call `mcp_azure_devops__repo_list_pull_request_threads` with `status: Active`.

For each thread that has a `threadContext` (file + line), extract:
- `filePath` — the file the comment is on
- `line` — the right-side line number
- `comment` — the full comment content
- `threadId` — needed to mark resolved later

Skip system threads (reviewer added, branch updated, etc.) — only process human-authored comment threads.

---

## Step 3 — Read file content for each thread

For each active thread, call `mcp_azure_devops__repo_get_file_content` to get the current file at the PR's source branch. Extract the surrounding context (±20 lines around the flagged line).

---

## Step 4 — Triage: classify each finding

Classify every thread as **Trivial** or **Non-trivial**:

### Trivial (can apply directly)
- Change is ≤ ~15 lines, localized to one function, struct, or block
- The suggestion in the comment provides a clear before→after
- No interface changes, no cross-file ripple effects
- Examples: add a binding tag, remove a field from a DTO, add a nil check, add a `code` field to an error response, rename a field

### Non-trivial (needs a plan first)
- Change touches multiple files or multiple call sites
- Alters a public interface, type definition, or shared utility
- Requires understanding broader context (e.g. "all callers must update")
- The refactor is structural (e.g. extract function, change error contract across handlers)
- Examples: rename a field that appears in 10 files, change an error response struct used by all handlers, add middleware-level validation

---

## Step 5 — Present triage summary to user

Before touching any code, show a triage table and ask for consent:

```
## PR Comment Resolver — Triage

Found {N} active comment threads with file context.

### ✅ Trivial fixes ({count}) — can apply with your approval:
| # | File | Line | Summary |
|---|---|---|---|
| 1 | main.go | 50 | Add `min=1` binding to `Values` field |
| 2 | constant.go | 10 | Remove unused `CODE_INTERNAL_SERVER_ERROR` |
| ... |

### 🔧 Non-trivial — needs a refactoring plan first:
| # | File | Line | Summary |
|---|---|---|---|
| 3 | main.go | 208 | Remove raw AWS struct from response (check all callers) |
| ... |

### ⏭️ Skipped (no suggestion or already resolved):
| # | Thread | Reason |
|---|---|---|
| ... |

---
How would you like to proceed?
- Type **"all trivial"** to review and apply all trivial fixes together
- Type **"plan non-trivial"** to get the refactoring plan for non-trivial items
- Type a number (e.g. **"1, 3"**) to pick specific items
- Type **"skip"** to exit without changes
```

Wait for the user's response before proceeding.

---

## Step 6 — Apply trivial fixes (with per-fix consent)

For each trivial fix the user approved:

1. **Show the diff** — display the before/after for that specific change:

```
### Fix #1 — main.go line 50

**Before:**
```go
Values []string `json:"values" binding:"required"`
```

**After:**
```go
Values []string `json:"values" binding:"required,min=1"`
```

Apply this fix? (yes / skip)
```

2. **Wait for confirmation** per fix, or if the user said "all trivial", confirm the full batch once with the complete diff before applying.

3. **Apply the change** using the file editing tool.

4. **Reply to the ADO thread** using `mcp_azure_devops__repo_reply_to_comment`:
```
✅ Fixed: {one-line description of what was applied}.
```

5. **Mark the thread as resolved** using `mcp_azure_devops__repo_update_pull_request_thread` with `status: Fixed`.

---

## Step 7 — Refactoring plan for non-trivial items

For each non-trivial item the user wants to address:

### 7a — Analyse the scope

Before writing the plan:
- Fetch all files likely affected (search for the symbol/field/function across the repo if needed)
- Identify every call site, usage, or dependent type
- Assess risk: breaking change? Requires coordinated deploy? Needs test update?

### 7b — Present the plan

```
## Refactoring Plan — #{number}: {short title}

### What needs to change
{1-2 sentence description of the root issue}

### Files affected
| File | Change required |
|---|---|
| main.go | Remove `AliasTarget`, `TTL`, `Weight` from response struct |
| main.go | Update all 3 call sites of `serializeRecord()` |
| main_test.go | Update fixture to match new response shape |

### Steps (in order)
1. Define a new `RecordResponse` projection struct with only `fqdn`, `domain`, `type`
2. Replace `"record": r` with `"record": toRecordResponse(r)` at lines 208, 312, 418
3. Update test fixtures in `main_test.go`

### Risk assessment
- **Breaking change for callers?** {Yes/No — explain}
- **Requires coordinated deploy?** {Yes/No}
- **Test coverage affected?** {Yes/No}

### Estimated scope
~{N} lines changed across {M} files

---
Proceed with this plan? (yes / revise / skip)
```

Wait for user response.

### 7c — Execute step by step

If the user approves:
- Execute **one step at a time**
- After each step, show what was changed and pause:
  ```
  Step 1 complete — defined `RecordResponse` struct in main.go.
  Continue to step 2? (yes / pause / stop)
  ```
- On `pause` or `stop`, summarise what is done and what remains, so the user can continue later

### 7d — Reply and resolve

After all steps are complete, reply to the ADO thread:
```
✅ Refactored: {short description of what changed and which files were modified}.
```
Mark thread as `Fixed`.

---

## Step 8 — Final summary

After all selected items are processed:

```
## Resolution Summary

✅ Applied ({count}): {list of files + one-line summaries}
🔧 Refactored ({count}): {list of files + plan titles}
⏭️ Skipped ({count}): {list with reason}

All resolved threads have been marked as Fixed in the PR.
```

---

## Rules

- **Never apply a change without showing a diff and getting explicit user confirmation first.**
- If a trivial fix has an unclear suggestion, escalate it to non-trivial and generate a plan.
- If a file cannot be fetched or the diff cannot be constructed, skip and note it in the summary.
- Do not mark a thread as `Fixed` until the code change has been confirmed applied.
- If the user says `stop` at any point, stop immediately, summarise what was done, and list what remains.

---

## Using the `diagnose` skill before applying fixes

### When to invoke `diagnose`

Before applying any fix — trivial or non-trivial — use the `diagnose` skill when:

- The PR comment says the issue exists but the **root cause is unclear** from the comment alone
- You are about to apply a fix but are **not confident** the suggestion fully addresses the underlying issue
- The fix touches a code path that has **no tests** and the failure mode cannot be verified statically
- A non-trivial refactoring plan involves **multiple callers** and you need to confirm all affected paths before presenting the plan

### How to apply it

**Before a trivial fix:**
1. Run `diagnose` Phase 1 — build a minimal repro (e.g. a failing test or curl) that confirms the issue
2. Run `diagnose` Phase 3 — confirm the fix addresses the right root cause, not a symptom
3. Proceed with the before/after diff and user consent as normal
4. After applying, run the loop again to confirm the fix works (Phase 5)

**Before a non-trivial refactoring plan:**
1. Run `diagnose` Phase 1 — build a loop that reproduces the problem across the affected call sites
2. Run `diagnose` Phase 3 — rank hypotheses for why the structural issue exists
3. Use the loop and hypotheses to build an accurate, scoped refactoring plan (Step 7b)
4. Include the reproduction evidence in the plan so the user can verify it themselves

**If no feedback loop is possible** (external service, env not available):
- Note it explicitly in the triage table under the finding
- Mark the fix as `⚠️ Unverified — static analysis only` in the before/after diff
- Still require user consent before applying
