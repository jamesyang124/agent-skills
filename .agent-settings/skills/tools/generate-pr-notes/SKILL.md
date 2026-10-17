---
name: generate-pr-notes
description: Automatically generate pull request notes based on git changes. Analyzes commits or branch diffs and fills the shared PR template: title, summary, changes, API impact with compatibility classification, compatibility and constitution check, deploy notes, spec impact and tests. Use when creating a PR, writing PR description, summarizing changes for review, or asked to generate PR notes.
argument-hint: "[base-branch]"
allowed-tools: Bash(git *), Bash(uname *), Bash(pbcopy *), Bash(xclip *), Bash(xsel *), Bash(clip *), Read, Write
---

# Generate PR Notes

## Install this skill globally

Install once — available in all projects.

```bash
# Claude (copy the whole folder: the PR template lives in references/)
mkdir -p ~/.claude/skills
cp -R <agent-settings-repo>/.agent-settings/skills/tools/generate-pr-notes ~/.claude/skills/
# Add to ~/.claude/CLAUDE.md: - **generate-pr-notes** (`~/.claude/skills/generate-pr-notes/SKILL.md`)

# Copilot
mkdir -p ~/.copilot/skills
cp -R <agent-settings-repo>/.agent-settings/skills/tools/generate-pr-notes ~/.copilot/skills/
```

Or link it with `.agent-settings/skills/import-skills.sh --global claude generate-pr-notes`.

## Dependencies

No external skills or MCPs required. Requires `git` to be available in the shell.

---

Automatically generate pull request notes based on git changes.

## Description

This skill analyzes git changes and generates comprehensive pull request notes. It can work with either a single commit or all changes in the current branch compared to the main/master branch.

## Usage

```
/generate-pr-notes
```

## Arguments

All optional.

| Token | Meaning |
|---|---|
| a branch name (e.g. `develop`) | base branch to diff against — skips the base-branch question in step 1 |

Scope (last commit vs. entire branch) is always asked; it is not an argument.

---

## Instructions

Use the Task tool with subagent_type="general-purpose" to spawn an agent that will generate pull request notes. Pass the following instructions to the agent.

**CRITICAL: After the agent completes, follow these steps IN ORDER:**

1. **Output verbatim** — display the agent's full response exactly as returned in the terminal. Do NOT summarize or modify it.

2. **Extract content** — strip the outer ` ```markdown ` opening fence and the closing ` ``` ` fence from the agent output to get the raw markdown text only.

3. **Determine output path** — before writing, run these two commands via Bash:
   - Repo name: `basename $(git rev-parse --show-toplevel)`
   - Short hash: `git rev-parse --short HEAD`
   Construct the output path as `/tmp/pr-notes-<repo-name>-<short-hash>.md` (e.g. `/tmp/pr-notes-agent-skills-a1b2c3d.md`).
   Use the Write tool to save the extracted markdown to that path.

4. **Copy to clipboard** — detect the OS by running `uname -s` via Bash, then use the appropriate command (substitute the computed path from step 3):
   - macOS (`Darwin`): `pbcopy < <output-path>`
   - Linux (`Linux`): try `xclip -selection clipboard < <output-path>`; if that fails, try `xsel --clipboard --input < <output-path>`
   - Windows / PowerShell (`Windows_NT`): try `clip < <output-path>`
   - If all commands fail or the platform is unrecognized, skip silently.

5. **Confirm to user** — print exactly ONE line after the code block output (use the actual computed path from step 3):
   - If clipboard copy succeeded: `PR notes saved to <output-path> and copied to clipboard.`
   - If clipboard copy failed or unavailable: `PR notes saved to <output-path> (clipboard unavailable — paste manually from the file).`

---

You are a specialized agent for generating pull request notes. Follow these steps:

1. **Determine the scope of changes:**
   - First, check the current git status and branch information
   - Interactively ask the user the following THREE questions (use whatever input mechanism your agent supports — interactive prompt, structured options, or chat):
     1. Which scope they prefer:
        - "Single commit" (the most recent commit only)
        - "Entire branch" (all changes compared to a base branch)
     2. Which base branch to compare against (ask upfront regardless of scope, it applies when "Entire branch" is selected):
        - "main"
        - "master"
        - "release"
        - "Other" — if selected, follow up with a free-text prompt asking the user to type in the branch name or commit hash manually
     3. Jira ticket ID (optional, free-text):
        - Ask: "Jira ticket ID? Type the ID (e.g. PROJ-1234) or type n to skip"
        - Treat any of the following as "no ticket": `n`, `no`, `none`, `skip`, `n/a`, `-`
        - If a real ticket ID is given, prefix the Title with it in square brackets: `[PROJ-1234] Your title here`
        - Otherwise omit any Jira reference entirely

2. **Retrieve the diff:**
   - For single commit: Use `git show HEAD` or `git diff HEAD~1 HEAD`
   - For branch changes:
     - Use the base branch or commit hash selected by the user in step 1
     - First run `git fetch origin` to ensure remote refs are up to date
     - If the input is a branch name: Use `git diff origin/<base-branch>...HEAD` (with three dots for the merge base), substituting the user's chosen branch
     - If the input looks like a commit hash: Use `git diff <commit-hash>...HEAD`
     - **Always prefer the remote branch (e.g. origin/main, origin/master, origin/release) as the base over local branches**
     - If the remote ref does not exist, fall back to the local branch and warn the user

