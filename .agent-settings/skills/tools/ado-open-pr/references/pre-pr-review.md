# Pre-PR review — reviewer briefs

Used by `ado-open-pr` Step 1.7. Each reviewer runs as its own sub-agent with a clean context. The orchestrator
builds each prompt from **Common rules** + the reviewer's brief + the run inputs.

## Run inputs (filled in by the orchestrator)

- repository root and repository name
- diff range: `origin/<target-branch>...HEAD` (three-dot; committed work only)
- changed files: `git diff --name-only origin/<target-branch>...HEAD`
- focus notes for this repository from `review-profile.md`, if any
- the path of the sibling skill `ado-pr-code-review/SKILL.md` (same parent folder as `ado-open-pr`)
- for `standards`: the Jira ticket key (and its description / acceptance criteria if the Jira MCP can read it), the
  spec folder that Step 1.5 resolved, and the **pre-sync commit** captured in Step 1 (read the spec as it was before
  Step 1.5 synced it, with `git show <pre-sync commit>:<spec path>`)
- for `refactor`: the complexity measurements (see **Orchestrator: measurements**)

## Common rules (every reviewer)

- **Read only.** Do not edit, create or delete files. Do not commit, push, or run builds, tests or package
  managers. You may run `git diff`, `git log`, `git show` and read any file in the repository.
- **Review this change only.** Report problems that the diff introduces or touches. Read surrounding code to
  understand it, but do not report problems in code the diff does not touch unless the diff makes them worse.
- **Evidence.** Each finding names a file and a line in the PR head, and quotes or describes the code it is about.
  If you are not sure, report it as a `question` instead of a finding.
- **Do not repeat other reviewers.** Stay in your own area. Another reviewer covers the rest.
- **Return only this JSON array** (empty array if you found nothing), no other text:

```json
[
  {
    "reviewer": "code | security | standards | tests | minimal | refactor",
    "severity": "critical | medium | minor | question",
    "file": "path/from/repo/root",
    "line": 42,
    "title": "short claim",
    "problem": "what is wrong and why it matters",
    "fix": "the concrete change you suggest",
    "effort": "trivial | larger",
    "confidence": "high | medium | low"
  }
]
```

Severity: `critical` = security hole, lost or wrong data, crash on a reachable path, or a leak that grows with
traffic. `medium` = a real defect with bounded impact. `minor` = clarity or maintainability. `question` = needs
the author's answer before anyone can judge it.

Confidence (how sure you are that the finding is real): `high` = you traced the code path and it fails as
described; `medium` = likely, but it depends on code or data you could not see; `low` = a suspicion worth a look.

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
`minor`; a spec requirement missing or implemented wrongly is `medium` or `critical` by impact. Start each title with
`[standards]` or `[spec]`.

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

## minimal — scope and over-engineering

If the `ponytail-review` skill is available, read it and apply it to this diff. Otherwise use these rules:

- changes that the PR's purpose does not need (unrelated renames, formatting, drive-by refactors);
- abstractions with one user: an interface with one implementation, a factory for one product, config for a
  value that never changes;
- new code that the standard library, the platform or an installed dependency already provides;
- a new dependency for something a few lines can do;
- dead code, unused parameters, scaffolding "for later".

`fix` says what to delete or inline. Do not suggest new abstractions; that is the `refactor` reviewer's job.

## refactor — duplication and magic values

Only inside the scope of this diff. Start from the complexity measurements in the run inputs: for each changed
function over the threshold, say whether it should be split and how.

- code the diff adds that duplicates existing code, or that copies the same logic in several places in the diff:
  suggest one shared function and where it should live;
- the diff re-implements a helper, constant or type that already exists in the repository: name the existing one;
- magic numbers and strings (timeouts, limits, sizes, status codes, keys) used without a name: suggest a named
  constant, or a config value if it differs per environment. A literal is fine when its meaning is obvious in place,
  such as `0`, `1`, `-1`, an index, or a value used once next to a comment that explains it.

Do not suggest repository-wide refactors, new layers or patterns the diff does not need. A suggestion must make
the diff smaller or simpler, or remove a real duplicate.

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

