---
name: ado-open-pr
description: Create an Azure DevOps pull request for the current branch using the Azure DevOps MCP. Pushes the branch, generates the description via the generate-pr-notes contract, opens the PR against a target branch (default develop), and adds reviewers resolved from teams or explicit emails. By default (opt out with --no-sync-spec) scans the committed diff against spec-kit/openspec docs and syncs drifted docs to match the code before opening the PR. Use when asked to open a PR, create an Azure DevOps PR, raise a pull request, or ship the current branch for review.
argument-hint: "[target-branch] [draft] [team] [reviewer-email...] [TICKET-123] [--title <text>] [--ado-project <name>] [--ado-repo <name>] [--no-sync-spec]"
allowed-tools: Bash(git *), Bash(az *), Read, Edit, Task, mcp_azure_devops__repo_get_repo_by_name_or_id, mcp_azure_devops__repo_create_pull_request, mcp_azure_devops__repo_update_pull_request_reviewers, mcp_azure_devops__core_get_identity_ids
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

Flags: `--title <text>` (explicit PR title), `--ado-project <name>`, `--ado-repo <name>`, `--no-sync-spec` (skip the Step 1.5 spec-alignment scan, which otherwise runs by default). Default target branch is `develop`.

---

## Step 1 — Preflight

1. Confirm this is a git repo. Read the current branch: `git branch --show-current`.
2. **Abort** if the branch is empty, `main`, or `develop` — a PR must come from a feature branch. Tell the user which branch they are on.
3. Check the working tree: `git status --porcelain=v1 -b`. If there are uncommitted changes, warn: *"The PR will only include committed work — uncommitted changes are not part of it."* Continue unless the user redirects.
4. Resolve the **target branch** from the args; default to `develop`.
5. Resolve the **Jira ticket** in this order — accept the first `[A-Z]+-\d+` match found:
   1. explicit ticket arg
   2. current branch name
   3. latest commit subject (`git log --format=%s -1`)
6. **Load the reviewer config** now (the merged sources in Step 6) so a bare token can be recognized as a team key during argument parsing. A missing or malformed config is fine here — it just means no team keys are known yet.
7. **Capture the title candidate now** — `git log --format=%s -1` — and hold it for Step 4. Do this before Step 1.5 can add a `docs(spec): sync to code` commit on top of `HEAD`; otherwise that commit would become the PR title.

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

4. **Detect drift.** Compare the diff against the working-doc paths from step 2 and produce a drift report — statements the code now contradicts, behavior renamed/removed/added, stale examples, and `tasks.md` items implemented-but-unchecked. **Check every working doc for this change** (`spec.md`, `plan.md`, `tasks.md`) — the same fact is often repeated across them, so one inconsistency can surface in several places; record **all** occurrences, not just the first. When the diff already edited an SDD doc (step 2), also confirm those spec edits actually match the code and finish any the author started but left half-done. Do this **inline by default** (read the docs yourself) so the step works on every harness. You *may* offload it to a read-only **Task** `subagent_type="general-purpose"` sub-agent for token isolation **only if your harness supports sub-agents** — Claude Code does; harnesses like the VS Code Copilot agent do not, so fall back to inline there. Never make the sub-agent a hard requirement. Either way, treat **the rubric files in step 2 and the top-level `openspec/specs/` tree as read-only** — you may *cite* a constitution / source-of-truth violation but must never edit those trees.

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

Confirm the repo and capture its **repository ID** by calling `mcp_azure_devops__repo_get_repo_by_name_or_id` with `{ project, repositoryNameOrId: <repo> }`. Use the returned `id` as `repositoryId` in later calls.

**Abort** with a clear message if the Azure DevOps MCP is unavailable or the repo cannot be resolved.

## Step 4 — Build the PR title and description

