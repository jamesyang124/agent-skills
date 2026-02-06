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
   - Determine if the user wants notes for:
     - A single commit (the most recent commit), OR
     - The entire branch's changes compared to main/master
   - If unclear from context, use AskUserQuestion to ask the user which scope they prefer

2. **Retrieve the diff:**
   - For single commit: Use `git show HEAD` or `git diff HEAD~1 HEAD`
   - For branch changes:
     - Identify the remote base branch (origin/main or origin/master)
     - First run `git fetch origin` to ensure remote refs are up to date
     - Use `git diff origin/main...HEAD` or `git diff origin/master...HEAD` (with three dots for the merge base)
     - **Always use the remote branch (origin/main or origin/master) as the base, not the local branch**

3. **Analyze the changes:**
   - Review all modified files
   - Identify the nature of changes (new features, bug fixes, refactoring, etc.)
   - Look for patterns and group related changes together

4. **Generate comprehensive PR notes with the following sections:**

   **## Title**
   - Provide a single-sentence title that describes the overall change

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
   [Single sentence describing the PR]

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
   - **STOP WRITING** immediately after the closing ```
   - Use `##` for main sections (Title, Summary, Changes, Technical Details, Breaking Changes)
   - Use `###` ONLY for change categories under Changes section
   - New Features section must have AT MOST 5 items
   - Technical Details section must have AT MOST 5 items
   - Each piece of information should appear in only ONE section - no redundancy

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
- **DO NOT include a Testing section in the output**
- Tailor the tone and detail level to the size and complexity of the changes
- If there are no changes to analyze, inform the user clearly
- Output must be clean markdown with no wrapper text for easy copy/paste
- **MANDATORY: The generated notes MUST be displayed in the terminal output for the user to copy/paste directly**
