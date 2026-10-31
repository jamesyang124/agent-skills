# PR target branch map

Which branch a normal feature PR should merge into, per repository. Used by:

- `ado-pr-code-review` — Step 2.5 Check 0 (merge direction)
- `ado-open-pr` — the default target branch

A repository's ADO default branch is not always where PRs go: some point at a branch that has not moved
in years. Trust this table first. For a repository that is not listed, fall back to the ADO default branch,
and if that branch's last commit is more than 90 days old, say it may not be the real target and ask.

Replace the example rows below with your own repositories.

| Repository | PR target | Other branches PRs may target |
|---|---|---|
| example-api | `master` | `release/YYYYMMDD` for a fix to a release in progress; the CI/CD pipeline opens the `[Backport] release/… → master` PR itself, so the author does not open one. `develop` is **not** a PR target. |
| example-web | `main` | `hotfix/*` |
| example-legacy | `develop` | The ADO default branch `master` is stale; do not target it. |

## How to read it

- **Target matches "PR target":** normal.
- **Target is listed under "Other branches PRs may target":** allowed. Show the note (for example the
  backport reminder) in the review summary.
- **Target is anything else:** show the merge target warning and ask the author to confirm it.

## Keeping it current

Add a repository when the team agrees on its PR target. Base each row on where completed PRs actually
merge (for example `git log --first-parent --format=%s origin/<branch> | grep -c '^Merged PR'` over the last
two months), not only on the ADO default branch.
