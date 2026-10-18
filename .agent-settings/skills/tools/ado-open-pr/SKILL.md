---
name: ado-open-pr
description: Create an Azure DevOps pull request for the current branch using the Azure DevOps MCP. Pushes the branch, generates the description via the generate-pr-notes contract, opens the PR against a target branch (default: the repo's PR target from the shared branch map, else the repo's ADO default branch), and adds reviewers resolved from teams or explicit emails. By default (opt out with --no-sync-spec) scans the committed diff against spec-kit/openspec docs and syncs drifted docs to match the code before opening the PR. Also by default (opt out with --no-review) runs a pre-PR review with lint and function-complexity measurements plus parallel clean-context reviewers (code, security, standards and spec, test coverage, minimal change, refactor), fixes accepted findings with the user, and rates how much human review the PR needs. Use when asked to open a PR, create an Azure DevOps PR, raise a pull request, or ship the current branch for review.
argument-hint: "[target-branch] [draft] [team] [reviewer-email...] [TICKET-123] [--title <text>] [--ado-project <name>] [--ado-repo <name>] [--no-sync-spec] [--no-review] [--review=<keys>] [--no-release-notes]"
allowed-tools: Bash(git *), Bash(az *), Bash(python3 *), Bash(uvx lizard *), Bash(golangci-lint *), Bash(pnpm exec eslint *), Bash(npx eslint *), Bash(mix format *), Read, Edit, Agent, mcp__azure-devops-mcp__repo_repository, mcp__azure-devops-mcp__repo_pull_request, mcp__azure-devops-mcp__repo_pull_request_write, mcp__azure-devops-mcp__core_get_identity_ids
---

# Create Azure DevOps Pull Request

## ⚙️ Dependencies

1. **Azure DevOps MCP** — provides the `repo_*` and `core_*` tools. Install once with the
   `install-azure-devops-mcp` skill (writes `.mcp.json` + `~/.env.mcp-azure-devops`), then restart your agent.
   Repository: https://github.com/microsoft/azure-devops-mcp
2. **generate-pr-notes** skill — its note-generation contract is reused for the PR description (see Step 4).
   Install it globally (`~/.claude/skills/generate-pr-notes/`) or import it with
   `.agent-settings/skills/import-skills.sh <agent> generate-pr-notes`.
3. Optional: **Azure CLI** (`az`, logged in) — used only to identify the current user so they are not added as
   their own reviewer. Falls back to `git config user.email` when `az` is unavailable.
4. Optional: **Confluence credentials** in `~/.env.mcp-atlassian` (`CONFLUENCE_URL`, `CONFLUENCE_USERNAME`,
   `CONFLUENCE_API_TOKEN`, written by `install-atlassian-mcp`) and `python3` — used only by Step 6.5.

This skill lives at `.agent-settings/skills/tools/ado-open-pr/` and is auto-discovered by `import-skills.sh` — no manual copy or registry edit is needed.

---

## Arguments

All optional, any order. Disambiguate each bare (unflagged) token as follows:

| Token shape | Interpreted as |
|---|---|
| matches `[A-Z]+-\d+` | Jira ticket |
| contains `@` | reviewer email / unique name |
| matches a team key under `teams` in the reviewer config | reviewer team |
| literally `draft` | open the PR as a draft |
| anything else | target branch |

Flags: `--title <text>` (explicit PR title), `--ado-project <name>`, `--ado-repo <name>`, `--no-sync-spec` (skip the Step 1.5 spec-alignment scan, which otherwise runs by default), `--no-review` (skip the Step 1.7 pre-PR review), `--review=<keys>` (run only these Step 1.7 reviewers, comma-separated from `code,security,standards,tests,minimal,refactor`), `--no-release-notes` (skip the Step 6.5 release-notes page update). Default target branch: see Step 1 item 4.

---

## Step 1 — Preflight

1. Confirm this is a git repo. Read the current branch: `git branch --show-current`. Then run `git fetch origin`
   so every `origin/<branch>` read below (branch age, ahead count, the Step 1.5 diff) is current. If the fetch
   fails, warn that remote refs may be stale, continue, and repeat the warning in the Step 7 report.
