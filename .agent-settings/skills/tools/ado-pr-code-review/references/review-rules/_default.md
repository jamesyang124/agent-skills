# Review rules — default (all repositories)

Applied to every repository. A repository file `review-rules/<repo>.md` adds to these rules; where both files
have the same section, the repository file wins for that section. Read by `ado-pr-code-review` and by
`ado-open-pr` Step 1.7, and passed to every reviewer and to the verifier.

## Important means

- 🔴 Critical: a security hole, lost or wrong data, a crash on a reachable path, a broken API or data contract,
  or a leak that grows with traffic.
- 🟡 Medium: a real defect with bounded impact — wrong behavior on an edge case, a missing guard, a missing test
  for new or changed behavior.
- 🔵 Minor: clarity or maintainability. Never block on it.

## Always check

- New or changed behavior has a test, or the PR says why not.
- An API change (route, field, status code, validation) says whether it is backward compatible, potentially
  breaking or breaking, and a breaking change has a migration or versioning plan.
- Secrets, tokens and credentials are not added to code, config, docs or PR text.
- The PR description matches the net diff.

## Skip

- Lock files and dependency checksums (`*.lock`, `package-lock.json`, `pnpm-lock.yaml`, `go.sum`, `mix.lock`),
  unless the change is the point of the PR.
- Generated files (marked "generated", "DO NOT EDIT", or produced by a codegen tool) and vendored code.
- Anything the repository's linter or formatter enforces.

## Nit cap

At most **5** 🔵 Minor comments per review. Pick the most useful ones and count the rest in the summary.

## Higher bar

None by default. A repository file can name paths where only near-certain, severe findings are posted.
