---
name: ado-pr-code-review
description: Review an Azure DevOps PR by URL and post inline LOC-level comments. Covers commit provenance (merge direction / target-branch warnings, merge commits smuggling other work in, lost work from force-pushes, rebases, dropped child PRs or overwritten conflict resolutions), security (PII exposure, input validation, error `code` field, OWASP Top 10, CWE Top 25, OWASP API/Mobile/IoT Top 10), runtime correctness and resource leaks (crashes, races, lost work, memory/connection/listener leaks, unbounded growth, in backend and frontend code), and repo standards and spec conformance; every finding is verified before it is posted. Use when asked to review a PR, code review an ado PR, security review a pull request, find bugs or memory leaks in a PR, do a final/last review, or given an Azure DevOps PR URL.
argument-hint: "<azure-devops-pr-url> [--deep] [--preview] [--fast]"
allowed-tools: Skill, Agent, Bash, Read, mcp__azure-devops-mcp__repo_repository, mcp__azure-devops-mcp__repo_pull_request, mcp__azure-devops-mcp__repo_file, mcp__azure-devops-mcp__repo_pull_request_thread, mcp__azure-devops-mcp__repo_pull_request_thread_write, mcp__azure-devops-mcp__pipelines_build, mcp__azure-devops-mcp__pipelines_definition
---

# Azure DevOps PR Code Review

## Companion skills (optional)

Both come from `mattpocock/skills` (`skills/engineering/<name>/`). If one is not installed, the review
still runs: skip that part and say so in the summary.

- **`code-review`** — optional help for the standards and spec pass (Step 5); the pass runs without it.
- **`diagnosing-bugs`** — the repro loop for findings whose cause is unclear (see the last section).
  It replaces the older `diagnose` skill; do not reference `diagnose`.

---

PR review that posts inline LOC-level comments on the diff. It finds, verifies, then posts:

1. Commit provenance (Step 2.5)
2. Security lenses A–H (Step 3)
3. Runtime correctness and resource leaks (Step 4)
4. Standards and spec (Step 5)
5. Test coverage (Step 5.1) and impact outside the diff (Step 5.2)
6. Verify every candidate finding (Step 5.5)
7. Post the verified findings inline (Step 6), then one summary thread (Step 7)

Findings use the format and rules in `references/review-findings.md`. Read it before Step 3. Run Steps 3, 4, 5, 5.1 and 5.2
as separate fresh sub-agents in parallel when the agent supports them (one per pass, not forked from this context),
each returning the JSON findings of that file. That file's part 1 says what to read and from where, part 2 how the
passes run (at most 6 sub-agents at once, the second look for large or high-risk PRs, read-only, model, rule-file edits), part 4 how findings are
verified, and part 5 what is posted. Without sub-agents, run the passes one after another and say so in the
summary. The review never approves, votes, or completes the PR (see Notes).

## Arguments

| Token | Meaning |
|---|---|
| an Azure DevOps PR URL | **required** — the PR to review; parsed in Step 1 |
| `--preview` | run every step up to Step 5.5, then show the inline comments and the summary exactly as they would be posted, and call no write tool. Post them only if the user then says so |
| `--fast` | ask nothing during the run: the PR-description update becomes a summary item, not an offer. Posting still follows `--preview` |
| `--deep` | deep review: always run the second look and the tie-break layer for criticals left at `medium` confidence (`references/review-findings.md` parts 2 and 4) |

No URL → ask for one before doing anything else.

---

## Step 1 — Parse the PR URL

Extract from the URL:
- `org` — the Azure DevOps organization
- `project` — the team project
- `repo` — the repository name
- `prId` — the pull request ID (integer)

URL patterns:
```
https://dev.azure.com/{org}/{project}/_git/{repo}/pullrequest/{prId}
https://{org}.visualstudio.com/{project}/_git/{repo}/pullrequest/{prId}
```

## Step 2 — Fetch PR metadata and changed files

1. Call `repo_pull_request` with `{ action: "get", project: {project}, repositoryId: {repo}, pullRequestId: {prId}, includeChangedFiles: true }`
2. Take the list of changed files from that response. For each file's diff, read both sides with `repo_file`
   (`action: "get_content"`, `versionType: "Commit"`): the target side at `lastMergeTargetCommit` and the source
   side at `lastMergeSourceCommit`. With a local clone, `git diff <target>...<source>` gives the same diff
3. For each changed file, use the source-side `repo_file` content from step 2 as the full file at the PR's source branch
4. If a local clone exists, `git fetch` the source and target branches and work from
   `git diff {target}...{source}` instead: the runtime pass needs to read callers and run tests.
5. Call `repo_pull_request_thread` with `{ action: "list", repositoryId, project, pullRequestId }` and note every earlier finding and its status.
   On a re-review, do not raise a finding again if its thread is fixed, won't-fix or by-design, unless the
   fix is wrong or incomplete. Then say so in a new thread that names the old one.
6. Read the repo's rule files (`CLAUDE.md`, `AGENTS.md`, constitution, `docs/agents/`) and the reference data
   findings rely on (schemas, contracts, API reference) from the **target branch**, and this repo's central review
   rules (`references/review-rules/_default.md` + `references/review-rules/<repo>.md`), as part 1 of
   `references/review-findings.md` describes. Pass them to every pass and to the verifier.

## Comment Format

