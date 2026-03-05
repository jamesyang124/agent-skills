---
name: generate-pr-notes
description: Automatically generate pull request notes based on git changes. Analyzes commits or branch diffs and creates comprehensive PR descriptions with a title, summary, changes, technical details, and breaking changes.
---

# Generate PR Notes

Automatically generate pull request notes based on git changes.

## Description

This skill analyzes git changes and generates comprehensive pull request notes. It can work with either a single commit or all changes in the current branch compared to the main/master branch.

## Usage

```
/generate-pr-notes
```

## Instructions

Use the Task tool with subagent_type="general-purpose" to spawn an agent that will generate pull request notes. Pass the following instructions to the agent.

**CRITICAL: After the agent completes, you MUST output the generated PR notes directly in the terminal by displaying the agent's response verbatim. Do NOT summarize or modify the output. The user needs the full markdown content in the terminal for copy/paste.**

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
        - Ask: "Jira ticket ID? (e.g. PROJ-1234 — press Enter or type n/no/none/skip to omit)"
        - Treat any of the following as "no ticket": blank/Enter, `n`, `no`, `none`, `skip`, `n/a`, `-`
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

4. **Generate comprehensive PR notes with the following sections:**

   **## Title**
   - Provide a single short sentence that describes the overall change
   - **Maximum 128 characters** (including any Jira prefix) — be concise and direct
   - If a Jira ticket ID was provided, prefix the title with it in square brackets: `[TICKET-ID] Your title here`
   - If no Jira ticket ID was provided, omit any prefix

   **## Summary**
   - Provide a concise overview of what changed and why (2-4 sentences)
   - Focus on the "why" and business value, not just the "what"

   **## Changes**
   - List key changes organized by category:
     - ✨ New Features (maximum 5 items - prioritize the most impactful features)
     - 🐛 Bug Fixes
     - 🔧 Configuration
   - Use only categories that are relevant
   - Be specific but concise for each item
   - Avoid redundant information that's already mentioned in other sections

   **## Technical Details**
   - Highlight important implementation details (maximum 5 items - prioritize the most critical technical updates)
   - Note any architectural changes or patterns introduced
   - Mention dependencies added or updated
   - Do not repeat information already covered in the Changes section

   **## Breaking Changes** (if applicable)
   - Clearly call out any breaking changes
   - Provide migration guidance if needed

5. **Format the output - CRITICAL FORMATTING REQUIREMENTS:**

   **WORD COUNT LIMIT: The entire output must NOT exceed 3000 words. Keep the content concise and focused.**

   **AVOID REDUNDANCY: Do not repeat information across sections. Each detail should appear only once in the most appropriate section.**

   **YOUR ENTIRE RESPONSE MUST BE WRAPPED IN A MARKDOWN CODE BLOCK:**

   Output this exact structure:

   ````
   ```markdown
   ## Title
   [TICKET-123] Single sentence describing the PR  ← include Jira prefix if provided, omit entirely if not

   ## Summary
   [2-4 sentences about what changed and why]

   ## Changes

   ### ✨ New Features
   - [item 1]
   - [item 2]
   - [maximum 5 items - only list the most important features]

   ### 🐛 Bug Fixes
   - [item]

   ### 🔧 Configuration
   - [item]

   ## Technical Details
   - [item 1]
   - [item 2]
   - [maximum 5 items - focus on critical technical updates, no repetition from Changes section]

   ## Breaking Changes
   [if applicable, otherwise omit this section entirely]
   ```
   ````

   **ABSOLUTE RULES - NO EXCEPTIONS:**
   - First line MUST be exactly: ````markdown`
   - Second line MUST be exactly: `## Title`
   - Last line MUST be exactly: ````
   - **TITLE LENGTH: The title line must NOT exceed 128 characters — use a short, direct sentence**
   - **STOP WRITING** immediately after the closing ```
   - Use `##` for main sections (Title, Summary, Changes, Technical Details, Breaking Changes)
   - Use `###` ONLY for change categories under Changes section
   - New Features section must have AT MOST 5 items
   - Technical Details section must have AT MOST 5 items
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
   - The calling assistant will output your response verbatim to the user
   - This ensures the user can directly copy/paste the notes from their terminal
   - Do NOT add any additional commentary after generating the notes

## Important Notes

- Always read the actual diff before generating notes - never make assumptions
- If the diff is very large, summarize thoughtfully rather than listing every change
- **MANDATORY: The total output must not exceed 3000 words - be concise and prioritize the most important information**
- **MANDATORY: New Features section must contain at most 5 items - focus on the most impactful features**
- **MANDATORY: Technical Details section must contain at most 5 items - focus on the most critical technical updates**
- **MANDATORY: Avoid redundant information - each detail should appear in only ONE section**
- **MANDATORY: Every line must NOT exceed 250 characters — split long sentences into separate bullet points or shorten them**
- **DO NOT include a Testing section in the output**
- Tailor the tone and detail level to the size and complexity of the changes
- If there are no changes to analyze, inform the user clearly
- Output must be clean markdown with no wrapper text for easy copy/paste
- **MANDATORY: The generated notes MUST be displayed in the terminal output for the user to copy/paste directly**
