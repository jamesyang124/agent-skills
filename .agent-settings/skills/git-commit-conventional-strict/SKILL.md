---
name: git-commit-conventional-strict
description: 移植自 Cursor Directory 的嚴格版 Conventional Commits 規範，包含 Emoji 與 Breaking Change 處理。
---

# Git Commit Generator (Strict Mode)

You are an expert in Semantic Versioning and Conventional Commits.

## Rules
1.  **Format**: `<type>(<scope>): <subject>`
2.  **Subject**:
    - Imperative tone (e.g., "add" not "added", "fix" not "fixed").
    - No dot (.) at the end.
    - Max 50 chars.
3.  **Scope**:
    - Must be a noun describing the section of the codebase (e.g., `auth`, `ui`, `deps`).
4.  **Line Length**:
    - Each line of the commit message should not exceed 120 characters.
5.  **Types**:
    - `feat`: A new feature
    - `fix`: A bug fix
    - `docs`: Documentation only changes
    - `style`: Changes that do not affect the meaning of the code (white-space, formatting, etc)
    - `refactor`: A code change that neither fixes a bug nor adds a feature
    - `perf`: A code change that improves performance
    - `test`: Adding missing tests or correcting existing tests
    - `build`: Changes that affect the build system or external dependencies
    - `ci`: Changes to our CI configuration files and scripts
    - `chore`: Other changes that don't modify src or test files

## Emoji Guide (Optional but Recommended)
- 🐛 `fix`: Fix a bug
- ✨ `feat`: Introduce new features
- 📝 `docs`: Add or update documentation
- 🚀 `perf`: Improve performance
- ♻️ `refactor`: Refactor code
- 🏗️ `build`: Build system changes
- 👷 `ci`: CI configuration changes

## Process
1.  Analyze the `git diff`.
2.  Identify the primary `scope`.
3.  Draft the `subject`.
4.  If the change involves logic (not just style), write a `body` explaining the "why".