2. **Abort** if the branch is empty, `main`, `master` or `develop` — a PR must come from a feature branch. Tell the user which branch they are on. A `release/*` or `hotfix/*` source is allowed: a backport PR (for example `release/20261015` → `main`) starts there.
3. Check the working tree: `git status --porcelain=v1 -b`. If there are uncommitted changes, warn: *"The PR will only include committed work — uncommitted changes are not part of it."* Continue unless the user redirects.
4. **Resolve the Azure DevOps repository now** with Step 3 (it needs only the git remote): the default-branch lookup
   below and the existing-PR check after it need the repository ID.
   Then resolve the **target branch**:
   1. an explicit target branch arg wins;
   2. otherwise the repo's PR target from `references/branch-map.md` in the sibling `ado-pr-code-review` skill
      (same parent folder as this skill, e.g. `../ado-pr-code-review/references/branch-map.md`);
   3. otherwise the repo's ADO default branch (`repo_repository` with `action: "get"` → `defaultBranch`). If its last
      commit is more than 90 days old, ask the user which branch to target instead of guessing.
   Never fall back to a hard-coded `develop`: several repos merge into `master` or `main`, and some still have a
   live `develop` that is not a PR target. State the chosen target and where it came from before creating the PR.
   If the user named a branch that the map does not list for this repo, say so and ask them to confirm.
   If the map's note for this repo says a pipeline opens this kind of PR itself (for example a
   `release/*` → `main` backport), say so and ask whether to open one by hand anyway.
   Then **abort** with a clear message if any of these is true:
   - the target is the current branch;
   - `origin/<target-branch>` does not exist (`git rev-parse --verify --quiet origin/<target-branch>` fails) — the
     target branch is not on the remote;
   - `git rev-list --count origin/<target-branch>..HEAD` is `0` — the branch has no commits to merge.

   Then **stop if a PR already exists**, before any review or push. Call `repo_pull_request` with
   `{ action: "list", repositoryId, project, status: "Active", sourceRefName: "refs/heads/<current-branch>", targetRefName: "refs/heads/<target-branch>" }`.
   If it returns a PR:
   - report its id, title and URL (built as in Step 7) — do not create a second PR, and do not change its
     description or reviewers;
   - if the local branch has commits that are not on `origin/<current-branch>`, ask whether to push them to that PR
     (`git push origin HEAD:<current-branch>`), and push only on approval;
   - suggest `ado-pr-code-review <PR URL>` to review the open PR, then **stop**. Skip Step 1.5, Step 1.7 and every
     later step.
5. Resolve the **Jira ticket** in this order — accept the first `[A-Z]+-\d+` match found:
   1. explicit ticket arg
   2. current branch name
   3. latest commit subject (`git log --format=%s -1`)
6. **Load the reviewer config** now (the merged sources in Step 6) so a bare token can be recognized as a team key during argument parsing. A missing or malformed config is fine here — it just means no team keys are known yet.
7. **Capture the title candidate now** — `git log --format=%s -1` — and hold it for Step 4, together with the **pre-sync commit** `git rev-parse HEAD` (the Step 1.7 `standards` reviewer reads the spec as it was at that commit). Do this before Step 1.5 can add a `docs(spec): sync to code` commit on top of `HEAD`; otherwise that commit would become the PR title.

## Step 1.5 — Spec/doc alignment (on by default)

Keeps spec-driven docs from drifting behind the code that actually ships in this PR. **The code is the source of truth** — when a working spec doc disagrees with the committed diff, the doc is synced to the code, never the reverse. **This step only ever edits spec docs — it reads the code but never changes the implementation.** A code problem it happens to spot is surfaced for a human, never fixed here. Runs before the push (Step 2) so any doc fix rides along in the same PR.

**When it runs — by default whenever the repo has an SDD layout (step 1 below). This is opt-out, not opt-in:**
- `--no-sync-spec` → skip this step entirely and go straight to Step 2.
- No SDD layout found → nothing to check, skip silently.
- The scan itself always runs when reached — there is **no** "do you want to scan?" prompt; consent is asked only per doc edit in step 5. A non-interactive / headless run still scans and **reports** drift but applies no edits (see step 5), so it never hangs.

