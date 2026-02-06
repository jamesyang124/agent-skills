---
name: git-commit-conventional-cliff-optimized
description: 專為 git-cliff 優化的嚴格版 Conventional Commits 生成器，支援 SemVer 與 Emoji。
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
2.  **Detect Commit Split Requirements**: Check if changes include both spec/doc files AND implementation files.
    - **Spec/Doc files**: Files in `doc/`, `spec-kit/`, or `*.md` files (except root-level README.md)
    - **Implementation files**: Source code, tests, configuration files
    - If BOTH types are present, split into separate commits (see Commit Splitting Strategy below)
3.  **Determine SemVer**: Is this a Patch (fix), Minor (feat), or Major (Breaking) change?
4.  **Identify Scope**: Which module constitutes the primary scope (e.g., auth, ui, deps)?
5.  **Draft Message**:
    - If Breaking: Use type!: format.
    - Select appropriate Emoji.
    - Write imperative subject.
6.  **Execute Commit**: Use standard git commit command with the -m flag and include the Co-Authored-By line.

## Commit Splitting Strategy

When changes include BOTH spec/documentation files AND implementation files, create separate commits in this order:

### 1. Spec/Documentation Commit First
**Pattern**: `docs(scope): 📝 [description of spec/doc changes]`
- Include all files in `doc/`, `spec-kit/`, and related markdown files
- Use `docs` type even if the spec describes a new feature
- Focus the message on what specifications/documentation changed

### 2. Implementation Commit Second
**Pattern**: `[type](scope): [emoji] [description of implementation]`
- Include source code, tests, and configuration files
- Use appropriate type (feat, fix, refactor, etc.) based on the implementation
- Reference the spec commit if helpful: "per updated spec in [commit-hash]"

### Why This Order?
- Specs/docs define the "what" before implementation defines the "how"
- Easier code review: reviewers can understand requirements first
- Better git history: clear separation of design vs implementation
- Allows spec changes to be cherry-picked or reverted independently

### Example Workflow
```bash
# Given changes to both doc/api-spec.md and src/api/handler.go

# Commit 1: Documentation
git add doc/api-spec.md spec-kit/examples/
git commit -m "docs(api): 📝 add user authentication endpoint spec"

# Commit 2: Implementation
git add src/api/handler.go src/api/handler_test.go
git commit -m "feat(api): ✨ implement user authentication endpoint"
```

## Examples
- **Standard Feature**: feat(auth): ✨ add google login support
- **Bug Fix**: fix(ui): 🐛 prevent crash on empty input
- **Breaking Change**: feat(api)!: 💥 remove v1 endpoints
- **Documentation**: docs: 📝 update contribution guidelines
- **Spec + Implementation (split)**:
  - Commit 1: `docs(api): 📝 define product search filtering spec`
  - Commit 2: `feat(api): ✨ implement product search filtering`

## Usage Notes

### Commit Splitting Detection
When analyzing changes, always check for mixed file types:
```bash
# Check what types of files changed
git diff --name-only

# If you see BOTH:
# - doc/, spec-kit/, or .md files AND
# - src/, lib/, or other implementation files
# Then split into two commits
```

### Interactive Staging for Split Commits
Use `git add` with specific paths to stage files separately:
```bash
# Stage only spec/doc files
git add doc/ spec-kit/ '*.md'

# Stage only implementation files
git add src/ lib/ test/ config/
```

**Git Commit Command**: This skill uses standard git commit commands with the -m flag. The Bash tool automatically handles any necessary escaping for special characters. Keep commit messages straightforward and let the tool handle the execution details.

### When NOT to Split
- **Don't split** if changes are only in one category (all docs OR all code)
- **Don't split** root-level README.md updates - treat as docs
- **Don't split** inline code comments/docstrings - treat as implementation
- **Don't split** if spec and code are trivial (e.g., typo fixes in both)