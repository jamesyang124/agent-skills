# Pre-PR review — reviewer briefs

Used by `ado-open-pr` Step 1.7. Each reviewer runs as its own sub-agent with a clean context. The orchestrator
builds each prompt from **Common rules** + the reviewer's brief + the run inputs.

## Run inputs (filled in by the orchestrator)

- repository root and repository name
- diff range: `origin/<target-branch>...HEAD` (three-dot; committed work only)
- changed files: `git diff --name-only origin/<target-branch>...HEAD`
- this repository's review rules: `ado-pr-code-review/references/review-rules/_default.md` plus
  `review-rules/<repo>.md` if it exists (part 1 of `review-findings.md`), and the focus notes from
  `review-profile.md` for repositories that have no rules file yet
- the path of the sibling skill `ado-pr-code-review/SKILL.md` (same parent folder as `ado-open-pr`)
- for `standards`: the Jira ticket key (and its description / acceptance criteria if the Jira MCP can read it), the
  spec folder that Step 1.5 resolved, and the **pre-sync commit** captured in Step 1 (read the spec as it was before
  Step 1.5 synced it, with `git show <pre-sync commit>:<spec path>`)
- for `code`, `standards` and the verifier, when Step 1 found conflicts: the target's diff in the conflicting files
  and the instruction to check for collisions with it ("Target moved" in part 1 of `review-findings.md`)
- for `minimal`: the complexity measurements (see **Orchestrator: measurements**)

## Common rules (every reviewer)

- **Read only.** Do not edit, create or delete files. Do not commit, push, or run builds, tests or package
  managers. You may run `git diff`, `git log`, `git show` and read any file in the repository.
- **Review this change only.** Report problems that the diff introduces or touches. Read surrounding code to
  understand it, but do not report problems in code the diff does not touch unless the diff makes them worse.
- **Evidence.** Each finding names a file and a line in the PR head, and quotes or describes the code it is about.
  If you are not sure, report it as a `question` instead of a finding.
- **Do not repeat other reviewers.** Stay in your own area. Another reviewer covers the rest.
- **Return only a JSON array** in the finding format of the shared rules
  `ado-pr-code-review/references/review-findings.md` (severity, confidence, `verified`, evidence), empty if you
  found nothing, with no other text. Pass that section of the file into each reviewer's prompt.
- **Sources and finders follow parts 1 and 2 of the same file:** rule files and reference data from the target
  branch, read-only (no `checkout`, `switch`, `stash`, `reset`, `pull`), at most 6 sub-agents at once, the
  deep review, and the rule-file-edit check for the `standards` reviewer.

## code — correctness and runtime

Read **Step 4 — Runtime correctness and resource leaks** in `ado-pr-code-review/SKILL.md` and apply its method and
its table to this diff. Skip its **Verify** paragraph: in this pass you do not run checks. Also report logic errors,
wrong conditions, off-by-one, broken error handling and API contract changes that callers do not expect.

**API compatibility.** List every route the diff adds, changes or removes (or, in a client app, every backend route
it starts calling, calls differently, or stops calling), and classify each as **backward compatible**,
**potentially breaking** (an existing caller can get a new error or must send a new field or value) or **breaking**
(a request accepted before is now rejected, or its meaning changes). Report a potentially breaking or breaking change
that the diff does not handle (no new version, no compatibility window, callers not updated) as a finding.

Return the route list in the finding `problem` text of one `question`-severity finding titled `API routes`, so the
orchestrator can fill the PR's API impact section, even when no route has a problem.

## standards — conventions, principles and spec

Read **Step 5 — Standards and spec** in `ado-pr-code-review/SKILL.md` for the two axes and their severities, and
review this diff on both axes yourself (do not invoke another skill):

- **Conventions:** the repo's documented coding standards: `AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md`,
  `docs/agents/`, `.agent-settings/project-config.md`, and the naming, import and layering rules in its lint
  configs. Check what a linter cannot: naming, where code lives, error-handling and logging conventions.
  The orchestrator runs the linter itself; do not repeat lint output.
- **Principles:** if the repo has a constitution (`.specify/memory/constitution.md`, or `openspec/project.md`), read
  all of it and check the diff against each principle it touches. Report as `critical` a change that violates a
  principle (name it, for example `Principle III`), including a potentially breaking or breaking API change without
  the evidence its principle requires (affected consumers, deploy order, rollback, compatibility window or new
  version, old-and-new client tests).
- **Spec:** compare the diff with what was asked: the Jira ticket and the spec for this change **as it was before
  Step 1.5** (Step 1.5 makes the docs match the code, so the synced version would always agree). Report requirements
  or acceptance criteria that are missing or implemented differently, and tasks marked done that the diff does not
  implement.

Severity: a breach of a documented standard is `medium` (`critical` if it breaks behavior); a judgment call is
`minor`; a spec requirement missing or implemented wrongly is `medium` or `critical` by impact. Set `reviewer` to
`standards` or `spec`.