**Function complexity** — `uvx lizard --csv <changed source files>` at HEAD, and the same on the `BASE` version of
those files (write them to a scratch folder with `git show $BASE:<path>`). lizard reads Go, TypeScript and JavaScript;
it does not read Elixir, so skip `.ex` / `.exs`. CSV columns: NLOC, CCN, tokens, params, length, location, file,
function, signature, start line, end line. Leave out docs, generated files and test fixtures. Match functions
by file and name, and keep those that are **new or grew** (higher CCN or more lines) and are over the threshold:
**CCN above 15, or more than 80 lines**. Pass this list to the `refactor` reviewer, and count it in the complexity
score below. A `lizard` already on `PATH` works the same as `uvx lizard`.

**lizard not available** (no `uvx` and no `lizard`, or the first download fails): skip only this measurement and go
on with everything else. Then:
- tell the user how to install it: `brew install uv` (then `uvx lizard` works), or `pipx install lizard`;
- ask whether to install it now and measure before the reviewers start, or to continue without it;
- when continuing without it, write `function complexity not measured (lizard not installed)` in the complexity line
  of the report and of the PR's Pre-PR Review section, so a reader knows the score is missing a signal;
- after the PR exists, if the user installs lizard later in this run, offer to measure then and update the PR
  description's Pre-PR Review section (`repo_pull_request_write` with `action: "update"` and the new `description`).

## Orchestrator: merge the results

1. Add the `lint` findings from the measurements. Parse each reviewer's JSON. A reviewer that fails or returns invalid JSON is reported as *"<reviewer> did not
   finish"*. The others still count.
2. **Verify each finding** against the code at the stated file and line. Drop findings that are wrong or that point
   at code the diff does not touch.
3. **Merge duplicates** (same file, same line range, same problem) and keep the highest severity.
4. **Conflicts between `minimal` and `refactor`:** when one says "inline / delete" and the other says "extract",
   prefer `minimal`, unless the duplicate is introduced by this diff and occurs 3 or more times. Show both views to
   the user when it is unclear.
5. Sort by severity: critical, medium, minor, question. Inside one severity, put `high` confidence first.
   Your own check in step 2 can raise or lower a finding's confidence.

## Orchestrator: review confidence (after fixes)

Rate how much a human reviewer must check, after the user has accepted or declined each fix.

**Complexity score.** Add 1 point for each signal the diff shows:

| Signal | Examples |
|---|---|
| API contract added or changed | new route; request or response field, status code or validation changed |
| Data shape changed | new table or column, DB migration, CMS or schema-registry change |
| Async or concurrent work | new background job, worker, goroutine, scheduler, queue consumer |
| New external dependency | third-party service, AWS resource, new Redis key space, new package |
| New config | env var, feature flag |
| Wide change | 3 or more top-level modules or packages touched |
| Complex function | a new or grown function over the lizard threshold (CCN above 15, or more than 80 lines) |
| Large change | more than 400 changed lines or 20 files, **not counting** docs (`*.md`, `docs/`, `specs/`), generated files (swagger, mocks, lockfiles) and test fixtures |

Complexity: 0–1 = low, 2–3 = medium, 4 or more = high.

**Level.** Use the first level whose condition is true:

| Level | Condition | Human review |
|---|---|---|
| **Low** | an unresolved `critical`; an unresolved `medium` with `high` confidence; a reviewer did not finish; a **potentially breaking or breaking** API change; the diff changes auth, permissions, payments, PII handling, DB migrations or infra/deploy config; or **high** complexity | **Required.** Ask a reviewer to read the whole diff, and point them at the unresolved findings. |
| **Medium** | other unresolved `medium` findings or `question`s; new or changed behavior with an unresolved `tests` gap; or **medium** complexity | **Recommended.** A reviewer should check the listed areas. |
| **High** | none of the above: all reviewers finished, only `minor` findings remain, and complexity is low | **Light review is enough.** Branch policies and required reviewers still apply. |

State the level, the one or two reasons that decided it, the complexity score with its signals, and the counts of
resolved and unresolved findings.
The level is advice for the humans. It never removes required reviewers or bypasses a branch policy.