Short enough to read in the PR page. The title, the reviewers line, the impact and the Fix must stand on
their own; keep a blank line between them, or the PR page joins them into one line:

```
{severity_emoji} **{Severity} — {short title}**

Reviewers: {reviewer} · {reviewer}

{One sentence: the case that triggers it and its concrete impact.}

**Fix:** {one line: the change to make — or, for a 🔍 Question, `**Q:**` and the question to answer}

{Optional: a code block of at most 10 lines with the fix, only when the one-line Fix is not enough.}

How verified: {how Step 5.5 confirmed it — traced path / compared base and head / ran a command / inference}
```

> **Rule**: Every comment **must** have a `**Fix:**` (or `**Q:**`) line that names a concrete change or question —
> "consider fixing this" is not one. A finding without it is incomplete; do not post it.

- Title at most 80 characters. Use backticks for symbols, paths and code.
- Do not open with filler ("Note:", "Please", "Additionally", "However") and do not restate the code.
- The whole comment stays under 15 lines. More context belongs in the code block or not at all.
- The lens templates below give the wording for their findings; fit them to this shape.

**Severity levels:**

| Emoji | Level | When to use |
|---|---|---|
| 🔴 | Critical | Security breach, data leak, broken contract, crash path |
| 🟡 | Medium | Logic flaw, misleading behaviour, missing safeguard |
| 🔵 | Minor | Code quality, unnecessary exposure, inconsistency |
| 🔍 | Question | Clarification needed — not necessarily a bug |
| 🟣 | Pre-existing | Real, but the same code is already on the target branch. **Summary only, never inline**, and never counted against this PR |

**Reviewers line** (its own line under the title, so the title stays short): every pass that raised the finding,
by name, joined with ` · `. Every comment has one, security findings included.

| Name | Pass |
|---|---|
| `provenance` | Commit provenance (Step 2.5) — summary only |
| `security` | Security lenses A–H (these also end with a `CWE Mapping:` line) |
| `runtime` | Runtime correctness and resource leaks (Step 4) |
| `standards` | Repo standards (Step 5) |
| `spec` | Spec / ticket conformance (Step 5) |
| `tests` | Test coverage (Step 5.1) |
| `impact` | Impact outside the diff (Step 5.2) |

When several passes hit the same line, post one comment and name them all. In the summary and in `ado-open-pr`'s
list, a finding ends with its reviewers in brackets instead: `— {short title} (runtime, standards)`.

**Examples:**

```
🔴 **Critical — `accountId` returned by a public endpoint**

Reviewers: security

Any caller can read the account id of every user in the list, which identifies them.

**Fix:** Drop `accountId` from the response DTO, or move the endpoint behind authentication.

How verified: traced the route → handler → DTO; no auth middleware on the route (static).
```

```
🟡 **Medium — Empty `sceneSID` passes binding**

Reviewers: security

`{ "sceneSID": "" }` passes `required` and builds an empty FQDN, so Route53 returns an error.

**Fix:** Add `min=1` to the binding tag.

```go
SceneSID string `json:"sceneSID" binding:"required,min=1"`
```

How verified: ran the handler test with an empty value on head (fails as described).
```

```
🔍 **Question — Is an empty `values` array valid?**

Reviewers: security

`{ "values": [] }` passes binding and reaches the update with nothing to write.

**Q:** Is this a valid caller intent? If not, add `min=1`; if so, say why in a code comment.

How verified: inference — not traced.
```

---

## Step 2.5 — Commit provenance audit (blocking, run before any lens)

A PR can silently carry the wrong commits, or silently drop the right ones. Both have shipped
before (a `Merge branch 'X' into Y` brought a stale branch in, and PRs already merged into the
feature branch were no longer reachable from its tip, so they never reached master).
Do this **before** reading any diff, and report the result even when it is clean.

Get the PR's commit list (PR commits API, or `git fetch` then
`git log --format='%h %p | %an | %s' {targetCommit}..{lastMergeSourceCommit}`) and `lastMergeSourceCommit`.

### Check 0 — Merge direction (is this PR going where it should?)

Merging into the wrong branch is easy to miss because the diff still looks right. First work out the
repo's **PR target** (`{target}` below):

1. **`references/branch-map.md`** in this skill: the team's agreed PR target per repository, plus other
   branches PRs may legitimately target (for example `release/*` with a required backport).
2. **Not listed:** the repo's ADO default branch (`defaultBranch` from the repository API). If that branch's
   last commit is more than 90 days old, say it may not be the real PR target and ask which branch is.

Then compare it with the PR's `targetRefName` and `sourceRefName`:

- **Target is `{target}`:** normal. Note `→ {target}` in the summary and continue.
- **Target is an allowed other branch in the map:** fine. Put that row's note in the summary (for example
  "`release/*`: the CI/CD pipeline opens the `[Backport] … → main` PR after this one merges").