## security — vulnerabilities and data exposure

Read **Step 3 — Security lenses** and **Lens A** to **Lens H** in `ado-pr-code-review/SKILL.md`, and apply the lenses
that fit each changed file. Use their severity guidance, mapped to the severities above. Also report secrets,
tokens or credentials added to code, config or docs in this diff.

## tests — coverage gaps

For each behavior the diff adds or changes, find the test that covers it. Report:

- new or changed behavior with no test;
- error paths, edge cases and boundary values (empty, null, zero, maximum, duplicates, concurrency, timeouts)
  that the existing tests do not reach;
- tests that pass without checking the behavior (no assertion, assert on a mock only, snapshot of the wrong thing);
- tests changed so that they no longer check what they checked before.

For each gap, `fix` names the test file and describes the test case to add (inputs and expected result).
Do not write the test code. Use `minor` for gaps on low-risk code.

## minimal — scope, over-engineering and duplication

If the `ponytail-review` skill is available, read it and apply it to this diff as well. Only inside the scope of
this diff, report:

- changes that the PR's purpose does not need (unrelated renames, formatting, drive-by refactors);
- abstractions with one user: an interface with one implementation, a factory for one product, config for a
  value that never changes;
- new code that the standard library, the platform or an installed dependency already provides, or a new
  dependency for something a few lines can do;
- dead code, unused parameters, scaffolding "for later";
- code the diff adds that duplicates existing code or repeats itself in the diff, and helpers, constants or types
  the diff re-implements: name the existing one, or one shared function and where it lives;
- magic numbers and strings (timeouts, limits, sizes, status codes, keys) without a name. A literal is fine when
  its meaning is obvious in place (`0`, `1`, `-1`, an index) or it is used once next to a comment that explains it;
- each changed function in the complexity measurements: whether it should be split and how — or whether a smaller
  change brings it back under the threshold.

`fix` says what to delete, inline or share. Prefer deleting over extracting; suggest an extraction only when the
diff itself adds the same code 3 or more times. No repository-wide refactors, new layers or patterns the diff does
not need: a suggestion must make the diff smaller or simpler.

## Orchestrator: measurements (before the reviewers)

You run these yourself; the reviewers stay read-only. Each is best-effort: if the tool or the repo's dependencies are
missing, skip it and say so in the report. Report only problems on lines or functions this diff adds or changes.
Let `BASE` be `git merge-base origin/<target-branch> HEAD`.

**Lint** — the lint command from this repo's row in `review-profile.md`, or by language:

| Language | Command | New problems only |
|---|---|---|
| Go | `golangci-lint run --new-from-rev=$BASE ./...` | built in |
| TypeScript / JavaScript | `pnpm exec eslint <changed .ts .tsx .js .jsx files>` (or `npx eslint`) | keep problems on lines in `git diff -U0 $BASE` |
| Elixir | `mix format --check-formatted <changed .ex .exs files>` | the changed files only |

Each problem becomes a finding with `reviewer: "lint"`: an error is `medium`, a warning is `minor`, `effort: trivial`,
`confidence: high`. Never run a fix mode (`--fix`, `mix format` without `--check-formatted`) here.

**Function complexity** — run `python3 -I scripts/complexity.py --base $BASE --repo <repo root>` from this skill's
folder. It measures the changed Go, TypeScript and JavaScript files at HEAD and at `BASE` (in a temp folder; it
changes no file), leaves out tests, docs and generated code, and prints the functions that are **new or grew** and
are over the threshold: **CCN above 15, or more than 80 lines**. Pass the list to the `minimal` reviewer and count
it in the complexity score. It does not read Elixir.

**lizard not available** (the script exits `3`): ask the user to approve installing it, with the first that applies:
`brew install uv` (the script then uses `uvx lizard`), else `pipx install lizard`. On approval, install, run the script
again and go on. When the user declines, neither installer exists, or the run is non-interactive, go on without it
and write `function complexity not measured (lizard not installed)` in the complexity line of the report and of the
PR's Pre-PR Review section. Never install without approval.

## Orchestrator: merge the results

1. Add the `lint` findings from the measurements. Parse each reviewer's JSON. A reviewer that fails or returns invalid JSON is reported as *"<reviewer> did not
   finish"*. The others still count.
2. **Verify, merge and sort** with the shared rules in `ado-pr-code-review/references/review-findings.md`
   (parts 4 and 5): a verifier that did not find the issue, the keep / downgrade /
   drop / pre-existing outcomes, linter-catchable findings dropped, duplicates merged, delete-vs-extract
   conflicts settled. Here "posted" means "shown to the user as a finding to fix"; pre-existing ones are listed
   separately and are not fixed in this PR unless the user asks.

## Orchestrator: review confidence (after fixes)

Rate it with "Review confidence" in part 5 of `ado-pr-code-review/references/review-findings.md`, after the user has
accepted or declined each fix. Open findings are the ones not fixed; the function-complexity signal uses the lizard
measurements above.
