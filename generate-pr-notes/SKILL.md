---
name: generate-pr-notes
description: Automatically generate pull request notes based on git changes. Analyzes commits or branch diffs and creates comprehensive PR descriptions with summary, changes, technical details, testing steps, and breaking changes.
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
     - Identify the base branch (main or master)
     - Use `git diff main...HEAD` or `git diff master...HEAD` (with three dots for the merge base)

3. **Analyze the changes:**
   - Review all modified files
   - Identify the nature of changes (new features, bug fixes, refactoring, etc.)
   - Look for patterns and group related changes together

4. **Generate comprehensive PR notes with the following sections:**

   **## Summary**
   - Provide a concise overview of what changed and why (2-4 sentences)
   - Focus on the "why" and business value, not just the "what"

   **## Changes**
   - List key changes organized by category:
     - ✨ New Features
     - 🐛 Bug Fixes
     - ♻️ Refactoring
     - 📝 Documentation
     - 🎨 UI/UX
     - ⚡ Performance
     - 🔧 Configuration
     - 🧪 Tests
   - Use only categories that are relevant
   - Be specific but concise for each item

   **## Technical Details**
   - Highlight important implementation details
   - Note any architectural changes or patterns introduced
   - Mention dependencies added or updated

   **## Testing**
   - Suggest testing steps or scenarios
   - Note if automated tests were added/updated

   **## Breaking Changes** (if applicable)
   - Clearly call out any breaking changes
   - Provide migration guidance if needed

5. **Format the output:**
   - Use clear markdown formatting
   - Keep it concise but informative
   - Focus on what reviewers need to know

## Important Notes

- Always read the actual diff before generating notes - never make assumptions
- If the diff is very large, summarize thoughtfully rather than listing every change
- Tailor the tone and detail level to the size and complexity of the changes
- If there are no changes to analyze, inform the user clearly