- **Target is anything else** (a feature, a stale `develop`, another person's branch): put a ⚠️ **Merge
  target warning** at the very top of the summary, above the recommendation, stating:
  - the target branch, and that this work will **not** reach `{target}` when this PR completes;
  - whether the target branch itself has an open PR to `{target}` (link it), or none, in which case this
    work has no path to `{target}` yet;
  - how far the target branch is behind `{target}` (`git rev-list --count {branch}..{target}`): a stale
    branch means the follow-up PR will need a sync merge, which is where conflict resolutions drop work
    (see Check 2);
  - that **squash on completion** will rewrite these commits, so the follow-up PR to `{target}` must be
    checked with Check 2b against this PR's merge commit.
  Ask the author to confirm the target is intended. When the repo is in the branch map, raise it as
  🟡 Medium.
- **Source is `{target}` or a `release/*` branch, merging into a feature branch:** a sync in the reverse
  direction. Say so in the warning; it is fine only if that is the intent, and its conflict resolution must
  be reviewed like normal code (see Check 1.3).

### Check 1 — Merge commits inside the PR (smuggled commits)

1. Flag **every commit with more than one parent**, and every subject starting with
   `Merge branch`, `Merge remote-tracking branch`, or `Merge pull request`.
2. For each one, enumerate what the second parent brought in:
   `git log --no-merges --format='%h %an %ad | %s' {first-parent}..{second-parent}`
3. For every brought-in commit, check it against the PR title, description and ticket:
   - Another ticket key, another author, or a `Merged PR {n}` subject that does not belong to this
     PR's scope: 🔴 **Critical**. List each commit.
   - A merge **from the target branch** (syncing master/develop into the branch) is acceptable, but
     review its conflict resolution: `git show --diff-merges=cc {merge}`. Hand-edited content inside a
     merge ("evil merge") is reviewed like normal code.
   - A merge from any other branch is **never** acceptable without an explicit reason in the PR
     description. Ask the author to rebase or cherry-pick instead.
4. Never treat "the diff looks fine" as clearing a merge commit. The diff only shows the end state,
   not what history was dragged in or overwritten.

### Check 2 — Lost work (rewritten pushes, child PRs, overwritten content)

Commits get lost in three ways, and a reachability check alone only catches the first:
a child PR merged into the branch and later dropped, a commit pushed straight to the branch and later
rewritten away, and a commit that is still there but whose changes were undone by a bad rebase or
conflict resolution. Check all three, **by content**, not just by commit hash.

**2a — Every head the branch ever had (catches force-push / rebase, with or without a PR).**
1. List the PR threads with the full response (`repo_pull_request_thread`, `action: "list"`, `fullResponse: true`).
   Each push to the source branch is a system thread whose `properties.CodeReviewThreadType` is
   `RefUpdate`; read `CodeReviewRefNewHeadCommit` (the head after that push) and `CodeReviewRefNewCommits`
   (`;`-separated new commits) from it. In order, these give every head the branch had since the PR opened.
   (The REST endpoint `pullRequests/{id}/iterations` gives the same heads if you have a PAT.)
2. Walk the heads **push by push**, as consecutive pairs `(old, new)`, ending with the tip `T`
   (`lastMergeSourceCommit`). If a head is not local, fetch it by SHA: `git fetch origin {sha}`
   (ADO still serves rewritten commits).
   - `git merge-base --is-ancestor old new` succeeds: a normal push that only added commits. Nothing to check,
     even if later pushes edit that code on purpose.
   - It fails: that push rewrote history (force-push, rebase or squash). Only these pushes are checked.
   Compare only consecutive heads, never an old head against the final tip: work that evolved over
   normal pushes would otherwise look lost.
3. For each rewriting push, check that every change in `old` is still in `new`:
   `M = git merge-base {target} old`, then for each file in `git diff --name-only M old`,
   `git diff M old -- {file}` must reverse-apply on `new`'s tree
   (`GIT_INDEX_FILE=tmp git read-tree new && git apply --cached --check -R`).
4. If every file reverse-applies, the rewrite was a squash, reword or clean rebase: note it in the summary
   (`✅ {k} force-push/rebase pushes, all changes preserved`). If a file is missing, check whether that same
   push changed it on purpose (amended commit message, PR discussion). If nothing explains it:
   🔴 **Critical, blocking**. Name the push, the two heads and the missing files.

If the repo runs a provenance build validation on PRs (for example a `scripts/ci/pr_provenance.py` that
implements Checks 0, 1, 2a and 2b), read its result instead of redoing those checks by hand.

**2b — Child / stacked PRs (work merged into this branch through its own PR).**
1. List completed PRs whose **target branch is this PR's source branch**.
2. For each, take its `lastMergeCommit` and check it is reachable from `T`:
   `git merge-base --is-ancestor {childMergeCommit} {T}`. If the hash changed through a rebase, match by
   patch-id (`git cherry`).
3. Reachable or not, check the content is still there: in a worktree at `T`,
   `git diff {childMergeCommit}^1 {childMergeCommit} | git apply --check -R`. A hunk that no longer
   reverse-applies was overwritten later, typically by a conflict resolution. Apply the same rule as 2a.4.
4. Unreachable and not matched by patch-id: 🔴 **Critical, blocking**. Name each missing PR and commit,
   and ask the author to restore the branch before merging.

**2c — Scope.** Compare the PR's declared scope (title / description / linked work items) with the files
actually changed. Scope listed but not changed, or a child PR's changed files absent from the diff, is a miss.

A squash merge on completion hides all of this afterwards, so run Check 2 **before** completion, and again
on a re-review if new pushes arrived since the last one.

### Check 3 — Has the target moved since the merge was computed?

Azure DevOps computes `mergeStatus` against `lastMergeTargetCommit`, which can be weeks old. Compare it with the
current target head (`git fetch` then `git rev-parse origin/{target}`). If the target has moved:

1. Count how far: `git rev-list --count {lastMergeTargetCommit}..origin/{target}`.
2. Test the merge against today's target: `git merge-tree --write-tree --name-only origin/{target} {lastMergeSourceCommit}`.
   A non-zero exit lists the conflicting files.
3. For each conflicting file, say what the target changed there since the merge-base (`git log
   {merge-base}..origin/{target} -- <file>`), for example "master already added this file in PR N" or "the
   constitution moved from 1.16 to 1.19". Keep `git diff {merge-base} origin/{target} -- <conflicting files>` and pass it
   to Steps 4 and 5 and to Step 5.5 ("Target moved" in part 1 of `references/review-findings.md`).
4. Conflicts make the PR **stale**: report them under Commit provenance as 🟡 Medium (🔴 Critical when the target
   already contains a different implementation of the same change), and apply the stale-PR gating in
   `references/review-findings.md`. A target that moved without conflicts is a one-line note.

### Output

- Do **not** post a separate thread for this step. Its result goes in the `🚫 Commit provenance` section
  of the Step 7 summary: merge commits found, commits brought in by each, rewritten heads and whether
  their content survived, child PRs checked, and any unreachable PR. When clean, one line such as
  `✅ {n} linear commits, no merge commits, {k} rewritten heads (content preserved), no child PRs`.
- Findings from Checks 1 and 2 are **Critical**: list them first in that section and count them under
  🔴 Critical. While any remain, the Recommendation is never "ready for human review". Check 3 uses the
  severities it states.

---

## Step 3 — Security lenses: analyze each file

For every changed file apply all required review lenses below (A-H), based on file surface and runtime context. Collect findings as a list of `{filePath, line, severity, title, body}` tuples — **one finding per line**.

Every finding is posted inline on a specific line. The only top-level thread is the Step 7 summary;
a finding that has no line (for example a missing doc or a missing requirement) goes in that summary.

## Baseline Standards (Must Use Latest Version)

Before evaluating findings, use the latest available release of each standard below (do not rely on outdated versions if a newer release exists):

- OWASP Code Review Guide: https://owasp.org/www-project-code-review-guide/assets/OWASP_Code_Review_Guide_v2.pdf
- OWASP Top 10 Web: https://owasp.org/www-project-top-ten/
- CWE Top 25: https://cwe.mitre.org/top25/
- OWASP API Security Top 10: https://owasp.org/API-Security/
- OWASP Mobile Top 10: https://owasp.org/www-project-mobile-top-10/
- OWASP IoT Top 10 / IoT project: https://owasp.org/www-project-internet-of-things/

As of 2026-06 reference points are:

- OWASP Top 10 Web: 2025
- CWE Top 25: 2025 list
- OWASP API Security Top 10: 2023
- OWASP Mobile Top 10: 2024 final release
- OWASP IoT Top 10: latest archived OWASP IoT Top 10 guidance (no newer replacement shown on project page)

If a newer edition is published, use the newer edition immediately.

---

### Lens A — PII Exposure & Regulatory Compliance

**Scope**: Any file that is part of a public-facing API (request/response DTOs, controllers, serializers, GraphQL types, URL route definitions, UI components that render data to end-users).

**Regulatory baseline**: flag any exposure that would violate:
- **GDPR** — personal data of EU residents must not be exposed without lawful basis; data minimisation principle applies
- **CCPA** — personal information of California residents must not be sold or disclosed without disclosure + opt-out mechanism
- **ISO 27001** — access to personal/sensitive information must be controlled, logged, and limited to authorised parties

The table below lists **minimum required fields to check**. It is **not exhaustive** — you must also flag any other field whose name or context suggests it could identify a person or reveal sensitive personal information, even if it is not listed here.

| PII Type | Example field names (non-exhaustive) | Regulation |
|---|---|---|
| Account ID | `accountId`, `account_id`, `userAccountId`, `user_account_id` | GDPR, CCPA |
| Email | `email`, `emailAddress`, `email_address` | GDPR, CCPA |
| Phone number | `phone`, `phoneNumber`, `phone_number`, `mobile` | GDPR, CCPA |
| Wallet / crypto address | `walletAddress`, `wallet_address`, `cryptoAddress` | CCPA |
| Date of birth | `dateOfBirth`, `dob`, `date_of_birth`, `birthDate` | GDPR, CCPA |
| Credit card / payment | `cardNumber`, `cvv`, `cvc`, `creditCard`, `pan` | GDPR, CCPA, ISO 27001 |
| Full name (combination risk) | `fullName` combined with other PII fields | GDPR, CCPA |
| National / government ID | `nationalId`, `ssn`, `taxId`, `passportNumber` | GDPR, CCPA |
| Location / biometric data | `ipAddress`, `gpsCoord`, `biometric`, `faceId` | GDPR |
| Device / behavioural identifiers | `deviceId`, `advertisingId`, `userAgent`, `sessionId` | GDPR, CCPA |
| Health / sensitive category data | `healthData`, `diagnosis`, `gender`, `religion`, `ethnicity` | GDPR (special category) |
| Any other identifiable field | `homeAddress`, `mailingAddress`, `employeeId`, etc. | GDPR, CCPA |

**Additionally flag**:
- Bulk export endpoints (no pagination / rate limit) that could enable mass harvesting of personal data — ISO 27001 data leakage risk
- Logs or error responses that include personal data fields — GDPR data minimisation violation
- Unauthenticated endpoints returning any field from the table above — 🔴 Critical under all three regulations
- Missing or insufficient access control on endpoints returning personal data — ISO 27001 A.9 (Access Control)

**Comment template** (use the format defined in "Comment Format" above):
```
🟡 **Medium — PII / Regulatory Risk: `{fieldName}` in public-facing {API / URL / UI}**

`{fieldName}` may expose {pii type}, which is regulated under {GDPR / CCPA / ISO 27001}.
Exposing this without lawful basis, access control, or explicit disclosure may constitute a compliance violation.

**Fix:** {Choose one based on context:}
- Remove the field from the response DTO if it is not needed by callers.
- Replace with a masked/truncated value (e.g. last 4 digits, first letter of email domain).
- Move the field to an authenticated-only endpoint and document the lawful basis / access requirement.
- If intentional, add a code comment stating the business reason, lawful basis (GDPR Art. 6), and whether a DPIA is required.
```

Use 🔴 Critical if the field is in an unauthenticated public endpoint. Use 🟡 Medium if behind auth but still potentially over-sharing.

Post the comment on the **line where the field is declared or serialized**.

---

### Lens B — Input Validation & Security

**Scope**: API endpoint handlers, request DTOs, form inputs, URL parameter bindings, query parameters.

Flag when:
- A request body DTO has no validation annotations (e.g. `@NotNull`, `@Size`, `@Pattern`, `Required`, `z.string()`, etc.)
- User-supplied input is passed directly to a database query, HTML renderer, shell command, or template engine without sanitization
- URL or query parameters are reflected back into responses or HTML without encoding
- File upload endpoints lack MIME type / size validation
- String inputs that will be stored and later rendered in UI have no XSS-safe encoding

**Null / empty / undefined guard checks** — flag when any of the following is missing and the absence appears unintentional:
- A string field has no empty-string (`""`) guard — comment if empty string is not a valid design state
- An array/slice/list field has no empty-array (`[]`) guard — comment if an empty collection is not a valid design state
- A value can be `null`, `nil`, `undefined`, or `None` but is used without a nil/null check before access
- A required field has no presence check before it is read or forwarded

For each null/empty finding, **ask the author** whether the empty/nil state is intentional by design. Do not assume it is a bug — treat it as a clarification request.

**Comment template — missing type/length/format validation**:
```
🟡 **Medium — No input validation on `{parameter/field}`**

`{parameter/field}` is user-supplied with no visible type/length/format constraint.
This may allow unexpected values that could lead to XSS or injection.

**Fix:** Add validation appropriate to the framework, e.g.:
```{language}
{concrete corrected declaration with validation annotation or binding tag}
```
If validation exists elsewhere in the call chain, add a comment pointing to it.
```

**Comment template — missing null/empty guard**:
```
🔍 **Question — Is {null / empty string / empty array} valid for `{field}`?**

`{field}` can be {nil/null/empty} here with no guard before use.

**Fix:** If this state is invalid, add an explicit guard:
```{language}
{concrete nil/empty check with early return or error}
```
If it is intentional by design, add a short comment in the code explaining why
so future reviewers don't flag it again.
```

Post on the **line of the parameter declaration or the first use of the unvalidated / unguarded value**.

---

### Lens C — Error Response `code` Field

**Scope**: Error/exception handlers, error response structs/classes/types, API middleware, HTTP error factories.

Flag when:
- An error response object is defined without a `code` field (at root or nested level)
- An error is returned/thrown where only `message` is set, with no `code`
- A catch block or error handler returns a response body that contains only `message`, `error`, or `description` but no machine-readable `code`
- A caller is reading `.message` from an error response instead of `.code`

**Expected pattern** (any of these is acceptable):
```json
{ "code": "INVALID_INPUT", "message": "..." }
{ "error": { "code": "NOT_FOUND", "message": "..." } }
{ "status": { "code": 4001, "description": "..." } }
```

**Comment template**:
```
🟡 **Medium — Error response missing `code` field**

This error response does not include a `code` field. Callers must be able to identify
error types via a stable `code` (not `message`, which can change with copy/i18n).

**Fix:** Add a `code` field at the root or a known nested path:
```{language}
{concrete corrected error response construction with code field added}
```
For example:
```json
{ "code": "INVALID_INPUT", "message": "..." }
{ "error": { "code": "NOT_FOUND", "message": "..." } }
```
```

Use 🔴 Critical if this is a contract-breaking change where a downstream caller currently reads `.code`. Use 🟡 Medium for new endpoints.

Post on the **line where the error response object is constructed or returned**.

---

### Lens D — OWASP Top 10 Web (Latest)

Map changed code to OWASP Top 10 categories and flag applicable issues, with emphasis on:

- Broken access control
- Cryptographic failures
- Injection
- Insecure design
- Security misconfiguration
- Vulnerable/outdated components
- Identification/authentication failures
- Software/data integrity failures
- Security logging/monitoring failures
- SSRF

Rules:

- Use current OWASP Top 10 terminology and IDs from the latest edition.
- If the code introduces one of these risks, post a finding with a concrete exploit path.
- If no category applies for a file, do not force a finding.

Post on the most specific risky line (sink, policy bypass, or insecure config declaration).

---

### Lens E — CWE Top 25 (Latest)

Map findings to CWE IDs from the latest CWE Top 25 list.

Rules:

- Every high-confidence weakness should include at least one CWE mapping (for example `CWE-79`, `CWE-89`, `CWE-22`, `CWE-287`, `CWE-502`).
- Prefer the most specific CWE that matches code behavior.
- If uncertainty is high, use a question-severity comment and ask for clarification before asserting a CWE.

Comment addition requirement:

Add a final line to each applicable comment:
`CWE Mapping: CWE-XXX ({short name})`

---

### Lens F — OWASP API Security Top 10 (Latest)

For API code paths, evaluate against current OWASP API Top 10 categories, including at minimum:

- API1 Broken Object Level Authorization (BOLA)
- API2 Broken Authentication
- API3 Broken Object Property Level Authorization (BOPLA)
- API4 Unrestricted Resource Consumption
- API5 Broken Function Level Authorization
- API6 Unrestricted Access to Sensitive Business Flows
- API7 Server Side Request Forgery
- API8 Security Misconfiguration
- API9 Improper Inventory Management
- API10 Unsafe Consumption of APIs

Flag missing object-level authorization checks, tenant scoping flaws, unconstrained pagination, missing rate limiting, privileged function exposure, and untrusted upstream API handling.

Post on the authorization decision point, route handler, or outbound API consumption line.

---

### Lens G — OWASP Mobile Top 10 (Latest)

When changed code affects mobile apps, SDKs, mobile APIs, or app-backend contracts used by mobile clients, evaluate against the latest OWASP Mobile Top 10.

Check for at least:

- Improper credential usage
- Inadequate supply chain security
- Insecure authentication/authorization
- Insufficient input/output validation
- Insecure communication
- Inadequate privacy controls
- Insufficient binary protections
- Security misconfiguration
- Insecure data storage
- Insufficient cryptography

Flag risky local storage, hardcoded secrets, weak transport/crypto defaults, weak token/session handling, and missing anti-tamper assumptions in client-trusting flows.

Post where the insecure mobile-facing contract, storage usage, credential handling, or crypto/transport config is defined.

---

### Lens H — OWASP IoT Top 10 (Latest Available)

When changed code affects device firmware, embedded services, management planes, device onboarding, OTA update flow, or IoT cloud control APIs, evaluate against OWASP IoT Top 10 guidance (latest available from OWASP IoT project/archive).

Check for at least:

- Weak/guessable/default passwords
- Insecure network services
- Insecure ecosystem interfaces (web/cloud/mobile/API)
- Lack of secure update mechanism
- Use of insecure or outdated components
- Insufficient privacy protection
- Insecure data transfer/storage
- Lack of device management and monitoring
- Insecure default settings
- Lack of physical hardening assumptions where relevant

Flag unauthenticated device actions, unsigned update paths, insecure provisioning, exposed debug/admin interfaces, and missing device identity validation.

Post where trust is established or broken (auth boundary, update verifier, provisioning logic, or control-plane endpoint).

---

## Step 4 — Runtime correctness and resource leaks

Goal: find defects that make the change wrong at runtime: crashes, wrong or lost data, lost work, races,
leaks, unbounded growth. The security lenses and the standards/spec pass are not designed to catch these.

Run it as its own sub-agent when the agent supports one, so it does not inherit the other passes'
conclusions. Give it the diff, the PR description and the list of earlier review threads.

**Method — trace, don't tick boxes.** List every new or changed *thing* the PR introduces: goroutines and
async tasks, connections, rows and cursors, timers, listeners, subscriptions, caches, maps and stores,
component state, DB rows it writes, external calls, and any rule that now exists in more than one place.
Trace each one end to end through its callers and answer:

1. Who creates it, and who releases or ends it? What happens if that never happens?
2. What happens on error, timeout, cancellation, shutdown, deploy or unmount?
3. What happens when it runs concurrently, twice, or out of order?
4. Can it grow without bound? Which input or key decides its size?
5. Is it shared? Who changes it after it is handed out?
6. If the same rule exists in more than one place, do all copies agree?
7. What does it assume about the data (NULL, empty, ordering, timing, clock) that nothing checks?

**The examples below are starting points, not a complete list.** Report anything else that looks wrong at
runtime even if it fits none of them.

| Area | Backend (e.g. Go) | Frontend (e.g. TS / React) |
|---|---|---|
| Lifecycle / cleanup | goroutine never stopped; no drain on shutdown; `rows.Close()` / `resp.Body.Close()` not deferred | `useEffect` without cleanup for listeners, `setInterval`, subscriptions, sockets, observers |
| Async races | shared data changed after hand-off; work tied to a request context that gets cancelled | a slow response overwrites newer state (no `AbortController` / ignore flag); setState after unmount |
| Unbounded growth | cache key built from caller input; maps or slices that only grow | module-level `Map` / cache, a store that only appends, memo keys that never repeat |
| Shared mutable state | cache or singleflight result mutated by one caller | props or state mutated in place; stale closures; missing hook dependencies |
| Crash paths | type assertions, `MustGet`, nil dereference, index out of range | `undefined` access, unhandled promise rejection, render errors with no error boundary |
| Drift between copies | the same SQL predicate or rule written in several queries | the same check copied across components or hooks |

**Verify.** Run the project's own checks on the PR head **and** on its merge-base, then report only failures
that are new on the PR. Use what the repo already has, for example `go vet` + `go test -race` for Go, or
`tsc --noEmit`, `eslint` (including `react-hooks/exhaustive-deps`) and the `package.json` test script for
frontend projects. A failure that also happens on the merge-base is pre-existing: mention it in the summary,
not as a finding. Many frontend leaks only show at runtime (heap snapshots, detached DOM); if you suspect
one you cannot confirm statically, raise it as a 🔍 Question and say how to measure it.

A claim that CI, a build or a deploy fails needs the pipeline that actually runs (`pipelines_build` for
`refs/pull/{prId}/merge` or the source branch, pipeline definitions, or the review rules) — `review-findings.md`
part 4, layer 4.

Name these findings `runtime`. Severity: lost data, lost work, a crash on a reachable path or a leak that
grows with traffic is 🔴 Critical; a defect with a bounded or rare impact is 🟡 Medium.

---

## Step 5 — Standards and spec

1. The standards pass reviews the PR range `{target-branch merge-base}..{lastMergeSourceCommit}` on two axes itself:
   - **Standards**: does the change follow this repo's documented coding standards (CLAUDE.md, constitution,
     `.agent-settings`, the central review rules), read from the target branch (Step 2)? When the PR edits a rule
     file, also check that code already on the target branch still complies (`review-findings.md` part 2).
   - **Spec**: does the change match what the Jira ticket / PR description / linked spec asked for? Feed it the
     ticket key and PR description. This also cross-checks the scope check in Step 2.5.