3. **Analyze the changes:**
   - Review all modified files
   - Identify the nature of changes (new features, bug fixes, refactoring, etc.)
   - Look for patterns and group related changes together

4. **Fill the PR template.** Read `references/pull_request_template.md` in this skill's folder. It is the one
   template for PR notes, for `ado-open-pr`, and for repos that copy it as `.azuredevops/pull_request_template.md`.
   Keep every heading, its order and every checklist item word for word, and fill each section:

   **## Title**
   - One short sentence that describes the overall change. **At most 128 characters**, Jira prefix included.
   - With a Jira ticket, prefix it in square brackets (`[TICKET-ID] Your title here`) and fill the next line:
     `Jira: https://your-org.atlassian.net/browse/TICKET-ID`. Without a ticket, drop the prefix and the `Jira:` line.

   **## Summary**
   - What changed and why, in 2-4 sentences. Focus on the "why" and the value, not only the "what".

   **## Changes**
   - At most 5 bullets, the most important first, each starting with ✨ (feature), 🐛 (fix) or 🔧 (config / chore).
   - Add a sub-bullet only for an implementation detail a reviewer needs: an architectural change, a new pattern,
     a dependency added or updated.

   **## API impact**
   - Backend: every route the diff adds, changes or removes (router registrations, handlers, swagger, `api-spec.md`).
   - Client app: every backend route the diff starts calling, calls differently, or stops calling.
   - One sub-bullet per route: `` `METHOD /path` — added | changed | removed — what changed — classification ``.
     Classification: **backward compatible** (every request accepted before is still accepted with the same meaning),
     **potentially breaking** (an existing caller can get a new error or must send a new field or value), or
     **breaking** (a request accepted before is now rejected, or its meaning changes).

   **## Compatibility**
   - Tick the item that matches the strongest classification in API impact. For potentially breaking or breaking,
     write the affected consumers, before → after, deploy order, rollback, and the compatibility window or new version.
   - If the repo has a constitution (`.specify/memory/constitution.md`, or `openspec/project.md`), read it and tick
     the principles item: name each principle the diff touches (for example `Principle III`) and how it complies.
     Without a constitution, leave that item unticked and add `(no constitution in this repo)`.

   **## Deploy notes / ## Spec impact / ## Tests**
   - Tick each item only when the diff shows it is true, and add sub-bullets with the evidence: env var names and
     values per environment, migration scripts, deploy order, spec files changed, test files and the cases they cover.
   - When a "No …" item applies, tick it and give the reason.

5. **Format the output - CRITICAL FORMATTING REQUIREMENTS:**

   **WORD COUNT LIMIT: The entire output must NOT exceed 3000 words. Keep the content concise and focused.**

   **AVOID REDUNDANCY: Do not repeat information across sections. Each detail should appear only once in the most appropriate section.**

   **YOUR ENTIRE RESPONSE MUST BE WRAPPED IN A MARKDOWN CODE BLOCK:**

   Output the filled template from step 4 inside one ```` ```markdown ```` block.

   **ABSOLUTE RULES - NO EXCEPTIONS:**
   - First line MUST be exactly: ````markdown`
   - Second line MUST be exactly: `## Title`
   - Last line MUST be exactly: ````
   - **TITLE LENGTH: The title line must NOT exceed 128 characters — use a short, direct sentence**
   - **STOP WRITING** immediately after the closing ```
   - Use exactly the `##` sections of the template, in its order. Do not add, rename or drop a section.
   - Changes has AT MOST 5 bullets
   - Each piece of information should appear in only ONE section - no redundancy
   - **LINE LENGTH: Every line must NOT exceed 250 characters. If a sentence is too long, split it into two separate bullet points or shorten it.**

   **FORBIDDEN - NEVER INCLUDE THESE:**
   - Any text before ````markdown`
   - Any text after the closing ```
   - Separators like `---` or `===` anywhere in the markdown content
   - Headers like "Pull Request Notes" or "PR Description"
   - "Files Changed:" sections or file statistics
   - Phrases like "Here are the notes:", "Based on...", "Perfect!", etc.
   - Agent IDs or metadata

   **CRITICAL:** Your response must be ONLY the markdown code block. The user should be able to copy everything between (and including) the ````markdown` and closing ``` for use in their PR description.

6. **OUTPUT TO TERMINAL - MANDATORY:**
   - After you generate the PR notes, they MUST be displayed in the terminal
   - The calling assistant will output your response verbatim to the user, then also write the content to a `/tmp/pr-notes-<repo-name>-<short-hash>.md` file and attempt to copy it to the clipboard
   - Do NOT add any additional commentary after generating the notes

## Important Notes

- Always read the actual diff before generating notes - never make assumptions
- If the diff is very large, summarize thoughtfully rather than listing every change
- **MANDATORY: The total output must not exceed 3000 words - be concise and prioritize the most important information**
- **MANDATORY: Changes must contain at most 5 bullets - focus on the most important changes**
- **MANDATORY: Avoid redundant information - each detail should appear in only ONE section**
- **MANDATORY: Every line must NOT exceed 250 characters — split long sentences into separate bullet points or shorten them**
- **MANDATORY: Tick a checklist item only when the diff shows it is true**
- Tailor the tone and detail level to the size and complexity of the changes
- If there are no changes to analyze, inform the user clearly
- Output must be clean markdown with no wrapper text for easy copy/paste
- **MANDATORY: The generated notes MUST be displayed in the terminal output for the user to copy/paste directly**