1. **Resolve the SDD tool and doc roots.** Read `.agent-settings/project-config.md` → `## SDD Tool` → `Tool:` if present. Otherwise detect from the repo root: `.specify/`, `.speckit`, or `spec-kit.json` → **spec-kit**; `openspec/`, `.openspec`, or `openspec.json` → **openspec**. Neither → log *"no SDD layout found — skipping spec alignment"* and continue to Step 2.

2. **Locate the working docs for THIS change** (the ones allowed to drift), plus the read-only rubric:

   | SDD tool | Working docs — may be synced to code | Read-only rubric — flag violations, never edit |
   |---|---|---|
   | spec-kit | `specs/<NNN-name>/{spec,plan,tasks}.md` | `.specify/memory/constitution.md` |
   | openspec | `openspec/changes/<name>/{proposal.md,design.md,tasks.md}` and `openspec/changes/<name>/specs/` | `openspec/project.md` and the top-level `openspec/specs/` tree |

   Identify `<NNN-name>` / `<name>` in this order:
   - **If the diff already touches an SDD doc** (a working-doc file above appears in the diff), that pins the folder directly *and* is a signal in its own right: the author edited the spec in this PR, so step 4 also checks whether those spec edits actually match the code and, where they don't, corrects the **doc** the rest of the way — the code stays the source of truth and is never edited, so this is still a doc-only sync, not just a plain code→doc pass.
   - Otherwise, the **code paths the diff touches** (most reliable), then the Jira ticket / branch name.

   If you cannot confidently pin a single folder, **report that and skip the sync** — do not guess-edit an unrelated spec. Stay within **this change's** spec folder — reconciling drift across the wider repo is `spec-recalibrate`'s job, not this pre-PR guard.

3. **Compute the diff the PR will contain:** `git diff origin/<target-branch>...HEAD` (three-dot; committed work only, matching the body built in Step 4).

4. **Detect drift.** Compare the diff against the working-doc paths from step 2 and produce a drift report — statements the code now contradicts, behavior renamed/removed/added, stale examples, and `tasks.md` items implemented-but-unchecked. **Check every working doc for this change** (`spec.md`, `plan.md`, `tasks.md`) — the same fact is often repeated across them, so one inconsistency can surface in several places; record **all** occurrences, not just the first. When the diff already edited an SDD doc (step 2), also confirm those spec edits actually match the code and finish any the author started but left half-done. Do this **inline by default** (read the docs yourself) so the step works on every harness. You *may* offload it to a read-only `general-purpose` sub-agent (the **Agent** tool; **Task** in older harnesses) for token isolation **only if your harness supports sub-agents** — Claude Code does; harnesses like the VS Code Copilot agent do not, so fall back to inline there. Never make the sub-agent a hard requirement. Either way, treat **the rubric files in step 2 and the top-level `openspec/specs/` tree as read-only** — you may *cite* a constitution / source-of-truth violation but must never edit those trees.

5. **Report and sync (code → doc), with consent** — mirror the `ado-pr-resolve-comments` model:
   - No drift → report *"spec docs aligned"* and continue to Step 2.
   - Before editing a drifted doc, check `git status --porcelain -- <doc-path>`; if it already has uncommitted changes, **skip that doc** and report it — never fold the user's pre-existing WIP into the sync commit.
   - Trivial doc edits → show each as a before/after diff and apply on approval (`Edit`).
   - Larger rewrites → present an update plan and apply on approval.
   - **Fix every occurrence.** If an inconsistency appears in more than one place within this change's spec docs (across `spec.md` / `plan.md` / `tasks.md` or several sections), update **all** of them — a partial fix leaves the doc self-contradictory. Keep this bounded to **this change's** spec folder; propagating a fix across every spec in the repo is `spec-recalibrate`'s job.
   - **Non-interactive / headless run:** report the drift but apply **no** edits — treat the absence of an approver as no approval and never block on a consent prompt, so a headless run never hangs.
   - A **rubric violation** (constitution / source-of-truth spec contradicted by the code) is surfaced as a warning for the human to resolve — fix the code or consciously amend the rubric — and is **never auto-synced**.