2. The `code-review` skill, when installed, may be used for either axis; it is optional and never a reason to skip
   the pass.
3. Map the results onto the same comment format:
   - A breach of a documented standard is 🟡 Medium (🔴 Critical if it breaks behaviour); a judgement call
     (code smell) is 🔵 Minor. A spec requirement implemented wrongly is 🟡 Medium or 🔴 Critical by impact.
   - Name each finding's reviewer `standards` or `spec`.
   - A finding without a `**Fix:**` is still not posted.
   - Anything without a file/line (a missing requirement, missing docs, an inaccurate PR description) goes in
     the summary's `Findings without a line` section.
   - Compare the PR description with the **net** diff, as `references/review-findings.md` describes. When the PR
     author is the current user, offer to update the description; change it only on approval. With `--fast`, list the
     suggested description change in the summary instead of asking.
4. This pass **adds to** Steps 2.5, 3 and 4. It never replaces them, and its "no findings" result does not
   clear a PR that has findings from the other passes.

---

## Step 5.1 — Test coverage

For each behavior the diff adds or changes — including changed error codes, status codes and response bodies — find
the test that covers it. Report:

- new or changed behavior with no test, and changed contracts (codes, bodies) that no test pins;
- error paths, edge cases and boundary values (empty, null, zero, maximum, duplicates, concurrency, timeouts,
  cancellation) that the tests do not reach;
