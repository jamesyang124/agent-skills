# generate-pr-notes

## Overview

Automatically generate pull request notes based on git changes. Analyzes commits or branch diffs and creates comprehensive PR descriptions with a title, summary, changes, technical details, and breaking changes.

## When to Use

- Creating a PR and need a description written
- Summarizing branch changes for review
- Asked to "generate PR notes" or "write PR description"

## Usage

```
/generate-pr-notes [base-branch]
```

The skill interactively asks three questions before generating:
1. **Scope** — single commit (latest only) or entire branch vs. a base branch
2. **Base branch** — `main`, `master`, `release`, or a custom branch/commit hash
3. **Jira ticket ID** — optional; if provided, prefixes the PR title as `[PROJ-1234] ...`

After generation, the notes are:
- Displayed verbatim in the terminal
- Saved to `/tmp/pr-notes-<repo>-<hash>.md`
- Copied to clipboard (macOS/Linux/Windows)

## Output Structure

```markdown
## Title
[TICKET-ID] Short sentence describing the PR  ← Jira prefix only if provided

## Summary
2-4 sentences about what changed and why

## Changes
### ✨ New Features   (max 5 items)
### 🐛 Bug Fixes
### 🔧 Configuration

## Technical Details  (max 5 items)

## Breaking Changes   (if applicable)
```

## Notes

- Total output is capped at 3000 words — large diffs are summarized, not dumped
- Each detail appears in only one section (no cross-section redundancy)
- Remote branch is always preferred as the diff base (falls back to local with a warning)
- Testing section is intentionally excluded from output
