# Review rules — example-api

An example repository file. Copy it to `review-rules/<your-repo>.md` (the Azure DevOps repository name) and
replace the content. It adds to `_default.md`; where both files have the same section, this file wins for that
section. If the repository has a constitution, cite its principle numbers in findings, for example
`[standards] Principle III — cache key omits locale`.

## Important means

- 🔴 Critical also covers: personal data returned by a public endpoint; a cache key that omits an input that
  changes the payload; a database connection or transaction that can outlive its request.

## Always check

- Every HTTP error response carries the error `code` field and follows the status convention.
- A behavior or contract change updates the owning spec and the API reference in the same PR.
- A non-trivial query is checked for index coverage.
- Values an operator may change per environment are env vars with a documented default.

## Skip

- Routes that are deprecated and answer `410 Gone` before any handler runs.
- `go.sum`.

## Nit cap

At most **5** 🔵 Minor comments (same as default).

## Higher bar

- `local/` (local stack, mock server, seed data): post only near-certain, severe findings.