- tests that pass without checking the behavior: no assertion, an assertion on a constant or a mock only, a test
  named after a handler that never calls it, a shape check that the old shape also passes;
- tests changed so that they no longer check what they checked before, or that pin the new wrong value.

`**Fix:**` names the test file and the case to add (inputs and expected result); do not write the test. Name
the reviewer `tests`. Severity: a changed contract or a security/data path with no test is 🟡 Medium; a gap on low-risk code is
🔵 Minor.

---

## Step 5.2 — Impact outside the diff

The other passes read the diff; this one looks at what the diff can break **where it does not look**.

1. List every exported symbol the diff renames, removes, or changes the type, signature or meaning of (functions,
   vars, constants, types, error values, config keys, routes, DB columns). For each, `git grep` every use in the
   whole repository at the PR head — **not only the changed files** — and report uses the diff did not update. A use
   that still compiles but now means something else is the worst case (for example a var renamed and its old name
   reused for a function: `json.Marshal` of a func value sends an empty body).
2. Do the same on the target branch head for code added there since the merge-base (`git grep` on
   `origin/{target}`): it merges without a conflict and breaks after the merge.
3. When Step 2.5 Check 3 found conflicts, check the target's diff in the conflicting files for collisions ("Target
   moved" in part 1 of `references/review-findings.md`): the same code, constant, name, route or migration number used
   for something else.

