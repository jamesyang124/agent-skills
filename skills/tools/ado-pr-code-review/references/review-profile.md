# Pre-PR review profile

Which pre-PR reviewers run for each repository, and what they should know about it. Used by:

- `ado-open-pr` — Step 1.7 (pre-PR review)

Reviewer keys: `code`, `security`, `standards`, `tests`, `minimal` (`refactor` is an old name for `minimal`). A
repository that is not listed runs all five. The orchestrator runs the lint command on the changed code (new problems only). The test command is a
reference for the author after fixes are applied; nothing runs it without approval.

Replace the example rows below with your own repositories.

| Repository | Reviewers | Lint command | Test command | Focus notes |
|---|---|---|---|---|
| example-api | all | `golangci-lint run --new-from-rev=<base> ./...` | `make test` | Go API service. Check context cancellation, DB transactions and cache keys. |
| example-web | all | `pnpm exec eslint <changed files>` | `pnpm test` | React app. Check effect cleanup, listener leaks and server-only secrets kept out of client bundles. |
| example-phoenix | code,security,tests | `mix format --check-formatted <changed files>` | `mix test` | Elixir / Phoenix. lizard does not read Elixir. |

## How to read it

- **Reviewers:** `all`, or a comma-separated list of keys (for example `code,security,tests`).
  The `--review=<keys>` argument of `ado-open-pr` overrides this column for one run.
- **Lint command:** `<base>` is `git merge-base origin/<target-branch> HEAD`; `<changed files>` are the files this
  PR changes, filtered to the linter's language. `none` skips lint for that repository.
- **Focus notes:** passed to every reviewer as extra context, only for repositories that have no
  `review-rules/<repo>.md` yet. When a repository gets a rules file, move its notes there and point this column
  at the file. This table keeps the machine-read settings (reviewers, lint, test); the review rules hold the text.

## Keeping it current

Add or change a row when the team agrees on it. Base the test command on the repository's own `Makefile`,
`package.json` or CI pipeline.
