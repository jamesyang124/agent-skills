# git-commit-conventional-strict

## Overview

Strict Conventional Commits generator optimized for `git-cliff`, with SemVer and Emoji support. Analyzes staged changes, determines the correct type/scope, and executes the commit — including automatic detection of when to split doc and implementation changes into separate commits.

## When to Use

- Committing code changes with a conventional format
- Asked to "commit with conventional format", "semantic versioning", "emoji commits", or "gitmoji"
- Any commit in a repo that uses `git-cliff` for changelog generation

## Commit Format

```
type(scope): emoji subject

optional body (bullets for multiple points)

optional footer (BREAKING CHANGE: ..., Refs: PROJ-1234)
```

## Type → SemVer Mapping

| Type | SemVer | Emoji |
|---|---|---|
| `feat!` / `fix(x)!` | **Major** (breaking) | 💥 |
| `feat` | Minor | ✨ |
| `fix` | Patch | 🐛 |
| `docs` | no bump | 📝 |
| `refactor` | no bump | ♻️ |
| `perf` | no bump | ⚡️ |
| `test` | no bump | ✅ |
| `build` | no bump | 📦 |
| `ci` | no bump | 👷 |
| `chore` | no bump | 🔧 |
| `style` | no bump | 💄 / 🎨 |

## Commit Splitting

When staged changes include **both** spec/doc files (`doc/`, `spec-kit/`, `*.md`) **and** implementation files (source, tests, config), the skill automatically splits into two commits:

1. **Docs first**: `docs(scope): 📝 [spec/doc changes]`
2. **Implementation second**: `[type](scope): [emoji] [implementation]`

Do not split for root-level `README.md` updates, inline code comments, or trivial changes spanning both categories.

## Usage

```
/git-commit-conventional-strict
```

The skill will:
1. Read the staged diff
2. Detect if a split is needed
3. Ask for an optional Jira ticket ID (`PROJ-1234` or `n` to skip)
4. Execute the commit(s) with `Co-Authored-By: Claude` appended

## Notes

- Jira ticket appears as a footer: `Refs: PROJ-1234` (not in the subject line)
- Breaking changes use `!` after type/scope: `feat(api)!: 💥 remove v1 endpoints`
- Subject stays under 50 characters when possible; emoji goes after the colon
- Multi-point bodies use bullet lists, not run-on prose