Name the reviewer `impact`. Severity: a reachable broken caller or a public collision is 🔴 Critical; a broken caller on a rare
path is 🟡 Medium.

---

## Step 5.5 — Verify the findings

Collect the candidate findings from Steps 2.5–5.2 and verify them with `references/review-findings.md`:

1. Verify with part 4 of that file: reuse earlier outcomes for unchanged code, then the layers in order
   (mechanical checks, pre-existing, precedents, the independent disprover, proof by test for a kept `critical`;
   the tie-break only when the user asks).
2. Give every finding one outcome — keep, downgrade, drop, or pre-existing — with the evidence in `verified`.
3. Merge, sort and apply the posting rules of part 5 (including doc drift and stale-PR gating).
4. Check the clones you used are unchanged (part 2, read-only).

The provenance findings from Step 2.5 are verified too, but they always go to the summary, never inline.

---

## Step 6 — Post inline comments

With `--preview`, skip Steps 6 and 7: show each inline comment with its `file:line`, then the summary, and stop
until the user asks to post. Otherwise post the findings that Step 5.5 marked for inline posting: one thread per
line. For each finding:

Call `repo_pull_request_thread_write` with:
- `action`: `"create"`
- `pullRequestId`: `{prId}`
- `repositoryId`: `{repo}`
- `project`: `{project}`
- `status`: `"Active"`
- `filePath`, `rightFileStartLine` and `rightFileEndLine` set to the finding's line number, `rightFileStartOffset: 1`, `rightFileEndOffset: 1`
- Comment `content`: formatted using the **Comment Format** template above