**Title** (the PR's title field):
- Use the `--title <text>` arg if provided; otherwise the **title candidate captured in Step 1** (the pre-sync `HEAD` subject). Do not re-read `HEAD` here — Step 1.5 may have added a `docs(spec): sync to code` commit on top of it.
- If a Jira ticket was resolved and the title does not already start with it, prefix: `[TICKET-ID] <title>`.

**Description** (the PR's body): reuse the **generate-pr-notes** contract, but drive it non-interactively — the Skill tool cannot inject answers into that skill's hardwired interactive sub-agent, so spawn your **own** general-purpose sub-agent instead:

1. Use the **Task** tool with `subagent_type="general-purpose"`. Author its prompt to:
   - **Read the generate-pr-notes skill and follow its note-generation steps.** Resolve it at `.agent-settings/skills/tools/generate-pr-notes/SKILL.md` (project-local) or `~/.claude/skills/generate-pr-notes/SKILL.md` (global). If neither file is found, follow the inline fallback contract below. This is why generate-pr-notes is a dependency — its logic is reused verbatim, only driven non-interactively.
   - **Skip its interactive questions** — supply these answers directly instead: scope = *Entire branch*; base branch = `origin/<target-branch>` (three-dot / merge-base); Jira ticket = `<resolved ticket>` or `n` if none.
   - **Skip its `/tmp` write, `uname`, and clipboard steps.** **Return ONLY the raw markdown body** — no ```` ```markdown ```` fence, no commentary.

   Inline fallback contract (used only when the skill file cannot be found; ≤3000 words, no `Testing` section, each detail in one section only):
   ```
   ## Title
   [TICKET-ID] short sentence (≤128 chars; Jira prefix only if a ticket was resolved)

   ## Summary
   2-4 sentences on what changed and why

   ## Changes
   ### ✨ New Features   (≤5 items)
   ### 🐛 Bug Fixes
   ### 🔧 Configuration

   ## Technical Details   (≤5 items)

   ## Breaking Changes   (only if applicable)
   ```

2. **Jira line** — if a ticket was resolved, insert immediately below the `## Title` content line:
   `Jira: {{JIRA_BASE_URL}}TICKET-ID`
   Resolve `JIRA_BASE_URL` from `.github/config/pr-tools.json` (key `jiraBaseUrl`) → `config/reviewers.json` (key `jiraBaseUrl`) → default `https://your-org.atlassian.net/browse/`. Example: `Jira: https://your-org.atlassian.net/browse/PROJ-3716`.

3. If the returned body is unexpectedly fenced, strip **only** a leading line exactly equal to ```` ```markdown ```` and a final line exactly equal to ```` ``` ````. Do not remove first/last lines unconditionally.

**Hard limit — 4000 characters.** `repo_create_pull_request` rejects a `description` longer than 4000 chars (this supersedes the ~3000-*word* target above, which is far longer). Before Step 5:
- If the body exceeds 4000 chars, trim by priority: keep `## Title` + Jira line + `## Summary` + `## Changes`; shorten or drop the lowest-priority `## Technical Details` bullets.
- **Final unconditional clamp:** if still over 4000 chars, truncate to 3990 chars and append ` …(truncated)`. The body sent to Step 5 must never exceed 4000 chars.

**Fallback** — if the sub-agent / generate-pr-notes contract cannot be run, build the description from the **title candidate captured in Step 1** (the pre-sync `HEAD` subject — not a fresh `git log`, which Step 1.5 may have topped with `docs(spec): sync to code`) plus a summary of `git diff --stat origin/<target-branch>...HEAD` (three-dot), still capped at 4000 chars.

## Step 5 — Create the PR

Call `mcp_azure_devops__repo_create_pull_request` with:
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
5. **Resolve each remaining reviewer to an identity GUID** via `mcp_azure_devops__core_get_identity_ids` with `{ searchFilter: <email-or-unique-name> }`. It returns `[{ id, displayName, descriptor }]` — note there is **no email field** to match against, so use result-count logic:
   - exactly **one** identity returned → use its `id`
   - **zero or more than one** → skip that reviewer and record it as unresolved/ambiguous. Do not guess.
6. **Self-exclusion by GUID** — resolve the current user's value (from step 4) with `core_get_identity_ids` too, and drop that GUID from the resolved reviewer id set. GUID equality is the reliable identity match; the org UPN and the config email are often different strings, so the string pre-filter alone is not enough.
7. **Add** the resolved GUIDs in one call: `mcp_azure_devops__repo_update_pull_request_reviewers` with
   `{ repositoryId, project, pullRequestId, reviewerIds: [<id>...], action: "add" }`.
   If that batched call fails, retry once per-id and record which ids succeeded/failed. If it still fails, report *"PR created; adding reviewers failed: <error> — add them manually"* — never abort.

## Step 7 — Report

The `repo_create_pull_request` response has **no** web URL — construct it:

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

## Notes

- The Azure DevOps MCP is configured with the org at install time (`npx @azure-devops/mcp <org>`); the tools infer it. The org is parsed from the git remote only to build the human-facing PR URL in Step 7.
- Branch refs to `repo_create_pull_request` must be the full `refs/heads/...` form — short names are rejected.
- `pullRequestId` is a number; the MCP coerces numeric strings, but prefer passing the integer.
- Pass the whole resolved `reviewerIds` array in a single `action: "add"` call; only fan out per-id as the retry path when the batch fails.
