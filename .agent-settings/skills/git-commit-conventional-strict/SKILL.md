---
name: git-commit-conventional-cliff-optimized
description: A strict Conventional Commits generator optimized for git-cliff, supporting SemVer and Emoji.
---

# Git Commit Generator (Cliff Optimized)

You are an expert in Semantic Versioning (SemVer) and Conventional Commits. Your goal is to generate git commit messages that are machine-readable for tools like `git-cliff` while remaining human-readable.

## Core Rules

1.  **Structure**:
    - Default: type(scope): emoji subject
    - Breaking Change: type(scope)!: emoji subject
    - Note: Scope is optional but recommended.
    - Keep messages simple and avoid special shell characters in examples

2.  **Types & SemVer Mapping**:
    Select the type based on the nature of the change and its impact on Semantic Versioning:
    - **Major (💥 BREAKING CHANGE)**:
        - Syntax: Add exclamation mark after the type/scope (e.g., feat!:, fix(api)!:)
        - Use when the change breaks backward compatibility.
    - **Minor (feat)**:
        - feat: A new feature.
    - **Patch (fix)**:
        - fix: A bug fix.
    - **No Version Bump (General)**:
        - docs: Documentation only changes.
        - style: Formatting, missing semi-colons, etc (no code change).
        - refactor: A code change that neither fixes a bug nor adds a feature.
        - perf: A code change that improves performance.
        - test: Adding missing tests or correcting existing tests.
        - build: Changes that affect the build system or external dependencies.
        - ci: Changes to CI configuration files and scripts.
        - chore: Other changes that don't modify src or test files.

3.  **Subject Rules**:
    - **Imperative mood**: "add" not "added", "fix" not "fixed".
    - **No trailing punctuation**: Do not end with a period.
    - **Length**: Keep the subject under 50 characters if possible.
    - **Emoji Position**: If using emojis, place them after the colon, at the start of the subject. DO NOT place emojis before the type.

4.  **Body & Footer (Optional)**:
    - Use the body to explain "why" and "what", not "how".
    - For breaking changes, you MAY also add a footer: BREAKING CHANGE: followed by description.
    - For references, use: Refs: #123.

5.  **Git Commit Command Format**:
    - Use standard git commit with -m flag for the message
    - Keep commit messages simple and on a single line when possible
    - For multi-line messages, use standard git commit without special escaping
    - The Bash tool will handle any necessary escaping automatically

## Emoji Guide (Subject Prefix)
- feat: ✨ (Sparkles)
- fix: 🐛 (Bug)
- docs: 📝 (Memo)
- style: 💄 (Lipstick) or 🎨 (Art)
- refactor: ♻️ (Recycle)
- perf: ⚡️ (Zap)
- test: ✅ (White Check Mark)
- build: 📦 (Package)
- ci: 👷 (Construction Worker)
- chore: 🔧 (Wrench)
- breaking: 💥 (Boom) - Use this in addition to the exclamation mark syntax if emphasized.

## Analysis Process
1.  **Analyze**: Read the provided git diff or code changes.
2.  **Determine SemVer**: Is this a Patch (fix), Minor (feat), or Major (Breaking) change?
3.  **Identify Scope**: Which module constitutes the primary scope (e.g., auth, ui, deps)?
4.  **Draft Message**:
    - If Breaking: Use type!: format.
    - Select appropriate Emoji.
    - Write imperative subject.
5.  **Execute Commit**: Use standard git commit command with the -m flag and include the Co-Authored-By line.

## Examples
- **Standard Feature**: feat(auth): ✨ add google login support
- **Bug Fix**: fix(ui): 🐛 prevent crash on empty input
- **Breaking Change**: feat(api)!: 💥 remove v1 endpoints
- **Documentation**: docs: 📝 update contribution guidelines

## Usage Notes
**Git Commit Command**: This skill uses standard git commit commands with the -m flag. The Bash tool automatically handles any necessary escaping for special characters. Keep commit messages straightforward and let the tool handle the execution details.