Post **one thread per finding**. Do not batch multiple findings into one thread.

---

## Step 7 — Post one summary thread

After all inline comments are posted, create **one** thread without a file/line context. It is the only
top-level thread this review posts. Set its status to `closed`: it reports, and each finding stays open in
its own inline thread. Format:

```
## 🔍 Code Review — `{branch-name}` → `{target-branch}` @ `{short-sha}`

{⚠️ Merge target warning from Check 0, only when the PR does not target the repo's PR target}

{🔁 **Rebase first** — `{target}` moved {n} commits and the PR conflicts in {files}. Only verified critical findings and decisions a rebase will not change are posted inline; the rest is listed under "After the rebase". Request a full review after rebasing. (Check 3 conflicts only)}

**Recommendation:** {ready for human review | fix {what} first | needs changes} — {one sentence why}. This is advice; the merge decision stays with the human reviewers.

**Review confidence:** {Low — human review required | Medium — check {areas} | High — light review} — {one or two reasons} · complexity {low|medium|high} ({n}: {signals}) · {open} open / {resolved} resolved findings (`references/review-findings.md` part 5)

{✂️ Large PR — {n} code lines; consider splitting into {suggested split}. (only above 1500 code lines)}

### 🚫 Commit provenance
{✅ {n} linear commits, no merge commits, no child PRs — or each finding}

### 🔴 Critical ({count})
- `{file}:{line}` — {short title} ({reviewers})

### 🟡 Medium ({count})
- `{file}:{line}` — {short title} ({reviewers})

### 🔵 Minor ({count})
- `{file}:{line}` — {short title} ({reviewers})

### 🔍 Questions ({count})
- `{file}:{line}` — {short title} ({reviewers})

### 📝 Findings without a line
- {missing requirement / missing docs / PR description inaccuracy} ({reviewers})

### 📚 Spec docs disagree with the code ({count}) — only when 3 or more
- `{file}:{line}` — {what the doc says} vs {what the code does}

### ⏳ After the rebase ({count}) — stale / conflicting PR only
- `{file}:{line}` — {short title} ({reviewers})

### 🟣 Pre-existing ({count}) — not introduced by this PR
- `{file}:{line}` — {short title} ({reviewers}) — {also on `{target-branch}`; suggest a separate ticket when serious}

Verification: {n} candidates · {kept} posted · {downgraded} downgraded · {dropped} dropped (wrong, unreachable, linter-catchable or already resolved) · {pre-existing} pre-existing

### ✅ Checked and clean
- {one line per pass: what was traced or checked and found fine}
- Tests: {commands run} — {new failures, or "same {n} failures as the merge-base, nothing new"}

---

Passes: commit provenance · security lenses A–H · runtime correctness & leaks · standards · spec · tests · impact · verify{ (skipped: …) where a pass did not run}
```