6. **Commit the synced docs so the PR carries them.** `git add` **only the specific doc paths you edited** (never `-A` / `-u`), then commit those same paths explicitly so nothing already in the index rides along: `git commit -m "docs(spec): sync to code" -- <the doc paths you edited>`. Both the scoped add and the pathspec commit are required to keep the user's unrelated staged/uncommitted work (warned about in Step 1) out of the PR. If the user declines every edit, continue with a note that the drift is unresolved.

This step is **best-effort**: any failure here (missing docs, ambiguous folder, sub-agent error) is reported and execution continues to Step 2. It must never block PR creation. The PR title still comes from the **title candidate captured in Step 1**, not from `HEAD` after this step's commit.

## Step 1.7 — Pre-PR review (on by default)

Before anything is pushed, a team of reviewers checks the committed diff. Each reviewer looks for one kind of
problem in a clean context. You collect their findings, check them, fix the accepted ones with the user, and rate
how much human review the PR still needs. The briefs, the finding format and the rating rules are in
`references/pre-pr-review.md`. Read it before you start this step.

**Skip** this step with `--no-review`.

1. **Choose the reviewers.** The keys are `code`, `security`, `standards`, `tests`, `minimal`, `refactor`.
   Use the first one that applies:
   1. `--review=<keys>`;
   2. this repo's row in `references/review-profile.md` in the sibling `ado-pr-code-review` skill
      (`../ado-pr-code-review/references/review-profile.md`), which also gives focus notes, the lint command and the
      test command;
   3. all six.
2. **Measure, then run the reviewers in parallel.** First run the lint and function-complexity measurements in
   `references/pre-pr-review.md` yourself (best-effort; skip a tool that is missing and say so). Lint problems become
   findings; the complexity list goes to the `refactor` reviewer and into the complexity score.
   Then start one fresh `general-purpose` sub-agent per reviewer, all started in the same message
   (the **Agent** tool; **Task** in older harnesses). Do not fork your own context into them: each reviewer must
   start clean. Build each prompt from the run inputs, the common rules and that reviewer's brief in
   `references/pre-pr-review.md`. If the harness has no sub-agents, run the briefs one after another inline, and say
   in the report that the reviews did not have separate contexts.
3. **Merge the results** as `references/pre-pr-review.md` describes: check each finding against the code yourself,
   drop the wrong ones, merge duplicates, settle `minimal` / `refactor` conflicts and sort by severity.
4. **Show the findings to the user**, grouped by severity, with reviewer, confidence, file:line and the suggested fix.
   - **Critical findings:** stop and ask: fix them now, open the PR anyway, or stop without a PR.
   - **Non-interactive / headless run:** report the findings and apply no fixes. With a critical finding, do not
     open the PR: stop after the report.
5. **Fix with the user, one finding at a time** (the same model as Step 1.5 and `ado-pr-resolve-comments`):
   - `trivial` → show a before/after diff and apply it on approval.
   - `larger` → show a short plan and apply it on approval.
   - Before you edit a file, check `git status --porcelain -- <path>`. If it has uncommitted changes, skip that fix
     and say so. Never fold the user's work in progress into a review commit.
   - The user may decline any finding. Keep it in the list as unresolved.
   - After the fixes, offer to run the repo's test command from the review profile. Do not run it without approval.
6. **Commit the fixes** so the PR carries them: `git add` only the paths you edited, then
   `git commit -m "<type>(<scope>): address pre-PR review" -- <those paths>`, with a Conventional Commit type that
   fits the fixes (`fix`, `refactor`, `test`). The PR title still comes from the title candidate captured in Step 1.
7. **Rate the review confidence** (High / Medium / Low) with the table in `references/pre-pr-review.md`, and keep
   the level, its reasons and the unresolved findings for Step 4 and Step 7.

Apart from the critical-finding stop in step 4, this step is **best-effort**: if a reviewer fails, report it, count
it in the confidence rating, and continue.

## Step 2 — Push the branch

1. Detect an upstream: `git rev-parse --abbrev-ref --symbolic-full-name @{u}` (non-zero exit = no upstream).
2. No upstream → `git push -u origin <current-branch>`. Upstream exists → `git push origin HEAD`.
   Always push explicitly to `origin` / the current branch — never a bare `git push`, so the pushed ref is the same ref the PR's `sourceRefName` will point at (Step 5), regardless of what the local branch tracks.
3. If the push fails, **stop** and show the error — do not create a PR against a stale or missing remote branch.

