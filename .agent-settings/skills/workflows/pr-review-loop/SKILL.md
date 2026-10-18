---
name: pr-review-loop
description: Run the whole Azure DevOps pull-request loop for the current branch — open the PR with the pre-PR review (ado-open-pr), review it (ado-pr-code-review), resolve the review threads with the author (ado-pr-resolve-comments), and re-review until no blocking finding is left or the round limit is reached. Keeps the loop state per PR so a later run continues where it stopped. Never approves, votes or merges. Use when asked to take a branch through review end to end, run the PR review loop, or "open, review and fix this PR".
argument-hint: "[azure-devops-pr-url] [--max-rounds <n>] [any ado-open-pr argument]"
allowed-tools: Bash(git *), Read, Write, Skill, mcp__azure-devops-mcp__repo_pull_request, mcp__azure-devops-mcp__repo_pull_request_thread
---

# PR review loop

Runs three skills in order and carries state between them. Each skill keeps its own consent rules; this workflow
only decides what runs next.

| Phase | Skill |
|---|---|
| Open | `ado-open-pr` (pre-PR review, PR template, reviewers) |
| Review | `ado-pr-code-review` (inline threads + one summary thread) |
| Resolve | `ado-pr-resolve-comments` (fixes with the author, commit and push, then resolve threads) |

The three skills must be installed next to this one (`.agent-settings/skills/tools/`, or the same global skills
folder). If one is missing, stop and say which.

## Arguments

| Token | Meaning |
|---|---|
| an Azure DevOps PR URL | continue the loop for this PR; skip the Open phase |
| `--max-rounds <n>` | review/resolve rounds before stopping; default **3** |
| anything else | passed to `ado-open-pr` unchanged (target branch, `draft`, team, reviewers, ticket, flags) |

## State

Keep one JSON file per PR at `$(git rev-parse --git-dir)/pr-review-loop/<prId>.json`. It lives inside `.git`, so it
is never committed. Read it at the start; write it after every phase.

```json
{
  "prUrl": "https://dev.azure.com/{org}/{project}/_git/{repo}/pullrequest/{prId}",
  "sourceBranch": "feature/x",
  "targetBranch": "main",
  "round": 1,
  "lastReviewedCommit": "<lastMergeSourceCommit at the last review>",
  "reviewConfidence": "Medium",
  "rounds": [
    { "round": 1, "reviewedCommit": "<sha>", "threadsOpened": 6, "fixed": 4, "leftActive": 2, "blocking": 1 }
  ],
  "status": "reviewing | resolving | done | stopped"
}
```

## Step 1 — Open, or find the PR

1. With a PR URL argument, or a state file whose `sourceBranch` is the current branch: use that PR and go to Step 2.
2. Otherwise run `ado-open-pr` with the remaining arguments. It stops early when an active PR already exists for
   this branch and target; use that PR. Take the PR URL from its report.
3. If `ado-open-pr` stopped without a PR (a critical finding, an abort, or the user declined), set `status: stopped`
   and end with its report.
4. Write the state file with `round: 0` and the `reviewConfidence` from the `ado-open-pr` report, if any.

## Step 2 — Review

1. Call `repo_pull_request` (`action: "get"`) and take `lastMergeSourceCommit`. If it equals `lastReviewedCommit`
   in the state, nothing changed since the last review: skip to Step 4.
2. Run `ado-pr-code-review <PR URL>`.
3. Increase `round`, set `lastReviewedCommit`, and record the counts of the review's new threads.

## Step 3 — Resolve

1. Count the **blocking** threads: active threads whose first comment's title line contains `🔴 **Critical`
   (a source tag such as `[runtime]` may come before it; see the Comment Format in `ado-pr-code-review`). List them
   with `repo_pull_request_thread` (`action: "list"`, `status: "Active"`).
2. No active review threads → go to Step 4.
3. Otherwise run `ado-pr-resolve-comments <PR URL>`. It asks the author about every fix and pushes before it marks a
   thread Fixed.
4. Record fixed and still-active counts in this round's entry. If it pushed a commit and `round` is below
   `--max-rounds`, go back to Step 2 for a re-review of the new commits.

## Step 4 — Finish

Stop when one of these is true, and set `status: done` (or `stopped`):
- no blocking thread is active;
- `round` reached `--max-rounds`;
- the author ended `ado-pr-resolve-comments` without pushing anything;
- the user said stop.

Report: the PR URL, the rounds with their counts, the threads still active (blocking first), the latest review
confidence, and what a human reviewer should look at. Merging stays with the team.

## Rules

- **Never approve, vote, complete or merge the PR,** and never bypass a branch policy.
- Do not duplicate a child skill's consent: let each skill ask its own questions.
- A non-interactive / headless run runs each child skill in its own headless mode and stops after the first Review.
- Do not edit code in this workflow; edits happen only inside `ado-open-pr` and `ado-pr-resolve-comments`.