Omit any section that has nothing in it, except Commit provenance, Checked and clean, and the Passes line.
On a re-review, list only findings that are still open or new, and mention how many earlier threads were
confirmed fixed.

## Notes

- Step 2.5 (commit provenance) is never skipped, even for small PRs or PRs with no public-facing surface
- Step 4 (runtime) is never skipped either: it applies to every PR that changes code
- Skip binary files, lock files (`*.lock`, `package-lock.json`), and generated files
- If a file has no public-facing surface (e.g. internal utility with no HTTP/UI exposure), skip Lens A for that file but still apply relevant lenses (always B and C; plus D-H where applicable)
- When in doubt about PII risk, keep it as a 🔍 Question with `medium` confidence rather than dropping it — it is better to ask the author than to miss a leak
- **Never approve, vote, complete or set auto-complete on the PR,** and never bypass a branch policy. The summary's Recommendation is advice for the humans
- Do not flag intentional internal IDs used only in backend-to-backend calls that never reach a client

---

## Using the `diagnosing-bugs` skill for deep findings

For any finding in Lens B (validation), Lens C (error contract) or Step 4 (runtime) where the root cause is **unclear or the fix is non-obvious**, invoke the `diagnosing-bugs` skill inline before posting the comment. If it is not installed, skip this and add the static-analysis note below:

1. **Phase 1** — build a minimal feedback loop to confirm the vulnerability or broken contract is actually reachable (e.g. craft a curl that triggers the missing validation, or a test that reproduces the missing `code` field)
2. **Phase 3** — generate 2–3 ranked hypotheses for _why_ the issue exists (missing middleware? wrong layer? copy-paste pattern?)
3. Use the confirmed reproduction and ranked hypotheses to make the comment's **Fix** line concrete and accurate — not speculative

If you cannot build a feedback loop (e.g. the code path requires a running external service), note this explicitly in the comment:
```
⚠️ Note: Could not build a local repro loop for this finding. The suggestion is based on static analysis only — please verify before applying.
```