## Step 3 — Resolve the Azure DevOps repository

Azure DevOps remotes carry org / project / repo in the URL. Read it with `git remote get-url origin` and parse:

```
git@ssh.dev.azure.com:v3/{org}/{project}/{repo}
https://{org}@dev.azure.com/{org}/{project}/_git/{repo}
https://{org}.visualstudio.com/{project}/_git/{repo}
```

Resolve each value with this precedence:
- **org** — the parsed value (needed only to build the PR URL in Step 7).
- **project** — `--ado-project` arg → `git config azure.project` → parsed value.
- **repo** — `--ado-repo` arg → `git config azure.repository` → parsed value.

Confirm the repo and capture its **repository ID** by calling `repo_repository` with `{ action: "get", project, repositoryNameOrId: <repo> }`. Use the returned `id` as `repositoryId` in later calls.

**Abort** with a clear message if the Azure DevOps MCP is unavailable or the repo cannot be resolved.

This step runs early, inside Step 1 item 4, so the existing-PR check happens before any review or push. When you
reach this heading in order, reuse the values already resolved.

## Step 4 — Build the PR title and description

**Title** (the PR's title field):
- Use the `--title <text>` arg if provided; otherwise the **title candidate captured in Step 1** (the pre-sync `HEAD` subject). Do not re-read `HEAD` here — Step 1.5 may have added a `docs(spec): sync to code` commit on top of it.
- If a Jira ticket was resolved and the title does not already start with it, prefix: `[TICKET-ID] <title>`.

**Description** (the PR's body) — fill one PR template. Azure DevOps applies a repo's PR template only when a PR
is created in the web UI, not through the API, so this skill applies it itself.

1. **Choose the template.** Look in the **target branch** for the first file that exists, and read it with
   `git show origin/<target-branch>:<path>`:
   1. `<folder>/pull_request_template/branches/<target-branch>.md`, for `<folder>` in `.azuredevops`, `.vsts`,
      `docs` and the repo root, in that order (a template for one target branch);
   2. `<folder>/pull_request_template.md` (also `.txt`), for the same folders in the same order;
   3. no repo template → the shared template `references/pull_request_template.md` of the **generate-pr-notes**
      skill (`.agent-settings/skills/tools/generate-pr-notes/` or `~/.claude/skills/generate-pr-notes/`).
   State which template was used in the Step 7 report.

2. **Fill it with a sub-agent.** Use the **Agent** tool (**Task** in older harnesses) with
   `subagent_type="general-purpose"`. Author its prompt to:
   - **Fill the chosen template** (pass its full text) from the diff `origin/<target-branch>...HEAD` (three-dot).
     Keep its headings, their order and every checklist item word for word, and add no sections.
   - **Follow generate-pr-notes step 4** for how to fill each section (title length, at most 5 changes, API routes
     and their classification, constitution check, ticking a checklist item only when the diff shows it is true).
     The skill is the dependency for these rules; a repo template simply has its own set of sections.
   - Use these facts: Jira ticket = `<resolved ticket>` or none; Jira URL = `{{JIRA_BASE_URL}}TICKET-ID` for the
     template's `Jira:` line (or the first line of the first section when the template has none); spec docs changed
     or synced in Step 1.5; the Step 1.7 `tests` findings and API / constitution findings.
   - **Return ONLY the filled markdown body** — no ```` ```markdown ```` fence, no commentary. Skip generate-pr-notes'
     interactive questions and its `/tmp` write, `uname` and clipboard steps.

   Resolve `JIRA_BASE_URL` from `.github/config/pr-tools.json` (key `jiraBaseUrl`) → `config/reviewers.json`
   (key `jiraBaseUrl`) → default `https://your-org.atlassian.net/browse/`.

3. If the returned body is unexpectedly fenced, strip **only** a leading line exactly equal to ```` ```markdown ````
   and a final line exactly equal to ```` ``` ````. Do not remove first/last lines unconditionally.

4. **Pre-PR review section** — if Step 1.7 ran, append it as the **last** section. Keep it under 600 characters:
   list at most 3 unresolved findings and give the count of the rest.
   ```
   ## Pre-PR Review
   Confidence: **Low** — human review required (unresolved critical in auth middleware)
   Complexity: high (4) — new route, migration, background job, new env var
   Reviewers: code, security, standards, tests, minimal, refactor + lint, lizard · fixed 5 · unresolved 2
   - 🔴 src/auth/session.go:88 — token not checked for expiry (security)
   - 🟡 api/rooms.go:140 — no test for an empty filter (tests)
   ```

**Hard limit — 4000 characters.** `repo_pull_request_write` (`action: "create"`) rejects a `description` longer
than 4000 chars. Before Step 5:
- Shorten prose and sub-bullets first (Summary sentences, then Changes sub-bullets, then evidence sub-bullets).
  Never drop a template heading, a checklist item, the `Jira:` line or the `## Pre-PR Review` section.
- **Final unconditional clamp:** if still over 4000 chars, cut the text **before** `## Pre-PR Review` and append
  ` …(truncated)` at the cut, so the body is at most 4000 chars and the review section stays whole.

**Fallback** — if the sub-agent cannot be run, send the chosen template with only the title and the `Jira:` line
filled and every checkbox unticked, plus a summary of `git diff --stat origin/<target-branch>...HEAD`, and tell the
user to complete it. The title is the **title candidate captured in Step 1** (not a fresh `git log`, which Step 1.5
may have topped with `docs(spec): sync to code`). Still capped at 4000 chars.

## Step 5 — Create the PR

Call `repo_pull_request_write` with:
- `action`: `"create"`
- `repositoryId`: the repo ID from Step 3
- `project`: the resolved project
- `sourceRefName`: `refs/heads/<current-branch>` (full ref form is required)
- `targetRefName`: `refs/heads/<target-branch>` (full ref form is required)
- `title`: the title from Step 4
- `description`: the ≤4000-char body from Step 4
- `isDraft`: `true` **only** when the `draft` arg was passed; otherwise omit (defaults to `false`)

Capture the returned `pullRequestId`. **The PR now exists** — everything in Step 6 is best-effort and must never surface as a failure of the whole skill (always reach Step 7 with the PR id/URL).

## Step 6 — Add reviewers (best-effort)

1. **Load reviewer config** and merge, guarding each read so a missing or malformed file degrades to "no config" (never aborts):
   - `.github/config/pr-tools.json` (consuming repo) — primary
   - `config/reviewers.json` (a **local, user-provided** fallback; this shared repo intentionally ships only `config/reviewers.example.json`, never a real `reviewers.json`)
   - Team keys are the top-level keys under `teams`.
   - If neither file is found, skip team expansion and use only explicit reviewer args; record that no config was found for the Step 7 report.
2. **Expand** each requested team via `teams.<team-key>`. If a named team key is absent from the config, record *"team `<key>` not found — skipped"* and continue.
3. **Merge** expanded team members with explicit reviewer args into one set; de-duplicate case-insensitively.
4. **String pre-filter** — resolve the current user via `az account show --query user.name -o tsv` (fallback `git config user.email`) and drop any case-insensitive string match from the set. This is a cheap first pass, not the sole exclusion (see step 6).
5. **Resolve each remaining reviewer to an identity GUID** via `core_get_identity_ids` with `{ searchFilter: <email-or-unique-name> }`. It returns `[{ id, displayName, descriptor }]` — note there is **no email field** to match against, so use result-count logic:
   - exactly **one** identity returned → use its `id`
   - **zero or more than one** → skip that reviewer and record it as unresolved/ambiguous. Do not guess.
6. **Self-exclusion by GUID** — resolve the current user's value (from step 4) with `core_get_identity_ids` too, and drop that GUID from the resolved reviewer id set. GUID equality is the reliable identity match; the org UPN and the config email are often different strings, so the string pre-filter alone is not enough.
7. **Add** the resolved GUIDs in one call: `repo_pull_request_write` with
   `{ action: "update_reviewers", repositoryId, project, pullRequestId, reviewerIds: [<id>...], reviewerAction: "add" }`.
   If that batched call fails, retry once per-id and record which ids succeeded/failed. If it still fails, report *"PR created; adding reviewers failed: <error> — add them manually"* — never abort.

## Step 6.5 — Add the ticket to the release-notes page (best-effort)

Adds the Jira ticket to this repo's row in a Confluence release-notes page (for example
`2026-10XX Release Notes` or `2026-1019 Release Notes`). The user picks the page
at runtime, because a PR can belong to the monthly page or to a specific release.

**Skip** this step when any of these is true: `--no-release-notes` was passed; no Jira ticket was resolved in Step 1;
this run stopped at the existing-PR check in Step 1; the run is non-interactive / headless (nobody can pick a page).

Run `scripts/confluence_ticket_log.py` from this skill's folder. It needs the Confluence space, a phrase that the
release-notes page titles contain, and the heading above the table with one row per service. Set them in the
reviewer config (Step 6) and pass them as `--space`, `--title-contains` and `--heading` on every call below.
Without this key, skip this step:

```json
"releaseNotes": { "space": "ENG", "titleContains": "Release Notes", "heading": "Services" }
```

1. **List pages:** `python3 -I scripts/confluence_ticket_log.py --list`. It prints the 5 most recently changed
   release-notes pages (id, last change date, title) and whether this month's `YYYY-MMXX ` page exists.
2. **Ask which page this PR belongs to.** Options: each listed page; *"Create this month's page"* only when the
   list says it does not exist yet; *"Skip"*.
3. **Dry run** on the chosen page, with `<repo>` = the repo name from Step 3:
   - listed page: `python3 -I scripts/confluence_ticket_log.py --page-id <id> --service <repo> --ticket <TICKET-ID>`
   - new month: `python3 -I scripts/confluence_ticket_log.py --create-month <YYYY-MM> --service <repo> --ticket <TICKET-ID>`.
     It copies last month's `YYYY-MMXX ` page (same parent, content and attachments kept, only `MMXX` changed in
     the title; the sprint number is not changed).

   It prints the exact storage it would insert, or that the ticket is already in that cell.
