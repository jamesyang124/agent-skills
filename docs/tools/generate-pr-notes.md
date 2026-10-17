# generate-pr-notes

## Overview

Automatically generate pull request notes based on git changes. Analyzes commits or branch diffs and fills the shared PR template (`.agent-settings/skills/tools/generate-pr-notes/references/pull_request_template.md`). The same template is used by `ado-open-pr` and can be copied into a repo as `.azuredevops/pull_request_template.md`.

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
## Title            [TICKET-ID] sentence (≤128 chars) + Jira: link
## Summary          2-4 sentences: what changed and why
## Changes          at most 5 bullets: ✨ feature, 🐛 fix, 🔧 config
## API impact       routes added / changed / removed, each backward compatible | potentially breaking | breaking
## Compatibility    breaking-change evidence and the repo constitution check
## Deploy notes     env vars, migrations, deploy order
## Spec impact      specs updated, or why not
## Tests            tests added, or why not
```

## Notes

- Total output is capped at 3000 words — large diffs are summarized, not dumped
- Each detail appears in only one section (no cross-section redundancy)
- Remote branch is always preferred as the diff base (falls back to local with a warning)
- A checklist item is ticked only when the diff shows it is true