4. **Show the dry-run output and ask before writing.** On approval, run the same command with `--apply`.
5. Exit `2` (page, table or service row not found) or any other error: report it and continue to Step 7.
   The PR already exists.

**Never edit the page another way.** Do not read the page with the Confluence MCP and write it back:
`confluence_get_page` returns a converted view even with `convert_to_markdown=false` (it turns `<ac:image>` into
`<img>`). Writing that view back breaks images, Jira macros and layout. The script reads and writes raw storage
through the REST API, inserts only one `<li>` with a Jira macro per new ticket, and checks that nothing else changed.

## Step 7 — Report

The `repo_pull_request_write` create response has **no** web URL — construct it:

```
https://dev.azure.com/{org}/{project}/_git/{repo}/pullrequest/{pullRequestId}
```

Then report:
- PR id and URL
- title
- source branch → target branch
- draft status
- reviewers **added** and reviewers **skipped** (with the reason for each)
- if no reviewer config was found and a team arg was given, note it (team args produced no reviewers)
- the PR template used (repo template path, or the shared generate-pr-notes template)
- pre-PR review: the reviewers that ran (and any that did not finish), findings fixed and unresolved, and the
  **review confidence** level with its reasons and what a human reviewer should check (or *"skipped"* with the reason)
- release-notes page: the page and version written, "already present", skipped (with the reason), or the error.
  If a new month's page was created, say that its title still has last month's sprint number and must be updated by hand.

## Notes

- Tool names here are the Azure DevOps MCP short names. The full name is the MCP server key plus the short name: with the `install-azure-devops-mcp` server key `azure-devops-mcp`, Claude Code exposes `mcp__azure-devops-mcp__<tool>` (the names in `allowed-tools`). Each tool takes an `action` (`repo_repository`: `get`; `repo_pull_request`: `list`; `repo_pull_request_write`: `create`, `update_reviewers`).
- The Azure DevOps MCP is configured with the org at install time (`npx @azure-devops/mcp <org>`); the tools infer it. The org is parsed from the git remote only to build the human-facing PR URL in Step 7.
- Branch refs to `repo_pull_request_write` (`action: "create"`) must be the full `refs/heads/...` form — short names are rejected.
- `pullRequestId` is a number; the MCP coerces numeric strings, but prefer passing the integer.
- Pass the whole resolved `reviewerIds` array in a single `reviewerAction: "add"` call; only fan out per-id as the retry path when the batch fails.
